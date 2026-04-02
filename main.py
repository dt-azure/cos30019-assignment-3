import argparse
import sys

from machine_learning.common.cli_route_service import (
    DEFAULT_CLI_ALGORITHM,
    DEFAULT_CLI_MODEL_NAME,
    compute_terminal_route,
    compute_terminal_routes,
    format_route_result,
    format_route_results,
)
from machine_learning.common.topology_service import (
    DEFAULT_CONNECTIVITY_CSV,
    DEFAULT_LOCATIONS_CSV,
)


def parse_args():
    parser = argparse.ArgumentParser(
        description="Run the end-to-end dynamic routing pipeline from the terminal."
    )
    parser.add_argument("--origin", type=int, required=True, help="Origin SCATS site ID.")
    parser.add_argument(
        "--destination",
        type=int,
        required=True,
        help="Destination SCATS site ID.",
    )
    parser.add_argument(
        "--model",
        default=DEFAULT_CLI_MODEL_NAME,
        help="Prediction model to use. Defaults to LightGBM.",
    )
    parser.add_argument(
        "--algorithm",
        default=DEFAULT_CLI_ALGORITHM,
        choices=["astar", "uniform_cost"],
        help="Search algorithm to use.",
    )
    parser.add_argument(
        "--locations-csv",
        default=DEFAULT_LOCATIONS_CSV,
        help="CSV file containing graph node coordinates.",
    )
    parser.add_argument(
        "--connectivity-csv",
        default=DEFAULT_CONNECTIVITY_CSV,
        help="CSV file containing directed graph edges and distances.",
    )
    parser.add_argument(
        "--top-k",
        type=int,
        default=1,
        choices=range(1, 6),
        help="Number of routes to return, from 1 to 5.",
    )
    return parser.parse_args()


def main():
    args = parse_args()

    try:
        if args.top_k == 1:
            route_result, *_ = compute_terminal_route(
                origin_site_id=args.origin,
                destination_site_id=args.destination,
                model_name=args.model,
                algorithm=args.algorithm,
                locations_csv=args.locations_csv,
                connectivity_csv=args.connectivity_csv,
            )
        else:
            route_results, *_ = compute_terminal_routes(
                origin_site_id=args.origin,
                destination_site_id=args.destination,
                model_name=args.model,
                algorithm=args.algorithm,
                top_k=args.top_k,
                locations_csv=args.locations_csv,
                connectivity_csv=args.connectivity_csv,
            )
    except KeyError as exc:
        message = exc.args[0] if exc.args else str(exc)
        print(f"Error: {message}", file=sys.stderr)
        raise SystemExit(2)
    except (FileNotFoundError, ValueError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        raise SystemExit(2)

    if args.top_k == 1:
        print(
            format_route_result(
                route_result=route_result,
                origin_site_id=args.origin,
                destination_site_id=args.destination,
                model_name=args.model,
            )
        )
    else:
        print(
            format_route_results(
                route_results=route_results,
                origin_site_id=args.origin,
                destination_site_id=args.destination,
                model_name=args.model,
                top_k=args.top_k,
            )
        )


if __name__ == "__main__":
    main()
