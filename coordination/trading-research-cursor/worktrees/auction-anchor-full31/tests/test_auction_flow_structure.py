"""Independent verification of unpublished causal structure arithmetic.

Expected integer swing geometry is taken from the original DirectionalChanges
and PricePoint objects. Fractional expected values are a local literal
recurrence that does not import or call the candidate kernel. Pivot expected
records come from the original pivot_reference. This module does not execute
registered actual-data validation or claim family completion.
"""
from dataclasses import FrozenInstanceError, asdict
from fractions import Fraction
from types import SimpleNamespace
import random
import unittest

import numpy as np
import pyarrow as pa

from trading_research.errors import ContractError, IntegrityError
from trading_research.foundations.bars import CausalBar
from trading_research.measurements.structure import DirectionalChanges, PricePoint, pivot_reference
from trading_research.operations.artifacts import canonical_json, digest
from trading_research.research.auction_flow_structure import (
    VERSION, FinalBarPivotDefinition, FinalBarPivotStream, FixedThresholdDefinition,
    DirectionalChangeStream, StreamedSwing,
)
from trading_research.research.auction_flow_windows import prepare_trade_batch


DELAY = 5
START = 0
END = 10 ** 12
INSTRUMENT_ID = 1
SOURCE = "src"


def spec(t, source_order, *, price=100, price_valid=1, source_row=None, source_key=SOURCE,
         raw_flags=0, raw_side="B", instrument_id=INSTRUMENT_ID, size=1, known_at_ns=None):
    if price is None:
        price, price_valid = 0, 0
    if source_row is None:
        source_row = source_order
    side = 1 if raw_side == "B" else -1 if raw_side == "A" else 0
    return {
        "t": t, "source_order": source_order, "instrument_id": instrument_id,
        "price": price, "size": size, "side": side, "price_valid": price_valid,
        "source_row": source_row, "source_key": source_key, "raw_flags": raw_flags,
        "raw_side": raw_side, "raw_action": "T",
        "known_at_ns": t + DELAY if known_at_ns is None else known_at_ns,
    }


def table_from(rows, *, source_row_type=None):
    numeric = ("t", "source_order", "instrument_id", "price", "size", "side", "price_valid",
               "source_row", "raw_flags", "known_at_ns")
    arrays = {}
    for name in numeric:
        values = [row[name] for row in rows]
        if name == "source_row" and source_row_type is not None:
            arrays[name] = pa.array(values, type=source_row_type)
        elif name == "price_valid":
            arrays[name] = pa.array(values, type=pa.uint8())
        else:
            arrays[name] = pa.array(values, type=pa.int64())
    arrays["raw_action"] = pa.array([row["raw_action"] for row in rows])
    arrays["raw_side"] = pa.array([row["raw_side"] for row in rows])
    arrays["source_key"] = pa.array([row["source_key"] for row in rows])
    return pa.table(arrays)


def prepared_from(rows, **kwargs):
    return prepare_trade_batch(table_from(rows, **kwargs))


def independent_fixed_definition_id(version, reversal, frozen_at=0):
    """Content identity for a frozen threshold. Does not call the candidate."""
    ticks = Fraction(reversal)
    return digest({"frozen_at": frozen_at, "kind": "fixed_threshold_directional_change",
                   "reversal_ticks": [ticks.numerator, ticks.denominator], "version": version})


def independent_pivot_stream_id(version, left, right, ties, frozen_at=0):
    """Content identity for a frozen pivot stream definition. Does not call the candidate."""
    return digest({"frozen_at": frozen_at, "kind": "final_bar_pivot_stream_definition",
                   "left": left, "right": right, "ties": ties, "version": version})


def independent_pivot_reference_id(left, right, ties):
    """Original pivot_reference definition digest. Does not call the candidate."""
    return digest({"kind": "final_bar_pivot", "left": left, "right": right, "ties": ties})


def tamper_values(prepared, **columns):
    for name, values in columns.items():
        owned = np.array(values, dtype=prepared.values[name].dtype)
        owned.flags.writeable = False
        prepared.values[name] = owned
    return prepared


def definition(version="fixed10", reversal=10, frozen_at=0):
    return FixedThresholdDefinition(version, reversal, frozen_at)


def stream(*definitions, start=START, end=END, delay_ns=DELAY, instrument_id=INSTRUMENT_ID,
           source_key=SOURCE, max_source_rows=50_000_000, max_emitted_rows=500_000):
    if not definitions:
        definitions = (definition(),)
    return DirectionalChangeStream(
        instrument_id=instrument_id, source_key=source_key, start=start, end=end,
        delay_ns=delay_ns, definitions=definitions, max_source_rows=max_source_rows,
        max_emitted_rows=max_emitted_rows)


def geometry(item):
    return (item.side, item.price_ticks, item.extreme_start, item.extreme_end,
            item.confirmed_at, item.status)


def original_swings(prices, times, orders, *, threshold, complete=None, delay=DELAY,
                    definition_version="fixed10"):
    complete = [True] * len(prices) if complete is None else complete
    engine = DirectionalChanges(instrument="NQH5", threshold_ticks=threshold,
                                definition_version=definition_version)
    confirmed = []
    for index, (price, at, order, supported) in enumerate(zip(prices, times, orders, complete)):
        confirmed.extend(engine.add(PricePoint(str(index), "NQH5", at, at + delay, price,
                                               order, supported)))
    return tuple(confirmed), engine


def independent_fractional_swings(points, threshold):
    """Literal scalar recurrence. Does not import or call the candidate kernel."""
    direction = 0
    high = low = origin = None
    output = []
    for point in points:
        if not point["complete"]:
            direction = 0
            high = low = origin = None
            continue
        if high is None:
            high = low = origin = point
            continue
        if point["ticks"] > high["ticks"]:
            high = point
        if point["ticks"] < low["ticks"]:
            low = point
        if direction >= 0 and high["ticks"] - point["ticks"] >= threshold:
            extreme = high
            kind = "segment_first" if direction == 0 else "previous_extreme"
            output.append({"side": "high", "extreme": extreme, "confirmation": point,
                           "origin": origin, "origin_kind": kind, "threshold": Fraction(threshold)})
            direction = -1
            origin = extreme
            high = low = point
        elif direction <= 0 and point["ticks"] - low["ticks"] >= threshold:
            extreme = low
            kind = "segment_first" if direction == 0 else "previous_extreme"
            output.append({"side": "low", "extreme": extreme, "confirmation": point,
                           "origin": origin, "origin_kind": kind, "threshold": Fraction(threshold)})
            direction = 1
            origin = extreme
            high = low = point
    return tuple(output)


def fractional_points(rows):
    return [{
        "complete": row["price_valid"] == 1 and row["raw_flags"] & 4 == 0,
        "ticks": row["price"],
        "event_at": row["t"],
        "known_at": row["known_at_ns"],
        "source_order": row["source_order"],
        "source_row": row["source_row"],
        "source_key": row["source_key"],
    } for row in rows]


def bar(index, high, low, *, published=None, final=True, complete=True, instrument="NQH5",
        definition_version="bar10", empty=False):
    start = index * 10
    end = start + 10
    published_at = end if published is None else published
    observed = end - start if complete else end - start - 1
    if empty:
        return CausalBar(instrument, start, end, definition_version, 0, end, end, final,
                         None, None, None, None, 0, 0, 0, True, complete, observed,
                         (), "coverage", (), published_at)
    return CausalBar(instrument, start, end, definition_version, 0, end, end, final,
                     low, high, low, high, 2, 2, 0, True, complete, observed,
                     (f"a{index}", f"b{index}"), "coverage", (), published_at)


