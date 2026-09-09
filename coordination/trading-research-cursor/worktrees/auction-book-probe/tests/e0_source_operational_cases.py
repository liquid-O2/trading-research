"""Independent operational checks for the frozen E0 source cases.

The integration test module contains the broad source fixture checks.  This
module keeps the seven operational case IDs and their causal assertions in a
small helper that can be called by wrappers in that module.  The helpers build
the native rows themselves, retain a :class:`NativeCoverageReceipt`, and then
use the public source bridge.  Expected values are frozen literals from
``tests/golden/e0_integration_v1.json``; the golden file is consulted only to
make sure that every case and variant remains declared.

Each ``check_*`` function accepts a ``unittest.TestCase`` (or an object with
the same assertion methods) and returns ``None``.  The parent integration
tests can therefore delegate to these checks without duplicating fixtures or
weakening the assertions to comparisons against the expected JSON object.
"""

from __future__ import annotations

from datetime import date, time
from decimal import Decimal
from hashlib import sha256
import json
from pathlib import Path
import tempfile

from trading_research.data.events import (
    Flags,
    LatencyScenario,
    SourceAddress,
    UNDEF_PRICE,
    normalize_mbp,
)
from trading_research.errors import ContractError, DependencyUnavailable
from trading_research.execution.accounting import AccountingLedger, TradingFill
from trading_research.execution.costs import FeeSchedule
from trading_research.execution.venue import FillScenario
from trading_research.experiments.e0.admission import separate_scope_manifests
from trading_research.experiments.e0.source_bridge import (
    NativeCoverageReceipt,
    reconcile_trade_streams,
    venue_path_from_mbp,
)
from trading_research.foundations.cash_calendar import (
    CashCalendar,
    VenueBoundary,
    e0_window,
)
from trading_research.foundations.calendar import local_timestamp
from trading_research.foundations.time import timestamp

from e0_source_fixtures import fee_schedule, make_source_day, shared_comparator_source


NS = 1_000_000_000
NY = "America/New_York"
INSTRUMENT = "1002"
ROOT = "NQ"
SOURCE_VERSION = "mbp-1-synthetic-v1"
SCHEMA_VERSION = "mbp-native-v1"
GOLDEN_PATH = Path(__file__).with_name("golden") / "e0_integration_v1.json"

# Keep every frozen operational ID visible to static reviewers and callers.
FROZEN_CASE_IDS = (
    "E0-INT-04-F01",
    "E0-INT-04-F02",
    "E0-INT-04-F03",
    "E0-INT-12-F01",
    "E0-INT-12-F02",
    "E0-INT-12-F03",
    "E0-SCOPE-F01",
)


def _declared_case_ids() -> tuple[str, ...]:
    with GOLDEN_PATH.open(encoding="utf-8") as handle:
        payload = json.load(handle)
    return tuple(row["case_id"] for row in payload["cases"])


def _require_case(testcase, case_id: str, *, variants: tuple[str, ...] = ()) -> None:
    """Check declaration identity without deriving assertions from expected JSON."""
    declared = _declared_case_ids()
    testcase.assertEqual(set(FROZEN_CASE_IDS), set(FROZEN_CASE_IDS) & set(declared))
    testcase.assertIn(case_id, declared)
    if variants:
        with GOLDEN_PATH.open(encoding="utf-8") as handle:
            payload = json.load(handle)
        case = next(row for row in payload["cases"] if row["case_id"] == case_id)
        testcase.assertEqual(
            {row["id"] for row in case.get("variants", ())},
            set(variants),
        )


def _native_event(
    *,
    row: int,
    sequence: int | None,
    event_at: int,
    action: str,
    bid_ticks: int,
    ask_ticks: int,
    size: int,
    side: str,
    flags: int,
    trade_ticks: int | None = None,
    event_price_ticks: int | None = None,
    unpriced: bool = False,
    bid_size: int = 5,
    ask_size: int = 7,
):
    """Build one exact native MBP row through the public normalizer."""
    timestamp(event_at)
    if unpriced and not action == "T":
        raise ContractError("only a trade row can carry the native undefined-price sentinel")
    if unpriced:
        native_price = UNDEF_PRICE
    elif event_price_ticks is not None:
        native_price = event_price_ticks
    elif action == "T":
        native_price = bid_ticks if trade_ticks is None else trade_ticks
    else:
        native_price = bid_ticks
    address = SourceAddress(
        dataset_id="e0-frozen-native-mbp-1",
        acquisition_version="e0-frozen-acquisition-v1",
        relative_path="native/2024-06-03.mbp-1",
        container_version=SOURCE_VERSION,
        partition="2024-06-03",
        row=row,
        schema_version=SCHEMA_VERSION,
    )
    fields = {
        "ts_event": event_at,
        "ts_recv": event_at + 25 * 1_000_000,
        "action": action,
        "side": side,
        "price": native_price * 250_000_000 if native_price != UNDEF_PRICE else UNDEF_PRICE,
        "size": size,
        "flags": flags,
        "instrument_id": int(INSTRUMENT),
        "bid_px_00": bid_ticks * 250_000_000,
        "ask_px_00": ask_ticks * 250_000_000,
        "bid_sz_00": bid_size,
        "ask_sz_00": ask_size,
        "publisher_id": 1,
        "sequence": sequence,
        "depth": 0,
    }
    return normalize_mbp(
        fields,
        address,
        native=True,
        scenario=LatencyScenario("e0-provider-receipt-v1", "provider_received", 0, 0),
    )


