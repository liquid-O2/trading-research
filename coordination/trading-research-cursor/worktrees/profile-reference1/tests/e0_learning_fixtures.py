"""Frozen E0 learning controls with authentic retained F11 source fixtures.

No expected coefficient, probability or bracket label is used to fit a model.
The independent literal tables supply only feature values and observed labels;
connected controls derive those values from the native E0 source pipeline.
"""

from dataclasses import replace
from datetime import datetime, timezone
from pathlib import Path
import hashlib
import json

from trading_research.operations.artifacts import canonical_json, digest
from trading_research.operations.artifact_graph import SemanticArtifactStore, payload_ref
from trading_research.operations.provenance import InputValue
from trading_research.research.folds import Sample
from trading_research.research.models import BinaryExample
from trading_research.experiments.e0.learning import E0LearningConfig


REPO = Path(__file__).parents[1]
GOLDEN = json.loads((REPO / "tests/golden/e0_integration_v1.json").read_text())
CASES = {case["case_id"]: case for case in GOLDEN["cases"]}
NS = 1_000_000_000
HORIZON = 900 * NS


def literal(case_id):
    return CASES[case_id]


def utc_at(year, *, day=1, hour=14, minute=0):
    return int(datetime(year, 6, day, hour, minute, tzinfo=timezone.utc).timestamp()) * NS


def example(identity, day, at, target_version, columns, values, outcome):
    sample = Sample(identity, day, at, at + HORIZON, at + HORIZON, target_version)
    inputs = tuple(InputValue(column, digest((identity, column, value)), at,
                             canonical_json(value)) for column, value in zip(columns, values))
    return BinaryExample(sample, inputs, outcome)


def retained_references(target_payload):
    """Retain actual reviewed implementation bytes and exact target definition."""
    payloads = {}
    def keep(raw, kind):
        ref = payload_ref(raw, kind)
        payloads[ref.sha256] = raw
        return ref
    paths = ("src/trading_research/research/models.py", "src/trading_research/research/calibration.py",
             "src/trading_research/experiments/e0/learning.py",
             "src/trading_research/experiments/e0/learning_store.py")
    code_ref = keep(canonical_json(tuple((path, (REPO / path).read_text()) for path in paths)), "code")
    target_ref = keep(target_payload, "target")
    definition_ref = keep(canonical_json({"schema": "E0FixtureInputDefinitionV1",
        "source": "exact published InputValue snapshots", "target": target_ref.sha256}), "definition")
    return {"code_ref": code_ref, "target_ref": target_ref,
            "definition_ref": definition_ref, "payloads": payloads}


def analytic_learning_fixture(root):
    """Return the exact nonconstant four-stage INT09F03 feature/label rows."""
    frozen = literal("E0-INT-09-F03")["inputs"]
    linked = frozen["linked_nonconstant_pipeline"]
    columns = tuple(linked["feature_columns"])
    target = canonical_json({"schema": "E0AnalyticReachTargetV1",
        "literal_target": frozen["target_version"], "horizon_ns": HORIZON,
        "purpose": "independent_symmetric_ridge_control"})
    refs = retained_references(target)
    config = E0LearningConfig(refs["target_ref"].sha256, "INT09-linked-four-stage", "INT09-full-literal-rows",
        columns=columns, frequency_columns=columns, frequency_cuts=((0.,), (0.,)),
        control="analytic_ridge", target_payload=target)
    stages = (
        (2022, linked["fit_rows_2022"]),
        (2023, linked["fit_artifacts_and_selection_predictions"][0]["predictions"]),
        (2024, linked["calibration_2024"]["feature_rows_2024"]),
        (2025, frozen["evaluation_predictions_2025"]),
    )
    rows = []
    for year, source_rows in stages:
        for index, row in enumerate(source_rows):
            rows.append(example(row["id"], f"{year}-06-01", utc_at(year, minute=index),
                config.target_version, columns, tuple(row["features"]), row.get("label", 0)))
    # The zero-input heldout check is an additional prediction control; the
    # frozen eval-s25-1 row remains exact and separately asserted.
    rows.append(example("INT09-extra-zero-evaluation", "2025-06-02", utc_at(2025, day=2),
        config.target_version, columns, (0., 0.), 0))
    store = SemanticArtifactStore(Path(root), "INT09-linked-models")
    return {"examples": tuple(rows), "config": config, "store": store,
            "namespace": store.namespace, "references": refs, "literal": frozen}


def stage_literal_samples():
    frozen = literal("E0-INT-09-F01")["inputs"]
    return tuple(Sample(**{**{k: v for k, v in row.items() if k != "past_lookback_end"},
                           "target_version": frozen["target_version"]}) for row in frozen["samples"])


