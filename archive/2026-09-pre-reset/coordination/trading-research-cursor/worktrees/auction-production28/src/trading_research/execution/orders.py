"""Durable simulated broker-event reducer; no network or live adapter.

Broker observations are retained even when they reveal excess exposure. A cancel
request, timeout or OCO sibling event never substitutes for confirmed broker truth.
"""

from dataclasses import asdict,dataclass
from copy import deepcopy
from pathlib import Path

from trading_research.errors import ContractError,IntegrityError
from trading_research.foundations.time import timestamp
from trading_research.operations.artifacts import digest
from trading_research.operations.journal import Journal


@dataclass(frozen=True)
class OrderSpec:
    client_id:str
    account_id:str
    instrument:str
    side:int
    quantity:int
    role:str
    order_type:str
    price_ticks:int|None
    submitted_at:int
    expires_at:int
    authorization_version:str
    oco_group:str|None=None
    parent_id:str|None=None

    def __post_init__(self):
        timestamp(self.submitted_at);timestamp(self.expires_at)
        if not all((self.client_id,self.account_id,self.instrument,self.authorization_version)) or type(self.side) is not int or self.side not in (-1,1) or type(self.quantity) is not int or self.quantity!=1:
            raise ContractError("primary order authorization is one mini in one account")
        if self.role not in ('entry','protective_stop','target','full_exit') or self.order_type not in ('market','limit','stop_market','stop_limit') or self.expires_at<=self.submitted_at:
            raise ContractError("invalid order role/type/original expiry")
        if self.order_type!='market' and type(self.price_ticks) is not int:raise ContractError("priced/trigger order needs exact tick geometry")
        if self.role=='protective_stop' and self.order_type not in ('stop_market','stop_limit'):
            raise ContractError("protective stop role requires an actual stop order type")


@dataclass(frozen=True)
class BrokerEvent:
    event_id:str
    client_id:str
    kind:str
    event_at:int
    known_at:int
    evidence_version:str
    execution_id:str|None=None
    filled_quantity:int=0
    fill_ticks:int|None=None
    reason:str='broker observation'

    def __post_init__(self):
        timestamp(self.event_at);timestamp(self.known_at)
        if not all((self.event_id,self.client_id,self.evidence_version,self.reason)) or self.kind not in ('acknowledged','working','fill','cancel_requested','cancelled','cancel_rejected','rejected','timeout'):
            raise ContractError("broker message requires raw evidence, clocks and registered event type")
        if self.kind=='fill':
            if not self.execution_id or type(self.filled_quantity) is not int or self.filled_quantity<=0 or type(self.fill_ticks) is not int:
                raise ContractError("fill needs execution identity, actual integer quantity and exact price")
        elif self.execution_id is not None or self.filled_quantity or self.fill_ticks is not None:
            raise ContractError("non-fill message cannot mutate economic fills")


