# MVFL indicator zones and bias vote

**Historical background — scope clarified 2026-09-12.** This retained note predates the current M01–M12 / O001–O166 contracts and is outside empirical v1. Its “faithful object,” upgrade and outcome sections describe earlier proposals; they do not report current implementation acceptance or measured results. Source/Pine constructions and old statistics remain distinct from author rules. See the [current method map](index.md), [status](current-status.md), [source catalog](source-catalog.md) and [historical review ledger](/workspace/planning/phase-1-from-scratch/REVIEW_LEDGER.md).

## Definition
The user-supplied "institutional indicator" `[CEX L17]`, `sources/documents/indicators/momentum-volume-flow-levels.txt`: a seven-condition bias with hysteresis (4 of 7 votes to flip) `[MVFL L2, L9–10]` built on a 5-minute calculation timeframe `[MVFL L5–6]`, two of whose conditions create price zones: delta-event zones from k-means clustering of outsized delta bars `[MVFL L19–37]`, and volume-anomaly zones from bars whose volume exceeds 2.5 × a 20-bar average `[MVFL L39–46]`, both traded as break / rejection levels `[MVFL L139–150, L178–181, L414–432]`, inside a London / NY session filter `[MVFL L51–56]`. Ids `flow.delta.zone.kmeans`, `flow.vol.anomaly.zone`, `bias.mvfl`. Tier 2: constructions to rebuild, no hardcoded statistic to trust; the prior review kept the shelf-clustering idea, session window and hysteresis and asked for a rebuild on true aggressor delta `[CEX L33]` (assistant note, tier 4).

## Citations
- Title and vote inputs `[MVFL L2, L9–10]`; SMA200 / 50 / 5 `[MVFL L14–16]`; delta granularity 1-minute sub-bars, dynamic threshold 6 × a 50-bar average, fixed floor 3000 `[MVFL L19–23]`; SQA 27 vs SMA50 `[MVFL L25–26]`; k-means k = 4 per side, hide zones below 45% of the strongest, 12 iterations, minimum thickness 0.4 × ATR-14, 3000 detections `[MVFL L29–37]`; volume anomaly 2.5 × avg-20, zone thickness 0.2% of price, merge within 0.5%, 50 zones `[MVFL L39–46]`; session window `[MVFL L51–56]`; HTF calculations `[MVFL L58–70]`; delta signal and anomaly detection `[MVFL L79–102]`; direction on anomaly zones `[MVFL L139–150]`; delta-line break / rejection `[MVFL L178–181, L414–424]`; MTF confirmation `[MVFL L432]`.

## Faithful object
As coded: delta per 1-minute bar by the script's sub-bar volume rule (OHLC proxy, same family as `flow.cvd.ohlc`); event when |delta| ≥ max(6 × SMA50(|delta|), 3000) inside the session window; `flow.delta.zone.kmeans` = per side, k-means (k = 4, 12 iterations) on event prices weighted by |delta|, zone = cluster min / max padded to 0.4 × ATR-14, zones below 45% of the strongest weight hidden; `flow.vol.anomaly.zone` = bars with volume > 2.5 × SMA20(volume) → zone of ± 0.1% of price around the close, merged within 0.5%; `bias.mvfl` = the 4-of-7 vote label with hysteresis. `known_at` = bar close on the 5-minute timeframe.

## Upgrades
- Aggressor delta from MBP-1 in place of the OHLC proxy `[CEX L33]` (assistant); k 2 / 6; thresholds; session NY-only.

## Outcomes
- Grid at zone edges (break / rejection as the script labels them); HOD / LOD capture vs random levels of matched density (the density caution `[CEX L33]`, assistant); `bias.mvfl` agreement with `path_class`; faithful disagreements = zone sets that differ between proxy and aggressor delta.

## Links
[cvd-variants](cvd-variants.md) · [value-and-profiles](value-and-profiles.md) · [sources-pine-archive](sources-pine-archive.md) · `../RULES.md` R-P20
