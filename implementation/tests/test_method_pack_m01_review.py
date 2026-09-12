"""Independent adversarial review cases for the public M01 evidence/report seam."""

from __future__ import annotations

from copy import deepcopy
from decimal import Decimal
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from trading_research.research.method_pack import objects as _registered_objects  # noqa: F401
from trading_research.research.method_pack.evidence import (
    SchemaError,
    fixture_document,
    parse_manifest,
    score_episode,
)
from trading_research.research.method_pack.protocol import jsonable, run_recipe
from trading_research.research.method_pack.secondary import reference_outcome


ROOT = Path(__file__).resolve().parents[2]
RUNNER = ROOT / "implementation/tools/run_phase1_objects.py"
BASE = 1_768_500_000_000_000_000


def at(minute: int) -> int:
    return BASE + minute * 60_000_000_000


def reversal_values(**updates):
    values = {
        "branch": "judas_reversal",
        "side": "short",
        "instrument_id": "NQ-test",
        "range_frozen": True,
        "context_fixed": True,
        "location_touched": True,
        "source_confirmation": True,
        "risk_defined": True,
        "objective_fixed": True,
        "range_known_at": at(0),
        "context_at": at(20),
        "touch_at": at(41),
        "sweep_at": at(41),
        "confirm_at": at(43),
        "decision_at": at(44),
        "reversal_context": True,
        "edge_swept": True,
        "source_time_window": True,
        "objective_is_opposing_draw": True,
    }
    values.update(updates)
    return values


def synthetic_document(fid: str = "entry"):
    doc = fixture_document("JJ-TBR", "sequence", fid, reversal_values())
    # These are hand-authored algebra fixtures, not historical source records.
    doc['candidates'][0]['cohort_id'] = 'synthetic-test'
    return doc


def score_document(doc, candidate_id="entry"):
    parsed = parse_manifest(doc, "JJ-TBR")
    return score_episode(parsed[0][candidate_id], *parsed[1:])


def add_management(doc, *, bad_object_identity=False, explicit_parent=False):
    parent = doc["candidates"][0]
    action_at = at(50)
    evidence = {
        "evidence_id": "action-evidence",
        "method_id": "JJ-TBR",
        "branch": "judas_reversal",
        "instrument_id": "NQ-test",
        "band_id": "fixture-band",
        "side": "short",
        "source_ref": "review observed management action",
        "source_version": "review-v1",
        "description": "One supplied partial-fill action under the selected policy.",
        "payload": {"action": "partial", "filled_quantity": 1, "action_policy_ok": True},
        "observation_start": action_at,
        "observation_end": action_at,
        "known_at": action_at,
        "evidence_mode": "supplied_contemporaneous",
    }
    obj = {
        "object_id": "action-object",
        "recipe_id": "O142",
        "method_id": "JJ-TBR",
        "branch_scope": ["judas_outbound"] if bad_object_identity else ["judas_reversal"],
        "author": "JJumbo",
        "instrument_id": "NQ-test",
        "parent_ids": ["entry-ticket"] if explicit_parent else [],
        "source_ref": "review observed management action",
        "source_version": "review-v1",
        "value": {"action_policy_ok": True},
        "units": {"action_policy_ok": "boolean?"},
        "formation_start": action_at,
        "formation_end": action_at,
        "as_of": action_at,
        "known_at": action_at,
        "state": "supplied",
        "hole_ids": [],
        "evidence_ids": ["action-evidence"],
        "band_id": "foreign-band" if bad_object_identity else "fixture-band",
        "side": "long" if bad_object_identity else "short",
    }
    if explicit_parent:
        parent_object = {
            **obj,
            "object_id": "entry-ticket",
            "recipe_id": "O150",
            "parent_ids": [],
            "value": {"decision_at": parent["decision_at"]},
            "units": {"decision_at": "event_key?"},
            "formation_start": parent["decision_at"],
            "formation_end": parent["decision_at"],
            "as_of": parent["decision_at"],
            "known_at": parent["decision_at"],
        }
        doc["objects"].append(parent_object)
        doc["candidates"][0]["object_ids"].append("entry-ticket")
        obj["inputs"] = {
            "entry_id": parent["candidate_id"],
            "entry_at": parent["decision_at"],
        }
    action = {
        "candidate_id": "action",
        "method_id": "JJ-TBR",
        "branch": "judas_reversal",
        "side": "short",
        "instrument_id": "NQ-test",
        "session_date_et": parent["session_date_et"],
        "decision_at": action_at,
        "band_ids": ["fixture-band"],
        "object_ids": ["action-object"],
        "assertion_ids": [],
        "cohort_id": "review-management",
        "evidence_mode": "supplied_contemporaneous",
        "operands": {},
        "predicate": "management",
        "action_object_id": "action-object",
        "parent_attempt_id": parent["candidate_id"],
    }
    doc["candidates"].append(action)
    doc["objects"].append(obj)
    doc["evidence"].append(evidence)
    return doc


