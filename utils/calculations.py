import numpy as np

A = -1.4648375
B = 93.75
DELAY = 30  # seconds


def calculate_speed(flow):
    """
    Convert traffic flow (vehicles/hour) into speed (km/h)
    based on the assignment's quadratic flow-speed relationship.
    """
    if flow <= 351:
        return 60

    C = -flow
    discriminant = B**2 - 4 * A * C

    if discriminant < 0:
        raise ValueError(f"Invalid discriminant for flow={flow}")

    sqrt_d = np.sqrt(discriminant)

    speed1 = (-B + sqrt_d) / (2 * A)
    speed2 = (-B - sqrt_d) / (2 * A)

    valid_speeds = [s for s in (speed1, speed2) if s > 0]
    if not valid_speeds:
        raise ValueError(f"No valid positive speed for flow={flow}")

    # Use the higher positive speed under the simplified under-capacity assumption
    return max(valid_speeds)


def calculate_travel_time(starting_node, end_node, distance, predicted_flows):
    """
    Calculate travel time (seconds) for a graph edge.

    Parameters:
    - starting_node: origin SCATS site ID
    - end_node: destination SCATS site ID (kept for graph API consistency)
    - distance: edge distance in km
    - predicted_flows: dict {site_id: predicted flow per 15 minutes}

    Note:
    According to the assignment assumption, the link flow is estimated
    from the starting SCATS site.
    """
    if starting_node not in predicted_flows:
        raise KeyError(f"No predicted flow found for site {starting_node}")

    flow_per_hour = predicted_flows[starting_node] * 4
    speed = calculate_speed(flow_per_hour)

    travel_time_seconds = (distance / speed) * 3600
    return travel_time_seconds + DELAY