"""TBR pp.27-29: the stop of an orderblock or rejection-block fill rests a tick
beyond the block's extreme ("Conservative Stop Loss at the low of the
orderblock") or at its midpoint ("Aggressive Stop Loss at the midpoint of the
orderblock"; "at the midpoint of the rejection block"). The placement is a
module constant a rescan sets; the conservative placement is the baseline."""
from decimal import Decimal as D

import pytest

from trading_research.research.rule_discovery.source_adapters import jumbo

MIN = 60 * 1_000_000_000


def _bar(i, o, h, l, c):
    return {"start": i * MIN, "end": (i + 1) * MIN, "known_at": (i + 1) * MIN, "O": D(o), "H": D(h), "L": D(l), "C": D(c)}


# C1, then C2 sweeps C1's low to 100 and spans 100-110, then C3 closes above C2's high
OB_LONG = [_bar(0, "106", "108", "103", "105"), _bar(1, "105", "110", "100", "104"), _bar(2, "104", "113", "103", "112")]
# a rejection wick: the sweep candle opens 108, closes 107, wicks to 100 (wick 7 > body 1); the next candle closes above its high
RB_LONG = [_bar(0, "108", "109", "100", "107"), _bar(1, "107", "112", "106", "111")]


@pytest.mark.parametrize(
    "placement, ob_stop, rb_stop",
    [
        ("conservative", D("100") - jumbo.TICK, D("100") - jumbo.TICK),
        ("aggressive", D("105"), D("103.5")),
    ],
)
def test_signature_stop_placement(monkeypatch, placement, ob_stop, rb_stop):
    monkeypatch.setattr(jumbo, "SIGNATURE_STOP", placement)
    ob = jumbo._three_candle_ob(OB_LONG, "long")
    assert ob is not None and ob["kind"] == "orderblock" and ob["entry"] == D("112")
    assert ob["stop"] == ob_stop  # the orderblock is C2, 100-110: its low, or its midpoint 105
    rb = jumbo._rejection_block(RB_LONG, "long")
    assert rb is not None and rb["kind"] == "rejection_block" and rb["band"] == [D("100"), D("107")]
    assert rb["stop"] == rb_stop  # the rejection block is the wick 100-107: its low, or its midpoint 103.5


def test_unknown_placement_is_an_error(monkeypatch):
    monkeypatch.setattr(jumbo, "SIGNATURE_STOP", "midway")
    with pytest.raises(ValueError):
        jumbo._three_candle_ob(OB_LONG, "long")
