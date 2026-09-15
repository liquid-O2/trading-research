# Level Atlas

Descriptive census. This document selects nothing.

Levels counted: 530. Strategy-alignment rows: 4111.

## Extreme proximity by level kind

| kind | n | high within 8 ticks | low within 8 ticks | control high within 8 |
| --- | ---: | ---: | ---: | ---: |
| call_wall | 38 | 0 | 0 | 0 |
| gamma_flip | 36 | 0 | 0 | 0 |
| key_gamma | 38 | 0 | 0 | 0 |
| max_pain | 38 | 0 | 0 | 0 |
| put_wall | 38 | 0 | 0 | 0 |
| top_gamma | 114 | 0 | 1 | 0 |
| top_vanna | 114 | 0 | 1 | 0 |
| top_vega | 114 | 0 | 1 | 1 |

## Strategy alignment distance bins

| bucket | n |
| --- | ---: |
| beyond | 2314 |
| within_0.1 | 205 |
| within_0.25 | 379 |
| within_0.5 | 462 |
| within_1.0 | 751 |

## Limitations

- Cash-index roots have no native intraday spot; mapping is ETF/futures labelled comparison only.
- NQ/ES option boards are unsupported because Databento DBN is unparsed.
- Strategy alignment uses Phase 1 run-1.0.1 geometry.entry, not a P15-03 refit.
- Profile-family atlas cells are specified but not produced in this attempt.
- Intraday quotes are scoped DTE/strike feeds, not full-chain.

Every numeric cell in LEVEL_ATLAS.json points at `extremes_sha256` or a board field from EXPOSURE_BOARDS.json.

