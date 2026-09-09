"""Static contracts shared by engineering mapping, supervision and attachment.

Reading this module does not import candidate implementations or discover tests.
Every family/case binding is supplied in a retained batch contract.
"""
from dataclasses import asdict
import ast
import hashlib
import json
import math
import os
import stat
from pathlib import Path
import re

from trading_research.operations.artifacts import artifact_ref, digest

ROOT = Path(__file__).resolve().parents[1]
RESOURCE_CONTRACT = (180, 190, 4 * 1024 ** 3, 240)
RESOURCE_CONTRACT_V2 = (180, 190, 4 * 1024 ** 3, 360)
RESOURCE_PRESETS = {'legacy': RESOURCE_CONTRACT, 'bounded_complete_suite_v2': RESOURCE_CONTRACT_V2}
REGISTRATION_RESOURCE_FIELDS = ('maximum_cpu_per_attempt', 'hard_cpu_seconds', 'address_space_bytes', 'wall_seconds')
CONFIGURATION_RESOURCE_FIELDS = ('cpu_reservation_seconds', 'cpu_hard_seconds', 'address_space_bytes', 'wall_limit_seconds')
RESOLVED = {'repaired_and_statically_verified', 'verified_no_change_required'}


def package_path(relative):
    if type(relative) is not str or not relative or '\\' in relative:
        raise ValueError('canonical relative package path required')
    path = Path(relative)
    if (path.is_absolute() or path.as_posix() != relative
            or any(part in {'.', '..', 'archive'} for part in path.parts)):
        raise ValueError('noncanonical or excluded package path')
    result = ROOT / path
    if result.resolve() != result:
        raise ValueError('package path traverses a symlink')
    return result


def local_identity(relative):
    raw = package_path(relative).read_bytes()
    return byte_identity(relative,raw)


def byte_identity(relative,raw):
    return {'path': relative, 'sha256': hashlib.sha256(raw).hexdigest(), 'size_bytes': len(raw)}


def capture_inputs(paths):
    captured={}
    for path in dict.fromkeys(paths):
        with package_path(path).open('rb') as stream:
            raw=stream.read(16*1024**2+1)
        if len(raw)>16*1024**2:
            raise ValueError('mapping input byte capacity exceeded')
        captured[path]=raw
    return captured


def retain_captured_inputs(store,captured,identities):
    retained=[]
    for item in identities:
        raw=captured[item['path']]
        if byte_identity(item['path'],raw)!=item:
            raise ValueError('captured mapping input identity differs')
        ref=store.put_bytes(raw,kind='mapping_input')
        if ref.sha256!=item['sha256'] or ref.size_bytes!=item['size_bytes']:
            raise ValueError('retained mapping bytes differ from validated input')
        retained.append({'identity':item,'artifact':asdict(ref)})
    return retained


def resource_preset(version):
    if type(version) is not str or version not in RESOURCE_PRESETS:
        raise ValueError('unknown frozen engineering resource version')
    return RESOURCE_PRESETS[version]


def batch_resources(batch):
    if type(batch) is not dict:
        raise ValueError('explicit engineering batch required')
    if batch.get('kind') == 'engineering_batch_contract_v1':
        if 'resources' in batch:
            raise ValueError('legacy batch cannot add or change its frozen resources')
        return RESOURCE_CONTRACT
    if batch.get('kind') != 'engineering_batch_contract_v2':
        raise ValueError('unknown engineering batch resource schema')
    resources = batch.get('resources')
    if type(resources) is not dict or set(resources) != set(REGISTRATION_RESOURCE_FIELDS):
        raise ValueError('exact v2 resource fields required')
    values = tuple(resources[k] for k in REGISTRATION_RESOURCE_FIELDS)
    if any(type(v) is not int for v in values) or values != RESOURCE_CONTRACT_V2:
        raise ValueError('v2 resources differ from the predeclared complete-suite contract')
    return values


def resource_configuration(batch):
    result = dict(zip(CONFIGURATION_RESOURCE_FIELDS, batch_resources(batch)))
    if batch['kind'] == 'engineering_batch_contract_v2':
        result['resource_contract_version'] = 'bounded_complete_suite_v2'
    return result


