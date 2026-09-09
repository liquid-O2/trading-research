#!/usr/bin/env bash
set -euo pipefail

cd /workspace/quantpad-data-pull
mkdir -p logs
uv sync --frozen
uv run python pull_quantpad.py run \
  --phase 2 \
  --keep-going \
  --partition-retries 3
