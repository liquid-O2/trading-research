# Merge notes (JJ-TBR repair track)

This track owns `source_adapters/jumbo.py`, `families/jumbo.json`, `tests/rule_discovery/test_p15_16a_jumbo.py`, `tests/rule_discovery/test_p15_16a_plausibility_jumbo.py`, and `reports/research-work/P15-16A/_repair_jumbo/`.

`common.py` and `confirmation.py` were not edited.

## runner.py (shared, required to import tests)

The worktree cut imported `directory_listing_digest` from `contracts.identity`. That name does not exist. Green Bird's track uses the same one-line `file_digest` map as main. This track matches that hunk.

```diff
--- a/implementation/src/trading_research/research/rule_discovery/runner.py
+++ b/implementation/src/trading_research/research/rule_discovery/runner.py
@@ -16,7 +16,6 @@
 from trading_research.research.contracts.identity import (
     ...
-    directory_listing_digest,
     file_digest,
     ...
 )
@@ -575,8 +574,7 @@
     plan_files = {rel: file_digest(ROOT / rel) for rel in plan_paths}
-    code_files = {}
-    for rel in code_paths:
-        path = ROOT / rel
-        code_files[rel] = directory_listing_digest(path) if path.is_dir() else file_digest(path)
+    code_files = {rel: file_digest(ROOT / rel) for rel in code_paths}
```

Reason: contracts are frozen; this is the smallest import-fix. Prefer Green Bird's identical hunk on merge if both land.

## common.py RR-02

Not applied here. `changed_reference_scan` already has `"R-eq": None` and `for side in sides`. q1 stays long and q3 stays short in the candidate enumerator. B0.2 in `jumbo.py` enumerates both sides and binds side from context. Candidate enumeration for P15-17 still uses `common.py`. The first-round MERGE_NOTES patch for q1/q3 remains optional and is not required for this repair.

## confirmation.py

No edit. OB/RB stay in `jumbo.py` so the merge does not fight other families.

## Integration step must

1. Re-run `tests/rule_discovery/test_p15_16a_plausibility_jumbo.py` after the four-track merge.
2. Re-run `tests/rule_discovery/test_p15_16a_jumbo.py`.
3. Do not recompute B0/B0.1. Byte-identity on 2021-01-04 and 2025-01-02 is the frozen-row check.
4. Full-history B0.2 rerun is the orchestrator's job, not this track's.
5. Replay 16 inside-tape JJ examples through `replay_example` / `tools/replay_author_examples.py`. Detection verdict is the population scan on that date.

## Test output path

Round-1 `_track_jumbo/FUNNEL_JJ-TBR.json`, `REPLAY_JJ-TBR.json`, and `RULES_JJ-TBR.json` are restored to committed bytes. This round writes under `_repair_jumbo/` only.

## Cache

`replay_example` returns `detected=None`, `divergence='date outside the tape'` for dates outside 2020-01-02..2026-08-19 before it reads the market. Tests monkeypatch `event_cache.build_event_window` to raise.
