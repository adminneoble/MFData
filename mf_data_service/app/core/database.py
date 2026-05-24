from typing import Any, Union
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from app.core.config import get_settings


def sc_filter(schemecode: Union[str, int]) -> Any:
    """MongoDB filter value that matches both str and int schemecode storage.

    Datadump records store schemecode as string ("513"); daily-sync records
    store it as int (513).  Using $in covers both without schema migration.
    """
    sc = str(schemecode).strip()
    try:
        return {"$in": [sc, int(sc)]}
    except (ValueError, TypeError):
        return sc

_client: AsyncIOMotorClient | None = None
_db: AsyncIOMotorDatabase | None = None


async def connect_db() -> None:
    global _client, _db
    settings = get_settings()
    _client = AsyncIOMotorClient(settings.MONGODB_URL)
    _db = _client[settings.MONGODB_DB_NAME]

    # Create indexes
    await _create_indexes(_db)


async def close_db() -> None:
    global _client, _db
    if _client:
        _client.close()
    _client = None
    _db = None


def get_db() -> AsyncIOMotorDatabase:
    if _db is None:
        raise RuntimeError("Database not initialized. Call connect_db() first.")
    return _db


async def _create_indexes(db: AsyncIOMotorDatabase) -> None:
    # scheme_master: unique on schemecode
    await db.scheme_master.create_index("schemecode", unique=True)
    await db.scheme_master.create_index("amc_code")
    await db.scheme_master.create_index("status")
    await db.scheme_master.create_index("scheme_name")
    await db.scheme_master.create_index(
        [("scheme_name", "text"), ("short_name", "text")],
        name="scheme_text_search",
    )

    # scheme_isin: unique on ISIN + schemecode
    await db.scheme_isin.create_index("ISIN", unique=True, sparse=True)
    await db.scheme_isin.create_index("Schemecode")

    # scheme_nav: compound unique on schemecode + navdate
    await db.scheme_nav.create_index(
        [("schemecode", 1), ("navdate", -1)], unique=True
    )
    await db.scheme_nav.create_index("schemecode")

    # scheme_portfolio: compound on schemecode + invdate
    await db.scheme_portfolio.create_index(
        [("schemecode", 1), ("invdate", -1)]
    )

    # fund_manager
    await db.fund_manager.create_index("id", unique=True)

    # amc_master
    await db.amc_master.create_index("amc_code", unique=True)

    # scheme_performance (returns)
    await db.scheme_performance.create_index("schemecode", unique=True)

    # scheme_ratio
    await db.scheme_ratio.create_index("schemecode", unique=True)

    # expense_ratio
    await db.expense_ratio.create_index(
        [("schemecode", 1), ("date", -1)]
    )

    # classification masters
    await db.type_master.create_index("type_code", unique=True)
    await db.sclass_master.create_index("classcode", unique=True)
