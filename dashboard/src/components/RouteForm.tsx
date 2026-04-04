import type { AppConfig } from "../types";
import "../styles/RouteForm.scss";

import {
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Button,
  CircularProgress
} from "@mui/material";
import type { SelectChangeEvent } from "@mui/material";

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
        <h2>Parameters</h2>
      </div>

      <div className="form-grid">
        <label className="field">
          <p>Origin SCATS site ID</p>

          <FormControl fullWidth>
            <InputLabel id="origin-label">Origin SCATS site ID</InputLabel>
            <Select
              labelId="origin-label"
              value={origin}
              label="Origin SCATS site ID"
              onChange={(event: SelectChangeEvent) =>
                onOriginChange(event.target.value)
              }
            >
              <MenuItem value="">
                <em>Select origin</em>
              </MenuItem>

              {config?.sites.map((site) => (
                <MenuItem key={site.site_id} value={site.site_id.toString()}>
                  {site.site_id} {site.description ? `- ${site.description}` : ""}
                </MenuItem>
              ))}
            </Select>
          </FormControl>

          <small>{originDescription ? "" : "Enter a valid origin site ID."}</small>
        </label>
        <label className="field">
          <p>Destination SCATS site ID</p>

          <FormControl fullWidth>
            <InputLabel id="origin-label">Origin SCATS site ID</InputLabel>
            <Select
              labelId="origin-label"
              value={destination}
              label="Origin SCATS site ID"
              onChange={(event: SelectChangeEvent) =>
                onDestinationChange(event.target.value)
              }
            >
              <MenuItem value="">
                <em>Select origin</em>
              </MenuItem>

              {config?.sites.map((site) => (
                <MenuItem key={site.site_id} value={site.site_id.toString()}>
                  {site.site_id} {site.description ? `- ${site.description}` : ""}
                </MenuItem>
              ))}
            </Select>
          </FormControl>
          
          <small>{destinationDescription ? "" : "Enter a valid destination site ID."}</small>
        </label>

        <label className="field">
          <p>Prediction model</p>

          <FormControl fullWidth>
            <InputLabel id="model-label">Origin SCATS site ID</InputLabel>
            <Select
              labelId="model-label"
              value={model}
              label="Prediction model"
              onChange={(event: SelectChangeEvent) =>
                onModelChange(event.target.value)
              }
            >
              <MenuItem value="">
                <em>Select model</em>
              </MenuItem>

              {config?.available_models.map((modelOption) => (
                <MenuItem key={modelOption} value={modelOption}>
                  {modelOption.toUpperCase()}
                </MenuItem>
              ))}
            </Select>
          </FormControl>

          <small>LightGBM stays the default model for the live route pipeline.</small>
        </label>

        <label className="field">
          <p>Top-k routes</p>
          
          <FormControl fullWidth>
            <InputLabel id="top-k-label">Top-k routes</InputLabel>
            <Select
              labelId="top-k-label"
              value={topK.toString()}
              label="Top-k routes"
              onChange={(event: SelectChangeEvent) =>
                onTopKChange(+event.target.value)
              }
            >
              <MenuItem value="">
                <em>Select Top-k routes</em>
              </MenuItem>

              {Array.from({ length: maxTopK }, (_, i) => i + 1).map((value) => (
                <MenuItem key={value} value={value}>
                  {value}
                </MenuItem>
              ))}
            </Select>
          </FormControl>

          <small>Request between 1 and {maxTopK} ranked route options.</small>
        </label>
      </div>

      <Button
        variant="contained"
        disabled={loading || !config}
        onClick={onSubmit}
        sx={{
          backgroundColor: "#005FB8",
          width: "100%",
          "&:hover": {
            backgroundColor: "#0F172A"
          }
        }}
      >
        {loading ? (
          <>
            <CircularProgress size={20} sx={{ mr: 1 }} />
            Computing routes...
          </>
        ) : (
          "Find shortest route(s)"
        )}
      </Button>
    </section>
  );
}