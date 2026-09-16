# Phase 2 implementation pack

Status: **specified, not implemented by this planning task**.

Build intraday forecasts, native options updates and separately fitted context/method experts. Start only after the verified complete Phase 1.5 release.

Start with the first open subphase: read its task cards and follow [HOW_TO_RUN.md](/workspace/planning/research-program/HOW_TO_RUN.md).

[Specification](/workspace/planning/phase-2/SPEC.md) · [Roadmap](/workspace/planning/ROADMAP.md) · [Execution contract](/workspace/planning/research-program/WORKFLOW.md) · [Machine-readable task graph](/workspace/planning/research-program/TASK_GRAPH.json).

## Subphases

| Order | Subphase | Tasks | Exit evidence |
| --- | --- | --- | --- |
| 0 | 00-entry-gate | P2-00 | Verified task receipts + SUBPHASE_RECEIPT.json + passing GATE_REVIEW.json |
| 1 | 01-datasets-and-fitting | P2-01, P2-02 | Verified task receipts + SUBPHASE_RECEIPT.json + passing GATE_REVIEW.json |
| 2 | 02-native-options-baseline | P2-09, P2-10 | Verified task receipts + SUBPHASE_RECEIPT.json + passing GATE_REVIEW.json |
| 3 | 03-joint-volatility | P2-03, P2-04 | Verified task receipts + SUBPHASE_RECEIPT.json + passing GATE_REVIEW.json |
| 4 | 04-context-mechanisms | P2-05, P2-06, P2-07, P2-11, P2-08 | Verified task receipts + SUBPHASE_RECEIPT.json + passing GATE_REVIEW.json |
| 5 | 05-intraday-oi | P2-12 | Verified task receipts + SUBPHASE_RECEIPT.json + passing GATE_REVIEW.json |
| 6 | 06-method-experts | P2-13, P2-14, P2-15, P2-16, P2-17, P2-18, P2-19, P2-20, P2-21 | Verified task receipts + SUBPHASE_RECEIPT.json + passing GATE_REVIEW.json |
| 7 | 07-plans-and-adaptation | P2-22, P2-23 | Verified task receipts + SUBPHASE_RECEIPT.json + passing GATE_REVIEW.json |
| 8 | 08-release | P2-24 | Verified task receipts + SUBPHASE_RECEIPT.json + passing GATE_REVIEW.json |

## Operating rules

One owner per subphase with exclusive write ownership; at most one additional implementation worker on separated paths when the user asks; a fresh reviewer at phase closure. Registered defaults, baselines, missing data, ambiguous ordering and unsuccessful trials are preserved as the contracts state. See [HOW_TO_RUN.md](/workspace/planning/research-program/HOW_TO_RUN.md).

## Document maintenance

Task cards and the named contracts are the source of truth. Runbooks and prompt bundles are retired; edit the canonical card and record any change to a pinned plan file in `planning/research-program/AMENDMENTS.json`.
