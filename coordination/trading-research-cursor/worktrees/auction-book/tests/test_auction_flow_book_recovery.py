import copy
import hashlib
import unittest

import pyarrow as pa

from trading_research.errors import ContractError, IntegrityError
from trading_research.operations.artifacts import canonical_json
from trading_research.research.auction_flow_book_recovery import ReportedBBOReinitializer
from trading_research.research.auction_flow_quotes import QuoteWindow


KNOWN = {"A", "M", "C", "R", "T", "N"}
UPDATES = {"A", "M", "C"}
LINEAGE = (
    "observed_history_complete", "blocked", "terminal_episode_unresolved",
    "rows", "candidate_valid_rows", "candidate_invalid_rows", "changed_book_valid_rows",
    "original_valid_rows", "provider_flagged_records", "clear_rows", "unknown_action_rows",
    "episode_count", "resolved_episode_count", "unresolved_episode_count", "episodes",
    "first_unresolved_invalidation", "last_source_address", "source_key",
    "prefix_start_ns", "cumulative_coverage_complete", "policy", "version",
)


def quote_row(t, *, source_order, instrument_id=1, bid=400, ask=401, bid_size=7, ask_size=9,
              book_valid=1, snapshot=0, raw_flags=128, raw_action="M", raw_side="B",
              known_at_ns=None, source_key="src", source_row=None, delay=250):
    if snapshot:
        raw_flags = raw_flags | 32
    return {"t": t, "source_order": source_order, "instrument_id": instrument_id,
            "bid": bid, "ask": ask, "bid_size": bid_size, "ask_size": ask_size,
            "book_valid": book_valid, "snapshot": snapshot, "raw_flags": raw_flags,
            "raw_action": raw_action, "raw_side": raw_side,
            "known_at_ns": t + delay if known_at_ns is None else known_at_ns,
            "source_key": source_key, "source_row": source_order if source_row is None else source_row}


def make_quote_table(rows, *, action_type=None, side_type=None, source_key_type=None,
                     book_valid_type=None, metadata=None, field_metadata=None):
    numeric = ("t", "source_order", "instrument_id", "bid", "ask", "bid_size", "ask_size",
               "book_valid", "snapshot", "raw_flags", "known_at_ns", "source_row")
    data = {name: [row[name] for row in rows] for name in numeric}

    def encode(values, typ):
        if typ is not None and (pa.types.is_binary(typ) or pa.types.is_large_binary(typ)):
            return [None if value is None else value.encode() if isinstance(value, str) else value
                    for value in values]
        return values

    arrays = {name: pa.array(data[name], type=(book_valid_type or pa.uint8()) if name == "book_valid"
                             else pa.uint8() if name == "snapshot" else pa.int64())
              for name in numeric}
    arrays["raw_action"] = pa.array(encode([row["raw_action"] for row in rows], action_type),
                                    type=action_type or pa.string())
    arrays["raw_side"] = pa.array(encode([row["raw_side"] for row in rows], side_type),
                                  type=side_type or pa.string())
    arrays["source_key"] = pa.array(encode([row["source_key"] for row in rows], source_key_type),
                                    type=source_key_type or pa.string())
    table = pa.table(arrays)
    if field_metadata is not None:
        index = table.schema.get_field_index("book_valid")
        field = table.schema.field(index).with_metadata(field_metadata)
        table = table.set_column(index, field, table[index])
    if metadata is not None:
        table = table.replace_schema_metadata(metadata)
    return table


def kernel(*, start=0, end=100, delay=250, maximum_rows=10_000, maximum_episodes=50,
           continuation=None):
    return ReportedBBOReinitializer(
        instrument_id=1, start_ns=start, end_ns=end, latency_ns=delay,
        maximum_rows=maximum_rows, maximum_episodes=maximum_episodes, continuation=continuation)


