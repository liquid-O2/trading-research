"""All 24 preregistered F11 finite cases; no market-data or predictor search."""
from dataclasses import asdict, dataclass, replace
from fractions import Fraction
import json
import multiprocessing
from pathlib import Path
import resource
import tempfile
import time
import unittest

from references import artifact_graph_literal as literal
from trading_research.errors import ContractError, DependencyUnavailable, IntegrityError
from trading_research.operations.artifacts import ArtifactRef, canonical_json
from trading_research.operations.artifact_graph import (
    ExecutionIdentity, DependencyRef, RowEvidence, ValidatedFoldEvidence, LabelEvidence,
    FitEvidence, PredictionEvidence, ReadRequest, ReadBinding, ReadRecord, ReadManifest,
    SemanticNodeSpec, Limits, SemanticArtifactStore, ReadSession, payload_ref,
    validate_closure, validate_oof_producer, plan_rebuild, attest_state, evaluate_toy,
    record_failed_attempt, LabelTarget, DerivationEvidence, numerical_decision, snapshot_pair, training_standardization, _encode, _decode,
)
from trading_research.operations.provenance import InputAudit, InputValue, compatible_checkpoint
from trading_research.research.folds import Sample, chronological_fold, validate_fold_population


GOLDEN = json.loads((Path(__file__).parent / "golden/f11-artifacts.json").read_text())
CASES = {c["id"]: c for c in GOLDEN["cases"]}
ENGINEERING_METRICS = {}


@dataclass(frozen=True)
class SuppliedState:
    id: str = "legacy-m"
    columns: tuple[str, ...] = ("x",)
    mean: int = 1
    scale: int = 1
    coefficient: int = 1


class Fixture:
    def __init__(self):
        self.namespace = GOLDEN["base_evidence"]["namespace"]
        self.payloads = {}
        self.definition = self.keep(b"definition-v1", "definition")
        self.target = self.keep(b"first-passage-v1", "target")
        self.code = self.keep(b"code-v1", "code")
        numerical = {"backend_id": "independent-rational-toy-v1", "precision": "exact_fraction",
                     "rounding": "none", "seed": None, "thread_count": 1, "library_versions": {"rational": "literal-v1"}}
        self.execution = ExecutionIdentity(self.code, canonical_json({"window": 2}), canonical_json(numerical))

    def keep(self, raw, kind="semantic_payload"):
        ref = payload_ref(raw, kind)
        self.payloads[ref.sha256] = raw
        return ref

    def node(self, key, kind="checkpoint", *, rows=(), dependencies=(), raw=None, **kwargs):
        if rows:
            rows = tuple(sorted(rows, key=lambda r: (r.row_id, r.column)))
            raw = canonical_json([[r.row_id, r.column, json.loads(r.value_json)] for r in rows])
        elif raw is None:
            raw = canonical_json({"state": key})
        if kind == "label" and "label_targets" not in kwargs:
            kwargs["label_targets"] = tuple(LabelTarget(r.row_id, self.target, 20 if r.row_id == "train-0" else 100, r.observed_at) for r in rows)
        return SemanticNodeSpec(self.namespace, key, kind, kwargs.pop("schema_id", "Row.v1"),
                                kwargs.pop("unit", "probability"), self.definition, self.keep(raw),
                                kwargs.pop("execution", None if kind in {"source", "definition", "label", "fold"} else self.execution),
                                tuple(dependencies), tuple(rows), **kwargs)

    def row(self, *, row_id="sample-eval", column="x", value=3, observed=99, known=100,
            version="x-v1", acquisition="receipt-x1", valid_until=140):
        return RowEvidence(row_id, column, version, acquisition, observed, known, "received", canonical_json(value),
                           valid_from=None, valid_until=valid_until)

    def source(self, key="source", **kwargs):
        return self.node(key, "source", rows=(self.row(**kwargs),))

    def dep(self, key, node, use="provenance", columns=()):
        return DependencyRef(key, node.id, use, columns)

    def closure(self, nodes, roots=None, limits=Limits()):
        nodes = tuple(nodes)
        return validate_closure(tuple(n.id for n in (roots or nodes)), nodes, self.payloads, self.namespace, limits)

    def complete(self, mode="OOF", source_until=140):
        train = self.source("training-x", row_id="train-0", value=1, observed=19, known=20,
                            version="training-x-v1", acquisition="training-receipt-x1")
        label = self.node("training-label", "label", rows=(self.row(row_id="train-0", column="label", value=1,
                            observed=50, known=51, version="label-v1"),))
        source = self.source(valid_until=source_until)
        population = (Sample("train-0", "day-0", 20, 51, 50, self.target.sha256),
                      Sample("sample-eval", "day-1", 100, 131, 130, self.target.sha256))
        fold = chronological_fold(population, id="fold-1", fit_at=90, evaluation_start=100, evaluation_end=140)
        fold_node = self.node("fold", "fold", fold_evidence=ValidatedFoldEvidence(population, fold))
        train_request = ReadRequest("train-0", 20, 20, "fit_feature", "Row.v1", "probability",
                                    date_group="day-0", fold_node_id=fold_node.id)
        tb = ReadBinding("x", train.id, "x", train_request)
        tm = ReadManifest(self.namespace, (tb,), (ReadRecord(tb, train.row_evidence[0]),), ())
        train_reads = self.node("training-reads", "read_manifest", read_manifest=tm,
                               dependencies=(self.dep("x", train, "value", ("x",)), self.dep("fold", fold_node)))
        fit = FitEvidence(fold_node.id, 90, 92, ("train-0",), ("day-0",),
                          (LabelEvidence("train-0", label.id, "label", self.target),), (train_reads.id,), self.target)
        model = self.node("model", "model", raw=canonical_json(SuppliedState()), fit_evidence=fit,
                           dependencies=(self.dep("fold", fold_node), self.dep("labels", label, "fit_label", ("label",)),
                                         self.dep("training", train_reads)))
        request = ReadRequest("sample-eval", 100, 102, "OOF" if mode == "OOF" else "final", "Row.v1", "probability",
                              self.target, 100, 130, "day-1", fold_node.id)
        binding = ReadBinding("x", source.id, "x", request)
        reads = self.node("prediction-reads", "read_manifest",
                          read_manifest=ReadManifest(self.namespace, (binding,), (ReadRecord(binding, source.row_evidence[0]),), ()),
                          dependencies=(self.dep("x", source, "value", ("x",)), self.dep("fold", fold_node)))
        p = PredictionEvidence("sample-eval", self.target, 100, 130, 100, 102, 100, model.id, reads.id, mode)
        prediction = self.node("prediction", "oof_prediction" if mode == "OOF" else "final_prediction",
                               rows=(replace(self.row(value=.7,valid_until=min(130,source_until)),availability_basis="derived"),), prediction_evidence=p,
                               dependencies=(self.dep("model", model), self.dep("reads", reads)))
        return {n.logical_key: n for n in (train, label, source, fold_node, train_reads, model, reads, prediction)}, request


def supplied_fixture(model_kind="binary", mode="OOF", value=3):
    from trading_research.research.models import BinaryModel, FrequencyModel
    from trading_research.research.calibration import CalibratedBinary
    from trading_research.research.folds import FittedArtifact
    if model_kind=="frequency":
        f,finite_nodes,template=normalization_fixture(evaluation=value)
        nodes={n.logical_key:n for n in finite_nodes if n.id!=template.id}
        fold=next(n for n in finite_nodes if n.kind=="fold")
        artifact=FittedArtifact("frequency","model",fold.fold_evidence.fold.version,90,frozenset({"train-a","train-b"}),frozenset({"day1","day2"}),90,())
        state=FrequencyModel("frequency",("x",),((2.,),),(((0,),0,1),((1,),1,1)),.5,1.,"uniform",artifact,f.target.sha256,"supplied-reads")
        execution=replace(f.execution,configuration_json=canonical_json({"input_columns":["x"]}))
        model=f.node("frequency","model",raw=canonical_json(state),fit_evidence=template.fit_evidence,dependencies=template.dependencies,execution=execution)
        nodes["frequency"]=model
        q=ReadRequest("sample-eval",100,102,mode,"Row.v1","probability",f.target,100,130,"evaluation" if mode=="OOF" else None,fold.id if mode=="OOF" else None)
        source=nodes["evaluation"]
        return f,nodes,q,state,model,(ReadBinding("x",source.id,"x",q),)
    f=Fixture();nodes,q=f.complete(mode)
    nodes.pop("prediction");nodes.pop("prediction-reads")
    if mode=="final":q=replace(q,date_group=None,fold_node_id=None)
    template=nodes.pop("model");fit=replace(template.fit_evidence,actual_fit_completion_at=90)
    nodes["source"]=f.source(value=value)
    artifact=FittedArtifact("supplied","model",nodes["fold"].fold_evidence.fold.version,90,frozenset({"train-0"}),frozenset({"day-0"}),51,())
    def execution(columns, refs=()):
        return replace(f.execution,configuration_json=canonical_json({"input_columns":columns}),transform_state_refs=refs)
    def binary(key, columns=("x",)):
        local_fit=fit; local_dependencies=template.dependencies
        if columns!=("x",):
            binding=nodes["training-reads"].read_manifest.bindings[0]
            binding=replace(binding,column=columns[0])
            manifest=f.node(key+"-training-reads","read_manifest",read_manifest=ReadManifest(f.namespace,(binding,),(ReadRecord(binding,nodes["training-x"].row_evidence[0]),),()),
                            dependencies=(f.dep(columns[0],nodes["training-x"],"value",("x",)),f.dep("fold",nodes["fold"])))
            nodes[manifest.logical_key]=manifest
            local_fit=replace(fit,actual_training_read_manifests=(manifest.id,))
            local_dependencies=tuple(replace(d,source_id=manifest.id) if d.source_id==nodes["training-reads"].id else d for d in template.dependencies)
        state=BinaryModel(key,columns,(1.,),(1.,),0.,(1.,),0.,0,0.,0.,"supplied-reads",f.target.sha256,())
        raw=canonical_json({"means":state.means,"scales":state.scales})
        transform=f.node(key+"-scaler","transform",raw=raw,fit_evidence=local_fit,dependencies=local_dependencies,
                         execution=execution(columns))
        nodes[transform.logical_key]=transform
        model=f.node(key,"model",raw=canonical_json(state),fit_evidence=local_fit,
                     dependencies=(*local_dependencies,f.dep("scaler",transform)),
                     execution=execution(columns,(("standardization",transform.payload_ref),)))
        nodes[key]=model
        return state,model
    if model_kind=="frequency":
        state=FrequencyModel("frequency",("x",),((2.,),),(((0,),0,1),((1,),1,1)),.5,1.,"uniform",artifact,f.target.sha256,"supplied-reads")
        model=f.node("frequency","model",raw=canonical_json(state),fit_evidence=fit,dependencies=template.dependencies,execution=execution(("x",)))
        nodes[model.logical_key]=model
    else:
        state,model=binary("base")
        if model_kind=="calibrated":
            calibration,calnode=binary("calibration",("raw_logit",))
            state=CalibratedBinary("calibrated",state,calibration,artifact,.01,(),"supplied-oof-cohort")
            model=f.node("calibrated","calibrator",raw=canonical_json(state),fit_evidence=fit,
                         dependencies=(*template.dependencies,f.dep("base",model),f.dep("calibration",calnode)),execution=execution(("x",)))
            nodes[model.logical_key]=model
    binding=ReadBinding("x",nodes["source"].id,"x",q)
    return f,nodes,q,state,model,(binding,)


