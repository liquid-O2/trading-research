# 01: Published 06–09 range to a real path report

**What to build:** Inspect one source-defined 06–09 NQ range, its honest session coverage, and the 09–12 high-only/low-only/both/neither path on real data.

**Blocked by:** None (first slice after this planning task; definition blockers still apply).

**Definition blockers:** Q01, Q03 in [QUESTIONS](../QUESTIONS.md)

**Status:** planned — no implementation or worker authorized in this session.

**PRD story:** [S01](../PRD.md). **Wiki:** [time based ranges](../wiki/time-based-ranges.md), [range break paths](../wiki/range-break-paths.md), [inventory and availability](../wiki/inventory-and-availability.md). **Contract:** [SPEC](../SPEC.md).

## Owned scope

Own only the published06–09 NQ baseline and its source09–12 path/coverage report. Ticket06 owns the other clock and formation-bar comparisons. Do not expand this first proof to every range source.

## Vertical slice

1. Freeze the cited source definition and this slice’s finite named variants. Resolve its questions before claiming faithful measurement. Preserve literal-source and causal/experimental identities when they differ.
2. Compute the object/feature and its future path on actual acquired data. Start with the narrowest real discovery sample that exercises the definition and its failure case. Extend to the longest honest family sample; do not widen into an unrelated data audit.
3. Produce the source-versus-variant coverage/statistics report, with eligible sessions/events, ambiguity, failures and missingness. Freeze choices before reading confirmation. Reuse predecessor records and accepted evidence by identity; add only helpers necessary to make this report true.

## Independent expected result

A hand-built range H100/L90 followed by 91,89,95,101 must be both/low-first; a no-breach path must remain neither. An incomplete formation is excluded with reason.

Use this expected example plus a manually adjudicated real-data example from the cited definition. The implementation must not generate its own expected answer. Source empirical percentages and selected success charts are not golden results.

## Acceptance

- [ ] Every source construction within this ticket’s stated scope is represented by a faithful row or its explicit definition/data/defer status. No unsupported approximation is called faithful.
- [ ] The named wiki upgrades owned by this ticket are measured through the same declared outcomes. Freeze a finite set of variants/ablation combinations; do not silently drop a required CVD, day class, zone or bar family.
- [ ] Independent examples pass and every source/implementation disagreement is explained. Availability precedes outcomes; ambiguous OHLC order remains explicit.
- [ ] The report shows native coverage and matched comparisons, full failure/no-event populations, outcome-specific n, year stability and frozen confirmation boundaries. Null/worse or low-support results are reported honestly.
- [ ] The proposed command below emits the shared header and this slice’s real report rows. Required blocked definitions, omissions or unexplained fidelity errors make verification nonzero.

## Coverage and statistics command

```sh
phase1 measure --slice 01 --verify
```

This is a proposed interface for later execution, not an existing or executed command. Planned report root: `reports/phase-1/01/`. Each printed row must point to its actual generated report.

## Scope and handoff

Own this selector’s definition → computation → evidence path and the minimum necessary shared change. Concrete application file locations are chosen during execution; do not scaffold speculative infrastructure now. Preserve raw sources, raw data and archive. No bundled indicator execution, model training, trading or P&L acceptance. After the slice passes, record result, evidence path and remaining blockers, then continue on the unblocked frontier under [PHASE](../PHASE.md). No wall-clock kill or unrequested retry loop.
