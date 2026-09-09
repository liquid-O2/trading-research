"""Question-based readable views of retained, fully enumerated year reports.

This reporter performs no fits, searches or new confidence-interval calculation.
Pooled counts are descriptive. Annual block intervals keep their original scope.
"""
from collections import Counter, defaultdict

from trading_research.errors import IntegrityError
from trading_research.operations.artifacts import artifact_ref

VERSION = 'jumbo-question-report-v3'
CLASSES = ('no_break', 'high_only', 'low_only', 'high_then_low', 'low_then_high', 'ambiguous')


def _number(value, digits=2):
    return 'unavailable' if value is None else f'{value:.{digits}f}'


def _percent(numerator, denominator):
    return 'unavailable' if not denominator else f'{100*numerator/denominator:.1f}%'


def _interval(metric):
    if not metric:
        return 'unavailable'
    b = metric['bootstrap']
    f = lambda x: 'unavailable' if x is None else f'{100*x:.1f}%'
    return f"{f(metric['estimate'])} [{f(b['lower'])}, {f(b['upper'])}]"


def _annual_quantiles(records, field, level):
    values = [r.get('distributions', {}).get(field, {}).get('quantiles', {}).get(str(level))
              for _, r in records]
    values = [v for v in values if v is not None]
    return 'unavailable' if not values else f'{_number(min(values))}–{_number(max(values))}'


def _observed_rate(records, field):
    metrics = [r['metrics'][field] for _, r in records if field in r['metrics']]
    n = sum(m.get('actual_valid_date_count', 0) for m in metrics)
    events = sum(m.get('positive_events', 0) for m in metrics)
    return f'{_percent(events,n)} ({events}/{n})'


