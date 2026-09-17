"""Bounded refinement neighborhoods, promotion gates and trial ledger."""

from __future__ import annotations

from decimal import Decimal
from functools import cmp_to_key
from pathlib import Path
from typing import Any, Callable, Iterable, Mapping, Sequence
import json

import numpy as np

from trading_research.errors import ContractError
from trading_research.research.contracts.evaluation import (
    BLOCK_LENGTH,
    BOOTSTRAP_DRAWS,
    BOOTSTRAP_SEED,
    attainable_holm_floor,
    floor_admits_decision,
    holm,
    moving_block_bootstrap,
)

MINUTE_NS = 60_000_000_000
MAX_NEIGHBORS_PER_BANK = 12
MAX_NEIGHBORS_PER_FAMILY = 24
MAX_REFINED_PLUS_COMBINED = 25
#: EVALUATION.md reports block lengths 1 and 10 beside the frozen block 5 as
#: sensitivity, never as additional selection opportunities.
BLOCK_SENSITIVITY = (1, 10)
SIMPLICITY_THRESHOLD = 0.01
FREQUENCY_FLOOR_FRACTION = 0.5
SUPPORT_GATE_OPPORTUNITIES = 100
SUPPORT_GATE_DAYS = 30
SUPPORT_GATE_OUTER_BLOCKS = 3
BLOCK_POSITIVE_FRACTION = 0.6
CONTROL_OFFSETS = (-2, -1, 1, 2)
ATTRIBUTION_ORDER = (
    "frequency",
    "location_miss",
    "confirmation_delay",
    "adverse_before_target",
    "cost_sensitivity",
    "support",
    "coverage",
)
RETENTION_STATUSES = ("active_selected", "active_baseline", "inactive_retained")
HOLM_ALPHA = 0.05
TRIAL_RECORD_FIELDS = (
    "trial_id",
    "parent_trial_ids",
    "family",
    "branch",
    "outer_fold",
    "stage",
    "bank",
    "parameters",
    "code_hash",
    "data_hash",
    "plan_hash",
    "fit_window",
    "tune_window",
    "calibration_window",
    "outcome_exposure_cutoff",
    "candidate_population_counts",
    "score",
    "loss",
    "support",
    "test_metrics",
    "reason",
    "disposition",
    "runtime",
    "artifacts",
    "failure_attribution",
    "candidate_id",
    "recipe_id",
    "status",
    "replaces_attempt_id",
)
_OUTER_KEYS = ("outer", "outer_score", "test", "test_metrics")
_SKIP_PARAM_KEYS = {"refinement_axis", "refinement_values"}

_F3 = (
    {"axis": "width_S", "values": (0.5, 0.75, 1.0), "freeze": {"efficiency": 0.35}},
    {"axis": "efficiency", "values": (0.2, 0.35, 0.5), "parent_axis": "width_S"},
)
#: SEARCH_CONTRACT refinement table, row "P value-area fraction" (2026-09-16):
#: the chosen fraction -.10, the chosen fraction and +.10, bounded to [.30,.90],
#: at the chosen b and prominence. The chosen value is always among the
#: neighbours, so the round can keep it.
VALUE_AREA_FRACTION_BOUNDS = (Decimal("0.30"), Decimal("0.90"))
VALUE_AREA_FRACTION_STEP = Decimal("0.10")


def value_area_fraction_values(chosen: Any) -> tuple[Decimal, ...]:
    """The registered fraction neighbourhood around `chosen`, inside the bounds."""
    low, high = VALUE_AREA_FRACTION_BOUNDS
    centre = Decimal(str(chosen))
    values = []
    for value in (centre - VALUE_AREA_FRACTION_STEP, centre, centre + VALUE_AREA_FRACTION_STEP):
        bounded = min(max(value, low), high)
        if bounded not in values:
            values.append(bounded)
    return tuple(values)


_P = (
    {"axis": "bandwidth", "values": (0, 2, 4), "freeze": {"prominence": 0.20}},
    {"axis": "prominence", "values": (0.10, 0.20, 0.30), "parent_axis": "bandwidth"},
)
_P_FRACTION = {"axis": "fraction", "values": None, "bounded": VALUE_AREA_FRACTION_BOUNDS}
_S_DEADLINE = ({"axis": "deadline_minutes", "values": (5, 10, 15)},)
_S_TICKS = ({"axis": "favorable_ticks", "values": (1, 2, 4)},)
_S_BOTH = _S_DEADLINE + _S_TICKS
_T = ({"axis": "shift_minutes", "values": (-30, -15, 0, 15, 30)},)

NEIGHBORHOODS: dict[str, tuple[dict[str, Any], ...]] = {
    "F1": ({"axis": "minutes", "values": (30, 60, 90)},),
    "F2": ({"axis": "volume_threshold_multiplier", "values": (0.75, 1.0, 1.25)},),
    "F3": _F3,
    "P1": _P,
    "P2": _P,
    "P3": _P + (_P_FRACTION,),
    "P4": _P + (_P_FRACTION,),
    "R1": ({"axis": "dispersion", "values": (0.5, 1.0, 1.5)},),
    "R2": (),
    "C1": ({"axis": "window_minutes", "values": (2, 5, 10)},),
    "C2": ({"axis": "half_life_s", "values": (120, 300, 600)},),
    "C3": ({"axis": "history_sessions", "values": (10, 20, 40)},),
    "S1": _S_DEADLINE,
    "S2": _S_TICKS,
    "S3": _S_BOTH,
    "S4": _S_BOTH,
    "M1": ({"axis": "max_prior_contacts", "values": (0, 1, 2)},),
    "M2": ({"axis": "prior_reaction_S", "values": (0.1, 0.25, 0.5)},),
    "T1": _T,
    "T2": _T,
    "T3": _T,
    "T4": _T,
}


def _as_float(value: Any, default: float | None = None) -> float | None:
    if value is None:
        return default
    if isinstance(value, bool):
        return default
    if isinstance(value, str) and value.endswith("S"):
        try:
            return float(value[:-1])
        except ValueError:
            return default
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _render_value(value: Any) -> str:
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, int) and not isinstance(value, bool):
        return str(value)
    if isinstance(value, float):
        text = format(value, ".12f").rstrip("0").rstrip(".")
        if text in {"", "-"}:
            return "0"
        return text
    return str(value)


def _normalize_scalar(value: Any) -> Any:
    if isinstance(value, bool):
        return value
    if isinstance(value, int):
        return float(value)
    if isinstance(value, float):
        return float(value)
    if isinstance(value, str):
        if value.endswith("S"):
            parsed = _as_float(value)
            if parsed is not None:
                return parsed
        try:
            return float(value)
        except ValueError:
            return value
    return value


def _canonical_params(parameters: Mapping[str, Any] | None) -> tuple[tuple[str, Any], ...]:
    raw = dict(parameters or {})
    out: dict[str, Any] = {}
    for key, value in raw.items():
        if key in _SKIP_PARAM_KEYS:
            continue
        out[key] = _normalize_scalar(value)
    if "width_S" not in out and "width_mult" in out:
        width = _as_float(out["width_mult"])
        if width is not None:
            out["width_S"] = width
    if "width_S" in out:
        width = _as_float(out["width_S"])
        if width is not None:
            out["width_S"] = width
            out["width_mult"] = width
    if "deadline_minutes" in out:
        minutes = _as_float(out["deadline_minutes"])
        if minutes is not None:
            out["deadline_minutes"] = minutes
            out["deadline_s"] = float(int(round(minutes * 60)))
    elif "deadline_s" in out:
        seconds = _as_float(out["deadline_s"])
        if seconds is not None:
            out["deadline_s"] = seconds
            out["deadline_minutes"] = seconds / 60.0
    if "prior_reaction_S" in out:
        reaction = _as_float(out["prior_reaction_S"])
        if reaction is not None:
            out["prior_reaction_S"] = reaction
            out["prior_reaction"] = f"{_render_value(reaction)}S"
    elif "prior_reaction" in out:
        reaction = _as_float(out["prior_reaction"])
        if reaction is not None:
            out["prior_reaction_S"] = reaction
            out["prior_reaction"] = f"{_render_value(reaction)}S"
    items: list[tuple[str, Any]] = []
    for key in sorted(out):
        value = out[key]
        if isinstance(value, float):
            items.append((key, round(value, 10)))
        else:
            items.append((key, value))
    return tuple(items)


def _identity(row: Mapping[str, Any]) -> tuple[Any, ...]:
    return (
        row.get("family"),
        row.get("branch"),
        row.get("recipe_id"),
        _canonical_params(row.get("parameters") or {}),
    )


def _parent_axis_value(parameters: Mapping[str, Any], axis: str) -> Any:
    if axis == "width_S":
        if "width_S" in parameters:
            return _as_float(parameters["width_S"], 0.75)
        if "width_mult" in parameters:
            return _as_float(parameters["width_mult"], 0.75)
        return 0.75
    if axis in parameters:
        value = parameters[axis]
        numeric = _as_float(value)
        return value if numeric is None else numeric
    defaults = {"bandwidth": 0, "prominence": 0.20, "efficiency": 0.35}
    return defaults.get(axis)


def _apply_axis(axis: str, value: Any) -> dict[str, Any]:
    applied = {axis: value}
    if axis == "deadline_minutes":
        applied["deadline_s"] = int(value) * 60
    elif axis == "width_S":
        applied["width_mult"] = value
    elif axis == "prior_reaction_S":
        applied["prior_reaction"] = f"{_render_value(value)}S"
    return applied


def _spec_for(recipe_id: str, parameters: Mapping[str, Any] | None) -> tuple[dict[str, Any], ...] | None:
    if recipe_id in NEIGHBORHOODS:
        return NEIGHBORHOODS[recipe_id]
    params = dict(parameters or {})
    axis = params.get("refinement_axis")
    values = params.get("refinement_values")
    if axis is None or values is None:
        return None
    return ({"axis": str(axis), "values": tuple(values)},)


