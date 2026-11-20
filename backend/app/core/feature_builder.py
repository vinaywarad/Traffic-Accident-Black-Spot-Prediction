"""
Reconstructs the exact feature vector from an API request.
Feature order and names must match Phase 2 output exactly.
Loads feature_names list from model_metadata.json at startup.
"""
import math
from typing import Union

import numpy as np
import pandas as pd

from app.schemas.predict import PredictionRequest

# ── Encoding maps ─────────────────────────────────────────────────────────────
ROAD_RISK = {
    "NH": 5, "ORR": 5, "SH": 4,
    "City_Road": 3, "Service_Road": 2, "Residential": 1,
}
WEATHER_ENCODE = {
    "Clear": 1, "Overcast": 2, "Cloudy": 2, "Drizzle": 3,
    "Rainy": 4, "Night-Clear": 3, "Night-Rainy": 5, "Foggy": 5,
}
ROAD_COND_ENCODE = {"Dry": 1, "Wet": 3, "Potholed": 4, "Slippery": 5}
LIGHT_ENCODE     = {"Daylight": 1, "Dusk/Dawn": 3, "Dark-Lit": 2, "Dark": 4}

MONSOON_MONTHS   = {6, 7, 8, 9}
FESTIVAL_MONTHS  = {10, 11, 1}
MORNING_PEAK     = set(range(8, 11))
EVENING_PEAK     = set(range(17, 21))
NIGHT_HOURS      = set(range(22, 24)) | set(range(0, 5))

EARTH_R = 6_371_000

# Known Bengaluru junctions for distance approximation
KNOWN_JUNCTIONS = [
    (12.9170, 77.6228), (12.9591, 77.6974), (13.0450, 77.5970),
    (13.0067, 77.6963), (12.9980, 77.6590), (12.9228, 77.6200),
    (12.9307, 77.6784), (12.8353, 77.6772), (13.0290, 77.5160),
    (12.9087, 77.4824),
]

KNOWN_BLACKSPOTS = [
    (12.9170, 77.6228), (12.9591, 77.6974), (13.0450, 77.5970),
    (13.0067, 77.6963), (12.9980, 77.6590), (12.9228, 77.6200),
    (12.9307, 77.6784), (12.8353, 77.6772),
]


def _haversine(lat1, lng1, lat2, lng2) -> float:
    dlat = math.radians(lat2 - lat1)
    dlng = math.radians(lng2 - lng1)
    a = (math.sin(dlat / 2) ** 2 +
         math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) *
         math.sin(dlng / 2) ** 2)
    return EARTH_R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))


def _min_dist(lat: float, lng: float, points: list) -> float:
    return min(_haversine(lat, lng, p[0], p[1]) for p in points)


def build_feature_vector(
    req: PredictionRequest,
    feature_names: list,
    as_dict: bool = False,
) -> Union[pd.DataFrame, dict]:
    """
    Build the feature dict matching Phase 2's feature_pipeline output.

    Spatial features use coordinate-based heuristics since full OSMnx
    cannot run at request time. These approximate the training-time values.

    Args:
        req: Validated PredictionRequest.
        feature_names: Ordered list from model_metadata.json.
        as_dict: If True, return dict instead of DataFrame.

    Returns:
        Single-row DataFrame (or dict if as_dict=True).
    """
    h = req.hour
    m = req.month
    d = req.day_of_week

    # Derive optional fields
    road_condition = req.road_condition or ("Wet" if req.weather == "Rainy" else "Dry")
    light_condition = req.light_condition or ("Dark" if h in NIGHT_HOURS else "Daylight")

    feats = {
        # Spatial
        "dist_to_nearest_junction": _min_dist(req.latitude, req.longitude, KNOWN_JUNCTIONS),
        "num_junctions_500m":       _approx_junction_count(req.road_type),
        "road_risk_score":          ROAD_RISK.get(req.road_type, 3),
        "accident_density_1km":     0.0,
        "accident_density_500m":    0.0,
        "nearest_blackspot_dist":   _min_dist(req.latitude, req.longitude, KNOWN_BLACKSPOTS),

        # Temporal
        "hour_sin":           math.sin(2 * math.pi * h / 24),
        "hour_cos":           math.cos(2 * math.pi * h / 24),
        "month_sin":          math.sin(2 * math.pi * m / 12),
        "month_cos":          math.cos(2 * math.pi * m / 12),
        "day_sin":            math.sin(2 * math.pi * d / 7),
        "day_cos":            math.cos(2 * math.pi * d / 7),
        "is_peak_hour":       int(h in MORNING_PEAK | EVENING_PEAK),
        "is_morning_peak":    int(h in MORNING_PEAK),
        "is_evening_peak":    int(h in EVENING_PEAK),
        "is_night":           int(h in NIGHT_HOURS),
        "is_weekend":         int(d >= 5),
        "is_monsoon":         int(m in MONSOON_MONTHS),
        "is_pre_monsoon":     int(m in {3, 4, 5}),
        "is_festival_month":  int(m in FESTIVAL_MONTHS),
        "days_since_epoch":   0,

        # Road
        "speed_limit":         float(req.speed_limit),
        "vehicles_involved":   float(req.vehicles_involved),
        "is_national_highway": int(req.road_type in {"NH", "ORR"}),
        "is_highway":          int(req.road_type in {"NH", "SH", "ORR"}),
        "has_median":          int(req.road_type in {"NH", "ORR"}),
        "num_lanes_estimated": {"NH": 4, "ORR": 4, "SH": 2, "City_Road": 2,
                                "Residential": 1, "Service_Road": 1}.get(req.road_type, 2),

        # Environmental
        "weather_encoded":          WEATHER_ENCODE.get(req.weather, 1),
        "road_condition_encoded":   ROAD_COND_ENCODE.get(road_condition, 1),
        "light_condition_encoded":  LIGHT_ENCODE.get(light_condition, 1),
        "is_adverse_weather":       int(req.weather in {"Rainy", "Foggy", "Night-Rainy"}),
        "is_wet_road":              int(road_condition in {"Wet", "Slippery"}),
        "env_risk_score":           (WEATHER_ENCODE.get(req.weather, 1) *
                                     ROAD_COND_ENCODE.get(road_condition, 1) *
                                     LIGHT_ENCODE.get(light_condition, 1)),
    }

    # Align to exact feature_names order — fill missing with 0.0
    ordered = {k: float(feats.get(k, 0.0)) for k in feature_names}

    if as_dict:
        return ordered
    return pd.DataFrame([ordered])


def _approx_junction_count(road_type: str) -> int:
    return {"NH": 3, "ORR": 4, "SH": 2, "City_Road": 5,
            "Residential": 2, "Service_Road": 1}.get(road_type, 2)
