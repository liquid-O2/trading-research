"""P15-18 refinement neighborhoods, gates, ledger and retention."""

from __future__ import annotations

import random

import pytest

from trading_research.errors import ContractError
from trading_research.research.contracts.evaluation import holm, moving_block_bootstrap
from trading_research.research.rule_discovery.refinement import (
    ATTRIBUTION_ORDER,
    CONTROL_OFFSETS,
    HOLM_ALPHA,
    MAX_NEIGHBORS_PER_BANK,
    MAX_NEIGHBORS_PER_FAMILY,
    MAX_REFINED_PLUS_COMBINED,
    MINUTE_NS,
    NEIGHBORHOODS,
    RETENTION_STATUSES,
    TRIAL_RECORD_FIELDS,
    TrialLedger,
    attribute_failure,
    centered_bootstrap_pvalue,
    combine_candidates,
    evaluate_promotion,
    family_dispositions,
    generate_neighbors,
    make_trial_record,
    neighborhood_values,
    rank_inner,
    select_banks,
    selected_rules_by_fold,
    simpler_wins,
    support_sensitivity,
)


def _fold(**kwargs):
    body = {
        "outer_fold": 2022,
        "fit_window": {"start": "2020-01-01", "end": "2021-06-30"},
        "tune_window": {"start": "2021-07-01", "end": "2021-09-30"},
        "calibration_window": {"start": "2021-10-01", "end": "2021-12-31"},
        "fit_cutoff_ns": 100 * MINUTE_NS,
        "outcome_exposure_cutoff": "2021-12-31",
        "issue_at_ns": 100 * MINUTE_NS,
        "synthetic": True,
    }
    body.update(kwargs)
    body["synthetic"] = True
    return body


def _candidate(**kwargs):
    body = {
        "candidate_id": "parent-f1",
        "family": "JJ-TBR",
        "branch": "judas_reversal",
        "bank": "Formation",
        "recipe_id": "F1",
        "parameters": {"minutes": 60},
        "changed_axis": "minutes",
        "changed_axes": 1,
        "required_stages": ["formation"],
        "trial_id": "parent-1",
        "synthetic": True,
    }
    body.update(kwargs)
    body["synthetic"] = True
    return body


def _diag(**kwargs):
    body = {
        "runtime_failure": False,
        "timed_out": False,
        "candidate_entries": 80,
        "baseline_entries": 100,
        "objective_reached": True,
        "nearest_approach_S": 1.0,
        "adverse_S_before_favorable_0_5S": 0.0,
        "favorable_0_5S_reached": True,
        "missed_move_share": 0.1,
        "family_median_missed_move_share": 0.2,
        "stop_first_share": 0.1,
        "family_baseline_stop_first_share": 0.2,
        "cost_stress_sign_reversal": False,
        "resolved_opportunities": 100,
        "eligible_test_days": 30,
        "supported_outer_blocks": 3,
        "unexplained_coverage_loss": False,
        "synthetic": True,
    }
    body.update(kwargs)
    body["synthetic"] = True
    return body


def _inner_candidate(bank: str, candidate_id: str, mean: float, improvement: float, **kwargs):
    body = _candidate(
        bank=bank,
        candidate_id=candidate_id,
        recipe_id=kwargs.pop("recipe_id", "F1"),
        parameters=kwargs.pop("parameters", {"minutes": 30}),
        changed_axes=kwargs.pop("changed_axes", 1),
        inner_tuning={
            "mean_daily_net_points": mean,
            "improvement_vs_b02": improvement,
            "support_opportunities": kwargs.pop("support_opportunities", 12),
            "support_days": kwargs.pop("support_days", 8),
            "inner_support_ok": kwargs.pop("inner_support_ok", True),
        },
    )
    body.update(kwargs)
    body["synthetic"] = True
    return body


def _promo_candidate(**kwargs):
    body = {
        "trial_id": "t-main",
        "candidate_id": "c-main",
        "daily_diff": [1.0] * 30,
        "resolved_opportunities": 100,
        "eligible_test_days": 30,
        "supported_outer_blocks": 3,
        "block_improvements": [1.0, 1.0, 1.0],
        "candidate_entries": 80,
        "baseline_entries": 100,
        "software_causality_pass": True,
        "cost_stress_sign_reversal": False,
        "unexplained_coverage_loss": False,
        "synthetic": True,
    }
    body.update(kwargs)
    body["synthetic"] = True
    return body


def _axis_values(recipe_id: str, parameters: dict, axis: str) -> list:
    return [row["value"] for row in neighborhood_values(recipe_id, parameters) if row["axis"] == axis]


def test_neighborhood_f1():
    rows = neighborhood_values("F1", {"minutes": 60})
    assert [row["value"] for row in rows] == [30, 60, 90]
    assert [row["axis"] for row in rows] == ["minutes", "minutes", "minutes"]
    neighbors = generate_neighbors("JJ-TBR", _fold(), [_candidate(recipe_id="F1", parameters={"minutes": 60})])
    by_minutes = {row["parameters"]["minutes"]: row for row in neighbors}
    assert by_minutes[30]["status"] == "attempted"
    assert by_minutes[60]["status"] == "duplicate"
    assert by_minutes[90]["status"] == "attempted"
    assert by_minutes[30]["candidate_id"] == "JJ-TBR:judas_reversal:F1:minutes=30"


def test_neighborhood_f2():
    rows = neighborhood_values("F2", {"median_sessions": 20, "max_minutes": 180})
    assert [row["value"] for row in rows] == [0.75, 1.0, 1.25]
    assert all(row["parameters"]["median_sessions"] == 20 for row in rows)
    assert all(row["axis"] == "volume_threshold_multiplier" for row in rows)


def test_neighborhood_f3():
    params = {"lengths": "15,30,60", "width_mult": "0.75", "efficiency": "0.35"}
    rows = neighborhood_values("F3", params)
    width_rows = [row for row in rows if row["axis"] == "width_S"]
    eff_rows = [row for row in rows if row["axis"] == "efficiency"]
    assert [row["value"] for row in width_rows] == [0.5, 0.75, 1.0]
    assert [row["parameters"]["efficiency"] for row in width_rows] == [0.35, 0.35, 0.35]
    assert [row["value"] for row in eff_rows] == [0.2, 0.35, 0.5]
    assert [row["parameters"]["width_S"] for row in eff_rows] == [0.75, 0.75, 0.75]
    assert len(rows) == 6


def test_neighborhood_p():
    p1 = neighborhood_values("P1", {"bandwidth": 0})
    p2 = neighborhood_values("P2", {"bandwidth": 2})
    assert _axis_values("P1", {"bandwidth": 0}, "bandwidth") == [0, 2, 4]
    assert _axis_values("P1", {"bandwidth": 0}, "prominence") == [0.10, 0.20, 0.30]
    assert all(row["parameters"]["prominence"] == 0.20 for row in p1 if row["axis"] == "bandwidth")
    assert all(row["parameters"]["bandwidth"] == 0 for row in p1 if row["axis"] == "prominence")
    assert all(row["parameters"]["bandwidth"] == 2 for row in p2 if row["axis"] == "prominence")
    assert all(row["parameters"]["prominence"] == 0.20 for row in p2 if row["axis"] == "bandwidth")


