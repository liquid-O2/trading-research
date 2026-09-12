"""FORMULAS M11 object delta and printed fixtures."""

from __future__ import annotations

from decimal import Decimal

from trading_research.research.method_pack.logic import dec
from trading_research.research.method_pack.protocol import RecipeResult, add_fixture, register
from trading_research.research.method_pack.objects.rest_recipes import _d, _yd, _r

_Z_SAMPLE = Decimal(2) / Decimal(2).sqrt()

@register("O157", ("required_n", "available"))
def o157(inp: dict) -> RecipeResult:
    req = int(inp["required_n"])
    avail = inp["available"]
    if req <= 0 or not isinstance(avail, list):
        return _r("O157", "invalid", {"available_series_count": None,
                  "required_series_present": None, "automatic_verdict": None},
                  base_ok=False, reason="invalid required series inventory")
    as_of = inp.get("as_of")
    usable = []
    for s in avail:
        t = s.get("at")
        if as_of is None or t is None or t <= as_of:
            usable.append(s)
    count = len(usable)
    ids = [s.get("id") for s in usable]
    duplicate = None in ids or len(ids) != len(set(ids))
    present = True if count >= req and not duplicate else None
    later = inp.get("later_value")
    used = inp.get("used_value")
    return _r("O157", "supplied", {
        "available_series_count": count,
        "of": req,
        "required_series_present": present,
        "series_ids_unique": not duplicate,
        "vintage_records_complete": all(s.get("at") is not None and s.get("value") is not None for s in usable),
        "automatic_verdict": None,
        "later_replaces": False if later is not None else None,
        "used_value": used,
    }, known_at=inp.get("known_at"), hole_ids=["HOLE:O157:series"] if present is not True else ["HOLE:O157:engine"])


@register("O158", ("source_cycle_label", "indicator_count"))
def o158(inp: dict) -> RecipeResult:
    label = inp.get("source_cycle_label")
    n = inp.get("indicator_count")
    if not isinstance(label, str) or not label.strip() or type(n) is not int or n <= 0:
        return _r("O158", "invalid", {"automatic_cycle": None, "source_cycle_label": label},
                  base_ok=False, coverage_ok=None, reason="invalid supplied cycle record")
    holes = [] if inp.get("source_rule_id") else ["HOLE:O158:engine"]
    return _r("O158", "supplied" if not holes else "hole", {
        "source_cycle_label": label,
        "indicator_count": n,
        "majority_vote": False,
        "automatic_cycle": None,
    }, known_at=inp.get("known_at"), coverage_ok=True if not holes else None, hole_ids=holes)


@register("O159", ("z_score",))
def o159(inp: dict) -> RecipeResult:
    score = dec(inp.get("c_score"))
    z = dec(inp.get("z_score"))
    if score is None:
        return _r("O159", "hole", {"automatic_c_score": None, "source_c_score": None, "z_is_c": False}, hole_ids=["HOLE:O159:custom_score_formula"], coverage_ok=None)
    substituted = inp.get("metric_kind") == "z_score" or inp.get("substituted_from_z") is True
    if substituted:
        return _r("O159", "invalid", {"source_c_score": score, "z_score": z,
                  "distinct": False, "z_is_c": False, "automatic_c_score": None},
                  base_ok=False, coverage_ok=None, hole_ids=["HOLE:O159:metric_identity"],
                  reason="generic z-score substituted for Stoic custom C-score")
    holes = [] if inp.get("source_rule_id") else ["HOLE:O159:custom_score_formula"]
    return _r("O159", "supplied" if not holes else "hole", {
        "source_c_score": score,
        "z_score": z,
        "distinct": z is None or z != score,
        "z_is_c": False,
        "automatic_c_score": None,
    }, known_at=inp.get("known_at"), coverage_ok=True if not holes else None, hole_ids=holes)


@register("O160", ("baseline", "x"))
def o160(inp: dict) -> RecipeResult:
    xs = [dec(v) for v in inp["baseline"]]
    x = dec(inp["x"])
    conv = inp.get("convention")
    n = len(xs)
    if not xs or x is None or not x.is_finite() or any(v is None or not v.is_finite() for v in xs):
        return _r("O160", "invalid", {"baseline_mean": None, "standardized": None},
                  base_ok=False, reason="empty or nonfinite historical baseline")
    mean = sum(xs, Decimal(0)) / n
    if conv is None:
        return _r("O160", "hole", {
            "baseline_mean": mean, "baseline_sd": None, "raw_deviation": x - mean,
            "standardized": None, "author_exact_z": None,
        }, hole_ids=["HOLE:O160:convention"], coverage_ok=None)
    if conv not in {"sample", "population"}:
        return _r("O160", "hole", {"baseline_mean": mean, "baseline_sd": None,
                  "raw_deviation": x - mean, "standardized": None, "author_exact_z": None},
                  hole_ids=["HOLE:O160:convention"], coverage_ok=None)
    sample = conv == "sample"
    if sample and n < 2:
        return _r("O160", "invalid", {"baseline_mean": mean, "baseline_sd": None,
                  "raw_deviation": x - mean, "standardized": None},
                  base_ok=False, reason="sample deviation requires at least two values")
    denom = n - 1 if sample else n
    var = sum((v - mean) ** 2 for v in xs) / denom
    sd = var.sqrt() if var > 0 else Decimal(0)
    raw = x - mean
    z = None if sd == 0 else raw / sd
    return _r("O160", "computed", {
        "baseline_mean": mean,
        "baseline_sd": sd if sd != 0 or conv else sd,
        "raw_deviation": raw,
        "standardized": z,
        "zero_scale": sd == 0,
    }, known_at=inp.get("known_at"))


