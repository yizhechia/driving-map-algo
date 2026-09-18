"""Synthetic KL-inspired fixture; no road or traffic measurements are implied."""
from dataclasses import dataclass
from .model import Edge, Graph, Node

@dataclass
class Scenario:
    graph: Graph
    cells: dict
    size: int
    examples: tuple
    workplace: str = "KLCC"

def build_scenario(size=32):
    if isinstance(size, bool) or size not in (16, 32, 64):
        raise ValueError("grid size must be 16, 32, or 64")
    graph = Graph()
    graph.add_node(Node("KLCC", 24, 20, "KLCC · example workplace"))
    # id, schematic coordinates, outbound/inbound minutes, invented road km
    gateways = [("SB", 10, 21, 30, 34, 24),
                ("RAWANG", 10, 29, 35, 39, 35),
                ("CHERAS", 25, 8, 22, 27, 16)]
    names = {"SB": "Sungai Buloh", "RAWANG": "Rawang", "CHERAS": "Cheras"}
    for key, x, y, outbound, inbound, km in gateways:
        graph.add_node(Node(key, x, y, names[key] + " · access gateway"))
        graph.add_edge(Edge("KLCC", key, outbound, km, "corridor", 1.05, 1.25))
        graph.add_edge(Edge(key, "KLCC", inbound, km, "corridor", 1.3, 1.05))

    def connect(home, gateway, local, km, inward=None):
        graph.add_edge(Edge(gateway, home, local, km, "local", 1.1, 1.2))
        graph.add_edge(Edge(home, gateway, local if inward is None else inward,
                            km, "local", 1.25, 1.05))

    fixtures = [
        ("SB_HOUSE", "Sungai Buloh · inner estate", "SB", 7, 23, 18, 6, False),
        ("RAWANG_HOUSE", "Rawang · near access", "RAWANG", 12, 30, 5, 3, False),
        ("CHERAS_HOUSE", "Cheras · inner estate", "CHERAS", 28, 5, 20, 5, False),
        ("CHERAS_CONDO", "Cheras · condo", "CHERAS", 24, 9, 4, 2, True),
    ]
    for key, name, gate, x, y, local, km, condo in fixtures:
        graph.add_node(Node(key, x, y, name, names[gate], condo, True))
        connect(key, gate, local, km)
    graph.add_node(Node("ALTERNATIVE", 12, 25, "Two possible entrances", "Sungai Buloh", False, True))
    connect("ALTERNATIVE", "SB", 20, 2)
    connect("ALTERNATIVE", "RAWANG", 5, 8)
    graph.add_node(Node("ISOLATED", 3, 3, "Unconnected access point", "Unknown", False, True))
    cells = {}
    for row in range(size):
        for col in range(size):
            x, y = (col + 0.5) * 32 / size, (row + 0.5) * 32 / size
            ranked = sorted(gateways, key=lambda g: (abs(x-g[1])+abs(y-g[2]), g[0]))
            gate = ranked[0][0]
            key = f"cell_{col}_{row}"
            condo = (int(x / 2) + int(y / 2)) % 7 == 0
            graph.add_node(Node(key, x, y, f"Access {col}, {row}", names[gate], condo, True))
            cells[col, row] = key
            if 15 <= x < 18 and 13 <= y < 16:
                continue
            for g in ranked[:2]:
                key_gate, gx, gy, *_ = g
                km = (abs(x-gx) + abs(y-gy)) * 1.15 + 0.3
                local = 2 + km * 1.25
                if key_gate == "SB" and x < 8 and 16 <= y <= 25:
                    local += 12
                    km += 3
                if key_gate == "CHERAS" and 20 <= x < 22 and 10 <= y < 12:
                    local = 2.0
                    km = 1.0
                connect(key, key_gate, local, km, local * (1.1 if x < 16 else 1.25))
    return Scenario(graph, cells, size, tuple(f[0] for f in fixtures) + ("ALTERNATIVE", "ISOLATED"))
