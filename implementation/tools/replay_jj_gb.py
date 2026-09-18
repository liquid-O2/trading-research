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
                    "expected_play": module._expected_play(entry),
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

        # Item 11 (coordinator, 2026-09-17): matching ANY fill of ANY passing
        # episode proves little when a session raises hundreds of them. The
        # acceptance question is whether the trade list the family would
        # ACTUALLY have taken -- the day's primary play, the first qualifying
        # setup, at most three entries -- contains the author's entry. The same
        # tolerances apply; only the candidate set is narrowed.
        selected = _selection_for_session(module, market, episodes, read)
        row["selected_trades"] = selected["trades"]
        row["n_selected"] = len(selected["trades"])
        row["selected_primary_play"] = selected.get("primary_play")
        selected_match = module.match_entry(market, selected["episodes"], entry)
        row["selected_our_entry"] = selected_match.get("our_entry")
        row["selected_our_branch"] = selected_match.get("our_branch")
        row["selected_our_mode"] = selected_match.get("our_mode")
        row["selected_delta_points"] = selected_match.get("delta_points")
        row["selected_bars_from_printed"] = selected_match.get("bars_from_printed")
        row["selected_strict_10"] = strict_10(entry, selected_match)
        if entry.get("scored_by_decision"):
            row["decision_match"] = _decision_match(entry, selected_match)
            row["detected_strict_10"] = bool(row.get("detected_strict_10")) or row["decision_match"]
        row["selected_strict"] = selected_match.get("detected_strict")
        row["selected_detected"] = selected_match.get("detected")
        row["selected_within_3_bars"] = selected_match.get("detected_within_3_bars")
        # the EXECUTED list: one position at a time, with the family's adds and
        # flips -- reported beside the candidate list, never in its place
        executed_match = module.match_entry(market, selected.get("executed_episodes") or [], entry)
        row["executed_trades"] = selected.get("executed_trades") or []
        row["n_executed"] = len(selected.get("executed_trades") or [])
        row["n_round_trips"] = selected.get("n_round_trips")
        row["executed_our_entry"] = executed_match.get("our_entry")
        row["executed_our_mode"] = executed_match.get("our_mode")
        row["executed_delta_points"] = executed_match.get("delta_points")
        row["executed_bars_from_printed"] = executed_match.get("bars_from_printed")
        row["executed_strict_10"] = strict_10(entry, executed_match)

        # The same selected-list test with the day read's classifier taken out
        # of the question: the primary play is set to the play the AUTHOR
        # traded. The gap between this column and the one above is the
        # classifier's error; the gap between this column and a perfect score
        # is the selection rule's.
        author_play = module._expected_play(entry)
        row["author_play"] = author_play
        row["primary_play_matches_author"] = (selected.get("primary_play") == author_play)
        if author_play and author_play != selected.get("primary_play"):
            forced = _selection_for_session(module, market, episodes, {"primary_play": author_play})
            forced_match = module.match_entry(market, forced["episodes"], entry)
            row["selected_trades_if_play_known"] = forced["trades"]
            row["selected_strict_if_play_known"] = forced_match.get("detected_strict_10")
            row["selected_detected_if_play_known"] = forced_match.get("detected")
            row["selected_entry_if_play_known"] = forced_match.get("our_entry")
            row["selected_delta_if_play_known"] = forced_match.get("delta_points")
            row["selected_bars_if_play_known"] = forced_match.get("bars_from_printed")
        else:
            row["selected_trades_if_play_known"] = selected["trades"]
            row["selected_strict_if_play_known"] = selected_match.get("detected_strict_10")
            row["selected_detected_if_play_known"] = selected_match.get("detected")
            row["selected_entry_if_play_known"] = selected_match.get("our_entry")
            row["selected_delta_if_play_known"] = selected_match.get("delta_points")
            row["selected_bars_if_play_known"] = selected_match.get("bars_from_printed")
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



