"""
SQLAlchemy SQLite setup for the local feature store.
Provides functions to store and query processed accident data.
"""
from pathlib import Path
from typing import Optional

import pandas as pd
from loguru import logger
from sqlalchemy import create_engine, text, inspect
from sqlalchemy.engine import Engine

from src.config import PROCESSED_DIR

DB_PATH = PROCESSED_DIR / "blackspot_features.db"


def get_engine(db_path: Path = DB_PATH) -> Engine:
    """
    Create and return a SQLAlchemy engine for the SQLite feature store.

    Args:
        db_path: Path to the SQLite database file.

    Returns:
        SQLAlchemy Engine instance.
    """
    db_path.parent.mkdir(parents=True, exist_ok=True)
    engine = create_engine(f"sqlite:///{db_path}", echo=False)
    logger.debug(f"Connected to SQLite: {db_path}")
    return engine


def save_to_db(
    df: pd.DataFrame,
    table_name: str,
    engine: Optional[Engine] = None,
    if_exists: str = "replace",
) -> None:
    """
    Save a DataFrame to a SQLite table.

    Args:
        df: DataFrame to save.
        table_name: Target table name.
        engine: SQLAlchemy engine (creates default if None).
        if_exists: 'replace', 'append', or 'fail'.
    """
    engine = engine or get_engine()
    df.to_sql(table_name, engine, if_exists=if_exists, index=False)
    logger.info(f"Saved {len(df)} rows to table '{table_name}' in SQLite")


def load_from_db(
    table_name: str,
    engine: Optional[Engine] = None,
    query: Optional[str] = None,
) -> pd.DataFrame:
    """
    Load data from a SQLite table into a DataFrame.

    Args:
        table_name: Source table name.
        engine: SQLAlchemy engine (creates default if None).
        query: Optional SQL query (overrides table_name if provided).

    Returns:
        DataFrame with table contents.
    """
    engine = engine or get_engine()
    sql = query or f"SELECT * FROM {table_name}"
    df = pd.read_sql(sql, engine)
    logger.info(f"Loaded {len(df)} rows from '{table_name}'")
    return df


def list_tables(engine: Optional[Engine] = None) -> list[str]:
    """
    List all tables in the SQLite database.

    Args:
        engine: SQLAlchemy engine.

    Returns:
        List of table names.
    """
    engine = engine or get_engine()
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    logger.info(f"Tables in DB: {tables}")
    return tables


def execute_query(sql: str, engine: Optional[Engine] = None) -> pd.DataFrame:
    """
    Execute a raw SQL query and return results as a DataFrame.

    Args:
        sql: SQL query string.
        engine: SQLAlchemy engine.

    Returns:
        Query result as DataFrame.
    """
    engine = engine or get_engine()
    with engine.connect() as conn:
        result = conn.execute(text(sql))
        return pd.DataFrame(result.fetchall(), columns=result.keys())