def pivot_stream(*, left=1, right=1, ties="strict", frozen_at=0, version="pivot",
                 max_bars=100_000, max_emitted_rows=200_000, interval_ns=10, instrument="NQH5"):
    return FinalBarPivotStream(
        instrument=instrument, interval_ns=interval_ns,
        definition=FinalBarPivotDefinition(version, left, right, ties, frozen_at),
        max_bars=max_bars, max_emitted_rows=max_emitted_rows)


def add_all(engine, bars):
    emitted = []
    for item in bars:
        emitted.extend(engine.add(item))
    return tuple(emitted)


class LiteralDirectionalCases(unittest.TestCase):
    def assert_point(self, record, row):
        self.assertEqual(record["event_at"], row["t"])
        self.assertEqual(record["known_at"], row["known_at_ns"])
        self.assertEqual(record["ticks"], None if row["price_valid"] == 0 else row["price"])
        self.assertEqual(record["source_order"], row["source_order"])
        self.assertEqual(record["source_row"], row["source_row"])
        self.assertEqual(record["source_key"], row["source_key"])

    def assert_swing(self, got, *, side, extreme, confirmation, origin, origin_kind, threshold,
                     version="fixed10", frozen_at=0):
        expected_id = independent_fixed_definition_id(version, threshold, frozen_at)
        self.assertIsInstance(got, StreamedSwing)
        self.assertTrue(got.unpublished_arithmetic)
        self.assertEqual(got.side, side)
        self.assertEqual(got.price_ticks, extreme["price"])
        self.assertEqual(got.extreme_event_at, extreme["t"])
        self.assertEqual(got.extreme_known_at, extreme["known_at_ns"])
        self.assertEqual(got.extreme_source_order, extreme["source_order"])
        self.assertEqual(got.extreme_source_row, extreme["source_row"])
        self.assertEqual(got.extreme_source_key, extreme["source_key"])
        self.assertEqual(got.confirmation_event_at, confirmation["t"])
        self.assertEqual(got.confirmation_known_at, max(extreme["known_at_ns"], confirmation["known_at_ns"]))
        self.assertEqual(got.confirmation_source_order, confirmation["source_order"])
        self.assertEqual(got.confirmation_source_row, confirmation["source_row"])
        self.assertEqual(got.confirmation_source_key, confirmation["source_key"])
        self.assertEqual(got.origin_event_at, origin["t"])
        self.assertEqual(got.origin_known_at, origin["known_at_ns"])
        self.assertEqual(got.origin_ticks, origin["price"])
        self.assertEqual(got.origin_source_order, origin["source_order"])
        self.assertEqual(got.origin_source_row, origin["source_row"])
        self.assertEqual(got.origin_source_key, origin["source_key"])
        self.assertEqual(got.origin_kind, origin_kind)
        self.assertEqual(got.threshold, Fraction(threshold))
        self.assertEqual(got.definition_id, expected_id)
        self.assertEqual(got.definition_version, version)
        self.assertNotEqual(got.definition_id, version)
        self.assertEqual(got.instrument_id, INSTRUMENT_ID)
        self.assertEqual(got.delay_ns, DELAY)
        self.assertEqual(got.status, "confirmed")
        self.assertEqual(got.extreme_start, extreme["t"])
        self.assertEqual(got.extreme_end, extreme["t"])
        self.assertEqual(got.confirmed_at, max(extreme["known_at_ns"], confirmation["known_at_ns"]))
        self.assertEqual(got.extreme_known_at, got.extreme_event_at + DELAY)
        self.assertEqual(got.confirmation_known_at, got.confirmation_event_at + DELAY)
        self.assertEqual(got.origin_known_at, got.origin_event_at + DELAY)

    def feed(self, rows, *definitions, **kwargs):
        engine = stream(*definitions, **kwargs)
        prepared = prepared_from(rows)
        return engine.add_prepared(prepared), engine

    def test_trend_without_confirmation_exposes_full_provisional_state(self):
        rows = [spec(i + 1, i, price=100 + i) for i in range(4)]
        emitted, engine = self.feed(rows, definition("fixed10", 10))
        self.assertEqual(emitted, ())
        snap = engine.snapshot()
        self.assertEqual(snap["version"], VERSION)
        self.assertTrue(snap["unpublished_arithmetic"])
        self.assertFalse(snap["f09_producer_authenticated"])
        self.assertFalse(snap["venue_completeness_certificate"])
        self.assertEqual(snap["rows"], 4)
        self.assertEqual(snap["reason_counts"]["priced_complete"], 4)
        self.assertEqual(snap["reason_counts"]["resets"], 0)
        provisional = snap["provisional"][0]
        self.assertEqual(provisional["direction"], 0)
        self.assertEqual(provisional["threshold"], Fraction(10))
        self.assertEqual(provisional["complete"], 4)
        self.assertEqual(provisional["incomplete"], 0)
        self.assert_point(provisional["high"], rows[3])
        self.assert_point(provisional["low"], rows[0])
        self.assert_point(provisional["last"], rows[3])
        self.assert_point(provisional["origin"], rows[0])

    def test_high_then_low_asserts_every_field_and_origin_kind(self):
        rows = [spec(1, 0, price=100), spec(2, 1, price=90), spec(3, 2, price=100)]
        emitted, engine = self.feed(rows, definition("fixed10", 10))
        self.assertEqual(len(emitted), 2)
        self.assert_swing(emitted[0], side="high", extreme=rows[0], confirmation=rows[1],
                          origin=rows[0], origin_kind="segment_first", threshold=10)
        self.assert_swing(emitted[1], side="low", extreme=rows[1], confirmation=rows[2],
                          origin=rows[0], origin_kind="previous_extreme", threshold=10)
        snap = engine.snapshot()["provisional"][0]
        self.assertEqual(snap["direction"], 1)
        self.assert_point(snap["high"], rows[2])
        self.assert_point(snap["low"], rows[2])
        self.assert_point(snap["origin"], rows[1])
        self.assert_point(snap["last"], rows[2])
        self.assertEqual(engine.record()["reason_counts"]["confirmed_high"], 1)
        self.assertEqual(engine.record()["reason_counts"]["confirmed_low"], 1)

    def test_initial_upward_move_confirms_low_before_later_high(self):
        rows = [spec(1, 0, price=100), spec(2, 1, price=110), spec(3, 2, price=100)]
        emitted, engine = self.feed(rows, definition("fixed10", 10))
        self.assert_swing(emitted[0], side="low", extreme=rows[0], confirmation=rows[1],
                          origin=rows[0], origin_kind="segment_first", threshold=10)
        self.assert_swing(emitted[1], side="high", extreme=rows[1], confirmation=rows[2],
                          origin=rows[0], origin_kind="previous_extreme", threshold=10)
        self.assertEqual(engine.snapshot()["provisional"][0]["direction"], -1)

    def test_initial_downward_then_upward_is_high_priority_from_direction_zero(self):
        down = [spec(1, 0, price=100), spec(2, 1, price=90)]
        up = [spec(1, 0, price=100), spec(2, 1, price=110)]
        high, _ = self.feed(down, definition("fixed10", 10))
        low, _ = self.feed(up, definition("fixed10", 10))
        self.assertEqual(high[0].side, "high")
        self.assertEqual(low[0].side, "low")
        self.assertEqual(high[0].origin_kind, "segment_first")
        self.assertEqual(low[0].origin_kind, "segment_first")

    def test_exact_integer_threshold_boundary_and_short_move(self):
        exact = [spec(1, 0, price=100), spec(2, 1, price=104)]
        short = [spec(1, 0, price=100), spec(2, 1, price=103)]
        emitted, _ = self.feed(exact, definition("fixed4", 4))
        none, engine = self.feed(short, definition("fixed4", 4))
        self.assert_swing(emitted[0], side="low", extreme=exact[0], confirmation=exact[1],
                          origin=exact[0], origin_kind="segment_first", threshold=4,
                          version="fixed4")
        self.assertEqual(none, ())
        self.assertEqual(engine.snapshot()["provisional"][0]["direction"], 0)
        self.assert_point(engine.snapshot()["provisional"][0]["high"], short[1])

    def test_fractional_threshold_uses_exact_rational_boundary(self):
        short = [spec(1, 0, price=100), spec(2, 1, price=102)]
        exact = [spec(1, 0, price=100), spec(2, 1, price=103)]
        none, _ = self.feed(short, definition("half", Fraction(5, 2)))
        emitted, engine = self.feed(exact, definition("half", Fraction(5, 2)))
        self.assertEqual(none, ())
        self.assert_swing(emitted[0], side="low", extreme=exact[0], confirmation=exact[1],
                          origin=exact[0], origin_kind="segment_first", threshold=Fraction(5, 2),
                          version="half")
        self.assertEqual(emitted[0].threshold, Fraction(5, 2))
        self.assertEqual(engine.snapshot()["provisional"][0]["threshold"], Fraction(5, 2))

    def test_equal_extreme_retains_first_occurrence(self):
        rows = [spec(1, 0, price=100), spec(2, 1, price=110), spec(3, 2, price=110),
                spec(4, 3, price=100)]
        emitted, _ = self.feed(rows, definition("fixed10", 10))
        self.assert_swing(emitted[0], side="low", extreme=rows[0], confirmation=rows[1],
                          origin=rows[0], origin_kind="segment_first", threshold=10)
        self.assert_swing(emitted[1], side="high", extreme=rows[1], confirmation=rows[3],
                          origin=rows[0], origin_kind="previous_extreme", threshold=10)
        self.assertEqual(emitted[1].extreme_event_at, 2)
        self.assertEqual(emitted[1].extreme_source_order, 1)
        lows = [spec(1, 0, price=100), spec(2, 1, price=90), spec(3, 2, price=90),
                spec(4, 3, price=100)]
        emitted, _ = self.feed(lows, definition("fixed10", 10))
        self.assertEqual(emitted[1].extreme_event_at, 2)
        self.assertEqual(emitted[1].extreme_source_order, 1)

    def test_same_time_source_order_confirms_in_physical_order(self):
        rows = [spec(10, 1, price=100), spec(10, 2, price=90), spec(10, 3, price=100)]
        emitted, engine = self.feed(rows, definition("fixed10", 10))
        self.assert_swing(emitted[0], side="high", extreme=rows[0], confirmation=rows[1],
                          origin=rows[0], origin_kind="segment_first", threshold=10)
        self.assert_swing(emitted[1], side="low", extreme=rows[1], confirmation=rows[2],
                          origin=rows[0], origin_kind="previous_extreme", threshold=10)
        self.assertEqual(emitted[0].extreme_event_at, emitted[0].confirmation_event_at)
        self.assertLess(emitted[0].extreme_source_order, emitted[0].confirmation_source_order)
        self.assertEqual(engine.record()["reason_counts"]["rows"], 3)

    def test_unknown_aggressor_does_not_invalidate_priced_path(self):
        rows = [spec(1, 0, price=100, raw_side="N"), spec(2, 1, price=90, raw_side="N")]
        emitted, engine = self.feed(rows, definition("fixed10", 10))
        self.assert_swing(emitted[0], side="high", extreme=rows[0], confirmation=rows[1],
                          origin=rows[0], origin_kind="segment_first", threshold=10)
        self.assertEqual(engine.record()["reason_counts"]["unknown_aggressor"], 2)
        self.assertEqual(engine.record()["reason_counts"]["priced_complete"], 2)

    def test_no_priced_rows_reset_and_count_without_swings(self):
        rows = [spec(1, 0, price=None), spec(2, 1, price=None)]
        emitted, engine = self.feed(rows, definition("fixed10", 10))
        self.assertEqual(emitted, ())
        snap = engine.snapshot()
        self.assertIsNone(snap["provisional"][0]["high"])
        self.assertIsNone(snap["provisional"][0]["low"])
        self.assertIsNone(snap["provisional"][0]["origin"])
        self.assert_point(snap["provisional"][0]["last"], rows[1])
        self.assertEqual(snap["provisional"][0]["direction"], 0)
        self.assertEqual(snap["reason_counts"]["unpriced"], 2)
        self.assertEqual(snap["reason_counts"]["resets"], 2)
        self.assertEqual(snap["reason_counts"]["rows"], 2)
        self.assertEqual(snap["definitions"][0]["incomplete"], 2)
        self.assertEqual(snap["definitions"][0]["complete"], 0)

    def test_flag4_resets_and_does_not_bridge_the_prior_extreme(self):
        rows = [spec(1, 0, price=100), spec(2, 1, price=106), spec(3, 2, price=100, raw_flags=4),
                spec(4, 3, price=100), spec(5, 4, price=90)]
        emitted, engine = self.feed(rows, definition("fixed10", 10))
        self.assertEqual(len(emitted), 1)
        self.assert_swing(emitted[0], side="high", extreme=rows[3], confirmation=rows[4],
                          origin=rows[3], origin_kind="segment_first", threshold=10)
        self.assertEqual(emitted[0].price_ticks, 100)
        self.assertEqual(engine.record()["reason_counts"]["flag4"], 1)
        self.assertEqual(engine.record()["reason_counts"]["resets"], 1)
        self.assertEqual(engine.snapshot()["provisional"][0]["incomplete"], 1)

    def test_segment_incompleteness_resets_and_starts_a_new_leg(self):
        first = [spec(1, 0, price=100), spec(2, 1, price=106)]
        gap = [spec(3, 2, price=103)]
        later = [spec(4, 3, price=100), spec(5, 4, price=90)]
        engine = stream(definition("fixed10", 10))
        prepared = prepared_from(first + gap + later)
        self.assertEqual(engine.add_prepared(prepared, 0, 2, history_complete=True), ())
        self.assertEqual(engine.add_prepared(prepared, 2, 3, history_complete=False), ())
        emitted = engine.add_prepared(prepared, 3, 5, history_complete=True)
        self.assert_swing(emitted[0], side="high", extreme=later[0], confirmation=later[1],
                          origin=later[0], origin_kind="segment_first", threshold=10)
        self.assertEqual(engine.record()["reason_counts"]["incomplete_segment"], 1)
        self.assertEqual(engine.snapshot()["provisional"][0]["origin"]["event_at"], 4)
        all_incomplete = stream(definition("fixed10", 10))
        self.assertEqual(all_incomplete.add_prepared(prepared, 0, 2, history_complete=False), ())
        emitted = all_incomplete.add_prepared(prepared, 3, 5, history_complete=True)
        self.assertEqual(emitted[0].extreme_event_at, 4)
        self.assertEqual(all_incomplete.record()["reason_counts"]["incomplete_segment"], 2)

    def test_two_definitions_emit_in_tuple_order_on_the_same_confirmation(self):
        rows = [spec(1, 0, price=100), spec(2, 1, price=90)]
        emitted, engine = self.feed(rows, definition("a", 4), definition("b", 10))
        self.assertEqual(tuple(item.definition_id for item in emitted),
                         (independent_fixed_definition_id("a", 4),
                          independent_fixed_definition_id("b", 10)))
        self.assertEqual(tuple(item.definition_version for item in emitted), ("a", "b"))
        self.assertEqual(tuple(item.side for item in emitted), ("high", "high"))
        self.assertEqual(engine.record()["emitted_rows"], 2)
        only_small, _ = self.feed([spec(1, 0, price=100), spec(2, 1, price=95)],
                                  definition("a", 4), definition("b", 10))
        self.assertEqual(tuple(item.definition_id for item in only_small),
                         (independent_fixed_definition_id("a", 4),))


