#!/usr/bin/env python3
"""Recorded 60-date B0 parity replay used by the P15-02 hardening attempt."""
from pathlib import Path
from trading_research.research.rule_discovery.runner import freeze, slice_run, stratified_parity_dates

ROOT = Path("/tmp/p15-02-parity-order-fix")
ROOT.mkdir(parents=True, exist_ok=True)
freeze(run_root=ROOT)
result = slice_run(
    run_root=ROOT,
    manifest=ROOT / "FROZEN_MANIFEST.json",
    dates=stratified_parity_dates(),
    task_id="P15-02",
    workers=6,
    write_jobs=False,
)
print(result["jobs"], result["matches"], len(result.get("mismatches") or []))
