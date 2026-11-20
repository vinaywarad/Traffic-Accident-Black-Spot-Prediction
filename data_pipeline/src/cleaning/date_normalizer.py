"""
Date and time standardization for accident records.
Handles multiple input formats, extracts temporal components,
and creates a unified datetime column.
"""
import pandas as pd
import numpy as np
from loguru import logger

# Common date formats to try in order
DATE_FORMATS = [
    "%Y-%m-%d",
    "%d-%m-%Y",
    "%d/%m/%Y",
    "%m/%d/%Y",
    "%Y/%m/%d",
    "%d-%b-%Y",
    "%d %b %Y",
    "%B %d, %Y",
]

TIME_FORMATS = ["%H:%M", "%H:%M:%S", "%I:%M %p", "%I:%M:%S %p"]


def _try_parse_date(series: pd.Series) -> pd.Series:
    """Try multiple date formats until one works."""
    for fmt in DATE_FORMATS:
        try:
            parsed = pd.to_datetime(series, format=fmt, errors="coerce")
            success_rate = parsed.notna().mean()
            if success_rate > 0.8:
                logger.debug(f"Date format '{fmt}' matched {success_rate:.1%} of values")
                return parsed
        except Exception:
            continue
    # Fallback: pandas inference
    return pd.to_datetime(series, errors="coerce", dayfirst=True)


def normalize_dates(df: pd.DataFrame) -> pd.DataFrame:
    """
    Standardize date and time columns in the accident DataFrame.

    Creates:
        - date (datetime64): normalized date
        - time (str): HH:MM format
        - datetime (datetime64): combined date + time
        - year, month, day, hour, minute: extracted components
        - day_of_week (str): Monday–Sunday
        - day_of_week_num (int): 0=Monday, 6=Sunday
        - week_of_year (int): ISO week number

    Args:
        df: DataFrame with 'date' and optionally 'time' columns.

    Returns:
        DataFrame with normalized temporal columns.
    """
    df = df.copy()

    # Parse date
    if "date" in df.columns:
        df["date"] = _try_parse_date(df["date"].astype(str))
    else:
        logger.warning("No 'date' column found")
        return df

    # Parse time
    if "time" in df.columns:
        df["time"] = df["time"].astype(str).str.strip()
        # Normalize to HH:MM
        df["time"] = pd.to_datetime(
            df["time"], format="%H:%M", errors="coerce"
        ).dt.strftime("%H:%M").fillna("00:00")
    else:
        df["time"] = "00:00"

    # Combined datetime
    df["datetime"] = pd.to_datetime(
        df["date"].dt.strftime("%Y-%m-%d") + " " + df["time"],
        errors="coerce",
    )

    # Extract components
    df["year"]           = df["date"].dt.year
    df["month"]          = df["date"].dt.month
    df["day"]            = df["date"].dt.day
    df["hour"]           = df["datetime"].dt.hour.fillna(0).astype(int)
    df["minute"]         = df["datetime"].dt.minute.fillna(0).astype(int)
    df["day_of_week"]    = df["date"].dt.day_name()
    df["day_of_week_num"]= df["date"].dt.dayofweek   # 0=Mon, 6=Sun
    df["week_of_year"]   = df["date"].dt.isocalendar().week.astype(int)
    df["quarter"]        = df["date"].dt.quarter

    # Drop rows with completely unparseable dates
    before = len(df)
    df = df.dropna(subset=["date"])
    if len(df) < before:
        logger.info(f"Dropped {before - len(df)} rows with unparseable dates")

    logger.info(
        f"Date range: {df['date'].min().date()} → {df['date'].max().date()} "
        f"({df['year'].nunique()} years)"
    )
    return df.reset_index(drop=True)


def get_temporal_coverage(df: pd.DataFrame) -> dict:
    """
    Return temporal coverage statistics.

    Args:
        df: DataFrame with normalized date columns.

    Returns:
        Dict with date range, year counts, and monthly distribution.
    """
    if "date" not in df.columns:
        return {}
    return {
        "date_min":       str(df["date"].min().date()),
        "date_max":       str(df["date"].max().date()),
        "years":          sorted(df["year"].unique().tolist()) if "year" in df.columns else [],
        "records_per_year": df.groupby("year").size().to_dict() if "year" in df.columns else {},
        "null_dates":     df["date"].isna().sum(),
    }
