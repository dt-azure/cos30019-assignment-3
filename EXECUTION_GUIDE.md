# Execution Guide — COS30019 Assignment 3

This guide is written for beginners. Follow the steps one by one.

---

## Table of Contents

1. [Install Required Software](#step-1-install-required-software)
2. [Get the Project](#step-2-get-the-project)
3. [Create Virtual Environment (Fresh Clone Only)](#step-3-create-virtual-environment-fresh-clone-only)
4. [Install Backend Dependencies](#step-4-install-backend-dependencies)
5. [Install Frontend Dependencies](#step-5-install-frontend-dependencies)
6. [Train & Compare Models](#step-6-train--compare-models)
7. [Regenerate Default Topology Files](#step-7-regenerate-default-topology-files)
8. [Run Backend Tests (Smoke Tests)](#step-8-run-backend-tests-smoke-tests)
9. [Run the Application](#step-9-run-the-application)
10. [Open the Browser](#step-10-open-the-browser)
11. [How to Use the Web Application](#how-to-use-the-web-application)
12. [Run from Command Line (No Browser)](#run-from-command-line-no-browser)
13. [Optional: Use LSTM or GRU Models](#optional-use-lstm-or-gru-models)
14. [Common Problems and Fixes](#common-problems-and-fixes)
15. [How to Stop the Application](#how-to-stop-the-application)

---

## Step 1: Install Required Software

You need 2 things on your computer:

### 1. Python 3.13

Download from https://www.python.org/downloads/

During installation, **check the box** "Add Python to PATH".

### 2. Node.js (for the Web interface)

Open **PowerShell** and run this command to install automatically:

```powershell
winget install OpenJS.NodeJS.LTS
```

After installation, **close PowerShell and reopen it** so the system recognizes the new commands.

Verify the installation:

```powershell
node --version
npm --version
```

If you see version numbers (e.g., `v20.x.x` and `10.x.x`), you're good to go.

> **If `winget` doesn't work:** Download Node.js from https://nodejs.org (green LTS button), install it, then restart your computer.

---

## Step 2: Get the Project

1. Download the project `.zip` file from GitHub (or clone it if you have Git).
2. Extract it to a folder, for example: `C:\Users\YourName\cos30019-assignment-3`
3. Open **PowerShell** and navigate to the extracted folder:

   ```powershell
   cd C:\Users\YourName\cos30019-assignment-3
   ```

   *(Replace `YourName` with your actual Windows username)*

---

## Step 3: Create Virtual Environment (Fresh Clone Only)

> **Skip this step** if the `.venv` folder already exists in the project.

If you cloned the repo and there is no `.venv` folder, create one:

```powershell
python -m venv .venv
```

Activate it:

```powershell
.\.venv\Scripts\Activate.ps1
```

You should see `(.venv)` at the start of your prompt.

> **If activation is blocked by execution policy**, run this first:
>
> ```powershell
> Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
> ```

---

## Step 4: Install Backend Dependencies

Install all Python packages from `requirements.txt`:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

Wait until you see `Successfully installed ...` and your cursor returns.

> **Note:** `tensorflow` is **not** included by default. See [Optional: Use LSTM or GRU Models](#optional-use-lstm-or-gru-models) if you need it.

---

## Step 5: Install Frontend Dependencies

Run this command **only once** when you first get the project:

```powershell
cd frontend
npm install
cd ..
```

You'll see text scrolling as packages are downloaded. Wait until your cursor appears again.

---

## Step 6: Train & Compare Models

This step trains the AI models and saves them to the `saved_models/` folder. The backend needs these saved models to work.

### Train all models (LightGBM + LSTM + GRU):

> Requires TensorFlow to be installed first.

```powershell
.\.venv\Scripts\python.exe compare_models.py --save-models
```

### Train only LightGBM (fastest, recommended):

```powershell
.\.venv\Scripts\python.exe compare_models.py --models lightgbm --save-models
```

You should see a comparison table with metrics like MAE, MSE, RMSE, and training time.

---

## Step 7: Regenerate Default Topology Files

This generates the road network connectivity files that the routing system uses:

```powershell
.\.venv\Scripts\python.exe scripts/prepare_real_topology.py
```

You should see output like:

```
Wrote 40 locations to data/boroondara_locations_snapped.csv
Wrote XXX directed edges to data/boroondara_connectivity.csv
```

---

## Step 8: Run Backend Tests (Smoke Tests)

The project includes **11 test cases** covering different problem scenarios:

| # | Test Case | What It Checks |
|---|-----------|----------------|
| 1 | Load saved model | Model bundle loads correctly with expected type and metadata |
| 2 | Predict all sites | Predictions generated for all 40 SCATS sites |
| 3 | Real default topology files | Default topology CSVs exist and contain data |
| 4 | Build dynamic graph | Graph builds with predicted flows and valid edges |
| 5 | Build dynamic routing problem | Problem initializes with correct origin/goals |
| 6 | Solve single best route | Returns correct shortest path with valid travel time |
| 7 | Solve top-k routes | Returns multiple unique routes sorted by cost |
| 8 | Invalid origin handling | Raises `KeyError` for non-existent origin site |
| 9 | Invalid destination handling | Raises `KeyError` for non-existent destination site |
| 10 | Origin equals destination | Raises `ValueError` when origin == destination |
| 11 | No-route handling | Raises `ValueError` when no path exists between sites |

Run all tests:

```powershell
.\.venv\Scripts\python.exe -m scripts.backend_smoke_test
```

Expected output — all tests should show `PASS`:

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

If any test shows `FAIL`, check the error message and ensure Steps 4–7 completed successfully.

---

## Step 9: Run the Application

The app has 2 parts that must run at the same time: **Backend** (AI processing) and **Frontend** (Web interface). You need to open **2 PowerShell windows**.

### Window 1 — Start the Backend

1. Open a new PowerShell window.
2. Navigate to the project folder:

   ```powershell
   cd C:\Users\YourName\cos30019-assignment-3
   ```

3. Run the backend server:

   ```powershell
   .\.venv\Scripts\python.exe -m uvicorn webapi.server:app --reload --host 127.0.0.1 --port 8000
   ```

4. You should see: `Uvicorn running on http://127.0.0.1:8000`
5. **Leave this window open. Do not close it.**

### Window 2 — Start the Frontend

1. Open another new PowerShell window (keep Window 1 running).
2. Navigate to the frontend folder:

   ```powershell
   cd C:\Users\YourName\cos30019-assignment-3\frontend
   ```

3. Run the frontend dev server:

   ```powershell
   npm run dev
   ```

4. You should see: `Local: http://localhost:5173/`
5. **Leave this window open too.**

---

## Step 10: Open the Browser

1. Open your web browser (Chrome, Edge, Firefox).
2. Type: **http://127.0.0.1:5173**
3. Press Enter. You should see the home page of the Traffic Route Guidance System.

---

## How to Use the Web Application

### Map Prediction (Main Feature)

1. Go to the **Map Prediction** page (or click "Start Route Planning" on the home page).
2. Select **Origin** from the dropdown (e.g., `2000`).
3. Select **Destination** from the dropdown (e.g., `3002`).
4. Choose a **Model** (`lightgbm` is recommended for speed).
5. Choose **Top-K** (how many route options you want, 1 to 5).
6. Click **Find Routes**.
7. Routes will appear in the sidebar with travel times. Click any route to highlight it on the map and see turn-by-turn directions.

### Visualization

Go to the **Visualization** page to see charts comparing the accuracy, speed, and error rates of the 3 AI models.

---

## Run from Command Line (No Browser)

### Single best route:

```powershell
.\.venv\Scripts\python.exe main.py --origin 2000 --destination 3002 --model lightgbm
```

### Top-k routes:

```powershell
.\.venv\Scripts\python.exe main.py --origin 2000 --destination 3002 --model lightgbm --top-k 5
```

---

## Optional: Use LSTM or GRU Models

The GUI and API default to `lightgbm`. If you also want the `lstm` or `gru` models, install TensorFlow:

```powershell
.\.venv\Scripts\python.exe -m pip install tensorflow
```

Then retrain:

```powershell
.\.venv\Scripts\python.exe compare_models.py --save-models
```

Without TensorFlow, keep using `lightgbm` only.

---

## Useful Commands Quick Reference

| Task | Command |
|------|---------|
| Install backend deps | `.\.venv\Scripts\python.exe -m pip install -r requirements.txt` |
| Install frontend deps | `cd frontend && npm install` |
| Train models | `.\.venv\Scripts\python.exe compare_models.py --save-models` |
| Regenerate topology | `.\.venv\Scripts\python.exe scripts/prepare_real_topology.py` |
| Run backend tests | `.\.venv\Scripts\python.exe -m scripts.backend_smoke_test` |
| Start backend | `.\.venv\Scripts\python.exe -m uvicorn webapi.server:app --reload --host 127.0.0.1 --port 8000` |
| Start frontend | `cd frontend && npm run dev` |
| CLI route (single) | `.\.venv\Scripts\python.exe main.py --origin 2000 --destination 3002 --model lightgbm` |
| CLI route (top-k) | `.\.venv\Scripts\python.exe main.py --origin 2000 --destination 3002 --model lightgbm --top-k 5` |

---

## Common Problems and Fixes

| Problem | How to Fix |
|---------|-----------|
| `npm` is not recognized | Install Node.js (Step 1), then close and reopen PowerShell |
| `ModuleNotFoundError: No module named 'uvicorn'` | Run Step 4 to install requirements.txt |
| `No module named 'tensorflow'` | LightGBM works without it. Install TensorFlow only if you need LSTM/GRU (see Optional section) |
| `saved_models\lightgbm_metadata.pkl` not found | Run Step 6 to train and save models first |
| Web page is blank/white | Make sure the Backend (Window 1) is still running |
| "No route found" | Only select locations from the dropdown list |
| Port 8000 already in use | Close other programs using port 8000, or restart your computer |
| `Activate.ps1` blocked | Run `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser` first |

---

## How to Stop the Application

When you're done:

1. Go to each PowerShell window.
2. Press **Ctrl + C** to stop the program.
3. Close the windows.
