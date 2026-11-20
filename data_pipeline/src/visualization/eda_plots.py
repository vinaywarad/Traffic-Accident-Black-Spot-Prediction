"""
EDA visualization functions using matplotlib and seaborn.
All plots are saved to outputs/eda_report/ as PNG files.
"""
from pathlib import Path
from typing import Optional

import matplotlib
matplotlib.use("Agg")  # Non-interactive backend for server environments
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import seaborn as sns
import pandas as pd
import numpy as np
from loguru import logger

from src.config import EDA_REPORT_DIR

# Dark theme consistent with the frontend design
plt.rcParams.update({
    "figure.facecolor":  "#0A0C10",
    "axes.facecolor":    "#111418",
    "axes.edgecolor":    "#1E2329",
    "axes.labelcolor":   "#94A3B8",
    "xtick.color":       "#94A3B8",
    "ytick.color":       "#94A3B8",
    "text.color":        "#F1F5F9",
    "grid.color":        "#1E2329",
    "grid.alpha":        0.5,
    "figure.dpi":        120,
})

SEVERITY_COLORS = {
    "LOW":      "#22C55E",
    "MEDIUM":   "#F59E0B",
    "HIGH":     "#F97316",
    "CRITICAL": "#EF4444",
}


def _save(fig: plt.Figure, name: str) -> Path:
    EDA_REPORT_DIR.mkdir(parents=True, exist_ok=True)
    path = EDA_REPORT_DIR / f"{name}.png"
    fig.savefig(path, bbox_inches="tight", facecolor=fig.get_facecolor())
    plt.close(fig)
    logger.info(f"Saved plot: {path}")
    return path


def plot_missing_values(df: pd.DataFrame) -> Path:
    """Heatmap of missing values per column."""
    missing = df.isna().mean().sort_values(ascending=False)
    missing = missing[missing > 0]
    if missing.empty:
        logger.info("No missing values to plot")
        return None

    fig, ax = plt.subplots(figsize=(10, max(4, len(missing) * 0.4)))
    colors = ["#EF4444" if v > 0.2 else "#F59E0B" if v > 0.05 else "#22C55E"
              for v in missing.values]
    ax.barh(missing.index, missing.values * 100, color=colors)
    ax.set_xlabel("Missing %")
    ax.set_title("Missing Values by Column", color="#F1F5F9", fontsize=14)
    ax.xaxis.set_major_formatter(mticker.PercentFormatter())
    fig.tight_layout()
    return _save(fig, "01_missing_values")


def plot_class_balance(df: pd.DataFrame) -> Path:
    """Pie chart of is_blackspot class balance."""
    if "is_blackspot" not in df.columns:
        return None
    counts = df["is_blackspot"].value_counts()
    labels = ["Non-Black Spot", "Black Spot"]
    colors = ["#06B6D4", "#EF4444"]

    fig, ax = plt.subplots(figsize=(6, 6))
    wedges, texts, autotexts = ax.pie(
        counts.values, labels=labels, colors=colors,
        autopct="%1.1f%%", startangle=90,
        textprops={"color": "#F1F5F9"},
    )
    ax.set_title("Class Balance: Black Spot vs Non-Black Spot",
                 color="#F1F5F9", fontsize=13)
    return _save(fig, "02_class_balance")


def plot_accidents_by_year(df: pd.DataFrame) -> Path:
    """Bar chart of accident counts by year."""
    if "year" not in df.columns:
        return None
    counts = df.groupby("year").size()
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.bar(counts.index, counts.values, color="#F59E0B", alpha=0.85)
    ax.set_xlabel("Year")
    ax.set_ylabel("Accident Count")
    ax.set_title("Accidents by Year", color="#F1F5F9", fontsize=14)
    ax.grid(axis="y", alpha=0.3)
    return _save(fig, "03_accidents_by_year")


def plot_accidents_by_month(df: pd.DataFrame) -> Path:
    """Bar chart showing monsoon spike (Jun–Sep)."""
    if "month" not in df.columns:
        return None
    counts = df.groupby("month").size()
    month_names = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]
    colors = ["#EF4444" if m in [6,7,8,9] else "#F59E0B" for m in range(1, 13)]

    fig, ax = plt.subplots(figsize=(10, 5))
    ax.bar(month_names, [counts.get(m, 0) for m in range(1, 13)], color=colors)
    ax.set_xlabel("Month")
    ax.set_ylabel("Accident Count")
    ax.set_title("Accidents by Month (Red = Monsoon)", color="#F1F5F9", fontsize=14)
    ax.grid(axis="y", alpha=0.3)
    return _save(fig, "04_accidents_by_month")


