"""Independent literal cases for the M02 adaptive/soft cohort consumer."""
from fractions import Fraction
import unittest

import pyarrow as pa
import pyarrow.compute as pc

from trading_research.errors import ContractError, IntegrityError
from trading_research.foundations.time import MINUTE, NS
from trading_research.measurements.cvd import CohortChannel, CohortDefinition
from trading_research.research.auction_flow_cohorts import CohortWindow
from trading_research.research.auction_flow_adaptive_cohort_measurements import (
    ADAPTIVE_RECIPES,
    AGGREGATION_UNIT,
    LATENCY_NS,
    SOFT_KNOTS,
    SOURCE_LATENCY_NS,
    VERSION,
    build_cohort_tables,
    compose_cohort_records,
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
CONTRACT_B = "NQ:NQM0:1:0:1000"
MANIFEST = {"source_collection": SOURCE_COLLECTION, "root": "NQ"}


def identity(*, start=BASE, end=None, root="NQ", key=SOURCE_KEY, collection=SOURCE_COLLECTION):
    return {
        "root": root,
        "source_path": SOURCE_PATH,
        "source_metadata_sha256": SOURCE_META,
        "source_variant": SOURCE_VARIANT,
        "acquired_event_start_ns": start,
        "acquired_event_end_ns": start + 86400 * NS if end is None else end,
        "source_key": key,
        "source_collection": collection,
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
            presence=True, prints=0, volume=0, known_at=None, flow=None, source=None,
            coordinate=None):
    return {
        "root": "NQ",
        "source_path": SOURCE_PATH,
        "source_metadata_sha256": SOURCE_META,
        "source_variant": SOURCE_VARIANT,
        "instrument_id": instrument_id,
        "contract_key": contract_key,
        "event_start_ns": start,
        "event_end_ns": end,
        "known_at_ns": end + LATENCY if known_at is None else known_at,
        "source_coverage_complete": complete if source is None else source,
        "coordinate_complete": complete if coordinate is None else coordinate,
        "flow_history_complete": complete if flow is None else flow,
        "empty_observed_window": empty,
        "source_instrument_presence": presence,
        "prints": prints,
        "volume": volume,
    }


def obs_table(rows):
    names = (
        "root", "source_path", "source_metadata_sha256", "source_variant",
        "instrument_id", "contract_key", "event_start_ns", "event_end_ns", "known_at_ns",
        "source_coverage_complete", "coordinate_complete", "flow_history_complete",
        "empty_observed_window", "source_instrument_presence", "prints", "volume",
    )
    return pa.table({name: [row[name] for row in rows] for name in names})


def minute_atoms(count, *, start=BASE, instrument_id=1, empty=False, complete=True,
                 contract_key=CONTRACT, presence=True):
    return [
        obs_row(start=start + i * MINUTE, end=start + (i + 1) * MINUTE,
                instrument_id=instrument_id, empty=empty, complete=complete,
                contract_key=contract_key, presence=presence)
        for i in range(count)
    ]


def apply_trade_counts(atoms, groups):
    prints = {}
    volume = {}
    for instrument_id, specs in groups:
        for item in specs:
            at, size = item[0], item[1]
            start = at - (at % MINUTE)
            key = (instrument_id, start)
            prints[key] = prints.get(key, 0) + 1
            volume[key] = volume.get(key, 0) + size
    out = []
    for atom in atoms:
        row = dict(atom)
        key = (row["instrument_id"], row["event_start_ns"])
        row["prints"] = prints.get(key, 0)
        row["volume"] = volume.get(key, 0)
        if row["prints"]:
            row["empty_observed_window"] = False
        out.append(row)
    return out


def member_window(*, start=BASE, end=BASE + MINUTE, published=None, complete=True):
    published_at = end + LATENCY if published is None else published
    return {"start": start, "end": end, "published_at": published_at, "history_complete": complete}


def records(table, **equals):
    filtered = table
    for name, value in equals.items():
        if value is None:
            filtered = filtered.filter(pc.is_null(filtered[name]))
        else:
            filtered = filtered.filter(pc.equal(filtered[name], value))
    return filtered.to_pylist()


def frac(row, name):
    num, den = row[f"{name}_numerator"], row[f"{name}_denominator"]
    num_text, den_text = row.get(f"{name}_numerator_text"), row.get(f"{name}_denominator_text")
    if num_text:
        num = int(num_text)
    if den_text:
        den = int(den_text)
    if num is None:
        return None
    return Fraction(num, den)


def build(specs, atoms, *, inst=1, definitions=None, cut_start=None, cut_end=None, key=SOURCE_KEY):
    if definitions is None:
        definitions = frozen_fixed_definitions()
    atoms = apply_trade_counts(atoms, [(inst, specs)])
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


def adaptive_plan(*, available=BASE, lower=5, upper=6):
    definition = CohortDefinition(
        "equal_count_quartiles", AGGREGATION_UNIT,
        (CohortChannel("bin:0", 1, upper), CohortChannel("bin:1", upper, None)),
        origin="fitted", available_at=available, fit_recipe_id="literal-adaptive-bundle")
    return {
        "equal_count_quartiles": {
            "name": "equal_count_quartiles", "kind": "adaptive", "definition": definition,
            "unavailable": None, "partition": True, "family_occupancy_only": False,
            "fit_evidence_identity": "literal-adaptive-bundle",
            "train_end": available, "available_at": available,
        }
    }


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
        specs = ((BASE + 1, 1, 1, 0), (BASE + 2, 2, -1, 1), (BASE + 3, 3, 1, 2),
                 (BASE + 4, 4, 1, 3))
        atoms = apply_trade_counts(minute_atoms(1, empty=False), [(1, specs)])
        hist = histogram_for_training(
            trades(specs), obs_table(atoms), identity(),
            member_id="train-a", member_window=member_window(),
            source_manifest=MANIFEST, fold_manifest="fixture-fold")
        fitted = fit_definitions(
            hist, train_end=BASE + 2 * 60 * MINUTE, available_at=BASE + 2 * 60 * MINUTE,
            member_identities=("train-a",), member_windows={"train-a": member_window()},
            source_collection=SOURCE_COLLECTION, root="NQ")
        evidence = serialize_fit_evidence(fitted["fits"]["equal_count_quartiles"])
        self.assertEqual(evidence, serialize_fit_evidence(fitted["fits"]["equal_count_quartiles"]))
        self.assertFalse(evidence["admitted_for_serving"])
        self.assertEqual(evidence["publication_status"], "unpublished")
        self.assertEqual(fitted["version"], VERSION)
        self.assertEqual(fitted["source_collection"], SOURCE_COLLECTION)
        self.assertEqual(fitted["root"], "NQ")
        self.assertEqual(fitted["definitions"]["equal_count_quartiles"]["source_collection"],
                         SOURCE_COLLECTION)


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
        self.assertEqual(row["known_at_ns"], BASE + MINUTE + LATENCY)
        self.assertEqual(row["scenario_latency_ns"], LATENCY)
        self.assertEqual(row["observation_known_at_ns"], BASE + MINUTE + LATENCY)
        self.assertEqual(built["validation"]["trades_reconciled"], 3)
        self.assertEqual(built["validation"]["eligible_trades"], 3)
        self.assertEqual(BASE % (5 * MINUTE), 0)
        self.assertEqual(atoms[0]["event_start_ns"] % MINUTE, 0)

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
        atoms = apply_trade_counts(
            minute_atoms(15, instrument_id=1) + minute_atoms(15, instrument_id=2),
            [(1, specs_a), (2, specs_b)])
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
        self.assertEqual(built["validation"]["trades_reconciled"], 2)

    def test_empty_observed_versus_missing(self):
        atoms = [
            obs_row(start=BASE, end=BASE + MINUTE, empty=True, prints=0, volume=0),
            obs_row(start=BASE + MINUTE, end=BASE + 2 * MINUTE, empty=False, prints=1, volume=4),
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
        self.assertIsNone(missing["prints"])
        self.assertIsNone(missing["volume"])
        incomplete = records(
            built["formations"], definition_name="fixed_all", channel_id="all",
            formation_minutes=5, cut_ns=BASE + 5 * MINUTE)[0]
        self.assertTrue(incomplete["missing_window"])
        self.assertTrue(incomplete["partial_window"])
        self.assertEqual(incomplete["event_start_ns"], BASE)
        self.assertEqual(incomplete["event_end_ns"], BASE + 5 * MINUTE)
        self.assertIsNone(frac(incomplete, "close"))
        self.assertIsNone(incomplete["prints"])
        self.assertIsNone(incomplete["volume"])
        self.assertFalse(incomplete["empty_observed_window"])

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
                "fit_evidence_identity": "unpublished-fit-a",
                "train_end": available, "available_at": available,
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
        self.assertIsNone(frac(early, "close"))
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
        counted = apply_trade_counts(atoms, [(1, first + third)])
        left = build_cohort_tables(
            table, obs_table(counted), frozen_fixed_definitions(), identity(),
            BASE + 15 * MINUTE, BASE + 20 * MINUTE, economic_date="2020-01-01")
        right = build_cohort_tables(
            split, obs_table(counted), frozen_fixed_definitions(), identity(),
            BASE + 15 * MINUTE, BASE + 20 * MINUTE, economic_date="2020-01-01")
        self.assertEqual(left["minutes"].to_pydict(), right["minutes"].to_pydict())
        self.assertEqual(left["formations"].to_pydict(), right["formations"].to_pydict())

    def test_composed_15min_matches_literal_whole_window(self):
        specs = (
            (BASE + 1, 5, 1, 0),
            (BASE + MINUTE + 1, 95, -1, 1),
            (BASE + 2 * MINUTE + 1, 10, 1, 2),
            (BASE + 3 * MINUTE + 1, 29, -1, 3),
            (BASE + 4 * MINUTE + 1, 30, 1, 4),
            (BASE + 5 * MINUTE + 1, 60, -1, 5),
            (BASE + 6 * MINUTE + 1, 75, 1, 6),
            (BASE + 7 * MINUTE + 1, 100, -1, 7),
            (BASE + 8 * MINUTE + 1, 250, 1, 8),
        )
        atoms = minute_atoms(15)
        plan = {**frozen_fixed_definitions(), **adaptive_plan(available=BASE, lower=1, upper=6)}
        five_specs = ((BASE + 1, 5, 1, 0), (BASE + MINUTE + 1, 95, -1, 1))
        five_built = build(five_specs, atoms, definitions=plan)
        five_lot = records(
            five_built["formations"], definition_name="equal_count_quartiles", channel_id="bin:0",
            formation_minutes=15, cut_ns=BASE + 15 * MINUTE)[0]
        self.assertEqual(frac(five_lot, "volume_occupancy"), F(5, 100))
        self.assertNotEqual(frac(five_lot, "volume_occupancy"), 1)
        self.assertEqual(five_lot["volume"], 100)
        self.assertEqual(frac(five_lot, "volume"), 5)
        built = build(specs, atoms, definitions=plan)
        table = trades(specs)
        names = (
            ("fixed_all", None),
            ("ny_ge100", None),
            ("london_ge75", None),
            ("inclusive30_through60", None),
            ("soft_piecewise_linear_knots", None),
            ("equal_count_quartiles", None),
        )
        for definition_name, _ in names:
            window = CohortWindow(
                definition=plan[definition_name]["definition"],
                instrument_id=1, start_ns=BASE, end_ns=BASE + 15 * MINUTE,
                latency_ns=LATENCY)
            window.add(table)
            literal = window.record(source_coverage_complete=True, coordinate_complete=True)
            for channel in literal["channels"]:
                composed = records(
                    built["formations"], definition_name=definition_name,
                    channel_id=channel["channel_id"], formation_minutes=15,
                    cut_ns=BASE + 15 * MINUTE)[0]
                self.assertEqual(frac(composed, "open"), channel["open"])
                self.assertEqual(frac(composed, "close"), channel["close"])
                self.assertEqual(frac(composed, "high"), channel["high"])
                self.assertEqual(frac(composed, "low"), channel["low"])
                self.assertEqual(composed["high_at_ns"], channel["high_at_ns"])
                self.assertEqual(composed["low_at_ns"], channel["low_at_ns"])
                self.assertEqual(composed["high_source_order"], channel["high_source_order"])
                self.assertEqual(composed["low_source_order"], channel["low_source_order"])
                self.assertEqual(composed["prints"], literal["prints"])
                self.assertEqual(composed["volume"], literal["volume"])
                self.assertEqual(frac(composed, "volume"), channel["volume"])
                self.assertEqual(frac(composed, "count_occupancy"), channel["count_occupancy"])
                self.assertEqual(frac(composed, "volume_occupancy"), channel["volume_occupancy"])
                self.assertEqual(frac(composed, "true_signed_lower"), channel["true_signed_lower"])
                self.assertEqual(frac(composed, "true_signed_upper"), channel["true_signed_upper"])
                if channel["channel_id"] != "all":
                    self.assertNotEqual(frac(composed, "volume_occupancy"), 1)
        minutes = [
            records(built["minutes"], definition_name="fixed_all", channel_id="all",
                    event_start_ns=BASE + i * MINUTE)[0]
            for i in range(3)
        ]
        left = compose_cohort_records(
            _row_to_record(minutes[0]), compose_cohort_records(
                _row_to_record(minutes[1]), _row_to_record(minutes[2])))
        right = compose_cohort_records(
            compose_cohort_records(_row_to_record(minutes[0]), _row_to_record(minutes[1])),
            _row_to_record(minutes[2]))
        self.assertEqual(left["close"], right["close"])
        self.assertEqual(left["high"], right["high"])
        self.assertEqual(left["low"], right["low"])
        self.assertEqual(left["window_volume"], right["window_volume"])
        self.assertEqual(left["volume_occupancy"], right["volume_occupancy"])

    def test_invalid_source_aggregation_is_rejected(self):
        specs = ((BASE + 1, 2, 1, 0), (BASE + 2, 3, -1, 1))
        mixed = make_trade_table([
            trade(BASE + 1, 2, 1, 0, key="one"),
            trade(BASE + 2, 3, -1, 1, key="two"),
        ])
        with self.assertRaises(IntegrityError):
            build_cohort_tables(
                mixed, obs_table(apply_trade_counts(minute_atoms(15), [(1, specs)])),
                frozen_fixed_definitions(),
                identity(), BASE + 15 * MINUTE, BASE + 20 * MINUTE)
        with self.assertRaises(IntegrityError):
            build_cohort_tables(
                trades(specs, key="other"),
                obs_table(apply_trade_counts(minute_atoms(15), [(1, specs)])),
                frozen_fixed_definitions(), identity(), BASE + 15 * MINUTE, BASE + 20 * MINUTE)

    def test_same_instrument_contract_switch_nulls_path(self):
        specs = ((BASE + 1, 10, 1, 0), (BASE + MINUTE + 1, 20, -1, 1))
        atoms = apply_trade_counts([
            obs_row(start=BASE, end=BASE + MINUTE, contract_key=CONTRACT, prints=1, volume=10),
            obs_row(start=BASE + MINUTE, end=BASE + 2 * MINUTE, contract_key=CONTRACT_B,
                    prints=1, volume=20),
            *[obs_row(start=BASE + i * MINUTE, end=BASE + (i + 1) * MINUTE)
              for i in range(2, 15)],
        ], [(1, specs)])
        built = build_cohort_tables(
            trades(specs), obs_table(atoms), frozen_fixed_definitions(), identity(),
            BASE + 5 * MINUTE, BASE + 10 * MINUTE, economic_date="2020-01-01")
        composed = records(
            built["formations"], definition_name="fixed_all", channel_id="all",
            formation_minutes=5, cut_ns=BASE + 5 * MINUTE)[0]
        self.assertFalse(composed["coordinate_complete"])
        self.assertEqual(composed["composition_reason"], "raw_contract_switch")
        self.assertIsNone(composed["contract_key"])
        self.assertIsNone(frac(composed, "close"))
        self.assertIsNone(frac(composed, "high"))
        self.assertEqual(composed["volume"], 30)
        self.assertEqual(composed["prints"], 2)

    def test_compose_rejects_source_identity_mismatch(self):
        built = build(((BASE + 1, 10, 1, 0),), minute_atoms(15))
        left = _row_to_record(records(
            built["minutes"], definition_name="fixed_all", channel_id="all",
            event_start_ns=BASE)[0])
        right = dict(left)
        right["event_start_ns"] = left["event_end_ns"]
        right["event_end_ns"] = left["event_end_ns"] + MINUTE
        right["source_key"] = "other"
        with self.assertRaises(IntegrityError):
            compose_cohort_records(left, right)

    def test_flow_incomplete_nulls_true_bounds_and_late_observation_clock(self):
        late = BASE + MINUTE + 2 * LATENCY
        atoms = [
            obs_row(start=BASE, end=BASE + MINUTE, prints=1, volume=7, flow=False,
                    source=True, coordinate=True, known_at=late),
            *[obs_row(start=BASE + i * MINUTE, end=BASE + (i + 1) * MINUTE)
              for i in range(1, 15)],
        ]
        built = build(((BASE + 1, 7, 1, 0),), atoms)
        row = records(built["minutes"], definition_name="fixed_all", channel_id="all",
                      event_start_ns=BASE)[0]
        self.assertFalse(row["flow_history_complete"])
        self.assertTrue(row["source_coverage_complete"])
        self.assertIsNone(frac(row, "true_signed_lower"))
        self.assertIsNone(frac(row, "true_signed_upper"))
        self.assertEqual(frac(row, "close"), 7)
        self.assertEqual(row["observation_known_at_ns"], late)
        self.assertEqual(row["known_at_ns"], late)
        self.assertGreater(row["known_at_ns"], row["event_end_ns"] + LATENCY)

    def test_unsorted_and_foreign_instrument_are_rejected(self):
        specs = ((BASE + 2, 2, 1, 0), (BASE + 1, 3, -1, 1))
        atoms = apply_trade_counts(minute_atoms(15), [(1, ((BASE + 1, 3, -1, 1), (BASE + 2, 2, 1, 0)))])
        with self.assertRaises(IntegrityError):
            build_cohort_tables(
                trades(specs), obs_table(atoms), frozen_fixed_definitions(), identity(),
                BASE + 15 * MINUTE, BASE + 20 * MINUTE)
        foreign = trades(((BASE + 1, 2, 1, 0),), instrument_id=9)
        with self.assertRaises(IntegrityError):
            build_cohort_tables(
                foreign, obs_table(apply_trade_counts(minute_atoms(15), [(1, ())])),
                frozen_fixed_definitions(), identity(),
                BASE + 15 * MINUTE, BASE + 20 * MINUTE)

    def test_foreign_fit_binding_and_bare_fitted_definition_rejected(self):
        specs = ((BASE + 1, 2, 1, 0),)
        atoms = apply_trade_counts(minute_atoms(15), [(1, specs)])
        fitted = fit_definitions(
            histogram_for_training(
                trades(specs), obs_table(apply_trade_counts(minute_atoms(1), [(1, specs)])),
                identity(), member_id="train-a", member_window=member_window(),
                source_manifest=MANIFEST, fold_manifest="fixture-fold"),
            train_end=BASE + MINUTE + LATENCY, available_at=BASE + MINUTE + LATENCY,
            member_identities=("train-a",), member_windows={"train-a": member_window()},
            source_collection=SOURCE_COLLECTION, root="NQ")
        with self.assertRaises(IntegrityError):
            build_cohort_tables(
                trades(specs), obs_table(atoms), fitted,
                identity(collection="other-collection"),
                BASE + 15 * MINUTE, BASE + 20 * MINUTE)
        bare = CohortDefinition(
            "equal_count_quartiles", AGGREGATION_UNIT,
            (CohortChannel("bin:0", 1, 3), CohortChannel("bin:1", 3, None)),
            origin="fitted", available_at=BASE, fit_recipe_id="bare-vector")
        with self.assertRaises(ContractError):
            build_cohort_tables(
                trades(specs), obs_table(atoms), {"equal_count_quartiles": bare},
                identity(), BASE + 15 * MINUTE, BASE + 20 * MINUTE)

    def test_scientific_join_zero_250_1000_crossfold_futurefit(self):
        built = build(((BASE + 1, 2, 1, 0),), minute_atoms(15))
        feature = records(built["formations"], definition_name="fixed_all", channel_id="all",
                          formation_minutes=15)[0]
        self.assertTrue(feature["prefix_complete"])
        self.assertTrue(feature["atoms_complete"])
        self.assertGreaterEqual(feature["known_at_ns"], feature["event_end_ns"] + LATENCY)
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
            "source_key": feature["source_key"],
            "source_collection": feature["source_collection"],
            "known_at_ns": feature["cut_ns"] + 5 * MINUTE,
        }
        mid = scientific_join_eligibility(feature, {**label, "latency_ns": LATENCY})
        self.assertTrue(mid["eligible"])
        self.assertTrue(mid["actual_receipt_eligible"])
        self.assertEqual(mid["same_source_identity"], True)
        self.assertEqual(mid["same_instrument"], True)
        self.assertEqual(mid["same_cut"], True)
        self.assertEqual(mid["latency_scenario_ns"], LATENCY)
        self.assertFalse(mid["synthetic_latency_scenario"])
        self.assertEqual(tuple(LATENCY_NS), (250_000_000, 0, 1_000_000_000))
        zero = scientific_join_eligibility(feature, {**label, "latency_ns": 0})
        self.assertTrue(zero["eligible"])
        self.assertFalse(zero["actual_receipt_eligible"])
        self.assertTrue(zero["synthetic_latency_scenario"])
        late = scientific_join_eligibility(feature, {**label, "latency_ns": 1_000_000_000})
        self.assertTrue(late["eligible"])
        self.assertTrue(late["actual_receipt_eligible"])
        self.assertTrue(late["synthetic_latency_scenario"])
        cross = scientific_join_eligibility(
            feature, {**label, "latency_ns": LATENCY, "source_collection": "other-fold"})
        self.assertFalse(cross["eligible"])
        self.assertEqual(cross["reason"], "source_identity_mismatch")
        future = dict(feature)
        future["definition_available_at"] = feature["event_start_ns"] + MINUTE
        blocked = scientific_join_eligibility(future, {**label, "latency_ns": LATENCY})
        self.assertFalse(blocked["eligible"])
        self.assertEqual(blocked["reason"], "future_definition_availability")
        missing = dict(feature)
        missing["missing_window"] = True
        self.assertFalse(scientific_join_eligibility(missing, {**label, "latency_ns": LATENCY})["eligible"])


def _row_to_record(row):
    definition = frozen_fixed_definitions()["fixed_all"]["definition"]
    return {
        "channel_id": row["channel_id"],
        "channel_role": row["channel_role"],
        "open": frac(row, "open"),
        "high": frac(row, "high"),
        "low": frac(row, "low"),
        "close": frac(row, "close"),
        "high_at_ns": row["high_at_ns"],
        "low_at_ns": row["low_at_ns"],
        "high_source_order": row["high_source_order"],
        "low_source_order": row["low_source_order"],
        "high_origin": row["high_origin"],
        "low_origin": row["low_origin"],
        "buy": frac(row, "buy"),
        "sell": frac(row, "sell"),
        "unknown": frac(row, "unknown"),
        "volume": frac(row, "volume"),
        "signed": frac(row, "signed"),
        "weighted_prints": frac(row, "weighted_prints"),
        "contributing_prints": row["contributing_prints"],
        "prints": row["prints"],
        "window_volume": row["volume"],
        "count_occupancy": frac(row, "count_occupancy"),
        "volume_occupancy": frac(row, "volume_occupancy"),
        "observed_signed_lower": frac(row, "observed_signed_lower"),
        "observed_signed_upper": frac(row, "observed_signed_upper"),
        "true_signed_lower": frac(row, "true_signed_lower"),
        "true_signed_upper": frac(row, "true_signed_upper"),
        "empty_observed_channel": row["empty_observed_channel"],
        "empty_observed_window": row["empty_observed_window"],
        "source_coverage_complete": row["source_coverage_complete"],
        "coordinate_complete": row["coordinate_complete"],
        "flow_history_complete": row["flow_history_complete"],
        "atoms_complete": row["atoms_complete"],
        "prefix_complete": row["prefix_complete"],
        "missing_window": row["missing_window"],
        "partial_window": row["partial_window"],
        "unavailable": row["unavailable"],
        "unavailable_reason": row["unavailable_reason"],
        "composition_reason": row.get("composition_reason"),
        "event_start_ns": row["event_start_ns"],
        "event_end_ns": row["event_end_ns"],
        "contract_key": row["contract_key"],
        "instrument_id": row["instrument_id"],
        "source_key": row["source_key"],
        "source_collection": row["source_collection"],
        "definition_name": row["definition_name"],
        "definition": definition,
        "plan": frozen_fixed_definitions()["fixed_all"],
        "observation_known_at_ns": row["observation_known_at_ns"],
    }


class TrainingFitTests(unittest.TestCase):
    def histogram(self, sizes, *, member_id="train-a", complete=True, window=None, manifest=MANIFEST):
        specs = tuple((BASE + index + 1, size, 1, index) for index, size in enumerate(sizes))
        atoms = apply_trade_counts(
            minute_atoms(1, empty=not sizes, complete=complete), [(1, specs)])
        return histogram_for_training(
            trades(specs), obs_table(atoms), identity(), member_id=member_id,
            member_window=window or member_window(),
            source_manifest=manifest, fold_manifest="fixture-fold")

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
        self.assertEqual(fitted["definitions"]["equal_count_quartiles"]["histogram_identity"],
                         hist["histogram_identity"])

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

    def test_empty_table_conserves_zero_and_does_not_invent_mass(self):
        atoms = minute_atoms(1, empty=True)
        hist = histogram_for_training(
            make_trade_table([]), obs_table(atoms), identity(),
            member_id="empty-a", member_window=member_window(),
            source_manifest=MANIFEST, fold_manifest="fixture-fold")
        self.assertEqual(hist["report"]["prints"], 0)
        self.assertEqual(hist["report"]["contracts"], 0)
        self.assertEqual(hist["report"]["histogram"], ())
        self.assertFalse(hist["coverage_inferred_from_prints"])
        fitted = fit_definitions(
            hist, train_end=BASE + MINUTE, available_at=BASE + MINUTE,
            member_identities=("empty-a",), member_windows={"empty-a": member_window()})
        self.assertEqual(fitted["unavailable"]["equal_count_quartiles"],
                         "unavailable_empty_or_missing_eligible_training")
        self.assertIsNone(fitted["definitions"]["equal_count_quartiles"]["definition"])
        self.assertIsNotNone(fitted["definitions"]["fixed_all"]["definition"])

    def test_observation_print_conservation_and_future_rows_raise(self):
        specs = ((BASE + 1, 2, 1, 0),)
        atoms = [obs_row(start=BASE, end=BASE + MINUTE, prints=99, volume=2)]
        with self.assertRaises(IntegrityError):
            histogram_for_training(
                trades(specs), obs_table(atoms), identity(), member_id="train-a",
                member_window=member_window(), source_manifest=MANIFEST,
                fold_manifest="fixture-fold")
        future = ((BASE + 2 * MINUTE + 1, 2, 1, 0),)
        with self.assertRaises(ContractError):
            histogram_for_training(
                trades(future),
                obs_table(apply_trade_counts(minute_atoms(1), [(1, specs)])),
                identity(), member_id="train-a", member_window=member_window(),
                source_manifest=MANIFEST, fold_manifest="fixture-fold")
        with self.assertRaises(ContractError):
            histogram_for_training(
                trades(specs),
                obs_table(apply_trade_counts(minute_atoms(1), [(1, specs)])),
                identity(), member_id="train-a", member_window=member_window(),
                source_manifest=None, fold_manifest="fixture-fold")

    def test_training_member_future_duplicate_and_incomplete_exclusion(self):
        sizes = trades(((BASE + 1, 2, 1, 0),))
        atoms = apply_trade_counts(minute_atoms(1), [(1, ((BASE + 1, 2, 1, 0),))])
        with self.assertRaises(ContractError):
            histogram_for_training(
                sizes, obs_table(atoms), identity(), member_id="train-a",
                member_window=member_window(end=BASE + 10 * 60 * MINUTE),
                source_manifest=MANIFEST, fold_manifest="fixture-fold",
                train_end=BASE + MINUTE)
        incomplete = histogram_for_training(
            sizes, obs_table(atoms), identity(), member_id="train-a",
            member_window=member_window(complete=False),
            source_manifest=MANIFEST, fold_manifest="fixture-fold")
        self.assertIsNone(incomplete["report"])
        self.assertEqual(incomplete["excluded_members"][0]["member_id"], "train-a")
        self.assertEqual(incomplete["excluded_members"][0]["reason"], "history_incomplete")
        flagged = histogram_for_training(
            sizes, obs_table(apply_trade_counts(minute_atoms(1, complete=False),
                                                [(1, ((BASE + 1, 2, 1, 0),))])),
            identity(), member_id="train-a", member_window=member_window(),
            source_manifest=MANIFEST, fold_manifest="fixture-fold")
        self.assertIsNone(flagged["report"])
        self.assertEqual(flagged["excluded_members"][0]["reason"], "source_coverage_incomplete")
        with self.assertRaises(ContractError):
            histogram_for_training(
                sizes, obs_table(atoms), identity(), member_id="train-a",
                member_window=member_window(), source_manifest=MANIFEST,
                fold_manifest="fixture-fold",
                excluded_members=({"member_id": "train-a", "reason": "duplicate"},))
        with self.assertRaises(ContractError):
            histogram_for_training(
                sizes, obs_table(atoms), identity(), member_id="train-a",
                member_window=member_window(), source_manifest=MANIFEST,
                fold_manifest="fixture-fold",
                excluded_members=({"member_id": "other", "reason": "x"},
                                  {"member_id": "other", "reason": "y"}))
        mismatched = dict(MANIFEST)
        mismatched["source_collection"] = "other-collection"
        hist = self.histogram([2], manifest=mismatched)
        with self.assertRaises(IntegrityError):
            fit_definitions(
                hist, train_end=BASE + MINUTE, available_at=BASE + MINUTE,
                member_identities=("train-a",), member_windows={"train-a": member_window()},
                source_collection=SOURCE_COLLECTION, root="NQ")
        future_windows = {"train-a": member_window(end=BASE + 10 * MINUTE)}
        with self.assertRaises(ContractError):
            fit_definitions(
                self.histogram([2]), train_end=BASE + MINUTE, available_at=BASE + MINUTE,
                member_identities=("train-a",), member_windows=future_windows,
                source_collection=SOURCE_COLLECTION, root="NQ")

    def test_known_absence_does_not_require_inactive_contract(self):
        specs = ((BASE + 1, 3, 1, 0),)
        present = apply_trade_counts(minute_atoms(1, instrument_id=1), [(1, specs)])
        absent = [obs_row(start=BASE, end=BASE + MINUTE, instrument_id=2, empty=True,
                          presence=False, prints=0, volume=0)]
        hist = histogram_for_training(
            trades(specs, instrument_id=1), obs_table(present + absent), identity(),
            member_id="train-a", member_window=member_window(),
            source_manifest=MANIFEST, fold_manifest="fixture-fold")
        self.assertEqual(hist["report"]["prints"], 1)
        self.assertEqual(hist["report"]["contracts"], 3)
        self.assertIn(1, hist["included_instrument_ids"])
        self.assertNotIn(2, hist["included_instrument_ids"])


if __name__ == "__main__":
    unittest.main()
