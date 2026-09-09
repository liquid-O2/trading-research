"""Streaming acquired MBP observations for the auction/participation study.

The existing CompactProjector is the price/side/book reference adapter. This
consumer adds exact physical row addresses, original side/flag fields, explicit
excluded trades, and bounded streaming, without retaining all quotes in RAM.
Source event time plus a declared delay is an information scenario, not receipt.
"""
from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
import hashlib
import math
import struct
import time
from pathlib import Path

from trading_research.data.compact import (
    SOURCE_CLOCK_REDUNDANT_BACKWARD_SNAPSHOT_V1,
    SOURCE_CLOCK_STRICT,
    CompactProjector,
    arrow_bytes,
    named_source_clock_policy,
)
from trading_research.data.reconcile import select_groups
from trading_research.errors import ContractError, IntegrityError
from trading_research.operations.artifacts import digest
from trading_research.research.auction_flow_arrow import value_digest


VERSION = "auction-flow-physical-row-stream-v1"
CARRY_VERSION = "auction-flow-source-continuation-v1"
RAW_FIELDS = ("t", "action", "side", "price", "size", "bid_px", "ask_px",
              "bid_sz", "ask_sz", "instrument_id", "flags")


class RawStreamFingerprint:
    """Address-free, fixed-block all-field hash for acquisition comparisons.

    Different physical reader batches cannot create a false source difference.
    Every row and identical-print multiplicity still enters in original order.
    Original batch hashes and file/row lineage remain separately retained.
    """
    def __init__(self):
        self.parts, self.rows, self.total = [], 0, 0
        self.sha = hashlib.sha256()
        self.closed = False

    def _flush(self):
        import pyarrow as pa

        if self.parts:
            table = pa.concat_tables(self.parts).combine_chunks()
            self.sha.update(len(table).to_bytes(8, 'big'))
            self.sha.update(bytes.fromhex(value_digest(table)))
            self.parts, self.rows = [], 0

    def add(self, batch):
        import pyarrow as pa

        if self.closed:
            raise IntegrityError('completed raw fingerprint cannot resume')
        table = pa.Table.from_batches([batch]) if isinstance(batch, pa.RecordBatch) else batch
        offset = 0
        self.total += len(table)
        while offset < len(table):
            amount = min(65536 - self.rows, len(table) - offset)
            self.parts.append(table.slice(offset, amount))
            self.rows += amount
            offset += amount
            if self.rows == 65536:
                self._flush()

    def finish(self):
        if not self.closed:
            self._flush()
            self.closed = True
        return {'version': 'all-eleven-fields-fixed-65536-row-values-v2', 'rows': self.total,
                'sha256': self.sha.hexdigest(), 'comparison_scope': 'actual ordered selected values and multiplicity'}


@dataclass(frozen=True)
class ObservedBatch:
    """All projections use Arrow Tables, including raw and excluded records."""
    raw: object
    quotes: tuple
    trades: tuple
    excluded_trades: object
    source: dict
    temporal_raw: object = None
    replay_records: object = None
    replay_source_orders: tuple = ()


