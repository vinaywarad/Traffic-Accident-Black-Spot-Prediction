"""
CSV ingestion and schema validation for raw accident data files.
Supports multiple yearly CSVs and merges them into a single DataFrame.
"""
from pathlib import Path
from typing import Optional

import pandas as pd
from loguru import logger

from src.config import RAW_ACCIDENTS_DIR

# Minimum required columns (flexible — extras are kept)
REQUIRED_COLUMNS = {"latitude", "longitude", "date", "severity"}

# Column name aliases — maps common variants to canonical names
COLUMN_ALIASES = {
    "lat":          "latitude",
    "lon":          "longitude",
    "lng":          "longitude",
    "long":         "longitude",
    "accident_date": "date",
    "date_of_accident": "date",
    "acc_date":     "date",
    "road":         "road_type",
    "road_category": "road_type",
    "weather_condition": "weather",
    "no_of_vehicles": "vehicles_involved",
    "num_vehicles": "vehicles_involved",
    "injured":      "casualties",
    "no_injured":   "casualties",
    "killed":       "fatalities",
    "no_killed":    "fatalities",
    "fatal":        "fatalities",
}


def _normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Lowercase column names and apply aliases."""
    df.columns = df.columns.str.lower().str.strip().str.replace(" ", "_")
    df = df.rename(columns=COLUMN_ALIASES)
    return df


def load_single_csv(path: Path) -> Optional[pd.DataFrame]:
    """
    Load a single accident CSV file.

    Args:
        path: Path to the CSV file.

    Returns:
        Normalized DataFrame or None if loading fails.
    """
    try:
        df = pd.read_csv(path, low_memory=False)
        df = _normalize_columns(df)
        missing = REQUIRED_COLUMNS - set(df.columns)
        if missing:
            logger.warning(f"{path.name}: missing columns {missing} — skipping")
            return None
        logger.info(f"Loaded {len(df)} records from {path.name}")
        return df
    except Exception as e:
        logger.error(f"Failed to load {path}: {e}")
        return None


def load_all_accident_csvs(
    data_dir: Path = RAW_ACCIDENTS_DIR,
) -> pd.DataFrame:
    """
    Load and concatenate all accident CSV files from a directory.

    Args:
        data_dir: Directory containing yearly accident CSVs.

    Returns:
        Combined DataFrame with a 'source_file' column.
    """
    data_dir = Path(data_dir)
    csv_files = sorted(data_dir.glob("*.csv"))

    if not csv_files:
        logger.warning(f"No CSV files found in {data_dir}")
        return pd.DataFrame()

    frames = []
    for f in csv_files:
        df = load_single_csv(f)
        if df is not None:
            df["source_file"] = f.name
            frames.append(df)

    if not frames:
        logger.error("No valid accident CSVs loaded")
        return pd.DataFrame()

    combined = pd.concat(frames, ignore_index=True)
    logger.success(f"Loaded {len(combined)} total records from {len(frames)} files")
    return combined


def load_external_dataset(path: Path) -> Optional[pd.DataFrame]:
    """
    Load an external dataset (Kaggle / NCRB) and normalize columns.

    Args:
        path: Path to the external CSV file.

    Returns:
        Normalized DataFrame or None.
    """
    return load_single_csv(path)
