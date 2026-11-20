"""
Bayesian hyperparameter optimization using Optuna.
Much more efficient than GridSearchCV for large search spaces.
"""
import pandas as pd
from loguru import logger

try:
    import optuna
    optuna.logging.set_verbosity(optuna.logging.WARNING)
    OPTUNA_AVAILABLE = True
except ImportError:
    OPTUNA_AVAILABLE = False
    logger.warning("optuna not installed — hyperparameter tuning disabled")

from sklearn.model_selection import StratifiedKFold, cross_val_score

from src.config import N_TRIALS, TUNE_METRIC, TUNE_TIMEOUT, RANDOM_STATE, CV_FOLDS


def tune_model(
    model_builder_fn,
    X_train: pd.DataFrame,
    y_train: pd.Series,
    search_space: dict,
    n_trials: int = N_TRIALS,
    cv_folds: int = CV_FOLDS,
    metric: str = TUNE_METRIC,
    timeout: int = TUNE_TIMEOUT,
) -> dict:
    """
    Run Optuna Bayesian hyperparameter search.

    Args:
        model_builder_fn: Callable that accepts **params and returns a model.
        X_train: Training features.
        y_train: Training labels.
        search_space: Dict mapping param_name → (type, *args) spec.
            Types: 'int', 'float', 'categorical'
            Float spec: ('float', low, high, log_scale=False)
        n_trials: Number of Optuna trials (50 = good balance of speed/quality).
        cv_folds: Number of CV folds per trial.
        metric: sklearn scoring metric to maximize.
        timeout: Maximum tuning time in seconds.

    Returns:
        Dict of best hyperparameters.
    """
    if not OPTUNA_AVAILABLE:
        logger.warning("optuna not available — returning default params")
        return {}

    def objective(trial) -> float:
        params = _sample_params(trial, search_space)
        try:
            model = model_builder_fn(**params)
        except Exception as e:
            logger.debug(f"Model build failed for params {params}: {e}")
            raise optuna.exceptions.TrialPruned()

        cv = StratifiedKFold(n_splits=cv_folds, shuffle=True, random_state=RANDOM_STATE)
        scores = cross_val_score(model, X_train, y_train,
                                 cv=cv, scoring=metric, n_jobs=-1)
        return float(scores.mean())

    study = optuna.create_study(
        direction="maximize",
        sampler=optuna.samplers.TPESampler(seed=RANDOM_STATE),
        pruner=optuna.pruners.MedianPruner(n_startup_trials=10),
    )
    study.optimize(
        objective,
        n_trials=n_trials,
        timeout=timeout,
        show_progress_bar=False,
        n_jobs=1,
    )

    best_params = study.best_params
    best_value  = study.best_value

    logger.success(f"Optuna tuning complete | best {metric}: {best_value:.4f}")
    logger.info(f"Best params: {best_params}")
    return best_params


def _sample_params(trial, search_space: dict) -> dict:
    """Sample hyperparameters from the search space for one Optuna trial."""
    params = {}
    for param, spec in search_space.items():
        kind = spec[0]
        # Strip pipeline prefix (e.g. "clf__C" → "C") for direct model builders
        key = param.split("__")[-1]

        if kind == "int":
            params[key] = trial.suggest_int(param, spec[1], spec[2])
        elif kind == "float":
            log = len(spec) > 3 and bool(spec[3])
            params[key] = trial.suggest_float(param, spec[1], spec[2], log=log)
        elif kind == "categorical":
            params[key] = trial.suggest_categorical(param, spec[1])
    return params


def get_importance_df(study) -> pd.DataFrame:
    """
    Return hyperparameter importance from a completed Optuna study.

    Args:
        study: Completed optuna.Study object.

    Returns:
        DataFrame with param name and importance score.
    """
    if not OPTUNA_AVAILABLE:
        return pd.DataFrame()
    importance = optuna.importance.get_param_importances(study)
    return pd.DataFrame(
        list(importance.items()), columns=["parameter", "importance"]
    ).sort_values("importance", ascending=False)
