#!/usr/bin/env bash
# Evaluate every finished rescan candidate under the given roots that has no
# fold read yet: a candidate is finished when its POPULATION.json reports no
# failures; the family is the candidate name's prefix (JJ -> JJ-TBR, GB ->
# GB-FAIL). Prints one line per candidate evaluated or skipped.
#
#   evaluate_finished_rescans.sh <baseline rows.jsonl> <eval root> <rescan root>...
set -u
BASE="$1"; EVAL_ROOT="$2"; shift 2
W="${WORKTREE_IMPL:-/workspace/.worktrees/phase15/implementation}"
PY=/workspace/implementation/.venv/bin/python
mkdir -p "$EVAL_ROOT"
for root in "$@"; do
  for dir in "$root"/*/; do
    name=$(basename "$dir")
    [ -f "$dir/POPULATION.json" ] || continue
    case "$name" in *-merged|*-2|ruined-*) continue;; esac
    out="$EVAL_ROOT/eval-rescan-$name"
    [ -f "$out/VARIANTS.md" ] && continue
    status=$($PY -c "import json; d=json.load(open('$dir/POPULATION.json')); print('ok' if not d.get('failures') and (d.get('n_dates_complete') or 0) >= 1742 else 'incomplete %s/%s' % (d.get('n_dates_complete'), len(d.get('failures') or [])))")
    if [ "$status" != "ok" ]; then echo "skip $name ($status)"; continue; fi
    case "$name" in JJ-*) fam=JJ-TBR;; GB-*) fam=GB-FAIL;; *) echo "skip $name (unknown family)"; continue;; esac
    PYTHONPATH="$W/src" timeout 1800 $PY "$W/tools/evaluate_variants.py" --rows "$BASE" --out "$out" --families "$fam" --rescan "$name=$dir/rows.jsonl" > "$out.log" 2>&1
    echo "evaluated $name exit $?: $(grep "^| $name" "$out/VARIANTS.md" 2>/dev/null | cut -c1-300)"
  done
done
