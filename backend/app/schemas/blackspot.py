"""
Schemas for known Bengaluru black spot locations.
"""
from typing import List, Optional
from pydantic import BaseModel


class BlackSpot(BaseModel):
    id:               str
    name:             str
    lat:              float
    lng:              float
    severity:         str
    risk_score:       float
    annual_accidents: int
    fatalities_ytd:   int
    road_type:        str
    primary_cause:    str


class BlackSpotList(BaseModel):
    spots: List[BlackSpot]
    total: int
