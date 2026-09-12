"""Serializable, provenance-checked adapters for the immutable profile domain."""
from __future__ import annotations

from copy import deepcopy
from dataclasses import asdict, fields, replace
from datetime import date
from decimal import Decimal, InvalidOperation
from typing import Any, Mapping, Sequence

from ..contracts import OutputField as F
from ..native_resolution import NativeEvidenceError
from ..protocol import RecipeResult
from . import profiles as p


_MEASURED_EVIDENCE = frozenset({'resolved_native', 'parent_derived'})


def definition_from_config(config, native):
    supplied=config.get('profile_definition')
    if native is None or native.known_at is None:
        raise NativeEvidenceError('profile requires an available native instrument definition')
    actual=p.InstrumentDefinition(native.definition_id,native.instrument_id,native.tick_size,native.known_at)
    if isinstance(supplied,p.ProfileDefinition):
        if supplied.instrument.instrument_id!=actual.instrument_id or supplied.instrument.tick_size!=actual.tick_size:
            raise NativeEvidenceError('profile tick/instrument differs from the resolved definition')
        return replace(supplied,instrument=actual)
    if not isinstance(supplied,dict):
        raise NativeEvidenceError('profile requires its versioned definition record')
    instrument=supplied.get('instrument')
    if instrument is not None:
        if str(instrument.get('instrument_id'))!=str(actual.instrument_id) or Decimal(str(instrument.get('tick_size')))!=actual.tick_size:
            raise NativeEvidenceError('caller profile instrument/tick does not match native definition')
    window=dict(supplied['window'])
    window['session_date']=date.fromisoformat(window['session_date']) if isinstance(window['session_date'],str) else window['session_date']
    w=p.ProfileWindow(**window)
    va=supplied.get('value_area')
    if va is not None:
        va=p.ValueAreaConfig(**va)
        if va.algorithm=='adjacent_single' and config.get('variant')!='comparison':
            raise NativeEvidenceError('undisclosed VA expansion/tie policy must be a named comparison')
    allowed={f.name for f in fields(p.ProfileDefinition)}-{'instrument','window','value_area'}
    settings={k:v for k,v in supplied.items() if k in allowed}
    return p.ProfileDefinition(instrument=actual,window=w,value_area=va,**settings)


def definition_payload(definition):
    value=asdict(definition)
    value['window']['session_date']=definition.window.session_date.isoformat()
    return value


def snapshot_from_payload(value):
    """Decode an already validated parent payload; reconcile every native row."""
    required=set(p._PROFILE_OUTPUT_SCHEMA)
    if not required<=value.keys():raise NativeEvidenceError('parent is missing complete profile output fields')
    rows=tuple(p.PriceRow(**{f.name:(None if r.get(f.name) is None else Decimal(str(r[f.name]))) for f in fields(p.PriceRow)}) for r in value['rows'])
    if len({r.price for r in rows})!=len(rows):raise NativeEvidenceError('duplicate native profile row')
    for row in rows:
        if min(row.buy_volume,row.sell_volume,row.unknown_volume)<0 or row.total_volume!=row.buy_volume+row.sell_volume+row.unknown_volume:
            raise NativeEvidenceError('parent profile side totals do not reconcile')
        if row.known_delta!=row.buy_volume-row.sell_volume or row.delta_low!=row.known_delta-row.unknown_volume or row.delta_high!=row.known_delta+row.unknown_volume:
            raise NativeEvidenceError('parent signed profile bounds do not reconcile')
        if row.full_delta!=(row.known_delta if row.unknown_volume==0 else None):raise NativeEvidenceError('unknown aggression cannot become exact delta')
    total=Decimal(str(value['total_volume']))
    if total!=sum((r.total_volume for r in rows),Decimal(0)):raise NativeEvidenceError('parent profile total does not reconcile')
    if value['formation_start']>value['formation_end'] or value['formation_end']>value['as_of'] or value['as_of']>value['known_at']:
        raise NativeEvidenceError('parent profile snapshot clock does not reconcile')
    numeric={'tick_size','total_volume','H','L','poc','val','vah','value_area_fraction','volume_inside_value','achieved_value_fraction','bin_width','bin_origin'}
    kwargs={}
    for f in fields(p.ProfileSnapshot):
        key=f.name
        if key=='rows':kwargs[key]=rows
        elif key=='session_date':kwargs[key]=date.fromisoformat(value[key]) if value[key] is not None else None
        elif key=='coverage_state':kwargs[key]=value['coverage']['state']
        elif key=='coverage_holes':kwargs[key]=tuple(value['coverage']['holes'])
        elif key=='poc_candidates':kwargs[key]=tuple(Decimal(str(x)) for x in value[key])
        elif key in {'event_ids','parent_ids'}:kwargs[key]=tuple(value[key])
        elif key in numeric:kwargs[key]=None if value.get(key) is None else Decimal(str(value[key]))
        else:kwargs[key]=deepcopy(value.get(key))
    return p.ProfileSnapshot(**kwargs)


