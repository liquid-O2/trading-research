from __future__ import annotations

from datetime import date
from decimal import Decimal

from trading_research.research.method_pack.clocks import MINUTE_NS, et_ns
from trading_research.research.method_pack.objects.range_geometry import (
    REQUIRED_INPUTS,
    build_native_range,
    derived_range,
    native_o005,
    native_o006,
    native_o020,
    native_o025,
    native_o046,
    native_o002,
    native_o047,
    native_o048,
    native_o049,
    native_o050,
    native_o056,
    native_o057,
    native_o058,
    o002,
    o010,
    o015,
    o018,
    o021,
    o024,
    o028,
    o047,
    o050,
    o056,
    o058,
)
from trading_research.research.method_pack.evidence import mark_source_admitted


DAY = date(2026, 2, 24)


class Resolved:
    def __init__(self, start, end, rows, *, coverage_ok=True, instrument_id=42):
        self.start_ns = start
        self.end_ns = end
        self.instrument_id = instrument_id
        self.coverage_ok = coverage_ok
        self.known_at = max((row.get("known_at", row.get("end", row.get("event_ns")))
                             for row in rows), default=end)
        self._rows = rows

    def rows(self):
        return list(self._rows)


def _bar(start, high, low, index, *, complete=True):
    return {
        "bar_id": f"bar-{index}", "instrument_id": 42,
        "start": start, "end": start + MINUTE_NS,
        "known_at": start + MINUTE_NS, "O": Decimal("105"),
        "H": Decimal(str(high)), "L": Decimal(str(low)),
        "C": Decimal("105"), "V": Decimal("10"), "complete": complete,
    }


def _candle(cid, start, O, H, L, C):
    return {"candle_id": cid, "start": start, "end": start + 1,
            "known_at": start + 1, "O": Decimal(str(O)), "H": Decimal(str(H)),
            "L": Decimal(str(L)), "C": Decimal(str(C)), "V": Decimal("100"),
            "complete": True}


def _native_parent(object_id, value, known_at):
    return {"object_id": object_id, "recipe_id": "O005", "state": "computed",
            "value": value, "known_at": known_at, "recipe_base_ok": True,
            "recipe_coverage_ok": True, "evidence_ids": [f"native:{object_id}"],
            "evidence_class": "resolved_native"}


def _source_parent(object_id, value, known_at):
    parent = {"object_id": object_id, "recipe_id": "O023", "state": "supplied",
              "value": value, "known_at": known_at, "recipe_base_ok": True,
              "recipe_coverage_ok": True, "evidence_ids": [f"source:{object_id}"],
              "evidence_class": "supplied_source_audit"}
    for field in value:
        mark_source_admitted(parent, field)
    return parent


def test_native_0600_0900_range_uses_complete_membership_and_freezes_geometry():
    start, end = et_ns(DAY, 6), et_ns(DAY, 9)
    # Three one-hour bars are enough for this native-construction test because
    # they tile the selected interval exactly and are individually complete.
    hour = 60 * MINUTE_NS
    rows = [
        {**_bar(start, 110, 100, 1), "end": start + hour, "known_at": start + hour},
        {**_bar(start + hour, 120, 105, 2), "end": start + 2*hour, "known_at": start + 2*hour},
        {**_bar(start + 2*hour, 115, 102, 3), "end": end, "known_at": end},
    ]
    result = native_o005({"range_id": "NQ:2026-02-24:0600-0900"},
                         Resolved(start, end, rows))
    assert result.state == "computed"
    assert result.value["L"] == 100 and result.value["H"] == 120
    assert result.value["W"] == 20 and result.value["range_frozen"] is True
    assert result.known_at == end

    gapped = [rows[0], {**rows[2], "start": start + 2*hour}]
    partial = native_o005({"range_id": "bad"}, Resolved(start, end, gapped))
    assert partial.state == "hole" and partial.base_ok is True
    assert partial.value["L"] == 100 and partial.value["H"] == 115
    assert partial.value["range_frozen"] is False
    assert partial.coverage_ok is None


