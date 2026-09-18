# MVP model and learning notes

## One final planning time

For a candidate home p and a legal directed path P:

    planning_time(p) = home_access(p)
                       + min_P sum_e [road_minutes(e, period) + beta * road_km(e)]

beta is an adjustable planning allowance in minutes per routed kilometre. The displayed decomposition uses the chosen path and separates its corridor and local-road edges. All edge costs are nonnegative, so Dijkstra applies. The home allowance is constant across routes for a particular home and is added once.

The model chooses a route using the full road-plus-buffer cost. It does not choose the fastest base route first and blindly add a penalty afterward. For example, the alternative-entrance fixture switches routes when beta becomes sufficiently large.

For home-to-work, reverse the graph for the computation and search outward from the workplace. Preserve each original edge's cost and reconstruct the original legal direction. This is valid for the fixed snapshot model; it does not solve time-dependent arrive-by routing. Private home nodes are terminal access points and cannot become public shortcuts.

## How the user's examples appear

| Example | Corridor | Local | Home access | Base total |
| --- | ---: | ---: | ---: | ---: |
| KLCC to Sungai Buloh inner estate | 30 | 18 | 0 | 48 |
| KLCC to Rawang near access | 35 | 5 | 0 | 40 |
| KLCC to Cheras inner estate (invented) | 22 | 20 | 0 | 42 |
| KLCC to Cheras condo (invented) | 22 | 4 | 5 | 31 |

The first two corridor/local values are user-supplied illustrative examples, not measurements. All road lengths, other times, directions and profile multipliers are synthetic. The condo allowance comes from the user's suggested 5-minute example and is configurable.

At beta = 0.2, the assumed 30 km Sungai Buloh route adds 6 minutes; the assumed 38 km Rawang route adds 7.6. These distance assumptions are part of the fixture, not assertions about real road lengths.

Distance does not establish volatility by itself. The simple linear buffer is a testable planning assumption, not an empirical percentile or confidence guarantee. A future statistical version requires suitable repeated observations and calibration. FHWA describes route travel-time variation and additional planning buffers, but does not validate this project's distance coefficient: [travel-time reliability report](https://ops.fhwa.dot.gov/publications/tt_reliability/TTR_Report.htm).

## Major grid and internal grid

Spatial blocks organize sample allocation. They do not replace all homes in a suburb with one travel time or force routes through one representative centre. Individual points have their own local connections, condo flags and directed costs.

The adaptive method starts with 4 × 4 major blocks and probes corners and centres. It subdivides blocks with mixed labels, missing values, high cost range or near-threshold values. Uniform sampling queries a regular lattice. Both interpolate between corner samples. A matching set of corners does not certify the interior: the regression suite deliberately demonstrates a missed reachable pocket.

For this small offline graph, full scan is inexpensive and avoids interpolation error at cell centres. Uniform sampling performed better than this adaptive rule in the original fixed comparison. There is no claim that adaptive sampling must win or that this choice is best for every provider/budget.

## Boundary construction

Each inside cell contributes four oriented edges. Shared edges cancel, leaving the external outline and hole boundaries. Export keeps one valid polygon per eligible cell plus the boundary segments, avoiding a fabricated smooth region. Point eligibility is established only at sampled centres; the filled area is approximate.

Unknown, failed and no-route outcomes stay separate. No-route has no finite duration. A budget-exhausted location is not automatically outside.

## Learning review, deferred by instruction

The user requested autonomous implementation while asleep. UNDERSTOOD remains NO until demonstrated. When resuming, work through one question at a time:

1. Why can 35 + 5 beat 30 + 18?
2. When can a farther entrance reduce the complete route cost?
3. Why can a distance allowance change which route is selected?
4. What does reversing edges for computation mean, and why is it not driving against a one-way road?
5. Why can a coarse cell miss a reachable pocket?
6. Why does an assumed extra 6 minutes not mean 90% on-time reliability?

The initial five-node lesson remains a useful hand exercise: A→J 2, J→X 8, A→H 6, B→H 3, H→X 3, X→A 14. Determine which homes reach X within 8 minutes and explain the route comparisons.

## Scope boundary

This is an offline planning and algorithm MVP. It is not the completed live-traffic Stage 2–4 product, an empirical reliability layer, or a production deployment. The original provider investigation and acceptance targets remain available for that next stage.
