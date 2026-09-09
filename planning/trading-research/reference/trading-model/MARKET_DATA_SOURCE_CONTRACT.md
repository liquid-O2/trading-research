# Market-data source contract: MBP-1, derived BBO and event semantics

Updated 2026-09-06 in response to USR-20260906-06. This is a binding clarification of F01/F04/F05/F06, M01/M02/M09/M10/M13, P05 and E0. It specifies future implementation. The existing plan already required MBP-1 flow and quote events, but its repeated use of “BBO” did not adequately distinguish the observed book state from a sampled vendor schema, and its flag handling was insufficiently explicit.

## Source hierarchy

**Use acquired MBP-1 as the primary NQ/ES event source wherever its cohort passes validation.** Preserve every supplied field and native record order. Derive the current best bid/offer state, eligible trade stream and causal aggregates from that source. A model may read a compact projection; the canonical event ledger must retain the richer inputs for other consumers and reproducible replay.

| Term | Meaning in this plan | Permitted use |
|---|---|---|
| MBP-1 | Event stream containing trades and changes at the best price level | Primary available futures tape and book source; trade flow, event intensity, visible pressure and execution replay |
| BBO state | Best bid/ask prices and displayed sizes at a specified information or venue cut | A derived view of validated MBP-1 for pricing, spread, imbalance, contact observations and execution |
| Databento `bbo-1s` / `bbo-1m` | Vendor interval-sampled schemas | Explicit coarse-data comparison or source-specific fallback; cannot establish every intervening trade, quote transition or fill |
| Standalone trades | Independently acquired trade records | Reconciliation reference or declared alternate trade source; never added to the same trades embedded in MBP-1 |
| Options minute quotes | The actually acquired option snapshots | Source-specific surface/Greek observations, with their own timing and coverage; futures MBP-1 cannot supply missing option quote events |

Databento documents MBP-1 in book-update space, TBBO in trade space and interval BBO in sampled time space. The latter views can be derived from MBP-1. This plan's NQ/ES references to BBO mean the derived **state** unless an experiment explicitly names a sampled schema. [Provider comparison](https://databento.com/docs/faqs/difference-between-mbp-and-tbbo).

## Fields actually present in this workspace

The new [read-only audit](review/mbp-review/mbp_contract_audit.json), produced by [audit_mbp_contract.py](review/audit_mbp_contract.py), inspected all 167 NQ/ES MBP Parquet footers and selected 86,016 records from 15 files across five futures families. It is a field/flag audit, not a complete reconstruction or gap-recovery test.

| Archive | Completed check | Available fields and limitation |
|---|---|---|
| NQ QuantPad MBP-1 | All 142 footers; row prefixes in three selected files | Uniform 11-field schema: `t`, `action`, `side`, `price`, `size`, `bid_px`, `ask_px`, `bid_sz`, `ask_sz`, `instrument_id`, `flags` |
| ES QuantPad MBP-1 | All 25 footers; row prefixes in three selected files | Same 11 fields; discontinuous date cohort described in DA-02 |
| HG, NKD, SI native Databento MBP-1 | First/middle/last file per family, first 4,096 records each | Event and provider-receive clocks, sequence, publisher, action, side, depth, price/size, flags, sending-time delta, best prices/sizes and best-level order counts |

The NQ/ES exports preserve actions, reported sides and flags. They omit separate `ts_recv`, exchange sequence, best-level order counts, publisher and `ts_in_delta` columns present in the sampled native encoding. Do not invent these from the generic MBP-1 specification, substitute another asset's fields, or discard the useful fields that are present. Preserve the acquisition-level publisher provenance and validate the meaning/scale of `t`. Provider capture time in native DBN is distinct from receipt by our eventual strategy. [Native field reference](https://databento.com/docs/schemas-and-data-formats/mbp-1).

## Event interpretation and quality state

