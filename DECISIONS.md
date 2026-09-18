# Map Algorithm — Decisions

Updated: 2026-09-18. Offline MVP and bounded static OSM case implemented; current choices and the user-authorized workflow exception are in D014–D020. Earlier entries retain historical rationale. Stage 1 provider research remains open.

**Established** means required by the user's instructions, handoff, or an accepted subsequent scope decision. **Proposed** means a recommendation that has not yet been validated through implementation or the user's reasoning. **Deferred** means no selection has been made. A documented decision is not evidence that the user has mastered the concept.

## D001 — Establish the problem before building

- **Status:** Established.
- **Decision:** The initial work session completed Stage 0 documentation only. Keep the repository as persistent project memory and advance sequentially unless a justified change is recorded. Stage 1 research was subsequently authorized; D013 now records the accepted preliminary offline milestone.
- **Alternatives:** Start routing calls immediately; build a frontend first; leave scope only in chat.
- **Rationale:** The project needs an explicit question, input/output contract, and evaluation targets before technology choices.
- **Consequence:** Stage 0 contained no routing code, frontend, model, provider selection, package scaffold, or API calls. Stage 1 research followed. D013 governs the current next work.

## D002 — Use specific access locations and explicit directions

- **Status:** Established.
- **Decision:** Model each candidate as a driving access location. Home-to-work and work-to-home are distinct origin/destination mappings. Allow legal routes to choose useful access ramps rather than forcing the nearest one.
- **Alternatives:** Suburb centroids; distance circles; reversing an outbound polygon to represent inbound travel; always using the nearest highway entrance.
- **Rationale:** Local access, road direction, turns, and congestion are central to the user's problem.
- **Consequence:** Record direction, inspect road snapping, and keep access ambiguity visible. A fine grid alone cannot guarantee correct frontage-level routing.

## D003 — Own sampling and boundary generation

- **Status:** Established.
- **Decision:** Use a routing provider for travel-time evidence while implementing our own sampling and contour logic. Keep the core logic separable from vendor-specific request/response handling.
- **Alternatives:** Display a provider isochrone unchanged; write a full road-routing engine immediately.
- **Rationale:** The intended algorithmic contribution is spatial accessibility estimation and efficient querying, within a manageable V1.
- **Consequence:** Compare methods before selecting them. A coarse grid is a useful baseline, not a commitment to quadtree refinement, Marching Squares, or any particular architecture. Avoid a large abstraction framework before the first provider prototype.

## D004 — Start with departure-time semantics

- **Status:** Proposed V1 default.
- **Decision:** Use one explicit dated departure timestamp per run. For inbound travel every candidate departs at that time; for outbound travel the workplace departure is fixed.
- **Alternatives:** A common arrival deadline; a departure window; an undated “morning peak” label.
- **Rationale:** A fixed departure makes the first query precise and testable. An arrival deadline requires different time handling and possibly additional searches.
- **Consequence:** The first engine answers “leave at 08:00,” not “arrive by 09:00.” Record local timezone and normalized instant. Stage 1 must verify that a provider supports the required semantics; no silent substitution is allowed.
- **Revisit when:** The user prefers arrival-by as the first product question, or provider research identifies a feasibility constraint.

## D005 — Use a bounded pilot and explicit run policy

- **Status:** Proposed V1 contract.
- **Decision:** Require a bounded study area, one threshold, one workplace access point, one direction, and fixed routing preferences per run. Use seconds for durations and metric calculations for sampling distances.
- **Alternatives:** An unbounded regional search; multiple workplaces or thresholds immediately; implicit toll and traffic defaults; treating angular degrees as fixed distances.
- **Rationale:** Explicit bounds and policy make cost, coverage, and comparisons assessable.
- **Consequence:** The actual entrance coordinates, study bounds, date/time, toll choice, CRS method, and query cap remain open. Bounds constrain candidate homes, not permissible route geometry. A boundary touching the domain edge is potentially truncated.

