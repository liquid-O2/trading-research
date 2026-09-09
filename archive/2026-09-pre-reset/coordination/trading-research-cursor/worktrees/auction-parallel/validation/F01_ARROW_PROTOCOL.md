# Parquet field/type preservation: expectations before implementation

Opened 2026-09-06 after the native correction. This covers the remaining flat
Parquet physical profiles nominated by INV-01/04/05/06/09/11, not each domain's
economic or publication semantics. The supplied schema catalog contains 22
distinct field/type signatures, including dictionary strings, nullable numeric
fields, dates, ns/us UTC timestamps and trade/quote correction conditions.

Primary references: Arrow 25.0.1 [Parquet handling](https://arrow.apache.org/docs/python/parquet.html),
[timestamp representation](https://arrow.apache.org/docs/python/timestamps.html)
and [columnar validity/dictionary layout](https://arrow.apache.org/docs/format/Columnar.html).
The original source inventory and timestamp-conventions manifest remain the
source-specific time-profile authority. Storage units do not establish when a
strategy knew a value.

1. Register the entire serialized Arrow schema, including field/schema metadata,
   nullability, dictionary index/value types and timezone/unit. Two schemas whose
   long metadata differs after Arrow's display truncation must have different
   identities. `str(schema)` is a display, not a complete schema hash.
2. Preserve every column in IPC and a literal per-row field view. A timestamp
   at 1,234,567,891 ns stays that exact integer with its ns/UTC type. Date-only
   values stay epoch days; no midnight, localization or availability is invented.
   The decoder must not depend on a Python datetime conversion or pandas.
3. Preserve int8/16/32/64, uint32, bool, null, string/large_string, dictionary
   strings, date32 and timestamp ns/us. Float64 values retain their exact bits,
   including negative zero, infinities and distinct NaN payloads. Unknown types
   require registration and fail before any decoded prefix is emitted.
4. Null, a valid zero, a valid empty string and a valid dictionary value are
   distinct. Raw field decoding applies no price, rate, volume, option-side or
   timestamp sentinel meaning unless the source-specific adapter supplies it.
5. A partial multi-row-group read records each physical group/local row. Changing
   read batch size preserves source/row IDs and per-row values. Identical prints
   at different physical rows remain separate. Field, type, metadata or correction
   changes cannot silently reuse the old declared-schema view.
6. Explicit row and decoded-output limits apply to the diagnostic prefix. A
   record-count bound does not establish EOF or complete partition eligibility.
   Truncated containers fail explicitly within the attempted extent. All source
   bytes remain in place; diagnostic IPC is not a replacement raw archive.
7. Synthetic golden rows exercise every catalogued field/type signature and the
   discriminating values above. Bounded real prefixes then compare retained
   values to the fixed earlier audit and report each actual schema, field and
   sample extent. Synthetic schema coverage cannot certify 111 datasets.

Complete atomic MBP Parquet admission already has separate crash/count tests.
This step opens general raw field decoding. Wider complete/native admission,
domain meanings and downstream correction/replay remain separately required.

## Missing-profile supplement, registered before comparison

The original 216-row audit has no nonempty golden prefix matching the
normalized calendar's `symbol: null` / `timestamp[us, tz=UTC]` signature.
The original 21-profile result remains intact. A separately budgeted provider
reference nominated the lexicographically first matching file by exact catalog
signature, using at most five footers and three rows. The product raw-field
decoder was not invoked. Its 9,292-byte source snapshot and scalar results are
retained in `reports/f01-calendar-golden-capture.json`.

[The fixed expectation](golden/f01-event-calendar.json) records all eleven
fields of all three rows and independent epoch arithmetic. Compare these exact
types, values, column order, row addresses, schema and source identity with the
product decoder at batch sizes one and three. Require stable row IDs, valid
retained IPC, unchanged source and code, and 33 matching physical-field
expectations. Preserve `symbol = null`, `standard_release_time` and the null
release-update field without synthesizing receipt or publication knowledge.

The supplement runs only the missing profile. The coverage report references
the earlier 21-profile artifact and this new result separately; it must not
describe the combined evidence as one new 22-profile execution. Budget: 30 CPU
seconds, 60 wall seconds, 2 GiB address space, three rows per batch-size pass,
one source no larger than 1 MiB, and at most 2 MiB retained output.
