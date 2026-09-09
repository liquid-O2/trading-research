def window_statistics_inputs(authenticated):
    operational = load_reference(authenticated['extension']['window_statistics'])
    contract = load_reference(operational['scientific_contract'])
    prior = load_reference(operational['source_execution'])
    source_worker = load_reference(operational['source_worker'])
    population_summary = source_worker.get('actual_window_population', {})
    if (prior.get('success') is not True or source_worker.get('success') is not True
            or prior['attempt_id'] != source_worker['attempt_id'] or prior.get('mode') != 'window-links'
            or population_summary.get('phase') != 'full'
            or population_summary.get('processed_source_windows') != 3589
            or population_summary.get('raw_source_scans') != 0):
        raise ValueError('window statistics require accepted full retained-window population')
    reference = population_summary['refs']['population']
    population = load_reference(reference, maximum=512*1024**2)
    if len(population.get('units', [])) != 3589:
        raise ValueError('complete original window-unit membership required')
    for name, sha in operational['accepted_consumer_files'].items():
        checked(ROOT/name, sha)
    contract = dict(contract, accepted_partitions=operational.get('accepted_partitions', []))
    return operational, contract, population, reference


def window_statistics_selected_keys(operational, contract, population):
    from trading_research.research.auction_flow_window_statistics import window_partition_plan
    plan = window_partition_plan(population['units'], collections=contract['source_collections'])
    keys = [list(k) for k in plan['keys']]
    selected = operational.get('selected_partition_keys')
    if selected is None:
        return keys
    if not selected or len({tuple(k) for k in selected}) != len(selected) or any(k not in keys for k in selected):
        raise ValueError('statistical partition selection must be a complete declared member')
    return selected


def window_statistics_allocation(operational, selected, cap):
    count = len(selected)
    concurrency = min(int(operational.get('concurrency', 1)), count)
    if count < 1 or concurrency < 1 or concurrency > 16:
        raise ValueError('bounded statistical partition allocation required')
    cpu = (cap['cpu_seconds']-300)//count
    output = (cap['maximum_output_bytes']-cap['supervisor_output_reserve_bytes']-256*1024**2)//(count+1)
    if cpu < 10 or output < 1024**2:
        raise ValueError('insufficient statistical partition reservation')
    return {'jobs':count,'concurrency':concurrency,'child_cpu_seconds':cpu,'child_hard_cpu_seconds':cpu+1,
        'child_output_bytes':output,'child_address_space_bytes':cap['memory_bytes'],
        'aggregate_address_space_bytes':(concurrency+1)*cap['memory_bytes']}


def window_statistics_shard(registered_packet_path, child_packet_path):
    bootstrap_process_limits()
    install_source_worker_signal_handlers()
    child = json.loads(checked(child_packet_path)[0])
    registered = json.loads(checked(registered_packet_path,maximum=2*1024**2)[0])
    require_parent_identity(coordinator_pid=child['coordinator_pid'],supervisor_pid=registered['supervisor_pid'])
    authenticated = authenticate_registered_packet(registered_packet_path)
    packet,cap = authenticated['packet'],authenticated['cap']
    operational,contract,population,_ = window_statistics_inputs(authenticated)
    selected = window_statistics_selected_keys(operational,contract,population)
    allocation = window_statistics_allocation(operational,selected,cap)
    ordinal = child['ordinal']
    expected_packet=Path(registered_packet_path).parent/'outputs'/f'window-statistics-shard-{ordinal:02d}-packet.json'
    directory=expected_packet.parent/f'window-statistics-shard-{ordinal:02d}'
    if (type(ordinal) is not int or not 0 <= ordinal < len(selected)
            or child['partition_key'] != selected[ordinal] or child['allocation'] != allocation
            or child['attempt_id'] != packet['attempt_id'] or child['trial_id'] != packet['trial_id']
            or child['code_snapshot'] != packet['code_snapshot'] or child['configuration'] != packet['configuration']
            or child['coordinator_pid'] != os.getppid() or packet['configuration']['mode'] != 'window-statistics'
            or Path(child_packet_path).resolve() != expected_packet.resolve()
            or Path(child['output_directory']).resolve() != directory.resolve()):
        raise ValueError('statistical shard identity or allocation mismatch')
    resource.setrlimit(resource.RLIMIT_CPU,(allocation['child_cpu_seconds'],allocation['child_hard_cpu_seconds']))
    from trading_research.research.auction_flow_window_statistics import run_window_statistics
    from trading_research.research.auction_flow_storage import BoundedOutputs
    outputs=BoundedOutputs(directory,maximum_total_bytes=allocation['child_output_bytes'],
                           maximum_file_bytes=min(cap['maximum_output_file_bytes'],allocation['child_output_bytes']))
    actual=run_window_statistics(population=population,contract=contract,outputs=outputs,
        load_reference=load_reference,selected_partition_keys=[selected[ordinal]])
    outputs.json('result.json',{'passed':actual['passed'],'attempt_id':packet['attempt_id'],'ordinal':ordinal,
        'partition_key':selected[ordinal],'actual':actual},kind='auction_flow_window_statistics_shard_v1')
    return 0


