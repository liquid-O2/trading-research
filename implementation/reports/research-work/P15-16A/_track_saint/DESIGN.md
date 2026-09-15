# B0.2 saint-track design (implementation contract)

Worktree: `/workspace/.worktrees/b02-saint`. Python: `/workspace/implementation/.venv/bin/python` with cwd `.../b02-saint/implementation` and `PYTHONPATH=src`. pytest `-p no:cacheprovider`. No git. No edits under `/workspace` itself, `/workspace/data`, `/workspace/sources`, method_pack, `baseline_repairs.py`, `common.py`, `confirmation.py`, `run_adapter_populations.py`, tools/, wiki, receipts.

## Files to add or edit

Edit only:

- `implementation/src/trading_research/research/rule_discovery/source_adapters/saint.py`
- `implementation/src/trading_research/research/rule_discovery/source_adapters/member.py`
- `implementation/src/trading_research/research/rule_discovery/source_adapters/keani.py`
- `implementation/src/trading_research/research/rule_discovery/families/saint.json`
- `implementation/src/trading_research/research/rule_discovery/families/member.json`
- `implementation/src/trading_research/research/rule_discovery/families/keani.json`
- `implementation/tests/rule_discovery/test_p15_16a_saint.py` (new)
- `implementation/src/trading_research/research/rule_discovery/source_adapters/b02_saint_track.py` (new, this track only)
- evidence under `implementation/reports/research-work/P15-16A/_track_saint/`

Do not change existing functions used by B0/B0.1: `bind_saint_operational`, `apply_operational_stages`, `apply_member_rules`, `apply_keani_rules`, `confirm_at_contact`, `scan_variant`, `slice_family`, `register_family_transform`. Add new functions below them.

## Shared helper `b02_saint_track.py`

```
STAGE_ORDER = ("context", "reference", "location", "trigger", "confirmation", "risk", "objective", "management")
B02_VERSION = "B0.2-2026-09-15"
LEVEL_TOLERANCE_TICKS = 8  # OD, 2 NQ points
Q = Decimal("0.25")
SLICE_DATES = ["2020-01-02","2021-01-04","2022-01-03","2023-01-03","2024-01-02","2025-01-02","2026-01-02","2023-11-06","2026-09-03"]
HASH_DATES = ["2021-01-04","2022-01-03"]
TRACK_DIR = Path(__file__).resolve().parents[5] / "reports/research-work/P15-16A/_track_saint"
# from this file: source_adapters -> rule_discovery -> research -> trading_research -> src -> implementation
# parents[0]=source_adapters, [1]=rule_discovery, [2]=research, [3]=trading_research, [4]=src, [5]=implementation
```

Helpers (keep small):

- `stage(name, verdict, at_ns, operands) -> dict`
- `export_rules(rules_table, functions_by_id) -> list` with `file_line` = `Path(fn.__code__.co_filename).name + ":" + str(fn.__code__.co_firstlineno)`
- `episode_doc(...)` building the B0.1-like episode dict with `research_verdict`, `verdict`, `failed`, `unknown`, `values`, `stages`, `rules`, `side`, `branch`, `method`, `decision_at`, `geometry`, `reference`, `trigger`
- `window_doc(family, branch, market, episodes, rules, omissions=(), extra=None)`
- `parse_rec(rec, default_family, branches)` -> (family, list[branch])
- `market_at(market, hhmm)` using `market.at` if present else `clock(market.day, hhmm)`
- `market_bars(market, start, end)` 
- `first_retest(bars, lo, hi)` first bar whose range overlaps [lo, hi]
- `entry_window_ns(day, window_et)` parse `"19:30-20:15"` or `"session of the retest"` (then None,None meaning whole session)
- `levels_close(a, b, ticks=8)`
- `replay_match(document, example) -> replay dict`
- `account_day_for_example(example)` : if session mentions Asia and time_et >= 18:00, use calendar date + 1 weekday (2026-08-10 19:51 -> 2026-08-11)
- `SynthMarket` duck type (see tests)
- `funnel_counts(documents_by_branch)`
- `sha256_json(obj)`

## scan_b02 contract (every adapter)

```python
def scan_b02(market, rec) -> dict:
    family, branches = parse_rec(rec, FAMILY, BRANCHES)
    episodes = []
    for branch in branches:
        episodes.extend(_scan_branch_b02(market, branch))
    doc = window_doc(...)
    doc["rules"] = export_rules(RULES, RULE_FNS)
    doc["baseline_version"] = B02_VERSION
    return doc
```

