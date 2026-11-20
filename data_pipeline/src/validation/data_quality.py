"""
Data quality checks and reporting for the pipeline.
Validates DataFrames against schemas and generates quality reports.
"""
from typing import Optional
import pandas as pd
import numpy as np
from loguru import logger
from pydantic import ValidationError

from src.validation.schemas import AccidentRecord, FeatureRecord
from src.config import BENGALURU_BOUNDS


def check_accident_quality(df: pd.DataFrame) -> dict:
    """
    Run comprehensive quality checks on the accident DataFrame.

    Checks:
        - Missing value rates per column
        - Coordinate bounds violations
        - Duplicate accident IDs
        - Severity distribution
        - Date range validity
        - Class imbalance ratio

    Args:
        df: Accident DataFrame to check.

    Returns:
        Dict with quality metrics and pass/fail flags.
    """
    report = {}

    # Missing values
    report["missing_pct"] = (df.isna().sum() / len(df) * 100).round(2).to_dict()
    report["total_records"] = len(df)

    # Coordinate bounds
    if "latitude" in df.columns and "longitude" in df.columns:
        lat_ok = df["latitude"].between(*BENGALURU_BOUNDS["lat"])
        lng_ok = df["longitude"].between(*BENGALURU_BOUNDS["lng"])
        report["out_of_bounds_count"] = int((~lat_ok | ~lng_ok).sum())
        report["out_of_bounds_pct"]   = round(report["out_of_bounds_count"] / len(df) * 100, 2)

    # Duplicates
    if "accident_id" in df.columns:
        report["duplicate_ids"] = int(df["accident_id"].duplicated().sum())
    report["duplicate_rows"] = int(df.duplicated().sum())

    # Severity distribution
    if "severity" in df.columns:
        report["severity_dist"] = df["severity"].value_counts().to_dict()
        report["invalid_severity"] = int(
            ~df["severity"].isin(["LOW", "MEDIUM", "HIGH", "CRITICAL"]).sum()
        )

    # Date range
    if "date" in df.columns:
        dates = pd.to_datetime(df["date"], errors="coerce")
        report["date_min"]    = str(dates.min().date()) if dates.notna().any() else None
        report["date_max"]    = str(dates.max().date()) if dates.notna().any() else None
        report["invalid_dates"] = int(dates.isna().sum())

    # Class imbalance
    if "is_blackspot" in df.columns:
        bs_rate = df["is_blackspot"].mean()
        report["blackspot_rate_pct"] = round(bs_rate * 100, 2)
        report["class_imbalance_ratio"] = round(
            (1 - bs_rate) / bs_rate if bs_rate > 0 else float("inf"), 1
        )

    # Overall pass/fail
    report["passes_quality"] = (
        report.get("out_of_bounds_pct", 0) < 5 and
        report.get("duplicate_rows", 0) < len(df) * 0.01 and
        report.get("invalid_dates", 0) < len(df) * 0.05
    )

    return report


def validate_sample(
    df: pd.DataFrame,
    schema=AccidentRecord,
    sample_size: int = 100,
) -> dict:
    """
    Validate a random sample of records against a Pydantic schema.

    Args:
        df: DataFrame to validate.
        schema: Pydantic model class to validate against.
        sample_size: Number of rows to sample.

    Returns:
        Dict with validation results and error examples.
    """
    sample = df.sample(min(sample_size, len(df)), random_state=42)
    errors = []
    valid_count = 0

    for _, row in sample.iterrows():
        try:
            schema(**row.dropna().to_dict())
            valid_count += 1
        except (ValidationError, Exception) as e:
            errors.append(str(e)[:200])

    result = {
        "sample_size":   len(sample),
        "valid_count":   valid_count,
        "error_count":   len(errors),
        "valid_rate_pct": round(valid_count / len(sample) * 100, 1),
        "error_examples": errors[:5],
    }
    logger.info(f"Schema validation: {valid_count}/{len(sample)} valid "
                f"({result['valid_rate_pct']}%)")
    return result


def print_quality_report(report: dict) -> None:
    """Pretty-print a quality report dict to the logger."""
    logger.info("=" * 60)
    logger.info("DATA QUALITY REPORT")
    logger.info("=" * 60)
    for key, value in report.items():
        if key != "missing_pct":
            logger.info(f"  {key:<35} {value}")
    if "missing_pct" in report:
        logger.info("  Missing values per column:")
        for col, pct in report["missing_pct"].items():
            if pct > 0:
                logger.info(f"    {col:<30} {pct:.1f}%")
    status = "✓ PASS" if report.get("passes_quality") else "✗ FAIL"
    logger.info(f"  Overall: {status}")
    logger.info("=" * 60)
