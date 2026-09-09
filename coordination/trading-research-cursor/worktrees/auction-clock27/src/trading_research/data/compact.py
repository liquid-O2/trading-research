"""Bounded Arrow projection of full-field QuantPad MBP windows.

All supplied raw fields are hashed before projection. Integer-tick columns are
an explicitly narrower execution view; off-grid/unpriced flow remains counted
in quality totals. No missing receipt or venue status is inferred from quotes.
"""

from dataclasses import asdict
import hashlib
from pathlib import Path
import resource
import time

from trading_research.errors import ContractError,DependencyUnavailable,IntegrityError
from trading_research.operations.artifacts import code_manifest,code_snapshot,digest
from trading_research.operations.trials import TrialRegistry
from trading_research.data.reconcile import select_groups
from trading_research.data.compact_native import project_part


SOURCE_CLOCK_STRICT = 'strict'
SOURCE_CLOCK_REDUNDANT_BACKWARD_SNAPSHOT_V1 = 'redundant_backward_snapshot_v1'
_SOURCE_CLOCK_POLICIES = (SOURCE_CLOCK_STRICT, SOURCE_CLOCK_REDUNDANT_BACKWARD_SNAPSHOT_V1)
_REPLAY_ACTION = 'A'
_REPLAY_SIDE = 'N'
_REPLAY_FLAGS = 168
_ORDINARY_QUOTE_ACTIONS = frozenset({'A', 'M', 'C'})
_ORDINARY_QUOTE_FLAGS = 128
_UINT32_SENTINEL = 2**32 - 1
_REPLAY_REASON = 'redundant_backward_snapshot_v1_identical_adjacent_ordinary_bbo'
_CLOCK_FIELDS = ('t', 'action', 'side', 'price', 'size', 'bid_px', 'ask_px',
                 'bid_sz', 'ask_sz', 'instrument_id', 'flags')
_TERMINAL_FIELDS = _CLOCK_FIELDS + ('source_row', 'physical_source_key')


def named_source_clock_policy(value):
    if value in (None, SOURCE_CLOCK_STRICT):
        return SOURCE_CLOCK_STRICT
    if value != SOURCE_CLOCK_REDUNDANT_BACKWARD_SNAPSHOT_V1:
        raise ContractError('explicit named source-clock policy required')
    return value


def _finite_exact_positive_quarter_point(value):
    if type(value) is bool or type(value) not in (int, float):
        return False
    scaled = value * 4
    return scaled == scaled and scaled == int(scaled) and 0 < scaled < 2**53


def _positive_finite_size(value):
    if type(value) is bool or type(value) not in (int, float):
        return False
    if type(value) is float and value != int(value):
        return False
    return 0 < int(value) < _UINT32_SENTINEL


def _exact_int(value):
    if type(value) is bool or value is None:
        return None
    if type(value) is int:
        return value
    if type(value) is float and value == int(value):
        return int(value)
    return None


def valid_replay_bbo(bid_px, ask_px, bid_sz, ask_sz):
    return (_finite_exact_positive_quarter_point(bid_px) and _finite_exact_positive_quarter_point(ask_px)
            and bid_px < ask_px and _positive_finite_size(bid_sz) and _positive_finite_size(ask_sz))


def _same_original_bbo(left, right):
    return (left.get('bid_px') == right.get('bid_px') and left.get('ask_px') == right.get('ask_px')
            and left.get('bid_sz') == right.get('bid_sz') and left.get('ask_sz') == right.get('ask_sz'))


def _original_event_fields(item):
    if not isinstance(item, dict):
        return None
    if isinstance(item.get('record'), dict):
        fields = dict(item['record'])
        for name in ('source_row', 'row_group', 'source_key'):
            if name in item:
                fields[name] = item[name]
        return fields
    return dict(item)


