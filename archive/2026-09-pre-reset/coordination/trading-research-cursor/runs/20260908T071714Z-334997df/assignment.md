# Assignment 1: prepare quote columns once per bounded source batch

Implement this one performance change in the isolated checkout. The supervisor will review and run the registered verification. Use file reads and edits; shell commands, project imports/tests, market scans, fits and user questions are outside this assignment. Make one consolidated implementation and test pass, then return the changed files, important decisions and unresolved issues. Do not start other work.

## Why this change

The successful auction/flow check 6 retained at:
`/workspace/trading-research/reports/auction-flow-runs/c09887c082448be5af7e0fa23f4d880a545d83ea4f0c00fbff657dfed205660d/worker.json`
projects 195,233 source CPU seconds and 447,435,682,490 source output bytes. Before the 1.5 margin, `quote_atomic_consumers` is the largest CPU term at 39,324.58 seconds. These are projections, not full-study measured runtime. Existing structural storage and exact JSON improvements have already passed; retain them.

`InstrumentWindows.quote_rows` slices a bounded Arrow batch into atomic windows, then calls `QuoteWindow.add` separately. Each call repeats Arrow-to-NumPy conversion, action casting/membership masks and action/side grouping. Prepare reusable columns and categorical codes once per input batch, then pass views to the same ordered per-window calculations. This is a measured bottleneck with an identified repeated setup cost; the magnitude of savings remains to be established.

## Implementation boundary

Primary files:
- `src/trading_research/research/auction_flow_quotes.py`
- `src/trading_research/research/auction_flow_pipeline.py`
- `tests/test_auction_flow_quotes.py`
- `tests/test_auction_flow_pipeline.py`

Keep `QuoteWindow.add(table)` compatible for existing callers. An internal prepared-batch object/helper and a per-slice consumption method are sufficient; avoid a general framework. The pipeline should prepare one raw-instrument quote batch and consume its contiguous atomic slices. Preserve the previous arithmetic and reduction sequence inside each slice. Retain each actual last source key, row, action and side. Support actual Arrow null/string/binary cases accepted by the current interface; null categorical values must remain distinct from other categories. Keep preparation bounded to one input batch, with views released when it is consumed.

The supervisor has saved the exact pre-change quote implementation as `references/auction_flow_quote_check6/quotes.py`. Use it as an independent unchanged comparator; do not edit it or redefine its expected results.

## Acceptance criteria

- Preserve every output field and public call contract, including invalid-input rejection. Do not remove identity, order, window, known-at, null/flag, BBO/depth or capacity checks to gain speed.
- Preserve integer OFI, decompositions, paths, first extremum time/order, action-side counts, source lineage, snapshots, invalidation and original quote age exactly. Splitting or entering an empty interval must not invent a new quote or recover the book.
- Preserve the existing per-slice floating reduction order and tolerances. Current actual-source canonical measurement-byte comparisons remain required; no new looser tolerance is authorized.
- Add focused comparisons of ordinary and prepared paths against the frozen reference for chunked inputs, equal timestamps, boundary cuts/quiet windows, snapshots, clears/gaps, null categories, large clocks/depths and malformed inputs. Reuse existing fixtures where they cover these cases. Include the actual pipeline path, not only the helper.
- Keep native sink results and continuation state unchanged. Exercise the prepared path with the native sink in the existing integration fixtures.
- Retain existing source populations, storage formats, raw/data bytes, protocol, budgets, prior receipts, model targets and scientific definitions.

The supervisor will inspect the whole diff, consolidate genuine defects, and run the next authorized auction/flow check. That check must pass existing fixtures, all nine complete source-value comparisons and all three split-window comparisons. Acceptance of the optimization also requires a measured reduction in the affected setup/quote CPU at the same workload, without a material total-CPU or memory regression; fitting an overall budget is a later full-workload gate, not the definition of improvement. If the experiment does not improve cost, report that honestly instead of weakening correctness.

Output a concise patch summary and explicitly say that the implementation awaits registered execution. Do not claim verified performance or completed research.
