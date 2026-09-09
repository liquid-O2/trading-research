#!/usr/bin/env python3
"""Run the authorized ES option batch pull using the verified batch workflow."""

from __future__ import annotations

import os

import databento_nq_options as batch


batch.MANIFEST_PATH = batch.ROOT / "manifests" / "databento-es-options-2020.json"
batch.OUTPUT_ROOT = batch.Path(
    os.environ.get(
        "DATABENTO_ES_OUTPUT",
        str(batch.ROOT / "data" / "databento" / "glbx-mdp3" / "es-opt"),
    )
)
batch.SYMBOL = "ES.OPT"
batch.AUTHORIZED_COST_CAP_USD = 81.00


if __name__ == "__main__":
    raise SystemExit(batch.main())