def configuration_resources(configuration):
    if type(configuration) is not dict:
        raise ValueError('explicit frozen resource configuration required')
    expected = resource_preset(configuration.get('resource_contract_version', 'legacy'))
    values = tuple(configuration.get(k) for k in CONFIGURATION_RESOURCE_FIELDS)
    if any(type(v) is not int for v in values) or values != expected:
        raise ValueError('final resource configuration differs from the frozen shared contract')
    return values


def validate_resource_binding(batch, configuration, worker_acknowledgement=None):
    expected = resource_configuration(batch)
    actual = {k: configuration[k] for k in (*CONFIGURATION_RESOURCE_FIELDS, 'resource_contract_version') if k in configuration}
    configuration_resources(configuration)
    if actual != expected:
        raise ValueError('launch resource contract differs from the retained batch')
    if worker_acknowledgement is not None:
        if type(worker_acknowledgement) is not dict:
            raise ValueError('explicit worker acknowledgement required')
        observed = worker_acknowledgement.get('resource_limits')
        if observed is None and batch['kind'] == 'engineering_batch_contract_v1':
            return expected
        if type(observed) is not dict or set(observed) != set(expected):
            raise ValueError('exact worker resource acknowledgement fields required')
        configuration_resources(observed)
        if observed != expected:
            raise ValueError('worker acknowledgement differs from the frozen resource contract')
    elif batch['kind'] == 'engineering_batch_contract_v2':
        raise ValueError('v2 result requires its actual worker resource acknowledgement')
    return expected


def final_resource_error(cpu,wall,rss,configuration):
    try:
        configured = configuration_resources(configuration)
    except ValueError as exc:
        return str(exc)
    if (type(cpu) not in (int,float) or type(wall) not in (int,float) or type(rss) is not int
            or not math.isfinite(cpu) or not math.isfinite(wall) or min(cpu,wall,rss)<0):
        return 'final observed CPU, wall and RSS must be finite nonnegative exact values'
    if cpu>=configured[0]: return f'final process-group CPU reached the frozen {configured[0]}-second limit'
    if wall>=configured[3]: return f'final wall time reached the frozen {configured[3]}-second limit'
    if rss>=configured[2]: return 'final peak RSS reached the frozen 4-GiB limit'
    return None


def nonempty_strings(value, *, unique=True):
    if (type(value) is not list or not value
            or any(type(v) is not str or not v for v in value)
            or unique and len(value) != len(set(value))):
        raise ValueError('explicit nonempty string list required')
    return value


def select(value, key):
    if type(key) is not str or not key:
        raise ValueError('explicit JSON selector required')
    for part in key.split('.'):
        value = value[part]
    return value


def indexed(values, id_key, description):
    if type(values) is not list or not values or any(type(v) is not dict for v in values):
        raise ValueError(f'{description}: nonempty record list required')
    result = {}
    for value in values:
        key = value[id_key]
        if type(key) is not str or not key or key in result:
            raise ValueError(f'{description}: duplicate or invalid identity')
        result[key] = value
    return result


