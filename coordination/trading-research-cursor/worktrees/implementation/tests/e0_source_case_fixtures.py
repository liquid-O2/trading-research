"""Exact INT02/03/05 controls through source publications and native paths.

Stable names in the golden descriptor are reported as aliases of actual
content-addressed publications. They are never substituted for runtime hashes.
"""

from dataclasses import dataclass, replace
from datetime import date, datetime, time
from decimal import Decimal
from fractions import Fraction
import hashlib
import json
from pathlib import Path

from trading_research.context.range_adapter import primitive_from_shared_bar, select_clock
from trading_research.context.ranges import range_definition, range_version
from trading_research.data.events import LatencyScenario, SourceAddress, normalize_mbp
from trading_research.errors import ContractError, DependencyUnavailable, IntegrityError
from trading_research.experiments.e0.candidates import E0Object, objects, stop_distance
from trading_research.experiments.e0.observations import (
    build_e0_decision_population, label_e0_candidate, label_e0_price_path,
)
from trading_research.experiments.e0.policy import (
    E0ActionValue, E0SyntheticNumericalEvidence, TargetPolicy, score_and_decide_e0,
)
from trading_research.experiments.e0.source_bridge import NativeCoverageReceipt, freeze_e0_ranges, venue_path_from_mbp
from trading_research.foundations.bars import Watermark, WindowCoverage
from trading_research.foundations.calendar import Calendar, local_timestamp
from trading_research.foundations.contracts import Band
from trading_research.foundations.multiresolution import BarDefinition, BarDomain, BarLimits, SharedBarEngine, WindowRequest
from trading_research.foundations.units import Ticks
from trading_research.measurements.tape import Trade
from trading_research.operations.artifacts import canonical_json, digest

from e0_source_fixtures import _range_graph, _session, _source_instrument, make_int01_source


NS = 1_000_000_000
MINUTE = 60 * NS
NY = "America/New_York"
REPO = Path(__file__).resolve().parents[1]


def case(identity):
    return next(row for row in json.loads((REPO / "tests/golden/e0_integration_v1.json").read_bytes())["cases"]
                if row["case_id"] == identity)


def civil(value):
    parsed = datetime.fromisoformat(value)
    return local_timestamp(parsed.date(), parsed.time(), NY)


