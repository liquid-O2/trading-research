# Trading research implementation

This is the **current implementation**, not a second plan. Read the [durable project entry point](/workspace/planning/trading-research/START_HERE.md) for the complete plan, current evidence, pending work, resource limits and Cursor workflow.

| Folder | Purpose |
|---|---|
| `src/` | Shared data, numerical, measurement, research and model code |
| `tests/` | Focused independent semantic and integration checks |
| `tools/` | Registered study runners and execution support |
| `configs/`, `validation/` | Runtime configuration, frozen study definitions and authorization receipts |
| `references/` | Retained independent reference implementations |
| `reports/`, `evidence/` | Actual run outputs, receipts, source snapshots and immutable evidence |

Use `/tmp/trading-research-venv/bin/python` and the pinned `pyproject.toml`/`uv.lock` environment. Candidate tests, imports, scans, fits and benchmarks must use the applicable registered runner. Do not start a broad verification or raw-data scan just to resume context.

[Current results](/workspace/planning/trading-research/STATUS.md) distinguish verified calculations, actual-data findings and unfinished research. No completed Context or Location evaluation is claimed. Historical root document names are compatibility links to the planning bundle; they do not establish a competing work order.
