"""Primary-period admission tests bound to the real public research paths."""

from dataclasses import replace
from datetime import date
from decimal import Decimal
from pathlib import Path
import json
import tempfile
import unittest

from trading_research.data.cohorts import CohortEvidence, CohortRegistry
from trading_research.errors import ContractError, DependencyUnavailable, IntegrityError
from trading_research.foundations.cash_calendar import CashDay, VenueBoundary, e0_window
from trading_research.foundations.contracts import InstrumentKey
from trading_research.foundations.instruments import InstrumentDefinition
from trading_research.foundations.time import AvailabilityBasis, Clocks
from trading_research.operations.artifacts import ArtifactRef, ArtifactStore, canonical_json, digest
from trading_research.operations.provenance import InputValue
from trading_research.research.calibration import fit_sigmoid_calibration
from trading_research.research.folds import (Fold, Sample, chronological_fold,
    chronological_primary_fold, validate_fold_population)
from trading_research.research.models import BinaryExample, fit_frequency, fit_logistic, preflight_training
from trading_research.research.period import (PRIMARY_START_NS_UTC, PrimaryAdmissionV1,
    ResearchPeriodPolicyV1, ResearchScopeV1, check_cohort_bounds, check_protocol_dates)
from trading_research.research.protocols import Candidate, EvaluationRegistry, Protocol
from trading_research.research.scoring import IntervalSpec, Metric
from trading_research.research.temporal_folds import (TemporalDependencyV1, TemporalSampleV1,
    compile_temporal_fold, validate_temporal_fold_population, validate_dependency_bytes)


ROOT = Path(__file__).parents[1]
GOLDEN = json.loads((ROOT / "tests/golden/primary_period_admission_v1.json").read_text())
CASES = {case["id"]: case for case in GOLDEN["cases"]}


def golden(number):
    return next(case for identity, case in CASES.items() if identity.startswith(f"PERIOD-{number:02d}-"))


def literal_cohort(registry_, number):
    literal = golden(number)["literal"]
    body = dict(literal["cohort_evidence"])
    body["dependent_units"] = tuple(body["dependent_units"])
    body["evidence"] = registry_.artifacts.put_json(literal["artifact_certification"], kind="primary-period-fixture")
    return CohortEvidence(**body)



def policy():
    return ResearchPeriodPolicyV1.from_config(ROOT / "configs" / "research-period.json")


def primary_scope(period, cohort="fixture-primary"):
    return ResearchScopeV1.primary(cohort_id=cohort, denominator_id="fixture-primary-denominator", policy=period)


def cohort_record(registry, *, record_id, state="eligible", depth="complete_window",
                  observation_start=PRIMARY_START_NS_UTC, observation_end=PRIMARY_START_NS_UTC + 1,
                  next_action=None, dataset_id="fixture/dataset", operation="quote_replay"):
    cohort_id = record_id + "-cohort"
    field = "bid_px"
    ref = registry.artifacts.put_json({
        "success": True,
        "certification": {
            "datasets": [dataset_id], "cohort_id": cohort_id,
            "operations": [operation], "fields": [field], "depth": depth,
        },
    }, kind="primary-period-fixture")
    return CohortEvidence(record_id, dataset_id, field, cohort_id, operation, state, depth,
                          "fixture-source-v1", "fixture-definition-v1", "fixture-code-v1",
                          observation_start, observation_end, None, ref,
                          "fixture evidence", (), next_action)


def cohort_admission(record, scope, period, cut=PRIMARY_START_NS_UTC + 10):
    return PrimaryAdmissionV1.from_population((record,), scope=scope, policy=period,
                                              actual_cut_at=cut)


def registry(tmp, dataset_id="fixture/dataset", field="bid_px"):
    catalog = tmp / "catalog.json"
    schemas = tmp / "schemas.json"
    catalog.write_text(json.dumps({"datasets": [{"dataset_id": dataset_id, "status": "complete"}]}))
    schemas.write_text(json.dumps({dataset_id: {"fields": [field]}}))
    return CohortRegistry(tmp / "readiness", catalog_path=catalog, schemas_path=schemas,
                          expected_dataset_ids=frozenset({dataset_id}),
                          prior_audit_references=())


def input_value(sample, value):
    return InputValue("x", digest((sample.id, value)), sample.decision_at, canonical_json(value))


def binary_examples(samples):
    return tuple(BinaryExample(sample, (input_value(sample, float(i + 1)),), i % 2)
                 for i, sample in enumerate(samples))


def candidate(identifier, information=()):
    return Candidate(identifier, information, "repr-v1", "learner-v1", "generator-v1",
                     "policy-v1", 1, 1)


def protocol(*, dates, sample_manifest_hash, registered_at, endpoint_at):
    return Protocol("primary-period-protocol", "primary-period-selection", ("fixture-cohort",),
                    "target-v1", "fixture mechanism", "information",
                    (candidate("base", ()), candidate("challenger", ("x",))),
                    Metric("brier"), IntervalSpec(.95, 200, 7, 1, 2), .01, .01, .5,
                    tuple(dates), sample_manifest_hash, "future_confirmation",
                    PRIMARY_START_NS_UTC, endpoint_at, registered_at,
                    "literal primary-period admission fixture")


