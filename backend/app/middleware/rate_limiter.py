"""Rate limiting middleware using slowapi."""
from fastapi import FastAPI
from loguru import logger

try:
    from slowapi import Limiter, _rate_limit_exceeded_handler
    from slowapi.util import get_remote_address
    from slowapi.errors import RateLimitExceeded
    SLOWAPI_AVAILABLE = True
except ImportError:
    SLOWAPI_AVAILABLE = False
    logger.warning("slowapi not installed — rate limiting disabled")

from app.config import settings

limiter = None

if SLOWAPI_AVAILABLE:
    limiter = Limiter(
        key_func=get_remote_address,
        default_limits=[settings.RATE_LIMIT],
    )


def add_rate_limiter(app: FastAPI) -> None:
    if not SLOWAPI_AVAILABLE or limiter is None:
        return
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
