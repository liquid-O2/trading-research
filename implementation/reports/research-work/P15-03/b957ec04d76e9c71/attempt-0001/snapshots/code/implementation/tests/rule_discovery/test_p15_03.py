"""P15-03 ordered labels, costed replay and chronological comparison checks."""

from __future__ import annotations

from datetime import date
from decimal import Decimal
from pathlib import Path

import pytest

from trading_research.errors import ContractError
from trading_research.research.contracts.evaluation import (
    EXCLUSION_LABEL_AFTER_FIT,
    account_day_group,
    build_evaluation_splits,
    evaluation_protocol,
    holm,
    overlapping_horizons_same_day,
    purge_future_labels,
    purge_overlap,
    split_manifest,
)
from trading_research.research.contracts.execution import (
    DayReplay,
    daily_benchmark_series,
    gap_loss_not_clipped,
    net_dollars,
    replay_calendar,
    replay_family,
    worked_net_pnl_fixture,
)
from trading_research.research.contracts.outcomes import (
    PriceBatch,
    causal_scale,
    excursions,
    first_passage,
    interval_extrema,
)
from trading_research.research.contracts.types import Coverage, CoverageReceipt, EvidenceRef, QuoteBatch


def _batch(at: int, prices: list[str], *, ids: list[str] | None = None) -> PriceBatch:
    return PriceBatch(
        event_ns=at,
        available_at_ns=at,
        prices=tuple(Decimal(p) for p in prices),
        event_ids=tuple(ids or [f"e{at}-{i}" for i in range(len(prices))]),
    )


def test_a01_same_batch_ambiguous_and_prior_gap_unknown():
    start = 10
    events = [_batch(11, ["100.5"]), _batch(12, ["102"]), _batch(13, ["98.5"])]
    hit = first_passage(events, start_ns=start, end_ns=20, side=1, entry=Decimal("100"), stop=Decimal("99"), target=Decimal("102"))
    assert hit.result == "target_first"
    amb = first_passage(
        [_batch(11, ["100.5"]), _batch(12, ["98.5", "102"])],
        start_ns=start,
        end_ns=20,
        side=1,
        entry=Decimal("100"),
        stop=Decimal("99"),
        target=Decimal("102"),
    )
    assert amb.result == "same_batch_ambiguous"
    gapped = first_passage(
        [_batch(11, ["100.5"]), _batch(12, ["102"])],
        start_ns=start,
        end_ns=20,
        side=1,
        entry=Decimal("100"),
        stop=Decimal("99"),
        target=Decimal("102"),
        coverage={"unknown_intervals": [[11, 12]], "observed_scope_complete": False},
    )
    assert gapped.result == "prior_gap_unknown"
    neither = first_passage(
        [_batch(11, ["100.5"]), _batch(12, ["101.75"]), _batch(13, ["99.25"])],
        start_ns=start,
        end_ns=20,
        side=1,
        entry=Decimal("100"),
        stop=Decimal("99"),
        target=Decimal("102"),
        coverage={"unknown_intervals": [], "observed_scope_complete": True},
    )
    assert neither.result == "neither"
    short = first_passage(
        [_batch(12, ["98"])],
        start_ns=start,
        end_ns=20,
        side=-1,
        entry=Decimal("100"),
        stop=Decimal("101"),
        target=Decimal("98"),
    )
    assert short.result == "target_first"


def test_a02_worked_net_pnl_and_gap_not_clipped():
    fixture = worked_net_pnl_fixture()
    assert fixture["match"] is True
    assert fixture["net_dollars"] == "25.00"
    gap = gap_loss_not_clipped()
    assert gap["clipped"] is False
    assert gap["below_limit"] is True
    assert Decimal(gap["dollars"]) < Decimal("-1000")


