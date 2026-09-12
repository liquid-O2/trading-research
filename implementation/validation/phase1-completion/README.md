# Phase 1 completion evidence

The current [acceptance record](final-acceptance.json), [obligation matrix](obligation-matrix.json), [test record](test-run.json), and [runner record](runner-checks.json) describe the completed implementation. The [completion report](../../reports/phase1-live/methods/COMPLETION_REPORT.md) links the twelve method summaries and reviewed charts.

Git contains the implementation, tests, source-case manifests, review ledgers, charts, bounded native validation evidence, and report summaries. Following the repository's storage rules, raw `/workspace/data`, full method JSON coverage/trace runs, oversized copies of earlier reports, and the derived Parquet control remain on disk. Their paths and hashes are retained in the evidence records. A checkout alone does not contain those local artifacts.

Full verification requires the retained data and generated artifacts. Use the commands in the completion report and chart gallery to rebuild them; rerun the recorded method commands after implementation changes. Rebuilding changes run paths and report identities, so refresh the linked evidence through the documented validation workflow rather than treating an old hash as a new result.

`report-status-correction/` records the separately reviewed reporting fix. Implementation checks now report `checks_passed` or `implementation_fail`; source reconstruction and historical discovery retain their own results.
