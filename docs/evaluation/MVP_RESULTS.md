# MVP Algorithm Evaluation

All results concern synthetic model values at cell centres.
The same 18 cases are used for every method: both directions, three assumed profiles, thresholds 40/45/60 minutes, 0.2 min/km buffer, 5-minute condo access.

| Method | Budget | Mean queries | Mean agreement | Worst agreement | Unresolved eligible predictions |
| --- | ---: | ---: | ---: | ---: | ---: |
| full | 1024 | 1024.0 | 100.00% | 100.00% | 0 |
| uniform | 256 | 256.0 | 97.82% | 95.07% | 126 |
| adaptive | 256 | 256.0 | 95.38% | 82.46% | 685 |

Agreement uses all reference-routable cells. Unresolved predictions are not agreements. Reference no-route cases are separate. Sampled cells are included; the raw results also count unsampled-cell performance and false inclusions/exclusions. The sampler cannot access reference values it has not queried.

## Routing comparison

| Direction | Batch relaxations | Repeated point relaxations | Batch seconds | Point seconds |
| --- | ---: | ---: | ---: | ---: |
| home_to_work | 516 | 83830 | 0.003389 | 0.124959 |
| work_to_home | 516 | 125933 | 0.003337 | 0.180972 |

All 256 point queries in each direction agree with the shared index. Times are one-run observations, not performance guarantees.

## Decision

Full scan is the default for the small available graph. Sparse methods are experimental and can miss pockets.

The regression suite includes a reachable interior pocket that adaptive corner probes miss. Full scan removes interpolation error at sampled centres; cell interiors remain approximate. None of these results validates real traffic, a universally best sampler, API billing savings, or original traffic-aware V1 targets.

Reproduce with: python -m scripts.evaluate

Verified source: 3c590e9ea1f75e3c418049e5a54dd4e625d09fa7. [CI run](https://github.com/yizhechia/driving-map-algo/actions/runs/35313293512). Raw JSON, exports and screenshots are in that run's mvp-verification artifact.