def test_a03_zero_entry_day_stays_in_denominator():
    evidence = EvidenceRef("a" * 64, ("q1",), 1, 1, 1, Coverage.COMPLETE, ())
    quote = QuoteBatch("q1", "NQ:x", 1_000_000_000, 1_000_000_000, Decimal("100.00"), Decimal("100.25"), 1, 1, False, (evidence,))
    series = daily_benchmark_series(
        [
            {"account_day": "2020-01-02", "opportunities": [], "quotes": [quote]},
            {"account_day": "2020-01-06", "missing": True},
        ]
    )
    assert len(series) == 1
    zero = series[0]
    assert zero.account_day == "2020-01-02"
    assert zero.zero_entry is True
    assert zero.complete is True
    assert zero.fills == []
    assert "2020-01-06" not in {row.account_day for row in series}


def test_a04_account_day_rows_do_not_split():
    rows = [
        {"account_day": "2021-06-30", "asset": "NQ", "end": 2},
        {"account_day": "2021-06-30", "asset": "ES", "end": 9},
        {"account_day": "2021-07-01", "asset": "NQ", "end": 3},
    ]
    grouped = account_day_group(rows)
    assert {row["asset"] for row in grouped["2021-06-30"]} == {"NQ", "ES"}
    assert overlapping_horizons_same_day(rows) is True
    train = purge_overlap(["2021-06-29", "2021-06-30", "2021-07-01"], ["2021-07-01"])
    assert "2021-07-01" not in train
    assert "2021-06-30" not in train


def test_a06_protocol_records_primary_score():
    protocol = evaluation_protocol()
    assert protocol["primary_score"]
    assert protocol["registered_before_candidate_search"] is True


def test_a07_required_matrix_ids_match_graph():
    from trading_research.research.contracts.receipts import load_task_graph, required_matrix_ids
    graph, _ = load_task_graph()
    spec = graph.require("P15-03")
    ids = set(required_matrix_ids(spec))
    assert "A07" in ids and "S30" in ids and "S16" in ids


def test_a08_assigned_failure_probes_are_present():
    source = Path(__file__).read_text()
    for name in ("s01", "s02", "s03", "s05", "s06", "s07", "s08", "s09", "s10", "s11", "s14", "s16", "s17", "s30"):
        assert f"test_{name}" in source


def test_a05_reversed_side_and_future_import_fail():
    with pytest.raises(ContractError):
        first_passage([], start_ns=0, end_ns=1, side=0, entry=Decimal("1"), stop=Decimal("0"), target=Decimal("2"))
    invalid = first_passage([], start_ns=0, end_ns=1, side=1, entry=Decimal("100"), stop=Decimal("101"), target=Decimal("102"))
    assert invalid.result == "invalid_geometry"
    baseline = Path("/workspace/implementation/src/trading_research/research/rule_discovery/baseline.py").read_text()
    native = Path("/workspace/implementation/src/trading_research/research/rule_discovery/native.py").read_text()
    assert "contracts.outcomes" not in baseline
    assert "contracts.execution" not in native
    assert "from trading_research.research.contracts.outcomes" not in native


def test_s14_units_and_scale():
    scale = causal_scale(Decimal("104"), Decimal("100"), matching_minutes=60, complete=True)
    assert scale == Decimal("4")
    missing = causal_scale(Decimal("104"), Decimal("100"), matching_minutes=10, complete=True)
    assert missing is None
    stats = excursions([Decimal("102"), Decimal("99"), Decimal("104")], side=1, reference=Decimal("100"))
    assert stats["mfe_points"] == Decimal("4")
    assert stats["mae_points"] == Decimal("1")
    short = excursions([Decimal("98"), Decimal("101"), Decimal("96")], side=-1, reference=Decimal("100"))
    assert short["mfe_points"] == Decimal("4")
    assert short["mae_points"] == Decimal("1")


