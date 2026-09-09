"""Concrete reference runtime ports from the binding computation schedule.

Declarations establish legal information flow. They do not assert that a listed
producer has been implemented, fitted, evaluated, or selected. A run manifest
must still bind each enabled port to its actual implementation and artifacts.
"""

from dataclasses import dataclass

from trading_research.errors import ContractError, DependencyUnavailable
from trading_research.foundations.contracts import Capability as C
from trading_research.foundations.graph import Graph, InputPort, Port
from trading_research.foundations.time import MINUTE
from trading_research.foundations.units import Unit
from trading_research.operations.artifacts import digest


@dataclass(frozen=True)
class Binding:
    port: str
    implementation_hash: str
    definition_hash: str
    parameter_hash: str
    input_schema_hash: str
    model_artifact: str | None
    fit_lineage: str | None
    verification_artifact: str


def validate_bindings(graph: Graph, enabled: frozenset[str], bindings: tuple[Binding, ...]) -> str:
    by_id = {b.port: b for b in bindings}
    if len(by_id) != len(bindings) or set(by_id) != set(enabled) or not enabled.issubset(graph.ports):
        raise ContractError("enabled runtime ports require exact, unique implementation bindings")
    for id in enabled:
        p, b = graph.ports[id], by_id[id]
        if not all((b.implementation_hash, b.definition_hash, b.parameter_hash, b.input_schema_hash, b.verification_artifact)):
            raise DependencyUnavailable(f"unimplemented or unverified runtime binding: {id}")
        if p.learned and not (b.model_artifact and b.fit_lineage):
            raise DependencyUnavailable(f"missing fitted artifact or chronological closure: {id}")
        if any(not e.optional and e.source not in enabled for e in p.inputs):
            raise DependencyUnavailable(f"enabled consumer has a disabled required producer: {id}")
    return digest([graph.version, sorted(enabled), sorted(bindings, key=lambda b: b.port)])