def test_neighborhood_r1_r2():
    assert [row["value"] for row in neighborhood_values("R1", {"band": "vwap_pm_1_dispersion", "frozen": True})] == [
        0.5,
        1.0,
        1.5,
    ]
    assert neighborhood_values("R2", {"edge": "prior_completed_session"}) == []
    neighbors = generate_neighbors(
        "SIRES",
        _fold(),
        [_candidate(family="SIRES", recipe_id="R2", bank="Reference", parameters={"edge": "prior_completed_session"})],
    )
    assert len(neighbors) == 1
    assert neighbors[0]["status"] == "not_applicable"
    assert neighbors[0]["reason"] == "no_numeric_refinement"


def test_neighborhood_c1_c2_c3():
    assert [row["value"] for row in neighborhood_values("C1", {"window_minutes": 5})] == [2, 5, 10]
    assert [row["value"] for row in neighborhood_values("C2", {"half_life_s": 300})] == [120, 300, 600]
    assert [row["value"] for row in neighborhood_values("C3", {"history_sessions": 20})] == [10, 20, 40]


def test_neighborhood_s_deadline():
    rows = neighborhood_values("S1", {"deadline_s": 600})
    assert [row["value"] for row in rows] == [5, 10, 15]
    assert [row["parameters"]["deadline_s"] for row in rows] == [300, 600, 900]
    assert [row["axis"] for row in rows] == ["deadline_minutes", "deadline_minutes", "deadline_minutes"]


def test_neighborhood_s_reclaim():
    rows = neighborhood_values("S2", {"favorable_ticks": 2})
    assert [row["value"] for row in rows] == [1, 2, 4]
    both = neighborhood_values("S3", {"c1": "0.20", "cohort_s": 120})
    pairs = [(row["axis"], row["value"]) for row in both]
    assert pairs == [
        ("deadline_minutes", 5),
        ("deadline_minutes", 10),
        ("deadline_minutes", 15),
        ("favorable_ticks", 1),
        ("favorable_ticks", 2),
        ("favorable_ticks", 4),
    ]
    assert len(both) == 6
    deadline_rows = [row for row in both if row["axis"] == "deadline_minutes"]
    assert all("favorable_ticks" not in row["parameters"] for row in deadline_rows)
    s4 = neighborhood_values("S4", {"pressure_s": 120})
    assert len(s4) == 6


def test_neighborhood_m1_m2():
    assert [row["value"] for row in neighborhood_values("M1", {"max_prior_contacts": 1})] == [0, 1, 2]
    assert [row["value"] for row in neighborhood_values("M2", {"prior_reaction": "0.25S"})] == [0.1, 0.25, 0.5]


def test_neighborhood_t():
    values = [-30, -15, 0, 15, 30]
    for recipe_id in ("T1", "T2", "T3", "T4"):
        rows = neighborhood_values(recipe_id, {"shift_minutes": 15})
        assert [row["value"] for row in rows] == values
        assert [row["axis"] for row in rows] == ["shift_minutes"] * 5


def _overflow_parent(bank: str, branch: str) -> dict:
    return _candidate(
        recipe_id="OVERFLOW",
        bank=bank,
        branch=branch,
        parameters={"refinement_axis": "cap_value", "refinement_values": list(range(15))},
    )


def test_caps_12_24_25():
    fold = _fold()
    one = generate_neighbors("JJ-TBR", fold, [_overflow_parent("Formation", "b1")])
    assert len([row for row in one if row["status"] == "attempted"]) == MAX_NEIGHBORS_PER_BANK
    assert len([row for row in one if row["reason"] == "cap_per_bank"]) == 3
    three = generate_neighbors(
        "JJ-TBR",
        fold,
        [
            _overflow_parent("Formation", "b1"),
            _overflow_parent("Profile", "b2"),
            _overflow_parent("Delta", "b3"),
        ],
    )
    attempted = [row for row in three if row["status"] == "attempted"]
    family_capped = [row for row in three if row["reason"] == "cap_per_family"]
    assert len(attempted) == MAX_NEIGHBORS_PER_FAMILY
    assert family_capped
    assert all(row["bank"] == "Delta" for row in family_capped)
    a = _candidate(candidate_id="ing-a", parameters={"minutes": 30})
    b = _candidate(candidate_id="ing-b", parameters={"dispersion": 0.5}, bank="Reference", recipe_id="R1")
    assert combine_candidates("JJ-TBR", fold, a, b, b02_score=0.0, score_a=2.0, score_b=2.0, combo_score=3.0, refined_count=24)[
        "changed_axes"
    ] == 2
    assert (
        combine_candidates(
            "JJ-TBR",
            fold,
            a,
            b,
            b02_score=0.0,
            score_a=2.0,
            score_b=2.0,
            combo_score=3.0,
            refined_count=MAX_REFINED_PLUS_COMBINED,
        )
        is None
    )


def test_duplicate_and_inapplicable():
    fold = _fold()
    parent = _candidate(parameters={"minutes": 60})
    already = [_candidate(candidate_id="done-30", parameters={"minutes": 30}, recipe_id="F1")]
    rows = generate_neighbors("JJ-TBR", fold, [parent], attempted=already)
    by_minutes = {row["parameters"]["minutes"]: row for row in rows}
    assert by_minutes[30]["status"] == "duplicate"
    assert by_minutes[30]["reason"] == "duplicate"
    assert by_minutes[60]["status"] == "duplicate"
    assert by_minutes[90]["status"] == "attempted"
    t2 = generate_neighbors(
        "JJ-TBR",
        fold,
        [
            _candidate(
                recipe_id="T2",
                bank="Timing",
                parameters={"require_complete_formation": True},
                issue_at_ns=100 * MINUTE_NS,
                formation_available_at_ns=90 * MINUTE_NS,
            )
        ],
    )
    by_shift = {row["parameters"]["shift_minutes"]: row for row in t2}
    assert by_shift[-15]["status"] == "not_applicable"
    assert by_shift[-15]["reason"] == "formation_unavailable"
    assert by_shift[-30]["reason"] == "formation_unavailable"
    assert by_shift[0]["status"] == "attempted"


