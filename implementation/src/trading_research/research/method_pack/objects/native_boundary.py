"""Production native object boundary, isolated from primitive fixture helpers."""
from decimal import Decimal
from copy import deepcopy

from ..clocks import aligned_bar_bounds, aggregate_ohlcv, ns_to_et
from ..contracts import OutputField as F, register_output_schema, validate_output, OutputContractError
from ..logic import kleene_and
from ..native_resolution import NativeEvidenceError, ResolvedMembers, ns
from ..protocol import RecipeResult

NATIVE_PRODUCERS = {}
DERIVED_PRODUCERS = {}


def register_native(recipe_id, producer, schema):
    """producer(config, ResolvedMembers) must derive observations from members."""
    NATIVE_PRODUCERS[recipe_id] = producer
    register_output_schema(recipe_id, schema)


def register_derived(recipe_id, producer, schema):
    """producer(config, trusted_parent_objects) uses validated parent payloads."""
    DERIVED_PRODUCERS[recipe_id] = producer
    register_output_schema(recipe_id, schema)


def _interval_coverage(rows, start, end):
    bars = sorted((r for r in rows if 'start' in r), key=lambda r: r['start'])
    cursor, gaps = start, []
    for row in bars:
        if row['start'] < cursor:
            raise NativeEvidenceError('overlapping bar members')
        if row['start'] > cursor:
            gaps.append([cursor, row['start']])
        if row.get('complete') is not True:
            gaps.append([row['start'], row['end']])
        cursor = row['end']
    if cursor < end:
        gaps.append([cursor, end])
    return (True if not gaps else None), gaps


def o001(config, resolved):
    rows = resolved.rows()
    bars = [r for r in rows if 'start' in r]
    trades = [r for r in rows if r.get('action') == 'T']
    price, missing_intervals = _interval_coverage(bars, resolved.start_ns, resolved.end_ns)
    requirements = config.get('required_fields')
    if not isinstance(requirements, list) or not requirements:
        raise NativeEvidenceError('O001 needs a frozen required_fields list')
    missing = []
    side = None
    if trades and all(r.get('aggressor') in {'buy', 'sell'} and r.get('size') is not None for r in trades):
        side = resolved.coverage_ok
    checks = []
    for field in requirements:
        if field == 'ohlcv':
            check = price
        elif field == 'aggressor':
            check = side
        elif field == 'trades':
            check = resolved.coverage_ok if trades else None
        elif field == 'bbo':
            quote_rows = [r for r in rows if 'mbp-1' in r['dataset_id']]
            check = resolved.coverage_ok if quote_rows and all(r.get('bid') is not None and r.get('ask') is not None for r in quote_rows) else None
        else:
            check = None
        checks.append(check)
        if check is not True:
            missing.append(field)
    coverage = kleene_and(*checks)
    value = {'coverage_ok': coverage, 'base_identity_ok': True,
             'price_coverage': price, 'side_coverage': side,
             'missing_intervals': missing_intervals, 'missing_fields': missing,
             'source_precision': sorted(set(r['source_precision'] for r in rows)),
             'available_depth': 'bbo' if any('mbp-1' in r['dataset_id'] for r in rows) else 'trades' if trades else 'ohlcv'}
    return RecipeResult('O001', 'computed' if coverage is True else 'hole', value,
                        known_at=max(resolved.end_ns, resolved.known_at) if resolved.known_at is not None else None,
                        coverage_ok=coverage, hole_ids=[f'HOLE:O001:{f}' for f in missing])


def o003(config, resolved):
    verified = config.get('clock_verified')
    if verified is not None and type(verified) is not bool:
        raise NativeEvidenceError('clock_verified must be nullable Boolean')
    end = resolved.end_ns
    known = max(end, resolved.known_at) if resolved.known_at is not None else None
    available = None if known is None or config.get('use_at') is None else known <= config['use_at']
    return RecipeResult('O003', 'computed' if verified is True else 'hole', {
        'start_ns': resolved.start_ns, 'end_ns': end,
        'session_date_et': ns_to_et(resolved.start_ns).date().isoformat(),
        'bar_close_at': end, 'window_known_at': known, 'clock_verified': verified,
        'available': available, 'clock_check': kleene_and(verified, available),
    }, known_at=known, coverage_ok=verified,
        hole_ids=[] if verified is True else ['HOLE:O003:source_clock'])


