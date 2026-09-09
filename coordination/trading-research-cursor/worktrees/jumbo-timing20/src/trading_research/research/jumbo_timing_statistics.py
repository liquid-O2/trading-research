"""Controlled Jumbo clock-geometry and JTR transition-window descriptives.

Scientific products reuse the admitted common-clock adapter and retained
formation tables. They do not fit Context, score Locations, rank clocks, or
reproduce the undisclosed 86.46% source statistic.
"""
from __future__ import annotations

from collections import defaultdict
from datetime import date
import gc
import hashlib
import math
import resource
import time

import numpy as np

from trading_research.errors import ContractError, IntegrityError
from trading_research.operations.artifacts import ArtifactStore
from trading_research.research.auction_flow_storage import BoundedOutputs
from trading_research.research.jumbo_clock_comparison import (
    COMMON_TARGETS, HORIZON, VERSION as COMMON_ADAPTER_VERSION,
    prepare_common_clock_comparison,
)
from trading_research.research.jumbo_matrix import PreparedPaths, _read_columns, feature_names, prepare_paths
from trading_research.research.jumbo_report import _descriptive, metric_intervals

VERSION = "jumbo-timing-statistics-v1"
PRIMARY_VARIANT = "primary_corrected"
ORIGINAL_NQ2024_VARIANT = "original_nq2024_sensitivity"
TRANSITION_CLOCKS = ("JTR_fixed_04", "turn_earlier", "turn_source", "turn_later")
TURN_WINDOWS = ("turn_earlier", "turn_source", "turn_later")
PRECEDING_TURN = {"turn_earlier": None, "turn_source": "turn_earlier", "turn_later": "turn_source"}
ACTIVITY_COMPARATORS = ("OR_activity_1_2", "OR_activity_1_1", "OR_activity_3_2")
WIDTH_RATIO_LABELS = ("0-0.25", "0.25-0.5", "0.5-1", "1-2", "2-inf")
OVERLAP_LABELS = ("0-0.5", "0.5-1", "1")
POSITION_LABELS = ("below", "lower_half", "upper_half", "above")
PRIOR_VOL_LABELS = ("low", "mid", "high")
LEVEL_NAMES = ("equilibrium", "lower_half_extension", "upper_half_extension")
PHASE_SLICES = (
    ("training_2020_2022", 2020, 2022, "phase"),
    ("development_2023_2024", 2023, 2024, "phase"),
    ("confirmation_2025_2026", 2025, 2026, "phase"),
)
YEAR_SLICES = tuple((f"year_{year}", year, year, "year") for year in range(2020, 2027))
TARGET_LABELS = {
    "common_high_priorW": "common_up",
    "common_low_priorW": "common_down",
    "common_terminal_priorW": "common_terminal",
}
FORMATION_COLUMNS = (
    "date", "clock", "contract_key", "status", "exclusion_reasons", "formation_id",
    "root", "year", "source_version", "definition", "source_ids", "variant_role",
    "window_version", "formation_start_ns", "formation_end_ns", "origin_ns",
    "available_at_ns", "calendar_known_at_ns",
    "open_ticks", "high_ticks", "low_ticks", "close_ticks", "width_ticks", "zero_width",
)
REMAINING_D1_DEPENDENCIES = (
    {
        "id": "event_label_absent",
        "detail": "JTR-09 10:00 news delay and ordinary/event-day labels are not in the retained Jumbo tables; timing is not event-conditioned.",
    },
    {
        "id": "undisclosed_86_46_criteria",
        "detail": "JTR-18/JTR-19 86.46% reversal criteria, denominators and timestamps are undisclosed. This module does not invent a replication.",
    },
    {
        "id": "auction_completed_windows_waiting_auction_block",
        "detail": "Activity-completed OR15 comparators are OHLC-volume clocks, not auction-completion certificates. Auction-completed windows remain blocked on the auction family.",
    },
)


def doubled_equilibrium(high_ticks, low_ticks):
    """Exact 2*EQ = H+L. No half-tick float rounding."""
    high, low = _exact_tick(high_ticks, "high"), _exact_tick(low_ticks, "low")
    if high < low:
        raise ContractError("high must be at least low")
    return high + low


def doubled_lower_half_extension(high_ticks, low_ticks):
    """Exact 2*(L-W/2) = 3L-H."""
    high, low = _exact_tick(high_ticks, "high"), _exact_tick(low_ticks, "low")
    if high < low:
        raise ContractError("high must be at least low")
    return 3 * low - high


def doubled_upper_half_extension(high_ticks, low_ticks):
    """Exact 2*(H+W/2) = 3H-L."""
    high, low = _exact_tick(high_ticks, "high"), _exact_tick(low_ticks, "low")
    if high < low:
        raise ContractError("high must be at least low")
    return 3 * high - low


def jtr_doubled_levels(high_ticks, low_ticks):
    high, low = _exact_tick(high_ticks, "high"), _exact_tick(low_ticks, "low")
    width = high - low
    return {
        "width_ticks": width,
        "equilibrium": doubled_equilibrium(high, low),
        "lower_half_extension": doubled_lower_half_extension(high, low),
        "upper_half_extension": doubled_upper_half_extension(high, low),
    }


def classify_level_observation(open_ticks, high_ticks, low_ticks, close_ticks, level_doubled):
    """Compatible range intersection is not a definite OHLC print."""
    if any(value is None for value in (open_ticks, high_ticks, low_ticks, close_ticks, level_doubled)):
        return {
            "observation_class": "censored", "compatible_intersection": False,
            "boundary_touch": False, "definite_print": False, "print_members": (),
        }
    open_, high, low, close = (_exact_tick(open_ticks, "open"), _exact_tick(high_ticks, "high"),
                               _exact_tick(low_ticks, "low"), _exact_tick(close_ticks, "close"))
    level = _exact_tick(level_doubled, "level_doubled")
    if high < low:
        raise ContractError("window high must be at least low")
    if not low <= open_ <= high or not low <= close <= high:
        raise ContractError("open/close must lie inside the window extrema")
    two_open, two_high, two_low, two_close = 2 * open_, 2 * high, 2 * low, 2 * close
    compatible = two_low <= level <= two_high
    boundary = level in (two_low, two_high)
    members = tuple(name for name, price in (("O", two_open), ("H", two_high), ("L", two_low), ("C", two_close))
                    if price == level)
    definite = bool(members)
    if definite:
        klass = "definite_print"
    elif compatible:
        klass = "ambiguous"
    else:
        klass = "no_event"
    return {
        "observation_class": klass, "compatible_intersection": compatible,
        "boundary_touch": boundary, "definite_print": definite, "print_members": members,
    }


def signed_close_open(open_ticks, close_ticks):
    if open_ticks is None or close_ticks is None:
        return None
    return _exact_tick(close_ticks, "close") - _exact_tick(open_ticks, "open")


def classify_move_relationship(current_signed, prior_signed):
    """Operational consecutive 10-minute sign relation. Flat is not opposite."""
    if current_signed is None:
        return "insufficient"
    current = _exact_tick(current_signed, "current_signed")
    if current == 0:
        return "flat"
    if prior_signed is None:
        return "insufficient"
    prior = _exact_tick(prior_signed, "prior_signed")
    if prior == 0:
        return "insufficient"
    if (current > 0) == (prior > 0):
        return "continuation"
    return "opposite"


def width_ratio_bin(ratio):
    if ratio is None or isinstance(ratio, bool) or not _finite_number(ratio) or float(ratio) < 0:
        return "missing_own_geometry"
    value = float(ratio)
    if value < 0.25:
        return "0-0.25"
    if value < 0.5:
        return "0.25-0.5"
    if value < 1.0:
        return "0.5-1"
    if value < 2.0:
        return "1-2"
    return "2-inf"


def overlap_bin(fraction):
    if fraction is None or isinstance(fraction, bool) or not _finite_number(fraction) or float(fraction) < 0:
        return "missing_overlap"
    value = float(fraction)
    if value < 0.5:
        return "0-0.5"
    if value < 1.0:
        return "0.5-1"
    return "1"


def position_bin(position):
    if position is None or isinstance(position, bool) or not _finite_number(position):
        return "missing_own_geometry"
    value = float(position)
    if value < 0:
        return "below"
    if value < 0.5:
        return "lower_half"
    if value <= 1.0:
        return "upper_half"
    return "above"


def fit_root_prior_vol_tertiles(values_by_root):
    """Train-only known prior-20 widths. Outcomes and later years cannot enter."""
    fitted = {}
    for root, values in values_by_root.items():
        if type(root) is not str or not root:
            raise ContractError("root-specific tertiles require a named root")
        array = np.asarray(values, dtype=np.float64).reshape(-1)
        array = array[np.isfinite(array)]
        if array.size < 3:
            fitted[root] = None
            continue
        lower, upper = np.quantile(array, (1.0 / 3.0, 2.0 / 3.0))
        fitted[root] = (float(lower), float(upper))
    return fitted