def test_native_contact_and_failure_take_measurements_from_actual_parents():
    start, end = et_ns(DAY, 10), et_ns(DAY, 10, 5)
    reference = _native_parent("reference", {"L": Decimal("100"), "H": Decimal("110")}, start-1)
    contact_source = _source_parent("contact-source", {
        "side": "upper", "source_criterion": "literal_close_return",
        "source_reject_evidence": True, "source_hold_evidence": False}, start-1)
    contact_bar = {**_bar(start, 111, 105, 1), "end": end, "known_at": end,
                   "C": Decimal("109")}
    contact = native_o002({"parents": {"reference": reference, "source": contact_source},
        "reference_parent_id": "reference", "selection_parent_id": "contact-source",
        # Caller summaries cannot replace either selected parent.
        "lo": 900, "hi": 901, "source_reject_evidence": False},
        Resolved(start, end, [contact_bar]))
    assert contact.value["sweep_depth"] == Decimal("1")
    assert contact.value["literal_close_return"] is True
    assert contact.value["source_reject"] is True

    failure_source = _source_parent("failure-source", {
        "side": "high", "confirmation_type": "complete_close",
        "source_confirmation": None, "return_inside_box": False}, start-1)
    trade = {"event_id": "sweep", "action": "T", "event_ns": start+MINUTE_NS,
             "known_at": start+MINUTE_NS, "price": Decimal("111")}
    confirm = {**_bar(start+2*MINUTE_NS, 111, 108, 2),
               "C": Decimal("109"), "end": start+3*MINUTE_NS,
               "known_at": start+3*MINUTE_NS}
    failure = native_o047({"parents": {"reference": reference, "source": failure_source},
        "reference_parent_id": "reference", "selection_parent_id": "failure-source",
        "confirmation_bar_id": confirm["bar_id"], "reference_px": 999,
        "side": "low", "use_at": end}, Resolved(start, end, [trade, confirm]))
    assert failure.value["sweep_extreme"] == Decimal("111")
    assert failure.value["failure_confirmed"] is True


def test_comparison_contact_uses_actual_vwap_parent_and_bar_without_source_qualifiers():
    start, end = et_ns(DAY, 10), et_ns(DAY, 10, 1)
    vwap = _parent("vwap", "O030", {"vwap": None, "comparison_vwap": Decimal("100")}, start-1)
    bar = {**_bar(start, 101, 99, 1), "C": Decimal("100.5")}
    result = native_o002({"parents": {"vwap": vwap}, "reference_parent_id": "vwap",
        "variant": "comparison", "value_field": "caller_alias_is_forbidden"},
        Resolved(start, end, [bar]))
    assert result.state == "hole"
    assert result.value["reference_band"] == [Decimal("100"), Decimal("100")]
    assert result.value["observed_high"] == Decimal("101")
    assert result.value["observed_low"] == Decimal("99")
    assert result.value["contact_at"] == end
    assert result.value["price_overlap"] is True
    assert result.value["source_reject"] is None and result.value["source_hold"] is None
    assert "HOLE:O002:source_confirmation" in result.hole_ids


def test_comparison_sweep_uses_actual_reference_and_o004_bar_but_never_source_confirms():
    start, end = et_ns(DAY, 10), et_ns(DAY, 10, 5)
    reference = _parent("box", "O046", {"box_low": Decimal("100"),
        "box_high": Decimal("110")}, start-1)
    bar_value = {**_candle("confirm", start+2*MINUTE_NS, 111, 112, 108, 109),
        "bar_id": "confirm", "instrument_id": 42, "kind": "time", "size": "1m"}
    bar_value.pop("candle_id")
    confirmation = _parent("confirm-parent", "O004", bar_value, bar_value["end"])
    trade = {"event_id": "sweep", "action": "T", "event_ns": start+MINUTE_NS,
             "known_at": start+MINUTE_NS, "price": Decimal("111")}
    result = native_o047({"parents": {"box": reference, "confirm": confirmation},
        "reference_parent_id": "box", "confirmation_bar_parent_id": "confirm-parent",
        "variant": "comparison", "measurement_side": "high", "use_at": end},
        Resolved(start, end, [trade]))
    assert result.state == "hole"
    assert result.value["sweep_extreme"] == Decimal("111")
    assert result.value["confirm_close"] == Decimal("109")
    assert result.value["failure_confirmed"] is None
    assert "HOLE:O047:source_confirmation" in result.hole_ids


