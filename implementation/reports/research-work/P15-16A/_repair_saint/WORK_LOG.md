# P15-16A repair round, track saint

Exit predicate. STAGE_AUDIT, population `scan_b02`, plausibility blocks, gate test, replay, fixtures, B0/B0.1 byte identity, CLOSURE REPORT. No git. No receipts. No wiki edits.

## Decisions

Rulings win. Source quotes sit here when they disagree with a prior note.

### Driver round (gate, density, replay, cache)

Gate now fails on measurement. `bound_violation_errors` reads only `observed_rate_justification` from family JSON. Auto `_diagnose()` is a report note, not a pass. `test_p15_16a_plausibility_mutated_bound_fails` sets trapped `pass_rate` to `[0,0]` on a tmp spec and asserts the gate errors.

Failed-auction density. Close-inside overlapping VA was still mean reversion. Repair: prior VA must sit entirely outside the current box (AMTL p.8 previous area), price must leave current value then close inside that area, stay at least two bars (p.10 attempted acceptance), reject, then hold five minutes back in the original range. Slice pass rate 0.200, 2/15 sessions.

Member confirmation. Trigger remains the rejection/absorb wick. Confirmation is `reaction_held` over the next 15 minutes with at least one later bar (K10 pp.7-8 absorb-and-hold). Independent of the wick. Slice confirmation fail=9 on resistance_short.

Replay. `replay_example` always returns `reached_location` (bool) and `failing_operand`. Outside-tape dates return `date outside the tape` before any market load. Asia account-day reload no longer requires the `inside_tape` flag.

Cache. Tests write FUNNEL/RULES/REPLAY/STATISTICS under `_repair_saint/` only. Funnel skips dates outside 2020-01-02..2026-08-19. `test_after_tape_replay_does_not_build_cache` monkeypatches `event_cache.build_event_window`. Round-1 `_track_saint` seven files restored and sha256-pinned.

### Confirmation is the held retest (WIC p.8)

Quote, Who's In Control page 8 extract: the confirmation is the retest that held, not the initial break. Continuation confirmation now requires `confirm_at`, `held_retest`, `arrival_ok`, and `alignment_ok`. A missing `confirm_at` is unknown (04 F10 / Saint E), never a pass.

### 80/20 is a conditional tell (AMTL p.9)

Quote, AMT on Live Markets page 9: once price is back inside the previous range after a failed auction, 80 percent that price runs to the far extreme, 20 percent that it ranges inside. The tool is POC behavior: repeated failure to hold versus an aggressive push through POC with a retest that holds. That figure is not a session pass rate and is not a target to hit.

### Why continuation/trapped never confirmed on the full-history run

Job `2021-01-04/continuation_retest.json.gz` confirmation operands: `arrival=slow`, `arrival_ok=true`, `retest=true`, `htf_control=null`, `ltf_break=up`, `alignment_ok=null`. `htf_control_direction` called `market.bars(balance.start, decision_at)`. Fitted `balance.start` can sit after the trigger. `HistoricalFeatures.bars` returns `[]` when `end<=start`. Alignment was unknown, so confirmation was unknown. Repair: if `balance.start >= decision_at`, read from `market.start`. LTF break direction uses the traded level, not only the HTF box edges.

### Why failed_auction and poc_traversal almost always passed

Failed auction confirmation was `rejection` and `return` after a drive that any wick below the box into overlapping prior VA could satisfy. Repair: skip when prior VA is not distinct from the current box; missing return fails confirmation; missing return time is unknown.

POC confirmation required `held_retest` only on the branch that already had a hold, so the operand could not fail. Repair: emit the aggressive-push episode even when the retest does not hold. Repeated failure is a wick through POC that closes back, twice, not a close near POC.

### TRAP fill 29,729.25 versus our 29,857

Replay injected interior levels including 29,860. The first short close already below 29,860 was treated as a break. Repair: `first_true_break` requires a complete origin-side bar, then a close through. Asia replay loads account day 2026-08-11 (`account_day_for_example`) because 19:51 ET on 2026-08-10 sits after 18:00 on that calendar date.

### Member near-universal pass

Confirmation restamped `independent`. Trigger was `touch=True`. HVN on a 0.25 grid almost always sits within 2 ticks of some prior pivot, so four sessions in five passed. Repair: trigger records the contact reaction (K10 pp.7-8 rejection or absorb-and-hold). A pass needs both reasons and that reaction. ES-202609 stays `data_unavailable` / `ES tape required`.

### Keani

AVG p.21: A period sitting clear of prior VAH; rejection at POC or previous VAH; aggressive buying imbalances through developing VAH; defended retest. SD11: A low equal to prior VAH is not fully above. Ruled value is prior RTH 09:30-16:00 at 70% (`empirical_registry` `complete_a_above_prior_value`). DOM at the retest is unobservable; confirmation uses the 3-tick reward (AVG p.24). No dated ticket. B0.1 39/1695 is the density reference. B0.2 job collision on `source_long` is the integrator's fix.

### Shared files

`b02_saint_track.py` TRACK_DIR now resolves inside this worktree. Helpers `first_true_break`, `retest_held`, `contact_reaction`, `REPAIR_SLICE_DATES`, `REPAIR_DIR` added.

`runner.py` imports `directory_listing_digest` from `contracts.identity`, which does not define it on this cut. Additive fallback in `runner.py` so tests can collect. See MERGE_NOTES.md.

`common.py` and `confirmation.py` were not edited.

### Author examples on the tape

SA-2026-08-10-ASIA. Account day 2026-08-11. Population scan finds a short continuation whose entry is 29,776, near the marked 29,780 line. The printed fill is 29,729.25 (TRAP p.7), 11 points below 29,740. Registered tolerance is 8 ticks (2 points). The fill is therefore a miss at location-vs-fill, with `divergence=level`. An episode exists on that date (location stage reached). The 29,740 true-break did not match the fill inside 8 ticks because the fill sits 11 points through the level, which is the author's stop-box geometry (29,729–29,736.75), not the break.

SA-2026-08-04-12-WIC. No printed fill. `expected_detection` names the 29,740 break. Our short continuation prints 29,782.25. Location stage reached. Detected no. Failing operand is the break/entry versus 29,730–29,745.

MB-2026-07-K10. `detected=None`, `divergence=ES tape required`.

Keani. No dated example in AUTHOR_EXAMPLES_2026-09-15.json.

### Byte identity

Start hashes copied to `_repair_saint/B0_B01_HASHES_AT_START.json` from `_track_saint/B0_B01_HASHES.json` (dates 2021-01-04 and 2022-01-03). Tests recompute `dual_scan` B0/B0.1.

### Playbook

Autonomous run. Wake/loop skipped (no /loop). Commits skipped (no git). Opening a PR skipped (no git, orchestrator merges).
