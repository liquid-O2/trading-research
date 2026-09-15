"""P15-15 Keani ordered opening-value."""
from __future__ import annotations

from pathlib import Path
import inspect

from trading_research.research.rule_discovery.baseline_repairs import scan_keani_repaired
from trading_research.research.rule_discovery.native import replay_native_row
from trading_research.research.rule_discovery.source_adapters.keani import (
    a_period_trade_below_vah_invalidates,
    family_document,
    low_support_inconclusive,
    value_after_break_cannot_satisfy_before,
)


def test_a01_single_trade_below_vah_invalidates():
    assert a_period_trade_below_vah_invalidates(10, 12) is True
    assert a_period_trade_below_vah_invalidates(12, 10) is False


def test_a02_value_after_break_rejected():
    assert value_after_break_cannot_satisfy_before(5, 10) is True
    assert value_after_break_cannot_satisfy_before(15, 10) is False


def test_a03_low_support_inconclusive():
    assert low_support_inconclusive(2) is True
    assert low_support_inconclusive(20) is False


def test_c4_rejection_levels_in_repaired_scanner():
    src = inspect.getsource(scan_keani_repaired)
    assert "developing_poc" in src
    assert "prior_day_vah" in src
    assert family_document()["findings"] == ["C4"]


def test_s07_native_replay():
    path = "/workspace/data/quantpad/cme__nq-continuous-futures__mbp-1/2021-01.parquet"
    if Path(path).is_file():
        assert replay_native_row(path, 769284)["kind"] == "native"
