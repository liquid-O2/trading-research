"""Frozen F04 synthetic availability-merge assertions; no market inputs."""
from dataclasses import replace
from itertools import permutations
import json
from pathlib import Path
import sqlite3
from tempfile import TemporaryDirectory
import unittest

from references.replay_literal import batches as literal_batches
from trading_research.errors import ContractError, IntegrityError
from trading_research.foundations.time import AvailabilityBasis, Clocks
from trading_research.runtime.merge import PartitionMerge, ReplayBatch, ReplayEvent


class ReplayMergeTests(unittest.TestCase):
    def setUp(self):
        self.temporary = TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.domains = {'core': frozenset({'A', 'B'})}
        self.golden = json.loads((Path(__file__).parent / 'golden/f04-replay.json').read_text())['merge']
        self.events = (self.event('a0', 'A', 0, 10), self.event('b0', 'B', 0, 10),
                       self.event('a1', 'A', 1, 20))

    @staticmethod
    def event(identity, partition, sequence, known, *, origin=None, payload=b'value'):
        return ReplayEvent(identity, partition, sequence,
                           Clocks(known if origin is None else origin, known, 'synthetic-v1',
                                  AvailabilityBasis.RECEIVED, received_at=known), payload,
                           frozenset({'price'}))

    def merge(self, name='merge', *, domains=None, **limits):
        return PartitionMerge(self.root / (name + '.sqlite'), self.domains if domains is None else domains,
                              **limits)

    @staticmethod
    def seal(merge, before=30, known=None):
        for partition in sorted(merge.partitions):
            merge.advance(partition, before=before, known_at=before if known is None else known,
                          evidence_id=f'{partition}-watermark-{before}')

    @staticmethod
    def drain(merge, at=30, domain='core'):
        result = []
        while (batch := merge.peek(domain, at=at)) is not None:
            result.append(batch)
            merge.acknowledge(batch, at=at)
        return tuple(result)

    def test_golden_ties_and_registered_opposite_order_scenarios(self):
        merge = self.merge()
        for event in reversed(self.events):
            merge.append(event)
        self.seal(merge)
        actual = self.drain(merge)
        self.assertEqual([[e.id for e in b.events] for b in actual], self.golden['batches'])
        self.assertEqual([b.known_at for b in actual], self.golden['known_at'])
        self.assertEqual([b.ambiguous for b in actual], self.golden['ambiguous'])
        self.assertEqual(actual, literal_batches(self.events, domain='core', contract_version=merge.version,
                                                partitions=frozenset({'A', 'B'}), before=30))
        tie = actual[0]
        with self.assertRaises(ContractError):
            tie.ordered()
        for priority in (('A',), ('A', 'B', 'B'), ('A', 'C')):
            with self.subTest(priority=priority), self.assertRaises(ContractError):
                tie.ordered(partition_priority=priority)
        outcomes = []
        for priority in (('A', 'B'), ('B', 'A')):
            value = 1
            for event in tie.ordered(partition_priority=priority):
                value = value + 1 if event.partition == 'A' else value * 2
            outcomes.append(value)
        self.assertEqual(outcomes, [4, 3])
        self.assertEqual(actual[1].ordered(), (self.events[2],))

    def test_equal_watermark_is_exclusive_and_receipt_is_causal(self):
        merge = self.merge()
        merge.append(self.events[0])
        self.assertIsNone(merge.peek('core', at=100))
        merge.advance('A', before=11, known_at=11, evidence_id='a11')
        self.assertIsNone(merge.peek('core', at=100))
        merge.advance('B', before=10, known_at=10, evidence_id='b10')
        self.assertIsNone(merge.peek('core', at=100))
        merge.advance('B', before=11, known_at=15, evidence_id='b11')
        self.assertIsNone(merge.peek('core', at=14))
        self.assertEqual(tuple(e.id for e in merge.peek('core', at=15).events), ('a0',))

    def test_insertion_permutations_and_future_suffix_deletion_preserve_prefix_hashes(self):
        expected = None
        future = self.event('future', 'B', 1, 100)
        for index, ordering in enumerate(permutations(self.events)):
            for suffix in ((), (future,)):
                with self.subTest(order=tuple(e.id for e in ordering), future=bool(suffix)):
                    merge = self.merge(f'permutation-{index}-{len(suffix)}')
                    for event in suffix + ordering:
                        merge.append(event)
                    self.seal(merge)
                    result = self.drain(merge)
                    self.assertEqual([[e.id for e in b.events] for b in result], [['a0', 'b0'], ['a1']])
                    hashes = tuple(b.id for b in result)
                    if expected is None:
                        expected = hashes
                    self.assertEqual(hashes, expected)

    def test_correction_uses_actual_new_receipt_and_late_rejection_is_atomic(self):
        merge = self.merge(domains={'core': frozenset({'A'})})
        merge.append(self.events[0])
        self.seal(merge, before=11)
        original = merge.peek('core', at=11)
        before = merge.metrics()
        with self.assertRaises(ContractError):
            merge.append(self.event('late', 'A', 1, 10, payload=b'correction'))
        self.assertEqual(merge.metrics(), before)
        correction = self.event('corrected', 'A', 1, 20, origin=10, payload=b'correction')
        merge.append(correction)
        self.assertEqual(merge.peek('core', at=11), original)
        merge.acknowledge(original, at=11)
        self.assertIsNone(merge.peek('core', at=20))
        self.seal(merge, before=21)
        revised = merge.peek('core', at=21)
        self.assertEqual((revised.known_at, revised.events[0].clocks.event_at, revised.events[0].id),
                         (20, 10, 'corrected'))

    def test_stalled_options_does_not_block_trade_domain_or_share_ack_cursor(self):
        merge = self.merge(domains={'trade': frozenset({'T'}), 'options': frozenset({'T', 'O'})})
        trade = self.event('trade0', 'T', 0, 10)
        option = self.event('option0', 'O', 0, 10)
        merge.append(trade)
        merge.append(option)
        merge.advance('T', before=11, known_at=11, evidence_id='trade-live')
        self.assertIsNone(merge.peek('options', at=50))
        batch = merge.peek('trade', at=11)
        self.assertEqual(batch.events, (trade,))
        merge.acknowledge(batch, at=11)
        merge.advance('O', before=11, known_at=50, evidence_id='options-recovered')
        self.assertIsNone(merge.peek('options', at=49))
        self.assertEqual(tuple(e.id for e in merge.peek('options', at=50).events), ('option0', 'trade0'))
        self.assertIsNone(merge.peek('trade', at=50))

    def test_duplicate_event_idempotence_and_id_and_source_sequence_conflicts(self):
        merge = self.merge()
        event = self.events[0]
        self.assertTrue(merge.append(event))
        self.seal(merge)
        metrics = merge.metrics()
        self.assertFalse(merge.append(event))  # Even after its availability was sealed.
        with self.assertRaises(IntegrityError):
            merge.append(replace(event, payload=b'changed'))
        # A current-availability alias still cannot reuse the old source sequence.
        with self.assertRaises(IntegrityError):
            merge.append(self.event('alias', 'A', 0, 30))
        self.assertEqual(merge.metrics(), metrics)
        for invalid in ((event, replace(event, payload=b'changed')),
                        (event, self.event('alias', 'A', 0, 30))):
            with self.assertRaises(IntegrityError):
                literal_batches(invalid, domain='core', contract_version=merge.version,
                                partitions=merge.partitions, before=40)
        reopened = self.merge()
        self.assertFalse(reopened.append(event))
        self.assertEqual(reopened.metrics(), metrics)

    def test_watermark_evidence_duplicates_conflicts_and_regression_are_atomic(self):
        merge = self.merge()
        merge.advance('A', before=10, known_at=12, evidence_id='proof')
        metrics = merge.metrics()
        self.assertFalse(merge.advance('A', before=10, known_at=12, evidence_id='proof'))
        with self.assertRaises(IntegrityError):
            merge.advance('A', before=11, known_at=12, evidence_id='proof')
        for before, known in ((9, 13), (11, 11), (20, 19)):
            with self.subTest(before=before, known=known), self.assertRaises(ContractError):
                merge.advance('A', before=before, known_at=known, evidence_id='invalid')
        self.assertEqual(merge.metrics(), metrics)

    def test_record_bound_counts_watermarks_and_acknowledged_history(self):
        merge = self.merge(domains={'core': frozenset({'A'})}, max_records=3)
        merge.append(self.events[0])
        self.seal(merge, before=11)
        batch = merge.peek('core', at=11)
        merge.acknowledge(batch, at=11)
        self.assertEqual(merge.metrics()['retained_records'], 3)
        before = merge.metrics()
        with self.assertRaises(ContractError):
            merge.append(self.events[2])
        self.assertEqual(merge.metrics(), before)
        self.assertFalse(merge.append(self.events[0]))
        self.assertFalse(merge.acknowledge(batch, at=11))
        with sqlite3.connect(merge.path) as con:
            self.assertEqual(con.execute('SELECT COUNT(*) FROM events').fetchone()[0], 1)
            self.assertEqual(con.execute('SELECT COUNT(*) FROM acks').fetchone()[0], 1)
        self.assertEqual(self.merge(domains={'core': frozenset({'A'})}, max_records=3).metrics(), before)

    def test_byte_bound_exact_fit_and_failed_ack_leave_next_batch_intact(self):
        # Derive envelope lengths with stdlib JSON, independently of runtime canonical_json.
        event = self.events[0]
        event_size = len(json.dumps(event.record(), sort_keys=True, ensure_ascii=False,
                                    separators=(',', ':')).encode())
        watermark_size = len(b'["A",11,11,"A-watermark-11"]')
        merge = self.merge(domains={'core': frozenset({'A'})}, max_bytes=event_size + watermark_size)
        merge.append(event)
        self.seal(merge, before=11)
        metrics = merge.metrics()
        self.assertEqual(metrics['retained_envelope_bytes'], event_size + watermark_size)
        batch = merge.peek('core', at=11)
        with self.assertRaises(ContractError):
            merge.acknowledge(batch, at=11)
        with self.assertRaises(ContractError):
            merge.append(self.events[2])
        self.assertEqual(merge.metrics(), metrics)
        self.assertEqual(merge.peek('core', at=11), batch)
        with sqlite3.connect(merge.path) as con:
            self.assertEqual(con.execute('SELECT COUNT(*) FROM acks').fetchone()[0], 0)

    def test_oversized_tie_is_never_split_or_consumed(self):
        merge = self.merge(max_batch=1)
        for event in self.events:
            merge.append(event)
        self.seal(merge)
        before = merge.metrics()
        for instance in (merge, self.merge(max_batch=1)):
            with self.assertRaisesRegex(ContractError, 'tie|batch'):
                instance.peek('core', at=30)
        self.assertEqual(merge.metrics(), before)
        with sqlite3.connect(merge.path) as con:
            self.assertEqual(con.execute('SELECT COUNT(*) FROM events').fetchone()[0], 3)
            self.assertEqual(con.execute('SELECT COUNT(*) FROM acks').fetchone()[0], 0)

    def test_repeatable_peek_reopen_before_after_ack_and_configuration_identity(self):
        merge = self.merge()
        for event in self.events:
            merge.append(event)
        self.seal(merge)
        first = merge.peek('core', at=30)
        self.assertEqual(merge.peek('core', at=30), first)
        reopened = self.merge()
        self.assertEqual(reopened.peek('core', at=30).id, first.id)
        self.assertTrue(reopened.acknowledge(first, at=30))
        reopened = self.merge()
        self.assertFalse(reopened.acknowledge(first, at=30))
        second = reopened.peek('core', at=30)
        self.assertEqual(tuple(e.id for e in second.events), ('a1',))
        reopened.acknowledge(second, at=30)
        self.assertIsNone(self.merge().peek('core', at=30))
        with self.assertRaises(ContractError):
            self.merge(max_batch=2)

    def test_skipped_forged_unavailable_and_conflicting_acknowledgements(self):
        merge = self.merge()
        for event in self.events:
            merge.append(event)
        self.seal(merge)
        first = merge.peek('core', at=30)
        second = ReplayBatch('core', merge.version, 20, (self.events[2],))
        forged = replace(first, events=(replace(self.events[0], payload=b'forged'), self.events[1]))
        metrics = merge.metrics()
        for batch, at in ((second, 30), (forged, 30), (first, 29),
                          (replace(first, contract_version='foreign-contract'), 30)):
            with self.subTest(batch=batch.id, at=at), self.assertRaises(ContractError):
                merge.acknowledge(batch, at=at)
        self.assertEqual(merge.metrics(), metrics)
        self.assertEqual(merge.peek('core', at=30), first)
        merge.acknowledge(first, at=30)
        with self.assertRaises(IntegrityError):
            merge.acknowledge(forged, at=30)
        self.assertEqual(merge.peek('core', at=30), second)
