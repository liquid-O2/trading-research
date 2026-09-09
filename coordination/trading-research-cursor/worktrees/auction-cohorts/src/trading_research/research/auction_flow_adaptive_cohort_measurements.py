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

Root orchestration: ``histogram_for_training`` per physical unit (source
identity + member window); merge compatible unit reports outside this
helper (NQ 2020-22 vs ES 2020 stay separate source collections); 
``fit_definitions`` once; ``build_cohort_tables`` serves later units with
that frozen plan. Adaptive rows before availability and known source gaps
are retained. One unit may accumulate ~1e5 Arrow rows, not all history.
"""
from __future__ import annotations

from collections import deque
from datetime import datetime, timedelta, timezone
from fractions import Fraction
import math

from trading_research.errors import ContractError, DependencyUnavailable, IntegrityError
from trading_research.foundations.time import MINUTE, NS, timestamp
from trading_research.measurements.common import bounded_name
from trading_research.measurements.cvd import CohortChannel, CohortDefinition, exact_number, fixed_source_cohort
from trading_research.operations.artifacts import digest, json_value
from trading_research.research.auction_flow_cohorts import (
    BATCH_ROWS,
    DEFAULT_DISTINCT_SIZES,
    MAX_ELIGIBLE_SIZE,
    MAX_PRINTS,
    VERSION as KERNEL_VERSION,
    CohortWindow,
    TradeSizeHistogram,
    fit_unpublished_cohort_definition,
)
from trading_research.research.auction_flow_window_links import (
    CUT_CADENCE_NS,
    FORMATION_MINUTES,
    LATENCY_NS,
    MAX_CUT_SPAN_NS,
    MAX_INSTRUMENTS,
    SOURCE_LATENCY_NS,
    join_window_eligibility,
    _frozen_stage_intervals,
    _stage_pair,
    _trade_arrays,
    _validate_cuts,
    _validate_source_identity,
)
from trading_research.research.auction_flow_windows import TRADE_FIELDS, PreparedTradeBatch, prepare_trade_batch


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
_EMPTY_TRAINING = "unavailable_empty_or_missing_eligible_training"
_INT64_MIN = -(2 ** 63)
_INT64_MAX = 2 ** 63 - 1
_SHA_LEN = 64
_MAX_FORMATION_MINUTES = 240
_SOFT_MAX_DENOMINATOR = 870
_DECLARED_UNIT_PRINTS = MAX_PRINTS
_DECLARED_MAX_SIZE = MAX_ELIGIBLE_SIZE
_OBS_REQUIRED = (
    "root", "source_path", "source_metadata_sha256", "source_variant",
    "instrument_id", "contract_key", "event_start_ns", "event_end_ns", "known_at_ns",
    "source_coverage_complete", "coordinate_complete", "flow_history_complete",
    "empty_observed_window", "source_instrument_presence", "prints",
)
_FRACTION_FIELDS = (
    "open", "high", "low", "close", "buy", "sell", "unknown", "volume", "signed",
    "weighted_prints", "count_occupancy", "volume_occupancy",
    "observed_signed_lower", "observed_signed_upper",
    "true_signed_lower", "true_signed_upper",
)
_PATH_FIELDS = (
    "open", "high", "low", "close", "high_at_ns", "low_at_ns",
    "high_source_order", "low_source_order", "high_origin", "low_origin",
)
_MASS_FIELDS = (
    "buy", "sell", "unknown", "volume", "signed", "weighted_prints",
    "contributing_prints", "prints", "window_volume",
    "count_occupancy", "volume_occupancy",
    "observed_signed_lower", "observed_signed_upper",
    "true_signed_lower", "true_signed_upper",
)
_FIT_BINDING = (
    "source_collection", "root", "source_manifest", "fold_manifest",
    "histogram_identity", "train_end", "available_at", "fit_evidence_identity",
)
_IDENTITY_KEYS = (
    "root", "source_path", "source_metadata_sha256", "source_variant",
    "acquired_event_start_ns", "acquired_event_end_ns",
)


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


def _encode_exact_int(value):
    """int64 when it fits; decimal-string sibling otherwise. Same escape as profile."""
    if value is None:
        return None, None
    number = int(value)
    if _INT64_MIN <= number <= _INT64_MAX:
        return number, None
    return None, format(number, "d")


def _checked_add(left, right, *, what):
    if left is None or right is None:
        raise IntegrityError(f"{what} cannot add unknown integers")
    total = int(left) + int(right)
    if not _INT64_MIN <= total <= _INT64_MAX:
        raise IntegrityError(f"{what} exceeds the declared one-unit int64 domain")
    return total


def _fraction_storage(value):
    if value is None:
        return None, None, None, None
    number = exact_number(value)
    numerator = int(number.numerator)
    denominator = int(number.denominator)
    if denominator <= 0:
        raise IntegrityError("exact fraction denominator must stay positive")
    num, num_text = _encode_exact_int(numerator)
    den, den_text = _encode_exact_int(denominator)
    return num, den, num_text, den_text


def _approx(value):
    if value is None:
        return None
    return float(exact_number(value))


def _soft_max_denominator(knots=SOFT_KNOTS):
    maximum = 1
    for index, _knot in enumerate(knots):
        left = knots[index] - knots[index - 1] if index else None
        right = knots[index + 1] - knots[index] if index + 1 < len(knots) else None
        if left and right:
            maximum = max(maximum, math.lcm(left, right))
        else:
            maximum = max(maximum, left or right or 1)
    return maximum


def _typed_i64(column, *, what, nullable=False):
    import numpy as np

    combined = column.combine_chunks() if hasattr(column, "combine_chunks") else column
    if combined.null_count and not nullable:
        raise IntegrityError(f"{what} cannot contain nulls")
    filled = combined.fill_null(0) if combined.null_count else combined
    raw = filled.to_numpy(zero_copy_only=False)
    if raw.dtype.kind == "f":
        raise IntegrityError(f"{what} must be exact integers without float rounding")
    if raw.dtype.kind not in "iu":
        raise IntegrityError(f"{what} must be exact integers")
    if raw.dtype.kind == "u" and raw.itemsize >= 8:
        if raw.size and int(raw.max()) > _INT64_MAX:
            raise IntegrityError(f"{what} exceeds the exact int64 domain")
    return np.array(raw, dtype=np.int64, copy=True)


def _typed_bool(column, *, what):
    import numpy as np

    combined = column.combine_chunks() if hasattr(column, "combine_chunks") else column
    if combined.null_count:
        raise IntegrityError(f"{what} cannot contain nulls")
    values = combined.to_pylist()
    if any(type(item) is not bool for item in values):
        raise IntegrityError(f"{what} must be an explicit boolean")
    return np.array(values, dtype=bool, copy=True)


def _typed_text(column, *, what, allow_null=True):
    values = column.to_pylist()
    out = []
    for item in values:
        if item is None:
            if not allow_null:
                raise IntegrityError(f"{what} cannot contain nulls")
            out.append(None)
            continue
        if type(item) is not str:
            raise IntegrityError(f"{what} must be a string identifier")
        out.append(item)
    return out


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
    if _soft_max_denominator(SOFT_KNOTS) != _SOFT_MAX_DENOMINATOR:
        raise IntegrityError("soft knot denominators no longer match the declared bound")
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
    """Compact definition/channel/formation schema. Clocks stay int64.

    Fraction numerators/denominators use int64 when they fit the declared
    one-unit domain (frozen knots, ``MAX_PRINTS``, ``MAX_ELIGIBLE_SIZE``).
    Soft path numerators may exceed int64; sibling ``*_text`` columns then
    hold the exact decimal. Identifiers are strings. Nullable fields are
    typed nulls.
    """
    pa = _pa()

    def i64(name, nullable=True):
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
        i64("acquired_event_start_ns", nullable=False), i64("acquired_event_end_ns", nullable=False),
        i64("instrument_id", nullable=False), text("contract_key", nullable=True),
        i64("formation_minutes", nullable=False), i64("cut_ns", nullable=False),
        i64("event_start_ns"), i64("event_end_ns"), i64("known_at_ns"),
        i64("scenario_latency_ns", nullable=False), i64("scenario_known_at_ns"),
        i64("observation_known_at_ns"),
        text("formation_id"), text("economic_date"),
        text("stage"), flag("stage_boundary"),
        text("definition_name"), text("definition_id"), text("definition_version"),
        text("definition_origin"), i64("definition_available_at"),
        text("fit_recipe_id", nullable=True), text("aggregation_unit"),
        flag("partition"), flag("family_occupancy_only"),
        text("channel_id", nullable=True), text("channel_role", nullable=True),
        flag("unavailable"), text("unavailable_reason", nullable=True),
        flag("missing_window"), flag("partial_window"), text("composition_reason", nullable=True),
        flag("empty_observed_window"), flag("empty_observed_channel"),
        flag("source_coverage_complete"), flag("coordinate_complete"),
        flag("flow_history_complete"), flag("atoms_complete"), flag("prefix_complete"),
        i64("prints"), i64("volume"), text("volume_text", nullable=True),
        i64("contributing_prints"),
    ]
    for name in _FRACTION_FIELDS:
        fields.extend([
            i64(f"{name}_numerator"), i64(f"{name}_denominator"),
            text(f"{name}_numerator_text", nullable=True),
            text(f"{name}_denominator_text", nullable=True),
        ])
        if name in ("open", "high", "low", "close", "buy", "sell", "unknown", "volume",
                    "signed", "weighted_prints"):
            fields.append(f64(f"{name}_approx"))
    fields.extend([
        i64("high_at_ns"), i64("low_at_ns"),
        i64("high_source_order"), i64("low_source_order"),
        text("high_origin", nullable=True), text("low_origin", nullable=True),
    ])
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
    start, end = record.get("start"), record.get("end")
    published_at, complete = record.get("published_at"), record.get("history_complete")
    timestamp(start)
    timestamp(end)
    timestamp(published_at)
    if type(complete) is not bool or published_at < end or not start < end:
        raise ContractError("training member windows must be explicit complete records")
    return int(start), int(end), int(published_at), complete


def _require_manifest(value, *, what):
    if value is None:
        raise ContractError(f"invalid {what}")
    if type(value) is str:
        if not value:
            raise ContractError(f"invalid {what}")
        return value
    if type(value) in (int, bool):
        return value
    if type(value) is dict:
        if any(type(key) is not str for key in value):
            raise ContractError(f"invalid {what}")
        return value
    if type(value) in (tuple, list):
        return value
    raise ContractError(f"invalid {what}")


def _manifest_binding(source_manifest, *, source_collection, root):
    manifest = _require_manifest(source_manifest, what="source_manifest")
    if type(manifest) is dict:
        declared_collection = manifest.get("source_collection")
        declared_root = manifest.get("root")
        if (source_collection is not None and declared_collection is not None
                and declared_collection != source_collection):
            raise IntegrityError("source_collection does not match histogram source_manifest")
        if root is not None and declared_root is not None and declared_root != root:
            raise IntegrityError("root does not match histogram source_manifest")
    return manifest


def _observation_index(observations, identity):
    table = _require_table(observations, what="observations", names=_OBS_REQUIRED)
    if not len(table):
        return {"instruments": (), "by_instrument": {}, "by_start": {}, "arrays": None}
    roots = set(_typed_text(table["root"], what="observations.root", allow_null=False))
    paths = set(_typed_text(table["source_path"], what="observations.source_path", allow_null=False))
    shas = set(_typed_text(table["source_metadata_sha256"], what="observations.source_metadata_sha256",
                           allow_null=False))
    variants = set(_typed_text(table["source_variant"], what="observations.source_variant",
                               allow_null=False))
    if roots != {identity["root"]} or paths != {identity["source_path"]}:
        raise IntegrityError("observations cannot join a different root or physical source file")
    if shas != {identity["source_metadata_sha256"]} or variants != {identity["source_variant"]}:
        raise IntegrityError("observation source identity does not join source_identity")
    starts = _typed_i64(table["event_start_ns"], what="event_start_ns")
    ends = _typed_i64(table["event_end_ns"], what="event_end_ns")
    known = _typed_i64(table["known_at_ns"], what="known_at_ns")
    instrument_id = _typed_i64(table["instrument_id"], what="instrument_id")
    prints = _typed_i64(table["prints"], what="prints")
    volume = None
    if "volume" in table.schema.names:
        volume = _typed_i64(table["volume"], what="volume")
    if (instrument_id.size and (instrument_id <= 0).any()) or (prints.size and (prints < 0).any()):
        raise IntegrityError("instrument_id must be a positive raw identifier")
    if ends.size and (ends <= starts).any():
        raise IntegrityError("observation atoms must be positive half-open intervals")
    if known.size and (known < ends).any():
        raise IntegrityError("observation known_at_ns cannot precede event_end_ns")
    if ((starts < identity["acquired_event_start_ns"]).any()
            or (ends > identity["acquired_event_end_ns"]).any()):
        raise IntegrityError("observation atoms fall outside the acquired source envelope")
    if starts.size and ((starts % MINUTE) != 0).any():
        raise IntegrityError("observation atoms must fall on the source minute calendar grid")
    if ends.size and (ends != starts + MINUTE).any():
        raise IntegrityError("observation atoms must be one-minute tiles")
    unique = tuple(int(v) for v in sorted(set(int(v) for v in instrument_id.tolist())))
    if len(unique) > MAX_INSTRUMENTS:
        raise ContractError("cohort input cannot exceed eight instruments")
    arrays = {
        "event_start": starts,
        "event_end": ends,
        "instrument_id": instrument_id,
        "contract_key": _typed_text(table["contract_key"], what="contract_key", allow_null=True),
        "known_at_ns": known,
        "source_coverage_complete": _typed_bool(table["source_coverage_complete"],
                                                what="source_coverage_complete"),
        "coordinate_complete": _typed_bool(table["coordinate_complete"], what="coordinate_complete"),
        "flow_history_complete": _typed_bool(table["flow_history_complete"],
                                             what="flow_history_complete"),
        "empty_observed_window": _typed_bool(table["empty_observed_window"],
                                             what="empty_observed_window"),
        "presence": _typed_bool(table["source_instrument_presence"],
                                what="source_instrument_presence"),
        "prints": prints,
        "volume": volume,
    }
    grouped = {}
    by_start = {}
    for instrument in unique:
        mask = instrument_id == instrument
        idx = __import__("numpy").flatnonzero(mask)
        order = __import__("numpy").argsort(starts[idx], kind="stable")
        idx = idx[order]
        if idx.size and (starts[idx][1:] < starts[idx][:-1]).any():
            raise IntegrityError("observation atoms must be ordered by event_start_ns")
        if idx.size and (ends[idx][:-1] > starts[idx][1:]).any():
            raise IntegrityError("observation atoms cannot overlap for one instrument")
        grouped[instrument] = idx
        by_start[instrument] = {int(starts[i]): int(i) for i in idx}
    return {"instruments": unique, "by_instrument": grouped, "by_start": by_start, "arrays": arrays}


def _atom_coverage(arrays, index):
    if index is None:
        return None
    volume = None if arrays["volume"] is None else int(arrays["volume"][index])
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
        "prints": int(arrays["prints"][index]),
        "volume": volume,
    }


def _tiles_member_window(obs, instrument_id, start, end):
    arrays = obs["arrays"]
    idx = obs["by_instrument"].get(instrument_id)
    if arrays is None or idx is None or len(idx) == 0:
        return False
    selected = [int(i) for i in idx
                if int(arrays["event_end"][i]) > start and int(arrays["event_start"][i]) < end]
    if not selected:
        return False
    expected = start
    for index in selected:
        if int(arrays["event_start"][index]) != expected:
            return False
        expected = int(arrays["event_end"][index])
    return expected == end


def _later_observations(obs, end):
    arrays = obs["arrays"]
    if arrays is None:
        return False
    return bool((arrays["event_start"] >= end).any())


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


def _validate_unit_trades(trades, identity, obs):
    import numpy as np

    table = _require_table(trades, what="trades", names=TRADE_FIELDS)
    if not len(table):
        return table, {"instruments": (), "by_instrument": {}, "n": 0}
    key = _unique_source_key(table)
    if key != identity["source_key"]:
        raise IntegrityError("trades cannot join a different source_key")
    state = _trade_arrays(
        table, identity, identity["acquired_event_start_ns"], identity["acquired_event_end_ns"])
    event_ns = _typed_i64(table["t"], what="t")
    source_order = _typed_i64(table["source_order"], what="source_order")
    if event_ns.size > 1:
        later = event_ns[1:]
        previous = event_ns[:-1]
        later_order = source_order[1:]
        previous_order = source_order[:-1]
        if (later < previous).any() or (
                ((later == previous) & (later_order <= previous_order)).any()):
            raise IntegrityError("global unsorted trade array")
    trade_instruments = set(int(v) for v in state["instruments"])
    obs_instruments = set(int(v) for v in obs["instruments"])
    foreign = trade_instruments - obs_instruments
    if foreign:
        raise IntegrityError("foreign instrument has trades without observation atoms")
    return table, state


def _slice_prints_volume(slices):
    import numpy as np

    prints = 0
    volume = 0
    for prepared, left, right in slices:
        if not isinstance(prepared, PreparedTradeBatch) or prepared.released:
            raise IntegrityError("the complete source-bound eligible trade projection is required")
        width = right - left
        prints += width
        if width:
            sizes = prepared.values["size"][left:right]
            if int(np.max(sizes)) > _DECLARED_MAX_SIZE:
                raise ContractError("eligible whole-print sizes must be exact positive integers")
            volume += int(np.sum(sizes.astype(np.int64, copy=False), dtype=np.int64))
    if prints > _DECLARED_UNIT_PRINTS:
        raise ContractError("unit print count exceeds the declared one-unit bound")
    return prints, volume


def _instrument_training_status(obs, instrument_id, *, trade_count, member_start, member_end):
    arrays = obs["arrays"]
    idx = obs["by_instrument"].get(instrument_id)
    if arrays is None or idx is None or len(idx) == 0:
        if trade_count:
            raise IntegrityError("absent observation cannot drop trades")
        return "skip", None
    window_idx = [int(i) for i in idx
                  if int(arrays["event_end"][i]) > member_start
                  and int(arrays["event_start"][i]) < member_end]
    if not window_idx:
        if trade_count:
            raise IntegrityError("absent observation cannot drop trades")
        presence = bool(arrays["presence"][idx].any())
        if presence:
            return "exclude", "observation_tiling_incomplete"
        return "skip", None
    if not _tiles_member_window(obs, instrument_id, member_start, member_end):
        return "exclude", "observation_tiling_incomplete"
    source = all(bool(arrays["source_coverage_complete"][i]) for i in window_idx)
    flow = all(bool(arrays["flow_history_complete"][i]) for i in window_idx)
    presence = all(bool(arrays["presence"][i]) for i in window_idx)
    coordinate = all(bool(arrays["coordinate_complete"][i]) for i in window_idx)
    prints = sum(int(arrays["prints"][i]) for i in window_idx)
    if not source:
        return "exclude", "source_coverage_incomplete"
    if not flow:
        return "exclude", "flow_history_incomplete"
    if trade_count and not coordinate and prints != trade_count:
        return "exclude", "coordinate_incomplete_trade_identity_unknown"
    if not presence and trade_count:
        raise IntegrityError("trades on a known-absent instrument")
    if not presence and prints == 0 and trade_count == 0:
        return "skip", None
    return "include", None


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
    excluded_members=(),
    train_end=None,
    maximum_distinct_sizes=DEFAULT_DISTINCT_SIZES,
):
    """Build one unpublished training histogram for a complete source/date unit.

    Authenticates actual trade timestamps and observation coverage against
    ``member_window={start,end,published_at,history_complete}``. Coverage is
    the observation-flag conjunction, never the eligible print count. Root
    merges compatible complete unit reports outside this helper.
    """
    identity = validate_source_identity(source_identity)
    if aggregation_unit != AGGREGATION_UNIT:
        raise ContractError("cohorts are provider-reported eligible trade-row aggregates")
    bounded_name(member_id)
    start, end, published_at, complete = _member_window(member_window)
    source_manifest = _require_manifest(source_manifest, what="source_manifest")
    fold_manifest = _require_manifest(fold_manifest, what="fold_manifest")
    if train_end is None:
        train_end = published_at
    timestamp(train_end)
    if end > train_end or published_at > train_end:
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
    if _later_observations(obs, end):
        raise ContractError("training member has later observations")
    if obs["arrays"] is not None and (obs["arrays"]["known_at_ns"] > train_end).any():
        raise ContractError("training member has later observations")
    table, trade_state = _validate_unit_trades(trades, identity, obs)
    if len(table):
        event_ns = _typed_i64(table["t"], what="t")
        known_at = _typed_i64(table["known_at_ns"], what="known_at_ns")
        if event_ns.size and ((event_ns < start).any() or (event_ns >= end).any()):
            raise ContractError("future or out-of-window actual trade rows")
        if known_at.size and (known_at > train_end).any():
            raise ContractError("future actual trade known_at exceeds train_end")
    trade_counts = {}
    for instrument in trade_state["instruments"]:
        bundle = trade_state["by_instrument"][instrument]
        trade_counts[int(instrument)] = int(len(bundle["event_ns"]))
    window = {"start": start, "end": end, "published_at": published_at,
              "history_complete": complete}
    summary = {
        "member_id": member_id,
        "member_window": window,
        "source_identity": identity,
        "source_manifest": source_manifest,
        "fold_manifest": fold_manifest,
        "aggregation_unit": aggregation_unit,
        "coverage_inferred_from_prints": False,
        "publication_status": "unpublished",
        "admitted_for_serving": False,
        "kernel_version": KERNEL_VERSION,
        "version": VERSION,
        "train_end": train_end,
    }
    if not complete:
        excluded.append({"member_id": member_id, "reason": "history_incomplete"})
        return {**summary, "report": None, "excluded_members": tuple(excluded),
                "excluded_instruments": (), "instrument_ids": obs["instruments"],
                "included_instrument_ids": (), "coverage_complete": False,
                "prints": None, "volume": None}
    considered = set(int(v) for v in obs["instruments"]) | set(trade_counts)
    instrument_reasons = []
    included = []
    for instrument in sorted(considered):
        status, reason = _instrument_training_status(
            obs, instrument, trade_count=trade_counts.get(instrument, 0),
            member_start=start, member_end=end)
        if status == "exclude":
            instrument_reasons.append({"instrument_id": instrument, "reason": reason})
        elif status == "include":
            included.append(instrument)
    if instrument_reasons:
        excluded.append({
            "member_id": member_id,
            "reason": instrument_reasons[0]["reason"],
            "instruments": tuple(instrument_reasons),
        })
        return {**summary, "report": None, "excluded_members": tuple(excluded),
                "excluded_instruments": tuple(instrument_reasons),
                "instrument_ids": obs["instruments"],
                "included_instrument_ids": (), "coverage_complete": False,
                "prints": None, "volume": None}
    histogram = TradeSizeHistogram(
        source_manifest=source_manifest, fold_manifest=fold_manifest,
        aggregation_unit=aggregation_unit, maximum_distinct_sizes=maximum_distinct_sizes)
    accepted_prints = 0
    accepted_volume = 0
    try:
        if included and len(table):
            for instrument in included:
                kept = _filter_instrument(table, instrument)
                if not len(kept):
                    histogram.add_sizes([], member_id=member_id)
                    continue
                for offset in range(0, len(kept), BATCH_ROWS):
                    with prepare_trade_batch(kept.slice(offset, BATCH_ROWS)) as prepared:
                        histogram.add_prepared(prepared, 0, len(prepared), member_id=member_id)
                        accepted_prints += len(prepared)
                        if len(prepared):
                            sizes = prepared.values["size"]
                            accepted_volume += int(sizes.astype("int64", copy=False).sum())
        else:
            histogram.add_sizes([], member_id=member_id)
        report = histogram.record(coverage_complete=True)
    finally:
        histogram.close()
    observed_prints = 0
    observed_volume = 0
    arrays = obs["arrays"]
    if arrays is not None:
        for instrument in included:
            for index in obs["by_instrument"][instrument]:
                if not (start <= int(arrays["event_start"][index]) < end):
                    continue
                observed_prints += int(arrays["prints"][index])
                if arrays["volume"] is not None:
                    observed_volume += int(arrays["volume"][index])
    if observed_prints != report["prints"] or accepted_prints != report["prints"]:
        raise IntegrityError("training histogram print conservation failed")
    if arrays is not None and arrays["volume"] is not None and observed_volume != report["contracts"]:
        raise IntegrityError("training histogram volume conservation failed")
    return {
        **summary,
        "report": report,
        "excluded_members": tuple(excluded),
        "excluded_instruments": (),
        "instrument_ids": obs["instruments"],
        "included_instrument_ids": tuple(included),
        "coverage_complete": True,
        "prints": report["prints"],
        "volume": report["contracts"],
        "histogram_identity": report["identity"],
    }


def _unwrap_histogram_report(histogram_report):
    wrapper = None
    report = histogram_report
    if type(histogram_report) is dict and "report" in histogram_report and "histogram" not in histogram_report:
        wrapper = histogram_report
        report = histogram_report["report"]
    return wrapper, report


def _empty_eligible_training(report):
    if report is None:
        return True
    if type(report) is not dict or "histogram" not in report:
        return False
    if report.get("coverage_complete") is False:
        return True
    return report.get("prints") == 0


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
    existing size+1 tie policy and collapse equal thresholds. Only missing
    or empty eligible training becomes ``unavailable``; malformed, future,
    duplicate or manifest errors raise. The returned plan is bound to the
    exact source/fold/training evidence. No F11 serving admission.
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
    wrapper, report = _unwrap_histogram_report(histogram_report)
    if wrapper is not None:
        identity = wrapper.get("source_identity") or {}
        if source_collection is None:
            source_collection = wrapper.get("source_collection") or identity.get("source_collection")
        if root is None:
            root = wrapper.get("root") or identity.get("root")
    source_manifest = None if report is None else report.get("source_manifest")
    fold_manifest = None if report is None else report.get("fold_manifest")
    if wrapper is not None:
        source_manifest = source_manifest or wrapper.get("source_manifest")
        fold_manifest = fold_manifest or wrapper.get("fold_manifest")
    if not _empty_eligible_training(report):
        source_manifest = _manifest_binding(
            source_manifest, source_collection=source_collection, root=root)
        fold_manifest = _require_manifest(fold_manifest, what="fold_manifest")
    frozen = frozen_fixed_definitions(aggregation_unit=aggregation_unit)
    adaptive = {}
    unavailable = {}
    fits = {}
    empty_training = _empty_eligible_training(report)
    for name, weighting, probabilities in ADAPTIVE_RECIPES:
        if empty_training:
            adaptive[name] = {
                "name": name, "kind": "adaptive", "definition": None,
                "unavailable": _EMPTY_TRAINING,
                "partition": True, "family_occupancy_only": False,
            }
            unavailable[name] = _EMPTY_TRAINING
            continue
        fitted = fit_unpublished_cohort_definition(
            report, train_end=train_end, available_at=available_at,
            member_identities=member_identities, aggregation_unit=aggregation_unit,
            probabilities=probabilities, weighting=weighting, version=name,
            member_windows=member_windows)
        adaptive[name] = {
            "name": name, "kind": "adaptive", "definition": fitted["definition"],
            "unavailable": None, "partition": True, "family_occupancy_only": False,
        }
        fits[name] = fitted
        unavailable[name] = None
    evidence = {name: serialize_fit_evidence(fit) for name, fit in fits.items()}
    histogram_identity = None if report is None else report.get("identity")
    binding = {
        "source_collection": source_collection,
        "root": root,
        "source_manifest": source_manifest,
        "fold_manifest": fold_manifest,
        "histogram_identity": histogram_identity,
        "train_end": train_end,
        "available_at": available_at,
        "fit_evidence_identity": digest({name: item["identity"] for name, item in evidence.items()}),
    }
    definitions = {}
    for name, item in {**frozen, **adaptive}.items():
        bound = dict(item)
        for key, value in binding.items():
            if bound.get(key) is None:
                bound[key] = value
        definitions[name] = bound
    serialized = {name: None if item["definition"] is None else serialize_definition(item["definition"])
                  for name, item in definitions.items()}
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
        "source_manifest": source_manifest,
        "fold_manifest": fold_manifest,
        "histogram_identity": histogram_identity,
        "publication_status": "unpublished",
        "admitted_for_serving": False,
        "output_kind": _UNPUBLISHED,
        "tie_policy": _TIE_POLICY,
        "version": VERSION,
        "kernel_version": KERNEL_VERSION,
        "fit_evidence_identity": binding["fit_evidence_identity"],
    }


def _authenticated_fitted_bundle(item, name):
    definition = item.get("definition")
    if definition is None:
        return True
    if definition.origin != "fitted":
        return True
    if definition.available_at is None or definition.fit_recipe_id is None:
        raise ContractError("typed fitted definitions require authenticated fit bundle metadata")
    return True


def _plan_from_definitions(definitions):
    if type(definitions) is dict and "definitions" in definitions and "fixed_all" in definitions.get("definitions", {}):
        payload = definitions
        plan = {}
        for name, item in payload["definitions"].items():
            bound = dict(item)
            for key in _FIT_BINDING:
                if bound.get(key) is None and payload.get(key) is not None:
                    bound[key] = payload.get(key)
            if bound.get("kind") == "adaptive" or (
                    bound.get("definition") is not None
                    and bound["definition"].origin == "fitted"):
                _authenticated_fitted_bundle(bound, name)
            plan[name] = bound
        return plan
    if type(definitions) is dict and all(type(v) is dict and "definition" in v for v in definitions.values()):
        plan = {}
        for name, item in definitions.items():
            bound = dict(item)
            bound.setdefault("name", name)
            definition = bound.get("definition")
            if definition is not None and definition.origin == "fitted":
                _authenticated_fitted_bundle(bound, name)
            plan[name] = bound
        return plan
    if type(definitions) is dict and all(v is None or type(v) is CohortDefinition for v in definitions.values()):
        out = {}
        for name, definition in definitions.items():
            if definition is not None and definition.origin == "fitted":
                raise ContractError(
                    "typed fitted bare definitions require authenticated fit bundle metadata")
            out[name] = {
                "name": name,
                "kind": ("fixed_soft" if definition is not None and definition.knots else "fixed_source"),
                "definition": definition,
                "unavailable": None if definition is not None else "unavailable_missing_definition",
                "partition": False if name in OVERLAPPING_SOURCE_FILTERS else True,
                "family_occupancy_only": name in OVERLAPPING_SOURCE_FILTERS,
            }
        return out
    raise ContractError("definitions must be the fit_definitions payload or an explicit name map")


def _assert_serving_plan(plan, identity):
    for name, item in plan.items():
        collection = item.get("source_collection")
        root = item.get("root")
        if collection is not None and collection != identity["source_collection"]:
            raise IntegrityError("foreign source_collection cannot serve this unit")
        if root is not None and root != identity["root"]:
            raise IntegrityError("foreign root cannot serve this unit")
        definition = item.get("definition")
        if definition is not None and definition.origin == "fitted":
            if definition.available_at is None or definition.fit_recipe_id is None:
                raise ContractError("typed fitted definitions require authenticated fit bundle metadata")
            train_end = item.get("train_end")
            if train_end is not None and definition.available_at < train_end:
                raise ContractError("future fit availability")


def _null_metrics(row, *, path=True, mass=True):
    if path:
        for name in _PATH_FIELDS:
            row[name] = None
        for name in ("observed_signed_lower", "observed_signed_upper",
                     "true_signed_lower", "true_signed_upper"):
            row[name] = None
    if mass:
        for name in _MASS_FIELDS:
            row[name] = None
        row["empty_observed_channel"] = False
        row["empty_observed_window"] = False
    return row


def _reject_source_binding(left, right):
    if left.get("source_key") != right.get("source_key"):
        raise IntegrityError("composed cohort atoms cannot join distinct source_key streams")
    if left.get("source_collection") != right.get("source_collection"):
        raise IntegrityError("composed cohort atoms cannot join distinct source collections")
    if left.get("definition_name") != right.get("definition_name"):
        raise IntegrityError("composed cohort atoms must share a definition")
    left_id = None if left.get("definition") is None else left["definition"].id
    right_id = None if right.get("definition") is None else right["definition"].id
    if left_id is not None and right_id is not None and left_id != right_id:
        raise IntegrityError("composed cohort atoms must share a definition identity")
    if left.get("instrument_id") != right.get("instrument_id"):
        raise IntegrityError("composed cohort atoms must share a raw instrument")


def compose_cohort_records(left, right):
    """Associative composition of two consecutive relative (open-zero) records.

    ``window_volume`` is the integer all-flow denominator. ``volume`` is the
    left/right weighted cohort mass. Occupancy uses all-flow, not channel mass.
    """
    if left is None:
        return right
    if right is None:
        return left
    _reject_source_binding(left, right)
    start_ns = left["event_start_ns"]
    end_ns = right["event_end_ns"]
    if left.get("missing_window") or right.get("missing_window"):
        template = left if not left.get("missing_window") else right
        row = _missing_channel(
            plan=template.get("plan") or {},
            definition_name=template.get("definition_name"),
            start_ns=start_ns, end_ns=end_ns,
            contract_key=None,
            channel_id=template.get("channel_id"),
            role=template.get("channel_role"),
            reason="incomplete_composition",
            instrument_id=template.get("instrument_id"),
            source_key=template.get("source_key"),
            source_collection=template.get("source_collection"),
        )
        row["partial_window"] = bool(
            (not left.get("missing_window")) or (not right.get("missing_window")))
        row["source_coverage_complete"] = False
        row["flow_history_complete"] = False
        row["coordinate_complete"] = False
        row["prefix_complete"] = False
        row["atoms_complete"] = False
        row["observation_known_at_ns"] = None
        return row
    if left.get("unavailable") or right.get("unavailable"):
        reason = left.get("unavailable_reason") or right.get("unavailable_reason")
        template = left
        return _unavailable_channel(
            plan=template.get("plan") or {},
            definition_name=template.get("definition_name"),
            start_ns=start_ns, end_ns=end_ns,
            contract_key=None,
            channel_id=template.get("channel_id"),
            role=template.get("channel_role"),
            reason=reason or "unavailable_before_training_availability",
            instrument_id=template.get("instrument_id"),
            source_key=template.get("source_key"),
            source_collection=template.get("source_collection"),
        )
    if left["channel_id"] != right["channel_id"]:
        raise IntegrityError("composed cohort atoms must share a channel")
    if left["event_end_ns"] != right["event_start_ns"]:
        raise IntegrityError("composed cohort atoms must be contiguous")
    left_contract = left.get("contract_key")
    right_contract = right.get("contract_key")
    contract_switch = left_contract != right_contract
    source_complete = bool(left.get("source_coverage_complete") and right.get("source_coverage_complete"))
    flow_complete = bool(left.get("flow_history_complete") and right.get("flow_history_complete"))
    coordinate_complete = bool(
        left.get("coordinate_complete") and right.get("coordinate_complete") and not contract_switch)
    atoms_complete = bool(left.get("atoms_complete") and right.get("atoms_complete"))
    prefix_complete = bool(left.get("prefix_complete") and right.get("prefix_complete"))
    history = source_complete and flow_complete and prefix_complete and atoms_complete
    window_volume = _checked_add(left["window_volume"], right["window_volume"], what="window_volume")
    prints = _checked_add(left["prints"], right["prints"], what="prints")
    contributing = _checked_add(
        left["contributing_prints"], right["contributing_prints"], what="contributing_prints")
    buy = exact_number(left["buy"]) + exact_number(right["buy"])
    sell = exact_number(left["sell"]) + exact_number(right["sell"])
    unknown = exact_number(left["unknown"]) + exact_number(right["unknown"])
    weighted = exact_number(left["weighted_prints"]) + exact_number(right["weighted_prints"])
    channel_volume = buy + sell + unknown
    signed = buy - sell
    knowns = [value for value in (
        left.get("observation_known_at_ns"), right.get("observation_known_at_ns"))
        if value is not None]
    observation_known = max(knowns) if knowns else None
    composed = {
        "channel_id": left["channel_id"],
        "channel_role": left["channel_role"],
        "buy": buy,
        "sell": sell,
        "unknown": unknown,
        "volume": channel_volume,
        "signed": signed,
        "weighted_prints": weighted,
        "contributing_prints": contributing,
        "prints": prints,
        "window_volume": window_volume,
        "count_occupancy": (weighted / prints) if prints else None,
        "volume_occupancy": (channel_volume / window_volume) if window_volume else None,
        "observed_signed_lower": signed - unknown,
        "observed_signed_upper": signed + unknown,
        "true_signed_lower": (signed - unknown) if history else None,
        "true_signed_upper": (signed + unknown) if history else None,
        "empty_observed_channel": history and contributing == 0,
        "empty_observed_window": history and prints == 0,
        "source_coverage_complete": source_complete,
        "coordinate_complete": coordinate_complete,
        "flow_history_complete": flow_complete,
        "atoms_complete": atoms_complete,
        "prefix_complete": prefix_complete,
        "missing_window": False,
        "partial_window": False,
        "unavailable": False,
        "unavailable_reason": None,
        "composition_reason": None,
        "event_start_ns": start_ns,
        "event_end_ns": end_ns,
        "contract_key": left_contract if left_contract == right_contract else None,
        "instrument_id": left.get("instrument_id"),
        "source_key": left.get("source_key"),
        "source_collection": left.get("source_collection"),
        "definition_name": left["definition_name"],
        "definition": left.get("definition"),
        "plan": left.get("plan"),
        "observation_known_at_ns": observation_known,
    }
    if contract_switch or left.get("open") is None or right.get("open") is None:
        _null_metrics(composed, path=True, mass=False)
        composed["coordinate_complete"] = False
        composed["true_signed_lower"] = None
        composed["true_signed_upper"] = None
        if contract_switch:
            composed["composition_reason"] = "raw_contract_switch"
            composed["contract_key"] = None
        return composed
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
    composed.update({
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
    })
    if not coordinate_complete:
        _null_metrics(composed, path=True, mass=False)
        composed["true_signed_lower"] = None
        composed["true_signed_upper"] = None
    return composed


def _channel_from_record(record, channel, *, coverage, plan, definition_name, start_ns, end_ns,
                         identity, instrument_id):
    history = bool(coverage["source_coverage_complete"] and coverage["flow_history_complete"]
                   and coverage["prefix_complete"] and coverage["atoms_complete"])
    coordinate = bool(coverage["coordinate_complete"])
    return {
        "channel_id": channel["channel_id"],
        "channel_role": channel["role"],
        "open": channel["open"] if coordinate else None,
        "high": channel["high"] if coordinate else None,
        "low": channel["low"] if coordinate else None,
        "close": channel["close"] if coordinate else None,
        "high_at_ns": channel["high_at_ns"] if coordinate else None,
        "low_at_ns": channel["low_at_ns"] if coordinate else None,
        "high_source_order": channel["high_source_order"] if coordinate else None,
        "low_source_order": channel["low_source_order"] if coordinate else None,
        "high_origin": channel["high_origin"] if coordinate else None,
        "low_origin": channel["low_origin"] if coordinate else None,
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
        "empty_observed_channel": history and channel["contributing_prints"] == 0,
        "empty_observed_window": history and record["prints"] == 0,
        "source_coverage_complete": coverage["source_coverage_complete"],
        "coordinate_complete": coordinate,
        "flow_history_complete": coverage["flow_history_complete"],
        "atoms_complete": coverage["atoms_complete"],
        "prefix_complete": coverage["prefix_complete"],
        "missing_window": False,
        "partial_window": False,
        "unavailable": False,
        "unavailable_reason": None,
        "composition_reason": None,
        "event_start_ns": start_ns,
        "event_end_ns": end_ns,
        "contract_key": coverage.get("contract_key"),
        "instrument_id": instrument_id,
        "source_key": identity["source_key"],
        "source_collection": identity["source_collection"],
        "definition_name": definition_name,
        "definition": record.get("definition") or plan.get("definition"),
        "plan": plan,
        "observation_known_at_ns": coverage.get("known_at_ns"),
    }


def _missing_channel(*, plan, definition_name, start_ns, end_ns, contract_key, channel_id, role,
                     reason="missing_observation_atom", instrument_id=None, source_key=None,
                     source_collection=None):
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
        "missing_window": True, "partial_window": False, "unavailable": False,
        "unavailable_reason": reason, "composition_reason": reason,
        "event_start_ns": start_ns, "event_end_ns": end_ns, "contract_key": contract_key,
        "instrument_id": instrument_id, "source_key": source_key,
        "source_collection": source_collection,
        "definition_name": definition_name, "definition": plan.get("definition"), "plan": plan,
        "observation_known_at_ns": None,
    }


def _unavailable_channel(*, plan, definition_name, start_ns, end_ns, contract_key, channel_id, role,
                         reason, instrument_id=None, source_key=None, source_collection=None):
    row = _missing_channel(
        plan=plan, definition_name=definition_name, start_ns=start_ns,
        end_ns=end_ns, contract_key=contract_key, channel_id=channel_id,
        role=role, reason=reason, instrument_id=instrument_id,
        source_key=source_key, source_collection=source_collection)
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
                   coverage, plan, definition_name, identity):
    if coverage is None:
        return [_missing_channel(
            plan=plan, definition_name=definition_name, start_ns=start_ns,
            end_ns=end_ns, contract_key=None, channel_id=channel_id, role=role,
            instrument_id=instrument_id, source_key=identity["source_key"],
            source_collection=identity["source_collection"])
            for channel_id, role in _channel_specs_for_plan(plan)]
    if plan.get("unavailable") or definition is None:
        return [_unavailable_channel(
            plan=plan, definition_name=definition_name, start_ns=start_ns, end_ns=end_ns,
            contract_key=coverage.get("contract_key"), channel_id=channel_id, role=role,
            reason=plan.get("unavailable") or "unavailable_missing_definition",
            instrument_id=instrument_id, source_key=identity["source_key"],
            source_collection=identity["source_collection"])
            for channel_id, role in _channel_specs_for_plan(plan)]
    if definition.origin == "fitted" and definition.available_at is not None and definition.available_at > start_ns:
        return [_unavailable_channel(
            plan=plan, definition_name=definition_name, start_ns=start_ns, end_ns=end_ns,
            contract_key=coverage.get("contract_key"), channel_id=channel_id, role=role,
            reason="unavailable_before_training_availability",
            instrument_id=instrument_id, source_key=identity["source_key"],
            source_collection=identity["source_collection"])
            for channel_id, role in _channel_specs_for_plan(plan)]
    accepted_prints, accepted_volume = _slice_prints_volume(prepared_slices)
    if coverage["prints"] != accepted_prints:
        raise IntegrityError("observation prints do not conserve accepted atom trades")
    if coverage.get("volume") is not None and coverage["volume"] != accepted_volume:
        raise IntegrityError("observation volume does not conserve accepted atom trades")
    flags = {
        "source_coverage_complete": coverage["source_coverage_complete"],
        "coordinate_complete": coverage["coordinate_complete"],
        "flow_history_complete": coverage["flow_history_complete"],
        "atoms_complete": True,
        "prefix_complete": True,
        "contract_key": coverage.get("contract_key"),
        "known_at_ns": coverage.get("known_at_ns"),
    }
    try:
        window = CohortWindow(
            definition=definition, instrument_id=instrument_id, start_ns=start_ns,
            end_ns=end_ns, latency_ns=SOURCE_LATENCY_NS)
    except DependencyUnavailable:
        return [_unavailable_channel(
            plan=plan, definition_name=definition_name, start_ns=start_ns, end_ns=end_ns,
            contract_key=coverage.get("contract_key"), channel_id=channel_id, role=role,
            reason="unavailable_before_training_availability",
            instrument_id=instrument_id, source_key=identity["source_key"],
            source_collection=identity["source_collection"])
            for channel_id, role in _channel_specs_for_plan(plan)]
    for prepared, left, right in prepared_slices:
        window.add_prepared(prepared, left, right)
    record = window.record(
        source_coverage_complete=coverage["source_coverage_complete"],
        coordinate_complete=coverage["coordinate_complete"])
    if coverage["empty_observed_window"] and record["prints"] != 0:
        raise IntegrityError("empty observed atom cannot contain eligible prints")
    if (not coverage["presence"] and record["prints"] == 0
            and coverage["source_coverage_complete"] and coverage["flow_history_complete"]):
        record = dict(record)
        record["empty_observed_window"] = True
    if plan["name"] in OVERLAPPING_SOURCE_FILTERS:
        record = dict(record)
        record["partition"] = False
    return [_channel_from_record(
        record, channel, coverage=flags, plan=plan, definition_name=definition_name,
        start_ns=start_ns, end_ns=end_ns, identity=identity, instrument_id=instrument_id)
        for channel in record["channels"]]


def _formation_id(identity, instrument_id, contract_key, minutes, start_ns, end_ns, definition_id, channel_id):
    return digest({
        "root": identity["root"], "source_path": identity["source_path"],
        "source_key": identity["source_key"], "source_collection": identity["source_collection"],
        "instrument_id": instrument_id, "contract_key": contract_key,
        "formation_minutes": minutes, "event_start_ns": start_ns, "event_end_ns": end_ns,
        "definition_id": definition_id, "channel_id": channel_id,
    })


def _actual_known_at(end_ns, latency_ns, observation_known_at_ns, available_at):
    if end_ns is None:
        return None
    synthetic = latency_ns != SOURCE_LATENCY_NS
    scenario_floor = end_ns + (SOURCE_LATENCY_NS if synthetic else latency_ns)
    known = scenario_floor
    if observation_known_at_ns is not None:
        known = max(known, int(observation_known_at_ns))
    if available_at is not None:
        known = max(known, int(available_at))
    return known


def _emit_row(identity, instrument_id, channel, *, minutes, cut_ns, latency_ns, stages, economic_date):
    definition = channel.get("definition")
    plan = channel.get("plan") or {}
    available = None if definition is None else definition.available_at
    start_ns = channel["event_start_ns"]
    end_ns = channel["event_end_ns"]
    observation_known = channel.get("observation_known_at_ns")
    scenario_known = None if end_ns is None else end_ns + latency_ns
    known = _actual_known_at(end_ns, latency_ns, observation_known, available)
    if known is None or start_ns is None:
        stage, boundary = "unassigned", False
    else:
        stage, boundary = _stage_pair(identity["root"], start_ns, known, stages)
    date = economic_date or (_utc_date(start_ns) if start_ns is not None else _utc_date(cut_ns))
    definition_id = None if definition is None else definition.id
    window_volume = channel.get("window_volume")
    volume_stored, volume_text = _encode_exact_int(window_volume) if type(window_volume) is int else (None, None)
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
        "scenario_latency_ns": latency_ns,
        "scenario_known_at_ns": scenario_known,
        "observation_known_at_ns": observation_known,
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
        "partial_window": bool(channel.get("partial_window")),
        "composition_reason": channel.get("composition_reason"),
        "empty_observed_window": bool(channel.get("empty_observed_window")),
        "empty_observed_channel": bool(channel.get("empty_observed_channel")),
        "source_coverage_complete": bool(channel.get("source_coverage_complete")),
        "coordinate_complete": bool(channel.get("coordinate_complete")),
        "flow_history_complete": bool(channel.get("flow_history_complete")),
        "atoms_complete": bool(channel.get("atoms_complete")),
        "prefix_complete": bool(channel.get("prefix_complete")),
        "prints": channel.get("prints"),
        "volume": volume_stored,
        "volume_text": volume_text,
        "contributing_prints": channel.get("contributing_prints"),
    }
    for name in _FRACTION_FIELDS:
        num, den, num_text, den_text = _fraction_storage(channel.get(name))
        row[f"{name}_numerator"] = num
        row[f"{name}_denominator"] = den
        row[f"{name}_numerator_text"] = num_text
        row[f"{name}_denominator_text"] = den_text
        if name in ("open", "high", "low", "close", "buy", "sell", "unknown", "volume", "signed",
                    "weighted_prints"):
            row[f"{name}_approx"] = _approx(channel.get(name))
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
    expected = start_ns
    gapped = False
    for item in selected:
        if item["event_start_ns"] != expected:
            gapped = True
            break
        expected = item["event_end_ns"]
    complete = (selected[0]["event_start_ns"] == start_ns and expected == end_ns and not gapped)
    if not complete:
        template = selected[0]
        row = _missing_channel(
            plan=template.get("plan") or {},
            definition_name=template.get("definition_name"),
            start_ns=start_ns, end_ns=end_ns, contract_key=None,
            channel_id=template.get("channel_id"), role=template.get("channel_role"),
            reason="incomplete_composition",
            instrument_id=template.get("instrument_id"),
            source_key=template.get("source_key"),
            source_collection=template.get("source_collection"),
        )
        row["partial_window"] = True
        row["source_coverage_complete"] = False
        row["flow_history_complete"] = False
        row["coordinate_complete"] = False
        row["prefix_complete"] = False
        row["atoms_complete"] = False
        return row
    composed = selected[0]
    for item in selected[1:]:
        composed = compose_cohort_records(composed, item)
    return composed


class _PreparedCursor:
    """Stream one instrument's prepared batches; slices are reused across definitions."""

    def __init__(self, table, *, instrument_id, scan_start_ns, scan_end_ns):
        import numpy as np

        self._table = table
        self._instrument_id = instrument_id
        self._scan_start = scan_start_ns
        self._scan_end = scan_end_ns
        self._offset = 0
        self._prepared = None
        self._origin = 0
        self._width = 0
        self._retire = []
        self.consumed = 0
        self.eligible = 0
        if not len(table):
            return
        event_ns = _typed_i64(table["t"], what="t")
        source_order = _typed_i64(table["source_order"], what="source_order")
        known_at = _typed_i64(table["known_at_ns"], what="known_at_ns")
        flags = _typed_i64(table["raw_flags"], what="raw_flags")
        instruments = _typed_i64(table["instrument_id"], what="instrument_id")
        if instruments.size and (instruments != instrument_id).any():
            raise IntegrityError("foreign instrument in prepared cursor")
        if event_ns.size > 1 and (
                (event_ns[1:] < event_ns[:-1]).any()
                or (source_order[1:] <= source_order[:-1]).any()):
            raise IntegrityError("instrument trade array is unsorted")
        if known_at.size and (known_at != event_ns + SOURCE_LATENCY_NS).any():
            raise IntegrityError("stored trade known_at_ns must equal event time plus the 250ms source latency")
        if flags.size and ((flags > 255).any() or (flags & 32).any()):
            raise IntegrityError("trade source mapping, snapshot inclusion, identity or information cut changed")
        key = _unique_source_key(table)
        if key is None:
            raise IntegrityError("a cohort window cannot join distinct acquired source streams")
        self.eligible = int(np.count_nonzero((event_ns >= scan_start_ns) & (event_ns < scan_end_ns)))

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
                self.consumed += right - left
            if int(stamps[-1]) >= end_ns:
                break
            self._retire.append(prepared)
            self._prepared = None
            self._offset = self._origin + self._width
        return found

    def assert_reconciled(self):
        if self.consumed != self.eligible:
            raise IntegrityError("eligible events were not read exactly once")
        return self.consumed


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
    minute atoms per definition/channel. Frozen fit binding is required for
    fitted definitions; this helper does not refit.
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
    _assert_serving_plan(plan, identity)
    obs = _observation_index(observations, identity)
    table, _trade_state = _validate_unit_trades(trades, identity, obs)
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
    trades_reconciled = 0
    eligible_trades = 0
    for instrument in obs["instruments"]:
        arrays = obs["arrays"]
        by_start = obs["by_start"][instrument]
        kept = _filter_instrument(table, instrument) if len(table) else table
        rings = {name: {channel_id: deque(maxlen=_MAX_FORMATION_MINUTES)
                        for channel_id, _ in _channel_specs_for_plan(item)}
                 for name, item in plan.items()}
        cursor = _PreparedCursor(
            kept, instrument_id=instrument, scan_start_ns=int(grid_start), scan_end_ns=int(grid_end))
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
                        definition_name=name, identity=identity)
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
                                        role=role, instrument_id=instrument,
                                        source_key=identity["source_key"],
                                        source_collection=identity["source_collection"])
                                formation_rows.append(_emit_row(
                                    identity, instrument, composed, minutes=minutes,
                                    cut_ns=cut, latency_ns=latency_ns, stages=stages,
                                    economic_date=economic_date))
                minute = end
            trades_reconciled += cursor.assert_reconciled()
            eligible_trades += cursor.eligible
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
            "trades_reconciled": trades_reconciled,
            "eligible_trades": eligible_trades,
            "events_per_definition": eligible_trades,
            "definitions": tuple(plan),
            "coverage_inferred_from_prints": False,
            "admitted_for_serving": False,
            "publication_status": "unpublished",
            "family_complete": False,
        },
        "version": VERSION,
        "family_complete": False,
    }


