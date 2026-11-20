"""Tests for analytics endpoints."""
import pytest


@pytest.mark.asyncio
async def test_analytics_summary(client):
    response = await client.get("/api/v1/analytics/summary")
    assert response.status_code == 200
    data = response.json()
    assert "total_accidents_mtd" in data
    assert "active_blackspots" in data
    assert "avg_risk_score" in data
    assert 0.0 <= data["avg_risk_score"] <= 1.0


@pytest.mark.asyncio
async def test_analytics_heatmap(client):
    response = await client.get("/api/v1/analytics/heatmap")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0
    for point in data:
        assert "lat" in point
        assert "lng" in point
        assert "intensity" in point


@pytest.mark.asyncio
async def test_analytics_trends(client):
    response = await client.get("/api/v1/analytics/trends")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 24   # default 24 months


@pytest.mark.asyncio
async def test_analytics_trends_custom_months(client):
    response = await client.get("/api/v1/analytics/trends?months=12")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 12


@pytest.mark.asyncio
async def test_models_list(client):
    response = await client.get("/api/v1/models")
    assert response.status_code == 200
    data = response.json()
    assert "champion" in data
    assert "available" in data
    assert len(data["available"]) == 4


@pytest.mark.asyncio
async def test_model_metrics(client):
    response = await client.get("/api/v1/models/random_forest/metrics")
    assert response.status_code == 200
    data = response.json()
    assert data["model"] == "random_forest"
    assert "auc_roc" in data["metrics"]


@pytest.mark.asyncio
async def test_model_not_found(client):
    response = await client.get("/api/v1/models/nonexistent/metrics")
    assert response.status_code == 404
