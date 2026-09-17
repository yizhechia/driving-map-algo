# Map Algorithm — Decisions

Updated: 2026-09-17. Stage 1 research; no implementation.

**Established** means required by the user's formal instructions or Work Mode handoff. **Proposed** means a concrete Stage 0 recommendation that has not yet been validated through implementation or the user's reasoning. **Deferred** means no selection has been made. A documented decision is not evidence that the user has mastered the concept.

## D001 — Establish the problem before building

- **Status:** Established.
- **Decision:** The initial work session completed Stage 0 documentation only. Keep the repository as persistent project memory and advance sequentially. The user's subsequent instruction to continue permits Stage 1 research.
- **Alternatives:** Start routing calls immediately; build a frontend first; leave scope only in chat.
- **Rationale:** The project needs an explicit question, input/output contract, and evaluation targets before technology choices.
- **Consequence:** No routing code, frontend, model, provider selection, package scaffold, or API calls in Stage 0. The next stage is research.

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
- **Also deferred:** Language/framework, CRS implementation, database, cache lifetime, sampling/refinement method, contour library, test coordinates, and open-source licence.
- **Consequence:** Provider research is now documented, but no implementation or routing validation has occurred. Retention, redistribution, and public examples must follow the verified terms of the selected data source.

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
- **Consequence:** Use synthetic cases for deterministic failure tests and respect verified retention rules for provider results. No API client, cache, sampling algorithm, or frontend is created before the user reasons through the relevant concepts.

## Change log

| Date | Change | Evidence / consequence |
| --- | --- | --- |
| 2026-09-17 | Initialized the Stage 0 decision log. | Based on both identical uploaded instruction copies and the current Work Mode handoff. No previous repository files existed. |
| 2026-09-17 | Added the Stage 1 comparison and conditional TomTom pilot recommendation. | Official capability/price sources reviewed; current Mapbox Product Terms changed the initial technical preference. TomTom agreement, account access, and local quality remain unresolved. |
