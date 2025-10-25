import os

import requests

API_KEY = os.getenv("MAPBOX_API_KEY")

def get_map_path_coordinates(initial_point, scaling_factor, points):
    print("Initial Point:", initial_point)
    print("Scaling Factor:", scaling_factor)
    print("Points:", points)

    # Scale, translate and find bounds

    # Snap points to grid using API that strava uses
    snapped_points = fetch_snapped_points(points)

    return { "path_coordinates": snapped_points }


def fetch_snapped_points(points):
    query = "https://api.mapbox.com/matching/v5/mapbox/walking/" + ";".join([f"{lon},{lat}" for lon, lat in points]) + "?geometries=geojson&access_token=" + API_KEY
    print(query)
    response = requests.get(query)
    
    if response.status_code == 200:
        data = response.json()
        if 'matchings' in data and len(data['matchings']) > 0:
            return data['matchings'][0]['geometry']['coordinates']


    print("No matchings found in the response.")
    return []
