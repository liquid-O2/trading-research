"""Independent model orchestration fixtures; numerical optimizers are mocked.

Authored without importing/running candidate code. Backend calls follow the
currently reviewed signatures; registered checks own all execution.
"""
from datetime import date
from types import SimpleNamespace
import copy
import unittest
from unittest.mock import patch
import numpy as np
import pyarrow as pa
from trading_research.errors import ContractError, IntegrityError
from trading_research.research import jumbo_models as models
from trading_research.research.jumbo_matrix import (
    PreparedPaths, FEATURES, FLOAT_LABELS, INTEGER_LABELS, prepare_paths,
    feature_names, fit_feature_transform, transformed_features,
)
from trading_research.research.jumbo_tables import table_schema, VERSION as TABLE_VERSION
from trading_research.research.jumbo_targets import Target, boundary_ns
from trading_research.research.jumbo_anchors import build_anchor_supplement
from trading_research.research.ohlc_ranges import MinuteBars


def fixture():
    days=("2022-12-30","2022-12-31","2023-03-01","2023-12-31","2024-02-01",
          "2024-06-30","2024-08-01","2024-12-31","2025-01-02")
    known=("2022-12-31","2023-01-01","2023-03-02","2024-01-01","2024-02-02",
           "2024-07-01","2024-08-02","2025-01-01","2025-01-03")
    f={"date":np.asarray([date.fromisoformat(d).toordinal() for d in days],dtype=np.int64),
       "maturity_at_ns":np.asarray([boundary_ns(d) for d in known],dtype=np.int64),
       "root":np.zeros(9,dtype=np.int16),"clock":np.zeros(9,dtype=np.int16),
       "horizon":np.zeros(9,dtype=np.int16),"planned_minutes":np.full(9,15,dtype=np.int64),
       "future_high_ticks":np.arange(9,dtype=np.int64)+100,
       "future_low_ticks":np.arange(9,dtype=np.int64)+90,
       "future_close_ticks":np.arange(9,dtype=np.int64)+95}
    manifest={"id":"independent-matrix","feature_columns":["x_causal_a","x_causal_b"],
              "feature_groups":{"controls":["causal_a"],"own":["causal_a","causal_b"],"full":["causal_a","causal_b"]}}
    x=np.column_stack((np.arange(9),np.arange(9)*2)).astype(np.float32)
    return PreparedPaths(manifest,x,f,{"root":("NQ","ES"),"clock":("A",),"horizon":("15m",)},())


def target(m, name="path", kind="categorical", values=None):
    if values is None:values=np.arange(m.size,dtype=np.int64)%2 if kind=="categorical" else np.arange(m.size,dtype=float)+1
    metadata={"id":"target-"+name,"classes":[0,1],"nonnegative":False}
    return Target(name,kind,np.asarray(values),np.ones(m.size,dtype=bool),m.fields["maturity_at_ns"].copy(),metadata)


def plan():
    return {"minimum_fit_dates":1,"minimum_tuning_dates":1,"minimum_calibration_dates":1,
      "prior_date_mass":2.,"prior_max_iterations":20,"prior_tolerance":1e-10,
      "linear_variants":[{"name":"linear_full","group":"full","basis":"linear","l2":1.}],
      "solver_max_iterations":10,"solver_tolerance":1e-8,"smooth_pinball_epsilon":.01,
      "quantiles":[.1,.5,.9],"hgb_categorical_targets":[],"hgb_continuous_targets":[],
      "hgb_reason":"literal capacity comparison","hgb_configuration":{"max_iter":2},
      "hgb_probability_prior_mix":.01,"evaluation":{}}


def baseline(classes=2,converged=True):
    p=[.6,.4] if classes==2 else [1/classes]*classes
    return {"kind":"jumbo-grouped-compatible-distribution-v1","classes":classes,"group_count":2,
            "probabilities":[p,p],"converged":converged,"id":"literal-baseline"}


class Wire:
    def __init__(self, **values):self.values=values;self.__dict__.update(values)
    def as_dict(self):return self.values.copy()


def categorical_model(m,*,kind="softmax",converged=True,classes=2):
    transform=fit_feature_transform(m,np.arange(m.size)==0,group="full")
    return models._seal({"target_names":["path"],"target_kind":"categorical","feature_names":list(feature_names(m)),
       "target_metadata":[{"id":"target-path","classes":list(range(classes)),"nonnegative":False}],
       "baseline":baseline(classes),"kind":kind,"name":kind,"status":"fitted" if converged else "failed_empirical_fallback",
       "transform":transform,"basis":"linear","backend":{"converged":converged,"status":"completed"},
       "probability_prior_mix":.1})


