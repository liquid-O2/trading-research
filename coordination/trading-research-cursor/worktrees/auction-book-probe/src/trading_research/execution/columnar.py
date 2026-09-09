"""Memory-backed compact venue view with explicit constant-lag/status scenarios."""

from bisect import bisect_left,bisect_right
from dataclasses import dataclass
import hashlib
import sys
from types import MappingProxyType

from trading_research.errors import ContractError,DependencyUnavailable
from trading_research.execution.venue import VenuePath,VenueQuote,VenueTrade
from trading_research.operations.artifacts import digest
from trading_research.data.compact import arrow_bytes


def buffers(table):
    import pyarrow as pa
    if sys.byteorder!='little':raise DependencyUnavailable("Arrow native-buffer view requires a separately verified endian implementation")
    result={}
    for name in table.schema.names:
        column=table[name]
        if column.null_count or len(column) and column.num_chunks!=1:raise ContractError("compact numeric view requires one immutable nonnullable chunk")
        format={pa.int64():'q',pa.int32():'i',pa.uint8():'B'}.get(column.type)
        if format is None:raise ContractError("unsupported compact numeric buffer type")
        if not len(column):
            result[name]=memoryview(b'').cast(format)
            continue
        chunk=column.chunk(0)
        result[name]=memoryview(chunk.buffers()[1]).cast(format)[chunk.offset:chunk.offset+len(chunk)].toreadonly()
    return MappingProxyType(result)


@dataclass(frozen=True)
class _Events:
    path:object
    kind:str
    def __len__(self):return len(self.path.times if self.kind=='quote' else self.path.trade_times)
    def __iter__(self):return (self[i] for i in range(len(self)))
    def __getitem__(self,index):
        if isinstance(index,slice):return tuple(self[i] for i in range(*index.indices(len(self))))
        if index<0:index+=len(self)
        if not 0<=index<len(self):raise IndexError(index)
        return self.path._quote(index) if self.kind=='quote' else self.path._trade(index)


