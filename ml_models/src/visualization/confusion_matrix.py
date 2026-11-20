"""
Styled confusion matrix heatmap for each model.
"""
from pathlib import Path
from typing import Optional

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from loguru import logger
from sklearn.metrics import confusion_matrix

from src.config import PLOTS_DIR


def plot_confusion_matrix(
    model,
    X_test: pd.DataFrame,
    y_test: pd.Series,
    threshold: float = 0.5,
    model_name: str = "",
    save_path: Optional[Path] = None,
) -> Path:
    """
    Plot a styled confusion matrix heatmap.

    Annotates cells with descriptive labels:
        TN = Correctly safe, FP = False alarm,
        FN = MISSED black spot!, TP = Caught black spot

    Args:
        model: Fitted model with predict_proba.
        X_test: Test features.
        y_test: True labels.
        threshold: Decision threshold.
        model_name: Model name for plot title.
        save_path: Output path.

    Returns:
        Path to saved PNG.
    """
    y_proba = model.predict_proba(X_test)[:, 1]
    y_pred  = (y_proba >= threshold).astype(int)
    cm      = confusion_matrix(y_test, y_pred)

    fig, ax = plt.subplots(figsize=(8, 6))
    fig.patch.set_facecolor("#0A0C10")
    ax.set_facecolor("#111418")

    # Custom annotations
    tn, fp, fn, tp = cm.ravel()
    annot = np.array([
        [f"TN\n{tn}\n(Correctly safe)",    f"FP\n{fp}\n(False alarm)"],
        [f"FN\n{fn}\n⚠ MISSED black spot", f"TP\n{tp}\n(Caught black spot)"],
    ])

    sns.heatmap(
        cm, annot=annot, fmt="", cmap="Blues",
        xticklabels=["Predicted Safe", "Predicted Black Spot"],
        yticklabels=["Actually Safe", "Actually Black Spot"],
        ax=ax, linewidths=0.5, cbar=True,
        annot_kws={"size": 10},
    )

    ax.set_title(
        f"Confusion Matrix — {model_name.replace('_', ' ').title()} "
        f"(threshold={threshold})",
        color="#F1F5F9", pad=12,
    )
    ax.tick_params(colors="#94A3B8")
    ax.xaxis.label.set_color("#94A3B8")
    ax.yaxis.label.set_color("#94A3B8")

    plt.tight_layout()
    path = save_path or (PLOTS_DIR / f"confusion_matrix_{model_name}.png")
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(path, dpi=150, bbox_inches="tight", facecolor=fig.get_facecolor())
    plt.close()
    logger.info(f"Saved confusion matrix → {path}")
    return path


def plot_all_confusion_matrices(
    models_dict: dict,
    X_test: pd.DataFrame,
    y_test: pd.Series,
    thresholds: dict = None,
) -> list[Path]:
    """
    Plot confusion matrices for all models.

    Args:
        models_dict: Dict mapping model_name → fitted model.
        X_test: Test features.
        y_test: True labels.
        thresholds: Dict mapping model_name → threshold (default 0.5).

    Returns:
        List of saved plot paths.
    """
    thresholds = thresholds or {}
    paths = []
    for name, model in models_dict.items():
        t = thresholds.get(name, 0.5)
        path = plot_confusion_matrix(model, X_test, y_test, t, name)
        paths.append(path)
    return paths
