# JJ-TBR B0.2 implementation spec

Worktree only: `/workspace/.worktrees/b02-jumbo`.
Python: `/workspace/implementation/.venv/bin/python`, cwd `.../implementation`, `PYTHONPATH=src`.
pytest: `-p no:cacheprovider`.
Do not run git. Do not edit `/workspace` itself, `/workspace/data`, `/workspace/sources`, method_pack scanners, `baseline_repairs.py`, `common.py`, `confirmation.py`, `run_adapter_populations.py`, tools, wiki, or receipts.

## Public surface (jumbo.py)

Keep existing functions unchanged (`scan_variant`, `confirm_at_contact`, `_empty_hook`, `family_document`, etc).

Add:

```python
STAGE_ORDER = ("context", "reference", "location", "trigger", "confirmation", "risk", "objective", "management")
RULES: dict[str, dict[str, Any]]  # keyed by rule_id
REPLAY_LEVEL_TOLERANCE = Decimal("2")  # points; registered OD

def extension_reaction_bands(high, low, width=None) -> dict
def mean_reversal_bands(high, low) -> dict
def projection_ladder(high, low) -> dict
def scan_b02(market, rec) -> dict
def replay_example(market, example) -> dict
def compute_published_statistics(dates: list[str]) -> dict
def rules_payload() -> list[dict]
```

### `extension_reaction_bands`

Call `o015` from `objects/range_geometry.py` with `coordinate_convention_verified=True` and `parent_id` set. Return:

```
{"upper": [H+1.33W, H+1.66W], "lower": [L-1.66W, L-1.33W], "width": W}
```

as Decimals. Do not re-type the formula. The OD near band 0.33-0.66 is a separate helper `mean_reversal_bands` (edge ± [0.33, 0.66]·W) and is never the extension_reaction location.

Fixtures that must hold:

- H=110, L=100 → upper 123.30–126.60, lower 83.40–86.70
- H=21410, W=152.50 → upper 21612.825–21663.15
- L=23810, W=50 → lower 23727–23743.5

### `projection_ladder`

Multiples ±0.5, ±1, ±1.33, ±1.66, ±2, ±2.5, ±3 from H and L. Recorded as reference levels, not entry filters.

### `scan_b02(market, rec)`

`rec` may be a coverage-row dict with `branch`, a branch string, or None (all `FAMILY_BRANCHES["JJ-TBR"]` branches).

`market` may be:

- `NativeMarketView` (account-day census view)
- `HistoricalFeatures`
- duck type with `account_day` or `day`, and either `completed_bars(start,end,seconds)` or `bars(start,end,seconds=60)` and optionally `at(hhmm)`

Normalize bars to dicts `{start,end,O,H,L,C,known_at,volume,bar_id,observed_complete}`. Never read a bar whose `known_at` is after the episode `decision_at`.

Return a document:

```
{
  "schema_version": "research-family-b02-scan-v1",
  "baseline_version": "B0.2",
  "family": "JJ-TBR",
  "branch": <branch or "all">,
  "session_date": <YYYY-MM-DD or None>,
  "clock_zone": "America/New_York",
  "episodes": [...],
  "omissions": [...],
  "rules": rules_payload(),
  "n": pass+fail, "p": n_pass, "f": n_fail, "u": n_unknown,
  "populations": {"B0.2": {"episodes": ..., "setup": p, "rejected": f, "unknown": u, "no_setup": f}},
}
```

Each episode:

```
{
  "schema": "phase1-historical-episode-v2",
  "candidate_id": str,
  "method": "JJ-TBR",
  "branch": str,
  "side": "long"|"short",
  "session_date": str,
  "research_verdict": "pass"|"fail"|"unknown",
  "failed": [operand names],
  "unknown": [operand names],
  "values": {...},
  "geometry": {"entry": float|None, "stop": float|None, "target": float|None, "reference_level": float|None, "sweep_depth": float|None},
  "stages": [{"stage": <from STAGE_ORDER>, "verdict": "pass"|"fail"|"unknown", "at_ns": int|None, "operands": {}}],
  "rules": [{"rule_id", "kind": "literal"|"OD", "source": str, "file_line": "source_adapters/jumbo.py:<n>"}],
  "decision_at": int|None,
  "strategy_assessment": {"status": "setup"|"no_setup"|"data_unavailable"},
}
```

