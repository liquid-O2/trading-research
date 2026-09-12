# Independent selector and run review

Astra Low independent review, 2026-09-12. This review used code, the draft candidate registry, live FORMULAS/source-case references, and synthetic controls only. No historical evaluation scan or evaluation outcome was inspected. Scope: `empirical_bar_engine.py`, `empirical_market.py`, `empirical_binding.py`, `empirical_selectors.py`; additional review of `empirical_runner.py` after the lead requested it. M09 tape execution and its native assembly bridge have a separate implementation owner; this report does not claim a complete independent tape audit.

## Findings and disposition

| ID | Priority | Finding | Initial disposition (rechecked below) |
|---|---|---|---|
| SR-01 | P1 | MSS completed-reclaim reference was backdated to parent sweep availability; child occurrence was fabricated as completion minus one nanosecond. A completed prerequisite must be known at completion. | Lead corrected reference availability to parent completion and added explicit point-event occurrence. Three independent MSS tests pass, including mature-prefix invariance and missing postparent candle. |
| SR-02 | P1 | A 35-calendar-day BarMarket lookback cannot reconstruct the whole preceding month for late-month evaluation dates, even where acquired data exists. Artificial truncation is not a source/data hole. | Lead changed BarMarket to 62 days and is regenerating coverage. Run freeze now rejects lookback below 62. Verify regenerated split membership before acceptance. |
| SR-03 | P1 | Prior profiles were admitted by instrument plus early availability alone. A stale same-instrument profile could replace the immediately preceding weekday RTH profile; M08 did not independently check its frozen 70% contiguous expansion policy. | Reproduced: `test_opening_state_rejects_stale_same_instrument_profile` failed because a seven-day-old synthetic profile was accepted. Lead delegated production correction to tape agent. Retain regression and rerun after integration. |
| SR-04 | P1 | Resume accepts an existing checkpoint using run/implementation hashes and referenced artifact hash, but initially omitted exact checkpoint job/partition/date/instrument/registry/rule membership. Another job's valid checkpoint could skip an unscanned partition. | Reported to lead and regression added. Require exact expected identity, rule coverage and completion status before skipping. |
| SR-05 | P1 | `validate_run` initially checked split file hashes and job-ID uniqueness without reconstructing the exact jobs/rules from frozen splits. Logical omissions or reassignment could pass if manifest hash was recomputed. | Reported to lead. Validate complete partition-by-cohort membership and exact rule routing, including missing/extra/duplicate logical jobs. Checkpoint summary integrity must be bound or recomputed from artifact records. |
| SR-06 | P2 | Readable rules ambiguously said first later close/retest that satisfies a condition, while kernels intentionally score only the next close or first retest. These are different endpoints. | Lead explicitly confirmed next-close-only for M01/M02 and first-retest-only for M06 continuation/trapped comparison. Reviewer updated registry parameters/readable rules before freeze; draft hash `576037153a15375396fa37a24dfa491e0a9d9388aed99aa9b52a2a9c0f26eec6`. MSS remains a first postparent-gap appearance endpoint. |

## Selector observations

- M01 uses the declared outer 06:00–09:00 parent for its beyond-edge 1.33/1.66 bands. Internal rotation is explicitly a midpoint-to-edge path; its contact-close side is a research path convention, not a discretionary order.
- M02 creates opportunities at initial per-side/reference sweeps. Failed next-close confirmation remains in the denominator. Box routes additionally require return within both bounds; single-line references do not manufacture a box. Cash and TDO are explicitly minute opens available at minute end. Previous period references preserve same-contract identity and require all prior weekdays.
- MSS children are conditional observations over confirmed NYAM parent reclaims. All three 2-minute candles start after the parent completion, beginning at the next aligned grid boundary; parent counts and child counts remain different populations. Missing initial child coverage cannot be skipped to find a favorable later gap.
- M03 uses completed independent Asia/London references, a one-minute breakout and a later touch of a pre-bar VWAP. No defended-close condition is imposed. The source's unpublished VWAP settings and admission remain unknown.
- M05 freezes the touched pre-bar deviation band and scores only the first later aligned 5-minute close. Simultaneous upper/lower trigger contacts are retained as ambiguous side opportunities. It does not turn reentry into source absorption or ladder confirmation.
- M06 comparison names disclose omitted source context: boundary retest, positive-delta upper failure, prior-boundary return to POC, and POC crossing/hold. They do not reconstruct source two-prior-failure episodes or older-value exploration. First-retouch failures remain failed observations. POC streak ties reset; unresolved completed horizons are explicit unknowns.
- M08 initially observes every covered opening minute and only later classifies the full A period. Missing prior value can remain an unknown opening observation; the denominator does not select only above-value openings. Exact profile parent/configuration admission was the substantive gap in SR-03.
- The semantic binding layer restricts research roles to a narrow numerical/availability allowlist. It does not supply source context, actual O150 decisions, private admission, source VWAP verification, risk, orders or fills. The assembled complete source method remains separately scored and non-faithful.

