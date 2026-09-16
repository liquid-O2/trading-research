"""P15-17 stage B rehearsal self-check.

Independent of search_run's arithmetic: plain json/gzip/Decimal/statistics only,
reading the attempt's own artifacts. Recomputes a central result, traces one
native output back to the P15-16A bytes, and reconciles the declared jobs.
"""
import gzip, json, sys
from decimal import Decimal
from pathlib import Path

R = Path(sys.argv[1])
SPLITS = Path(sys.argv[2])
results = json.loads((R / "BREADTH_RESULTS.json").read_text())
folds = json.loads(SPLITS.read_text())["outer"]
manifest = json.loads((R / "MANIFEST.json").read_text())


def daily(day):
    path = R / "daily" / f"{day}.json"
    return json.loads(path.read_text())["rows"] if path.is_file() else []


_CACHE = {}


def table_for(candidate_ids, days):
    """One pass over the needed daily shards, indexed by candidate then day."""
    wanted = set(candidate_ids)
    out = {cid: {} for cid in wanted}
    for day in days:
        rows = _CACHE.get(day)
        if rows is None:
            rows = _CACHE[day] = {
                r["candidate_id"]: r for r in daily(day) if r["candidate_id"] in wanted
            }
        for cid, row in rows.items():
            if cid in wanted:
                out[cid][day] = row
    return out


def rows_for(candidate_id, days):
    return table_for([candidate_id], days)[candidate_id]


# the blind hold-out enters no statistic (EVALUATION.md, 2026-09-16)
HOLDOUT = results.get("holdout_excluded") or {"start": "2026-04-01", "end": "2026-09-03"}


def in_holdout(day):
    return HOLDOUT["start"] <= day <= HOLDOUT["end"]


# ---- 1. recompute one candidate's outer mean paired improvement ------------
target = max(results["decisions"], key=lambda r: r["mean_diff"])["candidate_id"]
claimed = next(r for r in results["decisions"] if r["candidate_id"] == target)
diffs, days_used, block_means = [], 0, []
for fold in folds:
    got = rows_for(target, fold["test"])
    fold_diffs = []
    for day in fold["test"]:
        if in_holdout(day):
            continue
        row = got.get(day)
        if row is None or row["status"] != "evaluated" or not row["complete"]:
            continue
        if row["candidate_net_points"] is None or row["baseline_net_points"] is None:
            continue
        fold_diffs.append(float(row["candidate_net_points"]) - float(row["baseline_net_points"]))
    if fold_diffs:
        block_means.append(sum(fold_diffs) / len(fold_diffs))
        diffs.extend(fold_diffs)
        days_used += len(fold_diffs)
mean = sum(diffs) / len(diffs)
print(f"RECOMPUTE A  {target}")
print(f"  mean paired improvement  recomputed {mean:.6f}  artifact {claimed['mean_diff']:.6f}  "
      f"delta {abs(mean - claimed['mean_diff']):.2e}")
print(f"  eligible test days       recomputed {days_used}  artifact {claimed['eligible_test_days']}")
print(f"  supported outer blocks   recomputed {len(block_means)}  artifact {claimed['supported_outer_blocks']}")

_CACHE.clear()

# ---- 2. recompute one fold's inner pick from the inner days only ----------
fold = folds[0]
inner = list(fold["fit"]) + list(fold["tune"])
selection = next(f for f in results["selections"] if f["outer_fold"] == fold["test_year"])
family = "SIRES"
scores = {}
family_ids = [r["candidate_id"] for r in results["decisions"] if r["family"] == family]
family_table = table_for(family_ids, inner)
for row in results["decisions"]:
    if row["family"] != family:
        continue
    got = family_table[row["candidate_id"]]
    pairs = [
        (float(r["candidate_net_points"]), float(r["baseline_net_points"]))
        for day in inner
        if not in_holdout(day)
        and (r := got.get(day)) is not None
        and r["status"] == "evaluated"
        and r["complete"]
        and r["candidate_net_points"] is not None
        and r["baseline_net_points"] is not None
    ]
    if pairs:
        entries = sum(
            int(r["candidate_fills"] or 0)
            for day in inner
            if not in_holdout(day)
            and (r := got.get(day)) is not None and r["status"] == "evaluated" and r["complete"]
        )
        support_days = sum(
            1
            for day in inner
            if not in_holdout(day)
            and (r := got.get(day)) is not None
            and r["status"] == "evaluated"
            and r["complete"]
            and int(r["candidate_fills"] or 0) > 0
        )
        scores[row["candidate_id"]] = {
            "score": sum(c for c, _ in pairs) / len(pairs) - sum(b for _, b in pairs) / len(pairs),
            "bank": row["bank"],
            "parameters": len(row.get("parameters") or {}),
            "entries": entries,
            "support_days": support_days,
        }