def authenticate_redundant_backward_snapshot(*, event, predecessor, same_physical_source, physically_adjacent):
    """Admit only the explicit no-economic-change A/N/168 adjacent snapshot."""
    if (not same_physical_source or not physically_adjacent or not isinstance(event, dict)
            or not isinstance(predecessor, dict)):
        return None
    if (event.get('action') != _REPLAY_ACTION or event.get('side') != _REPLAY_SIDE
            or _exact_int(event.get('flags')) != _REPLAY_FLAGS):
        return None
    if predecessor.get('action') == 'T' or predecessor.get('action') not in _ORDINARY_QUOTE_ACTIONS:
        return None
    if _exact_int(predecessor.get('flags')) != _ORDINARY_QUOTE_FLAGS:
        return None
    instrument = _exact_int(event.get('instrument_id'))
    if instrument is None or instrument <= 0 or instrument != _exact_int(predecessor.get('instrument_id')):
        return None
    if not valid_replay_bbo(event.get('bid_px'), event.get('ask_px'), event.get('bid_sz'), event.get('ask_sz')):
        return None
    if not valid_replay_bbo(predecessor.get('bid_px'), predecessor.get('ask_px'),
                            predecessor.get('bid_sz'), predecessor.get('ask_sz')):
        return None
    if not _same_original_bbo(event, predecessor):
        return None
    return _REPLAY_REASON


def classify_redundant_backward_snapshots(events, *, source_key=None):
    """Classify original physical-neighbor records. No source reread or rewrite."""
    highwater = None
    previous = None
    disposed = []
    for item in events:
        event = _original_event_fields(item)
        if not isinstance(event, dict) or type(event.get('t')) is not int or type(event.get('source_row')) is not int:
            raise IntegrityError('original all-field neighbor record with a physical source address required')
        key = event.get('source_key', source_key)
        if highwater is not None and event['t'] < highwater:
            adjacent = previous is not None and type(previous.get('source_row')) is int and previous['source_row'] + 1 == event['source_row']
            same = previous is not None and previous.get('source_key') == key
            reason = authenticate_redundant_backward_snapshot(
                event=event, predecessor=previous, same_physical_source=same, physically_adjacent=adjacent)
            if reason is None:
                raise IntegrityError('source event order/null clock requires separate resolution')
            disposed.append({'source_row': event['source_row'], 'row_group': event.get('row_group'),
                             't': event['t'], 'action': event['action'], 'side': event['side'],
                             'flags': event['flags'], 'instrument_id': event['instrument_id'],
                             'bid_px': event['bid_px'], 'ask_px': event['ask_px'],
                             'bid_sz': event['bid_sz'], 'ask_sz': event['ask_sz'],
                             'predecessor_source_row': previous['source_row'],
                             'predecessor_t': previous['t'], 'predecessor_action': previous['action'],
                             'predecessor_flags': previous['flags'], 'reason': reason})
        else:
            highwater = event['t']
        previous = {**event, 'source_key': key}
    return tuple(disposed)


def arrow_bytes(table):
    import pyarrow as pa
    sink=pa.BufferOutputStream()
    with pa.ipc.new_stream(sink,table.schema) as writer:writer.write_table(table) if isinstance(table,pa.Table) else writer.write_batch(table)
    return sink.getvalue().to_pybytes()


