# P15-17 stage A work log

Attempt: `47dedaaa4f5b9ce1`
Worktree: `/workspace/.worktrees/p15-17-stage-a` (branch `p15/17-stage-a`, start commit `50df48f2`)
Python: `/workspace/implementation/.venv/bin/python`, cwd `implementation/`, `PYTHONPATH=src`
`trading_research.__file__` = `/workspace/.worktrees/p15-17-stage-a/implementation/src/trading_research/__init__.py`

Playbook: Autonomous run. Feature throughput checkpoint recorded. architect skipped: RA-1..RA-6 already name the shape. Opening a PR skipped: no git commands. Docs skipped: orchestrating session writes the wiki.

Predicate: stage A only. No candidate scores. No `TRIALS.jsonl` row. `FREEZE.json` and `DRAFT_STUB.json` written. P15-16A receipt and corrected B0.2 run root stay `PENDING`.

## Decisions

- Pairing baseline is B0.2. A candidate is `scan_b02` with exactly one axis replaced. `overrides` is a keyword-only argument on every `scan_b02`. It is not a `rec` field. Green Bird and SIRES strip unknown rec keys.
- `overrides is None` and omitted both return the family document object unchanged. Apply runs only when the mapping is non-empty. Adapters lazy-import `finish_scan_b02` so the no-override path does not import `search.py`.
- Axis-to-stage map (RA-2): Formation → context+reference; Profile → reference; Reference → reference; Delta → confirmation; Sequence → trigger+confirmation; Memory → location; Timing → trigger. A candidate whose hooked stage the adapter does not emit is unsupported with a reason and stays in the list.
- GB-SCALP bank rows `bearish_small_scalp` / `bullish_discount_pullback` are observation-only in B0.2 (context + unpublished-entry reference). Sequence hooks confirmation and is unsupported.
- JETBUNDLE / STOIC have no B0.2 scanner. Unsupported if resolved.
- Bank is P15-08 attempt `9728f9ee0bbbdfd5` (`TASK_RECEIPT.json` sha256 `bfe62f1cc8e724f87a12fd6fd2e497a3f7ba38999b9799e415b3b7c1f4cb9bbf`, cited by every closed P15-16 receipt). `CANDIDATE_BANK.json` sha256 `3354f99fb315edebd62e17e6d32c80ea5c1400f6bd996488fbf7084798da54ee`. 160 candidates, 840 deferred, 50 baselines, used as they are.
- Splits: P15-03 `babe7a991b6b3dc1` `SPLIT_MANIFEST.json` sha256 `a30b03bf3ee7bd215ffaf11ff223b07fa0134202d544e4bd0dd353f730e2fde6`; `EVALUATION_PROTOCOL.json` sha256 `a22d86bff730bbb1f672cf9af6dfad95c88c310a6c7f639724c25f64573a272b`. Not regenerated.
- B0 census `20def36e065c13d7`: MANIFEST `20def36e065c13d75d738fbce475cf7ea5425255488861c58a1b5fbbbe8b488f`, SUMMARY `073f270c5a5f454f4a338219eca9421e43bd3440f4ed42252dfb19f5f4d7838d`.
- B0.1 `dd386316321ee58d`: RUN_COMPLETE sha256 `e4dea25d6b8a4910724bcb4f4e8bd3e218383924160153179fedf6643afcd267`, MANIFEST `dd386316321ee58d42dc70a612181ed365f727eb0f8d6a82c53a2afbff33164d`.
- Corrected B0.2 run root and P15-16A receipt: `PENDING`. First-round `1e13829f2c88f1e1` is schema-only; its numbers are superseded.
- Negative-control dates: `2020-01-02`, `2023-11-06`, `2024-01-02`. All inside the tape `2020-01-02..2026-08-19`. 2026-09-03 is outside the tape and is not used for scans.
- Throughput seven: `GB-FAIL:nyam_box:F1`, `KEANI-OPEN-ABOVE-VALUE:source_long:P1`, `GB-VWAP:source_long:R1`, `SAINT-AMT:continuation_retest:C1`, `SIRES:absorption_reward_retest:S1`, `MEMBER-TWO-REASONS:planned_return_long:M1`, `JJ-TBR:judas_reversal:T4`. Four-plus families. Projection formula is `160 x 1742 x p90 / (workers x 3600)` for 17 and 12. The 3x-vs-Phase-1 miss stays the R3 finding (2.71x, p90 1.48 s).
- SIRES and REFILL scan `NativeMarketView` (`market._native_view`). Other families scan `HistoricalFeatures`.
- Control scan files use the literal coverage_id, including colons. Comparison to the corrected full-history jobs (family-qualified `--` names) waits on resume.
- Override recipes now replace the hooked stage's verdict, at_ns, or existing operand values from the market and registered parameters (option a). Other stages stay byte-equal. RA-1 negative control unchanged.
- FREEZE.json `resolutions` pins all 160 bank candidates in bank order so stage B cannot silently re-resolve one.

