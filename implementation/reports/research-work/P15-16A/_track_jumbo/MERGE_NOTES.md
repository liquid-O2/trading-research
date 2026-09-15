# Merge notes (JJ-TBR track)

This track did not edit coordinator-owned files. Proposed diffs for the integration merge follow.

## RR-02 (Astra J22): EQ both sides; quadrant sides case-selected

`changed_reference_scan` in `source_adapters/common.py` pins R-eq and R-q1 to long and R-q3 to short. The author trades EQ both ways (2026-09-01, 2026-09-02). TBR pp.12-15 permit quadrant entries in the extended and purged cases with the side chosen by context, not by the level.

B0.2 in `jumbo.py` enumerates EQ both ways and q1-long / q3-short locally. Candidate enumeration for P15-17 still uses `common.py`.

```diff
--- a/implementation/src/trading_research/research/rule_discovery/source_adapters/common.py
+++ b/implementation/src/trading_research/research/rule_discovery/source_adapters/common.py
@@ -1224,9 +1224,10 @@
     form_row = formation_record(formed)
     contacts: list[dict[str, Any]] = []
     episodes: list[dict[str, Any]] = []
-    side_by_kind = {"R-eq": "long", "R-q1": "long", "R-q3": "short"}
+    # RR-02: EQ is two-sided. Quadrant sides stay case-selected (q1 long / q3 short
+    # as the default pair); the family adapter binds the trade side from context.
+    side_by_kind = {"R-eq": None, "R-q1": "long", "R-q3": "short"}
     for reference in refs:
         kind = next((name for name in ("R-q1", "R-q3", "R-eq") if name in reference.reference_id), "R-eq")
-        side = side_by_kind.get(kind, "long")
+        sides = ("long", "short") if side_by_kind.get(kind) is None else (side_by_kind[kind],)
+        for side in sides:
             found = enumerate_bar_contacts(
                 market,
                 lower=reference.lower,
                 upper=reference.upper,
                 start_ns=issue_ns,
                 end_ns=expiry_ns,
                 reference_id=reference.reference_id + f":{side}",
                 side=side,
                 reference_lifecycle_id=reference.reference_lifecycle_id,
             )
```

Indent the `enumerate_bar_contacts` / episode loop under `for side in sides` when applying. Tests for `q1_contact_absent_from_eq` stay valid.

## F18: clock_zone_unverified for JJ-TBR

F18 removes the blanket `clock_zone_unverified` flag for JJ-TBR (ET is stated, TBR p.6). B0.2 documents set `clock_zone` to `America/New_York`. `CLOCK_ZONE_UNVERIFIED_FAMILIES` in `common.py` still includes `JJ-TBR` so frozen B0/B0.1 tagging is unchanged.

```diff
--- a/implementation/src/trading_research/research/rule_discovery/source_adapters/common.py
+++ b/implementation/src/trading_research/research/rule_discovery/source_adapters/common.py
@@ -61,7 +61,6 @@
 CLOCK_ZONE_UNVERIFIED_FAMILIES = frozenset(
     {
-        "JJ-TBR",
         "GB-FAIL",
```

Apply only if the coordinator wants B0.1 documents to drop the flag. This track leaves B0/B0.1 bytes frozen.
