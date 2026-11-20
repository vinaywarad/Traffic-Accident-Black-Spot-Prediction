"""
Unit tests for SHAP explainability and feature importance modules.
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest
import numpy as np
import pandas as pd
from sklearn.datasets import make_classification
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

from src.explainability.feature_importance import (
    get_builtin_importance, get_permutation_importance,
)
from src.explainability.local_explainer import (
    score_to_risk_level, explain_prediction, _rule_based_factors,
)


# ── Fixtures ─────────────────────────────────────────────────────────────────

@pytest.fixture
def rf_model_and_data():
    """Fitted Random Forest with feature names."""
    X, y = make_classification(n_samples=300, n_features=10, weights=[0.8, 0.2],
                                random_state=42)
    feature_names = [f"feature_{i}" for i in range(10)]
    X_df = pd.DataFrame(X, columns=feature_names)
    y_s  = pd.Series(y, name="is_blackspot")
    model = RandomForestClassifier(n_estimators=20, random_state=42)
    model.fit(X_df, y_s)
    return model, X_df, y_s, feature_names


@pytest.fixture
def lr_model_and_data():
    """Fitted Logistic Regression pipeline."""
    X, y = make_classification(n_samples=300, n_features=10, weights=[0.8, 0.2],
                                random_state=42)
    feature_names = [f"feature_{i}" for i in range(10)]
    X_df = pd.DataFrame(X, columns=feature_names)
    y_s  = pd.Series(y, name="is_blackspot")
    model = Pipeline([("sc", StandardScaler()), ("clf", LogisticRegression(random_state=42))])
    model.fit(X_df, y_s)
    return model, X_df, y_s, feature_names


# ── score_to_risk_level tests ─────────────────────────────────────────────────

class TestRiskLevel:

    def test_critical_threshold(self):
        assert score_to_risk_level(0.80) == "CRITICAL"
        assert score_to_risk_level(0.75) == "CRITICAL"

    def test_high_threshold(self):
        assert score_to_risk_level(0.65) == "HIGH"
        assert score_to_risk_level(0.55) == "HIGH"

    def test_medium_threshold(self):
        assert score_to_risk_level(0.45) == "MEDIUM"
        assert score_to_risk_level(0.35) == "MEDIUM"

    def test_low_threshold(self):
        assert score_to_risk_level(0.20) == "LOW"
        assert score_to_risk_level(0.0)  == "LOW"

    def test_boundary_values(self):
        assert score_to_risk_level(0.749) == "HIGH"
        assert score_to_risk_level(0.750) == "CRITICAL"


# ── feature_importance tests ──────────────────────────────────────────────────

class TestFeatureImportance:

    def test_builtin_importance_rf(self, rf_model_and_data):
        model, X, y, names = rf_model_and_data
        df = get_builtin_importance(model, names)
        assert len(df) == len(names)
        assert "feature" in df.columns
        assert "importance" in df.columns
        assert df["importance"].sum() > 0

    def test_builtin_importance_sorted_descending(self, rf_model_and_data):
        model, X, y, names = rf_model_and_data
        df = get_builtin_importance(model, names)
        assert df["importance"].is_monotonic_decreasing

    def test_builtin_importance_lr(self, lr_model_and_data):
        model, X, y, names = lr_model_and_data
        df = get_builtin_importance(model, names)
        assert len(df) == len(names)

    def test_permutation_importance_returns_df(self, rf_model_and_data):
        model, X, y, names = rf_model_and_data
        df = get_permutation_importance(model, X, y, n_repeats=3)
        assert "feature" in df.columns
        assert "mean_importance" in df.columns
        assert "std_importance" in df.columns
        assert len(df) == len(names)

    def test_permutation_importance_std_non_negative(self, rf_model_and_data):
        model, X, y, names = rf_model_and_data
        df = get_permutation_importance(model, X, y, n_repeats=3)
        assert (df["std_importance"] >= 0).all()


# ── local_explainer tests ─────────────────────────────────────────────────────

class TestLocalExplainer:

    def test_explain_prediction_returns_dict(self, rf_model_and_data):
        model, X, y, names = rf_model_and_data
        sample = X.iloc[[0]]
        result = explain_prediction(model, sample)
        assert "risk_score" in result
        assert "risk_level" in result
        assert "is_blackspot" in result
        assert "confidence" in result

    def test_risk_score_in_range(self, rf_model_and_data):
        model, X, y, names = rf_model_and_data
        sample = X.iloc[[0]]
        result = explain_prediction(model, sample)
        assert 0.0 <= result["risk_score"] <= 1.0

    def test_confidence_in_range(self, rf_model_and_data):
        model, X, y, names = rf_model_and_data
        sample = X.iloc[[0]]
        result = explain_prediction(model, sample)
        assert 0.5 <= result["confidence"] <= 1.0

    def test_rule_based_factors_peak_hour(self):
        row = pd.DataFrame({
            "is_peak_hour": [1], "is_monsoon": [0], "weather_encoded": [1],
            "nearest_blackspot_dist": [9999], "accident_density_1km": [0],
            "road_risk_score": [1], "is_night": [0],
        })
        factors = _rule_based_factors(row)
        feature_names = [f["feature"] for f in factors]
        assert "is_peak_hour" in feature_names

    def test_rule_based_factors_monsoon(self):
        row = pd.DataFrame({
            "is_peak_hour": [0], "is_monsoon": [1], "weather_encoded": [1],
            "nearest_blackspot_dist": [9999], "accident_density_1km": [0],
            "road_risk_score": [1], "is_night": [0],
        })
        factors = _rule_based_factors(row)
        feature_names = [f["feature"] for f in factors]
        assert "is_monsoon" in feature_names

    def test_max_five_factors_returned(self):
        row = pd.DataFrame({
            "is_peak_hour": [1], "is_monsoon": [1], "weather_encoded": [5],
            "nearest_blackspot_dist": [100], "accident_density_1km": [10],
            "road_risk_score": [5], "is_night": [1],
        })
        factors = _rule_based_factors(row)
        assert len(factors) <= 5


# ── SHAP explainer tests (requires shap) ─────────────────────────────────────

class TestSHAPExplainer:

    def test_tree_explainer_initializes(self, rf_model_and_data):
        try:
            from src.explainability.shap_explainer import BlackSpotExplainer
            model, X, y, names = rf_model_and_data
            explainer = BlackSpotExplainer(model, X, "tree", names)
            assert explainer.model_type == "tree"
        except ImportError:
            pytest.skip("shap not installed")

    def test_compute_shap_values_shape(self, rf_model_and_data):
        try:
            from src.explainability.shap_explainer import BlackSpotExplainer
            model, X, y, names = rf_model_and_data
            explainer = BlackSpotExplainer(model, X, "tree", names)
            sv = explainer.compute_shap_values(X, sample_size=50)
            assert sv.shape[1] == len(names)
        except ImportError:
            pytest.skip("shap not installed")

    def test_get_top_features_json(self, rf_model_and_data):
        try:
            from src.explainability.shap_explainer import BlackSpotExplainer
            model, X, y, names = rf_model_and_data
            explainer = BlackSpotExplainer(model, X, "tree", names)
            explainer.compute_shap_values(X, sample_size=50)
            top = explainer.get_top_features_json(top_n=5)
            assert len(top) == 5
            assert all("feature" in f and "importance" in f for f in top)
        except ImportError:
            pytest.skip("shap not installed")