def validate_batch(batch):
    required = {'kind', 'id', 'families', 'baseline_verification', 'review_paths',
                'pre_repair_review', 'batch_review_path', 'review_text_path', 'tools',
                'additional_contract_paths'}
    batch_resources(batch)
    if batch['kind'] == 'engineering_batch_contract_v2':
        required.add('resources')
    if set(batch) != required:
        raise ValueError('batch contract schema differs')
    if type(batch['id']) is not str or re.fullmatch(r'[a-z0-9][a-z0-9-]{0,95}', batch['id']) is None:
        raise ValueError('bounded batch identity required')
    specs = batch['families']
    if type(specs) is not list or not 1 <= len(specs) <= 16:
        raise ValueError('batch needs one to sixteen explicit families')
    names, prefixes, outputs = set(), set(), set()
    spec_keys = {'prefix', 'family', 'registration_path', 'preparation_path', 'case_map_path',
                 'coverage_path', 'case_report_path', 'test_modules', 'prepared_cases',
                 'golden_collections', 'golden_to_preparation', 'extra_requirements', 'source_clauses'}
    for spec in specs:
        if type(spec) is not dict or set(spec) != spec_keys:
            raise ValueError('family specification schema differs')
        if (type(spec['prefix']) is not str or re.fullmatch(r'[a-z0-9][a-z0-9-]{0,63}', spec['prefix']) is None
                or type(spec['family']) is not str or not spec['family']
                or spec['family'] in names or spec['prefix'] in prefixes):
            raise ValueError('duplicate or invalid family/prefix')
        names.add(spec['family']); prefixes.add(spec['prefix'])
        for key in ('registration_path', 'preparation_path', 'case_map_path', 'coverage_path', 'case_report_path'):
            path = package_path(spec[key])
            if not path.is_relative_to(ROOT / 'reports'):
                raise ValueError('family metadata must remain below reports/')
            if path in outputs:
                raise ValueError('family metadata paths alias each other')
            outputs.add(path)
        for module in nonempty_strings(spec['test_modules']):
            if re.fullmatch(r'tests\.test_[a-z0-9_]+', module) is None:
                raise ValueError('explicit test module required')
        for selector in [spec['prepared_cases'], spec['source_clauses'], *spec['golden_collections']]:
            if (type(selector) is not dict or set(selector) != {'key', 'id_key'}
                    or any(type(selector[k]) is not str or not selector[k] for k in selector)):
                raise ValueError('exact case/source selector required')
        if not spec['golden_collections'] or type(spec['golden_to_preparation']) is not dict or type(spec['extra_requirements']) is not dict:
            raise ValueError('explicit golden/preparation/extra requirement bindings required')
    if (type(batch['review_paths']) is not dict or not batch['review_paths']
            or type(batch['additional_contract_paths']) is not list
            or len(batch['additional_contract_paths']) != len(set(batch['additional_contract_paths']))):
        raise ValueError('complete review/contract support paths required')
    for path, selector in batch['review_paths'].items():
        package_path(path)
        if type(selector) is not str or not selector:
            raise ValueError('explicit review finding selector required')
    tool_keys = {'supervisor', 'normalizer', 'recorder', 'contract_support'}
    if type(batch['tools']) is not dict or set(batch['tools']) != tool_keys:
        raise ValueError('all orchestration sources must be declared')
    for path in [*batch['tools'].values(), *batch['additional_contract_paths'],
                 batch['batch_review_path'], batch['review_text_path']]:
        package_path(path)
    receipt = batch['pre_repair_review']
    if type(receipt) is not dict or set(receipt) != {'path', 'sha256', 'size_bytes'}:
        raise ValueError('exact pre-repair review receipt identity required')
    package_path(receipt['path'])
    if (type(receipt['sha256']) is not str or re.fullmatch(r'[0-9a-f]{64}', receipt['sha256']) is None
            or type(receipt['size_bytes']) is not int or receipt['size_bytes'] <= 0):
        raise ValueError('pre-repair receipt is not frozen')
    if artifact_ref(batch['baseline_verification']).kind != 'verification':
        raise ValueError('successful prior verification reference required')
    return batch


def load_batch(relative):
    return load_batch_snapshot(relative)[1]


def load_batch_snapshot(relative):
    raw = package_path(relative).read_bytes()
    if len(raw) > 2 * 1024 ** 2:
        raise ValueError('batch metadata exceeds its finite bound')
    return raw,validate_batch(json.loads(raw))


def static_methods(modules, captured=None):
    result = []
    for module in modules:
        path=module.replace('.', '/')+'.py'
        tree = ast.parse(package_path(path).read_bytes() if captured is None else captured[path])
        for cls in tree.body:
            if isinstance(cls, ast.ClassDef):
                result.extend(f'{module}.{cls.name}.{method.name}' for method in cls.body
                              if isinstance(method, (ast.FunctionDef, ast.AsyncFunctionDef))
                              and method.name.startswith('test_'))
    if len(result) != len(set(result)):
        raise ValueError('duplicate static test identity')
    return sorted(result)


E0_AMENDMENT_PARENT = 'B03-E0-full-integration-engineering-v1'
E0_AMENDMENT_FAMILY = 'B03-E0-full-integration-engineering-amendment-v1'
E0_DEVIATION_PATHS = ('reports/e0-unregistered-execution-deviation.json',
                      'reports/e0-policy-account-execution-deviation-v2.json')


