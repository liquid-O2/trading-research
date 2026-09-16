# P15-16A repair — SIRES / REFILL-STUDY

Worktree `/workspace/.worktrees/b02r-sires`. Branch `p15/b02r-sires`. No git commands. No receipts. No wiki edits.

## Exit predicate

1. `scan_b02` enumerates locations from the market. `rec` is registry identity plus `b02_now_ns`. Author-context keys are not read.
2. Every stage is measured or returns unknown with a named unobservable operand. Gamma is not defaulted.
3. REFILL `touch_record` pass means held, fail means broke, unknown when the hold window is unobservable. Zone construction uses source 60/80/100 beside the labelled OD print floor 40.
4. Plausibility blocks exist. `test_p15_16a_plausibility_sires.py` writes PLAUSIBILITY files and fails without a named diagnosis.
5. Author examples report `reached_location` and `detected` separately. Rules are not loosened.
6. B0 and B0.1 gzip files for 2021-01-04 and 2022-01-03 stay byte-identical.
7. Existing `test_p15_16a_sires.py` and the plausibility gate are green.

Wake: no Cursor `/loop`. Sequential run in this session. Skip: architect/arena (shape was specified). Skip: git commit (forbidden).

## Data shape

Population episode: `{candidate_id, research_verdict, stages[], reference{kind,ticks,role}, geometry, values}`. Locations are `{kind, ticks, known_at_ns, role}`. Contact: first touch in a 2-tick band, then 4-tick departure (B0.1 lifecycle).

## Decisions

1. Root cause of 0 SIRES passes: `scan_b02` read `location_kind` and friends from `rec`. Population `rec` is the registry branch record. Rewrite enumerates overnight/session extremes, 1-minute swing pivots in the first two RTH hours, overnight LVN/shelf/ledge, F3 microbalances, control-zone VA edges, VWAP ±1/±2/±2.5, supplied KG1. Never emits POC.
2. Gamma: `ofm_aggressive` needs short, `balance_failure_fade` needs long. `NativeMarketView` has no options board. Context is unknown with reason `gamma regime not observable in Phase 1.5 inputs; Phase 2 options boards supply it`. A `supplied("gamma")` record, if present, is measured. `rec.gamma_regime` is ignored.
3. Daily R is not on the tape. Risk/management still measure stop geometry and 1:1 / trail from the market. Daily R is a named omitted operand, not an episode-wide unknown. Otherwise every branch would be unknown (the gamma bug in another costume).
4. ABS p.6 is not the replenishment page. Reward ticks are ABS pp.3-4 and 13. Location kinds are ABS p.6. Recorded, not silently moved.
5. K2345 p.9 OCR has no stop-limit sentence. Resting-stop OFM is OFM pp.11-14. Recorded.
6. VWAP ±2.5 is p.3 and p.8, not p.4. p.4 has ±1 and ±2. Bands stay (1, 2, 2.5) as RR-20.
7. "Control zone" is not a BIG p.10 phrase. BIG pp.15-16 is "where the other side last had control". Mapped to overnight VA / F3 far side.
8. REFILL pass is hold vs broke (REF pp.5-8). First-round 93% pass was touch-inside plus fillable bracket. `form_b02_zones` requires cluster size ≥ 60 (REF p.5). OD print floor 40 stays labelled. `processes.form_refill_zones` is unchanged.
9. 175 = 41152/235 (REF p.8). 42% hold is REF p.8. Hold tick boundary is unpublished; OD 8 ticks / 30 minutes.
10. `common.py` lazy-imports `peak_rss_bytes` so family adapters import in this worktree. Listed in MERGE_NOTES.

## Source quotes (binding)

