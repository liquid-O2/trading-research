# P15-01 task report

Disposition: implemented_verified.

The verifier reads TASK_GRAPH.json and file bytes. It does not treat REPORT.md PASS text as evidence.

`verify_research_release.py` supports task, subphase, phase and lineage. Exit 0 only when checks pass. Exit 2 prints a JSON list of objects with code, path and detail.

## Retrospective P15-00

- path `/workspace/implementation/reports/research-work/P15-00/b291864ccceaca9a/attempt-0001/TASK_RECEIPT.json`
- sha256 `a4c5e6bcecdae8af24b69021bf3d9da50f084ee4a2e96c18857e621d69785d20`
- command `/workspace/implementation/.venv/bin/python /workspace/implementation/tools/verify_research_release.py task --receipt /workspace/implementation/reports/research-work/P15-00/b291864ccceaca9a/attempt-0001/TASK_RECEIPT.json`
- exit 0 in 0.389s

## Tests

pytest `/workspace/implementation/tests/rule_discovery/test_p15_01.py` exit 0 in 7.568s.

...............                                                          [100%]
15 passed in 6.03s

## Acceptance

- A01 true. A P15-01 receipt with empty predecessor_receipts fails even when REPORT.md says PASS.
- A02 true. Tampering one copied artifact byte fails. Flipping a required acceptance flag fails. Accepted P15-00 files were only copied, never written.
- A03 true. blocked_implementation cannot take a phase gate of pass or closed_with_limits. Missing software tasks cannot use closed_with_limits because of an input gap.
- A04 true. A phase-2 receipt with phase_1_5_gate=missing fails.
- A05 true. The actual P15-00 bootstrap receipt verifies. Required negatives live in test_p15_01.py and VERIFIER_CASES.json.
- A06 true. Command exit codes, artifact hashes, coverage unknown counts and runtime are recorded on both receipts.

## Identity

- run_id `039267553e8bf721`
- plan_sha256 `61dfe7d2135988cef82c0bb1f94046b0e9c3a7829e794a3d5c8d56ceb4a4a5a1`
- code_sha256 `78980dab561eccdd3880ab925690548a8e37ef76f1d56976d9c254db29d93557`
- predecessor P15-00 `a4c5e6bcecdae8af24b69021bf3d9da50f084ee4a2e96c18857e621d69785d20`

Engineering dates come from P15-00 `ENGINEERING_DATES.json` year_slots and dst_slot. They were not chosen from outcomes.

Native: false. No MBP-1 census.

## Limitations

- The coordinator writes SUBPHASE_RECEIPT.json. This task does not.
- Nested pstack review agents were not spawned.
- Phase 1.5 and Phase 2 are not complete.
- Session prefix holes remain a P15-00 calendar limit.
- P15-00 still records that its verifier was pending at write time. That line is historical.

## Foundation gate inputs

Return these to the coordinator. Do not write SUBPHASE_RECEIPT.json from this worker.

- schema_versions: research-task-receipt-v1, research-subphase-receipt-v1, research-phase-receipt-v1, research-lineage-manifest-v1
- native_slice_ids: ["2020-01-02", "2021-01-04", "2022-01-03", "2023-01-03", "2024-01-02", "2025-01-02", "2026-01-02", "2023-11-06"]
- coverage: native false, declared_dates 1742, complete_eligible_dates 1666, unknown 73
- single_writer: this worker wrote only the P15-01 owned paths and this run directory on `/workspace`
- unresolved: coordinator SUBPHASE_RECEIPT.json, no nested review, no MBP-1 census, phases incomplete
