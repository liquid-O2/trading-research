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
    fidelity_guard.py --out <dir> --placebo  # also replay the fake tickets

A reproduction count is evidence only beside its chance rate (2026-09-18: the
loose Jumbo count was 0.87 real against 0.51 for fake tickets). With
``--placebo`` the Jumbo and Green Bird replay also runs on fake tickets (every
real one moved 40 minutes either way on its own day, side and branch, priced
at the market, ``placebo_examples_jj_gb.py``) and the share of them found on
the candidate list within ten points is pinned beside the tickets: the guard
fails when a ticket is lost OR when that chance rate rises by more than
PLACEBO_SLACK, so a list cannot be widened into reproducing everything.

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
PLACEBO_SHIFTS = (40, -40)
PLACEBO_SLACK = 0.05


def run(cmd: list[str], env_src: str) -> None:
    proc = subprocess.run(cmd, cwd=str(WORKTREE / "implementation"), env={**dict(__import__("os").environ), "PYTHONPATH": env_src}, capture_output=True, text=True)
    if proc.returncode != 0:
        sys.stderr.write(proc.stdout[-3000:] + proc.stderr[-3000:])
        raise SystemExit(f"replay failed (exit {proc.returncode}): {' '.join(cmd)}\n--- stderr tail ---\n{(proc.stderr or '')[-3000:]}")


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


def collect_placebo(out: Path) -> dict[str, dict]:
    """Per family: fake tickets replayed, and how many sit on the candidate
    list (and on the executed list) within ten points on the right bar."""
    rates: dict[str, dict] = {}
    for shift in PLACEBO_SHIFTS:
        doc = json.loads((out / f"placebo/{shift}/REPLAY_JJ_GB.json").read_text())
        for example in doc["examples"]:
            if example.get("inside_tape") is False:
                continue
            body = rates.setdefault(example["family"], {"tickets": 0, "selected": 0, "executed": 0})
            for entry in example.get("entries") or []:
                body["tickets"] += 1
                body["selected"] += 1 if entry.get("selected_strict_10") else 0
                body["executed"] += 1 if entry.get("executed_strict_10") else 0
    for body in rates.values():
        body["selected_rate"] = round(body["selected"] / max(1, body["tickets"]), 3)
    return rates


def main(argv=None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--pin", action="store_true", help="write the pin from this run (after an accepted change)")
    parser.add_argument("--skip-run", action="store_true", help="compare the replays already in --out")
    parser.add_argument("--placebo", action="store_true", help="also replay the fake Jumbo and Green Bird tickets and check the chance rate")
    args = parser.parse_args(argv)
    out = args.out
    src = str(WORKTREE / "implementation/src")
    if not args.skip_run:
        run([PYTHON, str(HERE / "replay_jj_gb.py"), "--out", str(out / "jjgb")], src)
        run([PYTHON, str(HERE / "replay_sires.py"), "--out", str(out / "sires"), "--levels", "drawn"], src)
        run([PYTHON, str(HERE / "replay_member.py"), "--out", str(out / "member")], src)
        if args.placebo:
            for shift in PLACEBO_SHIFTS:
                fake = out / f"placebo/fake_{shift}.json"
                fake.parent.mkdir(parents=True, exist_ok=True)
                run([PYTHON, str(HERE / "placebo_examples_jj_gb.py"), "--shift", str(shift), "--out", str(fake)], src)
                run([PYTHON, str(HERE / "replay_jj_gb.py"), "--examples", str(fake), "--out", str(out / f"placebo/{shift}")], src)
    flags = collect(out)
    placebo = collect_placebo(out) if args.placebo else None
    if args.pin or not PIN.exists():
        if placebo is None:
            raise SystemExit("a pin is written with --placebo: a ticket count is pinned beside its chance rate")
        PIN.write_text(json.dumps({"pinned_from": str(out), "tickets": flags, "placebo": placebo}, indent=1, sort_keys=True) + "\n")
        print(json.dumps({"event": "pinned", "tickets": len(flags), "detected": sum(1 for f in flags.values() if f["detected"]), "selected": sum(1 for f in flags.values() if f["selected"]), "placebo": placebo}))
        return 0
    document = json.loads(PIN.read_text())
    pinned = document["tickets"]
    risen = []
    if placebo is not None:
        for family, was in (document.get("placebo") or {}).items():
            now = placebo.get(family)
            if now is None or now["selected_rate"] > was["selected_rate"] + PLACEBO_SLACK:
                risen.append(f"{family}: fake tickets on the candidate list {None if now is None else now['selected_rate']} against the pinned {was['selected_rate']}")
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
    verdict = "fail" if lost or missing or risen else "pass"
    print(json.dumps({"event": "fidelity_guard", "verdict": verdict, "tickets": len(flags), "lost": lost, "missing": missing, "gained": gained, "new_tickets": new, "placebo": placebo, "placebo_risen": risen}, indent=1))
    return 1 if verdict == "fail" else 0


if __name__ == "__main__":
    raise SystemExit(main())
