# Stage 1 — Routing and Traffic Provider Review

Research date: **2026-09-17**. Scope: documentation research only; no routing queries, accounts, credentials, paid usage, or implementation.

**Recommendation: make TomTom Calculate Route the preferred technical candidate for the first point-to-point pilot. Keep the full V1 provider decision open until the applicable API agreement permits the intended use.** Mapbox initially looked attractive on functionality and cost, but its current Navigation API storage restriction conflicts with our evidence/replay design. TomTom's terms have not been established as more permissive; that is an unresolved condition, not a reason to assume permission.

## Evidence labels

- **CONFIRMED:** Stated in a retrieved official source. This establishes documented behaviour, not a successful test on our account or accuracy on a Klang Valley street.
- **INFERRED:** Our engineering interpretation or recommendation based on those facts.
- **UNKNOWN:** Not established by the sources or by a project experiment.

All sources linked below were accessed on the research date. Public prices are a snapshot, not an account quote. No numerical score is used to disguise missing evidence.

## 1. What the provider must supply

The essential requirements are driving routes in Klang Valley, explicit departure-time semantics, traffic information, correct endpoint order, and enough route/access evidence for a small pilot. Matrix support is useful for later efficiency; it is not required to understand the first point-to-point response.

Full V1 also needs a workable permission model for sampling, derived contours, retention, display, and evaluation. The licence for our own source code and the right to distribute a provider's results are separate questions.

These concepts must remain distinct:

| Concept | Meaning for this project |
| --- | --- |
| Routing engine | Software that finds a route on a road network. |
| Road data | Geometry, connectivity, road access, and restrictions. |
| Typical/historical traffic | A model of usual conditions by time; not a record of our actual journeys. |
| Live traffic | Information about current conditions where the provider observes or estimates them. |
| Future ETA | A prediction using the provider's traffic model; not knowledge of future incidents. |
| Actual duration | An observation from a completed journey, unavailable in this project so far. |

## 2. Country coverage and local quality

