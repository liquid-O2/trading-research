# Research status

Phase 1 setup implementation and measurement are complete for the acquired observed-input population. Phase 1.5 subphase `00-foundation` is closed under assurance `research-assurance-2026-09-14-v2`. Phase 1.5 subphase `01-native-and-outcomes` is closed on the immutable receipts below. The earlier foundation v2 attempt `240838146c38c484` was rejected by the [2026-09-14 v2 review](/workspace/planning/research-program/reviews/00-foundation-v2-2026-09-14/REVIEW.md) and remains preserved. The original 2026-09-14 v1 completion also remains preserved as a rejected historical attempt. Later Phase 1.5 subphases and Phase 2 are specified and have not been executed.

## Phase 1 baseline

The accepted census searched **1,742 declared session dates**, 2020-01-01 through 2026-09-03: **99,294 daily jobs**, three collection-process jobs and **18,747 observed setups** across 50 branches and eight additional units. Branch overlap makes this an opportunity count, not an independent trade count.

The native input endpoint is 2026-09-03T06:09:59.901114+00:00, exclusive. September 3 is partial. Missing context, unknown ordering, same-contract gaps and other branch-specific input limits remain explicit. These are observed price outcomes, not simulated fills or a profit claim.

[Measurement report and limitations](/workspace/implementation/reports/phase1-live/historical-measurement/MEASUREMENT_REPORT.md) · [Phase 1 family and audit tables](/workspace/planning/phase-1-live/PHASE.md) · [Reconstruction/source distinction](/workspace/planning/phase-1-live/STRATEGY_SOURCE_CONFORMANCE.md).

The completion report records 816 passing tests and 36 passing subtests, native integration and future-perturbation checks, 323,676 input-file verifications, restart verification, and 341 visually inspected charts. These are existing Phase 1 receipts; this documentation update did not rerun that census or suite.

## Phase 1.5 foundation

The 2026-09-14 v1 review reproduced 25 passing implementation tests while the independent 27-case suite accepted 18 invalid cases. The first repair recomputed plan/code/run identities, walked predecessors, rejected unlogged or failed required commands, enforced nested clocks including deserializers, selected engineering dates per input group, and replayed one native parquet row. The [2026-09-14 v2 review](/workspace/planning/research-program/reviews/00-foundation-v2-2026-09-14/REVIEW.md) then found ten further invalid submissions still accepted by the verifier despite 45 targeted tests and 27/27 pinned cases. The second repair fail-closes non-object reviews, reconciles matrix status with acceptance, checks snapshot source bytes and copies, matches parsed artifact schemas, and requires lineage availability, artifact paths and resolvable row IDs. The independent checker was not edited. Its hash remains `c9441fea0a79674991522ae8db5347cdd1060f372d6aa5cffd425c7f30d6b800`.

Current admission, all verifier commands exit 0, independent suite 27/27, additional 14-case probe 14/14:

[P15-00 `40ffb49bc037e3cc`](/workspace/implementation/reports/research-work/P15-00/40ffb49bc037e3cc/attempt-0001/TASK_RECEIPT.json) sha256 `ce57e93846d6a1b3af936703058e15b012aa23720387f00bad4c37cac1341858` · [P15-01 `ee71900e26791e89`](/workspace/implementation/reports/research-work/P15-01/ee71900e26791e89/attempt-0001/TASK_RECEIPT.json) sha256 `73ec9ea4ccd580275d47901cb807f57733f91d7914daf0e10e7e24fbe5962617` · [Subphase `6824d15fbda635ce`](/workspace/implementation/reports/research-work/00-foundation/6824d15fbda635ce/attempt-0001/SUBPHASE_RECEIPT.json) sha256 `d7f8878b0aa7fda33d0b88d194afff6ca2afb00ea4d85dcca251016b511bb019` · [GATE_REVIEW.json](/workspace/implementation/reports/research-work/00-foundation/6824d15fbda635ce/attempt-0001/GATE_REVIEW.json) sha256 `d9a6b98c06d67b8716f526710af2eee9c0db92b6503e271fca7f6b03ac4aed95` · [fixed-suite RESULTS.json](/workspace/implementation/reports/research-work/00-foundation/6824d15fbda635ce/fixed-suite/RESULTS.json) sha256 `5cf01df4d7b617ba6c9adb03a2472f5d8941ad9e74fe16516408a0e7c3e5d683` · [additional-suite RESULTS.json](/workspace/implementation/reports/research-work/00-foundation/6824d15fbda635ce/additional-suite/RESULTS.json) sha256 `b2cf057201988690c08644e29f96ca8bd2dd3a97764e5e70f09555351cc4acf9`.

2020-01-02 Keani prior-profile coverage stays partial with 390 unknown minutes. Native replay is parquet `2021-01.parquet` row 769284, kind `native`. Exchange-feed completeness remains unknown. Same-model coordinator review is not cross-model diversity.

Rejected v2 attempt `240838146c38c484`, hashes unchanged:

[P15-00 v2](/workspace/implementation/reports/research-work/P15-00/91ade001fb32cb9b/attempt-0001/TASK_RECEIPT.json) · [P15-01 v2](/workspace/implementation/reports/research-work/P15-01/7da6cc99d954e280/attempt-0001/TASK_RECEIPT.json) · [Subphase v2](/workspace/implementation/reports/research-work/00-foundation/240838146c38c484/attempt-0001/SUBPHASE_RECEIPT.json) · [v2 GATE_REVIEW.json](/workspace/implementation/reports/research-work/00-foundation/240838146c38c484/attempt-0001/GATE_REVIEW.json) · [v2 independent RESULTS.json](/workspace/implementation/reports/research-work/00-foundation/240838146c38c484/attempt-0001/INDEPENDENT_RESULTS.json).

