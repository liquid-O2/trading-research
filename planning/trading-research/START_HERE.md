# User stop — September 9, 2026, 07:14 UTC

**The user requested: “just stop everything please.” All research runs and Cursor workers are stopped. Do not resume without a new user instruction. Saved work and incomplete status are preserved in state/CURRENT.json.** The prior continuation instructions below are suspended.

# Trading research — start here

**Active task (user direction September 8, 20:41 UTC): complete Deliverable 1 across all intended families—definitions, measurement validation, statistics, timing and window links—then Context.** Source performance repair is accepted. Reuse the complete 3,589-window receipt catalog; do not rerun source extraction. Current work builds complete-population auction/flow observation tables and enables the separately scoped Jumbo descriptive confirmation. The family table below remains the full validation queue. Context and Location evaluation remain later.


This is the durable entry point for the whole project. The canonical plan is **`/workspace/planning/trading-research`**. The current implementation is **`/workspace/trading-research`**. Cursor coordination is **`/workspace/coordination/trading-research-cursor`**. Do not start another project or reconstruct the plan from old task messages.

Workspace consolidation and instruction review are complete. Apply [workspace rules](/workspace/AGENTS.md). **Source timestamp repair is complete and verified.** Run 36 succeeded for **all 3,589 source/date windows across 167 physical files**, with **zero failed or pending windows**. It reused 3,550 windows and completed the final 39 in **9.16 minutes**. All original timestamps, source fields and rows remain unchanged. Four short timing-uncertainty spans are explicit and excluded from exact duration claims; physical state and later carry continue. Verification ran 154 tests: 152 passed, zero failures/errors and two pre-existing optional-backend skips. All 167 carry chains reconcile. The complete receipt catalog is linked in the [verified result](/workspace/trading-research/reports/auction-flow-reset-clock-repair36-review.md). There are no active workers. The family has used **36/36 authorized attempts, 71,701.255619/192,000 CPU-seconds and 55,928,815,964 bytes of 256 GiB**. Earlier failures, budgets and the exceeded 20:11 cutoff remain recorded. Complete scientific research and full-pipeline three-hour timing are not claimed.

## Read once, then execute the relevant work

1. This file establishes authority, current state and working rules.
   Read the full plan/specification when onboarding for complete research continuation. For a focused repair or review, read the current checkpoint and affected contracts; do not reopen the whole catalogue.
2. [PLAN.md](PLAN.md) gives the complete current objectives, phase order and completion criteria.
3. [RESEARCH_SPEC.md](RESEARCH_SPEC.md) contains the full family requirements: formulas/mechanisms, source alternatives, statistical questions, models, comparisons, failure cases and expected outputs.
4. [STATUS.md](STATUS.md) identifies completed evidence and pending work. [state/CURRENT.json](state/CURRENT.json) provides exact current run references, consumed budgets and hardware.
5. [Cursor implementation workflow](/workspace/coordination/trading-research-cursor/HANDOFF.md) explains assignments, isolated edits, review, integration and registered execution.
6. For a named family, consult its rows in [UNIT_CATALOG.md](UNIT_CATALOG.md) and [scope_map.json](scope_map.json). Follow their exact definition/source/case links as needed. Reuse already verified unchanged evidence; do not reread every historical passage before each small change.

The catalogue retains **153 parent units, 191 refinements, 712 source findings, 119 external findings, three focused method references and all 111 inventoried datasets**. This entry point is a navigation and continuation document; it does not replace those detailed definitions with summaries.

## Binding direction and precedence

Later explicit user instructions take precedence. The current research order is **validation across all intended families and discretionary frameworks → Context → Location**. Validation includes actual calculations, eligible real-data statistics, distributions, paths, timing/window comparisons, source variants and exact evidence-backed unsupported dispositions. It is more than passing fixtures. Do not run full Context fitting while other required validation remains unfinished. The user previously allowed Location to follow in a separate user-created task, but it remains part of the intended deliverable and must retain a complete handoff.

Keep full scientific quality and scope. A proxy, representative child, tiny pilot, source inventory or synthetic check does not complete a family. Preserve failed/no-event/no-contact/censored cases, exact clocks and identities, chronological training/calibration/confirmation cuts, meaningful source alternatives, uncertainty and sparse-support limitations. Missing implementation is pending work, not evidence that a mechanism is unsupported.

The primary research population is **2020 onward**, through the latest actually available eligible observations at each frozen cut. Older Jumbo/OHLC work stays separately scoped. NQ/ES receivers do not limit information inputs to NQ/ES. Use each comparison's eligible dates; do not force the intersection of all 111 datasets.

