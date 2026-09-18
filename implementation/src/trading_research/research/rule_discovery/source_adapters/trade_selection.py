"""Per-session trade selection shared by the source-faithful Jumbo and Green Bird scans.

The branch scans enumerate every setup the author's rules admit on a session.
The authors do not trade every one of them: JJumboFX runs "one thesis per
session" with one to four round trips (fidelity audit 2026-09-17 §1.1
"Sizing and frequency"), and Green Bird states "One opportunity at a time",
"Two trades were enough" and shows one to three tickets a day (§2.1
"Frequency"). G11 of the audit makes the selection layer a requirement: any
strategy-level reading of the population needs "the first qualifying setup in
the author's clock, no re-entry after a full objective, at most three a day".

This module turns a branch population into that trade list. It is deliberately
separate from the scanners: the scanners answer "was the author's setup
present", this answers "would the author have been in it".
"""
from __future__ import annotations

from decimal import Decimal
from typing import Any, Iterable, Mapping, Sequence

MAX_ENTRIES_PER_SESSION = 3

#: Which fill of one opportunity the author actually took.
#:
#: The branch scans emit every fill the rules admit -- the limit at the level,
#: the close of the candle that failed it, the open of the bar after the
#: rejection candle -- as alternative fills of ONE opportunity. Selecting the
#: earliest of them always picks the most aggressive (the resting limit), which
#: on 2026-07-16 puts the EQ short on the 09:30 bar's dip, before the spike that
#: made the setup, and against the next 71 points of tape.
#:
#: The order below is read off the replay of the author's own tickets: for each
#: strict match among the 40 inside-tape proper entries, which mode reproduced
#: it. It is published as "Fill modes that reproduced the author's tickets" in
#: REBUILD_JJ_GB_2026-09-17.md. Modes not in a branch's list, and branches not
#: listed here, fall back to the earliest decision and are recorded as such --
#: no order is invented where the tickets are silent.

MODE_PREFERENCE: dict[str, tuple[str, ...]] = {
    # --- Jumbo, read off the author's tickets (coordinator rebuild 2026-09-17):
    # the resting limit at the line and the signature at the line lead the
    # Judas tickets (12-30, 02-24, 08-28, 09-01 at the line; 01-28, 10-03, 10-13
    # on the signature); the EQ tickets are the failure close (07-27 09:00 tag,
    # 07-16) and the two-minute reclaim (07-10); the London tickets are the
    # signature (10-06, 10-07, 05-23) and the limit at the box low (10-08); the
    # P-zone tickets are the limit inside the zone (01-09, 01-02).
    "judas_reversal": ("stop_at_line", "stop_at_next_line", "failure_close", "signature_close", "rejection_close", "two_minute_close", "next_bar_open"),
    "other_session": ("stop_at_line", "failure_close", "signature_close", "rejection_close", "two_minute_close", "next_bar_open"),
    "single_extended": ("stop_at_line", "failure_close", "two_minute_close", "next_bar_open", "signature_close", "rejection_close"),
    "single_purged": ("stop_at_line", "two_minute_close", "failure_close", "next_bar_open", "signature_close", "rejection_close"),
    "internal_rotation": ("two_minute_close", "stop_at_line", "failure_close", "next_bar_open", "signature_close", "rejection_close"),
    "timed_pzone_reversal": ("zone_limit", "rejection_close", "signature_close", "next_bar_open"),
    "judas_outbound": ("stop_at_line",),
    # --- Green Bird, read off the tickets (coordinator rebuild 2026-09-17):
    # the limit at the level on the retest (07-13, 09-03, 09-14, 11-20), the
    # five-minute close (04-23), the stop through the level (08-28 at the TDO),
    # the turn of the cash-open spike (08-31), the post-open retest (11-19),
    # the failed retest under the previous high (08-13, 04-23; FITTED).
    "nyam_box": ("at_level", "edge_test", "stop_at_level", "stop_at_next_level", "five_minute_close", "failure_close_1m", "approach_reject", "next_bar_open", "post_open_retest"),
    "previous_hour": ("approach_reject", "five_minute_close", "at_level", "stop_at_level", "failure_close_1m", "next_bar_open"),
    "prior_day_level": ("at_level", "post_open_retest", "five_minute_close", "stop_at_level", "failure_close_1m", "next_bar_open"),
    "prior_week_level": ("post_open_retest", "at_level", "five_minute_close", "stop_at_level", "failure_close_1m", "next_bar_open"),
    "asia_box": ("at_level", "five_minute_close", "stop_at_level", "failure_close_1m", "next_bar_open", "post_open_retest"),
    "asia_tdo_case": ("at_level", "tdo_close", "five_minute_close", "stop_at_level", "failure_close_1m", "next_bar_open"),
    "london_box": ("at_level", "post_open_reclaim", "five_minute_close", "stop_at_level", "failure_close_1m", "next_bar_open"),
    "cash_open_reclaim_case": ("next_bar_open", "at_level", "failure_close_1m"),
    "golden_pocket": ("pocket_retest_after_failure", "pocket_failure_close", "pocket_near_limit", "pocket_close", "pocket_far_limit"),
    "golden_pocket_continuation": ("pocket_retest_after_failure", "pocket_failure_close", "pocket_near_limit", "pocket_close", "pocket_far_limit"),
}
#: Branches whose preference order the tickets do not determine. Recorded in the
#: selection payload so the report can say which ones are still "earliest".
UNEVIDENCED_FALLBACK = "earliest_decision"


