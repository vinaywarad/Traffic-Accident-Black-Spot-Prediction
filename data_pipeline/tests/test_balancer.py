"""
Unit tests for class balancing (SMOTE / random oversampling).
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest
import pandas as pd
import numpy as np

from src.preprocessing.balancer import balance_classes, get_class_weights


# ── Fixtures ─────────────────────────────────────────────────────────────────

@pytest.fixture
def imbalanced_data():
    """Imbalanced dataset: 90% class 0, 10% class 1."""
    rng = np.random.default_rng(42)
    n = 200
    X = pd.DataFrame({
        "feature_1": rng.normal(0, 1, n),
        "feature_2": rng.normal(0, 1, n),
        "feature_3": rng.uniform(0, 1, n),
        "feature_4": rng.integers(1, 5, n).astype(float),
    })
    y = pd.Series(
        [0] * 180 + [1] * 20,
        name="is_blackspot",
    )
    return X, y


# ── balance_classes tests ─────────────────────────────────────────────────────

class TestBalancer:

    def test_random_oversampling_balances_classes(self, imbalanced_data):
        X, y = imbalanced_data
        X_bal, y_bal = balance_classes(X, y, strategy="random")
        counts = y_bal.value_counts()
        # After balancing, both classes should be equal
        assert counts[0] == counts[1]

    def test_output_shape_consistent(self, imbalanced_data):
        X, y = imbalanced_data
        X_bal, y_bal = balance_classes(X, y, strategy="random")
        assert len(X_bal) == len(y_bal)
        assert X_bal.shape[1] == X.shape[1]

    def test_column_names_preserved(self, imbalanced_data):
        X, y = imbalanced_data
        X_bal, y_bal = balance_classes(X, y, strategy="random")
        assert list(X_bal.columns) == list(X.columns)

    def test_target_name_preserved(self, imbalanced_data):
        X, y = imbalanced_data
        X_bal, y_bal = balance_classes(X, y, strategy="random")
        assert y_bal.name == y.name

    def test_smote_balances_if_available(self, imbalanced_data):
        """Test SMOTE if imbalanced-learn is installed."""
        try:
            from imblearn.over_sampling import SMOTE
            X, y = imbalanced_data
            X_bal, y_bal = balance_classes(X, y, strategy="smote")
            counts = y_bal.value_counts()
            assert counts[0] == counts[1]
        except ImportError:
            pytest.skip("imbalanced-learn not installed")

    def test_smote_tomek_if_available(self, imbalanced_data):
        """Test SMOTETomek if imbalanced-learn is installed."""
        try:
            from imblearn.combine import SMOTETomek
            X, y = imbalanced_data
            X_bal, y_bal = balance_classes(X, y, strategy="smote_tomek")
            assert len(y_bal) > 0
            assert y_bal.nunique() == 2
        except ImportError:
            pytest.skip("imbalanced-learn not installed")

    def test_invalid_strategy_raises(self, imbalanced_data):
        X, y = imbalanced_data
        with pytest.raises(ValueError, match="Unknown strategy"):
            balance_classes(X, y, strategy="invalid_strategy")

    def test_already_balanced_data(self):
        """Balanced data should not change significantly."""
        rng = np.random.default_rng(42)
        n = 100
        X = pd.DataFrame({"f1": rng.normal(0, 1, n), "f2": rng.normal(0, 1, n)})
        y = pd.Series([0] * 50 + [1] * 50, name="is_blackspot")
        X_bal, y_bal = balance_classes(X, y, strategy="random")
        assert y_bal.value_counts()[0] == y_bal.value_counts()[1]


# ── get_class_weights tests ───────────────────────────────────────────────────

class TestClassWeights:

    def test_returns_dict_with_both_classes(self, imbalanced_data):
        _, y = imbalanced_data
        weights = get_class_weights(y)
        assert 0 in weights
        assert 1 in weights

    def test_minority_class_has_higher_weight(self, imbalanced_data):
        _, y = imbalanced_data
        weights = get_class_weights(y)
        # Class 1 (minority) should have higher weight
        assert weights[1] > weights[0]

    def test_weights_are_positive(self, imbalanced_data):
        _, y = imbalanced_data
        weights = get_class_weights(y)
        assert all(w > 0 for w in weights.values())
