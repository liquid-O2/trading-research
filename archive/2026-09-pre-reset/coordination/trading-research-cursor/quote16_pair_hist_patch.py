from pathlib import Path
p=Path('/workspace/trading-research/src/trading_research/research/options_quote_measurements.py');s=p.read_text()
pos=s.index('\ndef _source_frame_hists(')
s=s[:pos]+'''
def _source_hist_populations(store, metric, family, values, present, unique, codes, include_raw):
    """One exact value/category sort provides both physical and unique counts."""
    np = _np()
    valid = present & np.isfinite(values)
    if not include_raw:
        valid &= unique
    if not np.any(valid):
        return
    value, category, kept = values[valid], codes[valid], unique[valid]
    order = np.lexsort((value, category))
    value, category, kept = value[order], category[order], kept[order]
    starts = np.r_[0, np.flatnonzero((value[1:] != value[:-1]) | (category[1:] != category[:-1])) + 1]
    raw_count = np.diff(np.r_[starts, len(value)]).astype(np.int64)
    unique_count = np.add.reduceat(kept.astype(np.int64), starts)
    value, category = value[starts], category[starts]
    groups = np.r_[0, np.flatnonzero(category[1:] != category[:-1]) + 1, len(category)]
    for begin,end in zip(groups[:-1],groups[1:]):
        right,dte = divmod(int(category[begin]),len(DTE_NAMES)+1)
        right_label = RIGHT_NAMES.get(right-1,'unknown')
        dte_label = DTE_NAMES[dte-1] if 0 < dte <= len(DTE_NAMES) else 'unknown'
        prefix = f'{family}|-|{right_label}|{dte_label}'
        if include_raw:
            _hist_merge(store,f'{metric}|raw_source|{prefix}',value[begin:end],raw_count[begin:end])
        keep = unique_count[begin:end] > 0
        if np.any(keep):
            _hist_merge(store,f'{metric}|unique_source|{prefix}',value[begin:end][keep],unique_count[begin:end][keep])

''' + s[pos:]
start=s.index('        selected = keep & present',s.index('def _source_frame_hists('));end=s.index('\n\ndef _cut_board_hists',start)
s=s[:start]+'''        _source_hist_populations(store,metric,family,values,present,keep,codes,include_raw)
''' + s[end:]
pos=s.index('\ndef _paired_stats(')
s=s[:pos]+'''
def _paired_arrow_stats(near, broad):
    """Integer-key intersection and payload equality with original last-row tie policy."""
    np, pa, pc = _np(), _pa(), _pc()
    near, broad = near.filter(near['quoted']), broad.filter(broad['quoted'])
    sizes = (len(near),len(broad))
    all_rows = pa.concat_tables([near,broad])
    if not len(all_rows):
        return dict.fromkeys(('common','agree','conflict','near_only','broad_only','unmatched_sample_clocks'),0)
    cut_codes = pc.dictionary_encode(all_rows['cut_label']).combine_chunks()
    # Cuts are explicit nonnull output keys; fixtures use arbitrary literal labels.
    cut = cut_codes.indices.to_numpy(zero_copy_only=False)
    cid = all_rows['contract_id'].combine_chunks().to_numpy(zero_copy_only=False)
    ts = all_rows['ts_event_ns'].combine_chunks()
    valid = ~pc.is_null(ts).to_numpy(zero_copy_only=False)
    stamps = ts.fill_null(0).to_numpy(zero_copy_only=False)
    source_positions = np.flatnonzero(valid)
    keys, inverse = _lex_unique_integer_rows((cid[valid],cut[valid],stamps[valid]))
    a = np.full(len(keys),-1,dtype=np.int64)
    b = np.full(len(keys),-1,dtype=np.int64)
    near_mask = source_positions < sizes[0]
    np.maximum.at(a,inverse[near_mask],source_positions[near_mask])
    np.maximum.at(b,inverse[~near_mask],source_positions[~near_mask])
    common = (a >= 0) & (b >= 0)
    left, right = a[common], b[common]
    view = _BoardColumns(all_rows)
    equal = ~view.values('conflict')[left] & ~view.values('conflict')[right]
    for name,null in (('bid','bid_null'),('ask','ask_null'),('bid_size','bid_size_null'),
                     ('ask_size','ask_size_null'),('bid_exchange','bid_ex_null'),
                     ('ask_exchange','ask_ex_null'),('bid_condition','bid_cond_null'),
                     ('ask_condition','ask_cond_null')):
        flags = view.values(null)
        values, present = view.values(name), view.present(name)
        same_value = ((~present[left] & ~present[right]) |
                      (present[left] & present[right] & (values[left] == values[right])))
        equal &= (flags[left] & flags[right]) | (~flags[left] & ~flags[right] & same_value)
    clock_keys,_ = _lex_unique_integer_rows((cid,cut))
    common_clocks,_ = _lex_unique_integer_rows((keys[common,0],keys[common,1]))
    ncommon, nagree = int(common.sum()),int(equal.sum())
    return {'common':ncommon,'agree':nagree,'conflict':ncommon-nagree,
            'near_only':int(((a >= 0) & (b < 0)).sum()),
            'broad_only':int(((b >= 0) & (a < 0)).sum()),
            'unmatched_sample_clocks':len(clock_keys)-len(common_clocks)}

''' + s[pos:]
s=s.replace('''    names = ('contract_id','cut_label','ts_event_ns','quoted','conflict','bid','ask',
''','''    if isinstance(near_rows, _pa().Table) and isinstance(broad_rows, _pa().Table):
        return _paired_arrow_stats(near_rows,broad_rows)
    names = ('contract_id','cut_label','ts_event_ns','quoted','conflict','bid','ask',
''')
# Match stable first-position semantics when all four keys tie exactly.
s=s.replace('''        sid = frame['sort_id'][idx]
        return idx[np.r_[sid[1:] != sid[:-1], True]]
''','''        sid = frame['sort_id'][idx]
        equal_keys = np.ones(max(0,len(idx)-1),dtype=bool)
        for name in ('sort_id','ts_event_ns','file_id','row_index'):
            values = frame[name][idx]
            equal_keys &= values[1:] == values[:-1]
        if not np.any(equal_keys):
            return idx[np.r_[sid[1:] != sid[:-1], True]]
''')
p.write_text(s)
import ast;ast.parse(s)
