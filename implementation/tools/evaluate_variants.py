#!/usr/bin/env python3
"""Fold evaluation of the population runner's variants against B0.3.

Input: rows.jsonl of run_jj_gb_population.py (its ``kind: session`` lines
carry every variant's executed-list result and the day reads). For each
family and variant the daily net-points series is paired with B0.3's on the
same sessions and judged the way EVALUATION.md judges a candidate:

* chronological outer folds by calendar year: the test fold is one year, the
  fit fold is every earlier year (the first two years are fit only);
* the score is the mean daily difference on the test fold with the frozen
  block bootstrap of ``refinement.centered_bootstrap_pvalue`` (20,000 draws,
  block 5, sensitivity blocks 1 and 10);
* Holm across the family's variants within a fold (the attainable floor is
  reported when the variant count makes the nominal level unreachable);
* the same difference broken down by the day-read strata, so a stratum-
  conditional policy can be proposed on the fit folds only (reported as a
  separate row, fitted on fit years, scored on the test year).

Output: VARIANTS.json and VARIANTS.md in --out. Nothing here rescans.
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np

WORKTREE = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(WORKTREE / "implementation/src"))

from trading_research.research.rule_discovery.refinement import centered_bootstrap_pvalue  # noqa: E402

BASELINE = "B0.3"
STRATA = {"JJ-TBR": ("classification", "range_bin"), "GB-FAIL": ("day_model", "bias"), "GB-SCALP": ("day_model",), "GB-VWAP": ("day_model",)}


def load_sessions(path: Path) -> list[dict]:
    out = []
    with path.open() as handle:
        for line in handle:
            if '"kind": "session"' not in line:
                continue
            out.append(json.loads(line))
    return sorted(out, key=lambda r: r["date"])


def series(sessions: list[dict], variant: str, family: str) -> dict[str, float]:
    return {s["date"]: float(s["variants"][variant][family]["net_points"]) for s in sessions if variant in s["variants"] and family in s["variants"][variant]}


def holm(p_values: list[float], alpha: float = 0.05) -> list[float]:
    order = sorted(range(len(p_values)), key=lambda i: p_values[i])
    adjusted = [1.0] * len(p_values)
    running = 0.0
    m = len(p_values)
    for rank, i in enumerate(order):
        step = min(1.0, p_values[i] * (m - rank))
        running = max(running, step)
        adjusted[i] = running
    return adjusted


def stratum_of(session: dict, family: str) -> str:
    read = (session.get("reads") or {}).get(family) or {}
    keys = STRATA.get(family, ())
    return "|".join(f"{k}={read.get(k)}" for k in keys) if keys else "all"


def evaluate(sessions: list[dict], family: str, variants: list[str]) -> dict:
    base = series(sessions, BASELINE, family)
    years = sorted({d[:4] for d in base})
    folds = [(y, [x for x in years if x < y]) for y in years[2:]]  # first two years fit only
    result = {"family": family, "baseline_sessions": len(base), "years": years, "folds": [], "variants": {}}
    for variant in variants:
        cand = series(sessions, variant, family)
        days = [d for d in base if d in cand]
        diff = {d: cand[d] - base[d] for d in days}
        rows = {"overall": {"sessions": len(days), "mean_daily_diff": round(float(np.mean(list(diff.values()))), 3) if days else None, "baseline_mean": round(float(np.mean([base[d] for d in days])), 3) if days else None, "variant_mean": round(float(np.mean([cand[d] for d in days])), 3) if days else None}, "test_folds": {}}
        for test_year, fit_years in folds:
            test_days = [d for d in days if d[:4] == test_year]
            if len(test_days) < 20:
                rows["test_folds"][test_year] = {"sessions": len(test_days), "verdict": "inconclusive_support"}
                continue
            boot = centered_bootstrap_pvalue([diff[d] for d in test_days], segments=[d[:4] for d in test_days])
            fit_days = [d for d in days if d[:4] in fit_years]
            rows["test_folds"][test_year] = {
                "sessions": len(test_days),
                "mean_daily_diff": round(float(np.mean([diff[d] for d in test_days])), 3),
                "p_raw": boot.get("p_raw", boot.get("p")),
                "ci_low": boot.get("ci_low"), "ci_high": boot.get("ci_high"),
                "fit_mean_daily_diff": round(float(np.mean([diff[d] for d in fit_days])), 3) if fit_days else None,
            }
        # strata (whole series, descriptive)
        by_stratum = defaultdict(list)
        for s in sessions:
            d = s["date"]
            if d in diff:
                by_stratum[stratum_of(s, family)].append(diff[d])
        rows["strata"] = {k: {"sessions": len(v), "mean_daily_diff": round(float(np.mean(v)), 3)} for k, v in sorted(by_stratum.items()) if len(v) >= 20}
        result["variants"][variant] = rows
    # Holm within each fold across variants
    for test_year, _fit in folds:
        ps = [(v, result["variants"][v]["test_folds"].get(test_year, {}).get("p_raw")) for v in variants]
        valid = [(v, p) for v, p in ps if p is not None]
        adjusted = holm([p for _v, p in valid]) if valid else []
        for (v, _p), adj in zip(valid, adjusted):
            result["variants"][v]["test_folds"][test_year]["p_holm"] = round(adj, 4)
            fold = result["variants"][v]["test_folds"][test_year]
            fold["verdict"] = "promoted" if adj <= 0.05 and fold["mean_daily_diff"] > 0 else ("worse" if fold["mean_daily_diff"] < 0 else "not_promoted")
        result["folds"].append({"test_year": test_year, "n_variants": len(valid), "holm_floor": round(1.0 / max(1, len(valid)) * 0.05, 4)})
    # the stratum-conditional policy: on each test fold pick, per stratum, the
    # variant with the best FIT-years mean (baseline included), then score the test year
    cond = {"test_folds": {}}
    for test_year, fit_years in folds:
        choice = {}
        strata_fit = defaultdict(lambda: defaultdict(list))
        for s in sessions:
            d = s["date"]
            if d[:4] not in fit_years or d not in base:
                continue
            st = stratum_of(s, family)
            for v in [BASELINE] + variants:
                if v in s["variants"] and family in s["variants"][v]:
                    strata_fit[st][v].append(float(s["variants"][v][family]["net_points"]))
        for st, per_v in strata_fit.items():
            means = {v: float(np.mean(x)) for v, x in per_v.items() if len(x) >= 20}
            choice[st] = max(means, key=means.get) if means else BASELINE
        test_diff = []
        for s in sessions:
            d = s["date"]
            if d[:4] != test_year or d not in base:
                continue
            v = choice.get(stratum_of(s, family), BASELINE)
            if v in s["variants"] and family in s["variants"][v]:
                test_diff.append(float(s["variants"][v][family]["net_points"]) - base[d])
        if len(test_diff) >= 20:
            boot = centered_bootstrap_pvalue(test_diff, segments=[test_year] * len(test_diff))
            cond["test_folds"][test_year] = {"sessions": len(test_diff), "mean_daily_diff": round(float(np.mean(test_diff)), 3), "p_raw": boot.get("p_raw", boot.get("p")), "ci_low": boot.get("ci_low"), "ci_high": boot.get("ci_high"), "choice": choice}
    result["stratum_conditional"] = cond
    return result


def render(report: dict) -> str:
    lines = ["# Selection variants against B0.3 (executed list, points a contract, no costs)", ""]
    for family, res in report.items():
        lines += [f"## {family}", "", f"baseline sessions {res['baseline_sessions']}; years {res['years'][0]}-{res['years'][-1]}; test folds {', '.join(f['test_year'] for f in res['folds'])}", "", "| variant | sessions | baseline mean | variant mean | mean diff | " + " | ".join(f"{f['test_year']} diff (p Holm)" for f in res["folds"]) + " |", "| --- | ---: | ---: | ---: | ---: | " + " | ".join("---:" for _ in res["folds"]) + " |"]
        for v, rows in res["variants"].items():
            o = rows["overall"]
            cells = []
            for f in res["folds"]:
                t = rows["test_folds"].get(f["test_year"], {})
                cells.append(f"{t.get('mean_daily_diff')} ({t.get('p_holm')}) {t.get('verdict', '')}".strip())
            lines.append(f"| {v} | {o['sessions']} | {o['baseline_mean']} | {o['variant_mean']} | {o['mean_daily_diff']} | " + " | ".join(cells) + " |")
        cond = res.get("stratum_conditional", {}).get("test_folds") or {}
        if cond:
            lines += ["", "Stratum-conditional policy (fitted on the fit years, scored on the test year):", ""]
            for y, t in cond.items():
                lines.append(f"- {y}: mean diff {t['mean_daily_diff']} over {t['sessions']} sessions, p {t['p_raw']}, CI [{t['ci_low']}, {t['ci_high']}]; choice {t['choice']}")
        lines.append("")
    return "\n".join(lines)


def merge_rescans(sessions: list[dict], rescans: dict[str, Path]) -> list[dict]:
    """A rescan candidate's run carries its own executed result under the name
    B0.3 (the scanner was different); fold it into the baseline sessions under
    the candidate's name so the same paired evaluation applies."""
    by_date = {s["date"]: s for s in sessions}
    for name, path in rescans.items():
        for s in load_sessions(path):
            base = by_date.get(s["date"])
            if base is None or BASELINE not in s["variants"]:
                continue
            base["variants"][name] = s["variants"][BASELINE]
    return sessions