def _coverage(
    events: tuple,
    *,
    interval_start: int,
    interval_end: int,
    version: str,
    source_order_known: bool,
    recovery_event_ids: tuple[str, ...] = (),
    recovery_certificate_ids: tuple[str, ...] = (),
) -> dict:
    receipt = NativeCoverageReceipt.from_events(
        events,
        source_id="e0-frozen-native-mbp-1",
        schema_version=SCHEMA_VERSION,
        instrument_id=INSTRUMENT,
        complete_intervals=((interval_start, interval_end),),
        source_order_known=source_order_known,
        recovery_event_ids=recovery_event_ids,
        recovery_certificate_ids=recovery_certificate_ids,
        coverage_version=version,
    )
    return {
        "complete_intervals": receipt.complete_intervals,
        "version": version,
        "source_receipt": receipt,
        "source_order_known": source_order_known,
        "source_versions": receipt.source_versions,
    }


def _f01_events(base: int) -> tuple:
    return (
        _native_event(
            row=10,
            sequence=10,
            event_at=base,
            action="A",
            bid_ticks=72000,
            ask_ticks=72004,
            size=5,
            side="B",
            flags=0,
            bid_size=5,
            ask_size=7,
        ),
        _native_event(
            row=11,
            sequence=11,
            event_at=base,
            action="A",
            bid_ticks=72000,
            ask_ticks=72004,
            size=7,
            side="A",
            flags=0,
            bid_size=5,
            ask_size=7,
            event_price_ticks=72004,
        ),
        _native_event(
            row=12,
            sequence=12,
            event_at=base + 100 * 1_000_000,
            action="T",
            bid_ticks=72000,
            ask_ticks=72004,
            size=1,
            side="B",
            flags=0,
            trade_ticks=72004,
            bid_size=5,
            ask_size=7,
        ),
        _native_event(
            row=13,
            sequence=13,
            event_at=base + 125 * 1_000_000,
            action="M",
            bid_ticks=72000,
            ask_ticks=72004,
            size=6,
            side="A",
            flags=0,
            bid_size=5,
            ask_size=6,
            event_price_ticks=72004,
        ),
    )


def _path_for_events(source, events: tuple, coverage: dict, *, latency_id: str):
    return venue_path_from_mbp(
        canonical_events=events,
        selected_instrument=source.admission,
        coverage=coverage,
        latency_scenario=LatencyScenario(latency_id, "event", 250 * 1_000_000, 0),
        market_state="continuous",
        source_manifest={"source_version": SOURCE_VERSION},
        tick_size=source.operational.terms.tick_size,
    )


def _marketable_scenario(source, path, scenario_id: str) -> FillScenario:
    return FillScenario(
        scenario_id,
        0,
        "venue_first",
        "touch_quote_scenario",
        path.coverage_version,
        source.operational.fees.version,
    )


def _project_same_time_uncertainty(path, *, at: int, public_reason: str) -> dict:
    """Retain the public reason and explicitly map it to the frozen wording."""
    tied = tuple(quote for quote in path.quotes if quote.event_at == at)
    if (
        public_reason != "same-time source quote ordering is unproved"
        or path.coverage.source_order_known
        or len(tied) < 2
        or any(quote.sequence is not None for quote in tied)
    ):
        raise AssertionError("same-time uncertainty projection lacks source-order evidence")
    return {
        "public_reason": public_reason,
        "evidence": {
            "source_order_known": path.coverage.source_order_known,
            "same_time_sequences": tuple(quote.sequence for quote in tied),
            "venue_quote": None,
        },
        "frozen_reason": "same-time source order is unproved; do not pick a last quote",
    }


def _project_book_gap_execution(path, fill) -> dict:
    """Map the public uncertain fill to the frozen blocked-execution claim."""
    if (
        fill.status != "uncertain"
        or path.quality["book_invalid_rows"] < 1
        or path.recovery_certificates
    ):
        raise AssertionError("book-gap execution projection lacks invalid-book evidence")
    return {
        "public_status": fill.status,
        "public_reason": fill.reason,
        "evidence": {
            "book_invalid_rows": path.quality["book_invalid_rows"],
            "recovery_certificates": path.recovery_certificates,
        },
        "frozen_reason": "F_MAYBE_BAD_BOOK invalidates trusted BBO pending RecoveryCertificate",
    }


