import { useEffect, useState } from "react";

import { DataSourcesPanel } from "./components/DataSourcesPanel";
import { RouteForm } from "./components/RouteForm";
import { RouteResults } from "./components/RouteResults";
import { computeRoutes, fetchAppConfig } from "./lib/api";
import type { AppConfig, RouteResponse, SiteOption } from "./types";

function getSiteDescription(sites: SiteOption[], rawValue: string): string | null {
  if (!rawValue.trim()) {
    return null;
  }

  const numericValue = Number(rawValue);
  if (Number.isNaN(numericValue)) {
    return null;
  }

  const site = sites.find((candidate) => candidate.site_id === numericValue);
  return site?.description ?? null;
}

export default function App() {
  const [config, setConfig] = useState<AppConfig | null>(null);
  const [configError, setConfigError] = useState<string | null>(null);
  const [loadingConfig, setLoadingConfig] = useState(true);

  const [origin, setOrigin] = useState("2000");
  const [destination, setDestination] = useState("3002");
  const [model, setModel] = useState("lightgbm");
  const [topK, setTopK] = useState(1);

  const [loadingRoutes, setLoadingRoutes] = useState(false);
  const [routeError, setRouteError] = useState<string | null>(null);
  const [routeResponse, setRouteResponse] = useState<RouteResponse | null>(null);

  useEffect(() => {
    let active = true;

    async function loadConfig() {
      try {
        const apiConfig = await fetchAppConfig();
        if (!active) {
          return;
        }
        setConfig(apiConfig);
        setModel(apiConfig.defaults.model);
        setTopK(apiConfig.defaults.top_k);
        setConfigError(null);
      } catch (error) {
        if (!active) {
          return;
        }
        setConfigError(
          error instanceof Error
            ? error.message
            : "The frontend could not load backend configuration."
        );
      } finally {
        if (active) {
          setLoadingConfig(false);
        }
      }
    }

    void loadConfig();

    return () => {
      active = false;
    };
  }, []);

  const sites = config?.sites ?? [];
  const originDescription = getSiteDescription(sites, origin);
  const destinationDescription = getSiteDescription(sites, destination);

  async function handleSubmit() {
        const numericOrigin = Number(origin);
    const numericDestination = Number(destination);

    if (Number.isNaN(numericOrigin) || Number.isNaN(numericDestination)) {
      setRouteError("Origin and destination must be valid numeric SCATS site IDs.");
      setRouteResponse(null);
      return;
    }

    setLoadingRoutes(true);
    setRouteError(null);

    try {
      const response = await computeRoutes({
        origin: numericOrigin,
        destination: numericDestination,
        model,
        top_k: topK
      });
          setRouteResponse(response);
    } catch (error) {
      setRouteResponse(null);
      setRouteError(
        error instanceof Error ? error.message : "The backend could not compute a route."
      );
    } finally {
      setLoadingRoutes(false);
    }
  }

  return (
    <div className="app-shell">
      <main className="page">
        <section className="hero">
          <p className="eyebrow">COS30019 Assignment 2B</p>
          <h1>Traffic-Based Route Guidance System</h1>
          <p className="hero-copy">
            This web client reuses the existing Python routing pipeline. It predicts
            current traffic flow, updates dynamic edge costs, and returns the best route
            or top-k route alternatives between SCATS sites.
          </p>
        </section>

        {configError ? (
          <section className="card">
            <div className="section-header">
              <p className="eyebrow">Connection Error</p>
              <h2>Backend unavailable</h2>
            </div>
            <p className="status-banner status-error">{configError}</p>
          </section>
          ) : null}

        <div className="dashboard-grid">
          <div className="left-column">
            <RouteForm
              config={config}
              origin={origin}
              destination={destination}
              model={model}
              topK={topK}
              loading={loadingRoutes || loadingConfig}
              originDescription={originDescription}
              destinationDescription={destinationDescription}
              onOriginChange={setOrigin}
                     onDestinationChange={setDestination}
              onModelChange={setModel}
              onTopKChange={setTopK}
              onSubmit={handleSubmit}
            />
            <DataSourcesPanel config={config} />
          </div>

          <RouteResults
            loading={loadingRoutes || loadingConfig}
            error={routeError}
            routeResponse={routeResponse}
          />
        </div>
      </main>
    </div>
  );
}