#!/usr/bin/env bash
set -euo pipefail

cd /workspace/quantpad-data-pull
mkdir -p logs manifests
chmod 600 .env

if command -v uv >/dev/null 2>&1; then
  uv_bin="$(command -v uv)"
elif [[ -x /root/.local/bin/uv ]]; then
  uv_bin=/root/.local/bin/uv
else
  curl --proto '=https' --tlsv1.2 -LsSf \
    https://astral.sh/uv/install.sh \
    -o /tmp/quantpad-uv-installer.sh
  sh /tmp/quantpad-uv-installer.sh
  uv_bin=/root/.local/bin/uv
fi

"${uv_bin}" sync --frozen
nohup "${uv_bin}" run python pull_quantpad.py run \
  --phase 2 \
  --keep-going \
  --partition-retries 3 \
  > logs/remaining.log 2>&1 < /dev/null &
runpod_pid=$!
echo "${runpod_pid}" > manifests/runpod.pid
echo "Started QuantPad downloader as PID ${runpod_pid}"
