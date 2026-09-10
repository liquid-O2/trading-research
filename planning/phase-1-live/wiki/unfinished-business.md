# Unfinished business (nearest owed level)

## Definition
The nearest untested objective above and below price, drawn from a fixed candidate set: naked prior POCs `[VP2 p.6]`, fresh single prints and poor highs / lows `[TPO p.5, p.7, p.9]`, leftover Asia / London / prior RTH highs and lows `[FIND p.5, p.9]` `[TBR p.11]`, and single prints and balances as the destinations price trades between `[C3 p.6]`. Ethos names the objective before the session as the higher-timeframe level that is actually owed something `[ANAT p.10]` `[K10 p.12]`; Jumbo treats unfinished business as a target, not an entry `[FIND p.9]`. Excess marks finished business `[TPO p.6, p.9]`. Id `lvl.owed.nearest`.

## Citations
- Naked POC target list `[VP2 p.6]`; single prints and poor extremes as magnets, excess holds `[TPO p.5–7, p.9]`; objectives = single prints and balances `[C3 p.6]`; objective named, failure named `[ANAT p.10]`; yearly POC / HVN objective `[K10 p.12]`; leftover London / Asia highs as the draw, lines deleted once purged `[FIND p.5, p.9]` `[TBR p.11]` `[XF p.30, p.33]`; MPOC and landmarks as targeting areas `[MAMT p.15]`.

## Faithful object
`lvl.owed.nearest`: at each 5-minute step, the candidate set = {naked prior-session POCs (`value.kz`), unfilled single prints and unrepaired poor extremes (`value.tpo.rth.30m`), untested session extremes (Asia, London, prior RTH, overnight)}; each candidate carries its formation `known_at` and is retired at its first `t2` touch; the object = the nearest surviving candidate above and below, with type and distance in ticks and in units of the 6–9 range.

## Upgrades
- Candidate set with / without composite HVNs and `lvl.mpoc.eth`; distance normalized by `env.ev.mean60`.

## Outcomes
- Reach rate of the nearest owed level by 12:00 and 16:00, by type; distance distribution; used as the target definition wherever a recipe in `../RULES.md` names "the owed objective".

## Links
[tpo-ib-auction](tpo-ib-auction.md) · [value-and-profiles](value-and-profiles.md) · [composite-profiles](composite-profiles.md) · [session-fail-boxes](session-fail-boxes.md)
