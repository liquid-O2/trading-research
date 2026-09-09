# F03 interval graph and durable timer reference batch, version 1

Frozen before implementation or test execution on 2026-09-06. Owners: F03,
F03.SESSION_CASES and B00.1. This batch is deterministic engineering;
it does not admit a market cohort, prove a source statistic, or select a trade.

Inputs are immutable versioned calendar rows, declared trading dates, explicit
wall clocks and DST folds, named finite half-open intervals, and independently
owned boundary actions. UTC offsets, New York wall time and exchange-local
time remain different declared variants. Missing source implementations,
unclear formation starts and unpublished venue deadlines stay dependencies.

The reference interface compiles explicit wall rules, interval unions and
named intersections. A graph freezes source versions and knowledge times;
queries before its knowledge cut fail. Empty intersections and holiday rows
remain explicit. Weekly/monthly periods are formed from declared calendar
dates and actual supplied intervals, never fixed bar counts or UTC midnight.
String/wall-rule membership and a direct pairwise intersection reference are
compared with compiled queries on fixed cases, including all endpoints.

Boundary events have stable logical IDs containing scope, owner and action
key. Their immutable version IDs include their effective and knowledge times
and dependencies. Completion/publication/reset/start order is deterministic.
An independently advanced clock makes events due without a market tick.
First installation catches up missed events at installation time. A newer
calendar supersedes unfired changed timers; already applied actions cannot
be repeated under a new version. Changes to past boundaries cause explicit
reconciliation at the new knowledge/installation cut, without backdating a
reset. Every changed graph emits a revision notice. Old graph queries and
event history remain unchanged.

A SQLite journal atomically commits a pure consumer state transition and
its application record. Restart before application retries it; restart after
commit does not repeat it. A reducer exception rolls the transaction back.
This is exactly-once application of internal JSON state only. Arbitrary
external side effects, order sends, acknowledgments, live reactor wiring and
all C/L/R/P consumer integration are separate P5 work.

The fixed expectations in `tests/golden/f03-intervals.json` cover:

- NY summer 09:00 versus 09:30: 30 minutes; fixed EST 09:30 is one hour later.
- Explicit DST gap rejection and two fall folds one hour apart. NY midnight
  to midnight lasts 23/25 hours on the spring/fall transition dates.
- Sunday 20:00 to Monday 00:00 belongs to the declared Monday trading date;
  it includes its start and excludes its end. No 23:59 truncation.
- `[0,10) U [20,30)` intersect `[5,25)` equals `[5,10) U [20,25)`;
  touching intervals have an empty intersection. Gaps stay gaps.
- Synthetic weekly intervals `[10,20), [30,40), [50,55)` total 25 units,
  retaining a half-day and explicit closed date; no fixed weekly duration.
- A synthetic session opens at 10 and closes at 100; firm 90, platform 80
  and margin 5 give a flatten send boundary of 75. A later known platform
  change to 55 gives 50. Future events move only when the revision is known.
- A changed boundary at 40 installed at 60 produces reconciliation at 60.
  A reset already committed once remains committed once through revisions.
- Timer processing at the declared deadline without any market data; duplicate
  installation; restart immediately before/after commit; rollback on failure;
  separate owners; chronological cuts and conflicting same-cut revisions.
- Missing opening prices do not move a scheduled interval or invent a price.
  Source clock gaps, 14–17 three-hour block, 09 versus 09:30, distinct 19/20
  Asia starts and the 23–03 next-day magic-hours deadline remain distinct.
- Calendar/cash-calendar nested immutability, typed clocks, malformed rows,
  invalid margins, unknown source scope and unsupported boundary facts fail.

The source catalogue retains all 74 assigned findings, 47 original static
source files, 41 visually inspected pages from 11 PDFs, the original image,
and the exact conversation passage. Selected original source bytes are hash
verified; source code is never executed. Source parity outside the declared
fixed cases, unresolved imports and private formulas remain open.

Family `F03-interval-timer-reference-v1`: at most three attempts and 600 CPU
seconds total. One combined verification reserves 180 CPU seconds, with hard
CPU 190 seconds, 4 GiB address space and 240 seconds wall time. No tape scans,
model fits or economic runs. Complete the new implementation and affected
caller review, collect all findings, make one consolidated repair, then run
the combined suite. Repeat only for a concrete unresolved failure or a new
implementation change. No whole-unit or P0–P7 completion follows from this
bounded reference batch.
