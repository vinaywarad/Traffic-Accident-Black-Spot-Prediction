"""
Shared pytest fixtures for all API tests.
"""
import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport

from app.main import app
from app.core.model_loader import _loader
from app.utils.cache import clear_cache


@pytest_asyncio.fixture(scope="session", autouse=True)
async def load_model_once():
    """Load the model once for the entire test session."""
    if not _loader.is_loaded():
        await _loader.load()


@pytest_asyncio.fixture
async def client(load_model_once):
    """Async HTTP client wired directly to the FastAPI app (no network)."""
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as ac:
        yield ac


@pytest.fixture(autouse=True)
def clear_prediction_cache():
    """Clear in-memory cache before each test for isolation."""
    clear_cache()
    yield
    clear_cache()




# ── Shared request payloads ───────────────────────────────────────────────────

SILK_BOARD = {
    "latitude": 12.9170, "longitude": 77.6228,
    "hour": 9, "month": 7, "day_of_week": 1,
    "road_type": "ORR", "weather": "Rainy",
    "speed_limit": 80, "vehicles_involved": 2,
}

HEBBAL = {
    "latitude": 13.0450, "longitude": 77.5970,
    "hour": 18, "month": 3, "day_of_week": 4,
    "road_type": "NH", "weather": "Clear",
    "speed_limit": 80, "vehicles_involved": 1,
}

RESIDENTIAL = {
    "latitude": 12.9500, "longitude": 77.5800,
    "hour": 14, "month": 2, "day_of_week": 2,
    "road_type": "Residential", "weather": "Clear",
    "speed_limit": 30, "vehicles_involved": 1,
}
