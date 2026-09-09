from pathlib import Path
p=Path('/workspace/trading-research/tests/test_options_quote_measurements.py');s=p.read_text();pos=s.index('\n\nif __name__ == "__main__":')
addition='''

class QuoteWorkReuseLiteralTests(unittest.TestCase):
    def test_eastern_day_codes_preserve_dst_midnight_and_integer_ns(self):
        import numpy as np
        from trading_research.research.options_oi_columnar import ClockMaps,DateCodebook
        from trading_research.research.options_quote_measurements import _eastern_day_codes
        stamps = [datetime_ns(datetime(2020,3,8,4,59,59,tzinfo=timezone.utc)),
                  datetime_ns(datetime(2020,3,8,5,0,tzinfo=timezone.utc)),
                  datetime_ns(datetime(2020,11,1,5,30,tzinfo=timezone.utc)),
                  datetime_ns(datetime(2020,11,1,6,30,tzinfo=timezone.utc))]
        values = np.array([stamps[3]+1,stamps[0],stamps[2],stamps[1],stamps[0]],dtype=np.int64)
        got = _eastern_day_codes(values,DateCodebook(),ClockMaps())
        epoch = date(1970,1,1)
        expected = [(date.fromisoformat(day)-epoch).days for day in
                    ['2020-11-01','2020-03-07','2020-11-01','2020-03-08','2020-03-07']]
        self.assertEqual(got.tolist(),expected)

    def test_sorted_and_unsorted_cut_selection_keep_literal_ties_and_boundaries(self):
        import numpy as np
        from trading_research.research.options_quote_measurements import _empty_frame,select_cut_rows
        f=_empty_frame(7)
        for v in f.values():
            if hasattr(v,'fill'):v.fill(0)
        f['sort_id'][:]=[-2,-2,1,1,1,1,2]
        f['ts_event_ns'][:]=[10,20,15,20,20,20,21]
        f['file_id'][:]=[1,1,1,1,2,2,1]
        f['row_index'][:]=[0,1,2,3,4,4,6]
        f['ts_ok'].fill(True);f['req_ok'].fill(True)
        args=dict(cut_ns=20,cut_days=0,session_open_ns=10,session_close_ns=30)
        self.assertEqual(select_cut_rows(f,**args).tolist(),[1,4])
        permutation=np.array([6,3,1,4,5,0,2])
        shuffled={k:v[permutation] if isinstance(v,np.ndarray) else v for k,v in f.items()}
        self.assertEqual(permutation[select_cut_rows(shuffled,**args)].tolist(),[1,4])
        f['ts_event_ns'][4:6]=22
        self.assertEqual(select_cut_rows(f,**args).tolist(),[1,3])

    def test_single_sort_keeps_physical_aliases_and_unique_conflicts_separate(self):
        from trading_research.research.options_quote_measurements import _empty_frame,_source_frame_hists
        f=_empty_frame(5)
        for v in f.values():
            if hasattr(v,'fill'):v.fill(0)
        f['bid'][:]=[1,1,2,3,float('nan')];f['ask'][:]=[2,2,3,4,4]
        f['keep'][:]=[True,False,True,True,True]
        f['unique_conflict'][2]=True;f['usable_raw'].fill(True)
        h={};_source_frame_hists(h,f,'near')
        raw=h['bid|raw_source|near|-|CALL|expired'];unique=h['bid|unique_source|near|-|CALL|expired']
        self.assertEqual((raw[0].tolist(),raw[1].tolist()),([1.,2.,3.],[2,1,1]))
        self.assertEqual((unique[0].tolist(),unique[1].tolist()),([1.,3.],[1,1]))

    def test_arrow_pairing_has_literal_null_conflict_and_last_duplicate_counts(self):
        from trading_research.research.options_quote_measurements import _board_table,_paired_stats
        clock=2**53+3
        def row(cid,stamp,bid,**extra):
            return dict(contract_id=cid,cut_label='literal',ts_event_ns=stamp,quoted=True,
                conflict=False,bid=bid,ask=2.,bid_null=False,ask_null=False,
                bid_size=10,ask_size=10,bid_exchange=1,ask_exchange=1,
                bid_condition=50,ask_condition=50,bid_size_null=False,ask_size_null=False,
                bid_ex_null=False,ask_ex_null=False,bid_cond_null=False,ask_cond_null=False,**extra)
        near=[row(1,clock,0.),row(1,clock,1.),row(2,clock,1.),row(3,clock,None),row(4,None,1.)]
        broad=[row(1,clock,1.),row(2,clock+1,1.),row(3,clock,None),row(5,clock,1.)]
        def table(rows):
            return _board_table({name:[r[name] for r in rows] for name in rows[0]},len(rows))
        expected={'common':2,'agree':2,'conflict':0,'near_only':1,'broad_only':2,'unmatched_sample_clocks':3}
        self.assertEqual(_paired_stats(table(near),table(broad)),expected)
        self.assertEqual(_paired_stats(near,broad),expected)
        broad[2]['conflict']=True
        expected.update(agree=1,conflict=1)
        self.assertEqual(_paired_stats(table(near),table(broad)),expected)

    def test_unquoted_identity_cache_tracks_day_and_late_extra_ids(self):
        import numpy as np
        from trading_research.research.options_quote_measurements import _unquoted_identity_columns
        class Adapter:
            _horizon={'listed_ids':np.array([1,2]),'cid':np.array([2])}
            calls=0
            def identity_fields(self,cid):
                self.calls+=1
                return dict(osi_symbol=str(cid),expiration='2020-01-17',millistrike=cid*1000,right='CALL')
        a=Adapter()
        x=_unquoted_identity_columns(a,'2020-01-02',np.array([2],dtype=np.int64))
        self.assertEqual(x['dte'].to_pylist(),[15]);self.assertEqual(a.calls,2)
        _unquoted_identity_columns(a,'2020-01-02',np.array([1,2],dtype=np.int64))
        self.assertEqual(a.calls,2)
        x=_unquoted_identity_columns(a,'2020-01-02',np.array([3],dtype=np.int64))
        self.assertEqual(x['millistrike'].to_pylist(),[3000])
        x=_unquoted_identity_columns(a,'2020-01-03',np.array([1],dtype=np.int64))
        self.assertEqual(x['dte'].to_pylist(),[14])
'''
s=s[:pos]+addition+s[pos:];p.write_text(s)
import ast;ast.parse(s)
