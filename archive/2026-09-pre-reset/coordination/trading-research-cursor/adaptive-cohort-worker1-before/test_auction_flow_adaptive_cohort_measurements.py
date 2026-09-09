"""Independent literal cases for the M02 adaptive/soft cohort consumer."""
from fractions import Fraction
import unittest

import pyarrow as pa

from trading_research.errors import ContractError, IntegrityError
from trading_research.foundations.time import MINUTE, NS
from trading_research.measurements.cvd import CohortChannel, CohortDefinition
from trading_research.research.auction_flow_cohorts import CohortWindow
from trading_research.research.auction_flow_adaptive_cohort_measurements import (
    ADAPTIVE_RECIPES,
    AGGREGATION_UNIT,
    SOFT_KNOTS,
    SOURCE_LATENCY_NS,
    VERSION,
    build_cohort_tables,
    default_available_at_ns,
    default_train_end_ns,
    fit_definitions,
    frozen_fixed_definitions,
    histogram_for_training,
    scientific_join_eligibility,
    serialize_definition,
    serialize_fit_evidence,
    validate_source_identity,
)
from tests.test_auction_flow_prepared_trades import make_trade_table, trade_row


F = Fraction
BASE = 1_577_836_800 * NS
LATENCY = SOURCE_LATENCY_NS
SOURCE_META = "aa" * 32
SOURCE_PATH = "quantpad/cme__nq-continuous-futures__mbp-1/adaptive-cohort-fixture.parquet"
SOURCE_VARIANT = "fixture12ab34"
SOURCE_KEY = "src"
SOURCE_COLLECTION = "cme-mbp-1-nq"
CONTRACT = "NQ:NQH0:1:0:1000"


def identity(*, start=BASE, end=None, root="NQ", key=SOURCE_KEY):
    return {
        "root": root,
        "source_path": SOURCE_PATH,
        "source_metadata_sha256": SOURCE_META,
        "source_variant": SOURCE_VARIANT,
        "acquired_event_start_ns": start,
        "acquired_event_end_ns": start + 86400 * NS if end is None else end,
        "source_key": key,
        "source_collection": SOURCE_COLLECTION,
        "economic_date": "2020-01-01",
    }


def trade(at, size, side, order, *, instrument_id=1, key=SOURCE_KEY):
    raw = "B" if side == 1 else "A" if side == -1 else "N"
    return trade_row(
        at, source_order=order, size=size, raw_side=raw, delay=LATENCY,
        instrument_id=instrument_id, source_row=order, source_key=key)


def trades(specs, **kwargs):
    return make_trade_table([trade(*spec, **kwargs) for spec in specs])


def obs_row(*, start, end, instrument_id=1, contract_key=CONTRACT, empty=False, complete=True,
            presence=True):
    return {
        "root": "NQ",
        "source_path": SOURCE_PATH,
        "source_metadata_sha256": SOURCE_META,
        "source_variant": SOURCE_VARIANT,
        "instrument_id": instrument_id,
        "contract_key": contract_key,
        "event_start_ns": start,
        "event_end_ns": end,
        "known_at_ns": end + LATENCY,
        "source_coverage_complete": complete,
        "coordinate_complete": complete,
        "flow_history_complete": complete,
        "empty_observed_window": empty,
        "source_instrument_presence": presence,
    }


def obs_table(rows):
    names = (
        "root", "source_path", "source_metadata_sha256", "source_variant",
        "instrument_id", "contract_key", "event_start_ns", "event_end_ns", "known_at_ns",
        "source_coverage_complete", "coordinate_complete", "flow_history_complete",
        "empty_observed_window", "source_instrument_presence",
    )
    return pa.table({name: [row[name] for row in rows] for name in names})


def minute_atoms(count, *, start=BASE, instrument_id=1, empty=False, complete=True):
    return [
        obs_row(start=start + i * MINUTE, end=start + (i + 1) * MINUTE,
                instrument_id=instrument_id, empty=empty, complete=complete)
        for i in range(count)
    ]


