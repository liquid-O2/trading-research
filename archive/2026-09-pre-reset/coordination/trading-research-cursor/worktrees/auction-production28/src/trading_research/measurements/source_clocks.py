"""Named source clock variants compiled by the existing F03 clock producer."""

from dataclasses import dataclass, field
from datetime import date, timedelta
from types import MappingProxyType

from trading_research.errors import ContractError, DependencyUnavailable
from trading_research.context.range_adapter import select_clock, primitive_from_shared_bar, _require_clock
from trading_research.context.ranges import range_definition, range_version
from trading_research.foundations.cash_calendar import zone_version
from trading_research.foundations.intervals import WallRule, IntervalGraph, NamedInterval, Span
from trading_research.operations.artifacts import digest


@dataclass(frozen=True)
class SourceClock:
    id: str
    source_ids: tuple
    start_wall: str
    end_wall: str
    zone_policy: str
    formation_policy: str
    source_boundary: str = 'last_inside_close'

    @property
    def version(self):
        return digest(self)


_ROWS = (
    SourceClock('ny_ib_60',('PIN026','PIN027','PIN030','PIN048'),'09:30','10:30','America/New_York','daily_ib'),
    SourceClock('ny_orb_5',('PIN027','PIN048'),'09:30','09:35','America/New_York','daily_orb'),
    SourceClock('ny_orb_15',('PIN026','PIN027','PIN048'),'09:30','09:45','America/New_York','daily_orb'),
    SourceClock('exchange_ib_60',('PIN028','PIN029','PIN043'),'08:30','09:30','explicit_exchange_zone','daily_ib'),
    SourceClock('weekly_source_daily_reset',('PIN078',),'22:00','21:00','UTC','each_monday_tuesday_session'),
    SourceClock('weekly_combined_two_trading_days',('PIN078',),'22:00','21:00','UTC','first_two_eligible_trading_days'),
    SourceClock('source_high_anchor_06_09',('PIN069',),'06:00','09:00','Etc/GMT+4','new_high_reset_exchange_weekday'),
    SourceClock('ny_rth_vwap',('PIN069',),'09:30','16:00','America/New_York','rth_vwap'),
    SourceClock('source_rth_open5',('PIN059',),'09:30','09:35','America/New_York','opening_five_minutes'),
    SourceClock('source_futures_open5',('PIN059',),'08:00','08:05','America/New_York','opening_five_minutes'),
    SourceClock('source_london_open5',('PIN059',),'02:00','02:05','America/New_York','opening_five_minutes'),
    SourceClock('source_asia_open5',('PIN059',),'19:00','19:05','America/New_York','opening_five_minutes'),
    SourceClock('source_midnight_open5',('PIN059',),'00:00','00:05','America/New_York','opening_five_minutes'),
    SourceClock('source_metals_open5',('PIN059',),'08:20','08:25','America/New_York','opening_five_minutes'),
)
SOURCE_CLOCKS = MappingProxyType({r.id:r for r in _ROWS})
SOURCE_BOUNDARY_DIAGNOSTICS = MappingProxyType({
    'PIN027':'outside_bar_close_is_delayed_diagnostic_not_range_close',
    'PIN043':'outside_bar_close_is_delayed_diagnostic_not_range_close',
    'PIN058':'requires_explicit_platform_240_minute_alignment_and_first_selected_15_minute_bar',
    'PIN059_custom':'requires_explicit_user_wall_clock_definition',
    'PIN066':'profile_anchor_and_grid_are_explicit_inputs_not_a_universal_session',
    'PIN077':'profile_anchor_and_grid_are_explicit_inputs_not_a_universal_session',
})


