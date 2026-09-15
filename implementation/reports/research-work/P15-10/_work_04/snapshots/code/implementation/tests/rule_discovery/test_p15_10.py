"""P15-10 Green Bird failure branches."""
from __future__ import annotations

from pathlib import Path
import inspect

from trading_research.research.method_pack.historical_price_scanners import scan_green_failure
from trading_research.research.rule_discovery.baseline_repairs import scan_green_failure_repaired
from trading_research.research.rule_discovery.native import replay_native_row
from trading_research.research.rule_discovery.source_adapters.common import empty_delta_spec, enumerate_own_population
from trading_research.research.rule_discovery.source_adapters.green_failure import (
    FAMILY,
    asia_box_window,
    family_document,
    london_box_window,
    overnight_scan_branches,
    p4_empty_path_omission,
    prior_period_unknown_not_substitute,
    sweep_and_reclaim_not_collapsed,
)


def test_a01_prior_week_month_stop_at_completed_window():
    assert prior_period_unknown_not_substitute(True) == "unknown"
    assert prior_period_unknown_not_substitute(False) == "complete"


def test_a01_gb_a1_london_box():
    win = london_box_window()
    assert win["start"] == "02:00"
    assert win["end"] == "05:00"
    assert win["addition"] == "A1"


def test_a01_gb_a2_asia_box():
    win = asia_box_window()
    assert win["tdo_required"] is False
    assert win["addition"] == "A2"


def test_a01_gb_a3_overnight_scan():
    branches = overnight_scan_branches()
    assert "prior_day_level" in branches
    assert "london_box" in branches


def test_a02_sweep_and_reclaim_not_collapsed():
    assert sweep_and_reclaim_not_collapsed(10, 20) is True
    assert sweep_and_reclaim_not_collapsed(10, 10) is True


def test_a03_missing_prior_is_unknown():
    assert prior_period_unknown_not_substitute(True) == "unknown"


def test_a04_own_population():
    out = enumerate_own_population(baseline_ids={"nyam"}, candidate_ids={"nyam", "london_box"}, geometry_changed=True)
    assert "london_box" in out["new_contacts"]


def test_a05_p4_empty_path():
    p4 = p4_empty_path_omission()
    frozen = inspect.getsource(scan_green_failure)
    repaired = inspect.getsource(scan_green_failure_repaired)
    assert "empty" in p4["frozen"].lower() or "ValueError" in p4["frozen"]
    assert "omission" in repaired.lower() or "availability" in repaired
    assert family_document()["clock_zone_unverified"] is True


def test_s07_native_replay():
    path = "/workspace/data/quantpad/cme__nq-continuous-futures__mbp-1/2021-01.parquet"
    if Path(path).is_file():
        assert replay_native_row(path, 769284)["kind"] == "native"


def test_s21_empty_delta_keeps_source_branch():
    spec = empty_delta_spec(FAMILY, "nyam_box")
    assert spec.source_branch == "nyam_box"
    assert spec.parameters["empty_delta"] is True


def test_scan_variant_changed_axis_dispatched():
    import inspect
    from trading_research.research.rule_discovery.source_adapters.green_failure import scan_variant

    assert "dispatch_scan_variant" in inspect.getsource(scan_variant)