class ReferenceIntegerParity(unittest.TestCase):
    def compare_path(self, prices, times=None, orders=None, *, threshold, complete=None):
        times = list(range(1, len(prices) + 1)) if times is None else times
        orders = list(range(len(prices))) if orders is None else orders
        complete = [True] * len(prices) if complete is None else complete
        expected, reference = original_swings(prices, times, orders, threshold=threshold,
                                              complete=complete)
        rows = []
        for at, order, price, supported in zip(times, orders, prices, complete):
            rows.append(spec(at, order, price=price, raw_flags=0 if supported else 4,
                             source_row=order))
        engine = stream(definition("fixed10", threshold))
        got = engine.add_prepared(prepared_from(rows))
        self.assertEqual(tuple(geometry(item) for item in got), tuple(geometry(item) for item in expected))
        expected_id = independent_fixed_definition_id("fixed10", threshold)
        for item, want in zip(got, expected):
            self.assertEqual(item.side, want.side)
            self.assertEqual(item.price_ticks, want.price_ticks)
            self.assertEqual(item.extreme_start, want.extreme_start)
            self.assertEqual(item.extreme_end, want.extreme_end)
            self.assertEqual(item.confirmed_at, want.confirmed_at)
            self.assertEqual(item.status, want.status)
            extreme_index = int(want.source_versions[0])
            confirm_index = int(want.source_versions[1])
            self.assertEqual(item.extreme_event_at, times[extreme_index])
            self.assertEqual(item.extreme_known_at, times[extreme_index] + DELAY)
            self.assertEqual(item.extreme_source_order, orders[extreme_index])
            self.assertEqual(item.extreme_source_row, orders[extreme_index])
            self.assertEqual(item.confirmation_event_at, times[confirm_index])
            self.assertEqual(item.confirmation_known_at, times[confirm_index] + DELAY)
            self.assertEqual(item.confirmation_source_order, orders[confirm_index])
            self.assertEqual(item.confirmation_source_row, orders[confirm_index])
            self.assertEqual(item.definition_id, expected_id)
            self.assertEqual(item.definition_version, "fixed10")
            self.assertIn(item.origin_kind, ("segment_first", "previous_extreme"))
            self.assertEqual(item.origin_known_at, item.origin_event_at + DELAY)
            self.assertEqual(item.origin_source_key, SOURCE)
            self.assertEqual(item.extreme_source_key, SOURCE)
            self.assertEqual(item.confirmation_source_key, SOURCE)
        snap = engine.snapshot()["provisional"][0]
        self.assertEqual(snap["direction"], reference.direction)
        if reference.high is None:
            self.assertIsNone(snap["high"])
        else:
            self.assertEqual(snap["high"]["ticks"], reference.high.ticks)
            self.assertEqual(snap["high"]["event_at"], reference.high.event_at)
        if reference.low is None:
            self.assertIsNone(snap["low"])
        else:
            self.assertEqual(snap["low"]["ticks"], reference.low.ticks)
            self.assertEqual(snap["low"]["event_at"], reference.low.event_at)
        return got, expected, engine, reference

    def test_objects_reference_path_matches_entire_swing_geometry_and_clocks(self):
        prices = (100, 106, 110, 109, 106)
        got, expected, engine, reference = self.compare_path(prices, threshold=4)
        self.assertEqual(len(expected), 2)
        self.assertEqual(len(got), 2)
        self.assertEqual(geometry(got[0]), ("low", 100, 1, 1, 2 + DELAY, "confirmed"))
        self.assertEqual(geometry(got[1]), ("high", 110, 3, 3, 5 + DELAY, "confirmed"))
        self.assertEqual(geometry(expected[0]), geometry(got[0]))
        self.assertEqual(geometry(expected[1]), geometry(got[1]))
        self.assertEqual(expected[0].source_versions, ("0", "1"))
        self.assertEqual(expected[1].source_versions, ("2", "4"))
        self.assertEqual(got[0].side, "low")
        self.assertEqual(got[0].price_ticks, 100)
        self.assertEqual(got[0].extreme_event_at, 1)
        self.assertEqual(got[0].confirmation_event_at, 2)
        self.assertEqual(got[0].origin_kind, "segment_first")
        self.assertEqual(got[1].side, "high")
        self.assertEqual(got[1].price_ticks, 110)
        self.assertEqual(got[1].extreme_event_at, 3)
        self.assertEqual(got[1].confirmation_event_at, 5)
        self.assertEqual(got[1].origin_kind, "previous_extreme")
        self.assertEqual(got[1].origin_event_at, 1)
        self.assertEqual(got[1].origin_ticks, 100)
        after = list(prices) + [50, 49]
        complete = [True] * 5 + [False, True]
        got, expected, _, _ = self.compare_path(after, threshold=4, complete=complete)
        self.assertEqual(tuple(geometry(item) for item in got), tuple(geometry(item) for item in expected))

    def test_high_then_low_and_prefix_match_original_directional_changes(self):
        self.compare_path((100, 90, 100), threshold=10)
        self.compare_path((100, 110, 100), threshold=10)
        self.compare_path((100, 101, 102, 103), threshold=10)
        self.compare_path((100, 104), threshold=4)
        self.compare_path((100, 103), threshold=4)
        self.compare_path((100, 110, 110, 100), threshold=10)
        self.compare_path((100, 90, 90, 100), threshold=10)
        self.compare_path((100, 90, 100), times=(10, 10, 10), orders=(1, 2, 3), threshold=10)

    def test_deterministic_randomized_small_paths_match_original(self):
        rng = random.Random(20260908)
        for _ in range(24):
            count = rng.randint(4, 16)
            prices = [100 + rng.randint(-12, 12) for _ in range(count)]
            times = [1]
            for _ in range(count - 1):
                times.append(times[-1] if rng.random() < 0.25 else times[-1] + rng.randint(1, 3))
            complete = [True] * count
            if rng.random() < 0.35:
                complete[rng.randrange(count)] = False
            self.compare_path(prices, times, list(range(count)),
                              threshold=rng.choice((2, 3, 4, 5)), complete=complete)


