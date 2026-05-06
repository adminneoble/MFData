import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.core.config import get_settings
from app.core.database import connect_db, close_db
from app.api.v1.router import api_router

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-7s | %(name)s | %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()
    logger.info(f"Starting {settings.APP_NAME} ({settings.APP_ENV})")
    await connect_db()
    logger.info("MongoDB connected")
    yield
    await close_db()
    logger.info("MongoDB disconnected")


app = FastAPI(
    title="MFDataService",
    description="Centralized Mutual Fund Data API — single source of truth for all MF data",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# API key authentication middleware
@app.middleware("http")
async def api_key_auth(request: Request, call_next):
    settings = get_settings()

    # Skip auth for docs, health, and openapi
    skip_paths = {"/docs", "/redoc", "/openapi.json", "/api/v1/health", "/api/v1/health/ready"}
    if request.url.path in skip_paths or not settings.api_keys_list:
        return await call_next(request)

    api_key = request.headers.get("X-API-Key")
    if not api_key or api_key not in settings.api_keys_list:
        return JSONResponse(
            status_code=401,
            content={"detail": "Invalid or missing API key"},
        )

    return await call_next(request)


# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled error: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"},
    )


# Include API routes
app.include_router(api_router)


@app.get("/")
async def root():
    return {
        "service": "MFDataService",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/api/v1/health",
    }
