"""
Analytics endpoints for the dashboard.
GET /analytics/summary  — KPI cards
GET /analytics/heatmap  — heatmap layer data
GET /analytics/trends   — monthly trend chart
"""
from typing import Optional
from fastapi import APIRouter, Query
from app.schemas.analytics import HeatmapPoint, TrendPoint, AnalyticsSummary
from app.core.blackspot_store import get_heatmap_data, get_trend_data

router = APIRouter(prefix="/analytics", tags=["Analytics"])


@router.get(
    "/summary",
    response_model=AnalyticsSummary,
    summary="Dashboard KPI summary",
    description="Returns headline KPIs for the dashboard stat cards.",
)
async def get_summary():
    return AnalyticsSummary(
        total_accidents_mtd=342,
        active_blackspots=15,
        high_risk_roads=8,
        avg_risk_score=0.61,
        blackspot_change_pct=4.2,
        model_accuracy=0.87,
        last_updated="2024-01-15T10:30:00Z",
    )


@router.get(
    "/heatmap",
    response_model=list[HeatmapPoint],
    summary="Accident density heatmap data",
    description="Returns lat/lng/intensity points for the Leaflet heatmap layer.",
)
async def get_heatmap(
    year:  Optional[int] = Query(None, description="Filter by year"),
    month: Optional[int] = Query(None, ge=1, le=12, description="Filter by month"),
):
    return get_heatmap_data(year=year, month=month)


@router.get(
    "/trends",
    summary="Monthly accident trends",
    description="Returns month-by-month accident counts for the trend chart.",
)
async def get_trends(
    months: int = Query(24, ge=1, le=60, description="Number of months to return"),
):
    return get_trend_data(months=months)
