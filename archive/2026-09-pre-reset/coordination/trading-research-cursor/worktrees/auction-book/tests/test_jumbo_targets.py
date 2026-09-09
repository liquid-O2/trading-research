"""Independent target contracts; authored without executing candidate code."""
from datetime import date
import unittest
import numpy as np
from trading_research.errors import ContractError
from trading_research.research.jumbo_matrix import PreparedPaths, PATH_CLASSES
from trading_research.research.jumbo_targets import (
    boundary_ns, duration_classes, target_catalog, group_ids, decode_group,
)
from trading_research.research.ohlc_ranges import MinuteBars
from trading_research.research.jumbo_tables import path_row

M = 60_000_000_000
BOUNDARY = boundary_ns("2023-01-01")


def matrix(n=1, **overrides):
    fields={
      "date":np.full(n,date(2022,12,31).toordinal(),dtype=np.int64),
      "path":np.zeros(n,dtype=np.int8),"inclusive_path":np.zeros(n,dtype=np.int8),
      "root":np.zeros(n,dtype=np.int16),"clock":np.zeros(n,dtype=np.int16),"horizon":np.zeros(n,dtype=np.int16),
      "maturity_at_ns":np.full(n,BOUNDARY-1,dtype=np.int64),
      "prefix_maturity_at_ns":np.full(n,BOUNDARY-2,dtype=np.int64),
      "formation_width_ticks":np.full(n,20,dtype=np.int64),
      "planned_minutes":np.full(n,100,dtype=np.int64),
      "observed_prefix_minutes":np.full(n,100,dtype=np.int64),
      "future_high_from_known_W":np.full(n,.6),"future_low_from_known_W":np.full(n,-.4),
      "terminal_from_known_W":np.full(n,.55),"quadratic_variation_W2":np.full(n,.0125),
      "reclaim_observed":np.zeros(n,dtype=np.int8),
      "prefix_first_lower_minutes":np.full(n,np.nan),"prefix_first_upper_minutes":np.full(n,np.nan),
      "second_lower_minutes":np.full(n,np.nan),"second_upper_minutes":np.full(n,np.nan),
    }
    for key,value in overrides.items():
        fields[key]=np.asarray(value,dtype=fields[key].dtype)
    return PreparedPaths({"id":"independent-literal-target-matrix"},np.zeros((n,1)),fields,
       {"root":("ES","NQ"),"clock":("A","B"),"horizon":("15m","30m")},())


def duration(lo,hi,seen,total=100):
    return duration_classes(np.asarray(lo,dtype=float),np.asarray(hi,dtype=float),
      np.asarray(seen,dtype=np.int64),np.full(len(lo),total,dtype=np.int64))


