# Map Algorithm — Project Brief

Status: **Offline algorithm MVP and bounded static OSM case implemented**, 2026-09-18. Routing, sampling, local demo, exports and automated checks exist. Browser rendering is still unverified. Stage 1 provider research remains incomplete and paused. The original traffic-aware V1 contract in sections 1–8 is retained as a later target; synthetic and static-road results do not satisfy it. See [current state](PROJECT_STATE.md), [MVP guide](docs/MVP_GUIDE.md), [road case](docs/evaluation/KLCC_ROAD_CASE.md), and [provider review](docs/research/ROUTING_PROVIDER_REVIEW.md).

## Current portfolio MVP

The user explicitly authorized autonomous implementation and debugging while away, including local-road differences, coarse/fine spatial grids, distance allowance within final travel time, and condo access. This supersedes the earlier instruction to wait for comprehension answers during this build; understanding remains unverified.

Current model, in minutes:

`T_plan(p,d) = a_p + min over legal routes P [sum of scenario edge times + beta × sum of routed edge km]`.

Here `a_p` is the once-per-home access allowance (5 minutes for a condo by default); `beta` is an adjustable, nonnegative assumed minutes-per-kilometre buffer. Optimize the complete planning time, not the nearest entrance or suburb-level corridor alone. Inputs include direction, threshold, fixed example/morning/evening profile, buffer, condo allowance, resolution, method and budget. Exact CLI/API limits and outputs are described in `docs/MVP_GUIDE.md` and validated in `commute_map/app.py`.

The implementation is Python 3.10+ with no runtime dependencies. It uses a synthetic directed graph, a one-workplace Dijkstra index, full/uniform/adaptive grid sampling, interpolation, unsmoothed cell outlines, and a small local UI. The geometric domain is a 32 × 32 km schematic with 2 km/1 km/500 m cell widths. Each centre is one assumed access point, not a guarantee about all properties inside a cell.

The original portfolio research question remains useful: can adaptive sampling reduce queries at comparable accuracy? The fixed comparison did not favor this adaptive method: at 256 samples uniform mean agreement was 97.82%, adaptive 95.38%. Full scan is the default for the available small graph. These are model comparisons, not real-world traffic accuracy or actual paid-API savings; the [report](docs/evaluation/MVP_RESULTS.md) provides denominators, unresolved predictions and limits.

The planning allowance is not calibrated statistical risk. No claim that it captures every traffic condition, represents P90, or provides an arrival probability is authorized by these examples. A separate bounded OSM case now supplies real network geometry, supported access/turn rules and a history-aware index, while using explicitly assumed static speeds. It evaluates road nodes, not verified residential entrances, and deliberately confines paths to the extract. Dated traffic routing, verified entrance access, journey observations, public deployment, and software licence selection remain future work. The bundled OSM database is attributed under ODbL. A later traffic integration must explicitly distinguish provider road duration from the added planning allowances before evaluating the retained traffic-aware criteria.

## 1. Problem statement

Build a fine-grained driving commute accessibility engine for Klang Valley. Given one workplace, one travel-time limit, one departure timestamp, one direction, and a bounded study area, estimate which specific residential road-access locations meet that limit using traffic-aware routing estimates. Generate the boundary with our own spatial sampling and contour algorithm.

Geographic distance, a suburb centroid, and proximity to a highway cannot adequately represent the question. Legal turns, medians, one-way streets, estate exits, feeder roads, ramps, and congestion can make nearby locations behave differently. Morning home-to-work travel and evening work-to-home travel are separate queries.

The project originates in the user's commuting experience, including local access differences around Sungai Buloh and queues near Jalan Ampang / Jalan Tun Razak. These observations motivate future test cases; they are not a measured validation dataset.

Long-term question: where can someone live given both a commute limit and a tolerance for uncertainty? V1 answers the narrower question using provider-predicted durations. It cannot establish the probability of a real journey arriving on time.

## 2. V1 user story and scope

> As a Klang Valley commuter, I want to specify my workplace access point, a 45-minute driving limit, a weekday departure date and time, and home-to-work direction, so I can inspect an estimated feasible region and the evidence behind it within a chosen study area.