def address_of(row, *, delay=250):
    return {"source_key": row["source_key"], "source_row": row["source_row"],
            "source_order": row["source_order"], "t": row["t"],
            "known_at": row["known_at_ns"] if row.get("known_at_ns") is not None else row["t"] + delay,
            "raw_flags": row["raw_flags"], "raw_action": row["raw_action"]}


def reference_reinitialize(rows, *, blocked=False, history_complete=True, episodes=None, delay=250):
    episodes = [] if episodes is None else [dict(item) for item in episodes]
    out = []
    for row in rows:
        flags, action = row["raw_flags"], row["raw_action"]
        bit4, snapshot, last = bool(flags & 4), bool(flags & 32), bool(flags & 128)
        unknown = action not in KNOWN
        update = action in UPDATES
        invalidation = bit4 or action == "R" or unknown
        domain = (0 < row["bid"] <= row["ask"] < 2**53
                  and 0 < row["bid_size"] < 2**32 - 1 and 0 < row["ask_size"] < 2**32 - 1)
        recovery = update and not bit4 and not snapshot and last and domain
        addr = address_of(row, delay=delay)
        if blocked:
            if recovery:
                out.append(1)
                episodes[-1] = {**episodes[-1], "recovery": dict(addr), "unresolved": False}
                blocked = False
            else:
                out.append(0)
                if bit4 or unknown:
                    history_complete = False
                if bit4:
                    episodes[-1]["provider_flagged_records"] += 1
        elif invalidation:
            out.append(0)
            if bit4 or unknown:
                history_complete = False
            episodes.append({"episode_index": len(episodes) + 1, "invalidation": dict(addr),
                             "recovery": None, "unresolved": True,
                             "provider_flagged_records": 1 if bit4 else 0})
            blocked = True
        elif not episodes:
            out.append(int(row["book_valid"]))
        else:
            out.append(1 if update and not bit4 and domain else 0)
    return out, {"blocked": blocked, "observed_history_complete": history_complete, "episodes": episodes}


def project(rows, *, chunks=None, start=0, end=100, delay=250, coverage=True, continuation=None,
            **kwargs):
    table = make_quote_table(rows)
    value = kernel(start=start, end=end, delay=delay, continuation=continuation, **kwargs)
    parts = []
    if not rows:
        parts.append(value.add(table))
    elif chunks is None:
        parts.append(value.add(table))
    else:
        offset = 0
        for width in chunks:
            parts.append(value.add(table.slice(offset, width)))
            offset += width
        if offset < len(table):
            parts.append(value.add(table.slice(offset)))
    projected = parts[0] if len(parts) == 1 else pa.concat_tables(parts)
    report = value.finish(coverage_complete=coverage)
    return projected, report, value.carry(), value


def lineage(report):
    return {name: report[name] for name in LINEAGE}


def redigest(carry, **updates):
    payload = copy.deepcopy({key: value for key, value in {**carry, **updates}.items() if key != "sha256"})
    return {**payload, "sha256": hashlib.sha256(canonical_json(payload)).hexdigest()}


def main_sequence():
    return [
        quote_row(10, source_order=0, raw_action="A"),
        quote_row(20, source_order=1, bid_size=8, ask_size=8),
        quote_row(25, source_order=2, raw_flags=132, book_valid=0),
        quote_row(25, source_order=3, raw_flags=132, book_valid=0, source_row=3),
        quote_row(28, source_order=4, raw_action="T", book_valid=0),
        quote_row(29, source_order=5, raw_action="A", snapshot=1, book_valid=0),
        quote_row(30, source_order=6, raw_action="A", raw_flags=0, book_valid=0),
        quote_row(31, source_order=7, raw_action="A", bid=402, ask=401, book_valid=0),
        quote_row(32, source_order=8, raw_action="A", bid_size=0, book_valid=0),
        quote_row(35, source_order=9, book_valid=0, bid_size=8, ask_size=9),
        quote_row(45, source_order=10, book_valid=0, bid_size=10, ask_size=6),
        quote_row(45, source_order=11, snapshot=1, book_valid=0, bid_size=11, ask_size=5),
        quote_row(60, source_order=12, raw_flags=132, book_valid=0),
        quote_row(70, source_order=13, raw_action="C", book_valid=0, bid_size=9, ask_size=4),
        quote_row(80, source_order=14, raw_action="N", book_valid=0),
        quote_row(90, source_order=15, book_valid=0, bid_size=12, ask_size=3),
    ]


