"""F01_NATIVE_PROTOCOL: independent packed values and provider getter checks."""

from decimal import Decimal, localcontext
from dataclasses import replace
import io
from pathlib import Path
import random
import struct
import tempfile
import unittest

from trading_research.data.events import decode_fields
from trading_research.data.readers import native_mbp, native_records
from trading_research.errors import ContractError, DependencyUnavailable
from tests.test_market_data import SCENARIO


def definition_record(dbn, version):
    # Explicit values for the legacy schema, with shared fields also tested in v3.
    values = dict(publisher_id=1, instrument_id=42, ts_event=100, ts_recv=102,
                  min_price_increment=250_000_000, display_factor=1_000_000_000,
                  expiration=2**64-1, activation=77, high_limit_price=2**63-1,
                  low_limit_price=-1_250_000_000, max_price_variation=500_000_000,
                  trading_reference_price=123_500_000_000, unit_of_measure_qty=50_000_000_000,
                  min_price_increment_amount=2**63-1, price_ratio=1_000_000_000,
                  inst_attrib_value=7, underlying_id=41, raw_instrument_id=4_000_000_001,
                  market_depth_implied=10, market_depth=10, market_segment_id=12,
                  max_trade_vol=100, min_lot_size=1, min_lot_size_block=5,
                  min_lot_size_round_lot=1, min_trade_vol=1, contract_multiplier=2**31-1,
                  decay_quantity=0, original_contract_size=1, trading_reference_date=19000,
                  appl_id=2, maturity_year=2027, decay_start_date=0, channel_id=9,
                  currency="USD", settl_currency="USD", secsubtype="", raw_symbol="ESZ7 C8250",
                  group="ES", exchange="XCME", asset="ES", cfi="OCAXPS", security_type="OOF",
                  unit_of_measure="IPNT", underlying="ESZ7", strike_price_currency="USD",
                  instrument_class="C", strike_price=8_250_000_000_000, match_algorithm="F",
                  md_security_trading_status=17, main_fraction=0, price_display_format=2,
                  settl_price_type=1, sub_fraction=0, underlying_product=7,
                  security_update_action="A", maturity_month=12, maturity_day=17,
                  maturity_week=0, user_defined_instrument="N", contract_multiplier_unit=0,
                  flow_schedule_type=0, tick_rule=1, ts_out=111)
    if version == 3:
        for field in ("trading_reference_price", "trading_reference_date", "settl_price_type",
                      "md_security_trading_status"):
            values.pop(field)
        values.update(raw_instrument_id=2**40+9, leg_count=2, leg_index=1,
                      leg_instrument_id=43, leg_raw_symbol="ESZ7 P8250", leg_instrument_class="P",
                      leg_side="A", leg_price=-1_250_000_000, leg_delta=-500_000_000,
                      leg_ratio_price_numerator=-1, leg_ratio_price_denominator=1,
                      leg_ratio_qty_numerator=2, leg_ratio_qty_denominator=1, leg_underlying_id=41)
    for field, enum in (("instrument_class", dbn.InstrumentClass),
                        ("security_update_action", dbn.SecurityUpdateAction),
                        ("match_algorithm", dbn.MatchAlgorithm),
                        ("user_defined_instrument", dbn.UserDefinedInstrument),
                        ("leg_instrument_class", dbn.InstrumentClass), ("leg_side", dbn.Side)):
        if field in values:
            values[field] = enum(values[field])
    return getattr(dbn, f"v{version}").InstrumentDefMsg(**values)


class NativeFieldTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        import databento_dbn as dbn
        import pyarrow as pa
        cls.dbn, cls.pa = dbn, pa

    def read(self, records, *, version=3, schema="mbp-1", ts_out=False, **bounds):
        d = self.dbn
        metadata = d.Metadata(dataset="GLBX.MDP3", start=0, end=1000, limit=123,
                              stype_in=d.SType.RAW_SYMBOL, stype_out=d.SType.INSTRUMENT_ID,
                              schema=d.Schema(schema), symbols=["fixture"], partial=["missing-history"],
                              not_found=["absent"], ts_out=ts_out, version=version)
        payload = bytes(self.pa.compress(bytes(metadata)+b"".join(records), codec="zstd"))
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder)/"fixture.dbn.zst"
            path.write_bytes(payload)
            return list(native_records(path, data_root=path.parent, dataset_id="fixture",
                                       acquisition_version="v1", expected_schema=schema,
                                       expected_version=version, **bounds))

    def test_hand_packed_mbp_keeps_unknown_enum_bytes_all_fields_and_ts_out(self):
        header = struct.pack("<BBHIQ", 22, 1, 7, 42, 100)
        body = struct.pack("<qIccBBQiI", -1_250_000_000, 2, b"?", b"\xff", 132, 3, 102, -7, 2**32-1)
        bbo = struct.pack("<qqIIII", -1_500_000_000, -1_250_000_000, 4, 5, 6, 7)
        raw = header+body+bbo+struct.pack("<Q", 111)
        record = self.read([raw], ts_out=True)[1]
        self.assertEqual(record.raw_bytes, raw)
        expected = {"length": 22, "rtype": 1, "publisher_id": 7, "instrument_id": 42,
                    "ts_event": 100, "price": -1_250_000_000, "size": 2, "action": b"?",
                    "side": b"\xff", "flags": 132, "depth": 3, "ts_recv": 102,
                    "ts_in_delta": -7, "sequence": 2**32-1, "bid_px_00": -1_500_000_000,
                    "ask_px_00": -1_250_000_000, "bid_sz_00": 4, "ask_sz_00": 5,
                    "bid_ct_00": 6, "ask_ct_00": 7, "ts_out": 111}
        self.assertEqual(record.fields, expected)
        event = native_mbp(record, scenario=SCENARIO)
        self.assertIsNone(event.action)
        self.assertIsNone(event.reported_side)
        self.assertIn("unknown_action", event.quality_reasons)
        self.assertEqual(decode_fields(event.raw_fields)["side"], b"\xff")
        self.assertEqual(event.clocks.provider_received_at, 102)
        self.assertIsNone(event.clocks.received_at)

    def test_hand_packed_statistics_versions_keep_own_quantity_width_and_delete(self):
        from trading_research.data.native_fields import typed_native_fields, reassemble_native_fields
        for version in (1, 2, 3):
            maximum = 2**(63 if version == 3 else 31)-1
            for quantity in (0, maximum-1, maximum):
                with self.subTest(version=version, quantity=quantity):
                    size = 80 if version == 3 else 64
                    raw = struct.pack("<BBHIQ", size//4, 24, 1, 42, 100)
                    raw += struct.pack("<QQq", 102, 2**64-1, 2**63-1)
                    raw += struct.pack("<q" if version == 3 else "<i", quantity)
                    raw += struct.pack("<IiHHBB", 2**32-1, -7, 9, 3, 2, 17)
                    raw += bytes(range(18 if version == 3 else 6))
                    record = self.read([raw], version=version, schema="statistics")[1]
                    self.assertEqual(record.fields["quantity"], quantity)
                    self.assertEqual(record.fields["update_action"], 2)
                    self.assertEqual(record.fields["stat_flags"], 17)
                    self.assertEqual(record.fields["_reserved"], bytes(range(18 if version == 3 else 6)))
                    typed = typed_native_fields(record)
                    self.assertEqual(typed["quantity"], None if quantity == maximum else quantity)
                    self.assertIsNone(typed["price"])
                    self.assertIsNone(typed["ts_ref"])
                    self.assertEqual(typed["sequence"], 2**32-1)
                    self.assertEqual(reassemble_native_fields(record), raw)

    def test_hand_packed_ohlcv_keeps_unsigned_volume_and_exact_negative_prices(self):
        from trading_research.data.native_fields import typed_native_fields, reassemble_native_fields
        raw = struct.pack("<BBHIQqqqqQ", 14, 33, 1, 42, 100, -1_250_000_000,
                          250_000_001, -2_000_000_000, 0, 2**64-1)
        record = self.read([raw], schema="ohlcv-1m")[1]
        self.assertEqual(record.fields["volume"], 2**64-1)
        with localcontext() as ctx:
            ctx.prec = 3
            typed = typed_native_fields(record)
        self.assertEqual([typed[k] for k in ("open", "high", "low", "close")],
                         [Decimal("-1.25"), Decimal(".250000001"), Decimal("-2"), Decimal(0)])
        self.assertEqual(typed["volume"], 2**64-1)
        self.assertEqual(reassemble_native_fields(record), raw)

    def test_all_definition_layouts_preserve_getters_padding_terms_and_v3_legs(self):
        from trading_research.data.native_fields import typed_native_fields, reassemble_native_fields
        for version in (1, 2, 3):
            with self.subTest(version=version):
                original = definition_record(self.dbn, version)
                record = self.read([bytes(original)], version=version, schema="definition", ts_out=True)[1]
                physical = dict(type(original)._dtypes)
                self.assertEqual(set(record.fields), set(physical)|{"ts_out"})
                for key, dtype in physical.items():
                    if dtype[0] in "ui" and hasattr(original, key):
                        self.assertEqual(record.fields[key], int(getattr(original, key)), key)
                self.assertEqual(record.fields["raw_symbol"].split(b"\0", 1)[0], b"ESZ7 C8250")
                self.assertEqual(record.fields["contract_multiplier"], 2**31-1)
                typed = typed_native_fields(record)
                self.assertIsNone(typed["contract_multiplier"])
                self.assertIsNone(typed["expiration"])
                self.assertEqual(typed["min_price_increment"], Decimal(".25"))
                self.assertEqual(typed["unit_of_measure_qty"], Decimal(50))
                self.assertEqual(typed["strike_price"], Decimal(8250))
                if version == 3:
                    self.assertEqual(record.fields["raw_instrument_id"], 2**40+9)
                    self.assertEqual(typed["leg_price"], Decimal("-1.25"))
                    self.assertEqual(typed["leg_delta"], Decimal("-.5"))
                    self.assertEqual(record.fields["leg_ratio_qty_numerator"], 2)
                else:
                    self.assertEqual(record.fields["raw_instrument_id"], 4_000_000_001)
                    self.assertIn("trading_reference_date", record.fields)
                    self.assertNotIn("leg_price", record.fields)
                self.assertEqual(reassemble_native_fields(record), bytes(original))

    def test_all_metadata_attributes_retained_with_raw_bytes(self):
        metadata = self.read([], ts_out=True)[0]
        self.assertEqual(metadata.fields["start"], 0)
        self.assertEqual(metadata.fields["end"], 1000)
        self.assertEqual(metadata.fields["limit"], 123)
        self.assertEqual(metadata.fields["ts_out"], True)
        self.assertEqual(metadata.fields["symbols"], ["fixture"])
        self.assertEqual(metadata.fields["partial"], ["missing-history"])
        self.assertEqual(metadata.fields["not_found"], ["absent"])
        self.assertEqual(metadata.fields["mappings"], {})
        self.assertEqual(metadata.fields["symbol_cstr_len"], 71)
        self.assertEqual(self.dbn.Metadata.decode(metadata.raw_bytes).ts_out, True)

    def test_unregistered_layout_version_and_length_cannot_silently_decode(self):
        from trading_research.data.native_fields import decode_record_fields
        d = self.dbn
        record = d.StatMsgV1(publisher_id=1, instrument_id=42, ts_event=100, ts_recv=102,
                             ts_ref=90, price=2**63-1, quantity=1, stat_type=d.StatType.OPEN_INTEREST)
        for kind, version, raw, ts_out in (("StatMsgV1", 3, bytes(record), False),
                                          ("UnregisteredNewMsg", 1, bytes(record), False),
                                          ("StatMsgV1", 1, bytes(record)[:-1], False),
                                          ("StatMsgV1", 1, bytes(record), True)):
            with self.subTest(kind=kind, version=version, size=len(raw), ts_out=ts_out), self.assertRaises(ContractError):
                decode_record_fields(raw, kind=kind, dbn_version=version, ts_out=ts_out)

    def test_metadata_reserved_bytes_survive_without_provider_reencoding(self):
        d = self.dbn
        metadata = d.Metadata(dataset="GLBX.MDP3", start=1, stype_in=d.SType.RAW_SYMBOL,
                              stype_out=d.SType.INSTRUMENT_ID, schema=d.Schema.MBP_1, version=3)
        raw = bytearray(bytes(metadata))
        raw[56] = 191  # Inside v3's reserved metadata area, not a semantic field.
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder)/"metadata.dbn.zst"
            path.write_bytes(bytes(self.pa.compress(bytes(raw), codec="zstd")))
            records = list(native_records(path, data_root=path.parent, dataset_id="fixture", acquisition_version="v1"))
        self.assertEqual(records[0].fields["start"], 1)
        self.assertEqual(records[0].raw_bytes, bytes(raw))

    def test_changed_or_projected_native_fields_cannot_enter_canonical_consumer(self):
        d = self.dbn
        original = d.MBP1Msg(publisher_id=1, instrument_id=42, ts_event=100, ts_recv=102,
                             price=100_000_000_000, size=2, action=d.Action.TRADE, side=d.Side.BID, depth=0)
        record = self.read([bytes(original)])[1]
        for fields in ({**record.fields, "sequence": 999},
                       {k: v for k, v in record.fields.items() if k != "ts_in_delta"},
                       {**record.fields, "new_correction_field": 7}):
            with self.subTest(fields=list(fields)), self.assertRaises(ContractError):
                native_mbp(replace(record, fields=fields), scenario=SCENARIO)

    def test_native_raw_volume_diagnostic_still_compares_bytes_with_canonical_trades(self):
        from trading_research.data.audit import sample_partition
        from trading_research.data.native_audit import compare_prior_row
        from trading_research.errors import IntegrityError
        d = self.dbn
        metadata = d.Metadata(dataset="GLBX.MDP3", start=0, stype_in=d.SType.RAW_SYMBOL,
                              stype_out=d.SType.INSTRUMENT_ID, schema=d.Schema.MBP_1, version=3)
        trade = d.MBP1Msg(publisher_id=1, instrument_id=42, ts_event=100, ts_recv=102,
                          price=100_000_000_000, size=2, action=d.Action.TRADE, side=d.Side.BID, depth=0)
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder)/"fixture.dbn.zst"
            path.write_bytes(bytes(self.pa.compress(bytes(metadata)+bytes(trade)*2, codec="zstd")))
            result = sample_partition(data_root=path.parent, relative_path=path.name, dataset_id="fixture",
                                      max_rows=2, native=True)
        self.assertEqual(result["raw_trade_volume"], 4)
        self.assertEqual(result["observed_trade_volume"], 4)
        self.assertEqual(compare_prior_row({"quantity": 7, "update_action": 2},
                                          {"quantity": 7, "update_action": "<StatUpdateAction.DELETE: 2>"}), 2)
        with self.assertRaises(IntegrityError):
            compare_prior_row({"price": 99}, {"price": 100})
        with self.assertRaises(IntegrityError):
            compare_prior_row({"price": 100}, {"price": 100, "missing_correction": 7})

    def test_compressed_byte_budget_is_not_eof_for_incompressible_valid_records(self):
        rng = random.Random(612)
        rows = []
        for i in range(5000):
            # Valid fixed-width records with deterministic incompressible payload.
            rows.append(struct.pack("<BBHIQqIccBBQiI", 12, 0, 1, 42, rng.getrandbits(63),
                                    rng.getrandbits(62), rng.getrandbits(32), b"T", b"B", 0, 0,
                                    rng.getrandbits(63), 0, rng.getrandbits(32)))
        # A Zstd block may require >64 KiB of compressed input before yielding
        # its first output. This budget admits that first block, not the suffix.
        prefix = self.read(rows, schema="trades", max_records=2, max_compressed_bytes=131072)
        self.assertEqual(len(prefix), 3)
        with self.assertRaises(DependencyUnavailable):
            self.read(rows, schema="trades", max_records=5001, max_compressed_bytes=131072)


if __name__ == "__main__":
    unittest.main()
