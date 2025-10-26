import os

import osmnx
import pyproj
import requests
from shapely import LineString
from shapely.ops import transform

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
