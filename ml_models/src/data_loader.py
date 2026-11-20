"""
Load and validate the ML-ready parquet splits produced by the data pipeline.
Provides synthetic fallback data when pipeline outputs are not yet available.
"""
from pathlib import Path
from typing import Optional

import numpy as np
import pandas as pd
from loguru import logger

from src.config import (
    X_TRAIN_PATH, X_TEST_PATH, Y_TRAIN_PATH, Y_TEST_PATH,
    RANDOM_STATE,
)

# Feature columns expected in the parquet files
EXPECTED_FEATURES = [
    "dist_to_nearest_junction", "num_junctions_500m", "road_risk_score",
    "accident_density_1km", "accident_density_500m", "nearest_blackspot_dist",
    "hour_sin", "hour_cos", "month_sin", "month_cos", "day_sin", "day_cos",
    "is_peak_hour", "is_night", "is_weekend", "is_monsoon", "is_festival_month",
    "days_since_epoch", "speed_limit", "vehicles_involved",
    "weather_encoded", "road_condition_encoded", "light_condition_encoded",
]


def load_splits(
    x_train_path: Path = X_TRAIN_PATH,
    x_test_path:  Path = X_TEST_PATH,
    y_train_path: Path = Y_TRAIN_PATH,
    y_test_path:  Path = Y_TEST_PATH,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.Series, pd.Series]:
    """
    Load train/test splits from parquet files.

    Falls back to synthetic data if files are not found, so the ML pipeline
    can run end-to-end without requiring the data pipeline to have run first.

    Args:
        x_train_path, x_test_path: Feature parquet paths.
        y_train_path, y_test_path: Label parquet paths.

    Returns:
        Tuple of (X_train, X_test, y_train, y_test).
    """
    paths = [x_train_path, x_test_path, y_train_path, y_test_path]
    if all(Path(p).exists() for p in paths):
        logger.info("Loading data splits from parquet files...")
        X_train = pd.read_parquet(x_train_path)
        X_test  = pd.read_parquet(x_test_path)
        y_train = _load_series(y_train_path, "is_blackspot")
        y_test  = _load_series(y_test_path,  "is_blackspot")
        _validate_splits(X_train, X_test, y_train, y_test)
    else:
        logger.warning("Parquet splits not found — generating synthetic data for demo")
        X_train, X_test, y_train, y_test = _generate_synthetic_splits()

    logger.info(
        f"Data loaded | train: {X_train.shape} | test: {X_test.shape} | "
        f"train BS rate: {y_train.mean():.2%} | test BS rate: {y_test.mean():.2%}"
    )
    return X_train, X_test, y_train, y_test


def _load_series(path: Path, col: str) -> pd.Series:
    """Load a single-column parquet as a Series."""
    df = pd.read_parquet(path)
    if col in df.columns:
        return df[col].reset_index(drop=True)
    return df.iloc[:, 0].reset_index(drop=True)


def _validate_splits(
    X_train: pd.DataFrame,
    X_test:  pd.DataFrame,
    y_train: pd.Series,
    y_test:  pd.Series,
) -> None:
    """Assert shapes are consistent and features are present."""
    assert len(X_train) == len(y_train), "X_train / y_train length mismatch"
    assert len(X_test)  == len(y_test),  "X_test / y_test length mismatch"
    assert len(X_train) > 0, "Empty training set"
    assert len(X_test)  > 0, "Empty test set"

    missing = [f for f in EXPECTED_FEATURES if f not in X_train.columns]
    if missing:
        logger.warning(f"Missing expected features: {missing}")

    logger.info(
        f"Validation passed | "
        f"train cols: {X_train.shape[1]} | test cols: {X_test.shape[1]}"
    )