def test_s16_label_boundary_purge():
    train = purge_overlap(["2021-12-30", "2021-12-31", "2022-01-03"], ["2022-01-03"])
    assert "2022-01-03" not in train
    splits = split_manifest(["2020-01-02", "2021-06-30", "2021-07-01", "2021-10-01", "2022-01-03"])
    assert splits["registered_before_search"] is True
    year = splits["outer"][0]
    assert year["test_year"] == 2022
    assert "2022-01-03" in year["test"]
    assert "2022-01-03" not in year["fit"]


def test_s17_future_labels_do_not_enter_fit():
    cutoff = 1_000
    rows = [
        {"row_id": "ok", "account_day": "2021-06-01", "label_known_at_ns": 900},
        {"row_id": "leak", "account_day": "2021-06-02", "label_known_at_ns": 1_001},
    ]
    split = build_evaluation_splits(
        ["2020-01-02", "2021-06-01", "2021-06-02"],
        rows,
        fit_cutoff_ns=cutoff,
    )
    assert split["evaluation_protocol"]["primary_score"] == evaluation_protocol()["primary_score"]
    assert [row["row_id"] for row in split["label_purge"]["kept"]] == ["ok"]
    assert len(split["label_purge"]["excluded"]) == 1
    assert split["label_purge"]["excluded"][0]["row_id"] == "leak"
    assert split["label_purge"]["excluded"][0]["exclusion_code"] == EXCLUSION_LABEL_AFTER_FIT
    direct = purge_future_labels(rows, fit_cutoff_ns=cutoff)
    assert direct["kept"] == split["label_purge"]["kept"]


def test_s30_costed_replay_and_zero_day():
    evidence = EvidenceRef("a" * 64, ("q1",), 1, 1, 1, Coverage.COMPLETE, ())
    q_entry = QuoteBatch("q1", "NQ:x", 1_000_000_000, 1_000_000_000, Decimal("100.00"), Decimal("100.00"), 1, 1, False, (evidence,))
    q_exit = QuoteBatch("q2", "NQ:x", 2_000_000_000, 2_000_000_000, Decimal("102.00"), Decimal("102.25"), 1, 1, False, (evidence,))
    opportunities = [
        {
            "opportunity_id": "o1",
            "rule_id": "r",
            "reference_id": "ref",
            "contact_id": "c1",
            "side": 1,
            "decision_at_ns": 1000,
            "stop": "99.00",
            "target": "102.00",
        }
    ]
    replay = replay_family(opportunities, [q_entry, q_exit], account_day="2020-01-02")
    assert replay.zero_entry is False
    empty = replay_family([], [q_entry], account_day="2020-01-03")
    assert empty.zero_entry is True
    assert empty.realized_dollars == Decimal(0)
    two = replay_family(opportunities + [{**opportunities[0], "opportunity_id": "o2", "contact_id": "c2", "decision_at_ns": 1500}], [q_entry, q_exit], account_day="2020-01-02")
    assert any(item["open"] == "o1" for item in two.occupied) or len(two.fills) >= 2


def test_s01_forged_split_identity_changes():
    left = split_manifest(["2020-01-02"])
    right = split_manifest(["2020-01-03"])
    assert left != right


def test_s02_sensitive_target_first_reverses_on_wrong_side():
    events = [_batch(12, ["102"])]
    assert first_passage(events, start_ns=10, end_ns=20, side=1, entry=Decimal("100"), stop=Decimal("99"), target=Decimal("102")).result == "target_first"
    assert first_passage(events, start_ns=10, end_ns=20, side=-1, entry=Decimal("100"), stop=Decimal("101"), target=Decimal("98")).result == "stop_first"
    hold = [_batch(12, ["100.50"])]
    assert first_passage(hold, start_ns=10, end_ns=20, side=-1, entry=Decimal("100"), stop=Decimal("101"), target=Decimal("98")).result == "neither"


def test_s03_protocol_identity_is_canonical():
    from trading_research.research.contracts.identity import digest

    left = digest(evaluation_protocol())
    right = digest(evaluation_protocol())
    assert left == right


