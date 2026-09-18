"""Fixed, additive costs. These assumptions are not probability estimates."""
from dataclasses import dataclass, field
import math


def nonnegative(value, name):
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"{name} must be a number")
    try:
        value = float(value)
    except OverflowError as error:
        raise ValueError(f"{name} must be a finite number") from error
    if not math.isfinite(value) or value < 0:
        raise ValueError(f"{name} must be finite and nonnegative")
    return value


@dataclass(frozen=True)
class Policy:
    period: str = "example"
    buffer_min_per_km: float = 0.2
    condo_minutes: float = 5.0

    def __post_init__(self):
        if self.period not in ("example", "morning", "evening"):
            raise ValueError("period must be example, morning, or evening")
        nonnegative(self.buffer_min_per_km, "buffer_min_per_km")
        nonnegative(self.condo_minutes, "condo_minutes")


@dataclass(frozen=True)
class Node:
    id: str
    x: float
    y: float
    name: str = ""
    area: str = ""
    condo: bool = False
    home: bool = False

    def __post_init__(self):
        if not isinstance(self.id, str) or not self.id:
            raise ValueError("node id must be a nonempty string")
        if not all(isinstance(v, (int, float)) and not isinstance(v, bool)
                   and math.isfinite(v) for v in (self.x, self.y)):
            raise ValueError("node coordinates must be finite numbers")


@dataclass(frozen=True)
class Edge:
    source: str
    target: str
    minutes: float
    km: float
    kind: str = "local"
    morning_factor: float = 1.0
    evening_factor: float = 1.0

    def __post_init__(self):
        for key in ("minutes", "km", "morning_factor", "evening_factor"):
            nonnegative(getattr(self, key), key)
        if self.kind not in ("local", "corridor"):
            raise ValueError("edge kind must be local or corridor")

    def time(self, policy):
        factor = {"example": 1, "morning": self.morning_factor,
                  "evening": self.evening_factor}[policy.period]
        result = self.minutes * factor
        return nonnegative(result, "effective edge time")

    def cost(self, policy):
        return nonnegative(self.time(policy) + self.km * policy.buffer_min_per_km,
                           "effective edge cost")


@dataclass
class Graph:
    nodes: dict = field(default_factory=dict)
    edges: list = field(default_factory=list)
    outgoing: dict = field(default_factory=dict)
    incoming: dict = field(default_factory=dict)

    def add_node(self, node):
        if node.id in self.nodes:
            raise ValueError(f"duplicate node: {node.id}")
        self.nodes[node.id] = node
        self.outgoing[node.id] = []
        self.incoming[node.id] = []

    def add_edge(self, edge):
        if edge.source not in self.nodes or edge.target not in self.nodes:
            raise ValueError("both edge endpoints must exist")
        self.edges.append(edge)
        self.outgoing[edge.source].append(edge)
        self.incoming[edge.target].append(edge)
