"""Versioned, outcome-blind empirical research comparison registry."""
from __future__ import annotations
import json
import re
import copy
from contextlib import contextmanager
from contextvars import ContextVar
from functools import lru_cache
from hashlib import sha256
from pathlib import Path
from .catalog import BRANCHES, METHOD_BY_ID, EXTRA_PREDICATES

REGISTRY_VERSION = '1.0.0'
DEFAULT_PATH = Path('/workspace/implementation/reports/phase1-live/empirical/registry/CANDIDATE_REGISTRY.json')

def canonical_hash(doc):
    body = {k:v for k,v in doc.items() if k != 'registry_sha256'}
    return sha256(json.dumps(body, sort_keys=True, separators=(',', ':'), allow_nan=False).encode()).hexdigest()

# All numbers and clocks below are frozen comparison decisions, not inferred
# source labels. The source method's missing conjuncts remain unknown.
SPECS = {
 ('JJ-TBR','judas_reversal'): ('range_sweep_reclaim', 'First native-minute strict range-edge sweep during 09:40–09:50; score only the NEXT strictly later aligned complete 3-minute close through swept edge by 09:50; no search for a later favorable close.', {'range_start':'06:00','range_end':'09:00','action_start':'09:40','expiry':'09:50','confirmation_minutes':3}, 'TBR:4;TBR:27;FORMULAS:M01', 'range_edge_sweep'),
 ('JJ-TBR','extension_reaction'): ('extension_band_reentry', 'First contact after 09:00 with frozen outer-range beyond-edge band H+[1.33,1.66]W or L-[1.66,1.33]W; score only the NEXT strictly later complete aligned 3-minute close inward through near edge by 16:00; no search for a later favorable close.', {'range_start':'06:00','range_end':'09:00','action_start':'09:00','expiry':'16:00','multipliers':['1.33','1.66'],'parent':'outer_06_09','confirmation_minutes':3}, 'TBR:20;TBR:21;JR:23;FORMULAS:O015', 'extension_band_touch'),
 ('JJ-TBR','internal_rotation'): ('midpoint_edge_path', 'First 09:30–16:00 contact with frozen 06:00–09:00 midpoint; freeze path side long if contact-bar close >= midpoint else short; first later high/low range-edge contact passes on chosen side and fails on opposite side; same-bar double edge is unknown; no trade claim.', {'range_start':'06:00','range_end':'09:00','action_start':'09:30','expiry':'16:00','trigger_minutes':1,'direction':'contact_close_ge_eq_long'}, 'TBR:4;FORMULAS:M01;FORMULAS:O007', 'midpoint_contact_path'),
 ('GB-VWAP','source_long'): ('session_high_break_vwap_touch', 'First complete native 1-minute close above both finished Asia/London highs; first strictly later 1-minute bar straddling its pre-bar VWAP by 16:00. No extra defended-close requirement.', {'asia':['20:00','00:00'],'london':['02:00','05:00'],'vwap_reset':'18:00_previous_day','vwap_basis':'HLC3_volume_weighted_native_1m','breakout_minutes':1,'retest_minutes':1,'action_start':'05:00','expiry':'16:00','sides':['long']}, 'GB:33;GB:34;FORMULAS:M03', 'session_high_breakout'),
 ('SIRES','vwap_deviation_fade'): ('fixed_band_first_close_reentry', 'First 5-minute action-bar touch per side of pre-bar VWAP +/- one population weighted SD, from native 1-minute HLC3 since previous 18:00; freeze touched band. Score FIRST strictly later 5-minute close inward, within 15 minutes. Retain both side opportunities when both bands touched together and mark ambiguous.', {'vwap_reset':'18:00_previous_day','vwap_basis':'HLC3_volume_weighted_native_1m','variance':'population_volume_weighted','sigma':'1','action_minutes':5,'action_start':'09:30','expiry':'16:00','horizon_minutes':15,'endpoint':'first_later_close_only','per_side':True}, 'FORMULAS:M05;FORMULAS:O125', 'deviation_band_touch'),
 ('SAINT-AMT','continuation_retest'): ('prior_rth_boundary_retest', 'First complete 5-minute close beyond prior complete same-contract RTH high/low; score only the FIRST later same-boundary touch within 60 minutes by whether its close is beyond that boundary; no search for a later favorable retest.', {'profile_session':['09:30','16:00'],'action_minutes':5,'horizon_minutes':60,'expiry':'16:00'}, 'FORMULAS:M06;FORMULAS:O091', 'prior_rth_boundary_break'),
 ('SAINT-AMT','trapped_buyers_retest'): ('positive_delta_upper_failure_retest', 'First 5-minute bar trades above prior RTH high with positive executed delta and closes below; score only the FIRST later high retest within 60 minutes by whether its close is below with negative delta; no later favorable retest search. Short only; does not reconstruct source two prior failures.', {'profile_session':['09:30','16:00'],'action_minutes':5,'horizon_minutes':60,'expiry':'16:00','sides':['short']}, 'FORMULAS:M06;FORMULAS:O119', 'positive_delta_upper_failure'),
 ('SAINT-AMT','failed_auction_return'): ('prior_rth_boundary_return_to_poc', 'First two consecutive complete 5-minute closes beyond prior RTH high/low; later close inside followed by prior trade-volume POC contact by 16:00. Older-value exploration and full source auction sequence remain unknown.', {'profile_session':['09:30','16:00'],'action_minutes':5,'outside_closes':2,'expiry':'16:00'}, 'FORMULAS:M06;FORMULAS:O094', 'two_close_boundary_excursion'),
 ('SAINT-AMT','poc_traversal'): ('prior_rth_poc_cross_two_close_hold', 'First complete 5-minute close crosses prior RTH trade-volume POC from previous-bar side while inside prior range. Pass at two consecutive destination-side closes before two origin-side closes; fail for origin first; ties reset streaks; no resolved streak by expiry is unknown. Source reacceptance antecedent remains unknown.', {'profile_session':['09:30','16:00'],'action_minutes':5,'hold_closes':2,'expiry':'16:00','ties':'reset_streak','unresolved':'unknown'}, 'FORMULAS:M06;FORMULAS:O095', 'poc_crossing'),
 ('KEANI-OPEN-ABOVE-VALUE','source_long'): ('complete_a_above_prior_value', 'Every eligible session opening creates an observation; at 10:00 classify complete A-period low strictly above frozen previous complete RTH trade-volume VAH. Profile uses 70% contiguous POC-outward higher-adjacent-volume expansion, both rows on ties. No developing-value, imbalance, DOM or entry inference.', {'prior_session':['09:30','16:00'],'a_period':['09:30','10:00'],'opportunity_at':'09:30','availability':'first_native_minute_end','expiry':'10:00','value_fraction':'0.70','poc_tie':'lowest_price','va_expansion':'contiguous_larger_adjacent_volume_tie_both','sides':['long']}, 'AVG:21;AVG:22;FORMULAS:M08', 'opening_state'),
 ('REFILL-STUDY','touch_record'): ('immutable_large_execution_zone_return', 'Two same-aggressor executions each >=100 contracts within 120 seconds and two native ticks form immutable zone at second event; require four-tick directional departure before each return. Fifteen-minute response: formation-side four-tick displacement before four-tick trade-through of opposite edge; ambiguous ordering unknown. New four-tick departure rearms; no private order or replenishment claim.', {'min_event_quantity':100,'min_events':2,'formation_seconds':120,'span_ticks':2,'departure_ticks':4,'response_ticks':4,'horizon_minutes':15,'zone_mutation':'forbidden','expiry':'16:00'}, 'REF:7;REF:12;OFM:18;FORMULAS:M09', 'zone_return'),
}
_m09 = SPECS[('REFILL-STUDY','touch_record')]
SPECS[('REFILL-STUDY','touch_record')] = (
    _m09[0],
    _m09[1] + ' Pair nonoverlapping chronological executions per side: hold one pending qualifying event; next strictly later qualifying event within 120 seconds and <=2 ticks forms a zone and consumes both, otherwise replace pending. For a complete timestamp batch with >1 qualifying same-side execution, skip all that side events and log ambiguous formation counts; opposite-side singleton batches independently seed pending. Zones persist to16:00. Rearm requires new four-tick directional departure strictly after prior touch timestamp batch. Outcomes start strictly after touch batch; simultaneous opposing endpoints are unknown.',
    {**_m09[2], 'pairing':'nonoverlapping_chronological_per_side_single_pending', 'pair_success':'consume_both', 'pair_failure':'replace_pending_with_current', 'formation_batch_policy':'skip_all_same_side_qualifying_events_if_count_gt_1_log_ambiguity', 'opposite_side_same_timestamp':'independent_singletons', 'zone_expiry':'16:00', 'rearm_clock':'strictly_after_previous_touch_timestamp_batch', 'outcome_clock':'strictly_after_touch_timestamp_batch', 'simultaneous_opposing_endpoints':'unknown'},
    _m09[3], _m09[4])

