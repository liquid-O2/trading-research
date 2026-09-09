"""Pure bounded M02 adaptive/soft cohort consumer for Deliverable 1.

Root owns registration, IO, source admission, full-population statistics
and acceptance. This module consumes one authenticated TRADE table and
observation table for a single source/date unit. It does not scan raw
files, admit F11 serving, fit Context, or evaluate Locations.

Frozen measurement definitions (distinct IDs):

* ``fixed_all``, ``ny_ge100``, ``london_ge75``, ``inclusive30_through60``
* training-only ``equal_count_quartiles``, ``equal_volume_quartiles``
* source top-35% ``source_top35_count_quantile`` (13/20) and the separately
  named ``source_top35_volume_quantile_sensitivity`` (weighting is not
  identified by JXA-13; neither variant is asserted to reproduce a chart)
* fixed continuous soft basis ``soft_piecewise_linear_knots`` at
  (1, 30, 60, 75, 100, 250) with endpoint continuation and partition sum 1

Preflight ``SOFT_KNOTS=(1, 30, 61, 75, 100)`` is a performance fixture, not
a scientific requirement. Thresholds are never rebucketed after a later fit.
Aggregation unit is the provider-reported eligible trade row. Coverage is
taken from observation flags, never inferred from eligible print counts.
"""
from __future__ import annotations

from collections import deque
from datetime import datetime, timedelta, timezone
from fractions import Fraction

from trading_research.errors import ContractError, DependencyUnavailable, IntegrityError
from trading_research.foundations.time import MINUTE, NS, timestamp
from trading_research.measurements.common import bounded_name
from trading_research.measurements.cvd import CohortChannel, CohortDefinition, exact_number, fixed_source_cohort
from trading_research.operations.artifacts import digest, json_value
from trading_research.research.auction_flow_cohorts import (
    BATCH_ROWS,
    DEFAULT_DISTINCT_SIZES,
    VERSION as KERNEL_VERSION,
    CohortWindow,
    TradeSizeHistogram,
    complete_histogram_report,
    fit_unpublished_cohort_definition,
    merge_histogram_reports,
)
from trading_research.research.auction_flow_window_links import (
    CUT_CADENCE_NS,
    FORMATION_MINUTES,
    MAX_CUT_SPAN_NS,
    MAX_INSTRUMENTS,
    SOURCE_LATENCY_NS,
    join_window_eligibility,
    _frozen_stage_intervals,
    _stage_pair,
    _validate_cuts,
    _validate_source_identity,
)
from trading_research.research.auction_flow_windows import TRADE_FIELDS, prepare_trade_batch


VERSION = "auction-flow-adaptive-soft-cohort-measurements-v1"
AGGREGATION_UNIT = "provider-reported-trade-record"
SOFT_KNOTS = (1, 30, 60, 75, 100, 250)
FIXED_FILTER_NAMES = ("fixed_all", "ny_ge100", "london_ge75", "inclusive30_through60")
OVERLAPPING_SOURCE_FILTERS = ("ny_ge100", "london_ge75", "inclusive30_through60")
ADAPTIVE_RECIPES = (
    ("equal_count_quartiles", "count", (Fraction(1, 4), Fraction(1, 2), Fraction(3, 4))),
    ("equal_volume_quartiles", "volume", (Fraction(1, 4), Fraction(1, 2), Fraction(3, 4))),
    ("source_top35_count_quantile", "count", (Fraction(13, 20),)),
    ("source_top35_volume_quantile_sensitivity", "volume", (Fraction(13, 20),)),
)
DEFAULT_AVAILABLE_AT_NS = {
    "NQ": datetime(2023, 1, 1, tzinfo=timezone.utc),
    "ES": datetime(2021, 1, 1, tzinfo=timezone.utc),
}
_UNPUBLISHED = "unpublished mathematical calculations"
_TIE_POLICY = "lower_bin_then_merge_empty"
_INT64_MIN = -(2 ** 63)
_INT64_MAX = 2 ** 63 - 1
_SHA_LEN = 64
_MAX_FORMATION_MINUTES = 240
_OBS_REQUIRED = (
    "root", "source_path", "source_metadata_sha256", "source_variant",
    "instrument_id", "contract_key", "event_start_ns", "event_end_ns", "known_at_ns",
    "source_coverage_complete", "coordinate_complete", "flow_history_complete",
    "empty_observed_window", "source_instrument_presence",
)
_FRACTION_FIELDS = (
    "open", "high", "low", "close", "buy", "sell", "unknown", "volume", "signed",
    "weighted_prints", "count_occupancy", "volume_occupancy",
    "observed_signed_lower", "observed_signed_upper",
    "true_signed_lower", "true_signed_upper",
)
_NULL_INTS = (
    "high_at_ns", "low_at_ns", "high_source_order", "low_source_order",
    "definition_available_at", "fit_recipe_id",
)
scientific_join_eligibility = join_window_eligibility


def default_available_at_ns(root):
    """Documented NQ 2023-01-01T00Z / ES 2021-01-01T00Z availability instants."""
    if root not in DEFAULT_AVAILABLE_AT_NS:
        raise ContractError("default availability is defined only for NQ and ES")
    delta = DEFAULT_AVAILABLE_AT_NS[root] - datetime(1970, 1, 1, tzinfo=timezone.utc)
    return timestamp((delta.days * 86400 + delta.seconds) * NS)


def default_train_end_ns(root):
    """Inclusive training closure equals the documented availability instant."""
    return default_available_at_ns(root)


def _pa():
    import pyarrow as pa
    return pa


def _text(value, *, what, allow_empty=False):
    if type(value) is not str or (not value and not allow_empty):
        raise IntegrityError(f"{what} must be a concrete string")
    return value


def _bool(value, *, what):
    if type(value) is not bool:
        raise IntegrityError(f"{what} must be an explicit boolean")
    return value


def _int(value, *, what, minimum=_INT64_MIN, maximum=_INT64_MAX):
    if type(value) is bool or type(value) is not int:
        raise IntegrityError(f"{what} must be an exact integer")
    if not minimum <= value <= maximum:
        raise IntegrityError(f"{what} exceeds the exact int64 domain")
    return value


def _require_table(table, *, what, names):
    pa = _pa()
    if not isinstance(table, pa.Table):
        raise ContractError(f"{what} must be a PyArrow table")
    missing = [name for name in names if name not in table.schema.names]
    if missing:
        raise ContractError(f"{what} lost required columns {missing[:8]}")
    return table


def _utc_date(event_ns):
    seconds, _ = divmod(timestamp(event_ns), NS)
    return (datetime(1970, 1, 1, tzinfo=timezone.utc) + timedelta(seconds=seconds)).date().isoformat()