def check_int04_f01(testcase) -> None:
    """INT04-F01: native rows preserve venue and strategy clocks."""
    _require_case(testcase, "E0-INT-04-F01")
    source = make_source_day("2024-06-03")
    base = 1717421460000000000
    events = _f01_events(base)
    coverage = _coverage(
        events,
        interval_start=1717421459000000000,
        interval_end=1717421461000000000,
        version="coverage-v1",
        source_order_known=True,
    )
    path = _path_for_events(source, events, coverage, latency_id="e0-int04-f01-250ms")

    testcase.assertEqual(path.instrument, INSTRUMENT)
    testcase.assertEqual(len(path.quotes), 3)
    testcase.assertEqual(len(path.trades), 1)
    testcase.assertEqual(path.source_row_count, 4)
    testcase.assertEqual(path.coverage.source_order_known, True)
    testcase.assertEqual(path.coverage.coverage_version, "coverage-v1")
    testcase.assertEqual(len(path.complete_intervals), 1)
    testcase.assertEqual(path.quality["event_count"], 4)
    testcase.assertEqual(path.quality["trade_volume"], 1)
    testcase.assertEqual(path.quality["flow_complete"], True)
    testcase.assertEqual(path.quality["bad_receive_rows"], 0)
    testcase.assertEqual(path.receipt_latency_claims, ())
    testcase.assertEqual(
        tuple(event.clocks.event_at for event in events),
        (
            1717421460000000000,
            1717421460000000000,
            1717421460100000000,
            1717421460125000000,
        ),
    )
    testcase.assertEqual(
        tuple(event.price for event in events),
        (Decimal("18000"), Decimal("18001"), Decimal("18001"), Decimal("18001")),
    )
    testcase.assertEqual(
        dict(path.known_clocks),
        {
            events[0].id: 1717421460250000000,
            events[1].id: 1717421460250000000,
            events[2].id: 1717421460350000000,
            events[3].id: 1717421460375000000,
        },
    )
    testcase.assertTrue(all(int(event.flags) == 0 for event in events))
    testcase.assertTrue(all(not event.flags & Flags.LAST for event in events))
    testcase.assertEqual(path.trades[0].quantity, 1)
    testcase.assertEqual(path.trades[0].ticks, 72004)
    testcase.assertEqual(path.trades[0].event_at, base + 100 * 1_000_000)
    testcase.assertEqual(path.trades[0].aggressor, 1)

    venue_quote, reason = path.quote_at(
        base, clock="venue", same_time_ordering="venue_first"
    )
    testcase.assertIsNone(reason)
    testcase.assertIsNotNone(venue_quote)
    testcase.assertEqual(venue_quote.event_at, base)
    testcase.assertEqual(venue_quote.bid, 72000)
    testcase.assertEqual(venue_quote.ask, 72004)
    testcase.assertEqual(venue_quote.bid_size, 5)
    testcase.assertEqual(venue_quote.ask_size, 7)
    testcase.assertEqual(venue_quote.book_valid, True)
    testcase.assertEqual(venue_quote.market_state, "continuous")

    strategy_known_at = 1717421460250000000
    strategy_quote, reason = path.quote_at(strategy_known_at, clock="strategy")
    testcase.assertIsNone(reason)
    testcase.assertIsNotNone(strategy_quote)
    testcase.assertEqual(strategy_quote.known_at, strategy_known_at)
    testcase.assertEqual(strategy_quote.event_at, base)

    order_arrival_at = 1717421460500000000
    arrival_quote, reason = path.quote_at(
        order_arrival_at, clock="venue", same_time_ordering="venue_first"
    )
    testcase.assertIsNone(reason)
    testcase.assertIsNotNone(arrival_quote)
    testcase.assertEqual(arrival_quote.event_at, base + 125 * 1_000_000)
    testcase.assertEqual(arrival_quote.bid, 72000)
    testcase.assertEqual(arrival_quote.ask, 72004)
    testcase.assertEqual(arrival_quote.bid_size, 5)
    testcase.assertEqual(arrival_quote.ask_size, 6)
    testcase.assertEqual(arrival_quote.book_valid, True)
    testcase.assertEqual(arrival_quote.known_at, 1717421460375000000)
    testcase.assertGreater(order_arrival_at, arrival_quote.event_at)

    scenario = FillScenario(
        "e0-int04-f01-marketable",
        0,
        "venue_first",
        "touch_quote_scenario",
        path.coverage_version,
        source.operational.fees.version,
    )
    fill = path.marketable(
        order_id="e0-int04-f01-order",
        side=1,
        arrival_at=order_arrival_at,
        scenario=scenario,
    )
    testcase.assertEqual(fill.status, "filled_under_scenario")
    testcase.assertEqual(fill.at, order_arrival_at)
    testcase.assertEqual(fill.price_ticks, 72004)
    testcase.assertEqual(fill.quantity, 1)
    testcase.assertEqual(fill.side, 1)
    testcase.assertEqual(fill.source_event_id, arrival_quote.id)


