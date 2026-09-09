# F02 / F02.PAYOFF source and expected-case review

Recorded 2026-09-06. This review covers the instrument definitions needed by
the opening NQ path and inventories the rest of the parent and child contract.
It does not certify the complete F02 service or its eight experiment phases.
The existing 247-test verification precedes this mapping. References to those
assertions are retrospective traceability; they are not preregistered tests.
The first table below preserves that earlier evidence state. The subsequent
[kernel batch evidence](../reports/f02-kernel-case-coverage.json) extends it
with 17 newly executed fixed tests in the 264-method combined passing run.
Expected extents absent from either record remain unrun.

## Definition, sources and alternatives

The whole F02 ten-part card, SR-F02, UP-F02, F02.PAYOFF and both complete P0–P7
phase tables have been reviewed. Identity includes provider, venue, instrument,
validity interval and definition version. Publication/receipt time determines
when a version can be used. Raw flow, valuation and execution have separate
eligibility. A display symbol, a root name or a current contract list cannot
replace a historical contract definition.

| Source route | Original passage reviewed | Consequence for F02 |
|---|---|---|
| CEX-16 | `sources/documents/conversations/conversation_export (1).md` 561–588 | The NDX/QQQ hierarchy is an earlier hypothesis. It supplies neither a contract identity nor permission to equate index, ETF and future price units. |
| CEX-23 | Same conversation 817–1021, within the prior complete 750–1021 reading | Acquisition plans and progress are dated statements. The supplied catalog controls which products and schemas are present; a requested parent chain is not evidence that its underlying future tape was acquired. |
| CEX-10, conversation lineage | Same conversation 214–416 | Prior subscription and intended-schema claims do not certify contract fields, rights or historical publication. |
| DRF-A06 | `sources/documents/conversations/Design robust feature levels.md` 114, read with 88–114 | NDX/NDXP style, settlement and multiplier require product/series evidence. A common expiry date or numeric strike does not make AM and PM contracts interchangeable. |
| DRF-A02, conversation lineage | Same document 88–96 and 195–236, both read | Publisher, exchange, instrument and side fields are not participant identity. Aggregated participant-origin feeds are a separate, unacquired product; no dealer identity enters this registry. |
| INV-01–08 | All 765 lines of `sources/documents/inventory/DATA_INVENTORY.md` | Keep outright, continuous-contract, option-parent, ETF and context acquisitions distinct. Missing option BBO, cash index observations, depth, deliverables or parent futures cannot be inferred from other files. Excluded partial downloads remain excluded. |
| INV-09 | Inventory 20–34 and complete `data/manifests/timestamp-conventions.json` | Preserve each physical epoch unit. Expiration, activation, event, provider receipt and actual strategy receipt remain separate fields. |
| INV-10 | All 91 lines of `sources/documents/inventory/databento_pull_list.md` | Requested products and old estimates remain acquisition history, not present instrument eligibility. |
| INV-11 | Complete DATA_CAPABILITY_AUDIT; original bounded audit structure and reconciliation | Prior representative schemas have unequal depth. The 216 original sample records have not each been re-certified here. Actual operation/cohort cases remain required. |
| INV-12 | Source findings and DATA_CAPABILITY_AUDIT hardware observation | The original hardware command transcript was not located. Runtime costs must be measured under the registered worker limits. |

Shared original readings are recorded once in
[F01_SOURCE_CASES.md](F01_SOURCE_CASES.md). This table records their additional
F02 implications. Original option product specifications, adjusted-deliverable
notices and all-date series joins still need their own verification before
those valuation adapters are admitted.

The required comparison stages remain separate:

1. Display-symbol/manual-multiplier source comparator, on cases where its
   meaning is recoverable; unsupported identities produce an explicit failure.
2. Curated authoritative definitions with knowledge-time and validity-time
   joins, compared with the provider mapping on the same instruments.
3. Compiled payoff, price-domain, tick, currency and sensitivity kernels versus
   independent hand calculations and valid inverse paths.

An automated reconciliation or learned match may flag an ambiguity; it cannot
authorize a trade. No compiled-kernel speed or downstream gain is established
by the current exact-arithmetic helper tests. Reciprocal and conditional
inverse mappings must remain different operations.

## Initial expected cases and prior evidence

In the table, `RD` means `tests.test_rolls_definitions`, `FD` means
`tests.test_foundations`, `BR` means `tests.test_batch_review`, and `DF` means
`tests.test_decoder_faults`. Every listed method passed in verification
`9c2b8b0bc45f77cd3254387de9eb8fdcb3f344200ffaf9f979f2b8e50518068e`.
The linked machine record expands the names and verifies membership in that
immutable result. A partial method does not close the broader row.

