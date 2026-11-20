"""
FastAPI application entry point.
Handles: startup model loading, middleware registration,
router mounting, and global exception handlers.
"""
import time
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from loguru import logger

from app.api.router import api_router
from app.core.model_loader import _loader as model_loader
from app.middleware.cors import add_cors_middleware
from app.middleware.logging import add_logging_middleware
from app.middleware.rate_limiter import add_rate_limiter
from app.config import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Startup: load model into memory once.
    Shutdown: log cleanup.
    """
    logger.info("=" * 60)
    logger.info("Starting Traffic Black Spot Prediction API")
    logger.info(f"Environment: {settings.APP_ENV}")
    logger.info("=" * 60)

    await model_loader.load()

    logger.success(f"Model: {model_loader.metadata.get('model_name', 'unknown')}")
    logger.success(f"Features: {len(model_loader.feature_names)}")
    logger.success(f"Threshold: {model_loader.threshold}")
    logger.success(f"AUC-ROC: {model_loader.metadata.get('metrics', {}).get('auc_roc', 'N/A')}")
    logger.success("API ready — http://localhost:8000/docs")

    yield

    logger.info("Shutting down API...")


# ── FastAPI app ───────────────────────────────────────────────────────────────
app = FastAPI(
    title="Traffic Black Spot Prediction API",
    description="""
## REST API for predicting traffic accident black spots in Bengaluru

Uses a champion ML model trained on historical accident data (2019–2022).
Provides risk scores, SHAP explanations, and spatial analytics.

### Key Endpoints
- **POST /api/v1/predict** — single location risk prediction
- **POST /api/v1/predict/batch** — bulk prediction (up to 500 locations)
- **GET /api/v1/blackspots** — known Bengaluru black spots
- **GET /api/v1/analytics/summary** — dashboard KPIs
- **GET /api/v1/health** — health check
    """,
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    contact={
        "name": "Traffic Safety Intelligence",
        "url":  "http://localhost:8000/docs",
    },
)

# ── Middleware ────────────────────────────────────────────────────────────────
add_cors_middleware(app)
add_logging_middleware(app)
add_rate_limiter(app)

# ── Routes ────────────────────────────────────────────────────────────────────
app.include_router(api_router, prefix="/api/v1")


# ── Root redirect ─────────────────────────────────────────────────────────────
@app.get("/", include_in_schema=False)
async def root():
    return {
        "name":    "Traffic Black Spot Prediction API",
        "version": "1.0.0",
        "docs":    "/docs",
        "health":  "/api/v1/health",
    }


# ── Global exception handler ──────────────────────────────────────────────────
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception on {request.url.path}: {exc}")
    return JSONResponse(
        status_code=500,
        content={"error": "Internal server error", "detail": str(exc)},
    )
