from dataclasses import replace
import unittest

from trading_research.errors import ContractError, DependencyUnavailable
from trading_research.foundations.graph import Graph, InputPort, Port
from trading_research.runtime.ports import Binding, reference_graph, validate_bindings


def add_edge(graph, source, consumer):
    p = graph.ports[source]
    edge = InputPort(source, p.schema, p.fields, p.unit, p.target_id, p.capabilities)
    return Graph([replace(node, inputs=(*node.inputs, edge)) if node.id == consumer else node for node in graph.ports.values()])


class ConcretePortTests(unittest.TestCase):
    def setUp(self):
        self.graph = reference_graph()

    def test_raw_precheck_normalization_semantic_quality_order_and_independent_sign(self):
        positions = {id:i for i, id in enumerate(self.graph.order)}
        pipeline = ["F01.RAW", "F06.RAW", "F05.NORMALIZED", "F06.SEMANTIC", "F07.ELIGIBLE"]
        self.assertEqual(sorted(pipeline, key=positions.get), pipeline)
        self.assertLess(positions["X02.BOOTSTRAP"], positions["O02.IV"])
        self.assertNotIn("O03.SIGN", self.graph.descendants(["O02.IV"]))
        self.assertNotIn("O15.RAW_FLOW", self.graph.descendants(["O04.SURFACE"]))
        self.assertNotIn("P10.EMERGENCY", self.graph.descendants(["O04.SURFACE"]))
        self.assertEqual(self.graph.ports["P10.EMERGENCY"].lane, "timer")

    def test_all_named_forbidden_feedback_paths_are_rejected(self):
        cases = [("C03", "C06"), ("G02.PATH", "C06"), ("X06", "C19"), ("O02.IV", "X02.BOOTSTRAP"),
                 ("G09.SELECT", "G01"), ("P01.INTENT", "G06"), ("O10.CHANGES", "C15.SCENARIO"),
                 ("O12.OBSERVED", "C15.SCENARIO"), ("X06", "C16.JOINT_STRESS"),
                 ("F05.NORMALIZED", "F06.RAW"), ("G06", "C22")]
        for source, consumer in cases:
            with self.subTest(source=source, consumer=consumer), self.assertRaises(ContractError):
                add_edge(self.graph, source, consumer)

    def test_observed_auction_and_topology_precede_separate_evolution_forecasts(self):
        inputs = lambda id: {e.source for e in self.graph.ports[id].inputs}
        self.assertIn("C07.STATE", inputs("C08.PROFILE_EVOLUTION"))
        self.assertNotIn("C07.TRANSITION", inputs("C08.PROFILE_EVOLUTION"))
        self.assertIn("O12.OBSERVED", inputs("O13.TOPOLOGY"))
        self.assertIn("O13.TOPOLOGY", inputs("O12.FIELD_EVOLUTION"))
        self.assertNotIn("O12.FIELD_EVOLUTION", inputs("O13.TOPOLOGY"))
        self.assertIn("O21.DECISION_SENSITIVITY", inputs("G09.SELECT"))
        self.assertNotIn("G01", self.graph.descendants(["O21.DECISION_SENSITIVITY"]))

    def test_component_declarations_are_not_executable_implementation_bindings(self):
        with self.assertRaises(ContractError):
            validate_bindings(self.graph, frozenset({"C19"}), ())
        binding = Binding("C19", "code", "definition", "params", "schema", None, None, "test-report")
        with self.assertRaises(DependencyUnavailable):
            validate_bindings(self.graph, frozenset({"C19"}), (binding,))
        binding = replace(binding, model_artifact="frozen-model", fit_lineage="OOF-lineage")
        with self.assertRaises(DependencyUnavailable):
            validate_bindings(self.graph, frozenset({"C19"}), (binding,))

    def test_raw_flow_can_bind_without_iv_or_optional_es_and_objects_without_response(self):
        enabled = {"O15.RAW_FLOW"}
        while True:
            expanded = enabled | {e.source for id in enabled for e in self.graph.ports[id].inputs if not e.optional}
            if expanded == enabled:
                break
            enabled = expanded
        self.assertNotIn("O02.IV", enabled)
        self.assertNotIn("X01.ALIGN", enabled)
        bindings = tuple(Binding(id, "code-fixture", "definition", "params", "schema", None, None, "test-report") for id in enabled)
        self.assertTrue(validate_bindings(self.graph, frozenset(enabled), bindings))
        self.assertFalse(any(e.source.startswith("R") for id in ("L01", "L18.GROUPS") for e in self.graph.ports[id].inputs))

    def test_full_transitive_fit_order_and_one_pass_calibrated_output(self):
        learned = [id for id in self.graph.order if self.graph.ports[id].learned]
        self.graph.validate_fit_order(learned)
        with self.assertRaises(ContractError):
            self.graph.validate_fit_order(reversed(learned))
        source = self.graph.ports["G01"]
        calibration = Port("G03.G01_APPLY", "G03", source.stage, source.schema, source.fields,
                           (InputPort(source.id, source.schema, source.fields, source.unit, source.target_id, source.capabilities),),
                           source.unit, source.target_id, source.capabilities, learned=True)
        graph = Graph([*self.graph.ports.values(), calibration])
        graph.validate_fit_order([id for id in graph.order if graph.ports[id].learned])
        with self.assertRaises(ContractError):
            add_edge(graph, calibration.id, "G01")


if __name__ == "__main__":
    unittest.main()