def _fraction_pair(value):
    if value is None:
        return None, None
    number = exact_number(value)
    return int(number.numerator), int(number.denominator)


def _approx(value):
    if value is None:
        return None
    return float(exact_number(value))


def _empty_fraction():
    return Fraction(0)


def validate_source_identity(source_identity):
    """Window-link identity plus the unit source_key and source_collection."""
    identity = dict(_validate_source_identity(source_identity))
    rec = source_identity if isinstance(source_identity, dict) else {}
    identity["source_key"] = _text(rec.get("source_key"), what="source_identity.source_key")
    identity["source_collection"] = _text(
        rec.get("source_collection"), what="source_identity.source_collection")
    if rec.get("economic_date") is not None:
        identity["economic_date"] = _text(rec.get("economic_date"), what="source_identity.economic_date")
    return identity


def frozen_fixed_definitions(*, aggregation_unit=AGGREGATION_UNIT):
    """Distinct fixed occupancy/all/soft measurement definitions. No fit."""
    bounded_name(aggregation_unit)
    if aggregation_unit != AGGREGATION_UNIT:
        raise ContractError("cohorts are provider-reported eligible trade-row aggregates")
    all_flow = CohortDefinition("fixed_all", aggregation_unit, (CohortChannel("all", 1, None),))
    filters = {name: fixed_source_cohort(name, aggregation_unit=aggregation_unit)
               for name in ("ny_ge100", "london_ge75", "inclusive30_through60")}
    soft = CohortDefinition("soft_piecewise_linear_knots", aggregation_unit, (), SOFT_KNOTS)
    return {
        "fixed_all": {"name": "fixed_all", "kind": "fixed_source", "definition": all_flow,
                      "unavailable": None, "partition": True, "family_occupancy_only": False},
        "ny_ge100": {"name": "ny_ge100", "kind": "fixed_source", "definition": filters["ny_ge100"],
                     "unavailable": None, "partition": False, "family_occupancy_only": True},
        "london_ge75": {"name": "london_ge75", "kind": "fixed_source",
                        "definition": filters["london_ge75"],
                        "unavailable": None, "partition": False, "family_occupancy_only": True},
        "inclusive30_through60": {
            "name": "inclusive30_through60", "kind": "fixed_source",
            "definition": filters["inclusive30_through60"],
            "unavailable": None, "partition": False, "family_occupancy_only": True},
        "soft_piecewise_linear_knots": {
            "name": "soft_piecewise_linear_knots", "kind": "fixed_soft", "definition": soft,
            "unavailable": None, "partition": True, "family_occupancy_only": False},
    }


def serialize_definition(definition):
    """Deterministic JSON-like payload with integer/Fraction identity support."""
    if type(definition) is not CohortDefinition:
        raise ContractError("typed frozen cohort definition required")
    payload = {
        "id": definition.id,
        "version": definition.version,
        "aggregation_unit": definition.aggregation_unit,
        "channels": tuple(
            {"id": c.id, "lower_inclusive": c.lower_inclusive,
             "upper_exclusive": c.upper_exclusive, "role": c.role}
            for c in definition.channels),
        "knots": definition.knots,
        "partition": definition.partition,
        "origin": definition.origin,
        "available_at": definition.available_at,
        "fit_recipe_id": definition.fit_recipe_id,
    }
    return json_value(payload)


def serialize_fit_evidence(fit):
    """Deterministic unpublished fit evidence. Never an F11 serving admission."""
    if type(fit) is not dict:
        raise ContractError("fit evidence must be the unpublished kernel payload")
    definition = fit.get("definition")
    payload = {
        "definition": None if definition is None else serialize_definition(definition),
        "recipe": fit.get("recipe"),
        "realized_count": fit.get("realized_count"),
        "realized_volume": fit.get("realized_volume"),
        "realized_count_occupancy": fit.get("realized_count_occupancy"),
        "realized_volume_occupancy": fit.get("realized_volume_occupancy"),
        "histogram_identity": fit.get("histogram_identity"),
        "source_manifest": fit.get("source_manifest"),
        "fold_manifest": fit.get("fold_manifest"),
        "publication_status": "unpublished",
        "admitted_for_serving": False,
        "output_kind": _UNPUBLISHED,
        "fitted_boundary_kind": fit.get("fitted_boundary_kind", "unpublished_training_quantile"),
        "tie_policy": _TIE_POLICY,
        "kernel_version": KERNEL_VERSION,
    }
    encoded = json_value(payload)
    encoded["identity"] = digest(encoded)
    return encoded


def cohort_row_schema():
    """Compact definition/channel/formation schema. Clocks stay int64."""
    pa = _pa()

    def i64(name, nullable=False):
        return pa.field(name, pa.int64(), nullable=nullable)

    def f64(name):
        return pa.field(name, pa.float64(), nullable=True)

    def flag(name):
        return pa.field(name, pa.bool_(), nullable=False)

    def text(name, nullable=False):
        return pa.field(name, pa.string(), nullable=nullable)

    fields = [
        text("root"), text("source_path"), text("source_key"), text("source_collection"),
        text("source_metadata_sha256"), text("source_variant"),
        i64("acquired_event_start_ns"), i64("acquired_event_end_ns"),
        i64("instrument_id"), text("contract_key", nullable=True),
        i64("formation_minutes"), i64("cut_ns"),
        i64("event_start_ns"), i64("event_end_ns"), i64("known_at_ns"),
        text("formation_id"), text("economic_date"),
        text("stage"), flag("stage_boundary"),
        text("definition_name"), text("definition_id"), text("definition_version"),
        text("definition_origin"), i64("definition_available_at", nullable=True),
        text("fit_recipe_id", nullable=True), text("aggregation_unit"),
        flag("partition"), flag("family_occupancy_only"),
        text("channel_id", nullable=True), text("channel_role", nullable=True),
        flag("unavailable"), text("unavailable_reason", nullable=True),
        flag("missing_window"), flag("empty_observed_window"), flag("empty_observed_channel"),
        flag("source_coverage_complete"), flag("coordinate_complete"),
        flag("flow_history_complete"), flag("atoms_complete"), flag("prefix_complete"),
        i64("prints", nullable=True), i64("volume", nullable=True),
        i64("contributing_prints", nullable=True),
        i64("open_numerator", nullable=True), i64("open_denominator", nullable=True),
        i64("high_numerator", nullable=True), i64("high_denominator", nullable=True),
        i64("low_numerator", nullable=True), i64("low_denominator", nullable=True),
        i64("close_numerator", nullable=True), i64("close_denominator", nullable=True),
        i64("buy_numerator", nullable=True), i64("buy_denominator", nullable=True),
        i64("sell_numerator", nullable=True), i64("sell_denominator", nullable=True),
        i64("unknown_numerator", nullable=True), i64("unknown_denominator", nullable=True),
        i64("volume_numerator", nullable=True), i64("volume_denominator", nullable=True),
        i64("signed_numerator", nullable=True), i64("signed_denominator", nullable=True),
        i64("weighted_prints_numerator", nullable=True),
        i64("weighted_prints_denominator", nullable=True),
        i64("count_occupancy_numerator", nullable=True),
        i64("count_occupancy_denominator", nullable=True),
        i64("volume_occupancy_numerator", nullable=True),
        i64("volume_occupancy_denominator", nullable=True),
        i64("observed_signed_lower_numerator", nullable=True),
        i64("observed_signed_lower_denominator", nullable=True),
        i64("observed_signed_upper_numerator", nullable=True),
        i64("observed_signed_upper_denominator", nullable=True),
        i64("true_signed_lower_numerator", nullable=True),
        i64("true_signed_lower_denominator", nullable=True),
        i64("true_signed_upper_numerator", nullable=True),
        i64("true_signed_upper_denominator", nullable=True),
        f64("open_approx"), f64("high_approx"), f64("low_approx"), f64("close_approx"),
        f64("buy_approx"), f64("sell_approx"), f64("unknown_approx"),
        f64("volume_approx"), f64("signed_approx"), f64("weighted_prints_approx"),
        i64("high_at_ns", nullable=True), i64("low_at_ns", nullable=True),
        i64("high_source_order", nullable=True), i64("low_source_order", nullable=True),
        text("high_origin", nullable=True), text("low_origin", nullable=True),
    ]
    return pa.schema(fields)


