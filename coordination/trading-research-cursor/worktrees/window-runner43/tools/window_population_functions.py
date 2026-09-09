def window_inputs(authenticated):
    extension = authenticated['extension']
    operational = load_reference(extension['window_population'])
    contract = load_reference(operational['scientific_contract'])
    prior = load_reference(operational['observation_execution'])
    source_worker = load_reference(operational['observation_worker'])
    if (prior.get('success') is not True or source_worker.get('success') is not True
            or prior['attempt_id'] != source_worker['attempt_id']
            or not source_worker['actual_observation_population']['all_population_materialized']):
        raise ValueError('window links require the accepted complete observation population')
    population_ref = source_worker['actual_observation_population']['reference']
    population = load_reference(population_ref, maximum=128 * 1024**2)
    contract = dict(contract, phase=operational['phase'],
                    selected_unit_ids=operational.get('selected_unit_ids'),
                    accepted_window_units=operational.get('accepted_window_units', []))
    for name, sha in operational.get('accepted_consumer_files', {}).items():
        checked(ROOT / name, sha)
    return operational, contract, population, population_ref


def window_allocation(cap):
    allowance = cap['maximum_output_bytes'] - cap['supervisor_output_reserve_bytes']
    return {'workers': 8, 'child_cpu_seconds': (cap['cpu_seconds'] - 120) // 8,
            'child_hard_cpu_seconds': (cap['cpu_seconds'] - 120) // 8 + 1,
            'child_output_bytes': (allowance - 512 * 1024**2) // 8,
            'child_address_space_bytes': 4 * 1024**3,
            'aggregate_address_space_bytes': 9 * 4 * 1024**3}


def window_shard(registered_packet_path, child_packet_path):
    bootstrap_process_limits()
    install_source_worker_signal_handlers()
    child = json.loads(checked(child_packet_path)[0])
    registered = json.loads(checked(registered_packet_path, maximum=2 * 1024**2)[0])
    require_parent_identity(coordinator_pid=child['coordinator_pid'], supervisor_pid=registered['supervisor_pid'])
    authenticated = authenticate_registered_packet(registered_packet_path)
    packet, cap = authenticated['packet'], authenticated['cap']
    operational, contract, population, _ = window_inputs(authenticated)
    allocation = window_allocation(cap)
    ordinal = child['ordinal']
    expected_packet = Path(registered_packet_path).parent / 'outputs' / f'window-shard-{ordinal:02d}-packet.json'
    expected_dir = expected_packet.parent / f'window-shard-{ordinal:02d}'
    if (type(ordinal) is not int or not 0 <= ordinal < allocation['workers']
            or packet['configuration']['mode'] != 'window-links'
            or child['attempt_id'] != packet['attempt_id'] or child['trial_id'] != packet['trial_id']
            or child['code_snapshot'] != packet['code_snapshot'] or child['configuration'] != packet['configuration']
            or child['allocation'] != allocation or child['coordinator_pid'] != os.getppid()
            or Path(child_packet_path).resolve() != expected_packet.resolve()
            or Path(child['output_directory']).resolve() != expected_dir.resolve()):
        raise ValueError('window shard identity or allocation differs')
    resource.setrlimit(resource.RLIMIT_CPU,
                       (allocation['child_cpu_seconds'], allocation['child_hard_cpu_seconds']))
    from trading_research.research.auction_flow_window_population import (
        plan_window_units, run_window_population, source_path_shard)
    from trading_research.research.auction_flow_storage import BoundedOutputs
    plan = plan_window_units(population, contract.get('selected_unit_ids'))
    paths = [path for path in plan['source_files'] if source_path_shard(path) == ordinal]
    if not paths or child['source_paths'] != paths:
        raise ValueError('window shard source paths differ from the frozen selection')
    outputs = BoundedOutputs(expected_dir, maximum_total_bytes=allocation['child_output_bytes'],
                             maximum_file_bytes=min(cap['maximum_output_file_bytes'], allocation['child_output_bytes']))
    actual = run_window_population(population=population, contract=dict(contract, source_paths=paths),
        outputs=outputs, load_reference=load_reference, finalize=True)
    outputs.json('result.json', {'passed': actual['passed'], 'attempt_id': packet['attempt_id'],
        'ordinal': ordinal, 'source_paths': paths, 'processed_source_windows': actual['processed_source_windows'],
        'population': actual['refs']['population']}, kind='auction_flow_window_shard_v1')
    return 0


