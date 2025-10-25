import overpy
import os

import requests

API_KEY = os.getenv("MAPBOX_API_KEY")


query = """
[out:json][timeout:25];
(
  way["highway"~"footway|path|pedestrian"]["foot"~"yes|designated"](45.50,-73.57,45.51,-73.56);
);
out body;
>;
out skel qt;
"""
BOUNDARY_PADDING = 2


def get_map_path_coordinates(initial_point, scaling_factor, points, use_MAPBOX = False):
    api = overpy.Overpass()
    result = api.query(query)
    print(result.ways)

    # min x, max x, min y, max y
    bounds = [float('inf'), float('-inf'), float('inf'), float('-inf')]

    # Scale, translate and find bounds
    for i in range(len(points)):
        # Scale
        points[i][0] *= scaling_factor
        points[i][1] *= scaling_factor

        # Translate
        points[i][0] += initial_point[0]
        points[i][1] += initial_point[1]

        # Update bounds
        bounds[0] = min(bounds[0], points[i][0])
        bounds[1] = max(bounds[1], points[i][0])
        bounds[2] = min(bounds[2], points[i][1])
        bounds[3] = max(bounds[3], points[i][1])

    # Add padding to bounds
    bounds[0] -= BOUNDARY_PADDING
    bounds[1] += BOUNDARY_PADDING
    bounds[2] -= BOUNDARY_PADDING
    bounds[3] += BOUNDARY_PADDING

    
    # Snap points to grid using API that strava uses
    if use_MAPBOX:
      snapped_points = fetch_snapped_points(points)
      return { "path_coordinates": snapped_points }
    
    # Run DFS to find a best-matching path

    # Return coordinates
    return { "path_coordinates": [1,1] }

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


def pulldata(bounds):
     pass


get_map_path_coordinates([4,4],3,[[0,0],[0,2],[2,2],[2,0]])
