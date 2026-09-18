# Results recorded before the workspace interruption

The original local implementation passed 45 unittest methods on 2026-09-17. The independent routing test covered 30 seeded graphs, both directions and three home endpoints per graph. The local browser could not be installed; the later cloud-browser attempt stalled and the workspace disconnected.

The original fixed 18-case experiment printed:

| Method | Queries | Mean model agreement | Worst model agreement | Total unresolved eligible predictions |
| --- | ---: | ---: | ---: | ---: |
| Full scan | 1024 | 100.00% | 100.00% | 0 |
| Uniform | 256 | 97.82% | 95.07% | 126 |
| Adaptive | 256 | 95.38% | 82.46% | 685 |

These are deterministic synthetic reference results at grid centres, not actual commute accuracy. Sampled points are included. The original full raw file is unavailable with the offline workspace, so it has not been recreated from guessed values. Running scripts.evaluate regenerates the full comparison for the recovered source.

The recovered source must be verified separately; previous local success is not proof that reconstruction introduced no errors. See the branch's GitHub Actions checks.