def test_native_range_aliases_do_not_promote_caller_source_facts():
    start = et_ns(DAY, 9, 30); end = et_ns(DAY, 16)
    rth = [{**_bar(start, 120, 100, 1), "end": end, "known_at": end}]
    context = native_o020({"rth_active_objectives": ["caller"], "chosen_draw": "caller",
        "current_direction": "long"}, Resolved(start, end, rth))
    assert context.value["rth_active_objectives"] == []
    assert context.value["chosen_draw"] is None and context.value["current_direction"] is None

    short_end = start + 30*MINUTE_NS
    short = [{**_bar(start, 110, 100, 1), "end": short_end, "known_at": short_end}]
    resolved = Resolved(start, short_end, short)
    opening = native_o025({"source_clock_verified": True,
        "subsequent_mid_retrace": start+1}, resolved)
    box = native_o046({"source_clock_verified": True}, resolved)
    prior = native_o048({"period_id": "p", "period_kind": "session", "period_scope": "RTH",
        "period_end": short_end, "active_state": True, "retirement_policy": "touch"}, resolved)
    assert opening.value["or_known"] is None and opening.value["subsequent_mid_retrace"] is None
    assert box.value["source_clock_verified"] is None
    assert prior.value["active_state"] is None and prior.value["retirement_policy"] is None

    manual_start = et_ns(DAY, 20); manual_end = manual_start+30*MINUTE_NS
    manual_rows = [{**_bar(manual_start, 110, 100, 1), "end": manual_end,
                    "known_at": manual_end}]
    manual = native_o006({"source_clock_verified": True, "source_clock_id": "caller",
        "source_version": "manual"}, Resolved(manual_start, manual_end, manual_rows))
    assert manual.value["source_clock_verified"] is None
    assert "HOLE:O006:source_clock" in manual.hole_ids


def test_native_candle_geometry_ignores_unadmitted_source_flags():
    def native_candle(cid, start, O, H, L, C, V=100):
        return {"bar_id": cid, "instrument_id": 42, "start": start, "end": start+1,
            "known_at": start+1, "O": Decimal(str(O)), "H": Decimal(str(H)),
            "L": Decimal(str(L)), "C": Decimal(str(C)), "V": Decimal(str(V)),
            "complete": True}

    candles = [native_candle("c1", 1, 102, 103, 101, 102),
               native_candle("c2", 3, 102, 104, 100, 103),
               native_candle("c3", 5, 103, 106, 102, 105)]
    caller_pattern = native_o056({"candle_ids": ["c1", "c2", "c3"],
        "sweep_side": "low", "selected_entry_mode": "midpoint", "selected_stop": 100},
        Resolved(1, 7, candles))
    assert caller_pattern.state == "invalid"
    measured_pattern = native_o056({"candle_ids": ["c1", "c2", "c3"],
        "variant": "comparison", "measurement_side": "low"}, Resolved(1, 7, candles))
    assert measured_pattern.value["confirmed"] is True
    assert measured_pattern.value["selected_entry_mode"] is None
    assert measured_pattern.value["selected_stop"] is None

    rejection = native_o057({"candle_id": "c2", "side": "lower",
        "source_rejection": True, "allowed_location": True, "stop_policy": "wick"},
        Resolved(3, 4, [candles[1]]))
    assert rejection.state == "invalid"
    measured_rejection = native_o057({"candle_id": "c2", "variant": "comparison",
        "measurement_side": "lower"}, Resolved(3, 4, [candles[1]]))
    assert measured_rejection.value["rejection_band"] == [Decimal("100"), Decimal("102")]
    assert measured_rejection.value["stop_policy"] is None

    history = [native_candle(f"h{i}", i*2, 100, 110, 100, 101) for i in range(14)]
    current = native_candle("current", 30, 100, 110, 100, 102, 200)
    policy = {"current_candle_id": "current", "average_inclusion": "prior_only",
        "reset_policy": "source", "equality_policy": "strict"}
    source_unknown = native_o058(policy, Resolved(0, 31, [*history, current]))
    comparison = native_o058({**policy, "variant": "comparison"},
        Resolved(0, 31, [*history, current]))
    assert source_unknown.value["source_zone_flag"] is None
    assert comparison.value["source_zone_flag"] is True


