import unittest

from trading_research.errors import IntegrityError
from trading_research.research.auction_flow_coordinates import RetainedCoordinateIndex


START = 1704067200000000000


def record(n, *, known=START, activation=START - 1000, expiry=START + 10**15, symbol="NQZ4", instrument=106364):
    return {"source_path": "quantpad/definition/2024.parquet", "source_row": n,
            "source_sha256": "source", "raw_fields_sha256": f"raw:{n}", "instrument_id": instrument,
            "raw_symbol": symbol, "contract_key": f"NQ:{symbol}:{instrument}:{activation}:{expiry}",
            "lifetime_id": f"lifetime:{activation}:{expiry}", "definition_version": f"definition:{n}",
            "known_at_ns": known, "valid_from_ns": activation, "valid_until_ns": expiry,
            "tick_size": "0.25", "eligible": True, "reason": "accepted_fixture"}


def manifest(records, blocks=()):
    return {"root": "NQ", "records": records, "indexed_records": len(records),
            "blocks": list(blocks), "unknown_instrument_ids": []}


def supplement(records):
    first = records[0]
    audited = [{**{k: r[k] for k in ("source_path", "source_row", "source_sha256", "raw_fields_sha256", "definition_version")},
                "t": r["known_at_ns"] - 250_000_000, "ts_recv": r["known_at_ns"] - 250_000_000,
                "security_update_action": "A"} for r in records]
    return {"actual_accepted": True, "generic_admission_untouched": True,
            "target_instrument_id": 106364, "target_symbol": "NQZ4", "target_year": 2024,
            "target_a_count": len(audited), "audits": [{"target_relevant_fields": audited}],
            "candidate_report": {"nonretroactive": True,
                "physical_coordinate": {"tick_size": "0.25", "expiration_ns": first["valid_until_ns"]},
                "authoritative_original": {"contract_key": first["contract_key"], "known_at_ns": first["known_at_ns"]},
                "latest_known_versions": {first["definition_version"]: first["known_at_ns"]}}}


class AuctionFlowCoordinateTests(unittest.TestCase):
    def test_original_availability_expiry_and_known_inactive_update_are_reused(self):
        first = record(0, known=START + 10)
        inactive = record(1, known=START + 100, activation=START + 1000, expiry=START + 2000)
        index = RetainedCoordinateIndex(manifest([first, inactive]), source_version="fixture")
        self.assertEqual(index.resolve(106364, START)[1], "unavailable_definition")
        self.assertEqual(index.resolve(106364, START + 10)[0].definition_version, "definition:0")
        self.assertEqual(index.resolve(106364, START + 101)[1], "unavailable_definition")

    def test_snapshot_changes_current_definition_without_rewriting_prior_coordinate(self):
        first = record(0, known=START + 10)
        second = record(1, known=START + 100, activation=START - 2000)
        rows = [first, second]
        original = RetainedCoordinateIndex(manifest(rows), source_version="fixture")
        self.assertTrue(original.resolve(106364, START + 101)[1].startswith("ambiguous_definition"))
        resolved = RetainedCoordinateIndex(manifest(rows), source_version="fixture",
                    snapshot_supplement=supplement(rows), snapshot_version="fixture-proof")
        before = resolved.resolve(106364, START + 99)
        after = resolved.resolve(106364, START + 101)
        self.assertEqual(before[0].definition_version, "definition:0")
        self.assertEqual(after[0].definition_version, "definition:1")
        self.assertEqual(after[0].contract_key, before[0].contract_key)
        self.assertEqual(after[1], "accepted_snapshot_supplement")
        # The second version is absent from the earlier minute-selected map.
        self.assertNotIn("definition:1", supplement(rows)["candidate_report"]["latest_known_versions"])

    def test_block_remains_unavailable_and_unbound_or_changed_snapshot_is_rejected(self):
        first = record(0)
        block = {k: first[k] for k in ("source_path", "source_row", "source_sha256", "raw_fields_sha256",
                                     "instrument_id", "raw_symbol", "known_at_ns", "reason")}
        block.update(known_at_ns=START + 100, blocks_prior_lifetime=True)
        index = RetainedCoordinateIndex(manifest([first], [block]), source_version="fixture")
        self.assertEqual(index.resolve(106364, START + 101)[1], "blocked_definition")
        second = record(1, known=START + 100, activation=START - 2000)
        proof = supplement([first, second])
        proof["audits"][0]["target_relevant_fields"][1]["source_row"] = 900
        with self.assertRaises(IntegrityError):
            RetainedCoordinateIndex(manifest([first, second]), source_version="fixture",
                                    snapshot_supplement=proof, snapshot_version="fixture-proof")

    def test_newer_unaudited_or_ineligible_state_does_not_resurrect_an_older_snapshot(self):
        first=record(0,known=START+10)
        second=record(1,known=START+100,activation=START-2000)
        latest=record(2,known=START+200,activation=START-3000)
        index=RetainedCoordinateIndex(manifest([first,second,latest]),source_version='fixture',
            snapshot_supplement=supplement([first,second]),snapshot_version='fixture-proof')
        self.assertEqual(index.resolve(106364,START+150)[0].definition_version,'definition:1')
        result,status=index.resolve(106364,START+201)
        self.assertIsNone(result)
        self.assertTrue(status.startswith('ambiguous_definition'))
        latest={**latest,'eligible':False,'reason':'unresolved_terms'}
        index=RetainedCoordinateIndex(manifest([first,second,latest]),source_version='fixture',
            snapshot_supplement=supplement([first,second,latest]),snapshot_version='fixture-proof')
        self.assertIsNone(index.resolve(106364,START+201)[0])


if __name__ == "__main__":
    unittest.main()
