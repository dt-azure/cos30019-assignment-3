# COS30019 Assignment 2B — Traffic-Based Route Guidance System

Traffic-Based Route Guidance System for SCATS traffic prediction and dynamic routing.

This project includes:
- a Python backend for machine learning, traffic prediction, graph updates, and route search
- a thin FastAPI API wrapper in `webapi/`
- a React + Vite frontend in `dashboard/`
- a CLI entry point in `main.py`

> Important:
> - The repository already includes saved model files in `saved_models/`
> - You do **not** need to retrain a model to run the web app or CLI
> - The default and recommended model is `lightgbm`

---

## Tech Stack

### Backend
- FastAPI
- Uvicorn
- scikit-learn
- LightGBM
- pandas
- numpy

### Frontend
- Vite
- npm
- Leaflet
- OSRM API

---

## Prerequisites

Make sure you have the following installed:

- **Python 3.13+**  
  Download: https://www.python.org/downloads/

- **Node.js** (includes npm)  
  Download: https://nodejs.org/en/download/current

You can verify the installation with:

```bash
python3 --version
npm --version
```

---

## Project Structure

```text
COS30019-ASSIGNMENT-3/
│
├── data/                       # Traffic data and topology inputs
├── machine_learning/           # Core ML pipeline, prediction, graph, and route services
├── utils/                      # Shared parsing, graph, search, and helper utilities
├── webapi/                     # FastAPI backend wrapper
├── dashboard/                  # React + Vite frontend
├── scripts/                    # Utility scripts and backend smoke tests
├── saved_models/               # Pretrained / saved models
├── main.py                     # CLI entry point
└── compare_models.py           # Model comparison script
```

---

## Setup Guide (From Fresh Clone to Running the Full App)

This section is for a new user who has just cloned the repository and wants to set everything up from scratch.

### 1. Clone the repository

```bash
git clone <your-github-repo-url>
cd COS30019-ASSIGNMENT-3
```

---

### 2. Create a Python virtual environment

It is recommended to use a virtual environment for the backend.

#### On macOS / Linux

```bash
python3 -m venv .venv
```

Activate it:

```bash
source .venv/bin/activate
```

#### On Windows (Command Prompt)

```bash
python -m venv .venv
.venv\Scripts\activate
```

#### On Windows (PowerShell)

```bash
python -m venv .venv
.venv\Scripts\Activate.ps1
```

---

### 3. Install backend dependencies

Upgrade pip first:

```bash
python -m pip install --upgrade pip
```

Then install the required backend packages:

```bash
pip install numpy pandas scikit-learn joblib lightgbm xlrd fastapi uvicorn
```

This is enough for the default backend and GUI flow using `lightgbm`.

> Optional:
> If you want to use the `lstm` or `gru` models later, install TensorFlow:
>
> ```bash
> pip install tensorflow
> ```
>
> Otherwise, keep using `lightgbm`.

---

### 4. Prepare the topology files

Run:

```bash
python scripts/prepare_real_topology.py
```

This regenerates the default routing topology files used by the system.

---

### 5. Run the backend smoke test

Before launching the app, check that the backend is working correctly:

```bash
python -m scripts.backend_smoke_test
```

Expected output:

```text
All backend smoke checks passed.
```

If this passes, the backend is ready.

---

### 6. Start the backend server

Run:

```bash
uvicorn webapi.server:app --reload --host 127.0.0.1 --port 8000
```

Expected output:

```text
Uvicorn running on http://127.0.0.1:8000
```

Leave this terminal running.

---

### 7. Test the backend API

Open this URL in your browser:

```text
http://127.0.0.1:8000/api/health
```

Expected response:

```json
{"status": "ok"}
```

You can also open the FastAPI docs here:

```text
http://127.0.0.1:8000/docs
```

---

### 8. Install frontend dependencies

Open a **new terminal**, then run:

```bash
cd dashboard
npm install
```

---

### 9. Start the frontend