## Commands

cwd `/workspace/.worktrees/p15-17-stage-a/implementation`, `PYTHONPATH=src`, python `/workspace/implementation/.venv/bin/python`. Logs under `logs/`.

| Command | Exit | Summary |
| --- | ---: | --- |
| import `trading_research` with worktree PYTHONPATH | 0 | `__file__` resolves under the worktree |
| `pytest tests/rule_discovery tests/contracts -p no:cacheprovider -q --tb=line` | 0 | 573 passed in 2792.04 s |
| `tools/check_outcome_fixtures.py` | 0 | TOTAL FAILURES 0 |
| `tools/check_foundation_adversarial.py` (first) | 2 | harness TimeoutExpired 60 s on `verify_research_release.py task --receipt P15-01` |
| `tools/check_foundation_adversarial.py` (retry) | 2 | same TimeoutExpired 60 s. Checker not edited. |
| `pytest tests/rule_discovery/test_p15_17.py -p no:cacheprovider -q` | 0 | 5 passed in 240.42 s (pre-fix) |
| `pytest tests/rule_discovery/test_p15_17.py -q -p no:cacheprovider` (after freeze 160-row list and real stage replace) | 0 | 6 passed in 221.76 s |
| `pytest tests/rule_discovery/test_candidate_verdicts.py tests/rule_discovery/test_engine_hygiene.py` | 0 | 13 passed in 453.38 s (R1 empty-delta + R3 parity) |
| `measure_stage_a.py` | 0 | THROUGHPUT_B02.json + PROFILE_B02.txt. Pipeline p90 25.246 s (Keani P1). |

## Hashes

- FREEZE.json sha256 `36e98f3a3b6d64cf937f12988641c5e1f127945e9045f2150a750c3c369c97fd`
- DRAFT_STUB.json sha256 `96b19051934848744ec16240f924508e21b5c82485ab2a23aab082ae33b00b66`
- THROUGHPUT_B02.json sha256 `7c658c25e969e6e2bebd3976195c3a89908e675fb05bb3f1737f2a46f4fa984c`
- PROFILE_B02.txt sha256 `387123427bf7c21d5b02cd30a092fbe0a26fcf2d7742e989e43086b16ec782be`

## Skips

- architect / arena. RA-1..RA-6 already name the data shape.
- Cursor `/loop` wake. Not in this harness.
- git commit / Opening a PR. User forbade git mutations. `git status --short` only, for the closure report.
- wiki. Orchestrating session writes it.
- TASK_RECEIPT.json. P15-16A digest and corrected run identity are PENDING.
- TRIALS.jsonl and candidate scores. Stage A does not score.
- family JSON edits. Stage names already live on the adapters.
- `family_scan_b02` / `run_adapter_populations.py` overrides wiring. search.py calls family `scan_b02` directly.
- Cross-family trail review. User required grok-4.6 for every role.
- `/no-comments`. No PR.

## Remaining

- Resume fills corrected B0.2 run path/sha256 and P15-16A receipt, repeats the control-scan compare against family-qualified job files, then issues the draft receipt.
- Pinned adversarial checker still times out at 60 s on P15-01 verify. Not a stage A code defect. Do not edit the checker. Independent timing: `verify_research_release.py task --receipt .../P15-01/a4c95ab43aef1038/attempt-0001/TASK_RECEIPT.json` took 109.6 s wall against the checker's hard-coded 60 s subprocess timeout (line 67). That subcommand exits 0 reporting an IDENTITY mismatch on `/workspace/implementation/src/trading_research/research/contracts/receipts.py` because the checker resolves code identity against main's working tree, which the concurrent P15-16A round is editing.
- Keani B0.2 scan p90 25.25 s dominates the 160 x 1742 projection (115 h on 17 workers, 163 h on 12). Freeze records it. Bank, dates, and coverage stay.


