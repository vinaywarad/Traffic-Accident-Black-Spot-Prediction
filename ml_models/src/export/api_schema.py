"""
Input/output schema for the FastAPI backend (Phase 4).
Build the Phase 4 API against this contract.
"""
from typing import Optional
from pydantic import BaseModel, Field


# ── Prediction Request (what the frontend sends) ─────────────────────────────

class PredictionRequest(BaseModel):
    """
    Input schema for the /predict endpoint.
    All fields required except spatial features computed server-side.
    """
    latitude:                 float = Field(..., ge=12.75, le=13.18,
                                            description="Bengaluru latitude")
    longitude:                float = Field(..., ge=77.38, le=77.82,
                                            description="Bengaluru longitude")
    hour:                     int   = Field(..., ge=0, le=23)
    month:                    int   = Field(..., ge=1, le=12)
    day_of_week:              int   = Field(..., ge=0, le=6,
                                            description="0=Monday, 6=Sunday")
    road_type:                str   = Field(..., description="NH/SH/ORR/City_Road/Residential/Service_Road")
    weather:                  str   = Field(..., description="Clear/Rainy/Foggy/Overcast/Night-Clear/Night-Rainy")
    speed_limit:              int   = Field(..., ge=0, le=120)
    vehicles_involved:        int   = Field(..., ge=1, le=20)

    # Optional — computed server-side from lat/lng if not provided
    dist_to_nearest_junction: Optional[float] = Field(None, ge=0)
    num_junctions_500m:       Optional[int]   = Field(None, ge=0)
    accident_density_1km:     Optional[float] = Field(None, ge=0)

    class Config:
        json_schema_extra = {
            "example": {
                "latitude":          12.9170,
                "longitude":         77.6228,
                "hour":              8,
                "month":             7,
                "day_of_week":       0,
                "road_type":         "ORR",
                "weather":           "Rainy",
                "speed_limit":       80,
                "vehicles_involved": 2,
            }
        }


# ── Prediction Response (what the API returns) ───────────────────────────────

class ContributingFactor(BaseModel):
    feature:     str
    shap_value:  Optional[float] = None
    direction:   str   # "increases_risk" | "decreases_risk"
    description: Optional[str] = None


class PredictionResponse(BaseModel):
    """
    Output schema for the /predict endpoint.
    """
    is_blackspot:             bool
    risk_score:               float = Field(..., ge=0.0, le=1.0,
                                            description="Probability of being a black spot")
    risk_level:               str   = Field(..., description="LOW/MEDIUM/HIGH/CRITICAL")
    confidence:               float = Field(..., ge=0.0, le=1.0)
    top_contributing_factors: list[ContributingFactor]
    model_used:               str
    threshold_used:           float

    class Config:
        json_schema_extra = {
            "example": {
                "is_blackspot":  True,
                "risk_score":    0.87,
                "risk_level":    "CRITICAL",
                "confidence":    0.87,
                "top_contributing_factors": [
                    {"feature": "nearest_blackspot_dist", "direction": "increases_risk",
                     "description": "Within 500m of a known black spot"},
                ],
                "model_used":    "xgboost",
                "threshold_used": 0.42,
            }
        }


# ── Batch Prediction Request ──────────────────────────────────────────────────

class BatchPredictionRequest(BaseModel):
    """Input schema for the /predict/batch endpoint."""
    records: list[PredictionRequest] = Field(..., max_length=1000)


class BatchPredictionResponse(BaseModel):
    """Output schema for the /predict/batch endpoint."""
    predictions:   list[PredictionResponse]
    total:         int
    blackspot_count: int
    processing_time_ms: float


# ── Model Info Response ───────────────────────────────────────────────────────

class ModelInfoResponse(BaseModel):
    """Response for the /model/info endpoint."""
    model_name:        str
    trained_at:        str
    feature_count:     int
    optimal_threshold: float
    metrics:           dict
    shap_top_features: list


# ── Risk level helper ─────────────────────────────────────────────────────────

def score_to_risk_level(score: float) -> str:
    """Convert probability score to risk level string."""
    if score >= 0.75:
        return "CRITICAL"
    if score >= 0.55:
        return "HIGH"
    if score >= 0.35:
        return "MEDIUM"
    return "LOW"