def reference_graph(*, preceding_state_max_age_ns: int = 2 * MINUTE) -> Graph:
    """Two-cycle lag TTL is a named engineering scenario, not source certification."""
    specs = []

    def add(id, stage, schema, fields, deps=(), *, target=None, caps=(), learned=False, lane="optional", unit=None):
        specs.append((id, stage, schema, frozenset(fields.split()), tuple(deps), target, frozenset(caps), learned, lane, unit))

    add("F01.RAW", 0, "RawObservation.v1", "raw_bytes raw_fields source_id clocks", lane="market")
    add("F02.METADATA", 0, "InstrumentDefinition.v1", "instrument terms valid_time known_time coverage", lane="market")
    add("F03.CALENDAR", 0, "Calendar.v1", "session anchors boundaries eligibility known_time", lane="timer")
    add("F11.FROZEN", 0, "FrozenArtifacts.v1", "models transforms calibrators training_closure", lane="offline")
    add("F10.LINEAGE", 0, "ImmutableLineage.v1", "objects versions geometry observations visits relations candidate_cut targets action_aliases known_time history_cursor", lane="offline")
    add("F11.AUDIT", 0, "ArtifactClosure.v1", "commit roots semantic_ids actual_reads fit_closure target clocks invalidation errors", lane="offline")
    add("F12.ARRIVAL_TRACE", 0, "ArrivalTrace.v1", "raw_receipts canonical_stream served_versions trace_prefix clock_diagnostics parity telemetry incidents simulated_boundary actual_live_evidence", lane="offline")
    add("P.STATE", 0, "PreDecisionAccount.v1", "position orders cash headroom rule_version reconciled_at", lane="account")
    add("F06.RAW", 1, "RawQuality.v1", "schema sentinels integrity coverage", ("F01.RAW", "F02.METADATA"), lane="market")
    add("F05.NORMALIZED", 2, "CanonicalEvent.v1", "instrument action side flags price size bbo clocks source_id", ("F01.RAW", "F02.METADATA", "F06.RAW"), lane="market")
    add("F05.TRANSACTIONS", 3, "TransactionDelta.v1", "root_id receipt_id revision_id predecessor operation before after clocks condition ownership affected_fields", ("F05.NORMALIZED",), lane="market")
    add("F05.RECONCILIATION", 3, "UnpublishedReconciliation.v1", "candidate_pairs certified_pairs multiplicity conditions ownership discrepancies input_known_at published", ("F05.NORMALIZED",), lane="market")
    add("F06.SEMANTIC", 4, "SemanticQuality.v2", "book_health flow_coverage gaps corrections source_age revision ownership condition reconciliation", ("F05.NORMALIZED", "F05.TRANSACTIONS", ("F05.RECONCILIATION", "optional")), lane="market")
    add("F07.ELIGIBLE", 5, "OperationEligibility.v2", "raw_flow valuation execution support availability revision ownership condition", ("F05.NORMALIZED", "F05.TRANSACTIONS", "F06.SEMANTIC", "F03.CALENDAR"), lane="market")
    add("F09.BARS", 6, "CausalBars.v1", "ohlc volume provisional final known_time unfinished_state", ("F07.ELIGIBLE",), lane="market")
    add("F10.OBJECTS", 0, "PrecedingObjects.v1", "objects versions visits geometry confirmation", lane="market")
    add("G09.MASK", 6, "ApplicabilityMask.v1", "validity fitted_support missing_pattern abstention", ("F07.ELIGIBLE", "F11.FROZEN"))

    measurement_fields = {
        "M01": "buy sell unknown signed cumulative reset coverage",
        "M02": "cohorts cumulative_ohlc relative_ohlc extrema_times unknown_bounds",
        "M04": "histogram poc value_area mass grid anchor provisional",
        "M05": "buy_profile sell_profile unknown_profile delta peaks grid anchor",
        "M06": "bracket_visits tpo initial_balance single_prints dwell_proxy",
        "M08": "confirmed_swings running_extrema geometry confirmation_time",
        "M03": "anchor_pairs price_change flow_change divergence smt lag uncertainty",
        "M07": "vwap weighted_variance bands anchor mass confirmation_time",
        "M09": "ofi queue_imbalance microprice net_recovery event_rates quality timing_bounds",
        "M10": "activity intensity seasonal_residual counts coverage",
        "M11": "aggression_memory objects visits source_events decay",
        "M12": "opens closes settlements gaps reference_type publication anchor support",
        "M13": "footprint side_rows diagonal_imbalance stacked_runs tails unknown coverage"}
    depmap = {"M01": ("F07.ELIGIBLE",), "M02": ("M01", "F09.BARS"), "M04": ("F07.ELIGIBLE", "F03.CALENDAR"),
              "M05": ("M01", "M04"), "M06": ("F07.ELIGIBLE", "F03.CALENDAR"), "M08": ("F09.BARS",),
              "M03": ("M08", "M01", "M02", "X01.ALIGN"), "M07": ("F07.ELIGIBLE", "M08", "F03.CALENDAR"),
              "M09": ("F07.ELIGIBLE",), "M10": ("M01", "M02", "M09", "F11.FROZEN"),
              "M11": ("M01", "M02", "M04", "M05", "M08", "M10", "F10.OBJECTS"),
              "M12": ("F02.METADATA", "F03.CALENDAR", "F07.ELIGIBLE", "F09.BARS", "F10.OBJECTS"),
              "M13": ("M01", "M02", "M04", "M05", "F09.BARS")}
    add("X01.ALIGN", 100, "AsOfAlignment.v1", "receiver sources dates clocks native_units coverage", ("F07.ELIGIBLE",))
    stages = {"M01":100, "M02":101, "M04":100, "M05":101, "M06":100, "M08":100, "M03":102,
              "M07":101, "M09":100, "M10":102, "M11":103, "M12":100, "M13":102}
    for id, fields in measurement_fields.items():
        add(id, stages[id], f"{id}.Measurement.v1", fields, depmap[id], lane="market")
    add("C01.RANGE", 110, "FormationRange.v1", "high low midpoint crosses break_order formation_complete", ("F09.BARS", "F03.CALENDAR"))
    add("C02.PATH", 110, "ObservedPath.v1", "excursions running_extremes elapsed transitions", ("F07.ELIGIBLE", "C01.RANGE"))
    add("C04.OPEN", 111, "OpenLocation.v1", "gap range_position value_position observed_open_prefix", ("C01.RANGE", "M04", "F03.CALENDAR"))
    add("C07.STATE", 112, "ObservedAuction.v1", "occupancy progress balance discovery profile_support", ("M04", "M05", "M06", "C02.PATH"))
    add("C08.STATE", 113, "ObservedMigration.v1", "poc_path value_path transitions geometry_versions", ("M04", "C07.STATE"))
    add("C12.MEASURE", 110, "RealizedVariation.v1", "realized_variation sampling noise support", ("F09.BARS",))
    add("C17.EVENT", 110, "EventCalendar.v1", "scheduled_event known_release elapsed time_to_event", ("F07.ELIGIBLE", "F03.CALENDAR"))
    add("C05.FORMATION", 114, "DiscoveredFormation.v1", "rules state anchor confirmation", ("M10", "C07.STATE", "F11.FROZEN"))

    add("O01.CHAIN", 200, "RawOptionChain.v1", "contracts quotes trades reports underlying discount coverage", ("F07.ELIGIBLE", "F02.METADATA"))
    add("X02.BOOTSTRAP", 201, "RawParity.v1", "forward discount quote_bounds parity_residual contract_class", ("O01.CHAIN",))
    add("O02.IV", 202, "ImpliedVolatility.v1", "iv intervals residual eligibility methodology", ("O01.CHAIN", "X02.BOOTSTRAP"))
    add("O03.SIGN", 201, "OptionRawSign.v1", "buy sell unknown sign_probability quote_age raw_size", ("O01.CHAIN",))
    add("O04.SURFACE", 203, "Surface.v1", "parameters knots fit_uncertainty arbitrage_residual support", ("O02.IV", "F11.FROZEN"))
    add("O05.GREEKS", 204, "Greeks.v1", "delta gamma vega vanna charm units uncertainty", ("O04.SURFACE", "F02.METADATA"))
    add("O06.REPORTS", 201, "OpenInterestReports.v1", "position_date published_at oi changes source_ids coverage", ("O01.CHAIN",))
    add("O23.STATIC", 202, "SettlementPayoff.v1", "per_expiry payoff minima support position_date", ("O06.REPORTS", "F02.METADATA"))
    add("C15.SCENARIO", 205, "PrimitivePriceSurfaceScenario.v1", "joint_shocks weights support scenario_id", ("O04.SURFACE", "M01", "C01.RANGE", "C02.PATH", "C17.EVENT", ("C20.STATE", "lag"), "F11.FROZEN"), learned=True)

    add("O15.RAW_FLOW", 300, "OptionRawFlow.v1", "signed_contracts premium buy sell unknown event_ids", ("O03.SIGN",))
    add("O16.WEIGHTED_FLOW", 301, "GreekWeightedFlow.v1", "delta gamma vega vanna charm event_frozen_surface units coverage", ("O15.RAW_FLOW", "O05.GREEKS"))
    add("O18.MEASURE", 302, "FlowPriceImpact.v1", "pressure price_progress decay support", ("O15.RAW_FLOW", "O16.WEIGHTED_FLOW", "X01.ALIGN"))
    add("O20.MEASURE", 302, "OptionEventState.v1", "event intensity event_time uncertainty", ("O15.RAW_FLOW", "C17.EVENT"))
    add("O07.ENDPOINTS", 300, "OIEndpoints.v1", "endpoints flow_bridge bounds report_ids assimilated_ids", ("O06.REPORTS", "O15.RAW_FLOW"))
    add("O08.SCENARIOS", 301, "PositionScenarios.v1", "position_bounds weights uncertainty evidence_ids", ("O07.ENDPOINTS", "F11.FROZEN"))
    add("O09.BOARDS", 302, "ExposureBoards.v1", "by_strike by_expiry signed_abs exposure_units support", ("O08.SCENARIOS", "O05.GREEKS"))
    add("O10.CHANGES", 303, "ExposureDecomposition.v1", "price_surface_time_position_terms residual uncertainty", ("O09.BOARDS", "C15.SCENARIO"))
    add("O11.NODES", 304, "OptionNodes.v1", "nodes physical_support contact_regions uncertainty identity", ("O09.BOARDS",))
    add("O12.OBSERVED", 305, "ObservedNodeHistory.v1", "birth migration death split merge ancestry changes", ("O10.CHANGES", "O11.NODES"))
    add("O13.TOPOLOGY", 306, "ObservedTopology.v1", "adjacency components bottlenecks support", ("O11.NODES", "O12.OBSERVED"))
    add("O12.FIELD_EVOLUTION", 307, "FieldEvolutionForecast.v1", "field_distribution node_distribution uncertainty", ("O12.OBSERVED", "O13.TOPOLOGY", "C15.SCENARIO", "F11.FROZEN"), target="option_field_evolution", learned=True)
    add("O17.CENTERS", 303, "ExposureCenters.v1", "strike_centers denominator sign concentration", ("O09.BOARDS",))
    add("O14.BASE", 308, "Forecast.WithinChain.v1", "distribution coverage uncertainty", ("O09.BOARDS", "O13.TOPOLOGY", "F11.FROZEN"), target="within_chain_path", caps=(C.FIRST_PASSAGE,), learned=True)
    add("O19.FUTURES_OPTIONS", 308, "FuturesOptionAdapter.v1", "raw_flow supported_valuation receiver_mapping uncertainty", ("O15.RAW_FLOW", ("O16.WEIGHTED_FLOW", "optional"), "F02.METADATA"))
    add("O21.QUALITY", 309, "OptionQuality.v1", "raw_coverage scenario_uncertainty identifiable_support", ("O01.CHAIN", "O08.SCENARIOS", "O09.BOARDS"))
    add("O23.SCENARIO", 302, "ScenarioSettlementPayoff.v1", "scenario_payoffs minima intervals", ("O08.SCENARIOS", "F02.METADATA"))
    add("X02.MAPPING", 310, "RelatedCoordinateMapping.v1", "source_coordinate execution_coordinate mapping_jacobian uncertainty support", ("X01.ALIGN", "F02.METADATA", ("X02.BOOTSTRAP", "optional"), "F11.FROZEN"))

    for id in ("X07", "X08", "X09", "X10"):
        add(f"{id}.MEASURE", 210, f"{id}.SourceMeasurements.v1", "native_features source_cadence observation_times coverage units", ("X01.ALIGN", "F07.ELIGIBLE"))
        add(f"{id}.FORECAST", 400, f"{id}.SourceForecast.v1", "distribution uncertainty support", (f"{id}.MEASURE", "F11.FROZEN"), target=f"{id}.source_path", caps=(C.FIRST_PASSAGE,), learned=True)
    add("C20.STATE", 400, "FilteredContextState.v1", "axes filtered_state uncertainty matured_residual_state", ("M10", "C07.STATE", "C08.STATE", "C12.MEASURE", "C17.EVENT", "F11.FROZEN", ("C20.STATE", "lag")), learned=True)
    var_deps = {"C09":("C01.RANGE",), "C10":("C02.PATH",), "C11":("C04.OPEN",), "C12":("C12.MEASURE",),
                "C13":("C09", "C10", "C11", "C12"), "C14":("C12", "C17.EVENT"),
                "C15":("O02.IV", "O04.SURFACE", "C15.SCENARIO"), "C16":("C16.MEASURE",),
                "C23":("F09.BARS",), "C24":("F09.BARS",)}
    add("C16.MEASURE", 401, "VIXMeasures.v1", "forward strip_vol vvix realized implied clock product_rules support", ("X02.BOOTSTRAP", "O02.IV", "O04.SURFACE", "X01.ALIGN", "F02.METADATA"))
    add("C16.JOINT_STRESS", 402, "PrimitiveStress.v1", "vix_surface raw_stress joint_state uncertainty", ("C16.MEASURE", "X01.ALIGN", "C12.MEASURE"))
    for id, deps in var_deps.items():
        add(id, 404 if id == "C13" else 403, "Forecast.Variance.v1", "distribution variance uncertainty support", (*deps, "C20.STATE", "F11.FROZEN"), target="remaining_log_return_variance", caps=(C.TERMINAL_VARIANCE,), unit=Unit.LOG_RETURN_VARIANCE, learned=id != "C23")
    add("C18", 405, "Forecast.AuctionPath.v1", "distribution uncertainty support", ("M01", "C07.STATE", "X01.ALIGN", "C20.STATE", "F11.FROZEN"), target="auction_path", caps=(C.FIRST_PASSAGE,), learned=True)
    add("C04.FORECAST", 406, "Forecast.OpenType.v1", "distribution observed_prefix support", ("C04.OPEN", "C18", "F11.FROZEN"), target="open_type", caps=(C.COUNT,), learned=True)
    add("C07.TRANSITION", 406, "Forecast.AuctionTransition.v1", "transition_distribution support", ("C07.STATE", "C18", "F11.FROZEN"), target="auction_state_transition", learned=True)
    add("C08.PROFILE_EVOLUTION", 407, "Forecast.Profile.v1", "mass_shape_distribution support uncertainty", ("M04", "M05", "C07.STATE", "C08.STATE", "F11.FROZEN"), target="future_profile_mass_shape", learned=True)

    add("G02.V", 500, "Forecast.Variance.v1", "distribution variance uncertainty support", (*var_deps.keys(), "F11.FROZEN"), target="remaining_log_return_variance", caps=(C.TERMINAL_VARIANCE,), unit=Unit.LOG_RETURN_VARIANCE, learned=True)
    add("C06", 501, "Forecast.Excursions.v1", "joint_excursions uncertainty support", ("G02.V", "C01.RANGE", "C04.OPEN", "C07.STATE", "F11.FROZEN"), target="remaining_excursions", caps=(C.EXCURSIONS,), learned=True)
    add("C03", 502, "Forecast.RangePaths.v1", "break_order distribution support", ("C06", "C01.RANGE", "C02.PATH", "F11.FROZEN"), target="range_break_order", caps=(C.FIRST_PASSAGE,), learned=True)
    add("C19", 503, "Forecast.Remainder.v1", "joint_path distribution uncertainty support", ("C06", "C03", "C02.PATH", "C18", ("O11.NODES", "optional"), ("O12.FIELD_EVOLUTION", "optional"), ("O13.TOPOLOGY", "optional"), ("O14.BASE", "optional"), "F11.FROZEN"), target="receiver_path", caps=(C.FIRST_PASSAGE,), learned=True)
    add("C21", 504, "Forecast.SessionTransition.v1", "transition_distribution support", ("C19", "F03.CALENDAR", "F11.FROZEN"), target="session_transition", learned=True)
    add("O13.FORECAST", 600, "Forecast.Topology.v1", "topology_distribution support", ("O13.TOPOLOGY", "C19", "F11.FROZEN"), target="future_topology", learned=True)
    add("O22.LOCAL", 601, "Forecast.OptionLocalPath.v1", "distribution uncertainty support", ("C19", "O13.FORECAST", "O14.BASE", "X01.ALIGN", "X02.BOOTSTRAP", "F11.FROZEN"), target="receiver_path", caps=(C.FIRST_PASSAGE,), learned=True)
    for id in ("X03", "X04"):
        add(id, 602, f"Forecast.{id}.v1", "distribution uncertainty support", ("O22.LOCAL", "X01.ALIGN", "F11.FROZEN"), target="receiver_path", caps=(C.FIRST_PASSAGE,), learned=True)
    add("X05", 603, "Forecast.Transmission.v1", "distribution source_known_time receiver_label_start uncertainty", ("X03", "X04", "X01.ALIGN", "F11.FROZEN"), target="receiver_path", caps=(C.FIRST_PASSAGE,), learned=True)
    add("X06", 604, "Forecast.JointReceiver.v1", "distribution uncertainty support", ("X03", "X04", "X05", "X07.FORECAST", "X08.FORECAST", "X09.FORECAST", "X10.FORECAST", "F11.FROZEN"), target="receiver_path", caps=(C.FIRST_PASSAGE,), learned=True)
    add("O22.JOINT_REFINED", 605, "Forecast.RefinedOptionPath.v1", "distribution uncertainty support", ("O22.LOCAL", "X06", "F11.FROZEN"), target="receiver_path", caps=(C.FIRST_PASSAGE,), learned=True)

    add("G01", 700, "Forecast.TargetMatchedMixture.v1", "distribution expert_ids weights target_signature support", ("C19", "X06", "O22.JOINT_REFINED", "G09.MASK", "F11.FROZEN"), target="receiver_path", caps=(C.FIRST_PASSAGE,), learned=True)
    add("G02.PATH", 701, "Forecast.Excursions.v1", "joint_excursions uncertainty support", ("C06", "G01", "F11.FROZEN"), target="remaining_excursions", caps=(C.EXCURSIONS,), learned=True)
    add("C22", 702, "OpportunityProposals.v1", "birth geometry target origin evidence_ids", ("G01", "G02.PATH", "C19", "F10.OBJECTS", "F11.FROZEN"), learned=True)
    location_inputs = {
        1:("C01.RANGE", "C02.PATH"), 2:("C01.RANGE", "C02.PATH"),
        3:("M12", ("M04", "optional"), ("M05", "optional"), "C04.OPEN"),
        4:("C06", "C01.RANGE", ("M04", "optional"), ("O11.NODES", "optional")),
        5:("M04", "C07.STATE", "C08.STATE"), 6:("M05", "M10", "M11"),
        7:("M06", "F03.CALENDAR"), 8:("M08",),
        9:("F09.BARS", ("M08", "optional"), ("M13", "optional")),
        10:("M08", "F09.BARS"), 11:("M07",), 12:("M12", "F03.CALENDAR", "C17.EVENT"),
        13:("O11.NODES", "X02.MAPPING", "O21.QUALITY"),
        14:("O17.CENTERS", "O13.TOPOLOGY", "X02.MAPPING", ("O23.STATIC", "optional")),
        15:("X05", "C19", "X01.ALIGN", "M08", "C22"),
        16:("M04", "M05", "M11", ("O11.NODES", "optional"), "C19"),
        19:("M11", "M02", "M10")}
    for number, inputs in location_inputs.items():
        id = f"L{number:02}"
        add(id, 703, f"{id}.Objects.v1", "identity geometry anchor clocks ancestry visits coverage", (*inputs, "F10.OBJECTS", "F11.FROZEN"), learned=number == 16)
        add(f"{id}.ROLE", 704, "Forecast.ObjectRole.v1", "roles distribution target_signature uncertainty support", (id, "C19", "F11.FROZEN"), target="frozen_object_role_path", caps=(C.FIRST_PASSAGE,), learned=True)
    add("L17", 704, "Forecast.ObjectLifecycle.v1", "survival retest failure expiry applicability uncertainty", ("F10.OBJECTS", "M11", "C20.STATE", ("O12.OBSERVED", "optional"), "F11.FROZEN"), target="object_lifecycle", learned=True)
    add("L18.GROUPS", 705, "OpportunityGroups.v1", "object_versions geometry groups source_lineage", ("F10.OBJECTS", *( (f"L{n:02}", "optional") for n in location_inputs), ("C22", "optional")))
    add("G04", 800, "Forecast.Reach.v1", "reach_probability nonreach time_distribution", ("L18.GROUPS", "G01", "F11.FROZEN"), target="frozen_object_reach", caps=(C.FIRST_PASSAGE,), learned=True)
    add("G05", 801, "Forecast.ConditionalPath.v1", "joint_outcomes terminal_branches uncertainty", ("G04", "G01", "L18.GROUPS", "F11.FROZEN"), target="frozen_object_postcontact_path", caps=(C.FIRST_PASSAGE,), learned=True)
    add("P02.PLANS", 802, "FullUnitPlans.v1", "entry stop target deadline costs feasibility", ("G05", "L18.GROUPS", "P.STATE", "F02.METADATA", "F03.CALENDAR"))
    add("L18.PLANS", 803, "ImmutableActionSet.v1", "plan_ids object_versions mutually_exclusive_actions wait_actions", ("L18.GROUPS", "P02.PLANS"))
    add("P05.FILL", 803, "Forecast.Fill.v1", "fill_probability delay adverse_selection nonfill", ("L18.PLANS", "F07.ELIGIBLE", "F11.FROZEN"), target="plan_fill", learned=True)
    add("P06.COST", 803, "Forecast.Cost.v1", "fees slippage latency uncertainty", ("L18.PLANS", "F07.ELIGIBLE", "F11.FROZEN"), target="plan_cost", learned=True)
    add("G06", 804, "Forecast.ActionValue.v1", "expected_net tail_risk uncertainty nonfill_value occupancy", ("G05", "L18.PLANS", "P05.FILL", "P06.COST", "P.STATE", "F11.FROZEN"), target="incremental_executable_action_value", caps=(C.ACTION_VALUE,), unit=Unit.USD, learned=True)
    add("G07", 805, "Forecast.WaitValue.v1", "wait_values missed_winner cost occupancy uncertainty", ("G06", "P.STATE", "F11.FROZEN"), target="incremental_executable_action_value", caps=(C.ACTION_VALUE,), unit=Unit.USD, learned=True)
    add("O21.DECISION_SENSITIVITY", 806, "DecisionSensitivity.v1", "value_sensitivity scenario_uncertainty next_cycle_priorities", ("O21.QUALITY", "G06", "G07"))
    add("G09.SELECT", 807, "FinalApplicability.v1", "admissible_actions reasons uncertainty", ("G06", "G07", "G09.MASK", "O21.DECISION_SENSITIVITY"))
    add("G08", 808, "Selection.v1", "selected rejected reasons candidate_ids", ("G06", "G07", "G09.SELECT", "L18.PLANS", "F11.FROZEN"), learned=True)
    add("P01.INTENT", 900, "EntryIntent.v1", "client_id one_mini side geometry version_vector expiry", ("G08", "P.STATE", "F03.CALENDAR"))
    add("P08.RESERVE", 901, "RiskReservation.v1", "headroom reserve atomic_version veto", ("P01.INTENT", "P.STATE", "F07.ELIGIBLE"), lane="account")
    add("P07.DISPATCH", 902, "OrderState.v1", "client_ids broker_events unknown reconcile position", ("P08.RESERVE", "P.STATE"), lane="account")
    add("P10.EMERGENCY", 1, "IndependentRiskAction.v1", "cancel protect flatten halt reason", ("P.STATE", "F03.CALENDAR"), lane="timer")

    declarations = {r[0]: r for r in specs}
    ports = []
    for id, stage, schema, fields, deps, target, caps, learned, lane, unit in specs:
        edges = []
        for dep in deps:
            source, qualifier = (dep, None) if isinstance(dep, str) else dep
            p = declarations[source]
            lag = qualifier == "lag"
            edges.append(InputPort(source, p[2], p[3], p[9], p[5], p[6],
                                   lag_ns=1 if lag else 0, max_age_ns=preceding_state_max_age_ns if lag else None,
                                   optional=qualifier in {"optional", "lag"}))
        ports.append(Port(id, "P07" if id == "P.STATE" else id.split(".")[0], stage, schema, fields, tuple(edges), unit, target, caps, learned, lane))
    return Graph(ports)
