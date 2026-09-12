# Phase 1 lifecycle correctness evidence

`original-check/` preserves the unchanged independent negative review, probe script and original six inputs/results with a hash manifest. `previous-acceptance/` preserves the earlier passing acceptance, tests and obligation ledgers; its large `method-reports/` copies remain local and are indexed by `method-report-preservation.json`.

`probe_lifecycles.py` is the original unchanged diagnostic; `lifecycle-probes.json` is its latest run. `repair-regressions.json` records the exact six cases with current source fingerprints and full schema/admission checks. `repair-review.json` records the parent's behavioral and obligation review. `runner-*.json` retain the twelve fresh method commands and output hashes.

See [the repair report](../../reports/phase1-live/methods/POST_IMPLEMENTATION_REPAIR.md) for the result and [completion reproducibility](../../reports/phase1-live/methods/COMPLETION_REPORT.md#validation-and-reproducibility) for commands. Bulk market data stays ignored under `/workspace/data`; no historical discovery or performance claim is made.
