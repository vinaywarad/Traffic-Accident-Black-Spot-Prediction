"""
Train/test splitting with spatial-awareness to prevent data leakage.

IMPORTANT: Random split causes spatial data leakage — nearby points
end up in both train and test sets. Use temporal split instead.
"""
import pandas as pd
import numpy as np
from loguru import logger
from pathlib import Path

from src.config import TEST_YEAR, PROCESSED_DIR


def temporal_split(
    df: pd.DataFrame,
    test_year: int = TEST_YEAR,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    Split data temporally: train on years before test_year, test on test_year.

    Prevents future data leaking into training set.

    Args:
        df: Feature-engineered DataFrame with 'year' column.
        test_year: Year to use as test set (default: 2023).

    Returns:
        Tuple of (train_df, test_df).
    """
    if "year" not in df.columns:
        df = df.copy()
        df["year"] = pd.to_datetime(df["date"]).dt.year

    train = df[df["year"] < test_year].copy()
    test  = df[df["year"] == test_year].copy()

    logger.info(
        f"Temporal split (test_year={test_year}): "
        f"train={len(train)} ({train['year'].min()}–{train['year'].max()}) | "
        f"test={len(test)} ({test_year})"
    )

    if len(test) == 0:
        logger.warning(f"No records found for test_year={test_year}. "
                       "Check your data date range.")

    return train, test


def spatial_block_split(
    df: pd.DataFrame,
    test_fraction: float = 0.2,
    grid_size_deg: float = 0.05,
    random_state: int = 42,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    Spatial block split: assign geographic grid cells to train or test.

    Prevents nearby points from appearing in both sets.

    Args:
        df: DataFrame with latitude/longitude.
        test_fraction: Fraction of grid cells to assign to test.
        grid_size_deg: Size of each grid cell in degrees (~5km).
        random_state: Random seed for reproducibility.

    Returns:
        Tuple of (train_df, test_df).
    """
    df = df.copy()
    df["_grid_lat"] = (df["latitude"]  / grid_size_deg).round() * grid_size_deg
    df["_grid_lng"] = (df["longitude"] / grid_size_deg).round() * grid_size_deg
    df["_grid_id"]  = df["_grid_lat"].astype(str) + "_" + df["_grid_lng"].astype(str)

    rng = np.random.default_rng(random_state)
    unique_grids = df["_grid_id"].unique()
    n_test = max(1, int(len(unique_grids) * test_fraction))
    test_grids = set(rng.choice(unique_grids, size=n_test, replace=False))

    train = df[~df["_grid_id"].isin(test_grids)].drop(columns=["_grid_lat", "_grid_lng", "_grid_id"])
    test  = df[ df["_grid_id"].isin(test_grids)].drop(columns=["_grid_lat", "_grid_lng", "_grid_id"])

    logger.info(
        f"Spatial block split: {len(unique_grids)} grid cells | "
        f"train={len(train)} | test={len(test)}"
    )
    return train, test


def save_splits(
    X_train: pd.DataFrame,
    X_test: pd.DataFrame,
    y_train: pd.Series,
    y_test: pd.Series,
) -> dict[str, Path]:
    """
    Save train/test splits to the processed directory as Parquet files.

    Args:
        X_train, X_test: Feature DataFrames.
        y_train, y_test: Target Series.

    Returns:
        Dict mapping split name to saved file path.
    """
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    paths = {}
    for name, data in [("X_train", X_train), ("X_test", X_test),
                       ("y_train", y_train), ("y_test", y_test)]:
        path = PROCESSED_DIR / f"{name}.parquet"
        if isinstance(data, pd.Series):
            data.to_frame().to_parquet(path, index=False)
        else:
            data.to_parquet(path, index=False)
        paths[name] = path
        logger.info(f"Saved {name}: {path} ({len(data)} rows)")
    return paths