Decision-time: every operand's `known_at` / bar `known_at` must be <= `decision_at`. Bars with `start >= decision_at` are ignored. Tests feed a future bar that would flip the verdict if consumed.

No stage is stamped True without operands. Verdict `unknown` when a required operand is missing. `fail` when the rule is observed and does not hold.

## Saint RULES (module-level in saint.py)

| rule_id | kind | source |
|---|---|---|
| F04-arrival_read | OD | OD:approach_bars=5,fast_ratio=0.08 of balance_width (WIC p.4) |
| F04-profile_allows_trade | OD | OD:shape classifier mid_volume_frac/poc_pos (RTVP pp.6-11) |
| F04-alignment_ok | OD | OD:HTF value-migration vs 15m break, never from trade side (WIC pp.5-10) |
| F05-failed_auction_return | literal | AMTL p.8 |
| F05-poc_traversal | literal | AMTL p.9; RTVP p.5 |
| RR-22-asia-session | literal | TRAP pp.3-10 |
| RR-22-balance-fit | OD | OD:cover_frac>=0.55 else latest confirmed (TRAP p.3) |
| RR-22-single-retest | literal | TRAP pp.6-7 |
| RR-22-asia-range | literal | TRAP p.8 (150-160 points; measure, do not gate entry) |
| RR-22-long-mirror | literal | TRAP long mirror as ruled |

### Saint branch funnels

**continuation_retest** stages: context=profile, reference=fitted/fixture balance, location=session-open + balance edges, trigger=LTF break of a boundary (1m close beyond edge), confirmation=first same-boundary retest then 15m-or-1m control, risk=stop beyond LTF opposite edge, objective=far HTF edge (Asia: also record whether distance is inside 150-160). Omit management if unused.

**trapped_buyers_retest** same plus trapped delta at the extreme. Sides: short (buyers trapped at high) AND long (sellers trapped at low). Fast arrival required for pass. Prior failures at the extreme are evidence, not a 2-failure gate if the delta trap is visible; if delta missing, two prior failures still qualify (TRAP p.5 twice-failed).

**failed_auction_return** stages: context=original HTF range known, reference=that range, location=prior VA (prior-day profile VAL/VAH; unknown if missing, not fail), trigger=drive into that VA then rejection (close back out), confirmation=return close inside original range, then POC tell is deferred to poc_traversal. Do not require an older completed balance object.

**poc_traversal** after a return (or after price is inside the original range): count completed bars that tag POC and fail to hold (close back) vs an aggressive close through POC (body+delta with the side) plus a held retest on that side of POC. Fail-to-hold → target VAL (short from above POC / long-fail). Aggressive through + held retest → target VAH (long) or VAL (short through). Bind confirm_at and ltf_balance.

Search window: `market.start` to `market.end`, not 09:30.

Balance: `market.b02_fixtures["balance"]` if present (`{"low","high","start","known_at","id"}` or `[low,high]`), else OD fitter.

15-minute bars: `market.bars(start, end, 900)` if the third arg is honoured, else resample 1m.

## Member RULES

| rule_id | kind | source |
|---|---|---|
| F15-no-1245-split | literal | K10 pp.5-8 |
| F15-two-reasons | OD | OD:reaction_ticks=4, confluence_ticks=2, look-left any prior history (K10 pp.5-8) |
| F15-kg1-alternative | OD | OD:KG1 aligned within confluence_ticks (K10 p.6) |
| F15-independence-admission | literal | K10 pp.5-8 (binds admission) |
| F15-target-1.5R | literal | K10 pp.7-8 |
| F15-ticket-rr-conflict | literal | K10 pp.7-8 tickets R:R 1.00 and 9.60 as conflicting evidence |
| F15-stop-beyond-rejection | literal | K10 pp.7-8 |
| F15-fixed-500-risk | literal | K10 p.13 |
| RR-23-instrument-transfer | OD | OD:instrument transfer NQ from ES-202609 (K10 pp.7-8,12-13) |

Look-left: pivots on prior session bars (full prior day, no 12:45 split) plus current session bars with `known_at < contact`. HVN from the same look-left profile (prior day full, or current session up to but not including the contact bar). Pair reaction with nearest HVN within 2 ticks. If no HVN pair, accept KG1 from `key_gamma_reference(market)` if that call works; on synth, `market.b02_fixtures["kg1"]`. Independence: reaction id != hvn parent; HVN window not equal to reaction window. Fail admission if independence fails.

