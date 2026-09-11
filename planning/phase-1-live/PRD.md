# Phase 1 implementer pack — product requirements

Version: `method-pack-v1`, 2026-09-11.

## Problem Statement

The wiki defines operating methods, but the existing implementation mostly scores isolated objects and daily flags. Those scores cannot establish that a method had its context, reference, confirmation, risk and objective in the right order. Some callers use future information or a different construction; several required source definitions and data surfaces are missing. An implementer must not resolve those gaps by inventing a trading rule.

## Solution

Deliver one checkable outcome: **for each of the 12 operating methods mapped by the wiki, a single method pass produces a reproducible report of its cited sequence or process, with every verdict traceable to timed evidence or an explicit hole.** The unit is the operating method. Branches and objects remain inside their parent method.

Completion means all 12 commands can execute their declared fixture and report contract; all 166 object procedures and all 373 predicate operands are covered; negative/unknown cases are correctly distinguished; every requested headline has a valid report artifact; and incorrectly admitted leakage/proxy-as-faithful counts are zero. A correct source_hole or data_hole report is valid completion of the audit implementation. It is not a claim that the source method is fully discoverable or profitable.

The inventory is fixed: `JJ-TBR`, `GB-FAIL`, `GB-VWAP`, `GB-SCALP`, `SIRES`, `SAINT-AMT`, `MEMBER-TWO-REASONS`, `KEANI-OPEN-ABOVE-VALUE`, `REFILL-STUDY`, `JETBUNDLE-STATES`, `STOIC-DATA`, `STOIC-RISK`.

## User Stories

1. As an implementer, I want one stable inventory of the 12 source operating methods, so that an indicator or recap title cannot become an extra product.
2. As a reviewer, I want one source-sequence or source-process verdict per identified observation, so that a later favorable move cannot repair missing prerequisites.
3. As an implementer, I want a complete procedure for every one of the 166 mapped objects, so that I can implement each operation without reopening the PDFs.
4. As an implementer, I want exact native field, unit, ET clock, bar, reset and known_at contracts, so that data adapters cannot silently change the source observation.
5. As a reviewer, I want every Boolean linked to an object procedure and evidence, so that a caller cannot bypass missing source definitions with true.
6. As an implementer, I want correct signed-execution decoding and overlap ownership, so that flow totals do not reverse or double-count the acquired tape.
7. As a reviewer, I want frozen source bands, impulses, profiles and native contract identities, so that a later reference cannot qualify an earlier decision.
8. As an implementer, I want unknown values and named holes for undisclosed source engines, so that I do not invent a substitute gamma, CVD, profile, grade or macro model.
9. As a reviewer, I want separate pass, fail and unknown counts, so that missing definitions and missing data cannot become negative market evidence.
10. As a reviewer, I want separate candidate, touch, order and fill denominators, so that selection and execution assumptions remain visible.
11. As a reviewer, I want all source branches and incomplete cases retained, so that the report cannot certify only the easiest branch while hiding the rest.
12. As an implementer, I want one method command that checks fixtures, processes supported evidence and writes the report, so that finishing helpers alone cannot count as finishing a method.
13. As a reviewer, I want source-specific positive, negative and hole fixtures, so that I can distinguish correct rejection from an implementation defect.
14. As a reviewer, I want late-input, wrong-identity and missing-input mutations, so that timing and identity requirements are checked at the public command.
15. As a reviewer, I want method, predicate, n, rate, interval, year split, status and report path in every headline, so that I can compare the requested observations with their exact scope.
16. As a reviewer, I want the rate denominator and exact missingness interval stated explicitly, so that I cannot mistake compliance for win rate or the interval for a confidence claim.
17. As a reviewer, I want immutable input ownership, source/formula versions and output hashes, so that the same method pass can be reproduced.
18. As a reviewer, I want the acquired data coverage and source holes exposed by branch/year, so that a partial file or missing depth cannot be mistaken for complete evidence.
19. As an implementer, I want freedom to replace conflicting legacy functions and invalidate their caches, so that old behavior cannot override the wiki or source figure.
20. As a reviewer, I want management and fresh re-entry attached to original thesis/position identities, so that a stop-out cannot erase losses or reuse old confirmation.
21. As a reviewer, I want research, auction-state and risk-rule methods audited in their own units, so that they do not turn into invented intraday entry systems.
22. As a reviewer, I want the Refill causal correction and Stoic activation conflict preserved, so that earlier attractive examples do not erase later limitations.
23. As an implementer, I want a method slice that finishes with its report even when status is source_hole, so that correct refusal to invent has an explicit, checkable completion state.
24. As a workspace owner, I want only the four authorized planning documents rewritten in this task, so that the wiki, raw sources, audits and implementation remain intact.

