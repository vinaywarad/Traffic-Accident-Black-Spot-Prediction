"""
Pydantic v2 schemas for prediction requests and responses.
Matches the api_schema.py contract from Phase 3 exactly.
"""
from typing import Optional, List
from pydantic import BaseModel, Field, field_validator

from app.config import settings

VALID_ROAD_TYPES = {"NH", "SH", "ORR", "City_Road", "Residential", "Service_Road"}
VALID_WEATHER    = {"Clear", "Rainy", "Foggy", "Overcast", "Night-Clear", "Night-Rainy", "Drizzle", "Cloudy"}


class PredictionRequest(BaseModel):
    latitude:          float = Field(..., ge=settings.LAT_MIN, le=settings.LAT_MAX,
                                     description="Latitude within Bengaluru bounds")
    longitude:         float = Field(..., ge=settings.LNG_MIN, le=settings.LNG_MAX,
                                     description="Longitude within Bengaluru bounds")
    hour:              int   = Field(..., ge=0,  le=23)
    month:             int   = Field(..., ge=1,  le=12)
    day_of_week:       int   = Field(..., ge=0,  le=6,
                                     description="0=Monday, 6=Sunday")
    road_type:         str   = Field(..., description="NH|SH|ORR|City_Road|Residential|Service_Road")
    weather:           str   = Field(..., description="Clear|Rainy|Foggy|Overcast|Night-Clear|Night-Rainy")
    speed_limit:       int   = Field(..., ge=20, le=120)
    vehicles_involved: int   = Field(..., ge=1,  le=20)
    road_condition:    Optional[str] = None   # auto-derived from weather if None
    light_condition:   Optional[str] = None   # auto-derived from hour if None

    @field_validator("road_type")
    @classmethod
    def valid_road_type(cls, v: str) -> str:
        if v not in VALID_ROAD_TYPES:
            raise ValueError(f"road_type must be one of {VALID_ROAD_TYPES}")
        return v

    @field_validator("weather")
    @classmethod
    def valid_weather(cls, v: str) -> str:
        if v not in VALID_WEATHER:
            raise ValueError(f"weather must be one of {VALID_WEATHER}")
        return v

    model_config = {
        "json_schema_extra": {
            "example": {
                "latitude": 12.9170, "longitude": 77.6228,
                "hour": 9, "month": 7, "day_of_week": 1,
                "road_type": "ORR", "weather": "Rainy",
                "speed_limit": 80, "vehicles_involved": 2,
            }
        }
    }


class BatchPredictionRequest(BaseModel):
    records:    List[PredictionRequest] = Field(..., min_length=1, max_length=500)
    model_name: Optional[str] = "best"


class FeatureFactor(BaseModel):
    feature:    str
    importance: float
    direction:  str    # increases_risk | decreases_risk
    value:      float


class PredictionResponse(BaseModel):
    is_blackspot:   bool
    risk_score:     float = Field(..., ge=0.0, le=1.0)
    risk_level:     str   # LOW | MEDIUM | HIGH | CRITICAL
    confidence:     float
    top_factors:    List[FeatureFactor] = []
    explanation:    str
    model_used:     str
    threshold_used: float
    location:       dict

    model_config = {
        "json_schema_extra": {
            "example": {
                "is_blackspot": True, "risk_score": 0.87,
                "risk_level": "CRITICAL", "confidence": 0.74,
                "top_factors": [
                    {"feature": "nearest_blackspot_dist", "importance": 0.31,
                     "direction": "increases_risk", "value": 42.5}
                ],
                "explanation": "High risk due to junction proximity during monsoon peak hour.",
                "model_used": "random_forest", "threshold_used": 0.48,
                "location": {"latitude": 12.9170, "longitude": 77.6228},
            }
        }
    }


class BatchPredictionResponse(BaseModel):
    predictions:     List[PredictionResponse]
    total:           int
    blackspot_count: int
    avg_risk_score:  float
    processing_ms:   float