def descriptor_hash(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


@dataclass(frozen=True)
class RangeControl:
    source: object
    engine: SharedBarEngine
    current: object
    prior: object
    provisional: object | None
    revised: object | None
    aliases: dict

    def frozen(self, current=None, *, cut=None, prior_selection="actual"):
        current = self.current if current is None else current
        return freeze_e0_ranges(selected_day=self.source.admission, range_06_09=current,
            prior_rth=self.prior, prior_selection=(self.source.admission.selection_evidence
                if prior_selection == "actual" else prior_selection),
            cut=current.known_at if cut is None else cut)


def range_control(*, current_ohlc=(72020, 72100, 72000, 72080),
                  prior_ohlc=(71960, 72080, 71920, 72040), prior_delay=0,
                  provisional=False, revision=False, two_rows=False):
    source = make_int01_source()
    day, previous = source.day, date(2024, 5, 31)
    start, end = civil("2024-06-03T06:00:00"), civil("2024-06-03T09:00:00")
    prior_start, prior_end = civil("2024-05-31T09:30:00"), civil("2024-05-31T16:00:00")
    prior_at = end + prior_delay
    instrument = _source_instrument(source.definitions[1],
        valid_from=source.definitions[1].clocks.valid_from, valid_until=source.definitions[1].clocks.valid_until)
    graph = _range_graph(day, previous, current_start=start, current_end=end,
                         prior_start=prior_start, prior_end=prior_end)
    calendar = Calendar()
    for day_value in (previous, day):
        calendar.append(_session(day_value, known_at=source.definitions[1].clocks.known_at))
    current_selection = select_clock(calendar=calendar, interval_graph=graph,
        interval_name=f"C01-06_09-{day}", trading_date=day, instrument_root="NQ", instrument=instrument,
        cut=end-MINUTE if provisional else end)
    prior_selection = select_clock(calendar=calendar, interval_graph=graph,
        interval_name=f"L03-prior-RTH-{previous}", trading_date=previous, instrument_root="NQ", instrument=instrument,
        cut=prior_at)
    domain = BarDomain(instrument.raw_symbol, "registered-whole-print", "registered-whole-print")
    definitions = tuple(BarDefinition(domain, role, graph.version, selection.clock_id)
        for role, selection in (("INT02-C01", current_selection), ("INT02-prior-RTH", prior_selection)))
    engine = SharedBarEngine(domain, definitions, limits=BarLimits(32, 8, 8, 8))
    def trade(identity, at, known, ticks, order):
        return Trade(identity, "INT02-native-source:"+identity, instrument.raw_symbol,
                     at, known, Ticks(ticks), 1, 1, order, "registered-whole-print", True)
    if two_rows:
        current_rows = (trade("bar-1", start+NS, start+NS, current_ohlc[2], 1),
                        trade("bar-2", start+2*NS, start+2*NS, current_ohlc[1], 2))
    else:
        times = (start+NS, start+2*NS, start+3*NS, end-NS)
        current_rows = tuple(trade("bar-"+str(i+1), at, at, value, i+1)
                             for i, (at,value) in enumerate(zip(times,current_ohlc)))
    prior_times = (prior_start+NS, prior_start+2*NS, prior_start+3*NS, prior_end-NS)
    prior_rows = tuple(trade("prior-"+str(i+1), at, prior_at, value, 10+i)
                      for i,(at,value) in enumerate(zip(prior_times,prior_ohlc)))
    engine.add_many(tuple(sorted((*current_rows,*prior_rows), key=lambda row: (row.known_at,row.id))))
    def publish(selection, definition, at, *, final):
        left, right = selection.formation_start, selection.formation_end
        observed = ((left,right if final else min(at,right)),)
        coverage = WindowCoverage(instrument.raw_symbol, left, right, observed, at,
                                  digest((definition.id,observed,at)))
        bar = engine.publish_window(engine.capture(at), WindowRequest(definition.id,left,right,coverage,
            Watermark(right,at,"INT02-watermark:"+str(at)) if final else None), published_at=at)
        primitive = primitive_from_shared_bar(selection=selection,engine=engine,
            publication_version_id=bar.version_id,cut=at)
        return range_version(primitive,range_definition(selection,id=definition.id,
            source_ids=("C01",) if definition is definitions[0] else ("L03",)),cut=at)
    forming = publish(current_selection,definitions[0],end-MINUTE,final=False) if provisional else None
    current = publish(current_selection,definitions[0],end,final=True)
    prior = publish(prior_selection,definitions[1],prior_at,final=True)
    revised = None
    if revision:
        changed_at = end+MINUTE
        engine.add(trade("correction-7",end-NS,changed_at,72104,30))
        revised = publish(current_selection,definitions[0],changed_at,final=True)
    aliases = {current.version_id:"c01-v1",prior.version_id:"prior-rth-v1"}
    if forming is not None: aliases[forming.version_id] = "c01-v0"
    if revised is not None: aliases[revised.version_id] = "c01-v2"
    return RangeControl(source,engine,current,prior,forming,revised,aliases)


def source_alias(control, obj):
    # E0Object retains the immutable FrozenRange parent; the parent retains
    # the actual C01/L03 formula publication. Neither identity is a label hash.
    frozen = control.frozen(cut=max(control.current.known_at,control.prior.known_at))
    parents = {frozen.range_06_09.version:frozen.range_06_09.source_version,
               frozen.prior_rth.version:frozen.prior_rth.source_version}
    return control.aliases[parents.get(obj.source_version,obj.source_version)]


def check_int02_f01(test):
    frozen = case("E0-INT-02-F01")
    control = range_control(provisional=True)
    test.assertEqual(control.provisional.known_at,frozen["inputs"]["range_versions"][0]["known_at"])
    test.assertEqual(control.provisional.status,"provisional")
    test.assertIsNone(control.provisional.geometry)
    test.assertFalse(control.provisional.primitive.coverage_complete)
    test.assertEqual(control.current.primitive.formation_start,frozen["inputs"]["clock"]["start"]["utc_ns"])
    test.assertEqual(control.current.primitive.formation_end,frozen["inputs"]["clock"]["end"]["utc_ns"])
    with test.assertRaises(DependencyUnavailable): control.frozen(control.provisional)
    # The public object producer cannot publish either future final parent.
    complete = control.frozen()
    early = objects(complete.range_06_09,complete.prior_rth,cut=control.provisional.known_at)
    test.assertEqual(len(early),frozen["variants"][0]["expected"]["object_count"])
    test.assertEqual(len(complete.objects),frozen["variants"][1]["expected"]["object_count"])
    current = {obj.type.split(":")[1]:int(obj.price) for obj in complete.objects if obj.type.startswith("06_09:")}
    prior = {obj.type.split(":")[1]:int(obj.price) for obj in complete.objects if obj.type.startswith("prior_rth:")}
    test.assertEqual(current,frozen["variants"][1]["expected"]["range_objects_ticks"])
    test.assertEqual(prior,frozen["variants"][1]["expected"]["prior_rth_objects_ticks"])
    test.assertEqual({source_alias(control,obj) for obj in complete.objects},
                     set(frozen["variants"][1]["all_source_versions"]))
    test.assertEqual(control.current.width_ticks,100)
    test.assertEqual(control.prior.primitive.selection.window.trading_date,date(2024,5,31))
    test.assertEqual({obj.instrument for obj in complete.objects},{frozen["inputs"]["selected_instrument_id"]})


def check_int02_f02(test):
    frozen = case("E0-INT-02-F02")
    control = range_control(two_rows=True,revision=True)
    old = control.frozen()
    old_bytes = canonical_json(old)
    old_population = build_e0_decision_population(frozen_context=old,completed_cuts=(control.current.known_at,),
                                                 sampled_midpoints={control.current.known_at:72050})
    row_bytes = canonical_json(tuple(old_population))
    new = control.frozen(control.revised)
    test.assertEqual(control.current.primitive.source_event_ids,tuple(frozen["inputs"]["revision_zero"]["source_event_ids"]))
    test.assertEqual(control.revised.primitive.source_event_ids,tuple(frozen["inputs"]["revision_one"]["source_event_ids"]))
    test.assertEqual(control.revised.primitive.supersedes,control.current.primitive.publication_version_id)
    test.assertEqual(control.aliases[old.range_06_09.source_version],frozen["expected"]["at_09_00_parent_version"])
    test.assertEqual(control.aliases[new.range_06_09.source_version],frozen["expected"]["at_09_01_parent_version"])
    test.assertEqual(new.range_06_09.width,frozen["expected"]["new_width_ticks"])
    test.assertEqual((old.cut,new.cut),tuple(frozen["inputs"]["decision_cuts"]))
    test.assertTrue(set(obj.version for obj in old.objects).isdisjoint(
        obj.version for obj in new.objects if obj.type.startswith("06_09:")))
    test.assertEqual(new.range_06_09.supersedes,control.current.primitive.publication_version_id)
    test.assertTrue(all(obj.source_version == new.range_06_09.version
                        for obj in new.objects if obj.type.startswith("06_09:")))
    test.assertEqual(canonical_json(old),old_bytes)
    test.assertEqual(canonical_json(tuple(old_population)),row_bytes)
    test.assertNotEqual(old.version,new.version)
    old_publication,_ = control.engine.window_publication(control.current.primitive.publication_version_id)
    test.assertEqual(old_publication.summary.high_ticks,72100)
    with test.assertRaises(DependencyUnavailable): control.frozen(control.revised,cut=control.current.known_at)


def check_int02_f03(test):
    frozen = case("E0-INT-02-F03")
    expected = {v["id"]:v["expected"] for v in frozen["variants"]}
    zero = range_control(current_ohlc=(72000,72000,72000,72000))
    test.assertEqual(zero.current.status,"final")
    test.assertEqual(zero.current.width_ticks,0)
    test.assertFalse(zero.current.usable_e0)
    with test.assertRaises(DependencyUnavailable): zero.frozen()
    with test.assertRaises(DependencyUnavailable) as error: stop_distance(zero.current.width_ticks)
    test.assertEqual(str(error.exception),expected["zero-width"]["reason"])
    control = range_control()
    with test.assertRaises(ContractError) as error: control.frozen(prior_selection=None)
    test.assertEqual(str(error.exception),expected["missing-prior-selection"]["reason"])
    with test.assertRaises(DependencyUnavailable) as error:
        control.frozen(prior_selection={"instrument_id":"1001"})
    test.assertEqual(str(error.exception),expected["cross-contract-prior"]["reason"])


def population_control():
    frozen = case("E0-INT-03-F01")
    control = range_control(current_ohlc=(72000,72012,71996,72004),
                            prior_ohlc=(71996,72012,71960,72004),prior_delay=MINUTE)
    context = control.frozen(cut=control.prior.known_at)
    templates = {obj.type:obj for obj in context.objects}
    selected = []
    for raw,kind in zip(frozen["inputs"]["objects"],("06_09:eq","prior_rth:close","06_09:high")):
        template = templates[kind]
        if template.price != raw["price_ticks"]:
            raise AssertionError("literal candidate does not match its actual range parent")
        selected.append(replace(template,id=raw["id"],born_at=raw["born_at"],known_at=raw["born_at"]))
    context = replace(context,e0_objects=tuple(selected),cut=max(obj.available_at for obj in selected))
    return frozen,control,context


def row_alias(row, *, missing=False):
    if row.side == 0:
        return "background-"+datetime.fromtimestamp(row.cut/NS,__import__('zoneinfo').ZoneInfo(NY)).strftime("%H%M")
    stem = {"obj-a":"cand-a","obj-b":"cand-b","obj-c":"cand-gap" if missing else "cand-c"}[row.object_id]
    return stem if missing else stem+("-long" if row.side==1 else "-short")


def policy_choice(ds, rows, policy_name, *, selected_side):
    """Exact policy-port control; probabilities are declared inputs, not fits."""
    policy = TargetPolicy(policy_name,1)
    values = []
    for row in rows:
        if row.contact is None or row.side != selected_side:
            continue
        payload = canonical_json(("INT03-declared-positive-contact-value",row.version,policy.version))
        values.append(E0ActionValue(row.id,policy,Fraction(1),Fraction(0),Fraction(0),
            Fraction(1),Fraction(-1),Fraction(0),ds.cut,ds.cut,digest(payload),digest((policy.id,"15m")),
            "INT03-policy-input-control",row.version,source_version=row.source_version,
            object_version=row.object_version,decision_set_id=ds.id,side=row.side,horizon_end=ds.cut+15*MINUTE,
            intent_id="intent:"+row.id,expiry_at=ds.cut+15*MINUTE,
            artifact_evidence=E0SyntheticNumericalEvidence(
                id=digest(payload), fitted_at=ds.cut, target_version=digest((policy.id,"15m")),
                fold_id="INT03-policy-input-control", feature_version=row.version,
                model_version=digest(payload), source_version=row.source_version)))
    return score_and_decide_e0(decision_set=ds,bracket_candidates=tuple(values))[1]


def check_int03_f01(test):
    frozen,control,context = population_control()
    inputs,expected = frozen["inputs"],frozen["expected"]
    sampled = {civil(at):price for at,price in inputs["sampled_midpoints_ticks"].items()}
    population = build_e0_decision_population(frozen_context=context,completed_cuts=tuple(inputs["cuts"]),
        sampled_midpoints=sampled,policy_id=inputs["policy_views_at_0932"]["learned"]["policy_id"])
    test.assertEqual(len(population.decision_sets),len(inputs["cuts"]))
    for ds in population.decision_sets:
        test.assertEqual(len(ds.rows),expected["population_count_per_cut"])
        test.assertEqual(sum(row.side != 0 for row in ds.rows),expected["object_candidate_rows_per_cut"])
        test.assertEqual(sum(row.side == 0 for row in ds.rows),expected["background_rows_per_cut"])
        expected_requests = inputs["label_requests_by_cut"][datetime.fromtimestamp(ds.cut/NS,
                            __import__('zoneinfo').ZoneInfo(NY)).isoformat().removesuffix("-04:00")]
        requests = [{"object_id":row.object_id,"side":row.side} if row.side else {"background":True}
                    for row in ds.rows]
        test.assertCountEqual(requests,expected_requests)
        clock_name = datetime.fromtimestamp(ds.cut/NS,__import__('zoneinfo').ZoneInfo(NY)).strftime("%H%M")
        test.assertEqual(len(requests),expected["label_requests_per_cut"])
        test.assertEqual(sum(row.side == 1 and row.contact is None for row in ds.rows),
                         expected["no_touch_object_count_by_cut"][clock_name])
        test.assertEqual(sum(row.side != 0 and row.contact is None for row in ds.rows),
                         expected["no_touch_side_row_count_by_cut"][clock_name])
    test.assertEqual(sum(row.side == 0 for row in population),expected["background_rows_retained"])
    test.assertEqual(sum(row.side == 1 and row.contact is None for row in population),
                     expected["no_touch_object_count_all_cuts"])
    test.assertEqual(sum(row.side != 0 and row.contact is None for row in population),
                     expected["no_touch_side_row_count_all_cuts"])
    ds = population.by_cut(inputs["cuts"][1])
    projected = [{"cut":"2024-06-03T09:32:00","distance_ticks":None if row.distance is None else int(row.distance),
        "id":row_alias(row),"object_id":row.object_id,"side":row.side} for row in ds.rows]
    test.assertEqual(projected,inputs["candidate_rows"])
    test.assertEqual(descriptor_hash(projected),expected["prepared_candidate_descriptor_sha256"])
    test.assertEqual([row_alias(row) for row in ds.rows],expected["candidate_order_at_0932"])
    contacts = [row for row in ds.rows if row.side == 1 and row.contact is not None]
    test.assertEqual(len(contacts),expected["same_price_source_rows_retained"])
    test.assertEqual({row.approach for row in contacts},{1})
    test.assertEqual({row.fade_side for row in contacts},{expected["rule_fade_side"]})
    learned = policy_choice(ds,ds.rows,inputs["policy_views_at_0932"]["learned"]["policy_id"],selected_side=1)
    rule = policy_choice(ds,ds.rows,"INT03-first-inward-fade",selected_side=contacts[0].fade_side)
    test.assertEqual(learned.candidate_ids,tuple(row.id for row in ds.rows))
    test.assertEqual(rule.candidate_ids,tuple(row.id for row in ds.rows))
    by_id = {row.id:row for row in ds.rows}
    test.assertEqual(row_alias(by_id[learned.selected_value.candidate_id]),expected["selected_action_at_0932"]["learned"])
    test.assertEqual(row_alias(by_id[rule.selected_value.candidate_id]),expected["selected_action_at_0932"]["rule"])
    # Bound input changes alter real decision identity independently of the
    # human-readable prepared descriptor and of any future label annotation.
    changed = build_e0_decision_population(frozen_context=context,completed_cuts=tuple(inputs["cuts"]),
        sampled_midpoints={**sampled,inputs["cuts"][1]:72005},policy_id=ds.policy_id)
    test.assertNotEqual(population.population_hash,changed.population_hash)
    test.assertNotEqual(ds.id,changed.by_cut(ds.cut).id)
    test.assertEqual({source_alias(control,obj) for obj in context.objects},{"c01-v1","prior-rth-v1"})


def native_path(rows, *, complete_intervals, source_order_known=True, name="INT05"):
    source = make_int01_source()
    events,aliases = [],{}
    for index,row in enumerate(rows):
        at = row.get("event_at",row.get("at"))
        known = row.get("known_at",at+250_000_000)
        price = row["price_ticks"]
        address = SourceAddress(name,"frozen-native-v1",name+".mbp-1","native-mbp-container-v1",
                                "2024-06-03",index,"mbp-native-v1")
        fields = {"ts_event":at,"ts_recv":known,"instrument_id":1002,"publisher_id":1,
            "action":row.get("action","A"),"side":row.get("side","N"),
            "price":price*250_000_000,"size":1,"flags":row.get("flags",128),"depth":0,
            "bid_px_00":(price-1)*250_000_000,"ask_px_00":(price+1)*250_000_000,"bid_sz_00":5,"ask_sz_00":5}
        fields["sequence"] = row.get("sequence",index+1) if source_order_known else None
        event = normalize_mbp(fields,address,native=True,
            scenario=LatencyScenario("INT05-exact-retained-receipt","provider_received",0,0))
        events.append(event);aliases[event.id] = row.get("id","native-"+str(index))
    events = tuple(events)
    receipt = NativeCoverageReceipt.from_events(events,source_id=name,schema_version="mbp-native-v1",
        instrument_id="1002",complete_intervals=tuple(complete_intervals),source_order_known=source_order_known,
        coverage_version=digest((name,complete_intervals,tuple(event.id for event in events))))
    path = venue_path_from_mbp(canonical_events=events,selected_instrument=source.admission,coverage=receipt,
        latency_scenario=LatencyScenario("INT05-retained-receipt-bound","provider_received",0,0),market_state="continuous")
    return path,aliases


def candidate_for_label(cut, *, object_id="obj-a", candidate_id=None, price=72004):
    _,_,context = population_control()
    obj = replace(context.objects[0],id=object_id,price=Fraction(price),band=Band(Fraction(price-1),Fraction(price+1)))
    population = build_e0_decision_population(frozen_context=replace(context,e0_objects=(obj,)),
        completed_cuts=(cut,),sampled_midpoints={cut:72000},policy_id="INT05-complete-label-population")
    row = next(row for row in population if row.side==1)
    return row if candidate_id is None else replace(row,id=candidate_id)


def check_int03_f02(test):
    frozen = case("E0-INT-03-F02")
    _,_,context = population_control()
    inputs,expected = frozen["inputs"],frozen["expected"]
    populations = []
    gaps_all = [inputs["path_coverage"]["gaps"],*expected["future_gap_change_check"]["alternate_gaps"]]
    for gaps in gaps_all:
        population = build_e0_decision_population(frozen_context=context,completed_cuts=(inputs["cut"],),
            sampled_midpoints={inputs["cut"]:None},path_coverage={**inputs["path_coverage"],"gaps":gaps})
        populations.append(population)
        test.assertEqual(len(population),7)  # Both label sides remain in the actual E0 denominator.
        projected = [row for row in population if row.side in (1,0)]
        test.assertEqual([row_alias(row,missing=True) for row in projected],expected["candidate_order"])
        test.assertEqual({row_alias(row,missing=True):row.reason for row in projected},expected["reasons"])
        test.assertEqual(sum(row.contact is not None for row in population),expected["touch_count"])
        decision = score_and_decide_e0(decision_set=population.decision_sets[0],bracket_candidates=())[1]
        test.assertEqual(decision.selected_action,expected["selected_action"])
    test.assertEqual(len({pop.population_hash for pop in populations}),1)
    projected = [row for row in populations[0] if row.side in (1,0)]
    descriptor = {**inputs,"candidate_ids":[row_alias(row,missing=True) for row in projected],
        "same_price_rows":[{"id":row_alias(row,missing=True),"born_at":row.born_at,"price_ticks":int(row.price)}
                           for row in projected if row.object_id in ("obj-a","obj-b")]}
    test.assertEqual(descriptor_hash(descriptor),expected["prepared_candidate_descriptor_sha256"])
    gap_start,gap_end = inputs["path_coverage"]["gaps"][0]
    endpoint = inputs["path_coverage"]["target_end"]
    path,_ = native_path(({"at":inputs["cut"],"price_ticks":72000,"known_at":inputs["cut"]},),
        complete_intervals=((inputs["cut"],gap_start),(gap_end,endpoint)),name="INT03-future-gap")
    before = canonical_json(tuple(populations[0]))
    for row in projected:
        if row.side == 0: continue
        bundle = label_e0_candidate(candidate_row=row,sampled_midpoints={row.cut:None},venue_path=path,
            target_end=endpoint,observation_process="INT03-separate-future-coverage")
        annotation = {**bundle.coverage_annotation,
                      "gap":[list(gap) for gap in bundle.coverage_annotation["gap"]]}
        test.assertEqual(annotation,expected["future_label_annotations_separate"][row_alias(row,missing=True)])
    test.assertEqual(canonical_json(tuple(populations[0])),before)


def check_int03_f03(test):
    frozen = case("E0-INT-03-F03")
    _,_,context = population_control()
    first,second,future = frozen["inputs"]["versions"]
    base = context.objects[0]
    old = replace(base,id="obj-a",price=Fraction(first["price_ticks"]),born_at=first["born_at"],known_at=first["known_at"])
    revised = replace(base,id="obj-a",price=Fraction(second["price_ticks"]),
        band=Band(Fraction(second["price_ticks"]-1),Fraction(second["price_ticks"]+1)),
        born_at=second["born_at"],known_at=second["known_at"],supersedes=old.version)
    early = build_e0_decision_population(frozen_context=replace(context,e0_objects=(old,)),
        completed_cuts=(frozen["inputs"]["cuts"][0],),sampled_midpoints={frozen["inputs"]["cuts"][0]:72004})
    before = canonical_json(tuple(early))
    later = build_e0_decision_population(frozen_context=replace(context,e0_objects=(revised,)),
        completed_cuts=(frozen["inputs"]["cuts"][1],),sampled_midpoints={frozen["inputs"]["cuts"][1]:72005})
    aliases = {old.version:first["id"],revised.version:second["id"]}
    test.assertEqual(aliases[early[0].object_version],frozen["expected"]["earlier_parent_version"])
    test.assertEqual(aliases[later[0].object_version],frozen["expected"]["later_parent_version"])
    test.assertEqual(revised.supersedes,old.version)
    test.assertEqual(later[0].object_version,revised.version)
    test.assertEqual(canonical_json(tuple(early)),before)
    test.assertNotEqual(early.population_hash,later.population_hash)
    too_late = replace(base,id=future["id"],price=Fraction(future["price_ticks"]),
        band=Band(Fraction(future["price_ticks"]-1),Fraction(future["price_ticks"]+1)),
        born_at=future["born_at"],known_at=future["known_at"])
    with test.assertRaises(ContractError) as error:
        build_e0_decision_population(frozen_context=replace(context,e0_objects=(too_late,)),
            completed_cuts=(frozen["inputs"]["cuts"][1],),sampled_midpoints={})
    test.assertEqual(str(error.exception),frozen["expected"]["reason_future_object"])
    # Birth and receipt are separate: an old object received tomorrow is unavailable today.
    with test.assertRaises(ContractError):
        build_e0_decision_population(frozen_context=replace(context,e0_objects=(replace(old,known_at=future["known_at"]),)),
            completed_cuts=(frozen["inputs"]["cuts"][1],),sampled_midpoints={})


def check_int05_f01(test):
    frozen = case("E0-INT-05-F01")
    inputs,expected = frozen["inputs"],frozen["expected"]
    cut,endpoint = inputs["cut"]["utc_ns"],inputs["target_end"]["utc_ns"]
    candidate = candidate_for_label(cut,candidate_id=inputs["candidate_id"])
    before = canonical_json(candidate)
    path,aliases = native_path(tuple(inputs["native_events"]),complete_intervals=((cut,endpoint),))
    sampled = {row["at"]:row["midpoint_ticks"] for row in inputs["sampled_midpoints"]}
    bundle = label_e0_candidate(candidate_row=candidate,sampled_midpoints=sampled,venue_path=path,
        target_end=endpoint,observation_process="INT05-native-object-fixed-end")
    test.assertEqual(bundle.sampled_contact.at,expected["sampled_contact_at"])
    test.assertEqual(bundle.sampled_contact.price,expected["sampled_contact_price_ticks"])
    test.assertEqual(bundle.visit_count,expected["visit_count"])
    test.assertEqual(bundle.label["reach_status"],expected["reach_status"])
    test.assertEqual(bundle.label["contact_at"],expected["native_intervening_touch_at"])
    test.assertLess(bundle.label["contact_at"],bundle.sampled_contact.at)
    test.assertEqual(bundle.label["observed_end"],expected["actual_observation_end"])
    test.assertEqual(bundle.target.end,expected["fixed_end"])
    test.assertEqual([aliases[identity] for identity in bundle.native_event_ids],
                     [row["id"] for row in inputs["native_events"]])
    test.assertEqual(canonical_json(candidate),before)
    prefix = label_e0_candidate(candidate_row=candidate,sampled_midpoints={cut:sampled[cut]},venue_path=path,
        target_end=endpoint,observation_process="INT05-native-object-fixed-end")
    test.assertIsNone(prefix.sampled_contact)
    test.assertEqual(prefix.label,bundle.label)
    test.assertNotEqual(prefix.sampled_observation_version,bundle.sampled_observation_version)
    with test.assertRaises(IntegrityError):
        venue_path_from_mbp(
            canonical_events=path.canonical_events,
            selected_instrument=path.selected_day,
            coverage=replace(path.coverage,source_id="INT05-unregistered-source"),
            latency_scenario=path.latency_scenario,
            market_state="continuous",
        )
    tampered_bytes = b"INT05-tampered-native-bytes"
    with test.assertRaises(IntegrityError):
        venue_path_from_mbp(
            canonical_events=path.canonical_events,
            selected_instrument=path.selected_day,
            coverage=replace(path.coverage,raw_bytes=tampered_bytes,
                             raw_sha256=hashlib.sha256(tampered_bytes).hexdigest()),
            latency_scenario=path.latency_scenario,
            market_state="continuous",
        )
    # A print cannot create a midpoint touch, or a midpoint a trade touch.
    mixed,_ = native_path(({"at":cut+NS,"price_ticks":72000},
                          {"at":cut+2*NS,"price_ticks":72004,"action":"T","side":"B"}),
                         complete_intervals=((cut,endpoint),),name="INT05-distinct-native-streams")
    midpoint = label_e0_candidate(candidate_row=candidate,sampled_midpoints={cut:72000},venue_path=mixed,
        target_end=endpoint,observation_process="INT05-midpoint",native_observation="bbo_midpoint")
    prints = label_e0_candidate(candidate_row=candidate,sampled_midpoints={cut:72000},venue_path=mixed,
        target_end=endpoint,observation_process="INT05-trade",native_observation="eligible_trade")
    test.assertEqual(midpoint.label["reach_status"],"no_contact")
    test.assertEqual(prints.label["reach_status"],"contact")
    test.assertNotEqual(midpoint.target.version,prints.target.version)


def check_int05_f02(test):
    frozen = case("E0-INT-05-F02")
    inputs = frozen["inputs"]
    expected = {row["id"]:row["expected"] for row in frozen["variants"]}
    candidate = candidate_for_label(inputs["cut"],object_id="obj-b",candidate_id=inputs["candidate_id"])
    for variant in inputs["variants"]:
        with test.subTest(variant=variant["id"]):
            cursor = inputs["cut"]
            intervals = []
            for left,right in variant["gaps"]:
                intervals.append((cursor,left));cursor=right
            intervals.append((cursor,variant["observed_end"]))
            path,_ = native_path(tuple(variant["points"]),complete_intervals=tuple(intervals),
                source_order_known=variant["source_order_known"],name="INT05:"+variant["id"])
            bundle = label_e0_candidate(candidate_row=candidate,sampled_midpoints={inputs["cut"]:inputs["initial_ticks"]},
                venue_path=path,target_end=inputs["target_end"],observation_process="INT05-native-object-fixed-end",
                favorable_distance=Fraction(inputs["favorable_distance_ticks"]),
                adverse_distance=Fraction(inputs["adverse_distance_ticks"]))
            for key,value in expected[variant["id"]].items():
                actual = bundle.label[key]
                test.assertEqual(list(actual) if type(actual) is tuple and type(value) is list else actual,value,key)
            test.assertEqual(bundle.coverage.end,variant["observed_end"])
            test.assertEqual(bundle.target.end,inputs["target_end"])
            test.assertEqual(bundle.coverage.source_order_known,variant["source_order_known"])
            if not variant["source_order_known"]:
                test.assertTrue(all(event.provider_sequence is None for event in path.canonical_events))
    late,_ = native_path(({"at":inputs["cut"],"known_at":inputs["cut"],"price_ticks":72000},
        {"at":inputs["cut"]+5*MINUTE,"known_at":inputs["target_end"]+2*NS,
         "price_ticks":72004,"flags":132}),complete_intervals=((inputs["cut"],inputs["target_end"]),),
         name="INT05-late-invalid-book-evidence")
    late_bundle = label_e0_candidate(candidate_row=candidate,sampled_midpoints={inputs["cut"]:72000},
        venue_path=late,target_end=inputs["target_end"],observation_process="INT05-late-gap")
    test.assertEqual(late_bundle.label["status"],"censored")
    test.assertEqual(late_bundle.label["maturity_at"],inputs["target_end"]+2*NS)
    late_invalid = late.canonical_events[1]
    test.assertEqual(late.event_ids,tuple(event.id for event in late.canonical_events))
    test.assertIn(late_invalid.id,late.event_ids)
    test.assertEqual(late.quality["book_invalid_rows"],1)
    test.assertEqual(late_bundle.coverage.gaps,((late_invalid.clocks.event_at,inputs["target_end"]),))
    test.assertTrue(late.coverage.recovery_complete)
    with test.assertRaises(DependencyUnavailable) as incomplete:
        venue_path_from_mbp(
            canonical_events=late.canonical_events,
            selected_instrument=late.selected_day,
            coverage=replace(late.coverage,recovery_complete=False),
            latency_scenario=late.latency_scenario,
            market_state="continuous",
        )
    test.assertEqual(str(incomplete.exception),"native recovery evidence is incomplete")


def check_int05_f03(test):
    frozen = case("E0-INT-05-F03")
    inputs,expected = frozen["inputs"],frozen["expected"]
    candidate = candidate_for_label(inputs["cut"],candidate_id=inputs["candidate_id"])
    path,aliases = native_path(tuple(inputs["points"]),
        complete_intervals=((inputs["cut"],inputs["points"][-1]["at"]+1),),name="INT05-endpoint")
    bundle = label_e0_price_path(candidate_row=candidate,sampled_midpoints={inputs["cut"]:inputs["initial_ticks"]},
        venue_path=path,target_end=inputs["target_end"],observation_process=inputs["label_semantics"],
        up_ticks=inputs["favorable_barrier_ticks"]-inputs["initial_ticks"],
        down_ticks=inputs["initial_ticks"]-inputs["adverse_barrier_ticks"])
    test.assertEqual(bundle.control_type,expected["control_type"])
    test.assertEqual(bundle.label.first_barrier,"upper")
    test.assertEqual(bundle.label.first_barrier_at,expected["first_barrier_at"])
    test.assertEqual(bundle.label.observed_end,expected["observed_end"])
    test.assertEqual(bundle.target.horizon_end,inputs["target_end"])
    test.assertEqual(inputs["initial_ticks"]+8,expected["barrier_ticks"])
    test.assertIn(expected["endpoint_point_included"],[aliases[value] for value in bundle.native_event_ids])
    test.assertEqual([aliases[value] for value in bundle.rejected_event_ids],[expected["post_endpoint_point_handling"]["point"]])
    test.assertEqual(bundle.rejection_reasons[0][1],expected["post_endpoint_point_handling"]["reason"])
    test.assertEqual(bundle.label.maturity_at,inputs["points"][1]["known_at"])
    test.assertFalse(hasattr(bundle.label,"departure"))
    second_at=path.canonical_events[1].clocks.event_at
    tampered_intervals=((path.coverage.window_start,second_at),
                        (second_at+1,path.coverage.window_end))
    with test.assertRaises(DependencyUnavailable):
        venue_path_from_mbp(
            canonical_events=path.canonical_events,
            selected_instrument=path.selected_day,
            coverage=replace(path.coverage,complete_intervals=tampered_intervals),
            latency_scenario=path.latency_scenario,
            market_state="continuous",
        )
    changed = label_e0_price_path(candidate_row=candidate,sampled_midpoints={inputs["cut"]:inputs["initial_ticks"]},
        venue_path=path,target_end=inputs["target_end"],observation_process=inputs["label_semantics"],
        up_ticks=16,down_ticks=8)
    test.assertNotEqual(bundle.target.signature,changed.target.signature)
    test.assertNotEqual(bundle.target_definition,changed.target_definition)
    test.assertEqual(changed.label.first_barrier,"neither")
    object_bundle = label_e0_candidate(candidate_row=candidate,sampled_midpoints={inputs["cut"]:inputs["initial_ticks"]},
        venue_path=path,target_end=inputs["target_end"],observation_process="INT05-object-control")
    test.assertEqual(object_bundle.label["reach_status"],"no_contact")
    test.assertEqual(object_bundle.label["departure"],"no_contact")
