"""Exact unpublished size histograms, quantile bins and ordered cohort paths.

These kernels are measurement-definition alternatives to the retained hard
source filters. Trade size is an observation, not a participant identity.
Outputs are unpublished mathematical calculations. Actual source, fold and
F11 fit publication are joined later by the registered study caller.
"""
from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
import math
from types import MappingProxyType

from trading_research.errors import ContractError, DependencyUnavailable, IntegrityError
from trading_research.foundations.time import timestamp
from trading_research.measurements.common import bounded_name, bounded_rows
from trading_research.measurements.cvd import CohortChannel, CohortDefinition, exact_number
from trading_research.operations.artifacts import digest
from trading_research.research.auction_flow_windows import PreparedTradeBatch, prepare_trade_batch


VERSION = "auction-flow-exact-unpublished-cohort-calculations-v1"
BATCH_ROWS = 65_536
DEFAULT_DISTINCT_SIZES = 250_000
MAX_DISTINCT_SIZES = 1_000_000
MAX_PRINTS = 50_000_000
MAX_ELIGIBLE_SIZE = 2**32 - 2
INT64_MAX = 2**63 - 1
_PROJECTION = "the complete source-bound eligible trade projection is required"
_MAPPING = "trade source mapping, snapshot inclusion, identity or information cut changed"
_FAILED = "a failed cohort accumulator cannot publish or resume partial state"
_UNPUBLISHED = "unpublished mathematical calculations"
_TIE_POLICY = "lower_bin_then_merge_empty"


def _row_index(value):
    import numpy as np

    if isinstance(value, (bool, np.bool_)) or not isinstance(value, (int, np.integer)):
        raise IntegrityError(_PROJECTION)
    return int(value)


def _freeze_manifest(value):
    if value is None or type(value) in (str, int, bool):
        if type(value) is str and len(value) > 4096:
            raise ContractError("source/fold manifest is too large")
        return value
    if type(value) is dict:
        if any(type(k) is not str for k in value):
            raise ContractError("manifest keys must be strings")
        return MappingProxyType({k: _freeze_manifest(v) for k, v in value.items()})
    if type(value) in (tuple, list):
        return tuple(_freeze_manifest(v) for v in value)
    raise ContractError("source/fold manifest must be an explicit JSON-like value")


def _eligible_scalar(value):
    import numpy as np

    if isinstance(value, (bool, np.bool_)) or not isinstance(value, (int, np.integer)):
        raise ContractError("eligible whole-print sizes must be exact positive integers")
    size = int(value)
    if not 1 <= size <= MAX_ELIGIBLE_SIZE:
        raise ContractError("eligible whole-print sizes must be exact positive integers")
    return size


def _eligible_size_values(values):
    import numpy as np

    if isinstance(values, (list, tuple)):
        if len(values) > BATCH_ROWS:
            raise ContractError("size batches cannot exceed the prepared-trade row bound")
        return [_eligible_scalar(v) for v in values]
    array = np.asarray(values)
    if array.ndim != 1 or array.dtype.kind not in "iu" or len(array) > BATCH_ROWS:
        raise ContractError("bounded equal exact arrays of eligible reported-side trades required")
    if np.any(array <= 0) or np.any(array >= 2**32 - 1):
        raise ContractError("eligible whole-print sizes must be exact positive integers")
    return array


def _histogram_identity(*, histogram, prints, contracts, member_ids, source_manifest, fold_manifest,
                        aggregation_unit):
    return digest({"version": VERSION, "histogram": histogram, "prints": prints, "contracts": contracts,
                   "member_ids": member_ids, "source_manifest": source_manifest,
                   "fold_manifest": fold_manifest, "aggregation_unit": aggregation_unit})


def _pairs_from_counts(pairs):
    if type(pairs) not in (tuple, list) or len(pairs) > MAX_DISTINCT_SIZES:
        raise ContractError("complete histogram pairs must be a bounded sequence")
    seen = set()
    histogram = []
    for item in pairs:
        if type(item) not in (tuple, list) or len(item) != 2:
            raise ContractError("histogram pairs are (size, count)")
        size, count = item
        if type(size) is not int or type(count) is not int or count < 1 or not 1 <= size <= MAX_ELIGIBLE_SIZE:
            raise ContractError("histogram summaries need exact positive size and count integers")
        if size in seen:
            raise ContractError("histogram summaries cannot repeat a size")
        seen.add(size)
        histogram.append((size, count))
    histogram.sort()
    return tuple(histogram)


