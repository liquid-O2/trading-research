"""Source-written regression cases for the candidate-only supplement.

These tests are intentionally kept next to the candidate rather than wired
into the repository test suite.  The registered worker will run equivalent
checks only after it has supplied the complete raw definition rows and the
matched canonical rows from check7/extract8.
"""

from __future__ import annotations

import unittest

from trading_research.research.jumbo_definition_supersession import (
    DEFAULT_LATENCY_NS,
    INT64_MAX,
    SOURCE_SUPERSESSION_STATUS,
    TARGET_INSTRUMENT_ID,
    TARGET_PUBLISHER_ID,
    TARGET_SYMBOL,
    build_definition_supersession_supplement,
    SNAPSHOT_SEMANTICS, SNAPSHOT_DOC, QUANTPAD_DOC,
)


EXPIRATION_NS = 1_734_652_800_000_000_000
JAN_2_2024_NS = 1_704_153_600_000_000_000
FEB_3_2024_NS = 1_707_004_800_000_000_000
FEB_10_2024_NS = 1_707_609_600_000_000_000
MAR_1_2024_NS = 1_709_251_200_000_000_000
APR_1_2024_NS = 1_711_929_600_000_000_000


def definition_row(action: str, *, activation_ns: int, event_ns: int,
                   tick: object = 0.25, symbol: str = TARGET_SYMBOL,
                   publisher: str = "quantpad", source_row: int | None = None,
                   publisher_id: int = TARGET_PUBLISHER_ID,
                   instrument_class: str | None = None,
                   security_type: str | None = None,
                   definition_version: str | None = None,
                   expiration_ns: int = EXPIRATION_NS) -> dict:
    row = {
        "security_update_action": action,
        "publisher": publisher,
        "instrument_id": TARGET_INSTRUMENT_ID,
        "raw_symbol": symbol,
        "expiration": expiration_ns,
        "publisher_id": publisher_id,
        "min_price_increment": tick,
        "activation": activation_ns,
        "t": event_ns,
        "ts_recv": event_ns,
        "source_path": "raw/nq-definition.dbn",
    }
    if source_row is not None:
        row["source_row"] = source_row
    if instrument_class is not None:
        row["instrument_class"] = instrument_class
    if security_type is not None:
        row["security_type"] = security_type
    if definition_version is not None:
        row["definition_version"] = definition_version
    return row


def observed_row(start_ns: int, value: int, *, date: str = "2024-01-02") -> dict:
    return {
        "date": date,
        "start_ns": start_ns,
        "instrument_id": TARGET_INSTRUMENT_ID,
        "open": value,
        "high": value + 1,
        "low": value - 1,
        "close": value,
        "volume": 7,
        "caller_owned_column": "preserved",
    }


