"""Manifest, object and acquired-scope checks for JETBUNDLE-STATES."""

from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from decimal import Decimal

from trading_research.research.method_pack.catalog import objects_for
from trading_research.research.method_pack.evidence import fixture_document, parse_manifest, score_episode
from trading_research.research.method_pack.method_slices.m10 import (
    STAGE_LIMITS,
    _transition_document,
    _state,
    method_fixtures,
)
from trading_research.research.method_pack.objects import run_object_fixtures
from trading_research.research.method_pack.objects.m10_recipes import (
    _t,
    o163,
    o165,
    o166,
)


ROOT = Path(__file__).resolve().parents[2]
RUNNER = ROOT / "implementation/tools/run_phase1_objects.py"
METHOD = "JETBUNDLE-STATES"


class MethodPackM10Tests(unittest.TestCase):
    def test_all_five_states_and_transition_rows(self):
        rows = {row["id"]: row for row in method_fixtures()}
        expected = {
            "M10-F1-B": "pass",
            "M10-F1": "pass",
            "M10-F1-D": "pass",
            "M10-F1-E": "pass",
            "M10-F1-W": "pass",
            "M10-F1-transition": "pass",
            "M10-F1-transition-AE": "pass",
            "M10-F2-W-no-cancels": "unknown",
            "M10-F2-conditioning": "fail",
            "M10-F2-tied-order": "unknown",
            "M10-F2-nq-counts": "fail",
            "M10-F3-depth": "unknown",
            "M10-F1:c08-late": "fail",
            "M10-F1:c08-identity": "fail",
            "M10-F1:c08-missing": "unknown",
        }
        self.assertEqual(set(expected), set(rows))
        self.assertTrue(all(row["status"] == "pass" for row in rows.values()))
        self.assertEqual(
            {fid: rows[fid]["actual_value"]["verdict"] for fid in expected},
            expected,
        )
        self.assertEqual(rows["M10-F1"]["actual_value"]["operands"]["state"]["value"], "A")
        self.assertEqual(rows["M10-F1-transition"]["predicate"], "transition_observation")
        self.assertIn("HOLE:C02:unknown_order:state_at:next_state_at",
                      rows["M10-F2-tied-order"]["actual_value"]["hole_ids"])

    def test_stage_limits_keep_current_state_causal(self):
        expected = {
            "participation_record_complete": "participation_known_at",
            "response_record_complete": "response_known_at",
            "state": "state_at",
            "two_sided_executions": "state_at",
            "recent_revisits": "state_at",
            "low_aggression_both_sides": "state_at",
            "high_aggression": "state_at",
            "low_response_efficiency": "state_at",
            "opposite_liquidity_holds_and_refills": "state_at",
            "aggression": "state_at",
            "efficient_displacement": "state_at",
            "prior_absorption_or_effort": "state_at",
            "replenishment_stops": "state_at",
            "level_gives_way": "state_at",
            "cancellations_dominate": "state_at",
            "conditioning_known_at": "state_at",
        }
        self.assertEqual(STAGE_LIMITS, expected)
        self.assertNotIn("next_state_at", STAGE_LIMITS)

    def test_native_object_recipes_preserve_holes_and_timing(self):
        events = [
            {"event_id": "a1", "order_id": "o1", "exchange_seq": 1,
             "instrument_id": "AAPL-fixture", "event_ns": _t(9, 59, 50),
             "known_at": _t(9, 59, 50), "action": "add", "side": "buy",
             "price": "100", "size": 10, "depth_level": 1},
            {"event_id": "c1", "order_id": "o1", "exchange_seq": 2,
             "instrument_id": "AAPL-fixture", "event_ns": _t(9, 59, 55),
             "known_at": _t(9, 59, 55), "action": "cancel", "side": "buy",
             "price": "100", "size": 3, "depth_level": 1},
            {"event_id": "e1", "order_id": "o1", "exchange_seq": 3,
             "instrument_id": "AAPL-fixture", "event_ns": _t(10),
             "known_at": _t(10), "action": "execute", "side": "buy",
             "price": "100", "size": 4, "depth_level": 1},
        ]
        good = o163({"events": events, "instrument_id": "AAPL-fixture",
                     "source_symbol": "AAPL", "depth_coverage": 10,
                     "required_depth_levels": 10,
                     "depth_complete": True, "known_at": _t(10),
                     "use_at": _t(10, 1)})
        self.assertEqual(good.state, "computed")
        self.assertEqual(good.value["remaining"], Decimal("3"))
        bad = o163({"events": [{**events[0], "depth_level": None}],
                    "instrument_id": "AAPL-fixture", "source_symbol": "AAPL",
                    "depth_coverage": 10, "depth_complete": True,
                    "required_depth_levels": 10,
                    "known_at": _t(10), "use_at": _t(10, 1)})
        self.assertEqual(bad.state, "hole")
        self.assertIn("HOLE:O163:depth_level", bad.hole_ids)

        state = o165({"state_label": "A", "state_at": _t(10),
                      "known_at": _t(10), "source_symbol": "AAPL",
                      "depth_levels": 10, "source_observation_id": "state-A",
                      "required_depth_levels": 10,
                      "high_aggression": True, "low_response_efficiency": True,
                      "opposite_liquidity_holds_and_refills": True})
        self.assertEqual(state.state, "supplied")
        self.assertIsNone(state.value["automatic_state"])
        missing_w = o165({"state_label": "W", "state_at": _t(10),
                          "known_at": _t(10), "source_symbol": "AAPL",
                          "depth_levels": 10, "source_observation_id": "state-W",
                          "required_depth_levels": 10,
                          "display_imbalance": True,
                          "cancellations_dominate": None})
        self.assertEqual(missing_w.state, "hole")
        self.assertIn("HOLE:O165:cancellations_dominate", missing_w.hole_ids)

        row = o166({"counts": {"D": 84, "A": 12, "B": 4, "E": 0, "W": 0},
                    "from_state": "D", "to_state": "D", "state_at": _t(10),
                    "next_state_at": _t(10, 1),
                    "conditioning_known_at": _t(9, 59),
                    "cohort_id": "AAPL-20000", "source_symbol": "AAPL",
                    "source_counts_symbol": "AAPL",
                    "row_count": 100, "known_at": _t(10, 1), "use_at": _t(10, 2)})
        self.assertEqual(row.value["p_dd"], Decimal("0.84"))
        self.assertEqual(row.value["p_da"], Decimal("0.12"))
        tied = o166({"counts": {"D": 84, "A": 12, "B": 4, "E": 0, "W": 0},
                     "from_state": "D", "to_state": "D", "state_at": _t(10),
                     "next_state_at": _t(10),
                     "conditioning_known_at": _t(9, 59), "cohort_id": "AAPL-20000",
                     "source_symbol": "AAPL", "row_count": 100})
        self.assertEqual(tied.state, "hole")
        self.assertIn("HOLE:O166:ordering", tied.hole_ids)
        nq = o166({"counts": {"D": 84, "A": 12, "B": 4, "E": 0, "W": 0},
                   "from_state": "D", "to_state": "D", "state_at": _t(10),
                   "next_state_at": _t(10, 1),
                   "conditioning_known_at": _t(9, 59), "cohort_id": "NQ-row",
                   "source_symbol": "NQ", "row_count": 100})
        self.assertEqual(nq.state, "hole")
        self.assertIn("HOLE:O166:counts_source_instrument", nq.hole_ids)

    def test_nq_native_observation_uses_declared_depth_not_aapl_example(self):
        op = _state("A")
        op.update({"instrument_id": "NQH6", "source_symbol": "NQ",
                   "band_id": "NQ-local-level", "source_event_log_id": "NQ-native-log",
                   "local_interval_id": "NQ-local-interval", "depth_levels": 1,
                   "required_depth_levels": 1})
        document = fixture_document(METHOD, "state_observation", "NQ-observation", op)
        parsed = parse_manifest(document, METHOD)
        self.assertEqual(score_episode(parsed[0]["NQ-observation"], *parsed[1:])["verdict"], "pass")

        # A complete one-level record cannot support a requested second level.
        op["required_depth_levels"] = 2
        parsed = parse_manifest(fixture_document(METHOD, "state_observation", "NQ-depth-gap", op), METHOD)
        result = score_episode(parsed[0]["NQ-depth-gap"], *parsed[1:])
        self.assertEqual(result["verdict"], "unknown")
        self.assertTrue(any("depth_levels" in h["reason"] for h in result["holes"]))

        events = [
            {"event_id": "nq-add", "order_id": "nq-order", "exchange_seq": 1,
             "instrument_id": "NQH6", "event_ns": _t(9, 59), "action": "add",
             "side": "buy", "price": "24800.25", "size": 10, "depth_level": 1},
            {"event_id": "nq-cancel", "order_id": "nq-order", "exchange_seq": 2,
             "instrument_id": "NQH6", "event_ns": _t(10), "action": "cancel",
             "side": "buy", "price": "24800.25", "size": 3, "depth_level": 1},
        ]
        config = {"events": events, "instrument_id": "NQH6", "source_symbol": "NQ",
                  "required_depth_levels": 1, "depth_coverage": 1,
                  "depth_complete": True, "known_at": _t(10)}
        observed = o163(config)
        self.assertEqual(observed.state, "computed")
        self.assertEqual(observed.value["remaining"], Decimal(7))
        self.assertEqual(o163({**config, "required_depth_levels": 2}).state, "hole")
        foreign = [{**events[0], "instrument_id": "ESH6"}, events[1]]
        self.assertEqual(o163({**config, "events": foreign}).state, "invalid")

        supplied = o165({"state_label": "A", "state_at": _t(10), "known_at": _t(10),
                         "source_symbol": "NQ", "depth_levels": 1, "required_depth_levels": 1,
                         "source_observation_id": "nq-observed-A", "high_aggression": True,
                         "low_response_efficiency": True, "opposite_liquidity_holds_and_refills": True})
        self.assertEqual(supplied.state, "supplied")
        self.assertIsNone(supplied.value["automatic_state"])

    def test_nq_transition_counts_require_provenance_not_different_numbers(self):
        row = {"counts": {"D": 84, "A": 12, "B": 4, "E": 0, "W": 0},
               "from_state": "D", "to_state": "D", "state_at": _t(10),
               "next_state_at": _t(10, 1), "conditioning_known_at": _t(9, 59),
               "cohort_id": "NQ-declared-cohort", "source_symbol": "NQ",
               "source_counts_symbol": "NQ", "row_count": 100, "known_at": _t(10, 1)}
        # Equal frequencies can occur independently; instrument provenance is decisive.
        self.assertEqual(o166(row).state, "computed")
        transferred = o166({**row, "source_counts_symbol": "AAPL"})
        self.assertEqual(transferred.state, "invalid")
        self.assertIn("HOLE:O166:cohort_identity", transferred.hole_ids)

    def test_every_m10_object_has_f1_and_real_c08_rows(self):
        rows = run_object_fixtures(objects_for(METHOD))
        self.assertTrue(rows)
        self.assertTrue(all(row["status"] == "pass" for row in rows),
                        [row for row in rows if row["status"] != "pass"])
        for object_id in objects_for(METHOD):
            self.assertTrue(any(row["id"] == f"{object_id}-F1" for row in rows), object_id)
            for mutation in ("c08_late", "c08_missing", "c08_identity"):
                self.assertTrue(
                    any(row["recipe"] == object_id and row["kind"] == mutation for row in rows),
                    (object_id, mutation),
                )

    def test_real_manifest_mutations_and_empty_acquired_scope(self):
        op = _state("A")
        document = fixture_document(METHOD, "state_observation", "episode", op)
        parsed = parse_manifest(document, METHOD)
        good = score_episode(parsed[0]["episode"], *parsed[1:])
        self.assertEqual(good["verdict"], "pass")

        identity = json.loads(json.dumps(document))
        state_object = next(row for row in identity["objects"]
                           if row["object_id"].endswith(":state"))
        state_object["band_id"] = "foreign-band"
        parsed = parse_manifest(identity, METHOD)
        identity_result = score_episode(parsed[0]["episode"], *parsed[1:])
        self.assertEqual(identity_result["verdict"], "fail")
        self.assertTrue(any(hole["kind"] == "identity" for hole in identity_result["holes"]))

        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            data = root / "data"
            reports = root / "reports"
            data.mkdir()
            run = subprocess.run([
                sys.executable, str(RUNNER), "method-pass", "--method", METHOD,
                "--scope", "acquired", "--data-root", str(data),
                "--report-root", str(reports),
            ], cwd=ROOT, text=True, capture_output=True)
            self.assertEqual(run.returncode, 0, run.stderr)
            report = json.loads((reports / "jetbundle-states.json").read_text())
            self.assertEqual(report["status"], "source_hole")
            self.assertEqual(report["summary"]["N"], 0)
            self.assertEqual(report["quality"]["fixture_failures"], 0)

    def test_transition_state_record_regressions(self):
        base = _state("A")
        base.update({
            "next_state_at": _t(10, 1),
            "conditioning_known_at": _t(9, 59),
            "conditioning_observation_id": "conditioning-opaque",
            "adjacency_observation_id": "adjacency-opaque",
            "cadence_seconds": 60,
        })

        def score(document, fid):
            parsed = parse_manifest(document, METHOD)
            return score_episode(parsed[0][fid], *parsed[1:])

        # The state IDs are opaque strings and do not encode the B/A/D/E/W
        # label.  The explicit state field is the source of truth.
        opaque = _transition_document("M10-reg-opaque", base)
        self.assertEqual(score(opaque, "M10-reg-opaque")["verdict"], "pass")

        branch = fixture_document(METHOD, "state_observation", "M10-reg-branch", _state("A"))
        branch["candidates"][0]["branch"] = "B"
        self.assertEqual(score(branch, "M10-reg-branch")["verdict"], "fail")

        missing_next = _transition_document("M10-reg-missing-next", base)
        missing_next["candidates"][0].pop("next_state_candidate_id")
        self.assertEqual(score(missing_next, "M10-reg-missing-next")["verdict"], "unknown")

        current_false = _transition_document("M10-reg-current-false", base)
        current_id = "M10-reg-current-false:current-state"
        assertion = next(row for row in current_false["assertions"]
                         if row["candidate_id"] == current_id
                         and row["field"] == "high_aggression")
        assertion["value"] = False
        for evidence in current_false["evidence"]:
            if evidence["evidence_id"] in assertion["evidence_ids"]:
                evidence["payload"]["high_aggression"] = False
        self.assertEqual(score(current_false, "M10-reg-current-false")["verdict"], "fail")

        wrong_next = _transition_document("M10-reg-wrong-next", base)
        next_id = "M10-reg-wrong-next:next-state"
        next_candidate = next(row for row in wrong_next["candidates"]
                              if row["candidate_id"] == next_id)
        next_candidate["instrument_id"] = "NQ-fixture"
        self.assertEqual(score(wrong_next, "M10-reg-wrong-next")["verdict"], "fail")

        gap = dict(base)
        gap["next_state_at"] = _t(10, 3)
        gap_document = _transition_document("M10-reg-gap", gap)
        self.assertEqual(score(gap_document, "M10-reg-gap")["verdict"], "unknown")

    def test_transition_rejects_linked_transition_predicate_without_recursion(self):
        base = _state("A")
        base.update({
            "next_state_at": _t(10, 1),
            "conditioning_known_at": _t(9, 59),
            "conditioning_observation_id": "conditioning-opaque",
            "adjacency_observation_id": "adjacency-opaque",
            "cadence_seconds": 60,
        })
        document = _transition_document("M10-reg-linked-transition", base)
        current_id = "M10-reg-linked-transition:current-state"
        current = next(row for row in document["candidates"]
                       if row["candidate_id"] == current_id)
        current["predicate"] = "transition_observation"
        parsed = parse_manifest(document, METHOD)
        result = score_episode(parsed[0]["M10-reg-linked-transition"], *parsed[1:])
        self.assertEqual(result["verdict"], "fail")
        self.assertIn("HOLE:O165:state_records", result["hole_ids"])

    def test_missing_state_label_is_unknown(self):
        document = fixture_document(METHOD, "state_observation", "M10-reg-missing-state", _state("A"))
        document["candidates"][0]["operands"].pop("state")
        parsed = parse_manifest(document, METHOD)
        result = score_episode(parsed[0]["M10-reg-missing-state"], *parsed[1:])
        self.assertEqual(result["verdict"], "unknown")
        self.assertIn("HOLE:O165:state", result["hole_ids"])

    def test_irregular_next_time_needs_and_accepts_explicit_source_link(self):
        base = _state("A")
        base.update({
            "next_state_at": _t(10, 1, 30),
            "conditioning_known_at": _t(9, 59),
            "conditioning_observation_id": "conditioning-opaque",
            "adjacency_observation_id": "adjacency-opaque",
            "cadence_seconds": 60,
        })
        document = _transition_document("M10-reg-irregular", base)
        parsed = parse_manifest(document, METHOD)
        missing = score_episode(parsed[0]["M10-reg-irregular"], *parsed[1:])
        self.assertEqual(missing["verdict"], "unknown")

        # Supply the source's opaque linkage and explicit no-gap/no-reset
        # status on the actual cited observation payloads.
        for candidate in document["candidates"]:
            if candidate["candidate_id"] == "M10-reg-irregular:next-state":
                candidate["predicate"] = "state_observation"
        current_state_id = "opaque-current-state"
        next_state_id = "opaque-next-state"
        for evidence in document["evidence"]:
            payload = evidence["payload"]
            payload.update({"previous_state_id": current_state_id,
                            "gap": False, "reset": False,
                            "current_state_id": current_state_id,
                            "next_state_id": next_state_id})
        parsed = parse_manifest(document, METHOD)
        linked = score_episode(parsed[0]["M10-reg-irregular"], *parsed[1:])
        self.assertEqual(linked["verdict"], "pass")


if __name__ == "__main__":
    unittest.main()
