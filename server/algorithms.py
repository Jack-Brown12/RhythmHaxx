import overpy
import math


def gmaps_link(coords):
    base = "https://www.google.com/maps/dir/"
    waypoints = "/".join(f"{lat},{lon}" for lat, lon in coords)
    return base + waypoints + "/"



def get_map_path_coordinates(initial_point, scaling_factor, points):
    #print("Initial Point:", initial_point)
    #print("Scaling Factor:", scaling_factor)
    #print("Points:", points)

    min_lat = float('inf')
    max_lat = float('-inf')
    min_lon = float('inf')
    max_lon = float('-inf')
    bounds = [min_lat,max_lat,min_lon,max_lon]
    

    # Scale, translate and find bounds
    points = scale_point(points,scaling_factor)
    points,bounds = translate_point(points,initial_point,bounds)
    #temporary, remove bounds = [43.47721....etc] -> just for testing
    bounds = [43.477211,-80.553445,43.477211,-80.547533]
    print(f"Bounds: {bounds}")
    MapData = pulldata(bounds)
    ClosestPoint = FindClosestNode([43.478305, -80.549604],MapData)
    print(ClosestPoint)



    

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

     
    
     
