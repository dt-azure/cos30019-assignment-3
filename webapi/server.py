from __future__ import annotations

import csv
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field
import osmnx as ox

from machine_learning.common.cli_route_service import (
    DEFAULT_CLI_ALGORITHM,
    DEFAULT_CLI_MODEL_NAME,
    compute_terminal_routes,
)
from machine_learning.common.config import (
    SCATS_DATA_PATH,
    SEQUENCE_MODEL_TYPES,
    TABULAR_MODEL_TYPES,
)
from machine_learning.common.topology_service import (
    DEFAULT_CONNECTIVITY_CSV,
    DEFAULT_LOCATIONS_CSV,
    get_default_topology_paths,
    validate_locations_csv,
)

API_PREFIX = "/api"
MAX_TOP_K = 5
SUPPORTED_MODELS = sorted(SEQUENCE_MODEL_TYPES | TABULAR_MODEL_TYPES)
FRONTEND_DIST = Path(__file__).resolve().parent.parent / "frontend" / "dist"


class SiteOption(BaseModel):
    site_id: int
    description: str | None = None
    latitude: float | None = None
    longitude: float | None = None


class DataSourcesResponse(BaseModel):
    traffic_data_path: str
    locations_csv: str
    connectivity_csv: str


class ConfigResponse(BaseModel):
    status: str
    defaults: dict[str, str | int]
    available_models: list[str]
    data_sources: DataSourcesResponse
    sites: list[SiteOption]


class RouteRequest(BaseModel):
    origin: int
    destination: int
    model: str = Field(default=DEFAULT_CLI_MODEL_NAME)
    top_k: int = Field(default=1, ge=1, le=MAX_TOP_K)


class RouteResultResponse(BaseModel):
    path: list[int]
    goal_site_id: int
    total_travel_time_sec: float
    total_travel_time_min: float
    algorithm: str


class RouteResponse(BaseModel):
    model: str
    origin: int
    destination: int
    origin_description: str | None = None
    destination_description: str | None = None
    routes_requested: int
    routes_found: int
    routes: list[RouteResultResponse]
    data_sources: DataSourcesResponse
    sites: list[SiteOption]


app = FastAPI(
    title="COS30019 Assignment 2B Route API",
    version="1.0.0",
    description="Thin API wrapper over the existing dynamic traffic routing backend.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:4173",
        "http://127.0.0.1:4173",
        "http://localhost:8000",
        "http://127.0.0.1:8000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

if FRONTEND_DIST.is_dir():
    app.mount("/", StaticFiles(directory=str(FRONTEND_DIST), html=True), name="frontend")


def _get_data_sources() -> DataSourcesResponse:
    default_topology_paths = get_default_topology_paths()
    return DataSourcesResponse(
        traffic_data_path=SCATS_DATA_PATH,
        locations_csv=default_topology_paths["locations_csv"],
        connectivity_csv=default_topology_paths["connectivity_csv"],
    )


def _extract_error_message(exc: Exception) -> str:
    if exc.args:
        return str(exc.args[0])
    return str(exc)


def _load_site_options(locations_csv: str = DEFAULT_LOCATIONS_CSV) -> list[SiteOption]:
    validated_locations_csv = validate_locations_csv(locations_csv)

    with Path(validated_locations_csv).open(newline="") as handle:
        reader = csv.DictReader(handle)
        return [
            SiteOption(
                site_id=int(row["NB_SCATS_SITE"]),
                description=row.get("SITE_DESC") or None,
                latitude=float(row["SNAPPED_LATITUDE"]) if row.get("SNAPPED_LATITUDE") else None,
                longitude=float(row["SNAPPED_LONGITUDE"]) if row.get("SNAPPED_LONGITUDE") else None,
            )
            for row in sorted(
                reader,
                key=lambda row: int(row["NB_SCATS_SITE"]),
            )
        ]


def _load_site_lookup(locations_csv: str = DEFAULT_LOCATIONS_CSV) -> dict[int, SiteOption]:
    return {
        site.site_id: site
        for site in _load_site_options(locations_csv=locations_csv)
    }


def _build_route_response(
    route_results: list[dict],
    origin: int,
    destination: int,
    model: str,
    routes_requested: int,
    sites: list[SiteOption] | None = None,
) -> RouteResponse:
    site_lookup = _load_site_lookup()
    data_sources = _get_data_sources()

    routes = [
        RouteResultResponse(
            path=[int(site_id) for site_id in route_result["path"]],
            goal_site_id=int(route_result["goal_site_id"]),
            total_travel_time_sec=float(route_result["total_travel_time_sec"]),
            total_travel_time_min=float(route_result["total_travel_time_sec"]) / 60,
            algorithm=str(route_result["algorithm"]),
        )
        for route_result in route_results
    ]

    return RouteResponse(
        model=model,
        origin=origin,
        destination=destination,
        origin_description=site_lookup.get(origin).description if origin in site_lookup else None,
        destination_description=(
            site_lookup.get(destination).description if destination in site_lookup else None
        ),
        routes_requested=routes_requested,
        routes_found=len(routes),
        routes=routes,
        data_sources=data_sources,
        sites=sites or [],
    )


@app.get(f"{API_PREFIX}/health")
def health_check() -> dict[str, str]:
    return {"status": "ok"}


@app.get(f"{API_PREFIX}/config", response_model=ConfigResponse)
def get_config() -> ConfigResponse:
    try:
        sites = _load_site_options()
    except (FileNotFoundError, ValueError) as exc:
        raise HTTPException(status_code=500, detail=_extract_error_message(exc)) from exc

    return ConfigResponse(
        status="ok",
        defaults={
            "model": DEFAULT_CLI_MODEL_NAME,
            "top_k": 1,
            "top_k_max": MAX_TOP_K,
            "algorithm": DEFAULT_CLI_ALGORITHM,
        },
        available_models=SUPPORTED_MODELS,
        data_sources=_get_data_sources(),
        sites=sites,
    )


@app.post(f"{API_PREFIX}/routes/compute", response_model=RouteResponse)
def compute_routes(request: RouteRequest) -> RouteResponse:
    if request.model not in SUPPORTED_MODELS:
        raise HTTPException(
            status_code=400,
            detail=(
                f"Unsupported model '{request.model}'. "
                f"Choose from: {SUPPORTED_MODELS}"
            ),
        )

    try:
        route_results, *_ = compute_terminal_routes(
            origin_site_id=request.origin,
            destination_site_id=request.destination,
            model_name=request.model,
            algorithm=DEFAULT_CLI_ALGORITHM,
            top_k=request.top_k,
            locations_csv=DEFAULT_LOCATIONS_CSV,
            connectivity_csv=DEFAULT_CONNECTIVITY_CSV,
        )
    except KeyError as exc:
        raise HTTPException(status_code=400, detail=_extract_error_message(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except FileNotFoundError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    response = _build_route_response(
        route_results=route_results,
        origin=request.origin,
        destination=request.destination,
        model=request.model,
        routes_requested=request.top_k,
        sites=_load_site_options(),
    )
    return response
