"""Physical locator and independently reconciled native-window coverage tests."""
from datetime import date
from decimal import Decimal
from pathlib import Path
import csv
import json

import pytest

from trading_research.research.method_pack.clocks import et_ns
from trading_research.research.method_pack.native_resolution import NativeEvidenceError
from trading_research.research.method_pack.native_windows import collect_window, AuditedWindowResolver

START = et_ns(date(2026, 1, 15), 10)
MINUTE = 60_000_000_000
TRADES = 'quantpad/cme__nq-continuous-futures__trades'
BARS = 'quantpad/cme__nq-continuous-futures__ohlcv-1m'


@pytest.fixture
def market(tmp_path):
    import pyarrow as pa
    import pyarrow.parquet as pq
    files = []
    data = {
        TRADES: [
            {'t': START, 'price': 500., 'size': 1, 'side': 'B', 'instrument_id': 99},
            {'t': START+1, 'price': 100., 'size': 1, 'side': 'B', 'instrument_id': 42},
            {'t': START+10_000_000_000, 'price': 102., 'size': 2, 'side': 'N', 'instrument_id': 42},
            {'t': START+MINUTE, 'price': 501., 'size': 1, 'side': 'B', 'instrument_id': 99},
            {'t': START+MINUTE+1, 'price': 101., 'size': 1, 'side': 'A', 'instrument_id': 42},
        ],
        BARS: [
            {'t': START//1_000_000, 'o': 100., 'h': 102., 'l': 100., 'c': 102., 'v': 3, 'instrument_id': 42},
            {'t': (START+MINUTE)//1_000_000, 'o': 101., 'h': 101., 'l': 101., 'c': 101., 'v': 1, 'instrument_id': 42},
        ],
    }
    for dataset, rows in data.items():
        path = tmp_path / dataset / 'case.parquet'
        path.parent.mkdir(parents=True)
        pq.write_table(pa.Table.from_pylist(rows), path, row_group_size=2)
        files.append({'dataset_id': dataset, 'archive_path': path.relative_to(tmp_path).as_posix()})
    manifest = tmp_path / 'manifests' / 'files.csv'
    manifest.parent.mkdir()
    with manifest.open('w') as handle:
        writer = csv.DictWriter(handle, fieldnames=['dataset_id','archive_path'])
        writer.writeheader(); writer.writerows(files)
    definition = tmp_path / 'derived' / 'continuous-futures__instrument-and-roll-maps' / 'nq-instruments.json'
    definition.parent.mkdir(parents=True)
    definition.write_text(json.dumps([{'instrument_id': 42, 'root': 'NQ', 'raw_symbol': 'NQH6',
                                       'min_price_increment': '0.25', 'first_definition_ns': START-1000}]))
    return tmp_path, data


def _write(root, dataset, rows):
    import pyarrow as pa
    import pyarrow.parquet as pq
    pq.write_table(pa.Table.from_pylist(rows), root / dataset / 'case.parquet', row_group_size=2)


def test_all_physical_rows_and_independent_volume_ohlc_reconcile(market):
    root, _ = market
    window = collect_window(root, TRADES, START, START+2*MINUTE, 42)
    assert window.coverage_ok is True
    assert [r['source_row'] for r in window.rows] == [1,2,4]
    assert [(l['row_start'], l['row_end']) for l in window.locators] == [(1,3),(4,5)]
    assert window.resolved.coverage_ok is True
    assert window.instrument_definition.tick_size == Decimal('.25')
    assert window.rows[1]['signed_size'] is None
    assert window.rows[1]['unknown_size'] == 2
    assert all(check['matched'] for check in window.coverage_evidence['minute_reconciliation'])


def test_missing_minute_cannot_be_certified_by_first_last_or_subset(market):
    root, data = market
    _write(root, BARS, data[BARS][:1])
    window = collect_window(root, TRADES, START, START+2*MINUTE, 42)
    assert window.coverage_ok is None
    assert window.resolved.coverage_ok is None
    assert window.missing_intervals == ((START+MINUTE,START+2*MINUTE),)


def test_missing_trade_revealed_by_independent_native_minute(market):
    root, data = market
    _write(root, TRADES, data[TRADES][:2]+data[TRADES][3:])
    window = collect_window(root, TRADES, START, START+2*MINUTE, 42)
    assert window.coverage_ok is None
    assert any('executed_volume_mismatch' in m['reason'] for m in window.mismatches)
    assert window.resolved.coverage_ok is None


def test_claimed_subset_cannot_reuse_complete_window_coverage(market):
    root, _ = market
    window = collect_window(root, TRADES, START, START+2*MINUTE, 42)
    subset = [dict(window.locators[0])]
    resolved = window.resolver.resolve(subset, instrument_id=42, start_ns=START, end_ns=START+2*MINUTE)
    assert resolved.coverage_ok is None


def test_roll_requires_actual_instrument_selection(market):
    root, _ = market
    with pytest.raises(NativeEvidenceError, match='contract change'):
        collect_window(root, TRADES, START, START+2*MINUTE)


def test_exact_ohlcv_window_and_partial_clock_window(market):
    root, _ = market
    full = collect_window(root, BARS, START, START+2*MINUTE, 42, required='ohlcv')
    assert full.coverage_ok is True
    partial = collect_window(root, BARS, START+1, START+2*MINUTE, 42, required='ohlcv')
    assert partial.coverage_ok is None
    assert any('partial_minute' in m['reason'] for m in partial.mismatches)


def test_complete_timestamp_tie_retains_ordering_uncertainty(market):
    root, data = market
    rows = data[TRADES]
    rows[2]['t'] = rows[1]['t']
    _write(root, TRADES, rows)
    window = collect_window(root, TRADES, START, START+2*MINUTE, 42)
    assert window.coverage_ok is True
    assert window.coverage_evidence['minute_reconciliation'][0]['endpoint_order'] == 'unknown_order'


def test_report_resolver_recomputes_coverage_and_never_certifies_manifest_subset(market):
    root, data = market
    window = collect_window(root, TRADES, START, START+2*MINUTE, 42)
    resolver=AuditedWindowResolver(root)
    complete=resolver.resolve(window.raw_member_locators,instrument_id=42,start_ns=START,end_ns=START+2*MINUTE)
    assert complete.coverage_ok is True
    assert resolver.audit_records()[0]['native_row_count']==3
    subset=resolver.resolve([window.raw_member_locators[0]],instrument_id=42,start_ns=START,end_ns=START+2*MINUTE)
    assert subset.coverage_ok is None
    # A changed corroborating OHLC file cannot reuse the earlier audit cache.
    _write(root,BARS,data[BARS][:1])
    changed=resolver.resolve(window.raw_member_locators,instrument_id=42,start_ns=START,end_ns=START+2*MINUTE)
    assert changed.coverage_ok is None
    assert changed.missing_intervals==((START+MINUTE,START+2*MINUTE),)
