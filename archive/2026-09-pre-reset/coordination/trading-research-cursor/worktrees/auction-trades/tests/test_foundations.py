from dataclasses import replace
from decimal import Decimal, localcontext
from fractions import Fraction
import unittest

from trading_research.errors import ContractError, DependencyUnavailable
from trading_research.foundations.availability import AvailabilityIndex, JoinPolicy, Observation, backward_reference
from trading_research.foundations.contracts import Band, Capability, Forecast, Geometry, InstrumentKey, MarketObject, Target
from trading_research.foundations.graph import Graph, InputPort, Port, PublishedVersion
from trading_research.foundations.instruments import InstrumentDefinition, InstrumentRegistry
from trading_research.foundations.time import AvailabilityBasis, Clocks, derived_clocks
from trading_research.foundations.units import NQ_REFERENCE, Quantity, Ticks, Unit, mini_equivalents


def clocks(at, *, event=None, version="v1"):
    return Clocks(at if event is None else event, at, version, AvailabilityBasis.RECEIVED, received_at=at)


def target(*, at=10, end=30, caps=frozenset({Capability.EXCURSIONS}), geometry=None):
    return Target("range", "v1", "NQ", at, end, "full-trade-tape", "all-eligible-days", Unit.TICKS,
                  caps, geometry_id=geometry)


class ArithmeticAndClockTests(unittest.TestCase):
    def test_ticks_use_exact_ratio_not_decimal_context_rounding(self):
        with localcontext() as context:
            context.prec = 3
            self.assertEqual(NQ_REFERENCE.ticks(Decimal("20000.25")), Ticks(80001))
            self.assertEqual(NQ_REFERENCE.price(Ticks(80001)), Decimal("20000.25"))
            self.assertEqual(NQ_REFERENCE.pnl(Ticks(0), Ticks(80001), side=1).value, Decimal("400005.00"))
            self.assertEqual((Quantity(Decimal("20000.25"), Unit.USD) + Quantity(Decimal("0.125"), Unit.USD)).value,
                             Decimal("20000.375"))
            with self.assertRaises(ContractError):
                NQ_REFERENCE.ticks(Decimal("20000.251"))
        self.assertEqual(NQ_REFERENCE.pnl(Ticks(80000), Ticks(80001), side=1).value, Decimal(5))
        self.assertEqual(NQ_REFERENCE.pnl(Ticks(80000), Ticks(79996), side=-1).value, Decimal(20))
        with self.assertRaises(ContractError):
            NQ_REFERENCE.pnl(Ticks(0), Ticks(1), side=1, contracts=2)

    def test_information_mini_equivalent_is_not_order_quantity(self):
        self.assertEqual(mini_equivalents(Decimal(50), Decimal(40), NQ_REFERENCE), Fraction(1, 16))
        with self.assertRaises(ContractError):
            Quantity(Decimal(1), Unit.USD) + Quantity(Decimal(1), Unit.CONTRACTS)
        with self.assertRaises(ContractError):
            Ticks(1.5)

    def test_actual_compute_is_not_charged_twice_and_confirmation_is_not_backdated(self):
        output = derived_clocks([clocks(10), clocks(12)], source_version="derived", actual_completion_at=20,
                                confirmation_known_at=25)
        self.assertEqual((output.known_at, output.computed_at), (25, 20))
        with self.assertRaises(ContractError):
            derived_clocks([clocks(10)], source_version="derived", actual_completion_at=20,
                           simulated_start_at=10, simulated_duration_ns=10)
        assumed = derived_clocks([clocks(12)], source_version="d", simulated_start_at=10,
                                 simulated_duration_ns=5, assumption_id="compute-pilot-5ns")
        self.assertEqual(assumed.known_at, 17)
        self.assertIsNone(assumed.received_at)
        self.assertIsNone(assumed.computed_at)

    def test_provider_receipt_is_distinct_and_missing_strategy_receipt_requires_assumption(self):
        with self.assertRaises(ContractError):
            Clocks(10, 12, "native", AvailabilityBasis.RECEIVED, provider_received_at=12)
        c = Clocks(15, 12, "native", AvailabilityBasis.ASSUMED, provider_received_at=11,
                   clock_uncertainty_ns=5, assumption_id="provider-plus-1ns")
        self.assertIsNone(c.received_at)
        self.assertEqual(c.clock_uncertainty_ns, 5)
        with self.assertRaises(ContractError):
            replace(c, assumption_id=None)


