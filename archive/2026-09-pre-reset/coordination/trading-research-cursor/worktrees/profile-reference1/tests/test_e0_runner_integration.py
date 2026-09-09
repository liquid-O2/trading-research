"""Frozen INT10 cases: actual fitted models, native execution, and ledgers."""

from dataclasses import asdict, replace
from fractions import Fraction
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

from tests.e0_learning_fixtures import build_connected_bracket_router
from tests.e0_source_fixtures import shared_comparator_source
from trading_research.errors import ContractError, DependencyUnavailable, IntegrityError
from trading_research.experiments.e0.runner import (
    BRANCHES, SCENARIOS, E0ReplaySession, E0RunManifest, run_e0_matrix,
    restore_run_checkpoint, run_cache_key, validate_run_inputs, load_e0_result_labels,
    e0_feature_values,
)
from trading_research.operations.artifacts import ArtifactStore, artifact_ref, canonical_json, digest
from trading_research.operations.trials import TrialRegistry


REPO = Path(__file__).resolve().parents[1]


def literal(identity):
    data = json.loads((REPO / "tests/golden/e0_integration_v1.json").read_bytes())
    return next(row for row in data["cases"] if row["case_id"] == identity)


def frozen_manifest(root, source, router):
    """Retain actual code, native inputs, causal context, and model references."""
    store = ArtifactStore(Path(root) / "manifest-artifacts")
    code = tuple((str(path.relative_to(REPO)), path.read_bytes())
                 for path in sorted((REPO / "src/trading_research").rglob("*.py")))
    code_ref = store.put_bytes(canonical_json(code), kind="actual_E0_code_snapshot")
    inputs = {
        "native_sources": tuple(day.native_events for day in source.run_days),
        "admitted_contexts": tuple(day.context for day in source.run_days),
        "operational_terms": tuple(day.operational for day in source.run_days),
        "completed_minutes": tuple(day.minute_history for day in source.run_days),
        "source_coverage": tuple(day.coverage for day in source.run_days),
        "model_references": tuple((policy, tuple((h.name, h.fit.version,
            tuple((b.model_id, b.commit_ref) for b in h.committed.bindings)) for h in heads))
            for policy, heads in router.policies),
    }
    refs = tuple((name, store.put_bytes(canonical_json(value), kind=name).sha256)
                 for name, value in sorted(inputs.items()))
    fold = digest(tuple((policy, tuple((h.name, h.fit.stages.version) for h in heads))
                        for policy, heads in router.policies))
    return E0RunManifest("INT10-actual-retained-common-manifest", literal("E0-INT-10-F01")["inputs"]["scope"],
        tuple(day.day for day in source.run_days), tuple(day.version for day in source.run_days),
        code_ref.sha256, fold, router.version, refs, source.run_days[0].operational.fees.version)


def semantic_report(result):
    return {key: value for key, value in result.items() if key != "processing_latency_ns"}