def test_past_only_allowlist():
    fold = _fold(fit_cutoff_ns=100 * MINUTE_NS, issue_at_ns=100 * MINUTE_NS)
    parent = _candidate(
        recipe_id="T1",
        bank="Timing",
        parameters={},
        issue_at_ns=100 * MINUTE_NS,
    )
    rows = generate_neighbors("JJ-TBR", fold, [parent], enforce_past_only=True)
    by_shift = {row["parameters"]["shift_minutes"]: row for row in rows}
    assert by_shift[15]["status"] == "not_applicable"
    assert by_shift[15]["reason"] == "past_only_allowlist"
    assert by_shift[30]["reason"] == "past_only_allowlist"
    assert by_shift[0]["status"] == "attempted"
    assert by_shift[-15]["status"] == "attempted"


def test_negative_control_past_only():
    fold = _fold(fit_cutoff_ns=100 * MINUTE_NS, issue_at_ns=100 * MINUTE_NS)
    parent = _candidate(recipe_id="T1", bank="Timing", parameters={}, issue_at_ns=100 * MINUTE_NS)
    off = generate_neighbors("JJ-TBR", fold, [parent], enforce_past_only=False)
    by_shift = {row["parameters"]["shift_minutes"]: row for row in off}
    assert by_shift[15]["status"] == "attempted"
    assert by_shift[30]["status"] == "attempted"
    on = generate_neighbors("JJ-TBR", fold, [parent], enforce_past_only=True)
    assert {row["parameters"]["shift_minutes"]: row for row in on}[30]["status"] == "not_applicable"


def test_simplicity_exactly_1_percent():
    simple = {"score": 100, "changed_axes": 1, "candidate_id": "simple", "synthetic": True}
    complex_ = {"score": 101, "changed_axes": 2, "candidate_id": "complex", "synthetic": True}
    assert simpler_wins(simple, complex_)["candidate_id"] == "simple"


def test_simplicity_just_above_1_percent():
    simple = {"score": 100, "changed_axes": 1, "candidate_id": "simple", "synthetic": True}
    complex_ = {"score": 101.1, "changed_axes": 2, "candidate_id": "complex", "synthetic": True}
    assert simpler_wins(simple, complex_)["candidate_id"] == "complex"


def test_negative_control_simplicity():
    simple = {"score": 100, "changed_axes": 1, "candidate_id": "simple", "synthetic": True}
    complex_ = {"score": 101, "changed_axes": 2, "candidate_id": "complex", "synthetic": True}
    assert simpler_wins(simple, complex_, enforce_simplicity=False)["candidate_id"] == "complex"
    assert simpler_wins(simple, complex_, enforce_simplicity=True)["candidate_id"] == "simple"
    same_bank = [
        _inner_candidate("Formation", "simple", 100, 1.0, changed_axes=1, parameters={"minutes": 60}),
        _inner_candidate("Formation", "complex", 101, 1.0, changed_axes=2, parameters={"minutes": 30, "extra": 1}),
    ]
    default = select_banks("JJ-TBR", same_bank)
    off = select_banks("JJ-TBR", same_bank, enforce_simplicity=False)
    assert default[0]["candidate_id"] == "simple"
    assert off[0]["candidate_id"] == "complex"


def test_outer_outcomes_do_not_change_bank_choice():
    candidates = [
        _inner_candidate("Formation", "cA", 5.0, 1.0, outer={"mean_daily_net_points": 0.0, "improvement_vs_b02": 0.0}),
        _inner_candidate("Profile", "cB", 4.0, 1.0, outer={"mean_daily_net_points": 0.0, "improvement_vs_b02": 0.0}),
        _inner_candidate("Delta", "cC", 3.0, 1.0, outer={"mean_daily_net_points": 99.0, "improvement_vs_b02": 99.0}),
    ]
    first = select_banks("JJ-TBR", candidates)
    candidates[2]["outer"] = {"mean_daily_net_points": 999.0, "improvement_vs_b02": 999.0}
    candidates[2]["outer_score"] = 999.0
    candidates[2]["test"] = {"mean_daily_net_points": 999.0}
    second = select_banks("JJ-TBR", candidates)
    assert [row["candidate_id"] for row in first] == ["cA", "cB"]
    assert [row["candidate_id"] for row in second] == ["cA", "cB"]
    assert [row["bank"] for row in first] == ["Formation", "Profile"]


def test_inner_support_ok_false_excludes_bank():
    candidates = [
        _inner_candidate("Formation", "cA", 5.0, 1.0, inner_support_ok=False, support_opportunities=12, support_days=8),
        _inner_candidate("Profile", "cB", 4.0, 1.0, inner_support_ok=True),
        _inner_candidate("Delta", "cC", 3.0, 1.0, inner_support_ok=True),
    ]
    chosen = select_banks("JJ-TBR", candidates)
    assert [row["candidate_id"] for row in chosen] == ["cC", "cB"]
    assert [row["bank"] for row in chosen] == ["Delta", "Profile"]
    assert "cA" not in [row["candidate_id"] for row in chosen]


def test_shuffle_does_not_change_selected_banks():
    candidates = [
        _inner_candidate("Formation", "cA", 5.0, 1.0),
        _inner_candidate("Profile", "cB", 4.0, 1.0),
        _inner_candidate("Delta", "cC", 3.5, 1.0),
        _inner_candidate("Memory", "cD", -1.0, -1.0),
    ]
    first = select_banks("JJ-TBR", candidates)
    shuffled = list(candidates)
    random.Random(7).shuffle(shuffled)
    second = select_banks("JJ-TBR", shuffled)
    assert [row["candidate_id"] for row in first] == [row["candidate_id"] for row in second]
    assert [row["bank"] for row in first] == ["Formation", "Profile"]


def test_holm_and_bootstrap_contract_constants():
    recorded = {}

    def spy(values, *, block, draws, seed):
        recorded["block"] = block
        recorded["draws"] = draws
        recorded["seed"] = seed
        recorded["n"] = len(list(values))
        return moving_block_bootstrap(values, block=block, draws=draws, seed=seed)

    candidate = _promo_candidate()
    result = evaluate_promotion(
        candidate,
        [{"trial_id": "t-main", "p_raw": 0.001, "synthetic": True}],
        bootstrap_fn=spy,
    )
    assert recorded["seed"] == 15022026
    assert recorded["draws"] == 2000
    assert recorded["block"] == 5
    assert recorded["n"] == 30
    assert result["promoted"] is True
    assert result["ci_low"] > 0
    assert result["mean_diff"] == 1.0


def test_frequency_floor():
    candidate = _promo_candidate(candidate_entries=40, baseline_entries=100)
    result = evaluate_promotion(candidate, [{"trial_id": "t-main", "p_raw": 0.001, "synthetic": True}])
    assert result["frequency_floor_pass"] is False
    assert result["promoted"] is False
    assert result["replace_baseline_allowed"] is False
    assert result["disposition"] == "high_selectivity"


