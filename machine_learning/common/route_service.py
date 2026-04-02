from machine_learning.common.config import SCATS_DATA_PATH
from machine_learning.common.problem_service import (
    DEFAULT_PROBLEM_MODEL_NAME,
    build_dynamic_problem,
    build_dynamic_problem_from_bundle,
)
from utils.search import (
    astar_search,
    extract_path_states,
    uniform_cost_search,
    uniform_cost_top_k_search,
)

SEARCH_ALGORITHMS = {
    "astar": astar_search,
    "uniform_cost": uniform_cost_search,
}


def solve_problem(problem, algorithm="astar"):
    if algorithm not in SEARCH_ALGORITHMS:
        raise ValueError(
            f"Unsupported search algorithm '{algorithm}'. "
            f"Choose from: {sorted(SEARCH_ALGORITHMS)}"
        )

    goal_node = SEARCH_ALGORITHMS[algorithm](problem)

    if goal_node is None:
        raise ValueError("No route found for the given origin and destination.")

    return {
        "path": extract_path_states(goal_node),
        "goal_site_id": int(goal_node.state),
        "total_travel_time_sec": float(goal_node.path_cost),
        "algorithm": algorithm,
    }, goal_node


def solve_top_k_problems(problem, top_k=5):
    if top_k < 1:
        raise ValueError("top_k must be at least 1.")

    goal_nodes = uniform_cost_top_k_search(problem, top_k=top_k)
    if not goal_nodes:
        raise ValueError("No route found for the given origin and destination.")

    routes = [
        {
            "path": extract_path_states(goal_node),
            "goal_site_id": int(goal_node.state),
            "total_travel_time_sec": float(goal_node.path_cost),
            "algorithm": "uniform_cost_top_k",
        }
        for goal_node in goal_nodes
    ]
    return routes, goal_nodes


def build_and_solve_dynamic_route_from_bundle(
    locations_csv,
    connectivity_list,
    origin_site_id,
    destination_site_ids,
    model_bundle,
    recent_windows,
    algorithm="astar",
):
    problem, graph, predicted_flows = build_dynamic_problem_from_bundle(
        locations_csv=locations_csv,
        connectivity_list=connectivity_list,
        origin_site_id=origin_site_id,
        destination_site_ids=destination_site_ids,
        model_bundle=model_bundle,
        recent_windows=recent_windows,
    )
    route_result, goal_node = solve_problem(problem, algorithm=algorithm)
    return route_result, goal_node, problem, graph, predicted_flows


def build_and_solve_dynamic_routes_from_bundle(
    locations_csv,
    connectivity_list,
    origin_site_id,
    destination_site_ids,
    model_bundle,
    recent_windows,
    top_k=1,
    algorithm="astar",
):
    problem, graph, predicted_flows = build_dynamic_problem_from_bundle(
        locations_csv=locations_csv,
        connectivity_list=connectivity_list,
        origin_site_id=origin_site_id,
        destination_site_ids=destination_site_ids,
        model_bundle=model_bundle,
        recent_windows=recent_windows,
    )

    if top_k == 1:
        route_result, goal_node = solve_problem(problem, algorithm=algorithm)
        return [route_result], [goal_node], problem, graph, predicted_flows

    route_results, goal_nodes = solve_top_k_problems(problem, top_k=top_k)
    return route_results, goal_nodes, problem, graph, predicted_flows


def build_and_solve_dynamic_route(
    locations_csv,
    connectivity_list,
    origin_site_id,
    destination_site_ids,
    model_name=DEFAULT_PROBLEM_MODEL_NAME,
    data_path=SCATS_DATA_PATH,
    model_path=None,
    metadata_path=None,
    algorithm="astar",
):
    problem, graph, predicted_flows = build_dynamic_problem(
        locations_csv=locations_csv,
        connectivity_list=connectivity_list,
        origin_site_id=origin_site_id,
        destination_site_ids=destination_site_ids,
        model_name=model_name,
        data_path=data_path,
        model_path=model_path,
        metadata_path=metadata_path,
    )
    route_result, goal_node = solve_problem(problem, algorithm=algorithm)
    return route_result, goal_node, problem, graph, predicted_flows


def build_and_solve_dynamic_routes(
    locations_csv,
    connectivity_list,
    origin_site_id,
    destination_site_ids,
    model_name=DEFAULT_PROBLEM_MODEL_NAME,
    data_path=SCATS_DATA_PATH,
    model_path=None,
    metadata_path=None,
    top_k=1,
    algorithm="astar",
):
    problem, graph, predicted_flows = build_dynamic_problem(
        locations_csv=locations_csv,
        connectivity_list=connectivity_list,
        origin_site_id=origin_site_id,
        destination_site_ids=destination_site_ids,
        model_name=model_name,
        data_path=data_path,
        model_path=model_path,
        metadata_path=metadata_path,
    )

    if top_k == 1:
        route_result, goal_node = solve_problem(problem, algorithm=algorithm)
        return [route_result], [goal_node], problem, graph, predicted_flows

    route_results, goal_nodes = solve_top_k_problems(problem, top_k=top_k)
    return route_results, goal_nodes, problem, graph, predicted_flows
