# Strategy reconstruction work order — 2026-09-13

The user clarified that the objective is to reconstruct executable strategy logic from the source documents, infer the required state/context inputs, and validate the implementation against those sources. Personal sizing, daily account limits, historical order logs and the authors' actual management records are not setup-qualification requirements.

This supersedes the supplied-record restrictions in the earlier implementation handoff for this work. The accepted v2 run remains a preserved comparison, not the completion criterion for strategy reconstruction.

## Delivered

1. Separate setup qualification from personal execution/process auditing. Keep structural invalidation and source entry sequencing where they define the setup. Report qualified setup, no setup, and unavailable market input separately from software failures.
2. Compute the disclosed qualitative conditions from market data. Add explicit, versioned operational definitions for auction states and for the model-dependent context/levels needed by the strategies. Identify inferred choices and source citations in each derivation.
3. Repair false failures caused by missing prior profiles or uncomputed entry geometry. Investigate unnecessary unknown propagation at candle and local-flow boundaries, while retaining true uncertainty when native evidence cannot decide a consumed condition.
4. Validate source logic with positive, negative, and causal boundary examples. Freeze the revised implementation before replaying the same pilot/evaluation dates. Preserve prior artifacts and show changes in scope and classifications explicitly.
5. Update current reports and live documentation with the actual implemented strategy coverage, validation, unresolved data requirements, and both required family tables.

## Interpretation rules

- A missing account, historical quantity, or executed order does not disqualify a market setup.
- An inferred implementation is allowed and must be documented. An undisclosed author formula is not claimed to have been recovered exactly.
- A correctly rejected candidate remains no setup. Thresholds are not optimized to make the existing sample pass.
- Auction-state classification and macro research are context/research outputs, not standalone entry signals. Risk compounding and order-lifecycle audits are outside the current setup denominator.
- Historical event ordering, source timestamps, and future availability remain causal constraints. Inference cannot create missing historical observations.

## Baseline

Accepted v2 evaluation: 325 branch/process observations, 34 pass, 183 fail, 108 unknown. This mixed denominator includes 35 Jetbundle state checks, 12 scalp records requiring size/management, and two custom-macro checks. The new report must reconcile the baseline rather than silently comparing changed denominators.

Initial defect audit identified missing prior-value coverage encoded as `prior_value_fixed=False` in Keani and an unavailable response/target encoded as `objective_fixed=False` in the two-reasons method. Both require correction and regression coverage.

Source review also confirms that O056's mathematical signature consumes C1/C2 extrema and C3 close, while the historical caller currently requires every O/H/L/C endpoint of all three candles. This needs a field-specific knowledge check, with a clear distinction between a complete observation window and an unneeded ambiguous endpoint.

Read-only recovery of historical CME schedule archives was attempted again. The exchange's localized calendar links reveal dated XLS/ZIP archives, but direct retrieval timed out. The reconstructed strategy uses a separately identified inferred calendar with recorded-market checks; the earlier source-evidence calendar is preserved.


## Reopened evidence resolution — 2026-09-13

The user explicitly rejected treating 51 undecided candidates as completed work. The r3 engineering run is retained as a diagnostic baseline, without publishing it as the completed reconstruction. Trace every open candidate to raw or complementary owned data, repair unnecessary unknown propagation, and verify actual resolved conditions. Initial cross-checks show that stored same-contract OHLCV supplies tied candle endpoints with matching H/L/volume; local-flow absence currently depends on unrelated endpoint ambiguity. These require implementation fixes, not a missing-data conclusion.


## Accepted reconstruction release

Current strategy reconstruction: **66 setups, 258 no-setup rejections and 0 unavailable market-input candidates** in the declared evaluation sample. Context and research units are separate.

[Completion report](/workspace/implementation/reports/phase1-live/strategy-reconstruction/COMPLETION_REPORT.md). All 58 branch/extra units were replayed; personal execution units and context outputs are separate from setup qualification.
