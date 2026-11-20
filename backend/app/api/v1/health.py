"""Health check endpoints."""
import time
from fastapi import APIRouter, Depends
from app.core.model_loader import get_model_loader, ModelLoader
from app.schemas.common import HealthCheck

router = APIRouter(prefix="/health", tags=["Health"])

_start_time = time.time()


@router.get("", response_model=dict, summary="Basic health check")
async def health():
    """Returns 200 OK if the API is running."""
    return {"status": "ok", "timestamp": time.time()}


@router.get("/detailed", response_model=HealthCheck, summary="Detailed system health")
async def health_detailed(loader: ModelLoader = Depends(get_model_loader)):
    """Returns model status, memory usage, CPU, and uptime."""
    try:
        import psutil
        mem_mb  = round(psutil.Process().memory_info().rss / 1024 ** 2, 1)
        cpu_pct = psutil.cpu_percent(interval=0.1)
    except ImportError:
        mem_mb  = None
        cpu_pct = None

    return HealthCheck(
        status="ok",
        timestamp=time.time(),
        model_loaded=loader.is_loaded(),
        model_name=loader.metadata.get("model_name"),
        auc_roc=loader.metadata.get("metrics", {}).get("auc_roc"),
        memory_mb=mem_mb,
        cpu_pct=cpu_pct,
        uptime_s=round(time.time() - _start_time, 1),
    )
