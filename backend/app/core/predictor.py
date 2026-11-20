"""
Core prediction logic.
Builds feature vector from request → runs model → postprocesses output.
"""
import time
from typing import List

import pandas as pd
from loguru import logger

from app.schemas.predict import PredictionRequest, PredictionResponse
from app.core.feature_builder import build_feature_vector
from app.core.explainer import SHAPExplainer
from app.utils.risk_utils import score_to_risk_level, score_to_confidence
from app.utils.geo_utils import generate_explanation


class Predictor:
    """
    Unified prediction pipeline for single and batch requests.
    Initialized once per request via FastAPI dependency injection.
    """

    def __init__(self, model, metadata: dict, explainer: SHAPExplainer):
        self.model      = model
        self.metadata   = metadata
        self.explainer  = explainer
        self.threshold  = metadata.get("optimal_threshold", 0.5)
        self.model_name = metadata.get("model_name", "unknown")
        self.feature_names = metadata.get("feature_names", [])

    def predict_single(self, request: PredictionRequest) -> PredictionResponse:
        """
        Full prediction pipeline for a single location.

        Steps:
            1. Build 23-feature vector matching training schema
            2. Run model.predict_proba()
            3. Apply optimal threshold
            4. Compute SHAP explanation (top 5 factors)
            5. Build human-readable explanation string
            6. Return typed PredictionResponse

        Args:
            request: Validated PredictionRequest.

        Returns:
            PredictionResponse with risk score, level, and explanation.
        """
        feature_df   = build_feature_vector(request, self.feature_names)
        risk_score   = float(self.model.predict_proba(feature_df)[0][1])
        is_blackspot = risk_score >= self.threshold
        top_factors  = self.explainer.explain(feature_df)
        explanation  = generate_explanation(top_factors, request)

        return PredictionResponse(
            is_blackspot=is_blackspot,
            risk_score=round(risk_score, 4),
            risk_level=score_to_risk_level(risk_score),
            confidence=score_to_confidence(risk_score, self.threshold),
            top_factors=top_factors,
            explanation=explanation,
            model_used=self.model_name,
            threshold_used=self.threshold,
            location={"latitude": request.latitude, "longitude": request.longitude},
        )

    def predict_batch(
        self,
        requests: List[PredictionRequest],
    ) -> List[PredictionResponse]:
        """
        Vectorized batch prediction.

        Builds all feature vectors at once and runs model.predict_proba()
        in a single call (much faster than looping).
        SHAP is computed only for HIGH/CRITICAL risk results to save compute.

        Args:
            requests: List of PredictionRequest objects.

        Returns:
            List of PredictionResponse objects.
        """
        t0 = time.time()

        # Build full feature matrix in one pass
        rows = [
            build_feature_vector(r, self.feature_names, as_dict=True)
            for r in requests
        ]
        feature_df = pd.DataFrame(rows)

        # Vectorized prediction
        probas = self.model.predict_proba(feature_df)[:, 1]

        results = []
        for i, (req, score) in enumerate(zip(requests, probas)):
            score    = float(score)
            is_bs    = score >= self.threshold
            risk_lvl = score_to_risk_level(score)

            # SHAP only for HIGH/CRITICAL — saves compute on large batches
            if score >= 0.55:
                factors = self.explainer.explain(feature_df.iloc[[i]])
            else:
                factors = []

            explanation = generate_explanation(factors, req) if factors else ""

            results.append(PredictionResponse(
                is_blackspot=is_bs,
                risk_score=round(score, 4),
                risk_level=risk_lvl,
                confidence=score_to_confidence(score, self.threshold),
                top_factors=factors,
                explanation=explanation,
                model_used=self.model_name,
                threshold_used=self.threshold,
                location={"latitude": req.latitude, "longitude": req.longitude},
            ))

        elapsed_ms = round((time.time() - t0) * 1000, 1)
        bs_count   = sum(1 for r in results if r.is_blackspot)
        logger.info(
            f"Batch {len(requests)} predictions in {elapsed_ms}ms | "
            f"{bs_count} black spots ({bs_count/len(requests):.1%})"
        )
        return results
