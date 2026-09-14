"""Single branch/unit coverage manifest for discovery, replay and acceptance.

Definitions below are frozen operational research choices. They never mutate
the historical comparison registry or turn a source interpretation into an
author-exact numeric detector.
"""
from __future__ import annotations
from dataclasses import asdict
import importlib
import json
from pathlib import Path

from .catalog import BRANCHES, EXTRA_PREDICATES, METHOD_BY_ID, OBJECT_META, objects_for, PRIMARY
from .contracts import fields_for, sections
from .empirical_protocol import content_hash
from .native_resolution import file_digest

VERSION = '2.0.0'
ROOT = Path('/workspace')
METHOD_PAGES = {
    'JJ-TBR': 'jumbo-tbr', 'GB-FAIL': 'green-bird-failure', 'GB-VWAP': 'green-bird-vwap-continuation',
    'GB-SCALP': 'green-bird-directional-scalps', 'SIRES': 'sires-thesis-flow', 'SAINT-AMT': 'saint-amt',
    'MEMBER-TWO-REASONS': 'member-two-reasons', 'KEANI-OPEN-ABOVE-VALUE': 'keani-open-above-value',
    'REFILL-STUDY': 'refill-effect', 'JETBUNDLE-STATES': 'jetbundle-auction-states',
    'STOIC-DATA': 'stoic-data-engine', 'STOIC-RISK': 'stoic-asymmetric-compounding',
}