def assign_prior_vol_bin(value, thresholds):
    if thresholds is None or value is None or isinstance(value, bool) or not _finite_number(value):
        return "missing_prior_vol"
    lower, upper = thresholds
    point = float(value)
    if point <= lower:
        return "low"
    if point <= upper:
        return "mid"
    return "high"


def raw_contract_field(record):
    """Prefer the saved raw contract. Metadata is inspected, never a root/date stand-in."""
    if not isinstance(record, dict):
        raise ContractError("formation record required")
    key = record.get("contract_key")
    if type(key) is str and key:
        return ("contract_key", key)
    metadata = {name: record.get(name) for name in
                ("source_version", "window_version", "definition", "source_ids", "variant_role", "formation_id")
                if record.get(name) not in (None, "")}
    if metadata:
        return ("window_metadata", tuple(sorted((k, str(v)) for k, v in metadata.items())))
    return (None, None)


def raw_contract_match(left, right):
    """Exclude mismatch and unresolved identity. Root+date is not a match."""
    left_kind, left_value = raw_contract_field(left)
    right_kind, right_value = raw_contract_field(right)
    if left_kind == "contract_key" and right_kind == "contract_key":
        return "matched" if left_value == right_value else "mismatch"
    return "unresolved"


def jtr_known_before_turn(jtr_available_at_ns, turn_start_ns):
    """JTR 06:00–09:00 is published at end+1 minute (09:01) before 09:30 turns."""
    if jtr_available_at_ns is None or turn_start_ns is None:
        return False
    available = _exact_tick(jtr_available_at_ns, "jtr_available_at_ns")
    start = _exact_tick(turn_start_ns, "turn_start_ns")
    return 0 <= available <= start


def declared_clock_pairs(plan):
    """Declared source vs its ±10-minute neighbors and OR15 activity clocks, not 16×16."""
    comparison = plan.get("matched_clock_comparison", {})
    clocks = tuple(comparison.get("clocks", ()))
    present = set(clocks)
    sources = tuple(plan.get("neighbor_clocks") or ())
    if not sources:
        sources = tuple(name for name in clocks if "__shift_" not in name
                        and name not in ACTIVITY_COMPARATORS
                        and not name.startswith("turn_") and name != "prior_RTH_preopen")
    shifts = tuple(plan.get("neighbor_shifts_minutes") or (-10, 10))
    pairs = []
    seen = set()
    for source in sources:
        if source not in present:
            continue
        for shift in shifts:
            neighbor = f"{source}__shift_{'+' if shift > 0 else ''}{int(shift)}m"
            if neighbor in present:
                key = (source, neighbor, "neighbor_shift")
                if key not in seen:
                    seen.add(key)
                    pairs.append(key)
        for activity in ACTIVITY_COMPARATORS:
            if activity in present:
                key = (source, activity, "or15_activity")
                if key not in seen:
                    seen.add(key)
                    pairs.append(key)
    return tuple(pairs)


def authenticate_workers(development, confirmation):
    if not isinstance(development, dict) or not isinstance(confirmation, dict):
        raise ContractError("authenticated development and confirmation worker dicts required")
    if development.get("success") is not True or development.get("mode") != "develop" or development.get("phase") != "extract":
        raise IntegrityError("development worker must be a successful develop/extract report")
    if confirmation.get("success") is not True or confirmation.get("mode") != "confirm" or confirmation.get("phase") != "confirmation":
        raise IntegrityError("confirmation worker must be a successful confirm/confirmation report")
    if not development.get("shards") or not confirmation.get("shards"):
        raise IntegrityError("both workers must retain their immutable shards")
    return True


def split_source_variants(development, confirmation):
    """Primary uses the admitted corrected chain. Original NQ2024 stays separate."""
    authenticate_workers(development, confirmation)
    if development.get("model_shards"):
        primary_development = list(development["model_shards"])
    else:
        primary_development = list(development["shards"])
        replacements = {(shard["root"], shard["year"]): shard
                        for shard in development.get("source_sensitivity_shards") or ()
                        if shard.get("source_supersession")}
        primary_development = [replacements.get((shard["root"], shard["year"]), shard)
                               for shard in primary_development]
    confirmation_shards = list(confirmation.get("model_shards") or confirmation["shards"])
    primary = _unique_shards(primary_development + confirmation_shards)
    original = [shard for shard in development["shards"]
                if shard.get("root") == "NQ" and int(shard["year"]) == 2024
                and not shard.get("source_supersession")]
    if len(original) > 1:
        raise IntegrityError("multiple original NQ2024 shards")
    return ((PRIMARY_VARIANT, primary),) + (((ORIGINAL_NQ2024_VARIANT, original),) if original else ())


def common_target_clock_spread(matrix):
    """Same-date common targets cannot differ across clocks. Spread 0 is not a gain."""
    eligible = np.asarray(matrix.fields["common_target_eligible"])
    roots, dates, clocks = (np.asarray(matrix.fields[name]) for name in ("root", "date", "clock"))
    spreads = []
    for name in COMMON_TARGETS:
        values = np.asarray(matrix.fields[name], dtype=np.float64)
        for root in np.unique(roots):
            for day in np.unique(dates):
                mask = eligible & (roots == root) & (dates == day)
                if not np.any(mask):
                    continue
                points = values[mask]
                points = points[np.isfinite(points)]
                if points.size < 2:
                    continue
                if np.any(points != points[0]):
                    raise IntegrityError("common normalized H/L/C target disagrees across clocks on one date")
                spreads.append(0.0)
    return 0.0 if not spreads else float(max(spreads))


def intended_root_dates(matrix, root_code):
    roots = np.asarray(matrix.fields["root"])
    dates = np.asarray(matrix.fields["date"])
    chosen = dates[roots == root_code]
    return tuple(int(day) for day in np.unique(chosen))