| Case | Fixed input and expected result | Executed extent / remaining work |
|---|---|---|
| F02-01 MISSING-TERMS | A valid NQ outright definition has no multiplier. Preserve identity, raw fields and raw-flow eligibility; block dollar valuation and orders. | `RD.DefinitionTests.test_missing_multiplier_preserves_raw_flow_but_blocks_execution` passes. Ten selected actual partitions contain 2,579 such rows; this is historical, partition-specific evidence. |
| F02-02 EXTERNAL-TERMS | A separately dated NQ multiplier becomes known after a decision. The old cut remains blocked; a later join may use it. If raw multiplier is 50 and the NQ evidence says 20, reject the conflict. | `RD.DefinitionTests.test_external_terms_must_be_available_match_raw_terms_and_preserve_unused_field_identity` passes. Actual NQ product evidence is separate from raw tick fields in `configs/product-terms.json`. No ES historical join is supplied there. |
| F02-03 EXACT-NQ-DOLLARS | A 0.25 point NQ move at 20 USD/point is 5 USD per mini. Long +1 point and short −1 point are +20 USD. Off-tick 20000.251 is rejected; Decimal precision must not change the answer. | `FD.ArithmeticAndClockTests.test_ticks_use_exact_ratio_not_decimal_context_rounding` and F02-01's method pass. This is one outright unit; no extra units or micros are introduced. |
| F02-04 EXACT-ES-DOLLARS | A dated 0.25 point ES tick at 50 USD/point is 12.50 USD. The full independent ES path must agree through order and account cash. | Required expected arithmetic; a dated ES terms join and this complete assertion chain are unrun. A reference constant alone is insufficient. |
| F02-05 ID-REUSE | The same provider/venue/numeric ID is assigned to a different contract in a later disjoint interval. Each cut resolves the correct lifetime; equal-looking prices must not join across lifetimes. | Unrun explicit two-lifetime fixture. Existing namespace and corrected-version tests are related evidence, not this case. |
| F02-06 LATE-CORRECTION | An unknown definition valid at 15 is corrected at knowledge time 20. A decision at 15 keeps the unknown version; research truth or a later query may see the correction. | `FD.GraphAndGeometryTests.test_definition_revision_is_known_time_and_use_specific` passes. Durable registry restart, suffix deletion and affected order/valuation replay remain open. |
| F02-07 FIELD-IDENTITY | Change a supplied but currently unused field without changing numeric terms. The definition version must change; no old cache may claim the new bytes. | `RD.DefinitionTests.test_external_terms_must_be_available_match_raw_terms_and_preserve_unused_field_identity` passes for raw-field identity. Full downstream invalidation for every contract field remains open. |
| F02-08 DELETION | A known security deletion retires the affected valid interval at its availability time and cannot resurrect an older tradeable definition. | The outright adapter explicitly rejects deletion in `RD.DefinitionTests.test_spreads_deletions_sentinels_and_bad_clocks_are_explicitly_unavailable`. Applying a retirement event to the registry is unimplemented; rejection is not retirement support. |
| F02-09 SPREAD-AND-LEGS | A UDS or multi-leg instrument, including one missing leg, cannot use the outright payoff. Preserve its raw signed price and identity; dispatch to explicit unsupported valuation until every leg and ratio is known. | The same RD method rejects spread input. `DF.NativeSemanticFaultTests.test_negative_spread_price_and_distinct_price_timestamp_sentinels` preserves −1.25. No compiled spread payoff or incomplete-leg resolution has run. |
| F02-10 AM-PM | Two options share root/date/strike/right but settle AM versus PM. They need distinct identities, expiry clocks and settlement inputs; a PM observation cannot settle the AM contract. | Unrun option style/series integration. Official dated product and holiday examples are required before admission. |
| F02-11 MONTHLY-WEEKLY | Monthly and weekly symbols that share a calendar date must resolve by explicit series and settlement rules, not a suffix heuristic. | Unrun. In particular, do not decode a display `C0000` into zero strike without source fields. |
| F02-12 EXPIRY-CLOCK | At expiry minus one supported time unit a contract can still be valid; at expiry it cannot open new risk. Holiday revisions apply only after publication. | `RD.RollTests.test_expired_outright_is_excluded_without_requiring_nonexistent_later_volume` passes for expired outright selection. Exact option AM/PM and holiday-clock cases remain open. |
| F02-13 VARIABLE-TICK | Values on either side of a source-defined option premium threshold use their own tick grid, including the exact boundary. Off-grid values fail under the correct style. | Unrun variable-tick kernel and dated product tables. The outright constant tick fixture does not cover this. |
| F02-14 ADJUSTED-DELIVERABLE | A valid adjusted option can have a nonstandard multiplier, shares and cash. Known terms select its exact payoff; unresolved terms yield unsupported, not a standard 100-share assumption. | Unrun adjusted-deliverable adapter, primary notices and independent payoff fixtures. |
| F02-15 MULTIPLIER-REVISION | A multiplier change creates a new version at its own knowledge/effective times. Earlier decisions and closed trades retain their original terms; later risk uses the applicable version. | Raw/external conflict rejection is covered by F02-02. Legitimate change plus historical account reconstruction remains unrun. |
| F02-16 SPLIT-COORDINATES | A published 4:1 split cannot rewrite a pre-effective decision. At the effective cut, 400 maps to 100 in the explicitly adjusted display; option strikes and valuation still use compatible raw coordinates and actual deliverables. | `RD.RollTests.test_future_split_does_not_rewrite_features_or_option_strike_coordinates` passes for display timing and raw-coordinate rejection. Adjusted option payoff and dividend cases remain open. |
| F02-17 OPTION-UNDERLIER | An option references a particular future that differs from a root's currently active future. Use that exact contract and expiry; replacing it with the active root blocks valuation. | Unrun option-underlying-future join. NQ.OPT activity is not NQ.FUT outright volume. |
| F02-18 VIX-UX | A VIX index observation and a dated volatility future remain different instruments and price domains. An option model must use its specified settlement/underlier, not whichever price exists. | Unrun style-specific valuation/settlement adapter. Acquired daily index data do not fill missing futures quotes. |
| F02-19 RECIPROCAL-INVERSE | For an explicit deterministic coordinate y=2x, valid inverse x=y/2 round-trips. A noisy conditional estimate E[y\|x] has no automatic reciprocal conditional estimate E[x\|y]. | Unrun compiled mapping-domain and independent inverse fixtures. Dimensional conversion helpers alone are not statistical inverse models. |
| F02-20 TIME-DERIVATIVE | With remaining time τ=T−t and fixed T, dV/dt=−dV/dτ. A changed expiry/calendar is a changed contract assumption; it cannot be hidden in the derivative sign. | Unrun payoff-kernel derivative and holiday-clock integration. |
| F02-21 INVALID-FIELDS | Missing/undefined expiry or required provider clock, unsupported class or ambiguous symbol cannot silently become a tradeable outright. Preserve the physical fields for diagnosis. | `RD.DefinitionTests.test_spreads_deletions_sentinels_and_bad_clocks_are_explicitly_unavailable` passes for its listed inputs. Full native definition semantic adapters remain open. |
| F02-22 INFORMATION-UNITS | Hedge sensitivity expressed as mini-equivalent information is not an allowed order quantity. Currency and contract quantities cannot be added. | `FD.ArithmeticAndClockTests.test_information_mini_equivalent_is_not_order_quantity` and `BR.FoundationReviewTests.test_integral_quantities_are_independent_of_decimal_precision` pass. Currency conversion with dated FX and compiled sensitivity kernels remains open. |
| F02-23 ROLL-UNIVERSE | Prior-session volume is required for every eligible competitor in the declared universe, at the selection cut. Missing competitor history is not zero; the tape of an acquired calendar-front contract is not a complete parent universe. | `RD.RollTests.test_previous_volume_ties_and_universe_scope_are_frozen_at_cut`, `RD.RollTests.test_missing_competitor_duplicate_definitions_and_mismatched_sessions_cannot_select` and `tests.test_e0.CohortTests.test_exact_reference_cannot_adopt_acquired_universe_as_complete_parent` pass. Actual exact-E0 universe/volume dependency is in the opening gate report. |

