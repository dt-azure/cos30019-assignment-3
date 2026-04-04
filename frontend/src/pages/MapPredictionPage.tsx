import { useEffect, useState, useCallback, useRef } from "react";
import L from "leaflet";
import "leaflet/dist/leaflet.css";
import icon from "leaflet/dist/images/marker-icon.png";
import iconShadow from "leaflet/dist/images/marker-shadow.png";
import iconRetina from "leaflet/dist/images/marker-icon-2x.png";
import { computeRoutes, fetchAppConfig } from "../lib/api";
import type { AppConfig, RouteResponse, SiteOption } from "../types";
import { Navigation, Clock, Car, Search, Loader2 } from "lucide-react";

delete (L.Icon.Default.prototype as any)._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: iconRetina,
  iconUrl: icon,
  shadowUrl: iconShadow,
});

const VALID_SITES = [2000, 2200, 2820, 2825, 3001, 3002, 3120, 3122, 3126, 3127, 3180, 3682, 3685, 3812, 4030, 4032, 4035, 4040, 4051, 4057, 4063, 4324];
const ROUTE_COLORS = ["#2563eb", "#dc2626", "#16a34a", "#d97706", "#7c3aed"];

type EdgeDetail = {
  from: number;
  to: number;
  distance: number;
  speed: number;
  travelTime: number;
  trafficLevel: "low" | "medium" | "high";
};

type RouteDetail = {
  path: number[];
  goal_site_id: number;
  total_travel_time_sec: number;
  total_travel_time_min: number;
  algorithm: string;
  edges: EdgeDetail[];
  estimatedArrival: string;
};

