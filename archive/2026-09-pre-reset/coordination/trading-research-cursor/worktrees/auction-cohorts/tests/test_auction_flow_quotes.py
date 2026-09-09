from fractions import Fraction
from pathlib import Path
import tempfile
import unittest

import pyarrow as pa
import pyarrow.parquet as pq

from references.auction_flow_quote_check6.quotes import QuoteWindow as FrozenQuoteWindow
from trading_research.data.book import BookReducer
from trading_research.data.events import Flags, LatencyScenario, SourceAddress, normalize_mbp
from trading_research.data.reconcile import footer_index
from trading_research.errors import ContractError, IntegrityError
from trading_research.measurements.quotes import transition_metrics
from trading_research.research.auction_flow_data import AuctionFlowStream, RAW_FIELDS
from trading_research.research.auction_flow_native_bins import NativeEventBins, QUOTE_FIELDS
from trading_research.research.auction_flow_quotes import QuoteWindow, prepare_quote_batch


def frozen_quote_window():
    return FrozenQuoteWindow


DATASET = "quantpad/cme__nq-continuous-futures__mbp-1"


def raw(at, *, action="M", flags=128, bid=100., ask=100.25, qb=7, qa=9, size=1, side="B"):
    return {"t": at, "action": action, "side": side, "price": ask, "size": size,
            "bid_px": bid, "ask_px": ask, "bid_sz": qb, "ask_sz": qa,
            "instrument_id": 1, "flags": flags}


def reference(rows, end=100, maximum_age=None):
    reducer = BookReducer()
    at, duration, weighted, positive, ofi, same = 0, 0, Fraction(0), 0, 0, 0
    updates, normalized, micro, spread, path = [], Fraction(0), Fraction(0), Fraction(0), [0]

    def expose(state, a, b):
        if not state or not state.trusted or state.economic_quote_at is None:
            return 0, Fraction(0), 0
        if maximum_age is not None:
            b = min(b, state.economic_quote_at + maximum_age)
        dt = max(0, b - a)
        q = state.quote
        return dt, dt * Fraction(q.bid_size - q.ask_size, q.bid_size + q.ask_size), dt if q.bid_size > q.ask_size else 0

    for i, row in enumerate(rows):
        event = normalize_mbp(row, SourceAddress(DATASET, "fixture", "fixture.parquet", "fixture",
                              "all", i, "eleven-fields"), native=False,
                              scenario=LatencyScenario("event-delay", "event", 250, 0))
        before = reducer.states.get(1)
        dt, mass, pos = expose(before, at, row["t"])
        duration += dt
        weighted += mass
        positive += pos
        tr = reducer.apply(event)
        value = transition_metrics(event, tr)
        if value is not None:
            p, q = tr.before.quote, tr.after.quote
            current_same = (q.bid_size - p.bid_size if q.bid == p.bid else 0) - (q.ask_size - p.ask_size if q.ask == p.ask else 0)
            ofi += value.ofi_contracts
            same += current_same
            path.append(ofi)
            updates.append(value.queue_imbalance)
            normalized += Fraction(value.ofi_contracts, p.bid_size + p.ask_size)
            micro += 4 * (value.microprice_points - (Fraction(q.bid) + Fraction(q.ask)) / 2)
            spread += 4 * value.spread_points
        at = row["t"]
    dt, mass, pos = expose(reducer.states.get(1), at, end)
    duration += dt
    weighted += mass
    positive += pos
    n = len(updates)
    return {"ofi_contracts": ofi, "same_price_size_ofi": same, "price_change_ofi": ofi - same,
            "pressure_transitions": n, "fresh_quote_updates": reducer.states[1].fresh_book_events,
            "sum_depth_normalized_ofi": normalized,
            "update_mean_imbalance": sum(updates) / n if n else None,
            "update_positive_fraction": Fraction(sum(q > 0 for q in updates), n) if n else None,
            "update_mean_microprice_minus_midpoint_ticks": micro / n if n else None,
            "update_mean_spread_ticks": spread / n if n else None,
            "observed_trusted_standing_duration_ns": duration,
            "duration_mean_imbalance": weighted / duration if duration else None,
            "duration_positive_fraction": Fraction(positive, duration) if duration else None,
            "high": max(path), "low": min(path)}


