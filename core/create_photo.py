import pandas as pd
import numpy as np
import random

def generate_photo_data(num_photos):
    photos = []
    lat = 49.2 + random.random() * 0.3
    lon = -123.2 + random.random() * 0.3
    timestamp = pd.Timestamp.now() - pd.to_timedelta(random.randint(0, 365), unit='D')
    for _ in range(num_photos):
        photos.append({'latitude': lat, 'longitude': lon, 'timestamp': timestamp})

        lat += (random.random() - 0.5) * 0.01
        lon += (random.random() - 0.5) * 0.01 

        lat = max(49.2, min(49.5, lat))
        lon = max(-123.5, min(-122.9, lon))

        timestamp += pd.to_timedelta(random.randint(5, 180), unit='min')

    return pd.DataFrame(photos)

def generate_vancouver_photo_data(num_photos):
    LAT_MIN, LAT_MAX = 49.0, 49.4
    LON_MIN, LON_MAX = -123.3, -122.5

    photos = []
    
    lat = random.uniform(LAT_MIN, LAT_MAX)
    lon = random.uniform(LON_MIN, LON_MAX)
    timestamp = pd.Timestamp.now() - pd.to_timedelta(random.randint(0, 365), unit='D')
    
    for _ in range(num_photos):
        photos.append({'latitude': lat, 'longitude': lon, 'timestamp': timestamp})
        
        lat += (random.random() - 0.5) * 0.01
        lon += (random.random() - 0.5) * 0.01
        
        lat = max(LAT_MIN, min(LAT_MAX, lat))
        lon = max(LON_MIN, min(LON_MAX, lon))
        
        timestamp += pd.to_timedelta(random.randint(5, 180), unit='min')
    
    return pd.DataFrame(photos)

def main():
    photos = generate_photo_data(10)
    
    photos.to_csv("photos.csv", index=False)

    v_photos = generate_vancouver_photo_data(10)
    
    v_photos.to_csv("v_photos.csv", index=False)
    
if __name__ == '__main__': 
    main()
