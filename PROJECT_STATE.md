# Map Algorithm — Project State

Updated: 2026-09-18.

## Current position

- **Milestone:** Offline algorithm MVP implemented and checked; browser rendering verification remains open. Original traffic-aware V1 is a later target. Stage 1 provider investigation is incomplete and paused.
- **Latest authorization:** The user explicitly requested autonomous implementation and debugging through a working MVP while away, including corridor/local grids, a distance allowance inside the final time, and condo access. This overrides the earlier requirement to wait for a learning answer before implementation for this work session. Understanding must still not be inferred.
- **Repository:** `yizhechia/driving-map-algo`, private, `main`. At this resumption, GitHub held Stage 0/1 documents; the offline plan and MVP code were local only. This version contains the reviewed offline MVP, tests, documentation and evaluation results. Earlier upload attempts were blocked by automatic approval review; the user subsequently instructed continuation after the destination and blocker were explained. Repository visibility stays private.
- **Run:** `python -m commute_map serve` from the repository root. Python ≥3.10, no runtime packages or API keys.
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
| Stage 1 provider investigation | PARTIAL | NO | NO | YES | Earlier research retained; applicable terms, account access, and local quality unresolved. |
| Live traffic-aware V1 | NO | NO | NO | PARTIAL | No commercial API calls, real road network, dated traffic query, or measured journeys. |
| Empirical reliability / bottleneck attribution | NO | NO | NO | PARTIAL | Distance buffer is an assumption; no statistical reliability or actual delay attribution. |
| Public open-source release | NO | NO | NO | PARTIAL | Runnable package in private repo; public release, licence, and screenshot/demo review remain pending. |

**Offline application:** BUILT YES; TESTED PARTIAL (browser verification gap); UNDERSTOOD NO; DOCUMENTED YES.

## Validation on 2026-09-18

- `python -m unittest discover -s tests -v`: **47 tests passed**.
- `node --test tests/frontend.test.cjs`: **6 tests passed**, no npm packages. Uses actual `app.js` and HTTP API, but a DOM/canvas test double.
- `python -m scripts.evaluate`: **18 scenarios × 3 samplers**, plus both-direction batch-versus-point routing comparison. Exact route costs agree for all 256 homes per direction; report and raw counts are included with this version.
- Built a wheel using `pip wheel --no-deps --no-build-isolation`; installed it into an isolated directory; verified imports, static assets, model execution, and GeoJSON serialization from outside the source directory.
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

- Real map/network acquisition, access correctness, turn restrictions, actual travel times, and provider traffic behavior.
- Appropriate distance allowance and per-building overhead. The current linear buffer does not estimate variance, a percentile, or a confidence level.
- Sparse-sampling generalization beyond these synthetic cases and preservation of unobserved discontinuities.
- Visual behavior in real desktop/mobile browsers and native GeoJSON downloads.
- Provider retention, derived-output and display terms and account entitlements. TomTom remains a conditional technical candidate; no account or paid request was activated.

## Repository synchronization history

The initial save attempt was blocked because automatic approval review required renewed confirmation for uploading local project source and documentation. After the destination and blocker were explained, the user asked to continue. The reviewed file scope is this project only; there are no credentials or unrelated user files. The save uses the existing `main` history without a force update. Verify the resulting commit and file hashes before reporting successful persistence.

## Next actions

1. Run the documented browser walkthrough and record actual observations; fix any layout or native-download issues found.
2. Walk the developer through the model, route choice, reversed-graph reasoning, sampling failure case, and measured trade-offs. Do not pause required fixes awaiting these answers.
3. Add a bounded real-road offline case with explicit static assumptions when ready; keep it separate from synthetic and live-traffic evidence.
4. Resume provider integration only after capability, data-use and account questions are resolved. Calibrate any reliability claim using suitable journey evidence later.

## Learning status

No checkpoint has been answered in this thread. The original directed-graph exercise remains in `docs/learning/OFFLINE_ALGORITHM_MILESTONE.md`. Earlier departure-time versus arrival-by, endpoint direction, and single-ETA versus 90% reliability questions remain unanswered. The user authorized implementation while away, not a change to UNDERSTOOD status.

## History and update discipline

Stage 0 established all nine foundation deliverables and preserved the byte-identical uploaded instructions. Stage 1 documented providers and a conditional pilot without any routing calls. The portfolio discussion authorized an offline milestone, then the user explicitly expanded that into autonomous MVP execution. D013–D018 record the sequence and choices.

Update evidence, unresolved work, and next actions with each meaningful change. Preserve the original formal instructions. The current repository files take precedence over older chat summaries that say the implementation is absent.