Omit a stage name when it does not apply to that branch. Do not rename stages.

Verdict: pass if required stages pass; fail if a required operand is false; unknown if a required operand is missing (including no tape). `failed`/`unknown` lists must be populated, never left implied.

### Branch funnels

Clocks are America/New_York via `et_ns` or `HistoricalFeatures.at`.

**Shared NY range.** Formation 06:00–09:00 ET. Frozen at 09:00. Width W=H-L.

**context (RR-08, F08).** At 09:30, open vs prior RTH (09:30–16:00 prior complete same-contract session): `inside_value`, `below_val`, `below_pdl`, `above_vah`, `above_pdh`. Precedence: `below_pdl` if open < PDL; `below_val` if open < VAL; `inside_value` if VAL <= open <= VAH; `above_vah` if open > VAH; `above_pdh` if open > PDH. If VA is missing, still label vs PDH/PDL and put `val`/`vah` in `unknown`. Record in stage `context`. Selectors for `single_extended`, `single_purged`, `internal_rotation` read this label (OD, no extra numeric threshold).

**judas_reversal (RR-03, RR-06, F11).**
- Sweep search of H or L starts at 09:00. A sweep before 09:30 is valid.
- Stage `trigger` records sweep time. Sweep depth is recorded, not required (F11/RR-06).
- Modal reversal window 09:40–09:50 is literal (JR p.70) and recorded, not a hard fail if the reclaim is later.
- Baseline entry is reclaim of the swept edge after the sweep (long: first bar with high >= L after L was swept; short: first bar with low <= H after H was swept). 2025-01-28 buy 09:53:46 ET is the worked case.
- Confirmation baseline: 3-minute 3-candle OB (TBR p.27: candle 2 sweeps candle 1, candle 3 closes beyond candle 2). 2-minute, 5-minute, and rejection-block are OD variants recorded in operands, not required for pass.
- Objective: +0.5·W beyond the swept edge, else the opposite edge. Mean-reversal band ±0.33–0.66 is recorded. Projection ladder recorded as references.
- Stop: beyond the sweep extreme, one tick (OD structural).

**judas_outbound.** 09:30 opening sweep of the 6–9 edge, expiry 09:40, objective ±0.5·W. Stages: context, reference, trigger, risk, objective. Omit confirmation if the opening batch is the entry.

**extension_reaction (RR-01, RR-03, RR-07, F08).**
- Location is the o015 band, not 0.33–0.66.
- Search contacts after 10:00.
- Stage `location` holds the band. Stage `trigger` is first touch of the band.
- Report coincidence `band ∩ SessionStat box` when SessionStat is available; unknown if not.
- 13:00 reaction is admitted (F08). Reduced-expectation-after-10:00 does not apply to this branch.

**other_session (RR-04).** London box 02:00–03:00 ET, traded 03:00–06:00. Same quadrant / ±0.5 / 1.33–1.66 geometry. Do not use 00:00–03:00. Quadrant long uses q1, short uses q3, EQ both sides (local to this adapter; RR-02 merge note for common.py).

**timed_pzone_reversal (RR-05, F17).** Anchors Session 1 09:00, Session 2 10:00 (also register 09:50), Session 3 02:00. Proprietary generator unknown. Use printed fixture boxes:

```
PZONE_FIXTURES = {
  "2026-01-02": boxes [25758-25764], [25718-25725], [25660-25666], [25620-25626], 10:00 [25760-25768],
  "2026-01-09": 09:00 [25655-25665] target 25850, 10:00 [25625-25640],
  "2025-12-30": 10-point boxes centered on 25790, 25745, 25682, 25635 (OD width),
  "2026-02-24": [24710-24720], [25000-25010],
}
```

