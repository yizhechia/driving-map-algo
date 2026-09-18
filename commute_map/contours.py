"""Grid boundary extraction without smoothing or connecting diagonal cells."""
import math

def boundary_segments(labels):
    """Cancel shared sides of inside cells; retain internal hole boundaries."""
    edges = set()
    for y, row in enumerate(labels):
        for x, value in enumerate(row):
            if value != "inside":
                continue
            ring = [(x,y),(x+1,y),(x+1,y+1),(x,y+1),(x,y)]
            for a,b in zip(ring,ring[1:]):
                if (b,a) in edges:
                    edges.remove((b,a))
                else:
                    edges.add((a,b))
    return sorted(edges)

def geographic(x, y):
    # Illustrative local frame; not a surveyed access location.
    return [101.71+(x-24)/(111.32*math.cos(math.radians(3.16))), 3.16+(y-20)/111.32]

def feature_collection(grid):
    scale = 32/grid["size"]
    features = []
    for y,row in enumerate(grid["labels"]):
        for x,label in enumerate(row):
            if label != "inside":
                continue
            ring = [geographic(a*scale,b*scale) for a,b in
                    [(x,y),(x+1,y),(x+1,y+1),(x,y+1),(x,y)]]
            features.append({"type":"Feature", "geometry":{"type":"Polygon","coordinates":[ring]},
                             "properties":{"col":x,"row":y,"planning_minutes":grid["values"][y][x],
                                           "sampled":grid["observed"][y][x],"data_source":"synthetic"}})
    segments = [[geographic(a[0]*scale,a[1]*scale),geographic(b[0]*scale,b[1]*scale)]
                for a,b in boundary_segments(grid["labels"])]
    if segments:
        features.append({"type":"Feature","geometry":{"type":"MultiLineString","coordinates":segments},
                         "properties":{"role":"estimated_grid_boundary","data_source":"synthetic"}})
    return {"type":"FeatureCollection","features":features,
            "data_source":"Synthetic georeferenced fixture; not surveyed roads or traffic.",
            "cell_semantics":"Eligibility at cell centre; polygon interior is an approximation."}