The same engine must support a separate work-to-home run with its own departure timestamp. A single run has exactly one workplace, threshold, timestamp, and direction.

V1 is an engine and inspectable geographic outputs. A polished map application is Stage 7. The routing provider supplies point-to-point durations and supported route information; this project owns sample placement, threshold classification, boundary construction, query accounting, and evaluation. A provider's isochrone polygon may be a later benchmark, never the core output passed through unchanged.

### Time and access semantics

- V1 uses **depart at**, not an arrival deadline. For inbound travel, every sampled home departs at the same timestamp. For outbound travel, the workplace departure is fixed.
- A date, local clock time, and timezone are required. “Morning peak” is a descriptive label, not a sufficient routing request. An arrival-by question needs a different formulation and is deferred.
- A location is a specific usable driving access point. A building centroid or suburb label is not an adequate replacement. Walking, parking, lift time, and unmodelled private-driveway time are outside the routed duration.
- The study area limits candidate home locations, not the roads a valid route may traverse. A good route may leave the study area and return.
- Road snapping must not silently move a home across a median, onto an inaccessible carriageway, or to a different estate exit. Access ambiguity must be visible.

## 3. Precise V1 inputs

This is a logical contract, not an implemented API schema. Names can change when the user understands and implements the relevant component.

| Input | Meaning and validation |
| --- | --- |
| `workplace_access` | One WGS84 position with explicitly named longitude and latitude in degrees; valid geographic ranges and a verified or explicitly unverified driving entrance. No silent conversion from a suburb centroid. |
| `study_area` | A bounded geographic polygon, or bounding box converted to one, within the Klang Valley pilot. Bounds must be explicit and nonempty. The workplace need not lie inside it. Exact pilot bounds remain to be chosen. |
| `threshold_seconds` | One positive finite maximum routed duration. User-facing minutes convert once to seconds; the inside rule is inclusive. Example: 45 minutes = 2,700 seconds. |
| `departure_at` | One dated, timezone-aware timestamp. Preserve the original local time and an unambiguous normalized instant. Use `Asia/Kuala_Lumpur` for the pilot; reject unsupported provider time horizons rather than silently substituting “now.” |
| `direction` | Exactly `home_to_work` or `work_to_home`; determines origin/destination ordering independently of the time label. |
| `routing_policy` | Driving mode and explicit toll/avoidance preferences, held constant within a run. Traffic mode must be supported and recorded. No provider defaults may remain undocumented. |
| `sampling_config` | Explicit initial coverage, refinement limit, and distance units. A proposed local target is 100 metres in resolved boundary areas; the method and feasible settings are deferred. |
| `query_budget` | A finite cap on routing elements/attempts and a runtime limit. Monetary estimates, matrix accounting, retries, and feasible default caps must be defined after Stage 1. This document authorizes no paid API calls. |

The selected provider/configuration and run identifier will also be explicit once Stage 1 is complete. The Stage 1 technical recommendation is conditional and does not activate an account or resolve data-use permissions. Secrets must remain outside committed configuration. Distances for sampling must use a suitable metric calculation; degrees are not metres. A projected CRS or geodesic approach remains undecided. Geographic output positions use longitude, latitude order.

## 4. Precise V1 outputs

| Output | Required contents |
| --- | --- |
| Estimated accessibility geometry | GeoJSON Polygon/MultiPolygon features or an explicit empty result; preserve supported holes and disconnected components. Clip to the study area and mark contact with its boundary as potentially truncated. |
| Sample evidence | Sample ID; requested coordinates; origin/destination; snapped/access coordinates and displacement when available; predicted duration in seconds or a null value with a reason; query timestamp; traffic mode; threshold classification. |
| Coverage and unresolved regions | Identify unqueried, failed, access-ambiguous, and insufficiently refined areas. Where a spatial uncertainty mask cannot be supported, explicitly mark the affected cells or withhold that part of the contour. |
| Run manifest | Complete inputs; provider and version/model information if exposed, otherwise `unknown`; collection start/end; software/configuration version; sampling resolution; interpolation settings; cache/retention policy; query and retry counts; elapsed time; stop reason. |
| Diagnostic summary | Inside/outside/unknown counts, provider-reported no-route counts, coverage, budget use, geometry validity, and applicable limitations. An evaluation run also reports the metrics below. |

