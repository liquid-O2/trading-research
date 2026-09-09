# Continuous, multiscale sister-market nonconfirmation

Family: **CVD-SMT**. Measure faithful objects; experiment with named upgrades in Phase 1.

## Evidence and source rules

[Open Source Fractal - Customized.txt, L144–182,1200–1521](../../../sources/documents/indicators/Open%20Source%20Fractal%20-%20Customized.txt) matches3/3 confirmed pivots within one bar across chart/pair, looks back200, compares breaks of matched extrema and requires mismatch. It uses the chart’s mintick for both markets, minimum2tick score, overlap2 ticks,12bar merge,150event cap and optional invalidation. NQ/ES and optionalYM are sourced pairs. [code-1-thesis.pdf, pp.5–7](../../../sources/documents/discretionary/code-1-thesis.pdf#page=5) adds leader/laggard and fresh-extreme nonconfirmation. The user requires trade-level NQ and OHLC across3–4assets, multiple scales, continuously. [conversation_export (1).md, Turns1–4](../../../sources/documents/conversations/conversation_export%20%281%29.md).

## Computability and faithful reconstruction

NQ/ES/YM/RTY OHLC and trades have different starts. NQ tick-event SMT needs a precisely defined comparator stream. No common sample intersection is required across all families.

Preserve the exact Pine pivot matcher as benchmark, including code-score unit errors in disagreement diagnostics. A sister pivot is not known before its own confirmation. Store every invalidated event. “SMT” remains a hypothesis, not an observed causal mechanism.

## Upgrades to measure

These are proposed experiments, not attributed source rules. The user requests stronger objects and independent comparisons. [Develop Trading Model.md, L13–31](../../../sources/documents/conversations/Develop%20Trading%20Model.md)

- **native-tick / return-volatility normalized score**, **continuous-extreme window**, **explicit asynchronous pair lag**, **3–4-asset breadth**.
- **1/5/15/60m plus confirmed HTF scales**, **NQ trade-clock triggers**, **volume/dollar-bar windows**, **append-only event lifecycle**. Proposed scale grid freezes in discovery; no09:30-only snapshot.

## Phase 1 outcomes

Availability/pair coverage, mismatch count/duration, source/upgrade disagreements, lag, later NQ rail/zone reaction and path, stability across years and session classes.

Use [the common measurement contract](measurement-contract.md) for availability, denominators, discovery and confirmation. A source percentage is a claim to recompute. It is never a pass threshold.

## Definition questions

Q21 defines trade-level SMT comparator, synchronization tolerance and exact asset/scales when not fixed by source. Do not equate CVD divergence with cross-asset SMT.

## Related

[cvd divergence](cvd-divergence.md), [cross asset object arrivals](cross-asset-object-arrivals.md), [jumbo day classes](jumbo-day-classes.md)

Review findings: USER-05, PINE-FRACTAL-03, D-SMT-01. [Review ledger](../REVIEW_LEDGER.md).
