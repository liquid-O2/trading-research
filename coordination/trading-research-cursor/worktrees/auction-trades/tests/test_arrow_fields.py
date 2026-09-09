"""F01_ARROW_PROTOCOL: golden physical types, not domain-eligibility claims."""

import json
from pathlib import Path
import struct
import tempfile
import unittest

from trading_research.data.events import decode_fields
from trading_research.data.readers import parquet_mbp
from trading_research.errors import ContractError, DependencyUnavailable, IntegrityError
from tests.test_market_data import SCENARIO, event


class ArrowFieldTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        import pyarrow as pa
        import pyarrow.parquet as pq
        cls.pa, cls.pq = pa, pq

    def read(self, path, schema, **kwargs):
        from trading_research.data.arrow_fields import parquet_raw_rows
        return list(parquet_raw_rows(path, data_root=path.parent, dataset_id="fixture",
                                     acquisition_version="v1", expected_schema=schema, **kwargs))

    def test_long_schema_metadata_has_exact_identity_beyond_display_truncation(self):
        table = self.pa.Table.from_pylist([decode_fields(event(0).raw_fields)])
        schemas = [table.schema.with_metadata({b"long": b"x"*120+tail}) for tail in (b"1",b"2")]
        self.assertEqual(str(schemas[0]), str(schemas[1]))  # Deliberate collision in display output.
        with tempfile.TemporaryDirectory() as folder:
            outputs = []
            for i, schema in enumerate(schemas):
                path = Path(folder)/f"{i}.parquet"
                self.pq.write_table(table.cast(schema), path)
                outputs.append(list(parquet_mbp(path, data_root=path.parent, dataset_id="fixture",
                                                acquisition_version="v1", scenario=SCENARIO))[0])
        self.assertNotEqual(outputs[0].address.schema_version, outputs[1].address.schema_version)

    def test_nanosecond_dates_nulls_and_timezone_survive_without_datetime_conversion(self):
        pa = self.pa
        schema = pa.schema([pa.field("event", pa.timestamp("ns",tz="UTC")),
                            pa.field("day", pa.date32()), pa.field("us",pa.timestamp("us",tz="UTC")),
                            pa.field("text",pa.large_string()),pa.field("flag",pa.bool_()),pa.field("absent",pa.null())],
                           metadata={b"time_basis":b"physical-only-not-strategy-receipt"})
        table = pa.Table.from_arrays([pa.array([1_234_567_891,None,0],type=schema.field("event").type),
                                      pa.array([-1,None,0],type=pa.date32()),
                                      pa.array([1_234_567,None,0],type=schema.field("us").type),
                                      pa.array(["β?",None,""],type=pa.large_string()),
                                      pa.array([True,None,False]),pa.nulls(3)],schema=schema)
        with tempfile.TemporaryDirectory() as folder:
            path=Path(folder)/"time.parquet"; self.pq.write_table(table,path,version="2.6")
            rows=self.read(path,schema,max_rows=3)
        self.assertEqual(rows[0].values()["event"],{"type":"timestamp[ns, tz=UTC]","value":1_234_567_891})
        self.assertEqual(rows[0].values()["day"],{"type":"date32[day]","value":-1})
        self.assertEqual(rows[0].values()["us"]["value"],1_234_567)
        self.assertEqual(rows[0].values()["text"]["value"],"β?")
        self.assertTrue(all(v["value"] is None for v in rows[1].values().values()))
        self.assertEqual(rows[2].values()["event"]["value"],0)
        self.assertEqual(rows[2].values()["text"]["value"],"")
        self.assertEqual(rows[2].values()["flag"]["value"],False)
        for i,row in enumerate(rows):
            batch=row.checked_batch()
            self.assertTrue(batch.schema.equals(schema,check_metadata=True))
            self.assertEqual(batch.column(0)[0].value,table.column(0)[i].value)

    def test_float_bits_keep_negative_zero_infinity_and_two_nan_payloads(self):
        pa=self.pa
        words=[0x8000000000000000,0,0x7ff0000000000000,0xfff0000000000000,0x7ff8000000000001,0x7ff8000000000012]
        data=b"".join(struct.pack("<Q",w) for w in words)
        arr=pa.Array.from_buffers(pa.float64(),len(words),[None,pa.py_buffer(data)])
        table=pa.Table.from_arrays([arr],names=["raw_price"])
        with tempfile.TemporaryDirectory() as folder:
            path=Path(folder)/"bits.parquet"; self.pq.write_table(table,path,use_dictionary=False)
            rows=self.read(path,table.schema,max_rows=len(words),batch_size=2)
        self.assertEqual([r.values()["raw_price"]["value"]["bits_le"] for r in rows],
                         [struct.pack("<Q",w).hex() for w in words])
        self.assertEqual(len({r.content_hash for r in rows}),len(words))

    def test_all_22_catalogued_field_type_profiles_preserve_golden_columns(self):
        pa=self.pa
        profiles=json.loads((Path(__file__).parent/"fixtures/arrow-profiles.json").read_text())["profiles"]
        self.assertEqual(len(profiles),22)
        simple={"int8":pa.int8(),"int16":pa.int16(),"int32":pa.int32(),"int64":pa.int64(),
                "uint32":pa.uint32(),"double":pa.float64(),"bool":pa.bool_(),"null":pa.null(),
                "string":pa.string(),"large_string":pa.large_string(),"date32[day]":pa.date32(),
                "timestamp[ns, tz=UTC]":pa.timestamp("ns",tz="UTC"),"timestamp[us, tz=UTC]":pa.timestamp("us",tz="UTC"),
                "dictionary<values=string, indices=uint32, ordered=0>":pa.dictionary(pa.uint32(),pa.string()),
                "dictionary<values=string, indices=int8, ordered=0>":pa.dictionary(pa.int8(),pa.string())}
        with tempfile.TemporaryDirectory() as folder:
            for profile_id,profile in profiles.items():
                with self.subTest(profile=profile_id,dataset=profile["datasets"][0]):
                    fields=[pa.field(f["name"],simple[f["type"]],nullable=f["nullable"]) for f in profile["fields"]]
                    schema=pa.schema(fields);arrays=[];expected={}
                    for field in fields:
                        t=field.type
                        if pa.types.is_dictionary(t):
                            array=pa.DictionaryArray.from_arrays(pa.array([1,0],type=t.index_type),pa.array(["T","?"],type=t.value_type)); value="?"
                        else:
                            if pa.types.is_timestamp(t):value=1_234_567_891 if t.unit=="ns" else 1_234_567
                            elif pa.types.is_date(t):value=-1
                            elif pa.types.is_floating(t):value=-1.25
                            elif pa.types.is_boolean(t):value=True
                            elif pa.types.is_null(t):value=None
                            elif pa.types.is_integer(t):value=(2**(t.bit_width-(0 if pa.types.is_unsigned_integer(t) else 1))-2)
                            else:value="β?"
                            array=pa.array([value,value],type=t)
                        arrays.append(array)
                        expected[field.name]={"type":str(t),"value":{"bits_le":struct.pack("<d",value).hex()} if pa.types.is_floating(t) else value}
                    table=pa.Table.from_arrays(arrays,schema=schema);path=Path(folder)/(profile_id+".parquet")
                    self.pq.write_table(table,path,version="2.6",row_group_size=1)
                    rows=self.read(path,schema,max_rows=2,row_groups=(0,1),batch_size=1)
                    self.assertEqual(rows[0].values(),expected)
                    self.assertEqual(list(rows[0].values()),schema.names)
                    self.assertTrue(rows[0].checked_batch().schema.equals(schema,check_metadata=True))
                    self.assertNotEqual(rows[0].id,rows[1].id)

    def test_row_group_batch_bound_and_declared_schema_preserve_correction_fields(self):
        pa=self.pa
        table=pa.table({"t":pa.array([1,2,2,4,5],type=pa.int64()),"correction":pa.array([7,7,8,7,9],type=pa.int16()),
                        "side":pa.DictionaryArray.from_arrays(pa.array([0,1,1,0,1],type=pa.int8()),pa.array(["B","?"]))})
        with tempfile.TemporaryDirectory() as folder:
            path=Path(folder)/"rows.parquet";self.pq.write_table(table,path,row_group_size=3)
            by_batch=[self.read(path,table.schema,max_rows=4,row_groups=(0,1),batch_size=n) for n in (1,2,4)]
            for rows in by_batch:
                self.assertEqual([(r.address.partition,r.address.row) for r in rows],[("row_group:0",0),("row_group:0",1),("row_group:0",2),("row_group:1",0)])
            self.assertEqual([[r.id for r in rows] for rows in by_batch],[[r.id for r in by_batch[0]]]*3)
            self.assertEqual(by_batch[0][2].values()["correction"]["value"],8)
            with self.assertRaises(ContractError):self.read(path,table.drop(["correction"]).schema)
            with self.assertRaises(DependencyUnavailable):self.read(path,table.schema,max_output_bytes=1)
            path.write_bytes(path.read_bytes()[:-6])
            with self.assertRaises(IntegrityError):self.read(path,table.schema)

    def test_unregistered_type_or_altered_bundle_fails_before_use(self):
        from dataclasses import replace
        pa=self.pa
        with tempfile.TemporaryDirectory() as folder:
            path=Path(folder)/"nested.parquet"
            table=pa.table({"unregistered":pa.array([[1,2]],type=pa.list_(pa.int64()))})
            self.pq.write_table(table,path)
            with self.assertRaises(ContractError):self.read(path,table.schema)
            table=pa.table({"x":pa.array([7],type=pa.int64())});self.pq.write_table(table,path)
            row=self.read(path,table.schema)[0]
            with self.assertRaises(ContractError):replace(row,raw_fields=b'[]').checked_batch()

    def test_prior_audit_comparison_preserves_submicrosecond_and_all_field_requirements(self):
        from trading_research.data.arrow_audit import compare_prior_values
        current={"ts_quote":{"type":"timestamp[ns, tz=UTC]","value":1_234_567_891},
                 "day":{"type":"date32[day]","value":-1},
                 "price":{"type":"double","value":{"bits_le":struct.pack("<d",-1.25).hex()}}}
        expected={"ts_quote":"1970-01-01 00:00:01.234567891+00:00","day":"1969-12-31","price":-1.25}
        self.assertEqual(compare_prior_values(current,expected),3)
        with self.assertRaises(IntegrityError):compare_prior_values(current,{**expected,"ts_quote":"1970-01-01 00:00:01.234567890+00:00"})
        with self.assertRaises(IntegrityError):compare_prior_values(current,{k:v for k,v in expected.items() if k!="price"})


if __name__=="__main__":unittest.main()
