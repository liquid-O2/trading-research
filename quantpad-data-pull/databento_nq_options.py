#!/usr/bin/env python3
"""Submit, monitor, download, and verify the authorized NQ option batch pull."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import time
from datetime import UTC, datetime
from pathlib import Path

import databento as db
from dotenv import load_dotenv


ROOT = Path(__file__).resolve().parent
MANIFEST_PATH = ROOT / "manifests" / "databento-nq-options-2020.json"
OUTPUT_ROOT = Path(
    os.environ.get(
        "DATABENTO_NQ_OUTPUT",
        str(ROOT / "data" / "databento" / "glbx-mdp3" / "nq-opt"),
    )
)

DATASET = "GLBX.MDP3"
SYMBOL = "NQ.OPT"
STYPE_IN = "parent"
START = "2020-01-01"
# Exclusive. This was the last complete historical boundary used for the
# user-authorized $32.70 estimate on 2026-09-03.
END = "2026-09-02"
SCHEMAS = ("definition", "statistics", "ohlcv-1m", "trades")
AUTHORIZED_COST_CAP_USD = 33.00


def now_iso() -> str:
    return datetime.now(tz=UTC).isoformat()


def load_manifest() -> dict:
    if not MANIFEST_PATH.exists():
        return {
            "dataset": DATASET,
            "symbol": SYMBOL,
            "stype_in": STYPE_IN,
            "start": START,
            "end": END,
            "encoding": "dbn",
            "compression": "zstd",
            "split_duration": "month",
            "authorized_cost_cap_usd": AUTHORIZED_COST_CAP_USD,
            "jobs": {},
            "created_at": now_iso(),
        }
    return json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))


def save_manifest(manifest: dict) -> None:
    MANIFEST_PATH.parent.mkdir(parents=True, exist_ok=True)
    temporary = MANIFEST_PATH.with_suffix(".json.tmp")
    temporary.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    os.replace(temporary, MANIFEST_PATH)


def client() -> db.Historical:
    load_dotenv(ROOT / ".env")
    if not os.environ.get("DATABENTO_API_KEY"):
        raise SystemExit(f"Missing DATABENTO_API_KEY in {ROOT / '.env'}")
    return db.Historical()


def estimate_costs(historical: db.Historical) -> dict[str, float]:
    return {
        schema: historical.metadata.get_cost(
            dataset=DATASET,
            symbols=[SYMBOL],
            schema=schema,
            start=START,
            end=END,
            stype_in=STYPE_IN,
        )
        for schema in SCHEMAS
    }


def submit() -> dict:
    historical = client()
    manifest = load_manifest()
    estimates = estimate_costs(historical)
    total = sum(estimates.values())
    if total > AUTHORIZED_COST_CAP_USD:
        raise RuntimeError(
            f"Current estimate ${total:.2f} exceeds authorized cap "
            f"${AUTHORIZED_COST_CAP_USD:.2f}; no jobs submitted"
        )
    manifest["cost_estimate_usd"] = estimates
    manifest["total_cost_estimate_usd"] = total
    save_manifest(manifest)

    for schema in SCHEMAS:
        if schema in manifest["jobs"]:
            print(f"{schema}: already submitted as {manifest['jobs'][schema]['id']}", flush=True)
            continue
        job = historical.batch.submit_job(
            dataset=DATASET,
            symbols=[SYMBOL],
            schema=schema,
            start=START,
            end=END,
            encoding="dbn",
            compression="zstd",
            map_symbols=False,
            split_symbols=False,
            split_duration="month",
            delivery="download",
            stype_in=STYPE_IN,
            # GLBX parent symbology resolves to instrument IDs. The definition
            # records retain raw_symbol for joining the other schemas later.
            stype_out="instrument_id",
        )
        manifest["jobs"][schema] = job
        manifest["jobs"][schema]["submitted_at_local"] = now_iso()
        save_manifest(manifest)
        print(f"{schema}: submitted as {job['id']}", flush=True)
    return manifest


def refresh_status(historical: db.Historical, manifest: dict) -> tuple[dict, bool]:
    all_done = True
    for schema, job in manifest["jobs"].items():
        details = historical.batch.get_job_details(job["id"])
        manifest["jobs"][schema]["latest_details"] = details
        state = details.get("state", "unknown")
        print(f"{schema}: {state}", flush=True)
        if state != "done":
            all_done = False
    manifest["status_checked_at"] = now_iso()
    save_manifest(manifest)
    return manifest, all_done


def wait_until_done(historical: db.Historical, manifest: dict, interval: int) -> dict:
    while True:
        manifest, all_done = refresh_status(historical, manifest)
        if all_done:
            return manifest
        time.sleep(interval)


def expected_file_size(file_info: dict) -> int | None:
    for key in ("size", "size_bytes", "bytes"):
        value = file_info.get(key)
        if value is not None:
            return int(value)
    return None


def file_matches(file_info: dict, path: Path) -> bool:
    if not path.is_file():
        return False
    expected_size = expected_file_size(file_info)
    if expected_size is not None and path.stat().st_size != expected_size:
        return False
    expected_hash = file_info.get("hash")
    if expected_hash and expected_hash.startswith("sha256:"):
        digest = hashlib.sha256()
        with path.open("rb") as handle:
            for chunk in iter(lambda: handle.read(8 * 1024 * 1024), b""):
                digest.update(chunk)
        return digest.hexdigest() == expected_hash.removeprefix("sha256:")
    return True


def download_and_verify(historical: db.Historical, manifest: dict) -> dict:
    OUTPUT_ROOT.mkdir(parents=True, exist_ok=True)
    for schema, job in manifest["jobs"].items():
        job_id = job["id"]
        schema_root = OUTPUT_ROOT / schema
        files = historical.batch.list_files(job_id)
        manifest["jobs"][schema]["files"] = files
        save_manifest(manifest)
        print(f"{schema}: {len(files)} server files", flush=True)

        for index, file_info in enumerate(files, start=1):
            filename = file_info["filename"]
            expected_size = expected_file_size(file_info)
            destination = schema_root / job_id / filename
            if file_matches(file_info, destination):
                print(f"{schema}: [{index}/{len(files)}] verified existing {filename}", flush=True)
                continue
            downloaded = historical.batch.download(
                job_id=job_id,
                output_dir=schema_root,
                filename_to_download=filename,
            )
            if destination not in downloaded and not destination.exists():
                raise RuntimeError(f"Download did not create {destination}")
            if expected_size is not None and destination.stat().st_size != expected_size:
                raise RuntimeError(
                    f"Size mismatch for {destination}: got {destination.stat().st_size}, "
                    f"expected {expected_size}"
                )
            if not file_matches(file_info, destination):
                raise RuntimeError(f"SHA-256 verification failed for {destination}")
            print(f"{schema}: [{index}/{len(files)}] downloaded {filename}", flush=True)

        local_files = [schema_root / job_id / item["filename"] for item in files]
        missing = [str(path) for path in local_files if not path.is_file()]
        if missing:
            raise RuntimeError(f"Missing downloaded files for {schema}: {missing[:3]}")
        manifest["jobs"][schema]["download_verified_at"] = now_iso()
        manifest["jobs"][schema]["downloaded_files"] = len(local_files)
        manifest["jobs"][schema]["downloaded_bytes"] = sum(
            path.stat().st_size for path in local_files
        )
        save_manifest(manifest)
    manifest["complete"] = True
    manifest["completed_at"] = now_iso()
    save_manifest(manifest)
    return manifest


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("cost", "submit", "status", "run"))
    parser.add_argument("--poll-seconds", type=int, default=30)
    args = parser.parse_args()

    historical = client()
    if args.command == "cost":
        estimates = estimate_costs(historical)
        print(json.dumps({"schemas": estimates, "total": sum(estimates.values())}, indent=2))
        return 0

    manifest = submit() if args.command in {"submit", "run"} else load_manifest()
    if not manifest["jobs"]:
        raise RuntimeError("No submitted jobs found")
    if args.command == "submit":
        return 0
    if args.command == "status":
        refresh_status(historical, manifest)
        return 0

    manifest = wait_until_done(historical, manifest, max(10, args.poll_seconds))
    download_and_verify(historical, manifest)
    print(f"Complete: {OUTPUT_ROOT}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
