from fastapi import APIRouter, Depends, Query, HTTPException
from motor.motor_asyncio import AsyncIOMotorDatabase
from typing import Optional

from app.core.database import get_db, sc_filter
from app.schemas.requests import BulkSchemeCodeRequest, BulkISINRequest

router = APIRouter(prefix="/schemes", tags=["Schemes"])


@router.get("")
async def search_schemes(
    q: Optional[str] = None,
    amc_code: Optional[str] = None,
    status: Optional[str] = None,
    classcode: Optional[str] = None,
    amfi_type: Optional[str] = None,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=50, ge=1, le=200),
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    """Search and list schemes with filters and pagination."""
    query = {}

    if q:
        query["$or"] = [
            {"scheme_name": {"$regex": q, "$options": "i"}},
            {"s_name": {"$regex": q, "$options": "i"}},
            {"amfi_name": {"$regex": q, "$options": "i"}},
            {"schemecode": q},
        ]
    if amc_code:
        query["amc_code"] = amc_code
    if status:
        query["status"] = {"$regex": f"^{status}$", "$options": "i"}
    if classcode:
        query["classcode"] = classcode
    if amfi_type:
        query["AMFIType"] = {"$regex": f"^{amfi_type}$", "$options": "i"}

    skip = (page - 1) * page_size
    total = await db.scheme_master.count_documents(query)
    cursor = db.scheme_master.find(query, {"_id": 0}).skip(skip).limit(page_size)
    items = await cursor.to_list(length=page_size)

    # Enrich with ISIN from scheme_isin collection
    schemecodes = [item["schemecode"] for item in items]
    isin_cursor = db.scheme_isin.find(
        {"Schemecode": {"$in": schemecodes}}, {"_id": 0}
    )
    isin_map = {}
    async for doc in isin_cursor:
        isin_map[doc["Schemecode"]] = doc.get("ISIN")

    for item in items:
        item["isin"] = isin_map.get(item["schemecode"]) or item.get("isin_code")

    pages = (total + page_size - 1) // page_size
    return {
        "items": items,
        "total": total,
        "page": page,
        "page_size": page_size,
        "pages": pages,
    }


@router.get("/{schemecode}")
async def get_scheme(
    schemecode: str,
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    """Get a single scheme by schemecode."""
    sc = sc_filter(schemecode)
    scheme = await db.scheme_master.find_one({"schemecode": sc}, {"_id": 0})
    if not scheme:
        raise HTTPException(status_code=404, detail=f"Scheme {schemecode} not found")

    # Enrich with ISIN
    isin_doc = await db.scheme_isin.find_one({"Schemecode": sc}, {"_id": 0})
    if isin_doc:
        scheme["isin_details"] = isin_doc
        scheme["isin"] = isin_doc.get("ISIN")

    # Enrich with classification
    if scheme.get("classcode"):
        sclass = await db.sclass_master.find_one(
            {"classcode": scheme["classcode"]}, {"_id": 0}
        )
        if sclass:
            scheme["classification"] = sclass

    # Enrich with current NAV
    nav = await db.current_nav.find_one({"schemecode": sc}, {"_id": 0})
    if nav:
        scheme["current_nav"] = nav

    return {"data": scheme}


@router.get("/{schemecode}/master")
async def get_scheme_master(
    schemecode: str,
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    """Get scheme metadata only (no enrichment)."""
    scheme = await db.scheme_master.find_one({"schemecode": sc_filter(schemecode)}, {"_id": 0})
    if not scheme:
        raise HTTPException(status_code=404, detail=f"Scheme {schemecode} not found")
    return {"data": scheme}


@router.post("/bulk")
async def get_schemes_bulk(
    request: BulkSchemeCodeRequest,
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    """Get multiple schemes by schemecodes."""
    all_codes = list(request.schemecodes)
    for sc in request.schemecodes:
        try:
            all_codes.append(int(sc))
        except (ValueError, TypeError):
            pass
    cursor = db.scheme_master.find({"schemecode": {"$in": all_codes}}, {"_id": 0})
    items = await cursor.to_list(length=len(all_codes))
    return {"data": items, "count": len(items)}
