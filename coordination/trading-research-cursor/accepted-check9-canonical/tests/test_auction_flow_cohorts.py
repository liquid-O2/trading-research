from fractions import Fraction
import math
import unittest

import numpy as np
import pyarrow as pa

from references import measurement_flow_literal as literal
from trading_research.errors import ContractError, DependencyUnavailable, IntegrityError
from trading_research.foundations.units import Ticks
from trading_research.measurements.cvd import (
    CohortChannel, CohortDefinition, _cohort_path, exact_number, fit_cohort_definition,
    fixed_source_cohort,
)
from trading_research.measurements.tape import Trade
from trading_research.research.auction_flow_cohorts import (
    BATCH_ROWS, INT64_MAX, MAX_ELIGIBLE_SIZE, VERSION, CohortWindow, TradeSizeHistogram,
    complete_histogram_report, fit_unpublished_cohort_definition, merge_histogram_reports,
)
from trading_research.research.auction_flow_windows import prepare_trade_batch
from tests.measurement_fixtures import CASES, UNIT, capture, gold_capture, row
from tests.test_auction_flow_prepared_trades import (
    FROZEN_MANIFEST, FROZEN_MEASUREMENTS, FROZEN_WINDOWS, make_trade_table, trade_row,
)


F = Fraction
ALL = CohortDefinition("all", UNIT, (CohortChannel("all", 1, None),))
PARTITION6 = CohortDefinition("partition6", UNIT, (CohortChannel("low", 1, 6), CohortChannel("high", 6, None)))
SOFT = CohortDefinition("soft", UNIT, (), (10, 20))


def specs_to_trades(specs):
    trades = []
    for i, (at, size, side, order) in enumerate(specs):
        trades.append(Trade(
            id=f"r{i}", source_content_version="v1", instrument="NQ.test", event_at=at,
            known_at=at, price=Ticks(100), size=size, side=None if side == 0 else side,
            order=order, aggregation_unit=UNIT, history_complete=True))
    return tuple(trades)


def reference_paths(specs, definition, openings=None):
    trades = specs_to_trades(specs)
    n = len(definition.channels) or len(definition.knots)
    if openings is None:
        openings = (0,) * n
    openings = tuple(exact_number(x) for x in openings)
    weights = tuple(definition.weights(trade.size) for trade in trades)
    ids = [channel.id for channel in definition.channels] if definition.channels else [
        f"knot:{knot}" for knot in definition.knots]
    return tuple(_cohort_path(trades, (weight[i] for weight in weights), openings[i], ids[i], True)
                 for i in range(n))


def specs_to_table(specs, *, delay=250, instrument_id=1):
    rows = []
    for at, size, side, order in specs:
        raw_side = "B" if side == 1 else "A" if side == -1 else "N"
        rows.append(trade_row(at, source_order=order, size=size, raw_side=raw_side, delay=delay,
                              instrument_id=instrument_id, source_row=order))
    return make_trade_table(rows)


def publish(window, *, source=True, coordinate=True):
    return window.record(source_coverage_complete=source, coordinate_complete=coordinate)


def measure(definition, specs, *, openings=None, opening_version=None, start=0, end=100, delay=250,
            instrument_id=1, maximum_prints=100, splits=None):
    table = specs_to_table(specs, delay=delay, instrument_id=instrument_id)
    version = opening_version
    if openings is not None and any(exact_number(x) for x in openings) and version is None:
        version = "literal-offset"
    window = CohortWindow(definition=definition, instrument_id=instrument_id, start_ns=start,
                          end_ns=end, latency_ns=delay, maximum_prints=maximum_prints,
                          openings=openings, opening_version=version)
    if splits is None:
        window.add(table)
    else:
        with prepare_trade_batch(table) as prepared:
            cursor = 0
            for width in splits:
                window.add_prepared(prepared, cursor, cursor + width)
                cursor += width
            if cursor != len(prepared):
                window.add_prepared(prepared, cursor, len(prepared))
    return publish(window)


def assert_channel_matches(test, channel, reference):
    test.assertEqual(channel["open"], reference.open)
    test.assertEqual(channel["close"], reference.close)
    test.assertEqual(channel["high_bounds"], reference.high_bounds)
    test.assertEqual(channel["low_bounds"], reference.low_bounds)
    test.assertEqual(channel["high"], reference.high_bounds[1])
    test.assertEqual(channel["low"], reference.low_bounds[0])
    test.assertEqual(channel["high_at_ns"], reference.high_at)
    test.assertEqual(channel["low_at_ns"], reference.low_at)
    test.assertEqual(channel["buy"], reference.buy)
    test.assertEqual(channel["sell"], reference.sell)
    test.assertEqual(channel["unknown"], reference.unknown)
    test.assertEqual(channel["volume"], reference.volume)
    test.assertEqual(channel["signed"], reference.signed)
    test.assertEqual(channel["weighted_prints"], reference.weighted_prints)
    test.assertEqual(channel["contributing_prints"], reference.contributing_prints)
    test.assertEqual(channel["high_origin"], reference.high_origin)
    test.assertEqual(channel["low_origin"], reference.low_origin)
    test.assertEqual(channel["observed_signed_lower"], reference.observed_signed_bounds[0])
    test.assertEqual(channel["observed_signed_upper"], reference.observed_signed_bounds[1])
    test.assertEqual(channel["true_signed_lower"], reference.true_signed_bounds[0])
    test.assertEqual(channel["true_signed_upper"], reference.true_signed_bounds[1])


