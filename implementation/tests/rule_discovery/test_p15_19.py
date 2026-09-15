"""P15-19 E0-E4 machinery. Synthetic fixtures are labelled. Native slice is descriptive only."""

from __future__ import annotations

from collections import Counter
from decimal import Decimal
from pathlib import Path
import json

import pytest

from trading_research.errors import ContractError
from trading_research.research.contracts.execution import ENTRY_WINDOW_NS, LATENCY_NS, net_dollars, net_points
from trading_research.research.contracts.outcomes import PriceBatch
from trading_research.research.contracts.types import Coverage, EvidenceRef, QuoteBatch
from trading_research.research.rule_discovery.exits import (
    JOBS_ROOT,
    MINUTE_NS,
    POLICIES,
    SLICE_DATES,
    ExitRecord,
    FrozenEntry,
    IncompleteExit,
    UnsupportedRecord,
    attempt_partial_exit,
    evaluate_entry,
    evaluate_entries,
    evaluate_policy,
    run_native_slice,
)

NS = 1_000_000_000
FILL = 10 * NS
PREP = Path("/workspace/.worktrees/p15-19-exits-prep/implementation/reports/research-work/P15-19/_prep")


def _ev(ns: int, name: str) -> EvidenceRef:
    return EvidenceRef("a" * 64, (name,), ns, ns, ns, Coverage.COMPLETE, ())


def _qb(ns: int, bid: str | Decimal, ask: str | Decimal | None = None, *, name: str | None = None) -> QuoteBatch:
    bid_d = Decimal(str(bid))
    ask_d = Decimal(str(ask if ask is not None else bid))
    token = name or f"q{ns}"
    return QuoteBatch(token, "NQ:x", ns, ns, bid_d, ask_d, 1, 1, False, (_ev(ns, token),))


def _with_fills(quotes: list[QuoteBatch]) -> list[QuoteBatch]:
    extra = [
        _qb(quote.available_at_ns + LATENCY_NS, quote.bid, quote.ask, name=f"{quote.batch_id}f")
        for quote in quotes
    ]
    return list(quotes) + extra


def _entry(**kwargs) -> FrozenEntry:
    body = dict(
        entry_id="e1",
        family="F",
        branch="b",
        side=1,
        fill_price=Decimal("100"),
        fill_at_ns=FILL,
        initial_stop=Decimal("99"),
        objective=Decimal("102"),
        source_deadline_ns=None,
        flatten_at_ns=FILL + 180 * MINUTE_NS,
    )
    body.update(kwargs)
    return FrozenEntry(**body)


def test_a01_outcomes_literal_target_first_long_and_short():
    quotes = _with_fills(
        [
            _qb(FILL + NS, "100.5"),
            _qb(FILL + 2 * NS, "102"),
            _qb(FILL + 3 * NS, "98.5"),
        ]
    )
    long_paired = evaluate_entry(_entry(), quotes)
    assert long_paired.entry_id == "e1"
    assert all(long_paired.records[p].entry_id == "e1" for p in POLICIES)
    e0 = long_paired.records["E0"]
    assert e0.reason == "objective"
    assert e0.complete is True
    short_quotes = _with_fills(
        [
            _qb(FILL + NS, "99.5"),
            _qb(FILL + 2 * NS, "98"),
            _qb(FILL + 3 * NS, "101.5"),
        ]
    )
    short = evaluate_entry(
        _entry(side=-1, initial_stop=Decimal("101"), objective=Decimal("98")),
        short_quotes,
    )
    assert short.records["E0"].reason == "objective"


def test_a01_same_batch_pessimistic_stop():
    quotes = _with_fills([_qb(FILL + NS, "100.5"), _qb(FILL + 2 * NS, "100.5")])
    trades = [
        PriceBatch(
            event_ns=FILL + 2 * NS,
            available_at_ns=FILL + 2 * NS,
            prices=(Decimal("98.5"), Decimal("102")),
            event_ids=("lo", "hi"),
        )
    ]
    e0 = evaluate_entry(_entry(), quotes, trades).records["E0"]
    assert e0.reason == "stop"


def test_a01_neither_then_time_exit():
    quotes = _with_fills(
        [
            _qb(FILL + NS, "100.5"),
            _qb(FILL + 2 * NS, "101.75"),
            _qb(FILL + 3 * NS, "99.25"),
            _qb(FILL + 30 * MINUTE_NS, "100.5"),
        ]
    )
    e1 = evaluate_entry(_entry(), quotes).records["E1"]
    assert e1.reason == "expiry"
    assert e1.reason not in {"objective", "stop"}


