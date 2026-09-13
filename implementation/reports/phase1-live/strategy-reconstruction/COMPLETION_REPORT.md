# Strategy reconstruction completion report

Current strategy reconstruction: **66 setups, 258 no-setup rejections and 0 unavailable market-input candidates** in the declared evaluation sample. Context and research units are separate.

Personal size, account limits and executed-order records do not gate setups. Auction states, QQQ gamma/key levels, P-zones and macro context have explicit source-inspired implementations. A no-setup rejection is not a losing trade or a software failure.

[Completion report](/workspace/implementation/reports/phase1-live/strategy-reconstruction/COMPLETION_REPORT.md) · [Strategy results](/workspace/implementation/reports/phase1-live/strategy-reconstruction/run-1.1.0-r1/STRATEGY_RESULTS.md) · [Source conformance](/workspace/planning/phase-1-live/STRATEGY_SOURCE_CONFORMANCE.md) · [Charts](/workspace/implementation/reports/phase1-live/strategy-reconstruction/run-1.1.0-r1/charts/README.md).

Validation: 803 passed, 36 subtests passed in 110.74s (0:01:50); 776 completed jobs across all 58 branch/extra units; 77 primary charts visually checked.

## Implemented changes

- Removed personal size/management and daily account-limit clauses from market setup qualification; retained source contracts as a separate audit comparison.
- Added source-inspired auction-state criteria, causal QQQ gamma/flip/wall and mapped key-level models, volume/volatility-conditioned P-zones and initial-release macro context.
- Repaired incomplete prior-value and unobserved-objective false failures; restricted O056 to fields its mathematical signature consumes.
- Used a separately identified inferred holiday calendar, retained real Friday-before-Saturday-New-Year trading, and fixed early-zone clocks and full-band contacts.
- Corrected file-hash caching at filesystem timestamp boundaries and preserved distinct context units when matching shared candidate IDs.

- Reconciled ambiguous candle endpoints with published same-contract OHLCV; evaluated local flow with order-independent batch prices and condition-specific absence proofs.
- Rebuilt prior-month chart context across explicit contract changes and documented empty expiration windows.
- Bound Saint control searches to the actual selected episode and exposed corrected reference selections even in zero-candidate windows.

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

## Resolution of the 51 open cases

All 51 original open entry candidates have an explicit disposition: 6 setups, 44 no-setup rejections and 1 candidate invalidated by reference correction. There are zero unavailable decisions across both fresh replay cohorts. [Case-by-case resolution](/workspace/implementation/reports/phase1-live/strategy-reconstruction/run-1.1.0-r1/validation/RESOLVED_51_CASES.md) and its linked JSON retain every original candidate ID, old and new job hashes, resolved values, stages and changed references.

The 2021 prior-month reference now includes the full acquired December chart and qualifies the short setup. The 2026 partial-range candidate never sweeps the corrected full-month boundary, so it is recorded as invalidated by reference correction rather than silently omitted. No additional private account, order, size or author-label records are required.

Models are explicit interpretations of the sources. Gamma uses a call-positive/put-negative OI assumption on the acquired chain; nearest-expiry fallback is identified when 0DTE is unavailable. The key level, P-zone quantiles, state thresholds and macro composite are our definitions, not recovered proprietary formulas. This is the same bounded annual engineering sample, not an untouched holdout, full-history census, fill simulation or profitability result.

## Validation and preserved evidence

Registry: `b64ffea8a5793620bcdd09960a49ec9619e1c0dd3aa33466b5b08d5f16e92f22`. Software: `aa1e55f8dd6f9178a101359e9abfaee3f350400ac942138449cfbfd03d281c0d`.

[Acceptance](/workspace/implementation/reports/phase1-live/strategy-reconstruction/run-1.1.0-r1/ACCEPTANCE.json); [native model causality and preservation](/workspace/implementation/reports/phase1-live/strategy-reconstruction/run-1.1.0-r1/validation/STRATEGY_MODELS_QA.json); [model diagnostics](/workspace/implementation/reports/phase1-live/strategy-reconstruction/run-1.1.0-r1/diagnostics/models/README.md); [all chart examples](/workspace/implementation/reports/phase1-live/strategy-reconstruction/run-1.1.0-r1/charts/README.md). The 745 protected older artifacts and 104 accepted-r9 report/chart/validation artifacts remain unchanged; earlier attempt job hashes are checked. Earlier source-audit bodies and user edits in live documents are preserved below the new current sections.

The [resume check](/workspace/implementation/reports/phase1-live/strategy-reconstruction/run-1.1.0-r1/validation/resume-verification.json) reran a completed date and preserved all 55 jobs plus its completion receipt. The primary charts use the corrected session endpoint; their consumed-input ledgers identify the strategy conditions used at the decision.

## Reproduction

Use the runtime versions frozen in the selected registry. Run from `/workspace`; keep `/workspace/data` on disk and out of Git. Choose a fresh root under `/workspace/implementation/reports/phase1-live/strategy-reconstruction/` after any implementation change. Resume an unchanged run by repeating its run command.

```bash
python implementation/tools/run_phase1_objects.py historical-replay freeze --strategy \
  --run-root <new-run-root> \
  --scope /workspace/implementation/reports/phase1-live/strategy-reconstruction/SCOPE_POLICY_1_1.json
python implementation/tools/run_phase1_objects.py historical-replay run --run-root <new-run-root> --cohort pilot --workers 4
python implementation/tools/run_phase1_objects.py historical-replay run --run-root <new-run-root> --cohort evaluation --workers 4
python implementation/tools/validate_phase1_native_replay.py --run-root <new-run-root> --part all
python implementation/tools/run_phase1_objects.py historical-replay report --run-root <new-run-root>
python implementation/tools/chart_phase1_native_replay.py --run-root <new-run-root>
cp /workspace/implementation/reports/phase1-live/strategy-reconstruction/run-1.1.0-r1/validation/PRESERVED_R9.json <new-run-root>/validation/PRESERVED_R9.json
PYTHONPATH=implementation/src python implementation/reports/phase1-live/strategy-reconstruction/tools/verify_resolved_cases.py --run-root <new-run-root>
PYTHONPATH=implementation/src python implementation/reports/phase1-live/strategy-reconstruction/tools/verify_strategy_models.py --run-root <new-run-root>
PYTHONPATH=implementation/src python implementation/reports/phase1-live/strategy-reconstruction/tools/render_model_diagnostics.py --run-root <new-run-root>
python implementation/reports/phase1-live/strategy-reconstruction/tools/prepare_chart_review.py --run-root <new-run-root>
# Review every newly rendered chart; record VISUAL_QA.json for that exact manifest.
python implementation/tools/run_phase1_objects.py historical-replay verify --run-root <new-run-root>
```

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
