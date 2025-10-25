import requests

def get_map_path_coordinates(initial_point, scaling_factor, points):
    print("Initial Point:", initial_point)
    print("Scaling Factor:", scaling_factor)
    print("Points:", points)

    # Scale, translate and find bounds

    # Snap points to grid using API that strava uses


    return { "path_coordinates": [[1,1]] }


def snap_to_map(points):
    pass


def fetch_snapped_points(points):
    query = "https://router.project-osrm.org/match/v1/driving/" + ";".join([f"{lon},{lat}" for lat, lon in points]) + "?geometries=geojson&overview=full"
    
    response = requests.get(query)
    
    if response.status_code == 200:
        data = response.json()
        if 'matchings' in data and len(data['matchings']) > 0:
            return data['matchings'][0]['geometry']['coordinates']


    print("No matchings found in the response.")
    return []
