"""Bounded descriptive-confirmation dispatch, feasibility and registration checks."""
import hashlib
import json
import sys
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from trading_research.errors import IntegrityError
from trading_research.research import jumbo_study as study
from tools import jumbo_verification as verification
from tools.run_jumbo_study import CHECK_TEST_SELECTION


def _sha(label):
    return hashlib.sha256(label.encode()).hexdigest()


def _write_execution(root, relative, payload):
    path = root / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    raw = json.dumps(payload, sort_keys=True).encode()
    path.write_bytes(raw)
    return {"path": relative, "sha256": hashlib.sha256(raw).hexdigest()}


class FakeStore:
    def __init__(self, reports):
        self.reports = reports

    def read_json(self, ref):
        key = ref.sha256 if hasattr(ref, "sha256") else ref["sha256"]
        if key not in self.reports:
            raise IntegrityError("missing artifact")
        return self.reports[key]


class DescriptiveConfirmationDispatchTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.extract_worker_sha = _sha("extract-worker")
        self.admit_worker_sha = _sha("admit-worker")
        self.fit_worker_sha = _sha("fit-worker")
        self.source_sha = _sha("source-supplement")
        self.admit_worker = {"success": True, "mode": "admit", "partitions": []}
        self.source_report = {"actual_accepted": True, "actual_status": "price_readmitted"}
        self.admit_identity = _write_execution(self.root, "reports/admit/execution.json", {
            "success": True, "mode": "admit", "phase": "full_admission",
            "worker_report": {"kind": "research_study_worker_report",
                              "sha256": self.admit_worker_sha, "size_bytes": 1}})
        self.extract_worker = {
            "success": True, "mode": "develop", "phase": "extract",
            "admission_predecessor": self.admit_identity,
            "source_supersession": {"kind": "jumbo_actual_definition_supersession_report_v1",
                                    "sha256": self.source_sha, "size_bytes": 1}}
        self.extract_identity = _write_execution(self.root, "reports/extract/execution.json", {
            "success": True, "mode": "develop", "phase": "extract",
            "worker_report": {"kind": "research_study_worker_report",
                              "sha256": self.extract_worker_sha, "size_bytes": 1}})
        self.fit_worker = {"success": True, "mode": "develop", "phase": "fit"}
        self.fit_identity = _write_execution(self.root, "reports/fit/execution.json", {
            "success": True, "mode": "develop", "phase": "fit",
            "worker_report": {"kind": "research_study_worker_report",
                              "sha256": self.fit_worker_sha, "size_bytes": 1}})
        self.store = FakeStore({
            self.extract_worker_sha: self.extract_worker,
            self.admit_worker_sha: self.admit_worker,
            self.fit_worker_sha: self.fit_worker,
            self.source_sha: self.source_report,
        })
        self.extraction = {
            "success": True, "model_fits": 0, "family_statistics_complete": False,
            "scope": "Complete declared heldout extraction", "remaining": ["placeholder"]}

    def packet(self, identity, *, descriptive):
        return {"mode": "confirm", "phase": "confirmation", "predecessor": identity,
                "descriptive_confirmation": descriptive}

    def run_study(self, packet):
        with patch.object(study, "ArtifactStore", return_value=self.store):
            return study.run(packet, {"study_id": "literal"}, self.root)

    def test_extract_predecessor_dispatches_heldout_with_admission_and_source(self):
        captured = {}

        def extract(_packet, _protocol, _root, _store, *, admitted=None, heldout=False,
                    frozen_source_supplement=None):
            captured.update(admitted=admitted, heldout=heldout,
                            frozen_source_supplement=frozen_source_supplement)
            return dict(self.extraction)

        blocked = SimpleNamespace()
        blocked.run_confirmation = lambda *args, **kwargs: (_ for _ in ()).throw(
            AssertionError("Context dispatch called"))
        saved = sys.modules.get("trading_research.research.jumbo_pipeline")
        sys.modules.pop("trading_research.research.jumbo_pipeline", None)
        try:
            with patch.object(study, "_run_extraction", side_effect=extract), \
                 patch.dict(sys.modules, {"trading_research.research.jumbo_pipeline": blocked}):
                result = self.run_study(self.packet(self.extract_identity, descriptive=True))
        finally:
            if saved is not None:
                sys.modules["trading_research.research.jumbo_pipeline"] = saved
            else:
                sys.modules.pop("trading_research.research.jumbo_pipeline", None)
        self.assertIs(captured["heldout"], True)
        self.assertIs(captured["admitted"], self.admit_worker)
        self.assertEqual(captured["frozen_source_supplement"], self.extract_worker["source_supersession"])
        self.assertEqual(result["development_predecessor"], self.extract_identity)
        self.assertEqual(result["admission_predecessor"], self.admit_identity)
        self.assertIs(result["family_statistics_complete"], False)
        self.assertEqual(result["model_fits"], 0)
        self.assertIs(result["context_models_complete"], False)
        self.assertIs(result["location_quality_complete"], False)
        self.assertIn("heldout descriptive extraction", result["scope"])
        self.assertTrue(any("Pooled" in item for item in result["remaining"]))
        self.assertNotIn("domains", result)

    def test_context_dispatch_is_never_imported_on_descriptive_branch(self):
        imported = []
        real_import = __import__

        def guarded(name, globals=None, locals=None, fromlist=(), level=0):
            imported.append(name)
            if name == "trading_research.research.jumbo_pipeline" or name.endswith("jumbo_pipeline"):
                raise AssertionError("Context module imported on descriptive confirmation")
            return real_import(name, globals, locals, fromlist, level)

        with patch.object(study, "_run_extraction", return_value=dict(self.extraction)), \
             patch("builtins.__import__", side_effect=guarded):
            self.run_study(self.packet(self.extract_identity, descriptive=True))
        self.assertNotIn("trading_research.research.jumbo_pipeline", imported)

    def test_fitted_predecessor_retains_model_confirmation_route(self):
        model_result = {"success": True, "domains": [{"domain": "range"}], "new_model_fits": 0}
        called = []

        def run_confirmation(packet, protocol, root, store):
            called.append((packet, protocol, root, store))
            return model_result

        fake = SimpleNamespace(run_confirmation=run_confirmation)
        saved = sys.modules.get("trading_research.research.jumbo_pipeline")
        try:
            with patch.object(study, "_run_extraction") as extract, \
                 patch.dict(sys.modules, {"trading_research.research.jumbo_pipeline": fake}):
                result = self.run_study(self.packet(self.fit_identity, descriptive=False))
        finally:
            if saved is not None:
                sys.modules["trading_research.research.jumbo_pipeline"] = saved
            else:
                sys.modules.pop("trading_research.research.jumbo_pipeline", None)
        self.assertEqual(len(called), 1)
        extract.assert_not_called()
        self.assertEqual(result, model_result)

    def test_missing_failed_tampered_and_wrong_phase_admission_or_source_reject(self):
        cases = []
        missing_admission = dict(self.extract_worker)
        missing_admission.pop("admission_predecessor")
        cases.append((missing_admission, self.extract_identity, self.store))
        failed_admit = _write_execution(self.root, "reports/admit-failed/execution.json", {
            "success": False, "mode": "admit", "phase": "full_admission",
            "worker_report": {"kind": "research_study_worker_report",
                              "sha256": self.admit_worker_sha, "size_bytes": 1}})
        failed_extract = dict(self.extract_worker, admission_predecessor=failed_admit)
        cases.append((failed_extract, self.extract_identity, self.store))
        tampered = dict(self.extract_worker)
        tampered["admission_predecessor"] = {"path": self.admit_identity["path"], "sha256": _sha("tampered")}
        cases.append((tampered, self.extract_identity, self.store))
        wrong_phase_admit = _write_execution(self.root, "reports/admit-wrong/execution.json", {
            "success": True, "mode": "develop", "phase": "extract",
            "worker_report": {"kind": "research_study_worker_report",
                              "sha256": self.admit_worker_sha, "size_bytes": 1}})
        wrong_extract = dict(self.extract_worker, admission_predecessor=wrong_phase_admit)
        cases.append((wrong_extract, self.extract_identity, self.store))
        wrong_admit_phase = _write_execution(self.root, "reports/admit-fit-phase/execution.json", {
            "success": True, "mode": "admit", "phase": "fit",
            "worker_report": {"kind": "research_study_worker_report",
                              "sha256": self.admit_worker_sha, "size_bytes": 1}})
        cases.append((dict(self.extract_worker, admission_predecessor=wrong_admit_phase),
                      self.extract_identity, self.store))
        missing_source = dict(self.extract_worker)
        missing_source.pop("source_supersession")
        cases.append((missing_source, self.extract_identity, self.store))
        failed_source_store = FakeStore({
            **self.store.reports, self.source_sha: {"actual_accepted": False}})
        cases.append((self.extract_worker, self.extract_identity, failed_source_store))
        wrong_kind = dict(self.extract_worker, source_supersession={
            "kind": "jumbo_independent_heldout_context_domain_gzip_v1",
            "sha256": self.source_sha, "size_bytes": 1})
        cases.append((wrong_kind, self.extract_identity, self.store))
        for worker, identity, store in cases:
            store.reports[self.extract_worker_sha] = worker
            with self.subTest(worker=worker.get("admission_predecessor"),
                              source=worker.get("source_supersession"), store=id(store)), \
                 patch.object(study, "ArtifactStore", return_value=store), \
                 patch.object(study, "_run_extraction") as extract, \
                 self.assertRaises(IntegrityError):
                study.run(self.packet(identity, descriptive=True), {"study_id": "literal"}, self.root)
            extract.assert_not_called()
        self.store.reports[self.extract_worker_sha] = self.extract_worker

    def test_packet_flag_cannot_fake_extract_predecessor(self):
        with patch.object(study, "ArtifactStore", return_value=self.store), \
             patch.object(study, "_run_extraction") as extract, \
             self.assertRaises(IntegrityError):
            study.run(self.packet(self.fit_identity, descriptive=True), {"study_id": "literal"}, self.root)
        extract.assert_not_called()
        with self.assertRaises(ValueError):
            verification.authenticate_descriptive_confirmation(True, {
                "success": True, "mode": "develop", "phase": "fit"})
        with self.assertRaises(ValueError):
            verification.authenticate_descriptive_confirmation(True, None)
        with self.assertRaises(ValueError):
            verification.authenticate_descriptive_confirmation(
                True, {"success": True, "mode": "develop", "phase": "extract"}, configured=False)


