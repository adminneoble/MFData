import logging
from fastapi import APIRouter, Depends, HTTPException
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.core.database import get_db
from app.core.collections import DATASET_REGISTRY
from app.schemas.requests import DataLoadRequest
from app.services.datadump_loader import load_all_datasets, load_dataset

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/admin", tags=["Admin"])


@router.post("/load-datadump")
async def load_datadump(
    request: DataLoadRequest,
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    """Trigger bulk data load from .txt dump files into MongoDB.

    Pass specific dataset names to load only those, or omit to load all.
    Set drop_existing=true to clear collections before loading.
    """
    result = await load_all_datasets(
        db,
        datasets=request.datasets,
        drop_existing=request.drop_existing,
    )
    return {"data": result}


@router.post("/load-datadump/{dataset_name}")
async def load_single_dataset(
    dataset_name: str,
    drop_existing: bool = False,
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    """Load a single dataset by name."""
    if dataset_name not in DATASET_REGISTRY:
        raise HTTPException(
            status_code=404,
            detail=f"Unknown dataset: {dataset_name}. Available: {list(DATASET_REGISTRY.keys())}",
        )
    result = await load_dataset(db, dataset_name, drop_existing=drop_existing)
    return {"data": result}


@router.get("/datasets")
async def list_datasets():
    """List all available datasets and their descriptions."""
    datasets = []
    for name, config in DATASET_REGISTRY.items():
        datasets.append({
            "name": name,
            "collection": config["collection"],
            "description": config.get("description", ""),
            "source_file": config.get("source_file", config.get("source_files", "")),
        })
    return {"data": datasets, "count": len(datasets)}


@router.get("/stats")
async def get_stats(
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    """Get record counts for all collections."""
    collections = await db.list_collection_names()
    stats = {}
    for coll_name in sorted(collections):
        count = await db[coll_name].count_documents({})
        stats[coll_name] = count
    return {"data": stats}


@router.post("/validate")
async def validate_data(
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    """Run data quality checks across collections."""
    checks = []

    # Check scheme_master has records
    scheme_count = await db.scheme_master.count_documents({})
    checks.append({
        "check": "scheme_master_count",
        "value": scheme_count,
        "status": "pass" if scheme_count > 0 else "fail",
    })

    # Check ISIN coverage
    isin_count = await db.scheme_isin.count_documents({})
    checks.append({
        "check": "scheme_isin_count",
        "value": isin_count,
        "status": "pass" if isin_count > 0 else "fail",
    })

    # Check NAV data exists
    nav_count = await db.current_nav.count_documents({})
    checks.append({
        "check": "current_nav_count",
        "value": nav_count,
        "status": "pass" if nav_count > 0 else "fail",
    })

    # Check AMC master
    amc_count = await db.amc_master.count_documents({})
    checks.append({
        "check": "amc_master_count",
        "value": amc_count,
        "status": "pass" if amc_count > 0 else "fail",
    })

    # Check fund managers
    fm_count = await db.fund_manager.count_documents({})
    checks.append({
        "check": "fund_manager_count",
        "value": fm_count,
        "status": "pass" if fm_count > 0 else "fail",
    })

    # Orphan check: schemes with no AMC in amc_master
    if amc_count > 0 and scheme_count > 0:
        amc_codes = await db.amc_master.distinct("amc_code")
        orphan_count = await db.scheme_master.count_documents(
            {"amc_code": {"$nin": amc_codes}}
        )
        checks.append({
            "check": "orphan_schemes_no_amc",
            "value": orphan_count,
            "status": "pass" if orphan_count == 0 else "warn",
        })

    all_pass = all(c["status"] == "pass" for c in checks)
    return {
        "overall": "pass" if all_pass else "issues_found",
        "checks": checks,
    }