The sample outcomes are distinct:

- `inside`: a valid, usable provider duration is at most the threshold.
- `outside`: a valid, usable provider duration exceeds the threshold.
- `no_route`: the provider explicitly reports no route for the request; keep separate from an over-limit duration. Whether this can establish model-unreachability depends on verified provider semantics and access validity.
- `unknown`: a request failed, was not made, used ambiguous access, or cannot support a valid classification.

Do not convert missing durations to zero or infinity to make contour extraction easier. Do not present interpolated interiors as independently queried evidence. A polygon estimates access within the sampled domain; it does not certify every property or every patch of land it encloses. If the budget stops a run early, return partial coverage and a visible reason, not a completed-looking region.

All persistence and sharing of provider-derived outputs must follow the terms verified in Stage 1. The logical output contract does not assume those terms permit public raw-response fixtures or indefinite caching.

## 5. Mathematical formulation

Let:

- `D` be the bounded study area and `A_D` its admissible residential driving access points;
- `X` be the workplace driving access point;
- `t` be a fixed departure timestamp, `Y > 0` the threshold in seconds;
- `d` be direction and `theta` the routing/traffic policy;
- `r` identify the provider query context, including when estimates were retrieved.

Define the origin/destination mapping:

$$
Q_d(p,X)=
\begin{cases}
(p,X), & d=\text{home-to-work},\\
(X,p), & d=\text{work-to-home}.
\end{cases}
$$

Write the returned predicted duration as:

$$
\widehat T_d(p;X,t,\theta,r)
=\widehat T\bigl(Q_d(p,X),t,\theta,r\bigr).
$$

The provider-defined feasible access set is:

$$
\widehat S_d(X,Y,t;\theta,r)
=\{p\in A_D:\widehat T_d(p;X,t,\theta,r)\le Y\}.
$$

This set is only defined where the routing result and access location are valid. In practice, query finitely many points `P` within `D`, classify them, and estimate a region `S_tilde` and its boundary. Report the unresolved domain alongside it. Approximation error and missing coverage remain even if every queried duration is correct.

“Deterministic” describes thresholding and contour generation from a fixed set of returned estimates. It does not imply that the provider will return the same ETA tomorrow, or that a real journey has a fixed duration. Queries made minutes apart may also reflect different traffic snapshots.

### Directed and time-dependent network intuition

A legal driving route is an ordered path through a directed road network. A conceptual edge cost `w_e(s)` is travel time when entering edge `e` at time `s`. Starting at `s_0 = t`, traverse a path using `s_i = s_(i-1) + w_ei(s_(i-1))`. An ideal fastest route minimizes `s_k - t` over legal paths, including turn restrictions.

This is the mathematical motivation, not a claim about any provider's algorithm. Reversing endpoints need not preserve duration. Evaluating every edge at the initial departure time is also not the same as modelling traffic encountered later in the trip.

The useful explanatory decomposition is:

$$
T_{\rm total}=T_{\rm local\ access}+T_{\rm main\ corridor}+T_{\rm destination\ access}.
$$

It is conceptual in V1. Do not claim to measure these components without suitable segment data. A farther highway entrance may produce a faster total route; do not force routing through the nearest entrance.

### Deferred reliability formulation

For actual journey duration `T_real` across comparable days and a defined travel/route-choice policy, the later target is:

$$
S_\alpha=\{p\in A_D:
P(T^{\rm real}_d(p;X,t)\le Y\mid\text{comparable commute conditions})\ge\alpha\}.
$$

Repeated API predictions alone describe prediction variability. They do not establish this real-world probability without appropriate observations or calibration. No reliability estimate is part of V1.

## 6. Explicit V1 non-goals

