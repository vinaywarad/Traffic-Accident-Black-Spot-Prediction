"""
Shared response schemas: errors, health checks, model info.
"""
from pydantic import BaseModel
from typing import Optional


class ErrorResponse(BaseModel):
    error:  str
    detail: Optional[str] = None
    code:   Optional[int] = None


class HealthCheck(BaseModel):
    status:       str
    timestamp:    float
    model_loaded: Optional[bool]  = None
    model_name:   Optional[str]   = None
    auc_roc:      Optional[float] = None
    memory_mb:    Optional[float] = None
    cpu_pct:      Optional[float] = None
    uptime_s:     Optional[float] = None


class ModelInfo(BaseModel):
    model_name:        str
    trained_at:        str
    feature_count:     int
    optimal_threshold: float
    metrics:           dict
    shap_top_features: list = []
