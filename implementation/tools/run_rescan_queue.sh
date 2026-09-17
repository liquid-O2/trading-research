#!/usr/bin/env bash
# Sequential queue of rescan candidates (one population run each, its own run root).
# usage: run_rescan_queue.sh <candidates.json> <root-dir> [workers]
set -u
CANDS="$1"; ROOT="$2"; WORKERS="${3:-10}"
W=/workspace/.worktrees/fidelity-jj-gb/implementation
PY=/workspace/implementation/.venv/bin/python
mkdir -p "$ROOT"
N=$($PY -c "import json,sys; print(len(json.load(open(sys.argv[1]))))" "$CANDS")
for ((i=0; i<N; i++)); do
  NAME=$($PY -c "import json,sys; print(json.load(open(sys.argv[1]))[int(sys.argv[2])]['name'])" "$CANDS" "$i")
  OVR=$($PY -c "import json,sys; print(json.dumps(json.load(open(sys.argv[1]))[int(sys.argv[2])]['overrides']))" "$CANDS" "$i")
  OUT="$ROOT/$NAME"
  if [ -f "$OUT/POPULATION.json" ]; then echo "skip $NAME (done)"; continue; fi
  echo "start $NAME $(date -u +%FT%TZ)"
  PYTHONPATH=$W/src timeout 5400 $PY $W/tools/run_jj_gb_population.py --out "$OUT" --workers "$WORKERS" --scanner-overrides "$OVR" > "$ROOT/$NAME.log" 2>&1
  echo "done $NAME exit $? $(date -u +%FT%TZ)"
done
echo "queue complete"
