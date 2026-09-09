from collections import Counter
from dataclasses import replace
import json
from pathlib import Path
import tempfile
import unittest

from trading_research.data.cohorts import CohortEvidence, CohortRegistry
from trading_research.data.reconcile import compare_multisets, footer_index, read_window, select_groups, semantic_key
from trading_research.errors import ContractError, IntegrityError


class MultisetTests(unittest.TestCase):
    def test_equal_looking_legitimate_prints_count_twice_and_side_mismatches_are_visible(self):
        row = {"t":10,"instrument_id":1,"price":100.0,"size":2,"side":"B"}
        key = semantic_key(row)
        mbp = Counter({key:2})
        same = compare_multisets(mbp,Counter({key:2}))
        self.assertTrue(same["exact_multiset_match"])
        self.assertEqual((same["mbp_volume"],same["mbp_duplicate_economic_keys"]),(4,1))
        bad = compare_multisets(mbp,Counter({key:1,semantic_key({**row,"side":"A"}):1}))
        self.assertEqual((bad["extra_mbp_rows"],bad["extra_standalone_rows"],bad["side_mismatch_rows"]),(1,1,1))

    def test_full_schema_window_keeps_t_without_last_and_retains_gap_flags(self):
        try:
            import pyarrow as pa
            import pyarrow.parquet as pq
        except ImportError:
            self.skipTest("optional data dependency unavailable")
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            mbp_id, trades_id = "mbp", "trades"
            for id in (mbp_id,trades_id):
                (root/id).mkdir()
            rows = [{"t":10,"instrument_id":1,"price":100.0,"size":2,"side":"B","flags":0,"action":"T","extra_raw":"retained"},
                    {"t":10,"instrument_id":1,"price":100.0,"size":2,"side":"B","flags":132,"action":"T","extra_raw":"also retained"},
                    {"t":11,"instrument_id":1,"price":100.0,"size":999,"side":"N","flags":160,"action":"T","extra_raw":"snapshot"},
                    {"t":20,"instrument_id":1,"price":101.0,"size":5,"side":"A","flags":0,"action":"T","extra_raw":"next window"}]
            pq.write_table(pa.Table.from_pylist(rows),root/mbp_id/'part.parquet',row_group_size=2)
            standalone = [{k:v for k,v in r.items() if k not in {"action","extra_raw"}} for r in rows[:2]]
            pq.write_table(pa.Table.from_pylist(standalone),root/trades_id/'part.parquet')
            index = footer_index(root,datasets=(mbp_id,trades_id),max_files=2)
            a,b = [read_window(root,index,dataset=id,start=10,end=20,max_scan_rows=10) for id in (mbp_id,trades_id)]
            self.assertTrue(compare_multisets(a["counter"],b["counter"])["exact_multiset_match"])
            self.assertEqual((a["selected_rows"],a["trade_rows_without_last"],a["gap_flag_rows"],a["snapshot_trade_rows_excluded"]),(3,1,1,1))
            self.assertIn("extra_raw",index["datasets"][mbp_id][0]["fields"])
            old_hash = a["selected_all_field_arrow_stream_hash"]
            rows[0]["extra_raw"] = "raw nonprojection mutation"
            pq.write_table(pa.Table.from_pylist(rows),root/mbp_id/'part.parquet',row_group_size=2)
            with self.assertRaises(IntegrityError):
                read_window(root,index,dataset=mbp_id,start=10,end=20,max_scan_rows=10)
            new_index = footer_index(root,datasets=(mbp_id,trades_id),max_files=2)
            self.assertNotEqual(old_hash,read_window(root,new_index,dataset=mbp_id,start=10,end=20,max_scan_rows=10)["selected_all_field_arrow_stream_hash"])
            with self.assertRaises(ContractError):
                select_groups(new_index,dataset=mbp_id,start=10,end=20,max_scan_rows=1)


class ReadinessTests(unittest.TestCase):
    def test_inventory_complete_is_not_eligibility_and_certificate_scope_must_match(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d)
            catalog=root/'catalog.json';schemas=root/'schemas.json'
            catalog.write_text(json.dumps({"datasets":[{"dataset_id":"a","status":"complete"},{"dataset_id":"b","status":"complete"}]}))
            schemas.write_text(json.dumps({"a":{"fields":["price","size"]},"b":{"fields":["close"]}}))
            args=dict(catalog_path=catalog,schemas_path=schemas,expected_dataset_ids=frozenset({"a","b"}),prior_audit_references=())
            registry=CohortRegistry(root/'readiness',**args)
            self.assertTrue(all(v["eligibility"]=="unassessed" for v in registry.audit()["datasets"].values()))
            ref=registry.artifacts.put_json({"success":True,"certification":{"datasets":["a"],"cohort_id":"hour1","operations":["observed_trade_multiset"],"fields":["size"],"depth":"complete_window"}},kind="fixture_scope_evidence")
            record=CohortEvidence("e1","a","size","hour1","observed_trade_multiset","eligible","complete_window","raw-v1","def-v1","code-v1",10,20,None,ref,"exact observed-source comparison",("F05",),None)
            registry.append(record)
            registry.append(record)
            self.assertEqual(CohortRegistry(root/'readiness',**args).audit()["cohort_evidence_count"],1)
            with self.assertRaises(IntegrityError):
                registry.append(replace(record,id="wrong-field",field="price"))
            with self.assertRaises(ContractError):
                replace(record,id="prefix",depth="row_prefix")
            with self.assertRaises(ContractError):
                replace(record,id="receipt",operation="actual_live_receipt")
            with self.assertRaises(IntegrityError):
                CohortRegistry(root/'missing',**{**args,"expected_dataset_ids":frozenset({"a","b","missing"})})


if __name__ == "__main__":
    unittest.main()
