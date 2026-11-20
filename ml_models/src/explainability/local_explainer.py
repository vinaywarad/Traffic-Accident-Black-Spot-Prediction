"""
Local (single-prediction) explainability for the FastAPI inference endpoint.
Explains why a specific location was predicted as a black spot.
"""
import numpy as np
import pandas as pd
from loguru import logger
from typing import Optional

from src.config import RISK_THRESHOLDS


def score_to_risk_level(score: float) -> str:
    """
    Convert a probability score to a human-readable risk level.

    Args:
        score: Probability of being a black spot (0.0–1.0).

    Returns:
        Risk level string: 'LOW', 'MEDIUM', 'HIGH', or 'CRITICAL'.
    """
    if score >= RISK_THRESHOLDS["CRITICAL"]:
        return "CRITICAL"
    if score >= RISK_THRESHOLDS["HIGH"]:
        return "HIGH"
    if score >= RISK_THRESHOLDS["MEDIUM"]:
        return "MEDIUM"
    return "LOW"


def explain_prediction(
    model,
    X_single: pd.DataFrame,
    explainer=None,
    threshold: float = 0.5,
) -> dict:
    """
    Generate a complete explanation for a single prediction.

    Returns a structured dict suitable for the FastAPI response and
    the React frontend's detail drawer.

    Args:
        model: Fitted model with predict_proba.
        X_single: Single-row feature DataFrame.
        explainer: Optional BlackSpotExplainer instance for SHAP values.
        threshold: Decision threshold.

    Returns:
        Dict with risk_score, risk_level, is_blackspot, and top_factors.
    """
    y_proba = float(model.predict_proba(X_single)[0, 1])
    is_bs   = y_proba >= threshold
    level   = score_to_risk_level(y_proba)

    result = {
        "risk_score":   round(y_proba, 4),
        "risk_level":   level,
        "is_blackspot": bool(is_bs),
        "confidence":   round(max(y_proba, 1 - y_proba), 4),
        "top_contributing_factors": [],
    }

    # Add SHAP-based factor explanations if explainer is available
    if explainer is not None:
        try:
            shap_result = explainer.explain_prediction_dict(X_single)
            result["top_contributing_factors"] = shap_result["top_factors"]
        except Exception as e:
            logger.warning(f"SHAP explanation failed: {e}")
            result["top_contributing_factors"] = _rule_based_factors(X_single)
    else:
        result["top_contributing_factors"] = _rule_based_factors(X_single)

    return result


def _rule_based_factors(X_single: pd.DataFrame) -> list[dict]:
    """
    Generate rule-based factor explanations when SHAP is unavailable.
    Uses domain knowledge about Bengaluru accident patterns.

    Args:
        X_single: Single-row feature DataFrame.

    Returns:
        List of factor dicts with feature, direction, and description.
    """
    row = X_single.iloc[0]
    factors = []

    if row.get("is_peak_hour", 0) == 1:
        factors.append({"feature": "is_peak_hour", "direction": "increases_risk",
                        "description": "Peak hour traffic (8–10am or 5–8pm)"})
    if row.get("is_monsoon", 0) == 1:
        factors.append({"feature": "is_monsoon", "direction": "increases_risk",
                        "description": "Monsoon season — wet roads, reduced visibility"})
    if row.get("weather_encoded", 1) >= 4:
        factors.append({"feature": "weather_encoded", "direction": "increases_risk",
                        "description": "Adverse weather conditions (rain/fog)"})
    if row.get("nearest_blackspot_dist", 9999) < 500:
        factors.append({"feature": "nearest_blackspot_dist", "direction": "increases_risk",
                        "description": "Within 500m of a known black spot"})
    if row.get("accident_density_1km", 0) > 5:
        factors.append({"feature": "accident_density_1km", "direction": "increases_risk",
                        "description": "High historical accident density in 1km radius"})
    if row.get("road_risk_score", 1) >= 4:
        factors.append({"feature": "road_risk_score", "direction": "increases_risk",
                        "description": "High-risk road type (NH/ORR)"})
    if row.get("is_night", 0) == 1:
        factors.append({"feature": "is_night", "direction": "increases_risk",
                        "description": "Night-time driving (10pm–5am)"})

    return factors[:5]
