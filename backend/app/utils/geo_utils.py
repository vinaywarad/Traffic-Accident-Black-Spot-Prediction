"""
Geospatial utilities and human-readable explanation builder.
"""
import math
from typing import List


EARTH_RADIUS_M = 6_371_000

FACTOR_DESCRIPTIONS = {
    "dist_to_nearest_junction": "junction proximity",
    "nearest_blackspot_dist":   "proximity to known black spot",
    "is_monsoon":               "monsoon season conditions",
    "is_peak_hour":             "peak hour traffic",
    "is_morning_peak":          "morning rush hour",
    "is_evening_peak":          "evening rush hour",
    "road_risk_score":          "high-risk road type",
    "is_night":                 "night-time driving",
    "weather_encoded":          "adverse weather",
    "road_condition_encoded":   "poor road condition",
    "num_junctions_500m":       "multiple nearby junctions",
    "accident_density_1km":     "high historical accident density",
    "accident_density_500m":    "high local accident density",
    "is_weekend":               "weekend traffic patterns",
    "is_festival_month":        "festival season",
    "speed_limit":              "high speed limit zone",
    "vehicles_involved":        "multi-vehicle scenario",
}


def haversine_distance(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
    """
    Calculate the great-circle distance between two points in meters.

    Args:
        lat1, lng1: First point coordinates.
        lat2, lng2: Second point coordinates.

    Returns:
        Distance in meters.
    """
    dlat = math.radians(lat2 - lat1)
    dlng = math.radians(lng2 - lng1)
    a = (math.sin(dlat / 2) ** 2 +
         math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) *
         math.sin(dlng / 2) ** 2)
    return EARTH_RADIUS_M * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))


def generate_explanation(factors: list, request) -> str:
    """
    Build a one-line human-readable explanation from top SHAP factors.

    Args:
        factors: List of FeatureFactor objects.
        request: PredictionRequest instance.

    Returns:
        Human-readable explanation string.
    """
    if not factors:
        return "Risk assessment based on road and temporal features."

    risk_parts = []
    for f in factors[:3]:
        if f.direction == "increases_risk" and f.feature in FACTOR_DESCRIPTIONS:
            risk_parts.append(FACTOR_DESCRIPTIONS[f.feature])

    if risk_parts:
        return f"High risk due to {', '.join(risk_parts)}."

    return "Elevated risk based on combined road and traffic features."


def validate_bengaluru_coords(lat: float, lng: float) -> bool:
    """Check if coordinates are within Bengaluru bounds."""
    return 12.75 <= lat <= 13.18 and 77.38 <= lng <= 77.82
