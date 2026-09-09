"""Meaningful consolidated dispatch, metadata and dependency-closure checks."""
from contextlib import ExitStack
import hashlib
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from tools import jumbo_verification as verification


class HardwareExecutionTests(unittest.TestCase):
    def fixture(self):
        protocol = {'family': 'unchanged', 'question': {'clocks': [5, 15]},
            'resources': {'memory_bytes': 4 * 1024**3, 'cpu_budget_seconds': 20000,
                'maximum_attempts': 24, 'phase_cpu_seconds': {'fit': 10000, 'confirmation': 6500},
                'maximum_derived_output_bytes': 768 * 1024**2}}
        reference = {'sha256': 'approved-budget', 'path': 'validation/budget.json', 'size_bytes': 10}
        allocation = {'kind': 'jumbo_user_hardware_execution_v1', 'family': 'unchanged',
            'budget_authorization': reference,
            'declared_hardware': {'vcpus': 21, 'memory_bytes': 83000000000},
            'execution': {'family_workers': 16, 'memory_bytes': 64 * 1024**3,
                'native_threads_per_worker': 1, 'gpu_workers': 0},
            'approval': {'source': 'explicit_user_instruction', 'messages': ['Use the supplied hardware.']}}
        live = {'cpu_quota_us': 1785000, 'cpu_period_us': 100000, 'memory_limit_bytes': 82999996416}
        return protocol, reference, allocation, live

    def test_effective_pod_limits_override_host_totals_and_preserve_all_spending(self):
        from copy import deepcopy
        from tools.jumbo_resources import apply_hardware_execution
        protocol, reference, allocation, live = self.fixture()
        before = deepcopy(protocol)
        result = apply_hardware_execution(protocol, allocation, budget_reference=reference, live_limits=live)
        self.assertEqual(protocol, before)
        self.assertEqual(result['question'], before['question'])
        expected = {**before['resources'], 'memory_bytes': 64 * 1024**3, 'family_workers': 16}
        self.assertEqual(result['resources'], expected)
        for change in (
            lambda a: a['execution'].update(family_workers=18),
            lambda a: a['execution'].update(family_workers=True),
            lambda a: a['execution'].update(memory_bytes=83000000000),
            lambda a: a['execution'].update(native_threads_per_worker=16),
            lambda a: a['approval'].update(source='inferred_host_hardware'),
            lambda a: a.update(budget_authorization={'sha256': 'different-budget'})):
            invalid = deepcopy(allocation)
            change(invalid)
            with self.assertRaises(ValueError):
                apply_hardware_execution(protocol, invalid, budget_reference=reference, live_limits=live)
        for restricted in ({**live, 'memory_limit_bytes': 32 * 1024**3},
                           {**live, 'cpu_quota_us': 800000}):
            with self.assertRaises(ValueError):
                apply_hardware_execution(protocol, allocation, budget_reference=reference, live_limits=restricted)

    def test_cgroup_v1_and_v2_report_the_enforced_quota_and_memory(self):
        from tools.jumbo_resources import live_hardware_limits
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            (root / 'cpu').mkdir()
            (root / 'memory').mkdir()
            (root / 'cpu/cpu.cfs_quota_us').write_text('1785000\n')
            (root / 'cpu/cpu.cfs_period_us').write_text('100000\n')
            (root / 'memory/memory.limit_in_bytes').write_text('82999996416\n')
            self.assertEqual(live_hardware_limits(root), self.fixture()[-1])
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            (root / 'cpu.max').write_text('1785000 100000\n')
            (root / 'memory.max').write_text('82999996416\n')
            self.assertEqual(live_hardware_limits(root), self.fixture()[-1])
            (root / 'cpu.max').write_text('max 100000\n')
            (root / 'memory.max').write_text('max\n')
            self.assertEqual(live_hardware_limits(root),
                {'cpu_quota_us': -1, 'cpu_period_us': 100000, 'memory_limit_bytes': None})


