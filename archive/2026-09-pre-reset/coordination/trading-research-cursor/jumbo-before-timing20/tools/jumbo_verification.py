"""Static phase-specific verification identities; no candidate code is imported.

The complete repository snapshot remains the reproducibility record. A check's
applicability is instead tied to declared entry points, their local imports,
phase dispatch boundaries, exact tests, semantic inputs and runtime providers.
"""
import ast
import hashlib
import json
from pathlib import Path

ENTRYPOINTS = {
    'extract': ('jumbo_study','jumbo_tables','jumbo_report','jumbo_narrative','jumbo_anchors','jumbo_definition_supersession','jumbo_source_reuse'),
    'fit': ('jumbo_study','jumbo_pipeline','jumbo_matrix','jumbo_targets','jumbo_models','jumbo_fitting','jumbo_model_backend',
            'jumbo_model_evaluation','jumbo_baselines','jumbo_clock_comparison','jumbo_special_targets','jumbo_special_models'),
    'confirmation': ('jumbo_descriptive_confirmation','jumbo_study','jumbo_pipeline','jumbo_matrix','jumbo_targets','jumbo_models','jumbo_fitting',
            'jumbo_model_backend','jumbo_model_evaluation','jumbo_clock_comparison','jumbo_special_targets','jumbo_special_models',
            'jumbo_anchors',
            'jumbo_definition_supersession','jumbo_report','jumbo_narrative'),
    'admission': ('jumbo_study',),
}
TESTS = {
    'extract': ('test_ohlc_ranges','test_ohlc_admission','test_ohlc_mechanisms','test_date_statistics',
                'test_jumbo_tables','test_jumbo_report','test_jumbo_narrative','test_jumbo_anchors','test_jumbo_definition_supersession','test_trial_budget_amendment'),
    'fit': ('test_jumbo_matrix','test_jumbo_targets','test_jumbo_baselines','test_jumbo_models',
            'test_jumbo_model_backend','test_jumbo_model_evaluation','test_jumbo_evaluation_storage','test_jumbo_clock_comparison',
            'test_jumbo_special_targets','test_jumbo_special_models','test_jumbo_fitting','test_jumbo_verification','test_trial_budget_amendment'),
    'confirmation': ('test_jumbo_descriptive_confirmation',),
    'admission': ('test_ohlc_admission',),
}
# These modules are imported only by the named dispatcher after mode/phase
# selection. The dispatcher itself is always hashed. All actual reachable
# measurement/model imports below an allowed entry point are included.
PHASE_DISPATCH_MODULES = {f'trading_research.research.{n}' for v in ENTRYPOINTS.values() for n in v}


def _json_digest(value):
    return hashlib.sha256(json.dumps(value,sort_keys=True,separators=(',',':'),allow_nan=False).encode()).hexdigest()


def retained_function_fingerprint(source, name):
    """Identity of an explicitly scoped function, excluding line locations."""
    matches = [node for node in ast.parse(source).body
               if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == name]
    if len(matches) != 1:
        raise ValueError("one retained function required")
    return hashlib.sha256(ast.dump(matches[0], include_attributes=False).encode()).hexdigest()


def annual_stage_fingerprint(source):
    """Exact existing extraction/statistics/serialization/parity statements.

    The old registered function has this block at top level. The reuse path
    retains it inside an else branch; its AST must be identical. This narrow
    contract permits changed later consumers without accepting changed annual
    computations on the strength of an old partial success.
    """
    functions = [node for node in ast.parse(source).body
                 if isinstance(node, ast.FunctionDef) and node.name == "_check_actual_annual_extraction"]
    if len(functions) != 1:
        raise ValueError("one annual check function required")
    matches = []
    for parent in ast.walk(functions[0]):
        for _, body in ast.iter_fields(parent):
            if not isinstance(body, list) or not body or not all(isinstance(n, ast.stmt) for n in body):
                continue
            starts = [i for i, n in enumerate(body) if isinstance(n, ast.Assign)
                      and any(isinstance(t, ast.Name) and t.id == "batch" for t in n.targets)
                      and isinstance(n.value, ast.Dict)]
            ends = [i for i, n in enumerate(body) if isinstance(n, ast.Delete)
                    and {t.id for t in n.targets if isinstance(t, ast.Name)} ==
                    {"payload", "compressed_statistics", "original_statistics", "statistics"}]
            if len(starts) == len(ends) == 1 and starts[0] < ends[0]:
                matches.append(ast.Module(body=body[starts[0]:ends[0] + 1], type_ignores=[]))
    if len(matches) != 1:
        raise ValueError("one unchanged annual measurement block required")
    return hashlib.sha256(ast.dump(matches[0], include_attributes=False).encode()).hexdigest()


def _module_path(name, manifest):
    if not name.startswith('trading_research'):
        return None
    stem='src/'+name.replace('.','/')
    for path in (stem+'.py',stem+'/__init__.py'):
        if path in manifest:
            return path
    return None