- A guaranteed arrival time, arrival-by optimization, or empirical on-time probability.
- GPS collection, repeated-day statistical modelling, P90 maps, or machine learning.
- Identifying or attributing actual bottleneck delay, or measuring the three commute components.
- Reimplementing a national routing engine or claiming globally optimal routes from a provider response.
- Property listings, property suitability ranking, automatic building-entrance discovery, or suburb-wide guarantees.
- Public transport, walking, multimodal routing, mobile apps, or multiple cities.
- Multiple workplaces, joint morning/evening optimization, or multiple thresholds within one run.
- A polished frontend, deployment, or an open-source release in Stage 0.

## 7. Major technical unknowns

The [Stage 1 review](docs/research/ROUTING_PROVIDER_REVIEW.md) now confirms several documented capabilities, limits, prices, and restrictions. The questions below remain the investigation register; documented support does not establish local quality or account entitlement. Retained provider evidence and contour export are still conditional on a compatible data-use permission model.

| Unknown | Why it matters | Stage that resolves it |
| --- | --- | --- |
| Klang Valley traffic coverage and departure-time semantics | “Traffic-aware” may mean different live, typical, historical, or forecast behaviour; the requested use case must actually be supported. | 1, verified in 2 |
| Matrix directions, limits, pricing, and request units | Many-origins-to-one-destination queries may have different constraints from outbound queries. Batch counts alone can hide cost. | 1 |
| Licensing, caching, derived outputs, attribution, and redistribution | Determines what can be stored, displayed, shared, replayed, and released. | 1 |
| Road snapping, entrances, divided roads, and restricted access | Incorrect access can erase the difference between neighbouring homes before our algorithm even starts. | 1–2, evaluated in 4 |
| Exact workplace entrance, pilot bounds, test times, and toll policy | Needed for a reproducible pilot, but not supplied yet. KLCC is an example, not a verified coordinate. | Before the first Stage 2 query |
| Sampling and contour method | Sparse samples can miss thin corridors, holes, and enclosed pockets. Equal corner labels do not prove a cell is uniform. | 3 |
| Discontinuity handling | Access changes can create abrupt jumps; smooth interpolation and gradients may be misleading. Radial binary search requires monotonicity that has not been established. | 3–4 |
| Query timing drift and lawful replay | Mixing live snapshots confounds algorithm comparisons; stored fixtures may have contractual limits. | 1–3 |
| Evaluation reference and practical resolution | Provider agreement is measurable before real journeys are available; real ETA accuracy is a different claim. | Design now; validate in 2–4 and expand in 8 |

## 8. Measurable V1 success criteria

These are proposed targets for later implementation and evaluation. They have not been tested. Resolve provider feasibility in Stage 1 and record any change to the numerical targets in `DECISIONS.md` before evaluating results.

| ID | Acceptance criterion | Evidence required later |
| --- | --- | --- |
| C1 — Query correctness | For two access points, two departure instants, and both directions (eight requests), 100% of captured requests preserve endpoints, time, timezone, units, and policy. | Request/response audit. Equal returned durations are allowed; an artificial duration change is not proof of time semantics. |
| C2 — Classification | 100% correct threshold classification for below/equal/above cases; every missing, invalid, ambiguous-access, and no-route case retains its distinct status. | Small deterministic fixtures including exact equality and failures. |
| C3 — Geometry and coverage | Every emitted geometry is valid or accompanied by an explicit failure; empty/full-domain cases, clipping, holes, disconnected pockets, and unknown areas have explicit behaviour. | Designed synthetic spatial fixtures and inspection of pilot outputs. No smoothing that destroys supported topology. |
| C4 — Spatial detail | Target at most 100 m sampling spacing in boundary areas declared resolved. Areas not meeting this target remain visibly unresolved; spacing is not a claim of 100 m boundary accuracy. | Sample spacing/refinement report and access audit. Stage 4 includes verified pairs across divided roads, near ramps, behind poor feeder access, and affected by one-way access. |
| C5 — Provider agreement | On at least 200 held-out, eligible access points, target at least 95% classification agreement, with false inclusion and false exclusion each at most 5%. At most 5% may be unresolved by the contour. | Freeze the evaluation points before tuning. Include at least 50 provider-inside, 50 provider-outside, and 50 within ±5 minutes of the threshold (these groups may overlap). Report all denominators and unresolved cases. |
| C6 — Cost and stopping | Never exceed the configured routing budget; account for all requests, matrix elements, retries, failures, and cache hits. Stop with a partial result when necessary. | Instrumented run report and budget-exhaustion checks. Stage 1 defines provider-specific accounting and feasible caps. |
| C7 — Algorithmic value | Produce the boundary from our sampled durations and our algorithm; compare against a uniform-grid baseline on the same domain and evaluation corpus. | Record query usage and quality at comparable resolution. A 30% reduction in routed elements is an exploratory efficiency goal, not grounds to select an adaptive algorithm prematurely. |
| C8 — Reproduction and honesty | Given the same lawful recorded durations and configuration, reproduce classifications and geometry within a declared numerical tolerance. All outputs identify ETA source, timestamp, coverage, and limitations. | Repeated offline runs where retention is permitted; otherwise synthetic fixtures plus documented live non-reproducibility. No actual-journey accuracy or reliability claim. |