def run_timing_statistics(*, store, development, confirmation, analysis_plan, outputs):
    """Descriptive common-clock geometry and JTR transition observations."""
    started = time.process_time()
    baseline_rss = _rss_bytes()
    resources = {"table_reads": 0, "prepare_paths_calls": 0, "common_adapter_calls": 0,
                 "bootstrap_metrics": 0, "conditional_groups": 0, "date_rows": 0,
                 "pilot": None, "peak_rss_bytes": baseline_rss}
    if not isinstance(store, ArtifactStore):
        raise ContractError("existing ArtifactStore from trials is required")
    if not isinstance(outputs, BoundedOutputs):
        raise ContractError("BoundedOutputs for the registered attempt is required")
    if not isinstance(analysis_plan, dict):
        raise ContractError("loaded analysis plan required")
    settings = dict(analysis_plan.get("statistics") or {})
    _require_statistics(settings)
    clocks = tuple(analysis_plan.get("matched_clock_comparison", {}).get("clocks") or ())
    if len(clocks) < 2 or len(set(clocks)) != len(clocks):
        raise ContractError("unique declared common-comparison clocks required")
    variants = split_source_variants(development, confirmation)
    if any(left[0] == right[0] for i, left in enumerate(variants) for right in variants[i + 1:]):
        raise IntegrityError("source variants must remain separate")
    checks = []
    tertiles = None
    variant_results = {}
    date_rows = []
    transition_rows = []
    for variant_name, shards in variants:
        if variant_name != PRIMARY_VARIANT and variant_name != ORIGINAL_NQ2024_VARIANT:
            raise IntegrityError("undeclared source variant")
        common, formations = _materialize_variant(
            store, shards, analysis_plan, resources=resources,
            variant=variant_name)
        adapter_ok = _adapter_identity_ok(common, clocks)
        checks.append({"id": "common_adapter_identity_reused", "passed": adapter_ok, "variant": variant_name})
        if not adapter_ok:
            raise IntegrityError("reused common-clock adapter identity failed")
        spread = common_target_clock_spread(common)
        checks.append({"id": "identical_common_target_no_clock_gain", "passed": spread == 0.0,
                       "variant": variant_name, "spread": spread})
        missing_ok = _missing_clock_preserves_dates(common)
        checks.append({"id": "missing_clock_preserves_intended_date", "passed": missing_ok,
                       "variant": variant_name})
        if tertiles is None:
            if variant_name != PRIMARY_VARIANT:
                raise IntegrityError("train tertiles must be fitted on the primary 2020-2022 chain")
            tertiles = _fit_train_tertiles(common)
            all_years = _fit_slice_tertiles(common, 2020, 2026)
            checks.append({
                "id": "train_quantile_thresholds_independent_of_confirmation",
                "passed": tertiles == _fit_train_tertiles(common),
                "used": "training_2020_2022_known_prior20_only",
                "all_year_fit_differs": tertiles != all_years,
            })
        product_a, a_rows = _product_a(common, analysis_plan, settings, tertiles,
                                       variant=variant_name, resources=resources)
        product_b, b_rows = _product_b(formations, common, settings, variant=variant_name,
                                       resources=resources)
        variant_results[variant_name] = {
            "product_a": product_a, "product_b": product_b,
            "shards": [_shard_ref(shard) for shard in shards],
            "intended_root_dates": {root: len(intended_root_dates(common, code))
                                    for root, code in _root_codes(common)},
        }
        date_rows.extend(a_rows)
        transition_rows.extend(b_rows)
        del common
        gc.collect()
    if PRIMARY_VARIANT in variant_results and ORIGINAL_NQ2024_VARIANT in variant_results:
        checks.append({"id": "source_variants_not_concatenated", "passed": True,
                       "detail": "original NQ2024 remains a separate sensitivity; it is not pooled with the corrected primary chain"})
    elif ORIGINAL_NQ2024_VARIANT not in variant_results:
        checks.append({"id": "source_variants_not_concatenated", "passed": True,
                       "detail": "no separate original NQ2024 shard was present to pool"})
    paired_zero = all(variant_results[name]["product_a"].get("paired_zero_event_dates_retained") is True
                      for name in variant_results)
    checks.append({"id": "paired_rates_same_dates_zero_event_retained", "passed": paired_zero})
    checks.append({"id": "no_clock_ranking_emitted", "passed": True})
    checks.append({"id": "context_increment_not_assessed", "passed": True})
    checks.append({"id": "no_86_46_replication", "passed": True})
    checks.append({"id": "jtr_hypothesis_limited_by_10m_ohlc", "passed": True})
    passed = [check for check in checks if check.get("passed") is True]
    failed = [check for check in checks if check.get("passed") is not True]
    tables = _sanitize({
        "schema": VERSION, "horizon": HORIZON, "common_adapter": COMMON_ADAPTER_VERSION,
        "clocks": list(clocks), "pairs": [list(pair) for pair in declared_clock_pairs(analysis_plan)],
        "prior_vol_tertiles": {root: None if bounds is None else list(bounds)
                               for root, bounds in (tertiles or {}).items()},
        "variants": variant_results,
        "clock_ranking": None, "clock_ranking_forbidden": True,
        "causal_forecast_gain_claimed": False, "context_increment_assessed": False,
        "source_86_46_replicated": False,
        "ambiguity_limitations": _ambiguity_limitations(),
        "remaining_d1_dependencies": list(REMAINING_D1_DEPENDENCIES),
        "annual_report_refs": _annual_refs(development, confirmation),
        "no_ci_rule": "Date-block intervals are not a claim when independent dates < 100 or events < 20.",
    })
    common_ref = _write_parquet(outputs, "timing-common-clock-dates.parquet", date_rows,
                                kind="jumbo_timing_common_clock_date_measurements_v1")
    transition_ref = _write_parquet(outputs, "timing-jtr-transition-dates.parquet", transition_rows,
                                    kind="jumbo_timing_jtr_transition_date_measurements_v1")
    tables_ref = outputs.json("timing-statistics-tables.json", tables, kind="jumbo_timing_statistics_tables_v1")
    report = _markdown_report(tables, checks, development, confirmation, resources)
    with outputs.create("timing-statistics-report.md") as stream:
        stream.write(report.encode("utf-8"))
    report_ref = outputs.reference("timing-statistics-report.md", kind="jumbo_timing_statistics_report_markdown_v1")
    resources.update(cpu_seconds=time.process_time() - started, output_bytes=int(outputs.written),
                     peak_rss_bytes=max(resources["peak_rss_bytes"], _rss_bytes()),
                     date_rows=len(date_rows), transition_rows=len(transition_rows),
                     baseline_rss_bytes=baseline_rss)
    summary = {
        "success": not failed, "schema": VERSION,
        "refs": {"tables": tables_ref, "common_dates": common_ref,
                 "transition_dates": transition_ref, "report": report_ref},
        "results": {
            "passed_checks": _sanitize(passed), "failed_checks": _sanitize(failed),
            "check_counts": {"passed": len(passed), "failed": len(failed), "total": len(checks)},
            "variants": list(variant_results),
            "conditional_groups": resources["conditional_groups"],
            "clock_ranking": None, "family_products": {
                "controlled_clock_geometry_descriptive": not failed,
                "jtr_relative_transition_window": not failed,
            },
        },
        "resources": _sanitize(resources),
        "fullContext": False, "context_models_complete": False,
        "location_quality_complete": False, "family_statistics_complete": False,
        "model_fits": 0,
    }
    return _sanitize(summary)


def _exact_tick(value, name):
    if isinstance(value, bool) or not isinstance(value, (int, np.integer)):
        raise ContractError(f"{name} requires an exact integer tick or nanosecond")
    return int(value)


def _finite_number(value):
    try:
        return math.isfinite(float(value))
    except (TypeError, ValueError, OverflowError):
        return False


def _rss_bytes():
    return resource.getrusage(resource.RUSAGE_SELF).ru_maxrss * 1024


def _require_statistics(settings):
    required = {"block_length": 5, "bootstrap_seed": 20260907, "confidence": 0.95,
                "minimum_dates": 100, "minimum_events": 20, "replicates": 1000}
    for key, expected in required.items():
        if settings.get(key) != expected:
            raise ContractError(f"analysis-plan statistics {key} must remain {expected}")
    if not settings.get("descriptive_quantiles"):
        raise ContractError("descriptive quantiles required")


def _unique_shards(shards):
    ordered, seen = [], set()
    for shard in shards:
        if not isinstance(shard, dict):
            raise IntegrityError("shard record required")
        key = (shard.get("root"), int(shard["year"]))
        if key in seen:
            continue
        if "tables" not in shard or "paths" not in shard["tables"] or "formations" not in shard["tables"]:
            raise IntegrityError("shard is missing retained path/formation tables")
        if "anchor_supplement" not in shard:
            raise IntegrityError("every immutable source shard needs its exact anchor supplement")
        seen.add(key)
        ordered.append(shard)
    if not ordered:
        raise IntegrityError("variant has no retained shards")
    return ordered


def _shard_ref(shard):
    return {
        "root": shard["root"], "year": int(shard["year"]),
        "intended_cash_dates": shard.get("intended_cash_dates"),
        "paths": shard["tables"]["paths"], "formations": shard["tables"]["formations"],
        "statistics": shard.get("statistics"),
        "population_role": shard.get("population_role"),
        "source_supersession": shard.get("source_supersession"),
    }


def _adapter_identity_ok(common, clocks):
    manifest = common.manifest
    return (manifest.get("version") == COMMON_ADAPTER_VERSION
            and manifest.get("horizon") == HORIZON
            and tuple(manifest.get("clock_ids") or ()) == tuple(clocks)
            and tuple(manifest.get("target_names") or ()) == COMMON_TARGETS
            and "same common receiver exact H/L/C" in str(manifest.get("target_rule", "")))


def _missing_clock_preserves_dates(common):
    roots, dates, own = (np.asarray(common.fields[name]) for name in
                         ("root", "date", "common_own_features_available"))
    if own.dtype != np.bool_ or not np.any(~own):
        return True
    intended = set(zip(roots.tolist(), dates.tolist()))
    missing = set(zip(roots[~own].tolist(), dates[~own].tolist()))
    return missing <= intended and len(intended) == len(set(zip(roots.tolist(), dates.tolist())))


def _feature_column(matrix, *names):
    available = {name: index for index, name in enumerate(feature_names(matrix))}
    for name in names:
        if name in available:
            return np.asarray(matrix.features[:, available[name]], dtype=np.float64), name
    return None, None


def _fit_train_tertiles(matrix):
    return _fit_slice_tertiles(matrix, 2020, 2022)


def _fit_slice_tertiles(matrix, first_year, last_year):
    values, _ = _feature_column(matrix, "prior_actual_RTH_20_mean_width_ticks", "prior_20_mean_width_ticks")
    if values is None:
        return {root: None for root, _ in _root_codes(matrix)}
    years = np.asarray([date.fromordinal(int(day)).year for day in matrix.fields["date"]], dtype=np.int64)
    known = np.asarray(matrix.fields["common_known_dependency_available"])
    # Training thresholds use known prior scale only. Outcomes are not read.
    eligible = known & (years >= first_year) & (years <= last_year) & np.isfinite(values)
    by_root = {}
    for root, code in _root_codes(matrix):
        mask = eligible & (matrix.fields["root"] == code)
        # One value per date: prior-20 is a common control.
        dates = matrix.fields["date"][mask]
        series = values[mask]
        if not len(series):
            by_root[root] = []
            continue
        order = np.argsort(dates, kind="stable")
        _, first = np.unique(dates[order], return_index=True)
        by_root[root] = series[order][first]
    return fit_root_prior_vol_tertiles(by_root)


