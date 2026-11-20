"""Tests for prediction endpoints."""
import pytest
from tests.conftest import SILK_BOARD, HEBBAL, RESIDENTIAL


@pytest.mark.asyncio
async def test_predict_single_valid(client):
    response = await client.post("/api/v1/predict", json=SILK_BOARD)
    assert response.status_code == 200
    data = response.json()
    assert "risk_score" in data
    assert 0.0 <= data["risk_score"] <= 1.0
    assert data["risk_level"] in ["LOW", "MEDIUM", "HIGH", "CRITICAL"]
    assert "is_blackspot" in data
    assert "top_factors" in data
    assert "explanation" in data
    assert "location" in data


@pytest.mark.asyncio
async def test_predict_returns_location_echo(client):
    response = await client.post("/api/v1/predict", json=SILK_BOARD)
    assert response.status_code == 200
    data = response.json()
    assert data["location"]["latitude"]  == SILK_BOARD["latitude"]
    assert data["location"]["longitude"] == SILK_BOARD["longitude"]


@pytest.mark.asyncio
async def test_predict_out_of_bounds_lat(client):
    bad = {**SILK_BOARD, "latitude": 28.6139}   # Delhi — outside Bengaluru
    response = await client.post("/api/v1/predict", json=bad)
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_predict_out_of_bounds_lng(client):
    bad = {**SILK_BOARD, "longitude": 72.8777}   # Mumbai
    response = await client.post("/api/v1/predict", json=bad)
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_predict_invalid_road_type(client):
    bad = {**SILK_BOARD, "road_type": "HIGHWAY"}
    response = await client.post("/api/v1/predict", json=bad)
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_predict_invalid_weather(client):
    bad = {**SILK_BOARD, "weather": "Tornado"}
    response = await client.post("/api/v1/predict", json=bad)
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_predict_risk_score_range(client):
    for payload in [SILK_BOARD, HEBBAL, RESIDENTIAL]:
        response = await client.post("/api/v1/predict", json=payload)
        assert response.status_code == 200
        score = response.json()["risk_score"]
        assert 0.0 <= score <= 1.0


@pytest.mark.asyncio
async def test_predict_cache_hit(client):
    """Second identical request should return same result (from cache)."""
    r1 = await client.post("/api/v1/predict", json=SILK_BOARD)
    r2 = await client.post("/api/v1/predict", json=SILK_BOARD)
    assert r1.status_code == 200
    assert r2.status_code == 200
    assert r1.json()["risk_score"] == r2.json()["risk_score"]


@pytest.mark.asyncio
async def test_predict_batch_valid(client):
    response = await client.post("/api/v1/predict/batch", json={
        "records": [SILK_BOARD, HEBBAL, RESIDENTIAL]
    })
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 3
    assert len(data["predictions"]) == 3
    assert "avg_risk_score" in data
    assert "processing_ms" in data
    assert "blackspot_count" in data


@pytest.mark.asyncio
async def test_predict_batch_empty_fails(client):
    response = await client.post("/api/v1/predict/batch", json={"records": []})
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_predict_batch_all_scores_valid(client):
    response = await client.post("/api/v1/predict/batch", json={
        "records": [SILK_BOARD, HEBBAL]
    })
    assert response.status_code == 200
    for pred in response.json()["predictions"]:
        assert 0.0 <= pred["risk_score"] <= 1.0
        assert pred["risk_level"] in ["LOW", "MEDIUM", "HIGH", "CRITICAL"]
