from machine_learning.common.route_service import build_and_solve_dynamic_routes
from machine_learning.common.topology_service import (
    DEFAULT_CONNECTIVITY_CSV,
    DEFAULT_LOCATIONS_CSV,
    load_connectivity_list,
    validate_locations_csv,
)

DEFAULT_CLI_MODEL_NAME = "lightgbm"
DEFAULT_CLI_ALGORITHM = "astar"


def validate_route_request(origin_site_id, destination_site_id):
    origin_site_id = int(origin_site_id)
    destination_site_id = int(destination_site_id)

    if origin_site_id == destination_site_id:
        raise ValueError("Origin and destination must be different SCATS site IDs.")

    return origin_site_id, destination_site_id


def compute_terminal_route(
    origin_site_id,
    destination_site_id,
    model_name=DEFAULT_CLI_MODEL_NAME,
    algorithm=DEFAULT_CLI_ALGORITHM,
    locations_csv=DEFAULT_LOCATIONS_CSV,
    connectivity_csv=DEFAULT_CONNECTIVITY_CSV,
):
    route_results, goal_nodes, problem, graph, predicted_flows = compute_terminal_routes(
        origin_site_id=origin_site_id,
        destination_site_id=destination_site_id,
        model_name=model_name,
        algorithm=algorithm,
        top_k=1,
        locations_csv=locations_csv,
        connectivity_csv=connectivity_csv,
    )
    return route_results[0], goal_nodes[0], problem, graph, predicted_flows


def compute_terminal_routes(
    origin_site_id,
    destination_site_id,
    model_name=DEFAULT_CLI_MODEL_NAME,
    algorithm=DEFAULT_CLI_ALGORITHM,
    top_k=1,
    locations_csv=DEFAULT_LOCATIONS_CSV,
    connectivity_csv=DEFAULT_CONNECTIVITY_CSV,
):
    origin_site_id, destination_site_id = validate_route_request(
        origin_site_id,
        destination_site_id,
    )

    validated_locations_csv = validate_locations_csv(locations_csv)
    connectivity_list = load_connectivity_list(connectivity_csv)

    route_results, goal_nodes, problem, graph, predicted_flows = build_and_solve_dynamic_routes(
        locations_csv=validated_locations_csv,
        connectivity_list=connectivity_list,
        origin_site_id=origin_site_id,
        destination_site_ids=destination_site_id,
        model_name=model_name,
        algorithm=algorithm,
        top_k=top_k,
    )

    return route_results, goal_nodes, problem, graph, predicted_flows


def format_route_result(route_result, origin_site_id, destination_site_id, model_name):
    total_seconds = route_result["total_travel_time_sec"]
    total_minutes = total_seconds / 60
    path_text = " -> ".join(str(site_id) for site_id in route_result["path"])

    return "\n".join(
        [
            f"Model: {model_name}",
            f"Origin: {origin_site_id}",
            f"Destination: {destination_site_id}",
            f"Algorithm: {route_result['algorithm']}",
            f"Best Path: {path_text}",
            f"Total Travel Time (seconds): {total_seconds:.2f}",
            f"Total Travel Time (minutes): {total_minutes:.2f}",
        ]
    )


def format_route_results(route_results, origin_site_id, destination_site_id, model_name, top_k):
    lines = [
        f"Model: {model_name}",
        f"Origin: {origin_site_id}",
        f"Destination: {destination_site_id}",
        f"Routes Requested: {top_k}",
        f"Routes Found: {len(route_results)}",
    ]

    for index, route_result in enumerate(route_results, start=1):
        total_seconds = route_result["total_travel_time_sec"]
        total_minutes = total_seconds / 60
        path_text = " -> ".join(str(site_id) for site_id in route_result["path"])
        lines.extend(
            [
                f"Route {index}:",
                f"Path: {path_text}",
                f"Goal Site: {route_result['goal_site_id']}",
                f"Strategy: {route_result['algorithm']}",
                f"Travel Time (seconds): {total_seconds:.2f}",
                f"Travel Time (minutes): {total_minutes:.2f}",
            ]
        )

    return "\n".join(lines)
