# Native field preservation: expected results before implementation

Opened 2026-09-06. This extends F01-GOLDEN-SCHEMAS, SENTINELS,
UNKNOWN-ENUM, SCHEMA-DRIFT and RESOURCE from F01_SOURCE_CASES. It is a
bounded reference decoder review, not option valuation or a complete data gate.

The existing reader preserves record bytes but exposes a selected MBP field
list. Statistics quantity/reference/update fields, bar OHLCV and most instrument
definition fields are missing from that list. A raw byte blob alone is not a
typed field-preservation result.

## Declared profiles and evidence

Use DBN versions 1, 2 and 3 as encoded, with databento-dbn 0.69.0. Register the
physical field layouts for TradeMsg, MBP1Msg, OHLCVMsg, the old and current
StatMsg, and the three InstrumentDefMsg layouts. Preserve padding, fixed-size
character arrays and an optional appended ts_out. Reject an unregistered class,
changed layout, version/class mismatch or header/body length disagreement.
Other schemas require their own registration; this scope does not admit them.

Primary references checked: [DBN encoding and version changes](https://databento.com/docs/knowledge-base/new-users/dbn-encoding),
[statistics](https://databento.com/docs/schemas-and-data-formats/statistics),
[instrument definitions](https://databento.com/docs/schemas-and-data-formats/instrument-definitions),
[common fields](https://databento.com/docs/standards-and-conventions/common-fields-enums-types).
The installed provider's physical `_dtypes` and native record constructors are
an additional implementation reference, not independent market validation.

## Fixed expectations

1. A hand-packed little-endian MBP record has its action/side bytes at offsets
   28/29, flags/depth at 30/31, provider receipt at 32, signed delta at 40 and
   venue sequence at 44. BBO begins at 48. Preserve unknown action/side bytes;
   canonical decoding marks them unknown. No enum getter may erase or reject
   an otherwise retainable byte. ts_out is separate from strategy receipt.
2. Statistics in versions 1/2 has signed 32-bit quantity, versus signed 64-bit
   in version 3. The corresponding signed maximum is missing; maximum minus
   one remains an exact integer. Do not apply a 64-bit sentinel to the old
   field. Preserve ts_ref, stat_type, update_action, stat_flags and padding.
   A delete remains a delete; this layer does not assimilate OI or settlements.
3. Prices use exact 1e-9 scaling, including negatives. Price max and timestamp
   max are distinct missing values. Explicitly supported definition multiplier
   and quantity sentinels become typed missing while raw integers survive.
   Sequence max, zero quantity and bar volume max are not automatically null.
   No generic 'every maximum integer is missing' rule is allowed.
4. Hand-specified bar open/high/low/close and volume must survive exactly. A
   bar's physical timestamp does not establish its availability or path order.
5. Definition fixtures cover the old and current layouts. The v3 64-bit raw
   instrument ID and leg fields survive without truncation. A missing native
   contract_multiplier is not the product's dollar-per-point multiplier; no
   external default is inserted. Expiration storage does not certify exact
   venue expiration precision or an execution boundary.
6. Reassemble every raw physical field to the original complete record bytes,
   including unknown characters, NUL tails, reserved bytes and ts_out. Compare
   all available integer fields with the provider's independent native getters,
   plus the hand-packed known values. Preserve all metadata attributes and
   original metadata bytes, including mappings and ts_out declaration.
7. An incompressible valid fixture exceeds the compressed-byte budget before
   the requested prefix ends: explicit resource/dependency failure, no valid
   EOF claim. A smaller requested prefix succeeds. A compressed-budget failure
   is separate from the already-tested decompressed budget and corrupt frame.
8. Bounded real prefixes nominated from the existing first/middle/last header
   audit compare against its recorded values, retain exact raw record hashes,
   and report source/version/field extents and actual resource use. They do not
   certify the suffix, full cohort, source receipt or executable eligibility.

Typed extraction returns only fields with explicit rules. All other raw
fields remain available as raw values and cannot be given invented meanings.
Changing the raw field set changes decoder identity; previous materializations
and book checkpoints require replay under an explicit version change.
