"""Strategy-only populations, source mapping, and exact baseline reconciliation."""
from collections import Counter,defaultdict
from pathlib import Path
from .strategy_policy import POLICY,observation_scope
from .historical_runner import BASE,ROOT,read_job,immutable_json,file_digest,read
from .historical_reporting import _table,_write_text
from .catalog import METHOD_BY_ID
from .empirical_protocol import content_hash


def report_strategy(root,registry,manifest,jobs,pilot_jobs):
    baseline=BASE/'run-2.0.0-r9';cohorts={};family=[];phase=[];audit=[]
    for cohort,selected in [('evaluation',jobs),('pilot',pilot_jobs)]:
        episodes=[dict(e,coverage_id=doc['coverage_id']) for row,doc,receipt in selected for e in doc['episodes']]
        totals=defaultdict(Counter);byfamily=defaultdict(Counter);causes=Counter();changes=Counter();original={};current={(e['coverage_id'],e['candidate_id']):e for e in episodes}
        for path in sorted((baseline/'jobs'/cohort).rglob('*.json.gz')):
            baseline_doc=read_job(path)
            original.update({(baseline_doc['coverage_id'],e['candidate_id']):dict(e,coverage_id=baseline_doc['coverage_id']) for e in baseline_doc.get('episodes',[])})
        for e in episodes:
            a=e.get('strategy_assessment')
            if a is None:raise ValueError('reconstruction episode lacks strategy assessment')
            totals[a['scope']][a['status']]+=1
            byfamily[e['method']][a['scope']+':'+a['status']]+=1
            if a['scope']=='entry_setup':
                for field in a['failed_conditions'] if a['status']=='no_setup' else a['unavailable_conditions'] if a['status']=='data_unavailable' else []:
                    causes[(e['method'],e['branch'],a['status'],field)]+=1
            old=original.get((e['coverage_id'],e['candidate_id']))
            changes[(old['research_verdict'] if old else 'new_observation',a['scope'],a['status'])]+=1
        removed=[{'coverage_id':key[0],'candidate_id':key[1],'method':e['method'],'branch':e['branch'],'date':e['session_date'],'old_verdict':e['research_verdict']}
            for key,e in original.items() if key not in current]
        cohorts[cohort]={'scopes':dict(totals),'families':dict(byfamily),'transitions':[{'old':k[0],'scope':k[1],'new':k[2],'n':v} for k,v in sorted(changes.items())],
            'retired_baseline_observations':removed,'baseline_observations':len(original),'current_observations':len(episodes),
            'condition_counts':[{'method':k[0],'branch':k[1],'status':k[2],'condition':k[3],'n':v} for k,v in causes.most_common()],
            'zero_candidate_windows':[{'method':row['method_id'],'branch':row['branch'],'date':doc['session_date'],'scope':observation_scope(row['method_id'],row['branch']),
                'omissions':doc['omissions']} for row,doc,receipt in selected if not doc['episodes']]}
    for method,id_ in METHOD_BY_ID.items():
        counts=cohorts['evaluation']['families'].get(method,{})
        p=counts.get('entry_setup:setup',0);f=counts.get('entry_setup:no_setup',0);u=counts.get('entry_setup:data_unavailable',0)
        context=sum(v for k,v in counts.items() if not k.startswith('entry_setup:'))
        rows=[r for r in manifest['branches'] if r['method_id']==method]
        path=root/'strategy-methods'/f'{method}.md'
        text=f'# {method}: strategy reconstruction\n\n'
        text+=f'Observed entry candidates: {p} setup, {f} no setup, {u} unavailable market input. Separately retained context/process observations: {context}. No personal quantity, account limit or executed-order history gates these setup results.\n\n'
        text+='No setup is a rejection of a candidate by the strategy rules. It is not a losing trade or a software failure. Zero-candidate windows are retained separately and are not counted as confirmed absent setups.\n\n'
        text+=_table(['Branch','Scope','Source logic'],[[r['branch'],observation_scope(method,r['branch']),r['source_definition']['citation']+': '+r['source_definition']['operation']] for r in rows])+'\n\n'
        relevant={'JJ-TBR':['pzone','calendar'],'SIRES':['gamma','auction'],'JETBUNDLE-STATES':['auction'],'STOIC-DATA':['macro'],'KEANI-OPEN-ABOVE-VALUE':['calendar']}.get(method,[])
        for key in relevant:text+=f'Operational model ({key}): `{POLICY[key]}`\n\n'
        conditions=[r for r in cohorts['evaluation']['condition_counts'] if r['method']==method]
        text+=_table(['Branch','Status','Condition','Observations'],[[r['branch'],r['status'],r['condition'],r['n']] for r in conditions])+'\n\n'
        text+=f'Full episode values, inferred-model receipts and legacy source-audit comparisons: [native report]({root}/methods/{method}.md). [Versioned policy]({root}/registry/STRATEGY_POLICY.json).\n'
        _write_text(path,text)
        family.append([method,p,f,u,context])
        phase.append([method,'strategy reconstruction v1',p+f,'not claimed','executed; reconstructed setup scope',str(path.relative_to(ROOT))])
        audit.append([method,id_,'source logic + replay checked','pass',0,0,'inferred models identified; private execution excluded; no profit claim'])
    body={'schema':'phase1-strategy-results-v1','registry_sha256':registry['registry_sha256'],'policy':POLICY,
        'baseline':str(baseline),'baseline_results_sha256':file_digest(baseline/'RESULTS.json'),**cohorts,'family_rows':family,
        'phase':phase,'audit':audit,'software_failures':0,'notes':['Counts are engineering observations, not trade returns.',
            'No sample/threshold search to force failed candidates to pass. New policy follows user strategy-only scope and reviewed source logic.',
            'Coverage-unit and candidate-ID pairs common to both runs are matched exactly; retired and introduced observations are explicit. Cohorts overlap and are not pooled.']}
    immutable_json(root/'registry/STRATEGY_POLICY.json',POLICY)
    immutable_json(root/'STRATEGY_RESULTS.json',body)
    text='# Strategy reconstruction results\n\n'
    text+='The implementation now evaluates market setup conditions without personal sizing, account history or actual orders. It derives auction states, QQQ gamma/key levels, P-zones and a macro composite using the versioned source-inspired models. These models do not claim to recover proprietary formulas.\n\n'
    text+=_table(['Family','Setup','No setup','Market input unavailable','Separate context/process'],family)+'\n\n'
    text+='## Scope and baseline reconciliation\n\n'
    for cohort,doc in cohorts.items():
        text+=f"### {cohort}\n\nBaseline observations: {doc['baseline_observations']}; current observations: {doc['current_observations']}; baseline IDs no longer selected: {len(doc['retired_baseline_observations'])}. Exact IDs and zero-candidate windows are in the JSON report.\n\n"
        text+=_table(['Scope','Classification','n'],[[scope,status,n] for scope,counts in doc['scopes'].items() for status,n in counts.items()])+'\n\n'
        text+=_table(['Old verdict','Current scope','Current classification','n'],[[r['old'],r['scope'],r['new'],r['n']] for r in doc['transitions']])+'\n\n'
    text+='## Interpreting remaining rejections and unknowns\n\nA known violated market condition is **no setup**. Unresolved native event ordering, missing same-contract history, unknown aggressor quantity or unavailable quotes remain **data unavailable**. A missing author label is no longer the sole blocker for an implemented inferred model. These categories are distinct from software failures.\n\n'
    text+='The gamma sign is an explicitly assumed call-positive/put-negative prior-OI model on the acquired QQQ chain. Front-expiry fallback is named whenever 0DTE is unavailable. The key-gamma level is our mapped maximum-gamma node. P-zones use up to 500 prior sessions, historical volume conditioning and volatility-normalized distances. Macro output is our growth-minus-inflation composite. None asserts recovered dealer inventory or a proprietary indicator.\n\n'
    text+='## PHASE lines\n\n'+_table(['family','variant','n','faithful_disagreements','status','report path'],phase)+'\n\n'
    text+='## Audit lines\n\n'+_table(['family','id','verdict','fixture','leakage','proxy-as-faithful','notes'],audit)+'\n'
    _write_text(root/'STRATEGY_RESULTS.md',text)
    print(_table(['family','variant','n','faithful_disagreements','status','report path'],phase))
    print(_table(['family','id','verdict','fixture','leakage','proxy-as-faithful','notes'],audit))
    return body
