"""
Generate realistic synthetic accident data for Bengaluru.
Based on real black spot locations, known traffic patterns,
monsoon seasonality, and road type distributions.
"""
import random
from datetime import datetime, timedelta

import numpy as np
import pandas as pd
from loguru import logger

# Bengaluru coordinate bounds
LAT_MIN, LAT_MAX = 12.75, 13.18
LNG_MIN, LNG_MAX = 77.38, 77.82

# Hotspot seeds: (lat, lng, weight)
HOTSPOT_SEEDS = [
    (12.9170, 77.6228, 0.15),  # Silk Board
    (12.9591, 77.6974, 0.12),  # Marathahalli
    (13.0450, 77.5970, 0.08),  # Hebbal
    (13.0067, 77.6963, 0.08),  # KR Puram
    (12.9980, 77.6590, 0.07),  # Tin Factory
    (12.9228, 77.6200, 0.06),  # Madiwala
    (12.9307, 77.6784, 0.05),  # Bellandur ORR
    (12.8353, 77.6772, 0.05),  # Electronic City
    (13.0290, 77.5160, 0.04),  # Tumkur Road
    (12.9087, 77.4824, 0.03),  # Mysore Road
]

ROAD_TYPES        = ["NH", "SH", "ORR", "City_Road", "Residential", "Service_Road"]
ROAD_TYPE_WEIGHTS = [0.10, 0.08, 0.15, 0.40, 0.20, 0.07]

ACCIDENT_TYPES = [
    "Rear-end collision", "Head-on collision", "Side swipe",
    "Pedestrian hit", "Two-wheeler fall", "Hit and run",
    "Vehicle overturning", "Hitting road divider",
]

WEATHER_CONDITIONS = ["Clear", "Rainy", "Foggy", "Overcast", "Night-Clear", "Night-Rainy"]
WEATHER_WEIGHTS    = [0.45,   0.25,   0.05,   0.10,       0.10,          0.05]

VEHICLE_TYPES = ["Car", "Two-wheeler", "Auto-rickshaw", "Bus", "Truck", "Van"]

SPEED_LIMITS = {
    "NH": 80, "SH": 60, "ORR": 80,
    "City_Road": 40, "Residential": 30, "Service_Road": 30,
}


def _sample_location() -> tuple[float, float]:
    """Sample a lat/lng — 56% near known hotspots, 44% random."""
    if random.random() < 0.56:
        seed = random.choices(HOTSPOT_SEEDS, weights=[s[2] for s in HOTSPOT_SEEDS])[0]
        lat = float(np.clip(np.random.normal(seed[0], 0.008), LAT_MIN, LAT_MAX))
        lng = float(np.clip(np.random.normal(seed[1], 0.008), LNG_MIN, LNG_MAX))
    else:
        lat = np.random.uniform(LAT_MIN, LAT_MAX)
        lng = np.random.uniform(LNG_MIN, LNG_MAX)
    return round(lat, 6), round(lng, 6)


def _sample_datetime(start_dt: datetime, date_range_days: int) -> tuple[datetime, int]:
    """Sample a datetime with peak-hour and monsoon bias."""
    rand_day = random.randint(0, date_range_days)
    dt = start_dt + timedelta(days=rand_day)
    month = dt.month
    is_monsoon = month in [6, 7, 8, 9]

    hour_weights = [1] * 24
    for h in [8, 9, 10]:
        hour_weights[h] = 4
    for h in [17, 18, 19, 20]:
        hour_weights[h] = 5
    if is_monsoon:
        for h in [21, 22, 23, 0]:
            hour_weights[h] = 3

    hour = random.choices(range(24), weights=hour_weights)[0]
    return dt.replace(hour=hour, minute=random.randint(0, 59)), hour


def _near_hotspot(lat: float, lng: float) -> bool:
    return any(
        ((lat - s[0]) ** 2 + (lng - s[1]) ** 2) ** 0.5 < 0.01
        for s in HOTSPOT_SEEDS
    )


def generate_accident_records(
    n: int = 5000,
    start_year: int = 2019,
    end_year: int = 2023,
    random_seed: int = 42,
) -> pd.DataFrame:
    """
    Generate n synthetic accident records with realistic Bengaluru patterns.

    Includes monsoon seasonality, peak-hour bias, and spatial hotspot clustering.

    Args:
        n: Number of records to generate.
        start_year: First year of data.
        end_year: Last year of data.
        random_seed: Reproducibility seed.

    Returns:
        DataFrame with all accident fields including is_blackspot target.
    """
    random.seed(random_seed)
    np.random.seed(random_seed)

    start_dt = datetime(start_year, 1, 1)
    end_dt   = datetime(end_year, 12, 31)
    date_range_days = (end_dt - start_dt).days

    records = []
    for i in range(n):
        lat, lng = _sample_location()
        dt, hour = _sample_datetime(start_dt, date_range_days)
        month = dt.month
        is_monsoon = month in [6, 7, 8, 9]

        weather = random.choices(WEATHER_CONDITIONS, weights=WEATHER_WEIGHTS)[0]
        if is_monsoon and random.random() < 0.4:
            weather = "Rainy"

        road_type   = random.choices(ROAD_TYPES, weights=ROAD_TYPE_WEIGHTS)[0]
        acc_type    = random.choice(ACCIDENT_TYPES)
        vehicles    = random.randint(1, 4)
        casualties  = random.randint(0, vehicles * 2)
        fatalities  = random.randint(0, min(casualties, 2))
        speed_limit = SPEED_LIMITS[road_type]

        if fatalities > 0 or casualties >= 3:
            severity = "CRITICAL"
        elif casualties >= 2:
            severity = "HIGH"
        elif casualties == 1:
            severity = "MEDIUM"
        else:
            severity = "LOW"

        hotspot_proximity = _near_hotspot(lat, lng)
        is_blackspot = int(
            (hotspot_proximity and severity in ["HIGH", "CRITICAL"])
            or random.random() < 0.08
        )

        records.append({
            "accident_id":       f"BLR-{start_year}-{i:05d}",
            "date":              dt.strftime("%Y-%m-%d"),
            "time":              dt.strftime("%H:%M"),
            "year":              dt.year,
            "month":             month,
            "day_of_week":       dt.strftime("%A"),
            "hour":              hour,
            "latitude":          lat,
            "longitude":         lng,
            "road_type":         road_type,
            "accident_type":     acc_type,
            "weather":           weather,
            "road_condition":    "Wet" if weather == "Rainy" else "Dry",
            "light_condition":   "Daylight" if 6 <= hour <= 18 else "Dark",
            "speed_limit":       speed_limit,
            "vehicles_involved": vehicles,
            "casualties":        casualties,
            "fatalities":        fatalities,
            "severity":          severity,
            "is_monsoon":        int(is_monsoon),
            "is_peak_hour":      int(hour in list(range(8, 11)) + list(range(17, 21))),
            "is_blackspot":      is_blackspot,
        })

    df = pd.DataFrame(records)
    logger.info(f"Generated {len(df)} synthetic accident records "
                f"({df['is_blackspot'].sum()} black spots, "
                f"{df['is_blackspot'].mean():.1%} rate)")
    return df