def continuous_model(m):
    transform=fit_feature_transform(m,np.arange(m.size)==0,group="full")
    return models._seal({"target_names":["a","b"],"target_kind":"continuous","feature_names":list(feature_names(m)),
       "target_metadata":[{"id":"target-a","classes":[0,1],"nonnegative":False},{"id":"target-b","classes":[0,1],"nonnegative":False}],
       "baseline":[],"baseline_id":"literal-quantile-prior","quantiles":[.1,.5,.9],"kind":"quantile","name":"linear_full",
       "status":"fitted","target_scales":[2.,10.],"nonnegative":[False,True],"transform":transform,
       "basis":"linear","backend":{"converged":True}})


def prepared_price_fixture(prior=100.):
    origin=boundary_ns("2022-12-31")
    row={name:None for name in FLOAT_LABELS}
    row.update({name:0. for name in FLOAT_LABELS[:6]})
    row.update({name:0 for name in INTEGER_LABELS})
    row.update({"x_"+name:0. for name in FEATURES})
    row.update(date="2022-12-31",year=2022,root="NQ",clock="A",horizon="after_15m",formation_id="parent",row_id="parent-path-row",contract_key="RAW",label_version=TABLE_VERSION,
       path="no_break",inclusive_path="no_break",prefix_first_side="neither",prefix_both_breach=False,reclaim_observed=False,
       origin_ns=origin,endpoint_ns=origin+15*60_000_000_000,maturity_at_ns=origin+16*60_000_000_000,
       prefix_maturity_at_ns=origin+16*60_000_000_000,planned_minutes=15,observed_prefix_minutes=15,
       label_origin_open_ticks=110,maximum_up_ticks=2,maximum_down_ticks=2,terminal_ticks=1,squared_close_returns_ticks2=4,
       x_width_ticks=20.,x_last_close_position=.5,x_last_close_age_minutes=1.,x_prior_width_ticks=prior)
    form={"formation_id":"parent","root":"NQ","year":2022,"date":"2022-12-31","clock":"A",
          "source_version":"literal-model-anchor","contract_key":"RAW","status":"complete",
          "formation_start_ns":origin-16*60_000_000_000,"formation_end_ns":origin-60_000_000_000,"available_at_ns":origin,
          "low_ticks":90,"high_ticks":110,"open_ticks":90,"close_ticks":100,"width_ticks":20}
    tables={"paths":pa.Table.from_pylist([row],schema=table_schema("paths")),
            "formations":pa.Table.from_pylist([form],schema=table_schema("formations"))}
    refs={k:{"kind":k,"rows":1,"size_bytes":1,"schema_sha256":("3" if k=="paths" else "4")*64,
             "sha256":("1" if k=="paths" else "2")*64} for k in tables}
    shard={"root":"NQ","year":2022,"tables":refs}
    series=MinuteBars(dict(start_ns=[origin-2*60_000_000_000],end_ns=[origin-60_000_000_000],known_at_ns=[origin],
       open_ticks=[100],high_ticks=[100],low_ticks=[100],close_ticks=[100],volume=[1],contract_key=["RAW"],valid=[True]),source_version="literal-model-anchor")
    supplement=build_anchor_supplement(series,tables["formations"],tables["paths"],root="NQ",year=2022,
       path_ref=refs["paths"],formation_ref=refs["formations"],frozen_analysis_id="original-d5f-fixture")
    anchorref={"kind":"anchors","rows":1,"size_bytes":1,"sha256":"5"*64,"schema_sha256":supplement["manifest"]["schema_sha256"]}
    tables["anchors"]=supplement["table"]
    def read(_store,ref,columns):return tables[ref["kind"]].select(columns)
    with patch("trading_research.research.jumbo_matrix._read_columns",side_effect=read):
        return prepare_paths(None,[shard],plan={"expected_formation_clock_ids":["A"],"horizons_minutes":[15],"prefix_delays_minutes":[]},phase="fixture",
             anchor_supplements={("NQ",2022):{"table_ref":anchorref,"manifest":supplement["manifest"]}})


