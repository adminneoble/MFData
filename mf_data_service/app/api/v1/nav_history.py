from fastapi import APIRouter, Depends, Query, HTTPException
from motor.motor_asyncio import AsyncIOMotorDatabase
from typing import Optional

from app.core.database import get_db
from app.schemas.requests import BulkSchemeCodeRequest

router = APIRouter(prefix="/nav-history", tags=["NAV History"])


@router.get("/{schemecode}")
async def get_nav_history(
    schemecode: str,
    from_date: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)"),
    to_date: Optional[str] = Query(None, description="End date (YYYY-MM-DD)"),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=100, ge=1, le=1000),
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    """Get NAV history for a scheme with optional date range."""
    query: dict = {"schemecode": schemecode}

    if from_date or to_date:
        date_filter = {}
        if from_date:
            date_filter["$gte"] = from_date
        if to_date:
            date_filter["$lte"] = to_date + " 23:59:59.999"
        query["navdate"] = date_filter

    skip = (page - 1) * page_size
    total = await db.scheme_nav.count_documents(query)
    cursor = (
        db.scheme_nav.find(query, {"_id": 0})
        .sort("navdate", -1)
        .skip(skip)
        .limit(page_size)
    )
    items = await cursor.to_list(length=page_size)

    if not items and total == 0:
        # Check if scheme exists at all
        exists = await db.scheme_master.find_one({"schemecode": schemecode})
        if not exists:
            raise HTTPException(status_code=404, detail=f"Scheme {schemecode} not found")

    pages = (total + page_size - 1) // page_size
    return {
        "data": items,
        "total": total,
        "page": page,
        "page_size": page_size,
        "pages": pages,
    }


@router.get("/{schemecode}/latest")
async def get_latest_nav(
    schemecode: str,
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    """Get the latest NAV for a scheme."""
    nav = await db.current_nav.find_one(
        {"schemecode": schemecode}, {"_id": 0}
    )
    if not nav:
        # Fallback to latest from nav history
        nav = await db.scheme_nav.find_one(
            {"schemecode": schemecode},
            {"_id": 0},
            sort=[("navdate", -1)],
        )
    if not nav:
        raise HTTPException(status_code=404, detail=f"NAV not found for scheme {schemecode}")
    return {"data": nav}


@router.post("/bulk")
async def get_nav_bulk(
    request: BulkSchemeCodeRequest,
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    """Get latest NAV for multiple schemes."""
    cursor = db.current_nav.find(
        {"schemecode": {"$in": request.schemecodes}}, {"_id": 0}
    )
    items = await cursor.to_list(length=len(request.schemecodes))
    return {"data": items, "count": len(items)}
