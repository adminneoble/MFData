from fastapi import APIRouter

from app.api.v1 import (
    admin,
    amc,
    fund_managers,
    health,
    lookup,
    nav_history,
    performance,
    portfolio,
    scheme_snapshot,
    schemes,
)

api_router = APIRouter(prefix="/api/v1")

api_router.include_router(schemes.router)
api_router.include_router(nav_history.router)
api_router.include_router(portfolio.router)
api_router.include_router(performance.router)
api_router.include_router(fund_managers.router)
api_router.include_router(amc.router)
api_router.include_router(lookup.router)
api_router.include_router(scheme_snapshot.router)
api_router.include_router(admin.router)
api_router.include_router(health.router)
