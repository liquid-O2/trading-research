#!/usr/bin/env python3
"""Build auditable continuous-futures roll maps from raw definitions and bars."""

from __future__ import annotations

import argparse
import json
import os
from datetime import UTC, datetime
from pathlib import Path

import polars as pl


ROOT = Path(__file__).resolve().parent
DATA_ROOT = ROOT / "data" / "phase-1" / "glbx-mdp3"
OUTPUT_ROOT = ROOT / "data" / "derived" / "futures-rolls"
MANIFEST_ROOT = ROOT / "manifests"
ROOTS = {
    "NQ": "nq-c-0",
    "ES": "es-c-0",
    "YM": "ym-c-0",
    "RTY": "rty-c-0",
}


def atomic_parquet(frame: pl.DataFrame, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    partial = path.with_suffix(path.suffix + ".part")
    frame.write_parquet(partial, compression="zstd", statistics=True)
    os.replace(partial, path)


def atomic_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    partial = path.with_suffix(path.suffix + ".part")
    partial.write_text(text, encoding="utf-8")
    os.replace(partial, path)


def definition_map(files: list[Path]) -> pl.DataFrame:
    frame = (
        pl.scan_parquet([str(path) for path in files])
        .filter(pl.col("raw_symbol").is_not_null() & (pl.col("raw_symbol") != ""))
        .sort("t")
        .group_by("instrument_id", maintain_order=True)
        .agg(
            pl.col("raw_symbol").last(),
            pl.col("instrument_class").last(),
            pl.col("expiration").last(),
            pl.col("activation").last(),
            pl.col("underlying").last(),
            pl.col("min_price_increment").last(),
            pl.col("min_lot_size").last(),
            pl.col("contract_multiplier").last(),
            pl.col("currency").last(),
            pl.col("t").min().alias("first_definition_ns"),
            pl.col("t").max().alias("last_definition_ns"),
            pl.len().alias("definition_events"),
        )
        .collect()
    )
    return frame.with_columns(
        pl.from_epoch("expiration", time_unit="ns").dt.replace_time_zone("UTC").alias("expiration_ts_utc"),
        pl.from_epoch("activation", time_unit="ns").dt.replace_time_zone("UTC").alias("activation_ts_utc"),
        pl.from_epoch("first_definition_ns", time_unit="ns").dt.replace_time_zone("UTC").alias(
            "first_definition_ts_utc"
        ),
        pl.from_epoch("last_definition_ns", time_unit="ns").dt.replace_time_zone("UTC").alias(
            "last_definition_ts_utc"
        ),
    )


def bar_usage_and_transitions(files: list[Path]) -> tuple[pl.DataFrame, pl.DataFrame]:
    usage_parts: list[pl.DataFrame] = []
    transitions: list[dict] = []
    previous_instrument: int | None = None
    for path in sorted(files):
        bars = (
            pl.scan_parquet(path)
            .select("t", "instrument_id")
            .sort("t")
            .collect()
        )
        if bars.is_empty():
            continue
        usage_parts.append(
            bars.group_by("instrument_id").agg(
                pl.col("t").min().alias("first_bar_ms"),
                pl.col("t").max().alias("last_bar_ms"),
                pl.len().alias("bar_rows"),
            )
        )
        changed = bars.filter(
            pl.col("instrument_id")
            != pl.col("instrument_id").shift(1).fill_null(-1)
        )
        for item in changed.iter_rows(named=True):
            instrument_id = int(item["instrument_id"])
            if instrument_id == previous_instrument:
                continue
            transitions.append(
                {
                    "segment_start_ms": int(item["t"]),
                    "instrument_id": instrument_id,
                }
            )
            previous_instrument = instrument_id

    if not usage_parts or not transitions:
        raise RuntimeError("No bar rows found")
    usage = (
        pl.concat(usage_parts)
        .group_by("instrument_id")
        .agg(
            pl.col("first_bar_ms").min(),
            pl.col("last_bar_ms").max(),
            pl.col("bar_rows").sum(),
        )
        .with_columns(
            pl.from_epoch("first_bar_ms", time_unit="ms").dt.replace_time_zone("UTC").alias("first_bar_ts_utc"),
            pl.from_epoch("last_bar_ms", time_unit="ms").dt.replace_time_zone("UTC").alias("last_bar_ts_utc"),
        )
    )
    segments = pl.DataFrame(transitions).sort("segment_start_ms")
    segments = segments.with_columns(
        pl.col("segment_start_ms").shift(-1).alias("segment_end_exclusive_ms"),
        pl.from_epoch("segment_start_ms", time_unit="ms").dt.replace_time_zone("UTC").alias(
            "segment_start_ts_utc"
        ),
    ).with_columns(
        pl.from_epoch("segment_end_exclusive_ms", time_unit="ms").dt.replace_time_zone("UTC").alias(
            "segment_end_exclusive_ts_utc"
        )
    )
    return usage, segments


def build_root(root: str) -> dict:
    directory = DATA_ROOT / ROOTS[root]
    definition_files = sorted((directory / "definition").glob("*.parquet"))
    bar_files = sorted((directory / "ohlcv-1m").glob("*.parquet"))
    bar_years = {path.stem for path in bar_files}
    definition_years = {path.stem for path in definition_files}
    missing = sorted(bar_years - definition_years)
    if missing:
        raise RuntimeError(f"{root} definitions missing years: {', '.join(missing)}")
    if not definition_files or not bar_files:
        raise RuntimeError(f"{root} definition or bar files are absent")

    definitions = definition_map(definition_files)
    usage, segments = bar_usage_and_transitions(bar_files)
    instrument_map = (
        usage.join(definitions, on="instrument_id", how="left", validate="m:1")
        .with_columns(
            pl.lit(root).alias("root"),
            pl.lit(f"{root}.c.0").alias("continuous_symbol"),
        )
        .select(
            "root",
            "continuous_symbol",
            "instrument_id",
            "raw_symbol",
            "instrument_class",
            "underlying",
            "expiration",
            "expiration_ts_utc",
            "activation",
            "activation_ts_utc",
            "min_price_increment",
            "min_lot_size",
            "contract_multiplier",
            "currency",
            "first_bar_ms",
            "first_bar_ts_utc",
            "last_bar_ms",
            "last_bar_ts_utc",
            "bar_rows",
            "first_definition_ns",
            "first_definition_ts_utc",
            "last_definition_ns",
            "last_definition_ts_utc",
            "definition_events",
        )
        .sort("first_bar_ms")
    )
    unresolved = instrument_map.filter(pl.col("raw_symbol").is_null()).height
    if unresolved:
        raise RuntimeError(f"{root} has {unresolved} unmapped bar instrument IDs")

    roll_segments = (
        segments.join(
            instrument_map.select(
                "instrument_id", "raw_symbol", "expiration_ts_utc"
            ),
            on="instrument_id",
            how="left",
            validate="m:1",
        )
        .with_columns(
            pl.lit(root).alias("root"),
            pl.lit(f"{root}.c.0").alias("continuous_symbol"),
        )
        .select(
            "root",
            "continuous_symbol",
            "segment_start_ms",
            "segment_start_ts_utc",
            "segment_end_exclusive_ms",
            "segment_end_exclusive_ts_utc",
            "instrument_id",
            "raw_symbol",
            "expiration_ts_utc",
        )
        .sort("segment_start_ms")
    )
    atomic_parquet(instrument_map, OUTPUT_ROOT / f"{root.lower()}-instruments.parquet")
    atomic_parquet(roll_segments, OUTPUT_ROOT / f"{root.lower()}-rolls.parquet")
    return {
        "definition_files": len(definition_files),
        "bar_files": len(bar_files),
        "instruments": instrument_map.height,
        "roll_segments": roll_segments.height,
        "start": str(roll_segments["segment_start_ts_utc"].min()),
        "end": str(instrument_map["last_bar_ts_utc"].max()),
        "unresolved_instruments": unresolved,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", action="append", choices=tuple(ROOTS))
    args = parser.parse_args()
    selected = args.root or list(ROOTS)
    summary = {root: build_root(root) for root in selected}
    manifest = {
        "status": "complete",
        "generated_at": datetime.now(tz=UTC).isoformat(),
        "roots": summary,
    }
    atomic_text(
        MANIFEST_ROOT / "futures-roll-map.json",
        json.dumps(manifest, indent=2, sort_keys=True) + "\n",
    )
    print(json.dumps(manifest, sort_keys=True), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
