# Bounded VIX-option intraday feasibility audit

Completed audit of three existing quote-day files and their OI files; no fitted trading model, strategy replay or official VVIX replication.

Read **261,970 quote rows**, at nine fixed UTC decision cuts across 18 expiry/cut combinations. Latest snapshots were selected before screening, so an invalid current quote cannot silently revive an old valid one.

The arithmetic screen requires positive bid, a strictly positive spread, positive displayed sizes and no more than one extra minute of snapshot age. Availability assumes a one-minute lag; actual receipts are absent. Quote condition codes, exchange-source rules and historical rates/settlement conventions are not certified here. Zero/invalid quotes remain excluded rather than interpolated into observations.

For each eligible expiry, infer a forward from the call/put pair with smallest absolute midpoint difference and retain the intersection of every eligible pair’s bid/ask parity interval. Fit individual OTM Black IVs by bisection under ACT/365, a declared 09:30 New York expiry assumption, and two discount-rate scenarios (0% and 5%). Rates are sensitivity assumptions, not historical rates. Nearest supported IV is not an interpolated ATM quote.

| Day | Quote rows | OI rows | Actual OI DTE range |
|---|---|---|---|
| 2020-01-02 | 62,560 | 440 | 20–167 |
| 2023-05-02 | 89,930 | 954 | 15–260 |
| 2026-09-03 | 109,480 | 1,120 | 13–257 |

| Cut UTC | Expiry | Paired strikes | Screened contracts | OTM IVs, 0% scenario | All-pair parity interval consistent? |
|---|---|---|---|---|---|
| 2020-01-02 15:00:00+00:00 | 2020-01-22 | 26 | 66/80 | 26 | True |
| 2020-01-02 15:00:00+00:00 | 2020-02-19 | 32 | 72/80 | 32 | True |
| 2020-01-02 17:00:00+00:00 | 2020-01-22 | 26 | 66/80 | 26 | True |
| 2020-01-02 17:00:00+00:00 | 2020-02-19 | 32 | 72/80 | 32 | True |
| 2020-01-02 19:00:00+00:00 | 2020-01-22 | 26 | 66/80 | 26 | True |
| 2020-01-02 19:00:00+00:00 | 2020-02-19 | 32 | 72/80 | 32 | True |
| 2023-05-02 15:00:00+00:00 | 2023-05-17 | 39 | 99/120 | 39 | False |
| 2023-05-02 15:00:00+00:00 | 2023-06-21 | 46 | 101/110 | 46 | False |
| 2023-05-02 17:00:00+00:00 | 2023-05-17 | 39 | 99/120 | 39 | True |
| 2023-05-02 17:00:00+00:00 | 2023-06-21 | 46 | 101/110 | 46 | False |
| 2023-05-02 19:00:00+00:00 | 2023-05-17 | 35 | 95/120 | 35 | True |
| 2023-05-02 19:00:00+00:00 | 2023-06-21 | 46 | 101/110 | 46 | False |
| 2026-09-03 15:00:00+00:00 | 2026-09-16 | 46 | 116/140 | 46 | True |
| 2026-09-03 15:00:00+00:00 | 2026-10-21 | 65 | 135/140 | 65 | False |
| 2026-09-03 17:00:00+00:00 | 2026-09-16 | 46 | 116/140 | 46 | True |
| 2026-09-03 17:00:00+00:00 | 2026-10-21 | 61 | 131/140 | 61 | False |
| 2026-09-03 19:00:00+00:00 | 2026-09-16 | 46 | 116/140 | 46 | True |
| 2026-09-03 19:00:00+00:00 | 2026-10-21 | 61 | 131/140 | 61 | False |

The directory name `dte60-full-chain` does not bound every OI expiry in these actual files. Quote eligibility and OI eligibility must be audited separately. This small deterministic selection shows which inputs are calculable in these snapshots, not representativeness across the archive.

An empty parity intersection means the entire screened set is inconsistent under that rate/synchronization scenario. A robust illustrative midpoint IV can still be calculated, but the inconsistency must reach O21 and be resolved or modeled before any certified surface is used. Small repricing error checks numerical inversion only; it does not establish a true IV, valid quote or predictive benefit.

Next research gate: certify quote/contract/source semantics and historical availability, run broader prespecified coverage cohorts, quantify bid/ask/rate/clock uncertainty, and then compare the C15/C16 specialists against physical-volatility and daily-VX baselines. VIX signed flow remains unavailable from these quote/OI files.

Detailed assumptions, numerical outputs and source hashes: [JSON evidence](vix_feasibility.json). Reproduction: [audit script](audit_vix_surface_feasibility.py).
