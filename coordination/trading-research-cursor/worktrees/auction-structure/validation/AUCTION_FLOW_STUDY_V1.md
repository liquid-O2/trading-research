# Auction and participation study on the acquired event stream

This is a distinct scientific study under research-v2. Its question is how
reported-side trades, their ordered size-cohort paths, trade-at-price auction
structure and best-quote pressure describe subsequent auction/participation
outcomes, and what information they add beyond price and ordinary activity.
It does not continue, rename, reset or spend another attempt of the Jumbo
study. It reuses applicable admitted prices, calendars, source audits and
measurement definitions. No run is authorized by this file beyond the
explicit bounded study registration described below.

The eventual result covers both auction/profile/reference and
flow/participation/structure/memory families in the active specification.
Sharing source extraction does not merge their prediction targets or replace
the individual results. A data pilot or baseline report cannot close either
family. E0, account/broker, full Response policies and live operation remain
outside this study.

## Population and source identity

The primary population is every actually acquired NQ/ES MBP-1 observation
from 2020-01-01 through the frozen acquired NQ endpoint,
2026-09-03T06:09:59.901114378Z (exclusive). The exact upper cut is
1788415799901114378 ns; ES ends at its actual acquired August 2024 endpoint. The existing
four-dataset footer index supplies the exact input list and metadata stamps;
original files remain unchanged. ES has the declared discontinuous 25-month
MBP cohort. Missing ES periods are retained as unavailable, including the
existing 2022 reconciliation window. NQ and ES comparisons use the dates
eligible for the specific question; broader NQ results remain separate.

Preserve all eleven raw columns, physical file/row address and original
storage order in the source lineage. A compact trade projection retains
reported aggressor, exact quarter-point ticks where valid, quantity, event
time, flags, source address, unknown side and exclusions. It must not dedupe
different prints with identical economic fields. A manifest hashes all raw
columns before projection. A compact quote projection retains action, side,
flags and provider-normalized before/after order; trade-attached pre-trade
quotes do not become additional fresh quote events.

Provider receipt, exchange sequence and numeric publisher are absent from
this export. They remain unknown. The primary information scenario is
event time plus 250 ms, with 0 and 1,000 ms sensitivity scenarios selected
before outcomes. These are scenarios, not measured historical strategy
receipts. Same-source storage order is retained; cross-source equal-time
order remains ambiguous. Raw contract identities are joined as of the cut
to existing admitted definitions; unresolved or changed coordinates cannot
be used for cross-contract price travel.

Trade action T is included regardless of F_LAST, except replay/snapshot
trades and invalid size, which retain explicit excluded rows. B is reported
buy, A sell, and N/unsupported sign stays unknown. Unpriced/off-grid volume
remains in flow totals and is unavailable to price-dependent geometry.
Book gaps, snapshots, clears, unsupported enums, receipt-quality flags and
their combined bitsets are retained. Unknown side bounds do not bound
unobserved volume. Book recovery and restarting a new local flow anchor
are different operations; neither reconstructs missing historical trades.
No complete-depth or hidden-inventory conclusion is supported by MBP-1.

Coverage means the declared acquired stream and whole requested source
window passed its checks. It is conditional on that supplied archive; an
absence of flags cannot prove the provider captured every exchange event.
Empty-but-observed windows, missing files, flagged interruptions, incomplete
anchors and unobserved endpoints stay separate. Expected cash dates and
early closes reuse the existing independently sourced cash calendar. A
full-session/overnight profile is an explicitly named observed futures-clock
window, not a certification of historical venue status.

### Overlapping acquisitions and reusable native observations

The full source index contains overlapping monthly and weekly acquisitions,
including the fixed NQ stressed date. Each acquisition is a separate source
variant. Read and measure every overlapping resource-window variant; do not
concatenate, time-sort across sources, or deduplicate economic fields. Compare
the complete eleven-column selected values in original order with fixed
65,536-row Arrow blocks so a reader batch boundary cannot invent a difference.
An equality result supports an address-preserving alias for that exact window;
it does not establish global source supersession. Disagreement retains both
populations and requires an explicit complete-cohort source disposition. All
statistical comparisons cluster shared variants by economic date.

