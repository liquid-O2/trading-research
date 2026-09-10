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


## 2026-09-10 — FORMULAS.md source check (wiki ≠ source patches)

Read: every source cited by `../RULES.md` section B and by the live pages (TBR, XF, FIND, SS, GB pack, X pack, the discretionary PDFs through the archived per-page text, the Pine archive, MVFL, user conversation turns), then `../RULES.md`, `../RULES_SCORES.md`, `../CONSTRUCTION_AUDIT.md`, and the Python under `implementation/src/trading_research/research/phase1_live/`. Output: `../FORMULAS.md` (105 R- blocks plus the shared primitives). Patches, one sentence each:

- session-fail-boxes: `lvl.nwog` endpoint changed from "Friday 17:00 settle" to Friday close per `[GB L60, L69]`, with the 15:59 RTH close and the 17:00 settlement kept only as named variants.
- absorption-candle-jumbo: removed the MVFL 2.5 × SMA20 borrowing; multiplier, body ratio and timeframe are source-unspecified for this Jumbo object and the 14-period average is trailing `[TBR p.35]`.
- tpo-ib-auction: `label.amt.open.30m` now carries the `[AMT1 p.11]` open-type definitions (drive = never trades back through the 09:30 open) and records that the retained code labels drive against the prior value area instead.
- manipulation-distribution-envelope: the Pine object is the HTF / daily candle anchored at 18:00 (NY-midnight option) with lookback 60 `[PINE Statistical OHLC Projections HTF.txt:8–15]`; the RTH 09:30–16:00 candle is a named variant, not the default.
- extensions-1-33-1-66: the beyond-edge coordinate now rests on Jumbo's own chart labels `[PACK L66]` and `[TBR p.21]`; the Pine 6–9 file is no longer cited as a source for a Jumbo object; the FIND fib-list reading is the named from-origin alternative.
- tbr-6-9-range: the Pine "restatement" line is marked as a third-party file that is not Jumbo's script and serves comparison rows only.
- sessionstat-9-12-envelope: `env.ss.minavg60` now states that `[SS p.6]` prints no formula and names both readings (lower-half average; min of the two one-sided means) with no default.
- refill-zone, delta-spike, tape-speed, approach-speed, candle-poc-flip, protected-high-low, weekly-delta-profile, ofm-catalyst: every constant the page names but no source prints is tagged "(named; not printed by the source)"; the printed ones (60 / 80 / 100-lot clusters `[REF p.5]`, the 30-lot minimum `[OFM p.4]`) stay as printed.

Rule recorded in `../FORMULAS.md` §0.1: Jumbo geometry comes from Jumbo's materials only (manuals, X archive, findings, X pack, user turns); the Pine archive holds no Jumbo script and its "6–9"-style files are cited only in the `R-P` rows. No tickets added, no Phase 2 work, no Python written.
