"""
Categorical encoding for ML preprocessing.
Supports label encoding, ordinal encoding, and one-hot encoding.
"""
import pandas as pd
import numpy as np
from loguru import logger
from sklearn.preprocessing import LabelEncoder, OrdinalEncoder


# Severity ordinal order
SEVERITY_ORDER = ["LOW", "MEDIUM", "HIGH", "CRITICAL"]

# Season ordinal order
SEASON_ORDER = ["Winter", "Summer", "Monsoon", "Post-Monsoon"]


def encode_categoricals(df: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    """
    Encode all categorical columns needed for ML.

    Encoding strategy:
        - severity → ordinal (LOW=0, MEDIUM=1, HIGH=2, CRITICAL=3)
        - season → ordinal
        - road_type → label encoded
        - weather, road_condition, light_condition → already encoded as risk scores
          in environmental_features.py; this adds label-encoded versions

    Args:
        df: Feature-engineered DataFrame.

    Returns:
        Tuple of (encoded DataFrame, encoders dict for inverse transform).
    """
    df = df.copy()
    encoders = {}

    # Severity ordinal encoding
    if "severity" in df.columns:
        sev_map = {s: i for i, s in enumerate(SEVERITY_ORDER)}
        df["severity_encoded"] = df["severity"].map(sev_map).fillna(0).astype(int)
        encoders["severity"] = sev_map
        logger.debug("Encoded severity (ordinal)")

    # Season ordinal encoding
    if "season" in df.columns:
        season_map = {s: i for i, s in enumerate(SEASON_ORDER)}
        df["season_encoded"] = df["season"].map(season_map).fillna(0).astype(int)
        encoders["season"] = season_map

    # Road type label encoding
    if "road_type" in df.columns:
        le = LabelEncoder()
        df["road_type_label"] = le.fit_transform(df["road_type"].astype(str))
        encoders["road_type"] = le
        logger.debug(f"Label-encoded road_type: {list(le.classes_)}")

    # Day of week label encoding (if string)
    if "day_of_week" in df.columns and df["day_of_week"].dtype == object:
        day_map = {"Monday": 0, "Tuesday": 1, "Wednesday": 2, "Thursday": 3,
                   "Friday": 4, "Saturday": 5, "Sunday": 6}
        df["day_of_week_num"] = df["day_of_week"].map(day_map).fillna(0).astype(int)

    logger.info(f"Encoded {len(encoders)} categorical columns")
    return df, encoders


def decode_severity(encoded: pd.Series) -> pd.Series:
    """
    Inverse-transform severity from ordinal back to string labels.

    Args:
        encoded: Series of integer severity codes.

    Returns:
        Series of severity strings.
    """
    inv_map = {i: s for i, s in enumerate(SEVERITY_ORDER)}
    return encoded.map(inv_map)