def _native(rid,config,resolved):
    definition=definition_from_config(config,resolved.instrument_definition)
    as_of=config.get('as_of',resolved.end_ns);cutoff=min(as_of,definition.window.end)
    if definition.window.start!=resolved.start_ns or cutoff!=resolved.end_ns:
        raise NativeEvidenceError('resolved members do not match the profile snapshot formation')
    coverage=p.Coverage('complete' if resolved.coverage_ok is True else 'unavailable',resolved.start_ns,resolved.end_ns,
        () if resolved.coverage_ok is True else (f'HOLE:{rid}:coverage',),f'native:{definition.window.window_id}')
    snapshot=p.build_profile(definition,resolved.rows(),as_of=as_of,coverage=coverage)
    result=p.o077({'profile':snapshot}) if rid=='O077' else p._result(rid,snapshot)
    if rid=='O063' and snapshot.kind!='developing_rth':raise NativeEvidenceError('O063 needs a developing RTH identity')
    result.value['variant']=config.get('variant','source')
    return result


def _profiles(parents):
    result=[]
    for parent in parents:
        if parent['recipe_id'] in {'O061','O063','O070'}:
            if parent.get('evidence_class') not in {'resolved_native','parent_derived'}:
                raise NativeEvidenceError('profile transform needs an actual native profile parent')
            result.append((parent,snapshot_from_payload(parent['value'])))
    return result


def _one_profile(parents,config):
    candidates=_profiles(parents)
    selected=config.get('profile_parent_id')
    if selected is not None:candidates=[x for x in candidates if x[0]['object_id']==selected]
    if len(candidates)!=1:raise NativeEvidenceError('profile transform must select exactly one dated native parent')
    return candidates[0]


def _parent(parents,key,config,required=False):
    identifier=config.get(key)
    matches=[o for o in parents if o['object_id']==identifier]
    if identifier is not None and len(matches)!=1:raise NativeEvidenceError(f'{key}: selected source parent is absent')
    if not matches and required:raise NativeEvidenceError(f'{key}: actual parent observation is required')
    return matches[0] if matches else None


def _source_selection(parent,keys):
    if parent is None:return {}
    if parent.get('evidence_class') not in {'resolved_native','parent_derived'}:
        from ..evidence import source_admitted
        fields=[key for key in keys if key in parent['value']]
        if parent.get('evidence_class')!='supplied_source_audit' or not fields or not all(source_admitted(parent,key) for key in fields):
            raise NativeEvidenceError('selection requires its fully audited actual source fields')
    if parent['state'] not in {'supplied','computed','hole'}:
        raise NativeEvidenceError('selection requires an actual cited source observation')
    return {k:deepcopy(parent['value'][k]) for k in keys if k in parent['value']}


def _actual_parent(parents, config, key, *, source_ok=False):
    """Select one real dependency; caller config can select but never replace it."""
    parent = _parent(parents, key, config, required=True)
    if parent.get('state') == 'invalid':
        raise NativeEvidenceError(f'{key}: invalid parent cannot support a derived object')
    if parent.get('evidence_class') in _MEASURED_EVIDENCE:
        return parent
    if (source_ok and parent.get('state') == 'supplied'
            and parent.get('evidence_class') == 'supplied_source_audit'):
        return parent
    raise NativeEvidenceError(f'{key}: actual native, derived, or admitted source evidence is required')


