"""Independent adapter/anchor fixtures. Authored only; registered execution required.

Anchor source: jumbo-location-anchor-probability-cases-v1.json,
SHA183293c2e8d6d0256580902ded54c22dccbf76d986c4789b078803f3c817b8ce.
No market observations or actual model quality are asserted by these fixtures.
"""
from datetime import date
import unittest
from unittest.mock import patch
import numpy as np
import pyarrow as pa
from trading_research.errors import ContractError, IntegrityError
from trading_research.research.jumbo_tables import FEATURES, VERSION, table_schema
from trading_research.research.ohlc_ranges import MinuteBars
from trading_research.research.jumbo_anchors import build_anchor_supplement
from trading_research.research.jumbo_matrix import (
    PreparedPaths, exact_known_anchor, _ints, prepare_paths,
    fit_feature_transform, transformed_features,
)

M=60_000_000_000
ORIGIN=1672488000000000000


def fixture_tables(*, low=90,width=20,position=.5,path_updates=None,formation_updates=None):
    row={"date":"2022-12-31","year":2022,"clock":"fixture_clock","horizon":"after_15m","root":"NQ",
         "path":"no_break","inclusive_path":"no_break","prefix_first_side":"neither",
         "formation_id":"literal-parent","row_id":"literal-source-row","contract_key":"RAW","label_version":VERSION,
         "origin_ns":ORIGIN,"endpoint_ns":ORIGIN+15*M,"planned_minutes":15,
         "maturity_at_ns":ORIGIN+16*M,"prefix_maturity_at_ns":ORIGIN+16*M,
         "observed_prefix_minutes":15,"label_origin_open_ticks":110,
         "maximum_up_ticks":2,"maximum_down_ticks":2,"terminal_ticks":1,
         "squared_close_returns_ticks2":4,"maximum_up_W":.1,"maximum_down_W":.1,
         "terminal_W":.05,"remaining_range_W":.2,"upper_overshoot_W":.1,"lower_overshoot_W":.1,
         "prefix_both_breach":False,"reclaim_observed":False}
    row.update({"x_"+name:0. for name in FEATURES})
    row.update(x_width_ticks=float(width),x_formation_minutes=15.,x_last_close_position=position,x_last_close_age_minutes=1.)
    row.update(path_updates or {})
    form={"formation_id":"literal-parent","clock":"fixture_clock","contract_key":"RAW","source_version":"literal-direct-canonical","low_ticks":low,"width_ticks":width,"high_ticks":low+width,
          "open_ticks":low,"close_ticks":low+width//2,"root":"NQ","year":2022,"date":"2022-12-31",
          "status":"complete","formation_start_ns":ORIGIN-16*M,"formation_end_ns":ORIGIN-M,"available_at_ns":ORIGIN}
    form.update(formation_updates or {})
    return (pa.Table.from_pylist([row],schema=table_schema("paths")),
            pa.Table.from_pylist([form],schema=table_schema("formations")))


def prepared(*, duplicate=False,anchor_ticks=None,**kwargs):
    path,formation=fixture_tables(**kwargs)
    pathref={"kind":"literal_paths","rows":1,"sha256":"1"*64,"size_bytes":1,"schema_sha256":"2"*64}
    formref={"kind":"literal_formations","rows":1,"sha256":"3"*64,"size_bytes":1,"schema_sha256":"4"*64}
    shard={"root":"NQ","year":2022,"tables":{"paths":pathref,"formations":formref}}
    plan={"expected_formation_clock_ids":["fixture_clock"],"horizons_minutes":[15],"prefix_delays_minutes":[]}
    if anchor_ticks is None:
        anchor_ticks=kwargs.get("low",90)+kwargs.get("width",20)//2
    series=MinuteBars(dict(start_ns=[ORIGIN-2*M],end_ns=[ORIGIN-M],known_at_ns=[ORIGIN],
        open_ticks=[anchor_ticks],high_ticks=[anchor_ticks],low_ticks=[anchor_ticks],close_ticks=[anchor_ticks],
        volume=[1],contract_key=["RAW"],valid=[True]),source_version="literal-direct-canonical")
    supplement=build_anchor_supplement(series,formation,path,root="NQ",year=2022,path_ref=pathref,
        formation_ref=formref,relationship_clocks=("OR5","OR15","JTR_fixed_04","futures08","NY08"),frozen_analysis_id="original-d5f-fixture")
    anchorref={"kind":"literal_anchors","rows":1,"sha256":"5"*64,"size_bytes":1,"schema_sha256":supplement["manifest"]["schema_sha256"]}
    def read(_store,ref,columns):
        tables={"literal_paths":path,"literal_formations":formation,"literal_anchors":supplement["table"]}
        return tables[ref["kind"]].select(columns)
    with patch("trading_research.research.jumbo_matrix._read_columns",side_effect=read):
        return prepare_paths(None,[shard,shard] if duplicate else [shard],plan=plan,phase="independent_fixture",
             anchor_supplements={("NQ",2022):{"table_ref":anchorref,"manifest":supplement["manifest"]}})



