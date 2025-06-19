import sys
import pandas as pd
import numpy as np
import folium
from folium.plugins import MarkerCluster

FOOD_AMENITIES = {
    'cafe', 'restaurant', 'fast_food', 'bar', 'pub', 
    'internet_cafe', 'food_court', 'ice_cream', 'biergarten'
}

def filter_food_place(data):
    food = data[data['amenity'].isin(FOOD_AMENITIES)]
    return food

def create_food_map(amenity):
    food = filter_food_place(amenity)

    m = folium.Map(location = [food['lat'].mean(), food['lon'].mean()], zoom_start = 10)
    marker = MarkerCluster().add_to(m)

    for _, row in food.iterrows():
        name = row['name']
        text = f'{name} ({row['amenity']})'
        folium.Marker(
            location = [row['lat'], row['lon']],
            popup = text,
            icon = folium.Icon(color = 'red', icon = 'cutlery', prefix = 'fa')
        ).add_to(marker)

    return m