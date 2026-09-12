from decimal import Decimal
from types import SimpleNamespace

from trading_research.research.method_pack.contracts import OUTPUT_SCHEMAS as CONTRACT_SCHEMAS
from trading_research.research.method_pack.contracts import validate_output
from trading_research.research.method_pack.objects.local_flow import (
    LOCAL_FLOW_SCHEMAS, NATIVE_PRODUCERS, OUTPUT_SCHEMAS, REGISTRATION_OVERRIDES,
)


def run(rid, **values):
    return REGISTRATION_OVERRIDES[rid](values)


def trade(event_id, at, price, size, side, **extra):
    return {"event_id": event_id, "event_ns": at, "known_at": at, "price": Decimal(str(price)),
            "size": size, "side": side, "action": "T", **extra}


def test_every_local_flow_payload_is_complete_and_typed_even_when_unavailable():
    previous = dict(CONTRACT_SCHEMAS)
    try:
        CONTRACT_SCHEMAS.update(OUTPUT_SCHEMAS)
        for rid, producer in REGISTRATION_OVERRIDES.items():
            result = producer({})
            assert set(LOCAL_FLOW_SCHEMAS[rid]) <= set(result.value)
            validate_output(result)
    finally:
        CONTRACT_SCHEMAS.clear(); CONTRACT_SCHEMAS.update(previous)


def test_executed_tape_preserves_b_a_n_events_and_ignores_quote_updates():
    result = run("O098", events=[trade("b", 1, 100, 7, "B"), trade("a", 2, 100, 4, "A"),
        trade("n", 3, 100, 2, "N"), {"event_id": "q", "event_ns": 4, "known_at": 4,
        "price": 100, "size": 100, "side": "B", "action": "M"}])
    assert [r["event_id"] for r in result.value["event_records"]] == ["b", "a", "n"]
    assert result.value["total"] == 13 and result.value["delta"] is None
    assert result.value["delta_interval"] == [Decimal(1), Decimal(5)]


def test_big_trade_settings_keep_per_print_and_cluster_markers_distinct():
    rows = [trade("a", 1, 100, 60, "B", cluster_id="x"),
            trade("b", 2, 100, 60, "B", cluster_id="x"), trade("c", 3, 101, 100, "A", cluster_id="y")]
    per_print = run("O099", trades=rows, threshold=100, comparator=">=", mode="per_print")
    clustered = run("O099", events=rows, source_setting={"setting_id": "x", "threshold": 100,
        "comparator": ">=", "aggregation_mode": "cluster", "cluster_rule": "cluster_id"})
    assert per_print.value["markers"] == 1
    assert clustered.value["markers"] == 2
    assert per_print.value["marker_events"][0]["side"] == "A"


def test_dom_bbo_change_does_not_invent_execution_depth_or_hidden_reserve():
    result = run("O100", band=[100, 100], reset_at=0, quotes=[
        {"quote_id": "q1", "at": 1, "bid": 100, "ask": 100.25, "bid_size": 10, "ask_size": 9},
        {"quote_id": "q2", "at": 3, "bid": 100, "ask": 100.25, "bid_size": 15, "ask_size": 9},
    ], events=[trade("s", 2, 100, 4, "A")], depth_coverage="bbo")
    assert result.value["execution_evidence"] is True
    assert result.value["consumed_and_replenished"] is True
    assert result.value["verified_hidden_reserve"] is None
    assert result.value["depth_coverage"] == "bbo"


def test_scalar_lifecycle_cannot_verify_replenishment_p14():
    for consumed, refresh in [(0, 8), (6, 0), (0, 0)]:
        result = run("O102", lifecycle={"consumed": consumed, "refresh": refresh, "final_display": 12}, known_at=10)
        assert result.value["verified_replenishment"] is None
        assert result.state == "hole"


def test_absorption_measurement_does_not_use_future_reversal_as_passive_proof():
    result = run("O101", band=[109.75, 110], events=[trade("b", 1, 110, 100, "B")],
        aggressive_side="buy", response_start_price=110, response_end_price=110.25,
        q=Decimal("0.25"), later_decline=2, known_at=2)
    assert result.value["price_progress_ticks"] == 1
    assert result.value["source_absorption"] is None
    assert result.value["later_decline_repairs"] is False


def test_directional_reward_and_later_return_defense_are_separate():
    adverse = run("O104", origin=100, direction="long", reward_price=Decimal("99.75"),
                  reward_at=2, return_at=3, renewed_defense_at=4, q=Decimal("0.25"))
    assert adverse.value["reward_ticks"] == -1
    assert adverse.value["directional_reward"] is False
    assert adverse.value["retest_is_reward"] is False


def test_cvd_obeys_reset_action_asof_and_preserves_unknown_side():
    rows = [trade("old", 1, 100, 100, "B"), trade("b", 3, 100, 7, "B"),
            trade("a", 4, 100, 4, "A"), trade("n", 5, 100, 2, "N"),
            trade("future", 9, 100, 50, "B"), {"event_id": "q", "event_ns": 4,
            "known_at": 4, "price": 100, "size": 99, "side": "B", "action": "M"}]
    result = run("O105", events=rows, reset_id="r", reset_at=2, as_of=5,
                 reference=0, reference_unit="contracts")
    assert result.value["event_ids"] == ["b", "a", "n"]
    assert result.value["known_cvd"] == 3 and result.value["cvd"] is None
    assert result.value["delta_interval"] == [Decimal(1), Decimal(5)]


def test_candle_disagreement_requires_actual_same_candle_executions():
    empty = run("O106", O=100, C=101, candle_id="k", events=[])
    assert empty.value["delta"] is None and empty.value["opposed_signs"] is None
    full = run("O106", O=100, C=101, candle_id="k", events=[
        trade("b", 1, 100, 4, "B", candle_id="k"), trade("a", 2, 101, 10, "A", candle_id="k")])
    assert full.value["opposed_signs"] is True


