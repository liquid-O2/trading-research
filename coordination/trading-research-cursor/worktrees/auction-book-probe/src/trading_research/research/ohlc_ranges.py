"""Ranges and partially ordered paths on observed minute OHLC intervals.

This is an OHLC observation domain. It does not mint trade events, exact
intraminute timestamps, F09 receipts, or executable fills. Missing minutes and
raw-contract changes make a requested window unavailable.
"""
from __future__ import annotations

from array import array
from bisect import bisect_left
from dataclasses import dataclass
from datetime import date, time, timedelta
from fractions import Fraction
from functools import cached_property
from itertools import accumulate

from trading_research.context.ranges import RangeArithmetic
from trading_research.errors import ContractError, DependencyUnavailable, IntegrityError
from trading_research.foundations.calendar import local_timestamp
from trading_research.operations.artifacts import digest

MINUTE = 60_000_000_000
VERSION = "observed-minute-ohlc-ranges-paths-v1"


def wall_endpoint(day: date, endpoint: dict, zone: str) -> int:
    if (type(day) is not date or set(endpoint) != {"day_offset", "time"}
            or type(endpoint["day_offset"]) is not int or not -7 <= endpoint["day_offset"] <= 7):
        raise ContractError("explicit bounded civil-date endpoint required")
    clock = time.fromisoformat(endpoint["time"])
    if clock.tzinfo is not None or clock.second or clock.microsecond:
        raise ContractError("source formation must align to observed minute intervals")
    return local_timestamp(day + timedelta(days=endpoint["day_offset"]), clock, zone)


def wall_interval(day: date, recipe: dict, zone: str) -> tuple[int, int]:
    if set(recipe) != {"start", "end", "interval"} or recipe["interval"] != "[start,end)":
        raise ContractError("explicit half-open clock recipe required")
    start, end = (wall_endpoint(day, recipe[k], zone) for k in ("start", "end"))
    if end <= start:
        raise ContractError("positive formation interval required")
    return start, end


