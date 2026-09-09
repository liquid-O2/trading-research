# Range/open-position probability maps and close labels

Family: **day-type**. Measure faithful objects; experiment with named upgrades in Phase 1.

## Evidence and source rules

[Range Prob.txt, L56–184,199–208,259–318,505–616](../../../sources/documents/indicators/Pinescript-indicators--main.zip) conditions fixed15/30/60/120/240m adjacent ranges on12 open-position buckets. Next close above/below prior range is resolved direction; inside is unresolved. Direction conditional on resolution and overall resolution rate are separate. Hardcoded train/test cells lack dates; display≥70% filtering is not a complete population. [Daily close stats.txt, L254–390](../../../sources/documents/indicators/Pinescript-indicators--main.zip) intends earlier-level filters but counts a new-day first-bar close versus its open/stale08open. [NQ Stats all in one.txt, L578–701](../../../sources/documents/indicators/Pinescript-indicators--main.zip) substitutes later highs/current references in historical filters. [Daily High Low probability zones.txt, L88–185](../../../sources/documents/indicators/Pinescript-indicators--main.zip) is an extreme-location histogram, a distinct outcome. Session/IB maps retain their own tables on related pages.

## Computability and faithful reconstruction

OHLC supports raw range and close categories on long history. Future-informed source lookups cannot enter causal confirmation features.

Emit all bucket cells, including low-rate, equality, inside/unresolved and no-data. Store source hardcoded claims with unknown provenance apart from independently recomputed probabilities. Freeze the conditioning open and previous completed reference.

## Upgrades to measure

These are proposed experiments, not attributed source rules. The user requests stronger objects and independent comparisons. [Develop Trading Model.md, L13–31](../../../sources/documents/conversations/Develop%20Trading%20Model.md)

- **causal prior-range/open map**, **discovery-only pooled/shrunk frequencies**, **fixed-clock-neighbor**, **activity-bar range**, **continuous normalized open position**.
- Recompute actual session close direction rather than relabel a first-bar result. Phase 1 comparisons do not deploy a probability selector.

## Phase 1 outcomes

Unconditional above/below/inside counts, resolved-only direction, resolution rate, calibration of eligible source claims, per-year support and remaining-path separation.

Use [the common measurement contract](measurement-contract.md) for availability, denominators, discovery and confirmation. A source percentage is a claim to recompute. It is never a pass threshold.

## Definition questions

Q01 defines horizon/flat handling. Published lookup validation is unavailable when its fit/test dates overlap or are undisclosed.

## Related

[session geometry](session-geometry.md), [opening range and ib](opening-range-and-ib.md), [distribution envelopes](distribution-envelopes.md), [deferred context location](deferred-context-location.md)

Review findings: ZIP-14, ZIP-15, ZIP-30, ZIP-41, ZIP-47, ZIP-54, ZIP-82. [Review ledger](../REVIEW_LEDGER.md).
