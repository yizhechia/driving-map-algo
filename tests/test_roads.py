"""Import semantics and an independent uncompressed-history route reference."""
from collections import defaultdict, deque
import json
import math
import random
import unittest
from unittest.mock import patch
from commute_map.osm import import_osm, RoadEdge, RoadNetwork
from commute_map.road_case import load_case, run_road_case
from commute_map.turn_routing import TurnRoutingIndex


def node(n, lon=None, lat=3.16, **tags):
    return {"type": "node", "id": n, "lon": 101.71 + n * .0001 if lon is None else lon,
            "lat": lat, "tags": tags}


def way(w, nodes, **tags):
    return {"type": "way", "id": w, "nodes": nodes,
            "tags": {"highway": "residential", **tags}}


def restriction(r, start, end, via, kind="no_right_turn", **tags):
    return {"type": "relation", "id": r, "members": [
        {"type": "way", "role": "from", "ref": start},
        *[{"type": typ, "role": "via", "ref": value} for typ, value in via],
        {"type": "way", "role": "to", "ref": end}],
        "tags": {"type": "restriction", "restriction": kind, **tags}}


def imported(elements):
    return import_osm({"elements": elements}, (3.15, 101.70, 3.17, 101.73))


def endpoints(graph):
    return {(e.source, e.target) for e in graph.edges}


def make_network(spec, forbidden=(), count=5):
    edges = tuple(RoadEdge(u, v, i, "residential", "", km, minutes)
                  for i, (u, v, minutes, km) in enumerate(spec))
    outgoing, incoming = defaultdict(list), defaultdict(list)
    for i, e in enumerate(edges):
        outgoing[e.source].append(i)
        incoming[e.target].append(i)
    return RoadNetwork({n: (101.71, 3.16) for n in range(count)}, edges,
                       dict(outgoing), dict(incoming), tuple(forbidden), {}, ())


def reference_cost(graph, source, target, beta):
    """Explicit finite history expansion, then Bellman-Ford (never reverses rules).

    Retain *every* recent edge up to max forbidden length minus one, without
    prefix compression. This is slower but independent of the production index.
    """
    depth = max(1, max(map(len, graph.forbidden), default=1) - 1)
    initial = (source, ())
    queue, states, transitions = deque([initial]), {initial}, []
    while queue:
        state = queue.popleft()
        current, history = state
        for eid in graph.outgoing.get(current, ()):
            edge = graph.edges[eid]
            if history:
                previous = graph.edges[history[-1]]
                if edge.source == previous.target and edge.target == previous.source:
                    continue
            extended = history + (eid,)
            if any(len(extended) >= len(p) and extended[-len(p):] == p for p in graph.forbidden):
                continue
            nxt = (edge.target, extended[-depth:])
            transitions.append((state, nxt, edge.minutes + beta * edge.km))
            if nxt not in states:
                states.add(nxt)
                queue.append(nxt)
    distance = {initial: 0.0}
    for _ in range(len(states) - 1):
        changed = False
        for a, b, weight in transitions:
            proposed = distance.get(a, math.inf) + weight
            if proposed < distance.get(b, math.inf):
                distance[b] = proposed
                changed = True
        if not changed:
            break
    return min((v for (n, _), v in distance.items() if n == target), default=math.inf)


