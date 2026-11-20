"""
SHAP (SHapley Additive exPlanations) for all model types.
This is the most important output for stakeholders —
traffic planners need to understand WHY a location is high risk.
"""
import json
from pathlib import Path
from typing import Optional

import numpy as np
import pandas as pd
from loguru import logger

try:
    import shap
    SHAP_AVAILABLE = True
except ImportError:
    SHAP_AVAILABLE = False
    logger.warning("shap not installed — explainability features disabled")

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from src.config import PLOTS_DIR


class BlackSpotExplainer:
    """
    SHAP explainer wrapper for all model types used in the pipeline.

    Supports:
        - TreeExplainer  : Random Forest, XGBoost, LightGBM (fast, exact)
        - LinearExplainer: Logistic Regression (fast, exact for linear models)
    """

    def __init__(
        self,
        model,
        X_train: pd.DataFrame,
        model_type: str,
        feature_names: Optional[list] = None,
    ):
        """
        Initialize the SHAP explainer.

        Args:
            model: Fitted sklearn-compatible model.
            X_train: Training data (used to build background distribution).
            model_type: 'tree' for RF/XGB/LGBM | 'linear' for LogReg.
            feature_names: List of feature column names.
        """
        if not SHAP_AVAILABLE:
            raise ImportError("shap is required. Install with: pip install shap")

        self.model         = model
        self.feature_names = feature_names or list(X_train.columns)
        self.model_type    = model_type
        self.shap_values   = None
        self.X_sample      = None

        # Build explainer
        if model_type == "tree":
            # For sklearn Pipeline, extract the classifier
            clf = model.named_steps.get("clf", model) if hasattr(model, "named_steps") else model
            self.explainer = shap.TreeExplainer(clf)
        elif model_type == "linear":
            # Use a background sample for LinearExplainer
            bg = shap.sample(X_train, min(100, len(X_train)), random_state=42)
            clf = model.named_steps.get("clf", model) if hasattr(model, "named_steps") else model
            self.explainer = shap.LinearExplainer(
                clf, bg, feature_perturbation="interventional"
            )
        else:
            raise ValueError(f"Unknown model_type: {model_type}. Use 'tree' or 'linear'.")

        logger.info(f"SHAP {model_type}Explainer initialized | {len(self.feature_names)} features")

    def compute_shap_values(
        self,
        X: pd.DataFrame,
        sample_size: int = 500,
    ) -> np.ndarray:
        """
        Compute SHAP values for a dataset.

        For large datasets, samples for speed without losing representativeness.

        Args:
            X: Feature DataFrame to explain.
            sample_size: Max rows to compute SHAP for.

        Returns:
            SHAP values array of shape (n_samples, n_features).
        """
        if len(X) > sample_size:
            X = X.sample(sample_size, random_state=42)

        self.X_sample = X.reset_index(drop=True)

        raw = self.explainer.shap_values(self.X_sample)

        # For binary classifiers, shap_values may return [neg_class, pos_class]
        if isinstance(raw, list) and len(raw) == 2:
            self.shap_values = raw[1]   # positive class (black spot)
        else:
            self.shap_values = raw

        logger.info(f"Computed SHAP values: {self.shap_values.shape}")
        return self.shap_values

    def plot_feature_importance(
        self,
        top_n: int = 20,
        save_path: Optional[Path] = None,
    ) -> Path:
        """
        Bar chart of mean |SHAP value| per feature — global importance ranking.
        Shows which features matter most across ALL predictions.
        """
        self._check_computed()
        fig, ax = plt.subplots(figsize=(10, 6))
        shap.summary_plot(
            self.shap_values, self.X_sample,
            feature_names=self.feature_names,
            plot_type="bar",
            max_display=top_n,
            show=False,
        )
        plt.title(f"Top {top_n} Features by Mean |SHAP Value|", pad=12)
        plt.tight_layout()
        path = save_path or (PLOTS_DIR / "shap_importance.png")
        plt.savefig(path, dpi=150, bbox_inches="tight")
        plt.close()
        logger.info(f"Saved SHAP importance plot → {path}")
        return path

    def plot_beeswarm(
        self,
        top_n: int = 20,
        save_path: Optional[Path] = None,
    ) -> Path:
        """
        Beeswarm plot: feature value (color) vs SHAP impact (x-axis).
        Best plot for understanding direction of feature effects.
        e.g. 'High dist_to_nearest_junction → pushes prediction toward black spot'
        """
        self._check_computed()
        shap.summary_plot(
            self.shap_values, self.X_sample,
            feature_names=self.feature_names,
            max_display=top_n,
            show=False,
        )
        plt.title("SHAP Beeswarm — Feature Impact on Black Spot Prediction")
        plt.tight_layout()
        path = save_path or (PLOTS_DIR / "shap_beeswarm.png")
        plt.savefig(path, dpi=150, bbox_inches="tight")
        plt.close()
        logger.info(f"Saved SHAP beeswarm → {path}")
        return path

    def explain_single_prediction(
        self,
        X_single: pd.DataFrame,
        save_path: Optional[Path] = None,
    ) -> Path:
        """
        Waterfall plot explaining ONE prediction.
        Shows exactly which features pushed the risk score up or down.
        Used in the frontend 'Why is this a black spot?' drawer.

        Args:
            X_single: Single-row DataFrame to explain.
            save_path: Output path for the plot.
        """
        sv = self.explainer(X_single)
        shap.waterfall_plot(sv[0], show=False)
        plt.title("Why is this location high risk?")
        plt.tight_layout()
        path = save_path or (PLOTS_DIR / "shap_waterfall_sample.png")
        plt.savefig(path, dpi=150, bbox_inches="tight")
        plt.close()
        logger.info(f"Saved SHAP waterfall → {path}")
        return path

    def plot_dependence(
        self,
        feature: str,
        interaction: str = "auto",
        save_path: Optional[Path] = None,
    ) -> Path:
        """
        Dependence plot: how a single feature affects risk score.
        e.g. plot_dependence('hour_sin') shows accident risk vs time of day.
        """
        self._check_computed()
        shap.dependence_plot(
            feature, self.shap_values, self.X_sample,
            feature_names=self.feature_names,
            interaction_index=interaction,
            show=False,
        )
        path = save_path or (PLOTS_DIR / f"shap_dependence_{feature}.png")
        plt.savefig(path, dpi=150, bbox_inches="tight")
        plt.close()
        return path

    def get_top_features_json(self, top_n: int = 10) -> list[dict]:
        """
        Return top N features with their mean SHAP importance as JSON.
        Used by the React frontend to render the feature importance chart.

        Returns:
            List of dicts: [{feature, importance, direction}, ...]
        """
        self._check_computed()
        mean_shap = np.abs(self.shap_values).mean(axis=0)
        indices   = np.argsort(mean_shap)[::-1][:top_n]
        return [
            {
                "feature":    self.feature_names[i],
                "importance": round(float(mean_shap[i]), 4),
                "direction":  "increases_risk",
            }
            for i in indices
        ]

    def explain_prediction_dict(self, X_single: pd.DataFrame) -> dict:
        """
        Return a structured dict explaining a single prediction.
        Used by the FastAPI /explain endpoint.

        Args:
            X_single: Single-row DataFrame.

        Returns:
            Dict with top contributing factors and their SHAP values.
        """
        sv = self.explainer.shap_values(X_single)
        if isinstance(sv, list):
            sv = sv[1]
        sv_flat = sv[0] if sv.ndim > 1 else sv

        pairs = sorted(
            zip(self.feature_names, sv_flat),
            key=lambda x: abs(x[1]),
            reverse=True,
        )
        return {
            "top_factors": [
                {
                    "feature":    name,
                    "shap_value": round(float(val), 4),
                    "direction":  "increases_risk" if val > 0 else "decreases_risk",
                }
                for name, val in pairs[:5]
            ]
        }

    def _check_computed(self) -> None:
        if self.shap_values is None:
            raise RuntimeError("Call compute_shap_values() before plotting.")