def descriptive_report(shards, store, *, protocol, analysis_plan, stage, supplements=()):
    if stage not in ('development', 'confirmation'):
        raise IntegrityError('explicit research report period required')
    years, paths, formations, specials = [], defaultdict(list), defaultdict(list), defaultdict(list)
    for shard in sorted(shards, key=lambda s: (s['root'], s['year'])):
        from trading_research.research.jumbo_study import _read_statistics
        stats = _read_statistics(store, shard['statistics'])
        if stats['kind'] != 'jumbo_observed_year_statistics_v1':
            raise IntegrityError('question report requires the declared year statistics')
        years.append((shard['root'], shard['year'], shard['intended_cash_dates']))
        for value in stats['formations']:
            formations[(shard['root'], value['clock'])].append((shard['year'], value))
        for value in stats['paths']:
            compact = {k: value[k] for k in ('clock','horizon','complete_target_dates','intended_dates','path_counts')}
            compact['metrics'] = {k: v for k, v in value['metrics'].items()
                                  if k in ('both_breach','both_full_population_rate_lower','both_full_population_rate_upper')
                                  or k.startswith('first_breach_by_')}
            compact['distributions'] = {k: v for k, v in value.get('distributions', {}).items()
                                        if k in ('maximum_up_W','maximum_down_W','terminal_W',
                                                 'first_lower_minutes','first_upper_minutes')}
            paths[(shard['root'], value['clock'], value['horizon'])].append((shard['year'], compact))
        for value in stats['special_mechanisms']:
            specials[(shard['root'], value['clock'])].append((shard['year'], value))
    lines = [f'# Jumbo range, path and timing study: {stage}', '',
      'This report answers descriptive questions across every declared formation clock and source-specific mechanism. '
      'The complete year tables preserve each candidate, failed formation, unresolved outcome and exact source identity. '
      'The separate model and Location reports assess predictive and candidate quality; a frequency difference alone does not choose a clock.', '',
      '## What population and clocks were measured?', '',
      '| Instrument | Year | Intended actual cash dates |', '|---|---:|---:|']
    lines += [f'| {r} | {y} | {n} |' for r,y,n in years]
    lines += ['', 'The acquired NQ/ES contract sequence is used with raw contract boundaries. Individual admitted minutes do not certify a whole window. '
      'The declared scenario publishes each minute bar one minute after its end; this is a latency assumption, not measured historical receipt. '
      'A 06:00–09:00 New York formation therefore ordinarily permits a 09:01 causal forecast and a 12:01 end for the following 180 minutes. '
      'Literal source forecasts and availability-delayed special-mechanism forecasts are separately identified.', '',
      'OR15 is the disclosed 09:30–09:45 source benchmark. Its prior-volume activity variants and old generic opening-reference features '
      'are explicitly legacy benchmark constructions. It has no privileged interpretation as the user framework. '
      'Exact anchor supplements identify OR5, OR15, the 06:00–09:00 JTR range, the futures 08:00 range and New York 08:00 range separately.', '',
      '## How often are ranges available, and how wide are they?', '',
      'Every declared clock appears below. Widths are integer quarter-point ticks. The median column is the range of separately computed annual medians, '
      'not a pooled median. Missing dates and zero-width formations are retained. Exclusion counts can overlap when a date has several reasons.', '',
      '| Instrument / clock | Available / intended | Zero width | Annual median width, min–max | Exclusion reasons |',
      '|---|---:|---:|---|---|']
    for (instrument,clock), records in sorted(formations.items()):
        reasons = Counter()
        medians = []
        for _,r in records:
            reasons.update(r['exclusion_reason_counts'])
            q = r['distributions']['width_ticks']['quantiles']
            # Stringified level keys are frozen by the statistics publisher.
            v = q.get('0.5')
            if v is not None:
                medians.append(v)
        med = 'unavailable' if not medians else f'{_number(min(medians))}–{_number(max(medians))}'
        rs = '; '.join(f'{k}: {v}' for k,v in sorted(reasons.items())) or 'none'
        lines.append(f"| {instrument} / {clock} | {sum(r['available_dates'] for _,r in records)} / {sum(r['intended_dates'] for _,r in records)} | {sum(r['zero_width_dates'] for _,r in records)} | {med} | {rs} |")
    lines += ['', '## Which boundary paths occur after formation?', '',
      'The following 180-minute table pools actual class counts across the displayed years for each instrument and clock. '
      'Its denominator is complete observed positive-width targets. Ordered high-then-low and low-then-high paths are displayed separately. '
      'Ambiguous first-side order remains a distinct observed OHLC class. These descriptive rates have different widths and forecast origins.', '',
      '| Instrument / clock | Complete / intended | No break | High only | Low only | High then low | Low then high | Both edges | Ambiguous order |',
      '|---|---:|---:|---:|---:|---:|---:|---:|---:|']
    for (instrument,clock,horizon), records in sorted(paths.items()):
        if horizon != 'after_180m':
            continue
        counts = Counter()
        for _,r in records:
            counts.update(r['path_counts'])
        n = sum(r['complete_target_dates'] for _,r in records)
        intended = sum(r['intended_dates'] for _,r in records)
        # Ambiguous is a both-edge observation whose intraminute first side is
        # unresolved. Full binary both counts are retained independently.
        both = sum(r['metrics']['both_breach'].get('positive_events',0) for _,r in records)
        lines.append(f"| {instrument} / {clock} | {n} / {intended} | {_percent(counts['no_break'],n)} | {_percent(counts['high_only'],n)} | {_percent(counts['low_only'],n)} | {_percent(counts['high_then_low'],n)} | {_percent(counts['low_then_high'],n)} | {_percent(both,n)} | {_percent(counts['ambiguous'],n)} |")
    lines += ['', '## Are event rates stable across years, and how much can censoring change them?', '',
      'Each annual both-edge estimate below includes its original 95% interval from 1,000 nonwrapping five-date block resamples, seed 20260907. '
      'The separate identified population bounds include every available positive-width formation: a breach observed before censoring stays positive, '
      'while an unresolved outcome can be either zero or one. The bounds are not confidence intervals. '
      'Sparse dates/events remain flagged in the full report; these intervals are descriptive and do not correct a search across all clocks.', '',
      '| Instrument / clock | Year | Complete / intended | Both-edge rate [95% interval] | Formed-population lower–upper |',
      '|---|---:|---:|---|---|']
    for (instrument,clock,horizon), records in sorted(paths.items()):
        if horizon != 'after_180m':
            continue
        for year,r in records:
            lower = r['metrics']['both_full_population_rate_lower']['estimate']
            upper = r['metrics']['both_full_population_rate_upper']['estimate']
            bounds = f"{_percent(lower,1) if lower is not None else 'unavailable'}–{_percent(upper,1) if upper is not None else 'unavailable'}"
            lines.append(f"| {instrument} / {clock} | {year} | {r['complete_target_dates']} / {r['intended_dates']} | {_interval(r['metrics']['both_breach'])} | {bounds} |")
    lines += ['', '## Does waiting reveal more information or merely change the target?', '',
      'The retained tables separately cover 15/30/60/180-minute horizons, actual cash-close endpoints, prefix updates and the common 10:01 prediction cut. '
      'First-breach curves at 1/5/15/30/60/180 minutes use observed prefixes and preserve no-event and censored dates. '
      'A later formation supplies later information and usually a shorter remaining fixed-end horizon. '
      'Timing superiority requires the independently scored common-cut, common-endpoint targets with prior-scale and available-geometry controls. '
      'The adjacent clock and OR15-volume activity constructions are named experiments, not selected defaults. '
      'Auction-completed windows require their separately admitted auction observations; minute volume is not an auction-state substitute.', '',
      'Every retained clock/horizon appears below, including prefix and common-cut updates. Each timing cell gives the observed-prefix rate and '
      'its actual event/known-outcome denominator. A requested time beyond the planned horizon has no eligible observations; censored truth is not a non-event. '
      'First-event medians are conditional on an observed event and display the range of annual medians of its lower/upper observation-time bounds. '
      'Pooling observed-prefix counts is descriptive and does not estimate a censoring-adjusted survival distribution.', '',
      '| Instrument / clock | Horizon | Complete / intended | First by 15m (events/known) | First by 60m (events/known) | First by 180m (events/known) | Annual median first-event lower / upper bounds, minutes |',
      '|---|---|---:|---|---|---|---|']
    for (instrument,clock,horizon), records in sorted(paths.items()):
        n = sum(r['complete_target_dates'] for _,r in records)
        intended = sum(r['intended_dates'] for _,r in records)
        cells = ' | '.join(_observed_rate(records,f'first_breach_by_{minute}m') for minute in (15,60,180))
        bounds = _annual_quantiles(records,'first_lower_minutes',.5)+' / '+_annual_quantiles(records,'first_upper_minutes',.5)
        lines.append(f'| {instrument} / {clock} | {horizon} | {n} / {intended} | {cells} | {bounds} |')
    lines += ['', '## How large are the subsequent excursions and terminal moves?', '',
      'Excursions and terminal displacement are in units of the specific formation width W. Each cell is the minimum–maximum across '
      'separately computed annual quantiles, not a pooled quantile or confidence interval. The terminal columns preserve negative as well as positive moves. '
      'Observed complete-horizon distributions condition on available truth; the preceding population counts expose the excluded and unresolved dates. '
      'Changing W or the forecast origin changes the quantity, so these marginal distributions cannot select the best timing.', '',
      '| Instrument / clock | Horizon | Annual median up / down excursion, W | Annual 95th-percentile up / down excursion, W | Annual terminal 5th / median / 95th percentiles, W |',
      '|---|---|---|---|---|']
    for (instrument,clock,horizon), records in sorted(paths.items()):
        median = ' / '.join(_annual_quantiles(records,f,.5) for f in ('maximum_up_W','maximum_down_W'))
        tail = ' / '.join(_annual_quantiles(records,f,.95) for f in ('maximum_up_W','maximum_down_W'))
        terminal = ' / '.join(_annual_quantiles(records,'terminal_W',q) for q in (.05,.5,.95))
        lines.append(f'| {instrument} / {clock} | {horizon} | {median} | {tail} | {terminal} |')
    lines += ['',
      '## Do the source-specific mechanisms support their stated claims?', '',
      'Generic double-break statistics do not answer these source questions. The table below reports the actual payload state populations for each source clock and branch. '
      'Magic midpoint return versus extension invalidation retains compatible terminal states when OHLC cannot order events. '
      'PIN073 midpoint return is conditional on its own conditioning stage, with neither/high-only/low-only/both strata; an earlier edge touch is not an invented prerequisite. '
      'PIN074/PIN076 open-to-open targets are created only once their observed opens are available. '
      'PIN078 measures separate Monday/Tuesday daily ranges and distinguishes repeated hit shares from unique-day hit rates. '
      'ONS retains the overnight range midpoint; no undisclosed classical-pivot formula is manufactured.', '',
      '| Instrument / source clock | Year | Candidate / intended | Branch | Observed states |',
      '|---|---:|---:|---|---|']
    for (instrument,clock), records in sorted(specials.items()):
        for year,r in records:
            for branch,counts in r['outcomes'].items():
                text = '; '.join(f'{k}: {v}' for k,v in sorted(counts.items())) or '; '.join(f'{k}: {v}' for k,v in sorted(r['status_counts'].items()))
                lines.append(f"| {instrument} / {clock} | {year} | {r['candidate_available_dates']} / {r['intended_dates']} | {branch} | {text} |")
            for metric,value in sorted(r.get('metrics',{}).items()):
                lines.append(f"| {instrument} / {clock} | {year} | {value['actual_valid_date_count']} observed dates | {metric} | {_interval(value)} |")
            if r.get('daily_hit_statistics'):
                daily = r['daily_hit_statistics']
                lines += ['', f'{instrument} {year}: Monday and Tuesday source ranges remain separate daily candidates. '
                          'Repeated compatible bars and unique contact dates answer different questions.', '',
                          '| Source level | Eligible / excluded dates | Unique compatible dates / rate | Unique definite-print dates / rate | Repeated compatible bars |',
                          '|---|---:|---|---|---:|']
                for level, v in sorted(daily['levels'].items()):
                    n = v['eligible_dates']
                    compatible, definite = v['unique_compatible_hit_dates'], v['unique_definite_print_dates']
                    lines.append(f"| {level} | {n} / {v['excluded_dates']} | {compatible} / {_percent(compatible,n)} | {definite} / {_percent(definite,n)} | {v['compatible_bar_hits']} |")
                lines += ['', daily['share_scope'], '',
                          '| Instrument / source clock | Year | Candidate / intended | Branch | Observed states |',
                          '|---|---:|---:|---|---|']
    lines += ['', '## What remains unresolved?', '',
      'OHLC resolves neither arbitrary intraminute event order nor every exact trade contact. Compatible range intersection, a definite observed print, '
      'no contact and incomplete future observation remain distinct. Fixed raw-contract coordinates never span an unhandled roll. '
      'The original NQ2024 definition-conflict exclusions remain auditable; a source-supported supersession supplement, when available, reports its incremental population separately. '
      'Unpublished statistical-zone formulas, source chart-clock assumptions and trade-order or auction dependencies retain their exact unresolved status. '
      'The matched timing, independent Context and full Location results have their own linked outputs and acceptance decisions. '
      'No descriptive table establishes trading profitability.', '', '## Reproducible evidence', '']
    for s in sorted(shards,key=lambda x:(x['root'],x['year'])):
        suffix = '-source-supersession' if 'source_supersession' in s else ''
        lines.append(f"- [{s['root']} {s['year']} tables and complete annual statistics]({s['root']}-{s['year']}{suffix}-shard.json): statistics SHA256 `{s['statistics']['sha256']}`.")
    for item in supplements:
        lines.append(f"- Explicit supplement: `{item}`.")
    lines += ['', f'Reporter: `{VERSION}`. Every published number above is derived from the linked actual annual reports.']
    return '\n'.join(lines)+'\n'