def cohort_column_names():
    return tuple(field.name for field in cohort_row_schema())


def _empty_table(schema):
    pa = _pa()
    return pa.table({field.name: pa.array([], type=field.type) for field in schema}, schema=schema)


def _table_from_rows(schema, rows):
    pa = _pa()
    names = [field.name for field in schema]
    if not rows:
        return _empty_table(schema)
    if any(set(row) != set(names) for row in rows):
        raise IntegrityError("cohort row columns must match the explicit schema exactly")
    return pa.table(
        {name: pa.array([row[name] for row in rows], type=schema.field(name).type) for name in names},
        schema=schema,
    )


def _member_window(record):
    if type(record) is not dict:
        raise ContractError("training member windows must be explicit complete records")
    end, published_at, complete = record.get("end"), record.get("published_at"), record.get("history_complete")
    timestamp(end)
    timestamp(published_at)
    if type(complete) is not bool or published_at < end:
        raise ContractError("training member windows must be explicit complete records")
    return end, published_at, complete


def _observation_index(observations, identity):
    import numpy as np

    table = _require_table(observations, what="observations", names=_OBS_REQUIRED)
    if not len(table):
        return {"instruments": (), "by_instrument": {}, "arrays": None}
    roots = set(table["root"].to_pylist())
    paths = set(table["source_path"].to_pylist())
    shas = set(table["source_metadata_sha256"].to_pylist())
    variants = set(table["source_variant"].to_pylist())
    if roots != {identity["root"]} or paths != {identity["source_path"]}:
        raise IntegrityError("observations cannot join a different root or physical source file")
    if shas != {identity["source_metadata_sha256"]} or variants != {identity["source_variant"]}:
        raise IntegrityError("observation source identity does not join source_identity")
    starts = np.asarray(table["event_start_ns"].to_pylist(), dtype=object)
    ends = np.asarray(table["event_end_ns"].to_pylist(), dtype=object)
    instrument_id = np.asarray(table["instrument_id"].to_pylist(), dtype=object)
    if any(type(v) is not int for v in starts) or any(type(v) is not int for v in ends):
        raise IntegrityError("observation clocks must be exact integers")
    if any(type(v) is not int or v <= 0 for v in instrument_id):
        raise IntegrityError("instrument_id must be a positive raw identifier")
    starts = np.array([int(v) for v in starts], dtype=np.int64)
    ends = np.array([int(v) for v in ends], dtype=np.int64)
    instrument_id = np.array([int(v) for v in instrument_id], dtype=np.int64)
    if np.any(ends <= starts):
        raise IntegrityError("observation atoms must be positive half-open intervals")
    unique = tuple(int(v) for v in np.unique(instrument_id))
    if len(unique) > MAX_INSTRUMENTS:
        raise ContractError("cohort input cannot exceed eight instruments")
    arrays = {
        "event_start": starts,
        "event_end": ends,
        "instrument_id": instrument_id,
        "contract_key": table["contract_key"].to_pylist(),
        "known_at_ns": np.array([int(v) for v in table["known_at_ns"].to_pylist()], dtype=np.int64),
        "source_coverage_complete": np.array(table["source_coverage_complete"].to_pylist(), dtype=bool),
        "coordinate_complete": np.array(table["coordinate_complete"].to_pylist(), dtype=bool),
        "flow_history_complete": np.array(table["flow_history_complete"].to_pylist(), dtype=bool),
        "empty_observed_window": np.array(table["empty_observed_window"].to_pylist(), dtype=bool),
        "presence": np.array(table["source_instrument_presence"].to_pylist(), dtype=bool),
    }
    grouped = {}
    by_start = {}
    for instrument in unique:
        mask = instrument_id == instrument
        idx = np.flatnonzero(mask)
        order = np.argsort(starts[idx], kind="stable")
        idx = idx[order]
        if np.any(starts[idx][1:] < starts[idx][:-1]):
            raise IntegrityError("observation atoms must be ordered by event_start_ns")
        if np.any(ends[idx][:-1] > starts[idx][1:]):
            raise IntegrityError("observation atoms cannot overlap for one instrument")
        grouped[instrument] = idx
        by_start[instrument] = {int(starts[i]): int(i) for i in idx}
    return {"instruments": unique, "by_instrument": grouped, "by_start": by_start, "arrays": arrays}


def _atom_coverage(arrays, index):
    if index is None:
        return None
    return {
        "contract_key": arrays["contract_key"][index],
        "known_at_ns": int(arrays["known_at_ns"][index]),
        "source_coverage_complete": bool(arrays["source_coverage_complete"][index]),
        "coordinate_complete": bool(arrays["coordinate_complete"][index]),
        "flow_history_complete": bool(arrays["flow_history_complete"][index]),
        "empty_observed_window": bool(arrays["empty_observed_window"][index]),
        "presence": bool(arrays["presence"][index]),
        "event_start_ns": int(arrays["event_start"][index]),
        "event_end_ns": int(arrays["event_end"][index]),
    }