class FractionalIndependentRecurrence(unittest.TestCase):
    def test_fractional_paths_match_literal_recurrence_not_the_candidate(self):
        cases = (
            ([100, 102], Fraction(5, 2)),
            ([100, 103], Fraction(5, 2)),
            ([100, 90, 100], Fraction(19, 2)),
            ([100, 110, 110, 100], Fraction(1, 2)),
            ([100, 106, 103, 100], Fraction(5, 2)),
        )
        for prices, threshold in cases:
            rows = [spec(i + 1, i, price=price) for i, price in enumerate(prices)]
            expected = independent_fractional_swings(fractional_points(rows), threshold)
            got = stream(definition("frac", threshold)).add_prepared(prepared_from(rows))
            self.assertEqual(len(got), len(expected))
            expected_id = independent_fixed_definition_id("frac", threshold)
            for item, want in zip(got, expected):
                self.assertEqual(item.side, want["side"])
                self.assertEqual(item.price_ticks, want["extreme"]["ticks"])
                self.assertEqual(item.extreme_event_at, want["extreme"]["event_at"])
                self.assertEqual(item.extreme_known_at, want["extreme"]["known_at"])
                self.assertEqual(item.extreme_source_order, want["extreme"]["source_order"])
                self.assertEqual(item.extreme_source_row, want["extreme"]["source_row"])
                self.assertEqual(item.extreme_source_key, want["extreme"]["source_key"])
                self.assertEqual(item.confirmation_event_at, want["confirmation"]["event_at"])
                self.assertEqual(item.confirmation_known_at, want["confirmation"]["known_at"])
                self.assertEqual(item.confirmation_source_order, want["confirmation"]["source_order"])
                self.assertEqual(item.confirmation_source_row, want["confirmation"]["source_row"])
                self.assertEqual(item.confirmation_source_key, want["confirmation"]["source_key"])
                self.assertEqual(item.origin_event_at, want["origin"]["event_at"])
                self.assertEqual(item.origin_known_at, want["origin"]["known_at"])
                self.assertEqual(item.origin_ticks, want["origin"]["ticks"])
                self.assertEqual(item.origin_source_order, want["origin"]["source_order"])
                self.assertEqual(item.origin_source_row, want["origin"]["source_row"])
                self.assertEqual(item.origin_source_key, want["origin"]["source_key"])
                self.assertEqual(item.origin_kind, want["origin_kind"])
                self.assertEqual(item.threshold, want["threshold"])
                self.assertEqual(item.definition_id, expected_id)
                self.assertEqual(item.definition_version, "frac")
                self.assertEqual(item.confirmed_at, max(want["extreme"]["known_at"],
                                                       want["confirmation"]["known_at"]))


