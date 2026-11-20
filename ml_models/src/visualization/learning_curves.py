"""
Learning curves for bias-variance analysis.
Shows how model performance changes with training set size.
"""
from pathlib import Path
from typing import Optional

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from loguru import logger
from sklearn.model_selection import learning_curve, StratifiedKFold

from src.config import PLOTS_DIR, RANDOM_STATE


def plot_learning_curve(
    model,
    X_train: pd.DataFrame,
    y_train: pd.Series,
    model_name: str = "",
    scoring: str = "roc_auc",
    cv: int = 5,
    n_jobs: int = -1,
    save_path: Optional[Path] = None,
) -> Path:
    """
    Plot learning curve showing train vs validation score vs training size.

    Diagnoses:
        - High bias (underfitting): both curves plateau low
        - High variance (overfitting): large gap between train and val curves

    Args:
        model: Unfitted sklearn-compatible model.
        X_train: Training features.
        y_train: Training labels.
        model_name: Model name for plot title.
        scoring: Metric to plot.
        cv: Number of CV folds.
        n_jobs: Parallel jobs.
        save_path: Output path.

    Returns:
        Path to saved PNG.
    """
    train_sizes = np.linspace(0.1, 1.0, 8)
    cv_strategy = StratifiedKFold(n_splits=cv, shuffle=True, random_state=RANDOM_STATE)

    train_sizes_abs, train_scores, val_scores = learning_curve(
        model, X_train, y_train,
        train_sizes=train_sizes,
        cv=cv_strategy,
        scoring=scoring,
        n_jobs=n_jobs,
        shuffle=True,
        random_state=RANDOM_STATE,
    )

    train_mean = train_scores.mean(axis=1)
    train_std  = train_scores.std(axis=1)
    val_mean   = val_scores.mean(axis=1)
    val_std    = val_scores.std(axis=1)

    fig, ax = plt.subplots(figsize=(9, 6))
    fig.patch.set_facecolor("#0A0C10")
    ax.set_facecolor("#111418")
    for spine in ax.spines.values():
        spine.set_edgecolor("#1E2329")

    ax.plot(train_sizes_abs, train_mean, "o-", color="#F59E0B", lw=2, label="Training score")
    ax.fill_between(train_sizes_abs, train_mean - train_std, train_mean + train_std,
                    alpha=0.15, color="#F59E0B")

    ax.plot(train_sizes_abs, val_mean, "o-", color="#06B6D4", lw=2, label="Validation score")
    ax.fill_between(train_sizes_abs, val_mean - val_std, val_mean + val_std,
                    alpha=0.15, color="#06B6D4")

    ax.set(
        xlabel="Training Set Size",
        ylabel=scoring.replace("_", " ").title(),
        title=f"Learning Curve — {model_name.replace('_', ' ').title()}",
        ylim=[0.4, 1.02],
    )
    ax.tick_params(colors="#94A3B8")
    ax.xaxis.label.set_color("#94A3B8")
    ax.yaxis.label.set_color("#94A3B8")
    ax.title.set_color("#F1F5F9")
    ax.legend(facecolor="#111418", labelcolor="#F1F5F9", edgecolor="#1E2329")
    ax.grid(color="#1E2329", alpha=0.4)

    plt.tight_layout()
    path = save_path or (PLOTS_DIR / f"learning_curve_{model_name}.png")
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(path, dpi=150, bbox_inches="tight", facecolor=fig.get_facecolor())
    plt.close()
    logger.info(f"Saved learning curve → {path}")
    return path
