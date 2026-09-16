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

