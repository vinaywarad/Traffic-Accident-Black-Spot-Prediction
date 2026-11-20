"""
Schemas for analytics endpoints.
"""
from typing import Optional
from pydantic import BaseModel


class HeatmapPoint(BaseModel):
    lat:       float
    lng:       float
    intensity: float
    count:     int


class TrendPoint(BaseModel):
    month:       str
    accidents:   int
    blackspots:  int


class AnalyticsSummary(BaseModel):
    total_accidents_mtd:  int
    active_blackspots:    int
    high_risk_roads:      int
    avg_risk_score:       float
    blackspot_change_pct: float
    model_accuracy:       float
    last_updated:         str
