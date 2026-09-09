from copy import deepcopy
from dataclasses import asdict
from pathlib import Path
import tempfile
import unittest

from trading_research.errors import ContractError, IntegrityError
from trading_research.operations.artifacts import digest
from trading_research.operations.trials import TrialRegistry
from tools.jumbo_resources import amended_protocol, worker_limits


class BudgetAmendmentTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.registry = TrialRegistry(Path(temporary.name))
        self.family = "literal-same-family"
        self.registry.register_family(self.family, scope_ids=("C01",), protocol={"science": "fixed"},
                                      max_attempts=2, cpu_budget_seconds=10)
        self.trial = self.registry.register(name="literal", family=self.family, stage="engineering",
              configuration={"fixed": True}, code_hash="source", data_hashes={"source": "data"},
              fold_version="chronological", target_version="fixed")

    def authorization(self, **changes):
        state = self.registry.state()
        value = {"kind": "family_budget_authorization_v1", "amendment_id": "literal-approval-1",
                 "family": self.family, "base_family_sha256": digest(state["families"][self.family]),
                 "previous_limits": {"max_attempts": 2, "cpu_budget_seconds": 10},
                 "authorized_limits": {"max_attempts": 4, "cpu_budget_seconds": 20},
                 "approval": {"source": "explicit_user_approval", "approved_at": "2026-09-07T23:16:30Z",
                              "question": "Increase these limits while retaining all spending?", "answer": "yes"},
                 "reason": "Literal authorization fixture; no market execution."}
        value.update(changes)
        return asdict(self.registry.artifacts.put_json(value, kind="family_budget_authorization_v1"))

    def failed_attempt(self, reservation, observed):
        attempt = self.registry.start(self.trial, cpu_reservation_seconds=reservation)
        self.registry.finish(attempt, status="failed", cpu_seconds=observed, wall_seconds=1,
                             peak_rss_bytes=1, reason="literal retained failure")
        return attempt

    def test_exhausted_family_can_continue_without_rewriting_records_or_forgiving_failures(self):
        self.failed_attempt(4, 4)
        self.failed_attempt(4, 4)
        with self.assertRaises(ContractError):
            self.registry.start(self.trial, cpu_reservation_seconds=1)
        before = self.registry.history()
        old = self.registry.state()
        self.registry.amend_budget(authorization=self.authorization())
        self.assertEqual(self.registry.history()[:len(before)], before)
        self.assertEqual(self.registry.state()["families"], old["families"])
        self.assertEqual(self.registry.state()["attempts"], old["attempts"])
        self.failed_attempt(6, 6)
        with self.assertRaises(ContractError):
            self.registry.start(self.trial, cpu_reservation_seconds=7)
        self.failed_attempt(6, 1)
        with self.assertRaises(ContractError):
            self.registry.start(self.trial, cpu_reservation_seconds=1)

    def test_unknown_failure_and_running_reservations_remain_charged(self):
        self.failed_attempt(5, None)
        self.registry.amend_budget(authorization=self.authorization())
        running = self.registry.start(self.trial, cpu_reservation_seconds=10)
        second = self.registry.register(name="literal2", family=self.family, stage="engineering",
              configuration={"fixed": 2}, code_hash="source", data_hashes={"source": "data"},
              fold_version="chronological", target_version="fixed")
        with self.assertRaises(ContractError):
            self.registry.start(second, cpu_reservation_seconds=6)
        self.registry.start(second, cpu_reservation_seconds=5)
        self.assertEqual(self.registry.state()["attempts"][running]["status"], "running")

    def test_exact_authorization_is_idempotent_and_changed_reuse_is_rejected(self):
        ref = self.authorization()
        event = self.registry.amend_budget(authorization=ref)
        history = self.registry.history()
        self.assertEqual(self.registry.amend_budget(authorization=ref), event)
        self.assertEqual(self.registry.history(), history)
        with self.assertRaises(ContractError):
            self.registry.amend_budget(authorization=self.authorization(reason="Different scope"))

    def test_wrong_family_stale_limits_reset_and_missing_approval_are_rejected(self):
        for changes in ({"family": "another-family"}, {"base_family_sha256": "wrong"},
                        {"previous_limits": {"max_attempts": 1, "cpu_budget_seconds": 10}},
                        {"authorized_limits": {"max_attempts": 1, "cpu_budget_seconds": 20}},
                        {"authorized_limits": {"max_attempts": 4, "cpu_budget_seconds": True}},
                        {"approval": {"source": "proposal"}}):
            with self.subTest(changes=changes), self.assertRaises(ContractError):
                self.registry.amend_budget(authorization=self.authorization(**changes))
        with self.assertRaises(ContractError):
            self.registry.register_family(self.family, scope_ids=("C01",), protocol={"science": "changed"},
                                           max_attempts=4, cpu_budget_seconds=20)

    def test_altered_authorization_artifact_invalidates_amended_state(self):
        ref = self.authorization()
        self.registry.amend_budget(authorization=ref)
        from trading_research.operations.artifacts import artifact_ref
        self.registry.artifacts.path(artifact_ref(ref)).write_bytes(b"changed")
        with self.assertRaises(IntegrityError):
            self.registry.state()

    def test_phase_limits_are_distinct_and_do_not_mutate_the_scientific_protocol(self):
        base = {"family": "fixed", "question": {"clocks": [5, 15]}, "resources": {
            "mode_cpu_seconds": {"check": 90, "develop": 480, "confirm": 480},
            "hard_cpu_margin_seconds": 10, "wall_seconds": 900, "memory_bytes": 4294967296,
            "maximum_derived_output_bytes": 536870912, "maximum_attempts": 10, "cpu_budget_seconds": 2400}}
        old = deepcopy(base)
        authority = {"kind": "family_budget_authorization_v1", "family": "fixed",
            "base_protocol": {"sha256": "original"}, "approval": {"source": "explicit_user_approval"},
            "authorized_limits": {"max_attempts": 16, "cpu_budget_seconds": 12000},
            "resource_limits": {"cpu_seconds_per_phase": {"code_check": 90, "extract": 900, "fit": 6000, "confirmation": 3600},
                "hard_cpu_margin_seconds": 10, "memory_bytes": 4294967296, "maximum_derived_output_bytes": 536870912}}
        amended = amended_protocol(base, "original", authority)
        self.assertEqual(base, old)
        for phase, cap in authority["resource_limits"]["cpu_seconds_per_phase"].items():
            self.assertEqual(worker_limits(amended, phase)["cpu_seconds"], cap)
            self.assertEqual(worker_limits(amended, phase)["hard_cpu_seconds"], cap + 10)
        with self.assertRaises(ValueError):
            amended_protocol(base, "changed", authority)


