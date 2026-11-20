"""
Merge accident data with weather and road network data.
Produces the unified interim dataset for feature engineering.
"""
from pathlib import Path

import pandas as pd
from loguru import logger

from src.config import INTERIM_DIR


def merge_all_sources(
    accidents: pd.DataFrame,
    weather: pd.DataFrame = None,
    roads_gdf=None,
) -> pd.DataFrame:
    """
    Merge accident records with weather and road data.

    Args:
        accidents: Cleaned accident DataFrame.
        weather: Optional weather DataFrame (merged by date).
        roads_gdf: Optional GeoDataFrame of road segments.

    Returns:
        Merged DataFrame saved to interim/weather_merged.parquet.
    """
    df = accidents.copy()

    # Merge weather by date
    if weather is not None and not weather.empty:
        df["date"] = pd.to_datetime(df["date"]).dt.normalize()
        weather["date"] = pd.to_datetime(weather["date"]).dt.normalize()

        weather_cols = ["date", "rainfall_mm", "humidity_pct", "temperature_max"]
        weather_cols = [c for c in weather_cols if c in weather.columns]

        df = df.merge(weather[weather_cols], on="date", how="left")
        logger.info(f"Merged weather: {df['rainfall_mm'].notna().sum()} records matched")

    # Add road-level attributes from OSM if available
    if roads_gdf is not None:
        df = _spatial_join_roads(df, roads_gdf)

    # Fill remaining nulls with sensible defaults
    if "rainfall_mm" in df.columns:
        df["rainfall_mm"] = df["rainfall_mm"].fillna(0.0)
    if "humidity_pct" in df.columns:
        df["humidity_pct"] = df["humidity_pct"].fillna(60.0)

    logger.success(f"Merged dataset: {len(df)} records, {df.shape[1]} columns")
    return df


def _spatial_join_roads(
    df: pd.DataFrame,
    roads_gdf,
    radius_deg: float = 0.001,
) -> pd.DataFrame:
    """
    Attach nearest road attributes to each accident point.

    Args:
        df: Accident DataFrame with latitude/longitude.
        roads_gdf: GeoDataFrame of road segments.
        radius_deg: Search radius in degrees (~100m).

    Returns:
        DataFrame with road attributes added.
    """
    try:
        import geopandas as gpd
        from shapely.geometry import Point
        from shapely.ops import nearest_points

        geometry = [Point(lng, lat) for lat, lng in zip(df["latitude"], df["longitude"])]
        acc_gdf = gpd.GeoDataFrame(df, geometry=geometry, crs="EPSG:4326")

        road_union = roads_gdf.geometry.unary_union

        def get_nearest_road_attrs(pt):
            nearest = nearest_points(pt, road_union)[1]
            candidates = roads_gdf[roads_gdf.geometry.distance(pt) < radius_deg]
            if candidates.empty:
                return pd.Series({"osm_road_type": None, "osm_lanes": None, "osm_maxspeed": None})
            row = candidates.iloc[0]
            return pd.Series({
                "osm_road_type": row.get("highway", None),
                "osm_lanes":     row.get("lanes", None),
                "osm_maxspeed":  row.get("maxspeed", None),
            })

        road_attrs = acc_gdf.geometry.apply(get_nearest_road_attrs)
        df = pd.concat([df, road_attrs], axis=1)
        logger.info("Attached OSM road attributes to accident records")
    except Exception as e:
        logger.warning(f"Road spatial join failed: {e} — skipping")

    return df


def save_interim(df: pd.DataFrame, name: str) -> Path:
    """
    Save a DataFrame to the interim directory as Parquet.

    Args:
        df: DataFrame to save.
        name: Filename without extension.

    Returns:
        Path to saved file.
    """
    INTERIM_DIR.mkdir(parents=True, exist_ok=True)
    path = INTERIM_DIR / f"{name}.parquet"
    df.to_parquet(path, index=False)
    logger.info(f"Saved interim data: {path} ({len(df)} rows)")
    return path
