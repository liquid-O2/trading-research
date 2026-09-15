"""P15-16 process observations and refill population."""
from __future__ import annotations

from pathlib import Path

import numpy as np

from trading_research.research.rule_discovery.native import (
    NativeMarketView,
    SessionArrays,
    empty_session_arrays,
    replay_native_row,
)
from trading_research.research.rule_discovery.source_adapters.processes import (
    PRINT_THRESHOLD,
    PRINTED_TOUCHES_PER_SESSION,
    amt_states_are_not_day_types,
    family_document,
    form_refill_zones,
    native_bbo_cannot_certify_ten_level,
    no_entry_denominator,
    python_form_refill_zones,
    reconcile_population,
)


def _arrays_from_events(events: list[tuple[int, int, int, int]]) -> SessionArrays:
    n = len(events)
    t = np.array([e[0] for e in events], dtype=np.int64)
    ticks = np.array([e[1] for e in events], dtype=np.int64)
    size = np.array([e[2] for e in events], dtype=np.int64)
    side = np.array([e[3] for e in events], dtype=np.int8)
    z64 = np.zeros(n, dtype=np.int64)
    z8 = np.zeros(n, dtype=np.int8)
    return SessionArrays(
        t_ns=t,
        price_ticks=ticks,
        size=size,
        side=side,
        action=np.ones(n, dtype=np.int8),
        bid_ticks=z64,
        ask_ticks=z64,
        bid_sz=z64,
        ask_sz=z64,
        flags=z64,
        known_at_ns=t,
        exchange_sequence=np.arange(n, dtype=np.int64),
        is_trade=np.ones(n, dtype=np.bool_),
        row_id=np.array([f"r{i}" for i in range(n)], dtype=object),
        ooo_index=np.zeros(0, dtype=np.int64),
        batch_starts=np.array([0], dtype=np.int64),
        instrument_id="NQ",
        start_ns=int(t[0]) if n else 0,
        end_ns=int(t[-1]) + 1 if n else 1,
        source_sha256=(),
    )


def test_a01_no_entry_denominator():
    assert no_entry_denominator("process") is True
    assert no_entry_denominator("entry") is False
    assert family_document()["entry_denominator"] is False


def test_a02_no_arrival_vs_unknown():
    recon = reconcile_population(0, 1)
    assert recon["touches_per_session"] == 0.0


def test_a03_amt_states_not_day_types():
    assert amt_states_are_not_day_types() == ("B", "A", "D", "E", "W")


def test_a04_bbo_cannot_certify_ten_level():
    assert native_bbo_cannot_certify_ten_level() is True


def test_a05_private_records_explicit():
    assert family_document()["clock_zone_unverified"] is True


def test_refill_python_oracle_matches_array():
    events = [
        (1_000, 40000, 50, 1),
        (2_000, 40000, 50, 1),
        (3_000, 40001, 40, 1),
    ]
    py = python_form_refill_zones(events)
    view = NativeMarketView(_arrays_from_events(events), account_day="2021-01-04")
    arr = form_refill_zones(view)
    assert py["n_zones"] == arr["n_zones"]
    assert arr["n_zones"] >= 1
    assert PRINT_THRESHOLD == 40


def test_refill_population_reconciliation_records_gap():
    recon = reconcile_population(3, 1)
    assert recon["printed_touches_per_session"] == PRINTED_TOUCHES_PER_SESSION
    assert recon["population_scale_unreconciled"] is True
    assert recon["resolution_path"] == "ii"
    assert recon["reason"]
    assert "pre-registration" in recon["reason"]
    assert recon["n_sessions"] == 1
    assert recon["population_kind"] == "engineering_slice"


def test_s07_native_replay():
    path = "/workspace/data/quantpad/cme__nq-continuous-futures__mbp-1/2021-01.parquet"
    if Path(path).is_file():
        assert replay_native_row(path, 769284)["kind"] == "native"