class JumboTargetTests(unittest.TestCase):
    def test_source_clock_population_preserves_missing_labels_without_other_clocks(self):
        from trading_research.research.jumbo_models import intended_universes
        m = matrix(4, clock=[0, 1, 0, 1], path=[0, 0, 6, 0])
        target = target_catalog(m)["path"]
        target.metadata["applicable_clocks"] = ["A"]
        self.assertEqual(target.applicable(m).tolist(), [True, False, True, False])
        self.assertEqual(target.phase(m, "fit").tolist(), [True, False, False, False])
        self.assertEqual(set(intended_universes(m, "fit", target=target)), {0})
        target.eligible[:] = False
        self.assertEqual(target.applicable(m).tolist(), [True, False, True, False])
        self.assertEqual(len(intended_universes(m, "fit", target=target)[0]), 1)

    def test_duration_literal_cells_and_shared_edge(self):
        a=duration([1,5,6,99],[2,5,9,100],[100]*4)
        self.assertEqual(np.flatnonzero(a[0]).tolist(),[0])
        self.assertEqual(np.flatnonzero(a[1]).tolist(),[0,1])
        self.assertEqual(np.flatnonzero(a[2]).tolist(),[1])
        self.assertEqual(np.flatnonzero(a[3]).tolist(),[5])
        self.assertFalse(a[:,-1].any())

    def test_duration_interval_spans_all_compatible_cells(self):
        a=duration([4],[26],[100])
        self.assertEqual(np.flatnonzero(a[0]).tolist(),[0,1,2,3])

    def test_right_censor_grid_edge_and_complete_no_event(self):
        a=duration([np.nan]*3,[np.nan]*3,[0,25,100])
        self.assertTrue(a[0].all())
        self.assertEqual(np.flatnonzero(a[1]).tolist(),[3,4,5,6])
        self.assertEqual(np.flatnonzero(a[2]).tolist(),[6])

    def test_duration_uses_declared_total_not_observed_prefix(self):
        a=duration([4],[5],[10],total=100)
        self.assertEqual(np.flatnonzero(a[0]).tolist(),[0,1])

    def test_duration_rejects_infinite_partial_or_impossible_events(self):
        for lo,hi,seen in ((np.inf,np.inf,10),(-np.inf,-np.inf,10),(1,np.nan,10),(-1,1,10),(2,1,10),(1,11,10)):
            with self.subTest(lo=lo,hi=hi),self.assertRaises(ContractError):
                duration([lo],[hi],[seen])
        with self.assertRaises(ContractError):
            duration_classes([np.nan],[np.nan],np.array([1.]),np.array([100],dtype=np.int64))

    def test_all_six_observation_path_classes_retained(self):
        m=matrix(8,path=range(8),inclusive_path=range(8))
        c=target_catalog(m)
        self.assertEqual(c["path"].metadata["classes"],list(PATH_CLASSES))
        self.assertEqual(c["path"].eligible.tolist(),[True]*6+[False,False])
        self.assertEqual(c["path"].values.tolist(),list(range(8)))
        self.assertEqual(c["inclusive_path"].eligible.tolist(),[True]*6+[False,False])

    def test_inclusive_category_has_own_validity(self):
        c=target_catalog(matrix(2,path=[0,0],inclusive_path=[6,-1]))
        self.assertFalse(c["inclusive_path"].eligible.any())

    def test_signed_known_anchor_labels_and_positive_atoms(self):
        c=target_catalog(matrix())
        self.assertEqual(c["future_low_from_known_W"].values.tolist(),[-.4])
        self.assertEqual(c["positive_low_excursion_from_known_W"].values.tolist(),[0.])
        self.assertEqual(c["future_high_from_known_W"].values.tolist(),[.6])
        self.assertEqual(c["terminal_from_known_W"].values.tolist(),[.55])
        self.assertTrue(c["quadratic_variation_W2"].metadata["nonnegative"])
        self.assertEqual(c["quadratic_variation_W2"].values.tolist(),[.0125])

    def test_ambiguous_reclaim_retains_both_classes(self):
        c=target_catalog(matrix(3,path=[0,1,5],reclaim_observed=[0,1,-1]))["reclaim"]
        self.assertEqual(c.kind,"interval_categorical")
        self.assertEqual(c.eligible.tolist(),[True,True,True])
        self.assertEqual(c.values.tolist(),[[True,False],[False,True],[True,True]])

    def test_full_label_requires_strict_phase_maturity(self):
        m=matrix(3,maturity_at_ns=[BOUNDARY-1,BOUNDARY,BOUNDARY+1],
                 prefix_maturity_at_ns=[BOUNDARY-100]*3)
        c=target_catalog(m)
        for name in ("path","inclusive_path","future_high_from_known_W","quadratic_variation_W2","reclaim"):
            self.assertEqual(c[name].phase(m,"fit").tolist(),[True,False,False])

    def test_incomplete_second_hit_censor_stops_before_first(self):
        m=matrix(path=[6],observed_prefix_minutes=[80],maturity_at_ns=[-1],
          prefix_first_lower_minutes=[20],prefix_first_upper_minutes=[21])
        c=target_catalog(m)
        self.assertTrue(c["second_duration"].eligible[0])
        # A second hit in (20,25] remains possible despite an 80-minute prefix;
        # absent second-state storage cannot assert censoring through minute 80.
        self.assertEqual(np.flatnonzero(c["second_duration"].values[0]).tolist(),[2,3,4,5,6])
        self.assertEqual(np.flatnonzero(c["first_duration"].values[0]).tolist(),[2])
        self.assertEqual(int(c["second_duration"].label_known_at_ns[0]),BOUNDARY-2)
        self.assertTrue(c["second_duration"].phase(m,"fit")[0])

    def test_first_bar_breach_gives_no_informative_second_censor(self):
        c=target_catalog(matrix(path=[6],observed_prefix_minutes=[80],maturity_at_ns=[-1],
            prefix_first_lower_minutes=[0],prefix_first_upper_minutes=[1]))
        self.assertFalse(c["second_duration"].eligible[0])
        self.assertTrue(c["second_duration"].values[0].all())

    def test_no_first_breach_prefix_supports_second_censor(self):
        c=target_catalog(matrix(path=[6],observed_prefix_minutes=[50],maturity_at_ns=[-1]))
        self.assertEqual(np.flatnonzero(c["second_duration"].values[0]).tolist(),[4,5,6])
        self.assertFalse(c["path"].eligible[0])

    def test_complete_second_event_uses_retained_interval(self):
        c=target_catalog(matrix(path=[3],second_lower_minutes=[74],second_upper_minutes=[76]))
        self.assertEqual(np.flatnonzero(c["second_duration"].values[0]).tolist(),[4,5])

    def test_zero_prefix_and_zero_width_not_duration_training(self):
        c=target_catalog(matrix(2,observed_prefix_minutes=[0,100],formation_width_ticks=[20,0]))
        self.assertFalse(c["first_duration"].eligible.any())
        self.assertFalse(c["second_duration"].eligible.any())

    def test_group_encoding_excludes_dates_and_labels(self):
        m=matrix(3,root=[0,1,1],clock=[0,0,1],horizon=[0,1,1])
        self.assertEqual(group_ids(m).tolist(),[0,5,7])
        self.assertEqual(decode_group(m,5),{"root":"NQ","clock":"A","horizon":"30m"})
        with self.assertRaises(ContractError):decode_group(m,-1)
        with self.assertRaises(ContractError):decode_group(m,8)

    def test_actual_path_qv_includes_first_open_close_then_close_returns(self):
        # Formation [90,110]; future first open 100 -> close 103 (9),
        # next open 120 is not an extra return; next close 107 adds 16.
        rows=[(100,110,90,100),(100,104,99,103),(120,121,106,107)]
        columns=dict(start_ns=[0,M,2*M],end_ns=[M,2*M,3*M],known_at_ns=[M,2*M,3*M],
                     volume=[1]*3,contract_key=["RAW"]*3,valid=[True]*3)
        for j,key in enumerate(("open_ticks","high_ticks","low_ticks","close_ticks")):
            columns[key]=[r[j] for r in rows]
        bars=MinuteBars(columns,source_version="qv-literal")
        formation=bars.window(0,M)
        row=dict(date="2022-01-03",year=2022,clock="literal",formation_id="literal",exclusion_reasons="",
                 contract_key="RAW",zero_width=False,available_at_ns=M,low_ticks=90,high_ticks=110,width_ticks=20)
        result=path_row((row,formation),origin=M,endpoint=3*M,horizon="literal2m",features={},available_cut=3*M,root="NQ")
        self.assertEqual(result["squared_close_returns_ticks2"],25)
        self.assertNotEqual(result["squared_close_returns_ticks2"],16)
        self.assertNotEqual(result["squared_close_returns_ticks2"],9+(107-120)**2)

if __name__ == "__main__":
    unittest.main()