OPEN_UNTIL = 2**62  # an unresolved position is live until the clock ends

def _d(value: Any) -> Decimal | None:
    if value is None:
        return None
    if isinstance(value, Decimal):
        return value
    try:
        return Decimal(str(value))
    except Exception:
        return None


def resolve_trade(
    bars: Sequence[Mapping[str, Any]],
    *,
    side: str,
    entry: Decimal,
    stop: Decimal,
    target: Decimal | None,
    after_ns: int,
) -> dict[str, Any]:
    """First touch of stop or target on the completed bars after ``after_ns``.

    Bars are the session's own one-minute bars. A bar that touches both is
    recorded as ``ambiguous`` and treated as a stop (the conservative reading);
    the ambiguity is reported, never silently resolved.
    """
    for row in bars:
        if int(row.get("start") or 0) < int(after_ns):
            continue
        high, low = _d(row.get("H")), _d(row.get("L"))
        if high is None or low is None:
            continue
        if side == "long":
            hit_stop = low <= stop
            hit_target = target is not None and high >= target
        else:
            hit_stop = high >= stop
            hit_target = target is not None and low <= target
        if hit_stop and hit_target:
            return {
                "outcome": "ambiguous",
                "at_ns": int(row.get("end") or row.get("start")),
                "ambiguous": True,
            }
        if hit_target:
            return {"outcome": "target", "at_ns": int(row.get("end") or row.get("start")), "ambiguous": False}
        if hit_stop:
            return {"outcome": "stop", "at_ns": int(row.get("end") or row.get("start")), "ambiguous": False}
    return {"outcome": "open", "at_ns": None, "ambiguous": False}


def branch_alternatives(text: Any) -> tuple[str, ...]:
    """A record may name two adapter branches for one author level, separated
    by "/": the trailing hour's high at 11:24 on 2026-08-13 IS the 10-11 box
    high, and the "09:30 low" of 2026-04-28 is the cash-open sweep of the
    09:00-09:30 low inside the developing 9-10 box. Either branch reproduces
    the author's reference; the first named is the primary."""
    if not text:
        return ()
    return tuple(part.strip() for part in str(text).split("/") if part.strip())


