"""Cross-market alignment: parse, clocks, and causal state.

QuantPad t is bar-start milliseconds UTC. New-bar known_at is a labelled
model (bar end + 60/0/120s), not an observed receipt. Daily cash and
corporate actions stay date-only. This module does not fit Context or
evaluate Location/node quality.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from zoneinfo import ZoneInfo
import hashlib
import math

from trading_research.errors import ContractError, IntegrityError
from trading_research.foundations.cash_calendar import CashCalendar
from trading_research.foundations.time import MINUTE, NS, timestamp
from trading_research.operations.artifacts import digest
from trading_research.research.jumbo_tables import cash_dates
from trading_research.research.physical_ohlc_volatility import (
    ceil_to_minute,
    load_year_series,
    session_bounds,
)


VERSION = "cross-market-alignment-acquired-v1"
FAMILY = "Research-Cross-Market-Alignment-Descriptive-acquired-v1"
PROTOCOL_KIND = "cross_market_alignment_descriptive_contract_v1"
MS = 1_000_000
BAR_MS = 60_000
BAR_NS = MINUTE
MAX_SOURCE_AGE_NS = 120 * NS
LATENCY_AFTER_END_S = (60, 0, 120)
BASELINE_LATENCY_S = 60
LOOKBACKS = (1, 5, 15, 60)
REFERENCE_LOOKBACKS = (15, 60)
FUTURE_HORIZONS = (1, 5, 15, 30, 60)
GRID_MINUTES = 5
PRIOR_RELATIVE_DATES = 20
PIVOT_CONFIRM = 2
NY_ZONE = "America/New_York"
POPULATION_START = date(2020, 1, 1)
POPULATION_END_EXCLUSIVE = date(2026, 9, 4)
STAGES = (
    ("training", date(2020, 1, 1), date(2023, 1, 1)),
    ("development", date(2023, 1, 1), date(2025, 1, 1)),
    ("confirmation", date(2025, 1, 1), date(2026, 9, 4)),
)
SOURCE_ROOTS = ("NQ", "ES", "YM", "RTY", "QQQ", "SPY")
RECEIVERS = ("NQ", "ES")
DIRECTED_PAIRS = (
    ("NQ", "ES"), ("ES", "NQ"),
    ("YM", "NQ"), ("YM", "ES"),
    ("RTY", "NQ"), ("RTY", "ES"),
    ("QQQ", "NQ"), ("QQQ", "ES"),
    ("SPY", "NQ"), ("SPY", "ES"),
)
MAPPING_CHAINS = (("NQ", "QQQ"), ("ES", "SPY"))
FUTURES_ROOTS = frozenset({"NQ", "ES", "YM", "RTY"})
ETF_ROOTS = frozenset({"QQQ", "SPY"})
CANONICAL_ROOTS = frozenset({"NQ", "ES"})
QUARTER_POINT = 0.25
DATA_ROOT = Path("/workspace/data")
MINUTE_OHLC_NAMES = ("t", "o", "h", "l", "c", "v", "instrument_id")
QUALITY = (
    "ok", "nonfinite_price", "nonpositive_price", "invalid_enclosure",
    "nonfinite_volume", "nonpositive_volume", "invalid_instrument",
    "off_minute_grid", "invalid_source_minutes", "uncertified_definition",
)
QUALITY_CODE = {name: index for index, name in enumerate(QUALITY)}
JOIN_STATUS = ("fresh", "stale", "missing", "future_excluded")
INSTRUMENT_PROVIDER = "provider_id"
INSTRUMENT_CANONICAL = "canonical_contract_code"
CANONICAL_FILE_ID_BASE = 1000

_NP = None


def _np():
    global _NP
    if _NP is None:
        import numpy as np
        _NP = np
    return _NP


def _pa():
    import pyarrow as pa
    import pyarrow.parquet as pq
    return pa, pq


def stage_of(day: date) -> str | None:
    for name, start, end in STAGES:
        if start <= day < end:
            return name
    return None


def volume_unit_for(symbol: str) -> str:
    if symbol in ETF_ROOTS:
        return "shares"
    if symbol in FUTURES_ROOTS:
        return "contracts"
    raise ContractError("volume unit is defined only for acquired minute roots")


def native_unit_for(symbol: str) -> str:
    if symbol in ETF_ROOTS:
        return "USD_per_share"
    if symbol in FUTURES_ROOTS:
        return "index_points"
    raise ContractError("native unit is defined only for acquired minute roots")


def definition_certified(symbol: str) -> bool:
    return symbol in CANONICAL_ROOTS


def canonical_file_id(partition) -> int:
    root = {"NQ": 0, "ES": 1}.get(partition["root"])
    if root is None:
        raise ContractError("canonical file_id is defined only for NQ/ES")
    variant = 0 if partition["variant"] == "primary_corrected" else 1
    return CANONICAL_FILE_ID_BASE + (int(partition["year"]) - 2020) * 4 + root * 2 + variant


def bar_clocks(start_ms: int, *, latency_after_end_s: int = BASELINE_LATENCY_S) -> dict:
    if type(start_ms) is not int or not 0 <= start_ms < 2 ** 63:
        raise ContractError("bar start must be an int64 millisecond UTC timestamp")
    if type(latency_after_end_s) is not int or latency_after_end_s not in LATENCY_AFTER_END_S:
        raise ContractError("latency scenario must be one of 60, 0, 120 seconds after bar end")
    start_ns = start_ms * MS
    if start_ns >= 2 ** 63:
        raise ContractError("bar start nanoseconds exceed int64")
    end_ns = start_ns + BAR_NS
    if end_ns >= 2 ** 63:
        raise ContractError("bar end nanoseconds exceed int64")
    known_at_ns = scenario_known_at(end_ns, latency_after_end_s)
    return {
        "start_ms": start_ms,
        "start_ns": timestamp(start_ns),
        "end_ns": timestamp(end_ns),
        "known_at_ns": timestamp(known_at_ns),
        "latency_after_end_s": latency_after_end_s,
        "actual_received_at_ns": None,
        "basis": "historical_latency_assumption",
        "assumption_id": f"bar_end_plus_{latency_after_end_s}s_model",
        "off_minute_grid": start_ms % BAR_MS != 0,
    }


def scenario_known_at(end_ns: int, latency_after_end_s: int) -> int:
    if type(end_ns) is not int:
        raise ContractError("bar end must stay int64; scenarios recompute from the original end")
    if type(latency_after_end_s) is not int or latency_after_end_s not in LATENCY_AFTER_END_S:
        raise ContractError("latency scenario must be one of 60, 0, 120 seconds after bar end")
    known = end_ns + latency_after_end_s * NS
    if not -(2 ** 63) <= known < 2 ** 63:
        raise ContractError("scenario known_at is outside int64")
    return timestamp(known)


def scenario_known_ats(end_ns, latency_after_end_s: int):
    np = _np()
    ends = np.asarray(end_ns, dtype=np.int64)
    if latency_after_end_s not in LATENCY_AFTER_END_S:
        raise ContractError("latency scenario must be one of 60, 0, 120 seconds after bar end")
    return ends + np.int64(latency_after_end_s * NS)


def daily_observation_clock(observed_date) -> dict:
    day = observed_date if type(observed_date) is date else date.fromisoformat(str(observed_date)[:10])
    return {
        "observed_date": day.isoformat(),
        "known_at_ns": None,
        "verified_known_at_ns": None,
        "causal_feature_eligible": False,
        "clock": "date_only",
        "next_open_invented": False,
        "publication_invented": False,
        "actual_received_at_ns": None,
    }


def intended_cash_dates(calendar, first: date, last: date):
    last = min(last, POPULATION_END_EXCLUSIVE - timedelta(days=1))
    if last < first:
        return ()
    return cash_dates(calendar, first, last)


def year_date_bounds(year: int) -> tuple[date, date]:
    first = max(date(year, 1, 1), POPULATION_START)
    last = min(date(year, 12, 31), POPULATION_END_EXCLUSIVE - timedelta(days=1))
    return first, last


def load_cash_calendar(protocol) -> CashCalendar:
    spec = protocol["cash_calendar"]
    path = Path(spec["path"])
    payload = path.read_bytes()
    if spec.get("sha256") and hashlib.sha256(payload).hexdigest() != spec["sha256"]:
        raise IntegrityError("frozen cash calendar bytes changed")
    if spec.get("size_bytes") is not None and len(payload) != spec["size_bytes"]:
        raise IntegrityError("frozen cash calendar length changed")
    return CashCalendar(path)


def futures_session_bounds(cash, zone: str = NY_ZONE):
    return session_bounds(cash, "futures_wallclock_18_17", zone)


def grid_cuts(start_ns: int, end_ns: int, grid_minutes: int = GRID_MINUTES):
    np = _np()
    if type(start_ns) is not int or type(end_ns) is not int or end_ns <= start_ns:
        raise ContractError("grid requires a positive half-open session interval")
    step = int(grid_minutes) * MINUTE
    n = (end_ns - start_ns) // step
    return start_ns + np.arange(n, dtype=np.int64) * np.int64(step)


def session_label(cut_ns: int, cash, zone: str = NY_ZONE) -> str:
    if cash.state != "closed" and cash.open_at is not None and cash.close_at is not None:
        if cash.open_at <= cut_ns < cash.close_at:
            return "cash_rth"
    pre_start, pre_end, _ = session_bounds(cash, "pre_rth_06_0930", zone)
    if pre_start is not None and pre_start <= cut_ns < pre_end:
        return "pre_rth"
    return "other_futures"


def utc_datetime(ts_ns: int) -> datetime:
    timestamp(ts_ns)
    seconds, remainder = divmod(int(ts_ns), NS)
    return datetime(1970, 1, 1, tzinfo=timezone.utc) + timedelta(seconds=seconds, microseconds=remainder // 1000)


def ny_wall_minute(ts_ns: int, zone: str = NY_ZONE) -> int:
    local = utc_datetime(ts_ns).astimezone(ZoneInfo(zone))
    return local.hour * 60 + local.minute


def ny_civil_date(ts_ns: int, zone: str = NY_ZONE) -> date:
    return utc_datetime(ts_ns).astimezone(ZoneInfo(zone)).date()


def stages_aligned_for_ci(formation_ns, label_ns, maturity_ns, assigned_day: date, zone: str = NY_ZONE) -> bool:
    assigned = stage_of(assigned_day)
    if assigned is None or formation_ns is None or label_ns is None or maturity_ns is None:
        return False
    formation = stage_of(ny_civil_date(int(formation_ns), zone))
    label = stage_of(ny_civil_date(int(label_ns), zone))
    maturity = stage_of(ny_civil_date(int(maturity_ns), zone))
    return assigned == formation == label == maturity


def verify_source_bytes(path, *, sha256_hex: str, size_bytes: int, maximum_bytes: int) -> bytes:
    source = Path(path)
    if source.suffix != ".parquet":
        raise ContractError("minute/daily sources must be completed parquet")
    try:
        payload = source.read_bytes()
    except OSError as exc:
        raise IntegrityError("source file could not be read as one complete bounded object") from exc
    if type(size_bytes) is not int or len(payload) != size_bytes:
        raise IntegrityError("source size does not match the admitted length")
    if hashlib.sha256(payload).hexdigest() != sha256_hex:
        raise IntegrityError("source SHA-256 does not match the admitted hash")
    if len(payload) > maximum_bytes:
        raise IntegrityError("source exceeds the declared byte bound")
    return payload


def decode_parquet(payload: bytes):
    pa, pq = _pa()
    return pq.read_table(pa.BufferReader(payload))


def _as_int64(values, *, name: str):
    np = _np()
    if isinstance(values, np.ndarray) and values.dtype == np.int64:
        return values
    out = np.empty(len(values), dtype=np.int64)
    for index, value in enumerate(values):
        if isinstance(value, (bool, float)) or value is None:
            raise ContractError(f"{name} must remain int64; float timestamps are rejected")
        out[index] = int(value)
    return out


def _as_float64(values):
    np = _np()
    return np.asarray(values, dtype=np.float64)


def _price_reason(open_, high, low, close) -> str:
    values = (open_, high, low, close)
    if any(not math.isfinite(float(value)) for value in values):
        return "nonfinite_price"
    if any(not (value > 0.0) for value in values):
        return "nonpositive_price"
    if not (low <= min(open_, close) <= max(open_, close) <= high):
        return "invalid_enclosure"
    return "ok"


def parse_raw_minute_arrays(
    *,
    t_ms,
    open_,
    high,
    low,
    close,
    volume,
    instrument_id,
    symbol: str,
    file_id: int = 0,
    source_sha256: str = "0" * 64,
    variant: str = "primary_corrected",
    year: int | None = None,
    latency_after_end_s: int = BASELINE_LATENCY_S,
    native_unit: str | None = None,
):
    """Preserve native float prices and int timestamps. No quarter rounding."""
    np = _np()
    t_ms = _as_int64(t_ms, name="t")
    instrument_id = _as_int64(instrument_id, name="instrument_id")
    open_ = _as_float64(open_)
    high = _as_float64(high)
    low = _as_float64(low)
    close = _as_float64(close)
    volume = _as_float64(volume)
    n = int(t_ms.size)
    if not (open_.size == high.size == low.size == close.size == volume.size == instrument_id.size == n):
        raise ContractError("raw minute columns must be equal length")
    start_ns = t_ms * np.int64(MS)
    if np.any(start_ns < 0) or np.any(t_ms > (np.iinfo(np.int64).max // MS)):
        raise ContractError("bar start cannot be represented as int64 nanoseconds")
    end_ns = start_ns + np.int64(BAR_NS)
    known_at_ns = scenario_known_ats(end_ns, latency_after_end_s)
    reasons = np.empty(n, dtype=np.int8)
    valid = np.zeros(n, dtype=np.bool_)
    certified = definition_certified(symbol)
    for index in range(n):
        reason = _price_reason(float(open_[index]), float(high[index]), float(low[index]), float(close[index]))
        if reason == "ok":
            vol = float(volume[index])
            if not math.isfinite(vol):
                reason = "nonfinite_volume"
            elif vol <= 0.0:
                reason = "nonpositive_volume"
            elif int(instrument_id[index]) <= 0:
                reason = "invalid_instrument"
            elif int(t_ms[index]) % BAR_MS != 0:
                reason = "off_minute_grid"
        reasons[index] = QUALITY_CODE[reason]
        valid[index] = reason == "ok"
    if n > 1 and np.any(t_ms[1:] <= t_ms[:-1]):
        raise IntegrityError("raw minute timestamps must be strictly increasing")
    return UnitBars(
        symbol=symbol,
        variant=variant,
        year=year,
        file_id=int(file_id),
        source_sha256=source_sha256,
        native_unit=native_unit or native_unit_for(symbol),
        volume_unit=volume_unit_for(symbol),
        definition_certified=certified,
        instrument_kind=INSTRUMENT_PROVIDER,
        start_ns=start_ns,
        end_ns=end_ns,
        known_at_ns=known_at_ns,
        open=open_,
        high=high,
        low=low,
        close=close,
        volume=volume,
        instrument_id=instrument_id,
        valid=valid,
        quality_reason=reasons,
        source_version=digest({
            "symbol": symbol, "sha256": source_sha256, "file_id": int(file_id),
            "variant": variant, "latency": latency_after_end_s,
        }),
    )


def parse_raw_minute_table(table, **kwargs):
    names = tuple(table.schema.names)
    if not set(MINUTE_OHLC_NAMES) <= set(names):
        raise ContractError("raw minute table must contain t,o,h,l,c,v,instrument_id")
    return parse_raw_minute_arrays(
        t_ms=table["t"].to_numpy(zero_copy_only=False),
        open_=table["o"].to_numpy(zero_copy_only=False),
        high=table["h"].to_numpy(zero_copy_only=False),
        low=table["l"].to_numpy(zero_copy_only=False),
        close=table["c"].to_numpy(zero_copy_only=False),
        volume=table["v"].to_numpy(zero_copy_only=False),
        instrument_id=table["instrument_id"].to_numpy(zero_copy_only=False),
        **kwargs,
    )


def validate_canonical_baseline(end_ns, known_at_ns):
    np = _np()
    expected = np.asarray(end_ns, dtype=np.int64) + np.int64(BASELINE_LATENCY_S * NS)
    if not np.array_equal(np.asarray(known_at_ns, dtype=np.int64), expected):
        raise IntegrityError("canonical baseline known_at is not bar end + 60s")


def unit_from_canonical(series, cols, *, symbol: str, variant: str, year: int,
                        source_sha256: str, source_version: str, file_id: int):
    np = _np()
    n = int(cols["start"].size)
    invalid = np.asarray(cols["invalid"], dtype=np.bool_)
    reasons = np.where(invalid, QUALITY_CODE["invalid_source_minutes"], QUALITY_CODE["ok"]).astype(np.int8)
    end_ns = np.asarray(cols["end"], dtype=np.int64)
    known_at_ns = np.asarray(cols["known"], dtype=np.int64)
    validate_canonical_baseline(end_ns, known_at_ns)
    names = tuple(cols.get("contract_names") or series.contract_names)
    return UnitBars(
        symbol=symbol,
        variant=variant,
        year=int(year),
        file_id=int(file_id),
        source_sha256=source_sha256,
        native_unit="index_points",
        volume_unit="contracts",
        definition_certified=True,
        instrument_kind=INSTRUMENT_CANONICAL,
        start_ns=np.asarray(cols["start"], dtype=np.int64),
        end_ns=end_ns,
        known_at_ns=known_at_ns,
        open=np.asarray(cols["open"], dtype=np.float64) * QUARTER_POINT,
        high=np.asarray(cols["high"], dtype=np.float64) * QUARTER_POINT,
        low=np.asarray(cols["low"], dtype=np.float64) * QUARTER_POINT,
        close=np.asarray(cols["close"], dtype=np.float64) * QUARTER_POINT,
        volume=np.frombuffer(series.volume, dtype=np.int64, count=n).astype(np.float64),
        instrument_id=np.asarray(cols["contract"], dtype=np.int64),
        valid=~invalid,
        quality_reason=reasons,
        source_version=source_version,
        contract_names=names,
    )


def load_canonical_unit(store, partition):
    series, cols, source_version = load_year_series(store, partition)
    return unit_from_canonical(
        series, cols,
        symbol=partition["root"],
        variant=partition["variant"],
        year=int(partition["year"]),
        source_sha256=partition["source_sha256"],
        source_version=source_version,
        file_id=canonical_file_id(partition),
    )


def contract_key_array(unit: "UnitBars"):
    np = _np()
    if unit._contract_keys is not None:
        return unit._contract_keys
    n = len(unit)
    if unit.instrument_kind == INSTRUMENT_CANONICAL and unit.contract_names:
        names = np.asarray(unit.contract_names, dtype=object)
        codes = np.asarray(unit.instrument_id, dtype=np.int64)
        out = np.empty(n, dtype=object)
        ok = (codes >= 0) & (codes < names.size)
        out[:] = None
        if np.any(ok):
            out[ok] = names[codes[ok]]
        unit._contract_keys = out
        return out
    prefix = unit.symbol + ":"
    codes, inverse = np.unique(unit.instrument_id, return_inverse=True)
    names = np.asarray([prefix + str(int(code)) for code in codes], dtype=object)
    unit._contract_keys = names[inverse]
    return unit._contract_keys


def same_contract_key(left, right) -> bool:
    return left is not None and right is not None and left == right


@dataclass
class UnitBars:
    symbol: str
    variant: str
    year: int | None
    file_id: int
    source_sha256: str
    native_unit: str
    volume_unit: str
    definition_certified: bool
    start_ns: object
    end_ns: object
    known_at_ns: object
    open: object
    high: object
    low: object
    close: object
    volume: object
    instrument_id: object
    valid: object
    quality_reason: object
    source_version: str
    instrument_kind: str = INSTRUMENT_PROVIDER
    contract_names: tuple = ()
    _clocks: dict | None = field(default=None, repr=False, compare=False)
    _contract_keys: object = field(default=None, repr=False, compare=False)

    def __len__(self):
        return int(self.start_ns.size)

    def ensure_clocks(self):
        if self._clocks is None:
            np = _np()
            end = np.asarray(self.end_ns, dtype=np.int64)
            baseline = np.asarray(self.known_at_ns, dtype=np.int64)
            if self.definition_certified:
                validate_canonical_baseline(end, baseline)
            self._clocks = {
                60: baseline,
                0: end,
                120: end + np.int64(120 * NS),
            }
        return self._clocks

    def known_for(self, latency_after_end_s: int):
        return self.ensure_clocks()[latency_after_end_s]

    def slice_session(self, start_ns: int, end_ns: int):
        np = _np()
        lo = int(np.searchsorted(self.start_ns, start_ns, side="left"))
        hi = int(np.searchsorted(self.start_ns, end_ns, side="left"))
        return lo, hi


def run_length_and_id(start_ns, instrument_id, valid):
    np = _np()
    n = int(start_ns.size)
    run = np.zeros(n, dtype=np.int32)
    run_id = np.full(n, -1, dtype=np.int32)
    if n == 0:
        return run, run_id
    current = 0
    if valid[0]:
        run[0] = 1
        run_id[0] = 0
    for index in range(1, n):
        cont = (valid[index] and valid[index - 1]
                and instrument_id[index] == instrument_id[index - 1]
                and start_ns[index] == start_ns[index - 1] + BAR_NS)
        if cont:
            run[index] = run[index - 1] + 1
            run_id[index] = run_id[index - 1]
        elif valid[index]:
            current += 1
            run[index] = 1
            run_id[index] = current
    return run, run_id


def run_length(start_ns, instrument_id, valid):
    return run_length_and_id(start_ns, instrument_id, valid)[0]


def backward_join_indices(known_at, cut_ns, bar_end, *, max_age_ns: int = MAX_SOURCE_AGE_NS):
    """Last bar with known_at<=cut. Future-nearest and equal-future matches excluded."""
    np = _np()
    known = np.asarray(known_at, dtype=np.int64)
    ends = np.asarray(bar_end, dtype=np.int64)
    cuts = np.asarray(cut_ns, dtype=np.int64)
    if cuts.ndim == 0:
        cuts = cuts.reshape(1)
        scalar = True
    else:
        scalar = False
    index = np.searchsorted(known, cuts, side="right") - 1
    status = np.empty(cuts.size, dtype=np.int8)
    missing = index < 0
    status[missing] = 2
    usable = ~missing
    if np.any(usable):
        chosen = index[usable]
        future = known[chosen] > cuts[usable]
        status_view = status[usable]
        status_view[future] = 3
        index[np.flatnonzero(usable)[future]] = -1
        usable = (~missing) & (index >= 0)
    if np.any(usable):
        chosen = index[usable]
        age = cuts[usable] - ends[chosen]
        stale = age > np.int64(max_age_ns)
        status[np.flatnonzero(usable)[stale]] = 1
        status[np.flatnonzero(usable)[~stale]] = 0
        negative = age < 0
        if np.any(negative):
            status[np.flatnonzero(usable)[negative]] = 3
            index[np.flatnonzero(usable)[negative]] = -1
    if scalar:
        return int(index[0]), int(status[0])
    return index, status


def join_status_name(code: int) -> str:
    if 0 <= code < len(JOIN_STATUS):
        return JOIN_STATUS[code]
    return "undefined"


def last_available(unit: UnitBars, cut_ns: int, *, latency_after_end_s: int = BASELINE_LATENCY_S,
                   max_age_ns: int = MAX_SOURCE_AGE_NS):
    known = unit.known_for(latency_after_end_s)
    index, status = backward_join_indices(known, cut_ns, unit.end_ns, max_age_ns=max_age_ns)
    if index < 0:
        return None, join_status_name(status)
    return int(index), join_status_name(status)


def priced_ok(unit: UnitBars, index, status: str) -> bool:
    if index is None or status != "fresh":
        return False
    return bool(unit.valid[index] and unit.close[index] > 0.0 and math.isfinite(float(unit.close[index])))


def close_to_close_logreturn(close, start_ns, instrument_id, valid, lookback: int, run=None):
    np = _np()
    n = int(close.size)
    out = np.full(n, np.nan, dtype=np.float64)
    defined = np.zeros(n, dtype=np.bool_)
    if lookback < 1 or n <= lookback:
        return out, defined
    if run is None:
        run = run_length(start_ns, instrument_id, valid)
    need = lookback + 1
    ok = run >= need
    if not np.any(ok):
        return out, defined
    idx = np.flatnonzero(ok)
    prior = close[idx - lookback]
    current = close[idx]
    good = (prior > 0.0) & (current > 0.0) & np.isfinite(prior) & np.isfinite(current)
    idx = idx[good]
    out[idx] = np.log(current[good] / prior[good])
    defined[idx] = True
    return out, defined


def lookback_extrema(high, low, start_ns, instrument_id, valid, lookback: int, run=None):
    np = _np()
    n = int(high.size)
    hi = np.full(n, np.nan, dtype=np.float64)
    lo = np.full(n, np.nan, dtype=np.float64)
    defined = np.zeros(n, dtype=np.bool_)
    if lookback < 1 or n < lookback:
        return hi, lo, defined
    if run is None:
        run = run_length(start_ns, instrument_id, valid)
    ok = run >= (lookback + 1)
    windows_h = np.lib.stride_tricks.sliding_window_view(high, lookback)
    windows_l = np.lib.stride_tricks.sliding_window_view(low, lookback)
    starts = np.arange(lookback, n, dtype=np.int64)
    take = ok[starts]
    if np.any(take):
        at = starts[take]
        hi[at] = windows_h.max(axis=1)[at - lookback + 1]
        lo[at] = windows_l.min(axis=1)[at - lookback + 1]
        defined[at] = True
    return hi, lo, defined


def running_references(high, low, start_ns, instrument_id, valid, lookback: int, run=None):
    """Past lookback extrema excluding the current bar."""
    np = _np()
    n = int(high.size)
    prior_high = np.full(n, np.nan, dtype=np.float64)
    prior_low = np.full(n, np.nan, dtype=np.float64)
    defined = np.zeros(n, dtype=np.bool_)
    if lookback < 1 or n <= lookback:
        return prior_high, prior_low, defined
    if run is None:
        run = run_length(start_ns, instrument_id, valid)
    ok = run >= (lookback + 1)
    if not np.any(ok):
        return prior_high, prior_low, defined
    windows = np.lib.stride_tricks.sliding_window_view(high, lookback)
    low_windows = np.lib.stride_tricks.sliding_window_view(low, lookback)
    prior_high[lookback:] = windows.max(axis=1)[: n - lookback]
    prior_low[lookback:] = low_windows.min(axis=1)[: n - lookback]
    prior_high[~ok] = np.nan
    prior_low[~ok] = np.nan
    defined[ok] = True
    return prior_high, prior_low, defined


def running_breaches(high, low, prior_high, prior_low, defined):
    np = _np()
    high_breach = defined & np.isfinite(prior_high) & (high > prior_high)
    low_breach = defined & np.isfinite(prior_low) & (low < prior_low)
    return high_breach, low_breach


def confirmed_pivots(high, low, start_ns, instrument_id, valid, known_at=None, *,
                     confirm: int = PIVOT_CONFIRM, end_ns=None, contract_key=None):
    """Strict 2+2 pivots. Reset on contract change, gap, or invalid. Known from right-2 end."""
    np = _np()
    n = int(high.size)
    high_level = np.full(n, np.nan, dtype=np.float64)
    low_level = np.full(n, np.nan, dtype=np.float64)
    high_formed = np.full(n, -1, dtype=np.int64)
    low_formed = np.full(n, -1, dtype=np.int64)
    high_known = np.full(n, -1, dtype=np.int64)
    low_known = np.full(n, -1, dtype=np.int64)
    high_known_end = np.full(n, -1, dtype=np.int64)
    low_known_end = np.full(n, -1, dtype=np.int64)
    high_breach = np.zeros(n, dtype=np.bool_)
    low_breach = np.zeros(n, dtype=np.bool_)
    high_anchor = np.full(n, -1, dtype=np.int64)
    low_anchor = np.full(n, -1, dtype=np.int64)
    empty = {
        "high_level": high_level, "low_level": low_level,
        "high_formed_ns": high_formed, "low_formed_ns": low_formed,
        "high_known_ns": high_known, "low_known_ns": low_known,
        "high_known_end_ns": high_known_end, "low_known_end_ns": low_known_end,
        "high_breach": high_breach, "low_breach": low_breach,
        "high_anchor_contract": np.empty(n, dtype=object),
        "low_anchor_contract": np.empty(n, dtype=object),
        "high_center": high_anchor, "low_center": low_anchor,
    }
    empty["high_anchor_contract"][:] = None
    empty["low_anchor_contract"][:] = None
    if n < 2 * confirm + 1:
        return empty
    if end_ns is None:
        if known_at is None:
            raise ContractError("confirmed pivots need end_ns or baseline known_at")
        end_ns = np.asarray(known_at, dtype=np.int64) - np.int64(BASELINE_LATENCY_S * NS)
    else:
        end_ns = np.asarray(end_ns, dtype=np.int64)
    run = run_length(start_ns, instrument_id, valid)
    keys = contract_key if contract_key is not None else instrument_id
    active_high = None
    active_low = None
    emitted_high = False
    emitted_low = False
    width = 2 * confirm + 1
    for index in range(n):
        broken = (
            index > 0 and (
                not bool(valid[index]) or not bool(valid[index - 1])
                or instrument_id[index] != instrument_id[index - 1]
                or start_ns[index] != start_ns[index - 1] + BAR_NS
            )
        )
        if broken:
            active_high = None
            active_low = None
            emitted_high = False
            emitted_low = False
        center = index - confirm
        if center >= confirm and int(run[index]) >= width and bool(valid[index]) and not broken:
            left = slice(center - confirm, center)
            right = slice(center + 1, center + confirm + 1)
            is_high = bool(np.all(high[center] > high[left]) and np.all(high[center] > high[right]))
            is_low = bool(np.all(low[center] < low[left]) and np.all(low[center] < low[right]))
            confirm_end = int(end_ns[index])
            if is_high:
                active_high = (center, float(high[center]), int(start_ns[center]), confirm_end, keys[center], index)
                emitted_high = False
            if is_low:
                active_low = (center, float(low[center]), int(start_ns[center]), confirm_end, keys[center], index)
                emitted_low = False
        if active_high is not None and index >= active_high[5]:
            high_level[index] = active_high[1]
            high_formed[index] = active_high[2]
            high_known_end[index] = active_high[3]
            high_known[index] = active_high[3] + BASELINE_LATENCY_S * NS
            empty["high_anchor_contract"][index] = active_high[4]
            high_anchor[index] = active_high[0]
            if (not emitted_high and index > active_high[0] + confirm
                    and valid[index] and keys[index] == active_high[4]
                    and high[index] > active_high[1]):
                high_breach[index] = True
                emitted_high = True
        if active_low is not None and index >= active_low[5]:
            low_level[index] = active_low[1]
            low_formed[index] = active_low[2]
            low_known_end[index] = active_low[3]
            low_known[index] = active_low[3] + BASELINE_LATENCY_S * NS
            empty["low_anchor_contract"][index] = active_low[4]
            low_anchor[index] = active_low[0]
            if (not emitted_low and index > active_low[0] + confirm
                    and valid[index] and keys[index] == active_low[4]
                    and low[index] < active_low[1]):
                low_breach[index] = True
                emitted_low = True
    return empty


def pivot_scenario_known(known_end_ns: int, latency_after_end_s: int) -> int | None:
    if known_end_ns is None or int(known_end_ns) < 0:
        return None
    return scenario_known_at(int(known_end_ns), latency_after_end_s)


def contemporaneous_ratio(receiver_close, source_close):
    if receiver_close is None or source_close is None:
        return None
    if not (receiver_close > 0.0 and source_close > 0.0):
        return None
    if not (math.isfinite(receiver_close) and math.isfinite(source_close)):
        return None
    ratio = receiver_close / source_close
    return {
        "ratio": ratio,
        "inverse": source_close / receiver_close,
        "units": "points_per_USD",
        "inverse_units": "USD_per_point",
        "zero_residual_is_not_validation": True,
    }


def lagged_mapping_residual(*, prior_receiver_close, prior_source_close,
                            current_source, current_receiver):
    if any(value is None for value in (prior_receiver_close, prior_source_close, current_source, current_receiver)):
        return {
            "ratio": None, "predicted_receiver": None, "residual_receiver_points": None,
            "status": "undefined", "reason": "previous_or_current_missing",
        }
    if not (prior_receiver_close > 0.0 and prior_source_close > 0.0 and current_source > 0.0):
        return {
            "ratio": None, "predicted_receiver": None, "residual_receiver_points": None,
            "status": "undefined", "reason": "nonpositive_close",
        }
    ratio = prior_receiver_close / prior_source_close
    predicted = ratio * current_source
    residual = current_receiver - predicted
    return {
        "ratio": ratio,
        "predicted_receiver": predicted,
        "residual_receiver_points": residual,
        "status": "defined",
        "reason": None,
        "units": "receiver_points",
        "prior_ratio_frozen": True,
    }


def previous_intended_date(dates, day: date):
    prior = None
    for item in dates:
        current = item.day if hasattr(item, "day") else item
        if current >= day:
            break
        prior = current
    return prior


def last_simultaneous_same_end(source: UnitBars, receiver: UnitBars, cash_close_ns: int,
                               *, latency_after_end_s: int = BASELINE_LATENCY_S):
    """Last shared bar-end <= cash close whose scenario known_at is <= cash_close+lag."""
    np = _np()
    known_cut = int(cash_close_ns) + int(latency_after_end_s) * NS
    src_end = np.asarray(source.end_ns, dtype=np.int64)
    rcv_end = np.asarray(receiver.end_ns, dtype=np.int64)
    src_known = source.known_for(latency_after_end_s)
    rcv_known = receiver.known_for(latency_after_end_s)
    i = int(np.searchsorted(src_end, int(cash_close_ns), side="right")) - 1
    j = int(np.searchsorted(rcv_end, int(cash_close_ns), side="right")) - 1
    src_keys = contract_key_array(source)
    rcv_keys = contract_key_array(receiver)
    lower_end = int(cash_close_ns) - MAX_SOURCE_AGE_NS
    while i >= 0 and j >= 0:
        if int(src_end[i]) < lower_end or int(rcv_end[j]) < lower_end:
            break
        se = int(src_end[i])
        re = int(rcv_end[j])
        if se == re:
            if (int(src_known[i]) <= known_cut and int(rcv_known[j]) <= known_cut
                    and source.valid[i] and receiver.valid[j]
                    and source.close[i] > 0.0 and receiver.close[j] > 0.0):
                return {
                    "source_index": i,
                    "receiver_index": j,
                    "source_close": float(source.close[i]),
                    "receiver_close": float(receiver.close[j]),
                    "source_instrument": int(source.instrument_id[i]),
                    "receiver_instrument": int(receiver.instrument_id[j]),
                    "source_contract_key": src_keys[i],
                    "receiver_contract_key": rcv_keys[j],
                    "source_version": source.source_version,
                    "receiver_version": receiver.source_version,
                    "bar_end_ns": se,
                    "lag_s": latency_after_end_s,
                    "cut_ns": known_cut,
                }
            i -= 1
            j -= 1
        elif se > re:
            i -= 1
        else:
            j -= 1
    return None


def last_simultaneous_close(source: UnitBars, receiver: UnitBars, cut_ns: int,
                            *, latency_after_end_s: int = BASELINE_LATENCY_S):
    return last_simultaneous_same_end(source, receiver, cut_ns, latency_after_end_s=latency_after_end_s)


def freeze_previous_closing_ratio(source: UnitBars, receiver: UnitBars, cash,
                                  *, latency_after_end_s: int = BASELINE_LATENCY_S):
    if cash.state == "closed" or cash.close_at is None:
        return None
    row = last_simultaneous_same_end(
        source, receiver, int(cash.close_at), latency_after_end_s=latency_after_end_s)
    if row is None or row["bar_end_ns"] < int(cash.open_at):
        return None
    return {
        "ratio": row["receiver_close"] / row["source_close"],
        "source_close": row["source_close"],
        "receiver_close": row["receiver_close"],
        "source_instrument": row["source_instrument"],
        "receiver_instrument": row["receiver_instrument"],
        "source_contract_key": row["source_contract_key"],
        "receiver_contract_key": row["receiver_contract_key"],
        "source_version": row["source_version"],
        "receiver_version": row["receiver_version"],
        "cut_ns": row["cut_ns"],
        "bar_end_ns": row["bar_end_ns"],
        "lag_s": latency_after_end_s,
        "date": cash.day.isoformat(),
        "day": cash.day,
    }


@dataclass
class PriorCarry:
    by_date: dict = field(default_factory=dict)
    dates: list = field(default_factory=list)
    history: list = field(default_factory=list)

    def relative_volume(self, wall_minute: int, current_volume: float, prior_intended=None):
        if prior_intended is None:
            if len(self.history) < PRIOR_RELATIVE_DATES:
                return None, "insufficient_prior_dates"
            snapshots = self.history[-PRIOR_RELATIVE_DATES:]
        else:
            if len(prior_intended) < PRIOR_RELATIVE_DATES:
                return None, "insufficient_prior_dates"
            snapshots = []
            for day in prior_intended[-PRIOR_RELATIVE_DATES:]:
                bucket = self.by_date.get(day)
                if bucket is None:
                    return None, "missing_prior_date"
                snapshots.append(bucket)
        values = []
        for bucket in snapshots:
            value = bucket["volumes"].get(wall_minute)
            if value is None:
                return None, "missing_prior_minute"
            values.append(value)
        mean = math.fsum(values) / float(PRIOR_RELATIVE_DATES)
        if mean <= 0.0:
            return None, "nonpositive_prior_mean"
        return current_volume / mean, None

    def prior_rth_scale(self, current_contract_key=None, prior_intended=None):
        days = self.dates if prior_intended is None else prior_intended[-1:]
        for day in reversed(days):
            row = self.by_date.get(day)
            if row is None or not row["rth_complete"] or row["rth_sqrt_rv"] is None:
                if prior_intended is not None:
                    return None
                continue
            if current_contract_key is not None and row.get("contract_key") != current_contract_key:
                return None
            return row["rth_sqrt_rv"]
        return None

    def push_day(self, day: date, volumes: dict, rth_sqrt_rv, rth_complete: bool, contract_key=None):
        row = {
            "volumes": dict(volumes),
            "rth_sqrt_rv": rth_sqrt_rv,
            "rth_complete": bool(rth_complete),
            "contract_key": contract_key,
        }
        self.by_date[day] = row
        self.dates.append(day)
        self.history.append(row)


def relative_volume_for_bar(carry: PriorCarry, start_ns: int, volume: float, zone: str = NY_ZONE,
                            prior_intended=None):
    return carry.relative_volume(ny_wall_minute(int(start_ns), zone), float(volume), prior_intended)


def economic_minute_volumes(unit: UnitBars, start_ns: int, end_ns: int, zone: str = NY_ZONE):
    lo, hi = unit.slice_session(start_ns, end_ns)
    volumes = {}
    for index in range(lo, hi):
        if not unit.valid[index]:
            continue
        volumes[ny_wall_minute(int(unit.start_ns[index]), zone)] = float(unit.volume[index])
    return volumes


def session_log_rv(close, start_ns, instrument_id, valid, start, end, *,
                   run=None, defined_1=None, prefix_sq=None, contract_key=None):
    np = _np()
    if defined_1 is None or prefix_sq is None:
        rets, defined_1 = close_to_close_logreturn(close, start_ns, instrument_id, valid, 1, run=run)
        prefix_sq = np.zeros(int(close.size) + 1, dtype=np.float64)
        prefix_sq[1:] = np.cumsum(np.where(defined_1, rets * rets, 0.0))
    lo = int(np.searchsorted(start_ns, start, side="left"))
    hi = int(np.searchsorted(start_ns, end, side="left"))
    if hi <= lo:
        return None, False
    expected = (end - start) // BAR_NS
    if (hi - lo) != expected or not bool(np.all(valid[lo:hi])):
        return None, False
    if hi - lo > 1 and not bool(np.all(start_ns[lo + 1:hi] == start_ns[lo:hi - 1] + BAR_NS)):
        return None, False
    if contract_key is not None and hi > lo and not all(contract_key[i] == contract_key[lo] for i in range(lo, hi)):
        return None, False
    if hi - lo > 1 and not bool(np.all(defined_1[lo + 1:hi])):
        return None, False
    total = float(prefix_sq[hi] - prefix_sq[lo + 1]) if hi > lo + 1 else 0.0
    if hi <= lo + 1:
        return None, False
    return float(math.sqrt(total)), True


def precompute_future_windows(unit: UnitBars, run, contract_key, horizons=FUTURE_HORIZONS):
    np = _np()
    n = len(unit)
    out = {}
    start = np.asarray(unit.start_ns, dtype=np.int64)
    for horizon in horizons:
        complete = np.zeros(n, dtype=np.bool_)
        high = np.full(n, np.nan, dtype=np.float64)
        low = np.full(n, np.nan, dtype=np.float64)
        close = np.full(n, np.nan, dtype=np.float64)
        open_ = np.full(n, np.nan, dtype=np.float64)
        status = np.full(n, 2, dtype=np.int8)
        if n >= horizon:
            ends = np.arange(n - horizon + 1, dtype=np.int64)
            tiled = (
                (run[ends + horizon - 1] >= horizon)
                & (start[ends + horizon - 1] == start[ends] + np.int64((horizon - 1) * MINUTE))
                & (unit.instrument_id[ends + horizon - 1] == unit.instrument_id[ends])
                & unit.valid[ends]
            )
            complete[ends] = tiled
            windows_h = np.lib.stride_tricks.sliding_window_view(unit.high, horizon)
            windows_l = np.lib.stride_tricks.sliding_window_view(unit.low, horizon)
            high[ends] = np.where(tiled, windows_h.max(axis=1), np.nan)
            low[ends] = np.where(tiled, windows_l.min(axis=1), np.nan)
            close[ends] = np.where(tiled, unit.close[ends + horizon - 1], np.nan)
            open_[ends] = np.where(tiled, unit.open[ends], np.nan)
            status[ends] = np.where(tiled, 0, 2)
            rolls = (unit.instrument_id[ends + horizon - 1] != unit.instrument_id[ends])
            status[ends[rolls]] = 3
        out[horizon] = {
            "complete": complete, "high": high, "low": low, "close": close, "open": open_,
            "status": status, "contract_key": contract_key,
        }
    return out


def lookup_future_window(unit: UnitBars, futures, label_start_ns: int, horizon: int,
                         reference_contract_key=None):
    np = _np()
    start = np.asarray(unit.start_ns, dtype=np.int64)
    index = int(np.searchsorted(start, int(label_start_ns), side="left"))
    payload = futures[horizon]
    if index >= start.size or int(start[index]) != int(label_start_ns):
        return {
            "status": "no_receiver", "reasons": ("missing_first_minute",),
            "open": None, "high": None, "low": None, "close": None, "count": 0,
            "instrument_id": None, "contract_key": None, "index": None,
        }
    if reference_contract_key is not None and payload["contract_key"][index] != reference_contract_key:
        return {
            "status": "roll", "reasons": ("reference_contract_mismatch",),
            "open": None, "high": None, "low": None, "close": None,
            "count": horizon, "instrument_id": int(unit.instrument_id[index]),
            "contract_key": payload["contract_key"][index], "index": index,
        }
    if payload["complete"][index]:
        return {
            "status": "complete", "reasons": (),
            "open": float(payload["open"][index]),
            "high": float(payload["high"][index]),
            "low": float(payload["low"][index]),
            "close": float(payload["close"][index]),
            "count": horizon, "instrument_id": int(unit.instrument_id[index]),
            "contract_key": payload["contract_key"][index], "index": index,
        }
    code = int(payload["status"][index])
    status = {1: "no_receiver", 2: "censored", 3: "roll"}.get(code, "censored")
    reasons = ("raw_contract_transition",) if status == "roll" else (
        ("missing_all_minutes",) if status == "no_receiver" else ("incomplete_future",))
    return {
        "status": status, "reasons": reasons,
        "open": None, "high": None, "low": None, "close": None,
        "count": horizon, "instrument_id": int(unit.instrument_id[index]),
        "contract_key": payload["contract_key"][index], "index": index,
    }


@dataclass
class PreparedUnit:
    unit: UnitBars
    run: object
    run_id: object
    contract_key: object
    logret: dict
    intervening: dict
    running: dict
    pivot: dict
    futures: dict
    prefix_sq: object
    defined_1: object


def prepare_unit(unit: UnitBars) -> PreparedUnit:
    unit.ensure_clocks()
    run, run_id = run_length_and_id(unit.start_ns, unit.instrument_id, unit.valid)
    keys = contract_key_array(unit)
    logret = {}
    intervening = {}
    for length in LOOKBACKS:
        logret[length] = close_to_close_logreturn(
            unit.close, unit.start_ns, unit.instrument_id, unit.valid, length, run=run)
        intervening[length] = lookback_extrema(
            unit.high, unit.low, unit.start_ns, unit.instrument_id, unit.valid, length, run=run)
    running = {}
    for length in REFERENCE_LOOKBACKS:
        prior_high, prior_low, defined = running_references(
            unit.high, unit.low, unit.start_ns, unit.instrument_id, unit.valid, length, run=run)
        high_b, low_b = running_breaches(unit.high, unit.low, prior_high, prior_low, defined)
        running[length] = {
            "prior_high": prior_high, "prior_low": prior_low, "defined": defined,
            "high_breach": high_b, "low_breach": low_b,
        }
    pivot = confirmed_pivots(
        unit.high, unit.low, unit.start_ns, unit.instrument_id, unit.valid,
        end_ns=unit.end_ns, contract_key=keys)
    futures = precompute_future_windows(unit, run, keys)
    ret1, defined_1 = logret[1]
    np = _np()
    prefix_sq = np.zeros(len(unit) + 1, dtype=np.float64)
    prefix_sq[1:] = np.cumsum(np.where(defined_1, ret1 * ret1, 0.0))
    return PreparedUnit(
        unit=unit, run=run, run_id=run_id, contract_key=keys, logret=logret,
        intervening=intervening, running=running, pivot=pivot, futures=futures,
        prefix_sq=prefix_sq, defined_1=defined_1,
    )


def _as_date(value):
    if hasattr(value, "as_py"):
        value = value.as_py()
    if type(value) is date:
        return value
    return date.fromisoformat(str(value)[:10])


def parse_daily_cash_table(table, *, symbol: str, file_id: int, source_sha256: str,
                           intended_dates=None):
    dates = [_as_date(day) for day in table["date"].to_pylist()]
    intended_index = {}
    if intended_dates is not None:
        intended_index = {item: index for index, item in enumerate(intended_dates)}
    seen = set()
    rows = []
    previous_close = previous_adj = None
    previous_date = None
    date_order_ok = True
    for index, day in enumerate(dates):
        duplicate = day in seen
        seen.add(day)
        if previous_date is not None and day <= previous_date:
            date_order_ok = False
        close = table["close"][index].as_py()
        adj = table["adjusted_close"][index].as_py() if "adjusted_close" in table.column_names else None
        raw = adjusted = None
        gap_not_compressed = False
        adjacent = False
        if previous_date is not None:
            if intended_index:
                left = intended_index.get(previous_date)
                right = intended_index.get(day)
                adjacent = left is not None and right is not None and right == left + 1
            else:
                adjacent = (day - previous_date).days == 1
            if not adjacent:
                gap_not_compressed = True
        if adjacent and previous_close and close and previous_close > 0 and close > 0:
            raw = math.log(close / previous_close)
        if adjacent and previous_adj and adj and previous_adj > 0 and adj > 0:
            adjusted = math.log(adj / previous_adj)
        in_cohort = POPULATION_START <= day < POPULATION_END_EXCLUSIVE
        clock = daily_observation_clock(day)
        rows.append({
            "date": day.isoformat(),
            "symbol": symbol,
            "open": table["open"][index].as_py() if "open" in table.column_names else None,
            "high": table["high"][index].as_py() if "high" in table.column_names else None,
            "low": table["low"][index].as_py() if "low" in table.column_names else None,
            "close": close,
            "adjusted_close": adj,
            "volume": table["volume"][index].as_py() if "volume" in table.column_names else None,
            "raw_log_return": raw,
            "adjusted_log_return": adjusted,
            "in_primary_cohort": in_cohort,
            "cohort": "primary" if in_cohort else "outside_primary",
            "file_id": file_id,
            "source_sha256": source_sha256,
            "date_order_ok": date_order_ok and not duplicate,
            "duplicate": duplicate,
            "gap_not_compressed": gap_not_compressed,
            "adjacent_intended": adjacent,
            **clock,
        })
        previous_close, previous_adj, previous_date = close, adj, day
    return rows


def parse_corporate_actions_table(table, *, symbol: str, file_id: int, source_sha256: str):
    rows = []
    dates = table["ex_date"].to_pylist() if "ex_date" in table.column_names else []
    seen = set()
    previous = None
    date_order_ok = True
    for index, day in enumerate(dates):
        day = _as_date(day)
        duplicate = day in seen
        seen.add(day)
        if previous is not None and day < previous:
            date_order_ok = False
        dividend = table["dividend"][index].as_py() if "dividend" in table.column_names else None
        split = table["split_ratio"][index].as_py() if "split_ratio" in table.column_names else None
        labels = []
        if dividend not in (None, 0, 0.0):
            labels.append("dividend")
        if split not in (None, 0, 0.0, 1, 1.0):
            labels.append("split")
        clock = daily_observation_clock(day)
        rows.append({
            "date": day.isoformat(),
            "symbol": symbol,
            "ex_date": day.isoformat(),
            "dividend": dividend,
            "split_ratio": split,
            "action_labels": "|".join(labels) if labels else "none",
            "action_date_is_not_publication": True,
            "file_id": file_id,
            "source_sha256": source_sha256,
            "in_primary_cohort": POPULATION_START <= day < POPULATION_END_EXCLUSIVE,
            "date_order_ok": date_order_ok and not duplicate,
            "duplicate": duplicate,
            **clock,
        })
        previous = day
    return rows


def admitted_minute_sources(admitted, *, years: list[int] | None):
    rows = []
    for item in admitted["sources"]:
        source = item["source"]
        if source.get("role") != "minute_ohlcv":
            continue
        year = source.get("year")
        if years is not None and year not in years:
            continue
        rows.append(item)
    return rows


def admitted_daily_sources(admitted):
    return [item for item in admitted["sources"] if item["source"].get("role") in ("daily_cash", "corporate_actions")]


def selected_year_list(selected_years) -> list[int]:
    if selected_years is None:
        return list(range(POPULATION_START.year, POPULATION_END_EXCLUSIVE.year + 1))
    if not isinstance(selected_years, list) or not selected_years:
        raise ContractError("selected_years must be None or a nonempty list of calendar years")
    return [int(year) for year in selected_years]


def canonical_partitions_for_year(protocol, year: int):
    rows = []
    for partition in protocol.get("canonical_partitions") or ():
        if int(partition["year"]) == int(year):
            rows.append(partition)
    return rows


def load_raw_unit(item, *, maximum_bytes: int, latency_after_end_s: int = BASELINE_LATENCY_S):
    source = item["source"]
    path = DATA_ROOT / source["path"]
    payload = verify_source_bytes(
        path, sha256_hex=item["sha256"], size_bytes=source["size_bytes"],
        maximum_bytes=maximum_bytes,
    )
    table = decode_parquet(payload)
    if item.get("rows") is not None and table.num_rows != item["rows"]:
        raise IntegrityError("admitted row count differs from the decoded source")
    return parse_raw_minute_table(
        table,
        symbol=source["symbol"],
        file_id=int(item["file_id"]),
        source_sha256=item["sha256"],
        variant="primary_corrected",
        year=source.get("year"),
        latency_after_end_s=latency_after_end_s,
        native_unit=source.get("native_unit"),
    )


def load_daily_observational(admitted, *, maximum_bytes: int, calendar=None):
    intended = None
    if calendar is not None:
        intended = [cash.day for cash in intended_cash_dates(
            calendar, POPULATION_START, POPULATION_END_EXCLUSIVE - timedelta(days=1))]
    cash_rows, action_rows = [], []
    for item in admitted_daily_sources(admitted):
        source = item["source"]
        payload = verify_source_bytes(
            DATA_ROOT / source["path"], sha256_hex=item["sha256"],
            size_bytes=source["size_bytes"], maximum_bytes=maximum_bytes,
        )
        table = decode_parquet(payload)
        if source["role"] == "daily_cash":
            cash_rows.extend(parse_daily_cash_table(
                table, symbol=source["symbol"], file_id=int(item["file_id"]),
                source_sha256=item["sha256"], intended_dates=intended))
        else:
            action_rows.extend(parse_corporate_actions_table(
                table, symbol=source["symbol"], file_id=int(item["file_id"]),
                source_sha256=item["sha256"]))
    return cash_rows, action_rows


def unit_quality_row(unit: UnitBars) -> dict:
    np = _np()
    counts = {name: int(np.count_nonzero(unit.quality_reason == code)) for name, code in QUALITY_CODE.items()}
    return {
        "symbol": unit.symbol,
        "variant": unit.variant,
        "year": unit.year,
        "file_id": unit.file_id,
        "source_sha256": unit.source_sha256,
        "source_version": unit.source_version,
        "rows": len(unit),
        "valid_rows": int(np.count_nonzero(unit.valid)),
        "volume_unit": unit.volume_unit,
        "native_unit": unit.native_unit,
        "definition_certified": unit.definition_certified,
        "instrument_kind": unit.instrument_kind,
        "contract_names": list(unit.contract_names),
        "quality_counts": counts,
    }


def mapping_chain_for(source_symbol: str, receiver_symbol: str):
    if (receiver_symbol, source_symbol) in MAPPING_CHAINS:
        return receiver_symbol, source_symbol
    if (source_symbol, receiver_symbol) in MAPPING_CHAINS:
        return source_symbol, receiver_symbol
    return None


def directed_unit_pairs(units):
    for source in units.values():
        for receiver in units.values():
            if (source.symbol, receiver.symbol) not in DIRECTED_PAIRS:
                continue
            if source.symbol == receiver.symbol and source.variant == receiver.variant:
                continue
            yield source, receiver


def unit_stable_key(unit: UnitBars):
    return (unit.symbol, unit.variant)
