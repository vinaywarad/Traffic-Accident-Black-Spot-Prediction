"""
Feature importance analysis using built-in model importances
and permutation importance (model-agnostic).
"""
import numpy as np
import pandas as pd
from loguru import logger

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from src.config import PLOTS_DIR


def get_builtin_importance(model, feature_names: list) -> pd.DataFrame:
    """
    Extract built-in feature importances from tree-based models.

    Works with: RandomForest, XGBoost, LightGBM.
    Returns empty DataFrame for Logistic Regression (use SHAP instead).

    Args:
        model: Fitted model.
        feature_names: List of feature column names.

    Returns:
        DataFrame with feature and importance columns, sorted descending.
    """
    # Handle sklearn Pipeline
    clf = model.named_steps.get("clf", model) if hasattr(model, "named_steps") else model

    if hasattr(clf, "feature_importances_"):
        importances = clf.feature_importances_
    elif hasattr(clf, "coef_"):
        importances = np.abs(clf.coef_[0])
    else:
        logger.warning("Model has no feature_importances_ or coef_ attribute")
        return pd.DataFrame()

    df = pd.DataFrame({
        "feature":    feature_names[:len(importances)],
        "importance": importances,
    }).sort_values("importance", ascending=False).reset_index(drop=True)

    return df


def get_permutation_importance(
    model,
    X_val: pd.DataFrame,
    y_val: pd.Series,
    n_repeats: int = 10,
    random_state: int = 42,
) -> pd.DataFrame:
    """
    Compute permutation importance (model-agnostic).

    Shuffles each feature and measures the drop in AUC-ROC.
    More reliable than built-in importances for correlated features.

    Args:
        model: Fitted model.
        X_val: Validation features.
        y_val: Validation labels.
        n_repeats: Number of permutation repeats per feature.
        random_state: Reproducibility seed.

    Returns:
        DataFrame with feature, mean_importance, std_importance.
    """
    from sklearn.inspection import permutation_importance

    result = permutation_importance(
        model, X_val, y_val,
        n_repeats=n_repeats,
        random_state=random_state,
        scoring="roc_auc",
        n_jobs=-1,
    )

    df = pd.DataFrame({
        "feature":          X_val.columns,
        "mean_importance":  result.importances_mean,
        "std_importance":   result.importances_std,
    }).sort_values("mean_importance", ascending=False).reset_index(drop=True)

    logger.info(f"Permutation importance computed for {len(df)} features")
    return df


def plot_importance_comparison(
    builtin_df: pd.DataFrame,
    perm_df: pd.DataFrame,
    model_name: str = "",
    top_n: int = 15,
    save_path=None,
) -> None:
    """
    Side-by-side comparison of built-in vs permutation importance.

    Args:
        builtin_df: DataFrame from get_builtin_importance().
        perm_df: DataFrame from get_permutation_importance().
        model_name: Model name for plot title.
        top_n: Number of top features to show.
        save_path: Output path (auto-generated if None).
    """
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
    fig.patch.set_facecolor("#0A0C10")

    for ax in [ax1, ax2]:
        ax.set_facecolor("#111418")
        ax.tick_params(colors="#94A3B8")
        ax.xaxis.label.set_color("#94A3B8")
        ax.yaxis.label.set_color("#94A3B8")
        ax.title.set_color("#F1F5F9")

    # Built-in importance
    if not builtin_df.empty:
        top = builtin_df.head(top_n)
        ax1.barh(top["feature"][::-1], top["importance"][::-1], color="#F59E0B")
        ax1.set_title(f"Built-in Importance — {model_name}")
        ax1.set_xlabel("Importance")

    # Permutation importance
    if not perm_df.empty:
        top = perm_df.head(top_n)
        ax2.barh(top["feature"][::-1], top["mean_importance"][::-1],
                 xerr=top["std_importance"][::-1], color="#06B6D4", capsize=3)
        ax2.set_title(f"Permutation Importance — {model_name}")
        ax2.set_xlabel("Mean AUC-ROC Drop")

    plt.tight_layout()
    path = save_path or (PLOTS_DIR / f"feature_importance_{model_name}.png")
    plt.savefig(path, dpi=150, bbox_inches="tight", facecolor=fig.get_facecolor())
    plt.close()
    logger.info(f"Saved importance comparison → {path}")