@register("O161", ("regression_slope",))
def o161(inp: dict) -> RecipeResult:
    strength = dec(inp.get("strength"))
    slope = dec(inp.get("regression_slope"))
    if strength is None:
        return _r("O161", "hole", {"automatic_strength": None, "source_strength": None}, hole_ids=["HOLE:O161:engine"], coverage_ok=None)
    if not strength.is_finite() or (slope is not None and not slope.is_finite()):
        return _r("O161", "invalid", {"automatic_strength": None, "source_strength": None},
                  base_ok=False, reason="nonfinite supplied strength record")
    holes = [] if inp.get("source_rule_id") and inp.get("scale") else ["HOLE:O161:engine"]
    return _r("O161", "supplied" if not holes else "hole", {
        "source_strength": strength,
        "scale": inp.get("scale"),
        "regression_slope": slope,
        "equivalent_to_slope": False,
        "automatic_strength": None,
    }, known_at=inp.get("known_at"), coverage_ok=True if not holes else None, hole_ids=holes)


add_fixture({"id": "O157-F1", "recipe": "O157", "inputs": {"required_n": 4, "available": [{"id": 1, "at": _yd(9, 0), "value": Decimal("1.5")}, {"id": 2, "at": _yd(9, 0)}, {"id": 3, "at": _yd(9, 0)}], "used_value": Decimal("1.5"), "later_value": Decimal("2.0"), "as_of": _d(9, 0), "known_at": _yd(9, 0), "use_at": _d(9, 0)}, "expected": {"available_series_count": 3, "of": 4, "required_series_present": None, "automatic_verdict": None, "later_replaces": False}})


add_fixture({"id": "O158-F1", "recipe": "O158", "inputs": {"source_cycle_label": "contraction", "indicator_count": 3, "known_at": _d(9, 0), "use_at": _d(9, 30)}, "expected": {"source_cycle_label": "contraction", "majority_vote": False, "automatic_cycle": None}})


add_fixture({"id": "O158-F1b", "recipe": "O158", "inputs": {"indicator_count": 3, "known_at": _d(9, 0), "use_at": _d(9, 30)}, "expected": {"automatic_cycle": None}})


add_fixture({"id": "O159-F1", "recipe": "O159", "inputs": {"c_score": Decimal("2.4"), "z_score": Decimal("1.2"), "known_at": _d(9, 0), "use_at": _d(9, 30)}, "expected": {"source_c_score": Decimal("2.4"), "distinct": True, "automatic_c_score": None}})


add_fixture({"id": "O159-F1b", "recipe": "O159", "inputs": {"z_score": Decimal("1.2"), "known_at": _d(9, 0), "use_at": _d(9, 30)}, "expected": {"automatic_c_score": None, "z_is_c": False}})


add_fixture({"id": "O160-F1", "recipe": "O160", "inputs": {"baseline": [1, 3], "x": 4, "convention": "population", "known_at": _d(9, 0), "use_at": _d(9, 30)}, "expected": {"baseline_mean": Decimal("2"), "baseline_sd": Decimal("1"), "raw_deviation": Decimal("2"), "standardized": Decimal("2")}})


add_fixture({"id": "O160-F1b", "recipe": "O160", "inputs": {"baseline": [1, 3], "x": 4, "convention": "sample", "known_at": _d(9, 0), "use_at": _d(9, 30)}, "expected": {"baseline_sd": Decimal(2).sqrt(), "standardized": _Z_SAMPLE}})


add_fixture({"id": "O160-F1c", "recipe": "O160", "inputs": {"baseline": [1, 3], "x": 4, "known_at": _d(9, 0), "use_at": _d(9, 30)}, "expected": {"author_exact_z": None}})


add_fixture({"id": "O160-F1d", "recipe": "O160", "inputs": {"baseline": [2, 2], "x": 4, "convention": "population", "known_at": _d(9, 0), "use_at": _d(9, 30)}, "expected": {"standardized": None, "zero_scale": True}})


add_fixture({"id": "O161-F1", "recipe": "O161", "inputs": {"strength": 7, "scale": "0-10", "regression_slope": Decimal("0.5"), "known_at": _d(9, 0), "use_at": _d(9, 30)}, "expected": {"source_strength": Decimal("7"), "equivalent_to_slope": False, "automatic_strength": None}})


add_fixture({"id": "O161-F1b", "recipe": "O161", "inputs": {"regression_slope": Decimal("0.5"), "known_at": _d(9, 0), "use_at": _d(9, 30)}, "expected": {"automatic_strength": None}})
