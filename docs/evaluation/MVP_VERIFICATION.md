# MVP verification record

Date: 2026-09-18. Version: 0.1.0. Offline synthetic model only.

## Executed checks

| Check | Result | Scope |
| --- | --- | --- |
| Python unittest discovery | 47 passed | Routing, input validation, grid budgets, interpolation, boundaries, unknown/no-route handling, HTTP and exports. |
| Node frontend tests | 6 passed | Actual application JavaScript and HTTP API; mocked DOM/canvas and download link. |
| Frozen spatial evaluation | 54 method-runs completed | 18 scenarios × three methods; no post-result algorithm tuning. |
| Batch routing comparison | All 256 homes agree in both directions | One workplace index versus repeated point searches. |
| Independent graph reference | Passed within routing suite | Floyd–Warshall on 30 seeded random directed graphs; private homes cannot be transit vertices. |
| Wheel build and isolated install | Passed | Import and runtime outside source directory; static assets present; model and export serialize. |
| Live provider calls | None | No credentials, paid requests, or observed commute evidence. |
| Browser rendering and native download | Not verified | Cloud browser rejected loopback navigation with `net::ERR_BLOCKED_BY_CLIENT`. |

Reproduce from the repository root:

```bash
python -m unittest discover -s tests -v
node --test tests/frontend.test.cjs
python -m scripts.evaluate
python -m commute_map demo --buffer 0 --output outputs/example.json
python -m commute_map export --output outputs/region.geojson
```

Node ≥18 is needed only for the optional frontend test command. It launches its own ephemeral Python server and uses no npm packages. Run `python -m commute_map serve` for the interactive demo.

## Bugs reproduced and corrected

**Huge numeric input.** Passing a 401-digit integer as `threshold` raised `OverflowError` during finite-number validation. Convert with an explicit overflow-to-validation-error boundary; HTTP now returns 400. App and server input regressions cover the case.

**Stale settings during a calculation.** If controls changed while a request was in flight, its response could re-enable export and report “Updated” for older settings. Compare current controls against the displayed result configuration before declaring it current or enabling export. The original result stays visible with “Settings changed” until applied.

**Stale settings during export.** The export completion handler used to re-enable its button unconditionally. It now checks whether controls still match the displayed run. Export always uses the displayed run's settings, even if controls are edited during the request.

**Study-edge interpretation.** A boundary at the study edge could look like a complete natural accessibility boundary. The UI and GeoJSON now report possible truncation. Export also retains coverage counts and states that omitted cells need not be inaccessible.

## Browser checks still open

The automated frontend tests execute drawing calls and reject nonfinite numeric drawing arguments. Their canvas is a test double: they cannot verify pixels, CSS, native browser form validation, responsive layout, or a downloaded file reaching disk.

In a real browser, check initial load; select all six cards; click a queried and an unqueried cell; change direction, traffic profile and allowances; try 64 × 64 and zero-budget sampling; inspect the page on a narrow screen; export and open GeoJSON; check for browser console errors. Record actual outcomes before marking UI TESTED = YES.

No failing executed tests remain. This is bounded verification evidence, not a claim that all possible inputs and browsers are error-free.