class CompactProjector:
    def __init__(self,*,tick_denominator:int,maximum_rows:int,source_clock_policy=SOURCE_CLOCK_STRICT):
        if tick_denominator!=4 or type(maximum_rows) is not int or maximum_rows<1:raise ContractError("this registered projection supports quarter-point minis and a finite row budget")
        self.source_clock_policy=named_source_clock_policy(source_clock_policy)
        self.tick_denominator=tick_denominator;self.maximum_rows=maximum_rows;self.rows=0;self.blocked={};self.flow_complete={};self.prior_time=None;self.raw_hash=hashlib.sha256();self.raw_parts=[]
        self.failed=False;self._source_parts=set()
        self.counts={'raw_rows':0,'trades':0,'volume':0,'buy_volume':0,'sell_volume':0,'unknown_volume':0,'unpriced_volume':0,'gap_rows':0,'snapshot_trade_rows':0,'quote_rows':0}
        self.disposed_snapshot_rows=0
        self._terminal=None
        self.last_replay_mask=None
        self.last_replay_orders=()
        self.last_replay_evidence=()

    def project(self,batch,*,source_part:str,physical_source_key=None):
        if self.failed:raise IntegrityError("failed compact projection must be restarted from its admitted source")
        try:
            return self._project(batch,source_part=source_part,physical_source_key=physical_source_key)
        except BaseException:
            self.failed=True
            raise

    def restore_clock_carry(self, record, *, highwater):
        """Restore authenticated terminal original identity and non-replay highwater."""
        if self.source_clock_policy == SOURCE_CLOCK_STRICT:
            raise IntegrityError('strict source-clock carry cannot restore a replay highwater')
        if record is None:
            if highwater is not None or self.rows:
                raise IntegrityError('source continuation row count and last observed event disagree')
            self.prior_time = None
            self._terminal = None
            return
        if (not isinstance(record, dict) or type(highwater) is not int
                or type(record.get('t')) is not int or record['t'] > highwater):
            raise IntegrityError('source continuation lost its non-replay clock highwater')
        self.prior_time = highwater
        self._terminal = {name: record.get(name) for name in _TERMINAL_FIELDS}

    def _row_record(self, table, index, physical_source_key):
        record = {name: table[name][index].as_py() for name in _CLOCK_FIELDS}
        record['source_row'] = table['source_row'][index].as_py() if 'source_row' in table.column_names else None
        record['physical_source_key'] = physical_source_key
        for name in ('t', 'flags', 'instrument_id', 'size', 'bid_sz', 'ask_sz', 'source_row'):
            value = record.get(name)
            coerced = _exact_int(value)
            if coerced is not None:
                record[name] = coerced
        return record

    def _predecessor_record(self, table, index, physical_source_key):
        if 'source_row' not in table.column_names:
            return None
        current = _exact_int(table['source_row'][index].as_py())
        if current is None:
            return None
        if index > 0:
            previous = _exact_int(table['source_row'][index - 1].as_py())
            if previous is None or current != previous + 1:
                return None
            return self._row_record(table, index - 1, physical_source_key)
        terminal = self._terminal
        if (terminal is None or type(terminal.get('source_row')) is not int
                or current != terminal['source_row'] + 1
                or terminal.get('physical_source_key') is None
                or terminal.get('physical_source_key') != physical_source_key):
            return None
        return terminal

    def _apply_replay_clock(self, table, *, physical_source_key):
        import numpy as np

        times = table['t']
        if times.null_count:
            raise IntegrityError("source event order/null clock requires separate resolution")
        t = times.to_numpy(zero_copy_only=False)
        if t.dtype.kind not in 'iu':
            raise IntegrityError("source event order/null clock requires separate resolution")
        t = np.asarray(t, dtype=np.int64)
        if self.prior_time is not None:
            prefix = np.maximum.accumulate(np.concatenate((np.array([self.prior_time], dtype=np.int64), t)))[:-1]
        else:
            prefix = np.maximum.accumulate(t)
            prefix = np.concatenate((t[:1], prefix[:-1])) if len(t) else prefix
        backward = t < prefix
        replay = np.zeros(len(t), dtype=bool)
        evidence = []
        if np.any(backward):
            for index in np.flatnonzero(backward).tolist():
                event = self._row_record(table, index, physical_source_key)
                predecessor = self._predecessor_record(table, index, physical_source_key)
                reason = authenticate_redundant_backward_snapshot(
                    event=event, predecessor=predecessor,
                    same_physical_source=predecessor is not None, physically_adjacent=predecessor is not None)
                if reason is None:
                    raise IntegrityError("source event order/null clock requires separate resolution")
                replay[index] = True
                evidence.append({'index': index, 'reason': reason, 'event': event, 'predecessor': dict(predecessor)})
        economic = t[~replay]
        if len(economic):
            self.prior_time = int(economic[-1])
        self._terminal = self._row_record(table, len(t) - 1, physical_source_key)
        self.last_replay_mask = replay
        self.last_replay_evidence = tuple(evidence)
        return replay

    def _drop_replay_quotes(self, quotes, replay_orders):
        import pyarrow as pa
        import pyarrow.compute as pc

        if not replay_orders or not len(quotes):
            return quotes
        marked = pa.array(replay_orders, type=quotes.schema.field('source_order').type)
        return quotes.filter(pc.invert(pc.is_in(quotes['source_order'], value_set=marked)))

    def _project(self,batch,*,source_part:str,physical_source_key=None):
        import numpy as np
        import pyarrow as pa
        import pyarrow.compute as pc
        required={'t','action','side','price','size','bid_px','ask_px','bid_sz','ask_sz','instrument_id','flags'}
        if not required.issubset(batch.schema.names) or not source_part:raise DependencyUnavailable("full admitted MBP schema and source-part identity required")
        if source_part in self._source_parts:raise IntegrityError("physical source part already projected; restart instead of double ingestion")
        if physical_source_key is not None and (type(physical_source_key) is not str or not physical_source_key):
            raise ContractError('physical source identity required for replay-clock adjacency')
        if not batch.num_rows:
            self.last_replay_mask=None;self.last_replay_orders=();self.last_replay_evidence=()
            return [],[]
        if self.rows+batch.num_rows>self.maximum_rows:raise ContractError("registered compact projection row budget exceeded")
        table=pa.Table.from_batches([batch]) if isinstance(batch,pa.RecordBatch) else batch
        table=table.combine_chunks();times=table['t'].chunk(0)
        replay_mask=None
        if self.source_clock_policy==SOURCE_CLOCK_STRICT:
            if times.null_count or pc.any(pc.less(times.slice(1),times.slice(0,len(times)-1))).as_py() or self.prior_time is not None and times[0].as_py()<self.prior_time:raise IntegrityError("source event order/null clock requires separate resolution")
            self.prior_time=times[-1].as_py()
            self.last_replay_mask=None;self.last_replay_orders=();self.last_replay_evidence=()
        else:
            replay_mask=self._apply_replay_clock(table,physical_source_key=physical_source_key)
        self._source_parts.add(source_part)
        raw=arrow_bytes(table);part_hash=hashlib.sha256(raw).hexdigest();self.raw_hash.update(len(raw).to_bytes(8,'big'));self.raw_hash.update(raw)
        self.raw_parts.append({'source_part':source_part,'rows':len(table),'all_field_arrow_hash':part_hash,'global_first_row':self.rows})
        first_order=self.rows
        table=table.append_column('source_order',pa.array(np.arange(first_order,first_order+len(table),dtype=np.int64)))
        self.rows+=len(table);self.counts['raw_rows']+=len(table)
        if replay_mask is not None and replay_mask.any():
            replay_orders=(first_order+np.flatnonzero(replay_mask)).tolist()
            self.disposed_snapshot_rows+=int(replay_mask.sum())
        else:
            replay_orders=[]
        self.last_replay_orders=tuple(replay_orders)
        quotes=[];trades=[]
        def clean_ticks(col):
            scaled=pc.multiply(col,self.tick_denominator)
            valid=pc.fill_null(pc.and_(pc.is_finite(scaled),pc.and_(pc.equal(scaled,pc.floor(scaled)),pc.and_(pc.greater(scaled,0),pc.less(scaled,2**53)))),False)
            return pc.cast(pc.if_else(valid,scaled,0),pa.int64()),valid
        def isum(col):return pc.sum(col).as_py() or 0
        instruments = pc.unique(table['instrument_id']).to_pylist()
        for instrument in instruments:
            if type(instrument) is not int or instrument<=0:raise IntegrityError("unresolved source instrument")
            part=table if len(instruments)==1 else table.filter(pc.equal(table['instrument_id'],instrument));flags=part['flags']
            if flags.null_count or pc.any(pc.or_(pc.less(flags,0),pc.greater(flags,255))).as_py():raise IntegrityError("invalid raw flag bitset")
            fused = project_part(part, instrument=instrument, first_order=self.rows-len(table), blocked=instrument in self.blocked) if len(instruments)==1 else None
            if fused is not None:
                q,t,invalid_index,flow_complete,counts=fused
                if invalid_index>=0 and instrument not in self.blocked:
                    self.blocked[instrument]=int(part['source_order'][invalid_index].as_py())
                self.flow_complete[instrument]=self.flow_complete.get(instrument,True) and flow_complete
                q=self._drop_replay_quotes(q,replay_orders)
                counts=dict(counts);counts['quote_rows']=len(q)
                for name,value in counts.items():self.counts[name]+=value
                if len(q):quotes.append(q)
                if len(t):trades.append(t)
                continue
            actions=pc.cast(part['action'],pa.string());side=pc.cast(part['side'],pa.string())
            gaps=pc.not_equal(pc.bit_wise_and(flags,4),0);snap=pc.not_equal(pc.bit_wise_and(flags,32),0)
            known_action=pc.is_in(actions,value_set=pa.array(['A','M','C','R','T','N']))
            unknown=pc.invert(pc.fill_null(known_action,False));clear=pc.equal(actions,'R')
            invalidation=pc.or_(gaps,pc.or_(unknown,pc.fill_null(clear,False)))
            invalid_index=pc.index(invalidation,True).as_py()
            if instrument in self.blocked:eligible=pa.repeat(pa.scalar(False),len(part))
            elif invalid_index>=0:
                eligible=pa.array(np.arange(len(part),dtype=np.int64)<invalid_index);self.blocked[instrument]=int(part['source_order'][invalid_index].as_py())
            else:eligible=pa.repeat(pa.scalar(True),len(part))
            self.counts['gap_rows']+=isum(pc.cast(gaps,pa.int64()))
            self.flow_complete[instrument]=self.flow_complete.get(instrument,True) and not pc.any(pc.or_(gaps,unknown)).as_py()
            bid,bid_ok=clean_ticks(part['bid_px']);ask,ask_ok=clean_ticks(part['ask_px'])
            bs=pc.fill_null(part['bid_sz'],0);asz=pc.fill_null(part['ask_sz'],0)
            valid=pc.and_(eligible,pc.and_(pc.and_(bid_ok,ask_ok),pc.and_(pc.less(bid,ask),pc.and_(pc.greater(bs,0),pc.greater(asz,0)))))
            qkeep=pc.or_(pc.is_in(actions,value_set=pa.array(['A','M','C'])),invalidation)
            q=pa.table({'t':part['t'],'source_order':part['source_order'],'instrument_id':part['instrument_id'],
                        'bid':bid,'ask':ask,'bid_size':pc.cast(bs,pa.int64()),'ask_size':pc.cast(asz,pa.int64()),'book_valid':pc.cast(valid,pa.uint8()),'snapshot':pc.cast(snap,pa.uint8())}).filter(qkeep)
            q=self._drop_replay_quotes(q,replay_orders)
            if len(q):quotes.append(q);self.counts['quote_rows']+=len(q)
            is_trade=pc.equal(actions,'T');self.counts['snapshot_trade_rows']+=isum(pc.cast(pc.and_(is_trade,snap),pa.int64()))
            tkeep=pc.and_(is_trade,pc.invert(snap));size=pc.fill_null(part['size'],0)
            good_size=pc.greater(size,0)
            if pc.any(pc.and_(tkeep,pc.invert(good_size))).as_py():self.flow_complete[instrument]=False
            tkeep=pc.and_(tkeep,good_size);price,price_ok=clean_ticks(part['price'])
            direction=pc.if_else(pc.equal(side,'B'),1,pc.if_else(pc.equal(side,'A'),-1,0));direction=pc.fill_null(direction,0)
            t=pa.table({'t':part['t'],'source_order':part['source_order'],'instrument_id':part['instrument_id'],'price':price,
                        'size':pc.cast(size,pa.int64()),'side':pc.cast(direction,pa.int64()),'price_valid':pc.cast(price_ok,pa.uint8())}).filter(tkeep)
            if len(t):
                self.counts['trades']+=len(t);self.counts['volume']+=isum(t['size'])
                for code,name in ((1,'buy_volume'),(-1,'sell_volume'),(0,'unknown_volume')):self.counts[name]+=isum(t.filter(pc.equal(t['side'],code))['size'])
                self.counts['unpriced_volume']+=isum(t.filter(pc.equal(t['price_valid'],0))['size']);trades.append(t)
        return quotes,trades

    def manifest(self):
        if self.failed:raise IntegrityError("failed compact projection cannot publish a partial manifest")
        if self.counts['volume']!=sum(self.counts[k] for k in ('buy_volume','sell_volume','unknown_volume')):raise IntegrityError("compact flow partition failed")
        counts=dict(self.counts)
        result={'version':'quantpad-quarter-point-compact-v2','tick_denominator':self.tick_denominator,'raw_parts':tuple(dict(p) for p in self.raw_parts),
                'all_selected_field_stream_hash':self.raw_hash.hexdigest(),'counts':counts,
                'unrecovered_book_instruments':{str(k):v for k,v in self.blocked.items()},'observed_prefix_flow_complete':{str(k):v for k,v in self.flow_complete.items()},
                'initialization_basis':'observed prefix only; absence of earlier gaps is not certified',
                'strategy_receipt':'missing; choose a separate named event-plus-delay scenario',
                'venue_status':'not supplied; a separately labeled market-state scenario or observed status evidence is required'}
        if self.source_clock_policy!=SOURCE_CLOCK_STRICT:
            counts['disposed_snapshot_rows']=self.disposed_snapshot_rows
            result['source_clock_policy']=self.source_clock_policy
            result['source_clock_replay']={'policy':self.source_clock_policy,
                'disposed_snapshot_rows':self.disposed_snapshot_rows,
                'reconstruction':'original source addresses and all-field hashes; no timestamp rewrite',
                'provenance':'explicit redundant_backward_snapshot_v1 no-economic-change replay disposition'}
        return result


