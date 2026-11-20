# Traffic Accident Black Spot Prediction — Data Pipeline

Bengaluru-specific data engineering pipeline that ingests, cleans, feature-engineers,
and exports ML-ready data for black spot prediction models.

---

## Architecture

```
Raw Data → Cleaning → Feature Engineering → Preprocessing → ML-Ready Splits
```

Three sequential stages:
1. **Collection** — synthetic data generation + OSM road network download
2. **Cleaning + EDA** — deduplication, coordinate validation, date normalization, EDA plots
3. **Feature Engineering** — spatial, temporal, environmental, road features + black spot labeling
4. **Preprocessing** — encoding, scaling, temporal split, SMOTE balancing, Parquet export

---

## Quick Start

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Run the full pipeline

```bash
python pipeline.py --stage all
```

### 3. Run individual stages

```bash
python pipeline.py --stage collect     # Generate synthetic data
python pipeline.py --stage clean       # Clean + EDA plots
python pipeline.py --stage features    # Feature engineering
python pipeline.py --stage preprocess  # Scale, split, SMOTE, export
```

### 4. Run tests

```bash
pytest tests/ -v
```

---

## Outputs

After `python pipeline.py --stage all`:

| File | Description |
|------|-------------|
| `data/processed/features_final.parquet` | Full feature matrix (all records) |
| `data/processed/X_train.parquet` | Training features (SMOTE-balanced) |
| `data/processed/X_test.parquet` | Test features (2023 data) |
| `data/processed/y_train.parquet` | Training labels |
| `data/processed/y_test.parquet` | Test labels |
| `data/processed/blackspot_features.db` | SQLite feature store |
| `outputs/eda_report/*.png` | EDA charts (9 plots) |
| `outputs/maps/bengaluru_accidents.html` | Interactive Folium map |
| `outputs/logs/pipeline.log` | Full run log |

---

## Feature Columns

### Spatial
| Feature | Description |
|---------|-------------|
| `dist_to_nearest_junction` | Meters to nearest road junction |
| `num_junctions_500m` | Junction count within 500m |
| `road_risk_score` | Ordinal road type risk (1–5) |
| `accident_density_1km` | Historical accidents in 1km radius |
| `accident_density_500m` | Historical accidents in 500m radius |
| `nearest_blackspot_dist` | Meters to nearest known black spot |

### Temporal
| Feature | Description |
|---------|-------------|
| `hour_sin`, `hour_cos` | Cyclic hour encoding |
| `month_sin`, `month_cos` | Cyclic month encoding |
| `day_sin`, `day_cos` | Cyclic day-of-week encoding |
| `is_peak_hour` | 1 if 8–10am or 5–8pm |
| `is_night` | 1 if 10pm–5am |
| `is_weekend` | 1 if Saturday/Sunday |
| `is_monsoon` | 1 if June–September |
| `is_festival_month` | 1 if Oct/Nov/Jan (Dasara, Deepavali, Sankranti) |
| `days_since_epoch` | Days since 2019-01-01 (trend feature) |

### Environmental
| Feature | Description |
|---------|-------------|
| `weather_encoded` | Weather risk score (1=Clear → 5=Foggy/Night-Rainy) |
| `road_condition_encoded` | Road condition risk (1=Dry → 5=Slippery) |
| `light_condition_encoded` | Lighting risk (1=Daylight → 4=Dark) |

### Road
| Feature | Description |
|---------|-------------|
| `speed_limit` | Posted speed limit (km/h) |
| `vehicles_involved` | Number of vehicles in accident |

---

## Black Spot Definition

Following WHO / IRC (Indian Roads Congress) definition:

> A location is a **black spot** if **3 or more accidents** occurred within a
> **500m radius** in any **rolling 12-month window**.

Implementation uses a KD-tree for O(n log n) spatial querying.

---

## Known Bengaluru Black Spots (Ground Truth)

| Location | Severity |
|----------|----------|
| Silk Board Junction | CRITICAL |
| Marathahalli Bridge | CRITICAL |
| Outer Ring Road Bellandur | CRITICAL |
| Hebbal Flyover | HIGH |
| KR Puram Bridge | HIGH |
| Tin Factory Junction | HIGH |
| Madiwala Junction | HIGH |
| Tumkur Road NH4 | HIGH |
| Hosur Road Electronic City | HIGH |
| Old Madras Road KR Puram | HIGH |
| Sarjapur Road Junction | HIGH |
| Nagawara Junction | MEDIUM |
| Bannerghatta Road ORR | MEDIUM |
| Bellary Road Hebbal | MEDIUM |
| Mysore Road Kengeri | MEDIUM |

---

## Data Sources

| Source | URL | Notes |
|--------|-----|-------|
| data.gov.in | https://data.gov.in/catalog/road-accidents-india | State/district level CSVs |
| Kaggle India Accidents | https://www.kaggle.com/datasets/s3bubble/road-accident-data | Filter for Karnataka |
| NCRB | https://ncrb.gov.in/en/accidental-deaths-suicides-india | Annual report data |
| OpenStreetMap | Via osmnx | Road network (programmatic) |
| Bengaluru Traffic Police | https://www.bengalurutrafficpolice.gov.in/ | Annual black spot lists |

> **Note:** Real data requires manual download. The pipeline uses synthetic data
> by default (5000 records, statistically realistic for Bengaluru).

---

## Project Structure

```
data_pipeline/
├── data/
│   ├── raw/          # Input CSVs (accidents, weather, road network)
│   ├── interim/      # Cleaned intermediate Parquet files
│   ├── processed/    # Final ML-ready splits + SQLite DB
│   └── external/     # Kaggle / NCRB datasets
├── src/
│   ├── collection/   # Data ingestion + synthetic generator
│   ├── cleaning/     # Cleaning, validation, date normalization
│   ├── features/     # Spatial, temporal, environmental, road features
│   ├── preprocessing/# Encoding, scaling, splitting, SMOTE
│   ├── validation/   # Pydantic schemas + quality checks
│   ├── storage/      # Parquet + SQLite utilities
│   └── visualization/# EDA plots + Folium maps
├── tests/            # pytest test suite
├── notebooks/        # Jupyter EDA notebooks
├── outputs/          # EDA charts, maps, logs
├── pipeline.py       # CLI entrypoint
├── config.yaml       # Pipeline configuration
└── requirements.txt
```

---

## Configuration

Edit `config.yaml` to change:
- Bengaluru bounding box
- Black spot radius/threshold
- Balancing strategy (smote / smote_tomek / adasyn)
- Test year for temporal split
- Feature columns

---

## Next Steps (Phase 3 — ML Training)

The outputs of this pipeline feed directly into:
- `RandomForestClassifier` — baseline model
- `XGBoostClassifier` — gradient boosting
- `LogisticRegression` — interpretable baseline

Input: `data/processed/X_train.parquet` + `y_train.parquet`