def member_window(*, end=BASE + 60 * MINUTE, published=None, complete=True):
    published_at = end + LATENCY if published is None else published
    return {"end": end, "published_at": published_at, "history_complete": complete}


def records(table, **equals):
    out = []
    for index in range(len(table)):
        row = {name: table[name][index].as_py() for name in table.column_names}
        if all(row[name] == value for name, value in equals.items()):
            out.append(row)
    return out


def frac(row, name):
    num, den = row[f"{name}_numerator"], row[f"{name}_denominator"]
    if num is None:
        return None
    return Fraction(num, den)


def build(specs, atoms, *, inst=1, definitions=None, cut_start=None, cut_end=None, key=SOURCE_KEY):
    if definitions is None:
        definitions = frozen_fixed_definitions()
    start = atoms[0]["event_start_ns"] if atoms else BASE
    last = atoms[-1]["event_end_ns"] if atoms else BASE + MINUTE
    if cut_start is None:
        cut_start = last
    if cut_end is None:
        cut_end = cut_start + 5 * MINUTE
    return build_cohort_tables(
        trades(specs, instrument_id=inst, key=key),
        obs_table(atoms),
        definitions,
        identity(start=BASE, key=key),
        cut_start,
        cut_end,
        economic_date="2020-01-01",
    )


class IdentityAndSerializationTests(unittest.TestCase):
    def test_identity_requires_source_key_and_collection(self):
        raw = identity()
        parsed = validate_source_identity(raw)
        self.assertEqual(parsed["source_key"], SOURCE_KEY)
        self.assertEqual(parsed["source_collection"], SOURCE_COLLECTION)
        incomplete = dict(raw)
        del incomplete["source_key"]
        with self.assertRaises(IntegrityError):
            validate_source_identity(incomplete)

    def test_soft_knots_and_default_nq_es_availability_are_distinct(self):
        self.assertEqual(SOFT_KNOTS, (1, 30, 60, 75, 100, 250))
        self.assertEqual(default_available_at_ns("NQ"), default_train_end_ns("NQ"))
        self.assertEqual(default_available_at_ns("ES"), 1_609_459_200 * NS)
        self.assertEqual(default_available_at_ns("NQ"), 1_672_531_200 * NS)
        self.assertGreater(default_available_at_ns("NQ"), default_available_at_ns("ES"))
        frozen = frozen_fixed_definitions()
        ids = [item["definition"].id for item in frozen.values()]
        self.assertEqual(len(ids), len(set(ids)))
        self.assertEqual(frozen["soft_piecewise_linear_knots"]["definition"].knots, SOFT_KNOTS)
        self.assertTrue(frozen["ny_ge100"]["family_occupancy_only"])
        self.assertFalse(frozen["fixed_all"]["family_occupancy_only"])
        self.assertFalse(frozen["soft_piecewise_linear_knots"]["family_occupancy_only"])

    def test_serialize_definition_and_fit_are_deterministic(self):
        definition = frozen_fixed_definitions()["fixed_all"]["definition"]
        self.assertEqual(serialize_definition(definition), serialize_definition(definition))
        sizes = trades(((BASE + 1, 1, 1, 0), (BASE + 2, 2, -1, 1), (BASE + 3, 3, 1, 2),
                        (BASE + 4, 4, 1, 3)))
        hist = histogram_for_training(
            sizes, obs_table(minute_atoms(1, empty=False)), identity(),
            member_id="train-a", member_window=member_window(),
            source_manifest="fixture-source", fold_manifest="fixture-fold")
        fitted = fit_definitions(
            hist, train_end=BASE + 2 * 60 * MINUTE, available_at=BASE + 2 * 60 * MINUTE,
            member_identities=("train-a",), member_windows={"train-a": member_window()},
            source_collection=SOURCE_COLLECTION, root="NQ")
        evidence = serialize_fit_evidence(fitted["fits"]["equal_count_quartiles"])
        self.assertEqual(evidence, serialize_fit_evidence(fitted["fits"]["equal_count_quartiles"]))
        self.assertFalse(evidence["admitted_for_serving"])
        self.assertEqual(evidence["publication_status"], "unpublished")
        self.assertEqual(fitted["version"], VERSION)


