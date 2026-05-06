from fastapi import APIRouter, Depends, Query, HTTPException
from motor.motor_asyncio import AsyncIOMotorDatabase
from typing import Optional

from app.core.database import get_db

router = APIRouter(prefix="/fund-managers", tags=["Fund Managers"])


@router.get("")
async def list_fund_managers(
    q: Optional[str] = None,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=50, ge=1, le=200),
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    """List fund managers with optional search."""
    query = {"flag": "A"}
    if q:
        query["fundmanager"] = {"$regex": q, "$options": "i"}

    skip = (page - 1) * page_size
    total = await db.fund_manager.count_documents(query)
    cursor = db.fund_manager.find(query, {"_id": 0}).skip(skip).limit(page_size)
    items = await cursor.to_list(length=page_size)

    pages = (total + page_size - 1) // page_size
    return {
        "items": items,
        "total": total,
        "page": page,
        "page_size": page_size,
        "pages": pages,
    }


@router.get("/{manager_id}")
async def get_fund_manager(
    manager_id: str,
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    """Get a single fund manager by ID."""
    manager = await db.fund_manager.find_one({"id": manager_id}, {"_id": 0})
    if not manager:
        raise HTTPException(status_code=404, detail=f"Fund manager {manager_id} not found")
    return {"data": manager}


@router.get("/{manager_id}/schemes")
async def get_manager_schemes(
    manager_id: str,
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    """Get schemes managed by a fund manager."""
    # Fund managers are referenced in scheme_master by fund_mgr_code1 etc.
    cursor = db.scheme_master.find(
        {
            "$or": [
                {"fund_mgr_code1": manager_id},
                {"FUND_MGR_CODE2": manager_id},
                {"FUND_MGR_CODE3": manager_id},
                {"FUND_MGR_CODE4": manager_id},
            ]
        },
        {"_id": 0, "schemecode": 1, "scheme_name": 1, "amc_code": 1, "status": 1},
    )
    items = await cursor.to_list(length=500)
    return {"data": items, "count": len(items)}