# SEARCH_CONTRACT: inside a bank take the best inner score, then the 1% simplicity
# rule (fewer parameters, then lower candidate ID); a bank qualifies only with a
# nonnegative improvement and inner support; at most two banks per family.
by_bank = {}
for cid, body in scores.items():
    by_bank.setdefault(body["bank"], []).append((cid, body))
representatives = []
for bank, group in by_bank.items():
    best = max(body["score"] for _, body in group)
    span = abs(best) * 0.01
    near = [(cid, body) for cid, body in group if body["score"] >= best - span]
    near.sort(key=lambda item: (item[1]["parameters"], item[0]))
    cid, body = near[0]
    if body["score"] < 0 or body["entries"] <= 0 or body["support_days"] <= 0:
        continue
    representatives.append((cid, body["score"], bank))
representatives.sort(key=lambda item: (-item[1], item[0]))
picked = representatives[:2]
claimed_banks = [b["candidate_id"] for b in selection["families"][family]["selected_banks"]]
print(f"RECOMPUTE B  fold {fold['test_year']} {family} inner tuning over {len(inner)} inner days")
print(f"  banks scored {len(by_bank)}  qualifying {len(representatives)}")
print(f"  recomputed picks {sorted(cid for cid, _, _ in picked)}")
print(f"  artifact picks   {sorted(claimed_banks)}")
print(f"  agree: {sorted(cid for cid, _, _ in picked) == sorted(claimed_banks)}")

# ---- 3. trace one native output back to the P15-16A bytes -----------------
day = "2024-03-05"
cid = next(
    r["candidate_id"]
    for r in daily(day)
    if r["family"] == "SIRES" and int(r.get("candidate_fills") or 0) > 0
)
job = json.loads(gzip.open(R / "jobs" / day / (cid.replace(":", "--") + ".json.gz")).read())
entry = (job["candidate"]["entries"] or [None])[0]
print(f"TRACE  {cid} {day}")
print(f"  pairing baseline {job['pairing_baseline_source']} {job['pairing_baseline_path']}")
import hashlib
h = hashlib.sha256()
with open(job["pairing_baseline_path"], "rb") as handle:
    for chunk in iter(lambda: handle.read(1 << 20), b""):
        h.update(chunk)
print(f"  recomputed sha256 matches recorded: {h.hexdigest() == job['pairing_baseline_sha256']}")
source = json.loads(gzip.open(job["pairing_baseline_path"]).read())
print(f"  source job family/branch {source['family']}/{source['branch']} episodes {len(source['episodes'])}"
      f" baseline_version {source['baseline_version']}")
if entry:
    side, fill, exit_px = int(entry["side"]), Decimal(entry["fill_price"]), Decimal(entry["exit_price"])
    cost = Decimal(entry["round_trip_cost"])
    delta = (exit_px - fill) if side == 1 else (fill - exit_px)
    expect = delta - cost / Decimal(20)
    print(f"  entry {entry['entry_id']} {entry['exit_reason']}")
    print(f"  net points recomputed {expect}  artifact {entry['net_points']}  equal {expect == Decimal(entry['net_points'])}")
    ids = {e.get("candidate_id") for e in source["episodes"]}
    print(f"  entry id present in the source B0.2 episodes: {entry['entry_id'] in ids}")

# ---- 4. declared jobs reconcile to unique artifacts and dispositions ------
complete = json.loads((R / "RUN_COMPLETE.json").read_text())
names = {c.replace(":", "--") for c in manifest["candidates"]}
print("RECONCILE")
print(f"  declared {complete['declared_jobs']} = written {complete['written_jobs']}"
      f" + absent {complete['jobs_absent_on_retained_failure_dates']}"
      f"  -> {complete['declared_jobs_reconciled']}")
print(f"  unique artifact names {len(names)} of {len(manifest['candidates'])} candidates")
statuses = results["coverage"]["rows_by_status"]
print(f"  terminal dispositions {statuses} sum {sum(statuses.values())}")
print(f"  retained failures {complete['retained_failure_dates']}")
ledger = [json.loads(line) for line in (R / "TRIALS.jsonl").read_text().splitlines() if line.strip()]
print(f"  ledger rows {len(ledger)} = {len(manifest['candidates'])} candidates x {len(folds)} folds"
      f"  -> {len(ledger) == len(manifest['candidates']) * len(folds)}")
print(f"  every ledger row has a disposition: {all(r['disposition'] for r in ledger)}")
print(f"  every non-attempted row has an attribution: "
      f"{all(r['failure_attribution'] for r in ledger if r['status'] != 'attempted')}")
