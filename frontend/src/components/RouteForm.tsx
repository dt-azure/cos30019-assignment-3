import type { AppConfig } from "../types";

type RouteFormProps = {
  config: AppConfig | null;
  origin: string;
  destination: string;
  model: string;
  topK: number;
  loading: boolean;
  originDescription: string | null;
  destinationDescription: string | null;
  onOriginChange: (value: string) => void;
  onDestinationChange: (value: string) => void;
  onModelChange: (value: string) => void;
  onTopKChange: (value: number) => void;
  onSubmit: () => void;
};

export function RouteForm({
  config,
  origin,
  destination,
  model,
  topK,
  loading,
  originDescription,
  destinationDescription,
  onOriginChange,
  onDestinationChange,
  onModelChange,
  onTopKChange,
  onSubmit
}: RouteFormProps) {
  const availableModels = config?.available_models ?? ["lightgbm"];
  const maxTopK = config?.defaults.top_k_max ?? 5;

  return (
    <section className="card">
      <div className="section-header">
        <p className="eyebrow">Route Request</p>
        <h2>Compute dynamic routes</h2>
      </div>

      <div className="form-grid">
        <label className="field">
          <span>Origin SCATS site ID</span>
          <input
            type="number"
            value={origin}
            onChange={(event) => onOriginChange(event.target.value)}
            placeholder="e.g. 2000"
          />
          <small>{originDescription ?? "Enter a valid origin site ID."}</small>
        </label>

        <label className="field">
          <span>Destination SCATS site ID</span>
          <input
            type="number"
            value={destination}
            onChange={(event) => onDestinationChange(event.target.value)}
            placeholder="e.g. 3002"
          />
          <small>{destinationDescription ?? "Enter a valid destination site ID."}</small>
        </label>

        <label className="field">
          <span>Prediction model</span>
          <select value={model} onChange={(event) => onModelChange(event.target.value)}>
            {availableModels.map((modelOption) => (
              <option key={modelOption} value={modelOption}>
                {modelOption}
              </option>
            ))}
          </select>
          <small>LightGBM stays the default model for the live route pipeline.</small>
        </label>

        <label className="field">
          <span>Top-k routes</span>
          <select value={topK} onChange={(event) => onTopKChange(Number(event.target.value))}>
            {Array.from({ length: maxTopK }, (_, index) => index + 1).map((value) => (
              <option key={value} value={value}>
                {value}
              </option>
            ))}
          </select>
          <small>Request between 1 and {maxTopK} ranked route options.</small>
        </label>
      </div>

      <button
        type="button"
        className="primary-button"
        disabled={loading || !config}
        onClick={onSubmit}
      >
        {loading ? "Computing routes..." : "Compute route"}
      </button>
    </section>
  );
}

