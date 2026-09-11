"""Replay current producers into audit-only files; never modify retained tables."""
from __future__ import annotations

import importlib
import json
from concurrent.futures import ThreadPoolExecutor

from chart_audit_plots import OUT, TABLES, tape, serial
from trading_research.research.phase1_live.compute import load_rows
from trading_research.research.phase1_live.family_tape import _score_one
from trading_research.research.phase1_live.threshold_grid import GRID_PATH


def compare(fresh, retained):
    prior={r['date']:r for r in retained}
    missing={"MISSING_KEY":True};diffs=[]
    for r in fresh:
        old=prior.get(r['date'],{})
        fields={k:{"fresh":r.get(k,missing),"retained":old.get(k,missing)}
                for k in sorted(set(r)|set(old)) if r.get(k,missing)!=old.get(k,missing)}
        if fields:diffs.append({"date":r['date'],"fields":fields})
    return diffs


def main():
    cases=json.loads((OUT/'chart_cases.json').read_text())
    dates=sorted({r['date'] for r in cases})
    grid=json.loads(GRID_PATH.read_text())
    fresh=[]
    for iso in dates:
        ev=tape(iso)
        if ev is not None:
            r=_score_one(iso,ev,TABLES['sessions_F'],TABLES['open_switch_F'],grid,TABLES['weekly_delta_F'])
            if r:fresh.append(r)
        print('tape replay',iso,flush=True)
    (OUT/'fresh_tape_selected.json').write_text(json.dumps(fresh,indent=2,default=serial)+'\n')
    diffs={"tape_flags_F":compare(fresh,load_rows('tape_flags_F'))}
    for module,table,fn in [('family_recipes','recipe_flags_F','build_recipe_table'),('family_levels','level_grid_F','build_level_table'),('family_fail','fail_F','build_fail_table')]:
        m=importlib.import_module('trading_research.research.phase1_live.'+module)
        m.load_rows=lambda name, target=table: [] if name==target else load_rows(name)
        def capture(name,rows):
            (OUT/('fresh_'+name+'.json')).write_text(json.dumps(rows,indent=2,default=serial)+'\n')
        m.save_rows=capture
        if module=='family_levels':
            for dep,attr,tab in [('family_open','build_open_table','open_switch_F'),('family_env','build_env_table','env_F')]:
                dm=importlib.import_module('trading_research.research.phase1_live.'+dep)
                setattr(dm,attr,lambda tab=tab:load_rows(tab))
        rows=getattr(m,fn)()
        diffs[table]=compare(rows,load_rows(table))
        print(table,'fresh rows',len(rows),'dates with differences',len(diffs[table]),flush=True)
    (OUT/'producer_replay_disagreements.json').write_text(json.dumps(diffs,indent=2,default=serial)+'\n')


if __name__=='__main__':main()
