from pathlib import Path
p=Path('/workspace/trading-research/src/trading_research/research/options_quote_statistics.py');s=p.read_text()
s=s.replace('''                key = tuple(item['key'])
                if len(key) != 7 or type(key[-1]) is not bool:
                    raise IntegrityError('pooled quote histogram key is invalid')
                vv, cc = _typed_histogram(item['v'], item['c'])
                pooled_bins += len(vv)
                self.pool[key] = _merge_exact_histograms(self.pool.get(key), (vv, cc))''','''                keys = [tuple(item['key']), *(tuple(key) for key in item.get('aliases',[]))]
                if len(set(keys)) != len(keys) or any(len(key) != 7 or type(key[-1]) is not bool for key in keys):
                    raise IntegrityError('pooled quote histogram key is invalid')
                vv, cc = _typed_histogram(item['v'], item['c'])
                for key in keys:
                    pooled_bins += len(vv)
                    self.pool[key] = _merge_exact_histograms(self.pool.get(key), (vv, cc))''')
s=s.replace('''        for key, (values, counts) in sorted(self.pool.items()):
            for begin in range(0, len(values), maximum_part_bins):''','''        import hashlib
        equal_histograms = {}
        for key,(values,counts) in sorted(self.pool.items()):
            identity = hashlib.sha256(values.tobytes() + counts.tobytes()).hexdigest()
            if identity not in equal_histograms:
                equal_histograms[identity] = {'keys':[],'values':values,'counts':counts}
            equal_histograms[identity]['keys'].append(key)
        stored_bins = 0
        for item in equal_histograms.values():
            keys,values,counts = item['keys'],item['values'],item['counts']
            for begin in range(0, len(values), maximum_part_bins):''')
s=s.replace("records.append({'key': list(key), 'v': values[begin:end].tolist(), 'c': counts[begin:end].tolist()})", "records.append({'key':list(keys[0]),'aliases':[list(key) for key in keys[1:]],\n                    'v':values[begin:end].tolist(),'c':counts[begin:end].tolist()})")
s=s.replace('''                total_bins += end - begin
        flush()''','''                total_bins += (end - begin)*len(keys)
                stored_bins += end - begin
        flush()''')
s=s.replace("'input_bins': self.input_bins, 'pooled_bins': total_bins,", "'input_bins':self.input_bins,'pooled_bins':total_bins,'stored_bins':stored_bins,")
s=s.replace("'pooled_bins': sum(ref['pooled_bins'] for ref in pools.values()),", "'pooled_bins':sum(ref['pooled_bins'] for ref in pools.values()),\n        'stored_bins':sum(ref.get('stored_bins',ref['pooled_bins']) for ref in pools.values()),")
s=s.replace('''    oi_listing_files_read=0, oi_listing_rows_read=0, oi_listing_bytes_read=0, phase_cpu=None,
):''','''    oi_listing_files_read=0, oi_listing_rows_read=0, oi_listing_bytes_read=0, phase_cpu=None,
    calculate_statistics=True,
):''')
a=s.index('    stats = run_statistics(',s.index('def finish_quote_outputs'));b=s.index('    cpu = pytime.process_time()',a)
block=s[a:b];block='    if calculate_statistics:\n'+''.join('    '+line+'\n' for line in block.rstrip().splitlines())+'''    else:
        stats = {'refs':{'statistics':None,'distributions':None,'results_md':None,'chain_groups':{}},
                 'group_count':0}
''';s=s[:a]+block+s[b:]
s=s.replace('''        "joined_coverage_complete": bool(joined_coverage_complete),''','''        "joined_coverage_complete": bool(joined_coverage_complete),
        "statistics_performed": bool(calculate_statistics),''')
p.write_text(s)
p=Path('/workspace/trading-research/src/trading_research/research/options_quote_measurements.py');s=p.read_text();s=s.replace('''        selected_chains=None):''','''        selected_chains=None, calculate_statistics=True, execution_resources=None):''',1)
s=s.replace('''        oi_listing_bytes_read=oi_join.listing_bytes_read,
    )''','''        oi_listing_bytes_read=oi_join.listing_bytes_read, calculate_statistics=calculate_statistics,
    )''',1)
s=s.replace('''max_worker_bytes=int(spec.get("resources", {}).get("memory_bytes", MAX_WORKER_BYTES)),''','''max_worker_bytes=int((execution_resources or spec.get("resources", {})).get("memory_bytes",MAX_WORKER_BYTES)),''')
p.write_text(s)
import ast
for p in (Path('/workspace/trading-research/src/trading_research/research/options_quote_statistics.py'),Path('/workspace/trading-research/src/trading_research/research/options_quote_measurements.py')):ast.parse(p.read_text())
print('storage and single final reduction ready')
