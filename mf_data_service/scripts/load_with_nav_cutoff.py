#!/usr/bin/env python3
"""
Load all MF datasets into MongoDB, with NAV history filtered to 2023+.

This avoids loading 20+ years of daily NAVs (40M rows → ~3.3GB) when
the Atlas M5 tier only has ~3.9GB free. Loading 2023+ gives ~3 years
of NAV data (~12M rows → ~1GB) which is sufficient for ForwardInsights
performance charts and analysis.

Usage:
    cd mf_data_service
    python -m scripts.load_with_nav_cutoff
"""
import asyncio
import json
import logging
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.config import get_settings
from app.core.database import connect_db, close_db, get_db
from app.core.collections import DATASET_REGISTRY
from app.services.datadump_loader import (
    parse_datadump_file,
    _bulk_upsert,
    BATCH_SIZE,
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-7s | %(message)s",
)
logger = logging.getLogger(__name__)

NAV_DATE_CUTOFF = "2023-01-01"


async def load_dataset(db, name: str, config: dict) -> dict:
    """Load a single dataset. For nav_history, filters rows >= NAV_DATE_CUTOFF."""
    collection_name = config["collection"]
    key_columns = config.get("key_columns", [])
    source_files = config.get("source_files", [])
    if not source_files:
        sf = config.get("source_file")
        if sf:
            source_files = [sf]

    settings = get_settings()
    root = settings.DATADUMP_ROOT
    source_files = [os.path.join(root, f) for f in source_files]

    is_nav = name == "nav_history"
    collection = db[collection_name]
    total = 0
    start = time.time()

    for sf in source_files:
        if not os.path.exists(sf):
            logger.warning(f"  File not found: {sf}")
            continue

        records = parse_datadump_file(sf)
        if not records:
            continue

        original_count = len(records)

        # Filter NAV by date cutoff
        if is_nav:
            records = [
                r for r in records
                if (r.get("navdate") or "") >= NAV_DATE_CUTOFF
            ]
            logger.info(
                f"  {os.path.basename(sf)}: {original_count:,} rows → "
                f"{len(records):,} after {NAV_DATE_CUTOFF} cutoff "
                f"({len(records)/original_count*100:.0f}%)"
            )

        if records:
            count = await _bulk_upsert(collection, records, key_columns)
            total += count

        del records

    duration = time.time() - start
    logger.info(f"  ✓ {name} → {collection_name}: {total:,} records ({duration:.1f}s)")
    return {"dataset": name, "records": total, "seconds": round(duration, 1)}


async def main():
    settings = get_settings()
    logger.info(f"MongoDB: {settings.MONGODB_URL[:40]}...")
    logger.info(f"Database: {settings.MONGODB_DB_NAME}")
    logger.info(f"Data root: {settings.DATADUMP_ROOT}")
    logger.info(f"NAV cutoff: >= {NAV_DATE_CUTOFF}")
    logger.info("")

    await connect_db()
    db = get_db()

    # Verify connection
    colls = await db.list_collection_names()
    logger.info(f"Connected. Existing collections: {len(colls)}")

    # Sort datasets: masters first, NAV last
    nav_datasets = []
    other_datasets = []
    for name, config in DATASET_REGISTRY.items():
        if name == "nav_history":
            nav_datasets.append((name, config))
        else:
            other_datasets.append((name, config))

    all_datasets = other_datasets + nav_datasets
    results = []
    total_start = time.time()

    for i, (name, config) in enumerate(all_datasets, 1):
        logger.info(f"[{i}/{len(all_datasets)}] Loading: {name}")
        try:
            result = await load_dataset(db, name, config)
            results.append(result)
        except Exception as e:
            logger.error(f"  ✗ {name} failed: {e}")
            results.append({"dataset": name, "records": 0, "error": str(e)})

    total_time = time.time() - total_start

    # Summary
    logger.info("")
    logger.info("=" * 60)
    logger.info(f"LOAD COMPLETE — {total_time:.0f}s total")
    logger.info("=" * 60)
    total_records = 0
    for r in results:
        status = "✓" if r.get("records", 0) > 0 else ("✗" if "error" in r else "○")
        logger.info(f"  {status} {r['dataset']:35s} {r.get('records',0):>10,} records")
        total_records += r.get("records", 0)
    logger.info(f"  Total: {total_records:,} records")

    # Check storage
    stats = await db.command("dbStats")
    storage_mb = stats["storageSize"] / 1024 / 1024
    index_mb = stats["indexSize"] / 1024 / 1024
    logger.info(f"  Storage: {storage_mb:.0f} MB data + {index_mb:.0f} MB indexes = {storage_mb+index_mb:.0f} MB")

    await close_db()


if __name__ == "__main__":
    asyncio.run(main())
