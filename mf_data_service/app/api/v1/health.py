from fastapi import APIRouter, Depends
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.core.database import get_db

router = APIRouter(tags=["Health"])


@router.get("/health")
async def health():
    """Liveness check."""
    return {"status": "ok"}


@router.get("/health/ready")
async def readiness(db: AsyncIOMotorDatabase = Depends(get_db)):
    """Readiness check — verifies MongoDB connectivity."""
    try:
        await db.command("ping")
        scheme_count = await db.scheme_master.count_documents({})
        return {
            "status": "ready",
            "mongodb": "connected",
            "scheme_count": scheme_count,
        }
    except Exception as e:
        return {
            "status": "not_ready",
            "mongodb": "disconnected",
            "error": str(e),
        }
