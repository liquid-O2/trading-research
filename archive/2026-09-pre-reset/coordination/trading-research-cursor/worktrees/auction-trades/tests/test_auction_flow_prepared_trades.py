import importlib.util
import json
import sys
from pathlib import Path
import unittest

import numpy as np
import pyarrow as pa

from trading_research.errors import ContractError, IntegrityError
from trading_research.research.auction_flow_measurements import OrderedFlow, SOURCE_FILTERS, SparseSideMass
from trading_research.research.auction_flow_pipeline import InstrumentWindows, _parts
from trading_research.research.auction_flow_windows import TapeWindow, prepare_trade_batch
from tests.test_auction_flow_quotes import AuctionFlowQuoteTests, raw


REFERENCE_ROOT = Path(__file__).resolve().parents[1] / "references" / "auction_flow_trades_check7"


def load_frozen_trade_modules():
    manifest_path = REFERENCE_ROOT / "manifest.json"
    if not manifest_path.is_file():
        return None, None, None
    manifest = json.loads(manifest_path.read_text())
    files = manifest["files"]

    def load(name, filename):
        path = REFERENCE_ROOT / filename
        spec = importlib.util.spec_from_file_location(name, path)
        module = importlib.util.module_from_spec(spec)
        sys.modules[name] = module
        spec.loader.exec_module(module)
        return module

    measurements = load("auction_flow_trades_check7.measurements", next(name for name in files if name.endswith("measurements.py") or name == "measurements.py"))
    saved = sys.modules.get("trading_research.research.auction_flow_measurements")
    sys.modules["trading_research.research.auction_flow_measurements"] = measurements
    try:
        windows = load("auction_flow_trades_check7.windows", next(name for name in files if name.endswith("windows.py") or name == "windows.py"))
    finally:
        if saved is not None:
            sys.modules["trading_research.research.auction_flow_measurements"] = saved
        else:
            sys.modules.pop("trading_research.research.auction_flow_measurements", None)
    return windows, measurements, manifest


FROZEN_WINDOWS, FROZEN_MEASUREMENTS, FROZEN_MANIFEST = load_frozen_trade_modules()


def frozen_tape_window():
    if FROZEN_WINDOWS is None:
        raise unittest.SkipTest("controller-provided auction_flow_trades_check7 fixtures are unavailable")
    return FROZEN_WINDOWS.TapeWindow


def frozen_ordered_flow():
    if FROZEN_MEASUREMENTS is None:
        raise unittest.SkipTest("controller-provided auction_flow_trades_check7 fixtures are unavailable")
    return FROZEN_MEASUREMENTS.OrderedFlow


def frozen_sparse_mass():
    if FROZEN_MEASUREMENTS is None:
        raise unittest.SkipTest("controller-provided auction_flow_trades_check7 fixtures are unavailable")
    return FROZEN_MEASUREMENTS.SparseSideMass


def trade_row(t, *, source_order, instrument_id=1, price=400, size=1, side=None,
              price_valid=1, source_row=None, source_key="src", raw_flags=0,
              raw_side="B", raw_action="T", known_at_ns=None, delay=250):
    if side is None:
        side = 1 if raw_side == "B" else -1 if raw_side == "A" else 0
    if price is None:
        price, price_valid = 0, 0
    return {"t": t, "source_order": source_order, "instrument_id": instrument_id,
            "price": price, "size": size, "side": side, "price_valid": price_valid,
            "source_row": source_order if source_row is None else source_row,
            "source_key": source_key, "raw_flags": raw_flags, "raw_side": raw_side,
            "raw_action": raw_action, "known_at_ns": t + delay if known_at_ns is None else known_at_ns}


def make_trade_table(rows, *, action_type=None, side_type=None, source_key_type=None):
    numeric = ("t", "source_order", "instrument_id", "price", "size", "side", "price_valid",
               "source_row", "raw_flags", "known_at_ns")
    data = {name: [row[name] for row in rows] for name in numeric}

    def encode(values, typ):
        if typ is not None and (pa.types.is_binary(typ) or pa.types.is_large_binary(typ)):
            return [None if value is None else value.encode() if isinstance(value, str) else value for value in values]
        return values

    actions = encode([row["raw_action"] for row in rows], action_type)
    sides = encode([row["raw_side"] for row in rows], side_type)
    keys = encode([row["source_key"] for row in rows], source_key_type)
    arrays = {name: pa.array(data[name], type=pa.uint8() if name == "price_valid" else pa.int64())
              for name in numeric}
    arrays["raw_action"] = pa.array(actions) if action_type is None else pa.array(actions, type=action_type)
    arrays["raw_side"] = pa.array(sides) if side_type is None else pa.array(sides, type=side_type)
    arrays["source_key"] = pa.array(keys) if source_key_type is None else pa.array(keys, type=source_key_type)
    return pa.table(arrays)