def bounded_metadata_bytes(path, *, limit=1024 ** 2):
    """Bound actual reads and reject aliases at every directory component."""
    path = Path(path).absolute()
    directory = descriptor = None
    try:
        if path.resolve(strict=True) != path:
            raise ValueError('metadata path traverses an alias')
        flags = os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW
        directory = os.open(path.anchor, flags)
        for part in path.parts[1:-1]:
            child = os.open(part, flags, dir_fd=directory)
            os.close(directory)
            directory = child
        descriptor = os.open(path.name, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK,
                             dir_fd=directory)
        info = os.fstat(descriptor)
        if not stat.S_ISREG(info.st_mode) or not 0 < info.st_size <= limit:
            raise ValueError('bounded regular metadata file required')
        with os.fdopen(descriptor, 'rb') as stream:
            descriptor = None
            raw = stream.read(limit + 1)
        if not 0 < len(raw) <= limit or len(raw) != info.st_size:
            raise ValueError('metadata file changed its bounded size during read')
        return raw
    except OSError as exc:
        raise ValueError('metadata cannot be read through its bounded regular path') from exc
    finally:
        if descriptor is not None:
            os.close(descriptor)
        if directory is not None:
            os.close(directory)


def _pinned_amendment_input(identity):
    if type(identity) is not dict or set(identity) != {'path', 'sha256', 'size_bytes'}:
        raise ValueError('exact pinned amendment input required')
    path = package_path(identity['path'])
    if not path.is_relative_to(ROOT / 'reports'):
        raise ValueError('amendment inputs must remain in reports')
    raw = bounded_metadata_bytes(path)
    if byte_identity(identity['path'], raw) != identity:
        raise ValueError('pinned amendment input bytes changed')
    return json.loads(raw)


def registration_budget(registry, registration, *, amendment_bytes=None):
    """Admit the single named E0 extension without modifying old budgets."""
    reference = registration.get('budget_amendment')
    if reference is None:
        if amendment_bytes is not None:
            raise ValueError('unbound amendment bytes supplied')
        return 3, 600
    ref = artifact_ref(reference)
    if ref.kind != 'engineering_budget_amendment' or not 0 < ref.size_bytes <= 1024 ** 2:
        raise ValueError('bounded retained engineering budget amendment required')
    raw = (bounded_metadata_bytes(registry.artifacts.path(ref))
           if amendment_bytes is None else amendment_bytes)
    if (type(raw) is not bytes or len(raw) != ref.size_bytes
            or hashlib.sha256(raw).hexdigest() != ref.sha256):
        raise ValueError('budget amendment differs from its retained bytes')
    amendment = json.loads(raw)
    required = {'schema', 'id', 'parent_family', 'additional_family', 'parent_registration',
                'deviation_records', 'additional_attempts', 'additional_cpu_budget_seconds',
                'resources', 'prior_attempts_reset', 'prior_private_passes_accepted',
                'prior_unobserved_resources', 'parent_budget_available', 'research_scope_changed',
                'economic_evidence', 'reason', 'authorization_basis', 'declared_at'}
    if type(amendment) is not dict or set(amendment) != required:
        raise ValueError('exact budget amendment schema required')
    if (amendment['schema'] != 'engineering_budget_amendment_v1'
            or amendment['parent_family'] != E0_AMENDMENT_PARENT
            or amendment['additional_family'] != E0_AMENDMENT_FAMILY
            or registration['family'] != E0_AMENDMENT_FAMILY
            or type(amendment['additional_attempts']) is not int or amendment['additional_attempts'] != 1
            or type(amendment['additional_cpu_budget_seconds']) is not int
            or amendment['additional_cpu_budget_seconds'] != RESOURCE_CONTRACT_V2[0]
            or type(amendment['resources']) is not dict
            or set(amendment['resources']) != set(REGISTRATION_RESOURCE_FIELDS)
            or any(type(v) is not int for v in amendment['resources'].values())
            or tuple(amendment['resources'][key] for key in REGISTRATION_RESOURCE_FIELDS) != RESOURCE_CONTRACT_V2
            or any(type(registration[key]) is not int for key in REGISTRATION_RESOURCE_FIELDS)
            or tuple(registration[key] for key in REGISTRATION_RESOURCE_FIELDS) != RESOURCE_CONTRACT_V2
            or any(amendment[key] is not False for key in ('prior_attempts_reset',
                'prior_private_passes_accepted', 'parent_budget_available', 'research_scope_changed', 'economic_evidence'))
            or amendment['prior_unobserved_resources'] != 'unknown_not_reconstructed'
            or any(type(amendment[key]) is not str or not amendment[key]
                   for key in ('id', 'reason', 'authorization_basis', 'declared_at'))):
        raise ValueError('amendment changes the one additional E0 attempt or hides prior history')
    parent = registry.state()['families'][amendment['parent_family']]
    original = parent['protocol']
    if ('budget_amendment' in original or parent['max_attempts'] != 3
            or parent['cpu_budget_seconds'] != 600):
        raise ValueError('budget amendments cannot chain or reset prior family limits')
    preserved = set(original) - {'family', 'registered_at'}
    if (set(registration) != set(original) | {'budget_amendment'}
            or any(registration[key] != original[key] for key in preserved)):
        raise ValueError('budget amendment changed the frozen original scope or evidence')
    identity = amendment['parent_registration']
    parent_input = _pinned_amendment_input(identity)
    if identity['path'] != 'reports/e0-integration-registration.json' or parent_input != original:
        raise ValueError('budget amendment lacks the unchanged exact parent registration')
    deviations = amendment['deviation_records']
    if (type(deviations) is not list or len(deviations) != len(E0_DEVIATION_PATHS)
            or any(type(row) is not dict for row in deviations)
            or tuple(row.get('path') for row in deviations) != E0_DEVIATION_PATHS):
        raise ValueError('budget amendment must retain both declared deviation reports')
    for row in deviations:
        value = _pinned_amendment_input(row)
        if (value['verification_disposition']['all_private_passes_rejected'] is not True
                or value['verification_disposition']['failed_outcomes_retained'] is not True
                or value['resources']['cpu_seconds'] is not None
                or value['resources']['peak_rss_bytes'] is not None):
            raise ValueError('budget amendment must preserve rejected evidence and unknown telemetry')
    return 1, RESOURCE_CONTRACT_V2[0]