def three_stage_fixture(variant=None):
    """Actual retained scaler -> model -> OOF row -> calibrator populations."""
    f=Fixture();nodes={}
    def add(node):nodes[node.logical_key]=node;return node
    population=(Sample("train-0","d0",10,70,60,f.target.sha256),
                Sample("cal-row","d1",88,90,89,f.target.sha256),
                Sample("eval","d2",100,131,130,f.target.sha256))
    source0=add(f.source("train-source",row_id="train-0",value=1,observed=9,known=10))
    source1=add(f.source("cal-source",row_id="cal-row",value=3,observed=87,known=88))
    label0=add(f.node("label0","label",rows=(f.row(row_id="train-0",column="label",observed=60,known=70,value=1),),
                      label_targets=(LabelTarget("train-0",f.target,10,60),)))
    label1=add(f.node("label1","label",rows=(f.row(row_id="cal-row",column="label",observed=89,known=90,value=1),),
                      label_targets=(LabelTarget("cal-row",f.target,88,89),)))
    def foldnode(key,at,start,end,training_start=None,routes=()):
        fold=chronological_fold(population,id=key,fit_at=at,evaluation_start=start,evaluation_end=end,training_start=training_start)
        return add(f.node(key,"fold",fold_evidence=ValidatedFoldEvidence(population,fold,routes)))
    def reads(key,source,fold,row,cut,group,*,target=False):
        q=ReadRequest(row,cut,cut,"fit_feature","Row.v1","probability",f.target if target else None,
                      cut if target else None,89 if target else None,group,fold.id)
        b=ReadBinding("x",source.id,"x",q)
        return add(f.node(key,"read_manifest",read_manifest=ReadManifest(f.namespace,(b,),(ReadRecord(b,next(r for r in source.row_evidence if r.row_id==row)),),()),
                          dependencies=(f.dep("x",source,"value",("x",)),f.dep("fold",fold))))
    def fitted(key,kind,fold,read,label,row,group,at,upstream=()):
        fit=FitEvidence(fold.id,at,101 if variant==key+"-future" else at,(row,),("d2",) if variant==key+"-group" else (group,),
                        (LabelEvidence(row,label.id,"label",f.target),),(read.id,),f.target)
        if variant==key+"-sample":fit=replace(fit,training_sample_ids=("eval",))
        if variant==key+"-empty":fit=replace(fit,training_sample_ids=(),training_groups=())
        return add(f.node(key,kind,fit_evidence=fit,dependencies=(f.dep("fold",fold),f.dep("labels",label,"fit_label",("label",)),
            f.dep("training",read),*(f.dep(n.logical_key,n) for n in upstream))))
    sf=foldnode("scaler-fold",80,88,90)
    sr=reads("scaler-reads",source0,sf,"train-0",10,"d0")
    scaler=fitted("scaler","transform",sf,sr,label0,"train-0","d0",80)
    mf=foldnode("model-fold",85,88,90,routes=((scaler.id,sf.id),))
    mr=reads("model-reads",source0,mf,"train-0",10,"d0")
    model=fitted("model","model",mf,mr,label0,"train-0","d0",85,(scaler,))
    mode="final" if variant=="final-substitution" else "OOF"
    pq=ReadRequest("cal-row",88,88,mode,"Row.v1","probability",f.target,88,89,"d1",mf.id)
    pb=ReadBinding("x",source1.id,"x",pq)
    pr=add(f.node("base-prediction-reads","read_manifest",read_manifest=ReadManifest(f.namespace,(pb,),(ReadRecord(pb,source1.row_evidence[0]),),()),
                  dependencies=(f.dep("x",source1,"value",("x",)),f.dep("fold",mf))))
    pe=PredictionEvidence("cal-row",f.target,88,89,88,88,88,model.id,pr.id,mode)
    prediction=add(f.node("base-oof","final_prediction" if mode=="final" else "oof_prediction",rows=(replace(f.row(row_id="cal-row",observed=87,known=88,value=.7,valid_until=89),availability_basis="derived"),),
                         prediction_evidence=pe,dependencies=(f.dep("fit",model),f.dep("reads",pr))))
    cf=foldnode("calibrator-fold",90,100,140,training_start=80,routes=((scaler.id,sf.id),(model.id,mf.id)))
    cr=reads("calibrator-reads",prediction,cf,"cal-row",88,"d1",target=True)
    calibrator=fitted("calibrator","calibrator",cf,cr,label1,"cal-row","d1",90,(model,))
    q=ReadRequest("eval",100,100,"OOF","Row.v1","probability",f.target,100,130,"d2",cf.id)
    return f,nodes,calibrator,q


def normalization_fixture(evaluation=3, groups=("day1","day2"), target_name=b"first-passage-v1", late_label=False):
    f=Fixture();f.target=f.keep(target_name,"target")
    ids=("train-a","train-b")
    population=(Sample(ids[0],groups[0],20,80,60,f.target.sha256),Sample(ids[1],groups[1],40,90,70,f.target.sha256),
                Sample("sample-eval","evaluation",100,131,130,f.target.sha256))
    fold=chronological_fold(population,id="normalization-fold",fit_at=90,evaluation_start=100,evaluation_end=140)
    fn=f.node("fold","fold",fold_evidence=ValidatedFoldEvidence(population,fold))
    source=f.node("training","source",rows=(f.row(row_id=ids[0],value=0,observed=19,known=20),f.row(row_id=ids[1],value=2,observed=39,known=40)))
    labels=f.node("labels","label",rows=(f.row(row_id=ids[0],column="label",value=0,observed=60,known=80),
                                            f.row(row_id=ids[1],column="label",value=1,observed=70,known=91 if late_label else 90)),
                  label_targets=(LabelTarget(ids[0],f.target,20,60),LabelTarget(ids[1],f.target,40,70)))
    manifests=[]
    for row,group in zip(source.row_evidence,groups):
        request=ReadRequest(row.row_id,row.input_known_at,row.input_known_at,"fit_feature","Row.v1","probability",date_group=group,fold_node_id=fn.id)
        binding=ReadBinding("x",source.id,"x",request)
        manifests.append(f.node("reads-"+row.row_id,"read_manifest",read_manifest=ReadManifest(f.namespace,(binding,),(ReadRecord(binding,row),),()),
                               dependencies=(f.dep("x",source,"value",("x",)),f.dep("fold",fn))))
    fit=FitEvidence(fn.id,90,90,ids,groups,tuple(LabelEvidence(i,labels.id,"label",f.target) for i in ids),tuple(m.id for m in manifests),f.target)
    transform=f.node("normalization","transform",raw=canonical_json({"means":[1.],"scales":[1.]}),fit_evidence=fit,
                     dependencies=(f.dep("fold",fn),f.dep("labels",labels,"fit_label",("label",)),*(f.dep(m.logical_key,m) for m in manifests)))
    evaluation_source=f.source("evaluation",value=evaluation)
    return f,(fn,source,labels,*manifests,transform,evaluation_source),transform


def _death_worker(root, namespace, nodes, roots, payloads, point):
    SemanticArtifactStore(Path(root), namespace).commit("run-new", roots, nodes, payloads, _death_point=point)