def _verified_source_clock(config, resolved):
    """Author clock verification requires exact audited source evidence."""
    from ..evidence import source_admitted
    parent_id=config.get('clock_parent_id',config.get('selection_parent_id'))
    if parent_id is not None:
        parent=config.get('parents',{}).get(parent_id)
        if parent is None or parent.get('state')!='supplied':
            raise NativeEvidenceError('source clock parent must be an audited supplied observation')
        value=parent.get('value',{})
        key='clock_verified' if 'clock_verified' in value else 'source_clock_verified'
        if not source_admitted(parent,key):raise NativeEvidenceError('source clock parent lacks actual source admission')
        start=value.get('start_ns',value.get('formation_start'))
        end=value.get('end_ns',value.get('formation_end'))
        if start!=resolved.start_ns or end!=resolved.end_ns:
            raise NativeEvidenceError('source clock parent has a different exact window')
        verified=value.get(key)
        if verified is not None and type(verified) is not bool:raise NativeEvidenceError('source clock evidence must be nullable Boolean')
        return verified
    cid=config.get('source_configuration_id')
    if cid is None:return None
    from ..source_config import load_catalog,SourceSetting
    from ..semantic_views import AUTHORS,source_citation
    from ..catalog import METHOD_BY_ID
    from ..clocks import et_ns
    from datetime import timedelta
    catalog=load_catalog();configuration=catalog['configurations'].get(cid)
    method=config.get('method_id');key=config.get('source_setting_key')
    if configuration is None or configuration.get('version')!=config.get('source_configuration_version'):
        raise NativeEvidenceError('source clock needs actual catalog configuration/version')
    if method not in AUTHORS or configuration.get('author') not in AUTHORS[method] or METHOD_BY_ID[method] not in configuration.get('scope',[]):
        raise NativeEvidenceError('source clock catalog has foreign author/method scope')
    if key not in configuration.get('settings',{}):raise NativeEvidenceError('source clock has no exact catalog setting')
    setting=SourceSetting.parse(configuration['settings'][key])
    if setting.status!='fact':return None
    for ref in setting.source_refs:
        source_key,page=ref.rsplit(':',1);source=catalog['sources'][source_key]
        try:source_citation({'source_key':source_key,'source_file':source['path'],'sha256':source['sha256'],
                            'page':int(page),'image_id':f'{source_key}:{page}:page'},method)
        except ValueError as exc:raise NativeEvidenceError(str(exc)) from exc
    window=setting.resolve();day=ns_to_et(resolved.end_ns).date()
    if isinstance(window,dict) and all(k in window for k in ('formation_start','formation_end')):
        start,end=(ns(window[k],k) for k in ('formation_start','formation_end'))
    else:
        if isinstance(window,list) and len(window) in {2,3}:
            first,last=window[:2];timezone=window[2] if len(window)==3 else 'America/New_York'
            start_day=-1 if last<=first else 0;end_day=0
        elif isinstance(window,dict) and all(k in window for k in ('start_et','end_et')):
            first,last=window['start_et'],window['end_et'];timezone=window.get('timezone','America/New_York')
            start_day=window.get('start_day_offset',-1 if last<=first else 0);end_day=window.get('end_day_offset',0)
        else:raise NativeEvidenceError('catalog source setting is not a complete clock window')
        if timezone!='America/New_York':raise NativeEvidenceError('catalog clock does not use documented ET timezone')
        try:
            sh,sm=map(int,first.split(':'));eh,em=map(int,last.split(':'))
            start=et_ns(day+timedelta(days=start_day),sh,sm);end=et_ns(day+timedelta(days=end_day),eh,em)
        except (ValueError,TypeError) as exc:raise NativeEvidenceError('invalid catalog source clock') from exc
    if (start,end)!=(resolved.start_ns,resolved.end_ns):raise NativeEvidenceError('native window differs from actual source clock')
    return True


