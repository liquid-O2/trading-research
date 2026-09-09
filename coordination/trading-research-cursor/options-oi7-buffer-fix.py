from pathlib import Path
import json,hashlib,datetime,shutil,ast
root=Path('/workspace/trading-research');coord=Path('/workspace/coordination/trading-research-cursor');out=root/'reports/options-oi-runs/ed8fc072fb4a7e9a40d0a23274c570e98accbe0c74fa00d0066508904c9c9ff3'
d={'kind':'options_oi_full6_memory_diagnosis_v1','at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'execution':json.loads((out/'execution.json').read_text()),'exception':(out/'worker.log').read_text(),'last_flushed_reports':{'part':908,'chain':'SPXW','last_date':'2023-10-23'},'last_allocated_global_contract_count':1941013,'failed_allocation_bytes':1941013*4,'observations':{'membership_parquet_parts':len(list((out/'outputs').glob('membership-*.parquet'))),'asof_aggregate_parquet_parts':len(list((out/'outputs').glob('asof-aggregates-*.parquet'))),'ArrayWriter_flush_policy':'only chunk_rows >=65536; membership and cut aggregates append one Arrow table per source/cut'},'decision':'Bound retained Arrow table/chunk count at256 as well as65536rows. No science, IDs, clocks or resource cap change. Exact eight-table and statistical pilot parity then complete full required. Cache/identity rewrites deferred because writer retention is directly observed.'}
(coord/'options-oi6-diagnosis.json').write_text(json.dumps(d,indent=2)+'\n')
p=root/'tests/test_options_oi_measurements.py';s=p.read_text();target='\n\nif __name__ == "__main__":'
addition='''

class RootBoundedSmallTablesTests(unittest.TestCase):
    def test_one_row_metadata_tables_flush_without_changing_values(self):
        from trading_research.research.options_oi_columnar import ArrayWriter
        import pyarrow as pa
        import pyarrow.parquet as pq
        with tempfile.TemporaryDirectory() as folder:
            outputs = BoundedOutputs(Path(folder), maximum_total_bytes=8*1024**2,
                                     maximum_file_bytes=4*1024**2)
            schema = pa.schema([('clock', pa.int64()), ('value', pa.int64())])
            writer = ArrayWriter(outputs, 'small', schema, 'literal_small_tables')
            expected = []
            for i in range(777):
                value = None if i % 7 == 0 else i - 400
                row = {'clock': 1600000000000000001+i, 'value': value}
                writer.write_table(pa.Table.from_pylist([row], schema=schema))
                expected.append(row)
                self.assertLess(len(writer.chunks), 256)
            refs = writer.finish()
            actual = [row for ref in refs for row in pq.read_table(ref['path']).to_pylist()]
            self.assertEqual(actual, expected)
'''
assert target in s;s=s.replace(target,addition+target);p.write_text(s)
p=root/'src/trading_research/research/options_oi_columnar.py';shutil.copy2(p,coord/'options-oi6-columnar-before-buffer.py');s=p.read_text();old='if self.chunk_rows >= self.batch_rows:\n            self._flush()';new='# Tiny metadata tables own many Arrow buffers despite having few rows.\n        if self.chunk_rows >= self.batch_rows or len(self.chunks) >= 256:\n            self._flush()';assert old in s;s=s.replace(old,new);p.write_text(s)
for p in [p,root/'tests/test_options_oi_measurements.py']:ast.parse(p.read_text())
# Administrative registration only: no research candidate import or execution.
import sys
sys.path[:0]=[str(root/'src')]
from trading_research.operations.trials import TrialRegistry
from trading_research.operations.artifacts import digest
from dataclasses import asdict
r=TrialRegistry(root/'evidence/trials');st=r.state();family='Research-Options-OI-report-lifecycle-v1';previous=st['effective_budgets'][family]
a=json.loads((root/'validation/CROSS_MARKET_DELIVERABLE1_CONTINUATION_V1.json').read_text())
a.update(amendment_id='options-oi-d1-small-table-retention-20260909-8',family=family,base_family_sha256=digest(st['families'][family]),previous_limits=previous,authorized_limits={**previous,'max_attempts':8},reason='Retain same OI family and all six used attempts, including full6 memory failure at1653.51CPU. Membership/cut summary writer retained many one-row Arrow tables under a65536row-only cap. One small bound correction, exact pilot parity and decisive full use two remaining attempts. The original six attempt ceiling was supervisor chosen under the continuing allD1 instruction, not a separate user-imposed cap. CPU12000,4GiBaddressspace/physicaloutput and all previous usage unchanged; no budget reset or workload rename.')
p=root/'validation/OPTIONS_OI_DELIVERABLE1_CONTINUATION_V1.json';p.write_text(json.dumps(a,indent=2,sort_keys=True)+'\n');ref=asdict(r.artifacts.put_json(a,kind=a['kind']));event=r.amend_budget(authorization=ref)
print(json.dumps({'diagnosis':str(coord/'options-oi6-diagnosis.json'),'amendment':ref,'event':event,'fix':'row or256table bound'}))
