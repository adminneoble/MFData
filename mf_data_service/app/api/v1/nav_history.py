from datetime import datetime
from fastapi import APIRouter, Depends, Query, HTTPException
from motor.motor_asyncio import AsyncIOMotorDatabase
from typing import Any, Optional

from app.core.database import get_db, sc_filter as _sc_filter
from app.schemas.requests import BulkSchemeCodeRequest

router = APIRouter(prefix="/nav-history", tags=["NAV History"])


def _navdate_filter(from_date: Optional[str], to_date: Optional[str]) -> dict:
    """Build a MongoDB navdate range filter that covers both storage formats.

    scheme_nav.navdate exists in two formats written by different importers:
      - datadump records:  string  "2026-04-13 00:00:00.000"
      - daily-sync records: ISODate  datetime(2026, 5, 22, 0, 0)

    MongoDB BSON type ordering places String < Date, so a string $lte bound
    silently excludes every ISODate record.  The $or covers both simultaneously.
    """
    if not from_date and not to_date:
        return {}

    iso_rng: dict[str, Any] = {}
    str_rng: dict[str, Any] = {}

    if from_date:
        try:
            iso_rng["$gte"] = datetime.fromisoformat(from_date)
        except ValueError:
            pass
        str_rng["$gte"] = from_date

    if to_date:
        try:
            iso_rng["$lte"] = datetime.fromisoformat(to_date).replace(
                hour=23, minute=59, second=59, microsecond=999000
            )
        except ValueError:
            pass
        # Tilde sorts after all printable date/time characters in string comparison.
        str_rng["$lte"] = to_date + "~"

    conditions = []
    if iso_rng:
        conditions.append({"navdate": iso_rng})
    if str_rng:
        conditions.append({"navdate": str_rng})

    if len(conditions) == 2:
        return {"$or": conditions}
    return conditions[0] if conditions else {}


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
    query: dict = {"schemecode": _sc_filter(schemecode)}
    query.update(_navdate_filter(from_date, to_date))

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
        exists = await db.scheme_master.find_one({"schemecode": _sc_filter(schemecode)})
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
        {"schemecode": _sc_filter(schemecode)}, {"_id": 0}
    )
    if not nav:
        # Fallback to latest from nav history
        nav = await db.scheme_nav.find_one(
            {"schemecode": _sc_filter(schemecode)},
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
    # Include int forms so daily-sync records (int schemecode) are matched too.
    all_codes: list = list(request.schemecodes)
    for sc in request.schemecodes:
        try:
            all_codes.append(int(sc))
        except (ValueError, TypeError):
            pass
    cursor = db.current_nav.find(
        {"schemecode": {"$in": all_codes}}, {"_id": 0}
    )
    items = await cursor.to_list(length=len(all_codes))
    return {"data": items, "count": len(items)}
