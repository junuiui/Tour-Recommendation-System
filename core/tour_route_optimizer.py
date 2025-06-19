# Description:
#   Recommoned walking path based on the closest distance from the current location (picture).

import numpy as np
import pandas as pd

import osmnx as ox
import networkx as nx

# cache
WALKING_GRAPH = None
DRIVING_GRAPH = None

def load_graph():
    global WALKING_GRAPH, DRIVING_GRAPH

    if WALKING_GRAPH is None:
        print("Loading walking network from OSM...")
        WALKING_GRAPH = ox.graph_from_place("Metro Vancouver, British Columbia, Canada", network_type='walk')
        print("Walking network loading completed!\n")

    if DRIVING_GRAPH is None:
        print("Loading driving network from OSM...")
        DRIVING_GRAPH = ox.graph_from_place("Metro Vancouver, British Columbia, Canada", network_type='drive')
        print("Driving network loading completed!\n")
        
def walking_route_distance(start_lat, start_lon, end_lat, end_lon):
    global WALKING_GRAPH
    G = WALKING_GRAPH

    try:
        start_node = ox.distance.nearest_nodes(G, X=start_lon, Y=start_lat)
        end_node = ox.distance.nearest_nodes(G, X=end_lon, Y=end_lat)
        route = nx.shortest_path(G, start_node, end_node, weight='length')
        length = nx.shortest_path_length(G, start_node, end_node, weight='length')
        return length / 1000, route
    except Exception as e:
        # print(f"Walking path error: {e}")
        return None, None
    
def driving_route_distance(start_lat, start_lon, end_lat, end_lon):
    global DRIVING_GRAPH
    G = DRIVING_GRAPH

    try:
        start_node = ox.distance.nearest_nodes(G, X=start_lon, Y=start_lat)
        end_node = ox.distance.nearest_nodes(G, X=end_lon, Y=end_lat)
        route = nx.shortest_path(G, start_node, end_node, weight='length')
        length = nx.shortest_path_length(G, start_node, end_node, weight='length')
        return length / 1000, route
    except Exception as e:
        # print(f"Driving path error: {e}")
        return None, None

def haversine(lat1, lon1, lat2, lon2):
    R = 6371  # Earth r in km
    lat1, lon1, lat2, lon2 = map(np.radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = np.sin(dlat/2)**2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon/2)**2
    c = 2 * np.arctan2(np.sqrt(a), np.sqrt(1 - a))
    return R * c

def remove_duplicate_amenities(places):
    """
    Remove rows with duplicate theme, keeping only the first occurrence.
    """
    return places.drop_duplicates(subset='amenity', keep='first').reset_index(drop=True)

def find_nearest_path(start_point, places):
    visited = []
    remaining = places.copy()
    current = start_point

    while not remaining.empty:
        remaining['distance'] = remaining.apply(
            lambda row: haversine(current[0], current[1], row['lat'], row['lon']),
            axis=1
        )

        nearest = remaining.sort_values(by='distance').iloc[0]
        visited.append(nearest)
        
        current = (nearest['lat'], nearest['lon'])
        remaining = remaining.drop(nearest.name)

    return visited
