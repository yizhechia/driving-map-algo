# Map Algorithm — Project State

Updated: 2026-09-17.

## Current position

- **Current stage:** Stage 1 — Routing & Traffic Data Investigation.
- **Current objective:** Establish a provider with both the technical capability and data-use permissions needed by the V1 design.
- **Outcome:** Initial official-source comparison documented. TomTom Calculate Route is the preferred technical candidate for a small pilot, conditional on applicable agreement and account access. No final full-V1 provider commitment or implementation.
- **Repository:** `yizhechia/driving-map-algo`; default branch `main`. GitHub reported the repository empty with no branches at the initial inspection. Repository visibility was private; public release is a future goal.
- **Working context:** `00 | Planning`. Read this file, `PROJECT_BRIEF.md`, and `DECISIONS.md` when resuming; the formal instructions are preserved in `docs/PROJECT_INSTRUCTIONS.md`.

## What we are building

A Klang Valley commute accessibility engine that takes one workplace, threshold, explicit departure time, direction, and study area. It queries traffic-aware driving durations for specific access points and uses our own sampling and contour algorithm to estimate the feasible region. It must reveal local access differences where the data and sampling support them.

V1 produces inspectable geographic outputs and supporting evidence. TomTom is the conditional technical recommendation, not an activated integration. The algorithm, stack, and precise pilot location remain undecided. Reliability, bottleneck attribution, and a frontend are later work.

## Completed in Stage 0

| Deliverable | Location | Current evidence |
| --- | --- | --- |
| Formal problem statement | `PROJECT_BRIEF.md` §1 | A bounded, directed, traffic-aware access problem. |
| V1 user story | `PROJECT_BRIEF.md` §2 | One workplace/threshold/departure/direction per run. |
| Precise inputs | `PROJECT_BRIEF.md` §3 | Coordinate, time, policy, domain, sampling, and budget contracts. |
| Precise outputs | `PROJECT_BRIEF.md` §4 | Geometry, sample evidence, unknown coverage, provenance, and diagnostics. |
| Mathematical formulation | `PROJECT_BRIEF.md` §5 | Directional ETA set, finite-sample approximation, and clearly deferred reliability target. |
| Explicit non-goals | `PROJECT_BRIEF.md` §6 | V1 exclusions and staged development scope are documented. |
| Technical unknowns | `PROJECT_BRIEF.md` §7 | Provider semantics, access validity, licensing, drift, and approximation risks. |
| Measurable success criteria | `PROJECT_BRIEF.md` §8 | Proposed C1–C8; no achieved results. |
| Initial repository structure | `PROJECT_BRIEF.md` §9 | Five documentation files; future source/test paths are suggestions only. |
| Decision rationale and alternatives | `DECISIONS.md` | Established constraints separated from proposed and deferred choices. |

The two uploaded Project Instructions files were byte-identical. The preserved copy changes only line-ending/final-newline formatting. Their source SHA-256 was `86100623ddc9236e6252f6311470001cbee38c82a784434774e76b04e08e7768`.

## Component status

Values are YES / PARTIAL / NO. For a documentation component, BUILT means the artifact exists; TESTED refers only to its documented consistency checks, never software tests. A NO for UNDERSTOOD means there is no demonstrated evidence yet, not that the user is assumed incapable of understanding it.

| Component | BUILT | TESTED | UNDERSTOOD | DOCUMENTED | Evidence / remaining work |
| --- | --- | --- | --- | --- | --- |
| Stage 0 specification and repo documentation | YES | PARTIAL | NO | YES | Draft exists; scope and content checks only. User reasoning and target feasibility remain unverified. |
| Stage 1 provider investigation | PARTIAL | NO | NO | YES | Official-source comparison and conditional recommendation exist; terms/account questions remain; no API behaviour tested. |
| Point-to-point routing prototype | NO | NO | NO | PARTIAL | Intended query contract defined; no client or observed responses. |
| Sampling and contour algorithm | NO | NO | NO | PARTIAL | Requirements and evaluation targets drafted; method not selected. |
| Fine-grained accessibility validation | NO | NO | NO | PARTIAL | Categories of access-pair test cases identified; no verified coordinates or measurements. |
| Reliability layer | NO | NO | NO | PARTIAL | Future objective and evidence limits defined; no data or model. |
| Bottleneck analysis | NO | NO | NO | PARTIAL | Motivation and future scope only. |
| Frontend / product | NO | NO | NO | NO | Deferred to Stage 7. |
| Evaluation framework | NO | NO | NO | PARTIAL | Proposed acceptance criteria; no test implementation or results. |
| Open-source release | NO | NO | NO | PARTIAL | Introductory README only; no software, licence selection, or release. |

