# Commute Lab

A working offline algorithm MVP for fine-grained commute accessibility, inspired by Klang Valley.

**Data:** synthetic road connections, distances and traffic scenarios. This is an inspectable planning model, not a live navigation service or a calibrated reliability forecast.

## Run

Requires Python 3.10 or newer. The application and Python tests have no third-party runtime dependencies.

From the repository root:

~~~sh
python -m commute_map serve
~~~

Open http://127.0.0.1:8080 in your browser. If that port is occupied, use --port 8081. On Windows, py can replace python. Stop with Ctrl+C. The development server binds only to your own computer.

If you already have the repository checked out:

~~~sh
git fetch origin
git switch main
git pull --ff-only
~~~

## What it does

- Computes KLCC-to-home and home-to-KLCC separately on a directed graph.
- Combines main-corridor time, local-road time, home access, and an adjustable distance buffer into one planning time.
- Includes the user's Sungai Buloh example (30 + 18 = 48 minutes) and Rawang example (35 + 5 = 40 minutes), before buffers.
- Applies the configurable condo allowance once per home endpoint, initially 5 minutes.
- Chooses the route with the lowest complete planning time. A farther entrance can win, and changing the buffer can change the preferred entrance.
- Displays an 8 km major grid with finer 2 km, 1 km or 500 m cells, route details and boundary segments.
- Supports full, uniform and adaptive sampling. Estimated and unknown cells remain distinguishable.
- Exports GeoJSON with synthetic provenance, settings and sample status. Eligible cell polygons preserve gaps; no smooth polygon is invented across missing areas.

The distance buffer defaults to **0.2 extra minutes per routed kilometre**, an illustrative assumption. It is not inferred from observations and has no on-time probability attached. Road times already include the selected assumed profile; the extra buffer is an additional planning allowance. The demo does not claim to include every real traffic condition.

## Tests and developer comparison

~~~sh
python -m unittest discover -s tests -v
python -m scripts.evaluate
~~~

The 45-test suite covers the commute examples, directed routing, alternative entrances, condo overhead, changing buffer costs, disconnected points, invalid data, budgets, interpolation, boundary holes, and HTTP requests. An independent Floyd–Warshall reference checks 30 generated graphs.

The algorithm comparison is development evidence, not an extra product scoring system. In the original 18-case synthetic experiment, full scan agreed with all reference cell values; uniform sampling outperformed this particular adaptive method at the same 256-query budget. Full scan is therefore the default for the small available graph. See [the experiment design](docs/evaluation/MVP_EXPERIMENT_PLAN.md) and [verified results](docs/evaluation/MVP_RESULTS.md).

Optional browser tests require Node and Playwright:

~~~sh
npm install --no-save --package-lock=false playwright@1.58.2
npx playwright install chromium
node scripts/browser_smoke.cjs
~~~

GitHub Actions has passed the recovered source's 45 Python tests, browser interactions, algorithm comparison and package installation. [Verified run](https://github.com/yizhechia/driving-map-algo/actions/runs/35313293512). Browser screenshots, exports and the regenerated evaluation report are saved as workflow artifacts.

## Command-line outputs

~~~sh
python -m commute_map demo --buffer 0 --output outputs/example.json
python -m commute_map export --threshold 45 --output outputs/region.geojson
python -m commute_map demo --direction home_to_work --period morning --method adaptive --budget 256
~~~

Optional installation: python -m pip install . exposes the commute-map command. Running from the checkout does not require installation or an API key.

## Code map

| File | Purpose |
| --- | --- |
| commute_map/model.py | Validated graph and planning assumptions |
| commute_map/routing.py | Shared Dijkstra search and route reconstruction |
| commute_map/scenarios.py | Explicit synthetic fixtures and local access variation |
| commute_map/sampling.py | Query budget, uniform sampling and adaptive refinement |
| commute_map/contours.py | Shared-edge cancellation and GeoJSON export |
| commute_map/app.py | Input validation, computation and explanatory output |
| commute_map/server.py | Local HTTP server |
| commute_map/static/ | Interactive demo |
| tests/ | Concept, reference, geometry and HTTP tests |
| scripts/ | Algorithm comparison and browser smoke test |

## Limits and project state

This MVP does not satisfy the original traffic-aware V1. It has no routing-provider integration, measured congestion, verified building entrances, calibrated risk distribution, real turn restrictions, or real street-level validation. Morning/evening selections are static invented profiles, not dated departure-time predictions. GeoJSON uses an illustrative frame near KL; its geometry is not surveyed residential coverage.

The viewport is a schematic of a 32 km square. Each cell represents an assumed access point; colouring the whole cell approximates its centre. A fully sampled grid still does not prove every real location inside a cell is reachable.

The developer's conceptual understanding remains unverified. The user's latest instruction authorized implementation without waiting for learning prompts; explanations and exercises are retained for review.

- [Project brief](PROJECT_BRIEF.md)
- [Current state](PROJECT_STATE.md)
- [Decisions](DECISIONS.md)
- [Model and learning notes](docs/MVP_MODEL.md)
- [Provider investigation](docs/research/ROUTING_PROVIDER_REVIEW.md)
- [Formal instructions](docs/PROJECT_INSTRUCTIONS.md)

The repository remains private; a licence and public release are still future work.
