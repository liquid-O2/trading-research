"""One shared, bounded raw-window pass for auction and participation research.

All raw fields remain in immutable source files and receive a complete selected
stream hash. Ordered trade blocks can be retained by a bounded study writer;
the minute measurements are reusable views, not substitutes for those events.
This source/measurement stage does not claim fitted Context or Location quality.
"""
from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from pathlib import Path
import time

from trading_research.errors import ContractError, IntegrityError
from trading_research.research.auction_flow_data import AuctionFlowStream
from trading_research.research.auction_flow_quotes import QuoteWindow
from trading_research.research.auction_flow_windows import TapeWindow
from trading_research.research.auction_flow_time_at_price import TimeAtPrice
from trading_research.research.auction_flow_native_bins import NativeEventBins, NativeSourceOwnership
from trading_research.operations.artifacts import digest


VERSION = "auction-flow-shared-event-window-pipeline-v1"
MINUTE_NS = 60_000_000_000
CARRY_VERSION = 'auction-flow-measurement-continuation-v1'


def _parts(table, *, start, width):
    import numpy as np

    at = table["t"].to_numpy(zero_copy_only=False)
    bins = (at - start) // width
    edges = np.r_[0, np.flatnonzero(bins[1:] != bins[:-1]) + 1, len(table)]
    for left, right in zip(edges[:-1], edges[1:], strict=True):
        if right > left:
            yield int(bins[left]), table.slice(int(left), int(right - left))


def _source_intervals(selection):
    intervals = []
    for record, _ in selection:
        groups = record["groups"]
        if not groups or any(g["minimum"] is None or g["maximum"] is None for g in groups):
            raise IntegrityError("unlocated source ranges cannot certify a whole window")
        a, b = min(g["minimum"] for g in groups), max(g["maximum"] for g in groups) + 1
        intervals.append((a, b))
    result = []
    for a, b in sorted(intervals):
        if result and a <= result[-1][1]:
            result[-1] = (result[-1][0], max(result[-1][1], b))
        else:
            result.append((a, b))
    return tuple(result)


def _covered(intervals, start, end):
    return any(a <= start and end <= b for a, b in intervals)


def coordinate_window(index, instrument_id, start, end):
    """Use every actual definition-change cut, retaining each source version."""
    rows = []
    for at in index.change_points(instrument_id, start, end)[:-1]:
        coordinate, status = index.resolve(instrument_id, at)
        rows.append({"from_ns": at, "status": status,
                     "contract_key": None if coordinate is None else coordinate.contract_key,
                     "definition_version": None if coordinate is None else coordinate.definition_version,
                     "source_path": None if coordinate is None else coordinate.source_path,
                     "source_row": None if coordinate is None else coordinate.source_row})
    keys = {r["contract_key"] for r in rows}
    complete = bool(rows) and all(r["status"].startswith("accepted_") for r in rows) and len(keys) == 1
    return {"complete": complete, "contract_key": next(iter(keys)) if complete else None,
            "source_versions": rows,
            "availability_rule": "retained conservative definition known-at <= event time; physical lifetime checked separately"}


