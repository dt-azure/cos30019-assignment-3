import csv
from pathlib import Path

DEFAULT_LOCATIONS_CSV = "data/boroondara_locations_sample.csv"
DEFAULT_CONNECTIVITY_CSV = "data/boroondara_connectivity_sample.csv"


def get_default_topology_paths():
    return {
        "locations_csv": DEFAULT_LOCATIONS_CSV,
        "connectivity_csv": DEFAULT_CONNECTIVITY_CSV,
    }


def load_connectivity_list(connectivity_csv=DEFAULT_CONNECTIVITY_CSV):
    connectivity_path = Path(connectivity_csv)
    if not connectivity_path.exists():
        raise FileNotFoundError(f"Connectivity file not found: {connectivity_csv}")

    with connectivity_path.open(newline="") as handle:
        reader = csv.DictReader(handle)
        required_columns = {"origin", "destination", "distance_km"}
        missing_columns = required_columns.difference(reader.fieldnames or [])
        if missing_columns:
            raise ValueError(
                f"Connectivity file is missing required columns: {sorted(missing_columns)}"
            )

        return [
            (
                int(row["origin"]),
                int(row["destination"]),
                float(row["distance_km"]),
            )
            for row in reader
        ]


def validate_locations_csv(locations_csv=DEFAULT_LOCATIONS_CSV):
    if not Path(locations_csv).exists():
        raise FileNotFoundError(f"Locations file not found: {locations_csv}")

    return locations_csv

