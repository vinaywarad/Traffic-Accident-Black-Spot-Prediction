"""
Handle severe class imbalance (black spots are rare ~8–15% of records).
Strategy: SMOTE on training set only — NEVER on test set.
"""
import pandas as pd
import numpy as np
from loguru import logger

try:
    from imblearn.over_sampling import SMOTE, ADASYN
    from imblearn.combine import SMOTETomek
    IMBLEARN_AVAILABLE = True
except ImportError:
    IMBLEARN_AVAILABLE = False
    logger.warning("imbalanced-learn not available — using random oversampling fallback")

from src.config import RANDOM_STATE


def balance_classes(
    X_train: pd.DataFrame,
    y_train: pd.Series,
    strategy: str = "smote_tomek",
) -> tuple[pd.DataFrame, pd.Series]:
    """
    Balance class distribution in the training set.

    IMPORTANT: Apply ONLY to training data, never to test data.

    Strategy options:
        - 'smote'        : Oversample minority class with SMOTE
        - 'smote_tomek'  : SMOTE + Tomek link removal (recommended)
        - 'adasyn'       : Adaptive synthetic sampling
        - 'random'       : Simple random oversampling (fallback)

    Args:
        X_train: Training feature DataFrame.
        y_train: Training target Series.
        strategy: Balancing strategy name.

    Returns:
        Tuple of (X_balanced, y_balanced).
    """
    before = y_train.value_counts().to_dict()
    logger.info(f"Class distribution before balancing: {before}")

    if not IMBLEARN_AVAILABLE or strategy == "random":
        return _random_oversample(X_train, y_train)

    if strategy == "smote":
        sampler = SMOTE(random_state=RANDOM_STATE, k_neighbors=5)
    elif strategy == "smote_tomek":
        sampler = SMOTETomek(random_state=RANDOM_STATE)
    elif strategy == "adasyn":
        sampler = ADASYN(random_state=RANDOM_STATE)
    else:
        raise ValueError(f"Unknown strategy: {strategy}. "
                         "Choose from: smote, smote_tomek, adasyn, random")

    X_bal, y_bal = sampler.fit_resample(X_train, y_train)

    # Convert back to DataFrame/Series with original column names
    X_bal = pd.DataFrame(X_bal, columns=X_train.columns)
    y_bal = pd.Series(y_bal, name=y_train.name)

    after = y_bal.value_counts().to_dict()
    logger.info(
        f"After {strategy}: {after} | "
        f"total: {len(y_bal)} (was {len(y_train)})"
    )
    return X_bal, y_bal


def _random_oversample(
    X: pd.DataFrame,
    y: pd.Series,
) -> tuple[pd.DataFrame, pd.Series]:
    """
    Simple random oversampling of the minority class.
    Used as fallback when imbalanced-learn is not available.
    """
    rng = np.random.default_rng(RANDOM_STATE)
    minority_mask = y == 1
    n_majority = (y == 0).sum()
    n_minority = minority_mask.sum()
    n_to_add   = n_majority - n_minority

    if n_to_add <= 0:
        return X, y

    minority_indices = np.where(minority_mask)[0]
    oversample_idx   = rng.choice(minority_indices, size=n_to_add, replace=True)

    X_over = pd.concat([X, X.iloc[oversample_idx]], ignore_index=True)
    y_over = pd.concat([y, y.iloc[oversample_idx]], ignore_index=True)

    logger.info(f"Random oversampling: {n_minority} → {n_majority} minority samples")
    return X_over, y_over


def get_class_weights(y: pd.Series) -> dict:
    """
    Compute class weights for use in sklearn estimators (class_weight='balanced').

    Args:
        y: Target Series with binary labels.

    Returns:
        Dict mapping class label to weight.
    """
    counts = y.value_counts()
    total  = len(y)
    weights = {cls: total / (len(counts) * count) for cls, count in counts.items()}
    logger.info(f"Class weights: {weights}")
    return weights