def _f02_bad_events(base: int) -> tuple:
    return (
        _native_event(
            row=20,
            sequence=20,
            event_at=base,
            action="M",
            bid_ticks=72000,
            ask_ticks=72004,
            size=0,
            side="B",
            flags=int(Flags.LAST | Flags.MAYBE_BAD_BOOK),
            bid_size=5,
            ask_size=7,
        ),
        _native_event(
            row=22,
            sequence=22,
            event_at=base + 50 * 1_000_000,
            action="T",
            bid_ticks=72000,
            ask_ticks=72004,
            size=2,
            side="B",
            flags=int(Flags.LAST | Flags.MAYBE_BAD_BOOK),
            trade_ticks=72004,
            bid_size=5,
            ask_size=7,
        ),
    )


def check_int04_f02(testcase) -> None:
    """INT04-F02: bad-book flags block BBO use until certified recovery."""
    _require_case(
        testcase,
        "E0-INT-04-F02",
        variants=("book-gap-132", "snapshot-168-after-recovery"),
    )
    source = make_source_day("2024-06-03")
    base = 1717421460000000000
    bad_events = _f02_bad_events(base)
    bad_coverage = _coverage(
        bad_events,
        interval_start=base - 100 * 1_000_000,
        interval_end=base + 1_000 * 1_000_000,
        version="coverage-int04-f02-gap-v1",
        source_order_known=True,
    )
    blocked = _path_for_events(
        source, bad_events, bad_coverage, latency_id="e0-int04-f02-gap-250ms"
    )

    testcase.assertEqual(int(Flags.LAST | Flags.MAYBE_BAD_BOOK), 132)
    testcase.assertEqual(
        tuple(event.clocks.event_at for event in bad_events),
        (1717421460000000000, 1717421460050000000),
    )
    testcase.assertEqual(
        tuple(event.price for event in bad_events),
        (Decimal("18000"), Decimal("18001")),
    )
    testcase.assertEqual(tuple(event.size for event in bad_events), (0, 2))
    testcase.assertEqual(tuple(int(event.flags) for event in bad_events), (132, 132))
    testcase.assertTrue(any(flags & int(Flags.MAYBE_BAD_BOOK) for _, flags in blocked.raw_flags))
    testcase.assertTrue(any(flags & int(Flags.LAST) for _, flags in blocked.raw_flags))
    testcase.assertFalse(blocked.quality["flow_complete"])
    testcase.assertEqual(blocked.quality["trade_volume"], 2)
    testcase.assertEqual(len(blocked.trades), 1)
    testcase.assertEqual(blocked.trades[0].quantity, 2)
    testcase.assertEqual(blocked.trades[0].aggressor, 1)
    testcase.assertTrue(any(not quote.book_valid for quote in blocked.quotes))
    testcase.assertEqual(blocked.recovery_certificates, ())
    blocked_quote, blocked_reason = blocked.quote_at(
        base + 1, clock="venue", same_time_ordering="venue_first"
    )
    testcase.assertIsNone(blocked_quote)
    testcase.assertIn("invalid", blocked_reason)
    blocked_fill = blocked.marketable(
        order_id="e0-int04-f02-blocked-order",
        side=1,
        arrival_at=base + 1,
        scenario=_marketable_scenario(source, blocked, "e0-int04-f02-blocked"),
    )
    blocked_projection = _project_book_gap_execution(blocked, blocked_fill)
    testcase.assertEqual(blocked_projection["public_status"], "uncertain")
    testcase.assertEqual(
        blocked_projection["frozen_reason"],
        "F_MAYBE_BAD_BOOK invalidates trusted BBO pending RecoveryCertificate",
    )

    snapshot = _native_event(
        row=21,
        sequence=21,
        event_at=base + 1_500 * 1_000_000,
        action="A",
        bid_ticks=72000,
        ask_ticks=72004,
        size=5,
        side="B",
        flags=int(Flags.LAST | Flags.SNAPSHOT | Flags.BAD_TS_RECV),
        bid_size=5,
        ask_size=6,
    )
    recovery_events = (bad_events[0], snapshot)
    recovery_coverage = _coverage(
        recovery_events,
        interval_start=base - 100 * 1_000_000,
        interval_end=base + 2_000 * 1_000_000,
        version="coverage-int04-f02-recovery-v1",
        source_order_known=True,
        recovery_event_ids=(snapshot.id,),
        recovery_certificate_ids=("e0-int04-recovery-1",),
    )
    from trading_research.data.book import RecoveryCertificate

    certificate = RecoveryCertificate(
        instrument_id=int(INSTRUMENT),
        invalidating_event_id=bad_events[0].id,
        recovery_event_id=snapshot.id,
        method="documented_full_snapshot",
        evidence_id="e0-int04-recovery-1",
    )
    recovered = venue_path_from_mbp(
        canonical_events=recovery_events,
        selected_instrument=source.admission,
        coverage=recovery_coverage,
        recovery_certificates=(certificate,),
        latency_scenario=LatencyScenario(
            "e0-int04-f02-recovery-250ms", "event", 250 * 1_000_000, 0
        ),
        market_state="continuous",
        source_manifest={"source_version": SOURCE_VERSION},
        tick_size=source.operational.terms.tick_size,
    )
    testcase.assertEqual(int(Flags.LAST | Flags.SNAPSHOT | Flags.BAD_TS_RECV), 168)
    testcase.assertEqual(snapshot.clocks.event_at, 1717421461500000000)
    testcase.assertEqual(snapshot.price, Decimal("18000"))
    testcase.assertEqual(snapshot.size, 5)
    testcase.assertEqual(int(snapshot.flags), 168)
    testcase.assertEqual(recovered.quality["recovered_rows"], 1)
    testcase.assertEqual(recovered.quality["snapshot_rows"], 1)
    testcase.assertEqual(recovered.quality["bad_receive_rows"], 1)
    testcase.assertFalse(recovered.quality["flow_complete"])
    testcase.assertEqual(recovered.coverage.recovery_complete, True)
    testcase.assertEqual(recovered.recovery_certificates, (certificate,))
    testcase.assertEqual(
        recovered.receipt_latency_claims,
        ((snapshot.id, "uncertain_due_to_F_BAD_TS_RECV"),),
    )
    testcase.assertTrue(snapshot.flags & Flags.BAD_TS_RECV)
    testcase.assertEqual(
        {
            "bad_receive_rows": recovered.quality["bad_receive_rows"],
            "receipt_latency_claim": "uncertain_due_to_F_BAD_TS_RECV",
        },
        {
            "bad_receive_rows": 1,
            "receipt_latency_claim": "uncertain_due_to_F_BAD_TS_RECV",
        },
    )
    recovered_quote, reason = recovered.quote_at(
        snapshot.clocks.event_at + 1, clock="venue", same_time_ordering="venue_first"
    )
    testcase.assertIsNone(reason)
    testcase.assertIsNotNone(recovered_quote)
    testcase.assertEqual(recovered_quote.book_valid, True)
    testcase.assertEqual(recovered_quote.ask_size, 6)
    testcase.assertEqual(recovered_quote.market_state, "continuous")
    recovered_fill = recovered.marketable(
        order_id="e0-int04-f02-recovered-order",
        side=1,
        arrival_at=snapshot.clocks.event_at + 1,
        scenario=_marketable_scenario(source, recovered, "e0-int04-f02-recovered"),
    )
    testcase.assertEqual(recovered_fill.status, "filled_under_scenario")
    testcase.assertEqual(recovered_fill.price_ticks, 72004)
    testcase.assertEqual(recovered_fill.quantity, 1)
    testcase.assertEqual(recovered_fill.source_event_id, snapshot.id)


