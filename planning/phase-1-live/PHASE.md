# Phase 1 — full acquired historical measurement

Phase 1 setup implementation and the acquired observed-input census are complete. The unchanged versioned scanners searched **1,742 declared session dates**, 2020-01-01 through 2026-09-03, across all 50 branches and eight additional observation units. The composed census contains **99,294 daily jobs** and **18,747 qualifying market setups**, plus three actual collection-process jobs. The independent primary run and all 90 calendar-recovery dates completed and were verified.

**The acquired observed-input census is executed. Input-limited populations remain unmeasured beyond the observed subset; the exact affected branch/session denominators are listed below.** Qualification does not establish a winning trade. All reported outcomes are subsequent observed prices; no return simulation or actual fill is claimed. Phase 2 remains the additional context layer that selects which setups to use.

[Current measurement report](/workspace/implementation/reports/phase1-live/historical-measurement/MEASUREMENT_REPORT.md) · [Charts](/workspace/implementation/reports/phase1-live/historical-measurement/run-1.0.1/charts/README.md)

| family | variant | n | faithful_disagreements | status | report path |
| --- | --- | --- | --- | --- | --- |
| JJ-TBR | full acquired historical measurement | 3912 | not claimed | all sessions searched; input-limited scope explicit | implementation/reports/phase1-live/historical-measurement/run-1.0.1/methods/JJ-TBR.md |
| GB-FAIL | full acquired historical measurement | 7589 | not claimed | all sessions searched; input-limited scope explicit | implementation/reports/phase1-live/historical-measurement/run-1.0.1/methods/GB-FAIL.md |
| GB-VWAP | full acquired historical measurement | 499 | not claimed | all sessions searched; input-limited scope explicit | implementation/reports/phase1-live/historical-measurement/run-1.0.1/methods/GB-VWAP.md |
| GB-SCALP | full acquired historical measurement | 3066 | not claimed | all sessions searched; input-limited scope explicit | implementation/reports/phase1-live/historical-measurement/run-1.0.1/methods/GB-SCALP.md |
| SIRES | full acquired historical measurement | 2538 | not claimed | all sessions searched; input-limited scope explicit | implementation/reports/phase1-live/historical-measurement/run-1.0.1/methods/SIRES.md |
| SAINT-AMT | full acquired historical measurement | 785 | not claimed | all sessions searched; input-limited scope explicit | implementation/reports/phase1-live/historical-measurement/run-1.0.1/methods/SAINT-AMT.md |
| MEMBER-TWO-REASONS | full acquired historical measurement | 352 | not claimed | all sessions searched; input-limited scope explicit | implementation/reports/phase1-live/historical-measurement/run-1.0.1/methods/MEMBER-TWO-REASONS.md |
| KEANI-OPEN-ABOVE-VALUE | full acquired historical measurement | 6 | not claimed | all sessions searched; input-limited scope explicit | implementation/reports/phase1-live/historical-measurement/run-1.0.1/methods/KEANI-OPEN-ABOVE-VALUE.md |
| REFILL-STUDY | full acquired historical measurement | 0 | not claimed | all sessions searched; input-limited scope explicit | implementation/reports/phase1-live/historical-measurement/run-1.0.1/methods/REFILL-STUDY.md |
| JETBUNDLE-STATES | full acquired historical measurement | 0 | not claimed | all sessions searched; input-limited scope explicit | implementation/reports/phase1-live/historical-measurement/run-1.0.1/methods/JETBUNDLE-STATES.md |
| STOIC-DATA | full acquired historical measurement | 0 | not claimed | all sessions searched; input-limited scope explicit | implementation/reports/phase1-live/historical-measurement/run-1.0.1/methods/STOIC-DATA.md |
| STOIC-RISK | full acquired historical measurement | 0 | not claimed | all sessions searched; input-limited scope explicit | implementation/reports/phase1-live/historical-measurement/run-1.0.1/methods/STOIC-RISK.md |

| family | id | verdict | fixture | leakage | proxy-as-faithful | notes |
| --- | --- | --- | --- | --- | --- | --- |
| JJ-TBR | M01 | measured observed setup population | pass: full suite and native controls | 0 | 0 | fixed rules; exact limitations retained; outcomes are prices, not fills |
| GB-FAIL | M02 | measured observed setup population | pass: full suite and native controls | 0 | 0 | fixed rules; exact limitations retained; outcomes are prices, not fills |
| GB-VWAP | M03 | measured observed setup population | pass: full suite and native controls | 0 | 0 | fixed rules; exact limitations retained; outcomes are prices, not fills |
| GB-SCALP | M04 | measured observed setup population | pass: full suite and native controls | 0 | 0 | fixed rules; exact limitations retained; outcomes are prices, not fills |
| SIRES | M05 | measured observed setup population | pass: full suite and native controls | 0 | 0 | fixed rules; exact limitations retained; outcomes are prices, not fills |
| SAINT-AMT | M06 | measured observed setup population | pass: full suite and native controls | 0 | 0 | fixed rules; exact limitations retained; outcomes are prices, not fills |
| MEMBER-TWO-REASONS | M07 | measured observed setup population | pass: full suite and native controls | 0 | 0 | fixed rules; exact limitations retained; outcomes are prices, not fills |
| KEANI-OPEN-ABOVE-VALUE | M08 | measured observed setup population | pass: full suite and native controls | 0 | 0 | fixed rules; exact limitations retained; outcomes are prices, not fills |
| REFILL-STUDY | M09 | non-entry scope retained; setup denominator not applicable | pass: full suite and native controls | 0 | 0 | fixed rules; exact limitations retained; outcomes are prices, not fills |
| JETBUNDLE-STATES | M10 | non-entry scope retained; setup denominator not applicable | pass: full suite and native controls | 0 | 0 | fixed rules; exact limitations retained; outcomes are prices, not fills |
| STOIC-DATA | M11 | non-entry scope retained; setup denominator not applicable | pass: full suite and native controls | 0 | 0 | fixed rules; exact limitations retained; outcomes are prices, not fills |
| STOIC-RISK | M12 | non-entry scope retained; setup denominator not applicable | pass: full suite and native controls | 0 | 0 | fixed rules; exact limitations retained; outcomes are prices, not fills |


## Next work and historical evidence

[Program roadmap](/workspace/planning/ROADMAP.md) · [Shared wiki](/workspace/wiki/index.md) · [Phase 1.5 pack](/workspace/planning/phase-1-5/README.md) · [Phase 2 pack](/workspace/planning/phase-2/README.md). Phase 1.5 must close before Phase 2 implementation.

Earlier bounded implementation, source-audit and reconstruction reports remain versioned under `implementation/reports/phase1-live`. They describe their own releases. The full acquired measurement report above governs current Phase 1 completion; its input limitations remain in force. The next-phase packs are plans, not completed research.