## Independent controls

New file: `/workspace/implementation/tests/test_empirical_bar_review.py`.

The initial four-test run produced three passing MSS controls and one failing stale-profile rejection, reproducing SR-03. A checkpoint-substitution rejection was then added for SR-04. These are synthetic adversarial controls, excluded from all historical counts. Production repair and rerun results must be appended below; initial failures are preserved as review history.

At initial review, acceptance was pending correction/recheck of the findings. See repair recheck below for their resolution. The lead's full integration gates remain separate; this report is not an empirical completion certificate.

## Repair recheck

After production repairs, the independent review file passed all 22 tests, including positive synthetic controls for each of the 14 bar-routed branches, complete/incomplete M08 opening-state populations, exact stale-profile/configuration rejection, MSS point clocks/postparent ordering/mature-prefix invariance, checkpoint substitution rejection, and rehashed split-partition omission rejection.

Combined command: `PYTHONPATH=implementation/src python -m pytest -q implementation/tests/test_empirical_bar_review.py implementation/tests/test_empirical_registry.py implementation/tests/test_empirical_selectors.py implementation/tests/test_empirical_pipeline.py`. Result: **49 passed, 34 subtests passed**, 32.07 seconds. Native pipeline controls use locally generated synthetic files, not historical evaluation records.

SR-01 through SR-06 are corrected in the reviewed production snapshot. In addition to the direct regressions, code inspection confirms exact cohort membership is required and the entire checkpoint rule scope (including statuses, population holes and references) is bound to the hashed artifact and checked on resume. The 62-day reference requirement is enforced before run freeze. Final actual coverage/scanning/completion gates remain the lead’s responsibility.

A bounded follow-up review of `empirical_tape_binding.py` found no new blocking issue: exact physical formation/touch IDs resolve against frozen source-file hashes; selected-subset coverage is not promoted to continuous coverage; O098 evidence does not invent a private selection, order or fill. A focused read of M09 pairing/timestamp batches found the frozen nonoverlapping-pair, ambiguous-batch exclusion, immutable-zone and later-timestamp response rules reflected in code. This remains a bounded bridge/lifecycle review, not an exhaustive independent tape audit.

### Reviewed production identity

These hashes identify the reviewed code snapshot. Later source changes require the lead to rerun affected controls and update final tested-code identity; this note does not certify unseen changes.

| File | SHA-256 |
|---|---|
| empirical_bar_engine.py | `cd3a84afe28e8c8223c241f61c87425bec38d53fffd3d53a9e486250896c3c13` |
| empirical_market.py | `ae20acfb5b72fff88da1be694fec0d8441376a2cbcaa23508504ea343c3f0671` |
| empirical_binding.py | `2957a91cbabf374e226ee84b888b8a8e4a55bdb9b376a9c4690028d966bf5383` |
| empirical_selectors.py | `29a51b16fc78a088d221e7b00800aed191f399e7d1d4f469d2be3a574d81ef0e` |
| empirical_protocol.py | `d190521cc37b088c838676c7cb3b3fdf31b740a592b2c5097cd64e567f692745` |
| empirical_registry.py | `6a5b3209dbeca231719a13cb1902a3f44b1b2ff54c4e9a026cbcb61091166152` |
| empirical_runner.py | `b6f5d50c1cd63fce2979728d47d626a1d5d5dcef91d5dfaa7a00ef2286d9ef94` |
| empirical_tape_binding.py | `bfb112dcc3064bda34383cd54f3f6c07b91234b1b12c66f0cfd03bc449b2a6ee` |
| empirical_tape.py | `2a6b05836079eb333fd41f720e94cefab89b49d3c1eefdc430403d2c9277d3f7` |

### Native path-cache follow-up

The lead changed WindowPrefixResolver construction to canonicalize each distinct row source path once instead of repeating realpath traversal for every minute. Review confirms native locator dataset/hash checks, source-stat freshness admission, contradictory-member rejection and per-resolution identity checks remain present. Existing native and physical pipeline regression command: `PYTHONPATH=implementation/src python -m pytest -q implementation/tests/test_empirical_native.py implementation/tests/test_empirical_pipeline.py`; **18 passed** in 14.15 seconds. Reviewed `empirical_native.py` SHA-256: `53486302aab3a8035089bfefec89b65adbc69c00eccb6dbd7b7eef757c6bfeb4`. No historical evaluation outcomes were involved.
