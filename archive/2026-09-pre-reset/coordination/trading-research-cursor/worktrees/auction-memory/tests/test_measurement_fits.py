"""M-F11-FIT-001: real retained temporal training reads and transform admission."""

from dataclasses import fields, replace
from pathlib import Path
from fractions import Fraction
from tempfile import TemporaryDirectory
import unittest

from trading_research.errors import ContractError, DependencyUnavailable, IntegrityError
from trading_research.measurements.measurement_fits import (
    admit_measurement_fit, standardize_from_measurement_fit, validate_measurement_fit_payload,
)
from trading_research.operations.artifacts import canonical_json, digest
from trading_research.operations.artifact_graph import (
    SemanticArtifactStore, ReadRequest, ReadBinding, ReadSession, FitEvidence, LabelEvidence, LabelTarget,
    validate_temporal_fold_evidence,
)
from trading_research.research.temporal_folds import DEFAULT_LIMITS, TemporalSampleV1, compile_temporal_fold
from tests.test_artifact_graph import Fixture


def measurement_fit_fixture(root, *, mean=2.0, completion=31, training_ids=None):
    f = Fixture()
    f.namespace = "m-fit-test"
    f.target = f.keep(b"m-next-window-target-v1", "target")
    population = tuple(TemporalSampleV1(id, group, cut, end, known, f.target.sha256, role, episode, (), ())
        for id, group, cut, end, known, role, episode in (
            ("train1", "date1", 10, 11, 12, "train", "episode1"),
            ("train2", "date2", 20, 21, 22, "train", "episode2"),
            ("heldout", "date3", 40, 50, 51, "outer", "episode3")))
    fold = compile_temporal_fold(population, id="m-fit-fold", fit_at=30, evaluation_start=40, evaluation_end=60)
    fold_node = f.node("fold", "fold", execution=replace(f.execution, configuration_json=canonical_json({
        "temporal_limits_v1": {field.name: getattr(DEFAULT_LIMITS, field.name) for field in fields(DEFAULT_LIMITS)},
    })), fold_evidence=validate_temporal_fold_evidence(population, fold))
    source = f.node("source", "source", rows=tuple(f.row(row_id=s.id, value=v, observed=s.decision_at-1,
        known=s.decision_at, version="source:"+s.id, acquisition="receipt:"+s.id, valid_until=60)
        for s, v in zip(population, (1, 3, 5))))
    labels = f.node("labels", "label", rows=tuple(f.row(row_id=s.id, column="label", value=0,
        observed=s.target_end, known=s.label_known_at, valid_until=60) for s in population[:2]),
        label_targets=tuple(LabelTarget(s.id, f.target, s.decision_at, s.target_end) for s in population[:2]))
    store = SemanticArtifactStore(Path(root), f.namespace)
    initial_nodes = (fold_node, source, labels)
    base = store.commit("sources", tuple(n.id for n in initial_nodes), initial_nodes, f.payloads)
    read_nodes = []
    for sample in population[:2]:
        q = ReadRequest(sample.id, sample.decision_at, sample.decision_at, "fit_feature", "Row.v1", "probability",
                        date_group=sample.date_group, fold_node_id=fold_node.id)
        session = ReadSession(store, base, (ReadBinding("x", source.id, "x", q),))
        session.read("x")
        read_nodes.append(f.node("read:"+sample.id, "read_manifest", read_manifest=session.seal(),
            dependencies=(f.dep("x", source, "value", ("x",)), f.dep("fold", fold_node))))
    fit = FitEvidence(fold_node.id, 30, completion, fold.training_ids if training_ids is None else training_ids,
        ("date1", "date2"), tuple(LabelEvidence(s.id, labels.id, "label", f.target) for s in population[:2]),
        tuple(n.id for n in read_nodes), f.target)
    recipe_id = digest({"kernel": "population-standardization-v1", "columns": ("x",)})
    execution = replace(f.execution, configuration_json=canonical_json({
        "measurement_fit": {"family": "standardization", "recipe_id": recipe_id, "parameters": {"columns": ("x",)}},
    }))
    state = canonical_json({"columns": ("x",), "means": (mean,), "scales": (1.0,)})
    transform = f.node("measurement-standardization", "transform", raw=state, execution=execution, fit_evidence=fit,
        dependencies=(f.dep("fold", fold_node), f.dep("labels", labels, "fit_label", ("label",)),
                      *(f.dep(n.logical_key, n) for n in read_nodes)))
    nodes = (*initial_nodes, *read_nodes, transform)
    commit = store.commit("fitted", (transform.id,), nodes, f.payloads)
    request = ReadRequest("heldout", 40, 41, "OOF", "Row.v1", "probability", f.target, 40, 50, "date3", fold_node.id)
    return store, commit, transform, request, recipe_id, source, fold_node, base, state


