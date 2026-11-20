"""
Decision threshold optimization for all trained models.
Finds the threshold that best balances recall and precision
for the black spot prediction use case.
"""
import numpy as np
import pandas as pd
from loguru import logger
from sklearn.metrics import (
    f1_score, precision_score, recall_score,
    matthews_corrcoef, roc_curve,
)


def optimize_all_thresholds(
    models: dict,
    X_val: pd.DataFrame,
    y_val: pd.Series,
    metric: str = "f1",
    min_precision: float = 0.30,
) -> dict[str, float]:
    """
    Find optimal thresholds for all models simultaneously.

    Args:
        models: Dict mapping model_name → fitted model.
        X_val: Validation features.
        y_val: Validation labels.
        metric: Metric to optimize ('f1', 'recall', 'mcc', 'youden').
        min_precision: Minimum precision when optimizing recall.

    Returns:
        Dict mapping model_name → optimal threshold.
    """
    thresholds = {}
    for name, model in models.items():
        t = find_threshold(model, X_val, y_val, metric, min_precision)
        thresholds[name] = t
        logger.info(f"{name}: optimal threshold = {t:.2f}")
    return thresholds


def find_threshold(
    model,
    X_val: pd.DataFrame,
    y_val: pd.Series,
    metric: str = "f1",
    min_precision: float = 0.30,
) -> float:
    """
    Find the optimal decision threshold for a single model.

    Strategies:
        - 'f1'     : maximize F1 score
        - 'recall' : maximize recall subject to precision >= min_precision
        - 'mcc'    : maximize Matthews Correlation Coefficient
        - 'youden' : maximize Youden's J statistic (sensitivity + specificity - 1)

    Args:
        model: Fitted model with predict_proba.
        X_val: Validation features.
        y_val: Validation labels.
        metric: Optimization strategy.
        min_precision: Precision floor for recall optimization.

    Returns:
        Optimal threshold float.
    """
    y_proba = model.predict_proba(X_val)[:, 1]

    if metric == "youden":
        return _youden_threshold(y_val, y_proba)

    thresholds = np.arange(0.10, 0.90, 0.01)
    best_score, best_t = -np.inf, 0.5

    for t in thresholds:
        y_pred = (y_proba >= t).astype(int)
        if y_pred.sum() == 0:
            continue

        if metric == "f1":
            score = f1_score(y_val, y_pred, zero_division=0)
        elif metric == "recall":
            prec  = precision_score(y_val, y_pred, zero_division=0)
            score = recall_score(y_val, y_pred) if prec >= min_precision else 0.0
        elif metric == "mcc":
            score = matthews_corrcoef(y_val, y_pred)
        else:
            score = f1_score(y_val, y_pred, zero_division=0)

        if score > best_score:
            best_score = score
            best_t     = t

    return float(round(best_t, 2))


def _youden_threshold(y_true: pd.Series, y_proba: np.ndarray) -> float:
    """
    Find threshold using Youden's J statistic from the ROC curve.
    J = sensitivity + specificity - 1 = TPR - FPR.
    """
    fpr, tpr, thresholds = roc_curve(y_true, y_proba)
    j_scores = tpr - fpr
    best_idx = int(np.argmax(j_scores))
    return float(round(thresholds[best_idx], 2))


def threshold_sensitivity_table(
    model,
    X_test: pd.DataFrame,
    y_test: pd.Series,
    thresholds: list = None,
) -> pd.DataFrame:
    """
    Show how metrics change across a range of thresholds.

    Args:
        model: Fitted model.
        X_test: Test features.
        y_test: True labels.
        thresholds: List of thresholds to evaluate (default: 0.1 to 0.9).

    Returns:
        DataFrame with metrics at each threshold.
    """
    if thresholds is None:
        thresholds = np.arange(0.10, 0.91, 0.05).tolist()

    y_proba = model.predict_proba(X_test)[:, 1]
    rows = []

    for t in thresholds:
        y_pred = (y_proba >= t).astype(int)
        rows.append({
            "threshold": round(t, 2),
            "precision": round(float(precision_score(y_test, y_pred, zero_division=0)), 4),
            "recall":    round(float(recall_score(y_test, y_pred, zero_division=0)), 4),
            "f1":        round(float(f1_score(y_test, y_pred, zero_division=0)), 4),
            "mcc":       round(float(matthews_corrcoef(y_test, y_pred)), 4),
            "predicted_positives": int(y_pred.sum()),
        })

    return pd.DataFrame(rows)
