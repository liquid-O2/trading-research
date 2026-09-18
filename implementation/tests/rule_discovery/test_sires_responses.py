"""Sires' entry at failed aggression (Big Trades p.4, p.13; NY AM p.4): a big
aggressive order that is traded back through was paid nothing; the entry is
against it, the stop a tick beyond the extreme made since it printed. The
expectations below are worked by hand on small tapes."""
from __future__ import annotations

import numpy as np

from trading_research.research.rule_discovery.source_adapters import sires_responses as sr

SEC = 1_000_000_000


def _tape(rows):
    """rows: (second, price, size, sign). Fills sharing a second and a side are one order."""
    t = np.array([int(r[0] * SEC) for r in rows], dtype=np.int64)
    return t, np.array([r[1] for r in rows], dtype=np.float64), np.array([r[2] for r in rows], dtype=np.int64), np.array([r[3] for r in rows], dtype=np.int64)


def test_sellers_taken_back_are_a_long_with_the_stop_under_their_extreme():
    tape = _tape([(1, 100.0, 1, 1), (10, 100.0, 40, -1), (11, 99.0, 1, -1), (12, 98.5, 1, -1), (20, 100.5, 1, 1), (21, 101.0, 1, 1), (22, 101.5, 1, 1)])
    events = sr.failed_aggression(*tape, begin=0, end=100 * SEC)
    assert len(events) == 1
    event = events[0]
    assert event["side"] == "long"
    assert event["decision_at"] == 21 * SEC and event["entry"] == 101.0, "100.5 is not a point back through 100; 101.0 is"
    assert event["extreme"] == 98.5 and event["stop"] == 98.25
    assert event["paid_points"] == 1.5 and event["failed_contracts"] == 40
    assert event["arrival"] is None


def test_an_order_that_is_paid_and_never_taken_back_in_time_is_no_event():
    paid = _tape([(10, 100.0, 40, -1), (11, 99.0, 1, -1), (12, 95.0, 1, -1), (400, 101.0, 1, 1)])
    assert sr.failed_aggression(*paid, begin=0, end=1000 * SEC) == [], "taken back after the five-minute window: not its failure"
    small = _tape([(10, 100.0, 29, -1), (20, 101.0, 1, 1)])
    assert sr.failed_aggression(*small, begin=0, end=100 * SEC) == [], "29 lots is under his Big Trades floor"


def test_nothing_after_the_decision_rewrites_it_and_a_stopped_failure_is_followed_by_a_new_one():
    """2026-08-06 09:33: S53 at 29,249 is taken back at 09:33:04, price then makes
    a lower low and S30 at 29,242 fails three seconds later. The first event's
    stop must stay under ITS extreme; the second is its own opportunity."""
    tape = _tape(
        [
            (10, 100.0, 53, -1), (11, 99.0, 1, -1),  # sellers, paid a point
            (12, 101.0, 1, 1),  # taken back: event one, extreme 99.0
            (13, 95.0, 30, -1), (14, 94.0, 1, -1),  # lower low AFTER the decision, second sellers
            (15, 96.0, 1, 1),  # second sellers taken back: event one's stop (98.75) has traded, so this is new
        ]
    )
    first, second = sr.failed_aggression(*tape, begin=0, end=100 * SEC)
    assert (first["decision_at"], first["extreme"], first["stop"], first["failed_contracts"]) == (12 * SEC, 99.0, 98.75, 53)
    assert (second["decision_at"], second["entry"], second["extreme"], second["stop"]) == (15 * SEC, 96.0, 94.0, 93.75)

    beside = _tape([(10, 100.0, 53, -1), (11, 99.0, 1, -1), (12, 101.0, 1, 1), (13, 100.5, 30, -1), (14, 101.5, 1, 1)])
    only = sr.failed_aggression(*beside, begin=0, end=100 * SEC)
    assert len(only) == 1 and only[0]["failed_contracts"] == 53, "a failure beside a live one is the same opportunity and adds nothing to it"


def test_the_arrival_is_decided_at_its_own_time_with_its_own_stop():
    tape = _tape([(10, 100.0, 40, -1), (11, 99.0, 1, -1), (12, 101.0, 1, 1), (13, 98.0, 1, -1), (20, 100.0, 35, 1), (20, 100.5, 5, 1)])
    event = sr.failed_aggression(*tape, begin=0, end=100 * SEC)[0]
    assert event["stop"] == 98.75, "the reclaim's stop knows nothing of the 98.0 print after it"
    assert event["arrival"] == {"decision_at": 20 * SEC, "entry": 100.5, "lots": 40, "stop": 97.75}, "the buyers' order is known at its last fill; its stop is under the low made by then"


def test_buyers_taken_back_are_a_short():
    tape = _tape([(10, 100.0, 40, 1), (11, 100.75, 1, 1), (12, 99.0, 1, -1)])
    event = sr.failed_aggression(*tape, begin=0, end=100 * SEC)[0]
    assert (event["side"], event["entry"], event["stop"]) == ("short", 99.0, 101.0)
