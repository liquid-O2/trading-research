from pathlib import Path
p=Path('/workspace/trading-research/src/trading_research/research/options_quote_measurements.py')
s=p.read_text()
s=s.replace('''    return pa.table({field.name: [row.get(field.name) for row in rows] for field in schema},
                    schema=schema)''','''    if isinstance(rows, pa.Table):
        if rows.schema != schema:
            raise IntegrityError("table schema differs from the declared output")
        return rows
    return pa.Table.from_pylist(rows, schema=schema)''')
a=s.index('def _source_frame_hists(');b=s.index('\ndef _cut_board_hists',a)
s=s[:a]+'''def _source_frame_hists(store, frame, family, *, include_raw=True):
    np = _np()
    if frame is None or not frame["n"]:
        return
    codes = _right_dte_codes(frame["right_code"], frame["dte_code"])
    keep = frame["keep"] & ~frame["unique_conflict"]
    usable = frame["usable_raw"] & ~frame["bid_null"] & ~frame["ask_null"]
    for metric, values, present in (
        ("bid", frame["bid"], ~frame["bid_null"]),
        ("ask", frame["ask"], ~frame["ask_null"]),
        ("mid", (frame["bid"] + frame["ask"]) / 2.0, usable),
        ("spread", frame["ask"] - frame["bid"], usable),
    ):
        selected = keep & present
        _hist_batch(store, metric, "unique_source", family, "-", frame["right_code"],
                    frame["dte_code"], values, selected, category_codes=codes)
        if not include_raw:
            continue
        if np.array_equal(selected, present):
            # Identical physical and unique populations share immutable sorted bins.
            prefix = f"{metric}|unique_source|{family}|"
            for key, hist in tuple(store.items()):
                if key.startswith(prefix):
                    raw_key = key.replace("|unique_source|", "|raw_source|", 1)
                    _hist_merge(store, raw_key, hist[0], hist[1])
        else:
            _hist_batch(store, metric, "raw_source", family, "-", frame["right_code"],
                        frame["dte_code"], values, present, category_codes=codes)

''' +s[b:]
s=s.replace('_source_frame_hists(day_hists, owned["union"], "union")','_source_frame_hists(day_hists, owned["union"], "union", include_raw=False)')
# Arrow owns the output columns. Scalar fields have one declared type and nullable
# integers are masked before any conversion, including nanosecond clocks.
a=s.index('def _build_board_columns(');b=s.index('\ndef _family_file_status',a)
s=s[:a]+'''def _board_table(columns, n):
    pa = _pa()
    arrays = []
    for field in cut_board_schema():
        value = columns.get(field.name)
        if value is None or isinstance(value, (str, bool, int, float)):
            arrays.append(pa.repeat(pa.scalar(value, type=field.type), n))
        elif isinstance(value, (pa.Array, pa.ChunkedArray)):
            arrays.append(value.cast(field.type))
        else:
            arrays.append(pa.array(value, type=field.type))
    return pa.Table.from_arrays(arrays, schema=cut_board_schema())


def _concat_boards(boards):
    if isinstance(boards, _pa().Table):
        return boards
    if not boards:
        return cut_board_schema().empty_table()
    if isinstance(boards[0], dict):
        return _table(cut_board_schema(), boards)
    return _pa().concat_tables(boards)


class _BoardColumns:
    """A bounded view; null integer clocks never pass through floating point."""
    def __init__(self, boards):
        self.table = _concat_boards(boards)
        self.cache = {}

    def __len__(self):
        return len(self.table)

    def values(self, name):
        if name not in self.cache:
            col = self.table[name]
            pa = _pa()
            if pa.types.is_boolean(col.type):
                col = _pc().fill_null(col, False)
            elif pa.types.is_integer(col.type) or pa.types.is_floating(col.type):
                col = _pc().fill_null(col, 0)
            self.cache[name] = col.to_numpy(zero_copy_only=False)
        return self.cache[name]

    def present(self, name):
        return self.table[name].is_valid().to_numpy(zero_copy_only=False)

    def count(self, mask):
        return int(_np().count_nonzero(mask))

    def sum(self, name, mask):
        values = self.values(name)[mask & self.present(name)]
        if values.dtype.kind in 'iu' and values.size:
            # Counts are usually int32-bounded. Preserve Python-integer totals
            # if a future input could exceed a signed int64 sum.
            if int(values.max()) * len(values) > (1 << 63) - 1:
                return sum(int(value) for value in values)
        return values.sum().item()


def _build_board_columns(chain, declared, cut_label, cut_ns, family, frame, chosen, osi_book,
                         dates, oi_state, listed_mask, listing_known, cut_status):
    np, pa = _np(), _pa()
    n = len(chosen)
    f = {name: value[chosen] for name, value in frame.items() if isinstance(value, np.ndarray)}
    raw, conflict = f['raw_base'], f['unique_conflict']
    board = np.where((raw > BASE_INVALID_NUMERIC) & conflict, BASE_CONFLICT, raw)
    hide_price = conflict | (raw <= BASE_INVALID_NUMERIC) | f['nonfinite_price'] | f['negative_price']
    bid, ask = f['bid'], f['ask']
    bid_null, ask_null = f['bid_null'] | hide_price, f['ask_null'] | hide_price
    usable = f['usable_raw'] & ~conflict
    finite = ~bid_null & ~ask_null & np.isfinite(bid) & np.isfinite(ask) & usable
    mid, spread, rel = np.full(n, np.nan), np.full(n, np.nan), np.full(n, np.nan)
    mid[finite] = (bid[finite] + ask[finite]) / 2.0
    spread[finite] = ask[finite] - bid[finite]
    positive = finite & (mid > 0)
    rel[positive] = spread[positive] / mid[positive]
    def nullable(value, mask):
        return pa.array(value, mask=mask)
    cols = {
        'chain':chain, 'request_date':[dates.iso(int(d)) if d >= 0 else declared for d in f['req_days']],
        'acquisition_date':declared, 'cut_label':cut_label, 'cut_ns':cut_ns, 'source_family':family,
        'contract_id':f['contract_id'], 'identity_resolved':f['identity_valid'],
        'osi_symbol':[osi_book.get(int(code)) for code in f['osi_code']],
        'expiration':[dates.iso(int(d)) if d >= 0 else None for d in f['exp_days']],
        'millistrike':f['milli'], 'right':[RIGHT_NAMES.get(int(code)) for code in f['right_code']],
        'dte':nullable(f['dte'], f['dte'] == -999),
        'dte_bucket':[DTE_NAMES[int(code)] if 0 <= code < len(DTE_NAMES) else None for code in f['dte_code']],
        'bid':nullable(bid,bid_null), 'ask':nullable(ask,ask_null),
        'diagnostic_bid':nullable(bid,f['bid_null'] | ~np.isfinite(bid)),
        'diagnostic_ask':nullable(ask,f['ask_null'] | ~np.isfinite(ask)),
        'mid':nullable(mid,~np.isfinite(mid)), 'spread':nullable(spread,~np.isfinite(spread)),
        'relative_spread':nullable(rel,~np.isfinite(rel)),
        'base_class':[BASE_NAMES[int(value)] for value in board],
        'raw_base_class':[BASE_NAMES[int(value)] for value in raw],
        'usable':usable, 'conflict':conflict, 'ts_event_ns':f['ts_event_ns'],
        'sample_age_ns':cut_ns-f['ts_event_ns'],
        'unchanged_payload_age_ns':cut_ns-f['run_start_ts'],
        'run_continuity_observed':f['run_continuity'], 'run_lower_bound_ns':f['run_start_ts'],
        'file_id':f['file_id'], 'row_index':f['row_index'],
        'run_start_file_id':f['run_start_file_id'], 'run_start_row_index':f['run_start_row_index'],
        'alias_file_id':nullable(f['alias_file_id'],f['alias_file_id'] < 0),
        'alias_row_index':nullable(f['alias_row_index'],f['alias_row_index'] < 0),
        'alias_multiplicity':f['multiplicity'], 'listed':listed_mask,
        'listing_known':listing_known, 'quoted':True,
        'oi':nullable(oi_state['oi'],~oi_state['available'] | (oi_state['oi'] < 0)),
        'actual_update_age_unknown':True, 'causal_feature_eligible':False, 'cut_status':cut_status,
    }
    for output, name, null in (
        ('bid_size','bid_size','bid_size_null'),('ask_size','ask_size','ask_size_null'),
        ('bid_exchange','bid_exchange','bid_ex_null'),('ask_exchange','ask_exchange','ask_ex_null'),
        ('bid_condition','bid_condition','bid_cond_null'),('ask_condition','ask_condition','ask_cond_null'),
    ):
        cols[output] = nullable(f[name],f[null])
    for name in ('bid_null','ask_null','bid_size_null','ask_size_null','bid_ex_null','ask_ex_null',
                 'bid_cond_null','ask_cond_null','condition_zero','nonpositive_size','negative_size',
                 'zero_bid','zero_ask','negative_price','nonfinite_price','session_outside','request_date_mismatch'):
        cols[name] = f[name]
    for name in ('available','ambiguous','missing','stale','expired','zero'):
        cols['oi_'+name] = oi_state[name]
    for seconds in (60,300,900):
        cols['sample_stale_'+str(seconds)] = cols['sample_age_ns'] > seconds*NS
        cols['payload_stale_'+str(seconds)] = cols['unchanged_payload_age_ns'] > seconds*NS
    return _board_table(cols,n)


def _listed_unquoted_rows(chain, declared, cut_label, cut_ns, family, unquoted, listing, oi_join,
                          oi_state, cut_status, dates):
    np, pa = _np(), _pa()
    n = len(unquoted)
    identities = [oi_join.identity_fields(int(cid)) for cid in unquoted]
    expiration = [row.get('expiration') for row in identities]
    dte = [dte_days(exp, declared) if exp and declared else None for exp in expiration]
    cols = {
        'chain':chain, 'request_date':declared, 'acquisition_date':declared,
        'cut_label':cut_label, 'cut_ns':cut_ns, 'source_family':family,
        'contract_id':unquoted, 'identity_resolved':True,
        'osi_symbol':[row.get('osi_symbol') for row in identities], 'expiration':expiration,
        'millistrike':[row.get('millistrike') for row in identities],
        'right':[row.get('right') for row in identities], 'dte':dte,
        'dte_bucket':[quote_dte_bucket(value) for value in dte],
        'listed':True, 'listing_known':True, 'quoted':False,
        'oi':pa.array(oi_state['oi'],mask=~oi_state['available'] | (oi_state['oi'] < 0)),
        'actual_update_age_unknown':True, 'causal_feature_eligible':False, 'cut_status':cut_status,
    }
    for name in ('bid_null','ask_null','bid_size_null','ask_size_null','bid_ex_null','ask_ex_null',
                 'bid_cond_null','ask_cond_null'):
        cols[name] = True
    for name in ('usable','conflict','condition_zero','nonpositive_size','negative_size','zero_bid',
                 'zero_ask','negative_price','nonfinite_price','session_outside','request_date_mismatch'):
        cols[name] = False
    for name in ('available','ambiguous','missing','stale','expired','zero'):
        cols['oi_'+name] = oi_state[name]
    return _board_table(cols,n)


def _oi_only_rows(chain, declared, cut_label, cut_ns, family, cids, oi_join, oi_state,
                  cut_status, dates, listing):
    table = _listed_unquoted_rows(chain,declared,cut_label,cut_ns,family,cids,
        {'listing_known':True},oi_join,oi_state,cut_status,dates)
    for name,value in (('listed',False if listing['listing_known'] else None),
                       ('listing_known',listing['listing_known'])):
        table = table.set_column(table.schema.get_field_index(name),name,
            _pa().repeat(_pa().scalar(value,type=_pa().bool_()),len(table)))
    return table

''' +s[b:]
# Direct board composition is kept in Arrow through the writer and reductions.
s=s.replace('board = []\n                    quoted_ids','board = []\n                    quoted_ids')
s=s.replace('board.extend(_build_board_columns(', 'board.append(_build_board_columns(')
s=s.replace('board.extend(_listed_unquoted_rows(', 'board.append(_listed_unquoted_rows(')
s=s.replace('board.extend(_oi_only_rows(', 'board.append(_oi_only_rows(')
s=s.replace('''                    if board:
                        board_w.write_table(_table(cut_board_schema(), board))
                    day_boards.extend(board)
                    boards_by_family[family].extend(board)''','''                    board = _concat_boards(board)
                    if len(board):
                        board_w.write_table(board)
                    day_boards.append(board)
                    boards_by_family[family].append(board)''')
