"""Frozen auction vectors exercised through actual causal source producers."""

import json
import unittest
from dataclasses import replace
from decimal import Decimal
from fractions import Fraction as F
from pathlib import Path

from trading_research.errors import ContractError, DependencyUnavailable, IntegrityError
from trading_research.measurements.profiles import (
    FrozenGrid, ProfileDefinition, build_profile, validate_profile, profile_geometry,
    transform_profile, multiscale_profile_topology, profile_transport, profile_change,
    side_geometry, bar_proxy_profile, source_pin066_poc, fit_developing_profile, apply_developing_profile,
)
from trading_research.measurements.vwap import (
    measure_vwap, validate_vwap, vwap_bands, vwap_difference, VWAPBook,
    moving_anchor_residual, residual_band_statistics, source_volume_ema, source_new_high_anchors,
)
from trading_research.measurements.tpo import (
    select_brackets, measure_tpo, tpo_tails, estimate_dwell, naked_reference, validate_tpo,
)
from trading_research.measurements.footprint import measure_footprint, footprint_available, validate_footprint
from trading_research.measurements.cvd import CohortDefinition, CohortChannel, measure_cvd, measure_cohort_cvd
from trading_research.measurements.oi_report_proxy import OIReportChanges
from trading_research.research.label_ledger import OIReport
from trading_research.operations.artifacts import canonical_json
from tests.measurement_sources import Sources
from tests.measurement_fixtures import row, ledger, capture
from tests.measurement_fit_sources import fitted_sources
from references import auction_measurements_literal as literal


GOLD = {c['case_id']: c for c in json.loads((Path(__file__).parent/'golden/m0407m13_auction_measurements_v1.json').read_text())['cases']}