def test_negative_control_frequency_floor():
    candidate = _promo_candidate(candidate_entries=40, baseline_entries=100)
    trials = [{"trial_id": "t-main", "p_raw": 0.001, "synthetic": True}]
    default = evaluate_promotion(candidate, trials)
    off = evaluate_promotion(candidate, trials, apply_frequency_floor=False)
    assert default["replace_baseline_allowed"] is False
    assert default["promoted"] is False
    assert off["replace_baseline_allowed"] is True
    assert off["promoted"] is True
    assert off["frequency_floor_pass"] is False


def test_support_sensitivity_half_and_twice():
    sens = support_sensitivity(100, 30, 3)
    assert sens["half"] == {"opportunities": 50, "days": 15, "blocks": 3, "pass": True}
    assert sens["nominal"] == {"opportunities": 100, "days": 30, "blocks": 3, "pass": True}
    assert sens["twice"] == {"opportunities": 200, "days": 60, "blocks": 3, "pass": False}
    result = evaluate_promotion(_promo_candidate(), [{"trial_id": "t-main", "p_raw": 0.001, "synthetic": True}])
    assert result["support_sensitivity"]["half"]["pass"] is True
    assert result["support_sensitivity"]["twice"]["pass"] is False
    low = support_sensitivity(40, 10, 2)
    assert low["half"]["pass"] is False
    assert low["nominal"]["pass"] is False


def test_six_example_perfect_is_inconclusive():
    candidate = _promo_candidate(resolved_opportunities=6, daily_diff=[1.0] * 6, eligible_test_days=6, supported_outer_blocks=1)
    result = evaluate_promotion(candidate, [{"trial_id": "t-main", "p_raw": 0.001, "synthetic": True}])
    assert result["promoted"] is False
    assert result["disposition"] == "inconclusive_support"
    assert result["support_pass"] is False


def test_attribution_every_reason_and_order():
    fired = _diag(
        candidate_entries=10,
        baseline_entries=100,
        objective_reached=False,
        nearest_approach_S=0.2,
        adverse_S_before_favorable_0_5S=0.6,
        favorable_0_5S_reached=False,
        missed_move_share=0.5,
        family_median_missed_move_share=0.2,
        stop_first_share=0.6,
        family_baseline_stop_first_share=0.3,
        cost_stress_sign_reversal=True,
        resolved_opportunities=6,
        eligible_test_days=5,
        supported_outer_blocks=1,
        unexplained_coverage_loss=True,
    )
    assert attribute_failure(fired) == [
        "frequency",
        "location_miss",
        "confirmation_delay",
        "adverse_before_target",
        "cost_sensitivity",
        "support",
        "coverage",
    ]
    assert list(ATTRIBUTION_ORDER) == attribute_failure(fired)
    assert attribute_failure(_diag(candidate_entries=10, baseline_entries=100)) == ["frequency"]
    assert attribute_failure(_diag(objective_reached=False, nearest_approach_S=0.25)) == ["location_miss"]
    assert attribute_failure(_diag(missed_move_share=0.4, family_median_missed_move_share=0.3)) == ["confirmation_delay"]
    assert attribute_failure(_diag(stop_first_share=0.5, family_baseline_stop_first_share=0.4)) == ["adverse_before_target"]
    assert attribute_failure(_diag(cost_stress_sign_reversal=True)) == ["cost_sensitivity"]
    assert attribute_failure(_diag(resolved_opportunities=6, eligible_test_days=5, supported_outer_blocks=1)) == ["support"]
    assert attribute_failure(_diag(unexplained_coverage_loss=True)) == ["coverage"]


def test_runtime_failure_not_data_rejection():
    fired = _diag(
        runtime_failure=True,
        candidate_entries=10,
        baseline_entries=100,
        objective_reached=False,
        nearest_approach_S=0.1,
        missed_move_share=1.0,
        family_median_missed_move_share=0.0,
        stop_first_share=1.0,
        family_baseline_stop_first_share=0.0,
        cost_stress_sign_reversal=True,
        resolved_opportunities=1,
        eligible_test_days=1,
        supported_outer_blocks=0,
        unexplained_coverage_loss=True,
    )
    assert attribute_failure(fired) == []
    timed = dict(fired)
    timed["runtime_failure"] = False
    timed["timed_out"] = True
    timed["synthetic"] = True
    assert attribute_failure(timed) == []


def test_ledger_append_only_and_replace(tmp_path):
    path = tmp_path / "trials.jsonl"
    ledger = TrialLedger(path)
    first = make_trial_record(
        trial_id="t1",
        family="JJ-TBR",
        branch="judas_reversal",
        outer_fold=2022,
        stage="refinement",
        bank="Formation",
        parameters={"minutes": 30},
        candidate_id="c1",
        recipe_id="F1",
        status="attempted",
        synthetic=True,
        fit_window={"start": "2020-01-01", "end": "2021-06-30"},
        tune_window={"start": "2021-07-01", "end": "2021-09-30"},
        calibration_window={"start": "2021-10-01", "end": "2021-12-31"},
        outcome_exposure_cutoff="2021-12-31",
    )
    for key in TRIAL_RECORD_FIELDS:
        assert key in first
    ledger.append(first)
    with pytest.raises(ContractError, match="append-only"):
        ledger.append(first)
    retry = make_trial_record(first, trial_id="t1-retry", reason="retry", synthetic=True)
    ledger.replace_attempt("t1", retry)
    rows = ledger.read()
    assert [row["trial_id"] for row in rows] == ["t1", "t1-retry"]
    assert rows[1]["replaces_attempt_id"] == "t1"
    assert rows[0]["trial_id"] == "t1"


def test_combination_requires_both_beat_b02():
    fold = _fold()
    a = _candidate(candidate_id="ing-a", parameters={"minutes": 30})
    b = _candidate(candidate_id="ing-b", recipe_id="R1", bank="Reference", parameters={"dispersion": 0.5})
    assert combine_candidates("JJ-TBR", fold, a, b, b02_score=2.0, score_a=2.0, score_b=3.0, combo_score=4.0) is None
    assert combine_candidates("JJ-TBR", fold, a, b, b02_score=2.0, score_a=3.0, score_b=2.0, combo_score=4.0) is None
    assert combine_candidates(
        "JJ-TBR",
        fold,
        a,
        b,
        b02_score=1.0,
        score_a=2.0,
        score_b=2.0,
        combo_score=4.0,
        source_dependencies_causal=False,
    ) is None
    combo = combine_candidates("JJ-TBR", fold, a, b, b02_score=1.0, score_a=2.0, score_b=2.0, combo_score=5.0)
    assert combo is not None
    assert combo["interaction"] == "synergistic"
    assert combo["changed_axis"] == "combination"
    assert combo["changed_axes"] == 2
    assert combo["vs_ingredient_a"] == 3.0
    assert combo["vs_ingredient_b"] == 3.0
    assert combo["vs_b02"] == 4.0
    assert combo["parameters"]["minutes"] == 30
    assert combo["parameters"]["dispersion"] == 0.5
    antagonistic = combine_candidates("JJ-TBR", fold, a, b, b02_score=0.0, score_a=2.0, score_b=2.0, combo_score=1.0)
    assert antagonistic["interaction"] == "antagonistic"
    additive = combine_candidates("JJ-TBR", fold, a, b, b02_score=0.0, score_a=2.0, score_b=4.0, combo_score=3.0)
    assert additive["interaction"] == "additive"