## D006 — Preserve missing information and spatial structure

- **Status:** Established intent; proposed output contract.
- **Decision:** Distinguish inside, outside, provider-reported no route, and unknown. Preserve supported holes, disconnected pockets, and sharp access differences; disclose interpolation and unresolved coverage.
- **Alternatives:** Turn failed queries into outside points; assume uniform cells from matching corners; smooth away inconvenient details; force every result into one solid polygon.
- **Rationale:** Unknown data and sampling artifacts must not masquerade as commuting evidence. Road access can change abruptly.
- **Consequence:** A budget-limited run can legitimately return an incomplete boundary. Classification is inclusive at `T_hat = Y`. Provider no-route semantics must be verified before using them to assert unreachability. Geometry handling is selected in Stage 3.

## D007 — Keep predictions separate from journey reliability

- **Status:** Established.
- **Decision:** Label V1 outputs as provider-predicted commute accessibility. Reliability and bottleneck attribution remain later stages.
- **Alternatives:** Treat repeated API ETAs as actual journey observations; label a single prediction a 90% on-time guarantee; infer intersection delay without segment evidence.
- **Rationale:** Provider predictions, observed journey durations, and estimated causes of delay are different evidence types.
- **Consequence:** V1 has no P90, confidence, or on-time probability claim. Later work must specify comparable conditions and appropriate observations or calibration.

## D008 — Define evaluation before optimizing

- **Status:** Proposed acceptance targets; not measured.
- **Decision:** Use semantic fixtures, geometry/coverage cases, access audits, and a held-out provider-reference corpus. Proposed targets include 100 m sampling spacing in resolved boundary areas and at least 95% agreement on at least 200 eligible held-out access points, with explicit failure and unresolved rates.
- **Alternatives:** Judge by appearance; report only average accuracy on easy distant points; count HTTP calls without matrix elements; demand empirical commute accuracy without actual journeys.
- **Rationale:** Tests must detect the access and direction errors that motivated the project. Algorithm quality and provider prediction quality must be assessed separately.
- **Consequence:** Freeze evaluation settings before tuning. Compare query efficiency against a uniform grid. A 30% element reduction is exploratory, not mandatory algorithm selection. The exact criteria and denominators are in `PROJECT_BRIEF.md` C1–C8.
- **Revisit when:** Stage 1 establishes costs, lawful replay options, and practical domain/resolution. Any change requires a recorded reason; do not adjust targets after seeing results just to claim success.

## D009 — Investigate before committing to a provider

- **Status:** Initial comparison documented; full V1 selection still conditional. See D011 and the [provider review](docs/research/ROUTING_PROVIDER_REVIEW.md).
- **Open candidates:** Mapbox, Google Routes, OpenRouteService, Valhalla, OSRM, GraphHopper, and other OpenStreetMap-based options. They are candidates named by the user, not assertions of equivalent traffic support.
- **Decision still needed:** Verify the applicable agreement and account capabilities for the preferred technical candidate, TomTom. Stage 1 has compared it with Mapbox and Google and screened the original open-source candidates. Local routing quality requires a later pilot; documentation cannot establish that result.
- **Also deferred:** Framework, CRS implementation, database, cache lifetime, sampling/refinement method, contour library, test coordinates, and open-source licence. Python is implemented for the offline MVP under D014–D018; the live-provider architecture remains open.
- **Consequence:** Provider research is documented, but no live-provider implementation or real-traffic validation has occurred. Retention, redistribution, and public examples must follow the verified terms of the selected data source.

## D010 — Preserve the developer learning loop

- **Status:** Established.
- **Decision:** Explain and compare important choices, ask the user to reason through the core idea, then implement and validate small components. Maintain separate BUILT / TESTED / UNDERSTOOD / DOCUMENTED status.
- **Alternatives:** Generate an entire application before the user can explain it; infer mastery from having shown an explanation.
- **Rationale:** The user is the primary developer and wants an interview-explainable project.
- **Consequence:** Stage 0 documents can be complete while conceptual mastery remains unverified. No implementation component can inherit an UNDERSTOOD status from a prose draft.

