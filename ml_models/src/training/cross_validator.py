"""
Cross-validation strategies for temporal accident data.
Uses TimeSeriesSplit to prevent future data leaking into past training folds.

Fold structure for 5-fold TimeSeriesSplit on 2019–2022 data:
  Fold 1: Train 2019       | Val 2020
  Fold 2: Train 2019–2020  | Val 2021
  Fold 3: Train 2019–2021  | Val 2022-H1
  Fold 4: Train 2019–2022  | Val 2022-H2
"""
import numpy as np
import pandas as pd
from loguru import logger
from sklearn.model_selection import TimeSeriesSplit, StratifiedKFold, cross_val_score

from src.config import CV_FOLDS, CV_GAP_DAYS, RANDOM_STATE


def get_cv_strategy(n_splits: int = CV_FOLDS) -> TimeSeriesSplit:
    """
    Return a TimeSeriesSplit cross-validator.

    gap=CV_GAP_DAYS prevents data from the same accident cluster
    spanning both train and validation sets.

    Args:
        n_splits: Number of CV folds.

    Returns:
        TimeSeriesSplit instance.
    """
    return TimeSeriesSplit(n_splits=n_splits, gap=CV_GAP_DAYS)


def cross_validate_model(
    model,
    X: pd.DataFrame,
    y: pd.Series,
    scoring: str = "roc_auc",
    n_splits: int = CV_FOLDS,
    use_stratified: bool = False,
) -> dict:
    """
    Run cross-validation and return summary statistics.

    Args:
        model: Unfitted sklearn-compatible model.
        X: Feature DataFrame.
        y: Target Series.
        scoring: sklearn scoring metric name.
        n_splits: Number of CV folds.
        use_stratified: Use StratifiedKFold instead of TimeSeriesSplit.
            Use only when temporal ordering is not meaningful.

    Returns:
        Dict with mean, std, min, max CV scores.
    """
    if use_stratified:
        cv = StratifiedKFold(n_splits=n_splits, shuffle=True, random_state=RANDOM_STATE)
    else:
        cv = get_cv_strategy(n_splits)

    scores = cross_val_score(model, X, y, cv=cv, scoring=scoring, n_jobs=-1)

    result = {
        "scoring":  scoring,
        "n_splits": n_splits,
        "mean":     round(float(scores.mean()), 4),
        "std":      round(float(scores.std()),  4),
        "min":      round(float(scores.min()),  4),
        "max":      round(float(scores.max()),  4),
        "scores":   [round(float(s), 4) for s in scores],
    }

    logger.info(
        f"CV ({scoring}) | mean={result['mean']:.4f} ± {result['std']:.4f} "
        f"| range=[{result['min']:.4f}, {result['max']:.4f}]"
    )
    return result


def cv_summary_table(cv_results: dict[str, dict]) -> pd.DataFrame:
    """
    Format cross-validation results from multiple models into a comparison table.

    Args:
        cv_results: Dict mapping model_name → cv result dict.

    Returns:
        DataFrame with one row per model.
    """
    rows = []
    for name, res in cv_results.items():
        rows.append({
            "model":   name,
            "cv_mean": res["mean"],
            "cv_std":  res["std"],
            "cv_min":  res["min"],
            "cv_max":  res["max"],
        })
    df = pd.DataFrame(rows).sort_values("cv_mean", ascending=False)
    return df