class ColumnarVenuePath:
    __slots__=('qtable','ttable','q','t','instrument','instrument_id','source_version','feed_delay_ns','market_state',
               'complete_intervals','coverage_version','times','trade_times','quotes','trades','version')

    def __setattr__(self,name,value):
        if hasattr(self,name):raise AttributeError("venue path is immutable; construct a new version")
        object.__setattr__(self,name,value)

    def __init__(self,*,instrument:str,instrument_id:int,quotes,trades,source_version:str,
                 feed_delay_ns:int,latency_scenario:str,market_state:str,market_state_version:str,
                 complete_intervals:tuple[tuple[int,int],...],coverage_version:str,maximum_rows:int=4_000_000):
        import pyarrow as pa
        import pyarrow.compute as pc
        if (not all((instrument,source_version,latency_scenario,market_state_version,coverage_version))
                or type(instrument_id) is not int or instrument_id<=0 or type(maximum_rows) is not int or maximum_rows<=0
                or type(feed_delay_ns) is not int or feed_delay_ns<0 or len(quotes)+len(trades)>maximum_rows):raise ContractError("bounded projection and named latency, status and coverage inputs required")
        if market_state not in ('continuous','auction','halted','closed','unknown'):raise ContractError("explicit observed or separately assumed market state required")
        if (not isinstance(complete_intervals,tuple) or any(not isinstance(span,tuple) or len(span)!=2 for span in complete_intervals)
                or any(a>=b for a,b in complete_intervals) or any(a[1]>b[0] for a,b in zip(complete_intervals,complete_intervals[1:]))):raise ContractError("invalid immutable source observation intervals")
        quote_fields={'t','source_order','instrument_id','bid','ask','bid_size','ask_size','book_valid','snapshot'}
        trade_fields={'t','source_order','instrument_id','price','size','side','price_valid'}
        for table,required in ((quotes,quote_fields),(trades,trade_fields)):
            if not isinstance(table,pa.Table) or not required.issubset(table.schema.names) or table.schema.field('t').type!=pa.int64():
                raise ContractError("complete registered compact columns and nanosecond int64 clocks required")
        # Arrow tables can wrap caller-owned writable memory. Serialize once into
        # owned immutable bytes before validating or exposing the execution view.
        quote_bytes=arrow_bytes(quotes.combine_chunks());trade_bytes=arrow_bytes(trades.combine_chunks())
        with pa.ipc.open_stream(quote_bytes) as reader:quotes=reader.read_all()
        with pa.ipc.open_stream(trade_bytes) as reader:trades=reader.read_all()
        for table in (quotes,trades):
            if pc.any(pc.not_equal(table['instrument_id'],instrument_id)).as_py():raise ContractError("compact path combines raw contracts")
            times=table['t']
            if pc.any(pc.less(times.slice(1),times.slice(0,max(0,len(times)-1)))).as_py() or pc.count_distinct(table['source_order']).as_py()!=len(table):raise ContractError("compact input ordering or raw-row identity invalid")
            if len(table)>1:
                tied=pc.equal(times.slice(1),times.slice(0,len(times)-1))
                reversed_order=pc.less_equal(table['source_order'].slice(1),table['source_order'].slice(0,len(times)-1))
                if pc.any(pc.and_(tied,reversed_order)).as_py():
                    raise ContractError("same-time compact rows must follow their preserved source order")
        self.qtable=quotes;self.ttable=trades;self.q=buffers(quotes);self.t=buffers(trades)
        self.instrument=instrument;self.instrument_id=instrument_id;self.source_version=source_version;self.feed_delay_ns=feed_delay_ns
        self.market_state=market_state;self.complete_intervals=complete_intervals;self.coverage_version=coverage_version
        self.times=self.q['t'];self.trade_times=self.t['t'];self.quotes=_Events(self,'quote');self.trades=_Events(self,'trade')
        self.version=digest({'source':source_version,'instrument':instrument,'instrument_id':instrument_id,'latency_scenario':latency_scenario,
                             'delay':feed_delay_ns,'market_state':market_state,'market_state_version':market_state_version,'coverage':complete_intervals,'coverage_version':coverage_version,
                             'quote_content_sha256':hashlib.sha256(quote_bytes).hexdigest(),'trade_content_sha256':hashlib.sha256(trade_bytes).hexdigest(),
                             'format':'immutable-compact-venue-v2'})

    covered=VenuePath.covered
    marketable=VenuePath.marketable

    def _quote(self,index):
        q=self.q;at=q['t'][index];order=q['source_order'][index]
        return VenueQuote(f'{self.source_version}:quote:{order}',self.instrument,at,at+self.feed_delay_ns,order,
                          q['bid'][index],q['ask'][index],q['bid_size'][index],q['ask_size'][index],bool(q['book_valid'][index]),self.market_state,self.source_version)

    def _trade(self,index):
        t=self.t
        if not t['price_valid'][index]:raise DependencyUnavailable("unpriced trade cannot receive an invented stop trigger price")
        return VenueTrade(f"{self.source_version}:trade:{t['source_order'][index]}",self.instrument,t['t'][index],t['source_order'][index],
                          t['price'][index],t['size'][index],t['side'][index] or None,self.source_version)

    def quote_at(self,at,*,clock,same_time_ordering='ambiguous'):
        if clock not in ('venue','strategy') or same_time_ordering not in ('ambiguous','venue_first','order_first'):raise ContractError("explicit quote clock and same-time scenario required")
        point=at-self.feed_delay_ns if clock=='strategy' else at
        if clock=='venue' and not self.covered(at):return None,'venue observation interval not certified'
        end=bisect_left(self.times,point) if clock=='venue' and same_time_ordering=='order_first' else bisect_right(self.times,point)
        if end==0:return None,'missing standing quote'
        if clock=='venue' and same_time_ordering=='ambiguous' and self.times[end-1]==at:return None,'order arrival versus same-time venue update is ambiguous'
        q=self._quote(end-1)
        if clock=='venue':
            segment_start=None;previous_end=None
            for left,right in self.complete_intervals:
                if previous_end!=left:segment_start=left
                if left<=at<right:break
                previous_end=right
            if segment_start is not None and q.event_at<segment_start:return None,'standing quote predates missing interval'
        return (q,None) if q.executable else (None,'invalid compact execution quote or noncontinuous state')

    def quote_range(self,start,end,*,clock='venue'):
        if clock not in ('venue','strategy'):raise ContractError("unknown quote range clock")
        delay=self.feed_delay_ns if clock=='strategy' else 0
        return (self._quote(i) for i in range(bisect_left(self.times,start-delay),bisect_right(self.times,end-delay)))

    def trade_range(self,start,end):
        return (self._trade(i) for i in range(bisect_left(self.trade_times,start),bisect_right(self.trade_times,end)))