Keep `raw_action`, `raw_side`, `raw_flags`, normalized action, reported aggressor, quote-state association, decoder/version and source-row address. Decode combined flag values with bitwise masks. Their use is schema/provider/version specific. The following operational rules are design decisions, informed by the [official field definitions](https://databento.com/docs/standards-and-conventions/common-fields-enums-types).

| Input | Required interpretation and downstream behavior |
|---|---|
| Trade action `T` | `B` means buying aggressor; `A` selling aggressor; `N` unknown. Count eligible trade volume once. Keep unknown volume in totals and uncertainty. |
| Add/Modify/Cancel | Side describes the affected resting side, not aggressive buying/selling. Preserve event type and visible before/after state. MBP-1 is insufficient to identify individual orders or gross hidden replenishment. |
| Clear `R`; recognized no-action `N` | Clear invalidates previous book state; no-action may convey metadata. Support only actions documented for the declared archive version; unknown enums remain explicit. |
| `F_LAST`, 128 | Retain instrument-event boundary information; never use it as a trade-inclusion filter. Apply the provider's MBP normalization semantics below. |
| `F_SNAPSHOT`, 32 | Distinguish replay/initialization from new market activity. Do not turn initialization adds into fresh buying pressure or reset a quote's economic age to its replay time. |
| `F_BAD_TS_RECV`, 8 | Provider receipt timing is unreliable; dependent latency claims require a separate uncertainty scenario. |
| `F_MAYBE_BAD_BOOK`, 4 | Invalidate trusted book-derived execution/pressure state pending documented recovery. Preserve observed trades, but mark incomplete flow coverage across the gap. A missing book does not become valid because price looks plausible. |
| `F_TOB`, 64; `F_MBP`, 16 | Respect the source's aggregate-message semantics; do not interpret aggregate size as an individual order or sum it blindly as new liquidity. |
| Publisher-specific bit, 2 | Preserve and resolve against the source/version supplement. The sampled native files contain this bit; its historical GLBX interpretation remains a certification item. It is not automatically a directional signal or corruption flag. |

**MBP-1 is already normalized.** Databento's CME documentation says its MBO event-boundary handling is accounted for when creating MBP-1 and trades; it does not require users to rebuild MBO or drop every MBP record lacking `F_LAST`. In this audit, 7,833 of 7,878 selected trade records lack that bit. Filtering to `flags == 128`, or even requiring `flags & 128` for trades, would destroy the tape. Retain provider sequence/storage order and the documented relation between a trade's attached pre-trade BBO and later book updates. Do not subtract trade size from a supplied quote and then subtract it again when the corresponding book change arrives. Exact intrabundle fill ambiguity stays explicit. [CME normalization](https://databento.com/docs/venues-and-datasets/glbx-mdp3).

The selected NQ file `2021-02-08.parquet`, row group 88, contains a 4,096-row prefix entirely carrying bit 4, via values 4 and 132. These are bounded sample counts, not archive prevalence. A later book recovery cannot reconstruct missing trades; continuous CVD/profile completeness needs its own recovery/reset policy. Native prefixes also contain initialization flags 168. The previous two-hour trade equality audit establishes equality of observed selected streams, not completeness through every data gap.

## Features and controlled comparisons

| Consumer | Information retained from MBP-1 | Comparison and acceptance question |
|---|---|---|
| M01/M02/M04/M05/M13 | Trade aggressor, quantity, price, time/order, quality; ordinary and cohort CVD OHLC, volume/delta profiles and footprint | Do reported-side event measurements reconcile exactly, and improve downstream forecasts relative to coarse proxies on the same dates? |
| M09/M10 | Quote prices/sizes; eligible action/side sequences; add/modify/cancel rates, OFI, spread/depletion/recovery and trade intensity | Compare quote-state-only, trade-only, combined event-type features and interaction models on matched information cuts. Gains must survive quality masks and latency. |
| Context and Location | Causal summaries of flow, liquidity, effort/progress and profile geometry | Test incremental range/auction/control, reach, rejection/continuation and candidate-value predictions. Detailed Response is not a prerequisite for these inputs. |
| P05/P06 and risk | Native validated quote transitions/trades and explicit gaps | Replay the standing venue BBO at order arrival; retain intervening events for protection and outcomes even when candidate scoring occurs once per minute. |
| Later Response | Ordered flow and visible quote changes with complete provenance | Evaluate sequence value after Context/Location baselines, preserving delay, missed winners, non-fills and adverse selection. |

E0 keeps its transparent price-only decision rule and one-minute candidate scoring as a reproducible control. Its ingestion, order/protection replay and future-path observations use the full eligible MBP-1 stream. Richer MBP features are measured early in B02 and evaluated through the registered M/C/L/P refinements. Distinguish **richer input features** from **faster decision cadence**: first compare features at identical cuts, then vary cadence with identical inputs and a refitted/calibrated policy. Quality rules and the one-mini/account constraints remain binding in every tradable comparison.

## Required implementation checks

Use the existing F01.DECODER, F05.CROSS_VENDOR, F06.GAP_RECOVERY, M01.SIGN_RESET, M09.RECOVERY and P05.CLOCKS experiments and their P0–P7 phases. Add these explicit cases to those existing units:

- Round-trip all supplied columns and enum representations; native action/side enums must normalize to their documented characters, not unexplained ASCII numbers.
- Reconcile embedded and standalone trades with multiplicity, flags, unknown side and raw-row identity; include trades without `F_LAST` and trades without a price change.
- Exercise combined flags 132 and 168, observed publisher-specific flags, clear/snapshot/restart, and a missing interval; distinguish book recovery from unrecoverable flow-history loss.
- Compare the provider-normalized BBO state at identical cuts, including pre-trade snapshots and subsequent changes; prevent double depletion and future quote substitution.
- Change or remove information available only after a decision and require the same earlier decisions. Test a native quote move and protective event between two minute scoring cuts.
- Run per-year/session/roll/auction quality and reconciliation cohorts before extending to the intended full history. Report excluded/unknown durations and zero-trade days in their proper denominators.

The audit above has executed only bounded reads and counting. These reconstruction, feature, prediction and trading-system checks remain to be implemented and run.