class ArtifactGraphTests(unittest.TestCase):
    def test_f11_01_typed_identity_and_immutable_configuration(self):
        f = Fixture(); source = f.source()
        self.assertEqual(canonical_json({"b": 2, "a": 1}), CASES["F11-01"]["expected"]["equivalent_config_canonical_json"].encode())
        self.assertEqual(source.id, replace(source).id)
        nf,nodes,transform=normalization_fixture()
        fit=transform.fit_evidence
        reordered=replace(fit,training_sample_ids=tuple(reversed(fit.training_sample_ids)),training_groups=tuple(reversed(fit.training_groups)),
                          training_label_refs=tuple(reversed(fit.training_label_refs)),actual_training_read_manifests=tuple(reversed(fit.actual_training_read_manifests)))
        self.assertEqual(replace(transform,fit_evidence=reordered,dependencies=tuple(reversed(transform.dependencies))).id,transform.id)
        fold_node=next(n for n in nodes if n.kind=="fold")
        self.assertEqual(replace(fold_node,fold_evidence=replace(fold_node.fold_evidence,population=tuple(reversed(fold_node.fold_evidence.population)))).id,fold_node.id)
        with self.assertRaises(AttributeError):transform.execution.__dict__["configuration_json"]=b"{}"

        for changed in (replace(source, namespace="other"), replace(source, unit="rank"),
                        replace(source, definition_ref=f.keep(b"definition-v2")), f.source(version="x-v2"), f.source(value=4)):
            self.assertNotEqual(source.id, changed.id)
        for thunk in (lambda: f.row(known=True), lambda: replace(source, dependencies=[]),
                      lambda: replace(source, namespace=""), lambda: replace(source.row_evidence[0],value_json=b"NaN"),
                      lambda: replace(source, dependencies=(f.dep("x", source), f.dep("x", source)))):
            with self.assertRaises(ContractError) as caught: thunk()
            self.assertIs(type(caught.exception),ContractError)
        with self.assertRaises(AttributeError): source.namespace = "other"
        with self.assertRaises(TypeError): source.row_evidence[0].value_json[0] = 0
        wrong = replace(source, payload_ref=replace(source.payload_ref, size_bytes=source.payload_ref.size_bytes+1))
        with self.assertRaises(IntegrityError): f.closure((wrong,))
        with tempfile.TemporaryDirectory() as root:
            store = SemanticArtifactStore(root, f.namespace)
            ref = store.commit("key", (source.id,), (source,), f.payloads)
            with self.assertRaises(AttributeError): store.namespace = "other"
            with self.assertRaises(AttributeError): del store.limits
            with self.assertRaises(ContractError): store.resolve(replace(ref, namespace="other"), source.id, "x", ReadRequest("sample-eval",100,100,"input","Row.v1","probability"))

    def test_f11_02_roles_share_bytes_but_not_identity(self):
        f = Fixture(); nodes, request = f.complete(); p = nodes["prediction"]
        final = replace(p, kind="final_prediction", prediction_evidence=replace(p.prediction_evidence, mode="final"))
        label = f.node("prediction-label", "label", rows=(replace(p.row_evidence[0],observed_at=130,input_known_at=131),))
        self.assertEqual(len({n.payload_ref.sha256 for n in (p,final,label)}), 1)
        self.assertEqual(len({n.id for n in (p,final,label)}), 3)
        with tempfile.TemporaryDirectory() as root:
            store = SemanticArtifactStore(root,f.namespace)
            ref = store.commit("oof",(p.id,),tuple(nodes.values()),f.payloads)
            self.assertEqual(store.resolve(ref,p.id,"x",request).value_json,b"0.7")
            final_nodes, final_request = f.complete("final")
            fp = final_nodes["prediction"]
            fr = store.commit("final", (fp.id,), tuple(final_nodes.values()), f.payloads)
            lr = store.commit("label", (label.id,), (label,), f.payloads)
            for ref_, bad in ((fr,fp),(lr,label)):
                with self.assertRaises(ContractError):
                    store.resolve(ref_,bad.id,"x",replace(request,purpose="OOF"))
            self.assertEqual(store.resolve(fr,fp.id,"x",final_request).value_json,b"0.7")
            self.assertGreater(store.storage_accounting()["manifest_bytes"],0)

    def test_f11_03_original_completion_and_expiry(self):
        f=Fixture();nodes,request=f.complete();p=nodes["prediction"]
        expected=CASES["F11-03"]["expected"]
        self.assertEqual(p.prediction_evidence.known_at,expected["published_known_at"])
        with tempfile.TemporaryDirectory() as root:
            store=SemanticArtifactStore(root,f.namespace);ref=store.commit("p",(p.id,),tuple(nodes.values()),f.payloads)
            actual=[]
            for at in CASES["F11-03"]["inputs"]["query_times"]:
                try:store.resolve(ref,p.id,"x",replace(request,assembled_at=at));actual.append(True)
                except DependencyUnavailable:actual.append(False)
            self.assertEqual(actual,expected["query_usable"])
            self.assertEqual(store.resolve(ref,p.id,"x",replace(request,purpose="audit",assembled_at=130)).value_json,b"0.7")
            row=replace(p.row_evidence[0],valid_until=120)
            shorter=f.node("prediction",p.kind,rows=(row,),prediction_evidence=p.prediction_evidence,dependencies=p.dependencies)
            revised={**nodes,"prediction":shorter};r2=store.commit("short",(shorter.id,),tuple(revised.values()),f.payloads)
            store.resolve(r2,shorter.id,"x",replace(request,assembled_at=119))
            with self.assertRaises(DependencyUnavailable):store.resolve(r2,shorter.id,"x",replace(request,assembled_at=120))
        f=Fixture();inherited,request=f.complete(source_until=120);prediction=inherited["prediction"]
        self.assertEqual(prediction.row_evidence[0].valid_until,inherited["source"].row_evidence[0].valid_until)
        with tempfile.TemporaryDirectory() as root:
            store=SemanticArtifactStore(root,f.namespace);ref=store.commit("inherited",(prediction.id,),tuple(inherited.values()),f.payloads)
            store.resolve(ref,prediction.id,"x",replace(request,assembled_at=119))
            with self.assertRaises(DependencyUnavailable):store.resolve(ref,prediction.id,"x",replace(request,assembled_at=120))
            row=replace(prediction.row_evidence[0],valid_until=130)
            invalid=f.node("prediction",prediction.kind,rows=(row,),prediction_evidence=prediction.prediction_evidence,dependencies=prediction.dependencies)
            with self.assertRaises(ContractError):f.closure(tuple(n for k,n in inherited.items() if k!="prediction")+(invalid,))
        self.assertFalse(literal.prediction_available({"target_end":130,"input_known_at":100,"actual_completion_at":102},120,120))
        audit=InputAudit(frozenset({"x"}),{"x":InputValue("x","v",15,b"1")},cut=20,fold_version="f")
        audit.read("x")
        with self.assertRaises(AttributeError):audit.cut=10
        self.assertEqual(audit.manifest()["decision_cut"],20)

    def test_f11_04_required_optional_actual_reads(self):
        f=Fixture();source=f.source();q=ReadRequest("sample-eval",100,100,"input","Row.v1","probability")
        bindings=tuple(ReadBinding(c,source.id,"x",q,c!="optional_z",() if c!="optional_z" else ("source unavailable",)) for c in ("price","rich_context","optional_z"))
        with tempfile.TemporaryDirectory() as root:
            store=SemanticArtifactStore(root,f.namespace);ref=store.commit("source",(source.id,),(source,),f.payloads)
            session=ReadSession(store,ref,bindings);session.read("price")
            with self.assertRaises(ContractError):session.seal()
            with self.assertRaises(ContractError):session.read("future_label")
            with self.assertRaises(AttributeError):session.bindings=()
            session.read("price");session.read("rich_context");session.omit_optional("optional_z","source unavailable")
            m=session.seal();self.assertEqual([r.binding.column for r in m.reads],CASES["F11-04"]["expected"]["second_actual_reads"])
            self.assertEqual([list(v) for v in m.omissions],CASES["F11-04"]["expected"]["second_optional_omissions"])
            other=ReadSession(store,ref,bindings)
            for b in bindings:other.read(b.column)
            self.assertEqual([r.binding.column for r in other.seal().reads],CASES["F11-04"]["expected"]["third_actual_reads"])
            self.assertEqual(other.seal().omissions,())

    def test_f11_05_future_suffix_and_old_commit(self):
        f=Fixture();old=f.source(value=1,observed=8,known=9,version="v1");new=f.source(value=1,observed=8,known=30,version="v2")
        with tempfile.TemporaryDirectory() as root:
            store=SemanticArtifactStore(root,f.namespace);a=store.commit("old",(old.id,),(old,),f.payloads);b=store.commit("new",(new.id,),(new,),f.payloads)
            q=ReadRequest("sample-eval",10,10,"input","Row.v1","probability")
            self.assertEqual(store.resolve(a,old.id,"x",q).value_json,b"1")
            with self.assertRaises(ContractError):store.resolve(b,new.id,"x",q)
            self.assertEqual(store.read_commit("old").reference,a)
            self.assertNotEqual(a.manifest_ref,b.manifest_ref)
        audit=InputAudit(frozenset({"x"}),{"x":InputValue("x","v",11,b"999")},cut=10,fold_version="f")
        with self.assertRaises(ContractError):audit.read("x")

    def test_f11_06_complete_dag_stage_and_corruption(self):
        case=CASES["F11-06"];edges=case["inputs"]["edges"]
        shape=literal.closure(edges,case["inputs"]["roots"])
        self.assertEqual(shape,{"nodes":case["expected"]["closure_sorted"],"edges":7,"depth":5})
        f=Fixture();built={}
        def build(k):
            if k not in built:built[k]=f.node(k,dependencies=tuple(f.dep(d,build(d)) for d in edges[k]))
            return built[k]
        root=build("prediction");closure=f.closure(tuple(built.values()),(root,))
        self.assertEqual((len(closure.nodes),closure.edges,closure.depth),(7,7,5))
        with self.assertRaises(ContractError):f.closure(tuple(n for k,n in built.items() if k!="scaler"),(root,))
        with self.assertRaises(ContractError):f.closure((*built.values(),f.node("extra")),(root,))
        with self.assertRaises(ValueError):literal.closure({**edges,"scaler":["model"]},["prediction"])
        with tempfile.TemporaryDirectory() as directory:
            store=SemanticArtifactStore(directory,f.namespace);store.commit("x",(root.id,),tuple(built.values()),f.payloads)
            (store.root/"blobs"/root.payload_ref.sha256[:2]/root.payload_ref.sha256).write_bytes(b"bad")
            with self.assertRaises(IntegrityError):store.read_commit("x")

    def test_f11_07_grouped_fold_rederivation(self):
        c=CASES["F11-07"];i=c["inputs"];e=c["expected"]
        rows=tuple(Sample(s["id"],s["group"],s["decision"],s["label_known"],s["dependency_end"],"target") for s in i["samples"])
        fold=chronological_fold(rows,id="fold",fit_at=i["fit_at"],evaluation_start=i["evaluation"][0],evaluation_end=i["evaluation"][1],embargo_ns=i["embargo"])
        ref=literal.fold(i["samples"],i["fit_at"],*i["evaluation"],i["embargo"])
        self.assertEqual(ref,{k:e[k] for k in ("training_ids","evaluation_ids","purged")})
        self.assertEqual(list(fold.training_ids),e["training_ids"]);self.assertEqual(list(fold.evaluation_ids),e["evaluation_ids"])
        self.assertEqual([list(p) for p in fold.purged],e["purged"])
        self.assertEqual(_decode(_encode(fold)),fold)
        for thunk in (lambda:chronological_fold(rows,id="bad",fit_at=20,evaluation_start=22,evaluation_end=40),
                      lambda:validate_fold_population(rows,replace(fold,training_ids=())),
                      lambda:validate_fold_population(rows,replace(fold,purged=())),lambda:replace(fold,training_ids=[])):
            with self.assertRaises(ContractError):thunk()

    def test_f11_08_ancestral_oof_exclusion(self):
        f=Fixture();nodes,q=f.complete();model=nodes["model"];closure=f.closure(tuple(nodes.values()),(nodes["prediction"],))
        self.assertEqual(validate_oof_producer(q,model.id,closure),(model.id,))
        for fit in (replace(model.fit_evidence,training_sample_ids=("sample-eval",)),replace(model.fit_evidence,training_groups=("day-1",)),
                    replace(model.fit_evidence,training_sample_ids=(),training_groups=())):
            changed=replace(model,fit_evidence=fit)
            with self.assertRaises(ContractError):f.closure(tuple(n for k,n in nodes.items() if k not in {"model","prediction"})+(changed,))
        future=replace(model,fit_evidence=replace(model.fit_evidence,actual_fit_completion_at=101))
        valid_fit=f.closure(tuple(n for k,n in nodes.items() if k not in {"model","prediction"})+(future,))
        with self.assertRaises(ContractError):validate_oof_producer(q,future.id,valid_fit)
        for bad in (replace(q,row_id="train-0",date_group="day-0",decision_cut=20,assembled_at=100,target_start=20,target_end=50),
                    replace(q,target_definition_ref=None,target_start=None,target_end=None),replace(q,target_end=129),
                    replace(q,date_group="day-other")):
            with self.assertRaises(ContractError):validate_oof_producer(bad,model.id,closure)
        from trading_research.operations.artifact_graph import ClosureManifest
        forged=ClosureManifest(f.namespace,closure.roots,closure.nodes,closure.topological_ids,closure.edges,closure.depth)
        with self.assertRaises(ContractError):validate_oof_producer(q,model.id,forged)
        primitive={k:{"fold":"f","completion":t,"training_ids":[],"groups":g} for k,t,g in zip(("scaler","model","calibrator"),(80,85,90),(["d0"],["d0"],["d1"]))}
        self.assertEqual(literal.oof(primitive,"eval","d2",100,"f",{}),CASES["F11-08"]["expected"]["valid_closure_sorted"])
        for key in primitive:
            bad={**primitive,key:{**primitive[key],"groups":["d2"]}}
            with self.assertRaises(ValueError):literal.oof(bad,"eval","d2",100,"f",{})

    def test_f11_09_exact_target_unit_endpoints(self):
        f=Fixture();nodes,q=f.complete();p=nodes["prediction"]
        with tempfile.TemporaryDirectory() as root:
            store=SemanticArtifactStore(root,f.namespace);ref=store.commit("p",(p.id,),tuple(nodes.values()),f.payloads)
            store.resolve(ref,p.id,"x",q)
            for bad in (replace(q,target_definition_ref=f.keep(b"terminal-v1")),replace(q,target_end=160),replace(q,unit="rank"),replace(q,target_start=102,target_end=132)):
                with self.assertRaises(ContractError):store.resolve(ref,p.id,"x",bad)

    def test_f11_10_predeclared_routes_not_self_authorization(self):
        f=Fixture();nodes,q=f.complete();base=nodes["model"];old_fold=nodes["fold"]
        renamed=replace(old_fold.fold_evidence.fold,id="fold-2")
        other=f.node("request-fold","fold",fold_evidence=ValidatedFoldEvidence(old_fold.fold_evidence.population,renamed,((base.id,old_fold.id),)))
        closure=f.closure((*nodes.values(),other));request=replace(q,fold_node_id=other.id)
        self.assertEqual(validate_oof_producer(request,base.id,closure),(base.id,))
        for routes in ((),((base.id,"f3"),)):
            bad=replace(other,fold_evidence=replace(other.fold_evidence,declared_routes=routes))
            badclosure=f.closure((*nodes.values(),bad))
            with self.assertRaises(ContractError):validate_oof_producer(replace(q,fold_node_id=bad.id),base.id,badclosure)
        ancestor={"earlier-model":{"fold":"f1","completion":90,"training_ids":[],"groups":["d0"]}}
        self.assertEqual(literal.oof(ancestor,"eval","d2",100,"f2",{"earlier-model":"f1"}),["earlier-model"])
        with self.assertRaises(ValueError):literal.oof(ancestor,"eval","d2",100,"f2",{})

    def test_f11_11_training_only_state_and_fit_clock(self):
        c=CASES["F11-11"];train=[Fraction(*x) for x in c["inputs"]["training_values"]]
        mean=sum(train)/len(train);variance=sum((x-mean)**2 for x in train)/len(train)
        self.assertEqual(mean,Fraction(1));self.assertEqual(variance,Fraction(1))
        f=Fixture();nodes,q=f.complete();original=nodes["model"]
        future=f.source(value=999)
        self.assertEqual(original.payload_ref,f.keep(canonical_json(SuppliedState())))
        self.assertNotEqual(nodes["source"].id,future.id)
        f1,n1,t1=normalization_fixture();f2,n2,t2=normalization_fixture(evaluation=1000000)
        c1=f1.closure(n1);c2=f2.closure(n2)
        self.assertEqual(training_standardization(c1,t1.id,("x",)),((1.,),(1.,)))
        self.assertEqual(training_standardization(c2,t2.id,("x",)),((1.,),(1.,)))
        self.assertEqual(t1.id,t2.id);self.assertEqual(t1.payload_ref,t2.payload_ref)
        late,late_nodes,late_fit=normalization_fixture(late_label=True)
        with self.assertRaises(ContractError):late.closure(late_nodes)
        with self.assertRaises(ContractError):replace(t1.fit_evidence,actual_fit_completion_at=89)

        self.assertEqual(original.fit_evidence.training_sample_ids,("train-0",))
        early=replace(q,decision_cut=91,assembled_at=91)
        with self.assertRaises(ContractError):validate_oof_producer(early,original.id,f.closure(tuple(nodes.values())))

    def test_f11_12_execution_identity_and_commit_alias(self):
        f=Fixture();source=f.source();base=f.node("computed",dependencies=(f.dep("source",source),),raw=b"5")
        settings=json.loads(f.execution.numerical_settings_json)
        versions=[replace(base,execution=replace(f.execution,code_ref=f.keep(b"code-v2"))),
                  replace(base,execution=replace(f.execution,configuration_json=canonical_json({"window":3})))]
        for key,value in (("precision","float32"),("rounding","down"),("seed",2),("thread_count",2)):
            versions.append(replace(base,execution=replace(f.execution,numerical_settings_json=canonical_json({**settings,key:value}))))
        self.assertEqual(len({n.id for n in (base,*versions)}),len(versions)+1)
        fit_fixture,fit_nodes,fit_node=normalization_fixture()
        fit_fixture.closure(fit_nodes)
        changed_groups,group_nodes,group_fit=normalization_fixture(groups=("other1","other2"));changed_groups.closure(group_nodes)
        changed_target,target_nodes,target_fit=normalization_fixture(target_name=b"target-v2");changed_target.closure(target_nodes)
        self.assertEqual(fit_node.payload_ref,group_fit.payload_ref);self.assertEqual(fit_node.payload_ref,target_fit.payload_ref)
        self.assertNotEqual(fit_node.id,group_fit.id);self.assertNotEqual(fit_node.id,target_fit.id)
        state_ref=fit_fixture.keep(b"changed-scaler-state")
        version=replace(fit_node,execution=replace(fit_node.execution,transform_state_refs=(("scaler",state_ref),)))
        fit_fixture.closure(tuple(n for n in fit_nodes if n.id!=fit_node.id)+(version,))
        self.assertNotEqual(fit_node.id,version.id)

        with tempfile.TemporaryDirectory() as root:
            store=SemanticArtifactStore(root,f.namespace);old=store.commit("same",(base.id,),(source,base),f.payloads)
            with self.assertRaises(ContractError):store.commit("same",(versions[0].id,),(source,versions[0]),f.payloads)
            store.commit("new",(versions[0].id,),(source,versions[0]),f.payloads)
            self.assertEqual(store.read_commit("same").reference,old)

    def _rebuild_fixture(self,edges,seed):
        f=Fixture()
        def build(changed):
            nodes={}
            def node(k):
                if k not in nodes:
                    deps=tuple(f.dep(d,node(d)) for d in edges[k])
                    if not edges[k] and k == seed:
                        nodes[k]=f.source(k,value=5,version="v2" if changed else "v1")
                    else:
                        nodes[k]=f.node(k,dependencies=deps,raw=canonical_json({"state":k}))
                return nodes[k]
            for k in edges:node(k)
            return nodes
        old=build(False);new=build(True)
        plan=plan_rebuild(f.closure(tuple(old.values())),tuple(new.values()),(seed,),payloads=f.payloads)
        return f,old,new,plan

    def test_f11_13_same_value_version_invalidation(self):
        c=CASES["F11-13"];edges={**c["inputs"]["edges"],"source":[]}
        f,old,new,plan=self._rebuild_fixture(edges,"source")
        self.assertEqual(list(plan.rebuilt_keys),c["expected"]["changed_keys"]);self.assertEqual(list(plan.reused_keys),c["expected"]["reused_keys"])
        self.assertEqual(literal.affected(edges,["source"]),(list(plan.rebuilt_keys),list(plan.reused_keys)))
        paths=dict(plan.first_change_paths)
        for k,path in c["expected"]["invalidation_paths"].items():self.assertEqual(list(paths[k]),path)
        for k in plan.rebuilt_keys:self.assertNotEqual(old[k].id,new[k].id)
        for k in plan.reused_keys:self.assertEqual(old[k].id,new[k].id)

    def test_f11_14_calibration_cohort_targeted_rebuild(self):
        c=CASES["F11-14"];edges=c["inputs"]["edges"]
        _,old,new,plan=self._rebuild_fixture(edges,"calibration-cohort")
        self.assertEqual(list(plan.rebuilt_keys),c["expected"]["rebuilt_keys"]);self.assertEqual(list(plan.reused_keys),c["expected"]["reused_keys"])
        self.assertEqual(old["base"].id,new["base"].id)
        eligible,eligible_nodes,transform=normalization_fixture(groups=tuple(c["inputs"]["old_cohort"]))
        calibrator=replace(transform,logical_key="eligible-calibrator",kind="calibrator")
        closure=eligible.closure(tuple(n for n in eligible_nodes if n.id!=transform.id)+(calibrator,))
        self.assertEqual(set(calibrator.fit_evidence.training_groups),set(c["inputs"]["old_cohort"]))
        self.assertEqual(len(calibrator.fit_evidence.training_label_refs),2)
        taken_only=replace(calibrator,fit_evidence=replace(calibrator.fit_evidence,training_sample_ids=("train-a",),training_groups=(c["inputs"]["old_cohort"][0],),training_label_refs=calibrator.fit_evidence.training_label_refs[:1]))
        with self.assertRaises(ContractError):eligible.closure(tuple(n for n in eligible_nodes if n.id!=transform.id)+(taken_only,))
        newer,newer_nodes,newer_transform=normalization_fixture(groups=tuple(c["inputs"]["new_cohort"]))
        newer.closure(newer_nodes)
        self.assertNotEqual(transform.id,newer_transform.id)

        f=Fixture();nodes,_=f.complete();model=nodes["model"]
        omitted=replace(model,fit_evidence=replace(model.fit_evidence,training_label_refs=()))
        with self.assertRaises(ContractError):f.closure(tuple(n for k,n in nodes.items() if k not in {"model","prediction"})+(omitted,))

    def test_f11_15_zero_effect_and_provenance_read(self):
        f=Fixture();x=f.source("x",value=2);z=f.source("z",column="z",value=7);q=ReadRequest("sample-eval",100,100,"input","Row.v1","probability")
        with tempfile.TemporaryDirectory() as root:
            store=SemanticArtifactStore(root,f.namespace);ref=store.commit("input",(x.id,z.id),(x,z),f.payloads)
            session=ReadSession(store,ref,(ReadBinding("x",x.id,"x",q),ReadBinding("z",z.id,"z",q)))
            xv=json.loads(session.read("x"))
            with self.assertRaises(ContractError):session.seal()
            zv=json.loads(session.read("z"));self.assertEqual(xv+0*zv,Fraction(*CASES["F11-15"]["expected"]["output"]))
            self.assertEqual([r.binding.column for r in session.seal().reads],["x","z"])
        _,_,_,plan=self._rebuild_fixture({"consumer":["calibration-definition"],"calibration-definition":[]},"calibration-definition")
        self.assertEqual(plan.rebuilt_keys,("calibration-definition","consumer"))

    def test_f11_16_actual_parameter_and_column_attestation(self):
        f=Fixture();nodes,_=f.complete();m=nodes["model"];manifest=nodes["prediction-reads"].read_manifest;state=SuppliedState()
        self.assertEqual(attest_state(state,m,f.payloads,("x",),manifest),m.id)
        self.assertEqual((3-state.mean)/state.scale*state.coefficient,2)
        for bad in (replace(state,coefficient=2),replace(state,mean=2),replace(state,columns=("y",)),replace(state,scale=2)):
            with self.assertRaises(IntegrityError):attest_state(bad,m,f.payloads,bad.columns,manifest)
        with self.assertRaises(ContractError):attest_state(state,m,f.payloads,("y",),manifest)

    def test_f11_17_checkpoint_restore_detached_and_config(self):
        f=Fixture();n=f.node("checkpoint",raw=b'{"count":3}')
        with tempfile.TemporaryDirectory() as root:
            store=SemanticArtifactStore(root,f.namespace);ref=store.commit("checkpoint",(n.id,),(n,),f.payloads)
            reopened=SemanticArtifactStore(root,f.namespace);self.assertEqual(reopened.read_commit("checkpoint").reference,ref)
            state=json.loads(reopened._blob_read(n.payload_ref,reopened.limits.max_node_payload_bytes));state["count"]=4
            self.assertEqual(json.loads(reopened._blob_read(n.payload_ref,reopened.limits.max_node_payload_bytes)),{"count":3})
            with self.assertRaises(IntegrityError):SemanticArtifactStore(root,"changed")
            with self.assertRaises(IntegrityError):SemanticArtifactStore(root,f.namespace,replace(Limits(),max_commits=255))
            with self.assertRaises(DependencyUnavailable):store.read_commit("missing")
            store._blobs.path(n.payload_ref).write_bytes(b"corrupt checkpoint")
            with self.assertRaises(IntegrityError):store.read_commit("checkpoint")
        checkpoint={"cache_key":"k","state":{"count":3}};copy=compatible_checkpoint(checkpoint,"k");copy["count"]=4
        self.assertEqual(checkpoint["state"],{"count":3})

    def test_f11_18_actual_child_process_death(self):
        f=Fixture();old=f.source("old");new=f.source("new",value=4)
        for point,code in (("before_pointer",23),("after_pointer",24)):
            with tempfile.TemporaryDirectory() as root:
                store=SemanticArtifactStore(root,f.namespace);oldref=store.commit("run-old",(old.id,),(old,),f.payloads)
                child=multiprocessing.get_context("fork").Process(target=_death_worker,args=(root,f.namespace,(new,),(new.id,),f.payloads,point))
                child.start();child.join(10)
                if child.is_alive():child.kill();child.join();self.fail("bounded death worker hung")
                self.assertEqual(child.exitcode,code)
                restarted=SemanticArtifactStore(root,f.namespace);self.assertEqual(restarted.read_commit("run-old").reference,oldref)
                if point=="before_pointer":
                    with self.assertRaises(DependencyUnavailable):restarted.read_commit("run-new")
                    self.assertTrue((restarted.root/"blobs"/new.payload_ref.sha256[:2]/new.payload_ref.sha256).exists())
                    self.assertGreater(restarted.storage_accounting()["orphan_manifest_bytes"],0)
                    self.assertGreater(restarted.storage_accounting()["orphan_blob_bytes"],0)
                else:
                    ref=restarted.read_commit("run-new").reference
                    self.assertEqual(restarted.commit("run-new",(new.id,),(new,),f.payloads),ref)
                    with self.assertRaises(ContractError):restarted.commit("run-new",(old.id,),(old,),f.payloads)

    def test_f11_19_manifest_only_reconstruction_and_absence(self):
        f=Fixture();nodes=CASES["F11-20"]["inputs"]["nodes"];built={}
        values,_,_=literal.full_rebuild(nodes,["c","d"])
        def build(k):
            if k not in built:
                d=nodes[k].get("dependency");deps=() if d is None else (f.dep(d,build(d)),)
                built[k]=f.node(k,raw=canonical_json({"recipe":nodes[k],"value":[values[k].numerator,values[k].denominator]}),dependencies=deps)
            return built[k]
        c=build("c");d=build("d")
        with tempfile.TemporaryDirectory() as root:
            store=SemanticArtifactStore(root,f.namespace);store.commit("graph",(c.id,d.id),tuple(built.values()),f.payloads)
            restored=SemanticArtifactStore(root,f.namespace);commit=restored.read_commit("graph")
            recipes={n.logical_key:json.loads(restored._blob_read(n.payload_ref,restored.limits.max_node_payload_bytes))["recipe"] for n in commit.closure.nodes}
            actual,_=evaluate_toy(recipes,("c","d"));self.assertEqual(actual["c"],Fraction(*CASES["F11-19"]["expected"]["complete_output"]))
            missing=built["a"].payload_ref;(restored.root/"blobs"/missing.sha256[:2]/missing.sha256).unlink()
            with self.assertRaises(DependencyUnavailable):restored.read_commit("graph")

    def test_f11_20_full_versus_incremental_exact_arithmetic(self):
        case=CASES["F11-20"];i=case["inputs"];e=case["expected"];nodes=i["nodes"]
        def timed(call):
            wall=time.perf_counter();cpu=time.process_time();value=call()
            return value,{"wall_seconds":time.perf_counter()-wall,"cpu_seconds":time.process_time()-cpu,
                          "peak_rss_bytes":resource.getrusage(resource.RUSAGE_SELF).ru_maxrss*1024}
        (old,oldwork),oldtime=timed(lambda:evaluate_toy(nodes,tuple(i["roots"])))
        ref,_,_=literal.full_rebuild(nodes,i["roots"])
        self.assertEqual(old,ref);self.assertEqual(old,{k:Fraction(*v) for k,v in e["old_values"].items()})
        newnodes={k:dict(v) for k,v in nodes.items()}
        for k,value in i["update"].items():newnodes[k]["value"]=value
        (full,fullwork),fulltime=timed(lambda:evaluate_toy(newnodes,tuple(i["roots"])))
        independent,_,_=literal.full_rebuild(newnodes,i["roots"])
        self.assertEqual(full,independent);self.assertEqual(full,{k:Fraction(*v) for k,v in e["new_values"].items()})
        f=Fixture()
        def semantic(recipes,values):
            built={}
            def build(k):
                if k not in built:
                    d=recipes[k].get("dependency")
                    deps=() if d is None else (f.dep(d,build(d)),)
                    value=values[k]
                    built[k]=f.node(k,raw=canonical_json({"recipe":recipes[k],"value":[value.numerator,value.denominator]}),dependencies=deps)
                return built[k]
            for k in recipes:build(k)
            return built
        oldspecs=semantic(nodes,old);fullspecs=semantic(newnodes,full)
        roots=lambda specs:tuple(specs[k].id for k in i["roots"])
        oldclosure=f.closure(tuple(oldspecs.values()),tuple(oldspecs[k] for k in i["roots"]))
        plan,plantime=timed(lambda:plan_rebuild(oldclosure,tuple(fullspecs.values()),tuple(i["update"]),payloads=f.payloads,roots=roots(fullspecs)))
        self.assertEqual(list(plan.rebuilt_keys),e["affected_keys"])
        (incremental,incwork),inctime=timed(lambda:evaluate_toy(newnodes,tuple(i["roots"]),previous_values=old,affected=plan.rebuilt_keys))
        self.assertEqual(incremental,full)
        incspecs=semantic(newnodes,incremental)
        self.assertEqual(tuple(sorted(n.id for n in incspecs.values())),tuple(sorted(n.id for n in fullspecs.values())))
        self.assertEqual(fullwork["source_reads"],e["full_source_value_reads"]);self.assertEqual(incwork["source_reads"],e["incremental_source_value_reads"])
        for op in ("multiply","add"):
            self.assertEqual(fullwork[op],e["full_arithmetic"][op]);self.assertEqual(incwork[op],e["incremental_arithmetic"][op])
        self.assertEqual((fullwork["validated_nodes"],fullwork["validated_edges"]),(6,4))
        with tempfile.TemporaryDirectory() as root:
            def build(path,specs):
                candidate=SemanticArtifactStore(path,f.namespace)
                return candidate,candidate.commit("toy",roots(specs),tuple(specs.values()),f.payloads)
            def restore():
                candidate=SemanticArtifactStore(Path(root)/"full",f.namespace)
                return candidate,candidate.read_commit("toy")
            (store,commit_ref),buildtime=timed(lambda:build(Path(root)/"full",fullspecs))
            buildio=store.io_counts
            (reopened,restored),restoretime=timed(restore)
            restoreio=reopened.io_counts
            (incstore,incref),incbuildtime=timed(lambda:build(Path(root)/"incremental",incspecs))
            self.assertEqual(commit_ref.manifest_ref,incref.manifest_ref)
            for key in plan.reused_keys:self.assertEqual(oldspecs[key].id,incspecs[key].id)
            ENGINEERING_METRICS.update({"case_id":"F11-20","exact_value_parity":True,"exact_manifest_parity":True,
                "old_arithmetic":{**oldtime,"operations":oldwork},"full_arithmetic":{**fulltime,"operations":fullwork},
                "incremental_arithmetic":{**inctime,"operations":incwork},"plan_validation":plantime,
                "full_build":buildtime,"incremental_build":incbuildtime,"restore":restoretime,
                "validated_nodes":len(restored.closure.nodes),"validated_edges":restored.closure.edges,
                "manifest_bytes":restored.manifest_bytes,"payload_bytes":restored.payload_bytes,
                "build_io":buildio,"restore_io":restoreio,"incremental_build_io":incstore.io_counts,
                "storage":store.storage_accounting(),"rebuilt_ids":plan.rebuilt_ids,"reused_ids":plan.reused_ids,
                "first_change_paths":plan.first_change_paths,"commit_manifest_sha256":commit_ref.manifest_ref.sha256,
                "claim_scope":"finite rational engineering; complete graph validation remains charged; native/economic/consumer gates open"})

    def test_f11_21_inclusive_bounds_and_no_partial_state(self):
        self.assertEqual(asdict(Limits()),GOLDEN["default_limits"])
        f=Fixture();a=f.node("a");b=f.node("b",dependencies=(f.dep("a",a),))
        f.closure((a,b),(b,),replace(Limits(),max_nodes_per_commit=2,max_edges_per_commit=1,max_dependency_depth=2))
        for limits in (replace(Limits(),max_nodes_per_commit=1),replace(Limits(),max_dependency_depth=1)):
            with self.assertRaises(ContractError):f.closure((a,b),(b,),limits)
        c=f.node("c",dependencies=(f.dep("a",a),f.dep("b",b)))
        with self.assertRaises(ContractError):f.closure((a,b,c),(c,),replace(Limits(),max_edges_per_commit=2))
        rows=tuple(f.row(row_id=str(i),known=100) for i in range(2));n=f.node("rows","source",rows=rows)
        f.closure((n,),limits=replace(Limits(),max_rows_per_node=2))
        with self.assertRaises(ContractError):f.closure((n,),limits=replace(Limits(),max_rows_per_node=1))
        cols=f.node("columns","source",rows=(f.row(column="a"),f.row(column="b")))
        f.closure((cols,),limits=replace(Limits(),max_columns_per_row=2))
        with self.assertRaises(ContractError):f.closure((cols,),limits=replace(Limits(),max_columns_per_row=1))
        exact=f.node("exact",raw=b"x"*1048576);f.closure((exact,))
        over=f.node("over",raw=b"x"*1048577)
        with self.assertRaises(ContractError):f.closure((over,))
        raw=_encode(((a.id,),(a,)));limit=len(raw)
        with tempfile.TemporaryDirectory() as root:
            store=SemanticArtifactStore(root,f.namespace,replace(Limits(),max_manifest_bytes=limit,max_commits=1))
            first=store.commit("first",(a.id,),(a,),f.payloads)
            with self.assertRaises(ContractError):store.commit("second",(a.id,),(a,),f.payloads)
            self.assertEqual(store.read_commit("first").reference,first)
        with tempfile.TemporaryDirectory() as root:
            store=SemanticArtifactStore(root,f.namespace,replace(Limits(),max_manifest_bytes=limit-1))
            with self.assertRaises(ContractError):store.commit("first",(a.id,),(a,),f.payloads)
            with self.assertRaises(DependencyUnavailable):store.read_commit("first")
        unique={r.sha256:f.payloads[r.sha256] for r in (a.definition_ref,a.payload_ref,a.execution.code_ref)};total=sum(len(v) for v in unique.values())
        for bound,success in ((total,True),(total-1,False)):
            with tempfile.TemporaryDirectory() as root:
                store=SemanticArtifactStore(root,f.namespace,replace(Limits(),max_store_blob_bytes=bound))
                if success:store.commit("x",(a.id,),(a,),f.payloads);self.assertEqual(store.storage_accounting()["unique_blob_bytes"],bound)
                else:
                    with self.assertRaises(ContractError):store.commit("x",(a.id,),(a,),f.payloads)

    def test_f11_22_tolerance_and_decision_consequence(self):
        c=CASES["F11-22"];i=c["inputs"];e=c["expected"]
        result=literal.numerical_decision(i["backend_a"],i["backend_b"],i["threshold"],i["absolute_tolerance"])
        self.assertEqual(result["difference"],Fraction(*e["absolute_difference"]));self.assertTrue(result["within"])
        self.assertEqual(result["decisions"],(False,True))
        self.assertEqual(numerical_decision(*(Fraction(*i[k]) for k in ("backend_a","backend_b","threshold","absolute_tolerance"))),result)
        f=Fixture();a=f.node("backend");settings=json.loads(f.execution.numerical_settings_json)
        b=replace(a,execution=replace(f.execution,numerical_settings_json=canonical_json({**settings,"backend_id":"other"})))
        self.assertNotEqual(a.id,b.id)

    def test_f11_23_failed_attempts_not_success_inputs(self):
        from trading_research.operations.trials import TrialRegistry
        f=Fixture();source=f.source()
        with tempfile.TemporaryDirectory() as root:
            store=SemanticArtifactStore(Path(root)/"semantic",f.namespace)
            registry=TrialRegistry(Path(root)/"trials")
            registry.register_family("synthetic",scope_ids=("F11",),protocol={"finite":True},max_attempts=3,cpu_budget_seconds=15)
            scientific=dict(family="synthetic",stage="engineering",configuration={"supplied":True},code_hash="code",data_hashes={"fixture":"frozen"},fold_version="fold",target_version="target")
            trial=registry.register(name="first",**scientific)
            self.assertEqual(registry.register(name="renamed",**scientific),trial)
            partial=registry.artifacts.put_bytes(f.payloads[source.payload_ref.sha256],kind=source.payload_ref.kind)
            for status in ("failed","interrupted"):
                attempt=registry.start(trial,cpu_reservation_seconds=5)
                registry.finish(attempt,status=status,cpu_seconds=None,wall_seconds=None,peak_rss_bytes=None,reason="synthetic outcome",result_artifacts=(asdict(partial),))
                record_failed_attempt(store,registry=registry,trial_id=trial,attempt_id=attempt,status=status,reserved_cpu_seconds=5,partial_refs=(partial,))
                with self.assertRaises(DependencyUnavailable):store.read_commit(attempt)
            attempt=registry.start(trial,cpu_reservation_seconds=5)
            ref=store.commit("run-success",(source.id,),(source,),f.payloads)
            result=registry.artifacts.put_bytes(canonical_json(asdict(ref)),kind="synthetic_commit_evidence")
            registry.finish(attempt,status="succeeded",cpu_seconds=1,wall_seconds=1,peak_rss_bytes=1,reason="supplied engineering commit",result_artifacts=(asdict(result),))
            with self.assertRaises(ContractError):record_failed_attempt(store,registry=registry,trial_id=trial,attempt_id=attempt,status="failed",reserved_cpu_seconds=5)
            restored=TrialRegistry(Path(root)/"trials").state()
            self.assertEqual(len(restored["trials"]),1);self.assertEqual(len(restored["attempts"]),3)
            self.assertEqual(sum(a["cpu_seconds"] for a in restored["attempts"].values()),11)
            self.assertEqual(SemanticArtifactStore(Path(root)/"semantic",f.namespace).read_commit("run-success").reference,ref)
            audits=[json.loads(p.read_bytes()) for p in (store.root/"failed_attempts").glob("*.json")]
            self.assertEqual(len({v["trial_id"] for v in audits}),1);self.assertEqual(len(audits),2)
            self.assertTrue(all(v["resource_basis"]=="reservation_charged_usage_unknown" for v in audits))

    def test_f11_24_snapshot_velocity_receipt_lineage(self):
        f=Fixture();snapshot=f.source("snapshot",value=5,observed=10,known=10,version="snapshot-v1")
        copied=f.source("snapshot",value=5,observed=10,known=20,version="snapshot-v1",acquisition="reconnect-1")
        velocity=f.source("velocity",value=[1,10],observed=11,known=12,version="velocity-v1",acquisition="velocity-receipt")
        self.assertEqual(copied.row_evidence[0].observed_at,10);self.assertEqual(copied.row_evidence[0].input_known_at,20)
        self.assertEqual(velocity.row_evidence[0].observed_at,11)
        self.assertEqual(snapshot.payload_ref,copied.payload_ref);self.assertNotEqual(snapshot.id,copied.id)
        self.assertNotEqual(copied.row_evidence[0].acquisition_id,velocity.row_evidence[0].acquisition_id)
        self.assertEqual(json.loads(copied.row_evidence[0].value_json)-json.loads(snapshot.row_evidence[0].value_json),0)
        for new,paired in ((copied,True),(velocity,False)):
            with self.assertRaises(ContractError):snapshot_pair(snapshot.row_evidence[0],new.row_evidence[0],observed_pairing=paired)
        self.assertEqual(snapshot_pair(snapshot.row_evidence[0],velocity.row_evidence[0],observed_pairing=True),
                         (snapshot.row_evidence[0].acquisition_id,velocity.row_evidence[0].acquisition_id))

    def test_f11_repair_committed_adapters_and_domains(self):
        import math
        from trading_research.operations.artifact_graph import restore_bound_model
        for kind in ("binary","frequency","calibrated"):
            for mode in ("OOF","final"):
                f,nodes,q,state,model,bindings=supplied_fixture(kind,mode)
                with tempfile.TemporaryDirectory() as root:
                    store=SemanticArtifactStore(root,f.namespace)
                    ref=store.commit("state",tuple(n.id for n in nodes.values()),tuple(nodes.values()),f.payloads)
                    result,manifest=state.predict_committed(store,ref,model.id,ReadSession(store,ref,bindings))
                    expected=.75 if kind=="frequency" else literal.binary_probability((3.,),(1.,),(1.,),(1.,),0.)
                    if kind=="calibrated":
                        expected=literal.binary_probability((math.log(expected)-math.log1p(-expected),),(1.,),(1.,),(1.,),0.)
                    self.assertEqual(result,expected);self.assertEqual(len(manifest.reads),1)
                    restored=restore_bound_model(SemanticArtifactStore(root,f.namespace),ref,model.id)
                    self.assertEqual(restored,state)
                    self.assertEqual(restored.predict_committed(store,ref,model.id,ReadSession(store,ref,bindings))[0],result)
                    alien=SemanticArtifactStore(root,f.namespace)
                    with self.assertRaises(ContractError):state.predict_committed(store,ref,model.id,ReadSession(alien,ref,bindings))
                    for request in (replace(q,purpose="audit"),replace(q,target_definition_ref=f.keep(b"wrong-target")),replace(q,decision_cut=89,assembled_at=100)):
                        with self.assertRaises(ContractError):state.predict_committed(store,ref,model.id,ReadSession(store,ref,(replace(bindings[0],request=request),)))
                    if kind=="binary":
                        for bad in (replace(state,scales=(0.,)),replace(state,coefficients=(True,)),replace(state,intercept=float("inf"))):
                            with self.assertRaises(ContractError):bad.predict_committed(store,ref,model.id,ReadSession(store,ref,bindings))
                    if kind=="frequency":
                        for bad in (replace(state,overall=1.1),replace(state,cells=(((0,),2,1),)),replace(state,prior_strength=-1.)):
                            with self.assertRaises(ContractError):bad.predict_committed(store,ref,model.id,ReadSession(store,ref,bindings))
                    if kind=="calibrated":
                        with self.assertRaises(ContractError):replace(state,probability_floor=0.).predict_committed(store,ref,model.id,ReadSession(store,ref,bindings))
                        with self.assertRaises(IntegrityError):replace(state,base=replace(state.base,intercept=1.)).predict_committed(store,ref,model.id,ReadSession(store,ref,bindings))
        for value in (True,"Infinity","3"):
            f,nodes,q,state,model,bindings=supplied_fixture(value=value)
            with tempfile.TemporaryDirectory() as root:
                store=SemanticArtifactStore(root,f.namespace);ref=store.commit("state",tuple(n.id for n in nodes.values()),tuple(nodes.values()),f.payloads)
                with self.assertRaises(ContractError):state.predict_committed(store,ref,model.id,ReadSession(store,ref,bindings))

    def test_f11_repair_causal_rows_labels_and_sessions(self):
        f=Fixture();q=ReadRequest("sample-eval",100,102,"input","Row.v1","probability")
        def derived(known=100,until=120,output_until=120,purpose="input",use="value"):
            source=f.source(known=known,valid_until=until)
            binding=ReadBinding("x",source.id,"x",replace(q,purpose=purpose))
            manifest=f.node("actual","read_manifest",read_manifest=ReadManifest(f.namespace,(binding,),(ReadRecord(binding,source.row_evidence[0]),),()),
                            dependencies=(f.dep("x",source,use,("x",)),))
            row=replace(f.row(known=100,valid_until=output_until),availability_basis="derived")
            feature=f.node("feature","feature",rows=(row,),dependencies=(f.dep("reads",manifest),),derivations=(DerivationEvidence("sample-eval",manifest.id,100,102),))
            return source,manifest,feature
        good=derived();closure=f.closure(good,(good[-1],))
        with tempfile.TemporaryDirectory() as root:
            store=SemanticArtifactStore(root,f.namespace);ref=store.commit("derived",(good[-1].id,),good,f.payloads)
            self.assertEqual(store.resolve(ref,good[-1].id,"x",q).value_json,b"3")
            with self.assertRaises(DependencyUnavailable):store.resolve(ref,good[-1].id,"x",replace(q,assembled_at=101))
            with self.assertRaises(DependencyUnavailable):store.resolve(ref,good[-1].id,"x",replace(q,assembled_at=120))
        for kwargs in ({"known":200},{"output_until":140},{"purpose":"audit"},{"use":"provenance"}):
            values=derived(**kwargs)
            with self.assertRaises(ContractError):f.closure(values,(values[-1],))
        primitive={"x":{"role":"source","known":100,"observed":99,"until":120,"value":3}}
        request={"sample":"sample-eval","cut":100,"assembled":102,"purpose":"input","source":"x"}
        self.assertEqual(literal.actual_reads(primitive,[request]),[3])
        for row in ({**primitive["x"],"known":200},{**primitive["x"],"role":"label"}):
            with self.assertRaises(ValueError):literal.actual_reads({"x":row},[request])
        f=Fixture();nodes,q=f.complete();model=nodes["model"]
        label=nodes["training-label"]
        for target in (replace(label.label_targets[0],target_start=21),replace(label.label_targets[0],target_definition_ref=f.keep(b"forged"))):
            changed=replace(label,label_targets=(target,))
            fit=replace(model.fit_evidence,training_label_refs=(replace(model.fit_evidence.training_label_refs[0],label_node_id=changed.id),))
            revised=replace(model,fit_evidence=fit,dependencies=tuple(replace(d,source_id=changed.id) if d.source_id==label.id else d for d in model.dependencies))
            with self.assertRaises(ContractError):f.closure(tuple(n for k,n in nodes.items() if k not in {"training-label","model","prediction"})+(changed,revised,))
        b=nodes["prediction-reads"].read_manifest.bindings[0]
        for request in (replace(q,row_id="other"),replace(q,decision_cut=99),replace(q,purpose="audit"),replace(q,target_end=129)):
            with self.assertRaises(ContractError):ReadManifest(f.namespace,(b,replace(b,column="z",request=request)),(),())
        audit=InputAudit(frozenset({"x","z"}),{"x":InputValue("x","v",100,b"3")},cut=100,fold_version="f",required=frozenset({"x"}))
        audit.read("x");audit.read("x")
        with self.assertRaises(ContractError):audit.manifest()
        with self.assertRaises(TypeError):audit._read["z"]=audit._read["x"]
        with self.assertRaises(AttributeError):audit._read={}
        with self.assertRaises(AttributeError):audit.__dict__["_read"]={}
        audit.omit_optional("z","not supplied")
        self.assertEqual(audit.manifest()["optional_omissions"],{"z":"not supplied"})

    def test_f11_repair_bounds_and_corruption(self):
        from unittest.mock import patch
        from trading_research.operations import artifact_graph as graph
        f=Fixture();source=f.source()
        over=f.node("rows","source",rows=(f.row(row_id="a"),f.row(row_id="b")))
        roots=(over.id,)
        with patch.object(graph,"_encode",side_effect=AssertionError("must reject before encoding")):
            with self.assertRaises(ContractError):validate_closure(roots,(over,),f.payloads,f.namespace,replace(Limits(),max_rows_per_node=1))
        with self.assertRaises(ContractError):replace(f.execution,configuration_json=b"x"*1048577)
        with self.assertRaises(ContractError):replace(source,namespace="x"*4097)
        with self.assertRaises(ContractError):f.closure((source,),limits={})
        from dataclasses import make_dataclass
        impostor=make_dataclass("ExecutionIdentity",[("code_ref",object)])(f.code)
        with self.assertRaises(ContractError):_encode(impostor)
        a=f.node("a");b=f.node("b");ordered=f.node("ordered",dependencies=(f.dep("a",a),f.dep("b",b)))
        envelope=json.loads(_encode(ordered));envelope["value"]["fields"]["dependencies"]["tuple"].reverse()
        with self.assertRaises(ContractError):_decode(canonical_json(envelope))
        with self.assertRaises(ContractError):replace(source,kind=[])
        with self.assertRaises(ContractError):replace(Limits(),max_nodes_per_commit=257)

        with tempfile.TemporaryDirectory() as root:
            store=SemanticArtifactStore(root,f.namespace,replace(Limits(),max_columns_per_row=1))
            ref=store.commit("source",(source.id,),(source,),f.payloads)
            q=ReadRequest("sample-eval",100,100,"input","Row.v1","probability")
            with self.assertRaises(ContractError):ReadSession(store,ref,(ReadBinding("x",source.id,"x",q),ReadBinding("y",source.id,"x",q)))
            with self.assertRaises(ContractError):store.commit("x"*4097,(source.id,),(source,),f.payloads)
            self.assertEqual(store.read_commit("source").reference,ref)
            manifest=store._manifests.path(ref.manifest_ref);original=manifest.read_bytes();manifest.write_bytes(b"corrupt")
            with self.assertRaises(IntegrityError):store.read_commit("source")
            manifest.write_bytes(original)
            pointer=store._pointer("source");original=pointer.read_bytes();bad=json.loads(original);bad["manifest_ref"]["kind"]="semantic_payload";pointer.write_bytes(canonical_json(bad))
            with self.assertRaises(IntegrityError):store.read_commit("source")
            pointer.write_bytes(original)
            bad=json.loads(original);bad["key"]="wrong";pointer.write_bytes(canonical_json(bad))
            with self.assertRaises(IntegrityError):store.read_commit("source")
        f=Fixture();a=f.node("a");b=f.node("b",dependencies=(f.dep("a",a),))
        old=f.closure((a,b),(b,));changed=replace(a,execution=replace(a.execution,code_ref=f.keep(b"new-code")))
        with self.assertRaises(ContractError):plan_rebuild(old,(changed,b),("a",),payloads=f.payloads)
        with self.assertRaises(ContractError):plan_rebuild(old,(a,b),("a",))
        with self.assertRaises(ContractError):evaluate_toy({"a":{"op":"add","dependency":"b","constant":[1,1]},"b":{"op":"add","dependency":"a","constant":[1,1]}},("a",))


    def test_f11_repair_real_three_stage_oof_and_population(self):
        f,nodes,calibrator,q=three_stage_fixture()
        closure=f.closure(tuple(nodes.values()),(calibrator,))
        admitted=validate_oof_producer(q,calibrator.id,closure)
        self.assertEqual(sorted(closure.by_id[i].logical_key for i in admitted),CASES["F11-08"]["expected"]["valid_closure_sorted"])
        self.assertEqual([nodes[k].fit_evidence.actual_fit_completion_at for k in ("scaler","model","calibrator")],[80,85,90])
        self.assertEqual([list(nodes[k].fit_evidence.training_groups) for k in ("scaler","model","calibrator")],[["d0"],["d0"],["d1"]])
        # The calibrator's sanctioned training read is an earlier OOF prediction,
        # admitted through exact producer routes in its later authoritative fold.
        self.assertEqual(nodes["calibrator-reads"].read_manifest.reads[0].row.value_json,b"0.7")
        for variant in ("scaler-group","model-sample","calibrator-group","scaler-empty","scaler-future","final-substitution"):
            bad,bnodes,broot,bq=three_stage_fixture(variant)
            with self.assertRaises(ContractError):
                candidate=bad.closure(tuple(bnodes.values()),(broot,))
                validate_oof_producer(bq,broot.id,candidate)
        missing=tuple(n for k,n in nodes.items() if k!="scaler-fold")
        with self.assertRaises(ContractError):f.closure(missing,(calibrator,))
        purged=replace(q,row_id="train-0",date_group="d0",decision_cut=10,assembled_at=100,target_start=10,target_end=60)
        with self.assertRaises(ContractError):validate_oof_producer(purged,calibrator.id,closure)
        with tempfile.TemporaryDirectory() as root:
            store=SemanticArtifactStore(root,f.namespace)
            ref=store.commit("closure",(calibrator.id,),tuple(nodes.values()),f.payloads)
            # Missing retained transform content cannot be reconstructed by name.
            store._blobs.path(nodes["scaler"].payload_ref).unlink()
            with self.assertRaises(DependencyUnavailable):store.read_commit("closure")
        sample={"id":"eval","group":"d2","decision":100,"dependency_end":130,"target":"t"}
        fit={"completion":90,"training_ids":["cal-row"],"groups":["d1"]}
        self.assertTrue(literal.retained_fit(sample,None,fit,["eval"]))
        label={"target":"t","start":100,"end":130,"known":131}
        self.assertTrue(literal.retained_fit(sample,label,fit,["eval"]))
        with self.assertRaises(ValueError):literal.retained_fit(sample,{**label,"end":129},fit,["eval"])
        with self.assertRaises(ValueError):literal.retained_fit(sample,None,fit,[])

    def test_f11_repair_concurrent_publication_and_snapshot(self):
        from concurrent.futures import ThreadPoolExecutor
        from threading import Barrier
        from unittest.mock import patch
        from trading_research.operations import artifact_graph as graph
        f=Fixture();a=f.source("a",value=1);b=f.source("b",value=2)
        for conflict in (False,True):
            with tempfile.TemporaryDirectory() as root:
                limits=replace(Limits(),max_commits=1)
                first=SemanticArtifactStore(root,f.namespace,limits);second=SemanticArtifactStore(root,f.namespace,limits)
                barrier=Barrier(2)
                def writer(store,key,node):
                    barrier.wait(timeout=5)
                    try:return store.commit(key,(node.id,),(node,),f.payloads)
                    except ContractError as error:return type(error)
                with ThreadPoolExecutor(max_workers=2) as workers:
                    futures=[workers.submit(writer,first,"same" if conflict else "a",a),workers.submit(writer,second,"same" if conflict else "b",b)]
                    results=[future.result(timeout=10) for future in futures]
                self.assertEqual(sum(result is ContractError for result in results),1)
                winner=next(result for result in results if result is not ContractError)
                self.assertEqual(first.read_commit(winner.key).reference,winner)
                self.assertEqual(first.storage_accounting()["commits"],1)
        with tempfile.TemporaryDirectory() as root:
            store=SemanticArtifactStore(root,f.namespace)
            raw=f.payloads[a.payload_ref.sha256];original=graph.validate_closure
            def mutate(*args,**kwargs):
                f.payloads[a.payload_ref.sha256]=b"changed after snapshot"
                return original(*args,**kwargs)
            with patch.object(graph,"validate_closure",side_effect=mutate):
                ref=store.commit("snapshot",(a.id,),(a,),f.payloads)
            self.assertEqual(store._blob_read(a.payload_ref,store.limits.max_node_payload_bytes),raw)
            self.assertEqual(store.read_commit("snapshot").reference,ref)
            counts=store.storage_accounting()
            self.assertEqual(counts["orphan_blob_bytes"],0);self.assertEqual(counts["orphan_manifest_bytes"],0)
            # A retained orphan remains charged even though it supplies no commit.
            orphan=store._blobs.put_bytes(b"orphan",kind="partial")
            self.assertEqual(store.storage_accounting()["orphan_blob_bytes"],len(b"orphan"))
            self.assertEqual(store.storage_accounting()["unique_blob_bytes"],counts["unique_blob_bytes"]+len(b"orphan"))
        f=Fixture();node=f.source()
        total=sum(len(f.payloads[r.sha256]) for r in (node.definition_ref,node.payload_ref))
        with tempfile.TemporaryDirectory() as root:
            limits=replace(Limits(),max_store_blob_bytes=total)
            store=SemanticArtifactStore(root,f.namespace,limits);store.commit("exact",(node.id,),(node,),f.payloads)
            store._blobs.put_bytes(b"unregistered-orphan",kind="partial")
            with self.assertRaises(ContractError):SemanticArtifactStore(root,f.namespace,limits)




if __name__ == "__main__":
    unittest.main()