for (method, branch), spec in SPECS.items():
    if method=='JJ-TBR' and branch in {'judas_reversal','extension_reaction'}: spec[2]['endpoint_policy']='next_aligned_close_only'
    if method=='SAINT-AMT' and branch in {'continuation_retest','trapped_buyers_retest'}: spec[2]['endpoint_policy']='first_later_retest_only'
    if method in {'SAINT-AMT', 'KEANI-OPEN-ABOVE-VALUE'}:
        spec[2]['action_start'] = '09:30'
        spec[2]['prior_rth_policy'] = 'immediately_preceding_weekday_same_contract_full_390_minutes; holidays_missing_without_trusted_closure'

for branch in BRANCHES['GB-FAIL']:
    params = {'trigger_minutes':1,'confirmation_minutes':5,'expiry':'16:00','reference_policy':'same_native_contract','strict_excursion':True,'strict_later_confirmation':True,'endpoint_policy':'next_aligned_close_only'}
    text = 'First strict native 1-minute cross per side/reference/session; score only the NEXT strictly later aligned complete 5-minute close back across reference before expiry; no later favorable close search.'
    if branch == 'nyam_box': params.update(reference_window=['09:00','10:00'],action_start='10:00')
    elif branch == 'previous_hour': params.update(reference='preceding_complete_clock_hour',action_hours=list(range(9,16)),earliest_action='09:30',expiry='following_hour_end')
    elif branch == 'prior_day_level': params.update(reference='previous_weekday_RTH',required_minutes=390,action_start='09:30',holiday_policy='missing_without_trusted_closure')
    elif branch in ('prior_week_level','prior_month_level'): params.update(reference='preceding_calendar_'+('week' if 'week' in branch else 'month'),required_session_minutes=390,require_all_weekdays=True,action_start='09:30',holiday_policy='missing_without_trusted_closure')
    elif branch == 'cash_open_reclaim_case': params.update(reference='09:30_native_minute_OPEN_known_at_minute_end',action_start='09:31',expiry='10:30',sides=['long'])
    elif branch == 'asia_tdo_case':
        params.update(reference_window=['20:00','00:00'],tdo='00:00_native_minute_OPEN_known_at_minute_end',action_start='00:01')
        text += ' Require reclaimed Asia edge and direction-consistent close across TDO; TDO is comparison minute-open, not observed source fill/tick.'
    else:
        params.update(endpoint_policy='first_postparent_gap_appearance',parent_branch='nyam_box',parent_population='every_confirmed_reclaim',confirmation_minutes=2,horizon_minutes=30,gap='wick_to_wick',pivot='preceding_two_complete_bars',all_three_candles_start_at_or_after_parent=True,earliest_candle_start='ceil_parent_completion_to_2m_grid',child_occurrence='parent_completion_instant',parent_identity='parent_opportunity_and_completion_ids')
        text = 'Each confirmed NYAM reclaim completion instant is a child opportunity carrying parent opportunity/completion IDs. Within 30 minutes, require three consecutive complete 2-minute candles all starting at/after parent completion (ceil to next aligned 2-minute boundary): third-candle wick gap beyond first and close beyond preceding two-bar high/low. First appearance passes; complete horizon without appearance fails; missing/gap unknown. This is not an entry; earlier November 20 sweep is not retimed.'
    SPECS[('GB-FAIL',branch)] = ('mss_fvg_after_reclaim' if branch=='mss_fvg_refinement' else 'reference_sweep_reclaim',text,params,'GB:31;GB:43;FORMULAS:M02', 'reclaim_parent' if branch=='mss_fvg_refinement' else 'reference_sweep')