class AuctionFlowStream:
    """One bounded requested interval; yields data and then a completed manifest.

    A failed/partly consumed iterator cannot claim a complete-window manifest.
    Different raw prints keep different physical addresses even at equal times.
    The original source files supply the canonical all-field event record; the
    compact tables are indexed consumers, not a replacement for those bytes.
    """

    def __init__(self, *, data_root: Path, index: dict, dataset: str,
                 start_ns: int, end_ns: int, maximum_scan_rows: int,
                 latency_ns: int = 250_000_000, batch_rows: int = 65536, source_paths=None,
                 continuation=None, source_clock_policy=SOURCE_CLOCK_STRICT, on_replay_record=None):
        if (type(start_ns) is not int or type(end_ns) is not int
                or not 0 <= start_ns < end_ns < 2**63
                or type(latency_ns) is not int or not 0 <= latency_ns <= 1_000_000_000
                or end_ns + latency_ns >= 2**63
                or type(batch_rows) is not int or not 1 <= batch_rows <= 65536
                or type(maximum_scan_rows) is not int or maximum_scan_rows < 1):
            raise ContractError("bounded interval, event-delay scenario and scan size required")
        self.data_root = Path(data_root).resolve()
        self.dataset = dataset
        self.start, self.end = start_ns, end_ns
        self.delay = latency_ns
        self.batch_rows = batch_rows
        if source_paths is not None:
            available = {r['path'] for r in index['datasets'][dataset]}
            if (type(source_paths) is not tuple or not source_paths or len(set(source_paths)) != len(source_paths)
                    or not set(source_paths) <= available):
                raise ContractError('explicit existing acquisition variant paths required')
            index = {**index, 'datasets': {**index['datasets'], dataset:
                [r for r in index['datasets'][dataset] if r['path'] in source_paths]}}
        self.lineage_records = tuple(index['datasets'][dataset])
        self.lineage_id = digest({'dataset': dataset, 'sources':
            [(r['path'], digest(r)) for r in sorted(self.lineage_records, key=lambda r: r['path'])]})
        self.selection, self.expected_scan = select_groups(
            index, dataset=dataset, start=start_ns, end=end_ns,
            max_scan_rows=maximum_scan_rows)
        selected_paths = {r['path'] for r, _ in self.selection}
        for record in self.lineage_records:
            if (record['path'] not in selected_paths and record['groups']
                    and min(g['minimum'] for g in record['groups']) < end_ns
                    and max(g['maximum'] for g in record['groups']) >= start_ns):
                # Verify the containing file even if the requested interval
                # falls entirely between two physical row groups.
                self.selection.append((record, []))
        ranges = sorted((max(start_ns, min(g['minimum'] for g in r['groups'])),
                         min(end_ns, max(g['maximum'] for g in r['groups']) + 1), r['path'])
                        for r, _ in self.selection)
        if any(a[1] > b[0] for a, b in zip(ranges[:-1], ranges[1:])):
            raise IntegrityError('overlapping acquired streams require separate explicit source variants; merging/deduplication is unsupported')
        self.selection.sort(key=lambda item: min(g['minimum'] for g in item[0]['groups']))
        self.reader_batch_ceiling = sum((sum(record['groups'][g]['rows'] for g in groups) + batch_rows - 1) // batch_rows
            + max(0, len(groups) - 1) for record, groups in self.selection)
        self.source_paths = source_paths
        self.source_clock_policy = named_source_clock_policy(source_clock_policy)
        if on_replay_record is not None and not callable(on_replay_record):
            raise ContractError('replay-record retention callback must be callable')
        self.on_replay_record = on_replay_record
        self.projector = CompactProjector(tick_denominator=4, maximum_rows=maximum_scan_rows,
                                          source_clock_policy=self.source_clock_policy)
        self.source_order_base = 0
        self.continuation = None
        self.prefix_start = start_ns
        self.prior_prefix_flow = {}
        self.invalidation_lineage = {}
        self.last_source_event = None
        self._last_original_record = None
        if continuation is not None:
            self._restore(continuation)
        self.scan_rows = 0
        self.cpu = Counter()
        self.reader_batches = 0
        self.sources = []
        self.exclusions = Counter()
        self.actions = Counter()
        self.flags = Counter()
        self.action_sides = Counter()
        self.trade_totals = Counter({name: 0 for name in ("trades", "volume", "buy_volume", "sell_volume",
                                                        "unknown_volume", "unpriced_volume")})
        self.invalid_size_instruments = set()
        self.raw_stream_hash = hashlib.sha256()
        self.canonical_fingerprint = RawStreamFingerprint()
        self._started = self._completed = self._failed = False

    def _restore(self, carry):
        """Restore only an adjacent completed interval of the exact source lineage.

        Local flow totals restart at the new measurement anchor. The persistent
        book invalidation and the separate original-prefix completeness do not.
        A source-path or delay change requires a separately declared lineage.
        """
        import copy

        if not isinstance(carry, dict):
            raise ContractError('completed source continuation record required')
        payload = {k: v for k, v in carry.items() if k != 'sha256'}
        if (carry.get('sha256') != digest(payload) or carry.get('version') != CARRY_VERSION
                or carry.get('dataset') != self.dataset or carry.get('lineage_id') != self.lineage_id
                or carry.get('next_start_ns') != self.start or carry.get('latency_ns') != self.delay
                or carry.get('completed') is not True):
            raise IntegrityError('source continuation is changed, nonadjacent, uncompleted or from another lineage')
        base, origin = carry.get('next_source_order'), carry.get('prefix_start_ns')
        if (type(base) is not int or not 0 <= base < 2**63 - self.projector.maximum_rows
                or type(origin) is not int or not 0 <= origin <= self.start
                or not isinstance(carry.get('blocked'), dict) or not isinstance(carry.get('prefix_flow_complete'), dict)):
            raise IntegrityError('source continuation has invalid order or prefix coordinates')
        last = carry.get('last_source_event')
        if last is not None and (type(last.get('event_ns')) is not int or not origin <= last['event_ns'] < self.start
                or type(last.get('source_order')) is not int or last['source_order'] != base - 1
                or type(last.get('source_row')) is not int or last['source_row'] < 0
                or type(last.get('source_key')) is not str or not last['source_key']):
            raise IntegrityError('source continuation terminal event is future or has lost its original address')
        if (base == 0) != (last is None):
            raise IntegrityError('source continuation row count and last observed event disagree')
        carry_policy = carry.get('source_clock_policy', SOURCE_CLOCK_STRICT)
        if (carry_policy not in (SOURCE_CLOCK_STRICT, SOURCE_CLOCK_REDUNDANT_BACKWARD_SNAPSHOT_V1)
                or carry_policy != self.source_clock_policy):
            raise IntegrityError('source continuation is changed, nonadjacent, uncompleted or from another lineage')
        last_original = None
        highwater = None
        if self.source_clock_policy != SOURCE_CLOCK_STRICT:
            if 'clock_highwater_ns' not in carry or 'last_original_record' not in carry:
                raise IntegrityError('source continuation lost its source-clock policy or replay carry')
            highwater = carry.get('clock_highwater_ns')
            last_original = carry.get('last_original_record')
            if (last is None) != (last_original is None) or (last is None) != (highwater is None):
                raise IntegrityError('source continuation row count and last observed event disagree')
            if last is not None:
                last_original = self._validated_last_original_record(
                    last_original, last, origin=origin, start=self.start, highwater=highwater)
            if type(carry.get('disposed_snapshot_rows')) is not int or carry['disposed_snapshot_rows'] < 0:
                raise IntegrityError('source continuation lost its source-clock policy or replay carry')
        for key, row in carry['blocked'].items():
            if (not isinstance(key, str) or not key.isdigit() or int(key) <= 0
                    or not isinstance(row, dict) or type(row.get('source_order')) is not int
                    or not 0 <= row['source_order'] < base or type(row.get('event_ns')) is not int
                    or not origin <= row['event_ns'] < self.start or type(row.get('source_row')) is not int
                    or row['source_row'] < 0 or type(row.get('source_key')) is not str or not row['source_key']):
                raise IntegrityError('source continuation lost the first book-invalidation lineage')
        if any(not isinstance(k, str) or not k.isdigit() or int(k) <= 0 or type(v) is not bool
               for k, v in carry['prefix_flow_complete'].items()):
            raise IntegrityError('source continuation flow completeness is not an explicit instrument decision')
        self.continuation = copy.deepcopy(carry)
        self.source_order_base, self.prefix_start = base, origin
        self.prior_prefix_flow = {int(k): v for k, v in carry['prefix_flow_complete'].items()}
        self.invalidation_lineage = {int(k): dict(v) for k, v in carry['blocked'].items()}
        # CompactProjector's local counts stay bounded by this interval. Its
        # negative local invalidation address denotes an actual prior event.
        self.projector.blocked = {int(k): v['source_order'] - base for k, v in carry['blocked'].items()}
        if self.source_clock_policy == SOURCE_CLOCK_STRICT:
            self.projector.prior_time = None if last is None else last['event_ns']
            self._last_original_record = None
        else:
            terminal = None if last_original is None else {
                **{name: last_original[name] for name in RAW_FIELDS},
                'source_row': last_original['source_row'],
                'physical_source_key': last_original['source_key'],
            }
            self.projector.restore_clock_carry(terminal, highwater=highwater)
            self._last_original_record = None if last_original is None else dict(last_original)
        self.last_source_event = None if last is None else dict(last)

    def _validated_last_original_record(self, record, last, *, origin, start, highwater):
        required = RAW_FIELDS + ('source_row', 'source_order', 'source_key')
        if (not isinstance(record, dict) or set(record) != set(required)
                or type(highwater) is not int or not origin <= highwater < start
                or highwater < last['event_ns']
                or record.get('t') != last['event_ns'] or record.get('source_order') != last['source_order']
                or record.get('source_row') != last['source_row'] or record.get('source_key') != last['source_key']):
            raise IntegrityError('source continuation lost its source-clock policy or replay carry')
        # Hash the encoded carry before this method; restore original numeric bits
        # only for the terminal raw record consumed by the projector.
        record = dict(record)
        for name in ('price', 'bid_px', 'ask_px', 'size', 'bid_sz', 'ask_sz', 'flags'):
            value = record.get(name)
            if isinstance(value, dict):
                bits = value.get('$float64_bits_le')
                if (set(value) != {'$float64_bits_le'} or type(bits) is not str
                        or len(bits) != 16 or any(c not in '0123456789abcdef' for c in bits)):
                    raise IntegrityError('source continuation has invalid nonfinite raw-field encoding')
                decoded = struct.unpack('<d', bytes.fromhex(bits))[0]
                if math.isfinite(decoded):
                    raise IntegrityError('finite raw carry fields must retain their original JSON representation')
                record[name] = decoded
        if any(type(record.get(name)) is not int for name in
               ('t', 'source_row', 'source_order', 'instrument_id')):
            raise IntegrityError('source continuation lost its source-clock policy or replay carry')
        if type(record.get('source_key')) is not str or not record['source_key']:
            raise IntegrityError('source continuation lost its source-clock policy or replay carry')
        if (any(record.get(name) is not None and type(record[name]) not in (int, float)
                for name in ('price', 'bid_px', 'ask_px', 'size', 'bid_sz', 'ask_sz', 'flags'))
                or any(record.get(name) is not None and type(record[name]) is not str for name in ('action', 'side'))):
            raise IntegrityError('source continuation lost its source-clock policy or replay carry')
        return dict(record)

    def carry(self):
        """Publish after every selected source row and source stamp was checked."""
        if not self._completed or self._failed:
            raise IntegrityError('partial or failed source intervals cannot provide continuation')
        current = dict(self.projector.flow_complete)
        current.update({instrument: False for instrument in self.invalid_size_instruments})
        prefix = {key: self.prior_prefix_flow.get(key, True) and current.get(key, True)
                  for key in self.prior_prefix_flow.keys() | current.keys()}
        result = {'version': CARRY_VERSION, 'completed': True, 'dataset': self.dataset,
            'lineage_id': self.lineage_id, 'latency_ns': self.delay,
            'prefix_start_ns': self.prefix_start, 'next_start_ns': self.end,
            'next_source_order': self.source_order_base + self.projector.rows,
            'last_source_event': self.last_source_event,
            'blocked': {str(k): dict(v) for k, v in sorted(self.invalidation_lineage.items())},
            'prefix_flow_complete': {str(k): v for k, v in sorted(prefix.items())},
            'previous_continuation_sha256': None if self.continuation is None else self.continuation['sha256'],
            'selected_raw_values': self.canonical_fingerprint.finish(),
            'book_recovery': 'no inferred recovery; all original invalidations persist'}
        if self.source_clock_policy != SOURCE_CLOCK_STRICT:
            result['source_clock_policy'] = self.source_clock_policy
            result['clock_highwater_ns'] = self.projector.prior_time
            result['last_original_record'] = None if self._last_original_record is None else {
                name: ({'$float64_bits_le': struct.pack('<d', value).hex()}
                       if type(value) is float and not math.isfinite(value) else value)
                for name, value in self._last_original_record.items()}
            result['disposed_snapshot_rows'] = self.projector.disposed_snapshot_rows
        return {**result, 'sha256': digest(result)}

    def _enrich(self, table, raw, source_order_base, source_key):
        import pyarrow as pa
        import pyarrow.compute as pc

        positions = pc.subtract(table["source_order"], source_order_base)
        for name, original in (("source_row", "source_row"), ("raw_flags", "flags"),
                               ("raw_side", "side"), ("raw_action", "action")):
            table = table.append_column(name, raw[original].take(positions))
        table = table.append_column("source_key", pa.repeat(pa.scalar(source_key), len(table)))
        table = table.append_column("known_at_ns", pc.add(table["t"], self.delay))
        return table

    def _project(self, original, *, source, physical_rows):
        import numpy as np
        import pyarrow as pa
        import pyarrow.compute as pc

        if set(original.schema.names) != set(RAW_FIELDS):
            raise IntegrityError("the complete frozen eleven-field MBP schema changed")
        # Hash the actual original columns, before adding any derived address.
        payload = arrow_bytes(original)
        part_hash = hashlib.sha256(payload).hexdigest()
        self.raw_stream_hash.update(len(payload).to_bytes(8, "big"))
        self.raw_stream_hash.update(payload)
        self.canonical_fingerprint.add(original)
        raw = pa.Table.from_batches([original]) if isinstance(original, pa.RecordBatch) else original
        raw = raw.append_column("source_row", physical_rows)
        local_before = self.projector.rows
        before = self.source_order_base + local_before
        part_identity = {**source, "first_physical_row": physical_rows[0].as_py(),
                         "last_physical_row": physical_rows[-1].as_py(),
                         "selected_rows": len(raw), "original_all_field_arrow_sha256": part_hash}
        quotes, trades = self.projector.project(raw, source_part=digest(part_identity),
                                                physical_source_key=source['source_key'])
        for instrument, local_at in self.projector.blocked.items():
            if instrument not in self.invalidation_lineage:
                position = local_at - local_before
                if not 0 <= position < len(raw):
                    raise IntegrityError('first invalidation does not join its actual original raw row')
                self.invalidation_lineage[instrument] = {'event_ns': raw['t'][position].as_py(),
                    'source_order': self.source_order_base + local_at,
                    'source_row': raw['source_row'][position].as_py(), 'source_key': source['source_key'],
                    'raw_action': raw['action'][position].as_py(), 'raw_flags': raw['flags'][position].as_py()}
        # A common original-order address also binds raw invalidations to the
        # eligible trade and quote projections. It changes no source bytes.
        raw = raw.append_column("source_order", pa.array(np.arange(before, before + len(raw), dtype=np.int64)))
        key = source["source_key"]
        self.last_source_event = {'event_ns': raw['t'][-1].as_py(), 'source_order': before + len(raw) - 1,
                                 'source_row': raw['source_row'][-1].as_py(), 'source_key': key}
        if self.source_clock_policy != SOURCE_CLOCK_STRICT:
            self._last_original_record = {**{name: raw[name][-1].as_py() for name in RAW_FIELDS},
                'source_row': raw['source_row'][-1].as_py(), 'source_order': before + len(raw) - 1, 'source_key': key}
        quote_parts = []
        for q in quotes:
            if self.source_order_base:
                q = q.set_column(q.schema.get_field_index('source_order'), 'source_order',
                                 pc.add(q['source_order'], self.source_order_base))
            q = self._enrich(q, raw, before, key)
            positions = pc.subtract(q['source_order'], before)
            q = q.append_column('raw_price', raw['price'].take(positions))
            q = q.append_column('raw_size', raw['size'].take(positions))
            instrument = q["instrument_id"][0].as_py()
            local_invalid = self.projector.blocked.get(instrument)
            invalid_from = None if local_invalid is None else local_invalid + self.source_order_base
            eligible = pa.repeat(pa.scalar(True), len(q)) if invalid_from is None else pc.less(q["source_order"], invalid_from)
            # The earlier execution projection required a positive spread.
            # Preserve that comparator while implementing the literal source
            # noncrossed BBO definition, including locked quotes, here.
            domain = pc.and_(pc.greater(q["bid"], 0), pc.and_(pc.greater(q["ask"], 0), pc.less_equal(q["bid"], q["ask"])))
            for name in ("bid_size", "ask_size"):
                domain = pc.and_(domain, pc.and_(pc.greater(q[name], 0), pc.less(q[name], 2**32 - 1)))
            valid = pc.and_(eligible, domain)
            q = q.append_column("legacy_positive_spread_book_valid", q["book_valid"])
            q = q.set_column(q.schema.get_field_index("book_valid"), "book_valid", pc.cast(valid, pa.uint8()))
            quote_parts.append(q)
        quotes = tuple(quote_parts)
        trade_parts = []
        for t in trades:
            if self.source_order_base:
                t = t.set_column(t.schema.get_field_index('source_order'), 'source_order',
                                 pc.add(t['source_order'], self.source_order_base))
            t = t.filter(pc.less(t["size"], 2**32 - 1))
            if not len(t):
                continue
            t = self._enrich(t, raw, before, key)
            self.trade_totals["trades"] += len(t)
            self.trade_totals["volume"] += pc.sum(t["size"]).as_py() or 0
            for sign, name in ((1, "buy_volume"), (-1, "sell_volume"), (0, "unknown_volume")):
                self.trade_totals[name] += pc.sum(t.filter(pc.equal(t["side"], sign))["size"]).as_py() or 0
            self.trade_totals["unpriced_volume"] += pc.sum(t.filter(pc.equal(t["price_valid"], 0))["size"]).as_py() or 0
            trade_parts.append(t)
        trades = tuple(trade_parts)
        # Snapshot and malformed-size trade records remain addressable evidence.
        action = pc.cast(raw["action"], pa.string())
        flags = raw["flags"]
        is_trade = pc.fill_null(pc.equal(action, "T"), False)
        snapshot = pc.not_equal(pc.bit_wise_and(flags, 32), 0)
        invalid_size = pc.invert(pc.fill_null(pc.and_(pc.greater(raw["size"], 0), pc.less(raw["size"], 2**32 - 1)), False))
        keep_excluded = pc.and_(is_trade, pc.or_(snapshot, invalid_size))
        reason = pc.add(pc.if_else(snapshot, 1, 0), pc.if_else(invalid_size, 2, 0))
        excluded = raw.append_column("exclusion_bits", reason).filter(keep_excluded)
        excluded = excluded.append_column("source_key", pa.repeat(pa.scalar(key), len(excluded)) if len(excluded) else pa.array([]))
        self.exclusions["snapshot_trade_rows"] += pc.sum(pc.cast(pc.and_(is_trade, snapshot), pa.int64())).as_py() or 0
        self.exclusions["invalid_size_trade_rows"] += pc.sum(pc.cast(pc.and_(is_trade, invalid_size), pa.int64())).as_py() or 0
        self.exclusions["unique_excluded_trade_rows"] += len(excluded)
        incomplete = pc.and_(is_trade, pc.and_(invalid_size, pc.invert(snapshot)))
        self.invalid_size_instruments.update(pc.unique(raw["instrument_id"].filter(incomplete)).to_pylist())
        for name, counter in (("action", self.actions), ("flags", self.flags)):
            for cell in pc.value_counts(raw[name]).to_pylist():
                counter[str(cell["values"])] += cell["counts"]
        pairs = pa.table({"action": action, "side": pc.cast(raw["side"], pa.string()),
                          "event_ns": raw["t"]}).group_by(["action", "side"], use_threads=False).aggregate([("event_ns", "count")])
        for cell in pairs.to_pylist():
            self.action_sides[(cell["action"], cell["side"])] += cell["event_ns_count"]
        replay_orders = tuple(self.source_order_base + value for value in self.projector.last_replay_orders)
        if replay_orders:
            temporal = raw.filter(pc.invert(pc.is_in(
                raw['source_order'], value_set=pa.array(replay_orders, type=raw.schema.field('source_order').type))))
            replay_records = self._replay_record_table(raw, replay_orders, source_key=key, batch_first=before)
            if len(replay_records) > self.projector.maximum_rows:
                raise ContractError('replay evidence exceeds the selected-row budget')
            if self.on_replay_record is not None:
                self.on_replay_record(replay_records, part_identity)
        else:
            temporal = raw
            replay_records = raw.slice(0, 0)
        return ObservedBatch(raw, quotes, trades, excluded, part_identity,
                             temporal_raw=temporal, replay_records=replay_records,
                             replay_source_orders=tuple(replay_orders))

    def _replay_record_table(self, raw, replay_orders, *, source_key, batch_first):
        import pyarrow as pa
        import pyarrow.compute as pc

        records = raw.filter(pc.is_in(
            raw['source_order'], value_set=pa.array(replay_orders, type=raw.schema.field('source_order').type)))
        by_index = {item['index']: item for item in self.projector.last_replay_evidence}
        pred_row, pred_order, pred_key, pred_t, pred_action, pred_flags, reasons = [], [], [], [], [], [], []
        for row in records.to_pylist():
            index = row['source_order'] - batch_first
            item = by_index[index]
            predecessor = item['predecessor']
            pred_row.append(predecessor.get('source_row'))
            if index > 0:
                pred_order.append(batch_first + index - 1)
                pred_key.append(source_key)
            else:
                pred_order.append(batch_first - 1)
                pred_key.append(predecessor.get('physical_source_key') or source_key)
            pred_t.append(predecessor.get('t'))
            pred_action.append(predecessor.get('action'))
            pred_flags.append(predecessor.get('flags'))
            reasons.append(item['reason'])
        return records.append_column('predecessor_source_row', pa.array(pred_row, type=pa.int64())) \
            .append_column('predecessor_source_order', pa.array(pred_order, type=pa.int64())) \
            .append_column('predecessor_source_key', pa.array(pred_key, type=pa.string())) \
            .append_column('predecessor_t', pa.array(pred_t, type=pa.int64())) \
            .append_column('predecessor_action', pa.array(pred_action, type=pa.string())) \
            .append_column('predecessor_flags', pa.array(pred_flags, type=pa.int64())) \
            .append_column('replay_reason', pa.array(reasons, type=pa.string()))

    def __iter__(self):
        import numpy as np
        import pyarrow as pa
        import pyarrow.compute as pc
        import pyarrow.parquet as pq

        if self._started:
            raise IntegrityError("a source stream is single-pass; reuse its retained output")
        self._started = True
        try:
            for record, groups in self.selection:
                metadata_started = time.process_time()
                path = (self.data_root / record["path"]).resolve()
                if not path.is_relative_to(self.data_root):
                    raise ContractError("registered source escapes the admitted data root")
                before = path.stat()
                stamp = (before.st_size, before.st_mtime_ns)
                if stamp != (record["bytes"], record["mtime_ns"]):
                    raise IntegrityError("source differs from the retained complete footer index")
                source = {"path": record["path"], "metadata_version": digest(record),
                          "dataset": self.dataset, "groups": groups}
                # Query bounds/group selections do not mint another identity
                # for the same physical source row in an overlapping window.
                source["source_key"] = digest({k: source[k] for k in ("path", "metadata_version", "dataset")})
                with pq.ParquetFile(path) as pf:
                    if (pf.metadata.num_rows != record["rows"]
                            or pf.schema_arrow.names != list(RAW_FIELDS)
                            or str(pf.schema_arrow) != record["schema"]):
                        raise IntegrityError("source schema or physical row count changed")
                    offsets = {}
                    current = 0
                    for group in range(pf.num_row_groups):
                        offsets[group] = current
                        current += pf.metadata.row_group(group).num_rows
                    group_position = offset_in_group = 0
                    self.cpu['source_metadata_and_open'] += time.process_time() - metadata_started
                    # The retained reconciliation uses this exact batch layout
                    # across selected row groups. Preserve it for raw-byte reuse.
                    batches = iter(pf.iter_batches(row_groups=groups, batch_size=self.batch_rows, use_threads=False))
                    while True:
                        read_started = time.process_time()
                        try:
                            batch = next(batches)
                        except StopIteration:
                            self.cpu['physical_batch_decode'] += time.process_time() - read_started
                            break
                        self.cpu['physical_batch_decode'] += time.process_time() - read_started
                        selected_started = time.process_time()
                        self.reader_batches += 1
                        self.scan_rows += len(batch)
                        clock = batch.column(batch.schema.get_field_index("t"))
                        if clock.null_count:
                            raise IntegrityError("unlocated event time cannot be silently filtered")
                        remaining, address_parts, spans = len(batch), [], []
                        while remaining:
                            if group_position >= len(groups):
                                raise IntegrityError("decoded rows exceed their physical group addresses")
                            group = groups[group_position]
                            count = min(remaining, pf.metadata.row_group(group).num_rows - offset_in_group)
                            first = offsets[group] + offset_in_group
                            address_parts.append(pa.array(np.arange(first, first + count, dtype=np.int64)))
                            spans.append({"group": group, "first_row_in_group": offset_in_group, "rows": count})
                            offset_in_group += count
                            remaining -= count
                            if offset_in_group == pf.metadata.row_group(group).num_rows:
                                group_position += 1
                                offset_in_group = 0
                        physical = pa.concat_arrays(address_parts)
                        mask = pc.and_(pc.greater_equal(clock, self.start), pc.less(clock, self.end))
                        selected = batch.filter(mask)
                        selected_physical = physical.filter(mask)
                        self.cpu['physical_address_and_selection'] += time.process_time() - selected_started
                        if len(selected):
                            projected_started = time.process_time()
                            result = self._project(selected, source={**source, "physical_group_spans": spans},
                                                   physical_rows=selected_physical)
                            self.cpu['selected_projection'] += time.process_time() - projected_started
                            yield result
                after = path.stat()
                if stamp != (after.st_size, after.st_mtime_ns):
                    raise IntegrityError("source changed during the complete requested-window scan")
                self.sources.append(source)
            if self.scan_rows != self.expected_scan:
                raise IntegrityError("physical scan does not match all selected footer rows")
            if self.reader_batches > self.reader_batch_ceiling:
                raise IntegrityError('pinned reader split count exceeds the prospective source budget; update its measured bound before extraction')
            self._completed = True
            self.canonical_fingerprint.finish()
        except BaseException:
            self._failed = True
            raise

    def manifest(self):
        if not self._completed or self._failed:
            raise IntegrityError("partial or failed scans cannot certify the requested window")
        original = self.projector.manifest()
        complete = dict(original["observed_prefix_flow_complete"])
        complete.update({str(instrument): False for instrument in self.invalid_size_instruments})
        projection = {**original, "version": VERSION,
            "reference_projection_version": original["version"],
            "reference_projection_counts": original["counts"],
            "counts": {**original["counts"], **self.trade_totals},
            'raw_parts': tuple({**p, 'global_first_row': p['global_first_row'] + self.source_order_base,
                               'reference_local_first_row': p['global_first_row']} for p in original['raw_parts']),
            'unrecovered_book_instruments': {str(k): v['source_order'] for k, v in self.invalidation_lineage.items()},
            "observed_prefix_flow_complete": complete,
            "quote_domain": "positive exact quarter-point prices, bid <= ask, positive sizes below uint32 undefined sentinel",
            "size_domain": "0 < eligible executed size < 2**32 - 1; invalid/snapshot records retained separately"}
        if projection["counts"]["volume"] != sum(projection["counts"][name] for name in ("buy_volume", "sell_volume", "unknown_volume")):
            raise IntegrityError("source-valid flow partition does not conserve observed volume")
        payload = {"version": VERSION, "dataset": self.dataset, "start_ns": self.start,
                "end_ns": self.end, "event_latency_scenario_ns": self.delay,
                "strategy_receipt_observed": False, "exchange_sequence_observed": False,
                "physical_scan_rows": self.scan_rows, "expected_physical_scan_rows": self.expected_scan,
                'physical_reader_batches': self.reader_batches, 'physical_reader_batch_ceiling': self.reader_batch_ceiling,
                'source_cpu_components': dict(self.cpu),
                'source_order_base': self.source_order_base,
                'continuation_from': None if self.continuation is None else self.continuation['sha256'],
                'source_continuation': self.carry(),
                "source_all_field_arrow_stream_sha256": self.raw_stream_hash.hexdigest(),
                'canonical_selected_raw_stream': self.canonical_fingerprint.finish(),
                'explicit_source_variant_paths': self.source_paths,
                "sources": self.sources, "actions": dict(self.actions), "flags": dict(self.flags),
                "action_side_counts": [{"action": a, "side": s, "rows": count}
                    for (a, s), count in sorted(self.action_sides.items(), key=lambda item: repr(item[0]))],
                "trade_exclusions": dict(self.exclusions), "projection": projection,
                "source_window_nonempty": self.projector.rows > 0,
                "coverage_claim": "complete selected physical scan, conditional on the acquired stream; inspect gaps/quality",
                "no_new_volume_claim_from_missing_source": False}
        if self.source_clock_policy != SOURCE_CLOCK_STRICT:
            payload['source_clock_policy'] = self.source_clock_policy
            payload['source_clock_replay'] = {
                'policy': self.source_clock_policy,
                'disposed_snapshot_rows': self.projector.disposed_snapshot_rows,
                'reconstruction': 'original source addresses and all-field hashes; no timestamp rewrite',
                'provenance': 'explicit redundant_backward_snapshot_v1 no-economic-change replay disposition',
            }
        return payload
