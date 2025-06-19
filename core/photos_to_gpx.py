import sys
import gpxpy
import gpxpy.gpx
import pandas as pd

def get_data(file):
    data = pd.read_csv(file, parse_dates=['timestamp'])
    return data

def photos_to_gpx(photos):
    """change Photos.csv to gpx file"""
    gpx = gpxpy.gpx.GPX()

    gpx_track = gpxpy.gpx.GPXTrack()
    gpx.tracks.append(gpx_track)

    gpx_segment = gpxpy.gpx.GPXTrackSegment()
    gpx_track.segments.append(gpx_segment)

    for _, row in photos.iterrows():
        gpx_segment.points.append(
            gpxpy.gpx.GPXTrackPoint(
                latitude = float(row['latitude']),
                longitude = float(row['longitude']),
                time = row['timestamp'].to_pydatetime()
            )
        )
    
    return gpx