import csv
from pathlib import Path

from machine_learning.common.cli_route_service import (
    DEFAULT_CLI_MODEL_NAME,
    compute_terminal_routes,
)
from machine_learning.common.config import (
    SCATS_DATA_PATH,
    SEQUENCE_MODEL_TYPES,
    TABULAR_MODEL_TYPES,
)
from machine_learning.common.topology_service import (
    DEFAULT_CONNECTIVITY_CSV,
    DEFAULT_LOCATIONS_CSV,
)

MAX_TOP_K = 5


def get_available_models():
    model_names = sorted(SEQUENCE_MODEL_TYPES | TABULAR_MODEL_TYPES)
    if DEFAULT_CLI_MODEL_NAME in model_names:
        model_names.remove(DEFAULT_CLI_MODEL_NAME)
        model_names.insert(0, DEFAULT_CLI_MODEL_NAME)
    return model_names


def get_default_data_sources():
    return {
        "traffic_data_path": SCATS_DATA_PATH,
        "locations_csv": DEFAULT_LOCATIONS_CSV,
        "connectivity_csv": DEFAULT_CONNECTIVITY_CSV,
    }


def load_site_descriptions(locations_csv=DEFAULT_LOCATIONS_CSV):
    descriptions = {}
    locations_path = Path(locations_csv)
    if not locations_path.exists():
        return descriptions

    with locations_path.open(newline="") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            site_id_text = row.get("NB_SCATS_SITE")
            if not site_id_text:
                continue
            descriptions[int(site_id_text)] = row.get("SITE_DESC", "").strip()

    return descriptions


def build_route_request(origin_value, destination_value, model_name, top_k):
    try:
        origin_site_id = int(str(origin_value).strip())
    except ValueError as exc:
        raise ValueError("Origin must be a valid SCATS site ID.") from exc

    try:
        destination_site_id = int(str(destination_value).strip())
    except ValueError as exc:
        raise ValueError("Destination must be a valid SCATS site ID.") from exc

    try:
        top_k_value = int(str(top_k).strip())
    except ValueError as exc:
        raise ValueError("Top-k must be an integer between 1 and 5.") from exc

    if not 1 <= top_k_value <= MAX_TOP_K:
        raise ValueError(f"Top-k must be between 1 and {MAX_TOP_K}.")

    available_models = get_available_models()
    if model_name not in available_models:
        raise ValueError(f"Unsupported model: {model_name}")

    return {
        "origin_site_id": origin_site_id,
        "destination_site_id": destination_site_id,
        "model_name": model_name,
        "top_k": top_k_value,
    }


def compute_gui_routes(
    origin_value,
    destination_value,
    model_name=DEFAULT_CLI_MODEL_NAME,
    top_k=1,
    locations_csv=DEFAULT_LOCATIONS_CSV,
    connectivity_csv=DEFAULT_CONNECTIVITY_CSV,
):
    route_request = build_route_request(
        origin_value=origin_value,
        destination_value=destination_value,
        model_name=model_name,
        top_k=top_k,
    )

    route_results, goal_nodes, problem, graph, predicted_flows = compute_terminal_routes(
        origin_site_id=route_request["origin_site_id"],
        destination_site_id=route_request["destination_site_id"],
        model_name=route_request["model_name"],
        top_k=route_request["top_k"],
        locations_csv=locations_csv,
        connectivity_csv=connectivity_csv,
    )

    site_descriptions = load_site_descriptions(locations_csv)

    return {
        **route_request,
        "route_results": route_results,
        "goal_nodes": goal_nodes,
        "problem": problem,
        "graph": graph,
        "predicted_flows": predicted_flows,
        "site_descriptions": site_descriptions,
        "traffic_data_path": SCATS_DATA_PATH,
        "locations_csv": locations_csv,
        "connectivity_csv": connectivity_csv,
    }
