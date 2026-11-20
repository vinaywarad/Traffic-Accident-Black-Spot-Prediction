"""Tests for black spot endpoints."""
import pytest


@pytest.mark.asyncio
async def test_list_blackspots(client):
    response = await client.get("/api/v1/blackspots")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] > 0
    assert len(data["spots"]) > 0


@pytest.mark.asyncio
async def test_list_blackspots_filter_critical(client):
    response = await client.get("/api/v1/blackspots?severity=CRITICAL")
    assert response.status_code == 200
    data = response.json()
    for spot in data["spots"]:
        assert spot["severity"] == "CRITICAL"


@pytest.mark.asyncio
async def test_list_blackspots_filter_high(client):
    response = await client.get("/api/v1/blackspots?severity=HIGH")
    assert response.status_code == 200
    for spot in response.json()["spots"]:
        assert spot["severity"] == "HIGH"


@pytest.mark.asyncio
async def test_list_blackspots_invalid_severity(client):
    response = await client.get("/api/v1/blackspots?severity=EXTREME")
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_get_blackspot_by_id(client):
    response = await client.get("/api/v1/blackspots/BS-001")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == "BS-001"
    assert data["name"] == "Silk Board Junction"


@pytest.mark.asyncio
async def test_get_blackspot_not_found(client):
    response = await client.get("/api/v1/blackspots/BS-999")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_blackspot_has_required_fields(client):
    response = await client.get("/api/v1/blackspots/BS-001")
    data = response.json()
    for field in ["id", "name", "lat", "lng", "severity", "risk_score",
                  "annual_accidents", "road_type", "primary_cause"]:
        assert field in data, f"Missing field: {field}"
