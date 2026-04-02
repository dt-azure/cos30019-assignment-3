import tkinter as tk
from tkinter import ttk
from tkinter.scrolledtext import ScrolledText


class RouteControls(ttk.LabelFrame):
    def __init__(self, parent, models, on_submit):
        super().__init__(parent, text="Route Request", padding=12)
        self._on_submit = on_submit

        self.origin_var = tk.StringVar()
        self.destination_var = tk.StringVar()
        self.model_var = tk.StringVar(value=models[0])
        self.top_k_var = tk.StringVar(value="1")

        self.columnconfigure(1, weight=1)
        self.columnconfigure(3, weight=1)

        ttk.Label(self, text="Origin SCATS Site ID").grid(
            row=0, column=0, sticky="w", padx=(0, 8), pady=(0, 8)
        )
        self.origin_entry = ttk.Entry(self, textvariable=self.origin_var, width=18)
        self.origin_entry.grid(row=0, column=1, sticky="ew", pady=(0, 8))

        ttk.Label(self, text="Destination SCATS Site ID").grid(
            row=0, column=2, sticky="w", padx=(16, 8), pady=(0, 8)
        )
        self.destination_entry = ttk.Entry(self, textvariable=self.destination_var, width=18)
        self.destination_entry.grid(row=0, column=3, sticky="ew", pady=(0, 8))

        ttk.Label(self, text="Model").grid(
            row=1, column=0, sticky="w", padx=(0, 8), pady=(0, 8)
        )
        self.model_combo = ttk.Combobox(
            self,
            textvariable=self.model_var,
            values=models,
            state="readonly",
            width=16,
        )
        self.model_combo.grid(row=1, column=1, sticky="w", pady=(0, 8))

        ttk.Label(self, text="Top-k Routes").grid(
            row=1, column=2, sticky="w", padx=(16, 8), pady=(0, 8)
        )
        self.top_k_combo = ttk.Combobox(
            self,
            textvariable=self.top_k_var,
            values=[str(value) for value in range(1, 6)],
            state="readonly",
            width=16,
        )
        self.top_k_combo.grid(row=1, column=3, sticky="w", pady=(0, 8))

        self.compute_button = ttk.Button(self, text="Compute Routes", command=self._on_submit)
        self.compute_button.grid(row=2, column=0, columnspan=4, sticky="ew", pady=(8, 0))

        self.origin_entry.bind("<Return>", lambda _event: self._on_submit())
        self.destination_entry.bind("<Return>", lambda _event: self._on_submit())

    def get_values(self):
        return {
            "origin_value": self.origin_var.get(),
            "destination_value": self.destination_var.get(),
            "model_name": self.model_var.get(),
            "top_k": self.top_k_var.get(),
        }

    def set_busy(self, is_busy):
        state = "disabled" if is_busy else "normal"
        self.compute_button.configure(state=state)
        self.origin_entry.configure(state=state)
        self.destination_entry.configure(state=state)
        self.model_combo.configure(state="disabled" if is_busy else "readonly")
        self.top_k_combo.configure(state="disabled" if is_busy else "readonly")

    def focus_origin(self):
        self.origin_entry.focus_set()


class DataSourcesPanel(ttk.LabelFrame):
    def __init__(self, parent, formatted_sources):
        super().__init__(parent, text="Current Data Sources", padding=12)
        self.columnconfigure(1, weight=1)

        for row_index, (label, value) in enumerate(formatted_sources.items()):
            ttk.Label(self, text=f"{label}:").grid(
                row=row_index,
                column=0,
                sticky="nw",
                padx=(0, 8),
                pady=(0, 4),
            )
            ttk.Label(self, text=value).grid(row=row_index, column=1, sticky="nw", pady=(0, 4))


class RouteResultsPanel(ttk.LabelFrame):
    def __init__(self, parent):
        super().__init__(parent, text="Route Results", padding=12)
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        self.text = ScrolledText(self, wrap="word", height=22)
        self.text.grid(row=0, column=0, sticky="nsew")
        self.text.configure(state="disabled")

    def set_text(self, value):
        self.text.configure(state="normal")
        self.text.delete("1.0", tk.END)
        self.text.insert(tk.END, value)
        self.text.configure(state="disabled")

