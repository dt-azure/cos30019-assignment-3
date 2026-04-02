import tkinter as tk
from tkinter import ttk

from gui.controllers import compute_gui_routes, get_available_models, get_default_data_sources
from gui.formatters import (
    format_data_sources,
    format_error_message,
    format_initial_message,
    format_route_results,
)
from gui.widgets import DataSourcesPanel, RouteControls, RouteResultsPanel


class RouteGuiApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("COS30019 Assignment 2B Route Guidance")
        self.geometry("920x720")
        self.minsize(780, 620)

        self.data_sources = get_default_data_sources()
        self.available_models = get_available_models()
        self.status_var = tk.StringVar(value="Ready.")

        self.columnconfigure(0, weight=1)
        self.rowconfigure(2, weight=1)

        self._build_layout()

    def _build_layout(self):
        container = ttk.Frame(self, padding=16)
        container.grid(row=0, column=0, sticky="nsew")
        container.columnconfigure(0, weight=1)
        container.rowconfigure(2, weight=1)

        header = ttk.Label(
            container,
            text="Traffic-Based Route Guidance System",
            font=("TkDefaultFont", 16, "bold"),
        )
        header.grid(row=0, column=0, sticky="w")

        subtitle = ttk.Label(
            container,
            text="Compute the best route or top-k routes using the existing dynamic backend pipeline.",
        )
        subtitle.grid(row=1, column=0, sticky="w", pady=(4, 12))

        top_frame = ttk.Frame(container)
        top_frame.grid(row=2, column=0, sticky="ew")
        top_frame.columnconfigure(0, weight=3)
        top_frame.columnconfigure(1, weight=2)

        self.controls = RouteControls(
            top_frame,
            models=self.available_models,
            on_submit=self.handle_compute_routes,
        )
        self.controls.grid(row=0, column=0, sticky="nsew", padx=(0, 12))

        self.data_sources_panel = DataSourcesPanel(
            top_frame,
            formatted_sources=format_data_sources(self.data_sources),
        )
        self.data_sources_panel.grid(row=0, column=1, sticky="nsew")

        self.results_panel = RouteResultsPanel(container)
        self.results_panel.grid(row=3, column=0, sticky="nsew", pady=(12, 0))
        self.results_panel.set_text(format_initial_message(self.data_sources))

        status_bar = ttk.Label(
            container,
            textvariable=self.status_var,
            anchor="w",
        )
        status_bar.grid(row=4, column=0, sticky="ew", pady=(10, 0))

        self.controls.focus_origin()

    def handle_compute_routes(self):
        request_values = self.controls.get_values()
        self.controls.set_busy(True)
        self.status_var.set("Computing route...")
        self.update_idletasks()

        try:
            route_payload = compute_gui_routes(
                **request_values,
                locations_csv=self.data_sources["locations_csv"],
                connectivity_csv=self.data_sources["connectivity_csv"],
            )
        except Exception as exc:
            self.results_panel.set_text(format_error_message(exc))
            self.status_var.set("Route computation failed.")
        else:
            self.results_panel.set_text(format_route_results(route_payload))
            route_count = len(route_payload["route_results"])
            self.status_var.set(f"Computed {route_count} route(s) successfully.")
        finally:
            self.controls.set_busy(False)


def main():
    app = RouteGuiApp()
    app.mainloop()


if __name__ == "__main__":
    main()
