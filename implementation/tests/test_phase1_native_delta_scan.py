"""Native RTH delta reconstruction and legacy-cache isolation tests."""

from datetime import date
from decimal import Decimal
from pathlib import Path
from types import SimpleNamespace

import pytest

from trading_research.research.method_pack import native_windows
from trading_research.research.phase1_live import family_value


DAY = date(2026, 6, 12)


def _window(rows, *, coverage_ok=True, coverage_reason="verified"):
    return SimpleNamespace(
        rows=tuple(rows),
        coverage_ok=coverage_ok,
        instrument_id=42004058,
        start_ns=1_781_271_000_000_000_000,
        end_ns=1_781_294_400_000_000_000,
        instrument_definition=SimpleNamespace(tick_size=Decimal("0.25")),
        raw_member_locators=[{
            "source_file": "/native/trades-2026-06-08.parquet",
            "dataset_id": "quantpad/cme__nq-continuous-futures__trades",
            "sha256": "a" * 64,
            "row_start": 12,
            "row_end": 17,
        }],
        missing_intervals=(),
        mismatches=() if coverage_ok else ({"reason": "executed_volume_mismatch"},),
        coverage_evidence={
            "coverage_reason": coverage_reason,
            "native_row_count": len(rows),
            "native_minute_count": 390,
            "reconciliation_summary": {
                "checked_minute_count": 390,
                "mismatch_count": 0 if coverage_ok else 1,
                "native_executed_volume": "11",
                "reference_ohlcv_volume": "11",
            },
            "corroborating_member_locators": [{
                "source_file": "/native/ohlcv-2026.parquet",
                "dataset_id": "quantpad/cme__nq-continuous-futures__ohlcv-1m",
                "sha256": "b" * 64,
                "row_start": 2,
                "row_end": 392,
            }],
        },
    )


def _run(monkeypatch, tmp_path, rows, *, coverage_ok=True, coverage_reason="verified"):
    cache_path = tmp_path / "validation" / "native-delta.parquet"
    monkeypatch.setattr(family_value, "SIGNED_DELTA_CACHE_PATH", cache_path)
    monkeypatch.setattr(
        native_windows,
        "collect_window",
        lambda *args, **kwargs: _window(rows, coverage_ok=coverage_ok, coverage_reason=coverage_reason),
    )
    return family_value.scan_rth_delta([DAY])[DAY.isoformat()], cache_path


def test_scan_uses_native_b_buy_a_sell_n_unknown_and_tick_grid(monkeypatch, tmp_path):
    rows = [
        {"action": "T", "price": Decimal("100.00"), "size": 5, "side": "B"},
        {"action": "T", "price": Decimal("100.25"), "size": 2, "side": "A"},
        {"action": "T", "price": Decimal("100.25"), "size": 1, "aggressor": "buy"},
        {"action": "T", "price": Decimal("100.50"), "size": 3, "side": "N"},
        # Non-trade native members cannot change executed delta.
        {"action": "A", "price": Decimal("99.00"), "size": 100, "aggressor": "buy"},
    ]
    row, cache_path = _run(monkeypatch, tmp_path, rows)

    assert row["known_delta"] == 4.0  # B +5, A -2, B +1
    assert row["known_volume"] == 8.0
    assert row["unknown_volume"] == 3.0
    assert row["total_volume"] == 11.0
    assert row["signed_volume_coverage"] == pytest.approx(8 / 11)
    assert row["tick_size"] == "0.25"
    assert row["known_delta_max_candidates"] == [100.0]
    assert row["known_delta_min_candidates"] == [100.25]
    assert row["unknown_price_candidates"] == [100.5]
    assert row["unknown_price_min"] == 100.5
    assert row["unknown_price_max"] == 100.5
    # Unknown executions make the signed extrema ineligible even with a
    # complete clock; the all-volume POC remains a separate observation.
    assert row["dp_max"] is None
    assert row["dp_min"] is None
    assert row["poc_candidates"] == [100.0]
    assert row["coverage_ok"] is True
    assert row["source_hashes"] == {
        "quantpad/cme__nq-continuous-futures__ohlcv-1m": ["b" * 64],
        "quantpad/cme__nq-continuous-futures__trades": ["a" * 64],
    }
    assert cache_path.is_file()
    assert "validation" in cache_path.parts


def test_unknown_side_and_reconciliation_gap_keep_extrema_unavailable(monkeypatch, tmp_path):
    rows = [
        {"action": "T", "price": Decimal("101.00"), "size": 9, "side": "N"},
        {"action": "T", "price": Decimal("100.00"), "size": 1, "side": "B"},
    ]
    row, _ = _run(
        monkeypatch,
        tmp_path,
        rows,
        coverage_ok=None,
        coverage_reason="cross_source_reconciliation_mismatch",
    )

    assert row["unknown_volume"] == 9.0
    assert row["unknown_price_count"] == 1
    assert row["unknown_price_candidates"] == [101.0]
    assert row["known_delta_max_candidates"] == [100.0]
    assert row["coverage_ok"] is None
    assert row["coverage_reason"] == "cross_source_reconciliation_mismatch"
    assert row["reconciliation_summary"]["mismatch_count"] == 1
    assert row["dp_max"] is None
    assert row["dp_min"] is None
    # The provisional all-volume extremum remains visible for reconciliation;
    # incomplete coverage still prevents it from supporting a delta flag.
    assert row["poc_candidates"] == [101.0]
    assert row["delta_ne_poc"] is None


def test_scan_never_reads_legacy_signed_cache(monkeypatch, tmp_path):
    rows = [{"action": "T", "price": Decimal("100.00"), "size": 2, "side": "B"}]
    calls = []

    def old_cache_reader(name):
        calls.append(name)
        return [{"date": DAY.isoformat(), "dp_max": -999.0, "signed_flow_version": "old-A-buy-B-sell"}]

    # If the implementation regresses to load_rows("value_delta_rth_F"),
    # this test sees the old inverted answer or the forbidden call.
    monkeypatch.setattr(family_value, "load_rows", old_cache_reader)
    row, cache_path = _run(monkeypatch, tmp_path, rows)

    assert calls == []
    assert row["known_delta"] == 2.0
    assert row["dp_max"] == 100.0
    assert row["signed_flow_version"] == family_value.SIGNED_DELTA_VERSION
    assert cache_path != family_value.LEGACY_SIGNED_DELTA_CACHES[0]


def test_scan_rejects_off_grid_native_price(monkeypatch, tmp_path):
    rows = [{"action": "T", "price": Decimal("100.10"), "size": 1, "side": "B"}]
    with pytest.raises(ValueError, match="tick grid"):
        _run(monkeypatch, tmp_path, rows)
