# Source additions from greenbirdtrader posts dated 2026-09-14

Raw capture: `/workspace/sources/x-raw-2026-09-14/greenbirdtrader/` (two posts, seven photos, full text). These are dated source examples with printed entries, stops and objectives. They add branches to the accepted Green Bird families and widen one scan window; they change no existing branch. Each addition is a versioned baseline branch with an exposure record dated 2026-09-14, implemented by the family adapters in subphase 04, given its own full-history population, and reported in the Strategy Book beside the accepted branches.

## What the accepted implementation covers and what it does not

`scan_green_failure` builds references for `nyam_box`, `previous_hour`, `asia_tdo_case`, `cash_open_reclaim_case` and the `prior_day/week/month_level` branches, and scans every one of them from `max(09:30, reference known-at)` to the account-day end. There is no London-box reference in the failure scanner (London appears only in the VWAP continuation scanner), the Asia box exists only with the midnight true-day-open confluence forced on, and `pocket_required` is false throughout, so the golden pocket is never evaluated as an entry condition. The GB-SCALP page records the continuation trigger as unpublished.

## GB-FAIL additions, owner P15-10

**A1 `london_box`.** Reference: the finished London box, operational 02:00 to 05:00 ET under A2-GB-CLOCK (the source names the London low and high, never the bounds). Sweep of the London low (long) or high (short) at any time after the box completes, including before 09:30. Confirmation: a complete five-minute close back through the level. Optional retest: after the confirming close, a later contact with a higher low (long) or lower high (short) relative to the sweep extreme, then a further five-minute close through the level; the post's entry is that later close after the New York open. Objectives as named: the midnight true-day open first, then the opposite London edge. Structural stop beyond the sweep extreme. Source, post 2099513366326730859: "London low gets swept before the NY open. We reclaim it, retest it and form a higher low. After the open, price closes back above the London low. That's my entry. Midnight open first. London high next. 100 points long."

**A2 `asia_box`.** The Asia box (20:00 to 00:00) failure without the true-day-open confluence that `asia_tdo_case` requires: sweep of the Asia high and a five-minute close back below it gives a short, mirrored for a long; objective the opposite liquidity as named. Source, same post: "Price pushes higher, sweeps the Asia high and fails to hold above it. There's my failed breakout. I switch sides. Another 100 points short."

**A3 overnight scan window.** For `prior_day_level`, `prior_week_level`, `prior_month_level`, `asia_tdo_case`, `asia_box` and `london_box`, scan from the reference's known-at time through the account-day end instead of from 09:30. The accepted 09:30-start population stays the accepted baseline; the widened window is the addition and is reported separately so the overnight population is visible on its own. Source, post 2099503614372741234: "Overnight, the sweep below the previous day's low and reclaim gave me the first long."

## GB-SCALP addition, owner P15-11

**A4 `golden_pocket_continuation`.** After a defined impulse, a measured range with known start and end (on 2026-09-11 the range created by the 08:30 CPI move), a New York session pullback into the golden pocket `[L + 0.50(H-L), L + 0.618(H-L)]` of that impulse, in the impulse direction. Entry on the first complete five-minute close back out of the pocket in the impulse direction; this trigger bar is an operational choice, because the post says "hit the continuation long" without naming the bar, and it stays labelled operational. Stop beyond the far edge of the pocket. Objective the impulse extreme or the prior-day extreme as named. Source, post 2099503614372741234 and its charts: "Bullish context. Defined range. Pullback into my area." with a 35-point stop below the pocket and sell limits at the prior-day high. This supplies the trigger the GB-SCALP page records as unpublished; the directional-context and small-size clauses of that page still apply.

## Search-bank note

The "retest and form a higher low" condition in A1 is the S2 defended-retest alternative applied to a source branch. Record it as source-stated for the London branch, not as a universal rule for other branches.

## Printed fixtures

MNQU2026, 2026-09-14: long entry 28,903.75, exit 29,037.00 (about 100 points); short entry 29,081.50, stop 29,098.75, target 28,890.50. MNQU2026, 2026-09-11: golden-pocket long entry 29,382.00, stop 29,347.00, targets 29,494.50 and 29,521.75. Replaying these as conformance fixtures needs native data after 2026-09-03, which is not owned at this snapshot; until it is, they are recorded examples, not replay checks.

## Wiki work at the next writer window

Add both posts to `wiki/source-catalog.md`; add the examples and the four additions to `wiki/method-green-bird-failure.md` and `wiki/method-green-bird-directional-scalps.md` with the raw anchors; add a dated `wiki/log.md` entry. Add A1 to A4 to the acceptance checklists of P15-10 and P15-11, rebuild the bundles, and record the change in AMENDMENTS.json.

## Clock caveat for every source-stated time

The chart footers in these posts read "UTC-4", so the times on them are New York daylight time, which our clocks reproduce. But an author who writes "02:00 to 05:00" or "20:00 to 00:00" in text may mean a fixed offset all year, a platform default, or a different zone, and our implementation converts every stated clock as New York time with daylight-saving handling. For a source that does not, every winter session window shifts by one hour. The reconstruction ledger records, per source, the zone each stated clock is expressed in and the evidence for it (chart footers across summer and winter posts, or an explicit statement), and lists the branches whose windows would move if the zone were a fixed offset. Until a source's zone is established, its clock-based branches carry the label `clock_zone_unverified`.