def _number(value: Any, label: str) -> Decimal:
    if value is None or isinstance(value, bool):
        raise NativeEvidenceError(f'{label} is missing or nonnumeric')
    try:
        result = value if isinstance(value, Decimal) else Decimal(str(value))
    except (InvalidOperation, TypeError, ValueError) as exc:
        raise NativeEvidenceError(f'{label} is nonnumeric') from exc
    if not result.is_finite():
        raise NativeEvidenceError(f'{label} must be finite')
    return result


def _value(parent: Mapping[str, Any]) -> Mapping[str, Any]:
    value = parent.get('value')
    if not isinstance(value, Mapping):
        raise NativeEvidenceError('parent value must be a typed mapping')
    return value


def _admit_used_source_fields(parent: Mapping[str, Any], names: Sequence[str]) -> None:
    """Validate every source field consumed by a direct derived route."""
    if parent.get('evidence_class') != 'supplied_source_audit':
        return
    from ..evidence import source_admitted
    value = _value(parent)
    used = [name for name in names if name in value]
    if not used or any(not source_admitted(parent, name) for name in used):
        raise NativeEvidenceError('source fields used by profile transform are not admitted')


def _bounds(parent: Mapping[str, Any]) -> tuple[Decimal, Decimal]:
    value = _value(parent)
    for low_key, high_key in (
        ('L', 'H'), ('lo', 'hi'), ('band_lo', 'band_hi'), ('box_low', 'box_high'),
        ('val', 'vah'), ('shelf_low', 'shelf_high'),
    ):
        if value.get(low_key) is not None and value.get(high_key) is not None:
            low, high = _number(value[low_key], low_key), _number(value[high_key], high_key)
            if low > high:
                raise NativeEvidenceError('parent bounds are reversed')
            return low, high
    for key in ('ledge_band', 'dealing_band', 'reaction_band', 'balance_band',
                'reference_band', 'shelf_band', 'band', 'price_or_band'):
        band = value.get(key)
        if isinstance(band, (list, tuple)) and len(band) == 2:
            low, high = _number(band[0], f'{key} low'), _number(band[1], f'{key} high')
            if low > high:
                raise NativeEvidenceError('parent bounds are reversed')
            return low, high
        if key == 'price_or_band' and band is not None:
            price = _number(band, key)
            return price, price
    for key in ('edge_price', 'ledge_px', 'price', 'poc', 'mpoc'):
        if value.get(key) is not None:
            price = _number(value[key], key)
            return price, price
    raise NativeEvidenceError('selected parent has no usable price bounds')


def _price(parent: Mapping[str, Any], *names: str) -> Decimal:
    value = _value(parent)
    for name in names:
        if value.get(name) is not None:
            return _number(value[name], name)
    low, high = _bounds(parent)
    if low == high:
        return low
    raise NativeEvidenceError('selected parent has no exact controlling price')


def _lineage(parent: Mapping[str, Any], names: Sequence[str], *, fallback=False):
    value = _value(parent)
    for name in names:
        identity = value.get(name)
        if isinstance(identity, str) and identity:
            return identity
    return parent.get('object_id') if fallback else None


def _event_at(parent: Mapping[str, Any], *names: str) -> int | None:
    value = _value(parent)
    for name in names:
        at = value.get(name)
        if at is not None:
            if type(at) is not int:
                raise NativeEvidenceError(f'{name} must be an integer event key')
            return at
    return None


def _known(parent: Mapping[str, Any]) -> int:
    known = parent.get('known_at')
    if type(known) is not int:
        raise NativeEvidenceError('derived parent availability is unknown')
    return known


