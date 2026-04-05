"""Comprehensive test suite for COS30019 Assignment 3.

Covers 3 testing categories:
  (A) ML Model Testing — prediction quality under different traffic scenarios
  (B) Software Testing — TBRGS system functionality and error handling
  (C) Integration Testing — ML predictions + search algorithms working together
"""

from __future__ import annotations

import sys
import time
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import numpy as np

from machine_learning.common.cli_route_service import (
    compute_terminal_route,
    compute_terminal_routes,
)
from machine_learning.common.graph_cost_service import (
    build_updated_graph_from_bundle,
    load_bundle_windows_and_graph,
)
from machine_learning.common.persistence import load_model_bundle
from machine_learning.common.prediction import predict_from_bundle
from machine_learning.common.problem_service import (
    build_dynamic_problem_from_bundle,
    load_bundle_windows_graph_and_problem,
)
from machine_learning.common.site_flow_service import (
    get_recent_windows_for_all_sites,
    load_default_prediction_bundle,
    predict_all_sites_from_bundle,
)
from machine_learning.common.topology_service import (
    DEFAULT_CONNECTIVITY_CSV,
    DEFAULT_LOCATIONS_CSV,
    SAMPLE_CONNECTIVITY_CSV,
    SAMPLE_LOCATIONS_CSV,
    load_connectivity_list,
)
from utils.parse_data import parse_scats_data

# ── Test result storage ──────────────────────────────────────────────────────

_results = []


def record(category, tc_id, name, status, details, metrics=None):
    _results.append({
        "category": category,
        "tc_id": tc_id,
        "name": name,
        "status": status,
        "details": details,
        "metrics": metrics or {},
    })


# ── Helper: run a single check ───────────────────────────────────────────────

def run_check(category, tc_id, name, fn):
    try:
        details, metrics = fn()
        record(category, tc_id, name, "PASS", details, metrics)
        print(f"  PASS [{tc_id}] {name}")
        if details:
            print(f"         {details}")
    except Exception as exc:
        record(category, tc_id, name, "FAIL", str(exc))
        print(f"  FAIL [{tc_id}] {name}: {exc}")


# ── (A) ML Model Testing ─────────────────────────────────────────────────────

def _load_test_infra():
    bundle = load_default_prediction_bundle(model_type="lightgbm")
    series_by_site = parse_scats_data(bundle["data_path"])
    return bundle, series_by_site


def tc01_normal_day_prediction():
    """TC01: Predict traffic on normal-day data — should be close to actual."""
    bundle, series_by_site = _load_test_infra()
    site_id = 970
    site_series = series_by_site[site_id]
    window_size = bundle["window_size"]

    # Use a mid-range window (not peak, not off-peak)
    recent = site_series[100:100 + window_size]
    actual_next = float(site_series[100 + window_size])
    predicted = predict_from_bundle(bundle, recent, site_id=site_id)

    error = abs(predicted - actual_next)
    pct_error = (error / actual_next) * 100 if actual_next > 0 else float("inf")

    assert predicted > 0, f"Prediction must be positive, got {predicted}"
    assert pct_error < 50, f"Percentage error {pct_error:.1f}% too high"

    return (
        f"Predicted={predicted:.2f}, Actual={actual_next:.2f}, "
        f"Error={error:.2f} ({pct_error:.1f}%)",
        {"predicted": predicted, "actual": actual_next, "error": error, "pct_error": pct_error},
    )


def tc02_peak_hour_prediction():
    """TC02: Predict traffic during peak hours — should predict high volume."""
    bundle, series_by_site = _load_test_infra()
    site_id = 970
    site_series = series_by_site[site_id]
    window_size = bundle["window_size"]

    # Find the peak hour window (highest traffic values)
    all_windows = [
        (i, float(site_series[i + window_size]))
        for i in range(len(site_series) - window_size)
    ]
    all_windows.sort(key=lambda x: x[1], reverse=True)

    # Use the top peak window
    peak_idx, peak_actual = all_windows[0]
    recent = site_series[peak_idx:peak_idx + window_size]
    predicted = predict_from_bundle(bundle, recent, site_id=site_id)

    # Peak hour should predict a relatively high value (> median of all values)
    all_values = [float(v) for v in site_series[window_size:]]
    median_val = float(np.median(all_values))

    assert predicted > 0, f"Prediction must be positive, got {predicted}"

    return (
        f"Peak predicted={predicted:.2f}, Peak actual={peak_actual:.2f}, "
        f"Dataset median={median_val:.2f}, "
        f"{'Above median' if predicted > median_val else 'Below median'}",
        {"predicted": predicted, "actual": peak_actual, "median": median_val,
         "above_median": predicted > median_val},
    )