def native_o003(config, resolved):
    verified=_verified_source_clock(config,resolved)
    return o003({**config,'clock_verified':verified},resolved)


def o004(config, resolved):
    if config.get('kind') != 'time':
        raise NativeEvidenceError('native range bars require verified platform construction')
    size = config.get('size_minutes')
    if type(size) is not int:
        raise NativeEvidenceError('source size_minutes is required')
    start, end = resolved.start_ns, resolved.end_ns
    if aligned_bar_bounds(start, size) != (start, end):
        raise NativeEvidenceError('source bar is not clock-aligned to its stated size')
    rows = resolved.rows()
    bars = [r for r in rows if 'start' in r]
    events = [r for r in rows if 'event_ns' in r]
    if bars and events:
        raise NativeEvidenceError('bar source cannot double count event and OHLCV members')
    if bars:
        coverage, missing = _interval_coverage(bars, start, end)
        agg = aggregate_ohlcv(bars)
    else:
        coverage, missing = resolved.coverage_ok, []
        trades = [r for r in events if r.get('action') == 'T']
        # Without verified sequence, a tied opening/closing batch has no exact
        # O/C even though its high/low and volume are commutative.
        ordered = sorted(trades, key=lambda r: r['event_ns'])
        boundary_tie = any(sum(r['event_ns'] == t for r in ordered) > 1
                           for t in ({ordered[0]['event_ns'], ordered[-1]['event_ns']} if ordered else set()))
        if boundary_tie:
            for at in {ordered[0]['event_ns'], ordered[-1]['event_ns']}:
                batch = [r for r in ordered if r['event_ns'] == at]
                seq = [r.get('exchange_sequence') for r in batch]
                if len({row['price'] for row in batch}) > 1 and (None in seq or len(set(seq)) != len(seq)):
                    raise NativeEvidenceError('unknown_order at bar opening/closing trade batch')
            ordered.sort(key=lambda r: (r['event_ns'], r.get('exchange_sequence') or 0))
        agg = aggregate_ohlcv([{**r, 'O': r['price'], 'H': r['price'], 'L': r['price'], 'C': r['price'], 'V': r['size']} for r in ordered])
    complete = coverage is True and (agg['complete'] or agg['empty'])
    known = max(end, resolved.known_at) if resolved.known_at is not None else None
    value = {'bar_id': config.get('bar_id') or f'{resolved.instrument_id}:{start}:{end}',
             'instrument_id': resolved.instrument_id, 'kind': 'time', 'size': f'{size}m',
             'start': start, 'end': end, 'complete': complete, 'known_at': known,
             'native_source_compatible': True, 'coverage_state': ('known_empty' if agg['empty'] else 'complete') if complete else 'missing_interval',
             'member_event_ids': [r.get('event_id', r.get('bar_id')) for r in rows],
             'missing_intervals': missing, 'O': agg['O'], 'H': agg['H'], 'L': agg['L'], 'C': agg['C'], 'V': agg['V']}
    return RecipeResult('O004', 'computed' if complete else 'hole', value, known_at=known,
                        coverage_ok=True if complete else None,
                        hole_ids=[] if complete else ['HOLE:O004:complete_membership'])


