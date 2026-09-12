# Freshly qualified re-entry

Object in [Sires — thesis, risk and order flow](method-sires-thesis-flow.md).

A stop-out can leave the wider thesis/band intact, but a new entry requires return inside that same band and fresh selected-branch confirmation. The location, reward/result and delta checks are rerun from zero. [ANAT] pp.7, 10; [STOP] pp.6, 14–15; [CONT] pp.8–10.

**Not a standalone trade.** Prior confirmation is not reusable entry permission, and calling a trade a re-entry does not reset a daily stop. A dead thesis needs a new thesis.

**Record before use.** Parent attempt/exit, new candidate_id, same thesis/band_id, return, fresh confirmation time, branch and account limit before new decision.

**Phase 1 observation.** Require prior exit < fresh confirmation ≤ new decision, same valid band and current daily permission; also run the full selected execution branch. Unknown fresh evidence is not a pass.

**Current implementation (2026-09-12).** [O144 contract](../FORMULAS.md#o144) is complete, with executable checks passing in the [object review](/workspace/implementation/validation/phase1-completion/obligation-matrix.json). Allow re-entry only after the linked parent exit, in the same live thesis band, with fresh confirmation and a full branch verdict. [Implementation](/workspace/implementation/src/trading_research/research/method_pack/objects/lifecycles.py).

**Evidence limits.** Actual thesis, instruction, fill, management, account or state records are required for a historical instance. Scoped source policies and supplied interpretations cannot manufacture missing private records or a contemporaneous cohort. See [current status](current-status.md) for the separate historical comparison scope; implementation completion does not establish a source trade or its performance.

**Related objects.** [Thesis, validity band and death condition](thesis-lifecycle.md) · [Source-selected dealing range](dealing-range.md) · [Fresh defense of a continuation band](defended-band-continuation.md) · [Defense, replenishment, exhaustion and lift-off](stop-four-stage.md) · [Source account and session stop](daily-loss-limit.md)

[Index](index.md) · [Observation contract](source-sequence-fidelity.md) · [Source map](source-catalog.md)

[STOP]: </workspace/sources/documents/discretionary/stop-re-entering.pdf>
[ANAT]: </workspace/sources/documents/discretionary/anatomy-of-a-losing-start.pdf>
[CONT]: </workspace/sources/documents/discretionary/a-clean-continuation-short.pdf>
[FORMULAS]: </workspace/planning/phase-1-live/FORMULAS.md>
