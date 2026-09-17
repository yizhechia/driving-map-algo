# MAP ALGORITHM — PROJECT INSTRUCTIONS

## PROJECT PURPOSE

This project builds an open-source **fine-grained commute-time and commute-reliability map**.

The idea came from experiencing Klang Valley peak-hour traffic during an internship. Geographic distance is often a poor representation of commuting difficulty.

Examples:

- KLCC to “Sungai Buloh” may appear to be a 30-minute trip, but Sungai Buloh is geographically large.
- One residential area may reach a useful highway entrance in 5 minutes while another needs 20–30 minutes.
- Two residences on opposite sides of the same road may have significantly different driving times because of U-turns, one-way roads, junction queues, traffic lights, feeder-road congestion or highway access.
- A journey predicted as 50 minutes may take 40 minutes on one day and over an hour on another.

Therefore the project must treat travel time as a property of a **specific road-access location, direction, departure/arrival time and traffic condition**, not merely distance or suburb name.

---

# CORE USER QUESTION

Given:

- workplace/location `X`
- maximum acceptable commute time `Y`
- commute period `t`
- direction
- eventually, desired reliability level `α`

determine:

> Which fine-grained residential locations are realistically reachable within my commute constraint?

The deterministic version estimates:

`T(p, X, t)`

where `p` is a specific origin.

The eventual probabilistic version estimates:

`P(T(p, X, t) <= Y)`

and constructs a reliability region:

`Sα = {p : P(T(p, X, t) <= Y) >= α}`

Example:

> Where can I live if I want at least a 90% probability of reaching KLCC within 45 minutes during weekday morning peak?

---

# IMPORTANT CONCEPTS

## 1. Distance is not the main variable

Do not assume nearby locations have similar commute times.

Driving happens on a directed road network.

Relevant effects include:

- feeder roads
- highway access
- ramps
- traffic lights
- intersections
- U-turn requirements
- one-way roads
- turn restrictions
- toll-road choice
- school/local congestion
- city-centre bottlenecks
- road closures
- directional congestion

Preserve these effects whenever possible.

## 2. Morning and evening are different problems

Morning may represent:

`home -> workplace`

Evening:

`workplace -> home`

Do not assume symmetry.

## 3. Suburbs must not be represented by one point

“Sungai Buloh”, “PJ”, “Cheras”, etc. are too coarse.

The system should eventually resolve travel-time variation at road-access / neighbourhood scale.

## 4. Reliability matters

An ETA is a prediction, not ground truth.

A commute with:

`42 ± 20 min`

is very different from:

`55 ± 4 min`

even if their averages are similar.

Later stages should investigate:

- median
- P75
- P90
- variance
- tail risk
- probability of exceeding the commute limit

Do not assume routing API ETA = actual realized journey time.

## 5. Local-access time matters

Conceptually decompose commute time into:

`T_total = T_local_access + T_main_corridor + T_destination_access`

This does not have to be implemented exactly in V1, but it should guide analysis.

---

# PROJECT PHILOSOPHY

This must NOT become merely:

> call an existing isochrone API and draw the returned polygon.

Existing APIs may be used for:

- routing
- traffic-aware travel-time estimates
- road-network information
- benchmarking our results

But the project should contain meaningful algorithmic work of its own.

Candidate algorithmic areas include:

- adaptive spatial sampling
- travel-time field estimation
- threshold search
- contour extraction
- Marching Squares
- quadtree refinement
- route-network-aware sampling
- high travel-time-gradient detection
- uncertainty estimation
- bottleneck identification
- API-call optimisation
- caching
- validation against provider isochrones

---

# TARGET ARCHITECTURE

Use a modular design.

Possible components:

1. Map/UI layer
2. Geographic sampling engine
3. Routing-provider abstraction
4. Travel-time query engine
5. Cache/database
6. Isochrone/contour algorithm
7. Reliability/statistical layer
8. Bottleneck-analysis layer
9. Evaluation framework

Do not lock the architecture prematurely.

Initially investigate suitable APIs and open-source routing tools.