For C5, agreement uses all eligible held-out points as its denominator; unresolved contour predictions do not count as agreements. False inclusion is the proportion of provider-outside points classified inside, and false exclusion is the proportion of provider-inside points classified outside. Report provider-query failures separately rather than quietly replacing inconvenient points. Held-out durations must be comparable in departure settings and traffic context. Report near-threshold and difficult-access subsets separately so easy points do not hide failures.

The holdout reference measures approximation to a routing provider, not actual commute accuracy. Any provider-isochrone comparison is supplementary and must account for differences in settings and access semantics.

## 9. Repository structure

Stage 0 began with documentation. The offline MVP now uses:

| Path | Responsibility |
| --- | --- |
| `README.md` | Overview, commands, model, results and limitations. |
| `PROJECT_BRIEF.md` | Stable goal, current offline scope, retained traffic-aware target. |
| `PROJECT_STATE.md` | Evidence, actual progress, remaining work and learning status. |
| `DECISIONS.md` | Choices, alternatives, rationale and scope changes. |
| `commute_map/` | Python graph, routing, sampling, boundary, app, CLI and server. |
| `commute_map/static/` | Local interactive demo. |
| `tests/` | Model/HTTP and optional frontend-logic tests. |
| `scripts/evaluate.py` | Reproducible developer experiment. |
| `docs/MVP_GUIDE.md` | Architecture, mathematics and user walkthrough. |
| `docs/evaluation/` | Frozen plan, raw results, report and verification record. |
| `docs/learning/` | Offline plan and original directed-graph exercise. |
| `docs/research/` | Earlier provider research. |
| `docs/PROJECT_INSTRUCTIONS.md` | Preserved user-supplied formal instructions. |

Add future components only when needed. The MVP uses in-run memoization, not a commercial-data cache. No runtime database, ML package or provider credential is required.

## 10. Delivery and learning rules

The user is the primary developer. The usual loop is to explain the problem, compare approaches, justify a recommendation, check understanding, implement, test and document. For this MVP session, the user explicitly instructed autonomous execution without waiting for further prompts; D014 records that exception. Preserve the learning backlog and never infer mastery from code completion.

Track BUILT, TESTED, UNDERSTOOD, and DOCUMENTED separately. Explained content does not count as understood, and written acceptance criteria do not count as passing tests.

The initial session delivered Stage 0 only. The user's subsequent instruction to continue advanced work to Stage 1 routing/data investigation. After clarifying the portfolio objective, the user accepted an additional offline algorithm milestone before further provider integration; see D013. Stage 1 remains open. Stages 2–4 build and examine the traffic-aware deterministic engine; Stages 5–6 add reliability and bottleneck work; Stage 7 adds the product UI; Stage 8 broadens evaluation; Stage 9 prepares release. Incremental validation belongs beside implementation even though there is a dedicated later evaluation stage.

The uploaded [formal instructions](docs/PROJECT_INSTRUCTIONS.md) and the user's Work Mode handoff govern this draft. New explicit user instructions take precedence. Important new assumptions here are marked as proposed in [DECISIONS.md](DECISIONS.md), and the current learning state is recorded in [PROJECT_STATE.md](PROJECT_STATE.md).