def test_unsuccessful_trials_count_in_holm():
    candidate = _promo_candidate()
    full = [
        {"trial_id": "t-main", "p_raw": 0.04, "synthetic": True},
        {"trial_id": "u1", "p_raw": 1.0, "synthetic": True},
        {"trial_id": "u2", "p_raw": 1.0, "synthetic": True},
    ]
    with_all = evaluate_promotion(candidate, full)
    assert with_all["p_raw"] == 0.04
    assert with_all["holm_reject"] is False
    assert with_all["promoted"] is False
    omitted = evaluate_promotion(candidate, [{"trial_id": "t-main", "p_raw": 0.04, "synthetic": True}])
    assert omitted["holm_reject"] is True
    assert omitted["promoted"] is True


def test_negative_control_holm():
    candidate = _promo_candidate()
    trials = [
        {"trial_id": "t-main", "p_raw": 0.04, "synthetic": True},
        {"trial_id": "u1", "p_raw": 1.0, "synthetic": True},
        {"trial_id": "u2", "p_raw": 1.0, "synthetic": True},
    ]
    default = evaluate_promotion(candidate, trials, apply_holm=True)
    off = evaluate_promotion(candidate, trials, apply_holm=False)
    assert default["holm_reject"] is False
    assert default["promoted"] is False
    assert off["holm_reject"] is True
    assert off["promoted"] is True


def test_missing_day_not_zero():
    result = centered_bootstrap_pvalue([2.0, None, 2.0])
    assert result["mean_diff"] == 2.0
    promo = evaluate_promotion(
        _promo_candidate(daily_diff=[2.0, None, 2.0], trial_id="t-main"),
        [{"trial_id": "t-main", "p_raw": 0.001, "synthetic": True}],
    )
    assert promo["mean_diff"] == 2.0


def test_zero_opportunity_day_stays_zero():
    result = centered_bootstrap_pvalue([2.0, 0.0])
    assert result["mean_diff"] == 1.0
    promo = evaluate_promotion(
        _promo_candidate(daily_diff=[2.0, 0.0] + [1.0] * 28),
        [{"trial_id": "t-main", "p_raw": 0.001, "synthetic": True}],
    )
    assert promo["mean_diff"] == pytest.approx((2.0 + 0.0 + 28.0) / 30)


def test_neighbors_are_new_parameter_tuples():
    parent = _candidate(candidate_id="parent-keep", parameters={"minutes": 60})
    rows = generate_neighbors("JJ-TBR", _fold(), [parent])
    attempted = [row for row in rows if row["status"] == "attempted"]
    assert attempted
    assert all(row["candidate_id"] != "parent-keep" for row in attempted)
    assert all(row["parameters"]["minutes"] != 60 for row in attempted)
    assert {row["parameters"]["minutes"] for row in attempted} == {30, 90}


def test_selected_rules_not_all_history():
    folds = [
        {
            "outer_fold": 2022,
            "family": "JJ-TBR",
            "candidate_id": "fold-2022-rule",
            "role": "selected",
            "selection_cutoff": "2021-06-30",
            "synthetic": True,
        }
    ]
    descriptive = {
        "candidate_id": "all-history-winner",
        "family": "JJ-TBR",
        "label": "descriptive",
        "synthetic": True,
    }
    document = selected_rules_by_fold(folds, descriptive)
    assert document["schema_version"] == "research-selected-rules-by-fold-v1"
    assert document["causal"] is True
    assert document["folds"][0]["candidate_id"] == "fold-2022-rule"
    assert document["all_history_descriptive_recommendation"]["candidate_id"] == "all-history-winner"
    assert all(row["candidate_id"] != "all-history-winner" for row in document["folds"])


def test_family_dispositions_retention_statuses():
    assert RETENTION_STATUSES == ("active_selected", "active_baseline", "inactive_retained")
    document = family_dispositions(
        [
            {
                "family": "JJ-TBR",
                "status": "active_selected",
                "candidate_id": "c-sel",
                "failure_attribution": [],
                "synthetic": True,
            },
            {
                "family": "GB-FAIL",
                "status": "active_baseline",
                "candidate_id": "c-base",
                "failure_attribution": ["support"],
                "synthetic": True,
            },
            {
                "family": "SIRES",
                "status": "inactive_retained",
                "candidate_id": "c-inact",
                "failure_attribution": ["location_miss", "coverage"],
                "synthetic": True,
            },
        ]
    )
    assert document["schema_version"] == "research-family-dispositions-v1"
    statuses = {row["family"]: row for row in document["families"]}
    assert statuses["JJ-TBR"]["status"] == "active_selected"
    assert statuses["JJ-TBR"]["first_attribution"] is None
    assert statuses["GB-FAIL"]["status"] == "active_baseline"
    assert statuses["GB-FAIL"]["first_attribution"] == "support"
    assert statuses["SIRES"]["status"] == "inactive_retained"
    assert statuses["SIRES"]["first_attribution"] == "location_miss"
    with pytest.raises(ContractError, match="unknown retention status"):
        family_dispositions(
            [
                {
                    "family": "JJ-TBR",
                    "status": "promoted",
                    "candidate_id": "c-bad",
                    "failure_attribution": [],
                    "synthetic": True,
                }
            ]
        )


def test_fixtures_labelled_synthetic():
    assert _fold()["synthetic"] is True
    assert _candidate()["synthetic"] is True
    assert _diag()["synthetic"] is True
    assert _inner_candidate("Formation", "x", 1.0, 1.0)["synthetic"] is True
    assert _promo_candidate()["synthetic"] is True
    neighbors = generate_neighbors("JJ-TBR", _fold(), [_candidate()])
    assert all(row["synthetic"] is True for row in neighbors)


def test_control_offsets_density_matched():
    assert CONTROL_OFFSETS == (-2, -1, 1, 2)


def test_rank_inner_ignores_outer():
    rows = [
        _inner_candidate("Formation", "low", 1.0, 1.0, outer_score=99.0),
        _inner_candidate("Formation", "high", 3.0, 1.0, outer_score=0.0),
    ]
    ranked = rank_inner(rows)
    assert [row["candidate_id"] for row in ranked] == ["high", "low"]
    assert "outer_score" not in ranked[0]
    assert "outer" not in ranked[0]