class ScoreEpisodeReviewTests(unittest.TestCase):
    def test_identity_collections_are_typed(self):
        doc = synthetic_document()
        doc["candidates"][0]["band_ids"] = "fixture-band"
        with self.assertRaises(SchemaError):
            parse_manifest(doc, "JJ-TBR")

    def test_false_required_observation_is_not_relabelled_as_a_hole(self):
        doc = synthetic_document()
        confirmation = next(a for a in doc["assertions"] if a["field"] == "source_confirmation")
        confirmation["value"] = False
        for eid in confirmation["evidence_ids"]:
            doc["evidence"][[e["evidence_id"] for e in doc["evidence"]].index(eid)]["payload"]["source_confirmation"] = False
        del doc["candidates"][0]["operands"]["objective_is_opposing_draw"]
        scored = score_document(doc)
        self.assertEqual(scored["verdict"], "fail")
        self.assertIs(scored["sequence_ok"], False)
        self.assertIsNone(scored["coverage_ok"])

    def test_nonselected_branch_operand_is_not_required(self):
        doc = fixture_document(
            "JJ-TBR",
            "sequence",
            "entry",
            reversal_values(directional_context=False),
        )
        scored = score_document(doc)
        self.assertEqual(scored["verdict"], "pass")
        self.assertEqual(scored["operands"]["directional_context"]["applicability"], "not_required")

    def test_raw_derived_cohort_cannot_be_built_from_supplied_assertions(self):
        doc = synthetic_document()
        doc["candidates"][0]["evidence_mode"] = "raw_derived"
        try:
            scored = score_document(doc)
        except SchemaError:
            return
        self.assertNotEqual(scored["verdict"], "pass")

    def test_supplied_branch_object_needs_evidence_for_its_value(self):
        doc = synthetic_document()
        branch = next(o for o in doc["objects"] if "branch" in o["value"])
        for eid in branch["evidence_ids"]:
            record = next(e for e in doc["evidence"] if e["evidence_id"] == eid)
            record["payload"] = {"unrelated": "observation"}
        try:
            scored = score_document(doc)
        except SchemaError:
            return
        self.assertNotEqual(scored["verdict"], "pass")

    def test_supplied_qualitative_assertion_is_not_a_wrapped_boolean(self):
        doc = synthetic_document()
        doc['candidates'][0]['evidence_mode']='supplied_contemporaneous'
        assertion = next(a for a in doc["assertions"] if a["field"] == "source_confirmation")
        for eid in assertion["evidence_ids"]:
            record = next(e for e in doc["evidence"] if e["evidence_id"] == eid)
            record["payload"] = {"source_confirmation": True}
        try:
            scored = score_document(doc)
        except SchemaError:
            return
        self.assertNotEqual(scored["verdict"], "pass")

    def test_width_comparison_cannot_become_qualitative_context(self):
        doc = synthetic_document()
        assertion = next(a for a in doc["assertions"] if a["field"] == "context_fixed")
        object_id = "entry:o:context_fixed"
        producer = next(o for o in doc["objects"] if o["object_id"] == object_id)
        evidence = next(e for e in doc["evidence"] if e["evidence_id"] in assertion["evidence_ids"])
        assertion.update(
            evidence_mode="raw_derived",
            object_id=object_id,
            comparison={"left_field": "width_points", "operator": ">", "right_value": Decimal("0")},
        )
        producer.update(
            state="computed",
            inputs={"W": "20", "known_at": at(20), "use_at": at(41)},
            raw_member_locators=[{"fixture": "width"}],
            band_id="foreign-band",
            side="long",
        )
        evidence["evidence_mode"] = "raw_derived"
        try:
            scored = score_document(doc)
        except SchemaError:
            return
        self.assertNotEqual(scored["verdict"], "pass")
        self.assertIn(object_id, scored["used_object_ids"])

    def test_management_requires_an_explicit_entry_link(self):
        doc = add_management(synthetic_document(), explicit_parent=False)
        try:
            scored = score_document(doc, "action")
        except SchemaError:
            return
        self.assertNotEqual(scored["verdict"], "pass")

    def test_management_checks_action_object_identity(self):
        doc = add_management(synthetic_document(), bad_object_identity=True, explicit_parent=False)
        try:
            scored = score_document(doc, "action")
        except SchemaError:
            return
        self.assertNotEqual(scored["verdict"], "pass")

    def test_management_policy_is_not_an_unsubstantiated_object_boolean(self):
        doc = add_management(synthetic_document(), explicit_parent=True)
        action_evidence = next(e for e in doc["evidence"] if e["evidence_id"] == "action-evidence")
        action_evidence["payload"] = {"unrelated": "observation"}
        try:
            scored = score_document(doc, "action")
        except SchemaError:
            return
        self.assertNotEqual(scored["verdict"], "pass")


