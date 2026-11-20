"""
Lightweight SHAP explainer for runtime use.
Initialized once at startup from the loaded model.
Returns top N features as structured FeatureFactor objects.
"""
import numpy as np
import pandas as pd
from loguru import logger

from app.schemas.predict import FeatureFactor

try:
    import shap
    SHAP_AVAILABLE = True
except ImportError:
    SHAP_AVAILABLE = False
    logger.warning("shap not installed — SHAP explanations disabled, using rule-based fallback")


class SHAPExplainer:
    """
    SHAP explainer wrapper for runtime inference.
    Supports TreeExplainer (RF/XGB/LGBM) and LinearExplainer (LogReg).
    Falls back to rule-based explanations if SHAP is unavailable.
    """

    def __init__(self, model, feature_names: list, model_type: str = "tree"):
        self.feature_names = feature_names
        self.model_type    = model_type
        self._explainer    = None

        if not SHAP_AVAILABLE:
            return

        try:
            # Extract classifier from sklearn Pipeline if needed
            clf = (model.named_steps.get("clf", model)
                   if hasattr(model, "named_steps") else model)

            if model_type == "tree":
                self._explainer = shap.TreeExplainer(clf)
            else:
                bg = np.zeros((1, len(feature_names)))
                self._explainer = shap.LinearExplainer(
                    clf, bg, feature_perturbation="interventional"
                )
            logger.info(f"SHAP {model_type}Explainer initialized")
        except Exception as e:
            logger.warning(f"SHAP explainer init failed: {e} — using rule-based fallback")

    def explain(
        self,
        feature_df: pd.DataFrame,
        top_n: int = 5,
    ) -> list[FeatureFactor]:
        """
        Return top_n most influential features for this prediction.

        Uses cached TreeExplainer — fast enough for real-time use (~10–30ms).
        Falls back to rule-based explanations if SHAP fails.

        Args:
            feature_df: Single-row feature DataFrame.
            top_n: Number of top factors to return.

        Returns:
            List of FeatureFactor objects.
        """
        if self._explainer is not None:
            try:
                sv = self._explainer.shap_values(feature_df)
                # Binary classifier may return [class0, class1]
                if isinstance(sv, list) and len(sv) == 2:
                    sv = sv[1]
                sv = np.array(sv).flatten()

                top_idx = np.argsort(np.abs(sv))[::-1][:top_n]
                return [
                    FeatureFactor(
                        feature=self.feature_names[i],
                        importance=round(float(np.abs(sv[i])), 4),
                        direction="increases_risk" if sv[i] > 0 else "decreases_risk",
                        value=round(float(feature_df.iloc[0, i]), 4),
                    )
                    for i in top_idx
                ]
            except Exception as e:
                logger.debug(f"SHAP explain failed: {e}")

        # Rule-based fallback
        return self._rule_based(feature_df, top_n)

    def _rule_based(self, feature_df: pd.DataFrame, top_n: int) -> list[FeatureFactor]:
        """Generate rule-based factors when SHAP is unavailable."""
        row = feature_df.iloc[0]
        candidates = []

        rules = [
            ("nearest_blackspot_dist",   row.get("nearest_blackspot_dist", 9999) < 1000, 0.35),
            ("is_peak_hour",             row.get("is_peak_hour", 0) == 1,                0.28),
            ("is_monsoon",               row.get("is_monsoon", 0) == 1,                  0.22),
            ("weather_encoded",          row.get("weather_encoded", 1) >= 4,             0.20),
            ("road_risk_score",          row.get("road_risk_score", 1) >= 4,             0.18),
            ("is_night",                 row.get("is_night", 0) == 1,                    0.15),
            ("dist_to_nearest_junction", row.get("dist_to_nearest_junction", 999) < 200, 0.12),
        ]

        for feat, condition, importance in rules:
            if condition and feat in self.feature_names:
                idx = self.feature_names.index(feat)
                candidates.append(FeatureFactor(
                    feature=feat,
                    importance=importance,
                    direction="increases_risk",
                    value=round(float(row.get(feat, 0)), 4),
                ))

        return candidates[:top_n]