def _causal_use(config: Mapping[str, Any], parents: Sequence[Mapping[str, Any]]) -> int | None:
    use_at = config.get('use_at', config.get('as_of'))
    if use_at is not None and type(use_at) is not int:
        raise NativeEvidenceError('use_at must be an integer event key')
    knowns = [_known(parent) for parent in parents]
    if use_at is not None and any(known > use_at for known in knowns):
        raise NativeEvidenceError('selected parent is available after use')
    return max(knowns) if knowns else None


def _coverage(parents: Sequence[Mapping[str, Any]], holes: Sequence[str]) -> bool | None:
    if holes or any(parent.get('recipe_coverage_ok') is not True for parent in parents):
        return None
    return True


def _derived_ledge(config, parents):
    ledge = _actual_parent(parents, config, 'ledge_parent_id', source_ok=True)
    retest = _actual_parent(parents, config, 'retest_parent_id')
    selected = [ledge, retest]
    known = _causal_use(config, selected)
    ledge_value, retest_value = _value(ledge), _value(retest)
    _admit_used_source_fields(ledge, tuple(ledge_value))
    ledge_id = _lineage(ledge, ('ledge_id', 'edge_id', 'band_id', 'reference_lineage_id'), fallback=True)
    retest_id = _lineage(retest, ('retest_ledge_id', 'ledge_id', 'reference_lineage_id', 'band_id'))
    low, high = _bounds(ledge)
    contact_at = _event_at(retest, 'contact_at', 'retest_at', 'touch_at')
    if contact_at is not None:
        if contact_at > _known(retest):
            raise NativeEvidenceError('retest contact is not yet available from its parent')
        if _known(ledge) >= contact_at:
            raise NativeEvidenceError('ledge was not selected before the retest contact')
    contact_price = None
    for name in ('contact_price', 'retest_px', 'price'):
        if retest_value.get(name) is not None:
            contact_price = _number(retest_value[name], name)
            break
    if contact_price is None:
        try:
            contact_price = _price(retest)
        except NativeEvidenceError:
            pass
    contacted = retest_value.get('price_overlap')
    if contacted is None and contact_price is not None:
        contacted = low <= contact_price <= high
    same_id = None if retest_id is None else retest_id == ledge_id
    same_price = None if contact_price is None or low != high else contact_price == low
    same_retest = (False if same_id is False or contacted is False else
                   True if same_id is True and contacted is True and contact_at is not None else None)
    holes = []
    if retest_id is None:
        holes.append('HOLE:O069:retest_identity')
    if contact_at is None or contacted is None:
        holes.append('HOLE:O069:contact')
    neighbor = ledge_value.get('neighbor_volumes')
    if neighbor is None and (ledge_value.get('shelf_volume') is not None
                             or ledge_value.get('transition_volume') is not None):
        neighbor = {'shelf': ledge_value.get('shelf_volume'),
                    'transition': ledge_value.get('transition_volume')}
    value = {'same_id': same_id, 'same_price': same_price, 'ledge_id': ledge_id,
             'retest_ledge_id': retest_id, 'vah_touch_is_retest': None,
             'ledge_band': [low, high], 'neighbor_volumes': deepcopy(neighbor),
             'same_ledge_retest': same_retest, 'contact_at': contact_at,
             'automatic_edge': None}
    return RecipeResult('O069', 'hole' if holes else 'computed', value, holes,
                        known, True, _coverage(selected, holes),
                        parent_ids=[parent['object_id'] for parent in selected])