def member_windows(capture):
    window = capture.window
    return {capture.id: {"end": window.end, "published_at": window.published_at,
                         "history_complete": window.history_complete}}


class AuctionFlowCohortReferenceLoadTests(unittest.TestCase):
    def test_explicit_frozen_and_literal_dependencies_are_loaded(self):
        self.assertEqual(literal.weighted_quantile([1, 2, 3, 4], F(1, 2)), 2)
        self.assertTrue(callable(_cohort_path))
        self.assertEqual(ALL.weights(15), (F(1),))
        self.assertEqual(SOFT.weights(15), (F(1, 2), F(1, 2)))
        self.assertIsNotNone(FROZEN_MANIFEST, "the frozen independent trade reference is required")
        self.assertIsNotNone(FROZEN_WINDOWS)
        self.assertIsNotNone(FROZEN_MEASUREMENTS)
        self.assertIn("auction_flow_trades_check7", FROZEN_WINDOWS.__file__)
        self.assertIn("auction_flow_trades_check7", FROZEN_MEASUREMENTS.__file__)


class TradeSizeHistogramTests(unittest.TestCase):
    def histogram(self, **kwargs):
        kwargs.setdefault("source_manifest", "fixture-source")
        kwargs.setdefault("fold_manifest", "fixture-fold")
        kwargs.setdefault("aggregation_unit", UNIT)
        return TradeSizeHistogram(**kwargs)

    def test_prepared_slices_and_explicit_sizes_reconcile_count_times_size(self):
        specs = ((10, 2, 1, 0), (20, 2, -1, 1), (30, 5, 0, 2), (40, 5, 1, 3))
        table = specs_to_table(specs)
        with self.histogram() as hist:
            hist.add_sizes([2, 2, 5, 5], member_id="window-a")
            from_sizes = hist.record(coverage_complete=True)
        with self.histogram() as hist:
            with prepare_trade_batch(table) as prepared:
                hist.add_prepared(prepared, 0, 2, member_id="window-a")
                hist.add_prepared(prepared, 2, 4, member_id="window-a")
            from_prepared = hist.record(coverage_complete=True)
        with self.histogram() as hist:
            hist.add(table, member_id="window-a")
            from_table = hist.record(coverage_complete=True)
        for report in (from_sizes, from_prepared, from_table):
            self.assertEqual(report["histogram"], ((2, 2), (5, 2)))
            self.assertEqual(report["prints"], 4)
            self.assertEqual(report["contracts"], 14)
            self.assertEqual(report["quantity_weighted_mass"], ((2, 4), (5, 10)))
            self.assertEqual(sum(size * count for size, count in report["histogram"]), report["contracts"])
            self.assertEqual(report["publication_status"], "unpublished")
            self.assertFalse(report["admitted_training_sample"])
            self.assertEqual(report["member_ids"], ("window-a",))
            self.assertEqual(report["version"], VERSION)
        self.assertEqual(from_sizes["identity"], from_prepared["identity"])
        self.assertEqual(from_sizes, from_table)

    def test_merged_summaries_add_huge_counts_without_expanding_prints(self):
        small = self.histogram()
        small.add_sizes([1, 2], member_id="tiny")
        tiny = small.record(coverage_complete=True)
        huge = complete_histogram_report(
            pairs=((2, 10**18), (3, 10**18 + 7)), member_ids=("huge-window",),
            source_manifest="fixture-source", fold_manifest="fixture-fold",
            coverage_complete=True, aggregation_unit=UNIT)
        merged = merge_histogram_reports(tiny, huge)
        self.assertEqual(merged["histogram"], ((1, 1), (2, 10**18 + 1), (3, 10**18 + 7)))
        self.assertEqual(merged["prints"], 2 + 2 * 10**18 + 7)
        self.assertEqual(merged["contracts"], 1 + 2 * (10**18 + 1) + 3 * (10**18 + 7))
        self.assertEqual(merged["member_ids"], ("huge-window", "tiny"))
        live = self.histogram()
        live.add_sizes([1, 2], member_id="tiny")
        live.merge_complete(huge)
        self.assertEqual(live.record(coverage_complete=True)["histogram"], merged["histogram"])
        with self.assertRaises(ContractError):
            merge_histogram_reports(tiny, tiny)
        duplicate = self.histogram()
        duplicate.add_sizes([1, 2], member_id="tiny")
        with self.assertRaises(ContractError):
            duplicate.merge_complete(tiny)
        other = complete_histogram_report(
            pairs=((4, 1),), member_ids=("other-window",), source_manifest="other-source",
            fold_manifest="fixture-fold", coverage_complete=True, aggregation_unit=UNIT)
        with self.assertRaises(ContractError):
            merge_histogram_reports(tiny, other)
        incomplete = {**huge, "coverage_complete": False}
        with self.assertRaises(ContractError):
            merge_histogram_reports(tiny, incomplete)

    def test_capacity_poison_bad_sizes_slices_and_close(self):
        hist = self.histogram(maximum_distinct_sizes=2)
        hist.add_sizes([1, 2], member_id="a")
        with self.assertRaises(ContractError):
            hist.add_sizes([3], member_id="a")
        with self.assertRaises(IntegrityError):
            hist.add_sizes([1], member_id="a")
        with self.assertRaises(IntegrityError):
            hist.record(coverage_complete=True)
        with self.assertRaises(ContractError):
            TradeSizeHistogram(source_manifest=None, fold_manifest=None, maximum_distinct_sizes=1_000_001)
        hist = self.histogram()
        with self.assertRaises(ContractError):
            hist.add_sizes([0], member_id="a")
        hist = self.histogram()
        with self.assertRaises(ContractError):
            hist.add_sizes([MAX_ELIGIBLE_SIZE + 1], member_id="a")
        hist = self.histogram()
        with self.assertRaises(ContractError):
            hist.add_sizes([True], member_id="a")
        hist = self.histogram()
        with self.assertRaises(ContractError):
            hist.add_sizes(np.array([1.5]), member_id="a")
        table = specs_to_table(((10, 1, 1, 0), (20, 2, 1, 1)))
        with prepare_trade_batch(table) as prepared:
            for left, right in ((True, 2), (0.5, 2), (-1, 2), (0, 3), (2, 0)):
                hist = self.histogram()
                with self.assertRaises(IntegrityError):
                    hist.add_prepared(prepared, left, right, member_id="a")
                with self.assertRaises(IntegrityError):
                    hist.add_sizes([1], member_id="a")
        prepared = prepare_trade_batch(table)
        prepared.close()
        hist = self.histogram()
        with self.assertRaises(IntegrityError):
            hist.add_prepared(prepared, 0, 2, member_id="a")
        hist = self.histogram()
        hist.add_sizes([4], member_id="a")
        hist.close()
        with self.assertRaises(IntegrityError):
            hist.record(coverage_complete=True)

    def test_public_large_table_uses_bounded_slices_and_keeps_owned_buffers(self):
        count = BATCH_ROWS + 1
        table = make_trade_table([trade_row(i, source_order=i) for i in range(count)])
        hist = self.histogram()
        hist.add(table, member_id="wide")
        report = hist.record(coverage_complete=True)
        self.assertEqual(report["prints"], count)
        self.assertEqual(report["histogram"], ((1, count),))
        with self.assertRaises(ContractError):
            prepare_trade_batch(table)
        table = specs_to_table(((10, 7, 1, 0), (20, 11, -1, 1)))
        sizes = np.array([7, 11], dtype=np.int64)
        table = table.set_column(table.schema.get_field_index("size"), "size", pa.array(sizes))
        hist = self.histogram()
        with prepare_trade_batch(table) as prepared:
            sizes[:] = 99
            hist.add_prepared(prepared, 0, 2, member_id="owned")
            self.assertEqual(prepared.values["size"].tolist(), [7, 11])
        self.assertEqual(hist.record(coverage_complete=True)["histogram"], ((7, 1), (11, 1)))
        self.assertTrue(prepared.released)