def test_a02_e4_does_not_peek_later_high():
    quotes = _with_fills(
        [
            _qb(FILL + NS, "105", name="arm"),
            _qb(FILL + 2 * NS, "103", name="mid"),
            _qb(FILL + 3 * NS, "100.00", name="dip"),
            _qb(FILL + 4 * NS, "130", name="late"),
        ]
    )
    entry = _entry(initial_stop=Decimal("95"), objective=Decimal("200"))
    e4 = evaluate_entry(entry, quotes).records["E4"]
    assert e4.reason == "trailing stop"
    assert e4.exit_at_ns < FILL + 4 * NS
    assert e4.exit_price != Decimal("130")
    assert all(item.trigger_batch_id != "late" for item in e4.stop_updates)
    peeked_points = net_points(
        side=1,
        entry=Decimal("100"),
        exit_price=Decimal("129.75"),
        commission=entry.round_trip_cost,
    )
    assert e4.net_points != peeked_points
    assert e4.stop_updates
    for item in e4.stop_updates:
        assert item.effective_available_at_ns > item.trigger_available_at_ns
        assert item.effective_after_batch_id != item.trigger_batch_id


def test_stop_update_names_effective_batch():
    quotes = _with_fills(
        [
            _qb(FILL + NS, "101.00", name="arm"),
            _qb(FILL + 2 * NS, "100.50", name="hold"),
            _qb(FILL + 3 * NS, "100.20", name="be"),
        ]
    )
    e3 = evaluate_entry(_entry(), quotes).records["E3"]
    assert isinstance(e3, ExitRecord)
    assert e3.stop_updates
    for item in e3.stop_updates:
        assert item.effective_available_at_ns > item.trigger_available_at_ns
        assert item.effective_after_batch_id != item.trigger_batch_id


def test_a01_break_even_does_not_loosen():
    quotes = _with_fills(
        [
            _qb(FILL + NS, "101.00", name="arm"),
            _qb(FILL + 2 * NS, "100.50", name="hold"),
            _qb(FILL + 3 * NS, "100.20", name="be"),
        ]
    )
    e3 = evaluate_entry(_entry(), quotes).records["E3"]
    assert e3.reason == "break-even stop"
    assert e3.stop_updates
    stops = [item.stop for item in e3.stop_updates]
    assert min(stops) >= Decimal("100.25")


def test_a03_fractional_partial_rejected():
    with pytest.raises(ContractError, match="fractional"):
        FrozenEntry(
            entry_id="x",
            family="F",
            branch="b",
            side=1,
            fill_price=Decimal("100"),
            fill_at_ns=FILL,
            initial_stop=Decimal("99"),
            objective=Decimal("102"),
            source_deadline_ns=None,
            flatten_at_ns=FILL + MINUTE_NS,
            quantity=2,
        )
    with pytest.raises(ContractError, match="fractional"):
        attempt_partial_exit(Decimal("0.5"))


def test_a04_undefined_r_unsupported_e3_e4():
    quotes = _with_fills([_qb(FILL + NS, "100.5"), _qb(FILL + 2 * NS, "102")])
    none_stop = evaluate_entry(_entry(initial_stop=None), quotes)
    equal_stop = evaluate_entry(_entry(initial_stop=Decimal("100")), quotes)
    for paired in (none_stop, equal_stop):
        assert isinstance(paired.records["E3"], UnsupportedRecord)
        assert paired.records["E3"].reason == "undefined_initial_r"
        assert isinstance(paired.records["E4"], UnsupportedRecord)
        assert isinstance(paired.records["E0"], ExitRecord)
        assert not isinstance(paired.records["E0"], UnsupportedRecord)
        assert paired.records["E0"].complete is True
        assert paired.records["E1"].complete is True
        assert paired.records["E2"].complete is True


def test_e0_missing_quote_is_incomplete_not_unsupported():
    rec = evaluate_policy(_entry(), "E0", [_qb(FILL + NS, "100.5")])
    assert isinstance(rec, IncompleteExit)
    assert rec.reason == "incomplete_no_quote"
    assert not isinstance(rec, UnsupportedRecord)


def test_e0_never_undefined_r_unsupported():
    quotes = _with_fills([_qb(FILL + NS, "100.5"), _qb(FILL + 2 * NS, "102")])
    paired = evaluate_entry(_entry(initial_stop=None), quotes)
    assert not isinstance(paired.records["E0"], UnsupportedRecord)
    assert paired.records["E0"].reason != "undefined_initial_r"
    with pytest.raises(ContractError, match="E3/E4"):
        UnsupportedRecord("E0", "e1")


def test_source_deadline_earlier_than_policy_expiry():
    deadline = FILL + 10 * MINUTE_NS
    quotes = _with_fills(
        [
            _qb(FILL + NS, "100.5"),
            _qb(deadline, "100.5", name="src"),
        ]
    )
    paired = evaluate_entry(_entry(source_deadline_ns=deadline), quotes)
    for policy_id in POLICIES:
        rec = paired.records[policy_id]
        assert rec.reason == "source deadline"


