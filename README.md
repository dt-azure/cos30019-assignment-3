# COS30019 Assignment 2B — Traffic-Based Route Guidance System

> A web application that uses AI to predict traffic and find the fastest routes in the Boroondara area.

---

## Quick Start — Run Everything in 5 Steps

Open **PowerShell** and follow these steps exactly.

### Step 1: Install Frontend Dependencies

```powershell
cd C:\Users\vieth\cos30019\cos30019-assignment-3\frontend
npm install
```

### Step 2: Train the AI Models

```powershell
cd C:\Users\vieth\cos30019\cos30019-assignment-3
.\.venv\Scripts\python.exe compare_models.py --save-models
```

Wait 2-3 minutes. Models will be saved to `saved_models/`.

### Step 3: Start the Backend (Terminal 1)

Open a **new PowerShell window**:

```powershell
cd C:\Users\vieth\cos30019\cos30019-assignment-3
.\.venv\Scripts\python.exe -m uvicorn webapi.server:app --reload --host 127.0.0.1 --port 8000
```

Leave this window open.

### Step 4: Start the Frontend (Terminal 2)

Open **another new PowerShell window**:

```powershell
cd C:\Users\vieth\cos30019\cos30019-assignment-3\frontend
npm run dev
```

Leave this window open.

### Step 5: Open the Browser

Go to: **http://127.0.0.1:5173**

---

## Using the Web App

### Map Prediction (`/map`)
1. Select **Origin** from dropdown (e.g., `2000`)
2. Select **Destination** from dropdown (e.g., `3002`)
3. Choose **Model** (`lightgbm` is fastest)
4. Choose **Top-K** (1-5 routes)
5. Click **Find Routes**

Click any route in the sidebar to see it highlighted on the map with turn-by-turn directions.

### Visualization (`/visualization`)
Charts comparing the 3 AI models: accuracy, speed, error distribution, and more.

---

## Run from Command Line (No Browser)

Single route:

```powershell
.\.venv\Scripts\python.exe main.py --origin 2000 --destination 3002 --model lightgbm
```

Top-5 routes:

```powershell
.\.venv\Scripts\python.exe main.py --origin 2000 --destination 3002 --model lightgbm --top-k 5
```

---

## Available SCATS Sites

`2000, 2200, 2820, 2825, 3001, 3002, 3120, 3122, 3126, 3127, 3180, 3682, 3685, 3812, 4030, 4032, 4035, 4040, 4051, 4057, 4063, 4324`

---

## Common Problems

| Problem | Fix |
|---------|-----|
| `npm` not found | Install Node.js from https://nodejs.org |
| `ModuleNotFoundError: No module named 'joblib'` | `.\.venv\Scripts\python.exe -m pip install joblib` |
| `ModuleNotFoundError: No module named 'tensorflow'` | `.\.venv\Scripts\python.exe -m pip install tensorflow` |
| Web page is blank | Make sure backend (Step 3) is still running |
| "No route found" | Use only the 22 valid sites listed above |
| `npm install` errors | Run `npm install --legacy-peer-deps` instead |

---

## How to Stop

Press **Ctrl + C** in each terminal window.
