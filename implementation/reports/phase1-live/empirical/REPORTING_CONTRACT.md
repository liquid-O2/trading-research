# Empirical reporting contract

`empirical_reporting.py` is the read-only boundary between a frozen empirical
run and its report. It reads the candidate registry, `RUN_MANIFEST.json`, one
checkpoint per manifest job, and the corresponding `records.json` artifact.
It does not search market data and does not infer a source method's private
selection, order, fill, or verdict.

## Inputs

The default root is
`implementation/reports/phase1-live/empirical`. The reporter expects:

```text
registry/CANDIDATE_REGISTRY.json
RUN_MANIFEST.json
checkpoints/{cohort}--{partition_id}.json
artifacts/{cohort}--{partition_id}/records.json
```

The run manifest contains the frozen `jobs` list. A job has a unique
`job_id`, `cohort`, original coverage `partition`, and exact `rule_ids` list.
The checkpoint repeats the job identity and stores `job_sha256`,
`registry_sha256`, `run_manifest_sha256` (the runner's historical
`manifest_sha256` spelling is accepted), `implementation_sha256`,
`search_completed: true`, the canonical artifact path and its byte hash, and
one summary row for every rule in the job.

The artifact contains the job identity, `records`, and an exact copy of the
checkpoint `rules` rows. Artifact bytes are hashed as written. A checkpoint
whose filename, job identity, artifact path, hashes, rule set, summary, or
record identity disagrees with its manifest is invalid. Missing checkpoints
are reported as unfinished scope; they are never counted as zero outcomes.

Registry and manifest self hashes are SHA-256 over canonical JSON: UTF-8
JSON, sorted keys, compact separators, and the self-hash field omitted. Job
hashes use the same canonical encoding. Artifact hashes use the complete raw
file bytes.

## Denominators and grouping

The primary denominator is one row per observed initial market opportunity.
For each record, `pass` and `fail` contribute to `n = p + f`, while `unknown`
contributes to `u`; `N = p + f + u`. The rate is `p / n` and the interval is
`[p/N, (p+u)/N]`. A missing-data rule has null counts and rates for that
population; the reporter never converts unavailable input into zero.

Metrics are grouped by rule, cohort, calendar year, native instrument ID,
evidence mode, and observation unit. Rates are not pooled across incompatible
groups. Rule and family totals are additive counts only and expose a null
rate. Actual selections, attempts, orders, fills, and P&L remain unavailable
unless separately supplied by an authorized ledger; they are not inferred
from passing comparison endpoints.

All registry rules appear in `RESULTS.json`, including unsupported/source-only
branches and their disposition. `extra_observation_units` are emitted as
separate supplied-only units with null empirical metrics. These process,
state, management, and risk observations remain separate from market
opportunities.

## Outputs

`write_results(root)` writes `RESULTS.json` and `RESULTS.md` atomically. The
JSON document contains validation errors and warnings, cohort scope
(`eligible`, `scanned`, `missing`, `remaining`), grouped metrics, all rule and
extra-unit dispositions, family summaries, and audit rows. Multiple
implementation hashes are a warning so an exposure revision is visible while
the underlying artifact identities remain auditable.

The Markdown document prints the required tables after the family reports:

```text
family | variant | n | faithful_disagreements | status | report path
family | id | verdict | fixture | leakage | proxy-as-faithful | notes
```

`faithful_disagreements` is null unless a paired source-faithful observation
is explicitly supplied. `source_assembly` is retained for audit, but a
proxy-as-faithful or timing/leakage count makes the report invalid.

The module can also be run directly:

```bash
PYTHONPATH=implementation/src python -m trading_research.research.method_pack.empirical_reporting \
  --root implementation/reports/phase1-live/empirical
```