def _unit_complete(obs, instrument_id):
    arrays = obs["arrays"]
    idx = obs["by_instrument"].get(instrument_id)
    if arrays is None or idx is None or len(idx) == 0:
        return False, "missing_observation_atoms"
    if not bool(arrays["source_coverage_complete"][idx].all()):
        return False, "source_coverage_incomplete"
    if not bool(arrays["flow_history_complete"][idx].all()):
        return False, "flow_history_incomplete"
    if not bool(arrays["coordinate_complete"][idx].all()):
        return False, "coordinate_incomplete"
    if not bool(arrays["presence"][idx].all()):
        return False, "source_instrument_absent"
    return True, None


def _unique_source_key(table):
    import pyarrow.compute as pc

    if "source_key" not in table.schema.names or not len(table):
        return None
    keys = pc.unique(table["source_key"]).to_pylist()
    if len(keys) != 1 or type(keys[0]) is not str or not keys[0]:
        raise IntegrityError("a cohort window cannot join distinct acquired source streams")
    return keys[0]


def _filter_instrument(table, instrument_id):
    import pyarrow.compute as pc

    return table.filter(pc.equal(table["instrument_id"], instrument_id))


def _validate_trades(trades, identity):
    table = _require_table(trades, what="trades", names=TRADE_FIELDS)
    if not len(table):
        return table
    key = _unique_source_key(table)
    if key != identity["source_key"]:
        raise IntegrityError("trades cannot join a different source_key")
    return table


def histogram_for_training(
    trades,
    observations,
    source_identity,
    *,
    member_id,
    member_window,
    source_manifest,
    fold_manifest,
    aggregation_unit=AGGREGATION_UNIT,
    complete_pairs=None,
    extra_complete_reports=(),
    excluded_members=(),
    train_end=None,
    maximum_distinct_sizes=DEFAULT_DISTINCT_SIZES,
):
    """Build one unpublished training histogram for a complete source/date unit.

    ``trades`` / ``observations`` are already-authenticated tables. Coverage is
    the observation-flag conjunction, never the eligible print count. Missing
    units stay excluded only with an explicit root-supplied reason. Integer
    ``(size, count)`` pairs from other complete members may be merged without
    expanding prints.
    """
    identity = validate_source_identity(source_identity)
    if aggregation_unit != AGGREGATION_UNIT:
        raise ContractError("cohorts are provider-reported eligible trade-row aggregates")
    bounded_name(member_id)
    end, published_at, complete = _member_window(member_window)
    if train_end is not None:
        timestamp(train_end)
        if end > train_end or published_at > train_end:
            raise ContractError("training member future/duplicate/partial rejection")
    if not complete:
        raise ContractError("training member future/duplicate/partial rejection")
    excluded = []
    seen_excluded = set()
    for item in excluded_members or ():
        if type(item) is not dict or type(item.get("member_id")) is not str or type(item.get("reason")) is not str:
            raise ContractError("excluded members need explicit member_id and reason")
        if item["member_id"] in seen_excluded or item["member_id"] == member_id:
            raise ContractError("training member future/duplicate/partial rejection")
        seen_excluded.add(item["member_id"])
        excluded.append({"member_id": item["member_id"], "reason": item["reason"]})
    obs = _observation_index(observations, identity)
    table = _validate_trades(trades, identity)
    instruments = obs["instruments"]
    if not instruments:
        raise ContractError("training member future/duplicate/partial rejection")
    reasons = []
    for instrument in instruments:
        ok, reason = _unit_complete(obs, instrument)
        if not ok:
            reasons.append({"instrument_id": instrument, "reason": reason})
    if reasons:
        raise ContractError("training member future/duplicate/partial rejection")
    histogram = TradeSizeHistogram(
        source_manifest=source_manifest, fold_manifest=fold_manifest,
        aggregation_unit=aggregation_unit, maximum_distinct_sizes=maximum_distinct_sizes)
    try:
        if complete_pairs is not None:
            pair_report = complete_histogram_report(
                pairs=complete_pairs, member_ids=(member_id,), source_manifest=source_manifest,
                fold_manifest=fold_manifest, coverage_complete=True, aggregation_unit=aggregation_unit)
            histogram.merge_complete(pair_report)
        else:
            saw_prints = False
            if len(table):
                for instrument in instruments:
                    kept = _filter_instrument(table, instrument)
                    if not len(kept):
                        continue
                    saw_prints = True
                    for offset in range(0, len(kept), BATCH_ROWS):
                        with prepare_trade_batch(kept.slice(offset, BATCH_ROWS)) as prepared:
                            histogram.add_prepared(prepared, 0, len(prepared), member_id=member_id)
            if not saw_prints:
                histogram.add_sizes([], member_id=member_id)
        for report in extra_complete_reports or ():
            histogram.merge_complete(report)
        coverage_complete = True
        report = histogram.record(coverage_complete=coverage_complete)
    finally:
        histogram.close()
    return {
        "report": report,
        "member_id": member_id,
        "member_window": {"end": end, "published_at": published_at, "history_complete": True},
        "excluded_members": tuple(excluded),
        "instrument_ids": instruments,
        "source_identity": identity,
        "aggregation_unit": aggregation_unit,
        "coverage_complete": True,
        "coverage_inferred_from_prints": False,
        "publication_status": "unpublished",
        "admitted_for_serving": False,
        "kernel_version": KERNEL_VERSION,
        "version": VERSION,
    }