def execute_window_statistics_shards(*, operational, contract, population, outputs, packet_path, authenticated):
    from trading_research.research.auction_flow_window_statistics import (
        window_partition_plan,window_partition_identity,window_partition_source_refs)
    packet,cap=authenticated['packet'],authenticated['cap']
    selected=window_statistics_selected_keys(operational,contract,population)
    allocation=window_statistics_allocation(operational,selected,cap)
    if allocation['aggregate_address_space_bytes']>authenticated['live']['memory_limit_bytes']:
        raise ValueError('statistical consumers exceed actual memory allocation')
    jobs=[];directories=[]
    for ordinal,key in enumerate(selected):
        directory=outputs.directory/f'window-statistics-shard-{ordinal:02d}'
        child={'ordinal':ordinal,'coordinator_pid':os.getpid(),'attempt_id':packet['attempt_id'],
            'trial_id':packet['trial_id'],'code_snapshot':packet['code_snapshot'],'configuration':packet['configuration'],
            'allocation':allocation,'partition_key':key,'output_directory':str(directory)}
        ref=outputs.json(f'window-statistics-shard-{ordinal:02d}-packet.json',child,kind='auction_flow_window_statistics_shard_packet_v1')
        jobs.append({'ordinal':ordinal,'argv':[sys.executable,str(Path(__file__).resolve()),'--window-statistics-shard',str(Path(packet_path).resolve()),ref['path']],
            'cwd':str(ROOT),'env':dict(os.environ)})
        directories.append(directory)
    evidence={}
    try:
        supervise_source_children(jobs,concurrency=allocation['concurrency'],cpu_soft_seconds=cap['cpu_seconds'],
            cpu_hard_seconds=cap['hard_cpu_seconds'],wall_deadline_monotonic=time.monotonic()+cap['wall_seconds']-120,
            allocated_address_space_bytes=allocation['aggregate_address_space_bytes'],evidence=evidence)
    finally:
        outputs.written+=sum(p.stat().st_size for d in directories for p in d.rglob('*') if p.is_file())
        if outputs.written>outputs.maximum_total:raise ValueError('statistical shards exceeded aggregate output')
        apply_remaining_coordinator_cpu_limit(cap['cpu_seconds'],cap['hard_cpu_seconds'])
        outputs.json('window-statistics-parallel-execution.json',evidence,kind='auction_flow_window_statistics_parallel_v1')
    plan=window_partition_plan(population['units'],collections=contract['source_collections'])
    accepted={load_reference(r,maximum=128*1024**2)['identity'] for r in contract.get('accepted_partitions',[])}
    refs=[];measurements=[]
    for ordinal,directory in enumerate(directories):
        result=json.loads(checked(directory/'result.json')[0]);key=selected[ordinal]
        if (result.get('passed') is not True or result['attempt_id']!=packet['attempt_id'] or result['ordinal']!=ordinal
                or result['partition_key']!=key or len(result['actual']['refs']['partitions'])!=1):
            raise ValueError('statistical shard output failed exact partition join')
        ref=result['actual']['refs']['partitions'][0];part=load_reference(ref,maximum=128*1024**2)
        expected=window_partition_identity(contract,collection=key[0],root=key[1],year=key[2],
            source_refs=window_partition_source_refs(plan['members'][tuple(key)]))
        if part['identity']!=expected or part.get('passed') is not True:
            raise ValueError('statistical shard source/science identity differs')
        if expected not in accepted and Path(ref['path']).resolve().parent!=directory.resolve():
            raise ValueError('statistical shard artifact escaped registered namespace')
        refs.append(ref);measurements.append({**part['measurement'],'partition_key':key,'reused':expected in accepted})
    return refs,evidence,measurements


