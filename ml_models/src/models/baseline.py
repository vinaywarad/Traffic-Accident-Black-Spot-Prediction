"""
Logistic Regression baseline model.
Interpretable, fast, establishes minimum performance bar.
All other models must beat this to justify their complexity.
"""
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

# Optuna search space spec: (type, *args)
LR_SEARCH_SPACE = {
    "clf__C":       ("float",       1e-4, 100.0, True),   # log scale
    "clf__solver":  ("categorical", ["lbfgs", "saga"]),
}


def build_logistic_regression(
    C: float = 1.0,
    solver: str = "lbfgs",
    max_iter: int = 1000,
    class_weight: str = "balanced",
    random_state: int = 42,
    **kwargs,
) -> Pipeline:
    """
    Build a Logistic Regression pipeline with StandardScaler.

    The scaler is included in the pipeline so it is correctly
    fit only on training data during cross-validation.

    Args:
        C: Inverse regularization strength (smaller = stronger regularization).
        solver: Optimization algorithm ('lbfgs' or 'saga').
        max_iter: Maximum iterations for convergence.
        class_weight: 'balanced' to handle residual class imbalance.
        random_state: Reproducibility seed.

    Returns:
        sklearn Pipeline with scaler + LogisticRegression.
    """
    return Pipeline([
        ("scaler", StandardScaler()),
        ("clf", LogisticRegression(
            C=C,
            solver=solver,
            max_iter=max_iter,
            class_weight=class_weight,
            random_state=random_state,
            n_jobs=-1,
        )),
    ])