class BatchSliceAndGuardrails(unittest.TestCase):
    def path_rows(self):
        return [spec(1, 0, price=100), spec(2, 1, price=90), spec(3, 2, price=100),
                spec(4, 3, price=110), spec(5, 4, price=100)]

    def test_slice_cuts_at_every_index_and_inside_a_timestamp_tie(self):
        rows = self.path_rows()
        prepared = prepared_from(rows)
        full = stream(definition("fixed10", 10)).add_prepared(prepared)
        for index in range(len(rows) + 1):
            engine = stream(definition("fixed10", 10))
            parts = engine.add_prepared(prepared, 0, index) + engine.add_prepared(prepared, index, len(rows))
            self.assertEqual(tuple(asdict(item) for item in parts), tuple(asdict(item) for item in full))
        singles = stream(definition("fixed10", 10))
        assembled = []
        for index in range(len(rows)):
            assembled.extend(singles.add_prepared(prepared, index, index + 1))
        self.assertEqual(tuple(asdict(item) for item in assembled), tuple(asdict(item) for item in full))
        ties = [spec(10, 1, price=100), spec(10, 2, price=90), spec(10, 3, price=100),
                spec(20, 4, price=110)]
        tied = prepared_from(ties)
        together = stream(definition("fixed10", 10)).add_prepared(tied)
        split = stream(definition("fixed10", 10))
        parts = split.add_prepared(tied, 0, 1) + split.add_prepared(tied, 1, 4)
        self.assertEqual(tuple(asdict(item) for item in parts), tuple(asdict(item) for item in together))
        self.assertEqual(together[0].confirmation_source_order, 2)

    def test_65536_batch_boundary_empty_slices_and_uint64_addresses(self):
        count = 65536
        rows = [spec(index + 1, index, price=100 + index % 3, source_row=index) for index in range(count)]
        prepared = prepared_from(rows)
        self.assertEqual(len(prepared), count)
        engine = stream(definition("wide", 10_000))
        self.assertEqual(engine.add_prepared(prepared, 0, count), ())
        self.assertEqual(engine.record()["rows"], count)
        self.assertEqual(engine.add_prepared(prepared, count, count), ())
        self.assertEqual(engine.record()["slices"], 2)
        empty = stream(definition("wide", 10))
        self.assertEqual(empty.add_prepared(prepared_from([]), 0, 0), ())
        self.assertEqual(empty.record()["rows"], 0)
        self.assertEqual(empty.record()["slices"], 1)
        base = 2 ** 63 + 100
        high = [spec(1, 0, price=100, source_row=base), spec(2, 1, price=90, source_row=base + 1),
                spec(3, 2, price=100, source_row=base + 2)]
        got = stream(definition("fixed10", 10)).add_prepared(prepared_from(high, source_row_type=pa.uint64()))
        self.assertGreater(got[0].extreme_source_row, 2 ** 63)
        self.assertEqual(got[0].extreme_source_row, base)
        self.assertEqual(got[0].confirmation_source_row, base + 1)
        self.assertEqual(got[1].origin_source_row, base)
        self.assertEqual(got[1].extreme_source_row, base + 1)

    def test_mutable_arrow_buffer_independence_and_rejected_handles(self):
        price = np.array([100, 90, 100], dtype=np.int64)
        rows = [spec(1, 0, price=100), spec(2, 1, price=90), spec(3, 2, price=100)]
        table = table_from(rows)
        table = table.set_column(table.schema.get_field_index("price"), "price", pa.array(price))
        prepared = prepare_trade_batch(table)
        price[1] = 999
        got = stream(definition("fixed10", 10)).add_prepared(prepared)
        self.assertEqual(got[0].confirmation_event_at, 2)
        self.assertEqual(got[0].price_ticks, 100)
        self.assertEqual(got[1].price_ticks, 90)
        released = prepare_trade_batch(table_from(rows))
        released.release()
        with self.assertRaises(IntegrityError):
            stream(definition("fixed10", 10)).add_prepared(released)
        forged = SimpleNamespace(released=False, values={}, source_key=lambda index: SOURCE)
        forged.__len__ = lambda: 0
        with self.assertRaises(IntegrityError):
            stream(definition("fixed10", 10)).add_prepared(forged)
        mixed = [spec(1, 0, source_key="a"), spec(2, 1, source_key="b")]
        with self.assertRaises(IntegrityError):
            stream(definition("fixed10", 10)).add_prepared(prepared_from(mixed))
        wrong = [spec(1, 0, instrument_id=2)]
        with self.assertRaises(IntegrityError):
            stream(definition("fixed10", 10)).add_prepared(prepared_from(wrong))

    def test_exact_limits_one_over_frozen_rule_and_constant_delay(self):
        rows = [spec(1, 0, price=100), spec(2, 1, price=90), spec(3, 2, price=100)]
        prepared = prepared_from(rows)
        capped = stream(definition("fixed10", 10), max_source_rows=2)
        self.assertEqual(len(capped.add_prepared(prepared, 0, 2)), 1)
        with self.assertRaises(ContractError):
            capped.add_prepared(prepared, 2, 3)
        over = stream(definition("fixed10", 10), max_source_rows=2)
        with self.assertRaises(ContractError):
            over.add_prepared(prepared)
        one = stream(definition("fixed10", 10), max_emitted_rows=1)
        self.assertEqual(len(one.add_prepared(prepared, 0, 2)), 1)
        with self.assertRaises(ContractError):
            one.add_prepared(prepared, 2, 3)
        both = stream(definition("a", 10), definition("b", 10), max_emitted_rows=1)
        with self.assertRaises(ContractError):
            both.add_prepared(prepared, 0, 2)
        with self.assertRaises(ContractError):
            stream(definition("late", 10, frozen_at=10), start=5)
        late = [spec(1, 0, known_at_ns=1 + DELAY + 1)]
        with self.assertRaises(IntegrityError):
            stream(definition("fixed10", 10)).add_prepared(prepared_from(late))
        with self.assertRaises(ContractError):
            FixedThresholdDefinition("x", True, 0)
        with self.assertRaises(ContractError):
            DirectionalChangeStream(instrument_id=True, source_key=SOURCE, start=0, end=10,
                                    delay_ns=DELAY, definitions=(definition(),))
        with self.assertRaises(ContractError):
            stream(definition("fixed10", 10)).add_prepared(prepared, history_complete=1)
        with self.assertRaises(IntegrityError):
            stream(definition("fixed10", 10)).add_prepared(prepared, True, 1)
        with self.assertRaises(ContractError):
            stream(*(definition(f"s{index}", index + 1) for index in range(33)))
        many = stream(*(definition(f"s{index}", index + 1) for index in range(32)))
        self.assertEqual(len(many.record()["definitions"]), 32)
        with self.assertRaises(ContractError):
            stream(definition("dup", 2), definition("dup", 3))
        with self.assertRaises(ContractError):
            stream(definition("same", 4), definition("same", Fraction(4)))
        distinct = stream(definition("x", 4), definition("y", 4))
        self.assertEqual(len(distinct.record()["definitions"]), 2)
        self.assertEqual(distinct.record()["definitions"][0]["id"],
                         independent_fixed_definition_id("x", 4))
        self.assertEqual(distinct.record()["definitions"][0]["version"], "x")
        with self.assertRaises(ContractError):
            stream(definition("fixed10", 10), max_source_rows=50_000_001)
        with self.assertRaises(ContractError):
            stream(definition("fixed10", 10), max_emitted_rows=500_001)

    def test_definition_ids_bind_full_frozen_science_not_the_human_label(self):
        expected = independent_fixed_definition_id("fixed4", 4, 7)
        self.assertEqual(expected, independent_fixed_definition_id("fixed4", Fraction(4), 7))
        self.assertEqual(expected, independent_fixed_definition_id("fixed4", Fraction(4, 1), 7))
        integer = definition("fixed4", 4, frozen_at=7)
        fraction = definition("fixed4", Fraction(4), frozen_at=7)
        equivalent = definition("fixed4", Fraction(4, 1), frozen_at=7)
        self.assertEqual(integer.id, expected)
        self.assertEqual(fraction.id, expected)
        self.assertEqual(equivalent.id, expected)
        self.assertEqual(integer.version, "fixed4")
        self.assertNotEqual(integer.id, integer.version)
        changed_threshold = independent_fixed_definition_id("fixed4", 5, 7)
        changed_frozen = independent_fixed_definition_id("fixed4", 4, 8)
        changed_label = independent_fixed_definition_id("other", 4, 7)
        self.assertEqual(definition("fixed4", 5, frozen_at=7).id, changed_threshold)
        self.assertEqual(definition("fixed4", 4, frozen_at=8).id, changed_frozen)
        self.assertEqual(definition("other", 4, frozen_at=7).id, changed_label)
        self.assertNotEqual(changed_threshold, expected)
        self.assertNotEqual(changed_frozen, expected)
        self.assertNotEqual(changed_label, expected)
        self.assertEqual(definition("fixed4", Fraction(8, 2), frozen_at=7).id, expected)
        rows = [spec(1, 0, price=100), spec(2, 1, price=104)]
        live = independent_fixed_definition_id("fixed4", 4)
        got = stream(definition("fixed4", 4)).add_prepared(prepared_from(rows))
        self.assertEqual(got[0].definition_id, live)
        self.assertEqual(got[0].definition_version, "fixed4")
        self.assertNotEqual(got[0].definition_id, got[0].definition_version)

    def test_emit_cap_stops_before_materializing_the_remaining_batch(self):
        early_rows = [spec(1, 0, price=100), spec(2, 1, price=90)]
        scales = tuple(definition(f"s{index}", 10) for index in range(8))
        engine = stream(*scales, max_emitted_rows=8)
        early = engine.add_prepared(prepared_from(early_rows))
        self.assertEqual(len(early), 8)
        payload = canonical_json(tuple(asdict(item) for item in early))
        count = 400
        later = [spec(3 + index, 2 + index, price=90 if index % 2 == 0 else 100)
                 for index in range(count)]
        with self.assertRaises(ContractError):
            engine.add_prepared(prepared_from(later))
        work = engine.work()
        self.assertTrue(work["failed"])
        self.assertEqual(work["rows_attempted"], 4)
        self.assertLess(work["rows_attempted"], 2 + count)
        self.assertEqual(work["emissions_attempted"], 9)
        self.assertEqual(work["slices_attempted"], 2)
        self.assertEqual(canonical_json(tuple(asdict(item) for item in early)), payload)
        with self.assertRaises(IntegrityError):
            engine.record()
        with self.assertRaises(IntegrityError):
            engine.snapshot()
        with self.assertRaises(IntegrityError):
            engine.add_prepared(prepared_from([spec(1000, 1000, price=80)]))
        self.assertEqual(engine.work()["rows_attempted"], 4)
        thirty_two = tuple(definition(f"w{index}", 10) for index in range(32))
        fresh = stream(*thirty_two, max_emitted_rows=1)
        long_batch = [spec(1 + index, index, price=100 if index % 2 == 0 else 90)
                      for index in range(count)]
        with self.assertRaises(ContractError):
            fresh.add_prepared(prepared_from(long_batch))
        halted = fresh.work()
        self.assertTrue(halted["failed"])
        self.assertEqual(halted["rows_attempted"], 2)
        self.assertEqual(halted["emissions_attempted"], 2)
        self.assertLess(halted["definition_visits_attempted"], count)
        self.assertLess(halted["rows_attempted"], count)

    def test_negative_domains_reject_signed_flags_forged_side_price_and_clocks(self):
        engine = stream(definition("fixed10", 10))
        with self.assertRaises(IntegrityError):
            engine.add_prepared(prepared_from([spec(1, 0, raw_flags=-256)]))
        self.assertTrue(engine.work()["failed"])
        self.assertGreaterEqual(engine.work()["slices_attempted"], 1)
        self.assertEqual(engine.work()["rows_attempted"], 0)
        with self.assertRaises(IntegrityError):
            engine.record()
        with self.assertRaises(IntegrityError):
            engine.snapshot()
        forged_side = tamper_values(prepared_from([spec(1, 0, price=100)]), side=[2])
        with self.assertRaises(IntegrityError):
            stream(definition("fixed10", 10)).add_prepared(forged_side)
        forged_side = tamper_values(prepared_from([spec(1, 0, price=100)]), side=[-2])
        with self.assertRaises(IntegrityError):
            stream(definition("fixed10", 10)).add_prepared(forged_side)
        over_flags = tamper_values(prepared_from([spec(1, 0, price=100)]), raw_flags=[256])
        with self.assertRaises(IntegrityError):
            stream(definition("fixed10", 10)).add_prepared(over_flags)
        snapshot = tamper_values(prepared_from([spec(1, 0, price=100)]), raw_flags=[32])
        with self.assertRaises(IntegrityError):
            stream(definition("fixed10", 10)).add_prepared(snapshot)
        negative_row = tamper_values(prepared_from([spec(1, 0, price=100)]), source_row=[-1])
        with self.assertRaises(IntegrityError):
            stream(definition("fixed10", 10)).add_prepared(negative_row)
        forged_price = tamper_values(prepared_from([spec(1, 0, price=100)]), price=[0])
        with self.assertRaises(ContractError):
            stream(definition("fixed10", 10)).add_prepared(forged_price)
        negative_price = tamper_values(prepared_from([spec(1, 0, price=100)]), price=[-1])
        with self.assertRaises(ContractError):
            stream(definition("fixed10", 10)).add_prepared(negative_price)
        with self.assertRaises(IntegrityError):
            stream(definition("fixed10", 10)).add_prepared(
                prepared_from([spec(1, 0, price=100), spec(2, 0, price=90)]))
        with self.assertRaises(IntegrityError):
            stream(definition("fixed10", 10)).add_prepared(
                prepared_from([spec(1, 1, price=100), spec(2, 0, price=90)]))
        with self.assertRaises(IntegrityError):
            stream(definition("fixed10", 10)).add_prepared(
                prepared_from([spec(1, 0, price=100, source_row=5),
                               spec(2, 1, price=90, source_row=5)]))
        with self.assertRaises(IntegrityError):
            stream(definition("fixed10", 10)).add_prepared(
                prepared_from([spec(1, 0, price=100, source_row=9),
                               spec(2, 1, price=90, source_row=8)]))
        with self.assertRaises(IntegrityError):
            stream(definition("fixed10", 10)).add_prepared(
                prepared_from([spec(5, 0, price=100), spec(4, 1, price=90)]))
        with self.assertRaises(IntegrityError):
            stream(definition("fixed10", 10)).add_prepared(
                prepared_from([spec(1, 0, known_at_ns=1 + DELAY + 1)]))
        with self.assertRaises(IntegrityError):
            stream(definition("fixed10", 10)).add_prepared(
                prepared_from([spec(1, 0, known_at_ns=1 + DELAY - 1)]))
        later = stream(definition("fixed10", 10))
        later.add_prepared(prepared_from([spec(10, 0, price=100), spec(11, 1, price=90)]))
        with self.assertRaises(IntegrityError):
            later.add_prepared(prepared_from([spec(9, 2, price=80)]))
        with self.assertRaises(IntegrityError):
            stream(definition("fixed10", 10), source_key="other").add_prepared(
                prepared_from([spec(1, 0, price=100)]))