def main(argv=None) -> int:
    global BASELINE
    parser = argparse.ArgumentParser()
    parser.add_argument("--rows", type=Path, required=True, help="the baseline run's rows.jsonl (B0.3 plus its selection variants)")
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--families", default="JJ-TBR,GB-FAIL")
    parser.add_argument("--rescan", action="append", default=[], help="name=path/to/rows.jsonl of a rescan candidate's run (repeatable)")
    parser.add_argument("--baseline", default=BASELINE, help="the variant every other variant is judged against (B0.3 for selection and rescan runs, E0 for the exit runs)")
    args = parser.parse_args(argv)
    BASELINE = args.baseline
    sessions = load_sessions(args.rows)
    if not sessions:
        raise SystemExit("no session lines in the rows file")
    if args.rescan:
        sessions = merge_rescans(sessions, {item.split("=", 1)[0]: Path(item.split("=", 1)[1]) for item in args.rescan})
    names = sorted({v for s in sessions for v in s["variants"]} - {BASELINE})
    report = {}
    for family in args.families.split(","):
        # a family's candidates carry its prefix (JJ-..., GB-...); a policy that
        # applies to every family (the exit policies E1..E4) carries the
        # family's stats in its session lines instead
        prefix = family.split("-")[0]
        applicable = [v for v in names if v.startswith(prefix) or any(family in (s["variants"].get(v) or {}) for s in sessions[:200])]
        report[family] = evaluate(sessions, family, applicable)
        print(json.dumps({"family": family, "variants": len(applicable), "sessions": report[family]["baseline_sessions"]}))
    args.out.mkdir(parents=True, exist_ok=True)
    (args.out / "VARIANTS.json").write_text(json.dumps(report, indent=1, default=str) + "\n")
    (args.out / "VARIANTS.md").write_text(render(report) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