LIMITS = {
 'JJ-TBR': 'Missing branch-specific preselected source context, admission and objective; proprietary EV/P-zone or other-session clock where required. Supplied examples remain auditable; comparison geometry does not supply these labels.',
 'GB-SCALP':'Case descriptions lack repeatable source-complete trigger, impulse, admission and invalidation; do not replace them with failure/VWAP trades.',
 'SIRES':'Missing source selected auction/thesis/band and branch-specific qualitative flow criteria; DOM/order identity, source CVD reference, fresh defense or gamma/KG1 where required.',
 'MEMBER-TWO-REASONS':'Missing independent prior-reaction and minor-HVN selection, profile window, confluence tolerance and current confirmation; arbitrary first HVN/prior extreme is not the source model.',
 'REFILL-STUDY':'Missing actual private model/grade, selected-order identity and order/fill ledger; public executions do not manufacture selection.',
 'JETBUNDLE-STATES':'Actual supplied state labels, classifier cadence/thresholds/priority and transition adjacency absent; no classifier training authorized.',
 'STOIC-DATA':'Process journal and declared process versions required; macro application additionally lacks custom series/vintages/C-score/cycle rules.',
 'STOIC-RISK':'Actual validated process, Monte Carlo inputs and risk-stage/position ledger absent; printed arithmetic is separately auditable.',
}
BRANCH_LIMITS = {
 ('SIRES','dom_rejection'):'Selected planned level and actual source DOM queue/rejection observations absent; trades alone do not recover standing depth.',
 ('SIRES','absorption_reward_retest'):'Source real-extreme selection, local absorption, own price reward and reward-retest qualification are absent; generic band touch is insufficient.',
 ('SIRES','stop_four_stage'):'Actual linked four-stage defense/replenishment/exhaustion/lift-off observations and source risk stage are absent.',
 ('SIRES','footprint_confirmed_reaction'):'Selected source candle/POC snapshot, local reaction and exact source footprint confirmation conventions are absent.',
 ('SIRES','ofm_aggressive'):'Source selected origin, catalyst/release, failure/refill and drive/retest episodes are absent; no generic impulse substitute.',
 ('SIRES','ofm_passive'):'Source selected origin and passive pullback/refill confirmation are absent; executed-only tape cannot reconstruct private passive order selection.',
 ('SIRES','clean_squeeze'):'Source clean-state and squeeze qualification, thesis and current flow criteria are unpublished.',
 ('SIRES','balance_failure_fade'):'Source gamma regime, selected balance and source aggression-failure confirmation are absent.',
 ('SIRES','defended_band_continuation'):'Actual selected continuation band and fresh same-band defense/current source confirmation are absent.',
 ('SIRES','microbalance_break'):'Actual selected small balance and larger thesis/strength are absent; source explicitly disallows universal fixed-clock box/run-detector substitution.',
 ('SIRES','kg1_retest'):'Proprietary source KG1/version and aggressive retest confirmation are absent; scenario gamma wall is not KG1.',
 ('JJ-TBR','judas_outbound'):'Actual source directional context and cash-open selection are absent; later path cannot select opening side or infer an entry.',
 ('JJ-TBR','single_extended'):'Unpublished extended-context classification and reduced-expectation source policy absent; midpoint path comparison is represented separately under internal_rotation.',
 ('JJ-TBR','single_purged'):'Required independently known purges, compressed-context selection and expansion policy absent; containment cannot substitute.',
 ('JJ-TBR','other_session'):'Actual source other-session formation/action clocks and source cleanliness selection absent.',
 ('JJ-TBR','timed_pzone_reversal'):'Source P-zone bounds/version/active policy and ordered source-to-destination path absent; engine is proprietary.',
}