| Candidate | CONFIRMED official coverage evidence | What remains UNKNOWN |
| --- | --- | --- |
| Mapbox | Malaysia appears in the Directions guide's list for real-time and typical traffic. The guide describes fallback to typical conditions when live information is unavailable. [Traffic coverage](https://docs.mapbox.com/help/dive-deeper/directions/) | Coverage of each estate exit, feeder road, divided carriageway, and bottleneck; local ETA accuracy. |
| Google Routes | Google's Malaysia row lists driving directions and the traffic layer as available. This is country-level coverage evidence. [Coverage table](https://developers.google.com/maps/coverage) | Routes-specific behaviour and traffic quality at our exact pilot points; the traffic-layer entry alone is not a guarantee about every route segment. |
| TomTom | Malaysia is explicitly supported for Calculate Route with real-time traffic, and separately for Matrix Routing v2 with real-time traffic. [Route coverage](https://docs.tomtom.com/routing-api/documentation/tomtom-maps/v1/product-information/market-coverage), [Matrix coverage](https://docs.tomtom.com/matrix-routing-v2-api/documentation/product-information/market-coverage) | Fine-grained access and ETA quality for our selected examples. |

**INFERRED:** All three merit technical consideration. None has earned a claim of being most accurate in Klang Valley. That would require common-location experiments and eventually observed journeys.

## 3. Technical comparison

### Mapbox

**CONFIRMED:** Directions `driving-traffic` supports `depart_at`, combines historical information with live traffic near the present, and provides route geometry, snapped waypoints, and optional segment duration/congestion annotations. The documented request limit is 300/minute. These features make it technically attractive for access inspection. [Directions API](https://docs.mapbox.com/api/navigation/directions/)

**CONFIRMED:** Matrix supports selected origins/destinations, seconds-based durations, snapped points, and null results; it omits route geometry. Traffic requests allow 10 coordinates and 30 requests/minute. `depart_at` is labelled beta and requires signup. A single-element result is unsupported. Billing uses returned origin–destination elements. [Matrix API](https://docs.mapbox.com/api/navigation/matrix/)

**INFERRED:** For distinct points, a traffic request can contain nine homes plus the workplace. Configure only the needed direction. Do not assume the Directions endpoint's features or access rights automatically apply to Matrix. Keep its straight-line fallback disabled for commute classification; an estimated straight line is not a drivable route.

### Google Routes

**CONFIRMED:** `TRAFFIC_AWARE` and `TRAFFIC_AWARE_OPTIMAL` support future `departureTime`; omitting it uses request time. The latter performs a more exhaustive search with higher latency. [Traffic settings](https://developers.google.com/maps/documentation/routes/config_trade_offs-rm)

**CONFIRMED:** Compute Routes is charged per request; Compute Route Matrix per origin–destination element. Traffic-aware options trigger Pro pricing. Limits include 3,000 route requests/minute, 3,000 matrix elements/minute, and 100 elements per traffic-aware-optimal matrix; the general matrix maximum is 625. [Usage and billing](https://developers.google.com/maps/documentation/routes/usage-and-billing)

**CONFIRMED:** Route polylines are available; requesting traffic on polylines is a separate feature that can change the billed SKU. [Polyline options](https://developers.google.com/maps/documentation/routes/traffic_on_polylines) The route-modifier guide says Compute Route Matrix does not support avoidance features. Do not promise identical toll-policy control across endpoints without resolving this against the exact API request contract. [Avoidance guide](https://developers.google.com/maps/documentation/routes/route-modifiers)

**INFERRED:** A useful technical comparator, but not the default source for a freely exportable contour dataset under the reviewed standard conditions.

### TomTom

**CONFIRMED:** Calculate Route exposes `departAt`, `traffic`, route geometry, effective settings, and optional traffic sections. `computeTravelTimeFor=all` supplies additional no-traffic, historical, and live-duration fields. `traffic=false` changes routing treatment of current traffic; it must not be interpreted as a guaranteed free-flow response. The `fastest` preference also considers route sensibility, so it is not proof of the mathematical global minimum. [Calculate Route](https://docs.tomtom.com/routing-api/documentation/tomtom-maps/v1/calculate-route)

**CONFIRMED:** Matrix v2 allows future departure timestamps and explicit `historical`/`live` modes. Its default `departAt=any` is unsuitable for our fixed-time question. `now` refers to each cell's processing time. Ordinary synchronous sizes of 100/200 cells are documented, with a 400 km square bound for the larger size under our timed settings. The 2,500-cell option has enterprise and untimed historical restrictions. [Synchronous Matrix](https://docs.tomtom.com/matrix-routing-v2-api/documentation/synchronous-matrix)

**INFERRED:** Start with individual routes to inspect access and time semantics. Consider Matrix only after comparing it with the point-to-point endpoint under equivalent settings. This does not establish that the endpoints always return identical durations.

## 4. Free allowances, pricing, and query economics

| Provider / endpoint | CONFIRMED public allowance | CONFIRMED first paid tier | Basis / limitation |
| --- | --- | --- | --- |
| Mapbox Directions | 100,000 requests/month | USD 2 per 1,000 requests | Published list; account eligibility and remaining allowance not checked. [Pricing](https://www.mapbox.com/pricing) |
| Mapbox Matrix | 100,000 elements/month | USD 2 per 1,000 elements | Not the same unit as requests. [Pricing](https://www.mapbox.com/pricing) |
| Google Compute Routes Pro | 5,000 billable events/month | USD 10 per 1,000 requests | Traffic-aware baseline, excluding extra Enterprise features. [Pricing](https://developers.google.com/maps/billing-and-pricing/pricing) |
| Google Compute Route Matrix Pro | 5,000 billable events/month | USD 10 per 1,000 elements | Separate SKU allowance; not 5,000 matrices. [Pricing](https://developers.google.com/maps/billing-and-pricing/pricing) |
| TomTom Routing | Pricing page displays 20,000/month | UNKNOWN from retrieved pricing text | The page offers evaluation usage; confirm the actual account's plan and units. [Pricing](https://docs.tomtom.com/pricing) |
| TomTom Matrix | Pricing page displays 2,500/month | UNKNOWN from retrieved pricing text | Apply the matrix transaction rules, not HTTP request count. [Pricing](https://docs.tomtom.com/pricing) |

Do not reuse older TomTom daily-quota descriptions as today's verified account entitlement. Its current page uses monthly figures. Applicable rate limits, paid rates, and the user's available allowance remain UNKNOWN.

For TomTom, **CONFIRMED:** when either matrix dimension is at most five, charged transactions equal origins times destinations. Its discount formula only changes that when both dimensions exceed five. No-route and map-matching failures can be charged. [Transaction accounting](https://docs.tomtom.com/matrix-routing-v2-api/documentation/discounted-transaction-billing)

**Derived example:** 1,000 homes to one workplace require 1,000 useful route pairs, not a million home-to-home pairs. A square matrix over the 1,001 combined points would request 1,002,001 cells before provider batching limits. That is wasted calculation for this question, even where the provider discounts billing. Track useful pairs, requested cells, billable units, and requests separately.

The pilot below proposes at most 20 request attempts, including retries. This is our proposed experiment cap, not a provider quota or authorization to incur charges.

## 5. Licensing and reproducibility: material findings

### Mapbox: a confirmed storage restriction

**CONFIRMED:** The official Product Terms dated July 21, 2026, section 2.10.1, prohibit export, download, caching, and storage of Navigation API results. Sections 1.5, 1.6, and 1.9 also restrict certain derivative/competitive uses, extraction, and automated access. Section 1.2.3 requires an additional commercial licence for production use in specified categories including analytics and real estate. [Official Product Terms portal](https://www.mapbox.com/legal/product-terms), [linked July 2026 PDF](https://cdn.prod.website-files.com/609ed46055e27a02ffc0749b/6a60463142f6478d57642594_Mapbox%20Product%20Terms%20%28July%2021%2C%202026%29.pdf)

**INFERRED:** Standard terms do not support our planned retained routing evidence/replay workflow. Permission for custom sampling and derived contour exports is not established. A generous free allowance does not resolve that mismatch. Do not infer permission from another customer's implementation or from Mapbox's own isochrone product.

Verification note: the PDF was downloaded through the exact link on the official portal after the web text reader failed. Pages 1, 3, and 8 contain the relevant provisions. SHA-256: `8462b80946abe90c4996577262928c7987ec2066e464c997869c4d82ebb9ec1c`. The PDF itself is not redistributed in this repository.

### Google: constrained content use

**CONFIRMED:** Routes policies require Google Maps when results are displayed on a map. [Policies](https://developers.google.com/maps/documentation/routes/policies) The general terms restrict caching, extraction, and creating content from Google Maps content. [General terms, §3.2.3](https://cloud.google.com/maps-platform/terms) Routes-specific terms permit temporary caching of returned latitude/longitude for 30 days; that is not a blanket permission to retain travel-time matrices. [Service terms, §19](https://cloud.google.com/maps-platform/terms/maps-service-terms)

**INFERRED:** Do not adopt Google as the source for freely retained and redistributed contour/ETA evidence without establishing an applicable permission. Merely using a Google basemap would not resolve every issue.

### TomTom: agreement unresolved

**UNKNOWN:** The linked developer terms page returned navigation/footer content without the API agreement, through both web extraction and a direct HTML read. The older developer terms URL redirected there. The general consumer website terms are not a substitute. Retention, derived polygons, public examples, attribution, and display rights therefore remain unverified. [Developer terms entrypoint](https://docs.tomtom.com/legal/terms-and-conditions)

**INFERRED:** Prefer TomTom for the next technical investigation because of its documented route and timed-matrix capabilities, but do not treat this as legal clearance or a final full-V1 selection. Obtain the agreement applicable to the account, then evaluate the intended operations explicitly. No provider has been contacted and no terms have been accepted on the user's behalf.

### Consequence for open-source work

The algorithm source and synthetic examples can be developed independently. Provider outputs need their own permission assessment. Do not silently remove caching/evidence requirements from the brief to make a provider seem suitable. If no compatible traffic source is available, discuss an explicit scope or data-source change; a static OSM demonstration must not be labelled a traffic-aware V1.

## 6. Open-source candidates screened

These alternatives solve parts of the stack. None has yet supplied this project with a verified, licensed Klang Valley traffic feed.

| Candidate | CONFIRMED capability | INFERRED role / UNKNOWN requirement |
| --- | --- | --- |
| OpenRouteService | Global directions and asymmetric time-distance matrices are documented. [Services](https://openrouteservice.org/services/) | Candidate for baseline experiments. A current usable Klang Valley traffic feed was not established; do not equate a routing profile with traffic observations. Hosted quotas and licence fit need a dedicated check if chosen. |
| OSRM | Open-source route and table services are available; its documented API includes durations and route geometry. [Project](https://github.com/Project-OSRM/osrm-backend), [API reference v5.24.0](https://project-osrm.org/docs/v5.24.0/api/) | Potential controllable baseline. The versioned reference is not evidence of the latest release or a hosted Malaysian traffic service. Traffic sourcing and operating costs are separate. |
| Valhalla | MIT-licensed engine with time-aware routing and matrices; supports integrating historical and live traffic. [Project documentation](https://valhalla.github.io/valhalla/), [Traffic integration](https://valhalla.github.io/valhalla/concepts/historical-traffic/) | Strong later research option if we acquire suitable traffic data. Engine support does not supply the feed or remove ingestion/hosting work. |
| GraphHopper | An open-source routing engine is available under Apache 2.0. [Open-source project](https://www.graphhopper.com/open-source/) | Keep as a baseline/engine option. Hosted traffic availability and Malaysian coverage were not established by the retrieved documentation. |
| OpenStreetMap | Its database uses ODbL with attribution obligations. [Copyright and licence](https://www.openstreetmap.org/copyright) | Road-network source, not a standalone traffic-aware routing API. Engine, traffic, hosting, and licence obligations remain separate choices. |

**INFERRED:** Self-hosting now would add substantial data and operations work before we test the project's core question. It is a later option, not a free substitute for a traffic provider. No open-source engine has been selected or installed.

## 7. Recommendation and unresolved decisions

1. **Preferred technical candidate:** TomTom Calculate Route for the small Stage 2 pilot, conditional on applicable agreement and account access. Its timed matrix endpoint offers a plausible later path.
2. **Mapbox:** retain as a technically useful alternative if suitable permissions are obtained; do not implement retained responses under the reviewed standard restriction.
3. **Google:** retain as a possible permitted comparator; address content-use and map-display constraints before use.
4. **Open-source engines:** preserve as baseline or future architecture options without downgrading the traffic-aware goal.

| Question | Status | Evidence needed |
| --- | --- | --- |
| Can the selected data source support retained evidence and our custom contours? | UNKNOWN for TomTom; material constraints confirmed elsewhere | Applicable API agreement or provider clarification covering sampling, retention, derived output, and release. |
| Does the user's account have access, quota, and a zero-charge pilot allowance? | UNKNOWN | Account entitlements and metering; do not put credentials in chat or Git. |
| Is the selected product version suitable? | UNKNOWN on account | Confirm availability of TomTom Maps Routing v1 and Matrix v2; do not transfer these findings to Orbis endpoints without checking. |
| Is fine-grained Klang Valley routing useful? | UNKNOWN empirically | The pilot below, followed by Stage 4 access-pair cases. |
| Can live runs be reproduced exactly? | Not established | Frozen lawful fixtures; otherwise synthetic deterministic tests and timestamped live limitations. |
| Are the 100 m / 95% / 200-point targets feasible? | Still proposed | Initial cost/coverage evidence; no targets changed during this research. |

## 8. Small Stage 2 pilot plan — not executed

**Learning goal:** explain what each request means before writing the client. The formal instructions require the user's reasoning before important implementation; that checkpoint remains open.

Proposed pilot inputs are one verified KLCC driving entrance and two nearby residential access points, preferably with contrasting access. Exact coordinates are not yet chosen. Use two future weekday departure instants, provisionally 08:00 and 18:00 in `Asia/Kuala_Lumpur`, both directions, driving mode, and an explicit toll policy. These are experiment proposals, not assumed user preferences.

This creates eight semantic cases: two homes × two times × two directions. The purpose is to inspect requests and responses, not to prove one direction or time must always be slower.

| Step | What we learn / inspect |
| --- | --- |
| Explain and check understanding | Fixed departure versus arrival deadline; directed endpoints; typical prediction versus observation. |
| Resolve the provider-use questions | Read the applicable API agreement and confirm the pilot's permitted output handling. |
| Inspect one route first | Units, timestamps, status, route geometry, effective options, and whether requested entrances match plausible road access. |
| Complete the eight cases | Preserve the requested direction/time; compare route access and traffic fields. Equal ETAs do not by themselves indicate a bug. |
| Repeat two cases if permitted | Reveal prediction drift and what the provider does or does not expose about snapshot/version. |
| Verify failures offline | Model malformed input, no route, timeout, authentication failure, and missing fields distinctly using synthetic responses. |
| Record a pilot verdict | Working, partially working, or unsuitable, with observed evidence and no claim of actual commute accuracy. |

Use a proposed hard cap of **20 attempts total including retries**; start sequentially. Verify account rate limits before querying. Do not implement persistent response caching until its rules are established. Access inspection should use available snapped/geometry endpoints; if snap evidence is unavailable, report that limitation explicitly.

No grid, contour extraction, frontend, reliability model, or broad benchmark belongs in this pilot. The next learning question is: **If a provider forecasts 38 minutes for one future departure, what would still be needed to claim a 90% chance of arriving within 45 minutes?**
