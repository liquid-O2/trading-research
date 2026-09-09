# Ingest log

Format: date · what was read · how · notes. Raw sources are immutable; this log records the compile, not edits to sources.

## 2026-09-09 — first compile (this tree)

1. Method files read in full, in order: `references/agent-method-matt-wiki.md` (157 lines), `references/jumbo-x-wiki-pack.md` (110 lines), `references/greenbirdtrader-trading-framework.md` (701 lines). GitHub skims: mattpocock/skills (to-prd, to-tickets), poteto-mode, karpathy CLAUDE.md.
2. `sources/documents/README.md`, `SOURCE_MANIFEST.json`, `inventory/DATA_INVENTORY.md` (765 lines), `inventory/databento_pull_list.md` (91 lines; a pull list, not proof of acquisition).
3. Conversations, every line: `Develop Trading Model.md` (1,540), `Design robust feature levels.md` (1,854), `conversation_export (1).md` (1,306), `conversation_raw_log.md` (1,072), `jumbo/JJumbo_Conversation_Export.md` (484). User turns carry authority; assistant plans are evidence of ideas, not approvals.
4. Jumbo PDFs: `Time-Based ranges Framework (JJumbo).pdf` 38 pp, `SessionStat+.pdf` 12 pp, `xfcmg2.pdf` 48 pp, `jjumbo-findings.pdf` 14 pp. Every page rendered and visually inspected; text extracted to scratch. Zoom renders used to confirm the numbers on XF p.11, p.24 and TBR p.12, p.30.
5. Discretionary PDFs: all 35, every page rendered and inspected; text extracted. Page counts in `REVIEW_LEDGER.md`.
6. `reference-images/zerano-charts-SPX-2026-08-24T18-51-29-251Z.webp` converted and viewed (SPX chart with levels; reference only).
7. Indicators: `Open Source Fractal - Customized.txt` (1,521 lines), `momentum-volume-flow-levels.txt` (488 lines), and `Pinescript-indicators--main.zip` unpacked to scratch: 84 files, 51,601 lines, 2,960,327 bytes. Every file read line by line across four batches. `md5sum` shows exactly one byte-identical pair: `6 to 9 Session and Levels.txt` = `6 to 9 session & levels v2.txt`. `nq_stats_mapper` vs `NQ Statistical Mapper.txt` and `hourly_stats_levels` vs `NQ Hourly Retracement Levels.txt` differ in bytes but carry the same hardcoded tables.
8. Repo runtime inspected for conventions only (no code written): `trading-research/AGENTS.md`, `tools/` registered runners, `src/trading_research/__main__.py` E0 limits (`cpu_soft_seconds 180`, `cpu_hard_seconds 190`, `address_space_bytes 4 GiB`, `wall_seconds_limit 360`), pinned venv `/tmp/trading-research-venv/bin/python`.
9. Not read by instruction: `planning/phase-1-from-scratch/` (Astra's tree), `archive/2026-09-pre-reset/` (no page here lacked a source citation, so it stayed closed), Skylit docs (Phase 2–3).
10. Context was compacted twice during the read; the Pine catalogue survived as notes plus the persisted tool outputs and was re-checked against the files before writing.

## Pages compiled this pass

index, log, data-coverage, touch-reject-hold-break-grid, tbr-6-9-range, range-path-class, open-location-switch, clock-grid-and-bars, ev-range-expected-move, sessionstat-9-12-envelope, extensions-1-33-1-66, p-zones-benchmark, session-fail-boxes, value-and-profiles, absorption-and-big-trades, cvd-variants, smt-divergence, vol-estimators, options-nodes, sources-pine-archive.

Then, from the wiki: `SOURCE_MECHANISMS.md`, `REVIEW_LEDGER.md`, `PRD.md`, `SPEC.md`, `tickets/01–07`, `PHASE.md`, `QUESTIONS.md`.