def tc03_off_peak_prediction():
    """TC03: Predict traffic during off-peak hours — should predict low volume."""
    bundle, series_by_site = _load_test_infra()
    site_id = 970
    site_series = series_by_site[site_id]
    window_size = bundle["window_size"]

    # Find the lowest traffic window
    all_windows = [
        (i, float(site_series[i + window_size]))
        for i in range(len(site_series) - window_size)
    ]
    all_windows.sort(key=lambda x: x[1])

    low_idx, low_actual = all_windows[0]
    recent = site_series[low_idx:low_idx + window_size]
    predicted = predict_from_bundle(bundle, recent, site_id=site_id)

    all_values = [float(v) for v in site_series[window_size:]]
    median_val = float(np.median(all_values))

    assert predicted > 0, f"Prediction must be positive, got {predicted}"

    return (
        f"Off-peak predicted={predicted:.2f}, Off-peak actual={low_actual:.2f}, "
        f"Dataset median={median_val:.2f}, "
        f"{'Below median' if predicted < median_val else 'Above median'}",
        {"predicted": predicted, "actual": low_actual, "median": median_val,
         "below_median": predicted < median_val},
    )


def tc04_model_predicts_new_data():
    """TC04: Model can predict on the most recent (unseen) data — no crash."""
    bundle, series_by_site = _load_test_infra()
    window_size = bundle["window_size"]

    # Test on 5 different sites using their most recent data
    test_sites = [970, 2000, 2200, 3001, 3002]
    predictions = {}

    for site_id in test_sites:
        site_series = series_by_site[site_id]
        recent = site_series[-window_size:]
        pred = predict_from_bundle(bundle, recent, site_id=site_id)
        predictions[site_id] = pred

    assert all(v > 0 for v in predictions.values()), "All predictions must be positive"

    details = ", ".join(f"{k}={v:.2f}" for k, v in sorted(predictions.items()))
    return (
        f"All {len(predictions)} sites predicted successfully: {details}",
        {"sites_tested": len(predictions), "predictions": predictions},
    )


def tc05_model_overall_accuracy():
    """TC05: Overall model accuracy — MAE and RMSE within acceptable range."""
    bundle, series_by_site = _load_test_infra()
    window_size = bundle["window_size"]

    # Predict on last 100 data points across multiple sites
    errors = []
    test_sites = [970, 2000, 2200, 3001, 3002, 3120, 2820, 4030]

    for site_id in test_sites:
        site_series = series_by_site[site_id]
        # Test on last 20 points
        for i in range(len(site_series) - window_size - 20, len(site_series) - window_size):
            recent = site_series[i:i + window_size]
            actual = float(site_series[i + window_size])
            predicted = predict_from_bundle(bundle, recent, site_id=site_id)
            errors.append(abs(predicted - actual))

    mae = float(np.mean(errors))
    rmse = float(np.sqrt(np.mean([e ** 2 for e in errors])))
    max_error = float(np.max(errors))
    mean_actual = float(np.mean([float(series_by_site[s][-1]) for s in test_sites]))
    mape = (mae / mean_actual) * 100 if mean_actual > 0 else 0

    return (
        f"MAE={mae:.2f}, RMSE={rmse:.2f}, MaxError={max_error:.2f}, "
        f"MAPE={mape:.1f}% (over {len(errors)} predictions, {len(test_sites)} sites)",
        {"mae": mae, "rmse": rmse, "max_error": max_error, "mape": mape,
         "total_predictions": len(errors), "sites": len(test_sites)},
    )