class ReferenceOutcomeReviewTests(unittest.TestCase):
    def candidate(self, **spec_updates):
        spec = {
            "source_ref": "review outcome",
            "source_version": "review-v1",
            "selected_at": BASE,
            "objective_id": "target-1",
            "invalidation_id": "stop-1",
            "target": "104",
            "invalidation": "98",
            "window_end": BASE + 100,
            "coverage_complete": True,
            "coverage_object_id": "coverage-1",
            "instrument_id": "NQ-test",
        }
        spec.update(spec_updates)
        return {
            "candidate_id": "entry",
            "method_id": "JJ-TBR",
            "branch": "judas_reversal",
            "side": "long",
            "instrument_id": "NQ-test",
            "evidence_mode": "supplied_contemporaneous",
            "cohort_id": "synthetic-test",
            "decision_at": BASE,
            "band_ids": ["fixture-band"],
            "object_ids": ["target-1", "stop-1", "coverage-1"],
            "outcome_spec": spec,
        }

    def records(self):
        common = {
            "method_id": "JJ-TBR",
            "branch_scope": ["judas_reversal"],
            "instrument_id": "NQ-test",
            "side": "long",
            "band_id": "fixture-band",
            "known_at": BASE,
            "state": "supplied",
        }
        objects = {
            "target-1": {
                **common,
                "object_id": "target-1",
                "recipe_id": "O141",
                "value": {"target": "104"},
                "evidence_ids": ["target-evidence"],
            },
            "stop-1": {
                **common,
                "object_id": "stop-1",
                "recipe_id": "O139",
                "value": {"stop": "98"},
                "evidence_ids": ["stop-evidence"],
            },
            "coverage-1": {
                **common,
                "object_id": "coverage-1",
                "recipe_id": "O001",
                "value": {"start": BASE, "end": BASE + 100, "gaps": []},
                "evidence_ids": ["coverage-evidence"],
                "raw_member_locators": [{"fixture": "covered-window"}],
            },
        }
        evidence = {
            "target-evidence": {"known_at": BASE, "payload": {"target": "104"}},
            "stop-evidence": {"known_at": BASE, "payload": {"stop": "98"}},
            "coverage-evidence": {
                "known_at": BASE,
                "payload": {"coverage": {"start": BASE, "end": BASE + 100, "gaps": []}},
            },
        }
        return objects, evidence

    def score(self, candidate):
        objects, evidence = self.records()
        return reference_outcome(candidate, objects, evidence)

    def test_single_sided_complete_bar_establishes_first_event(self):
        result = self.score(self.candidate(bars=[{
            "bar_id": "bar-1",
            "instrument_id": "NQ-test",
            "start": BASE + 1,
            "end": BASE + 2,
            "H": "104",
            "L": "100",
            "complete": True,
            "coverage_state": "covered",
        }]))
        self.assertEqual(result["outcome"], "target_first")

    def test_foreign_event_cannot_establish_target_first(self):
        result = self.score(self.candidate(events=[{
            "event_id": "foreign",
            "instrument_id": "ES-test",
            "t": BASE + 1,
            "price": "104",
            "ordering_basis": "event_ns",
        }]))
        self.assertEqual(result["outcome"], "unknown")
        self.assertIn("hole", result)

    def test_reversed_outcome_window_is_unknown(self):
        result = self.score(self.candidate(window_end=BASE - 1))
        self.assertEqual(result["outcome"], "unknown")

    def test_unlinked_reference_definition_is_unknown(self):
        result = reference_outcome(self.candidate())
        self.assertEqual(result["outcome"], "unknown")
        self.assertIn("objective_id", result["hole"])

    def test_coverage_boolean_without_coverage_evidence_cannot_prove_absence(self):
        candidate = self.candidate(events=[], bars=[])
        candidate["outcome_spec"].pop("coverage_object_id")
        result = self.score(candidate)
        self.assertEqual(result["outcome"], "unknown")
        self.assertIn("coverage", result["hole"])