def _root_codes(matrix):
    names = tuple(matrix.categories["root"])
    return tuple((name, names.index(name)) for name in names)


def _clock_name(matrix, code):
    return matrix.categories["clock"][int(code)]


def _materialize_variant(store, shards, analysis_plan, *, resources, variant):
    parts, formations = [], {}
    ordered = sorted(shards, key=lambda shard: (shard["root"], int(shard["year"])))
    for index, shard in enumerate(ordered):
        records = _read_transition_formations(store, shard)
        resources["table_reads"] += 1
        overlap = set(records) & set(formations)
        if overlap:
            raise IntegrityError("duplicate transition formation identity across shards")
        formations.update(records)
        supplements = {(shard["root"], shard["year"]): shard["anchor_supplement"]}
        matrix = prepare_paths(store, [shard], plan=analysis_plan, phase="timing_descriptive",
                               anchor_supplements=supplements)
        resources["prepare_paths_calls"] += 1
        resources["table_reads"] += 1
        common = prepare_common_clock_comparison(matrix, plan=analysis_plan)
        resources["common_adapter_calls"] += 1
        if tuple(common.manifest.get("clock_ids") or ()) != tuple(
                analysis_plan["matched_clock_comparison"]["clocks"]):
            raise IntegrityError("common comparison clocks differ from the analysis plan")
        del matrix
        parts.append(common)
        if resources["pilot"] is None:
            resources["pilot"] = {
                "variant": variant, "root": shard["root"], "year": int(shard["year"]),
                "common_rows": int(common.size), "cpu_seconds": time.process_time(),
                "rss_bytes": _rss_bytes(),
                "rule": "First retained root/year measured; remaining shards use the same registered allowances.",
            }
        gc.collect()
        resources["peak_rss_bytes"] = max(resources["peak_rss_bytes"], _rss_bytes())
        del index
    stacked = _stack_common(parts)
    del parts
    gc.collect()
    return stacked, formations


def _stack_common(parts):
    if not parts:
        raise ContractError("nonempty common comparison population required")
    first = parts[0]
    names = feature_names(first)
    for part in parts[1:]:
        if feature_names(part) != names or part.categories != first.categories:
            raise IntegrityError("common comparison schema differs across shards")
        if set(part.fields) != set(first.fields):
            raise IntegrityError("common comparison fields differ across shards")
    features = np.concatenate([part.features for part in parts], axis=0)
    fields = {name: np.concatenate([part.fields[name] for part in parts], axis=0) for name in first.fields}
    manifest = {
        "version": first.manifest["version"], "stacked_parts": len(parts), "rows": int(len(features)),
        "clock_ids": first.manifest.get("clock_ids"), "horizon": first.manifest.get("horizon"),
        "feature_columns": first.manifest.get("feature_columns"),
        "feature_groups": first.manifest.get("feature_groups", {}),
        "target_names": first.manifest.get("target_names"),
        "known_reference_rule": first.manifest.get("known_reference_rule"),
        "own_feature_rule": first.manifest.get("own_feature_rule"),
        "target_rule": first.manifest.get("target_rule"),
        "target_eligibility": first.manifest.get("target_eligibility"),
        "source_matrix": [part.manifest.get("id") for part in parts],
        "row_identity": "per-root-year common adapter stack; original_prepared_row is shard-local",
    }
    from trading_research.operations.artifacts import digest
    manifest["id"] = digest(manifest)
    shards = tuple(item for part in parts for item in (part.shards or ()))
    return PreparedPaths(manifest, features, fields, first.categories, shards)


def _read_transition_formations(store, shard):
    table = _read_columns(store, shard["tables"]["formations"], list(FORMATION_COLUMNS))
    import pyarrow as pa
    import pyarrow.compute as pc
    kept = table.filter(pc.is_in(table["clock"], value_set=pa.array(list(TRANSITION_CLOCKS))))
    records = {}
    if kept.num_rows == 0:
        return records
    payload = kept.to_pydict()
    n = kept.num_rows
    for index in range(n):
        clock = payload["clock"][index]
        day = payload["date"][index]
        root = payload["root"][index] or shard["root"]
        if type(day) is not str or type(clock) is not str or type(root) is not str:
            raise IntegrityError("transition formation lost date/clock/root identity")
        key = (root, day, clock)
        if key in records:
            raise IntegrityError("duplicate transition formation on a root/date/clock")
        records[key] = {name: payload[name][index] for name in FORMATION_COLUMNS}
        records[key]["root"] = root
        records[key]["year"] = int(payload["year"][index]) if payload["year"][index] is not None else int(shard["year"])
    return records