def test_native_opening_batch_never_uses_arbitrary_tie_order():
    midnight = et_ns(DAY, 0); end = midnight + 10*MINUTE_NS
    source = _source_parent("tdo-source", {"source_clock_verified": True,
        "tdo_required": True, "role": "opening_confirmation",
        "close_through_mode": "below", "side": "short"}, midnight-1)
    tied = [{"event_id": "a", "action": "T", "event_ns": midnight,
             "known_at": midnight, "price": Decimal("100")},
            {"event_id": "b", "action": "T", "event_ns": midnight,
             "known_at": midnight, "price": Decimal("101")}]
    result = native_o049({"parents": {"source": source},
        "selection_parent_id": "tdo-source", "tdo": 999},
        Resolved(midnight, end, tied))
    assert result.state == "hole"
    assert result.value["tdo_price"] is None
    assert result.value["opening_event_id"] is None

    opening = {"event_id": "open", "action": "T", "event_ns": midnight,
               "known_at": midnight, "price": Decimal("100"), "exchange_sequence": 7}
    confirm = {**_bar(midnight+MINUTE_NS, 101, 98, 3),
               "C": Decimal("99"), "end": midnight+6*MINUTE_NS,
               "known_at": midnight+6*MINUTE_NS}
    confirmed = native_o049({"parents": {"source": source},
        "selection_parent_id": "tdo-source", "confirmation_bar_id": confirm["bar_id"],
        "confirmation_close": 999}, Resolved(midnight, end, [opening, confirm]))
    assert confirmed.value["tdo_price"] == Decimal("100")
    assert confirmed.value["source_tdo_close_confirmed"] is True
    assert confirmed.known_at == confirm["known_at"]

    cash_open = et_ns(DAY, 9, 30); cash_end = cash_open + 5*MINUTE_NS
    reclaim_source = _source_parent("reclaim-source",
        {"source_reclaim_criterion": "strict"}, cash_open-1)
    cash_tied = [{**row, "event_ns": cash_open, "known_at": cash_open}
                 for row in tied]
    cash = native_o050({"parents": {"source": reclaim_source},
        "selection_parent_id": "reclaim-source", "source_reclaim_criterion": "anything"},
        Resolved(cash_open, cash_end, cash_tied))
    assert cash.state == "hole"
    assert cash.value["cash_open"] is None
    assert cash.value["source_open_reclaim"] is None

    path = [{"event_id": "open", "action": "T", "event_ns": cash_open,
             "known_at": cash_open, "price": Decimal("100")},
            {"event_id": "below", "action": "T", "event_ns": cash_open+MINUTE_NS,
             "known_at": cash_open+MINUTE_NS, "price": Decimal("99")},
            {"event_id": "reclaim", "action": "T", "event_ns": cash_open+2*MINUTE_NS,
             "known_at": cash_open+2*MINUTE_NS, "price": Decimal("101")}]
    reclaimed = native_o050({"parents": {"source": reclaim_source},
        "selection_parent_id": "reclaim-source", "source_reclaim_criterion": "garbage"},
        Resolved(cash_open, cash_end, path))
    assert reclaimed.value["cash_open"] == Decimal("100")
    assert reclaimed.value["reclaim_at"] == cash_open+2*MINUTE_NS
    assert reclaimed.value["source_open_reclaim"] is True


def test_o002_missing_bar_high_stays_unknown_and_lower_side_is_symmetric():
    missing = o002({"lo": 100, "hi": 101, "side": "upper",
                    "bars": [{"L": 100.5, "C": 100.75, "complete": True}]})
    assert missing.value["price_overlap"] is None
    assert missing.value["sweep_depth"] is None
    assert missing.coverage_ok is None

    lower = o002({"lo": 100, "hi": 101, "side": "lower", "q": ".25",
                  "bars": [{"L": 99, "H": 100.5, "C": 100.25,
                            "complete": True}], "source_criterion": "supplied",
                  "source_reject_evidence": True})
    assert lower.value["price_overlap"] is True
    assert lower.value["sweep_depth"] == 1
    assert lower.value["sweep_depth_ticks"] == 4
    assert lower.value["literal_close_return"] is True