class AppendOnlyAndPoison(unittest.TestCase):
    def test_future_suffix_leaves_earlier_results_byte_equal(self):
        rows = [spec(1, 0, price=100), spec(2, 1, price=90), spec(3, 2, price=100),
                spec(4, 3, price=110), spec(5, 4, price=100)]
        prepared = prepared_from(rows)
        engine = stream(definition("fixed10", 10))
        early = engine.add_prepared(prepared, 0, 3)
        payload = canonical_json(tuple(asdict(item) for item in early))
        later = engine.add_prepared(prepared, 3, 5)
        self.assertEqual(canonical_json(tuple(asdict(item) for item in early)), payload)
        self.assertGreater(len(later), 0)
        self.assertEqual(early[0].side, "high")
        with self.assertRaises(FrozenInstanceError):
            early[0].side = "low"
        mutated = engine.record()
        mutated["rows"] = -1
        mutated["reason_counts"]["flag4"] = 99
        mutated["definitions"][0]["visits"] = -1
        snap = engine.snapshot()
        snap["provisional"][0]["direction"] = 9
        snap["provisional"][0]["high"]["ticks"] = -1
        self.assertNotEqual(engine.record()["rows"], -1)
        self.assertNotEqual(engine.record()["reason_counts"]["flag4"], 99)
        self.assertNotEqual(engine.record()["definitions"][0]["visits"], -1)
        self.assertNotEqual(engine.snapshot()["provisional"][0]["direction"], 9)
        self.assertNotEqual(engine.snapshot()["provisional"][0]["high"]["ticks"], -1)

    def test_after_error_every_subsequent_use_is_rejected(self):
        rows = [spec(1, 0, price=100), spec(2, 1, price=90)]
        engine = stream(definition("fixed10", 10))
        engine.add_prepared(prepared_from(rows))
        with self.assertRaises(IntegrityError):
            engine.add_prepared(prepared_from([spec(3, 1, price=100)]))
        work = engine.work()
        self.assertTrue(work["failed"])
        self.assertGreaterEqual(work["slices_attempted"], 2)
        self.assertEqual(work["rows_attempted"], 2)
        with self.assertRaises(IntegrityError):
            engine.add_prepared(prepared_from([spec(4, 3, price=80)]))
        with self.assertRaises(IntegrityError):
            engine.record()
        with self.assertRaises(IntegrityError):
            engine.snapshot()
        self.assertEqual(engine.work()["rows_attempted"], work["rows_attempted"])