## D011 — Prefer TomTom for the point-to-point pilot, conditionally

- **Status:** Proposed technical selection; not a final full-V1 provider commitment.
- **Decision:** Prefer TomTom Calculate Route for the first small pilot. Resolve its applicable API agreement and account access before activating the integration. See the [research and pilot plan](docs/research/ROUTING_PROVIDER_REVIEW.md).
- **Alternatives:** Mapbox Directions, Google Routes, and self-hosted open-source routing engines.
- **Rationale:** Documented timed routing and Malaysia traffic coverage suit the pilot. Mapbox's current Navigation API storage restriction conflicts with our retained-evidence design; Google also has content-use constraints. TomTom's terms are unresolved, not assumed permissive.
- **Consequence:** Stage 1 remains open on data-use fit. No account has been created, provider contacted, or paid request authorized. Do not silently remove the brief's evidence requirements or call a static baseline a traffic-aware V1.
- **Revisit when:** The applicable agreement is available, access/price conditions differ, or the pilot exposes inadequate access/traffic behaviour.

## D012 — Validate individual routes before matrix scaling

- **Status:** Proposed experiment design; not implemented or tested.
- **Decision:** Plan eight semantic cases from two access points, two departure times, and two directions. Inspect one response before expanding. Proposed cap: 20 attempts including retries; exact points, dates, policy, account allowance, and rate limit remain unset.
- **Alternatives:** Query a large grid first; begin with a square matrix over every point; rely on a returned duration without inspecting access.
- **Rationale:** A small route response makes endpoint order, time, units, traffic fields, and entrance access inspectable. Larger matrices can hide these mistakes and consume unnecessary units.
- **Consequence:** Use synthetic cases for deterministic failure tests and respect verified retention rules for provider results. This was the initial learning gate; D014 supersedes it for the autonomous offline MVP. Live provider access and data-use permissions remain unresolved.

## D013 — Prioritize a preliminary offline algorithm milestone

- **Status:** Established direction; detailed algorithms and numerical experiment targets remain proposed.
- **Decision:** After the user clarified the Year 2 mathematics résumé objective, they accepted the recommendation to start with a hand-solvable directed graph and a uniform-sampling baseline. Add the offline milestone documented in `docs/learning/OFFLINE_ALGORITHM_MILESTONE.md`, then investigate one adaptive method. Pause further provider investigation for now.
- **Alternatives:** Keep provider licensing/account access on the critical path; implement the full traffic-aware product first; expand into reliability or a substantial frontend.
- **Rationale:** Controlled examples support reproducible algorithm evaluation and developer understanding without a commercial traffic dependency. The intended contribution is sample selection and boundary approximation, measured against a baseline.
- **Consequence:** This is an explicit sequencing change, not completion of Stage 1 or a substitute claim of traffic-aware V1 delivery. Retain the original brief and C1–C8 targets. Static/synthetic outputs must identify their assumptions. Commercial terms remain relevant when provider work resumes.
- **Experiment constraint:** A complete fixed-weight graph permits direct shortest-path computation. Use it as a reference behind a restricted travel-time query interface; report simulated queries separately from actual runtime, reference-generation cost, and later API billing. Do not claim that sampling beats exact graph routing merely because it accesses fewer precomputed values.
- **Implementation recommendation:** Python and small functions, with a trusted reference for routing checks. Teach and check understanding before each significant component. No code is authorized to be treated as understood from the user's agreement to the roadmap.
- **Revisit when:** The uniform baseline and first experiments expose feasibility or scope issues, or the user reprioritizes live traffic.

## D014 — Complete an autonomous offline MVP, preserve unverified learning