def _derived_dealing_range(config, parents):
    band = _actual_parent(parents, config, 'band_parent_id')
    control = _actual_parent(parents, config, 'control_parent_id')
    selection = (_actual_parent(parents, config, 'selection_parent_id', source_ok=True)
                 if config.get('selection_parent_id') is not None else None)
    selected = [band, control, *([selection] if selection is not None else [])]
    known = _causal_use(config, selected)
    low, high = _bounds(band)
    controlling = _price(control, 'controlling_reference', 'controlling_low',
                         'controlling_high', 'edge_price', 'price', 'poc', 'mpoc')
    band_id = _lineage(band, ('band_id', 'range_id', 'balance_id', 'ledge_id'), fallback=True)
    source = {}
    holes = []
    if selection is None:
        holes.append('HOLE:O071:source_selection')
    else:
        _admit_used_source_fields(selection, tuple(_value(selection)))
        source = _source_selection(selection, ('rationale', 'thesis_side', 'scale',
                                                'band_parent_id', 'control_parent_id',
                                                'band_id', 'selected_at'))
        if source.get('band_parent_id') is None or source.get('control_parent_id') is None:
            holes.append('HOLE:O071:selection_identity')
        elif source['band_parent_id'] != band['object_id'] or source['control_parent_id'] != control['object_id']:
            raise NativeEvidenceError('source selection names different band/control parents')
        selected_band_id = source.get('band_id')
        if selected_band_id is not None and selected_band_id not in {band_id, band['object_id']}:
            raise NativeEvidenceError('source selection names a different dealing band')
    side = source.get('thesis_side')
    if side not in {None, 'long', 'short'}:
        raise NativeEvidenceError('source thesis side must be long or short')
    if side == 'long' and controlling != low or side == 'short' and controlling != high:
        raise NativeEvidenceError('controlling parent is not the selected thesis-side extreme')
    result = p.o071({'lo': low, 'hi': high, 'band_id': band_id,
        'controlling_reference': controlling, 'selected_at': known,
        'use_at': config.get('use_at'), 'rationale': source.get('rationale'),
        'thesis_side': side, 'parent_ids': [parent['object_id'] for parent in selected]})
    result.value.update(thesis_side=side, scale=source.get('scale'))
    result.hole_ids = list(dict.fromkeys([*result.hole_ids, *holes]))
    if result.hole_ids and result.state == 'computed':
        result.state = 'hole'
    if result.hole_ids:
        result.value['band_known_before_use'] = None
    result.known_at = known
    result.coverage_ok = _coverage(selected, result.hole_ids)
    result.parent_ids = [parent['object_id'] for parent in selected]
    return result


def _defense_flag(value: Mapping[str, Any], *, current=False) -> bool | None:
    names = (('current_defense', 'fresh_defense', 'confirmed', 'source_defense') if current
             else ('prior_defense', 'defended', 'clean_reaction', 'source_defense'))
    for name in names:
        if value.get(name) is not None:
            flag = value[name]
            if type(flag) is not bool:
                raise NativeEvidenceError(f'{name} must be boolean')
            return flag
    return None