def test_neighborhoods_are_exactly_the_contract_recipes():
    assert set(NEIGHBORHOODS) == {
        "F1",
        "F2",
        "F3",
        "P1",
        "P2",
        "R1",
        "R2",
        "C1",
        "C2",
        "C3",
        "S1",
        "S2",
        "S3",
        "S4",
        "M1",
        "M2",
        "T1",
        "T2",
        "T3",
        "T4",
    }
    assert "_CAP" not in NEIGHBORHOODS
    assert len(NEIGHBORHOODS) == 20


def test_generic_refinement_fallback_and_cap_registry():
    rows = neighborhood_values(
        "UNREGISTERED",
        {"refinement_axis": "cap_value", "refinement_values": list(range(15))},
    )
    assert [row["value"] for row in rows] == list(range(15))
    fallback = generate_neighbors(
        "JJ-TBR",
        _fold(),
        [
            _candidate(
                recipe_id="UNREGISTERED",
                parameters={"refinement_axis": "span", "refinement_values": [1, 2, 3]},
            )
        ],
    )
    assert [row["parameters"]["span"] for row in fallback] == [1, 2, 3]
    assert all(row["changed_axis"] == "span" for row in fallback)


def test_p_holm_matches_holm_fn_rows_with_ties():
    captured: dict = {}

    def spy(pvalues, *, alpha=0.05):
        rows = holm(pvalues, alpha=alpha)
        captured["rows"] = rows
        captured["alpha"] = alpha
        return rows

    trials = [
        {"trial_id": "t0", "p_raw": 0.02, "synthetic": True},
        {"trial_id": "t1", "p_raw": 0.01, "synthetic": True},
        {"trial_id": "t2", "p_raw": 0.02, "synthetic": True},
        {"trial_id": "t3", "p_raw": 0.40, "synthetic": True},
    ]
    result = evaluate_promotion(_promo_candidate(trial_id="t0"), trials, holm_fn=spy)
    rows = captured["rows"]
    alpha = captured["alpha"]
    assert alpha == HOLM_ALPHA
    assert len(rows) == 4
    assert [row["p"] for row in rows].count(0.02) == 2
    running = 0.0
    expected = {}
    for row in sorted(rows, key=lambda item: (float(item["p"]), int(item["index"]))):
        threshold = float(row["threshold"])
        running = max(running, min(1.0, float(row["p"]) * (alpha / threshold)))
        expected[int(row["index"])] = running
    assert result["p_holm"] == expected[0]
    assert result["p_raw"] == 0.02
    assert result["p_holm"] == pytest.approx(0.06)


# ==========================================================================
# The executed refinement round: the bank built from P15-17's allowlist, its
# caps, the fold isolation of the selection, the combination rule and the
# native negative control.
# ==========================================================================

from pathlib import Path as _Path

from trading_research.research.rule_discovery import refinement as rf

CONTRACT = _Path("/workspace/planning/phase-1-5/SEARCH_CONTRACT.md")
MINUTE_NS = 60_000_000_000
CUTOFF_NS = 1_600_000_000 * 1_000_000_000

#: The refinement neighbourhoods exactly as the search contract's table states
#: them, transcribed from the document, not from the implementation.
CONTRACT_NEIGHBOURHOODS = {
    "F1": {"minutes": [30, 60, 90]},
    "F2": {"volume_threshold_multiplier": [0.75, 1.0, 1.25]},
    "F3": {"width_S": [0.5, 0.75, 1.0], "efficiency": [0.2, 0.35, 0.5]},
    "P1": {"bandwidth": [0, 2, 4], "prominence": [0.10, 0.20, 0.30]},
    "P2": {"bandwidth": [0, 2, 4], "prominence": [0.10, 0.20, 0.30]},
    "R1": {"dispersion": [0.5, 1.0, 1.5]},
    "R2": {},
    "C1": {"window_minutes": [2, 5, 10]},
    "C2": {"half_life_s": [120, 300, 600]},
    "C3": {"history_sessions": [10, 20, 40]},
    "S1": {"deadline_minutes": [5, 10, 15]},
    "S2": {"favorable_ticks": [1, 2, 4]},
    "S3": {"deadline_minutes": [5, 10, 15], "favorable_ticks": [1, 2, 4]},
    "S4": {"deadline_minutes": [5, 10, 15], "favorable_ticks": [1, 2, 4]},
    "M1": {"max_prior_contacts": [0, 1, 2]},
    "M2": {"prior_reaction_S": [0.1, 0.25, 0.5]},
    "T1": {"shift_minutes": [-30, -15, 0, 15, 30]},
    "T2": {"shift_minutes": [-30, -15, 0, 15, 30]},
    "T3": {"shift_minutes": [-30, -15, 0, 15, 30]},
    "T4": {"shift_minutes": [-30, -15, 0, 15, 30]},
}


@pytest.mark.parametrize("recipe_id", sorted(CONTRACT_NEIGHBOURHOODS))
def test_neighborhood_values_are_exactly_the_contract_table(recipe_id):
    """Every proposed value comes from the contract's table, and no axis or
    value outside it is ever proposed."""
    expected = CONTRACT_NEIGHBOURHOODS[recipe_id]
    rows = rf.neighborhood_values(recipe_id, {})
    proposed: dict[str, list] = {}
    for row in rows:
        proposed.setdefault(row["axis"], []).append(row["value"])
    assert set(proposed) == set(expected), recipe_id
    for axis, values in expected.items():
        assert proposed[axis] == values, (recipe_id, axis)


def test_the_contract_document_still_states_those_values():
    """If the contract's table changes, this expectation is stale -- fail loudly
    rather than keep refining to a retired neighbourhood."""
    text = CONTRACT.read_text()
    for fragment in (
        "30,60,90 matching minutes",
        ".75,1,1.25 times the prior 20-session median",
        "width .5,.75,1S with efficiency fixed.35",
        "efficiency .2,.35,.5 at chosen width",
        "b0,2,4 with prominence.20",
        "prominence .10,.20,.30 at chosen b",
        ".5,1,1.5 dispersion",
        "2,5,10 minutes / 120,300,600 seconds / 10,20,40 sessions",
        "5,10,15 minutes / 1,2,4 ticks",
        "at most 0,1,2 previous contacts / .1,.25,.5S",
        "-30,-15,0,+15,+30 minutes",
    ):
        assert fragment in text, fragment


def _bank(recipe_id="F1", bank="Formation", parameters=None, branch="nyam_box"):
    return {
        "candidate_id": f"GB-FAIL:{branch}:{recipe_id}",
        "bank": bank,
        "recipe_id": recipe_id,
        "branch": branch,
        "family": "GB-FAIL",
        "parameters": dict(parameters or {"minutes": 60}),
        "issue_at_ns": CUTOFF_NS - rf.MAX_TIMING_SHIFT_MINUTES * MINUTE_NS,
    }