- **Status:** Authorized by the user's subsequent explicit instruction.
- **Decision:** Proceed through implementation, debugging, runnable tests and a local demo while the user is away, without stopping for comprehension replies. Keep the original formal instructions unchanged and record learning as unverified.
- **Alternatives:** Stop at each unanswered question; treat consent to build as demonstrated understanding.
- **Rationale:** The user explicitly requested a working MVP and autonomous continuation, including concrete corridor/local/condo/buffer examples. This takes precedence over the earlier pacing rule for this session.
- **Consequence:** Python package, tests, evaluation and local UI are implemented. This does not authorize paid routing calls, claim real traffic accuracy, publish the private repo, or change UNDERSTOOD status.

## D015 — Add distance allowance to optimized time, not a separate score

- **Status:** Implemented and tested as an assumption.
- **Decision:** Minimize the sum of nonnegative scenario edge minutes plus `beta × routed edge km`, then add one home access allowance. Defaults: beta 0.2 min/km, condo 5 minutes, landed 0. Both are adjustable.
- **Alternatives:** Choose the base-time route and only then buffer it; penalize straight-line distance; produce a separate residence score; call the buffer a statistical percentile.
- **Rationale:** The user wants one planning duration reflecting the modelled components. Including the allowance during route selection can change the best entrance. Routed distance is the distance exposure of the chosen path.
- **Consequence:** The base Sungai Buloh and Rawang examples are 48 and 40 minutes; at default assumed distances/buffer they are 54 and 47.6. The linear buffer is not calibrated variance or an arrival probability and cannot claim to capture all risks. Home overhead is fixed per endpoint, including outbound arrival; it is added once. Workplace overhead is unmodelled.

## D016 — Use one exact workplace search and full grid as the default

- **Status:** Implemented; fixture comparison supports the choice.
- **Decision:** Run Dijkstra once per workplace/direction/policy, reversing adjacency for inbound travel. Query all centres by default on the small available graph. Keep uniform and adaptive options for the expensive-oracle experiment.
- **Alternatives:** Repeated point-to-point searches; force an adaptive method as default; choose an entrance from first-leg distance alone.
- **Rationale:** A complete nonnegative static graph supports exact one-workplace search. Batch and repeated routes agree; sparse uniform mean agreement (97.82%) exceeded this adaptive method (95.38%) at 256 queries across 18 fixed cases.
- **Consequence:** No claim that fewer lookups beat exact graph routing or that the selected method is universally best. Report index work, model queries and six example lookups separately; paid API calls are zero. Private home access cannot serve as an intermediate shortcut.

## D017 — Represent coarse/fine accessibility by explicit cells

- **Status:** Implemented and tested at model centres.
- **Decision:** Use a 32 × 32 km schematic, 16/32/64 centres per axis, and 4 × 4 initial major blocks for adaptive sampling. Interpolate from usable observed corners; direct observations override interpolation. Extract cell boundaries by shared-side cancellation.
- **Alternatives:** One duration per suburb; excessive smoothing; assume all-equal corners imply a uniform interior; introduce Marching Squares before a simple boundary works.
- **Rationale:** Small modules make local access costs, query budgets and failure cases inspectable. Unsmooth outlines preserve grid-supported pockets and holes.
- **Consequence:** Resolution is 2 km/1 km/500 m, not the original live V1's proposed 100 m target. Cells approximate their centres; no real street-level guarantee. GeoJSON includes synthetic provenance, coverage and possible domain truncation. Sparse sampling can still miss pockets and unseen disconnected access.

## D018 — Keep the demo local and record verification limits

- **Status:** Implemented; automated checks pass; real browser verification open.
- **Decision:** Use the Python standard library server on loopback, vanilla JavaScript/canvas, no runtime package or routing key, and optional Node tests without npm dependencies.
- **Alternatives:** Start a large frontend framework, deploy publicly, or let browser availability block all completion work.
- **Rationale:** The objective is an inspectable algorithm MVP. The available cloud browser cannot access the loopback server; a DOM/canvas test double allows interaction-logic tests against the real API while keeping the rendering gap explicit.
- **Consequence:** 47 Python tests and 6 JavaScript tests pass. Installation was checked independently. Visual layout and native browser downloads remain unverified, so UI TESTED remains PARTIAL. Invalid huge numbers and stale settings/export races have regression coverage. No publication, account setup or public exposure was added.