def validate_registrations(registry, registrations, batch):
    resources = batch_resources(batch)
    expected = {s['family'] for s in batch['families']}
    if len(registrations) != len(expected) or {r['family'] for r in registrations} != expected:
        raise ValueError('exact distinct registered batch families required')
    state = registry.state()
    retired = set()
    for family in state['families'].values():
        if family['protocol'].get('budget_amendment') is not None:
            attempts, cpu = registration_budget(registry, family['protocol'])
            if family['max_attempts'] != attempts or family['cpu_budget_seconds'] != cpu:
                raise ValueError('registered amendment changed its one additional allowance')
            retired.add(E0_AMENDMENT_PARENT)
    for registration in registrations:
        family = state['families'][registration['family']]
        attempts, cpu_budget = registration_budget(registry, registration)
        if (registration['family'] in retired or family['protocol'] != registration
                or family['max_attempts'] != attempts or family['cpu_budget_seconds'] != cpu_budget
                or tuple(registration[k] for k in REGISTRATION_RESOURCE_FIELDS) != resources
                or any(type(registration[k]) is not int for k in REGISTRATION_RESOURCE_FIELDS)):
            raise ValueError('immutable family registration or shared budget differs')
        for key in ('protocol', 'golden'):
            if package_path(registration[key + '_path']).read_bytes() != registry.artifacts.read(artifact_ref(registration[key])):
                raise ValueError('frozen protocol/golden bytes changed')


def case_contract(store, registration, spec, captured=None):
    wrapper = store.read_json(artifact_ref(registration['source_cases']))
    raw = store.read(artifact_ref(wrapper['preparation_bytes']))
    preparation = json.loads(raw)
    local=package_path(spec['preparation_path']).read_bytes() if captured is None else captured[spec['preparation_path']]
    if preparation != wrapper['preparation'] or raw != local:
        raise ValueError('local source preparation differs from retained exact bytes')
    selector = spec['prepared_cases']
    originals = indexed(select(preparation, selector['key']), selector['id_key'], 'prepared cases')
    selector = spec['source_clauses']
    clauses = indexed(select(preparation, selector['key']), selector['id_key'], 'source clauses')
    golden = store.read_json(artifact_ref(registration['golden']))
    literals = {}
    for selector in spec['golden_collections']:
        collection = indexed(select(golden, selector['key']), selector['id_key'], 'golden cases')
        if set(literals) & set(collection):
            raise ValueError('golden collections reuse a case identity')
        literals.update(collection)
    bindings = spec['golden_to_preparation']
    if set(bindings) != set(literals):
        raise ValueError('every and only frozen golden ID requires an explicit binding')
    for case_id, bound in bindings.items():
        if (type(bound) is not list or len(bound) != len(set(bound))
                or any(type(v) is not str or v not in originals for v in bound)):
            raise ValueError('invalid prepared-case binding')
    extras = {case_id for case_id, bound in bindings.items() if not bound}
    if (set(spec['extra_requirements']) != extras
            or {v for values in bindings.values() for v in values} != set(originals)):
        raise ValueError('prepared case omitted or new case lacks its declared engineering requirement')
    for value in spec['extra_requirements'].values():
        nonempty_strings(value)
    return originals, literals, {k: sorted(v) for k, v in bindings.items()}, clauses