def run_native_object(obj, resolver, *, parents=()):
    rid = obj['recipe_id']
    config = deepcopy(obj.get('inputs', {}))
    locators = obj.get('raw_member_locators', [])
    start,end,as_of=None,None,obj.get('as_of')
    has_interval=obj.get('formation_start') is not None or obj.get('formation_end') is not None
    if locators or has_interval:
        if obj.get('formation_start') is None or obj.get('formation_end') is None:
            raise NativeEvidenceError('explicit native formation interval requires both endpoints')
        start,end=ns(obj['formation_start'],'formation_start'),ns(obj['formation_end'],'formation_end')
        if end<=start:raise NativeEvidenceError('reversed or empty native object window')
    if as_of is not None:as_of=ns(as_of,'object snapshot')
    elif locators:as_of=end
    if as_of is not None and end is not None and as_of<end:
        raise NativeEvidenceError('native formation interval extends after object snapshot')
    # Derived constituents may have different explicit windows. Only a raw
    # object requires one shared formation envelope; never fabricate it here.
    canonical={}
    if start is not None:
        canonical.update(formation_start=start,formation_end=end,start_ns=start,end_ns=end,
                         window_start=start,window_end=end)
    if as_of is not None:canonical['as_of']=as_of
    for key in ('formation_start','formation_end','start_ns','end_ns','window_start','window_end','as_of'):
        if config.get(key) is not None:
            stamp=ns(config[key],f'input {key}')
            if key in canonical and stamp!=canonical[key]:
                raise NativeEvidenceError('input/object native window or snapshot mismatch')
    config.update(canonical)
    for key in ('instrument_id','method_id'):
        if key in obj:
            if key in config and str(config[key])!=str(obj[key]):raise NativeEvidenceError('input/object native identity mismatch')
            config[key]=obj[key]
    if config.get('use_at') is not None:ns(config['use_at'],'input use_at')
    resolved = None
    if locators:
        resolved = resolver.resolve(locators, instrument_id=obj['instrument_id'],
                                    start_ns=start, end_ns=end,as_of=as_of,use_at=config.get('use_at'))
    producer = NATIVE_PRODUCERS.get(rid) if resolved is not None else None
    derived = False
    if producer is None and parents:
        producer = DERIVED_PRODUCERS.get(rid)
        derived = producer is not None
    if producer is None:
        raise OutputContractError(f'{rid}: native member or parent-derived producer not implemented')
    expected = obj.get('parent_ids', [])
    if len(expected)!=len(set(expected)) or len(parents)!=len({parent['object_id'] for parent in parents}) or set(expected) != {parent['object_id'] for parent in parents}:
        raise NativeEvidenceError('native parent identity does not resolve to actual objects')
    for parent in parents:
        if parent.get('state') == 'supplied':
            from ..evidence import source_admitted
            if not parent.get('value') or not all(source_admitted(parent,field) for field in parent['value']):
                raise NativeEvidenceError('supplied native parent has not passed full source audit')
        for key in ('instrument_id', 'method_id', 'side'):
            if key in obj and key in parent and str(obj[key]) != str(parent[key]):
                raise NativeEvidenceError('native parent identity mismatch')
    if 'dependencies' in config:
        supplied = config['dependencies']
        if not isinstance(supplied,list) or any(not isinstance(dep,dict) for dep in supplied) or len(supplied)!=len(expected) or {dep.get('object_id') for dep in supplied} != set(expected):
            raise NativeEvidenceError('caller dependency does not name actual native parents')
    actual_parents=deepcopy(list(parents))
    config['dependencies'] = actual_parents
    config['parents'] = {parent['object_id']: parent for parent in actual_parents}
    config['parent_ids']=list(expected)
    if resolved is not None:
        definition=resolved.instrument_definition
        config['instrument_definition']=definition
        config['coverage_ok']=config['coverage_complete']=resolved.coverage_ok
        for key in ('tick_size','q'):
            if config.get(key) is None:continue
            try:tick=Decimal(str(config[key]))
            except Exception as exc:raise NativeEvidenceError('invalid caller tick unit') from exc
            if not tick.is_finite() or tick<=0 or definition is None or tick!=definition.tick_size:
                raise NativeEvidenceError('caller tick unit differs from actual native instrument definition')
        if definition is not None:
            config['tick_size']=config['q']=definition.tick_size
        else:
            config.pop('tick_size',None);config.pop('q',None)
        # These are native observations, never source settings. Domain adapters
        # still own all other field-specific input and selection validation.
        for key in ('members','events','bars','trades','rows','footprint_rows','quote','candle',
                    'O','H','L','C','V','o','h','l','c','v','price','size','bid','ask','bid_size','ask_size'):
            config.pop(key,None)
        input_times=[resolved.known_at,resolved.end_ns]+[parent.get('known_at') for parent in parents]
        config['known_at']=max(input_times) if all(t is not None for t in input_times) else None
    result = producer(config, actual_parents) if derived else producer(config, resolved)
    if result.recipe_id != rid:
        raise OutputContractError('native producer returned another recipe identity')
    result = validate_output(result)
    result.evidence_class = 'parent_derived' if derived else 'resolved_native'
    times = ([resolved.known_at, resolved.end_ns] if resolved is not None else []) + [result.known_at] + [p.get('known_at') for p in parents]
    result.known_at = max(times) if all(t is not None for t in times) else None
    for parent in parents:
        result.base_ok = kleene_and(result.base_ok, parent.get('recipe_base_ok'))
        result.coverage_ok = kleene_and(result.coverage_ok, parent.get('recipe_coverage_ok'))
        result.hole_ids = list(dict.fromkeys(result.hole_ids + parent.get('hole_ids', [])))
        if parent.get('state') == 'invalid':
            result.base_ok = False
        if result.base_ok is False:
            result.state = 'invalid'
        elif result.coverage_ok is not True and result.state == 'computed':
            result.state = 'hole'
    result.parent_ids = list(expected)
    if resolved is not None:
        rows=resolved.rows()
        if rid not in {'O003','O112'}:
            independently_complete=None
            if rows and all('start' in row and 'end' in row for row in rows):
                independently_complete,_=_interval_coverage(rows,resolved.start_ns,resolved.end_ns)
            native_coverage=True if independently_complete is True else resolved.coverage_ok
            result.coverage_ok=kleene_and(result.coverage_ok,native_coverage)
            if result.coverage_ok is not True:
                result.hole_ids=list(dict.fromkeys(result.hole_ids+[f'HOLE:{rid}:native_coverage']))
                if result.state=='computed':result.state='hole'
        definition=resolved.instrument_definition
        unit_used=any(value is not None and (key in {'tick_size','q'} or key.endswith('_ticks')) for key,value in result.value.items())
        if definition is not None and unit_used:
            result.known_at=max(result.known_at,definition.known_at) if result.known_at is not None and definition.known_at is not None else None
    if result.known_at is None:
        result.hole_ids=list(dict.fromkeys(result.hole_ids+[f'HOLE:{rid}:availability']))
        if result.state=='computed':result.state='hole'
    if 'known_at' in result.value:result.value['known_at']=result.known_at
    if 'coverage_ok' in result.value:result.value['coverage_ok']=result.coverage_ok
    if rid=='O003':
        result.value['window_known_at']=result.known_at
        result.value['available']=None if result.known_at is None or config.get('use_at') is None else result.known_at<=config['use_at']
        result.value['clock_check']=kleene_and(result.value['clock_verified'],result.value['available'])
    use_at = config.get('use_at')
    if use_at is not None and result.known_at is not None and result.known_at > use_at:
        result.state, result.base_ok = 'invalid', False
        result.hole_ids.append(f'HOLE:{rid}:dependency_after_use')
    claimed = obj.get('known_at')
    if claimed is not None and result.known_at is not None and claimed < result.known_at:
        result.state, result.base_ok = 'invalid', False
        result.hole_ids.append(f'HOLE:{rid}:backdated_availability')
    return result