def source_clock_selection(variant_id, *, calendar, instrument, instrument_root, trading_date,
                           cut, exchange_zone=None, civil_start_day=None):
    variant=SOURCE_CLOCKS.get(variant_id)
    if variant is None or type(trading_date) is not date:
        raise ContractError('declared named source clock and explicit trading date required')
    if variant.formation_policy == 'first_two_eligible_trading_days':
        return weekly_balance_clocks(calendar=calendar,instrument=instrument,instrument_root=instrument_root,
                                     trading_date=trading_date,cut=cut)
    if variant.formation_policy == 'each_monday_tuesday_session' and trading_date.weekday() not in (0,1):
        raise DependencyUnavailable('source weekly geometry forms only on declared Monday/Tuesday sessions')
    return _daily_selection(variant,calendar=calendar,instrument=instrument,instrument_root=instrument_root,
        trading_date=trading_date,cut=cut,exchange_zone=exchange_zone,civil_start_day=civil_start_day)


def _daily_selection(variant, *, calendar, instrument, instrument_root, trading_date, cut,
                     exchange_zone=None, civil_start_day=None):
    session=calendar.resolve(trading_date,instrument_root,cut=cut)
    zone=exchange_zone if variant.zone_policy == 'explicit_exchange_zone' else variant.zone_policy
    if not zone:
        raise DependencyUnavailable('source exchange-clock variant needs the exact instrument venue timezone')
    start_day=trading_date if civil_start_day is None else civil_start_day
    end_day=start_day+timedelta(days=int(variant.end_wall <= variant.start_wall))
    known=session.known_at
    rule=WallRule(variant.id,'measurement-source-clock',trading_date,start_day,end_day,
        variant.start_wall,variant.end_wall,zone,variant.id,zone_version(zone),known,variant.version)
    node=rule.compile()
    if variant.formation_policy in ('daily_ib','daily_orb','rth_vwap'):
        start,end=node.spans[0].start,min(node.spans[0].end,session.close_at)
        if end <= start:
            raise DependencyUnavailable('session has no exposure in the declared source formation')
        node=NamedInterval(node.name,node.owner,(Span(start,end),),node.known_at,node.source_version,
                           node.clock_variant,node.timezone_version,node.trading_dates)
    graph=IntervalGraph('measurement-source-clock',(node,))
    return select_clock(calendar=calendar,interval_graph=graph,interval_name=node.name,
        trading_date=trading_date,instrument_root=instrument_root,instrument=instrument,cut=cut)


def weekly_balance_clocks(*, calendar, instrument, instrument_root, trading_date, cut):
    if type(trading_date) is not date:
        raise ContractError('weekly balance requires an explicit trading date')
    monday=trading_date-timedelta(days=trading_date.weekday())
    selections=[]
    variant=SOURCE_CLOCKS['weekly_combined_two_trading_days']
    for offset in range(7):
        day=monday+timedelta(days=offset)
        session=calendar.resolve(day,instrument_root,cut=cut)
        if session.eligible:
            selections.append(_daily_selection(variant,calendar=calendar,instrument=instrument,
                instrument_root=instrument_root,trading_date=day,cut=cut))
            if len(selections)==2:
                return tuple(selections)
    raise DependencyUnavailable('weekly balance lacks two explicitly eligible trading dates')


@dataclass(frozen=True)
class CombinedWeeklyBalance:
    instrument: object
    trading_dates: tuple
    formation_intervals: tuple
    source_versions: tuple
    geometry: object
    known_at: int
    definition_version: str
    _recipe: object = field(default=None,init=False,compare=False,repr=False)

    @property
    def version_id(self):
        return digest({k:getattr(self,k) for k in self.__dataclass_fields__ if k!='_recipe'})


