"""Bounded durable availability merge with explicit independent-stream ties."""
from contextlib import contextmanager
from dataclasses import asdict, dataclass
import json
from pathlib import Path
import sqlite3
from types import MappingProxyType
from typing import Mapping

from trading_research.errors import ContractError, IntegrityError
from trading_research.foundations.time import AvailabilityBasis, Clocks, timestamp
from trading_research.operations.artifacts import canonical_json, digest


def _name(value):
    if not isinstance(value, str) or not value:
        raise ContractError('nonempty string identity required')
    return value


@dataclass(frozen=True)
class ReplayEvent:
    id: str
    partition: str
    sequence: int
    clocks: Clocks
    payload: bytes
    fields: frozenset[str] = frozenset()

    def __post_init__(self):
        _name(self.id); _name(self.partition)
        if type(self.sequence) is not int or not 0 <= self.sequence < 2**63:
            raise ContractError('source sequence must be a nonnegative int64')
        if not isinstance(self.clocks, Clocks) or not isinstance(self.payload, bytes):
            raise ContractError('immutable event needs typed availability and bytes')
        if not isinstance(self.fields, frozenset) or any(not isinstance(s, str) or not s for s in self.fields):
            raise ContractError('changed raw fields must be immutable named fields')

    def record(self):
        return {'id': self.id, 'partition': self.partition, 'sequence': self.sequence,
                'clocks': asdict(self.clocks), 'payload_hex': self.payload.hex(), 'fields': sorted(self.fields)}

    @classmethod
    def restore(cls, row):
        c = row['clocks']
        return cls(row['id'], row['partition'], row['sequence'],
                   Clocks(**{**c, 'basis': AvailabilityBasis(c['basis'])}),
                   bytes.fromhex(row['payload_hex']), frozenset(row['fields']))


@dataclass(frozen=True)
class ReplayBatch:
    domain: str
    contract_version: str
    known_at: int
    events: tuple[ReplayEvent, ...]

    def __post_init__(self):
        _name(self.domain); _name(self.contract_version); timestamp(self.known_at)
        if not isinstance(self.events, tuple) or not self.events or any(not isinstance(e, ReplayEvent) for e in self.events):
            raise ContractError('batch needs a nonempty immutable event tuple')
        if any(e.clocks.known_at != self.known_at for e in self.events):
            raise ContractError('batch mixes availability cuts')
        if (len({e.id for e in self.events}) != len(self.events) or
                tuple(sorted(self.events, key=lambda e: (e.partition, e.sequence))) != self.events):
            raise ContractError('batch must preserve unique IDs and declared within-source order')

    @property
    def ambiguous(self):
        return len({e.partition for e in self.events}) > 1

    @property
    def id(self):
        return digest([self.domain, self.contract_version, self.known_at, [e.record() for e in self.events]])

    def ordered(self, *, partition_priority: tuple[str, ...] | None = None):
        if not self.ambiguous:
            return self.events
        if partition_priority is None or set(partition_priority) != {e.partition for e in self.events} or len(set(partition_priority)) != len(partition_priority):
            raise ContractError('independent tied streams require an explicit complete ordering scenario')
        rank = {p: i for i, p in enumerate(partition_priority)}
        return tuple(sorted(self.events, key=lambda e: (rank[e.partition], e.sequence)))