class PrimaryPeriodAdmissionTests(unittest.TestCase):
    def test_PERIOD_01_before_boundary_rejects_primary_cohort(self):
        period = policy()
        scope = primary_scope(period, "period-01")
        with tempfile.TemporaryDirectory() as root:
            body = golden(1)["literal"]["cohort_evidence"]
            registry_ = registry(Path(root), body["dataset_id"], body["field"])
            record = literal_cohort(registry_, 1)
            admission = cohort_admission(record, scope, period, cut=PRIMARY_START_NS_UTC + 2_000_000_000)
            with self.assertRaisesRegex(ContractError, golden(1)["expected"]["required_message"]):
                registry_.append_primary(record, scope=scope, policy=period,
                                         actual_cut_at=PRIMARY_START_NS_UTC + 2_000_000_000,
                                         admission=admission)
            self.assertEqual(registry_.audit()["cohort_evidence_count"], 0)

    def test_PERIOD_02_exact_boundary_passes_period_and_appends(self):
        period = policy()
        scope = primary_scope(period, "period-02")
        with tempfile.TemporaryDirectory() as root:
            body = golden(2)["literal"]["cohort_evidence"]
            registry_ = registry(Path(root), body["dataset_id"], body["field"])
            record = literal_cohort(registry_, 2)
            admission = cohort_admission(record, scope, period, cut=PRIMARY_START_NS_UTC + 2_000_000_000)
            bad_config = Path(root) / "bad-research-period.json"
            bad_config.write_text((ROOT / "configs" / "research-period.json").read_text().replace(
                "Jumbo source constructions and comparisons",
                "Jumbo source constructions and comparisons (unregistered)"))
            with self.assertRaisesRegex(ContractError, "optional uses differ"):
                ResearchPeriodPolicyV1.from_config(bad_config)
            with self.assertRaisesRegex(ContractError, "typed ResearchScopeV1"):
                registry_.append_primary(record, scope="primary_model", policy=period,
                                         actual_cut_at=PRIMARY_START_NS_UTC + 2_000_000_000,
                                         admission=admission)
            registry_.append_primary(record, scope=scope, policy=period,
                                     actual_cut_at=PRIMARY_START_NS_UTC + 2_000_000_000,
                                     admission=admission)
            self.assertEqual(registry_.audit()["cohort_evidence_count"], 1)

    def test_PERIOD_03_prefix_without_range_stays_observed_only(self):
        period = policy()
        scope = primary_scope(period, "period-03")
        with tempfile.TemporaryDirectory() as root:
            body = golden(3)["literal"]["cohort_evidence"]
            registry_ = registry(Path(root), body["dataset_id"], body["field"])
            record = literal_cohort(registry_, 3)
            admission = cohort_admission(record, scope, period, cut=PRIMARY_START_NS_UTC + 2_000_000_000)
            with self.assertRaisesRegex(ContractError, golden(3)["expected"]["required_message"]):
                registry_.append_primary(record, scope=scope, policy=period,
                                         actual_cut_at=PRIMARY_START_NS_UTC + 2_000_000_000,
                                         admission=admission)
            self.assertEqual(registry_.audit()["cohort_evidence_count"], 0)
            diagnostic = ResearchScopeV1.diagnostic(cohort_id=record.cohort_id,
                denominator_id="period03-diagnostic-only")
            retained = replace(record, next_action=golden(3)["expected"]["next_action"])
            registry_.append(retained, scope=diagnostic)
            payload = registry_.journal.read()[-1]["payload"]
            self.assertEqual(payload["record"]["state"], "observed")
            self.assertEqual(payload["record"]["next_action"], golden(3)["expected"]["next_action"])
            self.assertEqual(payload["research_scope"]["purpose_scope"], "diagnostic")
            self.assertNotIn("primary_admission", payload)

    def test_PERIOD_04_fold_model_calibration_and_temporal_paths_recheck_population(self):
        period = policy()
        scope = primary_scope(period, "period-04")
        literal = golden(4)["literal"]
        before, boundary = tuple(Sample(**row) for row in literal["legacy_samples"])
        clocks = literal["fold_clocks"]
        period_message = golden(4)["expected"]["required_message"]
        rejected_admission = PrimaryAdmissionV1.from_population(
            (before, boundary), scope=scope, policy=period,
            actual_cut_at=PRIMARY_START_NS_UTC + 10_000_000_000)
        with self.assertRaisesRegex(ContractError, period_message):
            chronological_fold((before, boundary), **clocks, scope=scope, policy=period,
                               admission=rejected_admission)
        direct_body = dict(literal["direct_legacy_fold_declaration"])
        for name in ("training_ids", "evaluation_ids", "purged"):
            direct_body[name] = tuple(direct_body[name])
        direct = Fold(**direct_body)
        examples = binary_examples((before, boundary))
        with self.assertRaisesRegex(ContractError, period_message):
            validate_fold_population((before, boundary), direct, scope=scope, policy=period,
                                     admission=rejected_admission)
        with self.assertRaisesRegex(ContractError, period_message):
            preflight_training(examples, direct, scope=scope, policy=period,
                               admission=rejected_admission)
        with self.assertRaisesRegex(ContractError, period_message):
            fit_frequency(examples, direct, ("x",), cuts=((0.0,),), scope=scope, policy=period,
                          admission=rejected_admission)
        with self.assertRaisesRegex(ContractError, period_message):
            fit_logistic(examples, direct, ("x",), l2_strength=.1, scope=scope, policy=period,
                         admission=rejected_admission)
        with self.assertRaisesRegex(ContractError, period_message):
            fit_sigmoid_calibration(None, examples, direct, l2_strength=.1,
                                    scope=scope, policy=period, admission=rejected_admission)

        dependency_body = dict(literal["temporal_dependency"])
        evidence_format = dependency_body.pop("evidence_payload_format")
        payload = canonical_json({"format": evidence_format, **dependency_body})
        with tempfile.TemporaryDirectory() as dependency_root:
            ref = ArtifactStore(Path(dependency_root)).put_bytes(payload, kind="temporal-dependency")
            dependency = TemporalDependencyV1(**dependency_body, evidence_ref=ref)
            validate_dependency_bytes(dependency, {ref.sha256: payload})
        temporal_rows = tuple(TemporalSampleV1(**{
            **row, "parent_groups": tuple(row["parent_groups"]),
            "dependencies": tuple(dependency for identity in row["dependencies"]
                                  if identity == dependency.id),
        }) for row in literal["temporal_samples"])
        temporal = temporal_rows[1]
        for row in temporal_rows:
            with self.assertRaisesRegex(ContractError, period_message):
                compile_temporal_fold((row,), **clocks, scope=scope, policy=period,
                    admission=PrimaryAdmissionV1.from_population((row,), scope=scope,
                        policy=period, actual_cut_at=PRIMARY_START_NS_UTC + 10_000_000_000))
        with self.assertRaisesRegex(ContractError, period_message):
            compile_temporal_fold((temporal,), id="period-04-temporal",
                                  fit_at=PRIMARY_START_NS_UTC + 4_000_000_000,
                                  evaluation_start=PRIMARY_START_NS_UTC + 5_000_000_000,
                                  evaluation_end=PRIMARY_START_NS_UTC + 6_000_000_000,
                                  scope=scope, policy=period,
                                  admission=PrimaryAdmissionV1.from_population(
                                      (temporal,), scope=scope, policy=period,
                                      actual_cut_at=PRIMARY_START_NS_UTC + 10_000_000_000))
        legacy_temporal_fold = compile_temporal_fold(
            (temporal,), id="period-04-temporal-legacy",
            fit_at=PRIMARY_START_NS_UTC + 4_000_000_000,
            evaluation_start=PRIMARY_START_NS_UTC + 5_000_000_000,
            evaluation_end=PRIMARY_START_NS_UTC + 6_000_000_000)
        with self.assertRaisesRegex(ContractError, period_message):
            validate_temporal_fold_population((temporal,), legacy_temporal_fold,
                                              scope=scope, policy=period,
                                              admission=PrimaryAdmissionV1.from_population(
                                                  (temporal,), scope=scope, policy=period,
                                                  actual_cut_at=PRIMARY_START_NS_UTC + 10_000_000_000))

        from tests.measurement_fit_sources import fitted_sources
        from trading_research.measurements.measurement_fits import admit_measurement_fit
        with tempfile.TemporaryDirectory() as root:
            fitted = fitted_sources(Path(root), family="period04", parameters={},
                                    recipe_id="period04-recipe", state={"state": "fixture"},
                                    training_features=({"x": 1.0}, {"x": 2.0}),
                                    query_features={"x": 3.0})
            population = fitted["fold_node"].fold_evidence.population
            measurement_admission = PrimaryAdmissionV1.from_population(
                population, scope=scope, policy=period, actual_cut_at=PRIMARY_START_NS_UTC + 100)
            with self.assertRaisesRegex(ContractError, "pre_period_training_or_dependency"):
                admit_measurement_fit(fitted["store"], fitted["commit"], fitted["transform"].id,
                                      fitted["request"], schema_id="MeasurementFixture.v1",
                                      unit="descriptive_measurement", recipe_id="period04-recipe",
                                      scope=scope, policy=period, admission=measurement_admission)

        positive = (
            Sample("a", "2020-01-01", PRIMARY_START_NS_UTC,
                   PRIMARY_START_NS_UTC + 1, PRIMARY_START_NS_UTC, "target-v1"),
            Sample("b", "2020-01-02", PRIMARY_START_NS_UTC + 1,
                   PRIMARY_START_NS_UTC + 2, PRIMARY_START_NS_UTC + 1, "target-v1"),
        )
        admission = PrimaryAdmissionV1.from_population(
            positive, scope=scope, policy=period, actual_cut_at=PRIMARY_START_NS_UTC + 10)
        with self.assertRaisesRegex(ContractError, "primary consumers require an immutable population admission envelope"):
            chronological_fold(positive, id="period-04-missing-admission",
                               fit_at=PRIMARY_START_NS_UTC + 3,
                               evaluation_start=PRIMARY_START_NS_UTC + 4,
                               evaluation_end=PRIMARY_START_NS_UTC + 5,
                               scope=scope, policy=period)
        with self.assertRaisesRegex(ContractError, "typed ResearchScopeV1"):
            chronological_primary_fold(positive, id="period-04-malformed-scope",
                                        fit_at=PRIMARY_START_NS_UTC + 3,
                                        evaluation_start=PRIMARY_START_NS_UTC + 4,
                                        evaluation_end=PRIMARY_START_NS_UTC + 5,
                                        scope="primary_model", policy=period,
                                        admission=admission)
        too_early_cut = PrimaryAdmissionV1.from_population(
            positive, scope=scope, policy=period, actual_cut_at=PRIMARY_START_NS_UTC + 2)
        with self.assertRaisesRegex(ContractError, "post_cut_training_or_dependency"):
            chronological_fold(positive, id="period-04-post-cut",
                               fit_at=PRIMARY_START_NS_UTC + 3,
                               evaluation_start=PRIMARY_START_NS_UTC + 4,
                               evaluation_end=PRIMARY_START_NS_UTC + 5,
                               scope=scope, policy=period, admission=too_early_cut)
        fold = chronological_primary_fold(positive, id="period-04-positive",
                                          fit_at=PRIMARY_START_NS_UTC + 3,
                                          evaluation_start=PRIMARY_START_NS_UTC + 4,
                                          evaluation_end=PRIMARY_START_NS_UTC + 5,
                                          scope=scope, policy=period, admission=admission)
        rows = binary_examples(positive)
        model = fit_frequency(rows, fold, ("x",), cuts=((0.0,),), scope=scope,
                              policy=period, admission=admission)
        self.assertEqual(model._period_policy_hash, period.config_hash)
        calibration_population = (
            Sample("cal-a", "2020-01-03", PRIMARY_START_NS_UTC + 6,
                   PRIMARY_START_NS_UTC + 7, PRIMARY_START_NS_UTC + 6, "target-v1"),
            Sample("cal-b", "2020-01-04", PRIMARY_START_NS_UTC + 7,
                   PRIMARY_START_NS_UTC + 8, PRIMARY_START_NS_UTC + 7, "target-v1"),
            Sample("heldout", "2020-01-05", PRIMARY_START_NS_UTC + 10,
                   PRIMARY_START_NS_UTC + 11, PRIMARY_START_NS_UTC + 10, "target-v1"),
        )
        calibration_admission = PrimaryAdmissionV1.from_population(
            calibration_population, scope=scope, policy=period, actual_cut_at=PRIMARY_START_NS_UTC + 12)
        calibration_fold = chronological_primary_fold(calibration_population, id="period04-calibration",
            fit_at=PRIMARY_START_NS_UTC + 9, evaluation_start=PRIMARY_START_NS_UTC + 10,
            evaluation_end=PRIMARY_START_NS_UTC + 12, scope=scope, policy=period,
            admission=calibration_admission)
        calibration_rows = binary_examples(calibration_population)
        calibrated = fit_sigmoid_calibration(model, calibration_rows, calibration_fold, l2_strength=.1,
            scope=scope, policy=period, admission=calibration_admission)
        self.assertEqual(calibrated.base.id, model.id)
        self.assertEqual(calibrated._period_policy_hash, period.config_hash)
        probability, prediction = calibrated.predict(calibration_rows[-1])
        self.assertTrue(0 <= probability <= 1)
        self.assertIn(model.id, prediction["fit_closure"])
        self.assertFalse(set(fold.training_ids) & set(calibration_fold.training_ids))
        # Admission/compiler/preflight use identical existing typed fold order.
        reverse_admission = PrimaryAdmissionV1.from_population(tuple(reversed(positive)),
            scope=scope, policy=period, actual_cut_at=admission.actual_cut_at)
        self.assertEqual(reverse_admission, admission)
        reverse_fold = chronological_primary_fold(tuple(reversed(positive)), id=fold.id,
            fit_at=fold.fit_at, evaluation_start=fold.evaluation_start, evaluation_end=fold.evaluation_end,
            scope=scope, policy=period, admission=reverse_admission)
        self.assertEqual(reverse_fold, fold)
        self.assertEqual(fit_frequency(tuple(reversed(rows)), fold, ("x",), cuts=((0.0,),),
            scope=scope, policy=period, admission=reverse_admission).id, model.id)
        for altered in (positive[:1], (replace(positive[0], dependency_end=PRIMARY_START_NS_UTC + 1), positive[1])):
            with self.assertRaisesRegex(IntegrityError, "immutable admission hash"):
                admission.validate_population(altered, policy=period)
        with self.assertRaisesRegex(ContractError, "duplicate sample identity"):
            PrimaryAdmissionV1.from_population((positive[0], positive[0]), scope=scope,
                policy=period, actual_cut_at=admission.actual_cut_at)

        from trading_research.measurements.measurement_fits import (
            read_measurement_query, validate_measurement_fit_payload)
        with tempfile.TemporaryDirectory() as root:
            fitted = fitted_sources(Path(root), family="period04-positive", parameters={},
                recipe_id="period04-positive-recipe", state={"state": "fixture"},
                training_features=({"x": 1.0}, {"x": 2.0}), query_features={"x": 3.0},
                clock_offset=PRIMARY_START_NS_UTC)
            population = fitted["fold_node"].fold_evidence.population
            actual = PrimaryAdmissionV1.from_population(tuple(reversed(population)), scope=scope,
                policy=period, actual_cut_at=PRIMARY_START_NS_UTC + 60)
            retained = admit_measurement_fit(fitted["store"], fitted["commit"], fitted["transform"].id,
                fitted["request"], schema_id="MeasurementFixture.v1", unit="descriptive_measurement",
                recipe_id=fitted["recipe_id"], scope=scope, policy=period, admission=actual)
            self.assertEqual(retained.population, population)
            self.assertEqual(validate_measurement_fit_payload(retained, fitted["payload"]), retained)
            self.assertEqual(read_measurement_query(retained, fitted["query_session"],
                window_start=PRIMARY_START_NS_UTC + 39, columns=("x",)), {"x": 3.0})
            fitted["query_session"].seal()
            self.assertEqual(read_measurement_query(retained, fitted["query_session"],
                window_start=PRIMARY_START_NS_UTC + 39, columns=("x",)), {"x": 3.0})
            tf = retained.fold
            self.assertEqual(compile_temporal_fold(tuple(reversed(population)), id=tf.id,
                fit_at=tf.fit_at, evaluation_start=tf.evaluation_start, evaluation_end=tf.evaluation_end,
                scope=scope, policy=period, admission=actual), tf)
            for changed in (None, replace(actual, population_hash="f" * 64),
                            replace(actual, actual_cut_at=PRIMARY_START_NS_UTC + 59)):
                with self.assertRaises((ContractError, IntegrityError)):
                    admit_measurement_fit(fitted["store"], fitted["commit"], fitted["transform"].id,
                        fitted["request"], schema_id="MeasurementFixture.v1", unit="descriptive_measurement",
                        recipe_id=fitted["recipe_id"], scope=scope, policy=period, admission=changed)
            for altered in (population[:1], (replace(population[0], endpoint_group="changed"), *population[1:])):
                with self.assertRaisesRegex(IntegrityError, "immutable admission hash"):
                    actual.validate_population(altered, policy=period)
            with self.assertRaisesRegex(ContractError, "duplicate sample identity"):
                PrimaryAdmissionV1.from_population((population[0], population[0]), scope=scope,
                    policy=period, actual_cut_at=actual.actual_cut_at)

    def test_PERIOD_05_protocol_rejects_preperiod_date_and_runs_corrected_path(self):
        period = policy()
        scope = primary_scope(period, "period-05")
        population = ("2020-01-01-row", "2020-01-02-row")
        admission = PrimaryAdmissionV1.from_population(
            population, scope=scope, policy=period, actual_cut_at=PRIMARY_START_NS_UTC + 10)
        with tempfile.TemporaryDirectory() as root:
            registry_ = EvaluationRegistry(Path(root) / "evaluation.sqlite")
            literal = golden(5)["literal"]
            original = replace(protocol(dates=literal["ordered_dates"],
                sample_manifest_hash=literal["sample_manifest_hash"],
                registered_at=literal["registered_at"], endpoint_at=literal["endpoint_at"]),
                id=literal["protocol_id"], evaluation_start_at=literal["evaluation_start_at"],
                role=literal["role"])
            with self.assertRaisesRegex(ContractError, golden(5)["expected"]["required_message"]):
                registry_.register(original, scope=scope, policy=period)
            corrected_literal = replace(original, **{
                **literal["corrected_variant"],
                "ordered_dates": tuple(literal["corrected_variant"]["ordered_dates"]),
            })
            self.assertEqual(check_protocol_dates(scope, period, corrected_literal.ordered_dates,
                evaluation_start_at=corrected_literal.evaluation_start_at,
                endpoint_at=corrected_literal.endpoint_at, actual_cut_at=admission.actual_cut_at),
                corrected_literal.ordered_dates)
            # Separate registration control replaces the non-SHA fixture marker
            # with the exact actual retained population identity.
            corrected = replace(corrected_literal, sample_manifest_hash=admission.population_hash)
            registry_.register_primary(corrected, scope=scope, policy=period, admission=admission)
            registry_.begin_primary(corrected,
                                    model_artifacts={"base": "base-hash", "challenger": "challenger-hash"},
                                    started_at=PRIMARY_START_NS_UTC - 1,
                                    scope=scope, policy=period, admission=admission)
            report = {"protocol_version": corrected.version,
                      "sample_manifest_hash": corrected.sample_manifest_hash}
            registered = registry_.journal.read()[0]["payload"]
            self.assertEqual(registered["research_scope"], {
                "purpose_scope": "primary_model",
                "cohort_id": scope.cohort_id,
                "denominator_id": scope.denominator_id,
                "policy_hash": period.config_hash,
            })
            self.assertEqual(registered["primary_admission"]["population_hash"], admission.population_hash)
            self.assertEqual(registered["actual_cut_at"], admission.actual_cut_at)

            reopened = EvaluationRegistry(Path(root) / "evaluation.sqlite")
            self.assertEqual(reopened.journal.read(), registry_.journal.read())
            before_attempts = reopened.journal.read()
            with self.assertRaisesRegex(IntegrityError, "immutable registration"):
                reopened.begin(corrected,
                               model_artifacts={"base": "base-hash", "challenger": "challenger-hash"},
                               started_at=PRIMARY_START_NS_UTC - 1)
            self.assertEqual(reopened.journal.read(), before_attempts)
            with self.assertRaisesRegex(IntegrityError, "immutable registration"):
                reopened.finish(corrected, report=report, finished_at=corrected.endpoint_at + 1)
            self.assertEqual(reopened.journal.read(), before_attempts)

            diagnostic = ResearchScopeV1.diagnostic(cohort_id="period-05",
                                                     denominator_id="fixture-primary-denominator")
            with self.assertRaisesRegex(IntegrityError, "immutable registration"):
                reopened.finish(corrected, report=report, finished_at=corrected.endpoint_at + 1,
                                scope=diagnostic, policy=period)
            self.assertEqual(reopened.journal.read(), before_attempts)

            changed_cut = PrimaryAdmissionV1.from_population(
                population, scope=scope, policy=period,
                actual_cut_at=admission.actual_cut_at + 1)
            with self.assertRaisesRegex(IntegrityError, "scope/policy/population/cut differs"):
                reopened.finish_primary(corrected, report=report,
                                        finished_at=corrected.endpoint_at + 1,
                                        scope=scope, policy=period, admission=changed_cut)
            self.assertEqual(reopened.journal.read(), before_attempts)

            changed_population = PrimaryAdmissionV1.from_population(
                ("changed-row",), scope=scope, policy=period,
                actual_cut_at=admission.actual_cut_at)
            with self.assertRaisesRegex(IntegrityError, "sample manifest"):
                reopened.finish_primary(corrected, report=report,
                                        finished_at=corrected.endpoint_at + 1,
                                        scope=scope, policy=period, admission=changed_population)
            self.assertEqual(reopened.journal.read(), before_attempts)

            wrong_policy = ResearchPeriodPolicyV1.default()
            wrong_scope = ResearchScopeV1.primary(
                cohort_id=scope.cohort_id, denominator_id=scope.denominator_id,
                policy=wrong_policy)
            wrong_admission = PrimaryAdmissionV1.from_population(
                population, scope=wrong_scope, policy=wrong_policy,
                actual_cut_at=admission.actual_cut_at)
            with self.assertRaisesRegex(IntegrityError, "immutable registration"):
                reopened.finish(corrected, report=report, finished_at=corrected.endpoint_at + 1,
                                scope=wrong_scope, policy=wrong_policy, admission=wrong_admission)
            self.assertEqual(reopened.journal.read(), before_attempts)

            with self.assertRaisesRegex(ContractError, "primary_result_endpoint_not_observed_at_frozen_cut"):
                reopened.finish_primary(corrected, report=report, finished_at=corrected.endpoint_at + 1,
                    scope=scope, policy=period, admission=admission)
            self.assertEqual(reopened.journal.read(), before_attempts)
            # An independently registered retrospective control starts after its
            # complete observed population/cut; it is never future confirmation.
            observed_population = (
                Sample("observed-day1", "2020-01-01", PRIMARY_START_NS_UTC,
                    PRIMARY_START_NS_UTC + 1, PRIMARY_START_NS_UTC, "target-v1"),
                Sample("observed-day2", "2020-01-02", PRIMARY_START_NS_UTC + 86_400_000_000_000,
                    corrected.endpoint_at, corrected.endpoint_at - 1, "target-v1"),
            )
            observed = PrimaryAdmissionV1.from_population(observed_population, scope=scope,
                policy=period, actual_cut_at=corrected.endpoint_at)
            chronological_primary_fold(observed_population, id="period05-observed-population",
                fit_at=PRIMARY_START_NS_UTC, evaluation_start=PRIMARY_START_NS_UTC,
                evaluation_end=corrected.endpoint_at, scope=scope, policy=period, admission=observed)
            retrospective = replace(corrected, id="period05-retrospective-observed",
                selection_chain="period05-retrospective-chain", role="retrospective_evaluation",
                registered_at=observed.actual_cut_at + 1,
                sample_manifest_hash=observed.population_hash,
                earlier_inspection="complete observations already retained; retrospective control")
            reopened.register_primary(retrospective, scope=scope, policy=period, admission=observed)
            reopened.begin_primary(retrospective, model_artifacts={"base": "base-hash", "challenger": "challenger-hash"},
                started_at=observed.actual_cut_at + 2, scope=scope, policy=period, admission=observed)
            report = {"protocol_version": retrospective.version,
                      "sample_manifest_hash": retrospective.sample_manifest_hash}
            before_completion = reopened.journal.read()
            reopened.finish_primary(retrospective, report=report,
                                    finished_at=retrospective.endpoint_at + 3,
                                    scope=scope, policy=period, admission=observed)
            finished_events = reopened.journal.read()
            self.assertEqual(len(finished_events), len(before_completion) + 1)
            result_hash = finished_events[-1]["hash"]
            self.assertEqual(reopened.finish_primary(retrospective, report=report,
                                                     finished_at=retrospective.endpoint_at + 3,
                                                     scope=scope, policy=period,
                                                     admission=observed), result_hash)
            self.assertEqual(reopened.journal.read(), finished_events)
            changed_report = {**report, "changed": True}
            with self.assertRaisesRegex(IntegrityError, "journal idempotency"):
                reopened.finish_primary(retrospective, report=changed_report,
                                        finished_at=retrospective.endpoint_at + 3,
                                        scope=scope, policy=period, admission=observed)
            self.assertEqual(reopened.journal.read(), finished_events)

    def test_PERIOD_06_inrange_missing_source_remains_source_failure(self):
        period = policy()
        scope = primary_scope(period, "period-06")
        literal = golden(6)["literal"]
        cut = literal["observation_end"]
        self.assertEqual(check_cohort_bounds(scope, period, literal["observation_start"],
            cut, depth=literal["depth"], state=literal["state"], frozen_cut_at=cut), "period_admissible")
        with tempfile.TemporaryDirectory() as root:
            registry_ = registry(Path(root), literal["dataset_id"], literal["field"])
            body = {name: value for name, value in literal.items()
                    if name not in ("decision_at", "trading_date", "paired_trade_fact")}
            body["dependent_units"] = tuple(body["dependent_units"])
            body["id"] = "fixture-period-06"
            body["evidence"] = registry_.artifacts.put_json(literal, kind="primary-period-source-failure")
            record = CohortEvidence(**body)
            admission = cohort_admission(record, scope, period, cut=cut)
            registry_.append_primary(record, scope=scope, policy=period, actual_cut_at=cut, admission=admission)
            retained_record = registry_.journal.read()[-1]["payload"]["record"]
            self.assertEqual(retained_record["state"], "missing")
            self.assertEqual(retained_record["next_action"], literal["next_action"])
            self.assertFalse(literal["paired_trade_fact"]["quote_substitution"])
            self.assertEqual(registry_.audit()["cohort_evidence_count"], 1)

            # Authentic retained quote-feature closure. Removing its actual
            # source blob simulates the unavailable partition at read/admission;
            # independent trade facts cannot replace its declared bid_px input.
            from tests.measurement_fit_sources import fitted_sources
            from trading_research.measurements.measurement_fits import admit_measurement_fit
            fitted = fitted_sources(Path(root) / "semantic", family="period06-missing-es-mbp",
                parameters={"dataset_id": literal["dataset_id"], "cohort_id": literal["cohort_id"]},
                recipe_id="period06-quote-recipe", state={"quote_feature": "retained"},
                training_features=({"bid_px": 1.0}, {"bid_px": 2.0}),
                query_features={"bid_px": 3.0}, clock_offset=literal["decision_at"] - 40)
            population = fitted["fold_node"].fold_evidence.population
            actual = PrimaryAdmissionV1.from_population(population, scope=scope, policy=period, actual_cut_at=cut)
            evidence = fitted["store"].read_commit(fitted["commit"].key).closure.by_id[fitted["fold_node"].id].fold_evidence
            self.assertEqual(evidence.population, population)
            source_blob = ArtifactStore(fitted["store"].root / "blobs").path(fitted["source"].payload_ref)
            source_blob.unlink()
            binding = fitted["query_session"].bindings[0]
            with self.assertRaisesRegex(DependencyUnavailable, "required committed bytes absent") as quote_error:
                fitted["store"].resolve(fitted["base"], binding.node_id, binding.source_column, binding.request)
            with self.assertRaisesRegex(DependencyUnavailable, "required committed bytes absent") as fit_error:
                admit_measurement_fit(fitted["store"], fitted["commit"], fitted["transform"].id,
                    fitted["request"], schema_id="MeasurementFixture.v1", unit="descriptive_measurement",
                    recipe_id=fitted["recipe_id"], scope=scope, policy=period, admission=actual)
            for failure in (quote_error.exception, fit_error.exception):
                self.assertNotIn("pre_period", str(failure))
            self.assertEqual(registry_.journal.read()[-1]["payload"]["record"], retained_record)

    def test_PERIOD_07_terms_and_verified_venue_are_independent_blocks(self):
        period = policy()
        scope = primary_scope(period, "period-07")
        literal = golden(7)["literal"]
        cut = literal["decision_at"]
        self.assertEqual(check_cohort_bounds(scope, period, cut, cut + 1,
            depth="complete_window", state="observed", frozen_cut_at=cut + 1), "period_admissible")
        spec = literal["instrument_definition"]
        universe_spec = literal["universe"]
        key = InstrumentKey("fixture", "CME", universe_spec["available_definition_ids"][0],
            "NQH20", spec["underlying"], spec["definition_version"], expiry_at=cut + 10_000_000_000)
        clocks = Clocks(event_at=PRIMARY_START_NS_UTC, known_at=PRIMARY_START_NS_UTC,
            source_version="definition-source-v1", basis=AvailabilityBasis.RECEIVED,
            received_at=PRIMARY_START_NS_UTC, valid_from=PRIMARY_START_NS_UTC,
            valid_until=cut + 20_000_000_000)
        definition = InstrumentDefinition(key, clocks, spec["classification"], spec["multiplier"], Decimal(spec["tick_size"]))
        self.assertEqual(definition.eligibility("raw_flow"), (True, "raw contract counts retain their identity without inferred valuation"))
        for purpose in ("execution", "valuation"):
            self.assertEqual(definition.eligibility(purpose), (False, "required multiplier/tick terms missing"))
        with self.assertRaises(DependencyUnavailable):
            definition.futures_terms()
        venue = literal["cash_and_venue"]
        day = CashDay(date.fromisoformat(venue["cash_context_day"]), "regular", 0, 2**62, 0,
            ("cash-v1",), "timezone-v1", "convention-v1")
        boundary = VenueBoundary(date.fromisoformat(venue["venue_boundary_day"]), "NQ", 0, 2**62, 2**61,
            0, "venue-v1", venue["venue_scope"])
        with self.assertRaises(DependencyUnavailable):
            e0_window(day, boundary=boundary, cut=cut, safety_buffer_ns=1,
                require_verified_venue=venue["require_verified_venue"])

        from trading_research.foundations.rolls import ContractUniverse, SessionSequence, select_prior_volume
        from trading_research.foundations.calendar import Session
        from trading_research.experiments.e0.cohort import DayCompleteness, REQUIRED_CHECKS, freeze_cohort, require_runnable
        universe = ContractUniverse("period07-universe", universe_spec["root"], PRIMARY_START_NS_UTC,
            tuple(universe_spec["contract_ids"]), universe_spec["coverage_scope"], "period07-universe-source")
        self.assertEqual(set(universe.contract_ids) - {definition.key.instrument_id},
            set(universe_spec["missing_definition_ids"]))
        previous = Session(universe_spec["previous_session_id"], date(2020, 1, 1), "NQ",
            PRIMARY_START_NS_UTC, PRIMARY_START_NS_UTC + 1_000_000_000, (), 0,
            PRIMARY_START_NS_UTC, "period07-previous", "tz-v1", True, "synthetic fixture")
        current = Session("NQ-session-2020-01-02", date.fromisoformat(literal["trading_date"]), "NQ",
            cut - 1, cut + 1_000_000_000, (), 0, PRIMARY_START_NS_UTC,
            "period07-current", "tz-v1", True, "synthetic fixture")
        sequence = SessionSequence("period07-sequence", "NQ", (previous, current),
            PRIMARY_START_NS_UTC + 1_000_000_000, "period07-calendar", True)
        with self.assertRaisesRegex(DependencyUnavailable, "lacks an available definition"):
            select_prior_volume(universe=universe, definitions=(definition,), volumes=(),
                previous_session_id=universe_spec["previous_session_id"], cut=cut, session_sequence=sequence)
        # The exact parent requirement is independently blocked even if all
        # unrelated historical completeness checks are explicitly satisfied.
        checks = tuple((name, "missing" if name == "complete_outright_universe" else "satisfied",
            universe.coverage_scope if name == "complete_outright_universe" else "period07-synthetic-evidence")
            for name in sorted(REQUIRED_CHECKS))
        assessment = DayCompleteness(date.fromisoformat(literal["trading_date"]), checks,
            (universe.version,), ("raw_definition", "volume"))
        frozen = freeze_cohort((assessment,), years=(2020,), per_end=1)
        self.assertIn("complete_outright_universe", frozen["exclusions"][0]["reasons"])
        with self.assertRaises(DependencyUnavailable):
            require_runnable(frozen)
        historical = literal["historical_e0_harness"]
        self.assertEqual(historical["scope"], "E0_exact")
        self.assertEqual(freeze_cohort.__kwdefaults__["years"], tuple(historical["default_years"]))
        self.assertTrue(historical["separate_from_primary_scope"])


if __name__ == "__main__":
    unittest.main()