def _decision_match(entry, match) -> bool:
    """A ticket whose price is a level read off a narration, not a printed fill, is scored by its
    decision bar (one bar for an R:R-tool mark, three otherwise)."""
    bars = match.get("bars_from_printed")
    allowed = 1.0 if entry.get("marked_by") == "rr_tool" else 3.0
    return bool(match.get("our_entry") is not None and bars is not None and float(bars) <= allowed)


def strict_10(entry, match) -> bool:
    """The acceptance flag of a ticket against ANY list (candidate or traded): within ten points on
    the right bar, or, for a decision-scored ticket, the decision bar. Until 2026-09-18 the traded
    list was scored without the decision rule the candidate list had (2025-11-20: our 10:05 short at
    the 9-10 high, his 10:05 short at the 9-10 high, scored a miss)."""
    return bool(match.get("detected_strict_10")) or (bool(entry.get("scored_by_decision")) and _decision_match(entry, match))


def _selection_for_session(module, market, episodes, read) -> dict:
    """The session's selected trade list, and the episodes behind it.

    ``selection_for`` returns the taken trades; ``match_entry`` needs episodes,
    so the taken trades are mapped back to the episodes that produced them by
    (branch, side, decision time, entry).
    """
    primary = (read or {}).get("primary_play")
    try:
        selection = module.selection_for(market, [ep for ep in episodes if ep.get("research_verdict") == "pass"], primary_play=primary)
    except Exception as exc:  # a selection failure is reported, never swallowed
        return {"trades": [{"error": f"{type(exc).__name__}: {exc}"}], "episodes": []}
    taken = selection.get("entries") or []
    executed = (selection.get("executed") or {}).get("entries") or []
    trades, chosen = _trades_and_episodes(episodes, taken)
    executed_trades, executed_episodes = _trades_and_episodes(episodes, executed)
    return {
        "trades": trades,
        "episodes": chosen,
        "primary_play": primary,
        "executed_trades": executed_trades,
        "executed_episodes": executed_episodes,
        "n_round_trips": (selection.get("executed") or {}).get("n_round_trips"),
    }


def _trades_and_episodes(episodes, taken) -> tuple[list[dict], list[dict]]:
    """The taken trades, and every supported fill of the opportunities behind them.

    The selected TRADE is the opportunity (branch, side, line, cycle); the fill
    the selection layer prices it with is one of the source-supported
    executions of that opportunity (the stop through the line, the failure
    close, the orderblock confirmation...). The author's own execution varies
    between them from day to day, so the selected-fill test scores every
    supported fill of the selected opportunity, and the population is priced
    with the preferred one.
    """
    from trading_research.research.rule_discovery.source_adapters.trade_selection import _episode_key
    keys = {
        (str(row.get("branch")), str(row.get("side")), int(row.get("decision_at") or 0), str(row.get("entry")))
        for row in taken
    }
    # a taken trade stands for the coincident levels merged into it (its confluences) as well
    keys |= {
        (str(twin.get("branch")), str(row.get("side")), int(twin.get("decision_at") or 0), str(twin.get("entry")))
        for row in taken
        for twin in row.get("confluences") or []
    }
    chosen_fills = [
        ep
        for ep in episodes
        if (str(ep.get("branch")), str(ep.get("side")), int(ep.get("decision_at") or 0), str((ep.get("geometry") or {}).get("entry"))) in keys
    ]
    opportunity_keys = {_episode_key(ep) for ep in chosen_fills}
    chosen = [ep for ep in episodes if _episode_key(ep) in opportunity_keys]
    trades = [
        {
            "branch": row.get("branch"),
            "side": row.get("side"),
            "mode": row.get("confirmation_mode"),
            "at_et": ns_to_et(int(row["decision_at"])).strftime("%H:%M") if row.get("decision_at") else None,
            "entry": None if row.get("entry") is None else float(row["entry"]),
            "stop": None if row.get("stop") is None else float(row["stop"]),
            "outcome": row.get("outcome"),
            "flipped_at": ns_to_et(int(row["flipped_at"])).strftime("%H:%M") if row.get("flipped_at") else None,
        }
        for row in taken
    ]
    return trades, chosen


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


