"""Authoritative historical scanner dispatch, driven by branch coverage."""
from .catalog import BRANCHES, EXTRA_PREDICATES
from .historical_features import HistoricalFeatures
from .historical_price_scanners import scan_jumbo,scan_green_failure,scan_green_vwap
from .historical_flow import scan_sires
from .historical_auction_scanners import scan_saint,scan_member,scan_keani
from .historical_process_scanners import scan_scalp,scan_refill,scan_jetbundle,scan_stoic_data,scan_risk,scan_supplied_unit

FAMILY_SCANNERS={'JJ-TBR':scan_jumbo,'GB-FAIL':scan_green_failure,'GB-VWAP':scan_green_vwap,'GB-SCALP':scan_scalp,
    'SIRES':scan_sires,'SAINT-AMT':scan_saint,'MEMBER-TWO-REASONS':scan_member,'KEANI-OPEN-ABOVE-VALUE':scan_keani,
    'REFILL-STUDY':scan_refill,'JETBUNDLE-STATES':scan_jetbundle,'STOIC-DATA':scan_stoic_data,'STOIC-RISK':scan_risk}
SCANNERS={(method,branch):FAMILY_SCANNERS[method] for method,branches in BRANCHES.items() for branch in branches}


def extra_jumbo(m,branch):return scan_supplied_unit(m,'JJ-TBR',branch)
def extra_scalp(m,branch):return scan_supplied_unit(m,'GB-SCALP',branch)
def extra_sires(m,branch):return scan_supplied_unit(m,'SIRES',branch)
def extra_refill(m,branch):return scan_supplied_unit(m,'REFILL-STUDY',branch)
def extra_jet(m,branch):return scan_supplied_unit(m,'JETBUNDLE-STATES',branch)
def extra_stoic(m,branch):return scan_stoic_data(m,branch,extra=True)
EXTRA_FAMILIES={'JJ-TBR':extra_jumbo,'GB-SCALP':extra_scalp,'SIRES':extra_sires,'REFILL-STUDY':extra_refill,
    'JETBUNDLE-STATES':extra_jet,'STOIC-DATA':extra_stoic}
EXTRA_SCANNERS={(method,branch):EXTRA_FAMILIES[method] for method,branches in EXTRA_PREDICATES.items() for branch in branches}


def scan_branch(market,row):
    key=row['method_id'],row['branch']
    scanner=(EXTRA_SCANNERS if row['extra_unit'] else SCANNERS)[key]
    actual=scanner.__module__+':'+scanner.__name__
    if actual!=row['scanner']:raise ValueError('manifest scanner binding changed')
    result=scanner(market,row['branch'])
    result.update(coverage_id=row['coverage_id'],scanner=actual,source_definition=row['source_definition'],
        observation_unit=row['observation_unit'],assumption_ids=row['assumption_ids'])
    return result


def run_method(method_id,market,manifest):
    from .branch_coverage import validate_manifest
    validate_manifest(manifest)
    rows=[r for r in manifest['branches'] if r['method_id']==method_id]
    if not rows:raise ValueError('method not in selected coverage manifest')
    return [scan_branch(market,row) for row in rows]
