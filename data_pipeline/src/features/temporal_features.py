"""
Extract rich temporal features capturing Bengaluru traffic patterns.
Includes cyclic encoding, peak hours, monsoon flags, and festival months.
"""
import numpy as np
import pandas as pd
from loguru import logger

# Bengaluru-specific peak hours (based on BTP data)
MORNING_PEAK = list(range(8, 11))     # 8am–10am
EVENING_PEAK = list(range(17, 21))    # 5pm–8pm
NIGHT_HOURS  = list(range(22, 24)) + list(range(0, 5))

# Bengaluru monsoon months
MONSOON_MONTHS   = [6, 7, 8, 9]
PRE_MONSOON      = [3, 4, 5]
POST_MONSOON     = [10, 11]

# Major festival months in Karnataka
FESTIVAL_MONTHS  = [10, 11, 1]   # Dasara, Deepavali, Sankranti


def add_temporal_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Add temporal features to the accident DataFrame.

    Features added:
        - hour, day_of_week_num, month, year (if not present)
        - is_peak_hour, is_morning_peak, is_evening_peak
        - is_night, is_weekend
        - is_monsoon, is_pre_monsoon, is_festival_month
        - season (Summer/Monsoon/Post-Monsoon/Winter)
        - hour_sin, hour_cos (cyclic)
        - month_sin, month_cos (cyclic)
        - day_sin, day_cos (cyclic)
        - days_since_epoch (ordinal trend feature)

    Args:
        df: DataFrame with 'date' and 'hour' columns.

    Returns:
        DataFrame with temporal features added.
    """
    df = df.copy()
    df["date"] = pd.to_datetime(df["date"])

    # Ensure base columns exist
    if "hour" not in df.columns:
        df["hour"] = df["date"].dt.hour
    df["hour"] = df["hour"].astype(int)

    if "day_of_week_num" not in df.columns:
        df["day_of_week_num"] = df["date"].dt.dayofweek   # 0=Mon, 6=Sun
    if "month" not in df.columns:
        df["month"] = df["date"].dt.month
    if "year" not in df.columns:
        df["year"] = df["date"].dt.year

    # Peak hour flags
    df["is_morning_peak"]   = df["hour"].isin(MORNING_PEAK).astype(int)
    df["is_evening_peak"]   = df["hour"].isin(EVENING_PEAK).astype(int)
    df["is_peak_hour"]      = (df["is_morning_peak"] | df["is_evening_peak"]).astype(int)
    df["is_night"]          = df["hour"].isin(NIGHT_HOURS).astype(int)

    # Day flags
    df["is_weekend"]        = (df["day_of_week_num"] >= 5).astype(int)

    # Seasonal flags
    df["is_monsoon"]        = df["month"].isin(MONSOON_MONTHS).astype(int)
    df["is_pre_monsoon"]    = df["month"].isin(PRE_MONSOON).astype(int)
    df["is_festival_month"] = df["month"].isin(FESTIVAL_MONTHS).astype(int)

    # Season label
    df["season"] = df["month"].apply(_get_season)

    # Cyclic encoding — prevents model treating hour 23 as far from hour 0
    df["hour_sin"]  = np.sin(2 * np.pi * df["hour"] / 24)
    df["hour_cos"]  = np.cos(2 * np.pi * df["hour"] / 24)
    df["month_sin"] = np.sin(2 * np.pi * df["month"] / 12)
    df["month_cos"] = np.cos(2 * np.pi * df["month"] / 12)
    df["day_sin"]   = np.sin(2 * np.pi * df["day_of_week_num"] / 7)
    df["day_cos"]   = np.cos(2 * np.pi * df["day_of_week_num"] / 7)

    # Ordinal time feature for trend detection
    epoch = pd.Timestamp("2019-01-01")
    df["days_since_epoch"] = (df["date"] - epoch).dt.days

    logger.info(
        f"Added temporal features | "
        f"peak_hour: {df['is_peak_hour'].sum()} | "
        f"monsoon: {df['is_monsoon'].sum()} | "
        f"night: {df['is_night'].sum()}"
    )
    return df


def _get_season(month: int) -> str:
    """Map month number to Bengaluru season name."""
    if month in [3, 4, 5]:
        return "Summer"
    if month in [6, 7, 8, 9]:
        return "Monsoon"
    if month in [10, 11]:
        return "Post-Monsoon"
    return "Winter"
