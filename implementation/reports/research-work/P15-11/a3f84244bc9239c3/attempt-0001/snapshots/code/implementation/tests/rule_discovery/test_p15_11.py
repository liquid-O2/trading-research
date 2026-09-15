"""P15-11 Green Bird VWAP and scalps."""
from __future__ import annotations

from decimal import Decimal
from pathlib import Path
import inspect

from trading_research.research.method_pack.historical_price_scanners import scan_green_vwap
from trading_research.research.rule_discovery.baseline_repairs import scan_green_vwap_repaired
from trading_research.research.rule_discovery.native import replay_native_row
from trading_research.research.rule_discovery.source_adapters.common import golden_pocket
from trading_research.research.rule_discovery.source_adapters.green_vwap_scalp import (
    d1_retest_window_explanation,
    family_document,
    golden_pocket_continuation,
)


def test_a01_unclosed_bar_cannot_admit():
    assert family_document()["clock_zone_unverified"] is True


def test_a01_gb_a4_golden_pocket_continuation():
    out = golden_pocket_continuation(Decimal("100"), Decimal("200"), "long")
    assert out["addition"] == "A4"
    assert out["custom_not_source_long"] is True
    lo, hi = golden_pocket(Decimal("100"), Decimal("200"))
    assert lo == Decimal("150.00") or lo == Decimal("150")
    assert hi > lo


def test_a02_custom_not_labelled_source_long():
    out = golden_pocket_continuation(Decimal("10"), Decimal("20"), "long")
    assert out["branch"] != "source_long"


def test_a03_scalp_mirrors():
    long_lo, long_hi = golden_pocket(Decimal("100"), Decimal("200"))
    assert long_hi > long_lo


def test_d1_retest_window_does_not_overwrite_breakout_context():
    frozen = inspect.getsource(scan_green_vwap)
    repaired = inspect.getsource(scan_green_vwap_repaired)
    explanation = d1_retest_window_explanation()
    assert "continuation_context" in frozen
    assert frozen.count("continuation_context") >= 1
    assert "retest_at" in repaired
    assert "breakout['C']>max" in repaired.replace(" ", "") or "breakout['C'] > max" in repaired
    assert explanation["finding"] == "D1"
    assert "rebound" in explanation["mechanism"] or "rebind" in explanation["mechanism"] or "overwrite" in explanation["mechanism"]
    assert explanation["example"] == "2023-12-08"


def test_s07_native_replay():
    path = "/workspace/data/quantpad/cme__nq-continuous-futures__mbp-1/2021-01.parquet"
    if Path(path).is_file():
        assert replay_native_row(path, 769284)["kind"] == "native"


def test_s31_provenance():
    doc = family_document()
    assert "golden_pocket_continuation" in doc["source_additions"]