def combined_weekly_balance(primitives, *, calendar, instrument, instrument_root, trading_date, cut):
    from trading_research.context.ranges import RangeArithmetic
    from trading_research.context.range_adapter import primitive_registry_links
    from trading_research.measurements.common import bounded_rows
    from trading_research.foundations.time import timestamp
    timestamp(cut)
    bounded_rows(primitives,2,name='weekly daily formations')
    if len(primitives)!=2:
        raise DependencyUnavailable('combined weekly balance needs both actual daily formations')
    selections=weekly_balance_clocks(calendar=calendar,instrument=instrument,instrument_root=instrument_root,
        trading_date=trading_date,cut=cut)
    for primitive,selection in zip(primitives,selections):
        primitive_registry_links(primitive)
        if (primitive.selection.clock_id!=selection.clock_id or primitive.instrument!=instrument
                or primitive.published_at>cut or primitive.selection.selected_at>cut
                or not primitive.supports('open','high','low','close') or primitive.status!='final'):
            raise DependencyUnavailable('combined weekly source is incomplete, future or uses another daily clock')
    a,b=primitives
    result=CombinedWeeklyBalance(instrument,tuple(s.window.trading_date for s in selections),
        tuple((s.formation_start,s.formation_end) for s in selections),tuple(p.version_id for p in primitives),
        RangeArithmetic(min(a.low_ticks,b.low_ticks),max(a.high_ticks,b.high_ticks),a.open_ticks,b.close_ticks),
        max(p.published_at for p in primitives),SOURCE_CLOCKS['weekly_combined_two_trading_days'].version)
    object.__setattr__(result,'_recipe',dict(primitives=tuple(primitives),calendar=calendar,instrument=instrument,
        instrument_root=instrument_root,trading_date=trading_date,cut=cut))
    return result


def validate_combined_weekly_balance(value):
    if type(value) is not CombinedWeeklyBalance or type(value._recipe) is not dict or combined_weekly_balance(**value._recipe)!=value:
        raise ContractError('weekly balance differs from its actual two-calendar-day source recipe')


def initial_balance_from_shared_bar(*, selection, engine, publication_version_id, cut):
    """Use the existing C01 range version; no duplicate IB state or object registry."""
    _require_clock(selection)
    variant=SOURCE_CLOCKS.get(selection.window.clock_variant)
    if variant is None or variant.formation_policy not in (
            'daily_ib','daily_orb','opening_five_minutes','each_monday_tuesday_session'):
        raise ContractError('IB adapter needs an actual registered source formation clock')
    primitive=primitive_from_shared_bar(selection=selection,engine=engine,
        publication_version_id=publication_version_id,cut=cut)
    definition=range_definition(selection,id='measurement-ib:'+variant.id,
        version=variant.version,source_ids=variant.source_ids)
    return range_version(primitive,definition)


SCHEDULED_OPENS = MappingProxyType({
    'PIN012':('00:00','09:53','10:34','11:10','11:21','12:35','13:30','12:02','18:07','19:37','21:44','00:08','03:12','04:10','05:29','06:58'),
    'PIN025':('00:00','02:00','04:00','04:30','07:00','08:00','09:00','09:30','10:00','14:00','16:00'),
    'PIN074':('00:00','01:00','03:00','04:00','07:00'),
})


def scheduled_reference_windows(source, *, day, zone, known_at, candle_minutes=1, variant='corrected'):
    from datetime import datetime, time
    if source not in SCHEDULED_OPENS or type(day) is not date or type(candle_minutes) is not int or not 1 <= candle_minutes <= 1440:
        raise ContractError('bounded explicit opening-candle clock required')
    if variant not in ('source','corrected'):
        raise ContractError('source and corrected clock representations must be separately named')
    if source == 'PIN025' and variant == 'source':
        raise DependencyUnavailable('manual source clock requires its original exchange/chart calendar reconstruction')
    if source in ('PIN025','PIN074') and variant == 'corrected' and zone != 'America/New_York':
        raise ContractError('corrected source definition explicitly uses the New York civil calendar')
    result=[]
    for i,wall in enumerate(SCHEDULED_OPENS[source]):
        start=datetime.combine(day,time.fromisoformat(wall))
        end=start+timedelta(minutes=candle_minutes)
        if source == 'PIN074' and variant == 'source' and i == 4:
            end=datetime.combine(day+timedelta(days=1),time(5,1))
        rule=WallRule(source+':'+str(i)+':'+variant,'M12',day,day,end.date(),wall,end.time().isoformat(),zone,
            source+':'+variant,zone_version(zone),known_at,digest((source,variant,wall,candle_minutes)))
        result.append(rule.compile())
    return tuple(result)
