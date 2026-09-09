from pathlib import Path
p=Path('/workspace/trading-research/src/trading_research/research/options_quote_measurements.py');s=p.read_text()
a=s.index('def _cut_board_hists(');b=s.index('\ndef _freeze_hists',a)
s=s[:a]+'''def _cut_board_hists(store, board_rows):
    np = _np()
    view = _BoardColumns(board_rows)
    if not len(view):
        return
    eligible = view.values('quoted') & view.values('usable')
    right = np.full(len(view), -1, dtype=np.int8)
    dte = np.full(len(view), -1, dtype=np.int8)
    for code, name in RIGHT_NAMES.items():
        right[view.values('right') == name] = code
    for code, name in enumerate(DTE_NAMES):
        dte[view.values('dte_bucket') == name] = code
    categories = _right_dte_codes(right,dte)
    for family in FAMILY_NAMES:
        for cut in ALL_CUTS:
            mask = eligible & (view.values('source_family') == family) & (view.values('cut_label') == cut)
            if not np.any(mask):
                continue
            for metric,field,scale in (('bid','bid',1),('ask','ask',1),('mid','mid',1),
                    ('spread','spread',1),('sample_age_s','sample_age_ns',NS),
                    ('payload_age_s','unchanged_payload_age_ns',NS)):
                _hist_batch(store,metric,'cut',family,cut,right,dte,
                    view.values(field)/scale,mask & view.present(field),category_codes=categories)

''' +s[b:]
a=s.index('def _coverage_row(');b=s.index('\ndef _support_bundle',a)
old=s[a:b];ret=old[old.index('    return {'):]
# Keep the exact public metadata and count keys, change only the reduction source.
ret=ret.replace('bool(quoted)','bool(nquoted)').replace('len(quoted)','nquoted').replace('len(usable)','nusable')
ret=ret.replace('len(listed_quoted)',"view.count(quoted & listed & listed_known)")
ret=ret.replace('len(quoted_unlisted)',"view.count(quoted & ~listed & listed_known)")
ret=ret.replace('len(listed_unquoted)',"view.count(~quoted & listed & listed_known)")
ret=ret.replace('len(ages)',"view.count(ages)").replace('len(oi_universe)',"view.count(oi_universe)")
for key in ('sample_stale_60','sample_stale_300','sample_stale_900','payload_stale_60','payload_stale_300','payload_stale_900'):
 ret=ret.replace(f'sum(1 for row in ages if row["{key}"])',f"view.count(ages & view.values('{key}'))")
for prefix,field in (('bid','bid'),('ask','ask'),('mid','mid'),('spread','spread'),('rel_spread','relative_spread')):
 ret=ret.replace(f'sum(row["{field}"] for row in usable if row.get("{field}") is not None)',f"view.sum('{field}', usable)")
 ret=ret.replace(f'sum(1 for row in usable if row.get("{field}") is not None)',f"view.count(usable & view.present('{field}'))")
ret=ret.replace('sum((row["sample_age_ns"] or 0) / NS for row in ages)',"float((view.values('sample_age_ns')[ages] / NS).sum())")
ret=ret.replace('sum((row["unchanged_payload_age_ns"] or 0) / NS for row in ages)',"float((view.values('unchanged_payload_age_ns')[ages] / NS).sum())")
ret=ret.replace('sum(1 for row in oi_universe if row["quoted"])',"view.count(oi_universe & quoted)")
for flag in ('oi_missing','oi_ambiguous','oi_zero'):
 ret=ret.replace(f'sum(1 for row in board_rows if row["{flag}"])',f"view.count(view.values('{flag}'))")