def _derived_prior_defense(config, parents):
    band = _actual_parent(parents, config, 'band_parent_id', source_ok=True)
    prior = _actual_parent(parents, config, 'prior_defense_parent_id', source_ok=True)
    contact = _actual_parent(parents, config, 'contact_parent_id')
    control = (_actual_parent(parents, config, 'control_parent_id', source_ok=True)
               if config.get('control_parent_id') is not None else None)
    selected = [band, prior, contact, *([control] if control is not None else [])]
    known = _causal_use(config, selected)
    low, high = _bounds(band)
    band_id = _lineage(band, ('band_id', 'range_id', 'balance_id', 'ledge_id'), fallback=True)
    prior_value, contact_value = _value(prior), _value(contact)
    _admit_used_source_fields(band, tuple(_value(band)))
    _admit_used_source_fields(prior, tuple(prior_value))
    prior_id = _lineage(prior, ('band_id', 'reference_lineage_id', 'reaction_band_id'))
    contact_id = _lineage(contact, ('contact_band_id', 'band_id', 'reference_lineage_id'))
    prior_at = _event_at(prior, 'defended_at', 'reaction_at', 'prior_defense_at')
    contact_at = _event_at(contact, 'contact_at', 'touch_at', 'retest_at')
    if contact_at is None:
        raise NativeEvidenceError('current contact parent has no observed contact event')
    if contact_at > _known(contact):
        raise NativeEvidenceError('current contact is not yet available from its parent')
    if prior_at is not None and (prior_at > _known(prior) or prior_at >= contact_at):
        raise NativeEvidenceError('prior defense event does not precede current contact causally')
    if prior_at is not None and _known(band) > prior_at:
        raise NativeEvidenceError('reaction band was selected after the prior defense')
    if _known(prior) >= contact_at:
        raise NativeEvidenceError('prior defense was not known before current contact')
    contact_price = None
    for name in ('contact_price', 'price', 'retest_px'):
        if contact_value.get(name) is not None:
            contact_price = _number(contact_value[name], name)
            break
    observed_contact = contact_value.get('price_overlap')
    if observed_contact is None and contact_price is not None:
        observed_contact = low <= contact_price <= high
    identity_match = None if contact_id is None else contact_id == band_id
    same_contact = (False if identity_match is False or observed_contact is False else
                    True if identity_match is True and observed_contact is True else None)
    prior_flag = _defense_flag(prior_value)
    prior_identity = None if prior_id is None else prior_id == band_id
    prior_known = (False if prior_identity is False or prior_flag is False else
                   True if prior_identity is True and prior_flag is True else None)
    holes = []
    if prior_id is None:
        holes.append('HOLE:O072:prior_band_identity')
    if contact_id is None:
        holes.append('HOLE:O072:contact_band_identity')
    if observed_contact is None:
        holes.append('HOLE:O072:contact')
    if prior_flag is None:
        holes.append('HOLE:O072:prior_defense_selector')
    if prior_at is None:
        holes.append('HOLE:O072:prior_reaction_event')
        prior_known = None
    current = None
    fresh_at = None
    if control is None:
        holes.append('HOLE:O072:fresh_defense')
    else:
        control_value = _value(control)
        _admit_used_source_fields(control, tuple(control_value))
        control_id = _lineage(control, ('band_id', 'reference_lineage_id', 'control_band_id'))
        fresh_at = _event_at(control, 'fresh_defense_at', 'confirmation_at', 'defense_at')
        current_flag = _defense_flag(control_value, current=True)
        if control_id is None:
            holes.append('HOLE:O072:control_band_identity')
        if fresh_at is None or current_flag is None:
            holes.append('HOLE:O072:fresh_defense')
        elif fresh_at < contact_at:
            raise NativeEvidenceError('fresh defense precedes the current contact')
        elif fresh_at > _known(control):
            raise NativeEvidenceError('fresh defense is not yet available from its parent')
        else:
            control_match = control_id == band_id if control_id is not None else None
            current = (False if control_match is False or current_flag is False or same_contact is False else
                       True if control_match is True and current_flag is True and same_contact is True else None)
    value = {'band': [low, high], 'prior_defense_known': prior_known,
             'same_band_contact': same_contact, 'current_defense': current,
             'history_ids': [prior['object_id']], 'prior_defense_known_at': _known(prior),
             'prior_defense_at': prior_at,
             'contact_at': contact_at, 'fresh_defense_at': fresh_at,
             'band_id': band_id, 'prior_band_id': prior_id, 'contact_band_id': contact_id}
    holes = list(dict.fromkeys(holes))
    return RecipeResult('O072', 'hole' if holes else 'computed', value, holes,
                        known, True, _coverage(selected, holes),
                        parent_ids=[parent['object_id'] for parent in selected])


