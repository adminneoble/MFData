#!/usr/bin/env python3
"""
One-time bulk loader: loads all .txt data dump files into MongoDB.

Usage:
    cd mf_data_service
    python -m scripts.load_datadump [--drop] [--datasets scheme_master,amc_master,...]
"""

import asyncio
import argparse
import logging
import sys
import os

# Add parent dir to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.config import get_settings
from app.core.database import connect_db, close_db, get_db
from app.services.datadump_loader import load_all_datasets
from app.core.collections import DATASET_REGISTRY

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-7s | %(name)s | %(message)s",
)
logger = logging.getLogger(__name__)


async def main():
    parser = argparse.ArgumentParser(description="Load MF data dump into MongoDB")
    parser.add_argument(
        "--drop",
        action="store_true",
        help="Drop existing data before loading",
    )
    parser.add_argument(
        "--datasets",
        type=str,
        default=None,
        help="Comma-separated list of dataset names to load (default: all)",
    )
    parser.add_argument(
        "--list",
        action="store_true",
        dest="list_datasets",
        help="List available datasets and exit",
    )
    args = parser.parse_args()

    if args.list_datasets:
        print("\nAvailable datasets:")
        print("-" * 60)
        for name, config in sorted(DATASET_REGISTRY.items()):
            print(f"  {name:30s}  → {config['collection']:25s}  {config.get('description', '')}")
        print(f"\nTotal: {len(DATASET_REGISTRY)} datasets")
        return

    settings = get_settings()
    logger.info(f"DATADUMP_ROOT: {settings.DATADUMP_ROOT}")
    logger.info(f"MONGODB_URL: {settings.MONGODB_URL}")
    logger.info(f"MONGODB_DB_NAME: {settings.MONGODB_DB_NAME}")

    await connect_db()
    db = get_db()

    datasets = None
    if args.datasets:
        datasets = [d.strip() for d in args.datasets.split(",")]
        unknown = [d for d in datasets if d not in DATASET_REGISTRY]
        if unknown:
            logger.error(f"Unknown datasets: {unknown}")
            await close_db()
            sys.exit(1)

    logger.info(f"Loading {'selected' if datasets else 'ALL'} datasets (drop={args.drop})")

    result = await load_all_datasets(db, datasets=datasets, drop_existing=args.drop)

    print("\n" + "=" * 60)
    print("LOAD SUMMARY")
    print("=" * 60)
    for r in result["results"]:
        status_icon = "✓" if r["status"] == "success" else "✗" if r["status"] == "error" else "○"
        print(f"  {status_icon} {r['dataset']:30s}  {r['records_loaded']:>8} records  ({r['duration_seconds']:.1f}s)")
        if r.get("error"):
            print(f"    Error: {r['error']}")
    print("-" * 60)
    print(
        f"  Total: {result['successful']} succeeded, {result['failed']} failed  "
        f"({result['total_duration_seconds']:.1f}s)"
    )
    print("=" * 60)

    await close_db()


if __name__ == "__main__":
    asyncio.run(main())