Still inside the `dashboard` folder, run:

```bash
npm run dev
```

Expected output:

```text
Local: http://localhost:5173/
```

---

### 10. Open the web app

Open this in your browser:

```text
http://127.0.0.1:5173
```

---

### 11. First GUI test

In the web interface:

- enter origin SCATS site ID: `2000`
- enter destination SCATS site ID: `3002`
- keep model as `lightgbm`
- choose top-k as `1` or `5`
- click the route button

This is the recommended first test for checking that the full stack works correctly.

---

## Testing the CLI

This section is specifically for testing the command-line interface in `main.py`.

Make sure:
- the virtual environment is activated
- backend dependencies are installed
- topology files have already been prepared

### 1. Run the CLI for a single best route

```bash
python main.py --origin 2000 --destination 3002 --model lightgbm
```

This should compute and display the best route from SCATS site `2000` to `3002` using the `lightgbm` model.

---

### 2. Run the CLI for top-k routes

```bash
python main.py --origin 2000 --destination 3002 --model lightgbm --top-k 5
```

This should return the top 5 route options.

---

### 3. Recommended CLI test cases

#### Test case 1: Single best route

```bash
python main.py --origin 2000 --destination 3002 --model lightgbm
```

#### Test case 2: Top 5 routes

```bash
python main.py --origin 2000 --destination 3002 --model lightgbm --top-k 5
```

#### Test case 3: Different origin/destination pair

```bash
python main.py --origin 2200 --destination 4034 --model lightgbm --top-k 3
```

> Note:
> Use valid SCATS site IDs that exist in the dataset and generated topology files.

---

### 4. What to check when testing CLI

When the CLI runs successfully, verify that:
- the command completes without crashing
- a route is returned
- origin and destination are processed correctly
- changing `top-k` changes the number of route options
- the model argument is accepted correctly

---

## Backend Testing

### Backend smoke test

```bash
python -m scripts.backend_smoke_test
```

Expected output:

```text
All backend smoke checks passed.
```

### Health check endpoint

Open in browser:

```text
http://127.0.0.1:8000/api/health
```

Expected response:

```json
{"status": "ok"}
```

### API docs

Open in browser:

```text
http://127.0.0.1:8000/docs
```

---

## API Endpoints

The FastAPI layer reuses the existing backend route pipeline through:

- `machine_learning.common.cli_route_service.compute_terminal_routes`

Available endpoints:
- `GET /api/health`
- `GET /api/config`
- `POST /api/routes/compute`

### Example request

```bash
curl -X POST http://127.0.0.1:8000/api/routes/compute \
  -H "Content-Type: application/json" \
  -d '{"origin": 2000, "destination": 3002, "model": "lightgbm", "top_k": 3}'
```

---

## Useful Commands

### Compare models

```bash
python compare_models.py
```

Save models while comparing:

```bash
python compare_models.py --save-models
```

### Load the saved default prediction bundle

```bash
python -c "from machine_learning.common.site_flow_service import load_default_prediction_bundle; bundle = load_default_prediction_bundle(); print(bundle['model_type'], bundle['window_size'])"
```

---

## Data Sources

- ML training and prediction windows use `data/scats_data_october_2006.xls`
- default routing uses:
  - `data/boroondara_locations.csv`
  - `data/boroondara_connectivity.csv`
- those routing CSVs are generated from:
  - `data/Traffic_Count_Locations_with_LONG_LAT.csv`
  - the 40 SCATS site IDs present in the traffic dataset
- `data/SCATSSiteListingSpreadsheet_VicRoads.xls/.xlsx` is not used directly in the active routing path

---

## Notes

- You do not need to retrain the models to run the project.
- For most users, `lightgbm` is the best default choice.
- If TensorFlow is not installed, avoid selecting `lstm` or `gru`.
- Start the backend before using the frontend.
- Use two terminals:
  - Terminal 1 for backend
  - Terminal 2 for frontend