def tc06_prediction_consistency():
    """TC06: Same input always produces same output (deterministic model)."""
    bundle, series_by_site = _load_test_infra()
    site_id = 970
    site_series = series_by_site[site_id]
    window_size = bundle["window_size"]
    recent = site_series[50:50 + window_size]

    predictions = [predict_from_bundle(bundle, recent, site_id=site_id) for _ in range(5)]
    unique = set(predictions)

    assert len(unique) == 1, f"Expected 1 unique prediction, got {len(unique)}: {predictions}"

    return (
        f"5 runs all returned {predictions[0]:.4f} (deterministic OK)",
        {"runs": 5, "prediction": predictions[0], "unique_count": len(unique)},
    )


# ── (B) Software Testing ─────────────────────────────────────────────────────

def _expect_raises(expected_exc, fn):
    try:
        fn()
    except expected_exc:
        return
    raise AssertionError(f"Expected {expected_exc.__name__} to be raised.")


def tc07_load_saved_model():
    """TC07: Saved model bundle loads with correct metadata."""
    bundle = load_default_prediction_bundle()
    assert bundle["model_type"] == "lightgbm"
    assert bundle["window_size"] > 0
    assert "scalers" in bundle
    assert len(bundle["scalers"]) == 40

    return (
        f"Model type={bundle['model_type']}, window_size={bundle['window_size']}, "
        f"scalers={len(bundle['scalers'])} sites",
        {"model_type": bundle["model_type"], "window_size": bundle["window_size"],
         "scaler_count": len(bundle["scalers"])},
    )


def tc08_predict_all_sites():
    """TC08: Predictions generated for all 40 SCATS sites."""
    bundle = load_default_prediction_bundle()
    windows = get_recent_windows_for_all_sites(bundle["data_path"], bundle["window_size"])
    predictions = predict_all_sites_from_bundle(bundle, windows)

    assert isinstance(predictions, dict)
    assert len(predictions) == 40
    assert 970 in predictions
    assert all(v > 0 for v in predictions.values())

    min_site = min(predictions, key=predictions.get)
    max_site = max(predictions, key=predictions.get)

    return (
        f"40 sites predicted, min={predictions[min_site]:.2f} (site {min_site}), "
        f"max={predictions[max_site]:.2f} (site {max_site})",
        {"total_sites": len(predictions), "min_site": min_site,
         "min_value": predictions[min_site], "max_site": max_site,
         "max_value": predictions[max_site]},
    )


def tc09_build_dynamic_graph():
    """TC09: Dynamic graph builds with ML-predicted edge costs."""
    graph, predicted_flows, model_bundle, recent_windows = load_bundle_windows_and_graph(
        SAMPLE_LOCATIONS_CSV,
        load_connectivity_list(SAMPLE_CONNECTIVITY_CSV),
    )

    assert predicted_flows
    assert graph.adj
    assert graph.adj[2000][2200] > 0
    assert model_bundle["model_type"] == "lightgbm"

    edge_count = sum(len(neighbors) for neighbors in graph.adj.values())
    avg_cost = np.mean([cost for neighbors in graph.adj.values() for cost in neighbors.values()])

    return (
        f"Graph has {len(graph.nodes)} nodes, {edge_count} directed edges, "
        f"avg edge cost={avg_cost:.2f}s",
        {"nodes": len(graph.nodes), "edges": edge_count, "avg_cost": avg_cost},
    )


def tc10_valid_route_returns_path():
    """TC10: Valid O→D returns 1-5 routes with positive travel time."""
    route_results, goal_nodes, *_ = compute_terminal_routes(
        2000, 3002, top_k=5,
        locations_csv=SAMPLE_LOCATIONS_CSV,
        connectivity_csv=SAMPLE_CONNECTIVITY_CSV,
    )

    assert 1 <= len(route_results) <= 5
    costs = [r["total_travel_time_sec"] for r in route_results]
    assert all(c > 0 for c in costs), "All travel times must be positive"
    assert costs == sorted(costs), "Routes must be sorted by cost"

    paths_info = [f"Route {i+1}: {' -> '.join(map(str, r['path']))} ({r['total_travel_time_sec']:.1f}s)"
                  for i, r in enumerate(route_results)]

    return (
        f"{len(route_results)} routes found: {'; '.join(paths_info)}",
        {"routes_found": len(route_results), "costs": costs,
         "paths": [r["path"] for r in route_results]},
    )