def test_neighbors_respect_the_per_bank_and_per_family_caps():
    """At most 12 attempted neighbours per bank and 24 per family; everything
    beyond the cap keeps a row with its reason."""
    banks = [
        _bank("S3", "Sequence", {"deadline_minutes": d}, branch=f"b{i}")
        for i, d in enumerate((5, 10, 15, 5, 10))
    ]
    rows = rf.generate_neighbors("GB-FAIL", rf.fold_guard(CUTOFF_NS), banks)
    attempted = [row for row in rows if row["status"] == "attempted"]
    per_bank: dict[str, int] = {}
    for row in attempted:
        per_bank[row["bank"]] = per_bank.get(row["bank"], 0) + 1
    assert max(per_bank.values()) <= rf.MAX_NEIGHBORS_PER_BANK
    assert len(attempted) <= rf.MAX_NEIGHBORS_PER_FAMILY
    capped = [row for row in rows if row["reason"] in ("cap_per_bank", "cap_per_family")]
    assert capped, "the cap must be visible as a row, not as a silent truncation"
    assert all(row["status"] == "not_applicable" for row in capped)


def test_a_timing_shift_outside_the_registered_set_is_refused_by_the_past_only_guard():
    """The registered T neighbourhood is -30..+30 minutes measured from the
    parent issue; a wider shift needs information the fit cutoff cannot supply."""
    guard = rf.fold_guard(CUTOFF_NS)
    parent = _bank("T4", "Timing", {"shift_minutes": 0})
    rows = rf.generate_neighbors("GB-FAIL", guard, [parent])
    assert [row["status"] for row in rows if row["changed_axis"] == "shift_minutes"].count("attempted") >= 1
    assert all(
        abs(row["parameters"]["shift_minutes"]) <= rf.MAX_TIMING_SHIFT_MINUTES
        for row in rows
        if row["status"] == "attempted"
    )
    wider = dict(parent, issue_at_ns=CUTOFF_NS)  # a parent issued at the cutoff itself
    rows = rf.generate_neighbors("GB-FAIL", guard, [wider])
    late = [row for row in rows if row["parameters"].get("shift_minutes", 0) > 0]
    assert late and all(row["reason"] == "past_only_allowlist" for row in late)


def test_a_selected_bank_without_a_branch_is_refused():
    """Two branches of one family and recipe would collide in the neighbour
    identity; the bank builder refuses rather than merge them."""
    allowlist = {
        "folds": [
            {
                "outer_fold": 2022,
                "inner_cutoff_day": "2021-09-30",
                "families": [
                    {"family": "GB-FAIL", "selected_banks": [{"candidate_id": "GB-FAIL:x:F1", "bank": "Formation", "recipe_id": "F1", "parameters": {"minutes": 60}}]}
                ],
            }
        ]
    }
    with pytest.raises(ContractError) as excinfo:
        rf.build_refinement_bank(allowlist, {2022: CUTOFF_NS})
    assert "collide" in str(excinfo.value)


def test_a_combination_needs_both_ingredients_to_beat_the_baseline():
    """A01: the combined candidate exists only when each ingredient individually
    beats B0.2 on inner tuning."""
    a = _bank("F1", "Formation", {"minutes": 30})
    b = _bank("T4", "Timing", {"shift_minutes": 15})
    fold = rf.fold_guard(CUTOFF_NS)
    combined = rf.combine_candidates(
        "GB-FAIL", fold, a, b, b02_score=1.0, score_a=2.0, score_b=1.5, combo_score=2.5
    )
    assert combined is not None
    assert combined["changed_axes"] == 2 and combined["interaction"] == "synergistic"
    assert combined["parameters"] == {"minutes": 30, "shift_minutes": 15}
    assert combined["parent_trial_ids"] == [a["candidate_id"], b["candidate_id"]]
    for score_a, score_b in ((1.0, 1.5), (2.0, 0.5), (0.9, 0.9)):
        assert (
            rf.combine_candidates(
                "GB-FAIL", fold, a, b, b02_score=1.0, score_a=score_a, score_b=score_b, combo_score=9.0
            )
            is None
        )
    assert (
        rf.combine_candidates(
            "GB-FAIL", fold, a, b, b02_score=1.0, score_a=2.0, score_b=1.5, combo_score=2.5,
            source_dependencies_causal=False,
        )
        is None
    )


def test_a_combination_reports_an_antagonistic_interaction_honestly():
    a = _bank("F1", "Formation", {"minutes": 30})
    b = _bank("T4", "Timing", {"shift_minutes": 15})
    combined = rf.combine_candidates(
        "GB-FAIL", {}, a, b, b02_score=1.0, score_a=2.0, score_b=1.8, combo_score=1.2
    )
    assert combined["interaction"] == "antagonistic"
    assert combined["vs_ingredient_a"] < 0 and combined["vs_ingredient_b"] < 0
    assert combined["vs_b02"] > 0


# --------------------------------------------------------------------------
# fold isolation and the negative control
# --------------------------------------------------------------------------

_FOLD_2022 = {
    "test_year": 2022,
    "fit": ["2020-01-02", "2020-01-03"],
    "tune": ["2021-07-01"],
    "calibrate": ["2021-10-01"],
    "test": ["2022-01-03", "2022-01-04"],
}
_FOLD_2023 = {
    "test_year": 2023,
    "fit": ["2022-01-03", "2022-01-04"],
    "tune": ["2022-07-01"],
    "calibrate": ["2022-10-03"],
    "test": ["2023-01-03", "2023-01-04"],
}


def _neighbor_row(candidate_id, bank, recipe_id, parameters, axis):
    return {
        "candidate_id": candidate_id,
        "family": "SYN",
        "branch": "syn_branch",
        "bank": bank,
        "recipe_id": recipe_id,
        "parameters": dict(parameters),
        "changed_axis": axis,
        "changed_axes": 1,
        "parent_trial_ids": ["SYN:syn_branch:" + recipe_id],
        "status": "attempted",
        "reason": None,
    }


def _series(values):
    """A CandidateSeries whose paired days carry the given per-day net points."""
    from trading_research.research.rule_discovery import search_run as sr

    series = sr.CandidateSeries("cid")
    for day, (candidate, baseline) in values.items():
        series.paired[day] = {
            "day": day,
            "candidate": candidate,
            "baseline": baseline,
            "diff": candidate - baseline,
            "candidate_fills": 2,
            "baseline_fills": 2,
            "stress": None,
            "control": None,
            "missed_move": 0,
            "stop_first": 0,
            "delay": None,
            "nearest_approach_S": None,
            "adverse_S": None,
        }
    return series


def _resolved(candidate_id, bank, recipe_id, parameters):
    from trading_research.research.rule_discovery.search import ResolvedCandidate

    return ResolvedCandidate(
        candidate_id=candidate_id,
        family="SYN",
        branch="syn_branch",
        bank=bank,
        changed_axis=bank.lower(),
        recipe_id=recipe_id,
        parameters=dict(parameters),
        required_stages=("trigger",),
        hooks=("trigger",),
        phase="evaluation",
        applicable=True,
        supported=True,
        unsupported_reason=None,
        coverage_id="SYN:branch:syn_branch",
        evidence={"synthetic": True},
    )


