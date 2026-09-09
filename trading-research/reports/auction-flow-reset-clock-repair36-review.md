# Source timestamp repair: complete extraction verified

**All four reset timestamp faults are handled, and all 3,589 scheduled source/date windows across 167 physical files are now complete.** Registered run36 succeeded, reused 3,550 complete windows, produced the final 39 and left **zero failed or pending windows**. All child processes were reaped and every adjacent carry identity in the complete receipt catalog was independently reconciled.

The implementation preserves original raw timestamps, all eleven source fields, physical row addresses, event multiplicity, invalidation and same-file carry. It applies book state in original source order. The short spans whose duration cannot be established are explicitly recorded as **clock uncertainty**; they are subtracted from standing and dwell integrals. Overlapping native bins and atomic minutes cannot claim complete timing coverage. State then continues after the interval, with no inferred book recovery.

| Physical source variant | Affected date | Uncertain duration |
|---|---|---:|
| ES `2020-06.parquet` | June 30, 2020 | 396,342,941 ns |
| ES `2020-07.parquet` | July 1, 2020 | 903,843 ns |
| NQ `2020-06-29.parquet` | June 30, 2020 | 499,920,433 ns |
| NQ `2020-06.parquet` | June 30, 2020 | 499,920,433 ns |

The two NQ acquisitions remain separate variants. The exact plan pins each source metadata identity and both original neighboring rows. It does not admit arbitrary backward clocks or discard resets as duplicate snapshots. The strict default and existing redundant-snapshot predicate remain intact.

Audit35 read all four complete affected days and established that each contains exactly one reversed event. The June ES reset follows 96 source rows and nine trades; both NQ variants follow 141 rows and eighteen trades, with no earlier gap or reset. This ruled out treating those clears as redundant. The earlier conclusion that the whole windows had to remain blocked was too restrictive: exact timing can be marked unknown while physical state and later carry continue.

Verification36 ran **154 tests: 152 passed, zero failures/errors and two pre-existing optional compiled-backend skips**. New cases check literal duration subtraction, preserved reset/raw/native row counts, unchanged original timestamps, blocked carry, malformed-plan rejection and reader batch sizes 1, 2 and 64. Existing quote, time-at-price, native, pipeline, carry, replay and production checks also passed. Production then compiled and used the existing native kernel, with the affected uncertain quote intervals routed through the checked reference duration path.

Independent inspection of the four real repaired measurement artifacts reconciled **16,177,008 original rows** against audit35's counts, exact uncertainty bounds and affected-minute timing ineligibility. Each original reset remained present. ES July's first-minute standing duration is zero; June ES and both NQ variants retain only the trusted duration before their uncertainty begins. Both NQ variants have the same address-free raw-value hash while retaining distinct physical provenance.

The complete [receipt catalog](/workspace/trading-research/validation/AUCTION_FLOW_RETAINED_PRODUCTION_RECEIPTS_36.json) contains 3,589 unique, hash-checked success receipts. All 167 physical chains begin with their original initialization, and every subsequent start/carry joins the previous completed end/carry. The runner's [V28 operational configuration](/workspace/trading-research/validation/AUCTION_FLOW_SOURCE_CHECK_EXTENSION_V28.json) now points to this complete catalog. Only that pointer/catalog changed after verified run36; source producer code remains identical to its registered snapshot.

Run36 took **549.426 seconds (9.16 minutes)**, used **1,909.896156 CPU-seconds**, wrote **923,923,974 bytes** and peaked at **4.285 GB observed aggregate RSS**. CPU accounting was complete and every declared resource limit was satisfied. Production finished at **2026-09-08T20:26:25.433785+00:00**. This was beyond the earlier 20:11 UTC cutoff; work continued under the user's latest instruction to fix these faults. Earlier elapsed time and resource consumption were retained.

The family now stands at **36/36 authorized attempts**, **71,701.255619/192,000 CPU-seconds** and **55,928,815,964 bytes of 256 GiB**. No retries, failures, budgets or source variants were erased. No further source retry is needed for this repair.

Complete physical source extraction retains conditional data/timing eligibility. It does not mean every source interval has exact timing, or that the deferred all-family research, Context, Location or full-pipeline three-hour target has been completed or measured.

Evidence: [original full-day reset audit](/workspace/trading-research/reports/auction-flow-runs/29ea857d072996b6fc8cfb114f35d0c48f44fb82672b81066974857022f7530b/outputs/original-reset-context.json), [frozen uncertainty plan](/workspace/trading-research/validation/AUCTION_FLOW_RESET_CLOCK_UNCERTAINTY_V1.json), [registered verification](/workspace/trading-research/reports/auction-flow-runs/aa5d1159b3fcba6782f654516d05f35ce182df4890973329eb7324027082007b/execution.json), [complete production outcome](/workspace/trading-research/reports/auction-flow-runs/aa5d1159b3fcba6782f654516d05f35ce182df4890973329eb7324027082007b/worker.json), [regression results](/workspace/trading-research/reports/auction-flow-runs/aa5d1159b3fcba6782f654516d05f35ce182df4890973329eb7324027082007b/outputs/continuation-checks.json), [current checkpoint](/workspace/planning/trading-research/state/CURRENT.json).
