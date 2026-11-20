"""
CLI entrypoint for SHAP explainability analysis.

Usage:
    python explain.py                         # SHAP for champion model
    python explain.py --model random_forest   # SHAP for specific model
    python explain.py --all-models            # SHAP for all models
    python explain.py --single-prediction     # explain one sample prediction
"""
import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from loguru import logger
from src.config import setup_logging, ensure_dirs, PLOTS_DIR


def main():
    parser = argparse.ArgumentParser(description="SHAP Explainability for Black Spot Models")
    parser.add_argument("--model", default="best",
                        help="Model name or 'best' for champion model")
    parser.add_argument("--all-models",       action="store_true")
    parser.add_argument("--single-prediction", action="store_true",
                        help="Explain a single sample prediction")
    parser.add_argument("--top-n", type=int, default=20,
                        help="Number of top features to show")
    args = parser.parse_args()

    setup_logging()
    ensure_dirs()

    from src.data_loader import load_splits
    from src.training.trainer import load_model
    from src.export.model_exporter import load_champion_model
    from src.explainability.shap_explainer import BlackSpotExplainer
    from src.explainability.feature_importance import (
        get_builtin_importance, get_permutation_importance, plot_importance_comparison
    )
    from src.config import MODEL_NAMES, MODELS_DIR

    X_train, X_test, y_train, y_test = load_splits()

    # Determine which models to explain
    if args.all_models:
        model_names = MODEL_NAMES
    elif args.model == "best":
        model_names = ["best"]
    else:
        model_names = [args.model]

    for name in model_names:
        logger.info(f"Generating SHAP explanations for: {name}")
        try:
            if name == "best":
                model = load_champion_model()
                model_type = "tree"   # assume tree-based champion
                display_name = "champion"
            else:
                model = load_model(name)
                model_type = "linear" if name == "logistic_regression" else "tree"
                display_name = name
        except FileNotFoundError as e:
            logger.warning(f"Skipping {name}: {e}")
            continue

        feature_names = list(X_train.columns)

        # SHAP explainer
        try:
            explainer = BlackSpotExplainer(model, X_train, model_type, feature_names)
            explainer.compute_shap_values(X_test, sample_size=500)

            # Global importance bar chart
            explainer.plot_feature_importance(
                top_n=args.top_n,
                save_path=PLOTS_DIR / f"shap_importance_{display_name}.png",
            )

            # Beeswarm plot
            explainer.plot_beeswarm(
                top_n=args.top_n,
                save_path=PLOTS_DIR / f"shap_beeswarm_{display_name}.png",
            )

            # Single prediction waterfall
            if args.single_prediction:
                sample = X_test.sample(1, random_state=42)
                explainer.explain_single_prediction(
                    sample,
                    save_path=PLOTS_DIR / f"shap_waterfall_{display_name}.png",
                )

            # Export top features JSON
            top_features = explainer.get_top_features_json(top_n=10)
            import json
            json_path = PLOTS_DIR / f"shap_top_features_{display_name}.json"
            json_path.write_text(json.dumps(top_features, indent=2))
            logger.info(f"Saved top features JSON → {json_path}")

        except Exception as e:
            logger.warning(f"SHAP failed for {name}: {e}")

        # Built-in + permutation importance
        try:
            builtin_df = get_builtin_importance(model, feature_names)
            perm_df    = get_permutation_importance(model, X_test, y_test, n_repeats=5)
            plot_importance_comparison(
                builtin_df, perm_df, model_name=display_name,
                save_path=PLOTS_DIR / f"feature_importance_{display_name}.png",
            )
        except Exception as e:
            logger.warning(f"Importance comparison failed for {name}: {e}")

    logger.success("SHAP analysis complete")


if __name__ == "__main__":
    main()
