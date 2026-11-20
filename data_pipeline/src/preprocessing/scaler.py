"""
Feature scaling and normalization for ML preprocessing.
Applies StandardScaler to continuous features, preserves binary/ordinal features.
"""
import pandas as pd
import numpy as np
from loguru import logger
from sklearn.preprocessing import StandardScaler, MinMaxScaler
import joblib
from pathlib import Path

from src.config import PROCESSED_DIR

# Columns to scale (continuous numeric features)
SCALE_COLUMNS = [
    "dist_to_nearest_junction",
    "num_junctions_500m",
    "accident_density_1km",
    "accident_density_500m",
    "nearest_blackspot_dist",
    "speed_limit",
    "vehicles_involved",
    "days_since_epoch",
    "env_risk_score",
]

# Columns to leave as-is (binary flags, cyclic encodings, ordinal)
PASSTHROUGH_COLUMNS = [
    "hour_sin", "hour_cos", "month_sin", "month_cos", "day_sin", "day_cos",
    "is_peak_hour", "is_night", "is_weekend", "is_monsoon", "is_festival_month",
    "is_national_highway", "is_highway", "has_median",
    "weather_encoded", "road_condition_encoded", "light_condition_encoded",
    "road_risk_score", "severity_encoded",
]


def scale_features(
    X_train: pd.DataFrame,
    X_test: pd.DataFrame,
    method: str = "standard",
) -> tuple[pd.DataFrame, pd.DataFrame, object]:
    """
    Fit scaler on training data and transform both train and test sets.

    IMPORTANT: Scaler is fit ONLY on X_train to prevent data leakage.

    Args:
        X_train: Training feature DataFrame.
        X_test: Test feature DataFrame.
        method: 'standard' (StandardScaler) or 'minmax' (MinMaxScaler).

    Returns:
        Tuple of (X_train_scaled, X_test_scaled, fitted_scaler).
    """
    scale_cols = [c for c in SCALE_COLUMNS if c in X_train.columns]

    if not scale_cols:
        logger.warning("No scalable columns found — returning unscaled data")
        return X_train, X_test, None

    scaler = StandardScaler() if method == "standard" else MinMaxScaler()

    X_train_scaled = X_train.copy()
    X_test_scaled  = X_test.copy()

    X_train_scaled[scale_cols] = scaler.fit_transform(X_train[scale_cols])
    X_test_scaled[scale_cols]  = scaler.transform(X_test[scale_cols])

    logger.info(
        f"Scaled {len(scale_cols)} columns using {method} scaler | "
        f"train: {X_train_scaled.shape}, test: {X_test_scaled.shape}"
    )
    return X_train_scaled, X_test_scaled, scaler


def save_scaler(scaler, name: str = "feature_scaler") -> Path:
    """
    Persist the fitted scaler to disk for inference use.

    Args:
        scaler: Fitted sklearn scaler object.
        name: Filename without extension.

    Returns:
        Path to saved scaler file.
    """
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    path = PROCESSED_DIR / f"{name}.joblib"
    joblib.dump(scaler, path)
    logger.info(f"Saved scaler: {path}")
    return path


def load_scaler(name: str = "feature_scaler") -> object:
    """
    Load a previously saved scaler from disk.

    Args:
        name: Filename without extension.

    Returns:
        Loaded sklearn scaler object.
    """
    path = PROCESSED_DIR / f"{name}.joblib"
    scaler = joblib.load(path)
    logger.info(f"Loaded scaler from {path}")
    return scaler
