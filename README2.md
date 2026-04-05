## Tech stack
***Backend***
- FastAPI
- Uvicorn
- tensorflow
- scikit-learn
- LightGBM
- pandas, numpy

***Frontend***
- Vite
- npm
- Leaflet
- OSRM API

## Prerequisites
Make sure you have the following installed:
- Python 3.13+
Download: https://www.python.org/downloads/

- Node.js (includes npm)
Download: https://nodejs.org/en/download/current

## Getting started
### 1. Clone the Repository

```bash
git clone <your-github-repo-url>
cd COS30019-ASSIGNMENT-3
```

### 2. Backend setup
Create a virtual environment (recommended)

[Add intructions here]

Activate it:

[Add intructions here]

Install backend dependencies:

```bash
pip install --upgrade pip
pip install numpy pandas tensorflow scikit-learn joblib lightgbm xlrd fastapi uvicorn osmnx tqdm
```

Run backend smoke test:

```bash
python -m scripts.backend_smoke_test
```

Expected output:

```
All backend smoke checks passed.
```

Generate the default topology files:

```bash
python scripts/prepare_real_topology.py
```

Generate snapped coordinates for each node:

```bash
python scripts/snap_map_coords.py
```

### 3. Run backend

```bash
uvicorn webapi.server:app --reload --host 127.0.0.1 --port 8000
```

Execpted output:

```
Uvicorn running on http://127.0.0.1:8000
```

### 4. Test backend
Open in browser:

```bash
http://127.0.0.1:8000/api/health
```

Expected response:

```JSON
{"status": "ok"}
```

### 5. Frontend setup
Open in new terminal:

```
cd dashboard
npm install
```

### 6. Frontend setup
Run command:

```
npm run dev
```

Expected output:

```
Local: http://localhost:5173/
```

## API Endpoints
Open in browser (after starting backend):


```
http://127.0.0.1:8000/docs
```


