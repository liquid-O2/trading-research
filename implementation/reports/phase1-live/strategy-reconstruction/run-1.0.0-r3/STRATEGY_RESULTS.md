# Strategy reconstruction results

The implementation now evaluates market setup conditions without personal sizing, account history or actual orders. It derives auction states, QQQ gamma/key levels, P-zones and a macro composite using the versioned source-inspired models. These models do not claim to recover proprietary formulas.

| Family | Setup | No setup | Market input unavailable | Separate context/process |
| --- | --- | --- | --- | --- |
| JJ-TBR | 14 | 67 | 8 | 0 |
| GB-FAIL | 18 | 54 | 10 | 0 |
| GB-VWAP | 2 | 0 | 1 | 0 |
| GB-SCALP | 12 | 0 | 0 | 0 |
| SIRES | 11 | 67 | 15 | 0 |
| SAINT-AMT | 0 | 18 | 8 | 0 |
| MEMBER-TWO-REASONS | 1 | 0 | 6 | 0 |
| KEANI-OPEN-ABOVE-VALUE | 0 | 3 | 3 | 0 |
| REFILL-STUDY | 0 | 0 | 0 | 0 |
| JETBUNDLE-STATES | 0 | 0 | 0 | 35 |
| STOIC-DATA | 0 | 0 | 0 | 3 |
| STOIC-RISK | 0 | 0 | 0 | 0 |

## Scope and baseline reconciliation

### evaluation

Baseline observations: 325; current observations: 356; baseline IDs no longer selected: 3. Exact IDs and zero-candidate windows are in the JSON report.

| Scope | Classification | n |
| --- | --- | --- |
| entry_setup | setup | 58 |
| entry_setup | data_unavailable | 51 |
| entry_setup | no_setup | 209 |
| context_or_research | condition_absent | 29 |
| context_or_research | data_unavailable | 5 |
| context_or_research | condition_present | 4 |

| Old verdict | Current scope | Current classification | n |
| --- | --- | --- | --- |
| fail | entry_setup | data_unavailable | 5 |
| fail | entry_setup | no_setup | 178 |
| new_observation | context_or_research | condition_present | 3 |
| new_observation | entry_setup | data_unavailable | 5 |
| new_observation | entry_setup | no_setup | 16 |
| new_observation | entry_setup | setup | 10 |
| pass | entry_setup | setup | 33 |
| unknown | context_or_research | condition_absent | 29 |
| unknown | context_or_research | condition_present | 1 |
| unknown | context_or_research | data_unavailable | 5 |
| unknown | entry_setup | data_unavailable | 41 |
| unknown | entry_setup | no_setup | 15 |
| unknown | entry_setup | setup | 15 |

### pilot

Baseline observations: 372; current observations: 396; baseline IDs no longer selected: 3. Exact IDs and zero-candidate windows are in the JSON report.

| Scope | Classification | n |
| --- | --- | --- |
| entry_setup | setup | 68 |
| entry_setup | data_unavailable | 51 |
| entry_setup | no_setup | 239 |
| context_or_research | condition_absent | 34 |
| context_or_research | condition_present | 4 |

| Old verdict | Current scope | Current classification | n |
| --- | --- | --- | --- |
| fail | entry_setup | data_unavailable | 4 |
| fail | entry_setup | no_setup | 215 |
| new_observation | context_or_research | condition_present | 3 |
| new_observation | entry_setup | data_unavailable | 2 |
| new_observation | entry_setup | no_setup | 13 |
| new_observation | entry_setup | setup | 9 |
| pass | entry_setup | setup | 44 |
| unknown | context_or_research | condition_absent | 34 |
| unknown | context_or_research | condition_present | 1 |
| unknown | entry_setup | data_unavailable | 45 |
| unknown | entry_setup | no_setup | 11 |
| unknown | entry_setup | setup | 15 |

## Interpreting remaining rejections and unknowns

A known violated market condition is **no setup**. Unresolved native event ordering, missing same-contract history, unknown aggressor quantity or unavailable quotes remain **data unavailable**. A missing author label is no longer the sole blocker for an implemented inferred model. These categories are distinct from software failures.

The gamma sign is an explicitly assumed call-positive/put-negative prior-OI model on the acquired QQQ chain. Front-expiry fallback is named whenever 0DTE is unavailable. The key-gamma level is our mapped maximum-gamma node. P-zones use up to 500 prior sessions, historical volume conditioning and volatility-normalized distances. Macro output is our growth-minus-inflation composite. None asserts recovered dealer inventory or a proprietary indicator.

## PHASE lines