def build_registry():
    rules, assumptions = [], []
    for method, branches in BRANCHES.items():
        for branch in branches:
            key = method, branch
            supported = key in SPECS
            rule_id = f'{method}:{branch}:comparison-v1' if supported else f'{method}:{branch}:disposition-v1'
            if supported:
                algorithm, readable, parameters, refs, unit = SPECS[key]
                assumption_id = 'A-' + METHOD_BY_ID[method] + '-' + branch.replace('_','-') + '-v1'
                assumptions.append({'assumption_id':assumption_id,'kind':'research_definition','rationale':'Observable deterministic comparison authorized by handoff; does not reconstruct missing private source selectors. Frozen without evaluation outcomes.','definition':readable,'parameters':parameters,'source_refs':refs.split(';')})
                ids = [assumption_id]
                status = 'supported_comparison'
            else:
                algorithm, readable, parameters, refs, unit, ids = 'unavailable', BRANCH_LIMITS.get(key,LIMITS.get(method,'Source-complete selector definition unavailable.')), {}, 'FORMULAS:'+METHOD_BY_ID[method], 'supplied_source_observation', []
                status = 'source_case_only' if method=='GB-SCALP' else 'supplied_only' if method in {'REFILL-STUDY','JETBUNDLE-STATES','STOIC-RISK'} else 'non_entry' if method=='STOIC-DATA' else 'unavailable_definition'
            rules.append({'rule_id':rule_id,'method_id':method,'branch':branch,'algorithm':algorithm,'parameters':parameters,'supported':supported,'status':status,'assumption_ids':ids,'evidence_mode':'research_comparison' if supported else 'source_disposition','variant':'comparison' if supported else 'unavailable','faithful_eligible':False,'source_method_verdict':'unknown','source_refs':refs.split(';'),'readable_rule':readable,'observation_unit':unit,'transport_observation_unit':('opening_period_state' if method=='KEANI-OPEN-ABOVE-VALUE' else 'range_path' if key==('JJ-TBR','internal_rotation') else 'zone_touch' if key==('REFILL-STUDY','touch_record') else 'market_opportunity'),'instrument':'NQ native contracts only; same native instrument ID throughout; no MNQ transfer','session':'America/New_York, exact rule clocks; DST handled by timezone','initial_opportunity_trigger':readable.split(';')[0] if supported else None,'prerequisites':'Complete exact reference and trigger coverage, native identity, positive definition tick where needed; source private gates remain unknown.','availability_clocks':'int64 UTC nanoseconds; complete native minute OHLCV available at minute end; aggregate close plus all member availability; frozen reference known before use.','lifecycle':'Create initial opportunity before inspecting endpoint; separate immutable trigger and replay; no inferred orders/fills.','invalidation':'Known identity/clock violations reject record; observed endpoint failure follows fixed rule.','expiry':parameters.get('expiry','not_applicable'),'reentry':'No inferred discretionary reentry. Only explicitly rearmed M09 zone returns; otherwise at most one per rule/reference/side/session except each completed prior-hour reference.','deduplication':'rule_id + registry_sha256 + partition_id + native instrument_id + reference_id + side + trigger interval; deterministic stable ID','exclusions':'Source/calibration dates and previously exposed dates per frozen split; incomplete required reference/action coverage; no synthetic fixtures in historical n.','required_data':['native_1m_OHLCV','native_instrument_definitions'] + (['native_executed_trades_with_aggressor'] if method in {'REFILL-STUDY','KEANI-OPEN-ABOVE-VALUE'} or (method=='SAINT-AMT' and branch!='continuation_retest') else []),'unknown_handling':'Missing coverage and unresolved same-bar ordering remain unknown/censored; never encode unavailable or unscanned as completed zero. Fully observed absent endpoint fails unless explicit unresolved-state policy says unknown.','denominators':{'opportunities':'All initial triggers, independently of later endpoint; M08 every eligible opening.','selected_signals':'Passing comparison endpoints only; nested subset, no private selection.','attempts_orders_fills':'Unavailable without actual ledgers, never inferred.','rates':'n=p+f; N=p+f+u; [p/N,(p+u)/N], null for N=0; no source win-rate claim.'}})
    extra_units = []
    for method, predicates in EXTRA_PREDICATES.items():
        for predicate in predicates:
            extra_units.append({'unit_id':f'{method}:{predicate}:observation-v1','method_id':method,'observation_unit':predicate,'supported':False,'status':'supplied_only','reason':'Actual linked source process/position/decision/state records are indispensable; preserve separately from market opportunities and never infer from later prices.','source_refs':['FORMULAS:'+METHOD_BY_ID[method]],'n':None})
    doc = {'schema':'phase1-empirical-registry-v1','version':REGISTRY_VERSION,'freeze_status':'draft','evaluation_exposure':'No evaluation outcomes viewed for this rule design; root must freeze with split/run identity before replay.','scope':'Existing 50 catalog branches and separate process/state/risk/management/reentry units; no new entry strategies.','rules':rules,'assumptions':assumptions,'extra_observation_units':extra_units,'input_identities':input_identities(),'source_case_registry':'implementation/src/trading_research/research/method_pack/source_cases_v2.json','review':'implementation/reports/phase1-live/empirical/registry/RULE_DESIGN_REVIEW.md'}
    doc['registry_sha256'] = canonical_hash(doc)
    return doc

