export type SiteOption = {
  site_id: number;
  description: string | null;
};

export type DataSources = {
  traffic_data_path: string;
  locations_csv: string;
  connectivity_csv: string;
};

export type AppConfig = {
  status: string;
  defaults: {
    model: string;
    top_k: number;
    top_k_max: number;
    algorithm: string;
  };
  available_models: string[];
  data_sources: DataSources;
  sites: SiteOption[];
};


export type RouteRequest = {
  origin: number;
  destination: number;
  model: string;
  top_k: number;
};

export type RouteResult = {
  path: number[];
  goal_site_id: number;
  total_travel_time_sec: number;
  total_travel_time_min: number;
  algorithm: string;
};


export type RouteResponse = {
  model: string;
  origin: number;
  destination: number;
  origin_description: string | null;
  destination_description: string | null;
  routes_requested: number;
  routes_found: number;
  routes: RouteResult[];
  data_sources: DataSources;
};