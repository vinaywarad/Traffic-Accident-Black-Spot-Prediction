"""
Export champion model + metadata for consumption by the FastAPI backend.
Produces: best_model.pkl + model_metadata.json
"""
import json
import shutil
from datetime import datetime
from pathlib import Path

import joblib
from loguru import logger

from src.config import MODELS_DIR, BEST_MODEL, METADATA_PATH


def export_champion_model(
    model,
    model_name: str,
    metrics: dict,
    feature_names: list,
    threshold: float,
    shap_top_features: list = None,
    output_dir: Path = None,
) -> dict:
    """
    Save the champion model and its metadata for the FastAPI backend.

    Produces:
        - models/best_model.pkl       → loaded by FastAPI at startup
        - models/model_metadata.json  → model card with metrics + feature list

    Args:
        model: Fitted champion model.
        model_name: Name of the champion model.
        metrics: Evaluation metrics dict from evaluate_model().
        feature_names: Ordered list of feature column names.
        threshold: Optimal decision threshold.
        shap_top_features: Top SHAP features list (optional).
        output_dir: Override output directory.

    Returns:
        Metadata dict.
    """
    out_dir = Path(output_dir) if output_dir else BEST_MODEL.parent
    out_dir.mkdir(parents=True, exist_ok=True)

    # Save model binary
    model_path = out_dir / "best_model.pkl"
    joblib.dump(model, model_path)
    size_mb = model_path.stat().st_size / 1_048_576
    logger.success(f"Champion model saved → {model_path} ({size_mb:.1f} MB)")

    # Also save a named copy in models/saved/
    named_copy = MODELS_DIR / f"{model_name}.pkl"
    MODELS_DIR.mkdir(parents=True, exist_ok=True)
    if not named_copy.exists():
        shutil.copy2(model_path, named_copy)

    # Build metadata
    metadata = {
        "model_name":          model_name,
        "trained_at":          datetime.now().isoformat(),
        "optimal_threshold":   round(threshold, 4),
        "feature_names":       feature_names,
        "feature_count":       len(feature_names),
        "metrics": {
            "auc_roc":   metrics.get("auc_roc"),
            "auc_pr":    metrics.get("auc_pr"),
            "f1":        metrics.get("f1"),
            "recall":    metrics.get("recall"),
            "precision": metrics.get("precision"),
            "mcc":       metrics.get("mcc"),
            "brier_score": metrics.get("brier_score"),
        },
        "shap_top_features":   shap_top_features or [],
        "blackspot_definition": "3+ accidents within 500m in 12-month window (IRC/WHO)",
        "training_data":       "Bengaluru 2019–2022 | Test: 2023",
        "class_balance_strategy": "SMOTE-Tomek on training set only",
        "risk_thresholds": {
            "CRITICAL": 0.75,
            "HIGH":     0.55,
            "MEDIUM":   0.35,
            "LOW":      0.0,
        },
    }

    # Save metadata JSON
    meta_path = out_dir / "model_metadata.json"
    with open(meta_path, "w") as f:
        json.dump(metadata, f, indent=2)
    logger.success(f"Metadata saved → {meta_path}")

    return metadata


def load_champion_model(model_path: Path = None):
    """
    Load the champion model from disk.

    Args:
        model_path: Path to best_model.pkl (uses default if None).

    Returns:
        Loaded model object.
    """
    path = Path(model_path) if model_path else BEST_MODEL
    if not path.exists():
        raise FileNotFoundError(
            f"Champion model not found: {path}\n"
            "Run: python train.py --model all --export"
        )
    model = joblib.load(path)
    logger.info(f"Loaded champion model from {path}")
    return model


def load_metadata(meta_path: Path = None) -> dict:
    """
    Load model metadata JSON.

    Args:
        meta_path: Path to model_metadata.json.

    Returns:
        Metadata dict.
    """
    path = Path(meta_path) if meta_path else METADATA_PATH
    if not path.exists():
        raise FileNotFoundError(f"Metadata not found: {path}")
    with open(path) as f:
        return json.load(f)
