from collections.abc import Iterable

from machine_learning.common.config import SCATS_DATA_PATH
from machine_learning.common.graph_cost_service import (
    build_updated_graph,
    build_updated_graph_from_bundle,
    load_bundle_windows_and_graph,
)
from utils.graph import BoroondaraProblem

DEFAULT_PROBLEM_MODEL_NAME = "lightgbm"


def normalize_goal_site_ids(destination_site_ids):
    if isinstance(destination_site_ids, Iterable) and not isinstance(
        destination_site_ids,
        (str, bytes),
    ):
        return {int(site_id) for site_id in destination_site_ids}

    return {int(destination_site_ids)}


def validate_problem_site_ids(graph, origin_site_id, goal_site_ids):
    origin_site_id = int(origin_site_id)
    goal_site_ids = {int(site_id) for site_id in goal_site_ids}

    if origin_site_id not in graph.nodes:
        raise KeyError(f"Origin site {origin_site_id} does not exist in the graph.")

    missing_goals = sorted(site_id for site_id in goal_site_ids if site_id not in graph.nodes)
    if missing_goals:
        raise KeyError(f"Destination site(s) not found in the graph: {missing_goals}")

    return origin_site_id, goal_site_ids


def build_problem_from_graph(graph, origin_site_id, destination_site_ids):
    goal_site_ids = normalize_goal_site_ids(destination_site_ids)
    origin_site_id, goal_site_ids = validate_problem_site_ids(
        graph,
        origin_site_id,
        goal_site_ids,
    )
    return BoroondaraProblem(
        initial=origin_site_id,
        goals=goal_site_ids,
        graph=graph,
    )


def build_dynamic_problem_from_bundle(
    locations_csv,
    connectivity_list,
    origin_site_id,
    destination_site_ids,
    model_bundle,
    recent_windows,
):
    graph, predicted_flows = build_updated_graph_from_bundle(
        locations_csv=locations_csv,
        connectivity_list=connectivity_list,
        model_bundle=model_bundle,
        recent_windows=recent_windows,
    )
    problem = build_problem_from_graph(
        graph=graph,
        origin_site_id=origin_site_id,
        destination_site_ids=destination_site_ids,
    )
    return problem, graph, predicted_flows


def build_dynamic_problem(
    locations_csv,
    connectivity_list,
    origin_site_id,
    destination_site_ids,
    model_name=DEFAULT_PROBLEM_MODEL_NAME,
    data_path=SCATS_DATA_PATH,
    model_path=None,
    metadata_path=None,
):
    graph, predicted_flows = build_updated_graph(
        locations_csv=locations_csv,
        connectivity_list=connectivity_list,
        model_name=model_name,
        data_path=data_path,
        model_path=model_path,
        metadata_path=metadata_path,
    )
    problem = build_problem_from_graph(
        graph=graph,
        origin_site_id=origin_site_id,
        destination_site_ids=destination_site_ids,
    )
    return problem, graph, predicted_flows


def load_bundle_windows_graph_and_problem(
    locations_csv,
    connectivity_list,
    origin_site_id,
    destination_site_ids,
    model_name=DEFAULT_PROBLEM_MODEL_NAME,
    data_path=SCATS_DATA_PATH,
    model_path=None,
    metadata_path=None,
):
    graph, predicted_flows, model_bundle, recent_windows = load_bundle_windows_and_graph(
        locations_csv=locations_csv,
        connectivity_list=connectivity_list,
        model_name=model_name,
        data_path=data_path,
        model_path=model_path,
        metadata_path=metadata_path,
    )
    problem = build_problem_from_graph(
        graph=graph,
        origin_site_id=origin_site_id,
        destination_site_ids=destination_site_ids,
    )
    return problem, graph, predicted_flows, model_bundle, recent_windows