class AvailabilityTests(unittest.TestCase):
    def test_future_suffix_correction_and_restart_preserve_past_cut(self):
        old = Observation("OI", "oi-v0", 0, clocks(10), b"100", 5, session="day")
        revision = Observation("OI", "oi-v1", 1, clocks(20), b"110", 5, session="day")
        index = AvailabilityIndex()
        index.append(old)
        index.append(revision)
        policy = JoinPolicy(30, "day")
        for actual in (index, AvailabilityIndex.restore(index.checkpoint())):
            self.assertEqual(actual.asof("OI", cut=15, policy=policy), old)
            self.assertEqual(actual.asof("OI", cut=20, policy=policy), revision)
        self.assertEqual(backward_reference([old], "OI", cut=15, policy=policy), old)
        index.append(old)
        self.assertEqual(len(index.checkpoint()), 2)
        with self.assertRaises(ContractError):
            index.append(replace(old, payload_json=b"999"))

    def test_stale_no_resurrection_and_late_older_observation(self):
        old = Observation("q", "q0", 0, clocks(5), b"1", 5)
        recent = Observation("q", "q1", 0, clocks(10), b"2", 10)
        late = Observation("q", "q-late", 1, clocks(12), b"3", 4)
        policy = JoinPolicy(5)
        self.assertEqual(backward_reference([old, recent, late], "q", cut=12, policy=policy), recent)
        invalid = replace(recent, id="q2", revision=1, clocks=clocks(13), eligible=False, reason="withdrawn")
        self.assertIsNone(backward_reference([old, recent, invalid], "q", cut=14, policy=policy))
        self.assertIsNone(backward_reference([recent], "q", cut=16, policy=policy))

    def test_nearest_future_join_and_ambiguous_source_priority_fail(self):
        a = Observation("q", "a", 0, clocks(12), b"1", 12)
        self.assertIsNone(backward_reference([a], "q", cut=11, policy=JoinPolicy(10)))
        with self.assertRaises(ContractError):
            backward_reference([a, replace(a, id="b", payload_json=b"2")], "q", cut=12, policy=JoinPolicy(10))


