# Wiki reconciliation after empirical v1

This record accompanies the 2026-09-12 update of the [live wiki](/workspace/planning/phase-1-live/wiki/index.md). It reconciles completed object/method implementation, post-implementation repairs, source-case corrections and the accepted empirical sample. It preserves raw sources, production code, tests, frozen rules, market inputs and original acceptance artifacts.

## Historical definition context

Empirical registry 1.0.0 includes SHA-256 identities for 190 then-current wiki pages and four executable definition files. The live wiki is intentionally newer. The ordinary validator must reject that historical registry against changed live documentation; this maintenance does not silently refresh its hashes or create a new empirical freeze.

[FROZEN_DEFINITIONS.json](FROZEN_DEFINITIONS.json) records the exact 194-file input set from accepted commit `8449573` and the hash of [empirical-v1-frozen-definitions.tar.gz](empirical-v1-frozen-definitions.tar.gz). Every archived file is individually checked against the original frozen registry. No source or rule text is reconstructed from a summary.

[verify_frozen_empirical.py](verify_frozen_empirical.py) materializes those verified files into a temporary definition root. It binds the original registry's definition-signature and input-identity functions to that root; their implementations are unchanged. It verifies that current executable inputs still equal the accepted run and that any live definition drift is confined to wiki pages. It then executes the original [verify_completed_run.py](../empirical/validation/verify_completed_run.py), including its actual native/artifact identities, schema, clock, membership, count and chart assertions. Only the destination of its verification output is redirected into this directory.

The resulting [FROZEN_RUN_VERIFICATION.json](FROZEN_RUN_VERIFICATION.json) must be byte-identical to the original [FINAL_VERIFICATION.json](../empirical/validation/FINAL_VERIFICATION.json). [VERIFICATION.json](VERIFICATION.json) separately records the current wiki hashes and every changed or added page. This is explicit archival verification of the accepted run, not validation of a new run against the updated wiki.

```sh
cd /workspace
PYTHONPATH=implementation/src implementation/.venv/bin/python implementation/reports/phase1-live/wiki-reconciliation/verify_frozen_empirical.py
```

Run the integrated tests against the updated live documentation without replacing the historical empirical test evidence:

```sh
cd /workspace
PYTHONPATH=implementation/src implementation/.venv/bin/python -m pytest implementation/tests -q --junitxml=implementation/reports/phase1-live/wiki-reconciliation/tests.xml
```

The [current status page](/workspace/planning/phase-1-live/wiki/current-status.md) is the reader's entry point. The [ingest log](/workspace/planning/phase-1-live/wiki/log.md) records one entry for each wiki page touched. This update does not establish any new source trade, fill, empirical observation or performance result.

## Verified result

- [Documentation QA](DOCUMENTATION_QA.json) passed for 191 pages: 166 objects, 12 methods, the source/observation/index/log pages, eight historical background notes and one new status page. All 4,846 local links/anchors resolve; all 465 prior raw-source reference definitions are preserved. Every method's object map and all 50 frozen branch dispositions/counts match the accepted catalogs and results. The twelve methods' SQL code blocks are unchanged.
- [Integrated tests](tests.log) passed: **736 tests and 36 subtests**, in 125.08 seconds. [JUnit evidence](tests.xml) contains 772 cases with zero failures, errors or skips.
- [Frozen-context acceptance](VERIFICATION.json) passed with 190 changed wiki pages and one new page. The original 165-job, 2,274-assignment, 2,452-record and 50-chart acceptance result reproduced byte for byte.
- [Boundary checks](BOUNDARY_CHECKS.json) confirmed that the ordinary live validator rejects the old registry against the updated wiki. Archive corruption and individual-member corruption are both rejected, including a changed member in an archive with a recomputed container digest. The original snapshot is unchanged.
- Production source, tests, CLIs, canonical FORMULAS and frozen empirical artifacts retain their accepted identities. Tracked modifications are confined to the wiki; new reconciliation artifacts are stored here. `git diff --check` passed.