def test_retrospective_path_keeps_absence_unknown_until_window_coverage_finishes():
    prefix = o010({"H": 120, "L": 100, "events": [{"t": 20, "price": 121}],
                   "window_start": 10, "window_end": 40, "as_of": 30,
                   "coverage_ok": True})
    complete = o010({"H": 120, "L": 100,
                     "events": [{"t": 20, "price": 121},
                                {"t": 31, "price": 110}, {"t": 35, "price": 99}],
                     "window_start": 10, "window_end": 40, "as_of": 40,
                     "coverage_ok": True})
    assert prefix.value["path"] == "high_so_far"
    assert prefix.coverage_ok is None
    assert complete.value["path"] == "both"
    assert complete.value["first_side"] == "high"
    assert complete.value["eq_return_at"] == 31


def test_extensions_bind_the_selected_parent_and_do_not_substitute_outer_width():
    valid = o015({"L": 106, "H": 114, "W": 8, "parent_id": "inner",
                  "coordinate_convention_verified": True, "known_at": 10})
    invalid = o015({"L": 106, "H": 114, "W": 20, "parent_id": "inner",
                    "coordinate_convention_verified": True, "known_at": 10})
    assert valid.value["upper_band"] == [Decimal("124.64"), Decimal("127.28")]
    assert invalid.state == "invalid" and invalid.base_ok is False


def test_source_only_evrange_and_action_windows_never_default_to_true_or_a_date():
    missing = o018({"ev_mid": 111, "use_at": 20})
    assert missing.value["ev_reference_known"] is None
    assert missing.value["automatic_ev"] is None

    no_window = o021({"event_ns": et_ns(DAY, 9, 45), "purpose": "reversal",
                      "branch": "judas"})
    boundary = o021({"event_ns": 20, "window_start": 10, "window_end": 20,
                     "purpose": "reversal", "branch": "judas"})
    assert no_window.value["source_time_window"] is None
    assert "HOLE:O021:source_window" in no_window.hole_ids
    assert boundary.value["source_time_window"] is None
    assert boundary.value["boundary_ambiguous"] is True


def test_three_failures_are_distinct_failed_attempts_at_same_level_and_branch():
    attempts = [
        {"attempt_id": "a1", "level_id": "x", "branch": "rev", "outcome": "failed", "ended_at": 11},
        {"attempt_id": "a1", "level_id": "x", "branch": "rev", "outcome": "failed", "ended_at": 12},
        {"attempt_id": "a2", "level_id": "other", "branch": "rev", "outcome": "failed", "ended_at": 13},
        {"attempt_id": "a2", "level_id": "x", "branch": "rev", "outcome": "win", "ended_at": 14},
        {"attempt_id": "a2", "level_id": "x", "branch": "rev", "outcome": "failed", "ended_at": 15},
        {"attempt_id": "a3", "level_id": "x", "branch": "rev", "outcome": "failed", "ended_at": 25},
    ]
    early = o024({"attempts": attempts, "level_id": "x", "branch": "rev",
                  "evaluation_at": 20, "invalidation_evidence_complete": True})
    late = o024({"attempts": attempts, "level_id": "x", "branch": "rev",
                 "evaluation_at": 30, "prior_allocation": 4,
                 "new_allocation": 2, "continued_after_failure": True})
    assert early.value["failed_attempt_count"] == 2
    assert early.value["three_failed_attempts"] is False
    assert late.value["failed_attempt_count"] == 3
    assert late.value["reversal_invalidated"] is True
    assert late.value["later_allocation_ok"] is True


