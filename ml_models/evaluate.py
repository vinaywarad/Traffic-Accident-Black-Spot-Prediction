"""
CLI entrypoint for model evaluation and comparison.

Usage:
    python evaluate.py                        # evaluate all saved models
    python evaluate.py --model xgboost        # evaluate single model
    python evaluate.py --threshold-opt        # optimize thresholds
    python evaluate.py --plots                # generate all evaluation plots
"""
import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from loguru import logger
from src.config import setup_logging, ensure_dirs, REPORTS_DIR
from src.data_loader import load_splits


def main():
    parser = argparse.ArgumentParser(description="Evaluate Black Spot Prediction Models")
    parser.add_argument("--model", default="all",
                        choices=["all", "logistic_regression", "random_forest",
                                 "xgboost", "lightgbm"])
    parser.add_argument("--threshold-opt", action="store_true",
                        help="Optimize decision thresholds")
    parser.add_argument("--plots", action="store_true",
                        help="Generate all evaluation plots")
    args = parser.parse_args()

    setup_logging()
    ensure_dirs()

    from src.training.trainer import load_model
    from src.evaluation.metrics import evaluate_model, get_classification_report
    from src.evaluation.threshold_optimizer import optimize_all_thresholds
    from src.evaluation.comparator import compare_all_models, print_performance_targets
    from src.config import MODEL_NAMES, MODELS_DIR

    X_train, X_test, y_train, y_test = load_splits()

    # Load models
    model_names = [args.model] if args.model != "all" else MODEL_NAMES
    models = {}
    for name in model_names:
        try:
            models[name] = load_model(name)
        except FileNotFoundError:
            logger.warning(f"Model not found: {name} — skipping")

    if not models:
        logger.error("No models found. Run: python train.py --model all")
        sys.exit(1)

    # Optimize thresholds
    thresholds = {}
    if args.threshold_opt:
        thresholds = optimize_all_thresholds(models, X_test, y_test)
    else:
        thresholds = {name: 0.5 for name in models}

    # Evaluate all models
    results = []
    for name, model in models.items():
        t = thresholds.get(name, 0.5)
        metrics = evaluate_model(model, X_test, y_test, threshold=t, model_name=name)
        results.append(metrics)

        # Save classification report
        REPORTS_DIR.mkdir(parents=True, exist_ok=True)
        report = get_classification_report(model, X_test, y_test, threshold=t)
        report_path = REPORTS_DIR / f"classification_report_{name}.txt"
        report_path.write_text(f"Model: {name}\nThreshold: {t}\n\n{report}")
        logger.info(f"Saved classification report → {report_path}")

    # Compare all models
    if len(results) > 1:
        compare_all_models(results)
        print_performance_targets(results)

    # Generate plots
    if args.plots:
        from src.visualization.roc_curves import plot_roc_all_models
        from src.visualization.confusion_matrix import plot_all_confusion_matrices
        from src.visualization.calibration_plot import plot_calibration_curves

        plot_roc_all_models(models, X_test, y_test)
        plot_all_confusion_matrices(models, X_test, y_test, thresholds)
        plot_calibration_curves(models, X_test, y_test)
        logger.success("All evaluation plots saved")

    logger.success("Evaluation complete")


if __name__ == "__main__":
    main()
