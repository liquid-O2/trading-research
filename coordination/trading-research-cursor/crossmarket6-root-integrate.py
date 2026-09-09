from pathlib import Path
import ast,shutil,json,hashlib
root=Path('/workspace/trading-research');coord=Path('/workspace/coordination/trading-research-cursor');wt=coord/'worktrees/crossmarket1'
p=wt/'src/trading_research/research/cross_market_alignment.py';s=p.read_text()
# NumPy object arrays require scalar fill to retain tuple-valued reasons.
s=s.replace('reasons[:] = ("missing_first_minute",)','reasons.fill(("missing_first_minute",))')
s=s.replace('reasons[done] = ()', 'reasons[done] = [()] * int(done.sum())')
# A list of tuples is still two-dimensional on NumPy assignment: assign tuple scalars.
s=s.replace('reasons[done] = [()] * int(done.sum())', 'reasons[done] = None')
# None is exactly the empty-reason serialization for complete paths; scalar API restores ().
s=s.replace('why[:] = ("incomplete_future",)','why.fill(("incomplete_future",))')
s=s.replace('why[names == "roll"] = ("raw_contract_transition",)', 'why[names == "roll"] = "raw_contract_transition"')
s=s.replace('why[names == "no_receiver"] = ("missing_all_minutes",)', 'why[names == "no_receiver"] = "missing_all_minutes"')
s=s.replace('reasons[mismatch] = ("reference_contract_mismatch",)', 'reasons[mismatch] = "reference_contract_mismatch"')
# Keep every vector reason element a tuple by normalizing only unique reason classes.
s=s.replace('    return {\n        "status": status, "reasons": reasons,', '    reasons = np.asarray([() if x is None else (x,) if isinstance(x, str) else x for x in reasons], dtype=object) if False else reasons\n    for i in range(n):\n        value = reasons[i]\n        reasons[i] = () if value is None else (value,) if isinstance(value, str) else value\n    return {\n        "status": status, "reasons": reasons,')
s=s.replace('    reasons = np.asarray([() if x is None else (x,) if isinstance(x, str) else x for x in reasons], dtype=object) if False else reasons\n','')
ast.parse(s);p.write_text(s)
p=wt/'src/trading_research/research/cross_market_descriptive.py';s=p.read_text();baseline=(root/'src/trading_research/research/cross_market_descriptive.py').read_text()
# Array data must stay stable while shifting retained rows before append().
s=s.replace('pa.array(self._values[name][:take], mask=self._null[name][:take], type=field.type)', 'pa.array(self._values[name][:take].copy(), mask=self._null[name][:take], type=field.type)')
# Scalar reference for complete one-day fieldwise verification, retained from original corrected implementation.
ref=baseline[baseline.index('def process_year('):baseline.index('\ndef _write_mapping_cuts(')]
ref=ref.replace('def process_year(', 'def process_year_reference(').replace('        _emit_source_events(\n', '        _emit_source_events_reference(\n')
s+='\n\n'+ref
s=s.replace('def _emit_source_events_legacy(', 'def _emit_source_events_reference(')
s=s.replace('calendar, event_seq, label_ids):\n    return\n    sess_start,', 'calendar, event_seq, label_ids):\n    sess_start,')
# Return only priced indices/identities from event joins, matching _past_receiver.
a=s.index('def _join_event_cuts(');b=s.index('\ndef _collect_source_events(',a);piece=s[a:b]
piece=piece.replace('    return {\n', '    idx = np.where(priced, idx, -1)\n    close[~priced] = np.nan\n    ckey[~priced] = None\n    return {\n')
piece=piece.replace('"missing": ~present,', '"missing": ~priced,')
s=s[:a]+piece+s[b:]
# Equal-date aggregate output must not materialize all rows.
a=s.index('def _write_date_aggregates(');b=s.index('\ndef _group_intended(',a)
s=s[:a]+baseline[baseline.index('def _write_date_aggregates('):baseline.index('\ndef _group_intended(')]+s[b:]
s=s.replace('                    lb_out["relative_volume"][dest] = rel\n', '                    lb_out["relative_volume"][dest] = np.where(row["priced"], rel, np.nan)\n')
s=s.replace('                    lb_out["prior_rth_sqrt_rv"][dest] = scale\n', '                    lb_out["prior_rth_sqrt_rv"][dest] = np.where(row["priced"], scale, np.nan)\n')
s=s.replace('                    lb_nulls["relative_volume"][dest] = ~np.isfinite(rel)', '                    lb_nulls["relative_volume"][dest] = ~row["priced"] | ~np.isfinite(rel)')
s=s.replace('                    lb_nulls["prior_rth_sqrt_rv"][dest] = ~np.isfinite(scale)', '                    lb_nulls["prior_rth_sqrt_rv"][dest] = ~row["priced"] | ~np.isfinite(scale)')
s=s.replace('horizon=None), day, rel[sel])', 'horizon=None), day, rel[sel], missing=~row["priced"][sel])')
# Preassign receiver IDs in old event/receiver/lag/horizon order before vector computation.
a=s.index('def _emit_source_events(');b=s.index('\ndef _emit_source_events_reference(',a);piece=s[a:b]
old='        src_contract = prep.contract_key[idx]\n        src_start = source.start_ns[idx]\n'
new=old+'''        pending_label_keys = set()
        eligible_receivers = [r for r in receivers if (source.symbol, r.symbol) in DIRECTED_PAIRS
                              and not (source.symbol == r.symbol and source.variant == r.variant)]
        label_starts_by_lag = {lag: ceil_to_minute_array(clocks[lag][idx]) for lag in LATENCY_AFTER_END_S}
        for event_i in range(n_ev):
            for target in eligible_receivers:
                for lag in LATENCY_AFTER_END_S:
                    label_start = int(label_starts_by_lag[lag][event_i])
                    for horizon in FUTURE_HORIZONS:
                        key = (target.symbol, target.variant, lag, horizon, label_start)
                        if key not in label_ids:
                            label_ids[key] = label_ids['_next']
                            label_ids['_next'] += 1
                            pending_label_keys.add(key)
'''
assert old in piece;piece=piece.replace(old,new)
old='''                        label_id = label_ids.get(key)
                        if label_id is None:
                            label_id = label_ids["_next"]
                            label_ids["_next"] = label_id + 1
                            label_ids[key] = label_id
                            raw = block["raw"]'''