def native_coordinate_mask(index, instrument_id, start, end, width):
    """Cover complete cells by accepted, contiguous physical contract lifetimes."""
    import numpy as np

    cuts = index.change_points(instrument_id, start, end)
    accepted = []
    for a, b in zip(cuts[:-1], cuts[1:], strict=True):
        coordinate, status = index.resolve(instrument_id, a)
        if coordinate is not None and status.startswith('accepted_'):
            key = coordinate.contract_key
            if accepted and accepted[-1][1] == a and accepted[-1][2] == key:
                accepted[-1] = (accepted[-1][0], b, key)
            else:
                accepted.append((a, b, key))
    starts = start + np.arange((end - start + width - 1) // width, dtype=np.int64) * width
    ends = np.minimum(starts + width, end)
    covered = np.zeros(len(starts), dtype=bool)
    for a, b, _ in accepted:
        covered |= (starts >= a) & (ends <= b)
    return covered


@dataclass
class InstrumentWindows:
    instrument_id: int
    start: int
    end: int
    width: int
    latency: int
    maximum_trades: int
    maximum_cells: int
    native_width: int = 100_000_000
    initial_state: dict | None = None

    def __post_init__(self):
        self.tape = {}
        self.quotes = {}
        self.closed_quotes = {}
        self.raw = {}
        self.first_raw = self.last_raw = None
        self.current_quote_bin = 0
        self.cpu = Counter()
        self.work = Counter()
        self.native = NativeEventBins(instrument_id=self.instrument_id, start_ns=self.start, end_ns=self.end,
                                      width_ns=self.native_width)
        self.quotes[0] = self._new_quote(0)
        initial = self.initial_state or {}
        if initial.get('quote') is not None:
            self.quotes[0]._seed(initial['quote'])
        self.whole_tape = TapeWindow(instrument_id=self.instrument_id, start_ns=self.start, end_ns=self.end,
            latency_ns=self.latency, maximum_trades=self.maximum_trades, maximum_profile_cells=self.maximum_cells)
        self.time_at_price = TimeAtPrice(instrument_id=self.instrument_id, start_ns=self.start, end_ns=self.end,
            atomic_width_ns=self.width, latency_ns=self.latency, maximum_cells=min(1_000_000, 4 * self.maximum_cells),
            initial_state=initial.get('dwell'), initial_raw=initial.get('last_raw'))

    def bounds(self, number):
        a = self.start + number * self.width
        return a, min(a + self.width, self.end)

    def _new_quote(self, number):
        a, b = self.bounds(number)
        return QuoteWindow(instrument_id=self.instrument_id, start_ns=a, end_ns=b,
                           latency_ns=self.latency, maximum_events=50_000_000, native_sink=self.native)

    def raw_rows(self, table):
        import numpy as np
        import pyarrow as pa
        import pyarrow.compute as pc

        started = time.process_time()
        if len(table):
            self.first_raw = table["t"][0].as_py() if self.first_raw is None else self.first_raw
            self.last_raw = table["t"][-1].as_py()
            at = table['t'].to_numpy(zero_copy_only=False)
            bins = (at - self.start) // self.width
            left = np.r_[0, np.flatnonzero(bins[1:] != bins[:-1]) + 1]
            right = np.r_[left[1:], len(table)]
            flags = table["flags"]
            action = pc.cast(table["action"], pa.string())
            snapshot = pc.not_equal(pc.bit_wise_and(flags, 32), 0)
            known = pc.fill_null(pc.is_in(action, value_set=pa.array(["A", "M", "C", "R", "T", "N"])), False)
            invalid_size = pc.invert(pc.fill_null(pc.and_(pc.greater(table["size"], 0), pc.less(table["size"], 2**32 - 1)), False))
            invalid_trade = pc.and_(pc.fill_null(pc.equal(action, "T"), False), pc.and_(pc.invert(snapshot), invalid_size))
            totals = {'raw_rows': right - left}
            for name, mask in (("gap_rows", pc.not_equal(pc.bit_wise_and(flags, 4), 0)),
                               ("unknown_action_rows", pc.invert(known)), ("invalid_trade_size_rows", invalid_trade),
                               ("snapshot_rows", snapshot), ("non_snapshot_rows", pc.invert(snapshot))):
                values = pc.cast(pc.fill_null(mask, False), pa.int64()).to_numpy(zero_copy_only=False)
                totals[name] = np.add.reduceat(values, left)
            self.work['raw_atomic_parts'] += len(left)
            reduced = time.process_time()
            self.cpu['raw_atomic_batch_reduction'] += reduced - started
            for index, number in enumerate(bins[left]):
                counter = self.raw.setdefault(int(number), Counter())
                for name, values in totals.items():
                    counter[name] += int(values[index])
            self.cpu['raw_atomic_counter_updates'] += time.process_time() - reduced
        else:
            self.cpu['raw_atomic_batch_reduction'] += time.process_time() - started

    def trade_rows(self, table):
        started = time.process_time()
        self.whole_tape.add(table)
        self.native.add_trades(table)
        self.cpu['whole_trade_and_native_consumers'] += time.process_time() - started
        started = time.process_time()
        for number, part in _parts(table, start=self.start, width=self.width):
            self.work['trade_atomic_parts'] += 1
            if number not in self.tape:
                a, b = self.bounds(number)
                self.tape[number] = TapeWindow(instrument_id=self.instrument_id, start_ns=a, end_ns=b,
                    latency_ns=self.latency, maximum_trades=self.maximum_trades, maximum_profile_cells=self.maximum_cells)
            self.tape[number].add(part)
        self.cpu['trade_atomic_consumers'] += time.process_time() - started

    def quote_rows(self, table):
        started = time.process_time()
        for number, part in _parts(table, start=self.start, width=self.width):
            self.work['quote_atomic_parts'] += 1
            while self.current_quote_bin < number:
                current = self.quotes[self.current_quote_bin]
                # Coverage is not published until the full scan and source
                # finalization below. Arithmetic/standing state can now carry.
                self.closed_quotes[self.current_quote_bin] = current.finish(coverage_complete=False)
                self.current_quote_bin += 1
                _, end = self.bounds(self.current_quote_bin)
                self.quotes[self.current_quote_bin] = current.continue_window(end_ns=end)
            self.quotes[number].add(part)
        self.cpu['quote_atomic_consumers'] += time.process_time() - started

    def carry(self):
        if any(not q._closed for q in self.quotes.values()):
            raise IntegrityError('unpublished instrument windows cannot provide continuation')
        last = self.quotes[max(self.quotes)].previous
        return {'instrument_id': self.instrument_id, 'quote': None if last is None else dict(last),
                'dwell': self.time_at_price.last_state, 'last_raw': self.time_at_price.last_raw}

    def finish(self, *, source_intervals, source_owners, coordinates, native_ownership, retain_native_table):
        import numpy as np

        count = (self.end - self.start + self.width - 1) // self.width
        while self.current_quote_bin < count:
            current = self.quotes[self.current_quote_bin]
            self.closed_quotes[self.current_quote_bin] = current.finish(coverage_complete=False)
            self.current_quote_bin += 1
            if self.current_quote_bin < count:
                _, end = self.bounds(self.current_quote_bin)
                self.quotes[self.current_quote_bin] = current.continue_window(end_ns=end)
        result, source_complete_all = [], True
        for number in range(count):
            start, end = self.bounds(number)
            quality = self.raw.get(number, Counter())
            # The last raw ID observed at each cut is causal. A future print
            # must not decide whether an earlier quiet bin is eligible. A
            # snapshot-only bin is initialization, not observed quiet trading.
            before_owner, after_owner, observed_owners = source_owners[number]
            presence = bool(quality.get("non_snapshot_rows", 0)) or (
                not quality.get("raw_rows", 0) and before_owner == after_owner == self.instrument_id)
            owner_stable = (before_owner in (None, self.instrument_id) and after_owner == self.instrument_id
                and (not observed_owners or observed_owners == (self.instrument_id,)))
            source_complete = (_covered(source_intervals, start, end) and presence and owner_stable
                and not any(quality.get(k, 0) for k in ("gap_rows", "unknown_action_rows", "invalid_trade_size_rows")))
            source_complete_all &= source_complete
            coordinate = coordinate_window(coordinates, self.instrument_id, start, end)
            tape = self.tape.get(number)
            if tape is None:
                tape = TapeWindow(instrument_id=self.instrument_id, start_ns=start, end_ns=end,
                    latency_ns=self.latency, maximum_trades=self.maximum_trades, maximum_profile_cells=self.maximum_cells)
            trades = tape.record(source_coverage_complete=source_complete, coordinate_complete=coordinate["complete"])
            quotes = dict(self.closed_quotes[number])
            quotes["coverage_complete"] = source_complete
            quotes["per_complete_window_second_ofi"] = quotes["ofi_contracts"] * 1e9 / (end - start) if source_complete else None
            quotes["full_standing_window_eligible"] = bool(source_complete and coordinate["complete"]
                and quotes["observed_trusted_standing_duration_ns"] == end - start)
            quotes["full_pressure_transition_window_eligible"] = bool(quotes["full_standing_window_eligible"]
                and quotes["initial_projection"] is not None and quotes["initial_projection"]["book_valid"])
            result.append({"bin": number, "event_start_ns": start, "event_end_ns": end,
                "known_at_ns": end + self.latency, "instrument_id": self.instrument_id,
                "source_quality": dict(quality), "source_instrument_presence": presence,
                "observed_source_owner_before": before_owner, "observed_source_owner_after": after_owner,
                "raw_contracts_observed_in_source_bin": observed_owners, "supplied_raw_coordinate_stable": owner_stable,
                "coordinate": coordinate, "trade": trades, "quote": quotes})
        coordinate = coordinate_window(coordinates, self.instrument_id, self.start, self.end)
        whole = self.whole_tape.record(source_coverage_complete=source_complete_all, coordinate_complete=coordinate["complete"])
        volume = sum(r["trade"]["flows"]["all"]["volume"] for r in result)
        if volume != whole["flows"]["all"]["volume"] or sum(r["trade"]["prints"] for r in result) != whole["prints"]:
            raise IntegrityError("atomic and whole-window trade populations do not reconcile")
        time_at_price = self.time_at_price.finish(covered_intervals=[(r['event_start_ns'], r['event_end_ns'])
            for r in result if r['trade']['price_history_complete']])
        if time_at_price['eligible_prints'] != whole['prints'] or time_at_price['unpriced_prints'] != whole['unpriced_prints']:
            raise IntegrityError("time-at-price and ordinary tape populations differ")
        native = self.native.table(source_eligible=native_ownership.eligible(self.instrument_id, source_intervals),
            coordinate_eligible=native_coordinate_mask(coordinates, self.instrument_id, self.start, self.end, self.native_width),
            latency_ns=self.latency)
        native_summary = {'width_ns': self.native_width, 'cells': len(native), 'table_bytes': native.nbytes,
            'retained_artifact': None, 'quality_counts': {}, 'cohorts': {}}
        for flag in ('source_eligible', 'coordinate_eligible', 'price_history_complete',
                     'quote_standing_complete', 'quote_pressure_complete'):
            native_summary['quality_counts'][flag] = int(native[flag].to_numpy().sum())
        for name, ordinary in whole['flows'].items():
            cols = self.native.columns
            close = cols[name + '__close']
            before = np.cumsum(close, dtype=np.int64) - close
            measured = {field: int(cols[name + '__' + field].sum()) for field in ('prints', 'volume', 'unknown')}
            measured.update(close=int(close.sum()), high=int((before + cols[name + '__high']).max()),
                            low=int((before + cols[name + '__low']).min()))
            if (any(measured[k] != ordinary[k] for k in ('prints', 'volume', 'unknown'))
                    or any(measured[k] != ordinary[k] for k in ('close', 'high', 'low'))):
                raise IntegrityError('native cohort event paths do not reconcile with whole-window ordered trades')
            native_summary['cohorts'][name] = measured
        quote_totals = {'quote_rows': 'quote_or_invalidation_rows', 'fresh_quotes': 'fresh_quote_updates',
            'pressure_transitions': 'pressure_transitions', 'ofi_close': 'ofi_contracts',
            'same_price_ofi': 'same_price_size_ofi', 'price_change_ofi': 'price_change_ofi',
            'standing_ns': 'observed_trusted_standing_duration_ns'}
        for name, field in quote_totals.items():
            if int(self.native.columns[name].sum()) != sum(r['quote'][field] for r in result):
                raise IntegrityError('native and atomic quote populations or exposure differ')
        if retain_native_table is not None:
            native_summary['retained_artifact'] = retain_native_table(native, {'instrument_id': self.instrument_id,
                'event_start_ns': self.start, 'event_end_ns': self.end, 'width_ns': self.native_width})
        return {"instrument_id": self.instrument_id, "coordinate": coordinate,
                "whole_window": whole, "atomic_windows": result, 'time_at_price': time_at_price,
                'native_event_measurements': native_summary}


def measure_raw_window(*, data_root: Path, index, coordinates, root, start_ns, end_ns,
                       maximum_scan_rows=50_000_000, latency_ns=250_000_000,
                       atomic_width_ns=MINUTE_NS, maximum_profile_cells=250000,
                       retain_trade_batch=None, retain_native_table=None, native_width_ns=100_000_000,
                       maximum_native_array_bytes=2 * 1024**3,
                       retain_quote_batch=None, retain_excluded_batch=None, inspect_raw_batch=None,
                       source_paths=None, continuation=None):
    """Complete raw scan and measurements; callback retains exact ordered trades.

    The callback is a storage consumer inside the same registered worker. No
    study result is returned if reading, storage, identity or arithmetic fails.
    """
    import pyarrow.compute as pc
    import copy

    pipeline_started = time.process_time()
    if (root not in ("NQ", "ES") or coordinates.root != root
            or type(atomic_width_ns) is not int or not 0 < atomic_width_ns <= MINUTE_NS
            or (end_ns - start_ns + atomic_width_ns - 1) // atomic_width_ns > 100000
            or any(callback is not None and not callable(callback) for callback in
                   (retain_trade_batch, retain_native_table, retain_quote_batch, retain_excluded_batch, inspect_raw_batch))
            or type(maximum_native_array_bytes) is not int or not 1 <= maximum_native_array_bytes <= 2 * 1024**3):
        raise ContractError("bounded same-root source/window grid and optional registered storage consumer required")
    parameters = {'root': root, 'latency_ns': latency_ns, 'atomic_width_ns': atomic_width_ns,
                  'native_width_ns': native_width_ns}
    initial_states, initial_owner, preceding_owner = {}, None, None
    if continuation is not None:
        if (not isinstance(continuation, dict)
                or continuation.get('sha256') != digest({k: v for k, v in continuation.items() if k != 'sha256'})
                or continuation.get('version') != CARRY_VERSION or continuation.get('completed') is not True
                or continuation.get('next_start_ns') != start_ns or continuation.get('parameters') != parameters
                or continuation.get('coordinate_version') != coordinates.source_version
                or continuation.get('coordinate_snapshot_version') != coordinates.snapshot_version
                or not isinstance(continuation.get('instruments'), dict) or len(continuation['instruments']) > 4096):
            raise IntegrityError('measurement continuation is changed, nonadjacent or from another definition')
        initial_states = copy.deepcopy(continuation['instruments'])
        for key, state in initial_states.items():
            if (not isinstance(key, str) or not key.isdigit() or int(key) <= 0
                    or not isinstance(state, dict) or state.get('instrument_id') != int(key)):
                raise IntegrityError('measurement continuation instrument identity changed')
        preceding_owner = copy.deepcopy(continuation.get('last_ordinary_source_event'))
        if preceding_owner is not None:
            if (not isinstance(preceding_owner, dict) or type(preceding_owner.get('instrument_id')) is not int
                    or preceding_owner['instrument_id'] <= 0 or type(preceding_owner.get('event_ns')) is not int
                    or not 0 <= preceding_owner['event_ns'] < start_ns
                    or str(preceding_owner['instrument_id']) not in initial_states):
                raise IntegrityError('measurement continuation lost the past observed source owner')
            current, _ = coordinates.resolve(preceding_owner['instrument_id'], start_ns)
            if current is not None and current.contract_key == preceding_owner.get('contract_key'):
                initial_owner = preceding_owner['instrument_id']
    stream = AuctionFlowStream(data_root=data_root, index=index,
        dataset=f"quantpad/cme__{root.lower()}-continuous-futures__mbp-1",
        start_ns=start_ns, end_ns=end_ns, maximum_scan_rows=maximum_scan_rows, latency_ns=latency_ns,
        source_paths=source_paths, continuation=None if continuation is None else continuation.get('source'))
    # Whole acquired file ranges also contain observed empty intervals between
    # adjacent row groups. A requested quiet interval need not decode a row.
    intervals = _source_intervals([(r, ()) for r in stream.lineage_records])
    native_ownership = NativeSourceOwnership(start_ns=start_ns, end_ns=end_ns, width_ns=native_width_ns,
                                             initial_owner=initial_owner)
    native_instrument_bytes = NativeEventBins.required_array_bytes(start_ns=start_ns, end_ns=end_ns, width_ns=native_width_ns)
    if native_ownership.array_bytes + native_instrument_bytes > maximum_native_array_bytes:
        raise ContractError('declared native window cannot fit its aggregate array allowance')
    by_instrument, last_owner_in_bin, owners_in_bin = {}, {}, {}
    initialized = time.process_time()
    allocation_cpu = 0.0
    detail_cpu, work = Counter(), Counter()
    def instrument_windows(instrument):
        nonlocal allocation_cpu
        if instrument not in by_instrument:
            if len(by_instrument) >= 16:
                raise ContractError('requested window exceeds its declared supplied-instrument capacity')
            if native_ownership.array_bytes + (len(by_instrument) + 1) * native_instrument_bytes > maximum_native_array_bytes:
                raise ContractError('all observed raw instruments exceed the declared aggregate native array allowance')
            at = time.process_time()
            seed = copy.deepcopy(initial_states.get(str(instrument)))
            if seed is not None and seed.get('quote') is not None:
                previous, _ = coordinates.resolve(instrument, seed['quote']['t'])
                current, _ = coordinates.resolve(instrument, start_ns)
                if previous is None or current is None or previous.contract_key != current.contract_key:
                    # A reused raw number does not carry another physical
                    # contract's trusted quote into its new lifetime.
                    seed['quote']['book_valid'] = 0
            if seed is not None and seed.get('dwell') is not None:
                previous, _ = coordinates.resolve(instrument, seed['dwell'][0])
                current, _ = coordinates.resolve(instrument, start_ns)
                if previous is None or current is None or previous.contract_key != current.contract_key:
                    seed['dwell'] = (seed['dwell'][0], seed['dwell'][1], False)
            by_instrument[instrument] = InstrumentWindows(instrument, start_ns, end_ns,
                atomic_width_ns, latency_ns, maximum_scan_rows, maximum_profile_cells, native_width_ns, seed)
            allocation_cpu += time.process_time() - at
        return by_instrument[instrument]
    if initial_owner is not None:
        instrument_windows(initial_owner)
    iterator = iter(stream)
    while True:
        at = time.process_time()
        try:
            batch = next(iterator)
        except StopIteration:
            detail_cpu['source_decode_and_projection'] += time.process_time() - at
            break
        detail_cpu['source_decode_and_projection'] += time.process_time() - at
        work['raw_batches'] += 1
        at = time.process_time()
        native_ownership.add(batch.raw)
        detail_cpu['native_source_ownership'] += time.process_time() - at
        if inspect_raw_batch is not None:
            at = time.process_time()
            inspect_raw_batch(batch.raw, batch.source)
            detail_cpu['reference_sample_collection'] += time.process_time() - at
        if retain_excluded_batch is not None and len(batch.excluded_trades):
            at = time.process_time()
            retain_excluded_batch(batch.excluded_trades, batch.source)
            detail_cpu['event_storage'] += time.process_time() - at
        trade_parts = {table['instrument_id'][0].as_py(): table for table in batch.trades}
        ordinary = batch.raw.filter(pc.equal(pc.bit_wise_and(batch.raw["flags"], 32), 0))
        for number, part in _parts(ordinary, start=start_ns, width=atomic_width_ns):
            last_owner_in_bin[number] = part["instrument_id"][-1].as_py()
            owners_in_bin.setdefault(number, set()).update(pc.unique(part["instrument_id"]).to_pylist())
        if len(ordinary):
            last = ordinary.slice(len(ordinary) - 1).to_pylist()[0]
            coordinate, _ = coordinates.resolve(last['instrument_id'], last['t'])
            preceding_owner = {'instrument_id': last['instrument_id'], 'event_ns': last['t'],
                'source_order': last['source_order'], 'source_key': batch.source['source_key'],
                'source_row': last['source_row'], 'contract_key': None if coordinate is None else coordinate.contract_key}
        for instrument in pc.unique(batch.raw["instrument_id"]).to_pylist():
            work['raw_instrument_batches'] += 1
            instrument_windows(instrument)
            part = batch.raw.filter(pc.equal(batch.raw["instrument_id"], instrument))
            by_instrument[instrument].raw_rows(part)
            at = time.process_time()
            by_instrument[instrument].time_at_price.add(part, trade_parts.get(instrument), source_key=batch.source['source_key'])
            detail_cpu['time_at_price_consumers'] += time.process_time() - at
        for table in batch.trades:
            instrument = table["instrument_id"][0].as_py()
            if retain_trade_batch is not None:
                at = time.process_time()
                retain_trade_batch(table, batch.source)
                detail_cpu['event_storage'] += time.process_time() - at
            by_instrument[instrument].trade_rows(table)
        for table in batch.quotes:
            instrument = table["instrument_id"][0].as_py()
            if retain_quote_batch is not None:
                at = time.process_time()
                retain_quote_batch(table, batch.source)
                detail_cpu['event_storage'] += time.process_time() - at
            by_instrument[instrument].quote_rows(table)
    manifest = stream.manifest()
    scanned = time.process_time()
    source_owners, owner = [], initial_owner
    for number in range((end_ns - start_ns + atomic_width_ns - 1) // atomic_width_ns):
        before, owner = owner, last_owner_in_bin.get(number, owner)
        source_owners.append((before, owner, tuple(sorted(owners_in_bin.get(number, ())))))
    instruments = [by_instrument[key].finish(source_intervals=intervals, source_owners=source_owners,
        coordinates=coordinates, native_ownership=native_ownership, retain_native_table=retain_native_table)
        for key in sorted(by_instrument)]
    counts = manifest["projection"]["counts"]
    if (sum(r["whole_window"]["prints"] for r in instruments) != counts["trades"]
            or sum(r["whole_window"]["flows"]["all"]["volume"] for r in instruments) != counts["volume"]
            or sum(w["quote"]["quote_or_invalidation_rows"] for r in instruments for w in r["atomic_windows"]) != counts["quote_rows"]):
        raise IntegrityError("source, whole-window and atomic measurement counts differ")
    for value in by_instrument.values():
        detail_cpu.update(value.cpu)
        work.update(value.work)
        initial_states[str(value.instrument_id)] = value.carry()
    if len(initial_states) > 4096:
        raise ContractError('source continuation exceeds its retained instrument-state capacity')
    carry = {'version': CARRY_VERSION, 'completed': True, 'parameters': parameters, 'next_start_ns': end_ns,
        'coordinate_version': coordinates.source_version, 'coordinate_snapshot_version': coordinates.snapshot_version,
        'source': stream.carry(), 'instruments': initial_states, 'last_ordinary_source_event': preceding_owner,
        'previous_continuation_sha256': None if continuation is None else continuation['sha256'],
        'flow_reset': 'new local window; original-prefix completeness retained separately',
        'quote_recovery': 'no date/file-cut recovery; first invalidation, actual standing state and age persist'}
    carry['sha256'] = digest(carry)
    detail_cpu['unassigned_scan_routing'] = max(0.0, scanned - initialized - allocation_cpu - sum(detail_cpu.values()))
    work['source_files_selected'] = len(stream.selection)
    work['source_groups_selected'] = sum(len(groups) for _, groups in stream.selection)
    work['instrument_atomic_cells'] = len(by_instrument) * len(source_owners)
    return {"version": VERSION, "root": root, "event_start_ns": start_ns, "event_end_ns": end_ns,
            "known_at_ns": end_ns + latency_ns, "atomic_width_ns": atomic_width_ns,
            'native_width_ns': native_width_ns,
            'native_allocated_array_bytes': native_ownership.array_bytes + len(by_instrument) * native_instrument_bytes,
            'pipeline_cpu_components': {'initialization': initialized - pipeline_started,
                'instrument_allocation': allocation_cpu, 'scan_and_consumers': scanned - initialized - allocation_cpu,
                'finalization_and_native_storage': time.process_time() - scanned},
            'scan_cpu_components_disjoint': dict(detail_cpu), 'workload_counts': dict(work),
            'measurement_continuation': carry,
            "source_manifest": manifest, "source_archive_intervals": intervals,
            "coordinate_manifest_version": coordinates.source_version,
            "coordinate_snapshot_supplement_version": coordinates.snapshot_version,
            "instruments": instruments, "status": "measured" if instruments else "unavailable_source_window",
            "statistics_or_predictive_family_complete": False,
            "coverage_basis": "conditional on the supplied archive; source range, per-window flags and raw coordinates remain separate",
            "quote_history_basis": ('observed prefix initialization; no earlier-history certification inferred' if continuation is None
                else 'adjacent continuation of the exact source lineage, invalidation, standing quote and original economic age')}
