# P15-02 report

MarketView wraps native executions as columnar integer-tick arrays.
Unchanged baseline rules still call native_discovery.scan_branch.
Parity compared 60 dates in manifest order against run-1.0.1.
Jobs 3420, matches 3420, mismatches [].
Throughput n=20, CPU quota 17, MarketView median 12.972s p90 17.678s, replay median 140.972s p90 175.345s.
Quotes on MarketView are trade-synchronous BBO from T rows because mixed-action iteration raises on out-of-order timestamps.
Exchange-feed completeness remains unknown.