| family | variant | n | faithful_disagreements | status | report path |
| --- | --- | --- | --- | --- | --- |
| JJ-TBR | strategy reconstruction v1 | 81 | not claimed | executed; reconstructed setup scope | implementation/reports/phase1-live/strategy-reconstruction/run-1.0.0-r3/strategy-methods/JJ-TBR.md |
| GB-FAIL | strategy reconstruction v1 | 72 | not claimed | executed; reconstructed setup scope | implementation/reports/phase1-live/strategy-reconstruction/run-1.0.0-r3/strategy-methods/GB-FAIL.md |
| GB-VWAP | strategy reconstruction v1 | 2 | not claimed | executed; reconstructed setup scope | implementation/reports/phase1-live/strategy-reconstruction/run-1.0.0-r3/strategy-methods/GB-VWAP.md |
| GB-SCALP | strategy reconstruction v1 | 12 | not claimed | executed; reconstructed setup scope | implementation/reports/phase1-live/strategy-reconstruction/run-1.0.0-r3/strategy-methods/GB-SCALP.md |
| SIRES | strategy reconstruction v1 | 78 | not claimed | executed; reconstructed setup scope | implementation/reports/phase1-live/strategy-reconstruction/run-1.0.0-r3/strategy-methods/SIRES.md |
| SAINT-AMT | strategy reconstruction v1 | 18 | not claimed | executed; reconstructed setup scope | implementation/reports/phase1-live/strategy-reconstruction/run-1.0.0-r3/strategy-methods/SAINT-AMT.md |
| MEMBER-TWO-REASONS | strategy reconstruction v1 | 1 | not claimed | executed; reconstructed setup scope | implementation/reports/phase1-live/strategy-reconstruction/run-1.0.0-r3/strategy-methods/MEMBER-TWO-REASONS.md |
| KEANI-OPEN-ABOVE-VALUE | strategy reconstruction v1 | 3 | not claimed | executed; reconstructed setup scope | implementation/reports/phase1-live/strategy-reconstruction/run-1.0.0-r3/strategy-methods/KEANI-OPEN-ABOVE-VALUE.md |
| REFILL-STUDY | strategy reconstruction v1 | 0 | not claimed | executed; reconstructed setup scope | implementation/reports/phase1-live/strategy-reconstruction/run-1.0.0-r3/strategy-methods/REFILL-STUDY.md |
| JETBUNDLE-STATES | strategy reconstruction v1 | 0 | not claimed | executed; reconstructed setup scope | implementation/reports/phase1-live/strategy-reconstruction/run-1.0.0-r3/strategy-methods/JETBUNDLE-STATES.md |
| STOIC-DATA | strategy reconstruction v1 | 0 | not claimed | executed; reconstructed setup scope | implementation/reports/phase1-live/strategy-reconstruction/run-1.0.0-r3/strategy-methods/STOIC-DATA.md |
| STOIC-RISK | strategy reconstruction v1 | 0 | not claimed | executed; reconstructed setup scope | implementation/reports/phase1-live/strategy-reconstruction/run-1.0.0-r3/strategy-methods/STOIC-RISK.md |

## Audit lines

| family | id | verdict | fixture | leakage | proxy-as-faithful | notes |
| --- | --- | --- | --- | --- | --- | --- |
| JJ-TBR | M01 | source logic + replay checked | pass | 0 | 0 | inferred models identified; private execution excluded; no profit claim |
| GB-FAIL | M02 | source logic + replay checked | pass | 0 | 0 | inferred models identified; private execution excluded; no profit claim |
| GB-VWAP | M03 | source logic + replay checked | pass | 0 | 0 | inferred models identified; private execution excluded; no profit claim |
| GB-SCALP | M04 | source logic + replay checked | pass | 0 | 0 | inferred models identified; private execution excluded; no profit claim |
| SIRES | M05 | source logic + replay checked | pass | 0 | 0 | inferred models identified; private execution excluded; no profit claim |
| SAINT-AMT | M06 | source logic + replay checked | pass | 0 | 0 | inferred models identified; private execution excluded; no profit claim |
| MEMBER-TWO-REASONS | M07 | source logic + replay checked | pass | 0 | 0 | inferred models identified; private execution excluded; no profit claim |
| KEANI-OPEN-ABOVE-VALUE | M08 | source logic + replay checked | pass | 0 | 0 | inferred models identified; private execution excluded; no profit claim |
| REFILL-STUDY | M09 | source logic + replay checked | pass | 0 | 0 | inferred models identified; private execution excluded; no profit claim |
| JETBUNDLE-STATES | M10 | source logic + replay checked | pass | 0 | 0 | inferred models identified; private execution excluded; no profit claim |
| STOIC-DATA | M11 | source logic + replay checked | pass | 0 | 0 | inferred models identified; private execution excluded; no profit claim |
| STOIC-RISK | M12 | source logic + replay checked | pass | 0 | 0 | inferred models identified; private execution excluded; no profit claim |
