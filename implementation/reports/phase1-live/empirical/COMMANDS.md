# Empirical commands

Run from `/workspace` with the existing virtual environment. These commands
belong to this empirical extension; earlier Phase1 acceptance stays unchanged.

```bash
implementation/.venv/bin/python implementation/tools/run_phase1_empirical.py calibrate
implementation/.venv/bin/python implementation/tools/run_phase1_empirical.py freeze
implementation/.venv/bin/python implementation/tools/run_phase1_empirical.py validate
implementation/.venv/bin/python implementation/tools/run_phase1_empirical.py run --cohort bar-monthly --max-partitions 1
implementation/.venv/bin/python implementation/tools/run_phase1_empirical.py run --cohort tape-annual-trades --max-partitions 1
implementation/.venv/bin/python implementation/tools/run_phase1_empirical.py report
implementation/.venv/bin/python implementation/tools/run_phase1_empirical.py run --workers 4
implementation/.venv/bin/python implementation/tools/run_phase1_empirical.py report
PYTHONPATH=implementation/src implementation/.venv/bin/python -m trading_research.research.method_pack.empirical_charts
implementation/.venv/bin/python implementation/tools/validate_phase1_empirical_baseline.py
PYTHONPATH=implementation/src implementation/.venv/bin/python -m pytest implementation/tests -q --junitxml=implementation/reports/phase1-live/empirical/validation/final-tests.xml
```

`freeze` refuses to overwrite an existing run. `validate` checks the registry,
implementation, calibration and exact coverage-split/job membership. `run`
checks full native input hashes, processes one bounded instrument/date at a
time, validates typed opportunities and endpoints, and writes artifacts only
after the immutable registry batch exits successfully. Each checkpoint binds
its exact job, artifact and complete rule-scope summaries.

Up to four independent date processes can run concurrently with `--workers 4`; each retains the same bounded-input and publication checks. Resume all remaining jobs with the same `run` command. Completed jobs are
verified and skipped; they are not appended again. To execute one declared
partition, pass its exact `job_id` from `RUN_MANIFEST.json`:

```bash
implementation/.venv/bin/python implementation/tools/run_phase1_empirical.py run --job-id '<exact frozen job_id>'
```

Code or rule changes after evaluation exposure require an explicit revision
record and a refreshed run identity. They cannot silently reuse old
checkpoints or relabel previous results as newly tested.

The sampled cohorts are monthly native-bar sessions and annual standalone
trade sessions. They are coverage-selected samples, not an exhaustive census.
Missing reference/action coverage is recorded separately from completed-zero
searches. Rates measure named observable sequences; actual discretionary
selections, attempts, orders, fills and profitability remain unavailable.

## Recorded implementation repair

The initial exposed run is preserved under `revisions/run-v1/`. Its large
artifacts remain at their original absolute paths. `EVALUATION_EXPOSURE.json`
records the defect, saved checkpoints and conservative exposure scope.

The recorded `revise-reporting` operations create run versions 1.0.1 and 1.0.2 after
fresh calibration. Version 1.0.2 repairs the reporter’s validation of the versioned
artifact directory; the exposed 1.0.1 run is preserved under `revisions/run-v1.0.1/`. It refuses changed rules, dates, inputs or selector code;
only the reviewed reporter/orchestration fixes and the unchanged-semantics
per-file tape metadata cache are allowed. It also refuses to relabel existing
checkpoints. Every declared job is recomputed into a new run-hash directory.
The fresh test identity and independent review document the repaired code.

```bash
implementation/.venv/bin/python implementation/tools/run_phase1_empirical.py calibrate
implementation/.venv/bin/python implementation/tools/run_phase1_empirical.py revise-reporting
implementation/.venv/bin/python implementation/tools/run_phase1_empirical.py validate
implementation/.venv/bin/python implementation/tools/run_phase1_empirical.py run --workers 4
```

These revision commands record the actual repair, not an optimization
workflow. After version 1.0.2, `revise-reporting` refuses to run again. Use the ordinary validated `run` command to resume remaining partitions.

## Final acceptance verification

After the full report and reviewed chart index exist, run:

```bash
PYTHONPATH=implementation/src implementation/.venv/bin/python implementation/reports/phase1-live/empirical/validation/verify_completed_run.py
```

This checks all 165 jobs and 2,274 rule/partition assignments, exact artifact
identities, typed clocks, observed-count reconciliation at every report level,
tested source/test/tool hashes and the deterministic scored-record chart links.
It requires `charts/VISUAL_REVIEW.json` covering every selected chart; it does
not infer visual review merely from chart generation.
