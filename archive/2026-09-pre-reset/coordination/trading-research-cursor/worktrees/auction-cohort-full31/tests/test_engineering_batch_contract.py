"""Exact-byte provenance and final resource boundaries for the shared batch."""
from dataclasses import asdict
import hashlib
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from tools import engineering_batch_contract as contract
from trading_research.operations.artifacts import ArtifactStore, ArtifactRef


class EngineeringBatchContractTests(unittest.TestCase):
    def test_final_resources_include_the_last_cpu_wall_and_rss_observation(self):
        config=dict(zip(('cpu_reservation_seconds','cpu_hard_seconds','address_space_bytes','wall_limit_seconds'),
                        (180,190,4*1024**3,240)))
        self.assertIsNone(contract.final_resource_error(179.99,239.99,4*1024**3-1,config))
        for cpu,wall,rss,word in ((180,20,1024,'CPU'),(180.01,20,1024,'CPU'),
                (1,240,1024,'wall'),(1,240.01,1024,'wall'),(1,20,4*1024**3,'RSS')):
            self.assertIn(word,contract.final_resource_error(cpu,wall,rss,config))
        for cpu,wall,rss in ((float('nan'),1,1),(1,float('inf'),1),(True,1,1),(1,1,1.0),(-1,1,1)):
            self.assertIsNotNone(contract.final_resource_error(cpu,wall,rss,config))
        self.assertIsNotNone(contract.final_resource_error(1,1,1,{**config,'cpu_hard_seconds':191}))

    def test_retention_uses_validated_bytes_and_checks_the_returned_reference(self):
        raw=b'reviewed input';captured={'reports/map.json':raw}
        identity={'path':'reports/map.json','sha256':hashlib.sha256(raw).hexdigest(),'size_bytes':len(raw)}
        with tempfile.TemporaryDirectory() as directory:
            store=ArtifactStore(Path(directory))
            retained=contract.retain_captured_inputs(store,captured,[identity])
            self.assertEqual(store.read(ArtifactRef(**retained[0]['artifact'])),raw)
            with self.assertRaises(ValueError):contract.retain_captured_inputs(store,{'reports/map.json':b'changed'},[identity])
            with patch.object(store,'put_bytes',return_value=ArtifactRef('0'*64,len(raw),'mapping_input')):
                with self.assertRaises(ValueError):contract.retain_captured_inputs(store,captured,[identity])

    def test_map_edit_during_normalization_cannot_substitute_retained_provenance(self):
        with tempfile.TemporaryDirectory() as directory,patch.object(contract,'ROOT',Path(directory)):
            root=Path(directory);store=ArtifactStore(root/'artifacts')
            def write(path,value):
                p=root/path;p.parent.mkdir(parents=True,exist_ok=True)
                p.write_bytes(value if type(value) is bytes else (json.dumps(value,sort_keys=True)+'\n').encode())
                return p.read_bytes()
            prep={'cases':[{'id':'C1'}],'clauses':[{'id':'S1'}]}
            prep_raw=write('reports/preparation.json',prep)
            prep_ref=store.put_bytes(prep_raw,kind='preparation')
            source=store.put_json({'preparation_bytes':asdict(prep_ref),'preparation':prep},kind='source_cases')
            golden=write('tests/golden.json',{'cases':[{'id':'C1'}]});protocol=write('protocols/example.md',b'Frozen test protocol.')
            registration={'source_cases':asdict(source),'golden':asdict(store.put_bytes(golden,kind='golden')),
                'protocol':asdict(store.put_bytes(protocol,kind='protocol')),'golden_path':'tests/golden.json','protocol_path':'protocols/example.md'}
            write('reports/registration.json',registration)
            assertion='tests.test_example.Example.test_case'
            raw_map={'test_modules':['tests.test_example'],'cases':[{'case_id':'C1','assertion_ids':[assertion],'remaining':['Economic validation.']}],
                'source_dispositions':[{'source_id':'S1','case_ids':['C1'],'assertion_ids':[assertion],
                    'covered_mechanism':'Exact primitive example.','whole_source_closed':False,'remaining':['Source scope.']}],
                'remaining':['Economic validation.']}
            original_map=write('reports/map.json',raw_map)
            write('tests/test_example.py',b'class Example:\n    def test_case(self):\n        pass\n')
            write('tools/map.py',b'# normalizer');write('tools/contract.py',b'# support')
            spec={'family':'example','test_modules':['tests.test_example'],'registration_path':'reports/registration.json',
                'preparation_path':'reports/preparation.json','case_map_path':'reports/map.json',
                'prepared_cases':{'key':'cases','id_key':'id'},'source_clauses':{'key':'clauses','id_key':'id'},
                'golden_collections':[{'key':'cases','id_key':'id'}],'golden_to_preparation':{'C1':['C1']},'extra_requirements':{}}
            batch={'tools':{'normalizer':'tools/map.py','contract_support':'tools/contract.py'}}
            batch_raw=write('reports/batch.json',batch)
            original=contract.case_contract
            def changed_after_capture(*args,**kwargs):
                value=original(*args,**kwargs)
                write('reports/map.json',{**raw_map,'remaining':['Changed after capture.']})
                return value
            with patch.object(contract,'case_contract',side_effect=changed_after_capture):
                mapped=contract.normalize_coverage(store,registration,spec,batch,'reports/batch.json',batch_raw)
            item=next(v for v in mapped['inputs'] if v['path']=='reports/map.json')
            self.assertEqual(item['sha256'],hashlib.sha256(original_map).hexdigest())
            self.assertEqual(mapped['remaining'],['Economic validation.'])
            with self.assertRaisesRegex(ValueError,'bytes changed'):
                contract.retain_mapping_inputs(store,mapped,registration,spec,batch,'reports/batch.json',batch_raw)


if __name__=='__main__':unittest.main()