def _validate_histogram_report(report):
    if type(report) is not dict:
        raise ContractError("a complete unpublished histogram report is required")
    required = ("version", "histogram", "prints", "contracts", "member_ids", "source_manifest",
                "fold_manifest", "aggregation_unit", "coverage_complete", "identity")
    if any(name not in report for name in required) or report["version"] != VERSION:
        raise ContractError("histogram report is missing its unpublished identity fields")
    if type(report["coverage_complete"]) is not bool or type(report["prints"]) is not int:
        raise ContractError("histogram totals and coverage must be exact")
    if type(report["contracts"]) is not int or report["prints"] < 0 or report["contracts"] < 0:
        raise ContractError("histogram totals and coverage must be exact")
    histogram = _pairs_from_counts(report["histogram"])
    prints = sum(count for _, count in histogram)
    contracts = sum(size * count for size, count in histogram)
    if prints != report["prints"] or contracts != report["contracts"]:
        raise IntegrityError("count times size does not reconcile with histogram totals")
    member_ids = report["member_ids"]
    if (type(member_ids) not in (tuple, list) or any(type(m) is not str for m in member_ids)
            or tuple(sorted(member_ids)) != tuple(member_ids) or len(set(member_ids)) != len(member_ids)):
        raise ContractError("histogram member identities must be a sorted unique tuple")
    member_ids = tuple(member_ids)
    identity = _histogram_identity(
        histogram=histogram, prints=prints, contracts=contracts, member_ids=member_ids,
        source_manifest=report["source_manifest"], fold_manifest=report["fold_manifest"],
        aggregation_unit=report["aggregation_unit"])
    if identity != report["identity"]:
        raise IntegrityError("histogram identity does not match its complete sorted counts")
    return {"histogram": histogram, "prints": prints, "contracts": contracts, "member_ids": member_ids,
            "source_manifest": report["source_manifest"], "fold_manifest": report["fold_manifest"],
            "aggregation_unit": report["aggregation_unit"], "coverage_complete": report["coverage_complete"],
            "identity": identity}


def complete_histogram_report(*, pairs, member_ids, source_manifest, fold_manifest, coverage_complete,
                              aggregation_unit=None):
    """Build a complete histogram summary without expanding whole prints."""
    if type(coverage_complete) is not bool:
        raise ContractError("histogram coverage is an explicit separate input")
    histogram = _pairs_from_counts(pairs)
    ids = tuple(bounded_name(m) for m in bounded_rows(member_ids, MAX_PRINTS, name="histogram members"))
    if tuple(sorted(ids)) != ids or len(set(ids)) != len(ids):
        raise ContractError("histogram member identities must be a sorted unique tuple")
    if aggregation_unit is not None:
        bounded_name(aggregation_unit)
    prints = sum(count for _, count in histogram)
    contracts = sum(size * count for size, count in histogram)
    source_manifest = _freeze_manifest(source_manifest)
    fold_manifest = _freeze_manifest(fold_manifest)
    identity = _histogram_identity(
        histogram=histogram, prints=prints, contracts=contracts, member_ids=ids,
        source_manifest=source_manifest, fold_manifest=fold_manifest, aggregation_unit=aggregation_unit)
    return _histogram_payload(histogram, prints, contracts, ids, source_manifest, fold_manifest,
                              aggregation_unit, coverage_complete, identity)


def _histogram_payload(histogram, prints, contracts, member_ids, source_manifest, fold_manifest,
                       aggregation_unit, coverage_complete, identity):
    return {"version": VERSION, "histogram": histogram, "prints": prints, "contracts": contracts,
            "distinct_sizes": len(histogram),
            "quantity_weighted_mass": tuple((size, size * count) for size, count in histogram),
            "member_ids": member_ids, "source_manifest": source_manifest, "fold_manifest": fold_manifest,
            "aggregation_unit": aggregation_unit, "coverage_complete": coverage_complete,
            "identity": identity, "publication_status": "unpublished",
            "admitted_training_sample": False, "output_kind": _UNPUBLISHED,
            "admitted_for_serving": False}


