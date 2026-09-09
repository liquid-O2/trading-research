"""Transactional append-only runtime events, with content and predecessor checks."""

from contextlib import contextmanager
import hashlib
import json
from pathlib import Path
import sqlite3
from types import MappingProxyType
from typing import Iterator

from trading_research.errors import ContractError, IntegrityError
from trading_research.operations.artifacts import canonical_json


def _freeze(value):
    if isinstance(value, dict):
        return MappingProxyType({key: _freeze(item) for key, item in value.items()})
    if isinstance(value, list):
        return tuple(_freeze(item) for item in value)
    return value


class Journal:
    def __init__(self, path: Path):
        self.path = Path(path)
        self._transaction = None
        self._transaction_events = None
        self._transaction_keys = None
        self._transaction_remaining = 0
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self._connection() as con:
            con.execute("PRAGMA journal_mode=WAL")
            con.execute("CREATE TABLE IF NOT EXISTS events (sequence INTEGER PRIMARY KEY, event_key TEXT UNIQUE NOT NULL, kind TEXT NOT NULL, payload BLOB NOT NULL, previous TEXT, hash TEXT NOT NULL)")
            con.execute("CREATE TRIGGER IF NOT EXISTS no_event_updates BEFORE UPDATE ON events BEGIN SELECT RAISE(ABORT, 'append-only journal'); END")
            con.execute("CREATE TRIGGER IF NOT EXISTS no_event_deletes BEFORE DELETE ON events BEGIN SELECT RAISE(ABORT, 'append-only journal'); END")

    @contextmanager
    def _connection(self) -> Iterator[sqlite3.Connection]:
        con = sqlite3.connect(self.path, timeout=30)
        con.execute("PRAGMA synchronous=FULL")
        try:
            yield con
        finally:
            con.close()

    @staticmethod
    def _hash(sequence: int, key: str, kind: str, payload: bytes, previous: str | None) -> str:
        return hashlib.sha256(canonical_json([sequence, key, kind, payload, previous])).hexdigest()

    @contextmanager
    def transaction(self, *, maximum_new_events: int = 4096):
        """Atomically import a bounded retained history under the SQLite lock.

        The existing journal is fully verified once while the write lock is
        held. Every new event keeps the ordinary content/idempotency/head
        checks. Reads inside this explicit scope return immutable snapshots;
        competing writers cannot alter the verified prefix. Ordinary live
        append/read calls retain their per-call durable behavior.
        """
        if (self._transaction is not None or type(maximum_new_events) is not int
                or not 1 <= maximum_new_events <= 16384):
            raise ContractError("journal import requires one bounded nonnested transaction")
        with self._connection() as con:
            con.execute("BEGIN IMMEDIATE")
            events = self._read_connection(con)
            frozen = [_freeze(event) for event in events]
            keys = {event["key"]: event for event in frozen}
            self._transaction = con
            self._transaction_events = frozen
            self._transaction_keys = keys
            self._transaction_remaining = maximum_new_events
            try:
                yield self
                con.commit()
            except BaseException:
                con.rollback()
                raise
            finally:
                self._transaction = None
                self._transaction_events = None
                self._transaction_keys = None
                self._transaction_remaining = 0

    def append(self, *, key: str, kind: str, payload: dict, expected_head: str | None = None,
               check_head: bool = False) -> tuple[str, bool]:
        if not key or not kind:
            raise ContractError("journal event needs immutable identity and type")
        raw = canonical_json(payload)
        if self._transaction is not None:
            old = self._transaction_keys.get(key)
            if old is not None:
                if old["kind"] != kind or canonical_json(old["payload"]) != raw:
                    raise IntegrityError("journal idempotency key reused with different content")
                return old["hash"], False
            if self._transaction_remaining == 0:
                raise ContractError("bounded journal import event budget exhausted")
            events = self._transaction_events
            sequence, previous = len(events) + 1, events[-1]["hash"] if events else None
            if check_head and previous != expected_head:
                raise ContractError("critical state changed before its atomic commit")
            value = self._hash(sequence, key, kind, raw, previous)
            self._transaction.execute("INSERT INTO events VALUES (?,?,?,?,?,?)",
                                      (sequence, key, kind, raw, previous, value))
            event = _freeze({"sequence": sequence, "key": key, "kind": kind,
                            "payload": json.loads(raw), "previous": previous, "hash": value})
            events.append(event); self._transaction_keys[key] = event
            self._transaction_remaining -= 1
            return value, True
        with self._connection() as con:
            con.execute("BEGIN IMMEDIATE")
            old = con.execute("SELECT kind,payload,hash FROM events WHERE event_key=?", (key,)).fetchone()
            if old is not None:
                if old[:2] != (kind, raw):
                    raise IntegrityError("journal idempotency key reused with different content")
                con.rollback()
                return old[2], False
            head = con.execute("SELECT sequence,hash FROM events ORDER BY sequence DESC LIMIT 1").fetchone()
            sequence, previous = (head[0] + 1, head[1]) if head else (1, None)
            if check_head and previous != expected_head:
                raise ContractError("critical state changed before its atomic commit")
            value = self._hash(sequence, key, kind, raw, previous)
            con.execute("INSERT INTO events VALUES (?,?,?,?,?,?)", (sequence, key, kind, raw, previous, value))
            con.commit()
            return value, True

    def read(self) -> tuple[dict, ...]:
        if self._transaction is not None:
            return tuple(self._transaction_events)
        with self._connection() as con:
            con.execute("BEGIN")
            return self._read_connection(con)

    def _read_connection(self, con) -> tuple[dict, ...]:
        result, previous = [], None
        for sequence, key, kind, raw, prev, value in con.execute("SELECT * FROM events ORDER BY sequence"):
            if (sequence != len(result) + 1 or prev != previous
                    or self._hash(sequence, key, kind, raw, prev) != value):
                raise IntegrityError("runtime journal content/order/hash mismatch")
            result.append({"sequence": sequence, "key": key, "kind": kind,
                           "payload": json.loads(raw), "previous": prev, "hash": value})
            previous = value
        return tuple(result)