def test_account_day_close_ends_open_position():
    flatten = FILL + 5 * MINUTE_NS
    quotes = _with_fills(
        [
            _qb(FILL + NS, "100.5"),
            _qb(flatten, "100.5", name="flat"),
        ]
    )
    paired = evaluate_entry(_entry(flatten_at_ns=flatten, source_deadline_ns=None), quotes)
    for policy_id in POLICIES:
        rec = paired.records[policy_id]
        assert rec.reason == "account-day close"
        assert rec.exit_at_ns <= flatten + ENTRY_WINDOW_NS


def test_s02_known_at_guard_negative_control():
    quotes = _with_fills(
        [
            _qb(FILL + NS, "101.00", name="mix"),
            _qb(FILL + 180 * MINUTE_NS, "100.50", name="end"),
        ]
    )
    trades = [
        PriceBatch(
            event_ns=FILL + NS,
            available_at_ns=FILL + NS,
            prices=(Decimal("101.00"), Decimal("100.20")),
            event_ids=("hi", "be"),
        )
    ]
    entry = _entry()
    guarded = evaluate_policy(entry, "E3", quotes, trades, known_at_guard=True)
    naive = evaluate_policy(entry, "E3", quotes, trades, known_at_guard=False)
    production = evaluate_entry(entry, quotes, trades).records["E3"]
    assert naive.reason == "break-even stop"
    assert guarded.reason != naive.reason or guarded.exit_at_ns != naive.exit_at_ns
    assert production.reason == guarded.reason
    assert production.exit_at_ns == guarded.exit_at_ns


def test_a05_occupancy_flagged_not_merged():
    flatten = FILL + 180 * MINUTE_NS
    first = _entry(entry_id="a", flatten_at_ns=flatten)
    second = _entry(entry_id="b", fill_at_ns=FILL + 45 * MINUTE_NS, flatten_at_ns=flatten)
    quotes = _with_fills(
        [
            _qb(FILL + NS, "100.5"),
            _qb(FILL + 30 * MINUTE_NS, "100.5", name="e1"),
            _qb(FILL + 45 * MINUTE_NS, "100.5", name="e2"),
            _qb(FILL + 120 * MINUTE_NS, "100.5", name="e2end"),
        ]
    )
    rows = evaluate_entries([first, second], quotes)
    assert rows[0].entry_id == "a"
    assert rows[1].entry_id == "b"
    assert rows[0].records["E1"].entry_id == "a"
    assert rows[1].records["E1"].entry_id == "b"
    assert rows[1].occupancy_flags["E1"] is False
    assert rows[1].occupancy_flags["E2"] is True
    assert set(rows[1].records) == set(POLICIES)


def test_s14_worked_net_points_on_e0_exit():
    entry = _entry(fill_price=Decimal("100.25"), initial_stop=Decimal("99.00"), objective=Decimal("102.00"))
    quotes = _with_fills([_qb(FILL + NS, "102.00")])
    e0 = evaluate_entry(entry, quotes).records["E0"]
    assert e0.reason == "objective"
    assert e0.net_points == Decimal("1.25")
    assert e0.net_dollars == Decimal("25.00")
    assert e0.net_points == net_points(
        side=1, entry=Decimal("100.25"), exit_price=Decimal("101.75"), commission=entry.round_trip_cost
    )
    assert e0.net_dollars == net_dollars(
        side=1, entry=Decimal("100.25"), exit_price=Decimal("101.75"), commission=entry.round_trip_cost
    )


def test_native_chronological_slice_reconciliation():
    assert JOBS_ROOT.is_dir()
    recon = run_native_slice(SLICE_DATES, JOBS_ROOT, out_dir=PREP)
    assert recon["descriptive_only"] is True
    assert recon["dates"] == list(SLICE_DATES)
    n = recon["entries"]
    assert n > 0
    for policy_id in POLICIES:
        row = recon["per_policy"][policy_id]
        assert (
            row["reason_sum"] + row["unsupported_undefined_r"] + row["incomplete_no_quote"] == n
        )
        if policy_id in ("E0", "E1", "E2"):
            assert row["unsupported_undefined_r"] == 0
    payload = json.loads((PREP / "SLICE_EXITS.json").read_text())
    by_day = Counter(row["account_day"] for row in payload["entries"])
    assert "" not in by_day
    assert [{"date": day, "entries": by_day[day]} for day in recon["dates"]] == recon["date_counts"]
    for row in payload["entries"]:
        e0 = row["records"]["E0"]
        assert e0.get("reason") != "undefined_initial_r"
        assert e0.get("disposition") != "unsupported_undefined_r"
        for rec in row["records"].values():
            for item in rec.get("stop_updates") or []:
                assert item["effective_available_at_ns"] > item["trigger_available_at_ns"]
                assert item["effective_after_batch_id"] != item["trigger_batch_id"]
    assert (PREP / "SLICE_EXITS.json").is_file()
    assert (PREP / "RECONCILIATION.json").is_file()
