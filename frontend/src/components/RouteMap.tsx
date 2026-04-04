import { useEffect, useState } from "react";
import L from "leaflet";
import "leaflet/dist/leaflet.css";

import icon from "leaflet/dist/images/marker-icon.png";
import iconShadow from "leaflet/dist/images/marker-shadow.png";
import iconRetina from "leaflet/dist/images/marker-icon-2x.png";

// Fix Leaflet default icon issue with Vite
delete (L.Icon.Default.prototype as any)._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: iconRetina,
  iconUrl: icon,
  shadowUrl: iconShadow,
});

type SiteOption = {
  site_id: number;
  description: string | null;
  latitude: number | null;
  longitude: number | null;
};

type RouteResult = {
  path: number[];
  goal_site_id: number;
  total_travel_time_sec: number;
  total_travel_time_min: number;
  algorithm: string;
};

type RouteMapProps = {
  sites: SiteOption[];
  routes: RouteResult[];
  origin: number;
  destination: number;
};

const ROUTE_COLORS = ["#2563eb", "#dc2626", "#16a34a", "#d97706", "#7c3aed"];

export function RouteMap({ sites, routes, origin, destination }: RouteMapProps) {
  const [mapReady, setMapReady] = useState(false);

  useEffect(() => {
    if (!mapReady) return;

    const mapEl = document.getElementById("route-map");
    if (!mapEl) return;

    const map = L.map(mapEl);

    L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
      attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
      maxZoom: 19,
    }).addTo(map);

    const siteMap = new Map<number, SiteOption>();
    for (const site of sites) {
      siteMap.set(site.site_id, site);
    }

    const bounds: L.LatLngExpression[] = [];

    // Draw all sites as markers
    for (const site of sites) {
      if (site.latitude != null && site.longitude != null) {
        const latlng: L.LatLngExpression = [site.latitude, site.longitude];
        bounds.push(latlng);

        const isOrigin = site.site_id === origin;
        const isDestination = site.site_id === destination;

        let markerIcon: L.Icon;
        if (isOrigin) {
          markerIcon = new L.Icon({
            iconUrl: "https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/marker-icon-green.png",
            shadowUrl: iconShadow,
            iconRetinaUrl: "https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/marker-icon-2x-green.png",
            iconSize: [25, 41],
            iconAnchor: [12, 41],
            popupAnchor: [1, -34],
            shadowSize: [41, 41],
          });
        } else if (isDestination) {
          markerIcon = new L.Icon({
            iconUrl: "https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/marker-icon-red.png",
            shadowUrl: iconShadow,
            iconRetinaUrl: "https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/marker-icon-2x-red.png",
            iconSize: [25, 41],
            iconAnchor: [12, 41],
            popupAnchor: [1, -34],
            shadowSize: [41, 41],
          });
        } else {
          markerIcon = new L.Icon.Default();
        }

        L.marker(latlng, { icon: markerIcon })
          .bindPopup(`<b>${site.site_id}</b><br>${site.description ?? ""}`)
          .addTo(map);
      }
    }

    // Draw route lines
    routes.forEach((route, index) => {
      const color = ROUTE_COLORS[index % ROUTE_COLORS.length];
      const latlngs: L.LatLngExpression[] = [];

      for (const siteId of route.path) {
        const site = siteMap.get(siteId);
        if (site && site.latitude != null && site.longitude != null) {
          latlngs.push([site.latitude, site.longitude]);
        }
      }

      if (latlngs.length >= 2) {
        L.Routing.control(latlngs, {
          color,
          weight: 4,
          opacity: 0.8,
        })
          .bindTooltip(
            `Route ${index + 1}: ${route.total_travel_time_min.toFixed(1)} min`,
            { sticky: true }
          )
          .addTo(map);
      }
    });

    if (bounds.length > 0) {
      map.fitBounds(bounds, { padding: [50, 50] });
    }

    return () => {
      map.remove();
    };
  }, [sites, routes, origin, destination, mapReady]);


  return (
    <div>
      <button
        type="button"
        className="map-toggle-button"
        onClick={() => setMapReady(!mapReady)}
      >
        {mapReady ? "Hide Map" : "Show Map"}
      </button>
      {mapReady && (
        <div
          id="route-map"
          style={{
            height: "500px",
            width: "100%",
            borderRadius: "8px",
            marginTop: "12px",
          }}
        />
      )}
    </div>
  );
}