def test_equal_reference_requires_dated_contributors_and_explicit_band():
    result = o028({"contributors": [
        {"id": "h1", "price": 120, "confirmed_at": 10},
        {"id": "h2", "price": 120, "confirmed_at": 12}],
        "equality_criterion": "exact", "objective_band": [120, 120],
        "selected_at": 13, "use_at": 14, "coverage_ok": True})
    assert result.value["prices_equal"] is True
    assert result.value["reference_known"] is True
    assert result.value["remaining_objective"] is True
    future = o028({"contributors": [{"id": "h1", "price": 120, "confirmed_at": 20}],
                   "equality_criterion": "exact", "objective_band": [120, 120],
                   "selected_at": 20, "use_at": 14, "coverage_ok": True})
    assert future.value["reference_known"] is False


def test_sweep_failure_requires_strict_side_and_strict_event_order_in_both_directions():
    high = o047({"reference_px": 110, "side": "high", "reference_known_at": 5,
                 "events": [{"t": 10, "price": 111}], "confirmation_type": "complete_close",
                 "confirmation_bar": {"C": 109, "end": 15, "known_at": 15, "complete": True},
                 "decision_at": 16, "coverage_ok": True})
    low = o047({"reference_px": 100, "side": "low", "reference_known_at": 5,
                "events": [{"t": 10, "price": 99}], "confirmation_type": "complete_close",
                "confirmation_bar": {"C": 101, "end": 15, "known_at": 15, "complete": True},
                "decision_at": 16, "coverage_ok": True})
    reversed_order = o047({"reference_px": 110, "side": "high", "reference_known_at": 5,
                           "events": [{"t": 15, "price": 111}], "confirmation_type": "complete_close",
                           "confirmation_bar": {"C": 109, "end": 14, "known_at": 14, "complete": True},
                           "decision_at": 16, "coverage_ok": True})
    assert high.value["failure_confirmed"] is True
    assert low.value["failure_confirmed"] is True
    assert reversed_order.state == "invalid"


def test_cash_open_path_is_clipped_to_as_of_and_never_backdates_reclaim():
    values = {"open_px": 100, "open_at": 10,
              "events": [{"t": 12, "price": 99}, {"t": 14, "price": 101}],
              "source_reclaim_criterion": "strict"}
    early = o050({**values, "as_of": 13})
    late = o050({**values, "as_of": 15})
    assert early.value["cross_below_at"] == 12
    assert early.value["reclaim_at"] is None
    assert early.known_at == 12
    assert late.value["reclaim_at"] == 14 and late.known_at == 14


def test_orderblock_pattern_is_complete_c2_range_and_has_bearish_mirror():
    bull = o056({"c1": _candle("b1", 1, 102, 103, 101, 102),
                 "c2": _candle("b2", 3, 102, 104, 100, 103),
                 "c3": _candle("b3", 5, 103, 106, 102, 105),
                 "sweep_side": "low", "selected_entry_mode": "midpoint",
                 "selected_stop": 100, "timeframe": "2m"})
    bear = o056({"c1": _candle("s1", 1, 102, 103, 100, 101),
                 "c2": _candle("s2", 3, 102, 105, 101, 102),
                 "c3": _candle("s3", 5, 102, 103, 99, 100),
                 "sweep_side": "high", "selected_entry_mode": "retrace",
                 "selected_stop": 105, "timeframe": "2m"})
    assert bull.value["confirmed"] is True and bull.value["ob_band"] == [100, 104]
    assert bear.value["confirmed"] is True and bear.value["ob_band"] == [101, 105]
    assert REQUIRED_INPUTS["O056"] == ("c1", "c2", "c3", "sweep_side")


def test_absorption_uses_exactly_fourteen_prior_complete_causal_bars():
    history = [_candle(f"h{i}", i*2, 100, 110, 100, 101) for i in range(14)]
    for candle in history:
        candle["V"] = Decimal("100")
    current = _candle("current", 30, 100, 110, 100, 102)
    current["V"] = Decimal("200")
    settings = {"bar": current, "history": history,
                "average_inclusion": "prior_only", "reset_policy": "source",
                "equality_policy": "strict"}
    result = o058(settings)
    short = o058({**settings, "history": history[:-1]})
    assert result.value["body_ratio"] == Decimal(".2")
    assert result.value["volume_average"] == 100
    assert result.value["volume_ratio"] == 2
    assert result.value["source_zone_flag"] is True
    assert short.value["source_zone_flag"] is None
    assert "HOLE:O058:history_14" in short.hole_ids


