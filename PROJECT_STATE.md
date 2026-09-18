# Map Algorithm — Project State

Updated: 2026-09-18.

## Current position

- **Milestone:** Offline algorithm MVP plus a bounded real OSM road case implemented and checked. Static assumed speeds; traffic-aware V1 remains a later target. Browser rendering verification and Stage 1 provider investigation remain open.
- **Latest authorization:** The user explicitly requested autonomous implementation and debugging through a working MVP while away, including corridor/local grids, a distance allowance inside the final time, and condo access. This overrides the earlier requirement to wait for a learning answer before implementation for this work session. Understanding must still not be inferred.
- **Repository:** `yizhechia/driving-map-algo`, private, `main`. The preceding synthetic MVP was saved in commit `4cddd49e228cf794e0bd1ca65b26d41cb8fa66a8`. This revision adds the bounded real-road experiment, source snapshot, tests and results. Repository visibility stays private.
- **Save authorization:** After automatic approval review blocked the real-road upload, the user explicitly answered “yes” to uploading and committing the prepared code, data, reports and maps to this private repository, then instructed continuation. That authorization covers this prepared update; no further confirmation is needed for it.
- **Run:** `python -m commute_map serve` for the synthetic UI; `python -m commute_map roads --output outputs/klcc.geojson` for the static OSM case. Python ≥3.10, no runtime packages or API keys.
- **Working context:** `00 | Planning`. Read this file, `PROJECT_BRIEF.md`, and `DECISIONS.md` when resuming.

## Implemented behavior

One planning time per home:

`home access + min over directed routes (corridor time + local-road time + beta × routed km)`.

The buffer is part of route optimization, not a separate residence score. Default beta is an assumed 0.2 min/km. Condo access adds 5 minutes once at the home endpoint, adjustable. These assumptions are not empirical volatility estimates or arrival guarantees.

- Generic directed graph and one-workplace Dijkstra index, with forward/outbound and reverse/inbound search.
- Synthetic KL-inspired fixture with Sungai Buloh, Rawang, Cheras, an alternative-entrance example, disconnected access, a local-access jump, and an easy-access pocket.
- A 32 × 32 km schematic with 16/32/64 cells per axis. Each centre represents one invented access point. Neither suburb labels nor major grid blocks determine a single cost for all homes.
- Full, uniform, and adaptive sampling; budgets, in-run cache, interpolation, explicit unknown and no-route results.
- Unsmooth cell-boundary extraction, cell-polygon GeoJSON, provenance, coverage counts, and a warning when eligibility reaches the study edge.
- Local UI, route breakdowns, selectable examples/cells, settings, error recovery, GeoJSON download logic, and a command-line entry point.
- Separate frozen KLCC OSM case: 12,645 road nodes, 20,106 directed segments; 291 compiled turn restrictions and 51 audited conservative fallbacks. A history-aware Dijkstra index supports via-node and via-way rules in both directions. Road-node point GeoJSON and optional route geometry carry provenance and limitations. No real-home grid or traffic is inferred.

## Evidence and component status

YES / PARTIAL / NO. UNDERSTOOD = NO means unverified, not a judgment of ability.

| Component | BUILT | TESTED | UNDERSTOOD | DOCUMENTED | Evidence / limit |
| --- | --- | --- | --- | --- | --- |
| Stage 0 specification | YES | PARTIAL | NO | YES | All nine original deliverables retained; original traffic-aware targets still proposed. |
| Offline directed routing and additive time | YES | YES | NO | YES | Hand-checkable examples; both directions; independent Floyd–Warshall reference on 30 seeded random graphs. |
| Synthetic spatial fixture | YES | YES | NO | YES | Repeatable access costs, multiple entrances, disconnected patch and pocket; no real-world accuracy claim. |
| Sampling and grid boundary | YES | YES | NO | YES | Budget, interpolation, equality, unknowns, holes, diagonal pockets, clipping, and missed-pocket tests. |
| Local API and CLI | YES | YES | NO | YES | HTTP inputs/errors/assets/export; package build and isolated installation. |
| Demo interface | YES | PARTIAL | NO | YES | Six JavaScript interaction tests against the real API with mocked DOM/canvas. Actual browser layout and native download remain unverified. |
| Algorithm evaluation | YES | YES | NO | YES | All 18 frozen spatial cases; both routing directions against repeated point searches. |
| OSM import and restriction-aware routing | YES | YES | NO | YES | 24 new tests; 240 independent full-history/Bellman–Ford comparisons; checksum and snapshot route checks. |
| Bounded real-road case and figures | YES | PARTIAL | NO | YES | Reproducible source and model results; figures visually checked. Entrances, map rules and durations are not externally validated. |
| Stage 1 provider investigation | PARTIAL | NO | NO | YES | Earlier research retained; applicable terms, account access, and local quality unresolved. |
| Live traffic-aware V1 | NO | NO | NO | PARTIAL | No commercial API calls, dated traffic query, verified residential access or measured journeys. Static OSM case is separate evidence. |
| Empirical reliability / bottleneck attribution | NO | NO | NO | PARTIAL | Distance buffer is an assumption; no statistical reliability or actual delay attribution. |
| Public open-source release | NO | NO | NO | PARTIAL | Runnable package in private repo; public release, licence, and screenshot/demo review remain pending. |