# Every threshold is consumed by code through this mapping. No outcome-driven
# replacement or per-year tuning is permitted in v2.
ASSUMPTIONS = {
 'event_population': {'id': 'A2-EVENT', 'value': 'owned_observed_executions',
    'reason': 'Measure recorded T events consistently on event time; completeness and unknown gaps remain separate. This is not a historical-feed-arrival or fill claim.'},
 'profile': {'id': 'A2-PROFILE', 'value': {'fraction': '.70', 'poc_tie': 'lowest', 'va_tie': 'both'},
    'reason': 'Freeze contiguous executed-volume value and deterministic ties; source profile platforms do not publish one universal setting.'},
 'balance': {'id': 'A2-BALANCE', 'value': {'pivot_bars': 2, 'bar_seconds': 300, 'alternating_pivots': 4,
    'edge_tolerance_fraction': '.25', 'max_width_prior_fraction': '.5'},
    'reason': 'A price-defined balance requires repeated alternating, confirmed boundary tests. No elapsed-time box alone selects a microbalance or source auction.'},
 'context': {'id': 'A2-CONTEXT', 'value': {'wide_ratio': '1', 'compression_ratio': '.5',
    'direction': 'last_completed_structure_and_preopen_displacement'},
    'reason': 'Compare completed overnight and 6–9 widths to the prior same-contract RTH width; wide means at least prior width, compressed at most half. These are minimal ordinal research choices, not author-exact labels.'},
 'flow': {'id': 'A2-FLOW', 'value': {'local_horizon_seconds': 120, 'effort_seconds': 5, 'reward_ticks': 3,
    'no_progress_ticks': 2, 'near_origin_ticks': 3, 'entry_distance_ticks': 2,
    'band_halfwidth_ticks': 2, 'thinning_fraction': '.5', 'minimum_effort_events': 2},
    'reason': 'Observe actual executions and completed depth-one updates at an already fixed band. Compare effort/pace against its immediately preceding equal-duration window. Preserve exact 2–4 tick STOP reward and distinct reward/retest; no hidden reserve or order identity inference.'},
 'imbalance': {'id': 'A2-IMBALANCE', 'value': {'ratio': '3', 'consecutive_rows': 3, 'zero': 'skip'},
    'reason': 'Fixed diagonal ratio and three adjacent native ticks for a research footprint stack. The source figure/wording disagreement remains a source limit, not a parameter search.'},
 'mss_fvg': {'id': 'A2-MSS-FVG', 'value': {'seconds': 120, 'horizon_minutes': 30},
    'reason': 'Retain a two-minute post-parent annotation unit, with three distinct aligned candles. It never delays the November 20 displayed sweep entry.'},
 'gb_sessions': {'id': 'A2-GB-CLOCK', 'value': {'asia': ['20:00', '00:00'], 'london': ['02:00', '05:00'],
    'vwap_reset': '18:00', 'reclaim_seconds': 300, 'action_end': '16:00'},
    'reason': 'Keep explicitly named operational Asia/London clocks where exact London settings are absent. Five-minute reclaim is used for the cited close variants, separately from the sweep-entry source case.'},
 'tbr_sessions': {'id': 'A2-TBR-CLOCK', 'value': {'main': ['06:00', '09:00'],
    'other': [['20:00','20:30'], ['00:00','00:30'], ['03:00','03:30'], ['09:30','10:00'], ['10:00','10:30'], ['12:00','12:30'], ['15:00','15:30']],
    'other_action_minutes': 60, 'confirmation_seconds': 180, 'outbound_end': '09:40'},
    'reason': 'TBR p.7 publishes all seven formations. The research action horizon and selected three-minute block confirmation are frozen choices; source personal signatures are not universal.'},
 'tbr_projection': {'id': 'A2-TBR-PROJ', 'value': {'exhaustion': '.5', 'extension': ['1.33','1.66'], 'internal': ['.25','.5','.75']},
    'reason': 'Named range geometry only. Reversal permits a strict shallow edge sweep; an exact exhaustion-depth touch is not mandatory. Extended targets stop at the range edge.'},
 'reaction': {'id': 'A2-REACTION-HVN', 'value': {'reaction_ticks': 4, 'hvn_radius_ticks': 2,
    'confluence_ticks': 2, 'target_r': '1.5'},
    'reason': 'A confirmed earlier reaction and a locally maximal volume node use disjoint observation windows and separate IDs. Two-tick confluence is an explicit scale choice. Member target follows prose; conflicting ticket/trailing states remain source limits.'},
 'keani_time': {'id': 'A2-KEANI-TIME', 'value': {'a_start': '09:30', 'a_end': '10:00', 'latest_break': '11:00'},
    'reason': 'Around 10:00 operationalized as completed A through 11:00. Opening above value only starts an observation; higher developing value, rejection, actual imbalance break and defended same-band retest are required.'},
 'refill': {'id': 'A2-REFILL', 'value': {'min_event_quantity': 100, 'min_events': 2, 'formation_seconds': 120,
    'span_ticks': 2, 'departure_ticks': 4, 'response_ticks': 4, 'horizon_minutes': 15},
    'reason': 'Retain the original nonoverlapping native large-execution pair study threshold and lifecycle. No threshold reduction, proprietary touch grader, selected order or fictional fills.'},
 'outcomes': {'id': 'A2-OUTCOME', 'value': {'horizon_minutes': 60, 'same_batch': 'unknown', 'costs': 'not_a_fill_model'},
    'reason': 'First observed target/structural invalidation after completed sequence, with preselected objective. Missing future scope stays unknown. Endpoint observations are not profit or author trades.'},
 'risk': {'id': 'A2-STRUCTURAL-RISK', 'value': {'outside_structure_ticks': 1, 'default_size': None},
    'reason': 'One native tick beyond the observed invalidation structure makes the operational stop strictly outside. No account size, execution or author-exact stop is inferred.'},
 'auction_selection': {'id': 'A2-AUCTION-SAMPLE', 'value': {'primary': 'latest_confirmed_by_0930_else_first_confirmed_after',
    'contacts': 'first_distinct_per_side', 'vwap_deviation_sd': 1, 'saint_ltf_seconds': 60,
    'saint_value_fraction': '.68', 'control': 'two_successive_directional_body_and_delta_closes',
    'member_prior_split': '12:45', 'keani_fallback_objective': 'A_high_plus_A_width',
    'jet_observation': ['09:30','09:32']},
    'reason': 'Bounded deterministic auction observation: select the latest price-defined balance already known at the cash open, or the first subsequently confirmed one if none exists. Do not replace failed sequences with later favorable balances. VWAP tests use the first one-SD visit per side.'},
 'macro': {'id': 'A2-MACRO', 'value': {'release_as_availability': True, 'initial_only': True, 'standardization_prior_values': 12},
    'reason': 'Use already verified initial CPI/payroll BLS clocks only under explicit publication-as-availability assumption. Civil-date daily series do not acquire an invented intraday clock. Custom cycle/C-score rules remain separate.'},
}


