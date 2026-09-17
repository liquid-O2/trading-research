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
    # --- read off the replay of the author's tickets (strict matches, 2026-09-17)
    "judas_reversal": ("at_level", "signature_close"),            # 4 + 3 tickets
    "other_session": ("rejection_block", "absorption"),           # 2 + 1
    "extension_reaction": ("absorption", "orderblock", "rejection_block"),  # 2 + 1 + 1
    "timed_pzone_reversal": ("rejection_close", "at_level"),      # 1 + 1
    "internal_rotation": ("two_minute_close",),                   # 1 (2026-07-10)
    "single_purged": ("two_minute_close",),                       # 1 (2026-07-28)
    # The ticket-evidenced mode first, then the mode the SOURCE TEXT names for
    # the same failure trade -- "wait for the 5 min close back below the PDL
    # after sweeping above it", then "low risk entry on any retracement with
    # stops above PDL" (GB p.3). That rule is written for the failure family as
    # a whole, so the retracement limit is supported on every failure branch,
    # not only on the ones a ticket happens to show it on.
    "prior_week_level": ("post_open_retest", "five_minute_close", "at_level"),   # ticket 2025-11-19
    "previous_hour": ("five_minute_close", "at_level"),                         # ticket 2026-04-23
    "nyam_box": ("five_minute_close", "at_level"),                              # ticket 2026-08-28
    # --- no ticket reproduced these branches strictly; the order is the one the
    # --- SOURCE TEXT names for the Green Bird failure trade -- "wait for the
    # --- 5-minute close through the level", then "low risk entry on any
    # --- retracement with stops above PDL" (GB p.3) -- and nothing more.
    "prior_day_level": ("five_minute_close", "at_level"),
    "asia_box": ("five_minute_close", "at_level"),
    "london_box": ("five_minute_close", "at_level"),
    "asia_tdo_case": ("five_minute_close", "at_level"),
}

#: Branches whose preference order the tickets do not determine. Recorded in the
#: selection payload so the report can say which ones are still "earliest".
UNEVIDENCED_FALLBACK = "earliest_decision"


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


def _episode_key(episode: Mapping[str, Any]) -> tuple:
    values = episode.get("values") or {}
    return (
        episode.get("branch"),
        episode.get("side"),
        values.get("reference_id") or (episode.get("reference") or {}).get("id"),
        values.get("cycle"),
    )


def select_session_trades(
    episodes: Iterable[Mapping[str, Any]],
    *,
    bars: Sequence[Mapping[str, Any]],
    clock: tuple[int, int] | None = None,
    max_entries: int = MAX_ENTRIES_PER_SESSION,
) -> dict[str, Any]:
    """The author's trade list for one session.

    Rules, in the audit's words:

    * the first qualifying setup in the author's clock -- episodes are ordered
      by decision time and the earliest is taken;
    * one position at a time -- a later setup is skipped while the open trade is
      still live;
    * no re-entry after a full objective -- once a taken trade reaches its
      target the session is finished;
    * at most ``max_entries`` entries a session.

    Two modes of the same failure at the same reference are one opportunity: the
    earlier decision wins and the other is recorded as ``duplicate_of``.
    """
    rows = []
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
        rows.append((int(decision), episode, entry, stop, _d(geometry.get("target"))))
    rows.sort(key=lambda item: (item[0], str(item[1].get("branch")), str(item[1].get("side"))))

    # One opportunity is one (branch, side, reference, cycle). Among its
    # alternative fills the author's own tickets decide which one he took; only
    # where they are silent does the earliest decision win.
    best_by_key: dict[tuple, tuple] = {}
    fallbacks: set[str] = set()
    for row in rows:
        episode = row[1]
        key = _episode_key(episode)
        order = MODE_PREFERENCE.get(str(episode.get("branch"))) or ()
        if not order:
            fallbacks.add(str(episode.get("branch")))
        mode = str((episode.get("values") or {}).get("confirmation_mode"))
        rank = order.index(mode) if mode in order else len(order)
        current = best_by_key.get(key)
        if current is None or (rank, row[0]) < (current[0], current[1][0]):
            best_by_key[key] = (rank, row)
    rows = [item[1] for item in best_by_key.values()]
    rows.sort(key=lambda item: (item[0], str(item[1].get("branch")), str(item[1].get("side"))))

    taken: list[dict[str, Any]] = []
    seen_keys: set[tuple] = set()
    busy_until: int | None = None
    finished = False
    skipped = {"duplicate": 0, "position_open": 0, "after_objective": 0, "max_entries": 0}
    NEAR_PRICE = Decimal("2")
    NEAR_NS = 10 * 60 * 1_000_000_000
    for decision, episode, entry, stop, target in rows:
        key = _episode_key(episode)
        if key in seen_keys:
            skipped["duplicate"] += 1
            continue
        # Two fills at the same price, on the same branch and side, minutes
        # apart are one trade however the reference ids differ: 2026-07-10
        # otherwise takes 29,804.25 twice, at 09:04 and 09:05.
        if any(
            row["branch"] == episode.get("branch")
            and row["side"] == episode.get("side")
            and abs(row["entry"] - entry) <= NEAR_PRICE
            and abs(int(row["decision_at"]) - decision) <= NEAR_NS
            for row in taken
        ):
            skipped["duplicate"] += 1
            continue
        if finished:
            skipped["after_objective"] += 1
            continue
        if len(taken) >= max_entries:
            skipped["max_entries"] += 1
            continue
        if busy_until is not None and decision < busy_until:
            skipped["position_open"] += 1
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
                "reference_id": (episode.get("reference") or {}).get("id"),
                "outcome": result["outcome"],
                "outcome_at": result["at_ns"],
                "outcome_ambiguous": result["ambiguous"],
            }
        )
        busy_until = result["at_ns"]
        if result["outcome"] == "target":
            finished = True
    return {
        "entries": taken,
        "n_entries": len(taken),
        "mode_preference_fallback": sorted(fallbacks),
        "n_candidates": len(rows),
        "skipped": skipped,
        "max_entries": max_entries,
        "rule": "first qualifying setup in the author's clock; one position at a time; no re-entry after a full objective; at most three a session",
    }