class JumboModelOrchestrationTests(unittest.TestCase):
    def test_phase_masks_use_target_specific_strict_full_maturity(self):
        m=fixture();t=target(m)
        for phase,index in (("fit",0),("tune",2),("calibrate",4),("select",6)):
            self.assertEqual(np.flatnonzero(t.phase(m,phase)).tolist(),[index])
        self.assertEqual(np.flatnonzero(models._phase_rows(m,"select")).tolist(),[6,7])

    def test_fit_masks_all_class_rows_before_priors_and_transforms(self):
        m=fixture();m.fields["maturity_at_ns"][1]=boundary_ns("2022-12-31")
        values=np.ones((9,2),dtype=bool);values[1]=[True,False]
        t=target(m,kind="interval_categorical",values=values)
        with patch.object(models,"fit_grouped_distribution",return_value=baseline()) as prior,\
             patch.object(models.backend,"fit_softmax",return_value=Wire(converged=True)) as fit:
            family=models.fit_categorical_family(m,t,plan=plan())
        self.assertEqual(family["fit"]["eligible_training_rows"],2)
        self.assertEqual(family["fit"]["all_class_uninformative_rows"],1)
        np.testing.assert_equal(prior.call_args.args[0],[[True,False]])
        self.assertEqual(fit.call_args.args[0].shape[0],1)
        self.assertEqual(family["models"]["linear_full"]["transform"]["means"],[1.,2.])
        self.assertEqual(fit.call_args.kwargs["offset_identity"],"literal-baseline")

    def test_no_information_fit_never_calls_optimizer(self):
        m=fixture();t=target(m,kind="interval_categorical",values=np.ones((9,2),dtype=bool))
        with patch.object(models.backend,"fit_softmax") as fit:
            family=models.fit_categorical_family(m,t,plan=plan())
        self.assertEqual(family["status"],"insufficient_training_dates")
        self.assertEqual(family["models"],{});fit.assert_not_called()

    def test_equal_date_weights_and_missing_date_scores(self):
        np.testing.assert_allclose(models.date_weights(np.array([1,1,2],dtype=np.int64)),[.75,.75,1.5])
        self.assertEqual(models.date_mean([0.,2.,10.],np.array([1,1,2],dtype=np.int64)),5.5)
        self.assertIsNone(models.date_mean([np.nan],np.array([1],dtype=np.int64)))
        with self.assertRaises(ContractError):models.date_weights(np.array([1.]))

    def test_dynamic_feature_schema_and_future_input_invariance(self):
        m=fixture();mask=np.arange(m.size)==0
        tr=fit_feature_transform(m,mask,group="full")
        original=transformed_features(m,tr)
        for name in ("future_high_ticks","future_low_ticks","future_close_ticks","maturity_at_ns"):
            m.fields[name][:]=999999999
        np.testing.assert_equal(transformed_features(m,tr),original)
        self.assertEqual(feature_names(m),("causal_a","causal_b"))
        m.manifest["feature_columns"]=["x_causal_a","x_causal_a"]
        with self.assertRaises(ContractError):feature_names(m)

    def test_dynamic_root_identity_is_decoded_not_assumed_code_one(self):
        m=fixture();m.categories["root"]=("ES","NQ")
        tr=fit_feature_transform(m,np.arange(m.size)==0,group="full")
        self.assertEqual(transformed_features(m,tr)[0,-1],1.)

    def test_softmax_prediction_carries_matching_prior_identity_and_checksum(self):
        m=fixture();record=categorical_model(m);mask=np.arange(m.size)==2
        with patch.object(models.backend.SoftmaxFit,"from_dict",return_value=object()),\
             patch.object(models.backend,"offset_array_checksum",return_value="literal-checksum"),\
             patch.object(models.backend,"predict_softmax",return_value=np.array([[.7,.3]])) as predict:
            p,raw=models.predict_model(record,m,mask)
        np.testing.assert_allclose(p,[[.7,.3]])
        np.testing.assert_allclose(predict.call_args.kwargs["offset_logits"],np.log([[.6,.4]]))
        self.assertEqual(predict.call_args.kwargs["offset_identity"],"literal-baseline")
        self.assertEqual(predict.call_args.kwargs["offset_checksum"],"literal-checksum")
        changed=copy.deepcopy(record);changed["name"]="changed"
        with self.assertRaises(IntegrityError):models.predict_model(changed,m,mask)

    def test_failed_softmax_emits_visible_baseline_without_backend_prediction(self):
        m=fixture();record=categorical_model(m,converged=False)
        with patch.object(models.backend,"predict_softmax") as predict:
            p,_=models.predict_model(record,m,np.arange(m.size)==2)
        np.testing.assert_allclose(p,[[.6,.4]]);predict.assert_not_called()
        self.assertEqual(record["status"],"failed_empirical_fallback")

    def test_empty_predictions_have_target_specific_shapes(self):
        m=fixture();empty=np.zeros(m.size,dtype=bool)
        self.assertEqual(models.predict_model(categorical_model(m),m,empty)[0].shape,(0,2))
        self.assertEqual(models.predict_model(continuous_model(m),m,empty)[0].shape,(0,2,3))

    def test_multi_target_scaled_offsets_raw_and_final_projection(self):
        m=fixture();record=continuous_model(m);mask=np.arange(m.size)==2
        base=np.array([[[10.,20.,30.],[100.,200.,300.]]])
        raw_scaled=np.array([[[3.,1.,2.],[-.1,-.2,.3]]])
        with patch.object(models,"_baseline_quantiles",return_value=base),\
             patch.object(models.backend.QuantileFit,"from_dict",return_value=object()),\
             patch.object(models.backend,"offset_array_checksum",return_value="q-checksum"),\
             patch.object(models.backend,"predict_quantiles",return_value=(np.maximum.accumulate(raw_scaled,axis=-1),raw_scaled)) as pred:
            final,raw=models.predict_model(record,m,mask)
        np.testing.assert_equal(raw,[[[6.,2.,4.],[-1.,-2.,3.]]])
        np.testing.assert_equal(final,[[[6.,6.,6.],[0.,0.,3.]]])
        np.testing.assert_equal(pred.call_args.kwargs["offset_quantiles"],[[[5.,10.,15.],[10.,20.,30.]]])
        self.assertTrue(pred.call_args.kwargs["return_raw"])
        self.assertEqual(pred.call_args.kwargs["offset_identity"],"literal-quantile-prior")

    def test_joint_continuous_fitting_never_intersects_different_populations(self):
        m=fixture();a=target(m,"a","continuous");b=target(m,"b","continuous");b.eligible[0]=False
        with self.assertRaises(ContractError):models.fit_continuous_family(m,[a,b],plan=plan())

    def test_continuous_prior_uses_equal_dates_but_group_mass_uses_dates(self):
        m=fixture()
        m.fields["date"][:3]=[date(2022,1,1).toordinal(),date(2022,1,1).toordinal(),date(2022,1,2).toordinal()]
        m.fields["maturity_at_ns"][:3]=boundary_ns("2022-01-03")
        m.fields["root"][1]=1
        t=target(m,"a","continuous",values=[0.,0.,10.,1.,1.,1.,1.,1.,1.])
        p=plan();p["linear_variants"]=[];p["quantiles"]=[.1,.6,.9]
        family=models.fit_continuous_family(m,[t],plan=p)
        wire=family['empirical_distribution_evidence'][0]
        np.testing.assert_allclose(wire["global_atom_masses"],[.5,.5],atol=1e-12,rtol=0)
        self.assertEqual(wire["global_values"],[0.,10.,10.])
        at=wire["groups"].index(1)
        self.assertAlmostEqual(wire["zero_atom_masses"][at],2/3,places=12)

    def test_hgb_quantiles_use_declared_quantile_loss(self):
        m=fixture();t=target(m,"a","continuous");p=plan();p["linear_variants"]=[];p["hgb_continuous_targets"]=["a"]
        with patch.object(models.backend,"fit_empirical_quantiles",return_value=Wire(kind="fixture")),\
             patch('trading_research.research.jumbo_prior_storage.quantile_serving_record',side_effect=lambda wire:wire),\
             patch.object(models,"_baseline_quantiles",return_value=np.ones((1,1,3))),\
             patch.object(models.backend,"fit_hgb_challenger",return_value=Wire(status="completed")) as hgb:
            models.fit_continuous_family(m,[t],plan=p)
        self.assertEqual(hgb.call_count,3)
        for call,q in zip(hgb.call_args_list,p["quantiles"],strict=True):
            self.assertEqual(call.kwargs["loss"],"quantile")
            self.assertEqual(call.kwargs["quantile"],q)
            self.assertEqual(call.kwargs["task"],"regression")

    def test_hgb_declared_class_columns_not_estimator_subset_columns(self):
        m=fixture();record=categorical_model(m,kind="hgb",classes=3)
        fit=SimpleNamespace(estimator=SimpleNamespace(classes_=np.array([0,2])),classes=(0,1,2))
        raw=np.array([[.6,.1,.3]])
        with patch.object(models.backend.HGBChallenger,"from_dict",return_value=fit),\
             patch.object(models.backend,"predict_hgb_challenger",return_value=raw):
            p,_=models.predict_model(record,m,np.arange(m.size)==2)
        np.testing.assert_allclose(p,.9*raw+.1/3,atol=1e-12,rtol=0)

    def test_declared_quantile_tree_is_not_skipped_by_an_undeclared_fused_sibling(self):
        m=fixture();a=target(m,'a','continuous');b=target(m,'b','continuous')
        p=plan();p['linear_variants']=[];p['hgb_continuous_targets']=['a']
        with patch.object(models.backend,'fit_empirical_quantiles',return_value=Wire(kind='fixture')),\
             patch('trading_research.research.jumbo_prior_storage.quantile_serving_record',side_effect=lambda wire:wire),\
             patch.object(models,'_baseline_quantiles',return_value=np.ones((1,2,3))),\
             patch.object(models.backend,'fit_hgb_challenger',return_value=Wire(status='completed')) as hgb:
            family=models.fit_continuous_family(m,[a,b],plan=p)
        self.assertEqual(hgb.call_count,3)
        record=family['models']['hgb_full']
        self.assertIsNone(record['backend'][1])
        self.assertEqual(record['target_statuses'],['fitted','not_declared_for_target'])
        self.assertEqual(models.model_target_status(record,0),'fitted')
        self.assertEqual(models.model_target_status(record,1),'not_declared_for_target')
        # Both source-prior feature blocks remain in the active tree input.
        self.assertGreaterEqual(hgb.call_args.args[0].shape[1],6)
        with self.assertRaises(ContractError):
            models.calibration_for(m,b,record,plan=p,target_index=1)

    def test_tree_failure_in_one_target_does_not_disqualify_an_independent_fitted_head(self):
        m=fixture();t=target(m,'b','continuous')
        family={'models':{'empirical':{'id':'base','status':'fitted'},
             'hgb_full':{'id':'tree','kind':'hgb_quantiles','status':'partial_failure_empirical_fallback',
                         'target_names':['a','b'],'target_statuses':['failed_empirical_fallback','fitted']}}}
        good=np.asarray([[[1.,2.,3.],[2.,3.,4.]]]);bad=good+10
        with patch.object(models,'predict_model',side_effect=[(bad,bad),(good,good)]):
            tuned=models.choose_tuning_model(m,t,family,plan=plan(),target_index=1)
        self.assertEqual(tuned['winner'],'hgb_full')
        self.assertEqual(tuned['comparisons'][1]['status'],'fitted')

    def test_undeclared_tree_target_has_no_tuning_scores_or_prediction_calls(self):
        m=fixture();t=target(m,'b','continuous')
        family={'models':{'empirical':{'id':'base','status':'fitted'},
             'hgb_full':{'id':'tree','kind':'hgb_quantiles','status':'fitted',
                         'target_names':['a','b'],'target_statuses':['fitted','not_declared_for_target']}}}
        prediction=np.asarray([[[1.,2.,3.],[2.,3.,4.]]])
        with patch.object(models,'predict_model',return_value=(prediction,prediction)) as predict:
            tuned=models.choose_tuning_model(m,t,family,plan=plan(),target_index=1)
        self.assertEqual(predict.call_count,1)
        self.assertEqual(tuned['comparisons'][1]['status'],'not_declared_for_target')
        self.assertIsNone(tuned['comparisons'][1]['date_mean_primary_loss'])

    def test_unused_tree_slot_preserves_array_alignment_and_its_exact_baseline(self):
        m=fixture();record=continuous_model(m)
        record.update(kind='hgb_quantiles',backend=[[{'status':'completed'}]*3,None],
                      target_statuses=['fitted','not_declared_for_target'])
        record=models._seal(record)
        base=np.asarray([[[1.,2.,3.],[10.,20.,30.]]])
        with patch.object(models,'_baseline_quantiles',return_value=base),\
             patch.object(models.backend.HGBChallenger,'from_dict',return_value=SimpleNamespace()),\
             patch.object(models.backend,'predict_hgb_challenger',return_value=np.asarray([5.])) as predict:
            result,_=models.predict_model(record,m,np.arange(m.size)==2)
        self.assertEqual(predict.call_count,3)
        np.testing.assert_array_equal(result[:,1],base[:,1])
        np.testing.assert_array_equal(result[:,0],[[10.,10.,10.]])

    def test_quantile_calibration_uses_target_index_and_backend_N_by_Q_API(self):
        m=fixture();t=target(m,"b","continuous");record=continuous_model(m)
        prediction=np.array([[[1.,2.,3.],[10.,20.,30.]]])
        with patch.object(models,"predict_model",return_value=(prediction,prediction)),\
             patch.object(models.backend,"fit_quantile_residual_calibration",return_value=Wire(status="converged")) as calibrate:
            cal=models.calibration_for(m,t,record,plan=plan(),target_index=1)
        np.testing.assert_equal(calibrate.call_args.args[0],[[10.,20.,30.]])
        np.testing.assert_equal(calibrate.call_args.args[1],[5.])
        self.assertEqual(calibrate.call_args.kwargs["source_fit_id"],record["id"])
        with patch.object(models.backend.QuantileResidualCalibration,"from_dict",return_value=SimpleNamespace(status="converged")),\
             patch.object(models.backend,"predict_quantile_residual",return_value=np.array([[11.,21.,31.]])) as apply:
            out=models.apply_calibration(cal,prediction,model=record,target=t,target_index=1)
        self.assertEqual(out.shape,(1,1,3));np.testing.assert_equal(apply.call_args.args[1],[[10.,20.,30.]])

    def test_joint_model_calibration_cannot_be_attached_to_different_target(self):
        m=fixture();b=target(m,"b","continuous");a=target(m,"a","continuous");record=continuous_model(m)
        prediction=np.ones((1,2,3))
        with patch.object(models,"predict_model",return_value=(prediction,prediction)),\
             patch.object(models.backend,"fit_quantile_residual_calibration",return_value=Wire(status="converged")):
            cal=models.calibration_for(m,b,record,plan=plan(),target_index=1)
        with self.assertRaises(IntegrityError):
            models.apply_calibration(cal,prediction,model=record,target=a,target_index=0)

    def test_noinfo_calibration_does_not_fit_temperature(self):
        m=fixture();t=target(m,kind="interval_categorical",values=np.ones((9,2),dtype=bool))
        with patch.object(models.backend,"fit_temperature") as fit:
            out=models.calibration_for(m,t,categorical_model(m),plan=plan())
        self.assertEqual(out["kind"],"unavailable");fit.assert_not_called()

    def test_empty_selection_labels_retain_intended_date_denominator(self):
        m=fixture();t=target(m);t.eligible[:]=False
        out=models.evaluate_target(m,t,{"models":{}},phase="select",plan=plan(),tuned={"winner":"empirical"})
        self.assertEqual(out["status"],"no_eligible_labels")
        self.assertEqual(out["intended_rows"],2)
        self.assertEqual(out["eligible_rows"],0)
        self.assertEqual(out["excluded_or_unmatured_rows"],2)
        self.assertEqual(out["intended_date_universes"]["0"],m.fields["date"][[6,7]].tolist())

    def test_failed_variant_cannot_win_tuning_on_its_fallback_score(self):
        m=fixture();t=target(m)
        family={"models":{"empirical":{ "id":"base","status":"fitted"},"failed":{ "id":"bad","status":"failed_empirical_fallback"}}}
        with patch.object(models,"predict_model",side_effect=[(np.array([[.6,.4]]),np.array([[.6,.4]])),(np.array([[.99,.01]]),np.array([[.99,.01]]))]):
            tuned=models.choose_tuning_model(m,t,family,plan=plan())
        self.assertEqual(tuned["winner"],"empirical")

    def test_exact_prior_width_and_raw_extrema_remain_separate_from_features(self):
        m=prepared_price_fixture(prior=float(2**24+1))
        self.assertEqual(int(m.fields["prior_width_ticks"][0]),2**24+1)
        self.assertEqual(float(m.features[0,FEATURES.index("prior_width_ticks")]),float(2**24))
        self.assertEqual([int(m.fields[k][0]) for k in ("future_high_ticks","future_low_ticks","future_close_ticks")],[112,108,111])
        self.assertNotIn("future_high_ticks",feature_names(m))
        tr=fit_feature_transform(m,np.array([True]),group="full");before=transformed_features(m,tr)
        m.fields["future_high_ticks"][:]=999999
        np.testing.assert_equal(transformed_features(m,tr),before)

    def test_prior_width_missing_fractional_negative_and_precision_bounds(self):
        self.assertEqual(int(prepared_price_fixture(prior=None).fields["prior_width_ticks"][0]),-1)
        self.assertEqual(int(prepared_price_fixture(prior=0.).fields["prior_width_ticks"][0]),0)
        self.assertEqual(int(prepared_price_fixture(prior=float(2**53)).fields["prior_width_ticks"][0]),2**53)
        for prior in (-1.,1.5,float(2**53+2)):
            with self.subTest(prior=prior),self.assertRaises(IntegrityError):prepared_price_fixture(prior=prior)