class PivotReferenceParity(unittest.TestCase):
    def compare(self, bars, *, left=1, right=1, ties="strict"):
        engine = pivot_stream(left=left, right=right, ties=ties)
        got = add_all(engine, bars)
        expected = pivot_reference(bars, left=left, right=right, ties=ties,
                                   cut=max(item.published_at for item in bars))
        self.assertEqual(tuple(item.reference_swing() for item in got), expected)
        for item, want in zip(got, expected):
            self.assertTrue(item.unpublished_arithmetic)
            self.assertFalse(item.f09_producer_authenticated)
            self.assertEqual(item.max_published_at, want.confirmed_at)
            self.assertEqual(item.center_start, want.extreme_start)
            self.assertEqual(item.center_end, want.extreme_end)
            self.assertEqual(item.support_version_ids, want.source_versions)
            self.assertEqual(item.id, want.id)
            self.assertEqual(item.definition_version, want.definition_version)
            self.assertEqual(item.definition_id, independent_pivot_stream_id("pivot", left, right, ties))
            self.assertEqual(item.version, "pivot")
            self.assertEqual(item.definition_version, independent_pivot_reference_id(left, right, ties))
        return got, expected, engine

    def test_all_tie_rules_and_multiple_left_right_match_original_records(self):
        plateau = (bar(0, 100, 90), bar(1, 105, 91), bar(2, 105, 92), bar(3, 100, 93))
        for ties in ("strict", "earliest", "latest", "ambiguous"):
            self.compare(plateau, ties=ties)
        ordinary = (bar(0, 101, 99), bar(1, 105, 100), bar(2, 103, 100, published=35))
        self.compare(ordinary)
        longer = (bar(0, 100, 90), bar(1, 110, 80), bar(2, 108, 82), bar(3, 104, 84),
                  bar(4, 102, 86))
        for left, right in ((1, 1), (2, 1), (1, 2), (2, 2)):
            self.compare(longer, left=left, right=right)

    def test_gaps_incomplete_quiet_missing_and_delayed_publication(self):
        gapped = (bar(0, 100, 90), bar(1, 110, 95), bar(3, 105, 92))
        got, expected, engine = self.compare(gapped)
        self.assertEqual(got, ())
        self.assertEqual(expected, ())
        self.assertEqual(engine.record()["invalid_support_windows"], 1)
        incomplete = (bar(0, 100, 90), bar(1, 110, 95, complete=False), bar(2, 105, 92))
        self.compare(incomplete)
        quiet = (bar(0, 100, 90), bar(1, 110, 95, empty=True), bar(2, 105, 92))
        got, expected, engine = self.compare(quiet)
        self.assertEqual(got, ())
        self.assertEqual(engine.record()["invalid_support_windows"], 1)
        delayed = (bar(0, 101, 99), bar(1, 105, 100), bar(2, 103, 100, published=35))
        got, expected, _ = self.compare(delayed)
        high = [item for item in got if item.side == "high"][0]
        self.assertEqual(high.confirmed_at, 35)
        self.assertEqual(high.extreme_start, 10)
        self.assertEqual(high.extreme_end, 20)
        self.assertEqual(high.max_published_at, 35)
        self.assertNotEqual(high.confirmed_at, high.extreme_end)

    def test_both_high_and_low_center_and_no_early_publication(self):
        bars = (bar(0, 100, 90), bar(1, 110, 80), bar(2, 105, 85))
        engine = pivot_stream()
        self.assertEqual(engine.add(bars[0]), ())
        self.assertEqual(engine.add(bars[1]), ())
        self.assertEqual(engine.snapshot()["deque_length"], 2)
        self.assertEqual(engine.record()["emitted_rows"], 0)
        got = engine.add(bars[2])
        expected = pivot_reference(bars, left=1, right=1, cut=30)
        self.assertEqual(tuple(item.reference_swing() for item in got), expected)
        self.assertEqual(tuple(item.side for item in got), ("high", "low"))
        self.assertEqual(got[0].price_ticks, 110)
        self.assertEqual(got[1].price_ticks, 80)
        self.assertEqual(engine.record()["valid_support_windows"], 1)
        self.assertEqual(engine.snapshot()["deque_length"], 3)
        self.assertEqual(engine.snapshot()["deque_capacity"], 3)

    def test_revisions_and_nonfinal_inputs_are_rejected_without_rewriting(self):
        bars = (bar(0, 101, 99), bar(1, 105, 100), bar(2, 103, 100, published=35))
        engine = pivot_stream()
        early = add_all(engine, bars)
        payload = canonical_json(tuple(asdict(item) for item in early))
        with self.assertRaises(ContractError) as raised:
            engine.add(bar(1, 102, 100, published=45))
        self.assertIn("as-of", str(raised.exception))
        self.assertEqual(canonical_json(tuple(asdict(item) for item in early)), payload)
        with self.assertRaises(IntegrityError):
            engine.add(bar(3, 120, 119))
        fresh = pivot_stream()
        with self.assertRaises(ContractError):
            fresh.add(bar(0, 101, 99, final=False))
        with self.assertRaises(IntegrityError):
            fresh.add(bar(1, 105, 100))
        none = pivot_stream()
        unpublished = CausalBar("NQH5", 0, 10, "bar10", 0, 10, 10, True, 99, 101, 99, 101,
                                2, 2, 0, True, True, 10, ("a0", "b0"), "coverage", (), None)
        with self.assertRaises(ContractError):
            none.add(unpublished)


