"""
Cleaning the data
"""

# ==============================================================
# Cleaning the data for amenities
# ==============================================================

# types of amenity that we are interested in
INTERESTING_AMENITIES = {'museum', 'theatre', 'arts_centre', 'cinema', 'library', 'public_bookcase',
    'monastery', 'courthouse', 'townhall', 'bar', 'pub', 'nightclub', 'casino',
    'biergarten', 'playground', 'marketplace', 'park', 'fountain', 'Observation Platform',
    'ferry_terminal', 'seaplane terminal', 'university', 'college', 'hospital',
    'fire_station', 'police'
}

def basic_clean_data(data):
    """
    Clean data
        1. Drop NaN values
        2. Drop duplicates
    """
    # drops NaNs
    data = data.dropna(subset=['lat', 'lon', 'timestamp', 'amenity'])
    
    # drop duplicates
    data = data.drop_duplicates(subset=['lat', 'lon'])
    
    return data.reset_index(drop=True)

def get_interesting_places(data):
    
    interesting_data = data[data['amenity'].isin(INTERESTING_AMENITIES)]
    return interesting_data.reset_index(drop=True)


def get_same_theme_places(data, theme):
    """
    Get same theme places
    """
    theme = theme.lower().strip()
    
    # Filter data based on the theme
    filtered_data = data[data['amenity'] == theme]
    
    return filtered_data.reset_index(drop=True)


def get_same_theme_places_by_tags_num(data, theme, tags, n):
    """
    Get same theme places by tags
    """
    data['tags'] = data['tags'].fillna({})
    
    # Filter data based on the theme and tags
    filtered = data[data['tags'].apply(len) > 2].reset_index()
    
    return filtered.reset_index(drop=True)


# ==============================================================
# Cleaning the data for photos (csv)
# ==============================================================
def photo_clean_data(data):
    
    data = data.dropna(subset=['latitude', 'longitude', 'timestamp'])
    
    return data.reset_index(drop=True)
    