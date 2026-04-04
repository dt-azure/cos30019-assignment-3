# COS30019 Assignment 2B — Traffic-Based Route Guidance System

> A web application that uses AI to predict traffic and find the fastest routes in the Boroondara area.

---

## What This Project Does

This system uses 3 AI models (LSTM, GRU, LightGBM) to:
1. **Predict traffic** at intersections
2. **Calculate travel time** for every road
3. **Find the fastest routes** from point A to B
4. **Show everything on an interactive map**

---

## Quick Start — 1 Command to Run Everything

### First Time Setup (do this once)

Open **PowerShell** and run these 3 commands:

**1. Install Node.js (via PowerShell, no browser needed):**
```powershell
winget install OpenJS.NodeJS.LTS
```
Then **close and reopen PowerShell**.

**2. Install frontend dependencies:**
```powershell
cd C:\Users\vieth\cos30019\cos30019-assignment-3\frontend
npm install
```

**3. Train the AI models:**
```powershell
cd C:\Users\vieth\cos30019\cos30019-assignment-3
.\.venv\Scripts\python.exe compare_models.py --save-models
```

Wait 2-3 minutes. Done.

### Run the Web App (every time after setup)

Just **1 command** in PowerShell:

```powershell
cd C:\Users\vieth\cos30019\cos30019-assignment-3
.\.venv\Scripts\python.exe -m uvicorn webapi.server:app --reload --host 127.0.0.1 --port 8000
```

Then open: **http://127.0.0.1:8000**

That's it. One terminal. One command.

---

## Using the Web App

### Map Prediction (main page)
1. Select **Origin** (e.g., `2000`)
2. Select **Destination** (e.g., `3002`)
3. Choose **Model** (`lightgbm` is fastest)
4. Click **Find Routes**
5. Click any route on the sidebar to see it on the map

### Visualization
Charts comparing AI model accuracy, speed, and error rates.

---

## Run from Command Line (No Browser)

```powershell
.\.venv\Scripts\python.exe main.py --origin 2000 --destination 3002 --model lightgbm
```

---

## Available Locations

`2000, 2200, 2820, 2825, 3001, 3002, 3120, 3122, 3126, 3127, 3180, 3682, 3685, 3812, 4030, 4032, 4035, 4040, 4051, 4057, 4063, 4324`

---

## Troubleshooting

| Problem | Fix |
|---------|-----|
| `winget` not found | Open Microsoft Store, search "App Installer", install it |
| `npm` not found after install | Close and reopen PowerShell |
| `ModuleNotFoundError` | `.\.venv\Scripts\python.exe -m pip install joblib tensorflow` |
| Web page is blank | Make sure the command above is still running |
| "No route found" | Use only the 22 locations listed above |

---

## How to Stop

Press **Ctrl + C** in the PowerShell window.
