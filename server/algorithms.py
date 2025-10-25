import overpy

api = overpy.Overpass()
query = """
[out:json][timeout:25];
(
  way["highway"~"footway|path|pedestrian"]["foot"~"yes|designated"](45.50,-73.57,45.51,-73.56);
);
out body;
>;
out skel qt;
"""
result = api.query(query)
print(result.ways)
def get_map_path_coordinates(initial_point, scaling_factor, points):
    #print("Initial Point:", initial_point)
    #print("Scaling Factor:", scaling_factor)
    #print("Points:", points)

    min_x = float('inf')
    max_x = float('-inf')
    min_y = float('inf')
    max_y = float('-inf')
    bounds = [min_x,max_x,min_y,max_y]

    # Scale, translate and find bounds
    points = scale_point(points,scaling_factor)
    points,bounds = translate_point(points,initial_point,bounds)
    print(points)
    print(bounds)
    

    # Find closest node to starting point

    # Run DFS to find best-matching path

    # Return coordinates
    
    return { "path_coordinates": [1,1] }



def scale_point(point, scaling_factor):
    for i in range(len(point)):
            point[i][0] *= scaling_factor
            point[i][1] *= scaling_factor
 
    return point
    

def translate_point(point, initial_point, bounds):
    for i in range(len(point)):
        point[i][0] += initial_point[0]
        point[i][1] += initial_point[1]
        bounds[0] = min(bounds[0],point[i][0]-2)
        bounds[1] = max(bounds[1],point[i][0]+2)
        bounds[2] = min(bounds[2],point[i][1]-2)
        bounds[3] = max(bounds[3],point[i][1]+2)
    return point,bounds

def pulldata(bounds):
     pass
     

    
get_map_path_coordinates([4,4],3,[[0,0],[0,2],[2,2],[2,0]])
    