class AttemptCountVerificationTests(unittest.TestCase):
    def authority(self):
        return {"kind": "family_budget_authorization_v1", "family": "literal-science", "base_family_sha256": "base",
            "base_protocol": {"sha256": "unchanged-science"}, "approval": {"source": "explicit_user_approval"},
            "authorized_limits": {"max_attempts": 16, "cpu_budget_seconds": 12000},
            "resource_limits": {"cpu_seconds_per_phase": {"code_check": 90, "extract": 900, "fit": 6000, "confirmation": 3600},
                "hard_cpu_margin_seconds": 10, "memory_bytes": 4294967296, "maximum_derived_output_bytes": 536870912,
                "maximum_attempts_total": 16, "cumulative_cpu_seconds_total": 12000}}

    def test_second_attempt_only_approval_appends_to_current_limits_and_retains_all_prior_usage(self):
        from tests import test_trial_budget_amendment
        from trading_research.errors import ContractError
        case = test_trial_budget_amendment.BudgetAmendmentTests()
        case.setUp()
        self.addCleanup(case.doCleanups)
        case.failed_attempt(4, 4)
        first = case.authorization()
        case.registry.amend_budget(authorization=first)
        case.failed_attempt(4, 4)
        before = case.registry.history()
        attempts = case.registry.state()["attempts"]
        second = case.authorization(amendment_id="literal-approval-2",
            previous_limits={"max_attempts": 4, "cpu_budget_seconds": 20},
            authorized_limits={"max_attempts": 5, "cpu_budget_seconds": 20})
        case.registry.amend_budget(authorization=second)
        self.assertEqual(case.registry.history()[:len(before)], before)
        self.assertEqual(case.registry.state()["attempts"], attempts)
        self.assertEqual(case.registry.state()["effective_budgets"][case.family], {"max_attempts": 5, "cpu_budget_seconds": 20})
        case.registry.amend_budget(authorization=first)
        self.assertEqual(case.registry.state()["effective_budgets"][case.family]["max_attempts"], 5)
        with self.assertRaises(ContractError):
            case.registry.start(case.trial, cpu_reservation_seconds=13)

    def test_attempt_only_approval_keeps_the_exact_frozen_execution_plan(self):
        from copy import deepcopy
        import json
        from tools import run_jumbo_study as runner
        baseline = self.authority()
        current = deepcopy(baseline)
        current["authorized_limits"]["max_attempts"] = 17
        current["resource_limits"]["maximum_attempts_total"] = 17
        with tempfile.TemporaryDirectory() as folder, patch.object(runner, "ROOT", Path(folder)):
            root = Path(folder)
            (root / "validation").mkdir()
            raw = json.dumps(baseline).encode()
            (root / "validation/baseline.json").write_bytes(raw)
            reference = {"path": "validation/baseline.json", "sha256": hashlib.sha256(raw).hexdigest(), "size_bytes": len(raw)}
            plan = {"resource_amendment": reference, "unchanged_execution": "complete-model-workload"}
            original = deepcopy(plan)
            self.assertEqual(runner.execution_authorization(plan), (reference, raw))
            path = root / "validation/current.json"
            path.write_text(json.dumps(current))
            effective, payload = runner.execution_authorization(plan, path)
            self.assertEqual(json.loads(payload)["authorized_limits"]["max_attempts"], 17)
            self.assertEqual(effective["sha256"], hashlib.sha256(path.read_bytes()).hexdigest())
            self.assertEqual(plan, original)
            with self.assertRaises(ValueError):
                runner.execution_authorization(plan, root / "outside.json")

    def test_cpu_memory_output_science_or_unapproved_override_needs_separate_resolution(self):
        from copy import deepcopy
        from tools.jumbo_resources import require_same_verification_resources
        baseline = self.authority()
        for change in (
            lambda a: a["resource_limits"]["cpu_seconds_per_phase"].update(fit=5000),
            lambda a: a["resource_limits"].update(memory_bytes=2**31),
            lambda a: a["resource_limits"].update(maximum_derived_output_bytes=2**28),
            lambda a: a["resource_limits"].update(hard_cpu_margin_seconds=11),
            lambda a: a["authorized_limits"].update(cpu_budget_seconds=13000),
            lambda a: a.update(family="different-science"),
            lambda a: a["base_protocol"].update(sha256="changed-definition"),
            lambda a: a["approval"].update(source="proposed_not_authorized"),
            lambda a: a["resource_limits"].update(maximum_attempts_total=999)):
            current = deepcopy(baseline)
            change(current)
            with self.assertRaises(ValueError):
                require_same_verification_resources(baseline, current)

    def test_measured_resource_envelope_requires_explicit_bounded_approval_and_changes_only_limits(self):
        from copy import deepcopy
        from tools.jumbo_resources import require_approved_execution_resources, amended_protocol, worker_limits
        baseline = self.authority()
        current = deepcopy(baseline)
        current['authorized_limits'] = {'max_attempts': 24, 'cpu_budget_seconds': 20000}
        current['resource_limits'].update(maximum_attempts_total=24, cumulative_cpu_seconds_total=20000,
            maximum_derived_output_bytes=768 * 1024**2)
        current['resource_limits']['cpu_seconds_per_phase'].update(fit=10000, confirmation=6500)
        plan = {'resource_verification_envelope': {'kind': 'jumbo_measured_resource_envelope_v1',
                    'resource_limits': deepcopy(current['resource_limits'])},
                'complete_resource_review': {'sha256': 'registered-complete-resource-evidence'}}
        require_approved_execution_resources(baseline, current, plan)
        with self.assertRaises(ValueError):
            require_approved_execution_resources(baseline, current, {})
        for change in (
            lambda a: a['approval'].update(source='proposed_not_authorized'),
            lambda a: a['resource_limits']['cpu_seconds_per_phase'].update(fit=10001),
            lambda a: a['resource_limits'].update(maximum_derived_output_bytes=769 * 1024**2),
            lambda a: a['resource_limits'].update(memory_bytes=8 * 1024**3),
            lambda a: a['resource_limits'].update(maximum_attempts_total=25),
            lambda a: a['resource_limits'].update(cumulative_cpu_seconds_total=20001),
            lambda a: a['authorized_limits'].update(max_attempts=17),
            lambda a: a['base_protocol'].update(sha256='changed-science')):
            altered = deepcopy(current)
            change(altered)
            with self.assertRaises(ValueError):
                require_approved_execution_resources(baseline, altered, plan)
        protocol = {'family': baseline['family'], 'question': {'clocks': [5, 15]},
            'resources': {'mode_cpu_seconds': {'check': 90, 'develop': 480, 'confirm': 480},
                'memory_bytes': 4 * 1024**3, 'maximum_derived_output_bytes': 512 * 1024**2,
                'hard_cpu_margin_seconds': 10, 'wall_seconds': 900}}
        original = deepcopy(protocol)
        amended = amended_protocol(protocol, 'unchanged-science', current)
        self.assertEqual(protocol, original)
        self.assertEqual(amended['question'], original['question'])
        self.assertEqual(worker_limits(amended, 'fit')['hard_cpu_seconds'], 10010)
        self.assertEqual(worker_limits(amended, 'confirmation')['cpu_seconds'], 6500)
        self.assertEqual(worker_limits(amended, 'confirmation')['maximum_output_bytes'], 768 * 1024**2)