class PathLiteralTests(unittest.TestCase):
    def test_plus10_minus20_plus10_close0_high10_low_minus10(self):
        specs = ((BASE + 1, 10, 1, 0), (BASE + 2, 20, -1, 1), (BASE + 3, 10, 1, 2))
        atoms = minute_atoms(15)
        built = build(specs, atoms)
        rows = records(built["minutes"], definition_name="fixed_all", channel_id="all",
                       event_start_ns=BASE)
        self.assertEqual(len(rows), 1)
        row = rows[0]
        self.assertEqual(frac(row, "open"), 0)
        self.assertEqual(frac(row, "close"), 0)
        self.assertEqual(frac(row, "high"), 10)
        self.assertEqual(frac(row, "low"), -10)
        self.assertEqual(row["high_at_ns"], BASE + 1)
        self.assertEqual(row["low_at_ns"], BASE + 2)
        self.assertLess(row["high_at_ns"], row["low_at_ns"])
        self.assertEqual(row["high_source_order"], 0)
        self.assertEqual(row["low_source_order"], 1)
        self.assertEqual(row["prints"], 3)
        self.assertEqual(row["volume"], 40)
        self.assertGreater(row["event_start_ns"], 2 ** 53)
        self.assertGreater(row["known_at_ns"], 2 ** 53)

    def test_hard_cutoff_neighbors(self):
        specs = (
            (BASE + 10, 29, 1, 0), (BASE + 20, 30, -1, 1), (BASE + 30, 60, 1, 2),
            (BASE + 40, 61, 0, 3), (BASE + 50, 74, -1, 4), (BASE + 60, 75, 1, 5),
            (BASE + 70, 99, -1, 6), (BASE + 80, 100, 1, 7),
        )
        built = build(specs, minute_atoms(15))
        expected = {
            "ny_ge100": {100},
            "london_ge75": {75, 99, 100},
            "inclusive30_through60": {30, 60},
        }
        for name, sizes in expected.items():
            row = records(built["minutes"], definition_name=name, channel_id="included",
                          event_start_ns=BASE)[0]
            self.assertEqual(row["contributing_prints"], len(sizes))
            self.assertEqual(frac(row, "volume"), sum(sizes))
            self.assertTrue(row["family_occupancy_only"])
            self.assertFalse(row["partition"])
        all_row = records(built["minutes"], definition_name="fixed_all", channel_id="all",
                          event_start_ns=BASE)[0]
        self.assertEqual(all_row["prints"], 8)
        self.assertTrue(all_row["partition"])
        self.assertFalse(all_row["family_occupancy_only"])

    def test_soft_partition_includes_above_250_and_sums_to_one(self):
        definition = frozen_fixed_definitions()["soft_piecewise_linear_knots"]["definition"]
        self.assertEqual(sum(definition.weights(1), F(0)), 1)
        self.assertEqual(definition.weights(1)[0], 1)
        self.assertEqual(definition.weights(400)[-1], 1)
        self.assertEqual(sum(definition.weights(400), F(0)), 1)
        self.assertEqual(definition.weights(45)[1], F(1, 2))
        self.assertEqual(definition.weights(45)[2], F(1, 2))
        specs = ((BASE + 1, 1, 1, 0), (BASE + 2, 45, -1, 1), (BASE + 3, 400, 1, 2))
        built = build(specs, minute_atoms(15))
        rows = records(built["minutes"], definition_name="soft_piecewise_linear_knots",
                       event_start_ns=BASE)
        volume = sum((frac(row, "volume") for row in rows), F(0))
        prints = sum((frac(row, "weighted_prints") for row in rows), F(0))
        close = sum((frac(row, "close") for row in rows), F(0))
        self.assertEqual(volume, 1 + 45 + 400)
        self.assertEqual(prints, 3)
        self.assertEqual(close, 1 - 45 + 400)
        self.assertTrue(all(row["partition"] for row in rows))
        above = next(row for row in rows if row["channel_id"] == "knot:250")
        self.assertEqual(frac(above, "volume"), 400)
        self.assertEqual(above["contributing_prints"], 1)

    def test_unknown_concentrated_in_one_cohort(self):
        specs = ((BASE + 1, 100, 0, 0), (BASE + 2, 2, 1, 1))
        built = build(specs, minute_atoms(15))
        included = records(built["minutes"], definition_name="ny_ge100", channel_id="included",
                           event_start_ns=BASE)[0]
        below = records(built["minutes"], definition_name="ny_ge100", channel_id="excluded_below",
                        event_start_ns=BASE)[0]
        self.assertEqual(frac(included, "unknown"), 100)
        self.assertEqual(frac(below, "unknown"), 0)
        self.assertEqual(frac(included, "observed_signed_lower"), -100)
        self.assertEqual(frac(included, "observed_signed_upper"), 100)

    def test_two_raw_contracts_do_not_mix(self):
        specs_a = ((BASE + 1, 10, 1, 0),)
        specs_b = ((BASE + 2, 50, -1, 1),)
        atoms = minute_atoms(15, instrument_id=1) + minute_atoms(15, instrument_id=2)
        table = pa.concat_tables([
            trades(specs_a, instrument_id=1),
            trades(specs_b, instrument_id=2),
        ])
        built = build_cohort_tables(
            table, obs_table(atoms), frozen_fixed_definitions(), identity(),
            BASE + 15 * MINUTE, BASE + 20 * MINUTE, economic_date="2020-01-01")
        a = records(built["minutes"], instrument_id=1, definition_name="fixed_all",
                    channel_id="all", event_start_ns=BASE)[0]
        b = records(built["minutes"], instrument_id=2, definition_name="fixed_all",
                    channel_id="all", event_start_ns=BASE)[0]
        self.assertEqual(frac(a, "close"), 10)
        self.assertEqual(frac(b, "close"), -50)
        self.assertEqual(a["volume"], 10)
        self.assertEqual(b["volume"], 50)

    def test_empty_observed_versus_missing(self):
        atoms = [
            obs_row(start=BASE, end=BASE + MINUTE, empty=True),
            obs_row(start=BASE + MINUTE, end=BASE + 2 * MINUTE, empty=False),
        ]
        specs = ((BASE + MINUTE + 1, 4, 1, 0),)
        built = build(specs, atoms, cut_start=BASE + 5 * MINUTE, cut_end=BASE + 10 * MINUTE)
        empty = records(built["minutes"], event_start_ns=BASE, definition_name="fixed_all",
                        channel_id="all")[0]
        present = records(built["minutes"], event_start_ns=BASE + MINUTE,
                          definition_name="fixed_all", channel_id="all")[0]
        missing = records(built["minutes"], event_start_ns=BASE + 2 * MINUTE,
                          definition_name="fixed_all", channel_id="all")[0]
        self.assertTrue(empty["empty_observed_window"])
        self.assertFalse(empty["missing_window"])
        self.assertEqual(frac(empty, "close"), 0)
        self.assertEqual(empty["prints"], 0)
        self.assertFalse(present["empty_observed_window"])
        self.assertEqual(frac(present, "close"), 4)
        self.assertTrue(missing["missing_window"])
        self.assertFalse(missing["empty_observed_window"])
        self.assertIsNone(frac(missing, "close"))

    def test_unavailable_before_training_availability(self):
        available = BASE + 10 * MINUTE
        definition = CohortDefinition(
            "equal_count_quartiles", AGGREGATION_UNIT,
            (CohortChannel("bin:0", 1, 3), CohortChannel("bin:1", 3, None)),
            origin="fitted", available_at=available, fit_recipe_id="unpublished-fit-a")
        plan = {
            "equal_count_quartiles": {
                "name": "equal_count_quartiles", "kind": "adaptive", "definition": definition,
                "unavailable": None, "partition": True, "family_occupancy_only": False,
            }
        }
        specs = ((BASE + 1, 5, 1, 0),)
        built = build(specs, minute_atoms(15), definitions=plan)
        early = records(built["minutes"], definition_name="equal_count_quartiles",
                        event_start_ns=BASE)[0]
        late = records(built["minutes"], definition_name="equal_count_quartiles",
                       event_start_ns=BASE + 10 * MINUTE)[0]
        self.assertTrue(early["unavailable"])
        self.assertEqual(early["unavailable_reason"], "unavailable_before_training_availability")
        self.assertFalse(late["unavailable"])
        self.assertGreaterEqual(late["known_at_ns"], available)

    def test_suffix_deletion_and_concatenated_batch_parity(self):
        first = ((BASE + 1, 10, 1, 0), (BASE + 2, 20, -1, 1))
        third = ((BASE + MINUTE + 1, 10, 1, 2),)
        atoms = minute_atoms(15)
        full = build(first + third, atoms)
        prefix = build(first, atoms)
        first_full = records(full["minutes"], event_start_ns=BASE, definition_name="fixed_all",
                             channel_id="all")[0]
        first_prefix = records(prefix["minutes"], event_start_ns=BASE, definition_name="fixed_all",
                               channel_id="all")[0]
        self.assertEqual(frac(first_full, "close"), frac(first_prefix, "close"))
        self.assertEqual(frac(first_full, "high"), frac(first_prefix, "high"))
        self.assertEqual(frac(first_full, "low"), frac(first_prefix, "low"))
        table = trades(first + third)
        split = pa.concat_tables([table.slice(0, 2), table.slice(2, 1)])
        left = build_cohort_tables(
            table, obs_table(atoms), frozen_fixed_definitions(), identity(),
            BASE + 15 * MINUTE, BASE + 20 * MINUTE, economic_date="2020-01-01")
        right = build_cohort_tables(
            split, obs_table(atoms), frozen_fixed_definitions(), identity(),
            BASE + 15 * MINUTE, BASE + 20 * MINUTE, economic_date="2020-01-01")
        self.assertEqual(left["minutes"].to_pydict(), right["minutes"].to_pydict())
        self.assertEqual(left["formations"].to_pydict(), right["formations"].to_pydict())

    def test_composed_15min_matches_literal_whole_window(self):
        specs = (
            (BASE + 1, 10, 1, 0),
            (BASE + MINUTE + 1, 20, -1, 1),
            (BASE + 2 * MINUTE + 1, 10, 1, 2),
        )
        atoms = minute_atoms(15)
        built = build(specs, atoms)
        composed = records(
            built["formations"], definition_name="fixed_all", channel_id="all",
            formation_minutes=15, cut_ns=BASE + 15 * MINUTE)[0]
        window = CohortWindow(
            definition=frozen_fixed_definitions()["fixed_all"]["definition"],
            instrument_id=1, start_ns=BASE, end_ns=BASE + 15 * MINUTE, latency_ns=LATENCY)
        window.add(trades(specs))
        literal = window.record(source_coverage_complete=True, coordinate_complete=True)
        channel = literal["channels"][0]
        self.assertEqual(frac(composed, "open"), channel["open"])
        self.assertEqual(frac(composed, "close"), channel["close"])
        self.assertEqual(frac(composed, "high"), channel["high"])
        self.assertEqual(frac(composed, "low"), channel["low"])
        self.assertEqual(composed["high_at_ns"], channel["high_at_ns"])
        self.assertEqual(composed["low_at_ns"], channel["low_at_ns"])
        self.assertEqual(composed["high_source_order"], channel["high_source_order"])
        self.assertEqual(composed["low_source_order"], channel["low_source_order"])
        self.assertEqual(composed["prints"], 3)
        self.assertEqual(composed["volume"], 40)

    def test_invalid_source_aggregation_is_rejected(self):
        specs = ((BASE + 1, 2, 1, 0), (BASE + 2, 3, -1, 1))
        mixed = make_trade_table([
            trade(BASE + 1, 2, 1, 0, key="one"),
            trade(BASE + 2, 3, -1, 1, key="two"),
        ])
        with self.assertRaises(IntegrityError):
            build_cohort_tables(
                mixed, obs_table(minute_atoms(15)), frozen_fixed_definitions(),
                identity(), BASE + 15 * MINUTE, BASE + 20 * MINUTE)
        with self.assertRaises(IntegrityError):
            build_cohort_tables(
                trades(specs, key="other"), obs_table(minute_atoms(15)),
                frozen_fixed_definitions(), identity(), BASE + 15 * MINUTE, BASE + 20 * MINUTE)

    def test_scientific_join_keys_are_present(self):
        built = build(((BASE + 1, 2, 1, 0),), minute_atoms(15))
        feature = records(built["formations"], definition_name="fixed_all", channel_id="all",
                          formation_minutes=15)[0]
        label = {
            "root": feature["root"],
            "source_path": feature["source_path"],
            "source_metadata_sha256": feature["source_metadata_sha256"],
            "source_variant": feature["source_variant"],
            "acquired_event_start_ns": feature["acquired_event_start_ns"],
            "acquired_event_end_ns": feature["acquired_event_end_ns"],
            "instrument_id": feature["instrument_id"],
            "contract_key": feature["contract_key"],
            "cut_ns": feature["cut_ns"],
            "latency_ns": LATENCY,
            "known_at_ns": feature["known_at_ns"],
        }
        joined = scientific_join_eligibility(feature, label)
        self.assertIn("eligible", joined)
        self.assertEqual(joined["same_source_identity"], True)
        self.assertEqual(joined["same_instrument"], True)
        self.assertEqual(joined["same_cut"], True)


