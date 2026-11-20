"""
CLI entrypoint for model training.

Usage:
    python train.py --model all              # train all 4 models
    python train.py --model xgboost          # train single model
    python train.py --model xgboost --tune   # with Optuna tuning
    python train.py --model all --export     # train + export champion
    python train.py --model all --cv         # train + cross-validate
"""
import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from loguru import logger
from src.config import setup_logging, ensure_dirs, RANDOM_STATE
from src.data_loader import load_splits, get_val_split


def train_logistic_regression(X_train, y_train, tune: bool = False):
    from src.models.baseline import build_logistic_regression, LR_SEARCH_SPACE
    from src.training.trainer import ModelTrainer
    from src.training.tuner import tune_model

    params = {}
    if tune:
        logger.info("Tuning Logistic Regression with Optuna...")
        params = tune_model(build_logistic_regression, X_train, y_train,
                            LR_SEARCH_SPACE, n_trials=30)

    model = build_logistic_regression(**params)
    trainer = ModelTrainer("logistic_regression", model)
    return trainer.train(X_train, y_train)


def train_random_forest(X_train, y_train, tune: bool = False):
    from src.models.random_forest import build_random_forest, RF_SEARCH_SPACE
    from src.training.trainer import ModelTrainer
    from src.training.tuner import tune_model

    params = {}
    if tune:
        logger.info("Tuning Random Forest with Optuna...")
        params = tune_model(build_random_forest, X_train, y_train,
                            RF_SEARCH_SPACE, n_trials=30)

    model = build_random_forest(**params)
    trainer = ModelTrainer("random_forest", model)
    return trainer.train(X_train, y_train)


def train_xgboost(X_train, y_train, X_val, y_val, tune: bool = False):
    from src.models.xgboost_model import build_xgboost, get_scale_pos_weight, XGB_SEARCH_SPACE
    from src.training.trainer import ModelTrainer
    from src.training.tuner import tune_model

    spw = get_scale_pos_weight(y_train)
    params = {"scale_pos_weight": spw}

    if tune:
        logger.info("Tuning XGBoost with Optuna...")
        tuned = tune_model(
            lambda **p: build_xgboost(scale_pos_weight=spw, **p),
            X_train, y_train, XGB_SEARCH_SPACE, n_trials=40,
        )
        params.update(tuned)

    model = build_xgboost(**params)
    trainer = ModelTrainer("xgboost", model)
    return trainer.train(X_train, y_train, X_val, y_val)


def train_lightgbm(X_train, y_train, X_val, y_val, tune: bool = False):
    from src.models.lightgbm_model import build_lightgbm, LGBM_SEARCH_SPACE
    from src.training.trainer import ModelTrainer
    from src.training.tuner import tune_model

    params = {}
    if tune:
        logger.info("Tuning LightGBM with Optuna...")
        params = tune_model(build_lightgbm, X_train, y_train,
                            LGBM_SEARCH_SPACE, n_trials=40)

    model = build_lightgbm(**params)
    trainer = ModelTrainer("lightgbm", model)
    return trainer.train(X_train, y_train, X_val, y_val)


def run_cross_validation(models: dict, X_train, y_train):
    from src.training.cross_validator import cross_validate_model, cv_summary_table
    cv_results = {}
    for name, model in models.items():
        logger.info(f"Cross-validating {name}...")
        cv_results[name] = cross_validate_model(model, X_train, y_train)
    table = cv_summary_table(cv_results)
    print("\nCross-Validation Results:")
    print(table.to_string(index=False))
    return cv_results


def export_champion(models: dict, X_test, y_test, X_train):
    from src.evaluation.metrics import evaluate_model
    from src.evaluation.threshold_optimizer import optimize_all_thresholds
    from src.evaluation.comparator import compare_all_models
    from src.export.model_exporter import export_champion_model

    # Evaluate all models
    results = []
    thresholds = optimize_all_thresholds(models, X_test, y_test)
    for name, model in models.items():
        t = thresholds.get(name, 0.5)
        metrics = evaluate_model(model, X_test, y_test, threshold=t, model_name=name)
        results.append(metrics)

    _, champion_name = compare_all_models(results)
    champion_model   = models[champion_name]
    champion_metrics = next(r for r in results if r["model"] == champion_name)
    champion_thresh  = thresholds[champion_name]

    # SHAP top features
    shap_features = []
    try:
        from src.explainability.shap_explainer import BlackSpotExplainer
        model_type = "linear" if champion_name == "logistic_regression" else "tree"
        explainer = BlackSpotExplainer(champion_model, X_train, model_type,
                                       list(X_train.columns))
        explainer.compute_shap_values(X_test, sample_size=300)
        shap_features = explainer.get_top_features_json(top_n=10)
    except Exception as e:
        logger.warning(f"SHAP export failed: {e}")

    export_champion_model(
        model=champion_model,
        model_name=champion_name,
        metrics=champion_metrics,
        feature_names=list(X_train.columns),
        threshold=champion_thresh,
        shap_top_features=shap_features,
    )


def main():
    parser = argparse.ArgumentParser(
        description="Train Traffic Black Spot Prediction Models"
    )
    parser.add_argument("--model", default="all",
                        choices=["all", "logistic_regression", "random_forest",
                                 "xgboost", "lightgbm"])
    parser.add_argument("--tune",   action="store_true", help="Run Optuna tuning")
    parser.add_argument("--cv",     action="store_true", help="Run cross-validation")
    parser.add_argument("--export", action="store_true", help="Export champion model")
    args = parser.parse_args()

    setup_logging()
    ensure_dirs()

    logger.info(f"Loading data splits...")
    X_train, X_test, y_train, y_test = load_splits()
    X_tr, X_val, y_tr, y_val = get_val_split(X_train, y_train)

    trained_models = {}

    try:
        if args.model in ("all", "logistic_regression"):
            trained_models["logistic_regression"] = train_logistic_regression(
                X_train, y_train, tune=args.tune
            )

        if args.model in ("all", "random_forest"):
            trained_models["random_forest"] = train_random_forest(
                X_train, y_train, tune=args.tune
            )

        if args.model in ("all", "xgboost"):
            trained_models["xgboost"] = train_xgboost(
                X_tr, y_tr, X_val, y_val, tune=args.tune
            )

        if args.model in ("all", "lightgbm"):
            trained_models["lightgbm"] = train_lightgbm(
                X_tr, y_tr, X_val, y_val, tune=args.tune
            )

        if args.cv and trained_models:
            run_cross_validation(trained_models, X_train, y_train)

        if args.export and trained_models:
            export_champion(trained_models, X_test, y_test, X_train)

        logger.success(f"Training complete | models: {list(trained_models.keys())}")

    except Exception as e:
        logger.exception(f"Training failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
