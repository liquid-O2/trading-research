"""Sires' OFM as the four-stage sequence of Origin of the Move pp.3-14: a
one-sided aggression box (catalyst), a release in the aggressors' direction, a
close back through the box (failure), a retest from the failure side; the trade
is against the catalyst's aggressors."""
from decimal import Decimal as D

from trading_research.research.rule_discovery.source_adapters import sires_ofm as ofm

MIN = 60 * 1_000_000_000


def _bars(rows):
    return [{"start": i * MIN, "end": (i + 1) * MIN, "O": D(o), "H": D(h), "L": D(l), "C": D(c)} for i, (o, h, l, c) in enumerate(rows)]


BOX = {"id": "b", "lo": D("100"), "hi": D("104"), "aggressor": ofm.BUY, "known_at": 0, "n_orders": 3, "contracts": 120}
# buyers absorbed at 100-104; squeeze to 118; close back below 99; retest of 100 from below; continuation lower
FAILED_SQUEEZE = [("103", "106", "102", "105"), ("105", "118", "104", "116"), ("116", "117", "108", "109"), ("109", "110", "97", "98"), ("98", "100.5", "96", "97"), ("97", "98", "90", "91")]


def test_a_failed_buy_squeeze_is_one_short_sequence_with_both_source_entries():
    bars = _bars(FAILED_SQUEEZE)
    seqs = ofm.ofm_sequences(bars, [BOX], session_open=0, session_end=10 * MIN)
    assert len(seqs) == 1
    s = seqs[0]
    assert (s["side"], s["squeeze_extreme"], s["failure_at"], s["retest_at"]) == ("short", D("118"), 4 * MIN, 5 * MIN)
    fills = {f["mode"]: f for f in ofm.ofm_fills(bars, s)}
    # passive: the resting order at the box's failure-side edge, stop beyond the aggression
    assert (fills["ofm_passive"]["entry"], fills["ofm_passive"]["stop"]) == (D("100"), D("104.25"))
    # aggressive: one tick below the retest bar's low, tagged by the next bar, stop beyond the retest wick
    assert (fills["ofm_aggressive"]["entry"], fills["ofm_aggressive"]["stop"], fills["ofm_aggressive"]["at"]) == (D("95.75"), D("100.75"), 6 * MIN)


def test_the_mirror_is_a_long_after_a_failed_sell_squeeze():
    flip = lambda v: str(D("200") - D(v))
    bars = _bars([(flip(o), flip(l), flip(h), flip(c)) for o, h, l, c in FAILED_SQUEEZE])
    box = {**BOX, "lo": D("96"), "hi": D("100"), "aggressor": ofm.SELL}
    seqs = ofm.ofm_sequences(bars, [box], session_open=0, session_end=10 * MIN)
    assert [s["side"] for s in seqs] == ["long"]
    assert ofm.ofm_fills(bars, seqs[0])[0]["entry"] == D("100")


def test_no_release_no_failure_or_a_reclaim_before_the_retest_is_no_sequence():
    no_release = _bars([("103", "106", "102", "105"), ("105", "109", "104", "105"), ("105", "106", "97", "98"), ("98", "100.5", "96", "97")])
    assert ofm.ofm_sequences(no_release, [BOX], session_open=0, session_end=10 * MIN) == []
    no_failure = _bars(FAILED_SQUEEZE[:3] + [("109", "112", "101", "110")])
    assert ofm.ofm_sequences(no_failure, [BOX], session_open=0, session_end=10 * MIN) == []
    reclaimed = _bars(FAILED_SQUEEZE[:4] + [("98", "107", "97", "106"), ("106", "108", "100", "101")])
    assert ofm.ofm_sequences(reclaimed, [BOX], session_open=0, session_end=10 * MIN) == []


def test_a_box_both_sides_built_is_not_a_squeeze():
    bars = _bars(FAILED_SQUEEZE)
    assert ofm.ofm_sequences(bars, [{**BOX, "aggressor": "AB"}], session_open=0, session_end=10 * MIN) == []


def test_range_bars_hold_forty_ticks_and_invent_no_price():
    import numpy as np

    from trading_research.research.method_pack.trade_tape import range_bars

    # 100 -> 110 in quarter-point steps (exactly forty ticks), then one more tick, then down twelve points
    up = [100 + 0.25 * i for i in range(41)]
    px = np.array(up + [110.25] + [110.25 - 0.25 * i for i in range(1, 49)])
    t = np.arange(len(px), dtype=np.int64) * 1_000
    size = np.ones(len(px), dtype=np.int64)
    sign = np.where(np.arange(len(px)) % 2 == 0, 1, -1).astype(np.int8)
    bars = range_bars(t, px, size, sign, ticks=40)
    assert [(float(b["O"]), float(b["H"]), float(b["L"]), float(b["C"])) for b in bars[:2]] == [(100.0, 110.0, 100.0, 110.0), (110.25, 110.25, 100.25, 100.25)]
    assert all(b["H"] - b["L"] <= 10 for b in bars)
    assert sum(b["V"] for b in bars) == len(px) and all(b["V"] == b["buy_volume"] + b["sell_volume"] for b in bars)
    # a bar is known complete when the next one opens; the last bar of a tape is not complete
    assert bars[0]["known_at"] == bars[1]["start"] and bars[-1]["complete"] is False and bars[-1]["known_at"] is None
