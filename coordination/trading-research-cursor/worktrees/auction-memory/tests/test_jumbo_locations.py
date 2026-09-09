"""Independent literal geometry/contact cases; run only in registered check.

Full design-case source SHA a8a3c0ff3f403d7c2d931a380b9fc08d06ea5938c9e6202c3e725df3cef56c38.
Cases requiring profile/model/version registry integration are explicitly outside
this kernel: their retained literals must be consumed by the integration suite.
"""
from fractions import Fraction
import unittest
import numpy as np
from trading_research.research.ohlc_ranges import MinuteBars
from trading_research.research.jumbo_locations import range_candidate_specs, append_candidate_bands, evaluate_location_bands

M = 60_000_000_000


def formation(low=90,high=110,op=100,close=102,available=0,contract="RAW"):
    return dict(status="complete",low_ticks=low,high_ticks=high,open_ticks=op,close_ticks=close,
                available_at_ns=available,contract_key=contract,formation_id="literal-ancestor",source_version="independent-literal")


def bars(rows, *, starts=None, known=None, keys=None, valid=None):
    n=len(rows)
    starts=list(range(n)) if starts is None else starts
    values=dict(start_ns=[t*M for t in starts],end_ns=[(t+1)*M for t in starts],
                known_at_ns=[(t+1)*M for t in starts] if known is None else known,
                volume=[1]*n,contract_key=["RAW"]*n if keys is None else keys,
                valid=[True]*n if valid is None else valid)
    for at,name in enumerate(("open_ticks","high_ticks","low_ticks","close_ticks")):
        values[name]=[r[at] for r in rows]
    return MinuteBars(values,source_version="independent-literal")


def point(value=100, *, low=None, high=None, available=0, contract="RAW"):
    return range_candidate_specs(formation(available=available,contract=contract),definitions=[
        dict(name="literal",geometry="custom_band",lower=value if low is None else low,upper=value if high is None else high)])


def evaluate(rows, *, candidate=None,horizon=None,departure=5,starts=None,known=None,keys=None,valid=None,cut=None):
    n=len(rows) if horizon is None else horizon
    series=bars(rows,starts=starts,known=known,keys=keys,valid=valid)
    window=series.window(0,n*M)
    return evaluate_location_bands(window,point() if candidate is None else candidate,horizons=(n,),
                                   available_cut=n*M if cut is None else cut,departure_ticks=departure)["columns"]


