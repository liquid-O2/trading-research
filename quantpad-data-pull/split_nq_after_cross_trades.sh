#!/bin/sh
set -eu

task_root=/workspace/quantpad-data-pull
cd "$task_root"

cross_pid=$(cat manifests/cross-index-trades.pid)
while kill -0 "$cross_pid" 2>/dev/null; do
    sleep 30
done

# Only repurpose the slot after every requested RTY annual partition exists.
for rty_year in 2020 2021 2022 2023 2024 2025 2026; do
    rty_path="data/phase-4/glbx-mdp3/rty-c-0/trades/$rty_year.parquet"
    if [ ! -s "$rty_path" ]; then
        echo "RTY verification failed: missing $rty_path" >&2
        exit 1
    fi
done

nq_pid=$(cat manifests/nq-mbp1-monthly.pid)
if kill -0 "$nq_pid" 2>/dev/null; then
    # Let the active month finish, then stop the original unbounded worker as
    # soon as it opens the next month. This preserves the current checkpoint.
    completed_before=$(grep -c '"spec_id": "06-nq-mbp1"' logs/nq-mbp1-monthly.log || true)
    while kill -0 "$nq_pid" 2>/dev/null; do
        completed_now=$(grep -c '"spec_id": "06-nq-mbp1"' logs/nq-mbp1-monthly.log || true)
        if [ "$completed_now" -gt "$completed_before" ]; then
            break
        fi
        sleep 5
    done

    nq_children=$(pgrep -P "$nq_pid" || true)
    if [ -n "$nq_children" ]; then
        kill -TERM $nq_children 2>/dev/null || true
    fi
    kill -TERM "$nq_pid" 2>/dev/null || true
    sleep 5

    if kill -0 "$nq_pid" 2>/dev/null; then
        echo "Original NQ worker did not stop; refusing overlapping split" >&2
        exit 1
    fi
    for nq_child in $nq_children; do
        if kill -0 "$nq_child" 2>/dev/null; then
            echo "Original NQ child $nq_child did not stop; refusing overlap" >&2
            exit 1
        fi
    done
fi

nohup uv run python pull_quantpad.py run \
    --id 06-nq-mbp1 \
    --start 2020-01-01 \
    --end 2024-07-01 \
    --keep-going \
    --partition-retries 5 \
    > logs/nq-mbp1-split-early.log 2>&1 < /dev/null &
early_pid=$!
echo "$early_pid" > manifests/nq-mbp1-split-early.pid

nohup uv run python pull_quantpad.py run \
    --id 06-nq-mbp1 \
    --start 2024-07-01 \
    --keep-going \
    --partition-retries 5 \
    > logs/nq-mbp1-split-late.log 2>&1 < /dev/null &
late_pid=$!
echo "$late_pid" > manifests/nq-mbp1-split-late.pid

echo "Started bounded NQ workers: early=$early_pid late=$late_pid"
