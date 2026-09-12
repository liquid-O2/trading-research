"""Bounded, immutable native windows for retrospective comparison selectors.

This cache accepts only rows already collected by the verified native adapter.
It resolves exact physical membership, rechecks file identities, and recomputes
clock coverage for each requested prefix. It cannot certify an arbitrary
manifest, substitute supplied values, or borrow a later window's coverage.
"""
from __future__ import annotations

from collections import defaultdict
from pathlib import Path
from types import MappingProxyType

from .native_resolution import NativeEvidenceError, NativeResolver, ResolvedMembers, _stat_signature, ns
from .native_windows import NativeWindow, _minute_coverage
from .objects import native_boundary  # installs the accepted domain producers
from .protocol import jsonable

MINUTE = 60_000_000_000


def prefix_minute_coverage(rows,start,end):
    """Exact UTC-minute equivalent of the native one-minute coverage guard.

    Native minute starts are integer UTC minute keys. New York DST changes
    local labels, not this contiguous UTC grid; enumerating every wall-clock
    minute of three dates for every one-minute object is unnecessary.
    """
    index={};missing=[];mismatch=[]
    if start%MINUTE or end%MINUTE:mismatch.append('partial_minute_interval')
    for row in rows:
        at=row['start']
        if at in index:mismatch.append('duplicate_native_minute');continue
        index[at]=row
    for at in range(start,end,MINUTE):
        row=index.get(at)
        if row is None or row['end']!=at+MINUTE or row.get('complete') is not True:
            missing.append((at,at+MINUTE))
        elif row['V']<0 or row['H']<max(row['O'],row['L'],row['C']) or row['L']>min(row['O'],row['H'],row['C']):
            mismatch.append('invalid_native_ohlcv')
    return index,missing,mismatch


def member_locators(rows, digests):
    """Compress actual physical row IDs without dropping duplicate market events."""
    grouped = defaultdict(list)
    for row in rows:
        grouped[(row['source_file'], row['dataset_id'])].append(row['source_row'])
    out = []
    for (path, dataset), indices in sorted(grouped.items()):
        if len(set(indices)) != len(indices):
            raise NativeEvidenceError('duplicate physical member in empirical object')
        runs = []
        for index in sorted(indices):
            if runs and runs[-1][1] == index:
                runs[-1][1] += 1
            else:
                runs.append([index, index + 1])
        out.extend({'source_file': path, 'dataset_id': dataset,
                    'sha256': digests[path], 'row_start': lo, 'row_end': hi}
                   for lo, hi in runs)
    return out