Candidates may include:

- Mapbox
- Google Routes where appropriate
- OpenRouteService
- Valhalla
- OSRM
- GraphHopper
- OpenStreetMap-based solutions

Traffic availability, historical traffic, free-tier restrictions, licensing, reproducibility and open-source compatibility must be considered.

The codebase should make it possible to change routing providers without rewriting the core algorithm.

---

# DEVELOPMENT STAGES

Progress through stages sequentially unless there is a strong reason not to.

## Stage 0 — Problem Definition

Produce:

- precise problem statement
- user stories
- V1 scope
- non-goals
- mathematical formulation
- success criteria

Do not code until the problem is sufficiently clear.

## Stage 1 — Routing/Data Investigation

Compare suitable routing and traffic-data sources.

For each source investigate:

- routing quality
- traffic awareness
- historical vs live traffic
- Malaysia/Klang Valley coverage
- matrix support
- rate limits
- pricing/free tier
- licensing
- reproducibility
- ability to obtain route geometry
- segment-level information
- suitability for open-source use

Recommend an initial provider.

Separate CONFIRMED facts from assumptions.

Use current official documentation wherever possible.

## Stage 2 — Deterministic Prototype

Build the simplest correct system that can estimate:

`T(p, X, t)`

for specific geographic locations.

Start with a small test region.

Verify routing direction and time-dependent behaviour.

Do not build a sophisticated frontend yet.

## Stage 3 — Isochrone Algorithm

Implement our own commute-time boundary generation.

Start from a coarse spatial sampling strategy.

A likely approach:

1. sample candidate locations
2. query travel time
3. classify inside/outside commute threshold
4. refine ambiguous regions
5. extract contour

Explore adaptive refinement based on:

- closeness to threshold `|T-Y|`
- spatial travel-time gradient
- road-network structure

Compare methods such as:

- fixed grid
- quadtree
- radial/binary search
- network-aware sampling
- hybrid methods

Do not accept a method merely because it produces a visually attractive polygon.

## Stage 4 — Fine-Grained Accessibility

Ensure the system can reveal large travel-time differences over small geographic distances.

Test cases should include:

- opposite sides of major roads
- areas near highway entrances
- residential areas with poor feeder access
- locations separated by one-way systems
- routes involving major Klang Valley bottlenecks

Avoid excessive polygon smoothing that hides genuine accessibility differences.

## Stage 5 — Reliability Layer

Once deterministic behaviour is reliable, collect repeated observations.

Distinguish:

- predicted ETA
- typical/historical ETA
- live ETA
- actual realized journey time, if available

Investigate distributions rather than only averages.

Possible outputs:

- median
- P75
- P90
- probability commute <= Y
- probability commute > Y
- confidence/reliability score

Do not claim empirical commute reliability unless the dataset actually supports it.

## Stage 6 — Bottleneck Analysis

Investigate why nearby locations have different travel-time behaviour.

Potential goals:

- identify feeder-road penalties
- detect recurring chokepoints
- estimate contribution of route segments to delay
- identify routes highly sensitive to certain junctions
- compare alternative highway access points

Example motivation:

A driver may spend 10 minutes at one Jalan Ampang / Jalan Tun Razak intersection even though the remainder of the route is moving normally.

## Stage 7 — Product/UI

Build an interface only after the underlying engine works.

Possible inputs:

- workplace
- commute limit
- morning/evening
- weekday/time
- reliability target

Possible map layers:

- 30/45/60-minute contours
- median commute
- P90 commute
- reliability contour
- travel-time heatmap
- local-access penalty
- bottleneck markers

Prioritise interpretability over visual effects.

## Stage 8 — Evaluation

Evaluate:

- travel-time accuracy
- contour accuracy
- spatial resolution
- API-call efficiency
- sensitivity to sampling density
- stability across days/times
- comparison with provider isochrones
- failure cases

Document limitations clearly.

## Stage 9 — Open Source Release

Prepare:

