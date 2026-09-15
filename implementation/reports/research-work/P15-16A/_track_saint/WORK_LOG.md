# P15-16A TRACK saint work log

Lead decisions. Rulings win over older wiki prose. Source quotes go here when they disagree with a prior note.

## Playbook

Feature playbook. Architect skipped: the user named `scan_b02`, `replay_example`, the RULES table, and the eight stage names; arena would exceed the three-agent cap and would route through Fable, which AGENTS.md forbids. Domain model is a RULES registry plus an ordered stage funnel.

## Data shape

`scan_b02(market, rec)` returns a B0.1-shaped window document plus:

- per episode `verdict` (`pass`/`fail`/`unknown`) mirroring `research_verdict`
- per episode `failed` / `unknown` operand lists
- per episode `stages`: ordered `{stage, verdict, at_ns, operands}` using only `context, reference, location, trigger, confirmation, risk, objective, management` (omit inapplicable, never rename)
- per episode and document `rules`: `{rule_id, kind: "literal"|"OD", source, file_line}`

`rec` is a mapping. `family`/`method_id` and optional `branch`. Missing branch scans every family branch. Each adapter scans only its own family.

`replay_example(market, example)` matches branch family, side, reference level within `LEVEL_TOLERANCE_TICKS=8` (2 NQ points, OD), entry inside `entry_window_et`. Miss is reported. `detected=None` only when the date is outside the tape or operands are unavailable.

B0.2 does not call `HistoricalEpisode.bind` (catalog field lock). It does not edit B0/B0.1 paths, `common.py`, `confirmation.py`, `baseline_repairs.py`, or method_pack.

## Session / Asia (RR-22)

`HistoricalFeatures(day)` already opens at prior-day 18:00 ET and closes at day 16:00. B0.1 Saint starts at `max(ref.known_at, 09:30)`. That is the NY-only bug.

B0.2 Saint searches from `market.start`. The Asia ticket is 19:51 ET on 2026-08-10, which sits on account-day 2026-08-11 (window 2026-08-10 18:00 to 2026-08-11 16:00). Replay of SA-2026-08-10-ASIA loads 2026-08-11.

## F04 arrival (WIC p.4)

Quote: "An aggressive move, buyers pushing in hard and fast, signals that side wants higher prices and is likely to defend the balance once it gets there. A slow, grinding move into the same extreme signals the opposite." Fast expects defense. Slow expects break.

OD: last 5 complete bars into the extreme, `mean(|C-O|)/balance_width`. Fast if ratio >= 0.08. Continuation_retest passes on slow (expects break). Trapped_buyers_retest passes on fast (aggressive into the extreme, then trap). Never stamp True.

## F04 profile (RTVP pp.6-11)

Shapes: balanced, double distribution, P, b, unrebalanced trend. Trend excluded. Continuation preferred.

OD classifier on the HTF profile over the fitted balance:

- `mid_volume_frac` = volume in middle 50% of range / total
- `poc_pos` = (poc-low)/(high-low)
- trending if `mid_volume_frac < 0.35` or VA spans > 0.90 of range → fail
- double if two local volume peaks separated by at least 0.15 of range
- P if poc_pos >= 0.66
- b if poc_pos <= 0.34
- else balanced

Pass for balanced, double, P, b. Fail for trending. Unknown if profile/POC missing.

## F04 alignment (WIC pp.5-10)

HTF control is value migration of the HTF balance (close vs mid, or a prior balance broken with a held retest) or trapped delta at the extreme. Compare that direction to the 15-minute break direction. Do not derive alignment from the trade side. Bind `confirm_at` and `ltf_balance` on all four Saint routes.

## F05 failed auction (AMTL pp.8-9)

Quote p.8: drive toward a previous area of fair value, reject, come all the way back into the original range. Quote p.9: repeated failure to hold POC → 20% chop / VAL; aggressive push through POC with a held retest → 80% / VAH.

No older-auction gate. Missing prior VA is unknown, not fail. `poc_traversal` is the POC tell and the target selector after return.

## RR-22 balance fit (TRAP p.3)

Author redraws the balance until it fits. OD: among balances known at the cash open (or first confirmed after), pick the one whose [low, high] covers the largest fraction of the overnight+session range already known, requiring cover >= 0.55, else the latest confirmed (`primary_balance` fallback). Replay injects the printed 29600-29960 (Asia) / 29560-29960 (WIC) via `market.b02_fixtures["balance"]` when present.

Intraday levels: session open and balance edges. Trade: the first retest after the break, not later retests. Target sits inside Asia's usual 150-160 point range as a literal statement to measure, not an admission gate. Long mirror of trapped buyers is kept (trapped sellers at a low).

## Member F15 / RR-23

