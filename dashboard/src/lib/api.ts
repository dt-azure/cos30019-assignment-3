import type { AppConfig, RouteRequest, RouteResponse } from "../types";

const API_BASE_URL = (import.meta.env.VITE_API_BASE_URL ?? "/api").replace(/\/$/, "");

async function requestJson<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    headers: {
      "Content-Type": "application/json"
    },
    ...init
  });

  const payload = await response.json().catch(() => null);
  if (!response.ok) {
    const message =
      payload && typeof payload.detail === "string"
        ? payload.detail
        : "The server could not process the request.";
    throw new Error(message);
  }

    return payload as T;
}

export function fetchAppConfig(): Promise<AppConfig> {
  return requestJson<AppConfig>("/config", {
    method: "GET"
  });
}

export function computeRoutes(payload: RouteRequest): Promise<RouteResponse> {
  return requestJson<RouteResponse>("/routes/compute", {
    method: "POST",
    body: JSON.stringify(payload)
  });
}

