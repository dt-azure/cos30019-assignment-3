# COS30019 Assignment 2B — Traffic-Based Route Guidance System

> A web application that uses AI to predict traffic and find the fastest routes in the Boroondara area.

This guide is written for beginners. If you've never used a terminal or run code before, don't worry — just follow the steps one by one.

---

## What This Project Does

Imagine Google Maps, but powered by AI that predicts traffic before you leave. This system:

1. **Predicts traffic** at 40 intersections using 3 AI models (LSTM, GRU, LightGBM)
2. **Calculates travel time** for every road based on predicted traffic
3. **Finds the fastest routes** from your starting point to your destination
4. **Shows everything on a map** with an easy-to-use web interface

---

## Before You Start

You need 2 things installed on your computer:

### 1. Python (already set up)
This project comes with a Python environment in the `.venv` folder. You don't need to install anything else for Python.

### 2. Node.js (for the web interface)
If you don't have Node.js installed:

1. Go to https://nodejs.org
2. Click the **green "LTS" button** (recommended for most users)
3. Download and run the installer
4. Restart your computer after installing

To check if Node.js is installed, open **PowerShell** and type:

```powershell
node --version
```

If you see a version number (like `v20.x.x`), you're good to go.

---

## How to Run the Web Application

The web app has **2 parts** that need to run at the same time:
- **Backend** (Python) — does the AI calculations
- **Frontend** (React) — shows the web page you interact with

Think of it like a restaurant: the backend is the kitchen (cooks the food), and the frontend is the dining room (where you see and order food).

### Step 1: Install Frontend Dependencies

This only needs to be done **once**. It downloads all the tools needed to build the web page.

1. Open **PowerShell**
2. Navigate to the project folder:

```powershell
cd C:\Users\vieth\cos30019\cos30019-assignment-3\frontend
```

3. Run this command:

```powershell
npm install
```

You'll see a lot of text scrolling. This is normal — it's downloading packages. Wait until it finishes and you see your cursor again.

### Step 2: Train the AI Models

This only needs to be done **once** (or when you want to retrain). It teaches the AI models to predict traffic.

1. Open **PowerShell**
2. Go to the project folder:

```powershell
cd C:\Users\vieth\cos30019\cos30019-assignment-3
```

3. Run this command:

```powershell
.\.venv\Scripts\python.exe compare_models.py --save-models
```

This will take **2-3 minutes**. You'll see progress bars for each model. When it's done, you'll see a comparison table like this:

```
Model    | MAE     | RMSE    | Time (s)
---------+---------+---------+---------
LSTM     | 14.41   | 21.75   | 115.66
GRU      | 14.30   | 21.66   | 123.55
LightGBM | 14.02   | 21.20   | 0.57
```

The trained models are saved in the `saved_models/` folder.

### Step 3: Start the Backend (Kitchen)

1. Open a **new PowerShell window**
2. Go to the project folder:

```powershell
cd C:\Users\vieth\cos30019\cos30019-assignment-3
```

3. Run this command:

```powershell
.\.venv\Scripts\python.exe -m uvicorn webapi.server:app --reload --host 127.0.0.1 --port 8000
```

You should see:
```
INFO:     Uvicorn running on http://127.0.0.1:8000
```

**Leave this window open.** Don't close it. The backend is now running.

### Step 4: Start the Frontend (Dining Room)

1. Open **another new PowerShell window** (keep the backend window open)
2. Go to the frontend folder:

```powershell
cd C:\Users\vieth\cos30019\cos30019-assignment-3\frontend
```

3. Run this command:

```powershell
npm run dev
```

You should see:
```
  VITE ready in xxx ms
  ➜  Local:   http://localhost:5173/
```

**Leave this window open too.**

### Step 5: Open the Web Page

1. Open your web browser (Chrome, Edge, Firefox)
2. Type this address: **http://127.0.0.1:5173**
3. Press Enter

You should see the home page of the Traffic Route Guidance System!

---

## How to Use the Web Application

### Page 1: Home
The landing page. Click **"Start Route Planning"** to go to the map, or **"View Model Comparison"** to see charts.

### Page 2: Map Prediction (the main feature)

This is where you find routes. Here's how:

1. **Select Origin** — click the dropdown and pick a starting point (e.g., `2000`)
2. **Select Destination** — click the dropdown and pick where you want to go (e.g., `3002`)
3. **Choose Model** — pick `lightgbm` (fastest) or try `lstm` / `gru`
4. **Choose Top-K** — how many route options you want (1 to 5)
5. Click **"Find Routes"**

After a few seconds, you'll see:
- **Route options** in the left sidebar with travel times
- **Routes drawn on the map** in different colors
- **Click any route** to highlight it and see details
- **Turn-by-turn directions** with traffic level, speed, and distance

### Page 3: Visualization

Shows how well each AI model performs with charts:
- **Performance Metrics** — accuracy and speed comparisons
- **Radar Comparison** — multi-dimensional view of each model's strengths
- **Insights** — key takeaways from the data

### Page 4: About

Explains the project, technology used, and how everything works.

---

## How to Run from Command Line (No Web Browser)

If you just want a quick route without opening the web page:

```powershell
.\.venv\Scripts\python.exe main.py --origin 2000 --destination 3002 --model lightgbm
```

You'll see the best route printed in the terminal.

To get up to 5 route options:

```powershell
.\.venv\Scripts\python.exe main.py --origin 2000 --destination 3002 --model lightgbm --top-k 5
```

---

## Available Locations (SCATS Sites)

You can only choose from these 22 locations that have road connections:

`2000, 2200, 2820, 2825, 3001, 3002, 3120, 3122, 3126, 3127, 3180, 3682, 3685, 3812, 4030, 4032, 4035, 4040, 4051, 4057, 4063, 4324`

---

## Common Problems and How to Fix Them

| Problem | How to Fix |
|---------|-----------|
| `npm` is not recognized | Install Node.js from https://nodejs.org and restart your computer |
| `ModuleNotFoundError: No module named 'joblib'` | Run: `.\.venv\Scripts\python.exe -m pip install joblib` |
| `ModuleNotFoundError: No module named 'tensorflow'` | Run: `.\.venv\Scripts\python.exe -m pip install tensorflow` |
| Web page is blank/white | Make sure the backend (Step 3) is still running in its terminal window |
| "No route found" | Make sure both origin and destination are in the list of 22 valid sites above |
| Port 8000 already in use | Close any other program using port 8000, or restart your computer |
| `npm install` gives errors | Run: `npm install --legacy-peer-deps` instead |

---

## How to Stop the Application

When you're done:

1. Go to each terminal window
2. Press **Ctrl + C** to stop the program
3. Close the terminal windows

---

## Project Structure (for reference)

```
machine_learning/     AI models and prediction logic
utils/                Helper functions for calculations
webapi/               Backend server code
frontend/             Web page code (React)
data/                 Traffic data and road network info
saved_models/         Trained AI models (created after Step 2)
main.py               Command-line entry point
compare_models.py     Model training script
```

---

## Need Help?

- Check the `EXECUTION_GUIDE.md` file for more detailed commands
- Ask your tutor if something doesn't work