class AuctionFlowQuoteTests(unittest.TestCase):
    def test_displayed_midpoint_occupancy_uses_actual_quote_clocks_and_keeps_half_tick_grid_boundaries(self):
        rows = [raw(0, action='A', flags=32), raw(10, action='A'),
            raw(30, bid=100.25, ask=100.5), raw(50, action='T', bid=200., ask=200.25, flags=0),
            raw(70, action='R')]
        quotes, _, _ = self.projected(rows)
        value = self.measure(quotes)
        occupancy = value['displayed_midpoint_occupancy']
        self.assertEqual(occupancy['duration_ns_by_row'], ((400, 20), (401, 40)))
        self.assertEqual(occupancy['observed_assigned_duration_ns'], 60)
        self.assertEqual(occupancy['unassigned_duration_ns'], 40)
        self.assertFalse(occupancy['trade_residence_claim'])

    def projected(self, rows, *, batch_rows=2, start_ns=0, end_ns=100):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            path = root / DATASET / "fixture.parquet"
            path.parent.mkdir(parents=True)
            schema = pa.schema([pa.field(name, pa.string() if name in ("action", "side")
                                         else pa.float64() if name in ("price", "bid_px", "ask_px")
                                         else pa.int64()) for name in RAW_FIELDS])
            pq.write_table(pa.Table.from_pylist(rows, schema=schema), path, row_group_size=3)
            index = footer_index(root, datasets=(DATASET,), max_files=1)
            stream = AuctionFlowStream(data_root=root, index=index, dataset=DATASET,
                start_ns=start_ns, end_ns=end_ns, maximum_scan_rows=100, latency_ns=250, batch_rows=batch_rows)
            batches = list(stream)
            return [q for b in batches for q in b.quotes], stream.manifest(), batches

    def measure(self, quotes, *, maximum_age=None, complete=True):
        result = QuoteWindow(instrument_id=1, start_ns=0, end_ns=100,
                             latency_ns=250, maximum_events=100, maximum_age_ns=maximum_age)
        for q in quotes:
            result.add(q)
        return result.finish(coverage_complete=complete)

    def assert_reference(self, rows, *, maximum_age=None):
        q, _, _ = self.projected(rows)
        result = self.measure(q, maximum_age=maximum_age)
        expected = reference(rows, maximum_age=maximum_age)
        for key, value in expected.items():
            if key in ("high", "low"):
                self.assertEqual(result["ofi_path"][key], value)
            elif value is None or isinstance(value, int):
                self.assertEqual(result[key], value, key)
            else:
                self.assertAlmostEqual(result[key], float(value), delta=1e-12, msg=key)
        return result

    def test_original_replay_parity_and_independent_ordered_quote_arithmetic(self):
        rows = [raw(10, action="A", flags=32), raw(20, qb=11, qa=5),
                raw(25, action="T", flags=0, qb=999, qa=1),
                raw(30, bid=100.25, ask=100.5, qb=6, qa=4),
                raw(35, flags=32, bid=100.25, ask=100.5, qb=9, qa=1),
                raw(40, bid=100.25, ask=100.5, qb=8, qa=2),
                raw(40, bid=100.25, ask=100.5, qb=7, qa=3),
                raw(50, flags=132), raw(60), raw(70, flags=32)]
        result = self.assert_reference(rows)
        self.assertEqual((result["ofi_contracts"], result["same_price_size_ofi"], result["price_change_ofi"]), (15, 4, 11))
        self.assertEqual(result["ofi_path"], {"open": 0, "high": 19, "low": 0, "close": 15,
            "high_at_ns": 30, "low_at_ns": None, "high_source_order": 3, "low_source_order": None})
        self.assertEqual(result["observed_trusted_standing_duration_ns"], 30)
        self.assertAlmostEqual(result["duration_mean_imbalance"], 17 / 40, delta=1e-12)
        self.assertEqual(result["equal_time_adjacent_quote_rows"], 1)
        self.assertFalse(result["exchange_order_certified"])
        q, _, _ = self.projected(rows, batch_rows=100)
        together = self.measure(q)
        self.assertEqual(result["ofi_path"], together["ofi_path"])
        self.assertAlmostEqual(result["duration_mean_imbalance"], together["duration_mean_imbalance"], delta=1e-12)

    def test_snapshot_does_not_create_fresh_age_or_recover_an_invalidated_book(self):
        snapshots = [raw(10, flags=32), raw(90, flags=160)]
        result = self.assert_reference(snapshots)
        self.assertEqual(result["fresh_quote_updates"], 0)
        self.assertEqual(result["observed_trusted_standing_duration_ns"], 0)
        for invalid in (raw(20, action="R"), raw(20, action="?"), raw(20, action="T", flags=4)):
            with self.subTest(invalid=invalid["action"]):
                result = self.assert_reference([raw(10), invalid, raw(30, flags=32), raw(40)])
                self.assertEqual(result["observed_trusted_standing_duration_ns"], 10)
                self.assertFalse(result["terminal_projection"]["book_valid"])

    def test_non_crossed_locked_quotes_and_undefined_sizes_keep_source_semantics(self):
        rows = [raw(10, bid=100, ask=100, qb=2, qa=1),
                raw(20, bid=100, ask=100, qb=4, qa=2),
                raw(25, action="T", size=2**32 - 1), raw(30, qb=2**32 - 1),
                raw(40, qb=2**32 - 2), raw(50, action="T", size=2**32 - 2)]
        result = self.assert_reference(rows)
        q, manifest, batches = self.projected(rows)
        first = q[0].to_pylist()[0]
        self.assertEqual((first["book_valid"], first["legacy_positive_spread_book_valid"]), (1, 0))
        self.assertEqual(result["ofi_contracts"], 1)
        self.assertEqual(manifest["projection"]["counts"]["volume"], 2**32 - 2)
        self.assertEqual(manifest["trade_exclusions"]["invalid_size_trade_rows"], 1)
        self.assertFalse(manifest["projection"]["observed_prefix_flow_complete"]["1"])
        excluded = [r for b in batches for r in b.excluded_trades.to_pylist()]
        self.assertEqual([(r["t"], r["exclusion_bits"]) for r in excluded], [(25, 2)])

    def test_standing_age_and_window_coverage_remain_separate_from_valid_quotes(self):
        rows = [raw(10, qb=6, qa=2), raw(20, flags=32, qb=5, qa=3), raw(70)]
        result = self.assert_reference(rows, maximum_age=15)
        self.assertEqual(result["observed_trusted_standing_duration_ns"], 30)
        q, _, _ = self.projected(rows)
        result = self.measure(q, complete=False)
        self.assertIsNone(result["per_complete_window_second_ofi"])
        self.assertFalse(result["coverage_complete"])

    def test_duplicate_order_information_clock_and_repeated_publication_are_rejected(self):
        q, _, _ = self.projected([raw(10), raw(20)])
        value = QuoteWindow(instrument_id=1, start_ns=0, end_ns=100, latency_ns=250)
        value.add(q[0])
        with self.assertRaises(IntegrityError):
            value.add(q[0])
        value.finish(coverage_complete=True)
        with self.assertRaises(IntegrityError):
            value.finish(coverage_complete=True)
        bad = q[0].set_column(q[0].schema.get_field_index("known_at_ns"), "known_at_ns", pa.array([1] * len(q[0])))
        with self.assertRaises(IntegrityError):
            QuoteWindow(instrument_id=1, start_ns=0, end_ns=100, latency_ns=250).add(bad)

    def test_adjacent_and_quiet_windows_retain_standing_age_and_boundary_ofi(self):
        quotes, _, _ = self.projected([raw(10, qb=9, qa=3), raw(70, qb=3, qa=9), raw(90, qb=7, qa=5)])
        all_rows = pa.concat_tables(quotes)
        whole = self.measure([all_rows])
        first = QuoteWindow(instrument_id=1, start_ns=0, end_ns=30, latency_ns=250)
        first.add(all_rows.slice(0, 1))
        a = first.finish(coverage_complete=True)
        middle = first.continue_window(end_ns=60)
        b = middle.finish(coverage_complete=True)
        last = middle.continue_window(end_ns=100)
        last.add(all_rows.slice(1))
        c = last.finish(coverage_complete=True)
        self.assertEqual(b["fresh_quote_updates"], 0)
        self.assertEqual(b["observed_trusted_standing_duration_ns"], 30)
        self.assertEqual(b["terminal_projection"]["economic_at"], 10)
        self.assertEqual(c["initial_projection"]["source_order"], 0)
        for key in ("ofi_contracts", "same_price_size_ofi", "price_change_ofi", "pressure_transitions",
                    "fresh_quote_updates", "observed_trusted_standing_duration_ns"):
            self.assertEqual(sum(r[key] for r in (a, b, c)), whole[key], key)
        weighted = sum(r["duration_mean_imbalance"] * r["observed_trusted_standing_duration_ns"] for r in (a, b, c))
        self.assertAlmostEqual(weighted / whole["observed_trusted_standing_duration_ns"], whole["duration_mean_imbalance"], delta=1e-12)


