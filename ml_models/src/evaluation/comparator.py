"""
Side-by-side comparison of all trained models.
Produces the model comparison table and selects the champion model.
"""
from pathlib import Path

import pandas as pd
from loguru import logger

try:
    import mlflow
    MLFLOW_AVAILABLE = True
except ImportError:
    MLFLOW_AVAILABLE = False

from src.config import REPORTS_DIR, MLFLOW_EXPERIMENT, MLFLOW_URI


def compare_all_models(results: list[dict]) -> tuple[pd.DataFrame, str]:
    """
    Compare all trained models and select the champion.

    Champion selection: highest AUC-ROC (threshold-independent metric).
    Tiebreaker: highest Recall (safety-critical — missing a black spot is worse).

    Args:
        results: List of metric dicts from evaluate_model().

    Returns:
        Tuple of (comparison DataFrame, champion model name).
    """
    df = pd.DataFrame(results).sort_values(
        ["auc_roc", "recall"], ascending=False
    ).reset_index(drop=True)

    display_cols = ["model", "auc_roc", "auc_pr", "f1",
                    "recall", "precision", "mcc", "brier_score"]
    display_cols = [c for c in display_cols if c in df.columns]

    print("\n" + "=" * 80)
    print("MODEL COMPARISON — Traffic Black Spot Prediction (Bengaluru)")
    print("=" * 80)
    print(df[display_cols].to_string(index=False))
    print("=" * 80)

    champion = df.iloc[0]["model"]
    print(f"\n🏆 CHAMPION MODEL: {champion.upper()}")
    print(f"   AUC-ROC : {df.iloc[0]['auc_roc']}")
    print(f"   Recall  : {df.iloc[0]['recall']}")
    print(f"   F1      : {df.iloc[0]['f1']}")
    print("=" * 80 + "\n")

    # Log to MLflow
    if MLFLOW_AVAILABLE:
        _log_comparison_to_mlflow(results)

    # Save CSV report
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    csv_path = REPORTS_DIR / "model_comparison.csv"
    df.to_csv(csv_path, index=False)
    logger.info(f"Saved model comparison → {csv_path}")

    return df, champion


def _log_comparison_to_mlflow(results: list[dict]) -> None:
    """Log all model metrics to a single MLflow comparison run."""
    try:
        mlflow.set_tracking_uri(MLFLOW_URI)
        mlflow.set_experiment(MLFLOW_EXPERIMENT)
        with mlflow.start_run(run_name="model_comparison"):
            for row in results:
                name = row.get("model", "unknown")
                mlflow.log_metrics({
                    f"{name}_auc_roc":  row.get("auc_roc",  0),
                    f"{name}_auc_pr":   row.get("auc_pr",   0),
                    f"{name}_recall":   row.get("recall",   0),
                    f"{name}_f1":       row.get("f1",       0),
                    f"{name}_mcc":      row.get("mcc",      0),
                })
    except Exception as e:
        logger.warning(f"MLflow comparison logging failed: {e}")


def print_performance_targets(results: list[dict]) -> None:
    """
    Check each model against the minimum performance targets.
    Logs a warning for any model that falls below targets.
    """
    TARGETS = {
        "logistic_regression": {"auc_roc": 0.72, "auc_pr": 0.35, "recall": 0.60, "f1": 0.45},
        "random_forest":       {"auc_roc": 0.82, "auc_pr": 0.50, "recall": 0.70, "f1": 0.58},
        "xgboost":             {"auc_roc": 0.85, "auc_pr": 0.55, "recall": 0.73, "f1": 0.62},
        "lightgbm":            {"auc_roc": 0.84, "auc_pr": 0.53, "recall": 0.72, "f1": 0.61},
    }

    print("\n📊 Performance vs Targets:")
    for row in results:
        name    = row.get("model", "")
        targets = TARGETS.get(name, {})
        passes  = []
        fails   = []
        for metric, target in targets.items():
            actual = row.get(metric, 0)
            if actual >= target:
                passes.append(f"{metric}={actual:.3f}✓")
            else:
                fails.append(f"{metric}={actual:.3f}<{target}")
        status = "✅ PASS" if not fails else "⚠️  BELOW TARGET"
        print(f"  {name:<25} {status}")
        if fails:
            print(f"    Below target: {', '.join(fails)}")
