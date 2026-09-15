# P15-16A track sires work log

Track: SIRES and REFILL-STUDY. Worktree `/workspace/.worktrees/b02-sires`. Branch `p15/b02-sires`.

## Data shape

B0.2 scan document (same keys as a B0.1 window document, plus funnel stages and a rules list):

- `schema_version`: `research-family-b02-scan-v1`
- `baseline_version`: `B0.2-2026-09-15`
- `family`, `branch`, `coverage_id`
- `episodes`: each episode has `candidate_id`, `research_verdict` in {pass, fail, unknown}, `status`, `side`, `failed`, `unknown`, `values`, `decision_at`, `geometry`, `reference`, `trigger`, plus:
  - `stages`: ordered `{stage, verdict, at_ns, operands}` using only `context`, `reference`, `location`, `trigger`, `confirmation`, `risk`, `objective`, `management` (omit a stage that does not apply to the branch; do not rename)
  - `rules`: `{rule_id, kind: "literal"|"OD", source, file_line}`
- document-level `rules` is the RULES table with `file_line` filled from inspect
- operands are read at decision time from the account-day view. Bars with known_at after decision_at are not bound.

`replay_example(market, example)` returns `{detected: bool|None, branch, our_side, our_level, our_entry_ns, author_level, author_side, divergence}`.

Organizing structure: a module-level `RULES` table keyed by `rule_id` (finding ids in the key or comment). `scan_b02` consumes it. Not a chain of booleans.

## Decisions

1. B0.2 is a new scan beside B0/B0.1. `apply_sires_rules`, `scan_variant`, `dual_scan`, `form_refill_zones`, `confirm_at_contact`, JETBUNDLE and STOIC paths stay untouched.
2. `scan_b02` does not call `scan_branch_repaired` or `HistoricalEpisode.bind`. New operands would raise in bind. Episode dicts are built in the adapter.
3. Engine is the array account-day view (`NativeMarketView`). HistoricalFeatures is accepted by building that view from `market.day` and reading `market.supplied` for gamma when present.
4. architect skipped: user capped live agents at 3 with one code writer. Two shapes compared in-thread. Chosen: independent B0.2 scanner with a RULES registry. Rejected: post-process B0.1 episodes (F02 must admit a clean squeeze B0.1 drops).
5. Shared files (`common.py`, `confirmation.py`, `run_adapter_populations.py`, `tools/`) are integration-owned. Needed runner registration goes in MERGE_NOTES.md as a unified diff. Tests pass without that patch.
6. Location kinds allowed: shelf, ledge, lvn, minor_volume_node, real_extreme. Forbidden: poc, inside_balance. Thesis death is the three C1 p.4 killers (structure break, value shift, new information). `thesis_alive` is not a stop-distance proxy.
7. Two three-tick measurements stay separate. Replenishment: count of executed passive refills at the same price (STOP pp.10, 14). Reward: price moves at least three ticks from the absorption print inside the registered window (ABS p.6). ES lesson distances are not NQ thresholds.
8. OFM aggressive baseline entry is the resting stop below the failed-squeeze wick. Drive-retest is the second entry. Objectives: 40-tick bracket (OFM pp.7-8) and far side of last control zone (BIG pp.10, 15-16).
9. Gamma: `ofm_aggressive` needs short gamma, `balance_failure_fade` needs long gamma, when a regime record exists. Missing Phase 2 options record makes the context stage unknown, not pass.
10. Replay miss is reported. Rules are not loosened to pass an author example.
11. Refill OD stand-ins stay ≥40 prints in 5 seconds and ≥80 size, labelled. Literal family of thresholds to test: 60, 80, 100 contracts in seconds. Hold-label boundary is OD. Printed bracket is literal REF p.12. If the 9-date slice is not ~175 touches/session, status is `population_scale_unreconciled`.
12. `_touches_after_departure` currently stamps `departure_at_ns` as the touch time. B0.2 records the actual first outside-band time. The B0.1 helper is not edited.
13. Byte-identity dates: 2021-01-04 and 2022-01-03. Hashes live in BYTE_IDENTITY_BEFORE.json.
14. 9-date slice: 2020-01-02, 2021-01-04, 2022-01-03, 2023-01-03, 2024-01-02, 2025-01-02, 2026-01-02, 2023-11-06, 2026-09-03.
15. Replay level tolerance is OD, 8 ticks (2.00 NQ points). Entry window is the example `entry_window_et` converted with `et_ns`.
16. No git commands. No receipts finalized. No wiki edits. No method_pack or baseline_repairs edits.

## Source quotes that bound the scan

- CONT p.11: "a squeeze with no failure: fast, real aggression, no retest, no false start." Entry once buyers hit the move and got absorbed, tight stop.
- STOP p.10: "My minimum filter is three ticks of replenishment; one or two is the classic fake-out zone."
- STOP p.14: "The level has refreshed at least three ticks. One or two is the fake-out zone." Daily stop minus four R.
- ABS p.6-7: absorption at POC/inside balance is not a signal. Real extremes: shelf, ledge, LVN, minor volume node.
- C1 p.4: three things end a bias: structure breaks, value shift, new information.
- RR-18 / K2345 p.9: resting sell stop 29370.25 below the failed-squeeze wick.
- REF p.12: 12 ticks inside, stop 32, target 96, cancel 30 minutes, one position, 1-tick cost and slippage.

## Disagreements recorded, not silently decided

Wiki "What B0.2 must reproduce" lists nine dated sessions. RR-17 also lists 2026-07-15 overnight. The examples file has SI-2026-07-15-OVERNIGHT. Replay set is the ten ids in the user prompt.

F09 original text says location follows LVN, shelf, value-area edge and auction extremes. RR-20 / ABS pp.6-7 say never POC or inside balance, and current-day VAH/VAL are lagging. B0.2 uses prior-day VAH/VAL as real extremes and rejects current-day VAH/VAL as the location.

## Replay finding (not a rule change)

All ten SI-* author examples remain misses. `our_level` is null on most rows, so no level comparison runs. Divergence is `match_branch_only`. SI-2026-07-08 has `our_side` long against the author's short. Recorded in REPLAY_SIRES.json. Rules were not loosened.

## Verification

- Synthetic ruling fixtures, byte-identity, replay, and slice. `22 passed in 192.07s`.
- Frozen P15-12 and P15-16 tests. `20 passed in 75.35s`.
- Census B0/B0.1 gzip hashes for 2021-01-04 and 2022-01-03 match BYTE_IDENTITY_BEFORE.json after the new scan exists.
- Author-example replay. All ten SI-* ids produced a verdict. All `detected=false` (miss reported, rules not loosened).
- REFILL 9-date slice. 1072 touches, 119.1 per session vs printed 175. Status `population_scale_unreconciled`.
- `scan_b02` is a new scan. `apply_sires_rules`, `form_refill_zones`, JETBUNDLE, and STOIC were not edited.