**Offline application:** BUILT YES; TESTED PARTIAL (browser verification gap); UNDERSTOOD NO; DOCUMENTED YES.

## Validation on 2026-09-18

- `python -m unittest discover -s tests -v`: **71 tests passed**, including 24 road import/history tests.
- `node --test tests/frontend.test.cjs`: **6 tests passed**, no npm packages. Uses actual `app.js` and HTTP API, but a DOM/canvas test double.
- `python -m scripts.evaluate`: **18 scenarios × 3 samplers**, plus both-direction batch-versus-point routing comparison. Exact route costs agree for all 256 homes per direction; report and raw counts are included with this version.
- Built a wheel using `pip wheel --no-deps --no-build-isolation`; installed it into an isolated directory; verified imports, static assets, model execution, and GeoJSON serialization from outside the source directory.
- The updated package also includes the attributed OSM snapshot, verifies its checksum, and runs the real-road CLI from an isolated installation.
- `python -m scripts.evaluate_roads --plots`: both directions, compiled-turn-rule ablation, nearby-node route example, JSON evidence and two visually reviewed map figures. At a 10-minute threshold, 9,003 inbound and 8,432 outbound road nodes qualify in the model.
- The available cloud browser returned `net::ERR_BLOCKED_BY_CLIENT` for the local demo. No browser-rendered screenshot or manual browser success is claimed.
- Fixed numeric overflow so a huge JSON integer returns HTTP 400 instead of interrupting the request.
- Fixed stale UI/export state when settings change during a calculation or export; regression tests cover both cases.
- Added coverage and possible clipping metadata to prevent an exported partial region being interpreted as the full reachable set.

See `docs/evaluation/MVP_VERIFICATION.md` for reproduction commands and the concrete remaining browser checks.

## Algorithm choice

On the frozen synthetic 32 × 32 grid, both directions, three profiles, thresholds 40/45/60:

| Method | Queries | Mean agreement on routable centres | Worst agreement |
| --- | ---: | ---: | ---: |
| Full | 1,024 | 100.00% | 100.00% |
| Uniform | 256 | 97.82% | 95.07% |
| Adaptive | 256 | 95.38% | 82.46% |

Unresolved centres count against agreement. Full scan is the dependable default for this small known graph. The adaptive method remains experimental: it can miss an interior reachable pocket even with matching corner labels. Results describe this fixture and resource model, not a universally best algorithm. Actual API calls and costs are zero. Sample query counts, example lookups, and routing-index work are separate.

## What remains uncertain

- Actual entrance access, source map correctness/completeness, unsupported OSM semantics, actual travel times, and provider traffic behavior. Acquisition and supported restriction logic now have a bounded offline example; this is not external validation.
- The real-road extract excludes outside detours and closes ambiguous approaches. No-route or a long route in this model does not prove real inaccessibility or a real journey time.
- Appropriate distance allowance and per-building overhead. The current linear buffer does not estimate variance, a percentile, or a confidence level.
- Sparse-sampling generalization beyond these synthetic cases and preservation of unobserved discontinuities.
- Visual behavior in real desktop/mobile browsers and native GeoJSON downloads.
- Provider retention, derived-output and display terms and account entitlements. TomTom remains a conditional technical candidate; no account or paid request was activated.

## Repository synchronization history

The synthetic MVP save initially required renewed confirmation and then succeeded. Automatic approval review also paused the real-road update at tree creation. The user subsequently explicitly approved uploading and committing its code, data, reports and maps to the same private repository. This update covers 21 project files: implementation/tests, source data/provenance, updated documentation, results and two map figures. There are no credentials or unrelated user files. Preserve the existing history with a non-force branch update, and verify the resulting commit and file hashes before reporting successful persistence.

## Next actions

1. Run the documented browser walkthrough and record actual observations; fix any layout or native-download issues found.
2. Walk the developer through the model, route choice, reversed-graph reasoning, sampling failure case, and measured trade-offs. Do not pause required fixes awaiting these answers.
3. Audit real entrances/manoeuvres and expand routing coverage beyond candidate bounds before claiming home accessibility. Use the new bounded road case and report as a reproducible starting point.
4. Resume provider integration only after capability, data-use and account questions are resolved. Calibrate any reliability claim using suitable journey evidence later.

## Learning status

No checkpoint has been answered in this thread. The original directed-graph exercise remains in `docs/learning/OFFLINE_ALGORITHM_MILESTONE.md`; `docs/learning/TURN_RESTRICTIONS.md` adds history-state and reversal questions. Earlier departure-time versus arrival-by, endpoint direction, and single-ETA versus 90% reliability questions remain unanswered. The user authorized implementation while away, not a change to UNDERSTOOD status.

## History and update discipline

Stage 0 established all nine foundation deliverables and preserved the byte-identical uploaded instructions. Stage 1 documented providers and a conditional pilot without any routing calls. The portfolio discussion authorized an offline milestone, then the user explicitly expanded that into autonomous MVP execution. D013–D018 record that sequence. Continued work added the static OSM case and history-aware routing under D019–D020.

Update evidence, unresolved work, and next actions with each meaningful change. Preserve the original formal instructions. The current repository files take precedence over older chat summaries that say the implementation is absent.
