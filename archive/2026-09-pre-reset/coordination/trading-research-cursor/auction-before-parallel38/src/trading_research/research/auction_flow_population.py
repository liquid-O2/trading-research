"""Materialize the registered source population without another raw-data scan."""
from __future__ import annotations

import time
from pathlib import Path

from trading_research.errors import IntegrityError
from trading_research.research.auction_flow_storage import read_json_artifact


KIND = "auction_flow_observation_population_v1"


def receipt_key(receipt):
    unit = receipt["unit"]
    return (unit["root"], unit["source_path"], unit["event_start_ns"], unit["event_end_ns"])


def validate_catalog(catalog, *, expected_windows):
    refs = catalog.get("receipts")
    if (not isinstance(refs, list) or len(refs) != expected_windows
            or catalog.get("receipt_count") != expected_windows):
        raise IntegrityError("complete source receipt population changed")
    identities = [(r.get("path"), r.get("sha256")) for r in refs]
    if len(set(identities)) != len(identities) or len({p for p, _ in identities}) != len(refs):
        raise IntegrityError("duplicate physical receipt in the population")
    return refs


def choose_receipts(all_refs, contract):
    if contract["phase"] == "full":
        return all_refs
    if contract["phase"] != "pilot":
        raise IntegrityError("unregistered observation-population phase")
    selected = contract["pilot_receipts"]
    canonical = {r["sha256"]: r for r in all_refs}
    if (not selected or len({r["sha256"] for r in selected}) != len(selected)
            or any(canonical.get(r["sha256"]) != r for r in selected)):
        raise IntegrityError("pilot receipts are not unique exact members of the accepted population")
    return selected


def projected_resources(inventory, measured_units):
    """Conservative measured envelope; no percentage from a partial raw scan."""
    if not measured_units or any(r["input_uncompressed_bytes"] <= 0 or r["cpu_seconds"] <= 0
                                 or r["observation_rows"] < 0 for r in measured_units):
        raise IntegrityError("resource projection requires complete measured units")
    observed = [r for r in measured_units if r["observation_rows"] > 0]
    if not observed:
        raise IntegrityError("resource projection needs at least one observed instrument window")
    per_byte = max(r["cpu_seconds"] / r["input_uncompressed_bytes"] for r in measured_units)
    per_row = max(r["cpu_seconds"] / r["observation_rows"] for r in observed)
    output_per_row = max(r["output_bytes"] / r["observation_rows"] for r in observed)
    total_bytes = sum(r["input_uncompressed_bytes"] for r in inventory)
    total_rows = sum(r["atomic_cells_upper"] for r in inventory)
    wall_per_byte = max(r.get("wall_seconds", r["cpu_seconds"]) / r["input_uncompressed_bytes"] for r in measured_units)
    wall_per_row = max(r.get("wall_seconds", r["cpu_seconds"]) / r["observation_rows"] for r in observed)
    return {"method": "maximum complete-unit CPU/time per input byte and per atomic cell, larger estimate, 1.5 margin",
            "units_measured": len(measured_units), "population_units": len(inventory),
            "population_uncompressed_input_bytes": total_bytes,
            "population_atomic_cells_upper": total_rows,
            "cpu_seconds_with_margin": 1.5 * max(per_byte * total_bytes, per_row * total_rows),
            "sequential_wall_seconds_with_margin": 1.5 * max(wall_per_byte * total_bytes, wall_per_row * total_rows),
            "output_bytes_with_margin": int(1.5 * output_per_row * total_rows) + 16 * 1024**2,
            "measured_maximum_unit_cpu_seconds": max(r["cpu_seconds"] for r in measured_units),
            "measured_maximum_unit_output_bytes": max(r["output_bytes"] for r in measured_units)}