## D019 — Add a frozen bounded OSM case, keep its assumptions explicit

- **Status:** Implemented and checked after the user's continuation request.
- **Decision:** Bundle an attributed ODbL road snapshot around KLCC/Jalan Tun Razak, with a source timestamp, exact Overpass query and checksums. Evaluate retained road nodes at fixed assumed class speeds plus the existing distance allowance. Keep the synthetic UI separate; expose the road case through the CLI, point GeoJSON and a reproducible report.
- **Alternatives:** Remain entirely synthetic; require a commercial traffic account; silently treat nearby road nodes as verified home entrances; infer a residential contour from unvalidated access.
- **Rationale:** Real geometry tests directional/local-access behavior while preserving offline reproducibility and avoiding a traffic-quality claim. The chosen 10-minute threshold fits this small local experiment; it does not replace the original V1's 45-minute example.
- **Consequence:** 12,645 retained nodes and 20,106 directed segments. No heading or building overhead at endpoints. Routes are deliberately bounded by the extract; outside detours, actual entrance validation and live times remain unresolved. Counts depend on OSM node density. The 74 m nearby-node illustration is exploratory, not held out. Source data has an explicit licence; software licence/public release remain separate decisions.

## D020 — Remember route history and fail closed on unsupported restrictions

- **Status:** Implemented with independent routing checks.
- **Decision:** Compile supported via-node/via-way `no_*` and `only_*` restrictions into forbidden directed-edge sequences. Track the previous edge and relevant prefix history in Dijkstra states. For inbound search reverse both traversal and restriction sequences. Explicitly prohibit immediate segment reversals as a conservative assumption. Close known approaches for ambiguous/incomplete/unsupported relations; record every fallback.
- **Alternatives:** Ignore turn restrictions; use node-only Dijkstra; remember only the last edge; interpret an only-turn rule solely at its last segment; claim complete OSM support.
- **Rationale:** Allowed future turns depend on how the current location was reached. The snapshot resolves 291 of 342 relations; the remaining 51 require recorded fallback, removing 109 directed segments. Unsupported semantics must not silently become permitted manoeuvres.
- **Consequence:** 24 new tests cover import and restriction semantics. An independent uncompressed-history/Bellman–Ford solver agrees on 240 comparisons across 24 seeded graphs, both directions. Turning off compiled restrictions alone puts 202 inbound and 180 outbound nodes incorrectly inside the 10-minute model limit. These are implementation/model checks, not on-road validation. UNDERSTOOD remains unverified.

## Change log

| Date | Change | Evidence / consequence |
| --- | --- | --- |
| 2026-09-17 | Initialized the Stage 0 decision log. | Based on both identical uploaded instruction copies and the current Work Mode handoff. No previous repository files existed. |
| 2026-09-17 | Added the Stage 1 comparison and conditional TomTom pilot recommendation. | Official capability/price sources reviewed; current Mapbox Product Terms changed the initial technical preference. TomTom agreement, account access, and local quality remain unresolved. |
| 2026-09-17 | Added the accepted offline algorithm milestone, D013. | User clarified the Year 2 mathematics portfolio objective and instructed continuation after the recommendation. Directed-graph lesson prepared; implementation and understanding remain unverified. |
| 2026-09-18 | Completed offline MVP and verification, D014–D018. | User explicitly requested autonomous build/debug; exact routing, additive planning time, grid algorithms, local demo, 47 Python and 6 frontend tests, package check. Browser rendering remains open. |
| 2026-09-18 | Added bounded OSM case and turn-history routing, D019–D020. | Frozen attributed data, static assumptions, 24 additional tests, both-direction results, restriction ablation and visually reviewed route maps; no live traffic or verified residential access claim. |
