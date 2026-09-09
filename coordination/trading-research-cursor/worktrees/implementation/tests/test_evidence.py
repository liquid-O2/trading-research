from copy import deepcopy
from dataclasses import asdict
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from trading_research.errors import ContractError, IntegrityError
from trading_research.operations.artifacts import ArtifactStore, canonical_json, digest, publish_new
from trading_research.operations.ledger import Ledger
from trading_research.operations.scope import Scope

PLAN = Path(__file__).resolve().parents[2] / "planning/trading-model"


class ArtifactTests(unittest.TestCase):
    def test_partial_write_never_publishes_an_artifact(self):
        with tempfile.TemporaryDirectory() as folder:
            store = ArtifactStore(Path(folder))
            with patch("trading_research.operations.artifacts.os.link", side_effect=OSError("disk full")):
                with self.assertRaises(OSError):
                    store.put_bytes(b"complete-payload", kind="reference")
            self.assertEqual([p for p in Path(folder).rglob("*") if p.is_file()], [])

    def test_duplicate_bytes_are_idempotent_and_mutation_is_detected(self):
        with tempfile.TemporaryDirectory() as folder:
            store = ArtifactStore(Path(folder))
            ref = store.put_json({"ticks": 4}, kind="reference")
            self.assertEqual(ref, store.put_json({"ticks": 4}, kind="reference"))
            store.path(ref).write_bytes(b"changed")
            with self.assertRaises(IntegrityError):
                store.read(ref)

    def test_immutable_publication_rejects_conflicting_writer(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "artifact"
            publish_new(path, b"old")
            with self.assertRaises(IntegrityError):
                publish_new(path, b"new")
            self.assertEqual(path.read_bytes(), b"old")


class ScopeLedgerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.scope = Scope.load(PLAN)

    def scope_with(self, manifest):
        manifest["scope_version"] = digest({k: v for k, v in manifest.items() if k != "scope_version"})
        return Scope(manifest, self.scope.experiments, self.scope.components, self.scope.contract_texts)

    def test_exact_ids_and_all_eight_phases_are_imported_unstarted(self):
        with tempfile.TemporaryDirectory() as folder:
            ledger = Ledger(Path(folder))
            result = ledger.import_scope(self.scope)
            self.assertEqual(result["imported"], 4173)
            records = ledger.current()
            self.assertEqual(set(records), set(self.scope.entries))
            self.assertTrue(all(r["engineering_state"] == "unstarted" for r in records.values()))
            self.assertTrue(all(r["evaluation_state"] == "unrun" for r in records.values()))
            self.assertFalse(ledger.audit(self.scope)["engineering_complete"])

    def test_duplicate_unit_and_missing_child_fail_even_with_recomputed_hash(self):
        manifest = deepcopy(self.scope.manifest)
        manifest["units"].append(deepcopy(manifest["units"][0]))
        with self.assertRaisesRegex(IntegrityError, "duplicate"):
            self.scope_with(manifest)
        manifest = deepcopy(self.scope.manifest)
        manifest["units"] = [u for u in manifest["units"] if u["id"] != "F01.DECODER"]
        with self.assertRaisesRegex(IntegrityError, "registries differ"):
            self.scope_with(manifest)

    def test_phase_omission_is_detected_before_implementation(self):
        manifest = deepcopy(self.scope.manifest)
        manifest["units"][0]["phase_ids"].pop()
        with self.assertRaisesRegex(IntegrityError, "phase"):
            self.scope_with(manifest)

    def test_same_count_with_wrong_exact_source_id_fails(self):
        manifest = deepcopy(self.scope.manifest)
        manifest["source_findings"][0]["id"] = "MADE-UP-SOURCE"
        with self.assertRaisesRegex(IntegrityError, "source route"):
            self.scope_with(manifest)

    def test_regeneration_preserves_empirical_history(self):
        with tempfile.TemporaryDirectory() as folder:
            ledger = Ledger(Path(folder))
            ledger.import_scope(self.scope)
            ledger.update({"B00.1": {"engineering_state": "in_progress",
                                    "reason": "Typed references under construction."}}, reason="Start B00.1.")
            before = [p.read_bytes() for p in sorted(ledger.events.glob("*.json"))]
            ledger.import_scope(self.scope)
            self.assertEqual(before, [p.read_bytes() for p in sorted(ledger.events.glob("*.json"))])
            self.assertEqual(ledger.current()["B00.1"]["engineering_state"], "in_progress")

    def test_atomic_evidence_append_and_attachment_retry_preserve_other_writer(self):
        with tempfile.TemporaryDirectory() as folder:
            ledger = Ledger(Path(folder))
            ledger.import_scope(self.scope)
            # Prepare one writer before a second writer commits another assertion.
            first = {"B00.1": {"assertion_ids": ["first-writer"]}}
            ledger.update({"B00.1": {"assertion_ids": ["second-writer"]}}, reason="Other writer.")
            transaction = ledger.update(first, reason="Shared attachment.",
                                        append_fields=("assertion_ids",), attachment_key="shared-run-1")
            self.assertEqual(set(ledger.current()["B00.1"]["assertion_ids"]),
                             {"first-writer", "second-writer"})
            before = ledger.history()
            self.assertEqual(ledger.update(first, reason="Shared attachment.",
                             append_fields=("assertion_ids",), attachment_key="shared-run-1"), transaction)
            self.assertEqual(ledger.history(), before)
            with self.assertRaisesRegex(ContractError, "different evidence"):
                ledger.update({"B00.1": {"assertion_ids": ["changed"]}}, reason="Shared attachment.",
                              append_fields=("assertion_ids",), attachment_key="shared-run-1")
            self.assertEqual(ledger.history(), before)

    def test_verified_and_evaluated_claims_require_separate_evidence(self):
        with tempfile.TemporaryDirectory() as folder:
            ledger = Ledger(Path(folder))
            ledger.import_scope(self.scope)
            for change in ({"engineering_state": "verified"}, {"evaluation_state": "evaluated"},
                           {"disposition": "dependency_blocked"}, {"disposition": "not_applicable"}):
                with self.subTest(change=change), self.assertRaises(ContractError):
                    ledger.update({"B00.1": change}, reason="Attempt unsupported promotion.")
            self.assertEqual(len(ledger.history()), 1)

    def test_wrong_assertion_cannot_verify_unrelated_scope(self):
        with tempfile.TemporaryDirectory() as folder:
            ledger = Ledger(Path(folder))
            ledger.import_scope(self.scope)
            code = asdict(ledger.artifacts.put_bytes(b"reference implementation", kind="code"))
            review = asdict(ledger.artifacts.put_json({"review": "B00.1"}, kind="review"))
            report = asdict(ledger.artifacts.put_json({"success": True, "covers": ["B00.2"],
                            "passed_assertion_ids": ["assert-exact-usd"]}, kind="verification"))
            change = {"definition_reviewed": True, "review_artifacts": [review],
                      "reference_and_code_artifacts": [code], "verification_artifacts": [report],
                      "assertion_ids": ["assert-exact-usd"], "engineering_state": "verified"}
            with self.assertRaisesRegex(ContractError, "does not cover"):
                ledger.update({"B00.1": change}, reason="Attempt unrelated evidence.")

    def test_deleted_middle_transaction_breaks_the_hash_chain(self):
        with tempfile.TemporaryDirectory() as folder:
            ledger = Ledger(Path(folder))
            ledger.import_scope(self.scope)
            for n in range(2):
                ledger.update({"B00.1": {"reason": f"Implementation step {n}."}}, reason="Progress fixture.")
            sorted(ledger.events.glob("*.json"))[1].unlink()
            with self.assertRaises(IntegrityError):
                ledger.current()

    def test_verified_invariant_is_not_empirical_model_selection(self):
        with tempfile.TemporaryDirectory() as folder:
            ledger = Ledger(Path(folder))
            ledger.import_scope(self.scope)
            code = asdict(ledger.artifacts.put_bytes(b"synthetic exact-unit fixture", kind="code"))
            review = asdict(ledger.artifacts.put_json({"review": "synthetic B00.1 fixture"}, kind="review"))
            report = asdict(ledger.artifacts.put_json({"success": True, "covers": ["B00.1"],
                            "passed_assertion_ids": ["synthetic-exact-unit-assertion"]}, kind="verification"))
            ledger.update({"B00.1": {"definition_reviewed": True, "review_artifacts": [review],
                          "reference_and_code_artifacts": [code], "verification_artifacts": [report],
                          "assertion_ids": ["synthetic-exact-unit-assertion"], "engineering_state": "verified"}},
                          reason="Synthetic fixture tests status mechanics only.")
            with self.assertRaises(ContractError):
                ledger.update({"B00.1": {"disposition": "selected"}}, reason="Cannot infer a research result from coding.")
            with self.assertRaises(ContractError):
                ledger.update({"B00.1": {"disposition": "selected", "acceptance_basis": "empirical"}},
                              reason="No empirical evaluation exists.")
            ledger.update({"B00.1": {"disposition": "selected", "acceptance_basis": "operational_fidelity"}},
                          reason="Synthetic invariant acceptance is distinct from evaluated alpha.")
            state = ledger.current()["B00.1"]
            self.assertEqual(state["evaluation_state"], "unrun")
            audit = ledger.audit(self.scope)
            self.assertEqual(audit["engineering"]["verified"], 1)
            self.assertEqual(audit["evaluation"], {"unrun": 4173})

    def test_changed_definition_requires_explicit_migration_and_keeps_prior_record(self):
        with tempfile.TemporaryDirectory() as folder:
            ledger = Ledger(Path(folder))
            ledger.import_scope(self.scope)
            ledger.update({"B00.1": {"engineering_state": "in_progress"}}, reason="Work began.")
            manifest = deepcopy(self.scope.manifest)
            manifest["backlog_tasks"][0]["deliverable"] += " Explicit extra constraint."
            revised = self.scope_with(manifest)
            with self.assertRaisesRegex(IntegrityError, "stale ledger"):
                ledger.import_scope(revised)
            result = ledger.migrate_scope(revised, reason="B00.1 gains a constraint; its prior evidence requires revalidation.")
            self.assertEqual(result["changed"], ["B00.1"])
            current = ledger.current()["B00.1"]
            self.assertEqual(current["engineering_state"], "unstarted")
            self.assertIn("prior_record_hash", current)
            self.assertEqual(ledger.history()[1]["records"][0]["engineering_state"], "in_progress")
            ledger.audit(revised)


if __name__ == "__main__":
    unittest.main()
