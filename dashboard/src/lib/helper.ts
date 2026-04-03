import Papa from "papaparse";

export type Site = {
  site_id: number;
  lat: number;
  lng: number;
  description: string;
};

export async function loadSites(): Promise<Site[]> {
  const response = await fetch("/data/sites.csv");
  const text = await response.text();

  const parsed = Papa.parse(text, {
    header: true,
    skipEmptyLines: true,
  });

  return parsed.data.map((row: any) => ({
    site_id: Number(row.NB_SCATS_SITE),
    lat: Number(row.LATITUDE),
    lng: Number(row.LONGITUDE),
    description: row.SITE_DESC,
  }));
}