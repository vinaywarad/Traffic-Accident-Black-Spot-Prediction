"""
Coordinate validation for Bengaluru accident data.
Checks lat/lng bounds, detects swapped coordinates, and flags suspicious points.
"""
import pandas as pd
import numpy as np
from loguru import logger

from src.config import BENGALURU_BOUNDS, BENGALURU_CENTER

# Bengaluru bounds
LAT_MIN, LAT_MAX = BENGALURU_BOUNDS["lat"]
LNG_MIN, LNG_MAX = BENGALURU_BOUNDS["lng"]


def validate_coordinates(df: pd.DataFrame) -> pd.DataFrame:
    """
    Validate and repair coordinate columns in the DataFrame.

    Operations:
        - Detect and fix swapped lat/lng (lat in lng range, lng in lat range)
        - Drop rows with coordinates outside Bengaluru bounds
        - Flag rows with coordinates suspiciously far from city center

    Args:
        df: DataFrame with 'latitude' and 'longitude' columns.

    Returns:
        DataFrame with validated coordinates and a 'coord_flag' column.
    """
    df = df.copy()

    if "latitude" not in df.columns or "longitude" not in df.columns:
        logger.warning("No latitude/longitude columns found — skipping validation")
        return df

    df["latitude"]  = pd.to_numeric(df["latitude"],  errors="coerce")
    df["longitude"] = pd.to_numeric(df["longitude"], errors="coerce")

    # Detect swapped coordinates
    swapped_mask = (
        df["latitude"].between(LNG_MIN, LNG_MAX) &
        df["longitude"].between(LAT_MIN, LAT_MAX)
    )
    if swapped_mask.sum() > 0:
        logger.warning(f"Detected {swapped_mask.sum()} rows with swapped lat/lng — fixing")
        df.loc[swapped_mask, ["latitude", "longitude"]] = (
            df.loc[swapped_mask, ["longitude", "latitude"]].values
        )

    # Drop out-of-bounds
    before = len(df)
    in_bounds = (
        df["latitude"].between(LAT_MIN, LAT_MAX) &
        df["longitude"].between(LNG_MIN, LNG_MAX)
    )
    df = df[in_bounds].copy()
    dropped = before - len(df)
    if dropped > 0:
        logger.info(f"Dropped {dropped} records outside Bengaluru bounds")

    # Flag points far from city center (> 30 km)
    center_lat, center_lng = BENGALURU_CENTER
    df["dist_from_center_km"] = np.sqrt(
        ((df["latitude"]  - center_lat) * 111) ** 2 +
        ((df["longitude"] - center_lng) * 111 * np.cos(np.radians(center_lat))) ** 2
    ).round(2)
    df["coord_flag"] = (df["dist_from_center_km"] > 30).astype(int)

    flagged = df["coord_flag"].sum()
    if flagged > 0:
        logger.info(f"Flagged {flagged} records > 30 km from city center")

    return df.reset_index(drop=True)


def get_coordinate_stats(df: pd.DataFrame) -> dict:
    """
    Return summary statistics for coordinate columns.

    Args:
        df: DataFrame with latitude/longitude columns.

    Returns:
        Dict with min/max/mean and out-of-bounds count.
    """
    if "latitude" not in df.columns:
        return {}
    return {
        "lat_min":       df["latitude"].min(),
        "lat_max":       df["latitude"].max(),
        "lat_mean":      df["latitude"].mean(),
        "lng_min":       df["longitude"].min(),
        "lng_max":       df["longitude"].max(),
        "lng_mean":      df["longitude"].mean(),
        "null_coords":   df[["latitude", "longitude"]].isna().any(axis=1).sum(),
        "flagged_far":   df["coord_flag"].sum() if "coord_flag" in df.columns else 0,
    }