def _episode_key(episode: Mapping[str, Any], running_bucket_min: int | None = None) -> tuple:
    """One opportunity: the branch, the side, the LINE (its kind and price) and
    the cycle. The reference id alone is the box, which every line of the play
    shares; keying on it collapsed every Judas long of a session into one
    opportunity and let the earliest fill of any line win (coordinator
    rebuild 2026-09-17)."""
    values = episode.get("values") or {}
    branch = str(episode.get("branch") or "")
    if branch.startswith("golden_pocket"):
        # one pocket is one opportunity whichever rung fills it (the near
        # limit, the far limit, the failure close or the retest): the author
        # sells the pocket once (2026-07-29 22:20) and adds later by hand
        return (branch, episode.get("side"), values.get("reference_id") or (episode.get("reference") or {}).get("id"), "pocket", None, None)
    kind = str(values.get("reference_kind") or "")
    running = kind.endswith("_running") or kind == "trailing_hour"
    if running:
        # a developing box has ONE high and ONE low however many five-minute
        # cuts it goes through and whatever price each cut printed: the edge
        # is the opportunity (2026-08-27: seven "lines" of the 12-13 hour's
        # high were one line moving up)
        # ... but a developing edge can be swept and fail MORE THAN ONCE in a
        # session, and a later cycle is its own opportunity (2026-07-30: the
        # London low fails at 03:21 and again at 04:01, where he buys;
        # 2026-08-27: the 12:00 hour's high at 12:34 and at 12:48, where he
        # sells). With ``running_bucket_min`` set, fills of one edge that
        # many minutes apart are different opportunities; None keeps one
        # opportunity an edge a session (the executed list).
        bucket = None
        if running_bucket_min and episode.get("decision_at") is not None:
            bucket = int(episode["decision_at"]) // (int(running_bucket_min) * 60 * 1_000_000_000)
        return (episode.get("branch"), episode.get("side"), None, kind.replace("_running", ""), str(values.get("level_edge") or ""), bucket)
    return (
        episode.get("branch"),
        episode.get("side"),
        values.get("reference_id") or (episode.get("reference") or {}).get("id"),
        kind,
        str(values.get("reference_px")),
        values.get("cycle"),
    )