def derived_profile(rid,config,parents):
    if rid == 'O069':
        return _derived_ledge(config, parents)
    if rid == 'O071':
        return _derived_dealing_range(config, parents)
    if rid == 'O072':
        return _derived_prior_defense(config, parents)
    if rid=='O070':
        native=_profiles(parents);requested=config.get('constituent_ids')
        if not isinstance(requested,list) or len(set(requested))!=len(requested) or set(requested)!={o['object_id'] for o,s in native}:
            raise NativeEvidenceError('composite requires exactly its explicit constituent object IDs')
        by_id={o['object_id']:s for o,s in native}
        result=p.o070(dict(profiles=[by_id[x] for x in requested],composite_id=config.get('composite_id'),
                           selection_known_at=config.get('selection_known_at'),rationale=config.get('rationale')))
        result.parent_ids=requested
        return result
    parent,profile=_one_profile(parents,config)
    inp={'profile':profile,'use_at':config.get('use_at'),'as_of':config.get('as_of',profile.as_of)}
    selection=_parent(parents,'selection_parent_id',config)
    price=_parent(parents,'price_parent_id',config)
    opening=_parent(parents,'opening_parent_id',config)
    if rid in {'O062','O064','O076'}:
        if price:
            inp['price']=price['value'].get('price',price['value'].get('C'))
        if opening:inp['opening_condition']=deepcopy(opening['value'])
    elif rid=='O066':
        inp.update(_source_selection(selection,('node','hvn_band','node_id')))
        inp['source_node_known']=selection is not None
    elif rid=='O067':
        inp.update(_source_selection(selection,('bridge_band','accepted_a_id','accepted_b_id','transition_ids')))
        inp['source_node_known']=selection is not None
    elif rid=='O068':
        inp.update(_source_selection(selection,('shelf','shelf_band','shelf_id','transition_band','edge_id')))
        inp['source_shelf_known']=selection is not None
    elif rid=='O073':
        if config.get('source')=='sires':
            clocks=[o for o in parents if o['recipe_id']=='O011']
            if len(clocks)!=1 or (clocks[0]['formation_start'],clocks[0]['formation_end'])!=(profile.formation_start,profile.formation_end):
                raise NativeEvidenceError('Sires O073 needs the same dated O011 parent window')
            # The dated O011 parent proves the clock directly.  Preserve that
            # audited identity instead of requiring a naming convention in an
            # independently reconstructed profile's window_id.
            inp['source_clock_id']='O011:sires_overnight_1800_0930_et'
        inp.update(_source_selection(selection,('lvn_band','landmarks')))
        older=_parent(parents,'older_poc_parent_id',config)
        if older and older['value'].get('poc') is not None:
            if older['formation_end']>=profile.formation_start:raise NativeEvidenceError('older POC profile is not earlier')
            inp['older_poc_reference']=p.ProfileReference(older['object_id'],older['value']['profile_id'],older['value']['snapshot_id'],'poc',Decimal(str(older['value']['poc'])),older['known_at'])
        if opening:inp['opening_response']={**deepcopy(opening['value']),'known_at':opening['known_at']}
    elif rid=='O074':
        inp.update(_source_selection(selection,('source_inventory','inventory')))
        inp['measured_evidence']=[{'profile_id':profile.profile_id,'snapshot_id':profile.snapshot_id,
          'buy':sum((r.buy_volume for r in profile.rows),Decimal(0)),'sell':sum((r.sell_volume for r in profile.rows),Decimal(0)),
          'unknown':sum((r.unknown_volume for r in profile.rows),Decimal(0))}]
        inp['inventory_known_at']=selection['known_at'] if selection else None
        if opening:inp['opening_response']={**deepcopy(opening['value']),'known_at':opening['known_at']}
    elif rid=='O075':
        inp.update(_source_selection(selection,('balance_band','scope_resolved','literal_source_label')))
        if opening:inp['open_px']=opening['value'].get('cash_open',opening['value'].get('O'))
    else:raise NativeEvidenceError(f'{rid}: unsupported profile transform')
    result=p.REGISTRATION_OVERRIDES[rid](inp)
    result.parent_ids=[o['object_id'] for o in parents]
    # Incorporating a contact or opening response cannot retain the earlier
    # profile-only availability. The shared boundary also enforces this maximum.
    timestamps=[o['known_at'] for o in parents]
    result.known_at=max(timestamps+[result.known_at]) if result.known_at is not None and all(t is not None for t in timestamps) else None
    return result


def native_reference_visits(config,resolved):
    parents=list(config.get('parents',{}).values())
    matches=[x for x in parents if x['object_id']==config.get('reference_parent_id')]
    if len(matches)!=1:raise NativeEvidenceError('reference history needs its selected native profile/POC parent')
    obj=matches[0];v=obj['value']
    if v.get('poc') is None:
        return RecipeResult('O065','hole',{'untested_at_decision':None,'first_qualifying_visit':None,'active_reference_id':obj['object_id']},
          ["HOLE:O065:poc"],obj['known_at'],True,None)
    reference=p.ProfileReference(config.get('reference_id',obj['object_id']),v['profile_id'],v['snapshot_id'],'poc',Decimal(str(v['poc'])),obj['known_at'])
    coverage=p.Coverage('complete' if resolved.coverage_ok is True else 'unavailable',resolved.start_ns,resolved.end_ns)
    result=p.o065(dict(reference=reference,as_of=config.get('as_of',resolved.end_ns),coverage=coverage,resolved_members=resolved.rows()))
    result.parent_ids=[obj['object_id']]
    return result