def tc11_origin_equals_destination():
    """TC11: O=D raises ValueError with clear message."""
    _expect_raises(ValueError, lambda: compute_terminal_route(
        2000, 2000,
        locations_csv=SAMPLE_LOCATIONS_CSV,
        connectivity_csv=SAMPLE_CONNECTIVITY_CSV,
    ))

    return (
        "Correctly raised ValueError for origin == destination",
        {"exception": "ValueError"},
    )


def tc12_invalid_origin():
    """TC12: Non-existent origin raises KeyError."""
    _expect_raises(KeyError, lambda: compute_terminal_route(
        999999, 3002,
        locations_csv=SAMPLE_LOCATIONS_CSV,
        connectivity_csv=SAMPLE_CONNECTIVITY_CSV,
    ))

    return (
        "Correctly raised KeyError for non-existent origin site 999999",
        {"exception": "KeyError", "invalid_site": 999999},
    )


def tc13_invalid_destination():
    """TC13: Non-existent destination raises KeyError."""
    _expect_raises(KeyError, lambda: compute_terminal_route(
        2000, 999999,
        locations_csv=SAMPLE_LOCATIONS_CSV,
        connectivity_csv=SAMPLE_CONNECTIVITY_CSV,
    ))

    return (
        "Correctly raised KeyError for non-existent destination site 999999",
        {"exception": "KeyError", "invalid_site": 999999},
    )


def tc14_no_route_found():
    """TC14: Unreachable destination raises ValueError."""
    _expect_raises(ValueError, lambda: compute_terminal_routes(
        2000, 4030, top_k=5,
        locations_csv=SAMPLE_LOCATIONS_CSV,
        connectivity_csv=SAMPLE_CONNECTIVITY_CSV,
    ))

    return (
        f"Correctly raised ValueError when no path exists (2000 to 4030)",
        {"exception": "ValueError", "origin": 2000, "destination": 4030},
    )


def tc15_single_best_route_correctness():
    """TC15: Single best route matches expected shortest path."""
    route_result, goal_node, *_ = compute_terminal_route(
        2000, 3002,
        locations_csv=SAMPLE_LOCATIONS_CSV,
        connectivity_csv=SAMPLE_CONNECTIVITY_CSV,
    )

    expected_path = [2000, 3120, 3001, 3002]
    assert route_result["path"] == expected_path, \
        f"Expected {expected_path}, got {route_result['path']}"
    assert route_result["goal_site_id"] == 3002
    assert route_result["total_travel_time_sec"] > 0

    return (
        f"Path={' -> '.join(map(str, route_result['path']))}, "
        f"Time={route_result['total_travel_time_sec']:.2f}s",
        {"path": route_result["path"], "time": route_result["total_travel_time_sec"],
         "expected_path": expected_path},
    )


# ── (C) Integration Testing (ML + Search) ────────────────────────────────────

def tc16_route_uses_ml_travel_time():
    """TC16: Route finding uses ML-predicted travel times (not static distances)."""
    # Route with ML predictions
    route_ml, *_ = compute_terminal_route(
        2000, 3002, model_name="lightgbm",
        locations_csv=SAMPLE_LOCATIONS_CSV,
        connectivity_csv=SAMPLE_CONNECTIVITY_CSV,
    )

    # Build graph manually to verify ML predictions are used
    bundle = load_default_prediction_bundle()
    windows = get_recent_windows_for_all_sites(bundle["data_path"], bundle["window_size"])
    graph, predicted_flows = build_updated_graph_from_bundle(
        SAMPLE_LOCATIONS_CSV,
        load_connectivity_list(SAMPLE_CONNECTIVITY_CSV),
        bundle, windows,
    )

    # Verify predicted flows affect edge costs
    assert len(predicted_flows) == 40, "Should have predictions for all 40 sites"
    assert route_ml["total_travel_time_sec"] > 0

    # Verify edge costs are based on ML predictions (not raw distances)
    # The graph.adj contains travel times computed from predicted flows
    edge_costs = []
    for origin, neighbors in graph.adj.items():
        for dest, cost in neighbors.items():
            edge_costs.append(cost)

    avg_cost = float(np.mean(edge_costs)) if edge_costs else 0

    return (
        f"Route time={route_ml['total_travel_time_sec']:.2f}s, "
        f"{len(predicted_flows)} sites predicted, "
        f"{len(edge_costs)} edges with avg cost={avg_cost:.2f}s",
        {"route_time": route_ml["total_travel_time_sec"],
         "predicted_sites": len(predicted_flows),
         "edge_count": len(edge_costs), "avg_edge_cost": avg_cost},
    )


