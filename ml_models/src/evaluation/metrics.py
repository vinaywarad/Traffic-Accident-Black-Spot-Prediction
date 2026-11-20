"""
Comprehensive evaluation metrics for imbalanced binary classification.

For black spot prediction: RECALL is more important than PRECISION.
Missing a black spot (false negative) is more dangerous than a false alarm.

Priority order:
  1. AUC-ROC  — overall discrimination ability
  2. AUC-PR   — performance on imbalanced classes
  3. Recall   — catch as many black spots as possible
  4. F1-Score — balance of precision and recall
  5. MCC      — Matthews correlation (best single metric for imbalance)
  6. Brier    — probability calibration quality
"""
import numpy as np
import pandas as pd
from loguru import logger
from sklearn.metrics import (
    roc_auc_score, average_precision_score,
    f1_score, precision_score, recall_score,
    confusion_matrix, classification_report,
    brier_score_loss, matthews_corrcoef,
)


def evaluate_model(
    model,
    X_test: pd.DataFrame,
    y_test: pd.Series,
    threshold: float = 0.5,
    model_name: str = "model",
) -> dict:
    """
    Full evaluation suite. Returns dict of all metrics.

    Args:
        model: Fitted sklearn-compatible model with predict_proba.
        X_test: Test features.
        y_test: True test labels.
        threshold: Decision threshold for binary classification.
        model_name: Name tag for the results dict.

    Returns:
        Dict with all evaluation metrics.
    """
    y_proba = model.predict_proba(X_test)[:, 1]
    y_pred  = (y_proba >= threshold).astype(int)

    cm = confusion_matrix(y_test, y_pred)
    tn, fp, fn, tp = cm.ravel()

    metrics = {
        "model":     model_name,
        "threshold": threshold,

        # Threshold-independent ranking metrics
        "auc_roc":  round(float(roc_auc_score(y_test, y_proba)), 4),
        "auc_pr":   round(float(average_precision_score(y_test, y_proba)), 4),

        # Threshold-dependent classification metrics
        "f1":        round(float(f1_score(y_test, y_pred, zero_division=0)), 4),
        "precision": round(float(precision_score(y_test, y_pred, zero_division=0)), 4),
        "recall":    round(float(recall_score(y_test, y_pred, zero_division=0)), 4),
        "mcc":       round(float(matthews_corrcoef(y_test, y_pred)), 4),
        "brier_score": round(float(brier_score_loss(y_test, y_proba)), 4),

        # Confusion matrix components
        "true_positives":  int(tp),
        "false_positives": int(fp),
        "true_negatives":  int(tn),
        "false_negatives": int(fn),
        "specificity":     round(tn / max(tn + fp, 1), 4),
        "false_alarm_rate": round(fp / max(fp + tn, 1), 4),
        "miss_rate":        round(fn / max(fn + tp, 1), 4),   # 1 - recall
    }

    logger.info(
        f"{model_name} | AUC-ROC={metrics['auc_roc']} | "
        f"AUC-PR={metrics['auc_pr']} | Recall={metrics['recall']} | "
        f"F1={metrics['f1']} | MCC={metrics['mcc']}"
    )
    return metrics


def find_optimal_threshold(
    model,
    X_val: pd.DataFrame,
    y_val: pd.Series,
    metric: str = "f1",
    min_precision: float = 0.30,
) -> float:
    """
    Find the decision threshold that maximizes the given metric.

    Default: maximize F1.
    For safety-critical use: maximize recall subject to precision >= min_precision.

    Args:
        model: Fitted model with predict_proba.
        X_val: Validation features.
        y_val: Validation labels.
        metric: 'f1', 'recall', or 'mcc'.
        min_precision: Minimum precision floor when optimizing recall.

    Returns:
        Optimal threshold float in [0.1, 0.9].
    """
    y_proba = model.predict_proba(X_val)[:, 1]
    thresholds = np.arange(0.10, 0.90, 0.01)
    best_score, best_thresh = -np.inf, 0.5

    for t in thresholds:
        y_pred = (y_proba >= t).astype(int)
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
            best_score  = score
            best_thresh = t

    logger.info(
        f"Optimal threshold ({metric}): {best_thresh:.2f} → score={best_score:.4f}"
    )
    return float(round(best_thresh, 2))


def get_classification_report(
    model,
    X_test: pd.DataFrame,
    y_test: pd.Series,
    threshold: float = 0.5,
) -> str:
    """
    Return sklearn classification_report as a formatted string.

    Args:
        model: Fitted model.
        X_test: Test features.
        y_test: True labels.
        threshold: Decision threshold.

    Returns:
        Formatted classification report string.
    """
    y_proba = model.predict_proba(X_test)[:, 1]
    y_pred  = (y_proba >= threshold).astype(int)
    return classification_report(
        y_test, y_pred,
        target_names=["Non-Black Spot", "Black Spot"],
        digits=4,
    )


def metrics_to_dataframe(metrics_list: list[dict]) -> pd.DataFrame:
    """
    Convert a list of metric dicts to a comparison DataFrame.

    Args:
        metrics_list: List of dicts from evaluate_model().

    Returns:
        DataFrame sorted by AUC-ROC descending.
    """
    df = pd.DataFrame(metrics_list)
    cols = ["model", "auc_roc", "auc_pr", "f1", "recall",
            "precision", "mcc", "brier_score", "threshold"]
    cols = [c for c in cols if c in df.columns]
    return df[cols].sort_values("auc_roc", ascending=False).reset_index(drop=True)