def merge_histogram_reports(*reports, maximum_distinct_sizes=DEFAULT_DISTINCT_SIZES):
    """Union complete compatible summaries without allocating their prints."""
    if type(maximum_distinct_sizes) is not int or not 1 <= maximum_distinct_sizes <= MAX_DISTINCT_SIZES:
        raise ContractError("distinct-size capacity must be an explicit bounded integer")
    if len(reports) < 2:
        raise ContractError("merging histograms requires at least two complete reports")
    parsed = [_validate_histogram_report(report) for report in reports]
    first = parsed[0]
    members = []
    seen = set()
    counts = {}
    prints = contracts = 0
    for item in parsed:
        if not item["coverage_complete"]:
            raise ContractError("only complete histogram summaries can be merged")
        if ((item["source_manifest"], item["fold_manifest"], item["aggregation_unit"]) !=
                (first["source_manifest"], first["fold_manifest"], first["aggregation_unit"])):
            raise ContractError("merged histograms must share explicit source, fold and unit identity")
        for member in item["member_ids"]:
            if member in seen:
                raise ContractError("duplicated source-window evidence cannot be merged")
            seen.add(member)
            members.append(member)
        for size, count in item["histogram"]:
            counts[size] = counts.get(size, 0) + count
        if len(counts) > maximum_distinct_sizes:
            raise ContractError("merged histogram exceeds its distinct-size capacity")
        prints += item["prints"]
        contracts += item["contracts"]
    members = tuple(sorted(members))
    histogram = tuple(sorted(counts.items()))
    if sum(size * count for size, count in histogram) != contracts:
        raise IntegrityError("merged count times size does not reconcile")
    identity = _histogram_identity(
        histogram=histogram, prints=prints, contracts=contracts, member_ids=members,
        source_manifest=first["source_manifest"], fold_manifest=first["fold_manifest"],
        aggregation_unit=first["aggregation_unit"])
    return _histogram_payload(histogram, prints, contracts, members, first["source_manifest"],
                              first["fold_manifest"], first["aggregation_unit"], True, identity)


class TradeSizeHistogram:
    """Streaming exact (size, count) sufficient statistic.

    Kernel state alone is not an admitted historical training sample. The
    caller supplies source/fold manifests and later training-member identities.
    """

    def __init__(self, *, source_manifest, fold_manifest, maximum_distinct_sizes=DEFAULT_DISTINCT_SIZES,
                 aggregation_unit=None):
        if type(maximum_distinct_sizes) is not int or not 1 <= maximum_distinct_sizes <= MAX_DISTINCT_SIZES:
            raise ContractError("distinct-size capacity must be an explicit bounded integer")
        if aggregation_unit is not None:
            bounded_name(aggregation_unit)
        self.maximum_distinct_sizes = maximum_distinct_sizes
        self.source_manifest = _freeze_manifest(source_manifest)
        self.fold_manifest = _freeze_manifest(fold_manifest)
        self.aggregation_unit = aggregation_unit
        self._counts = {}
        self._members = set()
        self._prints = 0
        self._contracts = 0
        self._failed = False
        self._closed = False

    def __enter__(self):
        self._require_live()
        return self

    def __exit__(self, exc_type, exc, tb):
        self.close()
        return False

    def close(self):
        self._closed = True
        self._counts = {}
        self._members = set()

    def _require_live(self):
        if self._failed:
            raise IntegrityError(_FAILED)
        if self._closed:
            raise IntegrityError("a closed size histogram cannot accept or publish state")

    def _fail(self):
        self._failed = True

    def add_prepared(self, prepared, left, right, *, member_id):
        self._require_live()
        try:
            if not isinstance(prepared, PreparedTradeBatch) or prepared.released:
                raise IntegrityError(_PROJECTION)
            left, right = _row_index(left), _row_index(right)
            if not 0 <= left <= right <= prepared._n:
                raise IntegrityError(_PROJECTION)
            if left == right:
                self._members.add(bounded_name(member_id))
                return
            self._add_sizes(prepared.values["size"][left:right], member_id=member_id)
        except BaseException:
            self._fail()
            raise

    def add_sizes(self, sizes, *, member_id):
        self._require_live()
        try:
            self._add_sizes(_eligible_size_values(sizes), member_id=member_id)
        except BaseException:
            self._fail()
            raise

    def add(self, table, *, member_id):
        self._require_live()
        try:
            if not len(table):
                with prepare_trade_batch(table) as prepared:
                    self.add_prepared(prepared, 0, 0, member_id=member_id)
            else:
                for offset in range(0, len(table), BATCH_ROWS):
                    with prepare_trade_batch(table.slice(offset, BATCH_ROWS)) as prepared:
                        self.add_prepared(prepared, 0, len(prepared), member_id=member_id)
        except BaseException:
            self._fail()
            raise

    def _add_sizes(self, sizes, *, member_id):
        import numpy as np

        bounded_name(member_id)
        n = len(sizes)
        if n > BATCH_ROWS:
            raise ContractError("size batches cannot exceed the prepared-trade row bound")
        self._members.add(member_id)
        if not n:
            return
        values = np.asarray(sizes)
        if values.ndim != 1:
            raise ContractError("eligible whole-print sizes must be exact positive integers")
        unique, counts = np.unique(values, return_counts=True)
        added_prints = 0
        added_contracts = 0
        pending = []
        for size, count in zip(unique, counts, strict=True):
            size, count = int(size), int(count)
            if not 1 <= size <= MAX_ELIGIBLE_SIZE or count < 1:
                raise ContractError("eligible whole-print sizes must be exact positive integers")
            pending.append((size, count))
            added_prints += count
            added_contracts += size * count
        new_sizes = sum(1 for size, _ in pending if size not in self._counts)
        if len(self._counts) + new_sizes > self.maximum_distinct_sizes:
            raise ContractError("size histogram exceeds its distinct-size capacity")
        for size, count in pending:
            self._counts[size] = self._counts.get(size, 0) + count
        self._prints += added_prints
        self._contracts += added_contracts

    def merge_complete(self, report):
        self._require_live()
        try:
            item = _validate_histogram_report(report)
            if not item["coverage_complete"]:
                raise ContractError("only complete histogram summaries can be merged")
            if ((item["source_manifest"], item["fold_manifest"], item["aggregation_unit"]) !=
                    (self.source_manifest, self.fold_manifest, self.aggregation_unit)):
                raise ContractError("merged histograms must share explicit source, fold and unit identity")
            if self._members.intersection(item["member_ids"]):
                raise ContractError("duplicated source-window evidence cannot be merged")
            new_sizes = sum(1 for size, _ in item["histogram"] if size not in self._counts)
            if len(self._counts) + new_sizes > self.maximum_distinct_sizes:
                raise ContractError("merged histogram exceeds its distinct-size capacity")
            for size, count in item["histogram"]:
                self._counts[size] = self._counts.get(size, 0) + count
            self._members.update(item["member_ids"])
            self._prints += item["prints"]
            self._contracts += item["contracts"]
        except BaseException:
            self._fail()
            raise

    def record(self, *, coverage_complete):
        self._require_live()
        if type(coverage_complete) is not bool:
            raise ContractError("histogram coverage is an explicit separate input")
        histogram = tuple(sorted(self._counts.items()))
        if sum(count for _, count in histogram) != self._prints:
            raise IntegrityError("histogram print totals do not reconcile")
        if sum(size * count for size, count in histogram) != self._contracts:
            raise IntegrityError("count times size does not reconcile with histogram totals")
        member_ids = tuple(sorted(self._members))
        identity = _histogram_identity(
            histogram=histogram, prints=self._prints, contracts=self._contracts, member_ids=member_ids,
            source_manifest=self.source_manifest, fold_manifest=self.fold_manifest,
            aggregation_unit=self.aggregation_unit)
        return _histogram_payload(histogram, self._prints, self._contracts, member_ids,
                                  self.source_manifest, self.fold_manifest, self.aggregation_unit,
                                  coverage_complete, identity)


