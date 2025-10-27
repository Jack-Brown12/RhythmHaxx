import os
import osmnx
import pyproj
import requests
from shapely import LineString
from shapely.ops import transform
import overpy
import math
import matplotlib.pyplot as plt
import numpy as np
import heapq

API_KEY = os.getenv("MAPBOX_API_KEY")
BOUNDARY_PADDING = 0.002
SHAPE_PENALTY_MULTIPLIER = 4
LENGTH_WEIGHT = 0.1

# Main function to get map path coordinates
def get_map_path_coordinates(points):
    try:
        # min x, max x, min y, max y
        bounds = [float('inf'), float('-inf'), float('inf'), float('-inf')]

        for i in range(len(points)):
            temp = points[i][0]
            points[i][0] = points[i][1]
            points[i][1] = temp

            bounds[0] = min(bounds[0], points[i][0])
            bounds[1] = max(bounds[1], points[i][0])
            bounds[2] = min(bounds[2], points[i][1])
            bounds[3] = max(bounds[3], points[i][1])

        bounds[0] -= BOUNDARY_PADDING
        bounds[1] += BOUNDARY_PADDING
        bounds[2] -= BOUNDARY_PADDING
        bounds[3] += BOUNDARY_PADDING

        G = osmnx.graph_from_bbox((bounds[0], bounds[2], bounds[1], bounds[3]), retain_all=True, network_type='walk')
        g_proj = osmnx.project_graph(G)

        target_shape_geom = LineString(points)

        points_proj_geometry = osmnx.projection.project_geometry(
            LineString(points),
            to_crs=g_proj.graph['crs'],
        )[0]

        transformer_to_proj = pyproj.Transformer.from_crs(
            'EPSG:4326', g_proj.graph['crs'], always_xy=True
        )
        transformer_to_wgs84 = pyproj.Transformer.from_crs(
            g_proj.graph['crs'], 'EPSG:4326', always_xy=True
        )

        target_shape_proj = transform(transformer_to_proj.transform, target_shape_geom)

        projected_points = list(target_shape_proj.coords)

        start_xy = projected_points[0]
        end_xy = projected_points[-1]

        start_node = osmnx.nearest_nodes(g_proj, X=start_xy[0], Y=start_xy[1])
        end_node = osmnx.nearest_nodes(g_proj, X=end_xy[0], Y=end_xy[1])

        for u, v, k, data in g_proj.edges(keys=True, data=True):
            edge_length = data['length']

            if "geometry" in data:
                edge_geom = data['geometry']
                distance_from_shape = edge_geom.distance(target_shape_proj)
                penalty = distance_from_shape * SHAPE_PENALTY_MULTIPLIER
                new_weight = edge_length * LENGTH_WEIGHT + penalty
            else:
                new_weight = edge_length * LENGTH_WEIGHT

            g_proj[u][v][k]['penalty_weight'] = new_weight

        route_nodes = osmnx.shortest_path(g_proj, start_node, end_node, weight="penalty_weight")
        route_gdf = osmnx.routing.route_to_gdf(g_proj, route_nodes)

        path_geom_proj = route_gdf.unary_union
        path_geom_wgs84 = transform(transformer_to_wgs84.transform, path_geom_proj)
        final_coordinates = []

        if path_geom_wgs84.is_empty:
            pass
        elif path_geom_wgs84.geom_type == 'LineString':
            final_coordinates = list(path_geom_wgs84.coords)
        elif path_geom_wgs84.geom_type == 'MultiLineString':
            for line in path_geom_wgs84.geoms:
                final_coordinates.extend(list(line.coords))

        for i in range(len(final_coordinates)):
            temp = final_coordinates[i][0]
            final_coordinates[i] = (final_coordinates[i][1], temp)

        return {"points": final_coordinates}

    except:
        final_coordinates = fetch_snapped_points(points)

        for i in range(len(final_coordinates)):
            temp = final_coordinates[i][0]
            final_coordinates[i] = (final_coordinates[i][1], temp)

        if final_coordinates:
            return {"points": final_coordinates}
    return None


# Fetch snapped points from Mapbox API
def fetch_snapped_points(points):
    query = "https://api.mapbox.com/matching/v5/mapbox/walking/" + ";".join(
        [f"{lon},{lat}" for lon, lat in points]) + "?geometries=geojson&access_token=" + API_KEY
    response = requests.get(query)

    if response.status_code == 200:
        data = response.json()
        if 'matchings' in data and len(data['matchings']) > 0:
            return data['matchings'][0]['geometry']['coordinates']
        return None
    return None







def JasonAlgorithm(points):
    #print("Initial Point:", initial_point)
    #print("Scaling Factor:", scaling_factor)
    #print("Points:", points)

    min_lat = float('inf')
    max_lat = float('-inf')
    min_lon = float('inf')
    max_lon = float('-inf')
    bounds = [min_lat,max_lat,min_lon,max_lon]
    

    # Scale, translate and find bounds
    for i in range(len(points)):
            bounds[0] = min(bounds[0],points[i][0]-0.01)
            bounds[1] = max(bounds[1],points[i][0]+0.01)
            bounds[2] = min(bounds[2],points[i][1]-0.01)
            bounds[3] = max(bounds[3],points[i][1]+0.01)


    print(f"Bounds: {bounds}")
    MapData = pulldata(bounds)
    test = EvaluateGraph([[float(node.lat),float(node.lon)] for way in MapData.ways for node in way.nodes],points)
    Graph = GetGraph(MapData)
    #StartToGraphNode = FindClosestNode(points[0],test)
    ActualSolution = []

    for i in range(len(test)-1):
        ActualSolution.append(Search(Graph,tuple(test[i]),tuple(test[i+1])))
    t = []

    for i in ActualSolution:
        try:
            for j in i:
                try:
                    t.append(j)
                except Exception:
                    pass
            
        except Exception:
            pass
    t = list(dict.fromkeys(t))
    print(f"Actual Solution: {t}")
    return { "points": t}



def scale_point_translate(point, initial_point,bounds):
    for i in range(len(point)):
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
    way["highway"~"footway|tertiary|secondary|primary"]({str(bounds[0])},{str(bounds[2])},{str(bounds[1])},{str(bounds[3])});
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


if __name__ == "__main__":
    JasonAlgorithm([
            [43.466215, -80.561157],  # top-left
    [43.466215, -80.558697],  # top-right
    [43.464415, -80.558697],  # bottom-right
    [43.464415, -80.561157],  # bottom-left
    [43.466215, -80.561157]]
    
            
        
    )


     
    
     