class MeasurementFitTests(unittest.TestCase):
    def test_M_F11_FIT_001_actual_cohort_conditional_and_surface_queries(self):
        from tests.measurement_fixtures import row,ledger,request as window_request
        from tests.measurement_fit_sources import fitted_sources
        from trading_research.measurements.common import capture_trade_window
        from trading_research.measurements.cvd import fit_cohort_definition,measure_cohort_cvd
        from trading_research.measurements.tape_intensity import (
            PrewindowContext,fit_conditional_flow,apply_conditional_flow,
            fit_effort_progress_surface,apply_effort_progress_surface,
        )
        from trading_research.measurements.measurement_fits import MeasurementFitBinding
        records=tuple(row(str(at),at=at,price=price,size=size) for at,price,size in
            ((8,100,1),(9,102,1),(18,100,3),(19,104,3),(38,100,2),(39,103,2)))
        view=ledger(records)
        captures=tuple(capture_trade_window(view,**window_request(start=a,end=b,published=p))
                       for a,b,p in ((8,10,10),(18,20,20),(38,40,41)))
        a,b,query=captures
        training=(('train1',a),('train2',b))
        with TemporaryDirectory() as directory:
            root=Path(directory)
            params=dict(train_end=30,available_at=31,probabilities=(Fraction(1,2),),weighting='count',version='cohort-query')
            state=fit_cohort_definition((a,b),view=view,**params)['definition']
            f=fitted_sources(root/'cohort',family='cohort',parameters=params,recipe_id=state.fit_recipe_id,state=state,
                training_features=({'measurement_capture':a.record()},{'measurement_capture':b.record()}),
                query_features={'measurement_capture':query.record()})
            binding=MeasurementFitBinding(f['admission'],training,query_session=f['query_session'])
            result=measure_cohort_cvd(query,view=view,definition=state,fit_binding=binding)
            self.assertEqual(tuple(p.close for p in result.paths),(0,4))
            self.assertEqual(tuple((c.lower_inclusive,c.upper_exclusive) for c in state.channels),((1,2),(2,None)))
            contexts=tuple(PrewindowContext('session',at,(('session','rth'),)) for at in (7,17,37))
            params=dict(train_end=30,available_at=31,version='conditional-query',minimum_cell_rows=1)
            state=fit_conditional_flow(((a,contexts[0]),(b,contexts[1])),view=view,**params)
            f=fitted_sources(root/'conditional',family='conditional_flow',parameters=params,recipe_id=state.recipe_id,state=state,
                training_features=tuple({'measurement_capture':c.record(),'prewindow_context':k} for c,k in zip((a,b),contexts)),
                query_features={'measurement_capture':query.record(),'prewindow_context':contexts[2]})
            binding=MeasurementFitBinding(f['admission'],training,tuple(zip(('train1','train2'),contexts)),f['query_session'])
            result=apply_conditional_flow(query,view=view,context=contexts[2],baseline=state,fit_binding=binding)
            self.assertEqual((result['expected'],result['residuals']),((2,4,4),(0,0,0)))
            with self.assertRaises(IntegrityError):
                apply_conditional_flow(query,view=view,context=replace(contexts[2],bins=(('session','other'),)),baseline=state,fit_binding=binding)
            params=dict(effort_cuts=(4,),volatility_cuts=(),shrinkage=0,available_at=31,version='surface-query',epsilon=1)
            state=fit_effort_progress_surface(((2,1,2),(6,1,4)),**{k:v for k,v in params.items() if k!='epsilon'})
            contexts=((7,1),(17,1),(37,1))
            f=fitted_sources(root/'surface',family='effort_surface',parameters=params,recipe_id=state.recipe_id,state=state,
                training_features=tuple({'measurement_capture':c.record(),'prewindow_context':k} for c,k in zip((a,b),contexts)),
                query_features={'measurement_capture':query.record(),'prewindow_context':contexts[2]})
            binding=MeasurementFitBinding(f['admission'],training,tuple(zip(('train1','train2'),contexts)),f['query_session'])
            kwargs=dict(view=view,surface=state,prewindow_volatility=1,context_known_at=37,fit_binding=binding)
            self.assertEqual(apply_effort_progress_surface(query,**kwargs)['residual'],-1)
            with self.assertRaises(ContractError):apply_effort_progress_surface(query,epsilon=2,**kwargs)

    def test_M_F11_FIT_001(self):
        with TemporaryDirectory() as directory:
            store, commit, transform, request, recipe, source, fn, base, state = measurement_fit_fixture(directory)
            admission = admit_measurement_fit(store, commit, transform.id, request, schema_id="Row.v1", unit="probability", recipe_id=recipe)
            self.assertEqual(admission.fold.training_ids, ("train1", "train2"))
            self.assertEqual(admission.fold.evaluation_ids, ("heldout",))
            read = ReadSession(store, base, (ReadBinding("x", source.id, "x", replace(request, purpose="input")),))
            self.assertEqual(read.read("x"), b"5")
            self.assertEqual(standardize_from_measurement_fit(admission, columns=("x",), values=(5,), query_session=read), (3,))
            with self.assertRaises(IntegrityError):
                standardize_from_measurement_fit(admission, columns=("x",), values=(6,), query_session=read)
            with self.assertRaises(ContractError):
                standardize_from_measurement_fit(admission, columns=("x",), values=(5,), query_session=None)
            self.assertEqual(admission.payload, state)
            reopened = SemanticArtifactStore(Path(directory), "m-fit-test")
            restored = admit_measurement_fit(reopened, commit, transform.id, request, schema_id="Row.v1", unit="probability", recipe_id=recipe)
            restored_read = ReadSession(reopened, base, (ReadBinding("x", source.id, "x", replace(request, purpose="input")),))
            self.assertEqual(standardize_from_measurement_fit(restored, columns=("x",), values=(5,), query_session=restored_read), (3,))
            bad_request = replace(request, purpose="fit_feature", assembled_at=40)
            forbidden = ReadSession(store, base, (ReadBinding("x", source.id, "x", bad_request),))
            with self.assertRaises(ContractError):
                forbidden.read("x")
            with self.assertRaises(IntegrityError):
                validate_measurement_fit_payload(admission, canonical_json({"columns": ("x",), "means": (4.,), "scales": (1.,)}))
        with TemporaryDirectory() as directory:
            store, commit, transform, request, recipe, *_ = measurement_fit_fixture(directory, completion=41)
            with self.assertRaises(ContractError):
                admit_measurement_fit(store, commit, transform.id, request, schema_id="Row.v1", unit="probability", recipe_id=recipe)
        with TemporaryDirectory() as directory:
            with self.assertRaises(ContractError):
                measurement_fit_fixture(directory, training_ids=("train1", "train2", "heldout"))
        with TemporaryDirectory() as directory:
            store, commit, transform, request, recipe, source, fn, base, state = measurement_fit_fixture(directory, mean=4.)
            admission = admit_measurement_fit(store, commit, transform.id, request, schema_id="Row.v1", unit="probability", recipe_id=recipe)
            read = ReadSession(store, base, (ReadBinding("x", source.id, "x", replace(request,purpose="input")),))
            with self.assertRaises(IntegrityError):
                standardize_from_measurement_fit(admission, columns=("x",), values=(5,), query_session=read)
