"""Request/response logging middleware."""
import time
from fastapi import FastAPI, Request
from loguru import logger


def add_logging_middleware(app: FastAPI) -> None:
    @app.middleware("http")
    async def log_requests(request: Request, call_next):
        t0 = time.time()
        response = await call_next(request)
        elapsed_ms = round((time.time() - t0) * 1000, 1)
        logger.info(
            f"{request.method} {request.url.path} "
            f"→ {response.status_code} [{elapsed_ms}ms]"
        )
        response.headers["X-Process-Time"] = f"{elapsed_ms}ms"
        return response