def tape_window(Window, *, start=0, end=100, delay=250, instrument_id=1, maximum_trades=100,
                maximum_profile_cells=250000):
    return Window(instrument_id=instrument_id, start_ns=start, end_ns=end, latency_ns=delay,
                  maximum_trades=maximum_trades, maximum_profile_cells=maximum_profile_cells)


def publish(window, *, source=True, coordinate=True):
    return window.record(source_coverage_complete=source, coordinate_complete=coordinate)


def finish_ordinary(tables, Window=TapeWindow, **kwargs):
    window = tape_window(Window, **kwargs)
    for table in tables:
        window.add(table)
    return publish(window)


def finish_prepared(tables, **kwargs):
    window = tape_window(TapeWindow, **kwargs)
    for table in tables:
        with prepare_trade_batch(table) as prepared:
            window.add_prepared(prepared, 0, len(prepared))
    return publish(window)


def replay_atomic(tables, *, Window, start, end, width, delay=250, prepared=False, instrument_id=1):
    count = (end - start + width - 1) // width
    found = {}

    def window_at(number):
        if number not in found:
            a = start + number * width
            found[number] = tape_window(Window, start=a, end=min(a + width, end), delay=delay,
                                        instrument_id=instrument_id)
        return found[number]

    for table in tables:
        if prepared:
            with prepare_trade_batch(table) as batch:
                for number, left, right in batch.atomic_slices(start=start, width=width):
                    window_at(number).add_prepared(batch, left, right)
        else:
            for number, part in _parts(table, start=start, width=width):
                window_at(number).add(part)
    records = {}
    for number in range(count):
        current = found[number] if number in found else tape_window(
            Window, start=start + number * width, end=min(start + (number + 1) * width, end),
            delay=delay, instrument_id=instrument_id)
        records[number] = publish(current)
    return records


