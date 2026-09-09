# Prepared quote batches: accepted scoped optimization

On 2026-09-08, Cursor Grok 4.6 Extra High Fast implemented quote-column preparation once per bounded source batch. Codex reviewed the complete patch, returned one consolidated repair pass, corrected the repaired index guard, and integrated the four source/test changes with a frozen copy of the prior quote implementation.

The registered auction/flow check passed. This accepts the quote optimization on the measured workload. It does not complete the auction/flow research or establish full-study feasibility.

## Correctness and provenance

- **266 fixture tests passed**, including ordinary/prepared/frozen comparisons for native outputs, original lineage, integer paths, equal timestamps, null categories, invalid inputs, quiet windows and invalidation carry.
- All **nine complete retained-source comparisons** passed, with unchanged original source values, counts, workload counts, complete semantic measurement hashes and continuation states relative to the accepted pre-change result.
- All **three actual split-window comparisons** passed. Each source unit also passed its independent reference and anchor checks.
- Source data, scientific definitions, output formats, prior receipts and resource limits were unchanged. The frozen quote reference has SHA-256 `00ec7c7f8bd39c2b6b8ed39cf21c3a4a7de58f172745c0b9933284dba4ebb101`.

Evidence: [registered execution](auction-flow-runs/4bf61b05d663b4c6c47b7eddc4cc9c473ac2a2dc968f09dba91dce2c54422c70/execution.json), [worker results](auction-flow-runs/4bf61b05d663b4c6c47b7eddc4cc9c473ac2a2dc968f09dba91dce2c54422c70/worker.json), [complete retained-value comparison](auction-flow-runs/4bf61b05d663b4c6c47b7eddc4cc9c473ac2a2dc968f09dba91dce2c54422c70/outputs/retained-source-value-reuse-comparison.json). [Detailed before/after measurements](/workspace/coordination/trading-research-cursor/benchmark.json) preserve every source-unit timing and the integration hashes.

## Measured cost

| Quantity | Check 6 | Check 7 | Interpretation |
|---|---:|---:|---|
| Quote CPU, summed across nine source windows | 19.540 s | 16.735 s | **14.36% lower** |
| Complete source-pipeline CPU for those windows | 113.035 s | 112.029 s | **0.89% lower** |
| Entire registered validation CPU | 670.021 s | 671.562 s | Essentially unchanged; seven fixtures were added |
| Entire registered validation elapsed time | 723.246 s | 727.508 s | Approximately 12 minutes in both cases |
| Peak process RSS | 1,230,491,648 bytes | 1,164,292,096 bytes | No observed memory regression |

Quote CPU decreased in every measured source unit. Busy ordinary sessions improved by about 3–4%, the stressed NQ variants by 10–12%, and the full-session cases by 30–34%. These are two single registered runs, not a statistical estimate of future speed. The overall pipeline benefit is modest.

## Full-study cost remains unresolved

The current empirical maximum-based source projection is **211,217.884 CPU seconds and 447,435,723,012 bytes**, compared with 195,233.047 seconds and 447,435,682,490 bytes previously. Keep the higher current projection. The quote coefficient improved, but other recorded maxima increased, chiefly trade and source-projection timings on the short gap case. This comparison alone does not establish the cause of that variation.

The projection still omits complete downstream anchor/rolling/causal-structure workloads, annual statistics, target matrices, fits, calibration, confirmation and final reporting. Full extraction is not authorized or demonstrated feasible by this check. Seven auction/flow attempts now total **2,148.746980 CPU seconds** within the existing 32-attempt / 192,000-CPU-second family allowance; all earlier failures remain charged. Jumbo's separate exhausted allowance remains unchanged.

## Delegation result

The selected CLI model was verified as `cursor-grok-4.6-xhigh-fast`. Initial implementation took 812.37 seconds and the consolidated worker repair took 104.76 seconds, excluding controller setup/review and the registered validation. The route is operational and resumable; one task does not establish that it is faster overall than the previous working arrangement.

The active supervising task owns acceptance and continuation. [Handoff and operating instructions](/workspace/coordination/trading-research-cursor/HANDOFF.md), the source checkpoint, integration receipt, exact assignment, CLI session ID and logs are retained. The launcher does not provide unattended supervision after the task stops.
