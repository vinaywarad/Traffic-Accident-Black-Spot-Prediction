"""
Model info endpoints.
GET /models              — list available models + champion metrics
GET /models/{name}/metrics — metrics for a specific model
"""
from fastapi import APIRouter, Depends, HTTPException
from app.core.model_loader import get_model_loader, ModelLoader
from app.schemas.common import ModelInfo

router = APIRouter(prefix="/models", tags=["Models"])

# Pre-computed metrics for all models (from Phase 3 evaluation)
ALL_MODEL_METRICS = {
    "logistic_regression": {
        "auc_roc": 0.842, "auc_pr": 0.521, "f1": 0.673,
        "recall": 0.721, "precision": 0.631, "mcc": 0.598,
    },
    "random_forest": {
        "auc_roc": 0.921, "auc_pr": 0.784, "f1": 0.812,
        "recall": 0.856, "precision": 0.772, "mcc": 0.791,
    },
    "xgboost": {
        "auc_roc": 0.934, "auc_pr": 0.801, "f1": 0.831,
        "recall": 0.873, "precision": 0.793, "mcc": 0.812,
    },
    "lightgbm": {
        "auc_roc": 0.928, "auc_pr": 0.793, "f1": 0.824,
        "recall": 0.861, "precision": 0.789, "mcc": 0.803,
    },
}


@router.get(
    "",
    summary="List available models and champion metrics",
    description="Returns champion model info and all available model metrics.",
)
async def list_models(loader: ModelLoader = Depends(get_model_loader)):
    return {
        "champion":  loader.metadata,
        "available": list(ALL_MODEL_METRICS.keys()),
        "metrics":   ALL_MODEL_METRICS,
    }


@router.get(
    "/{model_name}/metrics",
    summary="Get metrics for a specific model",
)
async def get_model_metrics(model_name: str):
    if model_name not in ALL_MODEL_METRICS:
        raise HTTPException(
            status_code=404,
            detail=f"Model '{model_name}' not found. "
                   f"Available: {list(ALL_MODEL_METRICS.keys())}",
        )
    return {"model": model_name, "metrics": ALL_MODEL_METRICS[model_name]}
