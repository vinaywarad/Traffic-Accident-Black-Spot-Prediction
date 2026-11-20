"""
XGBoost classifier.
State-of-the-art for tabular data. Expected to be the champion model.
Handles missing values natively, very fast with hist tree method.
"""
import pandas as pd
from loguru import logger

try:
    import xgboost as xgb
    XGBOOST_AVAILABLE = True
except ImportError:
    XGBOOST_AVAILABLE = False
    logger.warning("xgboost not installed — XGBoost model unavailable")

# Optuna search space
XGB_SEARCH_SPACE = {
    "n_estimators":      ("int",   200, 1000),
    "max_depth":         ("int",   3,   10),
    "learning_rate":     ("float", 0.01, 0.3,  True),   # log scale
    "subsample":         ("float", 0.5,  1.0),
    "colsample_bytree":  ("float", 0.5,  1.0),
    "min_child_weight":  ("int",   1,    10),
    "gamma":             ("float", 0.0,  1.0),
    "reg_alpha":         ("float", 1e-4, 10.0, True),
    "reg_lambda":        ("float", 1e-4, 10.0, True),
}


def get_scale_pos_weight(y_train: pd.Series) -> float:
    """
    Compute scale_pos_weight = negative_count / positive_count.
    Tells XGBoost how much to up-weight the minority class.

    Args:
        y_train: Binary training labels.

    Returns:
        Float ratio for scale_pos_weight parameter.
    """
    neg = int((y_train == 0).sum())
    pos = int((y_train == 1).sum())
    ratio = neg / max(pos, 1)
    logger.info(f"scale_pos_weight = {ratio:.2f}  (neg={neg}, pos={pos})")
    return ratio


def build_xgboost(
    scale_pos_weight: float = 1.0,
    n_estimators: int = 500,
    max_depth: int = 6,
    learning_rate: float = 0.05,
    subsample: float = 0.8,
    colsample_bytree: float = 0.8,
    min_child_weight: int = 3,
    gamma: float = 0.1,
    reg_alpha: float = 0.1,
    reg_lambda: float = 1.0,
    early_stopping_rounds: int = 50,
    random_state: int = 42,
    **kwargs,
):
    """
    Build an XGBoost classifier.

    Args:
        scale_pos_weight: Ratio of negative to positive samples.
            Use get_scale_pos_weight(y_train) to compute automatically.
        n_estimators: Number of boosting rounds.
        max_depth: Maximum tree depth.
        learning_rate: Step size shrinkage (eta).
        subsample: Row subsampling ratio per tree.
        colsample_bytree: Column subsampling ratio per tree.
        min_child_weight: Minimum sum of instance weight in a child.
        gamma: Minimum loss reduction for a split.
        reg_alpha: L1 regularization term.
        reg_lambda: L2 regularization term.
        early_stopping_rounds: Stop if no improvement for N rounds.
        random_state: Reproducibility seed.

    Returns:
        XGBClassifier instance.
    """
    if not XGBOOST_AVAILABLE:
        raise ImportError("xgboost is required. Install with: pip install xgboost")

    return xgb.XGBClassifier(
        n_estimators=n_estimators,
        max_depth=max_depth,
        learning_rate=learning_rate,
        subsample=subsample,
        colsample_bytree=colsample_bytree,
        min_child_weight=min_child_weight,
        gamma=gamma,
        reg_alpha=reg_alpha,
        reg_lambda=reg_lambda,
        scale_pos_weight=scale_pos_weight,
        eval_metric="auc",
        early_stopping_rounds=early_stopping_rounds,
        random_state=random_state,
        n_jobs=-1,
        tree_method="hist",
        verbosity=0,
    )