class ResourceDispatchTests(unittest.TestCase):
    def test_complete_model_workload_schema_runs_the_declared_annual_and_model_check(self):
        from trading_research.research.jumbo_parity import check_actual_extraction
        from types import SimpleNamespace
        execution={'version':'jumbo-complete-model-workload-v8'}
        store=SimpleNamespace(read_json=lambda reference:execution)
        packet={'execution_plan':{'sha256':'a'*64,'size_bytes':1,'kind':'literal_execution'}}
        with patch('trading_research.research.jumbo_parity._check_actual_annual_extraction',return_value={'sentinel':'complete'}) as annual:
            self.assertEqual(check_actual_extraction(packet,{},Path('.'),store),{'sentinel':'complete'})
        annual.assert_called_once_with(packet,{},Path('.'),store,execution)

    def test_unknown_or_missing_schema_cannot_fall_back_to_a_smaller_check(self):
        from trading_research.research.jumbo_parity import resource_check_route
        from trading_research.errors import IntegrityError
        for execution in ({},{'version':'typo'},{'version':'jumbo-complete-model-workload-v9'}):
            with self.assertRaises(IntegrityError):resource_check_route(execution)
        self.assertEqual(resource_check_route({'version':'jumbo-extraction-resume-performance-v1'}),'legacy_60_dates')
        self.assertEqual(resource_check_route({'version':'jumbo-extraction-resume-performance-v7'}),'annual_and_models')