def check_int04_f03(testcase) -> None:
    """INT04-F03: embedded/standalone trade identity and same-time order."""
    _require_case(
        testcase,
        "E0-INT-04-F03",
        variants=(
            "duplicate-embedded-standalone",
            "distinct-standalone-row",
            "same-time-unordered-quotes",
            "unpriced-flow",
        ),
    )
    source = make_source_day("2024-06-03")
    base = 1717421460000000000
    same_time = base + NS
    quotes = (
        _native_event(
            row=1,
            sequence=None,
            event_at=same_time,
            action="A",
            bid_ticks=72000,
            ask_ticks=72004,
            size=1,
            side="N",
            flags=0,
            bid_size=5,
            ask_size=7,
        ),
        _native_event(
            row=2,
            sequence=None,
            event_at=same_time,
            action="A",
            bid_ticks=71999,
            ask_ticks=72003,
            size=1,
            side="N",
            flags=0,
            bid_size=5,
            ask_size=7,
        ),
    )
    embedded = _native_event(
        row=30,
        sequence=30,
        event_at=base + 100 * 1_000_000,
        action="T",
        bid_ticks=72000,
        ask_ticks=72004,
        size=1,
        side="B",
        flags=0,
        trade_ticks=72004,
    )
    unpriced = _native_event(
        row=32,
        sequence=32,
        event_at=base + 300 * 1_000_000,
        action="T",
        bid_ticks=72000,
        ask_ticks=72004,
        size=1,
        side="N",
        flags=0,
        unpriced=True,
    )
    events = quotes + (embedded, unpriced)
    coverage = _coverage(
        events,
        interval_start=base - 100 * 1_000_000,
        interval_end=base + 2_000 * 1_000_000,
        version="coverage-int04-f03-v1",
        source_order_known=False,
    )
    path = _path_for_events(source, events, coverage, latency_id="e0-int04-f03-250ms")
    testcase.assertEqual(len(path.trades), 1)
    testcase.assertEqual(path.trades[0].quantity, 1)
    testcase.assertEqual(path.quality["trade_volume"], 2)
    testcase.assertEqual(path.quality["unpriced_flow"], 1)
    testcase.assertEqual(path.quality["unknown_side_volume"], 1)
    testcase.assertEqual(path.coverage.source_order_known, False)

    standalone = (
        {
            "id": "trade-30-duplicate",
            "instrument_id": 1002,
            "event_at": base + 100 * 1_000_000,
            "price_ticks": 72004,
            "size": 1,
            "embedded_row_id": 30,
        },
        {
            "id": "trade-31-distinct",
            "instrument_id": 1002,
            "event_at": base + 200 * 1_000_000,
            "price_ticks": 72005,
            "size": 2,
            "reconciliation_role": "alternate_stream_only",
        },
        {
            "id": "trade-32-unpriced",
            "instrument_id": 1002,
            "event_at": base + 300 * 1_000_000,
            "price_ticks": None,
            "size": 1,
            "reconciliation_role": "unknown_flow_only",
        },
    )
    reconciliation = reconcile_trade_streams(
        primary=path.trades,
        standalone=standalone,
        canonical_events=path.canonical_events,
        tick_size=source.operational.terms.tick_size,
    )
    testcase.assertEqual(reconciliation.primary_volume, 1)
    testcase.assertEqual(reconciliation.duplicate_volume, 1)
    testcase.assertEqual(reconciliation.distinct_volume, 2)
    testcase.assertEqual(reconciliation.unknown_volume, 1)
    testcase.assertEqual(reconciliation.duplicate_standalone[0]["id"], "trade-30-duplicate")
    testcase.assertEqual(reconciliation.distinct_standalone[0]["id"], "trade-31-distinct")
    testcase.assertEqual(reconciliation.unknown_unpriced[0]["id"], "trade-32-unpriced")
    priced_without_dedup = reconciliation.primary_volume + reconciliation.distinct_volume + reconciliation.duplicate_volume
    testcase.assertEqual(priced_without_dedup, 4)
    testcase.assertEqual(path.trades[0].event_at, base + 100 * 1_000_000)

    quote, reason = path.quote_at(
        same_time + 1, clock="venue", same_time_ordering="order_first"
    )
    testcase.assertIsNone(quote)
    same_time_projection = _project_same_time_uncertainty(
        path, at=same_time, public_reason=reason
    )
    testcase.assertEqual(
        same_time_projection["public_reason"],
        "same-time source quote ordering is unproved",
    )
    testcase.assertEqual(
        same_time_projection["evidence"],
        {
            "source_order_known": False,
            "same_time_sequences": (None, None),
            "venue_quote": None,
        },
    )
    testcase.assertEqual(
        same_time_projection["frozen_reason"],
        "same-time source order is unproved; do not pick a last quote",
    )
    testcase.assertEqual(path.canonical_events[-1].price, None)
    testcase.assertEqual(path.canonical_events[-1].aggressor, None)


