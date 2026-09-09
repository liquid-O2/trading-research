"""Preserved full-history order reducer from the registered pre-E0 snapshot.

This remains independent of the transaction/prefix optimization. It is used
as a deterministic reference for the exact order/account state transitions.
Original source SHA-256: 10f768aef2f6ef6d55579a6ee9300f667f28d57574c8fdc640ad78bdef5602c6
"""

from trading_research.errors import IntegrityError
from trading_research.execution.orders import OrderSpec, BrokerEvent


def reduce_order_history(events):
    orders={};executions={};position={};position_parents={};incidents=[];broker_truth=None;last_known=None;unprotected=[];unprotected_since=None
    for event in events:
        p=event['payload'];kind=event['kind']
        if kind=='order_submitted':
            spec=OrderSpec(**p['spec']);orders[spec.client_id]={'spec':spec,'state':'sent','filled':0,'broker_id':None}
            at=spec.submitted_at
        elif kind=='broker_event':
            message=BrokerEvent(**p['event']);at=message.known_at;o=orders[message.client_id];spec=o['spec']
            if message.kind=='fill':
                identity=(spec.client_id,spec.instrument,spec.side,message.filled_quantity,message.fill_ticks,message.event_at)
                if message.execution_id in executions:
                    if executions[message.execution_id]['identity']!=identity:raise IntegrityError("execution identity reused with contradictory content")
                else:
                    executions[message.execution_id]={'identity':identity,'known_at':message.known_at,'evidence_version':message.evidence_version}
                    previous_position=position.get(spec.instrument,0)
                    o['filled']+=message.filled_quantity;position[spec.instrument]=previous_position+spec.side*message.filled_quantity;o['state']='filled' if o['filled']>=spec.quantity else 'partially_filled'
                    if position[spec.instrument]==0:position_parents.pop(spec.instrument,None)
                    elif previous_position==0 and spec.role=='entry' and abs(position[spec.instrument])==1:
                        position_parents[spec.instrument]=spec.client_id
                    elif abs(position[spec.instrument])!=1 or previous_position*position[spec.instrument]<0:
                        position_parents[spec.instrument]=None
                    if o['filled']>spec.quantity:incidents.append({'at':at,'kind':'overfill','order':spec.client_id,'actual':o['filled']})
                    # OCO cancellation is a separate observation, never inferred here.
                    if spec.role!='entry' and position[spec.instrument]*spec.side>0:incidents.append({'at':at,'kind':'exit_reversed_position','order':spec.client_id})
            elif message.kind in ('acknowledged','working'):
                if o['state'] not in ('filled','cancelled','rejected','closed_by_reconciliation'):o['state']='working'
            elif message.kind=='cancel_requested':
                if o['state'] not in ('filled','cancelled','rejected','closed_by_reconciliation'):o['state']='cancel_pending'
            elif message.kind=='cancelled':
                if o['state']!='filled':o['state']='cancelled'
            elif message.kind=='rejected':
                if o['filled']:incidents.append({'at':at,'kind':'rejection_after_fill','order':spec.client_id})
                else:o['state']='rejected'
            elif message.kind=='cancel_rejected':
                if o['state'] not in ('filled','cancelled','rejected'):o['state']='unknown'
            elif o['state'] not in ('filled','cancelled','rejected','closed_by_reconciliation'):o['state']='unknown'
        elif kind=='broker_reconciliation':
            at=p['known_at'];broker_truth=p
            if not p['open_orders_complete'] or not p['execution_history_complete']:
                incidents.append({'at':at,'kind':'incomplete_broker_reconciliation'})
            else:
                truth={k:v for k,v in p['positions'].items() if v};local={k:v for k,v in position.items() if v}
                unknown=set(p['open_order_ids'])-set(orders)
                if truth!=local:incidents.append({'at':at,'kind':'position_discrepancy','local':local,'broker':truth})
                if unknown:incidents.append({'at':at,'kind':'unknown_broker_orders','orders':sorted(unknown)})
                if truth==local and not unknown:
                    for id,o in orders.items():
                        if id in p['open_order_ids']:
                            if o['state'] in ('filled','cancelled','rejected'):incidents.append({'at':at,'kind':'terminal_order_still_working','order':id})
                            else:o['state']='working'
                        elif o['state'] in ('sent','working','unknown','cancel_pending','partially_filled'):o['state']='closed_by_reconciliation'
        else:continue
        last_known=at
        actual={k:v for k,v in position.items() if v}
        if sum(abs(v) for v in actual.values())>1:incidents.append({'at':at,'kind':'one_mini_exposure_breach','positions':actual})
        protected=(len(actual)==1 and any(o['state']=='working' and o['spec'].role=='protective_stop' and o['spec'].instrument in actual and o['spec'].side==-actual[o['spec'].instrument] for o in orders.values()))
        if actual and not protected and unprotected_since is None:unprotected_since=at
        elif (not actual or protected) and unprotected_since is not None:
            unprotected.append((unprotected_since,at));unprotected_since=None
    live={id:o for id,o in orders.items() if o['state'] in ('sent','working','unknown','cancel_pending','partially_filled')}
    complete=bool(broker_truth and broker_truth['open_orders_complete'] and broker_truth['execution_history_complete'] and broker_truth['known_at']==last_known)
    reconciled=complete and {k:v for k,v in broker_truth['positions'].items() if v}=={k:v for k,v in position.items() if v} and set(broker_truth['open_order_ids'])==set(live)
    hard_incidents=[i for i in incidents if i['kind'] in ('overfill','exit_reversed_position','one_mini_exposure_breach','rejection_after_fill')]
    return {'orders':orders,'executions':executions,'positions':position,'position_parent_ids':position_parents,'live_orders':tuple(live),'incidents':incidents,
            'broker_truth':broker_truth,'last_known_at':last_known,'reconciled':reconciled,
            'entry_allowed':reconciled and not live and not any(position.values()) and not hard_incidents,
            'observed_unprotected_intervals':tuple(unprotected),'unprotected_since':unprotected_since,
            'unprotected_clock_basis':'local availability of broker observations; not a claim of exact venue interval'}