def chart(markets: Markets, payload, out_dir: Path, example=None) -> list[str]:
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
        low = min(float(b["L"]) for b in bars)
        high = max(float(b["H"]) for b in bars)
        pad = (high - low) * 0.08 or 10.0
        lo_lim, hi_lim = low - pad, high + pad
        for level, label in _our_levels(market, family):
            value = float(level)
            if not (lo_lim <= value <= hi_lim):
                continue
            ax.axhline(value, color="#3465a4", linewidth=0.9, alpha=0.7, zorder=1)
            ax.annotate(label, (len(bars) - 1, value), color="#3465a4", fontsize=7, va="center", ha="left", xytext=(3, 0), textcoords="offset points")
        for label, value in _author_levels(payload, example).items():
            value = float(value)
            if not (lo_lim <= value <= hi_lim):
                continue
            ax.axhline(value, color="#c77800", linewidth=1.3, linestyle="--", alpha=0.95, zorder=4)
            ax.annotate(f"author {label}", (0, value), color="#c77800", fontsize=7, va="center", ha="left", xytext=(3, 0), textcoords="offset points")
        ax.set_ylim(lo_lim, hi_lim)
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
        selected_strict = [row.get("selected_strict") for row in rows]
        title = f"{payload['example_id']}  session {day}  {payload['source']}  selected-strict={selected_strict}"
        read = payload["day_reads"].get(day) or {}
        subtitle = f"day read: {read.get('classification') or read.get('day_model')}  primary play: {read.get('primary_play')}"
        # Item 11: the chart carries the trade list the family would actually
        # have taken that session, so a reader can see what was traded rather
        # than only what some alternative fill reproduced.
        trades = []
        for row in rows:
            for trade in row.get("selected_trades") or []:
                token = f"{trade.get('at_et')} {trade.get('side')} {trade.get('branch')}/{trade.get('mode')} @{trade.get('entry')}"
                if token not in trades:
                    trades.append(token)
        third = "selected trades: " + ("; ".join(trades) if trades else "none")
        ax.set_title(title + "\n" + subtitle + "\n" + third, fontsize=9)
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


HOUR_NS = 3600 * 10**9


def _chart_window(market, family, rows) -> tuple[int, int]:
    """The author's own chart window: Jumbo 06:00-12:00 on a NY day and
    01:00-07:00 on a London day; Green Bird the overnight and the NY AM."""
    stamps = [_printed_ns(market, row) for row in rows if row.get("printed_time_et")]
    if not stamps:
        return (int(market.at("06:00")), int(market.at("13:00"))) if family == "JJ" else (
            int(market.at("18:00", -1)),
            int(market.at("16:00")),
        )
    lo = min(stamps) - 3 * HOUR_NS
    hi = max(stamps) + 3 * HOUR_NS
    if family == "JJ":
        lo = min(lo, int(market.at("06:00"))) if min(stamps) >= int(market.at("06:00")) else lo
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


def _author_levels(payload, example=None) -> dict[str, float]:
    """Every level the author drew on his own chart, plus the ticket's stop."""
    out: dict[str, float] = {}
    for key, raw in ((example or {}).get("levels") or {}).items():
        if isinstance(raw, (int, float)):
            out[key] = float(raw)
        elif isinstance(raw, (list, tuple)) and len(raw) == 2 and all(isinstance(v, (int, float)) for v in raw):
            out[f"{key}[0]"] = float(raw[0])
            out[f"{key}[1]"] = float(raw[1])
    for row in payload["entries"]:
        if row.get("printed_stop") is not None:
            out[f"{row['printed_time_et']} stop"] = row["printed_stop"]
        if row.get("printed_reference") is not None:
            out[f"{row['printed_time_et']} level"] = row["printed_reference"]
    return out


# ---------------------------------------------------------------------------


