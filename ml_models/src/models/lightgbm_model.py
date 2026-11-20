"""
LightGBM classifier.
Faster than XGBoost, better on large datasets, excellent AUC.
Often matches or beats XGBoost with less tuning.
"""
from loguru import logger

try:
    import lightgbm as lgb
    LIGHTGBM_AVAILABLE = True
except ImportError:
    LIGHTGBM_AVAILABLE = False
    logger.warning("lightgbm not installed — LightGBM model unavailable")

# Optuna search space
LGBM_SEARCH_SPACE = {
    "n_estimators":      ("int",   200, 1000),
    "max_depth":         ("int",   3,   12),
    "num_leaves":        ("int",   20,  200),
    "learning_rate":     ("float", 0.01, 0.3, True),   # log scale
    "min_child_samples": ("int",   10,  100),
    "subsample":         ("float", 0.5,  1.0),
    "colsample_bytree":  ("float", 0.5,  1.0),
}


def build_lightgbm(
    n_estimators: int = 500,
    max_depth: int = 7,
    learning_rate: float = 0.05,
    num_leaves: int = 63,
    min_child_samples: int = 20,
    subsample: float = 0.8,
    colsample_bytree: float = 0.8,
    reg_alpha: float = 0.1,
    reg_lambda: float = 1.0,
    is_unbalance: bool = True,
    random_state: int = 42,
    **kwargs,
):
    """
    Build a LightGBM classifier.

    Args:
        n_estimators: Number of boosting rounds.
        max_depth: Maximum tree depth (-1 = unlimited).
        learning_rate: Step size shrinkage.
        num_leaves: Maximum number of leaves per tree (2^max_depth - 1 rule).
        min_child_samples: Minimum data in a leaf node.
        subsample: Row subsampling ratio per tree.
        colsample_bytree: Column subsampling ratio per tree.
        reg_alpha: L1 regularization.
        reg_lambda: L2 regularization.
        is_unbalance: Automatically handle class imbalance internally.
        random_state: Reproducibility seed.

    Returns:
        LGBMClassifier instance.
    """
    if not LIGHTGBM_AVAILABLE:
        raise ImportError("lightgbm is required. Install with: pip install lightgbm")

    return lgb.LGBMClassifier(
        n_estimators=n_estimators,
        max_depth=max_depth,
        learning_rate=learning_rate,
        num_leaves=num_leaves,
        min_child_samples=min_child_samples,
        subsample=subsample,
        colsample_bytree=colsample_bytree,
        reg_alpha=reg_alpha,
        reg_lambda=reg_lambda,
        is_unbalance=is_unbalance,
        random_state=random_state,
        n_jobs=-1,
        verbose=-1,
    )
