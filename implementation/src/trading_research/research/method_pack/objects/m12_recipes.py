"""FORMULAS M12 validation gate and fixed-baseline ladder recipes."""

from __future__ import annotations

from decimal import Decimal

from trading_research.research.method_pack.logic import dec
from trading_research.research.method_pack.protocol import RecipeResult, add_fixture, register
from trading_research.research.method_pack.objects.rest_recipes import _d, _yd, _r


@register("O154", ("n", "win_rate", "avg_rr", "mc_max_streak"))
def o154(inp: dict) -> RecipeResult:
    """Audit a supplied prior-process validation; never run a simulation here."""
    n = inp["n"]
    minimum = inp.get("min_n", 100)
    win_rate = dec(inp["win_rate"])
    average_rr = dec(inp["avg_rr"])
    mc_streak = inp["mc_max_streak"]
    known_at = inp.get("known_at")
    common = {
        "overlay_validation": False,
        "sample_n": n,
        "sample_at_least100": type(n) is int and n >= 100,
        "winrate_known": win_rate is not None,
        "average_rr_known": average_rr is not None,
        "mc_result_known": mc_streak is not None,
        "validation_before_risk": (
            known_at is not None and inp.get("use_at") is not None
            and known_at <= inp["use_at"]
        ),
        "win_rate": win_rate,
        "average_rr": average_rr,
        "mc_max_loss_streak": mc_streak,
        "simulation_run": False,
    }
    if minimum != 100:
        return _r("O154", "invalid", common, known_at=known_at, base_ok=False,
                  reason="the printed minimum is fixed at 100 prior trades")
    if (type(n) is not int or n < 0 or win_rate is None
            or not Decimal(0) <= win_rate <= Decimal(1)
            or average_rr is None or average_rr <= 0
            or type(mc_streak) is not int or mc_streak < 0):
        return _r("O154", "invalid", common, known_at=known_at, base_ok=False,
                  reason="invalid supplied validation metric")
    if inp.get("same_process") is False:
        return _r("O154", "invalid", common, known_at=known_at, base_ok=False,
                  reason="prior sample belongs to another process")
    if inp.get("simulation_invented") is True:
        return _r("O154", "invalid", common, known_at=known_at, base_ok=False,
                  reason="a new simulation cannot substitute for the supplied validation")
    if n < 100:
        return _r("O154", "computed", common, known_at=known_at)
    common["overlay_validation"] = True
    return _r("O154", "supplied", common, known_at=known_at)


@register("O155", ("E0", "B"))
def o155(inp: dict) -> RecipeResult:
    """Compute only the two printed steps from one fixed original baseline."""
    e0, baseline = dec(inp["E0"]), dec(inp["B"])
    if e0 is None or baseline is None or e0 <= 0 or baseline <= 0:
        return _r("O155", "invalid", {"printed_stage": None},
                  known_at=inp.get("known_at"), base_ok=False,
                  reason="baseline equity and risk unit must be positive")
    fraction = baseline / e0
    first_win = Decimal(3) * baseline
    second_risk = Decimal(4) * baseline
    second_target = Decimal(3) * second_risk
    value = {
        "fixed_baseline_equity": e0, "fixed_baseline_unit": baseline,
        "base_risk_fraction": fraction, "first_risk": baseline,
        "first_win": first_win, "second_risk": second_risk,
        "second_target": second_target,
        "net_second_loss": first_win - second_risk,
        "net_second_win": first_win + second_target,
        "next_risk": baseline, "activation": None,
        "second_loss_next": None, "rebase_policy": None,
        "entry_created": False, "profitability_asserted": False,
    }
    alternative_pct = dec(inp.get("alt_pct"))
    alternative = None if alternative_pct is None else alternative_pct * (e0 + first_win)
    value["updated_equity_percentage_risk"] = alternative
    value["alt_not_printed"] = None if alternative is None else alternative != second_risk
    if fraction > Decimal("0.01"):
        return _r("O155", "invalid", value, known_at=inp.get("known_at"),
                  base_ok=False, reason="fixed baseline risk exceeds one percent")
    supplied_fraction = dec(inp.get("base_risk_fraction"))
    if supplied_fraction is not None and supplied_fraction != fraction:
        return _r("O155", "invalid", value, known_at=inp.get("known_at"),
                  base_ok=False, reason="declared base risk fraction does not equal B/E0")
    if inp.get("validated_process") is False:
        return _r("O155", "invalid", value, known_at=inp.get("known_at"),
                  base_ok=False, reason="printed ladder requires a validated process")
    stage = inp.get("risk_stage")
    if stage is not None:
        value["printed_stage"] = stage
        expected = {"first": (Decimal(1), Decimal(3)),
                    "second": (Decimal(4), Decimal(3))}.get(stage)
        supplied_risk = dec(inp.get("risk_units"))
        supplied_reward = dec(inp.get("planned_reward_r"))
        invalid = expected is not None and (
            (supplied_risk is not None and supplied_risk != expected[0])
            or (supplied_reward is not None and supplied_reward != expected[1])
        )
        if invalid:
            return _r("O155", "invalid", value, known_at=inp.get("known_at"),
                      base_ok=False,
                      reason="supplied sizing is not the printed fixed-baseline stage")
        if stage == "second" and (
            inp.get("first_trade_closed") is not True
            or dec(inp.get("first_trade_result_units")) != Decimal(3)
            or inp.get("first_trade_close_at") is None
            or inp.get("decision_at") is None
            or inp["first_trade_close_at"] >= inp["decision_at"]
        ):
            return _r("O155", "invalid", value, known_at=inp.get("known_at"),
                      base_ok=False,
                      reason="second risk requires the actual closed first +3B win")
        if stage == "reset_after_second_win":
            if dec(inp.get("second_trade_result_units")) is None:
                return _r("O155", "hole", value, known_at=inp.get("known_at"),
                          base_ok=None, coverage_ok=None,
                          hole_ids=["HOLE:O155:second_loss_next"],
                          reason="the next state after a second loss is unpublished")
            if (dec(inp.get("second_trade_result_units")) != Decimal(12)
                    or dec(inp.get("next_risk_units")) != Decimal(1)):
                return _r("O155", "invalid", value, known_at=inp.get("known_at"),
                          base_ok=False,
                          reason="reset is printed only after the second +12B win")
    return _r("O155", "computed", value, known_at=inp.get("known_at"),
              hole_ids=["HOLE:O155:activation", "HOLE:O155:second_loss_next",
                        "HOLE:O155:rebase"])