def constant_learning_control():
    from trading_research.research.folds import chronological_fold
    from trading_research.research.period import ResearchScopeV1
    frozen = literal("E0-INT-09-F03")["inputs"]["independent_logistic_fit_control"]
    columns = tuple(frozen["feature_columns"])
    rows = tuple(example(identity, "2022-06-01", utc_at(2022, minute=i), "constant-control-target",
                         columns, (value,), label) for i, (identity, value, label) in enumerate(zip(
                             frozen["training_ids"], frozen["feature_values"], frozen["labels"])))
    query = example("constant-heldout", "2025-06-01", utc_at(2025), "constant-control-target", columns, (1.,), 0)
    rows += (query,)
    scope = ResearchScopeV1.diagnostic(cohort_id="INT09-constant", denominator_id="literal-four-rows")
    fold = chronological_fold(tuple(e.sample for e in rows), id=frozen["fold_id"],
        fit_at=frozen["fitted_at"], evaluation_start=frozen["fitted_at"],
        evaluation_end=utc_at(2026), training_start=utc_at(2022)-HORIZON,
        embargo_ns=HORIZON, scope=scope)
    return rows, fold, scope, query, frozen


def frequency_learning_control():
    from trading_research.research.folds import chronological_fold
    from trading_research.research.period import ResearchScopeV1
    # Exact cell counts are frozen; distinct row identities/clocks are additional
    # retained scaffolding, not a second source of expected probabilities.
    columns = ("object_type", "side", "distance_over_width")
    data = (((0., 1., .1), 1), ((0., 1., .1), 1), ((0., 1., .1), 0),
            ((0., -1., .5), 1), ((0., -1., .5), 0))
    rows = tuple(example(f"frequency-fit-{i}", "2022-06-01", utc_at(2022, minute=i),
                         "frequency-control-target", columns, x, y) for i, (x,y) in enumerate(data))
    populated = example("frequency-populated", "2025-06-01", utc_at(2025),
                        "frequency-control-target", columns, (0., 1., .1), 0)
    unseen = example("frequency-unseen", "2025-06-02", utc_at(2025, day=2),
                     "frequency-control-target", columns, (1., -1., 1.), 0)
    rows += (populated, unseen)
    scope = ResearchScopeV1.diagnostic(cohort_id="INT09-frequency", denominator_id="literal-five-counts")
    fold = chronological_fold(tuple(e.sample for e in rows), id="INT09-frequency-fit", fit_at=utc_at(2023),
        evaluation_start=utc_at(2023), evaluation_end=utc_at(2026), training_start=utc_at(2022)-HORIZON,
        embargo_ns=HORIZON, scope=scope)
    return rows, fold, scope, populated, unseen, columns


def physical_reach_learning_control():
    """Derive the independent five-column reach control from literal raw inputs."""
    frozen = literal("E0-INT-09-F03")["inputs"]["full_e0_feature_pipeline_control"]
    columns = tuple(frozen["causal_feature_columns"])
    target = canonical_json({"schema": "E0PhysicalReachControlV1", "target": frozen["target"],
                             "horizon_ns": HORIZON})
    refs = retained_references(target)
    config = E0LearningConfig(refs["target_ref"].sha256, "INT09-physical-reach", "literal-full-five-columns",
        columns=columns, frequency_columns=("side",), frequency_cuts=((0.,),),
        control="physical_reach", target_payload=target)
    rows = []
    for day in frozen["days"]:
        prices = day["completed_minute_prices_ticks"]
        cut = day["decision_midpoint"]["known_at"]
        endpoint = day["decision_midpoint"]["at"] + HORIZON
        future = day["future_object"]
        features = (day["range_06_09"]["high_ticks"] - day["range_06_09"]["low_ticks"],
                    future["price_ticks"] - day["decision_midpoint"]["midpoint_ticks"],
                    prices[-1] - prices[-6],
                    sum((b-a)**2 for a,b in zip(prices, prices[1:])))
        outcome = int(any(point["event_at"] <= endpoint and point["price_ticks"] == future["price_ticks"]
                          for point in day["native_future_path"]))
        for side in day["side_rows"]:
            rows.append(example(side["id"], day["business_date"], cut, config.target_version,
                                columns, (*features, side["side"]), outcome))
    for year, key in ((2023, "selection_2023"), (2024, "calibration_2024")):
        for i, row in enumerate(frozen[key]["rows"]):
            rows.append(example(row["id"], f"{year}-06-01", utc_at(year, minute=i), config.target_version,
                                columns, tuple(row["features"]), row["label"]))
    rows.append(example("physical-reach-heldout", "2025-06-01", utc_at(2025), config.target_version,
                        columns, (100, 8, 0, 0, 1), 0))
    return tuple(rows), config, frozen


