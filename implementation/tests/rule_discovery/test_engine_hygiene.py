"""Write guard, worker sizing, job resources, and baseline-delegation parity."""

from __future__ import annotations

from pathlib import Path
import json

from trading_research.research.rule_discovery.native import CacheWriteBlocked, cgroup_worker_count, install_write_guard
from trading_research.research.rule_discovery.runner import (
    job_resource_record,
    peak_rss_bytes,
    replay_parity_sample,
    stratified_parity_dates,
)

PARITY_PATH = Path("/workspace/implementation/reports/research-work/P15-17/_track_r3/PARITY_STRATIFIED.json")


def test_write_guard_blocks_build_event_window():
    install_write_guard()
    from trading_research.research.method_pack import event_cache, event_time

    try:
        event_cache.build_event_window("/workspace/data", 0, 1, "1")
        raised = False
    except CacheWriteBlocked:
        raised = True
    assert raised is True
    try:
        event_time.build_event_window("/workspace/data", 0, 1, "1")
        raised_time = False
    except CacheWriteBlocked:
        raised_time = True
    assert raised_time is True


def test_worker_count_from_cgroup_or_affinity():
    n = cgroup_worker_count()
    assert n >= 1
    quota = Path("/sys/fs/cgroup/cpu/cpu.cfs_quota_us")
    period = Path("/sys/fs/cgroup/cpu/cpu.cfs_period_us")
    if quota.is_file() and period.is_file():
        q = int(quota.read_text().strip())
        p = int(period.read_text().strip())
        if q > 0 and p > 0:
            assert n == max(1, q // p)


def test_job_record_has_wall_seconds_and_peak_rss():
    rec = job_resource_record(wall_seconds=2.5)
    assert rec["wall_seconds"] == 2.5
    assert rec["peak_rss_bytes"] >= 0
    assert peak_rss_bytes() >= 0


def test_stratified_parity_dates_meet_the_contract():
    dates = stratified_parity_dates()
    assert len(dates) >= 40
    for required in ("2023-03-13", "2023-11-06", "2023-11-24", "2020-03-13", "2026-09-03"):
        assert required in dates
    for year in range(2020, 2026):
        assert sum(1 for item in dates if item.startswith(f"{year}-")) >= 8


def test_baseline_delegation_parity_one_date_byte_for_byte():
    install_write_guard()
    result = replay_parity_sample(["2020-01-02"], workers=1)
    assert result["jobs"] >= 50
    assert result["matches"] == result["jobs"]
    assert result["mismatches"] == []
    assert result["byte_equal"] is True


def test_recorded_parity_covers_stratified_contract_dates():
    dates = stratified_parity_dates()
    assert PARITY_PATH.is_file(), f"missing recorded parity artifact {PARITY_PATH}"
    document = json.loads(PARITY_PATH.read_text())
    recorded = list(document.get("dates") or [])
    assert set(recorded) == set(dates)
    assert len(recorded) == len(dates)
    for year in range(2020, 2026):
        assert sum(1 for item in recorded if item.startswith(f"{year}-")) >= 8
    assert "2026-09-03" in recorded
    assert document.get("byte_equal") is True
    assert document.get("jobs") == document.get("matches")
    assert document.get("mismatches") == []
