import osmnx as ox
import pandas as pd
from tqdm import tqdm

from machine_learning.common.config import (
    DEFAULT_TOPOLOGY_CONNECTIVITY_CSV,
    SNAPPED_TOPOLOGY_LOCATIONS_CSV
)

# tqdm library for visualizing a progress bar

def snap_scats_data(input_file, output_file):
    df = pd.read_csv(input_file)
    
    snapped_lats = []
    snapped_lons = []

    print(f"Processing {len(df)} sites...")

    for index, row in tqdm(df.iterrows(), total=len(df)):
        orig_lat = row['LATITUDE']
        orig_lon = row['LONGITUDE']
        
        try:
            # network_type='drive' ensures we stay on roads
            G = ox.graph_from_point((orig_lat, orig_lon), dist=500, network_type='drive')
            
            # Consolidate nearby nodes into single intersections with 25m tolerance
            G_proj = ox.project_graph(G)
            G_cons = ox.consolidate_intersections(G_proj, rebuild_graph=True, tolerance=25)
            G_final = ox.project_graph(G_cons, to_crs='EPSG:4326')
            
            nearest_node = ox.nearest_nodes(G_final, X=orig_lon, Y=orig_lat)
            
            new_lat = G_final.nodes[nearest_node]['y']
            new_lon = G_final.nodes[nearest_node]['x']
            
            snapped_lats.append(new_lat)
            snapped_lons.append(new_lon)
            
        except Exception as e:
            # If OSM doesn't have data for that area, keep original coordinates
            snapped_lats.append(orig_lat)
            snapped_lons.append(orig_lon)


    df['SNAPPED_LATITUDE'] = snapped_lats
    df['SNAPPED_LONGITUDE'] = snapped_lons
    
    df.to_csv(output_file, index=False)
    print(f"\nDone! Cleaned data saved to {output_file}")

def main():
    snap_scats_data(f"data/{DEFAULT_TOPOLOGY_CONNECTIVITY_CSV}", f"data/{SNAPPED_TOPOLOGY_LOCATIONS_CSV}")


if __name__ == "__main__":
    main()