class JumboLocationLiteralTests(unittest.TestCase):
    def bounds(self,out,name,expected):
        self.assertEqual((int(out[name+"_lower"][0,0]),int(out[name+"_upper"][0,0])),tuple(expected))

    def test_exact_quarters_close_body_and_edges(self):
        result=range_candidate_specs(formation(100,120,103,119))
        self.assertEqual(len(result["columns"]["slot"]),26)
        values={d["name"]:Fraction(int(result["columns"]["lower_num"][i]),int(result["columns"]["lower_den"][i])) for i,d in enumerate(result["metadata"]["definitions"])}
        self.assertEqual([values[n] for n in ("quarter","EQ","threequarter","open","close")],[105,110,115,103,119])
        self.assertEqual(values["body25"],115)
        self.assertEqual(values["lower_body25"],107)
        self.assertEqual(values["wick25"],105)

    def test_coincidence_zero_width_and_ancestry(self):
        for f in (formation(100,120,110,110),formation(100,100,100,100)):
            r=range_candidate_specs(f)
            self.assertEqual(len(r["columns"]["slot"]),26)
            self.assertTrue(r["columns"]["valid_geometry"].all())
            self.assertEqual(r["metadata"]["formation_id"],"literal-ancestor")
        self.assertTrue(r["metadata"]["zero_width"])
        self.assertEqual(len(set(zip(r["columns"]["lower_num"],r["columns"]["lower_den"]))),1)

    def test_edge_relative_decimal_and_mirror(self):
        r=range_candidate_specs(formation(100,200,100,200))
        values={d["name"]:(Fraction(int(r["columns"]["lower_num"][i]),int(r["columns"]["lower_den"][i])),Fraction(int(r["columns"]["upper_num"][i]),int(r["columns"]["upper_den"][i]))) for i,d in enumerate(r["metadata"]["definitions"])}
        self.assertEqual(values["upper_k133_100"],(333,333))
        self.assertEqual(values["lower_k133_100"],(-33,-33))
        self.assertEqual(values["lower_133_166"],(-66,-33))
        self.assertEqual(values["upper_133_166"],(333,366))
        r=range_candidate_specs(formation(0,3,0,3))
        i=next(i for i,d in enumerate(r["metadata"]["definitions"]) if d["name"]=="upper_k133_100")
        self.assertEqual((int(r["columns"]["lower_num"][i]),int(r["columns"]["lower_den"][i])),(699,100))

    def test_internal_continuation_no_edge_gate(self):
        out=evaluate([(99,100,98,100),(101,106,101,105)])
        self.bounds(out,"reach",(1,1)); self.bounds(out,"up_first",(1,1))

    def test_gap_without_contact(self):
        out=evaluate([(98,99,97,99),(102,104,101,103)])
        self.bounds(out,"reach",(0,0))
        self.assertEqual(int(out["gap_through"][0,0]),1)

    def test_negative_fraction_straddle_not_print(self):
        out=evaluate([(-1,0,-3,-2),(1,2,0,1)],candidate=point(Fraction(-3,2)))
        self.bounds(out,"reach",(0,0))
        self.assertFalse(out["has_lattice_price"][0])
        self.assertTrue(out["contact_ineligible_empty_lattice"][0])
        self.assertEqual(int(out["source_bar_intersection_count"][0,0]),1)
        self.assertEqual(int(out["compatible_count"][0,0]),0)
        self.assertEqual(int(out["definite_count"][0,0]),0)
        self.assertEqual(int(out["gap_through"][0,0]),1)

    def test_empty_lattice_band_vs_integer_endpoint(self):
        rows=[(100,101,100,101)]
        empty=evaluate(rows,candidate=point(low=Fraction(501,5),high=Fraction(504,5)))
        self.bounds(empty,"reach",(0,0))
        self.assertEqual(int(empty["source_bar_intersection"][0,0]),1)
        full=evaluate(rows,candidate=point(low=Fraction(501,5),high=101))
        self.bounds(full,"reach",(1,1))
        self.assertTrue(full["has_lattice_price"][0])

    def test_empty_lattice_no_future_has_structural_zero_joint_events(self):
        s=bars([(100,102,99,101)])
        out=evaluate_location_bands(s.window(2*M,3*M),point(Fraction(201,2)),horizons=(1,),available_cut=3*M,departure_ticks=5)["columns"]
        self.assertTrue(out["geometry_eligible"][0])
        self.assertFalse(out["eligible"][0])
        for name in ("reach","up_reach","down_reach","up_first","down_first","close_above_invalidation","close_below_invalidation"):
            self.bounds(out,name,(0,0))
        self.assertEqual(int(out["source_bar_intersection_upper"][0,0]),1)
        self.assertTrue(np.isnan(out["up_excursion_upper"][0,0]))

    def test_unconditional_fractional_barriers_do_not_require_contact(self):
        out=evaluate([(100,101,100,101)],candidate=point(Fraction(201,2)),departure=Fraction(1,4))
        self.bounds(out,"reach",(0,0))
        self.bounds(out,"unconditional_upper_barrier_reach",(1,1))
        self.bounds(out,"unconditional_lower_barrier_reach",(1,1))
        self.assertTrue(out["geometry_eligible"][0])
        self.assertFalse(out["eligible"][0])

    def test_empty_lattice_censored_unconditional_barriers_remain_unknown(self):
        s=bars([(100,102,99,101)])
        out=evaluate_location_bands(s.window(2*M,3*M),point(Fraction(201,2)),horizons=(1,),available_cut=3*M,departure_ticks=5)["columns"]
        self.bounds(out,"reach",(0,0))
        self.bounds(out,"unconditional_upper_barrier_reach",(0,1))
        self.bounds(out,"unconditional_lower_barrier_reach",(0,1))

    def test_integer_lattice_does_not_require_unit_step_trades(self):
        out=evaluate([(99,101,99,101)],candidate=point(100))
        self.bounds(out,"reach",(0,1))
        self.assertTrue(out["has_lattice_price"][0])

    def test_same_bar_competing_barriers(self):
        out=evaluate([(100,106,94,101)])
        self.bounds(out,"reach",(1,1)); self.bounds(out,"up_first",(0,1)); self.bounds(out,"down_first",(0,1))
        self.assertEqual(out["up_excursion_lower"][0,0],6)
        self.assertEqual(out["down_excursion_lower"][0,0],6)

    def test_close_contact_does_not_order_prior_extrema(self):
        out=evaluate([(110,112,100,100)])
        self.bounds(out,"reach",(1,1))
        self.assertEqual((out["up_excursion_lower"][0,0],out["up_excursion_upper"][0,0]),(0,12))

    def test_uncertain_first_contact_unions_possible_bars(self):
        out=evaluate([(99,102,98,101),(105,108,104,106),(101,103,100,102)])
        self.bounds(out,"reach",(1,1))
        self.assertEqual(int(out["first_possible_minute"][0,0]),0)
        self.assertEqual(int(out["first_definite_minute"][0,0]),2)
        self.assertEqual(out["up_excursion_upper"][0,0],8)
        self.assertEqual(out["up_excursion_lower"][0,0],2)

    def test_censored_no_contact_and_known_contact(self):
        out=evaluate([(90,92,89,91)],horizon=3)
        self.bounds(out,"reach",(0,1))
        self.assertFalse(out["complete_horizon"][0])
        out=evaluate([(100,102,99,101)],horizon=3)
        self.bounds(out,"reach",(1,1))
        self.assertTrue(np.isnan(out["up_excursion_upper"][0,0]))

    def test_far_failure_retained(self):
        out=evaluate([(100,110,90,105)],candidate=point(600))
        self.assertTrue(out["eligible"][0]); self.bounds(out,"reach",(0,0))

    def test_publication_before_origin_required(self):
        out=evaluate([(100,105,99,101)],candidate=point(100,available=M))
        self.assertFalse(out["eligible"][0]); self.assertEqual(int(out["candidate_reason"][0])&2,2)

    def test_contract_coordinate_mismatch(self):
        out=evaluate([(100,105,99,101)],candidate=point(100,contract="OTHER"))
        self.assertFalse(out["eligible"][0]); self.assertEqual(int(out["candidate_reason"][0])&4,4)

    def test_roll_gap_invalid_and_late_stop_prefix(self):
        scenarios=[dict(starts=[0,2]),dict(keys=["RAW","NEXT"]),dict(valid=[True,False]),dict(known=[M,4*M])]
        for kwargs in scenarios:
            with self.subTest(kwargs=kwargs):
                out=evaluate([(90,92,89,91),(100,102,99,101)],horizon=3,**kwargs)
                self.assertEqual(int(out["observed_minutes"][0]),1)
                self.bounds(out,"reach",(0,1))

    def test_original_observation_cut_not_widened(self):
        s=bars([(90,92,89,91),(100,102,99,101)])
        window=s.window(0,2*M,available_at=M)
        out=evaluate_location_bands(window,point(),horizons=(2,),available_cut=2*M,departure_ticks=5)["columns"]
        self.assertEqual(int(out["observed_minutes"][0]),1)
        self.bounds(out,"reach",(0,1))

    def test_band_width_and_uncertainty_separate(self):
        rows=[(104,104,103,103)]
        self.bounds(evaluate(rows),"reach",(0,0))
        self.bounds(evaluate(rows,candidate=point(low=95,high=105)),"reach",(1,1))
        self.bounds(evaluate([(108,109,107,108)]),"reach",(0,0))

    def test_append_snap_preserves_original_and_missing_prediction(self):
        base=point()
        joined=append_candidate_bands(base,[dict(name="snap",lower=102,upper=102),dict(name="unavailable",lower=None,upper=None)])
        self.assertEqual(len(base["columns"]["slot"]),1)
        self.assertEqual(len(joined["columns"]["slot"]),3)
        s=bars([(102,103,101,102)])
        out=evaluate_location_bands(s.window(0,M),joined,horizons=(1,),available_cut=M,departure_ticks=5)["columns"]
        self.assertEqual(out["reach_lower"][:,0].tolist(),[0,1,0])
        self.assertEqual(out["eligible"].tolist(),[True,True,False])

    def test_crossed_band_rejected(self):
        with self.assertRaises(ValueError):
            point(low=110,high=104)

    def test_flicker_and_two_observed_episodes(self):
        out=evaluate([(100,102,99,101),(101,103,99,102),(102,104,100,103)])
        self.assertEqual(int(out["possible_episode_count"][0,0]),1)
        self.assertEqual(int(out["definite_episode_count"][0,0]),1)
        out=evaluate([(100,101,99,100),(103,104,102,103),(104,105,103,104),(100,102,99,101)])
        self.assertEqual(int(out["possible_episode_count"][0,0]),2)
        self.assertEqual(int(out["definite_episode_count"][0,0]),2)

    def test_close_invalidation_not_wick(self):
        out=evaluate([(100,102,94,98)])
        self.bounds(out,"close_below_invalidation",(0,0))
        self.bounds(out,"down_reach",(1,1))

    def test_horizon_shapes_and_chunk_invariance(self):
        s=bars([(100,106,99,105),(105,107,94,96),(96,101,95,100)])
        small=point()
        large=append_candidate_bands(small,[dict(name=str(i),lower=100,upper=100) for i in range(260)])
        a=evaluate_location_bands(s.window(0,3*M),small,horizons=(1,3),available_cut=3*M,departure_ticks=5)["columns"]
        b=evaluate_location_bands(s.window(0,3*M),large,horizons=(1,3),available_cut=3*M,departure_ticks=5)["columns"]
        self.assertEqual(b["reach_lower"].shape,(261,2))
        for key,value in a.items():
            if value.ndim==2:
                np.testing.assert_equal(b[key],np.repeat(value,261,axis=0))

    def test_large_integer_exact_contact(self):
        x=2**53+1
        out=evaluate([(x,x+2,x-1,x+1)],candidate=point(x),departure=1)
        self.bounds(out,"reach",(1,1))
        self.assertEqual(out["up_excursion_upper"][0,0],2)
        self.assertEqual(out["down_excursion_upper"][0,0],1)

    def test_input_constraints(self):
        with self.assertRaises(ValueError):
            point(1.5)
        with self.assertRaises(ValueError):
            evaluate([(100,102,99,101)],departure=0)
        s=bars([(100,102,99,101)])
        with self.assertRaises(ValueError):
            evaluate_location_bands(s.window(0,M),point(),horizons=(181,),available_cut=M,departure_ticks=1)

    def test_no_mutation_and_changed_geometry(self):
        original=range_candidate_specs(formation(100,120,110,110))
        revised=range_candidate_specs(formation(100,140,110,110))
        self.assertEqual(int(original["columns"]["lower_num"][1]),110)
        self.assertEqual(int(revised["columns"]["lower_num"][1]),120)
        self.assertEqual(original["metadata"]["definitions"][1]["name"],"EQ")

    def test_wholly_missing_future_retains_unknown_candidate(self):
        s=bars([(100,102,99,101)])
        out=evaluate_location_bands(s.window(2*M,3*M),point(),horizons=(1,),available_cut=3*M,departure_ticks=5)["columns"]
        self.assertTrue(out["eligible"][0])
        self.bounds(out,"reach",(0,1))
        self.assertEqual(int(out["observed_minutes"][0]),0)

    def test_evaluation_cut_precedes_candidate_publication(self):
        s=bars([(100,102,99,101)])
        out=evaluate_location_bands(s.window(M,2*M),point(available=M),horizons=(1,),available_cut=0,departure_ticks=5)["columns"]
        self.assertFalse(out["eligible"][0])

    def test_custom_availability_cannot_precede_inputs(self):
        candidate=range_candidate_specs(formation(available=M),definitions=[dict(name="late",lower=100,upper=100,available_at_ns=2*M)])
        self.assertEqual(int(candidate["columns"]["available_at_ns"][0]),2*M)
        earlier=range_candidate_specs(formation(available=M),definitions=[dict(name="early",lower=100,upper=100,available_at_ns=0)])
        self.assertEqual(int(earlier["columns"]["available_at_ns"][0]),M)
        appended=append_candidate_bands(earlier,[dict(name="cannot-backdate",lower=101,upper=101,available_at_ns=0)])
        self.assertEqual(int(appended["columns"]["available_at_ns"][1]),M)

    def test_malformed_candidate_columns_rejected_before_conversion(self):
        mutations=[("lower_num",np.array([100.],dtype=np.float64)),("lower_den",np.array([0],dtype=np.int64)),
                   ("upper_den",np.array([-1],dtype=np.int64)),("available_at_ns",np.array([-1],dtype=np.int64)),
                   ("lower_num",np.array([100,101],dtype=np.int64)),("lower_num",np.array([[100]],dtype=np.int64))]
        s=bars([(100,102,99,101)])
        for name,value in mutations:
            with self.subTest(name=name,value=value):
                candidate=point()
                candidate["columns"][name]=value
                with self.assertRaises(ValueError):
                    evaluate_location_bands(s.window(0,M),candidate,horizons=(1,),available_cut=M,departure_ticks=5)

    def test_int64_horizon_endpoint_overflow_rejected(self):
        start=(np.iinfo(np.int64).max//M-1)*M
        s=bars([(100,102,99,101)],starts=[int(start//M)])
        with self.assertRaises(ValueError):
            evaluate_location_bands(s.window(int(start),int(start+M)),point(),horizons=(3,),available_cut=int(start+M),departure_ticks=5)

    def test_stop_reasons_and_no_price_gap_across_missing_minutes(self):
        scenarios=[(dict(starts=[0,2]),2,True),(dict(valid=[True,False]),4,True),
                   (dict(keys=["RAW","NEXT"]),8,True),(dict(known=[M,4*M]),16,False)]
        for kwargs,reason,gap in scenarios:
            with self.subTest(kwargs=kwargs):
                out=evaluate([(98,99,97,99),(102,104,101,103)],horizon=3,**kwargs)
                self.assertEqual(int(out["prefix_stop_reason"][0]),reason)
                self.assertEqual(bool(out["coverage_gap"][0]),gap)
                self.assertEqual(int(out["gap_through"][0,0]),0)

    def test_source_identity_is_series_not_window_version(self):
        s=bars([(100,102,99,101)])
        candidate=point()
        candidate["metadata"]["formation_id"]="older-legitimate-window-version"
        out=evaluate_location_bands(s.window(0,M),candidate,horizons=(1,),available_cut=M,departure_ticks=5)["columns"]
        self.assertTrue(out["eligible"][0])
        candidate["metadata"]["source_version"]="different-immutable-series"
        out=evaluate_location_bands(s.window(0,M),candidate,horizons=(1,),available_cut=M,departure_ticks=5)["columns"]
        self.assertFalse(out["eligible"][0])
        self.assertEqual(int(out["candidate_reason"][0])&32,32)
