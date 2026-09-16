# P15-17 freeze (stage A)

Attempt `47dedaaa4f5b9ce1`. Nothing in this freeze may change after a later result. Corrected B0.2 run identity and the P15-16A receipt stay `PENDING` until resume.

## Pairing baseline

A candidate is the family's B0.2 scan with exactly one axis replaced by the bank recipe. Same market view, dates, and episode accounting as the B0.2 run. `scan_b02(..., overrides=None)` is byte-identical to `scan_b02(...)` with the argument omitted. B0 and B0.1 rows are reported beside B0.2. They are not the pairing baseline.

## Axis-to-stage map

| Bank | Phase | B0.2 hooks | Enumeration point | Note |
| --- | --- | --- | --- | --- |
| Formation | enumeration | context, reference, location | references | formation part of context/reference; applied at enumeration, may change the contact population |
| Profile | evaluation | reference | - | reference profile construction; applied at stage evaluation on the enumerated contacts |
| Reference | enumeration | reference, location | references | the reference object itself; applied at enumeration, may change the contact population |
| Delta | evaluation | confirmation | - | delta input of confirmation; applied at stage evaluation on the enumerated contacts |
| Sequence | evaluation | trigger, confirmation | - | the sequence machine; applied at stage evaluation on the enumerated contacts |
| Memory | evaluation | location | - | contact-memory filter; applied at stage evaluation on the enumerated contacts |
| Timing | enumeration | trigger, location | window | trigger window and expiry; applied at enumeration, may change the contact population |

Stage order is context, reference, location, trigger, confirmation, risk, objective, management.

Amended 2026-09-16: Formation, Reference and Timing apply before the adapter builds references and
contacts and may change the contact population; Profile, Delta, Sequence and Memory apply at stage
evaluation on the contacts B0.2 has already enumerated. Resolution row ids are unchanged. The freeze
is a draft until resume.

GB-SCALP `bearish_small_scalp` and `bullish_discount_pullback` are observation-only records with no
published reference and no trigger. Their Sequence and Reference candidates are unsupported with a
reason. They stay in the frozen list.

## Bank (RA-3)

| Item | Value |
| --- | --- |
| Path | `implementation/reports/research-work/P15-08/9728f9ee0bbbdfd5/attempt-0001/CANDIDATE_BANK.json` |
| sha256 | `3354f99fb315edebd62e17e6d32c80ea5c1400f6bd996488fbf7084798da54ee` |
| P15-08 receipt sha256 | `bfe62f1cc8e724f87a12fd6fd2e497a3f7ba38999b9799e415b3b7c1f4cb9bbf` |
| Candidates | 160 |
| Deferred | 840 |
| Baselines | 50 |

Used as they are. Nothing added. Nothing dropped.

## Splits (RA-4)

| Artifact | sha256 |
| --- | --- |
| P15-03 `babe7a991b6b3dc1` `SPLIT_MANIFEST.json` | `a30b03bf3ee7bd215ffaf11ff223b07fa0134202d544e4bd0dd353f730e2fde6` |
| `EVALUATION_PROTOCOL.json` | `a22d86bff730bbb1f672cf9af6dfad95c88c310a6c7f639724c25f64573a272b` |

Not regenerated.

## Identities (RA-6)

| Identity | Value |
| --- | --- |
| Census B0 `20def36e065c13d7` MANIFEST | `20def36e065c13d75d738fbce475cf7ea5425255488861c58a1b5fbbbe8b488f` |
| Census SUMMARY | `073f270c5a5f454f4a338219eca9421e43bd3440f4ed42252dfb19f5f4d7838d` |
| B0.1 `dd386316321ee58d` RUN_COMPLETE | `e4dea25d6b8a4910724bcb4f4e8bd3e218383924160153179fedf6643afcd267` |
| B0.1 MANIFEST | `dd386316321ee58d42dc70a612181ed365f727eb0f8d6a82c53a2afbff33164d` |
| Corrected B0.2 run root | PENDING |
| P15-16A receipt | PENDING |

## Scoring and gates

Primary score is mean daily net points on the one-mini benchmark. Ties within 1% take the simpler model, then lower candidate id. At most two mechanism banks per family, chosen on inner tuning only.

Support gate is 100 resolved opportunities on 30 eligible test days in at least three outer blocks. Sensitivity is recorded at half (50 / 15 / 2) and twice (200 / 60 / 6). Below the gate is `inconclusive_support`. Frequency floor is 50% of baseline entries. Holm adjustment covers every candidate at the decision stage.

Block bootstrap seed is 15022026, 2,000 draws, block length 5. Density-matched control offsets are {-2S, -S, +S, +2S}, cycled by SHA256(reference_id) mod 4.

## Throughput (RA-5, round 3)

Twenty R3 dates, single core, one process. **fresh** is the first scan of that (family, branch) on
the session, after the data-plane warm only; **warm repeat** is the second scan of the same candidate
on the same session. The seven RA-5 candidates sit on seven distinct family-branch pairs, so one
session load yields the whole fresh column.

