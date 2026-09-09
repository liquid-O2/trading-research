"""Clock-driven, durable calendar applications with atomic internal JSON state.

Reducers must be pure: return the next owner state without external effects.
The database commits that state and an application record in one transaction.
This API cannot promise exactly-once order sends or arbitrary side effects.
"""

from contextlib import contextmanager
import json
from pathlib import Path
import sqlite3

from trading_research.errors import ContractError, DependencyUnavailable, IntegrityError
from trading_research.foundations.intervals import CalendarEvent, EVENT_PRIORITY, IntervalGraph, _name
from trading_research.foundations.time import timestamp
from trading_research.operations.artifacts import canonical_json, digest


def _state_json(value):
    def check(v):
        if type(v) is dict:
            if any(type(k) is not str for k in v):
                raise ContractError('consumer JSON state requires string keys')
            for child in v.values():
                check(child)
        elif type(v) is list:
            for child in v:
                check(child)
        elif type(v) not in (str, int, float, bool, type(None)):
            raise ContractError('consumer state must contain only JSON values')
    if type(value) is not dict:
        raise ContractError('consumer state must be a JSON object')
    check(value)
    try:
        return json.dumps(value, sort_keys=True, separators=(',', ':'), allow_nan=False)
    except (ValueError, TypeError) as exc:
        raise ContractError('consumer state is not finite JSON') from exc


