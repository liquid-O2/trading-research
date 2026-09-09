"""Independent common-clock causal adapter fixtures; no execution performed."""
import copy
import unittest
import numpy as np
from trading_research.errors import ContractError, IntegrityError
from trading_research.research.jumbo_matrix import PreparedPaths
from trading_research.research.jumbo_tables import FEATURES
from trading_research.research.jumbo_clock_comparison import (
    COMMON_FEATURES, COMMON_TARGETS, HORIZON, prepare_common_clock_comparison,
)

PLAN={"matched_clock_comparison":{"clocks":["A","B","C"],"origin_local":"10:01"}}
FI={name:i for i,name in enumerate(FEATURES)}


def fixture():
    x=np.full((3,len(FEATURES)),np.nan,dtype=np.float32)
    common=dict(last_close_age_minutes=1,weekday=1,month=6,cut_ny_minutes=601,early_close=0,
      prior_width_ticks=100,prior_age_minutes=1000,prior_5_mean_width_ticks=120,
      prior_20_mean_width_ticks=130,last_close_in_prior_position=.5,
      prior_last_close_displacement_ticks=5,observed_cash_open_gap_ticks=4)
    for i in (0,2):
        for name,value in common.items():x[i,FI[name]]=value
        for name,value in dict(width_ticks=10+5*i,formation_minutes=15,log_volume=5,
                               open_position=.4,close_position=.6,last_close_position=.7,
                               asia_width_ratio=2,opening_price_overlap_fraction=.5).items():
            x[i,FI[name]]=value
    for name,value in dict(weekday=1,month=6,cut_ny_minutes=601,early_close=0).items():x[1,FI[name]]=value
    fields={"root":np.array([0,0,0],dtype=np.int16),"date":np.array([738300]*3,dtype=np.int64),
      "clock":np.array([0,1,2],dtype=np.int16),"horizon":np.array([1,1,1],dtype=np.int16),
      "path":np.array([0,6,6],dtype=np.int8),"anchor_identified":np.array([True,False,True]),
      "origin_ns":np.array([1000]*3,dtype=np.int64),"endpoint_ns":np.array([2000]*3,dtype=np.int64),
      "maturity_at_ns":np.array([2001,-1,-1],dtype=np.int64),
      "prior_width_ticks":np.array([100,-1,100],dtype=np.int64),
      "anchor_ticks":np.array([1000,0,1000],dtype=np.int64),
      "future_high_ticks":np.array([1010,0,0],dtype=np.int64),
      "future_low_ticks":np.array([980,0,0],dtype=np.int64),
      "future_close_ticks":np.array([1005,0,0],dtype=np.int64)}
    return PreparedPaths({"id":"literal-original"},x,fields,
       {"root":("NQ",),"clock":("A","B","C"),"horizon":("after_15m",HORIZON)},())


def prepare(m=None):
    return prepare_common_clock_comparison(fixture() if m is None else m,plan=PLAN)


def complete_c(m):
    m.fields["path"][2]=0
    for name in ("future_high_ticks","future_low_ticks","future_close_ticks","maturity_at_ns"):
        m.fields[name][2]=m.fields[name][0]
    return m