def window_statistics(authenticated,packet_path):
    import unittest
    from trading_research.operations.artifacts import canonical_json,publish_new
    from trading_research.research.auction_flow_window_statistics import run_window_statistics
    from trading_research.research.auction_flow_storage import BoundedOutputs
    packet,protocol,cap=authenticated['packet'],authenticated['protocol'],authenticated['cap']
    operational,contract,population,population_ref=window_statistics_inputs(authenticated)
    modules=operational['check_modules']
    if not modules or any(m not in authenticated['extension']['additional_check_modules'] for m in modules):
        raise ValueError('statistical checks missing from registered dependency closure')
    began=time.process_time();result=unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromNames(modules))
    tests={'tests':result.testsRun,'errors':len(result.errors),'failures':len(result.failures),'success':result.wasSuccessful(),'cpu_seconds':time.process_time()-began}
    if not tests['success']:raise ValueError('window-statistics regression failure; no actual reduction')
    projection=None
    if operational['phase']=='full':
        pilot=load_reference(operational['accepted_pilot_execution']);worker=load_reference(operational['accepted_pilot_worker'])
        if (pilot.get('success') is not True or worker.get('success') is not True or pilot['attempt_id']!=worker['attempt_id']
                or worker.get('mode')!='window-statistics'):
            raise ValueError('full statistics require successful own-family pilot')
        projection=operational['measured_resource_projection']
        if (projection['cpu_seconds']>cap['cpu_seconds'] or projection['wall_seconds']>cap['wall_seconds']
                or projection['output_bytes']>cap['maximum_output_bytes']):
            raise ValueError('measured statistical full-population gate exceeds retained budget')
    outputs=BoundedOutputs(Path(packet_path).parent/'outputs',maximum_total_bytes=cap['maximum_output_bytes']-cap['supervisor_output_reserve_bytes'],maximum_file_bytes=cap['maximum_output_file_bytes'])
    evidence=None
    selected=operational.get('selected_partition_keys')
    if operational.get('concurrency',1)>1:
        refs,evidence,measurements=execute_window_statistics_shards(operational=operational,contract=contract,population=population,outputs=outputs,packet_path=packet_path,authenticated=authenticated)
        parent_contract={**contract,'accepted_partitions':refs}
        actual=run_window_statistics(population=population,contract=parent_contract,outputs=outputs,load_reference=load_reference,selected_partition_keys=selected)
        actual['coordinator_finalization_cpu_seconds']=actual['cpu_seconds']
        actual['partition_measurements']=measurements
    else:
        actual=run_window_statistics(population=population,contract=contract,outputs=outputs,load_reference=load_reference,selected_partition_keys=selected)
    report={k:packet[k] for k in ('attempt_id','trial_id','protocol_sha256','code_snapshot','tools_snapshot','configuration')}
    report.update(family=protocol['family'],mode='window-statistics',tests=tests,success=actual['passed'],
        actual_window_statistics=actual,input_population=population_ref,source_component_reused=True,
        source_component_verified=False,source_unit_parallel_execution=evidence,runtime_versions=authenticated['versions'],
        measured_resource_projection=projection,derived_output_bytes=outputs.written,
        scope='Actual formation/delay/forward-label/event descriptive statistics; no complete auction-family or Context claim.')
    publish_new(Path(packet['worker_report']),canonical_json(report)+b'\n')
    return 0 if report['success'] else 1


