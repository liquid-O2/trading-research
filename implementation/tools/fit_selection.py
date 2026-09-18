#!/usr/bin/env python3
"""A strategy's selection model, fitted on its own population and nothing
else, and readable: an L2 logistic regression (the repo's own gradient
descent, no library model) on named features, walk-forward by year, with

  * every feature ALSO fitted alone, so the ones that actually select are
    visible and a feature that only rides along is not credited;
  * the out-of-sample score deciles (does the label rate climb with the
    score?), the AUC per test year, and the standardized coefficients;
  * the per-day read: taking only the top-k scored events a day, the label
    rate and the mean excursion edge against taking every event.

One model per strategy and role; never pooled across authors. Rows on or after
the Phase 2 blind hold-out (2026-04-01) are not read.

    fit_selection.py --rows rows.jsonl --out <dir> --label held
        [--label-field label_outcome] [--label-positive held]
        [--mfe label_mfe_15 --mae label_mae_15] [--top-k 3,5,10]
        [--test-years 2023,2024,2025,2026] [--exclude a,b] [--filter key=value]

The label is ``label-field == label-positive``; with ``--label favourable`` it
is ``mfe > mae`` on the named excursion fields.
"""
from __future__ import annotations

import argparse
import json
import math
from collections import defaultdict
from pathlib import Path

import numpy as np

HOLDOUT_FROM = "2026-04-01"
META = {"family", "branch", "session", "decision_at", "side", "mode", "entry", "stop", "edge", "catalyst_kind", "cash_session", "entry_id", "example_id"}


def fit_logistic(X, y, l2: float = 1.0, iters: int = 400, lr: float = 0.5):
    n, d = X.shape
    w = np.zeros(d)
    b = 0.0
    for _ in range(iters):
        p = 1 / (1 + np.exp(-(X @ w + b)))
        g = p - y
        w -= lr * (X.T @ g / n + l2 * w / n)
        b -= lr * g.mean()
    return w, b


def auc(y, s) -> float | None:
    y = np.asarray(y)
    s = np.asarray(s)
    pos, neg = int(y.sum()), int(len(y) - y.sum())
    if pos == 0 or neg == 0:
        return None
    order = np.argsort(s, kind="mergesort")
    ranks = np.empty(len(s))
    ranks[order] = np.arange(1, len(s) + 1)
    # average ranks over ties
    sorted_s = s[order]
    i = 0
    while i < len(s):
        j = i
        while j + 1 < len(s) and sorted_s[j + 1] == sorted_s[i]:
            j += 1
        if j > i:
            ranks[order[i : j + 1]] = (i + j + 2) / 2
        i = j + 1
    return float((ranks[y == 1].sum() - pos * (pos + 1) / 2) / (pos * neg))


def design(rows, features, stats=None):
    """Numeric matrix with a missing indicator per feature that has gaps;
    medians and scales come from the training rows only."""
    cols = []
    names = []
    fresh = stats is None
    stats = {} if fresh else stats
    for f in features:
        raw = np.array([np.nan if r.get(f) is None else float(r[f]) for r in rows], dtype=float)
        if fresh:
            ok = raw[~np.isnan(raw)]
            med = float(np.median(ok)) if ok.size else 0.0
            lo, hi = (np.percentile(ok, [1, 99]) if ok.size else (0.0, 0.0))
            clipped = np.clip(np.where(np.isnan(raw), med, raw), lo, hi)
            sd = float(clipped.std()) or 1.0
            stats[f] = {"median": med, "lo": float(lo), "hi": float(hi), "mean": float(clipped.mean()), "sd": sd, "has_missing": bool(np.isnan(raw).any())}
        st = stats[f]
        value = np.clip(np.where(np.isnan(raw), st["median"], raw), st["lo"], st["hi"])
        cols.append((value - st["mean"]) / st["sd"])
        names.append(f)
        if st["has_missing"]:
            cols.append(np.isnan(raw).astype(float))
            names.append(f + "__missing")
    return np.column_stack(cols) if cols else np.zeros((len(rows), 0)), names, stats