def quote_row(t, *, source_order, instrument_id=1, bid=400, ask=401, bid_size=7, ask_size=9,
              book_valid=1, snapshot=0, raw_flags=128, raw_action="M", raw_side="B",
              known_at_ns=None, source_key="src", source_row=None, delay=250):
    if snapshot:
        raw_flags = raw_flags | 32
    return {"t": t, "source_order": source_order, "instrument_id": instrument_id,
            "bid": bid, "ask": ask, "bid_size": bid_size, "ask_size": ask_size,
            "book_valid": book_valid, "snapshot": snapshot, "raw_flags": raw_flags,
            "raw_action": raw_action, "raw_side": raw_side,
            "known_at_ns": t + delay if known_at_ns is None else known_at_ns,
            "source_key": source_key, "source_row": source_order if source_row is None else source_row}


def make_quote_table(rows, *, action_type=None, side_type=None, source_key_type=None):
    numeric = ("t", "source_order", "instrument_id", "bid", "ask", "bid_size", "ask_size",
               "book_valid", "snapshot", "raw_flags", "known_at_ns", "source_row")
    data = {name: [row[name] for row in rows] for name in numeric}

    def encode(values, typ):
        if typ is not None and (pa.types.is_binary(typ) or pa.types.is_large_binary(typ)):
            return [None if value is None else value.encode() if isinstance(value, str) else value for value in values]
        return values

    actions = encode([row["raw_action"] for row in rows], action_type)
    sides = encode([row["raw_side"] for row in rows], side_type)
    keys = encode([row["source_key"] for row in rows], source_key_type)
    arrays = {name: pa.array(data[name], type=pa.uint8() if name in ("book_valid", "snapshot") else pa.int64())
              for name in numeric}
    arrays["raw_action"] = pa.array(actions) if action_type is None else pa.array(actions, type=action_type)
    arrays["raw_side"] = pa.array(sides) if side_type is None else pa.array(sides, type=side_type)
    arrays["source_key"] = pa.array(keys) if source_key_type is None else pa.array(keys, type=source_key_type)
    return pa.table(arrays)


