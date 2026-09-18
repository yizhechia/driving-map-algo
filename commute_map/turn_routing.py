"""Shortest paths with forbidden segment sequences, in either direction.

A state remembers the last edge and the longest suffix that is a proper prefix
of a forbidden sequence. Reversing every sequence permits exact inbound search
without incorrectly applying forward turn rules to backwards traversals.
"""
from dataclasses import dataclass
import heapq
from .model import nonnegative


class RestrictionMemory:
    def __init__(self, forbidden):
        self.forbidden = set(forbidden)
        self.prefixes = {p[:n] for p in forbidden for n in range(1, len(p))}
        self.lengths = sorted({len(p) for p in forbidden})
        self.max_prefix = max(map(len, self.prefixes), default=0)
        self.cache = {}

    def advance(self, history, edge):
        key = (history, edge)
        if key in self.cache:
            return self.cache[key]
        extended = history + (edge,)
        if any(len(extended) >= n and extended[-n:] in self.forbidden for n in self.lengths):
            answer = None
        else:
            answer = ()
            for length in range(min(self.max_prefix, len(extended)), 0, -1):
                if extended[-length:] in self.prefixes:
                    answer = extended[-length:]
                    break
        self.cache[key] = answer
        return answer


@dataclass(frozen=True)
class RoadRoute:
    status: str
    edges: tuple = ()
    nodes: tuple = ()
    road_minutes: float = 0
    distance_km: float = 0
    buffer_minutes: float = 0

    @property
    def planning_minutes(self):
        return self.road_minutes + self.buffer_minutes if self.status == "ok" else None


class TurnRoutingIndex:
    """One Dijkstra index for every road-node probe around one anchor.

    Immediate reversal of a segment is disallowed everywhere as an explicit
    conservative model assumption. Starting/ending at any road node imposes no
    heading or building access cost. Real driveways are a separate future input.
    """
    def __init__(self, network, anchor, direction="home_to_work", buffer_min_per_km=0.2):
        if anchor not in network.nodes:
            raise ValueError("anchor is not a retained road node")
        if direction not in {"home_to_work", "work_to_home"}:
            raise ValueError("invalid direction")
        self.beta = nonnegative(buffer_min_per_km, "buffer_min_per_km")
        self.network, self.anchor, self.direction = network, anchor, direction
        self.reverse = direction == "home_to_work"
        patterns = [p[::-1] if self.reverse else p for p in network.forbidden]
        memory = RestrictionMemory(patterns)
        self.costs = [nonnegative(nonnegative(e.minutes, "road minutes")
                                 + self.beta * nonnegative(e.km, "road km"), "road cost")
                      for e in network.edges]
        self.distance, self.best, self.links = {anchor: 0.0}, {}, {}
        initial = (-1, ())
        self.states = {initial: 0.0}
        self.best[anchor] = initial
        queue = [(0.0, initial)]
        self.relaxations = 0
        while queue:
            cost, state = heapq.heappop(queue)
            if cost != self.states[state]:
                continue
            last, history = state
            previous = network.edges[last] if last >= 0 else None
            node = anchor if previous is None else previous.source if self.reverse else previous.target
            candidates = network.incoming.get(node, ()) if self.reverse else network.outgoing.get(node, ())
            for eid in candidates:
                self.relaxations += 1
                edge = network.edges[eid]
                if previous and previous.source == edge.target and previous.target == edge.source:
                    continue
                next_history = memory.advance(history, eid)
                if next_history is None:
                    continue
                new_state = (eid, next_history)
                value = nonnegative(cost + self.costs[eid], "path cost")
                if value >= self.states.get(new_state, float("inf")):
                    continue
                self.states[new_state] = value
                self.links[new_state] = state
                neighbor = edge.source if self.reverse else edge.target
                if value < self.distance.get(neighbor, float("inf")):
                    self.distance[neighbor] = value
                    self.best[neighbor] = new_state
                heapq.heappush(queue, (value, new_state))

    def route(self, node):
        if node not in self.network.nodes:
            raise ValueError("unknown road node")
        if node not in self.best:
            return RoadRoute("no_route")
        ids, state = [], self.best[node]
        while state[0] != -1:
            ids.append(state[0])
            state = self.links[state]
        if not self.reverse:
            ids.reverse()
        edges = [self.network.edges[i] for i in ids]
        nodes = (edges[0].source,) + tuple(e.target for e in edges) if edges else (node,)
        km = sum(e.km for e in edges)
        return RoadRoute("ok", tuple(ids), nodes, sum(e.minutes for e in edges), km, self.beta * km)