Branches: `resistance_short`, `planned_return_long`. Contact: first distinct touch of the confluence band after 09:30 (or after session start if synth has no 09:30). Confirmation: rejection (short) or absorb/hold (long). Stop: high+Q short, low-Q long. Target: entry ± 1.5 * R. Quantity: `500 / (stop_ticks * 5)` for NQ (`tick_value=5` OD transfer). Record `conflicting_evidence: [{"ticket":"first","rr":1.00},{"ticket":"second","rr":9.60}]`.

Stages: context=thesis/look-left, reference=confluence band, location=band, trigger=touch, confirmation=rejection/hold, risk=stop+qty, objective=1.5R.

`replay_example`: if example id is MB-2026-07-K10 or instrument starts with ES or `inside_tape` is false, return detected=None, divergence="ES tape required", other fields None/example values. Do not scan.

## Keani RULES

| rule_id | kind | source |
|---|---|---|
| F16-a-period | literal | TPO p.3 09:30-10:00 |
| F16-observation-1000 | literal | AVG p.21 |
| F16-no-1100-cutoff | literal | F16 |
| F16-no-60m-expiry | literal | F16 |
| F16-no-val-rise | literal | F16 |
| F16-open-above-value | literal | AVG pp.21-22 |
| F16-rejection-poc-or-prior-vah | literal | AVG pp.21-22 |
| F16-imbalance-vah-break | OD | OD:O109 buy run or synth fixture band (AVG pp.21-28) |
| F16-defended-retest | literal | AVG pp.21-28 |
| F16-three-tick-reward | literal | AVG p.24 |
| F16-htf-objective | OD | OD:nearest of prior-day high, prior VAH, weekly high above (F16) |

Funnel (map to stage names):

- context: open fully above value (A low >= prior VAH; A complete 09:30-10:00)
- reference: prior value / developing profile at observation
- location: rejection at developing POC or prior VAH (wick in, close above). Do not require developing VAL rise
- trigger: close through developing VAH with aggressive buy imbalances
- confirmation: first retest of the imbalance band after the break, no 60m cap, through session end; defense + 3-tick reward (`C >= retest_px + 3*Q` on a later complete bar, still holding the band)
- risk: stop 1 tick below the band
- objective: nearest HTF level above entry among {prior_day_high, prior_vah, weekly_high}. Weekly high: `market.prior("week")` range high if present, else fixture `weekly_high`, else unknown objective (do not fall back to A-high+A-width)

Document extras: `fully_above_a_eligible`: 1 if A fully above prior VAH else 0; `stage_funnel` counts.

`replay_example` for Keani: no dated example. If called with empty/unknown example, return detected=None, divergence="no dated example", branch="source_long".

## replay_example (Saint / Member)

```python
def replay_example(market, example) -> dict:
    # Member ES short-circuit first
    # Resolve account day; if market.day mismatches Asia mapping, still scan the given market
    # Apply fixture balance from example["levels"]["balance"] onto market.b02_fixtures
    doc = scan_b02(market, {"family": FAMILY, "branch": None})
    return replay_match(doc, example)
```

`replay_match`: expected_detection.side must match episode.side (allow "short then long" as two episodes; match if any requested side hits). Branch: substring / family match (`continuation_retest` matches "trapped_buyers_retest / continuation_retest"). Level: any of balance edges, break 29740, entry 29729.25, geometry.entry within 8 ticks of a parsed number in `reference` or `levels`. Entry ns inside window if window parsed; else any same session. If no episode: detected=False, divergence="miss". If market has no bars covering the window: detected=None, divergence="date outside tape".

## family json

Add without touching other keys:

```json
"baselines": {
  "B0.2": {
    "version": "B0.2-2026-09-15",
    "scan": "scan_b02",
    "replay": "replay_example"
  }
}
```

## Tests `test_p15_16a_saint.py`

Use SynthMarket. Each ruling fixture calls `scan_b02` (not a private helper alone). Assert literal verdicts.

Required tests (function names start with `test_<id>_` where id is F04/F05/F15/F16/RR-22/RR-23 so they fail if the rule is gone):

