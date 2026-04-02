import pandas as pd
from math import radians, cos, sin, asin, sqrt

from utils.calculations import calculate_travel_time

class BoroondaraGraph:
    def __init__(self, locations_csv, connectivity_list):
        """
        locations_csv: Path to Traffic_Count_Locations_with_LONG_LAT.csv
        connectivity_list: List of tuples (origin, goal, distance_km) from setup.py logic
        """
        # 1. Load Node Metadata (Coords)
        df_coords = pd.read_csv(locations_csv)
        # Dictionary: {SiteID: {'lat': Lat, 'lon': Lon}}
        self.nodes = {
            int(row['NB_SCATS_SITE']): {'lat': row['LATITUDE'], 'lon': row['LONGITUDE']}
            for _, row in df_coords.iterrows()
        }

        # 2. Store Static Topology
        # We keep distance separate so we can re-calculate time when flow changes
        self.static_edges = connectivity_list 
        
        # 3. Adjacency List for Search Algorithms
        self.adj = {}

    def update_edge_costs(self, predicted_flows):
        """
        Re-calculates the travel time for every edge based on predicted flows.
        predicted_flows: dict {SiteID: flow_value}
        """
        self.adj = {} # Reset adjacency list
        
        for u, v, dist in self.static_edges:
            if u not in self.adj:
                self.adj[u] = {}
            
            # Calculate the Path Cost (Travel Time in Seconds)
            # We pass the whole dict, but calculations.py usually looks for flow at 'u'
            cost = calculate_travel_time(u, v, dist, predicted_flows)
            
            # This is what Dijkstra/A* will iterate over
            self.adj[u][v] = cost

    def haversine_heuristic(self, current_node, goal_node):
        """
        Heuristic: Straight-line time estimate in seconds.
        """
        if current_node not in self.nodes or goal_node not in self.nodes:
            return 0

        lat1, lon1 = self.nodes[current_node]['lat'], self.nodes[current_node]['lon']
        lat2, lon2 = self.nodes[goal_node]['lat'], self.nodes[goal_node]['lon']

        # Haversine formula to find distance in km
        lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
        dlon = lon2 - lon1 
        dlat = lat2 - lat1 
        a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
        c = 2 * asin(sqrt(a)) 
        r = 6371 # Radius of earth in km
        distance_km = c * r

        # Convert to TIME (Seconds) assuming max speed of 60km/h
        # Time = (Distance / Speed) * 3600
        return (distance_km / 60) * 3600

    def get_neighbors(self, node):
        return self.adj.get(node, {}).items()
    
class BoroondaraProblem:
    def __init__(self, initial, goals, graph):
        self.initial = initial
        self.goals = goals
        self.graph = graph

    def actions(self, state):
        # Returns Site IDs connected to the current state
        return list(self.graph.adj.get(state, {}).keys())

    def goal_test(self, state):
        return state in self.goals

    def path_cost(self, cost_so_far, state1, action, state2):
        # Gets the travel time (seconds) from the adjacency list
        return cost_so_far + self.graph.adj[state1][state2]

    def h(self, node):
        # Returns the minimum time to any of the goal nodes
        return min(self.graph.haversine_heuristic(node.state, g) for g in self.goals)