class PublicMethodPassReviewTests(unittest.TestCase):
    def test_report_preserves_outcome_year_missingness_and_artifact_identity(self):
        doc = synthetic_document()
        candidate = doc["candidates"][0]
        reference_at = at(40)
        reference_common = {
            "method_id": "JJ-TBR",
            "branch_scope": ["judas_reversal"],
            "author": "JJumbo",
            "instrument_id": "NQ-test",
            "parent_ids": [],
            "source_ref": "review target and invalidation",
            "source_version": "review-v1",
            "formation_start": reference_at,
            "formation_end": reference_at,
            "as_of": reference_at,
            "known_at": reference_at,
            "state": "supplied",
            "hole_ids": [],
            "band_id": "fixture-band",
            "side": "short",
        }
        target_evidence = {
            "evidence_id": "target-evidence",
            "method_id": "JJ-TBR",
            "branch": "judas_reversal",
            "instrument_id": "NQ-test",
            "band_id": "fixture-band",
            "side": "short",
            "source_ref": "review target",
            "source_version": "review-v1",
            "description": "Preselected opposing range objective.",
            "payload": {"target": "100"},
            "observation_start": reference_at,
            "observation_end": reference_at,
            "known_at": reference_at,
            "evidence_mode": "supplied_contemporaneous",
        }
        stop_evidence = {
            **target_evidence,
            "evidence_id": "stop-evidence",
            "source_ref": "review invalidation",
            "description": "Preselected structural invalidation.",
            "payload": {"stop": "122"},
        }
        coverage_value = {"start": at(44), "end": at(60), "gaps": []}
        coverage_evidence = {
            **target_evidence,
            "evidence_id": "coverage-evidence",
            "source_ref": "review coverage",
            "description": "Complete covered outcome interval.",
            "payload": {"coverage": coverage_value},
        }
        doc["evidence"].extend([target_evidence, stop_evidence, coverage_evidence])
        doc["objects"].extend([
            {
                **reference_common,
                "object_id": "target-1",
                "recipe_id": "O141",
                "value": {"target": "100"},
                "units": {"target": "decimal?"},
                "evidence_ids": ["target-evidence"],
            },
            {
                **reference_common,
                "object_id": "stop-1",
                "recipe_id": "O139",
                "value": {"stop": "122"},
                "units": {"stop": "decimal?"},
                "evidence_ids": ["stop-evidence"],
            },
            {
                **reference_common,
                "object_id": "coverage-1",
                "recipe_id": "O001",
                "value": coverage_value,
                "units": {"start": "event_key?", "end": "event_key?", "gaps": "array"},
                "evidence_ids": ["coverage-evidence"],
                "raw_member_locators": [{"fixture": "covered-window"}],
            },
        ])
        candidate["object_ids"].extend(["target-1", "stop-1", "coverage-1"])
        doc["candidates"][0]["outcome_spec"] = {
            "source_ref": "review target and invalidation",
            "source_version": "review-v1",
            "selected_at": reference_at,
            "objective_id": "target-1",
            "invalidation_id": "stop-1",
            "target": "100",
            "invalidation": "122",
            "window_end": at(60),
            "coverage_complete": True,
            "coverage_object_id": "coverage-1",
            "instrument_id": "NQ-test",
            "bars": [{
                "bar_id": "bar-1",
                "instrument_id": "NQ-test",
                "start": at(45),
                "end": at(46),
                "H": "120",
                "L": "100",
                "complete": True,
                "coverage_state": "covered",
            }],
        }
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            data_root = root / "data"
            report_root = root / "reports"
            data_root.mkdir()
            episodes = root / "episodes.json"
            episodes.write_text(json.dumps(jsonable(doc)))
            run = subprocess.run(
                [
                    sys.executable,
                    str(RUNNER),
                    "method-pass",
                    "--method",
                    "JJ-TBR",
                    "--scope",
                    "acquired",
                    "--data-root",
                    str(data_root),
                    "--report-root",
                    str(report_root),
                    "--episodes",
                    str(episodes),
                ],
                cwd=ROOT,
                text=True,
                capture_output=True,
            )
            self.assertEqual(run.returncode, 0, run.stderr)
            report = json.loads((report_root / "jj-tbr.json").read_text())
            supplied = next(s for s in report["summaries"] if s["cohort"] == "synthetic-test")
            self.assertEqual([supplied[k] for k in ("p", "f", "u", "n", "N")], [1, 0, 0, 1, 1])
            self.assertEqual(supplied["rate_exact"], [1, 1])
            self.assertEqual(supplied["interval_exact"], [[1, 1], [1, 1]])
            self.assertEqual(sum(y["N"] for y in supplied["years"].values()), 1)
            branch_cohort = next(
                c for c in report["branches"]["judas_reversal"]["cohorts"]
                if c["cohort"] == "synthetic-test"
            )
            self.assertEqual(branch_cohort["N"], 1)
            self.assertEqual(report["reference_outcomes"]["counts"]["target_first"], 1)
            for name, meta in report["artifacts"].items():
                payload = Path(meta["path"]).read_bytes()
                self.assertEqual(hashlib.sha256(payload).hexdigest(), meta["sha256"], name)


class PartialRecipeReviewTests(unittest.TestCase):
    def test_source_hole_retains_independently_known_literals(self):
        result = run_recipe("O141", {
            "entry": "100",
            "target": "104",
            "selected_at": 1,
            "decision_at": None,
            "known_at": 1,
            "use_at": 2,
        })
        self.assertEqual(result.state, "hole")
        self.assertEqual(result.value.get("entry"), Decimal("100"))
        self.assertEqual(result.value.get("target"), Decimal("104"))
        self.assertIsNone(result.value.get("distance"))


if __name__ == "__main__":
    unittest.main()
