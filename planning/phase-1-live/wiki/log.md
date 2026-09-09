# Ingest log

Format: date · what was read · how · notes. Raw sources are immutable; this log records the compile, not edits to sources.

## 2026-09-09 — live compile from coverage audit

This tree is a merge of two planning wikis. Neither prior tree was edited. Inputs:

1. A = `planning/phase-1-from-scratch/` wiki index and every page that claims a checklist object.
2. B = `planning/phase-1-fable/` wiki index and every page that claims a checklist object.
3. Packs (already in B/references, not rewritten): `jumbo-x-wiki-pack.md`, `greenbirdtrader-trading-framework.md`, `agent-method-matt-wiki.md`.
4. Raw evidence: `sources/documents/` (jumbo PDFs, 35 discretionary PDFs by filename, conversations user turns, inventory, indicators, reference-images). Archive plans not used.
5. Coverage table: `planning/phase-1-compare/COVERAGE.md`. Verdict: `planning/phase-1-compare/VERDICT.md`.

Rule applied: if B already has the object with definition, citation, faithful row, upgrades, outcomes → keep B’s page. If B dropped a sourced object A still has → take A’s section or write a short page from the source. Options pages must list NDX, NDXP, SPX, SPXW.

## Pages in this tree

Kept from B (patched where the audit marked a miss or drift): index, data-coverage, touch-reject-hold-break-grid, tbr-6-9-range, range-path-class, open-location-switch, clock-grid-and-bars, ev-range-expected-move, sessionstat-9-12-envelope, extensions-1-33-1-66, p-zones-benchmark, session-fail-boxes, value-and-profiles, absorption-and-big-trades, cvd-variants, smt-divergence, vol-estimators, options-nodes, sources-pine-archive.

Written short from A/source: fvg-body-gaps, sweep-cisd-blocks, tpo-ib-auction.

Not rebuilt: A’s 51-ticket catalog, Pine LUT families, higher-Greeks family, BBO family, adaptive HMM, floor-pivots-as-family.
