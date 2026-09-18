"""What stop did the author's own tickets need? For every reproduced ticket
(the pinned replay's detected entries), from our reproduced entry: the largest
adverse excursion before his printed target (or, without one, our objective)
is reached, and whether it is reached before the session ends. The scanner's
own stop distance beside it shows which tickets the study's stop would have
taken out before his target.

    ticket_excursion.py --replay REPLAY_JJ_GB.json --records exits rows.jsonl --out report.md
"""
from __future__ import annotations

import argparse
import json
import statistics
from collections import defaultdict
from decimal import Decimal
from pathlib import Path

EXAMPLES = Path("/workspace/.worktrees/phase15/planning/phase-1-5/AUTHOR_EXAMPLES_2026-09-17.json")
TOOLS = Path("/workspace/.worktrees/phase15/implementation/tools")


def main(argv=None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--replay", type=Path, required=True)
    parser.add_argument("--records", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args(argv)
    import importlib.util
    import sys

    from trading_research.research.rule_discovery.source_adapters.common import load_source_market

    spec = importlib.util.spec_from_file_location("replay_sires", TOOLS / "replay_sires.py")
    rs = importlib.util.module_from_spec(spec)
    sys.modules["replay_sires"] = rs
    spec.loader.exec_module(rs)

    raw = json.loads(EXAMPLES.read_text())
    examples = {e["id"]: e for e in (raw["examples"] if isinstance(raw, dict) else raw)}
    records = defaultdict(list)
    with args.records.open() as handle:
        for line in handle:
            if '"kind": "entry"' in line:
                r = json.loads(line)
                records[(r["family"], r["date"])].append(r)
    doc = json.loads(args.replay.read_text())
    rows_out = []
    for example in doc["examples"]:
        for x in example["entries"]:
            if not x.get("detected") or x.get("our_entry_ns") is None or x.get("our_entry") is None:
                continue
            fam, day = x["family"], x["session_date"]
            side = x["printed_side"]
            sign = 1 if side == "long" else -1
            entry = Decimal(str(x["our_entry"]))
            at = int(x["our_entry_ns"])
            acts = [a for a in examples.get(x["example_id"], {}).get("actions", []) if a.get("price") is not None and x.get("printed_price") is not None and abs(float(a["price"]) - float(x["printed_price"])) < 0.01]
            his_target = next((Decimal(str(a["target"])) for a in acts if a.get("target") is not None), None)
            his_stop = next((Decimal(str(a["stop"])) for a in acts if a.get("stop") is not None), None)
            near = [r for r in records.get((fam, day), []) if abs(int(r["decision_at"]) - at) <= 120_000_000_000]
            ours = min(near, key=lambda r: abs(int(r["decision_at"]) - at)) if near else None
            our_stop = None if ours is None else Decimal(ours["stop"])
            our_target = None if ours is None or ours.get("target") is None else Decimal(ours["target"])
            target = his_target if his_target is not None else our_target
            market = load_source_market(day)
            end = int(market.at("16:00")) if at < int(market.at("16:00")) else int(market.end)
            bars = [b for b in rs.bars_between(market, at - 60_000_000_000, end) if int(b["end"]) > at]
            mae = Decimal(0)
            mfe = Decimal(0)
            reached = False
            minutes = None
            for b in bars:
                adverse = (entry - b["L"]) if sign == 1 else (b["H"] - entry)
                favour = (b["H"] - entry) if sign == 1 else (entry - b["L"])
                if target is not None and ((b["H"] >= target) if sign == 1 else (b["L"] <= target)):
                    # the bar that reaches the target: its adverse side counts only if it is a new extreme (conservative)
                    mae = max(mae, adverse)
                    reached = True
                    minutes = (int(b["end"]) - at) / 60e9
                    break
                mae = max(mae, adverse)
                mfe = max(mfe, favour)
            rows_out.append(
                {
                    "ticket": f"{x['example_id']} {x['printed_time_et']}",
                    "family": fam,
                    "side": side,
                    "entry": float(entry),
                    "his_target_pts": None if his_target is None else float(abs(his_target - entry)),
                    "his_stop_pts": None if his_stop is None else float(abs(entry - his_stop)),
                    "our_stop_pts": None if our_stop is None else float(abs(entry - our_stop)),
                    "our_target_pts": None if our_target is None else float(abs(our_target - entry)),
                    "target_used": "his" if his_target is not None else ("ours" if our_target is not None else None),
                    "reached": reached,
                    "minutes": None if minutes is None else round(minutes, 1),
                    "mae_pts": float(mae),
                    "mfe_pts": float(mfe),
                    "our_stop_survives": None if our_stop is None else bool(mae < abs(entry - our_stop)),
                }
            )
            print(json.dumps(rows_out[-1]), flush=True)
    lines = ["# What stop the authors' own tickets needed", "", "From our reproduced entry, the largest adverse excursion before the target (his printed one where the record carries it, else our objective) is reached, by 16:00.", ""]
    lines.append("| ticket | family | side | target used (pts) | reached | minutes | adverse excursion before it | our stop (pts) | our stop survives | his printed stop |")
    lines.append("| --- | --- | --- | ---: | --- | ---: | ---: | ---: | --- | ---: |")
    for r in rows_out:
        tp = r["his_target_pts"] if r["target_used"] == "his" else r["our_target_pts"]
        lines.append(f"| {r['ticket']} | {r['family']} | {r['side']} | {'' if tp is None else round(tp, 1)} ({r['target_used']}) | {'yes' if r['reached'] else 'no'} | {'' if r['minutes'] is None else r['minutes']} | {r['mae_pts']:.2f} | {'' if r['our_stop_pts'] is None else round(r['our_stop_pts'], 2)} | {'' if r['our_stop_survives'] is None else ('yes' if r['our_stop_survives'] else 'NO')} | {'' if r['his_stop_pts'] is None else r['his_stop_pts']} |")
    lines.append("")
    for fam in sorted({r["family"] for r in rows_out}):
        rs_ = [r for r in rows_out if r["family"] == fam]
        hit = [r for r in rs_ if r["reached"]]
        maes = sorted(r["mae_pts"] for r in hit)
        with_stop = [r for r in hit if r["our_stop_survives"] is not None]
        lines.append(f"**{fam}**: {len(rs_)} tickets, target reached on {len(hit)}. Adverse excursion before the target on those: median {statistics.median(maes) if maes else 0:.1f}, 75th percentile {maes[int(len(maes) * 0.75)] if maes else 0:.1f}, max {max(maes) if maes else 0:.1f} points. Our stop survives on {sum(1 for r in with_stop if r['our_stop_survives'])} of {len(with_stop)} of the tickets that reached the target and are on the executed list.")
        for buf in (5, 8, 12, 16, 20, 25, 30, 40, 50):
            lines.append(f"- a stop {buf} points from the entry keeps {sum(1 for r in hit if r['mae_pts'] < buf)} of {len(hit)}")
        lines.append("")
    args.out.write_text("\n".join(lines) + "\n")
    (args.out.with_suffix(".json")).write_text(json.dumps(rows_out, indent=1) + "\n")
    print(f"wrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