Keep ordered trade, quote/invalidation and excluded-trade Parquet projections,
including original addresses and raw fields needed for later quote/execution
joins. The 100 ms cells use true within-cell cumulative paths and quote
transitions, with source/coordinate/standing masks; exact event projections
remain available for finer lag, anchor and sequence questions. First/high/low
values keep actual event clocks and source order. Capped last-trade dwell and
displayed midpoint occupancy never claim the unobserved true residence path.

The first check certifies the implemented source/atomic/native/time-at-price
and storage path only. Later anchor/annual/model/Location workloads require
their own complete implemented workload estimates and applicable combined
checks within this same family budget. No study-wide fit feasibility is
inferred from the core source preflight.

## Definitions and meaningful comparisons

Retain the exact M01–M13, C07/C08/C18, L05–L11/L19 and observable R-pattern
contracts in the active unit catalogue. The reusable measurement kernels
are the references; new columnar calculation paths require independent
arithmetic cases and real-data equality on their actual inputs.

- Flow: literal buy/sell/unknown/CVD; session, rolling and event resets;
  exact source filters of at least 100, at least 75 and inclusive 30–60;
  all excluded mass; count- and size-weighted occupancy; true ordered
  cumulative OHLC including the opening value. Train-only equal-count,
  equal-volume and top-35% definitions and continuous size bases remain
  separate comparisons. Preserve source extrema clocks, ordinary/cohort
  disagreement, and close-only versus actual OHLC information.
- Auction: exact unsmoothed side-separated trade profiles and retained
  source bar proxies; tick rows, neighboring widths/origins and explicitly
  mass-conserving smoothing; the full POC maximizer set and plateaus;
  68% and 70% value conventions, declared expansion ties, prominence,
  shelves/valleys, and compatible-grid cumulative mass distance. Preserve
  low/high overflow and unpriced mass. Signed delta is never normalized as
  a probability distribution.
- Anchors: prior/developing cash RTH, observed full session, overnight,
  06:00–09:00, calendar week/month/quarter/year, rolling, disclosed dealing
  ranges, and causal confirmed swing/leg/event/composite anchors. A
  retrospective geometric start has its later selection/publication time.
  Source display toggles do not change numeric measurements.
- TPO and footprint: actual bracket visits, bar-range occupancy proxies,
  bounded trade dwell and displayed-quote occupancy remain distinct.
  Compare bracket length, initial balance, provisional/final single prints,
  tails and naked references. Preserve same-row/diagonal side geometry,
  physical row adjacency, stacked thresholds, unknown mass, source-time
  prefixes and true order. A crossed price without a print creates no trade
  mass or actual TPO visit.
- VWAP/references: exact weighted moments, rolling downdates, weighted
  quantile/robust bands and retained source percent/SD variants; anchor
  differences and selection delay. Official settlement remains distinct
  from observed closes/opens and needs its own publication evidence.
- Quote/participation: OFI, positive-depth imbalance, microprice, separate
  price/size changes, standing duration, action/side event rates, and
  source-supported net displayed recovery without double subtraction.
  Trade-only, quote-only and combined information use identical cuts.
  Compare covered-exposure intensity, multiscale lags/decays and effort
  versus progress; preserve zero effort and quiet/no-event outcomes.
- Structure/memory: causal multiscale swings, regular/hidden divergences,
  displacement, FVG/order/rejection-block variants and observed pattern
  state transitions. Keep birth, protection confirmation, retest, failure,
  expiration and revisions separate. Time, volume and visit decays are
  distinct; future favorable markout cannot select a memory's birth.

Subsecond/second questions reuse ordered compact trades and quote events;
minute totals cannot reconstruct lost extrema or event order. Aggregates
are reusable views, not replacements for the required event observations.

## Analysis and independent evaluation