def validate_coverage(coverage, spec, originals, literals, bindings, clauses, methods):
    if (coverage['family'] != spec['family'] or coverage['test_modules'] != spec['test_modules']
            or coverage['whole_unit_definition_closure'] is not False
            or coverage['executed_by_mapping'] is not False):
        raise ValueError('case mapping changed family, modules or its evidence boundary')
    nonempty_strings(coverage['remaining'])
    cases = indexed(coverage['cases'], 'case_id', 'implementation cases')
    if set(cases) != set(literals):
        raise ValueError('exact mandatory golden coverage differs')
    claimed = set()
    for case_id, case in cases.items():
        ids = nonempty_strings(case['assertion_ids'])
        if not set(ids) <= set(methods) or case['source_case_ids'] != bindings[case_id]:
            raise ValueError('unknown assertion or incorrectly bound case')
        nonempty_strings(case['remaining'])
        claimed.update(ids)
    if coverage['additional_assertion_ids'] != sorted(set(methods) - claimed):
        raise ValueError('additional assertion denominator differs')
    expected_sources = {source: sorted(k for k, values in bindings.items() if source in values)
                        for source in sorted(originals)}
    if coverage['source_case_mapping'] != expected_sources or coverage['extra_requirements'] != spec['extra_requirements']:
        raise ValueError('prepared/extra case accounting differs')
    dispositions = indexed(coverage['source_dispositions'], 'source_id', 'source dispositions')
    if set(dispositions) != set(clauses):
        raise ValueError('every independent source clause needs its own disposition')
    for row in dispositions.values():
        case_ids, assertions = row['case_ids'], row['assertion_ids']
        if (type(case_ids) is not list or len(case_ids) != len(set(case_ids))
                or not set(case_ids) <= set(literals) or type(assertions) is not list
                or len(assertions) != len(set(assertions)) or row['whole_source_closed'] is not False
                or type(row['covered_mechanism']) is not str or not row['covered_mechanism']):
            raise ValueError('invalid source-specific coverage or closure claim')
        possible = {a for case_id in case_ids for a in cases[case_id]['assertion_ids']}
        if not set(assertions) <= possible or bool(case_ids) != bool(assertions):
            raise ValueError('source mechanism assertion is unbound or unsupported')
        nonempty_strings(row['remaining'])


def input_paths(spec, registration):
    return [spec['registration_path'], registration['golden_path'], registration['protocol_path'],
            spec['preparation_path'], spec['case_map_path'],
            *(m.replace('.', '/') + '.py' for m in spec['test_modules'])]