def neighborhood_values(recipe_id: str, parameters: Mapping[str, Any] | None = None) -> list[dict[str, Any]]:
    params = dict(parameters or {})
    spec = _spec_for(recipe_id, params)
    if not spec:
        return []
    rows: list[dict[str, Any]] = []
    for sweep in spec:
        axis = str(sweep["axis"])
        if axis == "fraction" and sweep.get("values") is None:
            chosen = params.get("fraction")
            if chosen is None:
                continue
            for value in value_area_fraction_values(chosen):
                merged = dict(params)
                merged["fraction"] = str(value)
                rows.append(
                    {"axis": axis, "value": str(value), "parameters": merged, "changed_axis": axis}
                )
            continue
        freeze = dict(sweep.get("freeze") or {})
        parent_axis = sweep.get("parent_axis")
        if parent_axis:
            freeze[str(parent_axis)] = _parent_axis_value(params, str(parent_axis))
            freeze.update(_apply_axis(str(parent_axis), freeze[str(parent_axis)]))
        for value in sweep["values"]:
            applied = dict(freeze)
            applied.update(_apply_axis(axis, value))
            merged = dict(params)
            merged.update(applied)
            rows.append(
                {
                    "axis": axis,
                    "value": value,
                    "parameters": merged,
                    "changed_axis": axis,
                }
            )
    return rows


def _candidate_id(family: str, branch: str, recipe_id: str, axis: str, value: Any) -> str:
    return f"{family}:{branch}:{recipe_id}:{axis}={_render_value(value)}"


def _copy_list(value: Any) -> list[Any]:
    if value is None:
        return []
    if isinstance(value, list):
        return list(value)
    if isinstance(value, tuple):
        return list(value)
    return [value]


def _required_available_at_ns(parent: Mapping[str, Any], fold: Mapping[str, Any], recipe_id: str, parameters: Mapping[str, Any]) -> int:
    if recipe_id in {"T1", "T2", "T3", "T4"}:
        issue = parent.get("issue_at_ns", fold.get("issue_at_ns", fold.get("fit_cutoff_ns", 0)))
        shift = int(_as_float(parameters.get("shift_minutes"), 0) or 0)
        return int(issue) + shift * MINUTE_NS
    if parent.get("required_available_at_ns") is not None:
        return int(parent["required_available_at_ns"])
    if fold.get("required_available_at_ns") is not None:
        return int(fold["required_available_at_ns"])
    return 0


def _formation_available_at_ns(parent: Mapping[str, Any], fold: Mapping[str, Any]) -> int | None:
    if parent.get("formation_available_at_ns") is not None:
        return int(parent["formation_available_at_ns"])
    if fold.get("formation_available_at_ns") is not None:
        return int(fold["formation_available_at_ns"])
    return None


def generate_neighbors(
    family: str,
    fold: Mapping[str, Any],
    selected_banks: Sequence[Mapping[str, Any]],
    *,
    attempted: Iterable[Mapping[str, Any]] = (),
    enforce_past_only: bool = True,
) -> list[dict[str, Any]]:
    seen = {_identity(row) for row in attempted}
    fit_cutoff_ns = int(fold.get("fit_cutoff_ns") or 0)
    family_attempted = 0
    bank_attempted: dict[str, int] = {}
    out: list[dict[str, Any]] = []

    for parent in selected_banks:
        recipe_id = str(parent.get("recipe_id") or "")
        branch = str(parent.get("branch") or "")
        bank = str(parent.get("bank") or "")
        parent_params = dict(parent.get("parameters") or {})
        spec = _spec_for(recipe_id, parent_params)
        parent_ids = _copy_list(parent.get("parent_trial_ids"))
        if parent.get("trial_id"):
            parent_ids = [parent["trial_id"]]
        elif parent.get("candidate_id") and not parent_ids:
            parent_ids = [parent["candidate_id"]]
        required_stages = _copy_list(parent.get("required_stages"))
        seen.add(_identity({"family": family, "branch": branch, "recipe_id": recipe_id, "parameters": parent_params}))

        if spec is None or (recipe_id in NEIGHBORHOODS and not spec):
            row = {
                "candidate_id": f"{family}:{branch}:{recipe_id}:none",
                "family": family,
                "branch": branch,
                "bank": bank,
                "recipe_id": recipe_id,
                "parameters": dict(parent_params),
                "changed_axis": None,
                "changed_axes": 0,
                "required_stages": required_stages,
                "parent_trial_ids": parent_ids,
                "status": "not_applicable",
                "reason": "no_numeric_refinement",
                "required_available_at_ns": _required_available_at_ns(parent, fold, recipe_id, parent_params),
                "synthetic": bool(parent.get("synthetic", False)),
            }
            out.append(row)
            continue

        values = neighborhood_values(recipe_id, parent_params)
        for item in values:
            parameters = dict(item["parameters"])
            axis = str(item["axis"])
            value = item["value"]
            required_at = _required_available_at_ns(parent, fold, recipe_id, parameters)
            row = {
                "candidate_id": _candidate_id(family, branch, recipe_id, axis, value),
                "family": family,
                "branch": branch,
                "bank": bank,
                "recipe_id": recipe_id,
                "parameters": parameters,
                "changed_axis": axis,
                "changed_axes": 1,
                "required_stages": list(required_stages),
                "parent_trial_ids": list(parent_ids),
                "status": "attempted",
                "reason": None,
                "required_available_at_ns": required_at,
                "synthetic": bool(parent.get("synthetic", False)),
            }
            ident = _identity(row)
            if ident in seen:
                row["status"] = "duplicate"
                row["reason"] = "duplicate"
            elif recipe_id in {"T1", "T2", "T3", "T4"}:
                formation_at = _formation_available_at_ns(parent, fold)
                if formation_at is not None and formation_at > required_at:
                    row["status"] = "not_applicable"
                    row["reason"] = "formation_unavailable"
            if row["status"] == "attempted" and enforce_past_only and required_at > fit_cutoff_ns:
                row["status"] = "not_applicable"
                row["reason"] = "past_only_allowlist"
            if row["status"] == "attempted":
                used_bank = bank_attempted.get(bank, 0)
                if used_bank >= MAX_NEIGHBORS_PER_BANK:
                    row["status"] = "not_applicable"
                    row["reason"] = "cap_per_bank"
                elif family_attempted >= MAX_NEIGHBORS_PER_FAMILY:
                    row["status"] = "not_applicable"
                    row["reason"] = "cap_per_family"
                else:
                    bank_attempted[bank] = used_bank + 1
                    family_attempted += 1
                    seen.add(ident)
            else:
                seen.add(ident)
            out.append(row)
    return out


def combine_candidates(
    family: str,
    fold: Mapping[str, Any],
    ingredient_a: Mapping[str, Any],
    ingredient_b: Mapping[str, Any],
    *,
    b02_score: float,
    score_a: float,
    score_b: float,
    combo_score: float,
    source_dependencies_causal: bool = True,
    refined_count: int = 0,
) -> dict[str, Any] | None:
    del fold
    if score_a <= b02_score or score_b <= b02_score:
        return None
    if not source_dependencies_causal:
        return None
    if refined_count + 1 > MAX_REFINED_PLUS_COMBINED:
        return None
    branch = str(ingredient_a.get("branch") or ingredient_b.get("branch") or "")
    id_a = str(ingredient_a.get("candidate_id") or "a")
    id_b = str(ingredient_b.get("candidate_id") or "b")
    parameters = dict(ingredient_a.get("parameters") or {})
    parameters.update(dict(ingredient_b.get("parameters") or {}))
    if combo_score > score_a and combo_score > score_b:
        interaction = "synergistic"
    elif combo_score < score_a and combo_score < score_b:
        interaction = "antagonistic"
    else:
        interaction = "additive"
    stages = _copy_list(ingredient_a.get("required_stages"))
    for stage in _copy_list(ingredient_b.get("required_stages")):
        if stage not in stages:
            stages.append(stage)
    return {
        "candidate_id": f"{family}:{branch}:COMBINED:{id_a}+{id_b}",
        "family": family,
        "branch": branch,
        "bank": "COMBINED",
        "recipe_id": "COMBINED",
        "parameters": parameters,
        "changed_axis": "combination",
        "changed_axes": 2,
        "required_stages": stages,
        "parent_trial_ids": [
            ingredient_a.get("trial_id") or ingredient_a.get("candidate_id"),
            ingredient_b.get("trial_id") or ingredient_b.get("candidate_id"),
        ],
        "status": "attempted",
        "reason": None,
        "interaction": interaction,
        "vs_ingredient_a": combo_score - score_a,
        "vs_ingredient_b": combo_score - score_b,
        "vs_b02": combo_score - b02_score,
        "score": combo_score,
        "synthetic": bool(ingredient_a.get("synthetic") or ingredient_b.get("synthetic")),
    }


def changed_axes(candidate: Mapping[str, Any]) -> int:
    if candidate.get("changed_axes") is not None:
        return int(candidate["changed_axes"])
    axis = candidate.get("changed_axis")
    if axis in (None, "none", "baseline", ""):
        return 0
    if axis == "combination":
        return 2
    return 1


def _inner_only(candidate: Mapping[str, Any]) -> dict[str, Any]:
    body = {key: value for key, value in candidate.items() if key not in _OUTER_KEYS}
    inner = candidate.get("inner_tuning")
    if isinstance(inner, dict):
        body["inner_tuning"] = dict(inner)
    return body


