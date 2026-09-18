"""Conservative passenger-car graph import for a bounded offline OSM case.

This is deliberately a subset of OSM routing semantics, not a navigation engine.
Unknown rules close affected ways instead of silently allowing a manoeuvre.
"""
from collections import Counter, defaultdict
from dataclasses import dataclass
import math


# Experiment assumptions, NOT measured speeds or interpreted legal speed limits.
SPEED_KPH = {
    "motorway": 60, "motorway_link": 30, "trunk": 50, "trunk_link": 25,
    "primary": 40, "primary_link": 25, "secondary": 35, "secondary_link": 20,
    "tertiary": 30, "tertiary_link": 20, "unclassified": 25,
    "residential": 25, "living_street": 10, "service": 15,
}
ACCESS_KEYS = ("motorcar", "motor_vehicle", "vehicle", "access")
PERMITTED = {"yes", "permissive", "designated"}
RESTRICTIONS = {
    "no_left_turn", "no_right_turn", "no_straight_on", "no_u_turn",
    "no_entry", "no_exit", "only_left_turn", "only_right_turn",
    "only_straight_on", "only_u_turn",
}


@dataclass(frozen=True)
class RoadEdge:
    source: int
    target: int
    way: int
    highway: str
    name: str
    km: float
    minutes: float


@dataclass
class RoadNetwork:
    nodes: dict
    edges: tuple
    outgoing: dict
    incoming: dict
    forbidden: tuple
    audit: dict
    bounds: tuple


def distance_km(a, b):
    """Great-circle segment distance, coordinates (longitude, latitude)."""
    lon1, lat1, lon2, lat2 = map(math.radians, (*a, *b))
    h = (math.sin((lat2 - lat1) / 2) ** 2
         + math.cos(lat1) * math.cos(lat2) * math.sin((lon2 - lon1) / 2) ** 2)
    return 6371.0088 * 2 * math.asin(min(1.0, math.sqrt(h)))


def access_reason(tags, node=False):
    # Directional, lane-specific and conditional access need a richer model.
    if any(key.startswith(tuple(k + ":" for k in ACCESS_KEYS)) for key in tags):
        return "unsupported_access_rule"
    access = next((tags[k] for k in ACCESS_KEYS if k in tags), None)
    if access is not None and access not in PERMITTED:
        return "restricted_access"
    if node and "barrier" in tags:
        # Never infer an unlocked gate. Even an explicitly open height barrier
        # needs vehicle dimensions, so only a small barrier subset is accepted.
        if tags["barrier"] not in {"gate", "lift_gate", "swing_gate", "sliding_gate"}:
            return "unsupported_barrier"
        if access not in PERMITTED:
            return "unverified_barrier"
    return None


def way_direction(tags):
    keys = ("oneway:motorcar", "oneway:motor_vehicle", "oneway:vehicle", "oneway")
    if any(k.startswith("oneway") and k.endswith(":conditional") for k in tags):
        raise ValueError("conditional_oneway")
    value = next((tags[k] for k in keys if k in tags), None)
    if value is None:
        return 1 if tags.get("junction") == "roundabout" or tags.get("highway") == "motorway" else 0
    if value in {"yes", "1", "true"}:
        return 1
    if value in {"no", "0", "false"}:
        return 0
    if value == "-1":
        return -1
    raise ValueError("unsupported_oneway")