def _member_window(record):
    if type(record) is not dict:
        raise ContractError("training member windows must be explicit complete records")
    end, published_at, complete = record.get("end"), record.get("published_at"), record.get("history_complete")
    timestamp(end)
    timestamp(published_at)
    if type(complete) is not bool or published_at < end:
        raise ContractError("training member windows must be explicit complete records")
    return end, published_at, complete


def fit_unpublished_cohort_definition(report, *, train_end, available_at, member_identities,
                                      aggregation_unit, probabilities, weighting="count",
                                      version="empirical-cohort-v1", member_windows):
    """Exact original quantile rule over a complete size histogram.

    This is a pure unpublished kernel. It does not admit F11 serving and does
    not treat a fitted boundary as a fixed source constant.
    """
    if type(report) is TradeSizeHistogram:
        raise ContractError("kernel state alone is not an admitted historical training sample")
    parsed = _validate_histogram_report(report)
    bounded_name(version)
    bounded_name(aggregation_unit)
    timestamp(train_end)
    timestamp(available_at)
    identities = tuple(bounded_name(m) for m in bounded_rows(
        member_identities, MAX_PRINTS, name="cohort training members"))
    probabilities = tuple(exact_number(p) for p in bounded_rows(probabilities, 31, name="cohort probabilities"))
    if (not parsed["coverage_complete"] or not identities or available_at < train_end
            or weighting not in ("count", "volume") or not parsed["prints"]):
        raise ContractError("cohort fit requires historical rows, availability and weighting")
    if parsed["aggregation_unit"] not in (None, aggregation_unit):
        raise ContractError("cohort aggregation differs from the histogram unit")
    if tuple(sorted(set(identities))) != tuple(sorted(identities)):
        raise ContractError("cohort training is empty or duplicates source windows")
    if set(identities) != set(parsed["member_ids"]):
        raise ContractError("training member identities must match the histogram membership")
    if tuple(sorted(set(probabilities))) != probabilities or any(not 0 < p < 1 for p in probabilities):
        raise ContractError("quantile probabilities must be distinct increasing interior fractions")
    if type(member_windows) is not dict or set(member_windows) != set(identities):
        raise ContractError("each training member needs an explicit complete window record")
    for member in identities:
        end, published_at, complete = _member_window(member_windows[member])
        if end > train_end or published_at > train_end or not complete:
            raise ContractError("cohort training must use compatible, complete, available observations")
    total = parsed["prints"] if weighting == "count" else parsed["contracts"]
    thresholds = []
    for p in probabilities:
        mass = 0
        chosen = None
        for size, count in parsed["histogram"]:
            mass += count if weighting == "count" else size * count
            if mass >= p * total:
                chosen = size + 1
                break
        if chosen is None:
            raise IntegrityError("quantile mass never reached the requested interior probability")
        thresholds.append(chosen)
    cuts = (1, *sorted(set(thresholds)), None)
    recipe = {"family": "cohort", "version": version, "window_ids": identities,
              "train_end": train_end, "available_at": available_at, "probabilities": probabilities,
              "weighting": weighting, "requested_thresholds": tuple(thresholds),
              "tie_policy": _TIE_POLICY}
    definition = CohortDefinition(
        version, aggregation_unit,
        tuple(CohortChannel(f"bin:{i}", a, b) for i, (a, b) in enumerate(zip(cuts, cuts[1:]))),
        origin="fitted", available_at=available_at, fit_recipe_id=digest(recipe))
    realized_count = []
    realized_volume = []
    for channel in definition.channels:
        count = volume = 0
        for size, amount in parsed["histogram"]:
            if channel.lower_inclusive <= size and (channel.upper_exclusive is None or size < channel.upper_exclusive):
                count += amount
                volume += size * amount
        realized_count.append(count)
        realized_volume.append(volume)
    realized_count = tuple(realized_count)
    realized_volume = tuple(realized_volume)
    prints, contracts = parsed["prints"], parsed["contracts"]
    return {"definition": definition, "recipe": recipe, "publication_status": "unpublished",
            "realized_count": realized_count, "realized_volume": realized_volume,
            "realized_count_occupancy": tuple(Fraction(c, prints) for c in realized_count),
            "realized_volume_occupancy": tuple(Fraction(v, contracts) for v in realized_volume),
            "histogram_identity": parsed["identity"], "source_manifest": parsed["source_manifest"],
            "fold_manifest": parsed["fold_manifest"], "admitted_for_serving": False,
            "output_kind": _UNPUBLISHED, "fitted_boundary_kind": "unpublished_training_quantile"}


