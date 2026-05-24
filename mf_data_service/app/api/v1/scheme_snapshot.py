from fastapi import APIRouter, Depends, HTTPException
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.core.database import get_db, sc_filter
from app.schemas.requests import BulkSchemeCodeRequest

router = APIRouter(prefix="/scheme-snapshot", tags=["Scheme Snapshot"])


async def _build_snapshot(db: AsyncIOMotorDatabase, schemecode: str) -> dict:
    """Build a composite snapshot for a scheme."""
    sc = sc_filter(schemecode)
    scheme = await db.scheme_master.find_one({"schemecode": sc}, {"_id": 0})
    if not scheme:
        return None

    # ISIN
    isin_doc = await db.scheme_isin.find_one({"Schemecode": sc}, {"_id": 0})
    if isin_doc:
        scheme["isin"] = isin_doc.get("ISIN")
        scheme["isin_details"] = isin_doc

    # Classification
    if scheme.get("classcode"):
        sclass = await db.sclass_master.find_one(
            {"classcode": scheme["classcode"]}, {"_id": 0}
        )
        if sclass:
            scheme["classification"] = sclass

    # Current NAV
    nav = await db.current_nav.find_one({"schemecode": sc}, {"_id": 0})
    if nav:
        scheme["current_nav"] = nav

    # Performance (returns)
    returns = await db.scheme_performance.find_one({"schemecode": sc}, {"_id": 0})
    if returns:
        scheme["performance"] = returns

    # Expense ratio
    expense = await db.expense_ratio.find_one(
        {"schemecode": sc}, {"_id": 0}, sort=[("date", -1)]
    )
    if expense:
        scheme["expense_ratio"] = expense.get("expratio")

    # Latest AUM
    aum = await db.scheme_aum.find_one(
        {"schemecode": sc}, {"_id": 0}, sort=[("date", -1)]
    )
    if aum:
        scheme["aum"] = aum

    return scheme


@router.get("/{schemecode}")
async def get_scheme_snapshot(
    schemecode: str,
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    """Get composite snapshot: master + NAV + performance + classification + AUM."""
    snapshot = await _build_snapshot(db, schemecode)
    if not snapshot:
        raise HTTPException(status_code=404, detail=f"Scheme {schemecode} not found")
    return {"data": snapshot}


@router.post("/bulk")
async def get_snapshots_bulk(
    request: BulkSchemeCodeRequest,
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    """Get composite snapshots for multiple schemes."""
    results = []
    for code in request.schemecodes:
        snapshot = await _build_snapshot(db, code)
        if snapshot:
            results.append(snapshot)
    return {"data": results, "count": len(results)}
