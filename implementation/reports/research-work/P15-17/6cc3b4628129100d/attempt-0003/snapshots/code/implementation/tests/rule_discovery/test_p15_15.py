"""P15-15 Keani ordered opening-value."""
from __future__ import annotations

from pathlib import Path
import inspect

from trading_research.research.rule_discovery.baseline_repairs import scan_keani_repaired
from trading_research.research.rule_discovery.native import replay_native_row
from trading_research.research.rule_discovery.source_adapters.keani import (
    a_period_trade_below_vah_invalidates,
    apply_keani_rules,
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


def test_b0_matches_frozen_scan_branch():
    from trading_research.research.rule_discovery.source_adapters.common import FROZEN_PARITY_DATES, replay_b0_against_frozen
    from trading_research.research.rule_discovery.source_adapters import keani as _keani  # noqa: F401

    for day in FROZEN_PARITY_DATES:
        row = replay_b0_against_frozen(day, "KEANI-OPEN-ABOVE-VALUE", "source_long")
        assert row["b0_transform_markers"] == []
        assert row["match"] is True, row


def test_keani_findings_applied_in_scan():
    src = inspect.getsource(apply_keani_rules)
    assert "a_period_trade_below_vah_invalidates" in src
    assert "value_after_break_cannot_satisfy_before" in src
    out = apply_keani_rules(
        {
            "episodes": [
                {
                    "candidate_id": "a",
                    "values": {
                        "a_low": 10,
                        "prior_vah": 12,
                        "breakout_at": 10,
                        "dev_vah_known_at": 15,
                        "support_n": 2,
                    },
                    "geometry": {"rejection_level": "developing_poc"},
                }
            ]
        },
        None,
        "source_long",
        "B0.1",
    )
    values = out["episodes"][0]["values"]
    assert values["a_period_below_vah_invalidates"] is True
    assert values["whole_period_above_vah"] is False
    assert values["value_after_break_rejected"] is True
    assert values["low_support_inconclusive"] is True
    assert values["keani_adapter_rules"] is True


def test_s07_native_replay():
    path = "/workspace/data/quantpad/cme__nq-continuous-futures__mbp-1/2021-01.parquet"
    if Path(path).is_file():
        assert replay_native_row(path, 769284)["kind"] == "native"