add_fixture({
    "id": "O154-F1", "recipe": "O154",
    "inputs": {"n": 100, "min_n": 100, "win_rate": Decimal("0.55"),
               "avg_rr": 2, "mc_max_streak": 8, "same_process": True,
               "known_at": _yd(16, 0), "use_at": _d(9, 30)},
    "expected": {"overlay_validation": True, "sample_n": 100,
                 "sample_at_least100": True, "simulation_run": False},
})
add_fixture({
    "id": "O154-F1-n99", "recipe": "O154",
    "inputs": {"n": 99, "min_n": 100, "win_rate": Decimal("0.55"),
               "avg_rr": 2, "mc_max_streak": 8, "same_process": True,
               "known_at": _yd(16, 0), "use_at": _d(9, 30)},
    "expected": {"overlay_validation": False, "sample_at_least100": False},
})
add_fixture({
    "id": "O154-F1-mc-hole", "recipe": "O154",
    "inputs": {"n": 100, "min_n": 100, "win_rate": Decimal("0.55"),
               "avg_rr": 2, "known_at": _yd(16, 0), "use_at": _d(9, 30)},
    "expected": {"state": "hole", "coverage_ok": None,
                 "hole_ids": ["HOLE:O154:mc_max_streak"],
                 "overlay_validation": None},
})
add_fixture({
    "id": "O155-F1", "recipe": "O155",
    "inputs": {"E0": 10000, "B": 100, "alt_pct": Decimal("0.04"),
               "known_at": _d(9, 0), "use_at": _d(9, 30)},
    "expected": {"base_risk_fraction": Decimal("0.01"),
                 "first_win": Decimal("300"), "second_risk": Decimal("400"),
                 "second_target": Decimal("1200"),
                 "net_second_loss": Decimal("-100"),
                 "net_second_win": Decimal("1500"),
                 "next_risk": Decimal("100"), "alt_not_printed": True,
                 "activation": None, "entry_created": False,
                 "profitability_asserted": False},
})
add_fixture({
    "id": "O155-F2-rebase", "recipe": "O155",
    "inputs": {"E0": 10000, "B": 100, "risk_stage": "second",
               "risk_units": Decimal("4.12"), "planned_reward_r": 3,
               "first_trade_closed": True, "first_trade_result_units": 3,
               "first_trade_close_at": _d(10, 0), "decision_at": _d(10, 1),
               "known_at": _d(10, 0), "use_at": _d(10, 1)},
    "expected": {"state": "invalid", "base_ok": False,
                 "reason": "supplied sizing is not the printed fixed-baseline stage"},
})
add_fixture({
    "id": "O155-F3-after-loss", "recipe": "O155",
    "inputs": {"E0": 10000, "B": 100,
               "risk_stage": "reset_after_second_win",
               "second_trade_result_units": None, "next_risk_units": None,
               "known_at": _d(11, 0), "use_at": _d(11, 1)},
    "expected": {"state": "hole", "coverage_ok": None,
                 "hole_ids": ["HOLE:O155:second_loss_next"]},
})