#: Why each remaining strict miss is a miss, and whether it is an input limit.
#: Keyed by (example id, printed time). Filled from the measurements in
#: REBUILD_JJ_GB_2026-09-17.md section 10.5; a miss with no entry here is
#: printed as "not yet explained", which is the state that must not persist.
MISS_NOTES: dict[tuple[str, str], tuple[str, str]] = {
    ("JJ-2025-10-13", "09:40"): ("5.25 points: 0.25 outside strict; the at-level fill is the swept low itself", "no"),
    ("JJ-2026-07-16", "09:35"): ("his printed opening spike tops at 29,485 where our tape prints 29,532; his 29,451.50 lies between our 09:33 and 09:34 closes and is not a level either chart draws", "yes"),
    ("JJ-2026-06-05-LONDON", "03:20"): ("his London box R-Lo 30,162 / R-Hi 30,222 is not a range of our tape; no window of 1-5 hours between 18:00 and 06:00 reproduces both edges within 5 points (best 01:05-02:05 ET: 30,163.00 / 30,228.25)", "yes"),
    ("JJ-2026-07-27", "09:35"): ("no episode; the reference in play is still unidentified (JR p.38)", "open question"),
    ("GB-2025-11-20", "10:05"): ("his 09:00-10:00 box high is 25,301.75; our tape's high over that hour is 25,292.00 and it does not trade 25,301.75 until 10:37", "yes"),
    ("GB-2026-04-23", "13:00"): ("the proper-entry action carries no price (his 27,116.25 sits on the following action of the same ticket), so the test is play + side + time; no previous_hour fill of ours falls in the one-bar window and the nearest is 17 bars away", "no -- the record omits the price on the proper-entry action"),
    ("GB-2026-04-28", "09:30"): ("the developing box low is a reference now, but our tape has no sweep of it at 09:30", "no"),
    ("GB-2026-07-13", "20:40"): ("in time and on the right fill; his PDL is 29,385 and ours 29,393.25, and the reclaim close differs by 6.5", "yes"),
    ("GB-2026-07-29-30", "22:20"): ("our near pocket line is 27,650.75; his own printed pocket lines are 27,652 and 27,718, so his fill is 7.5 points from his own nearest line -- a +/-5 match to any level-based rule is arithmetically impossible on this ticket", "yes"),
    ("GB-2026-07-29-30", "04:00 (07-30)"): ("the running London low is a traded reference and the fill is in time; ours is 27,351.25 at 03:55 where his is 27,360", "yes"),
    ("GB-2026-08-11-12", "20:40"): ("our previous-session 09:00-10:00 box low is 29,631.75 against his 29,635 -- inside strict -- but our tape last trades that level at 20:14, 26 minutes before his stamp", "yes"),
    ("GB-2026-08-13", "11:30"): ("CORRECTED 2026-09-17: this is NOT a tape limit. His 30,238 poke IS on our tape -- the 11:24 bar prints H 30,238.75 -- and our 10:00-11:00 box high is 30,267.50 (his tops[0] 30,258). His 30,227.50 is a lower-high rejection about 29 points UNDER the previous-hour high, not a sweep of it, so the miss is our mechanism, not the data", "no -- a mechanism miss (discretion)"),
    ("GB-2026-08-27", "11:30"): ("our 10:00-11:00 box high 29,623.50 matches his 29,620 and the one-minute failure close 29,618.50 is 4.75 from his fill, but it prints at 11:21, 1.8 bars early", "no"),
    ("GB-2026-08-27", "13:00"): ("price is now within 3.25 points on the author's branch; the fill prints 3.8 bars early against the one-bar allowance for a ticket time", "no -- a timing miss only"),
    ("GB-2026-08-28", "10:05"): ("after the running-reference fix our 09:00-10:00 box high is 29,703.25 (his 29,708.75) and the nyam_box fill is 29,687.25, 13.00 points out; the nearest fill of all is the True Day Open at 29,668.00 (6.25) on asia_tdo_case, which the framework rule cannot count against a nyam_box entry. Our 00:00 bar opens 29,668.00 against his drawn 29,674", "yes, and a record question: his reference line names the box high but his fill is at the TDO"),
    ("GB-2026-08-31", "09:33"): ("his reference is the 09:30 spike high 29,515; our 09:31 bar's high is 29,516.75 and the retest reaches only 29,515.00, so a limit at our level misses by 1.75 points and never fills", "yes"),
    ("GB-2026-09-01", "11:45"): ("CORRECTED 2026-09-17: his 29,253.75 DOES print on our tape, at 11:38 (low 29,253.50) -- seven minutes before his printed 11:45, where our tape is 29,286-29,295. Our PDL 29,273.50 matches his 29,270. The miss stands but the reason is a clock or feed inconsistency in the ticket, not an absent price", "yes -- but as a ticket clock inconsistency, not a missing price"),
    ("GB-2026-09-03", "00:45"): ("CORRECTED 2026-09-17: the loader reads data/quantpad/cme__nq-continuous-futures__mbp-1/2026-09.parquet (the MBP-1 tick file), not the 1-minute file that ends 2026-09-02 11:19, so the session is fully covered. Re-verified: the high over 00:38-00:52 is 29,229.00, 9.25 points under his 29,238.25 -- INSIDE the ten-point rule -- so this is a mechanism miss, not an input limit: no episode of ours is on the right branch and mode in that window", "no -- a mechanism miss"),
}


