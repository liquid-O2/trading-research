# Volume value areas and profile shapes

Family: **auction-order-flow**. Measure faithful objects; experiment with named upgrades in Phase 1.

## Evidence and source rules

[amt-lesson-1.pdf, pp.3–6,12–14](../../../sources/documents/discretionary/amt-lesson-1.pdf#page=3) defines POC as maximum-volume price, 70% value area, D/P/b/B geometries and developing value. [code-3-orderflow.pdf, p.7](../../../sources/documents/discretionary/code-3-orderflow.pdf#page=7) explicitly uses 40%; [reading-the-volume-profile.pdf, pp.4–11](../../../sources/documents/discretionary/reading-the-volume-profile.pdf#page=4) uses 68%. B means double distribution in one source and lower-heavy in another; preserve geometry rather than infer direction. [mastering-amt-vp.pdf, pp.3–8](../../../sources/documents/discretionary/mastering-amt-vp.pdf#page=3) also has conflicting shape wording/illustration. [xfcmg2.pdf, pp.14–16; post 2077828415923581206](../../../sources/documents/jumbo/xfcmg2.pdf#page=14) explicitly identifies RTH VP and delta profile.

[Sessions & VP with prev session VP & daily weekly opens.txt, L216–289](../../../sources/documents/indicators/Pinescript-indicators--main.zip) and [VP History Widget.txt, L60–130,148–222](../../../sources/documents/indicators/Pinescript-indicators--main.zip) synthesize bar volume using body/double-wick weighting, split wick volume equally, and alternate VA expansion regardless of adjacent volume. They have bottom-bin POC and boundary bugs. Daily ΔOI distributed intrabar is not actual traded volume or participant position.

## Computability and faithful reconstruction

MBP-1 executions and tape support true volume-at-price. Minute synthetic VP has longer but approximate coverage. RTH, overnight, current balance, day/week/month/year composites retain their own anchors.

Build explicit profile price bins, volume rows, POC ties, 40/68/70% area variants and immutable completed snapshots. Retain source synthetic construction as its own benchmark. Keep developing versions causal. A volume profile need not be normally distributed; value fraction is not a Gaussian claim.

## Upgrades to measure

These are proposed experiments, not attributed source rules. The user requests stronger objects and independent comparisons. [Develop Trading Model.md, L13–31](../../../sources/documents/conversations/Develop%20Trading%20Model.md)

- **trade-at-price/tick-bins**, **highest-adjacent-volume-VA**, **POC-tie variants**, **fixed versus adaptive bin width**.
- **RTH-only / overnight / rolling composite**, **volume-bar snapshots**, **robust shape descriptors** (skew, concentration, number of modes), **density-matched node sets**.
- Compare 40/68/70% on the same outcomes; do not choose from confirmation results and then claim fresh validation.

## Phase 1 outcomes

VA edge/POC touch, dwell, reject, acceptance, traverse, migration, open-relative-to-prior-value and year stability. Include shape-unclassified snapshots and density/width/support so smaller areas do not win merely by changing event counts.

Use [the common measurement contract](measurement-contract.md) for availability, denominators, discovery and confirmation. A source percentage is a claim to recompute. It is never a pass threshold.

## Definition questions

Q08 fixes exact faithful VA expansion/tie/bin rules and profile anchors where unspecified. Proposed algorithms remain named variants.

## Related

[nodes shelves ledges](nodes-shelves-ledges.md), [auction acceptance and failure](auction-acceptance-and-failure.md), [delta profiles](delta-profiles.md), [tpo structures](tpo-structures.md)

Review findings: D-AMT-01, D-AMT-04, D-AMT-06, D-VP-03, D-VP-04, J-X-05, ZIP-66, ZIP-77. [Review ledger](../REVIEW_LEDGER.md).