class CompletedResourceEvidenceTests(unittest.TestCase):
    def setUp(self):
        import json
        self.root = Path(__file__).resolve().parents[1]
        self.review = json.loads((self.root / 'reports/jumbo-check15-extraction-reuse-failure-review.json').read_text())
        self.log = (self.root / self.review['worker_log']['path']).read_text()

    def test_all_completed_units_reconcile_to_the_original_log_and_incomplete_units_are_rejected(self):
        import json
        from trading_research.errors import IntegrityError
        from trading_research.research.jumbo_workload_reuse import _completed_expanded_rows
        result = _completed_expanded_rows(self.log)
        self.assertEqual(result, self.review['completed_expanded_resource_units'])
        lines = [line for line in self.log.splitlines() if line.startswith('{')]
        target = next(line for line in lines if json.loads(line).get('preflight') == 'completed_larger_tree_unit')
        for invalid in (self.log.replace(target, '', 1), self.log + '\n' + target):
            with self.assertRaises(IntegrityError):
                _completed_expanded_rows(invalid)
        altered = json.loads(target)
        altered['measurement']['cpu_seconds'] = -1
        with self.assertRaises(IntegrityError):
            _completed_expanded_rows(self.log.replace(target, json.dumps(altered), 1))

    def test_registered_completed_extraction_and_resource_units_require_unchanged_numerical_dependencies(self):
        import json
        from trading_research.errors import IntegrityError
        from trading_research.operations.trials import TrialRegistry
        from trading_research.research.jumbo_workload_reuse import (
            completed_development_extraction, retained_expanded_model_units)
        packet = json.loads((self.root / self.review['packet']['path']).read_text())
        plan = (self.root / 'validation/JUMBO_EXECUTION_V10.json').read_bytes()
        packet['execution_plan'] = {'sha256': hashlib.sha256(plan).hexdigest(),
            'size_bytes': len(plan), 'kind': 'jumbo_execution_plan_v1'}
        packet['code_manifest'] = {p: hashlib.sha256((self.root / p).read_bytes()).hexdigest()
                                   for p in packet['code_manifest']}
        registry = TrialRegistry(self.root / 'evidence/trials')
        protocol = {'family': self.review['family']}
        result = completed_development_extraction(packet, protocol, self.root, registry.artifacts)
        self.assertEqual(result['annual_shards'], 10)
        self.assertEqual(result['remaining_extraction_cpu_seconds'], 0.)
        expanded = retained_expanded_model_units(packet, protocol, self.root, registry.artifacts, [None] * 116)
        self.assertEqual(expanded['reuse']['original_attempt_status'], 'failed')
        self.assertEqual(expanded['reuse']['original_optimizer_calls'], 47)
        packet['code_manifest']['src/trading_research/research/jumbo_tables.py'] = 'changed'
        with self.assertRaises(IntegrityError):
            completed_development_extraction(packet, protocol, self.root, registry.artifacts)
        with self.assertRaises(IntegrityError):
            retained_expanded_model_units(packet, protocol, self.root, registry.artifacts, [None] * 116)


