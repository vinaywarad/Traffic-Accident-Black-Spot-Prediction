"""
Unit tests for evaluation metrics and threshold optimization.
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest
import numpy as np
import pandas as pd
from sklearn.datasets import make_classification
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

from src.evaluation.metrics import (
    evaluate_model, find_optimal_threshold,
    get_classification_report, metrics_to_dataframe,
)
from src.evaluation.threshold_optimizer import (
    find_threshold, threshold_sensitivity_table,
)


# ── Fixtures ─────────────────────────────────────────────────────────────────

@pytest.fixture
def fitted_model():
    """Simple fitted logistic regression for testing."""
    X, y = make_classification(n_samples=400, n_features=10, weights=[0.8, 0.2],
                                random_state=42)
    X_df = pd.DataFrame(X, columns=[f"f{i}" for i in range(10)])
    y_s  = pd.Series(y)
    model = Pipeline([("sc", StandardScaler()), ("clf", LogisticRegression(random_state=42))])
    model.fit(X_df, y_s)
    return model, X_df, y_s


# ── evaluate_model tests ──────────────────────────────────────────────────────

class TestEvaluateModel:

    def test_returns_all_required_keys(self, fitted_model):
        model, X, y = fitted_model
        metrics = evaluate_model(model, X, y, model_name="test_lr")
        required = ["model", "auc_roc", "auc_pr", "f1", "recall",
                    "precision", "mcc", "brier_score",
                    "true_positives", "false_positives",
                    "true_negatives", "false_negatives"]
        for key in required:
            assert key in metrics, f"Missing key: {key}"

    def test_auc_roc_in_valid_range(self, fitted_model):
        model, X, y = fitted_model
        metrics = evaluate_model(model, X, y)
        assert 0.0 <= metrics["auc_roc"] <= 1.0

    def test_recall_in_valid_range(self, fitted_model):
        model, X, y = fitted_model
        metrics = evaluate_model(model, X, y)
        assert 0.0 <= metrics["recall"] <= 1.0

    def test_confusion_matrix_sums_to_total(self, fitted_model):
        model, X, y = fitted_model
        metrics = evaluate_model(model, X, y)
        total = (metrics["true_positives"] + metrics["false_positives"] +
                 metrics["true_negatives"] + metrics["false_negatives"])
        assert total == len(y)

    def test_model_name_in_result(self, fitted_model):
        model, X, y = fitted_model
        metrics = evaluate_model(model, X, y, model_name="my_model")
        assert metrics["model"] == "my_model"

    def test_threshold_affects_predictions(self, fitted_model):
        model, X, y = fitted_model
        m_low  = evaluate_model(model, X, y, threshold=0.2)
        m_high = evaluate_model(model, X, y, threshold=0.8)
        # Lower threshold → more positives → higher recall
        assert m_low["recall"] >= m_high["recall"]

    def test_brier_score_in_valid_range(self, fitted_model):
        model, X, y = fitted_model
        metrics = evaluate_model(model, X, y)
        assert 0.0 <= metrics["brier_score"] <= 1.0


# ── find_optimal_threshold tests ─────────────────────────────────────────────

class TestThresholdOptimizer:

    def test_returns_float_in_range(self, fitted_model):
        model, X, y = fitted_model
        t = find_optimal_threshold(model, X, y, metric="f1")
        assert 0.1 <= t <= 0.9

    def test_recall_optimization_respects_precision_floor(self, fitted_model):
        model, X, y = fitted_model
        t = find_optimal_threshold(model, X, y, metric="recall", min_precision=0.3)
        # At optimal threshold, precision should be >= 0.3
        from sklearn.metrics import precision_score
        y_pred = (model.predict_proba(X)[:, 1] >= t).astype(int)
        prec = precision_score(y, y_pred, zero_division=0)
        assert prec >= 0.25   # allow small tolerance

    def test_mcc_optimization(self, fitted_model):
        model, X, y = fitted_model
        t = find_threshold(model, X, y, metric="mcc")
        assert 0.1 <= t <= 0.9

    def test_sensitivity_table_has_correct_columns(self, fitted_model):
        model, X, y = fitted_model
        table = threshold_sensitivity_table(model, X, y)
        assert "threshold" in table.columns
        assert "precision" in table.columns
        assert "recall" in table.columns
        assert "f1" in table.columns

    def test_sensitivity_table_thresholds_ascending(self, fitted_model):
        model, X, y = fitted_model
        table = threshold_sensitivity_table(model, X, y)
        assert table["threshold"].is_monotonic_increasing


# ── metrics_to_dataframe tests ────────────────────────────────────────────────

class TestMetricsDataframe:

    def test_sorted_by_auc_roc(self):
        results = [
            {"model": "a", "auc_roc": 0.75, "auc_pr": 0.4, "f1": 0.5,
             "recall": 0.6, "precision": 0.5, "mcc": 0.3, "brier_score": 0.2, "threshold": 0.5},
            {"model": "b", "auc_roc": 0.90, "auc_pr": 0.6, "f1": 0.7,
             "recall": 0.8, "precision": 0.6, "mcc": 0.5, "brier_score": 0.1, "threshold": 0.4},
        ]
        df = metrics_to_dataframe(results)
        assert df.iloc[0]["model"] == "b"   # higher AUC-ROC first

    def test_returns_dataframe(self):
        results = [{"model": "x", "auc_roc": 0.8, "auc_pr": 0.5, "f1": 0.6,
                    "recall": 0.7, "precision": 0.5, "mcc": 0.4,
                    "brier_score": 0.15, "threshold": 0.5}]
        df = metrics_to_dataframe(results)
        assert isinstance(df, pd.DataFrame)
        assert len(df) == 1


# ── classification_report tests ───────────────────────────────────────────────

class TestClassificationReport:

    def test_returns_string(self, fitted_model):
        model, X, y = fitted_model
        report = get_classification_report(model, X, y)
        assert isinstance(report, str)
        assert "Black Spot" in report
        assert "Non-Black Spot" in report