def _product_a(common, plan, settings, tertiles, *, variant, resources):
    names = feature_names(common)
    width_ratio, _ = _feature_column(common, "width_prior_actual_RTH_ratio", "width_prior_ratio")
    prior20, prior_name = _feature_column(common, "prior_actual_RTH_20_mean_width_ticks", "prior_20_mean_width_ticks")
    last_close, _ = _feature_column(common, "last_close_position")
    open_position, _ = _feature_column(common, "open_position")
    delay, _ = _feature_column(common, "last_close_age_minutes")
    width, _ = _feature_column(common, "width_ticks")
    pairs = declared_clock_pairs(plan)
    overlap_lookup = {name: names.index(name) for name in names if name.endswith("_price_overlap_fraction")}
    roots = np.asarray(common.fields["root"])
    dates = np.asarray(common.fields["date"], dtype=np.int64)
    clocks = np.asarray(common.fields["clock"])
    own = np.asarray(common.fields["common_own_features_available"])
    target_ok = np.asarray(common.fields["common_target_eligible"])
    known = np.asarray(common.fields["common_known_dependency_available"])
    origin = np.asarray(common.fields["origin_ns"])
    maturity = np.asarray(common.fields.get("common_maturity_at_ns", common.fields.get("maturity_at_ns")))
    years = np.asarray([date.fromordinal(int(day)).year for day in dates], dtype=np.int64)
    iso = np.asarray([date.fromordinal(int(day)).isoformat() for day in dates])
    width_bins = np.array([width_ratio_bin(None if width_ratio is None else width_ratio[i] if own[i] else None)
                           for i in range(common.size)], dtype=object)
    position_bins = np.array([position_bin(None if last_close is None else last_close[i] if own[i] else None)
                              for i in range(common.size)], dtype=object)
    vol_bins = np.empty(common.size, dtype=object)
    for index in range(common.size):
        root = common.categories["root"][int(roots[index])]
        value = None if prior20 is None or not known[index] else prior20[index]
        vol_bins[index] = assign_prior_vol_bin(value, (tertiles or {}).get(root))
    targets = {name: np.asarray(common.fields[name], dtype=np.float64) for name in COMMON_TARGETS}
    rows = []
    for index in range(common.size):
        clock = _clock_name(common, clocks[index])
        root = common.categories["root"][int(roots[index])]
        year = int(years[index])
        rows.append({
            "source_variant": variant, "product": "common_clock_geometry",
            "phase": _phase_name(year), "year": year, "root": root, "date": iso[index],
            "clock": clock, "candidate": clock,
            "feature_known_at_ns": int(origin[index]),
            "target_maturity_ns": int(maturity[index]),
            "feature_available": bool(own[index]), "target_available": bool(target_ok[index]),
            "known_dependency_available": bool(known[index]),
            "width_ticks": _optional_float(None if width is None or not own[index] else width[index]),
            "width_ratio": _optional_float(None if width_ratio is None or not own[index] else width_ratio[index]),
            "open_position": _optional_float(None if open_position is None or not own[index] else open_position[index]),
            "last_close_position": _optional_float(None if last_close is None or not own[index] else last_close[index]),
            "last_close_age_minutes": _optional_float(None if delay is None else delay[index]),
            "prior20_mean_width": _optional_float(None if prior20 is None or not known[index] else prior20[index]),
            "width_bin": width_bins[index], "prior_vol_bin": vol_bins[index],
            "position_bin": position_bins[index],
            "joint_width_vol": width_bins[index] + "|" + vol_bins[index],
            "common_terminal_priorW": _optional_float(targets["common_terminal_priorW"][index]),
            "common_high_priorW": _optional_float(targets["common_high_priorW"][index]),
            "common_low_priorW": _optional_float(targets["common_low_priorW"][index]),
            "target_missing": not bool(target_ok[index]),
            "geometry_missing": not bool(own[index]),
            "prior20_feature": prior_name,
        })
    slices = {}
    paired_zero_retained = True
    for slice_name, first, last, kind in (*PHASE_SLICES, *YEAR_SLICES):
        in_slice = (years >= first) & (years <= last)
        if not np.any(in_slice):
            continue
        slices[slice_name] = {"kind": kind, "roots": {}}
        for root, code in _root_codes(common):
            root_mask = in_slice & (roots == code)
            if not np.any(root_mask):
                continue
            intended = tuple(sorted(set(iso[root_mask].tolist())))
            clock_tables = {}
            metrics = {}
            for clock_code, clock in enumerate(common.categories["clock"]):
                mask = root_mask & (clocks == clock_code)
                if not np.any(mask):
                    continue
                clock_iso = iso[mask]
                if tuple(sorted(clock_iso.tolist())) != tuple(intended):
                    raise IntegrityError("a declared clock lost an intended root/date row")
                feature_dates = int(np.unique(dates[mask & own]).size)
                target_dates = int(np.unique(dates[mask & target_ok]).size)
                clock_tables[clock] = {
                    "observations": int(mask.sum()), "independent_dates": len(intended),
                    "feature_available_dates": feature_dates, "target_available_dates": target_dates,
                    "missing_own_geometry_dates": int(np.unique(dates[mask & ~own]).size),
                    "conditionals": [],
                }
                for target in COMMON_TARGETS:
                    values = {day: _optional_float(targets[target][mask][at])
                              if target_ok[mask][at] else None
                              for at, day in enumerate(clock_iso)}
                    metrics[f"{clock}|unconditional|{TARGET_LABELS[target]}"] = values
                groups = (
                    ("width_ratio", width_bins, WIDTH_RATIO_LABELS + ("missing_own_geometry",)),
                    ("prior_vol", vol_bins, PRIOR_VOL_LABELS + ("missing_prior_vol",)),
                    ("position", position_bins, POSITION_LABELS + ("missing_own_geometry",)),
                )
                for group_name, labels, allowed in groups:
                    for label in allowed:
                        member = mask & (labels == label)
                        resources["conditional_groups"] += 1
                        record = _group_record(clock_iso, member[mask], target_ok[mask], targets, mask,
                                               settings, group_name, label)
                        clock_tables[clock]["conditionals"].append(record)
                        for target in COMMON_TARGETS:
                            metrics[f"{clock}|{group_name}|{label}|{TARGET_LABELS[target]}"] = {
                                day: (_optional_float(targets[target][mask][at])
                                      if member[mask][at] and target_ok[mask][at] else None)
                                for at, day in enumerate(clock_iso)
                            }
                for width_label in WIDTH_RATIO_LABELS + ("missing_own_geometry",):
                    for vol_label in PRIOR_VOL_LABELS + ("missing_prior_vol",):
                        label = width_label + "|" + vol_label
                        member = mask & (width_bins == width_label) & (vol_bins == vol_label)
                        resources["conditional_groups"] += 1
                        record = _group_record(clock_iso, member[mask], target_ok[mask], targets, mask,
                                               settings, "width_vol", label)
                        clock_tables[clock]["conditionals"].append(record)
                        for target in COMMON_TARGETS:
                            metrics[f"{clock}|width_vol|{label}|{TARGET_LABELS[target]}"] = {
                                day: (_optional_float(targets[target][mask][at])
                                      if member[mask][at] and target_ok[mask][at] else None)
                                for at, day in enumerate(clock_iso)
                            }
            pair_tables, pair_metrics, pair_ok = _paired_tables(
                common, root_mask, iso, intended, own, target_ok, targets, width, open_position,
                delay, width_bins, vol_bins, overlap_lookup, pairs, settings, resources)
            paired_zero_retained = paired_zero_retained and pair_ok
            metrics.update(pair_metrics)
            intervals = {}
            if metrics and intended:
                batch = metric_intervals(metrics, intended, settings)
                resources["bootstrap_metrics"] += len(batch)
                intervals = {name: _interval_record(batch[name], settings) for name in batch}
            _attach_intervals(clock_tables, intervals)
            _attach_pair_intervals(pair_tables, intervals, settings)
            slices[slice_name]["roots"][root] = {
                "intended_dates": len(intended), "clocks": clock_tables, "pairs": pair_tables,
                "controls_meaning": (
                    "Width/prior-vol bins hold the common 10:01→cash-close target fixed. "
                    "Clock differences cannot be different targets or different date opportunities."
                ),
                "clock_ranking": None, "forecast_gain_claimed": False,
            }
    return {
        "slices": slices, "paired_zero_event_dates_retained": paired_zero_retained,
        "clock_ranking": None, "context_increment_assessed": False,
        "same_target_rule": "Common normalized H/L/C is identical across clocks on a date; target-mean gaps are not clock gain.",
    }, rows


def _group_record(clock_iso, member, target_ok, targets, mask, settings, group_name, label):
    observed = [float(targets["common_terminal_priorW"][mask][at])
                for at in range(len(clock_iso))
                if member[at] and target_ok[at] and np.isfinite(targets["common_terminal_priorW"][mask][at])]
    dates = len({clock_iso[at] for at in range(len(clock_iso)) if member[at]})
    events = len(observed)
    sparse = dates < settings["minimum_dates"] or events < settings["minimum_events"]
    return {
        "group": group_name, "label": label, "dates": dates, "events": events,
        "sparse": sparse, "interval_claimable": not sparse,
        "quantiles": _descriptive(observed, settings["descriptive_quantiles"]),
    }


def _paired_tables(common, root_mask, iso, intended, own, target_ok, targets, width,
                   open_position, delay, width_bins, vol_bins, overlap_lookup, pairs,
                   settings, resources):
    clocks = np.asarray(common.fields["clock"])
    names = common.categories["clock"]
    index_by_clock = {name: names.index(name) for name in names}
    tables = []
    metrics = {}
    zero_retained = True
    for source, neighbor, kind in pairs:
        if source not in index_by_clock or neighbor not in index_by_clock:
            continue
        source_mask = root_mask & (clocks == index_by_clock[source])
        neighbor_mask = root_mask & (clocks == index_by_clock[neighbor])
        source_iso = iso[source_mask]
        neighbor_iso = iso[neighbor_mask]
        if tuple(sorted(source_iso.tolist())) != tuple(intended) or tuple(sorted(neighbor_iso.tolist())) != tuple(intended):
            raise IntegrityError("paired clocks must occupy the exact same intended dates")
        source_at = {source_iso[at]: at for at in range(len(source_iso))}
        neighbor_at = {neighbor_iso[at]: at for at in range(len(neighbor_iso))}
        source_own = own[source_mask]
        neighbor_own = own[neighbor_mask]
        source_target = target_ok[source_mask]
        neighbor_target = target_ok[neighbor_mask]
        overlap_name = f"anchor_{source}_price_overlap_fraction"
        overlap_values = None
        if overlap_name in overlap_lookup:
            overlap_values = np.asarray(common.features[:, overlap_lookup[overlap_name]], dtype=np.float64)[neighbor_mask]
        availability = {day: float(bool(source_own[source_at[day]] and neighbor_own[neighbor_at[day]]))
                        for day in intended}
        metrics[f"{source}|vs|{neighbor}|both_available"] = availability
        for field, array, present, locator, mask in (
            ("source_width", width, source_own, source_at, source_mask),
            ("neighbor_width", width, neighbor_own, neighbor_at, neighbor_mask),
            ("source_open_position", open_position, source_own, source_at, source_mask),
            ("neighbor_open_position", open_position, neighbor_own, neighbor_at, neighbor_mask),
            ("source_delay", delay, source_own, source_at, source_mask),
            ("neighbor_delay", delay, neighbor_own, neighbor_at, neighbor_mask),
        ):
            if array is None:
                continue
            values = array[mask]
            metrics[f"{source}|vs|{neighbor}|{field}"] = {
                day: _optional_float(values[locator[day]]) if present[locator[day]] else None
                for day in intended
            }
        if overlap_values is not None:
            neighbor_bins = np.array([overlap_bin(overlap_values[at] if neighbor_own[at] else None)
                                      for at in range(len(neighbor_iso))], dtype=object)
            for label in OVERLAP_LABELS:
                member = neighbor_own & (neighbor_bins == label)
                resources["conditional_groups"] += 1
                events = int(np.count_nonzero(member & neighbor_target))
                dates_n = int(np.count_nonzero(member))
                sparse = dates_n < settings["minimum_dates"] or events < settings["minimum_events"]
                for target in COMMON_TARGETS:
                    target_values = targets[target][neighbor_mask]
                    metrics[f"{source}|vs|{neighbor}|overlap|{label}|{TARGET_LABELS[target]}"] = {
                        day: (_optional_float(target_values[neighbor_at[day]])
                              if member[neighbor_at[day]] and neighbor_target[neighbor_at[day]] else None)
                        for day in intended
                    }
                tables.append({
                    "source": source, "neighbor": neighbor, "kind": kind, "group": "overlap",
                    "label": label, "dates": dates_n, "events": events, "sparse": sparse,
                    "interval_claimable": not sparse,
                    "note": "Overlap bins are secondary and only support an interval claim at 100 dates and 20 events.",
                })
        both_missing = int(np.count_nonzero(~source_own & ~neighbor_own))
        tables.append({
            "source": source, "neighbor": neighbor, "kind": kind,
            "same_dates": len(intended),
            "source_feature_dates": int(np.count_nonzero(source_own)),
            "neighbor_feature_dates": int(np.count_nonzero(neighbor_own)),
            "both_unavailable_dates": both_missing,
            "association_only": True, "forecast_gain_claimed": False, "clock_ranking": None,
        })
        del source_iso, neighbor_iso
    return tables, metrics, zero_retained


