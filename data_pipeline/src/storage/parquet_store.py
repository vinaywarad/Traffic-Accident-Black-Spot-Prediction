"""
Parquet file read/write utilities for the pipeline data store.
All intermediate and processed data is stored as Parquet for efficiency.
"""
from pathlib import Path
from typing import Optional, Union

import pandas as pd
from loguru import logger

from src.config import INTERIM_DIR, PROCESSED_DIR


def save_parquet(
    df: pd.DataFrame,
    path: Union[str, Path],
    compression: str = "snappy",
) -> Path:
    """
    Save a DataFrame to a Parquet file.

    Args:
        df: DataFrame to save.
        path: Output file path (relative paths resolved from project root).
        compression: Parquet compression codec ('snappy', 'gzip', 'none').

    Returns:
        Absolute path to saved file.
    """
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(path, index=False, compression=compression)
    size_mb = path.stat().st_size / 1_048_576
    logger.info(f"Saved Parquet: {path} ({len(df)} rows, {size_mb:.2f} MB)")
    return path


def load_parquet(path: Union[str, Path]) -> pd.DataFrame:
    """
    Load a Parquet file into a DataFrame.

    Args:
        path: Path to the Parquet file.

    Returns:
        Loaded DataFrame.

    Raises:
        FileNotFoundError: If the file does not exist.
    """
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"Parquet file not found: {path}")
    df = pd.read_parquet(path)
    logger.info(f"Loaded Parquet: {path} ({len(df)} rows, {df.shape[1]} cols)")
    return df


def save_interim(df: pd.DataFrame, name: str) -> Path:
    """Save to the interim data directory."""
    return save_parquet(df, INTERIM_DIR / f"{name}.parquet")


def load_interim(name: str) -> pd.DataFrame:
    """Load from the interim data directory."""
    return load_parquet(INTERIM_DIR / f"{name}.parquet")


def save_processed(df: pd.DataFrame, name: str) -> Path:
    """Save to the processed data directory."""
    return save_parquet(df, PROCESSED_DIR / f"{name}.parquet")


def load_processed(name: str) -> pd.DataFrame:
    """Load from the processed data directory."""
    return load_parquet(PROCESSED_DIR / f"{name}.parquet")


def list_parquet_files(directory: Union[str, Path]) -> list[Path]:
    """
    List all Parquet files in a directory.

    Args:
        directory: Directory to search.

    Returns:
        Sorted list of Parquet file paths.
    """
    directory = Path(directory)
    files = sorted(directory.glob("*.parquet"))
    logger.debug(f"Found {len(files)} Parquet files in {directory}")
    return files


def get_parquet_info(path: Union[str, Path]) -> dict:
    """
    Return metadata about a Parquet file without loading all data.

    Args:
        path: Path to the Parquet file.

    Returns:
        Dict with row count, column names, and file size.
    """
    import pyarrow.parquet as pq
    path = Path(path)
    pf = pq.ParquetFile(path)
    meta = pf.metadata
    return {
        "path":       str(path),
        "rows":       meta.num_rows,
        "columns":    pf.schema_arrow.names,
        "row_groups": meta.num_row_groups,
        "size_mb":    round(path.stat().st_size / 1_048_576, 3),
    }
