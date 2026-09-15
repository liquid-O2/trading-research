# P15-16A JJ-TBR track work log

## Playbook

Feature. Architect arena skipped: the session cap is three live agents and one code writer, and only grok-4.6 is available. Two shapes were compared by the lead. Chosen shape is an independent B0.2 scanner in `jumbo.py` driven by a `RULES` table and a per-branch stage funnel. Rejected shape is a B0.1 transform that rewrites locations. B0.1 never saw the 1.33-1.66 band, so a rewrite cannot invent those contacts, and a family transform would risk changing frozen B0.1 rows.

## Source page notes

- NY clock. F18 cites TBR p.6. The user prompt cited TBR p.4. TBR p.4 is indicator instructions. TBR p.6 states all times in the document are Eastern Standard Time, ET. B0.2 uses TBR p.6 as the clock source and records the page mismatch here.
- 86.46% figure. JR p.70: "An astonishing 86.46% of reversal of off the -0.5 stdv (exhaustion)" with the modal window 09:40-09:50. The evening ruling restates it as reversal from the extended range. Statistics file stores both the source sentence and the ruling figure. A mismatch is a finding, not a rule change.
- Absorption body 0.6. TBR p.35 text names the 14-period volume average and a volume multiplier. "body 0.6" is not in the extracted text (it is on the settings picture). Registered OD: small-body ratio `abs(C-O)/max(H-L, tick) <= 0.6` and volume `>= 1.5 * 14-bar average`.
- 2025-12-30 P-zone prints are four prices, not boxes. OD: 10-point boxes centered on those prices.

## Decisions

- Do not edit `common.py`, `confirmation.py`, `baseline_repairs.py`, method_pack scanners, or wiki.
- Do not change `scan_variant`, `confirm_at_contact`, or `_empty_hook`.
- B0.2 episodes are plain dicts. `HistoricalEpisode.bind` rejects unknown fields.
- `scan_b02` accepts NativeMarketView, HistoricalFeatures, or a duck-typed tape used by fixtures.
- Extension bands call `o015`, they do not copy the formula by hand.
- Judas baseline entry is reclaim of the swept edge (RR-06). 3-minute OB is the F11 confirmation baseline, not a substitute for the reclaim.
- London box is 02:00-03:00 ET, action 03:00-06:00. The 00:00-03:00 clock is not used.
- Extension reaction search starts at 10:00 (wiki re-read and the track prompt). Internal rotation stays session-wide (F08). `single_extended` reduced-expectation after 10:00 (F08).
- RR-02 lives in MERGE_NOTES only.
- Judas B0.2 emits at most two sweep cycles per side: the first sweep from 09:00, and the first sweep inside 09:40-09:50 if it is a different bar. Unbounded rearm on every re-cross produced 2191 slice episodes.
- Replay matching scores pass + side + level + entry window and keeps the best episode, so an early sweep does not hide a later in-window reclaim.
- Prior RTH high/low for NativeMarketView is loaded once per date via HistoricalFeatures.prior("day"). VAL/VAH stay unknown without a prior profile.
- Funnel counts cascade: a non-pass stage stops later pass counts. Inapplicable stages are omitted, not written as 0/0/0 between live stages. Last recorded stage pass equals B0.2 pass.
- JR p.37 `one_side` is high_only + low_only. `both` is excluded.
- JJ-2025-09-09: our level 23739.24 sits inside the RR-01 band [23727.00, 23743.50]; the author printed the far edge 23727. Recorded on the replay row. Rule unchanged.
- RR-09 BigTrades deferred. JR p.50 NQ >=100 NY / >=75 London is a BigTrades indicator readout. JR pp.49-50 35% footprint transaction filter is a different flow view. Neither is a labelled series on the native tape, so B0.2 does not implement a substitute threshold. RULES row `RR-09-bigtrades-deferred`.