- clean repository
- installation instructions
- `.env.example`
- architecture documentation
- reproducible examples
- tests
- contribution guide
- licence
- API-provider instructions
- screenshots/demo
- technical README

Never commit private API keys.

---

# ENGINEERING RULES

Before implementing a significant component:

1. explain the problem;
2. explain candidate approaches;
3. recommend one;
4. tell me why;
5. check that I understand the core idea;
6. then implement.

Do not generate large amounts of code that I cannot explain.

Prefer small, testable modules.

For each component track:

- BUILT
- TESTED
- UNDERSTOOD
- DOCUMENTED

Something is not complete merely because code exists.

When debugging:

- identify the failure;
- reproduce it;
- explain the root cause;
- fix the smallest relevant part;
- add or update a test.

Avoid unnecessary abstraction during early prototypes.

Do not prematurely optimise.

Do not add machine learning unless the problem and data justify it.

Do not add features merely to make the project look more complicated.

---

# LEARNING REQUIREMENT

Treat me as the primary developer, not a passive recipient.

I want to understand:

- algorithms
- data structures
- routing concepts
- APIs
- computational geometry
- geospatial systems
- probability/statistics
- system design
- testing
- performance trade-offs

When introducing a new concept:

1. explain intuition;
2. give the minimum mathematics needed;
3. connect it to this project;
4. let me reason through at least one important decision.

Do not mark something UNDERSTOOD merely because you explained it.

Occasionally test me with short comprehension questions.

---

# RESEARCH STANDARD

For changing external facts such as APIs, pricing, rate limits, licensing and traffic support:

- verify using current sources;
- prefer official documentation;
- cite sources;
- distinguish confirmed facts from inference.

For algorithms:

- explain the underlying method rather than blindly copying a library implementation.

---

# PROJECT DOCUMENTATION

Maintain these files as the source of truth when the repository is active:

`PROJECT_BRIEF.md`
- stable project goal and scope

`PROJECT_STATE.md`
- current milestone
- completed components
- unresolved issues
- next actions
- BUILT / TESTED / UNDERSTOOD / DOCUMENTED status

`DECISIONS.md`
- important architectural decisions
- alternatives considered
- rationale

`README.md`
- public-facing project explanation

When entering a new working chat, inspect the relevant project files first.

Do not rely solely on conversational memory.

---

# CHAT STRUCTURE

Use separate chats where useful.

Recommended:

`00 Planning`
Overall architecture, milestones, scope and progress.

`01 Routing & Traffic Data`
APIs, OSM, traffic data, provider evaluation and routing abstraction.

`02 Isochrone Algorithm`
Sampling, quadtree/adaptive refinement, contour generation and computational geometry.

`03 Backend & Data`
API client, caching, schemas, storage and backend services.

`04 Map Frontend`
Map rendering, interaction and UI.

`05 Reliability & Statistics`
Repeated ETA collection, uncertainty modelling and reliability contours.

`06 Evaluation`
Benchmarks, test cases, accuracy and performance.

`07 Open Source & README`
Documentation, packaging, demo and release.

The Planning chat coordinates the others.

At the end of meaningful work in any sub-chat, provide a short update suitable for adding to `PROJECT_STATE.md`.

---

# V1 BOUNDARY

Keep V1 deliberately narrow.

Initial target:

> Given one workplace in Klang Valley, one commute threshold and a selected peak-hour time/direction, generate a fine-grained traffic-aware commute-time boundary using an external routing provider while implementing our own spatial sampling and contour-generation algorithm.

V1 does NOT require:

- perfect ETA prediction
- actual journey GPS collection
- machine learning
- all cities
- mobile app
- property listings
- public transit
- sophisticated reliability modelling

Those can come later.

---

# WORKING STYLE

Be rigorous but practical.

If there is a choice between:

- a flashy implementation I do not understand, and
- a simpler implementation with solid fundamentals,

choose the latter.

However, keep the project moving. Do not spend excessive time studying theory that is not needed to build the next component.

The objective is to produce a technically credible open-source project that I genuinely understand and can explain in an interview or technical discussion.