class AuctionMeasurements(unittest.TestCase):
    def setUp(self):
        self.s = Sources(self)

    def mass(self, values, *, origin=100, definition=None, bar=False):
        trades = [(origin+i, int(v), 1) for i, v in enumerate(values) if v]
        return self.s.profile(trades, grid=FrozenGrid(origin, 1, 0, len(values)-1, 'fixed', -100),
                              definition=definition, bar=bar)[0]

    def sides(self, buy, sell, unknown=None, *, bar=False, **kwargs):
        unknown = unknown or [0]*len(buy)
        trades = [(100+i, q, side) for side, values in ((1,buy),(-1,sell),(None,unknown))
                  for i,q in enumerate(values) if q]
        return self.s.profile(trades, grid=FrozenGrid(100,1,0,len(buy)-1,'fixed',-100), bar=bar, **kwargs)[0]

    def vwap(self, trades, *, start=0, end=10, published=None, name=None, view=None, bar=False,
             source_identity=None):
        result = self.s.profile([(p,q,1) for p,q in trades], start=start, end=end, published=published,
                                name=name, view=view, bar=bar, source_identity=source_identity)
        p,v,c,a,g,e = result
        return measure_vwap((c,), views=(v,), anchors=(a,), graphs=(g,), definition='vwap.v1'), result

    def tpo(self, events, *, end, width, cut=None, spans=None, representation='whole_trade_visits', minimum=5, grid=None):
        cut = end if cut is None else cut
        rows = [row(str(i),at=t,price=p,instrument=self.s.instrument.raw_symbol) for i,(t,p) in enumerate(events)]
        view,c,_ = self.s.capture(rows,end=end,cut=cut,spans=spans)
        a,g = self.s.anchor(c)
        _,ig,_ = self.s.clock(0,end,cut=cut)
        bs = select_brackets(ig,'session',bracket_ns=width,cut=cut)
        grid = grid or FrozenGrid(100,1,0,10,'fixed',-100)
        out = measure_tpo((c,),views=(view,),anchors=(a,),graphs=(g,),grid=grid,brackets=bs,
                          definition='tpo.v1',minimum_brackets=minimum,representation=representation)
        return out, (view,c,a,g,ig)

    def test_MP01_mass_unknown_unpriced_and_flat(self):
        p,*_ = self.s.profile([(100,7,1),(100,3,-1),(101,4,None),(None,2,1)],
                             grid=FrozenGrid(100,1,0,1,'fixed',-100))
        self.assertEqual(tuple((r.row,r.buy,r.sell,r.unknown) for r in p.rows), ((0,7,3,0),(1,0,0,4)))
        self.assertEqual((sum(r.mass for r in p.rows),sum(p.unpriced),p.total_mass),(14,2,16))
        self.assertEqual(literal.mass_profile(GOLD['MP01']['inputs']['trades'],100,1,0,1)[0],
                         tuple((r.row,r.buy,r.sell,r.unknown) for r in p.rows))
        flat,*_ = self.s.profile([(100,16,1)])
        self.assertEqual(flat.rows[0].mass,16)

    def test_MP02_MP11_MW07_exact_geography_and_bar_proxies(self):
        p,*_ = self.s.profile([(100,3,1),(105,9,1)],bar=True,grid=FrozenGrid(100,1,0,5,'fixed',-100))
        self.assertEqual(tuple(r.mass for r in p.rows),(3,0,0,0,0,9))
        self.assertEqual(tuple(r.mass for r in bar_proxy_profile(p,variant='equal_inclusive_rows').rows),(2,)*6)
        self.assertEqual(tuple(r.mass for r in bar_proxy_profile(p,variant='continuous_overlap').rows),(F(12,5),)*5+(0,))
        profiles = [self.s.profile([(p,q,1) for p,q in path],bar=True,grid=FrozenGrid(100,1,0,2,'fixed',-100))
                    for path in GOLD['MP11']['inputs']['paths']]
        self.assertEqual([profile_geometry(x[0])['poc_set'] for x in profiles],[(1,),(0,2)])
        self.assertEqual([literal.moments(path)[3] for path in GOLD['MP11']['inputs']['paths']],[101,101])
        for x in profiles:
            bar,_ = x[-1].window_publication(x[2].window.source_bar_version)
            self.assertEqual((bar.summary.open_ticks,bar.summary.high_ticks,bar.summary.low_ticks,bar.summary.close_ticks,bar.summary.volume),
                             (100,102,100,102,10))
        v,parts = self.vwap([(100,2),(102,3)],bar=True)
        proxy = bar_proxy_profile(parts[0],variant='hlc3')
        self.assertEqual(v.mean,F(506,5))
        self.assertEqual(F(304,3)-v.mean,F(2,15))
        self.assertNotEqual(proxy.representation,parts[0].representation)

    def test_MP03_MP04_MP14_value_area_modes_and_source_diagnostic(self):
        for values in ([5,0,5],[5,5,1],[9,1,0]):
            p=self.mass(values); g=profile_geometry(p)
            modes,poc,area,mass=literal.value_area(values,F(7,10))
            self.assertEqual((g['poc_set'],g['scalar_poc'],g['value_rows'],g['achieved_mass']),(modes,poc,area,mass))
        g=profile_geometry(self.mass([5,0,5]))
        self.assertEqual((g['mean_row'],g['requested_mass'],g['overshoot']),(1,7,3))
        stop=self.mass([5,0,5],definition=ProfileDefinition('atlas',gap_policy='stop_empty'))
        self.assertEqual(profile_geometry(stop)['value_rows'],(0,))
        plateau=profile_geometry(self.mass([5,5,1]))
        self.assertEqual(plateau['maximum_plateaus'],((0,1),))
        self.assertEqual(plateau['local_peaks'][0]['center'],F(1,2))
        p=self.mass([9,1,0],bar=True)
        self.assertIsNone(source_pin066_poc(bar_proxy_profile(p,variant='pin066_source')))

    def test_MP05_MP08_multiscale_mass_topology(self):
        p=self.mass([0,5,4,5,0]); sm=transform_profile(p,kind='triangular',scale=1)
        self.assertEqual(tuple(r.mass for r in sm.rows),tuple(map(F,GOLD['MP05']['expected']['smoothed'])))
        self.assertEqual(tuple(r.mass for r in sm.rows),literal.smooth([0,5,4,5,0]))
        self.assertEqual([x['rows'] for x in profile_geometry(p)['local_peaks']],[(1,1),(3,3)])
        self.assertEqual([x['rows'] for x in profile_geometry(sm)['local_peaks']],[(2,2)])
        self.assertEqual((p.total_mass,sm.total_mass),(14,14))
        self.assertEqual(len(multiscale_profile_topology(p,scales=(0,1))['representations']),2)
        self.assertEqual(multiscale_profile_topology(p,scales=(0,1))['matches'],())
        coarse=transform_profile(self.mass([1,2,3,4]),kind='coarsen',scale=2)
        self.assertEqual(tuple(r.mass for r in coarse.rows),(3,7))

    def test_MP06_MP07_fixed_grid_phase_and_overflow(self):
        trades=[(100,2,1),(101,3,1),(102,5,1)]
        profiles=[self.s.profile(trades,grid=FrozenGrid(o,2,-1,1,'fixed:'+str(o),-100))[0] for o in (100,101)]
        self.assertEqual([tuple((r.row,r.mass) for r in p.rows if r.mass) for p in profiles],[((0,5),(1,5)),((-1,2),(0,8))])
        self.assertEqual([p.total_mass for p in profiles],[10,10]);self.assertNotEqual(profiles[0].grid.id,profiles[1].grid.id)
        p,*_=self.s.profile([(99,2,1),(100,3,1),(101,5,1),(102,7,1)],grid=FrozenGrid(100,1,0,1,'fixed',-100))
        self.assertEqual((sum(p.low_overflow),tuple(r.mass for r in p.rows),sum(p.high_overflow),p.total_mass),(2,(3,5),7,17))
        self.assertIsNone(profile_transport(p,p))

    def test_MP09_MP10_transport_and_normalization(self):
        for a,b in GOLD['MP09']['inputs']['pairs']:
            self.assertEqual(profile_transport(self.mass(a),self.mass(b)),literal.transport(a,b))
        p,q=self.mass([2,2]),self.mass([2,6]);d=profile_change(p,q)
        self.assertEqual(d['row_mass_change'],(0,4));self.assertEqual(d['normalization_component'],(F(-1,4),)*2)
        self.assertEqual(d['new_mass_component'],(0,F(1,2)));self.assertEqual(d['probability_change'],(F(-1,4),F(1,4)))

    def test_MP12_MP13_explicit_source_body_wick_and_loss(self):
        p,*_=self.s.profile([(101,25,1),(104,25,1),(100,25,1),(103,25,1)],bar=True,grid=FrozenGrid(100,1,0,3,'fixed',-100))
        proxy=bar_proxy_profile(p,variant='pin066_source')
        expected=literal.body_wicks((101,104,100,103),100,[(i,i+1) for i in range(100,104)])
        self.assertEqual(tuple((r.buy,r.sell) for r in proxy.rows),expected)
        self.assertEqual(tuple(r.buy for r in proxy.rows),(F(50,3),)*4)
        self.assertEqual(tuple(r.sell for r in proxy.rows),(F(50,3),0,0,F(50,3)))
        flat,*_=self.s.profile([(100,10,1)],bar=True)
        source=bar_proxy_profile(flat,variant='pin066_source');corrected=bar_proxy_profile(flat,variant='pin066_corrected')
        self.assertEqual((source.total_mass,dict(source.work)['source_flat_bar_lost_mass'],corrected.total_mass),(0,10,10))
        self.assertNotEqual(source.id,corrected.id)

    def test_MP15_MP16_composite_anchor_variants_and_causality(self):
        allrows=[row(k,at=i,price=100+i,size=i+1,instrument=self.s.instrument.raw_symbol) for i,k in enumerate('abc')]
        view=ledger(allrows)
        parts=[]
        for start,end in ((0,2),(1,3)):
            v,c,_=self.s.capture([],view=view,start=start,end=end,cut=3)
            a,g=self.s.anchor(c);parts.append((v,c,a,g))
        kwargs=dict(views=tuple(p[0] for p in parts),anchors=tuple(p[2] for p in parts),graphs=tuple(p[3] for p in parts),
                    grid=FrozenGrid(100,1,0,2,'fixed',-100))
        for kind in GOLD['MP15']['inputs']['anchor_kinds']:
            p=build_profile(tuple(p[1] for p in parts),definition=ProfileDefinition(kind,anchor_kind=kind),**kwargs)
            self.assertEqual(tuple(t.id for t in p.members),tuple('abc'));self.assertEqual(p.total_mass,6)
        with self.assertRaises(ContractError):
            build_profile(tuple(p[1] for p in parts),definition=ProfileDefinition('viewport',viewport_known_at=11),**kwargs)
        self.assertEqual(profile_geometry(p),profile_geometry(p))

    def test_DP01_DP02_DP03_DP04_DP06_DP07_side_geometry(self):
        p=self.sides([100],[100]);g=side_geometry(p)
        self.assertEqual((g['rows'][0]['delta'],p.total_mass,g['overlap'],g['wasserstein_ticks']),(0,200,1,0))
        g=side_geometry(self.sides([3],[0],[5]),pseudo_mass=F(1))['rows'][0]
        self.assertEqual((g['observed_bounds'],g['certain_sign'],g['contrast']),((-2,8),None,F(3,10)))
        g=side_geometry(self.sides([1,100],[0,0]),pseudo_mass=F(1))
        self.assertEqual(tuple(r['contrast'] for r in g['rows']),(F(1,3),F(50,51)))
        self.assertTrue(all(r['zero_denominator'] and r['ratio'] is None for r in g['rows']))
        g=side_geometry(self.sides([10,0],[0,10]));self.assertEqual((g['cdf_buy'],g['cdf_sell'],g['overlap'],g['total_variation'],g['wasserstein_ticks']),((1,1),(0,1),0,1,1))
        self.assertEqual(tuple(r['cumulative_signed'] for r in g['rows']),(10,0))
        g=side_geometry(self.sides([1,4],[11,1]));self.assertEqual((g['minimum_rows'],g['maximum_rows'],g['absolute_peak_rows'],g['absolute_delta_mass']),((0,),(1,),(0,),13))
        a,b=self.sides([5,0],[0,5]),self.sides([0,5],[5,0])
        self.assertEqual(tuple(r.mass for r in a.rows),tuple(r.mass for r in b.rows))
        self.assertEqual((tuple(r.delta for r in a.rows),tuple(r.delta for r in b.rows)),((5,-5),(-5,5)))

    def test_MT01_MT06_MT08_exact_bracket_visits_and_chronology(self):
        events=[(0,100),(1,100),(2,102),(4,100)]
        out,_=self.tpo(events,end=6,width=3)
        self.assertEqual(tuple((r,len(ids)) for r,ids in out.rows),((0,2),(2,1)))
        expected=literal.tpo(events,[(0,3),(3,6)])
        self.assertEqual(tuple((r+100,len(ids)) for r,ids in out.rows),tuple((r,len(ids)) for r,ids in expected))
        proxy,_=self.tpo([(0,100),(1,102)],end=3,width=3,representation='ohlc_range_proxy')
        exact,_=self.tpo([(0,100),(1,102)],end=3,width=3)
        self.assertEqual(tuple(r for r,_ in exact.rows),(0,2));self.assertEqual(tuple(r for r,_ in proxy.rows),(0,1,2))
        a,_=self.tpo([(0,100),(1,101),(2,100)],end=3,width=3)
        b,_=self.tpo([(0,100),(1,100),(2,101)],end=3,width=3)
        self.assertEqual(a.rows,b.rows);self.assertNotEqual(a.chronological_visits,b.chronological_visits)

    def test_MT02_MT04_MT05_MT09_completion_missing_and_short_session(self):
        early,_=self.tpo([(0,100)],end=5,width=1,cut=1,spans=((0,1),))
        final,_=self.tpo([(0,100),(1,101),(2,100)],end=5,width=1)
        self.assertFalse(early.final);self.assertIsNone(early.confirmed_single_rows)
        self.assertEqual(early.completed_brackets,1)
        self.assertEqual((final.completed_brackets,final.occupied_brackets),(5,3));self.assertNotIn(0,final.confirmed_single_rows)
        four,_=self.tpo([(0,100),(1,100),(2,100),(3,100),(3,101)],end=4,width=1)
        self.assertFalse(four.source_display_ready);self.assertEqual(tuple(len(ids) for _,ids in four.rows),(4,1))
        missing,_=self.tpo([(0,100),(2,100),(2,101)],end=3,width=1,spans=((0,1),(2,3)))
        self.assertFalse(missing.history_complete);self.assertIsNone(missing.confirmed_single_rows)
        self.assertEqual(tuple(status for *_,status in missing.brackets),('complete','missing','complete'))
        short,_=self.tpo([],end=90,width=30)
        self.assertEqual(tuple((a,b) for _,a,b,_ in short.brackets),((0,30),(30,60),(60,90)))
        self.assertEqual(short.completed_brackets,3)

    def test_MT03_distinct_tail_definitions(self):
        events=[(t,100+i) for i,letters in enumerate(GOLD['MT03']['inputs']['row_brackets']) for t in [ord(c)-ord('A') for c in letters]]
        out,_=self.tpo(events,end=3,width=1,grid=FrozenGrid(100,1,0,5,'fixed',-100))
        self.assertEqual(tpo_tails(out),{'low':(0,1),'high':(4,5),'low_same_letter':False,'high_same_letter':True})

    def test_MT07_estimated_dwell_is_separate_from_observation(self):
        _,parts=self.tpo([(0,100),(9,101)],end=10,width=10)
        view,c,*_=parts
        result=estimate_dwell(c,view=view,grid=FrozenGrid(100,1,0,1,'fixed',-100),stale_cap_ns=3)
        expected,missing=literal.dwell([(0,100),(9,101)],10,3)
        self.assertEqual(tuple((r+100,d) for r,d in result['duration_by_row']),expected)
        self.assertEqual((result['unassigned_duration'],result['true_per_row_lower'],result['true_per_row_upper']),(missing,0,10))

    def test_MW01_MW02_MW04_MW05_exact_moments_and_robust_bands(self):
        for case in ('MW01','MW02','MW04','MW05'):
            inputs=GOLD[case]['inputs'];trades=inputs.get('trades',list(zip(inputs.get('prices',[]),inputs.get('weights',[]))))
            v,_=self.vwap(trades)
            self.assertEqual((v.mass,v.sum_pv,v.sum_p2v,v.mean,v.variance),literal.moments(trades))
            bands=vwap_bands(v)
            self.assertEqual(tuple(q for _,q in bands['quantiles']),tuple(literal.weighted_rank(trades,p) for p in (F(1,4),F(1,2),F(3,4))))
            if case=='MW02':self.assertEqual(bands['sd'],Decimal('0.5'))
            if case=='MW04':self.assertEqual((v.mean,bands['median'],v.variance),(105,100,25))
            if case=='MW05':self.assertEqual((v.mean,bands['sd'],bands['quantiles'][0][1],bands['quantiles'][2][1]),(110,30,100,100))

    def test_MW03_MA03_empty_restore_future_suffix(self):
        first,parts=self.vwap([(100,5)],end=2)
        empty,other=self.vwap([],start=2,end=4)
        self.assertEqual((empty.mass,empty.mean,empty.variance,vwap_bands(empty)['sigma_bands']),(0,None,None,None))
        book=VWAPBook()
        for value in (first,empty):book.advance(**value._recipe)
        restored=VWAPBook.restore(book.checkpoint(),recipes=book.recipes)
        self.assertEqual(restored.checkpoint(),book.checkpoint())
        from trading_research.measurements.tape import Trade
        parts[1].add(Trade.restore(row('future',at=9,known=10,price=999,instrument=self.s.instrument.raw_symbol)))
        validate_vwap(first);self.assertEqual(first.mean,100)

    def test_MW06_MW09_cross_anchor_contributions(self):
        rows=[row(k,at=i,price=100+10*i,instrument=self.s.instrument.raw_symbol) for i,k in enumerate('abc')]
        view=ledger(rows);values=[]
        for start,end in ((0,2),(1,3)):
            v,c,_=self.s.capture([],view=view,start=start,end=end,cut=3)
            a,g=self.s.anchor(c)
            values.append(measure_vwap((c,),views=(v,),anchors=(a,),graphs=(g,),definition='vwap'))
        d=vwap_difference(*values)
        self.assertEqual((values[0].mean,values[1].mean,d['difference'],d['reconciliation_error']),(105,115,10,0))
        self.assertEqual(tuple((i,v) for i,v,_ in d['contributions']),(('a',-50),('b',0),('c',60)))
        a,_=self.vwap([(105,1)], source_identity='mw06-a')
        b,_=self.vwap([(200,1)], source_identity='mw06-b')
        self.assertEqual(vwap_difference(a,b)['difference'],95)
        with self.assertRaises(ContractError):vwap_difference(a,b,kind='same_anchor_slope')

    def test_MW10_MA04_actual_source_high_reanchors_and_ema(self):
        parts=[self.s.profile([(p,1,1)],start=i,end=i+1,bar=True,source_identity=f'mw10-high-{i}')
               for i,p in enumerate([100,103,101,104])]
        _,ig,_=self.s.clock(0,4)
        out=source_new_high_anchors(tuple(p[2] for p in parts),views=tuple(p[1] for p in parts),anchors=tuple(p[3] for p in parts),
            graphs=tuple(p[4] for p in parts),interval_graph=ig,interval_name='session')
        self.assertEqual(tuple(r[0] for r in out),(0,1,1,3));self.assertEqual(tuple(r[1] for r in out),(100,103,102,104))
        parts=[self.s.profile([(100,q,1)],start=i,end=i+1,bar=True,source_identity=f'mw10-ema-{i}')
               for i,q in enumerate([3,6,9])]
        ema=source_volume_ema(tuple(p[2] for p in parts),views=tuple(p[1] for p in parts))
        self.assertEqual((ema['alpha'],ema['values'],ema['proxy_volume_total'],ema['actual_volume_total']),(F(1,3),(3,4,F(17,3)),F(38,3),18))

    def test_MW11_MW12_actual_historical_residuals(self):
        for residuals,weights,anchors in (([2,2],[1,1],[100,110]),([-2,1,3],[1,2,1],[100]*3)):
            observations=[]
            for i,(d,q,a) in enumerate(zip(residuals,weights,anchors)):
                anchor,_=self.vwap([(a,1)],start=i*10,end=i*10+1)
                _,source=self.vwap([(a+d,q)],start=i*10+2,end=i*10+3)
                observations.append(moving_anchor_residual(source[2],view=source[1],session_vwap=anchor,high_anchor_vwap=anchor))
            current,_=self.vwap([(110,1)],start=40,end=41)
            result=residual_band_statistics(tuple(observations),current_anchor=current)
            self.assertEqual(tuple(o.deviation for o in observations),tuple(residuals))
            if len(residuals)==2:
                self.assertEqual((result['rms'],result['centered_variance'],result['zero_centered_median_abs'],result['centered_mad'],result['weighted_offset_band']),(2,0,2,0,112))
            else:
                self.assertEqual((result['weighted_mean'],result['rms_squared'],result['positive_rms_squared'],result['negative_rms']),(F(3,4),F(15,4),F(11,3),2))
                self.assertEqual(result['source_quantiles'],literal.source_quantiles(residuals,(F(1,10),F(1,4),F(3,4),F(9,10))))
                single=residual_band_statistics((observations[0],),current_anchor=current)
                self.assertEqual(single['source_quantiles'],(None,)*4)

    def test_MF01_MF02_MF04_ratios_support_and_unknown_bounds(self):
        p=self.sides([0,56],[5,100],bar=True)
        diagonal=measure_footprint(p);same=measure_footprint(p,comparison='same_price')
        self.assertEqual(diagonal.rows[1]['buy']['observed_ratio'],F(56,5));self.assertTrue(diagonal.rows[1]['buy']['observed_qualifies'])
        self.assertEqual(same.rows[1]['buy']['observed_ratio'],F(14,25));self.assertFalse(same.rows[1]['buy']['observed_qualifies'])
        for b,s in GOLD['MF01']['inputs']['source_pairs']:
            value=measure_footprint(self.sides([b],[s],bar=True),comparison='same_price')
            self.assertFalse(value.rows[0]['buy']['observed_qualifies'])
        for policy,expected in (('require_opposition',(False,False)),('qualify_zero',(False,True))):
            value=measure_footprint(self.sides([1,10],[0,0],bar=True),comparison='same_price',minimum_numerator=5,zero_policy=policy)
            self.assertEqual(tuple(r['buy']['observed_qualifies'] for r in value.rows),expected)
            self.assertTrue(all(r['buy']['observed_ratio'] is None for r in value.rows))
        value=measure_footprint(self.sides([0,10],[1,0],[5,0],bar=True))
        r=value.rows[1]['buy'];self.assertEqual((r['observed_ratio'],r['minimum_compatible_ratio'],r['observed_qualifies'],r['certain_qualifies']),(10,F(5,3),True,False))
        partial=self.sides([10,10],[1,1],bar=True,spans=((0,4),(6,10)))
        pf=measure_footprint(partial,comparison='same_price')
        self.assertTrue(pf.rows[0]['buy']['observed_qualifies'])
        self.assertTrue(all(r['buy']['certain_qualifies'] is None and r['buy']['minimum_compatible_ratio'] is None for r in pf.rows))
        self.assertEqual(pf.buy_stacks,());self.assertTrue(all(r['certain_sign'] is None for r in side_geometry(partial)['rows']))
        from trading_research.measurements.measurement_ports import measurement_location
        unknown=self.sides([10,0],[0,1],[0,20],bar=True)
        for role in ('buy_delta_peak','sell_delta_peak','absolute_delta_peak'):
            with self.assertRaises(DependencyUnavailable):measurement_location(unknown,role=role)
        self.assertEqual(measurement_location(unknown,role='poc').geometry.lower,101)

    def test_MF03_MF08_stacks_and_fixed_haar(self):
        p=self.sides([10,10,0,10],[1,1,0,1],bar=True)
        a=measure_footprint(p,comparison='same_price',minimum_stack=2)
        b=measure_footprint(p,comparison='same_price',minimum_stack=3)
        self.assertEqual((a.buy_stacks,b.buy_stacks),(((0,1),),()))
        p=self.sides([1,3,2,2],[0]*4,bar=True);h=dict(measure_footprint(p).haar)['buy']
        self.assertEqual(h[0][:2],literal.haar([1,3,2,2]));self.assertEqual(h[1][:2],((2,),(0,)))
        self.assertEqual(p.total_mass,8)

    def test_MF05_MF06_temporal_signs_and_price_location(self):
        extrema=[]
        for signs in ([1,-1],[-1,1]):
            p,v,c,*_=self.s.profile([(100,10,s) for s in signs],bar=True)
            f=measure_footprint(p)
            cv=measure_cohort_cvd(c,view=v,definition=CohortDefinition('all',c.window.aggregation_unit,
                (CohortChannel('all',1,None),))).paths[0]
            self.assertEqual((f.total_delta,sum(r.buy for r in p.rows),sum(r.sell for r in p.rows)),(0,10,10))
            extrema.append((cv.high_bounds[0],cv.low_bounds[0]))
        self.assertEqual(extrema,[(10,0),(0,-10)])
        p,*_=self.s.profile([(100,1,1),(100,11,-1),(102,3,1)],bar=True)
        f=measure_footprint(p);g=dict(f.geometry)
        self.assertEqual((g['open'],g['close'],p.rows[0].delta,f.total_delta),(100,102,-10,-7))
        self.assertEqual(dict(f.signed_peaks)['negative'],(0,))

    def test_MF07_MF09_MF10_actual_prefix_and_final_geometry(self):
        rows=[row(str(i),at=t,known=k,price=p,instrument=self.s.instrument.raw_symbol) for i,(t,k,p) in enumerate([(1,1,100),(2,2,103),(3,4,101)])]
        view=ledger(rows);parts=[]
        for cut,pub in ((3,3),(4,4)):
            v,c,_=self.s.capture([],view=view,end=4,cut=cut,published=pub,spans=((0,cut),),bar=True)
            a,g=self.s.anchor(c)
            parts.append(build_profile((c,),views=(v,),anchors=(a,),graphs=(g,),grid=FrozenGrid(100,1,0,3,'fixed',-100),definition=ProfileDefinition('foot')))
        early,final=map(measure_footprint,parts)
        self.assertEqual((dict(early.geometry)['close'],dict(early.geometry)['upper_wick'],dict(final.geometry)['close'],dict(final.geometry)['upper_wick']),(103,0,101,2))
        self.assertFalse(early.final);self.assertTrue(final.final)
        prefixes=[]
        for cut,pub in ((2,3),(4,5)):
            v,c,_=self.s.capture([],view=view,end=cut,cut=cut,published=pub,bar=True)
            a,g=self.s.anchor(c)
            p=build_profile((c,),views=(v,),anchors=(a,),graphs=(g,),grid=FrozenGrid(100,1,0,3,'fixed',-100),definition=ProfileDefinition('prefix'))
            prefixes.append(measure_footprint(p))
        self.assertEqual([[footprint_available(p,c) for c in (2,3,4,5)] for p in prefixes],[[False,True,True,True],[False,False,False,True]])
        self.assertFalse(footprint_available(early,4,final_only=True))

    def test_MA06_actual_oi_receipt_change_once_and_restore(self):
        prior=OIReport('prior','NQ.test','2027-01-01',10,100)
        new=OIReport('OI.v1','NQ.test','2027-01-04',20,110)
        book=OIReportChanges(prior);book.append(new)
        self.assertEqual(book.observe(19)['state'],'unavailable')
        outputs=[book.observe(t) for t in (20,21,22)]
        self.assertEqual([len(o['events']) for o in outputs],[1,0,0])
        self.assertEqual([o['new_change'] for o in outputs],[10,0,0])
        self.assertTrue(all(o['transaction_volume'] is None for o in outputs))
        self.assertFalse(book.append(new))
        with self.assertRaises(IntegrityError):book.append(replace(new,count=111))
        restored=OIReportChanges.restore(book.checkpoint(),prior=prior,reports=(new,),queries=(19,20,21,22))
        self.assertEqual(restored.checkpoint(),book.checkpoint())

    def test_MA07_explicit_source_threshold_variants(self):
        profiles=[self.mass([68,1,31],definition=ProfileDefinition('va:'+str(v),value_fraction=F(v))) for v in ('2/5','17/25','7/10')]
        self.assertEqual(len({p.id for p in profiles}),3)
        self.assertEqual(profile_geometry(profiles[1])['value_rows'],(0,));self.assertEqual(profile_geometry(profiles[2])['value_rows'],(0,1,2))
        p=self.sides([4,4],[1,1],bar=True)
        variants=[measure_footprint(p,ratio=r,comparison='same_price',minimum_stack=k) for r in (3,4,F(7,2),F(9,2)) for k in (2,3)]
        self.assertEqual(len(variants),8)
        self.assertEqual([v.rows[0]['buy']['observed_qualifies'] for v in variants[::2]],[True,True,True,False])

    def test_MA02_public_producer_authentication(self):
        p,*_=self.s.profile([(100,5,1)],bar=True)
        changed=replace(p,rows=(replace(p.rows[0],buy=F(6)),*p.rows[1:]))
        object.__setattr__(changed,'_recipe',p._recipe)
        with self.assertRaises(IntegrityError):validate_profile(changed)
        for value,validator,field in ((measure_footprint(p),validate_footprint,'total_delta'),):
            forged=replace(value,**{field:F(999)});object.__setattr__(forged,'_recipe',value._recipe)
            with self.assertRaises(IntegrityError):validator(forged)
        v,_=self.vwap([(100,5)]);forged=replace(v,mean=F(999));object.__setattr__(forged,'_recipe',v._recipe)
        with self.assertRaises(IntegrityError):validate_vwap(forged)
        t,_=self.tpo([(0,100)],end=5,width=1);forged=replace(t,completed_brackets=999);object.__setattr__(forged,'_recipe',t._recipe)
        with self.assertRaises(IntegrityError):validate_tpo(forged)

    def test_MA01_grid_bracket_scale_band_capacity_before_allocation(self):
        self.assertEqual(FrozenGrid(0,1,0,4095,'max',-1).upper_row,4095)
        with self.assertRaises(ContractError):FrozenGrid(0,1,0,4096,'over',-1)
        _,graph,_=self.s.clock(0,1024)
        self.assertEqual(len(select_brackets(graph,'session',bracket_ns=1,cut=1024).brackets),1024)
        _,over,_=self.s.clock(0,1025,name='over')
        with self.assertRaises(ContractError):select_brackets(over,'over',bracket_ns=1,cut=1025)
        p=self.mass([1]);self.assertEqual(len(multiscale_profile_topology(p,scales=tuple(range(32)))['representations']),32)
        with self.assertRaises(ContractError):multiscale_profile_topology(p,scales=tuple(range(33)))
        v,_=self.vwap([(100,1)]);self.assertEqual(len(vwap_bands(v,multipliers=(F(1),)*32)['sigma_bands']),32)
        with self.assertRaises(ContractError):vwap_bands(v,multipliers=(F(1),)*33)
        touched=[]
        def stream():
            touched.append(True)
            yield F(1)
        with self.assertRaises(ContractError):vwap_bands(v,multipliers=stream())
        self.assertFalse(touched)
        value=p
        for _ in range(31):value=transform_profile(value,kind='triangular',scale=1)
        validate_profile(value);before=value.record()
        with self.assertRaisesRegex(ContractError,'acyclic capacity'):transform_profile(value,kind='triangular',scale=1)
        self.assertEqual(value.record(),before)
        t,_=self.tpo([(0,100)],end=5,width=1)
        cap=max(len(canonical_json(t.record())),len(canonical_json(tuple(v.record() for c in t._recipe['captures'] for v in c.trades))))
        self.assertEqual(measure_tpo(**{**t._recipe,'max_bytes':cap}).record(),t.record())
        with self.assertRaises(ContractError):measure_tpo(**{**t._recipe,'max_bytes':cap-1})

    def test_DP05_actual_soft_cohort_profiles_conserve_one_print(self):
        from trading_research.measurements.cvd import CohortChannel
        from tests.measurement_fixtures import UNIT
        definition=CohortDefinition('soft',UNIT,(),knots=(10,20))
        parts=self.s.profile([(100,15,1)])
        p,v,c,a,g,_=parts
        values=[build_profile((c,),views=(v,),anchors=(a,),graphs=(g,),grid=p.grid,definition=p.definition,
            cohort=definition,cohort_index=i) for i in (0,1)]
        self.assertEqual(tuple(x.rows[0].buy for x in values),(F(15,2),F(15,2)))
        self.assertEqual(sum(x.total_mass for x in values),15)
        self.assertEqual(len({t.id for x in values for t in x.members}),1)

    def test_MP17_MA03_actual_correction_prefix_and_fresh_restore(self):
        from trading_research.measurements.tape import Trade, TradeLedger
        initial=row('a',at=1,price=100,size=5,side=1,instrument=self.s.instrument.raw_symbol)
        view=ledger([initial])
        v,c,_=self.s.capture([],view=view,cut=10)
        a,g=self.s.anchor(c)
        grid=FrozenGrid(100,1,0,1,'fixed',-100)
        old=build_profile((c,),views=(v,),anchors=(a,),graphs=(g,),grid=grid,definition=ProfileDefinition('correction'))
        old_record=old.record()
        replacement=Trade.restore(row('b',at=1,known=20,price=101,size=5,side=-1,instrument=self.s.instrument.raw_symbol))
        view.correct(id='correct',original_id='a',known_at=20,reason='source revision',replacement=replacement)
        v2,c2,_=self.s.capture([],view=view,cut=20)
        a2,g2=self.s.anchor(c2)
        new=build_profile((c2,),views=(v2,),anchors=(a2,),graphs=(g2,),grid=grid,definition=old.definition)
        self.assertEqual((old.rows[0].buy,new.rows[1].sell),(5,5));self.assertEqual(old.record(),old_record)
        validate_profile(old)
        restored=TradeLedger.restore(view.checkpoint())
        for value in (old,new):
            recipe=dict(value._recipe[1],views=(restored,))
            self.assertEqual(build_profile(**recipe).record(),value.record())

    def test_MP18_MA05_actual_retained_developing_profile_fit(self):
        grid=FrozenGrid(100,1,0,1,'developing-grid',-100)
        a=self.s.profile([(100,2,1)],grid=grid,start=8,end=9,published=10)[0]
        b=self.s.profile([(101,2,1)],grid=grid,start=18,end=19,published=20)[0]
        query=self.s.profile([(100,4,1)],grid=grid,start=38,end=40,published=41)[0]
        contexts=((7,'same'),(17,'same'));qc=(37,'same')
        params=dict(train_end=30,available_at=31,minimum_context_rows=1)
        state=fit_developing_profile(((a,contexts[0]),(b,contexts[1])),**params)
        self.assertEqual(state.pooled_rates,(1,1));self.assertEqual(state.cells,(('same',(1,1),2),))
        incompatible=build_profile(**{**b._recipe[1],'definition':ProfileDefinition('different-definition')})
        with self.assertRaises(ContractError):fit_developing_profile(((a,contexts[0]),(incompatible,contexts[1])),**params)
        repeated=build_profile(**{**a._recipe[1],'published_at':11})
        with self.assertRaisesRegex(ContractError,'underlying exposure origin'):
            fit_developing_profile(((a,contexts[0]),(repeated,contexts[0])),**params)
        def fixture(path,**extra):
            return fitted_sources(self.s.root/path,family='developing_profile',parameters=params,recipe_id=state.recipe_id,
                state=state,training_features=({'profile':a.record(),'profile_context':contexts[0]},
                    {'profile':b.record(),'profile_context':contexts[1]}),
                query_features={'profile':query.record(),'profile_context':qc},**extra)
        f=fixture('fit')
        for key in ('profile','profile_context'):f['query_session'].read(key)
        result=apply_developing_profile(query,admission=f['admission'],training_profiles=(('train1',a,contexts[0]),('train2',b,contexts[1])),
            query_session=f['query_session'],context=qc)
        self.assertEqual((result['expected_mass'],result['expected_shape'],result['raw_residual'],result['shape_residual'],result['support_rows']),
            ((2,2),(F(1,2),F(1,2)),(2,-2),(F(1,2),F(-1,2)),2))
        from trading_research.operations.artifact_graph import SemanticArtifactStore,ReadSession,ReadBinding
        from trading_research.measurements.measurement_fits import admit_measurement_fit
        reopened=SemanticArtifactStore(self.s.root/'fit',f['store'].namespace)
        restored=admit_measurement_fit(reopened,f['commit'],f['transform'].id,f['request'],
            schema_id=f['request'].schema_id,unit=f['request'].unit,recipe_id=state.recipe_id)
        session=ReadSession(reopened,f['base'],tuple(ReadBinding(k,f['source'].id,k,replace(f['request'],purpose='input'))
            for k in ('profile','profile_context')))
        replay=apply_developing_profile(query,admission=restored,training_profiles=(('train1',a,contexts[0]),('train2',b,contexts[1])),
            query_session=session,context=qc)
        self.assertEqual(replay,result)
        with self.assertRaises((ContractError,IntegrityError,DependencyUnavailable)):
            fixture('future',completion=41)
        with self.assertRaises((ContractError,IntegrityError)):
            fixture('membership',training_ids=('train1','heldout'))
        bad=fixture('bad-payload',fit_payload=b'{}')
        for key in ('profile','profile_context'):bad['query_session'].read(key)
        with self.assertRaises(IntegrityError):
            apply_developing_profile(query,admission=bad['admission'],training_profiles=(('train1',a,contexts[0]),('train2',b,contexts[1])),query_session=bad['query_session'],context=qc)

    def test_MT11_MW08_actual_anchor_availability_and_next_open_touch(self):
        from trading_research.measurements.anchored import capture_anchor
        _,parts=self.tpo([(0,99)],end=2,width=1)
        _,_,a,g,_=parts
        for cut,events,end,spans in ((2,[],3,()),(3,[(3,100)],4,((2,3),))):
            rows=[row('touch',at=t,price=p,instrument=self.s.instrument.raw_symbol) for t,p in events]
            v,c,_=self.s.capture(rows,start=2,end=end,cut=cut,spans=spans)
            out=naked_reference(a,graph=g,level_ticks=100,price_capture=c,view=v,cut=cut)
            self.assertEqual(out['naked'],cut==2)
            if cut==3:self.assertEqual(out['first_touch_at'],3)
        p,*_=self.s.profile([(100,1,1)],start=10,end=11,published=15)
        a=p._recipe[1]['anchors'][0];g=p._recipe[1]['graphs'][0]
        with self.assertRaises(ContractError):
            capture_anchor(g,anchor_version_id=a.anchor.version_id,instrument=self.s.instrument,cut=12,published_at=12,definition_version='swing')
        actual=capture_anchor(g,anchor_version_id=a.anchor.version_id,instrument=self.s.instrument,cut=15,published_at=15,definition_version='swing')
        self.assertEqual(actual.anchor.start,10)

    def test_MP19_MA02_actual_F10_roles_freeze_all_V01_horizons(self):
        from trading_research.foundations.object_graph import ObjectGraph,RegistryDefinition,PublicationClock,AnchorVersion,EvidenceVersion,AtomicBatch,Support,EvidencePurpose
        from trading_research.measurements.measurement_ports import measurement_location,publish_measurement_location,location_targets,location_outcome
        from trading_research.measurements.anchored import capture_anchor
        from trading_research.measurements.tape import Trade,TradeLedger
        from trading_research.operations.artifacts import digest
        from trading_research.research.object_labels import ExactPoint
        from trading_research.research.labels import ObservationWindow
        end=7200000000000
        graph=ObjectGraph(self.s.root/'locations.sqlite',definition=RegistryDefinition(
            generator_versions=(('measurement-location-v1','v1'),),ttl_ns=end))
        v,c,_=self.s.capture([row('level',at=-2,price=100,instrument=self.s.instrument.raw_symbol)],start=-3,end=-1,cut=-1)
        a,_=self.s.anchor(c,graph=graph)
        accumulation=EvidenceVersion('s:location-accumulation','e:location-accumulation0',0,None,
            -1,-1,Support.OBSERVED,self.s.instrument,digest(c.record()),EvidencePurpose.MEASUREMENT)
        graph.commit_batch(AtomicBatch('batch:location-accumulation0',graph.sequence+1,graph.definition.version,
            PublicationClock(-1,-1,-1,actual_completion_at=-1),(accumulation,),1),expected_head=graph.head)
        for extras in ((accumulation.version_id,accumulation.version_id),a.anchor.evidence_versions,('e:absent',),[accumulation.version_id]):
            with self.assertRaises(ContractError):
                capture_anchor(graph,anchor_version_id=a.anchor.version_id,instrument=self.s.instrument,
                    cut=-1,published_at=-1,definition_version='event',accumulation_evidence_versions=extras)
        with self.assertRaises(ContractError):
            capture_anchor(graph,anchor_version_id=a.anchor.version_id,instrument=self.s.instrument,
                cut=-1,published_at=-1,definition_version='event',max_evidence=1,
                accumulation_evidence_versions=(accumulation.version_id,))
        a=capture_anchor(graph,anchor_version_id=a.anchor.version_id,instrument=self.s.instrument,
            cut=-1,published_at=-1,definition_version='event',max_evidence=2,
            accumulation_evidence_versions=(accumulation.version_id,))
        p=build_profile((c,),views=(v,),anchors=(a,),graphs=(graph,),grid=FrozenGrid(100,1,0,0,'fixed',-100),definition=ProfileDefinition('loc'))
        vw=measure_vwap((c,),views=(v,),anchors=(a,),graphs=(graph,),definition='vwap')
        valley_view,valley_capture,_=self.s.capture([row('valley-left',at=-3,price=99,instrument=self.s.instrument.raw_symbol),
            row('valley-right',at=-2,price=101,instrument=self.s.instrument.raw_symbol)],start=-4,end=-1,cut=-1)
        valley_anchor,_=self.s.anchor(valley_capture,graph=graph)
        valley=build_profile((valley_capture,),views=(valley_view,),anchors=(valley_anchor,),graphs=(graph,),
            grid=FrozenGrid(99,1,0,2,'valley-grid',-100),definition=ProfileDefinition('valley'))
        _,_,selection=self.s.clock(0,end,cut=0)
        source=GOLD['MP19']['inputs']['future_marks_minutes']
        objects={};frozen_targets={}
        for i,(value,role) in enumerate(((p,'poc'),(p,'value_low'),(p,'value_high'),(p,'buy_delta_peak'),(p,'sell_delta_peak'),
                (p,'absolute_delta_peak'),(p,'hvn'),(p,'poc_plateau'),(valley,'lvn'),
                (vw,'mean'),(vw,'median'),(vw,'quantile_low'),(vw,'quantile_high'),(vw,'sigma_low'),(vw,'sigma_high'))):
            loc=measurement_location(value,role=role)
            if role=='mean':
                head=graph.head
                with self.assertRaises(DependencyUnavailable):
                    publish_measurement_location(loc,graph=graph,clocks=PublicationClock(-2,-2,0,actual_completion_at=0),object_id='o:unavailable-mean')
                self.assertEqual(graph.head,head)
            obj=publish_measurement_location(loc,graph=graph,clocks=PublicationClock(0,-1,0,actual_completion_at=0),object_id='o:role:'+str(i))
            self.assertEqual(obj.confirmed_at,-1)
            self.assertEqual(graph.get_version(obj.evidence_versions[0]).content_digest,digest({
                'kind':'CausalMeasurementPublicationV1','measurement':loc.record(),
                'computation_clock':PublicationClock(0,-1,0,actual_completion_at=0)}))
            targets=location_targets(graph,obj.version_id,selection=selection,cut=0,side=1,favorable_distance=F(1),adverse_distance=F(1))
            objects[role]=obj;frozen_targets[role]=targets
            self.assertEqual(tuple(t.target.end for t in targets),tuple(GOLD['MP19']['expected']['ends']))
            self.assertEqual(len({t.target.version for t in targets}),4)
            for target in targets:
                points=tuple(ExactPoint(m*60000000000,0,F(price),m*60000000000) for m,price in source if m*60000000000 <= target.target.end)
                cov=ObservationWindow(0,target.target.end,target.target.end,version='role:'+target.horizon_kind)
                self.assertEqual(location_outcome(target,initial=F(99),points=points,coverage=cov,query_at=target.target.end-1)['state'],'pending')
                outcome=location_outcome(target,initial=F(99),points=points,coverage=cov,query_at=target.target.end)
                self.assertEqual(outcome['contact_at'],180000000000)
                self.assertEqual((target.target.band.lower,target.target.band.upper),(loc.geometry.contact_lower,loc.geometry.contact_upper))
                self.assertEqual(target.target.band.lower,100)
        old_mean=objects['mean'];old_anchor=a.anchor
        corrected_trade=Trade.restore(row('level-corrected',at=-2,known=1,price=102,instrument=self.s.instrument.raw_symbol))
        v.correct(id='location-source-correction',original_id='level',known_at=1,reason='source correction',replacement=corrected_trade)
        head=graph.head
        with self.assertRaises(IntegrityError):publish_measurement_location(measurement_location(vw,role='mean'),graph=graph,
            clocks=PublicationClock(2,2,2,actual_completion_at=2),object_id=old_mean.object_id,previous=old_mean)
        self.assertEqual(graph.head,head)
        restored_view=TradeLedger.restore(v.checkpoint())
        _,new_capture,_=self.s.capture([],view=restored_view,start=-3,end=-1,cut=1,published=1)
        source_evidence=EvidenceVersion(accumulation.source_id,'e:location-accumulation1',1,accumulation.version_id,
            -1,2,Support.OBSERVED,self.s.instrument,digest(new_capture.record()),EvidencePurpose.MEASUREMENT)
        graph.commit_batch(AtomicBatch('batch:location-source-corrected',graph.sequence+1,graph.definition.version,
            PublicationClock(2,2,2,actual_completion_at=2),(source_evidence,),1),expected_head=graph.head)
        self.assertFalse(graph.object_asof(old_mean.object_id,2).available(2,graph.definition.ttl_ns))
        with self.assertRaises(IntegrityError):
            measure_vwap((new_capture,),views=(restored_view,),anchors=(a,),graphs=(graph,),definition='vwap')
        anchored=capture_anchor(graph,anchor_version_id=old_anchor.version_id,instrument=self.s.instrument,
            cut=2,published_at=2,definition_version='event',max_evidence=2,
            accumulation_evidence_versions=(source_evidence.version_id,))
        corrected_vwap=measure_vwap((new_capture,),views=(restored_view,),anchors=(anchored,),graphs=(graph,),definition='vwap')
        revised=publish_measurement_location(measurement_location(corrected_vwap,role='mean'),graph=graph,
            clocks=PublicationClock(3,2,3,actual_completion_at=3),object_id=old_mean.object_id,previous=old_mean)
        self.assertEqual(revised.birth,old_mean.birth);self.assertEqual(revised.birth.anchors,(old_anchor.version_id,))
        self.assertEqual([graph.object_asof(old_mean.object_id,t).object.geometry.lower for t in (0,2,3)],[100,100,102])
        self.assertEqual(graph.object_asof(old_mean.object_id,3).born_at,0)
        self.assertTrue(graph.object_asof(old_mean.object_id,3).available(3,graph.definition.ttl_ns))
        self.assertIn(source_evidence.version_id,revised.evidence_versions)
        self.assertEqual(graph.get_version(old_anchor.version_id),old_anchor)
        self.assertTrue(all(t.target.band.lower==100 for t in frozen_targets['mean']))
        self.assertEqual(graph.active_set(end),())
        reopened=ObjectGraph(self.s.root/'locations.sqlite',definition=graph.definition)
        self.assertEqual([reopened.object_asof(old_mean.object_id,t).object.geometry.lower for t in (0,2,3)],[100,100,102])
        self.assertEqual(reopened.active_set(end),());self.assertEqual(reopened.get_version(old_mean.version_id),old_mean)

    def test_MT10_actual_source_clock_C01_F09_adapter(self):
        from datetime import date
        from trading_research.foundations.calendar import Calendar,Session,local_timestamp
        from datetime import time
        from trading_research.measurements.source_clocks import source_clock_selection,initial_balance_from_shared_bar,SOURCE_CLOCKS
        instrument=replace(self.s.instrument,valid_from=-(2**63),valid_until=2**63-1)
        sources=Sources(self,instrument=instrument);day=date(2026,1,5)
        start=local_timestamp(day,time(0),'America/New_York');end=local_timestamp(day,time(16),'America/New_York')
        cal=Calendar();cal.append(Session('daily',day,'NQ',start,end,(),0,start-1,'calendar-v1','source-clock',True,'synthetic'))
        clock_ids=[]
        for variant in ('ny_ib_60','exchange_ib_60'):
            selection=source_clock_selection(variant,calendar=cal,instrument=instrument,instrument_root='NQ',trading_date=day,
                cut=end,exchange_zone='America/Chicago')
            a,b=selection.formation_start,selection.formation_end
            rows=[row('inside',at=a,price=100,instrument=instrument.raw_symbol),row('last',at=b-1,price=102,instrument=instrument.raw_symbol),
                  row('outside',at=b,price=99,instrument=instrument.raw_symbol)]
            primitive,engine,bar,_=sources.primitive(rows,start=a,end=b,cut=end,published=end+2,selection=selection)
            with self.assertRaises(DependencyUnavailable):initial_balance_from_shared_bar(selection=selection,engine=engine,publication_version_id=bar.version_id,cut=end)
            value=initial_balance_from_shared_bar(selection=selection,engine=engine,publication_version_id=bar.version_id,cut=end+2)
            self.assertEqual(value.primitive.close_ticks,102);clock_ids.append(value.definition.clock_variant_id)
        self.assertNotEqual(*clock_ids)
        from datetime import timedelta
        from trading_research.measurements.source_clocks import weekly_balance_clocks,combined_weekly_balance,validate_combined_weekly_balance
        weekly_calendar=Calendar()
        for offset in (0,1):
            d=day+timedelta(days=offset)
            a=local_timestamp(d,time(22),'UTC');b=local_timestamp(d+timedelta(days=1),time(21),'UTC')
            weekly_calendar.append(Session('weekly:'+str(offset),d,'NQ',a,b,(),0,start-1,'weekly-calendar','UTC',True,'synthetic'))
        decision=b+1
        selections=weekly_balance_clocks(calendar=weekly_calendar,instrument=instrument,instrument_root='NQ',trading_date=day,cut=decision)
        primitives=[];daily=[]
        for i,(selection,prices) in enumerate(zip(selections,((100,103,101),(102,99,104)))):
            a,b=selection.formation_start,selection.formation_end
            rows=tuple(row('weekly:'+str(i)+':'+str(j),at=t,price=p,instrument=instrument.raw_symbol)
                for j,(t,p) in enumerate(zip((a,a+1,b-1),prices)))
            primitive,*_=sources.primitive(rows,start=a,end=b,cut=decision,published=decision+1,selection=selection)
            primitives.append(primitive)
            source_selection=source_clock_selection('weekly_source_daily_reset',calendar=weekly_calendar,instrument=instrument,
                instrument_root='NQ',trading_date=day+timedelta(days=i),cut=decision)
            _,engine,bar,_=sources.primitive(rows,start=a,end=b,cut=decision,published=decision+1,selection=source_selection)
            daily.append(initial_balance_from_shared_bar(selection=source_selection,engine=engine,publication_version_id=bar.version_id,cut=decision+1))
        kwargs=dict(calendar=weekly_calendar,instrument=instrument,instrument_root='NQ',trading_date=day,cut=decision+1)
        combined=combined_weekly_balance(tuple(primitives),**kwargs);validate_combined_weekly_balance(combined)
        self.assertEqual((combined.geometry.open,combined.geometry.high,combined.geometry.low,combined.geometry.close),(100,104,99,104))
        self.assertEqual(tuple((v.geometry.open,v.geometry.close) for v in daily),((100,101),(102,104)))
        self.assertEqual(combined.trading_dates,(day,day+timedelta(days=1)))
        with self.assertRaises(DependencyUnavailable):combined_weekly_balance(tuple(primitives[:1]),**kwargs)

    def test_MA01_actual_1024_profile_fit_rows_and_one_over(self):
        from trading_research.foundations.object_graph import ObjectGraph,RegistryDefinition,EvidenceVersion,AnchorVersion,AtomicBatch,PublicationClock,Support,EvidencePurpose
        from trading_research.measurements.anchored import capture_anchor
        from trading_research.operations.artifacts import digest
        rows=tuple(row('fit:'+str(i),at=i,price=100) for i in range(1024))
        view=ledger(rows)
        captures=tuple(self.s.capture([],view=view,start=i,end=i+1)[1] for i in range(1024))
        graph=ObjectGraph(self.s.root/'fit-capacity.sqlite',definition=RegistryDefinition(batch_members_max=2048))
        members=[]
        for i,capture in enumerate(captures):
            evidence=EvidenceVersion('s:fit:'+str(i),'e:fit:'+str(i),0,None,i+1,2048,
                Support.OBSERVED,self.s.instrument,digest(capture.record()),EvidencePurpose.MEASUREMENT)
            anchor=AnchorVersion('a:fit:'+str(i),'av:fit:'+str(i),0,None,(evidence.version_id,),i,i+1,i+1,2048)
            members.extend((evidence,anchor))
        graph.commit_batch(AtomicBatch('batch:fit-capacity',1,graph.definition.version,
            PublicationClock(2048,2048,2048,actual_completion_at=2048),tuple(members),2048),expected_head=graph.head)
        profiles=[]
        grid=FrozenGrid(100,1,0,0,'fit-capacity',-1);definition=ProfileDefinition('fit-capacity')
        for i,capture in enumerate(captures):
            anchor=capture_anchor(graph,anchor_version_id='av:fit:'+str(i),instrument=self.s.instrument,cut=2048,published_at=2048,definition_version='fit-capacity')
            profile=build_profile((capture,),views=(view,),anchors=(anchor,),graphs=(graph,),grid=grid,definition=definition)
            profiles.append((profile,(i-1,'same')))
        state=fit_developing_profile(tuple(profiles),train_end=2048,available_at=2049)
        self.assertEqual((len(state.training_profiles),state.pooled_rates,state.cells),(1024,(1,),(('same',(1,),1024),)))
        with self.assertRaises(ContractError):fit_developing_profile(tuple(profiles)+(profiles[0],),train_end=2048,available_at=2049)

    def test_MA08_source_accounting_has_explicit_remaining_requirements(self):
        base=Path(__file__).resolve().parents[1]
        preparation=json.loads((base/'reports/m0407m13-source-preparation.json').read_text())
        mapping=json.loads((base/'reports/m0407m13-case-test-map.json').read_text())
        expected={r['id'] for r in preparation['source_clauses']}
        actual={r['source_id'] for r in mapping['source_dispositions']}
        self.assertEqual(len(expected),182);self.assertEqual(actual,expected)
        self.assertTrue(all(r['whole_source_closed'] is False and r['remaining'] for r in mapping['source_dispositions']))

    def test_MA01_actual_source_and_retained_byte_capacity(self):
        from trading_research.measurements.profiles import auction_sources
        from trading_research.foundations.object_graph import ObjectGraph,RegistryDefinition,EvidenceVersion,AnchorVersion,AtomicBatch,PublicationClock,Support,EvidencePurpose
        from trading_research.measurements.anchored import capture_anchor
        from trading_research.operations.artifacts import digest
        rows=tuple(row('p'+str(i),at=i,price=100,size=1) for i in range(4096))
        view,c,_=self.s.capture(rows,end=4096)
        a,g=self.s.anchor(c)
        kwargs=dict(views=(view,),anchors=(a,),graphs=(g,),grid=FrozenGrid(100,1,0,0,'capacity',-1),definition=ProfileDefinition('capacity'))
        p=build_profile((c,),**kwargs)
        self.assertEqual((len(p.members),p.total_mass),(4096,4096))
        with self.assertRaises(ContractError):build_profile((c,),**kwargs,max_inputs=4095)
        exact=max(len(canonical_json(p.record())),len(canonical_json(tuple(t.record() for t in p.members))))
        self.assertEqual(build_profile((c,),**kwargs,max_bytes=exact).record(),p.record())
        with self.assertRaises(ContractError):build_profile((c,),**kwargs,max_bytes=exact-1)
        single_view,single,_=self.s.capture([row('single',at=0)],end=1)
        graph=ObjectGraph(self.s.root/'many-anchors.sqlite',definition=RegistryDefinition(batch_members_max=512))
        evidence=EvidenceVersion('s:common','e:common',0,None,1,1,Support.OBSERVED,self.s.instrument,digest(single.record()),EvidencePurpose.MEASUREMENT)
        anchors=tuple(AnchorVersion('a:'+str(i),'av:'+str(i),0,None,(evidence.version_id,),0,1,1,1) for i in range(256))
        graph.commit_batch(AtomicBatch('batch:many',1,graph.definition.version,PublicationClock(1,1,1,actual_completion_at=1),(evidence,*anchors),257),expected_head=graph.head)
        captures=tuple(capture_anchor(graph,anchor_version_id=a.version_id,instrument=self.s.instrument,cut=1,published_at=1,definition_version='composite') for a in anchors)
        members,visits=auction_sources((single,)*256,views=(single_view,)*256,anchors=captures,graphs=(graph,)*256)
        self.assertEqual((len(members),visits),(1,256))
        with self.assertRaises(ContractError):auction_sources((single,)*257,views=(single_view,)*257,anchors=captures+(captures[0],),graphs=(graph,)*257)