No 12:45 split. Look left over any prior history available on the market (prior day full session plus current session before contact). Two reasons: a prior reaction (pivot with `reaction_ticks=4`, OD) and a minor HVN within `confluence_ticks=2` (OD), overlapping windows allowed, or KG1 aligned as the alternative second reason. Independence binds admission: distinct parents, and HVN not formed solely from the reaction's own bars. Spoken target 1.5R is literal. Drawn tickets R:R 1.00 and 9.60 are recorded as `conflicting_evidence`, not used to loosen 1.5R. Stop above the rejection high (short) / below the rejection low (long). Fixed $500 risk; quantity = 500 / (stop_ticks * tick_value). NQ tick value $5 is an instrument transfer (OD). Replay of MB-2026-07-K10 returns `detected=None`, `divergence="ES tape required"` without requiring a tape.

## Keani F16

A period 09:30-10:00 (TPO p.3). Observation starts at A end (~10:00). Sequence runs to `market.end`. No 11:00 cutoff. No 60-minute retest expiry. No developing-VAL-rise conjunct. Open fully above value: A low >= prior VAH. Rejection: wick into developing POC or prior VAH, close back above (already in B0.1 C4; keep). Break: close through developing VAH with buy imbalance runs. Confirmation: defended retest of that imbalance band plus 3-tick reward (AVG p.24). Objective OD: nearest of prior-day high, prior VAH, weekly high above the entry; never A-high plus A-width. Document field `fully_above_a_eligible` is the denominator.

## Byte identity

Hash dual_scan B0 and B0.1 documents for 2021-01-04 and 2022-01-03 before adapter edits. Tests recompute and compare. B0.2 is a new scan beside them.

## How-findings that bind B0.2

- B0.2 must not use `HistoricalEpisode.bind` or FORMULAS M06/M07/M08. Those predicates still require older-auction keys and C7 stamps. B0.2 builds episode dicts with its own `verdict`.
- Adapter transforms (`bind_saint_operational`, `apply_member_rules`, `apply_keani_rules`) are the live B0.1 document. Do not change them.
- `confirm_at_contact` is the changed-axis path, not B0/B0.1. Leave it.
- Census B0.1 jobs are the repaired scanner without adapter transforms. Live `dual_scan` B0.1 includes transforms. Byte-identity of our code is live dual_scan before vs after, plus frozen gz file hashes (we never write those files).
- Saint B0/B0.1 also cap control search at trigger+60 minutes. B0.2 searches the first retest to session end so Asia (RR-22) is visible.
- Member 12:45 split lives in `scan_member_repaired` and `_member_prior_reasons`. B0.2 look-left ignores it. Do not edit `_member_prior_reasons` (used by confirm_at_contact / B0.1-adjacent).
- Import adapter modules before `dual_scan` so transforms register. `source_adapters/__init__.py` is empty.

## Independent verification fixes (2026-09-15)

- F04 stages: `stage_from` derives pass/fail/unknown from operand keys. No `stage("confirmation"|"objective"|"trigger"|"reference", "pass"` in saint.py. Cascade omits later stages after the first fail/unknown so funnel last-stage pass equals B0.2 pass.
- Replay: `FixtureMarket` overlays example balance/levels and does not write `market.b02_fixtures`. `replay_match` compares entry to the printed fill (`actions[].price`), not the first number in `levels` (29600). Tolerance remains 8 ticks. `test_replay_writes` loads `example["date"]` and records that producer on REPLAY_SAINT.json.
- Double distribution: `opposite_shelf_near_edge` (RTVP p.8) is the continuation target when shape is `double`. Long uses the lower edge of the upper shelf. Short uses the upper edge of the lower shelf.
- AVG p.21 OR vs p.22 AND is recorded on `F16-rejection-poc-or-prior-vah` as `unresolved`.
- K10 p.13 drawings are two SELL and one BUY (`K10_P13_DRAWN_DIRECTIONS`). Caption "three shorts" is conflicting evidence. Negative control: demand-hold (low reaction only) does not admit `resistance_short`.
- Asia-range statistic window is prior-day 18:00 ET through 03:00 ET (whole overnight), not the Asia session box. Recorded beside the TRAP p.8 claim. Widths unchanged.

## Shared files

Do not edit `common.py`, `confirmation.py`, `run_adapter_populations.py`, or `tools/`. Local duck-typed synth markets and adapter-local helpers. Any needed shared change goes in MERGE_NOTES.md as a unified diff.

## Source vs ruling notes

- AVG p.28 lists objectives "POC, value, VAH, the poor high or low". Ruling F16 wins: nearest of prior-day high, prior VAH, weekly level above.
- K10 prose 1.5R vs tickets 1.00 / 9.60. Both recorded. 1.5R is the target policy.
- TRAP p.8 150-160 is a usual-range claim to test, not an entry filter.
