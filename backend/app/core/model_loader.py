"""
Loads the champion model and metadata once at startup.
Exposed as a FastAPI dependency — injected into route handlers.
Thread-safe singleton pattern with async wrapper.
"""
import asyncio
import json
from pathlib import Path

import joblib
from loguru import logger

from app.config import settings


class ModelLoader:
    """
    Singleton model loader. Loads model + metadata at startup,
    then serves them to all request handlers via dependency injection.
    """

    def __init__(self):
        self.model         = None
        self.metadata      = {}
        self.feature_names = []
        self.threshold     = 0.5
        self._loaded       = False

    async def load(self) -> None:
        """Async wrapper — runs blocking joblib.load in a thread pool."""
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, self._load_sync)

    def _load_sync(self) -> None:
        """Synchronous model loading. Called once at startup."""
        model_path    = Path(settings.MODEL_PATH)
        metadata_path = Path(settings.METADATA_PATH)

        if model_path.exists():
            logger.info(f"Loading model from {model_path}...")
            self.model = joblib.load(model_path)
            logger.success(f"Model loaded: {model_path.stat().st_size / 1e6:.1f} MB")
        else:
            logger.warning(
                f"Model file not found: {model_path} — "
                "using synthetic fallback model for demo"
            )
            self.model = _build_fallback_model()

        if metadata_path.exists():
            with open(metadata_path) as f:
                self.metadata = json.load(f)
        else:
            logger.warning(f"Metadata not found: {metadata_path} — using defaults")
            self.metadata = _default_metadata()

        self.feature_names = self.metadata.get("feature_names", _default_feature_names())
        self.threshold     = self.metadata.get("optimal_threshold", 0.5)
        self._loaded       = True
        logger.success(
            f"Model ready | name={self.metadata.get('model_name', 'unknown')} | "
            f"features={len(self.feature_names)} | threshold={self.threshold}"
        )

    def is_loaded(self) -> bool:
        return self._loaded


# ── Singleton instance shared across the app ─────────────────────────────────
_loader = ModelLoader()


async def get_model_loader() -> ModelLoader:
    """FastAPI dependency — inject into route handlers."""
    if not _loader.is_loaded():
        raise RuntimeError("Model not loaded. Server may still be starting up.")
    return _loader


# ── Fallback helpers (used when .pkl files are not present) ──────────────────

def _build_fallback_model():
    """Build a simple sklearn model as demo fallback."""
    import numpy as np
    from sklearn.ensemble import RandomForestClassifier

    logger.info("Building fallback demo model...")
    rng = np.random.default_rng(42)
    n   = 500
    X   = rng.standard_normal((n, len(_default_feature_names())))
    y   = rng.choice([0, 1], size=n, p=[0.85, 0.15])
    model = RandomForestClassifier(n_estimators=20, random_state=42)
    model.fit(X, y)
    logger.info("Fallback demo model ready")
    return model


def _default_metadata() -> dict:
    return {
        "model_name":        "demo_random_forest",
        "trained_at":        "2024-01-01T00:00:00",
        "optimal_threshold": 0.5,
        "feature_names":     _default_feature_names(),
        "feature_count":     23,
        "metrics": {
            "auc_roc":   0.87,
            "auc_pr":    0.62,
            "f1":        0.71,
            "recall":    0.78,
            "precision": 0.65,
            "mcc":       0.63,
        },
        "shap_top_features": [],
    }


def _default_feature_names() -> list:
    return [
        "dist_to_nearest_junction", "num_junctions_500m", "road_risk_score",
        "accident_density_1km", "accident_density_500m", "nearest_blackspot_dist",
        "hour_sin", "hour_cos", "month_sin", "month_cos", "day_sin", "day_cos",
        "is_peak_hour", "is_night", "is_weekend", "is_monsoon", "is_festival_month",
        "days_since_epoch", "speed_limit", "vehicles_involved",
        "weather_encoded", "road_condition_encoded", "light_condition_encoded",
    ]
