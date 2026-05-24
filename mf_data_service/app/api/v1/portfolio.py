from fastapi import APIRouter, Depends, Query, HTTPException
from motor.motor_asyncio import AsyncIOMotorDatabase
from typing import Optional

from app.core.database import get_db, sc_filter

router = APIRouter(prefix="/portfolio", tags=["Portfolio"])


@router.get("/{schemecode}")
async def get_portfolio(
    schemecode: str,
    as_of_date: Optional[str] = Query(None, description="Portfolio date (YYYY-MM-DD)"),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=100, ge=1, le=500),
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    """Get portfolio holdings for a scheme."""
    sc = sc_filter(schemecode)
    query: dict = {"schemecode": sc}

    if as_of_date:
        query["invdate"] = {"$regex": f"^{as_of_date}"}
    else:
        # Get the latest portfolio date
        latest = await db.scheme_portfolio.find_one(
            {"schemecode": sc}, {"invdate": 1}, sort=[("invdate", -1)]
        )
        if latest:
            query["invdate"] = latest["invdate"]

    skip = (page - 1) * page_size
    total = await db.scheme_portfolio.count_documents(query)
    cursor = (
        db.scheme_portfolio.find(query, {"_id": 0})
        .sort("srno", 1)
        .skip(skip)
        .limit(page_size)
    )
    items = await cursor.to_list(length=page_size)

    if not items:
        exists = await db.scheme_master.find_one({"schemecode": sc})
        if not exists:
            raise HTTPException(status_code=404, detail=f"Scheme {schemecode} not found")

    # Calculate total AUM from first record
    total_aum = items[0].get("aum") if items else None

    pages = (total + page_size - 1) // page_size
    return {
        "schemecode": schemecode,
        "invdate": items[0].get("invdate") if items else None,
        "total_aum": total_aum,
        "holdings": items,
        "total": total,
        "page": page,
        "page_size": page_size,
        "pages": pages,
    }


@router.get("/{schemecode}/equity-holdings")
async def get_equity_holdings(
    schemecode: str,
    as_of_date: Optional[str] = Query(None),
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    """Get only equity holdings for a scheme."""
    sc = sc_filter(schemecode)
    query: dict = {"schemecode": sc, "asect_name": "Domestic Equities"}

    if as_of_date:
        query["invdate"] = {"$regex": f"^{as_of_date}"}
    else:
        latest = await db.scheme_portfolio.find_one(
            {"schemecode": sc}, {"invdate": 1}, sort=[("invdate", -1)]
        )
        if latest:
            query["invdate"] = latest["invdate"]

    cursor = db.scheme_portfolio.find(query, {"_id": 0}).sort("holdpercentage", -1)
    items = await cursor.to_list(length=500)

    return {
        "schemecode": schemecode,
        "holdings": items,
        "count": len(items),
    }