def quote_window(Window, *, start=0, end=100, delay=250, maximum_age=None,
                 maximum_events=100, native_sink=None):
    return Window(instrument_id=1, start_ns=start, end_ns=end, latency_ns=delay,
                  maximum_events=maximum_events, maximum_age_ns=maximum_age, native_sink=native_sink)


def finish_ordinary(tables, Window=QuoteWindow, *, complete=True, **kwargs):
    window = quote_window(Window, **kwargs)
    for table in tables:
        window.add(table)
    return window.finish(coverage_complete=complete)


def finish_prepared(tables, *, complete=True, **kwargs):
    window = quote_window(QuoteWindow, **kwargs)
    for table in tables:
        with prepare_quote_batch(table) as prepared:
            window.add_prepared(prepared)
    return window.finish(coverage_complete=complete)


def replay_atomic(tables, *, Window, start, end, width, delay=250, prepared=False,
                  maximum_events=100, native_sink=None):
    from trading_research.research.auction_flow_pipeline import _parts

    count = (end - start + width - 1) // width
    current = quote_window(Window, start=start, end=min(start + width, end), delay=delay,
                           maximum_events=maximum_events, native_sink=native_sink)
    closed, bin_no = {}, 0

    def advance(number):
        nonlocal current, bin_no
        while bin_no < number:
            closed[bin_no] = current.finish(coverage_complete=False)
            bin_no += 1
            current = current.continue_window(end_ns=min(start + (bin_no + 1) * width, end))

    for table in tables:
        if prepared:
            with prepare_quote_batch(table) as batch:
                for number, left, right in batch.atomic_slices(start=start, width=width):
                    advance(number)
                    current.add_prepared(batch, left, right)
        else:
            for number, part in _parts(table, start=start, width=width):
                advance(number)
                current.add(part)
    while bin_no < count:
        closed[bin_no] = current.finish(coverage_complete=False)
        bin_no += 1
        if bin_no < count:
            current = current.continue_window(end_ns=min(start + (bin_no + 1) * width, end))
    return closed


