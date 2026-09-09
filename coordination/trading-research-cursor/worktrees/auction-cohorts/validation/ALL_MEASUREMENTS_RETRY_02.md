# Combined measurements: second shared attempt

The first shared execution, `68b8120118d447aea09c4faec58197f7`, completed with 34 errors, no assertion failures, and five skipped entries. It ran 783 tests in the environment available to that worker. Missing pinned data dependencies prevented discovery or execution of some existing assertions, so those counts do not represent a complete successful suite. The immutable [failed summary](../reports/all-measurements-location-label-decision-v1-verification-68b8120118d4.json) retains all diagnostics, source bytes and family attribution.

The worker used 83.442069 CPU seconds, 116.883178 wall seconds, and 182,116,352 bytes peak RSS. Its failed attempt remains charged to each participating family as the same physical run. The original three-attempt, 600-CPU-second family budgets and per-run limits remain unchanged.

One post-execution repair addresses all 34 errors, grouped into 14 causes, and the dependency skips. Three bounded Luna max tasks repaired independent fixture interfaces, identities and authenticity assertions. An Astra low check examined the completed-measurement publication boundary; its one availability-order finding was fixed. Root integrated the public receipt change, journal restore, presentation clock and evidence records. No candidate test, compilation, import or private retry occurred during that repair.

Completed measurements retain their original computation clocks in the result digest. The producer checks source availability at that original cut; F10 then receives the completed result at publication. Existing F10 external-input gates remain intact. Actual birth/expiry, source corrections and frozen historical targets remain asserted. Other fixes preserve typed integer trade inputs, independent source identities, exact local fold limits and the full durable SQLite journal.

The [repair report](../reports/all-measurements-consolidated-repairs-retry-02.json) maps every observed error to its cause and repair. Original reviews, contracts, registrations, goldens, first-attempt coverage maps and failed receipts remain immutable. New coverage paths bind the repaired source bytes for this attempt. The original combined review and initial consolidated repair are retained separately from this post-execution repair.

The retry command uses the existing pinned data environment:

```bash
PYTHONPATH=src /tmp/trading-research-venv/bin/python tools/verify_engineering_batch.py reports/all-measurements-batch-retry-02.json
```

The retry includes all static assertion identities and every previously passing baseline assertion. It retains the 180-second CPU reservation, 190-second CPU hard limit, 4-GiB address-space limit and 240-second wall limit. Only a complete successful supervised result can be attached as engineering evidence.

The user's new [period policy](../RESEARCH_PERIOD.md) sets subsequent primary-model cohorts to 2020 onward. Older data remains optional for selected Jumbo/OHLC uses. This synthetic engineering batch does not establish native-source completeness, predictive value, economic performance or completion of B00–B10.
