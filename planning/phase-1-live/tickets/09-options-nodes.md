# 09 — Options nodes (four index products)

**Outcome.** Native strike nodes on **NDX, NDXP, SPX, SPXW**. This ticket is options-only.

**Wiki.** `wiki/options-nodes.md`, `wiki/data-coverage.md`.

**Definition → compute → pass.**
1. Native rows: `value.node.oi.{ndx,ndxp,spx,spxw}.top3` and gamma twins at 09:25. Variants: QQQ, SPY, NQ.OPT.
2. Each row: product, native, mapped_nq, map_known_at, OI_vintage.
3. Cash NDX/SPX minutes are not inputs. Missing quotes = coverage hole, not drop the product.
4. Rows `value.dealer.inventory`, `value.hidden.book`, `value.skylit.*` printed `not-measurable` / `deferred`.
5. Pass command: `... run_phase1_objects.py report --family options`

**Acceptance criteria.**
- Options report lists NDX, NDXP, SPX, SPXW as separate product rows; QQQ/SPY/NQ.OPT present as named variants.
- Every printed node row has product, native, mapped_nq, map_known_at, OI_vintage.
- A product with missing quotes still prints a row; coverage flags the hole; the product is not omitted.
- No row assumes cash-index minutes.
- The three not-measurable / deferred rows exist with that status.

**Blocked by.** 01 (session clock) only.
**Out of scope.** VP / absorption / BigTrades (ticket 06); Skylit engines as a build.