new='''                        label_id = label_ids[key]
                        if key in pending_label_keys:
                            pending_label_keys.remove(key)
                            raw = block["raw"]'''
assert old in piece;piece=piece.replace(old,new);s=s[:a]+piece+s[b:]
ast.parse(s);p.write_text(s)
# Check complete logical rows and date sums/counts against preserved scalar path.
p=wt/'tests/test_cross_market_descriptive.py';s=p.read_text();s+='''

class RootVectorEndToEndParity(unittest.TestCase):
    def test_all_day_tables_and_date_counts_match_retained_scalar(self):
        import collections
        import trading_research.research.cross_market_descriptive as cm
        class Capture:
            def __init__(self, schema): self.schema, self.rows = schema, []
            def add(self, row): self.rows.append({f.name: row.get(f.name) for f in self.schema})
            def add_columns(self, data, *, length, nulls=None):
                nulls = nulls or {}
                for i in range(length):
                    row = {}
                    for f in self.schema:
                        col = data.get(f.name)
                        value = None if col is None or (f.name in nulls and nulls[f.name][i]) else col[i]
                        if value is not None and hasattr(value, 'item'): value = value.item()
                        if isinstance(value, float) and not math.isfinite(value): value = None
                        row[f.name] = value
                    self.rows.append(row)
            def extend(self, rows):
                for row in rows:self.add(row)
        day = date(2020, 1, 6)
        start = local_timestamp(day, time(9, 30), NY)
        units = {}
        for symbol, base, variant in [('YM',100,'primary_corrected'),('NQ',1000,'primary_corrected'),
                                     ('ES',500,'primary_corrected'),('NQ',1001,'original_nq2024_sensitivity'),
                                     ('QQQ',100,'primary_corrected')]:
            closes = [base + (i % 9) * .1 + i * .01 for i in range(80)]
            unit = _bars(symbol, start, closes, variant=variant)
            units[(symbol,variant,2020)] = unit
        schemas = {'cuts':cm.aligned_schema(), 'smt':cm.smt_schema(), 'lookbacks':cm.lookback_schema(),
                   'mapping':cm.mapping_schema(), 'source_events':cm.source_event_schema(),
                   'receiver_labels':cm.receiver_label_schema(), 'event_links':cm.event_link_schema(),
                   'contrasts':cm.contrast_schema()}
        results=[]
        for method in (cm.process_year_reference, cm.process_year):
            writers={key:Capture(schema) for key,schema in schemas.items()}
            groups=collections.defaultdict(cm._empty_group)
            method(year=2020,units=units,calendar=CashCalendar(CALENDAR),writers=writers,groups=groups,
                   intended_dates=[],carry={},variant_dates={},fixture_dates=[day],event_seq=[1],label_ids={'_next':1})
            results.append((writers,groups))
        def norm(value):
            if isinstance(value,float):return round(value,12)
            return value
        for name in schemas:
            expected=collections.Counter(tuple(norm(r[f.name]) for f in schemas[name]) for r in results[0][0][name].rows)
            actual=collections.Counter(tuple(norm(r[f.name]) for f in schemas[name]) for r in results[1][0][name].rows)
            if expected!=actual:
                self.fail(name+' logical mismatch: '+repr(list((expected-actual).items())[:2])+' vs '+repr(list((actual-expected).items())[:2]))
        self.assertEqual(set(results[0][1]),set(results[1][1]))
        for key in results[0][1]:
            a,b=results[0][1][key],results[1][1][key]
            self.assertEqual(dict(a['count']),dict(b['count']),repr(key))
            for label,total in a['sum'].items():self.assertAlmostEqual(total,b['sum'][label],places=10,msg=repr(key))

    def test_writer_batch_overflow_preserves_pre_shift_int64_values(self):
        import numpy as np
        import trading_research.research.cross_market_descriptive as cm
        with tempfile.TemporaryDirectory() as folder:
            outputs=BoundedOutputs(Path(folder)/'out',maximum_total_bytes=32*1024**2,maximum_file_bytes=16*1024**2)
            writer=cm._SeriesWriter(outputs,'overflow',cm.source_event_schema())
            clocks=np.arange(cm.CHUNK+37,dtype=np.int64)+1600000000000000001
            writer.add_columns({'source_start_ns':clocks},length=len(clocks))
            ref=writer.finish()
            values=[v for t in read_series_tables(ref) for v in t['source_start_ns'].to_pylist()]
            self.assertEqual(values,clocks.tolist())
'''
# Obtain exact observed schema function names from AST, without candidate import.
names={n.name for n in ast.parse((wt/'src/trading_research/research/cross_market_descriptive.py').read_text()).body if isinstance(n,ast.FunctionDef)}
print(sorted(n for n in names if n.endswith('_schema')))
ast.parse(s);p.write_text(s)
backup=coord/'crossmarket6-before-root';backup.mkdir(exist_ok=True)
for rel in ['src/trading_research/research/cross_market_alignment.py','src/trading_research/research/cross_market_descriptive.py','tests/test_cross_market_descriptive.py']:
 dst=root/rel;shutil.copy2(dst,backup/dst.name);shutil.copy2(wt/rel,dst)
print('integrated three files; no tests/imports executed')