STOP p.10: "My minimum filter is three ticks of replenishment; one or two is the classic fake-out zone."
STOP p.14: "The level has refreshed at least three ticks." Daily stop minus four R on p.15.
ABS p.6: location question — extreme, shelf, ledge, LVN, minor volume node, not the middle of balance.
ABS pp.3-4: three-tick reward from the absorption print. Cited as ABS p.6 in the task pack; actual pages recorded here.
CONT p.11: squeeze with no failure, fast, real aggression, no retest, no false start.
OFM p.4: NY AM NQ bubbles 30-60 contracts.
BIG p.5: 350 percent same-price imbalance.
FP8 p.5: footprint flag 3x to 4x.
OFM pp.12: "The order rests below the wick so only aggressive continuation can tag it in."
C1 p.4: structure breaks, value shift, new information.
C2 p.5: 50% off at 1 to 1, stop to breakeven.
K18 p.14: stop moves to the next protected high only after price closes below the prior one with real aggression.
VWAP p.4: trades beyond the 1 band, ideally at 2, only with absorption.
REF p.5: sixty, eighty, a hundred contracts hitting in seconds.
REF p.8: 41,152 zone-touch events, 235 sessions, 42% hold.

## Disagreements recorded

Task pack cites ABS p.6 for reward ticks. Quote is pp.3-4/13. Location is p.6.
Task pack cites K2345 p.9 for resting stop. OCR of p.9 has no stop-limit text; OFM pp.11-14 does.
BIG p.14 "80% of the time" is the long-gamma regime share, not a pass rate.

## Author examples that miss location

SI-2026-07-15-OVERNIGHT. STOP pp.8-9. Printed fill 30045 at 01:01 ET. The population scan lays 1-minute highs and lows in 09:30-11:00, plus overnight session high/low. 30045 was not the overnight extreme and is outside the RTH minute window. `reached_location=false`, `miss:level`, our_level 29779.25. Tolerance was not widened.

SI-2026-08-06. BIG pp.3-16. First printed fill is BUY at about 29258 on the prior-day aggression band 29200-29255. 29258 is 12 ticks above 29255. Registered OD tolerance is 8 ticks. `reached_location=false`, `miss:side`. Tolerance was not widened.

The other eight dated sessions reach the author's level. OFM dates fail at context because gamma is unobservable. SI-2026-07-23 reaches location and fails at trigger (replenishment_ticks=1). SI-2026-07-14 fails at location (inside_balance). No rule was changed to force a detect.

## Verification round (driver failures 1-7)

1. `runner.py` dropped `directory_listing_digest`. Full suite collects.
2. Gate fails on out-of-bound measurement unless family JSON has `observed_rate_justification` `{page, text}`. `test_mutated_stop_four_stage_bound_fails_the_gate` mutates `stop_four_stage.pass_rate` to `[0,0]`, pops justification, asserts out of bound.
3. Episode is a contact at a source-literal location. Bound `[0,16]` (kg1 `[0,1]`). Every branch has a source_claim and page. Not `[0,800]` / "unstated".
4. `ofm_aggressive` and `balance_failure_fade` emit one `session_unknown` per session when gamma is missing.
5. REFILL bound stays `[80,350]` / `[0.25,0.60]`. Per-date touches 6..592. Gap is zone construction (cluster ≥ 60 varies by session) plus OD 8-tick/30-min NQ-only hold vs unpublished paper cutoff on NQ+MNQ. HOLD_BOUNDARY_TICKS stays 8.
6. Gate paths resolve from `Path(__file__).resolve().parents[2]`.
7. After-tape replay returns `detected=None`, `divergence="date outside the tape"` before `build_market_view`. Monkeypatch test. RULES/REPLAY/FUNNEL writes under `_repair_sires/`. `_track_sires` sha256 asserted.

Confirmation never-fail: `absorption_reward_retest` confirmation is own 3-tick reward then a distinct return to origin ± 2 (ABS pp.5-13). `defended_band_continuation` confirmation is `reward_ok`, not replenishment OR absorption. On the 15-date slice: absorption confirmation 0 pass / 4 fail; defended_band confirmation 140 pass / 15 fail.

## Tests

Full suite: `cd /workspace/.worktrees/b02r-sires/implementation && PYTHONPATH=src /workspace/implementation/.venv/bin/python -m pytest tests/rule_discovery -q -p no:cacheprovider` exit 0, 469 passed in 2078.97s.

## Byte identity

Hashes of frozen B0 and B0.1 job files for 2021-01-04 and 2022-01-03 taken at start in `B0_B01_HASHES.json`. All 52 files matched `_track_sires/BYTE_IDENTITY_BEFORE.json`. Re-checked after the scan exists in `BYTE_IDENTITY_AFTER.json`.