def family_of(example_id: str) -> str:
    return "JJ-TBR" if str(example_id).startswith("JJ") else "GB"


def by_family(payload) -> list[dict]:
    fields = ("n", "strict10", "strict", "risk", "b3", "sel_strict10", "sel_strict", "sel_risk", "sel_b3")
    rows = {}
    for item in payload["examples"]:
        if not item.get("inside_tape"):
            continue
        fam = family_of(item["example_id"])
        bucket = rows.setdefault(fam, {key: 0 for key in fields})
        for row in item["entries"]:
            bucket["n"] += 1
            bucket["strict10"] += 1 if row.get("detected_strict_10") else 0
            bucket["strict"] += 1 if row.get("detected_strict") else 0
            bucket["risk"] += 1 if row.get("detected") else 0
            bucket["b3"] += 1 if row.get("detected_within_3_bars") else 0
            bucket["sel_strict10"] += 1 if row.get("selected_strict_10") else 0
            bucket["exec_strict10"] = bucket.get("exec_strict10", 0) + (1 if row.get("executed_strict_10") else 0)
            bucket.setdefault("_cand", []).append(int(row.get("n_selected") or 0))
            bucket.setdefault("_exec", []).append(int(row.get("n_executed") or 0))
            bucket.setdefault("_rt", []).append(int(row.get("n_round_trips") or 0))
            bucket["sel_strict"] += 1 if row.get("selected_strict") else 0
            bucket["sel_risk"] += 1 if row.get("selected_detected") else 0
            bucket["sel_b3"] += 1 if row.get("selected_within_3_bars") else 0
    all_cand: list[int] = []
    all_exec: list[int] = []
    all_rt: list[int] = []
    for value in rows.values():
        for key, src, sink in (("cand_per_day", "_cand", all_cand), ("exec_per_day", "_exec", all_exec), ("rt_per_day", "_rt", all_rt)):
            items = value.pop(src, [])
            sink.extend(items)
            value[key] = None if not items else round(sum(items) / len(items), 1)
    out = [{"family": fam, **value} for fam, value in sorted(rows.items())]
    total = {"family": "both", **{key: 0 for key in fields}, "exec_strict10": 0}
    for value in out:
        for key in fields:
            total[key] += value[key]
        total["exec_strict10"] += int(value.get("exec_strict10") or 0)
    for key, items in (("cand_per_day", all_cand), ("exec_per_day", all_exec), ("rt_per_day", all_rt)):
        total[key] = None if not items else round(sum(items) / len(items), 1)
    out.append(total)
    return out


