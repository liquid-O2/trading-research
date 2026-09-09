# Handoff review and implementation interpretation

Review date: 2026-09-06. This review accompanies the initial implementation; it
does not certify the whole research program as complete.

**Subsequent correction:** [CONFORMANCE_AUDIT.md](CONFORMANCE_AUDIT.md) records
that original-source closure and parts of the refinement/upgrade review were not
completed before all dependent work. The initial reading summary below must not
be interpreted as complete compliance with that prerequisite. Its remaining-work
list is historical; [STATUS.md](STATUS.md) is current.

## Scope and sequencing

The handoff is a full research program. Its 344 units consist of 153 parents and
191 refinements, with eight local phases each. The implementation imports all
2,752 phase records, 712 supplied-source findings, 119 external findings,
68 requirements, 111 datasets, 64 backlog tasks and three method records. These
produce 4,173 exact ledger IDs. Counting them is a coverage check; their current
implementation and evaluation state must come from executed evidence.

The governing handoff, scope, master plan, requirements, source contract,
shared contracts, computation schedule, runtime scheduler, data capability
audit, quality/stopping rules, validation plan, complete backlog, specialist
experiment rules, experiment index, shared upgrade constructions and E0
reference were reviewed before building. Relevant foundation and research
parent cards, refinements, upgrades and local phase definitions were read for
the implemented services. The remaining per-unit original-source clause
expansion is explicitly unfinished. The earlier package's source-review totals
are prior planning evidence, not a new claim that this implementation has
verified every supplied mechanism.

The earlier planning-only instruction describes the prior planning task. The
current request authorizes starting implementation and bounded local checks.
It does not supply a trading deployment decision, new purchases or actual
prospective observations. The excluded archive remains outside this work.

The dependency order is substantive: B00 identity/time/evidence; B01 data and
calendar eligibility; B02 deterministic flow and objects; B03 E0; then eligible
Context, options, cross-market, Location/selection, policy/risk, later Response
and prospective evidence. Context and Location can originate entries. E0 does
not discharge the other specialists or their comparisons. An optional feed
dependency should disable its consumers while unrelated work continues.

## Binding decisions

| Question | Interpretation and implementation consequence |
|---|---|
| What is the account constraint? | One account, flat or one outright NQ/ES mini; NQ preferred. No copied accounts, extra units, partial exits or micro substitution. Informational mini-equivalents are a different unit. |
| What is the objective? | Assess mean daily net against $2,000 across all eligible days, including zero-trade days. The $1,000 daily loss objective is not silently changed into a trailing drawdown rule or a guaranteed stop outcome. |
| What counts as net? | Preserve trading net and business cash separately until target accounting is resolved. E0 requires verified numeric all-in fees; a missing input cannot become zero. |
| Which futures data is primary? | Acquired MBP-1. Its derived best-quote state is distinct from interval-sampled `bbo-1s`/`bbo-1m`. Standalone trades are a reconciliation/alternate source, not additional volume. |
| Which records are trades? | `T` records retain B/A/N aggressor meaning, including prints without `F_LAST`. Nontrade side is the resting side. Unknown aggressor contributes to total volume and uncertainty. |
| How is book state updated? | Attached trade BBO is pre-trade state. The reducer does not subtract execution size and then subtract the supplied quote change again. Snapshot adds are initialization, not fresh pressure. |
| What happens after a gap? | Bit 4 invalidates trusted book use. A later plausible quote cannot certify recovery. An explicit reconstruction certificate can recover the book; it cannot reconstruct missing flow history. |
| Which time is available? | Event time, provider receive time, actual strategy receipt, publication, computation and validity remain distinct. Missing strategy receipt stays missing, accompanied by a named historical assumption. |
| Can a computation be backdated? | Derived known time includes required input availability, completion and confirmation. Actual computation duration is not added a second time. Objects retain their confirmation and revision history. |
| Can forecast outputs substitute for each other? | Units, horizon, population, geometry, observation process and capabilities must match. Variance/excursion outputs do not identify the ordering of barrier hits. A later contact does not restart an earlier fixed-end target. |
| What is a location's width? | Physical support, labeled contact region, estimation uncertainty, mapping uncertainty and entry tolerance are separate. Changing the labeled region changes target identity. |
| What counts as forward evaluation? | Same-date related assets/objects remain grouped. Labels must be mature and dependency intervals purged before fitting. OOF exclusion includes scalers, transforms, experts and calibrators. |
| What makes a run reproducible? | Immutable code/configuration/input/fold/target identities, actual read lineage, atomic outputs and retained failed/interrupted attempts. Renaming the same configuration does not create independent evidence. |
| What counts as completion? | Engineering fidelity, empirical disposition, complete-policy economics and future dependencies are separate. An operational invariant is accepted on fidelity; a hypothesis needs empirical evaluation. |

The MBP interpretation follows the supplied source contract and the official
[MBP-1 schema](https://databento.com/docs/schemas-and-data-formats/mbp-1),
[common fields and flags](https://databento.com/docs/standards-and-conventions/common-fields-enums-types)
and [CME normalization](https://databento.com/docs/venues-and-datasets/glbx-mdp3).
Publisher-specific bits remain unresolved source-version information; they are
not automatically treated as direction or corruption.

## Material implementation risks

1. **Coverage differs by dataset, field and cohort.** NQ/ES QuantPad MBP has eleven
   supplied fields and omits several native timing/sequence/count fields. An
   options daily chain does not establish intraday quote coverage. Daily cash
   or volatility data cannot stand in for contemporaneous intraday observations.
   The catalog is imported in full, but full B01 certification remains open.
2. **A clean later book does not repair past flow.** The initial reducer and its
   gap fixture keep these quality states separate. Real recovery certificates
   and complete anchor/reset rules still need source-specific work.
3. **Reference correctness is not runtime readiness.** Per-row lossless encoding,
   hashes and retained ingestion identities are deliberately literal. The
   measured pilot is the starting point for optimization, persistent ingestion
   state and independent reference parity. Hard worker resource enforcement,
   atomic account/risk reservation and independent live timer handling remain
   required work.
4. **Source proposals are hypotheses.** Source-specific exceptions, unpublished
   formulas, interpretations, negative comparisons and upgrades must receive
   explicit assertions or dependencies. A component label or a nearby fixture
   cannot discharge them. No source's reported performance is adopted as an
   empirical prior.
5. **Historical and future evidence are different.** Previously inspected
   historical periods remain development/retrospective data. B10 begins after
   versions and its endpoint/inference protocol are frozen; it needs future
   elapsed eligible days and permitted receipt capture.

## Immediate remaining work

Expand the current services' source/local cases into complete assertion
inventories; complete the runtime port graph and remaining B00 reward,
standing-venue-quote, duplicate-assimilation and scheduler fixtures. Follow with
matched-hour embedded/standalone trade reconciliation, calendar/roll and
instrument certification, field/cohort eligibility and bounded full-partition
quality scans. Implement B02 CVD/profile/object references with those clocks and
quality states, then the neutral one-mini execution/account harness and E0.

The arithmetic and calendar fixtures are synthetic controls. The current
16,384-record pilot is an observed data-engineering result. Neither is an
economic experiment. The full scope stays in the ledger for continued work.
