"""Independent full-prefix F10 fold over primitive retained JSON only.

No production imports, SQL indexes, support predicates or candidate builders.
This reference intentionally recomputes every latest object's support per view.
"""
from copy import deepcopy
import hashlib
import json


def _bytes(value):
    return json.dumps(value,sort_keys=True,separators=(',', ':'),ensure_ascii=False,allow_nan=False).encode('utf8')


def _hash(value):
    return hashlib.sha256(_bytes(value)).hexdigest()


def _identity(member):
    p,t = member['value'],member['type']
    if t=='EvidenceVersion': return p['version_id'],'evidence',p['source_id']
    if t=='AnchorVersion': return p['version_id'],'anchor',p['anchor_id']
    if t=='ObjectRevision': return p['version_id'],'object',p['object_id']
    if t=='ObservationEvent': return p['event_id'],'observation',p['event_id']
    if t=='RelationVersion': return p['version_id'],'relation',p['relation_id']
    if t=='Alias': return p['alias_id'],'alias',p['alias_id']
    if t=='Presentation': return p['view_id'],'presentation',p['view_id']
    raise ValueError('unknown literal member kind')


def _lineage(versions,relations,seeds,all_visits=(),events=()):
    kept,edges,links,visits={},set(),{},{}
    pending=list(seeds);owners=set()
    def visit(vid):
        if vid in visits:return
        value=next(v for v in all_visits if v['visit_id']==vid)
        visits[vid]=deepcopy(value);pending.append(value['start_geometry'])
        pending.extend(e['event_id'] for e in events if e['visit_id']==vid)
        pending.extend(r['version_id'] for r in relations if vid in (r['left']['id'],r['right']['id']))
    while pending:
        vid=pending.pop()
        if vid in kept:continue
        member=versions[vid];kept[vid]=deepcopy(member);p,t=member['value'],member['type']
        if t=='ObjectRevision':
            pending.extend(p['evidence_versions']);pending.extend(p['birth']['anchors'])
            if p['mapping_version']:pending.append(p['mapping_version'])
            for parent in p['parent_versions']:edges.add((parent,vid));pending.append(parent)
            if p['object_id'] not in owners:
                owners.add(p['object_id'])
                for v in all_visits:
                    if v['object_id']==p['object_id']:visit(v['visit_id'])
                pending.extend(k for k,m in versions.items() if m['type'] in {'Alias','Presentation'} and m['value']['object_id']==p['object_id'])
        elif t=='AnchorVersion':pending.extend(p['evidence_versions'])
        elif t=='ObservationEvent':pending.append(p['object_version']);pending.extend(p['evidence_versions']);visit(p['visit_id'])
        elif t in {'Alias','Presentation'}:
            owner=max((m['value'] for m in versions.values() if m['type']=='ObjectRevision' and m['value']['object_id']==p['object_id']),key=lambda o:o['revision'])
            pending.append(owner['version_id'])
        elif t=='RelationVersion':
            links[p['relation_id']]=deepcopy(member)
            for endpoint in(p['left'],p['right']):
                if endpoint['kind']=='visit':visit(endpoint['id'])
                else:pending.append(endpoint['id'])
            if p['kind'] in {'parent','split_parent','merge_parent','mapped_from'}:edges.add((p['left']['id'],p['right']['id']))
        pending.extend(r['version_id'] for r in relations if vid in(r['left']['id'],r['right']['id']))
    return {'lineage_versions':[kept[k] for k in sorted(kept)],'lineage_visits':[visits[k] for k in sorted(visits)],
            'parent_edges':[list(e) for e in sorted(edges)],'relations':[links[k] for k in sorted(links)]}