def _numeric_score(candidate: Mapping[str, Any]) -> float:
    inner = candidate.get("inner_tuning")
    if isinstance(inner, dict) and inner.get("mean_daily_net_points") is not None:
        return float(inner["mean_daily_net_points"])
    if candidate.get("score") is not None:
        return float(candidate["score"])
    return 0.0


def simpler_wins(simple: Mapping[str, Any], complex: Mapping[str, Any], *, enforce_simplicity: bool = True) -> dict[str, Any]:
    if not enforce_simplicity:
        return dict(complex)
    simple_score = _numeric_score(simple)
    complex_score = _numeric_score(complex)
    denom = max(abs(simple_score), 1e-12)
    relative = (complex_score - simple_score) / denom
    if relative > SIMPLICITY_THRESHOLD:
        return dict(complex)
    return dict(simple)


def _compare_inner(left: Mapping[str, Any], right: Mapping[str, Any], *, enforce_simplicity: bool) -> int:
    left_axes = changed_axes(left)
    right_axes = changed_axes(right)
    if enforce_simplicity and left_axes != right_axes:
        simple, complex_ = (left, right) if left_axes < right_axes else (right, left)
        winner = simpler_wins(simple, complex_, enforce_simplicity=True)
        winner_id = winner.get("candidate_id")
        simple_id = simple.get("candidate_id")
        if winner_id == simple_id or winner is simple:
            return -1 if simple is left else 1
        return -1 if complex_ is left else 1
    left_score = _numeric_score(left)
    right_score = _numeric_score(right)
    if left_score > right_score:
        return -1
    if left_score < right_score:
        return 1
    left_keys = len(left.get("parameters") or {})
    right_keys = len(right.get("parameters") or {})
    if left_keys != right_keys:
        return -1 if left_keys < right_keys else 1
    left_id = str(left.get("candidate_id") or "")
    right_id = str(right.get("candidate_id") or "")
    if left_id < right_id:
        return -1
    if left_id > right_id:
        return 1
    return 0


def rank_inner(candidates: Sequence[Mapping[str, Any]], *, enforce_simplicity: bool = True) -> list[dict[str, Any]]:
    cleaned = [_inner_only(row) for row in candidates]
    return sorted(cleaned, key=cmp_to_key(lambda a, b: _compare_inner(a, b, enforce_simplicity=enforce_simplicity)))


def _inner_support_ok(inner: Mapping[str, Any]) -> bool:
    if "inner_support_ok" in inner:
        return bool(inner["inner_support_ok"])
    opportunities = inner.get("support_opportunities") or 0
    days = inner.get("support_days") or 0
    return opportunities > 0 and days > 0


def select_banks(
    family: str,
    candidates: Sequence[Mapping[str, Any]],
    *,
    max_banks: int = 2,
    enforce_simplicity: bool = True,
) -> list[dict[str, Any]]:
    cleaned = [_inner_only(row) for row in candidates]
    by_bank: dict[str, list[dict[str, Any]]] = {}
    for row in cleaned:
        row_family = row.get("family")
        if row_family not in (None, family):
            continue
        bank = str(row.get("bank") or "")
        by_bank.setdefault(bank, []).append(row)
    representatives: list[dict[str, Any]] = []
    for group in by_bank.values():
        ranked = rank_inner(group, enforce_simplicity=enforce_simplicity)
        if not ranked:
            continue
        best = ranked[0]
        inner = best.get("inner_tuning") or {}
        improvement = inner.get("improvement_vs_b02")
        if improvement is None:
            improvement = 0.0
        if float(improvement) < 0:
            continue
        if not _inner_support_ok(inner):
            continue
        representatives.append(best)
    representatives.sort(key=lambda row: (-_numeric_score(row), str(row.get("candidate_id") or "")))
    chosen = representatives[:max_banks]
    chosen.sort(key=lambda row: str(row.get("bank") or ""))
    return [
        {
            "bank": row.get("bank"),
            "candidate_id": row.get("candidate_id"),
            "recipe_id": row.get("recipe_id"),
            "family": row.get("family", family),
            "branch": row.get("branch"),
            "parameters": dict(row.get("parameters") or {}),
            "changed_axes": changed_axes(row),
            "inner_tuning": dict(row.get("inner_tuning") or {}),
        }
        for row in chosen
    ]


def _valid_diffs(daily_diff: Sequence[Any]) -> list[float]:
    return [float(value) for value in daily_diff if value is not None]


def _valid_diffs_with_segments(
    daily_diff: Sequence[Any], segments: Sequence[Any] | None
) -> tuple[list[float], list[Any] | None]:
    """Drop the missing days from the series and their labels with them, so the
    segment labels stay aligned with the values they describe."""
    if segments is None:
        return _valid_diffs(daily_diff), None
    labels = list(segments)
    if len(labels) != len(list(daily_diff)):
        raise ContractError("segments must align with the daily differences")
    values: list[float] = []
    kept: list[Any] = []
    for value, label in zip(daily_diff, labels):
        if value is None:
            continue
        values.append(float(value))
        kept.append(label)
    return values, kept


def centered_bootstrap_pvalue(
    daily_diff: Sequence[Any],
    *,
    bootstrap_fn: Callable[..., Any] = moving_block_bootstrap,
    segments: Sequence[Any] | None = None,
    sensitivity_blocks: Sequence[int] = BLOCK_SENSITIVITY,
) -> dict[str, Any]:
    """The frozen block bootstrap of EVALUATION.md.

    `segments` are the calendar-year labels of the paired days in order: block
    starts are drawn within a year and wrap only inside it. Block lengths 1 and
    10 are reported beside the block-5 interval as sensitivity, never as extra
    selection opportunities.
    """
    valid, kept = _valid_diffs_with_segments(daily_diff, segments)
    mean_diff = float(np.mean(valid)) if valid else 0.0
    draws = bootstrap_fn(
        valid, block=BLOCK_LENGTH, draws=BOOTSTRAP_DRAWS, seed=BOOTSTRAP_SEED, segments=kept
    )
    draws_arr = np.asarray(draws, dtype=np.float64)
    count = int(draws_arr.size)
    if count == 0:
        p_raw = 1.0
        ci_low = 0.0
        ci_high = 0.0
    else:
        p_raw = (1 + int(np.count_nonzero((draws_arr - mean_diff) >= mean_diff))) / (count + 1)
        ci_low = float(np.percentile(draws_arr, 2.5))
        ci_high = float(np.percentile(draws_arr, 97.5))
    sensitivity: dict[str, Any] = {}
    for block in sensitivity_blocks:
        if block == BLOCK_LENGTH or not valid:
            continue
        other = np.asarray(
            bootstrap_fn(valid, block=int(block), draws=BOOTSTRAP_DRAWS, seed=BOOTSTRAP_SEED, segments=kept),
            dtype=np.float64,
        )
        if other.size:
            sensitivity[f"block_{int(block)}"] = {
                "ci_low": float(np.percentile(other, 2.5)),
                "ci_high": float(np.percentile(other, 97.5)),
            }
    return {
        "p_raw": float(p_raw),
        "mean_diff": mean_diff,
        "ci_low": ci_low,
        "ci_high": ci_high,
        "block_length": BLOCK_LENGTH,
        "segments": len({label for label in kept}) if kept else 0,
        "block_sensitivity": sensitivity,
        "draws": draws_arr,
    }


def support_sensitivity(opportunities: int, days: int, blocks: int) -> dict[str, Any]:
    half = {
        "opportunities": 50,
        "days": 15,
        "blocks": SUPPORT_GATE_OUTER_BLOCKS,
        "pass": opportunities >= 50 and days >= 15 and blocks >= SUPPORT_GATE_OUTER_BLOCKS,
    }
    nominal = {
        "opportunities": SUPPORT_GATE_OPPORTUNITIES,
        "days": SUPPORT_GATE_DAYS,
        "blocks": SUPPORT_GATE_OUTER_BLOCKS,
        "pass": (
            opportunities >= SUPPORT_GATE_OPPORTUNITIES
            and days >= SUPPORT_GATE_DAYS
            and blocks >= SUPPORT_GATE_OUTER_BLOCKS
        ),
    }
    twice = {
        "opportunities": 200,
        "days": 60,
        "blocks": SUPPORT_GATE_OUTER_BLOCKS,
        "pass": opportunities >= 200 and days >= 60 and blocks >= SUPPORT_GATE_OUTER_BLOCKS,
    }
    return {"half": half, "nominal": nominal, "twice": twice}


def _support_pass(opportunities: int, days: int, blocks: int) -> bool:
    return (
        opportunities >= SUPPORT_GATE_OPPORTUNITIES
        and days >= SUPPORT_GATE_DAYS
        and blocks >= SUPPORT_GATE_OUTER_BLOCKS
    )


def _adjusted_p_from_holm_rows(holm_rows: Sequence[Mapping[str, Any]], *, alpha: float) -> dict[int, float]:
    ordered = sorted(holm_rows, key=lambda row: (float(row["p"]), int(row["index"])))
    adjusted: dict[int, float] = {}
    running = 0.0
    for row in ordered:
        threshold = float(row["threshold"])
        p_value = float(row["p"])
        if threshold == 0:
            step = 0.0 if p_value <= 0 else 1.0
        else:
            step = min(1.0, p_value * (alpha / threshold))
        running = max(running, step)
        adjusted[int(row["index"])] = running
    return adjusted


def _trial_index(candidate: Mapping[str, Any], stage_trials: Sequence[Mapping[str, Any]]) -> int | None:
    trial_id = candidate.get("trial_id")
    candidate_id = candidate.get("candidate_id")
    for index, trial in enumerate(stage_trials):
        if trial_id is not None and trial.get("trial_id") == trial_id:
            return index
        if candidate_id is not None and trial.get("candidate_id") == candidate_id:
            return index
    return None


