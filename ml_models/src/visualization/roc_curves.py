"""
ROC and Precision-Recall curves for all models overlaid on the same axes.
"""
from pathlib import Path
from typing import Optional

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from loguru import logger
from sklearn.metrics import roc_curve, precision_recall_curve, auc

from src.config import PLOTS_DIR

MODEL_COLORS = {
    "logistic_regression": "#3B82F6",   # blue
    "random_forest":       "#10B981",   # green
    "xgboost":             "#F59E0B",   # amber
    "lightgbm":            "#EF4444",   # red
}
DEFAULT_COLORS = ["#3B82F6", "#10B981", "#F59E0B", "#EF4444"]


def plot_roc_all_models(
    models_dict: dict,
    X_test: pd.DataFrame,
    y_test: pd.Series,
    save_path: Optional[Path] = None,
) -> Path:
    """
    Plot ROC and PR curves for all models on the same figure.

    Args:
        models_dict: Dict mapping model_name → fitted model.
        X_test: Test features.
        y_test: True test labels.
        save_path: Output path (auto-generated if None).

    Returns:
        Path to saved PNG.
    """
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
    fig.patch.set_facecolor("#0A0C10")

    for ax in [ax1, ax2]:
        ax.set_facecolor("#111418")
        ax.tick_params(colors="#94A3B8")
        for spine in ax.spines.values():
            spine.set_edgecolor("#1E2329")

    colors = list(MODEL_COLORS.values())

    for i, (name, model) in enumerate(models_dict.items()):
        color = MODEL_COLORS.get(name, DEFAULT_COLORS[i % len(DEFAULT_COLORS)])
        try:
            y_proba = model.predict_proba(X_test)[:, 1]
        except Exception as e:
            logger.warning(f"Skipping {name} in ROC plot: {e}")
            continue

        # ROC curve
        fpr, tpr, _ = roc_curve(y_test, y_proba)
        roc_auc = auc(fpr, tpr)
        ax1.plot(fpr, tpr, color=color, lw=2,
                 label=f"{name.replace('_', ' ').title()} (AUC={roc_auc:.3f})")

        # PR curve
        prec, rec, _ = precision_recall_curve(y_test, y_proba)
        pr_auc = auc(rec, prec)
        ax2.plot(rec, prec, color=color, lw=2,
                 label=f"{name.replace('_', ' ').title()} (AUC={pr_auc:.3f})")

    # ROC diagonal
    ax1.plot([0, 1], [0, 1], "w--", lw=1, alpha=0.4, label="Random (AUC=0.500)")
    ax1.set(xlabel="False Positive Rate", ylabel="True Positive Rate",
            title="ROC Curves — All Models", xlim=[0, 1], ylim=[0, 1.02])
    ax1.legend(loc="lower right", fontsize=9, facecolor="#111418",
               labelcolor="#F1F5F9", edgecolor="#1E2329")
    ax1.xaxis.label.set_color("#94A3B8")
    ax1.yaxis.label.set_color("#94A3B8")
    ax1.title.set_color("#F1F5F9")

    # PR baseline
    baseline = float(y_test.mean())
    ax2.axhline(baseline, color="w", linestyle="--", lw=1, alpha=0.4,
                label=f"Baseline ({baseline:.2f})")
    ax2.set(xlabel="Recall", ylabel="Precision",
            title="Precision-Recall Curves — All Models", xlim=[0, 1], ylim=[0, 1.02])
    ax2.legend(loc="upper right", fontsize=9, facecolor="#111418",
               labelcolor="#F1F5F9", edgecolor="#1E2329")
    ax2.xaxis.label.set_color("#94A3B8")
    ax2.yaxis.label.set_color("#94A3B8")
    ax2.title.set_color("#F1F5F9")

    plt.tight_layout()
    path = save_path or (PLOTS_DIR / "roc_pr_curves_all_models.png")
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(path, dpi=150, bbox_inches="tight", facecolor=fig.get_facecolor())
    plt.close()
    logger.info(f"Saved ROC/PR curves → {path}")
    return path