def setting(name):
    return ASSUMPTIONS[name]['value']


# Source scope and the complete intended operation are distinct from measured
# outcomes and from the presence of an external selected-object/account input.
BRANCH_DEFINITIONS = {
 'JJ-TBR': {
  'judas_outbound': ('TBR pp.8–10', 'pre-open direction → 09:30 outbound → selected exhaustion → exit by reversal window'),
  'judas_reversal': ('TBR pp.8–11,27–29', 'frozen range/context → edge sweep → 09:40–09:50 block/rejection → opposing draw'),
  'single_extended': ('TBR pp.12–14,24', 'extended overnight → EQ/quadrant → directional confirmation → range-edge target/reduced expectation'),
  'single_purged': ('TBR pp.12–15', 'dated prior-liquidity purge → compressed range → internal contact/confirmation → expansion'),
  'internal_rotation': ('JR pp.3,38–43;TBR pp.12,24', 'wide balanced context → named internal → actual reversal signature → nearer named target'),
  'extension_reaction': ('TBR pp.20–21;JR pp.23–26,57', 'prior expansion → actual parent 1.33–1.66 projection → response → still-unused objective'),
  'other_session': ('TBR p.7,36;JR pp.46,50–51', 'one of seven published formations → fixed context/location → selected confirmation/risk/objective'),
  'timed_pzone_reversal': ('JR pp.16–18,53–55,58–62', 'dated supplied P-zone → contact → reversal → directed named destination')},
 'GB-FAIL': {b: ('GB pp.21,23,25,27,30–35,38–40,43', {
  'nyam_box':'finished 09–10 box → contextual sweep → five-minute reclaim → opposing box liquidity',
  'previous_hour':'finished prior clock-hour reference → contextual sweep → reclaim → opposing hour liquidity',
  'asia_tdo_case':'completed Asia range + midnight TDO → sweep → reclaim with TDO confirmation',
  'prior_day_level':'same-contract previous actual RTH reference → sweep/reclaim → selected opposing level',
  'prior_week_level':'same-contract prior-week matching sessions → sweep/reclaim → selected opposing level',
  'prior_month_level':'same-contract prior-month matching sessions → sweep/reclaim → selected opposing level',
  'cash_open_reclaim_case':'09:30 open → below-open manipulation → reclaim → retracement objective with low invalidation',
  'mss_fvg_refinement':'completed parent reclaim → later three 2-minute candles → MSS plus actual wick FVG; annotation unit'}[b]) for b in BRANCHES['GB-FAIL']},
 'GB-VWAP': {'source_long': ('GB p.33 posts 2026329904690712970/2026386393820283204', 'both finished session highs → close above → later contemporaneous VWAP return → long risk/continuation observation')},
 'GB-SCALP': {'bearish_small_scalp': ('GB p.40 post 2095257805242446135', 'pre-existing bearish direction → pullback → supplied small exposure and limited management; entry rule unpublished'),
               'bullish_discount_pullback': ('GB p.40 post 2098075540607410229', 'NYAM direction → selected impulse discount pullback → small exposure/process audit; entry rule unpublished')},
 'SIRES': {
  'dom_rejection': ('DOM6/DOM7 pp.3–7', 'planned level → arriving effort/no progress → depth-one defense/rejection'),
  'absorption_reward_retest': ('ABS pp.5–13', 'real extreme → opposing effort/passive defense → own reward near origin → distinct reward-area retest/fresh defense'),
  'stop_four_stage': ('STOP pp.10,12,14', 'real extreme → defense → replenishment → opposing print thinning → absorber aggression and 2–4 tick lift-off; account -4R checked separately'),
  'footprint_confirmed_reaction': ('FP9 pp.4–7', 'known level → same-candle delta disagreement/absorption → within-candle POC relocation → local flow'),
  'vwap_deviation_fade': ('VWAP pp.3–8', 'auction context → pre-touch executed VWAP/deviation → same-band absorption → local CVD/ladder confirmation'),
  'ofm_aggressive': ('OFM pp.3–13;BIG pp.7–14,18;CONT p.10', 'catalyst → release → failed squeeze → catalyst reclaim/refill → initiative/wicks → defended drive retest; source gamma retained separately'),
  'ofm_passive': ('OFM p.14', 'failed squeeze → dying tape/no aggressive failure → actual buyer area → trigger above buyers and stop below aggression'),
  'clean_squeeze': ('CONT p.11;OFM p.5', 'catalyst → fast release with no earlier failure → first pullback → opposing absorption → continuation'),
  'balance_failure_fade': ('BIG pp.14–15,18', 'balance extreme → unpaid aggression → leave → same-area retest still unpaid → prior opposite-control target; dated gamma input separate'),
  'defended_band_continuation': ('NYAM pp.4–5;K18 pp.7,11,14;CONT pp.4–10;ANAT p.7', 'prior band control → distinct current return → fresh same-side defense/refresh and executed aggression'),
  'microbalance_break': ('K2345 pp.4–7', 'larger direction → price-defined alternating-pivot microbalance → strength/break → stop behind that structure'),
  'kg1_retest': ('NYAM pp.8–9', 'dated source KG1 → actual same-band retest → aggressive confirmation → supplied management policy')},
 'SAINT-AMT': {
  'continuation_retest': ('RTVP pp.3–11;WIC pp.7–10', 'fitted HTF accepted balance → actual LTF balance break → same-boundary retest → repeated directional aggression'),
  'trapped_buyers_retest': ('TRAP pp.3–10;WIC pp.7–10', 'two distinct earlier upper buying failures → current LTF down break → same-boundary retest → repeated body selling'),
  'failed_auction_return': ('AMTL pp.8–10', 'original balance → distinct older value tested/rejected → original balance reacceptance → local control'),
  'poc_traversal': ('RTVP pp.5–8;AMTL pp.8–11', 'original balance reacceptance → aggressive POC passage → source hold → far-edge objective')},
 'MEMBER-TWO-REASONS': {'resistance_short': ('K10 pp.5–7,12', 'prior reaction + independently observed nearby minor HVN → current rejection → stop above rejection'),
                        'planned_return_long': ('K10 pp.6–8,12', 'planned prior structure + independent minor HVN → second/distinct return → buyers absorb/hold → structural stop')},
 'KEANI-OPEN-ABOVE-VALUE': {'source_long': ('AVG pp.21–22', 'whole A above prior VAH → higher developing value/rejection → aggressive VAH imbalance break → defended same-imbalance retest')},
 'REFILL-STUDY': {'touch_record': ('REF pp.5–9;OFM pp.15–18', 'large execution cluster → immutable zone → departure → distinct return with pre-touch memory → later label'),
                  'supplied_selected_order': ('REF p.12,16;OFM p.18', 'actual supplied model selection → 12/32/96 tick configuration → 30 minute cancel → one position → actual lifecycle/cost audit')},
 'JETBUNDLE-STATES': {b: ('MATH pp.4–11', 'native provide/withdraw/consume and response observations → supplied '+b+' label/qualitative criteria; no invented classifier') for b in BRANCHES['JETBUNDLE-STATES']},
 'STOIC-DATA': {'process_review': ('DATA pp.3–4', 'frozen declared process → uniform inclusion → all observations → winner/loser comparison → prior-sample revision'),
                'macro_application': ('DATA pp.5–6', 'actual vintage admission → selected indicator historical comparison → supplied custom cycle/C-score/trend interpretation')},
 'STOIC-RISK': {b: ('DATA pp.7–8', 'prior process/100+ sample and validation → printed '+b+' stage arithmetic; no historical ledger reconstructed') for b in BRANCHES['STOIC-RISK']},
}

