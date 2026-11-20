"""
Pydantic validation schemas for all pipeline datasets.
Used to validate records before and after cleaning.
"""
from datetime import date
from typing import Optional, Literal

from pydantic import BaseModel, Field, field_validator, model_validator

SeverityType = Literal["LOW", "MEDIUM", "HIGH", "CRITICAL"]
RoadType     = Literal["NH", "SH", "ORR", "City_Road", "Residential", "Service_Road"]


class AccidentRecord(BaseModel):
    """Schema for a single cleaned accident record."""

    accident_id:       str
    date:              date
    latitude:          float = Field(..., ge=12.75, le=13.18)
    longitude:         float = Field(..., ge=77.38, le=77.82)
    severity:          SeverityType
    road_type:         str
    weather:           str
    vehicles_involved: int   = Field(..., ge=1, le=20)
    casualties:        int   = Field(..., ge=0)
    fatalities:        int   = Field(..., ge=0)
    is_blackspot:      Optional[int] = Field(None, ge=0, le=1)

    @field_validator("severity")
    @classmethod
    def valid_severity(cls, v: str) -> str:
        valid = {"LOW", "MEDIUM", "HIGH", "CRITICAL"}
        if v not in valid:
            raise ValueError(f"severity must be one of {valid}, got '{v}'")
        return v

    @model_validator(mode="after")
    def fatalities_lte_casualties(self) -> "AccidentRecord":
        if self.fatalities > self.casualties:
            raise ValueError(
                f"fatalities ({self.fatalities}) cannot exceed "
                f"casualties ({self.casualties})"
            )
        return self


class FeatureRecord(BaseModel):
    """Schema for a single ML-ready feature record."""

    dist_to_nearest_junction: float = Field(..., ge=0)
    num_junctions_500m:       int   = Field(..., ge=0)
    road_risk_score:          int   = Field(..., ge=1, le=5)
    accident_density_1km:     float = Field(..., ge=0)
    accident_density_500m:    float = Field(..., ge=0)
    nearest_blackspot_dist:   float = Field(..., ge=0)
    hour_sin:                 float = Field(..., ge=-1, le=1)
    hour_cos:                 float = Field(..., ge=-1, le=1)
    month_sin:                float = Field(..., ge=-1, le=1)
    month_cos:                float = Field(..., ge=-1, le=1)
    day_sin:                  float = Field(..., ge=-1, le=1)
    day_cos:                  float = Field(..., ge=-1, le=1)
    is_peak_hour:             int   = Field(..., ge=0, le=1)
    is_night:                 int   = Field(..., ge=0, le=1)
    is_weekend:               int   = Field(..., ge=0, le=1)
    is_monsoon:               int   = Field(..., ge=0, le=1)
    is_festival_month:        int   = Field(..., ge=0, le=1)
    days_since_epoch:         int   = Field(..., ge=0)
    speed_limit:              float = Field(..., ge=0, le=120)
    vehicles_involved:        int   = Field(..., ge=1, le=20)
    weather_encoded:          int   = Field(..., ge=1, le=5)
    road_condition_encoded:   int   = Field(..., ge=1, le=5)
    light_condition_encoded:  int   = Field(..., ge=1, le=4)
    is_blackspot:             Optional[int] = Field(None, ge=0, le=1)


class WeatherRecord(BaseModel):
    """Schema for a daily weather record."""

    date:              date
    temperature_max:   float = Field(..., ge=10, le=50)
    temperature_min:   float = Field(..., ge=5,  le=45)
    rainfall_mm:       float = Field(..., ge=0)
    humidity_pct:      float = Field(..., ge=0, le=100)
    wind_speed_kmh:    float = Field(..., ge=0)
    weather_condition: str


class BlackSpotRecord(BaseModel):
    """Schema for a known black spot location."""

    name:     str
    lat:      float = Field(..., ge=12.75, le=13.18)
    lng:      float = Field(..., ge=77.38, le=77.82)
    severity: SeverityType