def _exact_shape(actual, expected, label):
    """Equality including scalar/container types: bool is not an integer."""
    if type(actual) is not type(expected):
        raise ValueError(label + ': wrong type')
    if isinstance(expected, dict):
        if actual.keys() != expected.keys(): raise ValueError(label + ': fields differ')
        for key in expected: _exact_shape(actual[key], expected[key], label+'.'+key)
    elif isinstance(expected, list):
        if len(actual)!=len(expected): raise ValueError(label + ': length differs')
        for i, value in enumerate(expected): _exact_shape(actual[i], value, label+':'+str(i))
    elif actual != expected:
        raise ValueError(label + ': differs from versioned definition')


def _definition_paths(root='/workspace'):
    root = Path(root)
    package = root/'implementation/src/trading_research/research/method_pack'
    return [package/'catalog.py', package/'catalog_extract.json', package/'source_cases_v2.json', root/'planning/phase-1-live/FORMULAS.md'] + sorted((root/'planning/phase-1-live/wiki').glob('*.md'))


def _stat_signature(path):
    stat = Path(path).stat()
    return (str(path), stat.st_dev, stat.st_ino, stat.st_size, stat.st_mtime_ns, stat.st_ctime_ns)


def _definition_signature(root='/workspace'):
    # Detect additions/removals and content rewrites even with restored mtime.
    return tuple(_stat_signature(path) for path in _definition_paths(root))


