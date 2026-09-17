#!/usr/bin/env python3
"""Fit the grading model on the authors' own choices and report recall at
their density.

Input: rows.jsonl from build_grading_dataset.py (one row per admitted
opportunity on a dated session; label 1 = the author's ticket). The model is a
regularised logistic regression on the features the authors name (confluence
count, cycle index, sweep depth, minutes from the open, side with bias, the
day read, the play), fitted per family with plain numpy so every weight is
inspectable. Validation is leave-one-day-out: each dated session is scored by
a model that never saw it. The operating point is the authors' density: the
score threshold that admits ``--per-day`` candidates a session on average;
recall at that threshold is the fidelity of the whole system (admission plus
grading), and the ranked weights say which of their stated reasons carry the
choice.
"""
from __future__ import annotations

import argparse
import json
import math
from collections import defaultdict
from pathlib import Path

import numpy as np

NUMERIC = ["coincident_levels_n", "cycle", "sweep_depth_points", "minutes_from_open", "stop_points", "first_objective_points", "rr_far"]
BOOL = ["read_aligned", "read_big_range", "read_open_inside_value", "side_with_bias"]
CATEGORICAL = ["play", "mode", "reference_kind", "read_classification", "read_day_model", "depth_class"]


def load(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text().splitlines() if line.strip()]


def design(rows: list[dict], vocab: dict | None = None):
    """A dense feature matrix; categorical values one-hot on a vocabulary
    frozen from the training rows."""
    if vocab is None:
        vocab = {c: sorted({str(r.get(c)) for r in rows if r.get(c) is not None}) for c in CATEGORICAL}
    cols = list(NUMERIC) + list(BOOL) + [f"{c}={v}" for c in CATEGORICAL for v in vocab[c]]
    X = np.zeros((len(rows), len(cols)))
    for i, r in enumerate(rows):
        j = 0
        for c in NUMERIC:
            v = r.get(c)
            X[i, j] = 0.0 if v is None else float(v)
            j += 1
        for c in BOOL:
            v = r.get(c)
            X[i, j] = 1.0 if v is True else 0.0
            j += 1
        for c in CATEGORICAL:
            for v in vocab[c]:
                X[i, j] = 1.0 if str(r.get(c)) == v else 0.0
                j += 1
    return X, cols, vocab


def standardise(X, mu=None, sd=None):
    if mu is None:
        mu = X.mean(axis=0)
        sd = X.std(axis=0)
        sd[sd == 0] = 1.0
    return (X - mu) / sd, mu, sd


def fit_logistic(X, y, l2: float = 1.0, iters: int = 3000, lr: float = 0.05):
    """Plain gradient descent with class weights so the 1–3 positives a day
    are not swamped by the twenty negatives."""
    n, d = X.shape
    w = np.zeros(d)
    b = 0.0
    pos = max(1, int(y.sum()))
    neg = max(1, n - pos)
    wp, wn = n / (2 * pos), n / (2 * neg)
    sw = np.where(y == 1, wp, wn)
    for _ in range(iters):
        z = X @ w + b
        p = 1 / (1 + np.exp(-z))
        g = (p - y) * sw
        w -= lr * (X.T @ g / n + l2 * w / n)
        b -= lr * g.mean()
    return w, b


def scores(X, w, b):
    return 1 / (1 + np.exp(-(X @ w + b)))


def evaluate(rows: list[dict], per_day: float, l2: float) -> dict:
    days = sorted({r["example_id"] for r in rows})
    out_scores = np.zeros(len(rows))
    for day in days:
        train = [r for r in rows if r["example_id"] != day]
        test_idx = [i for i, r in enumerate(rows) if r["example_id"] == day]
        if not train or not any(r["label"] for r in train):
            continue  # leave-one-day-out needs another day with a ticket
        Xtr, cols, vocab = design(train)
        Xtr, mu, sd = standardise(Xtr)
        ytr = np.array([r["label"] for r in train], dtype=float)
        if ytr.sum() == 0:
            continue
        w, b = fit_logistic(Xtr, ytr, l2=l2)
        Xte, _, _ = design([rows[i] for i in test_idx], vocab)
        Xte, _, _ = standardise(Xte, mu, sd)
        out_scores[test_idx] = scores(Xte, w, b)
    # the operating point: the threshold that admits per_day candidates a session on average
    n_days = len(days)
    order = np.argsort(-out_scores)
    k = int(round(per_day * n_days))
    threshold = out_scores[order[k - 1]] if k <= len(rows) else 0.0
    admitted = out_scores >= threshold
    y = np.array([r["label"] for r in rows])
    recall = float((admitted & (y == 1)).sum() / max(1, y.sum()))
    density = float(admitted.sum() / n_days)
    # by-day view: rank of the positive within its day
    ranks = {}
    for day in days:
        idx = [i for i, r in enumerate(rows) if r["example_id"] == day]
        srt = sorted(idx, key=lambda i: -out_scores[i])
        for pos_i in [i for i in idx if rows[i]["label"] == 1]:
            ranks[f'{day} {rows[pos_i]["branch"]}/{rows[pos_i]["mode"]}'] = srt.index(pos_i) + 1
    # a full fit on all rows for the weights
    Xa, cols, vocab = design(rows)
    Xa, mu, sd = standardise(Xa)
    wa, ba = fit_logistic(Xa, np.array([r["label"] for r in rows], dtype=float), l2=l2)
    weights = sorted(zip(cols, wa), key=lambda kv: -abs(kv[1]))
    # chance: admitting per_day of the candidates a session at random recovers
    # per_day / (candidates a session) of the tickets
    chance = min(1.0, per_day * n_days / max(1, len(rows)))
    return {
        "rows": len(rows), "positives": int(y.sum()), "days": n_days, "per_day_target": per_day,
        "candidates_per_day": round(len(rows) / n_days, 1), "chance_recall_at_density": round(chance, 3),
        "threshold": float(threshold), "density_at_threshold": round(density, 2), "recall_at_density": round(recall, 3),
        "recall_top1": round(float(sum(1 for v in ranks.values() if v <= 1) / max(1, len(ranks))), 3),
        "recall_top3": round(float(sum(1 for v in ranks.values() if v <= 3) / max(1, len(ranks))), 3),
        "recall_top5": round(float(sum(1 for v in ranks.values() if v <= 5) / max(1, len(ranks))), 3),
        "median_rank_of_ticket": float(np.median(list(ranks.values()))) if ranks else None,
        "positive_ranks": ranks,
        "weights_top": [(c, round(float(w), 3)) for c, w in weights[:18]],
    }


def main(argv=None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--rows", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--per-day", type=float, default=2.0, help="the authors' density: candidates a session the threshold admits")
    parser.add_argument("--l2", type=float, default=2.0)
    args = parser.parse_args(argv)
    rows = load(args.rows)
    report = {}
    for family in sorted({r["family"] for r in rows}):
        fam_rows = [r for r in rows if r["family"] == family]
        report[family] = evaluate(fam_rows, args.per_day, args.l2)
        summary = {k: v for k, v in report[family].items() if k not in ("positive_ranks", "weights_top")}
        print(json.dumps({"family": family, **summary}))
        print("   weights:", report[family]["weights_top"][:10])
        print("   ticket ranks:", report[family]["positive_ranks"])
    args.out.mkdir(parents=True, exist_ok=True)
    (args.out / "GRADING_FIT.json").write_text(json.dumps(report, indent=1) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
