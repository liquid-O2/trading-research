# F08 roll and coordinate transition protocol

Status: frozen before dependent implementation. The registration report pins the
protocol, literal expectations, source review and code snapshot. This family shares
one combined full-suite worker with F05–F08; actual use is conservatively charged
to every participating family and retained under one physical execution identity.

## Scope and evidence

Cover F08, SR-F08, UP-F08 and F08.ROLL_PARITY with a finite deterministic
implementation batch. Source preparation is reports/f08-source-preparation.json:
one direct routed clause CEX-26 / T-SRC-CEX-26, hash-matched original conversation
lines 1155–1199 reused from F03; inherited INV-07, DA-01/02/10 and prior-level
context remain recorded separately. The source's 'front by volume' wording does
not specify causal selection time; the corrected comparator uses the completed
preceding session. Historical download claims do not certify current holdings.

The actual E0 dependency E0-COMPLETE-PARENT-OUTRIGHTS remains missing. Supplied
NQ.c.0 calendar-front outright acquisitions and NQ.OPT option acquisitions do not
provide the historically known complete NQ parent outright listings/definitions
and preceding completed-session volumes for every eligible competitor. Selected
raw-contract MBP over all required windows is separately required. An annual
union of calendar-front definition IDs is not a point-in-time parent universe.
No synthetic universe label or passing test can satisfy this real-data gate.
Continue independent engineering while leaving exact E0 cohort/policy execution
disabled. Acquired-cohort diagnostics retain their own names and requirements.

## Fixed semantic contracts

1. Immutable records validate exact string identities, int64 timestamps, tuple
   lineage, boolean eligibility/completeness and Fraction-valued coordinates.
   Namespace and instrument lifetime belong to a coordinate; numeric ID and
   display root alone are insufficient. Every change of evidence, even with
   unchanged numbers, changes the derived version. Reject an ID/content conflict.
2. Prior-volume selection uses a declared universe, typed predecessor-session
   evidence and definitions/volumes available at the cut. All eligible competitors
   need complete compatible volume. Missing does not mean zero. Tie-break by
   earlier expiry, then canonical identity. Retain every considered definition,
   volume record, exclusion, receipt, policy and universe version. Source evidence
   cannot silently certify itself as actual full parent market coverage.
   Name the latest source evidence clock input_known_at. The scalar reference is
   unpublished; an actual selection/transition publication separately retains
   decision_cut and actual_completion_at, with output availability max(required
   input availability, confirmation/effect, actual completion). Completion cannot
   precede the decision/submission cut; actual completion never also receives a
   modeled compute charge. Original horizon/validity endpoints do not restart.
3. Preserve fixed-calendar and supplied provider-map selectors as separately
   versioned deterministic comparators using explicit known-time mapping records.
   They cannot stand in for a missing volume comparator or use realized returns
   to choose a switch. Revisions never change decisions before their known_at.
4. A bridge is an additive point-coordinate relation between two different exact
   raw instrument lifetimes. Its two eligible observations retain their original
   clocks, price, tick size, skew, oldest-observation age, availability, evidence
   and uncertainty. Require a declared maximum skew and age. Age is admissible
   when cut minus the older quote time is at most max_age_ns; excess is stale.
   Missing, invalid, future or stale evidence produces reset/unavailable, never a
   fabricated simultaneous spread. Retain each bridge's actual observation span.
5. Translate old price p as p + new_observed_price - old_observed_price. Preserve
   genuine movement: current_new minus translated_previous_old is point change,
   not automatically a percentage or log return. Signed/zero prices are legal
   for point changes; log return requires positive operands and division requires
   a nonzero denominator. Do not silently mix these operation domains.
6. Old/new coordinates and source object/state versions accompany each transition.
   A repeated same-content transition ID is idempotent; conflicting reuse fails.
   A destination object cannot be submitted again as its old source. Translated
   level/profile/band records retain parent IDs, bridge version, uncertainty and
   cost/exposure lineage; reset is a distinct explicit lifecycle result. Price-
   bound state is reanchored or reset. State with a declared additive-translation
   invariant may carry; arbitrary indicator names confer no invariant.
