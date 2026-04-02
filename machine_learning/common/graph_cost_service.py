from machine_learning.common.config import SCATS_DATA_PATH
from machine_learning.common.site_flow_service import (
    get_recent_windows_for_all_sites,
    load_default_prediction_bundle,
    predict_all_sites,
    predict_all_sites_from_bundle,
)
from utils.graph import BoroondaraGraph

DEFAULT_GRAPH_MODEL_NAME = "lightgbm"


def build_boroondara_graph(locations_csv, connectivity_list):
    return BoroondaraGraph(locations_csv, connectivity_list)


def update_graph_edge_costs(graph, predicted_flows):
    graph.update_edge_costs(predicted_flows)
    return graph


def build_updated_graph_from_predictions(locations_csv, connectivity_list, predicted_flows):
    graph = build_boroondara_graph(locations_csv, connectivity_list)
    update_graph_edge_costs(graph, predicted_flows)
    return graph


def build_updated_graph_from_bundle(
    locations_csv,
    connectivity_list,
    model_bundle,
    recent_windows,
):
    predicted_flows = predict_all_sites_from_bundle(model_bundle, recent_windows)
    graph = build_updated_graph_from_predictions(
        locations_csv=locations_csv,
        connectivity_list=connectivity_list,
        predicted_flows=predicted_flows,
    )
    return graph, predicted_flows


def build_updated_graph(
    locations_csv,
    connectivity_list,
    model_name=DEFAULT_GRAPH_MODEL_NAME,
    data_path=SCATS_DATA_PATH,
    model_path=None,
    metadata_path=None,
):
    predicted_flows = predict_all_sites(
        model_name=model_name,
        data_path=data_path,
        model_path=model_path,
        metadata_path=metadata_path,
    )
    graph = build_updated_graph_from_predictions(
        locations_csv=locations_csv,
        connectivity_list=connectivity_list,
        predicted_flows=predicted_flows,
    )
    return graph, predicted_flows


def load_bundle_windows_and_graph(
    locations_csv,
    connectivity_list,
    model_name=DEFAULT_GRAPH_MODEL_NAME,
    data_path=SCATS_DATA_PATH,
    model_path=None,
    metadata_path=None,
):
    model_bundle = load_default_prediction_bundle(
        model_type=model_name,
        model_path=model_path,
        metadata_path=metadata_path,
    )
    recent_windows = get_recent_windows_for_all_sites(
        data_path,
        model_bundle["window_size"],
    )
    graph, predicted_flows = build_updated_graph_from_bundle(
        locations_csv=locations_csv,
        connectivity_list=connectivity_list,
        model_bundle=model_bundle,
        recent_windows=recent_windows,
    )
    return graph, predicted_flows, model_bundle, recent_windows
