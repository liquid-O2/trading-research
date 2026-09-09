# Auction/flow source check 5 — retained test failure

The fifth registered check stopped before market-data scanning: 259 tests ran, with three failures and two errors. The attempt remains failed and consumed **38.988804 CPU seconds**, **47.278677 wall seconds**, **192,761,856 peak RSS bytes**, and **247,171 output bytes**. All earlier attempts remain counted. No source, statistics, Context or Location completion claim follows from this run.

The fast serializer rejected the existing `ValueArea` record nested in full time-at-price measurements. Its exact supported domain now includes that explicit record, with the same field names and rational JSON tags; arbitrary object conversion remains rejected. The complete canonical-byte comparison still applies.

Three new long-clock assertions used a pre-existing fixture helper with a 100 ns default source interval. It clipped later minute-scale observations before the new calculations received them. The helper now accepts the explicitly requested interval. The original expected rolling prices, bracket memberships and unpriced failure expectations remain unchanged.

The 70,003-row storage test called the value-hash API above its 65,536-row bound. It now compares every bounded logical block, alongside the full series comparison, original schema metadata and every floating-point bit. The original input population and expected values remain unchanged.

The combined corrections are being checked in [registered check 6](auction-flow-runs/c09887c082448be5af7e0fa23f4d880a545d83ea4f0c00fbff657dfed205660d/packet.json) under the same resources and [explicit check extension](../validation/AUCTION_FLOW_SOURCE_CHECK_EXTENSION_V2.json). This document does not promote that pending result.

Evidence: [supervisor receipt](auction-flow-runs/d7cd6334391607f91998ac381d759248234a7e24dcdcb1310816115962d03482/execution.json), [worker result](auction-flow-runs/d7cd6334391607f91998ac381d759248234a7e24dcdcb1310816115962d03482/worker.json), [complete test log](auction-flow-runs/d7cd6334391607f91998ac381d759248234a7e24dcdcb1310816115962d03482/worker.log).