def test_absorption_volume_only_helper_keeps_missing_history_identity_explicit():
    result = o058({"O": 100, "H": 110, "L": 100, "C": 102, "V": 200,
                   "known_at": 30, "prior_volumes": [100] * 14,
                   "average_inclusion": "prior_only", "reset_policy": "source",
                   "equality_policy": "strict"})

    assert result.value["body_ratio"] == Decimal(".2")
    assert result.value["volume_average"] == 100
    assert result.value["volume_ratio"] == 2
    assert result.value["small_body"] is True
    assert result.value["high_volume"] is True
    assert result.value["source_zone_flag"] is None
    assert result.value["history_ids"] == [None] * 14
    assert {"HOLE:O058:current_candle_identity", "HOLE:O058:history_identity",
            "HOLE:O058:history_clock"} <= set(result.hole_ids)
    assert result.state == "hole" and result.known_at is None


def test_absorption_missing_identity_is_a_hole_but_duplicate_identity_is_invalid():
    history = [_candle(f"h{i}", i*2, 100, 110, 100, 101) for i in range(14)]
    current = _candle("current", 30, 100, 110, 100, 102)
    settings = {"bar": current, "history": history,
                "average_inclusion": "prior_only", "reset_policy": "source",
                "equality_policy": "strict"}
    history[0]["candle_id"] = None
    missing = o058(settings)
    history[0]["candle_id"] = history[1]["candle_id"]
    duplicate = o058(settings)

    assert missing.value["history_ids"][0] is None
    assert missing.value["source_zone_flag"] is None
    assert "HOLE:O058:history_identity" in missing.hole_ids
    assert missing.state == "hole"
    assert duplicate.state == "invalid" and duplicate.base_ok is False


def _parent(object_id, recipe_id, value, known_at=10, *, evidence_class="resolved_native"):
    return {"object_id": object_id, "recipe_id": recipe_id, "value": value,
            "known_at": known_at, "state": "computed", "evidence_class": evidence_class,
            "evidence_ids": [f"ev:{object_id}"], "recipe_coverage_ok": True}


def test_derived_projection_uses_selected_native_parent_and_ignores_summary_geometry():
    parent = _parent("range", "O005", {"range_id": "native-range", "L": Decimal(100),
        "H": Decimal(120), "W": Decimal(20)})
    result = derived_range("O007", {"range_parent_id": "range", "L": 999, "H": 1000}, [parent])
    assert result.value["parent_id"] == "native-range"
    assert result.value["q25"] == 105 and result.value["eq"] == 110 and result.value["q75"] == 115


def test_derived_orderblock_requires_three_distinct_resolved_native_candles():
    candles = [
        _parent("c1", "O004", _candle("b1", 1, 102, 103, 101, 102), 3),
        _parent("c2", "O004", _candle("b2", 3, 102, 104, 100, 103), 5),
        _parent("c3", "O004", _candle("b3", 5, 103, 106, 102, 105), 7),
    ]
    for row in candles:
        value = row["value"]
        value.update({"bar_id": value.pop("candle_id"), "instrument_id": "NQ", "kind": "time",
                      "size": "2m", "known_at": row["known_at"], "V": Decimal(10)})
    selection = _parent("selection", "O022", {"sweep_side": "low", "selected_entry_mode": "midpoint",
        "selected_stop": Decimal(100), "timeframe": "2m"}, 1, evidence_class=None)
    selection["state"] = "supplied"
    result = derived_range("O056", {"candle_parent_ids": ["c1", "c2", "c3"],
        "selection_parent_id": "selection"}, [*candles, selection])
    assert result.value["confirmed"] is True
    assert result.value["candle_ids"] == ["b1", "b2", "b3"]
    duplicate = derived_range("O056", {"candle_parent_ids": ["c1", "c1", "c3"],
        "selection_parent_id": "selection"}, [*candles, selection])
    assert duplicate.state == "invalid"
