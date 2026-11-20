"""
Prediction endpoints.
POST /predict        — single location
POST /predict/batch  — up to 500 locations
"""
import hashlib
import time
from fastapi import APIRouter, Depends
from loguru import logger

from app.schemas.predict import (
    PredictionRequest, PredictionResponse,
    BatchPredictionRequest, BatchPredictionResponse,
)
from app.core.model_loader import get_model_loader, ModelLoader
from app.core.predictor import Predictor
from app.core.explainer import SHAPExplainer
from app.utils.cache import get_cached, set_cached
from app.config import settings

router = APIRouter(prefix="/predict", tags=["Predictions"])


def _get_predictor(loader: ModelLoader = Depends(get_model_loader)) -> Predictor:
    """Build Predictor with SHAP explainer — called per request."""
    model_type = (
        "linear" if "logistic" in loader.metadata.get("model_name", "") else "tree"
    )
    explainer = SHAPExplainer(loader.model, loader.feature_names, model_type)
    return Predictor(loader.model, loader.metadata, explainer)


@router.post(
    "",
    response_model=PredictionResponse,
    summary="Predict single location risk",
    description=(
        "Predict whether a road location in Bengaluru is a traffic black spot. "
        "Returns risk score (0–1), risk level, and top contributing factors."
    ),
)
async def predict_single(
    request: PredictionRequest,
    predictor: Predictor = Depends(_get_predictor),
):
    # Check cache first
    cache_key = hashlib.md5(request.model_dump_json().encode()).hexdigest()
    cached = await get_cached(cache_key)
    if cached:
        logger.debug(f"Cache hit: {cache_key[:8]}")
        return PredictionResponse(**cached)

    result = predictor.predict_single(request)

    # Cache result
    await set_cached(cache_key, result.model_dump(), ttl=settings.CACHE_TTL)
    return result


@router.post(
    "/batch",
    response_model=BatchPredictionResponse,
    summary="Batch predict multiple locations",
    description=(
        "Predict risk for up to 500 locations in a single call. "
        "SHAP explanations are computed only for HIGH/CRITICAL risk locations. "
        "Used by the map page to score road segments simultaneously."
    ),
)
async def predict_batch(
    request: BatchPredictionRequest,
    predictor: Predictor = Depends(_get_predictor),
):
    t0 = time.time()
    predictions = predictor.predict_batch(request.records)
    bs_count    = sum(1 for p in predictions if p.is_blackspot)
    avg_risk    = sum(p.risk_score for p in predictions) / len(predictions)

    return BatchPredictionResponse(
        predictions=predictions,
        total=len(predictions),
        blackspot_count=bs_count,
        avg_risk_score=round(avg_risk, 4),
        processing_ms=round((time.time() - t0) * 1000, 2),
    )
