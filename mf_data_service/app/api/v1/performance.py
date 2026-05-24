from fastapi import APIRouter, Depends, Query, HTTPException
from motor.motor_asyncio import AsyncIOMotorDatabase
from typing import Optional

from app.core.database import get_db, sc_filter

router = APIRouter(prefix="/performance", tags=["Performance"])


@router.get("/{schemecode}")
async def get_performance(
    schemecode: str,
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    """Get returns and risk ratios for a scheme."""
    sc = sc_filter(schemecode)
    returns = await db.scheme_performance.find_one({"schemecode": sc}, {"_id": 0})
    ratios = await db.scheme_ratio.find_one({"schemecode": sc}, {"_id": 0})
    expense = await db.expense_ratio.find_one(
        {"schemecode": sc}, {"_id": 0}, sort=[("date", -1)]
    )

    if not returns and not ratios:
        raise HTTPException(
            status_code=404,
            detail=f"Performance data not found for scheme {schemecode}",
        )

    return {
        "data": {
            "schemecode": schemecode,
            "returns": returns,
            "ratios": ratios,
            "expense_ratio": expense,
        }
    }


@router.get("/compare")
async def compare_performance(
    schemecodes: str = Query(..., description="Comma-separated schemecodes"),
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    """Compare performance across multiple schemes."""
    codes = [c.strip() for c in schemecodes.split(",") if c.strip()]
    if len(codes) > 10:
        raise HTTPException(status_code=400, detail="Max 10 schemes for comparison")

    results = []
    for code in codes:
        sc = sc_filter(code)
        returns = await db.scheme_performance.find_one({"schemecode": sc}, {"_id": 0})
        scheme = await db.scheme_master.find_one(
            {"schemecode": sc}, {"_id": 0, "schemecode": 1, "scheme_name": 1}
        )
        results.append({
            "schemecode": code,
            "scheme_name": scheme.get("scheme_name") if scheme else None,
            "returns": returns,
        })

    return {"data": results, "count": len(results)}