@dataclass(frozen=True, init=False)
class PartitionMerge:
    """One retained disk envelope per event; per-domain peek/ack cursors.

    Watermarks are exclusive, evidence-backed availability bounds. Ack follows an
    idempotent consumer commit: a crash before ack redelivers the same batch.
    Retained history counts against the bound and is never silently evicted.
    """
    domains: Mapping[str, frozenset[str]]
    partitions: frozenset[str]
    max_records: int
    max_bytes: int
    max_batch: int
    path: Path
    version: str

    def __init__(self, path: Path, domains: Mapping[str, frozenset[str]], *, max_records=100_000,
                 max_bytes=64*1024**2, max_batch=1024):
        if not domains or any(not isinstance(parts, frozenset) or not parts for parts in domains.values()):
            raise ContractError('domains need explicit immutable nonempty partition sets')
        for d, parts in domains.items():
            _name(d)
            for p in parts: _name(p)
        if any(type(v) is not int or v <= 0 for v in (max_records, max_bytes, max_batch)):
            raise ContractError('positive record, byte and materialized tie bounds required')
        object.__setattr__(self, 'domains', MappingProxyType(dict(domains)))
        object.__setattr__(self, 'partitions', frozenset(p for parts in domains.values() for p in parts))
        for name, value in (('max_records', max_records), ('max_bytes', max_bytes), ('max_batch', max_batch), ('path', Path(path))):
            object.__setattr__(self, name, value)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        config = {'schema': 'availability-merge-v2', 'domains': {d: sorted(v) for d,v in sorted(domains.items())},
                  'max_records': max_records, 'max_bytes': max_bytes, 'max_batch': max_batch}
        object.__setattr__(self, 'version', digest(config))
        with self._connection() as con:
            con.execute('PRAGMA journal_mode=WAL')
            con.executescript('''
              CREATE TABLE IF NOT EXISTS config(id INTEGER PRIMARY KEY, raw BLOB NOT NULL);
              CREATE TABLE IF NOT EXISTS events(id TEXT PRIMARY KEY, partition TEXT NOT NULL, sequence INTEGER NOT NULL,
                 known_at INTEGER NOT NULL, raw BLOB NOT NULL, hash TEXT NOT NULL, UNIQUE(partition,sequence));
              CREATE INDEX IF NOT EXISTS event_clock ON events(known_at,partition,sequence);
              CREATE TABLE IF NOT EXISTS watermarks(partition TEXT NOT NULL, evidence TEXT NOT NULL, before_at INTEGER NOT NULL,
                 known_at INTEGER NOT NULL, raw BLOB NOT NULL, PRIMARY KEY(partition,evidence));
              CREATE TABLE IF NOT EXISTS acks(domain TEXT NOT NULL, at INTEGER NOT NULL, batch_id TEXT NOT NULL,
                 received_at INTEGER NOT NULL, raw BLOB NOT NULL, PRIMARY KEY(domain,at));
              CREATE TABLE IF NOT EXISTS counters(id INTEGER PRIMARY KEY, records INTEGER NOT NULL, bytes INTEGER NOT NULL);
            ''')
            con.execute('BEGIN IMMEDIATE')
            old = con.execute('SELECT raw FROM config WHERE id=1').fetchone()
            raw = canonical_json(config)
            if old is None:
                con.execute('INSERT INTO config VALUES(1,?)', (raw,))
                con.execute('INSERT INTO counters VALUES(1,0,0)')
            elif old[0] != raw:
                raise ContractError('merge configuration changed; explicit replay/migration required')
            con.commit()

    @contextmanager
    def _connection(self):
        con = sqlite3.connect(self.path, timeout=30)
        con.execute('PRAGMA synchronous=FULL')
        try: yield con
        finally: con.close()

    def _reserve(self, con, size):
        records, count = con.execute('SELECT records,bytes FROM counters WHERE id=1').fetchone()
        if records + 1 > self.max_records or count + size > self.max_bytes:
            raise ContractError('retained merge storage bound reached; explicit backpressure/rotation required')
        con.execute('UPDATE counters SET records=records+1,bytes=bytes+? WHERE id=1', (size,))

    def append(self, event: ReplayEvent):
        if not isinstance(event, ReplayEvent) or event.partition not in self.partitions:
            raise ContractError('event partition is not declared')
        raw = canonical_json(event.record())
        with self._connection() as con:
            con.execute('BEGIN IMMEDIATE')
            old = con.execute('SELECT raw FROM events WHERE id=?', (event.id,)).fetchone()
            if old:
                if old[0] != raw: raise IntegrityError('event identity reused with different content')
                return False
            bound = con.execute('SELECT MAX(before_at) FROM watermarks WHERE partition=?', (event.partition,)).fetchone()[0]
            if bound is not None and event.clocks.known_at < bound:
                raise ContractError('late event violates sealed availability watermark; correction needs its new receipt')
            if con.execute('SELECT 1 FROM events WHERE partition=? AND sequence=?', (event.partition, event.sequence)).fetchone():
                raise IntegrityError('source order identity reused')
            self._reserve(con, len(raw))
            con.execute('INSERT INTO events VALUES(?,?,?,?,?,?)',
                        (event.id, event.partition, event.sequence, event.clocks.known_at, raw, digest(raw)))
            con.commit()
        return True

    def advance(self, partition: str, *, before: int, known_at: int, evidence_id: str):
        timestamp(before); timestamp(known_at); _name(evidence_id)
        if partition not in self.partitions or known_at < before:
            raise ContractError('watermark needs a declared partition and cannot certify future availability')
        raw = canonical_json([partition, before, known_at, evidence_id])
        with self._connection() as con:
            con.execute('BEGIN IMMEDIATE')
            old = con.execute('SELECT raw FROM watermarks WHERE partition=? AND evidence=?', (partition, evidence_id)).fetchone()
            if old:
                if old[0] != raw: raise IntegrityError('watermark evidence identity conflict')
                return False
            prior = con.execute('SELECT MAX(before_at),MAX(known_at) FROM watermarks WHERE partition=?', (partition,)).fetchone()
            if any(old is not None and new < old for new,old in zip((before,known_at),prior)):
                raise ContractError('watermark/receipt cannot regress')
            self._reserve(con, len(raw))
            con.execute('INSERT INTO watermarks VALUES(?,?,?,?,?)', (partition,evidence_id,before,known_at,raw))
            con.commit()
        return True

    def _peek(self, con, domain, at):
        timestamp(at)
        if domain not in self.domains: raise ContractError('unknown consumer domain')
        self._validate_cursor_time(con, domain, at)
        parts = sorted(self.domains[domain]); marks = []
        for p in parts:
            w = con.execute('SELECT MAX(before_at) FROM watermarks WHERE partition=? AND known_at<=?', (p,at)).fetchone()[0]
            if w is None: return None
            marks.append(w)
        end = min(marks)
        last = con.execute('SELECT MAX(at) FROM acks WHERE domain=?', (domain,)).fetchone()[0]
        query = 'partition IN (' + ','.join('?' for _ in parts) + ') AND known_at<?'
        args = [*parts, end]
        if last is not None: query += ' AND known_at>?'; args.append(last)
        next_at = con.execute('SELECT MIN(known_at) FROM events WHERE '+query, args).fetchone()[0]
        if next_at is None: return None
        rows = con.execute('SELECT id,partition,sequence,known_at,raw,hash FROM events WHERE '+query+
                           ' AND known_at=? ORDER BY partition,sequence LIMIT ?', [*args,next_at,self.max_batch+1]).fetchall()
        if len(rows)>self.max_batch:
            raise ContractError('equal-time batch exceeds the materialization bound; no tie may be silently split')
        events=[]
        for id,p,seq,known,raw,sha in rows:
            if digest(raw) != sha: raise IntegrityError('merge envelope content hash mismatch')
            e=ReplayEvent.restore(json.loads(raw))
            if (e.id,e.partition,e.sequence,e.clocks.known_at)!=(id,p,seq,known):
                raise IntegrityError('merge envelope index differs from original content')
            events.append(e)
        return ReplayBatch(domain,self.version,next_at,tuple(events))

    def _validate_cursor_time(self, con, domain, at):
        last_received = con.execute('SELECT MAX(received_at) FROM acks WHERE domain=?', (domain,)).fetchone()[0]
        if last_received is not None and at < last_received:
            raise ContractError('consumer query/acknowledgement precedes its durable cursor receipt')

    def peek(self, domain: str, *, at: int):
        with self._connection() as con:
            con.execute('BEGIN')
            return self._peek(con,domain,at)

    def acknowledge(self, batch: ReplayBatch, *, at: int):
        timestamp(at)
        if not isinstance(batch, ReplayBatch) or batch.contract_version != self.version:
            raise ContractError('acknowledgement belongs to another merge contract')
        with self._connection() as con:
            con.execute('BEGIN IMMEDIATE')
            self._validate_cursor_time(con, batch.domain, at)
            prior=con.execute('SELECT batch_id FROM acks WHERE domain=? AND at=?', (batch.domain,batch.known_at)).fetchone()
            if prior:
                if prior[0] != batch.id: raise IntegrityError('conflicting acknowledgement at the same cut')
                return False
            expected=self._peek(con,batch.domain,at)
            if expected != batch:
                raise ContractError('cannot acknowledge unavailable, forged or skipped batch')
            raw=canonical_json([batch.domain,batch.known_at,batch.id,at])
            self._reserve(con,len(raw))
            con.execute('INSERT INTO acks VALUES(?,?,?,?,?)', (batch.domain,batch.known_at,batch.id,at,raw))
            con.commit()
        return True

    def metrics(self):
        with self._connection() as con:
            records,size=con.execute('SELECT records,bytes FROM counters WHERE id=1').fetchone()
            return {'retained_records':records,'retained_envelope_bytes':size,
                    'max_records':self.max_records,'max_bytes':self.max_bytes,'max_materialized_batch':self.max_batch}