def _join_reject(feature, reason, *, extra=None):
    payload = {
        "eligible": False,
        "reason": reason,
        "stage": None,
        "same_source_identity": False,
        "same_instrument": False,
        "same_raw_contract": False,
        "same_cut": False,
        "feature_interval_stage": None,
        "label_maturity_stage": None,
        "feature_known_at_ns": None,
        "label_maturity_ns": None,
        "actual_receipt_eligible": False,
        "actual_dependency_known_at_ns": feature.get("known_at_ns") if type(feature) is dict else None,
        "latency_scenario_ns": None,
        "synthetic_latency_scenario": None,
        "stored_source_latency_ns": SOURCE_LATENCY_NS,
    }
    if extra:
        payload.update(extra)
    return payload


def scientific_join_eligibility(feature, label):
    """Cohort-aware wrapper around accepted ``join_window_eligibility``.

    Rejects unavailable, missing, prefix/incomplete and future definition
    availability. Authenticates source + contract exactly. Then delegates
    the unchanged 0/250/1000 ms counterfactual contract. ``eligible`` is
    that counterfactual result after structural rejects.
    ``actual_receipt_eligible`` is false when the stored actual dependency
    clock (observation known_at and fit availability; synthetic scenario
    latency excluded from the floor) is later than the counterfactual
    feature clock. This does not claim actual receipt at an unavailable
    time. The window kernel is not modified.
    """
    if type(feature) is not dict or type(label) is not dict:
        raise ContractError("join feature and label must be explicit records")
    latency = label.get("latency_ns")
    extra = {
        "actual_dependency_known_at_ns": feature.get("known_at_ns"),
        "latency_scenario_ns": latency,
        "synthetic_latency_scenario": None if latency is None else latency != SOURCE_LATENCY_NS,
        "stored_source_latency_ns": SOURCE_LATENCY_NS,
    }
    if feature.get("unavailable"):
        return _join_reject(feature, "unavailable_definition", extra=extra)
    if feature.get("missing_window"):
        return _join_reject(feature, "missing_window", extra=extra)
    if feature.get("partial_window"):
        return _join_reject(feature, "partial_window", extra=extra)
    if not feature.get("prefix_complete") or not feature.get("atoms_complete"):
        return _join_reject(feature, "incomplete_prefix", extra=extra)
    if not feature.get("source_coverage_complete") or not feature.get("flow_history_complete"):
        return _join_reject(feature, "incomplete_history", extra=extra)
    available = feature.get("definition_available_at")
    start = feature.get("event_start_ns")
    if available is not None and start is not None and available > start:
        return _join_reject(feature, "future_definition_availability", extra=extra)
    if label.get("source_key") is not None and feature.get("source_key") != label.get("source_key"):
        return _join_reject(feature, "source_identity_mismatch", extra=extra)
    if (label.get("source_collection") is not None
            and feature.get("source_collection") != label.get("source_collection")):
        return _join_reject(feature, "source_identity_mismatch", extra=extra)
    feature_contract = feature.get("contract_key")
    label_contract = label.get("contract_key")
    if (type(feature_contract) is not str or not feature_contract
            or feature_contract != label_contract):
        return _join_reject(feature, "contract_mismatch", extra=extra)
    result = dict(join_window_eligibility(feature, label))
    result["actual_dependency_known_at_ns"] = feature.get("known_at_ns")
    result["latency_scenario_ns"] = latency
    result["synthetic_latency_scenario"] = None if latency is None else latency != SOURCE_LATENCY_NS
    result["stored_source_latency_ns"] = SOURCE_LATENCY_NS
    counterfactual = result.get("feature_known_at_ns")
    actual = feature.get("known_at_ns")
    actual_ok = (
        result["eligible"] and actual is not None and counterfactual is not None
        and actual <= counterfactual)
    result["actual_receipt_eligible"] = bool(actual_ok)
    return result
