# P15-17 freeze (stage A)

Attempt `47dedaaa4f5b9ce1`. Nothing in this freeze may change after a later result. Corrected B0.2 run identity and the P15-16A receipt stay `PENDING` until resume.

## Pairing baseline

A candidate is the family's B0.2 scan with exactly one axis replaced by the bank recipe. Same market view, dates, and episode accounting as the B0.2 run. `scan_b02(..., overrides=None)` is byte-identical to `scan_b02(...)` with the argument omitted. B0 and B0.1 rows are reported beside B0.2. They are not the pairing baseline.

## Axis-to-stage map

| Bank | B0.2 hooks | Note |
| --- | --- | --- |
| Formation | context, reference | formation part of context/reference |
| Profile | reference | profile construction |
| Reference | reference | the reference object itself |
| Delta | confirmation | delta input of confirmation |
| Sequence | trigger, confirmation | the sequence machine |
| Memory | location | contact-memory filter |
| Timing | trigger | trigger window and expiry |

Stage order is context, reference, location, trigger, confirmation, risk, objective, management.

GB-SCALP `bearish_small_scalp` and `bullish_discount_pullback` emit only context and reference. Sequence candidates on those branches are unsupported. They stay in the frozen list.

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

## Throughput (RA-5)

Market view loaded once per date. Single core, one process. Twenty R3 dates. Projection uses the slowest measured candidate-branch p90 (Keani P1). The bank, dates, and coverage are not shrunk. The 3x-versus-Phase-1 miss remains the R3 finding (2.71x, p90 1.48 s, residual parquet decode).

| Candidate | median s | p90 s |
| --- | ---: | ---: |
| GB-FAIL:nyam_box:F1 | 0.891 | 2.132 |
| KEANI-OPEN-ABOVE-VALUE:source_long:P1 | 18.411 | 25.246 |
| GB-VWAP:source_long:R1 | 0.271 | 10.252 |
| SAINT-AMT:continuation_retest:C1 | 0.035 | 0.086 |
| SIRES:absorption_reward_retest:S1 | 1.002 | 1.189 |
| MEMBER-TWO-REASONS:planned_return_long:M1 | 2.856 | 3.779 |
| JJ-TBR:judas_reversal:T4 | 0.021 | 0.039 |

Account-day view load median 5.118 s, p90 7.749 s.

| Workers | projected hours | exceeds 24 h |
| ---: | ---: | --- |
| 17 | 114.98 | yes |
| 12 | 162.88 | yes |

## Supported / unsupported

`FREEZE.json` `resolutions` pins all 160 bank candidates in the bank's own order. Each row has candidate_id, family, branch, bank, recipe_id, changed_axis, parameters, applicable, supported, hooks, and unsupported_reason (null when supported). Stage B must not re-resolve membership.

152 supported, 8 unsupported. The eight are GB-SCALP Sequence recipes on `bearish_small_scalp` and `bullish_discount_pullback`. Reason: adapter does not expose stage trigger (observation path emits context and reference only).