def render_md(payload) -> str:
    lines = [
        "# Author-example replay, source-faithful rebuild (B0.3-2026-09-17)",
        "",
        "Entries only: an example is detected when every proper entry on it is reproduced on the",
        "author's play and side, within one five-minute bar of the printed time and within the",
        "stated price tolerance. `tol` is the ticket's own printed risk (|stop - entry|), or 27",
        "points (the median printed stop) where the ticket prints no stop. `strict_10` is the owner's",
        "rule of 2026-09-17: within ten points of the printed price on the right bar AND on the",
        "author's framework -- same play, same branch, same side, and a fill mode the source or",
        "the tickets support. `+/-5` is the previous rule, kept so the change stays visible.",
        "",
        f"- proper entries inside the tape: {payload['n_inside']}",
        f"- detected (ticket-risk tolerance): {payload['n_detected']}",
        f"- **reproduced (strict_10: +/-10 points, right bar, the author's play, branch, side and a supported fill mode): {payload.get('n_detected_strict_10')}**",
        f"- reproduced under the old +/-5 rule: {payload['n_detected_strict']}",
        f"- detected within three five-minute bars of the printed time: {payload['n_detected_3bars']}",
        f"- **reproduced by the CANDIDATE list (strict_10): {payload.get('n_selected_strict_10')}** (every opportunity the framework admits, once; mean {payload.get('mean_candidates_per_day')} a day)",
        f"- reproduced by the EXECUTED list (one position at a time, adds and flips): {payload.get('n_executed_strict_10')} (mean {payload.get('mean_executed_per_day')} fills / {payload.get('mean_round_trips_per_day')} round trips a day)",
        f"- reproduced by the selected trade list (+/-5): {payload.get('n_selected_strict')}",
        f"- reproduced by the selected trade list (ticket-risk): {payload.get('n_selected_risk')}",
        f"- reproduced by the selected trade list (three bars): {payload.get('n_selected_3bars')}",
        f"- the day read named the author's play as PRIMARY on: {payload.get('n_primary_play_matches_author')}",
        f"- selected-list strict if the primary play is set to the author's: {payload.get('n_selected_strict_if_play_known')}",
        f"- outside the tape: {payload['n_outside']}",
        "",
        "## By family",
        "",
        "`any fill` scores every fill of every passing episode. `candidates` scores the",
        "CANDIDATE list: every opportunity the family's framework admits that session, once",
        "(per segment and play; at most two or three trades on one line; no position",
        "bookkeeping) -- the list the author chooses from. `executed` scores the one-position-",
        "at-a-time list with the family's adds and flips. The acceptance bar is the",
        "CANDIDATE column; the mean list sizes a day are printed beside it so the author's",
        "one to three trades a day can be compared with what the framework admits.",
        "",
        "| family | proper entries | candidates strict_10 | executed strict_10 | candidates +/-5 | candidates 3 bars | any-fill strict_10 | any-fill +/-5 | any-fill ticket-risk | mean candidates / day | mean executed fills / day | mean round trips / day |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for row in by_family(payload):
        lines.append(
            f"| {row['family']} | {row['n']} | **{row['sel_strict10']}** | {row.get('exec_strict10')} | {row['sel_strict']} | {row['sel_b3']} "
            f"| {row['strict10']} | {row['strict']} | {row['risk']} | {row.get('cand_per_day')} | {row.get('exec_per_day')} | {row.get('rt_per_day')} |"
        )
    lines += [
        "",
        "## Every entry",
        "",
        "| example | session | play (ours / author) | branch | side | printed | framework fill | d | bars | strict_10 | +/-5 | candidate fill | cand d | cand strict_10 | exec strict_10 | candidates / executed / round trips |",
        "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |",
    ]
    for item in payload["examples"]:
        for row in item["entries"]:
            printed = row.get("printed_price")
            if printed is None:
                printed = row.get("printed_reference")
            lines.append(
                "| `{id}` | {sess} | {op} / {ep} | {br} | {side} | {pt} @{tt} | {fv} | {fd} | {fb} | {s10} | {st} | {sv} | {sd} | {ss} | {es} | {counts} |".format(
                    es=row.get("executed_strict_10"),
                    counts=f"{row.get('n_selected')} / {row.get('n_executed')} / {row.get('n_round_trips')}",
                    id=item["example_id"],
                    sess=row.get("session_date"),
                    op=row.get("our_play"),
                    ep=row.get("expected_play"),
                    br=row.get("our_branch"),
                    side=row.get("printed_side"),
                    pt=printed,
                    tt=row.get("printed_time_et"),
                    fv=row.get("framework_entry"),
                    fd=row.get("framework_delta_points"),
                    fb=row.get("framework_bars"),
                    s10=row.get("detected_strict_10"),
                    st=row.get("detected_strict"),
                    sv=row.get("selected_our_entry"),
                    sd=row.get("selected_delta_points"),
                    ss=row.get("selected_strict_10"),
                )
            )
    lines += [
        "",
        "## Every remaining miss under strict_10, with its cause",
        "",
        "A miss is admissible only if it names the exact input that differs.",
        "",
        "| example | printed | ours | d(pts) | bars / allowed | cause | input limit? |",
        "| --- | --- | --- | ---: | --- | --- | --- |",
    ]
    for item in payload["examples"]:
        if not item.get("inside_tape"):
            continue
        for row in item["entries"]:
            if row.get("detected_strict_10"):
                continue
            key = (item["example_id"], str(row.get("printed_time_et")))
            cause, limit = MISS_NOTES.get(key, ("not yet explained", "**unexplained**"))
            lines.append(
                "| `{id}` {tt} | {pt} | {ov} | {d} | {b} / {ba} | {cause} | {limit} |".format(
                    id=item["example_id"],
                    tt=row.get("printed_time_et"),
                    pt=row.get("printed_price"),
                    ov=row.get("our_entry"),
                    d=row.get("delta_points"),
                    b=row.get("bars_from_printed"),
                    ba=row.get("bars_allowed"),
                    cause=cause,
                    limit=limit,
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
    parser.add_argument(
        "--render-only",
        action="store_true",
        help="re-render REPLAY_JJ_GB.md from the REPLAY_JJ_GB.json already in --out, without rescanning",
    )
    parser.add_argument("--overrides", default=None, help='JSON of module constants, e.g. {"green_b02.REENTER_SAME_LINE": false}: the ticket recall of a Phase 1.5 candidate')
    args = parser.parse_args(argv)
    if args.overrides:
        import importlib.util as _ilu

        spec = _ilu.spec_from_file_location("run_jj_gb_population", Path(__file__).resolve().parent / "run_jj_gb_population.py")
        runner = _ilu.module_from_spec(spec)
        spec.loader.exec_module(runner)
        runner.apply_overrides(json.loads(args.overrides))
    if args.render_only:
        out_dir = Path(args.out)
        payload = json.loads((out_dir / "REPLAY_JJ_GB.json").read_text())
        (out_dir / "REPLAY_JJ_GB.md").write_text(render_md(payload))
        print(json.dumps({"event": "render_only", "inside": payload["n_inside"],
                          "strict": payload["n_detected_strict"], "out": str(out_dir)}))
        return 0

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
            for name in chart(markets, payload, charts_dir, example):
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
        "n_detected_strict_10": sum(1 for row in inside if row.get("detected_strict_10")),
        "n_detected_strict": sum(1 for row in inside if row.get("detected_strict")),
        "n_detected_3bars": sum(1 for row in inside if row.get("detected_within_3_bars")),
        # Item 11: the same question asked of the SELECTED trade list only.
        "n_selected_strict_10": sum(1 for row in inside if row.get("selected_strict_10")),
        "n_executed_strict_10": sum(1 for row in inside if row.get("executed_strict_10")),
        "mean_candidates_per_day": None if not inside else round(sum(int(row.get("n_selected") or 0) for row in inside) / len(inside), 1),
        "mean_executed_per_day": None if not inside else round(sum(int(row.get("n_executed") or 0) for row in inside) / len(inside), 1),
        "mean_round_trips_per_day": None if not inside else round(sum(int(row.get("n_round_trips") or 0) for row in inside) / len(inside), 1),
        "n_selected_strict": sum(1 for row in inside if row.get("selected_strict")),
        "n_selected_3bars": sum(1 for row in inside if row.get("selected_within_3_bars")),
        "n_selected_risk": sum(1 for row in inside if row.get("selected_detected")),
        "n_selected_strict_if_play_known": sum(1 for row in inside if row.get("selected_strict_if_play_known")),
        "n_selected_risk_if_play_known": sum(1 for row in inside if row.get("selected_detected_if_play_known")),
        "n_primary_play_matches_author": sum(1 for row in inside if row.get("primary_play_matches_author")),
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