def _bank_document():
    rows = [
        _neighbor_row("SYN:syn_branch:S1:deadline_minutes=5", "Sequence", "S1", {"deadline_minutes": 5}, "deadline_minutes"),
        _neighbor_row("SYN:syn_branch:S1:deadline_minutes=15", "Sequence", "S1", {"deadline_minutes": 15}, "deadline_minutes"),
    ]
    return {
        "folds": [
            {"outer_fold": 2022, "families": [{"family": "SYN", "neighbors": rows}]},
            {"outer_fold": 2023, "families": [{"family": "SYN", "neighbors": rows}]},
        ]
    }


def test_a_fold_selects_only_from_its_own_inner_days():
    """A02: the 2022 fold's choice is made on its fit+tune days; changing only
    the 2023 fold's inner days (which are 2022's test days) cannot move it."""
    bank = _bank_document()
    resolved = {
        row["candidate_id"]: _resolved(row["candidate_id"], row["bank"], row["recipe_id"], row["parameters"])
        for row in bank["folds"][0]["families"][0]["neighbors"]
    }
    inner = {"2020-01-02": (3.0, 1.0), "2020-01-03": (3.0, 1.0), "2021-07-01": (3.0, 1.0)}
    outer = {"2022-01-03": (1.0, 1.0), "2022-01-04": (1.0, 1.0)}
    weak = {day: (2.0, 1.0) for day in inner}
    series = {
        "SYN:syn_branch:S1:deadline_minutes=5": _series({**inner, **outer}),
        "SYN:syn_branch:S1:deadline_minutes=15": _series({**weak, **outer}),
    }
    first = rf.select_refined_for_fold(bank, _FOLD_2022, resolved, series)
    assert first["families"]["SYN"]["refined"][0]["candidate_id"] == "SYN:syn_branch:S1:deadline_minutes=5"

    # move only the 2022 test days (= the 2023 fold's fit days) far in favour of
    # the loser: the 2022 choice must not move
    loud = {"2022-01-03": (99.0, 1.0), "2022-01-04": (99.0, 1.0)}
    series_outer = {
        "SYN:syn_branch:S1:deadline_minutes=5": _series({**inner, **outer}),
        "SYN:syn_branch:S1:deadline_minutes=15": _series({**weak, **loud}),
    }
    again = rf.select_refined_for_fold(bank, _FOLD_2022, resolved, series_outer)
    assert again["families"] == first["families"]
    # and the 2023 fold, whose inner days those are, does move
    later = rf.select_refined_for_fold(bank, _FOLD_2023, resolved, series_outer)
    assert later["families"]["SYN"]["refined"][0]["candidate_id"] == "SYN:syn_branch:S1:deadline_minutes=15"


def test_a_combination_is_proposed_only_from_two_qualifying_banks():
    """One combination per family per fold, from two different banks, and only
    when both ingredients beat B0.2 on inner tuning."""
    def selection(first_beats, second_beats, same_bank=False):
        return {
            "outer_fold": 2022,
            "families": {
                "SYN": {
                    "refined": [
                        {
                            "bank": "Sequence",
                            "candidate_id": "a",
                            "improvement_vs_b02": 2.0 if first_beats else -1.0,
                            "beats_b02": first_beats,
                        },
                        {
                            "bank": "Sequence" if same_bank else "Memory",
                            "candidate_id": "b",
                            "improvement_vs_b02": 1.0 if second_beats else -1.0,
                            "beats_b02": second_beats,
                        },
                    ],
                    "retained_parent": [],
                }
            },
        }

    assert len(rf.propose_combinations(selection(True, True), None)) == 1
    assert rf.propose_combinations(selection(True, False), None) == []
    assert rf.propose_combinations(selection(False, True), None) == []
    assert rf.propose_combinations(selection(True, True, same_bank=True), None) == []


def test_negative_control_a_refined_parameter_must_change_the_scan():
    """The negative control: a refinement that does not reach the scanner would
    leave the document identical to its parent's. The parent's own value must
    reproduce the parent exactly, and a neighbour value must not."""
    from trading_research.research.rule_discovery import search

    day = "2021-06-01"
    parents = {item.candidate_id: item for item in search.resolve_bank()}
    parent = parents["SAINT-AMT:continuation_retest:S1"]
    market = search.load_b02_market(day, warm=True, branches=[(parent.family, parent.branch)])
    base = search.serialize_scan_bytes(search.scan_candidate(market, parent))
    from dataclasses import replace

    same = replace(parent, parameters=dict(parent.parameters))
    assert search.serialize_scan_bytes(search.scan_candidate(market, same)) == base
    values = rf.neighborhood_values(parent.recipe_id, dict(parent.parameters))
    changed = [
        item for item in values if dict(item["parameters"]) != dict(parent.parameters)
    ]
    assert changed, "the contract's neighbourhood must offer a different value"
    moved = replace(parent, parameters=dict(changed[0]["parameters"]))
    assert search.serialize_scan_bytes(search.scan_candidate(market, moved)) != base


def test_a_combination_whose_ingredients_live_on_different_branches_is_not_applicable():
    """Two mechanisms on different branches cannot be put on one scan; the
    proposal keeps a row with its reason instead of disappearing."""
    selection = {
        "outer_fold": 2022,
        "families": {
            "JJ-TBR": {
                "refined": [
                    {
                        "bank": "Sequence",
                        "candidate_id": "JJ-TBR:judas_reversal:S4:deadline_minutes=10",
                        "improvement_vs_b02": 2.0,
                        "beats_b02": True,
                    },
                    {
                        "bank": "Formation",
                        "candidate_id": "JJ-TBR:internal_rotation:F2:volume_threshold_multiplier=0.75",
                        "improvement_vs_b02": 1.0,
                        "beats_b02": True,
                    },
                ],
                "retained_parent": [],
            },
            "GB-FAIL": {
                "refined": [
                    {
                        "bank": "Timing",
                        "candidate_id": "GB-FAIL:previous_hour:T4:shift_minutes=-15",
                        "improvement_vs_b02": 2.0,
                        "beats_b02": True,
                    },
                    {
                        "bank": "Formation",
                        "candidate_id": "GB-FAIL:previous_hour:F3:efficiency=0.5",
                        "improvement_vs_b02": 1.0,
                        "beats_b02": True,
                    },
                ],
                "retained_parent": [],
            },
        },
    }
    rows = {row["family"]: row for row in rf.propose_combinations(selection, None)}
    assert rows["JJ-TBR"]["status"] == "not_applicable"
    assert rows["JJ-TBR"]["reason"] == "ingredients_on_different_branches"
    assert rows["GB-FAIL"]["status"] == "attempted"
    assert rows["GB-FAIL"]["reason"] is None