class OrderLedger:
    def __init__(self,path:Path,*,account_id:str):
        if not account_id:raise ContractError("order ledger needs one account")
        self.account_id=account_id;self.journal=Journal(path)
        self._transaction_reduction = None
        self.journal.append(key='account-contract',kind='order_account',payload={'account_id':account_id,'adapter':'simulated-and-replayed-broker-evidence-only'})

    def _reduce(self,events):
        # Within an explicit bounded journal import, SQLite holds the write
        # lock and Journal has already verified the immutable prefix. Reuse
        # only that transaction's exact hash prefix. Ordinary reads continue
        # to verify and reduce the entire durable history.
        transaction = self.journal._transaction
        cached = self._transaction_reduction
        start = 0
        if (transaction is not None and cached is not None and cached[0] is transaction
                and len(events) >= len(cached[1])
                and tuple(event.get('hash') for event in events[:len(cached[1])]) == cached[1]):
            start = len(cached[1]); saved = cached[2]
            orders = {key: dict(value) for key, value in saved['orders'].items()}
            executions = {key: dict(value) for key, value in saved['executions'].items()}
            position = dict(saved['position']); position_parents = dict(saved['position_parents'])
            incidents = deepcopy(saved['incidents']); broker_truth = saved['broker_truth']; last_known = saved['last_known']
            unprotected = list(saved['unprotected']); unprotected_since = saved['unprotected_since']
            active = set(saved['active']); protection = set(saved['protection']); created = dict(saved['created'])
        else:
            orders={};executions={};position={};position_parents={};incidents=[];broker_truth=None;last_known=None;unprotected=[];unprotected_since=None
            active=set();protection=set();created={}
        live_states = ('sent','working','unknown','cancel_pending','partially_filled')
        def index_order(identity):
            order = orders[identity]
            if order['state'] in live_states: active.add(identity)
            else: active.discard(identity)
            if order['state']=='working' and order['spec'].role=='protective_stop': protection.add(identity)
            else: protection.discard(identity)
        for event in events[start:]:
            p=event['payload'];kind=event['kind']
            if kind=='order_submitted':
                spec=OrderSpec(**p['spec']);orders[spec.client_id]={'spec':spec,'state':'sent','filled':0,'broker_id':None}
                created[spec.client_id]=len(created);index_order(spec.client_id)
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
                index_order(message.client_id)
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
                        relevant = active | set(p['open_order_ids'])
                        for id in sorted(relevant, key=created.__getitem__):
                            o=orders[id]
                            if id in p['open_order_ids']:
                                if o['state'] in ('filled','cancelled','rejected'):incidents.append({'at':at,'kind':'terminal_order_still_working','order':id})
                                else:o['state']='working'
                            elif o['state'] in ('sent','working','unknown','cancel_pending','partially_filled'):o['state']='closed_by_reconciliation'
                            index_order(id)
            else:continue
            last_known=at
            actual={k:v for k,v in position.items() if v}
            if sum(abs(v) for v in actual.values())>1:incidents.append({'at':at,'kind':'one_mini_exposure_breach','positions':actual})
            protected=(len(actual)==1 and any(orders[id]['spec'].instrument in actual and orders[id]['spec'].side==-actual[orders[id]['spec'].instrument] for id in protection))
            if actual and not protected and unprotected_since is None:unprotected_since=at
            elif (not actual or protected) and unprotected_since is not None:
                unprotected.append((unprotected_since,at));unprotected_since=None
        live={id:o for id,o in orders.items() if o['state'] in ('sent','working','unknown','cancel_pending','partially_filled')}
        complete=bool(broker_truth and broker_truth['open_orders_complete'] and broker_truth['execution_history_complete'] and broker_truth['known_at']==last_known)
        reconciled=complete and {k:v for k,v in broker_truth['positions'].items() if v}=={k:v for k,v in position.items() if v} and set(broker_truth['open_order_ids'])==set(live)
        hard_incidents=[i for i in incidents if i['kind'] in ('overfill','exit_reversed_position','one_mini_exposure_breach','rejection_after_fill')]
        if transaction is not None and all('hash' in event for event in events):
            self._transaction_reduction = (transaction, tuple(event['hash'] for event in events), {
                'orders': {key: dict(value) for key, value in orders.items()},
                'executions': {key: dict(value) for key, value in executions.items()},
                'position': dict(position), 'position_parents': dict(position_parents),
                'incidents': deepcopy(incidents), 'broker_truth': broker_truth, 'last_known': last_known,
                'unprotected': tuple(unprotected), 'unprotected_since': unprotected_since,
                'active': frozenset(active), 'protection': frozenset(protection), 'created': dict(created)})
        return {'orders':orders,'executions':executions,'positions':position,'position_parent_ids':position_parents,'live_orders':tuple(live),'incidents':incidents,
                'broker_truth':broker_truth,'last_known_at':last_known,'reconciled':reconciled,
                'entry_allowed':reconciled and not live and not any(position.values()) and not hard_incidents,
                'observed_unprotected_intervals':tuple(unprotected),'unprotected_since':unprotected_since,
                'unprotected_clock_basis':'local availability of broker observations; not a claim of exact venue interval'}

    def state(self):return self._reduce(self.journal.read())

    def submit(self,spec:OrderSpec):
        if spec.account_id!=self.account_id:raise ContractError("cross-account order")
        events=self.journal.read();old=next((e for e in events if e['key']=='order:'+spec.client_id),None)
        payload={'spec':asdict(spec)}
        if old:
            if digest(old['payload'])!=digest(payload):raise IntegrityError("client order ID reused with different intent")
            return
        state=self._reduce(events)
        if state['last_known_at'] is not None and spec.submitted_at<state['last_known_at']:raise ContractError("order submission backdated before current account truth")
        if spec.role=='entry' and not state['entry_allowed']:raise ContractError("one-mini entry requires reconciled flat, no pending/unknown exposure and no unresolved hard incident")
        if spec.parent_id is not None and spec.parent_id not in state['orders']:raise ContractError("contingent order has no parent entry")
        if spec.role!='entry':
            pos=state['positions'].get(spec.instrument,0)
            parent=state['orders'].get(spec.parent_id)
            if parent and (parent['spec'].role!='entry' or parent['spec'].instrument!=spec.instrument or parent['spec'].side!=-spec.side):
                raise ContractError("contingent child does not match its parent instrument and side")
            actual=pos==-spec.side and (parent is None or state['position_parent_ids'].get(spec.instrument)==spec.parent_id)
            contingent=bool(parent and parent['state'] in ('sent','working','unknown','cancel_pending','partially_filled') and parent['filled']<parent['spec'].quantity)
            if not actual and not contingent:
                raise ContractError("exit/protection lacks matching actual or contingent one-mini position")
        self.journal.append(key='order:'+spec.client_id,kind='order_submitted',payload=payload,expected_head=events[-1]['hash'],check_head=True)

    def observe(self,message:BrokerEvent):
        events=self.journal.read();old=next((e for e in events if e['key']=='broker:'+message.event_id),None);payload={'event':asdict(message)}
        if old:
            if digest(old['payload'])!=digest(payload):raise IntegrityError("broker delivery ID changed")
            return
        state=self._reduce(events)
        if message.client_id not in state['orders']:raise ContractError("unmapped broker event needs incident reconciliation before attribution")
        if state['last_known_at'] is not None and message.known_at<state['last_known_at']:raise ContractError("broker receipt clock regressed; preserve source event_at separately")
        # Validate candidate reduction before atomic publication, including execution id collision.
        self._reduce((*events,{'kind':'broker_event','payload':payload}))
        self.journal.append(key='broker:'+message.event_id,kind='broker_event',payload=payload,expected_head=events[-1]['hash'],check_head=True)

    def reconcile(self,*,id:str,known_at:int,positions:dict[str,int],open_order_ids:tuple[str,...],
                  open_orders_complete:bool,execution_history_complete:bool,evidence_version:str):
        timestamp(known_at)
        if not id or not evidence_version or any(type(v) is not int for v in positions.values()) or len(set(open_order_ids))!=len(open_order_ids):raise ContractError("broker reconciliation needs actual positions, complete flags and immutable evidence")
        events=self.journal.read();state=self._reduce(events)
        payload={'id':id,'known_at':known_at,'positions':positions,'open_order_ids':open_order_ids,'open_orders_complete':open_orders_complete,
                 'execution_history_complete':execution_history_complete,'evidence_version':evidence_version}
        old=next((e for e in events if e['key']=='reconcile:'+id),None)
        if old:
            if digest(old['payload'])!=digest(payload):raise IntegrityError("reconciliation identity changed")
            return
        if state['last_known_at'] is not None and known_at<state['last_known_at']:raise ContractError("older reconciliation cannot replace current truth")
        self.journal.append(key='reconcile:'+id,kind='broker_reconciliation',payload=payload,expected_head=events[-1]['hash'],check_head=True)