def select_session_trades(
    episodes: Iterable[Mapping[str, Any]],
    *,
    bars: Sequence[Mapping[str, Any]],
    clock: tuple[int, int] | None = None,
    max_entries: int | None = None,
    stop_after_target: bool = True,
    reenter_same_line: bool = False,
    edge_first: bool = False,
    allow_adds: bool | str = False,
    max_per_line: int | None = None,
    allow_flips: bool = False,
    one_position: bool = True,
    running_bucket_min: int | None = None,
    windows: Sequence[tuple[int, int, int]] | None = None,
    objective_ends_session: bool | int | Decimal = False,
    trace: list | None = None,
    earliest_fill: bool = False,
) -> dict[str, Any]:
    """The author's trade list for one session.

    ``windows`` (start_ns, end_ns, max_round_trips), in time order and not
    overlapping, are the author's own clocks inside the session ("always
    terminating my trading session before 10am", "9-11 am est hands down best
    time to trade"): a setup decided outside every window is not taken, each
    window has its own cap, and with ``stop_after_target`` a paid objective
    ends THAT window only ("one and done"), not the ones after it, unless
    ``objective_ends_session`` ("One clean 100 point trade. Lock out."): then
    a paid objective ends the whole session. The one position carries across
    windows.

    Rules, in the audit's words:

    * the first qualifying setup in the author's clock -- episodes are ordered
      by decision time and the earliest is taken;
    * one position at a time -- a later setup is skipped while the open trade is
      still live;
    * no re-entry after a full objective -- once a taken trade reaches its
      target the session is finished;
    * at most ``max_entries`` entries a session;
    * at most ``max_per_line`` trades on one line and side (the first cycle and
      one re-entry): no ticket shows a third attempt at the same line;
    * with ``one_position`` False the list is the CANDIDATE list: every
      opportunity the framework admits, once, without the position bookkeeping
      (no blocking, no adds, no flips) -- the object the author chooses from;
    * with ``allow_flips`` a setup on the opposite side closes the open trade
      and is taken ("after a failed idea the author flips", audit 1.1;
      2025-10-13 shorts the R-Hi at 09:05 and buys the R-Lo at 09:40): the
      mechanical exit is not what keeps him in.

    Two modes of the same failure at the same reference are one opportunity: the
    earlier decision wins and the other is recorded as ``duplicate_of``.
    """
    if max_entries is None:
        max_entries = MAX_ENTRIES_PER_SESSION  # read at call time so a rescan override reaches it
    rows = []
    invalid_geometry = 0
    for episode in episodes:
        if episode.get("research_verdict") != "pass":
            continue
        decision = episode.get("decision_at")
        geometry = episode.get("geometry") or {}
        entry, stop = _d(geometry.get("entry")), _d(geometry.get("stop"))
        if decision is None or entry is None or stop is None:
            continue
        if clock is not None and not (clock[0] <= int(decision) < clock[1]):
            continue
        target = _d(geometry.get("target"))
        direction = 1 if str(episode.get("side")) == "long" else -1
        if (entry - stop) * direction <= 0 or (target is not None and (target - entry) * direction <= 0):
            # a stop or a target on the wrong side of the entry is not a trade: walked forward it
            # "reaches its target" on the first bar (Saint, 2026-09-18). Counted, never traded.
            invalid_geometry += 1
            continue
        rows.append((int(decision), episode, entry, stop, target))
    rows.sort(key=lambda item: (item[0], str(item[1].get("branch")), str(item[1].get("side"))))

    # One opportunity is one (branch, side, reference, cycle). Among its
    # alternative fills the author's own tickets decide which one he took; only
    # where they are silent does the earliest decision win.
    best_by_key: dict[tuple, tuple] = {}
    fallbacks: set[str] = set()
    for row in rows:
        episode = row[1]
        key = _episode_key(episode, running_bucket_min)
        order = MODE_PREFERENCE.get(str(episode.get("branch"))) or ()
        if not order:
            fallbacks.add(str(episode.get("branch")))
        mode = str((episode.get("values") or {}).get("confirmation_mode"))
        rank = order.index(mode) if mode in order else len(order)
        current = best_by_key.get(key)
        # ``earliest_fill``: a trader is filled by whichever of his orders comes first; he cannot wait for a
        # preferred fill that may come half an hour later or never (2026-08-28: the preferred retest limit
        # filled at 10:38, his entry after the five-minute close was 10:05). The preference then only breaks ties.
        better = current is None or ((row[0], rank) < (current[1][0], current[0]) if earliest_fill else (rank, row[0]) < (current[0], current[1][0]))
        if better:
            best_by_key[key] = (rank, row)
    rows = [item[1] for item in best_by_key.values()]
    # Two fills in the same minute, one at the box edge and one at a projection
    # line beyond it, are the same reversal seen from two lines; the author
    # names the edge ("R-Lo swept") and is filled on its reclaim (2025-10-03
    # 25,091.45 on the low's reclaim, not the -0.5 limit under it).
    EDGE_KINDS = {"box_low", "box_high", "london_low", "london_high"}
    # A line of the value-area layer that coincides with a line of the main range is a
    # confluence of that trade, not a second one: the main model's line names it
    # (2026-05-20 09:39: the 6-9 box's -0.33 at 29,028.60 and the value range's -1.33 at 29,029.42).
    layer = lambda item: 1 if str((item[1].get("values") or {}).get("reference_kind") or "").startswith("value_") else 0
    rows.sort(key=lambda item: (item[0] // (2 * 60 * 1_000_000_000) if edge_first else item[0], 0 if (edge_first and (item[1].get("values") or {}).get("reference_kind") in EDGE_KINDS) else 1, item[0], layer(item), str(item[1].get("branch")), str(item[1].get("side"))))

    taken: list[dict[str, Any]] = []
    seen_keys: set[tuple] = set()
    busy_until: int | None = None
    busy_side: str | None = None
    busy_line: Decimal | None = None
    round_trips = 0
    finished = False
    window_trips: dict[int, int] = {}
    window_finished: set[int] = set()
    per_line: list[tuple[str, Decimal, tuple | None]] = []
    skipped = {"duplicate": 0, "position_open": 0, "after_objective": 0, "max_entries": 0, "max_per_line": 0, "invalid_geometry": invalid_geometry}
    NEAR_PRICE = Decimal("2")
    NEAR_NS = 10 * 60 * 1_000_000_000
    for decision, episode, entry, stop, target in rows:
        key = _episode_key(episode, running_bucket_min)
        if key in seen_keys:
            skipped["duplicate"] += 1
            if trace is not None:
                trace.append({"candidate_id": episode.get("candidate_id"), "decision_at": decision, "side": episode.get("side"), "branch": episode.get("branch"), "entry": entry, "skipped": "duplicate"})
            continue
        # Two fills at the same price and side, minutes apart, are one trade
        # however the reference ids or branches differ: 2026-07-10 otherwise
        # takes 29,804.25 twice, at 09:04 and 09:05, and 2026-04-28 takes the
        # 09:00-09:30 low as a cash-open reclaim AND as a developing-box edge.
        # A later CYCLE of the same line is a new opportunity even at the same
        # price minutes later (2026-07-13: the PDL's second retest at 20:22
        # and the third cycle's fill at 20:29-20:41 are two entries).
        cycle = (episode.get("values") or {}).get("cycle")
        twin = next(
            (
                row
                for row in taken
                if row["side"] == episode.get("side")
                and abs(row["entry"] - entry) <= NEAR_PRICE
                and abs(int(row["decision_at"]) - decision) <= NEAR_NS
                and not (row["branch"] == episode.get("branch") and row.get("cycle") is not None and cycle is not None and row.get("cycle") != cycle)
            ),
            None,
        )
        if twin is not None:
            # the same trade seen from another drawn level is that trade's CONFLUENCE ("Bonus PDH", "More
            # confluence = higher rating"): kept on the trade, so a list is scored and graded by the trade,
            # whichever of its coincident levels happened to name it
            if episode.get("branch") != twin["branch"] or (episode.get("values") or {}).get("reference_kind") != twin.get("reference_kind"):
                twin.setdefault("confluences", []).append({"branch": episode.get("branch"), "reference_kind": (episode.get("values") or {}).get("reference_kind"), "decision_at": decision, "entry": entry, "candidate_id": episode.get("candidate_id")})
            skipped["duplicate"] += 1
            if trace is not None:
                trace.append({"candidate_id": episode.get("candidate_id"), "decision_at": decision, "side": episode.get("side"), "branch": episode.get("branch"), "entry": entry, "skipped": "duplicate"})
            continue
        if finished:
            skipped["after_objective"] += 1
            if trace is not None:
                trace.append({"candidate_id": episode.get("candidate_id"), "decision_at": decision, "side": episode.get("side"), "branch": episode.get("branch"), "entry": entry, "skipped": "after_objective"})
            continue
        window = None
        if windows is not None:
            window = next((n for n, (start, end, _cap) in enumerate(windows) if start <= decision < end), None)
            if window is None:
                skipped["outside_windows"] = skipped.get("outside_windows", 0) + 1
                if trace is not None:
                    trace.append({"candidate_id": episode.get("candidate_id"), "decision_at": decision, "side": episode.get("side"), "branch": episode.get("branch"), "entry": entry, "skipped": "outside_windows"})
                continue
            if window in window_finished:
                skipped["after_objective"] += 1
                if trace is not None:
                    trace.append({"candidate_id": episode.get("candidate_id"), "decision_at": decision, "side": episode.get("side"), "branch": episode.get("branch"), "entry": entry, "skipped": "after_objective"})
                continue
        line_px = _d((episode.get("values") or {}).get("reference_px")) or entry
        running_line = _episode_key(episode, running_bucket_min)[2] is None
        in_position = one_position and busy_until is not None and decision < busy_until and str(episode.get("side")) == busy_side
        # an add: the same side while the position is live -- any line when
        # ``allow_adds`` is True, the SAME line on a later cycle when it is
        # "same_line" (Green Bird's re-entry of a level he is already long)
        is_add = bool(in_position and (allow_adds is True or (allow_adds == "same_line" and busy_line is not None and abs(line_px - busy_line) <= NEAR_PRICE * 3)))
        if not is_add and round_trips >= max_entries:
            skipped["max_entries"] += 1
            if trace is not None:
                trace.append({"candidate_id": episode.get("candidate_id"), "decision_at": decision, "side": episode.get("side"), "branch": episode.get("branch"), "entry": entry, "skipped": "max_entries"})
            continue
        if window is not None and not is_add and window_trips.get(window, 0) >= windows[window][2]:
            skipped["max_entries"] += 1
            if trace is not None:
                trace.append({"candidate_id": episode.get("candidate_id"), "decision_at": decision, "side": episode.get("side"), "branch": episode.get("branch"), "entry": entry, "skipped": "max_entries"})
            continue
        line_tag = _episode_key(episode, running_bucket_min)[:2] + _episode_key(episode, running_bucket_min)[3:5] if running_line else None
        if max_per_line is not None and sum(1 for side_, px, tag in per_line if side_ == str(episode.get("side")) and ((tag is not None and tag == line_tag) or (tag is None and line_tag is None and abs(px - line_px) <= NEAR_PRICE * 3))) >= max_per_line:
            skipped["max_per_line"] += 1
            if trace is not None:
                trace.append({"candidate_id": episode.get("candidate_id"), "decision_at": decision, "side": episode.get("side"), "branch": episode.get("branch"), "entry": entry, "skipped": "max_per_line"})
            continue
        # One position at a time blocks the OPPOSITE side while a trade is live;
        # a second entry on the same side is an add ("scaling in at the lines
        # and out at the next line", audit §1.1) and counts against the cap.
        if one_position and busy_until is not None and decision < busy_until and not is_add:
            if allow_flips and str(episode.get("side")) != busy_side and taken:
                taken[-1]["flipped_at"] = decision
                taken[-1]["flipped_by"] = episode.get("candidate_id")
                busy_until = decision
            else:
                skipped["position_open"] += 1
                if trace is not None:
                    trace.append({"candidate_id": episode.get("candidate_id"), "decision_at": decision, "side": episode.get("side"), "branch": episode.get("branch"), "entry": entry, "skipped": "position_open"})
                continue
        # A stopped idea is not re-entered at the same line: "after a failed
        # idea the author flips" (audit §1.1); no ticket shows a second entry at
        # a line that has just stopped him out.
        if not reenter_same_line and any(
            row["outcome"] == "stop"
            and row["side"] == episode.get("side")
            and abs(_d(row.get("reference_px") or row["entry"]) - _d((episode.get("values") or {}).get("reference_px") or entry)) <= NEAR_PRICE * 3
            for row in taken
        ):
            skipped["same_line_after_stop"] = skipped.get("same_line_after_stop", 0) + 1
            if trace is not None:
                trace.append({"candidate_id": episode.get("candidate_id"), "decision_at": decision, "side": episode.get("side"), "branch": episode.get("branch"), "entry": entry, "skipped": "same_line_after_stop"})
            continue
        seen_keys.add(key)
        result = resolve_trade(bars, side=str(episode.get("side")), entry=entry, stop=stop, target=target, after_ns=decision)
        taken.append(
            {
                "candidate_id": episode.get("candidate_id"),
                "branch": episode.get("branch"),
                "side": episode.get("side"),
                "decision_at": decision,
                "entry": entry,
                "stop": stop,
                "target": target,
                "stop_points": abs(entry - stop),
                "reward_points": None if target is None else abs(target - entry),
                "r_multiple_at_target": None
                if target is None or entry == stop
                else abs(target - entry) / abs(entry - stop),
                "confirmation_mode": (episode.get("values") or {}).get("confirmation_mode"),
                "cycle": (episode.get("values") or {}).get("cycle"),
                "reference_px": (episode.get("values") or {}).get("reference_px"),
                "reference_kind": (episode.get("values") or {}).get("reference_kind"),
                "reference_id": (episode.get("reference") or {}).get("id"),
                "outcome": result["outcome"],
                "outcome_at": result["at_ns"],
                "outcome_ambiguous": result["ambiguous"],
            }
        )
        if not is_add:
            round_trips += 1
            if window is not None:
                window_trips[window] = window_trips.get(window, 0) + 1
        per_line.append((str(episode.get("side")), line_px, line_tag))
        # A position still open at the end of the bars is live for the rest of
        # the clock: nothing but an add or a flip may follow it.
        resolved_at = result["at_ns"] if result["at_ns"] is not None else (int(clock[1]) if clock is not None else OPEN_UNTIL)
        if busy_until is None or resolved_at > busy_until:
            busy_until = resolved_at
        busy_side = str(episode.get("side"))
        busy_line = line_px
        if result["outcome"] == "target" and stop_after_target:
            # ``objective_ends_session`` True: any paid objective ends the session; a number: only a paid
            # objective of at least that many points does ("One clean 100 point trade. Lock out."), a smaller
            # one ends its own window
            reward = abs(target - entry) if target is not None else Decimal(0)
            locks = objective_ends_session is True or (objective_ends_session not in (False, None) and reward >= Decimal(str(objective_ends_session)))
            if window is None or locks:
                finished = True
            else:
                window_finished.add(window)
    return {
        "entries": taken,
        "n_entries": len(taken),
        "n_round_trips": round_trips,
        "mode_preference_fallback": sorted(fallbacks),
        "n_candidates": len(rows),
        "skipped": skipped,
        "max_entries": max_entries,
        "rule": "first qualifying setup in the author's clock; one position at a time; at most three a segment" + ("; no re-entry after a full objective (Green Bird)" if stop_after_target else "; a stopped idea may be followed by the next qualifying setup (Jumbo)"),
    }
