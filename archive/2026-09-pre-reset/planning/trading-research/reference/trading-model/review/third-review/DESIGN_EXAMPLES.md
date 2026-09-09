# Verified finite design examples

Finite arithmetic, ordering and clock examples only. This does not test an implemented trading system, data feed, forecast model, policy or profit.

**27 explicit assertions passed.** These examples check the internal logic of the corrected specification and the small review-only IV inversion routine. They are not the thousands of proposed trading-system phase checks.

| Example | Actual | Expected | Meaning |
|---|---|---|---|
| EXAMPLE-REWARD-01 | 95 | 95 | Incremental marked-net reward telescopes to terminal net. |
| EXAMPLE-REWARD-02 | True | True | A shorter trade can leave valuable occupied-time capacity; all alternatives use the same boundary. |
| EXAMPLE-REWARD-03 | False | False | Adding complete-trade reward and overlapping continuation double counts value. |
| EXAMPLE-ORDER-01 | (2, 1, 1) | (2, 1, 1) | Identical excursions and endpoint do not identify order. |
| EXAMPLE-ORDER-02 | ('upper', 'lower') | ('upper', 'lower') | The ordered labels must differ despite matching excursion summaries. |
| EXAMPLE-HORIZON-01 | False | False | Contact at minute nine and favorable passage at eleven is unresolved at the original minute-ten end. |
| EXAMPLE-HORIZON-02 | True | True | A new ten-minute contact-origin forecast has a different end and label. |
| EXAMPLE-QUOTE-01 | 100 | 100 | The strategy cannot use the later venue quote before receipt. |
| EXAMPLE-QUOTE-02 | 102 | 102 | At arrival the venue can have a changed standing quote not yet received locally. |
| EXAMPLE-QUOTE-03 | False | False | A marketable fill is not delayed to the next quote update. |
| EXAMPLE-ASSIMILATION-01 | 0.5 | 0.5 | Identical evidence ID is assimilated once in this illustrative Gaussian model. |
| EXAMPLE-ASSIMILATION-02 | 0.5 | 0.5 | Duplicate input must not create a second independent observation. |
| EXAMPLE-GEOMETRY-01 | False | False | The original physical band does not include a point admitted only by a wider uncertainty region. |
| EXAMPLE-GEOMETRY-02 | True | True | A declared scenario region is a distinct event definition, not a retroactive physical touch. |
| EXAMPLE-VEGA-01 | 1000 | 1000 | USD per unit annualized IV fraction. |
| EXAMPLE-VEGA-02 | 10.00 | 10 | USD per one volatility percentage point. |
| EXAMPLE-VEGA-03 | -10.00 | -10 | A sold trade reverses the signed vega-flow contribution. |
| EXAMPLE-SKEW-01 | 0.06 | 0.06 | Put-minus-call skew uses a declared positive downside-richness convention. |
| EXAMPLE-SKEW-02 | 0.02 | 0.02 | Butterfly curvature is distinct from the skew slope. |
| EXAMPLE-TERM-01 | 0.14 | 0.14 | Interval total-variance difference is a variance proxy, not a difference of volatilities. |
| EXAMPLE-RISK-01 | 430 | 430 | Headroom subtracts current net loss and incremental stop/cost exposure once. |
| EXAMPLE-OI-01 | (80, 120) | (80, 120) | Synthetic no-exercise OI bounds do not identify a path or trade-level opening status. |
| EXAMPLE-NONFILL-01 | 0 | 0 | No fill creates zero trade P&L absent an explicit order cost; a missed winner is an alternative-policy diagnostic. |
| EXAMPLE-IV-01 | 0.40000000000000047 | 0.4 | Bisection inversion agrees with an independent ATM closed-form identity. |
| EXAMPLE-IV-02 | 0.40000000000000047 | 0.4 | ATM put/call symmetry under the same forward convention. |
| EXAMPLE-IV-03 | None | None | Below-bound quotes have no admissible IV. |
| EXAMPLE-IV-04 | None | None | A price at the strict upper bound has no finite IV in this convention. |

[Machine-readable results](design_examples.json). [Reproduction script](verify_design_examples.py).
