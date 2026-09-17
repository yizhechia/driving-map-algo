# Map Algorithm — Project State

Updated: 2026-09-17.

## Current position

- **Current stage:** Stage 0 — Problem Definition.
- **Current objective:** Establish a reviewable specification before provider research or implementation.
- **Outcome:** Stage 0 documentation drafted. Numerical targets and new contract defaults remain proposals; user understanding has not yet been checked.
- **Repository:** `yizhechia/driving-map-algo`; default branch `main`. GitHub reported the repository empty with no branches at the initial inspection. Repository visibility was private; public release is a future goal.
- **Working context:** `00 | Planning`. Read this file, `PROJECT_BRIEF.md`, and `DECISIONS.md` when resuming; the formal instructions are preserved in `docs/PROJECT_INSTRUCTIONS.md`.

## What we are building

A Klang Valley commute accessibility engine that takes one workplace, threshold, explicit departure time, direction, and study area. It queries traffic-aware driving durations for specific access points and uses our own sampling and contour algorithm to estimate the feasible region. It must reveal local access differences where the data and sampling support them.

V1 produces inspectable geographic outputs and supporting evidence. A routing provider, algorithm, stack, and precise pilot location have not been selected. Reliability, bottleneck attribution, and a frontend are later work.

## Completed in Stage 0

| Deliverable | Location | Current evidence |
| --- | --- | --- |
| Formal problem statement | `PROJECT_BRIEF.md` §1 | A bounded, directed, traffic-aware access problem. |
| V1 user story | `PROJECT_BRIEF.md` §2 | One workplace/threshold/departure/direction per run. |
| Precise inputs | `PROJECT_BRIEF.md` §3 | Coordinate, time, policy, domain, sampling, and budget contracts. |
| Precise outputs | `PROJECT_BRIEF.md` §4 | Geometry, sample evidence, unknown coverage, provenance, and diagnostics. |
| Mathematical formulation | `PROJECT_BRIEF.md` §5 | Directional ETA set, finite-sample approximation, and clearly deferred reliability target. |
| Explicit non-goals | `PROJECT_BRIEF.md` §6 | No routing implementation, frontend, ML, reliability, or provider selection now. |
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
| Stage 1 provider investigation | NO | NO | NO | NO | Candidate names and research questions only; no provider facts researched. |
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
- No routing API calls, provider comparisons, executable project code, automated software tests, benchmarks, or commute measurements exist.

## In progress / unresolved

- **Learning:** The user has not yet demonstrated the Stage 0 time-and-direction distinction.
- **Proposals:** Departure-time semantics, output contract details, and numerical acceptance targets await discussion and later feasibility evidence.
- **Stage 1 questions:** Traffic coverage, API semantics, limits/cost, output/caching permissions, and reproducibility are all UNKNOWN. These are planned research questions, not access failures.
- **Before Stage 2:** Need exact workplace entrance, pilot bounds, departure date/time, toll policy, usable credentials, and a finite query budget after a provider is chosen.
- **No current implementation blocker needs resolution in this turn:** Stage 0 intentionally stops at documentation.

## Learning checkpoint

**Prompt to answer next:** Suppose we sample homes A and B for a home-to-KLCC run at 08:00. What is held fixed for both requests? Why would “arrive at KLCC by 09:00” be a different problem, and why would querying KLCC-to-home fail to answer the original question?

**Status:** Not answered. UNDERSTOOD remains NO until the user reasons through it. If the answer is partial, record PARTIAL and revisit the specific misconception. Future graph, GIS, sampling, and probability concepts are also unassessed.

## Highest-value next actions

1. Discuss the concrete Stage 0 specification and complete the short time/direction checkpoint; update only statuses supported by the user's answer.
2. When the user asks to begin Stage 1, investigate suitable routing/traffic sources with current official documentation. Label claims CONFIRMED / INFERRED / UNKNOWN, and record citations and access dates.
3. Recommend an initial provider only after that investigation; document alternatives and consequences. Revisit proposed numerical targets if the evidence requires it.
4. Do not implement the Stage 2 prototype until the relevant approach has been explained and the user's understanding checked, as required by the formal instructions.

No Stage 1 research or implementation is authorized by this Stage 0-only turn.

## Update discipline

At each meaningful change, record what changed, the evidence supporting status changes, unresolved questions, and the next action. Keep the stable specification in `PROJECT_BRIEF.md` and decision rationale in `DECISIONS.md`. A chat handoff should point to these files rather than substitute for reading them.
