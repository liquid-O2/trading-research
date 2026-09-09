"""Literal factorized integration checks, to run only in registered code check."""
import unittest
from types import SimpleNamespace
from fractions import Fraction
import numpy as np
from trading_research.research.ohlc_ranges import MinuteBars
from trading_research.research.jumbo_location_tables import extract_location_year, preflight_location_year

M = 60_000_000_000


def series(*, missing=(), source="literal", price=120):
    starts = [i for i in range(2,190) if i not in missing]
    return MinuteBars(dict(start_ns=[i*M for i in starts],end_ns=[(i+1)*M for i in starts],
       known_at_ns=[(i+2)*M for i in starts],open_ticks=[price]*len(starts),
       high_ticks=[price+1]*len(starts),low_ticks=[price-1]*len(starts),
       close_ticks=[price]*len(starts),volume=[1]*len(starts),
       contract_key=["RAW"]*len(starts),valid=[True]*len(starts)),source_version=source)


def row(**changes):
    value=dict(root="NQ",year=2020,date="2020-01-02",clock="literal-clock",formation_id="one",
       source_version="literal",window_version="formation-window",contract_key="RAW",
       formation_start_ns=0,formation_end_ns=2*M,origin_ns=5*M,available_at_ns=3*M,
       status="complete",low_ticks=100,high_ticks=110,open_ticks=102,close_ticks=108,
       width_ticks=10,exclusion_reasons="",source_ids="L01")
    value.update(changes)
    return value


def extract(rows=None, *, bars=None, cut=200*M, plan=None):
    return extract_location_year(series() if bars is None else bars,[row()] if rows is None else rows,
       root="NQ",year=2020,evaluation_cut=cut,plan={} if plan is None else plan)


