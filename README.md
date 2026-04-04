# COS30019 Assignment 2B

Traffic-Based Route Guidance System for SCATS traffic prediction and dynamic routing.

This repository includes:
- the Python backend for ML, prediction, graph updates, and route search
- a thin FastAPI wrapper in `webapi/`
- a React + Vite frontend in `frontend/`
- a CLI entry point in `main.py`

Important note:
- the repo already includes saved model files in `saved_models/`
- you do not need to retrain a model just to run the GUI
- the default and recommended GUI model is `lightgbm`

## Quick Start From A Fresh Clone

Follow these commands in order.

### 1. Clone the repo and enter it

```bash
git clone <your-github-repo-url>
cd COS30019-ASSIGNMENT-3
```

### 2. Check that Python and npm are available

```bash
python3 --version
npm --version
```

### 3. Create a virtual environment

```bash
python3 -m venv .venv
```

### 4. Upgrade pip

```bash
./.venv/bin/python -m pip install --upgrade pip
```

### 5. Install the Python dependencies needed to run the backend and GUI

```bash
./.venv/bin/pip install numpy pandas scikit-learn joblib lightgbm xlrd fastapi uvicorn
```

This is enough for the default web GUI flow with `lightgbm`.

### 6. Install the frontend dependencies

```bash
cd frontend
npm install
cd ..
```

### 7. Regenerate the default topology files

```bash
./.venv/bin/python scripts/prepare_real_topology.py
```

### 8. Run the backend smoke test

```bash
./.venv/bin/python -m scripts.backend_smoke_test
```

If this passes, the backend is ready.

### 9. Start the backend API in Terminal 1

```bash
./.venv/bin/python -m uvicorn webapi.server:app --reload --host 127.0.0.1 --port 8000
```

Leave that terminal running.

### 10. Start the frontend in Terminal 2

```bash
cd frontend
npm run dev
```

### 11. Open the GUI in your browser

```text
http://127.0.0.1:5173
```

### 12. Use the GUI

In the web GUI:
- enter an origin SCATS site ID
- enter a destination SCATS site ID
- keep the model as `lightgbm` unless you have installed extra dependencies
- choose `top-k` from 1 to 5
- click the route button

Good first test:
- origin: `2000`
- destination: `3002`
- model: `lightgbm`
- top-k: `1` or `5`

## If You Want To Use LSTM Or GRU Later

The GUI and API default to `lightgbm`. If you also want the `lstm` or `gru` models, install TensorFlow:

```bash
./.venv/bin/pip install tensorflow
```

Without TensorFlow, keep using `lightgbm`.

## Useful Commands After Setup

### Run the CLI directly

Single best route:

```bash
./.venv/bin/python main.py --origin 2000 --destination 3002 --model lightgbm
```

Top-k routes:

```bash
./.venv/bin/python main.py --origin 2000 --destination 3002 --model lightgbm --top-k 5
```

### Run the model comparison script

```bash
./.venv/bin/python compare_models.py
```

Save models while comparing:

```bash
./.venv/bin/python compare_models.py --save-models
```

### Load the saved default prediction bundle

```bash
./.venv/bin/python -c "from machine_learning.common.site_flow_service import load_default_prediction_bundle; bundle = load_default_prediction_bundle(); print(bundle['model_type'], bundle['window_size'])"
```

## API Endpoints

The FastAPI layer is thin and reuses the existing backend route pipeline through:
- `machine_learning.common.cli_route_service.compute_terminal_routes`

Available endpoints:
- `GET /api/health`
- `GET /api/config`
- `POST /api/routes/compute`

Example request:

```bash
curl -X POST http://127.0.0.1:8000/api/routes/compute \
  -H "Content-Type: application/json" \
  -d '{"origin": 2000, "destination": 3002, "model": "lightgbm", "top_k": 3}'
```

## Data Sources

- ML training and prediction windows use `data/scats_data_october_2006.xls`
- default routing uses:
  - `data/boroondara_locations.csv`
  - `data/boroondara_connectivity.csv`
- those routing CSVs are generated from:
  - `data/Traffic_Count_Locations_with_LONG_LAT.csv`
  - the 40 SCATS site IDs present in the traffic dataset
- `data/SCATSSiteListingSpreadsheet_VicRoads.xls/.xlsx` is not used directly in the active routing path

## Project Structure

```text
machine_learning/   Core ML pipeline, prediction, graph, problem, and route services
utils/              Shared parsing, graph, search, and utility helpers
webapi/             Thin FastAPI wrapper
frontend/           React + Vite frontend
scripts/            Topology generation and backend smoke tests
data/               Traffic data and topology inputs
main.py             CLI entry point
compare_models.py   Model comparison entry point
```
