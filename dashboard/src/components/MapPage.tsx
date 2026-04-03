import L from "leaflet";
import "leaflet/dist/leaflet.css";


delete (L.Icon.Default.prototype as any)._getIconUrl;
L.Icon.Default.mergeOptions({
    iconUrl: "https://unpkg.com/leaflet/dist/images/marker-icon.png",
    iconRetinaUrl: "https://unpkg.com/leaflet/dist/images/marker-icon-2x.png",
    shadowUrl: "https://unpkg.com/leaflet/dist/images/marker-shadow.png",
});

import "../styles/MapPage.scss";
import { useEffect, useState } from "react";
import { loadSites } from "../lib/helper";
import type { Site } from "../lib/helper";
import { MapContainer, TileLayer, Marker, Popup } from "react-leaflet";
import { CircularProgress, Box } from "@mui/material";

export default function MapPage() {
    const [sites, setSites] = useState<Site[]>([]);

    useEffect(() => {
        loadSites().then(setSites);
    }, []);

    return <MapView sites={sites} />;
}

export function MapView({ sites }: { sites: Site[] }) {
    if (!sites.length) {
        return (
        <Box
            sx={{
            height: "500px",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            }}
        >
            <CircularProgress size={40} />
        </Box>
        );
    }

    return (
        <MapContainer
            center={[-35.8189368469882, 143.47004699625649]}
            zoom={12}
            style={{ height: "500px", width: "100%" }}
        >
        <TileLayer url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png" />

        {sites
            .filter(site => !Number.isNaN(site.lat) && !Number.isNaN(site.lng))
            .map((site) => (
                <Marker key={site.site_id} position={[site.lat, site.lng]}>
                <Popup>
                    <strong>{site.site_id}</strong>
                    <br />
                    {site.description}
                </Popup>
                </Marker>
            ))}
        </MapContainer>
    );
}