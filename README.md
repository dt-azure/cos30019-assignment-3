# COS30019 Assignment 2B

## Backend Usage

### Compare Models

Run the current model comparison script:

```bash
./.venv/bin/python compare_models.py
```

Save trained model artifacts while comparing:

```bash
./.venv/bin/python compare_models.py --save-models
```

### Save And Load Models

Train and save a LightGBM bundle:

```bash
./.venv/bin/python -c "from machine_learning.lightgbm import train_lightgbm; bundle, results = train_lightgbm(save=True); print(results)"
```

Load the saved default prediction bundle later:

```bash
./.venv/bin/python -c "from machine_learning.common.site_flow_service import load_default_prediction_bundle; bundle = load_default_prediction_bundle(); print(bundle['model_type'], bundle['window_size'])"
```

### Run Dynamic Routing From Terminal

Regenerate the default real topology files before routing if needed:

```bash
./.venv/bin/python scripts/prepare_real_topology.py
```

Data source note:
- ML training and prediction windows use `data/scats_data_october_2006.xls`.
- Default routing uses `data/boroondara_locations.csv` and `data/boroondara_connectivity.csv`.
- Those routing CSVs are generated from `data/Traffic_Count_Locations_with_LONG_LAT.csv` plus the 40 site IDs present in the traffic dataset.
- `data/SCATSSiteListingSpreadsheet_VicRoads.xls/.xlsx` is not used directly in the active backend routing path.

Single best route:

```bash
./.venv/bin/python main.py --origin 2000 --destination 3002 --model lightgbm
```

Top-k routes, up to 5:

```bash
./.venv/bin/python main.py --origin 2000 --destination 3002 --model lightgbm --top-k 5
```

### Run Backend Smoke Checks

Run the non-GUI backend validation sweep:

```bash
./.venv/bin/python -m scripts.backend_smoke_test
```

This smoke test covers:
- saved model loading
- all-site prediction
- dynamic graph construction
- dynamic problem construction
- single-route solving
- top-k route solving
- invalid origin and destination handling
- origin equals destination validation
- no-route handling