class TrainingFitTests(unittest.TestCase):
    def histogram(self, sizes, *, member_id="train-a", complete=True, window=None):
        specs = tuple((BASE + index + 1, size, 1, index) for index, size in enumerate(sizes))
        return histogram_for_training(
            trades(specs), obs_table(minute_atoms(1, empty=not sizes, complete=complete)),
            identity(), member_id=member_id,
            member_window=window or member_window(),
            source_manifest="fixture-source", fold_manifest="fixture-fold")

    def test_equal_count_versus_volume_unequal_sample(self):
        hist = self.histogram([1, 1, 1, 7])
        fitted = fit_definitions(
            hist, train_end=BASE + 2 * 60 * MINUTE, available_at=BASE + 2 * 60 * MINUTE,
            member_identities=("train-a",), member_windows={"train-a": member_window()},
            root="NQ", source_collection=SOURCE_COLLECTION)
        count = fitted["fits"]["equal_count_quartiles"]
        volume = fitted["fits"]["equal_volume_quartiles"]
        self.assertNotEqual(count["recipe"]["requested_thresholds"],
                            volume["recipe"]["requested_thresholds"])
        self.assertEqual(count["recipe"]["weighting"], "count")
        self.assertEqual(volume["recipe"]["weighting"], "volume")
        self.assertEqual(sum(count["realized_count"]), 4)
        self.assertEqual(sum(volume["realized_volume"]), 10)
        self.assertNotEqual(count["definition"].id, volume["definition"].id)
        self.assertFalse(fitted["admitted_for_serving"])

    def test_tied_size_thresholds_collapse(self):
        hist = self.histogram([5, 5, 5, 5])
        fitted = fit_definitions(
            hist, train_end=BASE + 2 * 60 * MINUTE, available_at=BASE + 2 * 60 * MINUTE,
            member_identities=("train-a",), member_windows={"train-a": member_window()})
        quartiles = fitted["fits"]["equal_count_quartiles"]
        self.assertEqual(quartiles["recipe"]["requested_thresholds"], (6, 6, 6))
        self.assertEqual(len(quartiles["definition"].channels), 2)
        self.assertEqual(quartiles["realized_count"], (4, 0))
        self.assertEqual(quartiles["recipe"]["tie_policy"], "lower_bin_then_merge_empty")

    def test_top35_count_and_named_volume_sensitivity_stay_distinct(self):
        hist = self.histogram(list(range(1, 21)))
        fitted = fit_definitions(
            hist, train_end=BASE + 2 * 60 * MINUTE, available_at=BASE + 2 * 60 * MINUTE,
            member_identities=("train-a",), member_windows={"train-a": member_window()})
        count = fitted["fits"]["source_top35_count_quantile"]
        volume = fitted["fits"]["source_top35_volume_quantile_sensitivity"]
        self.assertEqual(count["definition"].channels[1].lower_inclusive, 14)
        self.assertEqual(count["realized_count"], (13, 7))
        self.assertEqual([name for name, _, _ in ADAPTIVE_RECIPES],
                         ["equal_count_quartiles", "equal_volume_quartiles",
                          "source_top35_count_quantile",
                          "source_top35_volume_quantile_sensitivity"])
        self.assertNotEqual(count["definition"].id, volume["definition"].id)
        self.assertEqual(count["recipe"]["weighting"], "count")
        self.assertEqual(volume["recipe"]["weighting"], "volume")

    def test_complete_pairs_merge_without_expanding_prints(self):
        atoms = minute_atoms(1, empty=True)
        hist = histogram_for_training(
            make_trade_table([]), obs_table(atoms), identity(),
            member_id="pairs-a", member_window=member_window(),
            source_manifest="fixture-source", fold_manifest="fixture-fold",
            complete_pairs=((2, 10 ** 6), (3, 7)))
        self.assertEqual(hist["report"]["prints"], 10 ** 6 + 7)
        self.assertEqual(hist["report"]["contracts"], 2 * 10 ** 6 + 21)
        self.assertFalse(hist["coverage_inferred_from_prints"])

    def test_training_member_future_duplicate_and_partial_rejection(self):
        sizes = trades(((BASE + 1, 2, 1, 0),))
        atoms = minute_atoms(1)
        with self.assertRaises(ContractError):
            histogram_for_training(
                sizes, obs_table(atoms), identity(), member_id="train-a",
                member_window=member_window(end=BASE + 10 * 60 * MINUTE),
                source_manifest="fixture-source", fold_manifest="fixture-fold",
                train_end=BASE + MINUTE)
        with self.assertRaises(ContractError):
            histogram_for_training(
                sizes, obs_table(atoms), identity(), member_id="train-a",
                member_window=member_window(complete=False),
                source_manifest="fixture-source", fold_manifest="fixture-fold")
        with self.assertRaises(ContractError):
            histogram_for_training(
                sizes, obs_table(minute_atoms(1, complete=False)), identity(),
                member_id="train-a", member_window=member_window(),
                source_manifest="fixture-source", fold_manifest="fixture-fold")
        first = histogram_for_training(
            sizes, obs_table(atoms), identity(), member_id="train-a",
            member_window=member_window(), source_manifest="fixture-source",
            fold_manifest="fixture-fold")
        with self.assertRaises(ContractError):
            histogram_for_training(
                sizes, obs_table(atoms), identity(), member_id="train-a",
                member_window=member_window(), source_manifest="fixture-source",
                fold_manifest="fixture-fold", extra_complete_reports=(first["report"],))
        with self.assertRaises(ContractError):
            histogram_for_training(
                sizes, obs_table(atoms), identity(), member_id="train-a",
                member_window=member_window(), source_manifest="fixture-source",
                fold_manifest="fixture-fold",
                excluded_members=({"member_id": "train-a", "reason": "duplicate"},))


if __name__ == "__main__":
    unittest.main()
