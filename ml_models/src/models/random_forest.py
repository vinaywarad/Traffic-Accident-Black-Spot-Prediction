"""
Random Forest classifier.
Strong non-linear baseline. Handles feature interactions well.
Provides built-in feature importance scores and OOB validation.
"""
from sklearn.ensemble import RandomForestClassifier

# Optuna search space
RF_SEARCH_SPACE = {
    "n_estimators":      ("int",        100, 800),
    "max_depth":         ("int",        5,   30),
    "min_samples_split": ("int",        2,   20),
    "min_samples_leaf":  ("int",        1,   10),
    "max_features":      ("categorical", ["sqrt", "log2"]),
}


def build_random_forest(
    n_estimators: int = 300,
    max_depth: int = 15,
    min_samples_split: int = 5,
    min_samples_leaf: int = 2,
    max_features: str = "sqrt",
    class_weight: str = "balanced_subsample",
    random_state: int = 42,
    oob_score: bool = True,
    **kwargs,
) -> RandomForestClassifier:
    """
    Build a Random Forest classifier.

    Args:
        n_estimators: Number of trees.
        max_depth: Maximum tree depth (None = unlimited).
        min_samples_split: Minimum samples to split an internal node.
        min_samples_leaf: Minimum samples in a leaf node.
        max_features: Features to consider at each split ('sqrt' or 'log2').
        class_weight: 'balanced_subsample' recomputes weights per bootstrap sample.
        random_state: Reproducibility seed.
        oob_score: Compute out-of-bag score (free validation estimate).

    Returns:
        RandomForestClassifier instance.
    """
    return RandomForestClassifier(
        n_estimators=n_estimators,
        max_depth=max_depth,
        min_samples_split=min_samples_split,
        min_samples_leaf=min_samples_leaf,
        max_features=max_features,
        class_weight=class_weight,
        random_state=random_state,
        n_jobs=-1,
        oob_score=oob_score,
    )