class ImportTests(unittest.TestCase):
    def test_forward_reverse_and_explicit_two_way(self):
        g = imported([node(n) for n in range(1, 5)] + [
            way(10, [1, 2], oneway="yes"), way(11, [2, 3], oneway="-1"),
            way(12, [3, 4], highway="motorway", oneway="no")])
        self.assertEqual(endpoints(g), {(1, 2), (3, 2), (3, 4), (4, 3)})

    def test_implied_oneway_and_link_not_implied(self):
        g = imported([node(n) for n in range(1, 5)] + [
            way(10, [1, 2], junction="roundabout"), way(11, [2, 3], highway="motorway"),
            way(12, [3, 4], highway="motorway_link")])
        self.assertEqual(endpoints(g), {(1, 2), (2, 3), (3, 4), (4, 3)})

    def test_mode_specific_access_overrides_general(self):
        g = imported([node(n) for n in range(1, 5)] + [
            way(10, [1, 2], access="private", motorcar="yes"),
            way(11, [2, 3], access="yes", motor_vehicle="no"),
            way(12, [3, 4], access="destination")])
        self.assertEqual(endpoints(g), {(1, 2), (2, 1)})
        self.assertEqual(g.audit["rejected_ways"]["restricted_access"], 2)

    def test_conditional_rules_and_unverified_barriers_are_closed(self):
        g = imported([node(1), node(2, barrier="gate"), node(3), node(4)] + [
            way(10, [1, 2, 3]), way(11, [3, 4], **{"oneway:conditional": "yes @ (Mo-Fr)"}),
            way(12, [1, 4], **{"motorcar:conditional": "yes @ (08:00-09:00)"})])
        self.assertEqual(len(g.edges), 0)
        self.assertEqual(g.audit["rejected_nodes"]["unverified_barrier"], 1)

    def test_barrier_explicit_access_and_mode_oneway(self):
        g = imported([node(1), node(2, barrier="gate", motorcar="yes")] + [
            way(10, [1, 2], oneway="yes", **{"oneway:motorcar": "no"})])
        self.assertEqual(endpoints(g), {(1, 2), (2, 1)})

    def test_non_driving_areas_and_unknown_oneway(self):
        g = imported([node(n) for n in range(1, 5)] + [
            way(10, [1, 2], highway="footway"), way(11, [2, 3], area="yes"),
            way(12, [3, 4], oneway="reversible")])
        self.assertEqual(len(g.edges), 0)
        self.assertEqual(sum(g.audit["rejected_ways"].values()), 3)

    def test_bounds_missing_node_and_separate_ids(self):
        g = imported([node(1), node(2), node(3, lon=101.7102), node(4),
                      node(5, lon=102)] + [way(10, [1, 2]), way(11, [3, 4, 5, 99])])
        self.assertEqual(g.nodes[2], g.nodes[3])
        self.assertEqual(TurnRoutingIndex(g, 1, "work_to_home").route(4).status, "no_route")
        self.assertNotIn(5, g.nodes)
        self.assertEqual(g.audit["segments_omitted_at_bounds_missing_or_blocked_nodes"], 2)

    def test_via_node_prohibition_applies_in_both_directions(self):
        g = imported([node(n) for n in range(1, 5)] + [
            way(10, [1, 2], oneway="yes"), way(11, [2, 3], oneway="yes"),
            way(12, [2, 4, 3], oneway="yes"),
            restriction(100, 10, 11, [("node", 2)])])
        for anchor, direction, probe in [(1, "work_to_home", 3), (3, "home_to_work", 1)]:
            self.assertEqual(TurnRoutingIndex(g, anchor, direction).route(probe).nodes, (1, 2, 4, 3))

    def test_only_turn_blocks_every_alternative(self):
        g = imported([node(n) for n in range(1, 5)] + [
            way(10, [1, 2], oneway="yes"), way(11, [2, 3], oneway="yes"),
            way(12, [2, 4], oneway="yes"),
            restriction(100, 10, 11, [("node", 2)], "only_right_turn")])
        idx = TurnRoutingIndex(g, 1, "work_to_home")
        self.assertEqual(idx.route(3).nodes, (1, 2, 3))
        self.assertEqual(idx.route(4).status, "no_route")

    def test_via_way_no_rule_remembers_full_path_but_allows_early_exit(self):
        elements = [node(n) for n in range(1, 7)] + [
            way(10, [1, 2], oneway="yes"), way(11, [2, 3, 4], oneway="yes"),
            way(12, [4, 5], oneway="yes"), way(13, [3, 6], oneway="yes"),
            restriction(100, 10, 12, [("way", 11)])]
        g = imported(elements)
        idx = TurnRoutingIndex(g, 1, "work_to_home")
        self.assertEqual(idx.route(5).status, "no_route")
        self.assertEqual(idx.route(6).status, "ok")
        self.assertEqual(TurnRoutingIndex(g, 2, "work_to_home").route(5).status, "ok")
        self.assertEqual(TurnRoutingIndex(g, 5, "home_to_work").route(1).status, "no_route")

    def test_only_via_chain_blocks_premature_exit_and_wrong_final_turn(self):
        g = imported([node(n) for n in range(1, 8)] + [
            way(10, [1, 2], oneway="yes"), way(11, [2, 3], oneway="yes"),
            way(12, [3, 4], oneway="yes"), way(13, [4, 5], oneway="yes"),
            way(14, [3, 6], oneway="yes"), way(15, [4, 7], oneway="yes"),
            restriction(100, 10, 13, [("way", 11), ("way", 12)], "only_straight_on")])
        idx = TurnRoutingIndex(g, 1, "work_to_home")
        self.assertEqual(idx.route(5).status, "ok")
        self.assertEqual(idx.route(6).status, "no_route")
        self.assertEqual(idx.route(7).status, "no_route")
        self.assertEqual(TurnRoutingIndex(g, 6, "home_to_work").route(1).status, "no_route")

    def test_same_way_u_turn_does_not_ban_straight_continuation(self):
        g = imported([node(n) for n in range(1, 4)] + [way(10, [1, 2, 3]),
            restriction(100, 10, 10, [("node", 2)], "no_u_turn")])
        self.assertEqual(g.audit["restriction_status"], {"compiled": 1})
        self.assertEqual(TurnRoutingIndex(g, 1, "work_to_home").route(3).nodes, (1, 2, 3))

    def test_incomplete_or_conditional_relation_closes_approach(self):
        for rel in [restriction(100, 10, 999, [("node", 2)]),
                    restriction(100, 10, 11, [("node", 2)], **{"restriction:conditional": "no_right_turn @ (Mo-Fr)"})]:
            g = imported([node(n) for n in range(1, 4)] + [way(10, [1, 2]), way(11, [2, 3]), rel])
            self.assertEqual(g.audit["fallback_closed_ways"], [10])
            self.assertTrue(all(e.way != 10 for e in g.edges))

    def test_motorcar_exception_does_not_apply_rule(self):
        g = imported([node(n) for n in range(1, 4)] + [way(10, [1, 2]), way(11, [2, 3]),
            restriction(100, 10, 11, [("node", 2)], **{"except": "bus;motorcar"})])
        self.assertEqual(g.audit["restriction_status"], {"excepted": 1})
        self.assertEqual(TurnRoutingIndex(g, 1, "work_to_home").route(3).status, "ok")

    def test_invalid_coordinates_and_incomplete_response_rejected(self):
        with self.assertRaises(ValueError):
            imported([node(1, lon=float("nan"))])
        with self.assertRaises(ValueError):
            import_osm({"elements": [], "remark": "timed out"}, (3.15, 101.70, 3.17, 101.73))


