#!/bin/sh
set -u

project_root=/workspace/quantpad-data-pull
terminal_url='http://127.0.0.1:25503/v3/option/list/symbols?format=json'

cd "$project_root" || exit 1

restart_terminal() {
    echo "$(date -u +%FT%TZ) restarting Theta Terminal" >&2

    if [ -f manifests/thetadata-terminal.pid ]; then
        launcher_pid=$(sed -n '1p' manifests/thetadata-terminal.pid)
        if [ -n "$launcher_pid" ] && kill -0 "$launcher_pid" 2>/dev/null; then
            kill -TERM "$launcher_pid" 2>/dev/null || true
        fi
    fi

    wait_count=0
    while pgrep -f '[T]hetaTerminalv3.jar\|thetadata/lib/.*\.jar' >/dev/null 2>&1; do
        wait_count=$((wait_count + 1))
        [ "$wait_count" -ge 20 ] && break
        sleep 1
    done

    nohup java -jar thetadata/ThetaTerminalv3.jar \
        --dotenv-dir "$project_root" >> logs/thetadata-terminal.log 2>&1 < /dev/null &
    echo "$!" > manifests/thetadata-terminal.pid

    ready_count=0
    while [ "$ready_count" -lt 30 ]; do
        if curl -fsS --max-time 5 "$terminal_url" -o /dev/null; then
            echo "$(date -u +%FT%TZ) Theta Terminal ready" >&2
            return 0
        fi
        ready_count=$((ready_count + 1))
        sleep 2
    done

    echo "$(date -u +%FT%TZ) Theta Terminal failed readiness check" >&2
    return 1
}

if ! curl -fsS --max-time 5 "$terminal_url" -o /dev/null; then
    until restart_terminal; do sleep 15; done
fi

if [ "$#" -eq 0 ]; then
    set -- pull-2 pull-3
fi

for pull_name in "$@"; do
    until uv run python pull_thetadata.py run --pull "$pull_name" --retries 8; do
        until restart_terminal; do sleep 15; done
        sleep 5
    done
done