def main(argv=None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--rows", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--label", choices=("field", "favourable"), default="field")
    parser.add_argument("--label-field", default="label_outcome")
    parser.add_argument("--label-positive", default="held")
    parser.add_argument("--label-drop", default="unresolved", help="rows whose label field has this value are left out")
    parser.add_argument("--mfe", default="label_mfe_15")
    parser.add_argument("--mae", default="label_mae_15")
    parser.add_argument("--top-k", default="3,5,10")
    parser.add_argument("--test-years", default="2023,2024,2025,2026")
    parser.add_argument("--exclude", default="")
    parser.add_argument("--filter", action="append", default=[], help="key=value; keep rows whose field equals the value (repeatable)")
    parser.add_argument("--l2", type=float, default=1.0)
    args = parser.parse_args(argv)
    filters = [f.split("=", 1) for f in args.filter]
    rows = []
    with args.rows.open() as handle:
        for line in handle:
            r = json.loads(line)
            if r.get("kind") == "session" or str(r.get("session")) >= HOLDOUT_FROM:
                continue
            if any(str(r.get(k)) != v for k, v in filters):
                continue
            if args.label == "field":
                if r.get(args.label_field) is None or r.get(args.label_field) == args.label_drop:
                    continue
                r["_y"] = 1.0 if r[args.label_field] == args.label_positive else 0.0
            else:
                if r.get(args.mfe) is None or r.get(args.mae) is None:
                    continue
                r["_y"] = 1.0 if float(r[args.mfe]) > float(r[args.mae]) else 0.0
            r["_edge"] = None if r.get(args.mfe) is None or r.get(args.mae) is None else float(r[args.mfe]) - float(r[args.mae])
            rows.append(r)
    if not rows:
        raise SystemExit("no rows")
    excluded = {e for e in args.exclude.split(",") if e}
    features = sorted(k for k, v in rows[0].items() if k not in META and k not in excluded and not k.startswith(("label_", "_")) and isinstance(v, (int, float, bool, type(None))))
    years = sorted({r["session"][:4] for r in rows})
    test_years = [y for y in args.test_years.split(",") if y in years and any(r["session"][:4] < y for r in rows)]
    y_all = np.array([r["_y"] for r in rows])
    year_of = np.array([r["session"][:4] for r in rows])
    scores = np.full(len(rows), np.nan)
    single = {f: np.full(len(rows), np.nan) for f in features}
    coefs = defaultdict(list)
    fold_report = []
    for ty in test_years:
        tr, te = year_of < ty, year_of == ty
        if tr.sum() < 200 or te.sum() < 50:
            continue
        train = [r for r, m in zip(rows, tr) if m]
        test = [r for r, m in zip(rows, te) if m]
        Xtr, names, stats = design(train, features)
        Xte, _, _ = design(test, features, stats)
        w, b = fit_logistic(Xtr, y_all[tr], l2=args.l2)
        scores[te] = 1 / (1 + np.exp(-(Xte @ w + b)))
        for name, value in zip(names, w):
            coefs[name].append(float(value))
        for f in features:
            X1, n1, s1 = design(train, [f])
            w1, b1 = fit_logistic(X1, y_all[tr], l2=args.l2)
            X1te, _, _ = design(test, [f], s1)
            single[f][te] = 1 / (1 + np.exp(-(X1te @ w1 + b1)))
        fold_report.append({"test_year": ty, "train_rows": int(tr.sum()), "test_rows": int(te.sum()), "base_rate": round(float(y_all[te].mean()), 4), "auc": None if auc(y_all[te], scores[te]) is None else round(auc(y_all[te], scores[te]), 4)})
    scored = ~np.isnan(scores)
    if not scored.any():
        raise SystemExit("no test fold had enough rows")
    ys, ss = y_all[scored], scores[scored]
    edges = np.array([np.nan if r["_edge"] is None else r["_edge"] for r in rows])[scored]
    sess = np.array([r["session"] for r in rows])[scored]
    overall_auc = auc(ys, ss)
    # deciles of the out-of-sample score
    order = np.argsort(ss)
    deciles = []
    for d, idx in enumerate(np.array_split(order, 10), 1):
        deciles.append({"decile": d, "rows": int(len(idx)), "label_rate": round(float(ys[idx].mean()), 4), "mean_edge": None if np.isnan(edges[idx]).all() else round(float(np.nanmean(edges[idx])), 3)})
    single_auc = {}
    for f in features:
        s1 = single[f][scored]
        a = auc(ys, s1)
        single_auc[f] = None if a is None else round(a, 4)
    # per-day top-k against taking everything
    by_day = defaultdict(list)
    for i, day in enumerate(sess):
        by_day[day].append(i)
    topk = []
    for k in [int(v) for v in args.top_k.split(",") if v]:
        picked = []
        for day, idx in by_day.items():
            idx = sorted(idx, key=lambda i: -ss[i])[:k]
            picked.extend(idx)
        picked = np.array(picked)
        topk.append({"k": k, "events": int(len(picked)), "label_rate": round(float(ys[picked].mean()), 4), "mean_edge": None if np.isnan(edges[picked]).all() else round(float(np.nanmean(edges[picked])), 3)})
    summary = {
        "schema": "selection-fit-v1",
        "rows": len(rows),
        "rows_scored_out_of_sample": int(scored.sum()),
        "label": {"kind": args.label, "field": args.label_field, "positive": args.label_positive, "mfe": args.mfe, "mae": args.mae},
        "filters": filters,
        "base_rate": round(float(ys.mean()), 4),
        "mean_edge_all": None if np.isnan(edges).all() else round(float(np.nanmean(edges)), 3),
        "auc_out_of_sample": None if overall_auc is None else round(overall_auc, 4),
        "folds": fold_report,
        "deciles": deciles,
        "top_k_per_day": topk,
        "events_per_day": round(float(np.mean([len(v) for v in by_day.values()])), 1),
        "single_feature_auc": dict(sorted(single_auc.items(), key=lambda kv: -(abs((kv[1] or 0.5) - 0.5)))),
        "coefficients_standardized_mean": {k: round(float(np.mean(v)), 4) for k, v in sorted(coefs.items(), key=lambda kv: -abs(np.mean(kv[1])))},
        "holdout_untouched_from": HOLDOUT_FROM,
    }
    args.out.mkdir(parents=True, exist_ok=True)
    (args.out / "SELECTION_FIT.json").write_text(json.dumps(summary, indent=1) + "\n")
    lines = [f"# Selection fit: {args.rows}", "", f"Rows {summary['rows']} (scored out of sample {summary['rows_scored_out_of_sample']}); events a day {summary['events_per_day']}; base rate {summary['base_rate']}; out-of-sample AUC **{summary['auc_out_of_sample']}**; hold-out from {HOLDOUT_FROM} untouched.", "", "| test year | train rows | test rows | base rate | AUC |", "| --- | ---: | ---: | ---: | ---: |"]
    lines += [f"| {f['test_year']} | {f['train_rows']} | {f['test_rows']} | {f['base_rate']} | {f['auc']} |" for f in fold_report]
    lines += ["", "| score decile | rows | label rate | mean MFE-MAE |", "| ---: | ---: | ---: | ---: |"] + [f"| {d['decile']} | {d['rows']} | {d['label_rate']} | {d['mean_edge']} |" for d in deciles]
    lines += ["", f"Taking every event: label rate {summary['base_rate']}, mean MFE-MAE {summary['mean_edge_all']}.", "", "| top-k a day | events | label rate | mean MFE-MAE |", "| ---: | ---: | ---: | ---: |"] + [f"| {t['k']} | {t['events']} | {t['label_rate']} | {t['mean_edge']} |" for t in topk]
    lines += ["", "| feature alone | out-of-sample AUC |", "| --- | ---: |"] + [f"| {k} | {v} |" for k, v in list(summary["single_feature_auc"].items())[:20]]
    lines += ["", "| feature (joint model) | standardized coefficient, mean over folds |", "| --- | ---: |"] + [f"| {k} | {v} |" for k, v in list(summary["coefficients_standardized_mean"].items())[:20]]
    (args.out / "SELECTION_FIT.md").write_text("\n".join(lines) + "\n")
    print(json.dumps({"event": "fit_complete", "rows": summary["rows"], "auc": summary["auc_out_of_sample"], "base_rate": summary["base_rate"], "deciles": [d["label_rate"] for d in deciles]}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
