"""Developer comparison; no residence score is exposed by the product."""
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
                    for (x,y),minutes in truth.items():
                        if minutes is None:continue
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
                        "sample_seconds":seconds})
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
            "evaluation":"Exhaustive fixed 32x32 reference domain; sampled points included and unsampled results separately counted. No real journey validation.",
            "decision":"Full scan is the default for the small available graph. Sparse methods are experimental and can miss pockets."}

def main():
    data=evaluate()
    root=Path("docs/evaluation");root.mkdir(parents=True,exist_ok=True)
    (root/"results.json").write_text(json.dumps(data,indent=2,allow_nan=False)+"\n",encoding="utf-8")
    lines=["# MVP Algorithm Evaluation","","All results concern synthetic model values at cell centres.",
           "The same 18 cases are used for every method: both directions, three assumed profiles, thresholds 40/45/60 minutes, 0.2 min/km buffer, 5-minute condo access.","",
           "| Method | Budget | Mean queries | Mean agreement | Worst agreement | Unresolved eligible predictions |",
           "| --- | ---: | ---: | ---: | ---: | ---: |"]
    for method in ("full","uniform","adaptive"):
        rows=[r for r in data["cases"] if r["method"]==method]
        lines.append(f"| {method} | {rows[0]['budget']} | {sum(r['queries'] for r in rows)/len(rows):.1f} | {sum(r['agreement_fraction'] for r in rows)/len(rows):.2%} | {min(r['agreement_fraction'] for r in rows):.2%} | {sum(r['unresolved'] for r in rows)} |")
    lines += ["","Agreement uses all reference-routable cells. Unresolved predictions are not agreements. Reference no-route cases are separate. Sampled cells are included; the raw results also count unsampled-cell performance and false inclusions/exclusions. The sampler cannot access reference values it has not queried.",
              "","## Routing comparison","",
              "| Direction | Batch relaxations | Repeated point relaxations | Batch seconds | Point seconds |",
              "| --- | ---: | ---: | ---: | ---: |"]
    for r in data["routing"]:
        lines.append(f"| {r['direction']} | {r['batch_relaxations']} | {r['point_relaxations']} | {r['batch_seconds']:.6f} | {r['point_seconds']:.6f} |")
    lines += ["","All 256 point queries in each direction agree with the shared index. Times are one-run observations, not performance guarantees.","",
              "## Decision","",data["decision"],"",
              "The regression suite includes a reachable interior pocket that adaptive corner probes miss. Full scan removes interpolation error at sampled centres; cell interiors remain approximate. None of these results validates real traffic, a universally best sampler, API billing savings, or original traffic-aware V1 targets.","",
              "Reproduce with: python -m scripts.evaluate"]
    report="\n".join(lines)+"\n"
    (root/"MVP_RESULTS.md").write_text(report,encoding="utf-8")
    print(report)

if __name__ == "__main__":
    main()
