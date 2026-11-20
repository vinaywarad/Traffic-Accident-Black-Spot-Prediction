"""
Folium interactive map visualizations for accident data and black spots.
Outputs HTML files to outputs/maps/.
"""
from pathlib import Path
from typing import Optional

import pandas as pd
from loguru import logger

try:
    import folium
    from folium.plugins import HeatMap, MarkerCluster, MiniMap
    FOLIUM_AVAILABLE = True
except ImportError:
    FOLIUM_AVAILABLE = False
    logger.warning("folium not available — map visualization disabled")

from src.config import BENGALURU_CENTER, MAPS_DIR, KNOWN_BLACKSPOTS

SEVERITY_COLORS = {
    "LOW":      "#22C55E",
    "MEDIUM":   "#F59E0B",
    "HIGH":     "#F97316",
    "CRITICAL": "#EF4444",
}


def create_accident_map(
    df: pd.DataFrame,
    sample_n: int = 1000,
    output_name: str = "bengaluru_accidents",
) -> Optional[Path]:
    """
    Create an interactive Folium map of accident locations.

    Features:
        - Dark tile layer (CartoDB Dark Matter)
        - Color-coded markers by severity
        - Marker cluster for performance
        - Popup with accident details
        - MiniMap overlay
        - Known black spots highlighted

    Args:
        df: Accident DataFrame with latitude, longitude, severity columns.
        sample_n: Max number of accidents to plot (random sample).
        output_name: Output HTML filename without extension.

    Returns:
        Path to saved HTML file, or None if folium unavailable.
    """
    if not FOLIUM_AVAILABLE:
        logger.warning("folium not installed — skipping map generation")
        return None

    MAPS_DIR.mkdir(parents=True, exist_ok=True)

    # Sample for performance
    plot_df = df.sample(min(sample_n, len(df)), random_state=42)

    m = folium.Map(
        location=list(BENGALURU_CENTER),
        zoom_start=11,
        tiles="CartoDB dark_matter",
    )

    # Marker cluster layer
    cluster = MarkerCluster(name="Accidents").add_to(m)

    for _, row in plot_df.iterrows():
        if pd.isna(row.get("latitude")) or pd.isna(row.get("longitude")):
            continue
        severity = row.get("severity", "LOW")
        color    = SEVERITY_COLORS.get(severity, "#94A3B8")

        popup_html = f"""
        <div style='font-family:monospace;font-size:12px;min-width:180px'>
            <b>{row.get('accident_id', 'N/A')}</b><br>
            Date: {row.get('date', 'N/A')}<br>
            Severity: <span style='color:{color}'><b>{severity}</b></span><br>
            Road: {row.get('road_type', 'N/A')}<br>
            Weather: {row.get('weather', 'N/A')}<br>
            Casualties: {row.get('casualties', 0)}<br>
            Fatalities: {row.get('fatalities', 0)}
        </div>
        """

        folium.CircleMarker(
            location=[row["latitude"], row["longitude"]],
            radius=5 if severity == "CRITICAL" else 4,
            color=color,
            fill=True,
            fill_color=color,
            fill_opacity=0.7,
            popup=folium.Popup(popup_html, max_width=250),
            tooltip=f"{severity} — {row.get('road_type', '')}",
        ).add_to(cluster)

    # Known black spots layer
    bs_layer = folium.FeatureGroup(name="Known Black Spots")
    for bs in KNOWN_BLACKSPOTS:
        color = SEVERITY_COLORS.get(bs["severity"], "#EF4444")
        folium.Marker(
            location=[bs["lat"], bs["lng"]],
            popup=folium.Popup(
                f"<b>{bs['name']}</b><br>Severity: {bs['severity']}", max_width=200
            ),
            tooltip=bs["name"],
            icon=folium.Icon(color="red", icon="warning-sign", prefix="glyphicon"),
        ).add_to(bs_layer)
    bs_layer.add_to(m)

    # Heatmap layer
    heat_data = [
        [row["latitude"], row["longitude"]]
        for _, row in plot_df.iterrows()
        if pd.notna(row.get("latitude"))
    ]
    HeatMap(heat_data, name="Accident Heatmap", radius=15, blur=10).add_to(m)

    # Controls
    folium.LayerControl().add_to(m)
    MiniMap(toggle_display=True).add_to(m)

    output_path = MAPS_DIR / f"{output_name}.html"
    m.save(str(output_path))
    logger.success(f"Saved accident map: {output_path}")
    return output_path


def create_blackspot_map(
    df: pd.DataFrame,
    output_name: str = "bengaluru_blackspots",
) -> Optional[Path]:
    """
    Create a focused map showing only identified black spot locations.

    Args:
        df: DataFrame with is_blackspot=1 records.
        output_name: Output HTML filename.

    Returns:
        Path to saved HTML file.
    """
    if not FOLIUM_AVAILABLE:
        return None

    bs_df = df[df.get("is_blackspot", pd.Series(0, index=df.index)) == 1]
    if bs_df.empty:
        logger.warning("No black spot records found for map")
        return None

    return create_accident_map(bs_df, sample_n=500, output_name=output_name)