def phase_contracts(root, manifest, *, analysis_plan, execution_plan, model_plan, runtime_versions):
    root=Path(root)
    result={}
    for phase,names in ENTRYPOINTS.items():
        entry={f'trading_research.research.{n}' for n in names}
        seen={}
        pending=list(entry)
        while pending:
            module=pending.pop()
            path=_module_path(module,manifest)
            if path is None:
                raise ValueError(f'required {phase} entry/import is absent: {module}')
            if path in seen:
                continue
            raw=(root/path).read_bytes()
            sha=hashlib.sha256(raw).hexdigest()
            if sha!=manifest[path]:
                raise ValueError('phase verification source changed after complete snapshot')
            seen[path]=sha
            tree=ast.parse(raw,filename=path)
            for node in ast.walk(tree):
                dependencies=[]
                if isinstance(node,ast.Import):
                    dependencies=[alias.name for alias in node.names]
                elif isinstance(node,ast.ImportFrom):
                    base=node.module or ''
                    if node.level:
                        parts=module.split('.')
                        base='.'.join(parts[:-node.level]+([base] if base else []))
                    dependencies=[base]+[base+'.'+alias.name for alias in node.names if alias.name!='*']
                for dep in dependencies:
                    if _module_path(dep,manifest) is None:
                        continue
                    if module=='trading_research.research.jumbo_study' and dep in PHASE_DISPATCH_MODULES and dep not in entry:
                        continue
                    pending.append(dep)
        tests=TESTS[phase] if phase!='confirmation' else tuple(sorted(set(TESTS['extract']+TESTS['fit']+TESTS['confirmation'])))
        for name in tests:
            path='tests/'+name+'.py'
            if path not in manifest:
                raise ValueError(f'required {phase} consumer test is absent: {path}')
            raw=(root/path).read_bytes()
            if hashlib.sha256(raw).hexdigest()!=manifest[path]:
                raise ValueError("relevant test changed after complete snapshot")
            seen[path]=manifest[path]
        contract={'version':'jumbo-phase-verification-v1','phase':phase,'entrypoints':sorted(entry),
                  'source_and_test_files':dict(sorted(seen.items())),
                  'analysis_plan':analysis_plan,'execution_plan':execution_plan,
                  'model_plan':model_plan if phase in ('fit','confirmation') else None,
                  'runtime_versions':runtime_versions,
                  'dispatch_rule':'Exact dispatcher bytes + explicitly declared mode branch; other phase implementation is separately verified',
                  'complete_snapshot_retained':True}
        contract['id']=_json_digest(contract)
        result[phase]=contract
    return result


def _nonneg_real(value):
    return type(value) in (int, float) and value >= 0 and value == value and value != float('inf')


def descriptive_confirmation_from_predecessor(predecessor, *, mode='confirm'):
    """True only for an authenticated successful develop/extract predecessor."""
    return (mode == 'confirm' and predecessor is not None
            and predecessor.get('success') is True
            and predecessor.get('mode') == 'develop'
            and predecessor.get('phase') == 'extract')


def authenticate_descriptive_confirmation(flag, predecessor, configured=None, *, mode='confirm'):
    """Packet flag must match the registered trial and the exact predecessor."""
    expected = descriptive_confirmation_from_predecessor(predecessor, mode=mode)
    if flag is not True and flag is not False:
        raise ValueError('descriptive_confirmation must be an explicit boolean')
    if configured is not None and configured is not flag:
        raise ValueError('descriptive_confirmation does not match the registered trial')
    if flag is not expected:
        raise ValueError('descriptive_confirmation does not match the exact predecessor')
    return expected


def descriptive_confirmation_feasible(projected_cpu_seconds, projected_output_bytes,
                                     cpu_cap_seconds, output_cap_bytes):
    """Independent pass/fail from literal extract costing and confirmation caps.

    Does not read or return a stored feasibility flag. A boolean True cannot
    stand in for a projection or a cap.
    """
    if not all(_nonneg_real(v) for v in (
            projected_cpu_seconds, projected_output_bytes, cpu_cap_seconds, output_cap_bytes)):
        return False
    return (projected_cpu_seconds <= cpu_cap_seconds
            and projected_output_bytes <= output_cap_bytes)


def descriptive_confirmation_projection(model_preflight):
    """Join existing check projection fields; do not invent a True feasibility flag."""
    if not isinstance(model_preflight, dict):
        return None
    cpu = model_preflight.get('projected_confirmation_extraction_cpu_seconds_conservative')
    total = model_preflight.get('projected_confirmation_output_bytes_conservative')
    model_out = model_preflight.get('projected_confirmation_model_output_bytes_conservative')
    if not all(_nonneg_real(v) for v in (cpu, total, model_out)) or total < model_out:
        return None
    return {'projected_cpu_seconds': cpu, 'projected_output_bytes': total - model_out}


def confirmation_feasibility(parity, *, descriptive_confirmation, cpu_cap_seconds, output_cap_bytes):
    """Current check feasibility: extract costing when descriptive, model cap otherwise."""
    if not isinstance(parity, dict) or parity.get('passed') is not True:
        return False
    model = parity.get('model_preflight') or {}
    if descriptive_confirmation is True:
        projection = descriptive_confirmation_projection(model)
        if projection is None:
            return False
        return descriptive_confirmation_feasible(
            projection['projected_cpu_seconds'], projection['projected_output_bytes'],
            cpu_cap_seconds, output_cap_bytes)
    return model.get('within_declared_confirmation_cap') is True
