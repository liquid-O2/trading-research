#!/usr/bin/env python3
"""Validate that every planned Phase 1 partition is a readable Parquet file."""

from __future__ import annotations

import json
from pathlib import Path

import pyarrow.parquet as pq

from pull_quantpad import DATA_ROOT, Puller, partition_ranges, selected_specs


def main() -> int:
    puller = Puller()
    summaries: list[dict] = []
    missing: list[str] = []

    for spec in selected_specs([1], None):
        start_ms, end_ms, _ = puller.bounds(spec)
        expected = list(partition_ranges(start_ms, end_ms, spec.partition))
        rows = 0
        size = 0
        complete = 0
        for _, _, label in expected:
            path = puller.destination(spec, label)
            if not puller.valid_parquet(path):
                missing.append(str(path))
                continue
            metadata = pq.ParquetFile(path).metadata
            rows += metadata.num_rows
            size += path.stat().st_size
            complete += 1
        summaries.append(
            {
                "id": spec.id,
                "expected": len(expected),
                "complete": complete,
                "rows": rows,
                "bytes": size,
            }
        )

    partials = sorted(
        str(path)
        for path in DATA_ROOT.rglob("*.part")
        if "_superseded" not in path.parts
    )
    report = {
        "phase": 1,
        "ok": not missing and not partials,
        "specs": summaries,
        "missing": missing,
        "partials": partials,
    }
    path = Path("manifests/phase-1-validation.json")
    path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
