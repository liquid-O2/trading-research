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

## 2026-09-10 — thin pages from `../RULES.md` A7

Read: `../RULES.md` §A7 and the source rows it points at (TBR, XF, FIND, GB pack, the discretionary PDFs, the Pine archive, `momentum-volume-flow-levels.txt`, conversation user turns). How: one page per concept where an A7 id had a citation and no page; ids that are variants of an existing page's concept were named on that page instead of duplicated. Every A7 id carried a citation, so no id is blocked; none is listed here as blocked.

Pages written (31): tbr-remaining-clocks, overnight-range, overnight-profile, dealing-range, prior-eth-profile, composite-profiles, weekly-delta-profile, delta-spike, prior-rth-quadrants, prior-session-reference-levels, unfinished-business, sigma-band-reversion, manipulation-distribution-envelope, vwap-anchored, absorption-candle-jumbo, refill-zone, ofm-catalyst, footprint-imbalance-zones, candle-poc-flip, protected-high-low, mvfl-indicator-zones, reward-system-3tick, digit-thinning, tape-speed, spread-width, approach-speed, premium-discount-50, daily-open-1800, gex-walls-and-max-pain, amd-phase-labels, clean-session-label.

Ids folded into existing pages (one line each): `env.ss.rth.avgHL60` on sessionstat-9-12-envelope; `env.vwap.rth.sd1` / `sd2.5` / `sd3` on value-and-profiles; `label.amt.80pct.two-period` on tpo-ib-auction. Index: new section plus two citation-key rows.

Not paged (not A7 ids; grid candidates or tier-4 proposals only): `range.4h.*`, `env.pine.sessionstat.P10-P90`, the JJX derived-range families. Tape objects on the new pages keep the `[unmeasured]` tag from RULES.md §0.2: locations now, triggers only after a FINDINGS row. No tickets added, no runner started, RULES.md unchanged.