NUM=F((Decimal,),True);TEXT=F((str,),True);BOOL=F((bool,),True);NULL=F((type(None),),True)
OUTPUT_SCHEMAS={**p.OUTPUT_SCHEMAS,
 'O062':{'val':NUM,'vah':NUM,'fraction':NUM,'volume_inside':NUM,'achieved_fraction':NUM,'construction_known':BOOL,'profile_id':TEXT,'snapshot_id':TEXT},
 'O064':{'poc':NUM,'max_volume':NUM,'poc_candidates':F((list,)),'tie_state':F((str,)),'profile_id':TEXT,'snapshot_id':TEXT},
 'O065':{'untested_at_decision':BOOL,'first_qualifying_visit':F((dict,),True),'active_reference_id':TEXT},
 'O066':{'hvn_band':F((list,),True),'node_volume':NUM,'peak_candidates':F((list,)),'source_node_known':BOOL,'automatic_node_selection':NULL,'profile_id':TEXT,'snapshot_id':TEXT},
 'O067':{'bridge_band':F((list,),True),'bridge_volume':NUM,'trough_candidates':F((list,)),'accepted_area_ids':F((list,)),'transition_ids':F((list,)),'automatic_node_selection':NULL},
 'O068':{'shelf_band':F((list,),True),'shelf_volume':NUM,'transition_band':F((list,),True),'transition_volume':NUM,'edge_id':TEXT,'automatic_shelf_selection':NULL},
 'O069':{'same_id':BOOL,'same_price':BOOL,'ledge_id':TEXT,'retest_ledge_id':TEXT,'vah_touch_is_retest':BOOL},
 'O070':{**p._PROFILE_OUTPUT_SCHEMA,'constituent_ids':F((list,)),'composite_histogram':F((dict,)),'automatic_window_selection':NULL},
 'O071':{'dealing_band':F((list,)),'width':NUM,'band_id':TEXT,'controlling_reference':NUM,'band_known_before_use':BOOL,'parent_ids':F((list,)),'rationale':TEXT},
 'O072':{'band':F((list,)),'prior_defense_known':BOOL,'same_band_contact':BOOL,'current_defense':BOOL,'history_ids':F((list,))},
 'O073':{'overnight_profile_snapshot':F((dict,),True),'landmarks':F((list,)),'lvn_band':F((list,),True),'older_poc_alignment':BOOL,'opening_response':F((dict,),True),'source_clock_id':TEXT},
 'O074':{'source_inventory':TEXT,'measured_evidence':F((list,)),'opening_response':F((dict,str),True),'automatic_inventory':NULL},
 'O075':{'eth_profile_id':TEXT,'snapshot_id':TEXT,'scope_resolved':BOOL,'balance_band':F((list,),True),'va_band':F((list,),True),'cohort_eligibility':BOOL,'scope_holes':F((list,))},
 'O076':{'mpoc':NUM,'profile_id':TEXT,'snapshot_id':TEXT,'volume_poc':NUM,'opening_condition':F((dict,bool),True),'later_contact':F((dict,),True)},
}
NATIVE_PRODUCERS={rid:(lambda cfg,res,rid=rid:_native(rid,cfg,res)) for rid in ('O061','O063','O077')}
NATIVE_PRODUCERS['O065']=native_reference_visits
DERIVED_PRODUCERS={rid:(lambda cfg,parents,rid=rid:derived_profile(rid,cfg,parents)) for rid in ('O062','O064','O066','O067','O068','O069','O070','O071','O072','O073','O074','O075','O076')}
