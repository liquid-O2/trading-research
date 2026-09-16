"""P15-18 rehearsal self-check.

Independent of refinement.py's arithmetic: plain json/gzip/Decimal, reading the
refinement run's own artifacts. Recomputes one central number, traces one native
output, and reconciles the proposed trials against the ledger.
"""
import gzip, hashlib, json, sys
from decimal import Decimal
from pathlib import Path

R = Path(sys.argv[1])          # refinement run root
B = Path(sys.argv[2])          # breadth run root (the allowlist's home)
SPLITS = Path(sys.argv[3])

bank = json.loads((R / "REFINEMENT_BANK.json").read_text())
folds = json.loads(SPLITS.read_text())["outer"]
manifest = json.loads((R / "MANIFEST.json").read_text())
ledger = [json.loads(line) for line in (R / "TRIALS.jsonl").read_text().splitlines() if line.strip()]
rules = json.loads((R / "SELECTED_RULES_BY_FOLD.json").read_text())

_CACHE = {}


def rows_for(candidate_ids, days):
    wanted = set(candidate_ids)
    out = {cid: {} for cid in wanted}
    for day in days:
        cached = _CACHE.get(day)
        if cached is None:
            path = R / "daily" / f"{day}.json"
            cached = _CACHE[day] = (
                {r["candidate_id"]: r for r in json.loads(path.read_text())["rows"]}
                if path.is_file()
                else {}
            )
        for cid in wanted:
            row = cached.get(cid)
            if row is not None:
                out[cid][day] = row
    return out


# ---- 1. the contract's caps and neighbourhoods hold in the executed bank ----
per_fold_family = {}
for fold in bank["folds"]:
    for family in fold["families"]:
        attempted = [row for row in family["neighbors"] if row["status"] == "attempted"]
        per_bank = {}
        for row in attempted:
            per_bank[row["bank"]] = per_bank.get(row["bank"], 0) + 1
        per_fold_family[(fold["outer_fold"], family["family"])] = (len(attempted), per_bank)
worst_family = max((n for n, _ in per_fold_family.values()), default=0)
worst_bank = max((max(b.values()) for _, b in per_fold_family.values() if b), default=0)
print("CAPS")
print(f"  max attempted neighbours in one family-fold {worst_family} (limit {bank['max_neighbors_per_family']})")
print(f"  max attempted neighbours in one bank        {worst_bank} (limit {bank['max_neighbors_per_bank']})")
print(f"  counts {bank['counts']}")

# ---- 2. recompute one selected candidate's inner improvement ---------------
first = rules["folds"][0]
role = next(r for r in first["roles"] if r["role"] == "refined_selected")
fold = next(f for f in folds if f["test_year"] == first["outer_fold"])
inner = list(fold["fit"]) + list(fold["tune"])
got = rows_for([role["candidate_id"]], inner)[role["candidate_id"]]
pairs = [
    (float(r["candidate_net_points"]), float(r["baseline_net_points"]))
    for day in inner
    if (r := got.get(day)) is not None
    and r["status"] == "evaluated"
    and r["complete"]
    and r["candidate_net_points"] is not None
    and r["baseline_net_points"] is not None
]
mean_c = sum(c for c, _ in pairs) / len(pairs)
mean_b = sum(b for _, b in pairs) / len(pairs)
print("RECOMPUTE")
print(f"  {role['candidate_id']} fold {first['outer_fold']} over {len(pairs)} common complete inner days")
print(f"  inner improvement recomputed {mean_c - mean_b:.6f}  artifact {role['inner_improvement_vs_b02']:.6f}"
      f"  delta {abs((mean_c - mean_b) - role['inner_improvement_vs_b02']):.2e}")

# ---- 3. trace one native output of a refined candidate ---------------------
cid = role["candidate_id"]
day = next(
    (d for d in reversed(inner) if int((got.get(d) or {}).get("candidate_fills") or 0) > 0),
    inner[-1],
)
job = json.loads(gzip.open(R / "jobs" / day / (cid.replace(":", "--") + ".json.gz")).read())
print("TRACE")
print(f"  {cid} {day} status {job['status']} parameters {job['parameters']}")
print(f"  pairing baseline {job['pairing_baseline_source']} {Path(job['pairing_baseline_path'] or '').name}")
if job.get("pairing_baseline_path"):
    h = hashlib.sha256()
    with open(job["pairing_baseline_path"], "rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            h.update(chunk)
    print(f"  recomputed sha256 matches recorded: {h.hexdigest() == job['pairing_baseline_sha256']}")
entries = (job.get("candidate") or {}).get("entries") or []
if entries:
    e = entries[0]
    side, fill, exit_px = int(e["side"]), Decimal(e["fill_price"]), Decimal(e["exit_price"])
    delta = (exit_px - fill) if side == 1 else (fill - exit_px)
    expect = delta - Decimal(e["round_trip_cost"]) / Decimal(20)
    print(f"  entry {e['entry_id']} net points recomputed {expect} artifact {e['net_points']}"
          f" equal {expect == Decimal(e['net_points'])}")
else:
    print("  no filled entry on this day (a complete zero-entry day is kept)")
parent = json.loads((B / "REFINEMENT_ALLOWLIST.json").read_text())
parent_ids = {
    b["candidate_id"]
    for f in parent["folds"]
    for fam in f["families"]
    for b in fam["selected_banks"]
}
print(f"  parent trial ids are breadth-selected banks: {set(role['parent_trial_ids']) <= parent_ids}")

# ---- 4. every proposal is in the ledger exactly once -----------------------
proposed = [
    (fold["outer_fold"], row["candidate_id"])
    for fold in bank["folds"]
    for family in fold["families"]
    for row in family["neighbors"]
]
neighbour_rows = [r for r in ledger if r["stage"] == "refinement"]
combo_rows = [r for r in ledger if r["stage"] == "refinement_combination"]
ledger_keys = [(row["outer_fold"], row["candidate_id"]) for row in neighbour_rows]
combos = json.loads((R / "COMBINATION_RESULTS.json").read_text())["rows"]
print("RECONCILE")
print(f"  neighbour proposals {len(proposed)}  ledger rows {len(ledger_keys)}  unique {len(set(ledger_keys))}")
print(f"  every neighbour proposal has exactly one row: {sorted(proposed) == sorted(ledger_keys)}")
print(f"  combination proposals {len(combos)}  ledger rows {len(combo_rows)}"
      f"  match {sorted((c['outer_fold'], c['candidate_id']) for c in combos) == sorted((r['outer_fold'], r['candidate_id']) for r in combo_rows)}")
print(f"  combinations attempted {sum(1 for c in combos if c['status'] == 'attempted')}"
      f" not applicable {sum(1 for c in combos if c['status'] != 'attempted')}")
print(f"  every row has a disposition: {all(r['disposition'] for r in ledger)}")
print(f"  statuses {dict((s, sum(1 for r in ledger if r['status'] == s)) for s in {r['status'] for r in ledger})}")
print(f"  rows with parent_trial_ids: {sum(1 for r in ledger if r['parent_trial_ids'])} of {len(ledger)}")