register_native('O001', o001, {**{k: F((bool,), True) for k in ('coverage_ok','base_identity_ok','price_coverage','side_coverage')},
    **{k: F((list,)) for k in ('missing_intervals','missing_fields','source_precision')}, 'available_depth': F((str,))})
register_native('O003', native_o003, {**{k: F((int,)) for k in ('start_ns','end_ns','bar_close_at')},
    'window_known_at': F((int,), True), 'session_date_et': F((str,)),
    **{k: F((bool,), True) for k in ('clock_verified','available','clock_check')}})
register_native('O004', o004, {**{k: F((Decimal,), True) for k in ('O','H','L','C','V')},
    **{k: F((str,), True) for k in ('bar_id','kind','size')}, 'coverage_state': F((str,)),
    'instrument_id': F((str,int),True), **{k: F((int,),True) for k in ('start','end')}, 'known_at': F((int,), True),
    'complete': F((bool,)), 'native_source_compatible': F((bool,),True),
    **{k: F((list,)) for k in ('member_event_ids','missing_intervals')}})


def _local_members(inp, rid, required):
    """Validate an explicitly classified local/synthetic observation helper.

    This never creates resolved-native evidence and is not used by manifests.
    """
    from types import MappingProxyType
    missing = [key for key in required if inp.get(key) is None]
    if missing:
        return None, missing
    try:
        start, end = ns(inp['start_ns'], 'start'), ns(inp['end_ns'], 'end')
        if end <= start:
            raise NativeEvidenceError('reversed or empty interval')
        rows = []
        for source in inp.get('members', inp.get('bars', [])):
            row = dict(source)
            if 'instrument_id' not in row:
                missing.append('member_instrument_id')
                continue
            if str(row['instrument_id']) != str(inp['instrument_id']):
                raise NativeEvidenceError('cross-instrument local member')
            if 'start' in row and 'end' in row:
                at, until = ns(row['start'], 'member start'), ns(row['end'], 'member end')
                if until <= at:
                    raise NativeEvidenceError('reversed local member interval')
                if 'known_at' not in row:
                    row['known_at'] = until
                row.setdefault('complete', all(row.get(k) is not None for k in ('O','H','L','C','V')))
            elif 'event_ns' in row or 't' in row:
                at = ns(row.get('event_ns', row.get('t')), 'event')
                until = at + 1
                row['event_ns'] = at
                row.setdefault('known_at', at)
            else:
                missing.append('member_interval')
                continue
            if at < start or until > end:
                raise NativeEvidenceError('member outside local interval')
            row.setdefault('source_precision', 'explicit_local_ns')
            row.setdefault('dataset_id', 'local_observation')
            row.setdefault('bar_id', f'local:{inp["instrument_id"]}:{at}:{until}')
            rows.append(MappingProxyType(row))
        if missing:
            return None, sorted(set(missing))
        times = [r.get('known_at') for r in rows]
        known = max(times) if times and all(t is not None for t in times) else None
        return ResolvedMembers(tuple(rows), inp['instrument_id'], start, end, known, None, ()), []
    except (NativeEvidenceError, TypeError, ValueError) as exc:
        return RecipeResult(rid, 'invalid', {}, base_ok=False, coverage_ok=None,
                            reason=str(exc), hole_ids=[f'HOLE:{rid}:identity_or_interval']), []


