# Phase 1 method pack

The public command runs fixtures, inventories acquired coverage, binds any supplied C01 episodes, scores the selected FORMULAS predicates, and writes the report and its trace artifacts in one pass.

From `/workspace`:

```bash
python implementation/tools/run_phase1_objects.py method-pass --method JJ-TBR --scope acquired --data-root /workspace/data --report-root /workspace/implementation/reports/phase1-live/methods --formula-version method-pack-v1
```

The twelve method IDs and their exact object inventories are in `catalog.py`. `contracts.py` hashes the consumed C00–C08, method and object sections directly from `planning/phase-1-live/FORMULAS.md`. `expressions.py` evaluates that pack's expressions with nullable Boolean logic. The method modules add the identity, availability and lifecycle checks specified in the accompanying prose.

`--episodes PATH` optionally reads a JSON C01 manifest with `formula_version`, `candidates`, `objects`, `assertions` and `evidence` arrays. Each operand references a permitted object or assertion producer. Source observations, immutable identities, field types, actual availability and source versions travel with those records. The report's `operand_contract` lists the accepted fields, types and producers. Fixture constructors create explicitly synthetic observations; fixture rows are excluded from historical counts.

Without a source-complete candidate selector or a supplied episode manifest, historical candidate files are empty and the report retains every affected branch and its discovery hole. Unpublished engines remain unavailable. Separate predicates retain separate cohort denominators, including management, re-entry, selected orders, state transitions and process reviews. A later outcome cannot repair an entry prerequisite.

Reports are `<slug>.json` and `<slug>.md`. The JSON records paths, counts and SHA-256 hashes for immutable trace artifacts under `<slug>/run-*/`. Historical and supplied cohorts also remain partitioned by instrument, evidence mode and source version. `n=p+f`, `N=p+f+u`, and the missingness interval is `[p/N,(p+u)/N]`; empty denominators have null rates and intervals.

Git retains the readable method reports, command results and verification summary. Full machine reports and trace directories remain on disk because acquired coverage dumps can exceed 100 MB per file. Their paths and hashes stay in `pass-summary.json`; rerunning the public command above regenerates those local artifacts. Raw `/workspace/data` and the large exported trade/BBO streams remain outside Git.

Exit codes are `0` for a completed contract, including correctly reported holes; `1` for an implementation or report failure; and `2` for an invalid command, configuration or episode schema. The acquired data root is read-only.

Install the declared optional dependencies with `python -m pip install -e './implementation[data,research,test]'`. Local checks use disposable fixtures:

```bash
PYTHONPATH=implementation/src python -m pytest -q implementation/tests
python implementation/tools/check_object_fixtures.py
```

The `data` extra supports acquired Parquet inspection. The `research` extra is needed by the existing Phase 1 regression suite; this method pass does not start a new simulation or parameter search.

Bounded NQ trade, BBO and time-bar views can be exported from the acquired MBP-1 tape:

```bash
python implementation/tools/derive_mbp1_views.py --data-root /workspace/data --output-root /workspace/implementation/reports/phase1-live/derived-views --start 2020-01-02T14:30:00Z --end 2020-01-02T14:35:00Z --views trades bbo ohlcv-1s ohlcv-1m
```

The command clips the canonical monthly/weekly ownership manifest, reads only intersecting Parquet row groups, and creates a separate immutable JSONL bundle with hashes and raw row references. Outputs inside the acquired data root are rejected. Only `T` events contribute executed volume; identical genuine events are preserved. Each bar belongs to one native contract. Missing exchange sequence leaves differing open/close prices at equal timestamps unresolved. Empty time buckets are omitted, and observed values do not by themselves certify complete market coverage.

Derived bars use the stored exchange event timestamp. Databento's native OHLCV convention uses receive time, which the acquired NQ MBP-1 projection does not retain. Consequently these event-time bars are explicitly labeled and may differ from native vendor bars at interval boundaries. See the [provider's OHLCV schema](https://databento.com/docs/schemas-and-data-formats). No receive timestamp, deeper book, order identity or source-specific range-bar setting is reconstructed from absent fields.

`implementation/tools/audit_acquired_windows.py` records observed bounds, physical partition gaps and comparisons between existing resolutions. Its missing-minute manifest retains exact UTC nanosecond keys and native instrument IDs. The recovery command also accepts a JSON array of `{t, instrument_id}` keys with `t` in UTC milliseconds. Recover audited gaps from existing native one-second bars with:

```bash
python implementation/tools/recover_nq_minutes.py --data-root /workspace/data --output-root /workspace/implementation/reports/phase1-live/derived-views --gap-manifest /workspace/implementation/reports/phase1-live/coverage-audit/missing-one-minute-keys.json
```

Recovery preserves the native bar timestamp convention. Existing native minute keys take priority, and only absent `(minute, instrument_id)` pairs enter the fallback output. The manifest records recovered and unresolved counts, input file signatures and the derived artifact hash. Missing seconds are not turned into zero-volume observations. Keep the derived fallback separate from the acquired source archive.

## Separately scoped empirical extension

`implementation/tools/run_phase1_empirical.py` implements `calibrate`, `freeze`,
`validate`, `run` and `report` for the source-calibration/discovery handoff.
Commands and evidence live in
`implementation/reports/phase1-live/empirical/COMMANDS.md`. The versioned
comparison registry, coverage-selected split, causal opportunity/replay
records and empirical acceptance are separate from the original source
method acceptance. `research_comparison` candidates remain non-faithful and
cannot manufacture private source selections, orders or fills.
