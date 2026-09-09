"""Independent checks of unpublished full-source historical-aggression arithmetic.

Expected clusters and fields come from measurements.memory.build_memory on actual
small captures and from the independent literal all-pairs/triangular reference.
This module does not execute registered actual-data validation or claim F05, F10
or F11 admission.
"""
from dataclasses import replace
from fractions import Fraction
from types import SimpleNamespace
import unittest

import numpy as np
import pyarrow as pa

from references import structure_pressure_memory_literal as literal
from trading_research.errors import ContractError, DependencyUnavailable, IntegrityError
from trading_research.measurements.common import capture_trade_window
from trading_research.measurements.memory import MemoryDefinition, build_memory
from trading_research.operations.artifacts import canonical_json
from trading_research.research.auction_flow_memory import (
    VERSION, AuctionFlowMemoryDefinition, AuctionFlowMemoryWindow, _IDENTITY_KEYS,
)
from trading_research.research.auction_flow_windows import prepare_trade_batch
from tests.measurement_fixtures import ledger, request, row


DELAY = 5
START = 0
END = 100
INSTRUMENT_ID = 1
SOURCE = "src"


def spec(identity, t, *, price=100, size=1, side=1, source_order=None, source_row=None,
         source_key=SOURCE, raw_flags=0, instrument_id=INSTRUMENT_ID, known_at_ns=None,
         price_valid=None):
    if price is None:
        price, price_valid = 0, 0
    elif price_valid is None:
        price_valid = 1
    raw_side = "B" if side == 1 else "A" if side == -1 else "N"
    if source_order is None:
        source_order = t
    if source_row is None:
        source_row = source_order
    return {
        "id": identity, "t": t, "source_order": source_order, "instrument_id": instrument_id,
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


def definition(**changes):
    values = dict(version="memory", time_radius_ns=10, price_radius_ticks=0,
                  decay_kernel="box", decay_scale=1000)
    values.update(changes)
    return AuctionFlowMemoryDefinition(**values)


def window(defn=None, *, start=START, end=END, delay_ns=DELAY, instrument_id=INSTRUMENT_ID,
           source_key=SOURCE, **capacities):
    return AuctionFlowMemoryWindow(
        definition=defn or definition(), instrument_id=instrument_id, source_key=source_key,
        start_ns=start, end_ns=end, latency_ns=delay_ns, **capacities)


def finish(rows, defn=None, *, history=None, slices=None, **kwargs):
    engine = window(defn, **kwargs)
    prepared = prepared_from(rows)
    if slices is None:
        engine.add_prepared(prepared, history_complete=True if history is None else history)
    else:
        for left, right, complete in slices:
            engine.add_prepared(prepared, left, right,
                                history_complete=True if complete is None else complete)
    return engine.finish(), engine


def ids(rows):
    return {row["source_row"]: row["id"] for row in rows}


def side_canon(value):
    return None if value in (0, None) else value


def cluster_quant(cluster):
    return (side_canon(cluster["side"] if isinstance(cluster, dict) else cluster.side),
            cluster["center_ticks"] if isinstance(cluster, dict) else cluster.center_ticks,
            cluster["low_ticks"] if isinstance(cluster, dict) else cluster.low_ticks,
            cluster["high_ticks"] if isinstance(cluster, dict) else cluster.high_ticks,
            cluster["first_at"] if isinstance(cluster, dict) else cluster.first_at,
            cluster["last_at"] if isinstance(cluster, dict) else cluster.last_at,
            cluster["gross"] if isinstance(cluster, dict) else cluster.gross,
            cluster["raw_count"] if isinstance(cluster, dict) else cluster.raw_count)


def member_ids(cluster, by_row):
    return tuple(sorted(by_row[member["source_row"]] for member in cluster["members"]))


def measurement_rows(rows):
    return [row(item["id"], at=item["t"],
                price=None if item["price_valid"] == 0 else item["price"],
                size=item["size"], side=side_canon(item["side"]), order=item["source_order"])
            for item in rows]


def original_memory(rows, defn, *, start=START, end=None, cut=None):
    end = (max(item["t"] for item in rows) + 1) if end is None else end
    cut = end if cut is None else cut
    view = ledger(measurement_rows(rows))
    capture = capture_trade_window(view, **request(start=start, end=end, cut=cut, published=cut))
    original = MemoryDefinition(
        defn.version, minimum_size=defn.minimum_size, strict_size=defn.strict_size,
        price_radius_ticks=defn.price_radius_ticks, time_radius_ns=defn.time_radius_ns,
        max_age_ns=defn.max_age_ns, spatial_grid=defn.spatial_grid,
        spatial_kernel=defn.spatial_kernel, spatial_radius_ticks=defn.spatial_radius_ticks,
        decay_clock=defn.decay_clock, decay_scale=defn.decay_scale,
        decay_kernel=defn.decay_kernel, frozen_at=defn.frozen_at)
    return build_memory((capture,), views=(view,), definition=original, cut=cut, published_at=cut)


def literal_selected(rows, defn, *, end):
    chosen = []
    for item in rows:
        if item["price_valid"] != 1:
            continue
        if end - item["t"] > defn.max_age_ns:
            continue
        if defn.strict_size:
            if item["size"] <= defn.minimum_size:
                continue
        elif item["size"] < defn.minimum_size:
            continue
        chosen.append((item["id"], item["t"], item["price"], item["size"], side_canon(item["side"])))
    return literal.clusters(chosen, defn.price_radius_ticks, defn.time_radius_ns)


def work_map(report):
    return dict(report["work"])


class ConnectedComponentCases(unittest.TestCase):
    def test_literal_bridge_connects_endpoints_outside_direct_radius(self):
        rows = [spec("a", 0, price=100, size=10, source_order=0),
                spec("b", 0, price=104, size=10, source_order=1, source_row=1),
                spec("c", 1, price=102, size=10, source_order=2, source_row=2)]
        defn = definition(version="bridge", price_radius_ticks=2, time_radius_ns=2)
        report, _ = finish(rows, defn, end=2)
        self.assertTrue(report["unpublished_arithmetic"])
        self.assertFalse(report["f05_admitted"] or report["f10_admitted"] or report["f11_admitted"])
        self.assertEqual(report["publication_status"], "unpublished")
        self.assertEqual(len(report["clusters"]), 1)
        cluster = report["clusters"][0]
        self.assertEqual(member_ids(cluster, ids(rows)), ("a", "b", "c"))
        self.assertEqual(cluster["side"], 1)
        self.assertEqual(cluster["gross"], 30)
        self.assertEqual(cluster["raw_count"], 3)
        self.assertEqual(cluster["center_ticks"], 102)
        self.assertEqual((cluster["low_ticks"], cluster["high_ticks"]), (100, 104))
        self.assertEqual((cluster["first_at"], cluster["last_at"]), (0, 1))
        self.assertEqual(literal_selected(rows, defn, end=2),
                         ((("a", "b", "c"), 30, Fraction(102, 1)),))

    def test_separated_time_and_price_neighbors_stay_distinct(self):
        rows = [spec("a", 0, price=100, source_order=0),
                spec("b", 1, price=103, source_order=1, source_row=1),
                spec("c", 10, price=100, source_order=2, source_row=2)]
        defn = definition(version="apart", price_radius_ticks=2, time_radius_ns=2)
        report, _ = finish(rows, defn, end=11)
        names = tuple(member_ids(cluster, ids(rows)) for cluster in report["clusters"])
        self.assertEqual(set(names), {("a",), ("b",), ("c",)})
        self.assertEqual(literal_selected(rows, defn, end=11),
                         tuple(sorted(((("a",), 1, Fraction(100, 1)),
                                       (("b",), 1, Fraction(103, 1)),
                                       (("c",), 1, Fraction(100, 1))))))

    def test_equality_at_time_price_age_and_size_boundaries(self):
        rows = [spec("age_drop", 9, price=301, size=10, source_order=0, source_row=0),
                spec("age_keep", 10, price=300, size=10, source_order=1, source_row=1),
                spec("t0", 20, price=200, size=10, source_order=2, source_row=2),
                spec("p0", 25, price=100, size=10, source_order=3, source_row=3),
                spec("t1", 25, price=200, size=10, source_order=4, source_row=4),
                spec("p1", 26, price=102, size=10, source_order=5, source_row=5),
                spec("size_keep", 28, price=400, size=10, source_order=6, source_row=6),
                spec("size_drop", 29, price=400, size=9, source_order=7, source_row=7)]
        inclusive = definition(version="bounds", price_radius_ticks=2, time_radius_ns=5,
                               max_age_ns=20, minimum_size=10, strict_size=False)
        report, _ = finish(rows, inclusive, end=30)
        names = {member_ids(cluster, ids(rows)) for cluster in report["clusters"]}
        self.assertIn(("p0", "p1"), names)
        self.assertIn(("t0", "t1"), names)
        self.assertIn(("age_keep",), names)
        self.assertNotIn(("age_drop",), names)
        self.assertIn(("size_keep",), names)
        self.assertNotIn(("size_drop",), names)
        self.assertEqual(report["older_than_max_age_prints"], 1)
        self.assertEqual(report["below_filter_prints"], 1)
        strict = definition(version="strict", minimum_size=10, strict_size=True, max_age_ns=100)
        strict_rows = [spec("eq", 0, price=100, size=10, source_order=0),
                       spec("over", 1, price=100, size=11, source_order=1, source_row=1)]
        strict_report, _ = finish(strict_rows, strict, end=2)
        self.assertEqual(tuple(member_ids(cluster, ids(strict_rows))
                               for cluster in strict_report["clusters"]), (("over",),))

    def test_opposite_and_unknown_signs_at_one_price_do_not_merge(self):
        rows = [spec("buy", 0, price=100, size=10, side=1, source_order=0),
                spec("sell", 1, price=100, size=8, side=-1, source_order=1, source_row=1),
                spec("unk", 2, price=100, size=2, side=0, source_order=2, source_row=2)]
        report, _ = finish(rows, definition(version="sides"), end=3)
        self.assertEqual(len(report["clusters"]), 3)
        self.assertEqual(report["raw_mass"], (10, 8, 2))
        sides = tuple(sorted(cluster["side"] for cluster in report["clusters"]))
        self.assertEqual(sides, (-1, 0, 1))
        for cluster in report["clusters"]:
            self.assertEqual(len(cluster["members"]), 1)

    def test_repeated_equal_economic_prints_keep_distinct_physical_rows(self):
        rows = [spec("a", 4, price=100, size=7, source_order=10, source_row=10),
                spec("b", 4, price=100, size=7, source_order=11, source_row=11)]
        report, _ = finish(rows, definition(version="dup"), end=5)
        self.assertEqual(len(report["clusters"]), 1)
        cluster = report["clusters"][0]
        self.assertEqual(cluster["raw_count"], 2)
        self.assertEqual(cluster["gross"], 14)
        self.assertEqual(member_ids(cluster, ids(rows)), ("a", "b"))
        self.assertEqual([member["source_row"] for member in cluster["members"]], [10, 11])
        self.assertEqual({member["raw_action"] for member in cluster["members"]}, {"T"})

    def test_expiry_in_a_separately_formed_result_splits_a_prior_bridge(self):
        rows = [spec("bridge", 0, price=101, size=5, source_order=0),
                spec("left", 10, price=100, size=5, source_order=1, source_row=1),
                spec("right", 10, price=102, size=5, source_order=2, source_row=2)]
        connected = definition(version="expire", price_radius_ticks=1, time_radius_ns=20,
                               max_age_ns=100)
        split = definition(version="expire", price_radius_ticks=1, time_radius_ns=20,
                           max_age_ns=20)
        whole, _ = finish(rows, connected, end=25)
        expired, _ = finish(rows, split, end=25)
        self.assertEqual(len(whole["clusters"]), 1)
        self.assertEqual(member_ids(whole["clusters"][0], ids(rows)), ("bridge", "left", "right"))
        self.assertEqual(len(expired["clusters"]), 2)
        names = {member_ids(cluster, ids(rows)) for cluster in expired["clusters"]}
        self.assertEqual(names, {("left",), ("right",)})
        self.assertNotEqual(whole["id"], expired["id"])
        self.assertEqual(whole["definition_id"], connected.id)
        self.assertNotEqual(connected.id, split.id)
        self.assertNotIn("predecessors", whole["clusters"][0])

    def test_cluster_id_binds_selected_member_content_not_only_address(self):
        address = dict(source_order=9, source_row=9)
        base = spec("same", 4, price=100, size=7, **address)
        priced = spec("same", 4, price=101, size=7, **address)
        sized = spec("same", 4, price=100, size=8, **address)
        defn = definition(version="content-id")
        first, _ = finish([base], defn, end=5)
        second, _ = finish([priced], defn, end=5)
        third, _ = finish([sized], defn, end=5)
        member = first["clusters"][0]["members"][0]
        for key in ("source_key", "source_row", "source_order", "event_at", "known_at_ns",
                    "price", "size", "raw_flags", "raw_action", "raw_side", "side"):
            self.assertIn(key, member)
        self.assertEqual((member["source_row"], member["source_order"], member["source_key"]),
                         (9, 9, SOURCE))
        self.assertEqual((member["event_at"], member["known_at_ns"], member["price"], member["size"]),
                         (4, 4 + DELAY, 100, 7))
        self.assertNotEqual(first["clusters"][0]["id"], second["clusters"][0]["id"])
        self.assertNotEqual(first["clusters"][0]["id"], third["clusters"][0]["id"])
        self.assertNotEqual(second["clusters"][0]["id"], third["clusters"][0]["id"])
        self.assertNotEqual(first["id"], second["id"])
        self.assertEqual(second["clusters"][0]["members"][0]["source_row"], 9)
        self.assertEqual(second["clusters"][0]["members"][0]["price"], 101)
        self.assertEqual(third["clusters"][0]["members"][0]["size"], 8)


class OriginalAndLiteralComparison(unittest.TestCase):
    def compare(self, rows, defn, *, start=0, end=None):
        end = (max(item["t"] for item in rows) + 1) if end is None else end
        report, _ = finish(rows, defn, start=start, end=end)
        original = original_memory(rows, defn, start=start, end=end, cut=end)
        expected = literal_selected(rows, defn, end=end)
        by_row = ids(rows)
        got = tuple(sorted((member_ids(cluster, by_row), cluster["gross"], cluster["center_ticks"])
                           for cluster in report["clusters"]))
        self.assertEqual(got, expected)
        self.assertEqual(tuple(sorted((cluster.member_ids, cluster.gross, cluster.center_ticks)
                                      for cluster in original.clusters)), expected)
        self.assertEqual(len(report["clusters"]), len(original.clusters))
        by_members = {memory.member_ids: memory for memory in original.clusters}
        for actual in report["clusters"]:
            memory = by_members[member_ids(actual, by_row)]
            self.assertEqual(cluster_quant(actual), cluster_quant(memory))
            self.assertEqual(member_ids(actual, by_row), memory.member_ids)
            self.assertEqual(side_canon(actual["side"]), memory.side)
            self.assertEqual(len(actual["members"]), memory.raw_count)
        self.assertEqual(report["raw_mass"], original.raw_mass)
        return report, original

    def test_mm01_three_sides_and_mm02_bridge_match_original_and_literal(self):
        sides = [spec("a", 0, price=100, size=10, side=1, source_order=0),
                 spec("b", 1, price=100, size=8, side=-1, source_order=1, source_row=1),
                 spec("c", 2, price=100, size=2, side=0, source_order=2, source_row=2)]
        self.compare(sides, definition(version="memory", time_radius_ns=10, price_radius_ticks=0,
                                       decay_kernel="box", decay_scale=1000), end=3)
        chain = [spec("a", 0, price=100, size=10, source_order=0),
                 spec("b", 0, price=104, size=10, source_order=1, source_row=1),
                 spec("c", 1, price=102, size=10, source_order=2, source_row=2)]
        self.compare(chain, definition(version="bridge", price_radius_ticks=2, time_radius_ns=2,
                                       decay_scale=100), end=2)

    def test_contiguous_price_chain_and_unknown_none_semantics_match_both_references(self):
        rows = [spec("a", 0, price=100, size=3, source_order=0),
                spec("b", 1, price=101, size=6, source_order=1, source_row=1),
                spec("c", 2, price=102, size=9, source_order=2, source_row=2)]
        report, original = self.compare(
            rows, definition(version="union", price_radius_ticks=1, time_radius_ns=10,
                             decay_scale=100), end=3)
        self.assertEqual(report["clusters"][0]["center_ticks"], Fraction(304, 3))
        self.assertEqual(original.clusters[0].center_ticks, Fraction(304, 3))
        unknown = [spec("u", 0, price=50, size=4, side=0, source_order=0)]
        report, original = self.compare(
            unknown, definition(version="unknown", decay_kernel="box", decay_scale=1000), end=1)
        self.assertEqual(report["clusters"][0]["side"], 0)
        self.assertIsNone(original.clusters[0].side)


class SpatialFieldCases(unittest.TestCase):
    def test_point_and_triangular_raw_box_fields_and_out_of_grid_overflow(self):
        rows = [spec("a", 0, price=100, size=10, source_order=0)]
        point = definition(version="point", spatial_grid=(99, 100, 101), spatial_kernel="point",
                           decay_kernel="box", decay_scale=100)
        report, _ = finish(rows, point, end=1)
        original = original_memory(rows, point, end=1, cut=1)
        self.assertEqual(report["field_cells"], original.field_cells)
        self.assertEqual(report["overflow"], original.overflow)
        self.assertEqual(report["raw_mass"], (10, 0, 0))
        self.assertEqual(sum(cell[1][0] for cell in report["field_cells"]) + report["overflow"][0][0],
                         report["raw_mass"][0])
        triangular = definition(version="triangular", spatial_grid=(99, 100, 101),
                                spatial_kernel="triangular", spatial_radius_ticks=1,
                                decay_kernel="box", decay_scale=100)
        report, _ = finish(rows, triangular, end=1)
        original = original_memory(rows, triangular, end=1, cut=1)
        self.assertEqual(tuple(cell[1][0] for cell in report["field_cells"]),
                         literal.triangular(100, 10, [99, 100, 101]))
        self.assertEqual(report["field_cells"], original.field_cells)
        self.assertEqual(report["overflow"][0], (Fraction(0), Fraction(0), Fraction(0)))
        low = [spec("low", 0, price=98, size=8, source_order=0)]
        high = [spec("high", 0, price=102, size=8, source_order=0)]
        low_report, _ = finish(low, triangular, end=1)
        high_report, _ = finish(high, triangular, end=1)
        self.assertGreater(low_report["overflow"][0][0], 0)
        self.assertGreater(high_report["overflow"][0][0], 0)
        self.assertEqual(low_report["overflow"][0][0] + sum(cell[1][0] for cell in low_report["field_cells"]),
                         8)
        self.assertEqual(high_report["overflow"][0][0] + sum(cell[1][0] for cell in high_report["field_cells"]),
                         8)

    def test_empty_grid_sends_all_support_to_overflow_and_exclusions_do_not_enter_mass(self):
        empty = definition(version="empty-grid", spatial_grid=(), spatial_kernel="triangular",
                           spatial_radius_ticks=1, decay_kernel="box", decay_scale=100)
        rows = [spec("a", 0, price=100, size=10, source_order=0),
                spec("unpriced", 1, price=None, size=4, source_order=1, source_row=1),
                spec("small", 2, price=100, size=3, source_order=2, source_row=2)]
        report, _ = finish(rows, replace(empty, minimum_size=5), end=3)
        self.assertEqual(report["field_cells"], ())
        self.assertEqual(report["raw_mass"], (10, 0, 0))
        self.assertEqual(report["overflow"][0][0], 10)
        self.assertEqual(report["unpriced_prints"], 1)
        self.assertEqual(report["unpriced_volume"], 4)
        self.assertEqual(report["below_filter_prints"], 2)
        self.assertEqual(report["below_filter_volume"], 7)
        self.assertEqual(report["excluded_prints"], 2)
        self.assertEqual(report["excluded_volume"], 7)
        self.assertEqual(report["selected_prints"], 1)
        self.assertEqual(report["selected_volume"], 10)

    def test_large_exact_integer_and_fraction_products(self):
        size = 2 ** 31 - 1
        price = 2 ** 50
        rows = [spec("a", 0, price=price, size=size, source_order=0),
                spec("b", 1, price=price + 1, size=size, source_order=1, source_row=1)]
        defn = definition(version="big", price_radius_ticks=1, time_radius_ns=10,
                          spatial_grid=(price, price + 1), spatial_kernel="triangular",
                          spatial_radius_ticks=1, decay_kernel="box", decay_scale=1000)
        report, _ = finish(rows, defn, end=2)
        center = Fraction(size * price + size * (price + 1), size + size)
        self.assertEqual(report["clusters"][0]["center_ticks"], center)
        self.assertEqual(report["clusters"][0]["gross"], size + size)
        self.assertEqual(sum((cell[1][0] for cell in report["field_cells"]), Fraction(0))
                         + report["overflow"][0][0], report["raw_mass"][0])
        self.assertEqual(type(report["clusters"][0]["center_ticks"]), Fraction)


class DecayClockCases(unittest.TestCase):
    def test_time_and_volume_half_life_match_original_within_1e12(self):
        rows = [spec("a", 0, price=100, size=16, source_order=0),
                spec("later", 1, price=100, size=8, source_order=1, source_row=1)]
        for clock, scale, expected in (("time", 2, 8), ("volume", 4, 4)):
            defn = definition(version="decay:" + clock, minimum_size=10, decay_clock=clock,
                              decay_scale=scale, decay_kernel="half_life")
            report, _ = finish(rows, defn, end=2)
            original = original_memory(rows, defn, end=2, cut=2)
            self.assertAlmostEqual(report["decayed_mass"][0], expected, delta=1e-12)
            self.assertAlmostEqual(original.decayed_mass[0], expected, delta=1e-12)
            self.assertAlmostEqual(report["decayed_mass"][0], original.decayed_mass[0], delta=1e-12)
            self.assertEqual(report["raw_mass"][0], 16)
            self.assertEqual(report["decay_clock"], clock)

    def test_same_timestamp_group_spanning_chunks_and_later_unpriced_volume_age(self):
        rows = [spec("a", 10, price=100, size=3, source_order=0),
                spec("b", 10, price=100, size=5, source_order=1, source_row=1),
                spec("small", 20, price=100, size=2, source_order=2, source_row=2),
                spec("unpriced", 30, price=None, size=7, source_order=3, source_row=3)]
        defn = definition(version="volume-tie", minimum_size=3, decay_clock="volume",
                          decay_scale=9, decay_kernel="half_life")
        together, _ = finish(rows, defn, end=40)
        split, _ = finish(rows, defn, end=40, slices=((0, 1, True), (1, 4, True)))
        self.assertEqual(together["id"], split["id"])
        self.assertEqual(together["clusters"][0]["id"], split["clusters"][0]["id"])
        self.assertEqual(together["clusters"][0]["members"], split["clusters"][0]["members"])
        self.assertEqual(together["raw_mass"], split["raw_mass"])
        self.assertEqual(together["first_print"], split["first_print"])
        self.assertEqual(together["last_print"], split["last_print"])
        original = original_memory(rows, defn, end=40, cut=40)
        self.assertAlmostEqual(together["decayed_mass"][0], original.decayed_mass[0], delta=1e-12)
        age = 2 + 7
        expected = (3 + 5) * (2 ** (-float(Fraction(age, 9))))
        self.assertAlmostEqual(together["decayed_mass"][0], expected, delta=1e-12)
        self.assertEqual(together["unpriced_volume"], 7)
        self.assertEqual(together["below_filter_prints"], 1)
        self.assertEqual(together["below_filter_volume"], 2)
        self.assertGreater(split["slices"], 1)
        prepared = prepared_from(rows)
        pending = window(defn, end=40)
        pending.add_prepared(prepared, 0, 1)
        self.assertFalse(hasattr(pending, "_in_t"))
        self.assertFalse(hasattr(pending, "_in_size"))
        self.assertEqual(pending._pending_time, 10)
        self.assertEqual(pending._pending_selected, [0])
        self.assertEqual(pending._volume_total, 3)
        self.assertEqual(pending._sel_group_end, [None])
        pending.add_prepared(prepared, 1, 4)
        self.assertEqual(pending._pending_time, 30)
        self.assertEqual(pending._pending_selected, [])
        self.assertEqual(pending._volume_total, 3 + 5 + 2 + 7)
        self.assertEqual(pending._sel_group_end, [8, 8])
        pending_report = pending.finish()
        self.assertEqual(pending_report["id"], together["id"])
        self.assertAlmostEqual(pending_report["decayed_mass"][0], expected, delta=1e-12)

    def test_gap_history_and_bit4_mask_volume_decay_only(self):
        rows = [spec("a", 0, price=100, size=16, source_order=0),
                spec("later", 1, price=100, size=8, source_order=1, source_row=1)]
        volume = definition(version="gap-volume", minimum_size=10, decay_clock="volume",
                            decay_scale=4, decay_kernel="half_life")
        time = definition(version="gap-time", minimum_size=10, decay_clock="time",
                          decay_scale=2, decay_kernel="half_life")
        gapped, _ = finish(rows, volume, end=2, history=False)
        self.assertFalse(gapped["history_complete"])
        self.assertEqual(gapped["raw_mass"][0], 16)
        self.assertIsNone(gapped["decayed_mass"][0])
        timed, _ = finish(rows, time, end=2, history=False)
        self.assertFalse(timed["history_complete"])
        self.assertEqual(timed["raw_mass"][0], 16)
        self.assertAlmostEqual(timed["decayed_mass"][0], 8, delta=1e-12)
        flagged = [spec("a", 0, price=100, size=16, source_order=0, raw_flags=4),
                   spec("later", 1, price=100, size=8, source_order=1, source_row=1)]
        bit4, _ = finish(flagged, volume, end=2)
        self.assertFalse(bit4["history_complete"])
        self.assertEqual(bit4["flag4_prints"], 1)
        self.assertEqual(bit4["raw_mass"][0], 16)
        self.assertIsNone(bit4["decayed_mass"][0])
        empty_gap, _ = finish(rows, volume, end=2, slices=((0, 0, False), (0, 2, True)))
        self.assertFalse(empty_gap["history_complete"])
        self.assertIsNone(empty_gap["decayed_mass"][0])
        self.assertEqual(empty_gap["slices"], 2)

    def test_cut_scale_and_source_definitions_keep_distinct_identities(self):
        rows = [spec("a", 0, price=100, size=10, source_order=0)]
        a = definition(version="id-a", decay_scale=2, decay_kernel="half_life")
        b = definition(version="id-b", decay_scale=4, decay_kernel="half_life")
        first, _ = finish(rows, a, end=2)
        second, _ = finish(rows, b, end=2)
        third, _ = finish(rows, a, end=3)
        other_source = [replace_key(rows[0], "other")]
        fourth, _ = finish(other_source, a, end=2, source_key="other")
        self.assertNotEqual(a.id, b.id)
        self.assertNotEqual(first["definition_id"], second["definition_id"])
        self.assertNotEqual(first["clusters"][0]["id"], second["clusters"][0]["id"])
        self.assertNotEqual(first["id"], third["id"])
        self.assertNotEqual(first["clusters"][0]["id"], fourth["clusters"][0]["id"])
        self.assertEqual(first["definition_id"], a.id)
        self.assertNotIn("slices", _IDENTITY_KEYS)
        self.assertNotIn("work", _IDENTITY_KEYS)
        self.assertNotIn("id", _IDENTITY_KEYS)

    def test_volume_retention_scales_with_selected_membership_not_input_length(self):
        selected = [spec("keep", 0, price=100, size=10, source_order=0, source_row=0)]
        filler = [spec("x" + str(index), index + 1, price=100, size=1,
                       source_order=index + 1, source_row=index + 1)
                  for index in range(256)]
        later = [spec("unpriced", 300, price=None, size=9, source_order=300, source_row=300)]
        rows = selected + filler + later
        defn = definition(version="retain-volume", minimum_size=5, decay_clock="volume",
                          decay_scale=20, decay_kernel="half_life")
        prepared = prepared_from(rows)
        engine = window(defn, end=400)
        engine.add_prepared(prepared, 0, 128)
        engine.add_prepared(prepared, 128, len(rows))
        self.assertFalse(hasattr(engine, "_in_t"))
        self.assertFalse(hasattr(engine, "_in_size"))
        self.assertEqual(len(engine._sel_t), 1)
        self.assertEqual(len(engine._sel_size), 1)
        self.assertEqual(len(engine._sel_group_end), 1)
        self.assertEqual(len(engine._parent), 1)
        self.assertEqual(engine.selected_prints, 1)
        self.assertEqual(engine.input_prints, 258)
        self.assertEqual(engine._volume_total, 10 + 256 + 9)
        self.assertEqual(engine._sel_group_end, [10])
        self.assertEqual(engine.visited_selected_prints, 1)
        report = engine.finish()
        counts = work_map(report)
        age = 256 + 9
        expected = 10 * (2 ** (-float(Fraction(age, 20))))
        original = original_memory(rows, defn, end=400, cut=400)
        self.assertAlmostEqual(report["decayed_mass"][0], expected, delta=1e-12)
        self.assertAlmostEqual(report["decayed_mass"][0], original.decayed_mass[0], delta=1e-12)
        self.assertEqual(report["raw_mass"][0], 10)
        self.assertEqual(report["below_filter_prints"], 256)
        self.assertEqual(report["below_filter_volume"], 256)
        self.assertEqual(report["unpriced_prints"], 1)
        self.assertEqual(report["unpriced_volume"], 9)
        self.assertEqual(report["excluded_prints"], 257)
        self.assertEqual(counts["visited_selected_prints"], 1)
        self.assertEqual(counts["volume_groups"], 258)
        self.assertEqual(counts["cluster_inspected"], 1)
        self.assertLess(len(engine._sel_t), engine.input_prints)
        timed = window(definition(version="retain-time", minimum_size=5, decay_clock="time",
                                  decay_scale=20, decay_kernel="half_life"), end=400)
        timed.add_prepared(prepared)
        self.assertFalse(hasattr(timed, "_in_t"))
        self.assertEqual(len(timed._sel_t), 1)
        self.assertEqual(timed._sel_group_end, [])
        self.assertEqual(timed._volume_total, 0)
        self.assertIsNone(timed._pending_time)
        one, _ = finish(rows, defn, end=400)
        self.assertEqual(one["id"], report["id"])
        self.assertEqual(one["clusters"][0]["id"], report["clusters"][0]["id"])
        self.assertNotEqual(one["slices"], report["slices"])


def replace_key(row, key):
    copied = dict(row)
    copied["source_key"] = key
    return copied


def mutate_prepared(prepared, name, value, *, index=0):
    column = np.array(prepared.values[name], copy=True)
    column[index] = value
    prepared.values[name] = column
    return prepared


class BatchLineageAndRejection(unittest.TestCase):
    def path_rows(self):
        return [spec("a", 1, price=100, size=2, source_order=0),
                spec("b", 2, price=100, size=3, source_order=1, source_row=1),
                spec("c", 2, price=101, size=4, source_order=2, source_row=2),
                spec("d", 5, price=101, size=5, source_order=3, source_row=3)]

    def test_batch_slice_equality_and_first_to_last_source_lineage(self):
        rows = self.path_rows()
        defn = definition(version="slices", price_radius_ticks=1, time_radius_ns=10)
        prepared = prepared_from(rows)
        full, _ = finish(rows, defn, end=6)
        for index in range(len(rows) + 1):
            engine = window(defn, end=6)
            engine.add_prepared(prepared, 0, index)
            engine.add_prepared(prepared, index, len(rows))
            self.assertEqual(engine.finish()["id"], full["id"])
            self.assertEqual(engine.finish()["clusters"][0]["id"], full["clusters"][0]["id"])
        singles = window(defn, end=6)
        for index in range(len(rows)):
            singles.add_prepared(prepared, index, index + 1)
        assembled = singles.finish()
        self.assertEqual(assembled["id"], full["id"])
        self.assertEqual(full["first_print"]["source_row"], 0)
        self.assertEqual(full["last_print"]["source_row"], 3)
        self.assertEqual(full["first_print"]["source_key"], SOURCE)
        self.assertEqual(full["last_print"]["source_order"], 3)
        self.assertEqual(full["known_at_ns"], 6 + DELAY)
        self.assertEqual(full["source_key"], SOURCE)
        scientific = (
            "clusters", "field_cells", "overflow", "raw_mass", "decayed_mass",
            "input_prints", "input_volume", "selected_prints", "selected_volume",
            "excluded_prints", "excluded_volume", "first_print", "last_print",
            "history_complete", "order_exact", "below_filter_prints", "unpriced_prints",
        )
        for index in range(len(rows) + 1):
            engine = window(defn, end=6)
            engine.add_prepared(prepared, 0, index)
            engine.add_prepared(prepared, index, len(rows))
            got = engine.finish()
            for key in scientific:
                self.assertEqual(got[key], full[key])
            self.assertNotEqual(got["slices"], full["slices"])
            self.assertEqual(got["id"], full["id"])
        for member in full["clusters"][0]["members"]:
            for key in ("source_key", "source_row", "source_order", "event_at", "known_at_ns",
                        "price", "size", "raw_flags", "raw_action", "raw_side", "side"):
                self.assertIn(key, member)
        count = 65_536
        wide = [spec(str(index), index, price=100, source_order=index, source_row=index)
                for index in range(count)]
        prepared_wide = prepared_from(wide)
        self.assertEqual(len(prepared_wide), count)
        wide_window = window(definition(version="wide", time_radius_ns=0), end=count + 1,
                             max_selected_prints=count, max_clusters=count,
                             max_result_bytes=512 * 1024 * 1024)
        wide_window.add_prepared(prepared_wide, 0, count)
        wide_window.add_prepared(prepared_wide, count, count)
        wide_report = wide_window.finish()
        self.assertEqual(wide_report["input_prints"], count)
        self.assertEqual(wide_report["selected_prints"], count)
        self.assertEqual(wide_report["slices"], 2)

    def test_mutable_arrow_buffer_independence_uint64_and_empty_window(self):
        price = np.array([100, 104, 102], dtype=np.int64)
        rows = [spec("a", 0, price=100, source_order=0),
                spec("b", 0, price=104, source_order=1, source_row=1),
                spec("c", 1, price=102, source_order=2, source_row=2)]
        table = table_from(rows)
        table = table.set_column(table.schema.get_field_index("price"), "price", pa.array(price))
        prepared = prepare_trade_batch(table)
        price[0] = 999
        defn = definition(version="mut", price_radius_ticks=2, time_radius_ns=2)
        engine = window(defn, end=2)
        engine.add_prepared(prepared)
        report = engine.finish()
        self.assertEqual(report["clusters"][0]["low_ticks"], 100)
        self.assertEqual(report["clusters"][0]["high_ticks"], 104)
        base = 2 ** 63 + 100
        high = [spec("a", 1, price=100, source_order=0, source_row=base),
                spec("b", 2, price=100, source_order=1, source_row=base + 1)]
        prepared_high = prepared_from(high, source_row_type=pa.uint64())
        engine = window(definition(version="u64"), end=3)
        engine.add_prepared(prepared_high)
        got = engine.finish()
        self.assertGreater(got["clusters"][0]["members"][0]["source_row"], 2 ** 63)
        self.assertEqual(got["clusters"][0]["members"][0]["source_row"], base)
        self.assertEqual(got["last_print"]["source_row"], base + 1)
        empty = window(definition(version="empty"), end=3)
        empty.add_prepared(prepared_from([]), 0, 0)
        vacant = empty.finish()
        self.assertEqual(vacant["clusters"], ())
        self.assertEqual(vacant["raw_mass"], (0, 0, 0))
        self.assertTrue(vacant["empty_observed_window"])
        self.assertTrue(vacant["history_complete"])
        self.assertEqual(vacant["version"], VERSION)

    def test_strict_bounds_released_forged_mixed_future_delay_and_order_rejection(self):
        rows = [spec("a", 1, price=100, source_order=0), spec("b", 2, price=90, source_order=1, source_row=1)]
        prepared = prepared_from(rows)
        released = prepared_from(rows)
        released.release()
        with self.assertRaises(IntegrityError):
            window(definition()).add_prepared(released)
        forged = SimpleNamespace(released=False, values={}, source_key=lambda index: SOURCE)
        forged.__len__ = lambda: 0
        with self.assertRaises(IntegrityError):
            window(definition()).add_prepared(forged)
        mixed = [spec("a", 1, source_key="a", source_order=0),
                 spec("b", 2, source_key="b", source_order=1, source_row=1)]
        with self.assertRaises(IntegrityError):
            window(definition()).add_prepared(prepared_from(mixed))
        with self.assertRaises(IntegrityError):
            window(definition()).add_prepared(prepared_from(
                [spec("a", 1, instrument_id=2, source_order=0)]))
        with self.assertRaises(IntegrityError):
            window(definition(), end=2).add_prepared(prepared_from(
                [spec("late", 2, source_order=0)]))
        with self.assertRaises(IntegrityError):
            window(definition()).add_prepared(prepared_from(
                [spec("a", 1, source_order=0, known_at_ns=1 + DELAY + 1)]))
        with self.assertRaises(IntegrityError):
            window(definition()).add_prepared(prepared_from(
                [spec("a", 2, source_order=0), spec("b", 1, source_order=1, source_row=1)]))
        with self.assertRaises(IntegrityError):
            window(definition()).add_prepared(prepared_from(
                [spec("a", 1, source_order=2), spec("b", 2, source_order=2, source_row=3)]))
        with self.assertRaises(IntegrityError):
            window(definition()).add_prepared(prepared_from(
                [spec("a", 1, source_order=0, source_row=5),
                 spec("b", 2, source_order=1, source_row=5)]))
        with self.assertRaises(ContractError):
            window(definition()).add_prepared(prepared, history_complete=1)
        with self.assertRaises(IntegrityError):
            window(definition()).add_prepared(prepared, True, 1)
        with self.assertRaises(IntegrityError):
            window(definition()).add_prepared(prepared, 0, 3)
        with self.assertRaises(ContractError):
            definition(price_radius_ticks=65)
        with self.assertRaises(ContractError):
            definition(spatial_radius_ticks=65)
        with self.assertRaises(ContractError):
            definition(spatial_grid=(1, 3))
        with self.assertRaises(ContractError):
            window(definition(frozen_at=10), start=5)
        with self.assertRaises(DependencyUnavailable):
            AuctionFlowMemoryDefinition("visit-clock", decay_clock="visits")

    def test_mutated_quantity_signed_flags_and_forged_side_mapping_are_rejected(self):
        rows = [spec("a", 1, price=100, size=4, side=1, source_order=0)]
        defn = definition(version="mutated-domain")
        for quantity in (0, -1, 2 ** 32 - 1):
            prepared = mutate_prepared(prepared_from(rows), "size", quantity)
            with self.assertRaises(ContractError):
                window(defn).add_prepared(prepared)
        prepared = mutate_prepared(prepared_from(rows), "raw_flags", -256)
        with self.assertRaises(IntegrityError):
            window(defn).add_prepared(prepared)
        prepared = mutate_prepared(prepared_from(rows), "side", -1)
        with self.assertRaises(IntegrityError):
            window(defn).add_prepared(prepared)
        table = table_from([spec("u", 0, price=50, size=4, side=0, source_order=0)])
        table = table.set_column(
            table.schema.get_field_index("raw_side"), "raw_side",
            pa.array([None], type=pa.string()))
        engine = window(definition(version="null-side"), end=1)
        engine.add_prepared(prepare_trade_batch(table))
        vacant_side = engine.finish()
        self.assertIsNone(vacant_side["clusters"][0]["members"][0]["raw_side"])
        self.assertEqual(vacant_side["clusters"][0]["members"][0]["side"], 0)
        self.assertIsNone(vacant_side["first_print"]["raw_side"])
        self.assertEqual(vacant_side["unknown_side_prints"], 1)

    def test_poison_exact_and_one_over_limits_and_report_copy_independence(self):
        rows = [spec("a", 1, price=100, size=2, side=1, source_order=0),
                spec("b", 2, price=100, size=2, side=-1, source_order=1, source_row=1),
                spec("c", 3, price=100, size=2, side=0, source_order=2, source_row=2)]
        prepared = prepared_from(rows)
        capped = window(definition(version="cap"), max_input_rows=2, end=4)
        capped.add_prepared(prepared, 0, 2)
        exact = capped.finish()
        self.assertEqual(exact["input_prints"], 2)
        over = window(definition(version="cap"), max_input_rows=2, end=4)
        with self.assertRaises(ContractError):
            over.add_prepared(prepared)
        self.assertEqual(over.input_prints, 3)
        with self.assertRaises(IntegrityError):
            over.finish()
        selected = window(definition(version="sel"), max_selected_prints=2, end=4)
        selected.add_prepared(prepared, 0, 2)
        self.assertEqual(selected.finish()["selected_prints"], 2)
        selected_over = window(definition(version="sel"), max_selected_prints=2, end=4)
        with self.assertRaises(ContractError):
            selected_over.add_prepared(prepared)
        self.assertEqual(selected_over.selected_prints, 3)
        clusters = window(definition(version="cl"), max_clusters=1, end=4)
        clusters.add_prepared(prepared)
        with self.assertRaises(ContractError):
            clusters.finish()
        self.assertEqual(clusters.cluster_count, 2)
        self.assertEqual(clusters.cluster_inspected, 2)
        with self.assertRaises(IntegrityError):
            clusters.finish()
        tiny = window(definition(version="bytes"), max_result_bytes=8, end=4)
        tiny.add_prepared(prepared, 0, 1)
        with self.assertRaises(ContractError):
            tiny.finish()
        live = window(definition(version="copy", price_radius_ticks=0), end=4)
        live.add_prepared(prepared)
        report = live.finish()
        report["raw_mass"] = (0, 0, 0)
        report["clusters"] = ()
        report["work"] = (("visited_selected_prints", -1),)
        report["first_print"]["source_row"] = -1
        again = live.finish()
        self.assertEqual(again["raw_mass"], (2, 2, 2))
        self.assertEqual(len(again["clusters"]), 3)
        self.assertEqual(work_map(again)["visited_selected_prints"], 3)
        self.assertEqual(again["first_print"]["source_row"], 0)
        with self.assertRaises(IntegrityError):
            live.add_prepared(prepared, 0, 0)
        poisoned = window(definition(), end=4)
        poisoned.add_prepared(prepared, 0, 2)
        with self.assertRaises(IntegrityError):
            poisoned.add_prepared(prepared_from([spec("z", 3, source_order=1, source_row=9)]))
        with self.assertRaises(IntegrityError):
            poisoned.add_prepared(prepared, 2, 3)
        with self.assertRaises(IntegrityError):
            poisoned.finish()


class WorkCountCases(unittest.TestCase):
    def test_large_single_cluster_stops_at_byte_bound_and_exact_size_succeeds(self):
        rows = [spec(str(index), index, price=100, size=1,
                     source_order=index, source_row=index) for index in range(400)]
        defn = definition(version="bounded-members", time_radius_ns=1000)
        engine = window(defn, end=401, max_result_bytes=1000)
        engine.add_prepared(prepared_from(rows))
        with self.assertRaises(ContractError):
            engine.finish()
        self.assertEqual(engine.cluster_count, 1)
        self.assertGreater(engine.cluster_member_records, 0)
        self.assertLess(engine.cluster_member_records, len(rows))
        self.assertEqual(engine.kernel_operations, 0)
        with self.assertRaises(IntegrityError):
            engine.finish()
        small = rows[:2]
        baseline, _ = finish(small, defn, end=3)
        byte_count = len(canonical_json(baseline))
        exact, _ = finish(small, defn, end=3, max_result_bytes=byte_count)
        self.assertEqual(canonical_json(exact), canonical_json(baseline))
        with self.assertRaises(ContractError):
            finish(small, defn, end=3, max_result_bytes=byte_count - 1)

    def test_repeated_price_chain_lookups_scale_with_selected_count_and_radius(self):
        count = 64
        radius = 3
        rows = [spec(str(index), index, price=100, size=1, source_order=index, source_row=index)
                for index in range(count)]
        defn = definition(version="work", price_radius_ticks=radius, time_radius_ns=10 ** 9)
        report, engine = finish(rows, defn, end=count + 1)
        counts = work_map(report)
        lookups = count * (2 * radius + 1)
        pairs = count * (count - 1) // 2
        self.assertEqual(counts["visited_selected_prints"], count)
        self.assertEqual(counts["price_lookups"], lookups)
        self.assertEqual(engine.price_lookups, lookups)
        self.assertEqual(counts["union_attempts"], count - 1)
        self.assertEqual(counts["union_merges"], count - 1)
        self.assertEqual(counts["unions"], count - 1)
        self.assertEqual(engine.union_attempts, count - 1)
        self.assertEqual(engine.union_merges, count - 1)
        self.assertEqual(engine.unions, count - 1)
        self.assertEqual(counts["cluster_inspected"], count)
        self.assertLess(counts["price_lookups"], pairs)
        self.assertLess(counts["union_attempts"], pairs)
        self.assertLess(counts["unions"], pairs)
        self.assertEqual(len(report["clusters"]), 1)
        self.assertEqual(report["clusters"][0]["raw_count"], count)
        self.assertNotEqual(counts["price_lookups"], pairs)


class DefinitionAndCapacityDomain(unittest.TestCase):
    def test_grid_and_capacity_bounds_are_explicit(self):
        grid = tuple(range(65_536))
        wide = definition(version="grid", spatial_grid=grid)
        self.assertEqual(len(wide.spatial_grid), 65_536)
        with self.assertRaises(ContractError):
            definition(version="over-grid", spatial_grid=tuple(range(65_537)))
        with self.assertRaises(ContractError):
            window(definition(spatial_grid=tuple(range(8))), max_cells=4)
        with self.assertRaises(ContractError):
            window(definition(), max_input_rows=50_000_001)
        with self.assertRaises(ContractError):
            window(definition(), max_selected_prints=2_000_001)
        with self.assertRaises(ContractError):
            window(definition(), max_clusters=1_000_001)
        with self.assertRaises(ContractError):
            window(definition(), max_result_bytes=512 * 1024 * 1024 + 1)
        with self.assertRaises(DependencyUnavailable):
            AuctionFlowMemoryDefinition("visits-again", decay_clock="visits")
        self.assertNotEqual(definition(decay_scale=2).id, definition(decay_scale=3).id)
