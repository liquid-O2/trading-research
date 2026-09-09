# Absorption and BigTrades

## Definition
**Absorption**: aggressive effort into a level is soaked up by passive orders, price gets no reward, and the opposite-side aggression then confirms `[ABS p.8 L124–134, p.9 L141–143]`. Properly defined it needs three things including passive size that holds **and refills** as it is consumed `[MATH p.8 L124–128]`; large traded size alone is not absorption `[MATH p.4 L70, p.8 L124]`. Stages: failed vs confirmed absorption `[STOP p.2 L13]`. **BigTrades**: an indicator that highlights large executed trades at bid / ask; "those are not absorption bubbles" `[XF p.25 L326–327]`; his thresholds are 100 contracts on NQ during NY and 75 during London, below 100 is noise `[XF p.25 L322–323]`; footprint filtered to the top 35% of transactions `[XF p.23 L293]`.

## Citations
- Ethos BigTrades: aggression marker, 30–60 contracts on a 40-range NQ chart, instrument-specific `[BIG p.3 L46–52]`; effort vs reward, body vs wick prints `[BIG p.4 L63–77, p.6 L112–114]`.
- Refill: zone built by clustered large aggressive prints; refill = defenders reload; raw aggression features barely beat a coin flip (AUC 0.54), level memory carries the edge `[REF p.5 L101–113, p.9 L207, p.10 L224]`; three-tick replenishment reward window `[ABS p.3 L40, p.4 L59]`; refill schematic `[RD p.8 L109–119]`.
- Who's in control: how price arrives at the extreme (aggressive vs drift) `[WIC p.4 L47–54]`; retest logic `[WIC p.5 L62–69]`.
- Jumbo: "easy spot absorption at midpoint of the range and taper at lows" `[XF p.23 L292]`; absorption at 6–9 key levels `[XF p.27 L361]`; Absorption Zone+ features (colour coding, isolation, imbalances) `[XF p.44 L563–568]`, "absorption zone at the reversal" `[XF p.46 L607]`.
- Data limits: MBP-1 gives every BBO update and trade with aggressor side, size and order count at the touch; not depth beyond the touch `[JJX L159]`; MBP-1 only, no MBP-10 / MBO `[JJX L16, L146–157]` `[BRIEF]`; replenishment proxy = BBO reload after consumption (assistant idea, tier 4, to measure) `[CEX L35]` `[CRAW L378]`.

## Faithful object
- `flow.bigtrade.100ny` / `flow.bigtrade.75ldn`: single trade prints ≥ threshold, tagged by aggressor side and price; Ethos comparison `flow.bigtrade.30-60` `[BIG p.3]`.
- `flow.absorption.A` (effort / no-reward): at level `L` within 2 minutes, aggressive volume toward `L` ≥ the 90th percentile of 2-minute aggressive volume that session, price advance beyond `L` ≤ 2 ticks, then reversal ≥ 0.25·R within 15 minutes.
- `flow.absorption.B` (BBO replenishment proxy): size consumed at the touch ≥ q90 of touch sizes, reload of displayed size at the same price ≥ 50% within 500 ms, repeated ≥ 2 times; the "refill" measurable from MBP-1 only at the touch.
- Hidden book / off-touch refill / iceberg detection: **not measurable** with MBP-1; printed as such `[BRIEF]`.

## Upgrades
- Thresholds as named rows (100 / 75 / 50 / q99 of print size); window 1 / 2 / 5 minutes; reversal `r` from the grid; location conditioning (at key zone vs at POC vs at 6–9 edge / mid).
- Absorption at mid vs taper at lows (Jumbo's two shapes) as separate rows.

## Outcomes
- Event counts per session and per location class; reward / no-reward rate; grid outcomes at the event price; reject rate at extreme vs at POC.
- BigTrades vs absorption event overlap (share of BigTrades prints inside an absorption event) — the "bubbles are not absorption" check.
- Faithful disagreements: sessions where `flow.absorption.A` and `flow.absorption.B` disagree on the presence of an event at the AM extreme.

## Links
[value-and-profiles](value-and-profiles.md) · [cvd-variants](cvd-variants.md) · [data-coverage](data-coverage.md) · [touch-reject-hold-break-grid](touch-reject-hold-break-grid.md)
