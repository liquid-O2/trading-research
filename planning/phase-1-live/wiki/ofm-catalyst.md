# Origin-of-the-Move catalyst

Object in [Sires — thesis, risk and order flow](method-sires-thesis-flow.md).

Repeated aggressive effort failing to achieve movement creates the squeeze catalyst/origin. The source draws a line at the relevant absorbed aggression with its surrounding cluster; later releases, failures and retests refer back to that identified origin. [OFM] pp.3–13; [BIG] pp.5–14; [CONT] p.10.

**Not a standalone trade.** The catalyst, a failed squeeze or a bubble is not the completed OFM entry. Aggressive and passive branches have different later requirements.

**Record before use.** Catalyst_id, source price/cluster band, initial effort and response, side binding, known_at, and linked release/failure/refill/drive/retest events.

**Phase 1 observation.** Do not choose the final morning extreme as the origin or enter merely because the first squeeze failed. Preserve the source figure's actual sequence and direction.

**Current implementation (2026-09-12).** [O118 contract](../FORMULAS.md#o118) is complete, with executable checks passing in the [object review](/workspace/implementation/validation/phase1-completion/obligation-matrix.json). Link a catalyst origin to ordered release, failure, refill, drive, retest, and reward stages without replacing the origin later. [Implementation](/workspace/implementation/src/trading_research/research/method_pack/objects/local_flow.py).

**Evidence limits.** Native executions and BBO support literal measurements. Source-only filters and defense/absorption/replenishment interpretations require attributed observations; the tape does not prove hidden reserve or full-depth order history. Timestamp ties without sequence retain ordering uncertainty. See [current status](current-status.md) for the separate historical comparison scope; implementation completion does not establish a source trade or its performance.

**Related objects.** [Aggressive Origin of the Move](ofm-aggressive-branch.md) · [Passive Origin-of-the-Move variant](ofm-passive-branch.md) · [Clean squeeze continuation](clean-squeeze.md) · [Zone formed by aggressive prints](refill-zone.md)

[Index](index.md) · [Observation contract](source-sequence-fidelity.md) · [Source map](source-catalog.md)

[BIG]: </workspace/sources/documents/discretionary/only-trade-big-trades.pdf>
[OFM]: </workspace/sources/documents/discretionary/origin-of-the-move.pdf>
[CONT]: </workspace/sources/documents/discretionary/a-clean-continuation-short.pdf>
[FORMULAS]: </workspace/planning/phase-1-live/FORMULAS.md>
