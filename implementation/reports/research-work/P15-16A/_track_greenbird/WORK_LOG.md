# P15-16A track greenbird work log

## Frame

B0.2 is a new scan beside frozen B0 and B0.1. Family-owned code lives in `source_adapters/green_b02.py` plus wrappers on `green_failure.py` and `green_vwap_scalp.py`. Shared files were not edited.

## Decisions

- London August split: 03:00-04:30 through 19 August, 02:00-05:00 from 20 August. Recorded because RR-11 names both "August" and "late August".
- F07 "value" is unpublished. Registered OD is prior RTH close versus the prior range midpoint. 09:00-10:00 box direction is close versus open and is read only at or after 10:00 so it cannot leak into a 09:33 entry.
- Ticket arithmetic on several crops is about $250 at MNQ $2/point. RR-12 still records the printed tool amount $750 as a literal and does not score size.
- Asia-high 5-minute close is literal. Asia-low longs are A3 PDL or box-edge at-level, not the A2 long mirror (candidate only).
- Golden-pocket continuation is the GB-SCALP entry. GB-FAIL also scans the overnight down-leg pocket so GB-FAIL replay can match 2026-07-29.
- 5-minute closes are taken from 300-second bars when C is present, otherwise from assembled 1-minute bars. Synthetic same-timestamp fills leave C empty.
- At-level return is capped at 30 minutes after the sweep so a later unrelated bar cannot confirm an earlier box.
- PDL scan starts at account-day start (18:00 previous) so 20:40 Asia entries are visible.
- Objective for a PDL long is prior-day high. A1 uses TDO when it still lies ahead of entry, otherwise the London high.
- Replay dates after 2026-08-19, and JSON `inside_tape=false`, return `detected=None` / `data_unavailable`. RR-16 wins over the Astra Y/N flags.
- `clock_zone_unverified` is false on B0.2 documents (F18). B0/B0.1 still go through `common.py` and were not changed.

## Independent-verification fixes

- Management is fail when risk or objective fails. `_gate_stages` also blocks later passes after an earlier fail so the last-stage pass count matches B0.2 pass.
- A1 stop is retest higher-low minus one tick. Sweep-extreme minus tick stays `stop_sweep_extreme_od_variant`.
- A1 confirmation operands are reclaim price/time, retest low, sweep low, higher-low comparison, and post-open close price.
- Replay with no live fill uses drawn levels and labels `drawn-not-live`, or `no author fill to compare`.
- Asia 5-minute negative tape stays above the Asia high after the sweep so rejection is the missing 5-minute close.

## Source quotes used

- GB p.19, p.25, p.27: 5-minute close for Asia-high, TDO, PDL.
- NG 2099513366326730859: A1 reclaim, retest, higher low, post-open close; A2 Asia-high short without TDO.
- GB p.37: NWOG Sunday 18:00.
- GB p.33: VWAP only for continuation; 30-point stop on the single example.
- GB p.40: old scalp cases unpublished as entries.

## Conflicts logged rather than silently decided

- Wiki golden-pocket Phase 1 down-leg band versus F06 up-leg `[H-0.618W, H-0.50W]`: ruling wins; local `pocket_in_leg_direction` does not call `common.golden_pocket`.
- SOURCE_ADDITIONS A4 still says stop beyond the far edge: F06/RR-14 near-edge baseline wins; far edge stays an OD variant.
- 11:45 tickets (09-01, 08-13) sit in the 11:30-12:45 gap of the stated scan windows. Baseline windows stay as the user named them. Synthetic fixtures use 09:30-11:30.
