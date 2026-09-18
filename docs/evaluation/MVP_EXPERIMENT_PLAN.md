# Fixed MVP experiment design

Defined before the original local comparison on 2026-09-17.

- 32 × 32 synthetic access points; both directions; example, morning and evening profiles; thresholds 40, 45 and 60 minutes.
- Fixed 0.2-minute buffer per road kilometre and 5-minute condo allowance.
- Full scan: 1,024 queries. Uniform and adaptive: 256 queries each.
- Sparse methods share bilinear interpolation. Adaptive subdivision uses mixed classifications, unknown values, proximity within 4 minutes of the threshold, or travel-time range at least 8 minutes.
- All 18 cases are retained without tuning per case. Compare agreement with the reference, false inclusions/exclusions, unresolved predictions, queries, and unsampled-point results.
- Whole-domain metrics include queried points and are not independent real-world accuracy estimates. Reference no-route cells are evaluated separately.
- Compare a shared workplace index with repeated early-exit shortest-path searches on 256 homes in both directions. Independent Floyd–Warshall tests add 30 random-graph checks.
- Default selection: full scan for this small, cheap, fully available graph. Sparse methods remain experimental. A missed-pocket regression must stay visible.
- No residence scoring feature or extra public benchmark product. This experiment supports the user's request to test the algorithm choice.
