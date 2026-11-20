"""
Mounts all v1 routers under /api/v1.
"""
from fastapi import APIRouter
from app.api.v1 import health, predict, blackspots, analytics, models

api_router = APIRouter()

api_router.include_router(health.router)
api_router.include_router(predict.router)
api_router.include_router(blackspots.router)
api_router.include_router(analytics.router)
api_router.include_router(models.router)
