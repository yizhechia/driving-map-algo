"""Reproducible road-node accessibility, separate from the synthetic grid UI."""
from dataclasses import asdict
import gzip
import hashlib
import json
from pathlib import Path
from .model import nonnegative
from .osm import import_osm, SPEED_KPH
from .turn_routing import TurnRoutingIndex


DATA = Path(__file__).resolve().parent / "data/klcc"


def load_case():
    manifest = json.loads((DATA / "manifest.json").read_text(encoding="utf-8"))
    compressed = (DATA / "roads.json.gz").read_bytes()
    if hashlib.sha256(compressed).hexdigest() != manifest["snapshot_sha256"]:
        raise ValueError("OSM snapshot checksum does not match the manifest")
    payload = json.loads(gzip.decompress(compressed))
    network = import_osm(payload, manifest["query_bounds_south_west_north_east"])
    return network, manifest


def run_road_case(direction="home_to_work", threshold=10, buffer=0.2, probe=None):
    threshold = nonnegative(threshold, "threshold")
    network, source = load_case()
    index = TurnRoutingIndex(network, source["anchor_node"], direction, buffer)
    features, counts = [], {"inside": 0, "outside": 0, "no_route": 0}
    for node, coordinates in network.nodes.items():
        cost = index.distance.get(node)
        status = "no_route" if cost is None else "inside" if cost <= threshold else "outside"
        counts[status] += 1
        features.append({
            "type": "Feature", "id": f"osm-node-{node}",
            "geometry": {"type": "Point", "coordinates": list(coordinates)},
            "properties": {"osm_node": node, "status": status, "planning_minutes": cost,
                           "endpoint_type": "road_node_probe"},
        })
    result = {
        "type": "FeatureCollection", "features": features,
        "metadata": {
            "case": source["case"], "direction": direction, "threshold_minutes": threshold,
            "buffer_min_per_km": index.beta, "anchor_node": source["anchor_node"],
            "anchor_label": source["anchor_label"], "source": source,
            "assumed_speed_kph": SPEED_KPH, "counts": counts,
            "index_states": len(index.states), "index_relaxations": index.relaxations,
            "audit": network.audit, "traffic_data": False, "paid_api_calls": 0,
            "domain_is_bounded": True,
            "limits": [
                "Static assumed speeds; no observed traffic, signals, queues, turn delays or reliability calibration.",
                "Endpoints are road nodes with no initial/final heading, driveway validation or building overhead.",
                "Unresolved restrictions close approaches; conditional access and unverified barriers are excluded.",
                "Immediate segment reversals are prohibited as a conservative assumption.",
                "OSM is incomplete and this importer supports only documented routing tags; routes are not navigation instructions.",
                "Routes are confined to the extract; a missing or slower route may require an omitted detour.",
                "Counts depend on OSM node density; point eligibility does not classify land, homes or cell interiors.",
            ],
        },
    }
    if probe is not None:
        route = index.route(probe)
        properties = asdict(route)
        properties["planning_minutes"] = route.planning_minutes
        properties["osm_way_ids"] = [network.edges[i].way for i in route.edges]
        result["route"] = {
            "type": "Feature", "properties": properties,
            "geometry": {"type": "LineString", "coordinates": [network.nodes[n] for n in route.nodes]}
            if len(route.nodes) >= 2 else None,
        }
    return result