class IterativeWorkloadTests(unittest.TestCase):
    def test_fit_setup_is_not_repeated_for_each_projected_iteration(self):
        from trading_research.research.jumbo_preflight import iteration_cost
        result=iteration_cost({'iterations':10,'cpu_seconds':10.},
                              {'iterations':20,'cpu_seconds':15.},100)
        self.assertEqual(result['fixed_cpu_seconds'],5.)
        self.assertEqual(result['variable_cpu_seconds_per_unit'],.5)
        self.assertEqual(result['cpu_seconds'],55.)

    def test_early_convergence_does_not_imply_zero_cost_for_a_larger_full_fit(self):
        from trading_research.research.jumbo_preflight import iteration_cost
        result=iteration_cost({'iterations':8,'cpu_seconds':4.},
                              {'iterations':8,'cpu_seconds':5.},100)
        self.assertEqual(result['cpu_seconds'],62.5)
        self.assertIn('identification',result)


class PhaseContractTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.sources = {
            "src/trading_research/research/jumbo_study.py":
                "from trading_research.research import extract_only, fit_only\n",
            "src/trading_research/research/extract_only.py":
                "from . import common\nVALUE = 1\n",
            "src/trading_research/research/fit_only.py":
                "from .common import VALUE\nMODEL = 1\n",
            "src/trading_research/research/common.py":"VALUE = 5\n",
            "src/trading_research/research/unrelated.py":"DO_NOT_IMPORT = True\n",
            "tests/test_extract_literal.py":"# exact extraction test\n",
            "tests/test_fit_literal.py":"# exact fit test\n",
        }
        self.manifest = {}
        for path,raw in self.sources.items():
            self.write(path,raw)
        self.entries = {
            "extract":("jumbo_study","extract_only"),
            "fit":("jumbo_study","fit_only"),
            "confirmation":("jumbo_study","extract_only","fit_only"),
            "admission":("jumbo_study",),
        }
        self.tests = {"extract":("test_extract_literal",),"fit":("test_fit_literal",),
                      "confirmation":(),"admission":()}
        stack = ExitStack()
        self.addCleanup(stack.close)
        stack.enter_context(patch.object(verification,"ENTRYPOINTS",self.entries))
        stack.enter_context(patch.object(verification,"TESTS",self.tests))
        stack.enter_context(patch.object(verification,"PHASE_DISPATCH_MODULES",
                            {"trading_research.research."+name for names in self.entries.values() for name in names}))

    def write(self,path,raw):
        file = self.root/path
        file.parent.mkdir(parents=True,exist_ok=True)
        file.write_text(raw)
        self.manifest[path] = hashlib.sha256(raw.encode()).hexdigest()

    def contracts(self, **changes):
        kwargs = dict(analysis_plan={"sha256":"analysis"},execution_plan={"sha256":"execution"},
                      model_plan={"sha256":"model"},runtime_versions={"numpy":"literal-v1"})
        kwargs.update(changes)
        return verification.phase_contracts(self.root,self.manifest,**kwargs)

    def test_unrelated_changes_preserve_relevant_contracts(self):
        before = self.contracts()
        self.write("src/trading_research/research/unrelated.py","raise RuntimeError('must never import')\n")
        after = self.contracts()
        self.assertEqual(before,after)
        self.assertTrue(all("unrelated.py" not in " ".join(c["source_and_test_files"]) for c in after.values()))

    def test_phase_dispatch_boundaries_and_shared_dependency(self):
        before = self.contracts()
        self.write("src/trading_research/research/fit_only.py","from .common import VALUE\nMODEL = 2\n")
        changed_fit = self.contracts()
        self.assertEqual(before["extract"],changed_fit["extract"])
        self.assertNotEqual(before["fit"]["id"],changed_fit["fit"]["id"])
        self.assertNotEqual(before["confirmation"]["id"],changed_fit["confirmation"]["id"])
        self.write("src/trading_research/research/common.py","VALUE = 6\n")
        shared = self.contracts()
        self.assertNotEqual(changed_fit["extract"]["id"],shared["extract"]["id"])
        self.assertNotEqual(changed_fit["fit"]["id"],shared["fit"]["id"])

    def test_runtime_provider_and_model_plan_are_bound_to_intended_scope(self):
        before = self.contracts()
        runtime = self.contracts(runtime_versions={"numpy":"literal-v2"})
        self.assertTrue(all(before[p]["id"]!=runtime[p]["id"] for p in before))
        model = self.contracts(model_plan={"sha256":"different-model"})
        self.assertEqual(before["extract"],model["extract"])
        self.assertEqual(before["admission"],model["admission"])
        self.assertNotEqual(before["fit"]["id"],model["fit"]["id"])
        self.assertNotEqual(before["confirmation"]["id"],model["confirmation"]["id"])

    def test_source_drift_rejected_against_exact_snapshot(self):
        path = self.root/"src/trading_research/research/common.py"
        path.write_text("VALUE = 500\n")
        with self.assertRaises(ValueError):
            self.contracts()

    def test_test_bytes_rechecked_not_only_declared_manifest_hash(self):
        (self.root/"tests/test_fit_literal.py").write_text("# changed without a new snapshot\n")
        with self.assertRaises(ValueError):
            self.contracts()

    def test_missing_required_test_or_entry_fails_closed(self):
        del self.manifest["tests/test_fit_literal.py"]
        with self.assertRaises(ValueError):
            self.contracts()
        self.write("tests/test_fit_literal.py","# restored\n")
        del self.manifest["src/trading_research/research/fit_only.py"]
        with self.assertRaises(ValueError):
            self.contracts()

    def test_confirmation_binds_both_consumer_test_populations(self):
        result = self.contracts()
        paths = result["confirmation"]["source_and_test_files"]
        self.assertIn("tests/test_extract_literal.py",paths)
        self.assertIn("tests/test_fit_literal.py",paths)
        self.assertNotIn("tests/test_fit_literal.py",result["extract"]["source_and_test_files"])
        self.assertNotIn("tests/test_extract_literal.py",result["fit"]["source_and_test_files"])


