# F02 registry and payoff reference batch, version 1

Registered before the new implementation or verification on 2026-09-06.
This is deterministic engineering work under F02/F02.PAYOFF and UPK-01.
It does not select a market hypothesis or authorize options execution.
The primary policy remains one outright NQ/ES mini.

Input: an immutable, available instrument definition, explicit supported
contract terms, source/assumption versions, half-open validity interval,
separate last-trade/exercise/fixing/payment clocks, and exact rational prices
with named coordinates. Output: a definition-bound conversion kernel,
purpose-specific eligibility, tick validation/rounding, intrinsic exercise
value and separately typed settlement obligations. Future delivery is a
position at its exercise basis, not cash equal to option intrinsic value.
Unsupported/missing deliverables and model domains fail explicitly.

New declared reference ports:

| Port | Inputs and clock | Consumers/capability |
|---|---|---|
| F02.IDENTITY.SNAPSHOT | Available raw definition versions and explicit retirement events; selection at `(valid_at, known_at)` | Immutable contract identity and eligibility; no prediction |
| F02.PAYOFF.KERNEL | F02.IDENTITY.SNAPSHOT plus dated terms and explicit calendar facts; maximum input knowledge time | Exact quote/dollar and intrinsic/settlement conversion; no option fair-value model or future execution guarantee |
| F02.TICK.SCHEDULE | Same frozen definition/terms | Explicit premium bands, grid origin, domain and side-independent floor/ceil operations; a fixing value is not rounded to an order tick |
| F02.DEFINITION.CHANGES | Appended definition/retirement versions | New snapshot/kernel identity and affected consumer inputs; old frozen kernels and historical cuts remain unchanged |

These are reference service interfaces. Integration into the full runtime
graph and all O/P/X consumer reruns remain P5 work; no new current-cycle
feedback edge is introduced.

The batch implements identity lifetimes, retirement and serialized restart;
exact constant and piecewise tick arithmetic; linear outright dollar changes;
cash index, physical equity/basket and future-delivery option expiration
payoffs; missing-leg/unsupported domains; deterministic affine inverse versus
conditional-mean rejection; currency and sensitivity conversions; and the
calendar-time versus remaining-time derivative sign. A separate literal
payoff reference uses direct hand equations. A compiled kernel caches only
definition/term constants, not market observations.

Expected cases are F02-01–23 in F02_SOURCE_CASES.md, with these concrete batch
examples frozen in `tests/golden/f02-kernels.json` before execution:

- NQ +0.25 at 20 USD/point = 5 USD; ES +0.25 at 50 = 12.50 USD.
- Cash call `(8487.71−8250)×100 = 23771`; put
  `(8500−8487.71)×100 = 1229`. OTM/ATM exercise is zero.
- Known adjusted deliverable: 138 shares plus 10.94 USD. At a synthetic share
  price of 8 and a strike obligation of 1000 USD, call intrinsic is 114.94 USD.
  Exercise delivers 138 shares and requires 989.06 USD net cash payment.
- European option before its explicit exercise time: unavailable. AM and PM
  use different fixing identities and timestamps, even with equal strikes.
- A future-delivery call with fixing 12250.01 and strike 12250 exercises into
  one exact named future. Its 0.20 USD intrinsic is distinct from cash paid
  now (zero). The 0.01 fixing excess is not rounded to the 0.25 futures tick.
- NDXP premium bands: below 3.00, 0.05; from 3.00, 0.10. 2.95 and 3.00 are
  valid, 3.05 is invalid; floor/ceil of 3.05 are 3.00/3.10. Boundary behavior
  is explicit in the terms, not guessed from prose saying above/below.
- Reused numeric ID in disjoint lifetimes; delayed correction; deletion at
  known time 60/effective time 50; checkpoint/restart and suffix deletion;
  unrelated lifetime unaffected; no automatic resurrection of older state.
- Incomplete basket and unsupported exercise/style/currency/coordinate,
  wrong underlying future, stale/future fixing, incomplete metadata and
  ambiguous same-time versions must fail before a result is emitted.
- Exact affine `y=2x+3` has inverse `(y−3)/2`; a conditional-mean mapping
  cannot expose a reciprocal inverse. `dV/dt = −dV/dτ` at fixed expiry.

Primary sources inspected for these equations/domains:

- [CME equity index unit lesson](https://www.cmegroup.com/education/courses/introduction-to-equity-index-products/discover-equity-index-notional-value-and-price)
  states NQ/ES multipliers and the ES tick calculation. The current page is
  equation evidence; it is not a new dated historical ES terms admission.
- [Nasdaq's 2019 settlement example](https://www.nasdaq.com/articles/index-option-basics:-why-investors-should-consider-using-options-on-an-index-2019-12-17)
  distinguishes share delivery, cash settlement and XQO/XQC, with the two cash
  amounts above. Its then-current expiry schedule is not extrapolated.
- [Nasdaq NDXP factsheet](https://www.nasdaq.com/docs/2021/02/01/NDXPFactSheet.pdf)
  supplies the premium bands and European cash-settlement domain. Despite the
  2021 URL path, its footer says 2025; it is not treated as a 2021 publication.
- [CME NQ weekly options FAQ](https://www.cmegroup.com/articles/faqs/e-mini-nasdaq-100-tuesday-and-thursday-options-frequently-asked-questions.html)
  distinguishes the exercise fixing from the futures daily settlement and
  gives the 12250.01/12250 example. The actual underlying future is required.
- [OCC memo 49591](https://infomemo.theocc.com/infomemos?number=49591)
  describes the prior adjusted deliverable and a subsequent unresolved
  distribution. Only the stated prior basket is used as a literal arithmetic
  example; the synthetic price/strike are not market observations.
- [Cboe VX option specification](https://cdn.cboe.com/resources/membership/VIX_OOF_Contract_Specification.pdf)
  distinguishes UX future-delivery options from VIX cash-settled index options.
  No UX market cohort or quote coverage is inferred.

Resource family: `F02-registry-payoff-reference-v1`, maximum three verification
attempts, 600 CPU seconds total. A complete combined verification gets a
180-second CPU reservation, hard 190-second CPU limit, 4 GiB address-space
limit and 240-second wall limit; parent monitoring remains responsive.
Any numerical/resource comparison uses fixed small fixtures, no tape scan,
model fit, random hyperparameter search or economic simulation. First review
the complete new implementation and affected call sites, collect issues, then
make one consolidated repair pass and run the combined verification. Further
execution requires a changed implementation or a concrete unresolved failure.