s=s.replace('''            if "near" in boards_by_family or "broad" in boards_by_family:
                paired = _paired_stats(boards_by_family.get("near") or [],
                                       boards_by_family.get("broad") or [])''','''            day_boards = _concat_boards(day_boards)
            boards_by_family = {name:_concat_boards(tables) for name,tables in boards_by_family.items()}
            if "near" in boards_by_family or "broad" in boards_by_family:
                near = boards_by_family.get('near', cut_board_schema().empty_table())
                broad = boards_by_family.get('broad', cut_board_schema().empty_table())
                paired = _paired_stats(near, broad)''')
s=s.replace('''                        [row for row in (boards_by_family.get("near") or []) if row["cut_label"] == cut_label],
                        [row for row in (boards_by_family.get("broad") or []) if row["cut_label"] == cut_label],''','''                        near.filter(_pc().equal(near['cut_label'],cut_label)),
                        broad.filter(_pc().equal(broad['cut_label'],cut_label)),''')
# Pairing uses only the required quoted payload columns, never the listing-only board.
needle='''    near = {(row["contract_id"], row["cut_label"], row["ts_event_ns"]): row for row in near_rows'''
replacement='''    names = ('contract_id','cut_label','ts_event_ns','quoted','conflict','bid','ask',
        'bid_size','ask_size','bid_exchange','ask_exchange','bid_condition','ask_condition',
        'bid_null','ask_null','bid_size_null','ask_size_null','bid_ex_null','ask_ex_null',
        'bid_cond_null','ask_cond_null')
    if isinstance(near_rows, _pa().Table):
        near_rows = near_rows.filter(near_rows['quoted']).select(names).to_pylist()
    if isinstance(broad_rows, _pa().Table):
        broad_rows = broad_rows.filter(broad_rows['quoted']).select(names).to_pylist()
    near = {(row["contract_id"], row["cut_label"], row["ts_event_ns"]): row for row in near_rows'''
assert needle in s;s=s.replace(needle,replacement)
p.write_text(s)