1. `test_F04_arrival_fast_vs_slow` — slow continuation pass, fast continuation fail; fast trapped pass
2. `test_F04_arrival_ignores_future_bars` — bar after decision would make it fast; still slow
3. `test_F04_profile_excludes_trend` — trending fail, balanced pass
4. `test_F04_alignment_not_from_trade_side` — HTF down, LTF up, long episode alignment fail
5. `test_F05_no_older_auction_gate` — failed_auction_return can pass/unknown without older balance object
6. `test_F05_poc_tell_selects_target` — fail-to-hold POC → VAL; aggressive through + hold → VAH
7. `test_RR22_asia_session_not_ny_only` — trigger at 19:51 ET is found; a 09:30-only search would miss (assert episode exists)
8. `test_RR22_single_retest_only` — two returns to the edge produce one episode
9. `test_RR22_long_mirror` — trapped long exists as a side
10. `test_RR22_asia_range_literal` — RULES contains 150-160 / TRAP p.8
11. `test_F15_no_1245_split` — prior-day reaction after 12:45 still pairs
12. `test_F15_independence_binds_admission` — same-parent two reasons → fail not pass
13. `test_F15_target_1_5R_and_ticket_conflict` — target 1.5R and conflicting_evidence present
14. `test_F15_stop_above_rejection_high` — short stop > rejection high
15. `test_F15_fixed_500_risk` — quantity derived from $500
16. `test_RR23_es_tape_required` — replay_example returns detected is None and divergence "ES tape required" for MB-2026-07-K10 even with a dummy market
17. `test_F16_no_1100_cutoff` — break at 11:30 still eligible
18. `test_F16_no_60m_retest_expiry` — retest 90 minutes later still eligible
19. `test_F16_a_period_0930_1000` — A window is 09:30-10:00
20. `test_F16_no_developing_val_rise` — rejection without VAL rise still location-pass
21. `test_F16_htf_objective_not_a_width` — objective is prior high/VAH/weekly, not A-high+A-width
22. `test_F16_three_tick_reward` — confirmation fail without 3-tick reward, pass with it
23. `test_b0_b01_byte_identity` — load hashes from `_track_saint/B0_B01_HASHES.json`; recompute dual_scan for HASH_DATES × families/branches listed there; compare. Import adapters so transforms register.
24. `test_replay_writes` — load AUTHOR_EXAMPLES; Saint two examples via load_source_market on resolved account day (catch load errors → detected None, divergence "date outside tape"); Member ES short-circuit; write REPLAY_SAINT.json and REPLAY_MEMBER.json; assert each row has a verdict key (`detected` in {True, False, None})
25. `test_funnel_and_statistics_slice` — for each SLICE_DATES date, load_source_market once; scan_b02 each family; also dual_scan B0.1 counts; write FUNNEL_*.json, STATISTICS_SAINT.json, RULES_*.json. If a date fails to load, record error and continue. Assert files exist.

Byte-identity must not recompute B0.2 into B0. Hash only dual_scan `b0` and `b01` documents (json dumps sort_keys default=str, sha256 hex).

SynthMarket minimum: `day, start, end, instrument_id, reconstruct=False, b02_fixtures, window.document, at, bars, profile, prior, range, coverage, domain`. `at("HH:MM")` uses clocks.et_ns on `market.day` unless overridden in an `at_overrides` dict (needed for prior-day 18:00 / 19:51). Provide `at_overrides` in Asia fixtures.

## Evidence writers

The tests write:

- FUNNEL_SAINT-AMT.json, FUNNEL_MEMBER-TWO-REASONS.json, FUNNEL_KEANI-OPEN-ABOVE-VALUE.json
- REPLAY_SAINT.json, REPLAY_MEMBER.json
- STATISTICS_SAINT.json (poc 80% traverse on slice; Asia range vs 150-160)
- RULES_SAINT-AMT.json, RULES_MEMBER-TWO-REASONS.json, RULES_KEANI.json
- MERGE_NOTES.md if any shared-file wish remains; otherwise "none"
- PYTEST_SUMMARY.txt with the pytest summary line
- B0_B01_HASHES.json already captured before edits; test compares after

## Statistics

On the 9-date slice, among poc_traversal episodes with aggressive-through + held retest, fraction whose later bars reach the far VA edge before session end. Record n, hits, rate, source 0.80, AMTL p.9.

Asia range: for each slice date, range of bars between prior-day 18:00 and day 03:00 (or market.start to 03:00). Record per-date high-low, median, fraction whose width is in [150,160], source TRAP p.8.

## Quality

Short functions. No comments that narrate phases. Comments only for non-obvious why. Do not loosen a rule to make replay detect. Do not mutate B0.1 helper logic.