@lru_cache(maxsize=512)
def _file_hash(signature):
    return sha256(Path(signature[0]).read_bytes()).hexdigest()


def input_identities(root='/workspace'):
    root = Path(root)
    return {Path(sig[0]).relative_to(root).as_posix():_file_hash(sig) for sig in _definition_signature(root)}


_VALIDATED_REGISTRIES = set()
_LOAD_CACHE = {}
_BATCH_REGISTRY = ContextVar('phase1_validated_registry_batch', default=None)

def _validate_source_refs(doc):
    catalog = json.loads(Path('/workspace/implementation/src/trading_research/research/method_pack/source_cases_v2.json').read_text())
    formulas = Path('/workspace/planning/phase-1-live/FORMULAS.md').read_text()
    recipe_ids = set(re.findall(r'^## ([MO]\d+) \u2014', formulas, re.MULTILINE))
    for record in doc['rules'] + doc['assumptions'] + doc['extra_observation_units']:
        refs = record.get('source_refs')
        if type(refs) is not list or not refs or len(set(refs))!=len(refs): raise ValueError('missing/duplicate source references')
        for ref in refs:
            if type(ref) is not str or ':' not in ref: raise ValueError('invalid source reference')
            source, page = ref.split(':',1)
            if source == 'FORMULAS':
                if page not in recipe_ids: raise ValueError('unknown FORMULAS recipe: '+ref)
            elif source not in catalog['sources'] or not page.isdigit() or not 1<=int(page)<=catalog['sources'][source]['pages']:
                raise ValueError('unknown source/page: '+ref)


