# h3-py: Uber’s H3 Hexagonal Hierarchical Geospatial Indexing System in Python
# https://uber.github.io/h3-py/intro.html

import h3

# Constants involving H3 cell resolution.
# A resolution of 8 results in a hexagonal cell of roughly 1 km2 area and 0.5 km edge length.
RESOLUTION = 8

def latlon_to_h3(df, resolution = RESOLUTION):
    """
    Converts latitude and longitude to a specified H3 resolution.
    Inputs
        df: DataFrame
    Outputs
        df: DataFrame
    """
    df["h3"] = df.apply(lambda DF: h3.geo_to_h3(DF["latitude"], DF["longitude"], resolution), axis = 1)
    return df

def plot_hexagons(hexagons):
    """
    Plots H3 hexagons on a map.
    Inputs
        hexagons: list
    """
    m = visualize_hexagons(hexagons)
    display(m)

# The following functions are taken from:
# https://github.com/uber/h3-py-notebooks/blob/master/notebooks/usage.ipynb
def visualize_hexagons(hexagons, color = "red", folium_map = None):
    """
    hexagons is a list of hexcluster. Each hexcluster is a list of hexagons.
    eg. [[hex1, hex2], [hex3, hex4]]
    """
    polylines = []
    lat = []
    lng = []
    for hex in hexagons:
        polygons = h3.h3_set_to_multi_polygon([hex], geo_json = False)
        # flatten polygons into loops.
        outlines = [loop for polygon in polygons for loop in polygon]
        polyline = [outline + [outline[0]] for outline in outlines][0]
        lat.extend(map(lambda v:v[0],polyline))
        lng.extend(map(lambda v:v[1],polyline))
        polylines.append(polyline)
    
    if folium_map is None:
        m = folium.Map(location=[sum(lat)/len(lat), sum(lng)/len(lng)],
                       zoom_start = 13, tiles = 'cartodbpositron')
    else:
        m = folium_map
    for polyline in polylines:
        my_PolyLine = folium.PolyLine(locations = polyline, weight = 8,color = color)
        m.add_child(my_PolyLine)
    return m
    
def visualize_polygon(polyline, color):
    polyline.append(polyline[0])
    lat = [p[0] for p in polyline]
    lng = [p[1] for p in polyline]
    m = folium.Map(location = [sum(lat)/len(lat), sum(lng)/len(lng)],
                   zoom_start = 13, tiles = 'cartodbpositron')
    my_PolyLine = folium.PolyLine(locations = polyline, weight = 8, color = color)
    m.add_child(my_PolyLine)
    return m

