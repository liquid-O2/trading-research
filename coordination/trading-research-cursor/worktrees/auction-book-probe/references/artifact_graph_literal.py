"""Independent primitive full traversal and causal admission reference for F11.

No candidate imports, records, IDs or cached plan are used here.
"""
from fractions import Fraction
import hashlib
import json


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False).encode()


def identity(value):
    return hashlib.sha256(canonical(value)).hexdigest()


def closure(edges, roots):
    seen, active, depths = set(), set(), {}
    def visit(key):
        if key not in edges or key in active:
            raise ValueError("missing/cyclic graph")
        if key in seen:
            return depths[key]
        active.add(key)
        depth = 1
        for source in edges[key]:
            depth = max(depth, visit(source)+1)
        active.remove(key); seen.add(key); depths[key] = depth
        return depth
    maximum = max(visit(root) for root in roots)
    if seen != set(edges):
        raise ValueError("extra unreferenced nodes")
    return {"nodes": sorted(seen), "edges": sum(len(edges[k]) for k in seen), "depth": maximum}


def full_rebuild(nodes, roots):
    edges = {k: ([v["dependency"]] if "dependency" in v else []) for k,v in nodes.items()}
    shape = closure(edges, roots)
    values, counts = {}, {"source_reads": 0, "multiply": 0, "add": 0}
    def value(key):
        if key in values:
            return values[key]
        n = nodes[key]
        if n["op"] == "source":
            result = Fraction(n["value"][0], n["value"][1]); counts["source_reads"] += 1
        else:
            prior = value(n["dependency"])
            c = Fraction(n["constant"][0], n["constant"][1])
            if n["op"] == "multiply":
                result = prior*c; counts["multiply"] += 1
            elif n["op"] == "add":
                result = prior+c; counts["add"] += 1
            else:
                raise ValueError("unknown primitive operator")
        values[key] = result
        return result
    for root in roots:
        value(root)
    return values, counts, shape


def affected(edges, seeds):
    # Deliberately full repeated ancestral scans, independent of reverse indexing.
    closure(edges, tuple(edges))
    def depends(key, seed):
        return key == seed or any(depends(p, seed) for p in edges[key])
    changed = sorted(k for k in edges if any(depends(k,s) for s in seeds))
    return changed, sorted(set(edges)-set(changed))


def fold(samples, fit_at, start, end, embargo=0):
    rows = sorted(samples, key=lambda s: (s["decision"], s["id"]))
    evaluation = [s for s in rows if start <= s["decision"] < end]
    groups = {s["group"] for s in evaluation}
    if any(s["group"] in groups and not start <= s["decision"] < end for s in rows):
        raise ValueError("date group split")
    training, purged = [], []
    for s in rows:
        if s["decision"] >= start:
            continue
        if s["label_known"] > fit_at:
            purged.append([s["id"], "label_not_mature_at_fit"])
        elif s["dependency_end"] >= start-embargo:
            purged.append([s["id"], "dependency_interval_overlaps_evaluation_or_embargo"])
        else:
            training.append(s["id"])
    return {"training_ids": training, "evaluation_ids": [s["id"] for s in evaluation], "purged": purged}


def oof(ancestors, sample, group, cut, root_fold, routes):
    for key, a in ancestors.items():
        if (a["fold"] != routes.get(key, root_fold) or a["completion"] > cut
                or sample in a["training_ids"] or group in a["groups"]):
            raise ValueError("OOF exclusion/route/clock")
    return sorted(ancestors)


def prediction_available(prediction, assembled_at, valid_until=None):
    expiry = prediction["target_end"] if valid_until is None else min(prediction["target_end"], valid_until)
    return max(prediction["input_known_at"], prediction["actual_completion_at"]) <= assembled_at < expiry


def numerical_decision(a, b, threshold, tolerance):
    a, b, threshold, tolerance = (Fraction(*v) for v in (a,b,threshold,tolerance))
    return {"difference": abs(a-b), "within": abs(a-b) <= tolerance,
            "decisions": (a >= threshold, b >= threshold)}


def actual_reads(rows, requests, *, inference=True):
    """Finite primitive admission: no candidate records or serialization helpers."""
    if not requests or len(requests) > 128:
        raise ValueError("read count")
    identity = None
    result = []
    for q in requests:
        key=(q["sample"],q["cut"],q["assembled"],q["purpose"],q.get("target"))
        if identity is not None and identity != key: raise ValueError("mixed execution")
        identity=key
        r=rows[q["source"]]
        if inference and (r["role"]=="label" or q["purpose"] in ("audit","fit_label")):
            raise ValueError("inference label/audit")
        if r["known"]>q["cut"] or r["observed"]>q["cut"]:
            raise ValueError("future input")
        if r.get("until") is not None and q["assembled"]>=r["until"]:
            raise ValueError("expired original input")
        result.append(r["value"])
    return result


def retained_fit(sample, label, fit, evaluation_ids):
    if (sample["id"] not in evaluation_ids or fit["completion"] > sample["decision"]
            or sample["id"] in fit["training_ids"] or sample["group"] in fit["groups"]):
        raise ValueError("evaluation exclusion")
    if label is not None and (label["target"] != sample["target"] or label["start"] != sample["decision"]
                              or label["end"] != sample["dependency_end"] or label["known"] < label["end"]):
        raise ValueError("original target label")
    return True


def binary_probability(values, means, scales, coefficients, intercept):
    import math
    linear=intercept+sum(c*(x-m)/s for x,m,s,c in zip(values,means,scales,coefficients))
    return 1/(1+math.exp(-linear))