class RetainedAnnualStageTests(unittest.TestCase):
    def test_nested_reuse_branch_retains_exact_measurement_but_changed_algorithm_fails(self):
        block = ('batch = {"formations": [], "paths": [], "specials": []}\n'
                 'statistics = measure(batch, replicates=1000)\n'
                 'payload = serialize(statistics, level=3)\n'
                 'del payload, compressed_statistics, original_statistics, statistics\n')
        source = 'def _check_actual_annual_extraction():\n' + ''.join('    '+s+'\n' for s in block.splitlines())
        nested = ('def _check_actual_annual_extraction():\n    if reuse:\n        load_saved()\n    else:\n'
                  + ''.join('        '+s+'\n' for s in block.splitlines()) + '    changed_consumer()\n')
        self.assertEqual(verification.annual_stage_fingerprint(source), verification.annual_stage_fingerprint(nested))
        self.assertNotEqual(verification.annual_stage_fingerprint(source),
                            verification.annual_stage_fingerprint(nested.replace('replicates=1000', 'replicates=999')))

    def test_serialization_function_identity_ignores_unrelated_function_only(self):
        source = 'def serialize(x):\n    return compress(x, level=3)\ndef unrelated():\n    return 0\n'
        identity = verification.retained_function_fingerprint(source, 'serialize')
        self.assertEqual(identity, verification.retained_function_fingerprint(source.replace('return 0', 'return 1'), 'serialize'))
        self.assertNotEqual(identity, verification.retained_function_fingerprint(source.replace('level=3', 'level=4'), 'serialize'))