def normalize_coverage(store, registration, spec, batch, batch_path, batch_raw=None):
    paths=input_paths(spec,registration)
    captured=capture_inputs([*paths,batch['tools']['normalizer'],batch['tools']['contract_support'],batch_path])
    if json.loads(captured[batch_path])!=batch or batch_raw is not None and captured[batch_path]!=batch_raw:
        raise ValueError('loaded batch differs from captured contract bytes')
    if json.loads(captured[spec['registration_path']])!=registration:
        raise ValueError('captured registration differs')
    for kind in ('golden','protocol'):
        if captured[registration[kind+'_path']]!=store.read(artifact_ref(registration[kind])):
            raise ValueError('captured frozen family contract differs')
    originals, literals, bindings, clauses = case_contract(store, registration, spec, captured)
    raw_map = json.loads(captured[spec['case_map_path']])
    proposed = indexed(raw_map['cases'], 'case_id', 'raw case map')
    if set(proposed) != set(literals) or raw_map['test_modules'] != spec['test_modules']:
        raise ValueError('raw case map omits/adds a frozen vector or module')
    methods = static_methods(spec['test_modules'],captured)
    cases = [{'case_id': key, 'source_case_ids': bindings[key],
              'assertion_ids': sorted(nonempty_strings(proposed[key]['assertion_ids'])),
              'remaining': nonempty_strings(proposed[key]['remaining'])} for key in sorted(literals)]
    used = {a for case in cases for a in case['assertion_ids']}
    wrapper = store.read_json(artifact_ref(registration['source_cases']))
    result = {'kind': 'static_implementation_case_mapping', 'family': spec['family'],
              'test_modules': spec['test_modules'], 'cases': cases,
              'source_case_mapping': {source: sorted(k for k, values in bindings.items() if source in values)
                                      for source in sorted(originals)},
              'source_dispositions': raw_map['source_dispositions'],
              'extra_requirements': spec['extra_requirements'],
              'additional_assertion_ids': sorted(set(methods) - used),
              'remaining': nonempty_strings(raw_map['remaining']),
              'inputs': [byte_identity(p,captured[p]) for p in paths],
              'mapping_script': byte_identity(batch['tools']['normalizer'],captured[batch['tools']['normalizer']]),
              'contract_support': byte_identity(batch['tools']['contract_support'],captured[batch['tools']['contract_support']]),
              'batch_contract': byte_identity(batch_path,captured[batch_path]),
              'registered_source_cases': registration['source_cases'],
              'registered_preparation_bytes': wrapper['preparation_bytes'],
              'executed_by_mapping': False, 'whole_unit_definition_closure': False}
    validate_coverage(result, spec, originals, literals, bindings, clauses, methods)
    return result


def retain_mapping_inputs(store, coverage, registration, spec, batch, batch_path, batch_raw=None):
    paths=input_paths(spec,registration)
    captured=capture_inputs([*paths,batch_path,batch['tools']['normalizer'],batch['tools']['contract_support']])
    expected = [byte_identity(p,captured[p]) for p in paths]
    if (coverage['inputs'] != expected or coverage['batch_contract'] != byte_identity(batch_path,captured[batch_path])
            or json.loads(captured[batch_path])!=batch or batch_raw is not None and captured[batch_path]!=batch_raw
            or coverage['mapping_script'] != byte_identity(batch['tools']['normalizer'],captured[batch['tools']['normalizer']])
            or coverage['contract_support'] != byte_identity(batch['tools']['contract_support'],captured[batch['tools']['contract_support']])):
        raise ValueError('mapping inputs, tools or batch contract bytes changed')
    source = store.read_json(artifact_ref(registration['source_cases']))
    if (json.loads(captured[spec['registration_path']]) != registration
            or coverage['registered_source_cases'] != registration['source_cases']
            or coverage['registered_preparation_bytes'] != source['preparation_bytes']):
        raise ValueError('mapping registration provenance differs')
    case_contract(store, registration, spec,captured)
    for kind in ('golden','protocol'):
        if captured[registration[kind+'_path']]!=store.read(artifact_ref(registration[kind])):
            raise ValueError('retained frozen family contract differs')
    return {'inputs':retain_captured_inputs(store,captured,expected),
            'registered_source_cases': registration['source_cases'],
            'registered_preparation_bytes': source['preparation_bytes']}


