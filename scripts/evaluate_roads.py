"""Reproduce the frozen KLCC case; optional matplotlib figures for the report."""
import argparse
from collections import Counter
from dataclasses import replace
import json
from pathlib import Path
from commute_map.osm import distance_km, SPEED_KPH
from commute_map.road_case import load_case
from commute_map.turn_routing import TurnRoutingIndex


DEST = Path(__file__).resolve().parents[1] / "docs/evaluation"
# Exploratory nearby-node illustration, chosen after inspecting this extract.
# Not a held-out evaluation set or a pair of verified residential entrances.
PAIR = (1198144301, 293569258)
THRESHOLD = 10
BETA = .2


def evaluate():
    network, source = load_case()
    anchor = source["anchor_node"]
    summary = {"source": source, "threshold_minutes": THRESHOLD,
               "buffer_min_per_km": BETA, "assumed_speed_kph": SPEED_KPH,
               "audit": network.audit, "directions": {}}
    indices = {}
    for direction in ("home_to_work", "work_to_home"):
        index = TurnRoutingIndex(network, anchor, direction, BETA)
        indices[direction] = index
        # Same retained network, speeds, bounds and U-turn assumption. Disable
        # only compiled sequence restrictions to isolate their model effect.
        relaxed = TurnRoutingIndex(replace(network, forbidden=()), anchor, direction, BETA)
        common = index.distance.keys() & relaxed.distance.keys()
        increased = [n for n in common if index.distance[n] - relaxed.distance[n] > 1e-8]
        false_inside = [n for n in network.nodes if relaxed.distance.get(n, float("inf")) <= THRESHOLD
                        and index.distance.get(n, float("inf")) > THRESHOLD]
        summary["directions"][direction] = {
            "probes": len(network.nodes), "routable": len(index.distance),
            "inside": sum(v <= THRESHOLD for v in index.distance.values()),
            "outside": sum(v > THRESHOLD for v in index.distance.values()),
            "no_route_in_model": len(network.nodes) - len(index.distance),
            "index_states": len(index.states), "relaxations": index.relaxations,
            "restriction_ablation": {
                "cost_increased_for_routable_nodes": len(increased),
                "newly_unroutable_nodes": len(relaxed.distance.keys() - index.distance.keys()),
                "maximum_cost_increase_minutes": max((index.distance[n] - relaxed.distance[n] for n in common), default=0),
                "wrongly_inside_if_compiled_restrictions_disabled": len(false_inside),
            },
        }
    summary["fallback_reasons"] = dict(sorted(Counter(
        r["reason"] for r in network.audit["restrictions"] if r["status"] == "fallback").items()))
    summary["nearby_illustration"] = {
        "selection": "Exploratory maximum inbound time gap among non-motorway/trunk road nodes routable in both directions and separated by 20–80 m; not held out.",
        "separation_metres": distance_km(*(network.nodes[n] for n in PAIR)) * 1000,
        "points": [],
    }
    for n in PAIR:
        point = {"osm_node": n, "coordinates": network.nodes[n], "routes": {}}
        for direction, index in indices.items():
            route = index.route(n)
            point["routes"][direction] = {
                "planning_minutes": route.planning_minutes, "road_minutes": route.road_minutes,
                "buffer_minutes": route.buffer_minutes, "distance_km": route.distance_km,
                "osm_nodes": route.nodes,
                "osm_way_ids": [network.edges[e].way for e in route.edges],
            }
        summary["nearby_illustration"]["points"].append(point)
    DEST.mkdir(parents=True, exist_ok=True)
    (DEST / "KLCC_RESULTS.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False, allow_nan=False) + "\n", encoding="utf-8")
    return network, source, indices, summary


def plot(network, source, indices, summary):
    # Plotting is optional. Runtime routing and JSON evaluation use only stdlib.
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.collections import LineCollection
    from matplotlib.lines import Line2D
    from matplotlib.colors import Normalize
    import math

    origin = (101.701, 3.149)
    def xy(lonlat):
        lon, lat = lonlat
        return ((lon - origin[0]) * 111.195 * math.cos(math.radians(3.16)),
                (lat - origin[1]) * 111.195)
    coordinates = {n: xy(c) for n, c in network.nodes.items()}
    seen, segments = set(), []
    for e in network.edges:
        key = (e.way, min(e.source, e.target), max(e.source, e.target))
        if key not in seen:
            segments.append([coordinates[e.source], coordinates[e.target]])
            seen.add(key)
    anchor = source["anchor_node"]
    plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 10,
                         "axes.titleweight": "bold", "axes.spines.top": False,
                         "axes.spines.right": False})
    def backdrop(ax):
        ax.set_facecolor("#f7f8f5")
        ax.add_collection(LineCollection(segments, colors="#c8cdc8", linewidths=.45, zorder=1))
        ax.set_aspect("equal")
        ax.set_xlim(0, 3.67)
        ax.set_ylim(0, 3.003)
        ax.set_xlabel("East of study boundary (km)")
        ax.set_ylabel("North of study boundary (km)")
        ax.scatter(*coordinates[anchor], marker="*", s=220, color="#161f2e", edgecolor="white", linewidth=1, zorder=6)

    fig, axes = plt.subplots(1, 2, figsize=(13, 7.6))
    fig.patch.set_facecolor("white")
    fig.subplots_adjust(left=.07, right=.90, top=.80, bottom=.28, wspace=.20)
    norm = Normalize(0, THRESHOLD)
    cmap = plt.get_cmap("viridis").copy()
    cmap.set_over("#d85557")
    for ax, (direction, index) in zip(axes, indices.items()):
        backdrop(ax)
        missing = [coordinates[n] for n in network.nodes if n not in index.distance]
        ax.scatter(*zip(*missing), s=2.5, color="#c1c4c2", linewidth=0, zorder=2)
        finite = list(index.distance)
        scatter = ax.scatter(*zip(*(coordinates[n] for n in finite)), s=4,
                             c=[index.distance[n] for n in finite], cmap=cmap, norm=norm,
                             linewidth=0, zorder=3)
        title = "Road node → KLCC anchor" if direction == "home_to_work" else "KLCC anchor → road node"
        ax.set_title(title, loc="left", pad=13, fontsize=13)
        stats = summary["directions"][direction]
        fig.text(ax.get_position().x0, .185, f"{stats['inside']:,} nodes within 10 min · {stats['outside']:,} above\n"
                f"{stats['no_route_in_model']:,} with no route in this bounded model",
                va="top", fontsize=10, linespacing=1.6)
    cax = fig.add_axes([.92, .33, .015, .37])
    bar = fig.colorbar(scatter, cax=cax, extend="max")
    bar.set_label("Assumed planning minutes", labelpad=9)
    fig.text(.07, .94, "KLCC · direction changes accessibility", fontsize=22, weight="bold", color="#172333")
    fig.text(.07, .885, "Real OSM road geometry · fixed assumed speeds + 0.2 min/km · no live traffic", fontsize=12, color="#475568")
    fig.text(.07, .085, "★ Jalan Ampang road-node anchor; workplace entrance unverified. Grey = no route in this model.\n"
             "Road nodes are not homes or land-area samples. Extract limits and conservative closures can omit valid detours.",
             fontsize=10, color="#475568", linespacing=1.7, va="top")
    fig.text(.07, .016, "© OpenStreetMap contributors · openstreetmap.org/copyright · ODbL 1.0 · snapshot " + source["osm_base_timestamp"], fontsize=8.5, color="#647080")
    fig.savefig(DEST / "klcc-accessibility.png", dpi=160)
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(10, 8.5))
    fig.subplots_adjust(left=.10, right=.97, top=.78, bottom=.25)
    backdrop(ax)
    colors = ["#00887c", "#e66122"]
    labels = []
    for name, n, color in reversed(list(zip(("A", "B"), PAIR, colors))):
        route = indices["home_to_work"].route(n)
        path = [coordinates[node] for node in route.nodes]
        ax.plot(*zip(*path), color=color, linewidth=2.7, alpha=.9, zorder=4)
        ax.scatter(*coordinates[n], s=72, color=color, edgecolor="white", zorder=6)
        offset = (12, -23) if name == "A" else (-35, 20)
        ax.annotate(name, coordinates[n], xytext=offset, textcoords="offset points", fontsize=12,
                    weight="bold", color=color, arrowprops={"arrowstyle": "-", "color": color})
        labels.insert(0, Line2D([0], [0], color=color, lw=3,
                             label=f"{name}: {route.planning_minutes:.2f} min · {route.distance_km:.2f} km routed"))
    ax.legend(handles=labels, loc="upper left", framealpha=.96, fontsize=11)
    fig.text(.10, .94, "Nearby roads can require very different routes", fontsize=19, weight="bold", color="#172333")
    gap = summary["nearby_illustration"]["separation_metres"]
    fig.text(.10, .89, f"Two road nodes {gap:.1f} m apart near Jalan Tun Razak · both travelling to the KLCC anchor", fontsize=11, color="#475568")
    fig.text(.10, .105, "Exploratory illustration selected from this model; neither point is a verified home entrance.\n"
             "One-way streets, mapped turn rules, assumed speeds, closures and the study boundary all affect these paths.\n"
             "These are static model durations, not observed journeys or navigation instructions.",
             fontsize=10, color="#475568", linespacing=1.7)
    fig.text(.10, .025, "© OpenStreetMap contributors · openstreetmap.org/copyright · ODbL 1.0 · assumptions in KLCC_ROAD_CASE.md", fontsize=8.5, color="#647080")
    fig.savefig(DEST / "klcc-nearby-routes.png", dpi=160)
    plt.close(fig)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--plots", action="store_true", help="Requires optional matplotlib")
    args = parser.parse_args()
    network, source, indices, result = evaluate()
    if args.plots:
        plot(network, source, indices, result)
    print(json.dumps({"directions": result["directions"], "fallback_reasons": result["fallback_reasons"]}, indent=2))
    print("Saved docs/evaluation/KLCC_RESULTS.json" + (" and two PNG figures" if args.plots else ""))


if __name__ == "__main__":
    main()
