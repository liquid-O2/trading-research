"""Freeze completeness-based dates before candidate labels or economic outcomes."""

from collections import defaultdict
from dataclasses import dataclass
from datetime import date

from trading_research.errors import ContractError,DependencyUnavailable
from trading_research.operations.artifacts import digest


REQUIRED_CHECKS=frozenset(('raw_definition','product_terms','cash_calendar','venue_boundary','prior_session_volume',
                         'complete_outright_universe','mbp_full_schema','book_recovery','formation_window','prior_rth_window','entry_and_label_window'))


@dataclass(frozen=True)
class DayCompleteness:
    day:date
    checks:tuple[tuple[str,str,str],...]
    data_versions:tuple[str,...]
    inspected_fields:tuple[str,...]

    def __post_init__(self):
        if len({name for name,_,_ in self.checks})!=len(self.checks) or any(state not in ('satisfied','missing','invalid','unassessed') or not evidence for _,state,evidence in self.checks):raise ContractError("day completeness requires unique explicit checks with evidence or dependency")
        if not self.data_versions or not self.inspected_fields:raise ContractError("date admission requires exact input versions and inspected field disclosure")
        if any(any(word in field.lower() for word in ('pnl','profit','outcome','label','return','alpha','win_rate')) for field in self.inspected_fields):raise ContractError("outcomes cannot determine the eligible calendar population")


def freeze_cohort(rows:tuple[DayCompleteness,...],*,required_checks: frozenset[str]=REQUIRED_CHECKS,years=(2022,2023,2024,2025),per_end=5,scope='E0_exact'):
    if not isinstance(rows,tuple) or not rows or len({r.day for r in rows})!=len(rows) or type(per_end) is not int or per_end<=0 or not required_checks:raise ContractError("bounded unique completeness population required")
    if scope=='E0_exact' and required_checks!=REQUIRED_CHECKS:raise ContractError("exact E0 cannot silently relax contract, data or venue prerequisites")
    if scope not in ('E0_exact','registered_acquired_cohort_diagnostic'):raise ContractError("unregistered population scope")
    quarters=defaultdict(list);excluded=[]
    for row in sorted(rows,key=lambda r:r.day):
        if row.day.year not in years:raise ContractError("unexpected calendar year in cohort")
        by={n:(state,evidence) for n,state,evidence in row.checks}
        reasons={name:by.get(name,('missing','check absent')) for name in sorted(required_checks) if by.get(name,('missing',''))[0]!='satisfied'}
        if reasons:excluded.append({'day':row.day.isoformat(),'reasons':reasons,'assessment_version':digest(row)})
        else:quarters[(row.day.year,(row.day.month-1)//3+1)].append(row)
    selected=[];shortfalls=[]
    for year in years:
        for quarter in range(1,5):
            eligible=quarters[(year,quarter)]
            selected.extend({r.day:r for r in (*eligible[:per_end],*eligible[-per_end:])}.values())
            if len(eligible)<2*per_end:shortfalls.append({'year':year,'quarter':quarter,'eligible_count':len(eligible),'required_distinct':2*per_end})
    selected=sorted(selected,key=lambda r:r.day)
    result={'schema':'e0-completeness-cohort-v1','scope':scope,'dates':tuple(r.day.isoformat() for r in selected),
            'date_assessments':tuple(digest(r) for r in selected),'population_hash':digest(tuple(sorted(rows,key=lambda r:r.day))),
            'required_checks':tuple(sorted(required_checks)),'exclusions':tuple(excluded),'quarter_shortfalls':tuple(shortfalls),
            'historical_role':'development and retrospective evaluation, already historical material',
            'fold_years':{'fit':2022,'selection':2023,'calibration':2024,'retrospective_evaluation':2025}}
    return {**result,'version':digest(result)}


def require_runnable(manifest:dict):
    if manifest['scope']!='E0_exact' or manifest['quarter_shortfalls'] or not manifest['dates']:raise DependencyUnavailable("exact E0 cohort has unresolved completeness/quarter dependencies; diagnostic cohorts remain separately named")
    return manifest['version']
