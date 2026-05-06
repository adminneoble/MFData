#!/usr/bin/env python3
"""Fast NAV loader — insert_many (no upsert) + bulk index after.

Since scheme_nav is empty, we skip the expensive ReplaceOne upsert and
use insert_many with ordered=False. Index is created AFTER all inserts.

Usage:
    cd /Users/jpsinha/Documents/MFDataService/mf_data_service
    python -m scripts.fast_nav_load
"""
import asyncio
import json
import logging
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from motor.motor_asyncio import AsyncIOMotorClient
from app.core.config import get_settings

logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(message)s")
log = logging.getLogger(__name__)

NAV_DATE_CUTOFF = "2023-01-01"
BATCH = 25_000  # larger batches = fewer round-trips


def parse_and_filter(path: str) -> list[dict]:
    """Parse JSON file, keep only rows with navdate >= cutoff."""
    log.info(f"  Reading {os.path.basename(path)} ({os.path.getsize(path)/1e6:.0f} MB)")
    with open(path, "r", encoding="utf-8", errors="replace") as f:
        data = json.loads(f.read())
    rows = data.get("Table", [])
    total = len(rows)
    filtered = [r for r in rows if (r.get("navdate") or "") >= NAV_DATE_CUTOFF]
    log.info(f"    {total:,} → {len(filtered):,} after {NAV_DATE_CUTOFF} cutoff ({len(filtered)*100//max(total,1)}%)")
    del rows, data
    return filtered


async def main():
    settings = get_settings()
    client = AsyncIOMotorClient(settings.MONGODB_URL)
    db = client[settings.MONGODB_DB_NAME]

    coll = db["scheme_nav"]
    existing = await coll.count_documents({})
    if existing > 0:
        log.info(f"scheme_nav has {existing:,} docs — dropping for clean fast load")
        await coll.drop()

    # NAV files
    root = settings.DATADUMP_ROOT
    files = sorted(
        [os.path.join(root, f"Navhist_{i:02d}.txt") for i in range(1, 16)]
        + [os.path.join(root, "Navhist_HL.txt")]
    )
    files = [f for f in files if os.path.exists(f)]
    log.info(f"Found {len(files)} NAV files, cutoff >= {NAV_DATE_CUTOFF}")

    grand_total = 0
    grand_start = time.time()

    for i, fpath in enumerate(files, 1):
        log.info(f"[{i}/{len(files)}] {os.path.basename(fpath)}")
        t0 = time.time()
        records = parse_and_filter(fpath)
        if not records:
            continue

        # Remove _id if present from source
        for r in records:
            r.pop("_id", None)

        # insert_many in batches
        inserted = 0
        for start in range(0, len(records), BATCH):
            batch = records[start : start + BATCH]
            result = await coll.insert_many(batch, ordered=False)
            inserted += len(result.inserted_ids)

        grand_total += inserted
        elapsed = time.time() - t0
        rate = inserted / elapsed if elapsed > 0 else 0
        log.info(f"    ✓ {inserted:,} inserted ({elapsed:.1f}s, {rate:,.0f} docs/s)")
        del records

    # Build compound index AFTER all inserts (much faster than indexing during)
    log.info("Building index on (schemecode, navdate)...")
    t0 = time.time()
    await coll.create_index([("schemecode", 1), ("navdate", 1)], unique=True, name="schemecode_navdate")
    log.info(f"  Index built in {time.time()-t0:.1f}s")

    total_time = time.time() - grand_start
    log.info(f"\nDONE — {grand_total:,} NAV records loaded in {total_time:.0f}s")

    stats = await db.command("dbStats")
    storage = stats["storageSize"] / 1024 / 1024
    idx = stats["indexSize"] / 1024 / 1024
    log.info(f"MFData storage: {storage:.0f} MB data + {idx:.0f} MB indexes = {storage+idx:.0f} MB")

    client.close()


if __name__ == "__main__":
    asyncio.run(main())
