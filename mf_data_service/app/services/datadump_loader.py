"""
Datadump Loader: loads .txt JSON files from the data dump into MongoDB.

Each .txt file has the format:
  {"Table":[{row1}\n,{row2}\n,...,{rowN}]}

The first line starts with '{"Table":[{...}'
Subsequent lines start with ',{...}'
The last line ends with ']}' or ',{...}]}'
"""

import json
import logging
import os
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

from motor.motor_asyncio import AsyncIOMotorDatabase
from pymongo import ReplaceOne

from app.core.collections import DATASET_REGISTRY
from app.core.config import get_settings

logger = logging.getLogger(__name__)

# Batch size for bulk writes
BATCH_SIZE = 5000


def parse_datadump_file(file_path: str) -> List[Dict[str, Any]]:
    """Parse a .txt datadump file and return list of records.

    The files are JSON with format: {"Table":[{...},{...},...]}
    We read the whole file and parse the JSON.
    For very large files, we use a streaming approach.
    """
    path = Path(file_path)
    if not path.exists():
        logger.warning(f"File not found: {file_path}")
        return []

    file_size = path.stat().st_size
    logger.info(f"Parsing {path.name} ({file_size / 1024 / 1024:.1f} MB)")

    try:
        with open(file_path, "r", encoding="utf-8", errors="replace") as f:
            content = f.read()

        data = json.loads(content)
        records = data.get("Table", [])
        logger.info(f"  Parsed {len(records)} records from {path.name}")
        return records

    except json.JSONDecodeError as e:
        logger.warning(f"  JSON parse failed for {path.name}, trying line-by-line: {e}")
        return _parse_line_by_line(file_path)
    except Exception as e:
        logger.error(f"  Failed to parse {path.name}: {e}")
        return []


def _parse_line_by_line(file_path: str) -> List[Dict[str, Any]]:
    """Fallback parser: read line by line for malformed JSON files."""
    records = []
    with open(file_path, "r", encoding="utf-8", errors="replace") as f:
        for line_num, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue

            # Remove leading comma and trailing bracket
            if line.startswith('{"Table":['):
                line = line[len('{"Table":['):]
            if line.startswith(","):
                line = line[1:]
            if line.endswith("]}"):
                line = line[:-2]
            if line.endswith("]"):
                line = line[:-1]

            line = line.strip()
            if not line:
                continue

            try:
                record = json.loads(line)
                records.append(record)
            except json.JSONDecodeError:
                if line_num <= 3:
                    logger.debug(f"  Skipping unparseable line {line_num}")
                continue

    logger.info(f"  Line-by-line parsed {len(records)} records")
    return records


async def load_dataset(
    db: AsyncIOMotorDatabase,
    dataset_name: str,
    drop_existing: bool = False,
) -> Dict[str, Any]:
    """Load a single dataset into MongoDB."""
    if dataset_name not in DATASET_REGISTRY:
        return {
            "dataset": dataset_name,
            "collection": "",
            "records_loaded": 0,
            "duration_seconds": 0,
            "status": "error",
            "error": f"Unknown dataset: {dataset_name}",
        }

    config = DATASET_REGISTRY[dataset_name]
    collection_name = config["collection"]
    key_columns = config["key_columns"]
    settings = get_settings()
    start = time.time()

    # Resolve source files
    source_files = []
    if "source_files" in config:
        for sf in config["source_files"]:
            full_path = os.path.join(settings.DATADUMP_ROOT, sf)
            if os.path.exists(full_path):
                source_files.append(full_path)
    elif "source_file" in config:
        full_path = os.path.join(settings.DATADUMP_ROOT, config["source_file"])
        if os.path.exists(full_path):
            source_files.append(full_path)

    if not source_files:
        return {
            "dataset": dataset_name,
            "collection": collection_name,
            "records_loaded": 0,
            "duration_seconds": time.time() - start,
            "status": "skipped",
            "error": "Source file(s) not found",
        }

    collection = db[collection_name]

    # Drop existing data if requested
    if drop_existing:
        await collection.delete_many({})
        logger.info(f"  Dropped existing data in {collection_name}")

    # Determine write strategy
    merge_strategy = config.get("merge_strategy")
    total_written = 0

    # For multi-file datasets (e.g. nav_history with 16 files), process one
    # file at a time to avoid holding tens of millions of records in memory.
    for sf in source_files:
        records = parse_datadump_file(sf)
        if not records:
            continue

        if merge_strategy == "upsert_by_key":
            total_written += await _upsert_records(collection, records, key_columns)
        else:
            total_written += await _bulk_upsert(collection, records, key_columns)

        # Free memory between files
        del records

    if total_written == 0:
        return {
            "dataset": dataset_name,
            "collection": collection_name,
            "records_loaded": 0,
            "duration_seconds": time.time() - start,
            "status": "skipped",
            "error": "No records parsed",
        }

    duration = time.time() - start
    logger.info(
        f"  Loaded {total_written} records into {collection_name} "
        f"({duration:.1f}s)"
    )

    return {
        "dataset": dataset_name,
        "collection": collection_name,
        "records_loaded": total_written,
        "duration_seconds": round(duration, 2),
        "status": "success",
    }


