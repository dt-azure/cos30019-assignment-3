import L from "leaflet";
import "leaflet/dist/leaflet.css";


delete (L.Icon.Default.prototype as any)._getIconUrl;
L.Icon.Default.mergeOptions({
    iconUrl: "https://unpkg.com/leaflet/dist/images/marker-icon.png",
    iconRetinaUrl: "https://unpkg.com/leaflet/dist/images/marker-icon-2x.png",
    shadowUrl: "https://unpkg.com/leaflet/dist/images/marker-shadow.png",
});

const originIcon = new L.Icon({
  iconUrl: "https://maps.google.com/mapfiles/ms/icons/green-dot.png",
  iconSize: [32, 32],
  iconAnchor: [16, 32],
});

const destinationIcon = new L.Icon({
  iconUrl: "https://maps.google.com/mapfiles/ms/icons/red-dot.png",
  iconSize: [32, 32],
  iconAnchor: [16, 32],
});

const nodeIcon = new L.Icon({
  iconUrl: "https://maps.google.com/mapfiles/ms/icons/blue-dot.png",
  iconSize: [20, 20],
  iconAnchor: [10, 20],
});

import "../styles/MapPage.scss";
import type { Site, SiteOption, Route } from "../types";
import { MapContainer, TileLayer, Marker, Popup } from "react-leaflet";
import { CircularProgress, Box } from "@mui/material";
import { Polyline, useMap } from "react-leaflet";
import { useEffect } from "react";


const route_colors = ["blue", "red", "green", "purple", "orange"];

function FocusOnOrigin({ position }: { position: [number, number] | null }) {
  const map = useMap();

  useEffect(() => {
    if (position) {
      map.setView(position, 25);
    }
  }, [position]);

  return null;
}

export function MapView({
    sites,
    routes,
    }: {
    sites: Site[];
    routes: Route[];
    }) {
    const siteMap = new Map(sites.map(s => [s.site_id, s]));
        
    function toCoordinates(path: number[]) {
        return path.map(id => {
            const site = siteMap.get(id);

            if (!site) {
            console.warn("Missing site:", id);
            }

            return site;
        })
        .filter((s): s is Site => !!s)
        .map(s => [s.lat, s.lng] as [number, number]);
    }

    const firstRoute = routes[0];
    const firstCoords = firstRoute ? toCoordinates(firstRoute.path) : [];
    const originId = firstRoute ? firstRoute.path[0] : null;

    const originCoords = firstCoords.length > 0 ? firstCoords[0] : null;
    const destinationCoords = firstCoords.length > 0 ? firstCoords.at(-1)! : null;
    const destinationId = firstRoute ? firstRoute.path[firstRoute.path.length - 1] : null;

    const allNodeIds = Array.from(new Set(routes.flatMap(route => route.path)));
    const allCoords = allNodeIds.map(id => {
        const site = siteMap.get(id);
        return site ? { id, coords: [site.lat, site.lng] as [number, number] } : null;
    }).filter((x): x is { id: number; coords: [number, number] } => !!x);

    return (
        <MapContainer
            center={[-37.88, 145.16]}
            zoom={12}
            style={{ height: "500px", width: "100%" }}
        >
        <TileLayer url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png" />

        <FocusOnOrigin position={originCoords} />

        {originCoords && (
            <Marker position={originCoords} icon={originIcon}>
                <Popup>
                    <strong>Origin - SCATS {originId}</strong>
                </Popup>
            </Marker>
        )}

        {destinationCoords && (
            <Marker position={destinationCoords} icon={destinationIcon}>
                <Popup>
                    <strong>Destination - SCATS {destinationId}</strong>
                </Popup>
            </Marker>
        )}

        {allCoords.map(({ id, coords }) => {
            if (id == originId || id == destinationId) {
                return null;
            }

            return (
                <Marker key={id} position={coords} icon={nodeIcon}>
                    <Popup>
                    <strong>SCATS {id}</strong>
                    </Popup>
                </Marker>
            )
        })}

        {routes.map((route, index) => {
            const coords = toCoordinates(route.path);
            if (coords.length < 2) return null;

            return (
            <Polyline
                key={index}
                positions={coords}
                pathOptions={{
                color: route_colors[index % route_colors.length],
                weight: index === 0 ? 6 : 4,
                opacity: index === 0 ? 1 : 0.6,
                }}
            />
            );
        })}
        </MapContainer>
    );
}