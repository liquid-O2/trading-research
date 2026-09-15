# Merge notes (track sires)

Shared files were not edited. Tests pass without a coordinator patch.

## Suggested integration diffs (not applied)

`run_adapter_populations.py` still has no `--baseline B0.2` flag and does not dispatch SIRES or REFILL-STUDY. The integration step should add a B0.2 scanner lookup:

```diff
--- a/implementation/src/trading_research/research/rule_discovery/run_adapter_populations.py
+++ b/implementation/src/trading_research/research/rule_discovery/run_adapter_populations.py
@@
-        parser.add_argument(...)
+        parser.add_argument("--baseline", default="B0.1", choices=("B0", "B0.1", "B0.2"))
```

and call `source_adapters.sires.scan_b02` / `source_adapters.processes.scan_b02` when `--baseline B0.2` and the family is SIRES or REFILL-STUDY.

`source_adapters/common.py` `scan_family_date` / `dual_scan` should grow a third slot only in the integration merge, so B0 and B0.1 documents stay byte-identical:

```diff
--- a/implementation/src/trading_research/research/rule_discovery/source_adapters/common.py
+++ b/implementation/src/trading_research/research/rule_discovery/source_adapters/common.py
@@
 def dual_scan(...):
     ...
+    # Do not call scan_b02 here. B0.2 is a separate adapter function.
```

`tools/replay_author_examples.py` does not exist in this tree. The integration step should add it and call `replay_example(market, example)` per family.

## Local workarounds

- `scan_b02` and `replay_example` live on the family adapters and in `sires_b02.py` / `refill_b02.py`.
- Family JSON `baselines.B0.2` is registered without B0 / B0.1 keys.
- JETBUNDLE-STATES and STOIC scans are unchanged. `processes.scan_b02` raises `ContractError` for those families.
