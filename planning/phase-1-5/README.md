# Phase 1.5 implementation pack

Status: in execution; subphases 00 to 04 closed, 05 in progress (see [wiki/current-status.md](/workspace/wiki/current-status.md)).

Reconstruct missing numerical rules and compare finite, explicitly attributed setup improvements. All Phase 1.5 work must close before Phase 2 implementation.

Start with the first open subphase: read its task cards and follow [HOW_TO_RUN.md](/workspace/planning/research-program/HOW_TO_RUN.md).

[Specification](/workspace/planning/phase-1-5/SPEC.md) · [Roadmap](/workspace/planning/ROADMAP.md) · [Execution contract](/workspace/planning/research-program/WORKFLOW.md) · [Machine-readable task graph](/workspace/planning/research-program/TASK_GRAPH.json).

## Subphases

| Order | Subphase | Tasks | Exit evidence |
| --- | --- | --- | --- |
| 0 | 00-foundation | P15-00, P15-01 | Verified task receipts + SUBPHASE_RECEIPT.json + passing GATE_REVIEW.json |
| 1 | 01-native-and-outcomes | P15-02, P15-03 | Verified task receipts + SUBPHASE_RECEIPT.json + passing GATE_REVIEW.json |
| 2 | 02-source-reconstruction | P15-04 | Verified task receipts + SUBPHASE_RECEIPT.json + passing GATE_REVIEW.json |
| 3 | 03-primitives | P15-05, P15-06, P15-07, P15-08 | Verified task receipts + SUBPHASE_RECEIPT.json + passing GATE_REVIEW.json |
| 4 | 04-family-adapters | P15-09, P15-10, P15-11, P15-12, P15-13, P15-14, P15-15, P15-16 | Verified task receipts + SUBPHASE_RECEIPT.json + passing GATE_REVIEW.json |
| 5 | 05-finite-search | P15-16A, P15-17, P15-18 | Verified task receipts + SUBPHASE_RECEIPT.json + passing GATE_REVIEW.json |
| 6 | 06-exit-controls | P15-19 | Verified task receipts + SUBPHASE_RECEIPT.json + passing GATE_REVIEW.json |
| 7 | 07-release | P15-20 | Verified task receipts + SUBPHASE_RECEIPT.json + passing GATE_REVIEW.json |

## Operating rules

One owner per subphase with exclusive write ownership; at most one additional implementation worker on separated paths when the user asks; a fresh reviewer at phase closure. Registered defaults, baselines, missing data, ambiguous ordering and unsuccessful trials are preserved as the contracts state. See [HOW_TO_RUN.md](/workspace/planning/research-program/HOW_TO_RUN.md).

## Document maintenance

Task cards and the named contracts are the source of truth. Runbooks and prompt bundles are retired; edit the canonical card and record any change to a pinned plan file in `planning/research-program/AMENDMENTS.json`.