def read_compact_window(*,data_root:Path,index:dict,dataset:str,start:int,end:int,maximum_rows:int):
    import pyarrow as pa
    import pyarrow.compute as pc
    import pyarrow.parquet as pq
    selected,expected=select_groups(index,dataset=dataset,start=start,end=end,max_scan_rows=maximum_rows)
    projector=CompactProjector(tick_denominator=4,maximum_rows=maximum_rows);quotes=[];trades=[];scanned=0;sources=[]
    for record,groups in selected:
        path=data_root/record['path']
        if not path.resolve().is_relative_to(data_root.resolve()):raise ContractError("source resolves outside admitted data root")
        before=path.stat()
        if (before.st_size,before.st_mtime_ns)!=(record['bytes'],record['mtime_ns']):raise IntegrityError("indexed source changed")
        pf=pq.ParquetFile(path)
        for g in groups:
            offset=0
            for batch in pf.iter_batches(row_groups=[g],batch_size=65536,use_threads=False):
                scanned+=len(batch);clock=batch.column(batch.schema.get_field_index('t'))
                if clock.null_count:raise IntegrityError("unlocated event time cannot be dropped by a window filter")
                filtered=batch.filter(pc.and_(pc.greater_equal(clock,start),pc.less(clock,end)))
                qs,ts=projector.project(filtered,source_part=f"{record['path']}#row-group={g}#batch-offset={offset}")
                quotes.extend(qs);trades.extend(ts);offset+=len(batch)
        pf.close()
        after=path.stat()
        if (before.st_size,before.st_mtime_ns)!=(after.st_size,after.st_mtime_ns):raise IntegrityError("raw input changed while projecting")
        sources.append({'path':record['path'],'groups':groups,'metadata_version':digest(record)})
    if scanned!=expected:raise IntegrityError("selected physical-row count mismatch")
    if not quotes or not trades:raise DependencyUnavailable("nonempty eligible quote and trade projections required")
    # Input order is preserved for identical timestamps; an observed time decrease
    # raises above instead of inventing order across overlapping source files.
    q=pa.concat_tables(quotes).sort_by([('t','ascending'),('source_order','ascending')]).combine_chunks()
    t=pa.concat_tables(trades).sort_by([('t','ascending'),('source_order','ascending')]).combine_chunks()
    return q,t,{**projector.manifest(),'dataset':dataset,'start':start,'end':end,'physical_rows_scanned':scanned,'sources':sources}


