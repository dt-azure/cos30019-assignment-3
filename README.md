Boroondara Traffic Graph (graph.py)
The graph.py module defines the BoroondaraGraph class, which manages the spatial network of intersections and roads in the Boroondara area. It serves as the primary data structure for pathfinding algorithms (Dijkstra and A*).

Key Responsibilities
Node Management: Loads and stores geographic coordinates (Latitude/Longitude) for each SCATS site from the Traffic_Count_Locations_with_LONG_LAT.csv.

Topology Definition: Maintains the physical connections between intersections based on the Boroondara network layout.

Dynamic Weighting: Injects traffic flow predictions from the LSTM model into the graph, converting distances into Travel Time (seconds).

A Heuristic*: Provides a Haversine-based time estimate to ensure the A* algorithm remains admissible.