def _restriction_sequences(relation, ways, edges, by_way, lookup):
    """Return exact directed segment sequences for an unambiguous relation."""
    tags = relation.get("tags", {})
    if tags.get("type") != "restriction" or any(":conditional" in k for k in tags):
        raise ValueError("unsupported_restriction_rule")
    exceptions = {part.strip() for part in tags.get("except", "").split(";")}
    if exceptions & {"motorcar", "motor_vehicle", "vehicle"}:
        return "excepted", []
    kind = next((tags[k] for k in ("restriction:motorcar", "restriction:motor_vehicle",
                                 "restriction:vehicle", "restriction") if k in tags), None)
    if kind not in RESTRICTIONS:
        raise ValueError("unsupported_restriction_kind")
    members = relation.get("members", [])
    roles = {role: [m for m in members if m.get("role") == role] for role in ("from", "via", "to")}
    if (len(roles["from"]) != 1 or len(roles["to"]) != 1
            or any(m.get("role") not in roles for m in members)
            or roles["from"][0].get("type") != "way" or roles["to"][0].get("type") != "way"):
        raise ValueError("malformed_members")
    start, end = roles["from"][0]["ref"], roles["to"][0]["ref"]
    via = roles["via"]
    if start not in ways or end not in ways:
        raise ValueError("missing_member_way")
    middle = []
    if len(via) == 1 and via[0].get("type") == "node":
        entry = exit_node = via[0]["ref"]
    elif via and all(m.get("type") == "way" for m in via):
        chain = [start] + [m["ref"] for m in via] + [end]
        if any(w not in ways for w in chain):
            raise ValueError("missing_member_way")
        joins = []
        for a, b in zip(chain, chain[1:]):
            shared = set(ways[a]["nodes"]) & set(ways[b]["nodes"])
            if len(shared) != 1:
                raise ValueError("ambiguous_via_connection")
            joins.append(next(iter(shared)))
        entry, exit_node = joins[0], joins[-1]
        for way, a, b in zip(chain[1:-1], joins, joins[1:]):
            nodes = ways[way]["nodes"]
            if a == b or nodes.count(a) != 1 or nodes.count(b) != 1:
                raise ValueError("ambiguous_via_path")
            i, j = nodes.index(a), nodes.index(b)
            step = 1 if j > i else -1
            segment_nodes = [nodes[k] for k in range(i, j + step, step)]
            for u, v in zip(segment_nodes, segment_nodes[1:]):
                found = lookup.get((way, u, v), [])
                if len(found) != 1:
                    raise ValueError("unavailable_via_segment")
                middle.append(found[0])
    else:
        raise ValueError("unsupported_via_members")
    incoming = [i for i in by_way.get(start, []) if edges[i].target == entry]
    outgoing = [i for i in by_way.get(end, []) if edges[i].source == exit_node]
    if not incoming or not outgoing:
        raise ValueError("unavailable_approach_or_exit")
    if start == end and not middle and kind in {"no_u_turn", "only_u_turn"}:
        pairs = [(a, b) for a in incoming for b in outgoing if edges[a].source == edges[b].target]
    else:
        # Internal-node or multiply connected members do not establish a unique
        # approach/exit direction. Close the approach instead of guessing angles.
        if len(incoming) != 1 or len(outgoing) != 1:
            raise ValueError("ambiguous_approach_or_exit")
        pairs = [(incoming[0], outgoing[0])]
    sequences = [tuple([a] + middle + [b]) for a, b in pairs]
    if not sequences or any(len(s) > 128 for s in sequences):
        raise ValueError("unsupported_restriction_length")
    return kind, sequences


