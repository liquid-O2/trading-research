"""The selection fitter must find a planted signal out of sample, credit the
feature that carries it and not the one that does not, find nothing in
shuffled labels, and never read the Phase 2 hold-out."""
import importlib.util
import json
import sys
from pathlib import Path

import numpy as np
import pytest

TOOL = Path(__file__).resolve().parents[2] / "tools/fit_selection.py"


def _tool():
    spec = importlib.util.spec_from_file_location("fit_selection", TOOL)
    module = importlib.util.module_from_spec(spec)
    sys.modules["fit_selection"] = module
    spec.loader.exec_module(module)
    return module


def _rows(seed: int, shuffle: bool):
    rng = np.random.default_rng(seed)
    rows = []
    for year in (2021, 2022, 2023, 2024, 2025, 2026):
        for d in range(60):
            month = 1 + d % 12 if year < 2026 else 1 + d % 3  # 2026 rows stay before the April hold-out ...
            for _ in range(12):
                signal, noise = rng.normal(), rng.normal()
                held = rng.random() < 1 / (1 + np.exp(-1.5 * signal))
                rows.append({"session": f"{year}-{month:02d}-{1 + d % 27:02d}", "signal": signal, "noise": noise, "sometimes": None if rng.random() < 0.3 else noise * 0.1, "label_outcome": "held" if held else "broke", "label_mfe_15": 10.0 + 5 * held, "label_mae_15": 10.0})
    rows.append({"session": "2026-05-04", "signal": 99.0, "noise": 0.0, "sometimes": None, "label_outcome": "held", "label_mfe_15": 1.0, "label_mae_15": 1.0})  # ... except this one
    if shuffle:
        labels = [r["label_outcome"] for r in rows]
        rng.shuffle(labels)
        for r, lab in zip(rows, labels):
            r["label_outcome"] = lab
    return rows


@pytest.mark.parametrize("shuffle", [False, True], ids=["planted signal", "shuffled labels"])
def test_selection_fit_controls(tmp_path, shuffle):
    tool = _tool()
    rows = _rows(7, shuffle)
    path = tmp_path / "rows.jsonl"
    path.write_text("\n".join(json.dumps(r) for r in rows) + "\n")
    assert tool.main(["--rows", str(path), "--out", str(tmp_path / "fit")]) == 0
    fit = json.loads((tmp_path / "fit/SELECTION_FIT.json").read_text())
    assert fit["rows"] == len(rows) - 1  # the hold-out row was not read
    if shuffle:
        assert 0.45 < fit["auc_out_of_sample"] < 0.55
        assert abs(fit["deciles"][-1]["label_rate"] - fit["deciles"][0]["label_rate"]) < 0.12
    else:
        assert fit["auc_out_of_sample"] > 0.72
        assert fit["single_feature_auc"]["signal"] > 0.72 and abs(fit["single_feature_auc"]["noise"] - 0.5) < 0.05
        assert fit["deciles"][-1]["label_rate"] - fit["deciles"][0]["label_rate"] > 0.4
        assert fit["top_k_per_day"][0]["label_rate"] > fit["base_rate"] + 0.15
        assert abs(fit["coefficients_standardized_mean"]["signal"]) > 5 * abs(fit["coefficients_standardized_mean"]["noise"])
