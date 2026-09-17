"""P15-19 self-check (definitive-0002: the amended evaluation).

Independent of exits.py's aggregation: plain json/gzip/Decimal over the study's
own shards. Recomputes one central number, traces one exit to the entry run's
record and on to the P15-16A pairing bytes, and reconciles the trial ledger.
"""
import gzip, hashlib, json, sys
from decimal import Decimal
from pathlib import Path

R = Path(sys.argv[1])            # the evaluation attempt (results live here)
F = Path(sys.argv[2])            # P15-18 refinement evaluation attempt
# the per-day exit shards stay in the bound run root, named explicitly
RUN = Path(sys.argv[3]) if len(sys.argv) > 3 else R
results = json.loads((R / "EXIT_RESULTS.json").read_text())
fixed = json.loads((R / "FIXED_ENTRIES.json").read_text())
ledger = [json.loads(line) for line in (R / "EXIT_TRIALS.jsonl").read_text().splitlines() if line.strip()]

shards = {}
for day in fixed["dates_with_entries"]:
    path = RUN / "exits" / f"{day}.json"
    if path.is_file():
        shards[day] = json.loads(path.read_text())

# ---- 1. recompute one comparison's mean paired improvement ----------------
target = max(results["comparisons"], key=lambda row: row["eligible_test_days"])
rule, policy = target["entry_rule"], target["policy"]
holdout = results["holdout_excluded"]
diffs = []
excluded = 0
for day, shard in sorted(shards.items()):
    if holdout["start"] <= day <= holdout["end"]:
        excluded += 1
        continue
    rows = (shard.get("rules") or {}).get(rule)
    if not rows:
        continue
    if not all(row["e0_matches_entry_run"] for row in rows):
        continue
    ok = True
    e0 = Decimal(0)
    alt = Decimal(0)
    for row in rows:
        a, b = row["policies"]["E0"], row["policies"][policy]
        if not a.get("complete") or not b.get("complete"):
            ok = False
            break
        e0 += Decimal(str(a["net_points"]))
        alt += Decimal(str(b["net_points"]))
    if ok:
        diffs.append(float(alt - e0))
mean = sum(diffs) / len(diffs) if diffs else 0.0
print("RECOMPUTE")
print(f"  {rule} | {policy} over {len(diffs)} common complete days")
print(f"  mean paired improvement vs E0 recomputed {mean:.6f}  artifact {target['mean_diff']:.6f}"
      f"  delta {abs(mean - target['mean_diff']):.2e}")
print(f"  eligible days recomputed {len(diffs)}  artifact {target['eligible_test_days']}")
print(f"  hold-out days skipped by this recomputation {excluded} (artifact says {holdout['days_excluded']})")

# ---- 2. trace one exit to the entry record and the native pairing ---------
day, shard = next(
    (d, s) for d, s in sorted(shards.items()) if (s.get("rules") or {}).get(rule)
)
row = shard["rules"][rule][0]
print("TRACE")
print(f"  {rule} {day} entry {row['entry_id']}")
for policy_id in results["policies"]:
    body = row["policies"][policy_id]
    print(f"    {policy_id} complete={body.get('complete')} reason={body.get('reason')}"
          f" exit_at={body.get('exit_at_ns')} net={body.get('net_points')}")
e0 = row["policies"]["E0"]
side = int(row["side"])
fill = Decimal(row["fill_price"])
exit_px = Decimal(str(e0["exit_price"]))
cost = Decimal(row["round_trip_cost"])
delta = (exit_px - fill) if side == 1 else (fill - exit_px)
expect = delta - cost / Decimal(20)
print(f"  E0 net points recomputed {expect} artifact {e0['net_points']} equal {expect == Decimal(str(e0['net_points']))}")
print(f"  E0 reproduces the entry run's E0: {row['e0_matches_entry_run']}"
      f" (recorded {row['recorded_e0']['net_points']} at {row['recorded_e0']['exit_at_ns']})")

source = next(r for r in fixed["rules"] if r["candidate_id"] == rule)
job_path = Path(source["jobs_root"]) / "jobs" / day / (rule.replace(":", "--") + ".json.gz")
job = json.loads(gzip.open(job_path).read())
recorded = next(e for e in job["candidate"]["entries"] if e["entry_id"] == row["entry_id"])
print(f"  entry document {job_path.name} in {Path(source['jobs_root']).name}: fill {recorded['fill_price']}"
      f" stop {recorded['initial_stop']} objective {recorded['objective']}")
if job.get("pairing_baseline_path"):
    h = hashlib.sha256()
    with open(job["pairing_baseline_path"], "rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            h.update(chunk)
    print(f"  pairing baseline {Path(job['pairing_baseline_path']).name}"
          f" sha256 matches: {h.hexdigest() == job['pairing_baseline_sha256']}")

# ---- 3. the family is separately counted and rescues nothing --------------
print("SEPARATION")
print(f"  comparisons {len(results['comparisons'])} = {len(fixed['rules'])} rules x 4 non-baseline policies:"
      f" {len(results['comparisons']) == sum(1 for r in fixed['rules'] if r['candidate_id'] in results['per_rule']) * 4}")
print(f"  every comparison carries the entry stage's own disposition and entry_rescued false:"
      f" {all(row['entry_rescued'] is False and row['entry_stage']['unchanged_by_this_study'] for row in results['comparisons'])}")
entry_rules = json.loads((F / "SELECTED_RULES_BY_FOLD.json").read_text())
entry_dispositions = {
    role["candidate_id"]: role.get("disposition")
    for fold in entry_rules["folds"]
    for role in fold["roles"]
}
mismatched = [
    row["entry_rule"]
    for row in results["comparisons"]
    if row["entry_rule"] in entry_dispositions
    and row["entry_stage"]["disposition"] != entry_dispositions[row["entry_rule"]]
]
print(f"  entry dispositions unchanged by this study: {not mismatched}")
print("LEDGER")
print(f"  rows {len(ledger)}  unique {len({r['trial_id'] for r in ledger})}"
      f"  all with parent_trial_ids {all(r['parent_trial_ids'] for r in ledger)}")
print(f"  dispositions {dict((d, sum(1 for r in ledger if r['disposition'] == d)) for d in {r['disposition'] for r in ledger})}")
print(f"  e0 mismatches across the study: {sum(b['e0_mismatches'] for b in results['per_rule'].values())}")
