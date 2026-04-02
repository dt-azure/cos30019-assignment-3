def format_site_description(site_id, site_descriptions):
    description = site_descriptions.get(site_id, "").strip()
    if not description:
        return "N/A"
    return description


def format_initial_message(data_sources):
    return "\n".join(
        [
            "Enter an origin SCATS site ID and destination SCATS site ID, then click Compute Routes.",
            "",
            f"Traffic data: {data_sources['traffic_data_path']}",
            f"Locations source: {data_sources['locations_csv']}",
            f"Connectivity source: {data_sources['connectivity_csv']}",
        ]
    )


def format_error_message(error):
    if isinstance(error, KeyError):
        message = error.args[0] if error.args else str(error)
        return f"Error: {message}"
    return f"Error: {error}"


def format_route_results(route_payload):
    site_descriptions = route_payload["site_descriptions"]
    origin_site_id = route_payload["origin_site_id"]
    destination_site_id = route_payload["destination_site_id"]
    route_results = route_payload["route_results"]

    lines = [
        f"Model: {route_payload['model_name']}",
        f"Origin: {origin_site_id}",
        f"Origin Description: {format_site_description(origin_site_id, site_descriptions)}",
        f"Destination: {destination_site_id}",
        f"Destination Description: {format_site_description(destination_site_id, site_descriptions)}",
        f"Routes Requested: {route_payload['top_k']}",
        f"Routes Found: {len(route_results)}",
    ]

    for index, route_result in enumerate(route_results, start=1):
        total_seconds = route_result["total_travel_time_sec"]
        total_minutes = total_seconds / 60
        path_text = " -> ".join(str(site_id) for site_id in route_result["path"])
        label = "Best Route" if len(route_results) == 1 else f"Route {index}"
        lines.extend(
            [
                "",
                f"{label}:",
                f"Path: {path_text}",
                f"Goal Site: {route_result['goal_site_id']}",
                f"Algorithm: {route_result['algorithm']}",
                f"Travel Time (seconds): {total_seconds:.2f}",
                f"Travel Time (minutes): {total_minutes:.2f}",
            ]
        )

    return "\n".join(lines)


def format_data_sources(data_sources):
    return {
        "Traffic Data": data_sources["traffic_data_path"],
        "Locations CSV": data_sources["locations_csv"],
        "Connectivity CSV": data_sources["connectivity_csv"],
    }
