"""Native prefix-cache controls use actual disposable Parquet members."""
from copy import deepcopy
from datetime import date
import csv
import json

import pyarrow as pa
import pyarrow.parquet as pq
import pytest

from trading_research.research.method_pack.clocks import et_ns
from trading_research.research.method_pack.empirical_native import WindowPrefixResolver, native_object, prefix_minute_coverage
from trading_research.research.method_pack.native_resolution import NativeEvidenceError
from trading_research.research.method_pack.native_windows import collect_window

MINUTE = 60_000_000_000
START = et_ns(date(2026, 1, 15), 10)
DATASET = 'quantpad/cme__nq-continuous-futures__ohlcv-1m'


@pytest.fixture
def window(tmp_path):
    path = tmp_path / DATASET / 'case.parquet'
    path.parent.mkdir(parents=True)
    rows = [{'t': (START+i*MINUTE)//1_000_000, 'o': 100.+i,
             'h': 102.+i, 'l': 99.+i, 'c': 101.+i, 'v': 10,
             'instrument_id': 42} for i in range(10)]
    pq.write_table(pa.Table.from_pylist(rows), path, row_group_size=2)
    manifest = tmp_path/'manifests/files.csv'
    manifest.parent.mkdir()
    with manifest.open('w') as handle:
        writer = csv.DictWriter(handle, fieldnames=['dataset_id', 'archive_path'])
        writer.writeheader()
        writer.writerow({'dataset_id': DATASET, 'archive_path': path.relative_to(tmp_path).as_posix()})
    definitions = tmp_path/'derived/continuous-futures__instrument-and-roll-maps/nq-instruments.json'
    definitions.parent.mkdir(parents=True)
    definitions.write_text(json.dumps([{'instrument_id': 42, 'root': 'NQ', 'raw_symbol': 'NQH6',
                                       'min_price_increment': '.25', 'first_definition_ns': START-1}]))
    return collect_window(tmp_path, DATASET, START, START+10*MINUTE, 42, required='ohlcv')


def test_exact_prefix_produces_existing_typed_native_bar(window):
    resolver = WindowPrefixResolver([window])
    rows = window.rows[:5]
    obj, result = native_object(resolver, rows, object_id='bar', recipe_id='O004',
        method_id='GB-FAIL', branch='previous_hour', instrument_id=42,
        start=START, end=START+5*MINUTE, inputs={'kind':'time','size_minutes':5})
    assert result.coverage_ok is True
    assert result.value['O'] == 100 and result.value['C'] == 105
    assert result.known_at == START+5*MINUTE
    assert obj['raw_member_locators'][0]['row_end'] == 5


def test_missing_minute_does_not_borrow_window_coverage(window):
    resolver = WindowPrefixResolver([window])
    rows = [r for i, r in enumerate(window.rows[:5]) if i != 2]
    resolved = resolver.resolve(resolver.locators_for(rows), instrument_id=42,
        start_ns=START, end_ns=START+5*MINUTE, use_at=START+5*MINUTE)
    assert resolved.coverage_ok is None
    assert resolved.missing_intervals == ((START+2*MINUTE, START+3*MINUTE),)


@pytest.mark.parametrize('mutation', ['hash','dataset','future','instrument','duplicate','uncollected'])
def test_cache_rejects_false_membership_and_availability(window, mutation):
    resolver = WindowPrefixResolver([window])
    locators = resolver.locators_for(window.rows[:5])
    args = dict(instrument_id=42, start_ns=START, end_ns=START+5*MINUTE, use_at=START+5*MINUTE)
    if mutation == 'hash': locators[0]['sha256'] = '0'*64
    if mutation == 'dataset': locators[0]['dataset_id'] = 'foreign'
    if mutation == 'future': args['use_at'] -= 1
    if mutation == 'instrument': args['instrument_id'] = 99
    if mutation == 'duplicate': locators += deepcopy(locators)
    if mutation == 'uncollected': locators[0]['row_end'] = 11
    with pytest.raises(NativeEvidenceError): resolver.resolve(locators, **args)


def test_source_change_invalidates_existing_cache_and_new_cache(window):
    resolver = WindowPrefixResolver([window])
    path = window.resolver.root/DATASET/'case.parquet'
    rows = pq.read_table(path).to_pylist()
    rows[-1]['c'] = 110.
    pq.write_table(pa.Table.from_pylist(rows), path)
    with pytest.raises(NativeEvidenceError, match='changed'):
        resolver.resolve(resolver.locators_for(window.rows[:5]), instrument_id=42,
                         start_ns=START, end_ns=START+5*MINUTE)
    with pytest.raises(NativeEvidenceError, match='changed'):
        WindowPrefixResolver([window])


def test_definition_change_cannot_reuse_collected_identity(window):
    resolver = WindowPrefixResolver([window])
    path = window.resolver.root/'derived/continuous-futures__instrument-and-roll-maps/nq-instruments.json'
    row = json.loads(path.read_text())[0]
    row['min_price_increment'] = '.5'
    path.write_text(json.dumps([row]))
    with pytest.raises(NativeEvidenceError, match='definition changed'):
        resolver.resolve(resolver.locators_for(window.rows[:5]), instrument_id=42,
                         start_ns=START, end_ns=START+5*MINUTE)


@pytest.mark.parametrize('day', [date(2024,3,10),date(2024,11,3),date(2026,1,15)])
def test_fast_utc_grid_matches_native_DST_gap_and_fold_coverage(day):
    from trading_research.research.method_pack.native_windows import _minute_coverage
    start,end=et_ns(day,0),et_ns(day,5)
    rows=[{'start':at,'end':at+MINUTE,'complete':True,'O':1,'H':2,'L':0,'C':1,'V':1}
          for at in range(start,end,MINUTE)]
    # One missing observation checks the exact missing key through both DST
    # transitions as well as ordinary sessions.
    rows.pop(len(rows)//2)
    old=_minute_coverage(rows,start,end)
    new=prefix_minute_coverage(rows,start,end)
    assert old[0]==new[0] and old[1]==new[1] and not old[2] and not new[2]