## Implementation Decisions

- Use typed native events, bars, objects, assertions, candidates and hole records, with exact units and immutable identities. Source clocks use date-aware ET; completed bars are known at close.
- Build method-specific input views from named object producers. Evaluate the wiki predicates with three-valued logic and the shared causal/coverage wrapper. An unbound field stays unknown.
- Preserve source-defined versus supplied-contemporaneous versus retrospective-illustration versus synthetic evidence. Synthetic fixtures never enter historical counts. Missing automatic candidate selectors produce an unavailable cohort, not fabricated daily trades.
- Preserve distinct authors, branch permissions, profile settings and event order. Shared primitives do not transfer another author's trigger.
- Implement disclosed algebra and literal state transitions. Ingest a proprietary source value only when supplied with provenance; do not recreate an unpublished engine.
- Reuse or replace adapters, objects and reporting behind the existing runner entry point. Add one method-pass mode that owns the whole vertical operation. A legacy helper or cache that contradicts the contract must be replaced or invalidated.
- Default reporting scope inventories all acquired data relevant to the selected method, then attempts only source-complete discovery or explicitly supplied episodes. Coverage is interval/instrument/branch-specific; no blanket “all data exists” flag.
- Report decidable compliance n=p+f and rate=p/n, plus unknown count u, total N and exact missingness bounds [p/N,(p+u)/N]. Do not label these as trade win rate or sampling confidence. Split by the method observation's ET year.
- Preserve supplied research summaries, cost assumptions and risk arithmetic only as provenance/rule checks. Do not derive a new strategy return series, train a model or run a Monte Carlo study.

## Testing Decisions

Test the public method-pass command and its observable artifacts. Each method is an end-to-end slice: inputs, object values, ordered predicate, fixtures, holes, counts and report. The first slice establishes the runner/report seam; later slices reuse it without reducing the unit to a helper.

Required checks are the printed numeric object fixtures; each method's positive, negative and hole cases; late-dependency and wrong-identity mutations; missing-input propagation; exact source branch selection; and report arithmetic, year reconciliation and artifact existence. Verify the raw signed-flow fixture, clock/DST boundaries, overlapping-file ownership and zero-denominator behavior at the adapter seam. A test passes when a deliberate invalid candidate is rejected with the expected reason.

Existing fixture/quality-report patterns provide prior art for command-level verification, not the expected source truth. Do not preserve a stale test expectation that contradicts the wiki/figure. Do not add tests that merely duplicate implementation branches. This planning task executes no Python or method runner.

## Out of Scope

- Phase 2, strategy optimization, training, new performance/P&L backtests, profitability certification or live/paper order routing.
- Unpublished EV/P-zone/Session Stat minimum-average, gamma/KG1/CVD-reference, range-bar, grade, C-score, cycle or other custom engines. Undefined fields remain explicit holes.
- New operating methods, unmapped legacy wiki pages, unattributed author-rule transfers, new universal thresholds or statistical confidence levels.
- Editing the wiki, raw sources, RULES, chart audits or implementation during this planning task.

## Further Notes

The source of truth is [the wiki index](/workspace/planning/phase-1-live/wiki/index.md) and every method/object page it maps. The implementer consumes [FORMULAS.md](/workspace/planning/phase-1-live/FORMULAS.md) plus [PHASE.md](/workspace/planning/phase-1-live/PHASE.md); [SPEC.md](/workspace/planning/phase-1-live/SPEC.md) preserves one section per method and its complete mapped-object inventory. The four previous documents were replaced, not used as requirements.

This PRD follows the requested [to-prd structure](https://www.skills.sh/mattpocock/skills/to-prd). Implementation slices follow [to-tickets](https://github.com/mattpocock/skills/blob/main/docs/engineering/to-tickets.md); the writing follows [writing-for-agents](https://github.com/mattpocock/skills/blob/main/docs/productivity/writing-for-agents.md). The local [wiki method pack](/workspace/sources/method/agent-method-matt-wiki.md) governs source/wiki handling only; it is not the PRD template. Existing braindumps supply context; no interview or tracker publication is required.
