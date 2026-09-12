"""Adversarial freeze, identity and semantics checks for empirical rules."""
import copy
import unittest
import tempfile
import json
from pathlib import Path
from unittest.mock import patch

from trading_research.research.method_pack import empirical_registry as er


class EmpiricalRegistryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.draft = er.build_registry()

    def document(self, frozen=False):
        doc = copy.deepcopy(self.draft)
        if frozen: doc['freeze_status'] = 'frozen'
        doc['registry_sha256'] = er.canonical_hash(doc)
        return doc

    def candidate(self, doc):
        rule = next(r for r in doc['rules'] if r['supported'])
        value = {key:copy.deepcopy(rule[key]) for key in ('rule_id','method_id','branch','assumption_ids','variant','evidence_mode','faithful_eligible')}
        value.update(registry_version=doc['version'], registry_sha256=doc['registry_sha256'])
        return value

    def assert_registry_rejected(self, mutate):
        doc = self.document()
        mutate(doc)
        doc['registry_sha256'] = er.canonical_hash(doc)
        with self.assertRaises(ValueError): er.validate_registry(doc)

    def test_complete_inventory_and_native_transport(self):
        doc = er.validate_registry(self.document())
        self.assertEqual(len(doc['rules']),50)
        self.assertEqual(sum(r['supported'] for r in doc['rules']),19)
        self.assertEqual(len(doc['extra_observation_units']),8)
        by_key={(r['method_id'],r['branch']):r for r in doc['rules']}
        for key,unit in [(('JJ-TBR','internal_rotation'),'range_path'),(('KEANI-OPEN-ABOVE-VALUE','source_long'),'opening_period_state'),(('REFILL-STUDY','touch_record'),'zone_touch')]:
            self.assertEqual(by_key[key]['transport_observation_unit'],unit)
        saint=by_key[('SAINT-AMT','continuation_retest')]
        self.assertNotIn('native_executed_trades_with_aggressor',saint['required_data'])
        self.assertEqual(saint['parameters']['action_start'],'09:30')
        self.assertIn('immediately_preceding_weekday',saint['parameters']['prior_rth_policy'])

    def test_candidate_requires_frozen_registry(self):
        draft=self.document()
        candidate=self.candidate(draft)
        with self.assertRaises(ValueError): er.validate_comparison_candidate(candidate,draft)
        er.validate_comparison_candidate(candidate,draft,allow_draft=True)
        frozen=self.document(True)
        er.validate_comparison_candidate(self.candidate(frozen),frozen)
        with patch.object(er,'load_registry',return_value=draft):
            with self.assertRaises(ValueError): er.validate_comparison_candidate(candidate,allow_draft=True)

    def test_rehashed_mutations_cannot_redefine_version(self):
        mutations = {
            'unknown_algorithm':lambda d:d['rules'][0].update(algorithm='wins_only'),
            'foreign_branch':lambda d:d['rules'][0].update(branch='source_long'),
            'known_but_wrong_method':lambda d:d['rules'][0].update(method_id='GB-FAIL'),
            'bool_for_support':lambda d:d['rules'][0].update(supported=0),
            'parameters':lambda d:next(r for r in d['rules'] if r['supported'])['parameters'].update(confirmation_minutes=5),
            'bool_for_integer':lambda d:next(r for r in d['rules'] if r['supported'])['parameters'].update(confirmation_minutes=True),
            'source_page':lambda d:d['rules'][0].update(source_refs=['GB:999']),
            'source_key':lambda d:d['rules'][0].update(source_refs=['FAKE:1']),
            'recipe':lambda d:d['rules'][0].update(source_refs=['FORMULAS:O999']),
            'assumption_definition':lambda d:d['assumptions'][0].update(definition='Choose winning signals'),
            'assumption_parameters':lambda d:d['assumptions'][0]['parameters'].update(fake='x'),
            'extra_unit':lambda d:d['extra_observation_units'][0].update(status='supported'),
            'duplicate_branch':lambda d:d['rules'].__setitem__(1,copy.deepcopy(d['rules'][0])),
            'missing_branch':lambda d:d['rules'].pop(),
            'missing_unit':lambda d:d['extra_observation_units'].pop(),
            'changed_input_identity':lambda d:d['input_identities'].update({'planning/phase-1-live/FORMULAS.md':'0'*64}),
        }
        for label,mutation in mutations.items():
            with self.subTest(label=label): self.assert_registry_rejected(mutation)

    def test_candidate_cannot_escape_identity_or_claim_execution(self):
        doc=self.document(True)
        candidate=self.candidate(doc)
        mutations={'rule_id':'unknown','method_id':'GB-FAIL','branch':'not_this_branch','registry_version':'9','registry_sha256':'0'*64,'assumption_ids':[],'faithful_eligible':True,'variant':'source','evidence_mode':'source_fact','order_id':'invented','actual_fill':123,'actual_selection':True,'trading_return':1.2}
        for key,value in mutations.items():
            with self.subTest(key=key):
                changed=copy.deepcopy(candidate);changed[key]=value
                with self.assertRaises(ValueError):er.validate_comparison_candidate(changed,doc)
        changed=copy.deepcopy(candidate);changed['assumption_ids']*=2
        with self.assertRaises(ValueError):er.validate_comparison_candidate(changed,doc)

    def test_hash_covers_freeze_and_source_inputs(self):
        doc=self.document()
        doc['freeze_status']='frozen'
        with self.assertRaises(ValueError):er.validate_registry(doc)
        self.assertIn('implementation/src/trading_research/research/method_pack/source_cases_v2.json',doc['input_identities'])
        self.assertTrue(any('/wiki/' in path for path in doc['input_identities']))
        self.assertTrue(all(len(value)==64 for value in doc['input_identities'].values()))
        altered=copy.deepcopy(doc['input_identities']);altered['planning/phase-1-live/FORMULAS.md']='1'*64
        er._VALIDATED_REGISTRIES.clear()
        with patch.object(er,'input_identities',return_value=altered):
            with self.assertRaises(ValueError):er.validate_registry(self.document())

    def test_bounded_batch_uses_private_copy_and_defers_publication_until_exit(self):
        doc=self.document(True);candidate=self.candidate(doc)
        with er.validated_registry_batch(doc):
            with patch.object(er,'_definition_signature',side_effect=AssertionError('per-record stat forbidden')):
                returned=er.validate_comparison_candidate(candidate)
                returned['parameters']['tampered']=True
                self.assertNotIn('tampered',er.validate_comparison_candidate(candidate)['parameters'])
                doc['rules'][0]['status']='caller_mutated'
                er.validate_comparison_candidate(candidate)
        with self.assertRaises(ValueError):er.validate_comparison_candidate(candidate,doc)

    def test_batch_definition_mutation_aborts_before_publication(self):
        doc=self.document(True);candidate=self.candidate(doc);published=[]
        signature=er._definition_signature()
        with patch.object(er,'_definition_signature',return_value=signature) as signatures:
            with self.assertRaisesRegex(ValueError,'discard unpublished batch'):
                with er.validated_registry_batch(doc):
                    er.validate_comparison_candidate(candidate)
                    signatures.return_value=signature+(('changed',0,0,0,0,0),)
                published.append('accepted')
        self.assertEqual(published,[])
        self.assertIsNone(er._BATCH_REGISTRY.get())

    def test_mss_child_requires_entire_postparent_gap_sequence(self):
        rule=next(r for r in self.draft['rules'] if r['branch']=='mss_fvg_refinement')
        self.assertIs(rule['parameters']['all_three_candles_start_at_or_after_parent'],True)
        self.assertEqual(rule['parameters']['earliest_candle_start'],'ceil_parent_completion_to_2m_grid')
        self.assertEqual(rule['parameters']['child_occurrence'],'parent_completion_instant')
        def mutate(doc):
            next(r for r in doc['rules'] if r['branch']=='mss_fvg_refinement')['parameters']['all_three_candles_start_at_or_after_parent']=False
        self.assert_registry_rejected(mutate)

    def test_m09_pairing_and_batch_policies_are_frozen(self):
        rule=next(r for r in self.draft['rules'] if r['method_id']=='REFILL-STUDY' and r['supported'])
        p=rule['parameters']
        self.assertEqual(p['pairing'],'nonoverlapping_chronological_per_side_single_pending')
        self.assertEqual(p['pair_success'],'consume_both')
        self.assertEqual(p['pair_failure'],'replace_pending_with_current')
        self.assertEqual(p['formation_batch_policy'],'skip_all_same_side_qualifying_events_if_count_gt_1_log_ambiguity')
        self.assertEqual(p['outcome_clock'],'strictly_after_touch_timestamp_batch')
        self.assertEqual(p['rearm_clock'],'strictly_after_previous_touch_timestamp_batch')
        self.assertEqual(p['zone_expiry'],'16:00')
        self.assertEqual(p['simultaneous_opposing_endpoints'],'unknown')
        def mutation(doc):
            next(r for r in doc['rules'] if r['rule_id']==rule['rule_id'])['parameters']['pairing']='overlapping'
        self.assert_registry_rejected(mutation)

    def test_load_cache_is_isolated_and_rechecks_file_and_definition_drift(self):
        with tempfile.TemporaryDirectory() as directory:
            path=Path(directory)/'registry.json'
            doc=self.document(True)
            path.write_text(json.dumps(doc))
            loaded=er.load_registry(path)
            loaded['rules'][0]['status']='poisoned'
            with patch.object(er,'validate_registry',wraps=er.validate_registry) as validator:
                self.assertNotEqual(er.load_registry(path)['rules'][0]['status'],'poisoned')
                validator.assert_not_called()
            bad=copy.deepcopy(doc);bad['rules'][0]['status']='supported_comparison';bad['registry_sha256']=er.canonical_hash(bad)
            path.write_text(json.dumps(bad))
            with self.assertRaises(ValueError):er.load_registry(path)
            path.write_text(json.dumps(doc));er.load_registry(path)
            altered=copy.deepcopy(doc['input_identities']);altered['planning/phase-1-live/FORMULAS.md']='2'*64
            signature=er._definition_signature()+(('definition_changed',0,0,0,0,0),)
            with patch.object(er,'_definition_signature',return_value=signature), patch.object(er,'input_identities',return_value=altered):
                with self.assertRaises(ValueError):er.load_registry(path)

    def test_source_reference_validator_checks_real_catalog(self):
        for ref in ['GB:0','GB:999','NONE:1','FORMULAS:M99','FORMULAS:O999']:
            with self.subTest(ref=ref):
                doc=self.document();doc['rules'][0]['source_refs']=[ref]
                with self.assertRaises(ValueError):er._validate_source_refs(doc)
        er._validate_source_refs(self.document())

if __name__=='__main__': unittest.main()