Entry: absorption print inside the box (OD proxy above). Stop below the box (long) / above (short). Target 3-day pivot when printed (`d1_high` etc), else unknown.

**single_extended (F08, RR-08).** Selector: open below PDH or VAH (2026-07-27). Location EQ/quadrant of 6–9. Reduced expectations after 10:00.

**single_purged (E3, RR-08).** Selector: open below VAL (2026-07-28). Overnight purge of prior RTH H/L then compressed range, entry EQ/quadrant, 09:40–09:50 continuation window recorded.

**internal_rotation (F08, RR-08).** Selector: open inside value (2026-07-10). Location EQ / named internals / EVRange if printed. Action any time of session.

**SessionStat (RR-07).** OD: 60 prior complete same-contract sessions, same clock (RTH 09:30–16:00 or London 02:00–06:00). Mean and median of high, low, range. On NativeMarketView use `prior_complete_same_contract_dates(60)` and load views only as needed; if priors are missing, stage location records `sessionstat: unknown`. Do not load 60 sessions inside geometry unit tests.

**EVRange (RR-07).** Fixture only. 2026-08-28 and 2026-09-01 are after the tape (`native_calendar.last_date` 2026-08-19) → `data_unavailable`.

### `replay_example(market, example)`

Return exactly:

```
{
  "id": example["id"],
  "detected": bool | None,
  "branch": str,
  "our_side": str | None,
  "our_level": float | None,
  "our_entry_ns": int | None,
  "author_level": float | None,
  "author_side": str | None,
  "divergence": str,
}
```

`detected is None` only when `inside_tape` is false, the date is after 2026-08-19, the market has no tape, or required operands are unavailable. A miss is `detected is False` with a divergence string. Never loosen a rule to force a hit.

Match: same branch family (expected branch token in our branch), same side when the author side is long/short (if author side is "long then short", either matches), reference level within `REPLAY_LEVEL_TOLERANCE`, entry inside `entry_window_et` on that date. Author level: prefer L/H/minus_1_66/plus_1_33 from `levels`, else first numeric level.

### `rules_payload`

Every RULES row with `file_line` resolved via `inspect.getsourcelines` of the implementing function. Finding ids (RR-01 … RR-09, F08, F11, F12, F17, F18, F19) appear in `rule_id` or a `finding` field.

Required rule_ids (minimum):

- `RR-01-extension-band-1.33-1.66` literal JR p.23 / o015
- `RR-01-OD-near-band-0.33-0.66` OD
- `RR-03-sweep-from-09:00` literal JR p.20, p.70
- `RR-03-modal-reversal-09:40-09:50` literal JR p.70
- `RR-03-extension-after-10:00` literal
- `RR-04-london-02:00-03:00` literal JR pp.50, 63–64
- `RR-05-pzone-anchors` literal JR pp.16–18
- `RR-05-OD-absorption-proxy` OD TBR p.35 body 0.6 vol 1.5×14
- `RR-06-reclaim-entry` literal JR p.71
- `RR-06-objective-plus-0.5` literal
- `RR-06-projection-ladder` literal
- `RR-06-sweep-depth-recorded` F11
- `RR-07-OD-sessionstat-60` OD
- `RR-07-evrange-fixture` F17
- `RR-08-open-location-at-09:30` literal JR pp.36, 38, 42
- `RR-08-OD-branch-selector` OD
- `RR-09-published-statistics` literal JR pp.23, 37, 70
- `F08-single-extended-reduced-after-10:00` literal TBR p.12
- `F11-confirm-3m-ob-baseline` literal TBR p.27
- `F11-OD-confirm-2m-5m-rejection` OD
- `F12-candidate-references-unchanged` note only
- `F17-pzone-generator-unknown` OD
- `F18-ny-clock-ET` literal TBR p.6 (note p.4 in WORK_LOG)
- `F19-chart-clocks-UK-UTC` literal

