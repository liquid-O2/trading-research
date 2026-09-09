from pathlib import Path
p=Path('/workspace/trading-research/src/trading_research/research/options_quote_measurements.py');s=p.read_text()
old='''    if np.any(both):
        exp_u, exp_inv = np.unique(exp_days[both], return_inverse=True)
        req_u, req_inv = np.unique(req_days[both], return_inverse=True)
        grid = np.empty((len(exp_u), len(req_u)), dtype=np.int64)
        for i, exp in enumerate(exp_u):
            for j, req in enumerate(req_u):
                grid[i, j] = dte_days(dates.iso(int(exp)), dates.iso(int(req)))
        dte_v[np.flatnonzero(both)] = grid[exp_inv, req_inv]
'''
new='''    if np.any(both):
        # Both arrays are exact civil-day ordinals from the same codebook.
        dte_v[both] = exp_days[both].astype(np.int64) - req_days[both].astype(np.int64)
'''
assert old in s;s=s.replace(old,new)
old='''        labels = clocks.eastern_labels(ts_arr)
        uniq, inverse = np.unique(np.asarray(labels, dtype=object), return_inverse=True)
        days_u = np.array([
            -1 if lab is None else int(dates.days(lab) if type(lab) is str else dates.days(str(lab)))
            for lab in uniq
        ], dtype=np.int32)
        east_days = days_u[inverse]
'''
new='''        east_days = _eastern_day_codes(ts_arr, dates, clocks)
'''
assert old in s;s=s.replace(old,new)
pos=s.index('\ndef parse_quote_typed(')
s=s[:pos]+'''
def _eastern_day_codes(timestamps, dates, clocks):
    """Convert distinct integer timestamps, never sort per-row Python date strings."""
    np = _np()
    stamps, inverse = np.unique(timestamps, return_inverse=True)
    labels = clocks.eastern_labels(stamps)
    days = np.asarray([-1 if label is None else dates.days(str(label)) for label in labels],
                      dtype=np.int32)
    return days[inverse]


def _frame_is_ordered(frame):
    """Lexicographic order of (identity, time, file, row), including exact ties."""
    np = _np()
    undecided = np.ones(max(0, frame['n'] - 1), dtype=bool)
    for name in ('sort_id','ts_event_ns','file_id','row_index'):
        values = frame[name]
        if np.any(undecided & (values[1:] < values[:-1])):
            return False
        undecided &= values[1:] == values[:-1]
    return True

''' + s[pos:]
start=s.index('def annotate_runs(');end=s.index('\ndef _void_keys',start);b=s[start:end]
old='''    order = np.lexsort((frame["row_index"], frame["file_id"], frame["ts_event_ns"], frame["sort_id"]))
    for name in FRAME_ARRAYS:
        frame[name] = frame[name][order]
'''
new='''    if not _frame_is_ordered(frame):
        order = np.lexsort((frame["row_index"], frame["file_id"], frame["ts_event_ns"], frame["sort_id"]))
        for name in FRAME_ARRAYS:
            frame[name] = frame[name][order]
'''
assert old in b;b=b.replace(old,new);s=s[:start]+b+s[end:]
old='''    idx = np.flatnonzero(eligible)
    order = np.lexsort((
        -frame["row_index"][idx], -frame["file_id"][idx], -ts[idx], frame["sort_id"][idx],
    ))
'''
new='''    idx = np.flatnonzero(eligible)
    if _frame_is_ordered(frame):
        # Sorted frames contain each resolved timestamp once after deduplication.
        # The last eligible entry per identity matches descending time/file/row.
        sid = frame['sort_id'][idx]
        return idx[np.r_[sid[1:] != sid[:-1], True]]
    order = np.lexsort((
        -frame["row_index"][idx], -frame["file_id"][idx], -ts[idx], frame["sort_id"][idx],
    ))
'''
assert old in s;s=s.replace(old,new)
# Reuse the immutable day identity table for every unquoted cut/family.
old='''    identities = [oi_join.identity_fields(int(cid)) for cid in unquoted]
    expiration = [row.get('expiration') for row in identities]
    dte = [dte_days(exp, declared) if exp and declared else None for exp in expiration]
'''
new='''    identity_table = _unquoted_identity_columns(oi_join, declared, unquoted)
'''
assert old in s;s=s.replace(old,new)
old='''        'osi_symbol':[row.get('osi_symbol') for row in identities], 'expiration':expiration,
        'millistrike':[row.get('millistrike') for row in identities],
        'right':[row.get('right') for row in identities], 'dte':dte,
        'dte_bucket':[quote_dte_bucket(value) for value in dte],
'''
new='''        **{name:identity_table[name] for name in identity_table.schema.names},
'''
assert old in s;s=s.replace(old,new)
pos=s.index('\ndef _listed_unquoted_rows(')
s=s[:pos]+'''
def _unquoted_identity_columns(oi_join, declared, cids):
    np, pa = _np(), _pa()
    cached = getattr(oi_join, '_unquoted_day_columns', None)
    if cached is None or cached[0] != declared:
        horizon = getattr(oi_join, '_horizon', None) or {}
        arrays = [np.asarray(cids, dtype=np.int64)]
        for name in ('listed_ids','cid'):
            values = horizon.get(name)
            if values is not None:
                arrays.append(np.asarray(values, dtype=np.int64))
        ids = np.unique(np.concatenate(arrays))
        cached = None
    else:
        ids = cached[1]
        positions = np.searchsorted(ids, cids)
        if np.any(positions >= len(ids)) or np.any(ids[np.minimum(positions,len(ids)-1)] != cids):
            ids = np.unique(np.concatenate((ids,cids)))
            cached = None
    if cached is None:
        identities = [oi_join.identity_fields(int(cid)) for cid in ids]
        expiration = [row.get('expiration') for row in identities]
        dte = [dte_days(exp, declared) if exp and declared else None for exp in expiration]
        schema = cut_board_schema()
        columns = {
            'osi_symbol':[row.get('osi_symbol') for row in identities], 'expiration':expiration,
            'millistrike':[row.get('millistrike') for row in identities],
            'right':[row.get('right') for row in identities], 'dte':dte,
            'dte_bucket':[quote_dte_bucket(value) for value in dte],
        }
        table = pa.Table.from_arrays([pa.array(values,type=schema.field(name).type)
            for name,values in columns.items()],names=list(columns))
        cached = (declared,ids,table)
        oi_join._unquoted_day_columns = cached
    return cached[2].take(pa.array(np.searchsorted(cached[1],cids)))

''' + s[pos:]
s=s.replace('''    def release_day(self):
        self._horizon = None
''','''    def release_day(self):
        self._horizon = None
        self._unquoted_day_columns = None
''')
# Support selection is identical at all cuts of one civil date.
start=s.index('    def fred_at(self, cut_date):');end=s.index('\n    def actions_at',start);b=s[start:end]
b=b.replace('''        np = _np()
''','''        cached = getattr(self, '_fred_last_date', None)
        if cached is not None and cached[0] == cut_date:
            return [dict(row) for row in cached[1]]
        np = _np()
''',1)
b=b.replace('''        return rows
''','''        self._fred_last_date = (cut_date, tuple(dict(row) for row in rows))
        return rows
''');s=s[:start]+b+s[end:]
p.write_text(s)
import ast;ast.parse(s)
