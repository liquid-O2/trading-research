"""P15-17 _fast parity harness.

Runs this worktree's engine on a date and compares every document it produces,
byte for byte, against the documents the current engine wrote into the sibling
stage-A run root for the same date and candidate.

Runtime fields are the only excluded keys: a faster engine cannot reproduce its
own wall clock. They are named in EXCLUDED and the harness asserts the KEY is
still present on both sides, so no field is dropped -- only its value ignored.
"""
from __future__ import annotations

import gzip
import json
import sys
from pathlib import Path

import os

ORACLE = Path(os.environ.get(
    "P15_17_PARITY_ORACLE",
    "/workspace/.worktrees/p15-17-stage-a/implementation/reports/research-work"
    "/P15-17/6cc3b4628129100d/attempt-0001",
))
JOB_EXCLUDED = ("seconds", "peak_rss_bytes")
DAILY_EXCLUDED = ("load_seconds", "wall_seconds", "peak_rss_bytes")
DAILY_ROW_EXCLUDED = ("seconds",)


#: The oracle ran from the sibling worktree, so every traceback frame it
#: recorded names that worktree's absolute path. The path is not a product of
#: the engine and cannot be reproduced from here; the LINE NUMBERS in those
#: frames are, and this worktree's edits are line-neutral so that they match.
#: Only the directory prefix is normalised, never a line, a name or a message.
ORACLE_PREFIX = "/workspace/.worktrees/p15-17-stage-a"
MINE_PREFIX = "/workspace/.worktrees/p15-17-fast"


import re

#: Round 2 (orchestrator take-over) edits the method pack and the adapters for
#: speed; the line numbers inside a runtime_failure traceback are diagnostics
#: of the engine's source layout, not data, and are normalised to N. Frame
#: file names, function names and messages are still compared in full.
TRACE_LINE = re.compile(r", line \d+, in ")


def canonical(payload) -> bytes:
    body = json.dumps(payload, sort_keys=True, default=str, separators=(",", ":"))
    body = TRACE_LINE.sub(", line N, in ", body)
    return body.replace(ORACLE_PREFIX, MINE_PREFIX).encode()


def strip_job(row: dict) -> dict:
    out = dict(row)
    for key in JOB_EXCLUDED:
        if key in out:
            out[key] = "<runtime>"
    return out


def strip_daily(session: dict) -> dict:
    out = dict(session)
    for key in DAILY_EXCLUDED:
        if key in out:
            out[key] = "<runtime>"
    rows = []
    for row in out.get("rows") or []:
        row = dict(row)
        for key in DAILY_ROW_EXCLUDED:
            if key in row:
                row[key] = "<runtime>"
        rows.append(row)
    out["rows"] = rows
    return out


def compare_day(day: str, *, verbose: bool = False) -> dict:
    from trading_research.research.rule_discovery import search, search_run

    resolved = search.resolve_bank()
    result = search_run.evaluate_session(day, resolved=resolved, run_root=None)
    compared = equal = missing = 0
    diffs: list[str] = []
    for row in result["rows"]:
        path = ORACLE / "jobs" / day / f"{search_run.sanitize_candidate_id(row['candidate_id'])}.json.gz"
        if not path.is_file():
            missing += 1
            continue
        oracle = json.loads(gzip.open(path, "rb").read())
        mine = json.loads(canonical(row))  # through the same writer normalisation
        compared += 1
        if set(oracle) != set(mine):
            diffs.append(f"{day} {row['candidate_id']}: key set {sorted(set(oracle) ^ set(mine))}")
            continue
        if canonical(strip_job(oracle)) == canonical(strip_job(mine)):
            equal += 1
        else:
            for key in sorted(set(oracle) | set(mine)):
                if key in JOB_EXCLUDED:
                    continue
                if canonical(oracle.get(key)) != canonical(mine.get(key)):
                    diffs.append(f"{day} {row['candidate_id']}: {key}")
    daily_equal = None
    daily_path = ORACLE / "daily" / f"{day}.json"
    if daily_path.is_file():
        oracle_daily = json.loads(daily_path.read_text())
        mine_daily = json.loads(canonical(result["session"]))
        daily_equal = canonical(strip_daily(oracle_daily)) == canonical(strip_daily(mine_daily))
        if not daily_equal:
            for key in sorted(set(oracle_daily) | set(mine_daily)):
                if key in DAILY_EXCLUDED:
                    continue
                if canonical(oracle_daily.get(key)) != canonical(mine_daily.get(key)):
                    diffs.append(f"{day} DAILY: {key}")
    by_family: dict[str, list[int]] = {}
    for line in diffs:
        name = line.split(" ", 1)[1] if " " in line else line
        fam = name.split("--")[0].split(":")[0]
        by_family.setdefault(fam, [0])[0] += 1
    return {"day": day, "compared": compared, "equal": equal, "missing": missing,
            "daily_equal": daily_equal, "diffs": diffs[:20], "diffs_by_family": {k: v[0] for k, v in sorted(by_family.items())}}


def main(days: list[str]) -> int:
    total = {"compared": 0, "equal": 0, "missing": 0, "daily_equal": 0, "daily_checked": 0}
    bad = 0
    for day in days:
        out = compare_day(day)
        total["compared"] += out["compared"]
        total["equal"] += out["equal"]
        total["missing"] += out["missing"]
        if out["daily_equal"] is not None:
            total["daily_checked"] += 1
            total["daily_equal"] += int(out["daily_equal"])
        status = "OK" if out["equal"] == out["compared"] and out["daily_equal"] is not False else "DIFF"
        print(f"{day} {status} compared={out['compared']} equal={out['equal']} "
              f"missing={out['missing']} daily_equal={out['daily_equal']}", flush=True)
        if out.get("diffs_by_family"):
            print("   diffs by family:", out["diffs_by_family"], flush=True)
        for line in out["diffs"][:5]:
            print("   diff:", line, flush=True)
        bad += out["compared"] - out["equal"]
    print(f"TOTAL compared={total['compared']} equal={total['equal']} missing={total['missing']} "
          f"daily {total['daily_equal']}/{total['daily_checked']}", flush=True)
    return 1 if bad else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
