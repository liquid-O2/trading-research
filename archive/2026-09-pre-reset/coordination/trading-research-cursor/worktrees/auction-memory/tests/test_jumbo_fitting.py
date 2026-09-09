"""Synthetic publication contracts and one actual backend freeze/restore join."""
from contextlib import ExitStack
from dataclasses import dataclass
import gzip
import hashlib
import io
import unittest
from unittest.mock import patch
import numpy as np
from trading_research.errors import DependencyUnavailable, IntegrityError
from trading_research.operations.artifacts import canonical_json
from trading_research.research import jumbo_fitting as fitting
from tests.test_jumbo_models import fixture, target, plan as fixture_plan


@dataclass
class Ref:
    sha256: str
    size_bytes: int
    kind: str


class MemoryStore:
    def __init__(self):
        self.values = {}
        self.writes = []
    def put_bytes(self, raw, *, kind):
        ref = Ref(hashlib.sha256(raw).hexdigest(),len(raw),kind)
        self.values[ref.sha256] = raw
        self.writes.append(ref)
        return ref
    def read(self, ref):
        return self.values[ref.sha256]


class FittingPublicationTests(unittest.TestCase):
    def test_actual_backend_records_survive_freeze_restore_and_censored_prediction_population(self):
        matrix, store = fixture(), MemoryStore()
        matrix.fields['origin_ns'] = matrix.fields['maturity_at_ns']-1
        targets = {name:target(matrix,name,'continuous') for name in ('a','b')}
        targets['b'].values = targets['a'].values*10
        plan = fixture_plan()
        plan['evaluation'] = {'replicates':1000,'block_length':5,'minimum_dates':100,'minimum_events':20}
        result = fitting.fit_domain(matrix,targets,store,domain='literal-backend-integration',
                                    plan=plan,maximum_output_bytes=2_000_000)
        self.assertEqual([row['status'] for row in result['targets']],['independently_evaluated']*2)
        for row in result['targets']:
            with np.load(io.BytesIO(store.values[row['selection_predictions']['sha256']]),allow_pickle=False) as values:
                self.assertEqual(values['prepared_row'].tolist(),[6,7])
                self.assertEqual(values['scored_mask'].tolist(),[True,False])
                self.assertTrue(np.isfinite(values['selected_calibrated']).all())
        # A different matrix/target artifact identity is legitimate on a later
        # cohort; semantic target definitions and exact calibration binding stay.
        matrix.manifest = {**matrix.manifest,'id':'later-cohort'}
        for t in targets.values():
            t.metadata = {**t.metadata,'id':'later-'+t.name,'source_matrix':'later-cohort'}
        with (patch.object(fitting,'fit_continuous_family',side_effect=AssertionError('heldout refit')),
             patch.object(fitting,'choose_tuning_model',side_effect=AssertionError('heldout retuning')),
             patch.object(fitting,'calibration_for',side_effect=AssertionError('heldout recalibration'))):
            confirmed = fitting.confirm_domain(matrix,targets,result,store,plan=plan,maximum_output_bytes=2_000_000)
        self.assertEqual((confirmed['new_fits'],confirmed['new_calibrations'],confirmed['reselections']),(0,0,0))
        self.assertEqual(len(confirmed['targets']),2)
        for row in confirmed['targets']:
            with np.load(io.BytesIO(store.values[row['heldout_predictions']['sha256']]),allow_pickle=False) as values:
                self.assertEqual(values['prepared_row'].tolist(),[8])
                self.assertTrue(np.isfinite(values['selected_calibrated']).all())

    def test_joint_family_requires_identical_strict_fit_masks(self):
        matrix = fixture()
        a = target(matrix,"a","continuous")
        b = target(matrix,"b","continuous")
        c = target(matrix,"c","continuous")
        c.eligible[0] = False
        families = list(fitting._families(matrix,{t.name:t for t in (a,b,c)}))
        self.assertEqual([names for names,_ in families],[("a","b"),("c",)])
        self.assertEqual(a.phase(matrix,"fit").tolist(),[True,False,False,False,False,False,False,False,False])

    def test_compressed_identity_and_budget_precede_store_write(self):
        store = MemoryStore()
        value = {"model_id":"literal","coefficients":[1.,2.]}
        ref = fitting.put_json_compressed(store,value,kind="literal_test",remaining_bytes=10000)
        self.assertEqual(fitting.read_json_compressed(store,ref),value)
        with self.assertRaises(IntegrityError):
            fitting.read_json_compressed(store,{**ref,"uncompressed_sha256":"0"*64})
        with self.assertRaises(IntegrityError):
            fitting.read_json_compressed(store,{**ref,"uncompressed_size_bytes":1})
        before = len(store.writes)
        with self.assertRaises(DependencyUnavailable):
            fitting.put_json_compressed(store,value,kind="literal_test",remaining_bytes=1)
        self.assertEqual(len(store.writes),before)

    def test_every_target_and_shared_family_retained_and_confirmed_without_refit(self):
        matrix,store = fixture(),MemoryStore()
        targets = {name:target(matrix,name,"continuous") for name in ("a","b")}
        family = {"models":{"empirical":{"id":"baseline"},"fixed":{"id":"fixed-model"}},"status":"fitted"}
        def evaluation(matrix,target,family,**kwargs):
            return dict(target=target.name,phase=kwargs["phase"],status="evaluated",intended_rows=2,
                        eligible_rows=1,comparisons={})
        def calibration(matrix,target,model,**kwargs):
            return dict(source_model_id=model["id"],target=target.name,target_index=kwargs["target_index"])
        def predictions(*args,**kwargs):
            return {"size_bytes":7,"model_id":"fixed-model","phase":kwargs["phase"]}
        checkpoints = []
        def checkpoint(record):
            checkpoints.append(record)
            return len(canonical_json(record))
        with ExitStack() as stack:
            fit = stack.enter_context(patch.object(fitting,"fit_continuous_family",return_value=family))
            stack.enter_context(patch.object(fitting,"choose_tuning_model",return_value={"winner":"fixed"}))
            stack.enter_context(patch.object(fitting,"calibration_for",side_effect=calibration))
            stack.enter_context(patch.object(fitting,"evaluate_target",side_effect=evaluation))
            stack.enter_context(patch.object(fitting,"_emit_predictions",side_effect=predictions))
            result = fitting.fit_domain(matrix,targets,store,domain="literal",plan={"frozen":"one"},
                                        maximum_output_bytes=100000,checkpoint=checkpoint)
            self.assertEqual(fit.call_count,1)
            self.assertEqual([r["target"] for r in result["targets"]],["a","b"])
            self.assertEqual([r["target_index"] for r in result["targets"]],[0,1])
            self.assertEqual(len(checkpoints),2)
            self.assertEqual(result["heldout_rows_used"],0)
            self.assertEqual(result["derived_output_bytes"],sum(ref.size_bytes for ref in store.writes)+14+sum(len(canonical_json(record)) for record in checkpoints))
        with ExitStack() as stack:
            never = [stack.enter_context(patch.object(fitting,name,side_effect=AssertionError("confirmation mutated frozen development")))
                     for name in ("fit_continuous_family","fit_categorical_family","choose_tuning_model","calibration_for")]
            evaluated = stack.enter_context(patch.object(fitting,"evaluate_target",side_effect=evaluation))
            stack.enter_context(patch.object(fitting,"_emit_predictions",side_effect=predictions))
            confirmed = fitting.confirm_domain(matrix,targets,result,store,plan={"frozen":"one"},maximum_output_bytes=100000)
            self.assertEqual(len(confirmed["targets"]),2)
            self.assertEqual((confirmed["new_fits"],confirmed["new_calibrations"],confirmed["reselections"]),(0,0,0))
            self.assertTrue(all(not mocked.called for mocked in never))
            self.assertTrue(all(call.kwargs["phase"]=="heldout" for call in evaluated.call_args_list))
            self.assertEqual(evaluated.call_args_list[1].kwargs["target_index"],1)
        with self.assertRaises(IntegrityError):
            fitting.confirm_domain(matrix,targets,result,store,plan={"frozen":"changed"},maximum_output_bytes=100000)
        with self.assertRaises(IntegrityError):
            fitting.confirm_domain(matrix,{"a":targets["a"]},result,store,plan={"frozen":"one"},maximum_output_bytes=100000)

    def test_prediction_axis_and_source_rows_are_retained(self):
        matrix,store = fixture(),MemoryStore()
        matrix.fields["origin_ns"] = np.arange(matrix.size,dtype=np.int64)+100
        label = target(matrix,"b","continuous")
        family = {"models":{"fixed":{"id":"fixed"},"empirical":{"id":"empirical"}}}
        def predict(model,matrix,mask):
            # Distinct heads make accidentally taking target zero detectable.
            return np.tile(np.array([[[1.,2.,3.],[11.,12.,13.]]]),(int(mask.sum()),1,1)),{}
        def calibrate(calibration,prediction,**kwargs):
            return prediction[:,kwargs["target_index"]:kwargs["target_index"]+1]+100
        with patch.object(fitting,"predict_model",side_effect=predict),patch.object(fitting,"apply_calibration",side_effect=calibrate):
            ref = fitting._emit_predictions(store,matrix,label,family,{"winner":"fixed"},{},phase="select",target_index=1,plan={},remaining_bytes=100000)
        with np.load(io.BytesIO(store.values[ref["sha256"]]),allow_pickle=False) as values:
            self.assertEqual(values["prepared_row"].tolist(),[6,7])
            self.assertEqual(values["selected_calibrated"].tolist(),[[111.,112.,113.],[111.,112.,113.]])
            self.assertEqual(values["empirical"].tolist(),[[11.,12.,13.],[11.,12.,13.]])
            self.assertEqual(values["origin_ns"].tolist(),[106,107])
            self.assertEqual(values["scored_mask"].tolist(),[True,False])
        self.assertEqual(ref["model_id"],"fixed")
        self.assertEqual(ref["scored_rows"],1)
        self.assertEqual(ref["intended_prediction_rows"],2)
        self.assertTrue(ref["retrospective_reconstruction"])
        self.assertGreater(ref["actual_artifact_created_at_ns"],ref["historical_training_calibration_closure_ns"])
        label.eligible[:] = False
        label.values[:] = -999.
        with patch.object(fitting,"predict_model",side_effect=predict),patch.object(fitting,"apply_calibration",side_effect=calibrate):
            changed = fitting._emit_predictions(store,matrix,label,family,{"winner":"fixed"},{},phase="select",target_index=1,plan={},remaining_bytes=100000)
        with np.load(io.BytesIO(store.values[changed["sha256"]]),allow_pickle=False) as values:
            self.assertEqual(values["prepared_row"].tolist(),[6,7])
            self.assertEqual(values["selected_calibrated"].tolist(),[[111.,112.,113.],[111.,112.,113.]])
            self.assertEqual(values["scored_mask"].tolist(),[False,False])


    def test_checkpoint_aggregate_refusal_precedes_callback_publication(self):
        matrix,store = fixture(),MemoryStore()
        label = target(matrix,"unavailable","continuous")
        family = {"models":{},"status":"insufficient_fit_dates","fit":{"rows":0}}
        # A literal compressed family is allowed, but no space remains for the
        # canonical target checkpoint. The callback must never be called.
        writer = unittest.mock.Mock(return_value=0)
        with patch.object(fitting,"fit_continuous_family",return_value=family),patch.object(fitting,"put_json_compressed",return_value={"sha256":"family","size_bytes":10}):
            with self.assertRaises(DependencyUnavailable):
                fitting.fit_domain(matrix,{label.name:label},store,domain="literal",plan={},maximum_output_bytes=10,checkpoint=writer)
        writer.assert_not_called()

    def test_checkpoint_writer_must_report_exact_canonical_bytes(self):
        matrix,store = fixture(),MemoryStore()
        label = target(matrix,"unavailable","continuous")
        family = {"models":{},"status":"insufficient_fit_dates","fit":{"rows":0}}
        for wrong in (None,0,True):
            with patch.object(fitting,"fit_continuous_family",return_value=family):
                with self.assertRaises(IntegrityError):
                    fitting.fit_domain(matrix,{label.name:label},store,domain="literal",plan={},maximum_output_bytes=100000,checkpoint=lambda record:wrong)

