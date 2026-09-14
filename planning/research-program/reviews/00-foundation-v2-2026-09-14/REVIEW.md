# Foundation v2 review — 2026-09-14

**Verdict: 00-foundation still needs repair before 01-native-and-outcomes.** The earlier 27-case failures are repaired, but the current verifier accepts ten additional invalid submissions. These findings concern requirements already present in [ASSURANCE.md](/workspace/planning/research-program/ASSURANCE.md); they do not introduce another plan amendment.

This review covers P15-00 `91ade001fb32cb9b`, P15-01 `7da6cc99d954e280`, subphase `240838146c38c484` and its current GATE_REVIEW. [INPUT_IDENTITIES.json](/workspace/planning/research-program/reviews/00-foundation-v2-2026-09-14/INPUT_IDENTITIES.json) records the exact source and receipt hashes. Source, accepted outputs and the pinned checker were not edited during this review.

| Verification | Observed result |
| --- | --- |
| Independent rerun of the two foundation test files | 45 passed in 115.47 seconds |
| Pinned foundation checker on the actual new receipts | 27/27 passed; checker hash unchanged |
| Actual candidate with its actual `--gate-review` | Exit 0 |
| Additional public CLI probes | Four controls behaved correctly; ten invalid submissions returned exit 0 instead of 2 |
| Accepted Phase 1 software and historical foundation evidence | All 248 registered software hashes and 16 original task-artifact hashes match; original three receipt hashes unchanged |

The saved [fixed-suite result](/workspace/planning/research-program/reviews/00-foundation-v2-2026-09-14/FIXED_SUITE_RESULTS.json), [additional results](/workspace/planning/research-program/reviews/00-foundation-v2-2026-09-14/additional-suite/RESULTS.json) and [preservation check](/workspace/planning/research-program/reviews/00-foundation-v2-2026-09-14/PRESERVATION_CHECK.json) support these observations. The pytest command was `.venv/bin/python -m pytest tests/rule_discovery/test_p15_00.py tests/rule_discovery/test_p15_01.py -q -p no:cacheprovider`, from `/workspace/implementation`; its result above was recorded from the review tool output.

## What the transcript's attention and errors mean

The latest public Grok completion says the parent Grok model both implemented and reviewed the change, with no separate worker reviewing the diff. That is a review limitation, not a runtime failure. One code writer does not itself prevent a separate read-only review.

The later background notification identifies an earlier P15-00 pytest job, `call-92ac21fa-352d-4d51-8a9d-979daac9b38d-266`, terminated by signal 15 after 212 seconds. That job did not pass. Grok's final response identifies the later 45-test run as the completion run; this review independently reran those tests successfully, so the stopped job is not the remaining blocker. The notification does not establish who sent SIGTERM or why.

An intermediate combined run failed `test_s04_valid_phase_1_5_miniature`: 1 failed, 44 passed. The phase verifier was resolving a predecessor from the default report tree instead of the fixture's `--receipts-root`, producing `PREDECESSOR_HASH`. The transcript then records the passthrough fix; the passing rerun confirms that test now succeeds. A text replacement in DECISIONS.tsv also initially failed to match and was subsequently applied successfully. Neither explains away the current acceptance defects below.

Only public assistant messages, command results and the background notification were used for this transcript assessment. [TRANSCRIPT_REVIEW.json](/workspace/planning/research-program/reviews/00-foundation-v2-2026-09-14/TRANSCRIPT_REVIEW.json) preserves their source locations and relevant excerpts.

## Blocking findings

1. **[P1] The final review check accepts missing review content and fabricated results.** In [receipts.py](/workspace/implementation/src/trading_research/research/contracts/receipts.py:927), a successfully parsed non-object returns an empty failure list. An actual foundation candidate with a review containing only `[]` therefore passes. A second probe substitutes an independent-results object containing 27 null entries, no harness hash, arbitrary input keys and a hash different from the declared results hash; it also passes. A third removes code snapshots, evidence matrices, graph and command bindings, sets an unknown review subphase and supplies no reviewed task IDs; it passes too. The verifier checks neither all required bindings nor actual result-case identities. This makes `--gate-review` insufficient for downstream admission. Cases: `review_nonobject`, `review_null_cases`, `review_missing_bindings`.

