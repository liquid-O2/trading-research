# Upgrade paths across the complete system

**153 individually authored parent upgrade paths and 191 individually authored child bindings cover every registered F/M/C/O/X/L/G/P/R/V unit.** This is the substantive pass after the [full-system definition refinement](SYSTEM_REFINEMENT.md). It preserves the existing 344 units and 2,752 P0–P7 records, extending their comparisons instead of pretending every improvement needs another standalone model. All empirical comparisons remain unrun.

The path for each component is: **starting idea → existing conversation/plan improvements → remaining weakness → further construction → fair comparison → evidence and decision use**. Starting points are concise conceptual summaries, not verbatim quotes or claims that every source began at the same level. The exact reviewed source clauses and conversation experiment routes below preserve the historical proposals, user corrections, exceptions and uncertainty. A prior assistant proposal remains a hypothesis; listing it does not make it a user requirement or a proven method.

Read this with [implementation constructions](UPGRADE_CONSTRUCTIONS.md), the parent ten-part cards, [individual experiment phases](experiments/README.md) and [quality rules](MODEL_QUALITY_AND_STOPPING_RULES.md). The [complete handoff](IMPLEMENTATION_HANDOFF.md) and [versioned scope](IMPLEMENTATION_SCOPE.md) carry all of it through one continuing B00–B10 implementation workflow.

## Complete family coverage

| Family | Parent upgrade paths | Specific child bindings |
|---|---:|---:|
| [Foundations](#family-f) | 12 | 12 |
| [Measurements](#family-m) | 13 | 19 |
| [Context](#family-c) | 24 | 46 |
| [Options](#family-o) | 23 | 28 |
| [Cross-market information](#family-x) | 10 | 19 |
| [Locations](#family-l) | 19 | 20 |
| [Mixtures and selection](#family-g) | 10 | 11 |
| [Policy, execution and risk](#family-p) | 12 | 13 |
| [Later Response](#family-r) | 22 | 14 |
| [Research and operations](#family-v) | 8 | 9 |

The rows are a worklist, not a completeness proof by counting. Implementers must expand every named source alternative and clause inside each unit, preserve exact target/clock/coverage differences, and attach a comparison or evidence-backed dependency/disposition. Testing one representative child does not satisfy a whole family. Shared kernels can reuse semantic evidence only when definitions are actually identical; every affected child still needs its own integration and target scorecard.

## What qualifies as an upgrade

- Measurement upgrades improve supported information, geometry, stability or interpretability while retaining the literal reference. Learned residual transforms belong to the chronological fit graph.
- Forecast upgrades must beat or complement strong same-target baselines on proper scores, calibration and supported cohorts, then justify their role in complete decisions. Information changes and model-capacity changes are tested separately.
- Location upgrades control count, width, distance, age, formation and confirmation delay before comparing selected value. Wider or more numerous regions cannot alone establish better precision.
- Policy upgrades compare full feasible action trajectories, including waiting, occupancy, fills, costs and cumulative one-mini risk. A locally better hit rate is insufficient.
- Engineering/research-service upgrades can earn acceptance through exactness, valid inference, resource savings, recovery or diagnostics. They do not need a fabricated alpha story.

Complexity is optional. A deterministic representation, corrected definition, robust statistic, fewer duplicated calculations or a simpler policy may be the successful upgrade. The registered challenger can be rejected or inconclusive; no promised improvement factor, profitability, exhaustive global optimum or guarantee of future behavior is asserted.

<a id="family-f"></a>
## Foundations

<a id="up-f01"></a>
### UP-F01 — Immutable ingestion and schema decoding

Parent: [F01](components/FOUNDATIONS.md); [local phases](experiments/F.md#f01); [definition refinement](SYSTEM_REFINEMENT.md#sr-f01). Upgrade role: `engineering`.

**Starting idea.** Load files into a dataframe for each analysis.

**Existing improvement path.** Immutable sources, reference decoders, bounded columnar reads and partition manifests.

**Remaining weakness.** Repeated experiments can still rescan identical raw partitions or materialize unnecessary columns.

**Further upgrade.** Build a content-addressed partition index with field/schema/identity/time bounds and a one-pass shared measurement materializer. Register exact sufficient summaries and correction-aware checkpoints so later trials read the smallest valid view; retain the literal reader as the oracle.

**Fair comparison.** Literal per-trial reads versus projected/chunked/shared views on identical records and downstream outputs; vary chunking and cold/warm cache.

**Evidence.** Bytes read, CPU/RAM/storage, restart work and exact event/measurement parity; an engineering upgrade need not create alpha.

**Additional local cases to implement.** Interrupted materialization; changed enum/schema; same source under two paths; narrow projection accidentally omits a correction field.

**Decision or system use.** Cheaper complete-family research through V08, enabling more useful comparisons within the same budget without duplicating raw data.

**Exact reviewed source clauses.** [CEX-10](SOURCE_FINDINGS_AND_CONFLICTS.md:192), [CEX-22](SOURCE_FINDINGS_AND_CONFLICTS.md:204), [CEX-26](SOURCE_FINDINGS_AND_CONFLICTS.md:208), [INV-01](SOURCE_FINDINGS_AND_CONFLICTS.md:262), [INV-02](SOURCE_FINDINGS_AND_CONFLICTS.md:263), [INV-03](SOURCE_FINDINGS_AND_CONFLICTS.md:264), [INV-04](SOURCE_FINDINGS_AND_CONFLICTS.md:265), [INV-05](SOURCE_FINDINGS_AND_CONFLICTS.md:266), [INV-06](SOURCE_FINDINGS_AND_CONFLICTS.md:267), [INV-07](SOURCE_FINDINGS_AND_CONFLICTS.md:268), [INV-08](SOURCE_FINDINGS_AND_CONFLICTS.md:269), [INV-09](SOURCE_FINDINGS_AND_CONFLICTS.md:270), [INV-10](SOURCE_FINDINGS_AND_CONFLICTS.md:271), [INV-11](SOURCE_FINDINGS_AND_CONFLICTS.md:272), [INV-12](SOURCE_FINDINGS_AND_CONFLICTS.md:273), [DRF-A03](SOURCE_FINDINGS_AND_CONFLICTS.md:444), [PIN053-01](SOURCE_FINDINGS_AND_CONFLICTS.md:827).

**Conversation upgrade lineage.** [CEX-22](SOURCE_FINDINGS_AND_CONFLICTS.md:204), [CEX-26](SOURCE_FINDINGS_AND_CONFLICTS.md:208). Read the full rows and their original conversation references; [the recheck](CONVERSATION_RECHECK.md) preserves the exact unit/exception routes.

<a id="up-f01-decoder"></a>
#### F01.DECODER — Independent decoding reference

[Existing definition, target and P0–P7](experiments/F.md#f01-decoder) remain binding.

**Specific upgrade scope.** Apply content-addressed projection/chunking to each exact schema decoder while preserving the literal independent reader and complete correction fields.

**Local comparison.** Compare identical decoded records and downstream summaries under cold/warm cache, narrow projection and interrupted materialization; measure bytes, RAM and restart work.

**Additional cases.** Schema enum changes; shared bytes at two paths; omitted field needed for correction.

<a id="up-f02"></a>
### UP-F02 — Instrument, option contract and settlement registry

Parent: [F02](components/FOUNDATIONS.md); [local phases](experiments/F.md#f02); [definition refinement](SYSTEM_REFINEMENT.md#sr-f02). Upgrade role: `engineering`.

**Starting idea.** Identify instruments using display symbols and a few multipliers.

**Existing improvement path.** PIT identity, expiry/exercise/settlement and operation-specific registry.

**Remaining weakness.** Repeated handwritten price/payoff/unit conversions can disagree across options, mappings and account code.

**Further upgrade.** Compile validated instrument definitions into reusable payoff, price-domain, tick-rounding, currency and sensitivity-conversion kernels. Attach dimension checks and assumption sets to each conversion path; dispatch to an explicit unsupported path for nonstandard deliverables.

**Fair comparison.** Hand-coded reference fixtures versus compiled kernels and independent inverse/round-trip paths; compare maintenance and lookup cost.

**Evidence.** Zero unexplained payoff/unit differences; unsupported cases detected; lookup latency and definition-change impact radius.

**Additional local cases to implement.** Adjusted deliverable; multiplier change; underlying future differs from option root; reciprocal mapping versus conditional inverse.

**Decision or system use.** Consistent O/P/X calculations with less duplicated special-case code and clearer data eligibility.

**Exact reviewed source clauses.** [CEX-16](SOURCE_FINDINGS_AND_CONFLICTS.md:198), [CEX-23](SOURCE_FINDINGS_AND_CONFLICTS.md:205), [INV-01](SOURCE_FINDINGS_AND_CONFLICTS.md:262), [INV-02](SOURCE_FINDINGS_AND_CONFLICTS.md:263), [INV-03](SOURCE_FINDINGS_AND_CONFLICTS.md:264), [INV-04](SOURCE_FINDINGS_AND_CONFLICTS.md:265), [INV-05](SOURCE_FINDINGS_AND_CONFLICTS.md:266), [INV-06](SOURCE_FINDINGS_AND_CONFLICTS.md:267), [INV-07](SOURCE_FINDINGS_AND_CONFLICTS.md:268), [INV-08](SOURCE_FINDINGS_AND_CONFLICTS.md:269), [INV-09](SOURCE_FINDINGS_AND_CONFLICTS.md:270), [INV-10](SOURCE_FINDINGS_AND_CONFLICTS.md:271), [INV-11](SOURCE_FINDINGS_AND_CONFLICTS.md:272), [INV-12](SOURCE_FINDINGS_AND_CONFLICTS.md:273), [DRF-A06](SOURCE_FINDINGS_AND_CONFLICTS.md:447).

**Conversation upgrade lineage.** [CEX-10](SOURCE_FINDINGS_AND_CONFLICTS.md:192), [CEX-16](SOURCE_FINDINGS_AND_CONFLICTS.md:198), [CEX-23](SOURCE_FINDINGS_AND_CONFLICTS.md:205), [DRF-A02](SOURCE_FINDINGS_AND_CONFLICTS.md:443), [DRF-A06](SOURCE_FINDINGS_AND_CONFLICTS.md:447). Read the full rows and their original conversation references; [the recheck](CONVERSATION_RECHECK.md) preserves the exact unit/exception routes.

<a id="up-f02-payoff"></a>
#### F02.PAYOFF — Contract-style payoff and calendar cases

[Existing definition, target and P0–P7](experiments/F.md#f02-payoff) remain binding.

**Specific upgrade scope.** Compile each supported payoff/style/unit definition into reusable conversion kernels with explicit domain and unsupported cases.

**Local comparison.** Compare hand-calculated payoff/expiry cases, independent kernels and valid round trips; measure definition-change impact.

**Additional cases.** Adjusted deliverable; option underlier future differs from root; calendar versus remaining-time derivative.

<a id="up-f03"></a>
### UP-F03 — Trading calendar, session and boundary engine

Parent: [F03](components/FOUNDATIONS.md); [local phases](experiments/F.md#f03); [definition refinement](SYSTEM_REFINEMENT.md#sr-f03). Upgrade role: `engineering`.

**Starting idea.** Use fixed local-time strings for sessions and resets.

**Existing improvement path.** Versioned exchange/firm calendars, DST and independent boundary timers.

**Remaining weakness.** Many overlapping anchors can independently recompute boundaries or disagree on interval ownership.

**Further upgrade.** Compile calendar versions into a shared interval/event graph for formation, publication, reset, holiday and required cutoff. Derive named-session intersections and timer events once, with stable IDs and reusable queries for all anchors.

**Fair comparison.** String/rule reference versus compiled interval graph across every registered clock, including overlapping/global sessions.

**Evidence.** Boundary agreement, timer latency, query cost and number of contradictory/duplicated resets.

**Additional local cases to implement.** DST fold; cross-midnight anchor; half-day inside a weekly range; updated required cutoff; no market tick at reset.

**Decision or system use.** All C/L/R formation clocks and P boundaries use the same tested calendar events while preserving source-specific definitions.

**Exact reviewed source clauses.** [JSS-02](SOURCE_FINDINGS_AND_CONFLICTS.md:12), [JSS-04](SOURCE_FINDINGS_AND_CONFLICTS.md:14), [JTR-03](SOURCE_FINDINGS_AND_CONFLICTS.md:20), [JTR-09](SOURCE_FINDINGS_AND_CONFLICTS.md:26), [JXA-05](SOURCE_FINDINGS_AND_CONFLICTS.md:104), [JXA-21](SOURCE_FINDINGS_AND_CONFLICTS.md:120), [JFN-04](SOURCE_FINDINGS_AND_CONFLICTS.md:138), [JFN-10](SOURCE_FINDINGS_AND_CONFLICTS.md:144), [CEX-26](SOURCE_FINDINGS_AND_CONFLICTS.md:208), [IMG-01](SOURCE_FINDINGS_AND_CONFLICTS.md:248), [AM1-04](SOURCE_FINDINGS_AND_CONFLICTS.md:284), [TP3-01](SOURCE_FINDINGS_AND_CONFLICTS.md:310), [VW10-05](SOURCE_FINDINGS_AND_CONFLICTS.md:384), [MAV-11](SOURCE_FINDINGS_AND_CONFLICTS.md:515), [MAT-07](SOURCE_FINDINGS_AND_CONFLICTS.md:532), [TBR-07](SOURCE_FINDINGS_AND_CONFLICTS.md:742), [OBT-03](SOURCE_FINDINGS_AND_CONFLICTS.md:752), [OSF-01](SOURCE_FINDINGS_AND_CONFLICTS.md:795), [PIN001-01](SOURCE_FINDINGS_AND_CONFLICTS.md:812), [PIN002-02](SOURCE_FINDINGS_AND_CONFLICTS.md:817), [PIN003-01](SOURCE_FINDINGS_AND_CONFLICTS.md:819), [PIN006-01](SOURCE_FINDINGS_AND_CONFLICTS.md:833), [PIN007-05](SOURCE_FINDINGS_AND_CONFLICTS.md:840), [PIN012-02](SOURCE_FINDINGS_AND_CONFLICTS.md:853), [PIN012-03](SOURCE_FINDINGS_AND_CONFLICTS.md:854), [PIN012-04](SOURCE_FINDINGS_AND_CONFLICTS.md:855), [PIN013-03](SOURCE_FINDINGS_AND_CONFLICTS.md:859), [PIN014-02](SOURCE_FINDINGS_AND_CONFLICTS.md:864), [PIN015-01](SOURCE_FINDINGS_AND_CONFLICTS.md:865), [PIN015-02](SOURCE_FINDINGS_AND_CONFLICTS.md:866), [PIN016-04](SOURCE_FINDINGS_AND_CONFLICTS.md:871), [PIN018-02](SOURCE_FINDINGS_AND_CONFLICTS.md:877), [PIN024-02](SOURCE_FINDINGS_AND_CONFLICTS.md:879), [PIN021-02](SOURCE_FINDINGS_AND_CONFLICTS.md:893), [PIN025-01](SOURCE_FINDINGS_AND_CONFLICTS.md:899), [PIN028-01](SOURCE_FINDINGS_AND_CONFLICTS.md:904), [PIN032-02](SOURCE_FINDINGS_AND_CONFLICTS.md:915), [PIN039-01](SOURCE_FINDINGS_AND_CONFLICTS.md:933), [PIN040-02](SOURCE_FINDINGS_AND_CONFLICTS.md:936), [PIN041-01](SOURCE_FINDINGS_AND_CONFLICTS.md:938), [PIN041-02](SOURCE_FINDINGS_AND_CONFLICTS.md:939), [PIN041-03](SOURCE_FINDINGS_AND_CONFLICTS.md:940), [PIN043-01](SOURCE_FINDINGS_AND_CONFLICTS.md:944), [PIN045-05](SOURCE_FINDINGS_AND_CONFLICTS.md:952), [PIN046-01](SOURCE_FINDINGS_AND_CONFLICTS.md:955), [PIN047-01](SOURCE_FINDINGS_AND_CONFLICTS.md:956), [PIN047-02](SOURCE_FINDINGS_AND_CONFLICTS.md:957), [PIN049-01](SOURCE_FINDINGS_AND_CONFLICTS.md:964), [PIN051-02](SOURCE_FINDINGS_AND_CONFLICTS.md:972), [PIN054-01](SOURCE_FINDINGS_AND_CONFLICTS.md:978), [PIN055-02](SOURCE_FINDINGS_AND_CONFLICTS.md:981), [PIN057-01](SOURCE_FINDINGS_AND_CONFLICTS.md:985), [PIN059-01](SOURCE_FINDINGS_AND_CONFLICTS.md:990), [PIN061-01](SOURCE_FINDINGS_AND_CONFLICTS.md:997), [PIN064-01](SOURCE_FINDINGS_AND_CONFLICTS.md:1009), [PIN065-01](SOURCE_FINDINGS_AND_CONFLICTS.md:1012), [PIN066-03](SOURCE_FINDINGS_AND_CONFLICTS.md:1018), [PIN068-01](SOURCE_FINDINGS_AND_CONFLICTS.md:1024), [PIN068-02](SOURCE_FINDINGS_AND_CONFLICTS.md:1025), [PIN068-03](SOURCE_FINDINGS_AND_CONFLICTS.md:1026), [PIN069-01](SOURCE_FINDINGS_AND_CONFLICTS.md:1028), [PIN070-01](SOURCE_FINDINGS_AND_CONFLICTS.md:1033), [PIN071-05](SOURCE_FINDINGS_AND_CONFLICTS.md:1040), [PIN074-02](SOURCE_FINDINGS_AND_CONFLICTS.md:1052), [PIN075-01](SOURCE_FINDINGS_AND_CONFLICTS.md:1054), [PIN076-02](SOURCE_FINDINGS_AND_CONFLICTS.md:1058), [PIN077-02](SOURCE_FINDINGS_AND_CONFLICTS.md:1061), [PIN078-01](SOURCE_FINDINGS_AND_CONFLICTS.md:1063), [PIN080-01](SOURCE_FINDINGS_AND_CONFLICTS.md:1071), [PIN081-01](SOURCE_FINDINGS_AND_CONFLICTS.md:1075), [PIN081-04](SOURCE_FINDINGS_AND_CONFLICTS.md:1078), [PIN082-01](SOURCE_FINDINGS_AND_CONFLICTS.md:1080), [PIN082-03](SOURCE_FINDINGS_AND_CONFLICTS.md:1082), [PIN083-01](SOURCE_FINDINGS_AND_CONFLICTS.md:1084).

**Conversation upgrade lineage.** [CEX-26](SOURCE_FINDINGS_AND_CONFLICTS.md:208). Read the full rows and their original conversation references; [the recheck](CONVERSATION_RECHECK.md) preserves the exact unit/exception routes.

<a id="up-f03-session_cases"></a>
#### F03.SESSION_CASES — Session and boundary completeness

[Existing definition, target and P0–P7](experiments/F.md#f03-session_cases) remain binding.

**Specific upgrade scope.** Use a shared interval/event graph for every registered source clock, overlap and mandatory cutoff.

**Local comparison.** Compare original calendar rules with compiled intervals and timers across all named sessions, retaining unresolved source alternatives.

**Additional cases.** DST fold; cross-midnight window; no tick at reset; weekly range with half-day.

<a id="up-f04"></a>
### UP-F04 — Availability ledger and causal replay clock

Parent: [F04](components/FOUNDATIONS.md); [local phases](experiments/F.md#f04); [definition refinement](SYSTEM_REFINEMENT.md#sr-f04). Upgrade role: `engineering`.

**Starting idea.** Recompute the whole feature stack at each decision tick.

**Existing improvement path.** Causal multi-rate scheduler, immutable version cuts and late-result expiry.

**Remaining weakness.** Even a correct scheduler can spend most of its budget recomputing unaffected producers or deliver useful forecasts too late.

**Further upgrade.** Use dependency-driven dirty propagation and incremental state: classify changed raw fields, recompute only affected ports, coalesce superseded optional requests and prioritize producers by registered deadline/decision use. Benchmark a cost-aware schedule with measured runtime costs; integrity lanes remain unconditional.

**Fair comparison.** Full recompute reference versus incremental/deadline schedules on identical admitted observations and declared decision clocks.

**Evidence.** Completed useful forecasts by deadline, p95/p99 lag, CPU/RAM and decision parity; report any policy change caused by scheduling.

**Additional local cases to implement.** An OI revision changes exposure but not raw trade CVD; optional source outage; expensive surface fit; late result cannot restart its horizon.

**Decision or system use.** Make broad simultaneous information practical without requiring every specialist on every tick.

**Exact reviewed source clauses.** [DTM-A01](SOURCE_FINDINGS_AND_CONFLICTS.md:59), [CEX-24](SOURCE_FINDINGS_AND_CONFLICTS.md:206), [IMG-01](SOURCE_FINDINGS_AND_CONFLICTS.md:248), [INV-01](SOURCE_FINDINGS_AND_CONFLICTS.md:262), [INV-02](SOURCE_FINDINGS_AND_CONFLICTS.md:263), [INV-03](SOURCE_FINDINGS_AND_CONFLICTS.md:264), [INV-04](SOURCE_FINDINGS_AND_CONFLICTS.md:265), [INV-05](SOURCE_FINDINGS_AND_CONFLICTS.md:266), [INV-06](SOURCE_FINDINGS_AND_CONFLICTS.md:267), [INV-07](SOURCE_FINDINGS_AND_CONFLICTS.md:268), [INV-08](SOURCE_FINDINGS_AND_CONFLICTS.md:269), [INV-09](SOURCE_FINDINGS_AND_CONFLICTS.md:270), [INV-10](SOURCE_FINDINGS_AND_CONFLICTS.md:271), [INV-11](SOURCE_FINDINGS_AND_CONFLICTS.md:272), [INV-12](SOURCE_FINDINGS_AND_CONFLICTS.md:273), [VX4-07](SOURCE_FINDINGS_AND_CONFLICTS.md:330), [VW10-05](SOURCE_FINDINGS_AND_CONFLICTS.md:384), [DEN-04](SOURCE_FINDINGS_AND_CONFLICTS.md:412), [ALM-06](SOURCE_FINDINGS_AND_CONFLICTS.md:569), [OFM-01](SOURCE_FINDINGS_AND_CONFLICTS.md:623), [TBR-07](SOURCE_FINDINGS_AND_CONFLICTS.md:742), [OSF-02](SOURCE_FINDINGS_AND_CONFLICTS.md:796), [OSF-03](SOURCE_FINDINGS_AND_CONFLICTS.md:797), [PIN009-02](SOURCE_FINDINGS_AND_CONFLICTS.md:826), [PIN012-02](SOURCE_FINDINGS_AND_CONFLICTS.md:853), [PIN014-02](SOURCE_FINDINGS_AND_CONFLICTS.md:864), [PIN019-02](SOURCE_FINDINGS_AND_CONFLICTS.md:888), [PIN021-01](SOURCE_FINDINGS_AND_CONFLICTS.md:892), [PIN022-01](SOURCE_FINDINGS_AND_CONFLICTS.md:894), [PIN022-03](SOURCE_FINDINGS_AND_CONFLICTS.md:896), [PIN023-01](SOURCE_FINDINGS_AND_CONFLICTS.md:897), [PIN023-02](SOURCE_FINDINGS_AND_CONFLICTS.md:898), [PIN027-02](SOURCE_FINDINGS_AND_CONFLICTS.md:903), [PIN032-01](SOURCE_FINDINGS_AND_CONFLICTS.md:914), [PIN035-01](SOURCE_FINDINGS_AND_CONFLICTS.md:920), [PIN037-01](SOURCE_FINDINGS_AND_CONFLICTS.md:927), [PIN040-02](SOURCE_FINDINGS_AND_CONFLICTS.md:936), [PIN043-01](SOURCE_FINDINGS_AND_CONFLICTS.md:944), [PIN045-03](SOURCE_FINDINGS_AND_CONFLICTS.md:950), [PIN047-01](SOURCE_FINDINGS_AND_CONFLICTS.md:956), [PIN048-01](SOURCE_FINDINGS_AND_CONFLICTS.md:960), [PIN056-01](SOURCE_FINDINGS_AND_CONFLICTS.md:983), [PIN058-01](SOURCE_FINDINGS_AND_CONFLICTS.md:989), [PIN059-01](SOURCE_FINDINGS_AND_CONFLICTS.md:990), [PIN064-02](SOURCE_FINDINGS_AND_CONFLICTS.md:1010), [PIN066-02](SOURCE_FINDINGS_AND_CONFLICTS.md:1017), [PIN066-03](SOURCE_FINDINGS_AND_CONFLICTS.md:1018), [PIN068-02](SOURCE_FINDINGS_AND_CONFLICTS.md:1025), [PIN071-01](SOURCE_FINDINGS_AND_CONFLICTS.md:1036), [PIN071-02](SOURCE_FINDINGS_AND_CONFLICTS.md:1037), [PIN071-03](SOURCE_FINDINGS_AND_CONFLICTS.md:1038), [PIN071-06](SOURCE_FINDINGS_AND_CONFLICTS.md:1041), [PIN073-02](SOURCE_FINDINGS_AND_CONFLICTS.md:1049), [PIN077-02](SOURCE_FINDINGS_AND_CONFLICTS.md:1061), [PIN080-01](SOURCE_FINDINGS_AND_CONFLICTS.md:1071), [PIN081-03](SOURCE_FINDINGS_AND_CONFLICTS.md:1077).

**Conversation upgrade lineage.** [DTM-A01](SOURCE_FINDINGS_AND_CONFLICTS.md:59), [CEX-04](SOURCE_FINDINGS_AND_CONFLICTS.md:186), [CEX-24](SOURCE_FINDINGS_AND_CONFLICTS.md:206), [CRL-17](SOURCE_FINDINGS_AND_CONFLICTS.md:233). Read the full rows and their original conversation references; [the recheck](CONVERSATION_RECHECK.md) preserves the exact unit/exception routes.

<a id="up-f04-scheduler"></a>
#### F04.SCHEDULER — Multiple update clocks and atomic publication

[Existing definition, target and P0–P7](experiments/F.md#f04-scheduler) remain binding.

**Specific upgrade scope.** Add dirty-port propagation, request coalescing and deadline-based optional computation without changing admitted information or mandatory risk lanes.

**Local comparison.** Compare full recomputation and incremental schedules on identical decision clocks, complete emitted versions and measured action delay.

**Additional cases.** Superseded slow forecast; late result; unchanged upstream value with new lineage; timer/order race.

<a id="up-f05"></a>
### UP-F05 — Event identity, trade conditions and side normalization

Parent: [F05](components/FOUNDATIONS.md); [local phases](experiments/F.md#f05); [definition refinement](SYSTEM_REFINEMENT.md#sr-f05). Upgrade role: `engineering`.

**Starting idea.** Treat each row as a fresh trade or quote and deduplicate by timestamp/price.

**Existing improvement path.** Provider-specific action/side/flags, identity and correction lineage.

**Remaining weakness.** Every downstream measurement may separately implement correction, overlap and retraction logic.

**Further upgrade.** Emit a canonical transaction-delta stream with explicit insert/revise/cancel operations, original-event ownership and affected field deltas. Share correction reducers across volume, premium, profile and flow views; historical decision views remain immutable.

**Fair comparison.** Independent raw replay versus shared delta reducers under insert/cancel/revise/reordered-delivery scenarios.

**Evidence.** Mass/notional/state reconciliation; correction work and code duplication; no unintended cross-source double count.

**Additional local cases to implement.** Two legitimate identical prints; duplicate acquisition; correction changes side and size; correction arrives before original; partially matched standalone/embedded tapes.

**Decision or system use.** Upgrade every event-derived measurement by giving it a consistent, efficient correction algebra.

**Exact reviewed source clauses.** [DTM-A07](SOURCE_FINDINGS_AND_CONFLICTS.md:65), [JCV-A03](SOURCE_FINDINGS_AND_CONFLICTS.md:162), [CEX-24](SOURCE_FINDINGS_AND_CONFLICTS.md:206), [INV-01](SOURCE_FINDINGS_AND_CONFLICTS.md:262), [INV-02](SOURCE_FINDINGS_AND_CONFLICTS.md:263), [INV-03](SOURCE_FINDINGS_AND_CONFLICTS.md:264), [INV-04](SOURCE_FINDINGS_AND_CONFLICTS.md:265), [INV-05](SOURCE_FINDINGS_AND_CONFLICTS.md:266), [INV-06](SOURCE_FINDINGS_AND_CONFLICTS.md:267), [INV-07](SOURCE_FINDINGS_AND_CONFLICTS.md:268), [INV-08](SOURCE_FINDINGS_AND_CONFLICTS.md:269), [INV-09](SOURCE_FINDINGS_AND_CONFLICTS.md:270), [INV-10](SOURCE_FINDINGS_AND_CONFLICTS.md:271), [INV-11](SOURCE_FINDINGS_AND_CONFLICTS.md:272), [INV-12](SOURCE_FINDINGS_AND_CONFLICTS.md:273), [DEN-01](SOURCE_FINDINGS_AND_CONFLICTS.md:409), [DEN-02](SOURCE_FINDINGS_AND_CONFLICTS.md:410), [DEN-03](SOURCE_FINDINGS_AND_CONFLICTS.md:411), [DEN-04](SOURCE_FINDINGS_AND_CONFLICTS.md:412), [DEN-05](SOURCE_FINDINGS_AND_CONFLICTS.md:413), [DRF-A02](SOURCE_FINDINGS_AND_CONFLICTS.md:443).

**Conversation upgrade lineage.** [DTM-A07](SOURCE_FINDINGS_AND_CONFLICTS.md:65), [JCV-A03](SOURCE_FINDINGS_AND_CONFLICTS.md:162), [CEX-24](SOURCE_FINDINGS_AND_CONFLICTS.md:206), [DRF-A03](SOURCE_FINDINGS_AND_CONFLICTS.md:444). Read the full rows and their original conversation references; [the recheck](CONVERSATION_RECHECK.md) preserves the exact unit/exception routes.

<a id="up-f05-cross_vendor"></a>
#### F05.CROSS_VENDOR — Vendor trade/quote semantic reconciliation

[Existing definition, target and P0–P7](experiments/F.md#f05-cross_vendor) remain binding.

**Specific upgrade scope.** Compile source-specific event/flag semantics into canonical events and retain evidence-specific discrepancy categories.

**Local comparison.** Compare literal native decoding with canonical/reference projections on exact comparable observations; no vendor superiority inferred from unequal cohorts.

**Additional cases.** Trade summary differs across feeds; BBO snapshot repeats; multi-record event; unknown side distinct from missing print.

<a id="up-f06"></a>
### UP-F06 — Quality, gaps, stale data and quarantine

Parent: [F06](components/FOUNDATIONS.md); [local phases](experiments/F.md#f06); [definition refinement](SYSTEM_REFINEMENT.md#sr-f06). Upgrade role: `engineering`.

**Starting idea.** Drop a bad file or stop the entire strategy on a quality flag.

**Existing improvement path.** Raw/semantic checks, field masks, liveness and dependent-expert isolation.

**Remaining weakness.** A broad family-level mask can either discard too much usable information or understate which derived outputs were damaged.

**Further upgrade.** Compile field-to-output quality dependencies and affected time intervals. Produce a minimal invalidation set plus explicit uncertainty for partially affected aggregates; add a preceding-data liveness/change detector calibrated for each source cadence, below hard semantic rules.

**Fair comparison.** Global/family gating versus field-level propagation on planted and reviewed source faults; compare false halts and escaped corruption.

**Evidence.** Corrupt-output escape rate, false-blocked coverage, time to localization and restored independent opportunities.

**Additional local cases to implement.** Trade-history gap with recovered book; one expiry missing; healthy unchanged quote; schema corruption limited to one field.

**Decision or system use.** Preserve useful independent experts and direct repair effort to the actual limiting data defect.

**Exact reviewed source clauses.** [DTM-A07](SOURCE_FINDINGS_AND_CONFLICTS.md:65), [CEX-22](SOURCE_FINDINGS_AND_CONFLICTS.md:204), [INV-01](SOURCE_FINDINGS_AND_CONFLICTS.md:262), [INV-02](SOURCE_FINDINGS_AND_CONFLICTS.md:263), [INV-03](SOURCE_FINDINGS_AND_CONFLICTS.md:264), [INV-04](SOURCE_FINDINGS_AND_CONFLICTS.md:265), [INV-05](SOURCE_FINDINGS_AND_CONFLICTS.md:266), [INV-06](SOURCE_FINDINGS_AND_CONFLICTS.md:267), [INV-07](SOURCE_FINDINGS_AND_CONFLICTS.md:268), [INV-08](SOURCE_FINDINGS_AND_CONFLICTS.md:269), [INV-09](SOURCE_FINDINGS_AND_CONFLICTS.md:270), [INV-10](SOURCE_FINDINGS_AND_CONFLICTS.md:271), [INV-11](SOURCE_FINDINGS_AND_CONFLICTS.md:272), [INV-12](SOURCE_FINDINGS_AND_CONFLICTS.md:273).

<a id="up-f06-gap_recovery"></a>
#### F06.GAP_RECOVERY — Gap-specific state recovery

[Existing definition, target and P0–P7](experiments/F.md#f06-gap_recovery) remain binding.

**Specific upgrade scope.** Use dependency-local invalidation and correction-aware checkpoint repair by gap type rather than rebuilding unaffected state.

**Local comparison.** Compare full reference replay with repair strategies and bounded unavailable windows; measure recovery cost and validity restoration.

**Additional cases.** Gap inside unfinished bar; lost session open; late correction before checkpoint; source resumes at new price.

<a id="up-f07"></a>
### UP-F07 — As-of joins and coverage tensor

Parent: [F07](components/FOUNDATIONS.md); [local phases](experiments/F.md#f07); [definition refinement](SYSTEM_REFINEMENT.md#sr-f07). Upgrade role: `engineering`.

**Starting idea.** Join sources to the nearest timestamp and carry values forward.

**Existing improvement path.** Backward availability joins, sparse coverage tensor and purpose-specific eligibility.

**Remaining weakness.** Repeated full joins are expensive, and one generic joined table hides different effective information ages.

**Further upgrade.** Maintain incremental interval joins and a compact per-decision version vector. Materialize separate valuation, signing, forecasting and execution views only from eligible intervals; cache common-cohort membership independently of outcome data.

**Fair comparison.** Reference backward joins versus incremental views; common-grid and source-event cuts under identical availability rules.

**Evidence.** Exact eligible-row/age agreement, join CPU/RAM and retained valid coverage by operation.

**Additional local cases to implement.** Late correction closes an eligibility interval; sparse daily report; future-nearest match; many contracts share one underlying update.

**Decision or system use.** Faster, more transparent full-universe integration for O/X/C/L without weakening causal joins.

**Exact reviewed source clauses.** [CEX-05](SOURCE_FINDINGS_AND_CONFLICTS.md:187), [CEX-10](SOURCE_FINDINGS_AND_CONFLICTS.md:192), [CEX-23](SOURCE_FINDINGS_AND_CONFLICTS.md:205), [CEX-24](SOURCE_FINDINGS_AND_CONFLICTS.md:206), [INV-01](SOURCE_FINDINGS_AND_CONFLICTS.md:262), [INV-02](SOURCE_FINDINGS_AND_CONFLICTS.md:263), [INV-03](SOURCE_FINDINGS_AND_CONFLICTS.md:264), [INV-04](SOURCE_FINDINGS_AND_CONFLICTS.md:265), [INV-05](SOURCE_FINDINGS_AND_CONFLICTS.md:266), [INV-06](SOURCE_FINDINGS_AND_CONFLICTS.md:267), [INV-07](SOURCE_FINDINGS_AND_CONFLICTS.md:268), [INV-08](SOURCE_FINDINGS_AND_CONFLICTS.md:269), [INV-09](SOURCE_FINDINGS_AND_CONFLICTS.md:270), [INV-10](SOURCE_FINDINGS_AND_CONFLICTS.md:271), [INV-11](SOURCE_FINDINGS_AND_CONFLICTS.md:272), [INV-12](SOURCE_FINDINGS_AND_CONFLICTS.md:273), [DRF-A03](SOURCE_FINDINGS_AND_CONFLICTS.md:444).

**Conversation upgrade lineage.** [DTM-A07](SOURCE_FINDINGS_AND_CONFLICTS.md:65), [CEX-05](SOURCE_FINDINGS_AND_CONFLICTS.md:187), [CEX-23](SOURCE_FINDINGS_AND_CONFLICTS.md:205). Read the full rows and their original conversation references; [the recheck](CONVERSATION_RECHECK.md) preserves the exact unit/exception routes.

<a id="up-f07-age_support"></a>
#### F07.AGE_SUPPORT — Coverage and age propagation

[Existing definition, target and P0–P7](experiments/F.md#f07-age_support) remain binding.

**Specific upgrade scope.** Compile operation-specific support/age/liveness policies and propagate only affected capability masks.

**Local comparison.** Compare broad feed-level veto with field/cohort policies under the same causal validity rules; measure retained usable outputs and fault localization.

**Additional cases.** Healthy unchanged quote; missing wing only; repeated stale copy; expected slow publication.

<a id="up-f08"></a>
### UP-F08 — Futures rolls and equity adjustments

Parent: [F08](components/FOUNDATIONS.md); [local phases](experiments/F.md#f08); [definition refinement](SYSTEM_REFINEMENT.md#sr-f08). Upgrade role: `engineering`.

**Starting idea.** Back-adjust a continuous futures series and use it for every price calculation.

**Existing improvement path.** Actual-contract fills, causal roll/adjustment versions and explicit level translation.

**Remaining weakness.** Return forecasts and absolute-price objects need different histories; restarting everything at a roll can waste useful state.

**Further upgrade.** Maintain paired native-price and roll-neutral return views with a versioned bridge. Transfer only state whose invariants permit transfer; carry scale/return histories while re-anchoring price-bound objects through an uncertainty-tagged bridge or resetting them.

**Fair comparison.** Full reset, explicit bridge and native-only references on matched roll/corporate-action periods.

**Evidence.** Return/price conservation, warmup loss, bridge error versus zone width and economic sensitivity near rolls.

**Additional local cases to implement.** Roll spread changes intraday; stale bridge; split/dividend; old-contract profile mapped into new contract; indicator valid only in return units.

**Decision or system use.** Keep useful long history without manufacturing executable prices or false roll signals.

**Exact reviewed source clauses.** [CEX-26](SOURCE_FINDINGS_AND_CONFLICTS.md:208).

**Conversation upgrade lineage.** [CEX-26](SOURCE_FINDINGS_AND_CONFLICTS.md:208). Read the full rows and their original conversation references; [the recheck](CONVERSATION_RECHECK.md) preserves the exact unit/exception routes.

<a id="up-f08-roll_parity"></a>
#### F08.ROLL_PARITY — Roll and adjustment invariance

[Existing definition, target and P0–P7](experiments/F.md#f08-roll_parity) remain binding.

**Specific upgrade scope.** Use explicit raw/continuous coordinate bridges and reusable transformation metadata for each roll/adjustment view.

**Local comparison.** Compare economic/label invariance where mathematically valid and explicit differences where adjustments change level semantics.

**Additional cases.** Raw roll gap; backward adjustment changes old chart level; transformed tick units; mixed-contract profile.

<a id="up-f09"></a>
### UP-F09 — Causal bars and multiresolution aggregation

Parent: [F09](components/FOUNDATIONS.md); [local phases](experiments/F.md#f09); [definition refinement](SYSTEM_REFINEMENT.md#sr-f09). Upgrade role: `engineering`.

**Starting idea.** Aggregate time bars separately for each indicator.

**Existing improvement path.** Causal atomic time/event/volume bars with true OHLC and finalization.

**Remaining weakness.** Repeated aggregation can be costly and can subtly change extremes when different consumers partition the same tape.

**Further upgrade.** Build mergeable ordered summaries for volume, price-volume moments and cumulative-flow increments/extrema. Derive multiple clocks from shared event blocks while preserving whole-event threshold overshoot and correction dependencies; summarize only quantities with a proved composition rule.

**Fair comparison.** Literal event traversal versus ordered-block summaries across time/volume/event clocks and chunk boundaries.

**Evidence.** Exact OHLC/volume/CVD-extrema parity, throughput, memory and shared-state reuse.

**Additional local cases to implement.** One large trade crosses a volume threshold; two blocks have same final CVD but different extrema; correction touches an earlier block; empty interval.

**Decision or system use.** Support richer multiscale measurements economically, with a single reference arithmetic path.

**Exact reviewed source clauses.** [JTR-10](SOURCE_FINDINGS_AND_CONFLICTS.md:27), [OSF-01](SOURCE_FINDINGS_AND_CONFLICTS.md:795), [OSF-02](SOURCE_FINDINGS_AND_CONFLICTS.md:796), [OSF-03](SOURCE_FINDINGS_AND_CONFLICTS.md:797), [OSF-04](SOURCE_FINDINGS_AND_CONFLICTS.md:798), [OSF-05](SOURCE_FINDINGS_AND_CONFLICTS.md:799), [OSF-06](SOURCE_FINDINGS_AND_CONFLICTS.md:800), [OSF-07](SOURCE_FINDINGS_AND_CONFLICTS.md:801), [OSF-08](SOURCE_FINDINGS_AND_CONFLICTS.md:802), [OSF-09](SOURCE_FINDINGS_AND_CONFLICTS.md:803), [OSF-10](SOURCE_FINDINGS_AND_CONFLICTS.md:804), [PIN001-01](SOURCE_FINDINGS_AND_CONFLICTS.md:812), [PIN001-02](SOURCE_FINDINGS_AND_CONFLICTS.md:813), [PIN001-03](SOURCE_FINDINGS_AND_CONFLICTS.md:814), [PIN001-04](SOURCE_FINDINGS_AND_CONFLICTS.md:815), [PIN002-01](SOURCE_FINDINGS_AND_CONFLICTS.md:816), [PIN002-02](SOURCE_FINDINGS_AND_CONFLICTS.md:817), [PIN002-03](SOURCE_FINDINGS_AND_CONFLICTS.md:818), [PIN003-01](SOURCE_FINDINGS_AND_CONFLICTS.md:819), [PIN003-02](SOURCE_FINDINGS_AND_CONFLICTS.md:820), [PIN003-03](SOURCE_FINDINGS_AND_CONFLICTS.md:821), [PIN003-04](SOURCE_FINDINGS_AND_CONFLICTS.md:822), [PIN004-01](SOURCE_FINDINGS_AND_CONFLICTS.md:823), [PIN008-01](SOURCE_FINDINGS_AND_CONFLICTS.md:824), [PIN009-01](SOURCE_FINDINGS_AND_CONFLICTS.md:825), [PIN009-02](SOURCE_FINDINGS_AND_CONFLICTS.md:826), [PIN053-01](SOURCE_FINDINGS_AND_CONFLICTS.md:827), [PIN005-01](SOURCE_FINDINGS_AND_CONFLICTS.md:828), [PIN005-02](SOURCE_FINDINGS_AND_CONFLICTS.md:829), [PIN005-03](SOURCE_FINDINGS_AND_CONFLICTS.md:830), [PIN005-04](SOURCE_FINDINGS_AND_CONFLICTS.md:831), [PIN005-05](SOURCE_FINDINGS_AND_CONFLICTS.md:832), [PIN006-01](SOURCE_FINDINGS_AND_CONFLICTS.md:833), [PIN006-02](SOURCE_FINDINGS_AND_CONFLICTS.md:834), [PIN006-03](SOURCE_FINDINGS_AND_CONFLICTS.md:835), [PIN007-01](SOURCE_FINDINGS_AND_CONFLICTS.md:836), [PIN007-02](SOURCE_FINDINGS_AND_CONFLICTS.md:837), [PIN007-03](SOURCE_FINDINGS_AND_CONFLICTS.md:838), [PIN007-04](SOURCE_FINDINGS_AND_CONFLICTS.md:839), [PIN007-05](SOURCE_FINDINGS_AND_CONFLICTS.md:840), [PIN010-01](SOURCE_FINDINGS_AND_CONFLICTS.md:841), [PIN010-02](SOURCE_FINDINGS_AND_CONFLICTS.md:842), [PIN010-03](SOURCE_FINDINGS_AND_CONFLICTS.md:843), [PIN010-04](SOURCE_FINDINGS_AND_CONFLICTS.md:844), [PIN011-01](SOURCE_FINDINGS_AND_CONFLICTS.md:845), [PIN011-02](SOURCE_FINDINGS_AND_CONFLICTS.md:846), [PIN011-03](SOURCE_FINDINGS_AND_CONFLICTS.md:847), [PIN011-04](SOURCE_FINDINGS_AND_CONFLICTS.md:848), [PIN011-05](SOURCE_FINDINGS_AND_CONFLICTS.md:849), [PIN011-06](SOURCE_FINDINGS_AND_CONFLICTS.md:850), [PIN011-07](SOURCE_FINDINGS_AND_CONFLICTS.md:851), [PIN012-01](SOURCE_FINDINGS_AND_CONFLICTS.md:852), [PIN012-02](SOURCE_FINDINGS_AND_CONFLICTS.md:853), [PIN012-03](SOURCE_FINDINGS_AND_CONFLICTS.md:854), [PIN012-04](SOURCE_FINDINGS_AND_CONFLICTS.md:855), [PIN012-05](SOURCE_FINDINGS_AND_CONFLICTS.md:856), [PIN013-01](SOURCE_FINDINGS_AND_CONFLICTS.md:857), [PIN013-02](SOURCE_FINDINGS_AND_CONFLICTS.md:858), [PIN013-03](SOURCE_FINDINGS_AND_CONFLICTS.md:859), [PIN013-04](SOURCE_FINDINGS_AND_CONFLICTS.md:860), [PIN013-05](SOURCE_FINDINGS_AND_CONFLICTS.md:861), [PIN013-06](SOURCE_FINDINGS_AND_CONFLICTS.md:862), [PIN014-01](SOURCE_FINDINGS_AND_CONFLICTS.md:863), [PIN014-02](SOURCE_FINDINGS_AND_CONFLICTS.md:864), [PIN015-01](SOURCE_FINDINGS_AND_CONFLICTS.md:865), [PIN015-02](SOURCE_FINDINGS_AND_CONFLICTS.md:866), [PIN015-03](SOURCE_FINDINGS_AND_CONFLICTS.md:867), [PIN016-01](SOURCE_FINDINGS_AND_CONFLICTS.md:868), [PIN016-02](SOURCE_FINDINGS_AND_CONFLICTS.md:869), [PIN016-03](SOURCE_FINDINGS_AND_CONFLICTS.md:870), [PIN016-04](SOURCE_FINDINGS_AND_CONFLICTS.md:871), [PIN017-01](SOURCE_FINDINGS_AND_CONFLICTS.md:872), [PIN017-02](SOURCE_FINDINGS_AND_CONFLICTS.md:873), [PIN017-03](SOURCE_FINDINGS_AND_CONFLICTS.md:874), [PIN017-04](SOURCE_FINDINGS_AND_CONFLICTS.md:875), [PIN018-01](SOURCE_FINDINGS_AND_CONFLICTS.md:876), [PIN018-02](SOURCE_FINDINGS_AND_CONFLICTS.md:877), [PIN024-01](SOURCE_FINDINGS_AND_CONFLICTS.md:878), [PIN024-02](SOURCE_FINDINGS_AND_CONFLICTS.md:879), [PIN019-01](SOURCE_FINDINGS_AND_CONFLICTS.md:887), [PIN019-02](SOURCE_FINDINGS_AND_CONFLICTS.md:888), [PIN019-03](SOURCE_FINDINGS_AND_CONFLICTS.md:889), [PIN020-01](SOURCE_FINDINGS_AND_CONFLICTS.md:890), [PIN020-02](SOURCE_FINDINGS_AND_CONFLICTS.md:891), [PIN021-01](SOURCE_FINDINGS_AND_CONFLICTS.md:892), [PIN021-02](SOURCE_FINDINGS_AND_CONFLICTS.md:893), [PIN022-01](SOURCE_FINDINGS_AND_CONFLICTS.md:894), [PIN022-02](SOURCE_FINDINGS_AND_CONFLICTS.md:895), [PIN022-03](SOURCE_FINDINGS_AND_CONFLICTS.md:896), [PIN023-01](SOURCE_FINDINGS_AND_CONFLICTS.md:897), [PIN023-02](SOURCE_FINDINGS_AND_CONFLICTS.md:898), [PIN025-01](SOURCE_FINDINGS_AND_CONFLICTS.md:899), [PIN026-01](SOURCE_FINDINGS_AND_CONFLICTS.md:900), [PIN026-02](SOURCE_FINDINGS_AND_CONFLICTS.md:901), [PIN027-01](SOURCE_FINDINGS_AND_CONFLICTS.md:902), [PIN027-02](SOURCE_FINDINGS_AND_CONFLICTS.md:903), [PIN028-01](SOURCE_FINDINGS_AND_CONFLICTS.md:904), [PIN028-02](SOURCE_FINDINGS_AND_CONFLICTS.md:905), [PIN028-03](SOURCE_FINDINGS_AND_CONFLICTS.md:906), [PIN029-01](SOURCE_FINDINGS_AND_CONFLICTS.md:907), [PIN029-02](SOURCE_FINDINGS_AND_CONFLICTS.md:908), [PIN029-03](SOURCE_FINDINGS_AND_CONFLICTS.md:909), [PIN030-01](SOURCE_FINDINGS_AND_CONFLICTS.md:910), [PIN030-02](SOURCE_FINDINGS_AND_CONFLICTS.md:911), [PIN030-03](SOURCE_FINDINGS_AND_CONFLICTS.md:912), [PIN031-01](SOURCE_FINDINGS_AND_CONFLICTS.md:913), [PIN032-01](SOURCE_FINDINGS_AND_CONFLICTS.md:914), [PIN032-02](SOURCE_FINDINGS_AND_CONFLICTS.md:915), [PIN032-03](SOURCE_FINDINGS_AND_CONFLICTS.md:916), [PIN033-01](SOURCE_FINDINGS_AND_CONFLICTS.md:917), [PIN033-02](SOURCE_FINDINGS_AND_CONFLICTS.md:918), [PIN034-01](SOURCE_FINDINGS_AND_CONFLICTS.md:919), [PIN035-01](SOURCE_FINDINGS_AND_CONFLICTS.md:920), [PIN035-02](SOURCE_FINDINGS_AND_CONFLICTS.md:921), [PIN035-03](SOURCE_FINDINGS_AND_CONFLICTS.md:922), [PIN035-04](SOURCE_FINDINGS_AND_CONFLICTS.md:923), [PIN036-01](SOURCE_FINDINGS_AND_CONFLICTS.md:925), [PIN036-02](SOURCE_FINDINGS_AND_CONFLICTS.md:926), [PIN037-01](SOURCE_FINDINGS_AND_CONFLICTS.md:927), [PIN037-02](SOURCE_FINDINGS_AND_CONFLICTS.md:928), [PIN038-01](SOURCE_FINDINGS_AND_CONFLICTS.md:930), [PIN038-02](SOURCE_FINDINGS_AND_CONFLICTS.md:931), [PIN039-01](SOURCE_FINDINGS_AND_CONFLICTS.md:933), [PIN039-02](SOURCE_FINDINGS_AND_CONFLICTS.md:934), [PIN040-01](SOURCE_FINDINGS_AND_CONFLICTS.md:935), [PIN040-02](SOURCE_FINDINGS_AND_CONFLICTS.md:936), [PIN041-01](SOURCE_FINDINGS_AND_CONFLICTS.md:938), [PIN041-02](SOURCE_FINDINGS_AND_CONFLICTS.md:939), [PIN041-03](SOURCE_FINDINGS_AND_CONFLICTS.md:940), [PIN042-01](SOURCE_FINDINGS_AND_CONFLICTS.md:942), [PIN042-02](SOURCE_FINDINGS_AND_CONFLICTS.md:943), [PIN043-01](SOURCE_FINDINGS_AND_CONFLICTS.md:944), [PIN044-01](SOURCE_FINDINGS_AND_CONFLICTS.md:945), [PIN044-02](SOURCE_FINDINGS_AND_CONFLICTS.md:946), [PIN045-01](SOURCE_FINDINGS_AND_CONFLICTS.md:948), [PIN045-02](SOURCE_FINDINGS_AND_CONFLICTS.md:949), [PIN045-03](SOURCE_FINDINGS_AND_CONFLICTS.md:950), [PIN045-04](SOURCE_FINDINGS_AND_CONFLICTS.md:951), [PIN045-05](SOURCE_FINDINGS_AND_CONFLICTS.md:952), [PIN045-06](SOURCE_FINDINGS_AND_CONFLICTS.md:953), [PIN046-01](SOURCE_FINDINGS_AND_CONFLICTS.md:955), [PIN047-01](SOURCE_FINDINGS_AND_CONFLICTS.md:956), [PIN047-02](SOURCE_FINDINGS_AND_CONFLICTS.md:957), [PIN047-03](SOURCE_FINDINGS_AND_CONFLICTS.md:958), [PIN048-01](SOURCE_FINDINGS_AND_CONFLICTS.md:960), [PIN048-02](SOURCE_FINDINGS_AND_CONFLICTS.md:961), [PIN048-03](SOURCE_FINDINGS_AND_CONFLICTS.md:962), [PIN049-01](SOURCE_FINDINGS_AND_CONFLICTS.md:964), [PIN049-02](SOURCE_FINDINGS_AND_CONFLICTS.md:965), [PIN049-03](SOURCE_FINDINGS_AND_CONFLICTS.md:966), [PIN050-01](SOURCE_FINDINGS_AND_CONFLICTS.md:968), [PIN050-02](SOURCE_FINDINGS_AND_CONFLICTS.md:969), [PIN050-03](SOURCE_FINDINGS_AND_CONFLICTS.md:970), [PIN051-01](SOURCE_FINDINGS_AND_CONFLICTS.md:971), [PIN051-02](SOURCE_FINDINGS_AND_CONFLICTS.md:972), [PIN052-01](SOURCE_FINDINGS_AND_CONFLICTS.md:974), [PIN052-02](SOURCE_FINDINGS_AND_CONFLICTS.md:975), [PIN052-03](SOURCE_FINDINGS_AND_CONFLICTS.md:976), [PIN054-01](SOURCE_FINDINGS_AND_CONFLICTS.md:978), [PIN054-02](SOURCE_FINDINGS_AND_CONFLICTS.md:979), [PIN055-01](SOURCE_FINDINGS_AND_CONFLICTS.md:980), [PIN055-02](SOURCE_FINDINGS_AND_CONFLICTS.md:981), [PIN056-01](SOURCE_FINDINGS_AND_CONFLICTS.md:983), [PIN056-02](SOURCE_FINDINGS_AND_CONFLICTS.md:984), [PIN057-01](SOURCE_FINDINGS_AND_CONFLICTS.md:985), [PIN057-02](SOURCE_FINDINGS_AND_CONFLICTS.md:986), [PIN057-03](SOURCE_FINDINGS_AND_CONFLICTS.md:987), [PIN058-01](SOURCE_FINDINGS_AND_CONFLICTS.md:989), [PIN059-01](SOURCE_FINDINGS_AND_CONFLICTS.md:990), [PIN059-02](SOURCE_FINDINGS_AND_CONFLICTS.md:991), [PIN060-01](SOURCE_FINDINGS_AND_CONFLICTS.md:993), [PIN060-02](SOURCE_FINDINGS_AND_CONFLICTS.md:994), [PIN060-03](SOURCE_FINDINGS_AND_CONFLICTS.md:995), [PIN061-01](SOURCE_FINDINGS_AND_CONFLICTS.md:997), [PIN061-02](SOURCE_FINDINGS_AND_CONFLICTS.md:998), [PIN061-03](SOURCE_FINDINGS_AND_CONFLICTS.md:999), [PIN062-01](SOURCE_FINDINGS_AND_CONFLICTS.md:1001), [PIN062-02](SOURCE_FINDINGS_AND_CONFLICTS.md:1002), [PIN062-03](SOURCE_FINDINGS_AND_CONFLICTS.md:1003), [PIN063-01](SOURCE_FINDINGS_AND_CONFLICTS.md:1005), [PIN063-02](SOURCE_FINDINGS_AND_CONFLICTS.md:1006), [PIN063-03](SOURCE_FINDINGS_AND_CONFLICTS.md:1007), [PIN064-01](SOURCE_FINDINGS_AND_CONFLICTS.md:1009), [PIN064-02](SOURCE_FINDINGS_AND_CONFLICTS.md:1010), [PIN065-01](SOURCE_FINDINGS_AND_CONFLICTS.md:1012), [PIN065-02](SOURCE_FINDINGS_AND_CONFLICTS.md:1013), [PIN065-03](SOURCE_FINDINGS_AND_CONFLICTS.md:1014), [PIN066-01](SOURCE_FINDINGS_AND_CONFLICTS.md:1016), [PIN066-02](SOURCE_FINDINGS_AND_CONFLICTS.md:1017), [PIN066-03](SOURCE_FINDINGS_AND_CONFLICTS.md:1018), [PIN066-04](SOURCE_FINDINGS_AND_CONFLICTS.md:1019), [PIN067-01](SOURCE_FINDINGS_AND_CONFLICTS.md:1021), [PIN067-02](SOURCE_FINDINGS_AND_CONFLICTS.md:1022), [PIN068-01](SOURCE_FINDINGS_AND_CONFLICTS.md:1024), [PIN068-02](SOURCE_FINDINGS_AND_CONFLICTS.md:1025), [PIN068-03](SOURCE_FINDINGS_AND_CONFLICTS.md:1026), [PIN069-01](SOURCE_FINDINGS_AND_CONFLICTS.md:1028), [PIN069-02](SOURCE_FINDINGS_AND_CONFLICTS.md:1029), [PIN069-03](SOURCE_FINDINGS_AND_CONFLICTS.md:1030), [PIN069-04](SOURCE_FINDINGS_AND_CONFLICTS.md:1031), [PIN070-01](SOURCE_FINDINGS_AND_CONFLICTS.md:1033), [PIN070-02](SOURCE_FINDINGS_AND_CONFLICTS.md:1034), [PIN071-01](SOURCE_FINDINGS_AND_CONFLICTS.md:1036), [PIN071-02](SOURCE_FINDINGS_AND_CONFLICTS.md:1037), [PIN071-03](SOURCE_FINDINGS_AND_CONFLICTS.md:1038), [PIN071-04](SOURCE_FINDINGS_AND_CONFLICTS.md:1039), [PIN071-05](SOURCE_FINDINGS_AND_CONFLICTS.md:1040), [PIN071-06](SOURCE_FINDINGS_AND_CONFLICTS.md:1041), [PIN071-07](SOURCE_FINDINGS_AND_CONFLICTS.md:1042), [PIN071-08](SOURCE_FINDINGS_AND_CONFLICTS.md:1043), [PIN072-01](SOURCE_FINDINGS_AND_CONFLICTS.md:1045), [PIN072-02](SOURCE_FINDINGS_AND_CONFLICTS.md:1046), [PIN073-01](SOURCE_FINDINGS_AND_CONFLICTS.md:1048), [PIN073-02](SOURCE_FINDINGS_AND_CONFLICTS.md:1049), [PIN074-01](SOURCE_FINDINGS_AND_CONFLICTS.md:1051), [PIN074-02](SOURCE_FINDINGS_AND_CONFLICTS.md:1052), [PIN075-01](SOURCE_FINDINGS_AND_CONFLICTS.md:1054), [PIN075-02](SOURCE_FINDINGS_AND_CONFLICTS.md:1055), [PIN076-01](SOURCE_FINDINGS_AND_CONFLICTS.md:1057), [PIN076-02](SOURCE_FINDINGS_AND_CONFLICTS.md:1058), [PIN077-01](SOURCE_FINDINGS_AND_CONFLICTS.md:1060), [PIN077-02](SOURCE_FINDINGS_AND_CONFLICTS.md:1061), [PIN078-01](SOURCE_FINDINGS_AND_CONFLICTS.md:1063), [PIN078-02](SOURCE_FINDINGS_AND_CONFLICTS.md:1064), [PIN079-01](SOURCE_FINDINGS_AND_CONFLICTS.md:1066), [PIN079-02](SOURCE_FINDINGS_AND_CONFLICTS.md:1067), [PIN079-03](SOURCE_FINDINGS_AND_CONFLICTS.md:1068), [PIN079-04](SOURCE_FINDINGS_AND_CONFLICTS.md:1069), [PIN080-01](SOURCE_FINDINGS_AND_CONFLICTS.md:1071), [PIN080-02](SOURCE_FINDINGS_AND_CONFLICTS.md:1072), [PIN080-03](SOURCE_FINDINGS_AND_CONFLICTS.md:1073), [PIN081-01](SOURCE_FINDINGS_AND_CONFLICTS.md:1075), [PIN081-02](SOURCE_FINDINGS_AND_CONFLICTS.md:1076), [PIN081-03](SOURCE_FINDINGS_AND_CONFLICTS.md:1077), [PIN081-04](SOURCE_FINDINGS_AND_CONFLICTS.md:1078), [PIN082-01](SOURCE_FINDINGS_AND_CONFLICTS.md:1080), [PIN082-02](SOURCE_FINDINGS_AND_CONFLICTS.md:1081), [PIN082-03](SOURCE_FINDINGS_AND_CONFLICTS.md:1082), [PIN083-01](SOURCE_FINDINGS_AND_CONFLICTS.md:1084), [PIN083-02](SOURCE_FINDINGS_AND_CONFLICTS.md:1085).

**Conversation upgrade lineage.** [CRL-18](SOURCE_FINDINGS_AND_CONFLICTS.md:234). Read the full rows and their original conversation references; [the recheck](CONVERSATION_RECHECK.md) preserves the exact unit/exception routes.

<a id="up-f09-activity_bars"></a>
#### F09.ACTIVITY_BARS — Event and activity bars

[Existing definition, target and P0–P7](experiments/F.md#f09-activity_bars) remain binding.

**Specific upgrade scope.** Maintain shared whole-event prefix summaries for clock, trade-count, volume and volatility/activity bars.

**Local comparison.** Compare independent builders with one-pass multi-bar materialization, true cumulative OHLC and boundary overshoot accounting.

**Additional cases.** One large print exceeds threshold; identical close different intrabar extrema; no events; reset inside formation.

<a id="up-f10"></a>
### UP-F10 — Versioned market-object and event registry

Parent: [F10](components/FOUNDATIONS.md); [local phases](experiments/F.md#f10); [definition refinement](SYSTEM_REFINEMENT.md#sr-f10). Upgrade role: `engineering`.

**Starting idea.** Keep chart levels in mutable lists and delete them after failure.

**Existing improvement path.** Immutable market-object revisions, visits, provenance and lifecycle states.

**Remaining weakness.** Geometry, observations, forecast views and action aliases can still be entangled, causing duplicate evidence or lost history.

**Further upgrade.** Separate an immutable object/geometry graph, an append-only observation-event graph and derived forecast/action views. Maintain explicit equivalence, parent, split/merge and shared-idea edges; query historical state by cut without replaying all unrelated objects.

**Fair comparison.** Mutable/reference reconstruction versus graph projections and incremental indexes on the same event history.

**Evidence.** Historical-view agreement, duplicate-action rate, lineage completeness and object-query/restart cost.

**Additional local cases to implement.** POC and VWAP coincide; node split/merge; object renamed after loss; later geometry correction; expired object needed for labels.

**Decision or system use.** All generators gain reusable lifecycle/lineage machinery; L18/P04 can distinguish shared evidence from fresh opportunities.

**Exact reviewed source clauses.** [DRF-A07](SOURCE_FINDINGS_AND_CONFLICTS.md:448).

<a id="up-f10-lineage"></a>
#### F10.LINEAGE — Object and event identity integrity

[Existing definition, target and P0–P7](experiments/F.md#f10-lineage) remain binding.

**Specific upgrade scope.** Use typed object/revision/event relations and canonical identity independently from display grouping.

**Local comparison.** Compare registry/reference identity under split/merge/reanchor and exact action deduplication; measure false new-object counts.

**Additional cases.** New ID reuses same evidence; same price different parent; moving provisional object; correction invalidation.

<a id="up-f11"></a>
### UP-F11 — Feature, prediction and fold artifact store

Parent: [F11](components/FOUNDATIONS.md); [local phases](experiments/F.md#f11); [definition refinement](SYSTEM_REFINEMENT.md#sr-f11). Upgrade role: `engineering`.

**Starting idea.** Save feature tables and trained models under descriptive filenames.

**Existing improvement path.** Content-addressed artifacts, fold/target versions and OOF lineage.

**Remaining weakness.** A small upstream definition change can trigger either unnecessary complete rebuilds or dangerous stale reuse.

**Further upgrade.** Build a dependency-addressed artifact DAG with exact fit/inference closures and column-level transformation ownership. Recompute affected descendants only; keep reusable fold-independent measurements separate from fold-fitted transforms and include executable code/config hashes.

**Fair comparison.** Clean rebuild versus incremental rebuild after controlled data, definition, target, fold and calibrator changes.

**Evidence.** Stale-cache escape rate, identical final artifacts, recompute hours/storage saved and explainable invalidation paths.

**Additional local cases to implement.** Scaler changes; same model name with new transform; target horizon changes; late report revision; calibration fitted on a new cohort.

**Decision or system use.** Make the full experiment program reproducible and affordable without sharing fitted state across prohibited folds.

**Exact reviewed source clauses.** [DTM-A01](SOURCE_FINDINGS_AND_CONFLICTS.md:59), [DRF-A26](SOURCE_FINDINGS_AND_CONFLICTS.md:467).

**Conversation upgrade lineage.** [DTM-A01](SOURCE_FINDINGS_AND_CONFLICTS.md:59), [JCV-U06](SOURCE_FINDINGS_AND_CONFLICTS.md:159), [CEX-27](SOURCE_FINDINGS_AND_CONFLICTS.md:209), [CRL-20](SOURCE_FINDINGS_AND_CONFLICTS.md:236), [DRF-A07](SOURCE_FINDINGS_AND_CONFLICTS.md:448), [DRF-A26](SOURCE_FINDINGS_AND_CONFLICTS.md:467). Read the full rows and their original conversation references; [the recheck](CONVERSATION_RECHECK.md) preserves the exact unit/exception routes.

<a id="up-f11-input_audit"></a>
#### F11.INPUT_AUDIT — Actual model-input lineage

[Existing definition, target and P0–P7](experiments/F.md#f11-input_audit) remain binding.

**Specific upgrade scope.** Generate compact input dependency manifests and first-change impact maps from actual feature reads.

**Local comparison.** Compare declared versus instrumented lineage and content hashes, including fitted transforms and apparently unused data paths.

**Additional cases.** Feature reads future-adjusted value; stale cache; calibration dependency omitted; identical numeric value new version.

<a id="up-f12"></a>
### UP-F12 — Historical/live adapter and receipt telemetry

Parent: [F12](components/FOUNDATIONS.md); [local phases](experiments/F.md#f12); [definition refinement](SYSTEM_REFINEMENT.md#sr-f12). Upgrade role: `engineering`.

**Starting idea.** Use separate historical scripts and a later live connector.

**Existing improvement path.** Common event contracts, receipt telemetry and historical/live parity.

**Remaining weakness.** Equivalent formulas can still diverge because arrival scheduling, reconnect and batching differ.

**Further upgrade.** Create a portable arrival-trace replay format containing source deliveries, timers, computation completions and order-state messages. Drive reference and optimized adapters from the same trace; use seeded fault schedules and minimal divergent-prefix extraction for diagnosis.

**Fair comparison.** Native historical replay, captured-arrival replay and adapter projections under identical event/timer traces.

**Evidence.** Decision/state parity, first divergence, lag distribution and recoverability; actual live evidence remains a later dependency.

**Additional local cases to implement.** Reconnect duplicates; batch boundary changes; delayed source; clock adjustment; interrupted computation; timer fires without a trade.

**Decision or system use.** Upgrade parity testing from isolated formula checks to reproducible whole-runtime behavior.

**Exact reviewed source clauses.** [JCV-U03](SOURCE_FINDINGS_AND_CONFLICTS.md:156), [CEX-20](SOURCE_FINDINGS_AND_CONFLICTS.md:202), [CEX-22](SOURCE_FINDINGS_AND_CONFLICTS.md:204).

**Conversation upgrade lineage.** [CEX-20](SOURCE_FINDINGS_AND_CONFLICTS.md:202), [CEX-22](SOURCE_FINDINGS_AND_CONFLICTS.md:204), [CEX-24](SOURCE_FINDINGS_AND_CONFLICTS.md:206). Read the full rows and their original conversation references; [the recheck](CONVERSATION_RECHECK.md) preserves the exact unit/exception routes.

<a id="up-f12-parity"></a>
#### F12.PARITY — Historical and captured-live equivalence

[Existing definition, target and P0–P7](experiments/F.md#f12-parity) remain binding.

**Specific upgrade scope.** Share semantic kernels across historical/captured-live paths and compare versioned traces, including receipt uncertainty.

**Local comparison.** Compare value, state, timing and action parity; report legitimate transport/numeric differences separately from semantic mismatches.

**Additional cases.** Restart mid-event; sequence tie; actual finish already includes latency; missing historical receipt.

<a id="family-m"></a>
## Measurements

<a id="up-m01"></a>
### UP-M01 — Ordinary traded CVD

Parent: [M01](components/MEASUREMENTS.md); [local phases](experiments/M.md#m01); [definition refinement](SYSTEM_REFINEMENT.md#sr-m01). Upgrade role: `measurement`.

**Starting idea.** Accumulate signed trade volume and inspect its direction.

**Existing improvement path.** Exact ordinary CVD, reset/rolling variants, separate unknown volume and uncertainty.

**Remaining weakness.** The cumulative level mixes predictable activity, anchor age and unusual directional pressure; raw CVD alone does not describe how flow arrived.

**Further upgrade.** Keep literal CVD unchanged and add causal signed-flow rate, innovations relative to train-fitted expected side/activity, multiple registered decay kernels and joint flow/price-progress residual features. Export raw and residual channels together, with unknown-side bounds and missing-tape masks; interpretation belongs to C/G/R.

**Fair comparison.** Literal CVD, seasonal signed rate, residual multiscale flow and downstream sparse interactions on identical prints.

**Evidence.** Arithmetic parity, residual support/scale stability, incremental target proper loss and constrained policy net.

**Additional local cases to implement.** Balanced heavy trading; reset discontinuity; unchanged cumulative close with opposite paths; observed unknown side versus missing trades.

**Decision or system use.** Give downstream models unusual flow, persistence and pressure-response information without redefining CVD or assuming every signed print moves price.

**Exact reviewed source clauses.** [CEX-05](SOURCE_FINDINGS_AND_CONFLICTS.md:187), [DM5-01](SOURCE_FINDINGS_AND_CONFLICTS.md:348), [DM5-02](SOURCE_FINDINGS_AND_CONFLICTS.md:349), [DM5-03](SOURCE_FINDINGS_AND_CONFLICTS.md:350), [DM5-04](SOURCE_FINDINGS_AND_CONFLICTS.md:351), [FP9-01](SOURCE_FINDINGS_AND_CONFLICTS.md:374), [FP9-02](SOURCE_FINDINGS_AND_CONFLICTS.md:375), [FP9-03](SOURCE_FINDINGS_AND_CONFLICTS.md:376), [FP9-04](SOURCE_FINDINGS_AND_CONFLICTS.md:377), [FP9-05](SOURCE_FINDINGS_AND_CONFLICTS.md:378), [FP9-06](SOURCE_FINDINGS_AND_CONFLICTS.md:379), [VW10-01](SOURCE_FINDINGS_AND_CONFLICTS.md:380), [VW10-02](SOURCE_FINDINGS_AND_CONFLICTS.md:381), [VW10-03](SOURCE_FINDINGS_AND_CONFLICTS.md:382), [VW10-04](SOURCE_FINDINGS_AND_CONFLICTS.md:383), [VW10-05](SOURCE_FINDINGS_AND_CONFLICTS.md:384), [VW10-06](SOURCE_FINDINGS_AND_CONFLICTS.md:385), [VW10-07](SOURCE_FINDINGS_AND_CONFLICTS.md:386), [DEN-01](SOURCE_FINDINGS_AND_CONFLICTS.md:409), [DEN-02](SOURCE_FINDINGS_AND_CONFLICTS.md:410), [DEN-03](SOURCE_FINDINGS_AND_CONFLICTS.md:411), [DEN-04](SOURCE_FINDINGS_AND_CONFLICTS.md:412), [DEN-05](SOURCE_FINDINGS_AND_CONFLICTS.md:413), [WIC-06](SOURCE_FINDINGS_AND_CONFLICTS.md:582), [YMA-02](SOURCE_FINDINGS_AND_CONFLICTS.md:590), [K18-07](SOURCE_FINDINGS_AND_CONFLICTS.md:658), [F23-03](SOURCE_FINDINGS_AND_CONFLICTS.md:669), [ALS-01](SOURCE_FINDINGS_AND_CONFLICTS.md:696), [ALS-03](SOURCE_FINDINGS_AND_CONFLICTS.md:698), [NYA-01](SOURCE_FINDINGS_AND_CONFLICTS.md:709), [SRE-02](SOURCE_FINDINGS_AND_CONFLICTS.md:723), [SRE-05](SOURCE_FINDINGS_AND_CONFLICTS.md:726), [OBT-01](SOURCE_FINDINGS_AND_CONFLICTS.md:750), [OBT-06](SOURCE_FINDINGS_AND_CONFLICTS.md:755), [MVF-02](SOURCE_FINDINGS_AND_CONFLICTS.md:784), [PIN029-01](SOURCE_FINDINGS_AND_CONFLICTS.md:907), [PIN050-01](SOURCE_FINDINGS_AND_CONFLICTS.md:968), [PIN072-02](SOURCE_FINDINGS_AND_CONFLICTS.md:1046), [PIN079-04](SOURCE_FINDINGS_AND_CONFLICTS.md:1069).

<a id="up-m01-sign_reset"></a>
#### M01.SIGN_RESET — CVD sign and anchor decomposition

[Existing definition, target and P0–P7](experiments/M.md#m01-sign_reset) remain binding.

**Specific upgrade scope.** Keep every sign/reset series exact, then add exposure-normalized innovations and multiple decay clocks with the same underlying print ledger.

**Local comparison.** Compare raw/sign-proxy/reset variants and residual interpretations at common cuts with unknown-side bounds.

**Additional cases.** Reset creates slope jump; unknown signs concentrated in one interval; opposite paths same close.

<a id="up-m02"></a>
### UP-M02 — Size-cohort CVD with true within-bar OHLC

Parent: [M02](components/MEASUREMENTS.md); [local phases](experiments/M.md#m02); [definition refinement](SYSTEM_REFINEMENT.md#sr-m02). Upgrade role: `measurement`.

**Starting idea.** Filter trades above one size cutoff.

**Existing improvement path.** Source fixed cohorts, adaptive cohorts and true cumulative-path OHLC for each cohort.

**Remaining weakness.** Hard boundaries discard near-threshold similarity, while cohort activity and reported trade-summary conventions can change the apparent large-trader signal.

**Further upgrade.** Add a continuous trade-size basis with overlapping soft cohort weights whose sum is controlled, alongside every exact hard cohort. Preserve true weighted cumulative OHLC and exposure/breadth per channel; compare normalized size/intensity and cross-cohort lead-lag features only on compatible provider/aggregation cohorts.

**Fair comparison.** All-flow, source fixed/adaptive buckets, close-only versus true OHLC, and continuous size-basis channels.

**Evidence.** Volume reconciliation, threshold stability, intrabar information increment, conditional path loss and runtime.

**Additional local cases to implement.** Print shifts across hard cutoff; provider aggregates differently; one huge print; empty cohort; future quantiles leak.

**Decision or system use.** Retain the user's cohort distinctions while testing whether smoother size information and path shape outperform arbitrary cutoffs.

**Exact reviewed source clauses.** [DTM-A09](SOURCE_FINDINGS_AND_CONFLICTS.md:67), [JXA-13](SOURCE_FINDINGS_AND_CONFLICTS.md:112), [JXA-15](SOURCE_FINDINGS_AND_CONFLICTS.md:114), [CEX-05](SOURCE_FINDINGS_AND_CONFLICTS.md:187), [CRL-15](SOURCE_FINDINGS_AND_CONFLICTS.md:231), [FP9-04](SOURCE_FINDINGS_AND_CONFLICTS.md:377), [VW10-04](SOURCE_FINDINGS_AND_CONFLICTS.md:383), [DRF-A02](SOURCE_FINDINGS_AND_CONFLICTS.md:443), [WIC-06](SOURCE_FINDINGS_AND_CONFLICTS.md:582), [YMA-02](SOURCE_FINDINGS_AND_CONFLICTS.md:590), [K18-07](SOURCE_FINDINGS_AND_CONFLICTS.md:658), [F23-03](SOURCE_FINDINGS_AND_CONFLICTS.md:669), [ALS-01](SOURCE_FINDINGS_AND_CONFLICTS.md:696), [ALS-03](SOURCE_FINDINGS_AND_CONFLICTS.md:698), [NYA-01](SOURCE_FINDINGS_AND_CONFLICTS.md:709), [SRE-02](SOURCE_FINDINGS_AND_CONFLICTS.md:723), [SRE-05](SOURCE_FINDINGS_AND_CONFLICTS.md:726), [OBT-01](SOURCE_FINDINGS_AND_CONFLICTS.md:750), [OBT-02](SOURCE_FINDINGS_AND_CONFLICTS.md:751), [OBT-03](SOURCE_FINDINGS_AND_CONFLICTS.md:752), [OBT-04](SOURCE_FINDINGS_AND_CONFLICTS.md:753), [OBT-05](SOURCE_FINDINGS_AND_CONFLICTS.md:754), [OBT-06](SOURCE_FINDINGS_AND_CONFLICTS.md:755), [OBT-07](SOURCE_FINDINGS_AND_CONFLICTS.md:756), [OBT-08](SOURCE_FINDINGS_AND_CONFLICTS.md:757), [OBT-09](SOURCE_FINDINGS_AND_CONFLICTS.md:758), [OBT-10](SOURCE_FINDINGS_AND_CONFLICTS.md:759), [MVF-01](SOURCE_FINDINGS_AND_CONFLICTS.md:783), [MVF-02](SOURCE_FINDINGS_AND_CONFLICTS.md:784), [MVF-03](SOURCE_FINDINGS_AND_CONFLICTS.md:785), [MVF-04](SOURCE_FINDINGS_AND_CONFLICTS.md:786), [MVF-05](SOURCE_FINDINGS_AND_CONFLICTS.md:787), [MVF-06](SOURCE_FINDINGS_AND_CONFLICTS.md:788), [MVF-07](SOURCE_FINDINGS_AND_CONFLICTS.md:789), [PIN029-01](SOURCE_FINDINGS_AND_CONFLICTS.md:907), [PIN050-01](SOURCE_FINDINGS_AND_CONFLICTS.md:968), [PIN072-02](SOURCE_FINDINGS_AND_CONFLICTS.md:1046), [PIN079-04](SOURCE_FINDINGS_AND_CONFLICTS.md:1069).

**Conversation upgrade lineage.** [CEX-05](SOURCE_FINDINGS_AND_CONFLICTS.md:187), [CRL-15](SOURCE_FINDINGS_AND_CONFLICTS.md:231). Read the full rows and their original conversation references; [the recheck](CONVERSATION_RECHECK.md) preserves the exact unit/exception routes.

<a id="up-m02-adapt_cohort"></a>
#### M02.ADAPT_COHORT — Adaptive size cohorts

[Existing definition, target and P0–P7](experiments/M.md#m02-adapt_cohort) remain binding.

**Specific upgrade scope.** Compare train-frozen quantile buckets with smooth size weights and optional causal normalization by supported session/cohort scale.

**Local comparison.** Separate adaptive definition value from learner capacity, and report channel mass reconciliation and stability.

**Additional cases.** Future quantiles; sparse cohort; session distribution shift; unseen huge trade.

<a id="up-m02-fixed_cohort"></a>
#### M02.FIXED_COHORT — Source size cohorts

[Existing definition, target and P0–P7](experiments/M.md#m02-fixed_cohort) remain binding.

**Specific upgrade scope.** Retain each source fixed threshold and compare continuous overlapping size-basis channels around those boundaries.

**Local comparison.** Measure threshold sensitivity and path information at identical provider aggregation semantics; retain actual cohort volumes/OHLC.

**Additional cases.** Print at cutoff; 100 NY versus 75 London; changed reported trade summary.

<a id="up-m02-ohlc"></a>
#### M02.OHLC — True cohort CVD OHLC

[Existing definition, target and P0–P7](experiments/M.md#m02-ohlc) remain binding.

**Specific upgrade scope.** Extend true hard/soft cohort cumulative OHLC with extrema timing, order and path range relative to covered exposure.

**Local comparison.** Compare close-only, OHLC and ordered-extrema summaries under the same cohort definitions and downstream learner.

**Additional cases.** High before low versus low before high; opening baseline extreme; empty cohort; reset.

<a id="up-m03"></a>
### UP-M03 — Divergence and SMT measurement family

Parent: [M03](components/MEASUREMENTS.md); [local phases](experiments/M.md#m03); [definition refinement](SYSTEM_REFINEMENT.md#sr-m03). Upgrade role: `measurement`.

**Starting idea.** Flag a mismatch between price highs and CVD highs.

**Existing improvement path.** Explicit ordinary/hidden divergence, cohort SMT and asynchronous cross-market reference breaches.

**Remaining weakness.** Binary flags omit mismatch magnitude, confirmation delay, normal covariance and which stream moved first.

**Further upgrade.** Represent each source case by continuous standardized price/flow displacement, anchor age, breach order, lag and uncertainty. Add a train-fitted conditional residual/cross-lag basis and distinguish running-prefix from pivot-confirmed versions; preserve every source case as an independently scored comparator.

**Fair comparison.** Exact case flags, simple slopes, continuous discrepancy/order features and regularized temporal interactions.

**Evidence.** Case fidelity, delay-adjusted target loss, calibration by lag, redundancy and policy increment.

**Additional local cases to implement.** Small noisy miss versus large divergence; anchor revisions; one stream stale; identical endpoints with reversed order.

**Decision or system use.** Measure how and when streams disagree, allowing tests of whether the mismatch has useful future information.

**Exact reviewed source clauses.** [JTR-07](SOURCE_FINDINGS_AND_CONFLICTS.md:24), [JXA-23](SOURCE_FINDINGS_AND_CONFLICTS.md:122), [JFN-09](SOURCE_FINDINGS_AND_CONFLICTS.md:143), [CEX-07](SOURCE_FINDINGS_AND_CONFLICTS.md:189), [FP9-01](SOURCE_FINDINGS_AND_CONFLICTS.md:374), [FP9-02](SOURCE_FINDINGS_AND_CONFLICTS.md:375), [FP9-03](SOURCE_FINDINGS_AND_CONFLICTS.md:376), [FP9-04](SOURCE_FINDINGS_AND_CONFLICTS.md:377), [FP9-05](SOURCE_FINDINGS_AND_CONFLICTS.md:378), [FP9-06](SOURCE_FINDINGS_AND_CONFLICTS.md:379), [VW10-04](SOURCE_FINDINGS_AND_CONFLICTS.md:383), [CD1-04](SOURCE_FINDINGS_AND_CONFLICTS.md:397), [WIC-06](SOURCE_FINDINGS_AND_CONFLICTS.md:582), [YMA-01](SOURCE_FINDINGS_AND_CONFLICTS.md:589), [YMA-02](SOURCE_FINDINGS_AND_CONFLICTS.md:590), [YMA-03](SOURCE_FINDINGS_AND_CONFLICTS.md:591), [YMA-04](SOURCE_FINDINGS_AND_CONFLICTS.md:592), [YMA-05](SOURCE_FINDINGS_AND_CONFLICTS.md:593), [YMA-06](SOURCE_FINDINGS_AND_CONFLICTS.md:594), [K18-07](SOURCE_FINDINGS_AND_CONFLICTS.md:658), [F23-03](SOURCE_FINDINGS_AND_CONFLICTS.md:669), [ALS-01](SOURCE_FINDINGS_AND_CONFLICTS.md:696), [ALS-03](SOURCE_FINDINGS_AND_CONFLICTS.md:698), [NYA-01](SOURCE_FINDINGS_AND_CONFLICTS.md:709), [SRE-02](SOURCE_FINDINGS_AND_CONFLICTS.md:723), [SRE-05](SOURCE_FINDINGS_AND_CONFLICTS.md:726), [OBT-01](SOURCE_FINDINGS_AND_CONFLICTS.md:750), [OBT-06](SOURCE_FINDINGS_AND_CONFLICTS.md:755), [MVF-02](SOURCE_FINDINGS_AND_CONFLICTS.md:784), [OSF-07](SOURCE_FINDINGS_AND_CONFLICTS.md:801), [OSF-09](SOURCE_FINDINGS_AND_CONFLICTS.md:803), [PIN003-04](SOURCE_FINDINGS_AND_CONFLICTS.md:822), [PIN011-01](SOURCE_FINDINGS_AND_CONFLICTS.md:845), [PIN011-02](SOURCE_FINDINGS_AND_CONFLICTS.md:846), [PIN011-03](SOURCE_FINDINGS_AND_CONFLICTS.md:847), [PIN011-04](SOURCE_FINDINGS_AND_CONFLICTS.md:848), [PIN011-05](SOURCE_FINDINGS_AND_CONFLICTS.md:849), [PIN011-06](SOURCE_FINDINGS_AND_CONFLICTS.md:850), [PIN011-07](SOURCE_FINDINGS_AND_CONFLICTS.md:851), [PIN020-01](SOURCE_FINDINGS_AND_CONFLICTS.md:890), [PIN020-02](SOURCE_FINDINGS_AND_CONFLICTS.md:891), [PIN029-01](SOURCE_FINDINGS_AND_CONFLICTS.md:907), [PIN034-01](SOURCE_FINDINGS_AND_CONFLICTS.md:919), [PIN050-01](SOURCE_FINDINGS_AND_CONFLICTS.md:968), [PIN050-02](SOURCE_FINDINGS_AND_CONFLICTS.md:969), [PIN050-03](SOURCE_FINDINGS_AND_CONFLICTS.md:970), [PIN072-01](SOURCE_FINDINGS_AND_CONFLICTS.md:1045), [PIN072-02](SOURCE_FINDINGS_AND_CONFLICTS.md:1046), [PIN079-01](SOURCE_FINDINGS_AND_CONFLICTS.md:1066), [PIN079-02](SOURCE_FINDINGS_AND_CONFLICTS.md:1067), [PIN079-03](SOURCE_FINDINGS_AND_CONFLICTS.md:1068), [PIN079-04](SOURCE_FINDINGS_AND_CONFLICTS.md:1069).

<a id="up-m03-cohort_smt"></a>
#### M03.COHORT_SMT — Within-market inter-cohort SMT

[Existing definition, target and P0–P7](experiments/M.md#m03-cohort_smt) remain binding.

**Specific upgrade scope.** Add scale-normalized inter-cohort discrepancy magnitude and causal lead-lag among exact cohort paths.

**Local comparison.** Compare fixed/adaptive/smooth cohort SMT and all-flow baseline under common print definitions.

**Additional cases.** Small empty cohort; aggregate same sign with opposing cohorts; one print belongs to soft channels.

<a id="up-m03-price_cvd"></a>
#### M03.PRICE_CVD — Distinct price/CVD divergence cases

[Existing definition, target and P0–P7](experiments/M.md#m03-price_cvd) remain binding.

**Specific upgrade scope.** Represent each ordinary/hidden price-CVD case with continuous mismatch, anchor age, confirmation cost and direction of innovation.

**Local comparison.** Compare exact flags, slopes and residual lag interactions separately for every source case.

**Additional cases.** Running versus confirmed extrema; tiny noisy mismatch; same endpoints reversed order.

<a id="up-m04"></a>
### UP-M04 — Trade-at-price volume profiles and value geometry

Parent: [M04](components/MEASUREMENTS.md); [local phases](experiments/M.md#m04); [definition refinement](SYSTEM_REFINEMENT.md#sr-m04). Upgrade role: `measurement`.

**Starting idea.** Build a histogram and use its POC/value-area lines.

**Existing improvement path.** Exact trade profiles, source anchors, side-independent topology and multiscale/KDE alternatives.

**Remaining weakness.** A few landmarks hide broad shape, changing modes, unstable grid phase and whether new mass is unusual for formation progress.

**Further upgrade.** Add frozen-grid multiresolution mass functions with explicit overflow, mode/plateau sets, prominence/persistence across smoothing scales and cumulative mass transport. Decompose changes into newly traded mass versus normalization/representation changes; estimate expected developing profiles by elapsed formation/activity and export residual shape. Future profile evolution is a separately fitted C08/L16 consumer target.

**Fair comparison.** POC/VA, raw histogram moments, multiscale topology/transport, expected-profile residuals and optional compact functional encoder.

**Evidence.** Mass conservation, grid/scale stability, shape-target information, location/role value and computational cost.

**Additional local cases to implement.** POC ties; multimodal valley center; changing row width; growing profile changes normalized mass; future-grid leakage.

**Decision or system use.** Supply the whole auction shape and its meaningful development, enabling later prediction of mass redistribution and useful locations.

**Exact reviewed source clauses.** [JTR-21](SOURCE_FINDINGS_AND_CONFLICTS.md:38), [JTR-22](SOURCE_FINDINGS_AND_CONFLICTS.md:39), [DTM-A11](SOURCE_FINDINGS_AND_CONFLICTS.md:69), [JXA-09](SOURCE_FINDINGS_AND_CONFLICTS.md:108), [JXA-15](SOURCE_FINDINGS_AND_CONFLICTS.md:114), [JXA-16](SOURCE_FINDINGS_AND_CONFLICTS.md:115), [JFN-08](SOURCE_FINDINGS_AND_CONFLICTS.md:142), [JCV-U01](SOURCE_FINDINGS_AND_CONFLICTS.md:154), [CRL-01](SOURCE_FINDINGS_AND_CONFLICTS.md:217), [CRL-06](SOURCE_FINDINGS_AND_CONFLICTS.md:222), [AM1-01](SOURCE_FINDINGS_AND_CONFLICTS.md:281), [AM1-02](SOURCE_FINDINGS_AND_CONFLICTS.md:282), [AM1-03](SOURCE_FINDINGS_AND_CONFLICTS.md:283), [AM1-04](SOURCE_FINDINGS_AND_CONFLICTS.md:284), [AM1-05](SOURCE_FINDINGS_AND_CONFLICTS.md:285), [AM1-06](SOURCE_FINDINGS_AND_CONFLICTS.md:286), [AM1-07](SOURCE_FINDINGS_AND_CONFLICTS.md:287), [AM1-08](SOURCE_FINDINGS_AND_CONFLICTS.md:288), [AM1-09](SOURCE_FINDINGS_AND_CONFLICTS.md:289), [AM1-10](SOURCE_FINDINGS_AND_CONFLICTS.md:290), [VP2-01](SOURCE_FINDINGS_AND_CONFLICTS.md:298), [VP2-02](SOURCE_FINDINGS_AND_CONFLICTS.md:299), [VP2-03](SOURCE_FINDINGS_AND_CONFLICTS.md:300), [VP2-04](SOURCE_FINDINGS_AND_CONFLICTS.md:301), [VP2-05](SOURCE_FINDINGS_AND_CONFLICTS.md:302), [FP8-05](SOURCE_FINDINGS_AND_CONFLICTS.md:373), [CD3-05](SOURCE_FINDINGS_AND_CONFLICTS.md:408), [MAV-01](SOURCE_FINDINGS_AND_CONFLICTS.md:505), [MAV-02](SOURCE_FINDINGS_AND_CONFLICTS.md:506), [MAV-03](SOURCE_FINDINGS_AND_CONFLICTS.md:507), [MAV-04](SOURCE_FINDINGS_AND_CONFLICTS.md:508), [MAV-05](SOURCE_FINDINGS_AND_CONFLICTS.md:509), [MAV-06](SOURCE_FINDINGS_AND_CONFLICTS.md:510), [MAV-07](SOURCE_FINDINGS_AND_CONFLICTS.md:511), [MAV-08](SOURCE_FINDINGS_AND_CONFLICTS.md:512), [MAV-09](SOURCE_FINDINGS_AND_CONFLICTS.md:513), [MAV-10](SOURCE_FINDINGS_AND_CONFLICTS.md:514), [MAV-11](SOURCE_FINDINGS_AND_CONFLICTS.md:515), [MAV-12](SOURCE_FINDINGS_AND_CONFLICTS.md:516), [MAV-13](SOURCE_FINDINGS_AND_CONFLICTS.md:517), [MAV-14](SOURCE_FINDINGS_AND_CONFLICTS.md:518), [MAT-01](SOURCE_FINDINGS_AND_CONFLICTS.md:526), [MAT-02](SOURCE_FINDINGS_AND_CONFLICTS.md:527), [MAT-03](SOURCE_FINDINGS_AND_CONFLICTS.md:528), [MAT-04](SOURCE_FINDINGS_AND_CONFLICTS.md:529), [MAT-05](SOURCE_FINDINGS_AND_CONFLICTS.md:530), [MAT-06](SOURCE_FINDINGS_AND_CONFLICTS.md:531), [MAT-07](SOURCE_FINDINGS_AND_CONFLICTS.md:532), [MAT-08](SOURCE_FINDINGS_AND_CONFLICTS.md:533), [MAT-09](SOURCE_FINDINGS_AND_CONFLICTS.md:534), [RVP-01](SOURCE_FINDINGS_AND_CONFLICTS.md:542), [RVP-02](SOURCE_FINDINGS_AND_CONFLICTS.md:543), [RVP-03](SOURCE_FINDINGS_AND_CONFLICTS.md:544), [RVP-04](SOURCE_FINDINGS_AND_CONFLICTS.md:545), [RVP-05](SOURCE_FINDINGS_AND_CONFLICTS.md:546), [RVP-06](SOURCE_FINDINGS_AND_CONFLICTS.md:547), [RVP-07](SOURCE_FINDINGS_AND_CONFLICTS.md:548), [RVP-08](SOURCE_FINDINGS_AND_CONFLICTS.md:549), [YMA-03](SOURCE_FINDINGS_AND_CONFLICTS.md:591), [K10-01](SOURCE_FINDINGS_AND_CONFLICTS.md:639), [K10-02](SOURCE_FINDINGS_AND_CONFLICTS.md:640), [K10-03](SOURCE_FINDINGS_AND_CONFLICTS.md:641), [K10-04](SOURCE_FINDINGS_AND_CONFLICTS.md:642), [K10-05](SOURCE_FINDINGS_AND_CONFLICTS.md:643), [K10-06](SOURCE_FINDINGS_AND_CONFLICTS.md:644), [K18-02](SOURCE_FINDINGS_AND_CONFLICTS.md:653), [CCS-01](SOURCE_FINDINGS_AND_CONFLICTS.md:681), [CCS-02](SOURCE_FINDINGS_AND_CONFLICTS.md:682), [CCS-03](SOURCE_FINDINGS_AND_CONFLICTS.md:683), [CCS-04](SOURCE_FINDINGS_AND_CONFLICTS.md:684), [CCS-05](SOURCE_FINDINGS_AND_CONFLICTS.md:685), [CCS-06](SOURCE_FINDINGS_AND_CONFLICTS.md:686), [CCS-07](SOURCE_FINDINGS_AND_CONFLICTS.md:687), [CCS-08](SOURCE_FINDINGS_AND_CONFLICTS.md:688), [OBT-04](SOURCE_FINDINGS_AND_CONFLICTS.md:753), [OBT-05](SOURCE_FINDINGS_AND_CONFLICTS.md:754), [MVF-01](SOURCE_FINDINGS_AND_CONFLICTS.md:783), [MVF-02](SOURCE_FINDINGS_AND_CONFLICTS.md:784), [MVF-03](SOURCE_FINDINGS_AND_CONFLICTS.md:785), [MVF-04](SOURCE_FINDINGS_AND_CONFLICTS.md:786), [MVF-05](SOURCE_FINDINGS_AND_CONFLICTS.md:787), [MVF-06](SOURCE_FINDINGS_AND_CONFLICTS.md:788), [MVF-07](SOURCE_FINDINGS_AND_CONFLICTS.md:789), [PIN066-01](SOURCE_FINDINGS_AND_CONFLICTS.md:1016), [PIN066-02](SOURCE_FINDINGS_AND_CONFLICTS.md:1017), [PIN066-03](SOURCE_FINDINGS_AND_CONFLICTS.md:1018), [PIN066-04](SOURCE_FINDINGS_AND_CONFLICTS.md:1019), [PIN077-01](SOURCE_FINDINGS_AND_CONFLICTS.md:1060), [PIN077-02](SOURCE_FINDINGS_AND_CONFLICTS.md:1061).

**Conversation upgrade lineage.** [DTM-A11](SOURCE_FINDINGS_AND_CONFLICTS.md:69), [JCV-U01](SOURCE_FINDINGS_AND_CONFLICTS.md:154), [JCV-A01](SOURCE_FINDINGS_AND_CONFLICTS.md:160), [CEX-05](SOURCE_FINDINGS_AND_CONFLICTS.md:187), [CRL-01](SOURCE_FINDINGS_AND_CONFLICTS.md:217), [CRL-06](SOURCE_FINDINGS_AND_CONFLICTS.md:222), [CRL-11](SOURCE_FINDINGS_AND_CONFLICTS.md:227), [CRL-18](SOURCE_FINDINGS_AND_CONFLICTS.md:234). Read the full rows and their original conversation references; [the recheck](CONVERSATION_RECHECK.md) preserves the exact unit/exception routes.

<a id="up-m04-anchors"></a>
#### M04.ANCHORS — Profile anchor family

[Existing definition, target and P0–P7](experiments/M.md#m04-anchors) remain binding.

**Specific upgrade scope.** Apply frozen-grid profile functions and expected-maturity residuals to every source session/event/rolling/composite anchor.

**Local comparison.** Compare each anchor and relation features without picking the best historical window after outcomes; match formation exposure.

**Additional cases.** Partial anchor; overlap reuses trades; event anchor unavailable earlier; roll.

<a id="up-m04-proxy"></a>
#### M04.PROXY — True volume versus OHLC allocation

[Existing definition, target and P0–P7](experiments/M.md#m04-proxy) remain binding.

**Specific upgrade scope.** Treat true trade profiles and every OHLC allocation proxy as distinct information views before applying identical improved geometry.

**Local comparison.** Hold geometry/learner fixed for data-fidelity comparisons, then hold data fixed for representation comparisons.

**Additional cases.** Same bar OHLC/volume with different trade distribution; side allocation uncertain; sparse exact tape.

<a id="up-m04-topology"></a>
#### M04.TOPOLOGY — Profile shape and stable nodes

[Existing definition, target and P0–P7](experiments/M.md#m04-topology) remain binding.

**Specific upgrade scope.** Add plateau/mode sets, smoothing-scale persistence, mass transport and new-mass decomposition to all profile landmarks.

**Local comparison.** Compare POC/VA, raw topology and stable functional features at equal node count/width where used as locations.

**Additional cases.** Near-tie modes; grid phase; new mass outside grid; mass normalization changes without relocated trades.

<a id="up-m05"></a>
### UP-M05 — Delta profiles and side-separated auction geometry

Parent: [M05](components/MEASUREMENTS.md); [local phases](experiments/M.md#m05); [definition refinement](SYSTEM_REFINEMENT.md#sr-m05). Upgrade role: `measurement`.

**Starting idea.** Use positive or negative delta peaks as levels.

**Existing improvement path.** Buy/sell/unknown profiles, signed difference, side distributions and cohort channels.

**Remaining weakness.** Net delta cancels heavy two-sided activity, while a high ratio from tiny volume can look stronger than a well-supported shelf.

**Further upgrade.** Add joint side intensity and shrunken contrast fields, side-distribution overlap/separation, cumulative imbalance and price-local unknown-sign envelopes. Use a common nonnegative mass basis before differences; keep magnitude, breadth and uncertainty separate and align updates with M04's frozen geometry.

**Fair comparison.** Total profile, net delta, raw side ratios, shrunken multichannel geometry and optional structured encoder.

**Evidence.** Side/total reconciliation, sparse-cell stability, uncertainty sensitivity, role/path loss and incremental net.

**Additional local cases to implement.** Large buy and sell shelf cancel in net; tiny denominator; unknown volume dominates one row; cohort mix shifts.

**Decision or system use.** Distinguish concentrated directional pressure from intense two-sided trade and unsupported extremes.

**Exact reviewed source clauses.** [JTR-21](SOURCE_FINDINGS_AND_CONFLICTS.md:38), [JTR-22](SOURCE_FINDINGS_AND_CONFLICTS.md:39), [DTM-A11](SOURCE_FINDINGS_AND_CONFLICTS.md:69), [JXA-09](SOURCE_FINDINGS_AND_CONFLICTS.md:108), [JXA-15](SOURCE_FINDINGS_AND_CONFLICTS.md:114), [JXA-16](SOURCE_FINDINGS_AND_CONFLICTS.md:115), [JFN-08](SOURCE_FINDINGS_AND_CONFLICTS.md:142), [JCV-U01](SOURCE_FINDINGS_AND_CONFLICTS.md:154), [JCV-A01](SOURCE_FINDINGS_AND_CONFLICTS.md:160), [CRL-01](SOURCE_FINDINGS_AND_CONFLICTS.md:217), [CRL-06](SOURCE_FINDINGS_AND_CONFLICTS.md:222), [CRL-13](SOURCE_FINDINGS_AND_CONFLICTS.md:229), [RDL-01](SOURCE_FINDINGS_AND_CONFLICTS.md:550), [RDL-02](SOURCE_FINDINGS_AND_CONFLICTS.md:551), [RDL-03](SOURCE_FINDINGS_AND_CONFLICTS.md:552), [RDL-04](SOURCE_FINDINGS_AND_CONFLICTS.md:553), [RDL-05](SOURCE_FINDINGS_AND_CONFLICTS.md:554), [RDL-06](SOURCE_FINDINGS_AND_CONFLICTS.md:555), [RDL-07](SOURCE_FINDINGS_AND_CONFLICTS.md:556), [YMA-03](SOURCE_FINDINGS_AND_CONFLICTS.md:591), [K18-01](SOURCE_FINDINGS_AND_CONFLICTS.md:652), [K18-02](SOURCE_FINDINGS_AND_CONFLICTS.md:653), [K18-03](SOURCE_FINDINGS_AND_CONFLICTS.md:654), [K18-04](SOURCE_FINDINGS_AND_CONFLICTS.md:655), [K18-05](SOURCE_FINDINGS_AND_CONFLICTS.md:656), [K18-06](SOURCE_FINDINGS_AND_CONFLICTS.md:657), [K18-07](SOURCE_FINDINGS_AND_CONFLICTS.md:658), [K18-08](SOURCE_FINDINGS_AND_CONFLICTS.md:659), [CCS-03](SOURCE_FINDINGS_AND_CONFLICTS.md:683), [TBR-01](SOURCE_FINDINGS_AND_CONFLICTS.md:736), [TBR-02](SOURCE_FINDINGS_AND_CONFLICTS.md:737), [TBR-03](SOURCE_FINDINGS_AND_CONFLICTS.md:738), [TBR-04](SOURCE_FINDINGS_AND_CONFLICTS.md:739), [TBR-05](SOURCE_FINDINGS_AND_CONFLICTS.md:740), [TBR-06](SOURCE_FINDINGS_AND_CONFLICTS.md:741), [TBR-07](SOURCE_FINDINGS_AND_CONFLICTS.md:742), [MVF-01](SOURCE_FINDINGS_AND_CONFLICTS.md:783), [MVF-02](SOURCE_FINDINGS_AND_CONFLICTS.md:784), [MVF-03](SOURCE_FINDINGS_AND_CONFLICTS.md:785), [MVF-04](SOURCE_FINDINGS_AND_CONFLICTS.md:786), [MVF-05](SOURCE_FINDINGS_AND_CONFLICTS.md:787), [MVF-06](SOURCE_FINDINGS_AND_CONFLICTS.md:788), [MVF-07](SOURCE_FINDINGS_AND_CONFLICTS.md:789), [PIN066-01](SOURCE_FINDINGS_AND_CONFLICTS.md:1016), [PIN066-02](SOURCE_FINDINGS_AND_CONFLICTS.md:1017), [PIN066-03](SOURCE_FINDINGS_AND_CONFLICTS.md:1018), [PIN066-04](SOURCE_FINDINGS_AND_CONFLICTS.md:1019), [PIN077-01](SOURCE_FINDINGS_AND_CONFLICTS.md:1060), [PIN077-02](SOURCE_FINDINGS_AND_CONFLICTS.md:1061).

**Conversation upgrade lineage.** [DTM-A11](SOURCE_FINDINGS_AND_CONFLICTS.md:69), [JCV-U01](SOURCE_FINDINGS_AND_CONFLICTS.md:154), [JCV-A01](SOURCE_FINDINGS_AND_CONFLICTS.md:160), [CRL-01](SOURCE_FINDINGS_AND_CONFLICTS.md:217), [CRL-06](SOURCE_FINDINGS_AND_CONFLICTS.md:222), [CRL-11](SOURCE_FINDINGS_AND_CONFLICTS.md:227), [CRL-14](SOURCE_FINDINGS_AND_CONFLICTS.md:230), [CRL-18](SOURCE_FINDINGS_AND_CONFLICTS.md:234). Read the full rows and their original conversation references; [the recheck](CONVERSATION_RECHECK.md) preserves the exact unit/exception routes.

<a id="up-m05-side_topology"></a>
#### M05.SIDE_TOPOLOGY — Separate buy/sell/delta profiles

[Existing definition, target and P0–P7](experiments/M.md#m05-side_topology) remain binding.

**Specific upgrade scope.** Add shrunken side contrast/intensity, distribution overlap and unknown-sign envelopes without cancelling opposing supported shelves.

**Local comparison.** Compare total, net, buy/sell and cohort profile geometry under matched grid/support.

**Additional cases.** High two-sided volume zero net; tiny denominator; unknown mass changes dominant side.

<a id="up-m06"></a>
### UP-M06 — TPO and time-at-price auction measurements

Parent: [M06](components/MEASUREMENTS.md); [local phases](experiments/M.md#m06); [definition refinement](SYSTEM_REFINEMENT.md#sr-m06). Upgrade role: `measurement`.

**Starting idea.** Count TPO letters or estimate time spent in a price row.

**Existing improvement path.** Distinct bracket visits, exact observed visits, bounded dwell estimates and source auction geometry.

**Remaining weakness.** Equal TPO counts can arise from contiguous acceptance, scattered returns or one brief touch per bracket.

**Further upgrade.** Add causal occupancy/run-length and return-visit geometry: contiguous bracket support, first/last visit age, revisit gaps, observed dwell bounds and repair of sparse regions. Normalize against available bracket/time exposure without treating imputed dwell as observed; preserve daily/weekly IB and provisional/completed states.

**Fair comparison.** Source TPO, exact visits, dwell, occupancy continuity and multiscale revisit summaries.

**Evidence.** Bracket/dwell fidelity, boundary stability, incremental auction/role loss and location value.

**Additional local cases to implement.** Same counts with different visit order; sparse quotes; bracket in progress; overnight gap; missing interval.

**Decision or system use.** Describe how acceptance formed over time, beyond how many brackets touched a row.

**Exact reviewed source clauses.** [JXA-05](SOURCE_FINDINGS_AND_CONFLICTS.md:104), [AM1-01](SOURCE_FINDINGS_AND_CONFLICTS.md:281), [AM1-02](SOURCE_FINDINGS_AND_CONFLICTS.md:282), [AM1-03](SOURCE_FINDINGS_AND_CONFLICTS.md:283), [AM1-04](SOURCE_FINDINGS_AND_CONFLICTS.md:284), [AM1-05](SOURCE_FINDINGS_AND_CONFLICTS.md:285), [AM1-06](SOURCE_FINDINGS_AND_CONFLICTS.md:286), [AM1-07](SOURCE_FINDINGS_AND_CONFLICTS.md:287), [AM1-08](SOURCE_FINDINGS_AND_CONFLICTS.md:288), [AM1-09](SOURCE_FINDINGS_AND_CONFLICTS.md:289), [AM1-10](SOURCE_FINDINGS_AND_CONFLICTS.md:290), [TP3-01](SOURCE_FINDINGS_AND_CONFLICTS.md:310), [TP3-02](SOURCE_FINDINGS_AND_CONFLICTS.md:311), [TP3-03](SOURCE_FINDINGS_AND_CONFLICTS.md:312), [TP3-04](SOURCE_FINDINGS_AND_CONFLICTS.md:313), [TP3-05](SOURCE_FINDINGS_AND_CONFLICTS.md:314), [TP3-06](SOURCE_FINDINGS_AND_CONFLICTS.md:315), [TP3-07](SOURCE_FINDINGS_AND_CONFLICTS.md:316), [CD1-03](SOURCE_FINDINGS_AND_CONFLICTS.md:396), [MAV-01](SOURCE_FINDINGS_AND_CONFLICTS.md:505), [MAV-02](SOURCE_FINDINGS_AND_CONFLICTS.md:506), [MAV-03](SOURCE_FINDINGS_AND_CONFLICTS.md:507), [MAV-04](SOURCE_FINDINGS_AND_CONFLICTS.md:508), [MAV-05](SOURCE_FINDINGS_AND_CONFLICTS.md:509), [MAV-06](SOURCE_FINDINGS_AND_CONFLICTS.md:510), [MAV-07](SOURCE_FINDINGS_AND_CONFLICTS.md:511), [MAV-08](SOURCE_FINDINGS_AND_CONFLICTS.md:512), [MAV-09](SOURCE_FINDINGS_AND_CONFLICTS.md:513), [MAV-10](SOURCE_FINDINGS_AND_CONFLICTS.md:514), [MAV-11](SOURCE_FINDINGS_AND_CONFLICTS.md:515), [MAV-12](SOURCE_FINDINGS_AND_CONFLICTS.md:516), [MAV-13](SOURCE_FINDINGS_AND_CONFLICTS.md:517), [MAV-14](SOURCE_FINDINGS_AND_CONFLICTS.md:518), [AUT-06](SOURCE_FINDINGS_AND_CONFLICTS.md:772), [PIN026-01](SOURCE_FINDINGS_AND_CONFLICTS.md:900), [PIN026-02](SOURCE_FINDINGS_AND_CONFLICTS.md:901), [PIN027-01](SOURCE_FINDINGS_AND_CONFLICTS.md:902), [PIN027-02](SOURCE_FINDINGS_AND_CONFLICTS.md:903), [PIN028-01](SOURCE_FINDINGS_AND_CONFLICTS.md:904), [PIN028-02](SOURCE_FINDINGS_AND_CONFLICTS.md:905), [PIN028-03](SOURCE_FINDINGS_AND_CONFLICTS.md:906), [PIN029-01](SOURCE_FINDINGS_AND_CONFLICTS.md:907), [PIN029-02](SOURCE_FINDINGS_AND_CONFLICTS.md:908), [PIN029-03](SOURCE_FINDINGS_AND_CONFLICTS.md:909), [PIN030-01](SOURCE_FINDINGS_AND_CONFLICTS.md:910), [PIN030-02](SOURCE_FINDINGS_AND_CONFLICTS.md:911), [PIN030-03](SOURCE_FINDINGS_AND_CONFLICTS.md:912), [PIN043-01](SOURCE_FINDINGS_AND_CONFLICTS.md:944), [PIN048-01](SOURCE_FINDINGS_AND_CONFLICTS.md:960), [PIN048-02](SOURCE_FINDINGS_AND_CONFLICTS.md:961), [PIN048-03](SOURCE_FINDINGS_AND_CONFLICTS.md:962), [PIN058-01](SOURCE_FINDINGS_AND_CONFLICTS.md:989), [PIN059-01](SOURCE_FINDINGS_AND_CONFLICTS.md:990), [PIN059-02](SOURCE_FINDINGS_AND_CONFLICTS.md:991), [PIN078-01](SOURCE_FINDINGS_AND_CONFLICTS.md:1063), [PIN078-02](SOURCE_FINDINGS_AND_CONFLICTS.md:1064).

<a id="up-m06-dwell"></a>
#### M06.DWELL — TPO versus actual dwell

[Existing definition, target and P0–P7](experiments/M.md#m06-dwell) remain binding.

**Specific upgrade scope.** Add bracket continuity, revisit gaps and bounded dwell/repair trajectories while retaining distinct TPO versus time semantics.

**Local comparison.** Compare source bracket counts, exact visits, dwell and temporal occupancy summaries on equivalent available intervals.

**Additional cases.** Brief visits versus sustained stay; missing quote interval; unfinished bracket; interpolation cap.

<a id="up-m07"></a>
### UP-M07 — Price VWAP, anchored VWAP and dispersion

Parent: [M07](components/MEASUREMENTS.md); [local phases](experiments/M.md#m07); [definition refinement](SYSTEM_REFINEMENT.md#sr-m07). Upgrade role: `measurement`.

**Starting idea.** Use VWAP and fixed standard-deviation bands.

**Existing improvement path.** Exact traded VWAP, anchor variants, stable moments and robust/quantile alternatives.

**Remaining weakness.** A mean can sit between modes, and differences among anchors can be difficult to interpret or select consistently.

**Further upgrade.** Maintain weighted empirical quantiles and robust central bands alongside VWAP, plus deterministic decomposition of anchor-to-anchor differences into included volume and price contributions. Export relative positions, band asymmetry and convergence/divergence of supported anchors; downstream anchor selection uses only causal context and fixed comparisons.

**Fair comparison.** Exact/bar VWAP, SD/percentage bands, weighted quantile/robust bands and multi-anchor geometry.

**Evidence.** Moment/quantile fidelity, outlier sensitivity, anchor stability, reclaim/continuation loss and net role increment.

**Additional local cases to implement.** One extreme print; bimodal mass; low-volume anchor; rolling downdate; new event anchor resembles an old one.

**Decision or system use.** Preserve the reference mean while providing robust distribution shape and interpretable multi-anchor context.

**Exact reviewed source clauses.** [DTM-A11](SOURCE_FINDINGS_AND_CONFLICTS.md:69), [CEX-21](SOURCE_FINDINGS_AND_CONFLICTS.md:203), [CRL-06](SOURCE_FINDINGS_AND_CONFLICTS.md:222), [VP2-05](SOURCE_FINDINGS_AND_CONFLICTS.md:302), [FP8-05](SOURCE_FINDINGS_AND_CONFLICTS.md:373), [VW10-01](SOURCE_FINDINGS_AND_CONFLICTS.md:380), [VW10-02](SOURCE_FINDINGS_AND_CONFLICTS.md:381), [VW10-03](SOURCE_FINDINGS_AND_CONFLICTS.md:382), [VW10-04](SOURCE_FINDINGS_AND_CONFLICTS.md:383), [VW10-05](SOURCE_FINDINGS_AND_CONFLICTS.md:384), [VW10-06](SOURCE_FINDINGS_AND_CONFLICTS.md:385), [VW10-07](SOURCE_FINDINGS_AND_CONFLICTS.md:386), [OBT-04](SOURCE_FINDINGS_AND_CONFLICTS.md:753), [PIN069-01](SOURCE_FINDINGS_AND_CONFLICTS.md:1028), [PIN069-02](SOURCE_FINDINGS_AND_CONFLICTS.md:1029), [PIN069-03](SOURCE_FINDINGS_AND_CONFLICTS.md:1030), [PIN069-04](SOURCE_FINDINGS_AND_CONFLICTS.md:1031).

**Conversation upgrade lineage.** [CEX-21](SOURCE_FINDINGS_AND_CONFLICTS.md:203), [CRL-06](SOURCE_FINDINGS_AND_CONFLICTS.md:222). Read the full rows and their original conversation references; [the recheck](CONVERSATION_RECHECK.md) preserves the exact unit/exception routes.

<a id="up-m07-robust_bands"></a>
#### M07.ROBUST_BANDS — VWAP dispersion alternatives

[Existing definition, target and P0–P7](experiments/M.md#m07-robust_bands) remain binding.

**Specific upgrade scope.** Maintain weighted quantiles/asymmetry and anchor-contribution decomposition alongside exact VWAP/SD/percentage variants.

**Local comparison.** Compare outlier/anchor stability and conditional role value with matched band widths and target policies.

**Additional cases.** Bimodal mass; extreme print; rolling downdate; low-volume anchor.

<a id="up-m08"></a>
### UP-M08 — Causal swings, structure and retracement anchors

Parent: [M08](components/MEASUREMENTS.md); [local phases](experiments/M.md#m08); [definition refinement](SYSTEM_REFINEMENT.md#sr-m08). Upgrade role: `measurement`.

**Starting idea.** Choose a fixed pivot lookback or Fibonacci swing.

**Existing improvement path.** Confirmed versus provisional pivots, fixed/volatility directional changes and exact retracement identities.

**Remaining weakness.** Each scale duplicates some extrema and introduces a different confirmation delay; a single chosen scale hides this tradeoff.

**Further upgrade.** Build a causal multiscale swing tree with parent-leg relationships, confirmation delay, prominence and persistence across registered thresholds. Preserve threshold values at leg birth, record split/merge revisions forward, and compare compact tree summaries with one-scale swings under matched delay budgets.

**Fair comparison.** Each source pivot/reversal rule, single-scale baseline and multiscale persistence/leg-tree representation.

**Evidence.** Prefix parity, anchor stability, confirmation-cost-adjusted target loss, location utility and state size.

**Additional local cases to implement.** Nested swings; threshold changes without price reversal; simultaneous confirmations; equal extrema; provisional leg extends.

**Decision or system use.** Expose stable structure and scale relationships while pricing the information delay required to know them.

**Exact reviewed source clauses.** [JXA-16](SOURCE_FINDINGS_AND_CONFLICTS.md:115), [JXA-20](SOURCE_FINDINGS_AND_CONFLICTS.md:119), [JXA-26](SOURCE_FINDINGS_AND_CONFLICTS.md:125), [CRL-06](SOURCE_FINDINGS_AND_CONFLICTS.md:222), [OSF-01](SOURCE_FINDINGS_AND_CONFLICTS.md:795), [OSF-02](SOURCE_FINDINGS_AND_CONFLICTS.md:796), [OSF-03](SOURCE_FINDINGS_AND_CONFLICTS.md:797), [OSF-04](SOURCE_FINDINGS_AND_CONFLICTS.md:798), [OSF-05](SOURCE_FINDINGS_AND_CONFLICTS.md:799), [OSF-06](SOURCE_FINDINGS_AND_CONFLICTS.md:800), [OSF-07](SOURCE_FINDINGS_AND_CONFLICTS.md:801), [OSF-08](SOURCE_FINDINGS_AND_CONFLICTS.md:802), [OSF-09](SOURCE_FINDINGS_AND_CONFLICTS.md:803), [OSF-10](SOURCE_FINDINGS_AND_CONFLICTS.md:804), [PIN005-02](SOURCE_FINDINGS_AND_CONFLICTS.md:829), [PIN005-03](SOURCE_FINDINGS_AND_CONFLICTS.md:830), [PIN005-04](SOURCE_FINDINGS_AND_CONFLICTS.md:831), [PIN005-05](SOURCE_FINDINGS_AND_CONFLICTS.md:832), [PIN010-01](SOURCE_FINDINGS_AND_CONFLICTS.md:841), [PIN010-02](SOURCE_FINDINGS_AND_CONFLICTS.md:842), [PIN010-03](SOURCE_FINDINGS_AND_CONFLICTS.md:843), [PIN010-04](SOURCE_FINDINGS_AND_CONFLICTS.md:844), [PIN019-01](SOURCE_FINDINGS_AND_CONFLICTS.md:887), [PIN019-02](SOURCE_FINDINGS_AND_CONFLICTS.md:888), [PIN019-03](SOURCE_FINDINGS_AND_CONFLICTS.md:889), [PIN022-01](SOURCE_FINDINGS_AND_CONFLICTS.md:894), [PIN022-02](SOURCE_FINDINGS_AND_CONFLICTS.md:895), [PIN022-03](SOURCE_FINDINGS_AND_CONFLICTS.md:896), [PIN023-01](SOURCE_FINDINGS_AND_CONFLICTS.md:897), [PIN023-02](SOURCE_FINDINGS_AND_CONFLICTS.md:898), [PIN031-01](SOURCE_FINDINGS_AND_CONFLICTS.md:913), [PIN032-01](SOURCE_FINDINGS_AND_CONFLICTS.md:914), [PIN032-02](SOURCE_FINDINGS_AND_CONFLICTS.md:915), [PIN032-03](SOURCE_FINDINGS_AND_CONFLICTS.md:916), [PIN035-01](SOURCE_FINDINGS_AND_CONFLICTS.md:920), [PIN035-02](SOURCE_FINDINGS_AND_CONFLICTS.md:921), [PIN035-03](SOURCE_FINDINGS_AND_CONFLICTS.md:922), [PIN035-04](SOURCE_FINDINGS_AND_CONFLICTS.md:923), [PIN036-01](SOURCE_FINDINGS_AND_CONFLICTS.md:925), [PIN036-02](SOURCE_FINDINGS_AND_CONFLICTS.md:926), [PIN037-01](SOURCE_FINDINGS_AND_CONFLICTS.md:927), [PIN037-02](SOURCE_FINDINGS_AND_CONFLICTS.md:928), [PIN038-01](SOURCE_FINDINGS_AND_CONFLICTS.md:930), [PIN038-02](SOURCE_FINDINGS_AND_CONFLICTS.md:931), [PIN051-01](SOURCE_FINDINGS_AND_CONFLICTS.md:971), [PIN051-02](SOURCE_FINDINGS_AND_CONFLICTS.md:972), [PIN056-01](SOURCE_FINDINGS_AND_CONFLICTS.md:983), [PIN056-02](SOURCE_FINDINGS_AND_CONFLICTS.md:984), [PIN060-01](SOURCE_FINDINGS_AND_CONFLICTS.md:993), [PIN060-02](SOURCE_FINDINGS_AND_CONFLICTS.md:994), [PIN060-03](SOURCE_FINDINGS_AND_CONFLICTS.md:995), [PIN071-01](SOURCE_FINDINGS_AND_CONFLICTS.md:1036), [PIN071-02](SOURCE_FINDINGS_AND_CONFLICTS.md:1037), [PIN071-03](SOURCE_FINDINGS_AND_CONFLICTS.md:1038), [PIN071-04](SOURCE_FINDINGS_AND_CONFLICTS.md:1039), [PIN071-05](SOURCE_FINDINGS_AND_CONFLICTS.md:1040), [PIN071-06](SOURCE_FINDINGS_AND_CONFLICTS.md:1041), [PIN071-07](SOURCE_FINDINGS_AND_CONFLICTS.md:1042), [PIN071-08](SOURCE_FINDINGS_AND_CONFLICTS.md:1043).

**Conversation upgrade lineage.** [CEX-07](SOURCE_FINDINGS_AND_CONFLICTS.md:189), [CRL-04](SOURCE_FINDINGS_AND_CONFLICTS.md:220), [CRL-06](SOURCE_FINDINGS_AND_CONFLICTS.md:222). Read the full rows and their original conversation references; [the recheck](CONVERSATION_RECHECK.md) preserves the exact unit/exception routes.

<a id="up-m08-multiscale"></a>
#### M08.MULTISCALE — Causal swing and leg alternatives

[Existing definition, target and P0–P7](experiments/M.md#m08-multiscale) remain binding.

**Specific upgrade scope.** Build the causal nested swing/leg tree with prominence, persistence and recorded confirmation delay across every source threshold family.

**Local comparison.** Compare one-scale and tree summaries under equal information delay and bounded candidate count.

**Additional cases.** Threshold frozen at leg birth; nested equal extrema; delayed pivot; moving provisional leg.

<a id="up-m09"></a>
### UP-M09 — Best-quote OFI, imbalance and replenishment proxies

Parent: [M09](components/MEASUREMENTS.md); [local phases](experiments/M.md#m09); [definition refinement](SYSTEM_REFINEMENT.md#sr-m09). Upgrade role: `measurement`.

**Starting idea.** Use top-book imbalance or a rolling OFI number.

**Existing improvement path.** Exact MBP-derived OFI, microprice, trade/book channels and bounded net recovery.

**Remaining weakness.** Static imbalance loses pressure persistence and trade/quote interaction; raw OFI scale changes with displayed depth and activity.

**Further upgrade.** Add event-exposure-normalized pressure, distributed-lag OFI/trade interactions, imbalance persistence and depletion/recovery episode summaries. Compare simple causal exponential kernels with learned compact lag weights; retain source-order and zero-depth masks and separate price-change from size-change contributions.

**Fair comparison.** Quote-only, trade-only, raw OFI, normalized lagged joint features and optional compact sequence model.

**Evidence.** Event arithmetic, scale/support stability, price-path/cost loss, net increment and latency.

**Additional local cases to implement.** Empty side; flicker with no trade; common batching; unchanged healthy quote; stale copied snapshot.

**Decision or system use.** Represent how observable book pressure builds and resolves without claiming off-touch depth or queue identity.

**Exact reviewed source clauses.** [DTM-A12](SOURCE_FINDINGS_AND_CONFLICTS.md:70), [JCV-U02](SOURCE_FINDINGS_AND_CONFLICTS.md:155), [JCV-U03](SOURCE_FINDINGS_AND_CONFLICTS.md:156), [JCV-U04](SOURCE_FINDINGS_AND_CONFLICTS.md:157), [JCV-A03](SOURCE_FINDINGS_AND_CONFLICTS.md:162), [JCV-A06](SOURCE_FINDINGS_AND_CONFLICTS.md:165), [CRL-02](SOURCE_FINDINGS_AND_CONFLICTS.md:218), [DM5-01](SOURCE_FINDINGS_AND_CONFLICTS.md:348), [DM5-02](SOURCE_FINDINGS_AND_CONFLICTS.md:349), [DM5-03](SOURCE_FINDINGS_AND_CONFLICTS.md:350), [DM5-04](SOURCE_FINDINGS_AND_CONFLICTS.md:351), [DM6-01](SOURCE_FINDINGS_AND_CONFLICTS.md:352), [DM6-02](SOURCE_FINDINGS_AND_CONFLICTS.md:353), [DM6-03](SOURCE_FINDINGS_AND_CONFLICTS.md:354), [DM6-04](SOURCE_FINDINGS_AND_CONFLICTS.md:355), [DM6-05](SOURCE_FINDINGS_AND_CONFLICTS.md:356), [DM7-01](SOURCE_FINDINGS_AND_CONFLICTS.md:357), [DM7-02](SOURCE_FINDINGS_AND_CONFLICTS.md:358), [DM7-03](SOURCE_FINDINGS_AND_CONFLICTS.md:359), [DM7-04](SOURCE_FINDINGS_AND_CONFLICTS.md:360), [DM7-05](SOURCE_FINDINGS_AND_CONFLICTS.md:361), [DEN-01](SOURCE_FINDINGS_AND_CONFLICTS.md:409), [DEN-02](SOURCE_FINDINGS_AND_CONFLICTS.md:410), [DEN-03](SOURCE_FINDINGS_AND_CONFLICTS.md:411), [DEN-04](SOURCE_FINDINGS_AND_CONFLICTS.md:412), [DEN-05](SOURCE_FINDINGS_AND_CONFLICTS.md:413), [MAT-02](SOURCE_FINDINGS_AND_CONFLICTS.md:527), [MAT-03](SOURCE_FINDINGS_AND_CONFLICTS.md:528), [RFE-01](SOURCE_FINDINGS_AND_CONFLICTS.md:602), [RFE-02](SOURCE_FINDINGS_AND_CONFLICTS.md:603), [RFE-03](SOURCE_FINDINGS_AND_CONFLICTS.md:604), [RFE-04](SOURCE_FINDINGS_AND_CONFLICTS.md:605), [RFE-05](SOURCE_FINDINGS_AND_CONFLICTS.md:606), [RFE-06](SOURCE_FINDINGS_AND_CONFLICTS.md:607), [RFE-07](SOURCE_FINDINGS_AND_CONFLICTS.md:608), [RFE-08](SOURCE_FINDINGS_AND_CONFLICTS.md:609), [RFE-09](SOURCE_FINDINGS_AND_CONFLICTS.md:610), [RFE-10](SOURCE_FINDINGS_AND_CONFLICTS.md:611), [RFE-11](SOURCE_FINDINGS_AND_CONFLICTS.md:612), [RFE-12](SOURCE_FINDINGS_AND_CONFLICTS.md:613), [RFE-13](SOURCE_FINDINGS_AND_CONFLICTS.md:614), [RFE-14](SOURCE_FINDINGS_AND_CONFLICTS.md:615).

**Conversation upgrade lineage.** [JCV-U04](SOURCE_FINDINGS_AND_CONFLICTS.md:157), [JCV-A03](SOURCE_FINDINGS_AND_CONFLICTS.md:162), [JCV-A06](SOURCE_FINDINGS_AND_CONFLICTS.md:165), [CRL-14](SOURCE_FINDINGS_AND_CONFLICTS.md:230). Read the full rows and their original conversation references; [the recheck](CONVERSATION_RECHECK.md) preserves the exact unit/exception routes.

<a id="up-m09-recovery"></a>
#### M09.RECOVERY — BBO net recovery under executions

[Existing definition, target and P0–P7](experiments/M.md#m09-recovery) remain binding.

**Specific upgrade scope.** Add depletion/recovery episodes, pressure-normalized timing and lagged trade/quote interactions to net recovery bounds.

**Local comparison.** Compare book-only, trade-only and combined features under exact MBP event semantics, with simple kernels first.

**Additional cases.** Batched additions/cancels; zero depth; executions between quotes; unchanged standing best price.

<a id="up-m10"></a>
### UP-M10 — Tape intensity, effort, progress and response efficiency

Parent: [M10](components/MEASUREMENTS.md); [local phases](experiments/M.md#m10); [definition refinement](SYSTEM_REFINEMENT.md#sr-m10). Upgrade role: `measurement`.

**Starting idea.** Read tape speed or divide movement by volume.

**Existing improvement path.** Covered intensity, size/arrival distributions and explicit effort/progress components.

**Remaining weakness.** Ratios are unstable at low exposure and conflate expected activity with exceptional effort or efficiency.

**Further upgrade.** Fit simple conditional expected intensity/progress baselines by session, spread, volatility and covered exposure; export residuals, dispersion, burst persistence and nonlinear effort-progress curves. Compare a ratio with a joint two-dimensional surface before point-process or sequence complexity; keep future markouts in matured labels only.

**Fair comparison.** Rolling counts/ratio, seasonal z-scores, joint residual surfaces, then registered count/process challengers.

**Evidence.** Exposure fidelity, low-denominator stability, conditional target loss, transfer across sessions and decision increment.

**Additional local cases to implement.** Zero effort; sparse clock window; higher volume with proportional progress; changing trade size; missing coverage.

**Decision or system use.** Measure unusual participation and resistance/efficiency with interpretable raw components available for every inference.

**Exact reviewed source clauses.** [JTR-20](SOURCE_FINDINGS_AND_CONFLICTS.md:37), [DTM-A12](SOURCE_FINDINGS_AND_CONFLICTS.md:70), [JXA-13](SOURCE_FINDINGS_AND_CONFLICTS.md:112), [JCV-A06](SOURCE_FINDINGS_AND_CONFLICTS.md:165), [CRL-15](SOURCE_FINDINGS_AND_CONFLICTS.md:231), [DM5-01](SOURCE_FINDINGS_AND_CONFLICTS.md:348), [DM5-02](SOURCE_FINDINGS_AND_CONFLICTS.md:349), [DM5-03](SOURCE_FINDINGS_AND_CONFLICTS.md:350), [DM5-04](SOURCE_FINDINGS_AND_CONFLICTS.md:351), [DM6-01](SOURCE_FINDINGS_AND_CONFLICTS.md:352), [DM6-02](SOURCE_FINDINGS_AND_CONFLICTS.md:353), [DM6-03](SOURCE_FINDINGS_AND_CONFLICTS.md:354), [DM6-04](SOURCE_FINDINGS_AND_CONFLICTS.md:355), [DM6-05](SOURCE_FINDINGS_AND_CONFLICTS.md:356), [MAT-02](SOURCE_FINDINGS_AND_CONFLICTS.md:527), [MAT-03](SOURCE_FINDINGS_AND_CONFLICTS.md:528), [YMA-01](SOURCE_FINDINGS_AND_CONFLICTS.md:589), [YMA-02](SOURCE_FINDINGS_AND_CONFLICTS.md:590), [YMA-03](SOURCE_FINDINGS_AND_CONFLICTS.md:591), [YMA-04](SOURCE_FINDINGS_AND_CONFLICTS.md:592), [YMA-05](SOURCE_FINDINGS_AND_CONFLICTS.md:593), [YMA-06](SOURCE_FINDINGS_AND_CONFLICTS.md:594), [AUT-09](SOURCE_FINDINGS_AND_CONFLICTS.md:775).

**Conversation upgrade lineage.** [DTM-A10](SOURCE_FINDINGS_AND_CONFLICTS.md:68), [JCV-A06](SOURCE_FINDINGS_AND_CONFLICTS.md:165), [CRL-08](SOURCE_FINDINGS_AND_CONFLICTS.md:224), [CRL-14](SOURCE_FINDINGS_AND_CONFLICTS.md:230), [CRL-15](SOURCE_FINDINGS_AND_CONFLICTS.md:231). Read the full rows and their original conversation references; [the recheck](CONVERSATION_RECHECK.md) preserves the exact unit/exception routes.

<a id="up-m10-efficiency"></a>
#### M10.EFFICIENCY — Effort-progress asymmetry

[Existing definition, target and P0–P7](experiments/M.md#m10-efficiency) remain binding.

**Specific upgrade scope.** Model progress and effort jointly, with conditional progress residuals and denominator uncertainty.

**Local comparison.** Compare ratios against compact nonlinear surfaces and response kernels; future markouts remain matured labels.

**Additional cases.** Zero effort; same ratio very different support; quote-driven move; high volume proportional progress.

<a id="up-m10-intensity"></a>
#### M10.INTENSITY — Clock and event activity

[Existing definition, target and P0–P7](experiments/M.md#m10-intensity) remain binding.

**Specific upgrade scope.** Use covered exposure and expected activity to derive intensity surprise, dispersion and burst persistence for each clock.

**Local comparison.** Compare rolling counts, seasonal residuals and registered count/process models before temporal networks.

**Additional cases.** No trades with healthy feed; outage; trade-size mix changes; bursts at normal open.

<a id="up-m11"></a>
### UP-M11 — Aggression memory and subsequent markout ledger

Parent: [M11](components/MEASUREMENTS.md); [local phases](experiments/M.md#m11); [definition refinement](SYSTEM_REFINEMENT.md#sr-m11). Upgrade role: `measurement`.

**Starting idea.** Remember a large print or cluster as a permanent trapped level.

**Existing improvement path.** Causal aggression clusters, markout maturity, decay, retests and survival variants.

**Remaining weakness.** A single cluster center hides distributed pressure and reuses correlated observations across nearby memories.

**Further upgrade.** Maintain a sparse signed spatial memory field with multiple declared decay clocks, cluster lineage and uncertainty, plus retrieval of comparable matured episodes by observable state. Compare deterministic kernel memory with hard clusters; learned lifetime/markout remains downstream and cannot assign ownership.

**Fair comparison.** Fixed-size cluster, KDE/cluster baseline, sparse memory field and supported context-conditioned retrieval.

**Evidence.** Mass/lineage fidelity, memory stability, useful-lifetime/path loss, storage cost and location value.

**Additional local cases to implement.** Clusters merge/split; same prints in overlapping windows; markout pending; retest adds new flow; repeated failure.

**Decision or system use.** Retain where meaningful effort accumulated and how its relevance changes, without turning historical trade flow into invented current inventory.

**Exact reviewed source clauses.** [DTM-A09](SOURCE_FINDINGS_AND_CONFLICTS.md:67), [JXA-08](SOURCE_FINDINGS_AND_CONFLICTS.md:107), [JXA-15](SOURCE_FINDINGS_AND_CONFLICTS.md:114), [JCV-A02](SOURCE_FINDINGS_AND_CONFLICTS.md:161), [JCV-A08](SOURCE_FINDINGS_AND_CONFLICTS.md:167), [CRL-13](SOURCE_FINDINGS_AND_CONFLICTS.md:229), [CRL-19](SOURCE_FINDINGS_AND_CONFLICTS.md:235), [RDL-01](SOURCE_FINDINGS_AND_CONFLICTS.md:550), [RDL-02](SOURCE_FINDINGS_AND_CONFLICTS.md:551), [RDL-03](SOURCE_FINDINGS_AND_CONFLICTS.md:552), [RDL-04](SOURCE_FINDINGS_AND_CONFLICTS.md:553), [RDL-05](SOURCE_FINDINGS_AND_CONFLICTS.md:554), [RDL-06](SOURCE_FINDINGS_AND_CONFLICTS.md:555), [RDL-07](SOURCE_FINDINGS_AND_CONFLICTS.md:556), [OFM-01](SOURCE_FINDINGS_AND_CONFLICTS.md:623), [OFM-02](SOURCE_FINDINGS_AND_CONFLICTS.md:624), [OFM-03](SOURCE_FINDINGS_AND_CONFLICTS.md:625), [OFM-04](SOURCE_FINDINGS_AND_CONFLICTS.md:626), [OFM-05](SOURCE_FINDINGS_AND_CONFLICTS.md:627), [OFM-06](SOURCE_FINDINGS_AND_CONFLICTS.md:628), [OFM-07](SOURCE_FINDINGS_AND_CONFLICTS.md:629), [OFM-08](SOURCE_FINDINGS_AND_CONFLICTS.md:630), [OFM-09](SOURCE_FINDINGS_AND_CONFLICTS.md:631), [OBT-01](SOURCE_FINDINGS_AND_CONFLICTS.md:750), [OBT-02](SOURCE_FINDINGS_AND_CONFLICTS.md:751), [OBT-03](SOURCE_FINDINGS_AND_CONFLICTS.md:752), [OBT-04](SOURCE_FINDINGS_AND_CONFLICTS.md:753), [OBT-05](SOURCE_FINDINGS_AND_CONFLICTS.md:754), [OBT-06](SOURCE_FINDINGS_AND_CONFLICTS.md:755), [OBT-07](SOURCE_FINDINGS_AND_CONFLICTS.md:756), [OBT-08](SOURCE_FINDINGS_AND_CONFLICTS.md:757), [OBT-09](SOURCE_FINDINGS_AND_CONFLICTS.md:758), [OBT-10](SOURCE_FINDINGS_AND_CONFLICTS.md:759).

**Conversation upgrade lineage.** [DTM-A09](SOURCE_FINDINGS_AND_CONFLICTS.md:67), [JCV-A07](SOURCE_FINDINGS_AND_CONFLICTS.md:166). Read the full rows and their original conversation references; [the recheck](CONVERSATION_RECHECK.md) preserves the exact unit/exception routes.

<a id="up-m11-memory_decay"></a>
#### M11.MEMORY_DECAY — Aggression memory and causal markouts

[Existing definition, target and P0–P7](experiments/M.md#m11-memory_decay) remain binding.

**Specific upgrade scope.** Compare hard clusters with sparse signed spatial memory under time/volume/retest decay and causal context retrieval.

**Local comparison.** Score memory fidelity, survival/markout contribution and resource use without inferring current participant inventory.

**Additional cases.** Merged clusters reuse evidence; markout pending; fresh defense; repeated failure.

<a id="up-m12"></a>
### UP-M12 — Opens, gaps, settlements and reference-price measurements

Parent: [M12](components/MEASUREMENTS.md); [local phases](experiments/M.md#m12); [definition refinement](SYSTEM_REFINEMENT.md#sr-m12). Upgrade role: `measurement`.

**Starting idea.** Treat all opens, closes and settlements as interchangeable levels.

**Existing improvement path.** Typed official/source references, first-observed distinctions, exact gap and fractional constructions.

**Remaining weakness.** Independent scalar gaps lose their decomposition across session, reference convention, basis and contract roll.

**Further upgrade.** Create a typed reference graph with deterministic differences, elapsed publication age and bridge provenance. Decompose compatible gaps into overnight/session movement and known coordinate/basis effects; emit reference consensus/spread without merging unlike prices. Preserve every source fraction/body/range construction.

**Fair comparison.** Single open/settlement, separate typed references and graph-derived relative geometry.

**Evidence.** Price/unit reconciliation, publication-time fidelity, roll/basis separation and conditional gap/return information.

**Additional local cases to implement.** Delayed official settlement; no first trade observed; adjusted roll series; body25 differs from range quarter; stale reference.

**Decision or system use.** Use reference relationships consistently and test which differences carry information instead of silently substituting one reference for another.

**Exact reviewed source clauses.** [JTR-02](SOURCE_FINDINGS_AND_CONFLICTS.md:19), [DTM-A11](SOURCE_FINDINGS_AND_CONFLICTS.md:69), [JXA-10](SOURCE_FINDINGS_AND_CONFLICTS.md:109), [CEX-11](SOURCE_FINDINGS_AND_CONFLICTS.md:193), [CRL-06](SOURCE_FINDINGS_AND_CONFLICTS.md:222), [MAV-10](SOURCE_FINDINGS_AND_CONFLICTS.md:514), [PIN012-02](SOURCE_FINDINGS_AND_CONFLICTS.md:853), [PIN013-01](SOURCE_FINDINGS_AND_CONFLICTS.md:857), [PIN013-02](SOURCE_FINDINGS_AND_CONFLICTS.md:858), [PIN013-03](SOURCE_FINDINGS_AND_CONFLICTS.md:859), [PIN013-04](SOURCE_FINDINGS_AND_CONFLICTS.md:860), [PIN013-05](SOURCE_FINDINGS_AND_CONFLICTS.md:861), [PIN013-06](SOURCE_FINDINGS_AND_CONFLICTS.md:862), [PIN015-01](SOURCE_FINDINGS_AND_CONFLICTS.md:865), [PIN015-02](SOURCE_FINDINGS_AND_CONFLICTS.md:866), [PIN015-03](SOURCE_FINDINGS_AND_CONFLICTS.md:867), [PIN023-02](SOURCE_FINDINGS_AND_CONFLICTS.md:898), [PIN025-01](SOURCE_FINDINGS_AND_CONFLICTS.md:899), [PIN032-03](SOURCE_FINDINGS_AND_CONFLICTS.md:916), [PIN036-01](SOURCE_FINDINGS_AND_CONFLICTS.md:925), [PIN037-01](SOURCE_FINDINGS_AND_CONFLICTS.md:927), [PIN039-01](SOURCE_FINDINGS_AND_CONFLICTS.md:933), [PIN039-02](SOURCE_FINDINGS_AND_CONFLICTS.md:934), [PIN040-01](SOURCE_FINDINGS_AND_CONFLICTS.md:935), [PIN040-02](SOURCE_FINDINGS_AND_CONFLICTS.md:936), [PIN041-01](SOURCE_FINDINGS_AND_CONFLICTS.md:938), [PIN041-02](SOURCE_FINDINGS_AND_CONFLICTS.md:939), [PIN041-03](SOURCE_FINDINGS_AND_CONFLICTS.md:940), [PIN042-01](SOURCE_FINDINGS_AND_CONFLICTS.md:942), [PIN042-02](SOURCE_FINDINGS_AND_CONFLICTS.md:943), [PIN046-01](SOURCE_FINDINGS_AND_CONFLICTS.md:955), [PIN047-01](SOURCE_FINDINGS_AND_CONFLICTS.md:956), [PIN047-02](SOURCE_FINDINGS_AND_CONFLICTS.md:957), [PIN047-03](SOURCE_FINDINGS_AND_CONFLICTS.md:958), [PIN049-01](SOURCE_FINDINGS_AND_CONFLICTS.md:964), [PIN049-02](SOURCE_FINDINGS_AND_CONFLICTS.md:965), [PIN049-03](SOURCE_FINDINGS_AND_CONFLICTS.md:966), [PIN054-01](SOURCE_FINDINGS_AND_CONFLICTS.md:978), [PIN054-02](SOURCE_FINDINGS_AND_CONFLICTS.md:979), [PIN061-01](SOURCE_FINDINGS_AND_CONFLICTS.md:997), [PIN061-02](SOURCE_FINDINGS_AND_CONFLICTS.md:998), [PIN061-03](SOURCE_FINDINGS_AND_CONFLICTS.md:999), [PIN064-01](SOURCE_FINDINGS_AND_CONFLICTS.md:1009), [PIN064-02](SOURCE_FINDINGS_AND_CONFLICTS.md:1010), [PIN066-01](SOURCE_FINDINGS_AND_CONFLICTS.md:1016), [PIN066-02](SOURCE_FINDINGS_AND_CONFLICTS.md:1017), [PIN066-03](SOURCE_FINDINGS_AND_CONFLICTS.md:1018), [PIN066-04](SOURCE_FINDINGS_AND_CONFLICTS.md:1019), [PIN073-01](SOURCE_FINDINGS_AND_CONFLICTS.md:1048), [PIN073-02](SOURCE_FINDINGS_AND_CONFLICTS.md:1049), [PIN074-01](SOURCE_FINDINGS_AND_CONFLICTS.md:1051), [PIN074-02](SOURCE_FINDINGS_AND_CONFLICTS.md:1052), [PIN076-01](SOURCE_FINDINGS_AND_CONFLICTS.md:1057), [PIN076-02](SOURCE_FINDINGS_AND_CONFLICTS.md:1058), [PIN077-01](SOURCE_FINDINGS_AND_CONFLICTS.md:1060), [PIN077-02](SOURCE_FINDINGS_AND_CONFLICTS.md:1061), [PIN080-01](SOURCE_FINDINGS_AND_CONFLICTS.md:1071), [PIN080-02](SOURCE_FINDINGS_AND_CONFLICTS.md:1072), [PIN080-03](SOURCE_FINDINGS_AND_CONFLICTS.md:1073), [PIN081-01](SOURCE_FINDINGS_AND_CONFLICTS.md:1075), [PIN081-02](SOURCE_FINDINGS_AND_CONFLICTS.md:1076), [PIN081-03](SOURCE_FINDINGS_AND_CONFLICTS.md:1077), [PIN081-04](SOURCE_FINDINGS_AND_CONFLICTS.md:1078), [PIN082-01](SOURCE_FINDINGS_AND_CONFLICTS.md:1080), [PIN082-02](SOURCE_FINDINGS_AND_CONFLICTS.md:1081), [PIN082-03](SOURCE_FINDINGS_AND_CONFLICTS.md:1082).

**Conversation upgrade lineage.** [CRL-06](SOURCE_FINDINGS_AND_CONFLICTS.md:222). Read the full rows and their original conversation references; [the recheck](CONVERSATION_RECHECK.md) preserves the exact unit/exception routes.

<a id="up-m12-reference_types"></a>
#### M12.REFERENCE_TYPES — Opens, settlements and gaps

[Existing definition, target and P0–P7](experiments/M.md#m12-reference_types) remain binding.

**Specific upgrade scope.** Use typed reference graph relationships and gap decomposition while preserving every official/open/body/range convention.

**Local comparison.** Compare isolated references and relational features; never replace missing official data with a learned price called settlement.

**Additional cases.** Late settlement; first observed trade not true open; body25 versus range quarter; contract bridge.

<a id="up-m13"></a>
### UP-M13 — Footprint and within-bar aggression geometry

Parent: [M13](components/MEASUREMENTS.md); [local phases](experiments/M.md#m13); [definition refinement](SYSTEM_REFINEMENT.md#sr-m13). Upgrade role: `measurement`.

**Starting idea.** Read a footprint's largest imbalance or final delta.

**Existing improvement path.** Exact side/unknown rows, diagonal variants, stacks, tails and within-bar path extrema.

**Remaining weakness.** Final cells discard temporal order and a dense tensor may be costly or sparse relative to available evidence.

**Further upgrade.** Build a causal multiresolution footprint with chronological prefix slices, integrated side contrast, concentration, tail geometry and scale-stable local patterns. Compare compact low-rank/wavelet-style spatial summaries with exact source thresholds and a small tensor encoder, controlling observation granularity independently of learner capacity.

**Fair comparison.** Source rules/bar proxy, exact row statistics, compact spatial-temporal basis and eligible tensor model.

**Evidence.** Volume reconciliation, temporal-order information, sparse-cell robustness, target/net improvement and memory/latency.

**Additional local cases to implement.** Same final footprint with opposite order; row aggregation changes stack; unknown side; final wick unavailable; sparse tail.

**Decision or system use.** Retain useful fine-scale aggression geometry in a representation that can be tested and computed efficiently.

**Exact reviewed source clauses.** [JTR-11](SOURCE_FINDINGS_AND_CONFLICTS.md:28), [JTR-20](SOURCE_FINDINGS_AND_CONFLICTS.md:37), [JXA-13](SOURCE_FINDINGS_AND_CONFLICTS.md:112), [JXA-24](SOURCE_FINDINGS_AND_CONFLICTS.md:123), [CEX-05](SOURCE_FINDINGS_AND_CONFLICTS.md:187), [CRL-18](SOURCE_FINDINGS_AND_CONFLICTS.md:234), [FP8-01](SOURCE_FINDINGS_AND_CONFLICTS.md:369), [FP8-02](SOURCE_FINDINGS_AND_CONFLICTS.md:370), [FP8-03](SOURCE_FINDINGS_AND_CONFLICTS.md:371), [FP8-04](SOURCE_FINDINGS_AND_CONFLICTS.md:372), [FP8-05](SOURCE_FINDINGS_AND_CONFLICTS.md:373), [FP9-01](SOURCE_FINDINGS_AND_CONFLICTS.md:374), [FP9-02](SOURCE_FINDINGS_AND_CONFLICTS.md:375), [FP9-03](SOURCE_FINDINGS_AND_CONFLICTS.md:376), [FP9-04](SOURCE_FINDINGS_AND_CONFLICTS.md:377), [FP9-05](SOURCE_FINDINGS_AND_CONFLICTS.md:378), [FP9-06](SOURCE_FINDINGS_AND_CONFLICTS.md:379), [DEN-01](SOURCE_FINDINGS_AND_CONFLICTS.md:409), [DEN-02](SOURCE_FINDINGS_AND_CONFLICTS.md:410), [DEN-03](SOURCE_FINDINGS_AND_CONFLICTS.md:411), [DEN-04](SOURCE_FINDINGS_AND_CONFLICTS.md:412), [DEN-05](SOURCE_FINDINGS_AND_CONFLICTS.md:413), [F23-02](SOURCE_FINDINGS_AND_CONFLICTS.md:668), [OBT-02](SOURCE_FINDINGS_AND_CONFLICTS.md:751), [MVF-01](SOURCE_FINDINGS_AND_CONFLICTS.md:783), [MVF-02](SOURCE_FINDINGS_AND_CONFLICTS.md:784), [MVF-03](SOURCE_FINDINGS_AND_CONFLICTS.md:785), [MVF-04](SOURCE_FINDINGS_AND_CONFLICTS.md:786), [MVF-05](SOURCE_FINDINGS_AND_CONFLICTS.md:787), [MVF-06](SOURCE_FINDINGS_AND_CONFLICTS.md:788), [MVF-07](SOURCE_FINDINGS_AND_CONFLICTS.md:789).

<a id="up-m13-footprint_channels"></a>
#### M13.FOOTPRINT_CHANNELS — Footprint spatial and temporal detail

[Existing definition, target and P0–P7](experiments/M.md#m13-footprint_channels) remain binding.

**Specific upgrade scope.** Add chronological prefix slices and compact multiscale spatial summaries across side/cohort/diagonal/stack/tail channels.

**Local comparison.** Compare exact source thresholds, continuous row statistics and compact tensor basis independently of observation granularity.

**Additional cases.** Same final tensor different chronology; final wick unavailable; sparse diagonal cells; unknown side.

<a id="family-c"></a>
## Context

<a id="up-c01"></a>
### UP-C01 — Source-faithful range and session geometry

Parent: [C01](components/CONTEXT.md); [local phases](experiments/C.md#c01); [definition refinement](SYSTEM_REFINEMENT.md#sr-c01). Upgrade role: `measurement`.

**Starting idea.** Use one named time range and its quarters/extensions.

**Existing improvement path.** All disclosed source clocks, session geometries, inner/outer anchors and unresolved interpretations are preserved.

**Remaining weakness.** Independent range scalars hide nested/overlapping relationships and repeated geometry, while arbitrary clock choice can dominate results.

**Further upgrade.** Create a causal range-relation graph with shared/unique formation intervals, nestedness, overlap, relative width, opening position and inter-anchor displacement. Keep every exact source clock as a baseline; compare relation features and boundary-robust variants before C05 learned discovery, with no retrospective best window.

**Fair comparison.** Each source range, individual geometry, multi-range relation basis and registered clock-phase perturbations.

**Evidence.** Exact anchor fidelity, phase stability, incremental path information, candidate redundancy and net contribution.

**Additional local cases to implement.** Cross-midnight window; shared endpoints; partial holiday range; inner range outside prior outer range; unfinished formation.

**Decision or system use.** Use relationships among the full range family while preserving the specific clocks and definitions that generated the ideas.

**Exact reviewed source clauses.** [JSS-01](SOURCE_FINDINGS_AND_CONFLICTS.md:11), [JSS-02](SOURCE_FINDINGS_AND_CONFLICTS.md:12), [JSS-03](SOURCE_FINDINGS_AND_CONFLICTS.md:13), [JSS-04](SOURCE_FINDINGS_AND_CONFLICTS.md:14), [JSS-05](SOURCE_FINDINGS_AND_CONFLICTS.md:15), [JSS-06](SOURCE_FINDINGS_AND_CONFLICTS.md:16), [JSS-07](SOURCE_FINDINGS_AND_CONFLICTS.md:17), [JTR-01](SOURCE_FINDINGS_AND_CONFLICTS.md:18), [JTR-02](SOURCE_FINDINGS_AND_CONFLICTS.md:19), [JTR-03](SOURCE_FINDINGS_AND_CONFLICTS.md:20), [JTR-04](SOURCE_FINDINGS_AND_CONFLICTS.md:21), [JTR-05](SOURCE_FINDINGS_AND_CONFLICTS.md:22), [JTR-06](SOURCE_FINDINGS_AND_CONFLICTS.md:23), [JTR-07](SOURCE_FINDINGS_AND_CONFLICTS.md:24), [JTR-08](SOURCE_FINDINGS_AND_CONFLICTS.md:25), [JTR-09](SOURCE_FINDINGS_AND_CONFLICTS.md:26), [JTR-10](SOURCE_FINDINGS_AND_CONFLICTS.md:27), [JTR-11](SOURCE_FINDINGS_AND_CONFLICTS.md:28), [JTR-12](SOURCE_FINDINGS_AND_CONFLICTS.md:29), [JTR-13](SOURCE_FINDINGS_AND_CONFLICTS.md:30), [JTR-14](SOURCE_FINDINGS_AND_CONFLICTS.md:31), [JTR-15](SOURCE_FINDINGS_AND_CONFLICTS.md:32), [JTR-16](SOURCE_FINDINGS_AND_CONFLICTS.md:33), [JTR-17](SOURCE_FINDINGS_AND_CONFLICTS.md:34), [JTR-18](SOURCE_FINDINGS_AND_CONFLICTS.md:35), [JTR-19](SOURCE_FINDINGS_AND_CONFLICTS.md:36), [JTR-20](SOURCE_FINDINGS_AND_CONFLICTS.md:37), [JTR-21](SOURCE_FINDINGS_AND_CONFLICTS.md:38), [JTR-22](SOURCE_FINDINGS_AND_CONFLICTS.md:39), [JTR-23](SOURCE_FINDINGS_AND_CONFLICTS.md:40), [JTR-24](SOURCE_FINDINGS_AND_CONFLICTS.md:41), [DTM-A02](SOURCE_FINDINGS_AND_CONFLICTS.md:60), [JXA-01](SOURCE_FINDINGS_AND_CONFLICTS.md:100), [JXA-02](SOURCE_FINDINGS_AND_CONFLICTS.md:101), [JXA-03](SOURCE_FINDINGS_AND_CONFLICTS.md:102), [JXA-04](SOURCE_FINDINGS_AND_CONFLICTS.md:103), [JXA-05](SOURCE_FINDINGS_AND_CONFLICTS.md:104), [JXA-06](SOURCE_FINDINGS_AND_CONFLICTS.md:105), [JXA-07](SOURCE_FINDINGS_AND_CONFLICTS.md:106), [JXA-08](SOURCE_FINDINGS_AND_CONFLICTS.md:107), [JXA-09](SOURCE_FINDINGS_AND_CONFLICTS.md:108), [JXA-10](SOURCE_FINDINGS_AND_CONFLICTS.md:109), [JXA-11](SOURCE_FINDINGS_AND_CONFLICTS.md:110), [JXA-12](SOURCE_FINDINGS_AND_CONFLICTS.md:111), [JXA-13](SOURCE_FINDINGS_AND_CONFLICTS.md:112), [JXA-14](SOURCE_FINDINGS_AND_CONFLICTS.md:113), [JXA-15](SOURCE_FINDINGS_AND_CONFLICTS.md:114), [JXA-16](SOURCE_FINDINGS_AND_CONFLICTS.md:115), [JXA-17](SOURCE_FINDINGS_AND_CONFLICTS.md:116), [JXA-18](SOURCE_FINDINGS_AND_CONFLICTS.md:117), [JXA-19](SOURCE_FINDINGS_AND_CONFLICTS.md:118), [JXA-20](SOURCE_FINDINGS_AND_CONFLICTS.md:119), [JXA-21](SOURCE_FINDINGS_AND_CONFLICTS.md:120), [JXA-22](SOURCE_FINDINGS_AND_CONFLICTS.md:121), [JXA-23](SOURCE_FINDINGS_AND_CONFLICTS.md:122), [JXA-24](SOURCE_FINDINGS_AND_CONFLICTS.md:123), [JXA-25](SOURCE_FINDINGS_AND_CONFLICTS.md:124), [JXA-26](SOURCE_FINDINGS_AND_CONFLICTS.md:125), [JFN-01](SOURCE_FINDINGS_AND_CONFLICTS.md:135), [JFN-02](SOURCE_FINDINGS_AND_CONFLICTS.md:136), [JFN-03](SOURCE_FINDINGS_AND_CONFLICTS.md:137), [JFN-04](SOURCE_FINDINGS_AND_CONFLICTS.md:138), [JFN-05](SOURCE_FINDINGS_AND_CONFLICTS.md:139), [JFN-06](SOURCE_FINDINGS_AND_CONFLICTS.md:140), [JFN-07](SOURCE_FINDINGS_AND_CONFLICTS.md:141), [JFN-08](SOURCE_FINDINGS_AND_CONFLICTS.md:142), [JFN-09](SOURCE_FINDINGS_AND_CONFLICTS.md:143), [JFN-10](SOURCE_FINDINGS_AND_CONFLICTS.md:144), [JFN-11](SOURCE_FINDINGS_AND_CONFLICTS.md:145), [JFN-12](SOURCE_FINDINGS_AND_CONFLICTS.md:146), [JCV-A01](SOURCE_FINDINGS_AND_CONFLICTS.md:160), [JCV-A04](SOURCE_FINDINGS_AND_CONFLICTS.md:163), [CEX-02](SOURCE_FINDINGS_AND_CONFLICTS.md:184), [CRL-04](SOURCE_FINDINGS_AND_CONFLICTS.md:220), [PIN001-01](SOURCE_FINDINGS_AND_CONFLICTS.md:812), [PIN001-02](SOURCE_FINDINGS_AND_CONFLICTS.md:813), [PIN001-03](SOURCE_FINDINGS_AND_CONFLICTS.md:814), [PIN001-04](SOURCE_FINDINGS_AND_CONFLICTS.md:815), [PIN002-01](SOURCE_FINDINGS_AND_CONFLICTS.md:816), [PIN002-02](SOURCE_FINDINGS_AND_CONFLICTS.md:817), [PIN002-03](SOURCE_FINDINGS_AND_CONFLICTS.md:818), [PIN003-01](SOURCE_FINDINGS_AND_CONFLICTS.md:819), [PIN003-02](SOURCE_FINDINGS_AND_CONFLICTS.md:820), [PIN003-03](SOURCE_FINDINGS_AND_CONFLICTS.md:821), [PIN003-04](SOURCE_FINDINGS_AND_CONFLICTS.md:822), [PIN004-01](SOURCE_FINDINGS_AND_CONFLICTS.md:823), [PIN006-01](SOURCE_FINDINGS_AND_CONFLICTS.md:833), [PIN006-02](SOURCE_FINDINGS_AND_CONFLICTS.md:834), [PIN006-03](SOURCE_FINDINGS_AND_CONFLICTS.md:835), [PIN007-01](SOURCE_FINDINGS_AND_CONFLICTS.md:836), [PIN007-02](SOURCE_FINDINGS_AND_CONFLICTS.md:837), [PIN007-03](SOURCE_FINDINGS_AND_CONFLICTS.md:838), [PIN007-04](SOURCE_FINDINGS_AND_CONFLICTS.md:839), [PIN007-05](SOURCE_FINDINGS_AND_CONFLICTS.md:840), [PIN012-01](SOURCE_FINDINGS_AND_CONFLICTS.md:852), [PIN012-02](SOURCE_FINDINGS_AND_CONFLICTS.md:853), [PIN012-03](SOURCE_FINDINGS_AND_CONFLICTS.md:854), [PIN012-04](SOURCE_FINDINGS_AND_CONFLICTS.md:855), [PIN012-05](SOURCE_FINDINGS_AND_CONFLICTS.md:856), [PIN013-01](SOURCE_FINDINGS_AND_CONFLICTS.md:857), [PIN013-02](SOURCE_FINDINGS_AND_CONFLICTS.md:858), [PIN013-03](SOURCE_FINDINGS_AND_CONFLICTS.md:859), [PIN013-04](SOURCE_FINDINGS_AND_CONFLICTS.md:860), [PIN013-05](SOURCE_FINDINGS_AND_CONFLICTS.md:861), [PIN013-06](SOURCE_FINDINGS_AND_CONFLICTS.md:862), [PIN014-01](SOURCE_FINDINGS_AND_CONFLICTS.md:863), [PIN014-02](SOURCE_FINDINGS_AND_CONFLICTS.md:864), [PIN015-01](SOURCE_FINDINGS_AND_CONFLICTS.md:865), [PIN015-02](SOURCE_FINDINGS_AND_CONFLICTS.md:866), [PIN015-03](SOURCE_FINDINGS_AND_CONFLICTS.md:867), [PIN016-01](SOURCE_FINDINGS_AND_CONFLICTS.md:868), [PIN016-02](SOURCE_FINDINGS_AND_CONFLICTS.md:869), [PIN016-03](SOURCE_FINDINGS_AND_CONFLICTS.md:870), [PIN016-04](SOURCE_FINDINGS_AND_CONFLICTS.md:871), [PIN024-01](SOURCE_FINDINGS_AND_CONFLICTS.md:878), [PIN024-02](SOURCE_FINDINGS_AND_CONFLICTS.md:879), [PIN019-01](SOURCE_FINDINGS_AND_CONFLICTS.md:887), [PIN019-02](SOURCE_FINDINGS_AND_CONFLICTS.md:888), [PIN019-03](SOURCE_FINDINGS_AND_CONFLICTS.md:889), [PIN021-01](SOURCE_FINDINGS_AND_CONFLICTS.md:892), [PIN021-02](SOURCE_FINDINGS_AND_CONFLICTS.md:893), [PIN025-01](SOURCE_FINDINGS_AND_CONFLICTS.md:899), [PIN026-01](SOURCE_FINDINGS_AND_CONFLICTS.md:900), [PIN026-02](SOURCE_FINDINGS_AND_CONFLICTS.md:901), [PIN027-01](SOURCE_FINDINGS_AND_CONFLICTS.md:902), [PIN027-02](SOURCE_FINDINGS_AND_CONFLICTS.md:903), [PIN028-01](SOURCE_FINDINGS_AND_CONFLICTS.md:904), [PIN028-02](SOURCE_FINDINGS_AND_CONFLICTS.md:905), [PIN028-03](SOURCE_FINDINGS_AND_CONFLICTS.md:906), [PIN029-01](SOURCE_FINDINGS_AND_CONFLICTS.md:907), [PIN029-02](SOURCE_FINDINGS_AND_CONFLICTS.md:908), [PIN029-03](SOURCE_FINDINGS_AND_CONFLICTS.md:909), [PIN030-01](SOURCE_FINDINGS_AND_CONFLICTS.md:910), [PIN030-02](SOURCE_FINDINGS_AND_CONFLICTS.md:911), [PIN030-03](SOURCE_FINDINGS_AND_CONFLICTS.md:912), [PIN031-01](SOURCE_FINDINGS_AND_CONFLICTS.md:913), [PIN032-02](SOURCE_FINDINGS_AND_CONFLICTS.md:915), [PIN032-03](SOURCE_FINDINGS_AND_CONFLICTS.md:916), [PIN036-01](SOURCE_FINDINGS_AND_CONFLICTS.md:925), [PIN036-02](SOURCE_FINDINGS_AND_CONFLICTS.md:926), [PIN037-01](SOURCE_FINDINGS_AND_CONFLICTS.md:927), [PIN037-02](SOURCE_FINDINGS_AND_CONFLICTS.md:928), [PIN039-01](SOURCE_FINDINGS_AND_CONFLICTS.md:933), [PIN039-02](SOURCE_FINDINGS_AND_CONFLICTS.md:934), [PIN040-01](SOURCE_FINDINGS_AND_CONFLICTS.md:935), [PIN040-02](SOURCE_FINDINGS_AND_CONFLICTS.md:936), [PIN041-01](SOURCE_FINDINGS_AND_CONFLICTS.md:938), [PIN041-02](SOURCE_FINDINGS_AND_CONFLICTS.md:939), [PIN041-03](SOURCE_FINDINGS_AND_CONFLICTS.md:940), [PIN042-01](SOURCE_FINDINGS_AND_CONFLICTS.md:942), [PIN042-02](SOURCE_FINDINGS_AND_CONFLICTS.md:943), [PIN043-01](SOURCE_FINDINGS_AND_CONFLICTS.md:944), [PIN044-01](SOURCE_FINDINGS_AND_CONFLICTS.md:945), [PIN044-02](SOURCE_FINDINGS_AND_CONFLICTS.md:946), [PIN045-01](SOURCE_FINDINGS_AND_CONFLICTS.md:948), [PIN045-02](SOURCE_FINDINGS_AND_CONFLICTS.md:949), [PIN045-03](SOURCE_FINDINGS_AND_CONFLICTS.md:950), [PIN045-04](SOURCE_FINDINGS_AND_CONFLICTS.md:951), [PIN045-05](SOURCE_FINDINGS_AND_CONFLICTS.md:952), [PIN045-06](SOURCE_FINDINGS_AND_CONFLICTS.md:953), [PIN046-01](SOURCE_FINDINGS_AND_CONFLICTS.md:955), [PIN047-01](SOURCE_FINDINGS_AND_CONFLICTS.md:956), [PIN047-02](SOURCE_FINDINGS_AND_CONFLICTS.md:957), [PIN047-03](SOURCE_FINDINGS_AND_CONFLICTS.md:958), [PIN048-01](SOURCE_FINDINGS_AND_CONFLICTS.md:960), [PIN048-02](SOURCE_FINDINGS_AND_CONFLICTS.md:961), [PIN048-03](SOURCE_FINDINGS_AND_CONFLICTS.md:962), [PIN049-01](SOURCE_FINDINGS_AND_CONFLICTS.md:964), [PIN049-02](SOURCE_FINDINGS_AND_CONFLICTS.md:965), [PIN049-03](SOURCE_FINDINGS_AND_CONFLICTS.md:966), [PIN052-01](SOURCE_FINDINGS_AND_CONFLICTS.md:974), [PIN052-02](SOURCE_FINDINGS_AND_CONFLICTS.md:975), [PIN052-03](SOURCE_FINDINGS_AND_CONFLICTS.md:976), [PIN054-01](SOURCE_FINDINGS_AND_CONFLICTS.md:978), [PIN054-02](SOURCE_FINDINGS_AND_CONFLICTS.md:979), [PIN055-01](SOURCE_FINDINGS_AND_CONFLICTS.md:980), [PIN055-02](SOURCE_FINDINGS_AND_CONFLICTS.md:981), [PIN056-01](SOURCE_FINDINGS_AND_CONFLICTS.md:983), [PIN056-02](SOURCE_FINDINGS_AND_CONFLICTS.md:984), [PIN057-01](SOURCE_FINDINGS_AND_CONFLICTS.md:985), [PIN057-02](SOURCE_FINDINGS_AND_CONFLICTS.md:986), [PIN057-03](SOURCE_FINDINGS_AND_CONFLICTS.md:987), [PIN058-01](SOURCE_FINDINGS_AND_CONFLICTS.md:989), [PIN059-01](SOURCE_FINDINGS_AND_CONFLICTS.md:990), [PIN059-02](SOURCE_FINDINGS_AND_CONFLICTS.md:991), [PIN060-01](SOURCE_FINDINGS_AND_CONFLICTS.md:993), [PIN060-02](SOURCE_FINDINGS_AND_CONFLICTS.md:994), [PIN060-03](SOURCE_FINDINGS_AND_CONFLICTS.md:995), [PIN061-01](SOURCE_FINDINGS_AND_CONFLICTS.md:997), [PIN061-02](SOURCE_FINDINGS_AND_CONFLICTS.md:998), [PIN061-03](SOURCE_FINDINGS_AND_CONFLICTS.md:999), [PIN062-01](SOURCE_FINDINGS_AND_CONFLICTS.md:1001), [PIN062-02](SOURCE_FINDINGS_AND_CONFLICTS.md:1002), [PIN062-03](SOURCE_FINDINGS_AND_CONFLICTS.md:1003), [PIN063-01](SOURCE_FINDINGS_AND_CONFLICTS.md:1005), [PIN063-02](SOURCE_FINDINGS_AND_CONFLICTS.md:1006), [PIN063-03](SOURCE_FINDINGS_AND_CONFLICTS.md:1007), [PIN064-01](SOURCE_FINDINGS_AND_CONFLICTS.md:1009), [PIN064-02](SOURCE_FINDINGS_AND_CONFLICTS.md:1010), [PIN065-01](SOURCE_FINDINGS_AND_CONFLICTS.md:1012), [PIN065-02](SOURCE_FINDINGS_AND_CONFLICTS.md:1013), [PIN065-03](SOURCE_FINDINGS_AND_CONFLICTS.md:1014), [PIN067-01](SOURCE_FINDINGS_AND_CONFLICTS.md:1021), [PIN067-02](SOURCE_FINDINGS_AND_CONFLICTS.md:1022), [PIN068-01](SOURCE_FINDINGS_AND_CONFLICTS.md:1024), [PIN068-02](SOURCE_FINDINGS_AND_CONFLICTS.md:1025), [PIN068-03](SOURCE_FINDINGS_AND_CONFLICTS.md:1026), [PIN070-01](SOURCE_FINDINGS_AND_CONFLICTS.md:1033), [PIN070-02](SOURCE_FINDINGS_AND_CONFLICTS.md:1034), [PIN073-01](SOURCE_FINDINGS_AND_CONFLICTS.md:1048), [PIN073-02](SOURCE_FINDINGS_AND_CONFLICTS.md:1049), [PIN074-01](SOURCE_FINDINGS_AND_CONFLICTS.md:1051), [PIN074-02](SOURCE_FINDINGS_AND_CONFLICTS.md:1052), [PIN075-01](SOURCE_FINDINGS_AND_CONFLICTS.md:1054), [PIN075-02](SOURCE_FINDINGS_AND_CONFLICTS.md:1055), [PIN076-01](SOURCE_FINDINGS_AND_CONFLICTS.md:1057), [PIN076-02](SOURCE_FINDINGS_AND_CONFLICTS.md:1058), [PIN078-01](SOURCE_FINDINGS_AND_CONFLICTS.md:1063), [PIN078-02](SOURCE_FINDINGS_AND_CONFLICTS.md:1064), [PIN080-01](SOURCE_FINDINGS_AND_CONFLICTS.md:1071), [PIN080-02](SOURCE_FINDINGS_AND_CONFLICTS.md:1072), [PIN080-03](SOURCE_FINDINGS_AND_CONFLICTS.md:1073), [PIN081-01](SOURCE_FINDINGS_AND_CONFLICTS.md:1075), [PIN081-02](SOURCE_FINDINGS_AND_CONFLICTS.md:1076), [PIN081-03](SOURCE_FINDINGS_AND_CONFLICTS.md:1077), [PIN081-04](SOURCE_FINDINGS_AND_CONFLICTS.md:1078), [PIN082-01](SOURCE_FINDINGS_AND_CONFLICTS.md:1080), [PIN082-02](SOURCE_FINDINGS_AND_CONFLICTS.md:1081), [PIN082-03](SOURCE_FINDINGS_AND_CONFLICTS.md:1082), [PIN083-01](SOURCE_FINDINGS_AND_CONFLICTS.md:1084), [PIN083-02](SOURCE_FINDINGS_AND_CONFLICTS.md:1085).

**Conversation upgrade lineage.** [JCV-A04](SOURCE_FINDINGS_AND_CONFLICTS.md:163), [CEX-02](SOURCE_FINDINGS_AND_CONFLICTS.md:184). Read the full rows and their original conversation references; [the recheck](CONVERSATION_RECHECK.md) preserves the exact unit/exception routes.

<a id="up-c01-range_geometry"></a>
#### C01.RANGE_GEOMETRY — Source and learned range geometry

[Existing definition, target and P0–P7](experiments/C.md#c01-range_geometry) remain binding.

**Specific upgrade scope.** Add a causal relation graph across every source range: nesting, overlap, shared formation interval, relative width/open and inter-anchor displacement.

**Local comparison.** Compare individual exact ranges and relation features under clock-phase/formation controls, preserving all disclosed windows.

**Additional cases.** Cross-midnight; unfinished range; inner/outer anchors; unresolved London alternatives.

<a id="up-c02"></a>
### UP-C02 — Ordered break, sweep and reclaim state

Parent: [C02](components/CONTEXT.md); [local phases](experiments/C.md#c02); [definition refinement](SYSTEM_REFINEMENT.md#sr-c02). Upgrade role: `forecast`.

**Starting idea.** Label a range as broken, swept or reclaimed.

**Existing improvement path.** Ordered high/low breach, repeated return, depth, gap contact and source tolerance variants.

**Remaining weakness.** A discrete state omits how far, how long and under what pressure a break persists; repeated events can multiply labels without adding evidence.

**Further upgrade.** Add duration, excursion, accepted time/volume, effort and return-depth trajectories to the exact event automaton. Compare shrunken transition tables with semi-Markov competing next-event hazards, preserving simultaneous/gap cases and causal state revisions.

**Fair comparison.** Exact source states, empirical transitions, continuous state summaries and duration-aware hazards.

**Evidence.** Next-branch/time proper loss, state fidelity, repeated-event stability and policy value.

**Additional local cases to implement.** Brief wick versus sustained acceptance; high then low versus low then high; repeated shallow recross; gap over edge.

**Decision or system use.** Forecast the evolving meaning of breaks and reclaims using their observed strength and duration.

**Exact reviewed source clauses.** [JTR-01](SOURCE_FINDINGS_AND_CONFLICTS.md:18), [JTR-02](SOURCE_FINDINGS_AND_CONFLICTS.md:19), [JTR-03](SOURCE_FINDINGS_AND_CONFLICTS.md:20), [JTR-04](SOURCE_FINDINGS_AND_CONFLICTS.md:21), [JTR-05](SOURCE_FINDINGS_AND_CONFLICTS.md:22), [JTR-06](SOURCE_FINDINGS_AND_CONFLICTS.md:23), [JTR-07](SOURCE_FINDINGS_AND_CONFLICTS.md:24), [JTR-08](SOURCE_FINDINGS_AND_CONFLICTS.md:25), [JTR-09](SOURCE_FINDINGS_AND_CONFLICTS.md:26), [JTR-10](SOURCE_FINDINGS_AND_CONFLICTS.md:27), [JTR-11](SOURCE_FINDINGS_AND_CONFLICTS.md:28), [JTR-12](SOURCE_FINDINGS_AND_CONFLICTS.md:29), [JTR-13](SOURCE_FINDINGS_AND_CONFLICTS.md:30), [JTR-14](SOURCE_FINDINGS_AND_CONFLICTS.md:31), [JTR-15](SOURCE_FINDINGS_AND_CONFLICTS.md:32), [JTR-16](SOURCE_FINDINGS_AND_CONFLICTS.md:33), [JTR-17](SOURCE_FINDINGS_AND_CONFLICTS.md:34), [JTR-18](SOURCE_FINDINGS_AND_CONFLICTS.md:35), [JTR-19](SOURCE_FINDINGS_AND_CONFLICTS.md:36), [JTR-20](SOURCE_FINDINGS_AND_CONFLICTS.md:37), [JTR-21](SOURCE_FINDINGS_AND_CONFLICTS.md:38), [JTR-22](SOURCE_FINDINGS_AND_CONFLICTS.md:39), [JTR-23](SOURCE_FINDINGS_AND_CONFLICTS.md:40), [JTR-24](SOURCE_FINDINGS_AND_CONFLICTS.md:41), [JXA-01](SOURCE_FINDINGS_AND_CONFLICTS.md:100), [JXA-02](SOURCE_FINDINGS_AND_CONFLICTS.md:101), [JXA-03](SOURCE_FINDINGS_AND_CONFLICTS.md:102), [JXA-04](SOURCE_FINDINGS_AND_CONFLICTS.md:103), [JXA-05](SOURCE_FINDINGS_AND_CONFLICTS.md:104), [JXA-06](SOURCE_FINDINGS_AND_CONFLICTS.md:105), [JXA-07](SOURCE_FINDINGS_AND_CONFLICTS.md:106), [JXA-08](SOURCE_FINDINGS_AND_CONFLICTS.md:107), [JXA-09](SOURCE_FINDINGS_AND_CONFLICTS.md:108), [JXA-10](SOURCE_FINDINGS_AND_CONFLICTS.md:109), [JXA-11](SOURCE_FINDINGS_AND_CONFLICTS.md:110), [JXA-12](SOURCE_FINDINGS_AND_CONFLICTS.md:111), [JXA-13](SOURCE_FINDINGS_AND_CONFLICTS.md:112), [JXA-14](SOURCE_FINDINGS_AND_CONFLICTS.md:113), [JXA-15](SOURCE_FINDINGS_AND_CONFLICTS.md:114), [JXA-16](SOURCE_FINDINGS_AND_CONFLICTS.md:115), [JXA-17](SOURCE_FINDINGS_AND_CONFLICTS.md:116), [JXA-18](SOURCE_FINDINGS_AND_CONFLICTS.md:117), [JXA-19](SOURCE_FINDINGS_AND_CONFLICTS.md:118), [JXA-20](SOURCE_FINDINGS_AND_CONFLICTS.md:119), [JXA-21](SOURCE_FINDINGS_AND_CONFLICTS.md:120), [JXA-22](SOURCE_FINDINGS_AND_CONFLICTS.md:121), [JXA-23](SOURCE_FINDINGS_AND_CONFLICTS.md:122), [JXA-24](SOURCE_FINDINGS_AND_CONFLICTS.md:123), [JXA-25](SOURCE_FINDINGS_AND_CONFLICTS.md:124), [JXA-26](SOURCE_FINDINGS_AND_CONFLICTS.md:125), [PIN001-01](SOURCE_FINDINGS_AND_CONFLICTS.md:812), [PIN001-02](SOURCE_FINDINGS_AND_CONFLICTS.md:813), [PIN001-03](SOURCE_FINDINGS_AND_CONFLICTS.md:814), [PIN001-04](SOURCE_FINDINGS_AND_CONFLICTS.md:815), [PIN002-01](SOURCE_FINDINGS_AND_CONFLICTS.md:816), [PIN002-02](SOURCE_FINDINGS_AND_CONFLICTS.md:817), [PIN002-03](SOURCE_FINDINGS_AND_CONFLICTS.md:818), [PIN003-01](SOURCE_FINDINGS_AND_CONFLICTS.md:819), [PIN003-02](SOURCE_FINDINGS_AND_CONFLICTS.md:820), [PIN003-03](SOURCE_FINDINGS_AND_CONFLICTS.md:821), [PIN003-04](SOURCE_FINDINGS_AND_CONFLICTS.md:822), [PIN004-01](SOURCE_FINDINGS_AND_CONFLICTS.md:823), [PIN010-01](SOURCE_FINDINGS_AND_CONFLICTS.md:841), [PIN010-02](SOURCE_FINDINGS_AND_CONFLICTS.md:842), [PIN010-03](SOURCE_FINDINGS_AND_CONFLICTS.md:843), [PIN010-04](SOURCE_FINDINGS_AND_CONFLICTS.md:844), [PIN012-01](SOURCE_FINDINGS_AND_CONFLICTS.md:852), [PIN012-02](SOURCE_FINDINGS_AND_CONFLICTS.md:853), [PIN012-03](SOURCE_FINDINGS_AND_CONFLICTS.md:854), [PIN012-04](SOURCE_FINDINGS_AND_CONFLICTS.md:855), [PIN012-05](SOURCE_FINDINGS_AND_CONFLICTS.md:856), [PIN013-01](SOURCE_FINDINGS_AND_CONFLICTS.md:857), [PIN013-02](SOURCE_FINDINGS_AND_CONFLICTS.md:858), [PIN013-03](SOURCE_FINDINGS_AND_CONFLICTS.md:859), [PIN013-04](SOURCE_FINDINGS_AND_CONFLICTS.md:860), [PIN013-05](SOURCE_FINDINGS_AND_CONFLICTS.md:861), [PIN013-06](SOURCE_FINDINGS_AND_CONFLICTS.md:862), [PIN015-01](SOURCE_FINDINGS_AND_CONFLICTS.md:865), [PIN015-02](SOURCE_FINDINGS_AND_CONFLICTS.md:866), [PIN015-03](SOURCE_FINDINGS_AND_CONFLICTS.md:867), [PIN024-01](SOURCE_FINDINGS_AND_CONFLICTS.md:878), [PIN024-02](SOURCE_FINDINGS_AND_CONFLICTS.md:879), [PIN021-01](SOURCE_FINDINGS_AND_CONFLICTS.md:892), [PIN021-02](SOURCE_FINDINGS_AND_CONFLICTS.md:893), [PIN022-01](SOURCE_FINDINGS_AND_CONFLICTS.md:894), [PIN022-02](SOURCE_FINDINGS_AND_CONFLICTS.md:895), [PIN022-03](SOURCE_FINDINGS_AND_CONFLICTS.md:896), [PIN023-01](SOURCE_FINDINGS_AND_CONFLICTS.md:897), [PIN023-02](SOURCE_FINDINGS_AND_CONFLICTS.md:898), [PIN025-01](SOURCE_FINDINGS_AND_CONFLICTS.md:899), [PIN026-01](SOURCE_FINDINGS_AND_CONFLICTS.md:900), [PIN026-02](SOURCE_FINDINGS_AND_CONFLICTS.md:901), [PIN027-01](SOURCE_FINDINGS_AND_CONFLICTS.md:902), [PIN027-02](SOURCE_FINDINGS_AND_CONFLICTS.md:903), [PIN028-01](SOURCE_FINDINGS_AND_CONFLICTS.md:904), [PIN028-02](SOURCE_FINDINGS_AND_CONFLICTS.md:905), [PIN028-03](SOURCE_FINDINGS_AND_CONFLICTS.md:906), [PIN029-01](SOURCE_FINDINGS_AND_CONFLICTS.md:907), [PIN029-02](SOURCE_FINDINGS_AND_CONFLICTS.md:908), [PIN029-03](SOURCE_FINDINGS_AND_CONFLICTS.md:909), [PIN030-01](SOURCE_FINDINGS_AND_CONFLICTS.md:910), [PIN030-02](SOURCE_FINDINGS_AND_CONFLICTS.md:911), [PIN030-03](SOURCE_FINDINGS_AND_CONFLICTS.md:912), [PIN031-01](SOURCE_FINDINGS_AND_CONFLICTS.md:913), [PIN035-01](SOURCE_FINDINGS_AND_CONFLICTS.md:920), [PIN035-02](SOURCE_FINDINGS_AND_CONFLICTS.md:921), [PIN035-03](SOURCE_FINDINGS_AND_CONFLICTS.md:922), [PIN035-04](SOURCE_FINDINGS_AND_CONFLICTS.md:923), [PIN036-01](SOURCE_FINDINGS_AND_CONFLICTS.md:925), [PIN036-02](SOURCE_FINDINGS_AND_CONFLICTS.md:926), [PIN037-01](SOURCE_FINDINGS_AND_CONFLICTS.md:927), [PIN037-02](SOURCE_FINDINGS_AND_CONFLICTS.md:928), [PIN039-01](SOURCE_FINDINGS_AND_CONFLICTS.md:933), [PIN039-02](SOURCE_FINDINGS_AND_CONFLICTS.md:934), [PIN040-01](SOURCE_FINDINGS_AND_CONFLICTS.md:935), [PIN040-02](SOURCE_FINDINGS_AND_CONFLICTS.md:936), [PIN041-01](SOURCE_FINDINGS_AND_CONFLICTS.md:938), [PIN041-02](SOURCE_FINDINGS_AND_CONFLICTS.md:939), [PIN041-03](SOURCE_FINDINGS_AND_CONFLICTS.md:940), [PIN042-01](SOURCE_FINDINGS_AND_CONFLICTS.md:942), [PIN042-02](SOURCE_FINDINGS_AND_CONFLICTS.md:943), [PIN043-01](SOURCE_FINDINGS_AND_CONFLICTS.md:944), [PIN044-01](SOURCE_FINDINGS_AND_CONFLICTS.md:945), [PIN044-02](SOURCE_FINDINGS_AND_CONFLICTS.md:946), [PIN046-01](SOURCE_FINDINGS_AND_CONFLICTS.md:955), [PIN047-01](SOURCE_FINDINGS_AND_CONFLICTS.md:956), [PIN047-02](SOURCE_FINDINGS_AND_CONFLICTS.md:957), [PIN047-03](SOURCE_FINDINGS_AND_CONFLICTS.md:958), [PIN048-01](SOURCE_FINDINGS_AND_CONFLICTS.md:960), [PIN048-02](SOURCE_FINDINGS_AND_CONFLICTS.md:961), [PIN048-03](SOURCE_FINDINGS_AND_CONFLICTS.md:962), [PIN049-01](SOURCE_FINDINGS_AND_CONFLICTS.md:964), [PIN049-02](SOURCE_FINDINGS_AND_CONFLICTS.md:965), [PIN049-03](SOURCE_FINDINGS_AND_CONFLICTS.md:966), [PIN054-01](SOURCE_FINDINGS_AND_CONFLICTS.md:978), [PIN054-02](SOURCE_FINDINGS_AND_CONFLICTS.md:979), [PIN056-01](SOURCE_FINDINGS_AND_CONFLICTS.md:983), [PIN056-02](SOURCE_FINDINGS_AND_CONFLICTS.md:984), [PIN058-01](SOURCE_FINDINGS_AND_CONFLICTS.md:989), [PIN059-01](SOURCE_FINDINGS_AND_CONFLICTS.md:990), [PIN059-02](SOURCE_FINDINGS_AND_CONFLICTS.md:991), [PIN060-01](SOURCE_FINDINGS_AND_CONFLICTS.md:993), [PIN060-02](SOURCE_FINDINGS_AND_CONFLICTS.md:994), [PIN060-03](SOURCE_FINDINGS_AND_CONFLICTS.md:995), [PIN061-01](SOURCE_FINDINGS_AND_CONFLICTS.md:997), [PIN061-02](SOURCE_FINDINGS_AND_CONFLICTS.md:998), [PIN061-03](SOURCE_FINDINGS_AND_CONFLICTS.md:999), [PIN064-01](SOURCE_FINDINGS_AND_CONFLICTS.md:1009), [PIN064-02](SOURCE_FINDINGS_AND_CONFLICTS.md:1010), [PIN071-01](SOURCE_FINDINGS_AND_CONFLICTS.md:1036), [PIN071-02](SOURCE_FINDINGS_AND_CONFLICTS.md:1037), [PIN071-03](SOURCE_FINDINGS_AND_CONFLICTS.md:1038), [PIN071-04](SOURCE_FINDINGS_AND_CONFLICTS.md:1039), [PIN071-05](SOURCE_FINDINGS_AND_CONFLICTS.md:1040), [PIN071-06](SOURCE_FINDINGS_AND_CONFLICTS.md:1041), [PIN071-07](SOURCE_FINDINGS_AND_CONFLICTS.md:1042), [PIN071-08](SOURCE_FINDINGS_AND_CONFLICTS.md:1043), [PIN073-01](SOURCE_FINDINGS_AND_CONFLICTS.md:1048), [PIN073-02](SOURCE_FINDINGS_AND_CONFLICTS.md:1049), [PIN074-01](SOURCE_FINDINGS_AND_CONFLICTS.md:1051), [PIN074-02](SOURCE_FINDINGS_AND_CONFLICTS.md:1052), [PIN075-01](SOURCE_FINDINGS_AND_CONFLICTS.md:1054), [PIN075-02](SOURCE_FINDINGS_AND_CONFLICTS.md:1055), [PIN076-01](SOURCE_FINDINGS_AND_CONFLICTS.md:1057), [PIN076-02](SOURCE_FINDINGS_AND_CONFLICTS.md:1058), [PIN078-01](SOURCE_FINDINGS_AND_CONFLICTS.md:1063), [PIN078-02](SOURCE_FINDINGS_AND_CONFLICTS.md:1064), [PIN080-01](SOURCE_FINDINGS_AND_CONFLICTS.md:1071), [PIN080-02](SOURCE_FINDINGS_AND_CONFLICTS.md:1072), [PIN080-03](SOURCE_FINDINGS_AND_CONFLICTS.md:1073), [PIN081-01](SOURCE_FINDINGS_AND_CONFLICTS.md:1075), [PIN081-02](SOURCE_FINDINGS_AND_CONFLICTS.md:1076), [PIN081-03](SOURCE_FINDINGS_AND_CONFLICTS.md:1077), [PIN081-04](SOURCE_FINDINGS_AND_CONFLICTS.md:1078), [PIN082-01](SOURCE_FINDINGS_AND_CONFLICTS.md:1080), [PIN082-02](SOURCE_FINDINGS_AND_CONFLICTS.md:1081), [PIN082-03](SOURCE_FINDINGS_AND_CONFLICTS.md:1082).

**Conversation upgrade lineage.** [DRF-A20](SOURCE_FINDINGS_AND_CONFLICTS.md:461). Read the full rows and their original conversation references; [the recheck](CONVERSATION_RECHECK.md) preserves the exact unit/exception routes.

<a id="up-c02-ordered_path"></a>
#### C02.ORDERED_PATH — Range event order and repeated breaks

[Existing definition, target and P0–P7](experiments/C.md#c02-ordered_path) remain binding.

**Specific upgrade scope.** Augment exact ordered breach/reclaim states with duration, accepted exposure, depth and repeated-return trajectories.

**Local comparison.** Compare source automaton, transition tables and semi-Markov next-event hazards with exact gap/co-contact semantics.

**Additional cases.** High-then-low versus reverse; brief wick versus acceptance; gap; repeated shallow recross.

<a id="up-c03"></a>
### UP-C03 — Jumbo path and internal-versus-extension forecast experts

Parent: [C03](components/CONTEXT.md); [local phases](experiments/C.md#c03); [definition refinement](SYSTEM_REFINEMENT.md#sr-c03). Upgrade role: `forecast`.

**Starting idea.** Apply one Jumbo day type or projection rule.

**Existing improvement path.** Separate wide/internal, compressed/extension, first-leg, return, partial-retrace and no-move experts.

**Remaining weakness.** Hard branch subdivision can waste sparse data and hide shared dynamics; one successful endpoint can conceal a poor entry path.

**Further upgrade.** Use a shared causal path representation with branch-specific residual heads and duration/ordering distributions. Compare independent specialists, pooled model and hierarchical partial pooling; branch applicability uses only observed geometry/prefix, and every source branch retains its own scorecard.

**Fair comparison.** Source branch rules, pooled simple model, independent heads and shared-plus-branch residual model.

**Evidence.** Branch-specific joint path/time loss, rare-branch support, downstream internal/extension value and complexity.

**Additional local cases to implement.** Wide range still extends; compressed range fails; partial retrace then runner; overlapping branch attributes; no useful move.

**Decision or system use.** Improve all Jumbo paths while testing whether specialization adds information beyond a strong shared baseline.

**Exact reviewed source clauses.** [JTR-01](SOURCE_FINDINGS_AND_CONFLICTS.md:18), [JTR-02](SOURCE_FINDINGS_AND_CONFLICTS.md:19), [JTR-03](SOURCE_FINDINGS_AND_CONFLICTS.md:20), [JTR-04](SOURCE_FINDINGS_AND_CONFLICTS.md:21), [JTR-05](SOURCE_FINDINGS_AND_CONFLICTS.md:22), [JTR-06](SOURCE_FINDINGS_AND_CONFLICTS.md:23), [JTR-07](SOURCE_FINDINGS_AND_CONFLICTS.md:24), [JTR-08](SOURCE_FINDINGS_AND_CONFLICTS.md:25), [JTR-09](SOURCE_FINDINGS_AND_CONFLICTS.md:26), [JTR-10](SOURCE_FINDINGS_AND_CONFLICTS.md:27), [JTR-11](SOURCE_FINDINGS_AND_CONFLICTS.md:28), [JTR-12](SOURCE_FINDINGS_AND_CONFLICTS.md:29), [JTR-13](SOURCE_FINDINGS_AND_CONFLICTS.md:30), [JTR-14](SOURCE_FINDINGS_AND_CONFLICTS.md:31), [JTR-15](SOURCE_FINDINGS_AND_CONFLICTS.md:32), [JTR-16](SOURCE_FINDINGS_AND_CONFLICTS.md:33), [JTR-17](SOURCE_FINDINGS_AND_CONFLICTS.md:34), [JTR-18](SOURCE_FINDINGS_AND_CONFLICTS.md:35), [JTR-19](SOURCE_FINDINGS_AND_CONFLICTS.md:36), [JTR-20](SOURCE_FINDINGS_AND_CONFLICTS.md:37), [JTR-21](SOURCE_FINDINGS_AND_CONFLICTS.md:38), [JTR-22](SOURCE_FINDINGS_AND_CONFLICTS.md:39), [JTR-23](SOURCE_FINDINGS_AND_CONFLICTS.md:40), [JTR-24](SOURCE_FINDINGS_AND_CONFLICTS.md:41), [DTM-A02](SOURCE_FINDINGS_AND_CONFLICTS.md:60), [JXA-01](SOURCE_FINDINGS_AND_CONFLICTS.md:100), [JXA-02](SOURCE_FINDINGS_AND_CONFLICTS.md:101), [JXA-03](SOURCE_FINDINGS_AND_CONFLICTS.md:102), [JXA-04](SOURCE_FINDINGS_AND_CONFLICTS.md:103), [JXA-05](SOURCE_FINDINGS_AND_CONFLICTS.md:104), [JXA-06](SOURCE_FINDINGS_AND_CONFLICTS.md:105), [JXA-07](SOURCE_FINDINGS_AND_CONFLICTS.md:106), [JXA-08](SOURCE_FINDINGS_AND_CONFLICTS.md:107), [JXA-09](SOURCE_FINDINGS_AND_CONFLICTS.md:108), [JXA-10](SOURCE_FINDINGS_AND_CONFLICTS.md:109), [JXA-11](SOURCE_FINDINGS_AND_CONFLICTS.md:110), [JXA-12](SOURCE_FINDINGS_AND_CONFLICTS.md:111), [JXA-13](SOURCE_FINDINGS_AND_CONFLICTS.md:112), [JXA-14](SOURCE_FINDINGS_AND_CONFLICTS.md:113), [JXA-15](SOURCE_FINDINGS_AND_CONFLICTS.md:114), [JXA-16](SOURCE_FINDINGS_AND_CONFLICTS.md:115), [JXA-17](SOURCE_FINDINGS_AND_CONFLICTS.md:116), [JXA-18](SOURCE_FINDINGS_AND_CONFLICTS.md:117), [JXA-19](SOURCE_FINDINGS_AND_CONFLICTS.md:118), [JXA-20](SOURCE_FINDINGS_AND_CONFLICTS.md:119), [JXA-21](SOURCE_FINDINGS_AND_CONFLICTS.md:120), [JXA-22](SOURCE_FINDINGS_AND_CONFLICTS.md:121), [JXA-23](SOURCE_FINDINGS_AND_CONFLICTS.md:122), [JXA-24](SOURCE_FINDINGS_AND_CONFLICTS.md:123), [JXA-25](SOURCE_FINDINGS_AND_CONFLICTS.md:124), [JXA-26](SOURCE_FINDINGS_AND_CONFLICTS.md:125), [JFN-01](SOURCE_FINDINGS_AND_CONFLICTS.md:135), [JFN-02](SOURCE_FINDINGS_AND_CONFLICTS.md:136), [JFN-03](SOURCE_FINDINGS_AND_CONFLICTS.md:137), [JFN-04](SOURCE_FINDINGS_AND_CONFLICTS.md:138), [JFN-05](SOURCE_FINDINGS_AND_CONFLICTS.md:139), [JFN-06](SOURCE_FINDINGS_AND_CONFLICTS.md:140), [JFN-07](SOURCE_FINDINGS_AND_CONFLICTS.md:141), [JFN-08](SOURCE_FINDINGS_AND_CONFLICTS.md:142), [JFN-09](SOURCE_FINDINGS_AND_CONFLICTS.md:143), [JFN-10](SOURCE_FINDINGS_AND_CONFLICTS.md:144), [JFN-11](SOURCE_FINDINGS_AND_CONFLICTS.md:145), [JFN-12](SOURCE_FINDINGS_AND_CONFLICTS.md:146), [JCV-A01](SOURCE_FINDINGS_AND_CONFLICTS.md:160), [CEX-02](SOURCE_FINDINGS_AND_CONFLICTS.md:184), [CEX-04](SOURCE_FINDINGS_AND_CONFLICTS.md:186), [DRF-U07](SOURCE_FINDINGS_AND_CONFLICTS.md:431), [PIN001-01](SOURCE_FINDINGS_AND_CONFLICTS.md:812), [PIN001-02](SOURCE_FINDINGS_AND_CONFLICTS.md:813), [PIN001-03](SOURCE_FINDINGS_AND_CONFLICTS.md:814), [PIN001-04](SOURCE_FINDINGS_AND_CONFLICTS.md:815), [PIN002-01](SOURCE_FINDINGS_AND_CONFLICTS.md:816), [PIN002-02](SOURCE_FINDINGS_AND_CONFLICTS.md:817), [PIN002-03](SOURCE_FINDINGS_AND_CONFLICTS.md:818), [PIN003-01](SOURCE_FINDINGS_AND_CONFLICTS.md:819), [PIN003-02](SOURCE_FINDINGS_AND_CONFLICTS.md:820), [PIN003-03](SOURCE_FINDINGS_AND_CONFLICTS.md:821), [PIN003-04](SOURCE_FINDINGS_AND_CONFLICTS.md:822), [PIN004-01](SOURCE_FINDINGS_AND_CONFLICTS.md:823), [PIN012-01](SOURCE_FINDINGS_AND_CONFLICTS.md:852), [PIN012-02](SOURCE_FINDINGS_AND_CONFLICTS.md:853), [PIN012-03](SOURCE_FINDINGS_AND_CONFLICTS.md:854), [PIN012-04](SOURCE_FINDINGS_AND_CONFLICTS.md:855), [PIN012-05](SOURCE_FINDINGS_AND_CONFLICTS.md:856), [PIN024-01](SOURCE_FINDINGS_AND_CONFLICTS.md:878), [PIN024-02](SOURCE_FINDINGS_AND_CONFLICTS.md:879), [PIN021-01](SOURCE_FINDINGS_AND_CONFLICTS.md:892), [PIN021-02](SOURCE_FINDINGS_AND_CONFLICTS.md:893), [PIN044-01](SOURCE_FINDINGS_AND_CONFLICTS.md:945), [PIN044-02](SOURCE_FINDINGS_AND_CONFLICTS.md:946), [PIN075-01](SOURCE_FINDINGS_AND_CONFLICTS.md:1054), [PIN075-02](SOURCE_FINDINGS_AND_CONFLICTS.md:1055).

**Conversation upgrade lineage.** [DTM-A02](SOURCE_FINDINGS_AND_CONFLICTS.md:60), [JCV-A01](SOURCE_FINDINGS_AND_CONFLICTS.md:160), [DRF-U07](SOURCE_FINDINGS_AND_CONFLICTS.md:431), [DRF-A19](SOURCE_FINDINGS_AND_CONFLICTS.md:460), [DRF-A20](SOURCE_FINDINGS_AND_CONFLICTS.md:461). Read the full rows and their original conversation references; [the recheck](CONVERSATION_RECHECK.md) preserves the exact unit/exception routes.

<a id="up-c03-branches"></a>
#### C03.BRANCHES — Separate Jumbo path specialists

[Existing definition, target and P0–P7](experiments/C.md#c03-branches) remain binding.

**Specific upgrade scope.** Share causal path features across all six Jumbo branch heads while retaining branch-specific residuals and independent scorecards.

**Local comparison.** Compare pooled, separate and partially pooled models on joint path/time and complete internal/extension decisions.

**Additional cases.** Wide internal move; compressed extension; first leg; later return; partial retrace; no useful move.

<a id="up-c04"></a>
### UP-C04 — Open location relative to prior auction structure

Parent: [C04](components/CONTEXT.md); [local phases](experiments/C.md#c04); [definition refinement](SYSTEM_REFINEMENT.md#sr-c04). Upgrade role: `forecast`.

**Starting idea.** Opening outside value implies a drive or reversal.

**Existing improvement path.** Continuous open location plus explicit overlapping open-drive/test/rejection/auction path attributes.

**Remaining weakness.** A completed opening type arrives late and hides uncertainty during the opening sequence.

**Further upgrade.** Represent opening behavior as a landmark prefix with displacement, revisit, tested reference, effort efficiency and elapsed persistence. Forecast each next attribute/transition and remaining path with partial pooling across open locations; compare completed-type usage only at its actual availability.

**Fair comparison.** Source open tables, location-only baseline, continuous prefix features and duration-aware opening transition model.

**Evidence.** Opening attribute/path calibration, early decision value, confirmation delay and rare-type uncertainty.

**Additional local cases to implement.** Drive becomes rejection; test reference differs from value edge; auction and drive attributes overlap; opening reference unavailable.

**Decision or system use.** Use opening structure as evolving evidence rather than waiting for or assuming a final day-type label.

**Exact reviewed source clauses.** [JTR-06](SOURCE_FINDINGS_AND_CONFLICTS.md:23), [JTR-10](SOURCE_FINDINGS_AND_CONFLICTS.md:27), [JTR-21](SOURCE_FINDINGS_AND_CONFLICTS.md:38), [JTR-22](SOURCE_FINDINGS_AND_CONFLICTS.md:39), [JXA-03](SOURCE_FINDINGS_AND_CONFLICTS.md:102), [JXA-06](SOURCE_FINDINGS_AND_CONFLICTS.md:105), [JXA-07](SOURCE_FINDINGS_AND_CONFLICTS.md:106), [JXA-10](SOURCE_FINDINGS_AND_CONFLICTS.md:109), [JXA-13](SOURCE_FINDINGS_AND_CONFLICTS.md:112), [JXA-23](SOURCE_FINDINGS_AND_CONFLICTS.md:122), [JFN-04](SOURCE_FINDINGS_AND_CONFLICTS.md:138), [JFN-05](SOURCE_FINDINGS_AND_CONFLICTS.md:139), [JFN-10](SOURCE_FINDINGS_AND_CONFLICTS.md:144), [CEX-04](SOURCE_FINDINGS_AND_CONFLICTS.md:186), [AM1-08](SOURCE_FINDINGS_AND_CONFLICTS.md:288), [AM1-09](SOURCE_FINDINGS_AND_CONFLICTS.md:289), [MAV-03](SOURCE_FINDINGS_AND_CONFLICTS.md:507), [MAV-07](SOURCE_FINDINGS_AND_CONFLICTS.md:511), [MAV-09](SOURCE_FINDINGS_AND_CONFLICTS.md:513), [MAV-12](SOURCE_FINDINGS_AND_CONFLICTS.md:516), [AUT-06](SOURCE_FINDINGS_AND_CONFLICTS.md:772), [PIN003-01](SOURCE_FINDINGS_AND_CONFLICTS.md:819), [PIN003-02](SOURCE_FINDINGS_AND_CONFLICTS.md:820), [PIN003-03](SOURCE_FINDINGS_AND_CONFLICTS.md:821), [PIN003-04](SOURCE_FINDINGS_AND_CONFLICTS.md:822), [PIN004-01](SOURCE_FINDINGS_AND_CONFLICTS.md:823), [PIN013-01](SOURCE_FINDINGS_AND_CONFLICTS.md:857), [PIN013-02](SOURCE_FINDINGS_AND_CONFLICTS.md:858), [PIN013-03](SOURCE_FINDINGS_AND_CONFLICTS.md:859), [PIN013-04](SOURCE_FINDINGS_AND_CONFLICTS.md:860), [PIN013-05](SOURCE_FINDINGS_AND_CONFLICTS.md:861), [PIN013-06](SOURCE_FINDINGS_AND_CONFLICTS.md:862), [PIN015-01](SOURCE_FINDINGS_AND_CONFLICTS.md:865), [PIN015-02](SOURCE_FINDINGS_AND_CONFLICTS.md:866), [PIN015-03](SOURCE_FINDINGS_AND_CONFLICTS.md:867), [PIN025-01](SOURCE_FINDINGS_AND_CONFLICTS.md:899), [PIN026-01](SOURCE_FINDINGS_AND_CONFLICTS.md:900), [PIN026-02](SOURCE_FINDINGS_AND_CONFLICTS.md:901), [PIN027-01](SOURCE_FINDINGS_AND_CONFLICTS.md:902), [PIN027-02](SOURCE_FINDINGS_AND_CONFLICTS.md:903), [PIN028-01](SOURCE_FINDINGS_AND_CONFLICTS.md:904), [PIN028-02](SOURCE_FINDINGS_AND_CONFLICTS.md:905), [PIN028-03](SOURCE_FINDINGS_AND_CONFLICTS.md:906), [PIN029-01](SOURCE_FINDINGS_AND_CONFLICTS.md:907), [PIN029-02](SOURCE_FINDINGS_AND_CONFLICTS.md:908), [PIN029-03](SOURCE_FINDINGS_AND_CONFLICTS.md:909), [PIN030-01](SOURCE_FINDINGS_AND_CONFLICTS.md:910), [PIN030-02](SOURCE_FINDINGS_AND_CONFLICTS.md:911), [PIN030-03](SOURCE_FINDINGS_AND_CONFLICTS.md:912), [PIN035-02](SOURCE_FINDINGS_AND_CONFLICTS.md:921), [PIN039-01](SOURCE_FINDINGS_AND_CONFLICTS.md:933), [PIN039-02](SOURCE_FINDINGS_AND_CONFLICTS.md:934), [PIN040-01](SOURCE_FINDINGS_AND_CONFLICTS.md:935), [PIN040-02](SOURCE_FINDINGS_AND_CONFLICTS.md:936), [PIN041-01](SOURCE_FINDINGS_AND_CONFLICTS.md:938), [PIN041-02](SOURCE_FINDINGS_AND_CONFLICTS.md:939), [PIN041-03](SOURCE_FINDINGS_AND_CONFLICTS.md:940), [PIN042-01](SOURCE_FINDINGS_AND_CONFLICTS.md:942), [PIN042-02](SOURCE_FINDINGS_AND_CONFLICTS.md:943), [PIN043-01](SOURCE_FINDINGS_AND_CONFLICTS.md:944), [PIN046-01](SOURCE_FINDINGS_AND_CONFLICTS.md:955), [PIN047-01](SOURCE_FINDINGS_AND_CONFLICTS.md:956), [PIN047-02](SOURCE_FINDINGS_AND_CONFLICTS.md:957), [PIN047-03](SOURCE_FINDINGS_AND_CONFLICTS.md:958), [PIN048-01](SOURCE_FINDINGS_AND_CONFLICTS.md:960), [PIN048-02](SOURCE_FINDINGS_AND_CONFLICTS.md:961), [PIN048-03](SOURCE_FINDINGS_AND_CONFLICTS.md:962), [PIN049-01](SOURCE_FINDINGS_AND_CONFLICTS.md:964), [PIN049-02](SOURCE_FINDINGS_AND_CONFLICTS.md:965), [PIN049-03](SOURCE_FINDINGS_AND_CONFLICTS.md:966), [PIN054-01](SOURCE_FINDINGS_AND_CONFLICTS.md:978), [PIN054-02](SOURCE_FINDINGS_AND_CONFLICTS.md:979), [PIN058-01](SOURCE_FINDINGS_AND_CONFLICTS.md:989), [PIN059-01](SOURCE_FINDINGS_AND_CONFLICTS.md:990), [PIN059-02](SOURCE_FINDINGS_AND_CONFLICTS.md:991), [PIN061-01](SOURCE_FINDINGS_AND_CONFLICTS.md:997), [PIN061-02](SOURCE_FINDINGS_AND_CONFLICTS.md:998), [PIN061-03](SOURCE_FINDINGS_AND_CONFLICTS.md:999), [PIN064-01](SOURCE_FINDINGS_AND_CONFLICTS.md:1009), [PIN064-02](SOURCE_FINDINGS_AND_CONFLICTS.md:1010), [PIN073-01](SOURCE_FINDINGS_AND_CONFLICTS.md:1048), [PIN073-02](SOURCE_FINDINGS_AND_CONFLICTS.md:1049), [PIN074-01](SOURCE_FINDINGS_AND_CONFLICTS.md:1051), [PIN074-02](SOURCE_FINDINGS_AND_CONFLICTS.md:1052), [PIN076-01](SOURCE_FINDINGS_AND_CONFLICTS.md:1057), [PIN076-02](SOURCE_FINDINGS_AND_CONFLICTS.md:1058), [PIN078-01](SOURCE_FINDINGS_AND_CONFLICTS.md:1063), [PIN078-02](SOURCE_FINDINGS_AND_CONFLICTS.md:1064), [PIN080-01](SOURCE_FINDINGS_AND_CONFLICTS.md:1071), [PIN080-02](SOURCE_FINDINGS_AND_CONFLICTS.md:1072), [PIN080-03](SOURCE_FINDINGS_AND_CONFLICTS.md:1073), [PIN081-01](SOURCE_FINDINGS_AND_CONFLICTS.md:1075), [PIN081-02](SOURCE_FINDINGS_AND_CONFLICTS.md:1076), [PIN081-03](SOURCE_FINDINGS_AND_CONFLICTS.md:1077), [PIN081-04](SOURCE_FINDINGS_AND_CONFLICTS.md:1078), [PIN082-01](SOURCE_FINDINGS_AND_CONFLICTS.md:1080), [PIN082-02](SOURCE_FINDINGS_AND_CONFLICTS.md:1081), [PIN082-03](SOURCE_FINDINGS_AND_CONFLICTS.md:1082).

**Conversation upgrade lineage.** [CEX-04](SOURCE_FINDINGS_AND_CONFLICTS.md:186). Read the full rows and their original conversation references; [the recheck](CONVERSATION_RECHECK.md) preserves the exact unit/exception routes.

<a id="up-c04-open_type"></a>
#### C04.OPEN_TYPE — Opening structure and path attributes

[Existing definition, target and P0–P7](experiments/C.md#c04-open_type) remain binding.

**Specific upgrade scope.** Forecast opening attributes and next transitions from continuous prefix geometry, tested reference and elapsed persistence.

**Local comparison.** Compare open-location tables, completed-type rules at legal availability and duration-aware early-prefix models.

**Additional cases.** Drive later reverses; test reference changes; overlapping attributes; delayed opening observation.

<a id="up-c05"></a>
### UP-C05 — Adaptive clock, activity and auction-range discovery

Parent: [C05](components/CONTEXT.md); [local phases](experiments/C.md#c05); [definition refinement](SYSTEM_REFINEMENT.md#sr-c05). Upgrade role: `location`.

**Starting idea.** Choose a better fixed clock range by trial and error.

**Existing improvement path.** Registered clock, activity, volatility and auction stopping rules with nested selection budgets.

**Remaining weakness.** Searching many windows can find unstable winners, while a single stopping rule forces different sessions into the same formation pattern.

**Further upgrade.** Compare a small diverse ensemble of causal range proposals with one selected range, using stability-regularized selection and shared relation features. For adaptive formation, estimate stop/continue utility from prefixes with explicit duration, coverage and downstream candidate costs; benchmark simple activity thresholds before a learned boundary hazard.

**Fair comparison.** All source clocks, fixed-grid winner, simple activity/auction stops and bounded diverse proposal ensemble.

**Evidence.** Nested out-of-sample gain, boundary stability, search-adjusted uncertainty, range/candidate budget and compute.

**Additional local cases to implement.** Tiny timing change flips result; no clear auction transition; stopped range later expands; one day favors many hindsight windows.

**Decision or system use.** Discover useful formation schemes without letting clock search or proliferating ranges manufacture apparent improvement.

**Exact reviewed source clauses.** [JTR-03](SOURCE_FINDINGS_AND_CONFLICTS.md:20), [DTM-A04](SOURCE_FINDINGS_AND_CONFLICTS.md:62), [JXA-22](SOURCE_FINDINGS_AND_CONFLICTS.md:121), [JCV-U01](SOURCE_FINDINGS_AND_CONFLICTS.md:154), [JCV-U02](SOURCE_FINDINGS_AND_CONFLICTS.md:155), [JCV-U03](SOURCE_FINDINGS_AND_CONFLICTS.md:156), [JCV-A04](SOURCE_FINDINGS_AND_CONFLICTS.md:163), [CEX-03](SOURCE_FINDINGS_AND_CONFLICTS.md:185), [CRL-02](SOURCE_FINDINGS_AND_CONFLICTS.md:218), [CRL-04](SOURCE_FINDINGS_AND_CONFLICTS.md:220), [DRF-U08](SOURCE_FINDINGS_AND_CONFLICTS.md:432), [PIN001-01](SOURCE_FINDINGS_AND_CONFLICTS.md:812), [PIN001-02](SOURCE_FINDINGS_AND_CONFLICTS.md:813), [PIN001-03](SOURCE_FINDINGS_AND_CONFLICTS.md:814), [PIN001-04](SOURCE_FINDINGS_AND_CONFLICTS.md:815), [PIN002-01](SOURCE_FINDINGS_AND_CONFLICTS.md:816), [PIN002-02](SOURCE_FINDINGS_AND_CONFLICTS.md:817), [PIN002-03](SOURCE_FINDINGS_AND_CONFLICTS.md:818), [PIN012-01](SOURCE_FINDINGS_AND_CONFLICTS.md:852), [PIN012-02](SOURCE_FINDINGS_AND_CONFLICTS.md:853), [PIN012-03](SOURCE_FINDINGS_AND_CONFLICTS.md:854), [PIN012-04](SOURCE_FINDINGS_AND_CONFLICTS.md:855), [PIN012-05](SOURCE_FINDINGS_AND_CONFLICTS.md:856), [PIN024-01](SOURCE_FINDINGS_AND_CONFLICTS.md:878), [PIN024-02](SOURCE_FINDINGS_AND_CONFLICTS.md:879), [PIN021-01](SOURCE_FINDINGS_AND_CONFLICTS.md:892), [PIN021-02](SOURCE_FINDINGS_AND_CONFLICTS.md:893), [PIN044-01](SOURCE_FINDINGS_AND_CONFLICTS.md:945), [PIN044-02](SOURCE_FINDINGS_AND_CONFLICTS.md:946), [PIN075-01](SOURCE_FINDINGS_AND_CONFLICTS.md:1054), [PIN075-02](SOURCE_FINDINGS_AND_CONFLICTS.md:1055).

**Conversation upgrade lineage.** [DTM-A04](SOURCE_FINDINGS_AND_CONFLICTS.md:62), [JCV-U01](SOURCE_FINDINGS_AND_CONFLICTS.md:154), [JCV-U02](SOURCE_FINDINGS_AND_CONFLICTS.md:155), [JCV-U03](SOURCE_FINDINGS_AND_CONFLICTS.md:156), [JCV-A04](SOURCE_FINDINGS_AND_CONFLICTS.md:163), [JCV-A10](SOURCE_FINDINGS_AND_CONFLICTS.md:169), [CEX-03](SOURCE_FINDINGS_AND_CONFLICTS.md:185), [CRL-02](SOURCE_FINDINGS_AND_CONFLICTS.md:218), [CRL-04](SOURCE_FINDINGS_AND_CONFLICTS.md:220), [DRF-U08](SOURCE_FINDINGS_AND_CONFLICTS.md:432), [DRF-A26](SOURCE_FINDINGS_AND_CONFLICTS.md:467). Read the full rows and their original conversation references; [the recheck](CONVERSATION_RECHECK.md) preserves the exact unit/exception routes.

<a id="up-c05-activity"></a>
#### C05.ACTIVITY — Activity and volatility stopping ranges

[Existing definition, target and P0–P7](experiments/C.md#c05-activity) remain binding.

**Specific upgrade scope.** Add causal stop/continue utility and expected-activity phase to volume/event/variance stopping ranges.

**Local comparison.** Compare simple thresholds, one chosen rule and a bounded proposal ensemble; future total volume never sets current phase.

**Additional cases.** Large event overshoot; activity drought; opening burst; stop before later expansion.

<a id="up-c05-auction"></a>
#### C05.AUCTION — Auction and change-point ranges

[Existing definition, target and P0–P7](experiments/C.md#c05-auction) remain binding.

**Specific upgrade scope.** Use occupancy/migration/progress axes to define candidate formation transitions with duration and uncertainty.

**Local comparison.** Compare simple change-point/auction stops and compact boundary hazards after pricing delayed formation and candidate cost.

**Additional cases.** Ambiguous transition; gradual migration; noisy repeated change points; source coverage shift.

<a id="up-c05-clock_search"></a>
#### C05.CLOCK_SEARCH — Clock-range discovery

[Existing definition, target and P0–P7](experiments/C.md#c05-clock_search) remain binding.

**Specific upgrade scope.** Compare one selected clock range with a small diverse, stability-regularized set of source/registered clock proposals.

**Local comparison.** Keep search budget and nested selection explicit; score whether relations improve forecasts beyond more candidates.

**Additional cases.** Minute shift changes winner; many tried clocks; holiday; incomplete formation.

<a id="up-c06"></a>
### UP-C06 — Conditional excursion and P-zone distribution

Parent: [C06](components/CONTEXT.md); [local phases](experiments/C.md#c06); [definition refinement](SYSTEM_REFINEMENT.md#sr-c06). Upgrade role: `forecast`.

**Starting idea.** Turn a historical average or SD into an upper/lower zone.

**Existing improvement path.** Conditional joint excursions, quantiles, ordered touches and observed-prefix remainder targets.

**Remaining weakness.** Separate marginals omit dependence and time; one static daily distribution becomes stale after an unusual prefix.

**Further upgrade.** Compare joint U/D/time/ordering distributions with calibrated marginal baselines and a validated path-law challenger. Add prefix-conditioned residual distributions and common-horizon scenario outputs; compare empirical analog retrieval, distributional regression and compact structured models while preserving all source estimands.

**Fair comparison.** Source statistics, seasonal empirical, marginal quantiles, joint model and matched-information prefix/path challengers.

**Evidence.** Proper joint/quantile loss, tail/ordering/time calibration, band stability and downstream action value.

**Additional local cases to implement.** Large move already occurred; both tails possible; no future observations; session boundary truncates; zero future excursion is valid only when observed.

**Decision or system use.** Forecast remaining opportunity and path uncertainty rather than assigning win probability to an average range or quantile line.

**Exact reviewed source clauses.** [JSS-01](SOURCE_FINDINGS_AND_CONFLICTS.md:11), [JSS-02](SOURCE_FINDINGS_AND_CONFLICTS.md:12), [JSS-03](SOURCE_FINDINGS_AND_CONFLICTS.md:13), [JSS-04](SOURCE_FINDINGS_AND_CONFLICTS.md:14), [JSS-05](SOURCE_FINDINGS_AND_CONFLICTS.md:15), [JSS-06](SOURCE_FINDINGS_AND_CONFLICTS.md:16), [JSS-07](SOURCE_FINDINGS_AND_CONFLICTS.md:17), [DTM-A04](SOURCE_FINDINGS_AND_CONFLICTS.md:62), [JXA-11](SOURCE_FINDINGS_AND_CONFLICTS.md:110), [JXA-19](SOURCE_FINDINGS_AND_CONFLICTS.md:118), [JXA-22](SOURCE_FINDINGS_AND_CONFLICTS.md:121), [JFN-07](SOURCE_FINDINGS_AND_CONFLICTS.md:141), [JFN-11](SOURCE_FINDINGS_AND_CONFLICTS.md:145), [JCV-U01](SOURCE_FINDINGS_AND_CONFLICTS.md:154), [JCV-U02](SOURCE_FINDINGS_AND_CONFLICTS.md:155), [JCV-A04](SOURCE_FINDINGS_AND_CONFLICTS.md:163), [CEX-03](SOURCE_FINDINGS_AND_CONFLICTS.md:185), [CRL-02](SOURCE_FINDINGS_AND_CONFLICTS.md:218), [DRF-U08](SOURCE_FINDINGS_AND_CONFLICTS.md:432), [MAV-10](SOURCE_FINDINGS_AND_CONFLICTS.md:514), [PIN006-01](SOURCE_FINDINGS_AND_CONFLICTS.md:833), [PIN006-02](SOURCE_FINDINGS_AND_CONFLICTS.md:834), [PIN006-03](SOURCE_FINDINGS_AND_CONFLICTS.md:835), [PIN007-01](SOURCE_FINDINGS_AND_CONFLICTS.md:836), [PIN007-02](SOURCE_FINDINGS_AND_CONFLICTS.md:837), [PIN007-03](SOURCE_FINDINGS_AND_CONFLICTS.md:838), [PIN007-04](SOURCE_FINDINGS_AND_CONFLICTS.md:839), [PIN007-05](SOURCE_FINDINGS_AND_CONFLICTS.md:840), [PIN013-01](SOURCE_FINDINGS_AND_CONFLICTS.md:857), [PIN013-02](SOURCE_FINDINGS_AND_CONFLICTS.md:858), [PIN013-03](SOURCE_FINDINGS_AND_CONFLICTS.md:859), [PIN013-04](SOURCE_FINDINGS_AND_CONFLICTS.md:860), [PIN013-05](SOURCE_FINDINGS_AND_CONFLICTS.md:861), [PIN013-06](SOURCE_FINDINGS_AND_CONFLICTS.md:862), [PIN014-01](SOURCE_FINDINGS_AND_CONFLICTS.md:863), [PIN014-02](SOURCE_FINDINGS_AND_CONFLICTS.md:864), [PIN015-01](SOURCE_FINDINGS_AND_CONFLICTS.md:865), [PIN015-02](SOURCE_FINDINGS_AND_CONFLICTS.md:866), [PIN015-03](SOURCE_FINDINGS_AND_CONFLICTS.md:867), [PIN016-01](SOURCE_FINDINGS_AND_CONFLICTS.md:868), [PIN016-02](SOURCE_FINDINGS_AND_CONFLICTS.md:869), [PIN016-03](SOURCE_FINDINGS_AND_CONFLICTS.md:870), [PIN016-04](SOURCE_FINDINGS_AND_CONFLICTS.md:871), [PIN019-01](SOURCE_FINDINGS_AND_CONFLICTS.md:887), [PIN019-02](SOURCE_FINDINGS_AND_CONFLICTS.md:888), [PIN019-03](SOURCE_FINDINGS_AND_CONFLICTS.md:889), [PIN025-01](SOURCE_FINDINGS_AND_CONFLICTS.md:899), [PIN026-01](SOURCE_FINDINGS_AND_CONFLICTS.md:900), [PIN026-02](SOURCE_FINDINGS_AND_CONFLICTS.md:901), [PIN027-01](SOURCE_FINDINGS_AND_CONFLICTS.md:902), [PIN027-02](SOURCE_FINDINGS_AND_CONFLICTS.md:903), [PIN028-01](SOURCE_FINDINGS_AND_CONFLICTS.md:904), [PIN028-02](SOURCE_FINDINGS_AND_CONFLICTS.md:905), [PIN028-03](SOURCE_FINDINGS_AND_CONFLICTS.md:906), [PIN029-01](SOURCE_FINDINGS_AND_CONFLICTS.md:907), [PIN029-02](SOURCE_FINDINGS_AND_CONFLICTS.md:908), [PIN029-03](SOURCE_FINDINGS_AND_CONFLICTS.md:909), [PIN030-01](SOURCE_FINDINGS_AND_CONFLICTS.md:910), [PIN030-02](SOURCE_FINDINGS_AND_CONFLICTS.md:911), [PIN030-03](SOURCE_FINDINGS_AND_CONFLICTS.md:912), [PIN031-01](SOURCE_FINDINGS_AND_CONFLICTS.md:913), [PIN035-02](SOURCE_FINDINGS_AND_CONFLICTS.md:921), [PIN036-01](SOURCE_FINDINGS_AND_CONFLICTS.md:925), [PIN036-02](SOURCE_FINDINGS_AND_CONFLICTS.md:926), [PIN037-01](SOURCE_FINDINGS_AND_CONFLICTS.md:927), [PIN037-02](SOURCE_FINDINGS_AND_CONFLICTS.md:928), [PIN039-01](SOURCE_FINDINGS_AND_CONFLICTS.md:933), [PIN039-02](SOURCE_FINDINGS_AND_CONFLICTS.md:934), [PIN040-01](SOURCE_FINDINGS_AND_CONFLICTS.md:935), [PIN040-02](SOURCE_FINDINGS_AND_CONFLICTS.md:936), [PIN041-01](SOURCE_FINDINGS_AND_CONFLICTS.md:938), [PIN041-02](SOURCE_FINDINGS_AND_CONFLICTS.md:939), [PIN041-03](SOURCE_FINDINGS_AND_CONFLICTS.md:940), [PIN042-01](SOURCE_FINDINGS_AND_CONFLICTS.md:942), [PIN042-02](SOURCE_FINDINGS_AND_CONFLICTS.md:943), [PIN043-01](SOURCE_FINDINGS_AND_CONFLICTS.md:944), [PIN045-01](SOURCE_FINDINGS_AND_CONFLICTS.md:948), [PIN045-02](SOURCE_FINDINGS_AND_CONFLICTS.md:949), [PIN045-03](SOURCE_FINDINGS_AND_CONFLICTS.md:950), [PIN045-04](SOURCE_FINDINGS_AND_CONFLICTS.md:951), [PIN045-05](SOURCE_FINDINGS_AND_CONFLICTS.md:952), [PIN045-06](SOURCE_FINDINGS_AND_CONFLICTS.md:953), [PIN046-01](SOURCE_FINDINGS_AND_CONFLICTS.md:955), [PIN047-01](SOURCE_FINDINGS_AND_CONFLICTS.md:956), [PIN047-02](SOURCE_FINDINGS_AND_CONFLICTS.md:957), [PIN047-03](SOURCE_FINDINGS_AND_CONFLICTS.md:958), [PIN048-01](SOURCE_FINDINGS_AND_CONFLICTS.md:960), [PIN048-02](SOURCE_FINDINGS_AND_CONFLICTS.md:961), [PIN048-03](SOURCE_FINDINGS_AND_CONFLICTS.md:962), [PIN049-01](SOURCE_FINDINGS_AND_CONFLICTS.md:964), [PIN049-02](SOURCE_FINDINGS_AND_CONFLICTS.md:965), [PIN049-03](SOURCE_FINDINGS_AND_CONFLICTS.md:966), [PIN052-01](SOURCE_FINDINGS_AND_CONFLICTS.md:974), [PIN052-02](SOURCE_FINDINGS_AND_CONFLICTS.md:975), [PIN052-03](SOURCE_FINDINGS_AND_CONFLICTS.md:976), [PIN054-01](SOURCE_FINDINGS_AND_CONFLICTS.md:978), [PIN054-02](SOURCE_FINDINGS_AND_CONFLICTS.md:979), [PIN055-01](SOURCE_FINDINGS_AND_CONFLICTS.md:980), [PIN055-02](SOURCE_FINDINGS_AND_CONFLICTS.md:981), [PIN056-01](SOURCE_FINDINGS_AND_CONFLICTS.md:983), [PIN056-02](SOURCE_FINDINGS_AND_CONFLICTS.md:984), [PIN057-01](SOURCE_FINDINGS_AND_CONFLICTS.md:985), [PIN057-02](SOURCE_FINDINGS_AND_CONFLICTS.md:986), [PIN057-03](SOURCE_FINDINGS_AND_CONFLICTS.md:987), [PIN058-01](SOURCE_FINDINGS_AND_CONFLICTS.md:989), [PIN059-01](SOURCE_FINDINGS_AND_CONFLICTS.md:990), [PIN059-02](SOURCE_FINDINGS_AND_CONFLICTS.md:991), [PIN060-01](SOURCE_FINDINGS_AND_CONFLICTS.md:993), [PIN060-02](SOURCE_FINDINGS_AND_CONFLICTS.md:994), [PIN060-03](SOURCE_FINDINGS_AND_CONFLICTS.md:995), [PIN061-01](SOURCE_FINDINGS_AND_CONFLICTS.md:997), [PIN061-02](SOURCE_FINDINGS_AND_CONFLICTS.md:998), [PIN061-03](SOURCE_FINDINGS_AND_CONFLICTS.md:999), [PIN062-01](SOURCE_FINDINGS_AND_CONFLICTS.md:1001), [PIN062-02](SOURCE_FINDINGS_AND_CONFLICTS.md:1002), [PIN062-03](SOURCE_FINDINGS_AND_CONFLICTS.md:1003), [PIN063-01](SOURCE_FINDINGS_AND_CONFLICTS.md:1005), [PIN063-02](SOURCE_FINDINGS_AND_CONFLICTS.md:1006), [PIN063-03](SOURCE_FINDINGS_AND_CONFLICTS.md:1007), [PIN064-01](SOURCE_FINDINGS_AND_CONFLICTS.md:1009), [PIN064-02](SOURCE_FINDINGS_AND_CONFLICTS.md:1010), [PIN065-01](SOURCE_FINDINGS_AND_CONFLICTS.md:1012), [PIN065-02](SOURCE_FINDINGS_AND_CONFLICTS.md:1013), [PIN065-03](SOURCE_FINDINGS_AND_CONFLICTS.md:1014), [PIN067-01](SOURCE_FINDINGS_AND_CONFLICTS.md:1021), [PIN067-02](SOURCE_FINDINGS_AND_CONFLICTS.md:1022), [PIN068-01](SOURCE_FINDINGS_AND_CONFLICTS.md:1024), [PIN068-02](SOURCE_FINDINGS_AND_CONFLICTS.md:1025), [PIN068-03](SOURCE_FINDINGS_AND_CONFLICTS.md:1026), [PIN070-01](SOURCE_FINDINGS_AND_CONFLICTS.md:1033), [PIN070-02](SOURCE_FINDINGS_AND_CONFLICTS.md:1034), [PIN073-01](SOURCE_FINDINGS_AND_CONFLICTS.md:1048), [PIN073-02](SOURCE_FINDINGS_AND_CONFLICTS.md:1049), [PIN074-01](SOURCE_FINDINGS_AND_CONFLICTS.md:1051), [PIN074-02](SOURCE_FINDINGS_AND_CONFLICTS.md:1052), [PIN075-01](SOURCE_FINDINGS_AND_CONFLICTS.md:1054), [PIN075-02](SOURCE_FINDINGS_AND_CONFLICTS.md:1055), [PIN076-01](SOURCE_FINDINGS_AND_CONFLICTS.md:1057), [PIN076-02](SOURCE_FINDINGS_AND_CONFLICTS.md:1058), [PIN078-01](SOURCE_FINDINGS_AND_CONFLICTS.md:1063), [PIN078-02](SOURCE_FINDINGS_AND_CONFLICTS.md:1064), [PIN080-01](SOURCE_FINDINGS_AND_CONFLICTS.md:1071), [PIN080-02](SOURCE_FINDINGS_AND_CONFLICTS.md:1072), [PIN080-03](SOURCE_FINDINGS_AND_CONFLICTS.md:1073), [PIN081-01](SOURCE_FINDINGS_AND_CONFLICTS.md:1075), [PIN081-02](SOURCE_FINDINGS_AND_CONFLICTS.md:1076), [PIN081-03](SOURCE_FINDINGS_AND_CONFLICTS.md:1077), [PIN081-04](SOURCE_FINDINGS_AND_CONFLICTS.md:1078), [PIN082-01](SOURCE_FINDINGS_AND_CONFLICTS.md:1080), [PIN082-02](SOURCE_FINDINGS_AND_CONFLICTS.md:1081), [PIN082-03](SOURCE_FINDINGS_AND_CONFLICTS.md:1082), [PIN083-01](SOURCE_FINDINGS_AND_CONFLICTS.md:1084), [PIN083-02](SOURCE_FINDINGS_AND_CONFLICTS.md:1085).

**Conversation upgrade lineage.** [DTM-A03](SOURCE_FINDINGS_AND_CONFLICTS.md:61), [DTM-A04](SOURCE_FINDINGS_AND_CONFLICTS.md:62), [CEX-02](SOURCE_FINDINGS_AND_CONFLICTS.md:184), [CRL-02](SOURCE_FINDINGS_AND_CONFLICTS.md:218). Read the full rows and their original conversation references; [the recheck](CONVERSATION_RECHECK.md) preserves the exact unit/exception routes.

<a id="up-c06-conditional"></a>
#### C06.CONDITIONAL — Conditional excursion and analog specialists

[Existing definition, target and P0–P7](experiments/C.md#c06-conditional) remain binding.

**Specific upgrade scope.** Upgrade historical analog/statistical zones to uncertainty-aware conditional distributions with simple partial pooling and supported retrieval.

**Local comparison.** Compare disclosed source populations, seasonal empirical, quantile/GAM and richer models at identical target/anchor.

**Additional cases.** Sparse analogs; source mean versus weighted statistic; rare tail; incompatible maturity.

<a id="up-c06-joint"></a>
#### C06.JOINT — Joint excursion, time and ordering

[Existing definition, target and P0–P7](experiments/C.md#c06-joint) remain binding.

**Specific upgrade scope.** Learn or explicitly model joint U/D, arrival time and ordered outcomes with realizable scenario support.

**Local comparison.** Compare marginal quantiles with joint distribution and validated path-law challengers; score ordering separately from extrema.

**Additional cases.** Both excursions large but order differs; overlapping bands; gap; unresolved end.

<a id="up-c06-prefix"></a>
#### C06.PREFIX — Remaining distribution after observed travel

[Existing definition, target and P0–P7](experiments/C.md#c06-prefix) remain binding.

**Specific upgrade scope.** Condition the future remainder on observed travel, current location, duration and state instead of subtracting a used-range scalar.

**Local comparison.** Compare static, direct remainder and conditional path forecasts at frozen cuts and actual remaining horizons.

**Additional cases.** Already travelled both tails; expansion beyond prior forecast; no future coverage; near cutoff.

<a id="up-c07"></a>
### UP-C07 — Auction acceptance, rejection, balance and discovery

Parent: [C07](components/CONTEXT.md); [local phases](experiments/C.md#c07); [definition refinement](SYSTEM_REFINEMENT.md#sr-c07). Upgrade role: `forecast`.

**Starting idea.** Classify the auction as balance, acceptance, rejection or discovery.

**Existing improvement path.** Continuous observed acceptance/overlap/expansion axes and causal transition models.

**Remaining weakness.** One regime label conflates participation, spatial acceptance and directional progress, and transitions may have different durations.

**Further upgrade.** Factor auction state into separate occupancy/acceptance, value migration, directional efficiency and participation axes, then model their joint next transitions. Compare interpretable additive interactions with filtered duration models, retaining conflicting/uncertain states rather than forcing one label.

**Fair comparison.** Source labels, pooled continuous axes, additive transition model and filtered duration-state challenger.

**Evidence.** State/transition calibration, persistence timing, contribution of each axis and economic increment.

**Additional local cases to implement.** High participation with no progress; low-volume discovery; value shifts without price trend; missing tape resembles balance.

**Decision or system use.** Describe and forecast auction behavior through independently measurable dimensions with tested interactions.

**Exact reviewed source clauses.** [DTM-A13](SOURCE_FINDINGS_AND_CONFLICTS.md:71), [CEX-04](SOURCE_FINDINGS_AND_CONFLICTS.md:186), [CEX-09](SOURCE_FINDINGS_AND_CONFLICTS.md:191), [CRL-08](SOURCE_FINDINGS_AND_CONFLICTS.md:224), [AM1-01](SOURCE_FINDINGS_AND_CONFLICTS.md:281), [AM1-02](SOURCE_FINDINGS_AND_CONFLICTS.md:282), [AM1-03](SOURCE_FINDINGS_AND_CONFLICTS.md:283), [AM1-04](SOURCE_FINDINGS_AND_CONFLICTS.md:284), [AM1-05](SOURCE_FINDINGS_AND_CONFLICTS.md:285), [AM1-06](SOURCE_FINDINGS_AND_CONFLICTS.md:286), [AM1-07](SOURCE_FINDINGS_AND_CONFLICTS.md:287), [AM1-08](SOURCE_FINDINGS_AND_CONFLICTS.md:288), [AM1-09](SOURCE_FINDINGS_AND_CONFLICTS.md:289), [AM1-10](SOURCE_FINDINGS_AND_CONFLICTS.md:290), [VP2-01](SOURCE_FINDINGS_AND_CONFLICTS.md:298), [VP2-02](SOURCE_FINDINGS_AND_CONFLICTS.md:299), [VP2-03](SOURCE_FINDINGS_AND_CONFLICTS.md:300), [VP2-04](SOURCE_FINDINGS_AND_CONFLICTS.md:301), [VP2-05](SOURCE_FINDINGS_AND_CONFLICTS.md:302), [TP3-01](SOURCE_FINDINGS_AND_CONFLICTS.md:310), [TP3-02](SOURCE_FINDINGS_AND_CONFLICTS.md:311), [TP3-03](SOURCE_FINDINGS_AND_CONFLICTS.md:312), [TP3-04](SOURCE_FINDINGS_AND_CONFLICTS.md:313), [TP3-05](SOURCE_FINDINGS_AND_CONFLICTS.md:314), [TP3-06](SOURCE_FINDINGS_AND_CONFLICTS.md:315), [TP3-07](SOURCE_FINDINGS_AND_CONFLICTS.md:316), [VX4-09](SOURCE_FINDINGS_AND_CONFLICTS.md:332), [VW10-01](SOURCE_FINDINGS_AND_CONFLICTS.md:380), [VW10-02](SOURCE_FINDINGS_AND_CONFLICTS.md:381), [VW10-03](SOURCE_FINDINGS_AND_CONFLICTS.md:382), [VW10-04](SOURCE_FINDINGS_AND_CONFLICTS.md:383), [VW10-05](SOURCE_FINDINGS_AND_CONFLICTS.md:384), [VW10-06](SOURCE_FINDINGS_AND_CONFLICTS.md:385), [VW10-07](SOURCE_FINDINGS_AND_CONFLICTS.md:386), [CD1-01](SOURCE_FINDINGS_AND_CONFLICTS.md:394), [CD1-02](SOURCE_FINDINGS_AND_CONFLICTS.md:395), [CD1-03](SOURCE_FINDINGS_AND_CONFLICTS.md:396), [CD1-04](SOURCE_FINDINGS_AND_CONFLICTS.md:397), [CD1-05](SOURCE_FINDINGS_AND_CONFLICTS.md:398), [CD3-04](SOURCE_FINDINGS_AND_CONFLICTS.md:407), [MAV-01](SOURCE_FINDINGS_AND_CONFLICTS.md:505), [MAV-02](SOURCE_FINDINGS_AND_CONFLICTS.md:506), [MAV-03](SOURCE_FINDINGS_AND_CONFLICTS.md:507), [MAV-04](SOURCE_FINDINGS_AND_CONFLICTS.md:508), [MAV-05](SOURCE_FINDINGS_AND_CONFLICTS.md:509), [MAV-06](SOURCE_FINDINGS_AND_CONFLICTS.md:510), [MAV-07](SOURCE_FINDINGS_AND_CONFLICTS.md:511), [MAV-08](SOURCE_FINDINGS_AND_CONFLICTS.md:512), [MAV-09](SOURCE_FINDINGS_AND_CONFLICTS.md:513), [MAV-10](SOURCE_FINDINGS_AND_CONFLICTS.md:514), [MAV-11](SOURCE_FINDINGS_AND_CONFLICTS.md:515), [MAV-12](SOURCE_FINDINGS_AND_CONFLICTS.md:516), [MAV-13](SOURCE_FINDINGS_AND_CONFLICTS.md:517), [MAV-14](SOURCE_FINDINGS_AND_CONFLICTS.md:518), [MAT-01](SOURCE_FINDINGS_AND_CONFLICTS.md:526), [MAT-02](SOURCE_FINDINGS_AND_CONFLICTS.md:527), [MAT-03](SOURCE_FINDINGS_AND_CONFLICTS.md:528), [MAT-04](SOURCE_FINDINGS_AND_CONFLICTS.md:529), [MAT-05](SOURCE_FINDINGS_AND_CONFLICTS.md:530), [MAT-06](SOURCE_FINDINGS_AND_CONFLICTS.md:531), [MAT-07](SOURCE_FINDINGS_AND_CONFLICTS.md:532), [MAT-08](SOURCE_FINDINGS_AND_CONFLICTS.md:533), [MAT-09](SOURCE_FINDINGS_AND_CONFLICTS.md:534), [RVP-01](SOURCE_FINDINGS_AND_CONFLICTS.md:542), [RVP-02](SOURCE_FINDINGS_AND_CONFLICTS.md:543), [RVP-03](SOURCE_FINDINGS_AND_CONFLICTS.md:544), [RVP-04](SOURCE_FINDINGS_AND_CONFLICTS.md:545), [RVP-05](SOURCE_FINDINGS_AND_CONFLICTS.md:546), [RVP-06](SOURCE_FINDINGS_AND_CONFLICTS.md:547), [RVP-07](SOURCE_FINDINGS_AND_CONFLICTS.md:548), [RVP-08](SOURCE_FINDINGS_AND_CONFLICTS.md:549), [ALM-01](SOURCE_FINDINGS_AND_CONFLICTS.md:564), [ALM-02](SOURCE_FINDINGS_AND_CONFLICTS.md:565), [ALM-03](SOURCE_FINDINGS_AND_CONFLICTS.md:566), [ALM-04](SOURCE_FINDINGS_AND_CONFLICTS.md:567), [ALM-05](SOURCE_FINDINGS_AND_CONFLICTS.md:568), [ALM-06](SOURCE_FINDINGS_AND_CONFLICTS.md:569), [K10-01](SOURCE_FINDINGS_AND_CONFLICTS.md:639), [K10-02](SOURCE_FINDINGS_AND_CONFLICTS.md:640), [K10-03](SOURCE_FINDINGS_AND_CONFLICTS.md:641), [K10-04](SOURCE_FINDINGS_AND_CONFLICTS.md:642), [K10-05](SOURCE_FINDINGS_AND_CONFLICTS.md:643), [K10-06](SOURCE_FINDINGS_AND_CONFLICTS.md:644), [K18-02](SOURCE_FINDINGS_AND_CONFLICTS.md:653), [F23-01](SOURCE_FINDINGS_AND_CONFLICTS.md:667), [F23-02](SOURCE_FINDINGS_AND_CONFLICTS.md:668), [F23-03](SOURCE_FINDINGS_AND_CONFLICTS.md:669), [F23-04](SOURCE_FINDINGS_AND_CONFLICTS.md:670), [F23-05](SOURCE_FINDINGS_AND_CONFLICTS.md:671), [F23-06](SOURCE_FINDINGS_AND_CONFLICTS.md:672), [F23-07](SOURCE_FINDINGS_AND_CONFLICTS.md:673), [AUT-06](SOURCE_FINDINGS_AND_CONFLICTS.md:772), [PIN066-01](SOURCE_FINDINGS_AND_CONFLICTS.md:1016), [PIN066-02](SOURCE_FINDINGS_AND_CONFLICTS.md:1017), [PIN066-03](SOURCE_FINDINGS_AND_CONFLICTS.md:1018), [PIN066-04](SOURCE_FINDINGS_AND_CONFLICTS.md:1019), [PIN069-01](SOURCE_FINDINGS_AND_CONFLICTS.md:1028), [PIN069-02](SOURCE_FINDINGS_AND_CONFLICTS.md:1029), [PIN069-03](SOURCE_FINDINGS_AND_CONFLICTS.md:1030), [PIN069-04](SOURCE_FINDINGS_AND_CONFLICTS.md:1031), [PIN077-01](SOURCE_FINDINGS_AND_CONFLICTS.md:1060), [PIN077-02](SOURCE_FINDINGS_AND_CONFLICTS.md:1061).

**Conversation upgrade lineage.** [DRF-A20](SOURCE_FINDINGS_AND_CONFLICTS.md:461). Read the full rows and their original conversation references; [the recheck](CONVERSATION_RECHECK.md) preserves the exact unit/exception routes.

<a id="up-c07-acceptance"></a>
#### C07.ACCEPTANCE — Acceptance, rejection and discovery axes

[Existing definition, target and P0–P7](experiments/C.md#c07-acceptance) remain binding.

**Specific upgrade scope.** Separate occupancy/acceptance, migration, progress and participation axes and forecast their joint transitions.

**Local comparison.** Compare source hard states, additive axes and filtered duration models; retain simultaneous/conflicting state evidence.

**Additional cases.** High effort no progress; quiet discovery; value migrates without trend; missing tape.

<a id="up-c08"></a>
### UP-C08 — Value migration and multiscale auction relationships

Parent: [C08](components/CONTEXT.md); [local phases](experiments/C.md#c08); [definition refinement](SYSTEM_REFINEMENT.md#sr-c08). Upgrade role: `forecast`.

**Starting idea.** Track the slope of POC or overlap of value areas.

**Existing improvement path.** Distribution distance, emerging modes, valley filling and aligned developing profile comparisons.

**Remaining weakness.** Describing past movement does not predict where future traded mass or useful regions will form.

**Further upgrade.** Add explicit future profile-evolution targets on a grid frozen at the cut, with overflow and future added-mass versus total-profile distributions. Compare persistence/seasonal expected-profile baselines, low-rank mass-increment models and optional spatial-temporal encoders conditioned on flow, auction state and elapsed exposure; forecast mode/VA changes as derived targets.

**Fair comparison.** POC/overlap rules, transport features only, expected-profile residual baseline and future mass-evolution model.

**Evidence.** Proper mass-distribution score, mode/VA transition calibration, incremental path/location net and grid robustness.

**Additional local cases to implement.** New mode appears outside grid; total volume unknown; same POC with mass shift; elapsed maturity mismatch; missing future tape.

**Decision or system use.** Upgrade profile migration into a testable forecast of auction development, with economic value evaluated separately from shape accuracy.

**Exact reviewed source clauses.** [AM1-01](SOURCE_FINDINGS_AND_CONFLICTS.md:281), [AM1-02](SOURCE_FINDINGS_AND_CONFLICTS.md:282), [AM1-03](SOURCE_FINDINGS_AND_CONFLICTS.md:283), [AM1-04](SOURCE_FINDINGS_AND_CONFLICTS.md:284), [AM1-05](SOURCE_FINDINGS_AND_CONFLICTS.md:285), [AM1-06](SOURCE_FINDINGS_AND_CONFLICTS.md:286), [AM1-07](SOURCE_FINDINGS_AND_CONFLICTS.md:287), [AM1-08](SOURCE_FINDINGS_AND_CONFLICTS.md:288), [AM1-09](SOURCE_FINDINGS_AND_CONFLICTS.md:289), [AM1-10](SOURCE_FINDINGS_AND_CONFLICTS.md:290), [MAV-01](SOURCE_FINDINGS_AND_CONFLICTS.md:505), [MAV-02](SOURCE_FINDINGS_AND_CONFLICTS.md:506), [MAV-03](SOURCE_FINDINGS_AND_CONFLICTS.md:507), [MAV-04](SOURCE_FINDINGS_AND_CONFLICTS.md:508), [MAV-05](SOURCE_FINDINGS_AND_CONFLICTS.md:509), [MAV-06](SOURCE_FINDINGS_AND_CONFLICTS.md:510), [MAV-07](SOURCE_FINDINGS_AND_CONFLICTS.md:511), [MAV-08](SOURCE_FINDINGS_AND_CONFLICTS.md:512), [MAV-09](SOURCE_FINDINGS_AND_CONFLICTS.md:513), [MAV-10](SOURCE_FINDINGS_AND_CONFLICTS.md:514), [MAV-11](SOURCE_FINDINGS_AND_CONFLICTS.md:515), [MAV-12](SOURCE_FINDINGS_AND_CONFLICTS.md:516), [MAV-13](SOURCE_FINDINGS_AND_CONFLICTS.md:517), [MAV-14](SOURCE_FINDINGS_AND_CONFLICTS.md:518), [MAT-01](SOURCE_FINDINGS_AND_CONFLICTS.md:526), [MAT-02](SOURCE_FINDINGS_AND_CONFLICTS.md:527), [MAT-03](SOURCE_FINDINGS_AND_CONFLICTS.md:528), [MAT-04](SOURCE_FINDINGS_AND_CONFLICTS.md:529), [MAT-05](SOURCE_FINDINGS_AND_CONFLICTS.md:530), [MAT-06](SOURCE_FINDINGS_AND_CONFLICTS.md:531), [MAT-07](SOURCE_FINDINGS_AND_CONFLICTS.md:532), [MAT-08](SOURCE_FINDINGS_AND_CONFLICTS.md:533), [MAT-09](SOURCE_FINDINGS_AND_CONFLICTS.md:534), [RVP-01](SOURCE_FINDINGS_AND_CONFLICTS.md:542), [RVP-02](SOURCE_FINDINGS_AND_CONFLICTS.md:543), [RVP-03](SOURCE_FINDINGS_AND_CONFLICTS.md:544), [RVP-04](SOURCE_FINDINGS_AND_CONFLICTS.md:545), [RVP-05](SOURCE_FINDINGS_AND_CONFLICTS.md:546), [RVP-06](SOURCE_FINDINGS_AND_CONFLICTS.md:547), [RVP-07](SOURCE_FINDINGS_AND_CONFLICTS.md:548), [RVP-08](SOURCE_FINDINGS_AND_CONFLICTS.md:549), [ALM-01](SOURCE_FINDINGS_AND_CONFLICTS.md:564), [ALM-02](SOURCE_FINDINGS_AND_CONFLICTS.md:565), [ALM-03](SOURCE_FINDINGS_AND_CONFLICTS.md:566), [ALM-04](SOURCE_FINDINGS_AND_CONFLICTS.md:567), [ALM-05](SOURCE_FINDINGS_AND_CONFLICTS.md:568), [ALM-06](SOURCE_FINDINGS_AND_CONFLICTS.md:569), [K18-02](SOURCE_FINDINGS_AND_CONFLICTS.md:653), [F23-01](SOURCE_FINDINGS_AND_CONFLICTS.md:667), [F23-02](SOURCE_FINDINGS_AND_CONFLICTS.md:668), [F23-03](SOURCE_FINDINGS_AND_CONFLICTS.md:669), [F23-04](SOURCE_FINDINGS_AND_CONFLICTS.md:670), [F23-05](SOURCE_FINDINGS_AND_CONFLICTS.md:671), [F23-06](SOURCE_FINDINGS_AND_CONFLICTS.md:672), [F23-07](SOURCE_FINDINGS_AND_CONFLICTS.md:673), [CCS-01](SOURCE_FINDINGS_AND_CONFLICTS.md:681), [CCS-02](SOURCE_FINDINGS_AND_CONFLICTS.md:682), [CCS-03](SOURCE_FINDINGS_AND_CONFLICTS.md:683), [CCS-04](SOURCE_FINDINGS_AND_CONFLICTS.md:684), [CCS-05](SOURCE_FINDINGS_AND_CONFLICTS.md:685), [CCS-06](SOURCE_FINDINGS_AND_CONFLICTS.md:686), [CCS-07](SOURCE_FINDINGS_AND_CONFLICTS.md:687), [CCS-08](SOURCE_FINDINGS_AND_CONFLICTS.md:688).

<a id="up-c08-migration"></a>
#### C08.MIGRATION — Value migration across anchors

[Existing definition, target and P0–P7](experiments/C.md#c08-migration) remain binding.

**Specific upgrade scope.** Predict future added mass and resulting profile shape on a frozen grid, deriving future mode/value changes separately.

**Local comparison.** Compare POC slope/transport-only, persistence/seasonal profile and low-rank or spatial-temporal evolution models.

**Additional cases.** Overflow; new second mode; equal POC different mass; future profile volume unknown.

<a id="up-c09"></a>
### UP-C09 — Historical range and seasonal volatility baseline

Parent: [C09](components/CONTEXT.md); [local phases](experiments/C.md#c09); [definition refinement](SYSTEM_REFINEMENT.md#sr-c09). Upgrade role: `forecast`.

**Starting idea.** Scale today's room from yesterday's range or ATR.

**Existing improvement path.** Robust rolling/seasonal distributions and exact range-versus-variance targets.

**Remaining weakness.** Fixed lookbacks poorly share information across sparse calendar states and may overreact to one extreme day.

**Further upgrade.** Use hierarchical seasonal baselines that pool time-of-day, weekday/event and volatility-state effects with train-only shrinkage. Compare empirical quantile curves, recency weighting and simple additive distribution models; preserve a no-condition/persistence floor and separate opening jump from intraday range.

**Fair comparison.** Previous/ATR, existing seasonal/EWMA, hierarchically pooled empirical distributions and simple GAM.

**Evidence.** Proper range/quantile loss, tail coverage, stability across years and downstream value relative to added cost.

**Additional local cases to implement.** Rare event day; holiday duration; isolated extreme; changing volatility level; many zeros from unavailable data.

**Decision or system use.** Make the simple baseline strong and adaptive enough that richer specialists must demonstrate real incremental information.

**Exact reviewed source clauses.** [DTM-A03](SOURCE_FINDINGS_AND_CONFLICTS.md:61), [JCV-A05](SOURCE_FINDINGS_AND_CONFLICTS.md:164), [CEX-06](SOURCE_FINDINGS_AND_CONFLICTS.md:188), [DEN-03](SOURCE_FINDINGS_AND_CONFLICTS.md:411), [DRF-A12](SOURCE_FINDINGS_AND_CONFLICTS.md:453), [MAV-13](SOURCE_FINDINGS_AND_CONFLICTS.md:517), [PIN008-01](SOURCE_FINDINGS_AND_CONFLICTS.md:824), [PIN009-01](SOURCE_FINDINGS_AND_CONFLICTS.md:825), [PIN009-02](SOURCE_FINDINGS_AND_CONFLICTS.md:826), [PIN006-01](SOURCE_FINDINGS_AND_CONFLICTS.md:833), [PIN006-02](SOURCE_FINDINGS_AND_CONFLICTS.md:834), [PIN006-03](SOURCE_FINDINGS_AND_CONFLICTS.md:835), [PIN007-01](SOURCE_FINDINGS_AND_CONFLICTS.md:836), [PIN007-02](SOURCE_FINDINGS_AND_CONFLICTS.md:837), [PIN007-03](SOURCE_FINDINGS_AND_CONFLICTS.md:838), [PIN007-04](SOURCE_FINDINGS_AND_CONFLICTS.md:839), [PIN007-05](SOURCE_FINDINGS_AND_CONFLICTS.md:840), [PIN011-03](SOURCE_FINDINGS_AND_CONFLICTS.md:847), [PIN014-01](SOURCE_FINDINGS_AND_CONFLICTS.md:863), [PIN014-02](SOURCE_FINDINGS_AND_CONFLICTS.md:864), [PIN016-01](SOURCE_FINDINGS_AND_CONFLICTS.md:868), [PIN016-02](SOURCE_FINDINGS_AND_CONFLICTS.md:869), [PIN016-03](SOURCE_FINDINGS_AND_CONFLICTS.md:870), [PIN016-04](SOURCE_FINDINGS_AND_CONFLICTS.md:871), [PIN017-01](SOURCE_FINDINGS_AND_CONFLICTS.md:872), [PIN017-02](SOURCE_FINDINGS_AND_CONFLICTS.md:873), [PIN017-03](SOURCE_FINDINGS_AND_CONFLICTS.md:874), [PIN017-04](SOURCE_FINDINGS_AND_CONFLICTS.md:875), [PIN033-01](SOURCE_FINDINGS_AND_CONFLICTS.md:917), [PIN033-02](SOURCE_FINDINGS_AND_CONFLICTS.md:918), [PIN045-01](SOURCE_FINDINGS_AND_CONFLICTS.md:948), [PIN045-02](SOURCE_FINDINGS_AND_CONFLICTS.md:949), [PIN045-03](SOURCE_FINDINGS_AND_CONFLICTS.md:950), [PIN045-04](SOURCE_FINDINGS_AND_CONFLICTS.md:951), [PIN045-05](SOURCE_FINDINGS_AND_CONFLICTS.md:952), [PIN045-06](SOURCE_FINDINGS_AND_CONFLICTS.md:953), [PIN052-01](SOURCE_FINDINGS_AND_CONFLICTS.md:974), [PIN052-02](SOURCE_FINDINGS_AND_CONFLICTS.md:975), [PIN052-03](SOURCE_FINDINGS_AND_CONFLICTS.md:976), [PIN055-01](SOURCE_FINDINGS_AND_CONFLICTS.md:980), [PIN055-02](SOURCE_FINDINGS_AND_CONFLICTS.md:981), [PIN057-01](SOURCE_FINDINGS_AND_CONFLICTS.md:985), [PIN057-02](SOURCE_FINDINGS_AND_CONFLICTS.md:986), [PIN057-03](SOURCE_FINDINGS_AND_CONFLICTS.md:987), [PIN062-01](SOURCE_FINDINGS_AND_CONFLICTS.md:1001), [PIN062-02](SOURCE_FINDINGS_AND_CONFLICTS.md:1002), [PIN062-03](SOURCE_FINDINGS_AND_CONFLICTS.md:1003), [PIN063-01](SOURCE_FINDINGS_AND_CONFLICTS.md:1005), [PIN063-02](SOURCE_FINDINGS_AND_CONFLICTS.md:1006), [PIN063-03](SOURCE_FINDINGS_AND_CONFLICTS.md:1007), [PIN065-01](SOURCE_FINDINGS_AND_CONFLICTS.md:1012), [PIN065-02](SOURCE_FINDINGS_AND_CONFLICTS.md:1013), [PIN065-03](SOURCE_FINDINGS_AND_CONFLICTS.md:1014), [PIN067-01](SOURCE_FINDINGS_AND_CONFLICTS.md:1021), [PIN067-02](SOURCE_FINDINGS_AND_CONFLICTS.md:1022), [PIN068-01](SOURCE_FINDINGS_AND_CONFLICTS.md:1024), [PIN068-02](SOURCE_FINDINGS_AND_CONFLICTS.md:1025), [PIN068-03](SOURCE_FINDINGS_AND_CONFLICTS.md:1026), [PIN070-01](SOURCE_FINDINGS_AND_CONFLICTS.md:1033), [PIN070-02](SOURCE_FINDINGS_AND_CONFLICTS.md:1034), [PIN083-01](SOURCE_FINDINGS_AND_CONFLICTS.md:1084), [PIN083-02](SOURCE_FINDINGS_AND_CONFLICTS.md:1085).

**Conversation upgrade lineage.** [DTM-A03](SOURCE_FINDINGS_AND_CONFLICTS.md:61). Read the full rows and their original conversation references; [the recheck](CONVERSATION_RECHECK.md) preserves the exact unit/exception routes.

<a id="up-c09-seasonal"></a>
#### C09.SEASONAL — Session-conditioned volatility baselines

[Existing definition, target and P0–P7](experiments/C.md#c09-seasonal) remain binding.

**Specific upgrade scope.** Build partially pooled seasonal distribution curves with recency/event/state effects and robust tails.

**Local comparison.** Compare ATR/previous range, empirical/EWMA and hierarchical additive baselines at equal history support.

**Additional cases.** Rare calendar cell; half-day; outlier; changed volatility level.

<a id="up-c10"></a>
### UP-C10 — Garman–Klass measurement and forecast specialist

Parent: [C10](components/CONTEXT.md); [local phases](experiments/C.md#c10); [definition refinement](SYSTEM_REFINEMENT.md#sr-c10). Upgrade role: `forecast`.

**Starting idea.** Use one OHLC-based volatility estimate as future movement.

**Existing improvement path.** GK measured on compatible intervals and separately mapped to future variance/path targets.

**Remaining weakness.** OHLC estimates at several scales can be redundant or affected differently by opening jumps, noise and short intervals.

**Further upgrade.** Preserve the verified GK formula and add scale/interval diagnostics plus residual information relative to close-return and RV baselines. Compare pooled lag regression with a reliability-conditioned GK contribution in G02, holding forward target and observation set fixed; GK alone does not supply barrier ordering.

**Fair comparison.** Close/EWMA, lagged GK, multiscale GK residual features and regularized reliability-conditioned forecast.

**Evidence.** Reference arithmetic, common-target QLIKE/proper loss, incremental information, scale stability and net downstream use.

**Additional local cases to implement.** Opening jump omitted; very short noisy interval; flat prices; invalid OHLC ordering; many redundant scales.

**Decision or system use.** Use GK where its measured range information adds forecast value, rather than assuming the estimator is itself a prediction.

**Exact reviewed source clauses.** [DTM-A03](SOURCE_FINDINGS_AND_CONFLICTS.md:61), [JCV-U02](SOURCE_FINDINGS_AND_CONFLICTS.md:155), [JCV-A05](SOURCE_FINDINGS_AND_CONFLICTS.md:164), [CEX-06](SOURCE_FINDINGS_AND_CONFLICTS.md:188), [DRF-A12](SOURCE_FINDINGS_AND_CONFLICTS.md:453).

**Conversation upgrade lineage.** [JCV-U02](SOURCE_FINDINGS_AND_CONFLICTS.md:155), [JCV-A05](SOURCE_FINDINGS_AND_CONFLICTS.md:164), [CEX-06](SOURCE_FINDINGS_AND_CONFLICTS.md:188). Read the full rows and their original conversation references; [the recheck](CONVERSATION_RECHECK.md) preserves the exact unit/exception routes.

<a id="up-c10-gk_robust"></a>
#### C10.GK_ROBUST — GK measurement versus forecast

[Existing definition, target and P0–P7](experiments/C.md#c10-gk_robust) remain binding.

**Specific upgrade scope.** Expose multiscale GK residual information and reliability diagnostics relative to close-return/RV measures.

**Local comparison.** Preserve verified formula; compare aggregate lags and reliability-conditioned contribution under common future variance targets.

**Additional cases.** Opening jump; short noisy bar; redundant scales; invalid OHLC.

<a id="up-c11"></a>
### UP-C11 — Yang–Zhang opening-jump-aware specialist

Parent: [C11](components/CONTEXT.md); [local phases](experiments/C.md#c11); [definition refinement](SYSTEM_REFINEMENT.md#sr-c11). Upgrade role: `forecast`.

**Starting idea.** Add opening jumps to an OHLC volatility number.

**Existing improvement path.** YZ separates opening return, intraday close return and Rogers–Satchell components.

**Remaining weakness.** A combined scalar hides which component changes and whether a session convention makes the opening term meaningful.

**Further upgrade.** Keep verified YZ and expose its component/scale contributions with compatible session-gap metadata. Compare component-wise lag and asymmetric response models with the aggregate estimator, sharing shrinkage with other physical-volatility specialists while retaining target and horizon distinctions.

**Fair comparison.** Aggregate YZ, GK/RS/close baselines, component-wise linear model and regularized interaction challenger.

**Evidence.** Formula/component parity, future variance/tail proper loss, calendar stability and incremental ensemble/economic contribution.

**Additional local cases to implement.** Futures short maintenance gap versus cash overnight; roll gap; nontrading day; short sample; one jump dominates.

**Decision or system use.** Test whether opening and intraday components forecast different future behavior instead of hiding them in one combined value.

**Exact reviewed source clauses.** [DTM-A03](SOURCE_FINDINGS_AND_CONFLICTS.md:61), [JCV-A05](SOURCE_FINDINGS_AND_CONFLICTS.md:164), [CEX-06](SOURCE_FINDINGS_AND_CONFLICTS.md:188), [DRF-A12](SOURCE_FINDINGS_AND_CONFLICTS.md:453).

**Conversation upgrade lineage.** [JCV-A05](SOURCE_FINDINGS_AND_CONFLICTS.md:164), [CEX-06](SOURCE_FINDINGS_AND_CONFLICTS.md:188). Read the full rows and their original conversation references; [the recheck](CONVERSATION_RECHECK.md) preserves the exact unit/exception routes.

<a id="up-c11-yz_jump"></a>
#### C11.YZ_JUMP — Opening-jump-aware volatility

[Existing definition, target and P0–P7](experiments/C.md#c11-yz_jump) remain binding.

**Specific upgrade scope.** Retain opening, intraday and RS components separately and model their conditional memory/asymmetric responses.

**Local comparison.** Compare aggregate YZ with component lag models, common-target GK/RS controls and regularized interactions.

**Additional cases.** Cash overnight versus futures break; roll; sparse n; one opening shock.

<a id="up-c12"></a>
### UP-C12 — Multiscale realized variance and semivariance

Parent: [C12](components/CONTEXT.md); [local phases](experiments/C.md#c12); [definition refinement](SYSTEM_REFINEMENT.md#sr-c12). Upgrade role: `forecast`.

**Starting idea.** Sum squared sampled returns and call it volatility.

**Existing improvement path.** Multiple sampling grids, noise-robust variants and up/down semivariance.

**Remaining weakness.** Sampling choice and correlated estimator error can dominate incremental information; total RV hides signed temporal clustering.

**Further upgrade.** Build a measurement-error-aware multiscale RV/semivariance panel with quality/noise diagnostics, signed clustering and matched observation windows. Compare a good coarse-grid baseline, fixed multigrid combination and train-fitted reliability weighting; use components in common-horizon forecasts before complex encoders.

**Fair comparison.** Coarse RV, subsampling/pre-averaging variants, fixed blend, reliability-weighted panel and matched-lag predictor.

**Evidence.** Measurement stability, common-target QLIKE/proper loss, tail calibration, data-quality sensitivity and compute.

**Additional local cases to implement.** Bid/ask bounce; stale carry; sparse grid; jump at boundary; opposing signed bursts produce equal total RV.

**Decision or system use.** Separate genuine variation information from sampling artifacts and test which multiscale/directional components improve forecasts.

**Exact reviewed source clauses.** [DTM-A03](SOURCE_FINDINGS_AND_CONFLICTS.md:61), [JCV-A05](SOURCE_FINDINGS_AND_CONFLICTS.md:164), [CEX-06](SOURCE_FINDINGS_AND_CONFLICTS.md:188), [DRF-A12](SOURCE_FINDINGS_AND_CONFLICTS.md:453), [PIN008-01](SOURCE_FINDINGS_AND_CONFLICTS.md:824), [PIN009-01](SOURCE_FINDINGS_AND_CONFLICTS.md:825), [PIN009-02](SOURCE_FINDINGS_AND_CONFLICTS.md:826), [PIN017-01](SOURCE_FINDINGS_AND_CONFLICTS.md:872), [PIN017-02](SOURCE_FINDINGS_AND_CONFLICTS.md:873), [PIN017-03](SOURCE_FINDINGS_AND_CONFLICTS.md:874), [PIN017-04](SOURCE_FINDINGS_AND_CONFLICTS.md:875), [PIN033-01](SOURCE_FINDINGS_AND_CONFLICTS.md:917), [PIN033-02](SOURCE_FINDINGS_AND_CONFLICTS.md:918).

**Conversation upgrade lineage.** [CEX-06](SOURCE_FINDINGS_AND_CONFLICTS.md:188). Read the full rows and their original conversation references; [the recheck](CONVERSATION_RECHECK.md) preserves the exact unit/exception routes.

<a id="up-c12-noise"></a>
#### C12.NOISE — Sampling and microstructure noise

[Existing definition, target and P0–P7](experiments/C.md#c12-noise) remain binding.

**Specific upgrade scope.** Use a multigrid quality/error panel and compare fixed versus train-fitted reliability weighting against a strong coarse-grid baseline.

**Local comparison.** Measure incremental forecast information separately from noise reduction and runtime.

**Additional cases.** Bid/ask bounce; stale carry; sparse sampling; grid boundary jump.

<a id="up-c12-semivariance"></a>
#### C12.SEMIVARIANCE — Directional realized volatility

[Existing definition, target and P0–P7](experiments/C.md#c12-semivariance) remain binding.

**Specific upgrade scope.** Add signed clustering/order and scale-normalized up/down variation features to raw semivariance totals.

**Local comparison.** Compare total RV, separate signs, temporal signed summaries and identical-capacity forecasts.

**Additional cases.** Equal total opposite sign clustering; jump dominates one side; zero returns from outage.

<a id="up-c13"></a>
### UP-C13 — HAR and multiscale forward-volatility expert

Parent: [C13](components/CONTEXT.md); [local phases](experiments/C.md#c13); [definition refinement](SYSTEM_REFINEMENT.md#sr-c13). Upgrade role: `forecast`.

**Starting idea.** Extrapolate one recent volatility number.

**Existing improvement path.** Daily/weekly/monthly HAR, transforms, jump/semivariance inputs and richer common-target mixtures.

**Remaining weakness.** Fixed rectangular lag averages may approximate memory poorly, while flexible alternatives can win through extra inputs or tuning rather than better dynamics.

**Further upgrade.** Compare HAR, HAR-J/semivariance variants, regularized smooth distributed lags and an explicitly specified ARFIMA-on-log-variance long-memory challenger. Preserve the user's spoken HAR/ARFI upgrade path; ARFIMA is a proposed operational interpretation, not an asserted source formula. Register memory order, stationarity/domain, initialization, retransformation and matched information/tuning budgets; retain every estimator's individual contribution in G02.

**Fair comparison.** Persistence/EWMA, source HAR variants, smooth lag basis, ARFIMA challenger and compact nonlinear model under separate information/capacity comparisons.

**Evidence.** Common-target QLIKE/proper loss, tail/interval calibration, memory stability, inference cost and incremental ensemble/net value.

**Additional local cases to implement.** Log-zero handling; mean-log retransformation bias; long-memory fit near boundary; structural break; future lag average.

**Decision or system use.** Test how much temporal memory and richer dynamics improve forward volatility, without conflating the estimator collection with the forecasting model.

**Exact reviewed source clauses.** [DTM-A03](SOURCE_FINDINGS_AND_CONFLICTS.md:61), [JCV-A05](SOURCE_FINDINGS_AND_CONFLICTS.md:164), [CEX-06](SOURCE_FINDINGS_AND_CONFLICTS.md:188), [DRF-A12](SOURCE_FINDINGS_AND_CONFLICTS.md:453).

**Conversation upgrade lineage.** [DTM-A03](SOURCE_FINDINGS_AND_CONFLICTS.md:61), [JCV-A05](SOURCE_FINDINGS_AND_CONFLICTS.md:164), [CEX-06](SOURCE_FINDINGS_AND_CONFLICTS.md:188). Read the full rows and their original conversation references; [the recheck](CONVERSATION_RECHECK.md) preserves the exact unit/exception routes.

<a id="up-c13-har_variants"></a>
#### C13.HAR_VARIANTS — Multiscale forward-volatility models

[Existing definition, target and P0–P7](experiments/C.md#c13-har_variants) remain binding.

**Specific upgrade scope.** Retain HAR/J/semivariance and transform variants, then compare smooth distributed lags and explicitly specified ARFIMA-on-log-variance as the proposed HAR/ARFI interpretation.

**Local comparison.** Separate memory/model changes from added estimator/IV information, match tuning and verify retransformation/calibration.

**Additional cases.** Stationarity boundary; log zero; mean-log bias; structural break; future lag averaging.

<a id="up-c14"></a>
### UP-C14 — Jump, discontinuity and burst-volatility expert

Parent: [C14](components/CONTEXT.md); [local phases](experiments/C.md#c14); [definition refinement](SYSTEM_REFINEMENT.md#sr-c14). Upgrade role: `forecast`.

**Starting idea.** Mark large returns as jumps or volatility bursts.

**Existing improvement path.** Continuous/discontinuous proxies, local thresholds, event hazards and post-burst decay.

**Remaining weakness.** One jump statistic loses sign, clustering, duration and uncertainty about whether microstructure produced the event.

**Further upgrade.** Build a probabilistic discontinuity/burst feature panel with signed jump size, clustering, contemporaneous flow/liquidity and decay trajectories, preserving deterministic threshold/BV comparators. Compare additive jump-augmented forecasts with a compact marked-event transition model; quality artifacts remain a separate input class.

**Fair comparison.** Large-return threshold, RV/BV proxy, jump-augmented HAR and conditional burst/decay model.

**Evidence.** Event/tail/time proper loss, decay calibration, noise robustness and incremental path/value contribution.

**Additional local cases to implement.** Bid/ask bounce; clustered jumps; opening gap; return after outage; prolonged burst differs from isolated jump.

**Decision or system use.** Forecast the consequences and persistence of unusual movement rather than treating all large returns as the same event.

**Exact reviewed source clauses.** [DTM-A03](SOURCE_FINDINGS_AND_CONFLICTS.md:61), [JCV-A05](SOURCE_FINDINGS_AND_CONFLICTS.md:164), [CEX-06](SOURCE_FINDINGS_AND_CONFLICTS.md:188), [DRF-A12](SOURCE_FINDINGS_AND_CONFLICTS.md:453).

**Conversation upgrade lineage.** [JCV-A05](SOURCE_FINDINGS_AND_CONFLICTS.md:164). Read the full rows and their original conversation references; [the recheck](CONVERSATION_RECHECK.md) preserves the exact unit/exception routes.

<a id="up-c14-jump_split"></a>
#### C14.JUMP_SPLIT — Continuous versus discontinuous risk

[Existing definition, target and P0–P7](experiments/C.md#c14-jump_split) remain binding.

**Specific upgrade scope.** Add signed jump size, clustering and conditional post-burst decay while preserving deterministic BV/threshold proxies.

**Local comparison.** Compare simple jump-augmented forecasts and bounded marked-event transition models with quality artifacts separate.

**Additional cases.** Opening discontinuity; microstructure noise; sustained burst versus isolated jump; outage return.

<a id="up-c15"></a>
### UP-C15 — Implied-volatility, skew and term-structure forecast specialist

Parent: [C15](components/CONTEXT.md); [local phases](experiments/C.md#c15); [definition refinement](SYSTEM_REFINEMENT.md#sr-c15). Upgrade role: `forecast`.

**Starting idea.** Use ATM IV or one skew number as the volatility input.

**Existing improvement path.** Full supported smile/skew/curvature, total/forward/event variance, variance-gap, surface-change, leverage, 0DTE and cross-IV children.

**Remaining weakness.** A rich feature list can be redundant and still miss coherent surface innovations and their changing relation to physical outcomes.

**Further upgrade.** Add a low-rank functional representation of supported strike/tenor surfaces and innovations after mechanical spot/time movement, retaining observed uncertainty. Compare interpretable factors, residual nonlinear terms and a joint price/surface-shock law; bridge to physical variance/tails using chronological forecasts, with each existing child independently ablated and both primitive C15.SCENARIO and later physical ports kept acyclic.

**Fair comparison.** ATM-only, all existing engineered child features, regularized functional factors, factor-plus-residual and joint shock challengers.

**Evidence.** Own-surface and physical proper loss by target, conditional tails, support/arbitrage diagnostics, child contribution and downstream net.

**Additional local cases to implement.** Missing wing; sparse 0DTE; tenor event crossing; same IV different remaining trading time; correlated surface uncertainty; changing variance premium.

**Decision or system use.** Upgrade the entire implied-information family through coherent representation and forecast relationships, preserving each distinct source feature and its limits.

**Exact reviewed source clauses.** [CEX-06](SOURCE_FINDINGS_AND_CONFLICTS.md:188), [CEX-09](SOURCE_FINDINGS_AND_CONFLICTS.md:191), [CRL-05](SOURCE_FINDINGS_AND_CONFLICTS.md:221), [VX4-01](SOURCE_FINDINGS_AND_CONFLICTS.md:324), [VX4-02](SOURCE_FINDINGS_AND_CONFLICTS.md:325), [VX4-03](SOURCE_FINDINGS_AND_CONFLICTS.md:326), [VX4-04](SOURCE_FINDINGS_AND_CONFLICTS.md:327), [VX4-05](SOURCE_FINDINGS_AND_CONFLICTS.md:328), [VX4-06](SOURCE_FINDINGS_AND_CONFLICTS.md:329), [VX4-07](SOURCE_FINDINGS_AND_CONFLICTS.md:330), [VX4-08](SOURCE_FINDINGS_AND_CONFLICTS.md:331), [VX4-09](SOURCE_FINDINGS_AND_CONFLICTS.md:332), [DRF-U04](SOURCE_FINDINGS_AND_CONFLICTS.md:428), [DRF-A12](SOURCE_FINDINGS_AND_CONFLICTS.md:453), [DRF-A13](SOURCE_FINDINGS_AND_CONFLICTS.md:454), [GXF-01](SOURCE_FINDINGS_AND_CONFLICTS.md:485), [GXF-02](SOURCE_FINDINGS_AND_CONFLICTS.md:486), [GXF-03](SOURCE_FINDINGS_AND_CONFLICTS.md:487), [GXF-04](SOURCE_FINDINGS_AND_CONFLICTS.md:488), [GXF-05](SOURCE_FINDINGS_AND_CONFLICTS.md:489), [GXF-06](SOURCE_FINDINGS_AND_CONFLICTS.md:490), [GXF-07](SOURCE_FINDINGS_AND_CONFLICTS.md:491), [GXF-08](SOURCE_FINDINGS_AND_CONFLICTS.md:492), [GXF-09](SOURCE_FINDINGS_AND_CONFLICTS.md:493), [GXF-10](SOURCE_FINDINGS_AND_CONFLICTS.md:494), [GXF-11](SOURCE_FINDINGS_AND_CONFLICTS.md:495), [GXF-12](SOURCE_FINDINGS_AND_CONFLICTS.md:496), [GXF-13](SOURCE_FINDINGS_AND_CONFLICTS.md:497), [PIN018-01](SOURCE_FINDINGS_AND_CONFLICTS.md:876), [PIN018-02](SOURCE_FINDINGS_AND_CONFLICTS.md:877).

**Conversation upgrade lineage.** [DTM-A03](SOURCE_FINDINGS_AND_CONFLICTS.md:61), [CEX-06](SOURCE_FINDINGS_AND_CONFLICTS.md:188), [CEX-11](SOURCE_FINDINGS_AND_CONFLICTS.md:193), [CRL-05](SOURCE_FINDINGS_AND_CONFLICTS.md:221), [DRF-U04](SOURCE_FINDINGS_AND_CONFLICTS.md:428), [DRF-A06](SOURCE_FINDINGS_AND_CONFLICTS.md:447), [DRF-A12](SOURCE_FINDINGS_AND_CONFLICTS.md:453), [DRF-A13](SOURCE_FINDINGS_AND_CONFLICTS.md:454), [DRF-A15](SOURCE_FINDINGS_AND_CONFLICTS.md:456), [DRF-A17](SOURCE_FINDINGS_AND_CONFLICTS.md:458). Read the full rows and their original conversation references; [the recheck](CONVERSATION_RECHECK.md) preserves the exact unit/exception routes.

<a id="up-c15-atm"></a>
#### C15.ATM — ATM implied variance bridge

[Existing definition, target and P0–P7](experiments/C.md#c15-atm) remain binding.

**Specific upgrade scope.** Use supported fixed-tenor ATM total-variance level/change and residual factors relative to physical/seasonal forecasts.

**Local comparison.** Compare ATM-only bridge, engineered term information and functional residual contribution at matched maturity.

**Additional cases.** Spot/forward ATM differs; expiry approaches zero; tenor interpolation gap; stale carry.

<a id="up-c15-cross_iv"></a>
#### C15.CROSS_IV — Cross-chain implied differences

[Existing definition, target and P0–P7](experiments/C.md#c15-cross_iv) remain binding.

**Specific upgrade scope.** Decompose common and chain-specific implied factors at compatible tenor/coordinate, with mapping and coverage uncertainty.

**Local comparison.** Compare single-chain, raw difference and residual cross-chain information under common support and equal model budget.

**Additional cases.** NDX/QQQ conventions; one chain stale; different settlement; common factor counted twice.

<a id="up-c15-curvature"></a>
#### C15.CURVATURE — Butterfly and asymmetric curvature

[Existing definition, target and P0–P7](experiments/C.md#c15-curvature) remain binding.

**Specific upgrade scope.** Add scale/tenor-aware symmetric and asymmetric curvature modes with quote-noise uncertainty.

**Local comparison.** Compare source butterfly/curvature scalars, robust local shape and functional residual basis, controlling for ATM/skew.

**Additional cases.** Sparse three-point curvature; wide wing spread; asymmetry; surface fit induces false precision.

<a id="up-c15-delta_skew"></a>
#### C15.DELTA_SKEW — Delta-convention skew

[Existing definition, target and P0–P7](experiments/C.md#c15-delta_skew) remain binding.

**Specific upgrade scope.** Separate delta-convention geometry, skew level and innovations after mechanical spot/time movement.

**Local comparison.** Compare exact fixed-delta/fixed-moneyness features and residual skew factors with side-tail targets and uncertainty.

**Additional cases.** Delta convention changes; skew point outside support; sign orientation; same nominal delta different tenor.

<a id="up-c15-event"></a>
#### C15.EVENT — Event variance concentration

[Existing definition, target and P0–P7](experiments/C.md#c15-event) remain binding.

**Specific upgrade scope.** Separate supported event-localized implied variance shape from ordinary term slope and its physical bridge.

**Local comparison.** Compare calendar-only, term-only, event concentration and residual interactions with matched event/horizon support.

**Additional cases.** Multiple events in bucket; expiry before release; event cancellation; assumed variance allocation not identified.

<a id="up-c15-intraday"></a>
#### C15.INTRADAY — Surface changes and dynamics

[Existing definition, target and P0–P7](experiments/C.md#c15-intraday) remain binding.

**Specific upgrade scope.** Factor surface changes into expected mechanical evolution and fresh curve innovations with causal temporal uncertainty.

**Local comparison.** Compare snapshots, raw changes, functional innovations and compact state dynamics for own-surface and physical targets.

**Additional cases.** Repeated snapshots; update cadence; abrupt missing support; same surface different quote errors.

<a id="up-c15-leverage"></a>
#### C15.LEVERAGE — Joint price and surface shocks

[Existing definition, target and P0–P7](experiments/C.md#c15-leverage) remain binding.

**Specific upgrade scope.** Model supported joint price/surface shocks with factor/residual structure and preserve the early C15.SCENARIO port's allowed inputs.

**Local comparison.** Compare independent/sticky conventions, empirical joint shocks and conditional law; later physical heads stay downstream and separately scored.

**Additional cases.** Current O22/X06 feedback; near-expiry nonlinear shock; correlated strike errors; delayed surface.

<a id="up-c15-modelfree"></a>
#### C15.MODELFREE — Observed option-strip variance

[Existing definition, target and P0–P7](experiments/C.md#c15-modelfree) remain binding.

**Specific upgrade scope.** Retain the supported option-strip integral and add observed-domain contribution/wing-assumption sensitivity rather than a falsely complete scalar.

**Local comparison.** Compare ATM/surface features, observed-strip contributions and declared tail scenarios with exact methodology eligibility.

**Additional cases.** Missing wing; no reliable forward; option style incompatible; sparse strikes; extrapolated tail dominates.

<a id="up-c15-smile"></a>
#### C15.SMILE — Full supported smile information

[Existing definition, target and P0–P7](experiments/C.md#c15-smile) remain binding.

**Specific upgrade scope.** Represent the full observed smile by interpretable shape factors plus constrained residuals instead of isolated wing points.

**Local comparison.** Compare ATM, engineered smile and functional curve representations at identical strike support and forecast targets.

**Additional cases.** Missing wing; smile changes with spot; sparse strikes; extrapolation mistaken for observation.

<a id="up-c15-term"></a>
#### C15.TERM — Total and forward implied-variance buckets

[Existing definition, target and P0–P7](experiments/C.md#c15-term) remain binding.

**Specific upgrade scope.** Model the curve of total variance and admissible forward buckets as coherent functions, preserving each exact horizon capability.

**Local comparison.** Compare point slopes, bucket features and low-rank curve/innovation factors against physical future targets.

**Additional cases.** Calendar crossing event; negative noisy bucket; equal calendar DTE unequal trading time; missing tenor.

<a id="up-c15-vrp"></a>
#### C15.VRP — Forward variance gap

[Existing definition, target and P0–P7](experiments/C.md#c15-vrp) remain binding.

**Specific upgrade scope.** Compare descriptive IV-minus-lagged-RV with a same-horizon OOF physical variance-gap forecast and its conditional dynamics.

**Local comparison.** Keep forward forecast uncertainty/correlation and target convention explicit; test added gap information beyond both inputs separately.

**Additional cases.** Physical forecast in-sample; units differ; residual premium versus forecast error; common shock.

<a id="up-c15-zero_dte"></a>
#### C15.ZERO_DTE — Settlement-remainder IV specialists

[Existing definition, target and P0–P7](experiments/C.md#c15-zero_dte) remain binding.

**Specific upgrade scope.** Use actual settlement remainder, support and nonlinear price/surface sensitivity in separate short-horizon forecasts.

**Local comparison.** Compare naive same-DTE scaling, engineered remainder features and factor/residual model under strict weak-IV-identification rules.

**Additional cases.** AM versus PM settlement; minutes left; intrinsic-only price; event before expiry; missing wing.

<a id="up-c16"></a>
### UP-C16 — VX, volatility-complex and cross-market stress expert

Parent: [C16](components/CONTEXT.md); [local phases](experiments/C.md#c16); [definition refinement](SYSTEM_REFINEMENT.md#sr-c16). Upgrade role: `forecast`.

**Starting idea.** Use VIX/VX level or curve slope as a stress flag.

**Existing improvement path.** Separate VIX-option forward/surface/VVIX, daily VX curve, joint stress and native VX-option branches.

**Remaining weakness.** Static levels miss whether stress reflects forward level, tail repricing, volatility-of-volatility or a change in cross-market coupling.

**Further upgrade.** Build a decomposed stress-state trajectory from independently supported forward, term, tail and vol-of-vol innovations, with common uncertainty and event clocks. Compare additive receiver-tail forecasts with low-rank joint dynamics and conditional spillover kernels; native VX options remain independently data-gated and are never replaced by OHLC-derived IV.

**Fair comparison.** Equity RV only, primitive volatility-complex signals, existing joint stress, decomposed innovations and compact joint dynamics.

**Evidence.** Own-source and receiver-tail proper loss, stress lead time, calibration, redundancy and constrained net contribution.

**Additional local cases to implement.** Daily VX appears repeated intraday; right wing absent; parity forward uncertain; source stress without receiver move; option-on-VX distinct from VIX option.

**Decision or system use.** Determine which parts of the full volatility complex add fresh information and at what horizon.

**Exact reviewed source clauses.** [CEX-11](SOURCE_FINDINGS_AND_CONFLICTS.md:193), [CEX-25](SOURCE_FINDINGS_AND_CONFLICTS.md:207), [CRL-05](SOURCE_FINDINGS_AND_CONFLICTS.md:221), [VX4-01](SOURCE_FINDINGS_AND_CONFLICTS.md:324), [VX4-02](SOURCE_FINDINGS_AND_CONFLICTS.md:325), [VX4-03](SOURCE_FINDINGS_AND_CONFLICTS.md:326), [VX4-04](SOURCE_FINDINGS_AND_CONFLICTS.md:327), [VX4-05](SOURCE_FINDINGS_AND_CONFLICTS.md:328), [VX4-06](SOURCE_FINDINGS_AND_CONFLICTS.md:329), [VX4-07](SOURCE_FINDINGS_AND_CONFLICTS.md:330), [VX4-08](SOURCE_FINDINGS_AND_CONFLICTS.md:331), [VX4-09](SOURCE_FINDINGS_AND_CONFLICTS.md:332), [DRF-A12](SOURCE_FINDINGS_AND_CONFLICTS.md:453), [GXF-01](SOURCE_FINDINGS_AND_CONFLICTS.md:485), [GXF-02](SOURCE_FINDINGS_AND_CONFLICTS.md:486), [GXF-03](SOURCE_FINDINGS_AND_CONFLICTS.md:487), [GXF-04](SOURCE_FINDINGS_AND_CONFLICTS.md:488), [GXF-05](SOURCE_FINDINGS_AND_CONFLICTS.md:489), [GXF-06](SOURCE_FINDINGS_AND_CONFLICTS.md:490), [GXF-07](SOURCE_FINDINGS_AND_CONFLICTS.md:491), [GXF-08](SOURCE_FINDINGS_AND_CONFLICTS.md:492), [GXF-09](SOURCE_FINDINGS_AND_CONFLICTS.md:493), [GXF-10](SOURCE_FINDINGS_AND_CONFLICTS.md:494), [GXF-11](SOURCE_FINDINGS_AND_CONFLICTS.md:495), [GXF-12](SOURCE_FINDINGS_AND_CONFLICTS.md:496), [GXF-13](SOURCE_FINDINGS_AND_CONFLICTS.md:497), [PIN018-01](SOURCE_FINDINGS_AND_CONFLICTS.md:876), [PIN018-02](SOURCE_FINDINGS_AND_CONFLICTS.md:877).

**Conversation upgrade lineage.** [CEX-11](SOURCE_FINDINGS_AND_CONFLICTS.md:193), [CEX-25](SOURCE_FINDINGS_AND_CONFLICTS.md:207), [CRL-05](SOURCE_FINDINGS_AND_CONFLICTS.md:221). Read the full rows and their original conversation references; [the recheck](CONVERSATION_RECHECK.md) preserves the exact unit/exception routes.

<a id="up-c16-forward"></a>
#### C16.FORWARD — Intraday VIX option-implied forward

[Existing definition, target and P0–P7](experiments/C.md#c16-forward) remain binding.

**Specific upgrade scope.** Track VIX-option-implied forward level and innovations separately from any observed cash-index or VX price.

**Local comparison.** Compare parity/eligible valuation scenarios, temporal forward residuals and receiver forecasts with uncertainty intact.

**Additional cases.** Wide parity interval; rate scenario; missing paired strikes; no observed cash touch.

<a id="up-c16-joint_stress"></a>
#### C16.JOINT_STRESS — Joint volatility-complex stress

[Existing definition, target and P0–P7](experiments/C.md#c16-joint_stress) remain binding.

**Specific upgrade scope.** Combine primitive forward, tail, term and vol-of-vol innovations with sparse common/residual dynamics.

**Local comparison.** Compare additive stress and joint model under common information, preserving acyclic primitive inputs and contribution of each child.

**Additional cases.** No current X06 loop; common shock; missing wing; stress without receiver response.

<a id="up-c16-vix_surface"></a>
#### C16.VIX_SURFACE — VIX-option smile and right tail

[Existing definition, target and P0–P7](experiments/C.md#c16-vix_surface) remain binding.

**Specific upgrade scope.** Add functional right-tail/smile innovations and support-aware factor dynamics to the independently built VIX option surface.

**Local comparison.** Compare forward/ATM only, engineered tail features and compact surface representation with own-source and receiver targets separate.

**Additional cases.** Sparse right wing; poor IV conditioning; quote support changes; shape fit hides uncertainty.

<a id="up-c16-vvix"></a>
#### C16.VVIX — Intraday implied volatility of volatility

[Existing definition, target and P0–P7](experiments/C.md#c16-vvix) remain binding.

**Specific upgrade scope.** Decompose supported vol-of-vol information into level/change/tail innovations and distinguish internal measure from official-method replication.

**Local comparison.** Compare VIX forward/smile without VVIX, internal measure and residual contribution at matched support.

**Additional cases.** Methodology mismatch; wing truncation; common surface errors; daily versus intraday input.

<a id="up-c16-vx_curve"></a>
#### C16.VX_CURVE — Daily VX maturity structure

[Existing definition, target and P0–P7](experiments/C.md#c16-vx_curve) remain binding.

**Specific upgrade scope.** Separate curve level/slope/roll and event-related innovations on the actual daily publication clock.

**Local comparison.** Compare raw front/second signals and maturity/carry-aware residual factors; no duplicated intraday rows as independent evidence.

**Additional cases.** Roll jump; stale daily value; maturity gap; quote vintage.

<a id="up-c16-vx_options"></a>
#### C16.VX_OPTIONS — Distinct options on VX futures

[Existing definition, target and P0–P7](experiments/C.md#c16-vx_options) remain binding.

**Specific upgrade scope.** Maintain a separately eligible native options-on-VX branch with style/underlier/quote-specific valuation and flow information.

**Local comparison.** Compare no branch, supported native flow/settlement, and quoted/sensitivity features only if actually available.

**Additional cases.** VIX option mistaken for VX option; underlying expiry mismatch; no quotes; unsupported IV.

<a id="up-c17"></a>
### UP-C17 — Scheduled events, announcements and publication state

Parent: [C17](components/CONTEXT.md); [local phases](experiments/C.md#c17); [definition refinement](SYSTEM_REFINEMENT.md#sr-c17). Upgrade role: `forecast`.

**Starting idea.** Use a weekday or news-time avoid/trade rule.

**Existing improvement path.** Known-calendar anticipation, actual observed release/reaction and post-event decay are separate.

**Remaining weakness.** Broad event bins pool different phase, surprise availability and overlapping events, obscuring when risk actually changes.

**Further upgrade.** Fit event-family time kernels for anticipation, release response and decay, partially pooling sparse events and preserving exact publication vintages. Model overlapping-event interactions only with support; compare calendar-only, observed reaction and eligible surprise features at their actual cuts, using horizon intersections with event time.

**Fair comparison.** Source calendar rules, pooled bins, partially pooled event-time kernels and supported interaction/surprise challengers.

**Evidence.** Event-tail/time proper loss, uncertainty by independent release, pre/post value and waiting/flatten cost.

**Additional local cases to implement.** Two releases overlap; delayed release; press conference follows statement; consensus vintage absent; horizon straddles event.

**Decision or system use.** Use the timing and type of known and observed events to forecast changing opportunity and risk with explicit information availability.

**Exact reviewed source clauses.** [JTR-09](SOURCE_FINDINGS_AND_CONFLICTS.md:26), [JTR-13](SOURCE_FINDINGS_AND_CONFLICTS.md:30), [JTR-14](SOURCE_FINDINGS_AND_CONFLICTS.md:31), [DTM-A09](SOURCE_FINDINGS_AND_CONFLICTS.md:67), [JXA-17](SOURCE_FINDINGS_AND_CONFLICTS.md:116), [JXA-25](SOURCE_FINDINGS_AND_CONFLICTS.md:124), [JFN-09](SOURCE_FINDINGS_AND_CONFLICTS.md:143), [JCV-A05](SOURCE_FINDINGS_AND_CONFLICTS.md:164), [CEX-25](SOURCE_FINDINGS_AND_CONFLICTS.md:207), [CRL-10](SOURCE_FINDINGS_AND_CONFLICTS.md:226), [VX4-07](SOURCE_FINDINGS_AND_CONFLICTS.md:330), [DEN-04](SOURCE_FINDINGS_AND_CONFLICTS.md:412), [GXF-05](SOURCE_FINDINGS_AND_CONFLICTS.md:489), [GXF-08](SOURCE_FINDINGS_AND_CONFLICTS.md:492), [PIN003-01](SOURCE_FINDINGS_AND_CONFLICTS.md:819), [PIN003-02](SOURCE_FINDINGS_AND_CONFLICTS.md:820), [PIN003-03](SOURCE_FINDINGS_AND_CONFLICTS.md:821), [PIN003-04](SOURCE_FINDINGS_AND_CONFLICTS.md:822), [PIN004-01](SOURCE_FINDINGS_AND_CONFLICTS.md:823).

**Conversation upgrade lineage.** [DTM-A09](SOURCE_FINDINGS_AND_CONFLICTS.md:67), [CRL-10](SOURCE_FINDINGS_AND_CONFLICTS.md:226). Read the full rows and their original conversation references; [the recheck](CONVERSATION_RECHECK.md) preserves the exact unit/exception routes.

<a id="up-c17-pre_post_event"></a>
#### C17.PRE_POST_EVENT — Known calendar and observed response

[Existing definition, target and P0–P7](experiments/C.md#c17-pre_post_event) remain binding.

**Specific upgrade scope.** Use partially pooled event-time kernels for anticipation, actual reaction and decay, with eligible surprise vintages separate.

**Local comparison.** Compare calendar, observed response and supported surprise at actual cuts; price confirmation delay and overlapping events.

**Additional cases.** Release late; press conference follows statement; consensus absent; horizon straddles event.

<a id="up-c18"></a>
### UP-C18 — Participation, control and effort-progress forecast specialists

Parent: [C18](components/CONTEXT.md); [local phases](experiments/C.md#c18); [definition refinement](SYSTEM_REFINEMENT.md#sr-c18). Upgrade role: `forecast`.

**Starting idea.** Treat CVD direction or tape speed as control.

**Existing improvement path.** Independent continuation, failed-effort, persistence, participation and cohort-disagreement heads.

**Remaining weakness.** Separate scalars can miss nonlinear coupling between expected flow, price response, cohort breadth and book resilience.

**Further upgrade.** Use M01–M13 residual pressure/progress and multiscale state to fit a compact joint marked-flow/price transition representation, with separate named output heads. Compare additive/interactions before sequence models, and test raw versus residual, ordinary versus cohort, close versus true OHLC and trade versus quote information independently.

**Fair comparison.** Source CVD/OFI rules, simple joint features, residual interaction model and compact sequence challenger.

**Evidence.** Per-head proper loss, temporal lead/lag calibration, family interaction value, complete net and latency.

**Additional local cases to implement.** Large flow is expected; price moves without aggression; cohorts disagree; unknown signs; same final delta different path.

**Decision or system use.** Upgrade participation/control prediction through measured interactions while keeping every mechanism and information contribution reviewable.

**Exact reviewed source clauses.** [DTM-A10](SOURCE_FINDINGS_AND_CONFLICTS.md:68), [CEX-05](SOURCE_FINDINGS_AND_CONFLICTS.md:187), [CRL-11](SOURCE_FINDINGS_AND_CONFLICTS.md:227), [CRL-18](SOURCE_FINDINGS_AND_CONFLICTS.md:234), [CD3-01](SOURCE_FINDINGS_AND_CONFLICTS.md:404), [CD3-02](SOURCE_FINDINGS_AND_CONFLICTS.md:405), [CD3-03](SOURCE_FINDINGS_AND_CONFLICTS.md:406), [CD3-04](SOURCE_FINDINGS_AND_CONFLICTS.md:407), [CD3-05](SOURCE_FINDINGS_AND_CONFLICTS.md:408), [MAV-07](SOURCE_FINDINGS_AND_CONFLICTS.md:511), [MAT-02](SOURCE_FINDINGS_AND_CONFLICTS.md:527), [WIC-01](SOURCE_FINDINGS_AND_CONFLICTS.md:577), [WIC-02](SOURCE_FINDINGS_AND_CONFLICTS.md:578), [WIC-03](SOURCE_FINDINGS_AND_CONFLICTS.md:579), [WIC-04](SOURCE_FINDINGS_AND_CONFLICTS.md:580), [WIC-05](SOURCE_FINDINGS_AND_CONFLICTS.md:581), [WIC-06](SOURCE_FINDINGS_AND_CONFLICTS.md:582), [WIC-07](SOURCE_FINDINGS_AND_CONFLICTS.md:583), [MVF-01](SOURCE_FINDINGS_AND_CONFLICTS.md:783), [MVF-02](SOURCE_FINDINGS_AND_CONFLICTS.md:784), [MVF-03](SOURCE_FINDINGS_AND_CONFLICTS.md:785), [MVF-04](SOURCE_FINDINGS_AND_CONFLICTS.md:786), [MVF-05](SOURCE_FINDINGS_AND_CONFLICTS.md:787), [MVF-06](SOURCE_FINDINGS_AND_CONFLICTS.md:788), [MVF-07](SOURCE_FINDINGS_AND_CONFLICTS.md:789), [PIN008-01](SOURCE_FINDINGS_AND_CONFLICTS.md:824), [PIN009-01](SOURCE_FINDINGS_AND_CONFLICTS.md:825), [PIN009-02](SOURCE_FINDINGS_AND_CONFLICTS.md:826), [PIN011-01](SOURCE_FINDINGS_AND_CONFLICTS.md:845), [PIN011-02](SOURCE_FINDINGS_AND_CONFLICTS.md:846), [PIN011-03](SOURCE_FINDINGS_AND_CONFLICTS.md:847), [PIN011-04](SOURCE_FINDINGS_AND_CONFLICTS.md:848), [PIN011-05](SOURCE_FINDINGS_AND_CONFLICTS.md:849), [PIN011-06](SOURCE_FINDINGS_AND_CONFLICTS.md:850), [PIN011-07](SOURCE_FINDINGS_AND_CONFLICTS.md:851), [PIN017-01](SOURCE_FINDINGS_AND_CONFLICTS.md:872), [PIN017-02](SOURCE_FINDINGS_AND_CONFLICTS.md:873), [PIN017-03](SOURCE_FINDINGS_AND_CONFLICTS.md:874), [PIN017-04](SOURCE_FINDINGS_AND_CONFLICTS.md:875), [PIN020-01](SOURCE_FINDINGS_AND_CONFLICTS.md:890), [PIN020-02](SOURCE_FINDINGS_AND_CONFLICTS.md:891), [PIN033-01](SOURCE_FINDINGS_AND_CONFLICTS.md:917), [PIN033-02](SOURCE_FINDINGS_AND_CONFLICTS.md:918), [PIN034-01](SOURCE_FINDINGS_AND_CONFLICTS.md:919), [PIN050-01](SOURCE_FINDINGS_AND_CONFLICTS.md:968), [PIN050-02](SOURCE_FINDINGS_AND_CONFLICTS.md:969), [PIN050-03](SOURCE_FINDINGS_AND_CONFLICTS.md:970), [PIN072-01](SOURCE_FINDINGS_AND_CONFLICTS.md:1045), [PIN072-02](SOURCE_FINDINGS_AND_CONFLICTS.md:1046), [PIN079-01](SOURCE_FINDINGS_AND_CONFLICTS.md:1066), [PIN079-02](SOURCE_FINDINGS_AND_CONFLICTS.md:1067), [PIN079-03](SOURCE_FINDINGS_AND_CONFLICTS.md:1068), [PIN079-04](SOURCE_FINDINGS_AND_CONFLICTS.md:1069).

**Conversation upgrade lineage.** [DTM-A10](SOURCE_FINDINGS_AND_CONFLICTS.md:68). Read the full rows and their original conversation references; [the recheck](CONVERSATION_RECHECK.md) preserves the exact unit/exception routes.

<a id="up-c18-control"></a>
#### C18.CONTROL — Independent participation/control experts

[Existing definition, target and P0–P7](experiments/C.md#c18-control) remain binding.

**Specific upgrade scope.** Fit joint residual pressure/progress transitions with separate continuation, failure, persistence, expansion and cohort heads.

**Local comparison.** Compare raw/residual, ordinary/cohort, close/OHLC and trade/quote information independently before sequence complexity.

**Additional cases.** Expected large flow; quote-led move; same final delta different path; unknown side; contradictory cohorts.

<a id="up-c19"></a>
### UP-C19 — Remaining-session movement and opportunity budget

Parent: [C19](components/CONTEXT.md); [local phases](experiments/C.md#c19); [definition refinement](SYSTEM_REFINEMENT.md#sr-c19). Upgrade role: `forecast`.

**Starting idea.** Subtract used range from ADR to estimate remaining fuel.

**Existing improvement path.** Prefix-conditioned remaining extrema/time distributions truncated at the true boundary.

**Remaining weakness.** A single room number misses asymmetric path possibilities, conditional expansion and how soon movement can occur.

**Further upgrade.** Fit a coherent remaining-horizon surface over upward/downward travel, first passage and resolution time, conditioned on current price, realized prefix and state. Compare direct remainder models with a validated conditional full-path law; provide primitive movement/time outputs to G/P, which alone derive executable feasibility frontiers.

**Fair comparison.** Seasonal remainder, fixed ADR cap, direct conditional quantiles/hazards and coherent remaining-path model.

**Evidence.** Horizon/path proper loss, boundary calibration, expansion/quiet-state error and downstream wait/stop/target value.

**Additional local cases to implement.** Day exceeds prior range forecast; late fast opportunity; already travelled both sides; hard cutoff shortens horizon; variance high but signed payoff poor.

**Decision or system use.** Quantify remaining attainable movement and timing without imposing a spent-volatility ceiling or feeding current action values back into forecasts.

**Exact reviewed source clauses.** [JTR-04](SOURCE_FINDINGS_AND_CONFLICTS.md:21), [JTR-06](SOURCE_FINDINGS_AND_CONFLICTS.md:23), [JTR-12](SOURCE_FINDINGS_AND_CONFLICTS.md:29), [DTM-A10](SOURCE_FINDINGS_AND_CONFLICTS.md:68), [JXA-06](SOURCE_FINDINGS_AND_CONFLICTS.md:105), [JXA-12](SOURCE_FINDINGS_AND_CONFLICTS.md:111), [JXA-13](SOURCE_FINDINGS_AND_CONFLICTS.md:112), [JXA-17](SOURCE_FINDINGS_AND_CONFLICTS.md:116), [JXA-18](SOURCE_FINDINGS_AND_CONFLICTS.md:117), [JFN-09](SOURCE_FINDINGS_AND_CONFLICTS.md:143), [JCV-U03](SOURCE_FINDINGS_AND_CONFLICTS.md:156), [JCV-A08](SOURCE_FINDINGS_AND_CONFLICTS.md:167), [CEX-06](SOURCE_FINDINGS_AND_CONFLICTS.md:188), [VX4-05](SOURCE_FINDINGS_AND_CONFLICTS.md:328), [DRF-A05](SOURCE_FINDINGS_AND_CONFLICTS.md:446), [K10-02](SOURCE_FINDINGS_AND_CONFLICTS.md:640), [ALS-01](SOURCE_FINDINGS_AND_CONFLICTS.md:696), [ALS-02](SOURCE_FINDINGS_AND_CONFLICTS.md:697), [ALS-03](SOURCE_FINDINGS_AND_CONFLICTS.md:698), [ALS-04](SOURCE_FINDINGS_AND_CONFLICTS.md:699), [ALS-05](SOURCE_FINDINGS_AND_CONFLICTS.md:700), [ALS-06](SOURCE_FINDINGS_AND_CONFLICTS.md:701), [TBR-01](SOURCE_FINDINGS_AND_CONFLICTS.md:736), [TBR-02](SOURCE_FINDINGS_AND_CONFLICTS.md:737), [TBR-03](SOURCE_FINDINGS_AND_CONFLICTS.md:738), [TBR-04](SOURCE_FINDINGS_AND_CONFLICTS.md:739), [TBR-05](SOURCE_FINDINGS_AND_CONFLICTS.md:740), [TBR-06](SOURCE_FINDINGS_AND_CONFLICTS.md:741), [TBR-07](SOURCE_FINDINGS_AND_CONFLICTS.md:742), [PIN001-01](SOURCE_FINDINGS_AND_CONFLICTS.md:812), [PIN001-02](SOURCE_FINDINGS_AND_CONFLICTS.md:813), [PIN001-03](SOURCE_FINDINGS_AND_CONFLICTS.md:814), [PIN001-04](SOURCE_FINDINGS_AND_CONFLICTS.md:815), [PIN006-01](SOURCE_FINDINGS_AND_CONFLICTS.md:833), [PIN006-02](SOURCE_FINDINGS_AND_CONFLICTS.md:834), [PIN006-03](SOURCE_FINDINGS_AND_CONFLICTS.md:835), [PIN007-01](SOURCE_FINDINGS_AND_CONFLICTS.md:836), [PIN007-02](SOURCE_FINDINGS_AND_CONFLICTS.md:837), [PIN007-03](SOURCE_FINDINGS_AND_CONFLICTS.md:838), [PIN007-04](SOURCE_FINDINGS_AND_CONFLICTS.md:839), [PIN007-05](SOURCE_FINDINGS_AND_CONFLICTS.md:840), [PIN014-01](SOURCE_FINDINGS_AND_CONFLICTS.md:863), [PIN014-02](SOURCE_FINDINGS_AND_CONFLICTS.md:864), [PIN016-01](SOURCE_FINDINGS_AND_CONFLICTS.md:868), [PIN016-02](SOURCE_FINDINGS_AND_CONFLICTS.md:869), [PIN016-03](SOURCE_FINDINGS_AND_CONFLICTS.md:870), [PIN016-04](SOURCE_FINDINGS_AND_CONFLICTS.md:871), [PIN024-01](SOURCE_FINDINGS_AND_CONFLICTS.md:878), [PIN024-02](SOURCE_FINDINGS_AND_CONFLICTS.md:879), [PIN032-02](SOURCE_FINDINGS_AND_CONFLICTS.md:915), [PIN045-01](SOURCE_FINDINGS_AND_CONFLICTS.md:948), [PIN045-02](SOURCE_FINDINGS_AND_CONFLICTS.md:949), [PIN045-03](SOURCE_FINDINGS_AND_CONFLICTS.md:950), [PIN045-04](SOURCE_FINDINGS_AND_CONFLICTS.md:951), [PIN045-05](SOURCE_FINDINGS_AND_CONFLICTS.md:952), [PIN045-06](SOURCE_FINDINGS_AND_CONFLICTS.md:953), [PIN052-01](SOURCE_FINDINGS_AND_CONFLICTS.md:974), [PIN052-02](SOURCE_FINDINGS_AND_CONFLICTS.md:975), [PIN052-03](SOURCE_FINDINGS_AND_CONFLICTS.md:976), [PIN055-01](SOURCE_FINDINGS_AND_CONFLICTS.md:980), [PIN055-02](SOURCE_FINDINGS_AND_CONFLICTS.md:981), [PIN057-01](SOURCE_FINDINGS_AND_CONFLICTS.md:985), [PIN057-02](SOURCE_FINDINGS_AND_CONFLICTS.md:986), [PIN057-03](SOURCE_FINDINGS_AND_CONFLICTS.md:987), [PIN062-01](SOURCE_FINDINGS_AND_CONFLICTS.md:1001), [PIN062-02](SOURCE_FINDINGS_AND_CONFLICTS.md:1002), [PIN062-03](SOURCE_FINDINGS_AND_CONFLICTS.md:1003), [PIN063-01](SOURCE_FINDINGS_AND_CONFLICTS.md:1005), [PIN063-02](SOURCE_FINDINGS_AND_CONFLICTS.md:1006), [PIN063-03](SOURCE_FINDINGS_AND_CONFLICTS.md:1007), [PIN065-01](SOURCE_FINDINGS_AND_CONFLICTS.md:1012), [PIN065-02](SOURCE_FINDINGS_AND_CONFLICTS.md:1013), [PIN065-03](SOURCE_FINDINGS_AND_CONFLICTS.md:1014), [PIN067-01](SOURCE_FINDINGS_AND_CONFLICTS.md:1021), [PIN067-02](SOURCE_FINDINGS_AND_CONFLICTS.md:1022), [PIN068-01](SOURCE_FINDINGS_AND_CONFLICTS.md:1024), [PIN068-02](SOURCE_FINDINGS_AND_CONFLICTS.md:1025), [PIN068-03](SOURCE_FINDINGS_AND_CONFLICTS.md:1026), [PIN070-01](SOURCE_FINDINGS_AND_CONFLICTS.md:1033), [PIN070-02](SOURCE_FINDINGS_AND_CONFLICTS.md:1034), [PIN083-01](SOURCE_FINDINGS_AND_CONFLICTS.md:1084), [PIN083-02](SOURCE_FINDINGS_AND_CONFLICTS.md:1085).

**Conversation upgrade lineage.** [DTM-A10](SOURCE_FINDINGS_AND_CONFLICTS.md:68), [DRF-A20](SOURCE_FINDINGS_AND_CONFLICTS.md:461). Read the full rows and their original conversation references; [the recheck](CONVERSATION_RECHECK.md) preserves the exact unit/exception routes.

<a id="up-c19-remaining_room"></a>
#### C19.REMAINING_ROOM — Remaining movement and competing obstacles

[Existing definition, target and P0–P7](experiments/C.md#c19-remaining_room) remain binding.

**Specific upgrade scope.** Provide a coherent remaining U/D/time/order surface conditional on the observed prefix and mandatory boundary.

**Local comparison.** Compare seasonal, ADR-cap, direct remainder and valid conditional path models; economic feasibility stays in downstream G/P.

**Additional cases.** Already exceeded forecast; late fast move; high variance little net payoff; no remaining coverage.

<a id="up-c20"></a>
### UP-C20 — Regime and distribution-shift conditioning

Parent: [C20](components/CONTEXT.md); [local phases](experiments/C.md#c20); [definition refinement](SYSTEM_REFINEMENT.md#sr-c20). Upgrade role: `forecast`.

**Starting idea.** Name a day as trending, balanced or high volatility.

**Existing improvement path.** Continuous interpretable axes, causal filtered states and separate coverage drift.

**Remaining weakness.** Regime models may fit retrospective clusters that add no predictive information and can confuse gradual transitions with abrupt changes.

**Further upgrade.** Compare predictive state representations trained on next observable outcomes with descriptive regime fits, using a low-dimensional interpretable axis baseline and optional filtered latent residual state. Preserve posterior uncertainty, duration and drift; fit only chronological prefixes and distinguish representation changes from parameter adaptation.

**Fair comparison.** No regime, continuous axes, filtered HMM/HSMM/change point and predictive residual-state challenger.

**Evidence.** Downstream proper loss/net, state stability, transition delay, support and coverage-artifact sensitivity.

**Additional local cases to implement.** Mixed trend/balance evidence; abrupt source change; gradual market drift; rare state; future-smoothed label looks perfect.

**Decision or system use.** Use state conditioning only when it improves future decisions, with uncertainty and observable meaning retained.

**Exact reviewed source clauses.** [JXA-22](SOURCE_FINDINGS_AND_CONFLICTS.md:121), [JFN-05](SOURCE_FINDINGS_AND_CONFLICTS.md:139), [CEX-04](SOURCE_FINDINGS_AND_CONFLICTS.md:186), [CRL-08](SOURCE_FINDINGS_AND_CONFLICTS.md:224), [AM1-07](SOURCE_FINDINGS_AND_CONFLICTS.md:287), [AM1-10](SOURCE_FINDINGS_AND_CONFLICTS.md:290), [DEN-03](SOURCE_FINDINGS_AND_CONFLICTS.md:411), [GXF-05](SOURCE_FINDINGS_AND_CONFLICTS.md:489), [MAV-04](SOURCE_FINDINGS_AND_CONFLICTS.md:508), [MAT-05](SOURCE_FINDINGS_AND_CONFLICTS.md:530), [PIN008-01](SOURCE_FINDINGS_AND_CONFLICTS.md:824), [PIN009-01](SOURCE_FINDINGS_AND_CONFLICTS.md:825), [PIN009-02](SOURCE_FINDINGS_AND_CONFLICTS.md:826), [PIN011-01](SOURCE_FINDINGS_AND_CONFLICTS.md:845), [PIN011-02](SOURCE_FINDINGS_AND_CONFLICTS.md:846), [PIN011-03](SOURCE_FINDINGS_AND_CONFLICTS.md:847), [PIN011-04](SOURCE_FINDINGS_AND_CONFLICTS.md:848), [PIN011-05](SOURCE_FINDINGS_AND_CONFLICTS.md:849), [PIN011-06](SOURCE_FINDINGS_AND_CONFLICTS.md:850), [PIN011-07](SOURCE_FINDINGS_AND_CONFLICTS.md:851), [PIN017-01](SOURCE_FINDINGS_AND_CONFLICTS.md:872), [PIN017-02](SOURCE_FINDINGS_AND_CONFLICTS.md:873), [PIN017-03](SOURCE_FINDINGS_AND_CONFLICTS.md:874), [PIN017-04](SOURCE_FINDINGS_AND_CONFLICTS.md:875), [PIN019-01](SOURCE_FINDINGS_AND_CONFLICTS.md:887), [PIN019-02](SOURCE_FINDINGS_AND_CONFLICTS.md:888), [PIN019-03](SOURCE_FINDINGS_AND_CONFLICTS.md:889), [PIN020-01](SOURCE_FINDINGS_AND_CONFLICTS.md:890), [PIN020-02](SOURCE_FINDINGS_AND_CONFLICTS.md:891), [PIN033-01](SOURCE_FINDINGS_AND_CONFLICTS.md:917), [PIN033-02](SOURCE_FINDINGS_AND_CONFLICTS.md:918), [PIN034-01](SOURCE_FINDINGS_AND_CONFLICTS.md:919), [PIN035-03](SOURCE_FINDINGS_AND_CONFLICTS.md:922), [PIN050-01](SOURCE_FINDINGS_AND_CONFLICTS.md:968), [PIN050-02](SOURCE_FINDINGS_AND_CONFLICTS.md:969), [PIN050-03](SOURCE_FINDINGS_AND_CONFLICTS.md:970), [PIN072-01](SOURCE_FINDINGS_AND_CONFLICTS.md:1045), [PIN072-02](SOURCE_FINDINGS_AND_CONFLICTS.md:1046), [PIN079-01](SOURCE_FINDINGS_AND_CONFLICTS.md:1066), [PIN079-02](SOURCE_FINDINGS_AND_CONFLICTS.md:1067), [PIN079-03](SOURCE_FINDINGS_AND_CONFLICTS.md:1068), [PIN079-04](SOURCE_FINDINGS_AND_CONFLICTS.md:1069).

**Conversation upgrade lineage.** [JCV-U02](SOURCE_FINDINGS_AND_CONFLICTS.md:155), [JCV-A05](SOURCE_FINDINGS_AND_CONFLICTS.md:164), [JCV-A06](SOURCE_FINDINGS_AND_CONFLICTS.md:165), [JCV-A10](SOURCE_FINDINGS_AND_CONFLICTS.md:169), [CEX-04](SOURCE_FINDINGS_AND_CONFLICTS.md:186), [CEX-09](SOURCE_FINDINGS_AND_CONFLICTS.md:191), [CRL-02](SOURCE_FINDINGS_AND_CONFLICTS.md:218), [CRL-08](SOURCE_FINDINGS_AND_CONFLICTS.md:224). Read the full rows and their original conversation references; [the recheck](CONVERSATION_RECHECK.md) preserves the exact unit/exception routes.

<a id="up-c20-regime"></a>
#### C20.REGIME — Continuous state and filtered regimes

[Existing definition, target and P0–P7](experiments/C.md#c20-regime) remain binding.

**Specific upgrade scope.** Compare interpretable axes and uncertainty-aware predictive residual state with causal descriptive HMM/HSMM/change points.

**Local comparison.** Judge state by future forecast/decision increment, not retrospective cluster appearance; coverage state separate.

**Additional cases.** Future smoothing; mixed state; rare regime; feed acquisition change.

<a id="up-c20-reversion"></a>
#### C20.REVERSION — Observed reversion and expansion diagnostics

[Existing definition, target and P0–P7](experiments/C.md#c20-reversion) remain binding.

**Specific upgrade scope.** Use continuous reversion/expansion efficiency and duration features as distinct diagnostics within predictive state, not one Hurst-style rule.

**Local comparison.** Compare raw persistence/reversion measures with conditional residual relationships and support-aware interactions.

**Additional cases.** Short noisy window; trend with local pullback; jump; parameter selected after outcome.

<a id="up-c21"></a>
### UP-C21 — Session transition and time-dependent path expert

Parent: [C21](components/CONTEXT.md); [local phases](experiments/C.md#c21); [definition refinement](SYSTEM_REFINEMENT.md#sr-c21). Upgrade role: `forecast`.

**Starting idea.** Use a session-to-session hit table or AM/PM pattern.

**Existing improvement path.** Every source session/body/open/range target and exact ordered check window is retained.

**Remaining weakness.** A fixed session label loses how much of its typical activity/path has already occurred and how transitions depend on the prior session.

**Further upgrade.** Build duration- and activity-aware transition features on exact source clocks, using causal expected-activity phase rather than future total volume. Compare hierarchical pair-of-session models with pooled temporal kernels, preserving each reference/ordering target and including holiday/DST/overlap state.

**Fair comparison.** Source time-window tables, shrunken frequencies, exact-clock conditional model and activity-aware hierarchical transition model.

**Evidence.** Per-transition path/time calibration, seasonal/clock stability, independent date support and net contribution.

**Additional local cases to implement.** AM expansion followed by further expansion; overlap of global sessions; early close; body25 versus open-to-open target; partial current session.

**Decision or system use.** Improve the full session-transition family through richer observed phase and conditional relationships, without replacing exact source clocks.

**Exact reviewed source clauses.** [JTR-08](SOURCE_FINDINGS_AND_CONFLICTS.md:25), [JTR-09](SOURCE_FINDINGS_AND_CONFLICTS.md:26), [JTR-13](SOURCE_FINDINGS_AND_CONFLICTS.md:30), [JTR-23](SOURCE_FINDINGS_AND_CONFLICTS.md:40), [JXA-10](SOURCE_FINDINGS_AND_CONFLICTS.md:109), [JXA-12](SOURCE_FINDINGS_AND_CONFLICTS.md:111), [JXA-17](SOURCE_FINDINGS_AND_CONFLICTS.md:116), [JXA-18](SOURCE_FINDINGS_AND_CONFLICTS.md:117), [JXA-21](SOURCE_FINDINGS_AND_CONFLICTS.md:120), [JXA-25](SOURCE_FINDINGS_AND_CONFLICTS.md:124), [JFN-09](SOURCE_FINDINGS_AND_CONFLICTS.md:143), [CEX-03](SOURCE_FINDINGS_AND_CONFLICTS.md:185), [CEX-04](SOURCE_FINDINGS_AND_CONFLICTS.md:186), [PIN001-01](SOURCE_FINDINGS_AND_CONFLICTS.md:812), [PIN001-02](SOURCE_FINDINGS_AND_CONFLICTS.md:813), [PIN001-03](SOURCE_FINDINGS_AND_CONFLICTS.md:814), [PIN001-04](SOURCE_FINDINGS_AND_CONFLICTS.md:815), [PIN002-01](SOURCE_FINDINGS_AND_CONFLICTS.md:816), [PIN002-02](SOURCE_FINDINGS_AND_CONFLICTS.md:817), [PIN002-03](SOURCE_FINDINGS_AND_CONFLICTS.md:818), [PIN003-01](SOURCE_FINDINGS_AND_CONFLICTS.md:819), [PIN003-02](SOURCE_FINDINGS_AND_CONFLICTS.md:820), [PIN003-03](SOURCE_FINDINGS_AND_CONFLICTS.md:821), [PIN003-04](SOURCE_FINDINGS_AND_CONFLICTS.md:822), [PIN004-01](SOURCE_FINDINGS_AND_CONFLICTS.md:823), [PIN012-01](SOURCE_FINDINGS_AND_CONFLICTS.md:852), [PIN012-02](SOURCE_FINDINGS_AND_CONFLICTS.md:853), [PIN012-03](SOURCE_FINDINGS_AND_CONFLICTS.md:854), [PIN012-04](SOURCE_FINDINGS_AND_CONFLICTS.md:855), [PIN012-05](SOURCE_FINDINGS_AND_CONFLICTS.md:856), [PIN013-01](SOURCE_FINDINGS_AND_CONFLICTS.md:857), [PIN013-02](SOURCE_FINDINGS_AND_CONFLICTS.md:858), [PIN013-03](SOURCE_FINDINGS_AND_CONFLICTS.md:859), [PIN013-04](SOURCE_FINDINGS_AND_CONFLICTS.md:860), [PIN013-05](SOURCE_FINDINGS_AND_CONFLICTS.md:861), [PIN013-06](SOURCE_FINDINGS_AND_CONFLICTS.md:862), [PIN015-01](SOURCE_FINDINGS_AND_CONFLICTS.md:865), [PIN015-02](SOURCE_FINDINGS_AND_CONFLICTS.md:866), [PIN015-03](SOURCE_FINDINGS_AND_CONFLICTS.md:867), [PIN024-01](SOURCE_FINDINGS_AND_CONFLICTS.md:878), [PIN024-02](SOURCE_FINDINGS_AND_CONFLICTS.md:879), [PIN021-01](SOURCE_FINDINGS_AND_CONFLICTS.md:892), [PIN021-02](SOURCE_FINDINGS_AND_CONFLICTS.md:893), [PIN025-01](SOURCE_FINDINGS_AND_CONFLICTS.md:899), [PIN026-01](SOURCE_FINDINGS_AND_CONFLICTS.md:900), [PIN026-02](SOURCE_FINDINGS_AND_CONFLICTS.md:901), [PIN027-01](SOURCE_FINDINGS_AND_CONFLICTS.md:902), [PIN027-02](SOURCE_FINDINGS_AND_CONFLICTS.md:903), [PIN028-01](SOURCE_FINDINGS_AND_CONFLICTS.md:904), [PIN028-02](SOURCE_FINDINGS_AND_CONFLICTS.md:905), [PIN028-03](SOURCE_FINDINGS_AND_CONFLICTS.md:906), [PIN029-01](SOURCE_FINDINGS_AND_CONFLICTS.md:907), [PIN029-02](SOURCE_FINDINGS_AND_CONFLICTS.md:908), [PIN029-03](SOURCE_FINDINGS_AND_CONFLICTS.md:909), [PIN030-01](SOURCE_FINDINGS_AND_CONFLICTS.md:910), [PIN030-02](SOURCE_FINDINGS_AND_CONFLICTS.md:911), [PIN030-03](SOURCE_FINDINGS_AND_CONFLICTS.md:912), [PIN039-01](SOURCE_FINDINGS_AND_CONFLICTS.md:933), [PIN039-02](SOURCE_FINDINGS_AND_CONFLICTS.md:934), [PIN040-01](SOURCE_FINDINGS_AND_CONFLICTS.md:935), [PIN040-02](SOURCE_FINDINGS_AND_CONFLICTS.md:936), [PIN041-01](SOURCE_FINDINGS_AND_CONFLICTS.md:938), [PIN041-02](SOURCE_FINDINGS_AND_CONFLICTS.md:939), [PIN041-03](SOURCE_FINDINGS_AND_CONFLICTS.md:940), [PIN042-01](SOURCE_FINDINGS_AND_CONFLICTS.md:942), [PIN042-02](SOURCE_FINDINGS_AND_CONFLICTS.md:943), [PIN043-01](SOURCE_FINDINGS_AND_CONFLICTS.md:944), [PIN044-01](SOURCE_FINDINGS_AND_CONFLICTS.md:945), [PIN044-02](SOURCE_FINDINGS_AND_CONFLICTS.md:946), [PIN046-01](SOURCE_FINDINGS_AND_CONFLICTS.md:955), [PIN047-01](SOURCE_FINDINGS_AND_CONFLICTS.md:956), [PIN047-02](SOURCE_FINDINGS_AND_CONFLICTS.md:957), [PIN047-03](SOURCE_FINDINGS_AND_CONFLICTS.md:958), [PIN048-01](SOURCE_FINDINGS_AND_CONFLICTS.md:960), [PIN048-02](SOURCE_FINDINGS_AND_CONFLICTS.md:961), [PIN048-03](SOURCE_FINDINGS_AND_CONFLICTS.md:962), [PIN049-01](SOURCE_FINDINGS_AND_CONFLICTS.md:964), [PIN049-02](SOURCE_FINDINGS_AND_CONFLICTS.md:965), [PIN049-03](SOURCE_FINDINGS_AND_CONFLICTS.md:966), [PIN054-01](SOURCE_FINDINGS_AND_CONFLICTS.md:978), [PIN054-02](SOURCE_FINDINGS_AND_CONFLICTS.md:979), [PIN058-01](SOURCE_FINDINGS_AND_CONFLICTS.md:989), [PIN059-01](SOURCE_FINDINGS_AND_CONFLICTS.md:990), [PIN059-02](SOURCE_FINDINGS_AND_CONFLICTS.md:991), [PIN061-01](SOURCE_FINDINGS_AND_CONFLICTS.md:997), [PIN061-02](SOURCE_FINDINGS_AND_CONFLICTS.md:998), [PIN061-03](SOURCE_FINDINGS_AND_CONFLICTS.md:999), [PIN064-01](SOURCE_FINDINGS_AND_CONFLICTS.md:1009), [PIN064-02](SOURCE_FINDINGS_AND_CONFLICTS.md:1010), [PIN073-01](SOURCE_FINDINGS_AND_CONFLICTS.md:1048), [PIN073-02](SOURCE_FINDINGS_AND_CONFLICTS.md:1049), [PIN074-01](SOURCE_FINDINGS_AND_CONFLICTS.md:1051), [PIN074-02](SOURCE_FINDINGS_AND_CONFLICTS.md:1052), [PIN075-01](SOURCE_FINDINGS_AND_CONFLICTS.md:1054), [PIN075-02](SOURCE_FINDINGS_AND_CONFLICTS.md:1055), [PIN076-01](SOURCE_FINDINGS_AND_CONFLICTS.md:1057), [PIN076-02](SOURCE_FINDINGS_AND_CONFLICTS.md:1058), [PIN078-01](SOURCE_FINDINGS_AND_CONFLICTS.md:1063), [PIN078-02](SOURCE_FINDINGS_AND_CONFLICTS.md:1064), [PIN080-01](SOURCE_FINDINGS_AND_CONFLICTS.md:1071), [PIN080-02](SOURCE_FINDINGS_AND_CONFLICTS.md:1072), [PIN080-03](SOURCE_FINDINGS_AND_CONFLICTS.md:1073), [PIN081-01](SOURCE_FINDINGS_AND_CONFLICTS.md:1075), [PIN081-02](SOURCE_FINDINGS_AND_CONFLICTS.md:1076), [PIN081-03](SOURCE_FINDINGS_AND_CONFLICTS.md:1077), [PIN081-04](SOURCE_FINDINGS_AND_CONFLICTS.md:1078), [PIN082-01](SOURCE_FINDINGS_AND_CONFLICTS.md:1080), [PIN082-02](SOURCE_FINDINGS_AND_CONFLICTS.md:1081), [PIN082-03](SOURCE_FINDINGS_AND_CONFLICTS.md:1082).

**Conversation upgrade lineage.** [CEX-03](SOURCE_FINDINGS_AND_CONFLICTS.md:185). Read the full rows and their original conversation references; [the recheck](CONVERSATION_RECHECK.md) preserves the exact unit/exception routes.

<a id="up-c21-transitions"></a>
#### C21.TRANSITIONS — Session handoff and horizon experts

[Existing definition, target and P0–P7](experiments/C.md#c21-transitions) remain binding.

**Specific upgrade scope.** Add causal expected-activity phase and prior-session trajectory to every exact clock/reference/ordering transition.

**Local comparison.** Compare source hit tables, hierarchical session-pair models and duration kernels; score each body/open/range target independently.

**Additional cases.** Body25 versus O→O; AM expansion continues; holiday; overlapping sessions; current-inclusive count.

<a id="up-c22"></a>
### UP-C22 — Context originator and applicability contract

Parent: [C22](components/CONTEXT.md); [local phases](experiments/C.md#c22); [definition refinement](SYSTEM_REFINEMENT.md#sr-c22). Upgrade role: `decision`.

**Starting idea.** Use Context only to filter a separately generated entry.

**Existing improvement path.** Context forecasts can originate complete current-price or conditional-entry opportunities.

**Remaining weakness.** A single threshold may ignore several feasible ways to express the same forecast and duplicate candidates from other originators.

**Further upgrade.** Compile a bounded library of Context-originated opportunity templates with side, trigger/entry, invalidation, destination, horizon and evidence lineage. Compare immediate and conditional templates using calibrated path distributions and shared G/P value, deduplicating equivalent actions while preserving source evidence; no Response prerequisite is introduced.

**Fair comparison.** No Context origination, source simple rule, calibrated threshold and bounded template/proposal alternatives.

**Evidence.** New useful opportunity coverage, duplication invariance, calibration, complete-policy net and one-mini feasibility.

**Additional local cases to implement.** Strong Context with no local level; conditional trigger never arrives; two experts propose same action; future best entry unavailable.

**Decision or system use.** Let the full Context family create testable trades as well as inform selection, with every proposal passing common execution/risk rules.

**Exact reviewed source clauses.** [CEX-01](SOURCE_FINDINGS_AND_CONFLICTS.md:183), [CD1-01](SOURCE_FINDINGS_AND_CONFLICTS.md:394), [CD1-02](SOURCE_FINDINGS_AND_CONFLICTS.md:395), [CD1-03](SOURCE_FINDINGS_AND_CONFLICTS.md:396), [CD1-04](SOURCE_FINDINGS_AND_CONFLICTS.md:397), [CD1-05](SOURCE_FINDINGS_AND_CONFLICTS.md:398), [DRF-U07](SOURCE_FINDINGS_AND_CONFLICTS.md:431), [DRF-U11](SOURCE_FINDINGS_AND_CONFLICTS.md:435), [DRF-A20](SOURCE_FINDINGS_AND_CONFLICTS.md:461), [DRF-A24](SOURCE_FINDINGS_AND_CONFLICTS.md:465), [DRF-A29](SOURCE_FINDINGS_AND_CONFLICTS.md:470).

**Conversation upgrade lineage.** [JCV-A07](SOURCE_FINDINGS_AND_CONFLICTS.md:166), [CRL-07](SOURCE_FINDINGS_AND_CONFLICTS.md:223), [DRF-U11](SOURCE_FINDINGS_AND_CONFLICTS.md:435), [DRF-A24](SOURCE_FINDINGS_AND_CONFLICTS.md:465). Read the full rows and their original conversation references; [the recheck](CONVERSATION_RECHECK.md) preserves the exact unit/exception routes.

<a id="up-c22-origination"></a>
#### C22.ORIGINATION — Context-originated opportunity proposals

[Existing definition, target and P0–P7](experiments/C.md#c22-origination) remain binding.

**Specific upgrade scope.** Generate bounded complete Context opportunity templates for immediate and conditional entry with provenance and expiry.

**Local comparison.** Compare no origination, source threshold and calibrated templates through shared action deduplication/value/risk.

**Additional cases.** No local level; trigger never arrives; duplicate opportunity; no Response prerequisite; stop unaffordable.

<a id="up-c23"></a>
### UP-C23 — Parkinson high-low variance specialist

Parent: [C23](components/CONTEXT.md); [local phases](experiments/C.md#c23); [definition refinement](SYSTEM_REFINEMENT.md#sr-c23). Upgrade role: `forecast`.

**Starting idea.** Use high-low range as a volatility proxy.

**Existing improvement path.** Verified Parkinson measurement and separate common-horizon forecasts/comparators.

**Remaining weakness.** Range-only information can be redundant with GK/YZ or distorted by interval length and missing opening movement.

**Further upgrade.** Expose scale-consistent Parkinson contributions and residual range information relative to close-return/RV baselines, with gap/duration/quality metadata. Compare aggregate lag regression, component residual forecasting and G02 reliability weighting; preserve the diffusion-based estimator as the exact comparator.

**Fair comparison.** Close/EWMA, Parkinson lags, GK/YZ/RS controls, residual range features and regularized forecast.

**Evidence.** Reference arithmetic, common-target proper loss, gap/scale stability, incremental ensemble value and compute.

**Additional local cases to implement.** Unobserved opening jump; one extreme quote not trade high; short interval; constant price; drift-heavy period.

**Decision or system use.** Determine whether the range statistic supplies useful distinct forecast information under the actual observation process.

**Exact reviewed source clauses.** [DTM-A03](SOURCE_FINDINGS_AND_CONFLICTS.md:61), [CEX-06](SOURCE_FINDINGS_AND_CONFLICTS.md:188).

<a id="up-c23-parkinson_scale"></a>
#### C23.PARKINSON_SCALE — High-low variance information

[Existing definition, target and P0–P7](experiments/C.md#c23-parkinson_scale) remain binding.

**Specific upgrade scope.** Extract residual range information and quality/scale diagnostics from exact Parkinson measurements.

**Local comparison.** Compare close/EWMA, GK/YZ/RS and registered residual forecasts under identical forward target and intervals.

**Additional cases.** Opening gap; drift-heavy range; noisy extreme; flat interval; redundant estimator.

<a id="up-c24"></a>
### UP-C24 — ARCH/GARCH conditional-variance challenger

Parent: [C24](components/CONTEXT.md); [local phases](experiments/C.md#c24); [definition refinement](SYSTEM_REFINEMENT.md#sr-c24). Upgrade role: `forecast`.

**Starting idea.** Use constant variance or a simple ARCH/GARCH recursion.

**Existing improvement path.** Constrained low-order models, explicit multi-step horizon aggregation and tail/asymmetry challengers.

**Remaining weakness.** Return-only recursions can react slowly to new intraday measurements and fit tails separately from variance dynamics.

**Further upgrade.** Compare GARCH/asymmetric recursions with a compact realized-measurement-augmented variance model and a residual combination with HAR. Register each equation, positivity/stability/innovation assumptions and chronological initialization; match inputs separately when testing model class versus added RV information, and calibrate predictive tails.

**Fair comparison.** Constant/EWMA, ARCH/GARCH, registered asymmetric/t innovations, realized-measurement augmentation and HAR residual combination.

**Evidence.** Variance and tail proper loss, parameter stability, horizon calibration, computation and incremental ensemble/net value.

**Additional local cases to implement.** Near-unit persistence; structural break; heavy tails; measurement unavailable; multi-step covariance assumptions; nonpositive numerical state.

**Decision or system use.** Test whether conditional dynamics and fresh realized information improve the complete volatility ensemble beyond simpler memory models.

**Exact reviewed source clauses.** [DTM-A03](SOURCE_FINDINGS_AND_CONFLICTS.md:61), [CEX-06](SOURCE_FINDINGS_AND_CONFLICTS.md:188).

<a id="up-c24-garch_asymmetry"></a>
#### C24.GARCH_ASYMMETRY — Conditional-variance and leverage challengers

[Existing definition, target and P0–P7](experiments/C.md#c24-garch_asymmetry) remain binding.

**Specific upgrade scope.** Register each asymmetric/tail recursion and compare realized-measurement augmentation plus residual combination with HAR.

**Local comparison.** Separate added RV information from model class, verify positivity/stability/retransformation and calibrate horizons/tails.

**Additional cases.** Near-unit persistence; heavy tails; missing RV; regime break; multi-step aggregation.

<a id="family-o"></a>
## Options

<a id="up-o01"></a>
### UP-O01 — Chain assembly, eligibility and coverage accounting

Parent: [O01](components/OPTIONS.md); [local phases](experiments/O.md#o01); [definition refinement](SYSTEM_REFINEMENT.md#sr-o01). Upgrade role: `engineering`.

**Starting idea.** Take one downloaded option chain as the universe.

**Existing improvement path.** Sparse PIT union, distinct listed/quoted/traded/OI universes and field-specific coverage.

**Remaining weakness.** Repeated chain joins are costly, and a single coverage percentage hides structurally different holes that change model support.

**Further upgrade.** Maintain an incremental contract/strike/expiry support tensor with listing lifecycle, observation age, value-source lineage and operation eligibility. Cache only validated shared views; expose support topology and stable common-cohort projections to models, with sparse residual imputation a separately scored option.

**Fair comparison.** Literal sparse union, fixed intersection and incremental support-aware views; compare imputation only on masked observed targets and eligible downstream cohorts.

**Evidence.** Identity/coverage parity, query cost, held-out field error, support robustness and downstream uncertainty.

**Additional local cases to implement.** New listing; duplicate near/broad acquisition; disappearing wing; unchanged chain with fresh quotes; expired contract omitted from report.

**Decision or system use.** Give every option feature/model an accurate, efficient view of what is actually observed and where information is missing.

**Exact reviewed source clauses.** [DTM-A05](SOURCE_FINDINGS_AND_CONFLICTS.md:63), [CEX-10](SOURCE_FINDINGS_AND_CONFLICTS.md:192), [CEX-23](SOURCE_FINDINGS_AND_CONFLICTS.md:205).

**Conversation upgrade lineage.** [CEX-10](SOURCE_FINDINGS_AND_CONFLICTS.md:192), [CEX-23](SOURCE_FINDINGS_AND_CONFLICTS.md:205). Read the full rows and their original conversation references; [the recheck](CONVERSATION_RECHECK.md) preserves the exact unit/exception routes.

<a id="up-o01-coverage"></a>
#### O01.COVERAGE — Contract and strike support

[Existing definition, target and P0–P7](experiments/O.md#o01-coverage) remain binding.

**Specific upgrade scope.** Use an incremental contract/strike/expiry support tensor with listing, quote, trade, OI and valuation capabilities separate.

**Local comparison.** Compare sparse union/intersection and optimized support views; measure operation-specific coverage and information loss.

**Additional cases.** New listing; missing wing; duplicate acquisition; unchanged value fresh observation.

<a id="up-o02"></a>
### UP-O02 — Option price validation and IV inversion

Parent: [O02](components/OPTIONS.md); [local phases](experiments/O.md#o02); [definition refinement](SYSTEM_REFINEMENT.md#sr-o02). Upgrade role: `engineering`.

**Starting idea.** Invert a midpoint into one IV number.

**Existing improvement path.** Contract-specific price validation, bracketed inversion and bid/ask uncertainty intervals.

**Remaining weakness.** Near expiry or low vega, a precise numerical root can represent weakly identified volatility; repeated full inversion can waste compute.

**Further upgrade.** Add price-to-IV conditioning diagnostics and interval-aware inversion, switching downstream comparison to price-space when IV is weakly identified. Use bounded warm starts/adaptive solver tolerances tied to option-price and consumer sensitivity error; retain independent literal solvers for European and eligible American styles.

**Fair comparison.** Mid root, bid/ask interval, condition-aware price/IV representation and optimized versus reference solver.

**Evidence.** Price reconstruction, interval/domain fidelity, sensitivity error, failure detection and latency.

**Additional local cases to implement.** Intrinsic-only quote; tiny vega; one-sided market; dividend/exercise boundary; negative-rate/carry domain; near-zero time.

**Decision or system use.** Improve numerical usefulness and speed while making the information content of an IV estimate explicit.

**Exact reviewed source clauses.** [DRF-U04](SOURCE_FINDINGS_AND_CONFLICTS.md:428), [DRF-A06](SOURCE_FINDINGS_AND_CONFLICTS.md:447).

**Conversation upgrade lineage.** [DTM-A05](SOURCE_FINDINGS_AND_CONFLICTS.md:63). Read the full rows and their original conversation references; [the recheck](CONVERSATION_RECHECK.md) preserves the exact unit/exception routes.

<a id="up-o02-bidask_iv"></a>
#### O02.BIDASK_IV — IV uncertainty and solver domains

[Existing definition, target and P0–P7](experiments/O.md#o02-bidask_iv) remain binding.

**Specific upgrade scope.** Add price-to-IV conditioning and interval-aware solver outputs, with price-space alternatives when IV is weakly identified.

**Local comparison.** Compare mid, bid/ask, condition-aware representation and reference/optimized inversion under price-error tolerances.

**Additional cases.** Tiny vega; intrinsic-only; one-sided market; American boundary; near expiry.

<a id="up-o03"></a>
### UP-O03 — Options trade-sign uncertainty

Parent: [O03](components/OPTIONS.md); [local phases](experiments/O.md#o03); [definition refinement](SYSTEM_REFINEMENT.md#sr-o03). Upgrade role: `measurement`.

**Starting idea.** Assign every option trade a buy/sell sign from its price.

**Existing improvement path.** Reliable sign where available, conservative quote/tick rules and calibrated-label dependency.

**Remaining weakness.** Hard assignments near quote boundaries hide timing and classification uncertainty, and independent signs understate shared quote error.

**Further upgrade.** Construct sign-evidence likelihoods over admissible preceding quote states and report raw rule decisions, uncertain mass and common quote-error groups. Compare conservative intervals and probabilistic classifiers only on reliable matched-label cohorts; O20 later handles package-level alternatives without feeding its result back into the early sign port.

**Fair comparison.** Reported/quote/tick/conservative-unknown, timing-aware sign scenarios and eligible calibrated classifier.

**Evidence.** Sign calibration by quote age/condition, unknown retention, grouped uncertainty and downstream flow sensitivity.

**Additional local cases to implement.** Locked/crossed quote; quote arrives late; inside-spread print; shared stale quote signs many trades; reliable futures label fails to transfer.

**Decision or system use.** Preserve usable directional information with uncertainty that reflects the actual classification evidence.

**Exact reviewed source clauses.** [DTM-A05](SOURCE_FINDINGS_AND_CONFLICTS.md:63), [CEX-24](SOURCE_FINDINGS_AND_CONFLICTS.md:206), [DRF-A02](SOURCE_FINDINGS_AND_CONFLICTS.md:443).

This parent has no separate named child; its own P0–P7 phases carry the full upgrade and source-clause obligations.

<a id="up-o04"></a>
### UP-O04 — Arbitrage-aware volatility surface and uncertainty

Parent: [O04](components/OPTIONS.md); [local phases](experiments/O.md#o04); [definition refinement](SYSTEM_REFINEMENT.md#sr-o04). Upgrade role: `forecast`.

**Starting idea.** Interpolate IV points into a smooth curve.

**Existing improvement path.** Contract-consistent constrained surfaces, temporal continuity, missing support and price/IV uncertainty.

**Remaining weakness.** Smoothness alone can overfit noisy midpoints or create false precision in sparse wings and temporal extrapolation.

**Further upgrade.** Fit a robust interval-aware price surface with low-rank temporal factors and constrained residuals, comparing static snapshot fits with causal filtered updates. Preserve common parameter/quote uncertainty and distinguish interpolation from forecast/extrapolation; test future quote/price prediction and downstream sensitivity separately.

**Fair comparison.** Nearest/flat, constrained interpolation, SVI/SSVI or style-consistent price surface, temporal factors and bounded residual challenger.

**Evidence.** Held-out price loss relative to spreads, arbitrage/domain diagnostics, uncertainty coverage, temporal stability and economic increment.

**Additional local cases to implement.** Missing wing; conflicting quotes; expiry approaches zero; American exercise feature; broad common surface error.

**Decision or system use.** Improve the usable shape and dynamics of the surface without mistaking a smooth fitted curve for complete observation.

**Exact reviewed source clauses.** [DTM-A05](SOURCE_FINDINGS_AND_CONFLICTS.md:63), [CEX-11](SOURCE_FINDINGS_AND_CONFLICTS.md:193), [CRL-05](SOURCE_FINDINGS_AND_CONFLICTS.md:221), [DRF-U04](SOURCE_FINDINGS_AND_CONFLICTS.md:428), [DRF-A13](SOURCE_FINDINGS_AND_CONFLICTS.md:454).

**Conversation upgrade lineage.** [DTM-A05](SOURCE_FINDINGS_AND_CONFLICTS.md:63), [CEX-23](SOURCE_FINDINGS_AND_CONFLICTS.md:205). Read the full rows and their original conversation references; [the recheck](CONVERSATION_RECHECK.md) preserves the exact unit/exception routes.

<a id="up-o04-surface_fit"></a>
#### O04.SURFACE_FIT — Spatial surface and arbitrage constraints

[Existing definition, target and P0–P7](experiments/O.md#o04-surface_fit) remain binding.

**Specific upgrade scope.** Compare robust interval-aware constrained price fits and low-rank spatial residuals against exact existing style-appropriate surfaces.

**Local comparison.** Score held-out prices relative to spreads, support/arbitrage diagnostics and downstream sensitivity at matched observed strikes.

**Additional cases.** Missing wing; conflicting quotes; American style; local curvature noise; unsupported extrapolation.

<a id="up-o04-temporal_surface"></a>
#### O04.TEMPORAL_SURFACE — Surface continuity and observation noise

[Existing definition, target and P0–P7](experiments/O.md#o04-temporal_surface) remain binding.

**Specific upgrade scope.** Use causal temporal factors and filtered residual updates with shared quote/parameter uncertainty.

**Local comparison.** Compare independent snapshots, carry-forward and temporal fit on future quote prediction, calibration and decision increment.

**Additional cases.** Stale copies; support changes; rapid expiry; correlated surface error; future smoother.

<a id="up-o05"></a>
### UP-O05 — Greeks and unit-consistent sensitivities

Parent: [O05](components/OPTIONS.md); [local phases](experiments/O.md#o05); [definition refinement](SYSTEM_REFINEMENT.md#sr-o05). Upgrade role: `measurement`.

**Starting idea.** Add Gamma and higher Greeks as separate scalars.

**Existing improvement path.** Unit-consistent local and surface-aware sensitivities verified against finite differences.

**Remaining weakness.** Local derivatives become unstable or inaccurate for finite moves, while computing every derivative at full precision can be expensive.

**Further upgrade.** Build a consumer-specific response cube from full repricing over registered joint price/volatility/time shocks, with local Greek approximations and measured truncation error. Use adaptive finite differences/automatic derivatives where valid and cache only requested sensitivities; compare sticky conventions as scenarios rather than asserting one actual hedge law.

**Fair comparison.** Analytic/reference Greeks, finite differences, local scenario approximation and full nonlinear repricing with error-controlled optimization.

**Evidence.** Derivative/price parity, finite-move approximation error, scenario stability, inference cost and downstream added value.

**Additional local cases to implement.** Near-expiry delta saturation; surface kink; American boundary; charm sign; large correlated price/vol shock; unlike units.

**Decision or system use.** Provide stable local and finite-move sensitivity information appropriate to the consumer's actual scenario.

**Exact reviewed source clauses.** [CEX-11](SOURCE_FINDINGS_AND_CONFLICTS.md:193), [CEX-21](SOURCE_FINDINGS_AND_CONFLICTS.md:203), [DRF-U01](SOURCE_FINDINGS_AND_CONFLICTS.md:425), [DRF-U04](SOURCE_FINDINGS_AND_CONFLICTS.md:428), [DRF-A06](SOURCE_FINDINGS_AND_CONFLICTS.md:447), [DRF-A13](SOURCE_FINDINGS_AND_CONFLICTS.md:454), [GXF-01](SOURCE_FINDINGS_AND_CONFLICTS.md:485), [GXF-02](SOURCE_FINDINGS_AND_CONFLICTS.md:486), [GXF-03](SOURCE_FINDINGS_AND_CONFLICTS.md:487), [GXF-04](SOURCE_FINDINGS_AND_CONFLICTS.md:488), [GXF-05](SOURCE_FINDINGS_AND_CONFLICTS.md:489), [GXF-06](SOURCE_FINDINGS_AND_CONFLICTS.md:490), [GXF-07](SOURCE_FINDINGS_AND_CONFLICTS.md:491), [GXF-08](SOURCE_FINDINGS_AND_CONFLICTS.md:492), [GXF-09](SOURCE_FINDINGS_AND_CONFLICTS.md:493), [GXF-10](SOURCE_FINDINGS_AND_CONFLICTS.md:494), [GXF-11](SOURCE_FINDINGS_AND_CONFLICTS.md:495), [GXF-12](SOURCE_FINDINGS_AND_CONFLICTS.md:496), [GXF-13](SOURCE_FINDINGS_AND_CONFLICTS.md:497).

**Conversation upgrade lineage.** [CEX-10](SOURCE_FINDINGS_AND_CONFLICTS.md:192), [CEX-21](SOURCE_FINDINGS_AND_CONFLICTS.md:203), [DRF-U01](SOURCE_FINDINGS_AND_CONFLICTS.md:425), [DRF-U04](SOURCE_FINDINGS_AND_CONFLICTS.md:428), [DRF-A01](SOURCE_FINDINGS_AND_CONFLICTS.md:442), [DRF-A13](SOURCE_FINDINGS_AND_CONFLICTS.md:454). Read the full rows and their original conversation references; [the recheck](CONVERSATION_RECHECK.md) preserves the exact unit/exception routes.

<a id="up-o05-higher_greeks"></a>
#### O05.HIGHER_GREEKS — Vega, vanna, charm and volga sensitivity

[Existing definition, target and P0–P7](experiments/O.md#o05-higher_greeks) remain binding.

**Specific upgrade scope.** Retain every higher derivative and compare local approximations to full joint price/vol/time repricing cubes.

**Local comparison.** Verify analytic/automatic/finite-difference conventions, finite-shock truncation error and whether each derivative adds useful stable information.

**Additional cases.** Vanna interaction; charm time sign; volga curvature; near-expiry saturation; unlike units.

<a id="up-o06"></a>
### UP-O06 — Reported OI state and next-report label service

Parent: [O06](components/OPTIONS.md); [local phases](experiments/O.md#o06); [definition refinement](SYSTEM_REFINEMENT.md#sr-o06). Upgrade role: `engineering`.

**Starting idea.** Carry yesterday's OI and subtract the next file.

**Existing improvement path.** Published-report lineage, comparable contract intervals and revision/terminal-state labels.

**Remaining weakness.** Flat endpoint tables lose reporting cadence, missing-report patterns and the distinction between actual change and later revision.

**Further upgrade.** Represent OI as a versioned report-event ledger with comparable interval identities, lifecycle transitions and revision innovations. Generate next-report label families and support masks from one deterministic compiler; retain current vintage, later revised value and measurement uncertainty separately, never inventing an intraday position observation.

**Fair comparison.** Last-known table, naive-date diagnostic and event-ledger label service on identical reports.

**Evidence.** Report/contract reconciliation, label-maturity fidelity, revision attribution and reusable-label cost.

**Additional local cases to implement.** Weekend gap; omitted zero versus missing row; exercise/adjustment; late revision; new contract; changed publication schedule.

**Decision or system use.** Supply dependable endpoint supervision and clearly identified report innovations to all OI/holdings models.

**Exact reviewed source clauses.** [DTM-A05](SOURCE_FINDINGS_AND_CONFLICTS.md:63), [CEX-10](SOURCE_FINDINGS_AND_CONFLICTS.md:192), [CEX-17](SOURCE_FINDINGS_AND_CONFLICTS.md:199), [IMG-01](SOURCE_FINDINGS_AND_CONFLICTS.md:248), [IMG-02](SOURCE_FINDINGS_AND_CONFLICTS.md:249), [IMG-03](SOURCE_FINDINGS_AND_CONFLICTS.md:250), [IMG-04](SOURCE_FINDINGS_AND_CONFLICTS.md:251), [IMG-05](SOURCE_FINDINGS_AND_CONFLICTS.md:252), [IMG-06](SOURCE_FINDINGS_AND_CONFLICTS.md:253), [IMG-07](SOURCE_FINDINGS_AND_CONFLICTS.md:254), [DRF-U02](SOURCE_FINDINGS_AND_CONFLICTS.md:426), [DRF-U06](SOURCE_FINDINGS_AND_CONFLICTS.md:430), [DRF-A01](SOURCE_FINDINGS_AND_CONFLICTS.md:442), [DRF-A04](SOURCE_FINDINGS_AND_CONFLICTS.md:445), [DRF-A06](SOURCE_FINDINGS_AND_CONFLICTS.md:447), [DRF-A17](SOURCE_FINDINGS_AND_CONFLICTS.md:458), [GXF-08](SOURCE_FINDINGS_AND_CONFLICTS.md:492), [PIN066-01](SOURCE_FINDINGS_AND_CONFLICTS.md:1016), [PIN066-02](SOURCE_FINDINGS_AND_CONFLICTS.md:1017), [PIN066-03](SOURCE_FINDINGS_AND_CONFLICTS.md:1018), [PIN066-04](SOURCE_FINDINGS_AND_CONFLICTS.md:1019), [PIN077-01](SOURCE_FINDINGS_AND_CONFLICTS.md:1060), [PIN077-02](SOURCE_FINDINGS_AND_CONFLICTS.md:1061).

**Conversation upgrade lineage.** [CEX-10](SOURCE_FINDINGS_AND_CONFLICTS.md:192), [CEX-24](SOURCE_FINDINGS_AND_CONFLICTS.md:206), [DRF-U02](SOURCE_FINDINGS_AND_CONFLICTS.md:426), [DRF-A04](SOURCE_FINDINGS_AND_CONFLICTS.md:445). Read the full rows and their original conversation references; [the recheck](CONVERSATION_RECHECK.md) preserves the exact unit/exception routes.

<a id="up-o06-report_cohorts"></a>
#### O06.REPORT_COHORTS — OI reporting and terminal states

[Existing definition, target and P0–P7](experiments/O.md#o06-report_cohorts) remain binding.

**Specific upgrade scope.** Generate interval-specific OI labels from a versioned report/lifecycle/revision ledger.

**Local comparison.** Compare naive dates and exact report events with known-at timing and explicit missing/terminal states.

**Additional cases.** Weekend; exercise/adjustment; omitted row; revised report; newly listed contract.

<a id="up-o07"></a>
### UP-O07 — Aggregate next-reported-OI forecast experts

Parent: [O07](components/OPTIONS.md); [local phases](experiments/O.md#o07); [definition refinement](SYSTEM_REFINEMENT.md#sr-o07). Upgrade role: `forecast`.

**Starting idea.** Estimate OI by adding a fraction of volume.

**Existing improvement path.** Constrained count/distributional models and coherent contract/strike/expiry hierarchy.

**Remaining weakness.** Independent forecasts miss common expiry/market shocks and can perform well in aggregate while misplacing concentration across strikes.

**Further upgrade.** Fit joint nonnegative OI-change scenarios with partially pooled lifecycle/count parameters and low-rank cross-strike/expiry shocks. Compare aggregate reconciliation with jointly generated samples, preserving new/zero/expiring contract regimes and uncertainty in report revisions; evaluate concentration relocation as well as totals.

**Fair comparison.** Persistence/volume fraction, independent count model, hierarchical reconciled forecasts and joint factor/count scenarios.

**Evidence.** Count/distribution proper loss, aggregate coherence, small/new-contract and node-placement error, downstream value.

**Additional local cases to implement.** Same total with wrong strike allocation; many contracts share shock; expiration; sparse new listing; revision outside trade-only bound.

**Decision or system use.** Forecast the distribution of where aggregate positions may be reported, not just a chain-level total.

**Exact reviewed source clauses.** [DTM-A05](SOURCE_FINDINGS_AND_CONFLICTS.md:63), [CEX-17](SOURCE_FINDINGS_AND_CONFLICTS.md:199), [IMG-01](SOURCE_FINDINGS_AND_CONFLICTS.md:248), [IMG-02](SOURCE_FINDINGS_AND_CONFLICTS.md:249), [IMG-03](SOURCE_FINDINGS_AND_CONFLICTS.md:250), [IMG-04](SOURCE_FINDINGS_AND_CONFLICTS.md:251), [IMG-05](SOURCE_FINDINGS_AND_CONFLICTS.md:252), [IMG-06](SOURCE_FINDINGS_AND_CONFLICTS.md:253), [IMG-07](SOURCE_FINDINGS_AND_CONFLICTS.md:254), [DRF-U02](SOURCE_FINDINGS_AND_CONFLICTS.md:426), [DRF-U06](SOURCE_FINDINGS_AND_CONFLICTS.md:430), [DRF-A04](SOURCE_FINDINGS_AND_CONFLICTS.md:445), [DRF-A18](SOURCE_FINDINGS_AND_CONFLICTS.md:459).

**Conversation upgrade lineage.** [DTM-A05](SOURCE_FINDINGS_AND_CONFLICTS.md:63), [CEX-17](SOURCE_FINDINGS_AND_CONFLICTS.md:199), [DRF-U02](SOURCE_FINDINGS_AND_CONFLICTS.md:426), [DRF-U06](SOURCE_FINDINGS_AND_CONFLICTS.md:430), [DRF-A04](SOURCE_FINDINGS_AND_CONFLICTS.md:445), [DRF-A18](SOURCE_FINDINGS_AND_CONFLICTS.md:459). Read the full rows and their original conversation references; [the recheck](CONVERSATION_RECHECK.md) preserves the exact unit/exception routes.

<a id="up-o07-hierarchical_oi"></a>
#### O07.HIERARCHICAL_OI — Aggregate OI forecast hierarchy

[Existing definition, target and P0–P7](experiments/O.md#o07-hierarchical_oi) remain binding.

**Specific upgrade scope.** Add joint low-rank strike/expiry shocks and lifecycle-aware count scenarios to coherent aggregate OI forecasts.

**Local comparison.** Compare independent, reconciled and jointly generated distributions by totals, small contracts and concentration relocation.

**Additional cases.** Same total wrong strikes; common shock; zero/new/expiring contracts; revisions.

<a id="up-o08"></a>
### UP-O08 — Intraday aggregate-holdings scenario updater

Parent: [O08](components/OPTIONS.md); [local phases](experiments/O.md#o08); [definition refinement](SYSTEM_REFINEMENT.md#sr-o08). Upgrade role: `forecast`.

**Starting idea.** Update inferred holdings deterministically from signed flow.

**Existing improvement path.** Frozen holdings, latent opening/closing scenarios, coherent filtering and endpoint nonidentification.

**Remaining weakness.** A single chosen filter can appear precise despite many compatible intraday paths, and downstream usefulness may not require identifying one path.

**Further upgrade.** Compare a family of identified-compatible latent transition models with shared one-time evidence assimilation and endpoint likelihoods. Propagate model/parameter/path uncertainty separately; test decision sensitivity across plausible filters against direct observable flow-to-path challengers. Do not score an unavailable intraday truth as if observed.

**Fair comparison.** Frozen/proportional scenarios, one state-space filter, uncertainty-preserving model family and direct predictive bypass.

**Evidence.** Endpoint forecast loss, synthetic path recovery where truth is known, uncertainty sensitivity, downstream net and compute.

**Additional local cases to implement.** Different paths share endpoint; flow reused through O07; exercise shock; filter collapses after duplicate evidence; direct model works without holdings.

**Decision or system use.** Use latent holdings only to the extent supported by observations and added decision value, preserving uncertainty that endpoints cannot resolve.

**Exact reviewed source clauses.** [DTM-A05](SOURCE_FINDINGS_AND_CONFLICTS.md:63), [CEX-17](SOURCE_FINDINGS_AND_CONFLICTS.md:199), [IMG-01](SOURCE_FINDINGS_AND_CONFLICTS.md:248), [IMG-02](SOURCE_FINDINGS_AND_CONFLICTS.md:249), [IMG-03](SOURCE_FINDINGS_AND_CONFLICTS.md:250), [IMG-04](SOURCE_FINDINGS_AND_CONFLICTS.md:251), [IMG-05](SOURCE_FINDINGS_AND_CONFLICTS.md:252), [IMG-06](SOURCE_FINDINGS_AND_CONFLICTS.md:253), [IMG-07](SOURCE_FINDINGS_AND_CONFLICTS.md:254), [DRF-U06](SOURCE_FINDINGS_AND_CONFLICTS.md:430), [DRF-A01](SOURCE_FINDINGS_AND_CONFLICTS.md:442), [DRF-A04](SOURCE_FINDINGS_AND_CONFLICTS.md:445), [DRF-A18](SOURCE_FINDINGS_AND_CONFLICTS.md:459).

**Conversation upgrade lineage.** [DTM-A05](SOURCE_FINDINGS_AND_CONFLICTS.md:63), [CEX-17](SOURCE_FINDINGS_AND_CONFLICTS.md:199), [DRF-U01](SOURCE_FINDINGS_AND_CONFLICTS.md:425), [DRF-U06](SOURCE_FINDINGS_AND_CONFLICTS.md:430), [DRF-A02](SOURCE_FINDINGS_AND_CONFLICTS.md:443), [DRF-A04](SOURCE_FINDINGS_AND_CONFLICTS.md:445), [DRF-A18](SOURCE_FINDINGS_AND_CONFLICTS.md:459). Read the full rows and their original conversation references; [the recheck](CONVERSATION_RECHECK.md) preserves the exact unit/exception routes.

<a id="up-o08-assimilation"></a>
#### O08.ASSIMILATION — One-time evidence assimilation

[Existing definition, target and P0–P7](experiments/O.md#o08-assimilation) remain binding.

**Specific upgrade scope.** Compare compatible latent model families with explicit one-time evidence IDs and endpoint likelihood, preserving path nonidentification.

**Local comparison.** Test duplicate-input invariance, synthetic known-state recovery and downstream sensitivity versus direct observable bypass.

**Additional cases.** O07 and raw flow reused; same endpoint multiple paths; exercise shock; artificial posterior collapse.

<a id="up-o09"></a>
### UP-O09 — Exposure scenarios and concentration boards

Parent: [O09](components/OPTIONS.md); [local phases](experiments/O.md#o09); [definition refinement](SYSTEM_REFINEMENT.md#sr-o09). Upgrade role: `measurement`.

**Starting idea.** Treat a signed Gamma board as dealer positioning.

**Existing improvement path.** Explicit holdings/sign scenarios, gross concentration, correct units and nonlinear finite-move alternatives.

**Remaining weakness.** Separate boards obscure how Gamma, vanna, charm and surface/price shocks interact, while arbitrary sums create meaningless strength.

**Further upgrade.** Create common scenario response fields over source coordinate, tenor and shock, retaining gross concentration, assumed signed sensitivities and full repriced delta/option-value changes as distinct channels. Compare interpretable local boards with low-rank joint response summaries; empirical hedging/price response remains a separate forecast, not a measured position.

**Fair comparison.** Static prior-OI Gamma, mechanical repricing, all Greek/holdings scenarios and joint finite-shock response representation.

**Evidence.** Unit/repricing fidelity, scenario stability, concentration information, incremental path/value and inference cost.

**Additional local cases to implement.** Call/put sign scenario reverses; delta saturates; vanna/charm interaction; missing wing; coverage loss changes total.

**Decision or system use.** Represent the full exposure information and uncertainty while keeping mechanical sensitivity separate from actual market behavior.

**Exact reviewed source clauses.** [DTM-A05](SOURCE_FINDINGS_AND_CONFLICTS.md:63), [CEX-09](SOURCE_FINDINGS_AND_CONFLICTS.md:191), [CEX-18](SOURCE_FINDINGS_AND_CONFLICTS.md:200), [CEX-21](SOURCE_FINDINGS_AND_CONFLICTS.md:203), [IMG-01](SOURCE_FINDINGS_AND_CONFLICTS.md:248), [IMG-02](SOURCE_FINDINGS_AND_CONFLICTS.md:249), [IMG-03](SOURCE_FINDINGS_AND_CONFLICTS.md:250), [IMG-04](SOURCE_FINDINGS_AND_CONFLICTS.md:251), [IMG-05](SOURCE_FINDINGS_AND_CONFLICTS.md:252), [IMG-06](SOURCE_FINDINGS_AND_CONFLICTS.md:253), [IMG-07](SOURCE_FINDINGS_AND_CONFLICTS.md:254), [DRF-U01](SOURCE_FINDINGS_AND_CONFLICTS.md:425), [DRF-A01](SOURCE_FINDINGS_AND_CONFLICTS.md:442), [DRF-A07](SOURCE_FINDINGS_AND_CONFLICTS.md:448), [GXF-01](SOURCE_FINDINGS_AND_CONFLICTS.md:485), [GXF-02](SOURCE_FINDINGS_AND_CONFLICTS.md:486), [GXF-03](SOURCE_FINDINGS_AND_CONFLICTS.md:487), [GXF-04](SOURCE_FINDINGS_AND_CONFLICTS.md:488), [GXF-05](SOURCE_FINDINGS_AND_CONFLICTS.md:489), [GXF-06](SOURCE_FINDINGS_AND_CONFLICTS.md:490), [GXF-07](SOURCE_FINDINGS_AND_CONFLICTS.md:491), [GXF-08](SOURCE_FINDINGS_AND_CONFLICTS.md:492), [GXF-09](SOURCE_FINDINGS_AND_CONFLICTS.md:493), [GXF-10](SOURCE_FINDINGS_AND_CONFLICTS.md:494), [GXF-11](SOURCE_FINDINGS_AND_CONFLICTS.md:495), [GXF-12](SOURCE_FINDINGS_AND_CONFLICTS.md:496), [GXF-13](SOURCE_FINDINGS_AND_CONFLICTS.md:497).

**Conversation upgrade lineage.** [CEX-09](SOURCE_FINDINGS_AND_CONFLICTS.md:191), [CEX-21](SOURCE_FINDINGS_AND_CONFLICTS.md:203), [DRF-A01](SOURCE_FINDINGS_AND_CONFLICTS.md:442), [DRF-A08](SOURCE_FINDINGS_AND_CONFLICTS.md:449), [DRF-A09](SOURCE_FINDINGS_AND_CONFLICTS.md:450), [DRF-A14](SOURCE_FINDINGS_AND_CONFLICTS.md:455). Read the full rows and their original conversation references; [the recheck](CONVERSATION_RECHECK.md) preserves the exact unit/exception routes.

<a id="up-o09-scenario_curves"></a>
#### O09.SCENARIO_CURVES — Exposure across price and surface shocks

[Existing definition, target and P0–P7](experiments/O.md#o09-scenario_curves) remain binding.

**Specific upgrade scope.** Construct joint source-price/tenor/shock response fields with gross, assumed signed and nonlinear reprice channels distinct.

**Local comparison.** Compare static Gamma, all local Greek/holdings cases and finite-shock summaries with unit and uncertainty checks.

**Additional cases.** Delta saturation; sign reversal; vanna/charm joint move; missing coverage; actual hedge not observed.

<a id="up-o10"></a>
### UP-O10 — Mechanical-versus-flow exposure-change decomposition

Parent: [O10](components/OPTIONS.md); [local phases](experiments/O.md#o10); [definition refinement](SYSTEM_REFINEMENT.md#sr-o10). Upgrade role: `measurement`.

**Starting idea.** Call every Gamma-board change new dealer flow.

**Existing improvement path.** Mechanical spot/surface/time, holdings and universe changes with ordered/symmetric attribution.

**Remaining weakness.** Aggregate attribution hides which contracts drive a change and may allocate interactions differently under different factor orderings.

**Further upgrade.** Produce contract-to-node-to-chain attribution with explicit joint interaction terms and common-universe controls. Compare exact bounded-factor Shapley/symmetric allocation with the cheaper ordered reference, reporting allocation sensitivity; model unexplained future-relevant residuals only after measured/assumed factors and data changes are exposed.

**Fair comparison.** Raw change, ordered decomposition, symmetric/Shapley alternatives and interpretable residual features.

**Evidence.** Reconstruction error, factor-order stability, source/coverage attribution, incremental information and compute.

**Additional local cases to implement.** Spot and IV move together; holdings scenario changes; contract birth/expiry; missing quote; node identity splits.

**Decision or system use.** Explain exposure evolution at useful spatial scales and test which residual changes add information beyond mechanical repricing.

**Exact reviewed source clauses.** [DTM-A05](SOURCE_FINDINGS_AND_CONFLICTS.md:63), [CEX-18](SOURCE_FINDINGS_AND_CONFLICTS.md:200), [IMG-01](SOURCE_FINDINGS_AND_CONFLICTS.md:248), [IMG-02](SOURCE_FINDINGS_AND_CONFLICTS.md:249), [IMG-03](SOURCE_FINDINGS_AND_CONFLICTS.md:250), [IMG-04](SOURCE_FINDINGS_AND_CONFLICTS.md:251), [IMG-05](SOURCE_FINDINGS_AND_CONFLICTS.md:252), [IMG-06](SOURCE_FINDINGS_AND_CONFLICTS.md:253), [IMG-07](SOURCE_FINDINGS_AND_CONFLICTS.md:254), [DRF-U05](SOURCE_FINDINGS_AND_CONFLICTS.md:429), [DRF-A01](SOURCE_FINDINGS_AND_CONFLICTS.md:442), [DRF-A13](SOURCE_FINDINGS_AND_CONFLICTS.md:454), [DRF-A15](SOURCE_FINDINGS_AND_CONFLICTS.md:456), [DRF-A16](SOURCE_FINDINGS_AND_CONFLICTS.md:457).

**Conversation upgrade lineage.** [CEX-21](SOURCE_FINDINGS_AND_CONFLICTS.md:203), [DRF-U05](SOURCE_FINDINGS_AND_CONFLICTS.md:429), [DRF-A13](SOURCE_FINDINGS_AND_CONFLICTS.md:454), [DRF-A17](SOURCE_FINDINGS_AND_CONFLICTS.md:458). Read the full rows and their original conversation references; [the recheck](CONVERSATION_RECHECK.md) preserves the exact unit/exception routes.

<a id="up-o10-joint_decomposition"></a>
#### O10.JOINT_DECOMPOSITION — Mechanical and flow change attribution

[Existing definition, target and P0–P7](experiments/O.md#o10-joint_decomposition) remain binding.

**Specific upgrade scope.** Attribute changes contract→node→chain with explicit interactions and fixed-universe controls.

**Local comparison.** Compare ordered and symmetric/Shapley decompositions, reconstruction/order sensitivity and future residual information.

**Additional cases.** Spot/IV/time interact; holdings assumption changes; node split; quote coverage loss.

<a id="up-o11"></a>
### UP-O11 — Node extraction, width and stable identity

Parent: [O11](components/OPTIONS.md); [local phases](experiments/O.md#o11); [definition refinement](SYSTEM_REFINEMENT.md#sr-o11). Upgrade role: `location`.

**Starting idea.** Pick the largest strike peaks or draw dots by size.

**Existing improvement path.** All supported concentration nodes, explicit widths/uncertainties and stable split/merge identity.

**Remaining weakness.** A single smoothing threshold creates fragile nodes, and point identity can jump between nearby peaks as weights change.

**Further upgrade.** Add multiscale density/prominence persistence and scenario-consensus node sets, retaining tiny supported nodes and uncertain identity. Match nodes by member overlap plus constrained transport/geometry, comparing with deterministic adjacent-strike clusters; do not equate smoothing-scale persistence with observed lifetime.

**Fair comparison.** Individual strikes/top peaks, adjacent clusters, multiscale persistence, scenario-consensus nodes and bounded learned widths.

**Evidence.** Node/support stability, split/merge fidelity, density/width-matched role value, sensitivity and runtime.

**Additional local cases to implement.** Equal peaks; broad plateau; tiny persistent cluster; scenario-dependent sign; missing strike; two nodes merge.

**Decision or system use.** Generate stable, well-supported spatial objects whose geometry and identity uncertainty can be used explicitly downstream.

**Exact reviewed source clauses.** [CEX-18](SOURCE_FINDINGS_AND_CONFLICTS.md:200), [IMG-01](SOURCE_FINDINGS_AND_CONFLICTS.md:248), [IMG-02](SOURCE_FINDINGS_AND_CONFLICTS.md:249), [IMG-03](SOURCE_FINDINGS_AND_CONFLICTS.md:250), [IMG-04](SOURCE_FINDINGS_AND_CONFLICTS.md:251), [IMG-05](SOURCE_FINDINGS_AND_CONFLICTS.md:252), [IMG-06](SOURCE_FINDINGS_AND_CONFLICTS.md:253), [IMG-07](SOURCE_FINDINGS_AND_CONFLICTS.md:254), [DRF-U03](SOURCE_FINDINGS_AND_CONFLICTS.md:427), [DRF-U05](SOURCE_FINDINGS_AND_CONFLICTS.md:429), [DRF-A07](SOURCE_FINDINGS_AND_CONFLICTS.md:448), [DRF-A08](SOURCE_FINDINGS_AND_CONFLICTS.md:449), [DRF-A16](SOURCE_FINDINGS_AND_CONFLICTS.md:457), [DRF-A19](SOURCE_FINDINGS_AND_CONFLICTS.md:460), [GXF-07](SOURCE_FINDINGS_AND_CONFLICTS.md:491).

**Conversation upgrade lineage.** [CEX-18](SOURCE_FINDINGS_AND_CONFLICTS.md:200), [DRF-U03](SOURCE_FINDINGS_AND_CONFLICTS.md:427), [DRF-A08](SOURCE_FINDINGS_AND_CONFLICTS.md:449). Read the full rows and their original conversation references; [the recheck](CONVERSATION_RECHECK.md) preserves the exact unit/exception routes.

<a id="up-o11-node_geometry"></a>
#### O11.NODE_GEOMETRY — Node support, uncertainty and identity

[Existing definition, target and P0–P7](experiments/O.md#o11-node_geometry) remain binding.

**Specific upgrade scope.** Use multiscale prominence/persistence and common-scenario node sets with explicit membership, width and identity uncertainty.

**Local comparison.** Compare strike/adjacent clusters, persistence and constrained matching at equal node density/contact width.

**Additional cases.** Plateau; tiny stable peak; merge/split; scenario-dependent sign; smoothing persistence differs from lifetime.

<a id="up-o12"></a>
### UP-O12 — Node persistence, migration and thickening/thinning experts

Parent: [O12](components/OPTIONS.md); [local phases](experiments/O.md#o12); [definition refinement](SYSTEM_REFINEMENT.md#sr-o12). Upgrade role: `forecast`.

**Starting idea.** Assume a growing or moving node will attract price.

**Existing improvement path.** Distinct mechanical/holdings growth, persistence, migration, thinning and conditional path roles.

**Remaining weakness.** Node-by-node scalar trends miss interacting clusters, uncertain lineage and the difference between temporary revaluation and persistent structural change.

**Further upgrade.** Fit a joint node transition model with lineage, neighboring topology, factor-attributed changes and scenario uncertainty. Compare independent slopes/hazards with a sparse relational duration model forecasting survival, displacement, width/mass change and role; retain a future exposure-field challenger from which nodes are derived.

**Fair comparison.** Persistence/static rank, independent hazards, attribution-conditioned relational transitions and field-evolution challenger.

**Evidence.** Joint survival/migration calibration, identity uncertainty, useful role lifetime, matched-density net and cost.

**Additional local cases to implement.** Node moves mechanically then returns; one splits into two; original grows only after observed delivery; missing chain mimics thinning.

**Decision or system use.** Forecast how useful option-derived structure evolves and how that changes future opportunities, with timing and provenance intact.

**Exact reviewed source clauses.** [CEX-19](SOURCE_FINDINGS_AND_CONFLICTS.md:201), [IMG-01](SOURCE_FINDINGS_AND_CONFLICTS.md:248), [IMG-02](SOURCE_FINDINGS_AND_CONFLICTS.md:249), [IMG-03](SOURCE_FINDINGS_AND_CONFLICTS.md:250), [IMG-04](SOURCE_FINDINGS_AND_CONFLICTS.md:251), [IMG-05](SOURCE_FINDINGS_AND_CONFLICTS.md:252), [IMG-06](SOURCE_FINDINGS_AND_CONFLICTS.md:253), [IMG-07](SOURCE_FINDINGS_AND_CONFLICTS.md:254), [DRF-A15](SOURCE_FINDINGS_AND_CONFLICTS.md:456), [DRF-A19](SOURCE_FINDINGS_AND_CONFLICTS.md:460).

**Conversation upgrade lineage.** [CEX-18](SOURCE_FINDINGS_AND_CONFLICTS.md:200), [DRF-U05](SOURCE_FINDINGS_AND_CONFLICTS.md:429), [DRF-A14](SOURCE_FINDINGS_AND_CONFLICTS.md:455), [DRF-A17](SOURCE_FINDINGS_AND_CONFLICTS.md:458). Read the full rows and their original conversation references; [the recheck](CONVERSATION_RECHECK.md) preserves the exact unit/exception routes.

<a id="up-o12-migration"></a>
#### O12.MIGRATION — Node movement and thickening

[Existing definition, target and P0–P7](experiments/O.md#o12-migration) remain binding.

**Specific upgrade scope.** Forecast joint center/width/mass changes and topology transitions rather than independent slopes.

**Local comparison.** Compare raw/mechanical/holdings-attributed changes, relational node transitions and exposure-field evolution.

**Additional cases.** One node splits; rank changes without movement; mapping shifts; normalization changes share.

<a id="up-o12-persistence"></a>
#### O12.PERSISTENCE — Node persistence and useful lifetime

[Existing definition, target and P0–P7](experiments/O.md#o12-persistence) remain binding.

**Specific upgrade scope.** Forecast useful lifetime with duration, lineage, neighbor topology and factor-attributed growth under common uncertainty.

**Local comparison.** Compare static rank, independent survival and relational duration models with exact retirement observations.

**Additional cases.** Newly born node; missing acquisition; mechanically transient mass; growth observed only after delivery.

<a id="up-o13"></a>
### UP-O13 — Exposure topology and source pattern grammar

Parent: [O13](components/OPTIONS.md); [local phases](experiments/O.md#o13); [definition refinement](SYSTEM_REFINEMENT.md#sr-o13). Upgrade role: `measurement`.

**Starting idea.** Read named Gamma-chart patterns as fixed market narratives.

**Existing improvement path.** Every named topology grammar is measurable, with continuous alternatives and no mandatory exclusions.

**Remaining weakness.** Narrative categories overlap and can hide the exact relative geometry or transition that carries information.

**Further upgrade.** Build a continuous relational grammar over ordered nodes, gaps, opposing/gross concentration, slope/curvature, scenario state and temporal change. Preserve each named detector and forecast its transitions; compare sparse grammar features with graph motifs and a small temporal model, separately scoring whipsaw, rainbow, squeeze, weakening, decoy, stairstep, delivery and event-failure branches.

**Fair comparison.** Each source pattern, continuous topology baseline, sparse relational motifs and optional temporal graph model.

**Evidence.** Pattern-definition fidelity, branch/path proper loss, robustness to node extraction, net contribution and complexity.

**Additional local cases to implement.** Same topology fits two names; king changes sign but remains largest magnitude; distant node never reachable; midrange useful; missing wing mimics air pocket.

**Decision or system use.** Convert the entire pattern vocabulary into interpretable geometry and dynamics that can be improved without treating narrative names as truths.

**Exact reviewed source clauses.** [DTM-A05](SOURCE_FINDINGS_AND_CONFLICTS.md:63), [CEX-09](SOURCE_FINDINGS_AND_CONFLICTS.md:191), [CEX-19](SOURCE_FINDINGS_AND_CONFLICTS.md:201), [IMG-01](SOURCE_FINDINGS_AND_CONFLICTS.md:248), [IMG-02](SOURCE_FINDINGS_AND_CONFLICTS.md:249), [IMG-03](SOURCE_FINDINGS_AND_CONFLICTS.md:250), [IMG-04](SOURCE_FINDINGS_AND_CONFLICTS.md:251), [IMG-05](SOURCE_FINDINGS_AND_CONFLICTS.md:252), [IMG-06](SOURCE_FINDINGS_AND_CONFLICTS.md:253), [IMG-07](SOURCE_FINDINGS_AND_CONFLICTS.md:254), [DRF-U05](SOURCE_FINDINGS_AND_CONFLICTS.md:429), [DRF-A08](SOURCE_FINDINGS_AND_CONFLICTS.md:449), [DRF-A15](SOURCE_FINDINGS_AND_CONFLICTS.md:456), [DRF-A16](SOURCE_FINDINGS_AND_CONFLICTS.md:457), [DRF-A19](SOURCE_FINDINGS_AND_CONFLICTS.md:460), [GXF-01](SOURCE_FINDINGS_AND_CONFLICTS.md:485), [GXF-02](SOURCE_FINDINGS_AND_CONFLICTS.md:486), [GXF-03](SOURCE_FINDINGS_AND_CONFLICTS.md:487), [GXF-04](SOURCE_FINDINGS_AND_CONFLICTS.md:488), [GXF-05](SOURCE_FINDINGS_AND_CONFLICTS.md:489), [GXF-06](SOURCE_FINDINGS_AND_CONFLICTS.md:490), [GXF-07](SOURCE_FINDINGS_AND_CONFLICTS.md:491), [GXF-08](SOURCE_FINDINGS_AND_CONFLICTS.md:492), [GXF-09](SOURCE_FINDINGS_AND_CONFLICTS.md:493), [GXF-10](SOURCE_FINDINGS_AND_CONFLICTS.md:494), [GXF-11](SOURCE_FINDINGS_AND_CONFLICTS.md:495), [GXF-12](SOURCE_FINDINGS_AND_CONFLICTS.md:496), [GXF-13](SOURCE_FINDINGS_AND_CONFLICTS.md:497).

**Conversation upgrade lineage.** [CEX-18](SOURCE_FINDINGS_AND_CONFLICTS.md:200), [CEX-19](SOURCE_FINDINGS_AND_CONFLICTS.md:201), [DRF-U05](SOURCE_FINDINGS_AND_CONFLICTS.md:429), [DRF-A16](SOURCE_FINDINGS_AND_CONFLICTS.md:457). Read the full rows and their original conversation references; [the recheck](CONVERSATION_RECHECK.md) preserves the exact unit/exception routes.

<a id="up-o13-grammar"></a>
#### O13.GRAMMAR — Vendor pattern vocabulary as measurable hypotheses

[Existing definition, target and P0–P7](experiments/O.md#o13-grammar) remain binding.

**Specific upgrade scope.** Represent every named source topology by continuous geometry and causal transitions alongside its exact detector.

**Local comparison.** Compare sparse grammar, graph motifs and optional temporal model with branch-specific metrics and no universal admission rule.

**Additional cases.** Whipsaw/rainbow overlap; squeeze/weakening; decoy distance; stairstep; delivery/revisit; news/OPEX failure.

<a id="up-o14"></a>
### UP-O14 — Within-chain strike-by-expiry pattern experts

Parent: [O14](components/OPTIONS.md); [local phases](experiments/O.md#o14); [definition refinement](SYSTEM_REFINEMENT.md#sr-o14). Upgrade role: `forecast`.

**Starting idea.** Summarize the chain with a few totals or one expiry.

**Existing improvement path.** Per-expiry specialists, coordinate-aware sets/graphs and causal temporal encoders.

**Remaining weakness.** Unstructured pooling can lose strike/tenor localization, while a large graph wastes capacity on sparse or redundant contracts.

**Further upgrade.** Compare a hierarchical low-rank strike-by-expiry representation with shared contract encoding, local coordinate interactions and temporal residuals. Retain absolute and normalized coordinates, support masks and lifecycle; benchmark information-matched engineered summaries, per-expiry fusion and structured encoders, with separate auxiliary targets and no label feedback.

**Fair comparison.** Scalar/tabular, per-expiry fusion, existing set/graph, hierarchical tensor factors and bounded temporal residual model.

**Evidence.** Common-target proper loss, small-node/localization error, missing-support robustness, net contribution and compute.

**Additional local cases to implement.** Same totals different strike allocation; expiry appears/disappears; permutation changes output; sparse wing; auxiliary OI label not mature.

**Decision or system use.** Capture joint spatial and temporal chain structure efficiently while proving which information and representation improve forecasts.

**Exact reviewed source clauses.** [CEX-19](SOURCE_FINDINGS_AND_CONFLICTS.md:201), [DRF-A08](SOURCE_FINDINGS_AND_CONFLICTS.md:449).

**Conversation upgrade lineage.** [CEX-19](SOURCE_FINDINGS_AND_CONFLICTS.md:201). Read the full rows and their original conversation references; [the recheck](CONVERSATION_RECHECK.md) preserves the exact unit/exception routes.

<a id="up-o14-chain_encoder"></a>
#### O14.CHAIN_ENCODER — Strike-by-expiry representation

[Existing definition, target and P0–P7](experiments/O.md#o14-chain_encoder) remain binding.

**Specific upgrade scope.** Compare hierarchical low-rank strike-expiry factors and shared contract/local interactions with per-expiry/set/graph baselines.

**Local comparison.** Control information, support and compute; retain absolute coordinates and separate auxiliary label maturity.

**Additional cases.** Same totals different localization; expiry birth; permutation; sparse wings; auxiliary leak.

<a id="up-o15"></a>
### UP-O15 — Signed options contracts and premium-flow ledger

Parent: [O15](components/OPTIONS.md); [local phases](experiments/O.md#o15); [definition refinement](SYSTEM_REFINEMENT.md#sr-o15). Upgrade role: `measurement`.

**Starting idea.** Count large calls/puts or sum premium.

**Existing improvement path.** Complete contracts/premium flow ledgers with side/unknown, expiry/cohort and feed-versus-aggregate distinctions.

**Remaining weakness.** Totals lose moneyness/expiry distribution, duration and unusual flow relative to a contract's expected activity.

**Further upgrade.** Add incremental strike/expiry/size flow surfaces, multi-memory signed/gross paths and exposure-normalized innovations, with exact reconciliation to the original ledger. Track breadth and concentration separately from intensity; preserve raw call/put and aggressor channels rather than compressing them into one sentiment score.

**Fair comparison.** Raw volume/premium, signed totals, spatial/temporal flow surfaces and simple residual summaries.

**Evidence.** Ledger conservation, support/scale stability, incremental path/OI information and runtime.

**Additional local cases to implement.** Top-N feed omits trades; same total spread across expiries; one expensive contract dominates premium; uncertain side; corrected trade.

**Decision or system use.** Retain where, when and how options trading occurred so downstream models can distinguish new information from routine activity.

**Exact reviewed source clauses.** [CEX-17](SOURCE_FINDINGS_AND_CONFLICTS.md:199), [DRF-A17](SOURCE_FINDINGS_AND_CONFLICTS.md:458).

**Conversation upgrade lineage.** [CEX-17](SOURCE_FINDINGS_AND_CONFLICTS.md:199), [DRF-A03](SOURCE_FINDINGS_AND_CONFLICTS.md:444), [DRF-A17](SOURCE_FINDINGS_AND_CONFLICTS.md:458). Read the full rows and their original conversation references; [the recheck](CONVERSATION_RECHECK.md) preserves the exact unit/exception routes.

<a id="up-o15-flow_channels"></a>
#### O15.FLOW_CHANNELS — Contracts, premium and sign scenarios

[Existing definition, target and P0–P7](experiments/O.md#o15-flow_channels) remain binding.

**Specific upgrade scope.** Add spatial/temporal contracts/premium flow surfaces and expected-activity innovations with complete ledger reconciliation.

**Local comparison.** Compare gross/call-put, aggressor signed/unknown and multi-memory residual channels by each expiry/cohort.

**Additional cases.** Top-N feed; price dominates premium; same totals different expiry; corrected trade; uncertain sign.

<a id="up-o16"></a>
### UP-O16 — Delta-, gamma-, vega-, vanna- and charm-weighted flow/CVD

Parent: [O16](components/OPTIONS.md); [local phases](experiments/O.md#o16); [definition refinement](SYSTEM_REFINEMENT.md#sr-o16). Upgrade role: `measurement`.

**Starting idea.** Weight signed flow by delta or Gamma.

**Existing improvement path.** Distinct delta/Gamma/vega/vanna/charm CVD/OHLC with event-frozen, arrival-repriced and revalued paths.

**Remaining weakness.** Separate local Greek totals hide nonlinear response and joint shock dependence; current revaluation can obscure the original traded information.

**Further upgrade.** For each eligible trade, retain frozen local sensitivities and a common finite-shock response vector from contemporaneously available valuation/scenarios. Aggregate by time/expiry/cohort with exact units and sign uncertainty; compare local weighted CVD with full repriced scenario-flow summaries and their subsequent mechanical revaluation, never calling them actual hedge flow.

**Fair comparison.** Contracts/premium only, every separate Greek channel, frozen/repriced alternatives and joint finite-shock flow representation.

**Evidence.** Sensitivity/repricing fidelity, path OHLC correctness, scenario uncertainty, each channel's incremental value and cost.

**Additional local cases to implement.** Vega omitted by a delta/Gamma-only shortcut; late receipt changes valuation; near-expiry saturation; mapping Jacobian changes; unlike units.

**Decision or system use.** Upgrade all weighted-flow channels together while preserving their individual experiments and the timing of the original trade information.

**Exact reviewed source clauses.** [CEX-17](SOURCE_FINDINGS_AND_CONFLICTS.md:199), [DRF-A17](SOURCE_FINDINGS_AND_CONFLICTS.md:458).

**Conversation upgrade lineage.** [DTM-A05](SOURCE_FINDINGS_AND_CONFLICTS.md:63), [CEX-17](SOURCE_FINDINGS_AND_CONFLICTS.md:199), [DRF-U04](SOURCE_FINDINGS_AND_CONFLICTS.md:428), [DRF-A01](SOURCE_FINDINGS_AND_CONFLICTS.md:442). Read the full rows and their original conversation references; [the recheck](CONVERSATION_RECHECK.md) preserves the exact unit/exception routes.

<a id="up-o16-delta"></a>
#### O16.DELTA — Delta-weighted CVD

[Existing definition, target and P0–P7](experiments/O.md#o16-delta) remain binding.

**Specific upgrade scope.** Retain event-frozen delta-equivalent and dollar channels, then add finite-shock response and correctly mapped mini-equivalent features.

**Local comparison.** Compare raw contracts/premium, fixed delta, full valuation and nonlinear response at identical trade cuts.

**Additional cases.** Underlying point value; mapping slope; arrival repricing; fractional feature never changes execution units.

<a id="up-o16-frozen_repriced"></a>
#### O16.FROZEN_REPRICED — Frozen versus revalued flow paths

[Existing definition, target and P0–P7](experiments/O.md#o16-frozen_repriced) remain binding.

**Specific upgrade scope.** Maintain event-frozen, arrival-repriced and later-revalued paths with mechanical change attribution and actual availability.

**Local comparison.** Compare their separate information/decision contributions while reconciling original ledger and true within-bar extrema.

**Additional cases.** Late receipt; quote after event unavailable then; future IV leak; revaluation mistaken for new flow.

<a id="up-o16-gamma"></a>
#### O16.GAMMA — Gamma-weighted CVD

[Existing definition, target and P0–P7](experiments/O.md#o16-gamma) remain binding.

**Specific upgrade scope.** Compare local Gamma-weighted flow with full finite-move delta/hedge-scenario response, preserving assumed sign and gross channels.

**Local comparison.** Score each CVD/OHLC, expiry/cohort and price-path contribution separately from ordinary traded CVD.

**Additional cases.** Near-expiry saturation; call/put sign heuristic; missed .01 scale; hedge sign opposite option sensitivity.

<a id="up-o16-vanna_charm"></a>
#### O16.VANNA_CHARM — Vanna and charm flow channels

[Existing definition, target and P0–P7](experiments/O.md#o16-vanna_charm) remain binding.

**Specific upgrade scope.** Separate vanna vol-shock and charm elapsed-time effects, then test their interactions with price/Gamma under common scenarios.

**Local comparison.** Compare each channel alone, combined local approximation and full reprice response; no arbitrary unit sum.

**Additional cases.** Time sign; large joint move; surface convention; near expiry; mapping variation.

<a id="up-o16-vega"></a>
#### O16.VEGA — Vega-weighted flow and CVD

[Existing definition, target and P0–P7](experiments/O.md#o16-vega) remain binding.

**Specific upgrade scope.** Keep a standalone vega flow/CVD/OHLC program and add common-vol-shock repricing response alongside other channels.

**Local comparison.** Compare vega versus delta/Gamma and full joint features with explicit IV fraction versus percentage-point units.

**Additional cases.** Vega omitted in aggregate shortcut; .01 convention; event surface missing; uncertain trade sign.

<a id="up-o17"></a>
### UP-O17 — Exposure-weighted strike center and bands

Parent: [O17](components/OPTIONS.md); [local phases](experiments/O.md#o17); [definition refinement](SYSTEM_REFINEMENT.md#sr-o17). Upgrade role: `measurement`.

**Starting idea.** Use one magnitude-weighted mean strike and symmetric bands.

**Existing improvement path.** Source above/below-mean centers, filter conventions, opening envelopes and robust alternatives.

**Remaining weakness.** A scalar center can sit between modes and change dramatically when an uncertain distant cluster appears.

**Further upgrade.** Represent the normalized magnitude distribution with weighted quantiles, cluster-specific centers and asymmetric envelopes across common scenarios. Compare source mean/filter/opening-envelope variants with distributional summaries and consensus versus scenario-specific center regions; uncertainty is a scenario range unless probabilistically calibrated.

**Fair comparison.** Exact source center, all/per-expiry, trimmed/quantile alternatives and multimodal scenario-aware distribution.

**Evidence.** Arithmetic/filter fidelity, center stability, multimodal support, role/path information and downstream net.

**Additional local cases to implement.** Two equal peaks; zero total; 50%-of-king differs from percentile; upper/lower split uses mean not spot; opening window incomplete.

**Decision or system use.** Describe the full center/band information without forcing a misleading mean to stand for a multimodal board.

**Exact reviewed source clauses.** [CEX-19](SOURCE_FINDINGS_AND_CONFLICTS.md:201), [CEX-20](SOURCE_FINDINGS_AND_CONFLICTS.md:202), [CEX-21](SOURCE_FINDINGS_AND_CONFLICTS.md:203), [DRF-U05](SOURCE_FINDINGS_AND_CONFLICTS.md:429), [DRF-A16](SOURCE_FINDINGS_AND_CONFLICTS.md:457).

**Conversation upgrade lineage.** [CEX-19](SOURCE_FINDINGS_AND_CONFLICTS.md:201), [CEX-20](SOURCE_FINDINGS_AND_CONFLICTS.md:202). Read the full rows and their original conversation references; [the recheck](CONVERSATION_RECHECK.md) preserves the exact unit/exception routes.

<a id="up-o17-center_bands"></a>
#### O17.CENTER_BANDS — Exposure centers and envelopes

[Existing definition, target and P0–P7](experiments/O.md#o17-center_bands) remain binding.

**Specific upgrade scope.** Add weighted quantiles, multimode centers and asymmetric scenario envelopes while retaining exact source filters/opening rules.

**Local comparison.** Compare mean/trimmed/quantile/all/per-expiry and multimodal features for stability and conditional roles.

**Additional cases.** Above/below mean versus spot; 50%-of-largest; zero mass; incomplete opening calibration; mean in valley.

<a id="up-o18"></a>
### UP-O18 — Flow breadth, concentration and OI-relative activity experts

Parent: [O18](components/OPTIONS.md); [local phases](experiments/O.md#o18); [definition refinement](SYSTEM_REFINEMENT.md#sr-o18). Upgrade role: `forecast`.

**Starting idea.** Use put/call or volume/OI ratios and ranked activity.

**Existing improvement path.** Distinct count, volume, premium, breadth, concentration, same-time relative flow and OI-relative features.

**Remaining weakness.** Composition changes and sparse denominators can look like unusual participation even when within-contract activity is normal.

**Further upgrade.** Fit partially pooled expected activity by contract lifecycle, tenor/moneyness, clock exposure and supported market state. Decompose breadth expansion, within-contract intensity, signed imbalance and composition migration; compare residual feature tensors with raw ratios and simple shrinkage before nonlinear models.

**Fair comparison.** Raw ratios/totals, shrunken relative activity, component residuals and structured interaction challenger.

**Evidence.** Count/flow target proper loss, sparse-denominator stability, decomposition fidelity, incremental path/net and compute.

**Additional local cases to implement.** New listings inflate breadth; tiny known OI; a few expensive options dominate premium; partial chain; changing expiry mix.

**Decision or system use.** Identify what is unusual about participation and whether its breadth, intensity or directional composition carries future information.

**Exact reviewed source clauses.** [CEX-11](SOURCE_FINDINGS_AND_CONFLICTS.md:193), [CRL-06](SOURCE_FINDINGS_AND_CONFLICTS.md:222), [DRF-A17](SOURCE_FINDINGS_AND_CONFLICTS.md:458).

**Conversation upgrade lineage.** [CEX-19](SOURCE_FINDINGS_AND_CONFLICTS.md:201). Read the full rows and their original conversation references; [the recheck](CONVERSATION_RECHECK.md) preserves the exact unit/exception routes.

<a id="up-o18-ratios_breadth"></a>
#### O18.RATIOS_BREADTH — Flow ratios, breadth and concentration

[Existing definition, target and P0–P7](experiments/O.md#o18-ratios_breadth) remain binding.

**Specific upgrade scope.** Decompose expected-adjusted breadth, within-contract intensity, signed imbalance and strike/expiry composition migration.

**Local comparison.** Compare raw and shrunken ratios with partially pooled residual activity models, scoring each numerator/denominator convention.

**Additional cases.** Tiny OI; new listings; price-weighted premium mix; missing contracts; same-time exposure.

<a id="up-o19"></a>
### UP-O19 — Futures-options-specific information experts

Parent: [O19](components/OPTIONS.md); [local phases](experiments/O.md#o19); [definition refinement](SYSTEM_REFINEMENT.md#sr-o19). Upgrade role: `forecast`.

**Starting idea.** Port equity-option indicators directly to futures options.

**Existing improvement path.** Style/UDS-aware native flow, OI/settlement and separately eligible trade/settlement-implied valuation.

**Remaining weakness.** Missing continuous quotes can block a large indicator stack even though valuation-free strike/expiry flow still contains distinct information.

**Further upgrade.** Build a native valuation-free contract/strike/expiry activity and signed-flow surface with report innovations and decoded outright/package structure. Add settlement/trade-implied sensitivity channels only on eligible cohorts, and compare their increment separately against native flow and OPRA information using matched dates.

**Fair comparison.** Futures price, OI/settlement, native flow-only, eligible valuation channels and combined cross-chain models.

**Evidence.** Native ledger fidelity, unique common-target information, support robustness, net contribution and data cost.

**Additional local cases to implement.** UDS legs unresolved; aggressor available without quotes; settlement arrives later; American style; underlying future differs by expiry.

**Decision or system use.** Use all supported native futures-option information without fabricating a quoted surface or losing the flow-only branch.

**Exact reviewed source clauses.** [CEX-11](SOURCE_FINDINGS_AND_CONFLICTS.md:193), [CEX-25](SOURCE_FINDINGS_AND_CONFLICTS.md:207), [CRL-05](SOURCE_FINDINGS_AND_CONFLICTS.md:221).

**Conversation upgrade lineage.** [CEX-11](SOURCE_FINDINGS_AND_CONFLICTS.md:193), [CEX-25](SOURCE_FINDINGS_AND_CONFLICTS.md:207), [CRL-05](SOURCE_FINDINGS_AND_CONFLICTS.md:221), [DRF-A06](SOURCE_FINDINGS_AND_CONFLICTS.md:447), [DRF-A11](SOURCE_FINDINGS_AND_CONFLICTS.md:452). Read the full rows and their original conversation references; [the recheck](CONVERSATION_RECHECK.md) preserves the exact unit/exception routes.

<a id="up-o19-futures_option_style"></a>
#### O19.FUTURES_OPTION_STYLE — Futures-options information portability

[Existing definition, target and P0–P7](experiments/O.md#o19-futures_option_style) remain binding.

**Specific upgrade scope.** Keep a complete valuation-free native flow/strike/expiry branch and add eligible settlement/trade/quoted sensitivity layers separately.

**Local comparison.** Compare native unique information against futures-only and OPRA channels on matched dates and true contract styles.

**Additional cases.** UDS unresolved; no quoted IV; aggressor available; underlier expiry; late settlement.

<a id="up-o20"></a>
### UP-O20 — Multi-leg, sweep and large-print ambiguity specialist

Parent: [O20](components/OPTIONS.md); [local phases](experiments/O.md#o20); [definition refinement](SYSTEM_REFINEMENT.md#sr-o20). Upgrade role: `measurement`.

**Starting idea.** Group nearby similar-size prints into a sweep or spread.

**Existing improvement path.** Condition flags, causal temporal/size/leg-ratio grouping and explicit package uncertainty.

**Remaining weakness.** One committed grouping can double-count trades or assign incompatible package directions with unjustified certainty.

**Further upgrade.** Create a causal hypothesis graph of mutually compatible package groupings, with bounded candidate matches and one-use trade accounting per hypothesis. Aggregate flow/sensitivity under each admissible grouping and report ambiguity; compare deterministic clustering with probabilistic weights only when labelled support justifies them.

**Fair comparison.** No grouping, condition/source-window rule, deterministic clustering and compatible-hypothesis ensemble.

**Evidence.** Trade-use conservation, grouping fidelity on eligible labels, sensitivity range, downstream increment and compute.

**Additional local cases to implement.** Two possible parents share a print; delayed leg; repeated size by chance; later leg changes hypothesis; incomplete ratio.

**Decision or system use.** Preserve economically meaningful package possibilities without turning a heuristic into known order identity or intent.

**Exact reviewed source clauses.** [CEX-17](SOURCE_FINDINGS_AND_CONFLICTS.md:199), [DRF-A02](SOURCE_FINDINGS_AND_CONFLICTS.md:443), [DRF-A04](SOURCE_FINDINGS_AND_CONFLICTS.md:445), [DRF-A17](SOURCE_FINDINGS_AND_CONFLICTS.md:458).

**Conversation upgrade lineage.** [CEX-17](SOURCE_FINDINGS_AND_CONFLICTS.md:199), [DRF-A02](SOURCE_FINDINGS_AND_CONFLICTS.md:443), [DRF-A03](SOURCE_FINDINGS_AND_CONFLICTS.md:444), [DRF-A16](SOURCE_FINDINGS_AND_CONFLICTS.md:457). Read the full rows and their original conversation references; [the recheck](CONVERSATION_RECHECK.md) preserves the exact unit/exception routes.

<a id="up-o20-trade_ambiguity"></a>
#### O20.TRADE_AMBIGUITY — Complex trades and sweep uncertainty

[Existing definition, target and P0–P7](experiments/O.md#o20-trade_ambiguity) remain binding.

**Specific upgrade scope.** Build a causal compatible-grouping hypothesis graph with one-use trade accounting and bounded grouping alternatives.

**Local comparison.** Compare condition/window heuristics and uncertainty ensembles; probabilistic labels require reliable package evidence.

**Additional cases.** Shared trade in two hypotheses; delayed leg; coincidental size; incomplete ratio; future grouping.

<a id="up-o21"></a>
### UP-O21 — Options uncertainty and applicability propagation

Parent: [O21](components/OPTIONS.md); [local phases](experiments/O.md#o21); [definition refinement](SYSTEM_REFINEMENT.md#sr-o21). Upgrade role: `decision`.

**Starting idea.** Gate options on one freshness or confidence flag.

**Existing improvement path.** Common joint uncertainty propagated through valuation, exposure, nodes and path forecasts.

**Remaining weakness.** Large upstream uncertainty can be harmless to the chosen action, while a small uncertainty near a ranking boundary can matter greatly.

**Further upgrade.** Add downstream decision-sensitivity attribution across quote, sign, surface, holdings, mapping and model scenarios. Compare source-validity masks, forecast-spread gates and action-instability/value-of-better-measurement diagnostics; keep early quality ports separate from later decision sensitivity to preserve the DAG.

**Fair comparison.** Point estimate, joint scenarios, reliability meta-gate and decision-relevant sensitivity rules.

**Evidence.** Calibration, selected risk/coverage/net, disagreement attribution, uncertainty width and marginal data/compute value.

**Additional local cases to implement.** All scenarios choose same action; one uncertain node reverses ranking; correlated common errors; duplicate evidence shrinks interval.

**Decision or system use.** Use options uncertainty according to its effect on decisions and identify which missing precision would actually be worth improving.

**Exact reviewed source clauses.** [CEX-10](SOURCE_FINDINGS_AND_CONFLICTS.md:192), [CEX-23](SOURCE_FINDINGS_AND_CONFLICTS.md:205), [DRF-U01](SOURCE_FINDINGS_AND_CONFLICTS.md:425), [DRF-A11](SOURCE_FINDINGS_AND_CONFLICTS.md:452), [DRF-A14](SOURCE_FINDINGS_AND_CONFLICTS.md:455), [GXF-01](SOURCE_FINDINGS_AND_CONFLICTS.md:485), [GXF-02](SOURCE_FINDINGS_AND_CONFLICTS.md:486), [GXF-03](SOURCE_FINDINGS_AND_CONFLICTS.md:487), [GXF-04](SOURCE_FINDINGS_AND_CONFLICTS.md:488), [GXF-05](SOURCE_FINDINGS_AND_CONFLICTS.md:489), [GXF-06](SOURCE_FINDINGS_AND_CONFLICTS.md:490), [GXF-07](SOURCE_FINDINGS_AND_CONFLICTS.md:491), [GXF-08](SOURCE_FINDINGS_AND_CONFLICTS.md:492), [GXF-09](SOURCE_FINDINGS_AND_CONFLICTS.md:493), [GXF-10](SOURCE_FINDINGS_AND_CONFLICTS.md:494), [GXF-11](SOURCE_FINDINGS_AND_CONFLICTS.md:495), [GXF-12](SOURCE_FINDINGS_AND_CONFLICTS.md:496), [GXF-13](SOURCE_FINDINGS_AND_CONFLICTS.md:497), [K10-02](SOURCE_FINDINGS_AND_CONFLICTS.md:640), [K18-02](SOURCE_FINDINGS_AND_CONFLICTS.md:653), [CCS-04](SOURCE_FINDINGS_AND_CONFLICTS.md:684), [OBT-07](SOURCE_FINDINGS_AND_CONFLICTS.md:756).

**Conversation upgrade lineage.** [DRF-A14](SOURCE_FINDINGS_AND_CONFLICTS.md:455). Read the full rows and their original conversation references; [the recheck](CONVERSATION_RECHECK.md) preserves the exact unit/exception routes.

<a id="up-o21-sensitivity"></a>
#### O21.SENSITIVITY — Uncertainty propagation and support

[Existing definition, target and P0–P7](experiments/O.md#o21-sensitivity) remain binding.

**Specific upgrade scope.** Attribute joint uncertainty to downstream action/rank sensitivity and the potential value of better measurement.

**Local comparison.** Compare point, full scenario, reliability and action-instability gates while preserving early/late port order.

**Additional cases.** Same action despite wide forecasts; one uncertain node flips choice; correlated errors; duplicated evidence.

<a id="up-o22"></a>
### UP-O22 — Options node/path and actionable-role forecast experts

Parent: [O22](components/OPTIONS.md); [local phases](experiments/O.md#o22); [definition refinement](SYSTEM_REFINEMENT.md#sr-o22). Upgrade role: `forecast`.

**Starting idea.** Trade the strongest node as a universal magnet or reversal.

**Existing improvement path.** Independent reach, role, runner, room and lifetime heads; mediated and direct predictive challengers.

**Remaining weakness.** Separate heads can disagree on path order and hide whether latent holdings add anything beyond observable chain/flow information.

**Further upgrade.** Use a candidate-landmark path/role model with joint contact, departure, retrace, continuation and duration outputs under common scenarios. Compare mediated exposure features, direct observables and their residual mixture with factorial representation/information controls; integrate pre-touch arrival uncertainty without importing realized arrival features.

**Fair comparison.** Static node rule, simple role model, direct/mediated existing heads and coherent relational path model/mixture.

**Evidence.** Joint role/time proper loss, calibration, mediation-versus-direct increment, lifetime and complete-policy net.

**Additional local cases to implement.** Node predicts touch but not useful departure; runner after retrace; source-only opportunity; small node; latent model improves OI but harms action value.

**Decision or system use.** Forecast what option structure means for attainable receiver paths and determine whether each latent or direct information path earns its complexity.

**Exact reviewed source clauses.** [DRF-U03](SOURCE_FINDINGS_AND_CONFLICTS.md:427), [DRF-A05](SOURCE_FINDINGS_AND_CONFLICTS.md:446), [DRF-A09](SOURCE_FINDINGS_AND_CONFLICTS.md:450), [DRF-A15](SOURCE_FINDINGS_AND_CONFLICTS.md:456), [DRF-A18](SOURCE_FINDINGS_AND_CONFLICTS.md:459), [K10-02](SOURCE_FINDINGS_AND_CONFLICTS.md:640).

**Conversation upgrade lineage.** [CEX-09](SOURCE_FINDINGS_AND_CONFLICTS.md:191), [CRL-13](SOURCE_FINDINGS_AND_CONFLICTS.md:229), [DRF-U01](SOURCE_FINDINGS_AND_CONFLICTS.md:425), [DRF-A09](SOURCE_FINDINGS_AND_CONFLICTS.md:450), [DRF-A18](SOURCE_FINDINGS_AND_CONFLICTS.md:459). Read the full rows and their original conversation references; [the recheck](CONVERSATION_RECHECK.md) preserves the exact unit/exception routes.

<a id="up-o22-runner"></a>
#### O22.RUNNER — Node reaction and sustained departure

[Existing definition, target and P0–P7](experiments/O.md#o22-runner) remain binding.

**Specific upgrade scope.** Use coherent landmark contact/departure/retrace/runner/time outputs and direct-versus-mediated residual comparisons.

**Local comparison.** Compare simple node rule, direct chain/flow, latent exposure and their mixture with exact information/capacity controls.

**Additional cases.** Touch without value; retrace then runner; small node; no receiver local touch; pre-touch arrival uncertainty.

<a id="up-o23"></a>
### UP-O23 — Per-expiry max-pain settlement-payoff benchmark

Parent: [O23](components/OPTIONS.md); [local phases](experiments/O.md#o23); [definition refinement](SYSTEM_REFINEMENT.md#sr-o23). Upgrade role: `measurement`.

**Starting idea.** Use the max-pain minimizing strike as a price target.

**Existing improvement path.** Exact compatible terminal payoff curve and full minimizer set with simple role controls.

**Remaining weakness.** The minimizer discards slope, concentration and asymmetric payout geometry, and may not be stable to incomplete OI support.

**Further upgrade.** Retain the full piecewise-linear payout curve, one-sided slopes, normalized excess payout, minimizer interval and strike-local slope changes across valid OI/support scenarios. Compare these deterministic curve features with the scalar minimizer, nearby round strikes and other node/profile references; predictive use remains an independent hypothesis.

**Fair comparison.** Reference payoff arithmetic, minimizer-only, full curve summaries and shrunken conditional role model.

**Evidence.** Payoff/slope parity, minimizer stability, placebo-adjusted path/role evidence and net contribution.

**Additional local cases to implement.** Flat minimum; unbounded valid domain edge; missing wing; adjusted payoff; zero OI; same minimum with different slopes.

**Decision or system use.** Extract all supported information from the benchmark curve without calling hypothetical payout a force or observed dealer objective.

**Exact reviewed source clauses.** [GXF-07](SOURCE_FINDINGS_AND_CONFLICTS.md:491).

<a id="up-o23-payoff_set"></a>
#### O23.PAYOFF_SET — Max-pain minimizer set

[Existing definition, target and P0–P7](experiments/O.md#o23-payoff_set) remain binding.

**Specific upgrade scope.** Add exact payoff slopes, normalized excess payout and local slope changes to the complete minimizing interval.

**Local comparison.** Compare scalar minimizer and full curve features against round-strike/ordinary-node controls; predictive value remains separate.

**Additional cases.** Flat minimum; missing wing; adjusted deliverable; same minimum different slope; zero OI.

<a id="family-x"></a>
## Cross-market information

<a id="up-x01"></a>
### UP-X01 — Asynchronous cross-market alignment

Parent: [X01](components/CROSS_ASSET.md); [local phases](experiments/X.md#x01); [definition refinement](SYSTEM_REFINEMENT.md#sr-x01). Upgrade role: `engineering`.

**Starting idea.** Synchronize all markets into the same bar timestamp.

**Existing improvement path.** Backward availability joins, source ages, event-triggered grids and latency uncertainty.

**Remaining weakness.** Coarse snapshots lose event order, while naive event merges can overreact to frequent sources or compare unequal information delays.

**Further upgrade.** Build a multi-rate causal event view with source-liveness and publication-age channels, bounded event coalescing and explicit partial order for uncertain timing. Compare common-clock and source-triggered decisions at matched observation/delay budgets; downstream lag models use admitted observations only.

**Fair comparison.** Common-minute baseline, literal event merge, multi-rate coalesced views and latency scenarios.

**Evidence.** As-of/order fidelity, retained fresh information, forecast/value versus delay, event load and runtime.

**Additional local cases to implement.** ETF minute spans many futures ticks; same timestamp uncertain order; quiet healthy source; duplicated snapshot; delayed source burst.

**Decision or system use.** Preserve usable cross-market timing efficiently without manufacturing simultaneity or future access.

**Exact reviewed source clauses.** [CEX-07](SOURCE_FINDINGS_AND_CONFLICTS.md:189), [PIN022-03](SOURCE_FINDINGS_AND_CONFLICTS.md:896).

<a id="up-x01-async"></a>
#### X01.ASYNC — Asynchronous information alignment

[Existing definition, target and P0–P7](experiments/X.md#x01-async) remain binding.

**Specific upgrade scope.** Use a multi-rate event view with partial ordering, source liveness/age and bounded coalescing.

**Local comparison.** Compare clock/event-triggered grids under equal admitted information and measured delay, not invented simultaneity.

**Additional cases.** ETF bar spans futures ticks; tied timestamps; delayed source; unchanged healthy state.

<a id="up-x02"></a>
### UP-X02 — Related-instrument coordinate and sensitivity mapping

Parent: [X02](components/CROSS_ASSET.md); [local phases](experiments/X.md#x02); [definition refinement](SYSTEM_REFINEMENT.md#sr-x02). Upgrade role: `measurement`.

**Starting idea.** Convert a source strike with a fixed price ratio.

**Existing improvement path.** Causal affine/basis/parity mappings with Jacobians, domains and uncertainty.

**Remaining weakness.** A single point estimate ignores carry/maturity dependence, structural changes and correlated error across mapped nodes.

**Further upgrade.** Use a joint coordinate/basis state with explicit carry/expiry structure and residual bands, comparing robust filtered updates with fixed/rolling maps. Propagate common mapping scenarios through all related objects and sensitivities, test round-trip/domain behavior and compare joint observation models when both coordinates are noisy; keep predictive cross-index transmission separate.

**Fair comparison.** Fixed ratio, affine/filter/parity baseline, structured joint basis model and uncertainty-propagating map.

**Evidence.** Out-of-sample mapping error/coverage, coordinate/Jacobian fidelity, stability, mapped action robustness and cost.

**Additional local cases to implement.** Noisy source and receiver; roll; same underlying different maturity; inverse regression not algebraic inverse; cash proxy touch unknown.

**Decision or system use.** Map related instruments consistently and quantify whether mapping uncertainty matters to an actual one-mini decision.

**Exact reviewed source clauses.** [DTM-A06](SOURCE_FINDINGS_AND_CONFLICTS.md:64), [CEX-13](SOURCE_FINDINGS_AND_CONFLICTS.md:195), [CEX-16](SOURCE_FINDINGS_AND_CONFLICTS.md:198), [DRF-U09](SOURCE_FINDINGS_AND_CONFLICTS.md:433), [DRF-A11](SOURCE_FINDINGS_AND_CONFLICTS.md:452), [GXF-02](SOURCE_FINDINGS_AND_CONFLICTS.md:486), [GXF-03](SOURCE_FINDINGS_AND_CONFLICTS.md:487).

**Conversation upgrade lineage.** [DTM-A06](SOURCE_FINDINGS_AND_CONFLICTS.md:64), [CEX-13](SOURCE_FINDINGS_AND_CONFLICTS.md:195), [CEX-16](SOURCE_FINDINGS_AND_CONFLICTS.md:198), [DRF-A11](SOURCE_FINDINGS_AND_CONFLICTS.md:452), [DRF-A23](SOURCE_FINDINGS_AND_CONFLICTS.md:464). Read the full rows and their original conversation references; [the recheck](CONVERSATION_RECHECK.md) preserves the exact unit/exception routes.

<a id="up-x02-parity_basis"></a>
#### X02.PARITY_BASIS — Forward, basis and coordinate mapping

[Existing definition, target and P0–P7](experiments/X.md#x02-parity_basis) remain binding.

**Specific upgrade scope.** Fit structured coordinate/carry/basis state and common mapping uncertainty with explicit forward/maturity domains.

**Local comparison.** Compare fixed/affine/parity/filter maps and valid round trips; distinguish noisy-coordinate joint model from inverse regression.

**Additional cases.** Cash proxy not observed touch; roll; different maturity; Jacobian units; shared mapping error.

<a id="up-x03"></a>
### UP-X03 — Nasdaq-chain comparison and NDX hypothesis

Parent: [X03](components/CROSS_ASSET.md); [local phases](experiments/X.md#x03); [definition refinement](SYSTEM_REFINEMENT.md#sr-x03). Upgrade role: `forecast`.

**Starting idea.** Assume one Nasdaq options chain is best.

**Existing improvement path.** Separate NDX monthly, NDXP, QQQ and native futures-options experts plus matched joint comparisons.

**Remaining weakness.** Overlapping chains may share most information while differing in settlement, investor activity, coverage and residual signals.

**Further upgrade.** Decompose chain forecasts into common Nasdaq state and chain-specific residual information, with settlement/lifecycle/support factors. Compare hierarchical residual fusion and sparse cross-chain interactions against simple pooled forecasts, preserving each chain, small-node and source-only cohort plus native flow-only eligibility.

**Fair comparison.** Futures/QQQ/each NDX-family/native source alone, pairs/full family, linear fusion and common-plus-residual hierarchy.

**Evidence.** Common-target loss, unique/joint information, coverage/density-controlled net, uncertainty and compute.

**Additional local cases to implement.** Best chain changes by horizon; monthly versus daily expiry; unequal coverage; small useful node; shared shock counted repeatedly.

**Decision or system use.** Determine which Nasdaq sources add distinct information and whether their interactions improve the receiver policy.

**Exact reviewed source clauses.** [DTM-A06](SOURCE_FINDINGS_AND_CONFLICTS.md:64), [CEX-16](SOURCE_FINDINGS_AND_CONFLICTS.md:198), [GXF-02](SOURCE_FINDINGS_AND_CONFLICTS.md:486).

**Conversation upgrade lineage.** [DTM-A06](SOURCE_FINDINGS_AND_CONFLICTS.md:64), [CEX-16](SOURCE_FINDINGS_AND_CONFLICTS.md:198). Read the full rows and their original conversation references; [the recheck](CONVERSATION_RECHECK.md) preserves the exact unit/exception routes.

<a id="up-x03-ndx_qqq"></a>
#### X03.NDX_QQQ — Nasdaq chain specialists

[Existing definition, target and P0–P7](experiments/X.md#x03-ndx_qqq) remain binding.

**Specific upgrade scope.** Separate common Nasdaq state and NDX-monthly/NDXP/QQQ/native residual information with support/settlement factors.

**Local comparison.** Compare all single/pair/full sources, simple fusion and sparse residual interactions at matched density/cohorts.

**Additional cases.** Small node; no local touch; different expiries; native flow without quotes; unequal data dates.

<a id="up-x04"></a>
### UP-X04 — S&P-chain comparison and fair ES alternative

Parent: [X04](components/CROSS_ASSET.md); [local phases](experiments/X.md#x04); [definition refinement](SYSTEM_REFINEMENT.md#sr-x04). Upgrade role: `forecast`.

**Starting idea.** Transfer Nasdaq assumptions to S&P or choose ES from raw averages.

**Existing improvement path.** Separate SPX/SPXW/SPY/native ES information and fair one-mini NQ/ES policies.

**Remaining weakness.** Information value and execution feasibility can be confounded, especially across settlement conventions and unequal source histories.

**Further upgrade.** Build common S&P versus chain-specific residual forecasts with explicit AM/PM settlement and support, mirroring X03's controlled hierarchy. Separately pass predictions into actual one-mini ES economics and P12's budget-fit comparison; report full-supported and matched-date evidence without merging their claims.

**Fair comparison.** Each S&P chain/native source, transparent fusion, residual hierarchy, and matched NQ/ES complete policies.

**Evidence.** Source increment, settlement-specific calibration, net/risk feasibility, paired uncertainty and cost.

**Additional local cases to implement.** SPX AM expiry differs from SPXW PM; ES native quote gaps; NQ larger history; same forecast quality but different affordable stop.

**Decision or system use.** Improve S&P information and assess ES fairly without mistaking a feature advantage for an execution advantage.

**Exact reviewed source clauses.** [DTM-A06](SOURCE_FINDINGS_AND_CONFLICTS.md:64), [CEX-16](SOURCE_FINDINGS_AND_CONFLICTS.md:198), [GXF-02](SOURCE_FINDINGS_AND_CONFLICTS.md:486).

<a id="up-x04-spx_spy"></a>
#### X04.SPX_SPY — S&P family and fair ES comparison

[Existing definition, target and P0–P7](experiments/X.md#x04-spx_spy) remain binding.

**Specific upgrade scope.** Decompose S&P common and SPX/SPXW/SPY/native residual forecasts, then evaluate actual ES economics separately.

**Local comparison.** Compare source information and NQ/ES execution choice on matched dates, units, model budgets and mandatory constraints.

**Additional cases.** AM/PM settlement; native quote gap; NQ longer history; different stop affordability.

<a id="up-x05"></a>
### UP-X05 — Source reaction to receiver opportunity transmission

Parent: [X05](components/CROSS_ASSET.md); [local phases](experiments/X.md#x05); [definition refinement](SYSTEM_REFINEMENT.md#sr-x05). Upgrade role: `forecast`.

**Starting idea.** A source level reaction should make the receiver follow.

**Existing improvement path.** Explicit source-event availability, realized receiver movement, residual basis/lag and no-local-touch cohorts.

**Remaining weakness.** A fixed event flag loses remaining information lifetime and can mistake a shared contemporaneous shock for predictive transmission.

**Further upgrade.** Estimate conditional receiver innovations relative to a receiver-only/common-market baseline, using source-event geometry, intensity, lag and uncertainty. Compare distributed response kernels and event-survival models, distinguishing fast already-realized response from slower remaining effect; source-event matching and negative controls use only admissible past information.

**Fair comparison.** Receiver-only, simple source-return/event regression, residual transmission kernels and duration-aware event model.

**Evidence.** Incremental future path/time loss, lag stability, conditional controls, source-only policy net and latency sensitivity.

**Additional local cases to implement.** Receiver moves before source receipt; contradictory sources; source node never touched; common announcement; source event expires while waiting.

**Decision or system use.** Forecast the remaining receiver opportunity attributable predictively to fresh source information, without claiming structural causality or requiring local touch.

**Exact reviewed source clauses.** [DTM-A06](SOURCE_FINDINGS_AND_CONFLICTS.md:64), [DTM-A14](SOURCE_FINDINGS_AND_CONFLICTS.md:72), [DTM-A18](SOURCE_FINDINGS_AND_CONFLICTS.md:76), [CEX-13](SOURCE_FINDINGS_AND_CONFLICTS.md:195), [CD1-02](SOURCE_FINDINGS_AND_CONFLICTS.md:395), [CD1-03](SOURCE_FINDINGS_AND_CONFLICTS.md:396), [DRF-U09](SOURCE_FINDINGS_AND_CONFLICTS.md:433), [DRF-A23](SOURCE_FINDINGS_AND_CONFLICTS.md:464).

**Conversation upgrade lineage.** [DTM-A06](SOURCE_FINDINGS_AND_CONFLICTS.md:64), [DTM-A14](SOURCE_FINDINGS_AND_CONFLICTS.md:72), [DTM-A18](SOURCE_FINDINGS_AND_CONFLICTS.md:76), [CEX-13](SOURCE_FINDINGS_AND_CONFLICTS.md:195), [DRF-U09](SOURCE_FINDINGS_AND_CONFLICTS.md:433), [DRF-A11](SOURCE_FINDINGS_AND_CONFLICTS.md:452), [DRF-A23](SOURCE_FINDINGS_AND_CONFLICTS.md:464). Read the full rows and their original conversation references; [the recheck](CONVERSATION_RECHECK.md) preserves the exact unit/exception routes.

<a id="up-x05-source_only"></a>
#### X05.SOURCE_ONLY — Source-event receiver transmission

[Existing definition, target and P0–P7](experiments/X.md#x05-source_only) remain binding.

**Specific upgrade scope.** Estimate receiver innovation and remaining event lifetime after actual source availability, controlling past common-market movement.

**Local comparison.** Compare receiver-only, source event/return, distributed response and duration models across no-touch/already-reacted/contradictory cohorts.

**Additional cases.** Receiver moved before receipt; source expires; common announcement; no local level.

<a id="up-x06"></a>
### UP-X06 — Joint multi-chain, multi-asset temporal pattern model

Parent: [X06](components/CROSS_ASSET.md); [local phases](experiments/X.md#x06); [definition refinement](SYSTEM_REFINEMENT.md#sr-x06). Upgrade role: `forecast`.

**Starting idea.** Combine chains or markets by averaging signals.

**Existing improvement path.** Hierarchical contract/expiry/chain/asset sets with coordinate-aware graph/time alternatives.

**Remaining weakness.** A large joint model can learn coverage artifacts or repeat common factors, while its useful cross-source interactions remain opaque.

**Further upgrade.** Compare a shared low-rank common-state model with sparse, directed, lagged residual interactions and uncertainty-aware source masks. Add graph/attention residuals only after this structured baseline; preserve per-source/expiry ablations, interaction tests and equal information/compute comparisons, with all current-cut ports acyclic.

**Fair comparison.** Additive/per-chain fusion, regularized interactions, common-plus-residual hierarchy and bounded set/graph/temporal challengers.

**Evidence.** Joint target proper loss, unique/interaction contribution, missing-pattern transfer, complete net and compute.

**Additional local cases to implement.** One new feed changes regime label; common factor repeated many times; source order permutation; incompatible coordinates; unavailable intraday chain.

**Decision or system use.** Model useful joint information across the entire supported source hierarchy while making redundancy and real interactions measurable.

**Exact reviewed source clauses.** [DTM-A06](SOURCE_FINDINGS_AND_CONFLICTS.md:64), [CEX-13](SOURCE_FINDINGS_AND_CONFLICTS.md:195), [CEX-18](SOURCE_FINDINGS_AND_CONFLICTS.md:200), [CEX-19](SOURCE_FINDINGS_AND_CONFLICTS.md:201), [IMG-01](SOURCE_FINDINGS_AND_CONFLICTS.md:248), [IMG-02](SOURCE_FINDINGS_AND_CONFLICTS.md:249), [IMG-03](SOURCE_FINDINGS_AND_CONFLICTS.md:250), [IMG-04](SOURCE_FINDINGS_AND_CONFLICTS.md:251), [IMG-05](SOURCE_FINDINGS_AND_CONFLICTS.md:252), [IMG-06](SOURCE_FINDINGS_AND_CONFLICTS.md:253), [IMG-07](SOURCE_FINDINGS_AND_CONFLICTS.md:254), [DRF-U05](SOURCE_FINDINGS_AND_CONFLICTS.md:429).

**Conversation upgrade lineage.** [DTM-A06](SOURCE_FINDINGS_AND_CONFLICTS.md:64), [CEX-13](SOURCE_FINDINGS_AND_CONFLICTS.md:195), [CEX-18](SOURCE_FINDINGS_AND_CONFLICTS.md:200), [CEX-19](SOURCE_FINDINGS_AND_CONFLICTS.md:201), [DRF-U05](SOURCE_FINDINGS_AND_CONFLICTS.md:429), [DRF-A23](SOURCE_FINDINGS_AND_CONFLICTS.md:464). Read the full rows and their original conversation references; [the recheck](CONVERSATION_RECHECK.md) preserves the exact unit/exception routes.

<a id="up-x06-set_graph_time"></a>
#### X06.SET_GRAPH_TIME — Joint information and representation tests

[Existing definition, target and P0–P7](experiments/X.md#x06-set_graph_time) remain binding.

**Specific upgrade scope.** Add a common-factor hierarchy plus sparse directed lagged residual interactions before graph/attention complexity.

**Local comparison.** Compare additive, per-chain, low-rank/residual and bounded graph/time models with exact support and compute controls.

**Additional cases.** Duplicate common signal; source permutation; acquisition regime; incompatible coordinates; current-cut cycle.

<a id="up-x07"></a>
### UP-X07 — Relative strength, cross-flow SMT and lead-lag experts

Parent: [X07](components/CROSS_ASSET.md); [local phases](experiments/X.md#x07); [definition refinement](SYSTEM_REFINEMENT.md#sr-x07). Upgrade role: `forecast`.

**Starting idea.** Use price SMT, a ratio or cross-market CVD disagreement.

**Existing improvement path.** Own-reference breach order, normalized cohort flow, residual returns and lagged forecasts.

**Remaining weakness.** Binary SMT and raw correlations ignore expected common movement, unequal activity clocks and time-varying residual coupling.

**Further upgrade.** Build joint price/flow innovation channels after train-fitted common-factor and scale adjustment, with explicit breach magnitude/order and distributed causal lags. Compare stable shrinkage transfer kernels and duration-aware divergences across every price/cohort case; score after realistic availability and execution delay.

**Fair comparison.** Source SMT/ratio, linear VAR/ridge, normalized residual lag features and sparse nonlinear interactions.

**Evidence.** Per-case future path loss, lead-lag stability, conditional calibration, redundancy and net after latency.

**Additional local cases to implement.** Same movement explained by common factor; unequal contract units; one stale stream; cohort definitions differ; breach order reverses with valid delay.

**Decision or system use.** Test which cross-market disagreements contain fresh receiver information rather than scale, clock or common-factor artifacts.

**Exact reviewed source clauses.** [JTR-07](SOURCE_FINDINGS_AND_CONFLICTS.md:24), [JXA-23](SOURCE_FINDINGS_AND_CONFLICTS.md:122), [JFN-09](SOURCE_FINDINGS_AND_CONFLICTS.md:143), [JCV-A05](SOURCE_FINDINGS_AND_CONFLICTS.md:164), [CEX-07](SOURCE_FINDINGS_AND_CONFLICTS.md:189), [CD1-04](SOURCE_FINDINGS_AND_CONFLICTS.md:397), [OSF-07](SOURCE_FINDINGS_AND_CONFLICTS.md:801), [OSF-09](SOURCE_FINDINGS_AND_CONFLICTS.md:803), [PIN003-04](SOURCE_FINDINGS_AND_CONFLICTS.md:822), [PIN072-02](SOURCE_FINDINGS_AND_CONFLICTS.md:1046).

**Conversation upgrade lineage.** [CEX-07](SOURCE_FINDINGS_AND_CONFLICTS.md:189). Read the full rows and their original conversation references; [the recheck](CONVERSATION_RECHECK.md) preserves the exact unit/exception routes.

<a id="up-x07-flow_smt"></a>
#### X07.FLOW_SMT — Cross-market cohort-flow SMT

[Existing definition, target and P0–P7](experiments/X.md#x07-flow_smt) remain binding.

**Specific upgrade scope.** Add activity/contract-scale-normalized cohort-flow innovations and cross-price/flow response kernels.

**Local comparison.** Compare ordinary/fixed/adaptive/soft cohort cases with compatible provider aggregation and matched timing.

**Additional cases.** NQ/ES raw contracts incomparable; sparse cohort; shared trade-size artifact; asynchronous quotes.

<a id="up-x07-price_smt"></a>
#### X07.PRICE_SMT — Price relative strength and breach order

[Existing definition, target and P0–P7](experiments/X.md#x07-price_smt) remain binding.

**Specific upgrade scope.** Use standardized own-reference breach magnitude/order and residual price innovations at causal lags.

**Local comparison.** Compare exact price SMT, ratios/VAR and sparse conditional lag features after realistic timing.

**Additional cases.** Common factor explains move; stale source; reverse breach order; missing reference.

<a id="up-x08"></a>
### UP-X08 — ETF and constituent-event context

Parent: [X08](components/CROSS_ASSET.md); [local phases](experiments/X.md#x08); [definition refinement](SYSTEM_REFINEMENT.md#sr-x08). Upgrade role: `forecast`.

**Starting idea.** Use ETF direction or large off-exchange prints as broad sentiment.

**Existing improvement path.** ETF proxies, known constituent events, unsigned TRF receipt-time features and separate true-breadth dependency.

**Remaining weakness.** Aggregate ETF and print totals hide event concentration, activity surprise and reporting delays, while proxies can be mistaken for actual constituent breadth.

**Further upgrade.** Build residual ETF/print-event features conditional on market movement, expected receipt intensity and report lag, with price-reference controls. Where true PIT constituents/weights become eligible, decompose index movement into concentration/breadth and constituent-event contributions and compare its increment to existing proxies; no unsigned print becomes invented CVD.

**Fair comparison.** Futures-only, ETF proxy, TRF intensity/reference controls, residual event features and separately eligible true constituent decomposition.

**Evidence.** Event/report fidelity, incremental path/tail loss, placebo-adjusted print value, net and distinct data contribution.

**Additional local cases to implement.** Large late TRF print; cancelled print; one constituent drives ETF; current weights leak; known earnings with absent constituent tape.

**Decision or system use.** Use supported ETF and reported-event information more precisely while defining the additional value true constituent data must prove.

**Exact reviewed source clauses.** [DTM-A09](SOURCE_FINDINGS_AND_CONFLICTS.md:67), [CEX-25](SOURCE_FINDINGS_AND_CONFLICTS.md:207), [CRL-10](SOURCE_FINDINGS_AND_CONFLICTS.md:226), [DEN-04](SOURCE_FINDINGS_AND_CONFLICTS.md:412).

**Conversation upgrade lineage.** [DTM-A09](SOURCE_FINDINGS_AND_CONFLICTS.md:67), [CRL-10](SOURCE_FINDINGS_AND_CONFLICTS.md:226). Read the full rows and their original conversation references; [the recheck](CONVERSATION_RECHECK.md) preserves the exact unit/exception routes.

<a id="up-x08-constituents"></a>
#### X08.CONSTITUENTS — Constituent breadth and event concentration

[Existing definition, target and P0–P7](experiments/X.md#x08-constituents) remain binding.

**Specific upgrade scope.** Keep ETF/event proxies separate from PIT true breadth and contribution decomposition, adding each when its data becomes eligible.

**Local comparison.** Compare concentration/breadth/event residuals against futures/ETF baselines at supported clocks and effective dates.

**Additional cases.** Current weights leak; one constituent dominates; missing constituent tape; delayed daily index.

<a id="up-x08-trf"></a>
#### X08.TRF — Reported off-exchange equity prints

[Existing definition, target and P0–P7](experiments/X.md#x08-trf) remain binding.

**Specific upgrade scope.** Use unsigned receipt-time intensity/notional surprise, report lag and causal price-reference controls.

**Local comparison.** Compare no-print, simple intensity and residual event models; do not derive signed CVD, hidden venue or parent identity.

**Additional cases.** Late/cancelled report; price outlier; full-day top list; repeated size; no paired quote.

<a id="up-x09"></a>
### UP-X09 — Global futures, currency and commodity transmission

Parent: [X09](components/CROSS_ASSET.md); [local phases](experiments/X.md#x09); [definition refinement](SYSTEM_REFINEMENT.md#sr-x09). Upgrade role: `forecast`.

**Starting idea.** Compress global markets into a risk-on/off score.

**Existing improvement path.** Independent NKD/FX, HG/FX, SI, YM/RTY, rates and GC/USD children with correct clocks and units.

**Remaining weakness.** Raw cross-market returns mix currency, local-session effects and common events, and one pooled model can conceal weak individual sources.

**Further upgrade.** For every child, separate local-asset, currency/basis, session and common-event components, then estimate shrinkage causal lag/response features at supported horizons. Compare per-source residual experts and sparse joint fusion; preserve each commodity/index/rates branch and do not turn slow inputs into subsecond evidence.

**Fair comparison.** Receiver-only, every single-source lag model, decomposed residual children and bounded multivariate fusion.

**Evidence.** Child-specific path/tail loss, timing stability, unique/joint net contribution, effective dates and data/compute cost.

**Additional local cases to implement.** NKD move explained by FX; commodity holiday; daily rates observation copied intraday; shared announcement; one source unavailable.

**Decision or system use.** Identify which global relationships add distinct usable information, at the time scale the observations can support.

**Exact reviewed source clauses.** [JXA-21](SOURCE_FINDINGS_AND_CONFLICTS.md:120), [JXA-22](SOURCE_FINDINGS_AND_CONFLICTS.md:121), [CEX-12](SOURCE_FINDINGS_AND_CONFLICTS.md:194), [CEX-25](SOURCE_FINDINGS_AND_CONFLICTS.md:207), [PIN022-03](SOURCE_FINDINGS_AND_CONFLICTS.md:896).

**Conversation upgrade lineage.** [CEX-12](SOURCE_FINDINGS_AND_CONFLICTS.md:194), [CEX-25](SOURCE_FINDINGS_AND_CONFLICTS.md:207), [CRL-10](SOURCE_FINDINGS_AND_CONFLICTS.md:226). Read the full rows and their original conversation references; [the recheck](CONVERSATION_RECHECK.md) preserves the exact unit/exception routes.

<a id="up-x09-gc_usd"></a>
#### X09.GC_USD — Gold and dollar slow context

[Existing definition, target and P0–P7](experiments/X.md#x09-gc_usd) remain binding.

**Specific upgrade scope.** Separate gold and dollar components, publication/session state and conditional slow transmission.

**Local comparison.** Compare each source, simple joint residual context and receiver baseline at defensible horizons.

**Additional cases.** Dollar proxy mismatch; roll; common event; slow input cannot establish subsecond lead.

<a id="up-x09-hg_fx"></a>
#### X09.HG_FX — Copper and currency context

[Existing definition, target and P0–P7](experiments/X.md#x09-hg_fx) remain binding.

**Specific upgrade scope.** Decompose copper price/activity from currency/common-event state and test conditional receiver-tail/return information.

**Local comparison.** Compare each source, simple joint lag and sparse residual interaction with exact observation clocks.

**Additional cases.** Commodity-specific shock; FX collinearity; contract roll; unavailable intraday interval.

<a id="up-x09-nkd_fx"></a>
#### X09.NKD_FX — Japan equity and FX transmission

[Existing definition, target and P0–P7](experiments/X.md#x09-nkd_fx) remain binding.

**Specific upgrade scope.** Separate Japan equity, currency and local-session components and test causal residual transmission at supported horizons.

**Local comparison.** Compare NKD only, FX only, joint decomposition and receiver baseline with shared-event controls.

**Additional cases.** FX explains local move; nonoverlapping holiday; currency units; stale session close.

<a id="up-x09-rates"></a>
#### X09.RATES — Rates and inflation-context inputs

[Existing definition, target and P0–P7](experiments/X.md#x09-rates) remain binding.

**Specific upgrade scope.** Use exact rates/inflation source publication clocks and separate curve/change/state components where supported.

**Local comparison.** Compare slow context and eligible intraday response separately, pooling sparse releases by real observation counts.

**Additional cases.** Daily value repeated intraday; release revision; maturity/unit difference; announcement overlap.

<a id="up-x09-si"></a>
#### X09.SI — Silver context

[Existing definition, target and P0–P7](experiments/X.md#x09-si) remain binding.

**Specific upgrade scope.** Retain silver as its own source expert with local-session/activity residuals and conditional influence duration.

**Local comparison.** Compare receiver-only, raw silver lag and state-adjusted residual features; no generic metal pooling without ablation.

**Additional cases.** Silver-specific event; holiday; low activity; shared dollar shock.

<a id="up-x09-ym_rty"></a>
#### X09.YM_RTY — Other US index-futures specialists

[Existing definition, target and P0–P7](experiments/X.md#x09-ym_rty) remain binding.

**Specific upgrade scope.** Separate broad US index common movement and YM/RTY-specific price/flow/breadth residuals.

**Local comparison.** Compare each source, joint sparse lags and NQ/ES-only baseline under matched availability.

**Additional cases.** Same common equity shock; differing tick values; reference breach order; one source gap.

<a id="up-x10"></a>
### UP-X10 — Slow positioning, inventories and fund-flow context

Parent: [X10](components/CROSS_ASSET.md); [local phases](experiments/X.md#x10); [definition refinement](SYSTEM_REFINEMENT.md#sr-x10). Upgrade role: `forecast`.

**Starting idea.** Read slow positioning, inventory or fund holdings as a current trading signal.

**Existing improvement path.** Publication-lagged levels/changes/percentiles and distinct COT/SHFE/SLV report clocks.

**Remaining weakness.** Repeated intraday copies inflate apparent sample size and a raw change ignores expectations, revisions and elapsed report relevance.

**Further upgrade.** Model report-level innovations with partial pooling, explicit vintage/revision effects and a causal distributed influence kernel over subsequent sessions. Compare level/change, expectation-adjusted residual and interaction with current market state; estimate uncertainty by independent reports and keep each source's economic meaning separate.

**Fair comparison.** No slow data, last-published level/change, pooled report innovations and supported state interactions.

**Evidence.** Report-level target loss/calibration, age relevance, incremental session/day value, revision sensitivity and effective sample size.

**Additional local cases to implement.** Positions date precedes publication; missing report; revision later; holdings change from units/price convention; sparse rare extreme.

**Decision or system use.** Use slow information as a tested state modifier with a realistic lifetime, rather than pseudo-fresh intraday observations.

**Exact reviewed source clauses.** [CRL-10](SOURCE_FINDINGS_AND_CONFLICTS.md:226), [DEN-03](SOURCE_FINDINGS_AND_CONFLICTS.md:411), [DEN-04](SOURCE_FINDINGS_AND_CONFLICTS.md:412).

<a id="up-x10-cot"></a>
#### X10.COT — CFTC positioning specialist

[Existing definition, target and P0–P7](experiments/X.md#x10-cot) remain binding.

**Specific upgrade scope.** Model report-level positioning innovations and subsequent-session influence with exact as-of/publication/vintage handling.

**Local comparison.** Compare last level/change, pooled residual report model and supported current-state interactions by independent reports.

**Additional cases.** Tuesday position published later; revision; category changes; duplicated minute rows.

<a id="up-x10-shfe"></a>
#### X10.SHFE — Inventory publication specialist

[Existing definition, target and P0–P7](experiments/X.md#x10-shfe) remain binding.

**Specific upgrade scope.** Use inventory report innovations, unit/commodity/lifecycle conventions and causal report-age effects.

**Local comparison.** Compare level/change with partially pooled unexpected changes and interaction with observed commodity/global state.

**Additional cases.** Holiday report gap; revision; unit mismatch; warehouse/category change; stale report.

<a id="up-x10-slv"></a>
#### X10.SLV — Fund-holdings context

[Existing definition, target and P0–P7](experiments/X.md#x10-slv) remain binding.

**Specific upgrade scope.** Separate fund-holdings quantity changes from price/notional effects and model publication-lagged report innovations.

**Local comparison.** Compare last reported holdings, change and supported residual context with actual report counts.

**Additional cases.** Price rise looks like inflow; revised shares; publication after market close; missing vintage.

<a id="family-l"></a>
## Locations

<a id="up-l01"></a>
### UP-L01 — Internal range quarters, EQ and range-open locations

Parent: [L01](components/LOCATION.md); [local phases](experiments/L.md#l01); [definition refinement](SYSTEM_REFINEMENT.md#sr-l01). Upgrade role: `location`.

**Starting idea.** Trade fixed quarters or EQ as generic support/resistance.

**Existing improvement path.** Exact internal coordinates with distinct internal-to-edge and internal-to-extension roles.

**Remaining weakness.** One line per fraction ignores a broad useful interior region and how role changes after a break, purge or value shift.

**Further upgrade.** Represent internal geometry as a range-relative role/value field conditioned on frozen range width and observed path. Compare exact quarter/open points with bounded bands and small train-selected offsets using shared L16 machinery; retain separate reversal, continuation and target roles with equal candidate/width budgets.

**Fair comparison.** Source quarters/EQ/open, conditional point roles, bounded field/band variants and simple dense-grid controls.

**Evidence.** Role/path calibration, width-matched location precision, selected net and candidate coverage.

**Additional local cases to implement.** Wide versus compressed range; interior useful before any edge touch; moved formation range; identical point has opposite role after reclaim.

**Decision or system use.** Improve internal opportunity placement and interpretation without imposing edge-first or permanent fade rules.

**Exact reviewed source clauses.** [JTR-01](SOURCE_FINDINGS_AND_CONFLICTS.md:18), [JTR-02](SOURCE_FINDINGS_AND_CONFLICTS.md:19), [JTR-03](SOURCE_FINDINGS_AND_CONFLICTS.md:20), [JTR-04](SOURCE_FINDINGS_AND_CONFLICTS.md:21), [JTR-05](SOURCE_FINDINGS_AND_CONFLICTS.md:22), [JTR-06](SOURCE_FINDINGS_AND_CONFLICTS.md:23), [JTR-07](SOURCE_FINDINGS_AND_CONFLICTS.md:24), [JTR-08](SOURCE_FINDINGS_AND_CONFLICTS.md:25), [JTR-09](SOURCE_FINDINGS_AND_CONFLICTS.md:26), [JTR-10](SOURCE_FINDINGS_AND_CONFLICTS.md:27), [JTR-11](SOURCE_FINDINGS_AND_CONFLICTS.md:28), [JTR-12](SOURCE_FINDINGS_AND_CONFLICTS.md:29), [JTR-13](SOURCE_FINDINGS_AND_CONFLICTS.md:30), [JTR-14](SOURCE_FINDINGS_AND_CONFLICTS.md:31), [JTR-15](SOURCE_FINDINGS_AND_CONFLICTS.md:32), [JTR-16](SOURCE_FINDINGS_AND_CONFLICTS.md:33), [JTR-17](SOURCE_FINDINGS_AND_CONFLICTS.md:34), [JTR-18](SOURCE_FINDINGS_AND_CONFLICTS.md:35), [JTR-19](SOURCE_FINDINGS_AND_CONFLICTS.md:36), [JTR-20](SOURCE_FINDINGS_AND_CONFLICTS.md:37), [JTR-21](SOURCE_FINDINGS_AND_CONFLICTS.md:38), [JTR-22](SOURCE_FINDINGS_AND_CONFLICTS.md:39), [JTR-23](SOURCE_FINDINGS_AND_CONFLICTS.md:40), [JTR-24](SOURCE_FINDINGS_AND_CONFLICTS.md:41), [DTM-A02](SOURCE_FINDINGS_AND_CONFLICTS.md:60), [JXA-01](SOURCE_FINDINGS_AND_CONFLICTS.md:100), [JXA-02](SOURCE_FINDINGS_AND_CONFLICTS.md:101), [JXA-03](SOURCE_FINDINGS_AND_CONFLICTS.md:102), [JXA-04](SOURCE_FINDINGS_AND_CONFLICTS.md:103), [JXA-05](SOURCE_FINDINGS_AND_CONFLICTS.md:104), [JXA-06](SOURCE_FINDINGS_AND_CONFLICTS.md:105), [JXA-07](SOURCE_FINDINGS_AND_CONFLICTS.md:106), [JXA-08](SOURCE_FINDINGS_AND_CONFLICTS.md:107), [JXA-09](SOURCE_FINDINGS_AND_CONFLICTS.md:108), [JXA-10](SOURCE_FINDINGS_AND_CONFLICTS.md:109), [JXA-11](SOURCE_FINDINGS_AND_CONFLICTS.md:110), [JXA-12](SOURCE_FINDINGS_AND_CONFLICTS.md:111), [JXA-13](SOURCE_FINDINGS_AND_CONFLICTS.md:112), [JXA-14](SOURCE_FINDINGS_AND_CONFLICTS.md:113), [JXA-15](SOURCE_FINDINGS_AND_CONFLICTS.md:114), [JXA-16](SOURCE_FINDINGS_AND_CONFLICTS.md:115), [JXA-17](SOURCE_FINDINGS_AND_CONFLICTS.md:116), [JXA-18](SOURCE_FINDINGS_AND_CONFLICTS.md:117), [JXA-19](SOURCE_FINDINGS_AND_CONFLICTS.md:118), [JXA-20](SOURCE_FINDINGS_AND_CONFLICTS.md:119), [JXA-21](SOURCE_FINDINGS_AND_CONFLICTS.md:120), [JXA-22](SOURCE_FINDINGS_AND_CONFLICTS.md:121), [JXA-23](SOURCE_FINDINGS_AND_CONFLICTS.md:122), [JXA-24](SOURCE_FINDINGS_AND_CONFLICTS.md:123), [JXA-25](SOURCE_FINDINGS_AND_CONFLICTS.md:124), [JXA-26](SOURCE_FINDINGS_AND_CONFLICTS.md:125), [JFN-01](SOURCE_FINDINGS_AND_CONFLICTS.md:135), [JFN-02](SOURCE_FINDINGS_AND_CONFLICTS.md:136), [JFN-03](SOURCE_FINDINGS_AND_CONFLICTS.md:137), [JFN-04](SOURCE_FINDINGS_AND_CONFLICTS.md:138), [JFN-05](SOURCE_FINDINGS_AND_CONFLICTS.md:139), [JFN-06](SOURCE_FINDINGS_AND_CONFLICTS.md:140), [JFN-07](SOURCE_FINDINGS_AND_CONFLICTS.md:141), [JFN-08](SOURCE_FINDINGS_AND_CONFLICTS.md:142), [JFN-09](SOURCE_FINDINGS_AND_CONFLICTS.md:143), [JFN-10](SOURCE_FINDINGS_AND_CONFLICTS.md:144), [JFN-11](SOURCE_FINDINGS_AND_CONFLICTS.md:145), [JFN-12](SOURCE_FINDINGS_AND_CONFLICTS.md:146), [CRL-05](SOURCE_FINDINGS_AND_CONFLICTS.md:221), [DRF-U07](SOURCE_FINDINGS_AND_CONFLICTS.md:431), [DRF-A20](SOURCE_FINDINGS_AND_CONFLICTS.md:461), [MAV-09](SOURCE_FINDINGS_AND_CONFLICTS.md:513), [PIN001-01](SOURCE_FINDINGS_AND_CONFLICTS.md:812), [PIN001-02](SOURCE_FINDINGS_AND_CONFLICTS.md:813), [PIN001-03](SOURCE_FINDINGS_AND_CONFLICTS.md:814), [PIN001-04](SOURCE_FINDINGS_AND_CONFLICTS.md:815), [PIN002-01](SOURCE_FINDINGS_AND_CONFLICTS.md:816), [PIN002-02](SOURCE_FINDINGS_AND_CONFLICTS.md:817), [PIN002-03](SOURCE_FINDINGS_AND_CONFLICTS.md:818), [PIN003-01](SOURCE_FINDINGS_AND_CONFLICTS.md:819), [PIN003-02](SOURCE_FINDINGS_AND_CONFLICTS.md:820), [PIN003-03](SOURCE_FINDINGS_AND_CONFLICTS.md:821), [PIN003-04](SOURCE_FINDINGS_AND_CONFLICTS.md:822), [PIN004-01](SOURCE_FINDINGS_AND_CONFLICTS.md:823), [PIN006-01](SOURCE_FINDINGS_AND_CONFLICTS.md:833), [PIN006-02](SOURCE_FINDINGS_AND_CONFLICTS.md:834), [PIN006-03](SOURCE_FINDINGS_AND_CONFLICTS.md:835), [PIN007-01](SOURCE_FINDINGS_AND_CONFLICTS.md:836), [PIN007-02](SOURCE_FINDINGS_AND_CONFLICTS.md:837), [PIN007-03](SOURCE_FINDINGS_AND_CONFLICTS.md:838), [PIN007-04](SOURCE_FINDINGS_AND_CONFLICTS.md:839), [PIN007-05](SOURCE_FINDINGS_AND_CONFLICTS.md:840), [PIN012-01](SOURCE_FINDINGS_AND_CONFLICTS.md:852), [PIN012-02](SOURCE_FINDINGS_AND_CONFLICTS.md:853), [PIN012-03](SOURCE_FINDINGS_AND_CONFLICTS.md:854), [PIN012-04](SOURCE_FINDINGS_AND_CONFLICTS.md:855), [PIN012-05](SOURCE_FINDINGS_AND_CONFLICTS.md:856), [PIN013-01](SOURCE_FINDINGS_AND_CONFLICTS.md:857), [PIN013-02](SOURCE_FINDINGS_AND_CONFLICTS.md:858), [PIN013-03](SOURCE_FINDINGS_AND_CONFLICTS.md:859), [PIN013-04](SOURCE_FINDINGS_AND_CONFLICTS.md:860), [PIN013-05](SOURCE_FINDINGS_AND_CONFLICTS.md:861), [PIN013-06](SOURCE_FINDINGS_AND_CONFLICTS.md:862), [PIN014-01](SOURCE_FINDINGS_AND_CONFLICTS.md:863), [PIN014-02](SOURCE_FINDINGS_AND_CONFLICTS.md:864), [PIN015-01](SOURCE_FINDINGS_AND_CONFLICTS.md:865), [PIN015-02](SOURCE_FINDINGS_AND_CONFLICTS.md:866), [PIN015-03](SOURCE_FINDINGS_AND_CONFLICTS.md:867), [PIN016-01](SOURCE_FINDINGS_AND_CONFLICTS.md:868), [PIN016-02](SOURCE_FINDINGS_AND_CONFLICTS.md:869), [PIN016-03](SOURCE_FINDINGS_AND_CONFLICTS.md:870), [PIN016-04](SOURCE_FINDINGS_AND_CONFLICTS.md:871), [PIN024-01](SOURCE_FINDINGS_AND_CONFLICTS.md:878), [PIN024-02](SOURCE_FINDINGS_AND_CONFLICTS.md:879), [PIN021-01](SOURCE_FINDINGS_AND_CONFLICTS.md:892), [PIN021-02](SOURCE_FINDINGS_AND_CONFLICTS.md:893), [PIN025-01](SOURCE_FINDINGS_AND_CONFLICTS.md:899), [PIN026-01](SOURCE_FINDINGS_AND_CONFLICTS.md:900), [PIN026-02](SOURCE_FINDINGS_AND_CONFLICTS.md:901), [PIN027-01](SOURCE_FINDINGS_AND_CONFLICTS.md:902), [PIN027-02](SOURCE_FINDINGS_AND_CONFLICTS.md:903), [PIN028-01](SOURCE_FINDINGS_AND_CONFLICTS.md:904), [PIN028-02](SOURCE_FINDINGS_AND_CONFLICTS.md:905), [PIN028-03](SOURCE_FINDINGS_AND_CONFLICTS.md:906), [PIN029-01](SOURCE_FINDINGS_AND_CONFLICTS.md:907), [PIN029-02](SOURCE_FINDINGS_AND_CONFLICTS.md:908), [PIN029-03](SOURCE_FINDINGS_AND_CONFLICTS.md:909), [PIN030-01](SOURCE_FINDINGS_AND_CONFLICTS.md:910), [PIN030-02](SOURCE_FINDINGS_AND_CONFLICTS.md:911), [PIN030-03](SOURCE_FINDINGS_AND_CONFLICTS.md:912), [PIN031-01](SOURCE_FINDINGS_AND_CONFLICTS.md:913), [PIN036-01](SOURCE_FINDINGS_AND_CONFLICTS.md:925), [PIN036-02](SOURCE_FINDINGS_AND_CONFLICTS.md:926), [PIN037-01](SOURCE_FINDINGS_AND_CONFLICTS.md:927), [PIN037-02](SOURCE_FINDINGS_AND_CONFLICTS.md:928), [PIN039-01](SOURCE_FINDINGS_AND_CONFLICTS.md:933), [PIN039-02](SOURCE_FINDINGS_AND_CONFLICTS.md:934), [PIN040-01](SOURCE_FINDINGS_AND_CONFLICTS.md:935), [PIN040-02](SOURCE_FINDINGS_AND_CONFLICTS.md:936), [PIN041-01](SOURCE_FINDINGS_AND_CONFLICTS.md:938), [PIN041-02](SOURCE_FINDINGS_AND_CONFLICTS.md:939), [PIN041-03](SOURCE_FINDINGS_AND_CONFLICTS.md:940), [PIN042-01](SOURCE_FINDINGS_AND_CONFLICTS.md:942), [PIN042-02](SOURCE_FINDINGS_AND_CONFLICTS.md:943), [PIN043-01](SOURCE_FINDINGS_AND_CONFLICTS.md:944), [PIN044-01](SOURCE_FINDINGS_AND_CONFLICTS.md:945), [PIN044-02](SOURCE_FINDINGS_AND_CONFLICTS.md:946), [PIN045-01](SOURCE_FINDINGS_AND_CONFLICTS.md:948), [PIN045-02](SOURCE_FINDINGS_AND_CONFLICTS.md:949), [PIN045-03](SOURCE_FINDINGS_AND_CONFLICTS.md:950), [PIN045-04](SOURCE_FINDINGS_AND_CONFLICTS.md:951), [PIN045-05](SOURCE_FINDINGS_AND_CONFLICTS.md:952), [PIN045-06](SOURCE_FINDINGS_AND_CONFLICTS.md:953), [PIN046-01](SOURCE_FINDINGS_AND_CONFLICTS.md:955), [PIN047-01](SOURCE_FINDINGS_AND_CONFLICTS.md:956), [PIN047-02](SOURCE_FINDINGS_AND_CONFLICTS.md:957), [PIN047-03](SOURCE_FINDINGS_AND_CONFLICTS.md:958), [PIN048-01](SOURCE_FINDINGS_AND_CONFLICTS.md:960), [PIN048-02](SOURCE_FINDINGS_AND_CONFLICTS.md:961), [PIN048-03](SOURCE_FINDINGS_AND_CONFLICTS.md:962), [PIN049-01](SOURCE_FINDINGS_AND_CONFLICTS.md:964), [PIN049-02](SOURCE_FINDINGS_AND_CONFLICTS.md:965), [PIN049-03](SOURCE_FINDINGS_AND_CONFLICTS.md:966), [PIN052-01](SOURCE_FINDINGS_AND_CONFLICTS.md:974), [PIN052-02](SOURCE_FINDINGS_AND_CONFLICTS.md:975), [PIN052-03](SOURCE_FINDINGS_AND_CONFLICTS.md:976), [PIN054-01](SOURCE_FINDINGS_AND_CONFLICTS.md:978), [PIN054-02](SOURCE_FINDINGS_AND_CONFLICTS.md:979), [PIN055-01](SOURCE_FINDINGS_AND_CONFLICTS.md:980), [PIN055-02](SOURCE_FINDINGS_AND_CONFLICTS.md:981), [PIN056-01](SOURCE_FINDINGS_AND_CONFLICTS.md:983), [PIN056-02](SOURCE_FINDINGS_AND_CONFLICTS.md:984), [PIN057-01](SOURCE_FINDINGS_AND_CONFLICTS.md:985), [PIN057-02](SOURCE_FINDINGS_AND_CONFLICTS.md:986), [PIN057-03](SOURCE_FINDINGS_AND_CONFLICTS.md:987), [PIN058-01](SOURCE_FINDINGS_AND_CONFLICTS.md:989), [PIN059-01](SOURCE_FINDINGS_AND_CONFLICTS.md:990), [PIN059-02](SOURCE_FINDINGS_AND_CONFLICTS.md:991), [PIN060-01](SOURCE_FINDINGS_AND_CONFLICTS.md:993), [PIN060-02](SOURCE_FINDINGS_AND_CONFLICTS.md:994), [PIN060-03](SOURCE_FINDINGS_AND_CONFLICTS.md:995), [PIN061-01](SOURCE_FINDINGS_AND_CONFLICTS.md:997), [PIN061-02](SOURCE_FINDINGS_AND_CONFLICTS.md:998), [PIN061-03](SOURCE_FINDINGS_AND_CONFLICTS.md:999), [PIN062-01](SOURCE_FINDINGS_AND_CONFLICTS.md:1001), [PIN062-02](SOURCE_FINDINGS_AND_CONFLICTS.md:1002), [PIN062-03](SOURCE_FINDINGS_AND_CONFLICTS.md:1003), [PIN063-01](SOURCE_FINDINGS_AND_CONFLICTS.md:1005), [PIN063-02](SOURCE_FINDINGS_AND_CONFLICTS.md:1006), [PIN063-03](SOURCE_FINDINGS_AND_CONFLICTS.md:1007), [PIN064-01](SOURCE_FINDINGS_AND_CONFLICTS.md:1009), [PIN064-02](SOURCE_FINDINGS_AND_CONFLICTS.md:1010), [PIN065-01](SOURCE_FINDINGS_AND_CONFLICTS.md:1012), [PIN065-02](SOURCE_FINDINGS_AND_CONFLICTS.md:1013), [PIN065-03](SOURCE_FINDINGS_AND_CONFLICTS.md:1014), [PIN067-01](SOURCE_FINDINGS_AND_CONFLICTS.md:1021), [PIN067-02](SOURCE_FINDINGS_AND_CONFLICTS.md:1022), [PIN068-01](SOURCE_FINDINGS_AND_CONFLICTS.md:1024), [PIN068-02](SOURCE_FINDINGS_AND_CONFLICTS.md:1025), [PIN068-03](SOURCE_FINDINGS_AND_CONFLICTS.md:1026), [PIN070-01](SOURCE_FINDINGS_AND_CONFLICTS.md:1033), [PIN070-02](SOURCE_FINDINGS_AND_CONFLICTS.md:1034), [PIN073-01](SOURCE_FINDINGS_AND_CONFLICTS.md:1048), [PIN073-02](SOURCE_FINDINGS_AND_CONFLICTS.md:1049), [PIN074-01](SOURCE_FINDINGS_AND_CONFLICTS.md:1051), [PIN074-02](SOURCE_FINDINGS_AND_CONFLICTS.md:1052), [PIN075-01](SOURCE_FINDINGS_AND_CONFLICTS.md:1054), [PIN075-02](SOURCE_FINDINGS_AND_CONFLICTS.md:1055), [PIN076-01](SOURCE_FINDINGS_AND_CONFLICTS.md:1057), [PIN076-02](SOURCE_FINDINGS_AND_CONFLICTS.md:1058), [PIN078-01](SOURCE_FINDINGS_AND_CONFLICTS.md:1063), [PIN078-02](SOURCE_FINDINGS_AND_CONFLICTS.md:1064), [PIN080-01](SOURCE_FINDINGS_AND_CONFLICTS.md:1071), [PIN080-02](SOURCE_FINDINGS_AND_CONFLICTS.md:1072), [PIN080-03](SOURCE_FINDINGS_AND_CONFLICTS.md:1073), [PIN081-01](SOURCE_FINDINGS_AND_CONFLICTS.md:1075), [PIN081-02](SOURCE_FINDINGS_AND_CONFLICTS.md:1076), [PIN081-03](SOURCE_FINDINGS_AND_CONFLICTS.md:1077), [PIN081-04](SOURCE_FINDINGS_AND_CONFLICTS.md:1078), [PIN082-01](SOURCE_FINDINGS_AND_CONFLICTS.md:1080), [PIN082-02](SOURCE_FINDINGS_AND_CONFLICTS.md:1081), [PIN082-03](SOURCE_FINDINGS_AND_CONFLICTS.md:1082), [PIN083-01](SOURCE_FINDINGS_AND_CONFLICTS.md:1084), [PIN083-02](SOURCE_FINDINGS_AND_CONFLICTS.md:1085).

**Conversation upgrade lineage.** [DTM-A02](SOURCE_FINDINGS_AND_CONFLICTS.md:60), [CRL-05](SOURCE_FINDINGS_AND_CONFLICTS.md:221), [DRF-U07](SOURCE_FINDINGS_AND_CONFLICTS.md:431), [DRF-A19](SOURCE_FINDINGS_AND_CONFLICTS.md:460). Read the full rows and their original conversation references; [the recheck](CONVERSATION_RECHECK.md) preserves the exact unit/exception routes.

<a id="up-l01-internal_roles"></a>
#### L01.INTERNAL_ROLES — Internal range locations

[Existing definition, target and P0–P7](experiments/L.md#l01-internal_roles) remain binding.

**Specific upgrade scope.** Compare exact internal quarter/EQ/open points with bounded range-relative role/value fields and limited offsets.

**Local comparison.** Preserve internal-to-edge and internal-to-extension branches; equalize candidate count, width and information delay.

**Additional cases.** No edge touch; compressed/purged interior; wide range; role changes after reclaim.

<a id="up-l02"></a>
### UP-L02 — Range edges and edge-relative extensions

Parent: [L02](components/LOCATION.md); [local phases](experiments/L.md#l02); [definition refinement](SYSTEM_REFINEMENT.md#sr-l02). Upgrade role: `location`.

**Starting idea.** Project fixed multiples beyond a range edge.

**Existing improvement path.** Every source extension coordinate and conditional retrace/continuation/reversal role.

**Remaining weakness.** A disconnected list of multiples loses ordered travel, spacing and uncertainty about where overshoot may resolve.

**Further upgrade.** Create an ordered extension ladder with frozen coordinate semantics, conditional overshoot density, reach/order state and role transitions. Compare exact source ratios with C06-derived quantile bands and bounded refinements at matched candidate counts; do not infer order from marginal extrema alone.

**Fair comparison.** Source ratio ladder, nearest extension, conditional quantiles and role-aware ordered ladder.

**Evidence.** Reach/role/time proper loss, width/count-matched net, sensitivity to scale and remaining horizon.

**Additional local cases to implement.** Gap skips a band; 1.33 internal coordinate differs from edge+1.33W; partial retrace then extension; repeated break.

**Decision or system use.** Choose meaningful destinations or reversal/continuation regions along the possible extension path.

**Exact reviewed source clauses.** [JTR-01](SOURCE_FINDINGS_AND_CONFLICTS.md:18), [JTR-02](SOURCE_FINDINGS_AND_CONFLICTS.md:19), [JTR-03](SOURCE_FINDINGS_AND_CONFLICTS.md:20), [JTR-04](SOURCE_FINDINGS_AND_CONFLICTS.md:21), [JTR-05](SOURCE_FINDINGS_AND_CONFLICTS.md:22), [JTR-06](SOURCE_FINDINGS_AND_CONFLICTS.md:23), [JTR-07](SOURCE_FINDINGS_AND_CONFLICTS.md:24), [JTR-08](SOURCE_FINDINGS_AND_CONFLICTS.md:25), [JTR-09](SOURCE_FINDINGS_AND_CONFLICTS.md:26), [JTR-10](SOURCE_FINDINGS_AND_CONFLICTS.md:27), [JTR-11](SOURCE_FINDINGS_AND_CONFLICTS.md:28), [JTR-12](SOURCE_FINDINGS_AND_CONFLICTS.md:29), [JTR-13](SOURCE_FINDINGS_AND_CONFLICTS.md:30), [JTR-14](SOURCE_FINDINGS_AND_CONFLICTS.md:31), [JTR-15](SOURCE_FINDINGS_AND_CONFLICTS.md:32), [JTR-16](SOURCE_FINDINGS_AND_CONFLICTS.md:33), [JTR-17](SOURCE_FINDINGS_AND_CONFLICTS.md:34), [JTR-18](SOURCE_FINDINGS_AND_CONFLICTS.md:35), [JTR-19](SOURCE_FINDINGS_AND_CONFLICTS.md:36), [JTR-20](SOURCE_FINDINGS_AND_CONFLICTS.md:37), [JTR-21](SOURCE_FINDINGS_AND_CONFLICTS.md:38), [JTR-22](SOURCE_FINDINGS_AND_CONFLICTS.md:39), [JTR-23](SOURCE_FINDINGS_AND_CONFLICTS.md:40), [JTR-24](SOURCE_FINDINGS_AND_CONFLICTS.md:41), [DTM-A02](SOURCE_FINDINGS_AND_CONFLICTS.md:60), [JXA-01](SOURCE_FINDINGS_AND_CONFLICTS.md:100), [JXA-02](SOURCE_FINDINGS_AND_CONFLICTS.md:101), [JXA-03](SOURCE_FINDINGS_AND_CONFLICTS.md:102), [JXA-04](SOURCE_FINDINGS_AND_CONFLICTS.md:103), [JXA-05](SOURCE_FINDINGS_AND_CONFLICTS.md:104), [JXA-06](SOURCE_FINDINGS_AND_CONFLICTS.md:105), [JXA-07](SOURCE_FINDINGS_AND_CONFLICTS.md:106), [JXA-08](SOURCE_FINDINGS_AND_CONFLICTS.md:107), [JXA-09](SOURCE_FINDINGS_AND_CONFLICTS.md:108), [JXA-10](SOURCE_FINDINGS_AND_CONFLICTS.md:109), [JXA-11](SOURCE_FINDINGS_AND_CONFLICTS.md:110), [JXA-12](SOURCE_FINDINGS_AND_CONFLICTS.md:111), [JXA-13](SOURCE_FINDINGS_AND_CONFLICTS.md:112), [JXA-14](SOURCE_FINDINGS_AND_CONFLICTS.md:113), [JXA-15](SOURCE_FINDINGS_AND_CONFLICTS.md:114), [JXA-16](SOURCE_FINDINGS_AND_CONFLICTS.md:115), [JXA-17](SOURCE_FINDINGS_AND_CONFLICTS.md:116), [JXA-18](SOURCE_FINDINGS_AND_CONFLICTS.md:117), [JXA-19](SOURCE_FINDINGS_AND_CONFLICTS.md:118), [JXA-20](SOURCE_FINDINGS_AND_CONFLICTS.md:119), [JXA-21](SOURCE_FINDINGS_AND_CONFLICTS.md:120), [JXA-22](SOURCE_FINDINGS_AND_CONFLICTS.md:121), [JXA-23](SOURCE_FINDINGS_AND_CONFLICTS.md:122), [JXA-24](SOURCE_FINDINGS_AND_CONFLICTS.md:123), [JXA-25](SOURCE_FINDINGS_AND_CONFLICTS.md:124), [JXA-26](SOURCE_FINDINGS_AND_CONFLICTS.md:125), [JFN-01](SOURCE_FINDINGS_AND_CONFLICTS.md:135), [JFN-02](SOURCE_FINDINGS_AND_CONFLICTS.md:136), [JFN-03](SOURCE_FINDINGS_AND_CONFLICTS.md:137), [JFN-04](SOURCE_FINDINGS_AND_CONFLICTS.md:138), [JFN-05](SOURCE_FINDINGS_AND_CONFLICTS.md:139), [JFN-06](SOURCE_FINDINGS_AND_CONFLICTS.md:140), [JFN-07](SOURCE_FINDINGS_AND_CONFLICTS.md:141), [JFN-08](SOURCE_FINDINGS_AND_CONFLICTS.md:142), [JFN-09](SOURCE_FINDINGS_AND_CONFLICTS.md:143), [JFN-10](SOURCE_FINDINGS_AND_CONFLICTS.md:144), [JFN-11](SOURCE_FINDINGS_AND_CONFLICTS.md:145), [JFN-12](SOURCE_FINDINGS_AND_CONFLICTS.md:146), [PIN001-01](SOURCE_FINDINGS_AND_CONFLICTS.md:812), [PIN001-02](SOURCE_FINDINGS_AND_CONFLICTS.md:813), [PIN001-03](SOURCE_FINDINGS_AND_CONFLICTS.md:814), [PIN001-04](SOURCE_FINDINGS_AND_CONFLICTS.md:815), [PIN002-01](SOURCE_FINDINGS_AND_CONFLICTS.md:816), [PIN002-02](SOURCE_FINDINGS_AND_CONFLICTS.md:817), [PIN002-03](SOURCE_FINDINGS_AND_CONFLICTS.md:818), [PIN003-01](SOURCE_FINDINGS_AND_CONFLICTS.md:819), [PIN003-02](SOURCE_FINDINGS_AND_CONFLICTS.md:820), [PIN003-03](SOURCE_FINDINGS_AND_CONFLICTS.md:821), [PIN003-04](SOURCE_FINDINGS_AND_CONFLICTS.md:822), [PIN004-01](SOURCE_FINDINGS_AND_CONFLICTS.md:823), [PIN006-01](SOURCE_FINDINGS_AND_CONFLICTS.md:833), [PIN006-02](SOURCE_FINDINGS_AND_CONFLICTS.md:834), [PIN006-03](SOURCE_FINDINGS_AND_CONFLICTS.md:835), [PIN007-01](SOURCE_FINDINGS_AND_CONFLICTS.md:836), [PIN007-02](SOURCE_FINDINGS_AND_CONFLICTS.md:837), [PIN007-03](SOURCE_FINDINGS_AND_CONFLICTS.md:838), [PIN007-04](SOURCE_FINDINGS_AND_CONFLICTS.md:839), [PIN007-05](SOURCE_FINDINGS_AND_CONFLICTS.md:840), [PIN012-01](SOURCE_FINDINGS_AND_CONFLICTS.md:852), [PIN012-02](SOURCE_FINDINGS_AND_CONFLICTS.md:853), [PIN012-03](SOURCE_FINDINGS_AND_CONFLICTS.md:854), [PIN012-04](SOURCE_FINDINGS_AND_CONFLICTS.md:855), [PIN012-05](SOURCE_FINDINGS_AND_CONFLICTS.md:856), [PIN013-01](SOURCE_FINDINGS_AND_CONFLICTS.md:857), [PIN013-02](SOURCE_FINDINGS_AND_CONFLICTS.md:858), [PIN013-03](SOURCE_FINDINGS_AND_CONFLICTS.md:859), [PIN013-04](SOURCE_FINDINGS_AND_CONFLICTS.md:860), [PIN013-05](SOURCE_FINDINGS_AND_CONFLICTS.md:861), [PIN013-06](SOURCE_FINDINGS_AND_CONFLICTS.md:862), [PIN014-01](SOURCE_FINDINGS_AND_CONFLICTS.md:863), [PIN014-02](SOURCE_FINDINGS_AND_CONFLICTS.md:864), [PIN015-01](SOURCE_FINDINGS_AND_CONFLICTS.md:865), [PIN015-02](SOURCE_FINDINGS_AND_CONFLICTS.md:866), [PIN015-03](SOURCE_FINDINGS_AND_CONFLICTS.md:867), [PIN016-01](SOURCE_FINDINGS_AND_CONFLICTS.md:868), [PIN016-02](SOURCE_FINDINGS_AND_CONFLICTS.md:869), [PIN016-03](SOURCE_FINDINGS_AND_CONFLICTS.md:870), [PIN016-04](SOURCE_FINDINGS_AND_CONFLICTS.md:871), [PIN024-01](SOURCE_FINDINGS_AND_CONFLICTS.md:878), [PIN024-02](SOURCE_FINDINGS_AND_CONFLICTS.md:879), [PIN021-01](SOURCE_FINDINGS_AND_CONFLICTS.md:892), [PIN021-02](SOURCE_FINDINGS_AND_CONFLICTS.md:893), [PIN025-01](SOURCE_FINDINGS_AND_CONFLICTS.md:899), [PIN026-01](SOURCE_FINDINGS_AND_CONFLICTS.md:900), [PIN026-02](SOURCE_FINDINGS_AND_CONFLICTS.md:901), [PIN027-01](SOURCE_FINDINGS_AND_CONFLICTS.md:902), [PIN027-02](SOURCE_FINDINGS_AND_CONFLICTS.md:903), [PIN028-01](SOURCE_FINDINGS_AND_CONFLICTS.md:904), [PIN028-02](SOURCE_FINDINGS_AND_CONFLICTS.md:905), [PIN028-03](SOURCE_FINDINGS_AND_CONFLICTS.md:906), [PIN029-01](SOURCE_FINDINGS_AND_CONFLICTS.md:907), [PIN029-02](SOURCE_FINDINGS_AND_CONFLICTS.md:908), [PIN029-03](SOURCE_FINDINGS_AND_CONFLICTS.md:909), [PIN030-01](SOURCE_FINDINGS_AND_CONFLICTS.md:910), [PIN030-02](SOURCE_FINDINGS_AND_CONFLICTS.md:911), [PIN030-03](SOURCE_FINDINGS_AND_CONFLICTS.md:912), [PIN031-01](SOURCE_FINDINGS_AND_CONFLICTS.md:913), [PIN036-01](SOURCE_FINDINGS_AND_CONFLICTS.md:925), [PIN036-02](SOURCE_FINDINGS_AND_CONFLICTS.md:926), [PIN037-01](SOURCE_FINDINGS_AND_CONFLICTS.md:927), [PIN037-02](SOURCE_FINDINGS_AND_CONFLICTS.md:928), [PIN039-01](SOURCE_FINDINGS_AND_CONFLICTS.md:933), [PIN039-02](SOURCE_FINDINGS_AND_CONFLICTS.md:934), [PIN040-01](SOURCE_FINDINGS_AND_CONFLICTS.md:935), [PIN040-02](SOURCE_FINDINGS_AND_CONFLICTS.md:936), [PIN041-01](SOURCE_FINDINGS_AND_CONFLICTS.md:938), [PIN041-02](SOURCE_FINDINGS_AND_CONFLICTS.md:939), [PIN041-03](SOURCE_FINDINGS_AND_CONFLICTS.md:940), [PIN042-01](SOURCE_FINDINGS_AND_CONFLICTS.md:942), [PIN042-02](SOURCE_FINDINGS_AND_CONFLICTS.md:943), [PIN043-01](SOURCE_FINDINGS_AND_CONFLICTS.md:944), [PIN044-01](SOURCE_FINDINGS_AND_CONFLICTS.md:945), [PIN044-02](SOURCE_FINDINGS_AND_CONFLICTS.md:946), [PIN045-01](SOURCE_FINDINGS_AND_CONFLICTS.md:948), [PIN045-02](SOURCE_FINDINGS_AND_CONFLICTS.md:949), [PIN045-03](SOURCE_FINDINGS_AND_CONFLICTS.md:950), [PIN045-04](SOURCE_FINDINGS_AND_CONFLICTS.md:951), [PIN045-05](SOURCE_FINDINGS_AND_CONFLICTS.md:952), [PIN045-06](SOURCE_FINDINGS_AND_CONFLICTS.md:953), [PIN046-01](SOURCE_FINDINGS_AND_CONFLICTS.md:955), [PIN047-01](SOURCE_FINDINGS_AND_CONFLICTS.md:956), [PIN047-02](SOURCE_FINDINGS_AND_CONFLICTS.md:957), [PIN047-03](SOURCE_FINDINGS_AND_CONFLICTS.md:958), [PIN048-01](SOURCE_FINDINGS_AND_CONFLICTS.md:960), [PIN048-02](SOURCE_FINDINGS_AND_CONFLICTS.md:961), [PIN048-03](SOURCE_FINDINGS_AND_CONFLICTS.md:962), [PIN049-01](SOURCE_FINDINGS_AND_CONFLICTS.md:964), [PIN049-02](SOURCE_FINDINGS_AND_CONFLICTS.md:965), [PIN049-03](SOURCE_FINDINGS_AND_CONFLICTS.md:966), [PIN052-01](SOURCE_FINDINGS_AND_CONFLICTS.md:974), [PIN052-02](SOURCE_FINDINGS_AND_CONFLICTS.md:975), [PIN052-03](SOURCE_FINDINGS_AND_CONFLICTS.md:976), [PIN054-01](SOURCE_FINDINGS_AND_CONFLICTS.md:978), [PIN054-02](SOURCE_FINDINGS_AND_CONFLICTS.md:979), [PIN055-01](SOURCE_FINDINGS_AND_CONFLICTS.md:980), [PIN055-02](SOURCE_FINDINGS_AND_CONFLICTS.md:981), [PIN056-01](SOURCE_FINDINGS_AND_CONFLICTS.md:983), [PIN056-02](SOURCE_FINDINGS_AND_CONFLICTS.md:984), [PIN057-01](SOURCE_FINDINGS_AND_CONFLICTS.md:985), [PIN057-02](SOURCE_FINDINGS_AND_CONFLICTS.md:986), [PIN057-03](SOURCE_FINDINGS_AND_CONFLICTS.md:987), [PIN058-01](SOURCE_FINDINGS_AND_CONFLICTS.md:989), [PIN059-01](SOURCE_FINDINGS_AND_CONFLICTS.md:990), [PIN059-02](SOURCE_FINDINGS_AND_CONFLICTS.md:991), [PIN060-01](SOURCE_FINDINGS_AND_CONFLICTS.md:993), [PIN060-02](SOURCE_FINDINGS_AND_CONFLICTS.md:994), [PIN060-03](SOURCE_FINDINGS_AND_CONFLICTS.md:995), [PIN061-01](SOURCE_FINDINGS_AND_CONFLICTS.md:997), [PIN061-02](SOURCE_FINDINGS_AND_CONFLICTS.md:998), [PIN061-03](SOURCE_FINDINGS_AND_CONFLICTS.md:999), [PIN062-01](SOURCE_FINDINGS_AND_CONFLICTS.md:1001), [PIN062-02](SOURCE_FINDINGS_AND_CONFLICTS.md:1002), [PIN062-03](SOURCE_FINDINGS_AND_CONFLICTS.md:1003), [PIN063-01](SOURCE_FINDINGS_AND_CONFLICTS.md:1005), [PIN063-02](SOURCE_FINDINGS_AND_CONFLICTS.md:1006), [PIN063-03](SOURCE_FINDINGS_AND_CONFLICTS.md:1007), [PIN064-01](SOURCE_FINDINGS_AND_CONFLICTS.md:1009), [PIN064-02](SOURCE_FINDINGS_AND_CONFLICTS.md:1010), [PIN065-01](SOURCE_FINDINGS_AND_CONFLICTS.md:1012), [PIN065-02](SOURCE_FINDINGS_AND_CONFLICTS.md:1013), [PIN065-03](SOURCE_FINDINGS_AND_CONFLICTS.md:1014), [PIN067-01](SOURCE_FINDINGS_AND_CONFLICTS.md:1021), [PIN067-02](SOURCE_FINDINGS_AND_CONFLICTS.md:1022), [PIN068-01](SOURCE_FINDINGS_AND_CONFLICTS.md:1024), [PIN068-02](SOURCE_FINDINGS_AND_CONFLICTS.md:1025), [PIN068-03](SOURCE_FINDINGS_AND_CONFLICTS.md:1026), [PIN070-01](SOURCE_FINDINGS_AND_CONFLICTS.md:1033), [PIN070-02](SOURCE_FINDINGS_AND_CONFLICTS.md:1034), [PIN073-01](SOURCE_FINDINGS_AND_CONFLICTS.md:1048), [PIN073-02](SOURCE_FINDINGS_AND_CONFLICTS.md:1049), [PIN074-01](SOURCE_FINDINGS_AND_CONFLICTS.md:1051), [PIN074-02](SOURCE_FINDINGS_AND_CONFLICTS.md:1052), [PIN075-01](SOURCE_FINDINGS_AND_CONFLICTS.md:1054), [PIN075-02](SOURCE_FINDINGS_AND_CONFLICTS.md:1055), [PIN076-01](SOURCE_FINDINGS_AND_CONFLICTS.md:1057), [PIN076-02](SOURCE_FINDINGS_AND_CONFLICTS.md:1058), [PIN078-01](SOURCE_FINDINGS_AND_CONFLICTS.md:1063), [PIN078-02](SOURCE_FINDINGS_AND_CONFLICTS.md:1064), [PIN080-01](SOURCE_FINDINGS_AND_CONFLICTS.md:1071), [PIN080-02](SOURCE_FINDINGS_AND_CONFLICTS.md:1072), [PIN080-03](SOURCE_FINDINGS_AND_CONFLICTS.md:1073), [PIN081-01](SOURCE_FINDINGS_AND_CONFLICTS.md:1075), [PIN081-02](SOURCE_FINDINGS_AND_CONFLICTS.md:1076), [PIN081-03](SOURCE_FINDINGS_AND_CONFLICTS.md:1077), [PIN081-04](SOURCE_FINDINGS_AND_CONFLICTS.md:1078), [PIN082-01](SOURCE_FINDINGS_AND_CONFLICTS.md:1080), [PIN082-02](SOURCE_FINDINGS_AND_CONFLICTS.md:1081), [PIN082-03](SOURCE_FINDINGS_AND_CONFLICTS.md:1082), [PIN083-01](SOURCE_FINDINGS_AND_CONFLICTS.md:1084), [PIN083-02](SOURCE_FINDINGS_AND_CONFLICTS.md:1085).

<a id="up-l02-projection_roles"></a>
#### L02.PROJECTION_ROLES — Extension and retracement branches

[Existing definition, target and P0–P7](experiments/L.md#l02-projection_roles) remain binding.

**Specific upgrade scope.** Use an ordered extension ladder with conditional overshoot support, time and role transitions.

**Local comparison.** Compare all exact source ratios and learned quantile bands with equal count/width; source coordinate semantics stay explicit.

**Additional cases.** 1.33 coordinate versus edge extension; gap-over; partial retrace then continuation; deeper level not reached.

<a id="up-l03"></a>
### UP-L03 — Previous-RTH and full-session structure

Parent: [L03](components/LOCATION.md); [local phases](experiments/L.md#l03); [definition refinement](SYSTEM_REFINEMENT.md#sr-l03). Upgrade role: `location`.

**Starting idea.** Keep yesterday's RTH highs/lows until swept.

**Existing improvement path.** Faithful RTH-only freshness and full-session touch-aware alternatives with exact anchors.

**Remaining weakness.** Binary fresh/swept state discards pressure, depth of excursion, reclaims and overnight information.

**Further upgrade.** Maintain a source-clock memory vector for each prior-session reference: touch dose, excursion/reclaim, time away, accepted volume/time and current-session relation. Compare graded survival/role effects with delete-on-touch and the faithful ETH-ignoring rule; preserve inner 06–09 and outer RTH identities.

**Fair comparison.** RTH-only source, ETH touch flag, graded session memory and conditional role model.

**Evidence.** Anchor fidelity, useful-lifetime calibration, session-transfer performance and net location increment.

**Additional local cases to implement.** ETH wick only; sustained overnight acceptance; prior RTH level reclaimed; missing overnight data; half-day anchor.

**Decision or system use.** Use overnight and session-transition evidence as tested information while retaining the original source comparator.

**Exact reviewed source clauses.** [JTR-06](SOURCE_FINDINGS_AND_CONFLICTS.md:23), [JTR-21](SOURCE_FINDINGS_AND_CONFLICTS.md:38), [JTR-22](SOURCE_FINDINGS_AND_CONFLICTS.md:39), [DTM-A04](SOURCE_FINDINGS_AND_CONFLICTS.md:62), [DTM-A11](SOURCE_FINDINGS_AND_CONFLICTS.md:69), [JXA-03](SOURCE_FINDINGS_AND_CONFLICTS.md:102), [JXA-09](SOURCE_FINDINGS_AND_CONFLICTS.md:108), [JXA-10](SOURCE_FINDINGS_AND_CONFLICTS.md:109), [JXA-15](SOURCE_FINDINGS_AND_CONFLICTS.md:114), [JXA-16](SOURCE_FINDINGS_AND_CONFLICTS.md:115), [JXA-23](SOURCE_FINDINGS_AND_CONFLICTS.md:122), [JFN-04](SOURCE_FINDINGS_AND_CONFLICTS.md:138), [JFN-08](SOURCE_FINDINGS_AND_CONFLICTS.md:142), [JFN-10](SOURCE_FINDINGS_AND_CONFLICTS.md:144), [JCV-U01](SOURCE_FINDINGS_AND_CONFLICTS.md:154), [CRL-06](SOURCE_FINDINGS_AND_CONFLICTS.md:222), [AM1-09](SOURCE_FINDINGS_AND_CONFLICTS.md:289), [MAV-08](SOURCE_FINDINGS_AND_CONFLICTS.md:512), [MAV-12](SOURCE_FINDINGS_AND_CONFLICTS.md:516), [PIN003-01](SOURCE_FINDINGS_AND_CONFLICTS.md:819), [PIN003-02](SOURCE_FINDINGS_AND_CONFLICTS.md:820), [PIN003-03](SOURCE_FINDINGS_AND_CONFLICTS.md:821), [PIN003-04](SOURCE_FINDINGS_AND_CONFLICTS.md:822), [PIN004-01](SOURCE_FINDINGS_AND_CONFLICTS.md:823), [PIN013-01](SOURCE_FINDINGS_AND_CONFLICTS.md:857), [PIN013-02](SOURCE_FINDINGS_AND_CONFLICTS.md:858), [PIN013-03](SOURCE_FINDINGS_AND_CONFLICTS.md:859), [PIN013-04](SOURCE_FINDINGS_AND_CONFLICTS.md:860), [PIN013-05](SOURCE_FINDINGS_AND_CONFLICTS.md:861), [PIN013-06](SOURCE_FINDINGS_AND_CONFLICTS.md:862), [PIN015-01](SOURCE_FINDINGS_AND_CONFLICTS.md:865), [PIN015-02](SOURCE_FINDINGS_AND_CONFLICTS.md:866), [PIN015-03](SOURCE_FINDINGS_AND_CONFLICTS.md:867), [PIN025-01](SOURCE_FINDINGS_AND_CONFLICTS.md:899), [PIN039-01](SOURCE_FINDINGS_AND_CONFLICTS.md:933), [PIN039-02](SOURCE_FINDINGS_AND_CONFLICTS.md:934), [PIN040-01](SOURCE_FINDINGS_AND_CONFLICTS.md:935), [PIN040-02](SOURCE_FINDINGS_AND_CONFLICTS.md:936), [PIN041-01](SOURCE_FINDINGS_AND_CONFLICTS.md:938), [PIN041-02](SOURCE_FINDINGS_AND_CONFLICTS.md:939), [PIN041-03](SOURCE_FINDINGS_AND_CONFLICTS.md:940), [PIN042-01](SOURCE_FINDINGS_AND_CONFLICTS.md:942), [PIN042-02](SOURCE_FINDINGS_AND_CONFLICTS.md:943), [PIN046-01](SOURCE_FINDINGS_AND_CONFLICTS.md:955), [PIN047-01](SOURCE_FINDINGS_AND_CONFLICTS.md:956), [PIN047-02](SOURCE_FINDINGS_AND_CONFLICTS.md:957), [PIN047-03](SOURCE_FINDINGS_AND_CONFLICTS.md:958), [PIN049-01](SOURCE_FINDINGS_AND_CONFLICTS.md:964), [PIN049-02](SOURCE_FINDINGS_AND_CONFLICTS.md:965), [PIN049-03](SOURCE_FINDINGS_AND_CONFLICTS.md:966), [PIN054-01](SOURCE_FINDINGS_AND_CONFLICTS.md:978), [PIN054-02](SOURCE_FINDINGS_AND_CONFLICTS.md:979), [PIN061-01](SOURCE_FINDINGS_AND_CONFLICTS.md:997), [PIN061-02](SOURCE_FINDINGS_AND_CONFLICTS.md:998), [PIN061-03](SOURCE_FINDINGS_AND_CONFLICTS.md:999), [PIN064-01](SOURCE_FINDINGS_AND_CONFLICTS.md:1009), [PIN064-02](SOURCE_FINDINGS_AND_CONFLICTS.md:1010), [PIN073-01](SOURCE_FINDINGS_AND_CONFLICTS.md:1048), [PIN073-02](SOURCE_FINDINGS_AND_CONFLICTS.md:1049), [PIN074-01](SOURCE_FINDINGS_AND_CONFLICTS.md:1051), [PIN074-02](SOURCE_FINDINGS_AND_CONFLICTS.md:1052), [PIN076-01](SOURCE_FINDINGS_AND_CONFLICTS.md:1057), [PIN076-02](SOURCE_FINDINGS_AND_CONFLICTS.md:1058), [PIN080-01](SOURCE_FINDINGS_AND_CONFLICTS.md:1071), [PIN080-02](SOURCE_FINDINGS_AND_CONFLICTS.md:1072), [PIN080-03](SOURCE_FINDINGS_AND_CONFLICTS.md:1073), [PIN081-01](SOURCE_FINDINGS_AND_CONFLICTS.md:1075), [PIN081-02](SOURCE_FINDINGS_AND_CONFLICTS.md:1076), [PIN081-03](SOURCE_FINDINGS_AND_CONFLICTS.md:1077), [PIN081-04](SOURCE_FINDINGS_AND_CONFLICTS.md:1078), [PIN082-01](SOURCE_FINDINGS_AND_CONFLICTS.md:1080), [PIN082-02](SOURCE_FINDINGS_AND_CONFLICTS.md:1081), [PIN082-03](SOURCE_FINDINGS_AND_CONFLICTS.md:1082).

<a id="up-l03-rth_eth"></a>
#### L03.RTH_ETH — Prior-RTH and full-session memory

[Existing definition, target and P0–P7](experiments/L.md#l03-rth_eth) remain binding.

**Specific upgrade scope.** Attach graded overnight/current-session touch, pressure, acceptance and reclaim memory to prior-RTH/full-session objects.

**Local comparison.** Compare faithful RTH-only freshness, ETH flag and duration/pressure-aware role models without changing anchors.

**Additional cases.** ETH wick; sustained overnight acceptance; missing ETH; 06–09 inner versus RTH outer.

<a id="up-l04"></a>
### UP-L04 — Statistical bounds and improved P-zones

Parent: [L04](components/LOCATION.md); [local phases](experiments/L.md#l04); [definition refinement](SYSTEM_REFINEMENT.md#sr-l04). Upgrade role: `location`.

**Starting idea.** Use mean/SD bands or an opaque named P-zone.

**Existing improvement path.** Distinct disclosed formulas, conditional excursion distributions and explicit geometry/uncertainty types.

**Remaining weakness.** Point quantiles can be unstable, disconnected from action roles and overfit when width or snapping changes the outcome definition.

**Further upgrade.** Construct candidate regions from a frozen conditional excursion/path distribution with density support, overshoot and role uncertainty reported separately. Compare free bands, soft nearby-structure features and bounded snapping under matched width/count and evaluation targets; optimize only within training and preserve undisclosed-formula limits.

**Fair comparison.** Disclosed source bands, conditional quantiles, supported density regions and matched snapping/refinement variants.

**Evidence.** Quantile/path calibration, region stability, cost-aware location precision and selected net after width controls.

**Additional local cases to implement.** Sparse tail; multimodal density; mapping uncertainty confused with contact width; snapped band relabels success; unavailable source formula.

**Decision or system use.** Turn statistical range information into testable regions whose apparent improvement is not merely a wider target or hindsight snap.

**Exact reviewed source clauses.** [JSS-01](SOURCE_FINDINGS_AND_CONFLICTS.md:11), [JSS-02](SOURCE_FINDINGS_AND_CONFLICTS.md:12), [JSS-03](SOURCE_FINDINGS_AND_CONFLICTS.md:13), [JSS-04](SOURCE_FINDINGS_AND_CONFLICTS.md:14), [JSS-05](SOURCE_FINDINGS_AND_CONFLICTS.md:15), [JSS-06](SOURCE_FINDINGS_AND_CONFLICTS.md:16), [JSS-07](SOURCE_FINDINGS_AND_CONFLICTS.md:17), [JXA-11](SOURCE_FINDINGS_AND_CONFLICTS.md:110), [JXA-19](SOURCE_FINDINGS_AND_CONFLICTS.md:118), [JXA-22](SOURCE_FINDINGS_AND_CONFLICTS.md:121), [JFN-07](SOURCE_FINDINGS_AND_CONFLICTS.md:141), [JFN-11](SOURCE_FINDINGS_AND_CONFLICTS.md:145), [JCV-U01](SOURCE_FINDINGS_AND_CONFLICTS.md:154), [CEX-03](SOURCE_FINDINGS_AND_CONFLICTS.md:185), [VX4-01](SOURCE_FINDINGS_AND_CONFLICTS.md:324), [VX4-02](SOURCE_FINDINGS_AND_CONFLICTS.md:325), [VX4-03](SOURCE_FINDINGS_AND_CONFLICTS.md:326), [VX4-04](SOURCE_FINDINGS_AND_CONFLICTS.md:327), [VX4-05](SOURCE_FINDINGS_AND_CONFLICTS.md:328), [VX4-06](SOURCE_FINDINGS_AND_CONFLICTS.md:329), [VX4-07](SOURCE_FINDINGS_AND_CONFLICTS.md:330), [VX4-08](SOURCE_FINDINGS_AND_CONFLICTS.md:331), [VX4-09](SOURCE_FINDINGS_AND_CONFLICTS.md:332), [PIN006-01](SOURCE_FINDINGS_AND_CONFLICTS.md:833), [PIN006-02](SOURCE_FINDINGS_AND_CONFLICTS.md:834), [PIN006-03](SOURCE_FINDINGS_AND_CONFLICTS.md:835), [PIN007-01](SOURCE_FINDINGS_AND_CONFLICTS.md:836), [PIN007-02](SOURCE_FINDINGS_AND_CONFLICTS.md:837), [PIN007-03](SOURCE_FINDINGS_AND_CONFLICTS.md:838), [PIN007-04](SOURCE_FINDINGS_AND_CONFLICTS.md:839), [PIN007-05](SOURCE_FINDINGS_AND_CONFLICTS.md:840), [PIN011-03](SOURCE_FINDINGS_AND_CONFLICTS.md:847), [PIN014-01](SOURCE_FINDINGS_AND_CONFLICTS.md:863), [PIN014-02](SOURCE_FINDINGS_AND_CONFLICTS.md:864), [PIN016-01](SOURCE_FINDINGS_AND_CONFLICTS.md:868), [PIN016-02](SOURCE_FINDINGS_AND_CONFLICTS.md:869), [PIN016-03](SOURCE_FINDINGS_AND_CONFLICTS.md:870), [PIN016-04](SOURCE_FINDINGS_AND_CONFLICTS.md:871), [PIN018-01](SOURCE_FINDINGS_AND_CONFLICTS.md:876), [PIN018-02](SOURCE_FINDINGS_AND_CONFLICTS.md:877), [PIN019-01](SOURCE_FINDINGS_AND_CONFLICTS.md:887), [PIN019-02](SOURCE_FINDINGS_AND_CONFLICTS.md:888), [PIN019-03](SOURCE_FINDINGS_AND_CONFLICTS.md:889), [PIN026-01](SOURCE_FINDINGS_AND_CONFLICTS.md:900), [PIN026-02](SOURCE_FINDINGS_AND_CONFLICTS.md:901), [PIN027-01](SOURCE_FINDINGS_AND_CONFLICTS.md:902), [PIN027-02](SOURCE_FINDINGS_AND_CONFLICTS.md:903), [PIN028-01](SOURCE_FINDINGS_AND_CONFLICTS.md:904), [PIN028-02](SOURCE_FINDINGS_AND_CONFLICTS.md:905), [PIN028-03](SOURCE_FINDINGS_AND_CONFLICTS.md:906), [PIN029-01](SOURCE_FINDINGS_AND_CONFLICTS.md:907), [PIN029-02](SOURCE_FINDINGS_AND_CONFLICTS.md:908), [PIN029-03](SOURCE_FINDINGS_AND_CONFLICTS.md:909), [PIN030-01](SOURCE_FINDINGS_AND_CONFLICTS.md:910), [PIN030-02](SOURCE_FINDINGS_AND_CONFLICTS.md:911), [PIN030-03](SOURCE_FINDINGS_AND_CONFLICTS.md:912), [PIN043-01](SOURCE_FINDINGS_AND_CONFLICTS.md:944), [PIN045-01](SOURCE_FINDINGS_AND_CONFLICTS.md:948), [PIN045-02](SOURCE_FINDINGS_AND_CONFLICTS.md:949), [PIN045-03](SOURCE_FINDINGS_AND_CONFLICTS.md:950), [PIN045-04](SOURCE_FINDINGS_AND_CONFLICTS.md:951), [PIN045-05](SOURCE_FINDINGS_AND_CONFLICTS.md:952), [PIN045-06](SOURCE_FINDINGS_AND_CONFLICTS.md:953), [PIN048-01](SOURCE_FINDINGS_AND_CONFLICTS.md:960), [PIN048-02](SOURCE_FINDINGS_AND_CONFLICTS.md:961), [PIN048-03](SOURCE_FINDINGS_AND_CONFLICTS.md:962), [PIN052-01](SOURCE_FINDINGS_AND_CONFLICTS.md:974), [PIN052-02](SOURCE_FINDINGS_AND_CONFLICTS.md:975), [PIN052-03](SOURCE_FINDINGS_AND_CONFLICTS.md:976), [PIN055-01](SOURCE_FINDINGS_AND_CONFLICTS.md:980), [PIN055-02](SOURCE_FINDINGS_AND_CONFLICTS.md:981), [PIN057-01](SOURCE_FINDINGS_AND_CONFLICTS.md:985), [PIN057-02](SOURCE_FINDINGS_AND_CONFLICTS.md:986), [PIN057-03](SOURCE_FINDINGS_AND_CONFLICTS.md:987), [PIN058-01](SOURCE_FINDINGS_AND_CONFLICTS.md:989), [PIN059-01](SOURCE_FINDINGS_AND_CONFLICTS.md:990), [PIN059-02](SOURCE_FINDINGS_AND_CONFLICTS.md:991), [PIN062-01](SOURCE_FINDINGS_AND_CONFLICTS.md:1001), [PIN062-02](SOURCE_FINDINGS_AND_CONFLICTS.md:1002), [PIN062-03](SOURCE_FINDINGS_AND_CONFLICTS.md:1003), [PIN063-01](SOURCE_FINDINGS_AND_CONFLICTS.md:1005), [PIN063-02](SOURCE_FINDINGS_AND_CONFLICTS.md:1006), [PIN063-03](SOURCE_FINDINGS_AND_CONFLICTS.md:1007), [PIN065-01](SOURCE_FINDINGS_AND_CONFLICTS.md:1012), [PIN065-02](SOURCE_FINDINGS_AND_CONFLICTS.md:1013), [PIN065-03](SOURCE_FINDINGS_AND_CONFLICTS.md:1014), [PIN067-01](SOURCE_FINDINGS_AND_CONFLICTS.md:1021), [PIN067-02](SOURCE_FINDINGS_AND_CONFLICTS.md:1022), [PIN068-01](SOURCE_FINDINGS_AND_CONFLICTS.md:1024), [PIN068-02](SOURCE_FINDINGS_AND_CONFLICTS.md:1025), [PIN068-03](SOURCE_FINDINGS_AND_CONFLICTS.md:1026), [PIN070-01](SOURCE_FINDINGS_AND_CONFLICTS.md:1033), [PIN070-02](SOURCE_FINDINGS_AND_CONFLICTS.md:1034), [PIN075-01](SOURCE_FINDINGS_AND_CONFLICTS.md:1054), [PIN075-02](SOURCE_FINDINGS_AND_CONFLICTS.md:1055), [PIN078-01](SOURCE_FINDINGS_AND_CONFLICTS.md:1063), [PIN078-02](SOURCE_FINDINGS_AND_CONFLICTS.md:1064), [PIN083-01](SOURCE_FINDINGS_AND_CONFLICTS.md:1084), [PIN083-02](SOURCE_FINDINGS_AND_CONFLICTS.md:1085).

**Conversation upgrade lineage.** [DTM-A04](SOURCE_FINDINGS_AND_CONFLICTS.md:62), [JCV-U01](SOURCE_FINDINGS_AND_CONFLICTS.md:154), [DRF-U08](SOURCE_FINDINGS_AND_CONFLICTS.md:432), [DRF-A21](SOURCE_FINDINGS_AND_CONFLICTS.md:462). Read the full rows and their original conversation references; [the recheck](CONVERSATION_RECHECK.md) preserves the exact unit/exception routes.

<a id="up-l04-width_snap"></a>
#### L04.WIDTH_SNAP — Zone precision and spatial refinement

[Existing definition, target and P0–P7](experiments/L.md#l04-width_snap) remain binding.

**Specific upgrade scope.** Test bounded spatial refinement, soft structure-distance features and snapping under matched contact width/count and frozen labels.

**Local comparison.** Compare free zones and each refinement with fold-local generation/scoring and cost-aware selected value.

**Additional cases.** Wider zone raises hit rate; snap changes target; uncertainty not tolerance; outer-test tuning.

<a id="up-l04-zone_definition"></a>
#### L04.ZONE_DEFINITION — Statistical-zone anchors and uncertainty

[Existing definition, target and P0–P7](experiments/L.md#l04-zone_definition) remain binding.

**Specific upgrade scope.** Derive supported conditional regions from the exact declared excursion/dispersion target, with geometry and estimation uncertainty separate.

**Local comparison.** Compare all disclosed source populations/formulas, conditional quantiles and density regions; undisclosed formula remains unresolved.

**Additional cases.** Open-relative versus edge-relative; multimodal tails; sample mismatch; unavailable proprietary formula.

<a id="up-l05"></a>
### UP-L05 — Volume-profile value, nodes, shelves and valleys

Parent: [L05](components/LOCATION.md); [local phases](experiments/L.md#l05); [definition refinement](SYSTEM_REFINEMENT.md#sr-l05). Upgrade role: `location`.

**Starting idea.** Trade POC, value edges and visible peaks.

**Existing improvement path.** Full profile landmarks, multimodal separators, shelves/valleys and conditional roles.

**Remaining weakness.** Fixed prominence thresholds can create many unstable nodes and miss changing relevance as the auction develops.

**Further upgrade.** Use M04's multiscale persistence and developing residual shape to generate region proposals with support/identity uncertainty. Compare landmark-only roles with predicted profile-evolution features, distinguishing future mass accumulation, traversal and reversal; equalize node density and widths before judging precision.

**Fair comparison.** POC/VA, source topology, stable multiscale regions, evolution-conditioned roles and compatible random/grid controls.

**Evidence.** Node stability, future profile/path loss, useful role lifetime, width/count-matched net and compute.

**Additional local cases to implement.** POC plateau; small persistent node; empty historic valley with thick current book; new volume creates competing mode.

**Decision or system use.** Improve which auction regions are proposed and what role they are likely to play, beyond adding more profile lines.

**Exact reviewed source clauses.** [DTM-A04](SOURCE_FINDINGS_AND_CONFLICTS.md:62), [DTM-A11](SOURCE_FINDINGS_AND_CONFLICTS.md:69), [JXA-09](SOURCE_FINDINGS_AND_CONFLICTS.md:108), [JXA-15](SOURCE_FINDINGS_AND_CONFLICTS.md:114), [JXA-16](SOURCE_FINDINGS_AND_CONFLICTS.md:115), [JFN-06](SOURCE_FINDINGS_AND_CONFLICTS.md:140), [JFN-08](SOURCE_FINDINGS_AND_CONFLICTS.md:142), [JCV-U01](SOURCE_FINDINGS_AND_CONFLICTS.md:154), [JCV-U02](SOURCE_FINDINGS_AND_CONFLICTS.md:155), [JCV-A01](SOURCE_FINDINGS_AND_CONFLICTS.md:160), [CRL-01](SOURCE_FINDINGS_AND_CONFLICTS.md:217), [CRL-06](SOURCE_FINDINGS_AND_CONFLICTS.md:222), [CRL-12](SOURCE_FINDINGS_AND_CONFLICTS.md:228), [AM1-01](SOURCE_FINDINGS_AND_CONFLICTS.md:281), [AM1-02](SOURCE_FINDINGS_AND_CONFLICTS.md:282), [AM1-03](SOURCE_FINDINGS_AND_CONFLICTS.md:283), [AM1-04](SOURCE_FINDINGS_AND_CONFLICTS.md:284), [AM1-05](SOURCE_FINDINGS_AND_CONFLICTS.md:285), [AM1-06](SOURCE_FINDINGS_AND_CONFLICTS.md:286), [AM1-07](SOURCE_FINDINGS_AND_CONFLICTS.md:287), [AM1-08](SOURCE_FINDINGS_AND_CONFLICTS.md:288), [AM1-09](SOURCE_FINDINGS_AND_CONFLICTS.md:289), [AM1-10](SOURCE_FINDINGS_AND_CONFLICTS.md:290), [VP2-01](SOURCE_FINDINGS_AND_CONFLICTS.md:298), [VP2-02](SOURCE_FINDINGS_AND_CONFLICTS.md:299), [VP2-03](SOURCE_FINDINGS_AND_CONFLICTS.md:300), [VP2-04](SOURCE_FINDINGS_AND_CONFLICTS.md:301), [VP2-05](SOURCE_FINDINGS_AND_CONFLICTS.md:302), [TP3-07](SOURCE_FINDINGS_AND_CONFLICTS.md:316), [CD3-04](SOURCE_FINDINGS_AND_CONFLICTS.md:407), [CD3-05](SOURCE_FINDINGS_AND_CONFLICTS.md:408), [DRF-A20](SOURCE_FINDINGS_AND_CONFLICTS.md:461), [MAV-01](SOURCE_FINDINGS_AND_CONFLICTS.md:505), [MAV-02](SOURCE_FINDINGS_AND_CONFLICTS.md:506), [MAV-03](SOURCE_FINDINGS_AND_CONFLICTS.md:507), [MAV-04](SOURCE_FINDINGS_AND_CONFLICTS.md:508), [MAV-05](SOURCE_FINDINGS_AND_CONFLICTS.md:509), [MAV-06](SOURCE_FINDINGS_AND_CONFLICTS.md:510), [MAV-07](SOURCE_FINDINGS_AND_CONFLICTS.md:511), [MAV-08](SOURCE_FINDINGS_AND_CONFLICTS.md:512), [MAV-09](SOURCE_FINDINGS_AND_CONFLICTS.md:513), [MAV-10](SOURCE_FINDINGS_AND_CONFLICTS.md:514), [MAV-11](SOURCE_FINDINGS_AND_CONFLICTS.md:515), [MAV-12](SOURCE_FINDINGS_AND_CONFLICTS.md:516), [MAV-13](SOURCE_FINDINGS_AND_CONFLICTS.md:517), [MAV-14](SOURCE_FINDINGS_AND_CONFLICTS.md:518), [MAT-01](SOURCE_FINDINGS_AND_CONFLICTS.md:526), [MAT-02](SOURCE_FINDINGS_AND_CONFLICTS.md:527), [MAT-03](SOURCE_FINDINGS_AND_CONFLICTS.md:528), [MAT-04](SOURCE_FINDINGS_AND_CONFLICTS.md:529), [MAT-05](SOURCE_FINDINGS_AND_CONFLICTS.md:530), [MAT-06](SOURCE_FINDINGS_AND_CONFLICTS.md:531), [MAT-07](SOURCE_FINDINGS_AND_CONFLICTS.md:532), [MAT-08](SOURCE_FINDINGS_AND_CONFLICTS.md:533), [MAT-09](SOURCE_FINDINGS_AND_CONFLICTS.md:534), [RVP-01](SOURCE_FINDINGS_AND_CONFLICTS.md:542), [RVP-02](SOURCE_FINDINGS_AND_CONFLICTS.md:543), [RVP-03](SOURCE_FINDINGS_AND_CONFLICTS.md:544), [RVP-04](SOURCE_FINDINGS_AND_CONFLICTS.md:545), [RVP-05](SOURCE_FINDINGS_AND_CONFLICTS.md:546), [RVP-06](SOURCE_FINDINGS_AND_CONFLICTS.md:547), [RVP-07](SOURCE_FINDINGS_AND_CONFLICTS.md:548), [RVP-08](SOURCE_FINDINGS_AND_CONFLICTS.md:549), [ALM-01](SOURCE_FINDINGS_AND_CONFLICTS.md:564), [ALM-02](SOURCE_FINDINGS_AND_CONFLICTS.md:565), [ALM-03](SOURCE_FINDINGS_AND_CONFLICTS.md:566), [ALM-04](SOURCE_FINDINGS_AND_CONFLICTS.md:567), [ALM-05](SOURCE_FINDINGS_AND_CONFLICTS.md:568), [ALM-06](SOURCE_FINDINGS_AND_CONFLICTS.md:569), [YMA-01](SOURCE_FINDINGS_AND_CONFLICTS.md:589), [YMA-02](SOURCE_FINDINGS_AND_CONFLICTS.md:590), [YMA-03](SOURCE_FINDINGS_AND_CONFLICTS.md:591), [YMA-04](SOURCE_FINDINGS_AND_CONFLICTS.md:592), [YMA-05](SOURCE_FINDINGS_AND_CONFLICTS.md:593), [YMA-06](SOURCE_FINDINGS_AND_CONFLICTS.md:594), [K10-01](SOURCE_FINDINGS_AND_CONFLICTS.md:639), [K10-02](SOURCE_FINDINGS_AND_CONFLICTS.md:640), [K10-03](SOURCE_FINDINGS_AND_CONFLICTS.md:641), [K10-04](SOURCE_FINDINGS_AND_CONFLICTS.md:642), [K10-05](SOURCE_FINDINGS_AND_CONFLICTS.md:643), [K10-06](SOURCE_FINDINGS_AND_CONFLICTS.md:644), [K18-02](SOURCE_FINDINGS_AND_CONFLICTS.md:653), [F23-01](SOURCE_FINDINGS_AND_CONFLICTS.md:667), [F23-02](SOURCE_FINDINGS_AND_CONFLICTS.md:668), [F23-03](SOURCE_FINDINGS_AND_CONFLICTS.md:669), [F23-04](SOURCE_FINDINGS_AND_CONFLICTS.md:670), [F23-05](SOURCE_FINDINGS_AND_CONFLICTS.md:671), [F23-06](SOURCE_FINDINGS_AND_CONFLICTS.md:672), [F23-07](SOURCE_FINDINGS_AND_CONFLICTS.md:673), [CCS-01](SOURCE_FINDINGS_AND_CONFLICTS.md:681), [CCS-02](SOURCE_FINDINGS_AND_CONFLICTS.md:682), [CCS-03](SOURCE_FINDINGS_AND_CONFLICTS.md:683), [CCS-04](SOURCE_FINDINGS_AND_CONFLICTS.md:684), [CCS-05](SOURCE_FINDINGS_AND_CONFLICTS.md:685), [CCS-06](SOURCE_FINDINGS_AND_CONFLICTS.md:686), [CCS-07](SOURCE_FINDINGS_AND_CONFLICTS.md:687), [CCS-08](SOURCE_FINDINGS_AND_CONFLICTS.md:688), [TBR-01](SOURCE_FINDINGS_AND_CONFLICTS.md:736), [TBR-02](SOURCE_FINDINGS_AND_CONFLICTS.md:737), [TBR-03](SOURCE_FINDINGS_AND_CONFLICTS.md:738), [TBR-04](SOURCE_FINDINGS_AND_CONFLICTS.md:739), [TBR-05](SOURCE_FINDINGS_AND_CONFLICTS.md:740), [TBR-06](SOURCE_FINDINGS_AND_CONFLICTS.md:741), [TBR-07](SOURCE_FINDINGS_AND_CONFLICTS.md:742), [OBT-04](SOURCE_FINDINGS_AND_CONFLICTS.md:753), [OBT-05](SOURCE_FINDINGS_AND_CONFLICTS.md:754), [AUT-09](SOURCE_FINDINGS_AND_CONFLICTS.md:775), [PIN066-01](SOURCE_FINDINGS_AND_CONFLICTS.md:1016), [PIN066-02](SOURCE_FINDINGS_AND_CONFLICTS.md:1017), [PIN066-03](SOURCE_FINDINGS_AND_CONFLICTS.md:1018), [PIN066-04](SOURCE_FINDINGS_AND_CONFLICTS.md:1019), [PIN077-01](SOURCE_FINDINGS_AND_CONFLICTS.md:1060), [PIN077-02](SOURCE_FINDINGS_AND_CONFLICTS.md:1061).

**Conversation upgrade lineage.** [JCV-A01](SOURCE_FINDINGS_AND_CONFLICTS.md:160), [CRL-12](SOURCE_FINDINGS_AND_CONFLICTS.md:228). Read the full rows and their original conversation references; [the recheck](CONVERSATION_RECHECK.md) preserves the exact unit/exception routes.

<a id="up-l05-profile_roles"></a>
#### L05.PROFILE_ROLES — POC, value, shelves and valleys

[Existing definition, target and P0–P7](experiments/L.md#l05-profile_roles) remain binding.

**Specific upgrade scope.** Use stable multiscale profile regions and predicted added-mass/evolution features to forecast every POC/VA/node/shelf/valley role.

**Local comparison.** Compare landmark-only, stable geometry and evolution-conditioned roles with compatible grid/random controls.

**Additional cases.** POC plateau; small node; valley not book liquidity; new mode; changing maturity.

<a id="up-l06"></a>
### UP-L06 — Delta-profile and side-concentration locations

Parent: [L06](components/LOCATION.md); [local phases](experiments/L.md#l06); [definition refinement](SYSTEM_REFINEMENT.md#sr-l06). Upgrade role: `location`.

**Starting idea.** Use the biggest positive/negative delta shelf.

**Existing improvement path.** Separate buy/sell/unknown geometry and conditional side roles.

**Remaining weakness.** Net peaks can hide opposing supported shelves, and location strength lacks confidence and evolving pressure context.

**Further upgrade.** Generate side-specific supported regions from shrunken contrast and intensity fields, retaining overlapping opposing evidence. Attach new-flow, pressure-dose, uncertainty and subsequent observed reward states; compare joint side-role inference with total-profile and net-delta-only locations.

**Fair comparison.** Volume-only, raw delta peak, supported side regions and context/flow-conditioned role model.

**Evidence.** Region support/stability, side-role calibration, unknown-sign sensitivity and net beyond volume profile.

**Additional local cases to implement.** Two large opposing shelves; tiny extreme ratio; unknown-side mass changes rank; strong positive delta followed by failure.

**Decision or system use.** Distinguish economically useful directional concentration from cancellation artifacts and unsupported imbalance.

**Exact reviewed source clauses.** [DTM-A11](SOURCE_FINDINGS_AND_CONFLICTS.md:69), [JXA-09](SOURCE_FINDINGS_AND_CONFLICTS.md:108), [JXA-15](SOURCE_FINDINGS_AND_CONFLICTS.md:114), [JXA-16](SOURCE_FINDINGS_AND_CONFLICTS.md:115), [JFN-08](SOURCE_FINDINGS_AND_CONFLICTS.md:142), [JCV-U01](SOURCE_FINDINGS_AND_CONFLICTS.md:154), [JCV-U02](SOURCE_FINDINGS_AND_CONFLICTS.md:155), [JCV-A01](SOURCE_FINDINGS_AND_CONFLICTS.md:160), [CRL-01](SOURCE_FINDINGS_AND_CONFLICTS.md:217), [CRL-06](SOURCE_FINDINGS_AND_CONFLICTS.md:222), [RDL-01](SOURCE_FINDINGS_AND_CONFLICTS.md:550), [RDL-02](SOURCE_FINDINGS_AND_CONFLICTS.md:551), [RDL-03](SOURCE_FINDINGS_AND_CONFLICTS.md:552), [RDL-04](SOURCE_FINDINGS_AND_CONFLICTS.md:553), [RDL-05](SOURCE_FINDINGS_AND_CONFLICTS.md:554), [RDL-06](SOURCE_FINDINGS_AND_CONFLICTS.md:555), [RDL-07](SOURCE_FINDINGS_AND_CONFLICTS.md:556), [YMA-03](SOURCE_FINDINGS_AND_CONFLICTS.md:591), [K18-01](SOURCE_FINDINGS_AND_CONFLICTS.md:652), [K18-02](SOURCE_FINDINGS_AND_CONFLICTS.md:653), [K18-03](SOURCE_FINDINGS_AND_CONFLICTS.md:654), [K18-04](SOURCE_FINDINGS_AND_CONFLICTS.md:655), [K18-05](SOURCE_FINDINGS_AND_CONFLICTS.md:656), [K18-06](SOURCE_FINDINGS_AND_CONFLICTS.md:657), [K18-07](SOURCE_FINDINGS_AND_CONFLICTS.md:658), [K18-08](SOURCE_FINDINGS_AND_CONFLICTS.md:659), [CCS-03](SOURCE_FINDINGS_AND_CONFLICTS.md:683), [TBR-01](SOURCE_FINDINGS_AND_CONFLICTS.md:736), [TBR-02](SOURCE_FINDINGS_AND_CONFLICTS.md:737), [TBR-03](SOURCE_FINDINGS_AND_CONFLICTS.md:738), [TBR-04](SOURCE_FINDINGS_AND_CONFLICTS.md:739), [TBR-05](SOURCE_FINDINGS_AND_CONFLICTS.md:740), [TBR-06](SOURCE_FINDINGS_AND_CONFLICTS.md:741), [TBR-07](SOURCE_FINDINGS_AND_CONFLICTS.md:742), [PIN066-01](SOURCE_FINDINGS_AND_CONFLICTS.md:1016), [PIN066-02](SOURCE_FINDINGS_AND_CONFLICTS.md:1017), [PIN066-03](SOURCE_FINDINGS_AND_CONFLICTS.md:1018), [PIN066-04](SOURCE_FINDINGS_AND_CONFLICTS.md:1019), [PIN077-01](SOURCE_FINDINGS_AND_CONFLICTS.md:1060), [PIN077-02](SOURCE_FINDINGS_AND_CONFLICTS.md:1061).

**Conversation upgrade lineage.** [CRL-13](SOURCE_FINDINGS_AND_CONFLICTS.md:229). Read the full rows and their original conversation references; [the recheck](CONVERSATION_RECHECK.md) preserves the exact unit/exception routes.

<a id="up-l06-delta_roles"></a>
#### L06.DELTA_ROLES — Side-concentration locations

[Existing definition, target and P0–P7](experiments/L.md#l06-delta_roles) remain binding.

**Specific upgrade scope.** Generate supported buy/sell/unknown regions from intensity and shrunken contrast, with novelty/pressure and matured reward state.

**Local comparison.** Compare total/net/side-specific nodes at matched support and geometry before richer role models.

**Additional cases.** Opposing shelves cancel; tiny ratio; uncertain side; positive delta fails to hold.

<a id="up-l07"></a>
### UP-L07 — TPO, initial balance, single prints and auction tails

Parent: [L07](components/LOCATION.md); [local phases](experiments/L.md#l07); [definition refinement](SYSTEM_REFINEMENT.md#sr-l07). Upgrade role: `location`.

**Starting idea.** Treat single prints, IB edges or poor highs as fixed targets.

**Existing improvement path.** Exact TPO/IB variants, causal completion and conditional return/traversal roles.

**Remaining weakness.** Binary auction labels lose degree of repair, visit continuity and the difference between developing and completed structure.

**Further upgrade.** Create graded repair/excess/acceptance fields from M06's visit chronology and dwell bounds, with daily/weekly IB identities preserved. Compare discrete source regions with support-weighted bands and duration-aware role forecasts; developing structures have their own cuts and uncertainty.

**Fair comparison.** Source bracket/IB rules, exact visits/dwell, graded support/repair geometry and conditional role model.

**Evidence.** Definition fidelity, repair/return-time calibration, premature-object error and net increment.

**Additional local cases to implement.** Single print later repaired; provisional tail; short session; weekly IB overlap; same TPO count with different visit order.

**Decision or system use.** Use auction structure according to how it formed and changed, rather than assuming every named pattern has the same completion or destination meaning.

**Exact reviewed source clauses.** [JXA-05](SOURCE_FINDINGS_AND_CONFLICTS.md:104), [AM1-01](SOURCE_FINDINGS_AND_CONFLICTS.md:281), [AM1-02](SOURCE_FINDINGS_AND_CONFLICTS.md:282), [AM1-03](SOURCE_FINDINGS_AND_CONFLICTS.md:283), [AM1-04](SOURCE_FINDINGS_AND_CONFLICTS.md:284), [AM1-05](SOURCE_FINDINGS_AND_CONFLICTS.md:285), [AM1-06](SOURCE_FINDINGS_AND_CONFLICTS.md:286), [AM1-07](SOURCE_FINDINGS_AND_CONFLICTS.md:287), [AM1-08](SOURCE_FINDINGS_AND_CONFLICTS.md:288), [AM1-09](SOURCE_FINDINGS_AND_CONFLICTS.md:289), [AM1-10](SOURCE_FINDINGS_AND_CONFLICTS.md:290), [TP3-01](SOURCE_FINDINGS_AND_CONFLICTS.md:310), [TP3-02](SOURCE_FINDINGS_AND_CONFLICTS.md:311), [TP3-03](SOURCE_FINDINGS_AND_CONFLICTS.md:312), [TP3-04](SOURCE_FINDINGS_AND_CONFLICTS.md:313), [TP3-05](SOURCE_FINDINGS_AND_CONFLICTS.md:314), [TP3-06](SOURCE_FINDINGS_AND_CONFLICTS.md:315), [TP3-07](SOURCE_FINDINGS_AND_CONFLICTS.md:316), [CD3-04](SOURCE_FINDINGS_AND_CONFLICTS.md:407), [MAV-01](SOURCE_FINDINGS_AND_CONFLICTS.md:505), [MAV-02](SOURCE_FINDINGS_AND_CONFLICTS.md:506), [MAV-03](SOURCE_FINDINGS_AND_CONFLICTS.md:507), [MAV-04](SOURCE_FINDINGS_AND_CONFLICTS.md:508), [MAV-05](SOURCE_FINDINGS_AND_CONFLICTS.md:509), [MAV-06](SOURCE_FINDINGS_AND_CONFLICTS.md:510), [MAV-07](SOURCE_FINDINGS_AND_CONFLICTS.md:511), [MAV-08](SOURCE_FINDINGS_AND_CONFLICTS.md:512), [MAV-09](SOURCE_FINDINGS_AND_CONFLICTS.md:513), [MAV-10](SOURCE_FINDINGS_AND_CONFLICTS.md:514), [MAV-11](SOURCE_FINDINGS_AND_CONFLICTS.md:515), [MAV-12](SOURCE_FINDINGS_AND_CONFLICTS.md:516), [MAV-13](SOURCE_FINDINGS_AND_CONFLICTS.md:517), [MAV-14](SOURCE_FINDINGS_AND_CONFLICTS.md:518), [AUT-06](SOURCE_FINDINGS_AND_CONFLICTS.md:772), [PIN026-01](SOURCE_FINDINGS_AND_CONFLICTS.md:900), [PIN026-02](SOURCE_FINDINGS_AND_CONFLICTS.md:901), [PIN027-01](SOURCE_FINDINGS_AND_CONFLICTS.md:902), [PIN027-02](SOURCE_FINDINGS_AND_CONFLICTS.md:903), [PIN028-01](SOURCE_FINDINGS_AND_CONFLICTS.md:904), [PIN028-02](SOURCE_FINDINGS_AND_CONFLICTS.md:905), [PIN028-03](SOURCE_FINDINGS_AND_CONFLICTS.md:906), [PIN029-01](SOURCE_FINDINGS_AND_CONFLICTS.md:907), [PIN029-02](SOURCE_FINDINGS_AND_CONFLICTS.md:908), [PIN029-03](SOURCE_FINDINGS_AND_CONFLICTS.md:909), [PIN030-01](SOURCE_FINDINGS_AND_CONFLICTS.md:910), [PIN030-02](SOURCE_FINDINGS_AND_CONFLICTS.md:911), [PIN030-03](SOURCE_FINDINGS_AND_CONFLICTS.md:912), [PIN043-01](SOURCE_FINDINGS_AND_CONFLICTS.md:944), [PIN048-01](SOURCE_FINDINGS_AND_CONFLICTS.md:960), [PIN048-02](SOURCE_FINDINGS_AND_CONFLICTS.md:961), [PIN048-03](SOURCE_FINDINGS_AND_CONFLICTS.md:962), [PIN058-01](SOURCE_FINDINGS_AND_CONFLICTS.md:989), [PIN059-01](SOURCE_FINDINGS_AND_CONFLICTS.md:990), [PIN059-02](SOURCE_FINDINGS_AND_CONFLICTS.md:991), [PIN078-01](SOURCE_FINDINGS_AND_CONFLICTS.md:1063), [PIN078-02](SOURCE_FINDINGS_AND_CONFLICTS.md:1064).

<a id="up-l07-ib_tpo"></a>
#### L07.IB_TPO — IB, TPO tails and single prints

[Existing definition, target and P0–P7](experiments/L.md#l07-ib_tpo) remain binding.

**Specific upgrade scope.** Use graded occupancy, repair/excess and revisit continuity for daily/weekly IB, tails, single prints and POC roles.

**Local comparison.** Compare discrete source geometry and support-weighted duration/role forecasts on exact brackets/anchors.

**Additional cases.** Provisional single print; weekly IB differs; repaired tail; missing dwell; half-day.

<a id="up-l08"></a>
### UP-L08 — Swing, retracement and dynamic-range locations

Parent: [L08](components/LOCATION.md); [local phases](experiments/L.md#l08); [definition refinement](SYSTEM_REFINEMENT.md#sr-l08). Upgrade role: `location`.

**Starting idea.** Place Fibonacci or quarter retracements on one chosen swing.

**Existing improvement path.** Confirmed/provisional source legs, multiple causal swing definitions and bounded refinement.

**Remaining weakness.** Location quality depends on scale persistence and confirmation delay, which raw retracement ratios ignore.

**Further upgrade.** Generate a nested candidate hierarchy from the causal swing tree, with scale persistence, remaining-leg context and available confirmation time. Compare exact ratio points with uncertainty bands/limited offsets under matched decision delay and count; aggregate repeated geometry without erasing parent-leg lineage.

**Fair comparison.** Each source ratio/anchor, one-scale swings, persistent multiscale hierarchy and bounded refinement.

**Evidence.** Delay-adjusted role/value, scale stability, candidate redundancy and width/count-matched net.

**Additional local cases to implement.** Nested legs propose same tick; late pivot confirmation; moving provisional extreme; ratio remains but parent leg changes.

**Decision or system use.** Select useful retracement geometry from multiple causally available scales instead of privileging one arbitrary lookback.

**Exact reviewed source clauses.** [JXA-16](SOURCE_FINDINGS_AND_CONFLICTS.md:115), [JXA-20](SOURCE_FINDINGS_AND_CONFLICTS.md:119), [CRL-06](SOURCE_FINDINGS_AND_CONFLICTS.md:222), [OSF-01](SOURCE_FINDINGS_AND_CONFLICTS.md:795), [OSF-02](SOURCE_FINDINGS_AND_CONFLICTS.md:796), [OSF-03](SOURCE_FINDINGS_AND_CONFLICTS.md:797), [OSF-04](SOURCE_FINDINGS_AND_CONFLICTS.md:798), [OSF-05](SOURCE_FINDINGS_AND_CONFLICTS.md:799), [OSF-06](SOURCE_FINDINGS_AND_CONFLICTS.md:800), [OSF-07](SOURCE_FINDINGS_AND_CONFLICTS.md:801), [OSF-08](SOURCE_FINDINGS_AND_CONFLICTS.md:802), [OSF-09](SOURCE_FINDINGS_AND_CONFLICTS.md:803), [OSF-10](SOURCE_FINDINGS_AND_CONFLICTS.md:804), [PIN010-01](SOURCE_FINDINGS_AND_CONFLICTS.md:841), [PIN010-02](SOURCE_FINDINGS_AND_CONFLICTS.md:842), [PIN010-03](SOURCE_FINDINGS_AND_CONFLICTS.md:843), [PIN010-04](SOURCE_FINDINGS_AND_CONFLICTS.md:844), [PIN022-01](SOURCE_FINDINGS_AND_CONFLICTS.md:894), [PIN022-02](SOURCE_FINDINGS_AND_CONFLICTS.md:895), [PIN022-03](SOURCE_FINDINGS_AND_CONFLICTS.md:896), [PIN023-01](SOURCE_FINDINGS_AND_CONFLICTS.md:897), [PIN023-02](SOURCE_FINDINGS_AND_CONFLICTS.md:898), [PIN031-01](SOURCE_FINDINGS_AND_CONFLICTS.md:913), [PIN032-01](SOURCE_FINDINGS_AND_CONFLICTS.md:914), [PIN032-02](SOURCE_FINDINGS_AND_CONFLICTS.md:915), [PIN032-03](SOURCE_FINDINGS_AND_CONFLICTS.md:916), [PIN035-01](SOURCE_FINDINGS_AND_CONFLICTS.md:920), [PIN035-02](SOURCE_FINDINGS_AND_CONFLICTS.md:921), [PIN035-03](SOURCE_FINDINGS_AND_CONFLICTS.md:922), [PIN035-04](SOURCE_FINDINGS_AND_CONFLICTS.md:923), [PIN036-01](SOURCE_FINDINGS_AND_CONFLICTS.md:925), [PIN036-02](SOURCE_FINDINGS_AND_CONFLICTS.md:926), [PIN037-01](SOURCE_FINDINGS_AND_CONFLICTS.md:927), [PIN037-02](SOURCE_FINDINGS_AND_CONFLICTS.md:928), [PIN038-01](SOURCE_FINDINGS_AND_CONFLICTS.md:930), [PIN038-02](SOURCE_FINDINGS_AND_CONFLICTS.md:931), [PIN051-01](SOURCE_FINDINGS_AND_CONFLICTS.md:971), [PIN051-02](SOURCE_FINDINGS_AND_CONFLICTS.md:972), [PIN056-01](SOURCE_FINDINGS_AND_CONFLICTS.md:983), [PIN056-02](SOURCE_FINDINGS_AND_CONFLICTS.md:984), [PIN060-01](SOURCE_FINDINGS_AND_CONFLICTS.md:993), [PIN060-02](SOURCE_FINDINGS_AND_CONFLICTS.md:994), [PIN060-03](SOURCE_FINDINGS_AND_CONFLICTS.md:995), [PIN071-01](SOURCE_FINDINGS_AND_CONFLICTS.md:1036), [PIN071-02](SOURCE_FINDINGS_AND_CONFLICTS.md:1037), [PIN071-03](SOURCE_FINDINGS_AND_CONFLICTS.md:1038), [PIN071-04](SOURCE_FINDINGS_AND_CONFLICTS.md:1039), [PIN071-05](SOURCE_FINDINGS_AND_CONFLICTS.md:1040), [PIN071-06](SOURCE_FINDINGS_AND_CONFLICTS.md:1041), [PIN071-07](SOURCE_FINDINGS_AND_CONFLICTS.md:1042), [PIN071-08](SOURCE_FINDINGS_AND_CONFLICTS.md:1043).

<a id="up-l08-swing_refinement"></a>
#### L08.SWING_REFINEMENT — Swing and dynamic retracement locations

[Existing definition, target and P0–P7](experiments/L.md#l08-swing_refinement) remain binding.

**Specific upgrade scope.** Propose nested persistent swing/retracement regions with confirmation-delay and parent-leg uncertainty.

**Local comparison.** Compare every source ratio/anchor, one-scale and multiscale/bounded offset alternatives at equal count/width/delay.

**Additional cases.** Nested duplicates; late pivot; provisional move; unchanged ratio new leg.

<a id="up-l09"></a>
### UP-L09 — FVG, imbalance and displacement-origin zones

Parent: [L09](components/LOCATION.md); [local phases](experiments/L.md#l09); [definition refinement](SYSTEM_REFINEMENT.md#sr-l09). Upgrade role: `location`.

**Starting idea.** An FVG or gap is an inefficiency that must fill.

**Existing improvement path.** Separate price/body/volume imbalance definitions, causal birth and partial/full mitigation.

**Remaining weakness.** A fill flag omits repair depth, elapsed time, trading within the gap and whether the gap is unusual for that activity state.

**Further upgrade.** Maintain a typed spatial repair field and progress/duration history, normalized by formation volatility/activity. Compare geometric gap features with actual trade/footprint support when available, using competing continuation, partial repair and full traversal roles; preserve every source geometry.

**Fair comparison.** Exact gap rules, size/age baseline, repair-field model and measured-volume challenger on matched cohorts.

**Evidence.** Gap-type fidelity, repair/time calibration, incremental value beyond displacement and net after entry delay.

**Additional local cases to implement.** Geometric gap contains observed trades on another bar scale; partial repair then continuation; same higher-timeframe value new identity.

**Decision or system use.** Test which observable gap properties matter and avoid treating a pattern name as proof of a market mechanism.

**Exact reviewed source clauses.** [JTR-21](SOURCE_FINDINGS_AND_CONFLICTS.md:38), [JTR-22](SOURCE_FINDINGS_AND_CONFLICTS.md:39), [JXA-24](SOURCE_FINDINGS_AND_CONFLICTS.md:123), [JXA-26](SOURCE_FINDINGS_AND_CONFLICTS.md:125), [FP8-01](SOURCE_FINDINGS_AND_CONFLICTS.md:369), [FP8-02](SOURCE_FINDINGS_AND_CONFLICTS.md:370), [FP8-03](SOURCE_FINDINGS_AND_CONFLICTS.md:371), [FP8-04](SOURCE_FINDINGS_AND_CONFLICTS.md:372), [FP8-05](SOURCE_FINDINGS_AND_CONFLICTS.md:373), [OSF-01](SOURCE_FINDINGS_AND_CONFLICTS.md:795), [OSF-02](SOURCE_FINDINGS_AND_CONFLICTS.md:796), [OSF-03](SOURCE_FINDINGS_AND_CONFLICTS.md:797), [OSF-04](SOURCE_FINDINGS_AND_CONFLICTS.md:798), [OSF-05](SOURCE_FINDINGS_AND_CONFLICTS.md:799), [OSF-06](SOURCE_FINDINGS_AND_CONFLICTS.md:800), [OSF-07](SOURCE_FINDINGS_AND_CONFLICTS.md:801), [OSF-08](SOURCE_FINDINGS_AND_CONFLICTS.md:802), [OSF-09](SOURCE_FINDINGS_AND_CONFLICTS.md:803), [OSF-10](SOURCE_FINDINGS_AND_CONFLICTS.md:804), [PIN005-04](SOURCE_FINDINGS_AND_CONFLICTS.md:831), [PIN005-05](SOURCE_FINDINGS_AND_CONFLICTS.md:832), [PIN010-01](SOURCE_FINDINGS_AND_CONFLICTS.md:841), [PIN010-02](SOURCE_FINDINGS_AND_CONFLICTS.md:842), [PIN010-03](SOURCE_FINDINGS_AND_CONFLICTS.md:843), [PIN010-04](SOURCE_FINDINGS_AND_CONFLICTS.md:844), [PIN019-01](SOURCE_FINDINGS_AND_CONFLICTS.md:887), [PIN019-02](SOURCE_FINDINGS_AND_CONFLICTS.md:888), [PIN019-03](SOURCE_FINDINGS_AND_CONFLICTS.md:889), [PIN022-01](SOURCE_FINDINGS_AND_CONFLICTS.md:894), [PIN022-02](SOURCE_FINDINGS_AND_CONFLICTS.md:895), [PIN022-03](SOURCE_FINDINGS_AND_CONFLICTS.md:896), [PIN023-01](SOURCE_FINDINGS_AND_CONFLICTS.md:897), [PIN023-02](SOURCE_FINDINGS_AND_CONFLICTS.md:898), [PIN035-01](SOURCE_FINDINGS_AND_CONFLICTS.md:920), [PIN035-02](SOURCE_FINDINGS_AND_CONFLICTS.md:921), [PIN035-03](SOURCE_FINDINGS_AND_CONFLICTS.md:922), [PIN035-04](SOURCE_FINDINGS_AND_CONFLICTS.md:923), [PIN071-01](SOURCE_FINDINGS_AND_CONFLICTS.md:1036), [PIN071-02](SOURCE_FINDINGS_AND_CONFLICTS.md:1037), [PIN071-03](SOURCE_FINDINGS_AND_CONFLICTS.md:1038), [PIN071-04](SOURCE_FINDINGS_AND_CONFLICTS.md:1039), [PIN071-05](SOURCE_FINDINGS_AND_CONFLICTS.md:1040), [PIN071-06](SOURCE_FINDINGS_AND_CONFLICTS.md:1041), [PIN071-07](SOURCE_FINDINGS_AND_CONFLICTS.md:1042), [PIN071-08](SOURCE_FINDINGS_AND_CONFLICTS.md:1043).

<a id="up-l09-gap_types"></a>
#### L09.GAP_TYPES — FVG, body gap and true imbalance

[Existing definition, target and P0–P7](experiments/L.md#l09-gap_types) remain binding.

**Specific upgrade scope.** Maintain typed spatial repair/duration fields for price FVG, body gap and measured volume imbalance separately.

**Local comparison.** Compare exact source rules, continuous repair geometry and eligible actual-footprint support, preserving each population.

**Additional cases.** Partial fill then continuation; gap on one bar scale; new higher-timeframe identity; future origin.

<a id="up-l10"></a>
### UP-L10 — Order-block and rejection-block entry regions

Parent: [L10](components/LOCATION.md); [local phases](experiments/L.md#l10); [definition refinement](SYSTEM_REFINEMENT.md#sr-l10). Upgrade role: `location`.

**Starting idea.** Choose one order-block body or wick midpoint.

**Existing improvement path.** Source sweep confirmation and all distinct body/full-range/wick, entry and stop interpretations.

**Remaining weakness.** One successful interpretation can be selected retrospectively from several geometries and fill assumptions.

**Further upgrade.** Treat source interpretations as a registered geometry/action family with explicit uncertainty, not interchangeable labels. Compare continuous sweep/reclaim quality and bounded region refinement while preserving actual confirmation price, midpoint nonfills and complete stop/expiry plans; use shared paired scenarios.

**Fair comparison.** Every faithful interpretation, simple confirmed entry, continuous quality and bounded refinement under the same action budget.

**Evidence.** Interpretation-specific fidelity, fill-adjusted value, geometry robustness, delay cost and constrained net.

**Additional local cases to implement.** Midpoint never trades again; body and full range disagree; wick caption conflicts; confirmation jumps beyond affordable stop.

**Decision or system use.** Determine which operational interpretation and entry region works under actual availability and one-mini risk.

**Exact reviewed source clauses.** [JTR-16](SOURCE_FINDINGS_AND_CONFLICTS.md:33), [JTR-17](SOURCE_FINDINGS_AND_CONFLICTS.md:34), [OSF-01](SOURCE_FINDINGS_AND_CONFLICTS.md:795), [OSF-02](SOURCE_FINDINGS_AND_CONFLICTS.md:796), [OSF-03](SOURCE_FINDINGS_AND_CONFLICTS.md:797), [OSF-04](SOURCE_FINDINGS_AND_CONFLICTS.md:798), [OSF-05](SOURCE_FINDINGS_AND_CONFLICTS.md:799), [OSF-06](SOURCE_FINDINGS_AND_CONFLICTS.md:800), [OSF-07](SOURCE_FINDINGS_AND_CONFLICTS.md:801), [OSF-08](SOURCE_FINDINGS_AND_CONFLICTS.md:802), [OSF-09](SOURCE_FINDINGS_AND_CONFLICTS.md:803), [OSF-10](SOURCE_FINDINGS_AND_CONFLICTS.md:804), [PIN010-01](SOURCE_FINDINGS_AND_CONFLICTS.md:841), [PIN010-02](SOURCE_FINDINGS_AND_CONFLICTS.md:842), [PIN010-03](SOURCE_FINDINGS_AND_CONFLICTS.md:843), [PIN010-04](SOURCE_FINDINGS_AND_CONFLICTS.md:844), [PIN022-01](SOURCE_FINDINGS_AND_CONFLICTS.md:894), [PIN022-02](SOURCE_FINDINGS_AND_CONFLICTS.md:895), [PIN022-03](SOURCE_FINDINGS_AND_CONFLICTS.md:896), [PIN023-01](SOURCE_FINDINGS_AND_CONFLICTS.md:897), [PIN023-02](SOURCE_FINDINGS_AND_CONFLICTS.md:898), [PIN032-01](SOURCE_FINDINGS_AND_CONFLICTS.md:914), [PIN032-02](SOURCE_FINDINGS_AND_CONFLICTS.md:915), [PIN032-03](SOURCE_FINDINGS_AND_CONFLICTS.md:916), [PIN035-01](SOURCE_FINDINGS_AND_CONFLICTS.md:920), [PIN035-02](SOURCE_FINDINGS_AND_CONFLICTS.md:921), [PIN035-03](SOURCE_FINDINGS_AND_CONFLICTS.md:922), [PIN035-04](SOURCE_FINDINGS_AND_CONFLICTS.md:923), [PIN038-01](SOURCE_FINDINGS_AND_CONFLICTS.md:930), [PIN038-02](SOURCE_FINDINGS_AND_CONFLICTS.md:931), [PIN051-01](SOURCE_FINDINGS_AND_CONFLICTS.md:971), [PIN051-02](SOURCE_FINDINGS_AND_CONFLICTS.md:972), [PIN071-01](SOURCE_FINDINGS_AND_CONFLICTS.md:1036), [PIN071-02](SOURCE_FINDINGS_AND_CONFLICTS.md:1037), [PIN071-03](SOURCE_FINDINGS_AND_CONFLICTS.md:1038), [PIN071-04](SOURCE_FINDINGS_AND_CONFLICTS.md:1039), [PIN071-05](SOURCE_FINDINGS_AND_CONFLICTS.md:1040), [PIN071-06](SOURCE_FINDINGS_AND_CONFLICTS.md:1041), [PIN071-07](SOURCE_FINDINGS_AND_CONFLICTS.md:1042), [PIN071-08](SOURCE_FINDINGS_AND_CONFLICTS.md:1043).

<a id="up-l10-entry_geometry"></a>
#### L10.ENTRY_GEOMETRY — Block entry and stop alternatives

[Existing definition, target and P0–P7](experiments/L.md#l10-entry_geometry) remain binding.

**Specific upgrade scope.** Treat each body/full-range/wick interpretation and entry/stop combination as a distinct complete candidate family.

**Local comparison.** Compare continuous sweep/reclaim quality and bounded region improvement only after actual confirmation and nonfill accounting.

**Additional cases.** Midpoint not revisited; interpretation conflict; stop beyond budget; event-time versus candle delay.

<a id="up-l11"></a>
### UP-L11 — VWAP and anchored-dispersion locations

Parent: [L11](components/LOCATION.md); [local phases](experiments/L.md#l11); [definition refinement](SYSTEM_REFINEMENT.md#sr-l11). Upgrade role: `location`.

**Starting idea.** Fade a VWAP band or target the moving mean.

**Existing improvement path.** Distinct VWAP acceptance/reversion/continuation roles, anchor variants and frozen/dynamic policies.

**Remaining weakness.** Multiple anchors can duplicate evidence, and band width or target movement can create artificial hit-rate gains.

**Further upgrade.** Use robust asymmetry and multi-anchor convergence geometry from M07 to model role and bounded contact regions. Compare fixed-at-cut targets with explicitly tracking targets as complete policies, using identical original opportunities and accounting for target motion separately from price travel.

**Fair comparison.** Source SD/percentage bands, robust quantile bands, multi-anchor role model and fixed/tracking target policies.

**Evidence.** Role calibration, width-matched precision, target-motion attribution, net and amendment cost.

**Additional local cases to implement.** VWAP moves through stationary price; two anchors nearly identical; outlier shifts SD; remaining time too short for reversion.

**Decision or system use.** Improve anchor/band selection and evaluate dynamic targets as management decisions with their own costs.

**Exact reviewed source clauses.** [DTM-A11](SOURCE_FINDINGS_AND_CONFLICTS.md:69), [CEX-21](SOURCE_FINDINGS_AND_CONFLICTS.md:203), [CRL-06](SOURCE_FINDINGS_AND_CONFLICTS.md:222), [VP2-05](SOURCE_FINDINGS_AND_CONFLICTS.md:302), [VW10-01](SOURCE_FINDINGS_AND_CONFLICTS.md:380), [VW10-02](SOURCE_FINDINGS_AND_CONFLICTS.md:381), [VW10-03](SOURCE_FINDINGS_AND_CONFLICTS.md:382), [VW10-04](SOURCE_FINDINGS_AND_CONFLICTS.md:383), [VW10-05](SOURCE_FINDINGS_AND_CONFLICTS.md:384), [VW10-06](SOURCE_FINDINGS_AND_CONFLICTS.md:385), [VW10-07](SOURCE_FINDINGS_AND_CONFLICTS.md:386), [OBT-04](SOURCE_FINDINGS_AND_CONFLICTS.md:753), [PIN069-01](SOURCE_FINDINGS_AND_CONFLICTS.md:1028), [PIN069-02](SOURCE_FINDINGS_AND_CONFLICTS.md:1029), [PIN069-03](SOURCE_FINDINGS_AND_CONFLICTS.md:1030), [PIN069-04](SOURCE_FINDINGS_AND_CONFLICTS.md:1031).

<a id="up-l11-dynamic_bands"></a>
#### L11.DYNAMIC_BANDS — VWAP line and target policy

[Existing definition, target and P0–P7](experiments/L.md#l11-dynamic_bands) remain binding.

**Specific upgrade scope.** Use robust band asymmetry and multi-anchor convergence while testing frozen versus tracking levels as distinct policies.

**Local comparison.** Match initial opportunity, width and actual target-motion/amendment cost; retain reversion/acceptance/continuation roles.

**Additional cases.** VWAP crosses stationary price; duplicate anchors; outlier SD; late target move.

<a id="up-l12"></a>
### UP-L12 — Opens, settlement, gaps and reference-price locations

Parent: [L12](components/LOCATION.md); [local phases](experiments/L.md#l12); [definition refinement](SYSTEM_REFINEMENT.md#sr-l12). Upgrade role: `location`.

**Starting idea.** Use an open, settlement, gap-fill line or large reported print as a level.

**Existing improvement path.** Typed reference objects, exact fractional alternatives, causal print receipt and placebo comparisons.

**Remaining weakness.** Reference importance is often assumed from its name or print size rather than incremental information relative to ordinary nearby prices.

**Further upgrade.** Use the M12 reference graph to generate relational features, publication age, agreement/disagreement and gap state. For print objects add causal size/exposure surprise, clustering and uncertainty, while comparing time/distance/size-matched ordinary-price controls; no level birth before actual availability.

**Fair comparison.** Each source reference/fraction, simple gap role, relational reference model and controlled print-role alternatives.

**Evidence.** Reference fidelity, placebo-adjusted role evidence, future path calibration and full-policy net.

**Additional local cases to implement.** Late print; roll gap; close differs from settlement; fractional body versus range level; distant source needs valid mapping.

**Decision or system use.** Identify which known references and reported events add information beyond price proximity and common round numbers.

**Exact reviewed source clauses.** [JTR-02](SOURCE_FINDINGS_AND_CONFLICTS.md:19), [DTM-A11](SOURCE_FINDINGS_AND_CONFLICTS.md:69), [JXA-10](SOURCE_FINDINGS_AND_CONFLICTS.md:109), [CRL-04](SOURCE_FINDINGS_AND_CONFLICTS.md:220), [CRL-06](SOURCE_FINDINGS_AND_CONFLICTS.md:222), [AM1-09](SOURCE_FINDINGS_AND_CONFLICTS.md:289), [MAV-08](SOURCE_FINDINGS_AND_CONFLICTS.md:512), [MAV-10](SOURCE_FINDINGS_AND_CONFLICTS.md:514), [MAV-12](SOURCE_FINDINGS_AND_CONFLICTS.md:516), [F23-02](SOURCE_FINDINGS_AND_CONFLICTS.md:668), [PIN005-01](SOURCE_FINDINGS_AND_CONFLICTS.md:828), [PIN005-02](SOURCE_FINDINGS_AND_CONFLICTS.md:829), [PIN005-03](SOURCE_FINDINGS_AND_CONFLICTS.md:830), [PIN005-04](SOURCE_FINDINGS_AND_CONFLICTS.md:831), [PIN005-05](SOURCE_FINDINGS_AND_CONFLICTS.md:832), [PIN012-02](SOURCE_FINDINGS_AND_CONFLICTS.md:853), [PIN013-01](SOURCE_FINDINGS_AND_CONFLICTS.md:857), [PIN013-02](SOURCE_FINDINGS_AND_CONFLICTS.md:858), [PIN013-03](SOURCE_FINDINGS_AND_CONFLICTS.md:859), [PIN013-04](SOURCE_FINDINGS_AND_CONFLICTS.md:860), [PIN013-05](SOURCE_FINDINGS_AND_CONFLICTS.md:861), [PIN013-06](SOURCE_FINDINGS_AND_CONFLICTS.md:862), [PIN015-01](SOURCE_FINDINGS_AND_CONFLICTS.md:865), [PIN015-02](SOURCE_FINDINGS_AND_CONFLICTS.md:866), [PIN015-03](SOURCE_FINDINGS_AND_CONFLICTS.md:867), [PIN023-02](SOURCE_FINDINGS_AND_CONFLICTS.md:898), [PIN025-01](SOURCE_FINDINGS_AND_CONFLICTS.md:899), [PIN032-01](SOURCE_FINDINGS_AND_CONFLICTS.md:914), [PIN032-02](SOURCE_FINDINGS_AND_CONFLICTS.md:915), [PIN032-03](SOURCE_FINDINGS_AND_CONFLICTS.md:916), [PIN036-01](SOURCE_FINDINGS_AND_CONFLICTS.md:925), [PIN037-01](SOURCE_FINDINGS_AND_CONFLICTS.md:927), [PIN038-01](SOURCE_FINDINGS_AND_CONFLICTS.md:930), [PIN038-02](SOURCE_FINDINGS_AND_CONFLICTS.md:931), [PIN039-01](SOURCE_FINDINGS_AND_CONFLICTS.md:933), [PIN039-02](SOURCE_FINDINGS_AND_CONFLICTS.md:934), [PIN040-01](SOURCE_FINDINGS_AND_CONFLICTS.md:935), [PIN040-02](SOURCE_FINDINGS_AND_CONFLICTS.md:936), [PIN041-01](SOURCE_FINDINGS_AND_CONFLICTS.md:938), [PIN041-02](SOURCE_FINDINGS_AND_CONFLICTS.md:939), [PIN041-03](SOURCE_FINDINGS_AND_CONFLICTS.md:940), [PIN042-01](SOURCE_FINDINGS_AND_CONFLICTS.md:942), [PIN042-02](SOURCE_FINDINGS_AND_CONFLICTS.md:943), [PIN046-01](SOURCE_FINDINGS_AND_CONFLICTS.md:955), [PIN047-01](SOURCE_FINDINGS_AND_CONFLICTS.md:956), [PIN047-02](SOURCE_FINDINGS_AND_CONFLICTS.md:957), [PIN047-03](SOURCE_FINDINGS_AND_CONFLICTS.md:958), [PIN049-01](SOURCE_FINDINGS_AND_CONFLICTS.md:964), [PIN049-02](SOURCE_FINDINGS_AND_CONFLICTS.md:965), [PIN049-03](SOURCE_FINDINGS_AND_CONFLICTS.md:966), [PIN051-01](SOURCE_FINDINGS_AND_CONFLICTS.md:971), [PIN051-02](SOURCE_FINDINGS_AND_CONFLICTS.md:972), [PIN054-01](SOURCE_FINDINGS_AND_CONFLICTS.md:978), [PIN054-02](SOURCE_FINDINGS_AND_CONFLICTS.md:979), [PIN061-01](SOURCE_FINDINGS_AND_CONFLICTS.md:997), [PIN061-02](SOURCE_FINDINGS_AND_CONFLICTS.md:998), [PIN061-03](SOURCE_FINDINGS_AND_CONFLICTS.md:999), [PIN064-01](SOURCE_FINDINGS_AND_CONFLICTS.md:1009), [PIN064-02](SOURCE_FINDINGS_AND_CONFLICTS.md:1010), [PIN066-01](SOURCE_FINDINGS_AND_CONFLICTS.md:1016), [PIN066-02](SOURCE_FINDINGS_AND_CONFLICTS.md:1017), [PIN066-03](SOURCE_FINDINGS_AND_CONFLICTS.md:1018), [PIN066-04](SOURCE_FINDINGS_AND_CONFLICTS.md:1019), [PIN073-01](SOURCE_FINDINGS_AND_CONFLICTS.md:1048), [PIN073-02](SOURCE_FINDINGS_AND_CONFLICTS.md:1049), [PIN074-01](SOURCE_FINDINGS_AND_CONFLICTS.md:1051), [PIN074-02](SOURCE_FINDINGS_AND_CONFLICTS.md:1052), [PIN076-01](SOURCE_FINDINGS_AND_CONFLICTS.md:1057), [PIN076-02](SOURCE_FINDINGS_AND_CONFLICTS.md:1058), [PIN077-01](SOURCE_FINDINGS_AND_CONFLICTS.md:1060), [PIN077-02](SOURCE_FINDINGS_AND_CONFLICTS.md:1061), [PIN080-01](SOURCE_FINDINGS_AND_CONFLICTS.md:1071), [PIN080-02](SOURCE_FINDINGS_AND_CONFLICTS.md:1072), [PIN080-03](SOURCE_FINDINGS_AND_CONFLICTS.md:1073), [PIN081-01](SOURCE_FINDINGS_AND_CONFLICTS.md:1075), [PIN081-02](SOURCE_FINDINGS_AND_CONFLICTS.md:1076), [PIN081-03](SOURCE_FINDINGS_AND_CONFLICTS.md:1077), [PIN081-04](SOURCE_FINDINGS_AND_CONFLICTS.md:1078), [PIN082-01](SOURCE_FINDINGS_AND_CONFLICTS.md:1080), [PIN082-02](SOURCE_FINDINGS_AND_CONFLICTS.md:1081), [PIN082-03](SOURCE_FINDINGS_AND_CONFLICTS.md:1082).

<a id="up-l12-print"></a>
#### L12.PRINT — Unsigned print-reference locations

[Existing definition, target and P0–P7](experiments/L.md#l12-print) remain binding.

**Specific upgrade scope.** Add causal print-size/exposure surprise, grouping and reference-graph features to the unsigned received-price object.

**Local comparison.** Compare single/cluster objects, exact width/expiry variants and time/distance/size-matched ordinary-price controls.

**Additional cases.** Late report; cancelled print; future largest ranking; distant unmappable source; group grows after birth.

<a id="up-l13"></a>
### UP-L13 — Options concentration nodes mapped to execution

Parent: [L13](components/LOCATION.md); [local phases](experiments/L.md#l13); [definition refinement](SYSTEM_REFINEMENT.md#sr-l13). Upgrade role: `location`.

**Starting idea.** Map the largest Gamma node into futures and trade its touch.

**Existing improvement path.** All supported option nodes, small-node eligibility, mappings and uncertain scenario roles.

**Remaining weakness.** One point estimate can hide scenario-dependent node identity, mapping dispersion and competition between nearby nodes.

**Further upgrade.** Generate mapped node bands across common uncertainty/scenario draws, retaining stable support and scenario-specific alternatives. Use O12/O22 lifetime/role forecasts and test whether action choice is stable across the admissible mappings; compare against size/distance-matched node controls with equal candidate density.

**Fair comparison.** Static largest/nearest, mechanically repriced, dynamic/OI-informed and scenario-aware role/location policies.

**Evidence.** Mapped geometry fidelity, contact/role calibration, useful lifetime, scenario robustness and constrained net.

**Additional local cases to implement.** Small persistent node; cash proxy touch uncertain; scenario node disappears; two mapped bands overlap; stale OI.

**Decision or system use.** Translate options information into useful receiver opportunities without making node size or one uncertain coordinate the entire decision.

**Exact reviewed source clauses.** [IMG-01](SOURCE_FINDINGS_AND_CONFLICTS.md:248), [IMG-02](SOURCE_FINDINGS_AND_CONFLICTS.md:249), [IMG-03](SOURCE_FINDINGS_AND_CONFLICTS.md:250), [IMG-04](SOURCE_FINDINGS_AND_CONFLICTS.md:251), [IMG-05](SOURCE_FINDINGS_AND_CONFLICTS.md:252), [IMG-06](SOURCE_FINDINGS_AND_CONFLICTS.md:253), [IMG-07](SOURCE_FINDINGS_AND_CONFLICTS.md:254), [DRF-U01](SOURCE_FINDINGS_AND_CONFLICTS.md:425), [DRF-U03](SOURCE_FINDINGS_AND_CONFLICTS.md:427), [DRF-U07](SOURCE_FINDINGS_AND_CONFLICTS.md:431), [DRF-A08](SOURCE_FINDINGS_AND_CONFLICTS.md:449), [DRF-A09](SOURCE_FINDINGS_AND_CONFLICTS.md:450), [DRF-A19](SOURCE_FINDINGS_AND_CONFLICTS.md:460), [DRF-A20](SOURCE_FINDINGS_AND_CONFLICTS.md:461), [GXF-01](SOURCE_FINDINGS_AND_CONFLICTS.md:485), [GXF-02](SOURCE_FINDINGS_AND_CONFLICTS.md:486), [GXF-03](SOURCE_FINDINGS_AND_CONFLICTS.md:487), [GXF-04](SOURCE_FINDINGS_AND_CONFLICTS.md:488), [GXF-05](SOURCE_FINDINGS_AND_CONFLICTS.md:489), [GXF-06](SOURCE_FINDINGS_AND_CONFLICTS.md:490), [GXF-07](SOURCE_FINDINGS_AND_CONFLICTS.md:491), [GXF-08](SOURCE_FINDINGS_AND_CONFLICTS.md:492), [GXF-09](SOURCE_FINDINGS_AND_CONFLICTS.md:493), [GXF-10](SOURCE_FINDINGS_AND_CONFLICTS.md:494), [GXF-11](SOURCE_FINDINGS_AND_CONFLICTS.md:495), [GXF-12](SOURCE_FINDINGS_AND_CONFLICTS.md:496), [GXF-13](SOURCE_FINDINGS_AND_CONFLICTS.md:497), [K10-02](SOURCE_FINDINGS_AND_CONFLICTS.md:640).

**Conversation upgrade lineage.** [DRF-U01](SOURCE_FINDINGS_AND_CONFLICTS.md:425), [DRF-U03](SOURCE_FINDINGS_AND_CONFLICTS.md:427), [DRF-U07](SOURCE_FINDINGS_AND_CONFLICTS.md:431), [DRF-A19](SOURCE_FINDINGS_AND_CONFLICTS.md:460). Read the full rows and their original conversation references; [the recheck](CONVERSATION_RECHECK.md) preserves the exact unit/exception routes.

<a id="up-l13-small_scenario_nodes"></a>
#### L13.SMALL_SCENARIO_NODES — Small and scenario-conditioned option nodes

[Existing definition, target and P0–P7](experiments/L.md#l13-small_scenario_nodes) remain binding.

**Specific upgrade scope.** Retain all supported small and scenario-dependent nodes with common mapping uncertainty and lifetime/role forecasts.

**Local comparison.** Compare static largest/nearest, dynamic and scenario-aware policies at equal density/width, including no-local-touch cohorts.

**Additional cases.** Tiny persistent node; scenario sign changes; uncertain cash touch; overlapping mappings.

<a id="up-l14"></a>
### UP-L14 — Exposure centers, bands and topology corridors

Parent: [L14](components/LOCATION.md); [local phases](experiments/L.md#l14); [definition refinement](SYSTEM_REFINEMENT.md#sr-l14). Upgrade role: `location`.

**Starting idea.** Use one exposure center and symmetric envelope.

**Existing improvement path.** Centers, bands, multimodal corridors and conditional midpoint roles.

**Remaining weakness.** A weighted mean may fall in an unsupported valley and a symmetric envelope can obscure separated or asymmetric clusters.

**Further upgrade.** Generate quantile/cluster center bands and topology corridors with explicit support between modes. Compare scalar center/envelope with multimodal distribution summaries and O12/O13 transition information; predict traversal/reversal/target roles with width/count-matched compatible corridor controls.

**Fair comparison.** Source center/envelope, ordinary VWAP, simple node midpoint, multimodal corridors and conditional roles.

**Evidence.** Support/identity stability, role/path calibration, uncertainty sensitivity and selected net.

**Additional local cases to implement.** Two separated peaks place mean in valley; corridor narrows; one wing unobserved; midpoint useful only in one path state.

**Decision or system use.** Represent the actual exposure geometry and test its actionable regions without inventing an undisclosed vendor projection.

**Exact reviewed source clauses.** [CEX-21](SOURCE_FINDINGS_AND_CONFLICTS.md:203), [IMG-01](SOURCE_FINDINGS_AND_CONFLICTS.md:248), [IMG-02](SOURCE_FINDINGS_AND_CONFLICTS.md:249), [IMG-03](SOURCE_FINDINGS_AND_CONFLICTS.md:250), [IMG-04](SOURCE_FINDINGS_AND_CONFLICTS.md:251), [IMG-05](SOURCE_FINDINGS_AND_CONFLICTS.md:252), [IMG-06](SOURCE_FINDINGS_AND_CONFLICTS.md:253), [IMG-07](SOURCE_FINDINGS_AND_CONFLICTS.md:254), [DRF-A08](SOURCE_FINDINGS_AND_CONFLICTS.md:449), [GXF-01](SOURCE_FINDINGS_AND_CONFLICTS.md:485), [GXF-02](SOURCE_FINDINGS_AND_CONFLICTS.md:486), [GXF-03](SOURCE_FINDINGS_AND_CONFLICTS.md:487), [GXF-04](SOURCE_FINDINGS_AND_CONFLICTS.md:488), [GXF-05](SOURCE_FINDINGS_AND_CONFLICTS.md:489), [GXF-06](SOURCE_FINDINGS_AND_CONFLICTS.md:490), [GXF-07](SOURCE_FINDINGS_AND_CONFLICTS.md:491), [GXF-08](SOURCE_FINDINGS_AND_CONFLICTS.md:492), [GXF-09](SOURCE_FINDINGS_AND_CONFLICTS.md:493), [GXF-10](SOURCE_FINDINGS_AND_CONFLICTS.md:494), [GXF-11](SOURCE_FINDINGS_AND_CONFLICTS.md:495), [GXF-12](SOURCE_FINDINGS_AND_CONFLICTS.md:496), [GXF-13](SOURCE_FINDINGS_AND_CONFLICTS.md:497).

**Conversation upgrade lineage.** [CEX-20](SOURCE_FINDINGS_AND_CONFLICTS.md:202). Read the full rows and their original conversation references; [the recheck](CONVERSATION_RECHECK.md) preserves the exact unit/exception routes.

<a id="up-l14-corridors"></a>
#### L14.CORRIDORS — Centers and multi-node corridors

[Existing definition, target and P0–P7](experiments/L.md#l14-corridors) remain binding.

**Specific upgrade scope.** Build quantile/multimode center bands and support-aware topology corridors, using temporal transition information.

**Local comparison.** Compare source envelopes, ordinary VWAP, simple midpoints and role-aware corridors with compatible controls.

**Additional cases.** Mean in valley; missing wing; corridor narrows; midpoint useful; undisclosed projection not replicated.

<a id="up-l15"></a>
### UP-L15 — Source-event receiver opportunities without local touch

Parent: [L15](components/LOCATION.md); [local phases](experiments/L.md#l15); [definition refinement](SYSTEM_REFINEMENT.md#sr-l15). Upgrade role: `location`.

**Starting idea.** Require a receiver-level touch before using a source reaction.

**Existing improvement path.** Source-only transmission with immediate, pullback and confirmation entry alternatives.

**Remaining weakness.** A source event's remaining information decays while the receiver moves; a fixed pullback band ignores that competition.

**Further upgrade.** Model residual receiver movement and event lifetime from the first actionable source cut, separating already realized response from future opportunity. Generate a bounded entry-time/price frontier using X05's conditional transmission and G07 waiting costs; compare immediate versus pullback versus confirmation on the same events.

**Fair comparison.** No source, local-touch-required, immediate source event and residual-lifetime-aware entry alternatives.

**Evidence.** Transmission/time calibration, remaining net value, missed pullbacks, latency sensitivity and one-mini feasibility.

**Additional local cases to implement.** Receiver already moved before source receipt; no local touch; source failure during wait; stale event reissued.

**Decision or system use.** Originate receiver trades from fresh source information when their remaining opportunity survives timing, execution and risk constraints.

**Exact reviewed source clauses.** [DTM-A06](SOURCE_FINDINGS_AND_CONFLICTS.md:64), [DTM-A18](SOURCE_FINDINGS_AND_CONFLICTS.md:76), [CEX-13](SOURCE_FINDINGS_AND_CONFLICTS.md:195), [CD1-02](SOURCE_FINDINGS_AND_CONFLICTS.md:395), [CD1-03](SOURCE_FINDINGS_AND_CONFLICTS.md:396), [DRF-U09](SOURCE_FINDINGS_AND_CONFLICTS.md:433), [DRF-A23](SOURCE_FINDINGS_AND_CONFLICTS.md:464).

**Conversation upgrade lineage.** [DTM-A18](SOURCE_FINDINGS_AND_CONFLICTS.md:76), [CEX-13](SOURCE_FINDINGS_AND_CONFLICTS.md:195), [DRF-U09](SOURCE_FINDINGS_AND_CONFLICTS.md:433). Read the full rows and their original conversation references; [the recheck](CONVERSATION_RECHECK.md) preserves the exact unit/exception routes.

<a id="up-l15-immediate_wait"></a>
#### L15.IMMEDIATE_WAIT — Receiver entry after source reaction

[Existing definition, target and P0–P7](experiments/L.md#l15-immediate_wait) remain binding.

**Specific upgrade scope.** Generate entry-time/price frontiers from the source event's remaining receiver response and lifetime.

**Local comparison.** Compare immediate, pullback and confirmation through the same G07 time/occupancy and P risk/cost contract.

**Additional cases.** Receiver already reacted; no pullback; source fails while waiting; local touch absent.

<a id="up-l16"></a>
### UP-L16 — Learned location proposal and bounded price refinement

Parent: [L16](components/LOCATION.md); [local phases](experiments/L.md#l16); [definition refinement](SYSTEM_REFINEMENT.md#sr-l16). Upgrade role: `location`.

**Starting idea.** Refine a hand-drawn level or predict a best price.

**Existing improvement path.** Bounded grids/offsets, candidate budgets and no-reach/unresolved labels.

**Remaining weakness.** A flexible generator can improve hit rate by widening regions or flooding the candidate set rather than finding better locations.

**Further upgrade.** Factor proposal learning into contact probability, conditional role/outcome and executable utility over a fixed relative-price grid. Compare sparse selected bands with fixed grid/source candidates under matched count, width and decision cuts; use uncertainty-aware offsets and cross-fitted generator/scorer closure to avoid selection leakage.

**Fair comparison.** Fixed source/grid, KDE, existing utility proposal, factored spatial model and bounded offsets.

**Evidence.** Spatial proper loss, count/width-controlled selected net, proposal stability, no-reach calibration and compute.

**Additional local cases to implement.** Generator/scorer train on same held-out labels; far unreachable peak; wide band claims success; offset creates a new unsupported object.

**Decision or system use.** Learn where useful opportunities may exist while making the source of improvement and selection cost measurable.

**Exact reviewed source clauses.** [DTM-A04](SOURCE_FINDINGS_AND_CONFLICTS.md:62), [CEX-14](SOURCE_FINDINGS_AND_CONFLICTS.md:196), [CRL-11](SOURCE_FINDINGS_AND_CONFLICTS.md:227), [CRL-19](SOURCE_FINDINGS_AND_CONFLICTS.md:235), [DRF-U03](SOURCE_FINDINGS_AND_CONFLICTS.md:427), [DRF-U08](SOURCE_FINDINGS_AND_CONFLICTS.md:432), [RVP-01](SOURCE_FINDINGS_AND_CONFLICTS.md:542), [RVP-02](SOURCE_FINDINGS_AND_CONFLICTS.md:543), [RVP-03](SOURCE_FINDINGS_AND_CONFLICTS.md:544), [RVP-04](SOURCE_FINDINGS_AND_CONFLICTS.md:545), [RVP-05](SOURCE_FINDINGS_AND_CONFLICTS.md:546), [RVP-06](SOURCE_FINDINGS_AND_CONFLICTS.md:547), [RVP-07](SOURCE_FINDINGS_AND_CONFLICTS.md:548), [RVP-08](SOURCE_FINDINGS_AND_CONFLICTS.md:549), [MVF-01](SOURCE_FINDINGS_AND_CONFLICTS.md:783), [MVF-02](SOURCE_FINDINGS_AND_CONFLICTS.md:784), [MVF-03](SOURCE_FINDINGS_AND_CONFLICTS.md:785), [MVF-04](SOURCE_FINDINGS_AND_CONFLICTS.md:786), [MVF-05](SOURCE_FINDINGS_AND_CONFLICTS.md:787), [MVF-06](SOURCE_FINDINGS_AND_CONFLICTS.md:788), [MVF-07](SOURCE_FINDINGS_AND_CONFLICTS.md:789), [PIN005-01](SOURCE_FINDINGS_AND_CONFLICTS.md:828), [PIN005-02](SOURCE_FINDINGS_AND_CONFLICTS.md:829), [PIN005-03](SOURCE_FINDINGS_AND_CONFLICTS.md:830), [PIN005-04](SOURCE_FINDINGS_AND_CONFLICTS.md:831), [PIN005-05](SOURCE_FINDINGS_AND_CONFLICTS.md:832), [PIN011-03](SOURCE_FINDINGS_AND_CONFLICTS.md:847).

**Conversation upgrade lineage.** [DTM-A04](SOURCE_FINDINGS_AND_CONFLICTS.md:62), [JCV-U05](SOURCE_FINDINGS_AND_CONFLICTS.md:158), [CEX-14](SOURCE_FINDINGS_AND_CONFLICTS.md:196), [CRL-11](SOURCE_FINDINGS_AND_CONFLICTS.md:227), [CRL-19](SOURCE_FINDINGS_AND_CONFLICTS.md:235), [DRF-U10](SOURCE_FINDINGS_AND_CONFLICTS.md:434), [DRF-A08](SOURCE_FINDINGS_AND_CONFLICTS.md:449), [DRF-A26](SOURCE_FINDINGS_AND_CONFLICTS.md:467). Read the full rows and their original conversation references; [the recheck](CONVERSATION_RECHECK.md) preserves the exact unit/exception routes.

<a id="up-l16-grid_offsets"></a>
#### L16.GRID_OFFSETS — Bounded learned location proposals

[Existing definition, target and P0–P7](experiments/L.md#l16-grid_offsets) remain binding.

**Specific upgrade scope.** Factor fixed-grid proposals into reach/contact, conditional role/outcome and executable utility with uncertainty-aware bounded offsets.

**Local comparison.** Compare fixed/source/KDE and learned proposals under count/width controls and full cross-fitted generator/scorer closure.

**Additional cases.** Unreachable peak; wider region gaming; new object disguised as offset; training-label reuse.

<a id="up-l17"></a>
### UP-L17 — Location lifecycle, retest and invalidation hazard

Parent: [L17](components/LOCATION.md); [local phases](experiments/L.md#l17); [definition refinement](SYSTEM_REFINEMENT.md#sr-l17). Upgrade role: `forecast`.

**Starting idea.** Delete a level after a touch or fixed expiry.

**Existing improvement path.** Separate factual lifecycle from forecast useful life, retest/failure and role transitions.

**Remaining weakness.** Time and visit count underdescribe cumulative pressure, refresh and gradual role change.

**Further upgrade.** Use recurrent-event survival/transition models with pressure dose, fresh evidence, time away and object lineage, sharing strength across compatible families. Compare fixed expiry with value-aware retention/retirement as a full policy, keeping observations after retirement for unbiased diagnostics where available.

**Fair comparison.** Delete-on-touch/time/count, shrunken hazard, pressure/renewal lifecycle and value-aware retention.

**Evidence.** Lifetime/transition calibration, retained opportunity value, stale-candidate cost and lineage stability.

**Additional local cases to implement.** Object split/merge; retirement hides later success; refreshed evidence; many tiny visits; unknown coverage interval.

**Decision or system use.** Keep or retire locations according to tested remaining usefulness rather than a universal touch-count heuristic.

**Exact reviewed source clauses.** [DTM-A04](SOURCE_FINDINGS_AND_CONFLICTS.md:62), [DTM-A11](SOURCE_FINDINGS_AND_CONFLICTS.md:69), [JXA-22](SOURCE_FINDINGS_AND_CONFLICTS.md:121), [JFN-10](SOURCE_FINDINGS_AND_CONFLICTS.md:144), [CRL-19](SOURCE_FINDINGS_AND_CONFLICTS.md:235), [VP2-01](SOURCE_FINDINGS_AND_CONFLICTS.md:298), [VP2-02](SOURCE_FINDINGS_AND_CONFLICTS.md:299), [VP2-03](SOURCE_FINDINGS_AND_CONFLICTS.md:300), [VP2-04](SOURCE_FINDINGS_AND_CONFLICTS.md:301), [VP2-05](SOURCE_FINDINGS_AND_CONFLICTS.md:302), [CD1-01](SOURCE_FINDINGS_AND_CONFLICTS.md:394), [CD1-02](SOURCE_FINDINGS_AND_CONFLICTS.md:395), [CD1-03](SOURCE_FINDINGS_AND_CONFLICTS.md:396), [CD1-04](SOURCE_FINDINGS_AND_CONFLICTS.md:397), [CD1-05](SOURCE_FINDINGS_AND_CONFLICTS.md:398), [DRF-U08](SOURCE_FINDINGS_AND_CONFLICTS.md:432), [MAV-01](SOURCE_FINDINGS_AND_CONFLICTS.md:505), [MAV-02](SOURCE_FINDINGS_AND_CONFLICTS.md:506), [MAV-03](SOURCE_FINDINGS_AND_CONFLICTS.md:507), [MAV-04](SOURCE_FINDINGS_AND_CONFLICTS.md:508), [MAV-05](SOURCE_FINDINGS_AND_CONFLICTS.md:509), [MAV-06](SOURCE_FINDINGS_AND_CONFLICTS.md:510), [MAV-07](SOURCE_FINDINGS_AND_CONFLICTS.md:511), [MAV-08](SOURCE_FINDINGS_AND_CONFLICTS.md:512), [MAV-09](SOURCE_FINDINGS_AND_CONFLICTS.md:513), [MAV-10](SOURCE_FINDINGS_AND_CONFLICTS.md:514), [MAV-11](SOURCE_FINDINGS_AND_CONFLICTS.md:515), [MAV-12](SOURCE_FINDINGS_AND_CONFLICTS.md:516), [MAV-13](SOURCE_FINDINGS_AND_CONFLICTS.md:517), [MAV-14](SOURCE_FINDINGS_AND_CONFLICTS.md:518), [RVP-01](SOURCE_FINDINGS_AND_CONFLICTS.md:542), [RVP-02](SOURCE_FINDINGS_AND_CONFLICTS.md:543), [RVP-03](SOURCE_FINDINGS_AND_CONFLICTS.md:544), [RVP-04](SOURCE_FINDINGS_AND_CONFLICTS.md:545), [RVP-05](SOURCE_FINDINGS_AND_CONFLICTS.md:546), [RVP-06](SOURCE_FINDINGS_AND_CONFLICTS.md:547), [RVP-07](SOURCE_FINDINGS_AND_CONFLICTS.md:548), [RVP-08](SOURCE_FINDINGS_AND_CONFLICTS.md:549), [ALM-01](SOURCE_FINDINGS_AND_CONFLICTS.md:564), [ALM-02](SOURCE_FINDINGS_AND_CONFLICTS.md:565), [ALM-03](SOURCE_FINDINGS_AND_CONFLICTS.md:566), [ALM-04](SOURCE_FINDINGS_AND_CONFLICTS.md:567), [ALM-05](SOURCE_FINDINGS_AND_CONFLICTS.md:568), [ALM-06](SOURCE_FINDINGS_AND_CONFLICTS.md:569), [RFE-01](SOURCE_FINDINGS_AND_CONFLICTS.md:602), [RFE-02](SOURCE_FINDINGS_AND_CONFLICTS.md:603), [RFE-03](SOURCE_FINDINGS_AND_CONFLICTS.md:604), [RFE-04](SOURCE_FINDINGS_AND_CONFLICTS.md:605), [RFE-05](SOURCE_FINDINGS_AND_CONFLICTS.md:606), [RFE-06](SOURCE_FINDINGS_AND_CONFLICTS.md:607), [RFE-07](SOURCE_FINDINGS_AND_CONFLICTS.md:608), [RFE-08](SOURCE_FINDINGS_AND_CONFLICTS.md:609), [RFE-09](SOURCE_FINDINGS_AND_CONFLICTS.md:610), [RFE-10](SOURCE_FINDINGS_AND_CONFLICTS.md:611), [RFE-11](SOURCE_FINDINGS_AND_CONFLICTS.md:612), [RFE-12](SOURCE_FINDINGS_AND_CONFLICTS.md:613), [RFE-13](SOURCE_FINDINGS_AND_CONFLICTS.md:614), [RFE-14](SOURCE_FINDINGS_AND_CONFLICTS.md:615), [ALS-01](SOURCE_FINDINGS_AND_CONFLICTS.md:696), [ALS-02](SOURCE_FINDINGS_AND_CONFLICTS.md:697), [ALS-03](SOURCE_FINDINGS_AND_CONFLICTS.md:698), [ALS-04](SOURCE_FINDINGS_AND_CONFLICTS.md:699), [ALS-05](SOURCE_FINDINGS_AND_CONFLICTS.md:700), [ALS-06](SOURCE_FINDINGS_AND_CONFLICTS.md:701).

**Conversation upgrade lineage.** [DTM-A11](SOURCE_FINDINGS_AND_CONFLICTS.md:69), [CRL-19](SOURCE_FINDINGS_AND_CONFLICTS.md:235), [DRF-U08](SOURCE_FINDINGS_AND_CONFLICTS.md:432). Read the full rows and their original conversation references; [the recheck](CONVERSATION_RECHECK.md) preserves the exact unit/exception routes.

<a id="up-l17-retest_hazard"></a>
#### L17.RETEST_HAZARD — Useful lifetime and retest transitions

[Existing definition, target and P0–P7](experiments/L.md#l17-retest_hazard) remain binding.

**Specific upgrade scope.** Use recurrent pressure-dose, renewal, age and lineage transitions to estimate remaining useful life and role.

**Local comparison.** Compare source expiry/touch rules with calibrated retention/retirement policy, retaining observation after retirement where possible.

**Additional cases.** Object re-ID; many tiny visits; fresh evidence; retirement hides later outcome.

<a id="up-l18"></a>
### UP-L18 — Correlated objects, provenance groups and candidate-set assembly

Parent: [L18](components/LOCATION.md); [local phases](experiments/L.md#l18); [definition refinement](SYSTEM_REFINEMENT.md#sr-l18). Upgrade role: `engineering`.

**Starting idea.** Count confluence and merge overlapping chart lines.

**Existing improvement path.** Complete candidate sets with provenance groups, distinct identities and set alternatives.

**Remaining weakness.** Geometric overlap, common data ancestry and action equivalence are different relations that one merge rule can confuse.

**Further upgrade.** Build separate geometry, evidence-lineage and executable-action relation graphs, then derive compact set features and canonical action groups. Compare deterministic relation-aware aggregation with a sparse set/graph learner under equal candidate budgets; preserve an unmerged reference and source-clause trace.

**Fair comparison.** Independent list, simple overlap merge, typed relation graphs and learned aggregation with controlled inputs.

**Evidence.** Duplicate/action invariance, retained source coverage, selected net, set stability and latency.

**Additional local cases to implement.** Same line from one raw source counted many times; distinct evidence same action; overlapping bands different expiries; graph order changes.

**Decision or system use.** Give selection compact complementary evidence and complete alternatives without losing provenance or inventing extra independent signals.

**Exact reviewed source clauses.** [DTM-A04](SOURCE_FINDINGS_AND_CONFLICTS.md:62), [DTM-A11](SOURCE_FINDINGS_AND_CONFLICTS.md:69), [CEX-14](SOURCE_FINDINGS_AND_CONFLICTS.md:196), [CRL-03](SOURCE_FINDINGS_AND_CONFLICTS.md:219), [CRL-11](SOURCE_FINDINGS_AND_CONFLICTS.md:227), [CRL-19](SOURCE_FINDINGS_AND_CONFLICTS.md:235), [AM1-10](SOURCE_FINDINGS_AND_CONFLICTS.md:290), [DRF-U10](SOURCE_FINDINGS_AND_CONFLICTS.md:434), [DRF-A22](SOURCE_FINDINGS_AND_CONFLICTS.md:463), [AUT-04](SOURCE_FINDINGS_AND_CONFLICTS.md:770), [PIN005-01](SOURCE_FINDINGS_AND_CONFLICTS.md:828), [PIN005-02](SOURCE_FINDINGS_AND_CONFLICTS.md:829), [PIN005-03](SOURCE_FINDINGS_AND_CONFLICTS.md:830), [PIN005-04](SOURCE_FINDINGS_AND_CONFLICTS.md:831), [PIN005-05](SOURCE_FINDINGS_AND_CONFLICTS.md:832).

**Conversation upgrade lineage.** [DTM-A11](SOURCE_FINDINGS_AND_CONFLICTS.md:69), [CRL-19](SOURCE_FINDINGS_AND_CONFLICTS.md:235), [DRF-A22](SOURCE_FINDINGS_AND_CONFLICTS.md:463). Read the full rows and their original conversation references; [the recheck](CONVERSATION_RECHECK.md) preserves the exact unit/exception routes.

<a id="up-l18-dependence"></a>
#### L18.DEPENDENCE — Candidate provenance and complete alternatives

[Existing definition, target and P0–P7](experiments/L.md#l18-dependence) remain binding.

**Specific upgrade scope.** Separate geometry-overlap, source-evidence and executable-action graphs before aggregation and ranking.

**Local comparison.** Compare unmerged/simple overlap with typed relations and sparse learned aggregation, preserving every original object/source.

**Additional cases.** Same evidence many indicators; same action distinct evidence; different expiry; graph permutation.

<a id="up-l19"></a>
### UP-L19 — Large-print, origin-of-move and aggression-memory locations

Parent: [L19](components/LOCATION.md); [local phases](experiments/L.md#l19); [definition refinement](SYSTEM_REFINEMENT.md#sr-l19). Upgrade role: `location`.

**Starting idea.** Trade the price of a large print or presumed trapped origin.

**Existing improvement path.** Causal effort clusters, price-only controls, matured reward and protected-origin states.

**Remaining weakness.** Cluster size alone does not identify whether a memory remains useful or whether nearby ordinary price structure explains it.

**Further upgrade.** Generate support-weighted memory regions from M11's sparse field, with novelty, pressure history and context-residual markout/lifetime estimates. Compare exact center, cluster band and neighboring price-structure controls, preserving source fixed filters and causal confirmation of protected status.

**Fair comparison.** Source print/cluster, price-only origin, raw aggression memory and residual lifetime/role model.

**Evidence.** Placebo-adjusted location information, useful lifetime, precision versus width, net and cumulative idea risk.

**Additional local cases to implement.** Trend rewards all origins; one cluster dominates; same evidence reused; protected label not yet confirmed; neighboring swing explains reaction.

**Decision or system use.** Use meaningful effort-origin memory as a tested location family with graded relevance and explicit alternatives.

**Exact reviewed source clauses.** [JXA-08](SOURCE_FINDINGS_AND_CONFLICTS.md:107), [JXA-15](SOURCE_FINDINGS_AND_CONFLICTS.md:114), [CRL-18](SOURCE_FINDINGS_AND_CONFLICTS.md:234), [RDL-01](SOURCE_FINDINGS_AND_CONFLICTS.md:550), [RDL-02](SOURCE_FINDINGS_AND_CONFLICTS.md:551), [RDL-03](SOURCE_FINDINGS_AND_CONFLICTS.md:552), [RDL-04](SOURCE_FINDINGS_AND_CONFLICTS.md:553), [RDL-05](SOURCE_FINDINGS_AND_CONFLICTS.md:554), [RDL-06](SOURCE_FINDINGS_AND_CONFLICTS.md:555), [RDL-07](SOURCE_FINDINGS_AND_CONFLICTS.md:556), [RFE-01](SOURCE_FINDINGS_AND_CONFLICTS.md:602), [RFE-02](SOURCE_FINDINGS_AND_CONFLICTS.md:603), [RFE-03](SOURCE_FINDINGS_AND_CONFLICTS.md:604), [RFE-04](SOURCE_FINDINGS_AND_CONFLICTS.md:605), [RFE-05](SOURCE_FINDINGS_AND_CONFLICTS.md:606), [RFE-06](SOURCE_FINDINGS_AND_CONFLICTS.md:607), [RFE-07](SOURCE_FINDINGS_AND_CONFLICTS.md:608), [RFE-08](SOURCE_FINDINGS_AND_CONFLICTS.md:609), [RFE-09](SOURCE_FINDINGS_AND_CONFLICTS.md:610), [RFE-10](SOURCE_FINDINGS_AND_CONFLICTS.md:611), [RFE-11](SOURCE_FINDINGS_AND_CONFLICTS.md:612), [RFE-12](SOURCE_FINDINGS_AND_CONFLICTS.md:613), [RFE-13](SOURCE_FINDINGS_AND_CONFLICTS.md:614), [RFE-14](SOURCE_FINDINGS_AND_CONFLICTS.md:615), [OFM-01](SOURCE_FINDINGS_AND_CONFLICTS.md:623), [OFM-02](SOURCE_FINDINGS_AND_CONFLICTS.md:624), [OFM-03](SOURCE_FINDINGS_AND_CONFLICTS.md:625), [OFM-04](SOURCE_FINDINGS_AND_CONFLICTS.md:626), [OFM-05](SOURCE_FINDINGS_AND_CONFLICTS.md:627), [OFM-06](SOURCE_FINDINGS_AND_CONFLICTS.md:628), [OFM-07](SOURCE_FINDINGS_AND_CONFLICTS.md:629), [OFM-08](SOURCE_FINDINGS_AND_CONFLICTS.md:630), [OFM-09](SOURCE_FINDINGS_AND_CONFLICTS.md:631), [K10-01](SOURCE_FINDINGS_AND_CONFLICTS.md:639), [K10-02](SOURCE_FINDINGS_AND_CONFLICTS.md:640), [K10-03](SOURCE_FINDINGS_AND_CONFLICTS.md:641), [K10-04](SOURCE_FINDINGS_AND_CONFLICTS.md:642), [K10-05](SOURCE_FINDINGS_AND_CONFLICTS.md:643), [K10-06](SOURCE_FINDINGS_AND_CONFLICTS.md:644), [K18-01](SOURCE_FINDINGS_AND_CONFLICTS.md:652), [K18-02](SOURCE_FINDINGS_AND_CONFLICTS.md:653), [K18-03](SOURCE_FINDINGS_AND_CONFLICTS.md:654), [K18-04](SOURCE_FINDINGS_AND_CONFLICTS.md:655), [K18-05](SOURCE_FINDINGS_AND_CONFLICTS.md:656), [K18-06](SOURCE_FINDINGS_AND_CONFLICTS.md:657), [K18-07](SOURCE_FINDINGS_AND_CONFLICTS.md:658), [K18-08](SOURCE_FINDINGS_AND_CONFLICTS.md:659), [F23-01](SOURCE_FINDINGS_AND_CONFLICTS.md:667), [F23-02](SOURCE_FINDINGS_AND_CONFLICTS.md:668), [F23-03](SOURCE_FINDINGS_AND_CONFLICTS.md:669), [F23-04](SOURCE_FINDINGS_AND_CONFLICTS.md:670), [F23-05](SOURCE_FINDINGS_AND_CONFLICTS.md:671), [F23-06](SOURCE_FINDINGS_AND_CONFLICTS.md:672), [F23-07](SOURCE_FINDINGS_AND_CONFLICTS.md:673), [CCS-01](SOURCE_FINDINGS_AND_CONFLICTS.md:681), [CCS-02](SOURCE_FINDINGS_AND_CONFLICTS.md:682), [CCS-03](SOURCE_FINDINGS_AND_CONFLICTS.md:683), [CCS-04](SOURCE_FINDINGS_AND_CONFLICTS.md:684), [CCS-05](SOURCE_FINDINGS_AND_CONFLICTS.md:685), [CCS-06](SOURCE_FINDINGS_AND_CONFLICTS.md:686), [CCS-07](SOURCE_FINDINGS_AND_CONFLICTS.md:687), [CCS-08](SOURCE_FINDINGS_AND_CONFLICTS.md:688), [OBT-01](SOURCE_FINDINGS_AND_CONFLICTS.md:750), [OBT-02](SOURCE_FINDINGS_AND_CONFLICTS.md:751), [OBT-03](SOURCE_FINDINGS_AND_CONFLICTS.md:752), [OBT-04](SOURCE_FINDINGS_AND_CONFLICTS.md:753), [OBT-05](SOURCE_FINDINGS_AND_CONFLICTS.md:754), [OBT-06](SOURCE_FINDINGS_AND_CONFLICTS.md:755), [OBT-07](SOURCE_FINDINGS_AND_CONFLICTS.md:756), [OBT-08](SOURCE_FINDINGS_AND_CONFLICTS.md:757), [OBT-09](SOURCE_FINDINGS_AND_CONFLICTS.md:758), [OBT-10](SOURCE_FINDINGS_AND_CONFLICTS.md:759), [MVF-01](SOURCE_FINDINGS_AND_CONFLICTS.md:783), [MVF-02](SOURCE_FINDINGS_AND_CONFLICTS.md:784), [MVF-03](SOURCE_FINDINGS_AND_CONFLICTS.md:785), [MVF-04](SOURCE_FINDINGS_AND_CONFLICTS.md:786), [MVF-05](SOURCE_FINDINGS_AND_CONFLICTS.md:787), [MVF-06](SOURCE_FINDINGS_AND_CONFLICTS.md:788), [MVF-07](SOURCE_FINDINGS_AND_CONFLICTS.md:789).

**Conversation upgrade lineage.** [JCV-A07](SOURCE_FINDINGS_AND_CONFLICTS.md:166), [CRL-07](SOURCE_FINDINGS_AND_CONFLICTS.md:223). Read the full rows and their original conversation references; [the recheck](CONVERSATION_RECHECK.md) preserves the exact unit/exception routes.

<a id="up-l19-origin_memory"></a>
#### L19.ORIGIN_MEMORY — Effort-origin and protected-print objects

[Existing definition, target and P0–P7](experiments/L.md#l19-origin_memory) remain binding.

**Specific upgrade scope.** Use sparse aggression-memory support, novelty and context-residual reward/lifetime to form origin regions.

**Local comparison.** Compare exact center, support band and nearby price-only controls with causal protection and cumulative idea risk.

**Additional cases.** Trend rewards all origins; reused prints; markout pending; neighboring swing explains reaction.

<a id="family-g"></a>
## Mixtures and selection

<a id="up-g01"></a>
### UP-G01 — Target-specific Context and path mixtures

Parent: [G01](components/GATES_AND_SELECTION.md); [local phases](experiments/G.md#g01); [definition refinement](SYSTEM_REFINEMENT.md#sr-g01). Upgrade role: `forecast`.

**Starting idea.** Choose one Context signal or count agreeing indicators.

**Existing improvement path.** Target-specific distributions, regularized mixtures and feature-diverse experts.

**Remaining weakness.** Several nominally different experts may repeat the same evidence, while a useful small residual signal is overwhelmed by a flexible gate.

**Further upgrade.** Add hierarchical stacking by measurement lineage, with within-family and between-family shrinkage, and a residual-correction challenger to a strong simple forecast. Train every gate/correction on chronological out-of-fold predictions; preserve valid distribution support and compare conditional versus global weights.

**Fair comparison.** Best single, uniform/static blend, existing flat gate, hierarchical stack and regularized residual correction on identical targets and eligible cuts.

**Evidence.** Proper loss, calibration, residual diversity, weight stability, incremental constrained net and inference cost.

**Additional local cases to implement.** Duplicated expert; common input outage; one useful weak expert; new missing pattern; all experts share bias.

**Decision or system use.** Obtain useful complementary information without treating correlated variants as independent votes.

**Exact reviewed source clauses.** [DTM-A01](SOURCE_FINDINGS_AND_CONFLICTS.md:59), [DTM-A14](SOURCE_FINDINGS_AND_CONFLICTS.md:72), [JFN-05](SOURCE_FINDINGS_AND_CONFLICTS.md:139), [JCV-U05](SOURCE_FINDINGS_AND_CONFLICTS.md:158), [CEX-01](SOURCE_FINDINGS_AND_CONFLICTS.md:183), [CEX-04](SOURCE_FINDINGS_AND_CONFLICTS.md:186), [CRL-17](SOURCE_FINDINGS_AND_CONFLICTS.md:233), [DRF-U12](SOURCE_FINDINGS_AND_CONFLICTS.md:436), [DRF-A20](SOURCE_FINDINGS_AND_CONFLICTS.md:461), [DRF-A21](SOURCE_FINDINGS_AND_CONFLICTS.md:462), [DRF-A29](SOURCE_FINDINGS_AND_CONFLICTS.md:470), [MAT-05](SOURCE_FINDINGS_AND_CONFLICTS.md:530), [MVF-01](SOURCE_FINDINGS_AND_CONFLICTS.md:783), [MVF-02](SOURCE_FINDINGS_AND_CONFLICTS.md:784), [MVF-03](SOURCE_FINDINGS_AND_CONFLICTS.md:785), [MVF-04](SOURCE_FINDINGS_AND_CONFLICTS.md:786), [MVF-05](SOURCE_FINDINGS_AND_CONFLICTS.md:787), [MVF-06](SOURCE_FINDINGS_AND_CONFLICTS.md:788), [MVF-07](SOURCE_FINDINGS_AND_CONFLICTS.md:789), [PIN008-01](SOURCE_FINDINGS_AND_CONFLICTS.md:824), [PIN009-01](SOURCE_FINDINGS_AND_CONFLICTS.md:825), [PIN009-02](SOURCE_FINDINGS_AND_CONFLICTS.md:826), [PIN011-01](SOURCE_FINDINGS_AND_CONFLICTS.md:845), [PIN011-02](SOURCE_FINDINGS_AND_CONFLICTS.md:846), [PIN011-03](SOURCE_FINDINGS_AND_CONFLICTS.md:847), [PIN011-04](SOURCE_FINDINGS_AND_CONFLICTS.md:848), [PIN011-05](SOURCE_FINDINGS_AND_CONFLICTS.md:849), [PIN011-06](SOURCE_FINDINGS_AND_CONFLICTS.md:850), [PIN011-07](SOURCE_FINDINGS_AND_CONFLICTS.md:851), [PIN017-01](SOURCE_FINDINGS_AND_CONFLICTS.md:872), [PIN017-02](SOURCE_FINDINGS_AND_CONFLICTS.md:873), [PIN017-03](SOURCE_FINDINGS_AND_CONFLICTS.md:874), [PIN017-04](SOURCE_FINDINGS_AND_CONFLICTS.md:875), [PIN020-01](SOURCE_FINDINGS_AND_CONFLICTS.md:890), [PIN020-02](SOURCE_FINDINGS_AND_CONFLICTS.md:891), [PIN033-01](SOURCE_FINDINGS_AND_CONFLICTS.md:917), [PIN033-02](SOURCE_FINDINGS_AND_CONFLICTS.md:918), [PIN034-01](SOURCE_FINDINGS_AND_CONFLICTS.md:919), [PIN035-03](SOURCE_FINDINGS_AND_CONFLICTS.md:922), [PIN050-01](SOURCE_FINDINGS_AND_CONFLICTS.md:968), [PIN050-02](SOURCE_FINDINGS_AND_CONFLICTS.md:969), [PIN050-03](SOURCE_FINDINGS_AND_CONFLICTS.md:970), [PIN072-01](SOURCE_FINDINGS_AND_CONFLICTS.md:1045), [PIN072-02](SOURCE_FINDINGS_AND_CONFLICTS.md:1046), [PIN079-01](SOURCE_FINDINGS_AND_CONFLICTS.md:1066), [PIN079-02](SOURCE_FINDINGS_AND_CONFLICTS.md:1067), [PIN079-03](SOURCE_FINDINGS_AND_CONFLICTS.md:1068), [PIN079-04](SOURCE_FINDINGS_AND_CONFLICTS.md:1069).

**Conversation upgrade lineage.** [DTM-A01](SOURCE_FINDINGS_AND_CONFLICTS.md:59), [DTM-A15](SOURCE_FINDINGS_AND_CONFLICTS.md:73), [JCV-U05](SOURCE_FINDINGS_AND_CONFLICTS.md:158), [JCV-A08](SOURCE_FINDINGS_AND_CONFLICTS.md:167), [JCV-A09](SOURCE_FINDINGS_AND_CONFLICTS.md:168), [JCV-A10](SOURCE_FINDINGS_AND_CONFLICTS.md:169), [CEX-01](SOURCE_FINDINGS_AND_CONFLICTS.md:183), [CEX-05](SOURCE_FINDINGS_AND_CONFLICTS.md:187), [CRL-08](SOURCE_FINDINGS_AND_CONFLICTS.md:224), [CRL-17](SOURCE_FINDINGS_AND_CONFLICTS.md:233), [DRF-U07](SOURCE_FINDINGS_AND_CONFLICTS.md:431), [DRF-U12](SOURCE_FINDINGS_AND_CONFLICTS.md:436), [DRF-A28](SOURCE_FINDINGS_AND_CONFLICTS.md:469), [DRF-A29](SOURCE_FINDINGS_AND_CONFLICTS.md:470). Read the full rows and their original conversation references; [the recheck](CONVERSATION_RECHECK.md) preserves the exact unit/exception routes.

<a id="up-g01-diversity"></a>
#### G01.DIVERSITY — Specialist diversity and shared representations

[Existing definition, target and P0–P7](experiments/G.md#g01-diversity) remain binding.

**Specific upgrade scope.** Compare hierarchical lineage-aware stacking and residual correction against flat mixtures, preserving exact shared target capabilities.

**Local comparison.** Separate expert information diversity from random-seed/model duplication; assess proper loss, stability and incremental net.

**Additional cases.** Duplicate experts; common bias; useful weak residual; missing family.

<a id="up-g02"></a>
### UP-G02 — Rich volatility and excursion ensembles

Parent: [G02](components/GATES_AND_SELECTION.md); [local phases](experiments/G.md#g02); [definition refinement](SYSTEM_REFINEMENT.md#sr-g02). Upgrade role: `forecast`.

**Starting idea.** Convert a volatility number into expected movement.

**Existing improvement path.** Separate variance and joint path mixtures with diverse physical/implied specialists.

**Remaining weakness.** A stack may overweight many variants of one estimator and leave inconsistent horizon or tail behavior.

**Further upgrade.** Group primitive forecasts by information/estimand lineage and fit coherent horizon distributions within each valid target family. Compare pooled variance curves plus a separately learned conditional path law against direct path ensembles; share state representations only where target meaning is preserved.

**Fair comparison.** Single multiscale baseline, uniform blend, flat target-specific stack and hierarchy with explicit horizon/path consistency.

**Evidence.** Proper target loss by horizon, tail coverage, first-passage calibration where supported, downstream location/value improvement and cost.

**Additional local cases to implement.** Many near-identical lags; discontinuity at session boundary; correct RV with wrong return tail; shrinking remaining horizon.

**Decision or system use.** A richer ensemble supplies the specific variance, excursion or ordering information its consumers need; no unsupported conversion between them.

**Exact reviewed source clauses.** [DTM-A03](SOURCE_FINDINGS_AND_CONFLICTS.md:61), [JCV-A05](SOURCE_FINDINGS_AND_CONFLICTS.md:164), [CEX-06](SOURCE_FINDINGS_AND_CONFLICTS.md:188), [VX4-01](SOURCE_FINDINGS_AND_CONFLICTS.md:324), [VX4-02](SOURCE_FINDINGS_AND_CONFLICTS.md:325), [VX4-03](SOURCE_FINDINGS_AND_CONFLICTS.md:326), [VX4-04](SOURCE_FINDINGS_AND_CONFLICTS.md:327), [VX4-05](SOURCE_FINDINGS_AND_CONFLICTS.md:328), [VX4-06](SOURCE_FINDINGS_AND_CONFLICTS.md:329), [VX4-07](SOURCE_FINDINGS_AND_CONFLICTS.md:330), [VX4-08](SOURCE_FINDINGS_AND_CONFLICTS.md:331), [VX4-09](SOURCE_FINDINGS_AND_CONFLICTS.md:332), [DRF-A12](SOURCE_FINDINGS_AND_CONFLICTS.md:453), [PIN018-01](SOURCE_FINDINGS_AND_CONFLICTS.md:876), [PIN018-02](SOURCE_FINDINGS_AND_CONFLICTS.md:877).

**Conversation upgrade lineage.** [CEX-06](SOURCE_FINDINGS_AND_CONFLICTS.md:188). Read the full rows and their original conversation references; [the recheck](CONVERSATION_RECHECK.md) preserves the exact unit/exception routes.

<a id="up-g02-multitarget"></a>
#### G02.MULTITARGET — Variance, tail and excursion ensemble roles

[Existing definition, target and P0–P7](experiments/G.md#g02-multitarget) remain binding.

**Specific upgrade scope.** Build coherent within-target horizon ensembles and separate variance from U/D/order/time path mixtures.

**Local comparison.** Compare single/uniform/flat/hierarchical stacks on each target, with cross-target consistency only where mathematically declared.

**Additional cases.** Good RV but wrong tail; mixture quantiles; many correlated estimator lags; shortening horizon.

<a id="up-g03"></a>
### UP-G03 — Forecast calibration and uncertainty service

Parent: [G03](components/GATES_AND_SELECTION.md); [local phases](experiments/G.md#g03); [definition refinement](SYSTEM_REFINEMENT.md#sr-g03). Upgrade role: `forecast`.

**Starting idea.** Interpret fitted probabilities or quantiles literally.

**Existing improvement path.** Chronological calibration, conditional diagnostics and uncertainty with coherence checks.

**Remaining weakness.** Sparse local cells can overfit, while aggregate calibration conceals selection and horizon failures.

**Further upgrade.** Compare hierarchical shrinkage of conditional calibration parameters across asset/session/coverage/horizon with pooled calibration. Fit coherent target families jointly when feasible and evaluate calibration after the entire projection, gating and selection chain, including best-action versus flat margins.

**Fair comparison.** Identity, pooled logistic/temperature, isotonic and hierarchical conditional calibration using identical chronological fitting closures.

**Evidence.** Proper loss, reliability by supported group, interval coverage, selective risk, effective date support and decision stability.

**Additional local cases to implement.** Rare coverage cell; conditional reversal hidden by overall reliability; calibration projection changes rank; outer-test reuse.

**Decision or system use.** Supply calibrated uncertainty at the actual decision point, retaining pooled fallbacks when local evidence is insufficient.

**Exact reviewed source clauses.** [JTR-19](SOURCE_FINDINGS_AND_CONFLICTS.md:36), [JXA-07](SOURCE_FINDINGS_AND_CONFLICTS.md:106), [CRL-17](SOURCE_FINDINGS_AND_CONFLICTS.md:233), [DRF-U08](SOURCE_FINDINGS_AND_CONFLICTS.md:432), [DRF-A21](SOURCE_FINDINGS_AND_CONFLICTS.md:462), [PIN006-01](SOURCE_FINDINGS_AND_CONFLICTS.md:833), [PIN006-02](SOURCE_FINDINGS_AND_CONFLICTS.md:834), [PIN006-03](SOURCE_FINDINGS_AND_CONFLICTS.md:835), [PIN007-01](SOURCE_FINDINGS_AND_CONFLICTS.md:836), [PIN007-02](SOURCE_FINDINGS_AND_CONFLICTS.md:837), [PIN007-03](SOURCE_FINDINGS_AND_CONFLICTS.md:838), [PIN007-04](SOURCE_FINDINGS_AND_CONFLICTS.md:839), [PIN007-05](SOURCE_FINDINGS_AND_CONFLICTS.md:840), [PIN013-01](SOURCE_FINDINGS_AND_CONFLICTS.md:857), [PIN013-02](SOURCE_FINDINGS_AND_CONFLICTS.md:858), [PIN013-03](SOURCE_FINDINGS_AND_CONFLICTS.md:859), [PIN013-04](SOURCE_FINDINGS_AND_CONFLICTS.md:860), [PIN013-05](SOURCE_FINDINGS_AND_CONFLICTS.md:861), [PIN013-06](SOURCE_FINDINGS_AND_CONFLICTS.md:862), [PIN014-01](SOURCE_FINDINGS_AND_CONFLICTS.md:863), [PIN014-02](SOURCE_FINDINGS_AND_CONFLICTS.md:864), [PIN015-01](SOURCE_FINDINGS_AND_CONFLICTS.md:865), [PIN015-02](SOURCE_FINDINGS_AND_CONFLICTS.md:866), [PIN015-03](SOURCE_FINDINGS_AND_CONFLICTS.md:867), [PIN016-01](SOURCE_FINDINGS_AND_CONFLICTS.md:868), [PIN016-02](SOURCE_FINDINGS_AND_CONFLICTS.md:869), [PIN016-03](SOURCE_FINDINGS_AND_CONFLICTS.md:870), [PIN016-04](SOURCE_FINDINGS_AND_CONFLICTS.md:871), [PIN025-01](SOURCE_FINDINGS_AND_CONFLICTS.md:899), [PIN026-01](SOURCE_FINDINGS_AND_CONFLICTS.md:900), [PIN026-02](SOURCE_FINDINGS_AND_CONFLICTS.md:901), [PIN027-01](SOURCE_FINDINGS_AND_CONFLICTS.md:902), [PIN027-02](SOURCE_FINDINGS_AND_CONFLICTS.md:903), [PIN028-01](SOURCE_FINDINGS_AND_CONFLICTS.md:904), [PIN028-02](SOURCE_FINDINGS_AND_CONFLICTS.md:905), [PIN028-03](SOURCE_FINDINGS_AND_CONFLICTS.md:906), [PIN029-01](SOURCE_FINDINGS_AND_CONFLICTS.md:907), [PIN029-02](SOURCE_FINDINGS_AND_CONFLICTS.md:908), [PIN029-03](SOURCE_FINDINGS_AND_CONFLICTS.md:909), [PIN030-01](SOURCE_FINDINGS_AND_CONFLICTS.md:910), [PIN030-02](SOURCE_FINDINGS_AND_CONFLICTS.md:911), [PIN030-03](SOURCE_FINDINGS_AND_CONFLICTS.md:912), [PIN031-01](SOURCE_FINDINGS_AND_CONFLICTS.md:913), [PIN036-01](SOURCE_FINDINGS_AND_CONFLICTS.md:925), [PIN036-02](SOURCE_FINDINGS_AND_CONFLICTS.md:926), [PIN037-01](SOURCE_FINDINGS_AND_CONFLICTS.md:927), [PIN037-02](SOURCE_FINDINGS_AND_CONFLICTS.md:928), [PIN039-01](SOURCE_FINDINGS_AND_CONFLICTS.md:933), [PIN039-02](SOURCE_FINDINGS_AND_CONFLICTS.md:934), [PIN040-01](SOURCE_FINDINGS_AND_CONFLICTS.md:935), [PIN040-02](SOURCE_FINDINGS_AND_CONFLICTS.md:936), [PIN041-01](SOURCE_FINDINGS_AND_CONFLICTS.md:938), [PIN041-02](SOURCE_FINDINGS_AND_CONFLICTS.md:939), [PIN041-03](SOURCE_FINDINGS_AND_CONFLICTS.md:940), [PIN042-01](SOURCE_FINDINGS_AND_CONFLICTS.md:942), [PIN042-02](SOURCE_FINDINGS_AND_CONFLICTS.md:943), [PIN043-01](SOURCE_FINDINGS_AND_CONFLICTS.md:944), [PIN045-01](SOURCE_FINDINGS_AND_CONFLICTS.md:948), [PIN045-02](SOURCE_FINDINGS_AND_CONFLICTS.md:949), [PIN045-03](SOURCE_FINDINGS_AND_CONFLICTS.md:950), [PIN045-04](SOURCE_FINDINGS_AND_CONFLICTS.md:951), [PIN045-05](SOURCE_FINDINGS_AND_CONFLICTS.md:952), [PIN045-06](SOURCE_FINDINGS_AND_CONFLICTS.md:953), [PIN046-01](SOURCE_FINDINGS_AND_CONFLICTS.md:955), [PIN047-01](SOURCE_FINDINGS_AND_CONFLICTS.md:956), [PIN047-02](SOURCE_FINDINGS_AND_CONFLICTS.md:957), [PIN047-03](SOURCE_FINDINGS_AND_CONFLICTS.md:958), [PIN048-01](SOURCE_FINDINGS_AND_CONFLICTS.md:960), [PIN048-02](SOURCE_FINDINGS_AND_CONFLICTS.md:961), [PIN048-03](SOURCE_FINDINGS_AND_CONFLICTS.md:962), [PIN049-01](SOURCE_FINDINGS_AND_CONFLICTS.md:964), [PIN049-02](SOURCE_FINDINGS_AND_CONFLICTS.md:965), [PIN049-03](SOURCE_FINDINGS_AND_CONFLICTS.md:966), [PIN052-01](SOURCE_FINDINGS_AND_CONFLICTS.md:974), [PIN052-02](SOURCE_FINDINGS_AND_CONFLICTS.md:975), [PIN052-03](SOURCE_FINDINGS_AND_CONFLICTS.md:976), [PIN054-01](SOURCE_FINDINGS_AND_CONFLICTS.md:978), [PIN054-02](SOURCE_FINDINGS_AND_CONFLICTS.md:979), [PIN055-01](SOURCE_FINDINGS_AND_CONFLICTS.md:980), [PIN055-02](SOURCE_FINDINGS_AND_CONFLICTS.md:981), [PIN056-01](SOURCE_FINDINGS_AND_CONFLICTS.md:983), [PIN056-02](SOURCE_FINDINGS_AND_CONFLICTS.md:984), [PIN057-01](SOURCE_FINDINGS_AND_CONFLICTS.md:985), [PIN057-02](SOURCE_FINDINGS_AND_CONFLICTS.md:986), [PIN057-03](SOURCE_FINDINGS_AND_CONFLICTS.md:987), [PIN058-01](SOURCE_FINDINGS_AND_CONFLICTS.md:989), [PIN059-01](SOURCE_FINDINGS_AND_CONFLICTS.md:990), [PIN059-02](SOURCE_FINDINGS_AND_CONFLICTS.md:991), [PIN060-01](SOURCE_FINDINGS_AND_CONFLICTS.md:993), [PIN060-02](SOURCE_FINDINGS_AND_CONFLICTS.md:994), [PIN060-03](SOURCE_FINDINGS_AND_CONFLICTS.md:995), [PIN061-01](SOURCE_FINDINGS_AND_CONFLICTS.md:997), [PIN061-02](SOURCE_FINDINGS_AND_CONFLICTS.md:998), [PIN061-03](SOURCE_FINDINGS_AND_CONFLICTS.md:999), [PIN062-01](SOURCE_FINDINGS_AND_CONFLICTS.md:1001), [PIN062-02](SOURCE_FINDINGS_AND_CONFLICTS.md:1002), [PIN062-03](SOURCE_FINDINGS_AND_CONFLICTS.md:1003), [PIN063-01](SOURCE_FINDINGS_AND_CONFLICTS.md:1005), [PIN063-02](SOURCE_FINDINGS_AND_CONFLICTS.md:1006), [PIN063-03](SOURCE_FINDINGS_AND_CONFLICTS.md:1007), [PIN064-01](SOURCE_FINDINGS_AND_CONFLICTS.md:1009), [PIN064-02](SOURCE_FINDINGS_AND_CONFLICTS.md:1010), [PIN065-01](SOURCE_FINDINGS_AND_CONFLICTS.md:1012), [PIN065-02](SOURCE_FINDINGS_AND_CONFLICTS.md:1013), [PIN065-03](SOURCE_FINDINGS_AND_CONFLICTS.md:1014), [PIN067-01](SOURCE_FINDINGS_AND_CONFLICTS.md:1021), [PIN067-02](SOURCE_FINDINGS_AND_CONFLICTS.md:1022), [PIN068-01](SOURCE_FINDINGS_AND_CONFLICTS.md:1024), [PIN068-02](SOURCE_FINDINGS_AND_CONFLICTS.md:1025), [PIN068-03](SOURCE_FINDINGS_AND_CONFLICTS.md:1026), [PIN069-01](SOURCE_FINDINGS_AND_CONFLICTS.md:1028), [PIN069-02](SOURCE_FINDINGS_AND_CONFLICTS.md:1029), [PIN069-03](SOURCE_FINDINGS_AND_CONFLICTS.md:1030), [PIN069-04](SOURCE_FINDINGS_AND_CONFLICTS.md:1031), [PIN070-01](SOURCE_FINDINGS_AND_CONFLICTS.md:1033), [PIN070-02](SOURCE_FINDINGS_AND_CONFLICTS.md:1034), [PIN073-01](SOURCE_FINDINGS_AND_CONFLICTS.md:1048), [PIN073-02](SOURCE_FINDINGS_AND_CONFLICTS.md:1049), [PIN074-01](SOURCE_FINDINGS_AND_CONFLICTS.md:1051), [PIN074-02](SOURCE_FINDINGS_AND_CONFLICTS.md:1052), [PIN076-01](SOURCE_FINDINGS_AND_CONFLICTS.md:1057), [PIN076-02](SOURCE_FINDINGS_AND_CONFLICTS.md:1058), [PIN078-01](SOURCE_FINDINGS_AND_CONFLICTS.md:1063), [PIN078-02](SOURCE_FINDINGS_AND_CONFLICTS.md:1064), [PIN080-01](SOURCE_FINDINGS_AND_CONFLICTS.md:1071), [PIN080-02](SOURCE_FINDINGS_AND_CONFLICTS.md:1072), [PIN080-03](SOURCE_FINDINGS_AND_CONFLICTS.md:1073), [PIN081-01](SOURCE_FINDINGS_AND_CONFLICTS.md:1075), [PIN081-02](SOURCE_FINDINGS_AND_CONFLICTS.md:1076), [PIN081-03](SOURCE_FINDINGS_AND_CONFLICTS.md:1077), [PIN081-04](SOURCE_FINDINGS_AND_CONFLICTS.md:1078), [PIN082-01](SOURCE_FINDINGS_AND_CONFLICTS.md:1080), [PIN082-02](SOURCE_FINDINGS_AND_CONFLICTS.md:1081), [PIN082-03](SOURCE_FINDINGS_AND_CONFLICTS.md:1082), [PIN083-01](SOURCE_FINDINGS_AND_CONFLICTS.md:1084), [PIN083-02](SOURCE_FINDINGS_AND_CONFLICTS.md:1085).

**Conversation upgrade lineage.** [CRL-17](SOURCE_FINDINGS_AND_CONFLICTS.md:233), [DRF-U08](SOURCE_FINDINGS_AND_CONFLICTS.md:432), [DRF-A07](SOURCE_FINDINGS_AND_CONFLICTS.md:448), [DRF-A21](SOURCE_FINDINGS_AND_CONFLICTS.md:462). Read the full rows and their original conversation references; [the recheck](CONVERSATION_RECHECK.md) preserves the exact unit/exception routes.

<a id="up-g03-conditional"></a>
#### G03.CONDITIONAL — Calibration and uncertainty diagnostics

[Existing definition, target and P0–P7](experiments/G.md#g03-conditional) remain binding.

**Specific upgrade scope.** Add partial pooling of supported calibration cells and evaluate the complete post-projection/gating/selection chain.

**Local comparison.** Compare pooled calibration with hierarchical conditional alternatives by proper score, coverage and action stability.

**Additional cases.** Rare cell; aggregate calibration hides local failure; calibrator changes rank; missing-pattern shift.

<a id="up-g04"></a>
### UP-G04 — Level reach and first-passage expert

Parent: [G04](components/GATES_AND_SELECTION.md); [local phases](experiments/G.md#g04); [definition refinement](SYSTEM_REFINEMENT.md#sr-g04). Upgrade role: `forecast`.

**Starting idea.** Reach depends on distance divided by volatility.

**Existing improvement path.** Competing first-contact hazards and independently validated path-model alternatives.

**Remaining weakness.** Marginal reach estimates can miss topology, co-contact, changing travel speed and uncertainty about arrival conditions.

**Further upgrade.** Build a common landmark event model over frozen candidate regions, with disjoint first-contact/co-contact/gap/no-contact outcomes, arrival time and arrival-state distribution. Compare a sparse discrete hazard model with a shared path-scenario law that also generates these labels; include state-dependent activity clocks without changing wall-clock cutoffs.

**Fair comparison.** Distance baseline, independent hazards, joint landmark hazards and validated common path scenarios under identical frozen objects.

**Evidence.** Joint log/proper score, contact/time calibration, gap/co-contact error, pre-touch value and runtime.

**Additional local cases to implement.** Overlapping bands; gap jumps nearer band; removed optional candidate; slow approach followed by burst; censored boundary.

**Decision or system use.** Give G05/G07 a coherent distribution of where, when and in what observable state price may arrive.

**Exact reviewed source clauses.** [DTM-A03](SOURCE_FINDINGS_AND_CONFLICTS.md:61), [JXA-18](SOURCE_FINDINGS_AND_CONFLICTS.md:117), [DRF-A09](SOURCE_FINDINGS_AND_CONFLICTS.md:450), [DRF-A10](SOURCE_FINDINGS_AND_CONFLICTS.md:451), [MAV-03](SOURCE_FINDINGS_AND_CONFLICTS.md:507), [MAV-08](SOURCE_FINDINGS_AND_CONFLICTS.md:512), [MAT-01](SOURCE_FINDINGS_AND_CONFLICTS.md:526), [MAT-02](SOURCE_FINDINGS_AND_CONFLICTS.md:527), [MAT-03](SOURCE_FINDINGS_AND_CONFLICTS.md:528), [MAT-04](SOURCE_FINDINGS_AND_CONFLICTS.md:529), [MAT-05](SOURCE_FINDINGS_AND_CONFLICTS.md:530), [MAT-06](SOURCE_FINDINGS_AND_CONFLICTS.md:531), [MAT-07](SOURCE_FINDINGS_AND_CONFLICTS.md:532), [MAT-08](SOURCE_FINDINGS_AND_CONFLICTS.md:533), [MAT-09](SOURCE_FINDINGS_AND_CONFLICTS.md:534).

**Conversation upgrade lineage.** [DTM-A03](SOURCE_FINDINGS_AND_CONFLICTS.md:61), [DRF-A05](SOURCE_FINDINGS_AND_CONFLICTS.md:446), [DRF-A22](SOURCE_FINDINGS_AND_CONFLICTS.md:463). Read the full rows and their original conversation references; [the recheck](CONVERSATION_RECHECK.md) preserves the exact unit/exception routes.

<a id="up-g04-order"></a>
#### G04.ORDER — Reach, arrival and ordered first passage

[Existing definition, target and P0–P7](experiments/G.md#g04-order) remain binding.

**Specific upgrade scope.** Use joint landmark contact/co-contact/gap/time/arrival-state outcomes across the frozen candidate set.

**Local comparison.** Compare distance and independent hazards with coherent competing-event/path models, preserving nonexclusive geometry semantics.

**Additional cases.** Overlapping bands; gap skips nearer band; same-time contact; pre-touch arrival features unknown.

<a id="up-g05"></a>
### UP-G05 — Conditional departure, continuation and runner-quality experts

Parent: [G05](components/GATES_AND_SELECTION.md); [local phases](experiments/G.md#g05); [definition refinement](SYSTEM_REFINEMENT.md#sr-g05). Upgrade role: `forecast`.

**Starting idea.** Score a level by bounce or target-hit rate.

**Existing improvement path.** Distinct pre-touch and post-touch ordered departure, continuation and runner models.

**Remaining weakness.** A binary success label loses rebound-then-failure, traversal and duration that alter exit value.

**Further upgrade.** Use a compact multi-state landmark model for contact, initial departure, retrace, renewed departure, traversal and expiration; define barriers and states before outcomes. Compare structured transition hazards against direct joint outcome/time heads and simple empirical episode tables; pre-touch forecasts integrate possible arrival states.

**Fair comparison.** Existing hit/runner heads versus structured episode model and joint direct heads, at matched cuts and information budgets.

**Evidence.** Ordered path proper loss, duration/return calibration, stop/exit decision value and uncertainty by independent episode/date.

**Additional local cases to implement.** Fast bounce then failure; delayed runner; re-entry into band; simultaneous barriers; no resolved outcome by cutoff.

**Decision or system use.** Separate temporary reaction from sustainable opportunity and provide distributions usable by full-position management.

**Exact reviewed source clauses.** [JTR-12](SOURCE_FINDINGS_AND_CONFLICTS.md:29), [DTM-A03](SOURCE_FINDINGS_AND_CONFLICTS.md:61), [DTM-A15](SOURCE_FINDINGS_AND_CONFLICTS.md:73), [JXA-18](SOURCE_FINDINGS_AND_CONFLICTS.md:117), [JFN-06](SOURCE_FINDINGS_AND_CONFLICTS.md:140), [DRF-U01](SOURCE_FINDINGS_AND_CONFLICTS.md:425), [DRF-A05](SOURCE_FINDINGS_AND_CONFLICTS.md:446), [DRF-A09](SOURCE_FINDINGS_AND_CONFLICTS.md:450), [DRF-A10](SOURCE_FINDINGS_AND_CONFLICTS.md:451), [MAV-03](SOURCE_FINDINGS_AND_CONFLICTS.md:507), [MAT-01](SOURCE_FINDINGS_AND_CONFLICTS.md:526), [MAT-02](SOURCE_FINDINGS_AND_CONFLICTS.md:527), [MAT-03](SOURCE_FINDINGS_AND_CONFLICTS.md:528), [MAT-04](SOURCE_FINDINGS_AND_CONFLICTS.md:529), [MAT-05](SOURCE_FINDINGS_AND_CONFLICTS.md:530), [MAT-06](SOURCE_FINDINGS_AND_CONFLICTS.md:531), [MAT-07](SOURCE_FINDINGS_AND_CONFLICTS.md:532), [MAT-08](SOURCE_FINDINGS_AND_CONFLICTS.md:533), [MAT-09](SOURCE_FINDINGS_AND_CONFLICTS.md:534), [AUT-09](SOURCE_FINDINGS_AND_CONFLICTS.md:775).

**Conversation upgrade lineage.** [DTM-A15](SOURCE_FINDINGS_AND_CONFLICTS.md:73), [JCV-A08](SOURCE_FINDINGS_AND_CONFLICTS.md:167), [DRF-A05](SOURCE_FINDINGS_AND_CONFLICTS.md:446), [DRF-A27](SOURCE_FINDINGS_AND_CONFLICTS.md:468). Read the full rows and their original conversation references; [the recheck](CONVERSATION_RECHECK.md) preserves the exact unit/exception routes.

<a id="up-g05-runner_duration"></a>
#### G05.RUNNER_DURATION — Reaction versus runner quality

[Existing definition, target and P0–P7](experiments/G.md#g05-runner_duration) remain binding.

**Specific upgrade scope.** Model contact, initial departure, retrace, renewed departure and failure as ordered duration-aware branches.

**Local comparison.** Compare hit/runner labels with structured transitions and direct joint heads at matched forecast cuts.

**Additional cases.** Fast bounce then failure; slow runner; unresolved boundary; repeated contact.

<a id="up-g06"></a>
### UP-G06 — Executable action-value and cost model

Parent: [G06](components/GATES_AND_SELECTION.md); [local phases](experiments/G.md#g06); [definition refinement](SYSTEM_REFINEMENT.md#sr-g06). Upgrade role: `decision`.

**Starting idea.** Multiply win probability by reward and subtract loss/cost.

**Existing improvement path.** Joint fill, path, cost, occupied duration and terminal-state action value.

**Remaining weakness.** Independent action estimates waste shared information and can exaggerate uncertainty in one difference while understating common model error.

**Further upgrade.** Evaluate all feasible complete policies on coupled, admissible outcome scenarios and common random numbers. Compare direct action-value fits with a regularized model of paired value differences relative to a simple policy; propagate common fill/price/latency errors jointly and preserve the cash reward contract.

**Fair comparison.** Empirical outcome table, existing distributional value, coupled scenario evaluation and paired residual-value model.

**Evidence.** Paired value error, policy regret on supported simulation assumptions, net/tail calibration, ranking stability and compute.

**Additional local cases to implement.** Two actions share every outcome until one stop event; incompatible fill scenarios; double-counted continuation; profitable but long occupancy.

**Decision or system use.** Improve enter/route/exit comparisons while making common uncertainty and simulator dependence explicit.

**Exact reviewed source clauses.** [DTM-A15](SOURCE_FINDINGS_AND_CONFLICTS.md:73), [DRF-U01](SOURCE_FINDINGS_AND_CONFLICTS.md:425), [DRF-A10](SOURCE_FINDINGS_AND_CONFLICTS.md:451), [TBR-05](SOURCE_FINDINGS_AND_CONFLICTS.md:740).

**Conversation upgrade lineage.** [DRF-A05](SOURCE_FINDINGS_AND_CONFLICTS.md:446), [DRF-A10](SOURCE_FINDINGS_AND_CONFLICTS.md:451), [DRF-A21](SOURCE_FINDINGS_AND_CONFLICTS.md:462). Read the full rows and their original conversation references; [the recheck](CONVERSATION_RECHECK.md) preserves the exact unit/exception routes.

<a id="up-g06-cost_dependence"></a>
#### G06.COST_DEPENDENCE — Joint fill and action-value uncertainty

[Existing definition, target and P0–P7](experiments/G.md#g06-cost_dependence) remain binding.

**Specific upgrade scope.** Couple price, fill, delay, cost and occupied-duration scenarios across complete competing actions.

**Local comparison.** Compare direct values with paired residual differences and common random numbers, retaining shared model error.

**Additional cases.** Actions identical until one barrier; inconsistent fills; nonfill opportunity counted twice; continuation overlap.

<a id="up-g07"></a>
### UP-G07 — Value of waiting, deeper levels and additional information

Parent: [G07](components/GATES_AND_SELECTION.md); [local phases](experiments/G.md#g07); [definition refinement](SYSTEM_REFINEMENT.md#sr-g07). Upgrade role: `decision`.

**Starting idea.** Take the nearest good level or wait for confirmation.

**Existing improvement path.** Common-boundary finite-horizon policies with occupancy and information transitions.

**Remaining weakness.** Waiting rules rarely separate the information gained from the price, time and opportunity lost while obtaining it.

**Further upgrade.** Add bounded two-decision lookahead with explicit observation-event transitions. Estimate the incremental value of the next observable stage versus price deterioration, nonarrival and opportunity consumption; compare to a myopic policy and fixed waits before expanding depth. Include a finite-horizon value-of-information decomposition as a diagnostic.

**Fair comparison.** Positive-value now, fixed deeper/confirmation wait, one-step and bounded two-step policies with identical candidate availability and reward accounting.

**Evidence.** Full-day constrained net, waiting regret, missed/expired opportunities, occupancy, transition calibration and planning cost.

**Additional local cases to implement.** No confirmation arrives; better level invalidates; new opportunity appears while occupied; additional signal changes nothing; boundary intervenes.

**Decision or system use.** Choose when waiting improves the complete day policy instead of treating stronger confirmation as automatically beneficial.

**Exact reviewed source clauses.** [DTM-A04](SOURCE_FINDINGS_AND_CONFLICTS.md:62), [JXA-09](SOURCE_FINDINGS_AND_CONFLICTS.md:108), [DRF-A10](SOURCE_FINDINGS_AND_CONFLICTS.md:451), [AUT-04](SOURCE_FINDINGS_AND_CONFLICTS.md:770), [AUT-06](SOURCE_FINDINGS_AND_CONFLICTS.md:772).

**Conversation upgrade lineage.** [DTM-A04](SOURCE_FINDINGS_AND_CONFLICTS.md:62), [DTM-A11](SOURCE_FINDINGS_AND_CONFLICTS.md:69), [DTM-A14](SOURCE_FINDINGS_AND_CONFLICTS.md:72), [CRL-16](SOURCE_FINDINGS_AND_CONFLICTS.md:232), [DRF-A24](SOURCE_FINDINGS_AND_CONFLICTS.md:465), [DRF-A27](SOURCE_FINDINGS_AND_CONFLICTS.md:468). Read the full rows and their original conversation references; [the recheck](CONVERSATION_RECHECK.md) preserves the exact unit/exception routes.

<a id="up-g07-duration"></a>
#### G07.DURATION — Common-boundary waiting and occupancy

[Existing definition, target and P0–P7](experiments/G.md#g07-duration) remain binding.

**Specific upgrade scope.** Compare bounded lookahead with myopic policies using the same terminal boundary and correctly timed continuation.

**Local comparison.** Evaluate total day net/occupancy rather than independent USD-per-minute scores; common scenarios support paired differences.

**Additional cases.** Short trade leaves later opportunity; long trade blocks it; boundary truncation; pending order consumes capacity.

<a id="up-g07-information"></a>
#### G07.INFORMATION — Value of observing another stage

[Existing definition, target and P0–P7](experiments/G.md#g07-information) remain binding.

**Specific upgrade scope.** Estimate incremental value of the next observable stage against delay, price deterioration and nonarrival.

**Local comparison.** Compare fixed confirmation/deeper waits, one-step and bounded two-step policies before greater planning depth.

**Additional cases.** Next signal adds nothing; confirmation never arrives; source expires; price runs away.

<a id="up-g08"></a>
### UP-G08 — Candidate ranking and constrained action selection

Parent: [G08](components/GATES_AND_SELECTION.md); [local phases](experiments/G.md#g08); [definition refinement](SYSTEM_REFINEMENT.md#sr-g08). Upgrade role: `decision`.

**Starting idea.** Rank levels by distance, size or confluence count.

**Existing improvement path.** Complete action sets, calibrated values and pairwise/listwise/set alternatives.

**Remaining weakness.** Equivalent actions and correlated objects can inflate competition; value differences near the selected maximum remain poorly calibrated.

**Further upgrade.** Canonicalize actions with identical execution/terminal-policy meaning, preserve their evidence provenance, then compare calibrated pairwise value differences and set-aware selection. Add conservative dominance pruning only when the declared outcome/continuation model establishes it; benchmark against complete enumeration and keep a no-pruning reference.

**Fair comparison.** Nearest/confluence, pointwise value, paired difference and set policy; full enumeration versus proven-local pruning.

**Evidence.** Selected-versus-flat calibration, net/regret, candidate coverage, action stability under duplicates and decision latency.

**Additional local cases to implement.** Duplicate geometry with distinct evidence; action differs only in expiry; unseen set size; apparent pointwise dominance fails after occupancy.

**Decision or system use.** Select among complete feasible alternatives with less duplicated evidence and measured computational savings.

**Exact reviewed source clauses.** [DTM-A04](SOURCE_FINDINGS_AND_CONFLICTS.md:62), [DTM-A11](SOURCE_FINDINGS_AND_CONFLICTS.md:69), [DTM-A18](SOURCE_FINDINGS_AND_CONFLICTS.md:76), [JFN-10](SOURCE_FINDINGS_AND_CONFLICTS.md:144), [JCV-U02](SOURCE_FINDINGS_AND_CONFLICTS.md:155), [JCV-U05](SOURCE_FINDINGS_AND_CONFLICTS.md:158), [JCV-A06](SOURCE_FINDINGS_AND_CONFLICTS.md:165), [JCV-A07](SOURCE_FINDINGS_AND_CONFLICTS.md:166), [JCV-A08](SOURCE_FINDINGS_AND_CONFLICTS.md:167), [CEX-14](SOURCE_FINDINGS_AND_CONFLICTS.md:196), [CRL-03](SOURCE_FINDINGS_AND_CONFLICTS.md:219), [CRL-11](SOURCE_FINDINGS_AND_CONFLICTS.md:227), [CRL-19](SOURCE_FINDINGS_AND_CONFLICTS.md:235), [AM1-10](SOURCE_FINDINGS_AND_CONFLICTS.md:290), [DRF-U03](SOURCE_FINDINGS_AND_CONFLICTS.md:427), [DRF-U07](SOURCE_FINDINGS_AND_CONFLICTS.md:431), [DRF-U10](SOURCE_FINDINGS_AND_CONFLICTS.md:434), [DRF-U11](SOURCE_FINDINGS_AND_CONFLICTS.md:435), [DRF-A10](SOURCE_FINDINGS_AND_CONFLICTS.md:451), [DRF-A19](SOURCE_FINDINGS_AND_CONFLICTS.md:460), [DRF-A21](SOURCE_FINDINGS_AND_CONFLICTS.md:462), [DRF-A22](SOURCE_FINDINGS_AND_CONFLICTS.md:463), [DRF-A24](SOURCE_FINDINGS_AND_CONFLICTS.md:465), [AUT-04](SOURCE_FINDINGS_AND_CONFLICTS.md:770), [PIN005-01](SOURCE_FINDINGS_AND_CONFLICTS.md:828), [PIN005-02](SOURCE_FINDINGS_AND_CONFLICTS.md:829), [PIN005-03](SOURCE_FINDINGS_AND_CONFLICTS.md:830), [PIN005-04](SOURCE_FINDINGS_AND_CONFLICTS.md:831), [PIN005-05](SOURCE_FINDINGS_AND_CONFLICTS.md:832).

**Conversation upgrade lineage.** [JCV-U02](SOURCE_FINDINGS_AND_CONFLICTS.md:155), [CEX-14](SOURCE_FINDINGS_AND_CONFLICTS.md:196), [CRL-03](SOURCE_FINDINGS_AND_CONFLICTS.md:219), [CRL-11](SOURCE_FINDINGS_AND_CONFLICTS.md:227), [CRL-19](SOURCE_FINDINGS_AND_CONFLICTS.md:235), [DRF-U03](SOURCE_FINDINGS_AND_CONFLICTS.md:427), [DRF-U11](SOURCE_FINDINGS_AND_CONFLICTS.md:435), [DRF-A10](SOURCE_FINDINGS_AND_CONFLICTS.md:451), [DRF-A24](SOURCE_FINDINGS_AND_CONFLICTS.md:465). Read the full rows and their original conversation references; [the recheck](CONVERSATION_RECHECK.md) preserves the exact unit/exception routes.

<a id="up-g08-ranking"></a>
#### G08.RANKING — Candidate and action selection objectives

[Existing definition, target and P0–P7](experiments/G.md#g08-ranking) remain binding.

**Specific upgrade scope.** Canonicalize equivalent actions and compare calibrated pairwise value differences with pointwise and set ranking.

**Local comparison.** Keep full enumeration as reference; any pruning needs a stated dominance result under the actual continuation model.

**Additional cases.** Duplicate evidence; same entry different expiry; near tie to flat; apparent dominance fails with occupancy.

<a id="up-g09"></a>
### UP-G09 — Applicability, disagreement and abstention gate

Parent: [G09](components/GATES_AND_SELECTION.md); [local phases](experiments/G.md#g09); [definition refinement](SYSTEM_REFINEMENT.md#sr-g09). Upgrade role: `decision`.

**Starting idea.** Trade when enough indicators agree.

**Existing improvement path.** Separate critical validity and later uncertainty/support gates with risk-coverage evaluation.

**Remaining weakness.** Large forecast disagreement need not change the best action, while small forecast error can reverse a close decision.

**Further upgrade.** Compare action-stability and conditional regret gates under joint uncertainty scenarios with forecast-spread thresholds. Evaluate reduced-use, wait and flat choices separately; use supported reliability estimates and preserve unconditional integrity/risk rules. Calibrate the resulting selected policy rather than only the ungated predictor.

**Fair comparison.** Always-use-valid, fixed spread/support thresholds and joint action-instability/regret rules under the same opportunity set.

**Evidence.** Net-versus-coverage frontier, tail risk, abstention opportunity cost, decision disagreement and date support.

**Additional local cases to implement.** Uncertain forecasts imply same action; precise forecasts have near-tied values; unsupported missing pattern; false confidence from correlated experts.

**Decision or system use.** Abstain for decision-relevant uncertainty while retaining useful opportunities whose action is robust within tested assumptions.

**Exact reviewed source clauses.** [DTM-A10](SOURCE_FINDINGS_AND_CONFLICTS.md:68), [CEX-05](SOURCE_FINDINGS_AND_CONFLICTS.md:187), [CRL-17](SOURCE_FINDINGS_AND_CONFLICTS.md:233), [CRL-18](SOURCE_FINDINGS_AND_CONFLICTS.md:234), [DRF-A14](SOURCE_FINDINGS_AND_CONFLICTS.md:455), [MVF-01](SOURCE_FINDINGS_AND_CONFLICTS.md:783), [MVF-02](SOURCE_FINDINGS_AND_CONFLICTS.md:784), [MVF-03](SOURCE_FINDINGS_AND_CONFLICTS.md:785), [MVF-04](SOURCE_FINDINGS_AND_CONFLICTS.md:786), [MVF-05](SOURCE_FINDINGS_AND_CONFLICTS.md:787), [MVF-06](SOURCE_FINDINGS_AND_CONFLICTS.md:788), [MVF-07](SOURCE_FINDINGS_AND_CONFLICTS.md:789), [PIN008-01](SOURCE_FINDINGS_AND_CONFLICTS.md:824), [PIN009-01](SOURCE_FINDINGS_AND_CONFLICTS.md:825), [PIN009-02](SOURCE_FINDINGS_AND_CONFLICTS.md:826), [PIN011-01](SOURCE_FINDINGS_AND_CONFLICTS.md:845), [PIN011-02](SOURCE_FINDINGS_AND_CONFLICTS.md:846), [PIN011-03](SOURCE_FINDINGS_AND_CONFLICTS.md:847), [PIN011-04](SOURCE_FINDINGS_AND_CONFLICTS.md:848), [PIN011-05](SOURCE_FINDINGS_AND_CONFLICTS.md:849), [PIN011-06](SOURCE_FINDINGS_AND_CONFLICTS.md:850), [PIN011-07](SOURCE_FINDINGS_AND_CONFLICTS.md:851), [PIN017-01](SOURCE_FINDINGS_AND_CONFLICTS.md:872), [PIN017-02](SOURCE_FINDINGS_AND_CONFLICTS.md:873), [PIN017-03](SOURCE_FINDINGS_AND_CONFLICTS.md:874), [PIN017-04](SOURCE_FINDINGS_AND_CONFLICTS.md:875), [PIN020-01](SOURCE_FINDINGS_AND_CONFLICTS.md:890), [PIN020-02](SOURCE_FINDINGS_AND_CONFLICTS.md:891), [PIN033-01](SOURCE_FINDINGS_AND_CONFLICTS.md:917), [PIN033-02](SOURCE_FINDINGS_AND_CONFLICTS.md:918), [PIN034-01](SOURCE_FINDINGS_AND_CONFLICTS.md:919), [PIN050-01](SOURCE_FINDINGS_AND_CONFLICTS.md:968), [PIN050-02](SOURCE_FINDINGS_AND_CONFLICTS.md:969), [PIN050-03](SOURCE_FINDINGS_AND_CONFLICTS.md:970), [PIN072-01](SOURCE_FINDINGS_AND_CONFLICTS.md:1045), [PIN072-02](SOURCE_FINDINGS_AND_CONFLICTS.md:1046), [PIN079-01](SOURCE_FINDINGS_AND_CONFLICTS.md:1066), [PIN079-02](SOURCE_FINDINGS_AND_CONFLICTS.md:1067), [PIN079-03](SOURCE_FINDINGS_AND_CONFLICTS.md:1068), [PIN079-04](SOURCE_FINDINGS_AND_CONFLICTS.md:1069).

**Conversation upgrade lineage.** [DTM-A10](SOURCE_FINDINGS_AND_CONFLICTS.md:68), [JCV-A06](SOURCE_FINDINGS_AND_CONFLICTS.md:165), [CEX-04](SOURCE_FINDINGS_AND_CONFLICTS.md:186), [DRF-A07](SOURCE_FINDINGS_AND_CONFLICTS.md:448), [DRF-A21](SOURCE_FINDINGS_AND_CONFLICTS.md:462). Read the full rows and their original conversation references; [the recheck](CONVERSATION_RECHECK.md) preserves the exact unit/exception routes.

<a id="up-g09-support"></a>
#### G09.SUPPORT — Applicability and abstention

[Existing definition, target and P0–P7](experiments/G.md#g09-support) remain binding.

**Specific upgrade scope.** Gate on joint action instability/regret as well as validity and empirical support, keeping the early mask distinct.

**Local comparison.** Compare always-use-valid, spread thresholds, reduced-use/wait and stability-based abstention by net-risk-coverage.

**Additional cases.** Large forecast uncertainty same action; small uncertainty flips action; unseen support; false confidence from duplicates.

<a id="up-g10"></a>
### UP-G10 — Per-expert adaptation, recalibration and retirement policy

Parent: [G10](components/GATES_AND_SELECTION.md); [local phases](experiments/G.md#g10); [definition refinement](SYSTEM_REFINEMENT.md#sr-g10). Upgrade role: `research_method`.

**Starting idea.** Refit the full system whenever performance falls.

**Existing improvement path.** Per-expert versioned adaptation, mature-label monitoring and rollback.

**Remaining weakness.** One schedule can over-update stable measurements while missing deterioration in calibration or action selection.

**Further upgrade.** Separate measurement-state updates, forecast parameters, calibrators, mixture weights and policy thresholds into independently versioned change layers. Compare bounded layer-specific update policies and champion/challenger shadow evaluation under a fixed intervention/false-alert budget; evaluate the complete adaptation policy prequentially.

**Fair comparison.** Frozen, uniform scheduled refit, layer-specific schedule and registered drift response with identical data maturity and total budget.

**Evidence.** Recovery delay, unnecessary changes, calibration/net after costs, artifact compatibility and rollback time.

**Additional local cases to implement.** Calibration drift with stable ranking; upstream source fault; many correlated alerts; changed model needs new calibration; performance dip from chance.

**Decision or system use.** Change the smallest evidenced layer and retire unsupported experts without discretionary rescue of a future test.

**Exact reviewed source clauses.** [CEX-15](SOURCE_FINDINGS_AND_CONFLICTS.md:197), [CRL-09](SOURCE_FINDINGS_AND_CONFLICTS.md:225), [CRL-17](SOURCE_FINDINGS_AND_CONFLICTS.md:233), [DRF-U06](SOURCE_FINDINGS_AND_CONFLICTS.md:430), [PIN011-01](SOURCE_FINDINGS_AND_CONFLICTS.md:845), [PIN011-02](SOURCE_FINDINGS_AND_CONFLICTS.md:846), [PIN011-03](SOURCE_FINDINGS_AND_CONFLICTS.md:847), [PIN011-04](SOURCE_FINDINGS_AND_CONFLICTS.md:848), [PIN011-05](SOURCE_FINDINGS_AND_CONFLICTS.md:849), [PIN011-06](SOURCE_FINDINGS_AND_CONFLICTS.md:850), [PIN011-07](SOURCE_FINDINGS_AND_CONFLICTS.md:851), [PIN020-01](SOURCE_FINDINGS_AND_CONFLICTS.md:890), [PIN020-02](SOURCE_FINDINGS_AND_CONFLICTS.md:891), [PIN034-01](SOURCE_FINDINGS_AND_CONFLICTS.md:919), [PIN050-01](SOURCE_FINDINGS_AND_CONFLICTS.md:968), [PIN050-02](SOURCE_FINDINGS_AND_CONFLICTS.md:969), [PIN050-03](SOURCE_FINDINGS_AND_CONFLICTS.md:970), [PIN072-01](SOURCE_FINDINGS_AND_CONFLICTS.md:1045), [PIN072-02](SOURCE_FINDINGS_AND_CONFLICTS.md:1046), [PIN079-01](SOURCE_FINDINGS_AND_CONFLICTS.md:1066), [PIN079-02](SOURCE_FINDINGS_AND_CONFLICTS.md:1067), [PIN079-03](SOURCE_FINDINGS_AND_CONFLICTS.md:1068), [PIN079-04](SOURCE_FINDINGS_AND_CONFLICTS.md:1069).

**Conversation upgrade lineage.** [CEX-15](SOURCE_FINDINGS_AND_CONFLICTS.md:197), [CRL-09](SOURCE_FINDINGS_AND_CONFLICTS.md:225), [CRL-17](SOURCE_FINDINGS_AND_CONFLICTS.md:233), [DRF-U06](SOURCE_FINDINGS_AND_CONFLICTS.md:430), [DRF-A18](SOURCE_FINDINGS_AND_CONFLICTS.md:459). Read the full rows and their original conversation references; [the recheck](CONVERSATION_RECHECK.md) preserves the exact unit/exception routes.

<a id="up-g10-adaptation"></a>
#### G10.ADAPTATION — Controlled per-expert change policies

[Existing definition, target and P0–P7](experiments/G.md#g10-adaptation) remain binding.

**Specific upgrade scope.** Version and adapt measurement state, forecast parameters, calibrators, mixtures and policy thresholds separately.

**Local comparison.** Compare frozen/uniform schedules with bounded layer-specific policies and shadow challengers under one prequential protocol.

**Additional cases.** Calibration drifts but rank holds; new model needs new calibrator; source fault; chance drawdown.

<a id="family-p"></a>
## Policy, execution and risk

<a id="up-p01"></a>
### UP-P01 — Action state and complete sequential policy

Parent: [P01](components/POLICY_EXECUTION_RISK.md); [local phases](experiments/P.md#p01); [definition refinement](SYSTEM_REFINEMENT.md#sr-p01). Upgrade role: `engineering`.

**Starting idea.** Convert a signal directly into an order.

**Existing improvement path.** Complete one-mini state/action policy with risk-approved intents and causal event decisions.

**Remaining weakness.** Reference research and optimized runtime can interpret the same action or order transition differently.

**Further upgrade.** Compile registered action templates and pre/postconditions into a shared policy transition protocol, with a literal reference reducer and optimized executor. Explicitly encode pending entry, protective orders, action expiry, terminal time and reward ownership; enumerate small reachable state graphs for semantic checks.

**Fair comparison.** Hand-authored reference transitions versus compiled templates and optimized execution on identical event traces.

**Evidence.** State/action parity, unreachable illegal states, duplicate intent detection, transition latency and reproducible recovery.

**Additional local cases to implement.** Candidate changes while entry pending; exit and stop race; clock cutoff without price event; flat state with live entry order.

**Decision or system use.** Keep increasingly rich selection and management policies within the same complete executable one-mini contract.

**Exact reviewed source clauses.** [JTR-15](SOURCE_FINDINGS_AND_CONFLICTS.md:32), [DTM-A01](SOURCE_FINDINGS_AND_CONFLICTS.md:59), [DTM-A16](SOURCE_FINDINGS_AND_CONFLICTS.md:74), [JXA-24](SOURCE_FINDINGS_AND_CONFLICTS.md:123), [JFN-06](SOURCE_FINDINGS_AND_CONFLICTS.md:140), [VX4-03](SOURCE_FINDINGS_AND_CONFLICTS.md:326), [CD3-01](SOURCE_FINDINGS_AND_CONFLICTS.md:404), [CD3-02](SOURCE_FINDINGS_AND_CONFLICTS.md:405), [CD3-03](SOURCE_FINDINGS_AND_CONFLICTS.md:406), [CD3-04](SOURCE_FINDINGS_AND_CONFLICTS.md:407), [CD3-05](SOURCE_FINDINGS_AND_CONFLICTS.md:408), [EMO-01](SOURCE_FINDINGS_AND_CONFLICTS.md:481), [EMO-02](SOURCE_FINDINGS_AND_CONFLICTS.md:482), [EMO-03](SOURCE_FINDINGS_AND_CONFLICTS.md:483), [EMO-04](SOURCE_FINDINGS_AND_CONFLICTS.md:484), [K18-05](SOURCE_FINDINGS_AND_CONFLICTS.md:656).

**Conversation upgrade lineage.** [DTM-A01](SOURCE_FINDINGS_AND_CONFLICTS.md:59). Read the full rows and their original conversation references; [the recheck](CONVERSATION_RECHECK.md) preserves the exact unit/exception routes.

<a id="up-p01-action_state"></a>
#### P01.ACTION_STATE — Finite one-mini action transitions

[Existing definition, target and P0–P7](experiments/P.md#p01-action_state) remain binding.

**Specific upgrade scope.** Compile complete action templates and shared transition semantics into reference and optimized one-mini reducers.

**Local comparison.** Compare reachable state/action traces and reward ownership across research/runtime, including pending and protection states.

**Additional cases.** Exit/stop race; expired intent; candidate change while pending; flat with live order.

<a id="up-p02"></a>
### UP-P02 — Structural stop and full-position destination choice

Parent: [P02](components/POLICY_EXECUTION_RISK.md); [local phases](experiments/P.md#p02); [definition refinement](SYSTEM_REFINEMENT.md#sr-p02). Upgrade role: `decision`.

**Starting idea.** Use a fixed RR or a source stop and target.

**Existing improvement path.** Structural stops, valid tick rounding, path distributions and budget feasibility.

**Remaining weakness.** Optimizing stop, target and expiry separately can choose a bracket that is jointly dominated or unfunded at actual entry.

**Further upgrade.** Construct a joint feasible frontier over source-faithful stop variants, destination, expiry and route using the same coupled path/cost scenarios. Prune only verified dominated complete plans; compare robust lower-value/tail constraints with expected-value selection. Keep structural invalidation distinct from adjustable buffers.

**Fair comparison.** Fixed/source bracket, structural nearest target, full registered grid and conservative frontier selection at identical entry cuts.

**Evidence.** Net and tail loss, budget-feasible opportunity coverage, sensitivity to fill price, frontier regret and computation.

**Additional local cases to implement.** Tick rounding crosses headroom; target reached after expiry; mapping uncertainty changes stop; high-value plan consumes all remaining day.

**Decision or system use.** Choose complete feasible brackets with a transparent tradeoff among loss, destination, time and execution uncertainty.

**Exact reviewed source clauses.** [JTR-04](SOURCE_FINDINGS_AND_CONFLICTS.md:21), [JTR-15](SOURCE_FINDINGS_AND_CONFLICTS.md:32), [JTR-16](SOURCE_FINDINGS_AND_CONFLICTS.md:33), [JTR-17](SOURCE_FINDINGS_AND_CONFLICTS.md:34), [DTM-A16](SOURCE_FINDINGS_AND_CONFLICTS.md:74), [TP3-06](SOURCE_FINDINGS_AND_CONFLICTS.md:315), [VX4-03](SOURCE_FINDINGS_AND_CONFLICTS.md:326), [VX4-04](SOURCE_FINDINGS_AND_CONFLICTS.md:327), [CD2-01](SOURCE_FINDINGS_AND_CONFLICTS.md:399), [CD2-02](SOURCE_FINDINGS_AND_CONFLICTS.md:400), [CD2-03](SOURCE_FINDINGS_AND_CONFLICTS.md:401), [CD2-04](SOURCE_FINDINGS_AND_CONFLICTS.md:402), [CD2-05](SOURCE_FINDINGS_AND_CONFLICTS.md:403), [GXF-13](SOURCE_FINDINGS_AND_CONFLICTS.md:497), [OFM-01](SOURCE_FINDINGS_AND_CONFLICTS.md:623), [OFM-02](SOURCE_FINDINGS_AND_CONFLICTS.md:624), [OFM-03](SOURCE_FINDINGS_AND_CONFLICTS.md:625), [OFM-04](SOURCE_FINDINGS_AND_CONFLICTS.md:626), [OFM-05](SOURCE_FINDINGS_AND_CONFLICTS.md:627), [OFM-06](SOURCE_FINDINGS_AND_CONFLICTS.md:628), [OFM-07](SOURCE_FINDINGS_AND_CONFLICTS.md:629), [OFM-08](SOURCE_FINDINGS_AND_CONFLICTS.md:630), [OFM-09](SOURCE_FINDINGS_AND_CONFLICTS.md:631), [K10-01](SOURCE_FINDINGS_AND_CONFLICTS.md:639), [K10-02](SOURCE_FINDINGS_AND_CONFLICTS.md:640), [K10-03](SOURCE_FINDINGS_AND_CONFLICTS.md:641), [K10-04](SOURCE_FINDINGS_AND_CONFLICTS.md:642), [K10-05](SOURCE_FINDINGS_AND_CONFLICTS.md:643), [K10-06](SOURCE_FINDINGS_AND_CONFLICTS.md:644), [F23-04](SOURCE_FINDINGS_AND_CONFLICTS.md:670), [CCS-05](SOURCE_FINDINGS_AND_CONFLICTS.md:685), [TBR-05](SOURCE_FINDINGS_AND_CONFLICTS.md:740), [OBT-09](SOURCE_FINDINGS_AND_CONFLICTS.md:758), [AUT-03](SOURCE_FINDINGS_AND_CONFLICTS.md:769).

**Conversation upgrade lineage.** [DTM-A16](SOURCE_FINDINGS_AND_CONFLICTS.md:74), [JCV-A06](SOURCE_FINDINGS_AND_CONFLICTS.md:165), [DRF-A24](SOURCE_FINDINGS_AND_CONFLICTS.md:465). Read the full rows and their original conversation references; [the recheck](CONVERSATION_RECHECK.md) preserves the exact unit/exception routes.

<a id="up-p02-brackets"></a>
#### P02.BRACKETS — Structural invalidation and destination choices

[Existing definition, target and P0–P7](experiments/P.md#p02-brackets) remain binding.

**Specific upgrade scope.** Evaluate joint stop/target/expiry/route frontiers with common path/cost scenarios and structural feasibility.

**Local comparison.** Compare every source bracket with bounded complete grids and conservative frontier choices; measure net and tail/budget fit.

**Additional cases.** Tick rounding exceeds headroom; target after expiry; uncertain mapping; nonfilled midpoint entry.

<a id="up-p03"></a>
### UP-P03 — Full-position exits, protected structure and trailing value

Parent: [P03](components/POLICY_EXECUTION_RISK.md); [local phases](experiments/P.md#p03); [definition refinement](SYSTEM_REFINEMENT.md#sr-p03). Upgrade role: `decision`.

**Starting idea.** Move a stop to entry or trail each new swing.

**Existing improvement path.** Separate full-position exit, stop, target and hold policies with incremental value.

**Remaining weakness.** Frequent marginal amendments may add latency/race exposure and overreact to noisy small value changes.

**Further upgrade.** Estimate the incremental full-exit/hold/amend value relative to the current committed policy on paired scenarios. Compare shrinkage and hysteresis/minimum-value thresholds for optional amendments, accounting for cancel/replace delay and loss of old protection; emergency risk actions bypass discretionary thresholds.

**Fair comparison.** Fixed bracket, simple trail, existing stopping model and incremental-value policy with/without amendment hysteresis.

**Evidence.** Constrained net, giveback/tail risk, amendment count, protection gaps and incremental value calibration.

**Additional local cases to implement.** Tiny oscillating benefit; large thesis failure; old stop fills during replace; target extension loses a timely exit.

**Decision or system use.** Improve management only when its expected benefit survives amendment costs and uncertainty for the entire single position.

**Exact reviewed source clauses.** [JTR-04](SOURCE_FINDINGS_AND_CONFLICTS.md:21), [JTR-08](SOURCE_FINDINGS_AND_CONFLICTS.md:25), [JTR-24](SOURCE_FINDINGS_AND_CONFLICTS.md:41), [DTM-A16](SOURCE_FINDINGS_AND_CONFLICTS.md:74), [JXA-02](SOURCE_FINDINGS_AND_CONFLICTS.md:101), [JXA-09](SOURCE_FINDINGS_AND_CONFLICTS.md:108), [JXA-12](SOURCE_FINDINGS_AND_CONFLICTS.md:111), [JXA-16](SOURCE_FINDINGS_AND_CONFLICTS.md:115), [JXA-17](SOURCE_FINDINGS_AND_CONFLICTS.md:116), [JFN-10](SOURCE_FINDINGS_AND_CONFLICTS.md:144), [JCV-A08](SOURCE_FINDINGS_AND_CONFLICTS.md:167), [CEX-08](SOURCE_FINDINGS_AND_CONFLICTS.md:190), [VX4-03](SOURCE_FINDINGS_AND_CONFLICTS.md:326), [CD2-01](SOURCE_FINDINGS_AND_CONFLICTS.md:399), [CD2-02](SOURCE_FINDINGS_AND_CONFLICTS.md:400), [CD2-03](SOURCE_FINDINGS_AND_CONFLICTS.md:401), [CD2-04](SOURCE_FINDINGS_AND_CONFLICTS.md:402), [CD2-05](SOURCE_FINDINGS_AND_CONFLICTS.md:403), [CD3-01](SOURCE_FINDINGS_AND_CONFLICTS.md:404), [CD3-02](SOURCE_FINDINGS_AND_CONFLICTS.md:405), [CD3-03](SOURCE_FINDINGS_AND_CONFLICTS.md:406), [CD3-04](SOURCE_FINDINGS_AND_CONFLICTS.md:407), [CD3-05](SOURCE_FINDINGS_AND_CONFLICTS.md:408), [RDL-01](SOURCE_FINDINGS_AND_CONFLICTS.md:550), [RDL-02](SOURCE_FINDINGS_AND_CONFLICTS.md:551), [RDL-03](SOURCE_FINDINGS_AND_CONFLICTS.md:552), [RDL-04](SOURCE_FINDINGS_AND_CONFLICTS.md:553), [RDL-05](SOURCE_FINDINGS_AND_CONFLICTS.md:554), [RDL-06](SOURCE_FINDINGS_AND_CONFLICTS.md:555), [RDL-07](SOURCE_FINDINGS_AND_CONFLICTS.md:556), [OFM-01](SOURCE_FINDINGS_AND_CONFLICTS.md:623), [OFM-02](SOURCE_FINDINGS_AND_CONFLICTS.md:624), [OFM-03](SOURCE_FINDINGS_AND_CONFLICTS.md:625), [OFM-04](SOURCE_FINDINGS_AND_CONFLICTS.md:626), [OFM-05](SOURCE_FINDINGS_AND_CONFLICTS.md:627), [OFM-06](SOURCE_FINDINGS_AND_CONFLICTS.md:628), [OFM-07](SOURCE_FINDINGS_AND_CONFLICTS.md:629), [OFM-08](SOURCE_FINDINGS_AND_CONFLICTS.md:630), [OFM-09](SOURCE_FINDINGS_AND_CONFLICTS.md:631), [K10-01](SOURCE_FINDINGS_AND_CONFLICTS.md:639), [K10-02](SOURCE_FINDINGS_AND_CONFLICTS.md:640), [K10-03](SOURCE_FINDINGS_AND_CONFLICTS.md:641), [K10-04](SOURCE_FINDINGS_AND_CONFLICTS.md:642), [K10-05](SOURCE_FINDINGS_AND_CONFLICTS.md:643), [K10-06](SOURCE_FINDINGS_AND_CONFLICTS.md:644), [K18-01](SOURCE_FINDINGS_AND_CONFLICTS.md:652), [K18-02](SOURCE_FINDINGS_AND_CONFLICTS.md:653), [K18-03](SOURCE_FINDINGS_AND_CONFLICTS.md:654), [K18-04](SOURCE_FINDINGS_AND_CONFLICTS.md:655), [K18-05](SOURCE_FINDINGS_AND_CONFLICTS.md:656), [K18-06](SOURCE_FINDINGS_AND_CONFLICTS.md:657), [K18-07](SOURCE_FINDINGS_AND_CONFLICTS.md:658), [K18-08](SOURCE_FINDINGS_AND_CONFLICTS.md:659), [F23-01](SOURCE_FINDINGS_AND_CONFLICTS.md:667), [F23-02](SOURCE_FINDINGS_AND_CONFLICTS.md:668), [F23-03](SOURCE_FINDINGS_AND_CONFLICTS.md:669), [F23-04](SOURCE_FINDINGS_AND_CONFLICTS.md:670), [F23-05](SOURCE_FINDINGS_AND_CONFLICTS.md:671), [F23-06](SOURCE_FINDINGS_AND_CONFLICTS.md:672), [F23-07](SOURCE_FINDINGS_AND_CONFLICTS.md:673), [CCS-01](SOURCE_FINDINGS_AND_CONFLICTS.md:681), [CCS-02](SOURCE_FINDINGS_AND_CONFLICTS.md:682), [CCS-03](SOURCE_FINDINGS_AND_CONFLICTS.md:683), [CCS-04](SOURCE_FINDINGS_AND_CONFLICTS.md:684), [CCS-05](SOURCE_FINDINGS_AND_CONFLICTS.md:685), [CCS-06](SOURCE_FINDINGS_AND_CONFLICTS.md:686), [CCS-07](SOURCE_FINDINGS_AND_CONFLICTS.md:687), [CCS-08](SOURCE_FINDINGS_AND_CONFLICTS.md:688), [ALS-01](SOURCE_FINDINGS_AND_CONFLICTS.md:696), [ALS-02](SOURCE_FINDINGS_AND_CONFLICTS.md:697), [ALS-03](SOURCE_FINDINGS_AND_CONFLICTS.md:698), [ALS-04](SOURCE_FINDINGS_AND_CONFLICTS.md:699), [ALS-05](SOURCE_FINDINGS_AND_CONFLICTS.md:700), [ALS-06](SOURCE_FINDINGS_AND_CONFLICTS.md:701), [NYA-01](SOURCE_FINDINGS_AND_CONFLICTS.md:709), [NYA-02](SOURCE_FINDINGS_AND_CONFLICTS.md:710), [NYA-03](SOURCE_FINDINGS_AND_CONFLICTS.md:711), [NYA-04](SOURCE_FINDINGS_AND_CONFLICTS.md:712), [NYA-05](SOURCE_FINDINGS_AND_CONFLICTS.md:713), [NYA-06](SOURCE_FINDINGS_AND_CONFLICTS.md:714), [OBT-08](SOURCE_FINDINGS_AND_CONFLICTS.md:757), [OBT-09](SOURCE_FINDINGS_AND_CONFLICTS.md:758), [PIN011-07](SOURCE_FINDINGS_AND_CONFLICTS.md:851), [PIN034-01](SOURCE_FINDINGS_AND_CONFLICTS.md:919).

**Conversation upgrade lineage.** [DTM-A16](SOURCE_FINDINGS_AND_CONFLICTS.md:74), [JCV-A08](SOURCE_FINDINGS_AND_CONFLICTS.md:167), [CEX-08](SOURCE_FINDINGS_AND_CONFLICTS.md:190), [CRL-13](SOURCE_FINDINGS_AND_CONFLICTS.md:229). Read the full rows and their original conversation references; [the recheck](CONVERSATION_RECHECK.md) preserves the exact unit/exception routes.

<a id="up-p03-exit_value"></a>
#### P03.EXIT_VALUE — Full-position hold, protect and exit

[Existing definition, target and P0–P7](experiments/P.md#p03-exit_value) remain binding.

**Specific upgrade scope.** Estimate paired incremental exit/hold/amend value relative to the currently committed full-position plan.

**Local comparison.** Compare each stop/target policy alone and joint hysteresis/shrinkage alternatives including replace latency and protection gap.

**Additional cases.** Tiny alternating value; real thesis failure; old stop fills during amendment; extension misses exit.

<a id="up-p04"></a>
### UP-P04 — Re-entry, idea memory and cumulative risk

Parent: [P04](components/POLICY_EXECUTION_RISK.md); [local phases](experiments/P.md#p04); [definition refinement](SYSTEM_REFINEMENT.md#sr-p04). Upgrade role: `decision`.

**Starting idea.** Retry a level a fixed number of times.

**Existing improvement path.** Idea lineage, fresh-evidence rules and cumulative idea/day budgets.

**Remaining weakness.** A new timestamp or return to the same band may repeat the original evidence rather than renew opportunity.

**Further upgrade.** Build a causal evidence-novelty and replenishment state for each idea, separating new flow/structure/source changes from reused observations. Compare repeat quality conditional on visit history with pooled first-entry quality, using partial pooling for sparse later visits and the same cumulative budget.

**Fair comparison.** No retry, fixed cooldown/count, existing repeat model and novelty-conditioned repeat value.

**Evidence.** Net by visit and idea, cumulative loss/tails, false novelty, missed renewed opportunities and independent idea support.

**Additional local cases to implement.** Band reissued with new ID; same prints reused; new valid defense after loss; profitable prior trade but no new evidence.

**Decision or system use.** Permit re-entry only when fresh information adds value under unchanged one-unit and cumulative-risk constraints.

**Exact reviewed source clauses.** [JTR-14](SOURCE_FINDINGS_AND_CONFLICTS.md:31), [JTR-24](SOURCE_FINDINGS_AND_CONFLICTS.md:41), [DTM-A16](SOURCE_FINDINGS_AND_CONFLICTS.md:74), [JXA-02](SOURCE_FINDINGS_AND_CONFLICTS.md:101), [JXA-12](SOURCE_FINDINGS_AND_CONFLICTS.md:111), [JFN-10](SOURCE_FINDINGS_AND_CONFLICTS.md:144), [CD1-01](SOURCE_FINDINGS_AND_CONFLICTS.md:394), [CD1-02](SOURCE_FINDINGS_AND_CONFLICTS.md:395), [CD1-03](SOURCE_FINDINGS_AND_CONFLICTS.md:396), [CD1-04](SOURCE_FINDINGS_AND_CONFLICTS.md:397), [CD1-05](SOURCE_FINDINGS_AND_CONFLICTS.md:398), [CD2-01](SOURCE_FINDINGS_AND_CONFLICTS.md:399), [CD2-02](SOURCE_FINDINGS_AND_CONFLICTS.md:400), [CD2-03](SOURCE_FINDINGS_AND_CONFLICTS.md:401), [CD2-04](SOURCE_FINDINGS_AND_CONFLICTS.md:402), [CD2-05](SOURCE_FINDINGS_AND_CONFLICTS.md:403), [EMO-01](SOURCE_FINDINGS_AND_CONFLICTS.md:481), [EMO-02](SOURCE_FINDINGS_AND_CONFLICTS.md:482), [EMO-03](SOURCE_FINDINGS_AND_CONFLICTS.md:483), [EMO-04](SOURCE_FINDINGS_AND_CONFLICTS.md:484), [OFM-01](SOURCE_FINDINGS_AND_CONFLICTS.md:623), [OFM-02](SOURCE_FINDINGS_AND_CONFLICTS.md:624), [OFM-03](SOURCE_FINDINGS_AND_CONFLICTS.md:625), [OFM-04](SOURCE_FINDINGS_AND_CONFLICTS.md:626), [OFM-05](SOURCE_FINDINGS_AND_CONFLICTS.md:627), [OFM-06](SOURCE_FINDINGS_AND_CONFLICTS.md:628), [OFM-07](SOURCE_FINDINGS_AND_CONFLICTS.md:629), [OFM-08](SOURCE_FINDINGS_AND_CONFLICTS.md:630), [OFM-09](SOURCE_FINDINGS_AND_CONFLICTS.md:631), [K18-01](SOURCE_FINDINGS_AND_CONFLICTS.md:652), [K18-02](SOURCE_FINDINGS_AND_CONFLICTS.md:653), [K18-03](SOURCE_FINDINGS_AND_CONFLICTS.md:654), [K18-04](SOURCE_FINDINGS_AND_CONFLICTS.md:655), [K18-05](SOURCE_FINDINGS_AND_CONFLICTS.md:656), [K18-06](SOURCE_FINDINGS_AND_CONFLICTS.md:657), [K18-07](SOURCE_FINDINGS_AND_CONFLICTS.md:658), [K18-08](SOURCE_FINDINGS_AND_CONFLICTS.md:659), [F23-05](SOURCE_FINDINGS_AND_CONFLICTS.md:671), [CCS-05](SOURCE_FINDINGS_AND_CONFLICTS.md:685), [ALS-01](SOURCE_FINDINGS_AND_CONFLICTS.md:696), [ALS-02](SOURCE_FINDINGS_AND_CONFLICTS.md:697), [ALS-03](SOURCE_FINDINGS_AND_CONFLICTS.md:698), [ALS-04](SOURCE_FINDINGS_AND_CONFLICTS.md:699), [ALS-05](SOURCE_FINDINGS_AND_CONFLICTS.md:700), [ALS-06](SOURCE_FINDINGS_AND_CONFLICTS.md:701), [NYA-01](SOURCE_FINDINGS_AND_CONFLICTS.md:709), [NYA-02](SOURCE_FINDINGS_AND_CONFLICTS.md:710), [NYA-03](SOURCE_FINDINGS_AND_CONFLICTS.md:711), [NYA-04](SOURCE_FINDINGS_AND_CONFLICTS.md:712), [NYA-05](SOURCE_FINDINGS_AND_CONFLICTS.md:713), [NYA-06](SOURCE_FINDINGS_AND_CONFLICTS.md:714), [SRE-01](SOURCE_FINDINGS_AND_CONFLICTS.md:722), [SRE-02](SOURCE_FINDINGS_AND_CONFLICTS.md:723), [SRE-03](SOURCE_FINDINGS_AND_CONFLICTS.md:724), [SRE-04](SOURCE_FINDINGS_AND_CONFLICTS.md:725), [SRE-05](SOURCE_FINDINGS_AND_CONFLICTS.md:726), [SRE-06](SOURCE_FINDINGS_AND_CONFLICTS.md:727), [SRE-07](SOURCE_FINDINGS_AND_CONFLICTS.md:728), [TBR-01](SOURCE_FINDINGS_AND_CONFLICTS.md:736), [TBR-02](SOURCE_FINDINGS_AND_CONFLICTS.md:737), [TBR-03](SOURCE_FINDINGS_AND_CONFLICTS.md:738), [TBR-04](SOURCE_FINDINGS_AND_CONFLICTS.md:739), [TBR-05](SOURCE_FINDINGS_AND_CONFLICTS.md:740), [TBR-06](SOURCE_FINDINGS_AND_CONFLICTS.md:741), [TBR-07](SOURCE_FINDINGS_AND_CONFLICTS.md:742), [OBT-01](SOURCE_FINDINGS_AND_CONFLICTS.md:750), [OBT-02](SOURCE_FINDINGS_AND_CONFLICTS.md:751), [OBT-03](SOURCE_FINDINGS_AND_CONFLICTS.md:752), [OBT-04](SOURCE_FINDINGS_AND_CONFLICTS.md:753), [OBT-05](SOURCE_FINDINGS_AND_CONFLICTS.md:754), [OBT-06](SOURCE_FINDINGS_AND_CONFLICTS.md:755), [OBT-07](SOURCE_FINDINGS_AND_CONFLICTS.md:756), [OBT-08](SOURCE_FINDINGS_AND_CONFLICTS.md:757), [OBT-09](SOURCE_FINDINGS_AND_CONFLICTS.md:758), [OBT-10](SOURCE_FINDINGS_AND_CONFLICTS.md:759), [AUT-01](SOURCE_FINDINGS_AND_CONFLICTS.md:767), [AUT-02](SOURCE_FINDINGS_AND_CONFLICTS.md:768), [AUT-03](SOURCE_FINDINGS_AND_CONFLICTS.md:769), [AUT-04](SOURCE_FINDINGS_AND_CONFLICTS.md:770), [AUT-05](SOURCE_FINDINGS_AND_CONFLICTS.md:771), [AUT-06](SOURCE_FINDINGS_AND_CONFLICTS.md:772), [AUT-07](SOURCE_FINDINGS_AND_CONFLICTS.md:773), [AUT-08](SOURCE_FINDINGS_AND_CONFLICTS.md:774), [AUT-09](SOURCE_FINDINGS_AND_CONFLICTS.md:775), [AUT-10](SOURCE_FINDINGS_AND_CONFLICTS.md:776), [AUT-11](SOURCE_FINDINGS_AND_CONFLICTS.md:777).

**Conversation upgrade lineage.** [DTM-A16](SOURCE_FINDINGS_AND_CONFLICTS.md:74), [DRF-A27](SOURCE_FINDINGS_AND_CONFLICTS.md:468). Read the full rows and their original conversation references; [the recheck](CONVERSATION_RECHECK.md) preserves the exact unit/exception routes.

<a id="up-p04-reentry"></a>
#### P04.REENTRY — Idea lifetime and cumulative risk

[Existing definition, target and P0–P7](experiments/P.md#p04-reentry) remain binding.

**Specific upgrade scope.** Add evidence novelty, replenishment and pressure history to each exact parent-idea/visit state.

**Local comparison.** Compare no retry, source attempt caps and novelty-conditioned value with shared cumulative idea/day budgets.

**Additional cases.** New ID same evidence; losing trade followed by real refresh; prior win with no new support; sparse later visit.

<a id="up-p05"></a>
### UP-P05 — Event replay and passive-fill uncertainty

Parent: [P05](components/POLICY_EXECUTION_RISK.md); [local phases](experiments/P.md#p05); [definition refinement](SYSTEM_REFINEMENT.md#sr-p05). Upgrade role: `research_method`.

**Starting idea.** Assume a touch fills the order.

**Existing improvement path.** Venue/information clocks, marketable reference fills and passive uncertainty scenarios.

**Remaining weakness.** Independent optimistic/pessimistic assignments can create impossible comparisons among policies sharing one market path.

**Further upgrade.** Build coupled admissible fill scenarios with explicit latent queue/priority assumptions and common venue paths. Report partially identified economic ranges across the registered scenario set, preserving policy occupancy and order races; add telemetry-calibrated probabilities only when eligible observations exist.

**Fair comparison.** Marketable baseline, independent passive bounds and coupled feasible-scenario bounds; later telemetry-calibrated model when supported.

**Evidence.** Width of economic uncertainty, fill/markout calibration on supported cohorts, ordering consistency and policy robustness.

**Additional local cases to implement.** Competing orders cannot both receive the same scarce execution; cancel race; queue reset; insufficient depth; shared path with different occupancy.

**Decision or system use.** Distinguish promising policies robust to available fill uncertainty from ones requiring better execution evidence.

**Exact reviewed source clauses.** [JTR-15](SOURCE_FINDINGS_AND_CONFLICTS.md:32), [JTR-16](SOURCE_FINDINGS_AND_CONFLICTS.md:33), [DTM-A02](SOURCE_FINDINGS_AND_CONFLICTS.md:60), [DTM-A15](SOURCE_FINDINGS_AND_CONFLICTS.md:73), [DTM-A16](SOURCE_FINDINGS_AND_CONFLICTS.md:74), [JCV-U03](SOURCE_FINDINGS_AND_CONFLICTS.md:156), [JCV-U06](SOURCE_FINDINGS_AND_CONFLICTS.md:159), [JCV-A02](SOURCE_FINDINGS_AND_CONFLICTS.md:161), [JCV-A03](SOURCE_FINDINGS_AND_CONFLICTS.md:162), [JCV-A07](SOURCE_FINDINGS_AND_CONFLICTS.md:166), [JCV-A09](SOURCE_FINDINGS_AND_CONFLICTS.md:168), [CEX-02](SOURCE_FINDINGS_AND_CONFLICTS.md:184), [CRL-02](SOURCE_FINDINGS_AND_CONFLICTS.md:218), [DM7-01](SOURCE_FINDINGS_AND_CONFLICTS.md:357), [DM7-02](SOURCE_FINDINGS_AND_CONFLICTS.md:358), [DM7-03](SOURCE_FINDINGS_AND_CONFLICTS.md:359), [DM7-04](SOURCE_FINDINGS_AND_CONFLICTS.md:360), [DM7-05](SOURCE_FINDINGS_AND_CONFLICTS.md:361), [FP8-02](SOURCE_FINDINGS_AND_CONFLICTS.md:370), [RFE-01](SOURCE_FINDINGS_AND_CONFLICTS.md:602), [RFE-02](SOURCE_FINDINGS_AND_CONFLICTS.md:603), [RFE-03](SOURCE_FINDINGS_AND_CONFLICTS.md:604), [RFE-04](SOURCE_FINDINGS_AND_CONFLICTS.md:605), [RFE-05](SOURCE_FINDINGS_AND_CONFLICTS.md:606), [RFE-06](SOURCE_FINDINGS_AND_CONFLICTS.md:607), [RFE-07](SOURCE_FINDINGS_AND_CONFLICTS.md:608), [RFE-08](SOURCE_FINDINGS_AND_CONFLICTS.md:609), [RFE-09](SOURCE_FINDINGS_AND_CONFLICTS.md:610), [RFE-10](SOURCE_FINDINGS_AND_CONFLICTS.md:611), [RFE-11](SOURCE_FINDINGS_AND_CONFLICTS.md:612), [RFE-12](SOURCE_FINDINGS_AND_CONFLICTS.md:613), [RFE-13](SOURCE_FINDINGS_AND_CONFLICTS.md:614), [RFE-14](SOURCE_FINDINGS_AND_CONFLICTS.md:615), [SRE-01](SOURCE_FINDINGS_AND_CONFLICTS.md:722), [SRE-02](SOURCE_FINDINGS_AND_CONFLICTS.md:723), [SRE-03](SOURCE_FINDINGS_AND_CONFLICTS.md:724), [SRE-04](SOURCE_FINDINGS_AND_CONFLICTS.md:725), [SRE-05](SOURCE_FINDINGS_AND_CONFLICTS.md:726), [SRE-06](SOURCE_FINDINGS_AND_CONFLICTS.md:727), [SRE-07](SOURCE_FINDINGS_AND_CONFLICTS.md:728).

**Conversation upgrade lineage.** [DTM-A16](SOURCE_FINDINGS_AND_CONFLICTS.md:74), [JCV-U03](SOURCE_FINDINGS_AND_CONFLICTS.md:156), [JCV-A02](SOURCE_FINDINGS_AND_CONFLICTS.md:161), [CEX-02](SOURCE_FINDINGS_AND_CONFLICTS.md:184), [CRL-02](SOURCE_FINDINGS_AND_CONFLICTS.md:218). Read the full rows and their original conversation references; [the recheck](CONVERSATION_RECHECK.md) preserves the exact unit/exception routes.

<a id="up-p05-clocks"></a>
#### P05.CLOCKS — Venue arrival versus information time

[Existing definition, target and P0–P7](experiments/P.md#p05-clocks) remain binding.

**Specific upgrade scope.** Evaluate all execution variants on shared venue paths while keeping strategy information and order-arrival clocks separate.

**Local comparison.** Compare standing-quote arrival fills and latency scenarios; never wait artificially for the next quote update.

**Additional cases.** Venue event not yet received; order arrives before next update; source delay differs from outbound delay.

<a id="up-p05-passive"></a>
#### P05.PASSIVE — Passive fill and adverse-selection uncertainty

[Existing definition, target and P0–P7](experiments/P.md#p05-passive) remain binding.

**Specific upgrade scope.** Use coupled admissible queue/fill scenarios and later telemetry-calibrated probabilities only where observed support permits.

**Local comparison.** Compare marketable reference, touch/trade-through bounds and joint economic ranges including occupancy/races.

**Additional cases.** Two policies compete for same execution; cancel unknown; insufficient size; hidden queue state.

<a id="up-p06"></a>
### UP-P06 — Routing, latency, cost and adverse-selection experts

Parent: [P06](components/POLICY_EXECUTION_RISK.md); [local phases](experiments/P.md#p06); [definition refinement](SYSTEM_REFINEMENT.md#sr-p06). Upgrade role: `forecast`.

**Starting idea.** Subtract a fixed spread and commission.

**Existing improvement path.** Itemized shortfall, latency, adverse selection and route-conditioned cost models.

**Remaining weakness.** Mean costs obscure joint tails of delay, fill and adverse movement precisely when a signal looks strongest.

**Further upgrade.** Fit a compact joint execution outcome law for fill/no-fill, elapsed time, shortfall and subsequent markout conditional on route and observable state. Compare state-conditioned quantile/competing-risk models with conservative tables; separate controllable route effects from unsupported counterfactual claims.

**Fair comparison.** Fixed conservative cost, spread/pace table, existing cost regression and joint outcome model on matched eligible data.

**Evidence.** Joint/quantile loss, tail coverage, net after route choice, robustness to latency stress and additional data value.

**Additional local cases to implement.** Fast market widens spread and delay together; passive fill selects adverse paths; crossed venue; fee version changes.

**Decision or system use.** Price the full execution tradeoff and favor routes whose advantage survives observed support and cost uncertainty.

**Exact reviewed source clauses.** [JTR-15](SOURCE_FINDINGS_AND_CONFLICTS.md:32), [DTM-A10](SOURCE_FINDINGS_AND_CONFLICTS.md:68), [CEX-15](SOURCE_FINDINGS_AND_CONFLICTS.md:197), [CRL-09](SOURCE_FINDINGS_AND_CONFLICTS.md:225), [FP8-02](SOURCE_FINDINGS_AND_CONFLICTS.md:370).

**Conversation upgrade lineage.** [JCV-U03](SOURCE_FINDINGS_AND_CONFLICTS.md:156), [JCV-A03](SOURCE_FINDINGS_AND_CONFLICTS.md:162), [CEX-15](SOURCE_FINDINGS_AND_CONFLICTS.md:197), [CRL-09](SOURCE_FINDINGS_AND_CONFLICTS.md:225). Read the full rows and their original conversation references; [the recheck](CONVERSATION_RECHECK.md) preserves the exact unit/exception routes.

<a id="up-p06-shortfall"></a>
#### P06.SHORTFALL — Cost and latency specialists

[Existing definition, target and P0–P7](experiments/P.md#p06-shortfall) remain binding.

**Specific upgrade scope.** Fit joint fill/delay/shortfall/markout distributions conditional on permitted route and supported observable state.

**Local comparison.** Compare fixed conservative costs, state tables and joint quantile/competing-risk models with separate fee/spread accounting.

**Additional cases.** Delay and volatility rise together; passive adverse selection; fee version change; counterfactual route unsupported.

<a id="up-p07"></a>
### UP-P07 — Broker order state, idempotency and reconciliation

Parent: [P07](components/POLICY_EXECUTION_RISK.md); [local phases](experiments/P.md#p07); [definition refinement](SYSTEM_REFINEMENT.md#sr-p07). Upgrade role: `engineering`.

**Starting idea.** Send, cancel and retry orders based on acknowledgments.

**Existing improvement path.** Durable idempotent state machine, broker reconciliation and unknown states.

**Remaining weakness.** Rare interleavings and restart boundaries can evade a few happy-path replay cases.

**Further upgrade.** Specify a bounded protocol model with invariants and exhaustively enumerate short event interleavings, then replay generated traces through the reference reducer and adapter. Test durable intent/outbox checkpoints, duplicate acknowledgments and reconciliation; external exactly-once behavior is conditional on verified broker capabilities.

**Fair comparison.** Handwritten scenarios versus model-generated trace corpus and adapter/reference replay.

**Evidence.** Invariant failures, reachable unknown-state recovery, duplicate external intent risk and time to reconcile.

**Additional local cases to implement.** Crash between persist/send; late fill after cancel; duplicated/reordered ack; non-atomic OCO; broker snapshot older than fill.

**Decision or system use.** Strengthen deterministic order safety and recovery as the number of allowed policy actions grows.

**Exact reviewed source clauses.** [JTR-15](SOURCE_FINDINGS_AND_CONFLICTS.md:32), [DTM-A01](SOURCE_FINDINGS_AND_CONFLICTS.md:59).

<a id="up-p07-idempotency"></a>
#### P07.IDEMPOTENCY — Order and broker reconciliation

[Existing definition, target and P0–P7](experiments/P.md#p07-idempotency) remain binding.

**Specific upgrade scope.** Generate bounded interleaving/restart traces from an explicit durable order protocol and verified broker semantics.

**Local comparison.** Compare reference reducer and adapter against invariants; external exactly-once claims require actual broker capability.

**Additional cases.** Crash between persist/send; duplicate ack; late fill; stale broker snapshot; non-atomic OCO.

<a id="up-p08"></a>
### UP-P08 — Independent daily USD risk and pre-trade reservations

Parent: [P08](components/POLICY_EXECUTION_RISK.md); [local phases](experiments/P.md#p08); [definition refinement](SYSTEM_REFINEMENT.md#sr-p08). Upgrade role: `engineering`.

**Starting idea.** Stop trading after realized loss reaches a threshold.

**Existing improvement path.** Liquidation-based headroom, remaining adverse reserve and atomic pending-exposure accounting.

**Remaining weakness.** Blind summation wastes headroom, while incompatible favorable offsets or missed races underreserve it.

**Further upgrade.** Enumerate feasible near-term order/fill/cancel states and calculate incremental loss reserve on each state using a shared scenario tree. Compare the maximum valid reserve with a conservative additive reference; offsets require an enforceable relationship, and market gaps retain explicit stress uncertainty.

**Fair comparison.** Additive reference versus feasible-state reserve engine on identical positions, fees, order semantics and stress envelopes.

**Evidence.** Zero reserve omissions in enumerated cases, feasible opportunity retention, compute latency and breach outcomes under stress.

**Additional local cases to implement.** Entry and protective order race; cancel unconfirmed; already marked loss; fee accrued once; apparently offsetting orders both increase exposure.

**Decision or system use.** Use scarce one-mini risk headroom more precisely without weakening the independent daily/firm veto.

**Exact reviewed source clauses.** [JTR-14](SOURCE_FINDINGS_AND_CONFLICTS.md:31), [JTR-15](SOURCE_FINDINGS_AND_CONFLICTS.md:32), [JTR-24](SOURCE_FINDINGS_AND_CONFLICTS.md:41), [DTM-A01](SOURCE_FINDINGS_AND_CONFLICTS.md:59), [DTM-A08](SOURCE_FINDINGS_AND_CONFLICTS.md:66), [DTM-A16](SOURCE_FINDINGS_AND_CONFLICTS.md:74), [CEX-08](SOURCE_FINDINGS_AND_CONFLICTS.md:190), [VX4-04](SOURCE_FINDINGS_AND_CONFLICTS.md:327), [VX4-08](SOURCE_FINDINGS_AND_CONFLICTS.md:331), [CD2-01](SOURCE_FINDINGS_AND_CONFLICTS.md:399), [CD2-02](SOURCE_FINDINGS_AND_CONFLICTS.md:400), [CD2-03](SOURCE_FINDINGS_AND_CONFLICTS.md:401), [CD2-04](SOURCE_FINDINGS_AND_CONFLICTS.md:402), [CD2-05](SOURCE_FINDINGS_AND_CONFLICTS.md:403), [CD3-01](SOURCE_FINDINGS_AND_CONFLICTS.md:404), [CD3-02](SOURCE_FINDINGS_AND_CONFLICTS.md:405), [CD3-03](SOURCE_FINDINGS_AND_CONFLICTS.md:406), [CD3-04](SOURCE_FINDINGS_AND_CONFLICTS.md:407), [CD3-05](SOURCE_FINDINGS_AND_CONFLICTS.md:408), [DEN-05](SOURCE_FINDINGS_AND_CONFLICTS.md:413), [EMO-01](SOURCE_FINDINGS_AND_CONFLICTS.md:481), [EMO-02](SOURCE_FINDINGS_AND_CONFLICTS.md:482), [EMO-03](SOURCE_FINDINGS_AND_CONFLICTS.md:483), [EMO-04](SOURCE_FINDINGS_AND_CONFLICTS.md:484), [GXF-13](SOURCE_FINDINGS_AND_CONFLICTS.md:497), [RFE-11](SOURCE_FINDINGS_AND_CONFLICTS.md:612), [RFE-12](SOURCE_FINDINGS_AND_CONFLICTS.md:613), [OFM-08](SOURCE_FINDINGS_AND_CONFLICTS.md:630), [K18-05](SOURCE_FINDINGS_AND_CONFLICTS.md:656), [F23-05](SOURCE_FINDINGS_AND_CONFLICTS.md:671), [ALS-01](SOURCE_FINDINGS_AND_CONFLICTS.md:696), [ALS-02](SOURCE_FINDINGS_AND_CONFLICTS.md:697), [ALS-03](SOURCE_FINDINGS_AND_CONFLICTS.md:698), [ALS-04](SOURCE_FINDINGS_AND_CONFLICTS.md:699), [ALS-05](SOURCE_FINDINGS_AND_CONFLICTS.md:700), [ALS-06](SOURCE_FINDINGS_AND_CONFLICTS.md:701), [SRE-06](SOURCE_FINDINGS_AND_CONFLICTS.md:727), [AUT-01](SOURCE_FINDINGS_AND_CONFLICTS.md:767), [AUT-02](SOURCE_FINDINGS_AND_CONFLICTS.md:768), [AUT-03](SOURCE_FINDINGS_AND_CONFLICTS.md:769), [AUT-04](SOURCE_FINDINGS_AND_CONFLICTS.md:770), [AUT-05](SOURCE_FINDINGS_AND_CONFLICTS.md:771), [AUT-06](SOURCE_FINDINGS_AND_CONFLICTS.md:772), [AUT-07](SOURCE_FINDINGS_AND_CONFLICTS.md:773), [AUT-08](SOURCE_FINDINGS_AND_CONFLICTS.md:774), [AUT-09](SOURCE_FINDINGS_AND_CONFLICTS.md:775), [AUT-10](SOURCE_FINDINGS_AND_CONFLICTS.md:776), [AUT-11](SOURCE_FINDINGS_AND_CONFLICTS.md:777).

**Conversation upgrade lineage.** [DTM-A08](SOURCE_FINDINGS_AND_CONFLICTS.md:66), [DTM-A16](SOURCE_FINDINGS_AND_CONFLICTS.md:74). Read the full rows and their original conversation references; [the recheck](CONVERSATION_RECHECK.md) preserves the exact unit/exception routes.

<a id="up-p08-reservation"></a>
#### P08.RESERVATION — Daily loss and atomic risk reserve

[Existing definition, target and P0–P7](experiments/P.md#p08-reservation) remain binding.

**Specific upgrade scope.** Enumerate feasible pending-order states and compute worst incremental reserve within each registered stress scenario.

**Local comparison.** Compare feasible-state engine with conservative additive reference without allowing unenforceable favorable offsets.

**Additional cases.** Already marked loss; accrued fee once; cancel race; entry and stop both working; gap exceeds model envelope.

<a id="up-p09"></a>
### UP-P09 — Firm product and account lifecycle constraints

Parent: [P09](components/POLICY_EXECUTION_RISK.md); [local phases](experiments/P.md#p09); [definition refinement](SYSTEM_REFINEMENT.md#sr-p09). Upgrade role: `engineering`.

**Starting idea.** Treat a funded account as a fixed profit target and loss limit.

**Existing improvement path.** Versioned product/account state machines and exact rule scenarios.

**Remaining weakness.** Separate handwritten rule calculations can diverge across research, monitoring and cash reports.

**Further upgrade.** Represent product rules as typed balance functions, calendar predicates and lifecycle transitions with an evaluation trace. Compile the same definition into reference account replay and runtime checks; include effective-version and unknown-term handling. Any commercial comparison uses verified current terms at its actual decision time.

**Fair comparison.** Hand-calculated paths and existing engine versus compiled rule definitions with independent arithmetic fixtures.

**Evidence.** Rule parity, explanation coverage, update impact, lifecycle/cash reconciliation and unsupported-term detection.

**Additional local cases to implement.** Trailing floor locks; pending payout affects headroom; rule changes by purchase date; holiday boundary; failed account retained.

**Decision or system use.** Make product feasibility and breach reasons reproducible without letting a learned strategy reinterpret account rules.

**Exact reviewed source clauses.** [DTM-A08](SOURCE_FINDINGS_AND_CONFLICTS.md:66), [DTM-A16](SOURCE_FINDINGS_AND_CONFLICTS.md:74), [JXA-11](SOURCE_FINDINGS_AND_CONFLICTS.md:110), [CEX-08](SOURCE_FINDINGS_AND_CONFLICTS.md:190), [CD2-01](SOURCE_FINDINGS_AND_CONFLICTS.md:399), [CD2-02](SOURCE_FINDINGS_AND_CONFLICTS.md:400), [CD2-03](SOURCE_FINDINGS_AND_CONFLICTS.md:401), [CD2-04](SOURCE_FINDINGS_AND_CONFLICTS.md:402), [CD2-05](SOURCE_FINDINGS_AND_CONFLICTS.md:403), [RFE-11](SOURCE_FINDINGS_AND_CONFLICTS.md:612), [RFE-12](SOURCE_FINDINGS_AND_CONFLICTS.md:613), [RFE-13](SOURCE_FINDINGS_AND_CONFLICTS.md:614), [OFM-08](SOURCE_FINDINGS_AND_CONFLICTS.md:630), [K10-01](SOURCE_FINDINGS_AND_CONFLICTS.md:639), [K10-06](SOURCE_FINDINGS_AND_CONFLICTS.md:644), [K18-01](SOURCE_FINDINGS_AND_CONFLICTS.md:652), [K18-08](SOURCE_FINDINGS_AND_CONFLICTS.md:659), [F23-01](SOURCE_FINDINGS_AND_CONFLICTS.md:667), [F23-06](SOURCE_FINDINGS_AND_CONFLICTS.md:672), [F23-07](SOURCE_FINDINGS_AND_CONFLICTS.md:673), [CCS-04](SOURCE_FINDINGS_AND_CONFLICTS.md:684), [NYA-06](SOURCE_FINDINGS_AND_CONFLICTS.md:714), [SRE-06](SOURCE_FINDINGS_AND_CONFLICTS.md:727), [OBT-10](SOURCE_FINDINGS_AND_CONFLICTS.md:759), [AUT-01](SOURCE_FINDINGS_AND_CONFLICTS.md:767), [AUT-02](SOURCE_FINDINGS_AND_CONFLICTS.md:768), [AUT-03](SOURCE_FINDINGS_AND_CONFLICTS.md:769), [AUT-04](SOURCE_FINDINGS_AND_CONFLICTS.md:770), [AUT-05](SOURCE_FINDINGS_AND_CONFLICTS.md:771), [AUT-06](SOURCE_FINDINGS_AND_CONFLICTS.md:772), [AUT-07](SOURCE_FINDINGS_AND_CONFLICTS.md:773), [AUT-08](SOURCE_FINDINGS_AND_CONFLICTS.md:774), [AUT-09](SOURCE_FINDINGS_AND_CONFLICTS.md:775), [AUT-10](SOURCE_FINDINGS_AND_CONFLICTS.md:776), [AUT-11](SOURCE_FINDINGS_AND_CONFLICTS.md:777).

**Conversation upgrade lineage.** [CEX-08](SOURCE_FINDINGS_AND_CONFLICTS.md:190). Read the full rows and their original conversation references; [the recheck](CONVERSATION_RECHECK.md) preserves the exact unit/exception routes.

<a id="up-p09-account_paths"></a>
#### P09.ACCOUNT_PATHS — Product lifecycle and rule scenarios

[Existing definition, target and P0–P7](experiments/P.md#p09-account_paths) remain binding.

**Specific upgrade scope.** Compile versioned balance functions, time predicates and lifecycle transitions into one traced rule definition.

**Local comparison.** Compare hand-calculated, reference and runtime account/cash paths across each selected product scenario.

**Additional cases.** Trailing floor locks; pending payout; purchase-date terms; failed account remains in cash ledger.

<a id="up-p10"></a>
### UP-P10 — Day boundary, outage and emergency flattening

Parent: [P10](components/POLICY_EXECUTION_RISK.md); [local phases](experiments/P.md#p10); [definition refinement](SYSTEM_REFINEMENT.md#sr-p10). Upgrade role: `engineering`.

**Starting idea.** Flatten a fixed number of minutes before close.

**Existing improvement path.** Independent boundary timers, actual remaining horizons and conservative cancel/flatten buffers.

**Remaining weakness.** A single fixed buffer ignores route-specific tail latency and the time needed to discover and reconcile unknown orders.

**Further upgrade.** Build a deadline-budget controller that allocates time to cancel, reconcile, flatten and verify. Compare fixed conservative buffers with measured conditional latency quantiles and bounded retry plans; choose latest permitted entry from the complete boundary-truncated plan. Missing telemetry uses the registered conservative fallback.

**Fair comparison.** Fixed buffer versus conditional deadline budget under identical required cutoff and fault scenarios.

**Evidence.** Flat/no-live-order verification time, missed cutoff frequency in simulation, final-period opportunity value and safety margin.

**Additional local cases to implement.** No ticks near cutoff; cancel timeout; reconnect; halt; early close; high latency correlated with volatility.

**Decision or system use.** Retain eligible late opportunities only when the full exit/reconciliation plan fits the mandatory boundary budget.

**Exact reviewed source clauses.** [CEX-08](SOURCE_FINDINGS_AND_CONFLICTS.md:190).

**Conversation upgrade lineage.** [CEX-08](SOURCE_FINDINGS_AND_CONFLICTS.md:190). Read the full rows and their original conversation references; [the recheck](CONVERSATION_RECHECK.md) preserves the exact unit/exception routes.

<a id="up-p10-remainder"></a>
#### P10.REMAINDER — Boundary-truncated opportunity and flattening

[Existing definition, target and P0–P7](experiments/P.md#p10-remainder) remain binding.

**Specific upgrade scope.** Allocate deadline time to cancel, reconcile, flatten and verify, with actual remainder forecasts.

**Local comparison.** Compare conservative fixed buffer and supported conditional latency budgets under unchanged mandatory cutoff.

**Additional cases.** No ticks; early close; reconnect; halt; cancel timeout; last eligible opportunity.

<a id="up-p11"></a>
### UP-P11 — Trading net, business cash and objective accounting

Parent: [P11](components/POLICY_EXECUTION_RISK.md); [local phases](experiments/P.md#p11); [definition refinement](SYSTEM_REFINEMENT.md#sr-p11). Upgrade role: `decision`.

**Starting idea.** Judge the target from winning trades or displayed funded P&L.

**Existing improvement path.** All eligible-day trading net, separate cash ledgers, fees, failed accounts and payout states.

**Remaining weakness.** A mean result alone hides whether the gap to the objective comes from signal value, risk feasibility, inactivity or cash restrictions.

**Further upgrade.** Add an auditable objective-feasibility decomposition and scenario frontier: opportunity count, budget-fit rate, selected trade value, zero-trade days, tail breaches, business costs and payout timing. Preserve common chronological account paths and uncertain product inputs; report the $2,000 goal on both accounting bases until specified.

**Fair comparison.** Simple daily mean versus complete trading/account/cash path reports with paired assumptions and uncertainty.

**Evidence.** Mean net per eligible day, distribution of cash timing, drawdown/breach frequency, objective shortfall decomposition and unresolved inputs.

**Additional local cases to implement.** Many profitable days but no payout; failed attempts incur fees; long no-trade periods; fee timing differs from P&L; exceptional day dominates mean.

**Decision or system use.** Show what would have to improve for the one-account objective to be supported, without treating the target as a reason to chase losses.

**Exact reviewed source clauses.** [DTM-A08](SOURCE_FINDINGS_AND_CONFLICTS.md:66), [JXA-24](SOURCE_FINDINGS_AND_CONFLICTS.md:123), [JCV-A10](SOURCE_FINDINGS_AND_CONFLICTS.md:169), [RFE-11](SOURCE_FINDINGS_AND_CONFLICTS.md:612), [RFE-12](SOURCE_FINDINGS_AND_CONFLICTS.md:613), [RFE-13](SOURCE_FINDINGS_AND_CONFLICTS.md:614), [OFM-08](SOURCE_FINDINGS_AND_CONFLICTS.md:630), [K10-01](SOURCE_FINDINGS_AND_CONFLICTS.md:639), [K10-06](SOURCE_FINDINGS_AND_CONFLICTS.md:644), [K18-01](SOURCE_FINDINGS_AND_CONFLICTS.md:652), [K18-08](SOURCE_FINDINGS_AND_CONFLICTS.md:659), [F23-01](SOURCE_FINDINGS_AND_CONFLICTS.md:667), [F23-06](SOURCE_FINDINGS_AND_CONFLICTS.md:672), [F23-07](SOURCE_FINDINGS_AND_CONFLICTS.md:673), [CCS-01](SOURCE_FINDINGS_AND_CONFLICTS.md:681), [CCS-04](SOURCE_FINDINGS_AND_CONFLICTS.md:684), [NYA-01](SOURCE_FINDINGS_AND_CONFLICTS.md:709), [NYA-02](SOURCE_FINDINGS_AND_CONFLICTS.md:710), [NYA-03](SOURCE_FINDINGS_AND_CONFLICTS.md:711), [NYA-04](SOURCE_FINDINGS_AND_CONFLICTS.md:712), [NYA-05](SOURCE_FINDINGS_AND_CONFLICTS.md:713), [NYA-06](SOURCE_FINDINGS_AND_CONFLICTS.md:714), [TBR-06](SOURCE_FINDINGS_AND_CONFLICTS.md:741), [OBT-10](SOURCE_FINDINGS_AND_CONFLICTS.md:759), [AUT-01](SOURCE_FINDINGS_AND_CONFLICTS.md:767), [AUT-02](SOURCE_FINDINGS_AND_CONFLICTS.md:768), [AUT-03](SOURCE_FINDINGS_AND_CONFLICTS.md:769), [AUT-04](SOURCE_FINDINGS_AND_CONFLICTS.md:770), [AUT-05](SOURCE_FINDINGS_AND_CONFLICTS.md:771), [AUT-06](SOURCE_FINDINGS_AND_CONFLICTS.md:772), [AUT-07](SOURCE_FINDINGS_AND_CONFLICTS.md:773), [AUT-08](SOURCE_FINDINGS_AND_CONFLICTS.md:774), [AUT-09](SOURCE_FINDINGS_AND_CONFLICTS.md:775), [AUT-10](SOURCE_FINDINGS_AND_CONFLICTS.md:776), [AUT-11](SOURCE_FINDINGS_AND_CONFLICTS.md:777).

**Conversation upgrade lineage.** [DTM-A08](SOURCE_FINDINGS_AND_CONFLICTS.md:66). Read the full rows and their original conversation references; [the recheck](CONVERSATION_RECHECK.md) preserves the exact unit/exception routes.

<a id="up-p11-cash"></a>
#### P11.CASH — Trading net versus business cash

[Existing definition, target and P0–P7](experiments/P.md#p11-cash) remain binding.

**Specific upgrade scope.** Add objective-feasibility decomposition across opportunities, budget fit, net trade value, inactivity, failed fees and cash timing.

**Local comparison.** Compare both accounting bases and full chronological account scenarios, including zero-trade days and uncertainty.

**Additional cases.** Displayed profit no payout; exceptional day dominates mean; fees before payout; many inactive days.

<a id="up-p12"></a>
### UP-P12 — Execution-instrument research selection

Parent: [P12](components/POLICY_EXECUTION_RISK.md); [local phases](experiments/P.md#p12); [definition refinement](SYSTEM_REFINEMENT.md#sr-p12). Upgrade role: `decision`.

**Starting idea.** Prefer the market that moves more points.

**Existing improvement path.** Matched-date one-mini NQ/ES comparisons under identical constraints and frozen selection.

**Remaining weakness.** Raw net averages can hide which market loses opportunities because one mini cannot fit the same USD budget or execution conditions.

**Further upgrade.** Build risk-budget-compatible opportunity curves by instrument, decomposing information quality, structural stop feasibility, route costs, frequency and occupancy. Compare fixed NQ/ES and development-selected policies using paired dates and common uncertainty; any intraday selector remains a separately evaluated flat-confirmed policy.

**Fair comparison.** Always NQ, always ES, existing development choice and feasibility-aware selection with the same scope and trial budget.

**Evidence.** Net/day and paired uncertainty, budget-fit coverage, tail loss, fees/latency sensitivity and objective feasibility.

**Additional local cases to implement.** NQ stronger forecast but no affordable structural stop; ES lower costs but fewer useful moves; unequal data dates; selection after seeing outer test.

**Decision or system use.** Choose the actual one-mini instrument on constrained economic opportunity, preserving NQ preference under the registered noninferiority rule.

**Exact reviewed source clauses.** [CEX-12](SOURCE_FINDINGS_AND_CONFLICTS.md:194), [TP3-04](SOURCE_FINDINGS_AND_CONFLICTS.md:313), [TBR-06](SOURCE_FINDINGS_AND_CONFLICTS.md:741).

**Conversation upgrade lineage.** [CEX-12](SOURCE_FINDINGS_AND_CONFLICTS.md:194). Read the full rows and their original conversation references; [the recheck](CONVERSATION_RECHECK.md) preserves the exact unit/exception routes.

<a id="up-p12-fair_instrument"></a>
#### P12.FAIR_INSTRUMENT — NQ versus ES research selection

[Existing definition, target and P0–P7](experiments/P.md#p12-fair_instrument) remain binding.

**Specific upgrade scope.** Compare actual one-mini budget-fit opportunity frontiers, separating information, structural feasibility and execution cost.

**Local comparison.** Use paired eligible dates, frozen development selection and the registered NQ preference rule; any intraday selector is separate.

**Additional cases.** NQ stronger forecast unaffordable stop; ES different frequency; unequal histories; test-selected instrument.

<a id="family-r"></a>
## Later Response

<a id="up-r01"></a>
### UP-R01 — Approach speed, aggression and progress

Parent: [R01](components/RESPONSE_DEFERRED.md); [local phases](experiments/R.md#r01); [definition refinement](SYSTEM_REFINEMENT.md#sr-r01). Upgrade role: `measurement`.

**Starting idea.** Call an approach fast or slow.

**Existing improvement path.** Causal approach episodes with speed, acceleration, signed effort, progress and pauses.

**Remaining weakness.** Absolute speed and volume mix normal session activity with unusual pressure at a particular distance from the level.

**Further upgrade.** Construct approach trajectories in distance-to-frozen-band, wall time and covered activity, with residual speed/effort relative to comparable session/distance states. Compare compact trajectory summaries and a shared event kernel; expose stop-start structure and direction changes rather than only an average.

**Fair comparison.** Fast/slow rules, raw summaries, exposure-normalized residual summaries and compact trajectory model.

**Evidence.** Approach-state reproducibility, conditional path loss, entry timing value and computation.

**Additional local cases to implement.** Long pause then burst; high normal opening activity; moving band; sparse tape; crossing from wrong side.

**Decision or system use.** Improve estimates of arrival quality and immediate-versus-wait decisions at every eligible location type.

**Exact reviewed source clauses.** [JCV-A06](SOURCE_FINDINGS_AND_CONFLICTS.md:165), [CRL-08](SOURCE_FINDINGS_AND_CONFLICTS.md:224), [CRL-14](SOURCE_FINDINGS_AND_CONFLICTS.md:230), [CRL-15](SOURCE_FINDINGS_AND_CONFLICTS.md:231), [DM5-01](SOURCE_FINDINGS_AND_CONFLICTS.md:348), [DM5-02](SOURCE_FINDINGS_AND_CONFLICTS.md:349), [DM5-03](SOURCE_FINDINGS_AND_CONFLICTS.md:350), [DM5-04](SOURCE_FINDINGS_AND_CONFLICTS.md:351), [FP8-05](SOURCE_FINDINGS_AND_CONFLICTS.md:373), [CD3-01](SOURCE_FINDINGS_AND_CONFLICTS.md:404), [CD3-02](SOURCE_FINDINGS_AND_CONFLICTS.md:405), [CD3-03](SOURCE_FINDINGS_AND_CONFLICTS.md:406), [CD3-04](SOURCE_FINDINGS_AND_CONFLICTS.md:407), [CD3-05](SOURCE_FINDINGS_AND_CONFLICTS.md:408), [WIC-01](SOURCE_FINDINGS_AND_CONFLICTS.md:577), [WIC-02](SOURCE_FINDINGS_AND_CONFLICTS.md:578), [WIC-03](SOURCE_FINDINGS_AND_CONFLICTS.md:579), [WIC-04](SOURCE_FINDINGS_AND_CONFLICTS.md:580), [WIC-05](SOURCE_FINDINGS_AND_CONFLICTS.md:581), [WIC-06](SOURCE_FINDINGS_AND_CONFLICTS.md:582), [WIC-07](SOURCE_FINDINGS_AND_CONFLICTS.md:583), [AUT-09](SOURCE_FINDINGS_AND_CONFLICTS.md:775).

**Conversation upgrade lineage.** [DTM-A12](SOURCE_FINDINGS_AND_CONFLICTS.md:70). Read the full rows and their original conversation references; [the recheck](CONVERSATION_RECHECK.md) preserves the exact unit/exception routes.

This parent has no separate named child; its own P0–P7 phases carry the full upgrade and source-clause obligations.

<a id="up-r02"></a>
### UP-R02 — High-effort stall and absorption proxy

Parent: [R02](components/RESPONSE_DEFERRED.md); [local phases](experiments/R.md#r02); [definition refinement](SYSTEM_REFINEMENT.md#sr-r02). Upgrade role: `forecast`.

**Starting idea.** High volume with little price movement means absorption.

**Existing improvement path.** Observable stall prefixes separated from later displacement and book evidence.

**Remaining weakness.** Large effort can be ordinary for the state, and the same stall can precede reversal or continuation.

**Further upgrade.** Estimate expected progress conditional on side-specific executed effort, spread, depth, activity and distance, then model the progress residual and its persistence. Keep print-only and book-supported channels separate; compare a joint effort/progress surface with the simple ratio and a transition hazard after the stall.

**Fair comparison.** Source ratio, normalized residual surface, additive transition model and bounded local sequence challenger.

**Evidence.** Conditional event/path loss, stall-versus-continuation calibration, net timing value and support.

**Additional local cases to implement.** Huge volume with normal low progress; missing book; unknown side; sustained hold eventually breaks; zero progress denominator.

**Decision or system use.** Identify unusual resistance to pressure and forecast its next branch without asserting hidden participant intent.

**Exact reviewed source clauses.** [JTR-20](SOURCE_FINDINGS_AND_CONFLICTS.md:37), [DTM-A12](SOURCE_FINDINGS_AND_CONFLICTS.md:70), [JXA-03](SOURCE_FINDINGS_AND_CONFLICTS.md:102), [JXA-13](SOURCE_FINDINGS_AND_CONFLICTS.md:112), [JXA-15](SOURCE_FINDINGS_AND_CONFLICTS.md:114), [JCV-A07](SOURCE_FINDINGS_AND_CONFLICTS.md:166), [CRL-07](SOURCE_FINDINGS_AND_CONFLICTS.md:223), [CRL-12](SOURCE_FINDINGS_AND_CONFLICTS.md:228), [CRL-13](SOURCE_FINDINGS_AND_CONFLICTS.md:229), [CRL-14](SOURCE_FINDINGS_AND_CONFLICTS.md:230), [VP2-05](SOURCE_FINDINGS_AND_CONFLICTS.md:302), [DM5-01](SOURCE_FINDINGS_AND_CONFLICTS.md:348), [DM5-02](SOURCE_FINDINGS_AND_CONFLICTS.md:349), [DM5-03](SOURCE_FINDINGS_AND_CONFLICTS.md:350), [DM5-04](SOURCE_FINDINGS_AND_CONFLICTS.md:351), [DM6-01](SOURCE_FINDINGS_AND_CONFLICTS.md:352), [DM6-02](SOURCE_FINDINGS_AND_CONFLICTS.md:353), [DM6-03](SOURCE_FINDINGS_AND_CONFLICTS.md:354), [DM6-04](SOURCE_FINDINGS_AND_CONFLICTS.md:355), [DM6-05](SOURCE_FINDINGS_AND_CONFLICTS.md:356), [DM7-01](SOURCE_FINDINGS_AND_CONFLICTS.md:357), [DM7-02](SOURCE_FINDINGS_AND_CONFLICTS.md:358), [DM7-03](SOURCE_FINDINGS_AND_CONFLICTS.md:359), [DM7-04](SOURCE_FINDINGS_AND_CONFLICTS.md:360), [DM7-05](SOURCE_FINDINGS_AND_CONFLICTS.md:361), [FP8-01](SOURCE_FINDINGS_AND_CONFLICTS.md:369), [FP8-02](SOURCE_FINDINGS_AND_CONFLICTS.md:370), [FP8-03](SOURCE_FINDINGS_AND_CONFLICTS.md:371), [FP8-04](SOURCE_FINDINGS_AND_CONFLICTS.md:372), [FP8-05](SOURCE_FINDINGS_AND_CONFLICTS.md:373), [CD3-01](SOURCE_FINDINGS_AND_CONFLICTS.md:404), [CD3-02](SOURCE_FINDINGS_AND_CONFLICTS.md:405), [CD3-03](SOURCE_FINDINGS_AND_CONFLICTS.md:406), [CD3-04](SOURCE_FINDINGS_AND_CONFLICTS.md:407), [CD3-05](SOURCE_FINDINGS_AND_CONFLICTS.md:408), [MAT-02](SOURCE_FINDINGS_AND_CONFLICTS.md:527), [MAT-03](SOURCE_FINDINGS_AND_CONFLICTS.md:528), [WIC-01](SOURCE_FINDINGS_AND_CONFLICTS.md:577), [WIC-02](SOURCE_FINDINGS_AND_CONFLICTS.md:578), [WIC-03](SOURCE_FINDINGS_AND_CONFLICTS.md:579), [WIC-04](SOURCE_FINDINGS_AND_CONFLICTS.md:580), [WIC-05](SOURCE_FINDINGS_AND_CONFLICTS.md:581), [WIC-06](SOURCE_FINDINGS_AND_CONFLICTS.md:582), [WIC-07](SOURCE_FINDINGS_AND_CONFLICTS.md:583), [YMA-01](SOURCE_FINDINGS_AND_CONFLICTS.md:589), [YMA-02](SOURCE_FINDINGS_AND_CONFLICTS.md:590), [YMA-03](SOURCE_FINDINGS_AND_CONFLICTS.md:591), [YMA-04](SOURCE_FINDINGS_AND_CONFLICTS.md:592), [YMA-05](SOURCE_FINDINGS_AND_CONFLICTS.md:593), [YMA-06](SOURCE_FINDINGS_AND_CONFLICTS.md:594), [K10-01](SOURCE_FINDINGS_AND_CONFLICTS.md:639), [K10-02](SOURCE_FINDINGS_AND_CONFLICTS.md:640), [K10-03](SOURCE_FINDINGS_AND_CONFLICTS.md:641), [K10-04](SOURCE_FINDINGS_AND_CONFLICTS.md:642), [K10-05](SOURCE_FINDINGS_AND_CONFLICTS.md:643), [K10-06](SOURCE_FINDINGS_AND_CONFLICTS.md:644), [F23-01](SOURCE_FINDINGS_AND_CONFLICTS.md:667), [F23-02](SOURCE_FINDINGS_AND_CONFLICTS.md:668), [F23-03](SOURCE_FINDINGS_AND_CONFLICTS.md:669), [F23-04](SOURCE_FINDINGS_AND_CONFLICTS.md:670), [F23-05](SOURCE_FINDINGS_AND_CONFLICTS.md:671), [F23-06](SOURCE_FINDINGS_AND_CONFLICTS.md:672), [F23-07](SOURCE_FINDINGS_AND_CONFLICTS.md:673), [OBT-01](SOURCE_FINDINGS_AND_CONFLICTS.md:750), [OBT-02](SOURCE_FINDINGS_AND_CONFLICTS.md:751), [OBT-03](SOURCE_FINDINGS_AND_CONFLICTS.md:752), [OBT-04](SOURCE_FINDINGS_AND_CONFLICTS.md:753), [OBT-05](SOURCE_FINDINGS_AND_CONFLICTS.md:754), [OBT-06](SOURCE_FINDINGS_AND_CONFLICTS.md:755), [OBT-07](SOURCE_FINDINGS_AND_CONFLICTS.md:756), [OBT-08](SOURCE_FINDINGS_AND_CONFLICTS.md:757), [OBT-09](SOURCE_FINDINGS_AND_CONFLICTS.md:758), [OBT-10](SOURCE_FINDINGS_AND_CONFLICTS.md:759), [AUT-09](SOURCE_FINDINGS_AND_CONFLICTS.md:775).

**Conversation upgrade lineage.** [DTM-A12](SOURCE_FINDINGS_AND_CONFLICTS.md:70), [JCV-U02](SOURCE_FINDINGS_AND_CONFLICTS.md:155), [JCV-U04](SOURCE_FINDINGS_AND_CONFLICTS.md:157), [JCV-A07](SOURCE_FINDINGS_AND_CONFLICTS.md:166), [CRL-12](SOURCE_FINDINGS_AND_CONFLICTS.md:228), [CRL-14](SOURCE_FINDINGS_AND_CONFLICTS.md:230). Read the full rows and their original conversation references; [the recheck](CONVERSATION_RECHECK.md) preserves the exact unit/exception routes.

This parent has no separate named child; its own P0–P7 phases carry the full upgrade and source-clause obligations.

<a id="up-r03"></a>
### UP-R03 — Diminishing-effort exhaustion

Parent: [R03](components/RESPONSE_DEFERRED.md); [local phases](experiments/R.md#r03); [definition refinement](SYSTEM_REFINEMENT.md#sr-r03). Upgrade role: `forecast`.

**Starting idea.** Declining push volume signals exhaustion.

**Existing improvement path.** Causal push segmentation, effort/pace decay and quiet-progress distinction.

**Remaining weakness.** Changing push duration, distance and trade-size mix can manufacture a decline in aggregate volume.

**Further upgrade.** Model push effort and progress jointly after exposure adjustment for duration, distance and cohort composition. Compare robust sequential slopes with partially pooled push-to-push transition models; preserve incomplete pushes and uncertainty in segmentation rather than waiting for the final best turning point.

**Fair comparison.** Raw declining digits, normalized trend, pooled transition hazard and optional compact sequence model.

**Evidence.** Exhaustion/continuation proper loss, lead time, false signals from segmentation and incremental value.

**Additional local cases to implement.** Shorter push with same intensity; quiet quote-led continuation; changed cohort mix; unfinished last push.

**Decision or system use.** Distinguish weakening pressure from a merely shorter observation interval and price progress requiring less effort.

**Exact reviewed source clauses.** [CRL-15](SOURCE_FINDINGS_AND_CONFLICTS.md:231), [DM5-01](SOURCE_FINDINGS_AND_CONFLICTS.md:348), [DM5-02](SOURCE_FINDINGS_AND_CONFLICTS.md:349), [DM5-03](SOURCE_FINDINGS_AND_CONFLICTS.md:350), [DM5-04](SOURCE_FINDINGS_AND_CONFLICTS.md:351), [DM6-01](SOURCE_FINDINGS_AND_CONFLICTS.md:352), [DM6-02](SOURCE_FINDINGS_AND_CONFLICTS.md:353), [DM6-03](SOURCE_FINDINGS_AND_CONFLICTS.md:354), [DM6-04](SOURCE_FINDINGS_AND_CONFLICTS.md:355), [DM6-05](SOURCE_FINDINGS_AND_CONFLICTS.md:356), [CD3-01](SOURCE_FINDINGS_AND_CONFLICTS.md:404), [CD3-02](SOURCE_FINDINGS_AND_CONFLICTS.md:405), [CD3-03](SOURCE_FINDINGS_AND_CONFLICTS.md:406), [CD3-04](SOURCE_FINDINGS_AND_CONFLICTS.md:407), [CD3-05](SOURCE_FINDINGS_AND_CONFLICTS.md:408), [MAT-03](SOURCE_FINDINGS_AND_CONFLICTS.md:528), [WIC-01](SOURCE_FINDINGS_AND_CONFLICTS.md:577), [WIC-02](SOURCE_FINDINGS_AND_CONFLICTS.md:578), [WIC-03](SOURCE_FINDINGS_AND_CONFLICTS.md:579), [WIC-04](SOURCE_FINDINGS_AND_CONFLICTS.md:580), [WIC-05](SOURCE_FINDINGS_AND_CONFLICTS.md:581), [WIC-06](SOURCE_FINDINGS_AND_CONFLICTS.md:582), [WIC-07](SOURCE_FINDINGS_AND_CONFLICTS.md:583), [OFM-01](SOURCE_FINDINGS_AND_CONFLICTS.md:623), [OFM-02](SOURCE_FINDINGS_AND_CONFLICTS.md:624), [OFM-03](SOURCE_FINDINGS_AND_CONFLICTS.md:625), [OFM-04](SOURCE_FINDINGS_AND_CONFLICTS.md:626), [OFM-05](SOURCE_FINDINGS_AND_CONFLICTS.md:627), [OFM-06](SOURCE_FINDINGS_AND_CONFLICTS.md:628), [OFM-07](SOURCE_FINDINGS_AND_CONFLICTS.md:629), [OFM-08](SOURCE_FINDINGS_AND_CONFLICTS.md:630), [OFM-09](SOURCE_FINDINGS_AND_CONFLICTS.md:631), [NYA-01](SOURCE_FINDINGS_AND_CONFLICTS.md:709), [NYA-02](SOURCE_FINDINGS_AND_CONFLICTS.md:710), [NYA-03](SOURCE_FINDINGS_AND_CONFLICTS.md:711), [NYA-04](SOURCE_FINDINGS_AND_CONFLICTS.md:712), [NYA-05](SOURCE_FINDINGS_AND_CONFLICTS.md:713), [NYA-06](SOURCE_FINDINGS_AND_CONFLICTS.md:714), [OBT-01](SOURCE_FINDINGS_AND_CONFLICTS.md:750), [OBT-02](SOURCE_FINDINGS_AND_CONFLICTS.md:751), [OBT-03](SOURCE_FINDINGS_AND_CONFLICTS.md:752), [OBT-04](SOURCE_FINDINGS_AND_CONFLICTS.md:753), [OBT-05](SOURCE_FINDINGS_AND_CONFLICTS.md:754), [OBT-06](SOURCE_FINDINGS_AND_CONFLICTS.md:755), [OBT-07](SOURCE_FINDINGS_AND_CONFLICTS.md:756), [OBT-08](SOURCE_FINDINGS_AND_CONFLICTS.md:757), [OBT-09](SOURCE_FINDINGS_AND_CONFLICTS.md:758), [OBT-10](SOURCE_FINDINGS_AND_CONFLICTS.md:759).

This parent has no separate named child; its own P0–P7 phases carry the full upgrade and source-clause obligations.

<a id="up-r04"></a>
### UP-R04 — Stopping burst and climax hypothesis

Parent: [R04](components/RESPONSE_DEFERRED.md); [local phases](experiments/R.md#r04); [definition refinement](SYSTEM_REFINEMENT.md#sr-r04). Upgrade role: `forecast`.

**Starting idea.** An extreme burst marks a climax.

**Existing improvement path.** Causal burst detection and separate continuation/rejection outcomes.

**Remaining weakness.** A fixed tail cutoff ignores local intensity and cannot distinguish concentrated stopping effort from broad accelerating participation.

**Further upgrade.** Use conditional burst surprise by covered exposure, price concentration, cohort breadth and contemporaneous progress; retain a simple robust seasonal quantile baseline. Model post-burst competing continuation/stall/reversal transitions at detection and later prefixes; marked-intensity complexity must beat the compact features.

**Fair comparison.** Raw quantile burst, state-normalized surprise, additive hazard and optional marked-process model.

**Evidence.** Tail-event detection stability, branch/time calibration, incremental entry/exit net and false alarms.

**Additional local cases to implement.** Ordinary opening burst; distributed broad advance; one print dominates; late report; burst still in progress.

**Decision or system use.** Use the shape and context of extreme activity rather than assigning every large print the same reversal meaning.

**Exact reviewed source clauses.** [DM6-05](SOURCE_FINDINGS_AND_CONFLICTS.md:356), [FP9-05](SOURCE_FINDINGS_AND_CONFLICTS.md:378).

This parent has no separate named child; its own P0–P7 phases carry the full upgrade and source-clause obligations.

<a id="up-r05"></a>
### UP-R05 — At-touch replenishment and resilience sequence

Parent: [R05](components/RESPONSE_DEFERRED.md); [local phases](experiments/R.md#r05); [definition refinement](SYSTEM_REFINEMENT.md#sr-r05). Upgrade role: `forecast`.

**Starting idea.** Displayed size returns, so the level is defended.

**Existing improvement path.** Execution-adjusted net recovery, recovery delay and survival at the best price.

**Remaining weakness.** One recovery statistic hides repeated depletion cycles, diminishing resilience and uncertainty from batched book events.

**Further upgrade.** Build a touch-local depletion/recovery episode ledger with pressure exposure, recovery-time distribution, retained displayed fraction and cycle-to-cycle decay. Compare deterministic recovery summaries with a state-transition hazard for price loss/reclaim, propagating feasible net-recovery bounds.

**Fair comparison.** Hold rule, print-only, book-only, joint episode summaries and transition model.

**Evidence.** Price-survival/reclaim proper loss, recovery-time calibration, bound sensitivity and economic increment.

**Additional local cases to implement.** Book batch conceals adds/cancels; zero displayed size; unchanged quote price; repeated recovery weakens; execution timing uncertain.

**Decision or system use.** Measure how resilience evolves under actual pressure while retaining the limits of MBP-1 observation.

**Exact reviewed source clauses.** [DTM-A12](SOURCE_FINDINGS_AND_CONFLICTS.md:70), [JCV-U04](SOURCE_FINDINGS_AND_CONFLICTS.md:157), [JCV-A06](SOURCE_FINDINGS_AND_CONFLICTS.md:165), [CRL-07](SOURCE_FINDINGS_AND_CONFLICTS.md:223), [CRL-12](SOURCE_FINDINGS_AND_CONFLICTS.md:228), [CRL-14](SOURCE_FINDINGS_AND_CONFLICTS.md:230), [DM5-01](SOURCE_FINDINGS_AND_CONFLICTS.md:348), [DM5-02](SOURCE_FINDINGS_AND_CONFLICTS.md:349), [DM5-03](SOURCE_FINDINGS_AND_CONFLICTS.md:350), [DM5-04](SOURCE_FINDINGS_AND_CONFLICTS.md:351), [DM6-01](SOURCE_FINDINGS_AND_CONFLICTS.md:352), [DM6-02](SOURCE_FINDINGS_AND_CONFLICTS.md:353), [DM6-03](SOURCE_FINDINGS_AND_CONFLICTS.md:354), [DM6-04](SOURCE_FINDINGS_AND_CONFLICTS.md:355), [DM6-05](SOURCE_FINDINGS_AND_CONFLICTS.md:356), [DM7-01](SOURCE_FINDINGS_AND_CONFLICTS.md:357), [DM7-02](SOURCE_FINDINGS_AND_CONFLICTS.md:358), [DM7-03](SOURCE_FINDINGS_AND_CONFLICTS.md:359), [DM7-04](SOURCE_FINDINGS_AND_CONFLICTS.md:360), [DM7-05](SOURCE_FINDINGS_AND_CONFLICTS.md:361), [CD3-01](SOURCE_FINDINGS_AND_CONFLICTS.md:404), [CD3-02](SOURCE_FINDINGS_AND_CONFLICTS.md:405), [CD3-03](SOURCE_FINDINGS_AND_CONFLICTS.md:406), [CD3-04](SOURCE_FINDINGS_AND_CONFLICTS.md:407), [CD3-05](SOURCE_FINDINGS_AND_CONFLICTS.md:408), [MAT-02](SOURCE_FINDINGS_AND_CONFLICTS.md:527), [MAT-03](SOURCE_FINDINGS_AND_CONFLICTS.md:528), [RFE-01](SOURCE_FINDINGS_AND_CONFLICTS.md:602), [RFE-02](SOURCE_FINDINGS_AND_CONFLICTS.md:603), [RFE-03](SOURCE_FINDINGS_AND_CONFLICTS.md:604), [RFE-04](SOURCE_FINDINGS_AND_CONFLICTS.md:605), [RFE-05](SOURCE_FINDINGS_AND_CONFLICTS.md:606), [RFE-06](SOURCE_FINDINGS_AND_CONFLICTS.md:607), [RFE-07](SOURCE_FINDINGS_AND_CONFLICTS.md:608), [RFE-08](SOURCE_FINDINGS_AND_CONFLICTS.md:609), [RFE-09](SOURCE_FINDINGS_AND_CONFLICTS.md:610), [RFE-10](SOURCE_FINDINGS_AND_CONFLICTS.md:611), [RFE-11](SOURCE_FINDINGS_AND_CONFLICTS.md:612), [RFE-12](SOURCE_FINDINGS_AND_CONFLICTS.md:613), [RFE-13](SOURCE_FINDINGS_AND_CONFLICTS.md:614), [RFE-14](SOURCE_FINDINGS_AND_CONFLICTS.md:615), [OFM-01](SOURCE_FINDINGS_AND_CONFLICTS.md:623), [OFM-02](SOURCE_FINDINGS_AND_CONFLICTS.md:624), [OFM-03](SOURCE_FINDINGS_AND_CONFLICTS.md:625), [OFM-04](SOURCE_FINDINGS_AND_CONFLICTS.md:626), [OFM-05](SOURCE_FINDINGS_AND_CONFLICTS.md:627), [OFM-06](SOURCE_FINDINGS_AND_CONFLICTS.md:628), [OFM-07](SOURCE_FINDINGS_AND_CONFLICTS.md:629), [OFM-08](SOURCE_FINDINGS_AND_CONFLICTS.md:630), [OFM-09](SOURCE_FINDINGS_AND_CONFLICTS.md:631), [CCS-01](SOURCE_FINDINGS_AND_CONFLICTS.md:681), [CCS-02](SOURCE_FINDINGS_AND_CONFLICTS.md:682), [CCS-03](SOURCE_FINDINGS_AND_CONFLICTS.md:683), [CCS-04](SOURCE_FINDINGS_AND_CONFLICTS.md:684), [CCS-05](SOURCE_FINDINGS_AND_CONFLICTS.md:685), [CCS-06](SOURCE_FINDINGS_AND_CONFLICTS.md:686), [CCS-07](SOURCE_FINDINGS_AND_CONFLICTS.md:687), [CCS-08](SOURCE_FINDINGS_AND_CONFLICTS.md:688).

**Conversation upgrade lineage.** [DTM-A12](SOURCE_FINDINGS_AND_CONFLICTS.md:70), [JCV-U04](SOURCE_FINDINGS_AND_CONFLICTS.md:157). Read the full rows and their original conversation references; [the recheck](CONVERSATION_RECHECK.md) preserves the exact unit/exception routes.

This parent has no separate named child; its own P0–P7 phases carry the full upgrade and source-clause obligations.

<a id="up-r06"></a>
### UP-R06 — Depth-wide support, pulling and layering dependency

Parent: [R06](components/RESPONSE_DEFERRED.md); [local phases](experiments/R.md#r06); [definition refinement](SYSTEM_REFINEMENT.md#sr-r06). Upgrade role: `measurement`.

**Starting idea.** Read depth support or pulling from a displayed ladder.

**Existing improvement path.** Full-depth mechanism explicitly blocked where absent, plus distinct BBO turnover proxies.

**Remaining weakness.** A single top-book snapshot loses the sequence of resilience as price visits successive levels.

**Further upgrade.** Create a coverage-aware successive-best-price resilience map from observed visits, executions and recovery, with unobserved deeper levels explicitly absent. If suitable depth arrives, compare its incremental spatial support/cancellation information against the same top-book opportunity cohort; do not backfill hidden depth.

**Fair comparison.** BBO snapshot, successive-best episode map and separately eligible full-depth challenger.

**Evidence.** Measured-state fidelity, conditional adverse movement loss, incremental data value and coverage.

**Additional local cases to implement.** Price skips unobserved levels; repeated level visit; top size changes without depth; new depth feed has different dates.

**Decision or system use.** Extract more supported structure from current observations and define exactly what additional depth would need to improve.

**Exact reviewed source clauses.** [JCV-U03](SOURCE_FINDINGS_AND_CONFLICTS.md:156), [JCV-U04](SOURCE_FINDINGS_AND_CONFLICTS.md:157), [JCV-U06](SOURCE_FINDINGS_AND_CONFLICTS.md:159), [JCV-A03](SOURCE_FINDINGS_AND_CONFLICTS.md:162), [JCV-A07](SOURCE_FINDINGS_AND_CONFLICTS.md:166), [JCV-A09](SOURCE_FINDINGS_AND_CONFLICTS.md:168), [CRL-02](SOURCE_FINDINGS_AND_CONFLICTS.md:218), [CRL-14](SOURCE_FINDINGS_AND_CONFLICTS.md:230), [DM6-01](SOURCE_FINDINGS_AND_CONFLICTS.md:352), [DM6-02](SOURCE_FINDINGS_AND_CONFLICTS.md:353), [DM6-03](SOURCE_FINDINGS_AND_CONFLICTS.md:354), [DM6-04](SOURCE_FINDINGS_AND_CONFLICTS.md:355), [DM6-05](SOURCE_FINDINGS_AND_CONFLICTS.md:356), [DM7-01](SOURCE_FINDINGS_AND_CONFLICTS.md:357), [DM7-02](SOURCE_FINDINGS_AND_CONFLICTS.md:358), [DM7-03](SOURCE_FINDINGS_AND_CONFLICTS.md:359), [DM7-04](SOURCE_FINDINGS_AND_CONFLICTS.md:360), [DM7-05](SOURCE_FINDINGS_AND_CONFLICTS.md:361), [DEN-01](SOURCE_FINDINGS_AND_CONFLICTS.md:409), [DEN-02](SOURCE_FINDINGS_AND_CONFLICTS.md:410), [DEN-03](SOURCE_FINDINGS_AND_CONFLICTS.md:411), [DEN-04](SOURCE_FINDINGS_AND_CONFLICTS.md:412), [DEN-05](SOURCE_FINDINGS_AND_CONFLICTS.md:413).

**Conversation upgrade lineage.** [DTM-A07](SOURCE_FINDINGS_AND_CONFLICTS.md:65), [JCV-U02](SOURCE_FINDINGS_AND_CONFLICTS.md:155), [JCV-U03](SOURCE_FINDINGS_AND_CONFLICTS.md:156), [JCV-U04](SOURCE_FINDINGS_AND_CONFLICTS.md:157), [JCV-U06](SOURCE_FINDINGS_AND_CONFLICTS.md:159), [JCV-A03](SOURCE_FINDINGS_AND_CONFLICTS.md:162), [JCV-A07](SOURCE_FINDINGS_AND_CONFLICTS.md:166), [JCV-A09](SOURCE_FINDINGS_AND_CONFLICTS.md:168), [CRL-02](SOURCE_FINDINGS_AND_CONFLICTS.md:218). Read the full rows and their original conversation references; [the recheck](CONVERSATION_RECHECK.md) preserves the exact unit/exception routes.

This parent has no separate named child; its own P0–P7 phases carry the full upgrade and source-clause obligations.

<a id="up-r07"></a>
### UP-R07 — Candle/footprint effort-result disagreement

Parent: [R07](components/RESPONSE_DEFERRED.md); [local phases](experiments/R.md#r07); [definition refinement](SYSTEM_REFINEMENT.md#sr-r07). Upgrade role: `forecast`.

**Starting idea.** A green candle with negative delta is a reversal clue.

**Existing improvement path.** Distinct closed-bar and developing footprint effort-result disagreement.

**Remaining weakness.** Two sign bits discard where opposing effort occurred, the path through the candle and whether the result was unusual.

**Further upgrade.** Represent side-specific effort over causal body/wick/current-range coordinates and time within formation; add progress residuals and unknown-side mass. Compare continuous interactions and low-rank spatial-temporal summaries with raw signs, preserving separately trained developing and completed-bar cuts.

**Fair comparison.** Sign rule, scalar interaction, structured footprint summaries and small tensor model.

**Evidence.** Target proper loss, spatial contribution, timing delay cost, net increment and data support.

**Additional local cases to implement.** Final wick differs from current geometry; same totals with opposite event order; near-zero delta; body definition changes.

**Decision or system use.** Turn disagreement into a graded, spatial and temporal description of pressure versus achieved movement.

**Exact reviewed source clauses.** [JTR-11](SOURCE_FINDINGS_AND_CONFLICTS.md:28), [JTR-20](SOURCE_FINDINGS_AND_CONFLICTS.md:37), [JXA-13](SOURCE_FINDINGS_AND_CONFLICTS.md:112), [FP8-01](SOURCE_FINDINGS_AND_CONFLICTS.md:369), [FP8-02](SOURCE_FINDINGS_AND_CONFLICTS.md:370), [FP8-03](SOURCE_FINDINGS_AND_CONFLICTS.md:371), [FP8-04](SOURCE_FINDINGS_AND_CONFLICTS.md:372), [FP8-05](SOURCE_FINDINGS_AND_CONFLICTS.md:373), [FP9-01](SOURCE_FINDINGS_AND_CONFLICTS.md:374), [FP9-02](SOURCE_FINDINGS_AND_CONFLICTS.md:375), [FP9-03](SOURCE_FINDINGS_AND_CONFLICTS.md:376), [FP9-04](SOURCE_FINDINGS_AND_CONFLICTS.md:377), [FP9-05](SOURCE_FINDINGS_AND_CONFLICTS.md:378), [FP9-06](SOURCE_FINDINGS_AND_CONFLICTS.md:379), [CD3-01](SOURCE_FINDINGS_AND_CONFLICTS.md:404), [CD3-02](SOURCE_FINDINGS_AND_CONFLICTS.md:405), [CD3-03](SOURCE_FINDINGS_AND_CONFLICTS.md:406), [CD3-04](SOURCE_FINDINGS_AND_CONFLICTS.md:407), [CD3-05](SOURCE_FINDINGS_AND_CONFLICTS.md:408), [OBT-02](SOURCE_FINDINGS_AND_CONFLICTS.md:751).

This parent has no separate named child; its own P0–P7 phases carry the full upgrade and source-clause obligations.

<a id="up-r08"></a>
### UP-R08 — Diagonal imbalance and stacked-flow defense

Parent: [R08](components/RESPONSE_DEFERRED.md); [local phases](experiments/R.md#r08); [definition refinement](SYSTEM_REFINEMENT.md#sr-r08). Upgrade role: `measurement`.

**Starting idea.** Use a fixed diagonal imbalance ratio and count stacked rows.

**Existing improvement path.** Exact diagonal/same-price variants, smoothing, minimum support and causal stack lifecycle.

**Remaining weakness.** A large ratio from sparse cells can outweigh a broad supported stack, and one maximum hides partial repair.

**Further upgrade.** Compare posterior/shrunken side contrast with an exposure-weighted contiguous-support statistic; retain width, integrated contrast, uncertainty, gaps and repair fraction. Track the stack as a frozen causal object with forward revisions, then test its survival/action role separately.

**Fair comparison.** Source ratio/length grid, shrunken cell contrasts, integrated stack support and local model.

**Evidence.** False stack rate on sparse cells, geometry stability, defense/failure calibration and net location increment.

**Additional local cases to implement.** Zero denominator; one contract creates huge ratio; gapped stack; partial repair; tick-grid change.

**Decision or system use.** Produce stable defense regions and confidence appropriate to the amount and continuity of observed flow.

**Exact reviewed source clauses.** [JXA-24](SOURCE_FINDINGS_AND_CONFLICTS.md:123), [FP8-01](SOURCE_FINDINGS_AND_CONFLICTS.md:369), [FP8-02](SOURCE_FINDINGS_AND_CONFLICTS.md:370), [FP8-03](SOURCE_FINDINGS_AND_CONFLICTS.md:371), [FP8-04](SOURCE_FINDINGS_AND_CONFLICTS.md:372), [FP8-05](SOURCE_FINDINGS_AND_CONFLICTS.md:373), [F23-02](SOURCE_FINDINGS_AND_CONFLICTS.md:668), [OBT-02](SOURCE_FINDINGS_AND_CONFLICTS.md:751), [AUT-06](SOURCE_FINDINGS_AND_CONFLICTS.md:772).

This parent has no separate named child; its own P0–P7 phases carry the full upgrade and source-clause obligations.

<a id="up-r09"></a>
### UP-R09 — Developing POC flip and footprint-mode migration

Parent: [R09](components/RESPONSE_DEFERRED.md); [local phases](experiments/R.md#r09); [definition refinement](SYSTEM_REFINEMENT.md#sr-r09). Upgrade role: `measurement`.

**Starting idea.** A POC flip from low to high indicates control changed.

**Existing improvement path.** Developing mode identity, dominance margin, mass centroid and successive-bar migration.

**Remaining weakness.** Argmax flips can reflect a near tie, while meaningful mass redistribution can occur without changing the maximum.

**Further upgrade.** Track the distribution of newly added volume on a frozen grid, mode confidence set, normalized mass shifts and transport relative to the prior normalized profile. Decompose old fixed mass versus new additions; compare incremental functional summaries with the existing POC/centroid and tensor approaches.

**Fair comparison.** POC sign/flip count, mass moments, transport/new-mass summaries and optional structured learner.

**Evidence.** Grid/tie stability, early branch calibration, action value, latency and sensitivity to total exposure.

**Additional local cases to implement.** Two equal modes alternate; profile grows without relocating old trades; truncation/overflow; same final profile with different order.

**Decision or system use.** Detect meaningful developing auction change while separating unstable maxima from supported new mass.

**Exact reviewed source clauses.** [FP9-01](SOURCE_FINDINGS_AND_CONFLICTS.md:374), [FP9-02](SOURCE_FINDINGS_AND_CONFLICTS.md:375), [FP9-03](SOURCE_FINDINGS_AND_CONFLICTS.md:376), [FP9-04](SOURCE_FINDINGS_AND_CONFLICTS.md:377), [FP9-05](SOURCE_FINDINGS_AND_CONFLICTS.md:378), [FP9-06](SOURCE_FINDINGS_AND_CONFLICTS.md:379).

This parent has no separate named child; its own P0–P7 phases carry the full upgrade and source-clause obligations.

<a id="up-r10"></a>
### UP-R10 — CVD-relative control and multiscale divergence

Parent: [R10](components/RESPONSE_DEFERRED.md); [local phases](experiments/R.md#r10); [definition refinement](SYSTEM_REFINEMENT.md#sr-r10). Upgrade role: `forecast`.

**Starting idea.** Read control from CVD above a median or from one divergence.

**Existing improvement path.** All distinct multiscale price/CVD, cohort and cross-market cases with causal confirmation.

**Remaining weakness.** Rolling CVD trends can be driven by expected activity and correlated horizons; divergence labels omit whether flow or price is surprising.

**Further upgrade.** Use joint expected-flow/expected-progress residuals and distributed lag responses at matched causal cuts. Preserve each source divergence as a comparator, add a sparse multiscale interaction model, and distinguish flow leading price, price resisting flow and contemporaneous disagreement.

**Fair comparison.** Source cases, raw multiscale regression, residual lag features and pooled conditional model.

**Evidence.** Per-case path loss, lead-time calibration, unknown-side sensitivity, net increment and redundancy.

**Additional local cases to implement.** Reset creates false divergence; noisy small cohort; same event reused at many horizons; asynchronous source market.

**Decision or system use.** Unify comparison of control mechanisms without erasing their distinct directional and temporal meanings.

**Exact reviewed source clauses.** [CRL-12](SOURCE_FINDINGS_AND_CONFLICTS.md:228), [CRL-14](SOURCE_FINDINGS_AND_CONFLICTS.md:230), [FP9-01](SOURCE_FINDINGS_AND_CONFLICTS.md:374), [FP9-02](SOURCE_FINDINGS_AND_CONFLICTS.md:375), [FP9-03](SOURCE_FINDINGS_AND_CONFLICTS.md:376), [FP9-04](SOURCE_FINDINGS_AND_CONFLICTS.md:377), [FP9-05](SOURCE_FINDINGS_AND_CONFLICTS.md:378), [FP9-06](SOURCE_FINDINGS_AND_CONFLICTS.md:379), [CD3-01](SOURCE_FINDINGS_AND_CONFLICTS.md:404), [CD3-02](SOURCE_FINDINGS_AND_CONFLICTS.md:405), [CD3-03](SOURCE_FINDINGS_AND_CONFLICTS.md:406), [CD3-04](SOURCE_FINDINGS_AND_CONFLICTS.md:407), [CD3-05](SOURCE_FINDINGS_AND_CONFLICTS.md:408), [YMA-01](SOURCE_FINDINGS_AND_CONFLICTS.md:589), [YMA-02](SOURCE_FINDINGS_AND_CONFLICTS.md:590), [YMA-03](SOURCE_FINDINGS_AND_CONFLICTS.md:591), [YMA-04](SOURCE_FINDINGS_AND_CONFLICTS.md:592), [YMA-05](SOURCE_FINDINGS_AND_CONFLICTS.md:593), [YMA-06](SOURCE_FINDINGS_AND_CONFLICTS.md:594).

**Conversation upgrade lineage.** [CRL-12](SOURCE_FINDINGS_AND_CONFLICTS.md:228). Read the full rows and their original conversation references; [the recheck](CONVERSATION_RECHECK.md) preserves the exact unit/exception routes.

<a id="up-r10-cvd_cases"></a>
#### R10.CVD_CASES — Distinct CVD control hypotheses

[Existing definition, target and P0–P7](experiments/R.md#r10-cvd_cases) remain binding.

**Specific upgrade scope.** Add normalized flow/price innovations and causal distributed lags to every preserved control/divergence case.

**Local comparison.** Compare each raw source case, continuous residual features and pooled conditional model on identical cuts.

**Additional cases.** Median reset; cohort mismatch; confirmed pivot delay; same endpoint opposite chronology.

<a id="up-r11"></a>
### UP-R11 — Balance break, retest and failed-retest reversal

Parent: [R11](components/RESPONSE_DEFERRED.md); [local phases](experiments/R.md#r11); [definition refinement](SYSTEM_REFINEMENT.md#sr-r11). Upgrade role: `forecast`.

**Starting idea.** Trade a break, retest or failed auction as one setup.

**Existing improvement path.** Separate ordered branches, prior-balance POC versus broader value, and unfinished outcomes.

**Remaining weakness.** Hard completed-pattern recognition misses useful partial prefixes and confuses expected duration with failed confirmation.

**Further upgrade.** Use a semi-Markov branch model with explicit A/B objects, reference type, elapsed stage time and no-retest transitions. Compare source finite-state rules with partially pooled hazards that estimate each next branch and remaining travel; forecast at every permitted prefix.

**Fair comparison.** Source completed patterns, branch tables, duration-aware hazards and compact sequence model.

**Evidence.** Branch/time proper loss, prefix incremental value, no-retest coverage and exact source-case fidelity.

**Additional local cases to implement.** B-POC never reached; value edge reached instead; stalled unfinished traverse; return to A without entry authorization.

**Decision or system use.** Price the choice to enter, wait or cancel during the full balance-transition process.

**Exact reviewed source clauses.** [DTM-A07](SOURCE_FINDINGS_AND_CONFLICTS.md:65), [DTM-A13](SOURCE_FINDINGS_AND_CONFLICTS.md:71), [JXA-03](SOURCE_FINDINGS_AND_CONFLICTS.md:102), [JCV-A02](SOURCE_FINDINGS_AND_CONFLICTS.md:161), [JCV-A06](SOURCE_FINDINGS_AND_CONFLICTS.md:165), [CRL-07](SOURCE_FINDINGS_AND_CONFLICTS.md:223), [CRL-14](SOURCE_FINDINGS_AND_CONFLICTS.md:230), [TP3-06](SOURCE_FINDINGS_AND_CONFLICTS.md:315), [CD3-04](SOURCE_FINDINGS_AND_CONFLICTS.md:407), [MAV-05](SOURCE_FINDINGS_AND_CONFLICTS.md:509), [MAV-06](SOURCE_FINDINGS_AND_CONFLICTS.md:510), [RVP-03](SOURCE_FINDINGS_AND_CONFLICTS.md:544), [RVP-07](SOURCE_FINDINGS_AND_CONFLICTS.md:548), [ALM-01](SOURCE_FINDINGS_AND_CONFLICTS.md:564), [ALM-02](SOURCE_FINDINGS_AND_CONFLICTS.md:565), [ALM-03](SOURCE_FINDINGS_AND_CONFLICTS.md:566), [ALM-04](SOURCE_FINDINGS_AND_CONFLICTS.md:567), [ALM-05](SOURCE_FINDINGS_AND_CONFLICTS.md:568), [ALM-06](SOURCE_FINDINGS_AND_CONFLICTS.md:569), [WIC-01](SOURCE_FINDINGS_AND_CONFLICTS.md:577), [WIC-02](SOURCE_FINDINGS_AND_CONFLICTS.md:578), [WIC-03](SOURCE_FINDINGS_AND_CONFLICTS.md:579), [WIC-04](SOURCE_FINDINGS_AND_CONFLICTS.md:580), [WIC-05](SOURCE_FINDINGS_AND_CONFLICTS.md:581), [WIC-06](SOURCE_FINDINGS_AND_CONFLICTS.md:582), [WIC-07](SOURCE_FINDINGS_AND_CONFLICTS.md:583), [K10-01](SOURCE_FINDINGS_AND_CONFLICTS.md:639), [K10-02](SOURCE_FINDINGS_AND_CONFLICTS.md:640), [K10-03](SOURCE_FINDINGS_AND_CONFLICTS.md:641), [K10-04](SOURCE_FINDINGS_AND_CONFLICTS.md:642), [K10-05](SOURCE_FINDINGS_AND_CONFLICTS.md:643), [K10-06](SOURCE_FINDINGS_AND_CONFLICTS.md:644), [F23-01](SOURCE_FINDINGS_AND_CONFLICTS.md:667), [F23-02](SOURCE_FINDINGS_AND_CONFLICTS.md:668), [F23-03](SOURCE_FINDINGS_AND_CONFLICTS.md:669), [F23-04](SOURCE_FINDINGS_AND_CONFLICTS.md:670), [F23-05](SOURCE_FINDINGS_AND_CONFLICTS.md:671), [F23-06](SOURCE_FINDINGS_AND_CONFLICTS.md:672), [F23-07](SOURCE_FINDINGS_AND_CONFLICTS.md:673), [AUT-06](SOURCE_FINDINGS_AND_CONFLICTS.md:772).

**Conversation upgrade lineage.** [DTM-A13](SOURCE_FINDINGS_AND_CONFLICTS.md:71). Read the full rows and their original conversation references; [the recheck](CONVERSATION_RECHECK.md) preserves the exact unit/exception routes.

<a id="up-r11-fa_poc"></a>
#### R11.FA_POC — Specific prior-balance-POC failed auction

[Existing definition, target and P0–P7](experiments/R.md#r11-fa_poc) remain binding.

**Specific upgrade scope.** Use duration-aware A→B-POC→A branch forecasts at every observed prefix with exact two-balance identities.

**Local comparison.** Compare completed source rule with continuous stage/remaining-path models; B-POC contact cannot be replaced by another value reference.

**Additional cases.** B POC not reached; prior B unknown; partial return to A; far edge unresolved.

<a id="up-r11-fa_value"></a>
#### R11.FA_VALUE — Broader prior-value failed auction

[Existing definition, target and P0–P7](experiments/R.md#r11-fa_value) remain binding.

**Specific upgrade scope.** Apply the same branch machinery to the separately defined broader B-value reference and preserve its different opportunity population.

**Local comparison.** Compare faithful value versus POC requirements with matched source availability and report population changes explicitly.

**Additional cases.** Touches value edge but not POC; broad region widens hit rate; incomplete traversal.

<a id="up-r12"></a>
### UP-R12 — Failed squeeze, refill and renewed same-direction squeeze

Parent: [R12](components/RESPONSE_DEFERRED.md); [local phases](experiments/R.md#r12); [definition refinement](SYSTEM_REFINEMENT.md#sr-r12). Upgrade role: `forecast`.

**Starting idea.** A failed squeeze means fade, or a refill means squeeze again.

**Existing improvement path.** Plain squeeze, failed fade and renewed original-direction branches with separate origin IDs.

**Remaining weakness.** A single failure flag misses how much of the initial move survived and whether new effort replenished the original thesis.

**Further upgrade.** Represent squeeze/failure/refill as a signed progress-and-effort trajectory with surviving displacement, reclaimed origin fraction, new versus reused flow and elapsed stage time. Compare shared transition models with branch-specific residuals against the source finite-state paths.

**Fair comparison.** Source rules, branch frequencies, continuous stage summaries and duration-aware shared/branch model.

**Evidence.** Branch calibration, sparse-branch uncertainty, prefix value and cumulative idea loss.

**Additional local cases to implement.** Complete versus partial failure; refill at a distinct pocket; quiet renewal; no renewed squeeze; catalyst persists after local failure.

**Decision or system use.** Distinguish reversal from renewed continuation using measurable retained structure and fresh evidence.

**Exact reviewed source clauses.** [DTM-A07](SOURCE_FINDINGS_AND_CONFLICTS.md:65), [DTM-A13](SOURCE_FINDINGS_AND_CONFLICTS.md:71), [JCV-A02](SOURCE_FINDINGS_AND_CONFLICTS.md:161), [CRL-07](SOURCE_FINDINGS_AND_CONFLICTS.md:223), [CRL-14](SOURCE_FINDINGS_AND_CONFLICTS.md:230), [OFM-01](SOURCE_FINDINGS_AND_CONFLICTS.md:623), [OFM-02](SOURCE_FINDINGS_AND_CONFLICTS.md:624), [OFM-03](SOURCE_FINDINGS_AND_CONFLICTS.md:625), [OFM-04](SOURCE_FINDINGS_AND_CONFLICTS.md:626), [OFM-05](SOURCE_FINDINGS_AND_CONFLICTS.md:627), [OFM-06](SOURCE_FINDINGS_AND_CONFLICTS.md:628), [OFM-07](SOURCE_FINDINGS_AND_CONFLICTS.md:629), [OFM-08](SOURCE_FINDINGS_AND_CONFLICTS.md:630), [OFM-09](SOURCE_FINDINGS_AND_CONFLICTS.md:631), [CCS-01](SOURCE_FINDINGS_AND_CONFLICTS.md:681), [CCS-02](SOURCE_FINDINGS_AND_CONFLICTS.md:682), [CCS-03](SOURCE_FINDINGS_AND_CONFLICTS.md:683), [CCS-04](SOURCE_FINDINGS_AND_CONFLICTS.md:684), [CCS-05](SOURCE_FINDINGS_AND_CONFLICTS.md:685), [CCS-06](SOURCE_FINDINGS_AND_CONFLICTS.md:686), [CCS-07](SOURCE_FINDINGS_AND_CONFLICTS.md:687), [CCS-08](SOURCE_FINDINGS_AND_CONFLICTS.md:688), [OBT-03](SOURCE_FINDINGS_AND_CONFLICTS.md:752).

**Conversation upgrade lineage.** [DTM-A13](SOURCE_FINDINGS_AND_CONFLICTS.md:71), [JCV-A02](SOURCE_FINDINGS_AND_CONFLICTS.md:161), [CRL-14](SOURCE_FINDINGS_AND_CONFLICTS.md:230). Read the full rows and their original conversation references; [the recheck](CONVERSATION_RECHECK.md) preserves the exact unit/exception routes.

<a id="up-r12-squeeze_branches"></a>
#### R12.SQUEEZE_BRANCHES — Failed squeeze and resqueeze alternatives

[Existing definition, target and P0–P7](experiments/R.md#r12-squeeze_branches) remain binding.

**Specific upgrade scope.** Add retained displacement, origin reclaim, new effort and stage duration to plain, failed-fade and resqueeze branches.

**Local comparison.** Compare independent source paths with shared transitions plus branch-specific residuals.

**Additional cases.** Partial failure; new origin pocket; quiet renewal; no refill; reused initial catalyst.

<a id="up-r13"></a>
### UP-R13 — Quiet failure and passive-reversion alternative

Parent: [R13](components/RESPONSE_DEFERRED.md); [local phases](experiments/R.md#r13); [definition refinement](SYSTEM_REFINEMENT.md#sr-r13). Upgrade role: `forecast`.

**Starting idea.** Fade a quiet failed push without waiting for own-side aggression.

**Existing improvement path.** Observed slowing/failure separated from missing tape and own-flow confirmation.

**Remaining weakness.** Quietness may be normal inactivity, degraded coverage or efficient progress with low trading effort.

**Further upgrade.** Model the joint occurrence of reduced opposing intensity and reduced progress relative to covered state-dependent expectations; include quote-led progress and observed recovery when available. Compare failure-only action with direct C/L and later confirmation using the same boundary and executable prices.

**Fair comparison.** Raw quiet rule, normalized failure features and joint hazard, each with act-now/wait policy comparisons.

**Evidence.** Failure/continuation calibration, detection delay, coverage robustness and complete policy net.

**Additional local cases to implement.** Tape outage; normally quiet interval; low-volume steady trend; quote retreat without prints; valid quiet rejection.

**Decision or system use.** Retain a supported passive-reversion branch without treating absence of displayed activity as evidence by itself.

**Exact reviewed source clauses.** [MAT-03](SOURCE_FINDINGS_AND_CONFLICTS.md:528), [OFM-01](SOURCE_FINDINGS_AND_CONFLICTS.md:623), [OFM-02](SOURCE_FINDINGS_AND_CONFLICTS.md:624), [OFM-03](SOURCE_FINDINGS_AND_CONFLICTS.md:625), [OFM-04](SOURCE_FINDINGS_AND_CONFLICTS.md:626), [OFM-05](SOURCE_FINDINGS_AND_CONFLICTS.md:627), [OFM-06](SOURCE_FINDINGS_AND_CONFLICTS.md:628), [OFM-07](SOURCE_FINDINGS_AND_CONFLICTS.md:629), [OFM-08](SOURCE_FINDINGS_AND_CONFLICTS.md:630), [OFM-09](SOURCE_FINDINGS_AND_CONFLICTS.md:631), [NYA-01](SOURCE_FINDINGS_AND_CONFLICTS.md:709), [NYA-02](SOURCE_FINDINGS_AND_CONFLICTS.md:710), [NYA-03](SOURCE_FINDINGS_AND_CONFLICTS.md:711), [NYA-04](SOURCE_FINDINGS_AND_CONFLICTS.md:712), [NYA-05](SOURCE_FINDINGS_AND_CONFLICTS.md:713), [NYA-06](SOURCE_FINDINGS_AND_CONFLICTS.md:714), [OBT-01](SOURCE_FINDINGS_AND_CONFLICTS.md:750), [OBT-02](SOURCE_FINDINGS_AND_CONFLICTS.md:751), [OBT-03](SOURCE_FINDINGS_AND_CONFLICTS.md:752), [OBT-04](SOURCE_FINDINGS_AND_CONFLICTS.md:753), [OBT-05](SOURCE_FINDINGS_AND_CONFLICTS.md:754), [OBT-06](SOURCE_FINDINGS_AND_CONFLICTS.md:755), [OBT-07](SOURCE_FINDINGS_AND_CONFLICTS.md:756), [OBT-08](SOURCE_FINDINGS_AND_CONFLICTS.md:757), [OBT-09](SOURCE_FINDINGS_AND_CONFLICTS.md:758), [OBT-10](SOURCE_FINDINGS_AND_CONFLICTS.md:759).

<a id="up-r13-quiet_entry"></a>
#### R13.QUIET_ENTRY — Quiet failure without own-side burst

[Existing definition, target and P0–P7](experiments/R.md#r13-quiet_entry) remain binding.

**Specific upgrade scope.** Measure opposing intensity and progress shortfall relative to covered expected state without requiring own-side burst.

**Local comparison.** Compare direct C/L, failure-only and later confirmation using actual prices/horizon and complete net.

**Additional cases.** Outage looks quiet; efficient quiet trend; valid quote-led rejection; delay removes runway.

<a id="up-r14"></a>
### UP-R14 — Opposing absorption, reward, refresh and lift-off sequence

Parent: [R14](components/RESPONSE_DEFERRED.md); [local phases](experiments/R.md#r14); [definition refinement](SYSTEM_REFINEMENT.md#sr-r14). Upgrade role: `decision`.

**Starting idea.** Require a fixed absorption/reward/refresh sequence before entry.

**Existing improvement path.** Every causal stage and alternative source tick/update interpretation has its own action comparison.

**Remaining weakness.** A conjunction can discard valuable early entries and demand a later stage that adds little information at a worse price.

**Further upgrade.** Estimate incremental information and action value after each named prefix, allowing skipped/alternative transitions in a compact stage graph. Compare additive evidence accumulation and duration-aware hazards with strict conjunctions; explicitly price confirmation delay and optional reward-area retest.

**Fair comparison.** Each source threshold path, additive stages, flexible transition graph and bounded lookahead adapter.

**Evidence.** Conditional value of each additional stage, calibration, missed moves, actual-entry net and compute.

**Additional local cases to implement.** Recovery in updates differs from price ticks; lift-off without refresh; late confirmation exhausts runway; repeated stage adds no new evidence.

**Decision or system use.** Retain the useful parts of the sequence and determine which observed stages deserve waiting for.

**Exact reviewed source clauses.** [DTM-A07](SOURCE_FINDINGS_AND_CONFLICTS.md:65), [DTM-A12](SOURCE_FINDINGS_AND_CONFLICTS.md:70), [JXA-03](SOURCE_FINDINGS_AND_CONFLICTS.md:102), [JXA-17](SOURCE_FINDINGS_AND_CONFLICTS.md:116), [CRL-07](SOURCE_FINDINGS_AND_CONFLICTS.md:223), [CRL-08](SOURCE_FINDINGS_AND_CONFLICTS.md:224), [CRL-12](SOURCE_FINDINGS_AND_CONFLICTS.md:228), [CRL-16](SOURCE_FINDINGS_AND_CONFLICTS.md:232), [TP3-07](SOURCE_FINDINGS_AND_CONFLICTS.md:316), [DM5-04](SOURCE_FINDINGS_AND_CONFLICTS.md:351), [DM7-02](SOURCE_FINDINGS_AND_CONFLICTS.md:358), [WIC-01](SOURCE_FINDINGS_AND_CONFLICTS.md:577), [WIC-02](SOURCE_FINDINGS_AND_CONFLICTS.md:578), [WIC-03](SOURCE_FINDINGS_AND_CONFLICTS.md:579), [WIC-04](SOURCE_FINDINGS_AND_CONFLICTS.md:580), [WIC-05](SOURCE_FINDINGS_AND_CONFLICTS.md:581), [WIC-06](SOURCE_FINDINGS_AND_CONFLICTS.md:582), [WIC-07](SOURCE_FINDINGS_AND_CONFLICTS.md:583), [YMA-01](SOURCE_FINDINGS_AND_CONFLICTS.md:589), [YMA-02](SOURCE_FINDINGS_AND_CONFLICTS.md:590), [YMA-03](SOURCE_FINDINGS_AND_CONFLICTS.md:591), [YMA-04](SOURCE_FINDINGS_AND_CONFLICTS.md:592), [YMA-05](SOURCE_FINDINGS_AND_CONFLICTS.md:593), [YMA-06](SOURCE_FINDINGS_AND_CONFLICTS.md:594), [RFE-01](SOURCE_FINDINGS_AND_CONFLICTS.md:602), [RFE-02](SOURCE_FINDINGS_AND_CONFLICTS.md:603), [RFE-03](SOURCE_FINDINGS_AND_CONFLICTS.md:604), [RFE-04](SOURCE_FINDINGS_AND_CONFLICTS.md:605), [RFE-05](SOURCE_FINDINGS_AND_CONFLICTS.md:606), [RFE-06](SOURCE_FINDINGS_AND_CONFLICTS.md:607), [RFE-07](SOURCE_FINDINGS_AND_CONFLICTS.md:608), [RFE-08](SOURCE_FINDINGS_AND_CONFLICTS.md:609), [RFE-09](SOURCE_FINDINGS_AND_CONFLICTS.md:610), [RFE-10](SOURCE_FINDINGS_AND_CONFLICTS.md:611), [RFE-11](SOURCE_FINDINGS_AND_CONFLICTS.md:612), [RFE-12](SOURCE_FINDINGS_AND_CONFLICTS.md:613), [RFE-13](SOURCE_FINDINGS_AND_CONFLICTS.md:614), [RFE-14](SOURCE_FINDINGS_AND_CONFLICTS.md:615), [K18-01](SOURCE_FINDINGS_AND_CONFLICTS.md:652), [K18-02](SOURCE_FINDINGS_AND_CONFLICTS.md:653), [K18-03](SOURCE_FINDINGS_AND_CONFLICTS.md:654), [K18-04](SOURCE_FINDINGS_AND_CONFLICTS.md:655), [K18-05](SOURCE_FINDINGS_AND_CONFLICTS.md:656), [K18-06](SOURCE_FINDINGS_AND_CONFLICTS.md:657), [K18-07](SOURCE_FINDINGS_AND_CONFLICTS.md:658), [K18-08](SOURCE_FINDINGS_AND_CONFLICTS.md:659), [SRE-01](SOURCE_FINDINGS_AND_CONFLICTS.md:722), [SRE-02](SOURCE_FINDINGS_AND_CONFLICTS.md:723), [SRE-03](SOURCE_FINDINGS_AND_CONFLICTS.md:724), [SRE-04](SOURCE_FINDINGS_AND_CONFLICTS.md:725), [SRE-05](SOURCE_FINDINGS_AND_CONFLICTS.md:726), [SRE-06](SOURCE_FINDINGS_AND_CONFLICTS.md:727), [SRE-07](SOURCE_FINDINGS_AND_CONFLICTS.md:728), [AUT-08](SOURCE_FINDINGS_AND_CONFLICTS.md:774).

**Conversation upgrade lineage.** [DTM-A12](SOURCE_FINDINGS_AND_CONFLICTS.md:70), [DTM-A15](SOURCE_FINDINGS_AND_CONFLICTS.md:73), [CRL-07](SOURCE_FINDINGS_AND_CONFLICTS.md:223), [CRL-08](SOURCE_FINDINGS_AND_CONFLICTS.md:224), [CRL-12](SOURCE_FINDINGS_AND_CONFLICTS.md:228), [CRL-16](SOURCE_FINDINGS_AND_CONFLICTS.md:232), [DRF-A15](SOURCE_FINDINGS_AND_CONFLICTS.md:456). Read the full rows and their original conversation references; [the recheck](CONVERSATION_RECHECK.md) preserves the exact unit/exception routes.

<a id="up-r14-prefixes"></a>
#### R14.PREFIXES — Value of every absorption/refill stage

[Existing definition, target and P0–P7](experiments/R.md#r14-prefixes) remain binding.

**Specific upgrade scope.** Evaluate additive information and action value after every named hold/recovery/turn/progress/refresh prefix.

**Local comparison.** Compare strict source conjunctions with flexible stage transitions and bounded waiting, preserving tick-versus-update alternatives.

**Additional cases.** Skipped refresh; updates versus price ticks; repeated stage adds no evidence; lift-off already occurred.

<a id="up-r15"></a>
### UP-R15 — Rewarded-side memory and protected structure

Parent: [R15](components/RESPONSE_DEFERRED.md); [local phases](experiments/R.md#r15); [definition refinement](SYSTEM_REFINEMENT.md#sr-r15). Upgrade role: `forecast`.

**Starting idea.** An aggression origin that was rewarded is protected structure.

**Existing improvement path.** Causal markout maturity, confirmed protection, survival and role reversal.

**Remaining weakness.** A single successful reaction overstates durability and conflates a strong market trend with location-specific defense.

**Further upgrade.** Estimate protection strength from excess markout relative to matched context, new defense evidence and cumulative pressure, using shrinkage and age-aware survival. Compare price-only structure, raw rewarded effort and residual protection; preserve origin geometry and confirmation delays.

**Fair comparison.** Source protection, swing-only trail, raw markout survival and context-residual survival/value.

**Evidence.** Useful-lifetime calibration, incremental trail/exit value, decay stability and independent origin support.

**Additional local cases to implement.** Trend rewards every print; delayed markout not yet mature; strong first reaction followed by depletion; role reversal.

**Decision or system use.** Use protected structure according to tested persistence and added information, rather than a permanent label after one favorable move.

**Exact reviewed source clauses.** [DTM-A13](SOURCE_FINDINGS_AND_CONFLICTS.md:71), [JXA-08](SOURCE_FINDINGS_AND_CONFLICTS.md:107), [JXA-15](SOURCE_FINDINGS_AND_CONFLICTS.md:114), [JCV-A02](SOURCE_FINDINGS_AND_CONFLICTS.md:161), [CRL-07](SOURCE_FINDINGS_AND_CONFLICTS.md:223), [CRL-13](SOURCE_FINDINGS_AND_CONFLICTS.md:229), [CRL-14](SOURCE_FINDINGS_AND_CONFLICTS.md:230), [RDL-01](SOURCE_FINDINGS_AND_CONFLICTS.md:550), [RDL-02](SOURCE_FINDINGS_AND_CONFLICTS.md:551), [RDL-03](SOURCE_FINDINGS_AND_CONFLICTS.md:552), [RDL-04](SOURCE_FINDINGS_AND_CONFLICTS.md:553), [RDL-05](SOURCE_FINDINGS_AND_CONFLICTS.md:554), [RDL-06](SOURCE_FINDINGS_AND_CONFLICTS.md:555), [RDL-07](SOURCE_FINDINGS_AND_CONFLICTS.md:556), [WIC-01](SOURCE_FINDINGS_AND_CONFLICTS.md:577), [WIC-02](SOURCE_FINDINGS_AND_CONFLICTS.md:578), [WIC-03](SOURCE_FINDINGS_AND_CONFLICTS.md:579), [WIC-04](SOURCE_FINDINGS_AND_CONFLICTS.md:580), [WIC-05](SOURCE_FINDINGS_AND_CONFLICTS.md:581), [WIC-06](SOURCE_FINDINGS_AND_CONFLICTS.md:582), [WIC-07](SOURCE_FINDINGS_AND_CONFLICTS.md:583), [RFE-01](SOURCE_FINDINGS_AND_CONFLICTS.md:602), [RFE-02](SOURCE_FINDINGS_AND_CONFLICTS.md:603), [RFE-03](SOURCE_FINDINGS_AND_CONFLICTS.md:604), [RFE-04](SOURCE_FINDINGS_AND_CONFLICTS.md:605), [RFE-05](SOURCE_FINDINGS_AND_CONFLICTS.md:606), [RFE-06](SOURCE_FINDINGS_AND_CONFLICTS.md:607), [RFE-07](SOURCE_FINDINGS_AND_CONFLICTS.md:608), [RFE-08](SOURCE_FINDINGS_AND_CONFLICTS.md:609), [RFE-09](SOURCE_FINDINGS_AND_CONFLICTS.md:610), [RFE-10](SOURCE_FINDINGS_AND_CONFLICTS.md:611), [RFE-11](SOURCE_FINDINGS_AND_CONFLICTS.md:612), [RFE-12](SOURCE_FINDINGS_AND_CONFLICTS.md:613), [RFE-13](SOURCE_FINDINGS_AND_CONFLICTS.md:614), [RFE-14](SOURCE_FINDINGS_AND_CONFLICTS.md:615), [K18-01](SOURCE_FINDINGS_AND_CONFLICTS.md:652), [K18-02](SOURCE_FINDINGS_AND_CONFLICTS.md:653), [K18-03](SOURCE_FINDINGS_AND_CONFLICTS.md:654), [K18-04](SOURCE_FINDINGS_AND_CONFLICTS.md:655), [K18-05](SOURCE_FINDINGS_AND_CONFLICTS.md:656), [K18-06](SOURCE_FINDINGS_AND_CONFLICTS.md:657), [K18-07](SOURCE_FINDINGS_AND_CONFLICTS.md:658), [K18-08](SOURCE_FINDINGS_AND_CONFLICTS.md:659), [F23-02](SOURCE_FINDINGS_AND_CONFLICTS.md:668), [F23-04](SOURCE_FINDINGS_AND_CONFLICTS.md:670), [CCS-01](SOURCE_FINDINGS_AND_CONFLICTS.md:681), [CCS-02](SOURCE_FINDINGS_AND_CONFLICTS.md:682), [CCS-03](SOURCE_FINDINGS_AND_CONFLICTS.md:683), [CCS-04](SOURCE_FINDINGS_AND_CONFLICTS.md:684), [CCS-05](SOURCE_FINDINGS_AND_CONFLICTS.md:685), [CCS-06](SOURCE_FINDINGS_AND_CONFLICTS.md:686), [CCS-07](SOURCE_FINDINGS_AND_CONFLICTS.md:687), [CCS-08](SOURCE_FINDINGS_AND_CONFLICTS.md:688), [TBR-01](SOURCE_FINDINGS_AND_CONFLICTS.md:736), [TBR-02](SOURCE_FINDINGS_AND_CONFLICTS.md:737), [TBR-03](SOURCE_FINDINGS_AND_CONFLICTS.md:738), [TBR-04](SOURCE_FINDINGS_AND_CONFLICTS.md:739), [TBR-05](SOURCE_FINDINGS_AND_CONFLICTS.md:740), [TBR-06](SOURCE_FINDINGS_AND_CONFLICTS.md:741), [TBR-07](SOURCE_FINDINGS_AND_CONFLICTS.md:742).

**Conversation upgrade lineage.** [DTM-A13](SOURCE_FINDINGS_AND_CONFLICTS.md:71), [JCV-A02](SOURCE_FINDINGS_AND_CONFLICTS.md:161), [CRL-13](SOURCE_FINDINGS_AND_CONFLICTS.md:229), [CRL-14](SOURCE_FINDINGS_AND_CONFLICTS.md:230). Read the full rows and their original conversation references; [the recheck](CONVERSATION_RECHECK.md) preserves the exact unit/exception routes.

<a id="up-r15-protection"></a>
#### R15.PROTECTION — Causal protected structure

[Existing definition, target and P0–P7](experiments/R.md#r15-protection) remain binding.

**Specific upgrade scope.** Use context-residual reward, cumulative pressure, fresh defense and age to estimate protection strength/lifetime.

**Local comparison.** Compare source protected swing, price-only trail, raw markout and residual survival/value at actual confirmation times.

**Additional cases.** Trend rewards every origin; markout not mature; later depletion; role reversal.

<a id="up-r16"></a>
### UP-R16 — Minor-node and intra-wick repeated reactions

Parent: [R16](components/RESPONSE_DEFERRED.md); [local phases](experiments/R.md#r16); [definition refinement](SYSTEM_REFINEMENT.md#sr-r16). Upgrade role: `forecast`.

**Starting idea.** Repeated tiny reactions inside a wick identify a precise level.

**Existing improvement path.** Frozen neighboring nodes, causal interaction, overshoot/reclaim and current footprint evidence.

**Remaining weakness.** Sparse exact-price reactions encourage overprecise levels and retrospective selection of a visually attractive wick point.

**Further upgrade.** Model reaction intensity across a local price band with uncertainty and neighboring-region competition; shrink repeated responses by common episode and compare band-based versus exact-tick anchors. Include overshoot depth, new pressure and whether the same reaction is counted by several nodes.

**Fair comparison.** Node-only/flow-only, exact-tick source, uncertainty-band summaries and spatial conditional model.

**Evidence.** Out-of-sample location precision, useful reaction/runner calibration, net after spread and effective episode count.

**Additional local cases to implement.** One wiggle touches several nodes; final wick unavailable; sparse minor peak; neighboring level explains reaction.

**Decision or system use.** Assess whether minor structure earns a tradable precision improvement over a broader known region.

**Exact reviewed source clauses.** [RDL-01](SOURCE_FINDINGS_AND_CONFLICTS.md:550), [RDL-02](SOURCE_FINDINGS_AND_CONFLICTS.md:551), [RDL-03](SOURCE_FINDINGS_AND_CONFLICTS.md:552), [RDL-04](SOURCE_FINDINGS_AND_CONFLICTS.md:553), [RDL-05](SOURCE_FINDINGS_AND_CONFLICTS.md:554), [RDL-06](SOURCE_FINDINGS_AND_CONFLICTS.md:555), [RDL-07](SOURCE_FINDINGS_AND_CONFLICTS.md:556), [YMA-03](SOURCE_FINDINGS_AND_CONFLICTS.md:591), [CCS-06](SOURCE_FINDINGS_AND_CONFLICTS.md:686), [OBT-04](SOURCE_FINDINGS_AND_CONFLICTS.md:753), [OBT-05](SOURCE_FINDINGS_AND_CONFLICTS.md:754).

<a id="up-r16-anchor_detail"></a>
#### R16.ANCHOR_DETAIL — Minor-node and intra-wick alternatives

[Existing definition, target and P0–P7](experiments/R.md#r16-anchor_detail) remain binding.

**Specific upgrade scope.** Compare exact-tick minor/wick references with support-weighted spatial bands and neighboring-region competition.

**Local comparison.** Control width/count and shared episodes; assess whether precision survives spread and actual timing.

**Additional cases.** One wiggle touches many nodes; final wick unavailable; sparse peak; neighboring level explains reaction.

<a id="up-r17"></a>
### UP-R17 — First, second and later defended retests

Parent: [R17](components/RESPONSE_DEFERRED.md); [local phases](experiments/R.md#r17); [definition refinement](SYSTEM_REFINEMENT.md#sr-r17). Upgrade role: `forecast`.

**Starting idea.** Prefer the first or second defended retest.

**Existing improvement path.** Causal visit separation, cumulative testing and hierarchical durability/depletion hazards.

**Remaining weakness.** Visit number is a weak proxy when visits differ in pressure, recovery, duration and fresh evidence.

**Further upgrade.** Replace count-only strength with cumulative pressure dose, recovery history, time since last defense and evidence novelty; keep visit count as an explicit comparator. Use recurrent-event transitions with shared object/episode effects and reset only under registered lifecycle rules.

**Fair comparison.** First/second/count rules, existing repeat hazard and pressure-dose/renewal model.

**Evidence.** Visit-conditioned calibration, cumulative idea net/loss, false visit counts and sparse-late-visit uncertainty.

**Additional local cases to implement.** Several flickers are one visit; second visit much weaker; refreshed evidence after long pause; object split/reidentified.

**Decision or system use.** Distinguish depletion from renewed defense using the history that actually changed the object's state.

**Exact reviewed source clauses.** [WIC-01](SOURCE_FINDINGS_AND_CONFLICTS.md:577), [WIC-02](SOURCE_FINDINGS_AND_CONFLICTS.md:578), [WIC-03](SOURCE_FINDINGS_AND_CONFLICTS.md:579), [WIC-04](SOURCE_FINDINGS_AND_CONFLICTS.md:580), [WIC-05](SOURCE_FINDINGS_AND_CONFLICTS.md:581), [WIC-06](SOURCE_FINDINGS_AND_CONFLICTS.md:582), [WIC-07](SOURCE_FINDINGS_AND_CONFLICTS.md:583), [NYA-01](SOURCE_FINDINGS_AND_CONFLICTS.md:709), [NYA-02](SOURCE_FINDINGS_AND_CONFLICTS.md:710), [NYA-03](SOURCE_FINDINGS_AND_CONFLICTS.md:711), [NYA-04](SOURCE_FINDINGS_AND_CONFLICTS.md:712), [NYA-05](SOURCE_FINDINGS_AND_CONFLICTS.md:713), [NYA-06](SOURCE_FINDINGS_AND_CONFLICTS.md:714), [SRE-01](SOURCE_FINDINGS_AND_CONFLICTS.md:722), [SRE-02](SOURCE_FINDINGS_AND_CONFLICTS.md:723), [SRE-03](SOURCE_FINDINGS_AND_CONFLICTS.md:724), [SRE-04](SOURCE_FINDINGS_AND_CONFLICTS.md:725), [SRE-05](SOURCE_FINDINGS_AND_CONFLICTS.md:726), [SRE-06](SOURCE_FINDINGS_AND_CONFLICTS.md:727), [SRE-07](SOURCE_FINDINGS_AND_CONFLICTS.md:728), [TBR-01](SOURCE_FINDINGS_AND_CONFLICTS.md:736), [TBR-02](SOURCE_FINDINGS_AND_CONFLICTS.md:737), [TBR-03](SOURCE_FINDINGS_AND_CONFLICTS.md:738), [TBR-04](SOURCE_FINDINGS_AND_CONFLICTS.md:739), [TBR-05](SOURCE_FINDINGS_AND_CONFLICTS.md:740), [TBR-06](SOURCE_FINDINGS_AND_CONFLICTS.md:741), [TBR-07](SOURCE_FINDINGS_AND_CONFLICTS.md:742).

<a id="up-r17-visits"></a>
#### R17.VISITS — First, second and later visit selection

[Existing definition, target and P0–P7](experiments/R.md#r17-visits) remain binding.

**Specific upgrade scope.** Add pressure dose, recovery history, novelty and time away to each causal first/second/later visit.

**Local comparison.** Compare count-only and recurrent-event renewal/depletion models with partial pooling and cumulative idea budgets.

**Additional cases.** Flickers are one visit; second visit stronger; refreshed object ID; sparse late visits.

<a id="up-r18"></a>
### UP-R18 — Jumbo sweep, order-block and rejection-block entries

Parent: [R18](components/RESPONSE_DEFERRED.md); [local phases](experiments/R.md#r18); [definition refinement](SYSTEM_REFINEMENT.md#sr-r18). Upgrade role: `decision`.

**Starting idea.** Enter a completed sweep/block with one fixed midpoint rule.

**Existing improvement path.** Faithful source timeframe, entry, stop, rejection and failure-through branches.

**Remaining weakness.** Bar alignment and discrete candle completion can dominate apparent setup quality and delay execution.

**Further upgrade.** Add an event-time sweep/reclaim trajectory using the same frozen source anchors, plus continuous overshoot, reclaim speed and retained displacement. Compare it to each exact candle/timeframe variant with matched information-delay and executable-entry budgets; optimize entry/stop only in their registered joint grid.

**Fair comparison.** Faithful 2/3/5-minute variants, corrected causal variants, event-time summaries and conditional action model.

**Evidence.** Source fidelity, sensitivity to bar phase, prefix path calibration and complete one-mini net/risk.

**Additional local cases to implement.** Signal exists under one bar alignment; no retracement fill; confirmation after move; failure-through momentum; stop rounds beyond budget.

**Decision or system use.** Test whether continuous causal geometry improves the timing and robustness of the preserved source patterns.

**Exact reviewed source clauses.** [JTR-11](SOURCE_FINDINGS_AND_CONFLICTS.md:28), [JTR-16](SOURCE_FINDINGS_AND_CONFLICTS.md:33), [JTR-17](SOURCE_FINDINGS_AND_CONFLICTS.md:34), [JTR-24](SOURCE_FINDINGS_AND_CONFLICTS.md:41), [JXA-24](SOURCE_FINDINGS_AND_CONFLICTS.md:123), [OSF-01](SOURCE_FINDINGS_AND_CONFLICTS.md:795), [OSF-02](SOURCE_FINDINGS_AND_CONFLICTS.md:796), [OSF-03](SOURCE_FINDINGS_AND_CONFLICTS.md:797), [OSF-04](SOURCE_FINDINGS_AND_CONFLICTS.md:798), [OSF-05](SOURCE_FINDINGS_AND_CONFLICTS.md:799), [OSF-06](SOURCE_FINDINGS_AND_CONFLICTS.md:800), [OSF-07](SOURCE_FINDINGS_AND_CONFLICTS.md:801), [OSF-08](SOURCE_FINDINGS_AND_CONFLICTS.md:802), [OSF-09](SOURCE_FINDINGS_AND_CONFLICTS.md:803), [OSF-10](SOURCE_FINDINGS_AND_CONFLICTS.md:804), [PIN010-01](SOURCE_FINDINGS_AND_CONFLICTS.md:841), [PIN010-02](SOURCE_FINDINGS_AND_CONFLICTS.md:842), [PIN010-03](SOURCE_FINDINGS_AND_CONFLICTS.md:843), [PIN010-04](SOURCE_FINDINGS_AND_CONFLICTS.md:844), [PIN022-01](SOURCE_FINDINGS_AND_CONFLICTS.md:894), [PIN022-02](SOURCE_FINDINGS_AND_CONFLICTS.md:895), [PIN022-03](SOURCE_FINDINGS_AND_CONFLICTS.md:896), [PIN023-01](SOURCE_FINDINGS_AND_CONFLICTS.md:897), [PIN023-02](SOURCE_FINDINGS_AND_CONFLICTS.md:898), [PIN035-01](SOURCE_FINDINGS_AND_CONFLICTS.md:920), [PIN035-02](SOURCE_FINDINGS_AND_CONFLICTS.md:921), [PIN035-03](SOURCE_FINDINGS_AND_CONFLICTS.md:922), [PIN035-04](SOURCE_FINDINGS_AND_CONFLICTS.md:923), [PIN071-01](SOURCE_FINDINGS_AND_CONFLICTS.md:1036), [PIN071-02](SOURCE_FINDINGS_AND_CONFLICTS.md:1037), [PIN071-03](SOURCE_FINDINGS_AND_CONFLICTS.md:1038), [PIN071-04](SOURCE_FINDINGS_AND_CONFLICTS.md:1039), [PIN071-05](SOURCE_FINDINGS_AND_CONFLICTS.md:1040), [PIN071-06](SOURCE_FINDINGS_AND_CONFLICTS.md:1041), [PIN071-07](SOURCE_FINDINGS_AND_CONFLICTS.md:1042), [PIN071-08](SOURCE_FINDINGS_AND_CONFLICTS.md:1043).

<a id="up-r18-stop_interpretations"></a>
#### R18.STOP_INTERPRETATIONS — Sweep/block source alternatives

[Existing definition, target and P0–P7](experiments/R.md#r18-stop_interpretations) remain binding.

**Specific upgrade scope.** Pair every source confirmation/midpoint/extreme entry-stop interpretation with continuous event-time sweep/reclaim quality.

**Local comparison.** Match source timeframe and bar-phase alternatives, actual confirmation delay, nonfill and complete bracket feasibility.

**Additional cases.** Midpoint never returns; 2/3/5-minute phase; caption/drawing conflict; failure-through branch.

<a id="up-r19"></a>
### UP-R19 — Response-to-action and residual-management adapter

Parent: [R19](components/RESPONSE_DEFERRED.md); [local phases](experiments/R.md#r19); [definition refinement](SYSTEM_REFINEMENT.md#sr-r19). Upgrade role: `decision`.

**Starting idea.** Require Response confirmation for every entry and use it for exits too.

**Existing improvement path.** Separate entry filtering, timing refinement and residual management on frozen C/L opportunities.

**Remaining weakness.** A single ablation can hide whether Response helps information quality, changes entry price or merely rejects hard trades.

**Further upgrade.** Use a factorial action adapter comparing no Response, filter only, timing only, management only and prespecified combinations on the same initial opportunity ledger. Model paired incremental policy value at each actual prefix and remaining horizon, including skipped trades and occupancy.

**Fair comparison.** Direct C/L, simple price confirmation, each Response role and bounded combined policies.

**Evidence.** Full-day net, role-specific incremental value, selection/population effects, delay cost and complexity.

**Additional local cases to implement.** Filter improves hit rate but loses net; exit signal useful without entry signal; delayed entry changes stop feasibility.

**Decision or system use.** Assign Response only the roles for which it adds evidence-backed value to the complete policy.

**Exact reviewed source clauses.** [DTM-A14](SOURCE_FINDINGS_AND_CONFLICTS.md:72), [JCV-A08](SOURCE_FINDINGS_AND_CONFLICTS.md:167), [CRL-07](SOURCE_FINDINGS_AND_CONFLICTS.md:223), [CD1-01](SOURCE_FINDINGS_AND_CONFLICTS.md:394), [CD1-02](SOURCE_FINDINGS_AND_CONFLICTS.md:395), [CD1-03](SOURCE_FINDINGS_AND_CONFLICTS.md:396), [CD1-04](SOURCE_FINDINGS_AND_CONFLICTS.md:397), [CD1-05](SOURCE_FINDINGS_AND_CONFLICTS.md:398), [DRF-U11](SOURCE_FINDINGS_AND_CONFLICTS.md:435), [DRF-A24](SOURCE_FINDINGS_AND_CONFLICTS.md:465), [OFM-01](SOURCE_FINDINGS_AND_CONFLICTS.md:623), [OFM-02](SOURCE_FINDINGS_AND_CONFLICTS.md:624), [OFM-03](SOURCE_FINDINGS_AND_CONFLICTS.md:625), [OFM-04](SOURCE_FINDINGS_AND_CONFLICTS.md:626), [OFM-05](SOURCE_FINDINGS_AND_CONFLICTS.md:627), [OFM-06](SOURCE_FINDINGS_AND_CONFLICTS.md:628), [OFM-07](SOURCE_FINDINGS_AND_CONFLICTS.md:629), [OFM-08](SOURCE_FINDINGS_AND_CONFLICTS.md:630), [OFM-09](SOURCE_FINDINGS_AND_CONFLICTS.md:631), [ALS-01](SOURCE_FINDINGS_AND_CONFLICTS.md:696), [ALS-02](SOURCE_FINDINGS_AND_CONFLICTS.md:697), [ALS-03](SOURCE_FINDINGS_AND_CONFLICTS.md:698), [ALS-04](SOURCE_FINDINGS_AND_CONFLICTS.md:699), [ALS-05](SOURCE_FINDINGS_AND_CONFLICTS.md:700), [ALS-06](SOURCE_FINDINGS_AND_CONFLICTS.md:701).

**Conversation upgrade lineage.** [DTM-A14](SOURCE_FINDINGS_AND_CONFLICTS.md:72), [JCV-A08](SOURCE_FINDINGS_AND_CONFLICTS.md:167), [CRL-07](SOURCE_FINDINGS_AND_CONFLICTS.md:223), [DRF-U11](SOURCE_FINDINGS_AND_CONFLICTS.md:435), [DRF-A15](SOURCE_FINDINGS_AND_CONFLICTS.md:456). Read the full rows and their original conversation references; [the recheck](CONVERSATION_RECHECK.md) preserves the exact unit/exception routes.

<a id="up-r19-entry_exit"></a>
#### R19.ENTRY_EXIT — Independent Response timing and management roles

[Existing definition, target and P0–P7](experiments/R.md#r19-entry_exit) remain binding.

**Specific upgrade scope.** Run a factorial adapter for Response filter, entry timing, full-position management and prespecified combinations.

**Local comparison.** Keep the original C/L opportunity ledger and compare paired full-policy values, separating population selection from information.

**Additional cases.** Hit rate improves but net falls; exits useful without entries; delay changes stop feasibility; occupancy.

<a id="up-r20"></a>
### UP-R20 — Pine structural and oscillator timing hypotheses

Parent: [R20](components/RESPONSE_DEFERRED.md); [local phases](experiments/R.md#r20); [definition refinement](SYSTEM_REFINEMENT.md#sr-r20). Upgrade role: `measurement`.

**Starting idea.** Use visual Pine patterns and oscillator crosses as fixed signals.

**Existing improvement path.** Every preserved source member has faithful computable and corrected causal variants.

**Remaining weakness.** Binary pattern names discard continuous geometry, parameter stability and overlap among nearly identical scripts.

**Further upgrade.** For every registered member-specific family, extract causal continuous distances, run lengths, overlap/repair fractions, pivot age and oscillator divergence magnitude alongside the exact source rule. Compare a small regularized shared feature basis with family-specific residuals, controlled parameter perturbations and bar-phase tests; retain script-specific exceptions.

**Fair comparison.** Each original/corrected rule, continuous feature baseline and pooled/family-residual challenger with identical source eligibility.

**Evidence.** Member-level fidelity, parameter/phase stability, incremental forecast/net value and redundancy.

**Additional local cases to implement.** Pivot confirmation lag; expanding window changes anchor; repair versus cross-section sequence; threshold near equality; missing source tail.

**Decision or system use.** Upgrade each executable source mechanism through measurable geometry, while unsupported text remains an explicit dependency rather than an invented formula.

**Exact reviewed source clauses.** [JXA-26](SOURCE_FINDINGS_AND_CONFLICTS.md:125), [OSF-01](SOURCE_FINDINGS_AND_CONFLICTS.md:795), [OSF-02](SOURCE_FINDINGS_AND_CONFLICTS.md:796), [OSF-03](SOURCE_FINDINGS_AND_CONFLICTS.md:797), [OSF-04](SOURCE_FINDINGS_AND_CONFLICTS.md:798), [OSF-05](SOURCE_FINDINGS_AND_CONFLICTS.md:799), [OSF-06](SOURCE_FINDINGS_AND_CONFLICTS.md:800), [OSF-07](SOURCE_FINDINGS_AND_CONFLICTS.md:801), [OSF-08](SOURCE_FINDINGS_AND_CONFLICTS.md:802), [OSF-09](SOURCE_FINDINGS_AND_CONFLICTS.md:803), [OSF-10](SOURCE_FINDINGS_AND_CONFLICTS.md:804), [PIN008-01](SOURCE_FINDINGS_AND_CONFLICTS.md:824), [PIN009-01](SOURCE_FINDINGS_AND_CONFLICTS.md:825), [PIN009-02](SOURCE_FINDINGS_AND_CONFLICTS.md:826), [PIN005-02](SOURCE_FINDINGS_AND_CONFLICTS.md:829), [PIN005-03](SOURCE_FINDINGS_AND_CONFLICTS.md:830), [PIN005-04](SOURCE_FINDINGS_AND_CONFLICTS.md:831), [PIN005-05](SOURCE_FINDINGS_AND_CONFLICTS.md:832), [PIN010-01](SOURCE_FINDINGS_AND_CONFLICTS.md:841), [PIN010-02](SOURCE_FINDINGS_AND_CONFLICTS.md:842), [PIN010-03](SOURCE_FINDINGS_AND_CONFLICTS.md:843), [PIN010-04](SOURCE_FINDINGS_AND_CONFLICTS.md:844), [PIN011-01](SOURCE_FINDINGS_AND_CONFLICTS.md:845), [PIN011-02](SOURCE_FINDINGS_AND_CONFLICTS.md:846), [PIN011-03](SOURCE_FINDINGS_AND_CONFLICTS.md:847), [PIN011-04](SOURCE_FINDINGS_AND_CONFLICTS.md:848), [PIN011-05](SOURCE_FINDINGS_AND_CONFLICTS.md:849), [PIN011-06](SOURCE_FINDINGS_AND_CONFLICTS.md:850), [PIN011-07](SOURCE_FINDINGS_AND_CONFLICTS.md:851), [PIN017-01](SOURCE_FINDINGS_AND_CONFLICTS.md:872), [PIN017-02](SOURCE_FINDINGS_AND_CONFLICTS.md:873), [PIN017-03](SOURCE_FINDINGS_AND_CONFLICTS.md:874), [PIN017-04](SOURCE_FINDINGS_AND_CONFLICTS.md:875), [PIN019-01](SOURCE_FINDINGS_AND_CONFLICTS.md:887), [PIN019-02](SOURCE_FINDINGS_AND_CONFLICTS.md:888), [PIN019-03](SOURCE_FINDINGS_AND_CONFLICTS.md:889), [PIN020-01](SOURCE_FINDINGS_AND_CONFLICTS.md:890), [PIN020-02](SOURCE_FINDINGS_AND_CONFLICTS.md:891), [PIN022-01](SOURCE_FINDINGS_AND_CONFLICTS.md:894), [PIN022-02](SOURCE_FINDINGS_AND_CONFLICTS.md:895), [PIN022-03](SOURCE_FINDINGS_AND_CONFLICTS.md:896), [PIN023-01](SOURCE_FINDINGS_AND_CONFLICTS.md:897), [PIN023-02](SOURCE_FINDINGS_AND_CONFLICTS.md:898), [PIN031-01](SOURCE_FINDINGS_AND_CONFLICTS.md:913), [PIN032-01](SOURCE_FINDINGS_AND_CONFLICTS.md:914), [PIN032-02](SOURCE_FINDINGS_AND_CONFLICTS.md:915), [PIN032-03](SOURCE_FINDINGS_AND_CONFLICTS.md:916), [PIN033-01](SOURCE_FINDINGS_AND_CONFLICTS.md:917), [PIN033-02](SOURCE_FINDINGS_AND_CONFLICTS.md:918), [PIN034-01](SOURCE_FINDINGS_AND_CONFLICTS.md:919), [PIN035-01](SOURCE_FINDINGS_AND_CONFLICTS.md:920), [PIN035-02](SOURCE_FINDINGS_AND_CONFLICTS.md:921), [PIN035-03](SOURCE_FINDINGS_AND_CONFLICTS.md:922), [PIN035-04](SOURCE_FINDINGS_AND_CONFLICTS.md:923), [PIN036-01](SOURCE_FINDINGS_AND_CONFLICTS.md:925), [PIN036-02](SOURCE_FINDINGS_AND_CONFLICTS.md:926), [PIN037-01](SOURCE_FINDINGS_AND_CONFLICTS.md:927), [PIN037-02](SOURCE_FINDINGS_AND_CONFLICTS.md:928), [PIN038-01](SOURCE_FINDINGS_AND_CONFLICTS.md:930), [PIN038-02](SOURCE_FINDINGS_AND_CONFLICTS.md:931), [PIN050-01](SOURCE_FINDINGS_AND_CONFLICTS.md:968), [PIN050-02](SOURCE_FINDINGS_AND_CONFLICTS.md:969), [PIN050-03](SOURCE_FINDINGS_AND_CONFLICTS.md:970), [PIN051-01](SOURCE_FINDINGS_AND_CONFLICTS.md:971), [PIN051-02](SOURCE_FINDINGS_AND_CONFLICTS.md:972), [PIN056-01](SOURCE_FINDINGS_AND_CONFLICTS.md:983), [PIN056-02](SOURCE_FINDINGS_AND_CONFLICTS.md:984), [PIN060-01](SOURCE_FINDINGS_AND_CONFLICTS.md:993), [PIN060-02](SOURCE_FINDINGS_AND_CONFLICTS.md:994), [PIN060-03](SOURCE_FINDINGS_AND_CONFLICTS.md:995), [PIN071-01](SOURCE_FINDINGS_AND_CONFLICTS.md:1036), [PIN071-02](SOURCE_FINDINGS_AND_CONFLICTS.md:1037), [PIN071-03](SOURCE_FINDINGS_AND_CONFLICTS.md:1038), [PIN071-04](SOURCE_FINDINGS_AND_CONFLICTS.md:1039), [PIN071-05](SOURCE_FINDINGS_AND_CONFLICTS.md:1040), [PIN071-06](SOURCE_FINDINGS_AND_CONFLICTS.md:1041), [PIN071-07](SOURCE_FINDINGS_AND_CONFLICTS.md:1042), [PIN071-08](SOURCE_FINDINGS_AND_CONFLICTS.md:1043), [PIN072-01](SOURCE_FINDINGS_AND_CONFLICTS.md:1045), [PIN072-02](SOURCE_FINDINGS_AND_CONFLICTS.md:1046), [PIN079-01](SOURCE_FINDINGS_AND_CONFLICTS.md:1066), [PIN079-02](SOURCE_FINDINGS_AND_CONFLICTS.md:1067), [PIN079-03](SOURCE_FINDINGS_AND_CONFLICTS.md:1068), [PIN079-04](SOURCE_FINDINGS_AND_CONFLICTS.md:1069).

**Conversation upgrade lineage.** [CRL-18](SOURCE_FINDINGS_AND_CONFLICTS.md:234). Read the full rows and their original conversation references; [the recheck](CONVERSATION_RECHECK.md) preserves the exact unit/exception routes.

<a id="up-r20-causal_variants"></a>
#### R20.CAUSAL_VARIANTS — Every preserved Pine timing family

[Existing definition, target and P0–P7](experiments/R.md#r20-causal_variants) remain binding.

**Specific upgrade scope.** Apply continuous geometry/run-length/repair/pivot-age/divergence features to every member-specific source family beside its faithful and corrected rule.

**Local comparison.** Retain each exact inequality, reset and mitigation clause; compare pooled/family residual models with parameter and bar-phase controls.

**Additional cases.** Pivot backplot; expansive/protrend sweep; CISD run; repair/fork/cross-section ordering; missing source tail.

<a id="up-r21"></a>
### UP-R21 — Context-conditioned sequence alternatives

Parent: [R21](components/RESPONSE_DEFERRED.md); [local phases](experiments/R.md#r21); [definition refinement](SYSTEM_REFINEMENT.md#sr-r21). Upgrade role: `forecast`.

**Starting idea.** Hard-gate one response style by a broad context label.

**Existing improvement path.** Distinct sequence experts with soft Context/coverage mixtures and hard-gate comparators.

**Remaining weakness.** Regime labels can abruptly disable useful alternatives, and contextual effects may be sparse or duplicated across experts.

**Further upgrade.** Compare a regularized interaction basis and hierarchical residual gates that let common sequence evidence share strength while preserving branch-specific effects. Use continuous Context state and uncertainty, evaluate hard/soft alignment as alternatives, and shrink unsupported interactions toward pooled behavior.

**Fair comparison.** Hard source gates, uniform mixture, existing soft gate and hierarchical interaction/residual model.

**Evidence.** Proper loss by supported context, gate stability, net incremental value and missing-context robustness.

**Additional local cases to implement.** Higher-timeframe trend with local fade; ambiguous options scenario; rare transition; duplicated context in experts and gate.

**Decision or system use.** Learn where each sequence contributes without assuming one broad market narrative determines all permissible actions.

**Exact reviewed source clauses.** [CRL-08](SOURCE_FINDINGS_AND_CONFLICTS.md:224), [CRL-13](SOURCE_FINDINGS_AND_CONFLICTS.md:229), [VX4-09](SOURCE_FINDINGS_AND_CONFLICTS.md:332), [DRF-A15](SOURCE_FINDINGS_AND_CONFLICTS.md:456), [GXF-13](SOURCE_FINDINGS_AND_CONFLICTS.md:497), [MAT-05](SOURCE_FINDINGS_AND_CONFLICTS.md:530), [MAT-09](SOURCE_FINDINGS_AND_CONFLICTS.md:534), [RVP-07](SOURCE_FINDINGS_AND_CONFLICTS.md:548), [YMA-01](SOURCE_FINDINGS_AND_CONFLICTS.md:589), [YMA-02](SOURCE_FINDINGS_AND_CONFLICTS.md:590), [YMA-03](SOURCE_FINDINGS_AND_CONFLICTS.md:591), [YMA-04](SOURCE_FINDINGS_AND_CONFLICTS.md:592), [YMA-05](SOURCE_FINDINGS_AND_CONFLICTS.md:593), [YMA-06](SOURCE_FINDINGS_AND_CONFLICTS.md:594), [CCS-04](SOURCE_FINDINGS_AND_CONFLICTS.md:684), [OBT-07](SOURCE_FINDINGS_AND_CONFLICTS.md:756), [OBT-08](SOURCE_FINDINGS_AND_CONFLICTS.md:757), [AUT-06](SOURCE_FINDINGS_AND_CONFLICTS.md:772).

<a id="up-r21-soft_context"></a>
#### R21.SOFT_CONTEXT — Context-dependent sequence mixtures

[Existing definition, target and P0–P7](experiments/R.md#r21-soft_context) remain binding.

**Specific upgrade scope.** Compare sparse interpretable Context interactions and hierarchical residual gates across all separate sequence experts.

**Local comparison.** Preserve source hard gates, uniform and existing soft mixture as distinct policies and evaluate supported context cells.

**Additional cases.** HTF trend with local fade; uncertain exposure scenario; duplicated Context input; rare transition.

<a id="up-r22"></a>
### UP-R22 — Blinded visual/source annotation and mechanism adjudication

Parent: [R22](components/RESPONSE_DEFERRED.md); [local phases](experiments/R.md#r22); [definition refinement](SYSTEM_REFINEMENT.md#sr-r22). Upgrade role: `research_method`.

**Starting idea.** Treat illustrative charts and narrative annotations as ground truth.

**Existing improvement path.** Blinded structured annotation with uncertainty and numeric/source adjudication.

**Remaining weakness.** Agreement on easy examples can hide ambiguous mechanism boundaries and unsupported visual inference.

**Further upgrade.** Create an annotation decision manual from observed geometry and causal prefixes, then sample both representative episodes and prespecified disagreement/edge cases. Compare numeric rules with independently blinded labels, estimate disagreement by clause and refine definitions on a development subset before a held-out annotation audit.

**Fair comparison.** Numeric reference, independent blinded annotation and optional image-assisted extraction evaluated against structured records.

**Evidence.** Clause-level reliability, ambiguity rate, price/time extraction accuracy and held-out definition stability.

**Additional local cases to implement.** Chart crop hides future confirmation; same image suggests two mechanisms; pending order mistaken for fill; annotator sees outcome.

**Decision or system use.** Turn visual ideas into reproducible definitions and locate unresolved source ambiguity before it contaminates empirical labels.

**Exact reviewed source clauses.** [CRL-16](SOURCE_FINDINGS_AND_CONFLICTS.md:232), [DRF-A16](SOURCE_FINDINGS_AND_CONFLICTS.md:457), [TBR-07](SOURCE_FINDINGS_AND_CONFLICTS.md:742), [AUT-07](SOURCE_FINDINGS_AND_CONFLICTS.md:773).

**Conversation upgrade lineage.** [CRL-01](SOURCE_FINDINGS_AND_CONFLICTS.md:217), [CRL-04](SOURCE_FINDINGS_AND_CONFLICTS.md:220), [CRL-16](SOURCE_FINDINGS_AND_CONFLICTS.md:232), [CRL-20](SOURCE_FINDINGS_AND_CONFLICTS.md:236), [DRF-A16](SOURCE_FINDINGS_AND_CONFLICTS.md:457). Read the full rows and their original conversation references; [the recheck](CONVERSATION_RECHECK.md) preserves the exact unit/exception routes.

<a id="up-r22-blinded_definition"></a>
#### R22.BLINDED_DEFINITION — Source annotation reliability

[Existing definition, target and P0–P7](experiments/R.md#r22-blinded_definition) remain binding.

**Specific upgrade scope.** Develop a clause-level annotation manual with causal prefixes and a held-out representative plus edge/disagreement audit.

**Local comparison.** Compare numeric rules, independent blinded labels and optional image-assisted extraction without outcome or identity authority.

**Additional cases.** Crop hides confirmation; two plausible mechanisms; pending order mistaken for fill; annotator sees future.

<a id="family-v"></a>
## Research and operations

<a id="up-v01"></a>
### UP-V01 — Label, opportunity and evidence artifact service

Parent: [V01](components/RESEARCH_AND_OPERATIONS.md); [local phases](experiments/V.md#v01); [definition refinement](SYSTEM_REFINEMENT.md#sr-v01). Upgrade role: `research_method`.

**Starting idea.** Label only taken trades or chart-selected successful reactions.

**Existing improvement path.** All-candidate labels, frozen targets, censoring and simulation provenance.

**Remaining weakness.** A correct label table may still overweight dense opportunities or obscure exactly which population an improvement concerns.

**Further upgrade.** Build a population-indexed label service with clock samples, source episodes, object births, contacts and policy trajectories as separate sampling frames. Record inclusion probabilities where defined by the sampling design, otherwise explicit unknown/unsupported weighting; preserve shared endpoint/report IDs and target transformations; generate explicit risk sets for each forecast.

**Fair comparison.** Taken-trade, all-contact and full decision-population diagnostics against the declared target population; never promote selected-only performance.

**Evidence.** Coverage, label/reference agreement, effective episodes/dates and population-sensitive score/economic differences.

**Additional local cases to implement.** One day with thousands of nodes; repeated prefixes share one endpoint; missing horizon; no-touch versus censor; changed candidate density.

**Decision or system use.** Every upgrade is judged on the opportunity population it would actually face, with proper source and phase ownership.

**Exact reviewed source clauses.** [JSS-01](SOURCE_FINDINGS_AND_CONFLICTS.md:11), [JSS-02](SOURCE_FINDINGS_AND_CONFLICTS.md:12), [JSS-03](SOURCE_FINDINGS_AND_CONFLICTS.md:13), [JSS-04](SOURCE_FINDINGS_AND_CONFLICTS.md:14), [JSS-05](SOURCE_FINDINGS_AND_CONFLICTS.md:15), [JSS-06](SOURCE_FINDINGS_AND_CONFLICTS.md:16), [JSS-07](SOURCE_FINDINGS_AND_CONFLICTS.md:17), [JTR-01](SOURCE_FINDINGS_AND_CONFLICTS.md:18), [JTR-02](SOURCE_FINDINGS_AND_CONFLICTS.md:19), [JTR-03](SOURCE_FINDINGS_AND_CONFLICTS.md:20), [JTR-04](SOURCE_FINDINGS_AND_CONFLICTS.md:21), [JTR-05](SOURCE_FINDINGS_AND_CONFLICTS.md:22), [JTR-06](SOURCE_FINDINGS_AND_CONFLICTS.md:23), [JTR-07](SOURCE_FINDINGS_AND_CONFLICTS.md:24), [JTR-08](SOURCE_FINDINGS_AND_CONFLICTS.md:25), [JTR-09](SOURCE_FINDINGS_AND_CONFLICTS.md:26), [JTR-10](SOURCE_FINDINGS_AND_CONFLICTS.md:27), [JTR-11](SOURCE_FINDINGS_AND_CONFLICTS.md:28), [JTR-12](SOURCE_FINDINGS_AND_CONFLICTS.md:29), [JTR-13](SOURCE_FINDINGS_AND_CONFLICTS.md:30), [JTR-14](SOURCE_FINDINGS_AND_CONFLICTS.md:31), [JTR-15](SOURCE_FINDINGS_AND_CONFLICTS.md:32), [JTR-16](SOURCE_FINDINGS_AND_CONFLICTS.md:33), [JTR-17](SOURCE_FINDINGS_AND_CONFLICTS.md:34), [JTR-18](SOURCE_FINDINGS_AND_CONFLICTS.md:35), [JTR-19](SOURCE_FINDINGS_AND_CONFLICTS.md:36), [JTR-20](SOURCE_FINDINGS_AND_CONFLICTS.md:37), [JTR-21](SOURCE_FINDINGS_AND_CONFLICTS.md:38), [JTR-22](SOURCE_FINDINGS_AND_CONFLICTS.md:39), [JTR-23](SOURCE_FINDINGS_AND_CONFLICTS.md:40), [JTR-24](SOURCE_FINDINGS_AND_CONFLICTS.md:41), [DTM-A15](SOURCE_FINDINGS_AND_CONFLICTS.md:73), [DTM-A18](SOURCE_FINDINGS_AND_CONFLICTS.md:76), [JXA-01](SOURCE_FINDINGS_AND_CONFLICTS.md:100), [JXA-02](SOURCE_FINDINGS_AND_CONFLICTS.md:101), [JXA-03](SOURCE_FINDINGS_AND_CONFLICTS.md:102), [JXA-04](SOURCE_FINDINGS_AND_CONFLICTS.md:103), [JXA-05](SOURCE_FINDINGS_AND_CONFLICTS.md:104), [JXA-06](SOURCE_FINDINGS_AND_CONFLICTS.md:105), [JXA-07](SOURCE_FINDINGS_AND_CONFLICTS.md:106), [JXA-08](SOURCE_FINDINGS_AND_CONFLICTS.md:107), [JXA-09](SOURCE_FINDINGS_AND_CONFLICTS.md:108), [JXA-10](SOURCE_FINDINGS_AND_CONFLICTS.md:109), [JXA-11](SOURCE_FINDINGS_AND_CONFLICTS.md:110), [JXA-12](SOURCE_FINDINGS_AND_CONFLICTS.md:111), [JXA-13](SOURCE_FINDINGS_AND_CONFLICTS.md:112), [JXA-14](SOURCE_FINDINGS_AND_CONFLICTS.md:113), [JXA-15](SOURCE_FINDINGS_AND_CONFLICTS.md:114), [JXA-16](SOURCE_FINDINGS_AND_CONFLICTS.md:115), [JXA-17](SOURCE_FINDINGS_AND_CONFLICTS.md:116), [JXA-18](SOURCE_FINDINGS_AND_CONFLICTS.md:117), [JXA-19](SOURCE_FINDINGS_AND_CONFLICTS.md:118), [JXA-20](SOURCE_FINDINGS_AND_CONFLICTS.md:119), [JXA-21](SOURCE_FINDINGS_AND_CONFLICTS.md:120), [JXA-22](SOURCE_FINDINGS_AND_CONFLICTS.md:121), [JXA-23](SOURCE_FINDINGS_AND_CONFLICTS.md:122), [JXA-24](SOURCE_FINDINGS_AND_CONFLICTS.md:123), [JXA-25](SOURCE_FINDINGS_AND_CONFLICTS.md:124), [JXA-26](SOURCE_FINDINGS_AND_CONFLICTS.md:125), [JFN-12](SOURCE_FINDINGS_AND_CONFLICTS.md:146), [CEX-01](SOURCE_FINDINGS_AND_CONFLICTS.md:183), [CEX-02](SOURCE_FINDINGS_AND_CONFLICTS.md:184), [CEX-18](SOURCE_FINDINGS_AND_CONFLICTS.md:200), [CEX-27](SOURCE_FINDINGS_AND_CONFLICTS.md:209), [CRL-15](SOURCE_FINDINGS_AND_CONFLICTS.md:231), [CRL-16](SOURCE_FINDINGS_AND_CONFLICTS.md:232), [CRL-20](SOURCE_FINDINGS_AND_CONFLICTS.md:236), [IMG-01](SOURCE_FINDINGS_AND_CONFLICTS.md:248), [IMG-02](SOURCE_FINDINGS_AND_CONFLICTS.md:249), [IMG-03](SOURCE_FINDINGS_AND_CONFLICTS.md:250), [IMG-04](SOURCE_FINDINGS_AND_CONFLICTS.md:251), [IMG-05](SOURCE_FINDINGS_AND_CONFLICTS.md:252), [IMG-06](SOURCE_FINDINGS_AND_CONFLICTS.md:253), [IMG-07](SOURCE_FINDINGS_AND_CONFLICTS.md:254), [DEN-01](SOURCE_FINDINGS_AND_CONFLICTS.md:409), [DEN-02](SOURCE_FINDINGS_AND_CONFLICTS.md:410), [DEN-03](SOURCE_FINDINGS_AND_CONFLICTS.md:411), [DEN-04](SOURCE_FINDINGS_AND_CONFLICTS.md:412), [DEN-05](SOURCE_FINDINGS_AND_CONFLICTS.md:413), [DRF-U12](SOURCE_FINDINGS_AND_CONFLICTS.md:436), [DRF-A07](SOURCE_FINDINGS_AND_CONFLICTS.md:448), [DRF-A18](SOURCE_FINDINGS_AND_CONFLICTS.md:459), [DRF-A25](SOURCE_FINDINGS_AND_CONFLICTS.md:466), [DRF-A28](SOURCE_FINDINGS_AND_CONFLICTS.md:469), [GXF-01](SOURCE_FINDINGS_AND_CONFLICTS.md:485), [GXF-02](SOURCE_FINDINGS_AND_CONFLICTS.md:486), [GXF-03](SOURCE_FINDINGS_AND_CONFLICTS.md:487), [GXF-04](SOURCE_FINDINGS_AND_CONFLICTS.md:488), [GXF-05](SOURCE_FINDINGS_AND_CONFLICTS.md:489), [GXF-06](SOURCE_FINDINGS_AND_CONFLICTS.md:490), [GXF-07](SOURCE_FINDINGS_AND_CONFLICTS.md:491), [GXF-08](SOURCE_FINDINGS_AND_CONFLICTS.md:492), [GXF-09](SOURCE_FINDINGS_AND_CONFLICTS.md:493), [GXF-10](SOURCE_FINDINGS_AND_CONFLICTS.md:494), [GXF-11](SOURCE_FINDINGS_AND_CONFLICTS.md:495), [GXF-12](SOURCE_FINDINGS_AND_CONFLICTS.md:496), [GXF-13](SOURCE_FINDINGS_AND_CONFLICTS.md:497), [MAT-01](SOURCE_FINDINGS_AND_CONFLICTS.md:526), [MAT-02](SOURCE_FINDINGS_AND_CONFLICTS.md:527), [MAT-03](SOURCE_FINDINGS_AND_CONFLICTS.md:528), [MAT-04](SOURCE_FINDINGS_AND_CONFLICTS.md:529), [MAT-05](SOURCE_FINDINGS_AND_CONFLICTS.md:530), [MAT-06](SOURCE_FINDINGS_AND_CONFLICTS.md:531), [MAT-07](SOURCE_FINDINGS_AND_CONFLICTS.md:532), [MAT-08](SOURCE_FINDINGS_AND_CONFLICTS.md:533), [MAT-09](SOURCE_FINDINGS_AND_CONFLICTS.md:534), [RFE-01](SOURCE_FINDINGS_AND_CONFLICTS.md:602), [RFE-02](SOURCE_FINDINGS_AND_CONFLICTS.md:603), [RFE-03](SOURCE_FINDINGS_AND_CONFLICTS.md:604), [RFE-04](SOURCE_FINDINGS_AND_CONFLICTS.md:605), [RFE-05](SOURCE_FINDINGS_AND_CONFLICTS.md:606), [RFE-06](SOURCE_FINDINGS_AND_CONFLICTS.md:607), [RFE-07](SOURCE_FINDINGS_AND_CONFLICTS.md:608), [RFE-08](SOURCE_FINDINGS_AND_CONFLICTS.md:609), [RFE-09](SOURCE_FINDINGS_AND_CONFLICTS.md:610), [RFE-10](SOURCE_FINDINGS_AND_CONFLICTS.md:611), [RFE-11](SOURCE_FINDINGS_AND_CONFLICTS.md:612), [RFE-12](SOURCE_FINDINGS_AND_CONFLICTS.md:613), [RFE-13](SOURCE_FINDINGS_AND_CONFLICTS.md:614), [RFE-14](SOURCE_FINDINGS_AND_CONFLICTS.md:615), [OFM-09](SOURCE_FINDINGS_AND_CONFLICTS.md:631), [SRE-01](SOURCE_FINDINGS_AND_CONFLICTS.md:722), [SRE-02](SOURCE_FINDINGS_AND_CONFLICTS.md:723), [SRE-03](SOURCE_FINDINGS_AND_CONFLICTS.md:724), [SRE-04](SOURCE_FINDINGS_AND_CONFLICTS.md:725), [SRE-05](SOURCE_FINDINGS_AND_CONFLICTS.md:726), [SRE-06](SOURCE_FINDINGS_AND_CONFLICTS.md:727), [SRE-07](SOURCE_FINDINGS_AND_CONFLICTS.md:728), [AUT-01](SOURCE_FINDINGS_AND_CONFLICTS.md:767), [AUT-02](SOURCE_FINDINGS_AND_CONFLICTS.md:768), [AUT-03](SOURCE_FINDINGS_AND_CONFLICTS.md:769), [AUT-04](SOURCE_FINDINGS_AND_CONFLICTS.md:770), [AUT-05](SOURCE_FINDINGS_AND_CONFLICTS.md:771), [AUT-06](SOURCE_FINDINGS_AND_CONFLICTS.md:772), [AUT-07](SOURCE_FINDINGS_AND_CONFLICTS.md:773), [AUT-08](SOURCE_FINDINGS_AND_CONFLICTS.md:774), [AUT-09](SOURCE_FINDINGS_AND_CONFLICTS.md:775), [AUT-10](SOURCE_FINDINGS_AND_CONFLICTS.md:776), [AUT-11](SOURCE_FINDINGS_AND_CONFLICTS.md:777), [PIN001-01](SOURCE_FINDINGS_AND_CONFLICTS.md:812), [PIN001-02](SOURCE_FINDINGS_AND_CONFLICTS.md:813), [PIN001-03](SOURCE_FINDINGS_AND_CONFLICTS.md:814), [PIN001-04](SOURCE_FINDINGS_AND_CONFLICTS.md:815), [PIN002-01](SOURCE_FINDINGS_AND_CONFLICTS.md:816), [PIN002-02](SOURCE_FINDINGS_AND_CONFLICTS.md:817), [PIN002-03](SOURCE_FINDINGS_AND_CONFLICTS.md:818), [PIN003-01](SOURCE_FINDINGS_AND_CONFLICTS.md:819), [PIN003-02](SOURCE_FINDINGS_AND_CONFLICTS.md:820), [PIN003-03](SOURCE_FINDINGS_AND_CONFLICTS.md:821), [PIN003-04](SOURCE_FINDINGS_AND_CONFLICTS.md:822), [PIN004-01](SOURCE_FINDINGS_AND_CONFLICTS.md:823), [PIN008-01](SOURCE_FINDINGS_AND_CONFLICTS.md:824), [PIN009-01](SOURCE_FINDINGS_AND_CONFLICTS.md:825), [PIN009-02](SOURCE_FINDINGS_AND_CONFLICTS.md:826), [PIN053-01](SOURCE_FINDINGS_AND_CONFLICTS.md:827), [PIN005-01](SOURCE_FINDINGS_AND_CONFLICTS.md:828), [PIN005-02](SOURCE_FINDINGS_AND_CONFLICTS.md:829), [PIN005-03](SOURCE_FINDINGS_AND_CONFLICTS.md:830), [PIN005-04](SOURCE_FINDINGS_AND_CONFLICTS.md:831), [PIN005-05](SOURCE_FINDINGS_AND_CONFLICTS.md:832), [PIN006-01](SOURCE_FINDINGS_AND_CONFLICTS.md:833), [PIN006-02](SOURCE_FINDINGS_AND_CONFLICTS.md:834), [PIN006-03](SOURCE_FINDINGS_AND_CONFLICTS.md:835), [PIN007-01](SOURCE_FINDINGS_AND_CONFLICTS.md:836), [PIN007-02](SOURCE_FINDINGS_AND_CONFLICTS.md:837), [PIN007-03](SOURCE_FINDINGS_AND_CONFLICTS.md:838), [PIN007-04](SOURCE_FINDINGS_AND_CONFLICTS.md:839), [PIN007-05](SOURCE_FINDINGS_AND_CONFLICTS.md:840), [PIN010-01](SOURCE_FINDINGS_AND_CONFLICTS.md:841), [PIN010-02](SOURCE_FINDINGS_AND_CONFLICTS.md:842), [PIN010-03](SOURCE_FINDINGS_AND_CONFLICTS.md:843), [PIN010-04](SOURCE_FINDINGS_AND_CONFLICTS.md:844), [PIN011-01](SOURCE_FINDINGS_AND_CONFLICTS.md:845), [PIN011-02](SOURCE_FINDINGS_AND_CONFLICTS.md:846), [PIN011-03](SOURCE_FINDINGS_AND_CONFLICTS.md:847), [PIN011-04](SOURCE_FINDINGS_AND_CONFLICTS.md:848), [PIN011-05](SOURCE_FINDINGS_AND_CONFLICTS.md:849), [PIN011-06](SOURCE_FINDINGS_AND_CONFLICTS.md:850), [PIN011-07](SOURCE_FINDINGS_AND_CONFLICTS.md:851), [PIN012-01](SOURCE_FINDINGS_AND_CONFLICTS.md:852), [PIN012-02](SOURCE_FINDINGS_AND_CONFLICTS.md:853), [PIN012-03](SOURCE_FINDINGS_AND_CONFLICTS.md:854), [PIN012-04](SOURCE_FINDINGS_AND_CONFLICTS.md:855), [PIN012-05](SOURCE_FINDINGS_AND_CONFLICTS.md:856), [PIN013-01](SOURCE_FINDINGS_AND_CONFLICTS.md:857), [PIN013-02](SOURCE_FINDINGS_AND_CONFLICTS.md:858), [PIN013-03](SOURCE_FINDINGS_AND_CONFLICTS.md:859), [PIN013-04](SOURCE_FINDINGS_AND_CONFLICTS.md:860), [PIN013-05](SOURCE_FINDINGS_AND_CONFLICTS.md:861), [PIN013-06](SOURCE_FINDINGS_AND_CONFLICTS.md:862), [PIN014-01](SOURCE_FINDINGS_AND_CONFLICTS.md:863), [PIN014-02](SOURCE_FINDINGS_AND_CONFLICTS.md:864), [PIN015-01](SOURCE_FINDINGS_AND_CONFLICTS.md:865), [PIN015-02](SOURCE_FINDINGS_AND_CONFLICTS.md:866), [PIN015-03](SOURCE_FINDINGS_AND_CONFLICTS.md:867), [PIN016-01](SOURCE_FINDINGS_AND_CONFLICTS.md:868), [PIN016-02](SOURCE_FINDINGS_AND_CONFLICTS.md:869), [PIN016-03](SOURCE_FINDINGS_AND_CONFLICTS.md:870), [PIN016-04](SOURCE_FINDINGS_AND_CONFLICTS.md:871), [PIN017-01](SOURCE_FINDINGS_AND_CONFLICTS.md:872), [PIN017-02](SOURCE_FINDINGS_AND_CONFLICTS.md:873), [PIN017-03](SOURCE_FINDINGS_AND_CONFLICTS.md:874), [PIN017-04](SOURCE_FINDINGS_AND_CONFLICTS.md:875), [PIN018-01](SOURCE_FINDINGS_AND_CONFLICTS.md:876), [PIN018-02](SOURCE_FINDINGS_AND_CONFLICTS.md:877), [PIN024-01](SOURCE_FINDINGS_AND_CONFLICTS.md:878), [PIN024-02](SOURCE_FINDINGS_AND_CONFLICTS.md:879), [PIN019-01](SOURCE_FINDINGS_AND_CONFLICTS.md:887), [PIN019-02](SOURCE_FINDINGS_AND_CONFLICTS.md:888), [PIN019-03](SOURCE_FINDINGS_AND_CONFLICTS.md:889), [PIN020-01](SOURCE_FINDINGS_AND_CONFLICTS.md:890), [PIN020-02](SOURCE_FINDINGS_AND_CONFLICTS.md:891), [PIN021-01](SOURCE_FINDINGS_AND_CONFLICTS.md:892), [PIN021-02](SOURCE_FINDINGS_AND_CONFLICTS.md:893), [PIN022-01](SOURCE_FINDINGS_AND_CONFLICTS.md:894), [PIN022-02](SOURCE_FINDINGS_AND_CONFLICTS.md:895), [PIN022-03](SOURCE_FINDINGS_AND_CONFLICTS.md:896), [PIN023-01](SOURCE_FINDINGS_AND_CONFLICTS.md:897), [PIN023-02](SOURCE_FINDINGS_AND_CONFLICTS.md:898), [PIN025-01](SOURCE_FINDINGS_AND_CONFLICTS.md:899), [PIN026-01](SOURCE_FINDINGS_AND_CONFLICTS.md:900), [PIN026-02](SOURCE_FINDINGS_AND_CONFLICTS.md:901), [PIN027-01](SOURCE_FINDINGS_AND_CONFLICTS.md:902), [PIN027-02](SOURCE_FINDINGS_AND_CONFLICTS.md:903), [PIN028-01](SOURCE_FINDINGS_AND_CONFLICTS.md:904), [PIN028-02](SOURCE_FINDINGS_AND_CONFLICTS.md:905), [PIN028-03](SOURCE_FINDINGS_AND_CONFLICTS.md:906), [PIN029-01](SOURCE_FINDINGS_AND_CONFLICTS.md:907), [PIN029-02](SOURCE_FINDINGS_AND_CONFLICTS.md:908), [PIN029-03](SOURCE_FINDINGS_AND_CONFLICTS.md:909), [PIN030-01](SOURCE_FINDINGS_AND_CONFLICTS.md:910), [PIN030-02](SOURCE_FINDINGS_AND_CONFLICTS.md:911), [PIN030-03](SOURCE_FINDINGS_AND_CONFLICTS.md:912), [PIN031-01](SOURCE_FINDINGS_AND_CONFLICTS.md:913), [PIN032-01](SOURCE_FINDINGS_AND_CONFLICTS.md:914), [PIN032-02](SOURCE_FINDINGS_AND_CONFLICTS.md:915), [PIN032-03](SOURCE_FINDINGS_AND_CONFLICTS.md:916), [PIN033-01](SOURCE_FINDINGS_AND_CONFLICTS.md:917), [PIN033-02](SOURCE_FINDINGS_AND_CONFLICTS.md:918), [PIN034-01](SOURCE_FINDINGS_AND_CONFLICTS.md:919), [PIN035-01](SOURCE_FINDINGS_AND_CONFLICTS.md:920), [PIN035-02](SOURCE_FINDINGS_AND_CONFLICTS.md:921), [PIN035-03](SOURCE_FINDINGS_AND_CONFLICTS.md:922), [PIN035-04](SOURCE_FINDINGS_AND_CONFLICTS.md:923), [PIN036-01](SOURCE_FINDINGS_AND_CONFLICTS.md:925), [PIN036-02](SOURCE_FINDINGS_AND_CONFLICTS.md:926), [PIN037-01](SOURCE_FINDINGS_AND_CONFLICTS.md:927), [PIN037-02](SOURCE_FINDINGS_AND_CONFLICTS.md:928), [PIN038-01](SOURCE_FINDINGS_AND_CONFLICTS.md:930), [PIN038-02](SOURCE_FINDINGS_AND_CONFLICTS.md:931), [PIN039-01](SOURCE_FINDINGS_AND_CONFLICTS.md:933), [PIN039-02](SOURCE_FINDINGS_AND_CONFLICTS.md:934), [PIN040-01](SOURCE_FINDINGS_AND_CONFLICTS.md:935), [PIN040-02](SOURCE_FINDINGS_AND_CONFLICTS.md:936), [PIN041-01](SOURCE_FINDINGS_AND_CONFLICTS.md:938), [PIN041-02](SOURCE_FINDINGS_AND_CONFLICTS.md:939), [PIN041-03](SOURCE_FINDINGS_AND_CONFLICTS.md:940), [PIN042-01](SOURCE_FINDINGS_AND_CONFLICTS.md:942), [PIN042-02](SOURCE_FINDINGS_AND_CONFLICTS.md:943), [PIN043-01](SOURCE_FINDINGS_AND_CONFLICTS.md:944), [PIN044-01](SOURCE_FINDINGS_AND_CONFLICTS.md:945), [PIN044-02](SOURCE_FINDINGS_AND_CONFLICTS.md:946), [PIN045-01](SOURCE_FINDINGS_AND_CONFLICTS.md:948), [PIN045-02](SOURCE_FINDINGS_AND_CONFLICTS.md:949), [PIN045-03](SOURCE_FINDINGS_AND_CONFLICTS.md:950), [PIN045-04](SOURCE_FINDINGS_AND_CONFLICTS.md:951), [PIN045-05](SOURCE_FINDINGS_AND_CONFLICTS.md:952), [PIN045-06](SOURCE_FINDINGS_AND_CONFLICTS.md:953), [PIN046-01](SOURCE_FINDINGS_AND_CONFLICTS.md:955), [PIN047-01](SOURCE_FINDINGS_AND_CONFLICTS.md:956), [PIN047-02](SOURCE_FINDINGS_AND_CONFLICTS.md:957), [PIN047-03](SOURCE_FINDINGS_AND_CONFLICTS.md:958), [PIN048-01](SOURCE_FINDINGS_AND_CONFLICTS.md:960), [PIN048-02](SOURCE_FINDINGS_AND_CONFLICTS.md:961), [PIN048-03](SOURCE_FINDINGS_AND_CONFLICTS.md:962), [PIN049-01](SOURCE_FINDINGS_AND_CONFLICTS.md:964), [PIN049-02](SOURCE_FINDINGS_AND_CONFLICTS.md:965), [PIN049-03](SOURCE_FINDINGS_AND_CONFLICTS.md:966), [PIN050-01](SOURCE_FINDINGS_AND_CONFLICTS.md:968), [PIN050-02](SOURCE_FINDINGS_AND_CONFLICTS.md:969), [PIN050-03](SOURCE_FINDINGS_AND_CONFLICTS.md:970), [PIN051-01](SOURCE_FINDINGS_AND_CONFLICTS.md:971), [PIN051-02](SOURCE_FINDINGS_AND_CONFLICTS.md:972), [PIN052-01](SOURCE_FINDINGS_AND_CONFLICTS.md:974), [PIN052-02](SOURCE_FINDINGS_AND_CONFLICTS.md:975), [PIN052-03](SOURCE_FINDINGS_AND_CONFLICTS.md:976), [PIN054-01](SOURCE_FINDINGS_AND_CONFLICTS.md:978), [PIN054-02](SOURCE_FINDINGS_AND_CONFLICTS.md:979), [PIN055-01](SOURCE_FINDINGS_AND_CONFLICTS.md:980), [PIN055-02](SOURCE_FINDINGS_AND_CONFLICTS.md:981), [PIN056-01](SOURCE_FINDINGS_AND_CONFLICTS.md:983), [PIN056-02](SOURCE_FINDINGS_AND_CONFLICTS.md:984), [PIN057-01](SOURCE_FINDINGS_AND_CONFLICTS.md:985), [PIN057-02](SOURCE_FINDINGS_AND_CONFLICTS.md:986), [PIN057-03](SOURCE_FINDINGS_AND_CONFLICTS.md:987), [PIN058-01](SOURCE_FINDINGS_AND_CONFLICTS.md:989), [PIN059-01](SOURCE_FINDINGS_AND_CONFLICTS.md:990), [PIN059-02](SOURCE_FINDINGS_AND_CONFLICTS.md:991), [PIN060-01](SOURCE_FINDINGS_AND_CONFLICTS.md:993), [PIN060-02](SOURCE_FINDINGS_AND_CONFLICTS.md:994), [PIN060-03](SOURCE_FINDINGS_AND_CONFLICTS.md:995), [PIN061-01](SOURCE_FINDINGS_AND_CONFLICTS.md:997), [PIN061-02](SOURCE_FINDINGS_AND_CONFLICTS.md:998), [PIN061-03](SOURCE_FINDINGS_AND_CONFLICTS.md:999), [PIN062-01](SOURCE_FINDINGS_AND_CONFLICTS.md:1001), [PIN062-02](SOURCE_FINDINGS_AND_CONFLICTS.md:1002), [PIN062-03](SOURCE_FINDINGS_AND_CONFLICTS.md:1003), [PIN063-01](SOURCE_FINDINGS_AND_CONFLICTS.md:1005), [PIN063-02](SOURCE_FINDINGS_AND_CONFLICTS.md:1006), [PIN063-03](SOURCE_FINDINGS_AND_CONFLICTS.md:1007), [PIN064-01](SOURCE_FINDINGS_AND_CONFLICTS.md:1009), [PIN064-02](SOURCE_FINDINGS_AND_CONFLICTS.md:1010), [PIN065-01](SOURCE_FINDINGS_AND_CONFLICTS.md:1012), [PIN065-02](SOURCE_FINDINGS_AND_CONFLICTS.md:1013), [PIN065-03](SOURCE_FINDINGS_AND_CONFLICTS.md:1014), [PIN066-01](SOURCE_FINDINGS_AND_CONFLICTS.md:1016), [PIN066-02](SOURCE_FINDINGS_AND_CONFLICTS.md:1017), [PIN066-03](SOURCE_FINDINGS_AND_CONFLICTS.md:1018), [PIN066-04](SOURCE_FINDINGS_AND_CONFLICTS.md:1019), [PIN067-01](SOURCE_FINDINGS_AND_CONFLICTS.md:1021), [PIN067-02](SOURCE_FINDINGS_AND_CONFLICTS.md:1022), [PIN068-01](SOURCE_FINDINGS_AND_CONFLICTS.md:1024), [PIN068-02](SOURCE_FINDINGS_AND_CONFLICTS.md:1025), [PIN068-03](SOURCE_FINDINGS_AND_CONFLICTS.md:1026), [PIN069-01](SOURCE_FINDINGS_AND_CONFLICTS.md:1028), [PIN069-02](SOURCE_FINDINGS_AND_CONFLICTS.md:1029), [PIN069-03](SOURCE_FINDINGS_AND_CONFLICTS.md:1030), [PIN069-04](SOURCE_FINDINGS_AND_CONFLICTS.md:1031), [PIN070-01](SOURCE_FINDINGS_AND_CONFLICTS.md:1033), [PIN070-02](SOURCE_FINDINGS_AND_CONFLICTS.md:1034), [PIN071-01](SOURCE_FINDINGS_AND_CONFLICTS.md:1036), [PIN071-02](SOURCE_FINDINGS_AND_CONFLICTS.md:1037), [PIN071-03](SOURCE_FINDINGS_AND_CONFLICTS.md:1038), [PIN071-04](SOURCE_FINDINGS_AND_CONFLICTS.md:1039), [PIN071-05](SOURCE_FINDINGS_AND_CONFLICTS.md:1040), [PIN071-06](SOURCE_FINDINGS_AND_CONFLICTS.md:1041), [PIN071-07](SOURCE_FINDINGS_AND_CONFLICTS.md:1042), [PIN071-08](SOURCE_FINDINGS_AND_CONFLICTS.md:1043), [PIN072-01](SOURCE_FINDINGS_AND_CONFLICTS.md:1045), [PIN072-02](SOURCE_FINDINGS_AND_CONFLICTS.md:1046), [PIN073-01](SOURCE_FINDINGS_AND_CONFLICTS.md:1048), [PIN073-02](SOURCE_FINDINGS_AND_CONFLICTS.md:1049), [PIN074-01](SOURCE_FINDINGS_AND_CONFLICTS.md:1051), [PIN074-02](SOURCE_FINDINGS_AND_CONFLICTS.md:1052), [PIN075-01](SOURCE_FINDINGS_AND_CONFLICTS.md:1054), [PIN075-02](SOURCE_FINDINGS_AND_CONFLICTS.md:1055), [PIN076-01](SOURCE_FINDINGS_AND_CONFLICTS.md:1057), [PIN076-02](SOURCE_FINDINGS_AND_CONFLICTS.md:1058), [PIN077-01](SOURCE_FINDINGS_AND_CONFLICTS.md:1060), [PIN077-02](SOURCE_FINDINGS_AND_CONFLICTS.md:1061), [PIN078-01](SOURCE_FINDINGS_AND_CONFLICTS.md:1063), [PIN078-02](SOURCE_FINDINGS_AND_CONFLICTS.md:1064), [PIN079-01](SOURCE_FINDINGS_AND_CONFLICTS.md:1066), [PIN079-02](SOURCE_FINDINGS_AND_CONFLICTS.md:1067), [PIN079-03](SOURCE_FINDINGS_AND_CONFLICTS.md:1068), [PIN079-04](SOURCE_FINDINGS_AND_CONFLICTS.md:1069), [PIN080-01](SOURCE_FINDINGS_AND_CONFLICTS.md:1071), [PIN080-02](SOURCE_FINDINGS_AND_CONFLICTS.md:1072), [PIN080-03](SOURCE_FINDINGS_AND_CONFLICTS.md:1073), [PIN081-01](SOURCE_FINDINGS_AND_CONFLICTS.md:1075), [PIN081-02](SOURCE_FINDINGS_AND_CONFLICTS.md:1076), [PIN081-03](SOURCE_FINDINGS_AND_CONFLICTS.md:1077), [PIN081-04](SOURCE_FINDINGS_AND_CONFLICTS.md:1078), [PIN082-01](SOURCE_FINDINGS_AND_CONFLICTS.md:1080), [PIN082-02](SOURCE_FINDINGS_AND_CONFLICTS.md:1081), [PIN082-03](SOURCE_FINDINGS_AND_CONFLICTS.md:1082), [PIN083-01](SOURCE_FINDINGS_AND_CONFLICTS.md:1084), [PIN083-02](SOURCE_FINDINGS_AND_CONFLICTS.md:1085).

**Conversation upgrade lineage.** [DTM-A15](SOURCE_FINDINGS_AND_CONFLICTS.md:73), [CEX-01](SOURCE_FINDINGS_AND_CONFLICTS.md:183), [CRL-15](SOURCE_FINDINGS_AND_CONFLICTS.md:231), [DRF-A10](SOURCE_FINDINGS_AND_CONFLICTS.md:451), [DRF-A22](SOURCE_FINDINGS_AND_CONFLICTS.md:463). Read the full rows and their original conversation references; [the recheck](CONVERSATION_RECHECK.md) preserves the exact unit/exception routes.

<a id="up-v01-label_coverage"></a>
#### V01.LABEL_COVERAGE — Candidate and label completeness

[Existing definition, target and P0–P7](experiments/V.md#v01-label_coverage) remain binding.

**Specific upgrade scope.** Use an event/landmark label ledger with observation coverage and multi-state outcome ownership for every initial candidate and rejected/untraded branch.

**Local comparison.** Compare simple labels with the expanded target service, checking no-touch/nonfill/censor/tie partitions and candidate-population retention.

**Additional cases.** Missing future tape; overlapping objects; unresolved boundary; never acted candidate; revised geometry.

<a id="up-v02"></a>
### UP-V02 — Chronological splits, purging and OOF dependency builder

Parent: [V02](components/RESEARCH_AND_OPERATIONS.md); [local phases](experiments/V.md#v02); [definition refinement](SYSTEM_REFINEMENT.md#sr-v02). Upgrade role: `research_method`.

**Starting idea.** Random train/test split or one chronological split.

**Existing improvement path.** Nested walk-forward folds, maturity-aware purge and OOF dependencies.

**Remaining weakness.** Handwritten fold logic may miss a learned transform or over-purge harmless historical lookbacks, reducing support.

**Further upgrade.** Compile a temporal information graph for every fitted artifact and label span. Generate OOF schedules and machine-readable exclusion proofs from that graph; compare safe maximal-use folds with a conservative reference without changing evaluation dates.

**Fair comparison.** Reference conservative folds versus compiled dependency/maturity folds; planted indirect leakage through scalers, encoders, gates and calibrators.

**Evidence.** Leakage detection, eligible training support, OOF coverage, compute reuse and unchanged outer-test ownership.

**Additional local cases to implement.** Long OI endpoint; overlapping object life; innocent past lookback; joint encoder fit on future dates; outer result reused for feature selection.

**Decision or system use.** Increase usable evidence and reduce manual leakage errors across the entire multi-stage system.

**Exact reviewed source clauses.** [DTM-A17](SOURCE_FINDINGS_AND_CONFLICTS.md:75), [JCV-A03](SOURCE_FINDINGS_AND_CONFLICTS.md:162), [DRF-A27](SOURCE_FINDINGS_AND_CONFLICTS.md:468), [RFE-01](SOURCE_FINDINGS_AND_CONFLICTS.md:602), [RFE-02](SOURCE_FINDINGS_AND_CONFLICTS.md:603), [RFE-03](SOURCE_FINDINGS_AND_CONFLICTS.md:604), [RFE-04](SOURCE_FINDINGS_AND_CONFLICTS.md:605), [RFE-05](SOURCE_FINDINGS_AND_CONFLICTS.md:606), [RFE-06](SOURCE_FINDINGS_AND_CONFLICTS.md:607), [RFE-07](SOURCE_FINDINGS_AND_CONFLICTS.md:608), [RFE-08](SOURCE_FINDINGS_AND_CONFLICTS.md:609), [RFE-09](SOURCE_FINDINGS_AND_CONFLICTS.md:610), [RFE-10](SOURCE_FINDINGS_AND_CONFLICTS.md:611), [RFE-11](SOURCE_FINDINGS_AND_CONFLICTS.md:612), [RFE-12](SOURCE_FINDINGS_AND_CONFLICTS.md:613), [RFE-13](SOURCE_FINDINGS_AND_CONFLICTS.md:614), [RFE-14](SOURCE_FINDINGS_AND_CONFLICTS.md:615), [OFM-09](SOURCE_FINDINGS_AND_CONFLICTS.md:631).

**Conversation upgrade lineage.** [DTM-A17](SOURCE_FINDINGS_AND_CONFLICTS.md:75). Read the full rows and their original conversation references; [the recheck](CONVERSATION_RECHECK.md) preserves the exact unit/exception routes.

<a id="up-v02-lineage"></a>
#### V02.LINEAGE — OOF graph and legal overlaps

[Existing definition, target and P0–P7](experiments/V.md#v02-lineage) remain binding.

**Specific upgrade scope.** Compile the full chronological fit graph including generators, transforms, residual baselines, calibration, gates and auxiliary heads.

**Local comparison.** Compare declared folds with executable lineage queries and negative controls for each learned edge; overlapping intervals use exact maturity/dependence rules.

**Additional cases.** OOF predictor with in-sample scaler; residual model trained on outer labels; shared calendar day; late report.

<a id="up-v03"></a>
### UP-V03 — Hypothesis, search-budget and multiple-testing registry

Parent: [V03](components/RESEARCH_AND_OPERATIONS.md); [local phases](experiments/V.md#v03); [definition refinement](SYSTEM_REFINEMENT.md#sr-v03). Upgrade role: `research_method`.

**Starting idea.** Try many indicators and report the winner.

**Existing improvement path.** Trial registry, nested selection, useful-effect thresholds and search budgets.

**Remaining weakness.** A flat list of trials does not express the original idea's successive upgrades or the cost of abandoning weak branches.

**Further upgrade.** Use an experiment-family tree: original construction, faithful/corrected version, representation upgrade, model upgrade and integration trial. Preregister staged screening and allowed interactions; track all attempts, code/data changes and negative outcomes under the same family budget.

**Fair comparison.** Flat equal-budget sweeps versus staged family screening on planted/null and simulated known-effect problems, then actual research accounting.

**Evidence.** False discovery/selection behavior under declared assumptions, useful discoveries per compute, unexamined scope and decision reproducibility.

**Additional local cases to implement.** Renamed failed trial; adjacent-window search; optional branch rejection; multiple correlated metrics; an untested family silently disappears.

**Decision or system use.** Prioritize the whole program without equating complexity, trial count or a selected score with progress.

**Exact reviewed source clauses.** [JTR-18](SOURCE_FINDINGS_AND_CONFLICTS.md:35), [JTR-19](SOURCE_FINDINGS_AND_CONFLICTS.md:36), [DTM-A17](SOURCE_FINDINGS_AND_CONFLICTS.md:75), [JXA-07](SOURCE_FINDINGS_AND_CONFLICTS.md:106), [JXA-25](SOURCE_FINDINGS_AND_CONFLICTS.md:124), [JXA-26](SOURCE_FINDINGS_AND_CONFLICTS.md:125), [JFN-12](SOURCE_FINDINGS_AND_CONFLICTS.md:146), [JCV-U05](SOURCE_FINDINGS_AND_CONFLICTS.md:158), [JCV-A04](SOURCE_FINDINGS_AND_CONFLICTS.md:163), [JCV-A10](SOURCE_FINDINGS_AND_CONFLICTS.md:169), [CEX-02](SOURCE_FINDINGS_AND_CONFLICTS.md:184), [CEX-15](SOURCE_FINDINGS_AND_CONFLICTS.md:197), [CEX-27](SOURCE_FINDINGS_AND_CONFLICTS.md:209), [CRL-04](SOURCE_FINDINGS_AND_CONFLICTS.md:220), [CRL-08](SOURCE_FINDINGS_AND_CONFLICTS.md:224), [CRL-20](SOURCE_FINDINGS_AND_CONFLICTS.md:236), [CD1-01](SOURCE_FINDINGS_AND_CONFLICTS.md:394), [CD1-02](SOURCE_FINDINGS_AND_CONFLICTS.md:395), [CD1-03](SOURCE_FINDINGS_AND_CONFLICTS.md:396), [CD1-04](SOURCE_FINDINGS_AND_CONFLICTS.md:397), [CD1-05](SOURCE_FINDINGS_AND_CONFLICTS.md:398), [CD3-05](SOURCE_FINDINGS_AND_CONFLICTS.md:408), [DEN-01](SOURCE_FINDINGS_AND_CONFLICTS.md:409), [DEN-02](SOURCE_FINDINGS_AND_CONFLICTS.md:410), [DEN-03](SOURCE_FINDINGS_AND_CONFLICTS.md:411), [DEN-04](SOURCE_FINDINGS_AND_CONFLICTS.md:412), [DEN-05](SOURCE_FINDINGS_AND_CONFLICTS.md:413), [DRF-U10](SOURCE_FINDINGS_AND_CONFLICTS.md:434), [DRF-A22](SOURCE_FINDINGS_AND_CONFLICTS.md:463), [DRF-A25](SOURCE_FINDINGS_AND_CONFLICTS.md:466), [DRF-A27](SOURCE_FINDINGS_AND_CONFLICTS.md:468), [EMO-01](SOURCE_FINDINGS_AND_CONFLICTS.md:481), [EMO-02](SOURCE_FINDINGS_AND_CONFLICTS.md:482), [EMO-03](SOURCE_FINDINGS_AND_CONFLICTS.md:483), [EMO-04](SOURCE_FINDINGS_AND_CONFLICTS.md:484), [MAV-10](SOURCE_FINDINGS_AND_CONFLICTS.md:514), [RFE-14](SOURCE_FINDINGS_AND_CONFLICTS.md:615), [OFM-09](SOURCE_FINDINGS_AND_CONFLICTS.md:631), [AUT-01](SOURCE_FINDINGS_AND_CONFLICTS.md:767), [AUT-02](SOURCE_FINDINGS_AND_CONFLICTS.md:768), [AUT-03](SOURCE_FINDINGS_AND_CONFLICTS.md:769), [AUT-04](SOURCE_FINDINGS_AND_CONFLICTS.md:770), [AUT-05](SOURCE_FINDINGS_AND_CONFLICTS.md:771), [AUT-06](SOURCE_FINDINGS_AND_CONFLICTS.md:772), [AUT-07](SOURCE_FINDINGS_AND_CONFLICTS.md:773), [AUT-08](SOURCE_FINDINGS_AND_CONFLICTS.md:774), [AUT-09](SOURCE_FINDINGS_AND_CONFLICTS.md:775), [AUT-10](SOURCE_FINDINGS_AND_CONFLICTS.md:776), [AUT-11](SOURCE_FINDINGS_AND_CONFLICTS.md:777), [PIN001-01](SOURCE_FINDINGS_AND_CONFLICTS.md:812), [PIN001-02](SOURCE_FINDINGS_AND_CONFLICTS.md:813), [PIN001-03](SOURCE_FINDINGS_AND_CONFLICTS.md:814), [PIN001-04](SOURCE_FINDINGS_AND_CONFLICTS.md:815), [PIN002-01](SOURCE_FINDINGS_AND_CONFLICTS.md:816), [PIN002-02](SOURCE_FINDINGS_AND_CONFLICTS.md:817), [PIN002-03](SOURCE_FINDINGS_AND_CONFLICTS.md:818), [PIN008-01](SOURCE_FINDINGS_AND_CONFLICTS.md:824), [PIN009-01](SOURCE_FINDINGS_AND_CONFLICTS.md:825), [PIN009-02](SOURCE_FINDINGS_AND_CONFLICTS.md:826), [PIN053-01](SOURCE_FINDINGS_AND_CONFLICTS.md:827), [PIN005-01](SOURCE_FINDINGS_AND_CONFLICTS.md:828), [PIN005-02](SOURCE_FINDINGS_AND_CONFLICTS.md:829), [PIN005-03](SOURCE_FINDINGS_AND_CONFLICTS.md:830), [PIN005-04](SOURCE_FINDINGS_AND_CONFLICTS.md:831), [PIN005-05](SOURCE_FINDINGS_AND_CONFLICTS.md:832), [PIN006-01](SOURCE_FINDINGS_AND_CONFLICTS.md:833), [PIN006-02](SOURCE_FINDINGS_AND_CONFLICTS.md:834), [PIN006-03](SOURCE_FINDINGS_AND_CONFLICTS.md:835), [PIN007-01](SOURCE_FINDINGS_AND_CONFLICTS.md:836), [PIN007-02](SOURCE_FINDINGS_AND_CONFLICTS.md:837), [PIN007-03](SOURCE_FINDINGS_AND_CONFLICTS.md:838), [PIN007-04](SOURCE_FINDINGS_AND_CONFLICTS.md:839), [PIN007-05](SOURCE_FINDINGS_AND_CONFLICTS.md:840), [PIN011-01](SOURCE_FINDINGS_AND_CONFLICTS.md:845), [PIN011-02](SOURCE_FINDINGS_AND_CONFLICTS.md:846), [PIN011-03](SOURCE_FINDINGS_AND_CONFLICTS.md:847), [PIN011-04](SOURCE_FINDINGS_AND_CONFLICTS.md:848), [PIN011-05](SOURCE_FINDINGS_AND_CONFLICTS.md:849), [PIN011-06](SOURCE_FINDINGS_AND_CONFLICTS.md:850), [PIN011-07](SOURCE_FINDINGS_AND_CONFLICTS.md:851), [PIN012-01](SOURCE_FINDINGS_AND_CONFLICTS.md:852), [PIN012-02](SOURCE_FINDINGS_AND_CONFLICTS.md:853), [PIN012-03](SOURCE_FINDINGS_AND_CONFLICTS.md:854), [PIN012-04](SOURCE_FINDINGS_AND_CONFLICTS.md:855), [PIN012-05](SOURCE_FINDINGS_AND_CONFLICTS.md:856), [PIN013-01](SOURCE_FINDINGS_AND_CONFLICTS.md:857), [PIN013-02](SOURCE_FINDINGS_AND_CONFLICTS.md:858), [PIN013-03](SOURCE_FINDINGS_AND_CONFLICTS.md:859), [PIN013-04](SOURCE_FINDINGS_AND_CONFLICTS.md:860), [PIN013-05](SOURCE_FINDINGS_AND_CONFLICTS.md:861), [PIN013-06](SOURCE_FINDINGS_AND_CONFLICTS.md:862), [PIN014-01](SOURCE_FINDINGS_AND_CONFLICTS.md:863), [PIN014-02](SOURCE_FINDINGS_AND_CONFLICTS.md:864), [PIN015-01](SOURCE_FINDINGS_AND_CONFLICTS.md:865), [PIN015-02](SOURCE_FINDINGS_AND_CONFLICTS.md:866), [PIN015-03](SOURCE_FINDINGS_AND_CONFLICTS.md:867), [PIN016-01](SOURCE_FINDINGS_AND_CONFLICTS.md:868), [PIN016-02](SOURCE_FINDINGS_AND_CONFLICTS.md:869), [PIN016-03](SOURCE_FINDINGS_AND_CONFLICTS.md:870), [PIN016-04](SOURCE_FINDINGS_AND_CONFLICTS.md:871), [PIN017-01](SOURCE_FINDINGS_AND_CONFLICTS.md:872), [PIN017-02](SOURCE_FINDINGS_AND_CONFLICTS.md:873), [PIN017-03](SOURCE_FINDINGS_AND_CONFLICTS.md:874), [PIN017-04](SOURCE_FINDINGS_AND_CONFLICTS.md:875), [PIN018-01](SOURCE_FINDINGS_AND_CONFLICTS.md:876), [PIN018-02](SOURCE_FINDINGS_AND_CONFLICTS.md:877), [PIN024-01](SOURCE_FINDINGS_AND_CONFLICTS.md:878), [PIN024-02](SOURCE_FINDINGS_AND_CONFLICTS.md:879), [PIN019-01](SOURCE_FINDINGS_AND_CONFLICTS.md:887), [PIN019-02](SOURCE_FINDINGS_AND_CONFLICTS.md:888), [PIN019-03](SOURCE_FINDINGS_AND_CONFLICTS.md:889), [PIN020-01](SOURCE_FINDINGS_AND_CONFLICTS.md:890), [PIN020-02](SOURCE_FINDINGS_AND_CONFLICTS.md:891), [PIN021-01](SOURCE_FINDINGS_AND_CONFLICTS.md:892), [PIN021-02](SOURCE_FINDINGS_AND_CONFLICTS.md:893), [PIN025-01](SOURCE_FINDINGS_AND_CONFLICTS.md:899), [PIN026-01](SOURCE_FINDINGS_AND_CONFLICTS.md:900), [PIN026-02](SOURCE_FINDINGS_AND_CONFLICTS.md:901), [PIN027-01](SOURCE_FINDINGS_AND_CONFLICTS.md:902), [PIN027-02](SOURCE_FINDINGS_AND_CONFLICTS.md:903), [PIN028-01](SOURCE_FINDINGS_AND_CONFLICTS.md:904), [PIN028-02](SOURCE_FINDINGS_AND_CONFLICTS.md:905), [PIN028-03](SOURCE_FINDINGS_AND_CONFLICTS.md:906), [PIN029-01](SOURCE_FINDINGS_AND_CONFLICTS.md:907), [PIN029-02](SOURCE_FINDINGS_AND_CONFLICTS.md:908), [PIN029-03](SOURCE_FINDINGS_AND_CONFLICTS.md:909), [PIN030-01](SOURCE_FINDINGS_AND_CONFLICTS.md:910), [PIN030-02](SOURCE_FINDINGS_AND_CONFLICTS.md:911), [PIN030-03](SOURCE_FINDINGS_AND_CONFLICTS.md:912), [PIN031-01](SOURCE_FINDINGS_AND_CONFLICTS.md:913), [PIN033-01](SOURCE_FINDINGS_AND_CONFLICTS.md:917), [PIN033-02](SOURCE_FINDINGS_AND_CONFLICTS.md:918), [PIN034-01](SOURCE_FINDINGS_AND_CONFLICTS.md:919), [PIN036-01](SOURCE_FINDINGS_AND_CONFLICTS.md:925), [PIN036-02](SOURCE_FINDINGS_AND_CONFLICTS.md:926), [PIN037-01](SOURCE_FINDINGS_AND_CONFLICTS.md:927), [PIN037-02](SOURCE_FINDINGS_AND_CONFLICTS.md:928), [PIN039-01](SOURCE_FINDINGS_AND_CONFLICTS.md:933), [PIN039-02](SOURCE_FINDINGS_AND_CONFLICTS.md:934), [PIN040-01](SOURCE_FINDINGS_AND_CONFLICTS.md:935), [PIN040-02](SOURCE_FINDINGS_AND_CONFLICTS.md:936), [PIN041-01](SOURCE_FINDINGS_AND_CONFLICTS.md:938), [PIN041-02](SOURCE_FINDINGS_AND_CONFLICTS.md:939), [PIN041-03](SOURCE_FINDINGS_AND_CONFLICTS.md:940), [PIN042-01](SOURCE_FINDINGS_AND_CONFLICTS.md:942), [PIN042-02](SOURCE_FINDINGS_AND_CONFLICTS.md:943), [PIN043-01](SOURCE_FINDINGS_AND_CONFLICTS.md:944), [PIN044-01](SOURCE_FINDINGS_AND_CONFLICTS.md:945), [PIN044-02](SOURCE_FINDINGS_AND_CONFLICTS.md:946), [PIN045-01](SOURCE_FINDINGS_AND_CONFLICTS.md:948), [PIN045-02](SOURCE_FINDINGS_AND_CONFLICTS.md:949), [PIN045-03](SOURCE_FINDINGS_AND_CONFLICTS.md:950), [PIN045-04](SOURCE_FINDINGS_AND_CONFLICTS.md:951), [PIN045-05](SOURCE_FINDINGS_AND_CONFLICTS.md:952), [PIN045-06](SOURCE_FINDINGS_AND_CONFLICTS.md:953), [PIN046-01](SOURCE_FINDINGS_AND_CONFLICTS.md:955), [PIN047-01](SOURCE_FINDINGS_AND_CONFLICTS.md:956), [PIN047-02](SOURCE_FINDINGS_AND_CONFLICTS.md:957), [PIN047-03](SOURCE_FINDINGS_AND_CONFLICTS.md:958), [PIN048-01](SOURCE_FINDINGS_AND_CONFLICTS.md:960), [PIN048-02](SOURCE_FINDINGS_AND_CONFLICTS.md:961), [PIN048-03](SOURCE_FINDINGS_AND_CONFLICTS.md:962), [PIN049-01](SOURCE_FINDINGS_AND_CONFLICTS.md:964), [PIN049-02](SOURCE_FINDINGS_AND_CONFLICTS.md:965), [PIN049-03](SOURCE_FINDINGS_AND_CONFLICTS.md:966), [PIN050-01](SOURCE_FINDINGS_AND_CONFLICTS.md:968), [PIN050-02](SOURCE_FINDINGS_AND_CONFLICTS.md:969), [PIN050-03](SOURCE_FINDINGS_AND_CONFLICTS.md:970), [PIN052-01](SOURCE_FINDINGS_AND_CONFLICTS.md:974), [PIN052-02](SOURCE_FINDINGS_AND_CONFLICTS.md:975), [PIN052-03](SOURCE_FINDINGS_AND_CONFLICTS.md:976), [PIN054-01](SOURCE_FINDINGS_AND_CONFLICTS.md:978), [PIN054-02](SOURCE_FINDINGS_AND_CONFLICTS.md:979), [PIN055-01](SOURCE_FINDINGS_AND_CONFLICTS.md:980), [PIN055-02](SOURCE_FINDINGS_AND_CONFLICTS.md:981), [PIN056-01](SOURCE_FINDINGS_AND_CONFLICTS.md:983), [PIN056-02](SOURCE_FINDINGS_AND_CONFLICTS.md:984), [PIN057-01](SOURCE_FINDINGS_AND_CONFLICTS.md:985), [PIN057-02](SOURCE_FINDINGS_AND_CONFLICTS.md:986), [PIN057-03](SOURCE_FINDINGS_AND_CONFLICTS.md:987), [PIN058-01](SOURCE_FINDINGS_AND_CONFLICTS.md:989), [PIN059-01](SOURCE_FINDINGS_AND_CONFLICTS.md:990), [PIN059-02](SOURCE_FINDINGS_AND_CONFLICTS.md:991), [PIN060-01](SOURCE_FINDINGS_AND_CONFLICTS.md:993), [PIN060-02](SOURCE_FINDINGS_AND_CONFLICTS.md:994), [PIN060-03](SOURCE_FINDINGS_AND_CONFLICTS.md:995), [PIN061-01](SOURCE_FINDINGS_AND_CONFLICTS.md:997), [PIN061-02](SOURCE_FINDINGS_AND_CONFLICTS.md:998), [PIN061-03](SOURCE_FINDINGS_AND_CONFLICTS.md:999), [PIN062-01](SOURCE_FINDINGS_AND_CONFLICTS.md:1001), [PIN062-02](SOURCE_FINDINGS_AND_CONFLICTS.md:1002), [PIN062-03](SOURCE_FINDINGS_AND_CONFLICTS.md:1003), [PIN063-01](SOURCE_FINDINGS_AND_CONFLICTS.md:1005), [PIN063-02](SOURCE_FINDINGS_AND_CONFLICTS.md:1006), [PIN063-03](SOURCE_FINDINGS_AND_CONFLICTS.md:1007), [PIN064-01](SOURCE_FINDINGS_AND_CONFLICTS.md:1009), [PIN064-02](SOURCE_FINDINGS_AND_CONFLICTS.md:1010), [PIN065-01](SOURCE_FINDINGS_AND_CONFLICTS.md:1012), [PIN065-02](SOURCE_FINDINGS_AND_CONFLICTS.md:1013), [PIN065-03](SOURCE_FINDINGS_AND_CONFLICTS.md:1014), [PIN067-01](SOURCE_FINDINGS_AND_CONFLICTS.md:1021), [PIN067-02](SOURCE_FINDINGS_AND_CONFLICTS.md:1022), [PIN068-01](SOURCE_FINDINGS_AND_CONFLICTS.md:1024), [PIN068-02](SOURCE_FINDINGS_AND_CONFLICTS.md:1025), [PIN068-03](SOURCE_FINDINGS_AND_CONFLICTS.md:1026), [PIN069-01](SOURCE_FINDINGS_AND_CONFLICTS.md:1028), [PIN069-02](SOURCE_FINDINGS_AND_CONFLICTS.md:1029), [PIN069-03](SOURCE_FINDINGS_AND_CONFLICTS.md:1030), [PIN069-04](SOURCE_FINDINGS_AND_CONFLICTS.md:1031), [PIN070-01](SOURCE_FINDINGS_AND_CONFLICTS.md:1033), [PIN070-02](SOURCE_FINDINGS_AND_CONFLICTS.md:1034), [PIN072-01](SOURCE_FINDINGS_AND_CONFLICTS.md:1045), [PIN072-02](SOURCE_FINDINGS_AND_CONFLICTS.md:1046), [PIN073-01](SOURCE_FINDINGS_AND_CONFLICTS.md:1048), [PIN073-02](SOURCE_FINDINGS_AND_CONFLICTS.md:1049), [PIN074-01](SOURCE_FINDINGS_AND_CONFLICTS.md:1051), [PIN074-02](SOURCE_FINDINGS_AND_CONFLICTS.md:1052), [PIN075-01](SOURCE_FINDINGS_AND_CONFLICTS.md:1054), [PIN075-02](SOURCE_FINDINGS_AND_CONFLICTS.md:1055), [PIN076-01](SOURCE_FINDINGS_AND_CONFLICTS.md:1057), [PIN076-02](SOURCE_FINDINGS_AND_CONFLICTS.md:1058), [PIN078-01](SOURCE_FINDINGS_AND_CONFLICTS.md:1063), [PIN078-02](SOURCE_FINDINGS_AND_CONFLICTS.md:1064), [PIN079-01](SOURCE_FINDINGS_AND_CONFLICTS.md:1066), [PIN079-02](SOURCE_FINDINGS_AND_CONFLICTS.md:1067), [PIN079-03](SOURCE_FINDINGS_AND_CONFLICTS.md:1068), [PIN079-04](SOURCE_FINDINGS_AND_CONFLICTS.md:1069), [PIN080-01](SOURCE_FINDINGS_AND_CONFLICTS.md:1071), [PIN080-02](SOURCE_FINDINGS_AND_CONFLICTS.md:1072), [PIN080-03](SOURCE_FINDINGS_AND_CONFLICTS.md:1073), [PIN081-01](SOURCE_FINDINGS_AND_CONFLICTS.md:1075), [PIN081-02](SOURCE_FINDINGS_AND_CONFLICTS.md:1076), [PIN081-03](SOURCE_FINDINGS_AND_CONFLICTS.md:1077), [PIN081-04](SOURCE_FINDINGS_AND_CONFLICTS.md:1078), [PIN082-01](SOURCE_FINDINGS_AND_CONFLICTS.md:1080), [PIN082-02](SOURCE_FINDINGS_AND_CONFLICTS.md:1081), [PIN082-03](SOURCE_FINDINGS_AND_CONFLICTS.md:1082), [PIN083-01](SOURCE_FINDINGS_AND_CONFLICTS.md:1084), [PIN083-02](SOURCE_FINDINGS_AND_CONFLICTS.md:1085).

**Conversation upgrade lineage.** [DTM-A17](SOURCE_FINDINGS_AND_CONFLICTS.md:75), [DTM-A18](SOURCE_FINDINGS_AND_CONFLICTS.md:76), [JCV-A04](SOURCE_FINDINGS_AND_CONFLICTS.md:163), [JCV-A10](SOURCE_FINDINGS_AND_CONFLICTS.md:169), [CEX-27](SOURCE_FINDINGS_AND_CONFLICTS.md:209), [DRF-U10](SOURCE_FINDINGS_AND_CONFLICTS.md:434), [DRF-U12](SOURCE_FINDINGS_AND_CONFLICTS.md:436), [DRF-A25](SOURCE_FINDINGS_AND_CONFLICTS.md:466), [DRF-A29](SOURCE_FINDINGS_AND_CONFLICTS.md:470). Read the full rows and their original conversation references; [the recheck](CONVERSATION_RECHECK.md) preserves the exact unit/exception routes.

<a id="up-v03-search"></a>
#### V03.SEARCH — Honest model/definition selection

[Existing definition, target and P0–P7](experiments/V.md#v03-search) remain binding.

**Specific upgrade scope.** Separate a registered broad family pilot from bounded expansion and preserve all attempted definitions, hypotheses and stopping decisions.

**Local comparison.** Compare information versus representation/capacity under matched budgets, retaining negative/inconclusive branches and held-out integrity.

**Additional cases.** Successful window chosen from many; abandoned failed model omitted; expensive family crowds out others.

<a id="up-v04"></a>
### UP-V04 — Evidence gates and economic feasibility decision

Parent: [V04](components/RESEARCH_AND_OPERATIONS.md); [local phases](experiments/V.md#v04); [definition refinement](SYSTEM_REFINEMENT.md#sr-v04). Upgrade role: `research_method`.

**Starting idea.** Accept a high hit rate, attractive Sharpe or one profitable period.

**Existing improvement path.** Predictive, economic, account and frozen-future evidence gates with inconclusive/no-go outcomes.

**Remaining weakness.** A binary pass/fail hides whether failure comes from data, signal quality, decision use, costs, constraints or insufficient precision.

**Further upgrade.** Produce an evidence frontier by component and complete policy: predictive increment, calibration/support, usable opportunity rate, net after execution, account survival, resource cost and uncertainty. Attribute the objective gap with paired reruns and preregister useful tradeoffs rather than maximizing one metric.

**Fair comparison.** Simple/full policies and each upgrade stage on the same eligible dates and budget; fixed-endpoint or valid sequential future inference.

**Evidence.** Best-supported Pareto alternatives, objective gap, uncertainty, risk overshoot and remaining evidence required; no perfection claim.

**Additional local cases to implement.** Predictive gain but worse fills; fewer losses but too little opportunity; flat-day exclusion; positive point estimate with wide interval; future period incomplete.

**Decision or system use.** Make a concrete research/deployment decision and identify the next worthwhile upgrade when the current system is inadequate.

**Exact reviewed source clauses.** [JTR-18](SOURCE_FINDINGS_AND_CONFLICTS.md:35), [DTM-A08](SOURCE_FINDINGS_AND_CONFLICTS.md:66), [DTM-A17](SOURCE_FINDINGS_AND_CONFLICTS.md:75), [JXA-11](SOURCE_FINDINGS_AND_CONFLICTS.md:110), [JCV-U05](SOURCE_FINDINGS_AND_CONFLICTS.md:158), [JCV-A09](SOURCE_FINDINGS_AND_CONFLICTS.md:168), [JCV-A10](SOURCE_FINDINGS_AND_CONFLICTS.md:169), [CRL-03](SOURCE_FINDINGS_AND_CONFLICTS.md:219), [CD2-01](SOURCE_FINDINGS_AND_CONFLICTS.md:399), [CD2-02](SOURCE_FINDINGS_AND_CONFLICTS.md:400), [CD2-03](SOURCE_FINDINGS_AND_CONFLICTS.md:401), [CD2-04](SOURCE_FINDINGS_AND_CONFLICTS.md:402), [CD2-05](SOURCE_FINDINGS_AND_CONFLICTS.md:403), [DEN-05](SOURCE_FINDINGS_AND_CONFLICTS.md:413), [DRF-U12](SOURCE_FINDINGS_AND_CONFLICTS.md:436), [DRF-A27](SOURCE_FINDINGS_AND_CONFLICTS.md:468), [RFE-11](SOURCE_FINDINGS_AND_CONFLICTS.md:612), [RFE-12](SOURCE_FINDINGS_AND_CONFLICTS.md:613), [RFE-13](SOURCE_FINDINGS_AND_CONFLICTS.md:614), [RFE-14](SOURCE_FINDINGS_AND_CONFLICTS.md:615), [OFM-08](SOURCE_FINDINGS_AND_CONFLICTS.md:630), [K10-01](SOURCE_FINDINGS_AND_CONFLICTS.md:639), [K10-06](SOURCE_FINDINGS_AND_CONFLICTS.md:644), [K18-01](SOURCE_FINDINGS_AND_CONFLICTS.md:652), [K18-08](SOURCE_FINDINGS_AND_CONFLICTS.md:659), [F23-01](SOURCE_FINDINGS_AND_CONFLICTS.md:667), [F23-07](SOURCE_FINDINGS_AND_CONFLICTS.md:673), [NYA-06](SOURCE_FINDINGS_AND_CONFLICTS.md:714), [SRE-06](SOURCE_FINDINGS_AND_CONFLICTS.md:727), [OBT-10](SOURCE_FINDINGS_AND_CONFLICTS.md:759).

**Conversation upgrade lineage.** [DTM-A08](SOURCE_FINDINGS_AND_CONFLICTS.md:66), [DTM-A17](SOURCE_FINDINGS_AND_CONFLICTS.md:75), [JCV-A03](SOURCE_FINDINGS_AND_CONFLICTS.md:162), [JCV-A09](SOURCE_FINDINGS_AND_CONFLICTS.md:168), [DRF-U12](SOURCE_FINDINGS_AND_CONFLICTS.md:436), [DRF-A28](SOURCE_FINDINGS_AND_CONFLICTS.md:469), [DRF-A29](SOURCE_FINDINGS_AND_CONFLICTS.md:470). Read the full rows and their original conversation references; [the recheck](CONVERSATION_RECHECK.md) preserves the exact unit/exception routes.

<a id="up-v04-power"></a>
#### V04.POWER — Useful-effect and sample-support decisions

[Existing definition, target and P0–P7](experiments/V.md#v04-power) remain binding.

**Specific upgrade scope.** Attach useful-effect, dependence-aware uncertainty and learning-curve support decisions to each local target and complete policy.

**Local comparison.** Compare fixed-endpoint and valid preregistered sequential protocols by their own assumptions; insufficient precision is inconclusive.

**Additional cases.** Rare event dates; optional ordinary-CI extension; correlated trades; tiny statistically significant gain.

<a id="up-v05"></a>
### UP-V05 — Drift, calibration monitoring and controlled adaptation

Parent: [V05](components/RESEARCH_AND_OPERATIONS.md); [local phases](experiments/V.md#v05); [definition refinement](SYSTEM_REFINEMENT.md#sr-v05). Upgrade role: `research_method`.

**Starting idea.** Retrain whenever an indicator or P&L changes.

**Existing improvement path.** Matured-label drift, calibration monitoring and controlled adaptation.

**Remaining weakness.** Hundreds of correlated alarms can cause excessive refits or obscure a shared upstream failure.

**Further upgrade.** Use hierarchical monitoring from source quality to feature state, target calibration and policy outcomes. Aggregate related alerts by lineage/episode, distinguish source faults from market shifts, and compare residual CUSUM/run-length detectors with simple scheduled review under a registered false-alarm/delay budget.

**Fair comparison.** No adaptation, fixed reviews and registered adaptive policies on planted drift, stable nulls and chronological replay.

**Evidence.** False-alert clusters, detection delay, unnecessary refits, recovery time and full adaptive-policy net/risk.

**Additional local cases to implement.** One source fault triggers many experts; rare regime; delayed labels; abrupt versus gradual drift; market shift during missing data.

**Decision or system use.** Spend adaptation budget where new evidence warrants it; hard source/risk failures retain independent immediate handling.

**Exact reviewed source clauses.** [CEX-15](SOURCE_FINDINGS_AND_CONFLICTS.md:197), [CRL-09](SOURCE_FINDINGS_AND_CONFLICTS.md:225), [CRL-17](SOURCE_FINDINGS_AND_CONFLICTS.md:233), [DRF-A14](SOURCE_FINDINGS_AND_CONFLICTS.md:455), [EMO-01](SOURCE_FINDINGS_AND_CONFLICTS.md:481), [EMO-02](SOURCE_FINDINGS_AND_CONFLICTS.md:482), [EMO-03](SOURCE_FINDINGS_AND_CONFLICTS.md:483), [EMO-04](SOURCE_FINDINGS_AND_CONFLICTS.md:484).

**Conversation upgrade lineage.** [CEX-15](SOURCE_FINDINGS_AND_CONFLICTS.md:197), [CRL-09](SOURCE_FINDINGS_AND_CONFLICTS.md:225). Read the full rows and their original conversation references; [the recheck](CONVERSATION_RECHECK.md) preserves the exact unit/exception routes.

<a id="up-v05-drift"></a>
#### V05.DRIFT — Component-specific drift and fallback

[Existing definition, target and P0–P7](experiments/V.md#v05-drift) remain binding.

**Specific upgrade scope.** Organize source/state/forecast/calibration/policy alerts hierarchically and evaluate layer-specific adaptation policies.

**Local comparison.** Compare fixed reviews and registered detectors at matched false-alert/resource budgets with matured labels.

**Additional cases.** Shared source fault triggers many experts; slow labels; gradual versus abrupt drift; chance performance dip.

<a id="up-v06"></a>
### UP-V06 — Historical/live parity, restart and deterministic replay

Parent: [V06](components/RESEARCH_AND_OPERATIONS.md); [local phases](experiments/V.md#v06); [definition refinement](SYSTEM_REFINEMENT.md#sr-v06). Upgrade role: `engineering`.

**Starting idea.** Compare a few historical and live indicator values.

**Existing improvement path.** Prefix/restart parity and historical/live calculation contracts.

**Remaining weakness.** A final-table difference can be difficult to localize across many asynchronous producers.

**Further upgrade.** Add deterministic trace comparison with version-vector checkpoints, first-divergence bisection and dependency-local replay. Check numeric tolerance at outputs and decision sensitivity near thresholds; preserve separate bitwise-reference and permitted numeric-variation reports.

**Fair comparison.** Whole-run compare versus localized trace diagnostics after deliberately planted timing, numeric and state faults.

**Evidence.** Time to causal localization, reproducibility, false parity passes and action changes within numerical tolerance.

**Additional local cases to implement.** Floating sum changes rank near tie; expired forecast reused; checkpoint omits unfinished bar; timer/order race; same values with different lineage.

**Decision or system use.** Make broad optimizations and deployments diagnosable without weakening semantic or action-level parity.

**Exact reviewed source clauses.** [DTM-A07](SOURCE_FINDINGS_AND_CONFLICTS.md:65), [DTM-A17](SOURCE_FINDINGS_AND_CONFLICTS.md:75), [CEX-24](SOURCE_FINDINGS_AND_CONFLICTS.md:206), [CEX-26](SOURCE_FINDINGS_AND_CONFLICTS.md:208), [IMG-01](SOURCE_FINDINGS_AND_CONFLICTS.md:248), [INV-06](SOURCE_FINDINGS_AND_CONFLICTS.md:267), [INV-09](SOURCE_FINDINGS_AND_CONFLICTS.md:270), [INV-11](SOURCE_FINDINGS_AND_CONFLICTS.md:272), [VX4-07](SOURCE_FINDINGS_AND_CONFLICTS.md:330), [VW10-05](SOURCE_FINDINGS_AND_CONFLICTS.md:384), [DEN-04](SOURCE_FINDINGS_AND_CONFLICTS.md:412), [DRF-A26](SOURCE_FINDINGS_AND_CONFLICTS.md:467), [DRF-A28](SOURCE_FINDINGS_AND_CONFLICTS.md:469), [ALM-06](SOURCE_FINDINGS_AND_CONFLICTS.md:569), [OFM-01](SOURCE_FINDINGS_AND_CONFLICTS.md:623), [TBR-07](SOURCE_FINDINGS_AND_CONFLICTS.md:742), [OSF-01](SOURCE_FINDINGS_AND_CONFLICTS.md:795), [OSF-02](SOURCE_FINDINGS_AND_CONFLICTS.md:796), [OSF-03](SOURCE_FINDINGS_AND_CONFLICTS.md:797), [OSF-04](SOURCE_FINDINGS_AND_CONFLICTS.md:798), [OSF-05](SOURCE_FINDINGS_AND_CONFLICTS.md:799), [OSF-06](SOURCE_FINDINGS_AND_CONFLICTS.md:800), [OSF-07](SOURCE_FINDINGS_AND_CONFLICTS.md:801), [OSF-08](SOURCE_FINDINGS_AND_CONFLICTS.md:802), [OSF-09](SOURCE_FINDINGS_AND_CONFLICTS.md:803), [OSF-10](SOURCE_FINDINGS_AND_CONFLICTS.md:804), [PIN001-01](SOURCE_FINDINGS_AND_CONFLICTS.md:812), [PIN001-02](SOURCE_FINDINGS_AND_CONFLICTS.md:813), [PIN001-03](SOURCE_FINDINGS_AND_CONFLICTS.md:814), [PIN001-04](SOURCE_FINDINGS_AND_CONFLICTS.md:815), [PIN002-01](SOURCE_FINDINGS_AND_CONFLICTS.md:816), [PIN002-02](SOURCE_FINDINGS_AND_CONFLICTS.md:817), [PIN002-03](SOURCE_FINDINGS_AND_CONFLICTS.md:818), [PIN003-01](SOURCE_FINDINGS_AND_CONFLICTS.md:819), [PIN003-02](SOURCE_FINDINGS_AND_CONFLICTS.md:820), [PIN003-03](SOURCE_FINDINGS_AND_CONFLICTS.md:821), [PIN003-04](SOURCE_FINDINGS_AND_CONFLICTS.md:822), [PIN004-01](SOURCE_FINDINGS_AND_CONFLICTS.md:823), [PIN008-01](SOURCE_FINDINGS_AND_CONFLICTS.md:824), [PIN009-01](SOURCE_FINDINGS_AND_CONFLICTS.md:825), [PIN009-02](SOURCE_FINDINGS_AND_CONFLICTS.md:826), [PIN053-01](SOURCE_FINDINGS_AND_CONFLICTS.md:827), [PIN005-01](SOURCE_FINDINGS_AND_CONFLICTS.md:828), [PIN005-02](SOURCE_FINDINGS_AND_CONFLICTS.md:829), [PIN005-03](SOURCE_FINDINGS_AND_CONFLICTS.md:830), [PIN005-04](SOURCE_FINDINGS_AND_CONFLICTS.md:831), [PIN005-05](SOURCE_FINDINGS_AND_CONFLICTS.md:832), [PIN006-01](SOURCE_FINDINGS_AND_CONFLICTS.md:833), [PIN006-02](SOURCE_FINDINGS_AND_CONFLICTS.md:834), [PIN006-03](SOURCE_FINDINGS_AND_CONFLICTS.md:835), [PIN007-01](SOURCE_FINDINGS_AND_CONFLICTS.md:836), [PIN007-02](SOURCE_FINDINGS_AND_CONFLICTS.md:837), [PIN007-03](SOURCE_FINDINGS_AND_CONFLICTS.md:838), [PIN007-04](SOURCE_FINDINGS_AND_CONFLICTS.md:839), [PIN007-05](SOURCE_FINDINGS_AND_CONFLICTS.md:840), [PIN010-01](SOURCE_FINDINGS_AND_CONFLICTS.md:841), [PIN010-02](SOURCE_FINDINGS_AND_CONFLICTS.md:842), [PIN010-03](SOURCE_FINDINGS_AND_CONFLICTS.md:843), [PIN010-04](SOURCE_FINDINGS_AND_CONFLICTS.md:844), [PIN011-01](SOURCE_FINDINGS_AND_CONFLICTS.md:845), [PIN011-02](SOURCE_FINDINGS_AND_CONFLICTS.md:846), [PIN011-03](SOURCE_FINDINGS_AND_CONFLICTS.md:847), [PIN011-04](SOURCE_FINDINGS_AND_CONFLICTS.md:848), [PIN011-05](SOURCE_FINDINGS_AND_CONFLICTS.md:849), [PIN011-06](SOURCE_FINDINGS_AND_CONFLICTS.md:850), [PIN011-07](SOURCE_FINDINGS_AND_CONFLICTS.md:851), [PIN012-01](SOURCE_FINDINGS_AND_CONFLICTS.md:852), [PIN012-02](SOURCE_FINDINGS_AND_CONFLICTS.md:853), [PIN012-03](SOURCE_FINDINGS_AND_CONFLICTS.md:854), [PIN012-04](SOURCE_FINDINGS_AND_CONFLICTS.md:855), [PIN012-05](SOURCE_FINDINGS_AND_CONFLICTS.md:856), [PIN013-01](SOURCE_FINDINGS_AND_CONFLICTS.md:857), [PIN013-02](SOURCE_FINDINGS_AND_CONFLICTS.md:858), [PIN013-03](SOURCE_FINDINGS_AND_CONFLICTS.md:859), [PIN013-04](SOURCE_FINDINGS_AND_CONFLICTS.md:860), [PIN013-05](SOURCE_FINDINGS_AND_CONFLICTS.md:861), [PIN013-06](SOURCE_FINDINGS_AND_CONFLICTS.md:862), [PIN014-01](SOURCE_FINDINGS_AND_CONFLICTS.md:863), [PIN014-02](SOURCE_FINDINGS_AND_CONFLICTS.md:864), [PIN015-01](SOURCE_FINDINGS_AND_CONFLICTS.md:865), [PIN015-02](SOURCE_FINDINGS_AND_CONFLICTS.md:866), [PIN015-03](SOURCE_FINDINGS_AND_CONFLICTS.md:867), [PIN016-01](SOURCE_FINDINGS_AND_CONFLICTS.md:868), [PIN016-02](SOURCE_FINDINGS_AND_CONFLICTS.md:869), [PIN016-03](SOURCE_FINDINGS_AND_CONFLICTS.md:870), [PIN016-04](SOURCE_FINDINGS_AND_CONFLICTS.md:871), [PIN017-01](SOURCE_FINDINGS_AND_CONFLICTS.md:872), [PIN017-02](SOURCE_FINDINGS_AND_CONFLICTS.md:873), [PIN017-03](SOURCE_FINDINGS_AND_CONFLICTS.md:874), [PIN017-04](SOURCE_FINDINGS_AND_CONFLICTS.md:875), [PIN018-01](SOURCE_FINDINGS_AND_CONFLICTS.md:876), [PIN018-02](SOURCE_FINDINGS_AND_CONFLICTS.md:877), [PIN024-01](SOURCE_FINDINGS_AND_CONFLICTS.md:878), [PIN024-02](SOURCE_FINDINGS_AND_CONFLICTS.md:879), [PIN019-01](SOURCE_FINDINGS_AND_CONFLICTS.md:887), [PIN019-02](SOURCE_FINDINGS_AND_CONFLICTS.md:888), [PIN019-03](SOURCE_FINDINGS_AND_CONFLICTS.md:889), [PIN020-01](SOURCE_FINDINGS_AND_CONFLICTS.md:890), [PIN020-02](SOURCE_FINDINGS_AND_CONFLICTS.md:891), [PIN021-01](SOURCE_FINDINGS_AND_CONFLICTS.md:892), [PIN021-02](SOURCE_FINDINGS_AND_CONFLICTS.md:893), [PIN022-01](SOURCE_FINDINGS_AND_CONFLICTS.md:894), [PIN022-02](SOURCE_FINDINGS_AND_CONFLICTS.md:895), [PIN022-03](SOURCE_FINDINGS_AND_CONFLICTS.md:896), [PIN023-01](SOURCE_FINDINGS_AND_CONFLICTS.md:897), [PIN023-02](SOURCE_FINDINGS_AND_CONFLICTS.md:898), [PIN025-01](SOURCE_FINDINGS_AND_CONFLICTS.md:899), [PIN026-01](SOURCE_FINDINGS_AND_CONFLICTS.md:900), [PIN026-02](SOURCE_FINDINGS_AND_CONFLICTS.md:901), [PIN027-01](SOURCE_FINDINGS_AND_CONFLICTS.md:902), [PIN027-02](SOURCE_FINDINGS_AND_CONFLICTS.md:903), [PIN028-01](SOURCE_FINDINGS_AND_CONFLICTS.md:904), [PIN028-02](SOURCE_FINDINGS_AND_CONFLICTS.md:905), [PIN028-03](SOURCE_FINDINGS_AND_CONFLICTS.md:906), [PIN029-01](SOURCE_FINDINGS_AND_CONFLICTS.md:907), [PIN029-02](SOURCE_FINDINGS_AND_CONFLICTS.md:908), [PIN029-03](SOURCE_FINDINGS_AND_CONFLICTS.md:909), [PIN030-01](SOURCE_FINDINGS_AND_CONFLICTS.md:910), [PIN030-02](SOURCE_FINDINGS_AND_CONFLICTS.md:911), [PIN030-03](SOURCE_FINDINGS_AND_CONFLICTS.md:912), [PIN031-01](SOURCE_FINDINGS_AND_CONFLICTS.md:913), [PIN032-01](SOURCE_FINDINGS_AND_CONFLICTS.md:914), [PIN032-02](SOURCE_FINDINGS_AND_CONFLICTS.md:915), [PIN032-03](SOURCE_FINDINGS_AND_CONFLICTS.md:916), [PIN033-01](SOURCE_FINDINGS_AND_CONFLICTS.md:917), [PIN033-02](SOURCE_FINDINGS_AND_CONFLICTS.md:918), [PIN034-01](SOURCE_FINDINGS_AND_CONFLICTS.md:919), [PIN035-01](SOURCE_FINDINGS_AND_CONFLICTS.md:920), [PIN035-02](SOURCE_FINDINGS_AND_CONFLICTS.md:921), [PIN035-03](SOURCE_FINDINGS_AND_CONFLICTS.md:922), [PIN035-04](SOURCE_FINDINGS_AND_CONFLICTS.md:923), [PIN036-01](SOURCE_FINDINGS_AND_CONFLICTS.md:925), [PIN036-02](SOURCE_FINDINGS_AND_CONFLICTS.md:926), [PIN037-01](SOURCE_FINDINGS_AND_CONFLICTS.md:927), [PIN037-02](SOURCE_FINDINGS_AND_CONFLICTS.md:928), [PIN038-01](SOURCE_FINDINGS_AND_CONFLICTS.md:930), [PIN038-02](SOURCE_FINDINGS_AND_CONFLICTS.md:931), [PIN039-01](SOURCE_FINDINGS_AND_CONFLICTS.md:933), [PIN039-02](SOURCE_FINDINGS_AND_CONFLICTS.md:934), [PIN040-01](SOURCE_FINDINGS_AND_CONFLICTS.md:935), [PIN040-02](SOURCE_FINDINGS_AND_CONFLICTS.md:936), [PIN041-01](SOURCE_FINDINGS_AND_CONFLICTS.md:938), [PIN041-02](SOURCE_FINDINGS_AND_CONFLICTS.md:939), [PIN041-03](SOURCE_FINDINGS_AND_CONFLICTS.md:940), [PIN042-01](SOURCE_FINDINGS_AND_CONFLICTS.md:942), [PIN042-02](SOURCE_FINDINGS_AND_CONFLICTS.md:943), [PIN043-01](SOURCE_FINDINGS_AND_CONFLICTS.md:944), [PIN044-01](SOURCE_FINDINGS_AND_CONFLICTS.md:945), [PIN044-02](SOURCE_FINDINGS_AND_CONFLICTS.md:946), [PIN045-01](SOURCE_FINDINGS_AND_CONFLICTS.md:948), [PIN045-02](SOURCE_FINDINGS_AND_CONFLICTS.md:949), [PIN045-03](SOURCE_FINDINGS_AND_CONFLICTS.md:950), [PIN045-04](SOURCE_FINDINGS_AND_CONFLICTS.md:951), [PIN045-05](SOURCE_FINDINGS_AND_CONFLICTS.md:952), [PIN045-06](SOURCE_FINDINGS_AND_CONFLICTS.md:953), [PIN046-01](SOURCE_FINDINGS_AND_CONFLICTS.md:955), [PIN047-01](SOURCE_FINDINGS_AND_CONFLICTS.md:956), [PIN047-02](SOURCE_FINDINGS_AND_CONFLICTS.md:957), [PIN047-03](SOURCE_FINDINGS_AND_CONFLICTS.md:958), [PIN048-01](SOURCE_FINDINGS_AND_CONFLICTS.md:960), [PIN048-02](SOURCE_FINDINGS_AND_CONFLICTS.md:961), [PIN048-03](SOURCE_FINDINGS_AND_CONFLICTS.md:962), [PIN049-01](SOURCE_FINDINGS_AND_CONFLICTS.md:964), [PIN049-02](SOURCE_FINDINGS_AND_CONFLICTS.md:965), [PIN049-03](SOURCE_FINDINGS_AND_CONFLICTS.md:966), [PIN050-01](SOURCE_FINDINGS_AND_CONFLICTS.md:968), [PIN050-02](SOURCE_FINDINGS_AND_CONFLICTS.md:969), [PIN050-03](SOURCE_FINDINGS_AND_CONFLICTS.md:970), [PIN051-01](SOURCE_FINDINGS_AND_CONFLICTS.md:971), [PIN051-02](SOURCE_FINDINGS_AND_CONFLICTS.md:972), [PIN052-01](SOURCE_FINDINGS_AND_CONFLICTS.md:974), [PIN052-02](SOURCE_FINDINGS_AND_CONFLICTS.md:975), [PIN052-03](SOURCE_FINDINGS_AND_CONFLICTS.md:976), [PIN054-01](SOURCE_FINDINGS_AND_CONFLICTS.md:978), [PIN054-02](SOURCE_FINDINGS_AND_CONFLICTS.md:979), [PIN055-01](SOURCE_FINDINGS_AND_CONFLICTS.md:980), [PIN055-02](SOURCE_FINDINGS_AND_CONFLICTS.md:981), [PIN056-01](SOURCE_FINDINGS_AND_CONFLICTS.md:983), [PIN056-02](SOURCE_FINDINGS_AND_CONFLICTS.md:984), [PIN057-01](SOURCE_FINDINGS_AND_CONFLICTS.md:985), [PIN057-02](SOURCE_FINDINGS_AND_CONFLICTS.md:986), [PIN057-03](SOURCE_FINDINGS_AND_CONFLICTS.md:987), [PIN058-01](SOURCE_FINDINGS_AND_CONFLICTS.md:989), [PIN059-01](SOURCE_FINDINGS_AND_CONFLICTS.md:990), [PIN059-02](SOURCE_FINDINGS_AND_CONFLICTS.md:991), [PIN060-01](SOURCE_FINDINGS_AND_CONFLICTS.md:993), [PIN060-02](SOURCE_FINDINGS_AND_CONFLICTS.md:994), [PIN060-03](SOURCE_FINDINGS_AND_CONFLICTS.md:995), [PIN061-01](SOURCE_FINDINGS_AND_CONFLICTS.md:997), [PIN061-02](SOURCE_FINDINGS_AND_CONFLICTS.md:998), [PIN061-03](SOURCE_FINDINGS_AND_CONFLICTS.md:999), [PIN062-01](SOURCE_FINDINGS_AND_CONFLICTS.md:1001), [PIN062-02](SOURCE_FINDINGS_AND_CONFLICTS.md:1002), [PIN062-03](SOURCE_FINDINGS_AND_CONFLICTS.md:1003), [PIN063-01](SOURCE_FINDINGS_AND_CONFLICTS.md:1005), [PIN063-02](SOURCE_FINDINGS_AND_CONFLICTS.md:1006), [PIN063-03](SOURCE_FINDINGS_AND_CONFLICTS.md:1007), [PIN064-01](SOURCE_FINDINGS_AND_CONFLICTS.md:1009), [PIN064-02](SOURCE_FINDINGS_AND_CONFLICTS.md:1010), [PIN065-01](SOURCE_FINDINGS_AND_CONFLICTS.md:1012), [PIN065-02](SOURCE_FINDINGS_AND_CONFLICTS.md:1013), [PIN065-03](SOURCE_FINDINGS_AND_CONFLICTS.md:1014), [PIN066-01](SOURCE_FINDINGS_AND_CONFLICTS.md:1016), [PIN066-02](SOURCE_FINDINGS_AND_CONFLICTS.md:1017), [PIN066-03](SOURCE_FINDINGS_AND_CONFLICTS.md:1018), [PIN066-04](SOURCE_FINDINGS_AND_CONFLICTS.md:1019), [PIN067-01](SOURCE_FINDINGS_AND_CONFLICTS.md:1021), [PIN067-02](SOURCE_FINDINGS_AND_CONFLICTS.md:1022), [PIN068-01](SOURCE_FINDINGS_AND_CONFLICTS.md:1024), [PIN068-02](SOURCE_FINDINGS_AND_CONFLICTS.md:1025), [PIN068-03](SOURCE_FINDINGS_AND_CONFLICTS.md:1026), [PIN069-01](SOURCE_FINDINGS_AND_CONFLICTS.md:1028), [PIN069-02](SOURCE_FINDINGS_AND_CONFLICTS.md:1029), [PIN069-03](SOURCE_FINDINGS_AND_CONFLICTS.md:1030), [PIN069-04](SOURCE_FINDINGS_AND_CONFLICTS.md:1031), [PIN070-01](SOURCE_FINDINGS_AND_CONFLICTS.md:1033), [PIN070-02](SOURCE_FINDINGS_AND_CONFLICTS.md:1034), [PIN071-01](SOURCE_FINDINGS_AND_CONFLICTS.md:1036), [PIN071-02](SOURCE_FINDINGS_AND_CONFLICTS.md:1037), [PIN071-03](SOURCE_FINDINGS_AND_CONFLICTS.md:1038), [PIN071-04](SOURCE_FINDINGS_AND_CONFLICTS.md:1039), [PIN071-05](SOURCE_FINDINGS_AND_CONFLICTS.md:1040), [PIN071-06](SOURCE_FINDINGS_AND_CONFLICTS.md:1041), [PIN071-07](SOURCE_FINDINGS_AND_CONFLICTS.md:1042), [PIN071-08](SOURCE_FINDINGS_AND_CONFLICTS.md:1043), [PIN072-01](SOURCE_FINDINGS_AND_CONFLICTS.md:1045), [PIN072-02](SOURCE_FINDINGS_AND_CONFLICTS.md:1046), [PIN073-01](SOURCE_FINDINGS_AND_CONFLICTS.md:1048), [PIN073-02](SOURCE_FINDINGS_AND_CONFLICTS.md:1049), [PIN074-01](SOURCE_FINDINGS_AND_CONFLICTS.md:1051), [PIN074-02](SOURCE_FINDINGS_AND_CONFLICTS.md:1052), [PIN075-01](SOURCE_FINDINGS_AND_CONFLICTS.md:1054), [PIN075-02](SOURCE_FINDINGS_AND_CONFLICTS.md:1055), [PIN076-01](SOURCE_FINDINGS_AND_CONFLICTS.md:1057), [PIN076-02](SOURCE_FINDINGS_AND_CONFLICTS.md:1058), [PIN077-01](SOURCE_FINDINGS_AND_CONFLICTS.md:1060), [PIN077-02](SOURCE_FINDINGS_AND_CONFLICTS.md:1061), [PIN078-01](SOURCE_FINDINGS_AND_CONFLICTS.md:1063), [PIN078-02](SOURCE_FINDINGS_AND_CONFLICTS.md:1064), [PIN079-01](SOURCE_FINDINGS_AND_CONFLICTS.md:1066), [PIN079-02](SOURCE_FINDINGS_AND_CONFLICTS.md:1067), [PIN079-03](SOURCE_FINDINGS_AND_CONFLICTS.md:1068), [PIN079-04](SOURCE_FINDINGS_AND_CONFLICTS.md:1069), [PIN080-01](SOURCE_FINDINGS_AND_CONFLICTS.md:1071), [PIN080-02](SOURCE_FINDINGS_AND_CONFLICTS.md:1072), [PIN080-03](SOURCE_FINDINGS_AND_CONFLICTS.md:1073), [PIN081-01](SOURCE_FINDINGS_AND_CONFLICTS.md:1075), [PIN081-02](SOURCE_FINDINGS_AND_CONFLICTS.md:1076), [PIN081-03](SOURCE_FINDINGS_AND_CONFLICTS.md:1077), [PIN081-04](SOURCE_FINDINGS_AND_CONFLICTS.md:1078), [PIN082-01](SOURCE_FINDINGS_AND_CONFLICTS.md:1080), [PIN082-02](SOURCE_FINDINGS_AND_CONFLICTS.md:1081), [PIN082-03](SOURCE_FINDINGS_AND_CONFLICTS.md:1082), [PIN083-01](SOURCE_FINDINGS_AND_CONFLICTS.md:1084), [PIN083-02](SOURCE_FINDINGS_AND_CONFLICTS.md:1085).

**Conversation upgrade lineage.** [DTM-A07](SOURCE_FINDINGS_AND_CONFLICTS.md:65). Read the full rows and their original conversation references; [the recheck](CONVERSATION_RECHECK.md) preserves the exact unit/exception routes.

<a id="up-v06-prefix_restart"></a>
#### V06.PREFIX_RESTART — End-to-end replay equivalence

[Existing definition, target and P0–P7](experiments/V.md#v06-prefix_restart) remain binding.

**Specific upgrade scope.** Add trace checkpoint comparison and first-divergence localization across semantic, numeric and action outputs.

**Local comparison.** Compare literal and optimized/restarted chains after planted timing/state faults; measure localization speed and reproducibility.

**Additional cases.** Numeric tolerance hides action rank change; unfinished bar lost; stale version; no tick at timer.

<a id="up-v07"></a>
### UP-V07 — Failure attribution and controlled diagnostic interventions

Parent: [V07](components/RESEARCH_AND_OPERATIONS.md); [local phases](experiments/V.md#v07); [definition refinement](SYSTEM_REFINEMENT.md#sr-v07). Upgrade role: `research_method`.

**Starting idea.** Explain performance using feature importance or selected winning charts.

**Existing improvement path.** Layered failure attribution and controlled ablations with common cohorts.

**Remaining weakness.** Ablation loss conflates unique information, substitution by correlated inputs, model refitting and candidate-population changes.

**Further upgrade.** Use a structured diagnostic matrix: frozen scorer/generator, refitted drop-one, small prespecified interaction tests, representation-versus-capacity comparison and candidate/population controls. Add plausible perturbations and precisely scoped oracle diagnostics, never performance evidence. Certify an upper bound only with an exact scoped optimum or a valid bounding argument; a heuristic oracle is labelled approximate.

**Fair comparison.** Each diagnostic estimates its stated quantity; compare conclusions across paired dates and preserve incompatible/intervention limits.

**Evidence.** Failure ownership, uncertainty of marginal/joint contribution, reproducible attribution and practical upgrade targets.

**Additional local cases to implement.** Two redundant features each look unnecessary; interaction-only signal; deleting a generator changes opportunities; attention map misread as causality.

**Decision or system use.** Choose whether to improve measurement, add information, change the learner, change selection or remove a branch.

**Exact reviewed source clauses.** [DTM-A01](SOURCE_FINDINGS_AND_CONFLICTS.md:59), [DTM-A02](SOURCE_FINDINGS_AND_CONFLICTS.md:60), [DTM-A17](SOURCE_FINDINGS_AND_CONFLICTS.md:75), [JXA-02](SOURCE_FINDINGS_AND_CONFLICTS.md:101), [JFN-01](SOURCE_FINDINGS_AND_CONFLICTS.md:135), [JFN-02](SOURCE_FINDINGS_AND_CONFLICTS.md:136), [JFN-03](SOURCE_FINDINGS_AND_CONFLICTS.md:137), [JFN-04](SOURCE_FINDINGS_AND_CONFLICTS.md:138), [JFN-05](SOURCE_FINDINGS_AND_CONFLICTS.md:139), [JFN-06](SOURCE_FINDINGS_AND_CONFLICTS.md:140), [JFN-07](SOURCE_FINDINGS_AND_CONFLICTS.md:141), [JFN-08](SOURCE_FINDINGS_AND_CONFLICTS.md:142), [JFN-09](SOURCE_FINDINGS_AND_CONFLICTS.md:143), [JFN-10](SOURCE_FINDINGS_AND_CONFLICTS.md:144), [JFN-11](SOURCE_FINDINGS_AND_CONFLICTS.md:145), [JFN-12](SOURCE_FINDINGS_AND_CONFLICTS.md:146), [JCV-U01](SOURCE_FINDINGS_AND_CONFLICTS.md:154), [JCV-U05](SOURCE_FINDINGS_AND_CONFLICTS.md:158), [JCV-A02](SOURCE_FINDINGS_AND_CONFLICTS.md:161), [CEX-01](SOURCE_FINDINGS_AND_CONFLICTS.md:183), [CEX-14](SOURCE_FINDINGS_AND_CONFLICTS.md:196), [CRL-01](SOURCE_FINDINGS_AND_CONFLICTS.md:217), [CRL-03](SOURCE_FINDINGS_AND_CONFLICTS.md:219), [DEN-01](SOURCE_FINDINGS_AND_CONFLICTS.md:409), [DEN-02](SOURCE_FINDINGS_AND_CONFLICTS.md:410), [DEN-03](SOURCE_FINDINGS_AND_CONFLICTS.md:411), [DEN-04](SOURCE_FINDINGS_AND_CONFLICTS.md:412), [DEN-05](SOURCE_FINDINGS_AND_CONFLICTS.md:413), [DRF-U10](SOURCE_FINDINGS_AND_CONFLICTS.md:434), [DRF-U12](SOURCE_FINDINGS_AND_CONFLICTS.md:436), [DRF-A22](SOURCE_FINDINGS_AND_CONFLICTS.md:463), [DRF-A25](SOURCE_FINDINGS_AND_CONFLICTS.md:466), [DRF-A26](SOURCE_FINDINGS_AND_CONFLICTS.md:467), [DRF-A28](SOURCE_FINDINGS_AND_CONFLICTS.md:469), [DRF-A29](SOURCE_FINDINGS_AND_CONFLICTS.md:470), [K10-01](SOURCE_FINDINGS_AND_CONFLICTS.md:639), [K10-02](SOURCE_FINDINGS_AND_CONFLICTS.md:640), [K10-03](SOURCE_FINDINGS_AND_CONFLICTS.md:641), [K10-04](SOURCE_FINDINGS_AND_CONFLICTS.md:642), [K10-05](SOURCE_FINDINGS_AND_CONFLICTS.md:643), [K10-06](SOURCE_FINDINGS_AND_CONFLICTS.md:644), [K18-01](SOURCE_FINDINGS_AND_CONFLICTS.md:652), [K18-02](SOURCE_FINDINGS_AND_CONFLICTS.md:653), [K18-03](SOURCE_FINDINGS_AND_CONFLICTS.md:654), [K18-04](SOURCE_FINDINGS_AND_CONFLICTS.md:655), [K18-05](SOURCE_FINDINGS_AND_CONFLICTS.md:656), [K18-06](SOURCE_FINDINGS_AND_CONFLICTS.md:657), [K18-07](SOURCE_FINDINGS_AND_CONFLICTS.md:658), [K18-08](SOURCE_FINDINGS_AND_CONFLICTS.md:659), [F23-01](SOURCE_FINDINGS_AND_CONFLICTS.md:667), [F23-02](SOURCE_FINDINGS_AND_CONFLICTS.md:668), [F23-03](SOURCE_FINDINGS_AND_CONFLICTS.md:669), [F23-04](SOURCE_FINDINGS_AND_CONFLICTS.md:670), [F23-05](SOURCE_FINDINGS_AND_CONFLICTS.md:671), [F23-06](SOURCE_FINDINGS_AND_CONFLICTS.md:672), [F23-07](SOURCE_FINDINGS_AND_CONFLICTS.md:673), [ALS-01](SOURCE_FINDINGS_AND_CONFLICTS.md:696), [ALS-02](SOURCE_FINDINGS_AND_CONFLICTS.md:697), [ALS-03](SOURCE_FINDINGS_AND_CONFLICTS.md:698), [ALS-04](SOURCE_FINDINGS_AND_CONFLICTS.md:699), [ALS-05](SOURCE_FINDINGS_AND_CONFLICTS.md:700), [ALS-06](SOURCE_FINDINGS_AND_CONFLICTS.md:701), [NYA-01](SOURCE_FINDINGS_AND_CONFLICTS.md:709), [NYA-02](SOURCE_FINDINGS_AND_CONFLICTS.md:710), [NYA-03](SOURCE_FINDINGS_AND_CONFLICTS.md:711), [NYA-04](SOURCE_FINDINGS_AND_CONFLICTS.md:712), [NYA-05](SOURCE_FINDINGS_AND_CONFLICTS.md:713), [NYA-06](SOURCE_FINDINGS_AND_CONFLICTS.md:714), [AUT-07](SOURCE_FINDINGS_AND_CONFLICTS.md:773).

**Conversation upgrade lineage.** [DTM-A02](SOURCE_FINDINGS_AND_CONFLICTS.md:60), [DTM-A17](SOURCE_FINDINGS_AND_CONFLICTS.md:75), [JCV-U05](SOURCE_FINDINGS_AND_CONFLICTS.md:158), [JCV-A02](SOURCE_FINDINGS_AND_CONFLICTS.md:161), [CEX-01](SOURCE_FINDINGS_AND_CONFLICTS.md:183), [CEX-02](SOURCE_FINDINGS_AND_CONFLICTS.md:184), [CEX-14](SOURCE_FINDINGS_AND_CONFLICTS.md:196), [CRL-03](SOURCE_FINDINGS_AND_CONFLICTS.md:219), [DRF-U10](SOURCE_FINDINGS_AND_CONFLICTS.md:434), [DRF-U12](SOURCE_FINDINGS_AND_CONFLICTS.md:436), [DRF-A25](SOURCE_FINDINGS_AND_CONFLICTS.md:466), [DRF-A28](SOURCE_FINDINGS_AND_CONFLICTS.md:469). Read the full rows and their original conversation references; [the recheck](CONVERSATION_RECHECK.md) preserves the exact unit/exception routes.

<a id="up-v07-oracle_scope"></a>
#### V07.ORACLE_SCOPE — Exact in-set diagnostic ceiling

[Existing definition, target and P0–P7](experiments/V.md#v07-oracle_scope) remain binding.

**Specific upgrade scope.** Decompose diagnostic ceilings by admitted information, candidate set, action template and fill scenario using explicit future access only in the oracle diagnostic.

**Local comparison.** Use exact bounded enumeration where feasible; a heuristic oracle solver is not a certified upper bound. Compare real policy to the clearly stated feasible diagnostic scope.

**Additional cases.** Out-of-set hindsight entry; unknown passive fill; occupancy ignored; heuristic misses better feasible path.

<a id="up-v07-planted_signal"></a>
#### V07.PLANTED_SIGNAL — Synthetic positive and null controls

[Existing definition, target and P0–P7](experiments/V.md#v07-planted_signal) remain binding.

**Specific upgrade scope.** Plant known individual, redundant and interaction-only signals plus causal nulls into the actual candidate/fit pipeline.

**Local comparison.** Compare attribution and selection recovery with exact known mechanisms, without treating synthetic success as market performance.

**Additional cases.** Two redundant features; interaction only; hidden leakage; selected population changes.

<a id="up-v08"></a>
### UP-V08 — Resource-aware reproducible experiment orchestration

Parent: [V08](components/RESEARCH_AND_OPERATIONS.md); [local phases](experiments/V.md#v08); [definition refinement](SYSTEM_REFINEMENT.md#sr-v08). Upgrade role: `engineering`.

**Starting idea.** Run the largest feature/model grid that fits the machine.

**Existing improvement path.** Bounded pilots, caching, trial budgets and measured resource envelopes.

**Remaining weakness.** Trials may spend too much on low-value duplicate work while valuable families remain unexamined.

**Further upgrade.** Schedule a registered broad-coverage pilot for every eligible family, then allocate expansion by measured support, uncertainty, plausible useful effect and marginal compute cost. Use resumable DAG jobs, shared features and paired scenario seeds; retain explicit rejected/inconclusive/dependency records for every branch.

**Fair comparison.** Uniform expansion versus staged resource allocation with identical total budget and immutable evaluation sets.

**Evidence.** Completed scope coverage, useful evidence per CPU/GPU-hour, peak RAM/storage, wasted duplicate work and reproducible resumption.

**Additional local cases to implement.** One expensive model consumes all budget; failed worker; stale cache; rare family needs more days rather than compute; negative pilot closes a branch with evidence.

**Decision or system use.** Complete the full authorized research scope efficiently; resource limits can produce explicit inconclusive outcomes, never silent omissions or fabricated success.

**Exact reviewed source clauses.** [JCV-U03](SOURCE_FINDINGS_AND_CONFLICTS.md:156), [JCV-U06](SOURCE_FINDINGS_AND_CONFLICTS.md:159), [JCV-A09](SOURCE_FINDINGS_AND_CONFLICTS.md:168), [CEX-10](SOURCE_FINDINGS_AND_CONFLICTS.md:192), [CEX-20](SOURCE_FINDINGS_AND_CONFLICTS.md:202), [CEX-22](SOURCE_FINDINGS_AND_CONFLICTS.md:204), [INV-01](SOURCE_FINDINGS_AND_CONFLICTS.md:262), [INV-02](SOURCE_FINDINGS_AND_CONFLICTS.md:263), [INV-03](SOURCE_FINDINGS_AND_CONFLICTS.md:264), [INV-04](SOURCE_FINDINGS_AND_CONFLICTS.md:265), [INV-05](SOURCE_FINDINGS_AND_CONFLICTS.md:266), [INV-06](SOURCE_FINDINGS_AND_CONFLICTS.md:267), [INV-07](SOURCE_FINDINGS_AND_CONFLICTS.md:268), [INV-08](SOURCE_FINDINGS_AND_CONFLICTS.md:269), [INV-09](SOURCE_FINDINGS_AND_CONFLICTS.md:270), [INV-10](SOURCE_FINDINGS_AND_CONFLICTS.md:271), [INV-11](SOURCE_FINDINGS_AND_CONFLICTS.md:272), [INV-12](SOURCE_FINDINGS_AND_CONFLICTS.md:273), [DRF-A03](SOURCE_FINDINGS_AND_CONFLICTS.md:444).

**Conversation upgrade lineage.** [DTM-A17](SOURCE_FINDINGS_AND_CONFLICTS.md:75), [JCV-U06](SOURCE_FINDINGS_AND_CONFLICTS.md:159), [JCV-A09](SOURCE_FINDINGS_AND_CONFLICTS.md:168), [CEX-22](SOURCE_FINDINGS_AND_CONFLICTS.md:204), [CRL-08](SOURCE_FINDINGS_AND_CONFLICTS.md:224). Read the full rows and their original conversation references; [the recheck](CONVERSATION_RECHECK.md) preserves the exact unit/exception routes.

<a id="up-v08-resource_frontier"></a>
#### V08.RESOURCE_FRONTIER — Measured accuracy, latency and resource tradeoffs

[Existing definition, target and P0–P7](experiments/V.md#v08-resource_frontier) remain binding.

**Specific upgrade scope.** Measure paired accuracy/latency/RAM/storage frontiers and allocate expansion after broad eligible-family coverage.

**Local comparison.** Compare literal/shared materialization, simple/rich models and staged budgets with immutable evaluation sets and resumable jobs.

**Additional cases.** One family consumes budget; failed worker; stale cache; more time/data needed rather than more compute.

## Method references and limits of external support

The designs above are proposed applications and extensions, not claims that a cited paper established their performance on this dataset. These focused references supplement the existing 119 external finding records; they are kept as three method-reference entries, not silently added to the historical review totals. Before reproducing a named source algorithm, verify its full required equations and assumptions in the implementation definition phase.

**UP-METH-01: [Andersen, Bollerslev, Diebold and Labys — Realized Volatility and Correlation (1999 working paper)](https://archive.nyu.edu/bitstream/2451/27128/2/wpa99061.pdf).** ARFIMA as a fractional-memory model of log realized volatility; no copied parameter value, Gaussian-return guarantee or NQ/ES performance result. Read scope: Focused text read of section 4, PDF pages 9–10, plus surrounding sampling-noise discussion. Not a fresh full-paper review. Units: C12.NOISE, C13.HAR_VARIANTS, G02.MULTITARGET.

**UP-METH-02: [Chazal, Guibas, Oudot and Skraba — Persistence-Based Clustering in Riemannian Manifolds (2013)](https://doi.org/10.1145/2535927).** Mode prominence/persistence as a clustering idea. Trading-profile dependence, weighted observations and smoothing-scale stability need their own tests; no transferred statistical guarantee. Read scope: Publisher and author-hosted indexed abstracts read; full-PDF web retrieval exceeded size limit and publisher open failed. Conceptual reference only, not a formula/theorem reproduction. Units: M04.TOPOLOGY, O11.NODE_GEOMETRY, L05.PROFILE_ROLES.

**UP-METH-03: [Bacry and Muzy — Hawkes model for price and trades high-frequency dynamics (2013)](https://arxiv.org/abs/1301.1135).** Joint trade-arrival/price-change kernels as a bounded model challenger. Futures event semantics, stability, likelihood and actual predictive value must be verified independently. Read scope: Author abstract and bibliographic page read; no full-paper implementation reproduction. Units: M09.RECOVERY, M10.INTENSITY, C18.CONTROL, X07.FLOW_SMT.

## Evidence, preservation and completion

The authored [parent paths](review/system-refinement/upgrade_paths.psv), [child bindings](review/system-refinement/upgrade_bindings.psv) and [machine upgrade registry](review/system-refinement/upgrade_registry.json) preserve exact IDs. All 712 supplied-source routes and 122 conversation routes are carried into that registry. These links point to the original reviewed findings rather than replacing their detailed clauses with this summary. The [preserved baseline](review/system-refinement/baseline.zip) records the plan before this refinement pass.

Every parent and child has the upgrade in its local definition, case, comparison, interaction and decision phases. The implementation ledger records actual code, semantic verification, eligible experiments and selected/rejected/inconclusive/blocked disposition separately. New target schemas, fitted transforms and ports must be registered under UPGRADE_CONSTRUCTIONS before dependent code, with the DAG and OOF closure checked. All experiments here remain planned. Coverage, link and hash checks establish document consistency only.
