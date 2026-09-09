# F03 source clocks and reference cases

The assigned original passages were reviewed before this batch: 74 finding
rows, 47 static source files, 41 original PDF pages with both text and visual
inspection, the original multi-panel image, and conversation lines 1155–1199.
Exact source hashes, inspected line/page sets, retained excerpts/renders and
every source-specific finding/fixture are in `reports/f03-source-cases.json`.
No Pine source was executed. Narrative examples and embedded percentage tables
are source claims, not observed predictive performance.

The graph preserves clock alternatives rather than selecting them from results.
New York wall time differs from fixed EST/GMT offsets; exchange-time `time()`
calls do not become NY because a label says so. Sunday belongs to its declared
trading date. The OSF twelve-hour addition is a display day-label adjustment,
not a trading-date rule. Weekly/monthly membership uses supplied dated sessions.
The 14–17 final '4H' block lasts three hours. All twelve irregular time-based
windows retain their gaps. Asia 18/19/20 starts and NY 08/09/09:30 starts remain
separately named choices. The 23-hour magic formation ends at 00 and its analysis
ends at 03, not 04; the source countdown is one hour late.

No print means a missing price observation, not a moved boundary. Completed
H/L/C cannot be published at formation start. A display toggle, `timenow`,
array position, shifted UTC date or elapsed bar count cannot establish a reset.
Midnight double resets and transition-driven commits require one stable owner.
The generic timer journal commits internal state only; order-side uncertainty
and complete reactor/consumer integration remain separate work.

JFN is assistant synthesis. Its global session bans, IB dismissal and private
range formulas are not adopted. JTR's failed 09:40–50 turn is not a fixed
directional clock rule. London formation start remains unresolved. PDF/image
screen clocks and filenames are not observed exchange or strategy receipts.
The supplied cash calendar remains cash context; official futures and account
cutoffs require their own dated sources. Source imports and indicator statistics
are not supplied by this reference implementation.

All cases below are preregistered expectations; none closes the whole source
case or unit. Named test evidence will be attached after the single batch review
and consolidated repair pass.

| Case | Expected behavior | Assigned clauses |
|---|---|---|
| F03-01 | Immutable typed calendar facts and known-time revisions | CEX-26 |
| F03-02 | NY wall versus fixed offsets and explicit DST folds | JSS-04, JTR-03, MAV-11, PIN018-02, PIN021-02, PIN025-01 |
| F03-03 | Declared Sunday/overnight trading date; complete midnight interval | JSS-04, OSF-01, PIN001-01, PIN032-02, PIN066-03, PIN078-01 |
| F03-04 | Named half-open intersections retain overlap and inactive gaps | PIN075-01, PIN057-01, PIN083-01 |
| F03-05 | Weekly/monthly actual date union retains holidays and half-days | CEX-26, VW10-05, PIN045-05, PIN066-03, PIN077-02, PIN078-01 |
| F03-06 | Earliest venue/firm/platform boundary minus explicit margin | CEX-26, JXA-21 |
| F03-07 | Independent timer, no market tick, stable reset owner | JSS-04, PIN007-05, PIN012-04, PIN013-03, PIN024-02, PIN040-02, PIN068-03, PIN081-04 |
| F03-08 | Restart before and after atomic internal state commit | PIN061-01, PIN066-03, PIN068-03, PIN070-01, PIN077-02 |
| F03-09 | Future boundary revision supersedes unfired timer | CEX-26 |
| F03-10 | Past revision reconciles at known cut; never repeats a committed reset | CEX-26, PIN068-03 |
| F03-11 | Missing opening/closing print does not move a clock or supply a price | PIN012-02, PIN025-01, PIN040-02, PIN074-02, PIN076-02, PIN081-04 |
| F03-12 | 09:00 versus 09:30 and completed 5-minute opening range | JTR-03, JXA-05, TP3-01, PIN003-01, PIN057-01, PIN059-01, PIN083-01 |
| F03-13 | Literal exchange clocks remain separate from NY-labelled clocks | PIN006-01, PIN013-03, PIN015-01, PIN015-02, PIN016-04, PIN024-02, PIN028-01, PIN043-01, PIN046-01, PIN047-01, PIN064-01, PIN071-05 |
| F03-14 | Distinct Asia 18/19/20 starts, London and NY formations | PIN039-01, PIN041-01, PIN041-02, PIN049-01, PIN061-01, PIN064-01, PIN080-01, PIN082-01 |
| F03-15 | Three-hour 14–17 block and actual elapsed time, not bar counts | PIN001-01, PIN002-02, PIN032-02, PIN040-02, PIN054-01, PIN055-02, PIN081-04 |
| F03-16 | Separate formation, confirmation, publication and reset | AM1-04, MAT-07, PIN003-01, PIN014-02, PIN041-03, PIN047-02, PIN059-01, PIN065-01, PIN068-01, PIN068-02, PIN070-01 |
| F03-17 | Irregular DTT windows and inner minute markers; missing import stays open | PIN012-02, PIN012-03, PIN012-04 |
| F03-18 | Seven magic-hour one-hour formations with three-hour analysis | PIN081-01, PIN081-04 |
| F03-19 | Price-triggered anchor and bar-index expiry need price/bar dependencies | VW10-05, PIN051-02, PIN069-01 |
| F03-20 | Display clocks and filenames are not historical availability | IMG-01, TBR-07, OBT-03, OSF-01, PIN007-05, PIN021-02, PIN076-02 |
| F03-21 | No direction, global session ban or private formula inferred from narrative | JTR-09, JXA-05, JXA-21, JFN-04, JFN-10, AM1-04, MAT-07, TBR-07, OBT-03 |
| F03-22 | Source UI examples and alternative clock choices remain explicit | JSS-02, JSS-04, MAV-11, PIN055-02, PIN057-01, PIN065-01, PIN069-01, PIN074-02, PIN076-02, PIN083-01 |
| F03-23 | Literal versus compiled queries on frozen clocks and endpoints | JTR-03, TP3-01, PIN001-01, PIN054-01, PIN075-01, PIN081-01 |
| F03-24 | No empirical statistics or all-consumer admission from synthetic clock parity | PIN039-01, PIN041-01, PIN041-02, PIN043-01, PIN046-01, PIN047-02, PIN054-01, PIN080-01, PIN082-01, PIN082-03 |

The bounded batch subsequently passed 24 new and 264 existing methods on its
first registered execution. [Executed case mappings](../reports/f03-interval-case-coverage.json)
identify the partial assertions for each row; empty mappings remain explicit.
The catalogue and original source expectations above were recorded before that
run. No whole source case, definition or phase is marked complete by this result.