ret=ret.replace('sum(1 for row in board_rows if row["oi"] is None and not row["oi_available"])',"view.count(~view.present('oi') & ~oi_universe)")
ret=ret.replace('sum(1 for row in board_rows if row.get("dte_bucket") == "61+" and row["listed"] is True)',"view.count((view.values('dte_bucket') == '61+') & listed & listed_known)")
ret=ret.replace('0 if quoted else 1','0 if nquoted else 1')
assert 'for row in' not in ret
s=s[:a]+'''def _coverage_row(*, chain, declared, cut_label, family, intended, session, missing_file,
                  empty_marker, early_na, board_rows, listing):
    view = _BoardColumns(board_rows)
    quoted = view.values('quoted')
    usable = quoted & view.values('usable')
    listed, listed_known = view.values('listed'), view.present('listed')
    oi_universe = view.values('oi_available')
    universe = oi_universe & view.present('oi') & (view.values('oi') >= 0)
    total = int(view.sum('oi',universe))
    weighted = None if total <= 0 else int(view.sum('oi',universe & quoted)) / total
    classes = {name:view.count(quoted & (view.values('base_class') == name)) for name in BASE_CLASSES}
    applicable = not early_na
    ages = quoted & view.present('sample_age_ns')
    nquoted, nusable = view.count(quoted), view.count(usable)
''' +ret+s[b:]
a=s.index('def _board_slices(');b=s.index('\ndef _cut_plan',a)
s=s[:a]+'''def _board_slices(board_rows):
    np = _np()
    view = _BoardColumns(board_rows)
    quoted = view.values('quoted')
    slices = {}
    for family in FAMILY_NAMES:
        for cut in ALL_CUTS:
            base = quoted & (view.values('source_family') == family) & (view.values('cut_label') == cut)
            if not np.any(base):
                continue
            for right in ('CALL','PUT','unknown'):
                rm = base & ((view.values('right') == right) if right != 'unknown' else
                             ~np.isin(view.values('right'),('CALL','PUT')))
                for dte in (*DTE_NAMES,'unknown'):
                    mask = rm & ((view.values('dte_bucket') == dte) if dte != 'unknown' else
                                 ~np.isin(view.values('dte_bucket'),DTE_NAMES))
                    if not np.any(mask):
                        continue
                    cls = view.values('base_class')
                    bag = {'quoted':view.count(mask),'usable':view.count(mask & view.values('usable')),
                        'conflict':view.count(mask & (cls == 'conflict')),
                        'invalid':view.count(mask & np.isin(cls,('invalid_identity','invalid_clock','invalid_numeric')))}
                    for name in ('all_zero','one_sided','crossed','locked','two_sided'):
                        bag[name] = view.count(mask & (cls == name))
                    for name in ('bid','ask','mid','spread'):
                        bag[name+'_sum'] = float(view.sum(name,mask))
                        bag[name+'_n'] = view.count(mask & view.present(name))
                    ages = mask & view.present('sample_age_ns')
                    bag['sample_age_sum'] = float((view.values('sample_age_ns')[ages]/NS).sum())
                    bag['payload_age_sum'] = float((view.values('unchanged_payload_age_ns')[ages]/NS).sum())
                    bag['age_n'] = view.count(ages)
                    for name in ('sample_stale_60','sample_stale_300','sample_stale_900',
                                 'payload_stale_60','payload_stale_300','payload_stale_900'):
                        bag[name] = view.count(ages & view.values(name))
                    slices['|'.join((family,cut,right,dte))] = bag
    return slices


def _date_aggregate(chain, declared, intended, session, family_quality, coverage_rows, board_rows,
                    support_rows, paired, hists, unique_by_family=None, paired_by_cut=None):
    np = _np()
    raw_rows = sum(row['raw_rows'] for row in family_quality if row['source_family'] != 'union')
    unique_family = 'union' if any(row['source_family'] == 'union' for row in family_quality) else 'vix_full'
    unique_events = sum(row['unique_events'] for row in family_quality if row['source_family'] == unique_family)
    view = _BoardColumns(board_rows)
    quotes = view.values('quoted')
    usable = quotes & view.values('usable') & view.present('mid')
    canon_family = 'union' if np.any(quotes & (view.values('source_family') == 'union')) else 'near'
    canon = usable & (view.values('cut_label') == '10:00') & (view.values('source_family') == canon_family)
    if not np.any(canon):
        canon = usable & (view.values('source_family') == canon_family)
    bids = canon & view.present('bid')
    bid_count, bid_sum = view.count(bids), float(view.sum('bid',bids))
    def unique_count(mask):
        return int(len(np.unique(view.values('contract_id')[mask])))
    return {
        'chain':chain, 'request_date':declared, 'intended':intended, 'session_state':session.state,
        'raw_rows':raw_rows, 'unique_events':unique_events, 'unique_events_by_family':unique_by_family or {},
        'cut_board_rows':len(view),
        'quoted_contracts':unique_count(quotes & view.values('identity_resolved')),
        'listed_contracts':unique_count(view.values('listed') & view.present('listed')),
        'oi_matched_contracts':unique_count(view.values('oi_available')),
        'usable_quotes':view.count(usable), 'mean_bid':None if not bid_count else bid_sum/bid_count,
        'raw_bid_sum':bid_sum, 'raw_bid_n':bid_count,
        'quality':family_quality, 'coverage':coverage_rows, 'support':support_rows,
        'paired_near_broad':paired, 'paired_by_cut':paired_by_cut or {}, 'histograms':hists,
        'slices':_board_slices(board_rows),
        'by_cut':{label:{'quoted':view.count(quotes & (view.values('cut_label') == label)),
                         'usable':view.count(usable & (view.values('cut_label') == label))} for label in ALL_CUTS},
    }

''' +s[b:]
s=s.replace('    if not rows:\n        return schema.empty_table()','    if rows is None or len(rows) == 0:\n        return schema.empty_table()')
p.write_text(s)