def registered_compact_pilot(*,data_root:Path,package_root:Path,index:dict,index_version:str,start:int,end:int):
    registry=TrialRegistry(package_root/'evidence/trials');protocol={'dataset':'quantpad/cme__nq-continuous-futures__mbp-1','start':start,'end':end,'maximum_rows':4000000,'batch_rows':65536,'source_fields':'all','economic_evaluation':False}
    family='B01-compact-one-hour-v1';registry.register_family(family,scope_ids=('B01.1','B02.1','F01.DECODER'),protocol=protocol,max_attempts=4,cpu_budget_seconds=600)
    snapshot=code_snapshot(package_root,registry.artifacts);trial=registry.register(name='Compact full-field one-hour MBP projection',family=family,stage='engineering',configuration=protocol,code_hash=digest(code_manifest(package_root)),data_hashes={'footer_index':index_version},fold_version='no-fit',target_version='compact-literal-parity-v1')
    attempt=registry.start(trial,cpu_reservation_seconds=120);cpu=time.process_time();wall=time.monotonic()
    try:
        q,t,manifest=read_compact_window(data_root=data_root,index=index,dataset=protocol['dataset'],start=start,end=end,maximum_rows=protocol['maximum_rows'])
        qref=registry.artifacts.put_bytes(arrow_bytes(q),kind='arrow_compact_quotes');tref=registry.artifacts.put_bytes(arrow_bytes(t),kind='arrow_compact_trades')
        report={**manifest,'success':True,'quotes_artifact':asdict(qref),'trades_artifact':asdict(tref),'trial_id':trial,'attempt_id':attempt,'code_snapshot':asdict(snapshot),
                'cpu_seconds':time.process_time()-cpu,'wall_seconds':time.monotonic()-wall,'peak_rss_bytes':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss*1024,'economic_runs':0}
        ref=registry.artifacts.put_json(report,kind='compact_projection_pilot')
        registry.finish(attempt,status='succeeded',cpu_seconds=report['cpu_seconds'],wall_seconds=report['wall_seconds'],peak_rss_bytes=report['peak_rss_bytes'],reason='Registered complete window projected; quality channels retained.',result_artifacts=(asdict(ref),asdict(qref),asdict(tref)))
        return {'success':True,'artifact':asdict(ref),'report':str(registry.artifacts.path(ref)),'counts':manifest['counts'],'cpu_seconds':report['cpu_seconds'],'peak_rss_bytes':report['peak_rss_bytes']}
    except BaseException as exc:
        ref=registry.artifacts.put_json({'success':False,'error':type(exc).__name__,'reason':str(exc),'code_snapshot':asdict(snapshot)},kind='failed_compact_projection')
        registry.finish(attempt,status='failed',cpu_seconds=time.process_time()-cpu,wall_seconds=time.monotonic()-wall,peak_rss_bytes=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss*1024,reason=str(exc),result_artifacts=(asdict(ref),));raise
