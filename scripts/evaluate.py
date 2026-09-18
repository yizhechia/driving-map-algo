"""Developer validation only. No residence score is exposed by the product.

Run from the repository root: python -m scripts.evaluate
"""
import heapq
import json
from pathlib import Path
import time
from commute_map.model import Policy
from commute_map.routing import RoutingIndex
from commute_map.scenarios import build_scenario
from commute_map.sampling import Observation, sample_grid


def point_query(graph,source,target,policy):
    distances={source:0.0};queue=[(0.0,source)];relaxations=0
    while queue:
        cost,node=heapq.heappop(queue)
        if cost!=distances[node]:continue
        if node==target:return cost,relaxations
        if graph.nodes[node].home and node!=source:continue
        for edge in graph.outgoing[node]:
            relaxations+=1
            candidate=cost+edge.cost(policy)
            if candidate<distances.get(edge.target,float("inf")):
                distances[edge.target]=candidate;heapq.heappush(queue,(candidate,edge.target))
    return None,relaxations


def evaluate():
    scenario=build_scenario(32)
    records=[]
    # Fixed cases: no tuning after observing comparison results.
    for direction in ("home_to_work","work_to_home"):
        for period in ("example","morning","evening"):
            for threshold in (40,45,60):
                index=RoutingIndex(scenario.graph,"KLCC",direction,Policy(period,.2,5))
                truth={point:index.route(node).planning_minutes for point,node in scenario.cells.items()}
                def oracle(x,y):
                    t=truth[x,y]
                    return Observation("no_route") if t is None else Observation("ok",t)
                for method,budget in (("full",1024),("uniform",256),("adaptive",256)):
                    started=time.perf_counter()
                    grid=sample_grid(oracle,32,threshold,budget,method)
                    seconds=time.perf_counter()-started
                    eligible=agreement=wrong_inside=wrong_outside=unresolved=outside=inside=0
                    unqueried=unqueried_correct=0
                    no_route=no_route_correct=no_route_assigned_time=0
                    for (x,y),minutes in truth.items():
                        if minutes is None:
                            no_route+=1
                            no_route_correct+=grid["labels"][y][x]=="no_route"
                            no_route_assigned_time+=grid["labels"][y][x] in ("inside","outside")
                            continue
                        expected="inside" if minutes<=threshold else "outside"
                        actual=grid["labels"][y][x]
                        eligible+=1;inside+=expected=="inside";outside+=expected=="outside"
                        agreement+=actual==expected
                        wrong_inside+=actual=="inside" and expected=="outside"
                        wrong_outside+=actual=="outside" and expected=="inside"
                        unresolved+=actual not in ("inside","outside")
                        if not grid["observed"][y][x]:
                            unqueried+=1;unqueried_correct+=actual==expected
                    records.append({"direction":direction,"period":period,"threshold":threshold,
                        "method":method,"budget":budget,"queries":grid["queries"],
                        "eligible":eligible,"agreement":agreement,"agreement_fraction":agreement/eligible,
                        "reference_inside":inside,"reference_outside":outside,
                        "false_inclusions":wrong_inside,"false_exclusions":wrong_outside,
                        "unresolved":unresolved,"unqueried":unqueried,"unqueried_correct":unqueried_correct,
                        "reference_no_route":no_route,"correct_no_route":no_route_correct,
                        "no_route_assigned_time":no_route_assigned_time,
                        "sample_seconds":seconds})
    # Compare a batch index with independent early-exit point searches.
    routing=[];small=build_scenario(16);policy=Policy(buffer_min_per_km=.2)
    for direction in ("home_to_work","work_to_home"):
        start=time.perf_counter();index=RoutingIndex(small.graph,"KLCC",direction,policy)
        indexed={home:index.route(home) for home in small.cells.values()}
        indexed_seconds=time.perf_counter()-start
        start=time.perf_counter();count=0
        for home in small.cells.values():
            a,b=(home,"KLCC") if direction=="home_to_work" else ("KLCC",home)
            road,relaxations=point_query(small.graph,a,b,policy);count+=relaxations
            expected=None if road is None else road+(policy.condo_minutes if small.graph.nodes[home].condo else 0)
            actual=indexed[home].planning_minutes
            assert (expected is None and actual is None) or (expected is not None and actual is not None and abs(expected-actual)<1e-8)
        routing.append({"direction":direction,"homes":256,"all_routes_agree":True,
                        "batch_relaxations":index.relaxations,"point_relaxations":count,
                        "batch_seconds":indexed_seconds,"point_seconds":time.perf_counter()-start})
    return {"source":"synthetic_kl_v1","cases":records,"routing":routing,
            "evaluation":"Exhaustive fixed 32x32 reference domain; queried points included and unqueried results separately counted. No real travel-time validation.",
            "decision":"Full scan is the default for this small available graph. Sparse methods remain experimental and may miss pockets."}