@dataclass(frozen=True, slots=True, init=False)
class MinuteBars:
    """Compact, immutable index of admitted numeric columns.

    Source admission and its content-addressed tables supply ``source_version``.
    The numerical constructor also supports independent fixtures; constructing
    this index alone is never a source-admission certificate.
    """

    source_version: str
    start: memoryview
    end: memoryview
    known: memoryview
    open: memoryview
    high: memoryview
    low: memoryview
    close: memoryview
    volume: memoryview
    contract: memoryview
    contract_names: tuple
    bad: memoryview
    gaps: memoryview
    rolls: memoryview

    def __init__(self, columns: dict, *, source_version: str, maximum_rows=6_000_000):
        names = ("start_ns", "end_ns", "known_at_ns", "open_ticks", "high_ticks",
                 "low_ticks", "close_ticks", "volume", "contract_key", "valid")
        if (type(source_version) is not str or not 0 < len(source_version) <= 512
                or type(columns) is not dict or not set(names) <= set(columns)):
            raise ContractError("minute index needs actual columns and source identity")
        size = len(columns["start_ns"])
        if (type(maximum_rows) is not int or not 0 < size <= maximum_rows
                or any(len(columns[k]) != size for k in names)):
            raise ContractError("bounded equal-length nonempty minute columns required")
        object.__setattr__(self, "source_version", source_version)
        # Copy into immutable bytes: neither the caller's lists nor an exposed
        # view can alter an already admitted window without changing identity.
        for attr, name in zip(("start", "end", "known", "open", "high", "low", "close", "volume"), names[:8], strict=True):
            if any(type(v) is not int for v in columns[name]):
                raise ContractError("exact integer columns required; booleans are not numeric observations")
            try:
                values = memoryview(array("q", columns[name]).tobytes()).cast("q")
            except (OverflowError, TypeError, ValueError) as exc:
                raise ContractError("signed 64-bit integer column required") from exc
            object.__setattr__(self, attr, values)
        keys = {}
        codes = []
        bad = []
        for i, (key, valid) in enumerate(zip(columns["contract_key"], columns["valid"], strict=True)):
            if (type(valid) is not bool or key is not None and type(key) is not str
                    or self.start[i] < 0 or valid and self.start[i] % MINUTE
                    or self.end[i] != self.start[i] + MINUTE or self.known[i] < self.end[i]
                    or i and self.start[i] <= self.start[i - 1]):
                raise IntegrityError("invalid, duplicated or unordered minute identity/availability")
            if valid and (type(key) is not str or not key or self.volume[i] <= 0
                    or not self.low[i] <= min(self.open[i], self.close[i])
                    <= max(self.open[i], self.close[i]) <= self.high[i]):
                raise IntegrityError("a valid minute lacks ordered OHLC, positive volume or contract identity")
            code = keys.setdefault(key, len(keys))
            codes.append(code)
            bad.append(not valid)
        object.__setattr__(self, "contract", memoryview(array("i", codes).tobytes()).cast("i"))
        object.__setattr__(self, "contract_names", tuple(keys))
        for attr, events in (("bad", bad),
                ("gaps", (i > 0 and self.start[i] != self.end[i - 1] for i in range(size))),
                ("rolls", (i > 0 and self.contract[i] != self.contract[i - 1] for i in range(size)))):
            values = array("I", (0, *accumulate(events)))
            object.__setattr__(self, attr, memoryview(values.tobytes()).cast("I"))

    @classmethod
    def from_table(cls, table, *, source_version, maximum_rows=6_000_000):
        names = ("start_ns", "end_ns", "known_at_ns", "open_ticks", "high_ticks",
                 "low_ticks", "close_ticks", "volume", "contract_key", "valid")
        columns = {k: table[k].to_pylist() for k in names}
        # A nullable, quarantined source observation remains an invalid slot.
        # Internal storage zeros are never observations: every containing
        # window is unavailable, and the canonical table retains the NULLs.
        for name in names[3:8]:
            columns[name] = [0 if value is None and columns["valid"][i] is False else value
                             for i, value in enumerate(columns[name])]
        return cls(columns, source_version=source_version, maximum_rows=maximum_rows)

    def window(self, start: int, end: int, *, contract_key: str | None = None,
               available_at: int | None = None) -> OhlcWindow:
        if (type(start) is not int or type(end) is not int or start < 0
                or available_at is not None and (type(available_at) is not int or available_at < 0)
                or contract_key is not None and (type(contract_key) is not str or not contract_key)
                or start % MINUTE or end % MINUTE or not start < end <= start + 7 * 1440 * MINUTE):
            raise ContractError("bounded half-open whole-minute window required")
        left, right = bisect_left(self.start, start), bisect_left(self.start, end)
        reasons = []
        count = right - left
        expected = (end - start) // MINUTE
        if not count:
            reasons.append("missing_all_minutes")
        else:
            if self.start[left] != start:
                reasons.append("missing_first_minute")
            if self.end[right - 1] != end:
                reasons.append("missing_last_minute")
            if self.gaps[right] - self.gaps[left + 1]:
                reasons.append("missing_interior_minutes")
            if self.bad[right] - self.bad[left]:
                reasons.append("invalid_source_minutes")
            if self.rolls[right] - self.rolls[left + 1]:
                reasons.append("raw_contract_transition")
            key = self.contract_names[self.contract[left]]
            if contract_key is not None and key != contract_key:
                reasons.append("different_raw_contract")
            if available_at is not None and max(self.known[left:right]) > available_at:
                reasons.append("final_bar_not_available")
        if count != expected and not any(r.startswith("missing_") for r in reasons):
            reasons.append("minute_count_mismatch")
        return OhlcWindow(self, start, end, left, right, expected, tuple(reasons), available_at)


