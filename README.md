# Commute Lab · Map Algorithm

An offline algorithm MVP for comparing complete commutes in Klang Valley: main corridor, local access roads, building access, and a distance allowance, combined into **one planning time**.

**Working prototype:** Python routing engine, interactive local demo, three sampling methods, GeoJSON export, and reproducible tests. All road connections, distances, and times are synthetic examples. This is not a live traffic map or a calibrated reliability model.

## Run the demo

Requires Python 3.10 or newer. No API key, account, or third-party Python runtime package is needed.

```bash
git clone https://github.com/yizhechia/driving-map-algo.git
cd driving-map-algo
python -m commute_map serve
```

Open the address printed in the terminal (normally `http://127.0.0.1:8080`) in your browser. On systems that use `python3`, substitute that command. The repository is currently private, so cloning requires your existing GitHub access.

Use the controls to choose direction, threshold, assumed traffic scenario, distance allowance, and condo access time. Select a residence card or map cell to inspect the components and route. Under **Grid & sampling**, switch resolution or try a limited sampling budget. Export uses the settings of the displayed result.

If port 8080 is busy:

```bash
python -m commute_map serve --port 8090
```

## The model

For home `p`, direction `d`, and an assumed fixed traffic profile:

```math
T_{\mathrm{plan}}(p,d)=a_p+\min_{P\in\mathcal P_d(p)}\sum_{e\in P}\left(t_e+\beta\ell_e\right).
```

- `t_e`: corridor or local-road time in minutes under the selected scenario.
- `ell_e`: routed edge distance in kilometres; it is not straight-line distance.
- `beta`: assumed additional minutes per kilometre, adjustable from 0 to 5.
- `a_p`: home access allowance, default 5 minutes for a condo and 0 for a landed home. Applied once in either direction.

The buffer participates in route choice: a longer fast road can become less attractive when the buffer increases. Condo access is independent of the chosen route in this MVP. A point qualifies when its final planning time is at most the threshold. Missing or disconnected routes never become a zero-minute journey.

The distance allowance is a planning assumption. It is not a statistical estimate that all traffic conditions or risks are covered. Actual reliability requires journey observations and calibration.

## Your examples

Base scenario, KLCC → home, condo allowance 5 minutes:

| Residence | Corridor | Local roads | Home access | Assumed routed distance | With no distance buffer | With 0.2 min/km buffer |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Sungai Buloh inner estate | 30 | 18 | 0 | 30 km | 48 min | 54 min |
| Rawang near access | 35 | 5 | 0 | 38 km | 40 min | 47.6 min |
| Cheras inner estate | 22 | 20 | 0 | 21 km | 42 min | 46.2 min |
| Cheras condo | 22 | 4 | 5 | 18 km | 31 min | 34.6 min |

The first two corridor/local times come from the motivating user example. Distances and other fixture values are invented. Homes in the same area keep separate access costs. An additional example allows two entrances and changes its best route when the distance allowance is increased.

## Algorithms and results

- **Routing:** one priority-queue Dijkstra search from the workplace; use reversed edges for home → workplace. Homes are endpoints and cannot be used as shortcuts through private access.
- **Default grid:** query every cell centre in the available small synthetic graph. The 32 × 32 km schematic supports 16, 32, or 64 cells per axis. Each centre is one assumed access point.
- **Experimental sampling:** uniform lattice versus adaptive subdivision of 4 × 4 major blocks, using threshold proximity and sampled variation. Both use bilinear interpolation and retain unknown/no-route states.
- **Boundary:** cancel shared sides of qualifying cells. Keep holes and separate pockets; no smoothing. Export individual cell polygons and their outline, with coverage and study-edge metadata.

On the 18 fixed synthetic cases:

| Method | Samples per run | Mean classification agreement with the model |
| --- | ---: | ---: |
| Full scan | 1,024 | 100% at cell centres |
| Uniform | 256 | 97.82% |
| Adaptive | 256 | 95.38% |

Agreement counts unresolved routable cells as failures and includes queried centres. The [full report](docs/evaluation/MVP_RESULTS.md) also gives worst cases, disconnected-cell checks, and unqueried-point counts. The adaptive method can miss small reachable pockets. These results justify the current default, not a claim that one sampler is best on every network. Query savings here are simulated; the complete graph is already available and no paid API is called.

## Tests and command-line outputs

```bash
python -m unittest discover -s tests -v
python -m scripts.evaluate
python -m commute_map demo --buffer 0 --output outputs/example.json
python -m commute_map export --threshold 45 --output outputs/region.geojson
```

Optional frontend interaction-logic tests require Node 18 or newer, with no npm packages:

```bash
node --test tests/frontend.test.cjs
```

These tests launch an ephemeral local Python server. Set the `PYTHON` environment variable if your interpreter command differs. They run the actual JavaScript against the real API using a small DOM/canvas test double; they do not verify browser layout or native downloads.

Validation recorded on 2026-09-18: **47 Python tests and 6 frontend tests pass**, plus a wheel build and isolated installation check. Routing is also checked against independently implemented Floyd–Warshall on 30 seeded random directed graphs. See [verification details](docs/evaluation/MVP_VERIFICATION.md).

## Scope and next work

The local MVP is runnable. Visual browser verification remains incomplete: the available cloud browser blocked access to the loopback demo. The schematic is not a street map, and its approximate geographic export is not surveyed road data. Morning/evening profiles are fixed invented multipliers, not dated departure-time routing. Sparse results can miss access changes; cell interiors are approximations even with full sampling.

Live provider integration, real road-access validation, repeated journey observations, and calibrated risk remain future work. The original traffic-aware V1 criteria are preserved in the project brief and have not been met by this synthetic MVP. A public open-source release and licence selection are still pending.

## Project documents

| Document | Purpose |
| --- | --- |
| [Project state](PROJECT_STATE.md) | Current evidence, remaining work, and learning status. |
| [Project brief](PROJECT_BRIEF.md) | Current MVP scope and retained traffic-aware V1 target. |
| [Decisions](DECISIONS.md) | Choices, alternatives, rationale, and the authorized workflow change. |
| [MVP guide](docs/MVP_GUIDE.md) | Module map, mathematics, limitations, and walkthrough. |
| [Experiment plan](docs/evaluation/MVP_EXPERIMENT_PLAN.md) | Frozen comparison settings and default-selection rule. |
| [Results](docs/evaluation/MVP_RESULTS.md) | Reproducible outcomes and failure analysis. |
| [First learning exercise](docs/learning/OFFLINE_ALGORITHM_MILESTONE.md) | Directed-graph fundamentals; understanding is still unverified. |
| [Provider research](docs/research/ROUTING_PROVIDER_REVIEW.md) | Earlier official-source review; integration remains conditional. |
| [Formal instructions](docs/PROJECT_INSTRUCTIONS.md) | Preserved user-supplied instructions. |
