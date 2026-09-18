# Fixed MVP experiment design

Written before running the comparison on 2026-09-17. Developer validation only; the application presents a single planning time, not a residence score.

- Reference: the complete synthetic directed graph; one independently tested shortest-path index.
- Spatial cases: a 32 × 32 grid, both directions, example/morning/evening profiles, thresholds 40/45/60 minutes, 0.2 min per routed km, 5-minute condo access. All combinations are retained.
- Methods: full cell scan (budget 1,024), uniform sampling (budget 256), adaptive coarse-to-fine sampling (budget 256). Sparse methods share bilinear interpolation.
- Adaptive rule fixed before comparison: subdivide mixed/unknown cells, cells within 4 minutes of the threshold, or sample range at least 8 minutes. No per-case tuning.
- Compare whole-domain classification agreement at cell centres, false inclusions, false exclusions, unresolved predictions, sample counts, and separately the performance on unqueried cells. Reference no-route cases are separate. The sampler cannot inspect unsampled reference values.
- Routing check: one workplace search versus repeated early-exit Dijkstra queries for all 256 homes in the smaller grid, in both directions. Independent Floyd–Warshall tests provide a second algorithmic reference.
- Acceptance for the local MVP: exact methods agree on the model; all concept/error tests pass; budgets are respected; demo controls/export work; no model confidence or observed traffic claims. Sparse methods need not win.
- Default-selection rule: use the full scan when the complete small graph is available and inexpensive. Enable sparse methods only as visibly estimated alternatives. A missed-pocket fixture must stay visible in tests and documentation.
- No change to the original C1–C8 traffic-aware V1 targets. No public provider benchmark or additional scoring product is being built.
