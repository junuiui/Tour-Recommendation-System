import sys
import pandas as pd
import numpy as np
import folium
from folium.plugins import MarkerCluster

FOOD_AMENITIES = {
    'cafe', 'restaurant', 'fast_food', 'bar', 'pub', 
    'internet_cafe', 'food_court', 'ice_cream', 'biergarten'
}

def haversine(lat1, lon1, lat2, lon2):
    R = 6371000

    lat1, lon1, lat2, lon2 = map(np.radians, [lat1, lon1, lat2, lon2])

    diff_lat = lat2 - lat1
    diff_lon = lon2 - lon1

    a = np.sin(diff_lat / 2) ** 2 + np.cos(lat1) * np.cos(lat2) * np.sin(diff_lon / 2) ** 2
    c = 2 * np.arctan2(np.sqrt(a), np.sqrt(1 - a))

    distances = R * c / 1000
    
    return distances

def filter_food_place(data):
    food = data[data['amenity'].isin(FOOD_AMENITIES)]
    return food

def filter_not_food_place(data):
    not_food = data[~data['amenity'].isin(FOOD_AMENITIES)]
    return not_food

def find_near_amenities(photo, amenity):
    amenity = filter_not_food_place(amenity)
    near_amenity = []
    max_distance_km = 1
    
    for _, row in amenity.iterrows():
        distance = haversine(photo['latitude'], photo['longitude'], row['lat'], row['lon'])
        if distance <= max_distance_km:
            near_amenity.append((row, distance))
    return sorted(near_amenity, key = lambda x: x[1])

def find_near_food(photo, amenity, max_distance_km):
    amenity = filter_food_place(amenity)
    near_food = []
    for _, row in amenity.iterrows():
        distance = haversine(photo['latitude'], photo['longitude'], row['lat'], row['lon'])
        if distance <= max_distance_km:
            near_food.append((row, distance))
    return sorted(near_food, key = lambda x: x[1])

def show_all_amenity_type(data):
    unique = data[['amenity']].drop_duplicates()
    unique = unique['amenity'].sort_values()
    return unique

def make_map(amenity, amenity_type):
    amenity = amenity[amenity['amenity'] == amenity_type]

    m = folium.Map(location = [amenity['lat'].mean(), amenity['lon'].mean()], zoom_start = 10)
    marker = MarkerCluster().add_to(m)

    for _, row in amenity.iterrows():
        name = row['name']
        text = f'{name} ({row['amenity']})'
        folium.Marker(
            location = [row['lat'], row['lon']],
            popup = text,
            icon = folium.Icon(color = 'red')
        ).add_to(marker)

    return m

def tour(photo, amenity):
    route = []
    for _, row in photo.iterrows():
        near_amenity = find_near_amenities(row, amenity)
        if near_amenity:
            route.append((photo, near_amenity))
    return route