def test_unknown_volume_makes_delta_concentration_an_interval_p15():
    result = run("O107", B=7, A=4, N=2, source_spike=True)
    assert result.value["fraction"] is None
    assert result.value["fraction_interval"] == [Decimal(1)/13, Decimal(5)/13]


def test_poc_flip_needs_two_visible_snapshots_of_the_same_candle():
    one = run("O108", candle_id="k", snapshots=[{"snapshot_id": "s1", "candle_id": "k", "poc": 100, "known_at": 1}], use_at=1)
    assert one.state == "hole" and one.value["change"] is None
    two = run("O108", candle_id="k", snapshots=[
        {"snapshot_id": "s1", "candle_id": "k", "poc": 100, "known_at": 1},
        {"snapshot_id": "s2", "candle_id": "k", "poc": 101, "known_at": 2}], use_at=2)
    assert two.value["change"] == 1 and two.value["flip_at"] == 2
    reversed_input = run("O108", candle_id="k", snapshots=list(reversed([
        {"snapshot_id": "s1", "candle_id": "k", "poc": 100, "known_at": 1},
        {"snapshot_id": "s2", "candle_id": "k", "poc": 101, "known_at": 2}])), use_at=2)
    assert reversed_input.value == two.value


def test_diagonal_imbalance_finds_buy_and_sell_subruns_and_obeys_zero_rule():
    rows = [
        {"price": 100, "B": 1, "A": 10}, {"price": 101, "B": 40, "A": 10},
        {"price": 102, "B": 50, "A": 10}, {"price": 103, "B": 5, "A": 50},
        {"price": 104, "B": 10, "A": 60}, {"price": 105, "B": 10, "A": 1},
    ]
    result = run("O109", footprint_rows=rows, q=1, ratio_min=4, row_count=2,
                 zero_rule="does_not_qualify", candle_id="k")
    assert result.value["buy_runs"][0]["prices"] == [Decimal(101), Decimal(102)]
    assert result.value["sell_runs"][0]["prices"] == [Decimal(103), Decimal(104)]
    zero = run("O109", footprint_rows=[{"price": 100, "B": 0, "A": 0},
        {"price": 101, "B": 10, "A": 0}], q=1, ratio_min=4, row_count=1)
    assert zero.value["buy_comparisons"][1]["relation"] == "unbounded"
    assert zero.value["buy_comparisons"][1]["qualifies"] is None


def test_same_price_zero_denominator_is_not_silently_false():
    result = run("O110", buy_volume=35, sell_volume=0, rule="350_of")
    assert result.value["buy_relation"] == "unbounded"
    assert result.value["source_350_flag"] is None


def test_liftoff_requires_all_ordered_stages_and_directional_reward_p16():
    partial = run("O115", origin=100, direction="long", reward_price=101,
                  stage_ledger={"liftoff": 4, "entry": 5}, q=Decimal("0.25"))
    assert partial.value["order_ok"] is None and partial.state == "hole"
    full = run("O115", origin=100, direction="long", reward_price=101,
        stage_ledger={"defense": 1, "replenishment": 2, "exhaustion": 3, "liftoff": 4, "entry": 5},
        defender_aggression_events=[{"event_id": "x", "at": 3}], entry=Decimal("101.25"), q=Decimal("0.25"))
    assert full.value["order_ok"] is True and full.value["directional_reward"] is True

    unsigned = run("O115", origin=100, reward_price=101,
        stage_ledger={"defense": 1, "replenishment": 2, "exhaustion": 3, "liftoff": 4, "entry": 5},
        defender_aggression_events=[{"event_id": "x", "at": 3}],
        entry=Decimal("101.25"), q=Decimal("0.25"))
    assert unsigned.value["reward_points"] == 1
    assert unsigned.value["directional_reward"] is None
    assert unsigned.state == "hole"


def test_native_candle_footprint_is_complete_by_tick_and_keeps_unknown_volume():
    result = run("O120", candle_id="k", instrument_id="NQ", O=100, H=101, L=Decimal("99.5"), C=Decimal("100.5"),
        tick_size=Decimal("0.5"), formation_start=0, formation_end=10, as_of=10, coverage_ok=True,
        events=[trade("b",1,100,7,"B",candle_id="k"), trade("a",2,Decimal("100.5"),4,"A",candle_id="k"), trade("n",3,101,2,"N",candle_id="k")])
    assert [r["price"] for r in result.value["rows"]] == [Decimal("99.5"), Decimal(100), Decimal("100.5"), Decimal(101)]
    assert result.value["total_volume"] == 13 and result.value["delta"] is None
    assert result.value["unknown_by_price"]["101"] == 2


def test_native_adapters_do_not_promote_caller_panel_or_interpretation_to_observation():
    rows = [trade("a", 1, 100, 2, "A", instrument_id="NQ"),
            trade("b", 2, 101, 3, "B", instrument_id="NQ")]
    resolved = SimpleNamespace(rows=lambda: rows, instrument_id="NQ", start_ns=0, end_ns=3,
                               known_at=2, coverage_ok=True, instrument_definition=None)
    speed = NATIVE_PRODUCERS["O111"]({"source_panel_value": 99}, resolved)
    approach = NATIVE_PRODUCERS["O113"]({"source_arrival": True, "touch_at": 3}, resolved)
    assert speed.value["source_panel_value"] is None
    assert speed.hole_ids == ["HOLE:O111:panel"]
    assert approach.value["aggressive_arrival"] is None
    assert approach.hole_ids == ["HOLE:O113:interpretation"]