export function MapPredictionPage() {
  const mapRef = useRef<L.Map | null>(null);
  const mapContainerRef = useRef<HTMLDivElement>(null);
  const layersRef = useRef<L.Layer[]>([]);

  const [config, setConfig] = useState<AppConfig | null>(null);
  const [origin, setOrigin] = useState("2000");
  const [destination, setDestination] = useState("3002");
  const [model, setModel] = useState("lightgbm");
  const [topK, setTopK] = useState(5);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [routeResponse, setRouteResponse] = useState<RouteResponse | null>(null);
  const [selectedRoute, setSelectedRoute] = useState<number>(0);
  const [routeDetails, setRouteDetails] = useState<RouteDetail[]>([]);

  useEffect(() => {
    fetchAppConfig().then(setConfig).catch(() => {});
  }, []);

  useEffect(() => {
    if (!mapContainerRef.current || mapRef.current) return;

    const map = L.map(mapContainerRef.current, {
      zoomControl: true,
      attributionControl: true,
    }).setView([-37.82, 145.03], 12);

    L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
      attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
      maxZoom: 19,
    }).addTo(map);

    mapRef.current = map;

    return () => {
      map.remove();
      mapRef.current = null;
    };
  }, []);

  const clearMapLayers = useCallback(() => {
    if (!mapRef.current) return;
    layersRef.current.forEach((layer) => mapRef.current!.removeLayer(layer));
    layersRef.current = [];
  }, []);

  const fetchRoadPath = async (latlngs: [number, number][]) => {
    const osrmCoords = latlngs.map(ll => `${ll[1]},${ll[0]}`).join(";");
    const url = `https://router.project-osrm.org/route/v1/driving/${osrmCoords}?overview=full&geometries=geojson`;
    
    try {
      const response = await fetch(url);
      const data = await response.json();
      // GeoJSON returns [lng, lat], Leaflet needs [lat, lng]
      return data.routes[0].geometry.coordinates.map((c: any) => [c[1], c[0]]);
    } catch (err) {
      console.error("OSRM Routing failed, falling back to straight lines", err);
      return latlngs; // Fallback to straight lines if API fails
    }
  };

  const drawRoutesOnMap = useCallback(async (response: RouteResponse, selectedIdx: number) => {
    if (!mapRef.current) return;
    clearMapLayers();

    const siteMap = new Map<number, SiteOption>();
    for (const site of response.sites) {
      siteMap.set(site.site_id, site);
    }

    const allBounds: L.LatLngExpression[] = [];


    for (let idx = 0; idx < response.routes.length; idx++) {
      const route = response.routes[idx];
      const isSelected = idx === selectedIdx;
      const color = ROUTE_COLORS[idx % ROUTE_COLORS.length];
      
      const siteCoords: [number, number][] = [];
      for (const siteId of route.path) {
        const site = siteMap.get(siteId);
        if (site?.latitude != null && site?.longitude != null) {
          siteCoords.push([site.latitude, site.longitude]);
          allBounds.push([site.latitude, site.longitude]);
        }
      }

      if (siteCoords.length >= 2) {
        const roadCoords = await fetchRoadPath(siteCoords);

        const polyline = L.polyline(roadCoords, {
          color,
          weight: isSelected ? 6 : 3,
          opacity: isSelected ? 1 : 0.5,
          dashArray: isSelected ? undefined : "8 6",
        }).addTo(mapRef.current!);
        
        layersRef.current.push(polyline);
        
        const originSite = siteMap.get(route.path[0]);
        if (originSite && originSite.latitude != null && originSite.longitude != null) {
          const originMarker = L.marker([originSite.latitude, originSite.longitude], {
            icon: L.divIcon({
              className: "custom-marker",
              html: `<div style="background:#16a34a;color:white;border-radius:50%;width:32px;height:32px;display:flex;align-items:center;justify-content:center;font-weight:bold;font-size:12px;border:2px solid white;box-shadow:0 2px 6px rgba(0,0,0,0.3)">A</div>`,
              iconSize: [32, 32],
              iconAnchor: [16, 16],
            }),
          }).bindPopup(`<b>Origin: ${originSite.site_id}</b><br>${originSite.description ?? ""}`);
          originMarker.addTo(mapRef.current!);
          layersRef.current.push(originMarker);
        }

        const destSite = siteMap.get(route.path[route.path.length - 1]);
        if (destSite && destSite.latitude != null && destSite.longitude != null) {
          const destMarker = L.marker([destSite.latitude, destSite.longitude], {
            icon: L.divIcon({
              className: "custom-marker",
              html: `<div style="background:#dc2626;color:white;border-radius:50%;width:32px;height:32px;display:flex;align-items:center;justify-content:center;font-weight:bold;font-size:12px;border:2px solid white;box-shadow:0 2px 6px rgba(0,0,0,0.3)">B</div>`,
              iconSize: [32, 32],
              iconAnchor: [16, 16],
            }),
          }).bindPopup(`<b>Destination: ${destSite.site_id}</b><br>${destSite.description ?? ""}`);
          destMarker.addTo(mapRef.current!);
          layersRef.current.push(destMarker);
        }
      }
    }

    if (allBounds.length > 0) {
      mapRef.current.fitBounds(allBounds, { padding: [50, 50] });
    }
  }, [clearMapLayers]);

  const computeEdgeDetails = useCallback((response: RouteResponse): RouteDetail[] => {
    const siteMap = new Map<number, SiteOption>();
    for (const site of response.sites) {
      siteMap.set(site.site_id, site);
    }

    return response.routes.map((route) => {
      const edges: EdgeDetail[] = [];

      for (let i = 0; i < route.path.length - 1; i++) {
        const fromSite = siteMap.get(route.path[i]);
        const toSite = siteMap.get(route.path[i + 1]);
        if (!fromSite || !toSite || fromSite.latitude == null || toSite.latitude == null) continue;

        const dist = L.latLng(fromSite.latitude, fromSite.longitude).distanceTo(
          L.latLng(toSite.latitude, toSite.longitude)
        ) / 1000;

        const edgeTime = route.total_travel_time_sec / (route.path.length - 1);
        const speedKmh = dist > 0 ? (dist / edgeTime) * 3600 : 60;
        const flowPerHour = Math.max(0, (60 - speedKmh) * 100);
        const trafficLevel: "low" | "medium" | "high" =
          flowPerHour <= 351 ? "low" : flowPerHour <= 1000 ? "medium" : "high";

        edges.push({
          from: route.path[i],
          to: route.path[i + 1],
          distance: dist,
          speed: speedKmh,
          travelTime: edgeTime,
          trafficLevel,
        });
      }

      const now = new Date();
      const eta = new Date(now.getTime() + route.total_travel_time_sec * 1000);
      const estimatedArrival = eta.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });

      return {
        ...route,
        edges,
        estimatedArrival,
      };
    });
  }, []);

  const handleSubmit = async () => {
    const numOrigin = Number(origin);
    const numDest = Number(destination);
    if (Number.isNaN(numOrigin) || Number.isNaN(numDest)) {
      setError("Origin and destination must be valid numbers.");
      return;
    }

    setLoading(true);
    setError(null);
    setSelectedRoute(0);

    try {
      const response = await computeRoutes({
        origin: numOrigin,
        destination: numDest,
        model,
        top_k: topK,
      });
      setRouteResponse(response);
      const details = computeEdgeDetails(response);
      setRouteDetails(details);
      drawRoutesOnMap(response, 0);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to compute routes.");
    } finally {
      setLoading(false);
    }
  };

  const handleSelectRoute = (idx: number) => {
    setSelectedRoute(idx);
    if (routeResponse) {
      drawRoutesOnMap(routeResponse, idx);
    }
  };

  const selectedDetail = routeDetails[selectedRoute];

  return (
    <div className="page page-map">
      <div className="map-layout">
        <div className="map-sidebar">
          <div className="map-search-card">
            <h2>
              <Navigation size={20} />
              Route Planner
            </h2>
            <div className="map-form">
              <label>
                <span>Origin</span>
                <select value={origin} onChange={(e) => setOrigin(e.target.value)}>
                  <option value="">Select origin site</option>
                  {VALID_SITES.map((s) => (
                    <option key={s} value={s}>{s}</option>
                  ))}
                </select>
              </label>
              <label>
                <span>Destination</span>
                <select value={destination} onChange={(e) => setDestination(e.target.value)}>
                  <option value="">Select destination site</option>
                  {VALID_SITES.map((s) => (
                    <option key={s} value={s}>{s}</option>
                  ))}
                </select>
              </label>
              <div className="map-form-row">
                <label>
                  <span>Model</span>
                  <select value={model} onChange={(e) => setModel(e.target.value)}>
                    {config?.available_models.map((m) => (
                      <option key={m} value={m}>{m}</option>
                    ))}
                  </select>
                </label>
                <label>
                  <span>Top-K</span>
                  <select value={topK} onChange={(e) => setTopK(Number(e.target.value))}>
                    {[1, 2, 3, 4, 5].map((k) => (
                      <option key={k} value={k}>{k}</option>
                    ))}
                  </select>
                </label>
              </div>
              <button className="map-search-btn" onClick={handleSubmit} disabled={loading}>
                {loading ? <Loader2 size={18} className="spin" /> : <Search size={18} />}
                {loading ? "Computing..." : "Find Routes"}
              </button>
              <p className="map-sites-hint">
                Available SCATS sites: {VALID_SITES.join(", ")}
              </p>
            </div>
          </div>

          {error && <div className="map-error">{error}</div>}

          {routeResponse && (
            <div className="map-routes-list">
              <h3>{routeResponse.routes_found} Routes Found</h3>
              {routeResponse.routes.map((route, idx) => (
                <div
                  key={idx}
                  className={`route-option ${idx === selectedRoute ? "selected" : ""}`}
                  onClick={() => handleSelectRoute(idx)}
                >
                  <div className="route-option-header">
                    <div className="route-option-color" style={{ backgroundColor: ROUTE_COLORS[idx % ROUTE_COLORS.length] }} />
                    <div className="route-option-info">
                      <span className="route-option-title">Route {idx + 1}</span>
                      <span className="route-option-path">{route.path.join(" → ")}</span>
                    </div>
                    <div className="route-option-time">
                      <Clock size={14} />
                      {route.total_travel_time_min.toFixed(1)} min
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}

          {selectedDetail && (
            <div className="map-route-detail">
              <div className="detail-summary">
                <div className="detail-stat">
                  <Car size={18} />
                  <div>
                    <span className="detail-stat-value">{selectedDetail.total_travel_time_min.toFixed(1)}</span>
                    <span className="detail-stat-label">minutes</span>
                  </div>
                </div>
                <div className="detail-stat">
                  <Clock size={18} />
                  <div>
                    <span className="detail-stat-value">{selectedDetail.estimatedArrival}</span>
                    <span className="detail-stat-label">ETA</span>
                  </div>
                </div>
              </div>

              <h4>Turn-by-Turn Directions</h4>
              <div className="edge-list">
                {selectedDetail.edges.map((edge, i) => (
                  <div key={i} className="edge-item">
                    <div className="edge-marker" />
                    <div className="edge-info">
                      <div className="edge-route">
                        <strong>{edge.from}</strong> → <strong>{edge.to}</strong>
                      </div>
                      <div className="edge-meta">
                        <span className={`traffic-badge traffic-${edge.trafficLevel}`}>
                          {edge.trafficLevel === "low" ? "Low Traffic" : edge.trafficLevel === "medium" ? "Medium Traffic" : "Heavy Traffic"}
                        </span>
                        <span>{edge.distance.toFixed(2)} km</span>
                        <span>{edge.speed.toFixed(0)} km/h</span>
                        <span>{(edge.travelTime / 60).toFixed(1)} min</span>
                      </div>
                    </div>
                  </div>
                ))}
                <div className="edge-marker edge-marker-dest" />
                <div className="edge-destination">
                  <strong>Destination: {selectedDetail.path[selectedDetail.path.length - 1]}</strong>
                </div>
              </div>
            </div>
          )}
        </div>

        <div className="map-container">
          <div ref={mapContainerRef} className="map-view" />
        </div>
      </div>
    </div>
  );
}
