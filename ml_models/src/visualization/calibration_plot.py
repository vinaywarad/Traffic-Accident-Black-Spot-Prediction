"""
Probability calibration curves for all models.
Well-calibrated models: predicted probability ≈ actual frequency.
"""
from pathlib import Path
from typing import Optional

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
from loguru import logger
from sklearn.calibration import calibration_curve

from src.config import PLOTS_DIR

MODEL_COLORS = {
    "logistic_regression": "#3B82F6",
    "random_forest":       "#10B981",
    "xgboost":             "#F59E0B",
    "lightgbm":            "#EF4444",
}


def plot_calibration_curves(
    models_dict: dict,
    X_test: pd.DataFrame,
    y_test: pd.Series,
    n_bins: int = 10,
    save_path: Optional[Path] = None,
) -> Path:
    """
    Plot calibration curves for all models.

    A perfectly calibrated model follows the diagonal.
    Models above the diagonal are under-confident; below = over-confident.

    Args:
        models_dict: Dict mapping model_name → fitted model.
        X_test: Test features.
        y_test: True labels.
        n_bins: Number of calibration bins.
        save_path: Output path.

    Returns:
        Path to saved PNG.
    """
    fig, ax = plt.subplots(figsize=(8, 7))
    fig.patch.set_facecolor("#0A0C10")
    ax.set_facecolor("#111418")
    for spine in ax.spines.values():
        spine.set_edgecolor("#1E2329")

    # Perfect calibration reference
    ax.plot([0, 1], [0, 1], "w--", lw=1.5, alpha=0.5, label="Perfect calibration")

    for name, model in models_dict.items():
        color = MODEL_COLORS.get(name, "#94A3B8")
        try:
            y_proba = model.predict_proba(X_test)[:, 1]
            fraction_pos, mean_pred = calibration_curve(
                y_test, y_proba, n_bins=n_bins, strategy="uniform"
            )
            ax.plot(mean_pred, fraction_pos, marker="o", lw=2, color=color,
                    label=name.replace("_", " ").title(), markersize=5)
        except Exception as e:
            logger.warning(f"Calibration curve failed for {name}: {e}")

    ax.set(
        xlabel="Mean Predicted Probability",
        ylabel="Fraction of Positives",
        title="Probability Calibration Curves",
        xlim=[0, 1], ylim=[0, 1],
    )
    ax.tick_params(colors="#94A3B8")
    ax.xaxis.label.set_color("#94A3B8")
    ax.yaxis.label.set_color("#94A3B8")
    ax.title.set_color("#F1F5F9")
    ax.legend(facecolor="#111418", labelcolor="#F1F5F9", edgecolor="#1E2329")
    ax.grid(color="#1E2329", alpha=0.5)

    plt.tight_layout()
    path = save_path or (PLOTS_DIR / "calibration_curves.png")
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(path, dpi=150, bbox_inches="tight", facecolor=fig.get_facecolor())
    plt.close()
    logger.info(f"Saved calibration curves → {path}")
    return path
