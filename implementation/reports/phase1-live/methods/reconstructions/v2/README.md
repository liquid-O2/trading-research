# Phase 1 repaired source cases and native controls

This is the current reconstruction set. The [case-by-case visual review](../../CHART_VERIFICATION.md) covers 22 source records across all 12 methods and links the original images, interpretations and unavailable observations. [Completion evidence](../../COMPLETION_REPORT.md) reports software acceptance separately.

| Figure | What it establishes |
| --- | --- |
| [Green Bird sweep example](GB-FAIL-2025-11-20.png) | The displayed MNQ entry is at the sweep before later MSS/FVG annotations. Acquired NQ bars are a separate comparison; they are not an observed MNQ fill. |
| [Green Bird VWAP continuation](GB-VWAP-2026-02-24.png) | One frozen previous-18:00/HLC3 comparison, with source reset and price basis still unverified. [All 13 retained points](GB-VWAP-frozen-comparison.json) are recomputed without another search. |
| [Five dated profiles](JJ-profiles-2026-06-12.png) | Separate prior RTH, prior ETH, overnight, developing RTH and selected-range identities, full native price rows and unknown-side volume. |
| [Explicit composite](native-composite-2026-06-12.png) | Disjoint prior RTH and overnight snapshots: 498,476 + 104,734 = 603,210 contracts, with zero shared native event identities. |
| [Sires overnight binding](native-SIRES-overnight-2026-06-12.png) | O011 and O073 share the documented 18:00–09:30 window. The 40% fraction is sourced; undisclosed VA expansion and LVN selection remain unavailable. |
| [Range geometry](JJ-range-control-2026-02-24.png) | Both projections use the same frozen 06:00–09:00 range and its 107-point width. This is an explicit dated control. |
| [TPO and initial balance](native-TPO-IB-2026-06-12.png) | All 390 native minute bars and 13 declared 30-minute periods; source letter-window selection remains unverified. |
| [February flow](native-flow-2026-02-24.png), [June flow](native-flow-2026-06-12.png), [July flow](native-flow-2026-07-23.png) | Native execution rows, B buy/A sell/N unknown, exact footprints and two immutable snapshots of one five-minute candle. |
| [Sires loss and early-attempt context](SIRES-losses-2026-07-23.png) | All nine displayed attempts are retained, including five loss and four win labels. The conflicting caption is preserved; private fills and eligibility are unknown. |

The [source catalog](../../../../../src/trading_research/research/method_pack/source_cases_v2.json) distinguishes facts, inferences, conflicts and unknowns, including the original image reference and each case's visible timeframe. Some records are text or undated schematics. The source-only gallery does not imply a dated native match.

Four full profile windows have unresolved native trade-versus-minute reconciliation differences. Complete minute membership, known-side arithmetic and literal measurements remain available where supported. Neither missing depth/receive-sequence data nor source screenshots establish hidden orders, an automatic detector, a historical cohort or performance.

Rebuild from `/workspace` with the environment recorded in [the final test run](../../../../../validation/phase1-completion/test-run.json):

```bash
PYTHONPATH=implementation/src python implementation/tools/reconstruct_phase1_completion_cases.py --case all
PYTHONPATH=implementation/src python implementation/tools/validate_phase1_geometry_native.py
PYTHONPATH=implementation/src python implementation/tools/validate_phase1_flow_native.py
PYTHONPATH=implementation/src python implementation/tools/assemble_phase1_source_cases.py
PYTHONPATH=implementation/src python implementation/tools/plot_phase1_native_controls.py
PYTHONPATH=implementation/src python implementation/tools/review_phase1_completion_cases.py
```

The review program records the documented parent visual inspection; changing the computations or figures requires a fresh visual review. Its presence alone is not evidence that changed figures have been inspected. Stage 8 research remains deferred.