def _generate_synthetic_splits(
    n_train: int = 4000,
    n_test:  int = 1000,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.Series, pd.Series]:
    """
    Generate synthetic ML-ready feature data for demo/testing.
    Mimics the output of the data pipeline's feature engineering stage.
    """
    rng = np.random.default_rng(RANDOM_STATE)

    def _make_X(n: int, bs_rate: float = 0.15) -> tuple[pd.DataFrame, pd.Series]:
        y = pd.Series(
            rng.choice([0, 1], size=n, p=[1 - bs_rate, bs_rate]),
            name="is_blackspot",
        )
        # Features correlated with label for realistic model performance
        signal = y.values.astype(float)
        X = pd.DataFrame({
            "dist_to_nearest_junction": rng.uniform(50, 800, n) - signal * 200,
            "num_junctions_500m":       rng.integers(1, 8, n) + (signal * 2).astype(int),
            "road_risk_score":          rng.integers(1, 6, n),
            "accident_density_1km":     rng.exponential(3, n) + signal * 5,
            "accident_density_500m":    rng.exponential(1.5, n) + signal * 3,
            "nearest_blackspot_dist":   rng.uniform(100, 5000, n) - signal * 1500,
            "hour_sin":                 np.sin(2 * np.pi * rng.integers(0, 24, n) / 24),
            "hour_cos":                 np.cos(2 * np.pi * rng.integers(0, 24, n) / 24),
            "month_sin":                np.sin(2 * np.pi * rng.integers(1, 13, n) / 12),
            "month_cos":                np.cos(2 * np.pi * rng.integers(1, 13, n) / 12),
            "day_sin":                  np.sin(2 * np.pi * rng.integers(0, 7, n) / 7),
            "day_cos":                  np.cos(2 * np.pi * rng.integers(0, 7, n) / 7),
            "is_peak_hour":             rng.integers(0, 2, n),
            "is_night":                 rng.integers(0, 2, n),
            "is_weekend":               rng.integers(0, 2, n),
            "is_monsoon":               rng.integers(0, 2, n),
            "is_festival_month":        rng.integers(0, 2, n),
            "days_since_epoch":         rng.integers(0, 1460, n),
            "speed_limit":              rng.choice([30, 40, 60, 80], n),
            "vehicles_involved":        rng.integers(1, 5, n),
            "weather_encoded":          rng.integers(1, 6, n),
            "road_condition_encoded":   rng.integers(1, 6, n),
            "light_condition_encoded":  rng.integers(1, 5, n),
        })
        # Clip to valid ranges
        X["dist_to_nearest_junction"] = X["dist_to_nearest_junction"].clip(lower=10)
        X["nearest_blackspot_dist"]   = X["nearest_blackspot_dist"].clip(lower=50)
        X["accident_density_1km"]     = X["accident_density_1km"].clip(lower=0)
        X["accident_density_500m"]    = X["accident_density_500m"].clip(lower=0)
        return X.reset_index(drop=True), y.reset_index(drop=True)

    X_train, y_train = _make_X(n_train, bs_rate=0.20)
    X_test,  y_test  = _make_X(n_test,  bs_rate=0.15)
    return X_train, X_test, y_train, y_test


def get_val_split(
    X_train: pd.DataFrame,
    y_train: pd.Series,
    val_fraction: float = 0.15,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.Series, pd.Series]:
    """
    Carve out a validation set from the END of the training data.
    Used for XGBoost/LightGBM early stopping.
    Temporal ordering is preserved (last val_fraction rows = most recent).

    Args:
        X_train: Training features.
        y_train: Training labels.
        val_fraction: Fraction of training data to use as validation.

    Returns:
        (X_tr, X_val, y_tr, y_val)
    """
    n_val = max(1, int(len(X_train) * val_fraction))
    X_tr  = X_train.iloc[:-n_val].copy()
    X_val = X_train.iloc[-n_val:].copy()
    y_tr  = y_train.iloc[:-n_val].copy()
    y_val = y_train.iloc[-n_val:].copy()
    logger.info(f"Val split: train={len(X_tr)}, val={len(X_val)}")
    return X_tr, X_val, y_tr, y_val