def evaluate_promotion(
    candidate: Mapping[str, Any],
    stage_trials: Sequence[Mapping[str, Any]],
    *,
    holm_fn: Callable[..., Any] = holm,
    bootstrap_fn: Callable[..., Any] = moving_block_bootstrap,
    apply_holm: bool = True,
    apply_frequency_floor: bool = True,
) -> dict[str, Any]:
    computed = centered_bootstrap_pvalue(
        candidate.get("daily_diff") or (),
        bootstrap_fn=bootstrap_fn,
        segments=candidate.get("daily_segments"),
    )
    pvalues: list[float] = []
    for trial in stage_trials:
        raw = trial.get("p_raw")
        pvalues.append(1.0 if raw is None else float(raw))
    index = _trial_index(candidate, stage_trials)
    if index is None:
        pvalues.append(float(computed["p_raw"]))
        index = len(pvalues) - 1
    p_raw = float(pvalues[index])
    holm_rows = holm_fn(pvalues, alpha=HOLM_ALPHA) if pvalues else []
    reject_map = {int(row["index"]): bool(row["reject"]) for row in holm_rows}
    holm_reject = bool(reject_map.get(index, False))
    if not apply_holm:
        holm_reject = p_raw <= 0.05
    adjusted = _adjusted_p_from_holm_rows(holm_rows, alpha=HOLM_ALPHA)
    p_holm = float(adjusted.get(index, 1.0)) if adjusted else 1.0
    family_size = len(pvalues)
    p_floor = attainable_holm_floor(family_size)
    floor_ok = floor_admits_decision(family_size)

    opportunities = int(candidate.get("resolved_opportunities") or 0)
    days = int(candidate.get("eligible_test_days") or 0)
    blocks = int(candidate.get("supported_outer_blocks") or 0)
    # EVALUATION.md (amended 2026-09-17): the gate applies to both sides of the
    # pair. A candidate whose own baseline is below the gate is not an upgrade of
    # a supported rule, whatever its own frequency, so the pair is inconclusive.
    baseline_opportunities = int(
        candidate.get("baseline_resolved_opportunities")
        if candidate.get("baseline_resolved_opportunities") is not None
        else candidate.get("baseline_entries") or 0
    )
    candidate_support_ok = _support_pass(opportunities, days, blocks)
    baseline_support_ok = _support_pass(baseline_opportunities, days, blocks)
    support_ok = candidate_support_ok and baseline_support_ok
    sensitivity = support_sensitivity(opportunities, days, blocks)
    baseline_sensitivity = support_sensitivity(baseline_opportunities, days, blocks)
    entry_ratio = (
        float(opportunities) / float(baseline_opportunities) if baseline_opportunities else None
    )

    block_improvements = [float(value) for value in (candidate.get("block_improvements") or ()) if value is not None]
    if block_improvements:
        block_positive_fraction = sum(1 for value in block_improvements if value > 0) / len(block_improvements)
    else:
        block_positive_fraction = 0.0
    blocks_ok = block_positive_fraction >= BLOCK_POSITIVE_FRACTION

    candidate_entries = float(candidate.get("candidate_entries") or 0)
    baseline_entries = float(candidate.get("baseline_entries") or 0)
    frequency_floor_pass = candidate_entries >= FREQUENCY_FLOOR_FRACTION * baseline_entries

    software_ok = bool(candidate.get("software_causality_pass"))
    cost_fail = bool(candidate.get("cost_stress_sign_reversal"))
    coverage_fail = bool(candidate.get("unexplained_coverage_loss"))
    mean_diff = float(computed["mean_diff"])
    ci_low = float(computed["ci_low"])
    mean_ok = mean_diff > 0
    ci_ok = ci_low > 0
    gates_except_frequency = (
        software_ok
        and support_ok
        and mean_ok
        and ci_ok
        and holm_reject
        and blocks_ok
        and not cost_fail
        and not coverage_fail
    )
    frequency_ok = frequency_floor_pass or not apply_frequency_floor
    promoted = bool(gates_except_frequency and frequency_ok)
    replace_baseline_allowed = bool(gates_except_frequency and frequency_ok)

    gates_except_holm = (
        software_ok
        and support_ok
        and mean_ok
        and ci_ok
        and blocks_ok
        and not cost_fail
        and not coverage_fail
        and (frequency_floor_pass or not apply_frequency_floor)
    )
    if promoted:
        disposition = "promoted"
        reason = None
    elif not support_ok:
        disposition = "inconclusive_support"
        reason = "support" if not candidate_support_ok else "baseline_support"
    elif gates_except_holm and not holm_reject:
        # EVALUATION.md (amended 2026-09-17): every other gate passed and only the
        # multiplicity step failed. That is not evidence against the candidate; it
        # stays in the retention set to be re-tested under a smaller family.
        disposition = "inconclusive_multiplicity"
        reason = "holm"
        replace_baseline_allowed = False
    elif gates_except_frequency and not frequency_floor_pass:
        disposition = "high_selectivity"
        reason = "frequency"
        replace_baseline_allowed = False
    elif not mean_ok:
        disposition = "retained_baseline"
        reason = "no_improvement"
    else:
        disposition = "rejected_by_evidence"
        if not software_ok:
            reason = "software_causality"
        elif cost_fail:
            reason = "cost_stress"
        elif coverage_fail:
            reason = "coverage"
        elif not holm_reject:
            reason = "holm"
        elif not ci_ok:
            reason = "ci"
        elif not blocks_ok:
            reason = "blocks"
        else:
            reason = "rejected_by_evidence"

    return {
        "promoted": promoted,
        "disposition": disposition,
        "reason": reason,
        "p_raw": p_raw,
        "p_holm": float(p_holm),
        "ci_low": ci_low,
        "ci_high": float(computed["ci_high"]),
        "mean_diff": mean_diff,
        "block_sensitivity": computed.get("block_sensitivity", {}),
        "bootstrap_segments": computed.get("segments"),
        "support_pass": support_ok,
        "support_pass_candidate": candidate_support_ok,
        "support_pass_baseline": baseline_support_ok,
        "resolved_opportunities": opportunities,
        "baseline_resolved_opportunities": baseline_opportunities,
        "eligible_test_days": days,
        "supported_outer_blocks": blocks,
        "entry_ratio_to_baseline": entry_ratio,
        "candidate_mean_net_points": candidate.get("candidate_mean_net_points"),
        "baseline_mean_net_points": candidate.get("baseline_mean_net_points"),
        "support_sensitivity": sensitivity,
        "baseline_support_sensitivity": baseline_sensitivity,
        "family_size": family_size,
        "attainable_p_floor": p_floor,
        "attainable_floor_admits_decision": floor_ok,
        "frequency_floor_pass": frequency_floor_pass,
        "holm_reject": holm_reject,
        "software_causality_pass": software_ok,
        "block_positive_fraction": float(block_positive_fraction),
        "replace_baseline_allowed": replace_baseline_allowed,
    }


def _location_miss(diagnostics: Mapping[str, Any]) -> bool:
    if diagnostics.get("objective_reached"):
        return False
    nearest = diagnostics.get("nearest_approach_S")
    near = nearest is not None and float(nearest) <= 0.25
    adverse = diagnostics.get("adverse_S_before_favorable_0_5S")
    if isinstance(adverse, bool):
        adv = adverse
    elif adverse is None:
        adv = False
    else:
        adv = float(adverse) >= 0.5
    return near or adv


def attribute_failure(diagnostics: Mapping[str, Any]) -> list[str]:
    if diagnostics.get("runtime_failure") or diagnostics.get("timed_out"):
        return []
    candidate_entries = float(diagnostics.get("candidate_entries") or 0)
    baseline_entries = float(diagnostics.get("baseline_entries") or 0)
    flags = {
        "frequency": candidate_entries < FREQUENCY_FLOOR_FRACTION * baseline_entries,
        "location_miss": _location_miss(diagnostics),
        "confirmation_delay": float(diagnostics.get("missed_move_share") or 0)
        > float(diagnostics.get("family_median_missed_move_share") or 0),
        "adverse_before_target": float(diagnostics.get("stop_first_share") or 0)
        > float(diagnostics.get("family_baseline_stop_first_share") or 0),
        "cost_sensitivity": bool(diagnostics.get("cost_stress_sign_reversal")),
        "support": not _support_pass(
            int(diagnostics.get("resolved_opportunities") or 0),
            int(diagnostics.get("eligible_test_days") or 0),
            int(diagnostics.get("supported_outer_blocks") or 0),
        ),
        "coverage": bool(diagnostics.get("unexplained_coverage_loss")),
    }
    return [name for name in ATTRIBUTION_ORDER if flags[name]]


def make_trial_record(payload: Mapping[str, Any] | None = None, **kwargs: Any) -> dict[str, Any]:
    body: dict[str, Any] = {}
    if payload:
        body.update(dict(payload))
    body.update(kwargs)
    record = {key: body.get(key) for key in TRIAL_RECORD_FIELDS}
    if record["parent_trial_ids"] is None:
        record["parent_trial_ids"] = []
    if record["failure_attribution"] is None:
        record["failure_attribution"] = []
    if record["parameters"] is None:
        record["parameters"] = {}
    if record["candidate_population_counts"] is None:
        record["candidate_population_counts"] = {}
    if record["support"] is None:
        record["support"] = {}
    if record["test_metrics"] is None:
        record["test_metrics"] = {}
    if record["artifacts"] is None:
        record["artifacts"] = {}
    if record["status"] is None:
        record["status"] = "attempted"
    if "synthetic" in body:
        record["synthetic"] = body["synthetic"]
    return record