def _soft_spec(knots, index):
    left = knots[index] - knots[index - 1] if index else None
    right = knots[index + 1] - knots[index] if index + 1 < len(knots) else None
    if left and right:
        denom = math.lcm(left, right)
    else:
        denom = left or right or 1
    return denom, left, right


def _int64_prefix_safe(max_size, denom, n):
    if type(max_size) is not int or type(denom) is not int or type(n) is not int:
        return False
    if max_size < 0 or denom < 1 or n < 0:
        return False
    if denom > INT64_MAX or max_size > INT64_MAX:
        return False
    max_term = max_size * denom
    if max_term > INT64_MAX:
        return False
    if n and (max_term > INT64_MAX // n or denom > INT64_MAX // n):
        return False
    return True


@dataclass
class _ChannelSpec:
    index: int
    channel_id: str
    role: str
    kind: str
    denom: int
    lower: int | None = None
    upper: int | None = None
    knots: tuple = ()
    left_gap: int | None = None
    right_gap: int | None = None


@dataclass
class _ChannelState:
    opening: Fraction
    denom: int
    close_delta: int = 0
    high_delta: int = 0
    low_delta: int = 0
    high_at: int | None = None
    low_at: int | None = None
    high_order: int | None = None
    low_order: int | None = None
    buy_num: int = 0
    sell_num: int = 0
    unknown_num: int = 0
    weighted_prints_num: int = 0
    contributing: int = 0

    def value(self, delta):
        return self.opening + Fraction(delta, self.denom)


def _channel_specs(definition):
    if definition.channels:
        return tuple(_ChannelSpec(i, c.id, c.role, "hard", 1, c.lower_inclusive, c.upper_exclusive)
                     for i, c in enumerate(definition.channels))
    specs = []
    for i, knot in enumerate(definition.knots):
        denom, left, right = _soft_spec(definition.knots, i)
        specs.append(_ChannelSpec(i, f"knot:{knot}", "continuous_size_basis", "soft", denom,
                                  knots=definition.knots, left_gap=left, right_gap=right))
    return tuple(specs)


def _int64_spec_scalars(spec):
    # Small denominators do not prove that distant absolute knots/cutoffs fit
    # NumPy's integer scalar conversions (including empty masked expressions).
    values = (spec.lower, spec.upper) if spec.kind == "hard" else spec.knots
    return all(value is None or 0 < value <= INT64_MAX for value in values)


def _weight_num_one(spec, size):
    if spec.kind == "hard":
        if size >= spec.lower and (spec.upper is None or size < spec.upper):
            return spec.denom
        return 0
    knots, i, denom = spec.knots, spec.index, spec.denom
    if size <= knots[0]:
        return denom if i == 0 else 0
    if size >= knots[-1]:
        return denom if i == len(knots) - 1 else 0
    if spec.left_gap is not None and knots[i - 1] <= size < knots[i]:
        return (size - knots[i - 1]) * (denom // spec.left_gap)
    if spec.right_gap is not None and knots[i] <= size < knots[i + 1]:
        return (knots[i + 1] - size) * (denom // spec.right_gap)
    return 0


def _hard_weight_nums(spec, size):
    import numpy as np

    chosen = size >= spec.lower
    if spec.upper is not None:
        chosen = chosen & (size < spec.upper)
    return chosen.astype(np.int64)


def _soft_weight_nums(spec, size):
    import numpy as np

    knots, i, denom = spec.knots, spec.index, spec.denom
    weights = np.zeros(len(size), dtype=np.int64)
    if i == 0:
        weights[size <= knots[0]] = denom
    if i == len(knots) - 1:
        weights[size >= knots[-1]] = denom
    if spec.left_gap is not None:
        left = (size >= knots[i - 1]) & (size < knots[i])
        weights[left] = (size[left] - knots[i - 1]) * (denom // spec.left_gap)
    if spec.right_gap is not None:
        right = (size >= knots[i]) & (size < knots[i + 1])
        weights[right] = (knots[i + 1] - size[right]) * (denom // spec.right_gap)
    return weights


def _apply_python(state, spec, size, side, event_ns, source_order):
    for i in range(len(size)):
        current = int(size[i])
        weight = _weight_num_one(spec, current)
        if not weight:
            continue
        sign = int(side[i])
        state.contributing += 1
        state.weighted_prints_num += weight
        mass = current * weight
        if sign == 1:
            state.buy_num += mass
        elif sign == -1:
            state.sell_num += mass
        else:
            state.unknown_num += mass
        state.close_delta += current * sign * weight
        if state.close_delta > state.high_delta:
            state.high_delta = state.close_delta
            state.high_at = int(event_ns[i])
            state.high_order = int(source_order[i])
        if state.close_delta < state.low_delta:
            state.low_delta = state.close_delta
            state.low_at = int(event_ns[i])
            state.low_order = int(source_order[i])


def _apply_int64(state, spec, size, side, event_ns, source_order, weights):
    import numpy as np

    size64 = size.astype(np.int64, copy=False)
    side64 = side.astype(np.int64, copy=False)
    weight64 = weights.astype(np.int64, copy=False)
    increment = size64 * side64 * weight64
    mass = size64 * weight64
    path = np.cumsum(increment, dtype=np.int64)
    state.contributing += int(np.count_nonzero(weight64))
    state.weighted_prints_num += int(weight64.sum(dtype=np.int64))
    state.buy_num += int(mass[side64 == 1].sum(dtype=np.int64))
    state.sell_num += int(mass[side64 == -1].sum(dtype=np.int64))
    state.unknown_num += int(mass[side64 == 0].sum(dtype=np.int64))
    hi = int(np.argmax(path))
    lo = int(np.argmin(path))
    candidate_high = state.close_delta + int(path[hi])
    candidate_low = state.close_delta + int(path[lo])
    if candidate_high > state.high_delta:
        state.high_delta = candidate_high
        state.high_at = int(event_ns[hi])
        state.high_order = int(source_order[hi])
    if candidate_low < state.low_delta:
        state.low_delta = candidate_low
        state.low_at = int(event_ns[lo])
        state.low_order = int(source_order[lo])
    state.close_delta += int(path[-1])


def _publish_channel(state, spec, *, prints, volume, history_complete):
    denom = state.denom
    buy = Fraction(state.buy_num, denom)
    sell = Fraction(state.sell_num, denom)
    unknown = Fraction(state.unknown_num, denom)
    weighted = Fraction(state.weighted_prints_num, denom)
    close = state.value(state.close_delta)
    high = state.value(state.high_delta)
    low = state.value(state.low_delta)
    signed = buy - sell
    return {"channel_id": spec.channel_id, "role": spec.role, "open": state.opening, "high": high,
            "low": low, "close": close, "high_bounds": (high, high), "low_bounds": (low, low),
            "high_at_ns": state.high_at, "low_at_ns": state.low_at,
            "high_source_order": state.high_order, "low_source_order": state.low_order,
            "high_origin": "opening_baseline" if state.high_at is None else "print",
            "low_origin": "opening_baseline" if state.low_at is None else "print",
            "buy": buy, "sell": sell, "unknown": unknown, "volume": buy + sell + unknown,
            "signed": signed, "weighted_prints": weighted, "contributing_prints": state.contributing,
            "count_occupancy": (weighted / prints) if prints else None,
            "volume_occupancy": ((buy + sell + unknown) / volume) if volume else None,
            "observed_signed_lower": signed - unknown, "observed_signed_upper": signed + unknown,
            "true_signed_lower": (signed - unknown) if history_complete else None,
            "true_signed_upper": (signed + unknown) if history_complete else None,
            "empty_observed_channel": history_complete and state.contributing == 0,
            "history_complete": history_complete}


class CohortWindow:
    """Bounded exact ordered cohort paths over one frozen definition."""

    def __init__(self, *, definition, instrument_id, start_ns, end_ns, latency_ns=250_000_000,
                 maximum_prints=MAX_PRINTS, openings=None, opening_version=None):
        if type(definition) is not CohortDefinition:
            raise ContractError("typed frozen cohort definition required")
        CohortDefinition(**{name: getattr(definition, name) for name in definition.__dataclass_fields__})
        if (type(instrument_id) is not int or instrument_id <= 0
                or type(start_ns) is not int or type(end_ns) is not int
                or not 0 <= start_ns < end_ns < 2**63 - 1_000_000_000
                or type(latency_ns) is not int or not 0 <= latency_ns <= 1_000_000_000
                or type(maximum_prints) is not int or not 1 <= maximum_prints <= MAX_PRINTS):
            raise ContractError("exact raw instrument, bounded event interval and delay scenario required")
        if definition.origin == "fitted" and definition.available_at > start_ns:
            raise DependencyUnavailable("cohort fit was unavailable at window start")
        self.definition = definition
        self.instrument_id = instrument_id
        self.start = start_ns
        self.end = end_ns
        self.delay = latency_ns
        self.maximum_prints = maximum_prints
        self._specs = _channel_specs(definition)
        self._failed = False
        self._init_state(openings, opening_version)

    def _init_state(self, openings, opening_version):
        n = len(self._specs)
        if openings is None:
            openings = (0,) * n
        bounded_rows(openings, 32, name="cohort openings")
        if len(openings) != n:
            raise ContractError("one opening per cohort channel required")
        openings = tuple(exact_number(x) for x in openings)
        if any(openings):
            bounded_name(opening_version)
        elif opening_version is not None:
            bounded_name(opening_version)
        self.opening_version = opening_version
        self.openings = openings
        self._states = [_ChannelState(opening, spec.denom) for opening, spec in zip(openings, self._specs)]
        self.prints = 0
        self.volume = 0
        self.last_at_ns = None
        self.last_source_order = None
        self.first = None
        self.last = None
        self.source_key = None

    def reset(self, *, openings=None, opening_version=None):
        if self._failed:
            raise IntegrityError(_FAILED)
        self._init_state(openings, opening_version)

    def add(self, table):
        if self._failed:
            raise IntegrityError(_FAILED)
        try:
            if not len(table):
                with prepare_trade_batch(table) as prepared:
                    self._ingest_prepared(prepared, 0, 0)
            else:
                for offset in range(0, len(table), BATCH_ROWS):
                    with prepare_trade_batch(table.slice(offset, BATCH_ROWS)) as prepared:
                        self._ingest_prepared(prepared, 0, len(prepared))
        except BaseException:
            self._failed = True
            raise

    def add_prepared(self, prepared, left, right):
        if self._failed:
            raise IntegrityError(_FAILED)
        try:
            self._ingest_prepared(prepared, left, right)
        except BaseException:
            self._failed = True
            raise

    def _ingest_prepared(self, prepared, left, right):
        import numpy as np
        import pyarrow.compute as pc

        if not isinstance(prepared, PreparedTradeBatch) or prepared.released:
            raise IntegrityError(_PROJECTION)
        left, right = _row_index(left), _row_index(right)
        if not 0 <= left <= right <= prepared._n:
            raise IntegrityError(_PROJECTION)
        if left == right:
            return
        source_keys = pc.unique(prepared._source_key.slice(left, right - left)).to_pylist()
        if (len(source_keys) != 1 or type(source_keys[0]) is not str or not source_keys[0]
                or self.source_key is not None and source_keys[0] != self.source_key):
            raise IntegrityError("a cohort window cannot join distinct acquired source streams")
        self.source_key = source_keys[0]
        values = {name: array[left:right] for name, array in prepared.values.items()}
        t, size, side, order = (values[name] for name in ("t", "size", "side", "source_order"))
        if (np.any(values["instrument_id"] != self.instrument_id)
                or np.any(t < self.start) or np.any(t >= self.end)
                or np.any(values["known_at_ns"] != t + self.delay)):
            raise IntegrityError(_MAPPING)
        if (np.any(size <= 0) or np.any(size >= 2**32 - 1) or np.any(~np.isin(side, (-1, 0, 1)))
                or np.any(order < 0)):
            raise ContractError("bounded equal exact arrays of eligible reported-side trades required")
        if self.prints + (right - left) > self.maximum_prints:
            raise ContractError("bounded equal exact arrays of eligible reported-side trades required")
        if (np.any(t[1:] < t[:-1]) or np.any(order[1:] <= order[:-1])
                or self.last_at_ns is not None and int(t[0]) < self.last_at_ns
                or self.last_source_order is not None and int(order[0]) <= self.last_source_order):
            raise IntegrityError("ordered cumulative paths cannot invent or duplicate source order")
        self.last_at_ns, self.last_source_order = int(t[-1]), int(order[-1])

        def observation(i):
            return {"event_ns": int(t[i]), "known_at_ns": int(values["known_at_ns"][i]),
                    "source_order": int(order[i]), "source_row": int(values["source_row"][i]),
                    "source_key": prepared.source_key(left + i)}

        if self.first is None:
            self.first = observation(0)
        self.last = observation(right - left - 1)
        max_size = int(np.max(size))
        for spec, state in zip(self._specs, self._states):
            if _int64_spec_scalars(spec) and _int64_prefix_safe(max_size, spec.denom, right - left):
                weights = _hard_weight_nums(spec, size) if spec.kind == "hard" else _soft_weight_nums(spec, size)
                _apply_int64(state, spec, size, side, t, order, weights)
            else:
                _apply_python(state, spec, size, side, t, order)
        self.prints += right - left
        if _int64_prefix_safe(max_size, 1, right - left):
            self.volume += int(size.astype(np.int64, copy=False).sum(dtype=np.int64))
        else:
            self.volume += sum(int(v) for v in size)

    def record(self, *, source_coverage_complete, coordinate_complete):
        if self._failed or type(source_coverage_complete) is not bool or type(coordinate_complete) is not bool:
            raise IntegrityError("cohort publication needs successful arithmetic and explicit completed coverage")
        history = source_coverage_complete
        channels = tuple(_publish_channel(state, spec, prints=self.prints, volume=self.volume,
                                          history_complete=history)
                         for spec, state in zip(self._specs, self._states))
        partition_volume = sum((c["volume"] for c in channels), Fraction(0))
        partition_prints = sum((c["weighted_prints"] for c in channels), Fraction(0))
        if self.definition.partition:
            if partition_volume != self.volume or partition_prints != self.prints:
                raise IntegrityError("cohort partition lost or duplicated whole-print mass")
        return {"version": VERSION, "publication_status": "unpublished", "output_kind": _UNPUBLISHED,
                "admitted_for_serving": False, "fit_serving_admission": None,
                "definition_id": self.definition.id, "definition_version": self.definition.version,
                "definition_origin": self.definition.origin,
                "definition_available_at": self.definition.available_at,
                "fit_recipe_id": self.definition.fit_recipe_id,
                "aggregation_unit": self.definition.aggregation_unit,
                "partition": self.definition.partition, "instrument_id": self.instrument_id,
                "event_start_ns": self.start, "event_end_ns": self.end,
                "known_at_ns": self.end + self.delay, "source_delay_ns": self.delay,
                "mathematical_opening_version": self.opening_version, "openings": self.openings,
                "source_coverage_complete": source_coverage_complete,
                "coordinate_complete": coordinate_complete, "flow_history_complete": history,
                "prints": self.prints, "volume": self.volume, "channels": channels,
                "partition_volume": partition_volume, "partition_weighted_prints": partition_prints,
                "source_key": self.source_key,
                "first_print": None if self.first is None else dict(self.first),
                "last_print": None if self.last is None else dict(self.last),
                "empty_observed_window": history and self.prints == 0,
                "order_basis": "original single-source storage order; provider sequence absent",
                "ordering_scope": "prepared stream within this window; no cross-source join",
                "fitted_boundary_kind": None if self.definition.origin == "fixed" else "unpublished_training_quantile"}
