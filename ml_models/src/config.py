"""
Central configuration for the ML model training pipeline.
Loads config.yaml, sets up paths, logging, and MLflow tracking.
"""
import sys
import yaml
from pathlib import Path
from loguru import logger

ROOT_DIR = Path(__file__).resolve().parent.parent

CONFIG_PATH = ROOT_DIR / "config.yaml"


def load_config() -> dict:
    with open(CONFIG_PATH) as f:
        return yaml.safe_load(f)


CFG = load_config()

# ── Paths ────────────────────────────────────────────────────────────────────
DATA_DIR      = ROOT_DIR / CFG["paths"]["data_dir"]
MODELS_DIR    = ROOT_DIR / CFG["paths"]["models_dir"]
BEST_MODEL    = ROOT_DIR / CFG["paths"]["best_model"]
METADATA_PATH = ROOT_DIR / CFG["paths"]["metadata"]
PLOTS_DIR     = ROOT_DIR / CFG["paths"]["plots_dir"]
REPORTS_DIR   = ROOT_DIR / CFG["paths"]["reports_dir"]
LOGS_DIR      = ROOT_DIR / CFG["paths"]["logs_dir"]
MLRUNS_DIR    = ROOT_DIR / CFG["paths"]["mlruns_dir"]

# ── Data file paths ──────────────────────────────────────────────────────────
X_TRAIN_PATH = DATA_DIR / "X_train.parquet"
X_TEST_PATH  = DATA_DIR / "X_test.parquet"
Y_TRAIN_PATH = DATA_DIR / "y_train.parquet"
Y_TEST_PATH  = DATA_DIR / "y_test.parquet"

# ── Training constants ───────────────────────────────────────────────────────
RANDOM_STATE          = CFG["training"]["random_state"]
CV_FOLDS              = CFG["training"]["cv_folds"]
CV_GAP_DAYS           = CFG["training"]["cv_gap_days"]
EARLY_STOPPING_ROUNDS = CFG["training"]["early_stopping_rounds"]
VAL_MONTHS            = CFG["training"]["val_months"]

# ── Tuning constants ─────────────────────────────────────────────────────────
N_TRIALS      = CFG["tuning"]["n_trials"]
TUNE_METRIC   = CFG["tuning"]["metric"]
TUNE_TIMEOUT  = CFG["tuning"]["timeout_secs"]

# ── Threshold optimization ───────────────────────────────────────────────────
THRESHOLD_METRIC  = CFG["threshold"]["optimize_metric"]
MIN_PRECISION     = CFG["threshold"]["min_precision"]

# ── MLflow ───────────────────────────────────────────────────────────────────
MLFLOW_EXPERIMENT = CFG["mlflow"]["experiment_name"]
MLFLOW_URI        = str(ROOT_DIR / CFG["mlflow"]["tracking_uri"])

# ── Model names ──────────────────────────────────────────────────────────────
MODEL_NAMES = ["logistic_regression", "random_forest", "xgboost", "lightgbm"]

# ── Risk level thresholds ────────────────────────────────────────────────────
RISK_THRESHOLDS = {
    "CRITICAL": 0.75,
    "HIGH":     0.55,
    "MEDIUM":   0.35,
    "LOW":      0.0,
}


def ensure_dirs() -> None:
    """Create all output directories."""
    for d in [DATA_DIR, MODELS_DIR, PLOTS_DIR, REPORTS_DIR, LOGS_DIR, MLRUNS_DIR]:
        d.mkdir(parents=True, exist_ok=True)
    # Ensure best_model parent exists
    BEST_MODEL.parent.mkdir(parents=True, exist_ok=True)


def setup_logging(log_file: str = None) -> None:
    """Configure loguru with file + console sinks."""
    LOGS_DIR.mkdir(parents=True, exist_ok=True)
    path = log_file or str(LOGS_DIR / "training.log")
    logger.remove()
    logger.add(sys.stderr, level="INFO",
               format="<green>{time:HH:mm:ss}</green> | <level>{level:<8}</level> | {message}")
    logger.add(path, rotation="10 MB", retention="30 days",
               format="{time:YYYY-MM-DD HH:mm:ss} | {level:<8} | {name}:{line} — {message}")
