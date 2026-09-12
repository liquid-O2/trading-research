"""Immutable native member resolution. Locators identify observations, never values.

The resolver is a trusted application dependency, not an episode-manifest field.
File ownership and independently audited coverage may be injected by the runner.
A file's first/last observation is deliberately not continuous tape coverage.
"""
from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
from pathlib import Path
from decimal import Decimal
from bisect import bisect_right
import re
from types import MappingProxyType
from typing import Mapping

from . import adapters
from .logic import dec


class NativeEvidenceError(ValueError):
    pass


def ns(value, label):
    if type(value) is not int or not -(2**63) <= value < 2**63:
        raise NativeEvidenceError(f'{label} must be int64 UTC nanoseconds')
    return value


def file_digest(path):
    digest = sha256()
    with Path(path).open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            digest.update(block)
    return digest.hexdigest()


@dataclass(frozen=True)
class NativeInstrumentDefinition:
    definition_id: str
    instrument_id: str | int
    tick_size: Decimal
    known_at: int | None
    source_file: str
    sha256: str
    source_row: int
    root: str
    raw_symbol: str | None

    @property
    def available_at(self):
        return self.known_at


def instrument_definition_from_record(row, *, source_file, source_row, digest):
    """Normalize an actual instrument-map row, never a manifest price setting."""
    identifier = row.get('instrument_id')
    tick = dec(row.get('min_price_increment', row.get('tick_size')))
    if identifier is None or tick is None or not tick.is_finite() or tick <= 0:
        raise NativeEvidenceError('invalid native instrument definition')
    known = row.get('first_definition_ns')
    if known is not None:
        ns(known, 'instrument definition availability')
    return NativeInstrumentDefinition(f'{source_file}#{source_row}@{digest}', identifier,
        tick, known, str(source_file), digest, source_row, str(row.get('root', '')),
        row.get('raw_symbol'))


def _stat_signature(path):
    stat = path.stat()
    return stat.st_dev, stat.st_ino, stat.st_size, stat.st_mtime_ns, stat.st_ctime_ns


def _selected_source_rows(path, dataset, ranges):
    """Read each selected physical row once, skipping unrelated Parquet groups."""
    starts = [start for start, end in ranges]
    def selected(index):
        at = bisect_right(starts, index) - 1
        return at >= 0 and index < ranges[at][1]
    if path.suffix != '.parquet':
        for index, row in enumerate(adapters.iter_source_rows(path, dataset_id=dataset)):
            if index >= ranges[-1][1]:
                break
            if selected(index):
                yield index, row
        return
    import pyarrow as pa
    import pyarrow.parquet as pq
    parquet = pq.ParquetFile(path)
    offset = 0
    for group in range(parquet.num_row_groups):
        count = parquet.metadata.row_group(group).num_rows
        stop = offset + count
        if any(first < stop and last > offset for first, last in ranges):
            index = offset
            for batch in parquet.iter_batches(batch_size=65536, row_groups=[group]):
                units = {}
                for column_index, field in enumerate(batch.schema):
                    if pa.types.is_timestamp(field.type):
                        units[field.name] = {'source_unit': field.type.unit, 'timezone': field.type.tz, 'normalized_unit': 'ns'}
                        column = batch.column(column_index).cast(pa.timestamp('ns', tz=field.type.tz)).cast(pa.int64())
                        batch = batch.set_column(column_index, field.name, column)
                for row in batch.to_pylist():
                    if selected(index):
                        if units:
                            row['_timestamp_units'] = units
                        yield index, row
                    index += 1
        offset = stop
        if offset >= ranges[-1][1]:
            break


@dataclass(frozen=True)
class ResolvedMembers:
    members: tuple[Mapping, ...]
    instrument_id: str | int
    start_ns: int
    end_ns: int
    known_at: int | None
    coverage_ok: bool | None
    locators: tuple[Mapping, ...]
    missing_intervals: tuple[tuple[int, int], ...] = ()
    instrument_definition: NativeInstrumentDefinition | None = None

    def rows(self):
        return [dict(row) for row in self.members]