def fit_definitions(
    histogram_report,
    *,
    train_end,
    available_at,
    member_identities,
    member_windows,
    aggregation_unit=AGGREGATION_UNIT,
    source_collection=None,
    root=None,
):
    """Fit the frozen adaptive family on one complete unpublished histogram.

    Fixed and soft definitions are constants. Adaptive boundaries use the
    existing size+1 tie policy and collapse equal thresholds. Root supplies
    the actual train_end / available_at; documented NQ/ES closures are
    helpers only. No F11 serving admission is emitted.
    """
    timestamp(train_end)
    timestamp(available_at)
    if available_at < train_end:
        raise ContractError("cohort fit requires historical rows, availability and weighting")
    if aggregation_unit != AGGREGATION_UNIT:
        raise ContractError("cohorts are provider-reported eligible trade-row aggregates")
    if source_collection is not None:
        bounded_name(source_collection)
    if root is not None and root not in ("NQ", "ES"):
        raise ContractError("source_identity.root must be NQ or ES")
    frozen = frozen_fixed_definitions(aggregation_unit=aggregation_unit)
    adaptive = {}
    unavailable = {}
    fits = {}
    report = histogram_report
    if type(histogram_report) is dict and "report" in histogram_report and "histogram" not in histogram_report:
        report = histogram_report["report"]
    for name, weighting, probabilities in ADAPTIVE_RECIPES:
        try:
            fitted = fit_unpublished_cohort_definition(
                report, train_end=train_end, available_at=available_at,
                member_identities=member_identities, aggregation_unit=aggregation_unit,
                probabilities=probabilities, weighting=weighting, version=name,
                member_windows=member_windows)
        except ContractError as exc:
            adaptive[name] = {
                "name": name, "kind": "adaptive", "definition": None,
                "unavailable": str(exc) or "unavailable_adaptive_fit",
                "partition": True, "family_occupancy_only": False,
            }
            unavailable[name] = adaptive[name]["unavailable"]
            continue
        adaptive[name] = {
            "name": name, "kind": "adaptive", "definition": fitted["definition"],
            "unavailable": None, "partition": True, "family_occupancy_only": False,
        }
        fits[name] = fitted
        unavailable[name] = None
    definitions = {**frozen, **adaptive}
    serialized = {name: None if item["definition"] is None else serialize_definition(item["definition"])
                  for name, item in definitions.items()}
    evidence = {name: serialize_fit_evidence(fit) for name, fit in fits.items()}
    return {
        "definitions": definitions,
        "fits": fits,
        "serialized_definitions": serialized,
        "serialized_fit_evidence": evidence,
        "unavailable": unavailable,
        "train_end": train_end,
        "available_at": available_at,
        "aggregation_unit": aggregation_unit,
        "source_collection": source_collection,
        "root": root,
        "publication_status": "unpublished",
        "admitted_for_serving": False,
        "output_kind": _UNPUBLISHED,
        "tie_policy": _TIE_POLICY,
        "version": VERSION,
        "kernel_version": KERNEL_VERSION,
    }


def _plan_from_definitions(definitions):
    if type(definitions) is dict and "definitions" in definitions and "fixed_all" in definitions.get("definitions", {}):
        return definitions["definitions"]
    if type(definitions) is dict and all(type(v) is dict and "definition" in v for v in definitions.values()):
        return definitions
    if type(definitions) is dict and all(v is None or type(v) is CohortDefinition for v in definitions.values()):
        out = {}
        for name, definition in definitions.items():
            kind = "adaptive" if definition is not None and definition.origin == "fitted" else (
                "fixed_soft" if definition is not None and definition.knots else "fixed_source")
            out[name] = {
                "name": name, "kind": kind, "definition": definition,
                "unavailable": None if definition is not None else "unavailable_missing_definition",
                "partition": False if name in OVERLAPPING_SOURCE_FILTERS else True,
                "family_occupancy_only": name in OVERLAPPING_SOURCE_FILTERS,
            }
        return out
    raise ContractError("definitions must be the fit_definitions payload or an explicit name map")


def compose_cohort_records(left, right):
    """Associative composition of two consecutive relative (open-zero) records."""
    if left is None:
        return right
    if right is None:
        return left
    if left.get("missing_window") or right.get("missing_window"):
        missing = dict(left)
        missing["missing_window"] = True
        missing["prefix_complete"] = False
        missing["atoms_complete"] = False
        missing["source_coverage_complete"] = False
        missing["flow_history_complete"] = False
        missing["empty_observed_window"] = False
        return missing
    if left.get("unavailable") or right.get("unavailable"):
        reason = left.get("unavailable_reason") or right.get("unavailable_reason")
        return {
            **left,
            "unavailable": True,
            "unavailable_reason": reason or "unavailable_before_training_availability",
            "missing_window": False,
            "event_start_ns": left["event_start_ns"],
            "event_end_ns": right["event_end_ns"],
            "prefix_complete": False,
            "atoms_complete": False,
            "source_coverage_complete": False,
            "flow_history_complete": False,
        }
    if left["channel_id"] != right["channel_id"]:
        raise IntegrityError("composed cohort atoms must share a channel")
    if left["event_end_ns"] != right["event_start_ns"]:
        raise IntegrityError("composed cohort atoms must be contiguous")
    shift = exact_number(left["close"]) - exact_number(left["open"])
    right_open = exact_number(right["open"])
    high_r = shift + (exact_number(right["high"]) - right_open)
    low_r = shift + (exact_number(right["low"]) - right_open)
    close = shift + (exact_number(right["close"]) - right_open)
    high = exact_number(left["high"])
    low = exact_number(left["low"])
    high_at, high_order, high_origin = left["high_at_ns"], left["high_source_order"], left["high_origin"]
    low_at, low_order, low_origin = left["low_at_ns"], left["low_source_order"], left["low_origin"]
    if high_r > high:
        high, high_at, high_order, high_origin = (
            high_r, right["high_at_ns"], right["high_source_order"], right["high_origin"])
    if low_r < low:
        low, low_at, low_order, low_origin = (
            low_r, right["low_at_ns"], right["low_source_order"], right["low_origin"])
    buy = exact_number(left["buy"]) + exact_number(right["buy"])
    sell = exact_number(left["sell"]) + exact_number(right["sell"])
    unknown = exact_number(left["unknown"]) + exact_number(right["unknown"])
    weighted = exact_number(left["weighted_prints"]) + exact_number(right["weighted_prints"])
    prints = left["prints"] + right["prints"]
    volume = left["volume"] + right["volume"]
    contributing = left["contributing_prints"] + right["contributing_prints"]
    signed = buy - sell
    history = (left["source_coverage_complete"] and right["source_coverage_complete"]
               and left["prefix_complete"] and right["prefix_complete"]
               and left["atoms_complete"] and right["atoms_complete"])
    return {
        "channel_id": left["channel_id"],
        "channel_role": left["channel_role"],
        "open": exact_number(left["open"]),
        "high": high,
        "low": low,
        "close": close,
        "high_at_ns": high_at,
        "low_at_ns": low_at,
        "high_source_order": high_order,
        "low_source_order": low_order,
        "high_origin": high_origin,
        "low_origin": low_origin,
        "buy": buy,
        "sell": sell,
        "unknown": unknown,
        "volume": buy + sell + unknown,
        "signed": signed,
        "weighted_prints": weighted,
        "contributing_prints": contributing,
        "prints": prints,
        "window_volume": volume,
        "count_occupancy": (weighted / prints) if prints else None,
        "volume_occupancy": ((buy + sell + unknown) / volume) if volume else None,
        "observed_signed_lower": signed - unknown,
        "observed_signed_upper": signed + unknown,
        "true_signed_lower": (signed - unknown) if history else None,
        "true_signed_upper": (signed + unknown) if history else None,
        "empty_observed_channel": history and contributing == 0,
        "empty_observed_window": history and prints == 0,
        "source_coverage_complete": history,
        "coordinate_complete": left["coordinate_complete"] and right["coordinate_complete"],
        "flow_history_complete": history,
        "atoms_complete": left["atoms_complete"] and right["atoms_complete"],
        "prefix_complete": left["prefix_complete"] and right["prefix_complete"],
        "missing_window": False,
        "unavailable": False,
        "unavailable_reason": None,
        "event_start_ns": left["event_start_ns"],
        "event_end_ns": right["event_end_ns"],
        "contract_key": left["contract_key"] if left["contract_key"] == right["contract_key"] else None,
        "definition_name": left["definition_name"],
        "definition": left.get("definition"),
        "plan": left.get("plan"),
    }