class TrialLedger:
    def __init__(self, path: str | Path) -> None:
        self.path = Path(path)

    def read(self) -> list[dict[str, Any]]:
        if not self.path.is_file():
            return []
        rows: list[dict[str, Any]] = []
        for line in self.path.read_text().splitlines():
            if line.strip():
                rows.append(json.loads(line))
        return rows

    def append(self, record: Mapping[str, Any]) -> None:
        trial_id = record.get("trial_id")
        existing = {row.get("trial_id") for row in self.read()}
        if trial_id in existing:
            raise ContractError("append-only")
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(dict(record)) + "\n")

    def replace_attempt(self, old_id: str, new_record: Mapping[str, Any]) -> None:
        new_id = new_record.get("trial_id")
        if not new_id or new_id == old_id:
            raise ContractError("replace_attempt requires a new trial_id; ledger is append-only")
        body = dict(new_record)
        body["replaces_attempt_id"] = old_id
        self.append(body)


def selected_rules_by_fold(
    fold_roles: Sequence[Mapping[str, Any]],
    descriptive_recommendation: Mapping[str, Any] | None,
) -> dict[str, Any]:
    folds = [dict(row) for row in fold_roles]
    return {
        "schema_version": "research-selected-rules-by-fold-v1",
        "causal": True,
        "folds": folds,
        "all_history_descriptive_recommendation": descriptive_recommendation,
    }