class AuctionFlowPreparedTradeTests(unittest.TestCase):
    def three_way(self, tables, **kwargs):
        frozen = finish_ordinary(tables, Window=frozen_tape_window(), **kwargs)
        self.assertEqual(finish_ordinary(tables, **kwargs), frozen)
        self.assertEqual(finish_prepared(tables, **kwargs), frozen)
        return frozen

    def projected_tables(self, values, *, end_ns=100, batch_rows=2):
        rows = []
        for at, price, size, side in values:
            row = raw(at, action="T", flags=0, size=size, side=side)
            row["price"] = None if price is None else price / 4
            rows.append(row)
        _, _, batches = AuctionFlowQuoteTests().projected(rows, end_ns=end_ns, batch_rows=batch_rows)
        return [t for b in batches for t in b.trades]

    def test_manifest_loads_independent_frozen_windows_and_measurements(self):
        self.assertIsNotNone(FROZEN_MANIFEST)
        self.assertIsNotNone(FROZEN_WINDOWS)
        self.assertIsNotNone(FROZEN_MEASUREMENTS)
        self.assertIn("auction_flow_trades_check7", FROZEN_WINDOWS.__file__)
        self.assertIn("auction_flow_trades_check7", FROZEN_MEASUREMENTS.__file__)
        self.assertIs(FROZEN_WINDOWS.OrderedFlow, FROZEN_MEASUREMENTS.OrderedFlow)
        self.assertIsNot(FROZEN_MEASUREMENTS.OrderedFlow, OrderedFlow)
        self.assertIsNot(FROZEN_MEASUREMENTS.SparseSideMass, SparseSideMass)

    def test_chunked_equal_time_unknown_unpriced_and_runs_match_frozen_records(self):
        values = [(10, 400, 2, "B"), (10, 403, 3, "A"), (10, 400, 4, "B"),
                  (40, None, 5, "N"), (60, 500, 6, "B"), (70, 499, 7, "A"),
                  (80, 499, 8, "A"), (90, 498, 9, "B")]
        chunks = self.projected_tables(values, batch_rows=2)
        together = pa.concat_tables(chunks)
        frozen = self.three_way(chunks)
        self.three_way([together])
        self.three_way([together.slice(offset, 1) for offset in range(len(together))])
        self.assertEqual(frozen["same_time_adjacent_prints"], 2)
        self.assertEqual(frozen["observed_adjacent_priced_pairs"], 5)
        self.assertIsNone(frozen["complete_path_displacement_ticks"])
        self.assertEqual(frozen["observed_maximum_same_side_run"], 2)
        self.assertEqual((frozen["flows"]["all"]["buy"], frozen["flows"]["all"]["sell"],
                          frozen["flows"]["all"]["unknown"]), (21, 18, 5))

    def test_source_filter_boundaries_and_strict_source_order_match_frozen(self):
        sizes = (29, 30, 60, 61, 74, 75, 99, 100)
        sides = ("B", "A", "B", "N", "A", "B", "A", "B")
        values = [(10 * (i + 1), 400 + i, size, side) for i, (size, side) in enumerate(zip(sizes, sides))]
        table = pa.concat_tables(self.projected_tables(values, batch_rows=3))
        result = self.three_way([table])
        for name in SOURCE_FILTERS:
            self.assertEqual(result["flows"][name]["prints"] + result["flows"][name]["excluded_prints"], 8, name)
        self.assertEqual(result["flows"]["inclusive30_through60"]["prints"], 2)
        self.assertEqual(result["flows"]["london_ge75"]["prints"], 3)
        self.assertEqual(result["flows"]["ny_ge100"]["prints"], 1)
        self.assertEqual(result["last_trade"]["source_order"], table["source_order"][-1].as_py())
        live = TapeWindow(instrument_id=1, start_ns=0, end_ns=100, latency_ns=250)
        frozen = frozen_tape_window()(instrument_id=1, start_ns=0, end_ns=100, latency_ns=250)
        live.add(table.slice(0, 4))
        frozen.add(table.slice(0, 4))
        with self.assertRaises(IntegrityError):
            live.add(table.slice(0, 1))
        with self.assertRaises(IntegrityError):
            frozen.add(table.slice(0, 1))
        with self.assertRaises(IntegrityError):
            live.record(source_coverage_complete=True, coordinate_complete=True)
        with self.assertRaises(IntegrityError):
            frozen.record(source_coverage_complete=True, coordinate_complete=True)

    def test_huge_opening_quantity_moments_and_unpriced_break_keep_exact_integers(self):
        table = make_trade_table([
            trade_row(10, source_order=0, price=1, size=2**31 - 1, raw_side="B"),
            trade_row(20, source_order=1, price=2**53 - 1, size=2**31 - 1, raw_side="A"),
            trade_row(30, source_order=2, price=None, size=7, raw_side="N"),
        ])
        result = self.three_way([table])
        self.assertEqual(result["observed_squared_price_variation_ticks_squared"], (2**53 - 2)**2)
        self.assertEqual(result["sum_squared_trade_sizes"], 2 * (2**31 - 1)**2 + 49)
        self.assertEqual(result["sparse_profile"]["unpriced_buy_sell_unknown"], (0, 0, 7))
        opening = 2**80 + 13
        arrays = dict(size=np.array([3, 5, 2], dtype=np.int64), side=np.array([1, -1, 0], dtype=np.int64),
                      event_ns=np.array([10, 20, 30], dtype=np.int64), source_order=np.array([0, 1, 2], dtype=np.int64))
        live = OrderedFlow(opening=opening)
        frozen = frozen_ordered_flow()(opening=opening)
        live.add(**arrays)
        frozen.add(**arrays)
        self.assertEqual(live.record(coverage_complete=True), frozen.record(coverage_complete=True))
        self.assertEqual(live.record(coverage_complete=True)["high"], opening + 3)

    def test_null_empty_dictionary_sides_and_owned_prepared_values(self):
        rows = [trade_row(10, source_order=0, raw_side="B"),
                trade_row(20, source_order=1, raw_side=None, side=0, price=None),
                trade_row(30, source_order=2, raw_side="N", side=0),
                trade_row(40, source_order=3, raw_side="A")]
        expected = self.three_way([make_trade_table(rows)])
        self.assertEqual(expected["flows"]["all"]["unknown"], 1 + 1)
        self.assertEqual(expected["unpriced_prints"], 1)
        for action_type, side_type, key_type in (
                (pa.dictionary(pa.int8(), pa.string()), pa.dictionary(pa.int8(), pa.string()), pa.string()),
                (pa.large_string(), pa.large_string(), pa.large_string())):
            with self.subTest(action_type=action_type):
                table = make_trade_table(rows, action_type=action_type, side_type=side_type, source_key_type=key_type)
                self.three_way([table])
        table = make_trade_table(rows)
        size = table["size"].to_numpy(zero_copy_only=False)
        with prepare_trade_batch(table) as prepared:
            original = np.array(prepared.values["size"], copy=True)
            if size.flags.writeable:
                size[:] = 99
            self.assertFalse(prepared.values["size"].flags.writeable)
            with self.assertRaises(ValueError):
                prepared.values["size"][0] = 8
            self.assertTrue(np.array_equal(prepared.values["size"], original))
            TapeWindow(instrument_id=1, start_ns=0, end_ns=100, latency_ns=250).add_prepared(prepared, 0, len(prepared))
        self.assertTrue(prepared.released)
        self.assertEqual(prepared.values, {})

    def test_reader_and_atomic_cuts_share_one_prepare_and_match_frozen(self):
        values = [(10, 400, 29, "B"), (25, 401, 30, "A"), (40, None, 75, "N"),
                  (70, 500, 100, "B"), (90, 499, 61, "A")]
        chunks = self.projected_tables(values, batch_rows=2)
        together = pa.concat_tables(chunks)
        frozen = replay_atomic(chunks, Window=frozen_tape_window(), start=0, end=100, width=30, delay=250)
        ordinary = replay_atomic(chunks, Window=TapeWindow, start=0, end=100, width=30, delay=250)
        prepared = replay_atomic(chunks, Window=TapeWindow, start=0, end=100, width=30, delay=250, prepared=True)
        self.assertEqual(ordinary, frozen)
        self.assertEqual(prepared, frozen)
        self.assertEqual(replay_atomic([together], Window=frozen_tape_window(), start=0, end=100, width=30, delay=250),
                         frozen)
        pair = make_trade_table([trade_row(10, source_order=0), trade_row(40, source_order=1)])
        import trading_research.research.auction_flow_pipeline as pipeline
        calls = []
        original = pipeline.prepare_trade_batch

        def counted(table):
            calls.append(len(table))
            return original(table)

        pipeline.prepare_trade_batch = counted
        try:
            windows = InstrumentWindows(1, 0, 100, 30, 250, 100, 100, 20)
            windows.trade_rows(together)
            pair_windows = InstrumentWindows(1, 0, 100, 30, 250, 100, 100, 20)
            pair_windows.trade_rows(pair)
        finally:
            pipeline.prepare_trade_batch = original
        self.assertEqual(calls, [len(together), len(pair)])
        self.assertEqual(pair_windows.work["trade_atomic_parts"], 2)
        self.assertIn("whole_trade_and_native_consumers", windows.cpu)
        self.assertIn("trade_atomic_consumers", windows.cpu)
        self.assertEqual(publish(windows.whole_tape), finish_ordinary([together], Window=frozen_tape_window()))
        for number, record in frozen.items():
            if record["prints"]:
                self.assertEqual(publish(windows.tape[number]), record)
        pair_frozen = replay_atomic([pair], Window=frozen_tape_window(), start=0, end=100, width=30, delay=250)
        self.assertEqual(publish(pair_windows.whole_tape), finish_ordinary([pair], Window=frozen_tape_window()))
        self.assertEqual(publish(pair_windows.tape[0]), pair_frozen[0])
        self.assertEqual(publish(pair_windows.tape[1]), pair_frozen[1])

    def test_instrument_delay_snapshot_null_and_malformed_inputs_poison_like_frozen(self):
        good = make_trade_table([trade_row(10, source_order=0), trade_row(20, source_order=1)])
        missing = good.drop(["source_key"])
        null_clock = good.set_column(good.schema.get_field_index("t"), "t", pa.array([10, None], type=pa.int64()))
        null_side = make_trade_table([trade_row(10, source_order=0, raw_side=None, side=0)])
        known = good.set_column(good.schema.get_field_index("known_at_ns"), "known_at_ns",
                                pa.array([1, 2], type=pa.int64()))
        other = make_trade_table([trade_row(10, source_order=0, instrument_id=2)])
        snapshot = make_trade_table([trade_row(10, source_order=0, raw_flags=32)])
        mapped = make_trade_table([trade_row(10, source_order=0, side=-1, raw_side="B")])
        action = make_trade_table([trade_row(10, source_order=0, raw_action="M")])
        empty = good.slice(0, 0)
        cases = ((ContractError, lambda window: window.add(missing)),
                 (IntegrityError, lambda window: window.add(null_clock)),
                 (IntegrityError, lambda window: window.add(known)),
                 (IntegrityError, lambda window: window.add(other)),
                 (IntegrityError, lambda window: window.add(snapshot)),
                 (IntegrityError, lambda window: window.add(mapped)),
                 (IntegrityError, lambda window: window.add(action)))
        for Window in (TapeWindow, frozen_tape_window()):
            for error, call in cases:
                with self.subTest(window=Window.__module__, error=error.__name__):
                    with self.assertRaises(error):
                        call(Window(instrument_id=1, start_ns=0, end_ns=100, latency_ns=250, maximum_trades=100))
            accepted = Window(instrument_id=1, start_ns=0, end_ns=100, latency_ns=250)
            accepted.add(null_side)
            self.assertEqual(publish(accepted)["flows"]["all"]["unknown"], 1)
            Window(instrument_id=1, start_ns=0, end_ns=100, latency_ns=250).add(empty)
        self.three_way([null_side])
        self.three_way([empty])
        with self.assertRaises(IntegrityError):
            tape_window(TapeWindow, delay=0).add(good)
        with self.assertRaises(IntegrityError):
            tape_window(frozen_tape_window(), delay=0).add(good)
        with self.assertRaises(IntegrityError):
            prepare_trade_batch(null_clock)
        with self.assertRaises(IntegrityError):
            TapeWindow(instrument_id=1, start_ns=0, end_ns=100, latency_ns=250).add_prepared(good, 0, 2)
        prepared = prepare_trade_batch(good)
        prepared.close()
        with self.assertRaises(IntegrityError):
            TapeWindow(instrument_id=1, start_ns=0, end_ns=100, latency_ns=250).add_prepared(prepared, 0, 2)
        with prepare_trade_batch(good) as batch:
            TapeWindow(instrument_id=1, start_ns=0, end_ns=100, latency_ns=250).add_prepared(batch, 0, 0)
            for start, stop in ((0.5, 2), (True, 2), (-1, 2), (0, 3), (2, 0)):
                with self.subTest(start=start, stop=stop):
                    with self.assertRaises(IntegrityError):
                        TapeWindow(instrument_id=1, start_ns=0, end_ns=100, latency_ns=250).add_prepared(batch, start, stop)
            TapeWindow(instrument_id=1, start_ns=0, end_ns=100, latency_ns=250).add_prepared(batch, 0, 2)
        live = TapeWindow(instrument_id=1, start_ns=0, end_ns=100, latency_ns=250)
        frozen = frozen_tape_window()(instrument_id=1, start_ns=0, end_ns=100, latency_ns=250)
        live.add(good.slice(0, 1))
        frozen.add(good.slice(0, 1))
        with self.assertRaises(IntegrityError):
            live.add(snapshot)
        with self.assertRaises(IntegrityError):
            frozen.add(snapshot)
        with self.assertRaises(IntegrityError):
            live.record(source_coverage_complete=True, coordinate_complete=True)
        with self.assertRaises(IntegrityError):
            frozen.record(source_coverage_complete=True, coordinate_complete=True)

    def test_ordinary_flow_and_profile_boundaries_stay_checked(self):
        arrays = dict(size=np.array([1.5]), side=np.array([1]), event_ns=np.array([1]), source_order=np.array([0]))
        with self.assertRaises(ContractError):
            OrderedFlow().add(**arrays)
        with self.assertRaises(ContractError):
            frozen_ordered_flow()().add(**arrays)
        with self.assertRaises(ContractError):
            SparseSideMass().add(price_ticks=np.array([0]), price_valid=np.array([1]),
                                 size=np.array([1]), side=np.array([1]))
        with self.assertRaises(ContractError):
            frozen_sparse_mass()().add(price_ticks=np.array([0]), price_valid=np.array([1]),
                                       size=np.array([1]), side=np.array([1]))


if __name__ == "__main__":
    unittest.main()
