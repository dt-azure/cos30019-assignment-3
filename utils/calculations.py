import numpy as np

# flow = -1.4648375*(speed)**2 + 93.75*(speed)
# => -1.4648375 * speed² + 93.75 * speed - flow = 0
A = -1.4648375
B = 93.75

# Intersection delay
DELAY = 30

def calculate_speed(flow):
    # If flow <= 351 then speed is capped
    if flow <= 351:
        return 60

    C = -flow
    discriminant = B ** 2 - 4 * A * C
    
    if discriminant < 0:
        return 0    # safety fallback
    
    sqrt_d = np.sqrt(discriminant)

    speed1 = (-B + sqrt_d) / (2 * A)
    speed2 = (-B - sqrt_d) / (2 * A)

    if speed1 < 0 and speed2 < 0:
        raise Exception("Speed is below zero.")

    return max(speed1, speed2)

def calculate_travel_time(starting_node, end_node, distance, predicted_flow):
    """
    predicted_flow: dict
    """

    # Every 15 minutes -> every hour
    flow = predicted_flow[starting_node] * 4
    speed = calculate_speed(flow)
    travel_time_seconds = (distance / speed) * 3600

    return travel_time_seconds + DELAY


