# Execution Guide — COS30019 Assignment 2B

This guide covers all ways to run the Traffic-Based Route Guidance System.

---

## Installation

### Step 1: Install Node.js

If you don't have Node.js installed:

1. Go to https://nodejs.org
2. Download and install the **LTS version** (includes npm)
3. Verify installation:

```powershell
node --version
npm --version
```

### Step 2: Install Frontend Dependencies

Open a terminal in the project root and run:

```powershell
cd frontend
npm install
```

This installs: React, TypeScript, Vite, Leaflet, Recharts, React Router, Lucide Icons.

### Step 3: Install Python Dependencies (if needed)

The project uses the existing `.venv` virtual environment. If packages are missing:

```powershell
.\.venv\Scripts\python.exe -m pip install fastapi uvicorn joblib lightgbm numpy pandas scikit-learn tensorflow
```

### Step 4: Train and Save Models

Before running the web app, you must train and save the ML models:

```powershell
.\.venv\Scripts\python.exe compare_models.py --save-models
```

This creates the `saved_models/` directory with trained LSTM, GRU, and LightGBM models.

---

## Part 1: Run from Command Line (CLI)

### Single Route

```powershell
.\.venv\Scripts\python.exe main.py --origin 2000 --destination 3002 --model lightgbm
```

### Top-K Routes (up to 5)

```powershell
.\.venv\Scripts\python.exe main.py --origin 2000 --destination 3002 --model lightgbm --top-k 5
```

### Available Parameters

| Parameter | Description | Default | Options |
|-----------|-------------|---------|---------|
| `--origin` | Origin SCATS site ID | 2000 | Any valid site ID |
| `--destination` | Destination SCATS site ID | 3002 | Any valid site ID |
| `--model` | Prediction model | lightgbm | `lightgbm`, `lstm`, `gru` |
| `--top-k` | Number of routes (1-5) | 1 | 1, 2, 3, 4, 5 |
| `--algorithm` | Search algorithm | astar | `astar`, `ucs` |

### Available SCATS Sites

`2000, 2200, 2820, 2825, 3001, 3002, 3120, 3122, 3126, 3127, 3180, 3682, 3685, 3812, 4030, 4032, 4035, 4040, 4051, 4057, 4063, 4324`

---

## Part 2: Run the Web Application

The web app requires **2 terminals** running simultaneously.

### Terminal 1 — Start Backend API

```powershell
.\.venv\Scripts\python.exe -m uvicorn webapi.server:app --reload --host 127.0.0.1 --port 8000
```

You should see:
```
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
```

### Terminal 2 — Start Frontend

Open a **new terminal** (keep Terminal 1 running):

```powershell
cd C:\Users\vieth\cos30019\cos30019-assignment-3\frontend
npm run dev
```

You should see:
```
  VITE v6.0.3  ready in xxx ms

  ➜  Local:   http://localhost:5173/
```

### Open Browser

Go to `http://127.0.0.1:5173`

---

## Part 3: Using the Web Application

### Home Page (`/`)
- System overview and key statistics
- Quick navigation buttons to Map Prediction and Visualization

### Map Prediction Page (`/map`)

**How to find a route:**

1. Select **Origin** from dropdown (e.g., `2000`)
2. Select **Destination** from dropdown (e.g., `3002`)
3. Choose **Model** (LightGBM recommended for speed)
4. Choose **Top-K** (1-5 routes)
5. Click **Find Routes**

**After routes are computed:**

- Routes appear in the sidebar with travel times
- Click any route to highlight it on the map
- See turn-by-turn directions with traffic level, speed, distance, and ETA

### Visualization Page (`/visualization`)

**Tabs:**

1. **Performance Metrics** — Bar charts for MAE, RMSE, training time, efficiency
2. **Radar Comparison** — Multi-dimensional model comparison
3. **Insights** — Key findings from model evaluation

**Charts include:**
- MAE & RMSE comparison
- Training time comparison
- Model efficiency score
- Traffic flow prediction vs actual (24h)
- Error distribution
- Model performance share (pie chart)

### About Page (`/about`)
- Project overview and technology stack
- How the system works (5 steps)
- Resources and references

---

## Part 4: API Testing

### Health Check

```powershell
curl http://127.0.0.1:8000/api/health
```

### Get Configuration

```powershell
curl http://127.0.0.1:8000/api/config
```

### Compute Routes

```powershell
curl -X POST http://127.0.0.1:8000/api/routes/compute `
  -H "Content-Type: application/json" `
  -d '{"origin": 2000, "destination": 3002, "model": "lightgbm", "top_k": 3}'
```

---

## Part 5: Smoke Tests

```powershell
.\.venv\Scripts\python.exe -m scripts.backend_smoke_test
```

Expected: 11 tests all PASS.

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| `npm` not found | Install Node.js from https://nodejs.org |
| `ModuleNotFoundError: No module named 'joblib'` | `.\.venv\Scripts\python.exe -m pip install joblib` |
| `ModuleNotFoundError: No module named 'tensorflow'` | `.\.venv\Scripts\python.exe -m pip install tensorflow` |
| Frontend shows blank page | Check that backend is running on port 8000 |
| "No route found" error | Ensure origin and destination are in the valid sites list |
| Port 8000 already in use | Kill existing process or use `--port 8001` |
| Port 5173 already in use | Vite will auto-select another port (e.g., 5174) |
| `npm install` fails | Run `npm install --legacy-peer-deps` |

---

## Quick Reference

| Task | Command |
|------|---------|
| Install frontend deps | `cd frontend && npm install` |
| Train models | `.\.venv\Scripts\python.exe compare_models.py --save-models` |
| Start backend | `.\.venv\Scripts\python.exe -m uvicorn webapi.server:app --reload --host 127.0.0.1 --port 8000` |
| Start frontend | `cd frontend && npm run dev` |
| CLI route | `.\.venv\Scripts\python.exe main.py --origin 2000 --destination 3002 --model lightgbm` |
| Smoke tests | `.\.venv\Scripts\python.exe -m scripts.backend_smoke_test` |
