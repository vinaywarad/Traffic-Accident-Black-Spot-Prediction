"""
Unit tests for all model builders and the training pipeline.
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest
import numpy as np
import pandas as pd
from sklearn.datasets import make_classification


# ── Fixtures ─────────────────────────────────────────────────────────────────

@pytest.fixture
def binary_data():
    """Small imbalanced binary classification dataset."""
    X, y = make_classification(
        n_samples=300, n_features=23, n_informative=15,
        n_redundant=5, weights=[0.85, 0.15],
        random_state=42,
    )
    feature_names = [
        "dist_to_nearest_junction", "num_junctions_500m", "road_risk_score",
        "accident_density_1km", "accident_density_500m", "nearest_blackspot_dist",
        "hour_sin", "hour_cos", "month_sin", "month_cos", "day_sin", "day_cos",
        "is_peak_hour", "is_night", "is_weekend", "is_monsoon", "is_festival_month",
        "days_since_epoch", "speed_limit", "vehicles_involved",
        "weather_encoded", "road_condition_encoded", "light_condition_encoded",
    ]
    X_df = pd.DataFrame(X, columns=feature_names)
    y_s  = pd.Series(y, name="is_blackspot")
    return X_df, y_s


@pytest.fixture
def train_test(binary_data):
    X, y = binary_data
    n = len(X)
    split = int(n * 0.8)
    return X.iloc[:split], X.iloc[split:], y.iloc[:split], y.iloc[split:]


# ── Logistic Regression tests ─────────────────────────────────────────────────

class TestLogisticRegression:

    def test_build_returns_pipeline(self):
        from src.models.baseline import build_logistic_regression
        from sklearn.pipeline import Pipeline
        model = build_logistic_regression()
        assert isinstance(model, Pipeline)

    def test_pipeline_has_scaler_and_clf(self):
        from src.models.baseline import build_logistic_regression
        model = build_logistic_regression()
        assert "scaler" in model.named_steps
        assert "clf" in model.named_steps

    def test_fit_and_predict(self, train_test):
        from src.models.baseline import build_logistic_regression
        X_tr, X_te, y_tr, y_te = train_test
        model = build_logistic_regression()
        model.fit(X_tr, y_tr)
        proba = model.predict_proba(X_te)
        assert proba.shape == (len(X_te), 2)
        assert (proba >= 0).all() and (proba <= 1).all()

    def test_custom_params(self):
        from src.models.baseline import build_logistic_regression
        model = build_logistic_regression(C=0.1, solver="saga")
        assert model.named_steps["clf"].C == 0.1


# ── Random Forest tests ───────────────────────────────────────────────────────

class TestRandomForest:

    def test_build_returns_rf(self):
        from src.models.random_forest import build_random_forest
        from sklearn.ensemble import RandomForestClassifier
        model = build_random_forest()
        assert isinstance(model, RandomForestClassifier)

    def test_oob_score_enabled(self):
        from src.models.random_forest import build_random_forest
        model = build_random_forest(oob_score=True)
        assert model.oob_score is True

    def test_fit_and_predict_proba(self, train_test):
        from src.models.random_forest import build_random_forest
        X_tr, X_te, y_tr, y_te = train_test
        model = build_random_forest(n_estimators=20)
        model.fit(X_tr, y_tr)
        proba = model.predict_proba(X_te)
        assert proba.shape[1] == 2
        assert np.allclose(proba.sum(axis=1), 1.0)

    def test_feature_importances_available(self, train_test):
        from src.models.random_forest import build_random_forest
        X_tr, X_te, y_tr, y_te = train_test
        model = build_random_forest(n_estimators=10)
        model.fit(X_tr, y_tr)
        assert hasattr(model, "feature_importances_")
        assert len(model.feature_importances_) == X_tr.shape[1]


# ── XGBoost tests ─────────────────────────────────────────────────────────────

class TestXGBoost:

    def test_build_xgboost(self):
        try:
            from src.models.xgboost_model import build_xgboost
            import xgboost as xgb
            model = build_xgboost(scale_pos_weight=5.0)
            assert isinstance(model, xgb.XGBClassifier)
        except ImportError:
            pytest.skip("xgboost not installed")

    def test_scale_pos_weight_computed(self):
        from src.models.xgboost_model import get_scale_pos_weight
        y = pd.Series([0] * 90 + [1] * 10)
        spw = get_scale_pos_weight(y)
        assert abs(spw - 9.0) < 0.1

    def test_fit_predict(self, train_test):
        try:
            from src.models.xgboost_model import build_xgboost
            X_tr, X_te, y_tr, y_te = train_test
            model = build_xgboost(n_estimators=20, early_stopping_rounds=5)
            model.fit(X_tr, y_tr, eval_set=[(X_te, y_te)], verbose=False)
            proba = model.predict_proba(X_te)
            assert proba.shape == (len(X_te), 2)
        except ImportError:
            pytest.skip("xgboost not installed")


# ── LightGBM tests ────────────────────────────────────────────────────────────

class TestLightGBM:

    def test_build_lightgbm(self):
        try:
            from src.models.lightgbm_model import build_lightgbm
            import lightgbm as lgb
            model = build_lightgbm()
            assert isinstance(model, lgb.LGBMClassifier)
        except ImportError:
            pytest.skip("lightgbm not installed")

    def test_fit_predict(self, train_test):
        try:
            from src.models.lightgbm_model import build_lightgbm
            X_tr, X_te, y_tr, y_te = train_test
            model = build_lightgbm(n_estimators=20)
            model.fit(X_tr, y_tr, eval_set=[(X_te, y_te)])
            proba = model.predict_proba(X_te)
            assert proba.shape == (len(X_te), 2)
        except ImportError:
            pytest.skip("lightgbm not installed")


# ── Data loader tests ─────────────────────────────────────────────────────────

class TestDataLoader:

    def test_synthetic_data_loads(self):
        from src.data_loader import load_splits
        X_train, X_test, y_train, y_test = load_splits()
        assert len(X_train) > 0
        assert len(X_test) > 0
        assert len(X_train) == len(y_train)
        assert len(X_test)  == len(y_test)

    def test_val_split_preserves_order(self):
        from src.data_loader import get_val_split
        X = pd.DataFrame({"f": range(100)})
        y = pd.Series([0] * 85 + [1] * 15)
        X_tr, X_val, y_tr, y_val = get_val_split(X, y, val_fraction=0.2)
        assert len(X_tr) + len(X_val) == 100
        # Last rows should be in val
        assert X_val.index[-1] == 99

    def test_binary_labels(self):
        from src.data_loader import load_splits
        _, _, y_train, y_test = load_splits()
        assert set(y_train.unique()).issubset({0, 1})
        assert set(y_test.unique()).issubset({0, 1})
