from pathlib import Path
import json,hashlib,shutil,ast,datetime
r=Path('/workspace/trading-research');c=Path('/workspace/coordination/trading-research-cursor');w=c/'worktrees/performance-quote-fusion21';b=c/'performance-fusion21-before';b.mkdir(exist_ok=True)
names=['src/trading_research/data/compact_native.py','src/trading_research/research/auction_flow_quotes.py','src/trading_research/research/auction_flow_native_bins.py','tests/test_auction_flow_quotes.py','tests/test_auction_flow_native_bins.py'];base=json.loads((c/'performance-quote-fusion21-baseline.json').read_text())
for name in names:
 p=r/name;assert hashlib.sha256(p.read_bytes()).hexdigest()==base[name],name
 q=b/name;q.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,q);shutil.copy2(w/name,p)
p=r/names[0];s=p.read_text()
s=s.replace("array.dtype.kind not in 'iu':\n        return None\n    if array.dtype == np.int64", "array.dtype != np.int64:\n        return None\n    if array.dtype == np.int64")
s=s.replace("if array.dtype == bool or array.dtype == np.uint8 or array.dtype.kind in 'iu':", "if array.dtype == bool or array.dtype == np.uint8:")
s=s.replace("inputs = tuple(_contiguous_i64(a) for a in (t, order, bid, ask, bid_size, ask_size, flags))", "if not isinstance(flags, np.ndarray) or flags.dtype not in (np.dtype('uint8'), np.dtype('int64')):\n        return False\n    inputs = tuple(_contiguous_i64(a) for a in (t, order, bid, ask, bid_size, ask_size)) + (_contiguous_i64(flags.astype(np.int64, copy=False)),)")
s=s.replace('    const int64_t origin_abs = origin < 0 ? -origin : origin;\n','')
s=s.replace('row_ticks > 1024 || origin_abs >= 9007199254740992LL)', 'row_ticks > 1024 || origin <= -9007199254740992LL || origin >= 9007199254740992LL)')
needle='    const int64_t twice_row = row_ticks * 2;'
pre='''    // Validate the complete population before writing any caller-owned output.
    if (has_previous != 0 && has_previous != 1) return 1;
    if (prev_valid < 0 || prev_valid > 1 || maximum_age < -1) return 1;
    if (has_previous && (prev_t > t[0] || prev_t < 0)) return 1;
    if (has_previous && prev_valid && (prev_bid <= 0 || prev_ask >= 9007199254740992LL
            || prev_bid > prev_ask || prev_qb <= 0 || prev_qa <= 0
            || prev_qb >= 4294967295LL || prev_qa >= 4294967295LL)) return 1;
    for (int64_t i = 0; i < n; ++i) {
        if (t[i] < window_start || t[i] >= window_end || order[i] < 0
                || (i && (t[i] < t[i-1] || order[i] <= order[i-1]))
                || flags[i] < 0 || flags[i] > 255 || valid[i] > 1 || snapshot[i] > 1
                || updates[i] > 1 || clears[i] > 1
                || (snapshot[i] != ((flags[i] & 32) != 0))) return 1;
        if (valid[i] && (!updates[i] || clears[i] || (flags[i] & 4)
                || bid[i] <= 0 || ask[i] >= 9007199254740992LL || bid[i] > ask[i]
                || bid_size[i] <= 0 || ask_size[i] <= 0
                || bid_size[i] >= 4294967295LL || ask_size[i] >= 4294967295LL)) return 1;
    }
'''
assert needle in s;s=s.replace(needle,pre+needle,1);p.write_text(s)
p=r/names[1];s=p.read_text();needle='        n = int(len(t))\n        exp_starts'
pre='''        # Widening unusual prepared dtypes can change NumPy overflow and
        # promotion semantics. Keep those admitted inputs on the reference path.
        if (any(a.dtype != np.int64 or not a.flags.c_contiguous or not a.flags.aligned
                for a in (t, order, bid, ask, qb, qa))
                or any(a.dtype != bool for a in (valid, snapshot, updates, clears))
                or flags.dtype not in (np.dtype('uint8'), np.dtype('int64'))
                or np.any(flags < 0)
                or previous is not None and any(not -2**63 <= int(previous[key]) < 2**63
                    for key in ('t', 'bid', 'ask', 'bid_size', 'ask_size', 'book_valid', 'economic_at'))):
            return False
'''
assert needle in s;s=s.replace(needle,pre+needle,1)
old='''        counts = np.bincount(prepared.pair_codes[start:stop], minlength=len(prepared.pair_keys))
        for index, count in enumerate(counts):
            if count:
                key = prepared.pair_keys[index]
                self.action_sides[key] = self.action_sides.get(key, 0) + int(count)
        source_key, raw_action, raw_side = prepared.lineage(stop - 1)
        self.previous = {name: int(v[-1]) for name, v in values.items()}
'''
# There are two such blocks; alter only the compiled method.
left,tail=s.split('    def _try_add_prepared_compiled',1)
assert old in tail;tail=tail.replace(old,'''        for key, count in action_counts:
            self.action_sides[key] = self.action_sides.get(key, 0) + count
        self.previous = terminal_values
''')
needle='''        if self.native_sink is not None:
            self.native_sink.apply_compiled_quote_channels('''