class TimerJournal:
    def __init__(self, path):
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        self._db = sqlite3.connect(path, timeout=5, isolation_level=None)
        self._db.row_factory = sqlite3.Row
        self._db.execute('PRAGMA synchronous=FULL')
        self._db.execute('PRAGMA foreign_keys=ON')
        schema = '''
            CREATE TABLE IF NOT EXISTS meta (key TEXT PRIMARY KEY, value TEXT NOT NULL);
            CREATE TABLE IF NOT EXISTS plans (
                scope TEXT PRIMARY KEY, graph_id TEXT NOT NULL, known_at INTEGER NOT NULL,
                installed_at INTEGER NOT NULL, payload TEXT NOT NULL);
            CREATE TABLE IF NOT EXISTS plan_history (
                sequence INTEGER PRIMARY KEY AUTOINCREMENT, scope TEXT NOT NULL,
                graph_id TEXT NOT NULL, installed_at INTEGER NOT NULL, payload TEXT NOT NULL);
            CREATE TABLE IF NOT EXISTS events (
                event_id TEXT PRIMARY KEY, logical_id TEXT NOT NULL, scope TEXT NOT NULL,
                owner TEXT NOT NULL, action_key TEXT NOT NULL, priority INTEGER NOT NULL,
                effective_at INTEGER NOT NULL, known_at INTEGER NOT NULL, due_at INTEGER NOT NULL,
                status TEXT NOT NULL CHECK(status IN ('pending','applied','superseded')),
                payload TEXT NOT NULL);
            CREATE TABLE IF NOT EXISTS transitions (
                sequence INTEGER PRIMARY KEY AUTOINCREMENT, at INTEGER NOT NULL,
                event_id TEXT NOT NULL REFERENCES events(event_id), status TEXT NOT NULL,
                graph_id TEXT NOT NULL, reason TEXT NOT NULL);
            CREATE TABLE IF NOT EXISTS owner_states (owner TEXT PRIMARY KEY, payload TEXT NOT NULL);
            CREATE TABLE IF NOT EXISTS applications (
                sequence INTEGER PRIMARY KEY AUTOINCREMENT, logical_id TEXT NOT NULL UNIQUE,
                event_id TEXT NOT NULL UNIQUE REFERENCES events(event_id), applied_at INTEGER NOT NULL,
                due_at INTEGER NOT NULL, state_after TEXT NOT NULL, application_id TEXT NOT NULL UNIQUE);
            CREATE INDEX IF NOT EXISTS pending_events ON events(status,due_at,priority,effective_at);
        '''
        try:
            self._db.execute('BEGIN IMMEDIATE')
            tables = {r[0] for r in self._db.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")}
            if tables:
                expected = {'meta', 'plans', 'plan_history', 'events', 'transitions', 'owner_states', 'applications'}
                if tables != expected:
                    raise IntegrityError('existing database is not a timer journal')
                row = self._db.execute("SELECT value FROM meta WHERE key='schema'").fetchone()
                if row is None or row[0] != 'calendar-timer-journal-v1':
                    raise IntegrityError('unknown timer journal schema')
                if self._db.execute("SELECT value FROM meta WHERE key='clock'").fetchone() is None:
                    raise IntegrityError('existing timer journal lost its committed clock')
            for statement in schema.split(';'):
                if statement.strip():
                    self._db.execute(statement)
            self._db.execute("INSERT OR IGNORE INTO meta VALUES ('schema', 'calendar-timer-journal-v1')")
            self._db.execute("INSERT OR IGNORE INTO meta VALUES ('clock', ?)", (str(-(2 ** 63)),))
            timestamp(int(self._db.execute("SELECT value FROM meta WHERE key='clock'").fetchone()[0]))
            self._db.execute('COMMIT')
            self._db.execute('PRAGMA journal_mode=WAL')
        except BaseException:
            if self._db.in_transaction:
                self._db.execute('ROLLBACK')
            self._db.close()
            raise

    def close(self):
        self._db.close()

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        self.close()

    @contextmanager
    def _transaction(self, at):
        timestamp(at)
        self._db.execute('BEGIN IMMEDIATE')
        try:
            previous = int(self._db.execute("SELECT value FROM meta WHERE key='clock'").fetchone()[0])
            if at < previous:
                raise ContractError('timer journal clock cannot move backward across restart')
            yield
            self._db.execute("UPDATE meta SET value=? WHERE key='clock'", (str(at),))
            self._db.execute('COMMIT')
        except BaseException:
            self._db.execute('ROLLBACK')
            raise

    def _transition(self, event_id, status, at, graph_id, reason):
        self._db.execute('UPDATE events SET status=? WHERE event_id=?', (status, event_id))
        self._db.execute('INSERT INTO transitions(at,event_id,status,graph_id,reason) VALUES (?,?,?,?,?)',
                         (at, event_id, status, graph_id, reason))

    def _applied(self, logical_id):
        return self._db.execute('SELECT 1 FROM applications WHERE logical_id=?', (logical_id,)).fetchone() is not None

    def _enqueue(self, event, *, at, graph_id):
        payload = canonical_json(event.record()).decode()
        old = self._db.execute('SELECT * FROM events WHERE event_id=?', (event.event_id,)).fetchone()
        if old is not None:
            if old['payload'] != payload:
                raise IntegrityError('immutable event ID has different contents')
            if old['status'] != 'superseded' or self._applied(event.logical_id):
                return
            self._db.execute('UPDATE events SET due_at=? WHERE event_id=?',
                             (max(at, event.effective_at, event.known_at), event.event_id))
            self._transition(event.event_id, 'pending', at, graph_id, 'explicitly reintroduced unapplied action')
            return
        self._db.execute('''INSERT INTO events(event_id,logical_id,scope,owner,action_key,priority,
                            effective_at,known_at,due_at,status,payload) VALUES (?,?,?,?,?,?,?,?,?,?,?)''',
            (event.event_id, event.logical_id, event.scope, event.owner, event.key, EVENT_PRIORITY[event.kind],
             event.effective_at, event.known_at, max(at, event.effective_at, event.known_at), 'pending', payload))
        self._transition(event.event_id, 'pending', at, graph_id, 'scheduled independently of market data')

    def _reconcile(self, old, new, graph, at):
        subject = new if new is not None else old
        event = CalendarEvent(graph.scope, 'reconcile:' + subject.key + ':' + graph.version,
            subject.owner, 'reconcile', at, at, (graph.version,),
            (('logical_action', subject.logical_id), ('old_event', old.event_id if old else ''),
             ('new_event', new.event_id if new else ''), ('effective_at', str(subject.effective_at)),
             ('reason', 'past, removed, or already applied calendar action requires consumer reconciliation')))
        self._enqueue(event, at=at, graph_id=graph.version)

    def install(self, graph, *, at):
        if type(graph) is not IntervalGraph:
            raise ContractError('timer installation requires an immutable compiled graph')
        if timestamp(at) < graph.known_at:
            raise DependencyUnavailable('calendar graph was not available at installation time')
        snapshot = {'scope': graph.scope, 'graph_id': graph.version, 'known_at': graph.known_at,
                    'interval_versions': {name: node.version for name, node in graph.intervals.items()},
                    'events': [e.record() for e in graph.events], 'graph': graph.record()}
        payload = canonical_json(snapshot).decode()
        with self._transaction(at):
            previous = self._db.execute('SELECT * FROM plans WHERE scope=?', (graph.scope,)).fetchone()
            if previous is not None and previous['graph_id'] == graph.version:
                if previous['payload'] != payload:
                    raise IntegrityError('immutable graph ID has different contents')
                return False
            if previous is not None and graph.known_at <= previous['known_at']:
                raise ContractError('changed calendar requires a strictly newer knowledge version')
            old_events = {}
            if previous is not None:
                old_snapshot = json.loads(previous['payload'])
                old_graph = IntervalGraph.from_record(old_snapshot['graph'])
                if (old_graph.version != previous['graph_id'] or old_graph.scope != graph.scope
                        or old_graph.known_at != previous['known_at']
                        or [e.record() for e in old_graph.events] != old_snapshot['events']):
                    raise IntegrityError('persisted calendar plan disagrees with its definition')
                old_events = {e.logical_id: e for e in old_graph.events}
            new_events = {e.logical_id: e for e in graph.events}
            if previous is not None:
                notice = CalendarEvent(graph.scope, 'revision:' + graph.version, 'calendar', 'calendar_revision',
                    at, at, (previous['graph_id'], graph.version),
                    (('old_graph', previous['graph_id']), ('new_graph', graph.version)))
                self._enqueue(notice, at=at, graph_id=graph.version)
            for logical in sorted(set(old_events) | set(new_events)):
                old, new = old_events.get(logical), new_events.get(logical)
                if old is not None and new is not None and old.event_id == new.event_id:
                    continue
                if old is not None:
                    row = self._db.execute('SELECT status FROM events WHERE event_id=?', (old.event_id,)).fetchone()
                    if row is not None and row['status'] == 'pending':
                        self._transition(old.event_id, 'superseded', at, graph.version, 'known calendar revision')
                if previous is not None and (new is None or new.effective_at <= at
                        or old is not None and old.effective_at <= at or self._applied(logical)):
                    self._reconcile(old, new, graph, at)
                elif new is not None:
                    self._enqueue(new, at=at, graph_id=graph.version)
            self._db.execute('INSERT OR REPLACE INTO plans VALUES (?,?,?,?,?)',
                             (graph.scope, graph.version, graph.known_at, at, payload))
            self._db.execute('INSERT INTO plan_history(scope,graph_id,installed_at,payload) VALUES (?,?,?,?)',
                             (graph.scope, graph.version, at, payload))
        return True

    def next_due(self):
        return self._db.execute("SELECT min(due_at) FROM events WHERE status='pending'").fetchone()[0]

    def state(self, owner):
        _name(owner)
        row = self._db.execute('SELECT payload FROM owner_states WHERE owner=?', (owner,)).fetchone()
        return {} if row is None else json.loads(row['payload'])

    def process_due(self, at, reducer, *, limit=1000):
        """Apply due timers without market input; one transaction commits each batch.

        The reducer receives a detached owner state and an immutable event. It
        must perform no side effects; any exception rolls the whole batch back.
        """
        if type(limit) is not int or not 0 < limit < 2 ** 63 or not callable(reducer):
            raise ContractError('timer processing requires a pure reducer and positive finite batch size')
        results = []
        with self._transaction(at):
            rows = self._db.execute('''SELECT * FROM events WHERE status='pending' AND due_at<=?
                ORDER BY due_at,priority,effective_at,owner,action_key,event_id LIMIT ?''', (at, limit)).fetchall()
            for row in rows:
                event = CalendarEvent.from_record(json.loads(row['payload']))
                if (event.event_id != row['event_id'] or event.logical_id != row['logical_id']
                        or (event.scope, event.owner, event.key, EVENT_PRIORITY[event.kind], event.effective_at, event.known_at)
                        != (row['scope'], row['owner'], row['action_key'], row['priority'], row['effective_at'], row['known_at'])
                        or not max(event.effective_at, event.known_at) <= row['due_at'] <= at):
                    raise IntegrityError('timer payload identity mismatch')
                if self._applied(event.logical_id):
                    self._transition(event.event_id, 'superseded', at, '', 'logical action already committed')
                    continue
                state = reducer(self.state(event.owner), event)
                state_json = _state_json(state)
                record = {'event_id': event.event_id, 'logical_id': event.logical_id, 'applied_at': at,
                          'due_at': row['due_at'], 'state_after': json.loads(state_json)}
                record['application_id'] = digest(record)
                self._db.execute('INSERT OR REPLACE INTO owner_states VALUES (?,?)', (event.owner, state_json))
                self._db.execute('''INSERT INTO applications(logical_id,event_id,applied_at,due_at,state_after,application_id)
                                    VALUES (?,?,?,?,?,?)''',
                    (event.logical_id, event.event_id, at, row['due_at'], state_json, record['application_id']))
                self._transition(event.event_id, 'applied', at, '', 'consumer state and application committed atomically')
                results.append(record)
        return tuple(results)

    def applications(self):
        rows = self._db.execute('''SELECT a.*,e.payload FROM applications a JOIN events e ON a.event_id=e.event_id
                                  ORDER BY a.sequence''').fetchall()
        return tuple({**dict(r), 'payload': json.loads(r['payload']), 'state_after': json.loads(r['state_after'])}
                     for r in rows)

    def history(self):
        return tuple(dict(r) for r in self._db.execute('SELECT * FROM transitions ORDER BY sequence').fetchall())

    def plans(self):
        return tuple({**dict(r), 'payload': json.loads(r['payload'])}
                     for r in self._db.execute('SELECT * FROM plan_history ORDER BY sequence').fetchall())