class GraphAndGeometryTests(unittest.TestCase):
    def test_capability_horizon_and_geometry_cannot_be_substituted(self):
        base = target()
        f = Forecast("f", base, clocks(12), b'{"q50":4}', "predictive", "m", "fold", None, (), ())
        f.require(base, frozenset({Capability.EXCURSIONS}), cut=15)
        with self.assertRaises(DependencyUnavailable):
            f.require(base, frozenset({Capability.FIRST_PASSAGE}), cut=15)
        with self.assertRaises(DependencyUnavailable):
            f.require(base, frozenset(), cut=30)
        with self.assertRaises(ContractError):
            f.require(replace(base, decision_at=15, horizon_end=35), frozenset(), cut=15)
        g = Geometry(Band(Fraction(0), Fraction(1)), Band(Fraction(0), Fraction(1)),
                     Fraction(2), Fraction(3), Fraction(4), "level-v1", "QQQ", "NQ")
        self.assertEqual(replace(g, estimation_uncertainty=Fraction(20)).target_geometry_id, g.target_geometry_id)
        self.assertNotEqual(replace(g, contact_region=Band(Fraction(-1), Fraction(2))).target_geometry_id, g.target_geometry_id)

    def test_confirmed_object_has_immutable_revision_and_no_backdating(self):
        key = InstrumentKey("db", "CME", "42", "NQU6", "NQ", "def1")
        geom = Geometry(Band(Fraction(0), Fraction(1)), Band(Fraction(0), Fraction(1)),
                        Fraction(0), Fraction(0), Fraction(0), "v1", "NQ", "NQ")
        obj = MarketObject("swing", 0, "pivot", "v1", key, geom, clocks(20), (), ("a", "b"),
                           10, 15, 20, "eligible", "unvisited", "candidate", ("support",))
        with self.assertRaises(ContractError):
            replace(obj, clocks=clocks(15))
        self.assertNotEqual(replace(obj, revision=1, supersedes=obj.version_id).version_id, obj.version_id)

    def test_current_cycle_invalid_but_declared_lagged_feedback_valid(self):
        a = Port("a", "F04", 0, "v1", frozenset({"x"}), (InputPort("b", "v1", frozenset({"x"})),))
        b = Port("b", "F04", 0, "v1", frozenset({"x"}), (InputPort("a", "v1", frozenset({"x"})),))
        with self.assertRaises(ContractError):
            Graph([a, b])
        a = replace(a, inputs=(replace(a.inputs[0], lag_ns=1, max_age_ns=10),))
        graph = Graph([a, b])
        self.assertEqual(graph.order, ("a", "b"))
        previous = PublishedVersion("b", "b-old", 9, clocks(9), (), "hash")
        self.assertEqual(graph.validate_inputs("a", {"b": previous}, cut=10), ("b-old",))
        with self.assertRaises(ContractError):
            graph.validate_inputs("a", {"b": replace(previous, decision_cut=10)}, cut=10)

    def test_field_invalidation_and_fitted_transitive_closure(self):
        source = Port("raw", "F01", 0, "data", frozenset({"price", "volume"}))
        scale = Port("scale", "V02", 1, "vector", frozenset({"z"}),
                     (InputPort("raw", "data", frozenset({"price"})),), learned=True)
        fixed = Port("fixed", "F11", 2, "vector", frozenset({"z"}),
                     (InputPort("scale", "vector", frozenset({"z"})),))
        model = Port("model", "C06", 3, "forecast", frozenset({"p"}),
                     (InputPort("fixed", "vector", frozenset({"z"})),), learned=True)
        graph = Graph([source, scale, fixed, model])
        self.assertEqual(graph.affected_by_fields("raw", frozenset({"volume"})), frozenset())
        self.assertEqual(graph.affected_by_fields("raw", frozenset({"price"})), frozenset({"scale", "fixed", "model"}))
        graph.validate_fit_order(["scale", "model"])
        with self.assertRaises(ContractError):
            graph.validate_fit_order(["model", "scale"])
        with self.assertRaises(ContractError):
            Graph([source, replace(scale, inputs=(replace(scale.inputs[0], required_capabilities=frozenset({Capability.TRAJECTORY})),))])

    def test_definition_revision_is_known_time_and_use_specific(self):
        registry = InstrumentRegistry()
        key = InstrumentKey("db", "CME", "42", "NQU6", "NQ", "def1")
        c = replace(clocks(10), valid_from=0, valid_until=100)
        raw = InstrumentDefinition(key, c, "unknown", None, None)
        registry.append(raw)
        fixed = InstrumentDefinition(replace(key, definition_version="def2"), replace(c, known_at=20, received_at=20),
                                     "future", Decimal(20), Decimal("0.25"))
        registry.append(fixed)
        early = registry.resolve(provider="db", venue="CME", instrument_id="42", valid_at=15, known_at=15)
        self.assertEqual(early, raw)
        self.assertTrue(early.eligibility("raw_flow")[0])
        self.assertFalse(early.eligibility("execution")[0])
        self.assertEqual(registry.resolve(provider="db", venue="CME", instrument_id="42", valid_at=15, known_at=20), fixed)
        self.assertEqual(fixed.futures_terms().tick_size, Decimal("0.25"))
