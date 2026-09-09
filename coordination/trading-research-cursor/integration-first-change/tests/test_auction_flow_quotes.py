from fractions import Fraction
from pathlib import Path
import tempfile
import unittest

import pyarrow as pa
import pyarrow.parquet as pq

from trading_research.data.book import BookReducer
from trading_research.data.events import Flags, LatencyScenario, SourceAddress, normalize_mbp
from trading_research.data.reconcile import footer_index
from trading_research.errors import IntegrityError
from trading_research.measurements.quotes import transition_metrics
from trading_research.research.auction_flow_data import AuctionFlowStream, RAW_FIELDS
from trading_research.research.auction_flow_quotes import QuoteWindow


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


if __name__ == "__main__":
    unittest.main()
