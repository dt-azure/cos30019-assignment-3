import argparse
from importlib import import_module

SCATS_DATA_PATH = "data/scats_data_october_2006.xls"
DEFAULT_WINDOW_SIZE = 4
DEFAULT_TEST_RATIO = 0.2
DEFAULT_VALIDATION_RATIO = 0.2
DEFAULT_EPOCHS = 5
DEFAULT_BATCH_SIZE = 32

MODEL_RUNNERS = {
    "lstm": ("LSTM", "machine_learning.lstm", "lstm"),
    "gru": ("GRU", "machine_learning.gru", "gru"),
    "lightgbm": ("LightGBM", "machine_learning.lightgbm", "lightgbm_model"),
}

TABLE_COLUMNS = [
    ("model", "Model"),
    ("train_loss", "Train Loss"),
    ("val_loss", "Val Loss"),
    ("mae", "MAE"),
    ("mse", "MSE"),
    ("rmse", "RMSE"),
    ("training_time_sec", "Time (s)"),
]


def parse_args():
    parser = argparse.ArgumentParser(
        description="Run and compare the non-random-forest traffic prediction models."
    )
    parser.add_argument(
        "--data-path",
        default=SCATS_DATA_PATH,
        help="Path to the SCATS traffic data spreadsheet.",
    )
    parser.add_argument(
        "--models",
        nargs="+",
        choices=list(MODEL_RUNNERS.keys()),
        default=list(MODEL_RUNNERS.keys()),
        help="Subset of models to run.",
    )
    parser.add_argument(
        "--window-size",
        type=int,
        default=DEFAULT_WINDOW_SIZE,
        help="Number of recent 15-minute values used as input features.",
    )
    parser.add_argument(
        "--test-ratio",
        type=float,
        default=DEFAULT_TEST_RATIO,
        help="Fraction of the latest data reserved for testing.",
    )
    parser.add_argument(
        "--validation-ratio",
        type=float,
        default=DEFAULT_VALIDATION_RATIO,
        help="Fraction of the training period reserved for validation.",
    )
    parser.add_argument(
        "--epochs",
        type=int,
        default=DEFAULT_EPOCHS,
        help="Training epochs for sequence models.",
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=DEFAULT_BATCH_SIZE,
        help="Batch size for sequence models.",
    )
    parser.add_argument(
        "--save-models",
        action="store_true",
        help="Save trained models and metadata into saved_models/ after training.",
    )
    return parser.parse_args()


def format_metric(metric_name, value):
    if metric_name == "model":
        return str(value)

    if value is None:
        return "N/A"

    if isinstance(value, (int, float)):
        precision = 2 if metric_name == "training_time_sec" else 4
        return f"{value:.{precision}f}"

    return str(value)


def build_table_rows(results):
    headers = [label for _, label in TABLE_COLUMNS]
    rows = []

    for result in results:
        row = [format_metric(metric_name, result.get(metric_name)) for metric_name, _ in TABLE_COLUMNS]
        rows.append(row)

    return headers, rows


def print_results_table(results):
    headers, rows = build_table_rows(results)

    widths = []
    for index, header in enumerate(headers):
        column_width = max(len(header), *(len(row[index]) for row in rows))
        widths.append(column_width)

    def format_row(values):
        return " | ".join(value.ljust(widths[index]) for index, value in enumerate(values))

    separator = "-+-".join("-" * width for width in widths)

    print("\n========== MODEL COMPARISON ==========")
    print(format_row(headers))
    print(separator)
    for row in rows:
        print(format_row(row))


def run_model(model_key, args):
    model_name, module_path, function_name = MODEL_RUNNERS[model_key]
    runner = getattr(import_module(module_path), function_name)
    print(f"\nRunning {model_name}...")

    _, results = runner(
        args.data_path,
        window_size=args.window_size,
        test_ratio=args.test_ratio,
        validation_ratio=args.validation_ratio,
        epochs=args.epochs,
        batch_size=args.batch_size,
        save=args.save_models,
    )
    results["model"] = model_name
    return results


def main():
    args = parse_args()

    results = []
    failures = []

    for model_key in args.models:
        try:
            results.append(run_model(model_key, args))
        except Exception as exc:
            model_name = MODEL_RUNNERS[model_key][0]
            failures.append((model_name, exc))
            print(f"{model_name} failed: {exc.__class__.__name__}: {exc}")

    if results:
        print_results_table(results)

    if failures:
        print("\n========== FAILED RUNS ==========")
        for model_name, exc in failures:
            print(f"{model_name}: {exc.__class__.__name__}: {exc}")

    if not results:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
