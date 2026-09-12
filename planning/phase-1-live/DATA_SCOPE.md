# Active study data scope

User scope clarified on September 12, 2026: **NQ is the primary traded instrument; the historical study starts January 1, 2020.**

The archive-wide acquired inventory lists retained datasets and their physical gaps. Required coverage is assessed for the selected instrument, method branch and decision window, as FORMULAS C04 specifies. An unrelated archive gap is not a prerequisite for an NQ candidate.

| Input | Role in the current study | Required coverage |
|---|---|---|
| NQ trades, price bars and MBP-1 | Primary market observations and the selected execution/flow evidence | 2020 onward, bounded by actual acquired endpoints and the selected candidate's window |
| ES trades and OHLCV | Peer price/profile/volume/timing context when selected | 2020 onward for the required peer window; native ES instrument identity and causal ordering retained |
| ES MBP-1 | Optional quote/liquidity evidence | Required only if a selected rule examines ES's own spread, BBO or resting liquidity; no blanket ES book backfill for the NQ study |
| YM trades/OHLCV | Conditional peer input for the explicit ES/NQ/YM triad in O147 | The selected triad window; preserve native AMT-object correspondence |
| RTY | Conditional context only if explicitly selected | 2020 onward when used; absent 2017–2018 definitions and empty pre-2017 partitions are outside this study window |
| Macro observations | Conditional news/macro inputs | Only the named series, transformation, vintage and availability evidence required by the selected branch |

FORMULAS O147 uses native price/profile/TPO event timing for peer first use and target revision. ES trades can supply the executed price/volume evidence; OHLCV supplies compatible bar/window summaries. Those dependencies do not require ES resting-order-book data. A distinct ES liquidity rule would add quote requirements.

NQ MBP-1 remains limited to recorded depth-one state and executions. Selected procedures requiring off-touch depth, hidden reserve or individual order identity retain their specific evidence limitations.

For NQ minute recovery, the active 2020+ portion contains **12,420 recovered keys across nine full sessions**. The 32 recovered minute keys from 2010–2015 remain archived but are outside this study sample.

## Macro acquisition policy

- Use FRED/ALFRED observations and historical vintage queries for the selected macro series. Preserve the initial release and revisions as separate records. A current revised value cannot replace the value available at a past decision.
- Keep the observation/reference period separate from the vintage/release date. FRED real-time periods are calendar dates; they do not by themselves establish an intraday release clock or market-data receipt time.
- Add publisher release evidence where an intraday rule requires it. Preserve any assumption that official release time is the availability time, following O162.
- Use yfinance for supported market-price, corporate earnings and financial context. Do not treat it as a verified archive of original macro releases and their exact historical availability.
- Macro data is required only by the selected branch. Recoverable provider data and unpublished author-specific macro series/transform/decision definitions are separate gaps.

The identified 20-series FRED collection is now backfilled for 2020+ reference periods and vintages, with a December 2019 CPI/payroll supplement for releases published in January 2020. It contains 37,003 vintage records and 160 individually verified BLS publication dates. Intraday clocks for revisions/other series and observed feed arrival remain separate requirements. The credential is not stored in this plan or the artifacts. [Backfill and verification](/workspace/implementation/reports/phase1-live/macro-backfill/README.md).

References: [FORMULAS C04 and O147](/workspace/planning/phase-1-live/FORMULAS.md), [FRED vintage output options](https://fred.stlouisfed.org/docs/api/fred/series_observations.html), [FRED real-time date precision](https://fred.stlouisfed.org/docs/api/fred/realtime_period.html), [yfinance API reference](https://ranaroussi.github.io/yfinance/reference/index.html).