class AuctionFlowBookRecoveryTests(unittest.TestCase):
    def assert_same_schema_and_other_columns(self, original, projected):
        self.assertTrue(original.schema.equals(projected.schema, check_metadata=True))
        for name in original.schema.names:
            if name == "book_valid":
                continue
            self.assertTrue(original[name].equals(projected[name]), name)

    def assert_unmodified_rows(self, original, projected):
        for left, right in zip(original.to_pylist(), projected.to_pylist()):
            body = {key: value for key, value in left.items() if key != "book_valid"}
            self.assertEqual(body, {key: value for key, value in right.items() if key != "book_valid"})
            if left["book_valid"] == right["book_valid"]:
                self.assertEqual(left, right)

    def assert_matches_reference(self, rows, projected, report, **state):
        expected, status = reference_reinitialize(rows, **state)
        self.assertEqual(projected["book_valid"].to_pylist(), expected)
        self.assertEqual(report["blocked"], status["blocked"])
        self.assertEqual(report["observed_history_complete"], status["observed_history_complete"])
        self.assertEqual(report["episodes"], status["episodes"])
        self.assertEqual(report["terminal_episode_unresolved"], status["blocked"])

    def test_locked_and_noncrossed_valid_quotes_copy_original_book_valid(self):
        rows = [quote_row(10, source_order=0, bid=400, ask=400, bid_size=2, ask_size=1),
                quote_row(20, source_order=1, bid=400, ask=401, bid_size=4, ask_size=2)]
        projected, report, _, _ = project(rows)
        self.assertEqual(projected["book_valid"].to_pylist(), [1, 1])
        self.assertEqual(report["changed_book_valid_rows"], 0)
        self.assertTrue(report["observed_history_complete"])
        self.assertFalse(report["blocked"])
        self.assert_matches_reference(rows, projected, report)

    def test_repeated_flags_are_one_episode(self):
        rows = [quote_row(10, source_order=0),
                quote_row(20, source_order=1, raw_flags=132, book_valid=0),
                quote_row(21, source_order=2, raw_flags=132, book_valid=0),
                quote_row(22, source_order=3, raw_flags=132, book_valid=0),
                quote_row(40, source_order=4, book_valid=0, bid_size=8, ask_size=9)]
        projected, report, _, _ = project(rows)
        self.assertEqual(projected["book_valid"].to_pylist(), [1, 0, 0, 0, 1])
        self.assertEqual(report["episode_count"], 1)
        self.assertEqual(report["provider_flagged_records"], 3)
        self.assertEqual(report["episodes"][0]["provider_flagged_records"], 3)
        self.assertEqual(report["episodes"][0]["invalidation"], address_of(rows[1]))
        self.assertEqual(report["episodes"][0]["recovery"], address_of(rows[4]))
        self.assertFalse(report["observed_history_complete"])
        self.assert_matches_reference(rows, projected, report)

    def test_qualifying_completed_ordinary_restart(self):
        rows = [quote_row(10, source_order=0),
                quote_row(20, source_order=1, raw_flags=132, book_valid=0),
                quote_row(30, source_order=2, book_valid=0, bid_size=8, ask_size=9)]
        projected, report, _, _ = project(rows)
        self.assertEqual(projected["book_valid"].to_pylist(), [1, 0, 1])
        self.assertFalse(report["blocked"])
        self.assertFalse(report["observed_history_complete"])
        self.assertEqual(report["changed_book_valid_rows"], 1)

    def test_snapshot_last_no_last_trade_clear_and_unknown_cannot_restart(self):
        base = [quote_row(10, source_order=0),
                quote_row(20, source_order=1, raw_flags=132, book_valid=0)]
        rejected = [
            quote_row(30, source_order=2, snapshot=1, raw_flags=160, book_valid=0),
            quote_row(31, source_order=3, raw_flags=0, book_valid=0),
            quote_row(32, source_order=4, raw_action="T", book_valid=0),
            quote_row(33, source_order=5, raw_action="N", book_valid=0),
            quote_row(34, source_order=6, raw_action="R", book_valid=0),
            quote_row(35, source_order=7, raw_action="?", book_valid=0),
            quote_row(40, source_order=8, book_valid=0),
        ]
        rows = base + rejected
        projected, report, _, _ = project(rows)
        self.assertEqual(projected["book_valid"].to_pylist(), [1, 0, 0, 0, 0, 0, 0, 0, 1])
        self.assertEqual(report["episode_count"], 1)
        self.assertEqual(report["unknown_action_rows"], 1)
        self.assertEqual(report["clear_rows"], 1)
        self.assert_matches_reference(rows, projected, report)

    def test_crossed_zero_sentinel_and_locked_bbo(self):
        locked = [quote_row(5, source_order=0, bid=400, ask=400)]
        after = [
            quote_row(10, source_order=1, raw_flags=132, book_valid=0),
            quote_row(20, source_order=2, bid=402, ask=401, book_valid=0),
            quote_row(21, source_order=3, bid_size=0, book_valid=0),
            quote_row(22, source_order=4, ask=2**53, book_valid=0),
            quote_row(23, source_order=5, bid=0, book_valid=0),
            quote_row(24, source_order=6, bid_size=2**32 - 1, book_valid=0),
            quote_row(40, source_order=7, bid=400, ask=400, bid_size=3, ask_size=3, book_valid=0),
        ]
        rows = locked + after
        projected, report, _, _ = project(rows)
        self.assertEqual(projected["book_valid"].to_pylist(), [1, 0, 0, 0, 0, 0, 0, 1])
        self.assertEqual(report["episodes"][0]["recovery"]["t"], 40)
        self.assert_matches_reference(rows, projected, report)

    def test_second_episode_and_equal_timestamps_keep_original_order(self):
        rows = main_sequence()
        projected, report, _, _ = project(rows)
        self.assertEqual(projected["book_valid"].to_pylist(),
                         [1, 1, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 0, 1, 0, 1])
        self.assertEqual(report["episode_count"], 2)
        self.assertEqual(report["episodes"][0]["invalidation"]["source_order"], 2)
        self.assertEqual(report["episodes"][0]["recovery"]["source_order"], 9)
        self.assertEqual(report["episodes"][1]["invalidation"]["source_order"], 12)
        self.assertEqual(report["episodes"][1]["recovery"]["source_order"], 13)
        self.assertEqual(report["last_source_address"]["source_order"], 15)
        self.assertFalse(report["observed_history_complete"])
        self.assert_matches_reference(rows, projected, report)

    def test_clear_then_flag_or_unknown_history_stays_false_across_carry(self):
        prefix = [quote_row(10, source_order=0),
                  quote_row(20, source_order=1, raw_action="R", book_valid=0)]
        _, first, carry, _ = project(prefix, end=40)
        self.assertTrue(first["observed_history_complete"])
        self.assertTrue(first["blocked"])
        self.assertEqual(first["episode_count"], 1)
        later = [quote_row(50, source_order=2, raw_flags=132, book_valid=0),
                 quote_row(51, source_order=3, raw_action="?", book_valid=0),
                 quote_row(70, source_order=4, book_valid=0)]
        projected, report, _, _ = project(later, start=40, end=100, continuation=carry)
        self.assertEqual(projected["book_valid"].to_pylist(), [0, 0, 1])
        self.assertFalse(report["observed_history_complete"])
        self.assertEqual(report["episode_count"], 1)
        self.assertEqual(report["episodes"][0]["invalidation"]["t"], 20)
        self.assertEqual(report["episodes"][0]["recovery"]["t"], 70)
        self.assertEqual(report["prefix_start_ns"], 0)
        self.assertGreater(report["provider_flagged_records"], 0)
        self.assertGreater(report["unknown_action_rows"], 0)

    def test_false_coverage_then_later_true_remains_cumulatively_incomplete(self):
        rows = [quote_row(10, source_order=0), quote_row(50, source_order=1)]
        _, first, carry, _ = project(rows[:1], end=40, coverage=False)
        self.assertFalse(first["coverage_complete"])
        self.assertFalse(first["cumulative_coverage_complete"])
        self.assertTrue(first["observed_history_complete"])
        _, second, _, _ = project(rows[1:], start=40, end=100, continuation=carry, coverage=True)
        self.assertTrue(second["coverage_complete"])
        self.assertFalse(second["cumulative_coverage_complete"])
        self.assertTrue(second["observed_history_complete"])
        self.assertFalse(second["blocked"])

    def test_one_pass_batches_and_adjacent_cut_match_every_column_and_lineage(self):
        rows = main_sequence()
        expected_valid, _ = reference_reinitialize(rows)
        one, one_report, _, one_kernel = project(rows)
        self.assertEqual(one["book_valid"].to_pylist(), expected_valid)
        self.assert_same_schema_and_other_columns(make_quote_table(rows), one)
        self.assert_unmodified_rows(make_quote_table(rows), one)
        for chunks in ([1] * len(rows), [2, 3, 4, 1, 6], [5, 11], [len(rows)]):
            chunked, report, _, chunk_kernel = project(rows, chunks=chunks)
            self.assertTrue(one.schema.equals(chunked.schema, check_metadata=True))
            self.assertEqual(one.to_pylist(), chunked.to_pylist())
            self.assertEqual(lineage(one_report), lineage(report))
            self.assertEqual(one_kernel.episode_transition_visits, chunk_kernel.episode_transition_visits)
        cut = 28
        left = [row for row in rows if row["t"] < cut]
        right = [row for row in rows if row["t"] >= cut]
        first_table, first_report, carry, first_kernel = project(left, end=cut)
        second_table, second_report, _, second_kernel = project(right, start=cut, continuation=carry)
        combined = pa.concat_tables([first_table, second_table])
        self.assertTrue(one.schema.equals(combined.schema, check_metadata=True))
        self.assertEqual(one.to_pylist(), combined.to_pylist())
        self.assertEqual(lineage(one_report), lineage(second_report))
        self.assertEqual(first_report["episode_count"], 1)
        self.assertTrue(first_report["blocked"])
        self.assertEqual(first_report["first_unresolved_invalidation"]["source_order"], 2)
        self.assertEqual(second_report["episodes"][0]["invalidation"]["source_order"], 2)
        self.assertEqual(first_kernel.episode_transition_visits + second_kernel.episode_transition_visits,
                         one_kernel.episode_transition_visits)

    def test_sparse_python_episode_transitions_on_long_clean_and_repeated_flags(self):
        rows = []
        for i in range(800):
            rows.append(quote_row(i, source_order=i, bid_size=7 + (i % 3), ask_size=9))
        for i in range(800, 1200):
            rows.append(quote_row(i, source_order=i, raw_flags=132, book_valid=0))
        rows.append(quote_row(1200, source_order=1200, book_valid=0, bid_size=8, ask_size=9))
        for i in range(1201, 2000):
            rows.append(quote_row(i, source_order=i, book_valid=0, bid_size=8, ask_size=9))
        projected, report, _, value = project(rows, end=3000, maximum_rows=10_000)
        self.assertEqual(value.episode_transition_visits, 2)
        self.assertLess(value.episode_transition_visits, 10)
        self.assertEqual(report["episode_count"], 1)
        self.assertEqual(report["provider_flagged_records"], 400)
        self.assertEqual(projected["book_valid"].to_pylist()[799], 1)
        self.assertEqual(projected["book_valid"].to_pylist()[800], 0)
        self.assertEqual(projected["book_valid"].to_pylist()[1199], 0)
        self.assertEqual(projected["book_valid"].to_pylist()[1200], 1)
        self.assertEqual(projected["book_valid"].to_pylist()[-1], 1)

    def test_quote_window_excludes_gap_ofi_and_starts_standing_at_new_ordinary_quote(self):
        rows = [quote_row(5, source_order=0, raw_flags=132, book_valid=0),
                quote_row(20, source_order=1, book_valid=0, bid_size=8, ask_size=9),
                quote_row(40, source_order=2, book_valid=0, bid_size=10, ask_size=6)]
        projected, report, _, _ = project(rows, end=80)
        self.assertEqual(projected["book_valid"].to_pylist(), [0, 1, 1])
        self.assertFalse(report["observed_history_complete"])
        window = QuoteWindow(instrument_id=1, start_ns=0, end_ns=80, latency_ns=250, maximum_events=100)
        window.add(projected)
        measured = window.finish(coverage_complete=True)
        self.assertEqual(measured["fresh_quote_updates"], 2)
        self.assertEqual(measured["pressure_transitions"], 1)
        self.assertEqual(measured["ofi_contracts"], 5)
        self.assertEqual(measured["same_price_size_ofi"], 5)
        self.assertEqual(measured["observed_trusted_standing_duration_ns"], 60)
        self.assertEqual(measured["terminal_projection"]["economic_at"], 40)
        self.assertEqual(measured["book_recovery"],
                         "no recovery is inferred; original invalidation remains until supported source reconstruction")

    def test_schema_buffers_and_returned_addresses_are_isolated(self):
        rows = [quote_row(10, source_order=0),
                quote_row(20, source_order=1, raw_flags=132, book_valid=0),
                quote_row(30, source_order=2, book_valid=0)]
        original = make_quote_table(rows, book_valid_type=pa.int64(), metadata={b"src": b"mbp1"},
                                    field_metadata={b"unit": b"trust"})
        value = kernel()
        projected = value.add(original)
        self.assertTrue(original.schema.equals(projected.schema, check_metadata=True))
        self.assertEqual(projected.schema.field("book_valid").type, pa.int64())
        self.assertEqual(projected.schema.field("book_valid").metadata, {b"unit": b"trust"})
        self.assertEqual(original.schema.metadata, {b"src": b"mbp1"})
        self.assertEqual(original["book_valid"].to_pylist(), [1, 0, 0])
        self.assertEqual(projected["book_valid"].to_pylist(), [1, 0, 1])
        self.assert_same_schema_and_other_columns(original, projected)
        for name in original.schema.names:
            if name == "book_valid":
                continue
            self.assertEqual([chunk.buffers() for chunk in original[name].chunks],
                             [chunk.buffers() for chunk in projected[name].chunks])
        report = value.finish(coverage_complete=True)
        report["episodes"][0]["invalidation"]["t"] = -99
        report["last_source_address"]["source_order"] = -99
        carry = value.carry()
        self.assertEqual(carry["episodes"][0]["invalidation"]["t"], 20)
        self.assertEqual(carry["last_source_address"]["source_order"], 2)
        carry["blocked"] = True
        again = value.carry()
        self.assertFalse(again["blocked"])
        empty = kernel().add(original.slice(0, 0))
        self.assertTrue(original.schema.equals(empty.schema, check_metadata=True))
        self.assertEqual(len(empty), 0)

    def test_malformed_original_trust_mixed_source_delay_and_nulls(self):
        good = make_quote_table([quote_row(10, source_order=0), quote_row(20, source_order=1)])
        with self.assertRaises(IntegrityError):
            kernel().add(make_quote_table([quote_row(10, source_order=0, bid=402, ask=401)]))
        with self.assertRaises(IntegrityError):
            kernel().add(make_quote_table([quote_row(10, source_order=0, bid_size=0)]))
        with self.assertRaises(IntegrityError):
            kernel().add(make_quote_table([quote_row(10, source_order=0, raw_action="T")]))
        with self.assertRaises(IntegrityError):
            kernel().add(good.drop(["source_key"]))
        with self.assertRaises(IntegrityError):
            kernel().add(good.set_column(good.schema.get_field_index("t"), "t",
                                         pa.array([10, None], type=pa.int64())))
        delayed = make_quote_table([quote_row(10, source_order=0, known_at_ns=11)])
        with self.assertRaises(IntegrityError):
            kernel().add(delayed)
        mixed = make_quote_table([quote_row(10, source_order=0),
                                  quote_row(20, source_order=1, source_key="other")])
        with self.assertRaises(IntegrityError):
            kernel().add(mixed)
        numeric_action = good.set_column(good.schema.get_field_index("raw_action"), "raw_action",
                                         pa.array([1, 2], type=pa.int64()))
        with self.assertRaises(IntegrityError):
            kernel().add(numeric_action)
        other = make_quote_table([quote_row(10, source_order=0, instrument_id=2)])
        with self.assertRaises(IntegrityError):
            kernel().add(other)
        value = kernel()
        value.add(good.slice(0, 1))
        with self.assertRaises(IntegrityError):
            value.add(make_quote_table([quote_row(20, source_order=1, source_key="other")]))
        with self.assertRaises(IntegrityError):
            value.finish(coverage_complete=True)

    def test_categorical_string_binary_and_dictionary_values_are_preserved(self):
        rows = [quote_row(10, source_order=0, raw_action="A"),
                quote_row(20, source_order=1, raw_flags=132, book_valid=0, raw_action=None, raw_side=None),
                quote_row(40, source_order=2, book_valid=0)]
        for action_type, side_type, key_type in (
                (None, None, None),
                (pa.dictionary(pa.int8(), pa.string()), pa.dictionary(pa.int8(), pa.string()), pa.string()),
                (pa.binary(), pa.binary(), pa.binary()),
                (pa.large_string(), pa.large_string(), pa.large_string())):
            table = make_quote_table(rows, action_type=action_type, side_type=side_type,
                                     source_key_type=key_type)
            projected, report, _, _ = project(rows)
            value = kernel()
            actual = value.add(table)
            self.assertEqual(actual["book_valid"].to_pylist(), projected["book_valid"].to_pylist())
            self.assertTrue(table.schema.equals(actual.schema, check_metadata=True))
            self.assertTrue(table["raw_action"].equals(actual["raw_action"]))
            self.assertTrue(table["raw_flags"].equals(actual["raw_flags"]))
            finished = value.finish(coverage_complete=True)
            self.assertEqual(finished["episodes"][0]["invalidation"]["raw_action"], None)
            self.assertEqual(lineage(finished)["episode_count"], report["episode_count"])

    def test_capacity_one_over_and_poison(self):
        rows = [quote_row(10, source_order=0), quote_row(20, source_order=1),
                quote_row(30, source_order=2)]
        value = kernel(maximum_rows=2)
        with self.assertRaises(ContractError):
            value.add(make_quote_table(rows))
        with self.assertRaises(IntegrityError):
            value.add(make_quote_table(rows[:1]))
        with self.assertRaises(IntegrityError):
            value.finish(coverage_complete=True)
        with self.assertRaises(IntegrityError):
            value.carry()
        first = [quote_row(10, source_order=0),
                 quote_row(20, source_order=1, raw_flags=132, book_valid=0),
                 quote_row(30, source_order=2, book_valid=0),
                 quote_row(40, source_order=3, raw_flags=132, book_valid=0)]
        limited = kernel(maximum_episodes=1)
        with self.assertRaises(ContractError):
            limited.add(make_quote_table(first))
        with self.assertRaises(IntegrityError):
            limited.finish(coverage_complete=True)
        exact = kernel(maximum_rows=2)
        exact.add(make_quote_table(rows[:2]))
        exact.finish(coverage_complete=True)
        self.assertEqual(exact.carry()["rows"], 2)

    def test_corrupt_counts_actions_flags_key_order_and_carry_adjacency(self):
        rows = [quote_row(10, source_order=0),
                quote_row(20, source_order=1, raw_action="R", book_valid=0),
                quote_row(30, source_order=2, raw_flags=132, book_valid=0)]
        _, _, carry, _ = project(rows, end=40)
        self.assertFalse(carry["observed_history_complete"])
        self.assertTrue(carry["blocked"])
        with self.assertRaises(IntegrityError):
            kernel(start=40, continuation={**carry, "rows": 99})
        with self.assertRaises(IntegrityError):
            kernel(start=40, continuation=redigest(carry, rows=99, candidate_invalid_rows=99))
        with self.assertRaises(IntegrityError):
            kernel(start=40, continuation=redigest(carry, observed_history_complete=True))
        with self.assertRaises(IntegrityError):
            kernel(start=41, continuation=carry)
        with self.assertRaises(IntegrityError):
            kernel(start=40, delay=100, continuation=carry)
        with self.assertRaises(IntegrityError):
            kernel(start=40, continuation=redigest(carry, next_start_ns=40, event_end_ns=39))
        with self.assertRaises(IntegrityError):
            kernel(start=40, continuation=redigest(carry, extra_field=1))
        mutated = copy.deepcopy(carry)
        mutated["episodes"][0]["invalidation"]["raw_action"] = "M"
        mutated["episodes"][0]["invalidation"]["raw_flags"] = 128
        with self.assertRaises(IntegrityError):
            kernel(start=40, continuation=redigest(mutated))
        wrong_key = copy.deepcopy(carry)
        wrong_key["episodes"][0]["invalidation"]["source_key"] = "other"
        with self.assertRaises(IntegrityError):
            kernel(start=40, continuation=redigest(wrong_key))
        empty = kernel(end=40)
        empty.add(make_quote_table(rows).slice(0, 0))
        empty.finish(coverage_complete=True)
        stuffed = redigest(empty.carry(), episodes=carry["episodes"])
        with self.assertRaises(IntegrityError):
            kernel(start=40, continuation=stuffed)
        later = [quote_row(50, source_order=3, book_valid=0)]
        projected, report, _, _ = project(later, start=40, continuation=carry)
        self.assertEqual(projected["book_valid"].to_pylist(), [1])
        self.assertEqual(report["episode_count"], 1)
        self.assertEqual(report["episodes"][0]["invalidation"]["raw_action"], "R")
        self.assertFalse(report["observed_history_complete"])

    def test_empty_window_is_not_completeness_and_bit8_does_not_block_restart(self):
        value = kernel()
        empty = value.add(make_quote_table([]))
        report = value.finish(coverage_complete=True)
        self.assertEqual(len(empty), 0)
        self.assertTrue(report["empty_observed_window"])
        self.assertTrue(report["empty_window_is_not_market_completeness"])
        rows = [quote_row(10, source_order=0),
                quote_row(20, source_order=1, raw_flags=132, book_valid=0),
                quote_row(30, source_order=2, raw_flags=136, book_valid=0)]
        projected, recovered, _, _ = project(rows)
        self.assertEqual(projected["book_valid"].to_pylist(), [1, 0, 1])
        self.assertFalse(recovered["blocked"])


if __name__ == "__main__":
    unittest.main()
