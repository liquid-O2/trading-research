# Green Bird track merge notes

Shared files were not edited. Integration should apply the following after the four family branches merge.

## Runner redirects

`implementation/src/trading_research/research/rule_discovery/run_adapter_populations.py` owns the full-history run. B0.2 scans now live on the adapters.

Redirect these `_SCANNERS` entries to the adapter functions. Do not keep a second copy of the sweep loop in the runner.

```diff
-    "gb_fail_0930": _scan_gb_fail_0930,
-    "overnight": _scan_overnight,
-    "golden_pocket": _scan_golden_pocket,
+    "gb_fail_0930": green_failure.scan_b02,
+    "overnight": green_failure.scan_b02,
+    "golden_pocket": green_vwap_scalp.scan_b02,
```

Functions that can be deleted from the runner once every caller uses `scan_b02`:

- `_scan_gb_fail_0930` (lines 499-516)
- `_scan_overnight` (lines 518-552)
- `_scan_golden_pocket` (lines 619-657)
- `_golden_episode` (lines 555-616)
- `_gb_fail_sweep` (the A1-A3 copy of the repaired GB-FAIL loop)

`scan_b02(market, rec)` expects `rec["family"]` and `rec["branch"]`. Overnight should pass `branch="prior_day_level"` or `branch="all"`. Golden pocket should pass `family="GB-SCALP"` and `branch="golden_pocket_continuation"`.

## common.py (optional, not required for this track)

`golden_pocket(low, high)` still returns `[L+0.50W, L+0.618W]` both ways. B0.2 uses `green_b02.pocket_in_leg_direction` (O052 / F06). Integration may later label `common.golden_pocket` as the down-leg-only helper. Do not change it in this merge if B0.1 byte-identity is the gate.

`CLOCK_ZONE_UNVERIFIED_FAMILIES` still includes GB-FAIL / GB-VWAP / GB-SCALP. F18 removes that flag for B0.2 documents only. Leave the frozen B0/B0.1 path untouched.

## Family JSON

`families/green_failure.json` and `families/green_vwap_scalp.json` add `baselines.B0.2` without altering existing keys.

## New module

`source_adapters/green_b02.py` is family-owned, not a shared kernel. Other tracks should not import it.