def _bar_hole(inp, missing):
    value = {'bar_id': inp.get('bar_id'), 'instrument_id': inp.get('instrument_id'),
             'kind': inp.get('kind'), 'size': None if inp.get('size_minutes') is None else f'{inp["size_minutes"]}m',
             'start': inp.get('start_ns'), 'end': inp.get('end_ns'),
             'O': None, 'H': None, 'L': None, 'C': None, 'V': None,
             'complete': False, 'known_at': None, 'native_source_compatible': None,
             'coverage_state': 'missing_required_observation', 'member_event_ids': [], 'missing_intervals': []}
    return RecipeResult('O004', 'hole', value, base_ok=None, coverage_ok=None,
                        hole_ids=[f'HOLE:O004:{field}' for field in missing], reason='missing ' + ', '.join(missing))


def o004_local(inp):
    members, missing = _local_members(inp, 'O004', ('members','instrument_id','start_ns','end_ns','kind','size_minutes'))
    if isinstance(members, RecipeResult):
        return members
    if missing:
        return _bar_hole(inp, missing)
    if inp.get('kind') != 'time':
        return _bar_hole(inp, ['native_bar_definition'])
    try:
        result = o004(inp, members)
    except NativeEvidenceError as exc:
        return RecipeResult('O004', 'invalid', {}, base_ok=False, coverage_ok=None,
                            reason=str(exc), hole_ids=['HOLE:O004:bar_definition'])
    if result.known_at is not None and any(inp.get(k) is not None and result.known_at > inp[k] for k in ('known_at','use_at')):
        result.state, result.base_ok = 'invalid', False
        result.hole_ids.append('HOLE:O004:ordering')
    return result


