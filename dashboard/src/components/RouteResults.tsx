import type { RouteResponse } from "../types";
import "../styles/RouteResults.scss";

type RouteResultsProps = {
  loading: boolean;
  error: string | null;
  routeResponse: RouteResponse | null;
};

export function RouteResults({ loading, error, routeResponse }: RouteResultsProps) {
  return (
    <section className="card results-card">
      <div className="section-header">
        <h2>Results</h2>
      </div>

      {loading ? (
        <p className="status-banner status-loading">The backend is computing route options.</p>
      ) : null}

      {error ? <p className="status-banner status-error">{error}</p> : null}
      {!loading && routeResponse ? (
        <div className="results-stack">
          <div className="result-summary">
            <div className="results">
              <div className="result-item">
                <p>Model</p>
                <p>{routeResponse.model.toUpperCase()}</p>
              </div>

              <div className="result-item">
                <p>Origin</p>
                <p>
                  {routeResponse.origin}
                  {routeResponse.origin_description
                  ? ` · ${routeResponse.origin_description}`
                            : ""}
                </p>
              </div>
              
              <div className="result-item">
                <p>Destination</p>
                <p>
                  {routeResponse.destination}
                  {routeResponse.destination_description
                  ? ` · ${routeResponse.destination_description}`
                            : ""}
                </p>
              </div>

              <div className="result-item">
                <p>Routes found</p>
                <p>
                    {routeResponse.routes_found} / {routeResponse.routes_requested}
                </p>
              </div>
            </div>

          </div>
           <div className="routes-list">
            {routeResponse.routes.map((route, index) => (
              <article key={`${route.path.join("-")}-${index}`} className="route-card">
                <div className="route-card-header">
                  <h3>Route {index + 1}</h3>
                  <span className="route-badge">{route.algorithm}</span>
                </div>
                <p className="route-path">{route.path.join(" -> ")}</p>
                <dl className="route-metrics">
                  <div>
                    <dt>Goal site</dt>
                    <dd>{route.goal_site_id}</dd>
                  </div>
                  <div>
                    <dt>Travel time (sec)</dt>
                    <dd>{route.total_travel_time_sec.toFixed(2)}</dd>
                         </div>
                  <div>
                    <dt>Travel time (min)</dt>
                    <dd>{route.total_travel_time_min.toFixed(2)}</dd>
                  </div>
                </dl>
              </article>
            ))}
          </div>
        </div>
      ) : null}
    </section>
  );
}
