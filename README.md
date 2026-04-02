# COS30019 Assignment 2B

Traffic-Based Route Guidance System for SCATS traffic prediction and dynamic routing.

This repo keeps everything in one place:
- Python backend for ML, prediction, graph updates, and route search
- FastAPI web API as a thin wrapper over the existing backend services
- React + Vite frontend for a web-based GUI
- `main.py` as the existing CLI entry point

## Project Structure

```text
machine_learning/   Core ML pipeline, prediction, graph, problem, and route services
utils/              Shared parsing, graph, search, and utility helpers
webapi/             Thin FastAPI wrapper over the backend
frontend/           React + Vite web UI
scripts/            Topology generation and backend smoke tests
data/               Traffic data and topology CSV inputs
main.py             CLI route entry point
compare_models.py   Model comparison entry point
```

## Data Sources

- ML training and prediction windows use `data/scats_data_october_2006.xls`
- Default routing uses:
  - `data/boroondara_locations.csv`
  - `data/boroondara_connectivity.csv`
- Those routing CSVs are generated from:
  - `data/Traffic_Count_Locations_with_LONG_LAT.csv`
  - the 40 SCATS site IDs present in the traffic dataset
- `data/SCATSSiteListingSpreadsheet_VicRoads.xls/.xlsx` is present in the repo but is not used directly in the active routing pipeline

If you need to regenerate the default topology files:

```bash
./.venv/bin/python scripts/prepare_real_topology.py
```

## Backend Setup

This project assumes you are using the existing local virtual environment in `.venv`.

Install the web API dependencies if they are not already installed:

```bash
./.venv/bin/pip install fastapi uvicorn
```

## Frontend Setup

Install the React frontend dependencies:

```bash
cd frontend
npm install
```

## ML Workflow

### Compare Models

Run the current model comparison:

```bash
./.venv/bin/python compare_models.py
```

Save trained model artifacts while comparing:

```bash
./.venv/bin/python compare_models.py --save-models
```

### Save And Load Models

Train and save the default LightGBM bundle:

```bash
./.venv/bin/python -c "from machine_learning.lightgbm import train_lightgbm; bundle, results = train_lightgbm(save=True); print(results)"
```

Load the saved default prediction bundle:

```bash
./.venv/bin/python -c "from machine_learning.common.site_flow_service import load_default_prediction_bundle; bundle = load_default_prediction_bundle(); print(bundle['model_type'], bundle['window_size'])"
```

## Run Routing From The CLI

Single best route:

```bash
./.venv/bin/python main.py --origin 2000 --destination 3002 --model lightgbm
```

Top-k routes, up to 5:

```bash
./.venv/bin/python main.py --origin 2000 --destination 3002 --model lightgbm --top-k 5
```

The CLI keeps the existing validation behavior for:
- invalid origin
- invalid destination
- origin equals destination
- no route found

## Run The Backend API

Start the FastAPI server from the repo root:

```bash
./.venv/bin/python -m uvicorn webapi.server:app --reload --host 127.0.0.1 --port 8000
```

The API is a thin wrapper over the backend and reuses:
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

## Run The Web Frontend

Start the frontend development server:

```bash
cd frontend
npm run dev
```

By default, the frontend runs on:

```text
http://127.0.0.1:5173
```

The frontend proxies `/api` requests to:

```text
http://127.0.0.1:8000
```

Recommended local workflow:

1. Start the FastAPI server
2. Start the Vite frontend
3. Open the frontend in the browser
4. Enter origin, destination, model, and top-k
5. Submit the route request

## Run Backend Smoke Checks

Run the non-GUI backend validation sweep:

```bash
./.venv/bin/python -m scripts.backend_smoke_test
```

This smoke test covers:
- saved model loading
- all-site prediction
- dynamic graph construction
- dynamic problem construction
- single-route solving
- top-k route solving
- invalid origin handling
- invalid destination handling
- origin equals destination validation
- no-route handling

## End-To-End Demo Commands

Start backend API:

```bash
./.venv/bin/python -m uvicorn webapi.server:app --reload --host 127.0.0.1 --port 8000
```

Start frontend:

```bash
cd frontend
npm run dev
```

Run CLI directly:

```bash
./.venv/bin/python main.py --origin 2000 --destination 3002 --model lightgbm --top-k 5
```
