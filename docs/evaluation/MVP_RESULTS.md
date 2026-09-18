# MVP Algorithm Evaluation

Synthetic scenario experiment. No provider calls or real traffic measurements.

Fixed design: 32 × 32 cells, both directions, three assumed traffic profiles, thresholds 40/45/60 minutes, 0.2 min/km buffer and 5-minute condo access. All 18 cases are included; no per-case tuning.

| Method | Query budget | Mean queries | Mean classification agreement | Worst agreement | Total unresolved eligible predictions | Times inferred at disconnected cells |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| full | 1024 | 1024.0 | 100.00% | 100.00% | 0 | 0 |
| uniform | 256 | 256.0 | 97.82% | 95.07% | 126 | 0 |
| adaptive | 256 | 256.0 | 95.38% | 82.46% | 685 | 0 |

Agreement is with the deterministic reference at cell centres, not geographic interiors or real journeys. Its denominator is every reference-routable cell; unresolved predictions are not agreements. Known unconnected reference cells are excluded from this binary metric and tested separately. Sampled points are included; raw results also record unqueried-point performance, false inclusions/exclusions, and all denominators.

The last column counts invalid finite times inferred at model-disconnected cells, over all 18 runs (162 disconnected cell-cases). Sparse interpolation can bridge an unqueried disconnected patch; the main agreement figure excludes these cells and must be read alongside this count. This additional diagnostic was added on 2026-09-18; the frozen cases and algorithms were unchanged.

The uniform and adaptive methods share bilinear interpolation. Their sample locations differ. The full method queries all cells and therefore has no interpolation error at those centres. Boundary polygons still approximate each centre by its cell area.

## Routing comparison

A single workplace search and repeated early-exit point searches agree for every one of the 256 homes in each direction. The comparison includes condo access once per endpoint.

| Direction | Batch edge relaxations | Repeated point relaxations | Batch seconds | Point seconds |
| --- | ---: | ---: | ---: | ---: |
| home_to_work | 516 | 83830 | 0.001788 | 0.072639 |
| work_to_home | 516 | 125933 | 0.001799 | 0.101916 |

Wall-clock values are one local run and include Python overhead; they are not stable performance guarantees. The independent Floyd–Warshall tests additionally check 30 random directed graphs, zero weights, and unreachable cases.

## Decision and limits

Full scan is the default for this small available graph. Sparse methods remain experimental and may miss pockets.

A deliberately isolated reachable cell is missed by coarse adaptive probes in a regression fixture. Equal corner classifications therefore cannot certify a uniform interior. Increasing the model grid from 1 km to 500 m improves sampling resolution but does not establish actual road-access accuracy.

These experiments select an implementation default for this fixture and resource model. They do not establish a universally best sampler, actual API cost savings, calibrated volatility, or the original traffic-aware V1 targets.

Reproduce: `python -m scripts.evaluate`. Raw counts and timings: `results.json`.
