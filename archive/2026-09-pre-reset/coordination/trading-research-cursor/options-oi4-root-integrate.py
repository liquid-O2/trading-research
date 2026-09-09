from pathlib import Path
import ast,hashlib,json,shutil
C=Path('/workspace/coordination/trading-research-cursor');W=C/'worktrees/options-oi1';R=Path('/workspace/trading-research')
files=['src/trading_research/research/options_oi_columnar.py','src/trading_research/research/options_oi_measurements.py','src/trading_research/research/options_oi_statistics.py','tests/test_options_oi_measurements.py']
B=C/'options-oi4-before-root';B.mkdir(exist_ok=True)
for f in files:shutil.copy2(W/f,B/Path(f).name)
def sub(s,a,b):
 assert a in s,a[:150]
 return s.replace(a,b)
p=W/files[0];s=p.read_text()
s=sub(s,'        return\n        labels = np.array([key or "unknown" for key in keys], dtype=object)','        return\n    labels = np.array([key or "unknown" for key in keys], dtype=object)')
s=sub(s,'return pa.table({name: [row.get(name) for name in names] for name in names}, schema=coverage_schema())','return pa.table({name: [row.get(name) for row in rows] for name in names}, schema=coverage_schema())')
s=sub(s,'        for u, symbol in enumerate(uniq):\n            cid = self.osi_to_cid.get(symbol)','        for u in np.argsort(first_idx, kind="stable"):\n            symbol = uniq[u]\n            cid = self.osi_to_cid.get(symbol)')
s=sub(s,'        self.midnight = {}','        self.midnight = {}\n        self.osi = {}')
s=sub(s,'def _osi_unique_parse(dictionary):','def _osi_unique_parse(dictionary, cache):')
s=sub(s,'parsed = [parse_osi(value) if type(value) is str else None for value in values]','parsed = []\n    for value in values:\n        if value not in cache:\n            cache[value] = parse_osi(value) if type(value) is str else None\n        parsed.append(cache[value])')
s=sub(s,'    osi_parsed, osi_values = _osi_unique_parse(osi_dict)','    osi_parsed, osi_values = _osi_unique_parse(osi_dict, clocks.osi)')
s=sub(s,'        identities.release_keys()','        identities.release_keys()\n        clocks.osi.clear()')
a=s.index('        uniq, inverse = np.unique(np.asarray(ts_arr, dtype=np.int64), return_inverse=True)',s.index('    def seconds_after'))
b=s.index('        sec_u = ',a)
s=s[:a]+'''        uniq, first_idx, inverse = np.unique(np.asarray(ts_arr, dtype=np.int64), return_index=True, return_inverse=True)
        if east_labels is not None and len(east_labels):
            east_u = np.asarray(east_labels, dtype=object)[first_idx]
        else:
            east_u = np.asarray([self.east.get(int(ts)) for ts in uniq], dtype=object)
'''+s[b:]
a=s.index('        uniq = np.unique(days[~nulls])');b=s.index('        return iso, ok, days',a)
s=s[:a]+'''        uniq, inverse = np.unique(days, return_inverse=True)
        iso[:] = np.asarray([dates.iso(int(v)) for v in uniq],dtype=object)[inverse]
        iso[nulls] = None
        ok[:] = ~nulls
'''+s[b:]
a=s.index('    for i in range(n):',s.index('    parsed, parsed_ok = _safe_iso_dates(labels)'));b=s.index('    return iso, ok, days',a)
s=s[:a]+'''    present = ~nulls
    parsed_arr = np.asarray(parsed,dtype=object)
    good_arr = np.asarray(parsed_ok,dtype=bool)
    day_arr = np.asarray([dates.days(x) if good and x is not None else 0 for x,good in zip(parsed,parsed_ok)],dtype=np.int32)
    iso[present] = parsed_arr[inverse[present]]
    ok[present] = good_arr[inverse[present]]
    days[present] = day_arr[inverse[present]]
'''+s[b:]
a=s.index('        uniq = np.unique(strike_f[finite])');b=s.index('        return milli, strike_f, strike_ok, nulls',a)
s=s[:a]+'''        uniq, inverse = np.unique(strike_f[finite], return_inverse=True)
        mapped = [millistrike(float(value)) for value in uniq]
        mapped = np.asarray([-1 if v is None else v for v in mapped],dtype=np.int64)
        strike_ok[finite] = True
        milli[finite] = mapped[inverse]
'''+s[b:]
s=sub(s,'np.array(\n            [(type(value) is str and value != chain) for value in symbols], dtype=bool)','(symbols != chain)')
a=s.index('class TypedAsof:');b=s.index('\ndef _interval_table',a)
s=s[:a]+(C/'options-oi4-vector-asof.txt').read_text()+s[b:]
# Use Arrow masks, preserving every nullable scalar while avoiding Python int/dict materialization.
a=s.index('    prior_ids = ',s.index('def lifecycle_to_table'));b=s.index('    schema = ',a)
s=s[:a]+'''    prior_ids = pa.array(life['prior_report_id'],mask=~life['prior_report_ok'],type=pa.int64())
    next_ids = pa.array(life['next_report_id'],mask=~life['next_report_ok'],type=pa.int64())
    first_delta = pa.array(life['first_delta'],mask=~life['first_usable'],type=pa.int64())
    last_delta = pa.array(life['last_delta'],mask=~life['last_usable'],type=pa.int64())
    listed = pa.array(life['listed_on_prior'],mask=~life['listed_valid'],type=pa.bool_())
'''+s[b:]
s=sub(s,'pa.array([None if v is None else abs(v) for v in first_delta], type=pa.int64())',"pa.array(_np().abs(life['first_delta']),mask=~life['first_usable'],type=pa.int64())")
s=sub(s,'pa.array([None if v is None else abs(v) for v in last_delta], type=pa.int64())',"pa.array(_np().abs(life['last_delta']),mask=~life['last_usable'],type=pa.int64())")
a=s.index('    first_oi = [',s.index('def reports_to_table'));b=s.index('    update = ',a)
s=s[:a]+'''    first_oi = pa.array(reports['first_oi'],mask=~has,type=pa.int64())
    first_ts = pa.array(reports['first_ts'],mask=~has,type=pa.int64())
    first_fid = pa.array(reports['first_fid'],mask=~has,type=pa.int64())
    first_row = pa.array(reports['first_row'],mask=~has,type=pa.int64())
    last_oi = pa.array(reports['last_oi'],mask=last_eq|~has,type=pa.int64())
    last_ts = pa.array(reports['last_ts'],mask=last_eq|~has,type=pa.int64())
    last_fid = pa.array(reports['last_fid'],mask=last_eq|~has,type=pa.int64())
    last_row = pa.array(reports['last_row'],mask=last_eq|~has,type=pa.int64())
'''+s[b:]
s=sub(s,'["same_time_no_winner" if reports["same_time_conflict"][i] else "none" for i in range(n)]','_np().where(reports["same_time_conflict"], "same_time_no_winner", "none")')
s=sub(s,'[int(reports["observed_update_difference"][i]) if update[i] else None for i in range(n)],\n            type=pa.int64()','reports["observed_update_difference"], mask=~update, type=pa.int64()')
# Retain one physical report index list per iterator call, reading lifecycle parts incrementally.
a=s.index('    need_reports = False',s.index('def iter_logical_lifecycle'));b=s.index('\n\ndef read_logical_parts',a)
s=s[:a]+'''    reports = None
    for ref in life_refs:
        table = pq.read_table(ref['path'])
        if _is_compact_lifecycle(table):
            if reports is None:
                reports = _report_index(report_refs if report_refs is not None else _discover_report_refs(life_refs))
            for row in table.to_pylist():
                yield _expand_lifecycle_row(row, reports)
        else:
            yield from table.to_pylist()
'''+s[b:]
p.write_text(s)
# Add production vector-vs-literal state regression with later-reported conflicts/old clocks and pending rows.
p=W/files[3];s=p.read_text();pos=s.index('\nif __name__ == "__main__":')
s=s[:pos]+'''\nclass RootColumnarStateTests(unittest.TestCase):
    def test_array_timeline_matches_literal_all_intervals_and_cut_counts(self):
        from trading_research.research.options_oi_measurements import AsofTimeline
        from trading_research.research.options_oi_columnar import TypedAsof, DateCodebook
        literal=AsofTimeline('NDX');typed=TypedAsof('NDX',DateCodebook(),{})
        a=cut_ns_on('2020-01-02','06:30');b=cut_ns_on('2020-01-03','06:30')
        closed=[];actual=[]
        for day,rows in [('2020-01-02',[(1,a,100),(2,a,20),(2,a,25),(3,b+12*3600*1000000000,70)]),
                         ('2020-01-03',[(1,a-1,60),(1,a,120),(2,b,30),(4,b,50)])]:
            cols=list(zip(*rows));n=len(rows)
            args=(cols[0],cols[1],cols[2],[day]*n,[1]*n,list(range(n)),['2020-01-17']*n)
            literal.add(*args);typed.add(*args)
            for label in ['09:30','10:00','15:00']:
                cut=cut_ns_on(day,label)
                closed+=literal.apply_through(cut,day)
                part=typed.apply_through(cut,day)
                if part is not None:actual+=part.to_pylist()
                self.assertEqual(typed.snapshot_counts(cut,day,[1,2,3,4],'2020-01-02'),literal.snapshot_counts(cut,day,[1,2,3,4],'2020-01-02'))
        closed+=literal.apply_through(9223372036854775807,'9999-12-31')
        part=typed.apply_through(9223372036854775807,'9999-12-31')
        if part is not None:actual+=part.to_pylist()
        closed+=list(literal.open.values());actual+=typed.open_table().to_pylist()
        key=lambda r:(r['contract_id'],r['valid_from_ns'],r['ts_event_ns'])
        self.assertEqual(sorted(actual,key=key),sorted(closed,key=key))

''' +s[pos:];p.write_text(s)
for f in files:ast.parse((W/f).read_text())
(C/'options-oi4-root-review.json').write_text(json.dumps({'scope':'Same pilot2 logical semantics and unchanged family limits; full candidate not yet tested.','files':{f:hashlib.sha256((W/f).read_bytes()).hexdigest() for f in files},'corrections':['Fixed unbound labels and coverage comprehension.','Stable first-seen identity IDs.','Vector date/millistrike/unique clock gather and per-chain OSI cache.','Arrow report/lifecycle null masks.','Replaced repeated per-contract as-of dictionaries with independent typed column waves; retained later-clock conflicts/aliases/older-clock/pending semantics.','Added exact logical literal state regression.'],'verification':'Registered pilot4 must compare complete accepted pilot2 logical table populations plus frozen43checks and measured resource projection.'},indent=2)+'\n')
print('reviewed; ready to integrate4files')