class PivotBoundaries(unittest.TestCase):
    def test_gaps_do_not_invent_bars_and_deque_stays_bounded(self):
        engine = pivot_stream()
        sequence = (bar(0, 100, 90), bar(1, 110, 95), bar(3, 105, 92), bar(4, 104, 91),
                    bar(5, 103, 90), bar(6, 102, 89))
        got = add_all(engine, sequence)
        expected = pivot_reference(sequence, left=1, right=1,
                                   cut=max(item.published_at for item in sequence))
        self.assertEqual(tuple(item.reference_swing() for item in got), expected)
        snap = engine.snapshot()
        self.assertEqual(snap["deque_length"], 3)
        self.assertEqual(snap["deque_capacity"], 3)
        self.assertEqual(snap["bar_visits"], 6)
        self.assertLessEqual(snap["deque_length"], snap["deque_capacity"])

    def test_resource_one_over_instrument_overlap_and_frozen_rule(self):
        bars = (bar(0, 100, 90), bar(1, 110, 80), bar(2, 105, 85))
        limited = pivot_stream(max_bars=2)
        self.assertEqual(limited.add(bars[0]), ())
        self.assertEqual(limited.add(bars[1]), ())
        with self.assertRaises(ContractError):
            limited.add(bars[2])
        emit_cap = pivot_stream(max_emitted_rows=1)
        emit_cap.add(bars[0])
        emit_cap.add(bars[1])
        with self.assertRaises(ContractError):
            emit_cap.add(bars[2])
        exact = pivot_stream(max_emitted_rows=2)
        self.assertEqual(len(add_all(exact, bars)), 2)
        with self.assertRaises(ContractError):
            pivot_stream(frozen_at=15).add(bars[0])
        moved = pivot_stream()
        moved.add(bars[0])
        with self.assertRaises(ContractError):
            moved.add(bar(1, 110, 80, instrument="NQM5"))
        overlap = pivot_stream()
        overlap.add(bars[0])
        with self.assertRaises(ContractError):
            overlap.add(CausalBar("NQH5", 5, 15, "bar10", 0, 15, 15, True, 90, 110, 90, 110,
                                  2, 2, 0, True, True, 10, ("x", "y"), "coverage", (), 15))
        backward = pivot_stream()
        backward.add(bar(2, 105, 85))
        with self.assertRaises(ContractError):
            backward.add(bar(1, 110, 80))
        with self.assertRaises(ContractError):
            FinalBarPivotDefinition("p", 0, 1, "strict", 0)
        with self.assertRaises(ContractError):
            FinalBarPivotDefinition("p", 1, 1, "other", 0)
        with self.assertRaises(ContractError):
            FinalBarPivotStream(instrument="NQH5", interval_ns=10,
                                definition=FinalBarPivotDefinition("p", 1, 1, "strict", 0),
                                max_bars=100_001)
        with self.assertRaises(ContractError):
            pivot_stream().add(object())
        with self.assertRaises(ContractError):
            FinalBarPivotDefinition("p", True, 1, "strict", 0)

    def test_pivot_stream_ids_bind_science_and_keep_original_reference_identity(self):
        left, right, ties, frozen_at, version = 2, 1, "earliest", 3, "pivotA"
        expected_id = independent_pivot_stream_id(version, left, right, ties, frozen_at)
        reference_id = independent_pivot_reference_id(left, right, ties)
        frozen = FinalBarPivotDefinition(version, left, right, ties, frozen_at)
        self.assertEqual(frozen.id, expected_id)
        self.assertEqual(frozen.version, version)
        self.assertNotEqual(frozen.id, version)
        self.assertEqual(frozen.reference_definition_id, reference_id)
        self.assertNotEqual(frozen.id, frozen.reference_definition_id)
        self.assertEqual(
            FinalBarPivotDefinition(version, 1, right, ties, frozen_at).id,
            independent_pivot_stream_id(version, 1, right, ties, frozen_at))
        self.assertNotEqual(FinalBarPivotDefinition(version, 1, right, ties, frozen_at).id, expected_id)
        self.assertNotEqual(FinalBarPivotDefinition(version, left, 2, ties, frozen_at).id, expected_id)
        self.assertNotEqual(FinalBarPivotDefinition(version, left, right, "strict", frozen_at).id, expected_id)
        self.assertNotEqual(FinalBarPivotDefinition(version, left, right, ties, 4).id, expected_id)
        live_id = independent_pivot_stream_id(version, left, right, ties, 0)
        longer = (bar(0, 100, 90), bar(1, 110, 80), bar(2, 108, 82), bar(3, 104, 84))
        engine = pivot_stream(left=left, right=right, ties=ties, frozen_at=0, version=version)
        got = add_all(engine, longer)
        expected = pivot_reference(longer, left=left, right=right, ties=ties,
                                   cut=max(item.published_at for item in longer))
        self.assertEqual(tuple(item.reference_swing() for item in got), expected)
        for item in got:
            self.assertEqual(item.definition_id, live_id)
            self.assertEqual(item.version, version)
            self.assertEqual(item.definition_version, reference_id)
        record = engine.record()
        self.assertEqual(record["definition_id"], live_id)
        self.assertEqual(record["definition_version"], version)
        self.assertEqual(record["reference_definition_id"], reference_id)
