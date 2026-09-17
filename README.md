# Map Algorithm

Fine-grained driving commute accessibility for Klang Valley.

**Current status: Stage 0 — Problem Definition.** This repository contains project documentation only. No routing provider, implementation stack, or boundary-generation method has been selected; no working application or performance results exist yet. An open-source release is a future goal.

## The question

> Given my workplace, a driving-time limit, a departure time, and a direction, which residential access locations fit my commute constraint?

Two homes on opposite sides of a road can have different access to turns, estate exits, ramps, and congested feeder roads. A suburb label or a distance circle can hide those differences. Home-to-work and work-to-home travel also need separate calculations.

## Planned V1

- One workplace, one commute threshold, one explicit departure timestamp, one direction, and a bounded Klang Valley study area per run.
- Traffic-aware point-to-point duration estimates from a provider selected after research.
- Our own spatial sampling and contour generation, with holes, disconnected regions, and unresolved areas represented honestly.
- Geographic outputs supported by sampled durations, query settings, cost accounting, and validation evidence.

V1 estimates accessibility under provider-predicted travel times. It does not establish actual journey reliability. Reliability statistics, bottleneck attribution, a polished frontend, and release packaging belong to later stages.

## Project documents

| Document | Purpose |
| --- | --- |
| [Project brief](PROJECT_BRIEF.md) | Problem, V1 inputs/outputs, mathematics, non-goals, unknowns, and proposed acceptance criteria. |
| [Project state](PROJECT_STATE.md) | Current stage, actual progress, separate build/test/understanding/documentation status, and next actions. |
| [Decisions](DECISIONS.md) | Established requirements, proposed defaults, alternatives, and choices still deferred. |
| [Formal project instructions](docs/PROJECT_INSTRUCTIONS.md) | User-supplied staged workflow, engineering rules, and learning requirements. |

The next stage is routing and traffic-data investigation using current official sources. There are no installation or execution instructions yet because no software has been implemented.

## Development approach

The user is the primary developer. Before significant implementation, explain the problem, compare approaches, justify a recommendation, and check understanding. Then implement a small component, test it, and update the repository evidence.

Keep BUILT, TESTED, UNDERSTOOD, and DOCUMENTED separate. Never commit API keys. Provider data retention, redistribution, and attribution must follow verified terms before data is stored or shared. The project licence will be selected for release; none is asserted by this draft.