For each definition publish independent dates, windows, print/volume
support, exclusions, distributions/tails, conditional paths and timing
curves with date-block uncertainty. Preserve no-event/no-new-volume,
no-contact, ambiguous and censored populations. Report matched-date
differences and stability by year, session, coverage, activity and age.
Use 1,000 deterministic date-block bootstrap replicates for declared
comparisons; descriptive repeated prefixes do not increase date support.

Context targets remain individual: flow surprise/count/marked intensity;
effort-to-future-progress; cohort/control and known sequence branches;
auction acceptance/rejection/migration; added volume, no-new-volume and
added-mass shape; derived future POC/value; reference/band reach and
departure. Use suitable seasonal/persistence baselines and regularized
statistical models, with an information-matched stronger learner where
diagnostics justify it. Added information, representation and capacity are
separate comparisons. Report proper scores or distribution/duration error,
calibration/coverage, support, incremental information and disposition.

NQ chronology: train 2020–2022, development 2023, calibration/selection
assessment 2024, frozen confirmation 2025 through the actual September 2026 endpoint, retaining its
incomplete final observed day and unobserved future labels.
ES chronology follows its actual discontinuous coverage: train 2020,
development July–December 2023, calibration January–March 2024, and frozen
confirmation April–August 2024. Missing dates are not imputed. The ES later
confirmation period remains a data dependency. Every label must mature
within its stage, with overlapping observations purged at boundaries.
Train-derived cohorts, transforms, clocks, residuals, calibration and
downstream Context joins respect those closures.

Location populations include all source/revised candidates, ancestry,
width/distance/count/age, birth/publication/revisions and all failures.
Evaluate reach and time to reach, ordered reaction/traversal, favorable and
adverse excursion, retests and lifetime. Compare generators at fixed
scorer and scorers on fixed candidates, with matched placebo geometry and
Context ablations. Do not select successful examples or require unrelated
confluence/Response confirmation. Complete Location coverage remains an
individual research output, separate from calculation and model quality.

## Bounded execution and preservation

The initial registered check combines relevant semantic/adapter checks,
reuse validation of unchanged source evidence, selected real reference
parity and full ordinary/stressed-day pipeline measurements. The fixed
resource cohorts are NQ and ES on 2020-03-16 and 2024-03-11, plus the
previously identified NQ flagged-source hour, 2021-02-14 18:00–19:00
America/New_York (row group 88 in the weekly file named 2021-02-08). Two additional full observed 18:00-17:00 New York windows ending on
2024-03-11 (one per root) measure full-session array and output size. These
are cost and integrity units, not a random sample or finished empirical study. Inspect
all declared windows even when a quality failure makes a mechanism
unavailable; unexpected implementation errors fail the attempt.

The initial allowance is at most 32 attempts and 192,000 cumulative CPU
seconds for this distinct, previously unregistered study. Reserve 1,200 CPU
seconds per consolidated check/preflight, at most 12,000 per extraction
partition, and at most 16,000 per fit or confirmation stage, subject to the
cumulative balance. These are ceilings, not predictions of required compute:
the earlier retained one-hour compact projection is only a lower-complexity
reference, and this complete source path adds native cells, exact time-at-price,
full event retention and complete storage round trips. Peak RSS is bounded
at 4 GiB; native arrays together are bounded at 2 GiB. Derived output is
bounded at 16 GiB per attempt and 256 GiB for the study, with each file at
most 512 MiB. These initial bounds are fixed at first registration; subsequent
changes require an explicit same-family amendment and retain all consumption. A hard CPU
margin of 10 seconds is reserved and charged, and failures keep their
actual consumption. Full workloads start only after measured CPU,
memory and output projections fit, including statistics and serialization.

Plan one shared source extraction per root/year, retaining completed
partitions with exact input/dependency identity; reuse its ordered trades
and feature/label views across targets. Source partitions and raw field
hashes remain reproducible. Report fixed per-report work separately from
date/row-dependent work. No unregistered research imports/tests/scans/fits,
attempt resets, renamed continuation, paid data or external trading action
are authorized. New changes receive only the meaningful checks they need;
unchanged verified dependency closures remain applicable.
