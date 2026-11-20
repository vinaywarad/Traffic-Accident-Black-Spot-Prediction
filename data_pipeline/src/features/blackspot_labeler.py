"""
Creates the target variable: is_blackspot.

A road segment / location is labeled a black spot if it has
3 or more accidents within a 500m radius in any rolling 12-month window.
This follows the WHO / IRC (Indian Roads Congress) definition.
"""
import numpy as np
import pandas as pd
from loguru import logger
from scipy.spatial import cKDTree

from src.config import BLACKSPOT_RADIUS_M, BLACKSPOT_THRESHOLD, WINDOW_MONTHS

EARTH_RADIUS_M = 6_371_000


def label_blackspots(df: pd.DataFrame) -> pd.DataFrame:
    """
    For each accident record, count how many other accidents occurred
    within BLACKSPOT_RADIUS_M in the same rolling 12-month window.
    Mark as black spot if count >= BLACKSPOT_THRESHOLD.

    Uses a KD-tree for efficient spatial querying (O(n log n)).

    Args:
        df: Cleaned accident DataFrame with latitude, longitude, date columns.

    Returns:
        DataFrame with 'is_blackspot' column added (0 or 1).
    """
    df = df.copy().sort_values("date").reset_index(drop=True)
    df["date"] = pd.to_datetime(df["date"])

    coords_rad = np.radians(df[["latitude", "longitude"]].values)
    radius_rad = BLACKSPOT_RADIUS_M / EARTH_RADIUS_M

    tree = cKDTree(coords_rad)
    blackspot_labels = []

    half_window = pd.DateOffset(months=WINDOW_MONTHS // 2)

    for i in range(len(df)):
        # Spatial query: all points within radius
        indices = tree.query_ball_point(coords_rad[i], radius_rad)

        # Temporal filter: within ±6 months
        row_date = df.iloc[i]["date"]
        nearby = df.iloc[indices]
        window_mask = (
            (nearby["date"] >= row_date - half_window) &
            (nearby["date"] <= row_date + half_window)
        )
        nearby_count = window_mask.sum() - 1  # exclude self
        blackspot_labels.append(int(nearby_count >= BLACKSPOT_THRESHOLD))

    df["is_blackspot"] = blackspot_labels

    bs_count = df["is_blackspot"].sum()
    bs_rate  = df["is_blackspot"].mean()
    logger.info(
        f"Black spot labeling complete: {bs_count} / {len(df)} records "
        f"({bs_rate:.2%} rate) | "
        f"radius={BLACKSPOT_RADIUS_M}m, threshold={BLACKSPOT_THRESHOLD}, "
        f"window={WINDOW_MONTHS}mo"
    )
    return df


def label_blackspots_fast(df: pd.DataFrame) -> pd.DataFrame:
    """
    Faster approximate black spot labeling using spatial density only
    (ignores temporal window). Suitable for large datasets.

    Args:
        df: Accident DataFrame with latitude/longitude.

    Returns:
        DataFrame with 'is_blackspot' column.
    """
    df = df.copy()
    coords_rad = np.radians(df[["latitude", "longitude"]].values)
    radius_rad = BLACKSPOT_RADIUS_M / EARTH_RADIUS_M

    tree = cKDTree(coords_rad)
    counts = np.array([
        len(tree.query_ball_point(coords_rad[i], radius_rad)) - 1
        for i in range(len(df))
    ])
    df["is_blackspot"] = (counts >= BLACKSPOT_THRESHOLD).astype(int)

    logger.info(
        f"Fast black spot labeling: {df['is_blackspot'].sum()} / {len(df)} "
        f"({df['is_blackspot'].mean():.2%})"
    )
    return df


def get_blackspot_clusters(df: pd.DataFrame) -> pd.DataFrame:
    """
    Return a summary DataFrame of identified black spot clusters.

    Groups nearby black spot records and returns cluster centroids
    with aggregate statistics.

    Args:
        df: Labeled accident DataFrame.

    Returns:
        DataFrame of black spot clusters with location and stats.
    """
    bs = df[df["is_blackspot"] == 1].copy()
    if bs.empty:
        return pd.DataFrame()

    # Simple grid-based clustering (0.005 deg ≈ 500m)
    bs["grid_lat"] = (bs["latitude"]  / 0.005).round() * 0.005
    bs["grid_lng"] = (bs["longitude"] / 0.005).round() * 0.005

    clusters = bs.groupby(["grid_lat", "grid_lng"]).agg(
        accident_count=("accident_id", "count") if "accident_id" in bs.columns else ("latitude", "count"),
        avg_lat=("latitude",  "mean"),
        avg_lng=("longitude", "mean"),
        fatalities=("fatalities", "sum") if "fatalities" in bs.columns else ("latitude", "count"),
        severity_mode=("severity", lambda x: x.mode()[0]) if "severity" in bs.columns else ("latitude", "first"),
    ).reset_index()

    clusters = clusters.sort_values("accident_count", ascending=False)
    logger.info(f"Identified {len(clusters)} black spot clusters")
    return clusters