def _cash_day_and_boundary(day: date, required_flat_at: int, scope: str):
    calendar = CashCalendar(Path(__file__).resolve().parents[1] / "configs" / "cash-rth-calendar.json")
    cut = local_timestamp(day, time(0), NY)
    cash_day = calendar.resolve(day, cut=cut)
    boundary = VenueBoundary(
        day,
        ROOT,
        cash_day.open_at,
        required_flat_at,
        required_flat_at,
        cut,
        "cme-venue-boundary-e0-operational-v1",
        scope,
    )
    return cash_day, boundary, cut


def check_int12_f01(testcase) -> None:
    """INT12-F01: DST and the earliest certified boundary fix the E0 window."""
    _require_case(
        testcase,
        "E0-INT-12-F01",
        variants=("normal-edt", "spring-dst", "fall-dst", "early-boundary", "cash-only"),
    )
    safety = 60 * NS
    normal_day = date(2024, 6, 3)
    normal_cash, normal_boundary, normal_cut = _cash_day_and_boundary(
        normal_day, 1717444800000000000, "verified_venue_schedule"
    )
    normal = e0_window(
        normal_cash,
        boundary=normal_boundary,
        cut=normal_cut,
        safety_buffer_ns=safety,
        require_verified_venue=True,
    )
    testcase.assertEqual(normal["entry_start"], 1717421460000000000)
    testcase.assertEqual(normal["entry_end"], 1717443000000000000)
    testcase.assertEqual(normal["flatten_send_at"], 1717444500000000000)
    testcase.assertEqual(normal["required_flat_at"], 1717444800000000000)
    testcase.assertEqual(normal["safety_buffer_ns"], safety)
    testcase.assertEqual(normal["boundary_scope"], "verified_venue_schedule")

    spring_day = date(2024, 3, 11)
    spring_cash, spring_boundary, spring_cut = _cash_day_and_boundary(
        spring_day, 1710187200000000000, "verified_venue_schedule"
    )
    spring = e0_window(
        spring_cash,
        boundary=spring_boundary,
        cut=spring_cut,
        safety_buffer_ns=safety,
        require_verified_venue=True,
    )
    testcase.assertEqual(spring["entry_start"], 1710163860000000000)
    testcase.assertEqual(spring["entry_end"], 1710185400000000000)

    fall_day = date(2024, 11, 4)
    fall_cash, fall_boundary, fall_cut = _cash_day_and_boundary(
        fall_day, 1730754000000000000, "verified_venue_schedule"
    )
    fall = e0_window(
        fall_cash,
        boundary=fall_boundary,
        cut=fall_cut,
        safety_buffer_ns=safety,
        require_verified_venue=True,
    )
    testcase.assertEqual(fall["entry_start"], 1730730660000000000)
    testcase.assertEqual(fall["entry_end"], 1730752200000000000)

    early_cash, early_boundary, early_cut = _cash_day_and_boundary(
        normal_day, 1717443900000000000, "verified_venue_schedule"
    )
    early = e0_window(
        early_cash,
        boundary=early_boundary,
        cut=early_cut,
        safety_buffer_ns=safety,
        require_verified_venue=True,
    )
    testcase.assertEqual(early["flatten_send_at"], 1717443840000000000)
    testcase.assertEqual(early["required_flat_at"], 1717443900000000000)
    testcase.assertEqual(early["entry_end"], 1717443000000000000)

    cash_only = VenueBoundary(
        normal_day,
        ROOT,
        normal_cash.open_at,
        normal_cash.close_at,
        normal_cash.close_at,
        normal_cut,
        "cash-only-boundary-v1",
        "synthetic_research_window",
    )
    with testcase.assertRaises(DependencyUnavailable) as raised:
        e0_window(
            normal_cash,
            boundary=cash_only,
            cut=normal_cut,
            safety_buffer_ns=safety,
            require_verified_venue=True,
        )
    testcase.assertEqual(
        str(raised.exception),
        "cash RTH alone cannot certify a futures venue boundary",
    )