---

# Round 2, 2026-09-16: the three stage A verification findings

Same attempt directory `47dedaaa4f5b9ce1`. Round 1 artifacts preserved as
`THROUGHPUT_B02_run1.json`, `PROFILE_B02_run1.txt`, `B02_CONTROL_SCANS_run1/`.

## Decisions

| # | Decision |
| --- | --- |
| R2-01 | Finding 2 first: the axis-to-stage map is split by PHASE. Formation, Reference and Timing run at enumeration, before the adapter builds references and contacts, and may change the contact population. Profile, Delta, Sequence and Memory run at stage evaluation on the contacts B0.2 already enumerated. |
| R2-02 | The second hook point is a new dependency-free module `source_adapters/enumeration.py`: `ENUMERATION_KEY`, `split_b02_overrides`, `enumeration_scope` (a ContextVar scope opened by `scan_b02`) and `enumeration_point(point, payload, **ctx)`. Chosen over threading an `overrides` argument through every internal branch scanner: no internal signature changes, and with no hook installed every call is the identity, so the no-override path stays byte-identical. |
| R2-03 | Enumeration points implemented: `window` and `references` in jumbo `_scan_judas_reversal`, `_scan_other_session`, `_scan_eq_branch`; `window` and `references` in green_b02 `_scan_box_at_level` (nyam_box, previous_hour), `_scan_asia_tdo`, `_scan_cash_open`; `references` in green_b02 `_scan_vwap` and `_scan_golden_pocket`; `references` in saint `scan_saint_branch_b02`; `references` and `contacts` in sires_b02. Frozen in FREEZE.json `ra2_axis_to_stage.enumeration_support`. |
| R2-04 | Every `scan_b02` is now a thin wrapper `with enumeration_scope(overrides): return _scan_b02_impl(...)`, and `_scan_b02_impl` passes only the stage half of the overrides to `finish_scan_b02`. Nine families, seven modules. |
| R2-05 | GB-SCALP `bearish_small_scalp` and `bullish_discount_pullback` are observation-only records (`unpublished_entry`, `observation_only`) with no published reference. Their four Reference candidates join their eight Sequence candidates as unsupported-with-reason. 148 supported, 12 unsupported. Nothing dropped, nothing added. |
| R2-06 | `FAMILY_AXIS_STAGES` pins Profile on KEANI to `context, reference`: the decision operand (`fully_above`) is on the context stage, so a Profile recipe hooked only to `reference` could never move a verdict there. |
| R2-07 | CORRECTED in round 3 after independent verification; the original wording was wrong. The round 1 p90 of 25.2 s for KEANI P1 is NOT the prior-completed-session decode and the round 2 `warm_session` did not prepay it. See R3-01. |
| R2-08 | `SessionCache` is bound to the market object and memoizes every primitive on its parameter tuple: session minute bars with VWAP prefix sums, F1/F2/F3 geometry, VWAP mean and dispersion, C1/C2/C3 delta windows, the tick profile value area, band touches. Shared by every candidate on the session. |
| R2-09 | Incremental paths. GB-VWAP reference: `vwap_between` is a prefix-sum difference with `bisect`, O(log n), not a bar walk. KEANI profile: `_profile_state` keeps one tick histogram plus a cursor; `profile_value_area(end_ns)` advances the cursor with `np.add.at` over only the new slice, so the whole session's value areas cost one pass. A request behind the cursor falls back to one `np.bincount` over the prefix. |
| R2-10 | `scan_bank_session(market, resolved)` evaluates the whole bank on one loaded session; `measure_stage_a2.py` uses it for the per-session whole-bank cost. |
| R2-11 | Finding 3: recipes rewritten to reach a verdict, not only an operand. Profile recomputes the value reference from the raw tick tape (b0 or triangular b2) and re-derives `fully_above`. Delta recomputes the confirmation gate from C1/C2/C3 and recombines the stage's boolean gates. Sequence runs a real machine (S1 reclaim, S2 defended retest, S3 flow-supported reclaim, S4 failure-to-progress) and sets the trigger/confirmation verdict. Memory counts distinct prior completed contacts of the band and fails M1 above the limit, M2 without a prior favorable reaction. |
| R2-12 | `episode_operands(episode)` gives a recipe the operands of the whole episode plus its reference and geometry. Needed because SIRES `trigger` carries only `opposite_absorbed`; the contact level is on `location`/`reference`. Without it the Sequence machine had no level and added operands without moving a verdict. |
| R2-13 | `contact_ids(document)` deliberately excludes `at_ns`: a recipe that only moves a clock on the same contact must not read as a different contact population. `verdict_changed` counts an episode `research_verdict` difference, a stage verdict difference, or a contact-population difference. |
| R2-14 | Fixture date for the override proof and the positive controls is 2021-11-01, chosen because Formation F1 (3 -> 2 contacts) and Timing T4 (2 -> 1) both change count and ids there while Sequence S2 on SAINT keeps the contact set and moves stage verdicts. |
| R2-15 | Known limitation recorded in FREEZE.json `recipe_limitations`: F2 `median_sessions`, C3 `history_sessions` and a prior-session raw tape for P1/P2 all need cross-session history the account-day view does not carry. Stage A uses the in-session equivalent; stage B loads the history. Not silent: the parameter is named in the freeze. |
| R2-16 | `file_line` provenance in every rule payload shifts when a module gains lines. The RA-1 control is the same-process comparison of `scan_b02(...)` against `scan_b02(..., overrides=None)`, which is unaffected and passes 27/27. The regenerated `B02_CONTROL_SCANS/` differ from `B02_CONTROL_SCANS_run1/` by 1 to 4 bytes, all of it `file_line`. Recorded, not suppressed. |

