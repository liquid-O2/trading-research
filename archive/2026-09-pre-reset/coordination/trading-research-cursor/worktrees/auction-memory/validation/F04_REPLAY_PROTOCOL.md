# F04 bounded availability merge and scheduling protocol

Frozen before implementation and execution. This is reference engineering for
F04, F04.SCHEDULER and B00.1. The original source case catalogue retains all 56
assigned findings plus CEX-04 and CRL-17, including literal defects, corrections
and unavailable observations. It does not close all consumers or P0–P7.

Availability is max(required input availability, confirmation, actual completion).
An observed completion cannot also receive a modeled compute charge. Raw source
order, event time, strategy/provider receipt, publication and assumption identity
remain distinct. A plot's origin, final candle high or file timestamp is not its
first availability. Original horizons never restart after delayed computation.

The finite literal reference groups admitted events by known_at, then serializes
each group by declared partition and within-partition sequence. This is an audit
serialization, not an inferred order between independent streams. A batch with
multiple partitions explicitly reports ambiguity; an order-sensitive consumer
must select a registered scenario or reject it. Both opposite scenario outcomes
are retained in the fixed example. No arbitrary source priority admits conflicting
observations in a backward join.

The partitioned implementation stores immutable envelopes in SQLite with WAL and
FULL synchronous commits, bounded retained record/byte counts and bounded batch
materialization. A watermark W asserts, with an evidence identity, that no more
events with availability < W will arrive in that partition. Only batches strictly
below every required partition watermark are ready. Each named consumer domain
has its own explicit required partition set and durable acknowledgement cursor.
An optional options outage must not stop the trade-only domain. Late data below a
declared watermark is rejected without changing state; a correction uses its new
availability. Duplicate IDs are idempotent only for byte-identical content.

Peek is repeatable before acknowledgement. Ack is durable and rejects skipped,
forged or conflicting batches. On restart an unacknowledged batch is redelivered;
external exactly-once effects are not asserted. Source consumers must commit their
own idempotent state before ack. Full retained history counts toward the storage
bound; the caller must explicitly archive/rotate on backpressure. There is no
silent event loss or unbounded RAM fallback.

Dirty planning compares explicit raw fields and source lineage. An OI-only change
invalidates exposure and its descendants, not trade CVD. Identical values with new
lineage still invalidate the dependent forecast. Missing required ports block only
their mandatory descendants; an optional missing edge dirties its consumer so it
can explicitly omit the input. Lagged edges remain subject to the graph's preceding
state contract. Market/account/timer integrity lanes are listed unconditionally and
are never submitted to optional inference workers. The planner is not a cache of
published versions: any payload reuse must retain actual input clocks and lineage.

Optional queue policies are separately named FIFO, deadline, and deadline_cost.
Deadline_cost ranks declared decision priority, original deadline, then prior
measured median service time. Its bounded cost history uses only samples received
by the scheduling cut, retains censored failures and falls back to a registered
estimate without inventing empirical measurements. Changing/coalescing scheduling
is recorded because it changes the decision population. Queue policy cannot
coalesce across producers or silently remove an older task before validating a
newer one. Actual worker results retain parent receipt, original cut, endpoint,
wall/CPU/RSS, failures and discarded requests. Existing independent critical lane
and atomic publication/dispatch tests remain part of the combined execution.

Fixed expected assertions:

* Known times 10, 10, 20 from partitions A, B, A serialize as A0/B0, then A1;
  first batch is ambiguous. A watermark exactly 10 does not release time 10.
* Changing file insertion order and deleting a future suffix preserves all earlier
  batches/hashes. Restore before ack returns the same ID; restore after ack moves
  forward; duplicate and conflict behavior stays identical.
* A trade domain advances while an options domain stalls. Missing watermarks,
  buffer saturation, oversized ties and a forged ack fail explicitly.
* OI dirty set is exposure then decision; trade dirty set is cvd then decision;
  OI lineage alone gives the same OI set. Optional OI outage leaves trade outputs
  usable. Full recompute and incremental toy state agree for every declared cut;
  operation counts are measured, not inferred from component names.
* Two same-priority/same-deadline jobs with historical costs 9 and 2 select 2 under
  deadline_cost; FIFO preserves admission order. A future cost sample is excluded.
  Fresh real timed toy work supplies distinct timing telemetry and exact percentile
  calculations; no synthetic duration is labeled a measured live latency.
* Future OI/CPI revisions and pivot confirmation do not change earlier cuts;
  completion at 12 of input known at 10 is usable at 12. Delayed completion cannot
  restart a horizon or double-publish. Timer/account events remain operable while
  optional work is blocked or fails.

One complete static review of new code and affected callers precedes one
consolidated repair. Then run the entire engineering suite once, with at most
three attempts in this family and 600 CPU seconds total: 180 soft / 190 hard CPU
seconds, 4 GiB address space and 240 wall seconds per attempt. Preserve failures,
code snapshot, exact assertions, output and resource telemetry. No market reads,
model fitting, prediction/economic trials or parameter search is authorized by
this protocol. Actual live receipt distributions, full native cohort semantics,
source indicator replay and complete C/L/R/P consequences remain separate gates.