class WorkerReportAccountingTests(unittest.TestCase):
    def test_exact_disk_and_cas_serializations_close_at_the_byte_boundary(self):
        from trading_research.operations.artifacts import canonical_json
        from tools.run_jumbo_study import accounted_worker_report, encoded
        original = {"success":True,"derived_output_bytes":999,"message":"literal café"}
        result,payload = accounted_worker_report(original,100000)
        self.assertEqual(payload,encoded(result))
        self.assertEqual(result["worker_report_disk_bytes"],len(payload))
        self.assertEqual(result["worker_report_cas_bytes"],len(canonical_json(result)))
        self.assertEqual(result["derived_output_bytes"],999+len(payload)+len(canonical_json(result)))
        self.assertEqual(result["derived_output_before_worker_report_bytes"],999)
        # The cap itself is not serialized, so an exact-boundary rerun must
        # produce identical bytes and one byte less must fail before publishing.
        exact,payload_exact = accounted_worker_report(original,result["derived_output_bytes"])
        self.assertEqual((exact,payload_exact),(result,payload))
        with self.assertRaises(ValueError):
            accounted_worker_report(original,result["derived_output_bytes"]-1)
        self.assertEqual(original,{"success":True,"derived_output_bytes":999,"message":"literal café"})

    def test_no_derived_output_report_contract_is_unchanged(self):
        from tools.run_jumbo_study import accounted_worker_report, encoded
        report = {"mode":"check","tests":3,"success":True}
        result,payload = accounted_worker_report(report,0)
        self.assertEqual(result,report)
        self.assertEqual(payload,encoded(report))
        self.assertNotIn("derived_output_bytes",result)

    def test_lossy_or_negative_derived_output_counts_are_rejected(self):
        from tools.run_jumbo_study import accounted_worker_report
        for value in (-1,True,1.5):
            with self.assertRaises(ValueError):
                accounted_worker_report({"derived_output_bytes":value},10000)


class TwoSizeWorkloadTests(unittest.TestCase):
    def test_fixed_and_variable_terms_are_separate(self):
        from trading_research.research.jumbo_preflight import two_size_cost
        result = two_size_cost(3.,5.,10,20,100)
        self.assertAlmostEqual(result["fixed_cpu_seconds"],1.)
        self.assertAlmostEqual(result["variable_cpu_seconds_per_unit"],.2)
        self.assertAlmostEqual(result["cpu_seconds"],21.)
        self.assertEqual(result["planned_units"],100)
        # Multiplying the entire large measurement by five would report25,
        # which incorrectly scales its fixed reporting overhead five times.
        self.assertLess(result["cpu_seconds"],5.*100/20)

    def test_flat_or_noisy_timings_retain_nonzero_marginal_floor(self):
        from trading_research.research.jumbo_preflight import two_size_cost
        flat = two_size_cost(20.,20.,10,20,100)
        self.assertEqual(flat["variable_cpu_seconds_per_unit"],.5)
        self.assertEqual(flat["fixed_cpu_seconds"],15.)
        self.assertEqual(flat["cpu_seconds"],65.)
        noisy = two_size_cost(6.,4.,10,20,100)
        self.assertEqual(noisy["variable_cpu_seconds_per_unit"],.1)
        self.assertEqual(noisy["fixed_cpu_seconds"],5.)
        self.assertEqual(noisy["cpu_seconds"],15.)
        self.assertGreaterEqual(noisy["fixed_cpu_seconds"]+10*noisy["variable_cpu_seconds_per_unit"],6.)
        self.assertGreaterEqual(noisy["fixed_cpu_seconds"]+20*noisy["variable_cpu_seconds_per_unit"],4.)

    def test_invalid_numeric_measurements_and_unit_order_are_rejected(self):
        from trading_research.errors import IntegrityError
        from trading_research.research.jumbo_preflight import two_size_cost
        for args in ((-1.,2.,10,20,100),(1.,float("inf"),10,20,100),
                     (float("nan"),2.,10,20,100),(1.,2.,0,20,100),
                     (1.,2.,20,20,100),(1.,2.,21,20,100),
                     (1.,2.,10,20,0),(1.,2.,10,20,-1),
                     (1.,2.,10,float("inf"),100)):
            with self.subTest(args=args),self.assertRaises(IntegrityError):
                two_size_cost(*args)

    def test_workload_units_are_exact_integers_and_timings_are_numeric(self):
        from trading_research.errors import IntegrityError
        from trading_research.research.jumbo_preflight import two_size_cost
        for args in ((True,2.,10,20,100),(None,2.,10,20,100),
                     ("1",2.,10,20,100),(1.,2.,True,20,100),
                     (1.,2.,10.,20,100),(1.,2.,10,20.5,100),
                     (1.,2.,10,20,"100"),(1.,2.,10,20,100.1),
                     (1.,2.,10,20,10**1000)):
            with self.subTest(args=args),self.assertRaises(IntegrityError):
                two_size_cost(*args)