7. Preserve exact point coordinates and profile volume mass. Convert tick-valued
   quantities through each instrument's own tick size. Off-destination-grid
   levels remain exact and flagged; execution must reject them until a separately
   declared rounding/risk policy applies. Never silently round a mapped stop.
8. Corporate actions distinguish split price/quantity scaling from dividend cash
   adjustment and from total-return/display coordinates. Availability is no earlier
   than source publication, effect and actual transformation completion. Source
   action eligibility and derived-result publication are separate. Native fills/strikes remain native; split
   deliverables and an option's exact future remain F02-owned contracts. A raw-
   option consumer rejects adjusted-display/total-return inputs. Later corporate-
   action revisions cannot rewrite original decisions or filled-trade economics.
9. Raw-contract fills and cash costs determine P&L. A chart adjustment is never a
   fill price. Reference consumer fixtures compare profile mass, mapped levels,
   preserved genuine point change, declared scale transfer and raw-leg accounting.
10. Retain bounded append-only transition/decision evidence with serialization and
    restoration. Validate content/configuration hashes, duplicate/conflict rules,
    original clocks and query cuts. An uncommitted result must not appear after
    restart; no external exactly-once claim is made. Bound records, envelope bytes,
    profile nodes and bridge/action chain length; backpressure fails explicitly.

## Literal reference and compatibility

Use a separate references/rolls_literal.py for elementary hand-specified selection,
bridge/adjustment arithmetic and finite state/coordinate consumers. It must not
call implementation selector/translation methods to obtain expected outputs.
The JSON fixture contains exact integer/rational literals, not values generated
by implementation code. Existing scalar helper tests remain supported at their
explicit known cut. Legacy helpers without a declared age policy must not grant
indefinite bridge reuse; later use requires an explicit policy.

The finite expected arithmetic includes volume20 beating10; tie by earlier
expiry; source100/new110 maps101 to111; current113 retains genuine change2;
negative old-5/new-2 maps-4 to-1 and current1 retains change2; 4:1 split400 to100;
raw ex-dividend100 to98 differs from total-return change0 with cash2; and actual
NQ old100→101 plus new111→113 gives60 gross USD,52 after four side fees of2 USD.
Those are engineering fixtures and not observed market economics.

## Cases and verification boundary

Cover the 26 preparation cases with explicit per-case assertions and limits.
At minimum the combined batch must include: immutable identity; missing competitor;
future volume and same-value new lineage; predecessor-session mismatch; namespaced
contract collision; supplied/fixed/volume rule distinction; expired competitor;
trade/book contract mismatch; missing/asynchronous/stale/future bridge; intraday
bridge correction and suffix invariance; genuine plus roll gap; negative/zero
operation domains; reset versus one-time translation; duplicate/conflicting and
double translation; profile mass and mixed raw contract rejection; different tick
grids; split publication/effect; dividend versus raw/total-return; raw strike
coordinate gate; declared scale carry versus price-state reset; actual raw fill
P&L; restart/config/content corruption; bounded records and chain/node capacity.

Keep source-faithful, corrected and further-candidate representations separate.
The reference-versus-kernel comparison uses identical finite inputs and measured
operation counts. Any timing output comes from actual timed toy work and is
labelled synthetic engineering work, with CPU/wall/RSS and exact input counts.
No model fits, historical market tape reads, parameter search or prediction/economic
trial is part of this batch. No assertion closes the dated native market cohort,
all production consumer integration, all original indicators, or P0–P7.

Perform one complete static review of the combined new implementation and affected
callers, then one consolidated repair. Root owns registration and the combined
supervised full-suite run. Proposed ceiling for that combined family: three
attempts,600 CPU seconds total,180 soft/190 hard CPU seconds,4 GiB address space
and240 wall seconds per attempt, subject to root's registered combined protocol.
Preserve failed attempts, exact source snapshot, output and resource telemetry;
do not run an extra F08-only search family outside that accounting.

## Explicit remaining gates

Dated parent universe/volume and selected MBP; native simultaneous old/new quotes;
real provider-map versus prior-volume parity; corporate-action notices and full
adjusted deliverables; all object/order/account/option consumers; uncertainty
calibration/error cohorts; matched roll-period warmup and economic comparisons;
and actual captured future receipt/operational parity remain separate evidence.
