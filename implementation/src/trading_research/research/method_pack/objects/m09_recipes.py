"""FORMULAS M09 object delta and printed fixtures."""

from __future__ import annotations

from decimal import Decimal

from trading_research.research.method_pack.logic import dec
from trading_research.research.method_pack.protocol import RecipeResult, add_fixture, register
from trading_research.research.method_pack.objects.rest_recipes import _d, _yd, _r


@register("O149", ("score", "threshold", "features_known_at", "order_at"))
def o149(inp: dict) -> RecipeResult:
    score = dec(inp.get("score"))
    thr = dec(inp.get("threshold"))
    inclusive = inp.get("inclusive", True)
    sel = None if score is None else (score >= thr if inclusive else score > thr)
    feat_at = inp.get("features_known_at")
    order_at = inp.get("order_at")
    causal = None if feat_at is None or order_at is None else feat_at <= order_at
    if causal is False:
        return _r("O149", "invalid", {"selection": sel, "feature_causal": False, "automatic_grade": None}, base_ok=False, reason="causal")
    model_at = inp.get("model_known_at", inp.get("known_at"))
    training_at = inp.get("training_cutoff_at")
    grade_at = inp.get("grade_available_at")
    model_causal = None if model_at is None else model_at <= inp["order_at"]
    if training_at is not None:
        model_causal = model_causal and training_at <= model_at
    if grade_at is not None:
        model_causal = model_causal and grade_at <= inp["order_at"]
    if model_causal is False:
        return _r("O149", "invalid", {"selection": sel, "feature_causal": causal,
                  "model_known_before_use": False, "automatic_grade": None},
                  known_at=max(value for value in (model_at, feat_at, grade_at) if value is not None),
                  base_ok=False, reason="model, training or grade is available after order")
    holes = []
    if inp.get("model_id") is None:
        holes.append("HOLE:O149:model")
    if inp.get("transform_versions") is None:
        holes.append("HOLE:O149:transforms")
    if inp.get("label_definition") is None:
        holes.append("HOLE:O149:label")
    if inp.get("later_ofm_causal_status") != "negative":
        holes.append("HOLE:O149:causal_correction")
    known_values = [value for value in (model_at, feat_at, grade_at) if value is not None]
    return _r("O149", "supplied" if not holes else "hole", {
        "selection": sel,
        "feature_causal": causal,
        "model_known_before_use": model_causal,
        "max_feature_known_at": feat_at,
        "supplied_grade": inp.get("supplied_grade"),
        "automatic_grade": None,
        "score": score,
        "threshold": thr,
        "later_ofm_causal_status": inp.get("later_ofm_causal_status"),
        "reconstructed_profit": None,
    }, known_at=max(known_values) if known_values else None,
        coverage_ok=True if not holes else None, hole_ids=holes,
        reason=None if not holes else "supplied grader provenance or causal correction incomplete")


@register("O151", ("limit", "side", "active_at", "trades"))
def o151(inp: dict) -> RecipeResult:
    limit = dec(inp["limit"])
    side = inp["side"]
    if side not in {"buy", "sell"} or not limit.is_finite():
        return _r("O151", "invalid", {"modeled_fill_at": None, "fill_eligibility": False},
                  base_ok=False, reason="invalid passive order side or limit")
    cancel = inp.get("cancel_at")
    modeled = None
    ambiguous = False
    for tr in sorted(inp["trades"], key=lambda row: row["t"]):
        t = tr["t"]
        if t < inp["active_at"]:
            continue
        if cancel is not None and t > cancel:
            continue
        if t == inp["active_at"] or (cancel is not None and t == cancel):
            ambiguous = True
            continue
        px = dec(tr["price"])
        hit = px <= limit if side == "buy" else px >= limit
        if hit:
            modeled = t
            break
    actual = inp.get("fill_report")
    holes = []
    if inp.get("order_id") is None:
        holes.append("HOLE:O151:order_id")
    if inp.get("fill_convention") is None:
        holes.append("HOLE:O151:fill_convention")
    if ambiguous and modeled is None:
        holes.append("HOLE:O151:same_key_order")
    return _r("O151", "computed" if not holes else "hole", {
        "modeled_fill_at": modeled,
        "actual_fill": actual,
        "actual_fill_at": inp.get("actual_fill_at") if actual else None,
        "actual_unknown": actual is None,
        "modeled_fill_rule": inp.get("fill_convention"),
        "queue_verified": bool(inp.get("queue_evidence")),
        "fill_eligibility": None if ambiguous and modeled is None else modeled is not None,
    }, known_at=inp.get("known_at"), coverage_ok=True if not holes else None,
        hole_ids=holes, reason=None if not holes else "modeled fill provenance or event order incomplete")


