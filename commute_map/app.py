"""Application boundary: validate inputs, compute the model, expose evidence."""
from dataclasses import asdict
import time
from .model import Policy, nonnegative
from .routing import RoutingIndex, classify
from .scenarios import build_scenario
from .sampling import Observation, sample_grid
from .contours import boundary_segments, feature_collection, touches_domain_edge


DEFAULTS = {"threshold":45.0, "direction":"work_to_home", "period":"example",
            "buffer_min_per_km":0.2, "condo_minutes":5.0,
            "size":32, "method":"full", "budget":None}


def configuration(raw=None):
    if raw is None:
        raw = {}
    if not isinstance(raw, dict):
        raise ValueError("configuration must be a JSON object")
    extra = set(raw)-set(DEFAULTS)
    if extra:
        raise ValueError("unknown settings: " + ", ".join(sorted(extra)))
    config = DEFAULTS | raw
    for key, high in (("threshold",240),("buffer_min_per_km",5),("condo_minutes",60)):
        value = nonnegative(config[key],key)
        if value > high or (key == "threshold" and value == 0):
            raise ValueError(f"{key} is outside its supported range")
        config[key] = value
    if isinstance(config["size"],bool) or config["size"] not in (16,32,64):
        raise ValueError("size must be 16, 32, or 64")
    if not isinstance(config["size"],int):
        raise ValueError("size must be an integer")
    if config["budget"] is None:
        config["budget"] = config["size"]**2
    if isinstance(config["budget"],bool) or not isinstance(config["budget"],int) or not 0 <= config["budget"] <= 4096:
        raise ValueError("budget must be an integer from 0 to 4096")
    if config["direction"] not in ("home_to_work","work_to_home"):
        raise ValueError("invalid direction")
    if config["method"] not in ("full","uniform","adaptive"):
        raise ValueError("invalid sampling method")
    Policy(config["period"],config["buffer_min_per_km"],config["condo_minutes"])
    return config


def describe_route(index, home, threshold):
    node = index.graph.nodes[home]
    route = index.route(home)
    return {"id":home,"name":node.name,"area":node.area,"condo":node.condo,
            "x":node.x,"y":node.y,"status":classify(route,threshold),
            "planning_minutes":route.planning_minutes,
            "breakdown":{"corridor":route.corridor_minutes,"local":route.local_minutes,
                         "access":route.access_minutes,"buffer":route.buffer_minutes},
            "distance_km":route.distance_km if route.status=="ok" else None,
            "path":list(route.nodes),
            "route_points":[[index.graph.nodes[n].x,index.graph.nodes[n].y] for n in route.nodes]}


def run(raw=None):
    started = time.perf_counter()
    config = configuration(raw)
    scenario = build_scenario(config["size"])
    policy = Policy(config["period"],config["buffer_min_per_km"],config["condo_minutes"])
    index = RoutingIndex(scenario.graph,scenario.workplace,config["direction"],policy)
    indexed_at = time.perf_counter()
    def oracle(x,y):
        route = index.route(scenario.cells[x,y])
        return Observation(route.status,route.planning_minutes)
    grid = sample_grid(oracle,scenario.size,config["threshold"],config["budget"],config["method"])
    examples = [describe_route(index,key,config["threshold"]) for key in scenario.examples]
    # Grid details are withheld for unqueried cells; the sampler sees no holdout values.
    details = {}
    for (x,y),key in scenario.cells.items():
        if grid["observed"][y][x]:
            details[f"{x},{y}"] = describe_route(index,key,config["threshold"])
    return {"config":config,"grid":grid,"examples":examples,"cell_details":details,
            "outline":boundary_segments(grid["labels"]),
            "potentially_truncated":touches_domain_edge(grid["labels"]),
            "landmarks":[{"id":n.id,"name":n.name,"x":n.x,"y":n.y}
                         for n in scenario.graph.nodes.values() if not n.home],
            "manifest":{"source":"synthetic_kl_v1","version":"0.1.0",
                        "distance_units":"km","time_units":"minutes",
                        "route_model":"directed static snapshot; additive nonnegative edge costs",
                        "buffer_model":"assumed minutes per routed km; not a percentile or reliability guarantee",
                        "condo_model":"once per home endpoint, including arrival in outbound mode",
                        "period_model":"invented directional scenario multipliers; no live departure-time API",
                        "spatial_model":"32 by 32 schematic km; each cell represents one assumed access point",
                        "algorithm":"single workplace Dijkstra; reverse graph for home_to_work",
                        "graph_nodes":len(scenario.graph.nodes),"graph_edges":len(scenario.graph.edges),
                        "relaxations":index.relaxations,"index_seconds":indexed_at-started,
                        "total_seconds":time.perf_counter()-started,
                        "sample_queries":grid["queries"],"example_queries":len(examples),
                        "paid_api_calls":0}}


def export(raw=None):
    result = run(raw)
    geojson = feature_collection(result["grid"])
    geojson["manifest"] = result["manifest"]
    geojson["config"] = result["config"]
    return geojson
