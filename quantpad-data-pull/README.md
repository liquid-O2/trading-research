# QuantPad data pull

This uv project translates `/Users/arunavayun/Downloads/databento_pull_list.md`
into resumable QuantPad API pulls. The Markdown file supplies the requested
datasets and priorities; live QuantPad coverage supplies the actual available
date ranges.

Futures use QuantPad continuous symbols (`NQ.c.0`, `ES.c.0`, `YM.c.0`, and
`RTY.c.0`). Files retain raw, unadjusted prices plus `instrument_id`, so rolls
remain auditable and no adjustment is accidentally re-anchored at a partition
boundary.

## Commands

```bash
uv run python pull_quantpad.py plan --phase 1
uv run python pull_quantpad.py run --phase 1
```

The downloader writes compressed Parquet to `data/`. A partition is first
written as `*.parquet.part` and atomically renamed only after completion.
Rerunning a command skips valid Parquet files, so interrupted pulls resume at
the first unfinished partition.

Partition boundaries are storage/request boundaries only. They never resample
or aggregate rows: one-second bars remain one-second bars, and every native
definition, statistic, trade, quote, or book event is retained.

For a small smoke test:

```bash
uv run python pull_quantpad.py run --id 01-nq-1m --max-partitions 1
```

The API key is read from `.env`; do not commit or print it.

Before moving Phase 1 to another machine, run:

```bash
uv run python validate_phase1.py
```

The command writes `manifests/phase-1-validation.json` and fails unless every
planned Phase 1 partition is a readable Parquet file and no partial file is
left behind.

## Stages

- Phase 1: continuous NQ/ES/YM/RTY bars, NQ one-second bars, and futures
  statistics/definitions.
- Phase 2: QQQ/NDX/NDXP option definitions, statistics and available CBBO,
  plus QQQ/SPY underlying bars.
- Phase 3: six years of NQ option definitions, statistics, one-minute bars,
  and trades, plus the 30-day NQ L2 sample. QuantPad accepts the
  `NQ.FUT.OPT` parent for definitions and statistics. Bars and trades must be
  fanned out to the individual contract symbols discovered from definitions.
- Phase 4: long tick-history pulls. NQ MBP-1 is fixed to 2020-01-01 onward.
  These pulls are intentionally separate because they can consume substantial
  disk space and time.

OPRA pulls through QuantPad are paused in favor of ThetaData. NQ and ES
options-on-futures MBP-1 are also paused pending confirmation of a QuantPad
API upgrade; the external API requires per-contract fan-out for those option
chains. Do not add either options MBP-1 job to an unattended queue.

`VX.c.0` resolves through QuantPad symbology on `XCBF.PITCH`, but the external
v1 payload API currently rejects it and the explicit v2 payload endpoint does
not accept API-key authentication. It is therefore not included in executable
stages until QuantPad exposes CFE payloads through the external API.

Small dependencies required for option valuation are handled separately:

```bash
uv run python pull_market_dependencies.py
```

This retains the official Cboe per-contract VX daily files from 2020 onward,
FRED USD rate observations, Yahoo daily QQQ/SPY/NDX/SPX prices, and QQQ/SPY
dividend and split histories. QuantPad supplies the separate QQQ/SPY one-minute
bars. Historical minute cash-index values are not available from the current
providers, so NDX/SPX intraday work must use NQ/ES with the daily cash anchor.

After every futures definition partition is present, generate the auditable
instrument and roll-segment tables without modifying the raw files:

```bash
uv run python build_futures_roll_map.py
```
