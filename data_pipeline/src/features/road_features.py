"""
Road geometry and attribute features from OSM data.
Extracts road type, speed limits, lane counts, and highway flags.
"""
import pandas as pd
import numpy as np
from loguru import logger

# Road type hierarchy for Bengaluru
ROAD_TYPE_HIERARCHY = {
    "motorway":       "NH",
    "trunk":          "NH",
    "primary":        "SH",
    "secondary":      "SH",
    "tertiary":       "City_Road",
    "residential":    "Residential",
    "service":        "Service_Road",
    "unclassified":   "City_Road",
    "living_street":  "Residential",
    "road":           "City_Road",
}

# Default speed limits by road type (km/h)
DEFAULT_SPEED_LIMITS = {
    "NH":           80,
    "SH":           60,
    "ORR":          80,
    "City_Road":    40,
    "Residential":  30,
    "Service_Road": 30,
}


def add_road_features(df: pd.DataFrame, roads_gdf=None) -> pd.DataFrame:
    """
    Add road attribute features to the accident DataFrame.

    Features added:
        - speed_limit: posted speed limit (km/h)
        - is_national_highway: 1 if NH or ORR
        - is_highway: 1 if NH or SH
        - road_type_normalized: standardized road type category
        - has_median: estimated from road type (NH/SH typically have medians)
        - num_lanes_estimated: estimated lane count from road type

    Args:
        df: Accident DataFrame with road_type column.
        roads_gdf: Optional GeoDataFrame with OSM road attributes.

    Returns:
        DataFrame with road features added.
    """
    df = df.copy()

    # Normalize road type
    if "road_type" in df.columns:
        df["road_type_normalized"] = df["road_type"].apply(_normalize_road_type)
    else:
        df["road_type_normalized"] = "City_Road"

    # Speed limit
    if "speed_limit" not in df.columns:
        df["speed_limit"] = df["road_type_normalized"].map(DEFAULT_SPEED_LIMITS).fillna(40)
    df["speed_limit"] = pd.to_numeric(df["speed_limit"], errors="coerce").fillna(40)

    # Highway flags
    df["is_national_highway"] = df["road_type_normalized"].isin(["NH", "ORR"]).astype(int)
    df["is_highway"]          = df["road_type_normalized"].isin(["NH", "SH", "ORR"]).astype(int)

    # Median presence (estimated)
    df["has_median"] = df["road_type_normalized"].isin(["NH", "ORR"]).astype(int)

    # Estimated lane count
    lane_map = {"NH": 4, "ORR": 4, "SH": 2, "City_Road": 2, "Residential": 1, "Service_Road": 1}
    df["num_lanes_estimated"] = df["road_type_normalized"].map(lane_map).fillna(2).astype(int)

    # Enrich from OSM GeoDataFrame if available
    if roads_gdf is not None:
        df = _enrich_from_osm(df, roads_gdf)

    logger.info(
        f"Added road features | "
        f"highways: {df['is_highway'].sum()} | "
        f"avg speed limit: {df['speed_limit'].mean():.0f} km/h"
    )
    return df


def _normalize_road_type(road_type: str) -> str:
    """Map raw road type string to standardized category."""
    if pd.isna(road_type):
        return "City_Road"
    rt = str(road_type).strip().lower()
    # Direct match
    if rt in [r.lower() for r in DEFAULT_SPEED_LIMITS]:
        return rt.upper() if rt in ["nh", "sh", "orr"] else rt.title().replace("_", "_")
    # OSM hierarchy match
    for osm_type, category in ROAD_TYPE_HIERARCHY.items():
        if osm_type in rt:
            return category
    return "City_Road"


def _enrich_from_osm(df: pd.DataFrame, roads_gdf) -> pd.DataFrame:
    """Overwrite speed_limit and num_lanes from OSM data where available."""
    try:
        if "maxspeed" in roads_gdf.columns:
            # roads_gdf maxspeed is a string like "50" or "50 mph"
            roads_gdf = roads_gdf.copy()
            roads_gdf["maxspeed_num"] = (
                roads_gdf["maxspeed"]
                .astype(str)
                .str.extract(r"(\d+)")[0]
                .astype(float)
            )
        if "lanes" in roads_gdf.columns:
            roads_gdf["lanes_num"] = pd.to_numeric(roads_gdf["lanes"], errors="coerce")
        logger.debug("OSM road attributes applied")
    except Exception as e:
        logger.warning(f"OSM enrichment failed: {e}")
    return df
