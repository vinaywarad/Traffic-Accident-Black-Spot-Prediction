"""
Central configuration module.
Loads config.yaml and .env, exposes all path constants and pipeline settings.
"""
import os
import yaml
from pathlib import Path
from dotenv import load_dotenv
from loguru import logger

# ── Paths ──────────────────────────────────────────────────────────────────
ROOT_DIR = Path(__file__).resolve().parent.parent
load_dotenv(ROOT_DIR / ".env")

CONFIG_PATH = ROOT_DIR / "config.yaml"

def load_config() -> dict:
    """Load and return the full config.yaml as a dict."""
    with open(CONFIG_PATH, "r") as f:
        return yaml.safe_load(f)

CFG = load_config()

# ── Directory paths ─────────────────────────────────────────────────────────
RAW_DIR        = ROOT_DIR / CFG["pipeline"]["raw_data_dir"]
INTERIM_DIR    = ROOT_DIR / CFG["pipeline"]["interim_dir"]
PROCESSED_DIR  = ROOT_DIR / CFG["pipeline"]["processed_dir"]
OUTPUTS_DIR    = ROOT_DIR / CFG["pipeline"]["output_dir"]

RAW_ACCIDENTS_DIR    = RAW_DIR / "accidents"
RAW_ROAD_DIR         = RAW_DIR / "road_network"
RAW_WEATHER_DIR      = RAW_DIR / "weather"
RAW_ADMIN_DIR        = RAW_DIR / "administrative"
EXTERNAL_DIR         = ROOT_DIR / "data" / "external"

EDA_REPORT_DIR = OUTPUTS_DIR / "eda_report"
MAPS_DIR       = OUTPUTS_DIR / "maps"
LOGS_DIR       = OUTPUTS_DIR / "logs"

# ── Bengaluru bounds ─────────────────────────────────────────────────────────
BENGALURU_BOUNDS = {
    "lat": (CFG["bengaluru"]["lat_min"], CFG["bengaluru"]["lat_max"]),
    "lng": (CFG["bengaluru"]["lng_min"], CFG["bengaluru"]["lng_max"]),
}
BENGALURU_BBOX = {
    "north": CFG["bengaluru"]["lat_max"],
    "south": CFG["bengaluru"]["lat_min"],
    "east":  CFG["bengaluru"]["lng_max"],
    "west":  CFG["bengaluru"]["lng_min"],
}
BENGALURU_CENTER = (CFG["bengaluru"]["center_lat"], CFG["bengaluru"]["center_lng"])
UTM_CRS = CFG["bengaluru"]["utm_crs"]

# ── Black spot parameters ────────────────────────────────────────────────────
BLACKSPOT_RADIUS_M  = CFG["blackspot"]["radius_m"]
BLACKSPOT_THRESHOLD = CFG["blackspot"]["threshold"]
WINDOW_MONTHS       = CFG["blackspot"]["window_months"]

# ── Known Bengaluru black spots (ground-truth seed data) ────────────────────
KNOWN_BLACKSPOTS = [
    {"name": "Silk Board Junction",       "lat": 12.9170, "lng": 77.6228, "severity": "CRITICAL"},
    {"name": "Marathahalli Bridge",        "lat": 12.9591, "lng": 77.6974, "severity": "CRITICAL"},
    {"name": "Hebbal Flyover",             "lat": 13.0450, "lng": 77.5970, "severity": "HIGH"},
    {"name": "KR Puram Bridge",            "lat": 13.0067, "lng": 77.6963, "severity": "HIGH"},
    {"name": "Tin Factory Junction",       "lat": 12.9980, "lng": 77.6590, "severity": "HIGH"},
    {"name": "Madiwala Junction",          "lat": 12.9228, "lng": 77.6200, "severity": "HIGH"},
    {"name": "Nagawara Junction",          "lat": 13.0450, "lng": 77.6227, "severity": "MEDIUM"},
    {"name": "Bannerghatta Road ORR",      "lat": 12.8991, "lng": 77.5982, "severity": "MEDIUM"},
    {"name": "Tumkur Road NH4",            "lat": 13.0290, "lng": 77.5160, "severity": "HIGH"},
    {"name": "Hosur Road Electronic City", "lat": 12.8353, "lng": 77.6772, "severity": "HIGH"},
    {"name": "Bellary Road Hebbal",        "lat": 13.0358, "lng": 77.5970, "severity": "MEDIUM"},
    {"name": "Old Madras Road KR Puram",   "lat": 13.0024, "lng": 77.6740, "severity": "HIGH"},
    {"name": "Outer Ring Road Bellandur",  "lat": 12.9307, "lng": 77.6784, "severity": "CRITICAL"},
    {"name": "Mysore Road Kengeri",        "lat": 12.9087, "lng": 77.4824, "severity": "MEDIUM"},
    {"name": "Sarjapur Road Junction",     "lat": 12.9102, "lng": 77.6860, "severity": "HIGH"},
]

# ── ML / preprocessing settings ─────────────────────────────────────────────
BALANCE_STRATEGY = CFG["balancing"]["strategy"]
RANDOM_STATE     = CFG["balancing"]["random_state"]
TEST_YEAR        = CFG["split"]["test_year"]

# ── Feature columns ──────────────────────────────────────────────────────────
FEATURE_COLUMNS = [
    "dist_to_nearest_junction",
    "num_junctions_500m",
    "road_risk_score",
    "accident_density_1km",
    "accident_density_500m",
    "nearest_blackspot_dist",
    "hour_sin", "hour_cos",
    "month_sin", "month_cos",
    "day_sin", "day_cos",
    "is_peak_hour",
    "is_night",
    "is_weekend",
    "is_monsoon",
    "is_festival_month",
    "days_since_epoch",
    "speed_limit",
    "vehicles_involved",
    "weather_encoded",
    "road_condition_encoded",
    "light_condition_encoded",
]
TARGET_COLUMN = "is_blackspot"

# ── Logging setup ────────────────────────────────────────────────────────────
def setup_logging(log_file: str = None):
    """Configure loguru with file + console sinks."""
    LOGS_DIR.mkdir(parents=True, exist_ok=True)
    log_path = log_file or str(LOGS_DIR / "pipeline.log")
    logger.add(log_path, rotation="10 MB", retention="30 days",
               format="{time:YYYY-MM-DD HH:mm:ss} | {level:<8} | {name}:{line} — {message}")
    return logger

def ensure_dirs():
    """Create all output directories if they don't exist."""
    for d in [RAW_ACCIDENTS_DIR, RAW_ROAD_DIR, RAW_WEATHER_DIR, RAW_ADMIN_DIR,
              EXTERNAL_DIR, INTERIM_DIR, PROCESSED_DIR,
              EDA_REPORT_DIR, MAPS_DIR, LOGS_DIR]:
        d.mkdir(parents=True, exist_ok=True)
