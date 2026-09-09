# F04 complete review and consolidated repair

The parent/child definitions, 58 assigned and lineage findings, and the exact
original passages were reviewed and retained before the frozen protocol and
golden registration. The batch adds a literal availability oracle, bounded durable
partition/domain merge, field/lineage planner and named optional queue policies.
Two Astra agents at the user's requested low effort wrote the merge and scheduler
comparisons independently. A third Astra agent performed the complete static
review of the batch and affected timing, graph, availability and publication
contracts. No tests were run during implementation or review.

All ten findings below were collected before one consolidated implementation
repair. The existing fake worker fixture was initialized with the new runtime
cost state; its existing assertions were retained. Nine additional regression
methods cover the collected findings. Root reviewed the independent test files
and integration record. Verification remains unrun until the final supervised
command records its actual result.

| Finding | Concrete problem | Consolidated correction |
|---|---|---|
| F04-R01 | A malformed budget/callable/key could abandon an older coalesced request before failing admission. | Validate and serialize complete admission arguments before mutation, preserve producer-specific replacement and record policy identity. |
| F04-R02 | A future submitted_at entered the ready queue and could fault the optional supervisor. | Reject future admission before replacing accepted work. |
| F04-R03 | Mutable code/parameter/source identities and observation payloads survived frozen dataclasses and could change hashed lineage. | Strict typed nonempty string identities, immutable payload/input values, exact timestamps and boolean flags across public contracts. |
| F04-R04 | Assignable merge domain/bounds/path/version could drop part of a tie under its original contract hash. | Freeze the complete configuration and nested domain sets. |
| F04-R05 | Persisted and live runtime costs used different clock reads and included post-receipt publication work. | Capture one duration at parent receipt and reuse it for the durable sample and live history. |
| F04-R06 | Eviction allowed a historical cost query to return fallback after the evidence it needed disappeared. | Reject cuts before the retained history became valid. |
| F04-R07 | Ack receipt was discarded, allowing a later cursor change to affect earlier queries and acknowledgements. | Persist actual ack receipt and reject regressing domain queries/acks, including duplicate retry regressions. |
| F04-R08 | Lineage and optional outages failed to invalidate empty-field evidence dependencies. | Traverse all applicable direct dependencies for lineage/outage changes; retain field intersections for numeric changes. |
| F04-R09 | The full oracle could seed stale derived output and resolve a lagged edge using current state. | Require root-only seeds and reject unsupported lagged graphs explicitly. |
| F04-R10 | Truthiness treated a valid horizon endpoint of zero as absent. | Use explicit None checks for every original-horizon deadline. |

The comparisons preserve exact A/B tie scenarios, every seven-cut toy output and
lineage, actual arithmetic operation counts, bounded-buffer/restart behavior and
past-only cost inputs. Timed toy arithmetic supplies real process telemetry;
fixed synthetic durations remain identified as fixture values. These assertions
do not certify live receipt distributions, historical dataset cohorts, whole
source indicator parity, complete consumer integration or trading performance.
The registered suite includes prior independent critical-lane, atomic-publication
and order/dispatch fault assertions. All results and any failure remain recorded.

Executed result: first attempt `bba7931167d5bb20d025eae069d6ae4266bdb1943daf3ca9b489a2756ff92263` passed all 321 methods with zero failures/errors/skips. CPU 30.396436 s, wall 60.513123 s, peak RSS 158,339,072 bytes. The frozen protocol/golden bytes and final code identity matched throughout. See `reports/f04-replay-verification-bba7931167d5.json`. This appended status is after the immutable pre-execution review artifact retained in the run.
