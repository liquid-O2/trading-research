"""F05.CROSS_VENDOR bounded multiplicity and evidence-specific uncertainty."""
from dataclasses import asdict, replace
import hashlib
from itertools import permutations
import json
from pathlib import Path
import unittest

from trading_research.data.transaction_matching import (MatchContract, MatchObservation, PairingProof,
                                                         reconcile_observations)
from trading_research.errors import ContractError, IntegrityError

GOLDEN = json.loads((Path(__file__).parent / 'golden/f05-transactions.json').read_text())


def observation(identity, *, schema='left-v1', **changes):
    return MatchObservation(**{**dict(id=identity, source_row_id='physical:'+identity,
        source_identity_evidence='verified-content-row', raw_hash=hashlib.sha256(identity.encode()).hexdigest(),
        schema_version=schema, instrument='SYNTH-1', event_start=10, event_end=11, known_at=12,
        price_key='exact:100', quantity=3, reported_side=1, condition='NORMAL',
        aggregation_unit='whole-print', quantity_unit='contracts', price_unit='synthetic-ticks',
        kind='trade', source_order=None), **changes})


def contract(**changes):
    return MatchContract(**{**dict(id='synthetic-matching-v1', left_schema='left-v1', right_schema='right-v1',
        instrument='SYNTH-1', quantity_unit='contracts', price_unit='synthetic-ticks', time_rule='exact_interval',
        primary='left', proofs=()), **changes})