def check_int12_f02(testcase) -> None:
    """INT12-F02: complete positive itemized fees are required for replay."""
    _require_case(
        testcase,
        "E0-INT-12-F02",
        variants=("fee-missing-routing", "fee-zero-commission", "fee-complete"),
    )
    complete = fee_schedule()
    testcase.assertEqual(complete.id, "fee-nq-synthetic-v1")
    testcase.assertEqual(complete.currency, "USD")
    testcase.assertEqual(
        complete.included,
        frozenset({"exchange", "regulatory", "clearing", "commission", "routing"}),
    )
    testcase.assertEqual(complete.fee("NQ"), Decimal("5.03"))
    testcase.assertEqual(complete.fee("NQ", sides=2), Decimal("10.06"))

    with testcase.assertRaises(DependencyUnavailable) as missing:
        FeeSchedule(
            complete.id,
            complete.connection,
            complete.account_product,
            complete.currency,
            complete.per_side,
            complete.source_urls,
            complete.verified_at,
            complete.evidence_hash,
            complete.historical_basis,
            frozenset({"exchange", "regulatory", "clearing", "commission"}),
        )
    testcase.assertEqual(
        str(missing.exception),
        "all transaction-cost categories must be resolved",
    )

    with testcase.assertRaises(ContractError) as zero:
        FeeSchedule(
            complete.id,
            complete.connection,
            complete.account_product,
            complete.currency,
            (("NQ", Decimal("0.00")), ("ES", Decimal("5.03"))),
            complete.source_urls,
            complete.verified_at,
            complete.evidence_hash,
            complete.historical_basis,
            complete.included,
        )
    testcase.assertEqual(
        str(zero.exception),
        "missing fees cannot become zero or duplicate product rows",
    )


