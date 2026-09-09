"""Typed, causal source fixtures for the E0 integration controls.

The fixture deliberately builds the public E0 source path instead of writing
``FrozenRange`` or ``VenuePath`` result rows directly.  A day therefore keeps
the raw definition/universe selection, the calendar and shared-bar receipts,
the C01/L03 ``RangeVersion`` values, native MBP records, and the operational
binding that consumes those source facts.  The sparse 17-minute venue window
is an engineering control; it is not a claim about real-market coverage.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, time, timedelta
from decimal import Decimal
from fractions import Fraction
from pathlib import Path
from typing import Any

from trading_research.context.range_adapter import primitive_from_shared_bar, select_clock
from trading_research.context.ranges import RangeVersion, range_definition, range_version
from trading_research.data.events import CanonicalEvent, LatencyScenario, SourceAddress, normalize_mbp
from trading_research.execution.costs import FeeSchedule
from trading_research.experiments.e0.admission import (
    E0DayAdmission,
    E0OperationalBinding,
    admit_e0_day,
    bind_e0_day_operational_terms,
)
from trading_research.experiments.e0.runner import E0MinutePrice, E0RunDay
from trading_research.experiments.e0.source_bridge import E0FrozenContext, NativeCoverageReceipt, freeze_e0_ranges
from trading_research.foundations.bars import Watermark, WindowCoverage
from trading_research.foundations.calendar import Calendar, Session, local_timestamp
from trading_research.foundations.contracts import InstrumentKey
from trading_research.foundations.instruments import InstrumentDefinition, instrument_identity
from trading_research.foundations.intervals import IntervalGraph, NamedInterval, Span
from trading_research.foundations.multiresolution import (
    BarDefinition,
    BarDomain,
    BarLimits,
    SharedBarEngine,
    WindowRequest,
)
from trading_research.foundations.object_graph import Instrument
from trading_research.foundations.rolls import ContractUniverse, SessionSequence, SessionVolume
from trading_research.foundations.time import AvailabilityBasis, Clocks
from trading_research.foundations.units import FuturesTerms, Ticks
from trading_research.measurements.tape import Trade
from trading_research.operations.artifacts import digest


NS = 1_000_000_000
NY = "America/New_York"
PROVIDER = "quantpad"
VENUE = "CME"
ROOT = "NQ"
INSTRUMENT_ID = "1002"
RAW_SYMBOL = "NQU5"
SCOPE = "E0_historical_2022_2025_harness"
REPO = Path(__file__).resolve().parents[1]


@dataclass(frozen=True)
class SharedDaySource:
    """All retained typed source facts for one sparse E0 day."""

    day: date
    base_cut: int
    cuts: tuple[int, ...]
    canonical_events: tuple[CanonicalEvent, ...]
    coverage: dict[str, Any]
    range_06_09: Any
    prior_rth: Any
    range_versions: tuple[RangeVersion, RangeVersion]
    context: E0FrozenContext
    admission: E0DayAdmission
    operational: E0OperationalBinding
    cash_day: Any
    published_cash_day: Any
    venue_boundary: Any
    universe: ContractUniverse
    definitions: tuple[InstrumentDefinition, ...]
    volumes: tuple[SessionVolume, ...]
    session_sequence: SessionSequence
    objects: tuple
    source_receipts: tuple[dict[str, Any], ...]
    minute_history: tuple[E0MinutePrice, ...]
    quote_path: str
    source_manifest: dict[str, Any]
    terms: dict[str, FuturesTerms]
    operational_coverage: dict[str, Any]

    @property
    def source_versions(self) -> tuple[str, ...]:
        return tuple(dict.fromkeys((
            "fixture-native-mbp-v1",
            self.admission.selection_version,
            self.universe.version,
            *(d.key.definition_version for d in self.definitions),
            *(v.version for v in self.volumes),
            self.session_sequence.version,
            *(r.version_id for r in self.range_versions),
            self.coverage["version"],
            self.operational.version,
        )))

    @property
    def run_day(self) -> E0RunDay:
        """Return the runner-facing typed day envelope."""
        return E0RunDay(
            self.day.isoformat(),
            self.cuts,
            self.context,
            self.operational,
            self.canonical_events,
            self.coverage,
            self.minute_history,
            market_state="continuous",
        )


@dataclass(frozen=True)
class SharedComparatorSource:
    per_day: tuple[SharedDaySource, ...]
    canonical_events: tuple[CanonicalEvent, ...]
    cuts: tuple[int, ...]
    aliases: dict[str, str]
    source_receipts: tuple[dict[str, Any], ...]
    selected_instrument_id: str = INSTRUMENT_ID
    root: str = ROOT
    tick_size: Fraction = Fraction(1, 4)
    multiplier_usd_per_point: Fraction = Fraction(20)
    range_low_ticks: int = 71954
    range_high_ticks: int = 72054
    stop_distance_ticks: int = 10

    @property
    def source_versions(self) -> tuple[str, ...]:
        return tuple(dict.fromkeys(v for day in self.per_day for v in day.source_versions))

    @property
    def ranges(self) -> tuple[tuple[Any, Any], ...]:
        return tuple((day.range_06_09, day.prior_rth) for day in self.per_day)

    @property
    def run_days(self) -> tuple[E0RunDay, ...]:
        return tuple(day.run_day for day in self.per_day)


@dataclass(frozen=True)
class Int01AdmissionSource:
    """Typed source rows that mirror the frozen INT01 golden inputs.

    The golden file uses stable lifetime aliases (``life-1001`` and
    ``life-1002``).  The public foundations use content identities, so this
    envelope retains both: all typed universe/volume bindings use the actual
    ``instrument_identity`` digest and ``lifetime_aliases`` records the
    project-facing aliases for exact case reporting.
    """

    day: date
    cut: int
    definitions: tuple[InstrumentDefinition, ...]
    volumes: tuple[SessionVolume, ...]
    universe: ContractUniverse
    session_sequence: SessionSequence
    venue_boundary: Any
    source_manifest: dict[str, Any]
    terms: dict[str, FuturesTerms]
    admission: E0DayAdmission
    lifetime_aliases: dict[str, str]


def _int01_definitions() -> tuple[InstrumentDefinition, ...]:
    known_at = 1717214400000000000
    valid_from = 1687291200000000000
    valid_until = 1734728400000000000
    rows = (
        ("1001", "NQM4", 1718913600000000000, "def-1001-v1"),
        ("1002", "NQU4", 1726862400000000000, "def-1002-v1"),
    )
    return tuple(
        InstrumentDefinition(
            InstrumentKey(PROVIDER, VENUE, instrument_id, raw_symbol, ROOT, version,
                           expiry_at=expiry_at),
            Clocks(None, known_at, "definitions-v1", AvailabilityBasis.RECEIVED,
                   received_at=known_at, valid_from=valid_from, valid_until=valid_until),
            "future", Decimal("20"), Decimal("0.25"),
        )
        for instrument_id, raw_symbol, expiry_at, version in rows
    )


def make_int01_source() -> Int01AdmissionSource:
    """Return the exact typed INT01 2024-06-03/May-31 source population."""
    day = date(2024, 6, 3)
    previous = date(2024, 5, 31)
    cut = 1717421460000000000
    known_at = 1717214400000000000
    previous_open = 1717106400000000000
    previous_close = 1717189200000000000
    current_open = 1717419600000000000
    current_close = 1717444800000000000
    definitions = _int01_definitions()
    aliases = {"life-1001": instrument_identity(definitions[0]),
               "life-1002": instrument_identity(definitions[1])}
    previous_session = Session(
        "NQ-VENUE-2024-05-31", previous, ROOT, previous_open, previous_close,
        (), 0, known_at, "cme-venue-boundary-v1", "tzdb-America/New_York-v1", True,
        "verified venue schedule",
    )
    current_session = Session(
        "NQ-VENUE-2024-06-03", day, ROOT, current_open, current_close,
        (), 0, known_at, "cme-venue-boundary-v1", "tzdb-America/New_York-v1", True,
        "verified venue schedule",
    )
    sequence = SessionSequence(
        "NQ-calendar-2024-v4", ROOT, (previous_session, current_session), known_at,
        "calendar-v4", True,
    )
    volumes = tuple(
        SessionVolume(
            definition.key.instrument_id, previous_session.id, previous_open, previous_close,
            known_at, contracts, True, f"prior-volume-{definition.key.instrument_id}-v1",
            aliases[f"life-{definition.key.instrument_id}"],
        )
        for definition, contracts in zip(definitions, (1200, 2100))
    )
    universe = ContractUniverse(
        "NQ-parent-2024-06-03-v1", ROOT, known_at,
        ("1001", "1002"), "complete_parent_outrights", "definitions-v1",
        PROVIDER, VENUE,
        tuple((definition.key.instrument_id, aliases[f"life-{definition.key.instrument_id}"])
              for definition in definitions),
    )
    from trading_research.foundations.cash_calendar import VenueBoundary
    boundary = VenueBoundary(
        day, ROOT, current_open, current_close, current_close, known_at,
        "cme-venue-boundary-v1", "verified_venue_schedule",
    )
    required = (
        "raw_definition", "product_terms", "cash_calendar", "venue_boundary",
        "prior_session_volume", "complete_outright_universe", "mbp_full_schema",
        "book_recovery", "formation_window", "prior_rth_window", "entry_and_label_window",
    )
    source_manifest = {
        "checks": {name: {"state": "satisfied", "evidence": f"golden-int01:{name}"}
                   for name in required},
        "data_versions": ("definitions-v1", "calendar-v4", "mbp-schema-v2"),
        "golden_inspected_fields": (
            "raw_definition", "product_terms", "cash_calendar", "venue_boundary",
            "prior_volume", "mbp_fields", "book_recovery", "range_06_09",
            "prior_rth", "entry_label_window",
        ),
        # ``entry_window`` is the causal inspected field; the semantic check
        # remains the exact frozen ``entry_and_label_window`` row above.
        "inspected_fields": (
            "raw_definition", "product_terms", "cash_calendar", "venue_boundary",
            "prior_volume", "mbp_fields", "book_recovery", "range_06_09",
            "prior_rth", "entry_window",
        ),
        "previous_session_id": previous_session.id,
    }
    terms = {
        definition.key.instrument_id: FuturesTerms(
            ROOT, Decimal("0.25"), Decimal("20"), definition.key.definition_version,
        )
        for definition in definitions
    }
    admission = admit_e0_day(
        day=day, cut=cut, universe=universe, definitions=definitions, volumes=volumes,
        session_sequence=sequence, calendar=sequence, boundary=boundary,
        source_manifest=source_manifest, terms=terms,
        scope="E0_historical_2022_2025_harness",
    )
    return Int01AdmissionSource(
        day, cut, definitions, volumes, universe, sequence, boundary,
        source_manifest, terms, admission, aliases,
    )


def _ns(at: int) -> int:
    return at * NS


def _session(day: date, *, known_at: int) -> Session:
    return Session(
        f"NQ-VENUE-{day.isoformat()}",
        day,
        ROOT,
        local_timestamp(day, time(9, 30), NY),
        local_timestamp(day, time(16, 0), NY),
        (),
        0,
        known_at,
        f"venue-calendar-v1-{day.isoformat()}",
        "tzdb-America-New_York-v1",
        True,
        "verified sparse engineering venue session",
    )


def _instrument_definitions(day: date) -> tuple[InstrumentDefinition, ...]:
    valid_from = local_timestamp(day - timedelta(days=365), time(0), NY)
    known_at = local_timestamp(day - timedelta(days=30), time(0), NY)
    valid_until = local_timestamp(day + timedelta(days=365), time(0), NY)

    def make(instrument_id: str, raw_symbol: str, expiry_offset: int) -> InstrumentDefinition:
        expiry_at = local_timestamp(day + timedelta(days=expiry_offset), time(16), NY)
        version = f"def-{instrument_id}-{day.isoformat()}-v1"
        key = InstrumentKey(PROVIDER, VENUE, instrument_id, raw_symbol, ROOT, version, expiry_at=expiry_at)
        clocks = Clocks(
            None,
            known_at,
            f"instrument-definition-source-{day.isoformat()}-v1",
            AvailabilityBasis.RECEIVED,
            received_at=known_at,
            valid_from=valid_from,
            valid_until=valid_until,
        )
        return InstrumentDefinition(key, clocks, "future", Decimal("20"), Decimal("0.25"))

    return (make("1001", "NQM5", 30), make(INSTRUMENT_ID, RAW_SYMBOL, 60))


def _source_instrument(definition: InstrumentDefinition, *, valid_from: int, valid_until: int) -> Instrument:
    return Instrument(
        PROVIDER,
        VENUE,
        definition.key.instrument_id,
        definition.key.raw_symbol or RAW_SYMBOL,
        definition.key.definition_version or "definition-v1",
        Fraction(definition.tick_size),
        valid_from,
        valid_until,
        definition.key.expiry_at,
    )


def _range_graph(day: date, previous: date, *, current_start: int, current_end: int,
                 prior_start: int, prior_end: int) -> IntervalGraph:
    known_at = local_timestamp(day - timedelta(days=30), time(0), NY)
    current = NamedInterval(
        f"C01-06_09-{day.isoformat()}",
        "e0-source-fixture",
        (Span(current_start, current_end),),
        known_at,
        f"c01-clock-source-{day.isoformat()}-v1",
        "NY-06_09",
        "tzdb-America-New_York-v1",
        (day,),
    )
    prior = NamedInterval(
        f"L03-prior-RTH-{previous.isoformat()}",
        "e0-source-fixture",
        (Span(prior_start, prior_end),),
        known_at,
        f"l03-clock-source-{previous.isoformat()}-v1",
        "NY-prior-RTH",
        "tzdb-America-New_York-v1",
        (previous,),
    )
    return IntervalGraph(f"e0-range-graph-{day.isoformat()}", (current, prior))


def _trade(instrument: Instrument, *, identity: str, event_at: int, known_at: int,
           ticks: int, order: int, source_version: str) -> Trade:
    return Trade(
        identity,
        source_version,
        instrument.raw_symbol,
        event_at,
        known_at,
        Ticks(ticks),
        1,
        1,
        order,
        "registered-whole-print",
        True,
    )


def _build_range_versions(day: date, previous: date, *, current_end: int, prior_publication: int,
                          definition: InstrumentDefinition) -> tuple[RangeVersion, RangeVersion]:
    current_start = local_timestamp(day, time(6, 0), NY)
    prior_start = local_timestamp(previous, time(9, 30), NY)
    prior_end = local_timestamp(previous, time(16, 0), NY)
    graph = _range_graph(
        day,
        previous,
        current_start=current_start,
        current_end=current_end,
        prior_start=prior_start,
        prior_end=prior_end,
    )
    cal = Calendar()
    cal.append(_session(previous, known_at=local_timestamp(day - timedelta(days=30), time(0), NY)))
    cal.append(_session(day, known_at=local_timestamp(day - timedelta(days=30), time(0), NY)))
    source_instrument = _source_instrument(
        definition,
        valid_from=definition.clocks.valid_from,
        valid_until=definition.clocks.valid_until,
    )
    current_selection = select_clock(
        calendar=cal,
        interval_graph=graph,
        interval_name=f"C01-06_09-{day.isoformat()}",
        trading_date=day,
        instrument_root=ROOT,
        instrument=source_instrument,
        cut=current_end,
    )
    prior_selection = select_clock(
        calendar=cal,
        interval_graph=graph,
        interval_name=f"L03-prior-RTH-{previous.isoformat()}",
        trading_date=previous,
        instrument_root=ROOT,
        instrument=source_instrument,
        cut=prior_publication,
    )
    domain = BarDomain(source_instrument.raw_symbol, "registered-whole-print", "registered-whole-print")
    current_definition = BarDefinition(
        domain,
        f"C01-time-{day.isoformat()}-v1",
        graph.version,
        current_selection.clock_id,
    )
    prior_definition = BarDefinition(
        domain,
        f"L03-time-{previous.isoformat()}-v1",
        graph.version,
        prior_selection.clock_id,
    )
    engine = SharedBarEngine(domain, (current_definition, prior_definition), limits=BarLimits(64, 8, 8, 8))
    current_rows = (
        (current_start + 1 * NS, 71980),
        (current_start + 2 * NS, 72054),
        (current_start + 3 * NS, 71954),
        (current_end - 1 * NS, 72004),
    )
    prior_rows = (
        (prior_start + 1 * NS, 71996),
        (prior_start + 2 * NS, 72012),
        (prior_start + 3 * NS, 71960),
        (prior_end - 1 * NS, 72004),
    )
    current_trades = tuple(
        _trade(source_instrument, identity=f"{day.isoformat()}-c01-{index}", event_at=at,
               known_at=at, ticks=ticks, order=index, source_version=f"c01-trades-{day.isoformat()}-v1")
        for index, (at, ticks) in enumerate(current_rows)
    )
    prior_trades = tuple(
        _trade(source_instrument, identity=f"{previous.isoformat()}-prior-{index}", event_at=at,
               known_at=prior_publication, ticks=ticks, order=index, source_version=f"prior-trades-{previous.isoformat()}-v1")
        for index, (at, ticks) in enumerate(prior_rows)
    )
    # Admission is monotone in known_at.  The previous RTH trades are already
    # completed but their synthetic computation receipt arrives at 09:01.
    engine.add_many(tuple(sorted((*current_trades, *prior_trades), key=lambda row: (row.known_at, row.event_at, row.id))))
    current_coverage = WindowCoverage(
        source_instrument.raw_symbol,
        current_start,
        current_end,
        ((current_start, current_end),),
        current_end,
        f"c01-coverage-{day.isoformat()}-v1",
    )
    prior_coverage = WindowCoverage(
        source_instrument.raw_symbol,
        prior_start,
        prior_end,
        ((prior_start, prior_end),),
        prior_publication,
        f"prior-coverage-{previous.isoformat()}-v1",
    )
    current_bar = engine.publish_window(
        engine.capture(current_end),
        WindowRequest(
            current_definition.id,
            current_start,
            current_end,
            current_coverage,
            Watermark(current_end, current_end, f"c01-watermark-{day.isoformat()}-v1"),
        ),
        published_at=current_end,
    )
    prior_bar = engine.publish_window(
        engine.capture(prior_publication),
        WindowRequest(
            prior_definition.id,
            prior_start,
            prior_end,
            prior_coverage,
            Watermark(prior_end, prior_publication, f"prior-watermark-{previous.isoformat()}-v1"),
        ),
        published_at=prior_publication,
    )
    current_primitive = primitive_from_shared_bar(
        selection=current_selection,
        engine=engine,
        publication_version_id=current_bar.version_id,
        cut=current_end,
    )
    prior_primitive = primitive_from_shared_bar(
        selection=prior_selection,
        engine=engine,
        publication_version_id=prior_bar.version_id,
        cut=prior_publication,
    )
    current_range = range_version(
        current_primitive,
        range_definition(current_selection, id="C01-range-geometry-v1", version="v1", source_ids=("C01",)),
        cut=current_end,
    )
    prior_range = range_version(
        prior_primitive,
        range_definition(prior_selection, id="L03-prior-session-v1", version="v1", source_ids=("L03",)),
        cut=prior_publication,
    )
    return current_range, prior_range


def _native_event(*, day: date, row: int, sequence: int, event_at: int, action: str,
                  bid_ticks: int, ask_ticks: int, size: int, side: str, flags: int,
                  trade_ticks: int | None = None, with_trade: bool = False) -> CanonicalEvent:
    receive_at = event_at + 25_000_000
    address = SourceAddress(
        dataset_id="e0-fixture-native-mbp-1",
        acquisition_version="fixture-acquisition-native-v1",
        relative_path=f"native/{day.isoformat()}.mbp-1",
        container_version="fixture-native-container-v1",
        partition=day.isoformat(),
        row=row,
        schema_version="mbp-native-v1",
    )
    price_ticks = bid_ticks if with_trade and trade_ticks is None else (trade_ticks if with_trade else (bid_ticks + ask_ticks) // 2)
    fields = {
        "ts_event": event_at,
        "ts_recv": receive_at,
        "action": action,
        "side": side,
        "price": price_ticks * 250_000_000,
        "size": size,
        "flags": flags,
        "instrument_id": int(INSTRUMENT_ID),
        "bid_px_00": bid_ticks * 250_000_000,
        "ask_px_00": ask_ticks * 250_000_000,
        "bid_sz_00": 5,
        "ask_sz_00": 5,
        "publisher_id": 1,
        "sequence": sequence,
        "depth": 0,
    }
    return normalize_mbp(
        fields,
        address,
        native=True,
        scenario=LatencyScenario("fixture-provider-receipt-v1", "provider_received", 0, 0),
    )


def _native_events(day: date, *, base: int, quote_path: str) -> tuple[CanonicalEvent, ...]:
    if quote_path not in {"comparator_down", "comparator_quiet", "learning_up", "learning_down"}:
        raise ValueError(f"unsupported E0 source quote path: {quote_path}")
    if quote_path == "comparator_down":
        down_bid, down_ask, trade_ticks, include_trade = 71979, 71981, 71980, True
    elif quote_path == "learning_up":
        down_bid, down_ask, trade_ticks, include_trade = 72034, 72036, 72035, True
    elif quote_path == "learning_down":
        down_bid, down_ask, trade_ticks, include_trade = 71974, 71976, 71975, True
    else:
        down_bid, down_ask, trade_ticks, include_trade = 71999, 72001, None, False
    contact_bid, contact_ask = ((71999, 72001) if quote_path == "comparator_quiet" else (72003, 72005))
    rows = [
        (10, base - 62 * NS, "A", 71999, 72001, 1, "N", 128, None, False),
        (11, base - 2 * NS, "A", contact_bid, contact_ask, 1, "N", 128, None, False),
        (12, base + 120 * NS, "A", down_bid, down_ask, 1, "N", 128, None, False),
    ]
    if include_trade:
        rows.append((13, base + 120 * NS, "T", down_bid, down_ask, 2, "B", 0, trade_ticks, True))
    rows.append((14, base + 16 * 60 * NS, "A", down_bid, down_ask, 1, "N", 128, None, False))
    return tuple(
        _native_event(
            day=day,
            row=sequence,
            sequence=sequence,
            event_at=event_at,
            action=action,
            bid_ticks=bid_ticks,
            ask_ticks=ask_ticks,
            size=size,
            side=side,
            flags=flags,
            trade_ticks=trade_ticks,
            with_trade=with_trade,
        )
        for sequence, event_at, action, bid_ticks, ask_ticks, size, side, flags, trade_ticks, with_trade in rows
    )


def _minute_history(day: date, base: int) -> tuple[E0MinutePrice, ...]:
    # Include 09:00 through 09:31 so the 09:31 cut has 31 strictly prior
    # completed observations and the later cuts still use a full 30-change
    # lookback.
    return tuple(
        E0MinutePrice(
            base - (32 - index) * 60 * NS,
            base - (32 - index) * 60 * NS,
            Fraction(72000),
            f"minute-history-{day.isoformat()}-v1",
        )
        for index in range(32)
    )


def fee_schedule() -> FeeSchedule:
    return FeeSchedule(
        "fee-nq-synthetic-v1",
        "synthetic-verified-connection",
        "synthetic one-mini account",
        "USD",
        (("NQ", Decimal("5.03")), ("ES", Decimal("5.03"))),
        ("https://example.test/e0-fee-evidence",),
        "2026-09-07",
        "synthetic-e0-fee-evidence-v1",
        "published_benchmark_not_historical_account_cost",
        frozenset({"exchange", "regulatory", "clearing", "commission", "routing"}),
    )


def _build_day(day: date, *, quote_path: str) -> SharedDaySource:
    previous = day - timedelta(days=1)
    base = local_timestamp(day, time(9, 32), NY)
    current_end = local_timestamp(day, time(9, 0), NY)
    prior_publication = local_timestamp(day, time(9, 1), NY)
    definitions = _instrument_definitions(day)
    selected_definition = definitions[1]
    prev_session = _session(previous, known_at=local_timestamp(day - timedelta(days=30), time(0), NY))
    current_session = _session(day, known_at=local_timestamp(day - timedelta(days=30), time(0), NY))
    sequence = SessionSequence(
        f"NQ-session-sequence-{day.isoformat()}-v1",
        ROOT,
        (prev_session, current_session),
        current_session.known_at,
        f"venue-calendar-sequence-{day.isoformat()}-v1",
        True,
    )
    volumes = tuple(
        SessionVolume(
            definition.key.instrument_id,
            prev_session.id,
            prev_session.open_at,
            prev_session.close_at,
            local_timestamp(day, time(9, 0), NY),
            contracts,
            True,
            f"prior-volume-{day.isoformat()}-{definition.key.instrument_id}-v1",
            instrument_identity(definition),
        )
        for definition, contracts in zip(definitions, (1200, 2100))
    )
    universe = ContractUniverse(
        f"NQ-complete-parent-{day.isoformat()}-v1",
        ROOT,
        local_timestamp(day - timedelta(days=30), time(0), NY),
        tuple(d.key.instrument_id for d in definitions),
        "complete_parent_outrights",
        f"complete-parent-universe-{day.isoformat()}-v1",
        PROVIDER,
        VENUE,
        tuple((d.key.instrument_id, instrument_identity(d)) for d in definitions),
    )
    cash_calendar = __import__("trading_research.foundations.cash_calendar", fromlist=["CashCalendar"]).CashCalendar(
        REPO / "configs" / "cash-rth-calendar.json"
    )
    published_cash_day = cash_calendar.resolve(day, cut=base)
    # The source fixture declares a finite engineering venue horizon.  It is a
    # typed cash-day record with the published calendar/version retained in its
    # source versions, while the published calendar row remains available above.
    cash_day = type(published_cash_day)(
        day,
        "regular",
        published_cash_day.open_at,
        base + 17 * 60 * NS,
        published_cash_day.known_at,
        tuple(dict.fromkeys((*published_cash_day.source_versions, "cash-day-sparse-window-v1"))),
        published_cash_day.timezone_version,
        published_cash_day.convention_version,
    )
    from trading_research.foundations.cash_calendar import VenueBoundary
    venue_boundary = VenueBoundary(
        day,
        ROOT,
        cash_day.open_at,
        base + 17 * 60 * NS,
        base + 17 * 60 * NS,
        local_timestamp(day, time(9, 0), NY),
        f"verified-venue-boundary-sparse-{day.isoformat()}-v1",
        "verified_venue_schedule",
    )
    manifest_checks = {
        name: {"state": "satisfied", "evidence": f"source-receipt:{name}:{day.isoformat()}"}
        for name in (
            "raw_definition", "product_terms", "cash_calendar", "venue_boundary",
            "prior_session_volume", "complete_outright_universe", "mbp_full_schema",
            "book_recovery", "formation_window", "prior_rth_window", "entry_and_label_window",
        )
    }
    source_manifest = {
        "checks": manifest_checks,
        "data_versions": (
            f"definitions-{day.isoformat()}-v1",
            sequence.source_version,
            "mbp-native-v1",
            cash_day.convention_version,
        ),
        "inspected_fields": (
            "raw_definition", "product_terms", "cash_calendar", "venue_boundary",
            "prior_session_volume", "complete_outright_universe", "mbp_full_schema",
            "book_recovery", "formation_window", "prior_rth_window", "entry_window",
        ),
        "previous_session_id": prev_session.id,
    }
    terms = {
        d.key.instrument_id: FuturesTerms(ROOT, Decimal("0.25"), Decimal("20"), d.key.definition_version)
        for d in definitions
    }
    admission = admit_e0_day(
        day=day,
        cut=base,
        universe=universe,
        definitions=definitions,
        volumes=volumes,
        session_sequence=sequence,
        calendar=sequence,
        boundary=venue_boundary,
        source_manifest=source_manifest,
        terms=terms,
        scope=SCOPE,
    )
    operational_coverage = {
        "checks": {
            name: {"state": "satisfied", "evidence": f"native-receipt:{name}:{day.isoformat()}"}
            for name in ("mbp_full_schema", "book_recovery", "entry_and_label_window")
        },
        "source_versions": ("mbp-native-v1", f"coverage-{day.isoformat()}-v1"),
    }
    operational = bind_e0_day_operational_terms(
        day=day,
        cash_day=cash_day,
        venue_boundary=venue_boundary,
        selected_terms=terms[INSTRUMENT_ID],
        fee_schedule=fee_schedule(),
        source_coverage=operational_coverage,
        period_policy={"scope": SCOPE},
        safety_buffer_ns=60 * NS,
        cut=base,
        require_verified_venue=True,
    )
    current_range, prior_range = _build_range_versions(
        day,
        previous,
        current_end=current_end,
        prior_publication=prior_publication,
        definition=selected_definition,
    )
    context = freeze_e0_ranges(
        selected_day=admission,
        range_06_09=current_range,
        prior_rth=prior_range,
        prior_selection=admission.selection_evidence,
        cut=base,
    )
    events = _native_events(day, base=base, quote_path=quote_path)
    complete_intervals = ((base - 120 * NS, base + 17 * 60 * NS),)
    source_receipt = NativeCoverageReceipt.from_events(
        events,
        source_id=events[0].address.dataset_id,
        schema_version=events[0].address.schema_version,
        instrument_id=INSTRUMENT_ID,
        complete_intervals=complete_intervals,
        source_order_known=True,
        coverage_version=f"coverage-{day.isoformat()}-v1",
    )
    coverage = {
        "complete_intervals": complete_intervals,
        "version": f"coverage-{day.isoformat()}-v1",
        "source_receipt": source_receipt,
        "source_order_known": source_receipt.source_order_known,
        "source_versions": source_receipt.source_versions,
    }
    receipts = tuple(
        {
            "event_id": event.id,
            "address_id": event.address.id,
            "source_version": event.address.source_version,
            "sequence": event.provider_sequence,
            "row": event.address.row,
            "known_at": event.clocks.known_at,
        }
        for event in events
    )
    return SharedDaySource(
        day=day,
        base_cut=base,
        cuts=(base - 60 * NS, base, base + 60 * NS),
        canonical_events=events,
        coverage=coverage,
        range_06_09=context.range_06_09,
        prior_rth=context.prior_rth,
        range_versions=(current_range, prior_range),
        context=context,
        admission=admission,
        operational=operational,
        cash_day=cash_day,
        published_cash_day=published_cash_day,
        venue_boundary=venue_boundary,
        universe=universe,
        definitions=definitions,
        volumes=volumes,
        session_sequence=sequence,
        objects=context.objects,
        source_receipts=receipts,
        minute_history=_minute_history(day, base),
        quote_path=quote_path,
        source_manifest=source_manifest,
        terms=terms,
        operational_coverage=operational_coverage,
    )


def make_run_day(day: date | str, *, quote_path: str = "comparator_down") -> E0RunDay:
    """Build one actual typed ``E0RunDay`` for runner/learning controls.

    ``quote_path`` selects only the retained native future path: comparator
    down, quiet, or the up/down paths used by the connected target heads.
    """
    if isinstance(day, str):
        day = date.fromisoformat(day)
    if type(day) is not date:
        raise TypeError("E0 fixture day must be a civil date")
    return _build_day(day, quote_path=quote_path).run_day


def make_source_day(day: date | str, *, quote_path: str = "comparator_down") -> SharedDaySource:
    """Return the retained typed source facts for one requested golden date."""
    if isinstance(day, str):
        day = date.fromisoformat(day)
    if type(day) is not date:
        raise TypeError("E0 fixture day must be a civil date")
    return _build_day(day, quote_path=quote_path)


def connected_run_days() -> tuple[E0RunDay, ...]:
    """Return the two-date-per-year connected training/selection controls."""
    rows = []
    for year in (2022, 2023, 2024):
        rows.extend((make_run_day(date(year, 6, 1), quote_path="learning_up"),
                     make_run_day(date(year, 6, 2), quote_path="learning_down")))
    rows.extend((make_run_day(date(2025, 6, 3), quote_path="learning_up"),
                 make_run_day(date(2025, 6, 4), quote_path="learning_down")))
    return tuple(rows)


def shared_comparator_source() -> SharedComparatorSource:
    """Return the exact two-day native comparator source used by E0 replay."""
    days = (
        _build_day(date(2025, 6, 3), quote_path="comparator_down"),
        _build_day(date(2025, 6, 4), quote_path="comparator_quiet"),
    )
    return SharedComparatorSource(
        per_day=days,
        canonical_events=tuple(event for day in days for event in day.canonical_events),
        cuts=tuple(cut for day in days for cut in day.cuts),
        aliases={"a": "06_09:eq", "b": "prior_rth:close", "c": "prior_rth:high"},
        source_receipts=tuple(receipt for day in days for receipt in day.source_receipts),
    )


__all__ = [
    "SharedDaySource", "SharedComparatorSource", "Int01AdmissionSource", "fee_schedule",
    "make_int01_source", "make_run_day", "make_source_day",
    "connected_run_days", "shared_comparator_source",
]
