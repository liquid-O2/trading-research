# F01 literal partition admission: registered definition

This closes a specific opening F01/SR-F01 fault boundary. It is a literal
QuantPad MBP Parquet reference, under the originals and expected cases in
F01_SOURCE_CASES. Native/all-schema and incremental materializers retain their
own unclosed comparisons.

Inputs are one complete acquired Parquet file, an independently declared exact
Arrow schema, dataset/acquisition versions, an explicit historical latency
scenario and positive source-byte/row/output/chunk limits. A complete bounded
byte snapshot is hashed and retained before parsing; source locator metadata is
separate from same-content identity. An incomplete download suffix is rejected.
Full source snapshots deduplicate by content. They are small reference fixtures
and bounded cohorts; this does not authorize duplicating the entire raw archive.

Each physical `(row_group, row)` is decoded once, preserving every supplied
column. Unknown action/side remain unknown canonical fields. A decode contract
violation creates a rejected-row record with its physical address and raw Arrow
row. It cannot disappear from counts. Any rejection quarantines the partition
for semantic consumers, while retaining the complete decode/reject report.

Output chunks can exist before completion, but only an atomic final manifest
admits a partition. The manifest binds complete source hash, exact schema,
decoder/scenario, row-group counts, all chunk hashes and accepted/rejected
counts. Readers require that manifest, validate every chunk, counts and physical
row sequence before exposing an event, and reject quarantined or old-decoder
materializations. Same content at two paths has the same semantic identity;
both locators remain recorded. Different chunk layouts can have different
storage manifests but must reconstruct identical event IDs and fields.

Crash tests interrupt after a chunk and immediately before the final manifest.
Both leave no admitted partition. A restart with the same source recomputes the
literal result and publishes once. Changed bytes/schema/decoder/scenario change
identity and cannot reuse an old result. This reference does not claim
incremental checkpoint recovery or correction repair.

The first deterministic fixtures use at most 16 rows, 1 MiB source and 2 MiB
output per case. No real-market outcome is inspected. Expected assertions:
no partial publication; exact counts including rejections; zero-row admission;
same-content aliases; layout-independent event identity; preservation of a
correction field; corruption and changed-schema rejection; and explicit budget
failure without consumer-visible output. Native admission, projected views,
and cold/warm resource comparisons remain subsequent registered work.