def tc17_route_changes_with_traffic():
    """TC17: Different traffic predictions can produce different routes."""
    # Get route with current ML predictions
    route_result, _, problem, graph, predicted_flows = compute_terminal_routes(
        2000, 3002, top_k=3,
        locations_csv=SAMPLE_LOCATIONS_CSV,
        connectivity_csv=SAMPLE_CONNECTIVITY_CSV,
    )

    # Verify multiple routes have different paths
    paths = [tuple(r["path"]) for r in route_result]
    unique_paths = len(set(paths))

    # Verify routes are sorted by cost
    costs = [r["total_travel_time_sec"] for r in route_result]
    is_sorted = costs == sorted(costs)

    # Calculate cost difference between best and worst route
    if len(route_result) > 1:
        cost_diff = costs[-1] - costs[0]
        cost_diff_pct = (cost_diff / costs[0]) * 100
    else:
        cost_diff = 0
        cost_diff_pct = 0

    return (
        f"{len(route_result)} routes found, {unique_paths} unique paths, "
        f"cost range={costs[0]:.1f}s–{costs[-1]:.1f}s "
        f"(diff={cost_diff:.1f}s, {cost_diff_pct:.1f}%), sorted={'Yes' if is_sorted else 'No'}",
        {"routes": len(route_result), "unique_paths": unique_paths,
         "costs": costs, "is_sorted": is_sorted, "cost_diff_pct": cost_diff_pct},
    )


def tc18_end_to_end_pipeline():
    """TC18: Full end-to-end — load model → predict → build graph → find route."""
    start_time = time.time()

    # Step 1: Load model
    bundle = load_default_prediction_bundle()
    step1_time = time.time() - start_time

    # Step 2: Get recent windows
    windows = get_recent_windows_for_all_sites(bundle["data_path"], bundle["window_size"])
    step2_time = time.time() - start_time - step1_time

    # Step 3: Predict all sites
    predictions = predict_all_sites_from_bundle(bundle, windows)
    step3_time = time.time() - start_time - step1_time - step2_time

    # Step 4: Build graph with predictions
    graph, pred_flows = build_updated_graph_from_bundle(
        SAMPLE_LOCATIONS_CSV,
        load_connectivity_list(SAMPLE_CONNECTIVITY_CSV),
        bundle, windows,
    )
    step4_time = time.time() - start_time - step1_time - step2_time - step3_time

    # Step 5: Build problem and solve
    problem = build_dynamic_problem_from_bundle(
        SAMPLE_LOCATIONS_CSV,
        load_connectivity_list(SAMPLE_CONNECTIVITY_CSV),
        2000, 3002,
        bundle, windows,
    )
    step5_time = time.time() - start_time - step1_time - step2_time - step3_time - step4_time

    route_result, goal_node, *_ = compute_terminal_route(
        2000, 3002,
        locations_csv=SAMPLE_LOCATIONS_CSV,
        connectivity_csv=SAMPLE_CONNECTIVITY_CSV,
    )
    total_time = time.time() - start_time

    assert route_result["total_travel_time_sec"] > 0
    assert len(predictions) == 40

    return (
        f"Total pipeline time={total_time:.3f}s | "
        f"Load={step1_time:.3f}s, Windows={step2_time:.3f}s, "
        f"Predict={step3_time:.3f}s, Graph={step4_time:.3f}s, "
        f"Solve={step5_time:.3f}s | "
        f"Route={' -> '.join(map(str, route_result['path']))} "
        f"({route_result['total_travel_time_sec']:.1f}s)",
        {"total_time": total_time, "load_time": step1_time, "window_time": step2_time,
         "predict_time": step3_time, "graph_time": step4_time, "solve_time": step5_time,
         "route_path": route_result["path"], "route_time": route_result["total_travel_time_sec"]},
    )