def validate_review_support(review, store, batch):
    identity = batch['pre_repair_review']
    raw = package_path(identity['path']).read_bytes()
    if byte_identity(identity['path'],raw) != identity:
        raise ValueError('frozen pre-repair review receipt changed')
    receipt = json.loads(raw)
    if (type(receipt) is not dict or set(receipt) != {'artifact', 'code_snapshot', 'findings'}
            or artifact_ref(receipt['artifact']).kind != 'implementation_review'
            or artifact_ref(receipt['code_snapshot']).kind != 'code_snapshot'
            or type(receipt['findings']) is not int or receipt['findings'] < 0):
        raise ValueError('pre-repair review receipt schema differs')
    original = store.read_json(artifact_ref(receipt['artifact']))
    store.read(artifact_ref(receipt['code_snapshot']))
    if (original['pre_repair_code_snapshot'] != receipt['code_snapshot']
            or review['required_review_paths'] != sorted(batch['review_paths'])
            or review['reviews'] != original['reviews']
            or review['frozen_contracts'] != original['frozen_contracts']):
        raise ValueError('review no longer binds complete original code/reviews/contracts')
    # Original orchestration sources are retained as exact review-support
    # artifacts. Final tools have their own reviewed identities and receipts.
    tool_paths=set(batch['tools'].values())
    unchanged=[]
    for item in original['frozen_contracts']:
        ref=artifact_ref(item['artifact']);payload=store.read(ref)
        if ref.sha256!=item['sha256']:
            raise ValueError('original reviewed contract/source bytes changed')
        if item['path'] not in tool_paths:
            if package_path(item['path']).read_bytes()!=payload:
                raise ValueError('original frozen research contract changed')
            unchanged.append(byte_identity(item['path'],payload))
    effective=review['effective_contracts']
    if (type(effective) is not list or len({r['path'] for r in effective})!=len(effective)
            or any(local_identity(r['path'])!=r for r in effective)
            or any(r not in effective for r in unchanged)):
        raise ValueError('effective research contracts omit or change an original frozen contract')
    if review['repaired_orchestration_sources']!=[local_identity(p) for p in sorted(tool_paths)]:
        raise ValueError('final orchestration differs from its reviewed repair identity')
    rows = review['reviews']
    if len(rows) != len(batch['review_paths']) or {r['path'] for r in rows} != set(batch['review_paths']):
        raise ValueError('initial review omitted or substituted')
    findings = {}
    for row in rows:
        payload = package_path(row['path']).read_bytes()
        if (hashlib.sha256(payload).hexdigest() != row['sha256']
                or payload != store.read(artifact_ref(row['artifact']))
                or row['finding_key'] != batch['review_paths'][row['path']]):
            raise ValueError('retained initial reviewer bytes or selector changed')
        values = select(json.loads(payload), row['finding_key'])
        if type(values) is not list or any(type(v) is not dict for v in values):
            raise ValueError('review findings require explicit records')
        ids = [v['id'] for v in values]
        if (any(type(v) is not str or not v for v in ids) or len(ids) != len(set(ids))
                or sorted(ids) != sorted(row['finding_ids']) or set(ids) & set(findings)):
            raise ValueError('review finding IDs omitted or duplicated')
        findings.update({v['id']: v for v in values})
    if len(findings) != receipt['findings'] or set(review['dispositions']) != set(findings):
        raise ValueError('dispositions differ from the complete original finding union')
    repair_rows = review['repair_reports']
    if type(repair_rows) is not list or len({r['path'] for r in repair_rows}) != len(repair_rows):
        raise ValueError('distinct repair support reports required')
    repairs = {}
    for row in repair_rows:
        if local_identity(row['path'])['sha256'] != row['sha256']:
            raise ValueError('repair support bytes changed')
        value = json.loads(package_path(row['path']).read_bytes())['dispositions']
        repairs[row['path']] = value if type(value) is dict else indexed(value, 'id', 'repair dispositions')
    used = set()
    for key, disposition in review['dispositions'].items():
        support = disposition['repair_report']
        if (disposition['status'] not in RESOLVED or support not in repairs or key not in repairs[support]
                or repairs[support][key].get('status') != disposition['status']
                or not disposition.get('reason')):
            raise ValueError('finding lacks its explicit statically checked repair/no-change evidence')
        used.add(support)
    if used != set(repairs):
        raise ValueError('unused repair support report')
    passes = 1 if any(d['status'] == 'repaired_and_statically_verified' for d in review['dispositions'].values()) else 0
    if review['consolidated_repair_passes'] != passes:
        raise ValueError('one consolidated repair pass is required when repairs exist')
    return asdict(store.put_bytes(raw, kind='implementation_review'))


def baseline_assertions(store, batch):
    value = store.read_json(artifact_ref(batch['baseline_verification']))
    ids = value['passed_assertion_ids']
    if (value['success'] is not True or value['errors'] or value['failures'] or value['skipped']
            or len(ids) != value['tests_run'] or len(ids) != len(set(ids)) or not ids):
        raise ValueError('baseline does not prove a complete successful assertion population')
    return sorted(ids)
