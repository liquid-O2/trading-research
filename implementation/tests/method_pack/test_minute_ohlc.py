"""The withheld open and close of an event-time bar are recomputed from the
owned trades in exchange order (``method_pack/minute_ohlc.py``)."""
from decimal import Decimal as D

import numpy as np
import pytest

from trading_research.research.method_pack import minute_ohlc

MIN = 60_000_000_000


def _row(i, o, h, l, c):
    return {"start": i * MIN, "end": (i + 1) * MIN, "known_at": (i + 1) * MIN, "O": None if o is None else D(o), "H": D(h), "L": D(l), "C": None if c is None else D(c), "V": 10}


@pytest.fixture
def trades(monkeypatch):
    # minute 0: 100, 101, 99.5 ; minute 1: 99.75, 102 ; minute 2: none ; minute 3: 250 (outside the bar's range)
    ts = np.array([1, 2, MIN - 1, MIN, 2 * MIN - 1, 3 * MIN + 5], dtype=np.int64)
    px = np.array([100.0, 101.0, 99.5, 99.75, 102.0, 250.0])

    def fake(data_root, instrument_id, start, end):
        lo, hi = np.searchsorted(ts, start), np.searchsorted(ts, end)
        return (ts[lo:hi], px[lo:hi]) if hi > lo else None

    monkeypatch.setattr(minute_ohlc, "_from_trades", fake)
    monkeypatch.setattr(minute_ohlc, "_from_vendor", lambda *a, **k: {})


def test_withheld_open_and_close_are_the_first_and_last_trade_of_the_bar(trades):
    rows = [_row(0, None, "101", "99.5", None), _row(1, "99.75", "102", "99.75", None)]
    out = minute_ohlc.fill_withheld(rows, data_root="unused", instrument_id=1)
    assert (out[0]["O"], out[0]["C"]) == (D("100.0"), D("99.5"))
    assert out[0]["open_source"] == out[0]["close_source"] == "trades_file_order"
    assert out[1]["O"] == D("99.75") and "open_source" not in out[1]  # a known open is never replaced
    assert out[1]["C"] == D("102.0")
    assert rows[0]["O"] is None  # the input rows are not mutated


def test_a_bar_with_no_trades_or_a_value_outside_its_range_stays_withheld(trades):
    rows = [_row(2, None, "101", "99", None), _row(3, None, "101", "99", None)]
    out = minute_ohlc.fill_withheld(rows, data_root="unused", instrument_id=1)
    assert out[0]["O"] is None and out[0]["C"] is None  # no trade in the minute
    assert out[1]["O"] is None and out[1]["C"] is None  # 250 is outside 99-101: not this bar's trade


def test_rows_that_need_nothing_are_returned_as_they_are(trades):
    rows = [_row(0, "100", "101", "99.5", "99.5")]
    assert minute_ohlc.fill_withheld(rows, data_root="unused", instrument_id=1) is rows


def test_a_multi_minute_bar_takes_its_open_and_close_from_its_own_interval(trades):
    bar = {"start": 0, "end": 2 * MIN, "known_at": 2 * MIN, "O": None, "H": D("102"), "L": D("99.5"), "C": None, "V": 20}
    out = minute_ohlc.fill_withheld([bar], data_root="unused", instrument_id=1)
    assert (out[0]["O"], out[0]["C"]) == (D("100.0"), D("102.0"))
