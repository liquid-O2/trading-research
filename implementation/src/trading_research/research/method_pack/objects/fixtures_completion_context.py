"""Identified synthetic records for context and process fixture obligations.

These remain printed-algebra fixtures, separate from native coverage evidence.
Expected arithmetic is specified here independently of the recipe result.
"""
from decimal import Decimal as D


def prior_validation_record(known_at, use_at, *, n=100, include_mc=True):
    sample=[{'sample_id':f'closed-{i}', 'process_id':'process', 'process_version':'v1',
             'outcome':'win' if i<55 else 'loss', 'closed_at':known_at-200+i,
             'known_at':known_at-200+i} for i in range(n)]
    record={'n':n,'min_n':100,'process_id':'process','process_version':'v1',
            'validation_id':'validation-before-risk','sample':sample,
            'win_rate':D('0.55'),'avg_rr':D(2),
            'win_rate_definition':'closed wins / closed win-loss sample',
            'average_rr_definition':'supplied original-R reward/risk observation',
            'known_at':known_at,'use_at':use_at}
    if include_mc:
        record['monte_carlo']={'max_loss_streak':8,'known_at':known_at,
            'design':{'kind':'supplied illustrative permutation record', 'generated_by_this_run':False},
            'source_ref':'synthetic-fixture:supplied-MC-result','result_id':'mc-1',
            'process_id':'process','process_version':'v1','sample_ids':[r['sample_id'] for r in sample]}
    return record


def install(fixtures):
    for spec in fixtures:
        rid,fid,inp,expected=spec['recipe'],spec['id'],spec['inputs'],spec['expected']
        if rid=='O030':
            inp['coverage_complete']=True
        elif rid=='O031':
            inp.update(basis='trade_price',instrument_id='fixture-contract',canonical_tape_id='owned-trades',
                       coverage_complete=True,anchor_id='swing',anchor_selected_at=inp['anchor_known_at'],
                       anchor_reason='identified synthetic swing confirmed by second observation')
            for i,row in enumerate(inp['trades']):row['event_id']=f'{fid}:trade:{i}'
        elif rid=='O032':
            inp.update(band_id=f'{fid}:band',parent_snapshot_id='vwap-prior',
                       vwap_known_at=inp['known_at'],sigma_known_at=inp['known_at'])
        elif rid=='O034':
            # The old date literal was September while its actual timestamp
            # was January. The actual observation clock now determines 0DTE.
            from ..clocks import ns_to_et
            from datetime import timedelta
            observed=ns_to_et(inp['known_at']).date()
            expiry=observed if fid=='O034-F1' else observed+timedelta(days=3)
            inp.update(expiry=expiry.isoformat(),observation_at=inp['known_at'],right='C',
                       option_class='QQQ',osi_symbol=f'QQQ {expiry:%y%m%d}C00500000',unit='QQQ_points')
        elif rid=='O041':
            # A false case has two observed reasons sharing one identity.
            # Merely omitting a reason is unknown, not a false observation.
            duplicate=fid.endswith('F1b')
            inp['reason_records']=[
                {'role':'prior_reaction','object_id':'reaction', 'evidence_ids':['reaction-observation'],
                 'known_at':inp['known_at'],'band':[100,101]},
                {'role':'minor_hvn','object_id':'reaction' if duplicate else 'minor-hvn',
                 'evidence_ids':['hvn-profile-row'],'known_at':inp['known_at'],'band':[100,101]}]
        elif rid=='O044':
            inp.update(near_name='VIX9D',far_name='VIX',unit='percentage_points',operation='both',
                       near_known_at=inp['known_at'],far_known_at=inp['known_at'])
        elif rid=='O045' and fid.endswith('F1b'):
            expected.update(usable=None,base_ok=False,available_vvix=None)
        elif rid=='O153':
            inp.update(process_id='process',process_version='v1',cohort_id='ten-closed',closed_denominator='win_loss',
                       supplied_summary_ref='synthetic-fixture:reported-summary',
                       initial_R_provenance={'definition_id':'initial-R','known_at':inp['known_at']-1,'unit':'initial_R'})
        elif rid=='O154':
            inp.update(prior_validation_record(inp['known_at'],inp['use_at'],n=inp.get('n',100),include_mc=not fid.endswith('mc-hole')))
            if fid.endswith('mc-hole'):
                expected['hole_ids']=['HOLE:O154:supplied_mc_design_and_result']
        elif rid=='O162':
            inp.update(series_id='fixture-series',reference_period='2026-03',vintage_policy=inp.get('vintage_policy','latest_available'))
            for i,row in enumerate(inp['releases']):
                row.update(series_id='fixture-series',reference_period='2026-03',available_at=row['at'],
                           released_at=row['at'],unit='index_points',vintage_id=f'vintage-{i}',release_id=f'release-{i}')
        elif rid=='O163':
            inp['coverage_complete']=True
        elif rid=='O164':
            end=inp['known_at'];response=0 if fid.endswith('F1b') else 1
            inp.update(start_ns=end-2,end_ns=end,side='long',effort_side='total',response_basis='trade_price',
                       instrument_id='fixture-contract',instrument_tick_size=D('.25'),coverage_complete=True,
                       events=[{'event_id':'first','t':end-2,'price':100,'size':40,'side':'B','instrument_id':'fixture-contract'},
                               {'event_id':'last','t':end-1,'price':100+response,'size':60,'side':'A','instrument_id':'fixture-contract'}])
            expected.update(aggressive_volume=D(100),price_response_points=D(response),
                            price_response_ticks=D(response)*4,response_record_complete=True)
