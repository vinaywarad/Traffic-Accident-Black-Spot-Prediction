"""
Unit tests for data validation schemas and quality checks.
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest
import pandas as pd
from datetime import date

from src.validation.schemas import AccidentRecord, FeatureRecord, BlackSpotRecord
from src.validation.data_quality import check_accident_quality


# ── AccidentRecord schema tests ───────────────────────────────────────────────

class TestAccidentRecordSchema:

    def test_valid_record_passes(self):
        record = AccidentRecord(
            accident_id="BLR-001",
            date=date(2022, 6, 15),
            latitude=12.9170,
            longitude=77.6228,
            severity="HIGH",
            road_type="ORR",
            weather="Clear",
            vehicles_involved=2,
            casualties=1,
            fatalities=0,
        )
        assert record.severity == "HIGH"

    def test_invalid_severity_raises(self):
        from pydantic import ValidationError
        with pytest.raises(ValidationError):
            AccidentRecord(
                accident_id="BLR-002",
                date=date(2022, 6, 15),
                latitude=12.9170,
                longitude=77.6228,
                severity="EXTREME",   # invalid
                road_type="NH",
                weather="Clear",
                vehicles_involved=1,
                casualties=0,
                fatalities=0,
            )

    def test_latitude_out_of_bounds_raises(self):
        from pydantic import ValidationError
        with pytest.raises(ValidationError):
            AccidentRecord(
                accident_id="BLR-003",
                date=date(2022, 6, 15),
                latitude=99.0,         # out of Bengaluru bounds
                longitude=77.6228,
                severity="LOW",
                road_type="City_Road",
                weather="Clear",
                vehicles_involved=1,
                casualties=0,
                fatalities=0,
            )

    def test_fatalities_exceed_casualties_raises(self):
        from pydantic import ValidationError
        with pytest.raises(ValidationError):
            AccidentRecord(
                accident_id="BLR-004",
                date=date(2022, 6, 15),
                latitude=12.9170,
                longitude=77.6228,
                severity="CRITICAL",
                road_type="NH",
                weather="Rainy",
                vehicles_involved=3,
                casualties=1,
                fatalities=3,   # fatalities > casualties — invalid
            )

    def test_optional_is_blackspot(self):
        record = AccidentRecord(
            accident_id="BLR-005",
            date=date(2022, 6, 15),
            latitude=12.9170,
            longitude=77.6228,
            severity="MEDIUM",
            road_type="City_Road",
            weather="Clear",
            vehicles_involved=1,
            casualties=0,
            fatalities=0,
            is_blackspot=1,
        )
        assert record.is_blackspot == 1


# ── BlackSpotRecord schema tests ──────────────────────────────────────────────

class TestBlackSpotSchema:

    def test_valid_blackspot(self):
        bs = BlackSpotRecord(
            name="Silk Board Junction",
            lat=12.9170,
            lng=77.6228,
            severity="CRITICAL",
        )
        assert bs.name == "Silk Board Junction"

    def test_invalid_lat_raises(self):
        from pydantic import ValidationError
        with pytest.raises(ValidationError):
            BlackSpotRecord(name="Test", lat=15.0, lng=77.6, severity="HIGH")


# ── data_quality tests ────────────────────────────────────────────────────────

class TestDataQuality:

    @pytest.fixture
    def clean_df(self):
        return pd.DataFrame({
            "accident_id":    ["BLR-001", "BLR-002", "BLR-003"],
            "date":           ["2022-06-15", "2022-07-20", "2023-01-10"],
            "latitude":       [12.9170, 13.0067, 12.8353],
            "longitude":      [77.6228, 77.6963, 77.6772],
            "severity":       ["HIGH", "CRITICAL", "LOW"],
            "is_blackspot":   [1, 1, 0],
        })

    def test_quality_report_has_required_keys(self, clean_df):
        report = check_accident_quality(clean_df)
        assert "total_records" in report
        assert "missing_pct" in report
        assert "passes_quality" in report

    def test_clean_df_passes_quality(self, clean_df):
        report = check_accident_quality(clean_df)
        assert report["passes_quality"] is True

    def test_blackspot_rate_calculated(self, clean_df):
        report = check_accident_quality(clean_df)
        assert "blackspot_rate_pct" in report
        assert abs(report["blackspot_rate_pct"] - 66.67) < 1

    def test_duplicate_detection(self, clean_df):
        df_with_dup = pd.concat([clean_df, clean_df.iloc[[0]]], ignore_index=True)
        report = check_accident_quality(df_with_dup)
        assert report["duplicate_rows"] >= 1