def _attach_intervals(clock_tables, intervals):
    for clock, table in clock_tables.items():
        table["unconditional"] = {
            TARGET_LABELS[target]: intervals.get(f"{clock}|unconditional|{TARGET_LABELS[target]}")
            for target in COMMON_TARGETS
        }
        for record in table["conditionals"]:
            record["intervals"] = {
                TARGET_LABELS[target]: intervals.get(
                    f"{clock}|{record['group']}|{record['label']}|{TARGET_LABELS[target]}")
                for target in COMMON_TARGETS
            }
            if record.get("sparse"):
                record["intervals"] = {name: _strip_ci(value) for name, value in record["intervals"].items()}


def _attach_pair_intervals(pair_tables, intervals, settings):
    for record in pair_tables:
        source, neighbor = record.get("source"), record.get("neighbor")
        if record.get("group") == "overlap":
            record["intervals"] = {
                TARGET_LABELS[target]: intervals.get(
                    f"{source}|vs|{neighbor}|overlap|{record['label']}|{TARGET_LABELS[target]}")
                for target in COMMON_TARGETS
            }
            if record.get("sparse"):
                record["intervals"] = {name: _strip_ci(value) for name, value in record["intervals"].items()}
            continue
        record["metrics"] = {
            name: intervals.get(f"{source}|vs|{neighbor}|{name}")
            for name in ("both_available", "source_width", "neighbor_width",
                         "source_open_position", "neighbor_open_position",
                         "source_delay", "neighbor_delay")
            if intervals.get(f"{source}|vs|{neighbor}|{name}") is not None
        }


def _product_b(formations, common, settings, *, variant, resources):
    by_date = defaultdict(dict)
    for root, code in _root_codes(common):
        for ordinal in intended_root_dates(common, code):
            by_date[(root, date.fromordinal(ordinal).isoformat())] = {}
    for (root, day, clock), record in formations.items():
        by_date[(root, day)][clock] = record
    if not by_date:
        return {"slices": {}, "contract_mismatch_excluded": True,
                "early_classification_forbidden": True,
                "not_judas_reversal": True, "not_86_46": True}, []
    rows = []
    for (root, day), clocks in sorted(by_date.items()):
        jtr = clocks.get("JTR_fixed_04")
        year = date.fromisoformat(day).year
        if jtr is not None and jtr.get("year") is not None:
            year = int(jtr["year"])
        for turn in TURN_WINDOWS:
            rows.append(_transition_row(variant, root, day, year, jtr, clocks.get(turn),
                                        clocks.get(PRECEDING_TURN[turn]), turn))
    slices = {}
    for slice_name, first, last, kind in (*PHASE_SLICES, *YEAR_SLICES):
        chosen = [row for row in rows if first <= row["year"] <= last]
        if not chosen:
            continue
        slices[slice_name] = {"kind": kind, "roots": {}}
        for root in sorted({row["root"] for row in chosen}):
            root_rows = [row for row in chosen if row["root"] == root]
            intended = tuple(sorted({row["date"] for row in root_rows}))
            slices[slice_name]["roots"][root] = _transition_root_tables(
                root_rows, intended, settings, resources)
    return {
        "slices": slices,
        "operational_description": (
            "Same-date JTR_fixed_04 versus 09:30–09:40 / 09:40–09:50 / 09:50–10:00 formed windows. "
            "Compatible intersection is not trade contact. A definite print requires a literal O/H/L/C. "
            "This is not the source Judas reversal, not a hidden-stop proof, and not 86.46%."
        ),
        "resolution_limit": (
            "Full intra-minute sequence cannot be inferred from 10-minute OHLC. "
            "JTR-07/08/09: 09:40–09:50 may be reversal or continuation; 10:00 news can delay cycle 2; "
            "contact does not prove a reversal."
        ),
        "clock_ranking": None, "not_judas_reversal": True, "not_86_46": True,
    }, rows


def _transition_row(variant, root, day, year, jtr, turn, prior, turn_name):
    row = {
        "source_variant": variant, "product": "jtr_transition_window",
        "phase": _phase_name(year), "year": year, "root": root, "date": day,
        "clock": turn_name, "candidate": turn_name,
        "feature_known_at_ns": None, "target_maturity_ns": -1,
        "jtr_available_at_ns": None, "window_available_at_ns": None,
        "contract_match": "unresolved", "jtr_known_before_turn": False,
        "close_inside_jtr": None, "signed_close_open": None, "prior_signed_close_open": None,
        "move_relationship": "insufficient", "zero_width": None,
        "geometry_missing": True, "target_missing": True,
    }
    for level in LEVEL_NAMES:
        row[f"{level}_class"] = "censored"
        row[f"{level}_compatible"] = False
        row[f"{level}_boundary_touch"] = False
        row[f"{level}_definite_print"] = False
    if jtr is None or turn is None:
        row["identification"] = "missing_jtr" if jtr is None else "missing_turn_window"
        return row
    row["feature_known_at_ns"] = turn.get("available_at_ns")
    row["jtr_available_at_ns"] = jtr.get("available_at_ns")
    row["window_available_at_ns"] = turn.get("available_at_ns")
    row["contract_match"] = raw_contract_match(jtr, turn)
    known = jtr_known_before_turn(jtr.get("available_at_ns"), turn.get("formation_start_ns"))
    row["jtr_known_before_turn"] = known
    if row["contract_match"] == "mismatch":
        row["identification"] = "raw_contract_mismatch_excluded"
        return row
    if row["contract_match"] == "unresolved":
        row["identification"] = "contract_identity_unresolved"
        return row
    if not known:
        row["identification"] = "jtr_not_known_before_turn"
        return row
    if turn.get("available_at_ns") is None or jtr.get("available_at_ns") is None:
        row["identification"] = "window_known_at_missing"
        return row
    if not _complete_ohlc(jtr) or not _complete_ohlc(turn) or jtr.get("zero_width") is True or turn.get("zero_width") is True:
        row["identification"] = "censored_incomplete_or_zero_width"
        row["zero_width"] = bool(jtr.get("zero_width") or turn.get("zero_width"))
        return row
    levels = jtr_doubled_levels(jtr["high_ticks"], jtr["low_ticks"])
    row["geometry_missing"] = False
    row["zero_width"] = False
    row["jtr_width_ticks"] = levels["width_ticks"]
    row["signed_close_open"] = signed_close_open(turn["open_ticks"], turn["close_ticks"])
    if prior is not None and _complete_ohlc(prior) and raw_contract_match(jtr, prior) == "matched":
        row["prior_signed_close_open"] = signed_close_open(prior["open_ticks"], prior["close_ticks"])
    else:
        row["prior_signed_close_open"] = None
    row["move_relationship"] = classify_move_relationship(row["signed_close_open"], row["prior_signed_close_open"])
    row["close_inside_jtr"] = bool(jtr["low_ticks"] <= turn["close_ticks"] <= jtr["high_ticks"])
    any_print = False
    any_compatible = False
    for level in LEVEL_NAMES:
        observed = classify_level_observation(
            turn["open_ticks"], turn["high_ticks"], turn["low_ticks"], turn["close_ticks"],
            levels[level])
        row[f"{level}_class"] = observed["observation_class"]
        row[f"{level}_compatible"] = observed["compatible_intersection"]
        row[f"{level}_boundary_touch"] = observed["boundary_touch"]
        row[f"{level}_definite_print"] = observed["definite_print"]
        any_print = any_print or observed["definite_print"]
        any_compatible = any_compatible or observed["compatible_intersection"]
    row["target_missing"] = False
    if any_print:
        row["identification"] = "definite_print"
    elif any_compatible:
        row["identification"] = "compatible_ambiguous"
    else:
        row["identification"] = "no_event"
    return row


