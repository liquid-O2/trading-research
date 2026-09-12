"""Narrow native semantic bindings for explicitly registered comparisons.

Only numeric/availability roles listed here are admitted. Source directional
context, entry decisions, source VWAP verification, risk and execution fields
are never produced by these comparison definitions.
"""
from datetime import date, timedelta

from .empirical_market import clock
from .empirical_registry import validate_comparison_candidate
from .semantic_views import ROLES


def validate_role(role,obj,candidate):
    rule=validate_comparison_candidate(candidate)
    if role.get('registry_sha256')!=candidate['registry_sha256'] or role.get('rule_id')!=rule['rule_id']:
        raise ValueError('research semantic role has foreign registry identity')
    setting=role.get('source_definition',{})
    if setting.get('status')!='inference' or set(setting.get('source_refs',[]))!=set(rule['assumption_ids']):
        raise ValueError('research semantic role must retain its exact assumption identity')
    value=setting.get('value',{})
    day=date.fromisoformat(candidate['session_date_et'])
    method=candidate['method_id'];name=role.get('role')
    if method=='JJ-TBR' and name=='source_range' and obj['recipe_id']=='O005':
        bounds=clock(day,'06:00'),clock(day,'09:00')
    elif method=='GB-VWAP' and name in {'asia','london'} and obj['recipe_id']=='O046':
        bounds=(clock(day-timedelta(days=1),'20:00'),clock(day,'00:00')) if name=='asia' else (clock(day,'02:00'),clock(day,'05:00'))
    elif method=='GB-VWAP' and name=='breakout_candle' and obj['recipe_id']=='O004':
        end=candidate['decision_at']
        bounds=end-60_000_000_000,end
        if not clock(day,'05:00')<end<=clock(day,'16:00'):
            raise ValueError('comparison breakout outside frozen action clock')
    else:
        raise ValueError('unregistered research semantic role')
    if (obj['formation_start'],obj['formation_end'])!=bounds or (value.get('formation_start'),value.get('formation_end'))!=bounds:
        raise ValueError('research role differs from frozen rule formation')
    if value.get('role')!=name or value.get('session_date_et')!=str(day):
        raise ValueError('research role has foreign session or role')
    if obj.get('known_at') is None or obj['known_at']>candidate['decision_at']:
        raise ValueError('research native role unavailable at use')
    obj['source_role_comparison']=True
    return value


def selected_bindings(rule,objects,candidate):
    roles=[];bindings={}
    for obj in objects:
        fields=[]
        if rule['method_id']=='JJ-TBR' and obj['recipe_id']=='O005':
            fields=['range_frozen','range_known_at']
        elif rule['method_id']=='GB-VWAP':
            if obj['recipe_id']=='O004':fields=['breakout_close','breakout_at']
            elif obj['recipe_id']=='O046':
                # Actual dated formation, not nearest price, distinguishes the
                # two independent session roles.
                day=date.fromisoformat(candidate['session_date_et'])
                if obj['formation_end']==clock(day,'00:00'):fields=['asia_high','asia_known_at']
                elif obj['formation_end']==clock(day,'05:00'):fields=['london_high','london_known_at']
        for field in fields:
            bindings[field]={'object_id':obj['object_id']}
            role_name=ROLES[rule['method_id'],field]
            if any(r['object_id']==obj['object_id'] and r['role']==role_name for r in roles):continue
            roles.append({'object_id':obj['object_id'],'role':role_name,'method_id':rule['method_id'],
                'instrument_id':candidate['instrument_id'],'author':obj['author'],
                'registry_sha256':candidate['registry_sha256'],'rule_id':rule['rule_id'],
                'source_definition':{'status':'inference','source_refs':list(rule['assumption_ids']),
                    'reason':'Frozen observable research role; full source admission remains unknown.',
                    'value':{'role':role_name,'session_date_et':candidate['session_date_et'],
                             'formation_start':obj['formation_start'],'formation_end':obj['formation_end']}}})
    return bindings,roles
