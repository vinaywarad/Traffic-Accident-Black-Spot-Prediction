"""
Download and cache the full Bengaluru road network from OpenStreetMap.
Extracts road segments with geometry, type, speed limits, lanes.
"""
from pathlib import Path

import geopandas as gpd
from loguru import logger

try:
    import osmnx as ox
    OSMNX_AVAILABLE = True
except ImportError:
    OSMNX_AVAILABLE = False
    logger.warning("osmnx not available — road network download disabled")

from src.config import BENGALURU_BBOX, RAW_ROAD_DIR


def download_road_network(
    output_dir: Path = RAW_ROAD_DIR,
    network_type: str = "drive",
) -> tuple:
    """
    Download Bengaluru road network from OSM.
    Saves as .graphml and .geojson to output_dir.

    Args:
        output_dir: Directory to save network files.
        network_type: 'drive' for vehicle roads only.

    Returns:
        Tuple of (graph G, edges GeoDataFrame).
    """
    if not OSMNX_AVAILABLE:
        raise ImportError("osmnx is required for road network download. "
                          "Install with: pip install osmnx")

    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    graphml_path  = output_dir / "bengaluru_roads.graphml"
    geojson_path  = output_dir / "bengaluru_roads.geojson"

    # Use cached file if it exists
    if graphml_path.exists():
        logger.info(f"Loading cached road network from {graphml_path}")
        G = ox.load_graphml(graphml_path)
        edges = ox.graph_to_gdfs(G, nodes=False, edges=True)
        return G, edges

    logger.info("Downloading Bengaluru road network from OSM...")
    G = ox.graph_from_bbox(
        north=BENGALURU_BBOX["north"],
        south=BENGALURU_BBOX["south"],
        east=BENGALURU_BBOX["east"],
        west=BENGALURU_BBOX["west"],
        network_type=network_type,
        retain_all=False,
    )

    ox.save_graphml(G, filepath=graphml_path)
    edges = ox.graph_to_gdfs(G, nodes=False, edges=True)
    edges.to_file(geojson_path, driver="GeoJSON")

    logger.success(f"Saved {len(edges)} road segments to {output_dir}")
    return G, edges


def extract_junctions(G) -> gpd.GeoDataFrame:
    """
    Extract all road junctions (nodes with degree >= 3).

    Args:
        G: OSMnx road network graph.

    Returns:
        GeoDataFrame with junction coordinates and street_count.
    """
    if not OSMNX_AVAILABLE:
        raise ImportError("osmnx is required")

    nodes, _ = ox.graph_to_gdfs(G)
    junctions = nodes[nodes["street_count"] >= 3].copy()
    logger.info(f"Extracted {len(junctions)} junctions")
    return junctions


def load_road_network_from_file(
    geojson_path: Path = None,
) -> gpd.GeoDataFrame:
    """
    Load road network edges from a saved GeoJSON file.

    Args:
        geojson_path: Path to bengaluru_roads.geojson.

    Returns:
        GeoDataFrame of road edges.
    """
    path = geojson_path or (RAW_ROAD_DIR / "bengaluru_roads.geojson")
    if not Path(path).exists():
        raise FileNotFoundError(
            f"Road network file not found: {path}\n"
            "Run download_road_network() first."
        )
    gdf = gpd.read_file(path)
    logger.info(f"Loaded {len(gdf)} road segments from {path}")
    return gdf
