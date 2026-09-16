# MERGE_NOTES, saint repair track

This worktree owns SAINT-AMT, MEMBER-TWO-REASONS, KEANI-OPEN-ABOVE-VALUE. `common.py` and `confirmation.py` were not edited. B0 and B0.1 paths were not edited.

## Integrator must do

1. Re-run `tests/rule_discovery/test_p15_16a_plausibility_saint.py` after merge. It is the population gate.
2. Keani B0.2 jobs must not share `jobs/<date>/source_long.json.gz` with GB-VWAP. The full-history collision is still an integrator fix.
3. Author-example replay for SA-2026-08-10-ASIA must load account day 2026-08-11 (`account_day_for_example`). `saint.replay_example` reloads that day when the caller passes 2026-08-10.
4. Member ES-202609 stays `detected=None`, `divergence="ES tape required"`. NQ is the measured population.
5. Do not treat AMTL p.9 "80%" as a pass-rate target. It is a conditional traverse rate after return-into-range plus a held POC push.

## Shared-file edits

### `implementation/src/trading_research/research/rule_discovery/runner.py`

Reason: this cut imports `directory_listing_digest` from `contracts.identity`, which does not define it. The import is removed. The one call site inlines a directory digest with `file_digest` on children, the same shape as the jumbo track, so the merge is a one-line call-site change plus dropping the missing name.

```diff
 from trading_research.research.contracts.identity import (
     ...
     digest,
-    directory_listing_digest,
     file_digest,
     ...
 )

     for rel in code_paths:
         path = ROOT / rel
-        code_files[rel] = directory_listing_digest(path) if path.is_dir() else file_digest(path)
+        code_files[rel] = (
+            digest(sorted(str(child.relative_to(path)) + ":" + file_digest(child) for child in path.rglob("*") if child.is_file()))
+            if path.is_dir()
+            else file_digest(path)
+        )
```

### `common.py`, `confirmation.py`

No edits.

### `b02_saint_track.py`

Saint-track helper module (also imported by member.py and keani.py on this track). TRACK_DIR now resolves inside the worktree so tests do not write under `/workspace/implementation`. Additive helpers: `first_true_break`, `retest_held`, `contact_reaction`, `REPAIR_DIR`, `REPAIR_SLICE_DATES`.

## Owned adapter edits

- `source_adapters/saint.py`: true-break trigger, held-retest confirmation, F10 missing `confirm_at`, HTF window not inverted, distinct prior VA, POC push emitted when retest fails, Asia account-day reload.
- `source_adapters/member.py`: contact reaction at trigger; confirmation requires both reasons and the reaction.
- `source_adapters/keani.py`: strict `a_low > prior_vah`; prior RTH 70% VAH.
- `families/{saint,member,keani}.json`: `plausibility` blocks.
- `tests/rule_discovery/test_p15_16a_saint.py`: new fixtures.
- `tests/rule_discovery/test_p15_16a_plausibility_saint.py`: 15-date gate.