class HistoryRoutingTests(unittest.TestCase):
    def test_buffer_changes_chosen_path(self):
        g = make_network([(0, 1, 1, 10), (1, 2, 1, 10), (0, 2, 4, 1)], count=3)
        self.assertEqual(TurnRoutingIndex(g, 0, "work_to_home", 0).route(2).nodes, (0, 1, 2))
        self.assertEqual(TurnRoutingIndex(g, 0, "work_to_home", 1).route(2).nodes, (0, 2))

    def test_overlapping_prefixes_do_not_forget_shorter_prohibition(self):
        g = make_network([(0, 1, 1, 1), (1, 2, 1, 1), (2, 3, 1, 1), (3, 4, 1, 1)],
                         forbidden=((0, 1, 2, 3), (1, 2)))
        idx = TurnRoutingIndex(g, 0, "work_to_home")
        self.assertEqual(idx.route(2).status, "ok")
        self.assertEqual(idx.route(3).status, "no_route")

    def test_immediate_reversal_cannot_reset_restriction_history(self):
        g = make_network([(0, 1, 1, 1), (1, 2, 1, 1), (2, 1, 1, 1), (1, 3, 1, 1)],
                         forbidden=((0, 3),))
        self.assertEqual(TurnRoutingIndex(g, 0, "work_to_home").route(3).status, "no_route")

    def test_invalid_cost_direction_and_endpoint(self):
        g = make_network([(0, 1, -1, 10)])
        with self.assertRaises(ValueError):
            TurnRoutingIndex(g, 0)
        g = make_network([(0, 1, 1, 1)])
        for options in [{"direction": "bad"}, {"buffer_min_per_km": float("inf")}, {"anchor": 99}]:
            with self.assertRaises(ValueError):
                TurnRoutingIndex(g, **{"anchor": 0, **options})
        with self.assertRaises(ValueError):
            TurnRoutingIndex(g, 0).route(99)

    def test_seeded_graphs_match_independent_full_history_bellman_ford(self):
        for seed in range(24):
            rng = random.Random(seed)
            spec = [(a, b, rng.randrange(5), rng.randrange(4))
                    for a in range(5) for b in range(5) if a != b and rng.random() < .38]
            g = make_network(spec)
            patterns = []
            for _ in range(5):
                current, pattern = rng.randrange(5), []
                for _ in range(rng.randrange(2, 5)):
                    available = g.outgoing.get(current, [])
                    if not available:
                        break
                    eid = rng.choice(available)
                    pattern.append(eid)
                    current = g.edges[eid].target
                if len(pattern) >= 2:
                    patterns.append(tuple(pattern))
            g.forbidden = tuple(patterns)
            beta = rng.choice([0, .2, 1])
            for direction in ("home_to_work", "work_to_home"):
                index = TurnRoutingIndex(g, 0, direction, beta)
                for probe in range(5):
                    start, end = (probe, 0) if direction == "home_to_work" else (0, probe)
                    expected = reference_cost(g, start, end, beta)
                    route = index.route(probe)
                    with self.subTest(seed=seed, direction=direction, probe=probe):
                        if math.isinf(expected):
                            self.assertEqual(route.status, "no_route")
                        else:
                            self.assertAlmostEqual(route.planning_minutes, expected, places=9)
                            self.assertEqual((route.nodes[0], route.nodes[-1]), (start, end))
                            for p in patterns:
                                self.assertFalse(any(route.edges[i:i + len(p)] == p
                                                     for i in range(len(route.edges) - len(p) + 1)))


class FrozenCaseTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.graph, cls.source = load_case()

    def test_snapshot_counts_and_anchor_identity(self):
        self.assertEqual(len(self.graph.nodes), 12645)
        self.assertEqual(len(self.graph.edges), 20106)
        self.assertEqual(self.graph.nodes[self.source["anchor_node"]], (101.712888, 3.1589231))
        self.assertEqual(self.graph.audit["restriction_status"], {"compiled": 291, "fallback": 51})

    def test_sampled_reconstructed_routes_are_contiguous_legal_and_costed(self):
        for direction in ("home_to_work", "work_to_home"):
            index = TurnRoutingIndex(self.graph, self.source["anchor_node"], direction)
            # Deterministic spread across the entire extract, including no-route nodes.
            for probe in list(self.graph.nodes)[::29]:
                route = index.route(probe)
                if route.status != "ok":
                    self.assertNotIn(probe, index.distance)
                    continue
                self.assertAlmostEqual(route.planning_minutes, index.distance[probe], places=9)
                sequence = route.edges
                for a, b in zip(sequence, sequence[1:]):
                    self.assertEqual(self.graph.edges[a].target, self.graph.edges[b].source)
                    self.assertNotEqual(self.graph.edges[a].source, self.graph.edges[b].target)
                for pattern in self.graph.forbidden:
                    self.assertFalse(any(sequence[i:i + len(pattern)] == pattern
                                         for i in range(len(sequence) - len(pattern) + 1)))

    def test_geojson_has_no_route_nulls_threshold_equality_and_provenance(self):
        with patch("commute_map.road_case.load_case", return_value=(self.graph, self.source)):
            result = run_road_case(threshold=0, probe=self.source["anchor_node"])
        counts = result["metadata"]["counts"]
        self.assertEqual(sum(counts.values()), len(self.graph.nodes))
        anchor = next(f for f in result["features"] if f["properties"]["osm_node"] == self.source["anchor_node"])
        self.assertEqual(anchor["properties"]["status"], "inside")
        self.assertTrue(any(f["properties"]["planning_minutes"] is None for f in result["features"]))
        self.assertFalse(result["metadata"]["traffic_data"])
        self.assertEqual(result["metadata"]["source"]["license"], "ODbL 1.0")
        self.assertIsNone(result["route"]["geometry"])
        json.dumps(result, allow_nan=False)

    def test_checksum_tampering_is_rejected(self):
        with patch("pathlib.Path.read_bytes", return_value=b"damaged snapshot"):
            with self.assertRaisesRegex(ValueError, "checksum"):
                load_case()


if __name__ == "__main__":
    unittest.main()