def _channel_from_record(record, channel, *, coverage, plan, definition_name, start_ns, end_ns):
    history = bool(coverage["source_coverage_complete"] and coverage["prefix_complete"]
                   and coverage["atoms_complete"])
    return {
        "channel_id": channel["channel_id"],
        "channel_role": channel["role"],
        "open": channel["open"],
        "high": channel["high"],
        "low": channel["low"],
        "close": channel["close"],
        "high_at_ns": channel["high_at_ns"],
        "low_at_ns": channel["low_at_ns"],
        "high_source_order": channel["high_source_order"],
        "low_source_order": channel["low_source_order"],
        "high_origin": channel["high_origin"],
        "low_origin": channel["low_origin"],
        "buy": channel["buy"],
        "sell": channel["sell"],
        "unknown": channel["unknown"],
        "volume": channel["volume"],
        "signed": channel["signed"],
        "weighted_prints": channel["weighted_prints"],
        "contributing_prints": channel["contributing_prints"],
        "prints": record["prints"],
        "window_volume": record["volume"],
        "count_occupancy": channel["count_occupancy"],
        "volume_occupancy": channel["volume_occupancy"],
        "observed_signed_lower": channel["observed_signed_lower"],
        "observed_signed_upper": channel["observed_signed_upper"],
        "true_signed_lower": channel["true_signed_lower"] if history else None,
        "true_signed_upper": channel["true_signed_upper"] if history else None,
        "empty_observed_channel": channel["empty_observed_channel"],
        "empty_observed_window": record["empty_observed_window"],
        "source_coverage_complete": coverage["source_coverage_complete"],
        "coordinate_complete": coverage["coordinate_complete"],
        "flow_history_complete": coverage["flow_history_complete"],
        "atoms_complete": coverage["atoms_complete"],
        "prefix_complete": coverage["prefix_complete"],
        "missing_window": False,
        "unavailable": False,
        "unavailable_reason": None,
        "event_start_ns": start_ns,
        "event_end_ns": end_ns,
        "contract_key": coverage.get("contract_key"),
        "definition_name": definition_name,
        "definition": record.get("definition") or plan.get("definition"),
        "plan": plan,
    }


def _missing_channel(*, plan, definition_name, start_ns, end_ns, contract_key, channel_id, role,
                     reason="missing_observation_atom"):
    return {
        "channel_id": channel_id,
        "channel_role": role,
        "open": None, "high": None, "low": None, "close": None,
        "high_at_ns": None, "low_at_ns": None,
        "high_source_order": None, "low_source_order": None,
        "high_origin": None, "low_origin": None,
        "buy": None, "sell": None, "unknown": None, "volume": None, "signed": None,
        "weighted_prints": None, "contributing_prints": None, "prints": None,
        "window_volume": None, "count_occupancy": None, "volume_occupancy": None,
        "observed_signed_lower": None, "observed_signed_upper": None,
        "true_signed_lower": None, "true_signed_upper": None,
        "empty_observed_channel": False, "empty_observed_window": False,
        "source_coverage_complete": False, "coordinate_complete": False,
        "flow_history_complete": False, "atoms_complete": False, "prefix_complete": False,
        "missing_window": True, "unavailable": False, "unavailable_reason": reason,
        "event_start_ns": start_ns, "event_end_ns": end_ns, "contract_key": contract_key,
        "definition_name": definition_name, "definition": plan.get("definition"), "plan": plan,
    }


def _unavailable_channel(*, plan, definition_name, start_ns, end_ns, contract_key, channel_id, role,
                         reason):
    row = _missing_channel(plan=plan, definition_name=definition_name, start_ns=start_ns,
                           end_ns=end_ns, contract_key=contract_key, channel_id=channel_id,
                           role=role, reason=reason)
    row["missing_window"] = False
    row["unavailable"] = True
    return row


def _channel_specs_for_plan(plan):
    definition = plan.get("definition")
    if definition is None:
        return (("unavailable", "unavailable"),)
    if definition.channels:
        return tuple((c.id, c.role) for c in definition.channels)
    return tuple((f"knot:{knot}", "continuous_size_basis") for knot in definition.knots)


def _record_minute(*, definition, instrument_id, start_ns, end_ns, latency_ns, prepared_slices,
                   coverage, plan, definition_name):
    if coverage is None:
        return [_missing_channel(plan=plan, definition_name=definition_name, start_ns=start_ns,
                                 end_ns=end_ns, contract_key=None, channel_id=channel_id, role=role)
                for channel_id, role in _channel_specs_for_plan(plan)]
    if plan.get("unavailable") or definition is None:
        return [_unavailable_channel(
            plan=plan, definition_name=definition_name, start_ns=start_ns, end_ns=end_ns,
            contract_key=coverage.get("contract_key"), channel_id=channel_id, role=role,
            reason=plan.get("unavailable") or "unavailable_missing_definition")
            for channel_id, role in _channel_specs_for_plan(plan)]
    if definition.origin == "fitted" and definition.available_at is not None and definition.available_at > start_ns:
        return [_unavailable_channel(
            plan=plan, definition_name=definition_name, start_ns=start_ns, end_ns=end_ns,
            contract_key=coverage.get("contract_key"), channel_id=channel_id, role=role,
            reason="unavailable_before_training_availability")
            for channel_id, role in _channel_specs_for_plan(plan)]
    flags = {
        "source_coverage_complete": coverage["source_coverage_complete"],
        "coordinate_complete": coverage["coordinate_complete"],
        "flow_history_complete": coverage["flow_history_complete"],
        "atoms_complete": True,
        "prefix_complete": True,
        "contract_key": coverage.get("contract_key"),
    }
    try:
        window = CohortWindow(
            definition=definition, instrument_id=instrument_id, start_ns=start_ns,
            end_ns=end_ns, latency_ns=latency_ns)
    except DependencyUnavailable:
        return [_unavailable_channel(
            plan=plan, definition_name=definition_name, start_ns=start_ns, end_ns=end_ns,
            contract_key=coverage.get("contract_key"), channel_id=channel_id, role=role,
            reason="unavailable_before_training_availability")
            for channel_id, role in _channel_specs_for_plan(plan)]
    for prepared, left, right in prepared_slices:
        window.add_prepared(prepared, left, right)
    record = window.record(
        source_coverage_complete=coverage["source_coverage_complete"],
        coordinate_complete=coverage["coordinate_complete"])
    if coverage["empty_observed_window"] and record["prints"] != 0:
        raise IntegrityError("empty observed atom cannot contain eligible prints")
    if (not coverage["empty_observed_window"] and record["prints"] == 0
            and coverage["source_coverage_complete"] and coverage["presence"]):
        record = dict(record)
        record["empty_observed_window"] = False
    if plan["name"] in OVERLAPPING_SOURCE_FILTERS:
        record = dict(record)
        record["partition"] = False
    return [_channel_from_record(record, channel, coverage=flags, plan=plan,
                                 definition_name=definition_name, start_ns=start_ns, end_ns=end_ns)
            for channel in record["channels"]]


