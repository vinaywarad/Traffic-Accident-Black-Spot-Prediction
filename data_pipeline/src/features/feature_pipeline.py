"""
Orchestrates all feature modules into the final ML-ready feature matrix.
Runs spatial, temporal, environmental, and road features in sequence.
"""
from pathlib import Path

import pandas as pd
from loguru import logger

from src.config import FEATURE_COLUMNS, TARGET_COLUMN, PROCESSED_DIR
from src.features.temporal_features     import add_temporal_features
from src.features.spatial_features      import add_spatial_features
from src.features.environmental_features import add_environmental_features
from src.features.road_features         import add_road_features
from src.features.blackspot_labeler     import label_blackspots, label_blackspots_fast


def build_feature_matrix(
    df: pd.DataFrame,
    junctions_gdf=None,
    roads_gdf=None,
    label_method: str = "fast",
) -> pd.DataFrame:
    """
    Run the full feature engineering pipeline on a cleaned accident DataFrame.

    Steps:
        1. Temporal features (cyclic encoding, peak hours, monsoon flags)
        2. Road features (speed limit, highway flags, lane count)
        3. Environmental features (weather/road/light encoding)
        4. Spatial features (junction distance, accident density, blackspot dist)
        5. Black spot labeling (if is_blackspot not already present)

    Args:
        df: Cleaned accident DataFrame.
        junctions_gdf: Optional GeoDataFrame of road junctions.
        roads_gdf: Optional GeoDataFrame of road segments.
        label_method: 'fast' (spatial only) or 'full' (spatial + temporal window).

    Returns:
        Feature-engineered DataFrame.
    """
    logger.info(f"Building feature matrix from {len(df)} records...")

    df = add_temporal_features(df)
    logger.info("✓ Temporal features")

    df = add_road_features(df, roads_gdf=roads_gdf)
    logger.info("✓ Road features")

    df = add_environmental_features(df)
    logger.info("✓ Environmental features")

    df = add_spatial_features(df, junctions_gdf=junctions_gdf, roads_gdf=roads_gdf)
    logger.info("✓ Spatial features")

    # Label black spots if not already present
    if "is_blackspot" not in df.columns or df["is_blackspot"].isna().all():
        if label_method == "full":
            df = label_blackspots(df)
        else:
            df = label_blackspots_fast(df)
        logger.info("✓ Black spot labeling")
    else:
        logger.info("✓ Black spot labels already present — skipping labeling")

    logger.success(
        f"Feature matrix complete: {len(df)} rows × {df.shape[1]} columns | "
        f"black spot rate: {df[TARGET_COLUMN].mean():.2%}"
    )
    return df


def get_feature_matrix(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.Series]:
    """
    Extract X (features) and y (target) from the full feature DataFrame.

    Only includes columns defined in FEATURE_COLUMNS that are present in df.

    Args:
        df: Feature-engineered DataFrame.

    Returns:
        Tuple of (X DataFrame, y Series).
    """
    available = [c for c in FEATURE_COLUMNS if c in df.columns]
    missing   = [c for c in FEATURE_COLUMNS if c not in df.columns]

    if missing:
        logger.warning(f"Missing feature columns (will be skipped): {missing}")

    X = df[available].copy()
    y = df[TARGET_COLUMN].copy()

    # Drop any remaining NaN rows
    valid_mask = X.notna().all(axis=1) & y.notna()
    X = X[valid_mask]
    y = y[valid_mask]

    logger.info(f"Feature matrix: {X.shape} | Target: {y.value_counts().to_dict()}")
    return X, y


def save_feature_matrix(df: pd.DataFrame, name: str = "features_final") -> Path:
    """
    Save the full feature DataFrame to processed directory as Parquet.

    Args:
        df: Feature-engineered DataFrame.
        name: Output filename without extension.

    Returns:
        Path to saved file.
    """
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    path = PROCESSED_DIR / f"{name}.parquet"
    df.to_parquet(path, index=False)
    logger.info(f"Saved feature matrix: {path} ({len(df)} rows, {df.shape[1]} cols)")
    return path
