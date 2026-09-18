# Map Algorithm — Project State

Updated: 2026-09-18.

## Current objective and authority

Deliver a runnable offline algorithm MVP with concept tests and a local demo. The user explicitly expanded the task to autonomous implementation, debugging and test execution, requested corridor/local decomposition, a distance allowance inside the displayed time, condo access overhead, and asked not to wait for further learning prompts while asleep.

This latest instruction supersedes the earlier pause-before-implementation requirement for this work session. It does not establish conceptual mastery. UNDERSTOOD remains NO (unverified).

The original traffic-aware V1 remains a later target. Provider investigation is paused with unresolved terms/account questions. No commercial routing calls or actual travel measurements have been made.

## Implementation location

Delivery branch: mvp/offline-commute. The main branch is unchanged. Verified executable-source commit: 3c590e9ea1f75e3c418049e5a54dd4e625d09fa7.

The original workspace disconnected while browser verification was stalled. The core, local demo and tests were reconstructed from the recorded implementation and saved to GitHub. The recovered source independently passed GitHub Actions: 45 Python test methods, browser interaction/error/mobile checks, the full algorithm comparison, and package installation. Verified run: https://github.com/yizhechia/driving-map-algo/actions/runs/35313293512.

## Components

| Component | BUILT | TESTED | UNDERSTOOD | DOCUMENTED |
| --- | --- | --- | --- | --- |
| Directed static routing and additive planning costs | YES | YES | NO | YES |
| Synthetic KL examples and access variation | YES | YES | NO | YES |
| Full/uniform/adaptive sampling and query budgets | YES | YES | NO | YES |
| Grid boundary and GeoJSON output | YES | YES | NO | YES |
| Local API and interactive demo | YES | YES | NO | YES |
| Concept and independent-reference test suite | YES | YES | NO | YES |
| Browser checks and package verification | YES | YES | NO | YES |
| Live traffic integration and street-level validation | NO | NO | NO | PARTIAL |
| Empirical reliability or calibrated volatility | NO | NO | NO | PARTIAL |

TESTED means the recorded checks passed for the offline implementation; it is not a universal absence-of-bugs claim or real-traffic validation. The original local version passed 45 tests. The recovered source has now also passed all checks, including the browser tests that were incomplete before interruption.

## Implemented behaviour

- One final planning time: corridor + local roads + home access + assumed buffer per routed kilometre.
- Directions are separate. Static morning/evening profiles are labelled assumptions.
- Condo overhead is added once. Route selection includes the buffer.
- A shared workplace Dijkstra index replaces repeated route searches for the available fixed graph.
- Major blocks and finer cells retain point-specific access.
- Missing results, no-route and unqueried points retain distinct status.
- Full scan is the default; uniform and adaptive remain experimental.
- Python-only runtime, local server, command-line JSON/GeoJSON exports, optional browser test dependency.

## Evaluation evidence

The recovered-source CI reproduced the original fixed comparison: both directions × three assumed profiles × thresholds 40/45/60, 0.2 min/km buffer, 5-minute condo access, 32 × 32 grid.

Mean agreement with synthetic reference cell values: full 100%; uniform 97.82%; adaptive 95.38%. Uniform/adaptive used 256 queries; full used 1,024. These numbers include sampled cells. They do not measure real commute accuracy. See docs/evaluation/MVP_RESULTS.md and regenerate with python -m scripts.evaluate.

A missed-pocket test explains why matching corners are insufficient. Independent Floyd–Warshall checks cover 30 generated graphs; repeated point queries agree with the shared index in the local comparison.

## Next actions

1. Run the local demo with python -m commute_map serve and inspect the example routes.
2. Review the implementation with the user, one concept at a time, without assuming understanding.
3. When traffic integration becomes the priority, resolve applicable provider terms and exact entrance/time semantics before testing real routes.

## Important limits

No calibrated P90 or arrival probability. The distance coefficient is an adjustable assumption. All lengths and most route times are invented fixtures; the user's 30+18 and 35+5 examples are illustrative. The map is schematic. Static graph routing omits real turn restrictions and evolving traffic. The 500 m finest demo grid does not meet the original proposed 100 m target.

No numerical original V1 target has been declared achieved. No API credentials have been acquired or committed. Public release and licence selection remain future work.

## Promotion status

Automatic approval review rejected advancing main because development authorization did not explicitly include promoting the recovered implementation to the default branch. No retry or bypass was attempted. The tested feature branch is runnable and reviewable; main promotion requires explicit user authorization.