class RetainedSourceReceiptTests(unittest.TestCase):
    def fixture(self):
        packet = {'analysis_plan': {'sha256': 'analysis'}, 'protocol_sha256': 'protocol'}
        prior = {'attempt_id': 'attempt', 'trial_id': 'trial', 'success': False, 'mode': 'check',
                 'family': 'family', 'within_declared_limits': True, 'code_snapshot': {'sha256': 'code'}}
        old = {**packet, 'attempt_id': 'attempt', 'trial_id': 'trial'}
        state = {'attempts': {'attempt': {'status': 'failed', 'trial_id': 'trial', 'family': 'family',
                 'result_artifacts': [{'kind': 'research_study_execution', 'sha256': digest(prior)}]}},
                 'trials': {'trial': {'code_hash': 'code'}}}
        stage = {'accepted': True, 'status': 'price_readmitted', 'recovered_primary_minutes': 3, 'cpu_seconds': 2.5}
        report = {'actual_accepted': True, 'actual_status': 'price_readmitted', 'original_admission_unchanged': True,
                  'generic_rows_unchanged_outside_target_ambiguity': True, 'recovered_primary_minutes': 3,
                  'cpu_seconds_internal': 2.5}
        return [packet, {'family': 'family'}, prior, old, state, stage, report]

    def test_completed_source_stage_is_reusable_while_overall_failure_stays_failed(self):
        from trading_research.research.jumbo_source_reuse import validate_source_receipt
        args = self.fixture()
        before = deepcopy(args)
        validate_source_receipt(*args)
        self.assertEqual(args, before)
        self.assertEqual(args[4]['attempts']['attempt']['status'], 'failed')

    def test_changed_scientific_inputs_or_missing_exact_receipt_cannot_reuse_source_stage(self):
        from trading_research.research.jumbo_source_reuse import validate_source_receipt
        for alter in (
                lambda a: a[0].update(protocol_sha256='different'),
                lambda a: a[3].update(analysis_plan={'sha256': 'other'}),
                lambda a: a[4]['attempts']['attempt'].update(result_artifacts=[]),
                lambda a: a[4]['attempts']['attempt'].update(status='succeeded'),
                lambda a: a[4]['trials']['trial'].update(code_hash='different')):
            args = self.fixture()
            alter(args)
            with self.assertRaises(IntegrityError):
                validate_source_receipt(*args)

    def test_unfinished_source_stage_or_changed_exclusions_cannot_be_promoted_by_reuse(self):
        from trading_research.research.jumbo_source_reuse import validate_source_receipt
        for changes in ({'actual_accepted': False}, {'actual_status': 'pending'},
                        {'generic_rows_unchanged_outside_target_ambiguity': False},
                        {'recovered_primary_minutes': 4}, {'cpu_seconds_internal': 0}):
            args = self.fixture()
            args[-1].update(changes)
            with self.subTest(changes=changes), self.assertRaises(IntegrityError):
                validate_source_receipt(*args)