def build_connected_bracket_router(root, evaluation_days):
    """Train both policies from causal native-source rows and actual bracket labels.

    Returns ``(router, evidence)``. Evidence includes actual day/population/path
    versions, plans, outcomes, and full features for each policy. No expected
    probability or outcome table participates in fitting.
    """
    from datetime import date
    from decimal import Decimal
    from fractions import Fraction
    from tests.e0_source_fixtures import make_run_day
    from trading_research.data.events import LatencyScenario
    from trading_research.execution.replay import BracketPlan, reference_bracket
    from trading_research.execution.venue import FillScenario
    from trading_research.experiments.e0.source_bridge import venue_path_from_mbp
    from trading_research.experiments.e0.observations import build_e0_decision_population
    from trading_research.experiments.e0.runner import SCENARIOS, e0_feature_values
    from trading_research.experiments.e0.learning import (
        E0Head, E0BracketRouter, bracket_target_payload, fit_e0_binary)
    from trading_research.experiments.e0.learning_store import commit_e0_fit
    frozen = literal("E0-INT-09-F03")["inputs"]["root_connected_bracket_pipeline"]
    training_days = tuple(make_run_day(date.fromisoformat(day), quote_path="learning_up" if i == 0 else "learning_down")
        for dates in (frozen["training_dates"], frozen["selection_dates"], frozen["calibration_dates"])
        for i, day in enumerate(dates))
    days = (*training_days, *tuple(evaluation_days))
    scenario = SCENARIOS[0]
    records, day_evidence = [], []
    for day in days:
        path = venue_path_from_mbp(canonical_events=day.native_events, selected_instrument=day.context.selected_day,
            coverage=day.coverage, recovery_certificates=day.recovery_certificates,
            latency_scenario=LatencyScenario(scenario.id, "event", scenario.feed_lag_ms*1_000_000, 0),
            tick_size=day.operational.terms.tick_size, market_state=day.market_state)
        midpoints = {}
        for cut in day.cuts:
            quote, _ = path.quote_at(cut, clock="strategy")
            midpoints[cut] = None if quote is None else Fraction(quote.bid+quote.ask, 2)
        population = build_e0_decision_population(frozen_context=day.context, completed_cuts=day.cuts,
            sampled_midpoints=midpoints, policy_id="E0-common-clock-population-v1")
        day_evidence.append((day.day, day.context.version, path.version, population.population_hash))
        for row in population:
            if row.contact is None:
                continue
            quote, _ = path.quote_at(row.cut, clock="strategy")
            features = e0_feature_values(day, row, midpoint=midpoints[row.cut], cut=row.cut,
                                        source_quote=quote, scenario=scenario)
            records.append((day, path, row, features))
    policies, evidence = [], []
    for multiple in (1, 2):
        policy = f"target-{multiple}x-fixed"
        labeled = []
        for day, path, row, features in records:
            quote, reason = path.quote_at(row.cut, clock="strategy")
            if quote is None:
                raise ValueError(reason)
            worst = (quote.ask + scenario.impact_ticks if row.side == 1 else quote.bid - scenario.impact_ticks)
            plan = BracketPlan("INT09-label:"+policy+":"+row.id, path.instrument, row.side, row.cut,
                worst, worst-row.side*10, worst+row.side*10*multiple, row.cut+HORIZON,
                day.operational.window["flatten_send_at"], day.operational.window["required_flat_at"],
                Decimal(0), digest((policy, "fixed-ten-tick-stop", row.version if hasattr(row,"version") else row)))
            fill_scenario = FillScenario(scenario.id, scenario.impact_ticks, "venue_first", "strict_trade_through",
                                         path.coverage_version, day.operational.fees.version)
            outcome = reference_bracket(path, plan, terms=day.operational.terms, fees=day.operational.fees,
                                        fill_scenario=fill_scenario, timing=scenario.timing)
            if not outcome.observation_complete or outcome.exit_reason not in ("target", "stop", "deadline"):
                raise ValueError("connected learning label is incomplete: "+outcome.exit_reason)
            labeled.append((day, row, features, plan, outcome))
        heads = []
        for head in ("target", "stop", "deadline"):
            target = bracket_target_payload(policy, head)
            refs = retained_references(target)
            config = E0LearningConfig(refs["target_ref"].sha256, "INT09-connected:"+policy+":"+head,
                "native-contact-complete-eight-row-stages", policy_version=policy, head=head, target_payload=target)
            examples = tuple(BinaryExample(Sample(row.id, day.day, row.cut, row.cut+HORIZON,
                max(row.cut+HORIZON, outcome.position_known_flat_at or row.cut+HORIZON), config.target_version),
                features, int(outcome.exit_reason == head)) for day,row,features,plan,outcome in labeled)
            fit = fit_e0_binary(examples, config)
            store = SemanticArtifactStore(Path(root)/policy/head, "INT09-connected-models")
            committed = commit_e0_fit(store, namespace=store.namespace, **refs, examples=examples, fit=fit)
            heads.append(E0Head(head, fit, committed, examples))
        policies.append((policy, tuple(heads)))
        evidence.append((policy, tuple((day.day,row,features,plan,outcome) for day,row,features,plan,outcome in labeled)))
    return E0BracketRouter(tuple(policies)), {"days": tuple(day_evidence), "policies": tuple(evidence),
                                            "training_days": training_days, "evaluation_days": tuple(evaluation_days)}