E0, complete trading policy, accounts/brokers, Response entry/exit systems, live deployment and profitability are later work. They are not prerequisites for the current statistics, Context and Location deliverables. Historical B00–B10/P0–P7 obligations remain reference material and cannot be used as a new completion checklist or silently marked passed.

## What is actually done

- **Jumbo development statistics:** complete original NQ/ES 2020–2024 extraction plus separate corrected-source NQ2024 sensitivity. The report contains 202,266 formations, 1,081,778 path rows and 53,822 source-specific observations. [Actual result](/workspace/trading-research/reports/jumbo-complete-development-extraction13-review.md).
- **Jumbo Context preparation:** all 116 intended targets inventoried; bounded optimizer/workload checks completed, including larger trees. Check 16 passed 442 tests. Full fitting, confirmation and independent predictive-quality comparisons have not run. The approved continuation budget is retained.
- **Auction/flow source calculations:** benchmark **23** passed121affected tests, all9complete source comparisons and all3continuation replays. C++ quote/native fusion and exact raw-source quote replay are accepted for this scope. [Performance review](/workspace/trading-research/reports/auction-flow-performance23-review.md).
- **Broader auction/flow checks:** check17 passed338tests and retained complete anchors/cohorts. Downstream20 reused9accepted source populations and reproduced18complete anchor/cohort payloads in130.973elapsed seconds. Full annual family statistics remain unfinished.
- **Shared infrastructure:** substantial readers, exact units/clocks, source identity, measurements, labels/folds, models and Location helpers exist. The earlier 851-test suite is scoped engineering evidence, not empirical family completion.
- **Completed Context models: zero. Completed Location family evaluations: zero.** Do not infer otherwise from implemented classes or resource estimates.

## Efficiency gains already present

The current source code contains NumPy vectorization of physical addresses/constants and native quote-interval expansion; one prepared quote/trade conversion per source batch; structural Parquet encodings; exact restricted-domain compressed JSON; and a fused C++ acquired-schema projection. Arrow reads columnar data; NumPy and the C++ kernel perform relevant numerical work. Other schemas retain the exact Arrow reference path.

The C++ source is embedded in [compact_native.py](/workspace/trading-research/src/trading_research/data/compact_native.py). The registered runner compiles it with GCC 13.3, `-O3`, no fast math and contraction disabled, records source/library hashes, and charges compiler CPU. Benchmark 16 exercised 62,779,203 rows across its tests/scans/replays/diagnostics; these are execution rows, not independent market observations. The backend is explicitly enabled by registered `benchmark`/`compute` modes; ordinary imports and the legacy `check` path do not automatically activate it.

The actual repeated-import bottleneck was **missing `dateutil.relativedelta`**, not pandas. A diagnostic observed 6,820 failed attempts for that module in one NQ window. `python-dateutil==2.9.0.post0` and `six==1.17.0` are now pinned and installed. Preserve these gains and the lock file.

Across nine complete units, source-pipeline CPU was 92.383 seconds in benchmark 12, 83.542 in 15 and 79.778 in 16. The last two equivalent diagnostic passes without optional event/native file writes used 47.518 and 44.031 CPU-seconds. These are partial improvements, not an order-of-magnitude end-to-end gain. Storage-free diagnostics retain full calculations but do **not** authorize replacing required production artifacts without implementing/reviewing exact reconstruction and downstream needs.

The latest source-only allowance is **152,641.745 CPU-seconds and261.16GB**, retaining all original margins and failure reserves. Removing duplicate quote Parquet resolves the earlier419GB storage projection on the measured basis. A separately frozen dual-count quote-cost model gives134,722.304CPU seconds; it is an empirical costing correction pending successful independent 17-window validation. Neither estimate includes unimplemented downstream/all-family/Context/Location work, and neither establishes the user's under-three-hour end-to-end target. Full source extraction completed in attempt36; empirical family statistics remain unfinished.

Historical source-clock27 and production-controller29 evidence remain accepted for their original scopes. The original extraction30 completed 2,939 windows before 51 source failures. Repairs through attempt36 recovered all650 formerly blocked windows without recomputing accepted prefixes. The original 17-window strict throughput holdout is not relabelled a success. Downstream Cursor drafts remain stopped and unverified.

## What remains and how to proceed when research resumes

Use the full family table in [STATUS.md](STATUS.md). The immediate research problem is finishing the actual auction/flow validation cohort and downstream mechanisms with a feasible execution/storage design. Do not restart endless profiling, worker repair loops or broad unchanged test suites. The current compiled change is already checked; only a new change, failure or unresolved requirement justifies new verification.

Keep the reviewed-but-unverified book-reinitialization, causal structure and memory modules explicitly separate from accepted source results. Their stopped comparison probes, frozen contracts and isolated drafts are retained. The deferred Jumbo prediction-reuse draft has known review defects and is not integrated as accepted code. [Exact draft and file map](state/DEPENDENCIES.json).