class JumboMatrixIndependentTests(unittest.TestCase):
    def test_active_pipeline_never_inverts_normalized_price(self):
        with patch("trading_research.research.jumbo_matrix.exact_known_anchor",side_effect=AssertionError("reference inverse called")):
            matrix=prepared()
        self.assertEqual(int(matrix.fields["anchor_ticks"][0]),100)
        self.assertEqual(int(matrix.fields["anchor_start_ns"][0]),ORIGIN-2*M)
        self.assertEqual(int(matrix.fields["anchor_known_at_ns"][0]),ORIGIN)
        self.assertEqual(matrix.manifest["frozen_source_analysis_id"],"original-d5f-fixture")
        self.assertNotIn("opening_width_ratio",matrix.manifest["feature_groups"]["full"])
        self.assertIn("opening_width_ratio",matrix.manifest["feature_groups"]["legacy_references"])
        self.assertIn("anchor_OR5_width_ratio",matrix.manifest["feature_groups"]["named_anchor_OR5"])

    def test_direct_price_reconciliation_cannot_invent_anchor_from_ratio(self):
        with self.assertRaises(IntegrityError):prepared(position=.123)

    def test_explicit_supplement_required(self):
        with self.assertRaises((ContractError,IntegrityError)):
            prepare_paths(None,[{"root":"NQ","year":2022}],plan={},phase="fixture",anchor_supplements={})

    def test_large_absolute_price_keeps_exact_anchor(self):
        base=2**53+1
        anchor,valid=exact_known_anchor(np.array([base],dtype=np.int64),np.array([20],dtype=np.int64),np.array([.5]))
        self.assertTrue(valid[0])
        self.assertEqual(int(anchor[0]),base+10)

    def test_fractional_offset_roundtrip(self):
        anchor,valid=exact_known_anchor(np.array([100,-10],dtype=np.int64),np.array([3,3],dtype=np.int64),np.array([1/3,2/3]))
        self.assertEqual(valid.tolist(),[True,True])
        self.assertEqual(anchor.tolist(),[101,-8])

    def test_position_impossible_for_any_integer_price_rejected(self):
        anchor,valid=exact_known_anchor(np.array([100],dtype=np.int64),np.array([10],dtype=np.int64),np.array([.123]))
        self.assertFalse(valid[0])

    def test_precision_unidentifiable_requires_raw_lookup(self):
        _,valid=exact_known_anchor(np.array([0],dtype=np.int64),np.array([2**54],dtype=np.int64),np.array([1.]))
        self.assertFalse(valid[0])

    def test_unavailable_zero_width_nonfinite_and_overflow(self):
        low=np.array([10,10,10,np.iinfo(np.int64).max],dtype=np.int64)
        width=np.array([0,10,10,10],dtype=np.int64)
        _,valid=exact_known_anchor(low,width,np.array([.5,np.nan,np.inf,1.]))
        self.assertEqual(valid.tolist(),[False,False,False,False])

    def test_lossy_range_coordinates_rejected(self):
        with self.assertRaises(ContractError):
            exact_known_anchor(np.array([100.]),np.array([20],dtype=np.int64),np.array([.5]))

    def test_exact_null_and_large_timestamps(self):
        values=_ints(pa.chunked_array([[None,2**53+1],[2**53+3]],type=pa.int64()))
        self.assertEqual(values.dtype,np.dtype(np.int64))
        self.assertEqual(values.tolist(),[-1,2**53+1,2**53+3])
        with self.assertRaises(IntegrityError):
            _ints(pa.chunked_array([[1.,None]],type=pa.float64()))

    def test_signed_known_anchor_targets_not_future_open_targets(self):
        matrix=prepared()
        self.assertEqual(int(matrix.fields["anchor_ticks"][0]),100)
        self.assertAlmostEqual(matrix.fields["future_high_from_known_W"][0],.6)
        self.assertAlmostEqual(matrix.fields["future_low_from_known_W"][0],-.4)
        self.assertAlmostEqual(matrix.fields["terminal_from_known_W"][0],.55)
        self.assertAlmostEqual(matrix.fields["maximum_up_W"][0],.1)
        self.assertNotEqual(matrix.fields["future_high_from_known_W"][0],matrix.fields["maximum_up_W"][0])

    def test_large_anchor_and_label_reconstruct_without_absolute_float_loss(self):
        base=2**53+1
        matrix=prepared(low=base,width=20,position=.5,path_updates={"label_origin_open_ticks":base+20,"maximum_up_ticks":2,"maximum_down_ticks":2,"terminal_ticks":1})
        self.assertEqual(int(matrix.fields["anchor_ticks"][0]),base+10)
        self.assertAlmostEqual(matrix.fields["future_high_from_known_W"][0],.6)
        self.assertAlmostEqual(matrix.fields["future_low_from_known_W"][0],-.4)
        self.assertAlmostEqual(matrix.fields["terminal_from_known_W"][0],.55)

    def test_negative_tick_minus_one_not_null(self):
        matrix=prepared(low=-11,width=20,position=.5,path_updates={"label_origin_open_ticks":-1,"maximum_up_ticks":2,"maximum_down_ticks":2,"terminal_ticks":-1})
        self.assertEqual(int(matrix.fields["anchor_ticks"][0]),-1)
        self.assertAlmostEqual(matrix.fields["future_high_from_known_W"][0],.1)
        self.assertAlmostEqual(matrix.fields["terminal_from_known_W"][0],-.05)

    def test_observed_null_tick_or_geometry_rejected(self):
        for column in ("label_origin_open_ticks","maximum_up_ticks","maximum_down_ticks","terminal_ticks","squared_close_returns_ticks2"):
            with self.subTest(column=column), self.assertRaises((ContractError,IntegrityError)):
                prepared(path_updates={column:None})
        with self.assertRaises((ContractError,IntegrityError)):
            prepared(formation_updates={"low_ticks":None})

    def test_null_maturity_cannot_pass_training_boundary(self):
        matrix=prepared(path_updates={"path":"censored","inclusive_path":"censored","maturity_at_ns":None})
        self.assertEqual(int(matrix.fields["maturity_at_ns"][0]),-1)
        self.assertFalse(matrix.phase("2022-01-01","2022-12-31",maturity_before=ORIGIN+100*M)[0])

    def test_signed_target_overflow_cannot_wrap(self):
        with self.assertRaises((ContractError,IntegrityError)):
            prepared(low=-(2**62),width=20,position=0.,anchor_ticks=-(2**62),path_updates={"label_origin_open_ticks":2**62,"maximum_up_ticks":1,"maximum_down_ticks":1,"terminal_ticks":0})

    def test_future_inputs_excluded_from_model_features(self):
        original=prepared()
        changed=prepared(path_updates={"label_origin_open_ticks":300,"maximum_up_ticks":200,"maximum_down_ticks":100,"terminal_ticks":150,
                                       "maturity_at_ns":ORIGIN+30*M,"prefix_maturity_at_ns":ORIGIN+30*M,"prefix_both_breach":True,
                                       "reclaim_observed":True,"path":"high_then_low","inclusive_path":"high_then_low"})
        np.testing.assert_equal(original.features,changed.features)
        mask=np.array([True])
        transform=fit_feature_transform(original,mask,group="full")
        np.testing.assert_equal(transformed_features(original,transform),transformed_features(changed,transform))
        self.assertEqual(original.manifest["feature_sha256"],changed.manifest["feature_sha256"])
        self.assertNotEqual(original.manifest["id"],changed.manifest["id"])

    def test_float32_feature_overflow_not_silent_missingness(self):
        with self.assertRaises((ContractError,IntegrityError)):
            prepared(path_updates={"x_log_volume":1e300})

    def test_phase_maturity_strict_and_exact_above_2pow53(self):
        ordinal=date(2022,12,31).toordinal()
        matrix=PreparedPaths({},np.zeros((4,1)),{"date":np.array([ordinal]*4,dtype=np.int64),
            "maturity_at_ns":np.array([2**53,2**53+1,2**53+2,-1],dtype=np.int64)}, {},())
        self.assertEqual(matrix.phase("2022-12-31","2022-12-31",maturity_before=2**53+1).tolist(),[True,False,False,False])
        self.assertFalse(matrix.phase("2023-01-01","2023-12-31").any())
        with self.assertRaises((ContractError,IntegrityError)):
            matrix.phase("2022-12-31","2022-12-31",maturity_before=2**53+1,label_known=np.array([float(2**53)]*4))
        with self.assertRaises((ContractError,IntegrityError)):
            matrix.phase("2022-12-31","2022-12-31",maturity_before=2**53+1,label_known=np.array([2**53],dtype=np.int64))

    def test_duplicate_source_shard_rejected(self):
        with self.assertRaises((ContractError,IntegrityError)):
            prepared(duplicate=True)

    def test_iso_date_and_declared_shard_year_must_agree(self):
        with self.assertRaises((ContractError,IntegrityError)):
            prepared(path_updates={"date":"2023-01-01"})

    def test_row_identity_and_phase_weights(self):
        matrix=prepared()
        self.assertEqual(matrix.manifest["source_shards"][0]["start"],0)
        self.assertEqual(matrix.manifest["source_shards"][0]["rows"],1)
        self.assertEqual(matrix.size,1)
        self.assertEqual(matrix.equal_date_weights(np.array([True])).tolist(),[1.])

    def test_transforms_train_only_and_available_feature_missingness(self):
        fields={"date":np.array([1,2],dtype=np.int64),"planned_minutes":np.array([15,15],dtype=np.int64),"root":np.array([0,0],dtype=np.int16)}
        features=np.zeros((2,len(FEATURES)),dtype=np.float32)
        index=FEATURES.index("width_ticks")
        features[:,index]=[10,1_000_000]
        matrix=PreparedPaths({"id":"literal"},features,fields,{},())
        transform=fit_feature_transform(matrix,np.array([True,False]),group="controls")
        self.assertEqual(transform["means"][transform["names"].index("width_ticks")],10)
        self.assertEqual(transform["training_rows"],1)
        self.assertEqual(transform["training_last_date"],1)

    def test_root_indicator_decodes_reversed_category_order(self):
        fields = {"date":np.array([1,2],dtype=np.int64),
                  "planned_minutes":np.array([15,15],dtype=np.int64),
                  "root":np.array([0,1],dtype=np.int16)}
        matrix = PreparedPaths({"id":"literal-roots","feature_columns":["x_width_ticks"]},
                               np.array([[10.],[10.]]),fields,{"root":("ES","NQ")},())
        transform = {"names":["width_ticks"],"means":[10.],"scales":[1.]}
        self.assertEqual(transformed_features(matrix,transform)[:,-1].tolist(),[1.,0.])
        matrix.categories["root"] = ("NQ","ES")
        self.assertEqual(transformed_features(matrix,transform)[:,-1].tolist(),[0.,1.])