## Commands

| Command | Exit | Result |
| --- | --- | --- |
| `pytest tests/rule_discovery/test_p15_17.py -q -p no:cacheprovider --tb=line` | 0 | 8 passed in 236.09 s |
| `measure_stage_a2.py` (20 R3 dates, 148 supported candidates, single core) | 0 | THROUGHPUT_B02.json + VERDICT_CHANGES.json |
| `profile2.py` | 0 | PROFILE_B02.txt, whole bank 63.62 s on 2024-01-02 |
| `update_freeze.py` | 0 | FREEZE.json + FREEZE.md |
| `pytest tests/rule_discovery -q -p no:cacheprovider --tb=line` (detached, PID-file waiter) | 0 | 571 passed in 3069.61 s (0:51:09) |

## Hashes (round 2)

- FREEZE.json sha256 `251030f57a973224686088714d8283d2b3a17a734efe75c52c8d8770ff274c70`
- FREEZE.md sha256 `264d656f4849e56f518e29c442f68560c5446efea558f7d72ed9b58717078968`
- THROUGHPUT_B02.json sha256 `9ddc01438d37746dec9486289f013f6f9f044e476326c459b383ab57c23a8144`
- VERDICT_CHANGES.json sha256 `3dced7149c93da05473ad5d438df6bb7f5ddfa8d51c957ec2243e5af7130d0f3`
- PROFILE_B02.txt sha256 `2b9b4939a454a295c567262e57d155cb321aa132b4c2973b48d1646453f6acc9`
- DRAFT_STUB.json sha256 `96b19051934848744ec16240f924508e21b5c82485ab2a23aab082ae33b00b66` (unchanged; pending fields left for the orchestrator)

## Skips (round 2)

- git. Forbidden by the brief. No status, no commit, no branch.
- `tools/check_foundation_adversarial.py`. Its timeout finding is environmental and handled elsewhere.
- Receipt. Not issued. DRAFT_STUB.json pending fields untouched.
- `families/*.json`. No new stage name had to be registered; the enumeration points are code, not stage names.


---

# Round 3, 2026-09-16: orchestrator follow-up after independent verification