## families/jumbo.json

Add `"baselines": {"B0.2": {"scan": "scan_b02", "version": "B0.2-2026-09-15"}}`. Do not alter existing keys.

## Tests `implementation/tests/rule_discovery/test_p15_16a_jumbo.py`

Use a duck-typed tape for ruling fixtures (do not need parquet). Each ruling fixture must fail if the rule is removed, reversed, delayed, or fed future bars.

1. RR-01 geometry identity + 2025-01-28 and 2025-09-09 printed bands. Future-bar after 09:00 must not change the 06:00–09:00 width used for the band.
2. RR-03 sweep at 09:10 is a valid trigger; a 09:30-only search would miss it. 2025-10-13 style 09:00–09:15 H taken.
3. RR-04 London 02:00–03:00 formation, 03:00–06:00 action; 00:00–03:00 must not be the box.
4. RR-05 printed P-zone box + absorption print inside → episode; missing proprietary generator → unknown, not fail-closed as no_setup without the unknown list.
5. RR-06 reclaim after sweep is the entry; 09:53 reclaim admitted; sweep depth present but not required.
6. RR-07 SessionStat labelled OD; EVRange after tape → data_unavailable; coincidence field present on extension_reaction.
7. RR-08 open-location labels at 09:30 from prior RTH, not from later session outcome.
8. F11 3-minute OB baseline vs 2/5 recorded as OD.
9. F08 13:00 extension contact admitted; single_extended reduced-expectation flag after 10:00.
10. F18/F19 clock fields on the document.
11. Byte identity: `dual_scan` B0/B0.1 on `2021-01-04` and `2025-01-02` match `frozen_scan_document` / repaired scan after stripping `baseline_version`. Write hashes to `_track_jumbo/B0_B01_HASHES.json`.
12. Replay every JJ-* example through `replay_example`. Inside-tape dates use `build_market_view(date)` (census). After-tape ids return `detected is None`. Write `_track_jumbo/REPLAY_JJ-TBR.json`. Assert each row has a verdict (`detected` is bool or None), not that it detected.
13. 9-date slice `engineering_slice_dates()` through `scan_b02` per branch. Write `_track_jumbo/FUNNEL_JJ-TBR.json` with B0.1 counts from `dual_scan` beside B0.2 per-stage counts.
14. `compute_published_statistics` on the slice dates. Write `_track_jumbo/STATISTICS_JJ.json` with source figures beside measured. Mismatch listed under `findings`.
15. Write `_track_jumbo/RULES_JJ-TBR.json` from `rules_payload()`.
16. Negative: a long extension band must not equal the short band; a sweep after decision_at must not appear in operands.

## Evidence files

All under `implementation/reports/research-work/P15-16A/_track_jumbo/`:

- FUNNEL_JJ-TBR.json
- REPLAY_JJ-TBR.json
- STATISTICS_JJ.json
- RULES_JJ-TBR.json
- B0_B01_HASHES.json
- MERGE_NOTES.md (RR-02 unified diff suggestion for common.py: EQ both sides, quadrant sides case-selected; F18 remove JJ-TBR from CLOCK_ZONE_UNVERIFIED_FAMILIES; do not apply the diff)
- PYTEST_SUMMARY.txt
- WORK_LOG.md (append decisions)

## MERGE_NOTES.md

Explain RR-02: `common.py` changed-reference enumeration fixes EQ/q1 long and q3 short. Author trades EQ both ways; quadrants are case-selected (TBR pp.12–15). Include a unified diff against `source_adapters/common.py` only as a proposal. This track codes around it inside jumbo.py B0.2.

## Performance

Replay of ~23 dates and 9-date × 8 branches is expected to take minutes. Do not skip real `build_market_view` / `load_source_market` for those tests. Geometry fixtures must stay synthetic and fast.
