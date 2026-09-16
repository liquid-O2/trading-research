# P15-19 exit study — rehearsal-0001. One line per decision.

**Rehearsal.** The frozen entries come from the P15-18 *rehearsal*
(`P15-18/d183bbbaa3e5b556/attempt-0001`), whose allowlist comes from the P15-17 rehearsal against the
uncorrected P15-16A pairing. No disposition here is a research finding. The definitive study points the
same two functions at the definitive breadth and refinement roots.

## Boundary

- The exit study is a separately counted decision family. It runs after entry selection is frozen, holds
  those entries, their sizes, costs and initial structural stops constant, and compares E0-E4 on them.
  It cannot promote or rescue an entry candidate: every comparison carries the entry stage's own
  disposition unchanged and `entry_rescued: false`, and a test constructs a rejected entry rule whose E2
  is hugely better and asserts the entry verdict does not move.

## The frozen entries

- `exits.selected_entry_rules(refinement_root, breadth_root)` reads P15-18's SELECTED_RULES_BY_FOLD.json:
  a `refined_selected` fold contributes the refined rule (entries in the refinement run), a
  `retained_parent` fold contributes the breadth parent (entries in the breadth run), and an executed
  combination contributes itself. 17 rules in this rehearsal.
- The entries themselves are the rows the entry run already recorded in each job document: entry id,
  side, fill clock and price, initial stop, objective and round-trip cost. Nothing is re-scanned, so the
  study is a function of the two run roots.
- The job record does not carry the episode's source deadline. Rather than assume it never binds, the
  study recomputes E0 from the reconstructed entry and compares it with the E0 the entry run wrote; a
  mismatch marks that day unusable for the paired comparison and is counted
  (`e0_mismatches`). A binding source deadline would show up here rather than silently biasing E0.
- `freeze_entries` finds the days that carry an entry from the entry runs' daily shards (cheap) and falls
  back to reading the job documents when a shard is missing -- a missing input is never read as "no
  entry" (tested both ways).

## The run

- Measured first: one account day costs 9.1 s cold and 0.75-3.1 s warm in the same process (tape load
  plus five policies over that day's entries), peak RSS 0.58 GB.
- cgroup usage read before each launch; 4 workers (the definitive breadth run attempt-0003 is running
  beside this one at 17 workers), measured 2.1 GB for the whole pool against the 12 GB ceiling.
- 1,680 days carry at least one frozen entry, 9,562 entries over 17 rules. One shard per day under
  `exits/<date>.json`, a checkpoint per day, resume by checkpoint, failures recorded with their reason.

## Results (rehearsal)

- 1,680 account days carried a frozen entry; 9,562 entries over 17 selected rules; 0 failed dates;
  813 s on 4 workers (`PROGRESS.json`, `RUN_COMPLETE.json`).
- E0 recomputed from the frozen entries reproduces the entry run's own E0 exit and net points on every
  one of the 9,562 entries (`e0_mismatches: 0`): the reconstruction loses nothing, and no source
  deadline bound ahead of the 60-minute expiry anywhere in this population.
- 68 comparisons (17 rules x E1-E4). None clears the promotion gates. Mean improvement against E0 over
  the rules: E1 +0.04, E2 +0.38, E3 +0.42, E4 -0.14 net points per common complete day. The largest
  single comparison, KEANI E3 at +18.8 [3.8, 33.8], rests on 14 days and fails the support gate.
- Dispositions over the 68 ledger rows: 47 retained_baseline, 13 rejected_by_evidence,
  8 inconclusive_support. Every row carries `parent_trial_ids` pointing at its entry rule's trial
  (P15-18 for refined and combined rules, P15-17 for a fold that kept its breadth parent).
- The blind hold-out (2026-04-01..2026-09-03) enters no comparison: 112 hold-out days are excluded by
  the fold trim, of which 105 carry a frozen entry and a shard in this study.

## Self-check (evidence in this directory)

- Independent recomputation (`SELF_CHECK.txt`, `self_check.py`, plain json/gzip/Decimal): the E2-vs-E0
  mean paired improvement of `SIRES:absorption_reward_retest:M1:max_prior_contacts=0` over 898 common
  complete days recomputes to 0.016425 against the artifact's 0.016425 (delta 0).
- Native trace: entry `b02:SIRES:absorption_reward_retest:short:1578265714558414311` on 2020-01-06 --
  all five policies exit on the stop at the same batch for -2.50 net points; the E0 number recomputes
  from fill, exit and commission; the entry row matches the P15-18 job document (fill 8756.25, stop
  8758.25, objective 8746.25); that document's pairing baseline sha256 recomputes from the P15-16A bytes.
- Separation: 68 = 17 rules x 4 non-baseline policies, every comparison carries the entry stage's own
  disposition with `entry_rescued: false`, and no entry disposition differs from P15-18's.
- Tests: each policy against its scalar reference on one tape, the five policies' contract differences
  (E1/E0/E2 deadlines, E3/E4 stop moves that never loosen, the gap fill below a jumped stop), the frozen
  entry construction, the retained-parent source, the missing-shard fallback, the hold-out control and
  the "cannot rescue an entry" negative control.