| # | Decision |
| --- | --- |
| R3-01 | The verifier was right: round 2 `warm_session` did not prepay the cold cost. Measured directly (`probe.py`, 2024-01-02): after `load_b02_market(warm=True)` the FIRST B0.2 scan of KEANI-OPEN-ABOVE-VALUE:source_long still costs 19.8 s and the second 0.058 s; MEMBER planned_return_long 6.4 s then 0.066 s; SAINT continuation_retest 0.044 s; GB-FAIL nyam_box 0.082 s. cProfile of that cold scan: 360 calls to `historical_features.profile` (24.5 s cumulative), `dataclasses._asdict_inner` 4.7 s tottime, `copy.deepcopy` 3.5 s. So the cost is the family's OWN repeated profile construction, memoized on the market object by the first scan -- not the prior-completed-session decode, which `warm_session` already paid in 2.2 s and which returned a real value (no silent failure there). |
| R3-02 | `warm_session(market, *, branches=(), strict=False)` now has two parts: the shared data plane, and a per-(family, branch) prepay that runs each branch's B0.2 scan once and returns the baseline documents. That is the only way to prepay it: it is the same work either way. The cold cost is NOT removed, it is paid once per family-branch per session. |
| R3-03 | The blanket `except Exception: pass` is gone. Every warm step records `{"step", "error"}` in `failures`; `strict=True` re-raises. `measure_stage_a2.py` writes them to THROUGHPUT_B02.json `warm_failures` (0 over the twenty dates). |
| R3-04 | THROUGHPUT_B02.json now carries two columns per candidate, `fresh` (first scan of that family-branch on the session, after the data-plane warm only) and `warm_repeat`. The seven RA-5 candidates sit on seven distinct family-branch pairs, so one load yields the whole fresh column. The contract-formula projection is computed from the fresh column as instructed; it gives 109.32 h on 17 workers and 154.87 h on 12, both over budget, because it charges a once-per-branch cost to all 160 candidates. |
| R3-05 | Per instruction 2's fallback: the headline is now the per-session projection, in FREEZE.json `resource_profile.headline` and as the bold first row of the FREEZE.md table. per-session p90 156.90 s -> 4.47 h on 17 workers, 6.33 h on 12. FREEZE.md now states plainly that the cold cost is paid once per family-branch per session and cannot be made to disappear. |
| R3-06 | VERDICT_CHANGES.json schema v2: `rows` holds the full 2,960-row table (148 supported candidates x 20 dates) with candidate_id, date, bank, family, branch, episode_verdict_changed, stage_verdict_changed, contact_population_changed and both contact counts. `per_bank` is derived from `rows` in the same file and is independently recomputable. |
| R3-07 | The full-suite log is preserved at `logs/SUITE_round3.log` in this attempt directory. |

## Commands (round 3)

| Command | Exit | Result |
| --- | --- | --- |
| `probe.py` (cold-cost attribution) | 0 | KEANI first 19.767 s / second 0.058 s; 360 `historical_features.profile` calls |
| `measure_stage_a2.py` (20 dates, fresh + warm columns, 2,960 diff rows) | 0 | fresh p90 24.004 s, warm-repeat p90 1.056 s, per-session p90 156.90 s, 0 warm failures |
| `update_freeze3.py` | 0 | FREEZE.json + FREEZE.md |
| `pytest tests/rule_discovery tests/contracts -q -p no:cacheprovider --tb=line` (detached, PID-file waiter) | 0 | 581 passed in 2956.29 s (0:49:16); log preserved at `logs/SUITE_round3.log` |
| `pytest tests/contracts -q -p no:cacheprovider --tb=line` | 0 | 10 passed in 19.09 s; log at `logs/SUITE_round3_contracts.log` |

## Hashes (round 3)

- FREEZE.json sha256 `e06cf2765437a033e143b4e72e91bd853f4ea45f354f0c02dc524ed553099d74`
- FREEZE.md sha256 `c2abac01f4f29f20cbcdfd38065ba37b91b5d3234de2809561e844f1a2d7f069`
- THROUGHPUT_B02.json sha256 `dbdaafbdfb00781434503cd7459f538a54a0eb9fbd4461ddaa6cfa8e15575f7b`
- VERDICT_CHANGES.json sha256 `cd4e7affe92ec38c4fb7795bfe3c179dae17f988608e582e90df98552b08ba57`
- PROFILE_B02.txt sha256 `2b9b4939a454a295c567262e57d155cb321aa132b4c2973b48d1646453f6acc9`
- DRAFT_STUB.json sha256 `96b19051934848744ec16240f924508e21b5c82485ab2a23aab082ae33b00b66`