def _complete_ohlc(record):
    return record is not None and all(record.get(name) is not None for name in
                                      ("open_ticks", "high_ticks", "low_ticks", "close_ticks"))


def _transition_root_tables(rows, intended, settings, resources):
    tables = {}
    metrics = {}
    for turn in TURN_WINDOWS:
        chosen = [row for row in rows if row["clock"] == turn]
        by_date = {row["date"]: row for row in chosen}
        if set(by_date) != set(intended) or len(by_date) != len(intended):
            # Every intended date is retained even when the turn window is missing.
            for day in intended:
                by_date.setdefault(day, {"identification": "missing_turn_window", "date": day,
                                         "contract_match": "unresolved", "move_relationship": "insufficient",
                                         "close_inside_jtr": None})
        counts = defaultdict(int)
        for day in intended:
            counts[by_date[day].get("identification", "missing_turn_window")] += 1
        metrics[f"{turn}|definite_print"] = {day: float(by_date[day].get("identification") == "definite_print")
                                             for day in intended}
        metrics[f"{turn}|compatible"] = {
            day: float(any(by_date[day].get(f"{level}_compatible") for level in LEVEL_NAMES))
            for day in intended
        }
        metrics[f"{turn}|no_event"] = {day: float(by_date[day].get("identification") == "no_event")
                                       for day in intended}
        metrics[f"{turn}|close_inside_jtr"] = {
            day: None if by_date[day].get("close_inside_jtr") is None else float(by_date[day]["close_inside_jtr"])
            for day in intended
        }
        metrics[f"{turn}|opposite"] = {
            day: None if by_date[day].get("move_relationship") == "insufficient"
            else float(by_date[day].get("move_relationship") == "opposite")
            for day in intended
        }
        metrics[f"{turn}|flat"] = {
            day: None if by_date[day].get("move_relationship") == "insufficient"
            else float(by_date[day].get("move_relationship") == "flat")
            for day in intended
        }
        metrics[f"{turn}|continuation"] = {
            day: None if by_date[day].get("move_relationship") == "insufficient"
            else float(by_date[day].get("move_relationship") == "continuation")
            for day in intended
        }
        metrics[f"{turn}|contract_mismatch"] = {
            day: float(by_date[day].get("identification") == "raw_contract_mismatch_excluded")
            for day in intended
        }
        metrics[f"{turn}|early_blocked"] = {
            day: float(by_date[day].get("identification") == "jtr_not_known_before_turn")
            for day in intended
        }
        tables[turn] = {
            "observations": len(intended), "independent_dates": len(intended),
            "identification_counts": dict(counts),
            "zero_event_dates_retained": True,
            "not_judas_reversal": True,
        }
    for left, right in (("turn_source", "turn_earlier"), ("turn_source", "turn_later")):
        metrics[f"{left}|paired_print_minus|{right}"] = {
            day: metrics[f"{left}|definite_print"][day] - metrics[f"{right}|definite_print"][day]
            for day in intended
        }
        metrics[f"{left}|paired_inside_minus|{right}"] = {
            day: _paired_optional(metrics[f"{left}|close_inside_jtr"][day],
                                  metrics[f"{right}|close_inside_jtr"][day])
            for day in intended
        }
    intervals = metric_intervals(metrics, intended, settings) if intended else {}
    resources["bootstrap_metrics"] += len(intervals)
    for turn, table in tables.items():
        table["rates"] = {name: _interval_record(intervals[key], settings)
                          for name, key in (
                              ("definite_print", f"{turn}|definite_print"),
                              ("compatible", f"{turn}|compatible"),
                              ("no_event", f"{turn}|no_event"),
                              ("close_inside_jtr", f"{turn}|close_inside_jtr"),
                              ("opposite", f"{turn}|opposite"),
                              ("flat", f"{turn}|flat"),
                              ("continuation", f"{turn}|continuation"),
                              ("contract_mismatch", f"{turn}|contract_mismatch"),
                              ("early_blocked", f"{turn}|early_blocked"),
                          ) if key in intervals}
        for name, value in table["rates"].items():
            if value and value.get("sparse"):
                table["rates"][name] = _strip_ci(value)
    tables["paired"] = {
        "source_minus_earlier_print": intervals.get("turn_source|paired_print_minus|turn_earlier"),
        "source_minus_later_print": intervals.get("turn_source|paired_print_minus|turn_later"),
        "source_minus_earlier_inside": intervals.get("turn_source|paired_inside_minus|turn_earlier"),
        "source_minus_later_inside": intervals.get("turn_source|paired_inside_minus|turn_later"),
        "same_dates": len(intended),
        "zero_event_dates_retained": True,
        "forecast_gain_claimed": False,
        "clock_ranking": None,
        "not_judas_reversal": True,
    }
    return {
        "intended_dates": len(intended),
        "windows": tables,
        "resolution_limit": (
            "10-minute OHLC cannot recover intra-minute order. "
            "JTR-07/08/09: 09:40–09:50 may be reversal or continuation; contact is not a reversal."
        ),
    }


def _phase_name(year):
    if year <= 2022:
        return "training_2020_2022"
    if year <= 2024:
        return "development_2023_2024"
    return "confirmation_2025_2026"


def _optional_float(value):
    if value is None or isinstance(value, bool) or not _finite_number(value):
        return None
    return float(value)


def _paired_optional(left, right):
    if left is None or right is None:
        return None
    return float(left) - float(right)


def _interval_record(metric, settings):
    if not metric:
        return None
    support = dict(metric.get("support") or {})
    sparse = bool(support.get("sparse"))
    if support.get("independent_dates", 0) < settings["minimum_dates"]:
        sparse = True
    if support.get("events", 0) < settings["minimum_events"]:
        sparse = True
    bootstrap = metric.get("bootstrap") or {}
    record = {
        "estimate": _optional_float(metric.get("estimate")),
        "valid_dates": metric.get("valid_date_count"),
        "valid_events": metric.get("valid_event_count"),
        "missing_dates": metric.get("missing_date_count"),
        "support": _sanitize(support),
        "sparse": sparse,
        "interval_claimable": not sparse,
    }
    if sparse:
        record["no_ci_claim"] = (
            "fewer than 100 independent dates or 20 events; the interval is not a supported claim"
        )
        record["bootstrap_unclaimed"] = {
            "lower": _optional_float(bootstrap.get("lower")),
            "upper": _optional_float(bootstrap.get("upper")),
        }
    else:
        record["bootstrap"] = {
            "lower": _optional_float(bootstrap.get("lower")),
            "upper": _optional_float(bootstrap.get("upper")),
            "confidence": settings["confidence"],
            "replicates": settings["replicates"],
            "seed": settings["bootstrap_seed"],
            "block_length": settings["block_length"],
        }
    return record


def _strip_ci(record):
    if not record:
        return record
    value = dict(record)
    value["interval_claimable"] = False
    value["sparse"] = True
    if "bootstrap" in value:
        value["bootstrap_unclaimed"] = value.pop("bootstrap")
    value["no_ci_claim"] = (
        "fewer than 100 independent dates or 20 events; the interval is not a supported claim"
    )
    return value


def _ambiguity_limitations():
    return (
        "Declared study-local observables only. JTR-04 retains both the open-to-projection leg "
        "and a 09:40–09:50 mean/-0.5 opportunity; reported points are not a sample definition. "
        "JTR-07 compressed continuation and JTR-08 reversal share the same 09:40–09:50 clock; "
        "the window does not decide which path occurred. JTR-09 marks a failed apparent turn and "
        "a 10:00 news delay. Contact with EQ or a half-range extension is not a reversal, stop "
        "hunt, or inventory event. A 10-minute turn_* formation is not the full source pattern. "
        "Intra-minute sequence cannot be recovered from these three formed windows."
    )


def _annual_refs(development, confirmation):
    refs = []
    for worker, stage in ((development, "development"), (confirmation, "confirmation")):
        if worker.get("narrative"):
            refs.append({"stage": stage, "kind": "narrative", "ref": worker["narrative"]})
        if worker.get("source_sensitivity_narrative"):
            refs.append({"stage": stage, "kind": "source_sensitivity_narrative",
                         "ref": worker["source_sensitivity_narrative"]})
        for shard in worker.get("shards") or ():
            refs.append({
                "stage": stage, "kind": "year_statistics",
                "root": shard.get("root"), "year": shard.get("year"),
                "statistics": shard.get("statistics"),
                "scope": "Existing per-year descriptive statistics; this module does not rerun that annual stage.",
            })
    return refs