def check_int12_f03(testcase) -> None:
    """INT12-F03: eligible flat/outage/halted dates stay in the denominator."""
    _require_case(testcase, "E0-INT-12-F03")
    source = make_source_day("2024-06-03")
    eligible = (
        "2024-06-03",
        "2024-06-04",
        "2024-06-05",
        "2024-06-06",
    )
    statuses = (
        ("2024-06-03", "complete"),
        ("2024-06-04", "flat"),
        ("2024-06-05", "outage"),
        ("2024-06-06", "halted"),
    )
    with tempfile.TemporaryDirectory(prefix="e0-int12-f03-") as directory:
        ledger = AccountingLedger(
            Path(directory) / "accounting.jsonl",
            account_id="e0-int12-synthetic-account",
            eligible_dates=eligible,
            eligibility_version="e0-int12-eligible-dates-v1",
            terms=((ROOT, source.operational.terms),),
            fees=source.operational.fees,
        )
        per_side = source.operational.fees.fee(ROOT)
        fee_version = source.operational.fees.version
        ledger.fill(
            TradingFill(
                "e0-int12-entry",
                ROOT,
                "2024-06-03",
                1717421461000000000,
                1,
                72000,
                per_side,
                fee_version,
                "e0-int12-fill-source-v1",
            )
        )
        ledger.fill(
            TradingFill(
                "e0-int12-exit",
                ROOT,
                "2024-06-03",
                1717421462000000000,
                -1,
                72010,
                per_side,
                fee_version,
                "e0-int12-fill-source-v1",
            )
        )
        for index, (trading_date, status) in enumerate(statuses):
            ledger.day_status(
                trading_date=trading_date,
                at=1717421463000000000 + index,
                status=status,
                evidence_version=f"e0-int12-status-{status}-v1",
            )
        report = ledger.report()

    testcase.assertEqual(report["eligible_day_count"], 4)
    testcase.assertEqual(tuple(report["days"]), eligible)
    testcase.assertEqual(
        tuple(report["days"][day]["status"] for day in eligible),
        tuple(status for _, status in statuses),
    )
    testcase.assertEqual(report["trading_net"], Decimal("39.94"))
    testcase.assertEqual(report["mean_net_per_eligible_day"], Decimal("39.94") / 4)
    testcase.assertEqual(report["business_net_cash"], Decimal("0.00"))
    testcase.assertEqual(report["violations"], [])
    testcase.assertEqual(report["complete"], True)


def check_scope_f01(testcase) -> None:
    """SCOPE-F01: historical and primary populations cannot be substituted."""
    _require_case(testcase, "E0-SCOPE-F01")
    binding = separate_scope_manifests(
        {
            "scope": "E0_historical_2022_2025_harness",
            "start_date": "2022-01-01",
            "end_date": "2025-12-31",
            "cohort": "hist-cohort-v1",
            "folds": "hist-folds-v1",
            "calibration": "hist-cal-v1",
            "population": "hist-pop-v1",
        },
        {
            "scope": "primary_model_2020_onward",
            "start_date": "2020-01-01",
            "cohort": "primary-cohort-v1",
            "folds": "primary-folds-v1",
            "calibration": "primary-cal-v1",
            "population": "primary-pop-v1",
        },
    )
    testcase.assertEqual(binding.historical.scope, "E0_historical_2022_2025_harness")
    testcase.assertEqual(binding.primary.scope, "primary_model_2020_onward")
    testcase.assertNotEqual(binding.historical.scope, binding.primary.scope)
    testcase.assertEqual(binding.historical.start_date, date(2022, 1, 1))
    testcase.assertEqual(binding.primary.start_date, date(2020, 1, 1))
    testcase.assertEqual(binding.historical.end_date, date(2025, 12, 31))
    testcase.assertNotEqual(binding.historical.cohort_version, binding.primary.cohort_version)
    testcase.assertNotEqual(binding.historical.fold_version, binding.primary.fold_version)
    testcase.assertNotEqual(
        binding.historical.calibration_version,
        binding.primary.calibration_version,
    )
    testcase.assertNotEqual(
        binding.historical.population_version,
        binding.primary.population_version,
    )

    shared = shared_comparator_source()
    testcase.assertTrue(shared.source_versions)
    testcase.assertTrue(all(day.source_versions for day in shared.per_day))
    testcase.assertEqual(shared.selected_instrument_id, INSTRUMENT)
    testcase.assertTrue(all(day.admission.scope == binding.historical.scope for day in shared.per_day))

    # The source identity is independently retained in the exact native
    # address used by INT04; sharing that immutable source does not merge the
    # scope manifests above.
    native = _f01_events(1717421460000000000)
    testcase.assertEqual(
        tuple(dict.fromkeys(event.address.source_version for event in native)),
        (SOURCE_VERSION,),
    )
    testcase.assertTrue(all(event.raw_fields for event in native))
    native_receipt = _coverage(
        native,
        interval_start=1717421459000000000,
        interval_end=1717421461000000000,
        version="scope-shared-native-v1",
        source_order_known=True,
    )["source_receipt"]
    testcase.assertEqual(native_receipt.source_versions, (SOURCE_VERSION,))
    testcase.assertTrue(native_receipt.raw_bytes)
    testcase.assertEqual(
        native_receipt.raw_sha256,
        sha256(native_receipt.raw_bytes).hexdigest(),
    )

    with testcase.assertRaises(ContractError) as raised:
        binding.require_same(binding.historical.scope, binding.primary.scope)
    testcase.assertEqual(
        str(raised.exception),
        "historical E0 harness cannot silently substitute for the 2020-onward period",
    )


__all__ = [
    "FROZEN_CASE_IDS",
    "check_int04_f01",
    "check_int04_f02",
    "check_int04_f03",
    "check_int12_f01",
    "check_int12_f02",
    "check_int12_f03",
    "check_scope_f01",
]
