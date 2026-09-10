# Clean-session label (which clock is clean this cycle)

## Definition
Jumbo treats which session is clean this week as a real input: London-clean weeks trade 03:00–06:00 as A+ and use NY as management or as the draw, NY-clean weeks ignore the urge to invent a London home run `[FIND p.9]`; "which session is the clean one this week? Build that TBR, not every TBR" `[FIND p.11]`; "we are in a cycle where London gives cleaner moves in relation to NY AM" `[XF p.40]`. Id `label.clean.session.rollingN`, a rolling label computed from the two clocks' own outcomes, known before the session.

## Citations
- Session rotation and clean weeks `[FIND p.9]`; pre-open checklist `[FIND p.11]`; London range cycle `[XF p.40]`; London 3 on 3 after a lunch give-back `[XF p.21]`.

## Faithful object
`label.clean.session.rolling10`: for each clock c ∈ {`range.6-9.published` with the 09:30–12:00 window, `range.london.00-03` with the 03:00–06:00 window}, the share of the last 10 completed sessions in which the clock printed a `G-default` reject at its ±0.5 projection (either side, the swept one) with no `b.c1` continuation beyond it; label = the clock with the higher share, `both` within ±0.1, `neither` when both shares < 0.3 (named thresholds); `known_at` = prior session close.

## Upgrades
- N = 5 / 20; score = single-break rate, or realized range / `env.ev.mean60` reach; add `range.gb.asia` as a third clock.

## Outcomes
- Next-session reject rate per clock conditional on the label (persistence); run lengths of the label; share of sessions labelled `neither`.

## Links
[clock-grid-and-bars](clock-grid-and-bars.md) · [tbr-6-9-range](tbr-6-9-range.md) · [range-path-class](range-path-class.md)
