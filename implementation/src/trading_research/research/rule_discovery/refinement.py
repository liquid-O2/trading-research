"""Bounded refinement neighborhoods, promotion gates and trial ledger."""

from __future__ import annotations

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
    holm,
    moving_block_bootstrap,
)

MINUTE_NS = 60_000_000_000
MAX_NEIGHBORS_PER_BANK = 12
MAX_NEIGHBORS_PER_FAMILY = 24
MAX_REFINED_PLUS_COMBINED = 25
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
_P = (
    {"axis": "bandwidth", "values": (0, 2, 4), "freeze": {"prominence": 0.20}},
    {"axis": "prominence", "values": (0.10, 0.20, 0.30), "parent_axis": "bandwidth"},
)
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
            "parameters": dict(row.get("parameters") or {}),
            "changed_axes": changed_axes(row),
            "inner_tuning": dict(row.get("inner_tuning") or {}),
        }
        for row in chosen
    ]


def _valid_diffs(daily_diff: Sequence[Any]) -> list[float]:
    return [float(value) for value in daily_diff if value is not None]


def centered_bootstrap_pvalue(
    daily_diff: Sequence[Any],
    *,
    bootstrap_fn: Callable[..., Any] = moving_block_bootstrap,
) -> dict[str, Any]:
    valid = _valid_diffs(daily_diff)
    mean_diff = float(np.mean(valid)) if valid else 0.0
    draws = bootstrap_fn(valid, block=BLOCK_LENGTH, draws=BOOTSTRAP_DRAWS, seed=BOOTSTRAP_SEED)
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
    return {
        "p_raw": float(p_raw),
        "mean_diff": mean_diff,
        "ci_low": ci_low,
        "ci_high": ci_high,
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
    computed = centered_bootstrap_pvalue(candidate.get("daily_diff") or (), bootstrap_fn=bootstrap_fn)
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

    opportunities = int(candidate.get("resolved_opportunities") or 0)
    days = int(candidate.get("eligible_test_days") or 0)
    blocks = int(candidate.get("supported_outer_blocks") or 0)
    support_ok = _support_pass(opportunities, days, blocks)
    sensitivity = support_sensitivity(opportunities, days, blocks)

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

    if promoted:
        disposition = "promoted"
        reason = None
    elif not support_ok:
        disposition = "inconclusive_support"
        reason = "support"
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
        "support_pass": support_ok,
        "support_sensitivity": sensitivity,
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
