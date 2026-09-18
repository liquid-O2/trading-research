"""The profile-structure objects the authors read (VP2 p.3, AMT1 p.9, FIND p.8,
RTVP pp.7-11): nodes, ledges and shapes on profiles whose structure is known
by construction, so each expectation is independent of the code."""
from decimal import Decimal

import pytest

from trading_research.research.method_pack.profile_nodes import ledges, nodes, on_node_or_ledge, shape


def _payload(volumes: list[float], start: float = 20000.0, tick: float = 0.25) -> dict:
    rows = [{"price": start + i * tick, "total_volume": v} for i, v in enumerate(volumes)]
    peak = max(range(len(volumes)), key=lambda i: volumes[i])
    return {"rows": rows, "poc": rows[peak]["price"], "vah": None, "val": None}


def _bell(n: int, centre: int, width: float, height: float) -> list[float]:
    return [height * pow(2.718281828, -((i - centre) ** 2) / (2 * width * width)) for i in range(n)]


def test_two_humps_give_two_hvns_one_lvn_between_and_a_ledge_on_each_shelf_edge():
    # two shelves (bells at index 20 and 60) with a thin trough between: VP2's
    # double distribution; the LVN sits in the trough, the HVNs on the humps
    vols = [a + b for a, b in zip(_bell(80, 20, 4, 1000), _bell(80, 60, 4, 800))]
    payload = _payload(vols)
    hvn, lvn = nodes(payload)
    prices = [r["price"] for r in payload["rows"]]
    assert any(abs(float(h) - prices[20]) <= 0.5 for h in hvn) and any(abs(float(h) - prices[60]) <= 0.5 for h in hvn)
    assert lvn and all(prices[20] < float(l) < prices[60] for l in lvn)
    edges = [float(x) for x in ledges(payload)]
    # the ledge is where the shelf's volume falls to half its peak, between the LVN and each hump
    assert any(prices[20] < e < float(lvn[0]) for e in edges) and any(float(lvn[0]) < e < prices[60] for e in edges)


def test_single_bell_has_one_hvn_no_lvn_and_no_ledge():
    payload = _payload(_bell(60, 30, 6, 1000))
    hvn, lvn = nodes(payload)
    assert len(hvn) == 1 and lvn == [] and ledges(payload) == []


def test_pzone_keep_rule_holds_on_the_hump_and_fails_in_air():
    vols = [a + b for a, b in zip(_bell(80, 20, 4, 1000), _bell(80, 60, 4, 800))]
    payload = _payload(vols)
    prices = [r["price"] for r in payload["rows"]]
    assert on_node_or_ledge(Decimal(str(prices[20])), payload, Decimal("1"))
    # the trough's floor, well past the ledges on both sides, is air
    assert not on_node_or_ledge(Decimal(str(prices[40])), payload, Decimal("0.5"))


@pytest.mark.parametrize(
    "vols, expected",
    [
        (_bell(60, 30, 6, 1000), "balanced"),
        ([a + b for a, b in zip(_bell(80, 20, 4, 1000), _bell(80, 60, 4, 800))], "double_distribution"),
        ([100.0] * 60, "trending"),
        # P: the bulge in the upper third, a thin stem below (RTVP p.10)
        ([20.0] * 40 + _bell(20, 10, 3, 1000), "p"),
        # b: the bulge in the lower third, the stem above
        (_bell(20, 10, 3, 1000) + [20.0] * 40, "b"),
    ],
)
def test_shapes_follow_saints_five_forms(vols, expected):
    assert shape(_payload(vols)) == expected


def test_composite_merges_sessions_by_price_and_grows_value_from_the_poc():
    from trading_research.research.method_pack.profile_nodes import composite

    a = {"rows": [{"price": 100.0, "total_volume": 10}, {"price": 100.25, "total_volume": 50}, {"price": 100.5, "total_volume": 20}]}
    b = {"rows": [{"price": 100.25, "total_volume": 10}, {"price": 100.5, "total_volume": 25}, {"price": 100.75, "total_volume": 5}]}
    c = composite([a, b])
    assert [(str(r["price"]), int(r["total_volume"])) for r in c["rows"]] == [("100.0", 10), ("100.25", 60), ("100.5", 45), ("100.75", 5)]
    # 120 total; 70% = 84: the POC bin (60) plus the larger neighbour (45) reaches it
    assert (str(c["poc"]), str(c["val"]), str(c["vah"])) == ("100.25", "100.25", "100.5")


def test_compiled_extrema_pass_makes_the_decisions_of_the_reference_walk():
    """``_mark_extrema`` replaced the per-index ``_prominence`` walk inside
    ``nodes`` for speed (2026-09-18). The reference walk stays in the module;
    on random profiles with plateaus, ties and flat edges the compiled pass
    must mark exactly the indices the walk accepts."""
    import numpy as np

    from trading_research.research.method_pack import profile_nodes as pn

    rng = np.random.default_rng(20260918)
    for trial in range(200):
        n = int(rng.integers(5, 400))
        # integer-valued volumes make ties and plateaus common
        vol = rng.integers(0, 12, size=n).astype(float)
        if trial % 3 == 0:
            vol = np.convolve(vol, np.ones(5) / 5, mode="same")
        peak = float(vol.max())
        if peak <= 0:
            continue
        floor = 0.2 * peak
        neg = -vol
        expected = np.zeros(n, dtype=np.int8)
        for i in range(1, n - 1):
            if vol[i] >= vol[i - 1] and vol[i] > vol[i + 1] and pn._prominence(vol, i) >= floor:
                expected[i] = 1
            elif vol[i] <= vol[i - 1] and vol[i] < vol[i + 1] and pn._prominence(neg, i) >= floor:
                expected[i] = 2
        got = pn._mark_extrema(np.ascontiguousarray(vol, dtype=np.float64), float(floor))
        assert np.array_equal(got, expected), (trial, n)