def family_dispositions(rows: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    families: list[dict[str, Any]] = []
    for row in rows:
        status = row.get("status")
        if status not in RETENTION_STATUSES:
            raise ContractError(f"unknown retention status {status}")
        attribution = list(row.get("failure_attribution") or [])
        families.append(
            {
                "family": row.get("family"),
                "status": status,
                "candidate_id": row.get("candidate_id"),
                "failure_attribution": attribution,
                "first_attribution": attribution[0] if attribution else None,
            }
        )
    return {"schema_version": "research-family-dispositions-v1", "families": families}


# ==========================================================================
# P15-18 — one bounded refinement round over P15-17's allowlist.
#
# The bank is a pure function of the breadth allowlist; execution reuses the
# breadth runner (search_run) with that bank, and scoring reuses the breadth
# evaluation. Refinement never reads outer test data to choose anything.
# ==========================================================================

P15_18_TASK_ID = "P15-18"
REFINEMENT_BANK_SCHEMA = "research-p15-18-refinement-bank-v1"
#: The registered T neighbourhood is -30..+30 minutes (SEARCH_CONTRACT). The
#: fold guard compares an availability instant to the fit cutoff, so the parent
#: issue is taken one maximum shift before the cutoff: every registered shift is
#: then decidable by the cutoff and anything outside the registered set is not.
MAX_TIMING_SHIFT_MINUTES = 30


def fold_guard(inner_cutoff_ns: int) -> dict[str, Any]:
    """The fold dict `generate_neighbors` needs: the fit cutoff and the parent
    issue instant the timing neighbourhood is measured from."""
    return {
        "fit_cutoff_ns": int(inner_cutoff_ns),
        "issue_at_ns": int(inner_cutoff_ns) - MAX_TIMING_SHIFT_MINUTES * MINUTE_NS,
    }


def build_refinement_bank(
    allowlist: Mapping[str, Any],
    inner_cutoff_ns: Mapping[int, int],
    *,
    attempted: Iterable[Mapping[str, Any]] = (),
    branches: Mapping[str, str] | None = None,
) -> dict[str, Any]:
    """The whole refinement bank, per fold and family, from the allowlist alone.

    Pure: no run root, no market, no outcome. Every proposed neighbour keeps a
    row -- attempted, duplicate or not_applicable with its reason -- so the
    caps and the contract's neighbourhoods are auditable from this file.
    """
    folds: list[dict[str, Any]] = []
    rows: list[dict[str, Any]] = []
    for fold in allowlist["folds"]:
        year = int(fold["outer_fold"])
        guard = fold_guard(inner_cutoff_ns[year])
        families: list[dict[str, Any]] = []
        for family in fold["families"]:
            banks = [
                dict(
                    bank,
                    issue_at_ns=guard["issue_at_ns"],
                    branch=bank.get("branch")
                    or (branches or {}).get(str(bank.get("candidate_id")), ""),
                )
                for bank in family.get("selected_banks") or []
            ]
            missing = [bank["candidate_id"] for bank in banks if not bank["branch"]]
            if missing:
                raise ContractError(
                    f"selected banks without a branch would collide in the neighbour identity: {missing}"
                )
            if not banks:
                families.append(
                    {
                        "family": family["family"],
                        "selected_banks": [],
                        "neighbors": [],
                        "retained_baseline": True,
                        "reason": "no bank passed inner selection in this fold",
                    }
                )
                continue
            neighbors = generate_neighbors(
                family["family"], guard, banks, attempted=attempted
            )
            families.append(
                {
                    "family": family["family"],
                    "selected_banks": [bank["candidate_id"] for bank in banks],
                    "neighbors": neighbors,
                    "retained_baseline": False,
                }
            )
            for row in neighbors:
                rows.append({**row, "outer_fold": year})
        folds.append(
            {
                "outer_fold": year,
                "inner_cutoff_day": fold.get("inner_cutoff_day"),
                "fit_cutoff_ns": guard["fit_cutoff_ns"],
                "families": families,
            }
        )
    attempted_rows = [row for row in rows if row["status"] == "attempted"]
    distinct = {}
    for row in attempted_rows:
        distinct.setdefault(_identity(row), row)
    return {
        "schema_version": REFINEMENT_BANK_SCHEMA,
        "task_id": P15_18_TASK_ID,
        "max_neighbors_per_bank": MAX_NEIGHBORS_PER_BANK,
        "max_neighbors_per_family": MAX_NEIGHBORS_PER_FAMILY,
        "neighborhoods": {key: [dict(sweep) for sweep in spec] for key, spec in NEIGHBORHOODS.items()},
        "folds": folds,
        "rows": rows,
        "counts": {
            "rows": len(rows),
            "attempted": len(attempted_rows),
            "duplicate": sum(1 for row in rows if row["status"] == "duplicate"),
            "not_applicable": sum(1 for row in rows if row["status"] == "not_applicable"),
            "distinct_candidates": len(distinct),
        },
        "distinct_candidates": sorted(
            (dict(row) for row in distinct.values()), key=lambda row: str(row["candidate_id"])
        ),
    }


def refinement_candidate_id(row: Mapping[str, Any]) -> str:
    """The executed candidate's identity: the neighbour id is already unique per
    family, branch, recipe and changed axis value."""
    return str(row["candidate_id"])


def resolve_refinement_bank(
    distinct_candidates: Sequence[Mapping[str, Any]],
    parents: Mapping[str, Any],
) -> list[Any]:
    """Turn the bank's distinct rows into ResolvedCandidates the breadth runner
    can execute: the parent's resolution with its parameters replaced."""
    from dataclasses import replace as _replace

    out = []
    for row in distinct_candidates:
        parent = parents[str(row["parent_trial_ids"][0])]
        out.append(
            _replace(
                parent,
                candidate_id=refinement_candidate_id(row),
                parameters=dict(row["parameters"]),
            )
        )
    return out


def refinement_parents(
    allowlist: Mapping[str, Any], breadth_run_root: str | Path | None = None
) -> dict[str, Any]:
    """The breadth ResolvedCandidate behind every selected bank, by candidate id.

    The universe is what the breadth evaluation decided, not the frozen bank
    alone: a supplement attempt evaluated in the same Holm family can have a
    bank selected, so its declared candidates are resolved here too.
    """
    from trading_research.research.rule_discovery import search, search_run

    resolved = {item.candidate_id: item for item in search.resolve_bank()}
    if breadth_run_root is not None:
        results = Path(breadth_run_root) / "BREADTH_RESULTS.json"
        if results.is_file():
            for supplement in json.loads(results.read_text()).get("supplements") or []:
                declaration = supplement.get("declaration")
                if not declaration or not Path(declaration).is_file():
                    continue
                document = json.loads(Path(declaration).read_text())
                for item in search_run.supplement_candidates(document):
                    resolved[item.candidate_id] = item
    out: dict[str, Any] = {}
    for fold in allowlist["folds"]:
        for family in fold["families"]:
            for bank in family.get("selected_banks") or []:
                cid = str(bank["candidate_id"])
                if cid in resolved:
                    out[cid] = resolved[cid]
    return out


def refinement_bank_identity(bank: Mapping[str, Any], allowlist_sha256: str) -> dict[str, Any]:
    body = json.dumps(bank["distinct_candidates"], sort_keys=True, default=str).encode()
    from hashlib import sha256

    return {
        "source": "P15-18 refinement bank, generated from the P15-17 allowlist",
        "allowlist_sha256": allowlist_sha256,
        "sha256": sha256(body).hexdigest(),
        "candidates": len(bank["distinct_candidates"]),
        "rows": bank["counts"]["rows"],
    }


def prepare_refinement(
    breadth_run_root: str | Path,
    *,
    allowlist_path: str | Path | None = None,
) -> dict[str, Any]:
    """The whole refinement input, as a function of the breadth run root.

    Reads the allowlist and the breadth bank, builds the neighbour bank with the
    fold guards, and resolves the distinct candidates for execution.
    """
    from datetime import date

    from trading_research.research.rule_discovery import search_run
    from trading_research.research.rule_discovery.native import account_day_window

    root = Path(breadth_run_root)
    path = Path(allowlist_path) if allowlist_path else root / "REFINEMENT_ALLOWLIST.json"
    allowlist = json.loads(path.read_text())
    cutoffs = {
        int(fold["outer_fold"]): account_day_window(date.fromisoformat(fold["inner_cutoff_day"]))[1]
        for fold in allowlist["folds"]
    }
    from trading_research.research.rule_discovery import search

    attempted = [
        {
            "family": item.family,
            "branch": item.branch,
            "recipe_id": item.recipe_id,
            "parameters": dict(item.parameters),
        }
        for item in search.resolve_bank()
    ]
    parents = refinement_parents(allowlist, root)
    # an allowlist written before select_banks carried the branch still resolves:
    # the branch comes from the parent's own resolution
    bank = build_refinement_bank(
        allowlist,
        cutoffs,
        attempted=attempted,
        branches={cid: item.branch for cid, item in parents.items()},
    )
    candidates = resolve_refinement_bank(bank["distinct_candidates"], parents)
    return {
        "allowlist_path": str(path),
        "allowlist_sha256": search_run.file_sha256(path),
        "breadth_run_root": str(root),
        "bank": bank,
        "candidates": candidates,
        "bank_identity": refinement_bank_identity(bank, search_run.file_sha256(path)),
        "inner_cutoff_ns": cutoffs,
    }


def run_refinement(
    *,
    breadth_run_root: str | Path,
    run_root: str | Path,
    freeze_path: str | Path,
    dates: Sequence[str] | None = None,
    workers: int | None = None,
    allowlist_path: str | Path | None = None,
) -> dict[str, Any]:
    """Execute the refinement bank through the breadth runner.

    Same sessions, same pairing, same E0 benchmark, same checkpoints and resume:
    only the bank differs, so a refinement run is auditable exactly like a
    breadth run and re-runs against another breadth root by pointing at it.
    """
    from trading_research.research.rule_discovery import search_run

    prepared = prepare_refinement(breadth_run_root, allowlist_path=allowlist_path)
    root = Path(run_root)
    root.mkdir(parents=True, exist_ok=True)
    search_run._write_json(root / "REFINEMENT_BANK.json", prepared["bank"])
    summary = search_run.run_dates(
        run_root=root,
        freeze_path=freeze_path,
        dates=dates,
        workers=workers,
        candidates=prepared["candidates"],
        bank_identity=prepared["bank_identity"],
    )
    return {
        "summary": summary,
        "bank_identity": prepared["bank_identity"],
        "refinement_bank": str(root / "REFINEMENT_BANK.json"),
    }


def _fold_neighbors(bank: Mapping[str, Any], year: int) -> dict[str, list[dict[str, Any]]]:
    """The attempted neighbours of one fold, by family. Fold isolation starts
    here: a neighbour proposed for another fold is not in this mapping."""
    out: dict[str, list[dict[str, Any]]] = {}
    for fold in bank["folds"]:
        if int(fold["outer_fold"]) != year:
            continue
        for family in fold["families"]:
            rows = [row for row in family["neighbors"] if row["status"] == "attempted"]
            if rows:
                out[family["family"]] = rows
    return out


def select_refined_for_fold(
    bank: Mapping[str, Any],
    fold: Mapping[str, Any],
    resolved: Mapping[str, Any],
    series: Mapping[str, Any],
) -> dict[str, Any]:
    """The refined mechanism chosen inside each selected bank of each family.

    Inner fit+tune days of THIS fold only; the same 1% simplicity rule as the
    breadth stage; a bank keeps its breadth parent when no neighbour improves.
    """
    from trading_research.research.rule_discovery import search_run

    year = int(fold["test_year"])
    families: dict[str, Any] = {}
    for family, rows in sorted(_fold_neighbors(bank, year).items()):
        by_bank: dict[str, list[dict[str, Any]]] = {}
        for row in rows:
            item = resolved.get(str(row["candidate_id"]))
            if item is None:
                continue
            inner = search_run.inner_row_from_series(item, series.get(item.candidate_id), fold)
            inner["parent_trial_ids"] = list(row.get("parent_trial_ids") or [])
            inner["changed_axis"] = row.get("changed_axis")
            by_bank.setdefault(str(row["bank"]), []).append(inner)
        chosen: list[dict[str, Any]] = []
        for bank_name, group in sorted(by_bank.items()):
            best = search_run.pick_representative(group)
            if best is None:
                continue
            inner = best.get("inner_tuning") or {}
            improvement = float(inner.get("improvement_vs_b02") or 0.0)
            supported = _inner_support_ok(inner)
            chosen.append(
                {
                    "bank": bank_name,
                    "candidate_id": best["candidate_id"],
                    "recipe_id": best["recipe_id"],
                    "parameters": dict(best.get("parameters") or {}),
                    "parent_trial_ids": list(best.get("parent_trial_ids") or []),
                    "inner_tuning": dict(inner),
                    "improvement_vs_b02": improvement,
                    "inner_support_ok": supported,
                    "beats_b02": improvement > 0 and supported,
                    "candidates_considered": len(group),
                }
            )
        families[family] = {
            "refined": chosen,
            "retained_parent": [row for row in chosen if not row["beats_b02"]],
        }
    return {"outer_fold": year, "families": families, "evidence": "inner fit+tune days of this fold only"}


def _branch_of(candidate_id: str) -> str:
    """`FAMILY:branch:RECIPE:axis=value` -- the branch is the second segment."""
    parts = str(candidate_id).split(":")
    return parts[1] if len(parts) > 1 else ""


def propose_combinations(selection: Mapping[str, Any], fold: Mapping[str, Any]) -> list[dict[str, Any]]:
    """At most one combined candidate per family per fold, and only when each of
    the two best refined mechanisms beats B0.2 on inner tuning by itself (A01)."""
    out: list[dict[str, Any]] = []
    for family, body in sorted(selection["families"].items()):
        qualifying = [row for row in body["refined"] if row["beats_b02"]]
        qualifying.sort(key=lambda row: (-float(row["improvement_vs_b02"]), str(row["candidate_id"])))
        if len(qualifying) < 2:
            continue
        first, second = qualifying[0], qualifying[1]
        if first["bank"] == second["bank"]:
            continue
        row = {
            "family": family,
            "outer_fold": int(selection["outer_fold"]),
            "ingredients": [first, second],
            "candidate_id": f"{family}:COMBINED:{first['candidate_id']}+{second['candidate_id']}",
            "status": "attempted",
            "reason": None,
        }
        # both changes must live on one branch, or there is no single scan that
        # carries them; recorded with its reason, never silently dropped
        branches = {_branch_of(first["candidate_id"]), _branch_of(second["candidate_id"])}
        if len(branches) != 1:
            row["status"] = "not_applicable"
            row["reason"] = "ingredients_on_different_branches"
        out.append(row)
    del fold
    return out


def build_combined_overrides(first: Any, second: Any, market: Any) -> dict[str, Any]:
    """Both mechanisms on one scan.

    Enumeration hooks chain (the second sees the first's payload); stage hooks
    merge by stage name and chain when both name the same stage. Nothing else is
    changed, so a combination is exactly its two ingredients.
    """
    from trading_research.research.rule_discovery import search

    left = search.build_overrides(first, market)
    right = search.build_overrides(second, market)
    merged = dict(left)
    for key, hook in right.items():
        if key not in merged:
            merged[key] = hook
            continue
        before = merged[key]
        if key == search.ENUMERATION_KEY:

            def chained(*, point, payload, _a=before, _b=hook, **ctx):
                return _b(point=point, payload=_a(point=point, payload=payload, **ctx), **ctx)

        else:

            def chained(*, stage, episode, document, _a=before, _b=hook):
                return _b(stage=_a(stage=stage, episode=episode, document=document), episode=episode, document=document)

        merged[key] = chained
    return merged


def _refinement_trial_rows(
    bank: Mapping[str, Any],
    selections: Sequence[Mapping[str, Any]],
    decided: Mapping[str, Mapping[str, Any]],
    *,
    folds: Sequence[Mapping[str, Any]],
    identity: Mapping[str, Any],
    fold_metrics: Mapping[str, Mapping[int, Any]] | None = None,
) -> list[dict[str, Any]]:
    """One ledger row per proposed neighbour per fold, plus the combinations.

    Duplicates, capped and not-applicable neighbours all keep a row: the trial
    count and the multiplicity adjustment must see every proposal (A04). The
    promotion metric is pooled over the outer blocks, so each row also carries
    that fold's own outer-block evidence under ``test_metrics.fold``.
    """
    from trading_research.research.rule_discovery import search_run

    fold_metrics = dict(fold_metrics or {})
    windows = {int(fold["test_year"]): fold for fold in folds}
    chosen: dict[int, set[str]] = {}
    for selection in selections:
        year = int(selection["outer_fold"])
        chosen[year] = {
            row["candidate_id"] for body in selection["families"].values() for row in body["refined"]
        }
    rows: list[dict[str, Any]] = []
    for fold in bank["folds"]:
        year = int(fold["outer_fold"])
        window = windows[year]
        for family in fold["families"]:
            for row in family["neighbors"]:
                cid = str(row["candidate_id"])
                verdict = decided.get(cid) if row["status"] == "attempted" else None
                if row["status"] != "attempted":
                    status, disposition = row["status"], "unsupported_owned_input"
                    reason = row.get("reason")
                    attribution = ["coverage"]
                elif verdict is None:
                    status, disposition = "attempted", "inconclusive_support"
                    reason = "not selected inside its bank by inner tuning"
                    attribution = ["support"]
                else:
                    status = "attempted"
                    disposition = verdict["promotion"]["disposition"]
                    reason = verdict["promotion"]["reason"]
                    attribution = verdict["failure_attribution"]
                rows.append(
                    make_trial_record(
                        trial_id=f"P15-18:{year}:{cid}",
                        parent_trial_ids=list(row.get("parent_trial_ids") or []),
                        family=row["family"],
                        branch=row["branch"],
                        outer_fold=year,
                        stage="refinement",
                        bank=row["bank"],
                        parameters=dict(row["parameters"]),
                        code_hash=identity["code_sha256"],
                        data_hash=identity["bank_sha256"],
                        plan_hash=identity["freeze_sha256"],
                        fit_window=[window["fit"][0], window["fit"][-1]] if window["fit"] else None,
                        tune_window=[window["tune"][0], window["tune"][-1]] if window["tune"] else None,
                        calibration_window=[window["calibrate"][0], window["calibrate"][-1]]
                        if window["calibrate"]
                        else None,
                        outcome_exposure_cutoff=window["test"][-1] if window["test"] else None,
                        candidate_population_counts={}
                        if verdict is None
                        else {
                            "candidate_entries": verdict["candidate_entries"],
                            "baseline_entries": verdict["baseline_entries"],
                            "eligible_test_days": verdict["eligible_test_days"],
                        },
                        score=None if verdict is None else verdict["mean_diff"],
                        support={}
                        if verdict is None
                        else search_run.support_block(verdict["promotion"]),
                        test_metrics={}
                        if verdict is None
                        else {
                            "scope": "pooled_outer_blocks",
                            "mean_diff": verdict["mean_diff"],
                            "p_raw": verdict["promotion"]["p_raw"],
                            "p_holm": verdict["promotion"]["p_holm"],
                            "attainable_p_floor": verdict["promotion"].get("attainable_p_floor"),
                            "family_size": verdict["promotion"].get("family_size"),
                            "ci_low": verdict["promotion"]["ci_low"],
                            "ci_high": verdict["promotion"]["ci_high"],
                            "fold": (fold_metrics.get(cid) or {}).get(year),
                        },
                        reason=reason,
                        disposition=disposition,
                        artifacts={"run_root": identity["run_root"]},
                        failure_attribution=attribution,
                        candidate_id=cid,
                        recipe_id=row["recipe_id"],
                        status=status,
                        selected_in_fold=cid in chosen.get(year, set()),
                    )
                )
    return rows


def _score_combinations(
    proposals: Sequence[Mapping[str, Any]],
    selections: Sequence[Mapping[str, Any]],
    folds: Sequence[Mapping[str, Any]],
    resolved: Mapping[str, Any],
    series: Mapping[str, Any],
) -> list[dict[str, Any]]:
    """Each combination against B0.2 and against each ingredient, on the inner
    days of its own fold, with the interaction labelled explicitly."""
    from trading_research.research.rule_discovery import search_run

    by_year = {int(fold["test_year"]): fold for fold in folds}
    rows: list[dict[str, Any]] = []
    for proposal in proposals:
        year = int(proposal["outer_fold"])
        fold = by_year[year]
        first, second = proposal["ingredients"]
        cid = str(proposal["candidate_id"])
        row = {
            "candidate_id": cid,
            "family": proposal["family"],
            "outer_fold": year,
            "status": proposal.get("status", "attempted"),
            "reason": proposal.get("reason"),
            "ingredients": [first["candidate_id"], second["candidate_id"]],
            "parent_trial_ids": [first["candidate_id"], second["candidate_id"]],
            "inner_improvement_a": float(first["improvement_vs_b02"]),
            "inner_improvement_b": float(second["improvement_vs_b02"]),
        }
        item = resolved.get(cid)
        if row["status"] == "attempted" and item is not None and series.get(cid) is not None:
            inner = search_run.inner_row_from_series(item, series.get(cid), fold)["inner_tuning"]
            combo = float(inner["improvement_vs_b02"])
            row["inner_improvement_vs_b02"] = combo
            row["inner_tuning"] = inner
            verdict = combine_candidates(
                proposal["family"],
                fold,
                {"candidate_id": first["candidate_id"], "parameters": first["parameters"], "branch": _branch_of(first["candidate_id"])},
                {"candidate_id": second["candidate_id"], "parameters": second["parameters"], "branch": _branch_of(second["candidate_id"])},
                b02_score=0.0,
                score_a=row["inner_improvement_a"],
                score_b=row["inner_improvement_b"],
                combo_score=combo,
            )
            if verdict is None:
                row["status"] = "not_applicable"
                row["reason"] = "an ingredient does not beat B0.2 on inner tuning"
            else:
                row["interaction"] = verdict["interaction"]
                row["vs_ingredient_a"] = verdict["vs_ingredient_a"]
                row["vs_ingredient_b"] = verdict["vs_ingredient_b"]
                row["vs_b02"] = verdict["vs_b02"]
        elif row["status"] == "attempted":
            row["status"] = "not_applicable"
            row["reason"] = "not executed"
        rows.append(row)
    return rows


def _combination_trial_rows(
    rows: Sequence[Mapping[str, Any]],
    decided: Mapping[str, Mapping[str, Any]],
    *,
    folds: Sequence[Mapping[str, Any]],
    identity: Mapping[str, Any],
    fold_metrics: Mapping[str, Mapping[int, Any]] | None = None,
) -> list[dict[str, Any]]:
    """A combination's ledger row carries its own paired series: its mean, its
    interval and its raw p come from the combination's own days, never from an
    ingredient (a promoted trial without its own evidence is not promoted)."""
    from trading_research.research.rule_discovery import search_run

    fold_metrics = dict(fold_metrics or {})
    windows = {int(fold["test_year"]): fold for fold in folds}
    out: list[dict[str, Any]] = []
    for row in rows:
        year = int(row["outer_fold"])
        window = windows[year]
        verdict = decided.get(row["candidate_id"])
        if row["status"] != "attempted":
            disposition, attribution = "unsupported_owned_input", ["coverage"]
        elif verdict is None:
            disposition, attribution = "inconclusive_support", ["support"]
        else:
            disposition = verdict["promotion"]["disposition"]
            attribution = verdict["failure_attribution"]
        out.append(
            make_trial_record(
                trial_id=f"P15-18:{year}:{row['candidate_id']}",
                parent_trial_ids=list(row["parent_trial_ids"]),
                family=row["family"],
                branch=_branch_of(row["ingredients"][0]),
                outer_fold=year,
                stage="refinement_combination",
                bank="COMBINED",
                parameters={"ingredients": list(row["ingredients"])},
                code_hash=identity["code_sha256"],
                data_hash=identity["bank_sha256"],
                plan_hash=identity["freeze_sha256"],
                fit_window=[window["fit"][0], window["fit"][-1]] if window["fit"] else None,
                tune_window=[window["tune"][0], window["tune"][-1]] if window["tune"] else None,
                calibration_window=[window["calibrate"][0], window["calibrate"][-1]]
                if window["calibrate"]
                else None,
                outcome_exposure_cutoff=window["test"][-1] if window["test"] else None,
                score=row.get("inner_improvement_vs_b02"),
                candidate_population_counts={}
                if verdict is None
                else {
                    "candidate_entries": verdict["candidate_entries"],
                    "baseline_entries": verdict["baseline_entries"],
                    "eligible_test_days": verdict["eligible_test_days"],
                },
                support={} if verdict is None else search_run.support_block(verdict["promotion"]),
                test_metrics={}
                if verdict is None
                else {
                    "scope": "pooled_outer_blocks",
                    "mean_diff": verdict["mean_diff"],
                    "p_raw": verdict["promotion"]["p_raw"],
                    "p_holm": verdict["promotion"]["p_holm"],
                    "attainable_p_floor": verdict["promotion"].get("attainable_p_floor"),
                    "family_size": verdict["promotion"].get("family_size"),
                    "ci_low": verdict["promotion"]["ci_low"],
                    "ci_high": verdict["promotion"]["ci_high"],
                    "fold": (fold_metrics.get(row["candidate_id"]) or {}).get(year),
                    "interaction": row.get("interaction"),
                    "vs_ingredient_a": row.get("vs_ingredient_a"),
                    "vs_ingredient_b": row.get("vs_ingredient_b"),
                },
                reason=row.get("reason") or (None if verdict is None else verdict["promotion"]["reason"]),
                disposition=disposition,
                artifacts={"run_root": identity["run_root"]},
                failure_attribution=attribution,
                candidate_id=row["candidate_id"],
                recipe_id="COMBINED",
                status=row["status"],
            )
        )
    return out


def evaluate_refinement(
    *,
    run_root: str | Path,
    breadth_run_root: str | Path,
    freeze_path: str | Path,
    out_dir: str | Path | None = None,
    combination_run_root: str | Path | None = None,
    holdout: tuple[str, str] | None = None,
) -> dict[str, Any]:
    """The refinement evaluation, streaming, as a function of the run roots.

    The blind hold-out is removed from every fold window before anything is
    scored, so no hold-out date reaches a neighbourhood, a combination choice,
    the Holm family or the all-history recommendation.
    """
    from trading_research.research.rule_discovery import search_run

    root = Path(run_root)
    out = Path(out_dir) if out_dir else root
    out.mkdir(parents=True, exist_ok=True)
    freeze = search_run.load_freeze(freeze_path)
    folds, holdout_excluded = search_run.apply_holdout(search_run.load_splits(freeze), holdout)
    bank = json.loads((root / "REFINEMENT_BANK.json").read_text())
    prepared = prepare_refinement(breadth_run_root)
    resolved = {item.candidate_id: item for item in prepared["candidates"]}
    series, coverage = search_run.stream_run(root)
    if combination_run_root is not None:
        extra, extra_coverage = search_run.stream_run(combination_run_root)
        series = {**series, **extra}
        coverage = {"neighbors": coverage, "combinations": extra_coverage}

    selections = [select_refined_for_fold(bank, fold, resolved, series) for fold in folds]
    combinations = [row for selection in selections for row in propose_combinations(selection, None)]

    combined_candidates, _parts = resolve_combinations(combinations, resolved)
    resolved = {**resolved, **{item.candidate_id: item for item in combined_candidates}}
    combination_rows = _score_combinations(combinations, selections, folds, resolved, series)
    outer_ids = sorted(
        {row["candidate_id"] for s in selections for b in s["families"].values() for row in b["refined"]}
        | {row["candidate_id"] for row in combination_rows if row["status"] == "attempted"}
    )
    outer = [
        search_run.outer_row_from_series(resolved[cid], series.get(cid), folds)
        for cid in outer_ids
        if cid in resolved
    ]
    decided = {row["candidate_id"]: row for row in search_run.decide(outer)}
    fold_metrics = {
        cid: search_run.fold_metrics_from_series(resolved[cid], series.get(cid), folds)
        for cid in outer_ids
        if cid in resolved
    }

    manifest = json.loads((root / "MANIFEST.json").read_text())
    identity = {
        "code_sha256": manifest["code_sha256"],
        "bank_sha256": manifest["bank_sha256"],
        "freeze_sha256": manifest["freeze_sha256"],
        "run_root": str(root),
    }
    ledger_path = out / "TRIALS.jsonl"
    if ledger_path.exists():
        ledger_path.unlink()
    ledger = TrialLedger(ledger_path)
    for record in _refinement_trial_rows(
        bank, selections, decided, folds=folds, identity=identity, fold_metrics=fold_metrics
    ):
        record["holdout_excluded"] = holdout_excluded
        ledger.append(record)
    for record in _combination_trial_rows(
        combination_rows, decided, folds=folds, identity=identity, fold_metrics=fold_metrics
    ):
        record["holdout_excluded"] = holdout_excluded
        ledger.append(record)

    fold_roles = []
    for selection in selections:
        year = int(selection["outer_fold"])
        roles = []
        for family, body in sorted(selection["families"].items()):
            for row in body["refined"]:
                verdict = decided.get(row["candidate_id"])
                roles.append(
                    {
                        "family": family,
                        "bank": row["bank"],
                        "candidate_id": row["candidate_id"],
                        "parameters": row["parameters"],
                        "parent_trial_ids": row["parent_trial_ids"],
                        "role": "refined_selected" if row["beats_b02"] else "retained_parent",
                        "inner_improvement_vs_b02": row["improvement_vs_b02"],
                        "disposition": None if verdict is None else verdict["promotion"]["disposition"],
                        "promoted": bool(verdict and verdict["promotion"]["promoted"]),
                    }
                )
        fold_roles.append(
            {
                "outer_fold": year,
                "selection_manifest_id": f"P15-18:{year}",
                "evidence_cutoff_day": bank["folds"][0].get("inner_cutoff_day"),
                "roles": roles,
                "combinations": [row["candidate_id"] for row in combinations if row["outer_fold"] == year],
            }
        )
    promoted = [cid for cid, row in decided.items() if row["promotion"]["promoted"]]
    descriptive = None
    if promoted:
        best = max((decided[cid] for cid in promoted), key=lambda row: row["mean_diff"])
        descriptive = {
            "candidate_id": best["candidate_id"],
            "mean_diff": best["mean_diff"],
            "label": "all-history descriptive recommendation; never applied backward to an earlier fold",
        }
    manifest_rules = selected_rules_by_fold(fold_roles, descriptive)
    manifest_rules["holdout_excluded"] = holdout_excluded
    search_run._write_json(out / "SELECTED_RULES_BY_FOLD.json", manifest_rules)

    disposition_rows = []
    for family in sorted({row["family"] for fold in bank["folds"] for f in fold["families"] for row in f["neighbors"]}):
        family_rows = [decided[cid] for cid in decided if decided[cid]["family"] == family]
        if not family_rows:
            disposition_rows.append(
                {"family": family, "status": "active_baseline", "candidate_id": None, "failure_attribution": []}
            )
            continue
        best = max(family_rows, key=lambda row: row["mean_diff"])
        disposition_rows.append(
            {
                "family": family,
                "status": "active_selected" if best["promotion"]["promoted"] else "active_baseline",
                "candidate_id": best["candidate_id"],
                "failure_attribution": best["failure_attribution"],
            }
        )
    dispositions = family_dispositions(disposition_rows)
    dispositions["stage"] = "refinement"
    dispositions["holdout_excluded"] = holdout_excluded
    dispositions["coverage"] = coverage
    dispositions["multiplicity"] = search_run._multiplicity_block(list(decided.values()))
    search_run._write_json(out / "FAMILY_DISPOSITIONS.json", dispositions)

    reports = out / "FAMILY_REPORTS"
    reports.mkdir(parents=True, exist_ok=True)
    retention = [
        {
            "candidate_id": row["candidate_id"],
            "family": row["family"],
            "branch": row["branch"],
            "bank": row["bank"],
            "status": "active_selected" if row["promotion"]["promoted"] else "inactive_retained",
            "first_attribution": (row["failure_attribution"] or [None])[0],
            "reason": row["promotion"]["reason"],
        }
        for row in decided.values()
    ]
    for family in sorted({row["family"] for row in decided.values()}):
        body = search_run.family_report(
            family,
            list(decided.values()),
            retention,
            [
                {
                    "outer_fold": s["outer_fold"],
                    "families": {
                        fam: {
                            "selected_banks": [
                                {"bank": r["bank"], "candidate_id": r["candidate_id"]}
                                for r in b["refined"]
                                if r["beats_b02"]
                            ],
                            "retained_baseline": not any(r["beats_b02"] for r in b["refined"]),
                        }
                        for fam, b in s["families"].items()
                    },
                }
                for s in selections
            ],
            run_root=str(root),
            report_path=str(reports / f"{family}.md"),
            title="P15-18 refinement",
            results_file="SELECTED_RULES_BY_FOLD.json and COMBINATION_RESULTS.json",
        )
        (reports / f"{family}.md").write_text(body)

    search_run._write_json(out / "COMBINATION_RESULTS.json", {
        "schema_version": "research-p15-18-combination-results-v1",
        "task_id": P15_18_TASK_ID,
        "holdout_excluded": holdout_excluded,
        "rows": combination_rows,
    })
    return {
        "coverage": coverage,
        "holdout_excluded": holdout_excluded,
        "selections": selections,
        "combinations": combination_rows,
        "trials": sum(1 for line in ledger_path.read_text().splitlines() if line.strip()),
        "promoted": promoted,
        "family_reports": sorted(path.name for path in reports.glob("*.md")),
    }


from hashlib import sha256


def resolve_combinations(
    combinations: Sequence[Mapping[str, Any]],
    resolved: Mapping[str, Any],
) -> tuple[list[Any], dict[str, tuple[Any, Any]]]:
    """The distinct executable combined candidates and their two ingredients.

    A combined candidate is the first ingredient's resolution carrying both
    parameter sets; `build_combined_overrides` installs both mechanisms.
    """
    from dataclasses import replace as _replace

    out: dict[str, Any] = {}
    parts: dict[str, tuple[Any, Any]] = {}
    for row in combinations:
        if row.get("status") != "attempted":
            continue
        first = resolved.get(row["ingredients"][0]["candidate_id"])
        second = resolved.get(row["ingredients"][1]["candidate_id"])
        if first is None or second is None:
            continue
        cid = str(row["candidate_id"])
        if cid in out:
            continue
        parameters = dict(first.parameters)
        parameters.update(dict(second.parameters))
        out[cid] = _replace(first, candidate_id=cid, parameters=parameters)
        parts[cid] = (first, second)
    return [out[key] for key in sorted(out)], parts


def run_combinations(
    *,
    breadth_run_root: str | Path,
    refinement_run_root: str | Path,
    run_root: str | Path,
    freeze_path: str | Path,
    dates: Sequence[str] | None = None,
    workers: int | None = None,
    holdout: tuple[str, str] | None = None,
) -> dict[str, Any]:
    """Execute the combined candidates chosen by the refinement evaluation."""
    from trading_research.research.rule_discovery import search_run

    prepared = prepare_refinement(breadth_run_root)
    resolved = {item.candidate_id: item for item in prepared["candidates"]}
    bank = json.loads((Path(refinement_run_root) / "REFINEMENT_BANK.json").read_text())
    freeze = search_run.load_freeze(freeze_path)
    # the same trimmed folds the evaluation uses: a combination chosen on a
    # hold-out date would be a hold-out-influenced choice
    folds, _holdout_excluded = search_run.apply_holdout(search_run.load_splits(freeze), holdout)
    series, _ = search_run.stream_run(Path(refinement_run_root))
    proposals: list[dict[str, Any]] = []
    for fold in folds:
        selection = select_refined_for_fold(bank, fold, resolved, series)
        proposals.extend(propose_combinations(selection, None))
    candidates, parts = resolve_combinations(proposals, resolved)
    root = Path(run_root)
    root.mkdir(parents=True, exist_ok=True)
    search_run._write_json(
        root / "COMBINATIONS.json",
        {
            "schema_version": "research-p15-18-combinations-v1",
            "task_id": P15_18_TASK_ID,
            "proposals": proposals,
            "executed": [item.candidate_id for item in candidates],
            "not_applicable": [
                {"candidate_id": row["candidate_id"], "reason": row["reason"]}
                for row in proposals
                if row.get("status") != "attempted"
            ],
        },
    )
    if not candidates:
        # nothing qualified: there is no session to load, and a run over 1,742
        # dates with an empty bank would burn the budget to write nothing
        return {
            "summary": {
                "task_id": P15_18_TASK_ID,
                "run_root": str(root),
                "dates_declared": 0,
                "executed": 0,
                "reason": "no combination qualified in any fold",
            },
            "executed": [],
        }
    summary = search_run.run_dates(
        run_root=root,
        freeze_path=freeze_path,
        dates=dates,
        workers=workers,
        candidates=candidates,
        combinations=parts,
        bank_identity={
            "source": "P15-18 combined candidates",
            "sha256": sha256(
                json.dumps(sorted(item.candidate_id for item in candidates)).encode()
            ).hexdigest(),
            "candidates": len(candidates),
            "refinement_run_root": str(refinement_run_root),
        },
    )
    return {"summary": summary, "executed": [item.candidate_id for item in candidates]}
