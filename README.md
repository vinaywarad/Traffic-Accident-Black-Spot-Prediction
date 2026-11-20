# Traffic Accident Black Spot Prediction

A machine-learning and web application project for exploring accident-prone locations in Bengaluru. The repository brings together a Python data pipeline, model-training and evaluation modules, a FastAPI backend, and a React dashboard for viewing accident patterns and black-spot risk.

> **Data and evaluation note:** The included data pipeline generates synthetic Bengaluru-style accident records by default. Synthetic records are useful for demonstrating and testing the workflow, but they are not verified official accident records. Model metrics produced from synthetic data must not be presented as real-world performance. Validate with a documented real-world dataset before making operational or safety claims.

## Project objective

To build an end-to-end workflow that prepares road-accident data, derives spatial and temporal features, trains classification models, exposes prediction and analytics endpoints, and presents the results through an interactive dashboard. The intended use is exploratory analysis and decision support; predictions are not a substitute for official road-safety investigations.

## Key components

- **Data pipeline:** collection helpers, synthetic-data generation, cleaning, validation, feature engineering, preprocessing, and visualization.
- **Machine learning:** Logistic Regression, Random Forest, XGBoost, and LightGBM training modules, evaluation utilities, threshold optimization, and SHAP-based explainability.
- **Backend API:** FastAPI routes for health checks, predictions, black spots, analytics, and model information.
- **Frontend dashboard:** React + Vite interface with dashboard, map, analytics, predictions, upload, and settings pages.
- **Tests:** pytest test suites are included in the pipeline, model, and backend components.

## Methodology

1. **Data collection** – use the included synthetic generator by default; loaders are also provided for external road-network and accident-related inputs.
2. **Data cleaning and validation** – normalize dates, validate coordinates, remove/handle invalid or duplicate records, and check data quality.
3. **Exploratory analysis** – inspect accident distributions and visualize spatial and temporal patterns.
4. **Feature engineering** – derive spatial, temporal, road-related, and environmental features.
5. **Preprocessing** – encode categorical variables, scale numerical features where configured, split data, and apply the configured class-balancing method.
6. **Model training** – train the configured classification models and optionally tune hyperparameters.
7. **Evaluation and explainability** – compare model metrics and generate feature explanations with SHAP where configured.
8. **API and dashboard integration** – expose backend endpoints and present maps, charts, and prediction information in the frontend.

## Technology stack

| Area | Technologies |
|---|---|
| Programming languages | Python, JavaScript, HTML, CSS |
| Data processing | Pandas, NumPy, SciPy |
| Geospatial processing | GeoPandas, OSMnx, Shapely, Folium |
| Machine learning | scikit-learn, XGBoost, LightGBM, imbalanced-learn |
| Explainability and experiment tracking | SHAP, MLflow, Optuna |
| Backend | FastAPI, Pydantic, Uvicorn |
| Frontend | React, Vite, React Router, Zustand, TanStack Query |
| Maps and charts | Leaflet / React-Leaflet, Recharts |
| Storage and formats | SQLite / SQLAlchemy, Parquet / PyArrow |
| Testing and deployment support | pytest, Docker, Docker Compose |

## Repository structure

```text
.
├── data_pipeline/                 # Data collection, cleaning and feature pipeline
│   ├── src/
│   ├── tests/
│   ├── pipeline.py
│   ├── config.yaml
│   └── requirements.txt
├── ml_models/                     # Model training, evaluation and explainability
│   ├── src/
│   ├── tests/
│   ├── train.py
│   ├── evaluate.py
│   ├── explain.py
│   └── requirements.txt
├── backend/                       # FastAPI application and API tests
│   ├── app/
│   ├── tests/
│   ├── Dockerfile
│   └── requirements.txt
├── traffic-blackspot-frontend/    # React + Vite frontend
│   ├── src/
│   ├── public/
│   └── package.json
└── README.md
```

## Getting started

The project is split into separate components. Install dependencies in the component you intend to run. Commands below are starting points; the complete end-to-end workflow depends on generating/preparing data and exporting a compatible model before running prediction endpoints.

### 1. Data pipeline

```bash
cd data_pipeline
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
python pipeline.py --stage all
```

The pipeline README in `data_pipeline/README.md` documents individual stages and expected generated outputs. By default, the included generator creates synthetic records. Review `config.yaml` before running.

### 2. Train and evaluate machine-learning models

After the pipeline has generated the train/test files expected by the model loader:

```bash
cd ../ml_models
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
python train.py --model all
```

Optional flags documented in `ml_models/train.py` include `--tune`, `--cv`, and `--export`. Review the configuration and generated data before training. The backend expects model artifacts and metadata at the paths configured for it; these artifacts are not included in this repository snapshot.

### 3. Backend API

```bash
cd ../backend
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

If you change the API configuration, update your local `.env` file. Do not commit `.env` or credentials. API documentation is typically available at `http://127.0.0.1:8000/docs` while the local server is running.

### 4. Frontend dashboard

Open a separate terminal:

```bash
cd traffic-blackspot-frontend
npm install
npm run dev
```

Configure the frontend API base URL using the environment variable expected by the frontend source. Use a local environment file for machine-specific values and do not commit secrets.

## Tests

Run component tests from their respective folders after installing dependencies:

```bash
cd data_pipeline && pytest tests/ -v
cd ../ml_models && pytest tests/ -v
cd ../backend && pytest tests/ -v
```

## Data, model artifacts, and limitations

- The default pipeline includes a synthetic data generator. Clearly label generated records as synthetic.
- This repository snapshot does not include a verified official accident dataset or exported trained model artifacts.
- A model-comparison CSV is present under `ml_models/outputs/reports/`. Treat its values as an existing project artifact only; reproduce the experiment and verify the data split and evaluation process before reporting metrics in a resume, presentation, or production context.
- Do not upload private datasets, API keys, passwords, local `.env` files, or large generated artifacts.
- Geospatial results and black-spot definitions should be checked against the applicable official road-safety standards and validated data before real-world use.

## Future improvements

- Add a clearly licensed and documented real-world accident dataset.
- Re-run training and evaluation using a leakage-safe validation strategy on verified data.
- Add dashboard screenshots and a reproducible demo dataset.
- Document model artifact generation and provide a complete local end-to-end setup guide.
- Deploy the API and frontend with appropriate security, monitoring, and data governance.

## Author

**Vinay Warad**  
B.E. – Computer Science and Engineering (Data Science)  
Interested in Data Analytics, Data Science, and Machine Learning.

---

*Academic project for learning and demonstration. Not intended for emergency response or standalone traffic-safety decisions.*
