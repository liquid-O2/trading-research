# Restructuring proposal, 2026-09-17

Status: proposal for the owner's approval. Nothing in the task graph, roadmap or overview changes until it is accepted; acceptance is applied through the amendment chain. Written after the [source fidelity audit](/workspace/implementation/reports/research-work/reviews/FIDELITY_AUDIT_2026-09-17.md).

## Why

The audit found that none of the family scanners is the author's strategy: the replay detects 2 of 56 dated examples, every population is one to two orders above the authors' trade counts, and the Sires branches cannot observe the sequences they claim to score. Every Phase 1.5 result (P15-16A, P15-17, P15-18, P15-19) therefore measures our scans, not the authors' rules. The owner's reading of the plan is right: it is convoluted because it ran a candidate search on top of implementations that had never been proven against the sources.

## The four phases, restated in the owner's words

| Phase | Question | Deliverable | Gate |
| --- | --- | --- | --- |
| 1 · Source | What exactly does each author do, and do we reproduce it on their own days? | One scanner per family that produces the author's proper entries as printed (Green Bird: the risk-reward-tool entry; Jumbo: the narrated trade; Sires/Saint/Member: the ticketed fill), the side-by-side chart for every dated example, and the population statistics beside the author's counts | Every inside-tape example replays on entry time and price; entries per session in the author's band; no search, no promotion gates |
| 2 · Context | What is the market doing now, and what does each author read before trading? | The authors' own context reads as baselines (Sires' thesis and gamma regime, Jumbo's classifier, Green Bird's bias, Saint's balance state), then the fitted context experts of the existing Phase 2 pack | An expert is an upgrade only against the author's read; source entries consume context, never the reverse |
| 3 · Levels | Where are the levels each author draws, and how does price react there? | The level objects the audit found missing: profile shelves, ledges, low-volume and minor nodes, delta-print bands, composite nodes, prior balance edges, refill zones calibrated to the paper (175 touches a session, 42% hold), session boxes and projections, KG1 and gamma levels; then the fitted location experts | Each level set is registered from the source first; the Refill anchors reproduce before any touch model is trained |
| 4 · Mix | Given context and levels, which of the authors' entries do we take, and how does it perform as one account? | Entries = context × levels × the authors' confirmation mechanics; the frequency cap (ten a day hard, three or fewer aimed); the combined replay against the daily target | The full-edition and breakdown-edition reports; the hold-out tested once |

## What moves where

- **Kept as is**: the native engine and outcomes (P15-02, P15-03), the receipt and verifier machinery (P15-00, P15-01), the evaluation contract with its amended gates and plausibility cards, the Phase 2 data tasks already in flight (P2-09, P2-10, P2-03), the retention rules (nothing is deleted).
- **Phase 1 now**: the Jumbo and Green Bird rebuilds (dispatched 2026-09-17 on branch `fidelity/jj-gb`), then Sires, Saint, Member and Keani. For the Sires-school families the Phase 1 deliverable is the confirmation mechanics on the author's clock (40-range bars, the four absorption stages, the OFM sequence) proven on the ten tickets with the author's drawn levels taken as given inputs; detecting those levels ourselves is Phase 3 work, so the Phase 1 gate for these families is the mechanics, not the level finder.
- **Parked, retained with attribution `unfaithful_scan`**: the candidate bank and its search (P15-08, P15-17, P15-18), the exit study (P15-19) and the release (P15-20). They re-run in Phase 4 on the faithful entries; their current receipts stay as history.
- **Phase 2 gate**: no method-specific context expert (P2-13) or plan (P2-22) is fitted for a family whose Phase 1 replay has not passed. The strategy-agnostic experts (P2-04, P2-05, P2-07, P2-11, P2-12) proceed on their own inputs.
- **Reporting**: every result card prints entries per session next to the author's count; every release comes in the full edition and the breakdown edition (year, regime, day).

## Immediate sequence

1. Jumbo + Green Bird rebuild delivered with the replay charts; the coordinator checks every chart against the author's image (in progress).
2. B0.2 population re-run for those two families; the counts and the author-count comparison recorded.
3. Sires, Saint, Member, Keani mechanics rebuilt on the same template, with the author-given levels.
4. Amendment: task graph and overview re-labelled per the table above; Phase 1.5's parked tasks marked retained.
5. Phase 2 continues on the faithful entries; Phase 3 level pack written from the audit's level lists.
