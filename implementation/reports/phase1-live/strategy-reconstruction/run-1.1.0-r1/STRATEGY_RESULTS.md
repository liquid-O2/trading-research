# Strategy reconstruction results

The implementation now evaluates market setup conditions without personal sizing, account history or actual orders. It derives auction states, QQQ gamma/key levels, P-zones and a macro composite using the versioned source-inspired models. These models do not claim to recover proprietary formulas.

| Family | Setup | No setup | Market input unavailable | Separate context/process |
| --- | --- | --- | --- | --- |
| JJ-TBR | 16 | 74 | 0 | 0 |
| GB-FAIL | 22 | 62 | 0 | 0 |
| GB-VWAP | 3 | 0 | 0 | 0 |
| GB-SCALP | 12 | 0 | 0 | 0 |
| SIRES | 12 | 84 | 0 | 0 |
| SAINT-AMT | 0 | 26 | 0 | 0 |
| MEMBER-TWO-REASONS | 1 | 6 | 0 | 0 |
| KEANI-OPEN-ABOVE-VALUE | 0 | 6 | 0 | 0 |
| REFILL-STUDY | 0 | 0 | 0 | 0 |
| JETBUNDLE-STATES | 0 | 0 | 0 | 30 |
| STOIC-DATA | 0 | 0 | 0 | 3 |
| STOIC-RISK | 0 | 0 | 0 | 0 |

## Scope and baseline reconciliation

### evaluation

Baseline observations: 325; current observations: 357; baseline IDs no longer selected: 15. Exact IDs and zero-candidate windows are in the JSON report.

| Scope | Classification | n |
| --- | --- | --- |
| entry_setup | setup | 66 |
| entry_setup | no_setup | 258 |
| context_or_research | condition_absent | 29 |
| context_or_research | condition_present | 4 |

| Old verdict | Current scope | Current classification | n |
| --- | --- | --- | --- |
| fail | entry_setup | no_setup | 177 |
| fail | entry_setup | setup | 1 |
| new_observation | context_or_research | condition_present | 3 |
| new_observation | entry_setup | no_setup | 32 |
| new_observation | entry_setup | setup | 12 |
| pass | entry_setup | setup | 33 |
| unknown | context_or_research | condition_absent | 29 |
| unknown | context_or_research | condition_present | 1 |
| unknown | entry_setup | no_setup | 49 |
| unknown | entry_setup | setup | 20 |

### pilot

Baseline observations: 372; current observations: 397; baseline IDs no longer selected: 9. Exact IDs and zero-candidate windows are in the JSON report.

| Scope | Classification | n |
| --- | --- | --- |
| entry_setup | setup | 78 |
| entry_setup | no_setup | 281 |
| context_or_research | condition_absent | 34 |
| context_or_research | condition_present | 4 |

| Old verdict | Current scope | Current classification | n |
| --- | --- | --- | --- |
| fail | entry_setup | no_setup | 213 |
| new_observation | context_or_research | condition_present | 3 |
| new_observation | entry_setup | no_setup | 20 |
| new_observation | entry_setup | setup | 11 |
| pass | entry_setup | setup | 44 |
| unknown | context_or_research | condition_absent | 34 |
| unknown | context_or_research | condition_present | 1 |
| unknown | entry_setup | no_setup | 48 |
| unknown | entry_setup | setup | 23 |

## Interpreting remaining rejections and unknowns

A known violated market condition is **no setup**. Unresolved native event ordering, missing same-contract history, unknown aggressor quantity or unavailable quotes remain **data unavailable**. A missing author label is no longer the sole blocker for an implemented inferred model. These categories are distinct from software failures.

The gamma sign is an explicitly assumed call-positive/put-negative prior-OI model on the acquired QQQ chain. Front-expiry fallback is named whenever 0DTE is unavailable. The key-gamma level is our mapped maximum-gamma node. P-zones use up to 500 prior sessions, historical volume conditioning and volatility-normalized distances. Macro output is our growth-minus-inflation composite. None asserts recovered dealer inventory or a proprietary indicator.

## PHASE lines

| family | variant | n | faithful_disagreements | status | report path |
| --- | --- | --- | --- | --- | --- |
| JJ-TBR | strategy reconstruction v1 | 90 | not claimed | executed; reconstructed setup scope | implementation/reports/phase1-live/strategy-reconstruction/run-1.1.0-r1/strategy-methods/JJ-TBR.md |
| GB-FAIL | strategy reconstruction v1 | 84 | not claimed | executed; reconstructed setup scope | implementation/reports/phase1-live/strategy-reconstruction/run-1.1.0-r1/strategy-methods/GB-FAIL.md |
| GB-VWAP | strategy reconstruction v1 | 3 | not claimed | executed; reconstructed setup scope | implementation/reports/phase1-live/strategy-reconstruction/run-1.1.0-r1/strategy-methods/GB-VWAP.md |
| GB-SCALP | strategy reconstruction v1 | 12 | not claimed | executed; reconstructed setup scope | implementation/reports/phase1-live/strategy-reconstruction/run-1.1.0-r1/strategy-methods/GB-SCALP.md |
| SIRES | strategy reconstruction v1 | 96 | not claimed | executed; reconstructed setup scope | implementation/reports/phase1-live/strategy-reconstruction/run-1.1.0-r1/strategy-methods/SIRES.md |
| SAINT-AMT | strategy reconstruction v1 | 26 | not claimed | executed; reconstructed setup scope | implementation/reports/phase1-live/strategy-reconstruction/run-1.1.0-r1/strategy-methods/SAINT-AMT.md |
| MEMBER-TWO-REASONS | strategy reconstruction v1 | 7 | not claimed | executed; reconstructed setup scope | implementation/reports/phase1-live/strategy-reconstruction/run-1.1.0-r1/strategy-methods/MEMBER-TWO-REASONS.md |
| KEANI-OPEN-ABOVE-VALUE | strategy reconstruction v1 | 6 | not claimed | executed; reconstructed setup scope | implementation/reports/phase1-live/strategy-reconstruction/run-1.1.0-r1/strategy-methods/KEANI-OPEN-ABOVE-VALUE.md |
| REFILL-STUDY | strategy reconstruction v1 | 0 | not claimed | executed; reconstructed setup scope | implementation/reports/phase1-live/strategy-reconstruction/run-1.1.0-r1/strategy-methods/REFILL-STUDY.md |
| JETBUNDLE-STATES | strategy reconstruction v1 | 0 | not claimed | executed; reconstructed setup scope | implementation/reports/phase1-live/strategy-reconstruction/run-1.1.0-r1/strategy-methods/JETBUNDLE-STATES.md |
| STOIC-DATA | strategy reconstruction v1 | 0 | not claimed | executed; reconstructed setup scope | implementation/reports/phase1-live/strategy-reconstruction/run-1.1.0-r1/strategy-methods/STOIC-DATA.md |
| STOIC-RISK | strategy reconstruction v1 | 0 | not claimed | executed; reconstructed setup scope | implementation/reports/phase1-live/strategy-reconstruction/run-1.1.0-r1/strategy-methods/STOIC-RISK.md |

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
