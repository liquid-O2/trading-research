import copy
import hashlib
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path('/workspace')
OUT = Path('/tmp/phase15-foundation-review-20260914')
sys.path.insert(0, str(ROOT / 'implementation/src'))
from decimal import Decimal
from trading_research.research.contracts.types import Coverage, EvidenceRef, NativeTrade, Reference, Forecast

PYTHON = ROOT / 'implementation/.venv/bin/python'
CLI = ROOT / 'implementation/tools/verify_research_release.py'
R0 = ROOT / 'implementation/reports/research-work/P15-00/b291864ccceaca9a/attempt-0001/TASK_RECEIPT.json'
R1 = ROOT / 'implementation/reports/research-work/P15-01/039267553e8bf721/attempt-0001/TASK_RECEIPT.json'
RS = ROOT / 'implementation/reports/research-work/00-foundation/f7135f8d696ff1f5/attempt-0001/SUBPHASE_RECEIPT.json'

def write(name, payload):
    path = OUT / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + '\n')
    return path

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

results = []
def run(name, mode, path, *extra, expected=2):
    flag = '--manifest' if mode == 'lineage' else '--receipt'
    args = [str(PYTHON), str(CLI), mode, flag, str(path), *map(str, extra)]
    result = subprocess.run(args, cwd=ROOT, text=True, capture_output=True)
    results.append(dict(case=name, expected_exit=expected, actual_exit=result.returncode,
                        argv=args, stdout=result.stdout, stderr=result.stderr))

original = json.loads(R0.read_text())
run('accepted_task', 'task', R0, expected=0)
run('accepted_subphase', 'subphase', RS, expected=0)

doc = copy.deepcopy(original)
doc['artifact_manifest'] = []
run('required_artifacts_omitted', 'task', write('empty-artifacts.json', doc))

doc = copy.deepcopy(original)
doc['plan_sha256'] = '0' * 64
doc['code_sha256'] = '0' * 64
doc['run_id'] = '0' * 16
run('plan_code_and_run_identity_replaced', 'task', write('wrong-identities.json', doc))

doc = copy.deepcopy(original)
doc['command_results'][0]['exit_code'] = 1
doc['unresolved'] = ['pytest failed with exit 1; it has not been fixed']
run('failed_test_excused_as_implemented', 'task', write('failed-command.json', doc))

doc = copy.deepcopy(original)
doc['acceptance_checks']['A01'] = False
doc['disposition'] = 'blocked_implementation'
bad_parent = write('predecessors/P15-00/attempt-0001/TASK_RECEIPT.json', doc)
run('failed_parent_control', 'task', bad_parent)
doc = json.loads(R1.read_text())
doc['predecessor_receipts']['P15-00'] = sha(bad_parent)
run('child_of_failed_parent', 'task', write('child-of-failed-parent.json', doc),
    '--receipts-root', OUT / 'predecessors')

graph = json.loads((ROOT / 'planning/research-program/TASK_GRAPH.json').read_text())
phase = {'schema_version': 'research-phase-receipt-v1', 'phase': 'phase-2',
         'gate': 'pass', 'phase_1_5_gate': 'pass',
         'task_receipts': {t['id']: {'path': str(R0), 'sha256': sha(R0),
                                    'disposition': 'implemented_verified'}
                           for t in graph['tasks'] if t['phase'] == 'phase-2'}}
run('phase_2_closed_using_one_phase_1_5_receipt', 'phase', write('false-phase-2.json', phase))

doc = json.loads(RS.read_text())
doc['subphase_id'] = '00-foundaton'
doc['task_receipts'] = {}
doc['test_evidence'] = []
run('unknown_subphase_with_no_tasks', 'subphase', write('unknown-subphase.json', doc))

lineage = {'schema_version':'research-lineage-manifest-v1', 'records':[
    {'issue_at_ns':10, 'parents':[{'issue_at_ns':100, 'available_at_ns':100}]}]}
run('lineage_child_overrides_ancestor_clock', 'lineage', write('future-lineage.json', lineage))

late = EvidenceRef('a' * 64, ('future-row',), 100, 100, 100, Coverage.COMPLETE, ())
for name, build in [
    ('trade_backdates_late_evidence', lambda: NativeTrade('t', 'NQ:test', 10, 10, Decimal('100'), 1, 1, late)),
    ('reference_backdates_late_evidence', lambda: Reference('r', 'l', 'f', 'NQ:test', Decimal('99'), Decimal('101'), 10, 200, (1,), (late,))),
    ('forecast_training_ends_after_issue', lambda: Forecast('f', 'e', 'a' * 64, 's', 10, 'h', 20, {'variance':1.0}, 'supported', 100, 5, (), ())),
]:
    try:
        obj = build()
        results.append(dict(case=name, expected='ContractError', actual='accepted', record=repr(obj)))
    except Exception as exc:
        results.append(dict(case=name, expected='ContractError', actual=type(exc).__name__, error=str(exc)))

write('RESULTS.json', results)
print(json.dumps(results, indent=2))
