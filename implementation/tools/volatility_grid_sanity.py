"""Reconciliation and the clock sanity table of the full volatility-grid run."""
import json, glob, sys
from datetime import date, timedelta
import numpy as np, pandas as pd
out = sys.argv[1]
summary = json.load(open(f"{out}/SUMMARY.json"))
df = pd.concat([pd.read_parquet(p) for p in sorted(glob.glob(f"{out}/volatility_grid_*.parquet"))], ignore_index=True)
print("days requested", summary["days_requested"], "dispositions", summary["dispositions"], "reconciled", summary["reconciled"], "rows", len(df), "declared", summary["rows_declared_by_checkpoints"])
print("failures", summary["failures"][:10], "n", len(summary["failures"]))
print("non-trading days", len(summary["non_trading_days"]), summary["non_trading_days"][:12])
# every requested weekday has exactly one disposition; every complete day has its grid rows
per_day = df.groupby("day").size()
print("rows per complete day: min", int(per_day.min()), "max", int(per_day.max()), "days", len(per_day), "duplicated (day, issue_ns)", int(df.duplicated(["day", "issue_ns"]).sum()))
pop = [l.strip() for l in open("/workspace/.scratch/a537e734/p2-vol/population_dates.txt") if l.strip()]
have = set(per_day.index)
missing = [d for d in pop if d not in have]
print("Phase 1.5 population dates", len(pop), "covered by complete days", len(pop) - len(missing), "not covered", missing[:15])
print("hold-out rows", int(df.is_holdout.sum()), "first hold-out day", df[df.is_holdout].day.min(), "| any hold-out flag before 2026-04-01:", bool((df[df.day < "2026-04-01"].is_holdout).any()))
print("target status counts", json.dumps(summary["target_status_counts"]))
# causality spot check on the written table: a target is known only at or after its issue time
for name in ("tgt_rv_15m", "tgt_rv_60m", "tgt_rv_remaining_rth"):
    ok = df[df[f"{name}_status"] == "ok"]
    assert (ok[f"{name}_known_at_ns"] > ok["issue_ns"]).all(), name
for col in df.columns:
    if df[col].dtype == object and (col.startswith(("har_", "log_", "rv_", "gk", "yz", "tgt_rv", "overnight_", "rth_range")) and not col.endswith("_status")):
        df[col] = pd.to_numeric(df[col], errors="coerce")
rth = df[df.in_rth]
print("\ncorrelation of log recent-60m RV with log next-60m RV, RTH grid rows, by year (clock sanity; must be clearly positive):")
print("| year | rows with both | corr(log recent 60m, log next 60m) | corr(log HAR1 rth, log next 60m) | share of RTH rows with a complete 60m target |")
print("| --- | ---: | ---: | ---: | ---: |")
for year, g in rth.groupby(rth.day.str[:4]):
    both = g.dropna(subset=["rv_recent_60m", "tgt_rv_60m"])
    a, b = np.log(both.rv_recent_60m + 1e-12), np.log(both.tgt_rv_60m + 1e-12)
    h = g.dropna(subset=["har_rth_har1", "tgt_rv_60m"])
    ch = np.corrcoef(h.har_rth_har1, np.log(h.tgt_rv_60m + 1e-12))[0, 1] if len(h) > 2 else float("nan")
    share = float((g.tgt_rv_60m_status == "ok").mean())
    print(f"| {year} | {len(both)} | {np.corrcoef(a, b)[0, 1]:.3f} | {ch:.3f} | {share:.3f} |")
# a shuffled-clock negative control: pairing each row with another day's target should destroy most of the intraday signal
rng = np.random.default_rng(0)
both = rth.dropna(subset=["rv_recent_60m", "tgt_rv_60m"])
a = np.log(both.rv_recent_60m.to_numpy() + 1e-12); b = np.log(both.tgt_rv_60m.to_numpy() + 1e-12)
print(f"\nall years: corr {np.corrcoef(a, b)[0, 1]:.3f}; shuffled pairing (negative control) {np.corrcoef(a, rng.permutation(b))[0, 1]:.3f}")
cols = ["rv_recent_60m", "gk_60m", "rth_range_so_far_over_spot", "overnight_rv_cov", "har_rth_har1", "har_rth_har5", "har_rth_har22", "har_acct_cov_har1", "har_acct_strict_har1", "log_yz20_rth", "log_yz20_acct", "log_gk20_mean_rth"]
print("\nshare of RTH rows with a value:", {c: round(float(rth[c].notna().mean()), 3) for c in cols})