Then finish physical/implied volatility and remaining movement, options/OI/Greek-flow/exposure/node work, cross-market/events/regimes and the remaining discretionary frameworks under their full specifications. Complete all-family validation before Context; independently evaluate each meaningful Context target, then complete the Location catalogue and controlled lifecycle/path studies. Preserve every child and supported source comparison in the catalogue.

The user wants execution, results and completion without babysitting. Progress across implementation, verification and reporting boundaries without ending merely because an intermediate patch is done. Keep updates brief and factual. Ask only for genuinely missing information or authorization, and do independent work while waiting.

## Resources and safe continuation

Use `/tmp/trading-research-venv/bin/python` (Python 3.12.3) and the project's pinned dependencies. The environment can be restored from `pyproject.toml`/`uv.lock`; retain the runtime versions bound by each registered study. The supplied hardware is 21 vCPUs, 83 GB RAM and an RTX A4000 with 16 GB VRAM; current effective limits are 17.85 CPU cores and 82,999,996,416 bytes RAM. Host-wide CPU/RAM figures are not this allocation.

Auction/flow has **31 completed attempts, 58825.043296 CPU-seconds and 47,897,773,492 output bytes** retained against unchanged32attempts /192,000CPU-seconds /256GiB total output. Verification31 passed29affected checks and authenticated2939reused windows; all51original file failures are captured (33NaNserialization,18backwardclock), with599later windows blocked by carry. No run or repair cycle is active. The full performance target remains unresolved. Jumbo has **16 attempts and 1,473.051801 CPU-seconds** retained against its approved 24-attempt / 20,000-CPU-second continuation. Consult the live registries before any execution; this is a handoff snapshot. The previous bounded efficiency-delivery window and its consumption are recorded in CURRENT.json and were interrupted by this consolidation request. Never reset budgets or discard failed attempts.

All candidate imports, research tests, scans, fits and benchmarks run through the applicable registered family runner. Pure file organization, AST inspection and metadata/hash/link auditing do not execute research candidates. New scientific questions can use their own honest registered family under existing task authority; renaming the same failed or exhausted run to obtain a fresh budget is prohibited.

Preserve raw data under `/workspace/data`, original sources under `/workspace/sources`, immutable reports/CAS under the implementation and existing Git state. **Do not touch `/workspace/archive`.** Do not launch paid expansion, external trades, messages or live deployment. A historical filename containing “archive” inside the planning history is not the excluded `/workspace/archive` directory.

## Folder map and durable maintenance

| Location | Purpose |
|---|---|
| [PLAN.md](PLAN.md), [RESEARCH_SPEC.md](RESEARCH_SPEC.md), [UNIT_CATALOG.md](UNIT_CATALOG.md) | Complete current scope and exact detailed requirements |
| [STATUS.md](STATUS.md), [state/CURRENT.json](state/CURRENT.json) | Human and machine current state |
| [state/DEPENDENCIES.json](state/DEPENDENCIES.json), [state/FILE_INDEX.json](state/FILE_INDEX.json) | Exact key references and inventory of project files |
| [reference/trading-model](reference/trading-model) | Entire preserved historical plan, definitions, source review, cases and specifications |
| [history](history) | Earlier planning archive and pre-consolidation documents; historical authority only |
| [/workspace/trading-research](/workspace/trading-research) | Current code, tests, tools, frozen protocols, reports and evidence |
| [Cursor handoff](/workspace/coordination/trading-research-cursor/HANDOFF.md) | The implementation worker procedure and current assignment state |

`IMPLEMENTATION_INSTRUCTIONS.md` is a frozen registration input retained through a compatibility link. Its earlier family-by-family progression is superseded by this entry point and the current AGENTS.md; do not use it as the active execution order.

Old `/workspace/planning/trading-model`, `/workspace/planning/archives` and selected root document paths are compatibility links. Their underlying content now lives in this one planning folder. Existing immutable hashes and absolute references remain usable. Open historical documents through their recorded logical paths when following old relative links. Current documents link to the active sources directly.

Update STATUS.md, state/CURRENT.json and coordination/state.json after a substantive accepted result or changed user instruction. Keep old receipts and pre-change snapshots. Regenerate the file inventory when organization changes; never turn it into a research-completion percentage.

For a fresh task, use:

> Continue the existing project from `/workspace/planning/trading-research/START_HERE.md`. Read its current state, full plan/specification and Cursor workflow, preserve all scientific scope and consumed budgets, and continue the pending research in the recorded phase order. Reuse the existing implementation and accepted evidence. Do not restart the project or stop at an intermediate patch.
