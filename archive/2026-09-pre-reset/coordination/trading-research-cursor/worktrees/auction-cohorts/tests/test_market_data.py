from dataclasses import replace
from decimal import Decimal, localcontext
from pathlib import Path
import struct
import tempfile
import unittest

from trading_research.data.book import BookReducer, RecoveryCertificate
from trading_research.data.events import Flags, LatencyScenario, SourceAddress, decode_fields, encode_fields, normalize_mbp
from trading_research.data.readers import native_mbp, native_records, parquet_mbp
from trading_research.errors import ContractError, DependencyUnavailable


SCENARIO = LatencyScenario("synthetic-event-plus-2ns", "event", 2, 0)


def event(row, *, action="M", side="B", flags=128, at=None, bid=100.0, ask=100.25,
          bid_size=10, ask_size=10, size=1, price=100.0, instrument=1):
    address = SourceAddress("synthetic/mbp-1", "fixture-v1", "fixture.parquet", "fixture-content-v1",
                            "row_group:0", row, "quantpad11-v1")
    fields = {"t": row + 10 if at is None else at, "action": action, "side": side, "price": price,
              "size": size, "bid_px": bid, "ask_px": ask, "bid_sz": bid_size, "ask_sz": ask_size,
              "instrument_id": instrument, "flags": flags}
    return normalize_mbp(fields, address, native=False, scenario=SCENARIO)


class EventDecoderTests(unittest.TestCase):
    def test_native_nano_price_is_exact_even_in_low_precision_decimal_context(self):
        native = {"ts_event":10, "ts_recv":12, "action":"T", "side":"B", "price":20000250000000,
                  "size":1, "flags":0, "instrument_id":1, "bid_px_00":20000000000000, "ask_px_00":20000250000000,
                  "bid_sz_00":3, "ask_sz_00":4, "publisher_id":1, "sequence":1, "depth":0}
        with localcontext() as context:
            context.prec = 3
            decoded = normalize_mbp(native, event(0).address, native=True, scenario=SCENARIO)
        self.assertEqual(decoded.price, Decimal("20000.25"))
        self.assertEqual(decoded.quote.ask, Decimal("20000.25"))

    def test_lossless_all_columns_including_nan_sentinel_and_float_bits(self):
        fields = {"t": 123, "action": "T", "side": b"N", "flags": 168,
                  "negative_zero": -0.0, "nan_payload": struct.unpack(">d", bytes.fromhex("7ff8000000000042"))[0],
                  "extra_unknown_column": "retained", "missing": None}
        raw = encode_fields(fields)
        decoded = decode_fields(raw)
        self.assertEqual(raw, encode_fields(decoded))
        self.assertEqual(struct.pack(">d", decoded["nan_payload"]).hex(), "7ff8000000000042")
        self.assertEqual(decoded["extra_unknown_column"], "retained")
        self.assertEqual(decoded["side"], b"N")

    def test_trade_side_enum_flags_and_nontrade_resting_side(self):
        buy = event(0, action=ord("T"), side=ord("B"), flags=0, size=3)
        sell = event(1, action=b"T", side=b"A", flags=132, size=2)
        unknown = event(2, action="T", side="N", flags=2, size=4)
        resting = event(3, action="A", side="A", flags=128)
        self.assertEqual((buy.aggressor, sell.aggressor, unknown.aggressor, resting.aggressor), (1, -1, None, None))
        self.assertTrue(buy.trade_eligible)
        self.assertTrue(sell.trade_eligible)
        self.assertTrue(sell.flags & Flags.MAYBE_BAD_BOOK)
        self.assertTrue(sell.flags & Flags.LAST)
        self.assertIn("publisher_bit_requires_source_supplement", unknown.quality_reasons)
        self.assertNotIn("maybe_bad_book", unknown.quality_reasons)

    def test_missing_receipt_unknown_enums_and_off_tick_price_are_explicit(self):
        base = event(0, action="?", side="?", price=100.1)
        self.assertIsNone(base.action)
        self.assertIn("unknown_action", base.quality_reasons)
        self.assertIn("unknown_side_enum", base.quality_reasons)
        self.assertEqual(base.price, Decimal.from_float(100.1))
        self.assertIsNone(base.clocks.received_at)
        self.assertIsNone(base.provider_sequence)
        with self.assertRaises(ContractError):
            normalize_mbp(decode_fields(base.raw_fields), base.address, native=False, scenario=None)
        with self.assertRaises(ContractError):
            normalize_mbp(decode_fields(base.raw_fields), base.address, native=False,
                          scenario=LatencyScenario("wrong-field", "provider_received", 0, 0))


