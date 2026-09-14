"""C7 — census of source stages bound to literal constants in the frozen pack.

Every predicate operand below is written into the episode as a Python literal
(or an expression that restates how the trigger was selected), so the source
condition it names can never be observed false.
"""
import re,sys
from pathlib import Path
ROOT=Path('/workspace/implementation/src/trading_research/research/method_pack')
FILES=['historical_price_scanners.py','historical_auction_scanners.py','historical_flow.py',
       'historical_process_scanners.py']
pat=re.compile(r"'([a-z_0-9]+)'\s*:\s*(True|False)(?!\s+if\b)")
for name in FILES:
    text=(ROOT/name).read_text().splitlines()
    hits=[]
    for i,line in enumerate(text,1):
        if line.lstrip().startswith('#'):continue
        for m in pat.finditer(line):
            if m[1] in {'complete','observed_scope_complete','inferred_zone','external_record','reconstruct',
                        'immutable','release_as_availability','retain_stage_receipts','actual_trade',
                        'faithful_eligible','coverage_complete','depth_complete','book','extra'}:continue
            hits.append(f'{name}:{i}  {m[1]} = {m[2]}')
    print('\n'.join(hits))

print('\n--- source location objects never consumed by any scanner ---')
import subprocess
for rid,what in (('O066','HVN'),('O067','LVN'),('O068','profile shelf'),('O069','profile ledge'),
                 ('O116','refill zone'),('O072','prior reaction area'),('O065','naked POC'),('O087','unfinished business')):
    hits=subprocess.run(['grep','-rl',rid]+[str(ROOT/f) for f in FILES],capture_output=True,text=True).stdout.split()
    print(f'  {rid} ({what}): {"used by "+",".join(Path(h).name for h in hits) if hits else "NOT referenced by any historical scanner"}')
print('\n--- side-independent operands ---')
print('  historical_price_scanners.py:230  bias_recorded = pre is not None and pre["known_at"]<=trigger["start"]'
      '  -- no `side` term, so the long and the short at the same reference get the same value')
