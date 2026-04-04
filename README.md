# COS30019 Assignment 2B — Traffic-Based Route Guidance System

> An AI-powered web application that predicts traffic flow and finds the fastest routes in the Boroondara area.

This is the Assignment 2B submission for the course **COS30019 - Introduction to AI**.

---

## Project Structure (Folder Tree)

```text
cos30019-assignment-3/
│
├── .venv/                      # Python Virtual Environment (Backend)
├── data/                       # Input Data
│   ├── scats_data_october_2006.xls  # Historical traffic data
│   ├── boroondara_locations.csv     # SCATS site locations
│   └── boroondara_connectivity.csv  # Road network connectivity
│
├── frontend/                   # Web Interface (React + Vite)
│   ├── src/                    # Source code
│   ├── package.json            # Node.js configuration
│   └── node_modules/           # Installed libraries
│
├── machine_learning/           # AI/ML Source Code
│   ├── lstm.py                 # LSTM Model
│   ├── gru.py                  # GRU Model
│   ├── lightgbm.py             # LightGBM Model
│   └── common/                 # Shared ML utilities
│
├── utils/                      # Utility functions (Calculations, Search)
├── webapi/                     # Backend Server (FastAPI)
│   └── server.py               # API entry point
│
├── main.py                     # CLI entry point for routing
└── compare_models.py           # Script to train and compare models
```

---

## Key Features

1.  **Traffic Prediction:** Uses 3 AI models (LSTM, GRU, LightGBM) to forecast traffic flow.
2.  **Optimal Routing:** Finds fastest routes using A* and Uniform Cost Search algorithms.
3.  **Interactive Web UI:** Map visualization, route comparison, and model performance charts.
