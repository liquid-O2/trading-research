#!/usr/bin/env python3
"""Replay every dated Jumbo / Green Bird author example through the B0.3 scans.

Entries only (user instruction 2026-09-17): the acceptance question per dated
example is whether our scanner produces the author's proper entry, on his play,
on his side, within one five-minute bar of the printed time and within the
stated price tolerance. Stops and objectives are reported beside the entry and
never decide a match.

Writes, under the chosen run root:
  REPLAY_JJ_GB.json / .md   the replay table
  replay-charts/<id>.png    our reconstruction with the author's levels on it
  replay-charts/INDEX.md    each PNG against the author's source page
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import date, timedelta
from decimal import Decimal
from pathlib import Path

WORKTREE = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(WORKTREE / "implementation/src"))

from trading_research.research.method_pack import historical_runner as hr  # noqa: E402
from trading_research.research.method_pack.clocks import ns_to_et  # noqa: E402
from trading_research.research.method_pack.historical_features import HistoricalFeatures  # noqa: E402
from trading_research.research.rule_discovery.baseline import PHASE1_RUN  # noqa: E402
from trading_research.research.rule_discovery.native import install_write_guard  # noqa: E402
from trading_research.research.rule_discovery.run_baseline_repair import evaluation_dates  # noqa: E402
from trading_research.research.rule_discovery.source_adapters import green_b02 as gb  # noqa: E402
from trading_research.research.rule_discovery.source_adapters import jumbo as jj  # noqa: E402

EXAMPLES = WORKTREE / "planning/phase-1-5/AUTHOR_EXAMPLES_2026-09-17.json"


def _family(example) -> str:
    text = str(example.get("family") or "")
    return "JJ" if text.startswith("JJ") else "GB"


def _session_date(entry) -> date | None:
    """The session that contains a printed entry: 18:00 and later belong to the
    next session, the way the tape window is cut."""
    raw = entry.get("date")
    if not raw:
        return None
    day = date.fromisoformat(str(raw)[:10])
    token = str(entry.get("time_et") or "").split("-")[0].split("(")[0].strip()
    try:
        hour = int(token.split(":")[0])
    except (ValueError, IndexError):
        return day
    return day + timedelta(days=1) if hour >= 18 else day


class Markets:
    def __init__(self):
        install_write_guard()
        registry, _ = hr.load_registry(PHASE1_RUN, check_software=False)
        self.records = hr._records(registry)
        self.calendar = set(evaluation_dates(registry))
        self.cache: dict[str, object] = {}

    def get(self, day: str):
        if day not in self.cache:
            market = HistoricalFeatures(day, records=self.records)
            # The SessionStat envelope needs sixty prior windows; it only ever
            # decorates an operand, so it stays off for a scattered-date replay.
            market.jj_sessionstat = False
            self.cache[day] = market
        return self.cache[day]


def replay(markets: Markets, example) -> dict:
    family = _family(example)
    module = jj if family == "JJ" else gb
    entries = module.proper_entries(example)
    rows = []
    reads = {}
    for entry in entries:
        session = _session_date(entry)
        row = {
            "example_id": example.get("id"),
            "source": example.get("source"),
            "family": example.get("family"),
            "session_date": None if session is None else session.isoformat(),
            "printed_time_et": entry.get("time_et"),
            "printed_date": entry.get("date"),
            "printed_side": entry.get("side"),
            "printed_price": None if entry.get("price") is None else float(entry["price"]),
            "printed_reference": None if entry.get("reference_price") is None else float(entry["reference_price"]),
            "printed_stop": None if entry.get("stop") is None else float(entry["stop"]),
            "expected_branch": entry.get("branch"),
            "reference": entry.get("reference"),
            "marked_by": entry.get("marked_by"),
        }
        if session is None or session.isoformat() not in markets.calendar:
            row.update(
                {
                    "detected": None,
                    "detected_strict": None,
                    "divergence": "date outside the tape",
                    "expected_play": module.PLAY_OF_BRANCH.get(entry.get("branch")),
                }
            )
            rows.append(row)
            continue
        market = markets.get(session.isoformat())
        if family == "JJ":
            document = jj.scan_b02(market, {"branch": "all"})
            episodes = document.get("episodes") or []
            read = document.get("day_read") or {}
        else:
            episodes = []
            read = {}
            for item in ("GB-FAIL", "GB-VWAP", "GB-SCALP"):
                doc = gb.scan_b02(market, {"family": item, "branch": "all"})
                episodes.extend(doc.get("episodes") or [])
                read = read or (doc.get("day_read") or {})
        reads[session.isoformat()] = read
        match = module.match_entry(market, episodes, entry)
        row.update(match)
        row["day_read"] = read
        row["divergence"] = "" if match["detected"] else _why(match)
        rows.append(row)
    return {
        "example_id": example.get("id"),
        "source": example.get("source"),
        "family": example.get("family"),
        "date": example.get("date"),
        "inside_tape": example.get("inside_tape"),
        "n_proper_entries": len(entries),
        "entries": rows,
        "other_fills": module.other_fills(example),
        "day_reads": reads,
        "no_proper_entry_reason": example.get("no_proper_entry_reason"),
    }


def _why(match) -> str:
    if match.get("our_entry") is None:
        return "no passing episode on the author's play and side"
    if match.get("play_matches") is False:
        return f"play mismatch: ours {match.get('our_play')} vs {match.get('expected_play')}"
    bars = match.get("bars_from_printed")
    if bars is None or bars > 1.0:
        return f"entry {bars} five-minute bars from the printed time"
    delta = match.get("delta_points")
    return f"entry {delta} points from the printed fill (tolerance {match.get('tolerance_points')})"


# ---------------------------------------------------------------------------
# charts


def chart(markets: Markets, payload, out_dir: Path) -> list[str]:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.lines import Line2D

    written = []
    sessions = sorted({row["session_date"] for row in payload["entries"] if row.get("session_date")})
    sessions = [day for day in sessions if day in markets.calendar]
    if not sessions:
        return written
    family = _family({"family": payload["family"]})
    for index, day in enumerate(sessions):
        market = markets.get(day)
        rows = [row for row in payload["entries"] if row["session_date"] == day]
        start, end = _chart_window(market, family, rows)
        bars = [
            r
            for r in market.bars(start, end, 300)
            if r.get("O") is not None and r.get("C") is not None and r.get("H") is not None and r.get("L") is not None
        ]
        if not bars:
            continue
        fig, ax = plt.subplots(figsize=(16, 9))
        xs = list(range(len(bars)))
        for i, bar in enumerate(bars):
            up = bar["C"] >= bar["O"]
            colour = "#2a7f4f" if up else "#a83232"
            ax.plot([i, i], [float(bar["L"]), float(bar["H"])], color=colour, linewidth=0.8, zorder=2)
            ax.add_patch(
                plt.Rectangle(
                    (i - 0.35, float(min(bar["O"], bar["C"]))),
                    0.7,
                    max(float(abs(bar["C"] - bar["O"])), 0.25),
                    color=colour,
                    zorder=3,
                )
            )
        for level, label in _our_levels(market, family):
            ax.axhline(float(level), color="#3465a4", linewidth=0.9, alpha=0.75, zorder=1)
            ax.annotate(label, (len(bars) - 1, float(level)), color="#3465a4", fontsize=7, va="center", ha="left", xytext=(3, 0), textcoords="offset points")
        for label, value in _author_levels(payload).items():
            ax.axhline(float(value), color="#c77800", linewidth=1.2, linestyle="--", alpha=0.9, zorder=1)
            ax.annotate(f"author {label}", (0, float(value)), color="#c77800", fontsize=7, va="center", ha="left", xytext=(3, 0), textcoords="offset points")
        stamps = [int(b["start"]) for b in bars]
        for row in rows:
            if row.get("printed_price") is not None:
                x = _x_of(stamps, _printed_ns(market, row))
                ax.scatter([x], [row["printed_price"]], marker="v" if row["printed_side"] == "short" else "^", s=170, color="#c77800", zorder=6, edgecolor="black", linewidth=0.5)
                ax.annotate(f"author {row['printed_side']} {row['printed_price']} @{row['printed_time_et']}", (x, row["printed_price"]), color="#c77800", fontsize=8, xytext=(6, 10), textcoords="offset points")
            if row.get("our_entry") is not None and row.get("our_entry_ns"):
                x = _x_of(stamps, int(row["our_entry_ns"]))
                ax.scatter([x], [row["our_entry"]], marker="v" if row["printed_side"] == "short" else "^", s=170, color="#3465a4", zorder=6, edgecolor="black", linewidth=0.5)
                label = f"ours {row.get('our_branch')}/{row.get('our_mode') or ''} {row['our_entry']} @{ns_to_et(int(row['our_entry_ns'])).strftime('%H:%M')}"
                ax.annotate(label, (x, row["our_entry"]), color="#3465a4", fontsize=8, xytext=(6, -14), textcoords="offset points")
        ticks = [i for i in xs if i % max(1, len(bars) // 14) == 0]
        ax.set_xticks(ticks)
        ax.set_xticklabels([ns_to_et(bars[i]["start"]).strftime("%H:%M") for i in ticks], rotation=45, fontsize=8)
        detected = [row.get("detected") for row in rows]
        title = f"{payload['example_id']}  session {day}  {payload['source']}  detected={detected}"
        read = payload["day_reads"].get(day) or {}
        subtitle = f"day read: {read.get('classification') or read.get('day_model')}  primary play: {read.get('primary_play')}  plays: {read.get('plays')}"
        ax.set_title(title + "\n" + subtitle, fontsize=10)
        ax.grid(alpha=0.2)
        ax.legend(
            handles=[
                Line2D([0], [0], color="#3465a4", label="our levels / our entry"),
                Line2D([0], [0], color="#c77800", linestyle="--", label="author levels / printed fill"),
            ],
            loc="upper left",
            fontsize=8,
        )
        name = payload["example_id"] if len(sessions) == 1 else f"{payload['example_id']}-{day}"
        path = out_dir / f"{name}.png"
        fig.tight_layout()
        fig.savefig(path, dpi=110)
        plt.close(fig)
        written.append(path.name)
    return written


def _printed_ns(market, row) -> int:
    token = str(row.get("printed_time_et") or "").split("-")[0].split("(")[0].strip()
    parts = token.split(":")
    hour, minute = int(parts[0]), int(parts[1])
    day = date.fromisoformat(str(row.get("printed_date"))[:10])
    offset = (day - market.day).days
    if hour >= 18:
        offset -= 1
    return int(market.at(f"{hour:02d}:{minute:02d}", offset))


def _x_of(stamps, ns) -> float:
    for i, stamp in enumerate(stamps):
        if stamp > ns:
            return max(0, i - 1)
    return len(stamps) - 1


def _chart_window(market, family, rows) -> tuple[int, int]:
    stamps = [_printed_ns(market, row) for row in rows if row.get("printed_time_et")]
    if family == "JJ":
        lo, hi = int(market.at("02:00")), int(market.at("16:00"))
    else:
        lo, hi = int(market.at("18:00", -1)), int(market.at("16:00"))
    if stamps:
        lo = min(lo, min(stamps) - 2 * 3600 * 10**9)
        hi = max(min(hi, max(stamps) + 3 * 3600 * 10**9), min(stamps) + 3600 * 10**9)
    return max(lo, int(market.start)), min(hi, int(market.end))


def _our_levels(market, family) -> list[tuple[Decimal, str]]:
    out: list[tuple[Decimal, str]] = []
    if family == "JJ":
        context = jj.session_context(market)
        box = context.get("box")
        if box:
            for key in ("low", "q25", "eq", "q75", "high", "range_open"):
                out.append((box[key], f"6-9 {key}"))
            for name in ("plus_0.33", "plus_0.5", "plus_0.66", "plus_1", "plus_1.33", "plus_1.66", "minus_0.33", "minus_0.5", "minus_0.66", "minus_1", "minus_1.33", "minus_1.66"):
                out.append((box["ladder"][name], name))
        london = jj.box_geometry(market, "london")
        if london:
            for key in ("low", "eq", "high"):
                out.append((london[key], f"LON {key}"))
        for row in context.get("levels") or []:
            if row["kind"] not in {"box_low", "box_high"}:
                out.append((row["price"], row["kind"]))
    else:
        refs, _omit = gb.session_references(market)
        for ref in refs:
            out.append((ref["low"], f"{ref['kind']} low"))
            out.append((ref["high"], f"{ref['kind']} high"))
        for row in gb.objective_levels(market, refs):
            if row["label"] in {"tdo", "nwog_low", "nwog_high"}:
                out.append((row["price"], row["label"]))
    seen = set()
    unique = []
    for price, label in out:
        key = (round(float(price), 2), label)
        if key in seen:
            continue
        seen.add(key)
        unique.append((price, label))
    return unique


def _author_levels(payload) -> dict[str, float]:
    out = {}
    for row in payload["entries"]:
        if row.get("printed_stop") is not None:
            out[f"{row['printed_time_et']} stop"] = row["printed_stop"]
        if row.get("printed_reference") is not None:
            out[f"{row['printed_time_et']} level"] = row["printed_reference"]
    return out


# ---------------------------------------------------------------------------


def render_md(payload) -> str:
    lines = [
        "# Author-example replay, source-faithful rebuild (B0.3-2026-09-17)",
        "",
        "Entries only: an example is detected when every proper entry on it is reproduced on the",
        "author's play and side, within one five-minute bar of the printed time and within the",
        "stated price tolerance. `tol` is the ticket's own printed risk (|stop - entry|), or 27",
        "points (the median printed stop) where the ticket prints no stop; `strict` is +/-5 points.",
        "",
        f"- proper entries inside the tape: {payload['n_inside']}",
        f"- detected (ticket-risk tolerance): {payload['n_detected']}",
        f"- detected (strict +/-5 points): {payload['n_detected_strict']}",
        f"- detected within three five-minute bars of the printed time: {payload['n_detected_3bars']}",
        f"- outside the tape: {payload['n_outside']}",
        "",
        "| example | src | session | play (ours / author) | branch | side | printed | ours | d(pts) | bars | tol | det | strict | 3bar | note |",
        "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |",
    ]
    for item in payload["examples"]:
        for row in item["entries"]:
            printed = row.get("printed_price")
            if printed is None:
                printed = row.get("printed_reference")
            ours = row.get("our_entry")
            lines.append(
                "| `{id}` | {src} | {sess} | {op} / {ep} | {br} | {side} | {pt} @{tt} | {ov} @{ot} | {d} | {b} | {tol} | {det} | {st} | {b3} | {note} |".format(
                    id=item["example_id"],
                    src=item["source"],
                    sess=row.get("session_date"),
                    op=row.get("our_play"),
                    ep=row.get("expected_play"),
                    br=row.get("our_branch"),
                    side=row.get("printed_side"),
                    pt=printed,
                    tt=row.get("printed_time_et"),
                    ov=ours,
                    ot="" if not row.get("our_entry_ns") else ns_to_et(int(row["our_entry_ns"])).strftime("%H:%M"),
                    d=row.get("delta_points"),
                    b=row.get("bars_from_printed"),
                    tol=row.get("tolerance_points"),
                    det=row.get("detected"),
                    st=row.get("detected_strict"),
                    b3=row.get("detected_within_3_bars"),
                    note=row.get("divergence") or "",
                )
            )
    lines += ["", "## Examples with no proper entry to match", ""]
    for item in payload["examples"]:
        if item["n_proper_entries"] == 0:
            lines.append(f"- `{item['example_id']}` ({item['source']}): {item.get('no_proper_entry_reason')}")
    lines += ["", "## Other fills on the same charts (neither detections nor misses)", ""]
    for item in payload["examples"]:
        if item["other_fills"]:
            fills = "; ".join(f"{row['time_et']} {row.get('action')} {row.get('price')}" for row in item["other_fills"])
            lines.append(f"- `{item['example_id']}`: {fills}")
    lines.append("")
    return "\n".join(lines)


def main(argv=None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--examples", type=Path, default=EXAMPLES)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--charts", action="store_true")
    parser.add_argument("--only", default=None, help="comma-separated example ids")
    args = parser.parse_args(argv)

    document = json.loads(args.examples.read_text())
    wanted = set((args.only or "").split(",")) if args.only else None
    markets = Markets()
    out_dir = args.out
    out_dir.mkdir(parents=True, exist_ok=True)
    charts_dir = out_dir / "replay-charts"
    charts_dir.mkdir(parents=True, exist_ok=True)

    results = []
    chart_index = []
    for example in document.get("examples") or []:
        if not str(example.get("family") or "").startswith(("JJ", "GB")):
            continue
        if wanted and example.get("id") not in wanted:
            continue
        payload = replay(markets, example)
        results.append(payload)
        if args.charts:
            for name in chart(markets, payload, charts_dir):
                chart_index.append((name, example.get("source"), example.get("id")))
        print(json.dumps({"example": example.get("id"), "entries": payload["n_proper_entries"],
                          "detected": sum(1 for r in payload["entries"] if r.get("detected"))}), flush=True)

    inside = [row for item in results for row in item["entries"] if row.get("detected") is not None]
    outside = [row for item in results for row in item["entries"] if row.get("detected") is None]
    summary = {
        "schema": "author-example-replay-v2",
        "baseline_version": jj.B02_VERSION,
        "examples_path": str(args.examples),
        "n_examples": len(results),
        "n_inside": len(inside),
        "n_outside": len(outside),
        "n_detected": sum(1 for row in inside if row.get("detected")),
        "n_detected_strict": sum(1 for row in inside if row.get("detected_strict")),
        "n_detected_3bars": sum(1 for row in inside if row.get("detected_within_3_bars")),
        "examples": results,
    }
    (out_dir / "REPLAY_JJ_GB.json").write_text(json.dumps(summary, indent=2, default=str) + "\n")
    (out_dir / "REPLAY_JJ_GB.md").write_text(render_md(summary))
    if chart_index:
        lines = [
            "# Replay charts: our reconstruction beside the author's source page",
            "",
            "Blue: the levels our scanner computed for that session and our entry.",
            "Orange dashed: the levels and fills the author printed, from AUTHOR_EXAMPLES_2026-09-17.json.",
            "",
            "| chart | example | author source page |",
            "| --- | --- | --- |",
        ]
        for name, source, eid in chart_index:
            lines.append(f"| `{name}` | `{eid}` | {source} |")
        lines.append("")
        (charts_dir / "INDEX.md").write_text("\n".join(lines))
    print(json.dumps({"event": "replay_complete", "inside": len(inside), "detected": summary["n_detected"],
                      "strict": summary["n_detected_strict"], "out": str(out_dir)}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