class UnpublishedQuantileFitTests(unittest.TestCase):
    def fit_from_sizes(self, sizes, *, probabilities, weighting="count", train_end=10,
                       available_at=11, member_id="train-a", end=8, published_at=9):
        hist = TradeSizeHistogram(source_manifest="fixture-source", fold_manifest="fixture-fold",
                                  aggregation_unit=UNIT)
        hist.add_sizes(sizes, member_id=member_id)
        report = hist.record(coverage_complete=True)
        return fit_unpublished_cohort_definition(
            report, train_end=train_end, available_at=available_at, member_identities=(member_id,),
            aggregation_unit=UNIT, probabilities=probabilities, weighting=weighting,
            member_windows={member_id: {"end": end, "published_at": published_at, "history_complete": True}})

    def test_count_and_volume_thresholds_match_scalar_training_recipe(self):
        view, captured = capture([row(str(size), at=size, size=size) for size in (1, 2, 3, 4)],
                                 end=8, published=9)
        for weighting, cutoff, lower in (("count", 3, 3), ("volume", 4, 6)):
            scalar = fit_cohort_definition((captured,), view=view, train_end=10, available_at=11,
                                           probabilities=(F(1, 2),), weighting=weighting)
            hist = TradeSizeHistogram(source_manifest="fixture-source", fold_manifest="fixture-fold",
                                      aggregation_unit=UNIT)
            hist.add_sizes([1, 2, 3, 4], member_id=captured.id)
            actual = fit_unpublished_cohort_definition(
                hist.record(coverage_complete=True), train_end=10, available_at=11,
                member_identities=(captured.id,), aggregation_unit=UNIT,
                probabilities=(F(1, 2),), weighting=weighting, member_windows=member_windows(captured))
            self.assertEqual(actual["definition"], scalar["definition"])
            self.assertEqual(actual["recipe"]["requested_thresholds"], scalar["recipe"]["requested_thresholds"])
            self.assertEqual(actual["recipe"]["tie_policy"], "lower_bin_then_merge_empty")
            self.assertEqual(actual["realized_count"], scalar["realized_count"])
            self.assertEqual(actual["realized_volume"], scalar["realized_volume"])
            self.assertEqual(actual["publication_status"], "unpublished")
            self.assertFalse(actual["admitted_for_serving"])
            self.assertEqual(actual["definition"].channels[1].lower_inclusive, cutoff)
            self.assertEqual(actual["realized_volume"][0], lower)
            self.assertEqual(literal.weighted_quantile([1, 2, 3, 4], F(1, 2), volume=weighting == "volume") + 1,
                             cutoff)
            self.assertEqual(actual["definition"].origin, "fitted")

    def test_quartiles_top35_ties_and_repeated_thresholds(self):
        quartiles = self.fit_from_sizes([1, 2, 3, 4], probabilities=(F(1, 4), F(1, 2), F(3, 4)))
        self.assertEqual([c.lower_inclusive for c in quartiles["definition"].channels], [1, 2, 3, 4])
        self.assertEqual(quartiles["realized_count"], (1, 1, 1, 1))
        top = self.fit_from_sizes(list(range(1, 21)), probabilities=(F(13, 20),))
        self.assertEqual(top["definition"].channels[1].lower_inclusive, 14)
        self.assertEqual(top["realized_count"], (13, 7))
        self.assertEqual(top["realized_count_occupancy"][1], F(7, 20))
        tied = self.fit_from_sizes([1] * 12 + [50] * 2 + [100] * 6, probabilities=(F(13, 20),))
        self.assertEqual(tied["recipe"]["requested_thresholds"], (51,))
        self.assertEqual(tied["realized_count"], (14, 6))
        self.assertEqual(tied["realized_count_occupancy"][1], F(6, 20))
        self.assertNotEqual(tied["realized_count_occupancy"][1], F(7, 20))
        repeated = self.fit_from_sizes([5, 5, 5, 5], probabilities=(F(1, 4), F(1, 2), F(3, 4)))
        self.assertEqual(repeated["recipe"]["requested_thresholds"], (6, 6, 6))
        self.assertEqual(len(repeated["definition"].channels), 2)
        self.assertEqual(repeated["realized_count"], (4, 0))
        huge = complete_histogram_report(
            pairs=((1, 10**18), (2, 10**18)), member_ids=("huge-window",),
            source_manifest="fixture-source", fold_manifest="fixture-fold",
            coverage_complete=True, aggregation_unit=UNIT)
        fitted = fit_unpublished_cohort_definition(
            huge, train_end=10, available_at=11, member_identities=("huge-window",),
            aggregation_unit=UNIT, probabilities=(F(1, 2),), weighting="count",
            member_windows={"huge-window": {"end": 8, "published_at": 9, "history_complete": True}})
        self.assertEqual(fitted["definition"].channels[1].lower_inclusive, 2)
        self.assertEqual(fitted["realized_count"], (10**18, 10**18))

    def test_empty_incomplete_duplicate_future_and_kernel_state_are_rejected(self):
        hist = TradeSizeHistogram(source_manifest="fixture-source", fold_manifest="fixture-fold",
                                  aggregation_unit=UNIT)
        hist.add_sizes([1, 2, 3], member_id="train-a")
        complete = hist.record(coverage_complete=True)
        incomplete = hist.record(coverage_complete=False)
        windows = {"train-a": {"end": 8, "published_at": 9, "history_complete": True}}
        kwargs = dict(train_end=10, available_at=11, member_identities=("train-a",),
                      aggregation_unit=UNIT, probabilities=(F(1, 2),), member_windows=windows)
        with self.assertRaises(ContractError):
            fit_unpublished_cohort_definition(hist, **kwargs)
        with self.assertRaises(ContractError):
            fit_unpublished_cohort_definition(incomplete, **kwargs)
        with self.assertRaises(ContractError):
            fit_unpublished_cohort_definition(complete, **{**kwargs, "member_identities": ()})
        with self.assertRaises(ContractError):
            fit_unpublished_cohort_definition(complete, **{**kwargs, "member_identities": ("train-a", "train-a")})
        with self.assertRaises(ContractError):
            fit_unpublished_cohort_definition(complete, **{**kwargs, "member_identities": ("other",)})
        with self.assertRaises(ContractError):
            fit_unpublished_cohort_definition(complete, **{**kwargs, "available_at": 9})
        with self.assertRaises(ContractError):
            fit_unpublished_cohort_definition(
                complete, **{**kwargs, "member_windows": {"train-a": {
                    "end": 12, "published_at": 9, "history_complete": True}}})
        with self.assertRaises(ContractError):
            fit_unpublished_cohort_definition(
                complete, **{**kwargs, "member_windows": {"train-a": {
                    "end": 8, "published_at": 9, "history_complete": False}}})
        empty = TradeSizeHistogram(source_manifest="fixture-source", fold_manifest="fixture-fold",
                                   aggregation_unit=UNIT)
        empty.add_sizes([], member_id="train-a")
        with self.assertRaises(ContractError):
            fit_unpublished_cohort_definition(empty.record(coverage_complete=True), **kwargs)


