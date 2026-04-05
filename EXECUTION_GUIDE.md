# Execution Guide — COS30019 Assignment 2B

This guide is written for beginners. Follow the steps one by one.

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

## Step 1: Install Required Software

You need 2 things on your computer:

### 1. Create a Python virtual environment
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

### 2. Node.js (for the Web interface)
Open **PowerShell** and run this command to install automatically (no browser needed):

```powershell
winget install OpenJS.NodeJS.LTS
```

```macos(terminal)
brew install node
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

## Step 3: Install Frontend Dependencies

Run this command **only once** when you first get the project:

```powershell
cd frontend
npm install
```

You'll see text scrolling as packages are downloaded. Wait until your cursor appears again.

---

## Step 4: Run the Application

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

## Step 5: Open the Browser

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

If you just want a quick route result in the terminal:

```powershell
cd C:\Users\YourName\cos30019-assignment-3
.\.venv\Scripts\python.exe main.py --origin 2000 --destination 3002 --model lightgbm
```

---

## Common Problems and Fixes

| Problem | How to Fix |
|---------|-----------|
| `npm` is not recognized | Install Node.js (Step 1), then close and reopen PowerShell |
| `ModuleNotFoundError` | Make sure you're running commands from the project root folder |
| Web page is blank/white | Make sure the Backend (Window 1) is still running |
| "No route found" | Only select locations from the dropdown list |
| Port 8000 already in use | Close other programs using port 8000, or restart your computer |

---

## How to Stop the Application

When you're done:
1. Go to each PowerShell window.
2. Press **Ctrl + C** to stop the program.
3. Close the windows.