class BookProjectionTests(unittest.TestCase):
    def test_trade_quote_is_pretrade_and_size_is_not_depleted_twice(self):
        reducer = BookReducer()
        reducer.apply(event(0, ask_size=10))
        trade = reducer.apply(event(1, action="T", side="B", flags=0, ask_size=10, size=3))
        self.assertEqual(trade.pretrade_quote.ask_size, 10)
        self.assertEqual(trade.after.quote.ask_size, 10)
        update = reducer.apply(event(2, ask_size=7))
        self.assertEqual(update.ask_size_delta_at_same_price, -3)
        self.assertEqual(update.after.quote.ask_size, 7)
        self.assertEqual(update.after.total_volume, 3)
        # Standing BBO remains executable without requiring a subsequent quote event.
        self.assertEqual(reducer.standing(1, cut=16, max_age_ns=10).quote.ask_size, 7)

    def test_multiplicity_unknown_trade_volume_and_idempotent_ingestion(self):
        reducer = BookReducer()
        trades = [event(i, action="T", side=side, flags=0, at=10, size=2)
                  for i, side in enumerate(["B", "B", "A", "N"])]
        for t in trades:
            reducer.apply(t)
        state = reducer.states[1]
        self.assertEqual((state.total_volume, state.buy_volume, state.sell_volume, state.unknown_volume, state.trade_count),
                         (8, 4, 2, 2, 4))
        self.assertTrue(reducer.apply(trades[0]).duplicate)
        self.assertEqual(reducer.states[1].total_volume, 8)
        with self.assertRaises(ContractError):
            reducer.apply(event(0, action="T", side="B", flags=0, at=10, size=3))

    def test_bad_book_trades_retained_clean_quote_cannot_repair_and_flow_remains_incomplete(self):
        reducer = BookReducer()
        reducer.apply(event(0))
        gap = event(1, action="T", side="A", flags=132, size=4)
        reducer.apply(gap)
        reducer.apply(event(2))
        self.assertFalse(reducer.states[1].trusted)
        self.assertEqual(reducer.states[1].total_volume, 4)
        self.assertFalse(reducer.states[1].flow_complete)
        snapshot = event(3, flags=168)
        cert = RecoveryCertificate(1, gap.id, snapshot.id, "documented_full_snapshot", "synthetic-source-recovery-v1")
        reducer.apply(snapshot, recovery=cert)
        self.assertTrue(reducer.states[1].trusted)
        self.assertFalse(reducer.states[1].flow_complete)
        self.assertEqual(reducer.states[1].total_volume, 4)
        with self.assertRaises(ContractError):
            reducer.apply(snapshot, recovery=cert)

    def test_snapshots_and_clear_do_not_manufacture_fresh_pressure_or_quote_age(self):
        reducer = BookReducer()
        reducer.apply(event(0, flags=168))
        self.assertEqual(reducer.states[1].fresh_book_events, 0)
        self.assertIsNone(reducer.states[1].economic_quote_at)
        with self.assertRaises(DependencyUnavailable):
            reducer.standing(1, cut=12, max_age_ns=20)
        reducer.apply(event(1))
        before = reducer.states[1]
        reducer.apply(event(2, flags=168))
        self.assertEqual(reducer.states[1].economic_quote_at, before.economic_quote_at)
        self.assertEqual(reducer.states[1].fresh_book_events, before.fresh_book_events)
        reducer.apply(event(3, action="R"))
        self.assertFalse(reducer.states[1].trusted)
        self.assertIsNone(reducer.states[1].quote)

    def test_restart_suffix_equivalence_instrument_isolation_and_missing_book(self):
        prefix = [event(0), event(1, action="T", side="B", flags=0), event(2, ask_size=9)]
        suffix = [event(3, action="T", side="A", flags=132, size=2), event(4, instrument=2)]
        all_events = BookReducer()
        for e in prefix:
            all_events.apply(e)
        frozen = all_events.checkpoint()
        resumed = BookReducer.restore(frozen)
        for e in suffix:
            self.assertEqual(all_events.apply(e), resumed.apply(e))
        self.assertEqual(all_events.checkpoint(), resumed.checkpoint())
        self.assertTrue(BookReducer.restore(frozen).states[1].trusted)
        self.assertFalse(all_events.states[1].trusted)
        self.assertTrue(all_events.states[2].trusted)
        with self.assertRaises(ContractError):
            BookReducer.restore(frozen, decoder_version="different")
        crossed = BookReducer()
        crossed.apply(event(9, bid=101, ask=100))
        with self.assertRaises(DependencyUnavailable):
            crossed.standing(1, cut=21, max_age_ns=10)