def literal_projection(result, source):
    """Project actual identities to the frozen, explicitly semantic aliases."""
    aliases = {}
    for day in source.run_days:
        by_id = {obj.id: obj.type for obj in day.context.objects}
        for decision_set in result["decision_sets"]:
            for row in decision_set.rows:
                if row.object_id in by_id:
                    alias = {"06_09:eq": "a", "prior_rth:close": "b", "prior_rth:high": "c"}.get(by_id[row.object_id])
                    if alias is not None:
                        aliases[row.id] = "cand-" + alias + ("-long" if row.side == 1 else "-short")
    quote_aliases = {event.id: {10: "q-before", 11: "q-contact", 12: "q-down", 14: "q-last"}.get(event.provider_sequence)
                     for day in source.run_days for event in day.native_events}
    outcomes = result["outcomes"]
    account = result["account"]
    assert len(outcomes) <= 1, "frozen two-day control permits at most one actual entry"
    fills = [{"role": role, "at": fill.at, "quantity": fill.quantity, "side": fill.side,
              "ticks": fill.price_ticks, "source_quote": quote_aliases[fill.source_event_id]}
             for outcome in outcomes for role, fill in (("entry", outcome.entry), ("exit", outcome.exit))]
    monetary = {
        "gross_usd": sum((day["gross"] for day in account["days"].values()), 0),
        "fees_usd": sum((day["fees"] for day in account["days"].values()), 0),
        "net_day1_usd": account["days"][source.run_days[0].day]["net"],
        "net_day2_usd": account["days"][source.run_days[1].day]["net"],
        "mean_daily_net_usd": account["mean_net_per_eligible_day"],
        "maximum_risk_reserve_usd": result["maximum_risk_reserve_usd"],
        "minimum_marked_net_usd": result["minimum_marked_net_usd"],
        "occupied_seconds": result["occupied_seconds"],
    }
    return {"branch": result["branch"], "scenario": result["scenario"],
        "target_multiple": result["target_multiple"], "fills": fills,
        "decisions": [{"date": row["day"], "cut": row["cut"], "action": row["action"],
            "candidate_id": None if row["candidate_id"] is None else aliases[row["candidate_id"]],
            "desired_position": row["desired_position"], "reason": row["reason"]} for row in result["decisions"]],
        **{name: str(Fraction(value)) for name, value in monetary.items()},
        "exit_reason": outcomes[0].exit_reason if outcomes else None,
        "known_flat_at": outcomes[0].position_known_flat_at if outcomes else None,
        "eligible_day_count": account["eligible_day_count"],
        "zero_trade_day_count": result["zero_trade_day_count"],
        "daily_loss_breaches": result["daily_loss_breaches"], "boundary_met": result["boundary_met"]}


