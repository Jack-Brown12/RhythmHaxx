import overpy
import math
import matplotlib.pyplot as plt
import numpy as np


Minscore = 10*100
PathOfBest = []
numTraverse = 0

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
    bounds = [43.456500, -80.575000, 43.479500, -80.545000]
    print(f"Bounds: {bounds}")
    MapData = pulldata(bounds)
    test = EvaluateGraph([[float(node.lat),float(node.lon)] for way in MapData.ways for node in way.nodes],points)
    print(test)
    ClosestPoint = FindClosestNode([43.478305, -80.549604],MapData)
    print(f"Closest Point is: {ClosestPoint}")
    Graph = GetGraph(MapData)
    #for key,sets in Graph.items():
        #print(f"{key}:{sets}")
    plot_graph(Graph,points,test)
    #DFS(ClosestPoint,Graph,[],points)
    #print(PathOfBest)
   

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
    way["highway"~"footway|path|pedestrian|residential|tertiary|secondary|primary"]({str(bounds[0])},{str(bounds[1])},{str(bounds[2])},{str(bounds[3])});
    );
    out body;
    >;
    out skel qt;
    """
    result = api.query(query)
    print(f"How many Ways: {len(result.ways)}")
    return result

def FindClosestNode(Point,Data:overpy.Result):
    closestPoint = []
    closestDistance = 10**100
    allnodes = [[float(node.lat),float(node.lon)] for way in Data.ways for node in way.nodes]
    for [x,y] in allnodes:
         DistFromPoint = FindDistance(Point,x,y)
         if (DistFromPoint < closestDistance):
              closestDistance = DistFromPoint
              closestPoint = [x,y]
    print(closestDistance)
    return closestPoint
         
def GetGraph(Data:overpy.Result):
    graph = {}
    for way in Data.ways:
        nodes = way.nodes
        for i in range(len(nodes)):
            if not i == len(nodes)-1:
                graph.setdefault((float(nodes[i].lat),float(nodes[i].lon)),set()).add((float(nodes[i+1].lat),float(nodes[i+1].lon)))
                graph.setdefault((float(nodes[i+1].lat),float(nodes[i+1].lon)),set()).add((float(nodes[i].lat),float(nodes[i].lon)))
    return graph
    
    
def FindDistance(Point,x,y):
    return math.sqrt(((Point[1]-y)*111000*math.cos(math.radians(Point[0])))**2+((Point[0]-x)*111000)**2) 



def EvaluateGraph(CurGraph,ComparisonPoints):
    
    Nodes = set()
    for i in ComparisonPoints:
        shortest = 10**100
        CurNodes = []
        
        for j in range(len(CurGraph)-1):
            vectorAtoB = np.array(CurGraph[j+1])-np.array(CurGraph[j])
            vectorAtoP = np.array(i) - np.array(CurGraph[j])
            vectorClosestPointOnAB = (np.dot(vectorAtoB,vectorAtoP)/(np.linalg.norm(vectorAtoB))**2) * vectorAtoB
            shortestDistance = np.linalg.norm(np.array(i) - vectorClosestPointOnAB)
            if shortestDistance < shortest:
                shortest = shortestDistance
                CurNodes = (tuple(CurGraph[j]),tuple(CurGraph[j+1]))
                print(shortestDistance)
        
        Nodes.add(CurNodes)
    
    return Nodes
    
def plot_graph(graph,points,solution):
    plt.figure(figsize=(8,8))
    for node, neighbors in graph.items():
        x1, y1 = node
        for n in neighbors:
            x2, y2 = n
            plt.plot([y1, y2], [x1, x2], color='blue')  
    for i in range(len(points)-1):
        plt.plot([points[i][1],points[i+1][1]],[points[i][0],points[i+1][0]],color='red')
    solution = [x for x in solution]
    for i in range(len(solution)-1):
        for j in range(i):
            plt.plot([solution[i][j][1],solution[i+1][j][1]],[solution[i][j][0],solution[i+1][j][0]],color='green')


    plt.plot()
    plt.xlabel("Longitude")
    plt.ylabel("Latitude")
    plt.title("Graph Visualization")
    plt.show()


        
get_map_path_coordinates([43.465315, -80.559927],10,[
    [0.0, 0.0],
    [0.0, 0.00025],
    [0.0, 0.0005],
    [0.0, 0.00075],
    [0.0, 0.001],
    
    [0.00025, 0.001],
    [0.0005, 0.001],
    [0.00075, 0.001],
    [0.001, 0.001],
    
    [0.001, 0.00075],
    [0.001, 0.0005],
    [0.001, 0.00025],
    [0.001, 0.0],
    
    [0.00075, 0.0],
    [0.0005, 0.0],
    [0.00025, 0.0],
    
    [0.0, 0.0]  
]
)

     
    
     