async def _bulk_upsert(
    collection, records: List[Dict], key_columns: List[str]
) -> int:
    """Bulk upsert records using key columns as filter."""
    total = 0
    for i in range(0, len(records), BATCH_SIZE):
        batch = records[i : i + BATCH_SIZE]
        operations = []
        for record in batch:
            filter_doc = {k: record.get(k) for k in key_columns}
            # Skip records missing key columns
            if any(v is None or v == "" for v in filter_doc.values()):
                # For single key, skip if empty. For compound keys, allow partial.
                if len(key_columns) == 1:
                    continue
            operations.append(ReplaceOne(filter_doc, record, upsert=True))

        if operations:
            result = await collection.bulk_write(operations, ordered=False)
            total += result.upserted_count + result.modified_count

    return total


async def _upsert_records(
    collection, records: List[Dict], key_columns: List[str]
) -> int:
    """Upsert records by merging fields into existing documents."""
    total = 0
    for i in range(0, len(records), BATCH_SIZE):
        batch = records[i : i + BATCH_SIZE]
        operations = []
        for record in batch:
            filter_doc = {k: record.get(k) for k in key_columns}
            if any(v is None or v == "" for v in filter_doc.values()):
                if len(key_columns) == 1:
                    continue
            # Use $set to merge fields without overwriting the whole doc
            operations.append(
                ReplaceOne(
                    filter_doc,
                    {**filter_doc, **record},
                    upsert=True,
                )
            )

        if operations:
            result = await collection.bulk_write(operations, ordered=False)
            total += result.upserted_count + result.modified_count

    return total


async def load_all_datasets(
    db: AsyncIOMotorDatabase,
    datasets: Optional[List[str]] = None,
    drop_existing: bool = False,
) -> Dict[str, Any]:
    """Load multiple (or all) datasets into MongoDB."""
    start = time.time()

    if datasets:
        dataset_names = [d for d in datasets if d in DATASET_REGISTRY]
    else:
        dataset_names = list(DATASET_REGISTRY.keys())

    results = []
    successful = 0
    failed = 0

    for name in dataset_names:
        logger.info(f"Loading dataset: {name}")
        result = await load_dataset(db, name, drop_existing=drop_existing)
        results.append(result)
        if result["status"] == "success":
            successful += 1
        elif result["status"] == "error":
            failed += 1

    total_duration = time.time() - start
    logger.info(
        f"Data load complete: {successful} succeeded, {failed} failed, "
        f"{total_duration:.1f}s total"
    )

    return {
        "total_datasets": len(dataset_names),
        "successful": successful,
        "failed": failed,
        "results": results,
        "total_duration_seconds": round(total_duration, 2),
    }