def _formation_id(identity, instrument_id, contract_key, minutes, start_ns, end_ns, definition_id, channel_id):
    return digest({
        "root": identity["root"], "source_path": identity["source_path"],
        "source_key": identity["source_key"], "source_collection": identity["source_collection"],
        "instrument_id": instrument_id, "contract_key": contract_key,
        "formation_minutes": minutes, "event_start_ns": start_ns, "event_end_ns": end_ns,
        "definition_id": definition_id, "channel_id": channel_id,
    })


def _emit_row(identity, instrument_id, channel, *, minutes, cut_ns, latency_ns, stages, economic_date):
    definition = channel.get("definition")
    plan = channel.get("plan") or {}
    available = None if definition is None else definition.available_at
    known = None
    if not channel.get("unavailable") and not channel.get("missing_window"):
        known = channel["event_end_ns"] + latency_ns
        if available is not None and available > known:
            known = available
    elif channel.get("event_end_ns") is not None:
        known = channel["event_end_ns"] + latency_ns
        if available is not None:
            known = max(known, available)
    start_ns = channel["event_start_ns"]
    end_ns = channel["event_end_ns"]
    if known is None or start_ns is None:
        stage, boundary = "unassigned", False
    else:
        stage, boundary = _stage_pair(identity["root"], start_ns, known, stages)
    date = economic_date or (_utc_date(start_ns) if start_ns is not None else _utc_date(cut_ns))
    definition_id = None if definition is None else definition.id
    row = {
        "root": identity["root"],
        "source_path": identity["source_path"],
        "source_key": identity["source_key"],
        "source_collection": identity["source_collection"],
        "source_metadata_sha256": identity["source_metadata_sha256"],
        "source_variant": identity["source_variant"],
        "acquired_event_start_ns": identity["acquired_event_start_ns"],
        "acquired_event_end_ns": identity["acquired_event_end_ns"],
        "instrument_id": instrument_id,
        "contract_key": channel.get("contract_key"),
        "formation_minutes": minutes,
        "cut_ns": cut_ns,
        "event_start_ns": start_ns,
        "event_end_ns": end_ns,
        "known_at_ns": known,
        "formation_id": _formation_id(
            identity, instrument_id, channel.get("contract_key"), minutes, start_ns, end_ns,
            definition_id, channel.get("channel_id")),
        "economic_date": date,
        "stage": stage,
        "stage_boundary": boundary,
        "definition_name": channel["definition_name"],
        "definition_id": definition_id or "",
        "definition_version": "" if definition is None else definition.version,
        "definition_origin": "" if definition is None else definition.origin,
        "definition_available_at": available,
        "fit_recipe_id": None if definition is None else definition.fit_recipe_id,
        "aggregation_unit": AGGREGATION_UNIT,
        "partition": bool(plan.get("partition", False if channel["definition_name"] in OVERLAPPING_SOURCE_FILTERS
                                   else (definition.partition if definition is not None else False))),
        "family_occupancy_only": bool(plan.get("family_occupancy_only",
                                              channel["definition_name"] in OVERLAPPING_SOURCE_FILTERS)),
        "channel_id": channel.get("channel_id"),
        "channel_role": channel.get("channel_role"),
        "unavailable": bool(channel.get("unavailable")),
        "unavailable_reason": channel.get("unavailable_reason"),
        "missing_window": bool(channel.get("missing_window")),
        "empty_observed_window": bool(channel.get("empty_observed_window")),
        "empty_observed_channel": bool(channel.get("empty_observed_channel")),
        "source_coverage_complete": bool(channel.get("source_coverage_complete")),
        "coordinate_complete": bool(channel.get("coordinate_complete")),
        "flow_history_complete": bool(channel.get("flow_history_complete")),
        "atoms_complete": bool(channel.get("atoms_complete")),
        "prefix_complete": bool(channel.get("prefix_complete")),
        "prints": channel.get("prints"),
        "volume": channel.get("window_volume") if type(channel.get("window_volume")) is int else None,
        "contributing_prints": channel.get("contributing_prints"),
    }
    for name in _FRACTION_FIELDS:
        num, den = _fraction_pair(channel.get(name))
        row[f"{name}_numerator"] = num
        row[f"{name}_denominator"] = den
        row[f"{name}_approx"] = _approx(channel.get(name)) if name in (
            "open", "high", "low", "close", "buy", "sell", "unknown", "volume", "signed",
            "weighted_prints") else None
    for name in ("high_at_ns", "low_at_ns", "high_source_order", "low_source_order"):
        row[name] = channel.get(name)
    row["high_origin"] = channel.get("high_origin")
    row["low_origin"] = channel.get("low_origin")
    return row


def _compose_span(ring, *, start_ns, end_ns):
    selected = [item for item in ring if item["event_start_ns"] >= start_ns and item["event_end_ns"] <= end_ns]
    if not selected:
        return None
    selected.sort(key=lambda item: item["event_start_ns"])
    if selected[0]["event_start_ns"] != start_ns or selected[-1]["event_end_ns"] != end_ns:
        missing = dict(selected[0])
        missing["missing_window"] = True
        missing["prefix_complete"] = False
        missing["atoms_complete"] = False
        missing["source_coverage_complete"] = False
        missing["event_start_ns"] = start_ns
        missing["event_end_ns"] = end_ns
        return missing
    expected = start_ns
    for item in selected:
        if item["event_start_ns"] != expected:
            missing = dict(item)
            missing["missing_window"] = True
            missing["prefix_complete"] = False
            missing["atoms_complete"] = False
            missing["source_coverage_complete"] = False
            missing["event_start_ns"] = start_ns
            missing["event_end_ns"] = end_ns
            return missing
        expected = item["event_end_ns"]
    composed = selected[0]
    for item in selected[1:]:
        composed = compose_cohort_records(composed, item)
    return composed