@dataclass(frozen=True)
class OhlcWindow:
    series: MinuteBars
    start: int
    end: int
    left: int
    right: int
    expected_minutes: int
    reasons: tuple[str, ...]
    observation_cut_ns: int | None = None

    @property
    def complete(self):
        return not self.reasons

    @property
    def count(self):
        return self.right - self.left

    @property
    def contract_key(self):
        return None if not self.count else self.series.contract_names[self.series.contract[self.left]]

    def require(self):
        if not self.complete:
            raise DependencyUnavailable(";".join(self.reasons))

    @cached_property
    def version(self):
        return digest({"definition": VERSION, "source": self.series.source_version,
                       "start": self.start, "end": self.end, "contract": self.contract_key,
                       "count": self.count, "reasons": self.reasons,
                       "observation_cut_ns": self.observation_cut_ns})

    @cached_property
    def _price_bounds(self):
        self.require()
        s, a, b = self.series, self.left, self.right
        return min(s.low[a:b]), max(s.high[a:b])

    @cached_property
    def available_at_ns(self):
        self.require()
        return max(self.end, max(self.series.known[self.left:self.right]))

    @cached_property
    def volume(self):
        self.require()
        return sum(self.series.volume[self.left:self.right])

    @cached_property
    def _geometry(self):
        low, high = self._price_bounds
        return RangeArithmetic(low, high, self.series.open[self.left], self.series.close[self.right - 1])

    def geometry(self) -> RangeArithmetic:
        return self._geometry

    @cached_property
    def _summary_values(self):
        common = {"window_version": self.version, "source_version": self.series.source_version,
                  "formation_start_ns": self.start, "formation_end_ns": self.end,
                  "expected_minutes": self.expected_minutes, "observed_minutes": self.count,
                  "observation_cut_ns": self.observation_cut_ns,
                  "contract_key": self.contract_key, "status": "complete" if self.complete else "unavailable",
                  "exclusion_reasons": self.reasons}
        if not self.complete:
            return tuple(common.items())
        g, s, a, b = self.geometry(), self.series, self.left, self.right
        return tuple({**common, "available_at_ns": self.available_at_ns,
                "open_ticks": int(g.open), "high_ticks": int(g.high),
                "low_ticks": int(g.low), "close_ticks": int(g.close),
                "width_ticks": int(g.width), "volume": self.volume,
                "body25_ticks": float(g.body25()), "lower_body25_ticks": float(g.session_body_lower25()),
                "wick_quarter_ticks": None if not g.usable else float(g.coordinate(Fraction(1, 4))),
                "open_position": None if not g.usable else float(g.normalized_position(g.open)),
                "formation_up_ticks": int(g.high - g.open), "formation_down_ticks": int(g.open - g.low),
                "zero_width": not g.usable}.items())

    def summary(self):
        # Only immutable facts are cached. Callers retain an independent dict
        # and reasons list, so annotating a returned summary cannot mutate
        # later observations under the same window identity.
        result = dict(self._summary_values)
        result["exclusion_reasons"] = list(self.reasons)
        return result


def _first_hit(s, a, b, lower, upper, *, strict):
    for i in range(a, b):
        up = s.high[i] > upper if strict else s.high[i] >= upper
        down = s.low[i] < lower if strict else s.low[i] <= lower
        if not (up or down):
            continue
        open_up = s.open[i] > upper if strict else s.open[i] >= upper
        open_down = s.open[i] < lower if strict else s.open[i] <= lower
        side = ("upper" if open_up else "lower" if open_down else
                "ambiguous" if up and down else "upper" if up else "lower")
        return i, side, up, down
    return None, "neither", False, False


def range_path(window: OhlcWindow, *, low: int, high: int, strict=True) -> dict:
    if (type(low) is not int or type(high) is not int or high <= low or type(strict) is not bool):
        raise ContractError("nonzero exact frozen range and explicit reach/breach rule required")
    base = {"window_version": window.version, "origin_ns": window.start, "endpoint_ns": window.end,
            "rule": "strict_breach" if strict else "inclusive_boundary_reach",
            "observed_minutes": window.count, "exclusion_reasons": list(window.reasons)}
    if not window.complete:
        return {**base, "status": "censored", "path": "censored"}
    s, a, b = window.series, window.left, window.right
    first, side, first_up, first_down = _first_hit(s, a, b, low, high, strict=strict)
    minimum, maximum = window._price_bounds
    upper = maximum > high if strict else maximum >= high
    lower = minimum < low if strict else minimum <= low
    if upper and lower:
        path = "ambiguous" if side == "ambiguous" else "high_then_low" if side == "upper" else "low_then_high"
    else:
        path = "high_only" if upper else "low_only" if lower else "no_break"
    second = None
    if upper and lower:
        if first_up and first_down:
            second = first
        elif side == "upper":
            second = next(i for i in range(first + 1, b)
                          if (s.low[i] < low if strict else s.low[i] <= low))
        else:
            second = next(i for i in range(first + 1, b)
                          if (s.high[i] > high if strict else s.high[i] >= high))
    reclaim = None
    if first is not None and side != "ambiguous":
        reclaim = next((i for i in range(first, b) if low < s.close[i] < high), None)
    # First/second event times are intervals, never bar-open timestamps posing
    # as exact crossings. The cut-minute open is a label observation, not a
    # feature assumed available at the observation cut.
    return {**base, "status": "ambiguous" if side == "ambiguous" else "observed", "path": path,
            "first_side": side, "upper_reached": upper, "lower_reached": lower,
            "first_interval_start_ns": None if first is None else s.start[first],
            "first_interval_end_ns": None if first is None else s.end[first],
            "second_interval_start_ns": None if second is None else s.start[second],
            "second_interval_end_ns": None if second is None else s.end[second],
            "close_confirmed_reclaim_at_ns": None if reclaim is None else s.end[reclaim],
            "reclaim_known_at_ns": None if reclaim is None else s.known[reclaim],
            "label_origin_open_ticks": s.open[a], "terminal_ticks": s.close[b - 1] - s.open[a],
            "maximum_up_ticks": max(0, maximum - s.open[a]),
            "maximum_down_ticks": max(0, s.open[a] - minimum),
            "upper_overshoot_ticks": max(0, maximum - high),
            "lower_overshoot_ticks": max(0, low - minimum),
            "maturity_at_ns": window.available_at_ns,
            "origin_open_is_prediction_feature": False}