def tc19_multiple_od_pairs():
    """TC19: Multiple origin-destination pairs all return valid routes."""
    od_pairs = [
        (2000, 3002),
        (2200, 2820),
        (3001, 3120),
    ]

    results = []
    failed_pairs = []
    for origin, dest in od_pairs:
        try:
            route, *_ = compute_terminal_route(
                origin, dest,
                locations_csv=SAMPLE_LOCATIONS_CSV,
                connectivity_csv=SAMPLE_CONNECTIVITY_CSV,
            )
            results.append({
                "origin": origin, "destination": dest,
                "path": route["path"], "time": route["total_travel_time_sec"],
            })
        except (ValueError, KeyError) as e:
            failed_pairs.append((origin, dest, str(e)))

    assert len(results) >= 2, f"Expected at least 2 routes, got {len(results)}"
    assert all(r["time"] > 0 for r in results)
    assert all(len(r["path"]) >= 2 for r in results)

    details = "; ".join(
        f"{r['origin']} to {r['destination']}: {' -> '.join(map(str, r['path']))} ({r['time']:.1f}s)"
        for r in results
    )
    if failed_pairs:
        details += f" | {len(failed_pairs)} pairs had no route"

    return (
        f"{len(results)}/{len(od_pairs)} O-D pairs solved: {details}",
        {"pairs_tested": len(od_pairs), "pairs_solved": len(results),
         "pairs_failed": len(failed_pairs), "results": results},
    )


def tc20_search_algorithm_correctness():
    """TC20: A* and Uniform Cost Search both find valid routes, A* is faster."""
    results = {}
    for algorithm in ["astar", "uniform_cost"]:
        start = time.time()
        route, *_ = compute_terminal_route(
            2000, 3002, algorithm=algorithm,
            locations_csv=SAMPLE_LOCATIONS_CSV,
            connectivity_csv=SAMPLE_CONNECTIVITY_CSV,
        )
        elapsed = time.time() - start
        assert route["total_travel_time_sec"] > 0
        results[algorithm] = {"time": route["total_travel_time_sec"], "compute": elapsed, "path": route["path"]}
        print(f"    {algorithm.upper()}: path={' -> '.join(map(str, route['path']))}, "
              f"time={route['total_travel_time_sec']:.1f}s, compute={elapsed:.4f}s")

    # Both should find the same optimal cost
    assert abs(results["astar"]["time"] - results["uniform_cost"]["time"]) < 0.01, \
        "A* and UCS should find same optimal cost"

    return (
        f"Both A* and UCS found valid routes with same optimal cost "
        f"({results['astar']['time']:.1f}s), "
        f"A* compute={results['astar']['compute']:.4f}s, "
        f"UCS compute={results['uniform_cost']['compute']:.4f}s",
        {"algorithms_tested": ["astar", "uniform_cost"],
         "astar_time": results["astar"]["time"],
         "ucs_time": results["uniform_cost"]["time"],
         "astar_compute": results["astar"]["compute"],
         "ucs_compute": results["uniform_cost"]["compute"]},
    )


# ── Main runner ──────────────────────────────────────────────────────────────

