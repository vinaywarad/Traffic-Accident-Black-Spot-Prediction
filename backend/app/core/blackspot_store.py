"""
Static store of known Bengaluru black spots.
In production this would be a PostgreSQL table.
For now: in-memory list seeded from ground-truth data.
"""
import random
from datetime import datetime, timedelta

BENGALURU_BLACKSPOTS = [
    {"id": "BS-001", "name": "Silk Board Junction",       "lat": 12.9170, "lng": 77.6228,
     "severity": "CRITICAL", "risk_score": 0.94, "annual_accidents": 48, "fatalities_ytd": 3,
     "road_type": "ORR",       "primary_cause": "Junction complexity + high speed"},
    {"id": "BS-002", "name": "Marathahalli Bridge",        "lat": 12.9591, "lng": 77.6974,
     "severity": "CRITICAL", "risk_score": 0.91, "annual_accidents": 41, "fatalities_ytd": 2,
     "road_type": "ORR",       "primary_cause": "Narrow bridge + heavy traffic"},
    {"id": "BS-003", "name": "Outer Ring Road Bellandur",  "lat": 12.9307, "lng": 77.6784,
     "severity": "CRITICAL", "risk_score": 0.89, "annual_accidents": 38, "fatalities_ytd": 2,
     "road_type": "ORR",       "primary_cause": "High speed + frequent lane changes"},
    {"id": "BS-004", "name": "Hebbal Flyover",             "lat": 13.0450, "lng": 77.5970,
     "severity": "HIGH",     "risk_score": 0.82, "annual_accidents": 29, "fatalities_ytd": 1,
     "road_type": "NH",        "primary_cause": "Merging lanes at speed"},
    {"id": "BS-005", "name": "KR Puram Bridge",            "lat": 13.0067, "lng": 77.6963,
     "severity": "HIGH",     "risk_score": 0.79, "annual_accidents": 27, "fatalities_ytd": 2,
     "road_type": "NH",        "primary_cause": "Old bridge, poor visibility"},
    {"id": "BS-006", "name": "Tin Factory Junction",       "lat": 12.9980, "lng": 77.6590,
     "severity": "HIGH",     "risk_score": 0.77, "annual_accidents": 24, "fatalities_ytd": 1,
     "road_type": "City_Road", "primary_cause": "4-way junction, no signal compliance"},
    {"id": "BS-007", "name": "Madiwala Junction",          "lat": 12.9228, "lng": 77.6200,
     "severity": "HIGH",     "risk_score": 0.74, "annual_accidents": 22, "fatalities_ytd": 0,
     "road_type": "City_Road", "primary_cause": "Pedestrian + vehicle conflict"},
    {"id": "BS-008", "name": "Hosur Road Electronic City", "lat": 12.8353, "lng": 77.6772,
     "severity": "HIGH",     "risk_score": 0.78, "annual_accidents": 26, "fatalities_ytd": 1,
     "road_type": "NH",        "primary_cause": "IT corridor peak hour bottleneck"},
    {"id": "BS-009", "name": "Tumkur Road NH4",            "lat": 13.0290, "lng": 77.5160,
     "severity": "HIGH",     "risk_score": 0.75, "annual_accidents": 23, "fatalities_ytd": 2,
     "road_type": "NH",        "primary_cause": "Heavy truck + two-wheeler conflict"},
    {"id": "BS-010", "name": "Sarjapur Road Junction",     "lat": 12.9102, "lng": 77.6860,
     "severity": "HIGH",     "risk_score": 0.72, "annual_accidents": 20, "fatalities_ytd": 0,
     "road_type": "City_Road", "primary_cause": "Rapid growth area, poor signage"},
    {"id": "BS-011", "name": "Nagawara Junction",          "lat": 13.0450, "lng": 77.6227,
     "severity": "MEDIUM",   "risk_score": 0.62, "annual_accidents": 15, "fatalities_ytd": 0,
     "road_type": "City_Road", "primary_cause": "High pedestrian volume"},
    {"id": "BS-012", "name": "Bannerghatta Road ORR",      "lat": 12.8991, "lng": 77.5982,
     "severity": "MEDIUM",   "risk_score": 0.58, "annual_accidents": 13, "fatalities_ytd": 0,
     "road_type": "ORR",       "primary_cause": "Uncontrolled access points"},
    {"id": "BS-013", "name": "Bellary Road Hebbal",        "lat": 13.0358, "lng": 77.5970,
     "severity": "MEDIUM",   "risk_score": 0.55, "annual_accidents": 12, "fatalities_ytd": 0,
     "road_type": "NH",        "primary_cause": "Airport traffic merging"},
    {"id": "BS-014", "name": "Mysore Road Kengeri",        "lat": 12.9087, "lng": 77.4824,
     "severity": "MEDIUM",   "risk_score": 0.52, "annual_accidents": 11, "fatalities_ytd": 0,
     "road_type": "NH",        "primary_cause": "Suburban sprawl, mixed traffic"},
    {"id": "BS-015", "name": "Old Madras Road KR Puram",   "lat": 13.0024, "lng": 77.6740,
     "severity": "HIGH",     "risk_score": 0.76, "annual_accidents": 25, "fatalities_ytd": 1,
     "road_type": "NH",        "primary_cause": "Industrial traffic + potholes"},
]


def get_all_blackspots() -> list:
    return BENGALURU_BLACKSPOTS


def get_blackspot_by_id(spot_id: str) -> dict | None:
    return next((s for s in BENGALURU_BLACKSPOTS if s["id"] == spot_id), None)


def get_heatmap_data(year: int = None, month: int = None) -> list:
    """Return lat/lng/intensity points for the Leaflet heatmap layer."""
    return [
        {
            "lat":       s["lat"],
            "lng":       s["lng"],
            "intensity": s["risk_score"],
            "count":     s["annual_accidents"],
        }
        for s in BENGALURU_BLACKSPOTS
    ]


def get_trend_data(months: int = 24) -> list:
    """Return month-by-month accident counts for the trend chart."""
    rng = random.Random(42)
    data = []
    base = datetime(2022, 1, 1)
    for i in range(months):
        d = base + timedelta(days=30 * i)
        is_monsoon = d.month in [6, 7, 8, 9]
        count = rng.randint(28, 48) if is_monsoon else rng.randint(12, 30)
        data.append({
            "month":      d.strftime("%Y-%m"),
            "accidents":  count,
            "blackspots": rng.randint(10, 18),
        })
    return data