def level_outcome(window: OhlcWindow, *, level: Fraction, side: int) -> dict:
    """Bound post-contact excursions without assigning pre-contact extrema.

    A bar straddling a level establishes compatibility, not a trade at every
    intervening price. Exact O/H/L/C equality supplies a definite observed
    level print. The output retains that distinction and a fixed endpoint.
    """
    if type(level) is not Fraction or type(side) is not int or side not in (-1, 1):
        raise ContractError("exact level and named directional outcome required")
    return _level_result(window, level=level, side=side,
                         observations=None if not window.complete else _level_observations(window, level))


def _level_observations(window: OhlcWindow, level: Fraction):
    """One integer scan shared by contact counts and contact excursion bounds.

    For integer observations x, x<=n/d iff x<=floor(n/d), while x>=n/d
    iff x>=ceil(n/d). The target itself remains the exact rational n/d.
    """
    s, a, b = window.series, window.left, window.right
    numerator, denominator = level.numerator, level.denominator
    floor = numerator // denominator
    ceiling = -(-numerator // denominator)
    strict_below, strict_above = ceiling - 1, floor + 1
    integer_level = denominator == 1
    first = last = definite = None
    compatible_count = definite_count = 0
    gap = False
    for i in range(a, b):
        hit = s.low[i] <= floor and s.high[i] >= ceiling
        if hit:
            compatible_count += 1
            if first is None:
                first = i
            last = i
            if integer_level and numerator in (s.open[i], s.high[i], s.low[i], s.close[i]):
                definite_count += 1
                if definite is None:
                    definite = i
        elif i > a and not gap:
            previous, opening = s.close[i - 1], s.open[i]
            gap = (previous <= strict_below and opening >= strict_above
                   or opening <= strict_below and previous >= strict_above)
    return first, last, definite, compatible_count, definite_count, gap


def _level_result(window: OhlcWindow, *, level: Fraction, side: int, observations) -> dict:
    base = {"window_version": window.version, "endpoint_ns": window.end,
            "level_numerator": level.numerator, "level_denominator": level.denominator,
            "side": side, "exclusion_reasons": list(window.reasons)}
    if not window.complete:
        return {**base, "status": "censored"}
    s, a, b = window.series, window.left, window.right
    contact, last, definite, _, _, gap = observations
    if contact is None:
        return {**base, "status": "gap_through_without_observed_contact" if gap else "no_contact",
                "gap_through": gap}
    # Earlier compatible straddles do not prove a traded print. First actual
    # contact is no later than the first definite bar, or (conditionally on
    # any actual contact) the last compatible bar if there is no such proof.
    latest = definite if definite is not None else last
    later_hi = max([s.close[latest], *s.high[latest + 1:b]])
    later_lo = min([s.close[latest], *s.low[latest + 1:b]])
    possible_hi, possible_lo = max(s.high[contact:b]), min(s.low[contact:b])
    up_lo, up_hi = max(Fraction(0), later_hi - level), max(Fraction(0), possible_hi - level)
    down_lo, down_hi = max(Fraction(0), level - later_lo), max(Fraction(0), level - possible_lo)
    favorable, adverse = ((up_lo, up_hi), (down_lo, down_hi)) if side == 1 else ((down_lo, down_hi), (up_lo, up_hi))
    return {**base, "status": "definite_level_print" if definite is not None else "compatible_straddle_only",
            "contact_interval_start_ns": s.start[contact], "contact_interval_end_ns": s.end[contact],
            "first_definite_interval_start_ns": None if definite is None else s.start[definite],
            "first_definite_interval_end_ns": None if definite is None else s.end[definite],
            "first_actual_contact_lower_ns": s.start[contact],
            "first_actual_contact_upper_ns": s.end[latest],
            "gap_through": gap, "conditional_on_contact": definite is None,
            "favorable_lower_ticks": float(favorable[0]), "favorable_upper_ticks": float(favorable[1]),
            "adverse_lower_ticks": float(adverse[0]), "adverse_upper_ticks": float(adverse[1]),
            "terminal_from_level_ticks": float(side * (s.close[b - 1] - level)),
            "maturity_at_ns": window.available_at_ns}