class E0RunnerIntegrationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp = TemporaryDirectory()
        cls.addClassCleanup(cls.temp.cleanup)
        cls.root = Path(cls.temp.name)
        cls.source = shared_comparator_source()
        cls.router, cls.learning_evidence = build_connected_bracket_router(cls.root / "models", cls.source.run_days)
        cls.manifest = frozen_manifest(cls.root, cls.source, cls.router)
        # Exactly one physical matrix is shared by F01 and F02. No private or
        # pre-registration fit/replay occurs outside the registered suite.
        cls.matrix = run_e0_matrix(cls.root / "matrix", manifest=cls.manifest,
                                  days=cls.source.run_days, predict=cls.router)

    def test_e0_int_10_f01_one_actual_manifest_and_full_comparator_population(self):
        case = literal("E0-INT-10-F01")
        expected = case["expected"]
        actual = [row for row in self.matrix["results"] if row["scenario"] == "baseline"]
        self.assertEqual(len(actual), len(expected["baseline_branch_runs"]))
        self.assertEqual([literal_projection(row, self.source) for row in actual], expected["baseline_branch_runs"])
        self.assertEqual(len({row["population_hash"] for row in actual}), 1)
        for result in actual:
            with self.subTest(branch=result["branch"], multiple=result["target_multiple"]):
                self.assertEqual(result["population_count"], expected["total_population_rows_six_cuts"])
                self.assertEqual(len(result["decision_sets"]), 6)
                self.assertEqual(len(result["decisions"]), 6)
                for population in result["decision_sets"]:
                    self.assertEqual(sum(row.side == 0 for row in population.rows), expected["background_rows_per_cut"])
                    self.assertEqual(sum(row.side != 0 for row in population.rows), expected["side_rows_per_cut"])
                    self.assertEqual(len({row.object_id for row in population.rows if row.side}), expected["full_object_count"])
                self.assertTrue(result["account"]["complete"])
                self.assertTrue(result["orders"]["reconciled"])
                self.assertFalse(result["orders"]["incidents"])
                self.assertFalse(result["orders"]["live_orders"])
                self.assertFalse(any(result["orders"]["positions"].values()))
                self.assertEqual(len(result["orders"]["executions"]), 2 * len(result["outcomes"]))
                self.assertFalse(result["economic_market_evidence"])
        self.assertEqual(validate_run_inputs(self.manifest, self.source.run_days, predict=self.router), self.manifest.version)
        for field, changed_value in (("source_hashes", (("unrelated_source", "0" * 64),)),
                                     ("fold_version", "unrelated-fold")):
            with self.subTest(changed_direct_input=field):
                changed = replace(self.manifest, **{field: changed_value})
                destination = self.root / ("rejected-direct-" + field)
                with self.assertRaises(IntegrityError):
                    run_e0_matrix(destination, manifest=changed, days=self.source.run_days, predict=self.router)
                self.assertFalse(destination.exists())
        self.assertEqual(self.manifest.model_version, self.router.version)
        day = self.source.run_days[0]
        contact = next(row for row in actual[0]["decision_sets"][1].rows if row.contact is not None)
        stale = replace(day, minute_history=day.minute_history[:-1])
        with self.assertRaisesRegex(DependencyUnavailable, "last completed minute"):
            e0_feature_values(stale, contact, midpoint=Fraction(72004), cut=day.cuts[1])
        self.assertNotIn("outcomes", asdict(self.manifest))
        self.assertNotIn("profit", asdict(self.manifest))
        self.assertFalse(self.matrix["market_evidence"])
        self.assertFalse(self.matrix["program_complete"])
        for result in actual:
            inventory = load_e0_result_labels(ArtifactStore(self.root / "matrix/trials/artifacts"), result)
            self.assertEqual(result["label_status"], "post_replay_inventory")
            self.assertEqual(inventory["population_hash"], result["population_hash"])
            self.assertEqual(inventory["counts"], {"population": 162, "background": 6,
                "object_side": 156, "contact": 10, "no_contact": 146, "censored": 0,
                "ambiguous": 0, "unavailable": 0, "price_path_unavailable": 0})
            self.assertEqual(tuple(row["candidate_id"] for row in inventory["rows"]),
                tuple(row.id for group in result["decision_sets"] for row in group.rows))
            self.assertFalse(inventory["used_for_action_selection"])
            self.assertTrue(all(row["fixed_end"] == row["cut"] + 900_000_000_000
                                for row in inventory["rows"]))
            for row in inventory["rows"]:
                if row["side"]:
                    self.assertEqual(row["object_label"]["target"]["end"], row["fixed_end"])
                    self.assertEqual(row["price_path_label"]["target"]["horizon_end"], row["fixed_end"])
                    self.assertGreaterEqual(row["object_label"]["label"]["maturity_at"], row["fixed_end"])
            # The first cut stays flat even though its later native source
            # contains contacts. These labels are not entry-time features.
            self.assertEqual(result["decisions"][0]["action"], "flat")

    def test_e0_int_10_f02_exact_finite_paired_latency_and_impact_matrix(self):
        case = literal("E0-INT-10-F02")
        expected = case["expected"]
        self.assertEqual([asdict(scenario) for scenario in SCENARIOS], case["inputs"]["scenarios"])
        self.assertEqual(len(SCENARIOS), expected["total_registered_scenarios"])
        self.assertEqual(len(SCENARIOS) - 1, expected["axis_stress_scenario_count"])
        self.assertEqual(len(self.matrix["results"]), expected["tiny_synthetic_branch_policy_scenario_run_count"])
        self.assertEqual(len(self.matrix["label_inventory_artifacts"]), 16)
        for multiple in (1, 2):
            for scenario in SCENARIOS:
                paired = [row for row in self.matrix["results"]
                          if row["target_multiple"] == multiple and row["scenario"] == scenario.id]
                self.assertEqual(len({row["label_inventory_artifact"]["sha256"] for row in paired}), 1)
        baseline = next(row for row in self.matrix["results"]
                        if row["target_multiple"] == 1 and row["branch"] == "always_flat"
                        and row["scenario"] == "baseline")
        delayed = next(row for row in self.matrix["results"]
                       if row["target_multiple"] == 1 and row["branch"] == "always_flat"
                       and row["scenario"] == "feed-1000")
        label_store = ArtifactStore(self.root / "matrix/trials/artifacts")
        self.assertEqual(baseline["population_hash"], delayed["population_hash"])
        self.assertNotEqual(baseline["source_path_versions"], delayed["source_path_versions"])
        with self.assertRaises(IntegrityError):
            load_e0_result_labels(label_store,
                {**baseline, "label_inventory_artifact": delayed["label_inventory_artifact"]})
        ref = artifact_ref(baseline["label_inventory_artifact"])
        oversized = ArtifactStore(self.root / "oversized-label")
        oversized.path(ref).parent.mkdir(parents=True)
        with oversized.path(ref).open("wb") as stream:
            stream.truncate(4 * 1024 ** 2 + 1)
        with patch("trading_research.experiments.e0.runner.os.fdopen") as opened:
            with self.assertRaises(IntegrityError):
                load_e0_result_labels(oversized, baseline)
            opened.assert_not_called()
        aliased = ArtifactStore(self.root / "aliased-label")
        aliased.path(ref).parent.mkdir(parents=True)
        aliased.path(ref).symlink_to(label_store.path(ref))
        with self.assertRaises(IntegrityError):
            load_e0_result_labels(aliased, baseline)
        parent_alias = self.root / "parent-label-alias"
        parent_alias.symlink_to(label_store.root, target_is_directory=True)
        with self.assertRaises(IntegrityError):
            load_e0_result_labels(ArtifactStore(parent_alias), baseline)
        self.assertEqual([literal_projection(row, self.source) for row in self.matrix["results"]], expected["branch_runs"])
        self.assertEqual(len({row["population_hash"] for row in self.matrix["results"]}), 1)
        self.assertEqual(len(self.matrix["trials"]), 64)
        self.assertEqual(len({row[3] for row in self.matrix["trials"]}), 64)
        state = TrialRegistry(self.root / "matrix/trials").state()
        self.assertEqual(len(state["trials"]), 65)
        self.assertEqual(len(state["attempts"]), 1)
        attempt = state["attempts"][self.matrix["physical_attempt"]]
        self.assertEqual(attempt["status"], "succeeded")
        self.assertGreater(attempt["cpu_seconds"], 0)
        self.assertLess(attempt["cpu_seconds"], 180)
        self.assertGreater(attempt["wall_seconds"], 0)
        self.assertGreater(attempt["peak_rss_bytes"], 0)
        self.assertEqual(len(attempt["result_artifacts"]), 1)
        for result in self.matrix["results"]:
            self.assertEqual(len(result["processing_latency_ns"]), 6)
            self.assertTrue(all(type(value) is int and value > 0 for value in result["processing_latency_ns"]))
            if result["scenario"] == "impact-0" and result["outcomes"]:
                self.assertGreater(result["outcomes"][0].fees_usd, 0)

    def test_e0_int_10_f03_actual_pending_exit_restart_and_retained_abandonment(self):
        from tests.e0_report_fixtures import check_history_import
        from tests.e0_bundle_fixtures import check_e0_bundle, check_e0_supervision
        from tests.e0_serving_fixtures import check_e0_serving_operation
        self.serving_observation = check_e0_serving_operation(self, self.router, self.source.run_days[0].day)
        check_history_import(self, self.root / "bounded-history-import")
        check_e0_bundle(self, self.root / "bundle", self.manifest, self.source.run_days,
                        self.router, ArtifactStore(self.root / "manifest-artifacts"))
        check_e0_supervision(self, self.root / "supervision", matrix_root=self.root / "matrix")
        case = literal("E0-INT-10-F03")
        directory = self.root / "restart"
        session = E0ReplaySession(directory, manifest=self.manifest, days=self.source.run_days,
            branch="frequency", multiple=2, scenario=SCENARIOS[0], predict=self.router)
        session.run(through_cut=self.source.run_days[0].cuts[-1])
        self.assertEqual(session.report()["label_status"], "pending_complete_replay")
        self.assertIsNone(session.report()["label_inventory"])
        self.assertEqual(session.cursor, 3)
        self.assertTrue(any(session.orders.state()["positions"].values()))
        self.assertTrue(session.pending[0].pending)
        self.assertEqual(session.decisions.read()[-1]["payload"]["action"], "hold")
        self.assertGreater(session.authorized[0].reservation.reserve_usd, 0)
        prefix = session.checkpoint()
        retained = directory / "checkpoint.json"
        retained.write_bytes(canonical_json(prefix))
        reopened = json.loads(retained.read_bytes())
        self.assertEqual(restore_run_checkpoint(reopened, self.manifest, branch="frequency", multiple=2,
                                               scenario=SCENARIOS[0]), reopened["state"])
        for field, value in (("pending", []), ("closed_days", [0]), ("cursor", 2),
                             ("processing_latency_ns", [])):
            with self.subTest(changed_inventory=field):
                changed = json.loads(retained.read_bytes())
                changed["state"][field] = value
                with self.assertRaises(IntegrityError):
                    E0ReplaySession.restore(directory, changed, manifest=self.manifest, days=self.source.run_days,
                        branch="frequency", multiple=2, scenario=SCENARIOS[0], predict=self.router)
        # The journal comparison also rejects an internally inconsistent
        # inventory even when the caller retains a new checkpoint hash.
        for field, value in (("pending", ()), ("closed_days", (0,)), ("cursor", 2)):
            changed = {**prefix["state"], field: value}
            with self.subTest(inconsistent_inventory=field), self.assertRaises(IntegrityError):
                session._validate_checkpoint_inventory(changed)
        restored = E0ReplaySession.restore(directory, reopened, manifest=self.manifest, days=self.source.run_days,
            branch="frequency", multiple=2, scenario=SCENARIOS[0], predict=self.router)
        self.assertEqual(canonical_json(restored.checkpoint()), canonical_json(prefix))
        expected = next(row for row in self.matrix["results"] if
                        (row["branch"], row["target_multiple"], row["scenario"]) == ("frequency", 2, "baseline"))
        expected = {**expected, "label_inventory": load_e0_result_labels(
            ArtifactStore(self.root / "matrix/trials/artifacts"), expected)}
        expected.pop("label_inventory_artifact")
        self.assertEqual(canonical_json(semantic_report(restored.run().report())), canonical_json(semantic_report(expected)))
        for field, value in (("code_hash", digest("changed actual code")), ("fold_version", digest("changed fold")),
                             ("source_hashes", (("changed source", digest("different bytes")),))):
            with self.subTest(changed=field), self.assertRaisesRegex(ContractError, "input/code/fold hash changed"):
                restore_run_checkpoint(reopened, replace(self.manifest, **{field: value}),
                                       branch="frequency", multiple=2, scenario=SCENARIOS[0])
        # Exercise the literal generic cache identities separately from the
        # real 2025 account restart (the golden generic clock is in 2024).
        generic = case["inputs"]["checkpoint"]
        fixture_manifest = replace(self.manifest, code_hash=generic["code_hash"], fold_version=generic["fold_hash"],
                                   source_hashes=(("source", generic["input_hash"]),))
        checkpoint = {"cache_key": run_cache_key(fixture_manifest, branch="frequency", multiple=2,
                                                  scenario=SCENARIOS[0]), "state": generic}
        self.assertEqual(restore_run_checkpoint(checkpoint, fixture_manifest, branch="frequency", multiple=2,
                                                scenario=SCENARIOS[0]), generic)
        for variant in case["inputs"]["restart_variants"][1:]:
            changed = replace(fixture_manifest, source_hashes=(("source", variant["input_hash"]),))
            with self.assertRaisesRegex(ContractError, case["variants"][1]["expected"]["reason"]):
                restore_run_checkpoint(checkpoint, changed, branch="frequency", multiple=2, scenario=SCENARIOS[0])
        registry = TrialRegistry(self.root / "explicit-abandonment")
        registry.register_family("INT10-literal-trials", scope_ids=tuple(case["source_clause_ids"]),
            protocol={"case": case["case_id"]}, max_attempts=3, cpu_budget_seconds=600)
        trials = tuple(registry.register(name=name, family="INT10-literal-trials", stage="integration",
            configuration={"literal": name}, code_hash=generic["code_hash"], data_hashes={"input": generic["input_hash"]},
            fold_version=generic["fold_hash"], target_version="fixed-bracket") for name in case["inputs"]["trial_ids"])
        abandoned = registry.start(trials[-1], cpu_reservation_seconds=180)
        reason = "registered_failed_or_abandoned"
        registry.finish(abandoned, status="interrupted", cpu_seconds=None, wall_seconds=None,
                        peak_rss_bytes=None, reason=reason)
        preserved = TrialRegistry(self.root / "explicit-abandonment").state()
        self.assertEqual(len(preserved["trials"]), len(case["inputs"]["trial_ids"]))
        self.assertEqual(preserved["attempts"][abandoned]["reason"], case["variants"][2]["expected"]["report_status"])
        self.assertEqual(preserved["attempts"][abandoned]["cpu_seconds"], 180)
        self.assertFalse(preserved["attempts"][abandoned]["result_artifacts"])
        self.assertNotEqual(preserved["attempts"][abandoned]["status"], "succeeded")


if __name__ == "__main__":
    unittest.main()
