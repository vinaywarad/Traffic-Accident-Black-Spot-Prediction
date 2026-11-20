"""
Environmental feature encoding — weather, road condition, lighting.
Converts categorical environmental variables to ML-ready numeric features.
"""
import pandas as pd
import numpy as np
from loguru import logger

# Ordinal risk encoding for weather conditions
WEATHER_RISK = {
    "Clear":       1,
    "Overcast":    2,
    "Night-Clear": 3,
    "Drizzle":     3,
    "Cloudy":      2,
    "Rainy":       4,
    "Night-Rainy": 5,
    "Foggy":       5,
}

ROAD_CONDITION_RISK = {
    "Dry":                1,
    "Wet":                3,
    "Potholed":           4,
    "Slippery":           5,
    "Under Construction": 4,
}

LIGHT_CONDITION_RISK = {
    "Daylight":    1,
    "Dusk/Dawn":   3,
    "Dark":        4,
    "Dark-Lit":    2,
}


def add_environmental_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Encode environmental categorical variables as ordinal risk scores.

    Features added:
        - weather_encoded: ordinal risk score for weather
        - road_condition_encoded: ordinal risk score for road condition
        - light_condition_encoded: ordinal risk score for lighting
        - is_adverse_weather: 1 if weather is Rainy/Foggy/Night-Rainy
        - is_wet_road: 1 if road condition is Wet/Slippery
        - combined_risk_score: product of weather + road + light risk

    Args:
        df: DataFrame with weather, road_condition, light_condition columns.

    Returns:
        DataFrame with environmental features added.
    """
    df = df.copy()

    # Weather encoding
    if "weather" in df.columns:
        df["weather_encoded"] = (
            df["weather"].map(WEATHER_RISK).fillna(2).astype(int)
        )
        df["is_adverse_weather"] = df["weather"].isin(
            ["Rainy", "Foggy", "Night-Rainy"]
        ).astype(int)
    else:
        df["weather_encoded"]    = 1
        df["is_adverse_weather"] = 0

    # Road condition encoding
    if "road_condition" in df.columns:
        df["road_condition_encoded"] = (
            df["road_condition"].map(ROAD_CONDITION_RISK).fillna(1).astype(int)
        )
        df["is_wet_road"] = df["road_condition"].isin(
            ["Wet", "Slippery"]
        ).astype(int)
    else:
        df["road_condition_encoded"] = 1
        df["is_wet_road"]            = 0

    # Light condition encoding
    if "light_condition" in df.columns:
        df["light_condition_encoded"] = (
            df["light_condition"].map(LIGHT_CONDITION_RISK).fillna(1).astype(int)
        )
    else:
        # Derive from hour if available
        if "hour" in df.columns:
            df["light_condition_encoded"] = np.where(
                df["hour"].between(6, 18), 1, 4
            )
        else:
            df["light_condition_encoded"] = 1

    # Combined environmental risk score
    df["env_risk_score"] = (
        df["weather_encoded"] *
        df["road_condition_encoded"] *
        df["light_condition_encoded"]
    )

    logger.info(
        f"Added environmental features | "
        f"adverse weather: {df['is_adverse_weather'].sum()} | "
        f"wet road: {df['is_wet_road'].sum()}"
    )
    return df
