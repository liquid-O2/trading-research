#!/usr/bin/env python3
"""The fidelity regression guard.

Every family's dated tickets are the baseline: the entries the source-faithful
scanners reproduce within 10 points on the right bar, on the author's play and
side (fidelity-round8 REPORT). This tool re-runs the three replays (Jumbo and
Green Bird, Sires and Saint on the drawn levels, Member on the ES tape),
collects one flag per ticket, and compares them with the pinned baseline
``FIDELITY_PIN.json``. A ticket that was reproduced and no longer is fails
the guard; a ticket that is newly reproduced is reported as an improvement
and the pin is only rewritten with ``--pin``.

    fidelity_guard.py --out <dir>            # check against the pin
    fidelity_guard.py --out <dir> --pin      # re-pin after an accepted change

Any scanner change, in any family, runs this before it is merged: a change to
one strategy must not move another's tickets (owner instruction 2026-09-17).
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
WORKTREE = HERE.parents[1]
PIN = WORKTREE / "planning/phase-1-5/FIDELITY_PIN.json"
PYTHON = sys.executable


def run(cmd: list[str], env_src: str) -> None:
    proc = subprocess.run(cmd, cwd=str(WORKTREE / "implementation"), env={**dict(__import__("os").environ), "PYTHONPATH": env_src}, capture_output=True, text=True)
    if proc.returncode != 0:
        sys.stderr.write(proc.stdout[-3000:] + proc.stderr[-3000:])
        raise SystemExit(f"replay failed: {' '.join(cmd)}")


def collect(out: Path) -> dict[str, dict]:
    """One row per dated ticket: family, id, printed time, side, and the flag."""
    flags: dict[str, dict] = {}
    jjgb = json.loads((out / "jjgb/REPLAY_JJ_GB.json").read_text())
    for example in jjgb["examples"]:
        if example.get("inside_tape") is False:
            continue  # no tape, no ticket to pin
        for entry in example.get("entries") or []:
            key = f"{example['example_id']} {entry.get('printed_time_et')} @{entry.get('printed_price')}"
            flags[key] = {"family": example["family"], "marked_by": entry.get("marked_by"), "detected": bool(entry.get("detected_strict_10")), "selected": bool(entry.get("selected_strict_10")), "executed": bool(entry.get("executed_strict_10"))}
    sires = json.loads((out / "sires/REPLAY_SIRES.json").read_text())
    for row in sires.get("rows") or sires.get("table") or []:
        key = f"{row['example_id']} {row['time_et']}"
        flags[key] = {"family": "SIRES/SAINT", "detected": bool(row["strict_10"]), "selected": None, "executed": None}
    member = json.loads((out / "member/REPLAY_MEMBER.json").read_text())
    for row in member["rows"]:
        key = f"{row['example_id']} {row['time_et']}"
        flags[key] = {"family": "MEMBER", "detected": bool(row["strict_10"]), "selected": None, "executed": None}
    return flags


def main(argv=None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--pin", action="store_true", help="write the pin from this run (after an accepted change)")
    parser.add_argument("--skip-run", action="store_true", help="compare the replays already in --out")
    args = parser.parse_args(argv)
    out = args.out
    src = str(WORKTREE / "implementation/src")
    if not args.skip_run:
        run([PYTHON, str(HERE / "replay_jj_gb.py"), "--out", str(out / "jjgb")], src)
        run([PYTHON, str(HERE / "replay_sires.py"), "--out", str(out / "sires"), "--levels", "drawn"], src)
        run([PYTHON, str(HERE / "replay_member.py"), "--out", str(out / "member")], src)
    flags = collect(out)
    if args.pin or not PIN.exists():
        PIN.write_text(json.dumps({"pinned_from": str(out), "tickets": flags}, indent=1, sort_keys=True) + "\n")
        print(json.dumps({"event": "pinned", "tickets": len(flags), "detected": sum(1 for f in flags.values() if f["detected"])}))
        return 0
    pinned = json.loads(PIN.read_text())["tickets"]
    lost, gained, missing = [], [], []
    for key, was in pinned.items():
        now = flags.get(key)
        if now is None:
            missing.append(key)
            continue
        for field in ("detected", "selected", "executed"):
            if was.get(field) is True and now.get(field) is not True:
                lost.append(f"{key} [{field}]")
            if was.get(field) is False and now.get(field) is True:
                gained.append(f"{key} [{field}]")
    new = sorted(set(flags) - set(pinned))
    verdict = "fail" if lost or missing else "pass"
    print(json.dumps({"event": "fidelity_guard", "verdict": verdict, "tickets": len(flags), "lost": lost, "missing": missing, "gained": gained, "new_tickets": new}, indent=1))
    return 1 if verdict == "fail" else 0


if __name__ == "__main__":
    raise SystemExit(main())