class TransactionMatchingTests(unittest.TestCase):
    def test_two_identical_primary_prints_and_one_alternate_do_not_choose_identity(self):
        left = (observation('m1'), observation('m2'))
        right = (observation('s1',schema='right-v1'),)
        result = reconcile_observations(left,right,contract=contract())
        expected = next(c for c in GOLDEN['cases'] if c['id']=='F05-G17')['expected']
        self.assertEqual(result.candidate_edges,tuple(tuple(v) for v in expected['candidate_edges']))
        self.assertEqual(result.candidate_capacity,1)
        self.assertEqual(result.certified_pairs,())
        self.assertEqual(result.distinct_print_count_conditional_bounds,(2,3))
        self.assertEqual((result.primary_measurement_records,result.primary_measurement_volume),(2,6))
        self.assertEqual((result.components[0].left_ids,result.components[0].right_ids),(('m1','m2'),('s1',)))
        for ordering in permutations(left):
            self.assertEqual(reconcile_observations(ordering,right,contract=contract()),result)

    def test_proven_pair_keeps_other_identical_legitimate_print_and_versions_availability(self):
        left,right = (observation('m1'),observation('m2')),(observation('s1',schema='right-v1'),)
        before = reconcile_observations(left,right,contract=contract())
        proof = PairingProof('m2','s1','explicit-source-ownership-proof',30)
        after = reconcile_observations(left,right,contract=contract(proofs=(proof,)))
        self.assertEqual(after.certified_pairs,(('m2','s1'),))
        self.assertEqual(after.unmatched_left,('m1',))
        self.assertEqual(after.distinct_print_count_conditional_bounds,(2,2))
        self.assertEqual((before.input_known_at,after.input_known_at),(12,30))
        self.assertEqual((before.published, after.published), (False, False))
        self.assertNotIn('known_at', asdict(after))
        with self.assertRaises(ValueError):
            replace(after, published=True)
        self.assertEqual(before.certified_pairs,())
        self.assertNotEqual(before.id,after.id)
        for proofs in ((proof,proof),(PairingProof('m1','s1','other',30),proof),
                       (PairingProof('missing','s1','forged',30),)):
            with self.assertRaises(IntegrityError):
                reconcile_observations(left,right,contract=contract(proofs=proofs))

    def test_candidate_capacity_is_matching_cardinality_not_minimum_group_size(self):
        # l1/l2 overlap only r1; l3 overlaps all three. The component is connected,
        # but only two pairs can coexist. This forbids naive min(3,3) certainty.
        left = (observation('l1',event_start=0,event_end=1),observation('l2',event_start=0,event_end=1),
                observation('l3',event_start=0,event_end=3))
        right = (observation('r1',schema='right-v1',event_start=0,event_end=1),
                 observation('r2',schema='right-v1',event_start=1,event_end=2),
                 observation('r3',schema='right-v1',event_start=2,event_end=3))
        result = reconcile_observations(left,right,contract=contract(time_rule='overlapping_precision'))
        self.assertEqual((len(result.components),result.candidate_capacity),(1,2))
        self.assertEqual(result.distinct_print_count_conditional_bounds,(4,6))
        self.assertEqual(result.certified_pairs,())

    def test_acquisition_copy_is_idempotent_but_source_row_content_conflict_is_not(self):
        first,second = observation('m1'),observation('m2')
        copied = replace(first,id='m1-copy',known_at=20)
        result = reconcile_observations((first,second,copied),(),contract=contract())
        self.assertEqual((result.left_ids,result.primary_measurement_records,result.primary_measurement_volume),
                         (('m1','m2'),2,6))
        self.assertEqual((result.input_rows,result.duplicate_acquisition_rows),(3,1))
        self.assertEqual(result.input_known_at,20)
        with self.assertRaises(IntegrityError):
            reconcile_observations((first,replace(copied,quantity=4)),(),contract=contract())
        with self.assertRaises(IntegrityError):
            reconcile_observations((first,replace(first,raw_hash='0'*64)),(),contract=contract())

    def test_summary_volume_equality_does_not_create_record_parity(self):
        left = (observation('summary',quantity=5,aggregation_unit='provider-summary'),)
        right = (observation('p2',schema='right-v1',quantity=2),observation('p3',schema='right-v1',quantity=3))
        result = reconcile_observations(left,right,contract=contract())
        self.assertEqual((result.left_volume,result.right_volume,len(result.left_ids),len(result.right_ids)),(5,5,1,2))
        self.assertEqual(result.certified_pairs,())
        self.assertEqual(result.candidate_edges,())
        self.assertIsNone(result.distinct_print_count_conditional_bounds)
        self.assertEqual((result.left_record_count, result.right_record_count), (1, 2))
        self.assertTrue(any(category=='aggregation_mismatch' for category,_,_ in result.discrepancies))

    def test_unknown_sign_condition_missing_counterpart_and_snapshot_are_distinct(self):
        left = (observation('unknown',reported_side=None),
                observation('unknown-condition',condition=None,event_start=20,event_end=21),
                observation('snapshot',kind='snapshot',quantity=0),
                observation('unpriced',price_key=None))
        right = (observation('signed',schema='right-v1',reported_side=-1),)
        result = reconcile_observations(left,right,contract=contract())
        categories = {row[0] for row in result.discrepancies}
        self.assertTrue({'side_uncertainty','side_disagreement','condition_unknown','snapshot_state',
                         'unsupported_price','missing_counterpart'} <= categories)
        self.assertIsNone(result.distinct_print_count_conditional_bounds)
        self.assertEqual(result.primary_measurement_records,3)
        self.assertEqual(result.primary_measurement_volume,9)
        self.assertNotIn('snapshot',result.left_ids)
        self.assertEqual(result.candidate_edges,(('unknown','signed'),))
        self.assertEqual(result.certified_pairs,())
        self.assertNotIn('participant_identity',asdict(result))

    def test_schema_units_time_precision_and_missing_fields_cannot_be_invented(self):
        left,right = (observation('l'),),(observation('r',schema='right-v1',event_start=10,event_end=12),)
        exact = reconcile_observations(left,right,contract=contract())
        interval = reconcile_observations(left,right,contract=contract(time_rule='overlapping_precision'))
        self.assertEqual(exact.candidate_edges,())
        self.assertEqual(interval.candidate_edges,(('l','r'),))
        for bad in (replace(right[0],quantity_unit='shares'),replace(right[0],price_unit='USD'),
                    replace(right[0],instrument='SYNTH-2'),replace(right[0],schema_version='unknown')):
            with self.assertRaises(ContractError):
                reconcile_observations(left,(bad,),contract=contract())
        future = replace(right[0],event_start=11,event_end=12)
        self.assertEqual(reconcile_observations(left,(future,),contract=contract(time_rule='overlapping_precision')).candidate_edges,())

    def test_record_edge_bounds_and_primary_source_selection_are_explicit(self):
        left,right = (observation('m1'),observation('m2')),(observation('s1',schema='right-v1'),)
        exact = reconcile_observations(left,right,contract=contract(),max_rows=3,max_candidate_edges=2)
        self.assertEqual(len(exact.candidate_edges),2)
        with self.assertRaises(ContractError):
            reconcile_observations(left,right,contract=contract(),max_rows=2)
        with self.assertRaises(ContractError):
            reconcile_observations(left,right,contract=contract(),max_candidate_edges=1)
        alternate = reconcile_observations(left,right,contract=contract(primary='right'))
        self.assertEqual((alternate.primary_measurement_records,alternate.primary_measurement_volume),(1,3))
        self.assertEqual(alternate.candidate_edges,exact.candidate_edges)
        self.assertEqual(alternate.certified_pairs,())
        self.assertEqual(exact.pair_comparisons,2)
        self.assertNotEqual(alternate.id,exact.id)

    def test_missing_comparison_keys_do_not_prove_distinct_executions(self):
        for missing in ({'price_key': None}, {'condition': None}):
            with self.subTest(missing=missing):
                result = reconcile_observations((observation('l', **missing),),
                    (observation('r', schema='right-v1'),), contract=contract())
                self.assertEqual(result.candidate_edges, ())
                self.assertIsNone(result.distinct_print_count_conditional_bounds)
                self.assertEqual((result.left_record_count, result.right_record_count), (1, 1))
                self.assertFalse(result.published)
