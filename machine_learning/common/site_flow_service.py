import argparse

from machine_learning.common.config import DEFAULT_WINDOW_SIZE, SCATS_DATA_PATH
from machine_learning.common.persistence import load_model_bundle
from machine_learning.common.prediction import predict_from_bundle
from utils.parse_data import parse_scats_data

DEFAULT_PREDICTION_MODEL_TYPE = "lightgbm"


def load_default_prediction_bundle(
    model_type=DEFAULT_PREDICTION_MODEL_TYPE,
    model_path=None,
    metadata_path=None,
):
    return load_model_bundle(
        model_type=model_type,
        model_path=model_path,
        metadata_path=metadata_path,
    )


def get_recent_windows_for_all_sites(path=SCATS_DATA_PATH, window_size=DEFAULT_WINDOW_SIZE):
    series_by_site = parse_scats_data(path)
    recent_windows = {}

    for site_id in sorted(series_by_site):
        site_series = series_by_site[site_id]

        if len(site_series) < window_size:
            raise ValueError(
                f"Site {site_id} does not have enough data for window size {window_size}."
            )

        recent_windows[site_id] = site_series[-window_size:]

    return recent_windows


def predict_all_sites_from_bundle(model_bundle, recent_windows):
    return {
        int(site_id): float(
            predict_from_bundle(
                model_bundle=model_bundle,
                recent_values=recent_values,
                site_id=site_id,
            )
        )
        for site_id, recent_values in recent_windows.items()
    }


def predict_all_sites(
    model_name=DEFAULT_PREDICTION_MODEL_TYPE,
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
        model_bundle.get("window_size", DEFAULT_WINDOW_SIZE),
    )
    return predict_all_sites_from_bundle(model_bundle, recent_windows)


def preview_site_predictions(site_predictions, limit=5):
    return sorted(site_predictions.items())[:limit]


def parse_args():
    parser = argparse.ArgumentParser(
        description="Predict the next traffic flow value for every SCATS site."
    )
    parser.add_argument(
        "--model-type",
        default=DEFAULT_PREDICTION_MODEL_TYPE,
        help="Saved model bundle to load. Defaults to LightGBM.",
    )
    parser.add_argument(
        "--data-path",
        default=SCATS_DATA_PATH,
        help="Path to the SCATS traffic dataset.",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=5,
        help="Number of sample site predictions to print.",
    )
    return parser.parse_args()


def main():
    args = parse_args()
    model_bundle = load_default_prediction_bundle(model_type=args.model_type)
    recent_windows = get_recent_windows_for_all_sites(
        args.data_path,
        model_bundle.get("window_size", DEFAULT_WINDOW_SIZE),
    )
    site_predictions = predict_all_sites_from_bundle(
        model_bundle,
        recent_windows,
    )

    print(f"Total predicted sites: {len(site_predictions)}")
    print(f"First {args.limit} site predictions:")
    for site_id, predicted_flow in preview_site_predictions(site_predictions, args.limit):
        print(f"{site_id}: {predicted_flow:.4f}")


if __name__ == "__main__":
    main()
