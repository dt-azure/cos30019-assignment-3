import Papa from "papaparse";
import type { Site } from "../types";


export async function loadSites(): Promise<Site[]> {
  const response = await fetch("/data/boroondara_locations.csv");
  const text = await response.text();

  const parsed = Papa.parse(text, {
    header: true,
    skipEmptyLines: true,
  });

  return parsed.data.map((row: any) => {
    const lat = Number(String(row.LATITUDE).trim());
    const lng = Number(String(row.LONGITUDE).trim());

    if (Number.isNaN(lat) || Number.isNaN(lng)) {
      console.warn("Bad row:", row);
    }

    return {
      site_id: Number(String(row.NB_SCATS_SITE).trim()),
      lat,
      lng,
      description: row.SITE_DESC,
    };
  });
}

function buildRouteCoordinates(path: number[], siteMap: Map<number, Site>) {
  return path
    .map(id => siteMap.get(id))
    .filter((site): site is Site => !!site)
    .map(site => [site.lat, site.lng] as [number, number]);
}