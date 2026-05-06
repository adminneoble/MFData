from fastapi import APIRouter, Depends, Query, HTTPException
from motor.motor_asyncio import AsyncIOMotorDatabase
from typing import Optional

from app.core.database import get_db

router = APIRouter(prefix="/amcs", tags=["AMCs"])


@router.get("")
async def list_amcs(
    q: Optional[str] = None,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=50, ge=1, le=200),
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    """List all Asset Management Companies."""
    query = {"flag": "A"}
    if q:
        query["$or"] = [
            {"amc": {"$regex": q, "$options": "i"}},
            {"s_name": {"$regex": q, "$options": "i"}},
            {"fund": {"$regex": q, "$options": "i"}},
        ]

    skip = (page - 1) * page_size
    total = await db.amc_master.count_documents(query)
    cursor = db.amc_master.find(query, {"_id": 0}).skip(skip).limit(page_size)
    items = await cursor.to_list(length=page_size)

    pages = (total + page_size - 1) // page_size
    return {
        "items": items,
        "total": total,
        "page": page,
        "page_size": page_size,
        "pages": pages,
    }


@router.get("/{amc_code}")
async def get_amc(
    amc_code: str,
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    """Get a single AMC by code."""
    amc = await db.amc_master.find_one({"amc_code": amc_code}, {"_id": 0})
    if not amc:
        raise HTTPException(status_code=404, detail=f"AMC {amc_code} not found")
    return {"data": amc}


@router.get("/{amc_code}/schemes")
async def get_amc_schemes(
    amc_code: str,
    status: Optional[str] = None,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=50, ge=1, le=200),
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    """Get all schemes for an AMC."""
    query: dict = {"amc_code": amc_code}
    if status:
        query["status"] = {"$regex": f"^{status}$", "$options": "i"}

    skip = (page - 1) * page_size
    total = await db.scheme_master.count_documents(query)
    cursor = db.scheme_master.find(
        query, {"_id": 0}
    ).skip(skip).limit(page_size)
    items = await cursor.to_list(length=page_size)

    pages = (total + page_size - 1) // page_size
    return {
        "items": items,
        "total": total,
        "page": page,
        "page_size": page_size,
        "pages": pages,
    }
