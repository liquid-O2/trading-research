from pathlib import Path
import ast,hashlib,shutil
p=Path('/workspace/trading-research/tools/run_auction_flow_study.py')
old=p.read_text()
backup=Path('/workspace/coordination/trading-research-cursor/profile-reference-runner-before1.py')
if not backup.exists():shutil.copy2(p,backup)
start=old.index('def window_statistics_inputs(');end=old.index('\ndef core_parallel_execution(',start)
block=old[start:end].replace('window_statistics','profile_statistics').replace('window-statistics','profile-statistics').replace('window_partition','profile_partition').replace('actual_window_population','actual_profile_population')
a=block.index('def profile_statistics_inputs(');b=block.index('\ndef profile_statistics_selected_keys(',a)
block=block[:a]+'''def profile_statistics_inputs(authenticated):
    operational=load_reference(authenticated['extension']['profile_statistics'])
    contract=load_reference(operational['scientific_contract'])
    if contract.get('kind')!='auction_flow_profile_reference_statistics_contract_v1':
        raise ValueError('full frozen profile science contract required')
    for name,sha in operational['accepted_consumer_files'].items():checked(ROOT/name,sha)
    for name,mode,key in (('observations','observations','actual_observation_population'),('windows','window-links','actual_window_population')):
        execution=load_reference(operational[name+'_execution'])
        worker=load_reference(operational[name+'_worker'])
        if (execution.get('success') is not True or worker.get('success') is not True
                or execution['attempt_id']!=worker['attempt_id'] or worker.get('mode')!=mode):
            raise ValueError('profile inputs require successful complete retained predecessor')
        summary=worker.get(key,{})
        if summary.get('phase')!='full' or summary.get('processed_source_windows')!=3589:
            raise ValueError('profile source membership must be the accepted3589windows')
    refs=contract['input_populations']
    population=load_reference(refs['observations39'],maximum=128*1024**2)
    windows=load_reference(refs['windows46'],maximum=512*1024**2)
    if len(population.get('units',[]))!=3589 or len(windows.get('units',[]))!=3589:
        raise ValueError('complete observation and window populations required')
    collections=load_reference(operational['source_collection_contract'])['source_collections']
    contract=dict(contract,source_collections=collections,accepted_partitions=operational.get('accepted_partitions',[]))
    return operational,contract,population,windows,refs

'''+block[b:]
block=block.replace("plan = profile_partition_plan(population['units'], collections=contract['source_collections'])","plan = profile_partition_plan(population, contract)")
block=block.replace('operational,contract,population,_ = profile_statistics_inputs(authenticated)','operational,contract,population,windows,_ = profile_statistics_inputs(authenticated)')
block=block.replace('operational,contract,population,population_ref=profile_statistics_inputs(authenticated)','operational,contract,population,windows,population_ref=profile_statistics_inputs(authenticated)')
block=block.replace('population=population,contract=contract,outputs=outputs,','population=population,window_population=windows,contract=contract,outputs=outputs,')
block=block.replace('def execute_profile_statistics_shards(*, operational, contract, population, outputs, packet_path, authenticated):','def execute_profile_statistics_shards(*, operational, contract, population, windows, outputs, packet_path, authenticated):')
block=block.replace('execute_profile_statistics_shards(operational=operational,contract=contract,population=population,outputs=outputs,','execute_profile_statistics_shards(operational=operational,contract=contract,population=population,windows=windows,outputs=outputs,')
block=block.replace('population=population,contract=parent_contract,outputs=outputs,','population=population,window_population=windows,contract=parent_contract,outputs=outputs,')
block=block.replace('profile_partition_plan,profile_partition_identity,profile_partition_source_refs)','profile_partition_plan,profile_partition_identity,profile_partition_source_refs,neighbor_units,window_unit_refs)')
block=block.replace("plan=profile_partition_plan(population['units'],collections=contract['source_collections'])","plan=profile_partition_plan(population,contract)")
needle="""        expected=profile_partition_identity(contract,collection=key[0],root=key[1],year=key[2],
            source_refs=profile_partition_source_refs(plan['members'][tuple(key)]))"""
replacement="""        members=plan['members'][tuple(key)]
        neighbors=neighbor_units(plan,tuple(key),collections=contract['source_collections'])
        support=list(members)+list(neighbors)
        unique={ (u.get('source_path'),u.get('root'),u.get('source_window_start_ns'),u.get('source_window_end_ns')):u for u in support }
        source_refs=profile_partition_source_refs(list(unique.values()))
        paths={u['source_path'] for u in unique.values()}
        expected=profile_partition_identity(contract,collection=key[0],root=key[1],year=key[2],
            source_refs=source_refs,window_refs=window_unit_refs(windows['units'],paths=paths))"""
if needle not in block:raise ValueError('profile shard identity template changed')
block=block.replace(needle,replacement)
block=block.replace("'statistical partition allocation required'","'profile partition allocation required'")
block=block.replace('concurrency > 16','concurrency > 8')
block=block.replace("cpu = (cap['cpu_seconds']-300)//count","cpu = cap['cpu_seconds']-300")
block=block.replace("'Actual formation/delay/forward-label/event descriptive statistics; no complete auction-family or Context claim.'","'Actual profile/reference/TPO/VWAP/footprint and forward geometry statistics; no complete auction-family or Context claim.'")
block=block.replace("        projection=operational['measured_resource_projection']","""        pilot_operation=load_reference(operational['accepted_pilot_operational'])
        if (pilot_operation['scientific_contract']!=operational['scientific_contract']
                or pilot_operation['accepted_consumer_files']!=operational['accepted_consumer_files']):
            raise ValueError('full profiles require unchanged tested science and consumer implementations')
        projection=operational['measured_resource_projection']""")
s=old[:end]+ '\n\n'+block+old[end:]
s=s.replace("'window-links', 'window-statistics')","'window-links', 'window-statistics', 'profile-statistics')",1)
s=s.replace("    if mode == 'window-statistics':\n        declared_extension", "    if mode in ('window-statistics','profile-statistics'):\n        declared_extension",1)
s=s.replace("operation = load_reference(declared_extension['window_statistics'])","operation = load_reference(declared_extension['profile_statistics' if mode=='profile-statistics' else 'window_statistics'])",1)
s=s.replace("        if packet['configuration']['mode'] == 'window-statistics':", "        if packet['configuration']['mode'] == 'profile-statistics':\n            return profile_statistics(authenticated,packet_path)\n        if packet['configuration']['mode'] == 'window-statistics':",1)
s=s.replace("        else 'formation/delay/forward-label/event descriptive statistics'", "        else 'profile/reference/TPO/VWAP/footprint and future geometry statistics' if mode == 'profile-statistics'\n        else 'formation/delay/forward-label/event descriptive statistics'",1)
s=s.replace("mode in ('core-statistics','window-statistics')", "mode in ('core-statistics','window-statistics','profile-statistics')",1)
s=s.replace("    if len(sys.argv) == 4 and sys.argv[1] == '--window-statistics-shard':", "    if len(sys.argv) == 4 and sys.argv[1] == '--profile-statistics-shard':\n        raise SystemExit(profile_statistics_shard(sys.argv[2],sys.argv[3]))\n    if len(sys.argv) == 4 and sys.argv[1] == '--window-statistics-shard':",1)
ast.parse(s);p.write_text(s)
print({'path':str(p),'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'added_lines':len(s.splitlines())-len(old.splitlines())})