class SharedQuantileEvidenceTests(unittest.TestCase):
    def full_fit(self):
        return models.backend.fit_empirical_quantiles(
            np.asarray([-2., 0., 0., 3., 5., 8.]), np.ones(6),
            quantiles=[.1, .5, .9], shrinkage=2., group_ids=[1, 1, 1, 2, 2, 2],
            global_weights=np.asarray([.5, .5, 1., 1., .5, .5])).as_dict()

    def test_compact_serving_preserves_every_quantile_and_global_fallback_exactly(self):
        from trading_research.research.jumbo_prior_storage import quantile_serving_record, predict_quantile_serving
        full=self.full_fit()
        groups=[2, 1, 9, 1, 2]
        old=models.backend.predict_empirical_quantiles(models.backend.EmpiricalQuantileFit.from_dict(full),groups)
        serving=quantile_serving_record(full)
        actual=predict_quantile_serving(serving,groups)
        np.testing.assert_array_equal(actual.view(np.uint64),old.view(np.uint64))
        self.assertNotIn('atoms',serving)
        self.assertIn('atoms',full)
        self.assertIn('global_atom_masses',full)

    def test_frozen_family_requires_the_exact_full_distribution_and_serving_view(self):
        from trading_research.research.jumbo_prior_storage import quantile_serving_record, validate_family_priors, FAMILY_SCHEMA
        from trading_research.operations.artifacts import digest
        full=self.full_fit(); serving=quantile_serving_record(full)
        model={'target_kind':'continuous','baseline_id':digest([full]),'baseline':[serving]}
        family={'prior_storage_schema':FAMILY_SCHEMA,'empirical_distribution_evidence':[full],
                'models':{'empirical':model,'linear':copy.deepcopy(model)}}
        self.assertTrue(validate_family_priors(family)['full_atom_and_mass_evidence_retained'])
        bad=copy.deepcopy(family);bad['empirical_distribution_evidence'][0]['global_atom_masses'][0]+=.1
        with self.assertRaises(IntegrityError):validate_family_priors(bad)
        bad=copy.deepcopy(family);bad['models']['linear']['baseline'][0]['values'][0][0]+=.1
        with self.assertRaises(IntegrityError):validate_family_priors(bad)
        bad=copy.deepcopy(family);bad.pop('empirical_distribution_evidence')
        with self.assertRaises(IntegrityError):validate_family_priors(bad)

    def test_full_atom_evidence_can_be_published_before_fitting_and_restored_once(self):
        import tempfile
        from pathlib import Path
        from trading_research.operations.artifacts import ArtifactStore
        from trading_research.research.jumbo_fitting import put_json_compressed, read_json_compressed
        from trading_research.research.jumbo_prior_storage import validate_family_priors
        with tempfile.TemporaryDirectory() as directory:
            store=ArtifactStore(Path(directory));saved=[]
            def writer(full):
                saved.append(copy.deepcopy(full))
                return put_json_compressed(store,full,kind='fixture_full_empirical_prior',remaining_bytes=1024*1024,normalized=True)
            m=fixture();p=plan();p['linear_variants']=[]
            family=models.fit_continuous_family(m,[target(m,'a','continuous')],plan=p,prior_writer=writer)
            self.assertNotIn('empirical_distribution_evidence',family)
            self.assertEqual(read_json_compressed(store,family['empirical_distribution_artifact']),saved[0])
            self.assertEqual(validate_family_priors(family,store=store)['full_distribution_count'],1)
            self.assertTrue(saved[0][0]['atoms'])


if __name__ == "__main__":
    unittest.main()
