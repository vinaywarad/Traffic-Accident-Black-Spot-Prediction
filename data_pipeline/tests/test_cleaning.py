"""
Unit tests for the cleaning pipeline modules.
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest
import pandas as pd
import numpy as np

from src.cleaning.accident_cleaner import clean_accidents, SEVERITY_MAP
from src.cleaning.coordinate_validator import validate_coordinates
from src.cleaning.date_normalizer import normalize_dates


# ── Fixtures ─────────────────────────────────────────────────────────────────

@pytest.fixture
def sample_df():
    """Minimal valid accident DataFrame."""
    return pd.DataFrame({
        "accident_id":       ["BLR-001", "BLR-002", "BLR-003"],
        "date":              ["2022-06-15", "2022-07-20", "2023-01-10"],
        "time":              ["08:30", "17:45", "22:10"],
        "latitude":          [12.9170, 13.0067, 12.8353],
        "longitude":         [77.6228, 77.6963, 77.6772],
        "severity":          ["HIGH", "CRITICAL", "LOW"],
        "road_type":         ["ORR", "NH", "City_Road"],
        "weather":           ["Clear", "Rainy", "Foggy"],
        "road_condition":    ["Dry", "Wet", "Dry"],
        "light_condition":   ["Daylight", "Dark", "Daylight"],
        "vehicles_involved": [2, 3, 1],
        "casualties":        [1, 4, 0],
        "fatalities":        [0, 2, 0],
    })


@pytest.fixture
def dirty_df():
    """DataFrame with various data quality issues."""
    return pd.DataFrame({
        "accident_id":       ["BLR-001", "BLR-001", "BLR-003", "BLR-004"],  # duplicate
        "date":              ["2022-06-15", "2022-06-15", "not-a-date", "2023-03-01"],
        "time":              ["08:30", "08:30", "17:00", "09:00"],
        "latitude":          [12.9170, 12.9170, 99.0, 12.8353],   # 99.0 out of bounds
        "longitude":         [77.6228, 77.6228, 77.6963, 77.6772],
        "severity":          ["HIGH", "HIGH", "fatal", "minor"],   # needs normalization
        "road_type":         ["ORR", "ORR", "NH", "City_Road"],
        "weather":           ["Clear", "Clear", None, "Rainy"],    # null weather
        "road_condition":    ["Dry", "Dry", "Wet", "Dry"],
        "light_condition":   ["Daylight", "Daylight", "Dark", "Daylight"],
        "vehicles_involved": [2, 2, 3, 1],
        "casualties":        [1, 1, 4, 0],
        "fatalities":        [0, 0, 2, 0],
    })


# ── accident_cleaner tests ────────────────────────────────────────────────────

class TestAccidentCleaner:

    def test_clean_valid_df_unchanged_count(self, sample_df):
        cleaned = clean_accidents(sample_df)
        assert len(cleaned) == len(sample_df)

    def test_removes_duplicates(self, dirty_df):
        cleaned = clean_accidents(dirty_df)
        assert cleaned.duplicated().sum() == 0

    def test_removes_out_of_bounds_coordinates(self, dirty_df):
        cleaned = clean_accidents(dirty_df)
        assert (cleaned["latitude"] > 13.18).sum() == 0
        assert (cleaned["latitude"] < 12.75).sum() == 0

    def test_normalizes_severity_labels(self, dirty_df):
        cleaned = clean_accidents(dirty_df)
        valid = {"LOW", "MEDIUM", "HIGH", "CRITICAL"}
        assert set(cleaned["severity"].unique()).issubset(valid)

    def test_fills_missing_weather(self, dirty_df):
        cleaned = clean_accidents(dirty_df)
        if "weather" in cleaned.columns:
            assert cleaned["weather"].isna().sum() == 0

    def test_drops_invalid_dates(self, dirty_df):
        cleaned = clean_accidents(dirty_df)
        assert cleaned["date"].isna().sum() == 0

    def test_output_has_required_columns(self, sample_df):
        cleaned = clean_accidents(sample_df)
        for col in ["latitude", "longitude", "severity"]:
            assert col in cleaned.columns

    def test_severity_map_coverage(self):
        """All severity map values should be valid severities."""
        valid = {"LOW", "MEDIUM", "HIGH", "CRITICAL"}
        assert set(SEVERITY_MAP.values()).issubset(valid)


# ── coordinate_validator tests ────────────────────────────────────────────────

class TestCoordinateValidator:

    def test_valid_coordinates_unchanged(self, sample_df):
        validated = validate_coordinates(sample_df)
        assert len(validated) == len(sample_df)

    def test_out_of_bounds_dropped(self):
        df = pd.DataFrame({
            "latitude":  [12.9170, 99.0, 12.8353],
            "longitude": [77.6228, 77.6963, 77.6772],
        })
        validated = validate_coordinates(df)
        assert len(validated) == 2

    def test_swapped_coordinates_fixed(self):
        """Lat/lng that are swapped should be corrected."""
        df = pd.DataFrame({
            "latitude":  [77.6228],   # actually a longitude value
            "longitude": [12.9170],   # actually a latitude value
        })
        validated = validate_coordinates(df)
        # After fix, lat should be ~12.9 and lng ~77.6
        assert validated["latitude"].iloc[0] < 14
        assert validated["longitude"].iloc[0] > 77

    def test_dist_from_center_added(self, sample_df):
        validated = validate_coordinates(sample_df)
        assert "dist_from_center_km" in validated.columns
        assert (validated["dist_from_center_km"] >= 0).all()


# ── date_normalizer tests ─────────────────────────────────────────────────────

class TestDateNormalizer:

    def test_extracts_year_month_hour(self, sample_df):
        normalized = normalize_dates(sample_df)
        assert "year" in normalized.columns
        assert "month" in normalized.columns
        assert "hour" in normalized.columns

    def test_year_values_correct(self, sample_df):
        normalized = normalize_dates(sample_df)
        assert set(normalized["year"].unique()).issubset({2022, 2023})

    def test_hour_values_in_range(self, sample_df):
        normalized = normalize_dates(sample_df)
        assert normalized["hour"].between(0, 23).all()

    def test_day_of_week_added(self, sample_df):
        normalized = normalize_dates(sample_df)
        assert "day_of_week" in normalized.columns
        valid_days = {"Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"}
        assert set(normalized["day_of_week"].unique()).issubset(valid_days)

    def test_handles_missing_time_column(self, sample_df):
        df_no_time = sample_df.drop(columns=["time"])
        normalized = normalize_dates(df_no_time)
        assert "hour" in normalized.columns