def _coverage_hole_payload(missing):
    return {'coverage_ok': None, 'base_identity_ok': None,
            'price_coverage': None, 'side_coverage': None, 'missing_intervals': [],
            'missing_fields': list(missing), 'source_precision': [], 'available_depth': 'unresolved'}


GUARD_HOLE_PAYLOADS = {
    'O001': lambda result: _coverage_hole_payload(
        hole.removeprefix('HOLE:O001:') for hole in result.hole_ids),
}


def o001_local(inp):
    members, missing = _local_members(inp, 'O001', ('bars','instrument_id','start_ns','end_ns','required_fields'))
    if isinstance(members, RecipeResult):
        return members
    if missing:
        return RecipeResult('O001', 'hole', _coverage_hole_payload(missing), base_ok=None, coverage_ok=None,
            hole_ids=[f'HOLE:O001:{field}' for field in missing])
    # A complete synthetic tape must be explicitly declared and fully timed;
    # this record remains research_helper and never resolves native provenance.
    if inp.get('trades') is not None:
        from types import MappingProxyType
        from ..adapters import decode_aggressor
        tape, tape_missing = _local_members({**inp, 'members': inp['trades']}, 'O001',
                                            ('members','instrument_id','start_ns','end_ns'))
        if isinstance(tape, RecipeResult):
            return tape
        if tape_missing:
            return RecipeResult('O001', 'hole', {'coverage_ok': None, 'base_identity_ok': True,
                'price_coverage': _interval_coverage(members.rows(), members.start_ns, members.end_ns)[0],
                'side_coverage': None, 'missing_intervals': [], 'missing_fields': tape_missing,
                'source_precision': [], 'available_depth': 'ohlcv'}, coverage_ok=None,
                hole_ids=[f'HOLE:O001:{field}' for field in tape_missing])
        trades = [MappingProxyType({**r, 'action': 'T', 'aggressor': decode_aggressor(r.get('side'))['aggressor']}) for r in tape.members]
        coverage = inp.get('trade_coverage', {})
        tape_ok = (True if coverage.get('start_ns') == members.start_ns and coverage.get('end_ns') == members.end_ns
                   and coverage.get('coverage_ok') is True and coverage.get('missing_intervals') == []
                   and coverage.get('evidence_id') else None)
        known = max(members.known_at, tape.known_at) if members.known_at is not None and tape.known_at is not None else None
        members = ResolvedMembers(members.members + tuple(trades), members.instrument_id, members.start_ns,
                                  members.end_ns, known, tape_ok, ())
    return o001(inp, members)


def o003_local(inp):
    missing = [key for key in ('start_ns','end_ns') if inp.get(key) is None]
    if missing:
        return RecipeResult('O003', 'hole', {'start_ns': inp.get('start_ns'), 'end_ns': inp.get('end_ns'),
            'session_date_et': None, 'bar_close_at': inp.get('end_ns'), 'window_known_at': None,
            'clock_verified': None, 'available': None, 'clock_check': None}, base_ok=None, coverage_ok=None,
            hole_ids=[f'HOLE:O003:{field}' for field in missing])
    try:
        start, end = ns(inp['start_ns'], 'start'), ns(inp['end_ns'], 'end')
        if end <= start:
            raise NativeEvidenceError('reversed or empty interval')
        resolved = ResolvedMembers((), inp.get('instrument_id'), start, end, end, None, ())
        result = o003(inp, resolved)
        use = inp.get('use_at', inp.get('event_ns'))
        if use is not None and end > use:
            result.base_ok, result.state = False, 'invalid'
            result.value['available'], result.value['clock_check'] = False, False
        return result
    except NativeEvidenceError as exc:
        return RecipeResult('O003', 'invalid', {}, base_ok=False, coverage_ok=None,
                            reason=str(exc), hole_ids=['HOLE:O003:interval'])


REGISTRATION_OVERRIDES = {'O001': o001_local, 'O003': o003_local, 'O004': o004_local}
REQUIRED_INPUTS = {'O001': ('bars','instrument_id','start_ns','end_ns','required_fields'),
                   'O003': ('start_ns','end_ns'),
                   'O004': ('members',)}