class _PreparedCursor:
    """Stream one instrument's prepared batches; slices are reused across definitions."""

    def __init__(self, table):
        self._table = table
        self._offset = 0
        self._prepared = None
        self._origin = 0
        self._width = 0
        self._retire = []

    def close(self):
        self.release_retired()
        if self._prepared is not None and not self._prepared.released:
            self._prepared.close()
        self._prepared = None

    def release_retired(self):
        for prepared in self._retire:
            if not prepared.released:
                prepared.close()
        self._retire = []

    def _load(self):
        if self._prepared is not None:
            return True
        if self._offset >= len(self._table):
            return False
        self._width = min(BATCH_ROWS, len(self._table) - self._offset)
        self._origin = self._offset
        self._prepared = prepare_trade_batch(self._table.slice(self._offset, self._width))
        return True

    def slices_for_minute(self, start_ns, end_ns):
        import numpy as np

        found = []
        while self._load():
            prepared = self._prepared
            if not len(prepared):
                self._retire.append(prepared)
                self._prepared = None
                self._offset = self._origin + self._width
                continue
            stamps = prepared.values["t"]
            if int(stamps[-1]) < start_ns:
                self._retire.append(prepared)
                self._prepared = None
                self._offset = self._origin + self._width
                continue
            if int(stamps[0]) >= end_ns:
                break
            left = int(np.searchsorted(stamps, start_ns, side="left"))
            right = int(np.searchsorted(stamps, end_ns, side="left"))
            if right > left:
                found.append((prepared, left, right))
            if int(stamps[-1]) >= end_ns:
                break
            self._retire.append(prepared)
            self._prepared = None
            self._offset = self._origin + self._width
        return found


def build_cohort_tables(
    trades,
    observations,
    definitions,
    source_identity,
    cut_start_ns,
    cut_end_ns,
    *,
    latency_ns=SOURCE_LATENCY_NS,
    economic_date=None,
    formation_minutes=FORMATION_MINUTES,
):
    """One-pass minute paths and 5-minute-cut composed formations.

    Prepared batches are reused across definitions. Minutes start at open
    zero. Longer formations are associative compositions, not a second trade
    pass. Adaptive rows whose start precedes definition availability are
    emitted as unavailable. Memory retains one unit plus at most 240 composed
    minute atoms per definition/channel.
    """
    identity = validate_source_identity(source_identity)
    if economic_date is None:
        economic_date = identity.get("economic_date")
    if type(latency_ns) is not int or not 0 <= latency_ns <= 1_000_000_000:
        raise ContractError("exact raw instrument, bounded event interval and delay scenario required")
    if tuple(formation_minutes) != FORMATION_MINUTES and tuple(formation_minutes) != (5, 15, 60, 240):
        raise ContractError("every declared formation candidate must be retained")
    cut_start, cut_end, cuts = _validate_cuts(cut_start_ns, cut_end_ns, identity)
    if cut_end - cut_start > MAX_CUT_SPAN_NS:
        raise ContractError("cut interval cannot exceed one UTC day")
    cut_set = {int(v) for v in cuts}
    plan = _plan_from_definitions(definitions)
    obs = _observation_index(observations, identity)
    table = _validate_trades(trades, identity)
    stages = _frozen_stage_intervals()
    schema = cohort_row_schema()
    minute_rows = []
    formation_rows = []
    lookback = _MAX_FORMATION_MINUTES * MINUTE
    grid_start = cut_start - lookback
    if grid_start < identity["acquired_event_start_ns"]:
        grid_start = identity["acquired_event_start_ns"]
    grid_start = grid_start - (grid_start % MINUTE)
    grid_end = cut_end
    for instrument in obs["instruments"]:
        arrays = obs["arrays"]
        by_start = obs["by_start"][instrument]
        kept = _filter_instrument(table, instrument) if len(table) else table
        rings = {name: {channel_id: deque(maxlen=_MAX_FORMATION_MINUTES)
                        for channel_id, _ in _channel_specs_for_plan(item)}
                 for name, item in plan.items()}
        cursor = _PreparedCursor(kept)
        try:
            minute = grid_start
            while minute < grid_end:
                end = minute + MINUTE
                coverage = _atom_coverage(arrays, by_start.get(int(minute)))
                if coverage is not None and (
                        coverage["event_start_ns"] != minute or coverage["event_end_ns"] != end):
                    coverage = None
                slices = cursor.slices_for_minute(minute, end)
                if slices and coverage is None:
                    raise IntegrityError("trades without an observation atom")
                for name, item in plan.items():
                    channels = _record_minute(
                        definition=item.get("definition"), instrument_id=instrument,
                        start_ns=int(minute), end_ns=int(end), latency_ns=latency_ns,
                        prepared_slices=slices, coverage=coverage, plan=item,
                        definition_name=name)
                    for channel in channels:
                        rings[name][channel["channel_id"]].append(channel)
                        minute_rows.append(_emit_row(
                            identity, instrument, channel, minutes=1, cut_ns=int(end),
                            latency_ns=latency_ns, stages=stages, economic_date=economic_date))
                cursor.release_retired()
                if int(end) in cut_set:
                    cut = int(end)
                    for minutes in formation_minutes:
                        start = cut - minutes * MINUTE
                        for name, item in plan.items():
                            for channel_id, ring in rings[name].items():
                                composed = _compose_span(ring, start_ns=start, end_ns=cut)
                                if composed is None:
                                    specs = _channel_specs_for_plan(item)
                                    role = next((role for cid, role in specs if cid == channel_id), "included")
                                    composed = _missing_channel(
                                        plan=item, definition_name=name, start_ns=start,
                                        end_ns=cut, contract_key=None, channel_id=channel_id,
                                        role=role)
                                formation_rows.append(_emit_row(
                                    identity, instrument, composed, minutes=minutes,
                                    cut_ns=cut, latency_ns=latency_ns, stages=stages,
                                    economic_date=economic_date))
                minute = end
        finally:
            cursor.close()
    return {
        "minutes": _table_from_rows(schema, minute_rows),
        "formations": _table_from_rows(schema, formation_rows),
        "schema": schema,
        "validation": {
            "version": VERSION,
            "source_identity": identity,
            "cut_start_ns": cut_start,
            "cut_end_ns": cut_end,
            "instrument_ids": list(obs["instruments"]),
            "minute_rows": len(minute_rows),
            "formation_rows": len(formation_rows),
            "coverage_inferred_from_prints": False,
            "admitted_for_serving": False,
            "publication_status": "unpublished",
            "family_complete": False,
        },
        "version": VERSION,
        "family_complete": False,
    }

