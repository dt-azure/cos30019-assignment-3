"""Build the default routing topology files from the real location source.

The original repo history contains the real site coordinate export, but not the
old edge-generation script referenced by graph.py. To remove the placeholder
sample defaults while keeping the backend reproducible, this script:

1. Filters the real coordinate export down to the 40 SCATS sites used by the
   traffic dataset.
2. Writes a normalized locations CSV that matches the graph loader schema.
3. Builds a deterministic spatial fallback connectivity CSV from nearby sites.
"""

from __future__ import annotations

import csv
import math
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from machine_learning.common.config import (
    DEFAULT_TOPOLOGY_CONNECTIVITY_CSV,
    DEFAULT_TOPOLOGY_LOCATIONS_CSV,
    RAW_TOPOLOGY_LOCATIONS_CSV,
    SCATS_DATA_PATH,
)
from utils.parse_data import parse_scats_data

DEFAULT_NEIGHBORS_PER_SITE = 4
DEFAULT_MAX_EDGE_DISTANCE_KM = 10.0


def haversine_km(origin, destination):
    lat1, lon1 = map(math.radians, origin)
    lat2, lon2 = map(math.radians, destination)
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = (
        math.sin(dlat / 2) ** 2
        + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
    )
    return 6371 * (2 * math.asin(math.sqrt(a)))


def load_site_ids(data_path=SCATS_DATA_PATH):
    return sorted(parse_scats_data(data_path))


def load_raw_location_rows(raw_locations_csv=RAW_TOPOLOGY_LOCATIONS_CSV):
    with Path(raw_locations_csv).open(newline="", encoding="utf-8-sig") as handle:
        reader = csv.DictReader(handle)
        return {int(row["FID"]): row for row in reader if row["FID"].isdigit()}


def build_location_rows(site_ids, raw_location_rows):
    missing_ids = [site_id for site_id in site_ids if site_id not in raw_location_rows]
    if missing_ids:
        raise KeyError(f"Missing location rows for site IDs: {missing_ids}")

    return [
        {
            "NB_SCATS_SITE": site_id,
            "LATITUDE": float(raw_location_rows[site_id]["Y"]),
            "LONGITUDE": float(raw_location_rows[site_id]["X"]),
            "SITE_DESC": raw_location_rows[site_id]["SITE_DESC"],
        }
        for site_id in site_ids
    ]


def build_connectivity_rows(
    location_rows,
    neighbors_per_site=DEFAULT_NEIGHBORS_PER_SITE,
    max_edge_distance_km=DEFAULT_MAX_EDGE_DISTANCE_KM,
):
    coords_by_site = {
        row["NB_SCATS_SITE"]: (row["LATITUDE"], row["LONGITUDE"]) for row in location_rows
    }
    undirected_edges = {}

    for origin_site_id, origin_coords in coords_by_site.items():
        nearest_sites = sorted(
            (
                haversine_km(origin_coords, destination_coords),
                destination_site_id,
            )
            for destination_site_id, destination_coords in coords_by_site.items()
            if destination_site_id != origin_site_id
        )
        for distance_km, destination_site_id in nearest_sites[:neighbors_per_site]:
            if distance_km > max_edge_distance_km:
                continue

            edge_key = tuple(sorted((origin_site_id, destination_site_id)))
            undirected_edges[edge_key] = distance_km

    connectivity_rows = []
    for (origin_site_id, destination_site_id), distance_km in sorted(undirected_edges.items()):
        connectivity_rows.append(
            {
                "origin": origin_site_id,
                "destination": destination_site_id,
                "distance_km": round(distance_km, 6),
            }
        )
        connectivity_rows.append(
            {
                "origin": destination_site_id,
                "destination": origin_site_id,
                "distance_km": round(distance_km, 6),
            }
        )

    return sorted(connectivity_rows, key=lambda row: (row["origin"], row["destination"]))


def write_locations_csv(location_rows, output_path=DEFAULT_TOPOLOGY_LOCATIONS_CSV):
    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=["NB_SCATS_SITE", "LATITUDE", "LONGITUDE", "SITE_DESC"],
        )
        writer.writeheader()
        writer.writerows(location_rows)


def write_connectivity_csv(connectivity_rows, output_path=DEFAULT_TOPOLOGY_CONNECTIVITY_CSV):
    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=["origin", "destination", "distance_km"],
        )
        writer.writeheader()
        writer.writerows(connectivity_rows)


def main():
    site_ids = load_site_ids()
    raw_location_rows = load_raw_location_rows()
    location_rows = build_location_rows(site_ids, raw_location_rows)
    connectivity_rows = build_connectivity_rows(location_rows)
    write_locations_csv(location_rows)
    write_connectivity_csv(connectivity_rows)
    print(f"Wrote {len(location_rows)} locations to {DEFAULT_TOPOLOGY_LOCATIONS_CSV}")
    print(
        f"Wrote {len(connectivity_rows)} directed edges to "
        f"{DEFAULT_TOPOLOGY_CONNECTIVITY_CSV}"
    )


if __name__ == "__main__":
    main()