class DefinitionSupersessionSupplementTests(unittest.TestCase):
    def snapshot_fixture(self):
        rows = [definition_row("A", activation_ns=1_650_000_000_000_000_000,
                               event_ns=JAN_2_2024_NS, instrument_class="F",
                               definition_version="first-active-snapshot", source_row=0),
                definition_row("A", activation_ns=1_660_000_000_000_000_000,
                               event_ns=JAN_2_2024_NS + 86_400_000_000_000,
                               instrument_class="F", definition_version="next-active-snapshot", source_row=1)]
        for row in rows:
            row.update(source_sha256="a" * 64, contract_multiplier=1)
        binding = {"semantics": SNAPSHOT_SEMANTICS, "dataset": "GLBX.MDP3",
                   "publisher": "quantpad", "symbol": "NQ.c.0", "schema": "definition",
                   "source_path": rows[0]["source_path"], "source_sha256": "a" * 64,
                   "provider_documentation": SNAPSHOT_DOC, "export_documentation": QUANTPAD_DOC}
        return rows, binding

    def test_bound_daily_snapshots_are_active_states_without_inventing_M(self):
        rows, binding = self.snapshot_fixture()
        before = observed_row(JAN_2_2024_NS, 10)
        first = observed_row(JAN_2_2024_NS + DEFAULT_LATENCY_NS, 20)
        next_day = observed_row(rows[1]["ts_recv"] + DEFAULT_LATENCY_NS, 30, date="2024-01-03")
        result = build_definition_supersession_supplement(rows, [before, first, next_day], snapshot_binding=binding)
        self.assertEqual(result["report"]["status"], SOURCE_SUPERSESSION_STATUS)
        self.assertEqual(result["report"]["raw_actions"], ("A", "A"))
        self.assertNotIn("authoritative_modification", result["report"])
        self.assertEqual(result["pre_known_rows"], (before,))
        selected = result["candidate_canonical2024"]
        self.assertEqual([r["candidate_definition"]["definition_version"] for r in selected],
                         ["first-active-snapshot", "next-active-snapshot"])
        self.assertEqual(selected[0]["candidate_definition"]["contract_key"], selected[1]["candidate_definition"]["contract_key"])
        self.assertEqual(selected[0]["original"], first)
        self.assertEqual(rows[1]["security_update_action"], "A")

    def test_snapshot_timestamp_shape_does_not_replace_source_binding(self):
        rows, binding = self.snapshot_fixture()
        observed = [observed_row(rows[1]["ts_recv"] + 60_000_000_000, 20, date="2024-01-03")]
        self.assertEqual(build_definition_supersession_supplement(rows, observed)["report"]["status"], "unresolved")
        for field, value in (("source_sha256", "b" * 64), ("dataset", "OTHER"), ("provider_documentation", "unknown")):
            with self.subTest(field=field):
                result = build_definition_supersession_supplement(rows, observed, snapshot_binding={**binding, field: value})
                self.assertEqual(result["report"]["status"], "unresolved")

    def test_snapshot_requires_compatible_physical_fields_and_weekday_midnight_receipt(self):
        import copy
        rows, binding = self.snapshot_fixture()
        observed = [observed_row(MAR_1_2024_NS, 20, date="2024-03-01")]
        mutations = ({"min_price_increment": .5}, {"contract_multiplier": 2},
                     {"ts_recv": rows[1]["ts_recv"] + 1},
                     {"ts_recv": JAN_2_2024_NS + 4 * 86_400_000_000_000},
                     {"t": rows[1]["ts_recv"] + 1}, {"instrument_class": None})
        for mutation in mutations:
            with self.subTest(mutation=mutation):
                changed = copy.deepcopy(rows)
                changed[1].update(mutation)
                result = build_definition_supersession_supplement(changed, observed, snapshot_binding=binding)
                self.assertEqual(result["report"]["status"], "unresolved")

    def test_actual_m_preserves_physical_coordinate_and_is_nonretroactive(self) -> None:
        original_activation = 1_690_000_000_000_000_000
        corrected_activation = 1_695_000_000_000_000_000
        original_event = 1_700_000_000_000_000_000
        modification_event = FEB_3_2024_NS
        rows = [
            definition_row("A", activation_ns=original_activation,
                           event_ns=original_event, source_row=10,
                           definition_version="original-definition-v1"),
            definition_row("M", activation_ns=corrected_activation,
                           event_ns=modification_event, source_row=11,
                           definition_version="corrected-definition-v2"),
        ]
        pre = observed_row(JAN_2_2024_NS, 100)
        post = observed_row(MAR_1_2024_NS, 200, date="2024-03-01")

        result = build_definition_supersession_supplement(rows, [pre, post])

        self.assertEqual(result["report"]["status"], SOURCE_SUPERSESSION_STATUS)
        self.assertEqual(result["report"]["candidate_count"], 1)
        self.assertEqual(result["report"]["corrected_count"], 0)
        self.assertEqual(result["report"]["pre_known_count"], 1)
        self.assertTrue(result["report"]["nonretroactive"])
        self.assertEqual(result["pre_known_rows"], (pre,))
        self.assertEqual(result["candidate_canonical2024"][0]["original"], post)
        self.assertEqual(result["corrected_canonical2024"], ())
        self.assertEqual(
            result["candidate_canonical2024"][0]["candidate_definition"]["definition_version"],
            "corrected-definition-v2",
        )
        self.assertEqual(
            result["candidate_canonical2024"][0]["candidate_definition"]["original_contract_key"],
            "NQ:NQZ4:106364:1690000000000000000:1734652800000000000",
        )
        self.assertEqual(
            result["report"]["authoritative_original"]["coordinate"]["identity"],
            result["report"]["authoritative_modification"]["coordinate"]["identity"],
        )
        self.assertNotEqual(
            result["report"]["authoritative_original"]["activation_ns"],
            result["report"]["authoritative_modification"]["activation_ns"],
        )
        self.assertTrue(
            result["report"]["candidate_supersession_version"].startswith(
                "jumbo-definition-supersession-nonretroactive-v1:"
            )
        )
        self.assertEqual(
            result["report"]["supersession_known_at_ns"],
            modification_event + DEFAULT_LATENCY_NS,
        )

    def test_bar_at_known_time_is_admitted_but_earlier_bar_is_pre_known(self) -> None:
        event_ns = FEB_3_2024_NS
        rows = [
            definition_row("A", activation_ns=1_690_000_000_000_000_000,
                           event_ns=1_700_000_000_000_000_000),
            definition_row("M", activation_ns=1_695_000_000_000_000_000,
                           event_ns=event_ns),
        ]
        known_at = event_ns + DEFAULT_LATENCY_NS
        before = observed_row(known_at - 1, 1, date="2024-02-03")
        at_boundary = observed_row(known_at, 2, date="2024-02-03")

        result = build_definition_supersession_supplement(rows, [before, at_boundary])

        self.assertEqual(result["report"]["candidate_count"], 1)
        self.assertEqual(result["report"]["corrected_count"], 0)
        self.assertEqual(result["report"]["pre_known_count"], 1)
        self.assertEqual(result["candidate_canonical2024"][0]["original"], at_boundary)

    def test_each_bar_uses_latest_known_m_without_future_leakage(self) -> None:
        rows = [
            definition_row("A", activation_ns=1_690_000_000_000_000_000,
                           event_ns=1_700_000_000_000_000_000,
                           definition_version="original-definition-v1"),
            definition_row("M", activation_ns=1_695_000_000_000_000_000,
                           event_ns=FEB_3_2024_NS,
                           definition_version="changed-definition-v2"),
            definition_row("M", activation_ns=1_696_000_000_000_000_000,
                           event_ns=MAR_1_2024_NS,
                           definition_version="changed-definition-v3"),
        ]
        between = observed_row(FEB_10_2024_NS, 100, date="2024-02-10")
        after = observed_row(APR_1_2024_NS, 200, date="2024-04-01")

        result = build_definition_supersession_supplement(rows, [between, after])

        self.assertEqual(result["report"]["status"], SOURCE_SUPERSESSION_STATUS)
        candidates = result["candidate_canonical2024"]
        self.assertEqual(len(candidates), 2)
        self.assertEqual(
            candidates[0]["candidate_definition"]["definition_version"],
            "changed-definition-v2",
        )
        self.assertEqual(
            candidates[1]["candidate_definition"]["definition_version"],
            "changed-definition-v3",
        )
        self.assertEqual(
            candidates[0]["candidate_definition"]["original_contract_key"],
            candidates[1]["candidate_definition"]["original_contract_key"],
        )

    def test_rows_known_after_2024_are_reported_outside_conflict_scope(self) -> None:
        rows = [
            definition_row("A", activation_ns=1_690_000_000_000_000_000,
                           event_ns=1_700_000_000_000_000_000),
            definition_row("M", activation_ns=1_695_000_000_000_000_000,
                           event_ns=FEB_3_2024_NS),
            definition_row("M", activation_ns=1_696_000_000_000_000_000,
                           event_ns=1_735_776_000_000_000_000),
        ]

        result = build_definition_supersession_supplement(
            rows, [observed_row(MAR_1_2024_NS, 100, date="2024-03-01")]
        )

        self.assertEqual(result["report"]["status"], SOURCE_SUPERSESSION_STATUS)
        self.assertEqual(result["report"]["future_definition_rows_excluded_from_conflict_scope"], 1)
        self.assertFalse(result["report"]["future_definition_rows_affect_candidates"])
        self.assertEqual(
            result["report"]["receipt_selection"]["authoritative_modification"]["chosen_receipt_ns"],
            FEB_3_2024_NS,
        )

    def test_a_only_is_unresolved_without_inferred_modification(self) -> None:
        rows = [definition_row("A", activation_ns=1_690_000_000_000_000_000,
                              event_ns=1_700_000_000_000_000_000)]

        result = build_definition_supersession_supplement(
            rows, [observed_row(MAR_1_2024_NS, 100, date="2024-03-01")]
        )

        self.assertEqual(result["report"]["status"], "unresolved")
        self.assertIn("a_only_no_authoritative_modification",
                      result["report"]["reason_codes"])
        self.assertEqual(result["corrected_canonical2024"], ())

    def test_same_known_time_is_unresolved(self) -> None:
        event_ns = FEB_3_2024_NS
        rows = [
            definition_row("A", activation_ns=1_690_000_000_000_000_000,
                           event_ns=event_ns),
            definition_row("M", activation_ns=1_695_000_000_000_000_000,
                           event_ns=event_ns),
        ]

        result = build_definition_supersession_supplement(
            rows, [observed_row(MAR_1_2024_NS, 100, date="2024-03-01")]
        )

        self.assertEqual(result["report"]["status"], "unresolved")
        self.assertIn("same_known_at_conflict", result["report"]["reason_codes"])

    def test_unknown_action_is_unresolved(self) -> None:
        rows = [
            definition_row("A", activation_ns=1_690_000_000_000_000_000,
                           event_ns=1_700_000_000_000_000_000),
            definition_row("X", activation_ns=1_695_000_000_000_000_000,
                           event_ns=FEB_3_2024_NS),
        ]

        result = build_definition_supersession_supplement(
            rows, [observed_row(MAR_1_2024_NS, 100, date="2024-03-01")]
        )

        self.assertEqual(result["report"]["status"], "unresolved")
        self.assertIn("unknown_security_update_action",
                      result["report"]["reason_codes"])
        self.assertEqual(result["report"]["raw_actions"], ("A", "X"))

    def test_tick_mismatch_is_a_physical_coordinate_conflict(self) -> None:
        rows = [
            definition_row("A", activation_ns=1_690_000_000_000_000_000,
                           event_ns=1_700_000_000_000_000_000, tick=0.25),
            definition_row("M", activation_ns=1_695_000_000_000_000_000,
                           event_ns=FEB_3_2024_NS, tick=0.5),
        ]

        result = build_definition_supersession_supplement(
            rows, [observed_row(MAR_1_2024_NS, 100, date="2024-03-01")]
        )

        self.assertEqual(result["report"]["status"], "unresolved")
        self.assertIn("physical_coordinate_conflict",
                      result["report"]["reason_codes"])

    def test_cross_file_source_namespace_is_unresolved(self) -> None:
        original = definition_row(
            "A", activation_ns=1_690_000_000_000_000_000,
            event_ns=1_700_000_000_000_000_000,
        )
        modification = definition_row(
            "M", activation_ns=1_695_000_000_000_000_000,
            event_ns=FEB_3_2024_NS,
        )
        modification["source_path"] = "raw/nq-definition-next-year.dbn"

        result = build_definition_supersession_supplement(
            [original, modification],
            [observed_row(MAR_1_2024_NS, 100, date="2024-03-01")],
        )

        self.assertEqual(result["report"]["status"], "unresolved")
        self.assertIn("source_namespace_conflict", result["report"]["reason_codes"])

    def test_late_activation_is_unresolved(self) -> None:
        rows = [
            definition_row("A", activation_ns=1_700_000_000_000_000_000,
                           event_ns=1_700_000_000_000_000_000),
            definition_row("M", activation_ns=1_710_000_000_000_000_000,
                           event_ns=FEB_3_2024_NS),
        ]

        result = build_definition_supersession_supplement(
            rows, [observed_row(MAR_1_2024_NS, 100, date="2024-03-01")]
        )

        self.assertEqual(result["report"]["status"], "unresolved")
        self.assertIn("activation_not_before_all_observed_2024_dates",
                      result["report"]["reason_codes"])

    def test_publisher_id_mismatch_is_unresolved(self) -> None:
        rows = [
            definition_row("A", activation_ns=1_690_000_000_000_000_000,
                           event_ns=1_700_000_000_000_000_000),
            definition_row("M", activation_ns=1_695_000_000_000_000_000,
                           event_ns=FEB_3_2024_NS, publisher_id=2),
        ]

        result = build_definition_supersession_supplement(
            rows, [observed_row(MAR_1_2024_NS, 100, date="2024-03-01")]
        )

        self.assertEqual(result["report"]["status"], "unresolved")
        self.assertIn("malformed_target_definition_row",
                      result["report"]["reason_codes"])

    def test_missing_raw_publisher_id_binds_to_source_namespace(self) -> None:
        original = definition_row(
            "A", activation_ns=1_690_000_000_000_000_000,
            event_ns=1_700_000_000_000_000_000,
        )
        original.pop("publisher_id")
        modification = definition_row(
            "M", activation_ns=1_695_000_000_000_000_000,
            event_ns=FEB_3_2024_NS,
        )
        modification.pop("publisher_id")

        result = build_definition_supersession_supplement(
            [original, modification],
            [observed_row(MAR_1_2024_NS, 100, date="2024-03-01")],
        )

        self.assertEqual(result["report"]["status"], SOURCE_SUPERSESSION_STATUS)
        self.assertEqual(result["report"]["publisher_id"], None)
        self.assertEqual(
            result["report"]["publisher_id_resolution"],
            "publisher_namespace_only_raw_field_absent",
        )
        self.assertEqual(result["report"]["candidate_count"], 1)

    def test_rows_at_or_after_expiry_are_excluded_without_rewriting_earlier_rows(self) -> None:
        rows = [
            definition_row("A", activation_ns=1_690_000_000_000_000_000,
                           event_ns=1_700_000_000_000_000_000,
                           expiration_ns=MAR_1_2024_NS),
            definition_row("M", activation_ns=1_695_000_000_000_000_000,
                           event_ns=FEB_3_2024_NS,
                           expiration_ns=MAR_1_2024_NS),
        ]
        expired = observed_row(MAR_1_2024_NS, 100, date="2024-03-01")

        result = build_definition_supersession_supplement(rows, [expired])

        self.assertEqual(result["report"]["status"], SOURCE_SUPERSESSION_STATUS)
        self.assertEqual(result["report"]["candidate_count"], 0)
        self.assertEqual(result["report"]["expiry_excluded_count"], 1)
        self.assertEqual(result["candidate_canonical2024"], ())

    def test_known_at_int64_overflow_is_unresolved(self) -> None:
        rows = [
            definition_row("A", activation_ns=1_690_000_000_000_000_000,
                           event_ns=1_700_000_000_000_000_000),
            definition_row("M", activation_ns=1_695_000_000_000_000_000,
                           event_ns=INT64_MAX - DEFAULT_LATENCY_NS + 1),
        ]

        result = build_definition_supersession_supplement(
            rows, [observed_row(MAR_1_2024_NS, 100, date="2024-03-01")]
        )

        self.assertEqual(result["report"]["status"], "unresolved")
        self.assertIn("malformed_target_definition_row",
                      result["report"]["reason_codes"])


if __name__ == "__main__":
    unittest.main()