class DescriptiveConfirmationFeasibilityTests(unittest.TestCase):
    CPU = 321.07731806375
    OUTPUT = 590527624.7548462 - 446322032.7548462
    CPU_CAP = 6500
    OUTPUT_CAP = 768 * 1024 ** 2

    def test_literal_projection_pass_and_fail_are_independent_of_stored_flags(self):
        self.assertEqual(self.OUTPUT, 144205592.0)
        self.assertTrue(verification.descriptive_confirmation_feasible(
            self.CPU, self.OUTPUT, self.CPU_CAP, self.OUTPUT_CAP))
        self.assertFalse(verification.descriptive_confirmation_feasible(
            6500.1, self.OUTPUT, self.CPU_CAP, self.OUTPUT_CAP))
        self.assertFalse(verification.descriptive_confirmation_feasible(
            self.CPU, self.OUTPUT_CAP + 1, self.CPU_CAP, self.OUTPUT_CAP))
        self.assertFalse(verification.descriptive_confirmation_feasible(
            True, self.OUTPUT, self.CPU_CAP, self.OUTPUT_CAP))
        self.assertFalse(verification.descriptive_confirmation_feasible(
            self.CPU, True, self.CPU_CAP, self.OUTPUT_CAP))

    def test_current_check_projection_fields_not_model_cap_flag(self):
        parity = {"passed": True, "model_preflight": {
            "projected_confirmation_extraction_cpu_seconds_conservative": self.CPU,
            "projected_confirmation_output_bytes_conservative": 590527624.7548462,
            "projected_confirmation_model_output_bytes_conservative": 446322032.7548462,
            "within_declared_confirmation_cap": False}}
        self.assertTrue(verification.confirmation_feasibility(
            parity, descriptive_confirmation=True,
            cpu_cap_seconds=self.CPU_CAP, output_cap_bytes=self.OUTPUT_CAP))
        self.assertFalse(verification.confirmation_feasibility(
            parity, descriptive_confirmation=False,
            cpu_cap_seconds=self.CPU_CAP, output_cap_bytes=self.OUTPUT_CAP))
        over_cpu = {"passed": True, "model_preflight": {
            **parity["model_preflight"],
            "projected_confirmation_extraction_cpu_seconds_conservative": 7000.0,
            "within_declared_confirmation_cap": True}}
        self.assertFalse(verification.confirmation_feasibility(
            over_cpu, descriptive_confirmation=True,
            cpu_cap_seconds=self.CPU_CAP, output_cap_bytes=self.OUTPUT_CAP))
        self.assertIsNone(verification.descriptive_confirmation_projection({}))
        joined = verification.descriptive_confirmation_projection(parity["model_preflight"])
        self.assertEqual(joined["projected_cpu_seconds"], self.CPU)
        self.assertEqual(joined["projected_output_bytes"], self.OUTPUT)


class DescriptiveConfirmationRegistrationTests(unittest.TestCase):
    def test_module_is_registered_for_check_and_confirmation_contracts(self):
        self.assertIn("tests.test_jumbo_descriptive_confirmation", CHECK_TEST_SELECTION)
        self.assertIn("test_jumbo_descriptive_confirmation", verification.TESTS["confirmation"])
        self.assertNotIn("test_jumbo_descriptive_confirmation", verification.TESTS["extract"])
        self.assertNotIn("test_jumbo_descriptive_confirmation", verification.TESTS["fit"])
