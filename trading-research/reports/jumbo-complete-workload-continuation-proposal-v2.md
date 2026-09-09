# Jumbo continuation based on the complete measured workload

The [complete registered check](jumbo-check16-complete-resource-review.md) projects **8,670 CPU seconds for fitting**, **5,355 for confirmation**, and **591 MB of confirmation output**. These exceed the approved 6,000/3,600-second phase limits, 512 MiB output cap and remaining cumulative CPU. All sixteen attempts have been used; their **1,473.051801 CPU seconds** and failures remain counted.

Approve a same-family resource amendment with these ceilings:

| Resource | Current | Proposed |
|---|---:|---:|
| Total registered attempts | 16 | 24 |
| Cumulative CPU, including all prior use | 12,000 seconds | 20,000 seconds |
| Full-fit CPU per attempt | 6,000 seconds | 10,000 seconds |
| Confirmation CPU per attempt | 3,600 seconds | 6,500 seconds |
| Aggregate derived output per attempt | 512 MiB | 768 MiB |
| Memory | 4 GiB | 4 GiB |
| Maximum individual output file | 512 MiB | 512 MiB |
| Check / extraction CPU | 90 / 900 seconds | 90 / 900 seconds |

The existing ten-second hard CPU margin is reserved and charged in every attempt. Actual phase and cumulative limits remain binding. The measured fit plus confirmation projection is 14,025 CPU seconds; the proposed remaining cumulative allowance is 18,527 seconds. Both projected stage outputs fit 768 MiB, and projected peak memory is 3.81 GB under 4 GiB.

The concrete sequence is **17: consolidated verification, 18: full fit, 19: frozen confirmation**. Attempts 20–24 are a correction/partition reserve inside the same 20,000-second total. They permit documented recovery without another attempt-only request, not additional hypotheses, model search or a budget reset. New stages still require their relevant verification and resource feasibility.

The prepared [execution plan](../validation/JUMBO_EXECUTION_V11.json) reuses completed annual, source, numerical, reporting and model-storage evidence with exact dependency and input identity. The new check verifies the resource overlay and recomputes feasibility under the approved limits. All 116 targets, model alternatives, original/corrected populations and 1,000 bootstrap replicates remain required. No heldout result has been inspected. Numerical failures retain their explicit fallback status and cannot establish a successful learner.

This proposal supersedes the earlier unapproved seventeen-attempt-only request. It does not include paid data, E0/account/broker/live actions or claim that Context confirmation completes the separate full Location-quality study. Other eligible families continue independently.

Approval is needed because the user's prior amendment explicitly bounded this existing study at sixteen attempts and 12,000 CPU seconds; the [active plan](../../planning/trading-research/PLAN.md) preserves those limits. The prepared envelope alone cannot authorize execution. The [machine-readable proposal](../validation/JUMBO_COMPLETE_WORKLOAD_AMENDMENT_V2_PROPOSED.json) is marked **proposed, not authorized**.