class AuctionFlowPreparedQuoteTests(unittest.TestCase):
    def three_way(self, tables, **kwargs):
        frozen = finish_ordinary(tables, Window=frozen_quote_window(), **kwargs)
        self.assertEqual(finish_ordinary(tables, **kwargs), frozen)
        self.assertEqual(finish_prepared(tables, **kwargs), frozen)
        return frozen

    def three_way_native(self, tables, *, start=0, end=100, width=20, delay=250, **kwargs):
        records, columns = [], []
        for mode in ("ordinary", "prepared", "frozen"):
            sink = NativeEventBins(instrument_id=1, start_ns=start, end_ns=end, width_ns=width)
            if mode == "prepared":
                records.append(finish_prepared(tables, start=start, end=end, delay=delay, native_sink=sink, **kwargs))
            elif mode == "ordinary":
                records.append(finish_ordinary(tables, start=start, end=end, delay=delay, native_sink=sink, **kwargs))
            else:
                records.append(finish_ordinary(tables, Window=frozen_quote_window(), start=start, end=end,
                                               delay=delay, native_sink=sink, **kwargs))
            columns.append({name: sink.columns[name].copy() for name in (*QUOTE_FIELDS, "duration_imbalance_ns",
                                                                         "duration_spread_ticks_ns")})
        self.assertEqual(records[0], records[2])
        self.assertEqual(records[1], records[2])
        for name in columns[0]:
            self.assertTrue((columns[0][name] == columns[2][name]).all(), name)
            self.assertTrue((columns[1][name] == columns[2][name]).all(), name)
        return records[2]

    def projected_tables(self, rows, **kwargs):
        quotes, _, _ = AuctionFlowQuoteTests().projected(rows, **kwargs)
        return quotes, pa.concat_tables(quotes) if quotes else pa.table({})

    def test_chunked_equal_time_snapshot_and_gap_rows_match_frozen_reference(self):
        rows = [raw(10, action="A", flags=32), raw(20, qb=11, qa=5),
                raw(25, action="T", flags=0, qb=999, qa=1),
                raw(30, bid=100.25, ask=100.5, qb=6, qa=4),
                raw(35, flags=32, bid=100.25, ask=100.5, qb=9, qa=1),
                raw(40, bid=100.25, ask=100.5, qb=8, qa=2),
                raw(40, bid=100.25, ask=100.5, qb=7, qa=3),
                raw(50, flags=132), raw(60), raw(70, flags=32)]
        chunks, together = self.projected_tables(rows)
        self.three_way_native(chunks)
        self.three_way([together])
        self.three_way([together.slice(offset, 1) for offset in range(len(together))])
        whole = finish_ordinary([together])
        chunked = finish_ordinary(chunks)
        self.assertEqual(whole["ofi_path"], chunked["ofi_path"])
        self.assertEqual(whole["action_side_counts"], chunked["action_side_counts"])
        self.assertEqual(whole["terminal_projection"], chunked["terminal_projection"])
        self.assertAlmostEqual(whole["duration_mean_imbalance"], chunked["duration_mean_imbalance"], delta=1e-12)

    def test_clears_gaps_snapshots_and_quiet_cuts_do_not_invent_recovery(self):
        snapshots, _ = self.projected_tables([raw(10, flags=32), raw(90, flags=160)])
        self.three_way(snapshots)
        for invalid in (raw(20, action="R"), raw(20, action="?"), raw(20, action="T", flags=4)):
            with self.subTest(invalid=invalid["action"]):
                tables, _ = self.projected_tables([raw(10), invalid, raw(30, flags=32), raw(40)])
                result = self.three_way(tables)
                self.assertEqual(result["observed_trusted_standing_duration_ns"], 10)
                self.assertFalse(result["terminal_projection"]["book_valid"])
        quotes, _ = self.projected_tables([raw(10, qb=9, qa=3), raw(70, qb=3, qa=9), raw(90, qb=7, qa=5)])
        frozen = replay_atomic(quotes, Window=frozen_quote_window(), start=0, end=100, width=30, delay=250)
        ordinary = replay_atomic(quotes, Window=QuoteWindow, start=0, end=100, width=30, delay=250)
        prepared = replay_atomic(quotes, Window=QuoteWindow, start=0, end=100, width=30, delay=250, prepared=True)
        self.assertEqual(ordinary, frozen)
        self.assertEqual(prepared, frozen)
        self.assertEqual(frozen[1]["fresh_quote_updates"], 0)
        self.assertEqual(frozen[1]["quote_or_invalidation_rows"], 0)
        self.assertEqual(frozen[1]["terminal_projection"]["economic_at"], 10)
        self.assertEqual(frozen[1]["initial_projection"]["source_order"], frozen[1]["terminal_projection"]["source_order"])

    def test_null_empty_binary_and_dictionary_categories_stay_distinct(self):
        rows = [quote_row(10, source_order=0, raw_action="A"),
                quote_row(20, source_order=1, book_valid=0, raw_action=None, raw_side=None,
                          bid=0, ask=0, bid_size=0, ask_size=0),
                quote_row(30, source_order=2, book_valid=0, raw_action=None, raw_side="B",
                          bid=0, ask=0, bid_size=0, ask_size=0),
                quote_row(40, source_order=3, book_valid=0, raw_action="R", raw_side=None,
                          bid=0, ask=0, bid_size=0, ask_size=0),
                quote_row(50, source_order=4, book_valid=0, raw_action="", raw_side="",
                          bid=0, ask=0, bid_size=0, ask_size=0),
                quote_row(60, source_order=5, bid_size=8, ask_size=2)]
        expected = self.three_way([make_quote_table(rows)])
        keys = {(item["action"], item["side"]) for item in expected["action_side_counts"]}
        self.assertEqual(keys, {("A", "B"), (None, None), (None, "B"), ("R", None), ("", ""), ("M", "B")})
        self.assertEqual(expected["terminal_projection"]["raw_action"], "M")
        for action_type, side_type, key_type in (
                (pa.dictionary(pa.int8(), pa.string()), pa.dictionary(pa.int8(), pa.string()), pa.string()),
                (pa.binary(), pa.binary(), pa.binary()),
                (pa.large_string(), pa.large_string(), pa.large_string())):
            with self.subTest(action_type=action_type):
                table = make_quote_table(rows, action_type=action_type, side_type=side_type, source_key_type=key_type)
                self.three_way([table])
                last = finish_prepared([table])["terminal_projection"]
                self.assertEqual(last["raw_action"], table["raw_action"][-1].as_py())
                self.assertEqual(last["raw_side"], table["raw_side"][-1].as_py())
                self.assertEqual(last["source_key"], table["source_key"][-1].as_py())

    def test_large_clocks_depths_and_equal_timestamps_keep_integer_path(self):
        base = 2**62
        depth = 2**32 - 2
        rows = [quote_row(base, source_order=0, raw_action="A", snapshot=1, bid_size=depth, ask_size=depth - 1),
                quote_row(base + 10, source_order=1, bid_size=depth, ask_size=depth - 3),
                quote_row(base + 10, source_order=2, bid_size=depth - 4, ask_size=depth - 3),
                quote_row(base + 40, source_order=3, bid=401, ask=403, bid_size=depth - 5, ask_size=3)]
        result = self.three_way_native([make_quote_table(rows)], start=base, end=base + 100, width=20, delay=250)
        self.assertEqual(result["equal_time_adjacent_quote_rows"], 1)
        high = (depth - 5) + (depth - 3) + 2 - 4
        self.assertEqual(result["ofi_path"], {"open": 0, "high": high, "low": -2, "close": high,
            "high_at_ns": base + 40, "low_at_ns": base + 10,
            "high_source_order": 3, "low_source_order": 2})
        self.assertEqual(result["ofi_contracts"], high)
        self.assertEqual(result["terminal_projection"]["t"], base + 40)
        self.assertEqual(result["terminal_projection"]["bid_size"], depth - 5)

    def test_malformed_inputs_are_rejected_on_ordinary_prepared_and_frozen_paths(self):
        good = make_quote_table([quote_row(10, source_order=0), quote_row(20, source_order=1)])
        missing = good.drop(["source_key"])
        null_clock = good.set_column(good.schema.get_field_index("t"), "t", pa.array([10, None], type=pa.int64()))
        known = good.set_column(good.schema.get_field_index("known_at_ns"), "known_at_ns", pa.array([1, 2], type=pa.int64()))
        crossed = make_quote_table([quote_row(10, source_order=0, bid=402, ask=401)])
        trusted_null = make_quote_table([quote_row(10, source_order=0, raw_action=None)])
        cases = ((IntegrityError, lambda window: window.add(missing)),
                 (IntegrityError, lambda window: window.add(null_clock)),
                 (IntegrityError, lambda window: window.add(known)),
                 (IntegrityError, lambda window: window.add(crossed)),
                 (IntegrityError, lambda window: window.add(trusted_null)),
                 (ContractError, lambda window: quote_window(type(window), maximum_events=1).add(good)))
        for Window in (QuoteWindow, frozen_quote_window()):
            for error, call in cases:
                with self.subTest(window=Window.__module__, error=error.__name__):
                    with self.assertRaises(error):
                        call(Window(instrument_id=1, start_ns=0, end_ns=100, latency_ns=250, maximum_events=100))
        with self.assertRaises(IntegrityError):
            prepare_quote_batch(missing)
        with self.assertRaises(IntegrityError):
            QuoteWindow(instrument_id=1, start_ns=0, end_ns=100, latency_ns=250).add_prepared(good)
        prepared = prepare_quote_batch(null_clock)
        with self.assertRaises(IntegrityError):
            QuoteWindow(instrument_id=1, start_ns=0, end_ns=100, latency_ns=250).add_prepared(prepared)
        prepared.release()
        with self.assertRaises(IntegrityError):
            QuoteWindow(instrument_id=1, start_ns=0, end_ns=100, latency_ns=250).add_prepared(prepared)
        window = QuoteWindow(instrument_id=1, start_ns=0, end_ns=100, latency_ns=250)
        window.add(good.slice(0, 1))
        with self.assertRaises(IntegrityError):
            window.add(good.slice(0, 1))
        window.finish(coverage_complete=True)
        with self.assertRaises(IntegrityError):
            window.add(good.slice(1))
        empty = good.slice(0, 0)
        QuoteWindow(instrument_id=1, start_ns=0, end_ns=100, latency_ns=250).add(empty)
        with prepare_quote_batch(empty) as batch:
            QuoteWindow(instrument_id=1, start_ns=0, end_ns=100, latency_ns=250).add_prepared(batch)
            self.assertEqual(list(batch.atomic_slices(start=0, width=20)), [])
        with prepare_quote_batch(good) as batch:
            QuoteWindow(instrument_id=1, start_ns=0, end_ns=100, latency_ns=250).add_prepared(batch, 0, 2)
        self.assertTrue(batch.released)
        self.assertEqual(batch.values, {})
        prefix = prepare_quote_batch(null_clock)
        accepted = QuoteWindow(instrument_id=1, start_ns=0, end_ns=100, latency_ns=250)
        accepted.add_prepared(prefix, 0, 1)
        self.assertEqual(accepted.previous["t"], 10)
        with self.assertRaises(IntegrityError) as later:
            accepted.add_prepared(prefix, 1, 2)
        self.assertEqual(str(later.exception), "required quote coordinate or clock is null")
        prefix.release()
        uncastable = good.set_column(good.schema.get_field_index("t"), "t", pa.array([None, None], type=pa.int64()))
        uncastable = uncastable.set_column(uncastable.schema.get_field_index("raw_action"), "raw_action",
                                          pa.array([["A"], ["M"]], type=pa.list_(pa.string())))
        with self.assertRaises(IntegrityError) as public:
            QuoteWindow(instrument_id=1, start_ns=0, end_ns=100, latency_ns=250).add(uncastable)
        self.assertEqual(str(public.exception), "required quote coordinate or clock is null")
        with prepare_quote_batch(good) as batch:
            window = QuoteWindow(instrument_id=1, start_ns=0, end_ns=100, latency_ns=250)
            for start, stop in ((0.5, 2), (True, 2), (-1, 2), (0, 3), (2, 0)):
                with self.subTest(start=start, stop=stop):
                    with self.assertRaises(IntegrityError):
                        window.add_prepared(batch, start, stop)

    def test_instrument_windows_consume_prepared_slices_against_frozen_reference(self):
        from trading_research.research.auction_flow_pipeline import InstrumentWindows

        _, all_rows = self.projected_tables(
            [raw(10, qb=9, qa=3), raw(25, qb=8, qa=4), raw(70, qb=3, qa=9), raw(90, qb=7, qa=5)])
        windows = InstrumentWindows(1, 0, 100, 30, 250, 100, 100, 20)
        windows.quote_rows(all_rows)
        count = (windows.end - windows.start + windows.width - 1) // windows.width
        while windows.current_quote_bin < count:
            current = windows.quotes[windows.current_quote_bin]
            windows.closed_quotes[windows.current_quote_bin] = current.finish(coverage_complete=False)
            windows.current_quote_bin += 1
            if windows.current_quote_bin < count:
                _, end = windows.bounds(windows.current_quote_bin)
                windows.quotes[windows.current_quote_bin] = current.continue_window(end_ns=end)
        frozen = replay_atomic([all_rows], Window=frozen_quote_window(), start=0, end=100, width=30, delay=250)
        ordinary = replay_atomic([all_rows], Window=QuoteWindow, start=0, end=100, width=30, delay=250)
        prepared = replay_atomic([all_rows], Window=QuoteWindow, start=0, end=100, width=30, delay=250, prepared=True)
        self.assertEqual(windows.closed_quotes, frozen)
        self.assertEqual(ordinary, frozen)
        self.assertEqual(prepared, frozen)
        self.assertEqual(windows.native.columns["quote_rows"].sum(), 4)
        self.assertEqual(int(windows.native.columns["quote_rows"].sum()),
                         int(sum(item["quote_or_invalidation_rows"] for item in frozen.values())))


if __name__ == "__main__":
    unittest.main()
