# Trading research implementation

**Active direction, revised by the user on 2026-09-07:** validated statistics and
timings, independently tested Context, and evaluated Locations, with full rigor
and implementation detail across every family. Read the
[active plan](../planning/trading-research/PLAN.md),
[shared research specification](../planning/trading-research/RESEARCH_SPEC.md)
and [implementation instructions](../planning/trading-research/IMPLEMENTATION_INSTRUCTIONS.md).

This package retains partial B00–B03 references and later runtime/account machinery
from the [archived program](../planning/archives/2026-09-07-before-research-rescope/README.md).
Source/definition and data gates remain incomplete; no real-market prediction
comparison or complete E0 economic run has finished in the recorded evidence.
The old B00–B10 ledger remains historical evidence. E0 and full trading/live
readiness no longer govern current research completion. See [PLAN_UPDATE.md](PLAN_UPDATE.md).

The primary model uses 2020 onward. Older data is optional for selected Jumbo
and OHLC work; [the period policy](RESEARCH_PERIOD.md) records the cohort boundary.

Read [the active delivery table](../planning/trading-research/STATUS.md) for current
research outcomes and next work. [`CONFORMANCE_AUDIT.md`](CONFORMANCE_AUDIT.md),
[`DESIGN_REVIEW.md`](DESIGN_REVIEW.md) and [`STATUS.md`](STATUS.md) retain the detailed
engineering/evidence history and limitations. Original source/data and the frozen
historical plan remain inputs; `/workspace/archive` is excluded.

## Existing verification interfaces

These commands address the retained implementation and historical scope. Their
full B00–B10 completeness checks do not define current research delivery. Use
the applicable checks under the active plan and preserve existing explicit
review/testing and registered resource limits.

Use Python 3.12 and the pinned lock file:

```bash
cd /workspace/trading-research
uv sync --extra data
uv run python -m trading_research import-scope
uv run python -m trading_research.verify all --require-traceability
uv run python -m trading_research audit
```

The complete suite requires the data extra. Missing optional reader dependencies
are reported as skipped tests and prevent an all-suite success claim. These
smaller backlog interfaces also exist:

```bash
uv run python -m trading_research.verify contracts --suite all
uv run python -m trading_research.verify registry --require-traceability
uv run python -m trading_research.verify labels --fixtures hand_checked
uv run python -m trading_research.verify provenance --fixtures mutation_and_restart
uv run python -m trading_research.verify market-data
```

The explicitly bounded reader pilot reads four fixed prefixes of at most 4,096
rows each, including the documented NQ bit-4 row group:

```bash
uv run python -m trading_research.data.audit mbp-pilot --max-rows 4096
```

Each pilot is registered before execution. Retries retain their prior attempt,
resource use and result. The family allows at most 12 attempts within its
600 CPU-second accounting budget. Separate optional workers now have CPU/RAM/wall
bounds and independent risk timers tested in synthetic fixtures; this is not
live broker readiness. The pilot bounds records, Parquet batch size and native
compressed input bytes. Do not use its throughput to launch an unmeasured full
archive scan.

`audit --require-complete` intentionally fails while required work remains.
`import-scope` verifies the governing input hashes and preserves existing status.
A changed definition requires an explicit `Ledger.migrate_scope(...)` with a
reason and revalidation; neither command silently resets evidence.

## Contents

| Package | Current functionality |
|---|---|
| `foundations` | Exact quantities, distinct clocks, immutable messages and targets, typed dependency graph, instrument/calendar versions, shared trade/activity bars and immutable object lineage |
| `research` | Literal fixed-end path labels, ambiguous/censored outcomes, chronological date-group folds, transitive fitted-artifact exclusion and committed supplied-model serving |
| `data` | Lossless raw values, bounded QuantPad/native DBN readers, MBP normalization, BBO and trade-volume projection, separate book/flow quality and explicit recovery certificates |
| `operations` | Complete scope import, committed semantic artifact closures, immutable source snapshots, append-only evidence, actual input-read audit and family/trial/attempt accounting |
| `runtime` | Durable availability/scheduler references, typed ports, deterministic arrival traces, local raw-journal boundaries and synthetic fault replay |

The as-of index still uses the literal backward-join function after narrowing
the input prefix. Its tests establish reference behavior and restart stability;
they do not claim an independently optimized join. The book reducer retains
source-row keys in memory as a reference implementation. Native bytes and
Parquet floating-point bit patterns remain available alongside normalized data.

Calendar tests cover synthetic sessions, real timezone transitions and dated
cash-RTH publications. They do not certify CME or broker deadlines. Raw contract
definitions and an external NQ multiplier reference retain distinct provenance;
full roll-universe eligibility remains unresolved.
Missing strategy receipts remain `None`; pilot timing uses named assumptions.

## Evidence

`evidence/events/` contains immutable, hash-linked implementation transactions.
`evidence/artifacts/` contains definitions, reconstructible source snapshots and
executed test results. `evidence/trials/` contains the pilot protocol, immutable
configuration, every started/finished attempt and pilot artifacts. Test evidence
covers its named assertions, not every obligation of a parent, child or P0–P7
phase. Engineering, research disposition and economic results remain separate.

The latest [combined engineering execution](validation/ALL_MEASUREMENTS_EXECUTION.md)
passed all 851 methods on its third registered run, with both earlier failures
retained and no skipped tests. Native cohort, complete
consumer, market prediction and economic gates remain separate requirements.
