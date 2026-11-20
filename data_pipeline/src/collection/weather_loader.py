"""
Weather CSV ingestion and preprocessing.
Loads Bengaluru weather data and prepares it for merging with accident records.
"""
from pathlib import Path
from typing import Optional

import pandas as pd
from loguru import logger

from src.config import RAW_WEATHER_DIR

WEATHER_FILE = RAW_WEATHER_DIR / "bengaluru_weather_2019_2023.csv"

# Expected columns after normalization
WEATHER_COLUMNS = ["date", "temperature_max", "temperature_min",
                   "rainfall_mm", "humidity_pct", "wind_speed_kmh",
                   "weather_condition"]


def load_weather_data(path: Path = WEATHER_FILE) -> Optional[pd.DataFrame]:
    """
    Load and normalize weather CSV data.

    Args:
        path: Path to the weather CSV file.

    Returns:
        Cleaned weather DataFrame indexed by date, or None if file missing.
    """
    path = Path(path)
    if not path.exists():
        logger.warning(f"Weather file not found: {path} — generating synthetic weather")
        return _generate_synthetic_weather()

    df = pd.read_csv(path, low_memory=False)
    df.columns = df.columns.str.lower().str.strip().str.replace(" ", "_")
    df["date"] = pd.to_datetime(df["date"], errors="coerce", dayfirst=True)
    df = df.dropna(subset=["date"])
    df = df.sort_values("date").reset_index(drop=True)
    logger.info(f"Loaded {len(df)} weather records from {path.name}")
    return df


def _generate_synthetic_weather() -> pd.DataFrame:
    """
    Generate synthetic daily weather data for Bengaluru 2019–2023.
    Captures monsoon seasonality (Jun–Sep high rainfall).
    """
    import numpy as np

    dates = pd.date_range("2019-01-01", "2023-12-31", freq="D")
    records = []
    rng = np.random.default_rng(42)

    for d in dates:
        month = d.month
        is_monsoon = month in [6, 7, 8, 9]
        rainfall = rng.exponential(15) if is_monsoon else rng.exponential(2)
        rainfall = round(float(rainfall), 1)
        temp_max = round(float(rng.normal(28 if is_monsoon else 32, 2)), 1)
        temp_min = round(float(rng.normal(20 if is_monsoon else 18, 2)), 1)
        humidity  = round(float(rng.normal(80 if is_monsoon else 55, 10)), 1)
        wind      = round(float(rng.normal(15, 5)), 1)

        if rainfall > 20:
            condition = "Rainy"
        elif rainfall > 5:
            condition = "Overcast"
        elif month in [11, 12, 1] and rng.random() < 0.1:
            condition = "Foggy"
        else:
            condition = "Clear"

        records.append({
            "date":              d.strftime("%Y-%m-%d"),
            "temperature_max":   temp_max,
            "temperature_min":   temp_min,
            "rainfall_mm":       rainfall,
            "humidity_pct":      min(100, max(0, humidity)),
            "wind_speed_kmh":    max(0, wind),
            "weather_condition": condition,
        })

    df = pd.DataFrame(records)
    df["date"] = pd.to_datetime(df["date"])
    logger.info(f"Generated {len(df)} synthetic weather records")
    return df


def merge_weather_with_accidents(
    accidents: pd.DataFrame,
    weather: pd.DataFrame,
) -> pd.DataFrame:
    """
    Left-join weather data onto accident records by date.

    Args:
        accidents: Accident DataFrame with a 'date' column.
        weather: Weather DataFrame with a 'date' column.

    Returns:
        Merged DataFrame with weather columns added.
    """
    accidents = accidents.copy()
    weather = weather.copy()

    accidents["date"] = pd.to_datetime(accidents["date"]).dt.normalize()
    weather["date"]   = pd.to_datetime(weather["date"]).dt.normalize()

    merged = accidents.merge(
        weather[["date", "rainfall_mm", "humidity_pct",
                 "temperature_max", "weather_condition"]],
        on="date",
        how="left",
        suffixes=("", "_weather"),
    )

    # Prefer original weather column if present, fill from weather data
    if "weather" in merged.columns and "weather_condition" in merged.columns:
        merged["weather"] = merged["weather"].fillna(merged["weather_condition"])
        merged = merged.drop(columns=["weather_condition"])

    logger.info(f"Merged weather data: {len(merged)} records, "
                f"{merged['rainfall_mm'].notna().sum()} with weather info")
    return merged
