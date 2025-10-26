import overpy
import math
import matplotlib.pyplot as plt
import numpy as np
import heapq


Minscore = 10*100
PathOfBest = []
numTraverse = 0

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
    points,bounds = scale_point_translate(points,scaling_factor,initial_point,bounds)

    #temporary, remove bounds = [43.47721....etc] -> just for testing

    print(f"Bounds: {bounds}")
    MapData = pulldata(bounds)
    test = EvaluateGraph([[float(node.lat),float(node.lon)] for way in MapData.ways for node in way.nodes],points)
    print(test)
    Graph = GetGraph(MapData)
    StartToGraphNode = FindClosestNode(initial_point,test)
    ActualSolution = []
    for i in range(len(test)-1):
        ActualSolution.append(Search(Graph,tuple(test[i]),tuple(test[i+1])))
    
    plot_graph(Graph,points,test,[initial_point,StartToGraphNode],ActualSolution)
 
    return { "path_coordinates": [1,1] }



def scale_point_translate(point, scaling_factor,initial_point,bounds):
    for i in range(len(point)):
            point[i][0] *= scaling_factor
            point[i][1] *= scaling_factor
            point[i][0] += initial_point[0]
            point[i][1] += initial_point[1]
            bounds[0] = min(bounds[0],point[i][0]-0.01)
            bounds[1] = max(bounds[1],point[i][0]+0.01)
            bounds[2] = min(bounds[2],point[i][1]-0.01)
            bounds[3] = max(bounds[3],point[i][1]+0.01)
    return point,bounds
    


def pulldata(bounds):
    api = overpy.Overpass()
    query = f"""
    [out:json][timeout:25];
    (
    way["highway"~"footway|path|pedestrian|residential|tertiary|secondary|primary|unclassified|service|track"]({str(bounds[0])},{str(bounds[2])},{str(bounds[1])},{str(bounds[3])});
    );
    out body;
    >;
    out skel qt;
    """
    result = api.query(query)
    print(f"How many Ways: {len(result.ways)}")
    return result

def FindClosestNode(Point,Nodes):
    shortest = 10**100
    closest = None
    for i in range(len(Nodes)):
        distance = FindDistance(Point,Nodes[i][0],Nodes[i][1])
        if distance < shortest:
            shortest = distance
            closest = Nodes[i]
    return closest
         

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


def Search(Graph,Start,End):
    heap = []
    ArrOfKnown = set()
    heapq.heappush(heap,(0,Start))
    PrevSuccessors = {}
    weights = {Start:0}

    
    while (heap):
        CurNode = heapq.heappop(heap)
        ArrOfKnown.add(CurNode[1])
        weights.update({CurNode[1]:CurNode[0]})
        if CurNode[1] == End:
            path = []
            Traversal = CurNode[1]
            while Traversal != Start:
                path.append(Traversal)
                Traversal = PrevSuccessors[Traversal]
            path.append(Start)
            return path[::-1]
        for neighbor in Graph[CurNode[1]]:
            if neighbor not in ArrOfKnown:
                CurValue = CurNode[0]+FindDistance(CurNode[1],neighbor[0],neighbor[1])
                if CurValue < weights.get(neighbor,float('inf')):
                    weights[neighbor] = CurValue
                    PrevSuccessors[neighbor] = CurNode[1]
                    heapq.heappush(heap,(CurValue,neighbor))
             
                

    
    
        
def EvaluateGraph(CurGraph,ComparisonPoints):
    
    Nodes = []
    for i in ComparisonPoints:
        shortest = 10**100
        CurNodes = []
        for j in range(len(CurGraph)-1):
            x = FindDistance(i,CurGraph[j][0],CurGraph[j][1])
            if x < shortest:
                shortest = x
                CurNodes=CurGraph[j]
        Nodes.append(CurNodes)
    return Nodes
    
def plot_graph(graph,points,solution,initial,ActualSolution):
    plt.figure(figsize=(8,8))
    for node, neighbors in graph.items():
        x1, y1 = node
        for n in neighbors:
            x2, y2 = n
            plt.plot([y1, y2], [x1, x2], color='blue')  
    for i in range(len(points)-1):
        plt.plot([points[i][1],points[i+1][1]],[points[i][0],points[i+1][0]],color='red')
    solution = [x for x in solution]
    for i in range(len(solution)):
        plt.plot(solution[i][1],solution[i][0],marker='o',color='green')
    plt.plot(initial[0][1],initial[0][0],marker='x',color='black',markersize=10)
    print([initial[0][1],points[1][0]],[initial[0][0],initial[1][0]])
    plt.plot([initial[0][1],initial[1][1]],[initial[0][0],initial[1][0]],color='yellow')
    for path in ActualSolution:
        for i in range(len(path)-1):
            plt.plot([path[i][1],path[i+1][1]],[path[i][0],path[i+1][0]],color='orange',linewidth=2)


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

     
    
     