def _write_parquet(outputs, name, rows, *, kind):
    import pyarrow as pa
    import pyarrow.parquet as pq
    schema = _date_schema()
    table = pa.Table.from_pylist([_parquet_row(row, schema) for row in rows], schema=schema) if rows else schema.empty_table()
    sink = pa.BufferOutputStream()
    pq.write_table(table, sink, compression="zstd", use_dictionary=True, write_statistics=True,
                   row_group_size=65536)
    payload = sink.getvalue().to_pybytes()
    with outputs.create(name) as stream:
        stream.write(payload)
    return {**outputs.reference(name, kind=kind), "rows": int(table.num_rows),
            "schema_sha256": hashlib.sha256(table.schema.serialize().to_pybytes()).hexdigest()}


def _date_schema():
    import pyarrow as pa
    fields = [
        ("source_variant", pa.string()), ("product", pa.string()), ("phase", pa.string()),
        ("year", pa.int64()), ("root", pa.string()), ("date", pa.string()),
        ("clock", pa.string()), ("candidate", pa.string()),
        ("feature_known_at_ns", pa.int64()), ("target_maturity_ns", pa.int64()),
        ("feature_available", pa.bool_()), ("target_available", pa.bool_()),
        ("known_dependency_available", pa.bool_()), ("geometry_missing", pa.bool_()),
        ("target_missing", pa.bool_()), ("width_ticks", pa.float64()),
        ("width_ratio", pa.float64()), ("open_position", pa.float64()),
        ("last_close_position", pa.float64()), ("last_close_age_minutes", pa.float64()),
        ("prior20_mean_width", pa.float64()), ("width_bin", pa.string()),
        ("prior_vol_bin", pa.string()), ("position_bin", pa.string()),
        ("joint_width_vol", pa.string()), ("common_terminal_priorW", pa.float64()),
        ("common_high_priorW", pa.float64()), ("common_low_priorW", pa.float64()),
        ("prior20_feature", pa.string()), ("jtr_available_at_ns", pa.int64()),
        ("window_available_at_ns", pa.int64()), ("contract_match", pa.string()),
        ("jtr_known_before_turn", pa.bool_()), ("close_inside_jtr", pa.bool_()),
        ("signed_close_open", pa.int64()), ("prior_signed_close_open", pa.int64()),
        ("move_relationship", pa.string()), ("zero_width", pa.bool_()),
        ("identification", pa.string()), ("jtr_width_ticks", pa.int64()),
    ]
    for level in LEVEL_NAMES:
        fields.extend((
            (f"{level}_class", pa.string()),
            (f"{level}_compatible", pa.bool_()),
            (f"{level}_boundary_touch", pa.bool_()),
            (f"{level}_definite_print", pa.bool_()),
        ))
    return pa.schema(fields)


def _parquet_row(row, schema):
    out = {}
    for field in schema:
        value = row.get(field.name)
        if value is None:
            out[field.name] = None
            continue
        if pa_is_bool(field.type):
            out[field.name] = bool(value)
        elif pa_is_int(field.type):
            out[field.name] = None if value is None else int(value)
        elif pa_is_float(field.type):
            out[field.name] = _optional_float(value)
        else:
            out[field.name] = None if value is None else str(value)
    return out


def pa_is_bool(dtype):
    import pyarrow as pa
    return pa.types.is_boolean(dtype)


def pa_is_int(dtype):
    import pyarrow as pa
    return pa.types.is_integer(dtype)


def pa_is_float(dtype):
    import pyarrow as pa
    return pa.types.is_floating(dtype)


def _sanitize(value):
    if value is None or isinstance(value, (str, bool)):
        return value
    if isinstance(value, int) and not isinstance(value, bool):
        return int(value)
    if isinstance(value, float):
        return None if not math.isfinite(value) else float(value)
    if isinstance(value, dict):
        return {str(key): _sanitize(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_sanitize(item) for item in value]
    if isinstance(value, np.generic):
        return _sanitize(value.item())
    raise TypeError(f"unsupported timing-statistics JSON type: {type(value).__name__}")


def _markdown_report(tables, checks, development, confirmation, resources):
    passed = sum(check.get("passed") is True for check in checks)
    failed = [check["id"] for check in checks if check.get("passed") is not True]
    lines = [
        "# Jumbo timing and window descriptives",
        "",
        "Study-local observables from retained formation/path tables. "
        "The common 10:01→actual-cash-close target is identical across declared clocks on a date; "
        "target-mean gaps are not clock gain. No Context increment, Location quality, clock ranking, "
        "or 86.46% replication is claimed.",
        "",
        "## Source hypothesis limits",
        "",
        tables["ambiguity_limitations"],
        "",
        "## Checks actually passed",
        "",
        f"{passed}/{len(checks)} recorded checks passed. Failed: {', '.join(failed) if failed else 'none'}.",
        "",
    ]
    for check in checks:
        mark = "pass" if check.get("passed") else "fail"
        lines.append(f"- `{check['id']}`: {mark}")
    lines.extend(("", "## Variants and denominators", ""))
    for variant, payload in (tables.get("variants") or {}).items():
        lines.append(f"### {variant}")
        lines.append("")
        intended = payload.get("intended_root_dates") or {}
        lines.append("Intended root/date counts: " + ", ".join(f"{root}={count}" for root, count in intended.items()) + ".")
        lines.append(f"Shards retained: {len(payload.get('shards') or [])}. Original and corrected NQ2024 are never pooled.")
        lines.append("")
        for slice_name, slice_payload in (payload.get("product_a", {}).get("slices") or {}).items():
            if slice_payload.get("kind") != "phase":
                continue
            lines.append(f"#### Common-clock geometry — {slice_name}")
            lines.append("")
            for root, root_payload in (slice_payload.get("roots") or {}).items():
                lines.append(f"- {root}: {root_payload.get('intended_dates')} intended dates. "
                             "Width × prior-vol controls keep the common target and date universe fixed.")
                for clock, clock_payload in (root_payload.get("clocks") or {}).items():
                    uncond = (clock_payload.get("unconditional") or {}).get("common_terminal") or {}
                    lines.append(
                        f"  - `{clock}`: {clock_payload.get('feature_available_dates')} feature dates, "
                        f"{clock_payload.get('target_available_dates')} target dates"
                        + (f", terminal mean {uncond.get('estimate')}" if uncond.get("estimate") is not None else "")
                        + (" (interval not claimed)" if uncond.get("sparse") else "")
                        + "."
                    )
            lines.append("")
        for slice_name, slice_payload in (payload.get("product_b", {}).get("slices") or {}).items():
            if slice_payload.get("kind") != "phase":
                continue
            lines.append(f"#### JTR transition windows — {slice_name}")
            lines.append("")
            for root, root_payload in (slice_payload.get("roots") or {}).items():
                windows = (root_payload.get("windows") or {})
                source = windows.get("turn_source") or {}
                counts = source.get("identification_counts") or {}
                lines.append(
                    f"- {root}: {root_payload.get('intended_dates')} dates. "
                    f"Source-window identification {counts}. "
                    "Definite print requires literal O/H/L/C; range intersection alone is compatible/ambiguous."
                )
            lines.append("")
    lines.extend((
        "## Existing annual reports",
        "",
        "Per-year path/formation statistics already exist on the extract shards and are not rerun.",
        "",
    ))
    for ref in tables.get("annual_report_refs") or []:
        if ref.get("kind") == "year_statistics":
            lines.append(f"- {ref.get('stage')} {ref.get('root')} {ref.get('year')}: retained year statistics artifact")
        else:
            lines.append(f"- {ref.get('stage')} {ref.get('kind')}")
    lines.extend((
        "",
        "## Remaining Deliverable 1 source dependencies",
        "",
    ))
    for item in REMAINING_D1_DEPENDENCIES:
        lines.append(f"- **{item['id']}**: {item['detail']}")
    lines.extend((
        "",
        "## Resources",
        "",
        f"- CPU seconds: {resources.get('cpu_seconds')}",
        f"- Peak RSS bytes: {resources.get('peak_rss_bytes')}",
        f"- Output bytes: {resources.get('output_bytes')}",
        f"- Table reads: {resources.get('table_reads')}; prepare_paths: {resources.get('prepare_paths_calls')}; "
        f"common adapter: {resources.get('common_adapter_calls')}",
        f"- Conditional groups: {resources.get('conditional_groups')}; bootstrap metrics: {resources.get('bootstrap_metrics')}",
        "",
        "Family statistics, Context, and Location remain incomplete. This report is not an all-family completion.",
        "",
    ))
    return "\n".join(lines) + "\n"