def validate_registry(doc):
    if type(doc) is not dict: raise ValueError('registry must be object')
    if doc.get('schema') != 'phase1-empirical-registry-v1' or doc.get('version') != REGISTRY_VERSION:
        raise ValueError('unsupported registry schema/version')
    if doc.get('freeze_status') not in {'draft','frozen'} or doc.get('registry_sha256') != canonical_hash(doc):
        raise ValueError('registry freeze state/hash invalid')
    # This version has exact definitions, not an open parameter grid. Updating a
    # algorithm, assumption, status or data requirement requires a code/version
    # change and a fresh pre-outcome freeze or documented exposure revision.
    signature = _definition_signature()
    cache_key = (doc['registry_sha256'], signature)
    if cache_key in _VALIDATED_REGISTRIES: return doc
    expected = build_registry()
    for field in ('rules','assumptions','extra_observation_units','input_identities'):
        _exact_shape(doc.get(field), expected[field], field)
    _validate_source_refs(doc)
    if signature != _definition_signature(): raise ValueError('definitions changed during validation')
    _VALIDATED_REGISTRIES.add(cache_key)
    return doc

def load_registry(path=None):
    path = Path(path or DEFAULT_PATH).resolve()
    signature = (_stat_signature(path), _definition_signature())
    cached = _LOAD_CACHE.get(str(path))
    if cached is None or cached[0] != signature:
        doc = validate_registry(json.loads(path.read_text()))
        if signature != (_stat_signature(path), _definition_signature()):
            raise ValueError('registry/definitions changed during load')
        _LOAD_CACHE[str(path)] = signature, doc
    # Callers cannot poison the cached validated document by mutating a return.
    return copy.deepcopy(_LOAD_CACHE[str(path)][1])

@contextmanager
def validated_registry_batch(doc):
    """Validate an immutable bounded batch; publish only after clean exit.

    Private deep copy prevents caller mutation during assembly from changing
    per-record semantics. All definition files and this package's Python code
    are checked before/after; drift aborts the whole unpublished partition.
    """
    validate_registry(doc)
    private = copy.deepcopy(doc)
    if private['freeze_status'] != 'frozen': raise ValueError('batch requires frozen registry')
    definition_signature = _definition_signature()
    definitions = input_identities()
    if definitions != private['input_identities']:
        raise ValueError('definitions changed before batch snapshot')
    package = Path(__file__).parent
    def code_identity():
        return {str(path): sha256(path.read_bytes()).hexdigest() for path in sorted(package.rglob('*.py'))}
    code = code_identity()
    token = _BATCH_REGISTRY.set(private)
    try:
        yield copy.deepcopy(private)
    finally:
        _BATCH_REGISTRY.reset(token)
        if definition_signature != _definition_signature() or definitions != input_identities() or code != code_identity():
            raise ValueError('definitions/code changed during registry batch; discard unpublished batch')


