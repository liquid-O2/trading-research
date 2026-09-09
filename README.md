# Trading research workspace

Public snapshot of the current workspace. **Research is stopped at the user's request; Deliverable 1 remains incomplete.** Nothing in this export authorizes resuming research jobs.

- [Start here](planning/trading-research/START_HERE.md): current instructions and research state.
- [Research plan](planning/trading-research/PLAN.md) and [specification](planning/trading-research/RESEARCH_SPEC.md).
- [Current status](planning/trading-research/STATUS.md) and [checkpoint](planning/trading-research/state/CURRENT.json).
- [Implementation](trading-research/src/trading_research), [tests](trading-research/tests), and [research reports](trading-research/reports).
- [Source documents, PDFs, images, and indicators](sources/documents).
- [Planning references and chart images](planning/trading-research/reference).
- [Coordination, saved drafts, and worker reports](coordination/trading-research-cursor).
- [Acquisition scripts](quantpad-data-pull).

## Included and excluded

Includes code, documents, media, readable reports, supporting report metadata, and saved implementation drafts. Drafts and failed/interrupted runs retain their original status.

Excludes raw market data, generated data tables and artifact caches, credentials and `.env` files, local environments, execution logs, the original Git history, and `/workspace/archive`. These remain on the original workspace; this repository is not a complete market-data backup.

All standalone PDFs and images found outside the excluded raw-data/archive/runtime directories are retained. The planning history bundle is retained in numbered chunks. Source PDFs and images are unchanged.

[EXPORT_MANIFEST.json](EXPORT_MANIFEST.json) records selected files and their checksums, excluded generated files, and compressed/split-file mappings. Existing absolute `/workspace/...` links and research input paths describe the original environment.

## Large text reports and history bundle

Large text files are losslessly stored as `.gz`; large binary bundles are split into numbered pieces to fit GitHub's per-file limit. Large Markdown reports include a short navigation preview with a link to the complete compressed report.

To restore their original paths locally, with SHA-256 verification:

```bash
python3 restore_compacted_files.py
```

This only restores files; it does not run research or download market data. Keep restored oversized files out of Git. Credentials belong in a local ignored `.env` file.
