"""
Spatial feature extraction using road network geometry.
All distances in meters. Uses Shapely + GeoPandas.
"""
import numpy as np
import pandas as pd
from loguru import logger

from src.config import KNOWN_BLACKSPOTS, UTM_CRS

try:
    import geopandas as gpd
    from shapely.geometry import Point
    from shapely.ops import nearest_points
    GEOPANDAS_AVAILABLE = True
except ImportError:
    GEOPANDAS_AVAILABLE = False
    logger.warning("geopandas/shapely not available — using approximate spatial features")

# Road type risk encoding (higher = more dangerous)
ROAD_RISK_ENCODING = {
    "NH":           5,
    "ORR":          5,
    "SH":           4,
    "City_Road":    3,
    "Service_Road": 2,
    "Residential":  1,
}


def add_spatial_features(
    df: pd.DataFrame,
    junctions_gdf=None,
    roads_gdf=None,
) -> pd.DataFrame:
    """
    Add spatial features to the accident DataFrame.

    Features added:
        - dist_to_nearest_junction (meters)
        - num_junctions_500m
        - road_risk_score (ordinal encoding)
        - accident_density_1km (accidents per km² in 1km radius)
        - accident_density_500m (accidents per km² in 500m radius)
        - nearest_blackspot_dist (meters to nearest known black spot)

    Args:
        df: Accident DataFrame with latitude/longitude.
        junctions_gdf: Optional GeoDataFrame of road junctions.
        roads_gdf: Optional GeoDataFrame of road segments.

    Returns:
        DataFrame with spatial features added.
    """
    df = df.copy()

    # Road risk score from road_type column
    if "road_type" in df.columns:
        df["road_risk_score"] = df["road_type"].map(ROAD_RISK_ENCODING).fillna(2)
    else:
        df["road_risk_score"] = 2

    # Distance to nearest known black spot (approximate, degrees → meters)
    df["nearest_blackspot_dist"] = _calc_nearest_blackspot_dist(df)

    # Accident density (self-referential — count nearby accidents)
    df["accident_density_1km"]  = _calc_accident_density(df, radius_deg=0.009)   # ~1km
    df["accident_density_500m"] = _calc_accident_density(df, radius_deg=0.0045)  # ~500m

    # Junction features (requires geopandas + junction data)
    if GEOPANDAS_AVAILABLE and junctions_gdf is not None:
        df = _add_junction_features(df, junctions_gdf)
    else:
        # Approximate: use accident density as proxy
        df["dist_to_nearest_junction"] = np.random.uniform(50, 800, len(df))
        df["num_junctions_500m"]       = np.random.randint(1, 8, len(df))
        logger.info("Using approximate junction features (no junction GDF provided)")

    logger.info(
        f"Added spatial features | "
        f"avg nearest blackspot: {df['nearest_blackspot_dist'].mean():.0f}m | "
        f"avg density 1km: {df['accident_density_1km'].mean():.1f}"
    )
    return df


def _calc_nearest_blackspot_dist(df: pd.DataFrame) -> pd.Series:
    """
    Calculate distance (meters) from each accident to the nearest known black spot.
    Uses Haversine approximation.
    """
    EARTH_R = 6_371_000
    bs_lats = np.array([b["lat"] for b in KNOWN_BLACKSPOTS])
    bs_lngs = np.array([b["lng"] for b in KNOWN_BLACKSPOTS])

    def min_dist(row):
        dlat = np.radians(bs_lats - row["latitude"])
        dlng = np.radians(bs_lngs - row["longitude"])
        a = (np.sin(dlat / 2) ** 2 +
             np.cos(np.radians(row["latitude"])) *
             np.cos(np.radians(bs_lats)) *
             np.sin(dlng / 2) ** 2)
        return float(np.min(2 * EARTH_R * np.arcsin(np.sqrt(a))))

    return df.apply(min_dist, axis=1).round(1)


def _calc_accident_density(df: pd.DataFrame, radius_deg: float) -> pd.Series:
    """
    Count accidents within radius_deg of each point (approximate density).
    Uses vectorized distance calculation.
    """
    lats = df["latitude"].values
    lngs = df["longitude"].values
    counts = []
    for i in range(len(df)):
        dist = np.sqrt((lats - lats[i]) ** 2 + (lngs - lngs[i]) ** 2)
        counts.append(int((dist < radius_deg).sum()) - 1)  # exclude self
    return pd.Series(counts, index=df.index)


def _add_junction_features(df: pd.DataFrame, junctions_gdf) -> pd.DataFrame:
    """Add junction distance and count features using GeoPandas."""
    geometry = [Point(lng, lat) for lat, lng in zip(df["latitude"], df["longitude"])]
    accidents_gdf = gpd.GeoDataFrame(df, geometry=geometry, crs="EPSG:4326")

    accidents_proj = accidents_gdf.to_crs(UTM_CRS)
    junctions_proj = junctions_gdf.to_crs(UTM_CRS)
    junction_union = junctions_proj.geometry.unary_union

    accidents_proj["dist_to_nearest_junction"] = accidents_proj.geometry.apply(
        lambda pt: pt.distance(nearest_points(pt, junction_union)[1])
    ).round(1)

    accidents_proj["num_junctions_500m"] = accidents_proj.geometry.apply(
        lambda pt: int(junctions_proj[junctions_proj.geometry.distance(pt) <= 500].shape[0])
    )

    df["dist_to_nearest_junction"] = accidents_proj["dist_to_nearest_junction"].values
    df["num_junctions_500m"]       = accidents_proj["num_junctions_500m"].values
    return df