def test_s05_coverage_receipt_rejects_late_evidence():
    late = EvidenceRef("a" * 64, ("r",), 100, 100, 100, Coverage.COMPLETE, ())
    with pytest.raises(ContractError):
        CoverageReceipt(0, 10, Coverage.COMPLETE, ((0, 10),), ((0, 10),), (), "b" * 64, (late,))


def test_s06_missing_scale_is_not_filled():
    assert causal_scale(Decimal("10"), Decimal("1"), matching_minutes=59, complete=True) is None


def test_s07_native_scale_uses_owned_row_clock():
    from trading_research.research.rule_discovery.native import replay_native_row

    replayed = replay_native_row("/workspace/data/quantpad/cme__nq-continuous-futures__mbp-1/2021-01.parquet", 769284)
    assert replayed["kind"] == "native"
    assert replayed["event_ns"] == 1609770600002445765


def test_s08_later_price_does_not_change_earlier_passage():
    early = [_batch(12, ["102"])]
    later = early + [_batch(18, ["90"])]
    a = first_passage(early, start_ns=10, end_ns=15, side=1, entry=Decimal("100"), stop=Decimal("99"), target=Decimal("102"))
    b = first_passage(later, start_ns=10, end_ns=15, side=1, entry=Decimal("100"), stop=Decimal("99"), target=Decimal("102"))
    assert a.result == b.result == "target_first"


def test_s09_batch_order_does_not_invent_passage():
    mixed = [_batch(12, ["98.5", "102"])]
    swapped = [_batch(12, ["102", "98.5"])]
    assert first_passage(mixed, start_ns=10, end_ns=20, side=1, entry=Decimal("100"), stop=Decimal("99"), target=Decimal("102")).result == "same_batch_ambiguous"
    assert first_passage(swapped, start_ns=10, end_ns=20, side=1, entry=Decimal("100"), stop=Decimal("99"), target=Decimal("102")).result == "same_batch_ambiguous"


def test_s10_split_keeps_dst_year_together():
    splits = split_manifest(["2023-03-13", "2023-11-06", "2024-01-02"])
    year = next(item for item in splits["outer"] if item["test_year"] == 2023)
    assert "2023-03-13" in year["test"]
    assert "2023-11-06" in year["test"]


def test_s11_missing_future_is_not_neither():
    result = first_passage(
        [_batch(12, ["100.5"])],
        start_ns=10,
        end_ns=20,
        side=1,
        entry=Decimal("100"),
        stop=Decimal("99"),
        target=Decimal("102"),
        coverage={"unknown_intervals": [[12, 20]], "observed_scope_complete": False},
    )
    assert result.result in {"missing_future", "prior_gap_unknown"}
    assert result.result != "neither"


def test_p5_first_passage_includes_tail_span():
    start = 1_000
    horizon = 1_000
    end = start + horizon
    tail = [_batch(end, ["102.00"])]
    result = first_passage(
        tail,
        start_ns=start,
        end_ns=end,
        side=1,
        entry=Decimal("100"),
        stop=Decimal("99"),
        target=Decimal("102"),
    )
    assert result.result == "target_first"
    assert result.resolved_at_ns == end


def test_p7_extrema_and_first_passage_share_closing_endpoint():
    start = 10
    end = 20
    events = [_batch(end, ["101.00"])]
    extrema = interval_extrema(events, start_ns=start, end_ns=end)
    passage = first_passage(
        events,
        start_ns=start,
        end_ns=end,
        side=1,
        entry=Decimal("100"),
        stop=Decimal("99"),
        target=Decimal("101"),
    )
    assert extrema["convention"] == "(t, t+h]"
    assert extrema["high"] == Decimal("101.00")
    assert extrema["high_at_ns"] == end
    assert passage.result == "target_first"
    assert passage.resolved_at_ns == end