def plot_accidents_by_hour(df: pd.DataFrame) -> Path:
    """Line chart showing morning/evening peak hours."""
    if "hour" not in df.columns:
        return None
    counts = df.groupby("hour").size()

    fig, ax = plt.subplots(figsize=(12, 5))
    ax.plot(counts.index, counts.values, color="#06B6D4", linewidth=2.5, marker="o", markersize=4)
    ax.fill_between(counts.index, counts.values, alpha=0.2, color="#06B6D4")
    for peak in [8, 9, 10, 17, 18, 19, 20]:
        ax.axvline(peak, color="#F59E0B", alpha=0.3, linewidth=1)
    ax.set_xlabel("Hour of Day")
    ax.set_ylabel("Accident Count")
    ax.set_title("Accidents by Hour (Amber = Peak Hours)", color="#F1F5F9", fontsize=14)
    ax.set_xticks(range(24))
    ax.grid(alpha=0.3)
    return _save(fig, "05_accidents_by_hour")


def plot_hour_day_heatmap(df: pd.DataFrame) -> Path:
    """Seaborn heatmap: hour × day_of_week."""
    if "hour" not in df.columns or "day_of_week" not in df.columns:
        return None
    pivot = df.pivot_table(index="day_of_week", columns="hour",
                           values="accident_id" if "accident_id" in df.columns else "latitude",
                           aggfunc="count", fill_value=0)
    day_order = ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]
    pivot = pivot.reindex([d for d in day_order if d in pivot.index])

    fig, ax = plt.subplots(figsize=(16, 5))
    sns.heatmap(pivot, cmap="YlOrRd", ax=ax, linewidths=0.3,
                cbar_kws={"label": "Accident Count"})
    ax.set_title("Accident Heatmap: Hour × Day of Week", color="#F1F5F9", fontsize=14)
    ax.set_xlabel("Hour")
    ax.set_ylabel("Day")
    return _save(fig, "06_hour_day_heatmap")


def plot_severity_distribution(df: pd.DataFrame) -> Path:
    """Donut chart of severity distribution."""
    if "severity" not in df.columns:
        return None
    counts = df["severity"].value_counts()
    order  = [s for s in ["CRITICAL","HIGH","MEDIUM","LOW"] if s in counts.index]
    colors = [SEVERITY_COLORS[s] for s in order]

    fig, ax = plt.subplots(figsize=(7, 7))
    wedges, _, autotexts = ax.pie(
        [counts[s] for s in order], labels=order, colors=colors,
        autopct="%1.1f%%", startangle=90, pctdistance=0.75,
        wedgeprops={"width": 0.5}, textprops={"color": "#F1F5F9"},
    )
    ax.set_title("Severity Distribution", color="#F1F5F9", fontsize=14)
    return _save(fig, "07_severity_distribution")


def plot_weather_vs_severity(df: pd.DataFrame) -> Path:
    """Crosstab heatmap: weather vs severity."""
    if "weather" not in df.columns or "severity" not in df.columns:
        return None
    ct = pd.crosstab(df["weather"], df["severity"], normalize="index") * 100

    fig, ax = plt.subplots(figsize=(10, 6))
    sns.heatmap(ct, annot=True, fmt=".1f", cmap="RdYlGn_r", ax=ax,
                cbar_kws={"label": "% of accidents"})
    ax.set_title("Weather vs Severity (%)", color="#F1F5F9", fontsize=14)
    return _save(fig, "08_weather_vs_severity")


def plot_road_type_accidents(df: pd.DataFrame) -> Path:
    """Bar chart of accidents by road type."""
    if "road_type" not in df.columns:
        return None
    counts = df["road_type"].value_counts()
    fig, ax = plt.subplots(figsize=(9, 5))
    ax.bar(counts.index, counts.values, color="#06B6D4", alpha=0.85)
    ax.set_xlabel("Road Type")
    ax.set_ylabel("Accident Count")
    ax.set_title("Accidents by Road Type", color="#F1F5F9", fontsize=14)
    ax.grid(axis="y", alpha=0.3)
    return _save(fig, "09_road_type_accidents")


def run_all_eda_plots(df: pd.DataFrame) -> list[Path]:
    """Run all EDA plots and return list of saved file paths."""
    logger.info("Generating EDA plots...")
    plots = [
        plot_missing_values(df),
        plot_class_balance(df),
        plot_accidents_by_year(df),
        plot_accidents_by_month(df),
        plot_accidents_by_hour(df),
        plot_hour_day_heatmap(df),
        plot_severity_distribution(df),
        plot_weather_vs_severity(df),
        plot_road_type_accidents(df),
    ]
    saved = [p for p in plots if p is not None]
    logger.success(f"Saved {len(saved)} EDA plots to {EDA_REPORT_DIR}")
    return saved