**Application as a whole:** BUILT NO; TESTED NO; UNDERSTOOD NO (unverified); DOCUMENTED PARTIAL.

## Validation performed and limits

- Read the full uploaded formal instructions and the Work Mode handoff.
- Verified the attachment copies match and inspected repository metadata, root contents, and branches through the connected GitHub integration.
- Checked the documentation against the nine Stage 0 deliverables and the Stage 0-only boundary.
- Checked the distinction between departure time and arrival deadlines, inbound/outbound endpoints, unknown and outside, and predicted versus realized durations.
- Compared official provider documentation, country coverage, endpoint semantics, current public pricing, and available terms. Citations and evidence labels are in `docs/research/ROUTING_PROVIDER_REVIEW.md`.
- Retrieved Mapbox's linked July 21, 2026 Product Terms and checked the Navigation API storage restriction; the research records its section/page references and source hash.
- The TomTom developer terms page exposed no API agreement text through web extraction or direct HTML retrieval; permissions remain UNKNOWN.
- No routing API calls, executable project code, automated software tests, benchmarks, or commute measurements exist.

## Stage 1 findings

- **CONFIRMED in documentation:** the reviewed providers expose traffic/time-aware routing capabilities; the report records exact endpoint distinctions and country-level evidence.
- **Material issue:** retained routing evidence and exported contours require a compatible data-use permission model. Mapbox's reviewed terms explicitly restrict Navigation result storage. Google has separate storage/derived-content/display constraints.
- **INFERRED recommendation:** prioritize TomTom Calculate Route for the small pilot, pending its applicable API agreement and account entitlement. Its terms have not been verified as more permissive.
- **Planned experiment:** two access points × two departure times × two directions; one route inspected first; proposed cap of 20 attempts including retries. Nothing has been executed.
- **Scope:** screened OpenRouteService, OSRM, Valhalla, GraphHopper, and OpenStreetMap as engine/data/baseline options. No verified Klang Valley traffic feed has been acquired for them.

## In progress / unresolved

- **Learning:** The user has not yet demonstrated the Stage 0 time-and-direction distinction.
- **Proposals:** Departure-time semantics, output contract details, and numerical acceptance targets await discussion and later feasibility evidence.
- **Stage 1 questions:** TomTom API agreement, account-specific limits/pricing, retention/export rights, product-version access, and local routing quality remain unresolved. Documented country coverage is not street-level validation.
- **Before Stage 2:** Need exact workplace entrance, pilot bounds, departure date/time, toll policy, usable credentials, and a finite query budget after a provider is chosen.
- **Before implementation:** resolve the relevant provider-use conditions and complete the learning checkpoint required by the formal instructions. No credentials have been requested or exposed; no third party has been contacted.

## Learning checkpoint

**Original checkpoint, still unanswered:** Suppose we sample homes A and B for a home-to-KLCC run at 08:00. What is held fixed for both requests? Why would “arrive at KLCC by 09:00” be a different problem, and why would querying KLCC-to-home fail to answer the original question?

**Current short checkpoint:** If a provider forecasts 38 minutes for one future departure, what would still be needed to claim a 90% chance of arriving within 45 minutes?

**Status:** Not answered. UNDERSTOOD remains NO until the user reasons through it. If the answer is partial, record PARTIAL and revisit the specific misconception. Future graph, GIS, sampling, and probability concepts are also unassessed.

## Highest-value next actions

1. Discuss the conditional recommendation and complete the short learning checkpoint; update only statuses supported by the user's reasoning.
2. Obtain the TomTom API agreement applicable to the intended account through an accessible official source or a user-supplied copy; resolve sampling, retained evidence, derived contours, display, and redistribution. Do not substitute consumer terms or assumptions.
3. Confirm product access/allowance and choose one exact workplace entrance, two home access points, dates/times, toll policy, and a finite query cap for the documented pilot.
4. Explain the minimal client approach and check the user's time/direction reasoning before implementing Stage 2. Keep all larger components deferred.

The user's instruction to continue authorized this Stage 1 research. It did not answer the learning questions or establish provider account/data-use permissions. No numerical acceptance target has been relaxed.

## Update discipline

At each meaningful change, record what changed, the evidence supporting status changes, unresolved questions, and the next action. Keep the stable specification in `PROJECT_BRIEF.md` and decision rationale in `DECISIONS.md`. A chat handoff should point to these files rather than substitute for reading them.
