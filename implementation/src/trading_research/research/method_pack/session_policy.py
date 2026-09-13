"""Evidence-scoped NQ matching sessions, separate from cash-market calendars.

Unverified holiday schedules are explicit unknowns. No last-observed-day
fallback is allowed across an uncertified expected trading session.
"""
from __future__ import annotations
from datetime import date, timedelta
from functools import lru_cache
import json
from pathlib import Path

from .clocks import et_ns, ns_to_et
from .empirical_protocol import content_hash

POLICY_PATH = Path(__file__).with_name("nq_session_policy_v2.json")
MINUTE = 60_000_000_000


def _nth(year, month, weekday, occurrence):
    first = date(year, month, 1)
    return first + timedelta(days=(weekday - first.weekday()) % 7 + 7 * (occurrence - 1))


def _observed(day):
    return day - timedelta(days=1) if day.weekday() == 5 else day + timedelta(days=1) if day.weekday() == 6 else day


@lru_cache(maxsize=20)
def possible_holidays(year):
    """Investigation flags only. They do not assert a matching-hours change."""
    from dateutil.easter import easter
    last_may = date(year, 5, 31)
    memorial = last_may - timedelta(days=last_may.weekday())
    thanksgiving = _nth(year, 11, 3, 4)
    result = {_observed(date(year, 1, 1)): "new_year", _observed(date(year + 1, 1, 1)): "new_year",
              _nth(year, 1, 0, 3): "mlk", _nth(year, 2, 0, 3): "presidents",
              easter(year) - timedelta(days=2): "good_friday", memorial: "memorial",
              _observed(date(year, 7, 4)): "independence", _nth(year, 9, 0, 1): "labor",
              thanksgiving: "thanksgiving", thanksgiving + timedelta(days=1): "after_thanksgiving",
              _observed(date(year, 12, 25)): "christmas", date(year, 12, 24): "christmas_eve",
              date(year, 7, 3): "independence_eve"}
    if year >= 2022:
        result[_observed(date(year, 6, 19))] = "juneteenth"
    return result


class NQSessionPolicy:
    def __init__(self, document=None):
        self.document = json.loads(POLICY_PATH.read_text()) if document is None else document
        if self.document["product"] != "NQ" or self.document["timezone"] != "America/New_York":
            raise ValueError("session policy must identify NQ and its timezone")
        self.sha256 = content_hash(self.document)
        self.exceptions = self.document["exceptions"]

    def day(self, day):
        day = date.fromisoformat(day) if isinstance(day, str) else day
        explicit = self.exceptions.get(str(day))
        if explicit:
            if not explicit.get("source_url") or not explicit.get("reviewed_product_scope"):
                raise ValueError("calendar exception lacks product evidence")
            return {"date": str(day), **explicit}
        if day.weekday() >= 5:
            return {"date": str(day), "state": "closed_rth", "reason": "regular weekend", "rth_end": None}
        flag = possible_holidays(day.year).get(day)
        if flag:
            return {"date": str(day), "state": "unverified_holiday", "reason": flag,
                    "rth_end": None, "required_input": "dated NQ/CME equity matching-hours schedule"}
        return {"date": str(day), "state": "regular", "rth_end": "16:00",
                "reason": "versioned regular NQ matching policy; unscheduled interruptions not inferred"}

    def rth(self, day):
        day = date.fromisoformat(day) if isinstance(day, str) else day
        info = self.day(day)
        if info["state"] == "closed_rth":
            return {**info, "windows": [], "known": True}
        if info["state"] == "unverified_holiday":
            return {**info, "windows": [[et_ns(day, 9, 30), et_ns(day, 16, 0)]], "known": False}
        hour, minute = map(int, info.get("rth_end", "16:00").split(":"))
        return {**info, "windows": [[et_ns(day, 9, 30), et_ns(day, hour, minute)]], "known": True}

    def previous_session(self, day):
        """Stop at unknowns; do not silently bridge an absent/unverified date."""
        day = date.fromisoformat(day) if isinstance(day, str) else day
        for offset in range(1, 15):
            earlier = day - timedelta(days=offset)
            info = self.rth(earlier)
            if info["state"] == "closed_rth":
                continue
            return info
        raise ValueError("no session within explicit 14-day calendar bound")

    def state(self, start, end):
        if end <= start:
            raise ValueError("positive session interval required")
        first, last = ns_to_et(start), ns_to_et(end - 1)
        if first.date() != last.date():
            return "mixed_or_unknown"
        day = first.date()
        minute, final = first.hour * 60 + first.minute, last.hour * 60 + last.minute
        if day.weekday() == 5 or day.weekday() == 6 and final < 18 * 60:
            return "scheduled_closure"
        if day.weekday() == 4 and minute >= 17 * 60:
            return "scheduled_closure"
        if minute >= 17 * 60 and final < 18 * 60:
            return "scheduled_closure"
        if day < date(2021, 6, 28) and minute >= 16 * 60 + 15 and final < 16 * 60 + 30:
            return "scheduled_closure"
        info = self.day(day)
        for begin, finish in info.get("closed_local", []):
            h, m = map(int, begin.split(":")); h2, m2 = map(int, finish.split(":"))
            if minute >= h * 60 + m and final < h2 * 60 + m2:
                return "scheduled_closure"
        if info["state"] == "unverified_holiday":
            return "unverified_holiday"
        return "scheduled_open"


def same_contract_prior(policy, day, instrument_id, windows):
    expected = policy.previous_session(day)
    if not expected["known"]:
        return {"window": None, "reason": "prior_session_calendar_unverified", "expected": expected}
    matches = [w for w in windows if w.get("session_date") == expected["date"]
               and str(w.get("instrument_id")) == str(instrument_id)]
    if len(matches) != 1:
        return {"window": None, "reason": "same_contract_prior_session_missing", "expected": expected}
    return {"window": matches[0], "reason": None, "expected": expected}


class ReconstructionSessionPolicy(NQSessionPolicy):
    """Explicit model calendar allowed by the strategy reconstruction work order."""
    def __init__(self,document=None):
        super().__init__(document)
        from .strategy_policy import POLICY
        self.sha256=content_hash({'source_calendar_sha256':self.sha256,'inferred_calendar':POLICY['calendar']})

    def day(self,day):
        info=super().day(day)
        day=date.fromisoformat(day) if isinstance(day,str) else day
        # NQ records show a full 2021-12-31 RTH. Do not import the
        # observed-Friday closure convention used by other calendars.
        if info['state']=='unverified_holiday' and info['reason']=='new_year' and day.month==12 and day.day==31:
            return {**info,'state':'regular','rth_end':'16:00','calendar_model':'strategy-reconstruction-v1',
                'reason':'inferred regular RTH before Saturday New Year; corroborated by native 2021-12-31 trading'}
        if info['state']=='unverified_holiday' and info['reason'] in {'new_year','christmas'}:
            return {**info,'state':'closed_rth','calendar_model':'strategy-reconstruction-v1',
                'reason':'inferred '+info['reason']+' RTH closure','closed_local':[['00:00','18:00']]}
        return info