def execute_window_shards(*, contract, population, outputs, packet_path, authenticated):
    from trading_research.research.auction_flow_window_population import (
        plan_window_units, run_window_population, source_path_shard)
    packet, cap = authenticated['packet'], authenticated['cap']
    allocation = window_allocation(cap)
    if allocation['aggregate_address_space_bytes'] > authenticated['live']['memory_limit_bytes']:
        raise ValueError('window workers exceed actual allocated memory')
    plan = plan_window_units(population, contract.get('selected_unit_ids'))
    jobs, directories, expected = [], {}, {}
    for ordinal in range(allocation['workers']):
        paths = [path for path in plan['source_files'] if source_path_shard(path) == ordinal]
        if not paths:
            continue
        directory = outputs.directory / f'window-shard-{ordinal:02d}'
        expected[ordinal] = paths
        directories[ordinal] = directory
        child = {'ordinal': ordinal, 'coordinator_pid': os.getpid(), 'attempt_id': packet['attempt_id'],
                 'trial_id': packet['trial_id'], 'code_snapshot': packet['code_snapshot'],
                 'configuration': packet['configuration'], 'allocation': allocation,
                 'source_paths': paths, 'output_directory': str(directory)}
        ref = outputs.json(f'window-shard-{ordinal:02d}-packet.json', child,
                           kind='auction_flow_window_shard_packet_v1')
        jobs.append({'ordinal': ordinal, 'argv': [sys.executable, str(Path(__file__).resolve()),
                     '--window-shard', str(Path(packet_path).resolve()), ref['path']],
                     'cwd': str(ROOT), 'env': dict(os.environ)})
    evidence = {}
    try:
        supervise_source_children(jobs, concurrency=min(allocation['workers'], len(jobs)),
            cpu_soft_seconds=cap['cpu_seconds'], cpu_hard_seconds=cap['hard_cpu_seconds'],
            wall_deadline_monotonic=time.monotonic() + cap['wall_seconds'] - 120,
            allocated_address_space_bytes=allocation['aggregate_address_space_bytes'], evidence=evidence)
    finally:
        outputs.written += sum(p.stat().st_size for directory in directories.values()
                               for p in directory.rglob('*') if p.is_file())
        if outputs.written > outputs.maximum_total:
            raise ValueError('window shard outputs exceeded aggregate reservation')
        apply_remaining_coordinator_cpu_limit(cap['cpu_seconds'], cap['hard_cpu_seconds'])
        outputs.json('window-parallel-execution.json', evidence, kind='auction_flow_window_parallel_execution_v1')
    joined, seen = [], set()
    for ordinal, directory in directories.items():
        result = json.loads(checked(directory / 'result.json')[0])
        if (result.get('passed') is not True or result['attempt_id'] != packet['attempt_id']
                or result['ordinal'] != ordinal or result['source_paths'] != expected[ordinal]
                or Path(result['population']['path']).resolve().parent != directory.resolve()):
            raise ValueError('window shard result does not join its assigned source paths')
        part = load_reference(result['population'], maximum=cap['maximum_output_file_bytes'])
        expected_ids = {tuple(item['unit_id']) for item in plan['selected'] if item['source_path'] in expected[ordinal]}
        actual_ids = {tuple(item['unit_id']) for item in part['units']}
        if actual_ids != expected_ids or len(part['units']) != len(expected_ids) or seen & actual_ids:
            raise ValueError('window shard result lost or duplicated source windows')
        seen.update(actual_ids)
        joined.extend(part['units'])
    if seen != {tuple(item['unit_id']) for item in plan['selected']}:
        raise ValueError('window shard join omitted source windows')
    # Finalization authenticates every exact cache key and reuses immutable unit outputs.
    final_contract = dict(contract, accepted_window_units=joined)
    actual = run_window_population(population=population, contract=final_contract, outputs=outputs,
        load_reference=load_reference, finalize=True)
    return actual, evidence


def window_population(authenticated, packet_path):
    import unittest
    from trading_research.operations.artifacts import canonical_json, publish_new
    from trading_research.research.auction_flow_window_population import run_window_population
    from trading_research.research.auction_flow_storage import BoundedOutputs
    packet, protocol, cap = authenticated['packet'], authenticated['protocol'], authenticated['cap']
    operational, contract, population, population_ref = window_inputs(authenticated)
    modules = operational['check_modules']
    if any(name not in authenticated['extension']['additional_check_modules'] for name in modules):
        raise ValueError('window checks are absent from the registered dependency closure')
    if operational['phase'] == 'full':
        pilot_execution = load_reference(operational['accepted_pilot_execution'])
        pilot_worker = load_reference(operational['accepted_pilot_worker'])
        if (pilot_execution.get('success') is not True or pilot_worker.get('success') is not True
                or pilot_execution['attempt_id'] != pilot_worker['attempt_id']):
            raise ValueError('window full phase lacks accepted measured pilot')
        projection = operational['measured_resource_projection']
        if (projection['cpu_seconds'] > cap['cpu_seconds']
                or projection['parallel_wall_seconds'] > cap['wall_seconds']
                or projection['output_bytes'] > cap['maximum_output_bytes']):
            raise ValueError('window full phase exceeds its retained measured resource gate')
    began = time.process_time()
    result = unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromNames(modules))
    tests = {'tests': result.testsRun, 'errors': len(result.errors), 'failures': len(result.failures),
             'success': result.wasSuccessful(), 'cpu_seconds': time.process_time()-began}
    if not tests['success']:
        raise ValueError('causal window regressions failed; preserve and reassess before data execution')
    outputs = BoundedOutputs(Path(packet_path).parent/'outputs',
        maximum_total_bytes=cap['maximum_output_bytes']-cap['supervisor_output_reserve_bytes'],
        maximum_file_bytes=cap['maximum_output_file_bytes'])
    evidence = None
    if operational.get('parallel_execution'):
        actual, evidence = execute_window_shards(contract=contract, population=population,
            outputs=outputs, packet_path=packet_path, authenticated=authenticated)
    else:
        actual = run_window_population(population=population, contract=contract, outputs=outputs,
            load_reference=load_reference, finalize=True)
    brief = {key: value for key, value in actual.items() if key not in ('units', 'measurements')}
    # Unit refs, schema and original lineage remain in the authenticated population manifest.
    brief['refs'] = {key: value for key, value in actual['refs'].items() if key != 'units'}
    report = {key: packet[key] for key in
        ('attempt_id','trial_id','protocol_sha256','code_snapshot','tools_snapshot','configuration')}
    report.update(family=protocol['family'], mode='window-links', tests=tests, success=actual['passed'],
        actual_window_population=brief, input_population=population_ref,
        source_component_reused=True, source_component_verified=False,
        source_unit_parallel_execution=evidence, runtime_versions=authenticated['versions'],
        derived_output_bytes=outputs.written,
        scope='Actual causal formation and forward-label population; statistical analysis and full family validation remain separate.')
    publish_new(Path(packet['worker_report']), canonical_json(report)+b'\n')
    return 0 if report['success'] else 1
