# Offline MVP guide

The prototype answers: under this specified synthetic model, which access points fit a planning-time limit? It is an algorithm demonstration, not advice about a real house.

## Why the complete journey matters

The motivating outbound examples are Sungai Buloh `30 + 18 = 48` minutes and Rawang `35 + 5 = 40` minutes. Comparing only the main corridor reverses their ordering. Every home therefore has its own local access edge(s). A place name organizes examples; it does not supply one duration for an entire area.

The graph allows multiple gateway connections. For the alternative-entrance example, the base options are `30 + 20 = 50` through Sungai Buloh and `35 + 5 = 40` through Rawang. With an assumed 1 min/km buffer, their assumed distances of 26 and 43 km produce 76 and 83 minutes. The chosen entrance changes because the route optimizer includes the buffer.

A condo's 5-minute allowance covers the assumed home/parking/exit overhead once. Outbound includes arriving from the entrance/parking to home. Both directions use the same overhead here; real buildings may need different values. Workplace parking and lift overhead are zero/unmodelled in this fixture.

## Routing and its limits

For each edge, use `cost = scenario_minutes + beta × routed_km`, always finite and nonnegative. For each route, add its edge costs and the home overhead. Dijkstra repeatedly settles the smallest tentative cost using a heap. It is appropriate here because no edge has negative cost.

For outbound travel, search forward from KLCC. For inbound travel, search the reversed adjacency from KLCC while retaining the costs of the original directed edges. Reconstruct paths in their original driving order. This computes all home-to-KLCC distances in one search; it does not permit driving the wrong way.

Homes are private endpoints, not intermediate transit nodes. The search can reach a home but never expands through it. Endpoint overhead is added once after routing because it is independent of which permitted route reaches that home.

These are static snapshots. Morning/evening multipliers are fixed for the whole route. The implementation does not update traffic as the vehicle reaches later edges, query a calendar date, or solve an arrival-deadline problem. A linear distance buffer cannot capture correlated incidents or establish P90 travel time.

The heap implementation uses lazy duplicate entries. With `V` nodes and `E` edges, search work is bounded by roughly `O((V + E) log(E + 1))`, with up to `O(V + E)` storage. Reconstructing a route costs its number of edges. Scanning and drawing `n × n` centres is `O(n²)` plus route reconstruction. Adaptive interpolation has additional subdivision/painting overhead; fewer oracle calls do not imply lower end-to-end runtime for this known graph.

## Spatial representation and algorithm selection

The schematic is 32 km wide and high. A 16/32/64-cell axis gives 2 km/1 km/500 m cell widths. Coordinates and road distances are invented independently; the diagram is explanatory, not a scaled road survey. A centre represents one hypothetical residential access point, not every address in that cell.

| Method | Sampling rule | Main trade-off |
| --- | --- | --- |
| Full scan | Visit every centre in row order, or stop at an explicit CLI/API budget. | Exact classifications for queried model centres; sensible when the full graph is cheap. |
| Uniform | Query a roughly evenly spaced `floor(sqrt(budget))` by `floor(sqrt(budget))` lattice. | Broad coverage; may waste queries far from the threshold and leave some budget unused. |
| Adaptive | Start with 4 × 4 major blocks; probe corners/centre and subdivide selected blocks. | Targets sampled changes but can miss entirely unobserved pockets or exhaust the budget unevenly. |

Adaptive subdivision prioritizes mixed/unknown observations, proximity within 4 minutes of the threshold, or a sampled range of at least 8 minutes. The sampled range is a refinement heuristic, not a proven gradient bound. The parameter choices were fixed before the reported comparison.

Uniform and adaptive both use bilinear interpolation between valid observed corners. If required corners lack a usable duration, the interior remains unknown. Direct observations always override interpolation. A known no-route observation keeps that label. An unobserved no-route location can still be wrongly inferred by interpolation; sparse sampling has no general guarantee against that failure.

The full grid is the MVP default. Uniform did better than this adaptive policy at equal 256-query budgets in the fixed comparison. We retain the failed-pocket test and the weaker results rather than silently tuning the method until it looks successful.

## Boundary and export

Treat each qualifying centre as a qualifying cell for visualization. Collect its four directed sides and cancel shared reversed sides. The remaining segments preserve holes and disconnected pockets without smoothing. A GeoJSON export contains one polygon per qualifying cell plus the outline; it does not claim to be a merged smooth isochrone.

The export approximates longitude/latitude from a schematic local frame near KL. It includes a synthetic-data label, all settings, the time model, queried/estimated/unknown/no-route counts, and a study-edge flag. Contact with the study edge means the feasible set may continue beyond the domain. Omitted polygons do not distinguish outside from unknown/no-route without the accompanying coverage information; use the JSON `demo` command for the full labelled grid.

## Module map

| Path | Responsibility |
| --- | --- |
| `commute_map/model.py` | Validated graph nodes/edges and additive policy. |
| `commute_map/routing.py` | Dijkstra index, route reconstruction, and inclusive classification. |
| `commute_map/scenarios.py` | Clearly synthetic homes, gateways and spatial fixture. |
| `commute_map/sampling.py` | Query budget/cache, full/uniform/adaptive samples, and interpolation. |
| `commute_map/contours.py` | Cell sides, clipping signal, and GeoJSON. |
| `commute_map/app.py` | Validated run settings, assembled results and provenance. |
| `commute_map/server.py`, `__main__.py` | Loopback-only local API and command-line interface. |
| `commute_map/static/` | Dependency-free local interface and canvas. |
| `tests/` | Model, algorithm, HTTP and frontend-logic regressions. |
| `scripts/evaluate.py` | Fixed developer comparison and reproducible report generation. |

## Walkthrough

1. Start the demo, set the distance buffer to zero, and update. Sungai Buloh is 48 minutes; Rawang is 40. At a 45-minute limit, only Rawang qualifies among those two examples.
2. Set the buffer to 0.2. They become 54 and 47.6 minutes. Select a card to see all components; no extra risk score is used.
3. Select the Cheras condo: at zero buffer it is 31 minutes, including 5 minutes for access. Set condo access to zero; it becomes 26. Landed examples do not change.
4. Change direction to Home → KLCC. The base Sungai Buloh example becomes 52 minutes, demonstrating directional asymmetry.
5. Try adaptive sampling with budget zero. The grid is unknown, while six example cards are separate reference lookups and remain populated. Sample counters exclude those six lookups and report them separately in the manifest.
6. Export the current result. Changing controls without applying them disables export until the new run finishes. If the API errors, the old map remains with an explicit failure message.

## Learning checkpoints for later

- Why is Rawang preferred with no buffer even though its main corridor takes longer?
- Why must the distance allowance be included during route choice?
- What exactly does reverse-graph Dijkstra compute, and why is it valid for this static model?
- Can equal corner labels prove there is no reachable pocket inside a cell?
- Why do 100% model agreement and a distance allowance say nothing by themselves about a 90% real-world arrival probability?

No question is marked understood until the developer supplies their reasoning. Implementation was authorized to continue while the user was away.
