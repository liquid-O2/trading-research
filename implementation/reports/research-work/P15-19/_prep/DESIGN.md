# P15-19 prep design

Mode: reference. Engineering preparation for E0-E4. Not a research result.

## Problem

P15-18 has not produced `SELECTED_RULES_BY_FOLD.json`. This prep implements the exit machinery on fixtures and on a ten-date B0.2 pass slice so the later P15-19 run is a data step.

Existing `replay_family` is the wrong driver. It re-opens occupancy, has no 60-minute expiry, and has no break-even or trailing stop. `first_passage` labels trade-price order and returns `same_batch_ambiguous`. It does not fill.

Allowed writes: `rule_discovery/exits.py`, `tests/rule_discovery/test_p15_19.py`, this `_prep/` directory.

## Usage

```python
from trading_research.research.rule_discovery.exits import (
    FrozenEntry,
    evaluate_entry,
    evaluate_entries,
    frozen_entry_from_b02_episode,
    market_from_view,
)

paired = evaluate_entry(entry, quotes, trades)
# paired.entry_id, paired.records["E0"] ... paired.records["E4"]
# occupancy flags live on evaluate_entries, not inside a single-entry call
```

## Shape

Organizing structure: a policy table plus one causal batch reducer. Not five copied loops. Not `replay_family`.

Public types:

- `FrozenEntry`: entry_id, family, branch, side in `{1,-1}`, fill price and time, initial stop, objective, optional source deadline, flatten time, quantity 1, round-trip commission dollars.
- `ExitRecord`: policy, entry_id, exit time, exit price, reason, net points, net dollars, stop_updates, complete.
- `UnsupportedRecord`: policy, entry_id, reason `undefined_initial_r` or `incomplete_no_quote` or `fractional_partial`.
- `PairedExits`: entry_id plus five records, occupancy flags per policy default false.
- `MarketBatch`: equal-timestamp bundle of bids, asks, trade prices, quote rows for `select_quote`.

Policy table:

| id | minute expiry | management |
| --- | --- | --- |
| E0 | 60 | none |
| E1 | 30 | none |
| E2 | 120 | none |
| E3 | none | break-even after +1R |
| E4 | none | trail after +1R |

Reducer state: current stop, pending stop (effective next batch), armed_plus_one_r, highest_bid / lowest_ask, stop_updates.

Invariants encoded in types and guards:

- quantity other than 1 raises `ContractError` (A03).
- undefined R (`stop is None` or `abs(entry-stop)==0`) yields unsupported E3/E4 and still produces E0-E2 (A04).
- stop updates record `trigger_batch_id` and `effective_after_batch_id`. Pending stop applies only on the following batch (A01, A02).
- long stop only rises. Short stop only falls.
- fill uses `execution.select_quote` after trigger + 250 ms, 5 s window, `_quote_usable` 1 s age. Long exit `bid - 1 tick`. Short exit `ask + 1 tick`. PnL via `net_points` / `net_dollars` with round-trip commission `2 * COMMISSION_SIDE` unless the entry overrides the dollar amount.
- same-timestamp: keep every bid, ask, and trade price. If any price hits the stop and any hits the objective, reason is the stop family (`stop` / `break-even stop` / `trailing stop`). This is the pessimistic bound for the experiment. It does not change `first_passage`.
- occupancy: each entry is evaluated as if alone. `evaluate_entries` then flags a later same-branch entry whose fill time is before the prior exit of that policy. Flags are not merges (A05).

## Synthesis decision

Base: causal reducer plus policy table (candidate A).

Rejected: wrapping `replay_family` five times (candidate B). It re-simulates occupancy and cannot trail or break-even without editing `execution.py`.

Rejected: whole-path extrema then `first_passage` segments (candidate C). Computing the day's max first is the future-maximum leak A02 forbids.

Grafted from C: use `PriceBatch` trade prices inside a timestamp for the ambiguity set, matching the outcomes contract's "all possible prices retained."

## Tradeoffs accepted

- Native quotes from `NativeMarketView.quotes` are BBO on trade prints (`load_span_arrow(..., trades_only=True)`). Full MBP-1 quote actions are not loaded. Prep proves the machinery, not quote-tape completeness.
- Frozen B0.2 fill time is `decision_at`, fill price is stated geometry. This is not a latency-simulated entry.
- Green Bird MNQ `derived_quantity` is ignored. Quantity is always one NQ mini.
- Geometry: field names ending `_ticks`, or integer magnitude `>= 30000`, convert with `ticks_to_decimal`. Otherwise treat as NQ points.
- Break-even stop is `entry + side * (round_trip_dollars / POINT_VALUE)`. Round-trip dollars default `5.00`. The stop is then tightened, never loosened: long `max(old, be)`, short `min(old, be)`.
- Account-day flatten on the native slice is `account_day_window` end minus 1 minute (`16:59` ET on a regular day).
- Source deadline from `geometry.objective_horizon_ns` or `geometry.cancel_ns` when present and earlier than the policy expiry.
- Jobs are read from `/workspace/implementation/reports/research-work/P15-16A/1e13829f2c88f1e1/jobs` (gitignored, present on disk).

## Open questions recorded as decisions

See WORK_LOG.md. No human checkpoint.

## Next implementation step

Write `exits.py` against this sketch, then `test_p15_19.py` with the listed behavioral cases, then the ten-date slice writer that emits `SLICE_EXITS.json` and `RECONCILIATION.json`.
