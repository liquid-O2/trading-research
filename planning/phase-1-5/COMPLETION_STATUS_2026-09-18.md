# Strategy completion status (2026-09-18)

Order of work, set by the user on 2026-09-18: every strategy complete first, then Phase 1.5 upgrades of the strategies (entry side, judged on MAE/MFE with `tools/entry_excursions.py`), then Phase 2. No exit, stop or target upgrades until the user takes exits up; one simple baseline exit exists only so a baseline can be stated.

## What "complete" means here

A strategy is complete when all five hold:

1. Every dated ticket inside the tape is reproduced, or is a documented exception with a reason taken from the source.
2. The reproduction count is reported beside its placebo chance rate (`tools/replay_placebo.py`: the same replay on fake tickets moved in time on the same day and side) and beats it clearly. A count without its chance rate is not evidence.
3. Every structure the author names is generated from the tape by code. No level kind exists only as a drawn fixture in the record, and each level kind admits only the plays the source describes for it.
4. A full-tape population runs, and its per-branch density and pass rates are plausible. A branch that never passes is explained or repaired.
5. The fidelity guard pins it.

## Status

| strategy | 1. tickets | 2. placebo | 3. generated structure | 4. population | 5. pinned | complete |
| --- | --- | --- | --- | --- | --- | --- |
| Green Bird | 19 of 19 inside the tape (4 examples outside it) | not yet run | every named level is built; his charts carry no profile | yes, 1,742 sessions | yes | pending item 2 |
| Jumbo | 26 of 30. Misses: 2026-05-15 12:46 and 12:55 and 2026-05-19 (the May ranges are hand-drawn and their clock is unidentified); 2026-06-05 London (the documented exception) | not yet run | levels built; context reads NOT built: market conditions and the news calendar tiers (TBR pp.22-24), relative strength between indices (p.12), the aggressive entry at the orderblock midpoint (pp.27-28) | yes | yes | NO |
| Sires | 19 of 19 on his drawn levels | drawn levels: real 20 of 20 (with Saint) against 38 of 100 fake tickets, chance rate 0.38; generated levels: running | NOT complete: the aggression and absorption boxes are generated; the OFM line, the squeeze levels, the second-entry box, support and resistance bands, the KG1 level, the wick box, the dealing range, balance and microbalance exist only as drawn fixtures. Every play is tried at every level (about 970 fills a session on his side from his own levels), where the source ties plays to level kinds | yes, but 1,651 candidates a session against his 2 to 6 boxes | yes (drawn) | NO: the largest gap |
| Saint | 1 of 1 on the drawn line; on the generated line the same retest lands 4.25 points and 30 minutes from his | with Sires above | balance and lines generated (composite profile) | first full run in progress; on five sessions `trapped_buyers_retest` passed nothing and two branches barely fire | yes (drawn) | pending item 4 |
| Member | 2 of 2, on the ES tape (his instrument) | not yet run | reaction areas and minor HVNs generated | first full NQ run in progress | yes | pending item 4 |
| Keani | no dated ticket exists in the sources | not applicable | adapter built, trigger repaired 2026-09-17 | first full run in progress | not applicable | plausibility only: completion means item 4 |
| Refill | the paper's definitions are unpublished | not applicable | order-level zones built; touch and hold rules are the study's own | zones measured on three sessions | not applicable | cannot be a reproduction; stated as such |

## Work list, in order

1. **Sires structure (item 3).** Generate each drawn-only level kind from the tape, one at a time, each checked against the tickets that use it: the OFM line and squeeze levels (OFM), the wick box, the second-entry box, support and resistance bands, KG1, then the dealing range, balance and microbalance (the composite-profile machinery built for Saint applies). Then restrict each level kind to the plays its source describes, and re-run the replay and its placebo. Done when the 19 tickets reproduce on generated structure with a chance rate well under the real rate.
2. **Placebo for Jumbo and Green Bird (item 2).** Extend `replay_placebo.py` to `replay_jj_gb.py`.
3. **Saint, Member, Keani populations (item 4).** Read per-branch density and pass rates when the runs land; repair or explain dead branches.
4. **Jumbo's four tickets and three context reads (items 1 and 3).** The context reads are built as recorded reads, not gates.
5. Refill: state the limit in the report; no further work until the definitions exist.
