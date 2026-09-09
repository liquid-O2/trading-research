# Session-fail boxes and reference lines

Family: **day-type**. Jumbo 2026 remains the primary published range family. Green Bird adds named clocks and a sweep-failure rule to the same path tables.

## Evidence and definitions

Source: the supplied [greenbirdtrader-trading-framework.md](/home/arun/.codex/attachments/4acf7436-a646-4f7a-b1ad-f4271ecd42a8/greenbirdtrader-trading-framework.md), sections 0, 3–6, 8, 16 and the final July–September pass. **HIS WORDS**, **HIS CHART** and **INFERRED** preserve that file's evidence tags. Its instructions and execution examples do not expand this planning amendment.

| Object / named variant | Definition and evidence |
|---|---|
| Jumbo 6–9 | Reuse the existing 06:00–09:00 ET object unchanged. It remains the primary benchmark. |
| GB-NYAM | **HIS WORDS:** 09:00–10:00 ET high/low. The box must finish first. Outcomes count only after 10:00; 09:45 is early for this idea. |
| GB-10-11 | **HIS CHART:** 10:00–11:00 ET, the next completed hour in the August 20 example. Outcomes start after 11:00. |
| GB-hour | **HIS WORDS / HIS CHART:** the last completed 60 minutes. Freeze each box at its declared cutoff. The sampling cadence is a disclosed variant in SPEC. |
| GB-Asia | **HIS WORDS:** Asia high/low. **HIS CHART:** painted box and AS.L. **INFERRED clock:** approximately 20:00–00:00 ET. Outcomes start after midnight. |
| GB-London | **HIS WORDS / HIS CHART:** London high and LO.L. **INFERRED clock:** 02:00–05:00 ET. Outcomes start after 05:00. |
| Prior day high/low | **HIS WORDS / HIS CHART:** PDH/PDL. Reuse the existing prior-day reference variants and their session IDs. |
| TDO | **HIS WORDS / HIS CHART:** first print at 00:00 ET. A named confirmation is a 5-minute close back through this line after a sweep. |
| NWOG | **HIS WORDS / HIS CHART:** weekly gap and Sunday 18:00 ET open. This amendment locks the other endpoint to Friday settlement; the file says Friday close. Store both endpoints. NWOG is a destination, not an entry. |
| 9:30 open reaction | **HIS WORDS:** sweep/reclaim of the 09:30 ET cash-open price. This is a separate line reaction, not the unfinished 9–10 box. |
| Golden pocket | **HIS WORDS:** 50.0–61.8% retracement of a completed impulse. Measure the NYAM-height and user-requested 6–9-height variants. Location only. Keep the measured impulse and orientation explicit. |
| A+ sweep label | **HIS WORDS:** no sweep means not A+. This amendment records only whether a sweep happened. It does not reproduce a full grade or prescribe an action. |

Jumbo clocks retain their own source identity even when a window overlaps. The [Jumbo manual, pp.4–7](../../../sources/documents/jumbo/Time-Based%20ranges%20Framework%20%28JJumbo%29.pdf#page=4) includes a 20:00–00:00 liquidity window. That does not make the GB-Asia clock published. [Jumbo London examples, pp.25,40–41](../../../sources/documents/jumbo/xfcmg2.pdf#page=25) retain separate London TBR and 1.33/1.66 extension variants. Do not derive them from the inferred GB-London box.

## Faithful objects and failure rule

Freeze completed ranges and known reference prices. Persist formation end and known_at. A sweep requires a breach of an already available edge or line. A touch alone is not a sweep. Count what follows: fail back inside, hold outside, or an unresolved/censored path.

**HIS WORDS:** the failed-break rule and 5-minute close through TDO or PDL. Measure `sweep-fail-print` and `sweep-fail-close5` separately. The latter requires a completed 5-minute close back inside the box. Keep `close5-through-TDO` and `close5-through-PDL` as distinct confirmations. The [SPEC](../SPEC.md#session-fail-boxes-and-fail-back) defines the symmetric line rules and corresponding hold-outside variants.

**HIS WORDS / HIS CHART:** the London example stacks PDH, Asia-high and London-high sweeps before failure toward NWOG. Store each sweep and its time as confluence. NWOG remains the destination. A golden-pocket contact or an A+ sweep label alone supplies no failure confirmation.

## Upgrades to measure and outcomes

- Compare the stated clocks with the existing frozen clock grid. Keep inferred Asia/London clocks tagged in every row. Compare completed-hour and 15-minute sampling cutoffs for the portable 60-minute box.
- Compare print fail-back with 5-minute-close fail-back and hold-outside. Preserve the common G1–G3 reaction grid alongside these named confirmations.
- Compare golden-pocket location present/absent and TDO/PDL confirmation present/absent on matched event populations. Do not select a future impulse to improve a past location.

Use the existing touch, fail-back, hold-outside and four-way path-class table. Include opposite-edge and NWOG destination visits, timing, overshoot, no sweep, failed confirmation, neither break, ambiguous order and censoring. Compare native populations and matched cutoffs/horizons against Jumbo. Source percentages and fleet P&L are not measurement targets.

## Related

[Time-based ranges](time-based-ranges.md) · [Range-break paths](range-break-paths.md) · [Jumbo day classes](jumbo-day-classes.md) · [EV range](ev-range-expected-move.md)