| Candidate | Bank | Phase | fresh median s | fresh p90 s | warm median s | warm p90 s |
| --- | --- | --- | ---: | ---: | ---: | ---: |
| GB-FAIL:nyam_box:F1 | Formation | enumeration | 0.014 | 0.018 | 0.012 | 0.014 |
| KEANI-OPEN-ABOVE-VALUE:source_long:P1 | Profile | evaluation | 17.942 | 24.004 | 0.091 | 0.124 |
| GB-VWAP:source_long:R1 | Reference | enumeration | 0.244 | 2.518 | 0.007 | 0.015 |
| SAINT-AMT:continuation_retest:C1 | Delta | evaluation | 0.032 | 0.085 | 0.022 | 0.053 |
| SIRES:absorption_reward_retest:S1 | Sequence | evaluation | 0.969 | 1.177 | 0.938 | 1.056 |
| MEMBER-TWO-REASONS:planned_return_long:M1 | Memory | evaluation | 2.800 | 3.476 | 0.120 | 0.139 |
| JJ-TBR:judas_reversal:T4 | Timing | enumeration | 0.030 | 0.052 | 0.007 | 0.015 |

Account-day view load: median 5.38 s, p90 8.40 s.
Data-plane warm: median 2.41 s. Branch prepay over
26 distinct (family, branch) pairs: median 17.68 s,
p90 33.68 s. Whole bank (148 supported candidates) after the prepay:
median 46.01 s, p90 86.42 s.
Per session end to end (load + data plane + fresh + prepay + bank): median
92.65 s, p90 156.90 s.
`warm_session` recorded 0 named step failures over the twenty dates
(`THROUGHPUT_B02.json` `warm_failures`); no warm step is silently swallowed.

The per-(family, branch) cold cost is real work, not an accounting artifact. The first B0.2 scan of
`KEANI-OPEN-ABOVE-VALUE:source_long` drives 360 `historical_features.profile` calls whose results
memoize on the market object; the second scan of the same branch costs about 0.06 s. `warm_session`
now prepays it by running each branch's B0.2 scan once per session, so it is paid **once per
family-branch per session** and every candidate on the branch reuses it. It cannot be made to
disappear. The headline projection is therefore the per-session formula, which counts that cost once
per session; the contract formula, which charges a per-candidate p90 to all 160 candidates, is
reported beside it on both columns.

| Projection | 17 workers | 12 workers | > 24 h |
| --- | ---: | ---: | --- |
| **headline** 1,742 x per-session p90 / (workers x 3600) | **4.47 h** | **6.33 h** | no / no |
| 160 x 1,742 x fresh p90 (24.004 s) / (workers x 3600) | 109.32 h | 154.87 h | yes / yes |
| 160 x 1,742 x warm-repeat p90 (1.056 s) / (workers x 3600) | 4.81 h | 6.81 h | no / no |

Budget is 24 h. Bank, dates and coverage are unchanged. Round 1 measured p90 25.246 s and projected
114.98 h on 17 workers because it charged each branch's cold scan to whichever candidate touched the
branch first and then multiplied that by all 160 candidates. Round 1 numbers stay in
`THROUGHPUT_B02_run1.json` and `PROFILE_B02_run1.txt`.

## Recipes bite

Every supported candidate on every measurement date: 2960 rows in
`VERDICT_CHANGES.json` (`rows`), which is the source of truth. `per_bank` in the same file is derived
from those rows by grouping on bank and counting each flag.

| Bank | changed / evaluated | episode verdict | stage verdict | contact population |
| --- | ---: | ---: | ---: | ---: |
| Delta | 129 / 320 | 126 | 129 | 0 |
| Formation | 147 / 500 | 82 | 101 | 113 |
| Memory | 272 / 460 | 175 | 204 | 0 |
| Profile | 18 / 400 | 2 | 18 | 0 |
| Reference | 103 / 120 | 96 | 100 | 99 |
| Sequence | 600 / 880 | 331 | 600 | 0 |
| Timing | 149 / 280 | 121 | 147 | 95 |

Every bank changes at least one verdict. Only the enumeration axes (Formation, Reference, Timing)
change the contact population, which is the point of the amended map.

## Supported / unsupported

`FREEZE.json` `resolutions` pins all 160 bank candidates in the bank's own order. Each row has candidate_id, family, branch, bank, recipe_id, changed_axis, parameters, applicable, supported, hooks, and unsupported_reason (null when supported). Stage B must not re-resolve membership.

148 supported, 12 unsupported. All twelve are on GB-SCALP `bearish_small_scalp` and
`bullish_discount_pullback`: eight Sequence recipes (the observation path emits context and reference
only, so there is no trigger stage) and four Reference recipes (the observation record has no
published reference, so there is no references enumeration point). They stay in the frozen list with
their reasons.