class NativeResolver:
    def __init__(self, data_root='/workspace/data', *, owned_spans=None, coverage_records=()):
        self.root = Path(data_root).resolve()
        # These are supplied by the application/inventory, never taken from an
        # untrusted object claiming its own file is owned or continuously covered.
        self.owned_spans = owned_spans
        self.coverage_records = tuple(dict(row) for row in coverage_records)
        self._ownership = None
        self._ownership_index = {}
        self._ownership_token = None
        self._manifest_paths = None
        self._digests = {}
        self._definitions = {}

    def _digest(self, path):
        signature = _stat_signature(path)
        cached = self._digests.get(path)
        if cached is None or cached[0] != signature:
            digest = file_digest(path)
            if _stat_signature(path) != signature:
                raise NativeEvidenceError('raw source changed during digest verification')
            cached = signature, digest
            self._digests[path] = cached
        return cached

    def _owned(self, path, dataset, start, end):
        if self.owned_spans is not None:
            spans = self.owned_spans
        elif dataset == 'quantpad/cme__nq-continuous-futures__mbp-1':
            if self._ownership is None:
                self._ownership = adapters.ownership_manifest(self.root)['owned_spans']
            spans = self._ownership
        else:
            if self._manifest_paths is None:
                counts = {}
                for row in adapters._manifest_rows(self.root):
                    relative = row.get('archive_path')
                    counts[relative] = counts.get(relative, 0) + 1
                self._manifest_paths = {key for key, count in counts.items() if count == 1}
            return path.relative_to(self.root).as_posix() in self._manifest_paths
        token = id(spans), len(spans)
        if self._ownership_token != token:
            self._ownership_index = {}
            for span in spans:
                self._ownership_index.setdefault(Path(span['path']).resolve(), []).append(span)
            self._ownership_token = token
        return any(s.get('status', 'owned') != 'hole' and s['start_ns'] <= start and end <= s['end_ns']
                   for s in self._ownership_index.get(path, []))

    def _definition(self, instrument_id, datasets, use_at):
        roots = set()
        for dataset in datasets:
            match = re.search(r'cme__(nq|es|ym|rty)-', dataset)
            if match:
                roots.add(match[1])
        if len(roots) != 1:
            return None
        root = next(iter(roots))
        directory = self.root / 'derived' / 'continuous-futures__instrument-and-roll-maps'
        files = [directory / f'{root}-instruments.{extension}' for extension in ('parquet', 'json', 'csv')]
        existing = [path for path in files if path.is_file()]
        if len(existing) != 1:
            return None
        path = existing[0]
        signature, digest = self._digest(path)
        cache_key = path, signature
        if cache_key not in self._definitions:
            records = {}
            for index, row in enumerate(adapters.iter_source_rows(path)):
                definition = instrument_definition_from_record(row, source_file=str(path), source_row=index, digest=digest)
                records.setdefault(str(definition.instrument_id), []).append(definition)
            if _stat_signature(path) != signature:
                raise NativeEvidenceError('instrument definitions changed during resolution')
            self._definitions[cache_key] = records
        records = self._definitions[cache_key].get(str(instrument_id), [])
        if len(records) != 1:
            return None
        definition = records[0]
        if definition.root and definition.root.lower() != root:
            raise NativeEvidenceError('instrument root conflicts with native dataset')
        if definition.known_at is not None and use_at is not None and definition.known_at > use_at:
            raise NativeEvidenceError('instrument definition available after use')
        return definition

    def resolve(self, locators, *, instrument_id, start_ns, end_ns, as_of=None, use_at=None):
        start, end = ns(start_ns, 'start'), ns(end_ns, 'end')
        if end <= start:
            raise NativeEvidenceError('reversed or empty formation interval')
        if instrument_id is None:
            raise NativeEvidenceError('missing native instrument identity')
        if not isinstance(locators, list) or not locators:
            raise NativeEvidenceError('nonempty structured raw member locators required')
        groups = {}
        for locator in locators:
            if not isinstance(locator, dict):
                raise NativeEvidenceError('raw locator must identify a real file, digest and row/range')
            if not {'source_file', 'dataset_id', 'sha256'} <= locator.keys():
                raise NativeEvidenceError('locator missing file, dataset or immutable sha256')
            path = (self.root / locator['source_file']).resolve()
            if not path.is_relative_to(self.root) or not path.is_file():
                raise NativeEvidenceError('nonexistent or out-of-root raw source')
            dataset = adapters._dataset_for_path(self.root, path)
            if dataset != locator['dataset_id']:
                raise NativeEvidenceError('raw dataset/path identity mismatch')
            if 'source_row' in locator:
                first = locator['source_row']
                stop = first + 1 if type(first) is int else None
            else:
                first, stop = locator.get('row_start'), locator.get('row_end')
            if type(first) is not int or type(stop) is not int or first < 0 or stop <= first:
                raise NativeEvidenceError('locator needs a nonnegative row or half-open row range')
            group = groups.setdefault(path, {'dataset': dataset, 'ranges': [], 'locators': []})
            group['ranges'].append((first, stop))
            group['locators'].append(locator)
        members = []
        for path, group in groups.items():
            dataset = group['dataset']
            ranges = sorted(group['ranges'])
            if any(ranges[i][0] < ranges[i-1][1] for i in range(1, len(ranges))):
                raise NativeEvidenceError('duplicate raw member ownership')
            signature, digest = self._digest(path)
            if any(locator['sha256'] != digest for locator in group['locators']):
                raise NativeEvidenceError('raw source digest mismatch')
            normalizer = (adapters.normalize_ohlcv_row if 'ohlcv-' in dataset else
                          adapters.normalize_mbp1_row if 'mbp-1' in dataset else
                          adapters.normalize_trade_row if 'trades' in dataset else None)
            if normalizer is None:
                raise NativeEvidenceError('native dataset adapter is not supported by this resolver')
            found = 0
            for index, raw in _selected_source_rows(path, dataset, ranges):
                row = normalizer(raw, dataset_id=dataset, source_file=str(path), source_row=index)
                row['dataset_id'] = dataset
                prices = [row.get(k) for k in ('O', 'H', 'L', 'C')] if 'start' in row else [row.get('price')]
                if any(p is not None and not p.is_finite() for p in prices):
                    raise NativeEvidenceError('nonfinite native price')
                if 'start' in row and row.get('complete') is True:
                    if row['H'] < max(row['O'], row['L'], row['C']) or row['L'] > min(row['O'], row['H'], row['C']):
                        raise NativeEvidenceError('inconsistent native OHLC interval')
                    if not row['V'].is_finite() or row['V'] < 0:
                        raise NativeEvidenceError('invalid native bar volume')
                if str(row['instrument_id']) != str(instrument_id):
                    raise NativeEvidenceError('cross-instrument raw member')
                at = row.get('start', row.get('event_ns'))
                until = row.get('end', at + 1)
                if at < start or until > end:
                    raise NativeEvidenceError('raw member outside formation interval')
                if not self._owned(path, dataset, at, until):
                    raise NativeEvidenceError('unowned raw member')
                if as_of is not None:
                    cutoff = ns(as_of, 'snapshot')
                    if at > cutoff or ('end' in row and row['end'] > cutoff):
                        raise NativeEvidenceError('raw member event interval after snapshot')
                if use_at is not None:
                    cutoff = ns(use_at, 'use')
                    if at > cutoff or (row.get('known_at') is not None and row['known_at'] > cutoff):
                        raise NativeEvidenceError('raw member available after use')
                members.append(MappingProxyType(row))
                found += 1
            if found != sum(last-first for first, last in ranges):
                raise NativeEvidenceError('nonexistent raw row locator')
            if _stat_signature(path) != signature:
                raise NativeEvidenceError('raw source changed during resolution')
        times = [row.get('known_at') for row in members]
        known = max(times) if times and all(t is not None for t in times) else None
        coverage = None
        for record in self.coverage_records:
            if str(record.get('instrument_id')) != str(instrument_id):
                continue
            if record.get('start_ns') != start or record.get('end_ns') != end:
                continue
            wanted = {(str((self.root / l['source_file']).resolve()), l['sha256']) for l in locators}
            recorded = {(str((self.root / l['source_file']).resolve()), l['sha256']) for l in record.get('sources', [])}
            if (wanted == recorded and record.get('member_locators') == locators
                    and record.get('coverage_ok') is True and record.get('missing_intervals') == []):
                coverage = True
        definition = self._definition(instrument_id, [g['dataset'] for g in groups.values()], use_at)
        return ResolvedMembers(tuple(members), instrument_id, start, end, known, coverage,
                               tuple(MappingProxyType(dict(l)) for l in locators), instrument_definition=definition)
