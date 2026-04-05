# Execution Guide — COS30019 Assignment 3

> Traffic-Based Route Guidance System

This guide covers everything from zero to running the application. Follow the steps in order.

---

## Table of Contents

| Step | Description |
|------|-------------|
| [1](#step-1-install-prerequisites) | Install Prerequisites (Python + Node.js) |
| [2](#step-2-get-the-project) | Get the Project |
| [3](#step-3-create--activate-virtual-environment) | Create & Activate Virtual Environment |
| [4](#step-4-install-python-dependencies) | Install Python Dependencies (requirements.txt) |
| [5](#step-5-install-frontend-dependencies) | Install Frontend Dependencies |
| [6](#step-6-train--save-ml-models) | Train & Save ML Models |
| [7](#step-7-regenerate-default-topology-files) | Regenerate Default Topology Files |
| [8](#step-8-run-backend-smoke-tests) | Run Backend Smoke Tests |
| [9](#step-9-run-comprehensive-test-suite) | Run Comprehensive Test Suite (20 tests) |
| [10](#step-10-run-the-web-application) | Run the Web Application |
| [11](#step-11-open-the-browser) | Open the Browser |
| [12](#cli-commands-no-browser) | CLI Commands (No Browser) |
| [13](#optional-use-lstm-or-gru-models) | Optional: Use LSTM or GRU Models |
| [14](#troubleshooting) | Troubleshooting |
| [15](#stopping-the-application) | Stopping the Application |

---

## Step 1: Install Prerequisites

You need **Python** and **Node.js** on your machine.

### 1.1 Python 3.12+

Download from: https://www.python.org/downloads/

During installation, **check the box** "Add Python to PATH".

Verify:
```powershell
python --version
```

### 1.2 Node.js (for the frontend web interface)

Open PowerShell and run:
```powershell
winget install OpenJS.NodeJS.LTS
```

After installation, **close PowerShell and reopen it**, then verify:
```powershell
node --version
npm --version
```

You should see version numbers (e.g., `v20.x.x` and `10.x.x`).

> **If `winget` doesn't work:** Download from https://nodejs.org (LTS version), install, then restart your computer.

---

## Step 2: Get the Project

1. Clone or download the project to a folder, e.g.:
   ```
   C:\Users\YourName\cos30019-assignment-3
   ```
2. Open PowerShell and navigate to the project root:
   ```powershell
   cd C:\Users\YourName\cos30019-assignment-3
   ```
   *(Replace `YourName` with your actual Windows username)*

---

## Step 3: Create & Activate Virtual Environment

> **Skip** if the `.venv` folder already exists.

Create a new virtual environment:
```powershell
python -m venv .venv
```

Activate it:
```powershell
.\.venv\Scripts\Activate.ps1
```


```MacOs(terminal)
source .venv/bin/activate
```

You should see `(.venv)` at the start of your prompt.

> **If you get an execution policy error**, run this first:
> ```powershell
> Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
> ```

---

## Step 4: Install Python Dependencies

Install all required packages from `requirements.txt`:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

This installs: **pandas, numpy, lightgbm, scikit-learn, joblib, fastapi, pydantic, uvicorn, osmnx, tqdm**.

Wait until you see `Successfully installed ...` and your cursor returns.

> **Note:** `tensorflow` is NOT included. If you want LSTM/GRU models, please go to ([Step 13](#use-lstm-and-gru-models)).

---

## Step 5: Install Frontend Dependencies

Run this **once** when you first get the project:

```powershell
cd frontend
npm install
cd ..
```

Wait for the installation to complete (you'll see a summary of packages installed).

---

## Step 6: Train & Save ML Models

**Note:** If you see the `saved_models/` folder already has  `lstm.keras` or `gru.keras`, please skip this step.

The backend needs trained models in the `saved_models/` folder to work. This step trains the LightGBM model and saves it.

```powershell
.\.venv\Scripts\python.exe compare_models.py --models lightgbm --save-models
```

You should see output like:
```
========== LIGHTGBM MODEL ==========
Train X shape: (257368, 4)
Test X shape:  (80500, 4)
...

========== MODEL COMPARISON ==========
Model    | Train Loss | Val Loss | MAE     | MSE      | RMSE    | Time (s)
---------+------------+----------+---------+----------+---------+---------
LightGBM | N/A        | N/A      | 14.0165 | 449.2875 | 21.1964 | 0.42
```

This creates the `saved_models/` folder with:
- `lightgbm.pkl` — the trained model
- `lightgbm_metadata.pkl` — metadata (scalers, config, etc.)

---

## Step 7: Regenerate Default Topology Files

This generates the road network connectivity CSV files that the routing system uses:

```powershell
.\.venv\Scripts\python.exe scripts/prepare_real_topology.py
```

Expected output:
```
Wrote 40 locations to data/boroondara_locations_snapped.csv
Wrote XXX directed edges to data/boroondara_connectivity.csv
```

This creates/updates:
- `data/boroondara_locations_snapped.csv` — 40 SCATS site coordinates
- `data/boroondara_connectivity.csv` — road network edges with distances

---

## Step 8: Run Backend Smoke Tests

Runs **11 test cases** that verify the backend pipeline works correctly:

```powershell
.\.venv\Scripts\python.exe -m scripts.backend_smoke_test
```

Expected output — all should show `PASS`:
```
PASS - load saved model
PASS - predict all sites
PASS - real default topology files
PASS - build dynamic graph
PASS - build dynamic routing problem
PASS - solve single best route
PASS - solve top-k routes
PASS - invalid origin handling
PASS - invalid destination handling
PASS - origin equals destination handling
PASS - no-route handling
All backend smoke checks passed.
```

| # | Test | What It Checks |
|---|------|----------------|
| 1 | Load saved model | Model loads with correct type and metadata |
| 2 | Predict all sites | All 40 SCATS sites get predictions |
| 3 | Real topology files | Default CSVs exist and contain data |
| 4 | Build dynamic graph | Graph builds with ML-predicted edge costs |
| 5 | Build routing problem | Problem initializes with correct origin/goals |
| 6 | Single best route | Returns correct shortest path |
| 7 | Top-k routes | Returns multiple unique routes sorted by cost |
| 8 | Invalid origin | Raises `KeyError` for non-existent origin |
| 9 | Invalid destination | Raises `KeyError` for non-existent destination |
| 10 | Origin = Destination | Raises `ValueError` when same |
| 11 | No route found | Raises `ValueError` when unreachable |

---

## Step 9: Run Comprehensive Test Suite

Runs **20 test cases** covering 3 categories required by the assignment:

- **(A) ML Model Testing** — prediction quality under different traffic scenarios
- **(B) Software Testing** — system functionality and error handling
- **(C) Integration Testing** — ML + Search working together end-to-end

```powershell
.\.venv\Scripts\python.exe scripts/comprehensive_test.py
```

Expected output:
```
======================================================================
  COMPREHENSIVE TEST SUITE — COS30019 Assignment 3
======================================================================

[A] ML MODEL TESTING
----------------------------------------------------------------------
  PASS [TC01] Normal day prediction
         Predicted=34.04, Actual=34.00, Error=0.04 (0.1%)
  PASS [TC02] Peak hour prediction
         Peak predicted=363.28, Above median=132.00
  PASS [TC03] Off-peak prediction
         Off-peak predicted=6.65, Below median=132.00
  PASS [TC04] Model predicts new data
         All 5 sites predicted successfully
  PASS [TC05] Overall model accuracy
         MAE=17.42, RMSE=24.59, MAPE=32.8%
  PASS [TC06] Prediction consistency
         5 runs all returned 307.0491 (deterministic OK)

[B] SOFTWARE TESTING
----------------------------------------------------------------------
  PASS [TC07] Load saved model
  PASS [TC08] Predict all sites
  PASS [TC09] Build dynamic graph
  PASS [TC10] Valid route returns 1-5 paths
  PASS [TC11] Origin = Destination handling
  PASS [TC12] Invalid origin handling
  PASS [TC13] Invalid destination handling
  PASS [TC14] No route found handling
  PASS [TC15] Single best route correctness

[C] INTEGRATION TESTING (ML + Search)
----------------------------------------------------------------------
  PASS [TC16] Route uses ML travel time
  PASS [TC17] Route changes with traffic
  PASS [TC18] End-to-end pipeline
  PASS [TC19] Multiple O-D pairs
  PASS [TC20] Search algorithm correctness

======================================================================
  TOTAL: 20 tests | PASS: 20 | FAIL: 0
======================================================================
```

Results are automatically saved to `test_results.txt` for documentation.

See `TESTING_REPORT.md` for the full detailed report with tables, metrics, and analysis.

---

## Step 10: Run the Web Application

The app has 2 parts that must run **at the same time**. Open **2 PowerShell windows**.

### Window 1 — Backend (FastAPI Server)

1. Open a new PowerShell window
2. Navigate to the project folder:
   ```powershell
   cd C:\Users\YourName\cos30019-assignment-3
   ```
3. Start the backend server:
   ```powershell
   .\.venv\Scripts\python.exe -m uvicorn webapi.server:app --reload --host 127.0.0.1 --port 8000
   ```
4. You should see:
   ```
   INFO: Uvicorn running on http://127.0.0.1:8000/docs
   ```
5. **Leave this window open.**

### Window 2 — Frontend (React + Vite)

1. Open another new PowerShell window (keep Window 1 running)
2. Navigate to the frontend folder:
   ```powershell
   cd C:\Users\YourName\cos30019-assignment-3\frontend
   ```
3. Start the dev server:
   ```powershell
   npm run dev
   ```
4. You should see:
   ```
   VITE v6.x.x  ready in xxx ms
   Local:   http://localhost:5173/
   ```
5. **Leave this window open too.**

---

## Step 11: Open the Browser

1. Open your browser (Chrome, Edge, Firefox)
2. Go to: **http://localhost:5173/**
3. You should see the Traffic Route Guidance System home page

### How to Use

1. Click **Start Route Planning** or go to **Map Prediction**
2. Select **Origin** (e.g., `2000`)
3. Select **Destination** (e.g., `3002`)
4. Choose **Model** (`lightgbm` recommended)
5. Choose **Top-K** (1–5 route options)
6. Click **Find Routes**
7. Click any route to see it highlighted on the map with turn-by-turn directions

---

## CLI Commands (No Browser)

Get route results directly in the terminal:

### Single best route:
```powershell
.\.venv\Scripts\python.exe main.py --origin 2000 --destination 3002 --model lightgbm
```

### Top-k routes:
```powershell
.\.venv\Scripts\python.exe main.py --origin 2000 --destination 3002 --model lightgbm --top-k 5
```

---

## Use LSTM and GRU Models
### 1. Install TensorFlow
```powershell
.\.venv\Scripts\python.exe -m pip install tensorflow
```

### 2. Train all 3 models
```powershell
.\.venv\Scripts\python.exe compare_models.py --save-models
```

### 3. Use them in CLI or web UI
```powershell
.\.venv\Scripts\python.exe main.py --origin 2000 --destination 3002 --model lstm
.\.venv\Scripts\python.exe main.py --origin 2000 --destination 3002 --model gru
```

> You can refer back [Go to Step 5](#step-5-install-frontend-dependencies)

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| `python` is not recognized | Install Python, add to PATH, restart PowerShell |
| `npm` is not recognized | Install Node.js (Step 1), close and reopen PowerShell |
| `Activate.ps1` cannot be loaded | Run `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser` |
| `ModuleNotFoundError: No module named 'uvicorn'` | Run Step 4: `pip install -r requirements.txt` |
| `No module named 'tensorflow'` | LightGBM works without it. Only needed for LSTM/GRU |
| `saved_models\lightgbm_metadata.pkl` not found | Run Step 6 to train and save models |
| `data/boroondara_locations_snapped.csv` not found | Run Step 7 to regenerate topology files |
| Web page is blank/white | Make sure the Backend (Window 1) is still running |
| Port 8000 already in use | Close other programs using port 8000, or restart computer |
| "No route found" | Only select valid SCATS site IDs from the dropdown |
| Test fails with `FAIL` | Ensure Steps 4–7 completed successfully, then re-run tests |

---

## Stopping the Application

1. Go to each PowerShell window running the backend/frontend
2. Press **Ctrl + C** to stop the server
3. Close the windows

---

## Quick Reference — All Commands

| Task | Command |
|------|---------|
| Activate venv | `.\.venv\Scripts\Activate.ps1` |
| Install Python deps | `.\.venv\Scripts\python.exe -m pip install -r requirements.txt` |
| Install frontend deps | `cd frontend && npm install && cd ..` |
| Train models | `.\.venv\Scripts\python.exe compare_models.py --models lightgbm --save-models` |
| Regenerate topology | `.\.venv\Scripts\python.exe scripts/prepare_real_topology.py` |
| Backend smoke tests (11) | `.\.venv\Scripts\python.exe -m scripts.backend_smoke_test` |
| Comprehensive tests (20) | `.\.venv\Scripts\python.exe scripts/comprehensive_test.py` |
| Start backend | `.\.venv\Scripts\python.exe -m uvicorn webapi.server:app --reload --host 127.0.0.1 --port 8000` |
| Start frontend | `cd frontend && npm run dev` |
| CLI route (single) | `.\.venv\Scripts\python.exe main.py --origin 2000 --destination 3002 --model lightgbm` |
| CLI route (top-k) | `.\.venv\Scripts\python.exe main.py --origin 2000 --destination 3002 --model lightgbm --top-k 5` |
| Install TensorFlow | `.\.venv\Scripts\python.exe -m pip install tensorflow` |
