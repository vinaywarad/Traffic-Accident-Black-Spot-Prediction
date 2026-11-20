"""
Unified training interface for all models.
Handles MLflow logging, early stopping, model serialization, and metadata export.
"""
import json
import time
from pathlib import Path
from typing import Optional

import joblib
import pandas as pd
from loguru import logger

try:
    import mlflow
    import mlflow.sklearn
    MLFLOW_AVAILABLE = True
except ImportError:
    MLFLOW_AVAILABLE = False
    logger.warning("mlflow not installed — experiment tracking disabled")

from src.config import MODELS_DIR, MLFLOW_EXPERIMENT, MLFLOW_URI, RANDOM_STATE


def _setup_mlflow() -> None:
    if MLFLOW_AVAILABLE:
        mlflow.set_tracking_uri(MLFLOW_URI)
        mlflow.set_experiment(MLFLOW_EXPERIMENT)


class ModelTrainer:
    """
    Unified training wrapper for all model types.
    Handles MLflow logging, early stopping for boosting models,
    and serialization to disk.
    """

    def __init__(
        self,
        model_name: str,
        model,
        output_dir: Path = MODELS_DIR,
    ):
        self.model_name = model_name
        self.model      = model
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        _setup_mlflow()

    def train(
        self,
        X_train: pd.DataFrame,
        y_train: pd.Series,
        X_val: Optional[pd.DataFrame] = None,
        y_val: Optional[pd.Series]    = None,
    ):
        """
        Train the model with optional MLflow experiment tracking.

        For XGBoost/LightGBM: pass X_val/y_val for early stopping.
        For Logistic Regression/Random Forest: val set is ignored.

        Args:
            X_train: Training features.
            y_train: Training labels.
            X_val: Optional validation features (for early stopping).
            y_val: Optional validation labels.

        Returns:
            Fitted model.
        """
        logger.info(f"Training {self.model_name} | "
                    f"train={len(X_train)}, features={X_train.shape[1]}")
        t0 = time.time()

        ctx = mlflow.start_run(run_name=self.model_name) if MLFLOW_AVAILABLE else _NullCtx()

        with ctx:
            # Fit model — boosting models use eval_set for early stopping
            is_boosting = self.model_name in ("xgboost", "lightgbm")
            if is_boosting and X_val is not None:
                self.model.fit(
                    X_train, y_train,
                    eval_set=[(X_val, y_val)],
                    verbose=False,
                )
            else:
                self.model.fit(X_train, y_train)

            elapsed = round(time.time() - t0, 1)
            logger.success(f"{self.model_name} trained in {elapsed}s")

            # Log to MLflow
            if MLFLOW_AVAILABLE:
                try:
                    params = _safe_get_params(self.model)
                    mlflow.log_params(params)
                    mlflow.log_param("train_samples", len(X_train))
                    mlflow.log_param("train_time_s",  elapsed)
                    mlflow.sklearn.log_model(self.model, self.model_name)
                except Exception as e:
                    logger.warning(f"MLflow logging failed: {e}")

            # OOB score for Random Forest
            if hasattr(self.model, "oob_score_"):
                logger.info(f"OOB score: {self.model.oob_score_:.4f}")

        # Save to disk
        self.save()
        return self.model

    def save(self) -> Path:
        """Serialize model to disk as .pkl."""
        path = self.output_dir / f"{self.model_name}.pkl"
        joblib.dump(self.model, path)
        size_mb = path.stat().st_size / 1_048_576
        logger.info(f"Saved {self.model_name} → {path} ({size_mb:.1f} MB)")
        return path


def load_model(model_name: str, models_dir: Path = MODELS_DIR):
    """
    Load a saved model from disk.

    Args:
        model_name: Name without .pkl extension.
        models_dir: Directory containing saved models.

    Returns:
        Loaded model object.
    """
    path = Path(models_dir) / f"{model_name}.pkl"
    if not path.exists():
        raise FileNotFoundError(f"Model not found: {path}")
    model = joblib.load(path)
    logger.info(f"Loaded {model_name} from {path}")
    return model


def _safe_get_params(model) -> dict:
    """Extract params safely, handling Pipeline and nested estimators."""
    try:
        params = model.get_params()
        # Flatten and stringify for MLflow (no nested dicts)
        return {k: str(v) for k, v in params.items() if not isinstance(v, dict)}
    except Exception:
        return {}


class _NullCtx:
    """No-op context manager when MLflow is unavailable."""
    def __enter__(self): return self
    def __exit__(self, *args): pass
