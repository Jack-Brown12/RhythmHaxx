import overpy
import os
import math
import requests

API_KEY = os.getenv("MAPBOX_API_KEY")
BOUNDARY_PADDING = 2

def get_map_path_coordinates(initial_point, scaling_factor, points, use_MAPBOX = False):

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
  
    #temporary, remove bounds = [43.47721....etc] -> just for testing
    bounds = [43.477211,-80.553445,43.477211,-80.547533]
    print(f"Bounds: {bounds}")
    MapData = pulldata(bounds)
    ClosestPoint = FindClosestNode([43.478305, -80.549604],MapData)
    print(ClosestPoint)
    # Return coordinates
    return { "path_coordinates": [1,1] }

# Fetch snapped points from Mapbox API
def fetch_snapped_points(points):
    query = "https://api.mapbox.com/matching/v5/mapbox/walking/" + ";".join([f"{lon},{lat}" for lon, lat in points]) + "?geometries=geojson&access_token=" + API_KEY
    response = requests.get(query)
    
    if response.status_code == 200:
        data = response.json()
        if 'matchings' in data and len(data['matchings']) > 0:
            return data['matchings'][0]['geometry']['coordinates']
        return None
    return None


def pulldata(bounds):
    api = overpy.Overpass()
    query = f"""
    [out:json][timeout:25];
    (
    way["highway"~"footway|path|pedestrian|residential|tertiary|secondary|primary|service|unclassified|living_street"]({str(bounds[0])},{str(bounds[1])},{str(bounds[2])},{str(bounds[3])});
    );
    out body;
    >;
    out skel qt;
    """
    result = api.query(query)
    print(f"How many Ways: {len(result.ways)}")
    return result

def FindClosestNode(Point,Data:overpy.Result):
    print(Point)
    closestPoint = []
    closestDistance = 10**100
    allnodes = [[float(node.lat),float(node.lon)] for way in Data.ways for node in way.nodes]
    for [x,y] in allnodes:
         DistFromPoint = math.sqrt(((Point[1]-y)*111000*math.cos(math.radians(Point[0])))**2+((Point[0]-x)*111000)**2) 
         print(DistFromPoint)
         if (DistFromPoint < closestDistance):
              closestDistance = DistFromPoint
              closestPoint = [x,y]
    print(closestDistance)
    return closestPoint
      
get_map_path_coordinates([4,4],3,[[0,0],[0,2],[2,2],[2,0]])