@register("O156", ("currency_per_r",))
def o156(inp: dict) -> RecipeResult:
    per_r = dec(inp.get("currency_per_r"))
    target = dec(inp.get("target"))
    dd = dec(inp.get("drawdown"))
    daily_r = dec(inp.get("daily_r", -4))
    tgt_r = None if per_r is None or target is None else target / per_r
    dd_r = None if per_r is None or dd is None else dd / per_r
    daily_ccy = None if per_r is None or daily_r is None else daily_r * per_r
    paths = inp.get("paths")
    pass_n = inp.get("pass_n")
    if paths is not None and (type(paths) is not int or paths <= 0 or type(pass_n) is not int
                              or pass_n < 0 or pass_n > paths):
        return _r("O156", "invalid", {"path_rate": None, "reconstruct_from_rounded": False},
                  base_ok=False, coverage_ok=None, reason="invalid supplied path counts")
    rate = None if paths is None else dec(pass_n) / dec(paths)
    rounded = inp.get("rounded_pct")
    holes = []
    if inp.get("path_design") is None:
        holes.append("HOLE:O156:path_design")
    if inp.get("consistency_rule") is None:
        holes.append("HOLE:O156:consistency_rule")
    if inp.get("later_ofm_causal_status") != "negative":
        holes.append("HOLE:O156:causal_correction")
    return _r("O156", "computed" if not holes else "hole", {
        "target_r": tgt_r,
        "drawdown_r": dd_r,
        "daily_stop_currency": daily_ccy,
        "path_rate": rate,
        "reported_pass_rate": dec(rounded) if paths is None else rate,
        "reconstruct_from_rounded": False,
        "source_causal_status": inp.get("later_ofm_causal_status"),
        "missing_path_rules": holes,
    }, known_at=inp.get("known_at"), coverage_ok=True if not holes else None,
        hole_ids=holes, reason=None if not holes else "source path rules or causal correction incomplete")


add_fixture({"id": "O149-F1", "recipe": "O149", "inputs": {"score": Decimal("0.8"), "threshold": Decimal("0.7"), "inclusive": True, "features_known_at": _d(9, 59), "order_at": _d(10, 0), "known_at": _yd(16, 0), "use_at": _d(10, 0)}, "expected": {"selection": True, "feature_causal": True, "automatic_grade": None}})


add_fixture({"id": "O149-F1b", "recipe": "O149", "inputs": {"score": Decimal("0.8"), "threshold": Decimal("0.7"), "features_known_at": _d(10, 1), "order_at": _d(10, 0), "known_at": _yd(16, 0), "use_at": _d(10, 0)}, "expected": {"feature_causal": False, "base_ok": False}})


add_fixture({"id": "O149-F1c", "recipe": "O149", "inputs": {"score": Decimal("0.8"), "known_at": _yd(16, 0), "use_at": _d(10, 0)}, "expected": {"selection": None}})


add_fixture({"id": "O151-F1", "recipe": "O151", "inputs": {"limit": 100, "side": "buy", "active_at": _d(10, 0), "trades": [{"t": _d(10, 1), "price": Decimal("100.25")}, {"t": _d(10, 2), "price": 100}], "known_at": _d(10, 2), "use_at": _d(10, 2)}, "expected": {"modeled_fill_at": _d(10, 2), "actual_unknown": True}})


add_fixture({"id": "O151-F1b", "recipe": "O151", "inputs": {"limit": 100, "side": "buy", "active_at": _d(10, 0), "cancel_at": _d(10, 1, 30), "trades": [{"t": _d(10, 2), "price": 100}], "known_at": _d(10, 2), "use_at": _d(10, 2)}, "expected": {"modeled_fill_at": None}})


add_fixture({"id": "O156-F1", "recipe": "O156", "inputs": {"currency_per_r": 80, "target": 3000, "drawdown": 2000, "daily_r": -4, "pass_n": 3680, "paths": 4000, "known_at": _d(16, 0), "use_at": _d(16, 1)}, "expected": {"target_r": Decimal("37.5"), "drawdown_r": Decimal("25"), "daily_stop_currency": Decimal("-320"), "path_rate": Decimal("0.92")}})


add_fixture({"id": "O156-F1b", "recipe": "O156", "inputs": {"currency_per_r": 80, "rounded_pct": Decimal("0.92"), "known_at": _d(16, 0), "use_at": _d(16, 1)}, "expected": {"reconstruct_from_rounded": False}})