def run_population(*, contract, outputs, load_reference):
    from trading_research.research.auction_flow_observation_tables import write_observation_unit

    if (contract.get("kind") != "auction_flow_observation_population_contract_v1"
            or contract.get("atomic_width_ns") != 60_000_000_000
            or contract.get("worker_count") != 1):
        raise IntegrityError("unsupported frozen observation population")
    entry = time.process_time()
    catalog = load_reference(contract["source_catalog"])
    all_refs = validate_catalog(catalog, expected_windows=contract["source_window_count"])
    selected = choose_receipts(all_refs, contract)
    inventory, seen, files = [], set(), set()
    for reference in all_refs:
        receipt = load_reference(reference)
        if (receipt.get("kind") != "auction_flow_source_window_receipt_v1"
                or receipt.get("success") is not True
                or receipt.get("status") not in ("measured", "unavailable_source_window")):
            raise IntegrityError("population contains an unsuccessful source window")
        key, unit = receipt_key(receipt), receipt["unit"]
        if key in seen:
            raise IntegrityError("population repeats one physical source window")
        seen.add(key)
        files.add((unit["root"], unit["source_path"]))
        m = receipt["artifacts"]["measurement"]
        inventory.append({"receipt": reference, "unit": receipt["unit_identity"],
                          "utc_date": unit["utc_date"],
                          "input_uncompressed_bytes": m.get("uncompressed_size_bytes", m["size_bytes"]),
                          "atomic_cells_upper": unit["atomic_cells_per_instrument"] * unit["raw_instruments_per_window_upper"],
                          "raw_rows": receipt["counts"]["raw_rows"],
                          "canonical_raw_values": receipt["source_manifest_identity"]["canonical_selected_raw_stream"]})
    if len(files) != contract["source_file_count"]:
        raise IntegrityError("population lost an accepted physical source file")
    inventory_cpu = time.process_time() - entry
    summaries = []
    for ordinal, reference in enumerate(selected):
        began, wall_began, before = time.process_time(), time.monotonic(), outputs.written
        receipt = load_reference(reference)
        measured = read_json_artifact(receipt["artifacts"]["measurement"])
        try:
            summary = write_observation_unit(receipt, measured,
                                             receipt_reference=reference, outputs=outputs)
        except BaseException as exc:
            raise IntegrityError(f"observation table failed for {receipt_key(receipt)!r}; "
                                 f"receipt={reference['sha256']}; {type(exc).__name__}: {exc}") from exc
        del measured
        summary = {**summary, "receipt": reference, "observation_rows": summary['atomic_rows'],
                   "input_uncompressed_bytes": receipt["artifacts"]["measurement"].get(
                       "uncompressed_size_bytes", receipt["artifacts"]["measurement"]["size_bytes"]),
                   "cpu_seconds": time.process_time() - began,
                   "wall_seconds": time.monotonic() - wall_began,
                   "output_bytes": outputs.written - before}
        summaries.append(summary)
        print(f"observation {ordinal + 1}/{len(selected)} {receipt_key(receipt)!r} "
              f"rows={summary['observation_rows']} cpu={summary['cpu_seconds']:.3f}", flush=True)
    projection = projected_resources(inventory, summaries)
    report = {"kind": KIND, "phase": contract["phase"], "passed": True,
              "source_catalog": contract["source_catalog"],
              "population_source_windows": len(all_refs), "population_source_files": len(files),
              "processed_source_windows": len(summaries),
              "observation_rows": sum(r["observation_rows"] for r in summaries),
              "all_population_materialized": len(summaries) == len(all_refs),
              "inventory_cpu_seconds": inventory_cpu, "resource_projection": projection,
              "units": summaries, "inventory": inventory,
              "raw_source_scans": 0, "complete_family_statistics": False,
              "all_family_validation_complete": False,
              "next_consumer": "source-aware statistical populations and causal window/outcome links"}
    reference = outputs.json("observation-population.json", report, kind=KIND)
    return {"passed": True, "reference": reference,
            "processed_source_windows": len(summaries),
            "observation_rows": report["observation_rows"],
            "all_population_materialized": report["all_population_materialized"],
            "resource_projection": projection, "cpu_seconds": time.process_time() - entry,
            "output_bytes": outputs.written, "complete_family_statistics": False}