## Remaining phase work

The later [consolidated kernel review](F02_KERNEL_BATCH_REVIEW.md) addresses
retirement and serialized restart, exact NQ/ES and option payoff equations,
AM/PM fixing coordinates, adjusted share/cash and exact future delivery,
piecewise ticks, FX/unit guards and deterministic inverse/time derivatives.
Its machine record maps the new named assertions to all 23 expected rows;
each mapping remains partial. The original table's statements of unimplemented
reference arithmetic describe the state before this batch. Dated product,
native-series and complete downstream comparisons remain outstanding.

P0/P1 still require the unrun cases, domain/adapter manifests and original
product evidence above. P2 requires the actual curated/provider/compiled
comparisons and measured lookup costs. P3 needs operation-specific coverage
and numerical error across supported styles and dates; deterministic identity
must not acquire a learned confidence score. P4 preserves source, corrected
and compiled stages with common-input controls. P5 replays affected O/P/X
consumers and reports changed/missing candidates. P6 depends on eligible
complete economic policies. P7 requires future captured receipts and parity.

The exact NQ path does not wait for an unneeded option payoff adapter, but it
must pass its own identity, universe, session and data gates. F02 and
F02.PAYOFF remain incomplete, and neither receives a whole-unit verification
or research disposition from this review.