EXTERNAL = {
 'pzone': {'operands': ['source_zone_known', 'zone_known_at'], 'citation': 'JR pp.16–18,53–55,58–62;O019',
    'required': 'dated source P-zone band ID, bounds, active state, generator version and named destination',
    'inspected': ['planning/phase-1-live/wiki/p-zones-benchmark.md','implementation/src/trading_research/research/method_pack/source_cases_v2.json'],
    'recovery': 'Source catalog contains case readouts/settings, not a historical 2020+ P-zone series or generator. Usage scanner accepts dated supplied bands; no approximate substitute.'},
 'kg1': {'operands': ['source_kg1_level_known', 'level_known_at'], 'citation': 'NYAM pp.8–9;K10 pp.4–6;O041',
    'required': 'dated source KG1 level/band, identity and version',
    'inspected': ['planning/phase-1-live/wiki/kg1-level.md','implementation/src/trading_research/research/method_pack/source_cases_v2.json'],
    'recovery': 'Retained source cases provide limited readouts; no historical generator/series. Existing options snapshots cannot establish proprietary KG1.'},
 'gamma': {'operands': ['short_gamma', 'long_gamma', 'branch_regime_allowed'], 'citation': 'BIG pp.14–18;GEX pp.4–20;O033–O040',
    'required': 'dated source dealer-map regime and selected native product/transform',
    'inspected': ['planning/phase-1-live/wiki/gex-regime.md','data/thetadata-opra','data/manifests'],
    'recovery': 'Local option contract/quote/OI data exist; they do not disclose author dealer positions or gamma-map formula. Observable OFM/fade stages run independently.'},
 'account': {'operands': ['daily_r_before', 'daily_limit_allows_entry'], 'citation': 'STOP pp.12,14;O140,O145,O150',
    'required': 'actual account/session closed R and active quantity/order ledger',
    'inspected': ['implementation/src/trading_research/research/method_pack/objects/lifecycles.py','implementation/src/trading_research/research/method_pack/source_cases_v2.json'],
    'recovery': 'Public market events and illustrated tickets are not a historical account ledger. The connected process interface audits supplied real records; market-stage measurement does not wait for them.'},
 'selection': {'operands': ['grade_model_frozen_before_touch', 'grade_available_at', 'touch_selected_without_future_information'],
    'citation': 'REF pp.8–9,12,16;OFM pp.15–18;O149', 'required': 'original frozen touch model/features/grade and selected order lifecycle',
    'inspected': ['planning/phase-1-live/wiki/touch-grader.md','planning/phase-1-live/wiki/order-lifecycle.md'],
    'recovery': 'Cited causal rebuild is negative; original classifier/normalization and private selections are unpublished. Native zone/return denominator remains separate.'},
 'state_label': {'operands': ['state', 'high_aggression', 'low_response_efficiency', 'low_aggression_both_sides'],
    'citation': 'MATH pp.9–11;O165–O166', 'required': 'dated actual B–A–D–E–W labels or published fully specified classifier/qualitative annotation records',
    'inspected': ['planning/phase-1-live/wiki/auction-state.md','planning/phase-1-live/wiki/auction-state-transition.md'],
    'recovery': 'Numeric source illustration does not publish classifier thresholds/priority. Native participation/efficiency runs; no classifier invented or trained.'},
 'macro_custom': {'operands': ['cycle_and_indicator_rules_recorded'], 'citation': 'DATA pp.5–6;O157–O161',
    'required': 'source custom indicator set/transforms, C-score/cycle/trend formula and historical interpretation',
    'inspected': ['implementation/reports/phase1-live/macro-backfill/verification.json','planning/phase-1-live/wiki/c-score.md'],
    'recovery': 'Existing 20-series/37003-vintage bundles are used directly; initial BLS clocks and specified standardized comparisons are available. Source proprietary transforms and non-initial intraday clocks are not supplied by that recovery.'},
 'scalp_process': {'operands': ['small_size_recorded', 'source_scalp_management_recorded'], 'citation': 'GB p.40;O140,O142,O150',
    'required': 'actual size/management record plus author entry detector if automatic admission is requested',
    'inspected': ['planning/phase-1-live/wiki/method-green-bird-directional-scalps.md'],
    'recovery': 'The two posts disclose directional pullback and small-exposure behavior, not a repeatable complete entry. Native directional/pullback observations and supplied process audit are connected separately.'},
 'validated_process': {'operands': ['validated_process', 'prior_sample_n', 'win_rate_known', 'average_rr_known', 'mc_loss_streak_known'],
    'citation': 'DATA pp.7–8;O154–O155', 'required': 'actual prior validated trade sample, win/RR metrics, Monte Carlo loss-streak result and stage ledger',
    'inspected': ['planning/phase-1-live/wiki/loss-streak-validation.md','planning/phase-1-live/wiki/asymmetric-risk-state.md'],
    'recovery': 'Printed first/second/reset arithmetic is available and executable. Neither the private prior sample nor Monte Carlo specification is present; a new simulation would not reconstruct it.'},
}