def import_osm(payload, bounds):
    """Keep road segments whose two endpoints lie inside S,W,N,E bounds.

    Identities, not geometric intersections or proximity, create connections.
    No-route therefore means no route in this conservative, clipped model.
    """
    south, west, north, east = bounds
    if not (-90 <= south < north <= 90 and -180 <= west < east <= 180):
        raise ValueError("invalid study bounds")
    if payload.get("remark"):
        raise ValueError("Overpass returned an incomplete/error response")
    elements = payload["elements"]
    raw_nodes = {x["id"]: x for x in elements if x["type"] == "node"}
    ways = {x["id"]: x for x in elements if x["type"] == "way"}
    relations = [x for x in elements if x["type"] == "relation"]
    nodes, node_rejected = {}, Counter()
    for nid, n in sorted(raw_nodes.items()):
        lon, lat = n["lon"], n["lat"]
        if not all(isinstance(x, (float, int)) and not isinstance(x, bool) and math.isfinite(x)
                   for x in (lon, lat)) or not (-180 <= lon <= 180 and -90 <= lat <= 90):
            raise ValueError("invalid node coordinates")
        reason = access_reason(n.get("tags", {}), node=True)
        if reason:
            node_rejected[reason] += 1
        elif south <= lat <= north and west <= lon <= east:
            nodes[nid] = (lon, lat)
    edges, rejected, clipped = [], Counter(), 0
    by_way, lookup, outgoing, incoming = (defaultdict(list) for _ in range(4))
    for wid, way in sorted(ways.items()):
        tags = way.get("tags", {})
        highway = tags.get("highway")
        reason = "non_driving_class" if highway not in SPEED_KPH else access_reason(tags)
        if not reason and tags.get("area") == "yes":
            reason = "area_way"
        try:
            direction = way_direction(tags) if not reason else 0
        except ValueError as error:
            reason = str(error)
        if reason:
            rejected[reason] += 1
            continue
        for u, v in zip(way["nodes"], way["nodes"][1:]):
            if u not in nodes or v not in nodes or u == v:
                clipped += 1
                continue
            km = distance_km(nodes[u], nodes[v])
            pairs = [(u, v)] if direction == 1 else [(v, u)] if direction == -1 else [(u, v), (v, u)]
            for a, b in pairs:
                i = len(edges)
                edges.append(RoadEdge(a, b, wid, highway, tags.get("name", ""), km, km * 60 / SPEED_KPH[highway]))
                by_way[wid].append(i)
                lookup[wid, a, b].append(i)
                outgoing[a].append(i)
                incoming[b].append(i)
    forbidden, closed_ways, restriction_audit = set(), set(), []
    for relation in sorted(relations, key=lambda r: r["id"]):
        if not relation.get("tags", {}).get("type", "").startswith("restriction"):
            continue
        entry = {"relation": relation["id"]}
        try:
            kind, sequences = _restriction_sequences(relation, ways, edges, by_way, lookup)
            entry.update(status="excepted" if kind == "excepted" else "compiled", kind=kind,
                         sequences=len(sequences))
            if kind.startswith("only_"):
                allowed = defaultdict(set)
                for sequence in sequences:
                    for length in range(1, len(sequence)):
                        allowed[sequence[:length]].add(sequence[length])
                for prefix, next_edges in allowed.items():
                    for candidate in outgoing[edges[prefix[-1]].target]:
                        if candidate not in next_edges:
                            forbidden.add(prefix + (candidate,))
            elif kind.startswith("no_"):
                forbidden.update(sequences)
        except ValueError as error:
            from_ways = {m["ref"] for m in relation.get("members", [])
                         if m.get("type") == "way" and m.get("role") == "from"}
            # A missing from-member leaves no identifiable approach: close every
            # known way member, a deliberately conservative fallback.
            affected = from_ways or {m["ref"] for m in relation.get("members", []) if m.get("type") == "way"}
            affected = sorted(affected & by_way.keys())
            closed_ways.update(affected)
            entry.update(status="fallback", reason=str(error), closed_ways=affected)
        restriction_audit.append(entry)
    # Reindex after all closures; patterns containing a removed edge are moot.
    retained = [i for i, edge in enumerate(edges) if edge.way not in closed_ways]
    remap = {old: new for new, old in enumerate(retained)}
    patterns = tuple(sorted({tuple(remap[i] for i in p) for p in forbidden if all(i in remap for i in p)}))
    kept = tuple(edges[i] for i in retained)
    outgoing, incoming = defaultdict(list), defaultdict(list)
    used_nodes = set()
    for i, edge in enumerate(kept):
        outgoing[edge.source].append(i)
        incoming[edge.target].append(i)
        used_nodes.update((edge.source, edge.target))
    nodes = {nid: nodes[nid] for nid in sorted(used_nodes)}
    audit = {
        "input_nodes": len(raw_nodes), "input_ways": len(ways),
        "rejected_ways": dict(sorted(rejected.items())),
        "rejected_nodes": dict(sorted(node_rejected.items())),
        "segments_omitted_at_bounds_missing_or_blocked_nodes": clipped,
        "restriction_relations": len(restriction_audit),
        "restriction_status": dict(Counter(r["status"] for r in restriction_audit)),
        "fallback_closed_ways": sorted(closed_ways),
        "fallback_removed_directed_segments": len(edges) - len(kept),
        "forbidden_sequences": len(patterns), "nodes": len(nodes),
        "directed_segments": len(kept), "restrictions": restriction_audit,
    }
    return RoadNetwork(nodes, kept, dict(outgoing), dict(incoming), patterns, audit, tuple(bounds))
