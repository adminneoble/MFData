from fastapi import APIRouter, Depends, HTTPException
from motor.motor_asyncio import AsyncIOMotorDatabase
from typing import Optional

from app.core.database import get_db
from app.schemas.requests import BulkISINRequest
from app.services.validation import validate_isin

router = APIRouter(prefix="/lookup", tags=["Lookup"])


@router.get("/by-isin/{isin}")
async def lookup_by_isin(
    isin: str,
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    """Lookup a scheme by ISIN. Returns scheme master + ISIN details."""
    isin_doc = await db.scheme_isin.find_one({"ISIN": isin}, {"_id": 0})
    if not isin_doc:
        raise HTTPException(status_code=404, detail=f"ISIN {isin} not found")

    schemecode = isin_doc["Schemecode"]
    scheme = await db.scheme_master.find_one(
        {"schemecode": schemecode}, {"_id": 0}
    )

    return {
        "data": {
            "isin": isin,
            "schemecode": schemecode,
            "isin_details": isin_doc,
            "scheme": scheme,
        }
    }


@router.get("/by-name/{scheme_name}")
async def lookup_by_name(
    scheme_name: str,
    limit: int = 20,
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    """Search schemes by name (partial match)."""
    cursor = db.scheme_master.find(
        {
            "$or": [
                {"scheme_name": {"$regex": scheme_name, "$options": "i"}},
                {"s_name": {"$regex": scheme_name, "$options": "i"}},
                {"amfi_name": {"$regex": scheme_name, "$options": "i"}},
                {"LegalNames": {"$regex": scheme_name, "$options": "i"}},
            ]
        },
        {"_id": 0, "schemecode": 1, "scheme_name": 1, "amc_code": 1, "status": 1, "isin_code": 1},
    ).limit(limit)
    items = await cursor.to_list(length=limit)

    # Enrich with ISINs
    schemecodes = [item["schemecode"] for item in items]
    isin_cursor = db.scheme_isin.find(
        {"Schemecode": {"$in": schemecodes}}, {"_id": 0, "ISIN": 1, "Schemecode": 1}
    )
    isin_map = {}
    async for doc in isin_cursor:
        isin_map[doc["Schemecode"]] = doc["ISIN"]

    for item in items:
        item["isin"] = isin_map.get(item["schemecode"]) or item.get("isin_code")

    return {"data": items, "count": len(items)}


@router.post("/resolve")
async def resolve_bulk_isins(
    request: BulkISINRequest,
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    """Bulk resolve ISINs to schemecodes and scheme details."""
    cursor = db.scheme_isin.find(
        {"ISIN": {"$in": request.isins}}, {"_id": 0}
    )
    isin_docs = await cursor.to_list(length=len(request.isins))

    # Build response map
    result = {}
    schemecodes = []
    for doc in isin_docs:
        result[doc["ISIN"]] = {
            "isin": doc["ISIN"],
            "schemecode": doc["Schemecode"],
            "description": doc.get("LongSchemeDescrip"),
        }
        schemecodes.append(doc["Schemecode"])

    # Enrich with scheme names
    if schemecodes:
        scheme_cursor = db.scheme_master.find(
            {"schemecode": {"$in": schemecodes}},
            {"_id": 0, "schemecode": 1, "scheme_name": 1, "amc_code": 1},
        )
        async for scheme in scheme_cursor:
            for isin, data in result.items():
                if data["schemecode"] == scheme["schemecode"]:
                    data["scheme_name"] = scheme.get("scheme_name")
                    data["amc_code"] = scheme.get("amc_code")

    # Mark unresolved ISINs
    for isin in request.isins:
        if isin not in result:
            result[isin] = {"isin": isin, "schemecode": None, "error": "Not found"}

    return {"data": result, "resolved": len(isin_docs), "total": len(request.isins)}
