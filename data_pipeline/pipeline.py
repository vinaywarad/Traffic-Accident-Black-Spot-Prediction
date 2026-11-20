"""
Main CLI entrypoint — runs the full Traffic Accident Black Spot data pipeline.

Usage:
    python pipeline.py --stage all
    python pipeline.py --stage collect
    python pipeline.py --stage clean
    python pipeline.py --stage features
    python pipeline.py --stage preprocess
"""
import argparse
import sys
from pathlib import Path

from loguru import logger

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.config import setup_logging, ensure_dirs, PROCESSED_DIR, INTERIM_DIR
from src.config import FEATURE_COLUMNS, TARGET_COLUMN


def run_collect() -> None:
    """Stage 1: Data collection and ingestion."""
    logger.info("=== STAGE 1: DATA COLLECTION ===")

    from src.collection.synthetic_generator import generate_accident_records
    from src.collection.weather_loader import load_weather_data
    from src.storage.parquet_store import save_interim

    # Generate synthetic accident data (5000 records, 2019–2023)
    df = generate_accident_records(n=5000, start_year=2019, end_year=2023)
    save_interim(df, "accidents_raw")
    logger.success(f"Generated {len(df)} synthetic accident records")

    # Load/generate weather data
    weather = load_weather_data()
    if weather is not None:
        save_interim(weather, "weather_raw")
        logger.success(f"Loaded {len(weather)} weather records")


def run_clean() -> None:
    """Stage 2: Cleaning and EDA."""
    logger.info("=== STAGE 2: CLEANING + EDA ===")

    from src.storage.parquet_store import load_interim, save_interim
    from src.cleaning.accident_cleaner import clean_accidents, get_cleaning_report
    from src.cleaning.coordinate_validator import validate_coordinates
    from src.cleaning.date_normalizer import normalize_dates
    from src.collection.weather_loader import load_weather_data, merge_weather_with_accidents
    from src.validation.data_quality import check_accident_quality, print_quality_report
    from src.visualization.eda_plots import run_all_eda_plots

    # Load raw data
    df = load_interim("accidents_raw")
    original = df.copy()

    # Clean pipeline
    df = normalize_dates(df)
    df = validate_coordinates(df)
    df = clean_accidents(df)

    # Merge weather
    weather = load_weather_data()
    if weather is not None:
        df = merge_weather_with_accidents(df, weather)

    # Quality report
    report = check_accident_quality(df)
    print_quality_report(report)

    # Save cleaned data
    save_interim(df, "accidents_cleaned")
    logger.success(f"Cleaned dataset: {len(df)} records saved")

    # EDA plots
    run_all_eda_plots(df)


def run_features() -> None:
    """Stage 3: Feature engineering."""
    logger.info("=== STAGE 3: FEATURE ENGINEERING ===")

    from src.storage.parquet_store import load_interim
    from src.features.feature_pipeline import build_feature_matrix, save_feature_matrix

    df = load_interim("accidents_cleaned")
    df = build_feature_matrix(df, label_method="fast")
    save_feature_matrix(df, "features_final")
    logger.success(f"Feature matrix: {df.shape}")


def run_preprocess() -> None:
    """Stage 4: Preprocessing and export."""
    logger.info("=== STAGE 4: PREPROCESSING + EXPORT ===")

    from src.storage.parquet_store import load_processed
    from src.features.feature_pipeline import get_feature_matrix
    from src.preprocessing.encoder import encode_categoricals
    from src.preprocessing.splitter import temporal_split, save_splits
    from src.preprocessing.scaler import scale_features, save_scaler
    from src.preprocessing.balancer import balance_classes
    from src.storage.database import save_to_db
    from src.config import BALANCE_STRATEGY

    df = load_processed("features_final")

    # Encode categoricals
    df, encoders = encode_categoricals(df)

    # Temporal split
    train_df, test_df = temporal_split(df)

    # Extract X, y
    X_train, y_train = get_feature_matrix(train_df)
    X_test,  y_test  = get_feature_matrix(test_df)

    # Scale features
    X_train_scaled, X_test_scaled, scaler = scale_features(X_train, X_test)
    if scaler:
        save_scaler(scaler)

    # Balance training set (SMOTE)
    X_train_bal, y_train_bal = balance_classes(X_train_scaled, y_train, BALANCE_STRATEGY)

    # Save splits
    save_splits(X_train_bal, X_test_scaled, y_train_bal, y_test)

    # Save to SQLite feature store
    save_to_db(df, "features_final")

    logger.success(
        f"Preprocessing complete | "
        f"X_train: {X_train_bal.shape} | X_test: {X_test_scaled.shape}"
    )


def run_pipeline(stage: str = "all") -> None:
    """
    Run the specified pipeline stage(s).

    Args:
        stage: One of 'all', 'collect', 'clean', 'features', 'preprocess'.
    """
    setup_logging()
    ensure_dirs()

    logger.info(f"Starting pipeline — stage: {stage}")

    try:
        if stage in ("all", "collect"):
            run_collect()
        if stage in ("all", "clean"):
            run_clean()
        if stage in ("all", "features"):
            run_features()
        if stage in ("all", "preprocess"):
            run_preprocess()

        logger.success(f"Pipeline stage '{stage}' completed successfully")

    except Exception as e:
        logger.exception(f"Pipeline failed at stage '{stage}': {e}")
        sys.exit(1)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Traffic Accident Black Spot Prediction — Data Pipeline"
    )
    parser.add_argument(
        "--stage",
        default="all",
        choices=["all", "collect", "clean", "features", "preprocess"],
        help="Pipeline stage to run (default: all)",
    )
    args = parser.parse_args()
    run_pipeline(args.stage)
