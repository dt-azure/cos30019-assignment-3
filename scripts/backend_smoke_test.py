"""Practical smoke checks for the non-GUI backend pipeline."""

from machine_learning.common.cli_route_service import (
    compute_terminal_route,
    compute_terminal_routes,
)
from machine_learning.common.graph_cost_service import load_bundle_windows_and_graph
from machine_learning.common.problem_service import load_bundle_windows_graph_and_problem
from machine_learning.common.site_flow_service import (
    get_recent_windows_for_all_sites,
    load_default_prediction_bundle,
    predict_all_sites_from_bundle,
)
from machine_learning.common.topology_service import (
    DEFAULT_CONNECTIVITY_CSV,
    DEFAULT_LOCATIONS_CSV,
    load_connectivity_list,
)

DEFAULT_SAMPLE_CONNECTIVITY = load_connectivity_list(DEFAULT_CONNECTIVITY_CSV)


def run_check(name, fn):
    try:
        fn()
    except Exception as exc:
        print(f"FAIL - {name}: {exc}")
        raise

    print(f"PASS - {name}")


def expect_raises(expected_exception, fn):
    try:
        fn()
    except expected_exception:
        return

    raise AssertionError(f"Expected {expected_exception.__name__} to be raised.")


def check_load_saved_model():
    bundle = load_default_prediction_bundle()
    assert bundle["model_type"] == "lightgbm"
    assert bundle["window_size"] > 0
    assert "scalers" in bundle


def check_predict_all_sites():
    bundle = load_default_prediction_bundle()
    windows = get_recent_windows_for_all_sites(bundle["data_path"], bundle["window_size"])
    predictions = predict_all_sites_from_bundle(bundle, windows)
    assert isinstance(predictions, dict)
    assert len(predictions) == 40
    assert 970 in predictions


def check_build_dynamic_graph():
    graph, predicted_flows, model_bundle, recent_windows = load_bundle_windows_and_graph(
        DEFAULT_LOCATIONS_CSV,
        DEFAULT_SAMPLE_CONNECTIVITY,
    )
    assert predicted_flows
    assert graph.adj
    assert graph.adj[2000][2200] > 0
    assert model_bundle["model_type"] == "lightgbm"
    assert recent_windows[2000] is not None


def check_build_dynamic_problem():
    problem, graph, predicted_flows, model_bundle, recent_windows = (
        load_bundle_windows_graph_and_problem(
            DEFAULT_LOCATIONS_CSV,
            DEFAULT_SAMPLE_CONNECTIVITY,
            origin_site_id=2000,
            destination_site_ids=3002,
        )
    )
    assert problem.initial == 2000
    assert 3002 in problem.goals
    assert 2200 in dict(problem.graph.get_neighbors(2000))
    assert predicted_flows
    assert model_bundle["model_type"] == "lightgbm"
    assert recent_windows[2000] is not None


def check_single_best_route():
    route_result, goal_node, *_ = compute_terminal_route(2000, 3002)
    assert route_result["path"] == [2000, 3120, 3001, 3002]
    assert route_result["goal_site_id"] == 3002
    assert route_result["total_travel_time_sec"] > 0
    assert goal_node.state == 3002


def check_top_k_routes():
    route_results, goal_nodes, *_ = compute_terminal_routes(2000, 3002, top_k=5)
    assert 1 <= len(route_results) <= 5
    assert len(route_results) == 2
    costs = [route["total_travel_time_sec"] for route in route_results]
    assert costs == sorted(costs)
    paths = [tuple(route["path"]) for route in route_results]
    assert len(paths) == len(set(paths))
    assert route_results[0]["path"] == [2000, 3120, 3001, 3002]
    assert route_results[1]["path"] == [2000, 2200, 2820, 3001, 3002]
    assert len(goal_nodes) == len(route_results)


def check_invalid_origin():
    expect_raises(KeyError, lambda: compute_terminal_route(999999, 3002))


def check_invalid_destination():
    expect_raises(KeyError, lambda: compute_terminal_route(2000, 999999))


def check_origin_equals_destination():
    expect_raises(ValueError, lambda: compute_terminal_route(2000, 2000))


def check_no_route():
    expect_raises(ValueError, lambda: compute_terminal_routes(2000, 4030, top_k=5))


def main():
    checks = [
        ("load saved model", check_load_saved_model),
        ("predict all sites", check_predict_all_sites),
        ("build dynamic graph", check_build_dynamic_graph),
        ("build dynamic routing problem", check_build_dynamic_problem),
        ("solve single best route", check_single_best_route),
        ("solve top-k routes", check_top_k_routes),
        ("invalid origin handling", check_invalid_origin),
        ("invalid destination handling", check_invalid_destination),
        ("origin equals destination handling", check_origin_equals_destination),
        ("no-route handling", check_no_route),
    ]

    for name, fn in checks:
        run_check(name, fn)

    print("All backend smoke checks passed.")


if __name__ == "__main__":
    main()