def external_for(method, branch, *, extra=False):
    keys = []
    if method == 'JJ-TBR' and branch == 'timed_pzone_reversal': keys += ['pzone']
    if method == 'SIRES':
        if branch == 'kg1_retest': keys += ['kg1']
        if branch in {'ofm_aggressive', 'balance_failure_fade'}: keys += ['gamma']
        if branch in {'stop_four_stage', 'reentry', 'management'}: keys += ['account']
    if method == 'GB-SCALP': keys += ['scalp_process']
    if method == 'REFILL-STUDY' and branch != 'touch_record': keys += ['selection', 'account']
    if method == 'JETBUNDLE-STATES': keys += ['state_label']
    if method == 'STOIC-DATA' and branch == 'macro_application': keys += ['macro_custom']
    if method == 'STOIC-RISK': keys += ['validated_process', 'account']
    if branch == 'management' and method == 'JJ-TBR': keys += ['account']
    return keys


def build_manifest():
    from .assembly import operand_inventory, producer_coverage_matrix
    from .objects.native_boundary import NATIVE_PRODUCERS, DERIVED_PRODUCERS
    from .protocol import RECIPES
    from .native_discovery import SCANNERS, EXTRA_SCANNERS
    rows = []
    for method, branches in BRANCHES.items():
        for branch, extra in [(b, False) for b in branches] + [(b, True) for b in EXTRA_PREDICATES.get(method, [])]:
            scanner = (EXTRA_SCANNERS if extra else SCANNERS).get((method, branch))
            if scanner is None or not callable(scanner):
                raise ValueError('branch/unit lacks a reachable scanner: ' + method + '/' + branch)
            source, operation = BRANCH_DEFINITIONS[method].get(branch, ('FORMULAS:' + METHOD_BY_ID[method], branch + ' process/management unit'))
            page = 'planning/phase-1-live/wiki/method-' + METHOD_PAGES[method] + '.md'
            bindings = [asdict(b) for b in operand_inventory(method) if branch in b.branches or extra]
            unit = ('process_record' if method in {'STOIC-DATA','STOIC-RISK'} else
                    'state_observation' if method == 'JETBUNDLE-STATES' else
                    'source_case_structure' if method == 'GB-SCALP' else
                    'zone_return' if method == 'REFILL-STUDY' and branch == 'touch_record' else
                    'selected_order' if method == 'REFILL-STUDY' else 'market_sequence')
            if extra: unit = branch
            rows.append({'coverage_id': method + ':' + ('unit:' if extra else 'branch:') + branch,
                'method_id': method, 'branch': branch, 'extra_unit': extra, 'observation_unit': unit,
                'source_definition': {'citation': source, 'wiki_path': page, 'operation': operation,
                    'knowledge': 'documented_process_partial_entry' if method in {'GB-SCALP','JETBUNDLE-STATES','STOIC-DATA','STOIC-RISK'} else 'documented_sequence'},
                'required_objects': sorted({rid for b in bindings for rid in b['producers']}),
                'operand_bindings': bindings, 'producer': scanner.__module__ + ':' + scanner.__name__,
                'scanner': scanner.__module__ + ':' + scanner.__name__,
                'implementation_state': 'reachable', 'required_inputs': ['identified event-time NQ window'] if unit in {'market_sequence','zone_return','source_case_structure','state_observation'} else ['dated typed process/source records'],
                'assumption_ids': [a['id'] for a in ASSUMPTIONS.values()],
                'input_limits': [dict(id=k, **EXTERNAL[k]) for k in external_for(method, branch, extra=extra)],
                'measured_results': {'status': 'not_evaluated', 'N': None, 'p': None, 'f': None, 'u': None}})
    expected = {(m,b,False) for m,bs in BRANCHES.items() for b in bs} | {(m,b,True) for m,bs in EXTRA_PREDICATES.items() for b in bs}
    if {(r['method_id'],r['branch'],r['extra_unit']) for r in rows} != expected or len(rows) != 58:
        raise ValueError('coverage manifest differs from 50 catalog branches and 8 extra units')
    matrix = producer_coverage_matrix()
    objects = []
    for rid in sorted(OBJECT_META):
        consumers = [r['coverage_id'] for r in rows if rid in r['required_objects']]
        producer = NATIVE_PRODUCERS.get(rid, DERIVED_PRODUCERS.get(rid, RECIPES.get(rid)))
        if producer is None:
            raise ValueError('object has no callable producer/interface: ' + rid)
        objects.append({'object_id': rid, 'name': OBJECT_META[rid]['name'], 'source_contract_sha256': content_hash(sections()[rid]),
            'producer': producer.__module__ + ':' + producer.__name__,
            'route': 'native' if rid in NATIVE_PRODUCERS else 'parent_derived' if rid in DERIVED_PRODUCERS else 'typed_source_or_process_interface',
            'historical_record_interface': 'historical_features:HistoricalFeatures.domain',
            'record_admission': 'identified object_observation record; actual recipe rerun; no registration-only measured claim',
            'native_execution_proof': 'reported separately from declared consumer membership in each completed job domain_observations',
            'consumers': consumers, 'source_contract': 'planning/phase-1-live/FORMULAS.md#' + rid.lower(),
            'bindings': [r['method_id'] + ':' + r['field'] for r in matrix if rid in r['producers']]})
    for binding in matrix:
        binding['historical_routes']=[{'coverage_id':r['coverage_id'],'scanner':r['scanner'],
            'interface':'historical_assembly:HistoricalEpisode.bind' if not r['extra_unit'] else 'assembly:read_assembled_manifest',
            'proof':'selected operand must be explicitly derived or explicitly missing; finish rejects an unbound field'}
            for r in rows if r['method_id']==binding['method_id'] and (r['branch'] in binding['branches'] or r['extra_unit'])]
        if not binding['historical_routes']:
            raise ValueError('operand has no historical or typed-record route: '+binding['field'])
    if len(objects) != 166 or len(matrix) != 373:
        raise ValueError('object/operand census differs from 166/373')
    doc = {'schema': 'phase1-branch-coverage-v2', 'version': VERSION, 'branches': rows,
           'objects': objects, 'operand_matrix': matrix, 'assumptions': ASSUMPTIONS,
           'source_catalog_sha256': file_digest(Path(__file__).with_name('source_cases_v2.json')),
           'source_contract_sha256': file_digest(ROOT / 'planning/phase-1-live/FORMULAS.md'),
           'counts': {'methods': 12, 'branches': 50, 'additional_units': 8, 'objects': 166, 'operands': 373}}
    doc['manifest_sha256'] = content_hash(doc)
    return doc


def validate_manifest(document):
    expected = document['manifest_sha256']
    body = {k:v for k,v in document.items() if k != 'manifest_sha256'}
    if content_hash(body) != expected:
        raise ValueError('branch coverage manifest mutated')
    membership={(m,b,False) for m,bs in BRANCHES.items() for b in bs}|{(m,b,True) for m,bs in EXTRA_PREDICATES.items() for b in bs}
    actual=[(r['method_id'],r['branch'],r['extra_unit']) for r in document['branches']]
    if set(actual)!=membership or len(actual)!=len(membership):
        raise ValueError('coverage manifest omits or duplicates a branch/unit')
    if {r['object_id'] for r in document['objects']}!=set(OBJECT_META) or len(document['objects'])!=166:
        raise ValueError('coverage manifest object membership differs')
    expected_fields={(m,f) for m in BRANCHES for f in fields_for(m)}
    if {(r['method_id'],r['field']) for r in document['operand_matrix']}!=expected_fields or len(document['operand_matrix'])!=373:
        raise ValueError('coverage manifest operand membership differs')
    for row in document['branches']:
        module, name = row['scanner'].split(':')
        if not callable(getattr(importlib.import_module(module), name, None)):
            raise ValueError('unreachable branch scanner')
    return document