pre='''        counts = np.bincount(prepared.pair_codes[start:stop], minlength=len(prepared.pair_keys))
        action_counts = [(prepared.pair_keys[i], int(count)) for i, count in enumerate(counts) if count]
        source_key, raw_action, raw_side = prepared.lineage(stop - 1)
        terminal_values = {name: int(v[-1]) for name, v in values.items()}
'''
assert needle in tail;tail=tail.replace(needle,pre+needle,1);s=left+'    def _try_add_prepared_compiled'+tail;p.write_text(s)
p=r/names[3];s=p.read_text();needle='    def test_explicit_noncompiled_fallback_and_empty_slice_behavior_stay_unchanged(self):'
extra='''    def test_prepared_integer_dtype_variants_keep_reference_arithmetic(self):
        import numpy as np
        from trading_research.data import compact_native
        table = make_quote_table(self.BRANCH_ROWS)
        for dtype in (np.int32, np.uint64):
            records = []
            before = compact_native.execution_counts()['compiled_quote_slice_calls']
            for enabled in (False, None):
                previous = _quote_backend(enabled)
                try:
                    window = QuoteWindow(instrument_id=1, start_ns=0, end_ns=100, latency_ns=250)
                    with prepare_quote_batch(table) as prepared:
                        prepared.values['bid_size'] = prepared.values['bid_size'].astype(dtype)
                        window.add_prepared(prepared)
                    records.append(window.finish(coverage_complete=True))
                finally:
                    _restore_quote_backend(previous)
            self.assertEqual(records[0], records[1])
            self.assertEqual(compact_native.execution_counts()['compiled_quote_slice_calls'], before)

'''
assert needle in s;s=s.replace(needle,extra+needle);p.write_text(s)
p=r/'tools/run_auction_flow_study.py';s=p.read_text();needle="        if compiled_projection['fused_rows'] == 0:"
s=s.replace(needle,"        if benchmark and (compiled_projection['compiled_quote_slice_calls'] == 0 or compiled_projection['compiled_native_quote_calls'] == 0):\n            raise ValueError('compiled quote and native fusion must execute on the registered population')\n"+needle);p.write_text(s)
record={'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'status':'integrated_unverified','files':{},'corrections':['Reference fallback for unusual numeric/mask dtypes before scratch allocation','Complete C++ input validation before writes, safe signed origin bound','Categorical and terminal lineage checks before compiled state commit']}
for name in names:
 ast.parse((r/name).read_text());record['files'][name]={'worker_sha256':hashlib.sha256((w/name).read_bytes()).hexdigest(),'integrated_sha256':hashlib.sha256((r/name).read_bytes()).hexdigest()}
(c/'performance-quote-fusion21-integration.json').write_text(json.dumps(record,indent=2)+'\n')
print('Integrated reviewed C++ quote/native fusion, corrections and dtype regression; AST valid.')
