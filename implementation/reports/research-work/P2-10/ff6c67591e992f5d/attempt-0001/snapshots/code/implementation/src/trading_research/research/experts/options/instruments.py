"""Root ledger: underlying, multiplier, exercise, settlement and expiry clocks.

Theta contracts parquet has no multiplier or settlement-time columns. Those
fields are registered research policies labelled as such. NDX vs NDXP and
SPX vs SPXW keep distinct expiry clocks even when the parquet expiration
column is only a date.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, timedelta
from decimal import Decimal
from pathlib import Path
from typing import Mapping

from trading_research.errors import ContractError
from trading_research.research.method_pack.clocks import et_ns
from trading_research.research.method_pack.session_policy import NQSessionPolicy

NS = 1_000_000_000
DATA_ROOT = Path("/workspace/data")
THETA = DATA_ROOT / "thetadata-opra"
DATABENTO = DATA_ROOT / "databento"
CASH_DAILY = DATA_ROOT / "free-sources" / "yahoo__cash-daily__normalized"
QQQ_1M = DATA_ROOT / "quantpad" / "nasdaq__qqq-etf__ohlcv-1m"
SPY_1M = DATA_ROOT / "quantpad" / "nyse-arca__spy-etf__ohlcv-1m"
NQ_1M = DATA_ROOT / "quantpad" / "cme__nq-continuous-futures__ohlcv-1m"
ES_1M = DATA_ROOT / "quantpad" / "cme__es-continuous-futures__ohlcv-1m"
RATES = DATA_ROOT / "free-sources" / "fred__usd-rates__normalized" / "usd-rates.parquet"
DIVIDENDS = DATA_ROOT / "free-sources" / "yahoo__corporate-actions__normalized"
STRIKE_MILLI = Decimal("0.001")
PRICE_CENT = Decimal("0.01")
NQ_TICK = Decimal("0.25")
OSI_WIDTH = 21
RIGHT_CALL = 1
RIGHT_PUT = -1

REJECT_OK = 0
REJECT_MISSING = 1
REJECT_NEGATIVE = 2
REJECT_CROSSED = 3
REJECT_NO_TS = 4
REJECT_STALE = 5
REJECT_WIDE = 6
REJECT_EXPIRED = 7
REJECT_BOUNDS = 8
REJECT_ZERO_PX = 9
REJECT_AMBIGUOUS = 10

REJECT_NAMES = {
    REJECT_OK: "ok",
    REJECT_MISSING: "missing_bid_ask",
    REJECT_NEGATIVE: "negative_quote",
    REJECT_CROSSED: "crossed_or_inverted",
    REJECT_NO_TS: "missing_timestamp",
    REJECT_STALE: "stale_quote",
    REJECT_WIDE: "wide_spread",
    REJECT_EXPIRED: "expired_or_through_close",
    REJECT_BOUNDS: "model_bounds",
    REJECT_ZERO_PX: "zero_price_not_mid",
    REJECT_AMBIGUOUS: "same_timestamp_conflict",
}


@dataclass(frozen=True, slots=True)
class RootSpec:
    root: str
    underlying_id: str
    underlying_kind: str
    multiplier: int
    exercise: str
    settlement: str
    expiry_session: str
    expiry_hour_et: int
    expiry_minute_et: int
    pricing_model: str
    quote_tick: Decimal
    strike_tick: Decimal
    option_style_source: str
    theta_prefix: str | None
    quote_dte14_dir: str | None
    quote_dte60_dir: str | None
    trade_quote_dir: str | None
    contracts_dir: str | None
    oi_dir: str | None
    eod_dir: str | None
    spot_intraday: str
    databento_prefix: str | None
    definition_unparsed: bool
    native_intraday_spot: bool


def _spec(**kwargs: object) -> RootSpec:
    return RootSpec(**kwargs)  # type: ignore[arg-type]


ROOTS: dict[str, RootSpec] = {
    "NDX": _spec(
        root="NDX",
        underlying_id="NDX",
        underlying_kind="cash_index",
        multiplier=100,
        exercise="european",
        settlement="cash",
        expiry_session="am",
        expiry_hour_et=9,
        expiry_minute_et=30,
        pricing_model="bsm_spot",
        quote_tick=PRICE_CENT,
        strike_tick=STRIKE_MILLI,
        option_style_source="research_policy_exchange_product_description",
        theta_prefix="opra__ndx-options",
        quote_dte14_dir="opra__ndx-options__quote-1m__dte14__strike-range70",
        quote_dte60_dir="opra__ndx-options__quote-1m__dte60__atm10",
        trade_quote_dir="opra__ndx-options__trade-quote__dte7__strike-range70",
        contracts_dir="opra__ndx-options__contracts",
        oi_dir="opra__ndx-options__open-interest",
        eod_dir="opra__ndx-options__eod",
        spot_intraday="none_owned_cash_index",
        databento_prefix=None,
        definition_unparsed=False,
        native_intraday_spot=False,
    ),
    "NDXP": _spec(
        root="NDXP",
        underlying_id="NDX",
        underlying_kind="cash_index",
        multiplier=100,
        exercise="european",
        settlement="cash",
        expiry_session="pm",
        expiry_hour_et=16,
        expiry_minute_et=0,
        pricing_model="bsm_spot",
        quote_tick=PRICE_CENT,
        strike_tick=STRIKE_MILLI,
        option_style_source="research_policy_exchange_product_description",
        theta_prefix="opra__ndxp-options",
        quote_dte14_dir="opra__ndxp-options__quote-1m__dte14__strike-range70",
        quote_dte60_dir="opra__ndxp-options__quote-1m__dte60__atm10",
        trade_quote_dir="opra__ndxp-options__trade-quote__dte7__strike-range70",
        contracts_dir="opra__ndxp-options__contracts",
        oi_dir="opra__ndxp-options__open-interest",
        eod_dir="opra__ndxp-options__eod",
        spot_intraday="none_owned_cash_index",
        databento_prefix=None,
        definition_unparsed=False,
        native_intraday_spot=False,
    ),
    "SPX": _spec(
        root="SPX",
        underlying_id="SPX",
        underlying_kind="cash_index",
        multiplier=100,
        exercise="european",
        settlement="cash",
        expiry_session="am",
        expiry_hour_et=9,
        expiry_minute_et=30,
        pricing_model="bsm_spot",
        quote_tick=PRICE_CENT,
        strike_tick=STRIKE_MILLI,
        option_style_source="research_policy_exchange_product_description",
        theta_prefix="opra__spx-options",
        quote_dte14_dir="opra__spx-options__quote-1m__dte14__strike-range90",
        quote_dte60_dir="opra__spx-options__quote-1m__dte60__atm10",
        trade_quote_dir="opra__spx-options__trade-quote__dte7__strike-range90",
        contracts_dir="opra__spx-options__contracts",
        oi_dir="opra__spx-options__open-interest",
        eod_dir="opra__spx-options__eod",
        spot_intraday="none_owned_cash_index",
        databento_prefix=None,
        definition_unparsed=False,
        native_intraday_spot=False,
    ),
    "SPXW": _spec(
        root="SPXW",
        underlying_id="SPX",
        underlying_kind="cash_index",
        multiplier=100,
        exercise="european",
        settlement="cash",
        expiry_session="pm",
        expiry_hour_et=16,
        expiry_minute_et=0,
        pricing_model="bsm_spot",
        quote_tick=PRICE_CENT,
        strike_tick=STRIKE_MILLI,
        option_style_source="research_policy_exchange_product_description",
        theta_prefix="opra__spxw-options",
        quote_dte14_dir="opra__spxw-options__quote-1m__dte14__strike-range90",
        quote_dte60_dir="opra__spxw-options__quote-1m__dte60__atm10",
        trade_quote_dir="opra__spxw-options__trade-quote__dte7__strike-range90",
        contracts_dir="opra__spxw-options__contracts",
        oi_dir="opra__spxw-options__open-interest",
        eod_dir="opra__spxw-options__eod",
        spot_intraday="none_owned_cash_index",
        databento_prefix=None,
        definition_unparsed=False,
        native_intraday_spot=False,
    ),
    "QQQ": _spec(
        root="QQQ",
        underlying_id="QQQ",
        underlying_kind="etf",
        multiplier=100,
        exercise="american",
        settlement="physical",
        expiry_session="pm",
        expiry_hour_et=16,
        expiry_minute_et=0,
        pricing_model="bsm_spot",
        quote_tick=PRICE_CENT,
        strike_tick=STRIKE_MILLI,
        option_style_source="research_policy_exchange_product_description",
        theta_prefix="opra__qqq-options",
        quote_dte14_dir="opra__qqq-options__quote-1m__dte14__strike-range42",
        quote_dte60_dir="opra__qqq-options__quote-1m__dte60__atm10",
        trade_quote_dir="opra__qqq-options__trade-quote__dte7__strike-range42",
        contracts_dir="opra__qqq-options__contracts",
        oi_dir="opra__qqq-options__open-interest",
        eod_dir="opra__qqq-options__eod",
        spot_intraday="quantpad_qqq_ohlcv_1m",
        databento_prefix=None,
        definition_unparsed=False,
        native_intraday_spot=True,
    ),
    "SPY": _spec(
        root="SPY",
        underlying_id="SPY",
        underlying_kind="etf",
        multiplier=100,
        exercise="american",
        settlement="physical",
        expiry_session="pm",
        expiry_hour_et=16,
        expiry_minute_et=0,
        pricing_model="bsm_spot",
        quote_tick=PRICE_CENT,
        strike_tick=STRIKE_MILLI,
        option_style_source="research_policy_exchange_product_description",
        theta_prefix="opra__spy-options",
        quote_dte14_dir="opra__spy-options__quote-1m__dte14__strike-range45",
        quote_dte60_dir="opra__spy-options__quote-1m__dte60__atm10",
        trade_quote_dir="opra__spy-options__trade-quote__dte7__strike-range45",
        contracts_dir="opra__spy-options__contracts",
        oi_dir="opra__spy-options__open-interest",
        eod_dir="opra__spy-options__eod",
        spot_intraday="quantpad_spy_ohlcv_1m",
        databento_prefix=None,
        definition_unparsed=False,
        native_intraday_spot=True,
    ),
    "NQ": _spec(
        root="NQ",
        underlying_id="NQ_future_native_not_continuous",
        underlying_kind="future",
        multiplier=20,
        exercise="unknown_unparsed_definition",
        settlement="future",
        expiry_session="unknown_unparsed_definition",
        expiry_hour_et=16,
        expiry_minute_et=0,
        pricing_model="black76",
        quote_tick=NQ_TICK,
        strike_tick=NQ_TICK,
        option_style_source="owned_databento_definition_unparsed",
        theta_prefix=None,
        quote_dte14_dir=None,
        quote_dte60_dir=None,
        trade_quote_dir=None,
        contracts_dir=None,
        oi_dir=None,
        eod_dir=None,
        spot_intraday="quantpad_nq_ohlcv_1m",
        databento_prefix="cme__nq-options-on-futures",
        definition_unparsed=True,
        native_intraday_spot=True,
    ),
    "ES": _spec(
        root="ES",
        underlying_id="ES_future_native_not_continuous",
        underlying_kind="future",
        multiplier=50,
        exercise="unknown_unparsed_definition",
        settlement="future",
        expiry_session="unknown_unparsed_definition",
        expiry_hour_et=16,
        expiry_minute_et=0,
        pricing_model="black76",
        quote_tick=NQ_TICK,
        strike_tick=NQ_TICK,
        option_style_source="owned_databento_definition_unparsed",
        theta_prefix=None,
        quote_dte14_dir=None,
        quote_dte60_dir=None,
        trade_quote_dir=None,
        contracts_dir=None,
        oi_dir=None,
        eod_dir=None,
        spot_intraday="quantpad_es_ohlcv_1m",
        databento_prefix="cme__es-options-on-futures",
        definition_unparsed=True,
        native_intraday_spot=True,
    ),
}

REQUIRED_ROOTS = ("NDX", "NDXP", "SPX", "SPXW", "QQQ", "SPY", "NQ", "ES")
OPRA_ROOTS = ("NDX", "NDXP", "SPX", "SPXW", "QQQ", "SPY")
FUTURES_OPTION_ROOTS = ("NQ", "ES")


def root_spec(root: str) -> RootSpec:
    spec = ROOTS.get(root)
    if spec is None:
        raise ContractError(f"unknown option root {root}")
    return spec


def theta_path(spec: RootSpec, kind: str) -> Path | None:
    name = {
        "contracts": spec.contracts_dir,
        "oi": spec.oi_dir,
        "eod": spec.eod_dir,
        "quote_dte14": spec.quote_dte14_dir,
        "quote_dte60": spec.quote_dte60_dir,
        "trade_quote": spec.trade_quote_dir,
    }.get(kind)
    if not name:
        return None
    return THETA / name


def session_file(spec: RootSpec, kind: str, day: date) -> Path | None:
    folder = theta_path(spec, kind)
    if folder is None:
        return None
    return folder / f"{day.isoformat()}.parquet"


def parse_osi(osi: str) -> tuple[str, date, int, int]:
    """Return root, expiry date, right (+1 call / -1 put), strike millis from OSI."""
    if not isinstance(osi, str) or len(osi) < OSI_WIDTH:
        raise ContractError("osi_symbol must be the 21-character OCC key")
    root = osi[:6].rstrip()
    yymmdd = osi[6:12]
    right_ch = osi[12]
    strike_field = osi[13:21]
    if right_ch not in ("C", "P") or not yymmdd.isdigit() or not strike_field.isdigit():
        raise ContractError("osi_symbol is not a well-formed OCC key")
    year = 2000 + int(yymmdd[0:2])
    month = int(yymmdd[2:4])
    day = int(yymmdd[4:6])
    expiry = date(year, month, day)
    right = RIGHT_CALL if right_ch == "C" else RIGHT_PUT
    return root, expiry, right, int(strike_field)


def strike_from_millis(millis: int) -> Decimal:
    return (Decimal(int(millis)) * STRIKE_MILLI).quantize(STRIKE_MILLI)


def price_from_cents(cents: int) -> Decimal:
    return (Decimal(int(cents)) * PRICE_CENT).quantize(PRICE_CENT)


def cents_from_price(price: float | Decimal) -> int:
    value = price if isinstance(price, Decimal) else Decimal(str(price))
    quanta = value / PRICE_CENT
    if quanta != quanta.to_integral_value():
        raise ContractError("option price is not an integer cent tick")
    return int(quanta)


def expiry_ns(spec: RootSpec, expiry_day: date) -> int:
    return et_ns(expiry_day, spec.expiry_hour_et, spec.expiry_minute_et)


def next_regular_session(day: date, *, policy: NQSessionPolicy | None = None) -> date:
    policy = policy or NQSessionPolicy()
    cursor = day + timedelta(days=1)
    for _ in range(21):
        info = policy.day(cursor)
        if info.get("state") == "regular":
            return cursor
        cursor += timedelta(days=1)
    raise ContractError(f"no regular session within 21 days after {day}")


def previous_regular_session(day: date, *, policy: NQSessionPolicy | None = None) -> date | None:
    policy = policy or NQSessionPolicy()
    cursor = day - timedelta(days=1)
    for _ in range(21):
        info = policy.day(cursor)
        if info.get("state") == "regular":
            return cursor
        cursor -= timedelta(days=1)
    return None


def assumed_oi_available_ns(effective: date, *, extra_sessions: int = 0, policy: NQSessionPolicy | None = None) -> int:
    """Conservative research clock: 12:00 ET on the next verified regular session."""
    policy = policy or NQSessionPolicy()
    available_day = next_regular_session(effective, policy=policy)
    for _ in range(extra_sessions):
        available_day = next_regular_session(available_day, policy=policy)
    return et_ns(available_day, 12, 0)


def instrument_ledger_rows() -> list[dict[str, object]]:
    rows = []
    for root in REQUIRED_ROOTS:
        spec = root_spec(root)
        dbn_dir = None if spec.databento_prefix is None else DATABENTO / f"{spec.databento_prefix}__definition"
        rows.append(
            {
                "root": spec.root,
                "raw_ids_preserved": True,
                "underlying_id": spec.underlying_id,
                "underlying_kind": spec.underlying_kind,
                "multiplier": spec.multiplier,
                "exercise": spec.exercise,
                "settlement": spec.settlement,
                "expiry_session": spec.expiry_session,
                "expiry_hour_et": spec.expiry_hour_et,
                "expiry_minute_et": spec.expiry_minute_et,
                "pricing_model": spec.pricing_model,
                "option_style_source": spec.option_style_source,
                "definition_unparsed": spec.definition_unparsed,
                "native_intraday_spot": spec.native_intraday_spot,
                "spot_intraday": spec.spot_intraday,
                "theta_contracts": None if spec.contracts_dir is None else str(THETA / spec.contracts_dir),
                "theta_oi": None if spec.oi_dir is None else str(THETA / spec.oi_dir),
                "theta_quote_dte14": None if spec.quote_dte14_dir is None else str(THETA / spec.quote_dte14_dir),
                "databento_definition": None if dbn_dir is None else str(dbn_dir),
                "databento_present": False if dbn_dir is None else dbn_dir.is_dir(),
            }
        )
    return rows


def expiry_clocks_distinct() -> dict[str, object]:
    ndx = root_spec("NDX")
    ndxp = root_spec("NDXP")
    spx = root_spec("SPX")
    spxw = root_spec("SPXW")
    probe = date(2024, 1, 19)
    return {
        "ndx_expiry_ns": expiry_ns(ndx, probe),
        "ndxp_expiry_ns": expiry_ns(ndxp, probe),
        "spx_expiry_ns": expiry_ns(spx, probe),
        "spxw_expiry_ns": expiry_ns(spxw, probe),
        "ndx_session": ndx.expiry_session,
        "ndxp_session": ndxp.expiry_session,
        "spx_session": spx.expiry_session,
        "spxw_session": spxw.expiry_session,
        "ndx_ndxp_distinct": expiry_ns(ndx, probe) != expiry_ns(ndxp, probe),
        "spx_spxw_distinct": expiry_ns(spx, probe) != expiry_ns(spxw, probe),
    }


def ledger_document() -> dict[str, object]:
    clocks = expiry_clocks_distinct()
    return {
        "schema_version": "research-instrument-ledger-v1",
        "roots": instrument_ledger_rows(),
        "expiry_clocks": clocks,
        "notes": [
            "Theta contracts parquet has no multiplier, exercise or settlement-time columns.",
            "Cash-index AM/PM clocks are registered research policies, not parquet fields.",
            "NQ/ES option definitions are owned Databento DBN files; the decoder is not installed.",
        ],
    }