class LocationTablesTests(unittest.TestCase):
    def test_factorized_axes_and_continuous_precision(self):
        result=extract()
        a,m=result["arrays"],result["manifest"]
        self.assertEqual(a["outcome_reach_lower"].shape,(1,104,4))
        self.assertEqual(a["horizon_observed_minutes"].shape,(1,4))
        self.assertEqual(a["outcome_up_excursion_upper"].dtype,np.dtype("float64"))
        self.assertEqual(a["geometry_lower_num"].dtype,np.dtype("int64"))
        self.assertEqual(m["candidate_count"],104)
        self.assertEqual(m["array_bytes"],sum(v.nbytes for v in a.values()))
        np.testing.assert_array_equal(a["ancestor_slot"],list(range(26))*4)
        np.testing.assert_array_equal(a["generator_id"],[0]*26+[1]*26+[2]*26+[3]*26)

    def test_declared_origin_and_expected_published_anchor(self):
        m=extract()["manifest"]["formations"][0]
        self.assertEqual(m["available_at_ns"],3*M)
        self.assertEqual(m["forecast_origin_ns"],5*M)
        self.assertEqual(m["anchor_ticks"],120)
        self.assertEqual(m["anchor_age_ns"],M)
        self.assertFalse(m["anchor_fallback"])
        self.assertEqual(m["departure_ticks"],3)
        self.assertEqual(Fraction(*m["departure_width_ratio"]),Fraction(3,10))

    def test_availability_rounding_and_maturity(self):
        result=extract([row(available_at_ns=5*M+1)])
        m=result["manifest"]["formations"][0]
        self.assertEqual(m["creation_cut_ns"],5*M+1)
        self.assertEqual(m["forecast_origin_ns"],6*M)
        self.assertEqual(int(result["arrays"]["horizon_endpoint_ns"][0,0]),21*M)
        self.assertEqual(int(result["arrays"]["horizon_maturity_ns"][0,0]),22*M)

    def test_missing_expected_anchor_falls_back_not_older_series_close(self):
        m=extract(bars=series(missing=(3,)))["manifest"]["formations"][0]
        self.assertEqual(m["anchor_ticks"],108)
        self.assertEqual(m["anchor_age_ns"],3*M)
        self.assertTrue(m["anchor_fallback"])

    def test_mirror_exact_width_distance_side_and_lineage(self):
        result=extract()
        a=result["arrays"]
        for i in range(26):
            lo=lambda j:Fraction(int(a["geometry_lower_num"][0,j]),int(a["geometry_lower_den"][0,j]))
            hi=lambda j:Fraction(int(a["geometry_upper_num"][0,j]),int(a["geometry_upper_den"][0,j]))
            self.assertEqual(lo(i+26),240-hi(i))
            self.assertEqual(hi(i+26),240-lo(i))
            self.assertEqual(hi(i)-lo(i),hi(i+26)-lo(i+26))
            self.assertEqual(int(a["anchor_side"][0,i+26]),-int(a["anchor_side"][0,i]))
            self.assertEqual(result["manifest"]["candidate_definitions"][i+26]["ancestor_slot"],i)

    def test_unavailable_formation_retains_all_slots(self):
        result=extract([row(status="censored",available_at_ns=None,low_ticks=None,high_ticks=None,
                              open_ticks=None,close_ticks=None)])
        a=result["arrays"]
        self.assertEqual(result["manifest"]["candidate_count"],104)
        self.assertFalse(a["geometry_valid_geometry"].any())
        self.assertFalse(a["outcome_eligible"].any())

    def test_censored_future_keeps_eligible_unknown_bounds(self):
        a=extract(cut=5*M)["arrays"]
        self.assertTrue((a["horizon_maturity_ns"]==-1).all())
        self.assertTrue((a["horizon_prefix_maturity_ns"]==-1).all())
        self.assertTrue(a["outcome_geometry_eligible"].all())
        np.testing.assert_array_equal(a["outcome_eligible"],a["outcome_has_lattice_price"])
        self.assertTrue((a["outcome_reach_lower"]==0).all())
        np.testing.assert_array_equal(a["outcome_reach_upper"],np.broadcast_to(a["outcome_has_lattice_price"][:,:,None],a["outcome_reach_upper"].shape))
        self.assertTrue(np.isnan(a["outcome_up_excursion_upper"]).all())

    def test_zero_width_one_tick_barrier_and_coincident_slots_kept(self):
        result=extract([row(low_ticks=100,high_ticks=100,open_ticks=100,close_ticks=100,width_ticks=0)])
        self.assertEqual(result["manifest"]["formations"][0]["departure_ticks"],1)
        self.assertIsNone(result["manifest"]["formations"][0]["departure_width_ratio"])
        self.assertEqual(result["manifest"]["candidate_count"],104)

    def test_original_order_and_all_invalid_first_schema(self):
        result=extract([row(formation_id="missing",status="censored",available_at_ns=None),row(formation_id="ok")])
        self.assertEqual([r["formation_id"] for r in result["manifest"]["formations"]],["missing","ok"])
        self.assertFalse(result["arrays"]["outcome_eligible"][0].any())
        self.assertTrue(result["arrays"]["outcome_geometry_eligible"][1].all())

    def test_strict_identity_denominator_and_size_guards(self):
        bads=([row(root="ES")],[row(year=2021)],[row(date="2021-01-02")],
              [row(source_version="other")],[row(),row()],[row(origin_ns=5.0*M)])
        for rows in bads:
            with self.assertRaises(ValueError): extract(rows)
        with self.assertRaises(ValueError): extract(plan={"location_departure_width_ratio":[1,0]})
        with self.assertRaises(ValueError): extract(plan={"location_max_output_bytes":1})

    def test_reflection_above_float_exactness_limit(self):
        large=2**53+100
        r=row(low_ticks=large,high_ticks=large+10,open_ticks=large+2,close_ticks=large+8)
        a=extract([r],bars=series(price=large+20))["arrays"]
        self.assertEqual(Fraction(int(a["geometry_lower_num"][0,26]),int(a["geometry_lower_den"][0,26])),Fraction(2*(large+20))-Fraction(4*large+10,4))

    def test_explicit_two_generator_plan_and_invalid_lists(self):
        result=extract(plan={"location_generators":["raw","mirrored_raw"]})
        self.assertEqual(result["manifest"]["candidate_count"],52)
        self.assertEqual(result["arrays"]["outcome_reach_lower"].shape,(1,52,4))
        with self.assertRaises(ValueError):extract(plan={"location_generators":["tick_snapped"]})

    def test_snapped_point_and_band_geometry_are_explicit(self):
        result=extract()
        a=result["arrays"]
        value=lambda name,i:Fraction(int(a[name+"_num"][0,i]),int(a[name+"_den"][0,i]))
        # Quarter 102.5 below the available anchor120 becomes102; mirror138.
        self.assertEqual(value("geometry_lower",0),Fraction(205,2))
        self.assertEqual(value("geometry_lower",52),102)
        self.assertEqual(value("geometry_lower",78),138)
        self.assertEqual(value("anchor_distance_change",52),Fraction(1,2))
        self.assertEqual(value("anchor_distance_change",78),Fraction(1,2))
        self.assertEqual(value("width_change",52),0)
        self.assertFalse(a["outcome_has_lattice_price"][0,0])
        self.assertTrue(a["outcome_has_lattice_price"][0,52])
        self.assertTrue(a["outcome_has_lattice_price"][0,52:].all())
        # Lower source region83.4..86.7 becomes minimal outer cover83..87.
        self.assertEqual(value("geometry_lower",73),83)
        self.assertEqual(value("geometry_upper",73),87)
        self.assertEqual(value("width_change",73),Fraction(7,10))

    def test_snapped_above_anchor_ceil_and_exact_anchor_identity(self):
        result=extract(bars=series(price=100))
        a=result["arrays"]
        self.assertEqual(int(a["geometry_lower_num"][0,52]),103)
        # Source low100 equals anchor100 and remains100.
        self.assertEqual(int(a["geometry_lower_num"][0,57]),100)

    def test_derived_geometry_known_no_earlier_than_actual_anchor(self):
        result=extract()
        at=result["arrays"]["geometry_available_at_ns"][0]
        np.testing.assert_array_equal(at[:26],np.full(26,3*M))
        np.testing.assert_array_equal(at[26:],np.full(78,5*M))
        self.assertEqual(result["manifest"]["formations"][0]["anchor_known_at_ns"],5*M)

    def test_fallback_requires_exact_available_formation_end(self):
        for end in (None,6*M):
            result=extract([row(formation_end_ns=end)],bars=series(missing=(3,)))
            self.assertIsNone(result["manifest"]["formations"][0]["anchor_ticks"])
            self.assertFalse(result["arrays"]["geometry_valid_geometry"][0,26:].any())
        with self.assertRaises(ValueError):extract([row(formation_end_ns=2.0*M)],bars=series(missing=(3,)))
        result=extract([row(available_at_ns=None)],bars=series(missing=(3,)))
        self.assertIsNone(result["manifest"]["formations"][0]["anchor_known_at_ns"])
        self.assertFalse(result["arrays"]["geometry_valid_geometry"].any())

    def test_empty_year_invalid_dates_and_identity_types_rejected(self):
        with self.assertRaises(ValueError):extract([])
        for change in ({"date":"2020-02-30"},{"date":"20200102"},{"date":20200102},
                       {"year":2020.0},{"source_version":""},{"source_version":None}):
            with self.subTest(change=change),self.assertRaises(ValueError):extract([row(**change)])
        with self.assertRaises(ValueError):
            extract([row(source_version=None)],bars=SimpleNamespace(source_version=None))

    def test_ratio_bounds_apply_even_to_zero_width_formation(self):
        zero=row(low_ticks=100,high_ticks=100,open_ticks=100,close_ticks=100,width_ticks=0)
        for ratio in (Fraction(2**64),Fraction(1,2**64)):
            with self.subTest(ratio=ratio),self.assertRaises(ValueError):
                extract([zero],plan={"location_departure_width_ratio":ratio})

    def test_preflight_validates_unselected_rows_before_cost_projection(self):
        dates=[f"2020-01-{i:02}" for i in range(2,8)]
        rows=[row(date=day,formation_id=day) for day in dates]
        for bad in (row(date="2020-01-08",formation_id="bad",source_version="wrong"),
                    row(date="2020-02-30",formation_id="bad"),
                    row(date="2020-01-08",formation_id="bad",root="ES")):
            with self.subTest(bad=bad),self.assertRaises(ValueError):
                preflight_location_year(series(),rows+[bad],root="NQ",year=2020,evaluation_cut=200*M,plan={},dates=dates)

    def test_preflight_requires_six_present_predeclared_dates(self):
        with self.assertRaises(ValueError):
            preflight_location_year(series(),[row()],root="NQ",year=2020,evaluation_cut=200*M,plan={},dates=["2020-01-02"])
        with self.assertRaises(ValueError):
            preflight_location_year(series(),[row()],root="NQ",year=2020,evaluation_cut=200*M,plan={},
                                    dates=[f"2020-01-{i:02}" for i in range(2,8)])

if __name__ == "__main__":
    unittest.main()

