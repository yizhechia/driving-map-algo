"""One Dijkstra search per workplace and policy, with path reconstruction."""
from dataclasses import dataclass
import heapq
from .model import nonnegative

@dataclass(frozen=True)
class Route:
    status: str
    nodes: tuple = ()
    corridor_minutes: float = 0
    local_minutes: float = 0
    access_minutes: float = 0
    buffer_minutes: float = 0
    distance_km: float = 0
    @property
    def planning_minutes(self):
        if self.status != "ok":
            return None
        return (self.corridor_minutes + self.local_minutes
                + self.access_minutes + self.buffer_minutes)

def classify(route, threshold):
    nonnegative(threshold, "threshold")
    if route.status != "ok":
        return route.status
    return "inside" if route.planning_minutes <= threshold else "outside"

class RoutingIndex:
    """Fixed nonnegative costs. Private homes are endpoints, never shortcuts."""
    def __init__(self, graph, workplace, direction, policy):
        if workplace not in graph.nodes:
            raise ValueError("unknown workplace")
        if graph.nodes[workplace].home:
            raise ValueError("workplace cannot be a home access endpoint")
        if direction not in ("home_to_work", "work_to_home"):
            raise ValueError("invalid direction")
        self.graph, self.workplace = graph, workplace
        self.direction, self.policy = direction, policy
        self.reverse = direction == "home_to_work"
        self.distance, self.link = {workplace: 0.0}, {}
        self.relaxations = 0
        queue = [(0.0, workplace)]
        for edge in graph.edges:
            edge.cost(policy)
        while queue:
            cost, node = heapq.heappop(queue)
            if cost != self.distance[node]:
                continue
            if graph.nodes[node].home:
                continue
            edges = graph.incoming[node] if self.reverse else graph.outgoing[node]
            for edge in edges:
                self.relaxations += 1
                neighbor = edge.source if self.reverse else edge.target
                candidate = cost + edge.cost(policy)
                nonnegative(candidate, "path cost")
                if candidate < self.distance.get(neighbor, float("inf")):
                    self.distance[neighbor] = candidate
                    self.link[neighbor] = edge
                    heapq.heappush(queue, (candidate, neighbor))

    def route(self, home):
        if home not in self.graph.nodes or not self.graph.nodes[home].home:
            raise ValueError("unknown home access point")
        if home not in self.distance:
            return Route("no_route")
        edges, node = [], home
        while node != self.workplace:
            edge = self.link[node]
            edges.append(edge)
            node = edge.target if self.reverse else edge.source
        if not self.reverse:
            edges.reverse()
        nodes = (edges[0].source,) + tuple(e.target for e in edges)
        corridor = sum(e.time(self.policy) for e in edges if e.kind == "corridor")
        local = sum(e.time(self.policy) for e in edges if e.kind == "local")
        km = sum(e.km for e in edges)
        access = self.policy.condo_minutes if self.graph.nodes[home].condo else 0
        return Route("ok", nodes, corridor, local, access,
                     km * self.policy.buffer_min_per_km, km)