def main():
    data=evaluate();path=Path("docs/evaluation/results.json")
    path.write_text(json.dumps(data,indent=2,allow_nan=False)+"\n",encoding="utf-8")
    lines=["# MVP Algorithm Evaluation","", "Synthetic scenario experiment. No provider calls or real traffic measurements.","",
           "Fixed design: 32 × 32 cells, both directions, three assumed traffic profiles, thresholds 40/45/60 minutes, 0.2 min/km buffer and 5-minute condo access. All 18 cases are included; no per-case tuning.","",
           "| Method | Query budget | Mean queries | Mean classification agreement | Worst agreement | Total unresolved eligible predictions | Times inferred at disconnected cells |",
           "| --- | ---: | ---: | ---: | ---: | ---: | ---: |"]
    for method in ("full","uniform","adaptive"):
        rows=[r for r in data["cases"] if r["method"]==method]
        lines.append(f"| {method} | {rows[0]['budget']} | {sum(r['queries'] for r in rows)/len(rows):.1f} | {sum(r['agreement_fraction'] for r in rows)/len(rows):.2%} | {min(r['agreement_fraction'] for r in rows):.2%} | {sum(r['unresolved'] for r in rows)} | {sum(r['no_route_assigned_time'] for r in rows)} |")
    lines += ["", "Agreement is with the deterministic reference at cell centres, not geographic interiors or real journeys. Its denominator is every reference-routable cell; unresolved predictions are not agreements. Known unconnected reference cells are excluded from this binary metric and tested separately. Sampled points are included; raw results also record unqueried-point performance, false inclusions/exclusions, and all denominators.","",
              "The last column counts invalid finite times inferred at model-disconnected cells, over all 18 runs (162 disconnected cell-cases). Sparse interpolation can bridge an unqueried disconnected patch; the main agreement figure excludes these cells and must be read alongside this count. This additional diagnostic was added on 2026-09-18; the frozen cases and algorithms were unchanged.","",
              "The uniform and adaptive methods share bilinear interpolation. Their sample locations differ. The full method queries all cells and therefore has no interpolation error at those centres. Boundary polygons still approximate each centre by its cell area.","",
              "## Routing comparison","", "A single workplace search and repeated early-exit point searches agree for every one of the 256 homes in each direction. The comparison includes condo access once per endpoint.","",
              "| Direction | Batch edge relaxations | Repeated point relaxations | Batch seconds | Point seconds |",
              "| --- | ---: | ---: | ---: | ---: |"]
    for r in data["routing"]:
        lines.append(f"| {r['direction']} | {r['batch_relaxations']} | {r['point_relaxations']} | {r['batch_seconds']:.6f} | {r['point_seconds']:.6f} |")
    lines += ["", "Wall-clock values are one local run and include Python overhead; they are not stable performance guarantees. The independent Floyd–Warshall tests additionally check 30 random directed graphs, zero weights, and unreachable cases.","",
              "## Decision and limits","",data["decision"],"",
              "A deliberately isolated reachable cell is missed by coarse adaptive probes in a regression fixture. Equal corner classifications therefore cannot certify a uniform interior. Increasing the model grid from 1 km to 500 m improves sampling resolution but does not establish actual road-access accuracy.","",
              "These experiments select an implementation default for this fixture and resource model. They do not establish a universally best sampler, actual API cost savings, calibrated volatility, or the original traffic-aware V1 targets.","",
              "Reproduce: `python -m scripts.evaluate`. Raw counts and timings: `results.json`."]
    Path("docs/evaluation/MVP_RESULTS.md").write_text("\n".join(lines)+"\n",encoding="utf-8")
    print("\n".join(lines))


if __name__ == "__main__":main()
