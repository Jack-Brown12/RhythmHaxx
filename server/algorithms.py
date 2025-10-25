import overpy

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


def get_map_path_coordinates(initial_point, scaling_factor, points):
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

    # Run DFS to find a best-matching path

    # Return coordinates
    
    return { "path_coordinates": [1,1] }


def pulldata(bounds):
     pass


get_map_path_coordinates([4,4],3,[[0,0],[0,2],[2,2],[2,0]])