def validate_comparison_candidate(candidate, registry=None, *, allow_draft=False):
    batch = _BATCH_REGISTRY.get()
    if batch is not None:
        if registry is not None and (type(registry) is not dict or canonical_hash(registry) != batch['registry_sha256'] or registry.get('registry_sha256') != batch['registry_sha256']):
            raise ValueError('candidate supplied registry differs from immutable batch')
        doc = batch
    else:
        doc = validate_registry(registry) if registry is not None else load_registry()
    if type(candidate) is not dict: raise ValueError('candidate must be object')
    if doc['freeze_status'] != 'frozen' and not (registry is not None and allow_draft is True):
        raise ValueError('candidate requires frozen registry; explicit draft fixtures require allow_draft')
    if type(allow_draft) is not bool: raise ValueError('allow_draft must be boolean')
    if candidate.get('registry_version') != doc['version'] or candidate.get('registry_sha256') != doc['registry_sha256']:
        raise ValueError('candidate registry identity mismatch')
    rule = next((r for r in doc['rules'] if r['rule_id']==candidate.get('rule_id')),None)
    if rule is None or not rule['supported']: raise ValueError('candidate unsupported rule')
    if candidate.get('method_id') != rule['method_id'] or candidate.get('branch') != rule['branch']: raise ValueError('candidate branch identity mismatch')
    ids = candidate.get('assumption_ids',[])
    if type(ids) not in (list,tuple) or any(type(i) is not str for i in ids) or len(ids)!=len(set(ids)) or set(ids)!=set(rule['assumption_ids']): raise ValueError('candidate assumption identity mismatch')
    if candidate.get('evidence_mode')!='research_comparison' or candidate.get('variant')!='comparison' or candidate.get('faithful_eligible') is not False:
        raise ValueError('candidate is not explicitly non-faithful comparison')
    if any(candidate.get(k) is not None for k in ('order_id','actual_fill','actual_selection','actual_attempt','trading_return','pnl')):
        raise ValueError('comparison cannot manufacture execution or profitability')
    return copy.deepcopy(rule) if batch is not None else rule

def write_registry(root='/workspace'):
    root=Path(root)
    out=root/'implementation/reports/phase1-live/empirical/registry'
    out.mkdir(parents=True,exist_ok=True)
    doc=validate_registry(build_registry())
    path=out/'CANDIDATE_REGISTRY.json'
    path.write_text(json.dumps(doc,indent=2,sort_keys=True)+'\n')
    lines=['# Candidate rules v'+doc['version'],'','Status: DRAFT. Freeze this registry and split/run manifest before inspecting evaluation outcomes.','', 'All supported rules are non-faithful research comparisons. Source method prerequisites remain unknown; observations are not trades.','', '| Method | Branch | Status | Rule |','|---|---|---|---|']
    for r in doc['rules']: lines.append(f"| {r['method_id']} | {r['branch']} | {r['status']} | {r['readable_rule']} |")
    lines += ['', '## Separate observation units','']
    for u in doc['extra_observation_units']: lines.append(f"- {u['unit_id']}: {u['status']}. {u['reason']}")
    lines += ['', 'Registry canonical body SHA-256: `'+doc['registry_sha256']+'`.', '', 'Every rule includes exact parameters, source/assumption references, clocks, lifecycle, exclusions, unknown handling and denominator definitions in CANDIDATE_REGISTRY.json. Changes after outcome exposure require a new version and explicit exposure record.']
    (out/'CANDIDATE_RULES.md').write_text('\n'.join(lines)+'\n')
    return doc