Original rejected v1 receipts, hashes unchanged:

[P15-00 v1](/workspace/implementation/reports/research-work/P15-00/b291864ccceaca9a/attempt-0001/TASK_RECEIPT.json) · [P15-01 v1](/workspace/implementation/reports/research-work/P15-01/039267553e8bf721/attempt-0001/TASK_RECEIPT.json) · [Subphase v1](/workspace/implementation/reports/research-work/00-foundation/f7135f8d696ff1f5/attempt-0001/SUBPHASE_RECEIPT.json).

[Independent review that rejected v1](/workspace/planning/research-program/reviews/00-foundation-2026-09-14/REVIEW.md) · [v1 reproductions](/workspace/planning/research-program/reviews/00-foundation-2026-09-14/adversarial-confirmed/RESULTS.json) · [Independent review that rejected v2](/workspace/planning/research-program/reviews/00-foundation-v2-2026-09-14/REVIEW.md) · [v2 additional reproductions](/workspace/planning/research-program/reviews/00-foundation-v2-2026-09-14/additional-suite/RESULTS.json) · [ASSURANCE.md](/workspace/planning/research-program/ASSURANCE.md).

## Phase 1.5 native views and outcomes

P15-02 wraps HistoricalFeatures in a columnar MarketView and replays baseline scanners. P15-03 adds ordered first-passage labels, the one-mini costed benchmark, chronological splits and fit-period diagnostics. Task verifiers exit 0. Subphase `--gate-review` exits 0. Pinned checker 27/27 on the closed foundation receipts. Baseline parity is 3420/3420 jobs on 60 stratified dates versus run-1.0.1. Diagnostics through 2021-12-31 are descriptive and were not used to change the bank, thresholds or dates.

[P15-02 `ebb1b8270700be4d`](/workspace/implementation/reports/research-work/P15-02/ebb1b8270700be4d/attempt-0001/TASK_RECEIPT.json) sha256 `97c677a2ef9d29c1144dbb5e30e3f9e8ebddac54862bf10bb1e815358b48392f` · [P15-03 `53e8f17617f39a87`](/workspace/implementation/reports/research-work/P15-03/53e8f17617f39a87/attempt-0001/TASK_RECEIPT.json) sha256 `cfe8fc68c1cda6cb4bcb6d48a9012623169d6a5dad7773613c5085c239721412` · [Subphase `95522aebaedfa3ed`](/workspace/implementation/reports/research-work/01-native-and-outcomes/95522aebaedfa3ed/attempt-0001/SUBPHASE_RECEIPT.json) sha256 `8de21ad751caecab4cd9feafa73f4d8b56cb8349ea53750e792789203f119b67` · [GATE_REVIEW.json](/workspace/implementation/reports/research-work/01-native-and-outcomes/95522aebaedfa3ed/attempt-0001/GATE_REVIEW.json) sha256 `5d192e5f438f9c11355063204526eca0a6a1be0a4b95361727ab73393caceaa2`.

MarketView quotes are trade-synchronous BBO. Mixed-action MBP-1 iteration is refused by the frozen tape adapter. Exchange-feed completeness remains unknown. Same-model coordinator review is not cross-model diversity.

## Next phases

[Phase 1.5](/workspace/planning/phase-1-5/README.md) reconstructs remaining numerical rules, screens representative mechanisms, refines promising families within a finite budget and measures individual setup changes. Finishing it is a prerequisite to starting Phase 2 implementation. The current eligible work is `02-source-reconstruction`, using the closed 01 receipts `ebb1b8270700be4d` / `53e8f17617f39a87` / `95522aebaedfa3ed` and matching GATE_REVIEW.json above, which themselves require the closed v3 foundation receipts `40ffb49bc037e3cc` / `ee71900e26791e89` / `6824d15fbda635ce`. Do not treat rejected v1 receipts or rejected v2 attempt `240838146c38c484` as that gate. This status update did not start 02.

[Phase 2](/workspace/planning/phase-2/README.md) builds jointly fitted intraday volatility forecasts, native options context with intraday updates, auction/session/cross-market forecasts and method-specific context experts. It supplies conditional plans; final entry integration belongs to Phase 4. [Architecture](research-architecture.md) and the [roadmap](/workspace/planning/ROADMAP.md) define the boundaries.

## Source-exact versus operational definitions

Dated object implementation snapshots describe source-object contracts. They do not undo the later explicitly inferred P-zone, gamma, auction-state and macro reconstruction. Missing proprietary constants remain unknown; our versioned substitutes are never labelled recovered author formulas.

## Correction: definitions exist; 18 branches were not scanned

The older frozen empirical run used `unavailable_definition` for 18 branches that had documented source sequences but lacked scanner support in that run. The later reconstruction and acquired census supersede that scanner status. Preserve the older report as evidence of its own release, rather than interpreting its labels as current definition availability. Historical runs and their frozen definition identities are not rewritten when this shared wiki changes.

The retained compatibility anchor is below for older source links.

<a id="correction-definitions-exist-18-branches-were-not-scanned"></a>