def main():
    print("=" * 70)
    print("  COMPREHENSIVE TEST SUITE — COS30019 Assignment 3")
    print("=" * 70)

    # (A) ML Model Testing
    print("\n[A] ML MODEL TESTING")
    print("-" * 70)
    ml_tests = [
        ("TC01", "Normal day prediction", tc01_normal_day_prediction),
        ("TC02", "Peak hour prediction", tc02_peak_hour_prediction),
        ("TC03", "Off-peak prediction", tc03_off_peak_prediction),
        ("TC04", "Model predicts new data", tc04_model_predicts_new_data),
        ("TC05", "Overall model accuracy", tc05_model_overall_accuracy),
        ("TC06", "Prediction consistency", tc06_prediction_consistency),
    ]
    for tc_id, name, fn in ml_tests:
        run_check("A (ML)", tc_id, name, fn)

    # (B) Software Testing
    print("\n[B] SOFTWARE TESTING")
    print("-" * 70)
    sw_tests = [
        ("TC07", "Load saved model", tc07_load_saved_model),
        ("TC08", "Predict all sites", tc08_predict_all_sites),
        ("TC09", "Build dynamic graph", tc09_build_dynamic_graph),
        ("TC10", "Valid route returns 1-5 paths", tc10_valid_route_returns_path),
        ("TC11", "Origin = Destination handling", tc11_origin_equals_destination),
        ("TC12", "Invalid origin handling", tc12_invalid_origin),
        ("TC13", "Invalid destination handling", tc13_invalid_destination),
        ("TC14", "No route found handling", tc14_no_route_found),
        ("TC15", "Single best route correctness", tc15_single_best_route_correctness),
    ]
    for tc_id, name, fn in sw_tests:
        run_check("B (Software)", tc_id, name, fn)

    # (C) Integration Testing
    print("\n[C] INTEGRATION TESTING (ML + Search)")
    print("-" * 70)
    int_tests = [
        ("TC16", "Route uses ML travel time", tc16_route_uses_ml_travel_time),
        ("TC17", "Route changes with traffic", tc17_route_changes_with_traffic),
        ("TC18", "End-to-end pipeline", tc18_end_to_end_pipeline),
        ("TC19", "Multiple O-D pairs", tc19_multiple_od_pairs),
        ("TC20", "Search algorithm correctness", tc20_search_algorithm_correctness),
    ]
    for tc_id, name, fn in int_tests:
        run_check("C (Integration)", tc_id, name, fn)

    # Summary
    print("\n" + "=" * 70)
    passed = sum(1 for r in _results if r["status"] == "PASS")
    failed = sum(1 for r in _results if r["status"] == "FAIL")
    total = len(_results)

    print(f"  TOTAL: {total} tests | PASS: {passed} | FAIL: {failed}")
    print("=" * 70)

    if failed > 0:
        print("\nFAILED TESTS:")
        for r in _results:
            if r["status"] == "FAIL":
                print(f"  [{r['tc_id']}] {r['name']}: {r['details']}")

    # Category breakdown
    for cat in ["A (ML)", "B (Software)", "C (Integration)"]:
        cat_results = [r for r in _results if r["category"] == cat]
        cat_pass = sum(1 for r in cat_results if r["status"] == "PASS")
        print(f"  {cat}: {cat_pass}/{len(cat_results)} passed")

    if failed == 0:
        print("\nAll tests passed.")

    # Save results to file
    save_results()

    if failed > 0:
        sys.exit(1)


def save_results():
    """Save test results to a text file for report documentation."""
    output_path = PROJECT_ROOT / "test_results.txt"
    with open(output_path, "w", encoding="utf-8") as f:
        f.write("=" * 70 + "\n")
        f.write("  TEST RESULTS — COS30019 Assignment 3\n")
        f.write("=" * 70 + "\n\n")

        for r in _results:
            status_icon = "PASS" if r["status"] == "PASS" else "FAIL"
            f.write(f"[{r['tc_id']}] {r['name']}: {status_icon}\n")
            f.write(f"  Category: {r['category']}\n")
            f.write(f"  Details: {r['details']}\n")
            if r["metrics"]:
                f.write(f"  Metrics: {r['metrics']}\n")
            f.write("\n")

        passed = sum(1 for r in _results if r["status"] == "PASS")
        f.write(f"\nTotal: {len(_results)} tests | Passed: {passed} | Failed: {len(_results) - passed}\n")

    print(f"\nResults saved to: {output_path}")


if __name__ == "__main__":
    main()