class WindowPrefixResolver(NativeResolver):
    """Application-owned cache with exact membership and freshness admission."""

    def __init__(self, windows: list[NativeWindow]):
        if not windows:
            raise NativeEvidenceError('empirical cache requires a verified native window')
        roots = {w.resolver.root for w in windows}
        if len(roots) != 1:
            raise NativeEvidenceError('mixed data roots')
        super().__init__(next(iter(roots)))
        self.windows = tuple(windows)
        self.members = {}
        self.identities = {}
        self.definitions = {}
        # Every row in a collected window already names an immutable source
        # file. Resolve each distinct path once, not once per market minute.
        # Repeated realpath traversal on mounted archives dominates long
        # lookbacks without adding any membership or freshness guarantee.
        canonical_paths = {}
        for window in windows:
            if window.resolved is not None:
                self.definitions[(window.dataset_id, str(window.instrument_id))] = window.instrument_definition
            for locator in window.locators:
                path = str(Path(locator['source_file']).resolve())
                verified = window.resolver._digests.get(Path(path))
                if verified is None or verified[1] != locator['sha256'] or _stat_signature(Path(path)) != verified[0]:
                    raise NativeEvidenceError('native source changed between collection and cache construction')
                identity = (locator['dataset_id'], locator['sha256'], verified[0])
                if path in self.identities and self.identities[path] != identity:
                    raise NativeEvidenceError('cache has conflicting native source identities')
                self.identities[path] = identity
            for row in window.rows:
                source = row['source_file']
                if source not in canonical_paths:
                    canonical_paths[source] = str(Path(source).resolve())
                key = (canonical_paths[source], row['source_row'])
                if key in self.members and self.members[key] != row:
                    raise NativeEvidenceError('same native member has contradictory observations')
                self.members[key] = row

    def resolve(self, locators, *, instrument_id, start_ns, end_ns, as_of=None, use_at=None):
        start, end = ns(start_ns, 'start'), ns(end_ns, 'end')
        if end <= start or instrument_id is None or not locators:
            raise NativeEvidenceError('positive identified native interval required')
        if as_of is not None and ns(as_of, 'as_of') < end:
            raise NativeEvidenceError('native formation exceeds snapshot')
        if use_at is not None and ns(use_at, 'use_at') < end:
            raise NativeEvidenceError('native formation exceeds use')
        selected, seen, datasets = [], set(), set()
        for locator in locators:
            path = str((self.root / locator['source_file']).resolve())
            identity = self.identities.get(path)
            if identity is None or not Path(path).is_relative_to(self.root):
                raise NativeEvidenceError('locator is not in the verified empirical window')
            dataset, digest, signature = identity
            if (locator.get('dataset_id'), locator.get('sha256')) != (dataset, digest):
                raise NativeEvidenceError('empirical native dataset/hash mismatch')
            if _stat_signature(Path(path)) != signature:
                raise NativeEvidenceError('native source changed after empirical collection')
            lo = locator.get('source_row', locator.get('row_start'))
            hi = lo + 1 if 'source_row' in locator and type(lo) is int else locator.get('row_end')
            if type(lo) is not int or type(hi) is not int or lo < 0 or hi <= lo:
                raise NativeEvidenceError('invalid physical locator interval')
            datasets.add(dataset)
            for index in range(lo, hi):
                key = path, index
                if key in seen:
                    raise NativeEvidenceError('duplicate physical native locator')
                seen.add(key)
                row = self.members.get(key)
                if row is None:
                    raise NativeEvidenceError('locator borrows uncollected physical member')
                at = row.get('start', row.get('event_ns'))
                until = row.get('end', at + 1)
                if str(row['instrument_id']) != str(instrument_id) or at < start or until > end:
                    raise NativeEvidenceError('native member has foreign instrument or interval')
                if row.get('known_at') is not None and use_at is not None and row['known_at'] > use_at:
                    raise NativeEvidenceError('native member unavailable at use')
                selected.append(row)
        if len(datasets) != 1:
            raise NativeEvidenceError('empirical object must use one native dataset')
        dataset = next(iter(datasets))
        selected.sort(key=lambda r: (r.get('start', r.get('event_ns')), r['source_file'], r['source_row']))
        if dataset.endswith('ohlcv-1m'):
            _, missing, mismatch = prefix_minute_coverage(selected, start, end)
            coverage = True if selected and not missing and not mismatch else None
        else:
            # A tape subset is covered only by an independently reconciled exact
            # window with exactly the same physical members. No extrema shortcut.
            matching = [w for w in self.windows if w.dataset_id == dataset
                        and str(w.instrument_id) == str(instrument_id)
                        and w.start_ns == start and w.end_ns == end
                        and {(r['source_file'], r['source_row']) for r in w.rows} == seen]
            coverage = matching[0].coverage_ok if matching else None
            missing = list(matching[0].missing_intervals) if matching else []
        times = [r.get('known_at') for r in selected]
        known = max(times) if times and all(t is not None for t in times) else None
        definition = self.definitions.get((dataset, str(instrument_id)))
        if definition is not None:
            definition_path = Path(definition.source_file)
            signature, digest = self._digest(definition_path)
            if digest != definition.sha256:
                raise NativeEvidenceError('instrument definition changed after native collection')
        if definition is not None and definition.known_at is not None and use_at is not None and definition.known_at > use_at:
            raise NativeEvidenceError('instrument definition unavailable at use')
        return ResolvedMembers(tuple(selected), instrument_id, start, end, known, coverage,
                               tuple(MappingProxyType(dict(l)) for l in locators),
                               tuple(tuple(x) for x in missing), definition)

    def locators_for(self, rows):
        return member_locators(rows, {path: value[1] for path, value in self.identities.items()})


def native_object(resolver, rows, *, object_id, recipe_id, method_id, branch,
                  instrument_id, start, end, inputs=None, author='empirical-research',
                  source_version='empirical-v1'):
    """Create a replayable C01 object and run its existing complete typed producer."""
    obj = {'object_id': object_id, 'recipe_id': recipe_id, 'method_id': method_id,
           'branch_scope': [branch], 'author': author, 'instrument_id': instrument_id,
           'parent_ids': [], 'source_ref': 'planning/phase-1-live/SOURCE_CALIBRATION_DISCOVERY_HANDOFF.md',
           'source_version': source_version, 'value': {}, 'units': {},
           'formation_start': start, 'formation_end': end, 'as_of': end, 'known_at': end,
           'state': 'computed', 'hole_ids': [], 'evidence_ids': [],
           'inputs': dict(inputs or {}, use_at=end),
           'raw_member_locators': resolver.locators_for(rows)}
    if not obj['raw_member_locators']:
        raise NativeEvidenceError('empty native object has no observed members')
    result = native_boundary.run_native_object(obj, resolver)
    # Keep the input envelope as computed so C01 reparses/recomputes it. The
    # separate result is the validated actual output, including typed holes.
    return obj, result