class ReaderTests(unittest.TestCase):
    def test_parquet_stream_roundtrip_and_raw_row_addresses_across_batches(self):
        try:
            import pyarrow as pa
            import pyarrow.parquet as pq
        except ImportError:
            self.skipTest("optional pinned data reader dependencies not installed")
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "source.parquet"
            rows = [decode_fields(event(i, at=10).raw_fields) for i in range(6)]
            for row in rows:
                row["extra"] = "retain"
            pq.write_table(pa.Table.from_pylist(rows), path, row_group_size=3)
            values = list(parquet_mbp(path, data_root=Path(tmp), dataset_id="fixture", acquisition_version="v1",
                                      scenario=SCENARIO, max_rows=5, row_groups=(0, 1), batch_size=2))
            self.assertEqual(len(values), 5)
            self.assertEqual([(v.address.partition, v.address.row) for v in values],
                             [("row_group:0", 0), ("row_group:0", 1), ("row_group:0", 2), ("row_group:1", 0), ("row_group:1", 1)])
            self.assertEqual([decode_fields(v.raw_fields) for v in values], rows[:5])
            self.assertEqual(len({v.id for v in values}), 5)

    def test_native_record_bytes_and_ascii_enums_roundtrip(self):
        try:
            import databento_dbn as dbn
        except ImportError:
            self.skipTest("optional pinned DBN dependency not installed")
        from trading_research.data.readers import NativeRecord
        from trading_research.data.native_fields import decode_record_fields
        record = dbn.MBP1Msg(publisher_id=1, instrument_id=42, ts_event=10, price=100_000_000_000,
                             size=2, action=dbn.Action.TRADE, side=dbn.Side.BID, depth=0, ts_recv=12, flags=0,
                             sequence=5, levels=dbn.BidAskPair(99_750_000_000, 100_000_000_000, 4, 5, 1, 2))
        fields, layout_id = decode_record_fields(bytes(record), kind="MBP1Msg", dbn_version=3, ts_out=False)
        native = NativeRecord(event(0).address, "MBP1Msg", bytes(record), fields, 3, layout_id)
        decoded = native_mbp(native, scenario=LatencyScenario("native-plus-1", "provider_received", 1, 0))
        self.assertEqual(decoded.raw_record, bytes(record))
        self.assertEqual(decoded.aggressor, 1)
        self.assertEqual(decoded.quote.bid_count, 1)
        self.assertEqual(decoded.provider_sequence, 5)
        self.assertEqual(decoded.clocks.provider_received_at, 12)
        self.assertEqual(decoded.price, Decimal(100))