class LiteralObjectGraph:
    def __init__(self,journal,*,ttl_ns=None,visit_reset_policy='preserve'):
        self.journal=deepcopy(tuple(journal));self.ttl_ns=ttl_ns;self.visit_reset_policy=visit_reset_policy
        if visit_reset_policy not in {'preserve','reset_on_geometry_change'}:raise ValueError('unknown reset policy')
        self.last_object_evaluations=0;self.last_support_checks=0
        self.last_records_decoded=0;self.last_bytes_read=0
        previous=None;known=-(2**63)
        for sequence,record in enumerate(self.journal,1):
            material={'sequence':sequence,'key':record['key'],'known_at':record['known_at'],'payload':record['payload'],'previous':previous}
            if (record['sequence']!=sequence or record['previous']!=previous or _hash(material)!=record['hash'] or record['known_at']<known):
                raise ValueError('literal journal identity/hash/order mismatch')
            previous,known=record['hash'],record['known_at']

    def view(self,cut,*,instrument=None,cursor=None,_validate_controls=True):
        if type(cut) is not int or not -(2**63)<=cut<2**63:raise ValueError('literal cut must be int64')
        if cursor is not None and(type(cursor) is not int or not 0<=cursor<=len(self.journal)):raise ValueError('literal cursor outside journal')
        versions,heads,born,visits,observations,controls={},{},{},{},[],{}
        last_cursor=0;self.last_records_decoded=0;self.last_bytes_read=0;self.last_support_checks=0
        for row in self.journal:
            if row['known_at']>cut or(cursor is not None and row['sequence']>cursor):continue
            last_cursor=row['sequence'];self.last_records_decoded+=1;self.last_bytes_read+=len(_bytes(row['payload']))
            envelope=row['payload']
            if envelope['kind']!='batch':
                if envelope['id'] in controls and controls[envelope['id']]!=envelope:raise ValueError('literal control conflict')
                controls[envelope['id']]=deepcopy(envelope)
                continue
            batch=envelope['input']
            if len(batch['members'])!=batch['member_count']:raise ValueError('literal incomplete batch')
            for ordinal,member in enumerate(batch['members']):
                vid,kind,identity=_identity(member);p=deepcopy(member['value'])
                if vid in versions:
                    if versions[vid]!=member:raise ValueError('literal duplicate identity changed')
                    continue
                prior=heads.get((kind,identity))
                if kind=='object':
                    if prior is None:born[identity]=row['known_at']
                    elif p['birth']!=versions[prior]['value']['birth']:raise ValueError('literal birth changed')
                    terminal=p['existence'] in {'invalidated','expired','superseded'}
                    geometry_reset=(prior is not None and self.visit_reset_policy=='reset_on_geometry_change' and p['geometry']!=versions[prior]['value']['geometry'])
                    if terminal or geometry_reset:
                        for value in visits.values():
                            if value['object_id']==identity and value['state'] not in {'closed','reset'}:
                                value.update(state='reset',reset_at=p['known_at'],known_at=p['known_at'],
                                             reset_reason='lifecycle_'+p['existence'] if terminal else 'geometry_revision',member_ordinal=ordinal)
                elif kind=='observation':
                    parent=versions[p['object_version']]['value'];oid=parent['object_id'];old=visits.get(p['visit_id'])
                    if not p['source_order_known']:raise ValueError('unknown visit chronology')
                    if p['kind'] in {'enter','contact'}:
                        if old is not None or any(v['object_id']==oid and v['state'] not in {'closed','reset'} for v in visits.values()):raise ValueError('literal visit reopening')
                        visit={'visit_id':p['visit_id'],'object_id':oid,'ordinal':max((v['ordinal'] for v in visits.values() if v['object_id']==oid),default=0)+1,
                               'start_geometry':p['object_version'],'entered_at':p['event_at'],'state':'entered' if p['kind']=='enter' else 'contacted',
                               'known_at':p['known_at'],'last_event':p['event_id'],'last_event_at':p['event_at'],'reset_at':None,'reset_reason':None,'member_ordinal':ordinal}
                    else:
                        if old is None or old['state'] in {'closed','reset'} or p['predecessor_event']!=old['last_event'] or p['event_at']<old['last_event_at']:raise ValueError('literal orphan visit transition')
                        state={'exit':'closed','reset':'reset','sweep':'swept','reclaim':'reclaimed'}[p['kind']]
                        visit={**old,'state':state,'known_at':p['known_at'],'last_event':p['event_id'],'last_event_at':p['event_at'],
                               'reset_at':p['event_at'] if p['kind']=='reset' else None,'reset_reason':p['reason'] if p['kind']=='reset' else None,'member_ordinal':ordinal}
                    visits[p['visit_id']]=visit;observations.append(p)
                versions[vid]=deepcopy(member);heads[(kind,identity)]=vid
        relations=[versions[v]['value'] for(kind,_),v in heads.items() if kind=='relation' and not versions[v]['value']['tombstone']]
        relations.sort(key=lambda p:p['relation_id'])
        def support(obj,ancestry=()):
            self.last_support_checks+=1
            if obj['version_id'] in ancestry:raise ValueError('literal cyclic ancestry')
            ancestry=(*ancestry,obj['version_id'])
            evidence=set(obj['evidence_versions'])
            if obj['mapping_version']:evidence.add(obj['mapping_version'])
            for eid in sorted(evidence):
                ev=versions[eid]['value'];current_id=heads[('evidence',ev['source_id'])]
                if ev['support']!='observed':return False,'source_'+ev['support']
                if current_id!=eid:
                    current=versions[current_id]['value']
                    return False,'source_'+current['support'] if current['support']!='observed' else 'source_revision_pending'
            for avid in obj['birth']['anchors']:
                anchor=versions[avid]['value']
                if heads[('anchor',anchor['anchor_id'])]!=avid:return False,'anchor_revision_pending'
                for eid in anchor['evidence_versions']:
                    ev=versions[eid]['value']
                    if ev['support']!='observed' or heads[('evidence',ev['source_id'])]!=eid:return False,'anchor_source_pending'
            parents=set(obj['parent_versions'])
            parents.update(r['left']['id'] for r in relations if r['right']['id']==obj['version_id'] and r['kind'] in {'parent','split_parent','merge_parent','mapped_from'})
            for pid in sorted(parents):
                parent=versions[pid]['value'];current_id=heads[('object',parent['object_id'])];current=versions[current_id]['value']
                if parent['existence']!='active' or parent['evidence_state']!='observed':return False,'parent_formation_unavailable'
                if current['existence']=='invalidated':return False,'parent_invalidated'
                if current_id!=pid and current['existence'] not in {'superseded','expired'}:return False,'parent_revision_pending'
                good,reason=support(parent,ancestry)
                if not good:return False,reason
            return True,'supported'
        latest=[versions[v]['value'] for(kind,_),v in heads.items() if kind=='object'];latest.sort(key=lambda p:p['object_id'])
        self.last_object_evaluations=len(latest);states,active,objects=[],[],[]
        for obj in latest:
            good,reason=support(obj)
            if instrument is not None and obj['birth']['instrument']!=instrument:continue
            inst=obj['birth']['instrument'];valid=inst['valid_from']<=cut and all(t is None or cut<t for t in(inst['valid_until'],inst['expiry_at']))
            alive=obj['existence']=='active' and obj['eligibility']=='eligible' and obj['evidence_state']=='observed' and good and valid and(self.ttl_ns is None or cut<born[obj['object_id']]+self.ttl_ns)
            if alive:active.append(obj['version_id'])
            objects.append(obj);states.append({'object_id':obj['object_id'],'version_id':obj['version_id'],'dirty':not good,'reason':reason,'born_at':born[obj['object_id']]})
        if _validate_controls:
            for key,envelope in controls.items():
                value=envelope['value']
                if envelope['kind']=='candidate_cut':
                    projected=LiteralObjectGraph(self.journal,ttl_ns=self.ttl_ns,visit_reset_policy=self.visit_reset_policy).view(value['at'],instrument=value['instrument'],cursor=value['history_cursor'],_validate_controls=False)
                    if value['candidate_versions']!=projected['active_versions'] or value['candidate_count']!=len(projected['active_versions']) or value['considered_count']!=len(projected['objects']):raise ValueError('literal candidate denominator mismatch')
                    closure=_lineage(projected['versions'],projected['relations'],[o['version_id'] for o in projected['objects']],projected['visits'],projected['events'])
                    if any(value[k]!=closure[k] for k in closure):raise ValueError('literal full lineage closure mismatch')
                elif envelope['kind']=='target':
                    original=controls[value['cut_id']]['value'];obj=versions[value['object_version']]['value']
                    if value['object_version'] not in original['candidate_versions'] or value['geometry']!=obj['geometry'] or value['geometry_hash']!=_hash(obj['geometry']) or value['horizon_end']<=original['at']:raise ValueError('literal target substitution')
                elif envelope['kind']=='actions':
                    groups={}
                    for proposal in value['proposals']:
                        identity=_hash([value['policy'],proposal['canonical_idea_id'],proposal['visit_id'],proposal['side'],proposal['plan_definition'],proposal['horizon_end'],proposal['instrument']])
                        groups.setdefault(identity,[]).append(proposal['id'])
                    expected=[{'key':k,'members':sorted(v),'representative':min(v),'duplicate_members':sorted(v)[1:]} for k,v in sorted(groups.items())]
                    if value['groups']!=expected or value['unique_action_count']!=len(expected):raise ValueError('literal action grouping mismatch')
        return {'objects':objects,'active_versions':active,'states':states,'relations':relations,
                'visits':sorted(visits.values(),key=lambda p:(p['object_id'],p['visit_id'])),'events':observations,
                'versions':versions,'history_cursor':last_cursor,
                'candidate_cuts':{k:v['value'] for k,v in controls.items() if v['kind']=='candidate_cut'},
                'targets':{k:v['value'] for k,v in controls.items() if v['kind']=='target'},
                'actions':{k:v['value'] for k,v in controls.items() if v['kind']=='actions'}}