class CohortWindowPathTests(unittest.TestCase):
    def test_absolute_knots_and_cutoffs_beyond_int64_keep_the_exact_domain(self):
        huge = 2**80
        specs = ((1, 5, 1, 0), (2, MAX_ELIGIBLE_SIZE, -1, 1), (3, 7, 0, 2))
        definitions = (
            CohortDefinition("distant-hard", UNIT, (
                CohortChannel("below", 1, huge), CohortChannel("above", huge, None))),
            CohortDefinition("distant-soft", UNIT, (), (huge, huge + 1, huge + 3)),
            CohortDefinition("single-distant-knot", UNIT, (), (huge,)),
            CohortDefinition("full-32-knot-basis", UNIT, (), tuple(range(1, 33))),
        )
        for definition in definitions:
            result = measure(definition, specs)
            for channel, reference in zip(result["channels"], reference_paths(specs, definition), strict=True):
                assert_channel_matches(self, channel, reference)
            self.assertEqual(result["partition_volume"], sum(row[1] for row in specs))

    def test_source_join_rejected_and_returned_addresses_cannot_mutate_state(self):
        table = specs_to_table(((10, 2, 1, 0), (20, 3, -1, 1)))
        window = CohortWindow(definition=ALL, instrument_id=1, start_ns=0, end_ns=100, latency_ns=250)
        window.add(table)
        result = publish(window)
        result["first_print"]["source_row"] = 999
        result["last_print"]["source_order"] = 999
        self.assertEqual(publish(window)["first_print"]["source_row"], 0)
        self.assertEqual(publish(window)["last_print"]["source_order"], 1)
        changed = table.set_column(table.schema.get_field_index("source_key"), "source_key", pa.array(["one", "two"]))
        for pieces in ((changed,), (changed.slice(0, 1), changed.slice(1, 1))):
            candidate = CohortWindow(definition=ALL, instrument_id=1, start_ns=0, end_ns=100, latency_ns=250)
            with self.assertRaises(IntegrityError):
                for part in pieces:
                    candidate.add(part)
            with self.assertRaises(IntegrityError):
                publish(candidate)

    def test_zero_close_nonzero_extrema_match_literal_and_cohort_path(self):
        specs = ((1, 10, 1, 0), (2, 20, -1, 1), (3, 10, 1, 2))
        for openings in ((0,), (100,)):
            version = None if openings == (0,) else "literal-offset-100"
            actual = measure(ALL, specs, openings=openings, opening_version=version)
            reference = reference_paths(specs, ALL, openings)
            assert_channel_matches(self, actual["channels"][0], reference[0])
            expected = literal.paths(
                [{"event_at": at, "size": size, "side": side, "order": order, "id": str(order)}
                 for at, size, side, order in specs], openings[0])
            channel = actual["channels"][0]
            self.assertEqual((channel["close"], channel["high_bounds"], channel["low_bounds"]),
                             (expected["close"], expected["high_bounds"], expected["low_bounds"]))
            self.assertEqual((channel["high_source_order"], channel["low_source_order"]), (0, 1))
        self.assertEqual(actual["publication_status"], "unpublished")
        self.assertFalse(actual["admitted_for_serving"])
        self.assertIsNone(actual["fit_serving_admission"])

    def test_opposing_hard_partitions_cancel_only_in_aggregate(self):
        specs = ((1, 5, 1, 0), (2, 5, -1, 1), (3, 10, 0, 2))
        actual = measure(PARTITION6, specs)
        reference = reference_paths(specs, PARTITION6)
        for channel, path in zip(actual["channels"], reference, strict=True):
            assert_channel_matches(self, channel, path)
        low, high = actual["channels"]
        self.assertEqual((low["buy"], low["sell"], low["unknown"]), (5, 5, 0))
        self.assertEqual((high["buy"], high["sell"], high["unknown"]), (0, 0, 10))
        self.assertEqual(low["volume"] + high["volume"], 20)
        self.assertEqual(low["signed"] + high["signed"], 0)
        self.assertEqual(high["true_signed_lower"], -10)
        self.assertEqual(actual["partition_weighted_prints"], 3)

    def test_source_cutoff_neighbors_and_excluded_roles(self):
        specs = ((10, 29, 1, 0), (20, 30, -1, 1), (30, 60, 1, 2), (40, 61, 0, 3),
                 (50, 74, -1, 4), (60, 75, 1, 5), (70, 99, -1, 6), (80, 100, 1, 7))
        for name, included_sizes in (
                ("ny_ge100", {100}),
                ("london_ge75", {75, 99, 100}),
                ("inclusive30_through60", {30, 60})):
            definition = fixed_source_cohort(name)
            actual = measure(definition, specs)
            reference = reference_paths(specs, definition)
            for channel, path in zip(actual["channels"], reference, strict=True):
                assert_channel_matches(self, channel, path)
            included = next(channel for channel in actual["channels"] if channel["channel_id"] == "included")
            self.assertEqual(included["contributing_prints"], len(included_sizes))
            self.assertEqual(included["volume"], sum(included_sizes))
            self.assertEqual(actual["channels"][0]["role"], "excluded_below")
            if name == "inclusive30_through60":
                self.assertEqual(actual["channels"][2]["role"], "excluded_above")
            self.assertEqual(actual["partition_volume"], sum(size for _, size, _, _ in specs))
            self.assertEqual(actual["partition_weighted_prints"], len(specs))

    def test_soft_knot_hits_interiors_outside_and_unity(self):
        cases = (
            ((1, 5, 1, 0), (F(1), F(0))),
            ((1, 10, 1, 0), (F(1), F(0))),
            ((1, 15, 1, 0), (F(1, 2), F(1, 2))),
            ((1, 20, 1, 0), (F(0), F(1))),
            ((1, 25, 1, 0), (F(0), F(1))),
        )
        for specs, weights in cases:
            self.assertEqual(SOFT.weights(specs[1]), weights)
            actual = measure(SOFT, (specs,))
            reference = reference_paths((specs,), SOFT)
            for channel, path in zip(actual["channels"], reference, strict=True):
                assert_channel_matches(self, channel, path)
            self.assertEqual(actual["partition_volume"], specs[1])
            self.assertEqual(sum(channel["weighted_prints"] for channel in actual["channels"]), 1)
        together = ((1, 5, 1, 0), (2, 10, -1, 1), (3, 15, 1, 2), (4, 20, 0, 3), (5, 25, -1, 4))
        actual = measure(SOFT, together)
        reference = reference_paths(together, SOFT)
        for channel, path in zip(actual["channels"], reference, strict=True):
            assert_channel_matches(self, channel, path)
        self.assertEqual(actual["partition_volume"], 75)
        self.assertEqual(actual["partition_weighted_prints"], 5)

    def test_unknown_sign_no_print_channels_and_opening_baseline(self):
        unknown = measure(ALL, ((1, 7, 0, 0),))
        reference = reference_paths(((1, 7, 0, 0),), ALL)
        assert_channel_matches(self, unknown["channels"][0], reference[0])
        self.assertEqual(unknown["channels"][0]["close"], 0)
        self.assertEqual(unknown["channels"][0]["unknown"], 7)
        self.assertEqual((unknown["channels"][0]["true_signed_lower"],
                          unknown["channels"][0]["true_signed_upper"]), (-7, 7))
        empty = measure(ALL, (), openings=(7,), opening_version="offset7")
        self.assertEqual((empty["channels"][0]["open"], empty["channels"][0]["close"],
                          empty["channels"][0]["contributing_prints"]), (7, 7, 0))
        self.assertTrue(empty["channels"][0]["empty_observed_channel"])
        self.assertTrue(empty["empty_observed_window"])
        missing = CohortWindow(definition=ALL, instrument_id=1, start_ns=0, end_ns=100, latency_ns=250)
        unseen = publish(missing, source=False)
        self.assertFalse(unseen["empty_observed_window"])
        self.assertIsNone(unseen["channels"][0]["true_signed_lower"])
        quiet_large = measure(fixed_source_cohort("ny_ge100"), ((1, 29, 1, 0),))
        included = next(channel for channel in quiet_large["channels"] if channel["channel_id"] == "included")
        self.assertTrue(included["empty_observed_channel"])
        self.assertEqual(included["volume"], 0)
        opened = measure(ALL, ((1, 4, -1, 0),), openings=(10,), opening_version="offset10")
        self.assertEqual((opened["channels"][0]["high_origin"], opened["channels"][0]["low_origin"]),
                         ("opening_baseline", "print"))
        self.assertIsNone(opened["channels"][0]["high_source_order"])
        self.assertEqual(opened["channels"][0]["low_source_order"], 0)

    def test_equal_timestamp_strict_order_and_reader_cuts(self):
        specs = ((10, 10, 1, 0), (10, 20, -1, 1), (10, 10, 1, 2))
        whole = measure(ALL, specs)
        split = measure(ALL, specs, splits=(1, 1, 1))
        pairs = measure(ALL, specs, splits=(2, 1))
        reference = reference_paths(specs, ALL)
        for actual in (whole, split, pairs):
            assert_channel_matches(self, actual["channels"][0], reference[0])
            self.assertEqual((actual["channels"][0]["high_source_order"],
                              actual["channels"][0]["low_source_order"]), (0, 1))
        table = specs_to_table(specs)
        window = CohortWindow(definition=ALL, instrument_id=1, start_ns=0, end_ns=100, latency_ns=250)
        window.add(table.slice(0, 1))
        with self.assertRaises(IntegrityError):
            window.add(table.slice(0, 1))
        with self.assertRaises(IntegrityError):
            publish(window)

    def test_resets_and_large_integer_fraction_openings(self):
        specs = ((1, 3, 1, 0), (2, 5, -1, 1))
        huge = 2**80 + 13
        actual = measure(ALL, specs, openings=(huge,), opening_version="huge-int")
        reference = reference_paths(specs, ALL, (huge,))
        assert_channel_matches(self, actual["channels"][0], reference[0])
        self.assertEqual(actual["channels"][0]["high"], huge + 3)
        rational = F(2**80 + 1, 97)
        actual = measure(ALL, specs, openings=(rational,), opening_version="huge-frac")
        reference = reference_paths(specs, ALL, (rational,))
        assert_channel_matches(self, actual["channels"][0], reference[0])
        window = CohortWindow(definition=ALL, instrument_id=1, start_ns=0, end_ns=100, latency_ns=250,
                              openings=(5,), opening_version="first")
        window.add(specs_to_table(((1, 10, 1, 0),)))
        first = publish(window)
        window.reset(openings=(F(1, 6),), opening_version="second")
        window.add(specs_to_table(((2, 10, -1, 1),)))
        second = publish(window)
        self.assertEqual(first["channels"][0]["close"], 15)
        self.assertEqual(second["mathematical_opening_version"], "second")
        self.assertEqual(second["channels"][0]["open"], F(1, 6))
        self.assertEqual(second["channels"][0]["close"], F(1, 6) - 10)
        self.assertEqual(second["definition_id"], first["definition_id"])
        self.assertNotEqual(second["channels"][0]["close"], first["channels"][0]["close"])

    def test_maximum_eligible_size_and_prime_knot_python_fallback(self):
        specs = ((1, MAX_ELIGIBLE_SIZE, 1, 0), (2, MAX_ELIGIBLE_SIZE, -1, 1))
        actual = measure(ALL, specs)
        reference = reference_paths(specs, ALL)
        assert_channel_matches(self, actual["channels"][0], reference[0])
        self.assertEqual(actual["channels"][0]["high"], MAX_ELIGIBLE_SIZE)
        left, right = 1_000_003, 1_000_005
        knots = (1, 1 + left, 1 + left + right)
        definition = CohortDefinition("wide-soft", UNIT, (), knots)
        self.assertEqual(math.gcd(left, right), 1)
        self.assertLess(knots[-1], MAX_ELIGIBLE_SIZE)
        self.assertGreater(MAX_ELIGIBLE_SIZE * math.lcm(left, right), INT64_MAX)
        fallback = ((1, 5, 1, 0), (2, 1 + left, -1, 1), (3, MAX_ELIGIBLE_SIZE, 1, 2),
                    (4, knots[-1] + 9, 0, 3))
        actual = measure(definition, fallback)
        reference = reference_paths(fallback, definition)
        for channel, path in zip(actual["channels"], reference, strict=True):
            assert_channel_matches(self, channel, path)
        self.assertEqual(actual["partition_volume"], sum(size for _, size, _, _ in fallback))
        self.assertEqual(actual["partition_weighted_prints"], 4)
        self.assertEqual(sum(definition.weights(MAX_ELIGIBLE_SIZE), F(0)), 1)
        gap = 3_000_000_017
        pair = CohortDefinition("wide-pair", UNIT, (), (1, 1 + gap))
        self.assertGreater(MAX_ELIGIBLE_SIZE * gap, INT64_MAX)
        pair_specs = ((1, 5, 1, 0), (2, 1 + gap, -1, 1), (3, MAX_ELIGIBLE_SIZE, 0, 2))
        actual = measure(pair, pair_specs)
        reference = reference_paths(pair_specs, pair)
        for channel, path in zip(actual["channels"], reference, strict=True):
            assert_channel_matches(self, channel, path)

    def test_gold_m02_fixtures_and_fitted_definition_remain_unpublished(self):
        gold = (
            ("M02-OHLC-001", ALL, (100,), "literal-offset-100"),
            ("M02-OPEN-001", ALL, (10,), "offset10"),
            ("M02-PARTITION-001", PARTITION6, None, None),
            ("M02-SOFT-001", SOFT, None, None),
        )
        for case_id, definition, openings, version in gold:
            trades = CASES[case_id]["inputs"]["trades"]
            specs = tuple((row["event_at"], row["size"], 0 if row["side"] is None else row["side"], index)
                          for index, row in enumerate(trades))
            actual = measure(definition, specs, openings=openings, opening_version=version)
            reference = reference_paths(specs, definition, openings)
            for channel, path in zip(actual["channels"], reference, strict=True):
                assert_channel_matches(self, channel, path)
        view, captured = gold_capture("M02-FIXED-001")
        self.assertEqual(captured.window.eligible_volume, 449)
        sizes = [1, 2, 3, 4]
        view, captured = capture([row(str(size), at=size, size=size) for size in sizes], end=8, published=9)
        scalar = fit_cohort_definition((captured,), view=view, train_end=10, available_at=11,
                                       probabilities=(F(1, 2),))
        hist = TradeSizeHistogram(source_manifest="fixture-source", fold_manifest="fixture-fold",
                                  aggregation_unit=UNIT)
        hist.add_sizes(sizes, member_id=captured.id)
        fitted = fit_unpublished_cohort_definition(
            hist.record(coverage_complete=True), train_end=10, available_at=11,
            member_identities=(captured.id,), aggregation_unit=UNIT, probabilities=(F(1, 2),),
            member_windows=member_windows(captured))
        self.assertEqual(fitted["definition"], scalar["definition"])
        with self.assertRaises(DependencyUnavailable):
            CohortWindow(definition=fitted["definition"], instrument_id=1, start_ns=10, end_ns=20,
                         latency_ns=250)
        allowed = CohortWindow(definition=fitted["definition"], instrument_id=1,
                               start_ns=fitted["definition"].available_at, end_ns=fitted["definition"].available_at + 20,
                               latency_ns=0)
        allowed.add(make_trade_table([trade_row(fitted["definition"].available_at + 1, source_order=0,
                                                size=4, delay=0)]))
        record = publish(allowed)
        self.assertEqual(record["publication_status"], "unpublished")
        self.assertFalse(record["admitted_for_serving"])
        self.assertEqual(record["fitted_boundary_kind"], "unpublished_training_quantile")
        self.assertEqual(record["definition_id"], fitted["definition"].id)

    def test_public_large_table_isolation_and_nonzero_opening_contract(self):
        count = BATCH_ROWS + 1
        table = make_trade_table([trade_row(i, source_order=i) for i in range(count)])
        window = CohortWindow(definition=ALL, instrument_id=1, start_ns=0, end_ns=count + 1,
                              latency_ns=250, maximum_prints=count)
        window.add(table)
        record = publish(window)
        self.assertEqual(record["prints"], count)
        self.assertEqual(record["channels"][0]["close"], count)
        with self.assertRaises(ContractError):
            prepare_trade_batch(table)
        table = specs_to_table(((10, 7, 1, 0), (20, 11, -1, 1)))
        sizes = np.array([7, 11], dtype=np.int64)
        table = table.set_column(table.schema.get_field_index("size"), "size", pa.array(sizes))
        with prepare_trade_batch(table) as prepared:
            sizes[:] = 99
            window = CohortWindow(definition=ALL, instrument_id=1, start_ns=0, end_ns=100, latency_ns=250)
            window.add_prepared(prepared, 0, 2)
            self.assertEqual(prepared.values["size"].tolist(), [7, 11])
        self.assertEqual(publish(window)["channels"][0]["close"], -4)
        with self.assertRaises(ContractError):
            CohortWindow(definition=ALL, instrument_id=1, start_ns=0, end_ns=100, latency_ns=250,
                         openings=(1,))
        empty = make_trade_table([])
        CohortWindow(definition=ALL, instrument_id=1, start_ns=0, end_ns=100, latency_ns=250).add(empty)
        other = specs_to_table(((10, 1, 1, 0),), instrument_id=2)
        with self.assertRaises(IntegrityError):
            CohortWindow(definition=ALL, instrument_id=1, start_ns=0, end_ns=100, latency_ns=250).add(other)
        delayed = specs_to_table(((10, 1, 1, 0),), delay=250)
        with self.assertRaises(IntegrityError):
            CohortWindow(definition=ALL, instrument_id=1, start_ns=0, end_ns=100, latency_ns=0).add(delayed)
        over = CohortWindow(definition=ALL, instrument_id=1, start_ns=0, end_ns=100, latency_ns=250,
                            maximum_prints=1)
        with self.assertRaises(ContractError):
            over.add(specs_to_table(((10, 1, 1, 0), (20, 1, 1, 1))))


if __name__ == "__main__":
    unittest.main()
