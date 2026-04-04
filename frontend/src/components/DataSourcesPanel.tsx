import type { AppConfig } from "../types";

type DataSourcesPanelProps = {
  config: AppConfig | null;
};

export function DataSourcesPanel({ config }: DataSourcesPanelProps) {
  if (!config) {
    return (
      <section className="card">
        <div className="section-header">
          <p className="eyebrow">Backend Status</p>
          <h2>Loading data sources</h2>
        </div>
        <p className="muted">
          The app is checking which traffic dataset, topology files, and SCATS site
          records are available.
        </p>
      </section>
    );
  }

  return (
    <section className="card">
      <div className="section-header">
        <p className="eyebrow">Backend Status</p>
        <h2>Current data sources</h2>
      </div>
      <dl className="metadata-list">
        <div>
          <dt>Traffic data</dt>
          <dd>{config.data_sources.traffic_data_path}</dd>
        </div>
        <div>
          <dt>Locations topology</dt>
          <dd>{config.data_sources.locations_csv}</dd>
        </div>
        <div>
          <dt>Connectivity topology</dt>
          <dd>{config.data_sources.connectivity_csv}</dd>
        </div>
        <div>
          <dt>Available SCATS sites</dt>
          <dd>{config.sites.length}</dd>
        </div>
        <div>
          <dt>Default algorithm</dt>
          <dd>{config.defaults.algorithm}</dd>
        </div>
      </dl>
    </section>
  );
}

