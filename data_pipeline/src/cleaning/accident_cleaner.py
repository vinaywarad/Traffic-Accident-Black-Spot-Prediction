"""
Full cleaning pipeline for raw accident CSVs.
Handles: missing values, coordinate validation, duplicates,
outlier detection, type casting, and standardization.
"""
import pandas as pd
from loguru import logger

from src.config import BENGALURU_BOUNDS

# Expected column types
NUMERIC_COLUMNS = ["latitude", "longitude", "vehicles_involved", "casualties", "fatalities"]
CATEGORICAL_COLUMNS = ["weather", "road_type", "road_condition", "light_condition"]

# Severity label normalization map
SEVERITY_MAP = {
    "fatal":        "CRITICAL",
    "serious":      "HIGH",
    "grievous":     "HIGH",
    "minor":        "MEDIUM",
    "simple":       "LOW",
    "damage only":  "LOW",
    "non-fatal":    "MEDIUM",
    "critical":     "CRITICAL",
    "high":         "HIGH",
    "medium":       "MEDIUM",
    "low":          "LOW",
}

VALID_SEVERITIES = {"LOW", "MEDIUM", "HIGH", "CRITICAL"}


def clean_accidents(df: pd.DataFrame) -> pd.DataFrame:
    """
    Full cleaning pipeline. Returns cleaned DataFrame.

    Steps:
        1. Drop exact duplicates
        2. Standardize column names
        3. Parse datetime
        4. Cast numeric columns
        5. Validate coordinates (Bengaluru bounds)
        6. Cap outliers at 99th percentile
        7. Fill missing categoricals with mode
        8. Standardize severity labels
        9. Drop rows missing critical fields

    Args:
        df: Raw accident DataFrame.

    Returns:
        Cleaned DataFrame.
    """
    original_count = len(df)
    report = {}

    # 1. Drop exact duplicates
    before = len(df)
    df = df.drop_duplicates()
    report["duplicates_dropped"] = before - len(df)

    # 2. Standardize column names
    df.columns = df.columns.str.lower().str.strip().str.replace(" ", "_")

    # 3. Parse datetime
    df["date"] = pd.to_datetime(df["date"], errors="coerce", dayfirst=True)
    if "time" in df.columns:
        df["datetime"] = pd.to_datetime(
            df["date"].astype(str) + " " + df["time"].astype(str),
            errors="coerce",
        )
    before = len(df)
    df = df.dropna(subset=["date"])
    report["invalid_dates_dropped"] = before - len(df)

    # 4. Cast numeric columns
    for col in NUMERIC_COLUMNS:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    # 5. Validate coordinates
    before = len(df)
    if "latitude" in df.columns and "longitude" in df.columns:
        lat_ok = df["latitude"].between(*BENGALURU_BOUNDS["lat"])
        lng_ok = df["longitude"].between(*BENGALURU_BOUNDS["lng"])
        df = df[lat_ok & lng_ok]
    report["out_of_bounds_dropped"] = before - len(df)

    # 6. Cap outliers at 99th percentile
    for col in ["vehicles_involved", "casualties", "fatalities"]:
        if col in df.columns:
            cap = df[col].quantile(0.99)
            df[col] = df[col].clip(upper=cap)

    # 7. Fill missing categoricals with mode
    for col in CATEGORICAL_COLUMNS:
        if col in df.columns and df[col].isna().any():
            mode_val = df[col].mode()
            if len(mode_val) > 0:
                df[col] = df[col].fillna(mode_val[0])

    # 8. Standardize severity labels
    if "severity" in df.columns:
        df["severity"] = (
            df["severity"]
            .astype(str)
            .str.lower()
            .str.strip()
            .map(SEVERITY_MAP)
            .fillna(df["severity"].astype(str).str.upper())
        )
        # Keep only valid severities
        df = df[df["severity"].isin(VALID_SEVERITIES)]

    # 9. Drop rows missing critical fields
    critical_fields = [c for c in ["latitude", "longitude", "severity"] if c in df.columns]
    before = len(df)
    df = df.dropna(subset=critical_fields)
    report["missing_critical_dropped"] = before - len(df)

    df = df.reset_index(drop=True)

    logger.info(
        f"Cleaned: {original_count} → {len(df)} records "
        f"({original_count - len(df)} dropped) | {report}"
    )
    return df


def get_cleaning_report(original: pd.DataFrame, cleaned: pd.DataFrame) -> dict:
    """
    Generate a data quality report comparing original vs cleaned DataFrames.

    Args:
        original: Raw DataFrame before cleaning.
        cleaned: DataFrame after cleaning.

    Returns:
        Dict with quality metrics.
    """
    return {
        "original_records":  len(original),
        "cleaned_records":   len(cleaned),
        "records_dropped":   len(original) - len(cleaned),
        "drop_rate_pct":     round((1 - len(cleaned) / max(len(original), 1)) * 100, 2),
        "missing_pct":       (cleaned.isna().sum() / len(cleaned) * 100).round(2).to_dict(),
        "severity_dist":     cleaned["severity"].value_counts().to_dict() if "severity" in cleaned.columns else {},
        "blackspot_rate":    round(cleaned["is_blackspot"].mean() * 100, 2) if "is_blackspot" in cleaned.columns else None,
    }
