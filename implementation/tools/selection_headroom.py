"""The selection headroom of an executed list: what the list earns when every
trade is taken, when only the hindsight-best k trades a session are taken,
when only the winners are taken, and what the authors' own reproduced
tickets earned under our fills. Reads the per-entry records written by
run_exits_population.py (schema v2).

    oracle_bound.py --records rows.jsonl [--replay REPLAY_JJ_GB.json] --out report.md
"""
from __future__ import annotations

import argparse
import json
import statistics
from collections import defaultdict
from pathlib import Path

POLICIES = ("E0", "E5")


def load(path: Path):
    entries = defaultdict(list)  # (family, date) -> [record]
    sessions = defaultdict(set)  # family -> {date}
    with path.open() as handle:
        for line in handle:
            row = json.loads(line)
            if row.get("kind") == "entry":
                entries[(row["family"], row["date"])].append(row)
            elif row.get("kind") == "session":
                for policy, fams in (row.get("variants") or {}).items():
                    for family in fams:
                        sessions[family].add(row["date"])
    return entries, sessions


def net(record, policy):
    p = (record.get("policies") or {}).get(policy) or {}
    if not p.get("complete") or p.get("net_points") is None:
        return None
    return float(p["net_points"])


def year_of(date):
    return date[:4]


def summarize(entries, sessions, family, policy):
    per_session_all = {}
    per_session_topk = {1: {}, 2: {}, 3: {}}
    per_session_winners = {}
    per_branch = defaultdict(list)
    per_mode = defaultdict(list)
    n_trades = 0
    for date in sorted(sessions[family]):
        recs = entries.get((family, date), [])
        nets = [n for n in (net(r, policy) for r in recs) if n is not None]
        n_trades += len(nets)
        per_session_all[date] = sum(nets)
        ranked = sorted(nets, reverse=True)
        for k in per_session_topk:
            per_session_topk[k][date] = sum(ranked[:k])
        per_session_winners[date] = sum(n for n in nets if n > 0)
        for r in recs:
            n = net(r, policy)
            if n is None:
                continue
            per_branch[r.get("branch")].append(n)
            per_mode[r.get("mode")].append(n)
    n = len(per_session_all)
    mean = lambda d: sum(d.values()) / max(1, len(d))
    lines = [f"### {family}, policy {policy}: {n} sessions, {n_trades} trades ({n_trades / max(1, n):.1f} a session)", ""]
    lines.append("| list | points a session | median session | sessions positive |")
    lines.append("| --- | ---: | ---: | ---: |")
    for label, d in (("every executed trade", per_session_all), ("hindsight best 1 a session", per_session_topk[1]), ("hindsight best 2", per_session_topk[2]), ("hindsight best 3", per_session_topk[3]), ("winners only (a perfect filter)", per_session_winners)):
        vals = list(d.values())
        lines.append(f"| {label} | {mean(d):.1f} | {statistics.median(vals) if vals else 0:.1f} | {sum(1 for v in vals if v > 0) / max(1, len(vals)):.2f} |")
    lines.append("")
    lines.append("By year (points a session, every trade / best 1 / best 3):")
    lines.append("")
    lines.append("| year | sessions | every trade | best 1 | best 3 |")
    lines.append("| --- | ---: | ---: | ---: | ---: |")
    years = sorted({year_of(d) for d in per_session_all})
    for y in years:
        ds = [d for d in per_session_all if year_of(d) == y]
        lines.append(f"| {y} | {len(ds)} | {sum(per_session_all[d] for d in ds) / len(ds):.1f} | {sum(per_session_topk[1][d] for d in ds) / len(ds):.1f} | {sum(per_session_topk[3][d] for d in ds) / len(ds):.1f} |")
    lines.append("")
    lines.append("By branch (points a trade, count, share of trades positive):")
    lines.append("")
    lines.append("| branch | trades | mean | win share |")
    lines.append("| --- | ---: | ---: | ---: |")
    for branch, vals in sorted(per_branch.items(), key=lambda kv: -len(kv[1])):
        lines.append(f"| {branch} | {len(vals)} | {statistics.mean(vals):.2f} | {sum(1 for v in vals if v > 0) / len(vals):.2f} |")
    lines.append("")
    lines.append("By fill mode:")
    lines.append("")
    lines.append("| mode | trades | mean | win share |")
    lines.append("| --- | ---: | ---: | ---: |")
    for mode, vals in sorted(per_mode.items(), key=lambda kv: -len(kv[1])):
        lines.append(f"| {mode} | {len(vals)} | {statistics.mean(vals):.2f} | {sum(1 for v in vals if v > 0) / len(vals):.2f} |")
    lines.append("")
    return lines


def tickets(entries, replay_path: Path):
    """His reproduced tickets' outcomes under our fills: the replay's detected
    entries matched to the executed records by date, family and our entry
    time; a ticket whose reproduced entry was not executed (the one-position
    rule took another trade) is reported as such."""
    doc = json.loads(replay_path.read_text())
    lines = ["### The authors' reproduced tickets under our fills", "", "| ticket | family | printed | our entry | executed? | " + " | ".join(POLICIES) + " |", "| --- | --- | --- | --- | --- | " + " | ".join("---:" for _ in POLICIES) + " |"]
    totals = {p: [] for p in POLICIES}
    n_detected = n_executed = 0
    for example in doc.get("examples") or []:
        for entry in example.get("entries") or []:
            if not entry.get("detected"):
                continue
            n_detected += 1
            fam = entry.get("family")
            date = entry.get("session_date")
            at = entry.get("our_entry_ns")
            recs = entries.get((fam, date), [])
            match = None
            if at is not None:
                # the executed trade whose decision time is the reproduced fill's time (within two minutes)
                near = [r for r in recs if abs(int(r["decision_at"]) - int(at)) <= 120_000_000_000]
                if near:
                    match = min(near, key=lambda r: abs(int(r["decision_at"]) - int(at)))
            if match is None:
                lines.append(f"| {entry.get('example_id')} {entry.get('printed_time_et')} | {fam} | {entry.get('printed_side')} {entry.get('printed_price')} | {entry.get('our_entry')} | no (not on the executed list) | " + " | ".join("" for _ in POLICIES) + " |")
                continue
            n_executed += 1
            cells = []
            for p in POLICIES:
                v = net(match, p)
                cells.append("" if v is None else f"{v:.2f}")
                if v is not None:
                    totals[p].append(v)
            lines.append(f"| {entry.get('example_id')} {entry.get('printed_time_et')} | {fam} | {entry.get('printed_side')} {entry.get('printed_price')} | {match.get('entry')} ({match.get('mode')}) | yes | " + " | ".join(cells) + " |")
    lines.append("")
    lines.append(f"Detected tickets {n_detected}; on the executed list {n_executed}. Mean points a ticket: " + ", ".join(f"{p} {statistics.mean(v):.1f} over {len(v)}" for p, v in totals.items() if v) + ".")
    lines.append("")
    return lines


def main(argv=None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--records", type=Path, required=True)
    parser.add_argument("--replay", type=Path, default=None)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args(argv)
    entries, sessions = load(args.records)
    lines = ["# Selection headroom of the executed lists", "", f"Records: `{args.records}`", ""]
    for family in sorted(sessions):
        for policy in POLICIES:
            lines += summarize(entries, sessions, family, policy)
    if args.replay:
        lines += tickets(entries, args.replay)
    args.out.write_text("\n".join(lines) + "\n")
    print(f"wrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
