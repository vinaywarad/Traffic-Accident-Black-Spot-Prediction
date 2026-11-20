"""
Unit tests for feature engineering modules.
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest
import pandas as pd
import numpy as np

from src.features.temporal_features import add_temporal_features
from src.features.environmental_features import add_environmental_features
from src.features.road_features import add_road_features
from src.features.spatial_features import add_spatial_features


# ── Fixtures ─────────────────────────────────────────────────────────────────

@pytest.fixture
def base_df():
    """Base accident DataFrame for feature tests."""
    return pd.DataFrame({
        "accident_id":    [f"BLR-{i:04d}" for i in range(20)],
        "date":           pd.date_range("2022-01-01", periods=20, freq="15D").strftime("%Y-%m-%d"),
        "hour":           [8, 17, 22, 3, 9, 18, 12, 6, 20, 1,
                           8, 17, 22, 3, 9, 18, 12, 6, 20, 1],
        "latitude":       np.random.uniform(12.85, 13.05, 20),
        "longitude":      np.random.uniform(77.50, 77.70, 20),
        "road_type":      ["NH", "ORR", "City_Road", "Residential", "SH"] * 4,
        "weather":        ["Clear", "Rainy", "Foggy", "Overcast", "Night-Rainy"] * 4,
        "road_condition": ["Dry", "Wet", "Dry", "Potholed", "Slippery"] * 4,
        "light_condition":["Daylight", "Dark", "Daylight", "Dark", "Daylight"] * 4,
        "speed_limit":    [80, 80, 40, 30, 60] * 4,
        "vehicles_involved": np.random.randint(1, 4, 20),
        "casualties":     np.random.randint(0, 3, 20),
        "fatalities":     [0] * 20,
    })


# ── temporal_features tests ───────────────────────────────────────────────────

class TestTemporalFeatures:

    def test_adds_cyclic_hour_features(self, base_df):
        df = add_temporal_features(base_df)
        assert "hour_sin" in df.columns
        assert "hour_cos" in df.columns

    def test_cyclic_values_in_range(self, base_df):
        df = add_temporal_features(base_df)
        assert df["hour_sin"].between(-1, 1).all()
        assert df["hour_cos"].between(-1, 1).all()
        assert df["month_sin"].between(-1, 1).all()

    def test_peak_hour_flag_correct(self, base_df):
        df = add_temporal_features(base_df)
        # Hours 8, 9, 17, 18 should be peak
        peak_hours = df[df["hour"].isin([8, 9, 17, 18])]
        assert (peak_hours["is_peak_hour"] == 1).all()

    def test_night_flag_correct(self, base_df):
        df = add_temporal_features(base_df)
        night_hours = df[df["hour"].isin([22, 23, 0, 1, 2, 3, 4])]
        assert (night_hours["is_night"] == 1).all()

    def test_monsoon_flag_correct(self, base_df):
        df = add_temporal_features(base_df)
        assert "is_monsoon" in df.columns
        # Monsoon months are 6,7,8,9
        monsoon_rows = df[df["month"].isin([6, 7, 8, 9])]
        if len(monsoon_rows) > 0:
            assert (monsoon_rows["is_monsoon"] == 1).all()

    def test_days_since_epoch_positive(self, base_df):
        df = add_temporal_features(base_df)
        assert "days_since_epoch" in df.columns
        assert (df["days_since_epoch"] >= 0).all()

    def test_season_values_valid(self, base_df):
        df = add_temporal_features(base_df)
        valid_seasons = {"Summer", "Monsoon", "Post-Monsoon", "Winter"}
        assert set(df["season"].unique()).issubset(valid_seasons)


# ── environmental_features tests ─────────────────────────────────────────────

class TestEnvironmentalFeatures:

    def test_weather_encoded_in_range(self, base_df):
        df = add_environmental_features(base_df)
        assert df["weather_encoded"].between(1, 5).all()

    def test_road_condition_encoded_in_range(self, base_df):
        df = add_environmental_features(base_df)
        assert df["road_condition_encoded"].between(1, 5).all()

    def test_adverse_weather_flag(self, base_df):
        df = add_environmental_features(base_df)
        rainy_rows = df[df["weather"].isin(["Rainy", "Foggy", "Night-Rainy"])]
        assert (rainy_rows["is_adverse_weather"] == 1).all()

    def test_wet_road_flag(self, base_df):
        df = add_environmental_features(base_df)
        wet_rows = df[df["road_condition"].isin(["Wet", "Slippery"])]
        assert (wet_rows["is_wet_road"] == 1).all()

    def test_env_risk_score_positive(self, base_df):
        df = add_environmental_features(base_df)
        assert "env_risk_score" in df.columns
        assert (df["env_risk_score"] > 0).all()

    def test_handles_missing_weather_column(self):
        df = pd.DataFrame({"latitude": [12.9], "longitude": [77.6]})
        result = add_environmental_features(df)
        assert "weather_encoded" in result.columns
        assert result["weather_encoded"].iloc[0] == 1


# ── road_features tests ───────────────────────────────────────────────────────

class TestRoadFeatures:

    def test_speed_limit_added(self, base_df):
        df = add_road_features(base_df)
        assert "speed_limit" in df.columns
        assert (df["speed_limit"] > 0).all()

    def test_highway_flags_binary(self, base_df):
        df = add_road_features(base_df)
        assert df["is_highway"].isin([0, 1]).all()
        assert df["is_national_highway"].isin([0, 1]).all()

    def test_nh_is_highway(self, base_df):
        df = add_road_features(base_df)
        nh_rows = df[df["road_type"] == "NH"]
        assert (nh_rows["is_highway"] == 1).all()

    def test_num_lanes_positive(self, base_df):
        df = add_road_features(base_df)
        assert "num_lanes_estimated" in df.columns
        assert (df["num_lanes_estimated"] >= 1).all()


# ── spatial_features tests ────────────────────────────────────────────────────

class TestSpatialFeatures:

    def test_nearest_blackspot_dist_positive(self, base_df):
        df = add_spatial_features(base_df)
        assert "nearest_blackspot_dist" in df.columns
        assert (df["nearest_blackspot_dist"] >= 0).all()

    def test_road_risk_score_in_range(self, base_df):
        df = add_spatial_features(base_df)
        assert "road_risk_score" in df.columns
        assert df["road_risk_score"].between(1, 5).all()

    def test_accident_density_non_negative(self, base_df):
        df = add_spatial_features(base_df)
        assert "accident_density_1km" in df.columns
        assert (df["accident_density_1km"] >= 0).all()
        assert "accident_density_500m" in df.columns
        assert (df["accident_density_500m"] >= 0).all()

    def test_junction_features_added(self, base_df):
        df = add_spatial_features(base_df)
        assert "dist_to_nearest_junction" in df.columns
        assert "num_junctions_500m" in df.columns