class CommonClockComparisonTests(unittest.TestCase):
    def test_all_clocks_share_prior_scaled_receiver_and_row_identity(self):
        out=prepare()
        self.assertEqual(out.size,3)
        np.testing.assert_array_equal(out.fields["original_prepared_row"],[0,1,2])
        for name,expected in zip(COMMON_TARGETS,(.1,.2,.05),strict=True):
            np.testing.assert_allclose(out.fields[name],[expected]*3,atol=0,rtol=0)
            self.assertEqual(out.fields[name].dtype,np.dtype(np.float64))
        np.testing.assert_array_equal(out.fields["common_target_eligible"],[True]*3)
        np.testing.assert_array_equal(out.fields["common_maturity_at_ns"],[2001]*3)
        np.testing.assert_array_equal(out.fields["path"],[0,6,6])

    def test_missing_clock_gets_common_controls_and_missing_own_features(self):
        out=prepare()
        for name in COMMON_FEATURES:
            np.testing.assert_equal(out.features[:,FI[name]],np.repeat(out.features[0,FI[name]],3))
        for name in FEATURES:
            if name not in COMMON_FEATURES:self.assertTrue(np.isnan(out.features[1,FI[name]]))
        np.testing.assert_array_equal(out.fields["common_own_features_available"],[True,False,True])
        self.assertEqual(float(out.features[0,FI["width_ticks"]]),10.)
        self.assertEqual(float(out.features[2,FI["width_ticks"]]),20.)

    def test_future_completion_cannot_change_features_or_own_masks(self):
        original=prepare()
        m=complete_c(fixture())
        m.fields["path"][0]=6
        m.fields["maturity_at_ns"][0]=-1
        m.fields["future_high_ticks"][0]=9999
        changed=prepare(m)
        np.testing.assert_equal(original.features,changed.features)
        np.testing.assert_array_equal(original.fields["common_own_features_available"],changed.fields["common_own_features_available"])
        self.assertEqual(int(changed.fields["common_known_reference_row"][0]),0)
        self.assertEqual(int(changed.fields["common_future_reference_row"][0]),2)
        for name in COMMON_TARGETS:np.testing.assert_equal(original.fields[name],changed.fields[name])

    def test_all_future_censored_still_recovers_known_controls(self):
        original=prepare()
        m=fixture();m.fields["path"][:]=6;m.fields["maturity_at_ns"][:]=-1
        changed=prepare(m)
        np.testing.assert_equal(original.features,changed.features)
        self.assertTrue(changed.fields["common_known_dependency_available"].all())
        self.assertFalse(changed.fields["common_target_eligible"].any())
        for name in COMMON_TARGETS:self.assertTrue(np.isnan(changed.fields[name]).all())
        self.assertTrue((changed.fields["common_maturity_at_ns"]==-1).all())

    def test_old_anchor_after_source_roll_cannot_supply_own_features(self):
        m=complete_c(fixture())
        m.features[2,FI["last_close_age_minutes"]]=20
        m.fields["anchor_ticks"][2]=900
        m.fields["prior_width_ticks"][2]=-1
        # Its observed receiver can differ in an old raw coordinate; not a legal reference.
        m.fields["future_high_ticks"][2]=5000
        out=prepare(m)
        self.assertFalse(out.fields["common_own_features_available"][2])
        self.assertTrue(np.isnan(out.features[2,FI["width_ticks"]]))
        self.assertTrue(np.isnan(out.features[2,FI["asia_width_ratio"]]))
        self.assertEqual(float(out.features[2,FI["last_close_age_minutes"]]),1.)
        self.assertEqual(float(out.fields["common_high_priorW"][2]),.1)

    def test_known_anchor_and_prior_agreement_checked_without_future(self):
        for name,value in (("anchor_ticks",1001),("prior_width_ticks",101)):
            m=fixture();m.fields["path"][:]=6;m.fields[name][2]=value
            with self.subTest(name=name),self.assertRaises(IntegrityError):prepare(m)

    def test_complete_receiver_exact_agreement_and_maturity(self):
        for name in ("future_high_ticks","future_low_ticks","future_close_ticks","maturity_at_ns"):
            m=complete_c(fixture());m.fields[name][2]+=1
            with self.subTest(name=name),self.assertRaises(IntegrityError):prepare(m)
        for name in ("origin_ns","endpoint_ns"):
            m=fixture();m.fields[name][1]+=1
            with self.subTest(name=name),self.assertRaises(IntegrityError):prepare(m)

    def test_available_common_controls_must_agree(self):
        m=fixture();m.features[2,FI["prior_5_mean_width_ticks"]]=121
        with self.assertRaises(IntegrityError):prepare(m)

    def test_missing_optional_common_scale_can_use_other_known_reference(self):
        m=fixture();m.features[0,FI["prior_5_mean_width_ticks"]]=np.nan
        out=prepare(m)
        np.testing.assert_equal(out.features[:,FI["prior_5_mean_width_ticks"]],[120]*3)

    def test_missing_prior_retains_rows_and_unavailable_dependency(self):
        m=fixture();m.fields["prior_width_ticks"][:]=-1
        out=prepare(m)
        self.assertEqual(out.size,3)
        self.assertFalse(out.fields["common_known_dependency_available"].any())
        self.assertFalse(out.fields["common_target_eligible"].any())
        self.assertTrue((out.fields["common_prior_width_ticks"]==-1).all())
        self.assertTrue(np.isnan(out.fields["common_high_priorW"]).all())

    def test_exact_large_prices_subtract_before_float_conversion(self):
        m=fixture();base=2**53+1
        m.fields["anchor_ticks"][[0,2]]=base
        m.fields["future_high_ticks"][0]=base+1
        m.fields["future_low_ticks"][0]=base-3
        m.fields["future_close_ticks"][0]=base+2
        # Keep close within high: use a higher high by one tick.
        m.fields["future_high_ticks"][0]=base+3
        out=prepare(m)
        np.testing.assert_allclose(out.fields["common_high_priorW"],[.03]*3,atol=0,rtol=0)
        np.testing.assert_allclose(out.fields["common_terminal_priorW"],[.02]*3,atol=0,rtol=0)
        np.testing.assert_array_equal(out.fields["common_anchor_ticks"],[base]*3)

    def test_physically_absent_or_duplicate_clock_rejected(self):
        m=fixture();m.features=m.features[:2];m.fields={k:v[:2] for k,v in m.fields.items()}
        with self.assertRaises(IntegrityError):prepare(m)
        m=fixture();m.fields["clock"][2]=1
        with self.assertRaises(IntegrityError):prepare(m)

    def test_population_not_selected_by_common_future_success(self):
        m=fixture()
        # A second intended date visible only in another horizon must not silently vanish.
        m.features=np.concatenate((m.features,m.features[:1]),axis=0)
        m.fields={k:np.concatenate((v,v[:1])) for k,v in m.fields.items()}
        m.fields["date"][-1]+=1;m.fields["horizon"][-1]=0
        with self.assertRaises(IntegrityError):prepare(m)

    def test_original_matrix_is_not_mutated(self):
        m=fixture();before=copy.deepcopy(m)
        out=prepare(m)
        np.testing.assert_equal(m.features,before.features)
        for name in m.fields:np.testing.assert_equal(m.fields[name],before.fields[name])
        out.features[0,0]=999
        self.assertEqual(float(m.features[0,0]),10.)

    def test_lossy_raw_ticks_and_unknown_declared_clock_rejected(self):
        m=fixture();m.fields["future_high_ticks"]=m.fields["future_high_ticks"].astype(float)
        with self.assertRaises(ContractError):prepare(m)
        with self.assertRaises(IntegrityError):
            prepare_common_clock_comparison(fixture(),plan={"matched_clock_comparison":{"clocks":["D"]}})

    def test_invalid_receiver_maturity_rejected(self):
        m=fixture();m.fields["maturity_at_ns"][0]=1999
        with self.assertRaises(IntegrityError):prepare(m)
        m=fixture();m.fields["future_close_ticks"][0]=1011
        with self.assertRaises(IntegrityError):prepare(m)

if __name__ == "__main__":
    unittest.main()