2. **[P1] A passing task can have entirely failed or nonexistent supporting evidence.** In [receipts.py](/workspace/implementation/src/trading_research/research/contracts/receipts.py:675), `fail` is a supported matrix status, but it is not reconciled with acceptance flags or the task's successful disposition. Setting every matrix row to `fail` and clearing evidence, code references, test nodes and command indices still yields exit 0. Keeping `pass` while replacing every symbol, test node and evidence selector with a nonexistent name also succeeds: existence of a file is checked, but those references are not resolved. Both probes correctly refresh changed file hashes, so this is a content-validation failure. Cases: `matrix_failed_checks`, `matrix_nonexistent_references`.

3. **[P1] Snapshot identities are recomputed from declarations without verifying the declared source bytes and required copies.** In [receipts.py](/workspace/implementation/src/trading_research/research/contracts/receipts.py:785), code identity is the hash of the snapshot document. The underlying source-file hashes and code copies are never checked. A code snapshot claiming an all-zero hash for baseline_manifest.py passes after consistently rebinding the draft, run ID and manifest hashes, despite having no preserved code copies. A separate plan snapshot with an empty `snapshot_paths` map also passes. The existing requirement calls for an exact required file inventory, matching preserved copies and recomputation of actual file hashes. Cases: `code_false_file_hash`, `plan_no_preserved_copies`.

4. **[P1] A declared artifact schema can disagree with its contents.** In [receipts.py](/workspace/implementation/src/trading_research/research/contracts/receipts.py:747), the schema mismatch predicate requires both `schema` and `schema_version` to be present and disagree. With the usual single version field, the missing other field suppresses the failure. Replacing SCHEMA_EXAMPLES.json with an unrelated object whose version is `research-wrong-v900`, while refreshing its manifest and evidence hashes, is accepted under the original declared schema. Case: `artifact_wrong_schema`.

5. **[P1] Lineage evidence can omit its availability/path or cite nonexistent rows.** In [receipts.py](/workspace/implementation/src/trading_research/research/contracts/receipts.py:1272), clocks are only checked when supplied, and evidence leaves need only a hash and nonempty row list. A feature leaf below root issue 10, with event 100, no availability clock, no artifact path and a nonexistent row passes. Providing a real correctly hashed artifact with an invented row ID also passes because row IDs are not resolved. An explicit late availability clock is correctly rejected, confirming that omission bypasses the otherwise functioning cutoff check. Cases: `lineage_missing_clock_and_path`, `lineage_nonexistent_row`.

These are reproducible software-acceptance failures, not evidence that the recorded market research outcomes are wrong. The repaired constructor checks, previous negative cases and targeted tests do pass. The pinned 27-case suite is explicitly a minimum suite; it does not cover all of the review-sidecar, matrix, snapshot and lineage-content requirements above. The current task tests likewise do not exercise these counterexamples.

## Reproduction and handoff

[additional_probe.py](/workspace/planning/research-program/reviews/00-foundation-v2-2026-09-14/additional_probe.py) uses the public verifier CLI, creates isolated files and preserves each command, expected exit, actual exit and output. The saved run contains 14 cases: ten invalid acceptances, three valid accepted controls and one correctly rejected late-clock control. Exit 1 means the review harness detected expectation mismatches; it is not a harness crash. The individual fixtures and RESULT.json files are retained under `additional-suite/` with their original absolute paths.

The [single Grok repair prompt](/workspace/planning/research-program/reviews/00-foundation-v2-2026-09-14/REPAIR_PROMPT.md) targets these existing requirements. Preserve both v1 and the reviewed v2 outputs, repair the validation logic and its producers together, add discriminating tests, then issue new immutable attempts and a fresh review. Do not start 01 from the current GATE_REVIEW's `pass` claim.
