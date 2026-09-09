#!/usr/bin/env python3
"""Launch one scoped Cursor assignment; retain logs and an explicit resume ID."""

import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import time
import uuid

ROOT = Path(__file__).resolve().parent
MODEL = "cursor-grok-4.6-xhigh-fast"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("assignment", type=Path)
    parser.add_argument("--workspace", type=Path, default=ROOT)
    parser.add_argument("--resume")
    parser.add_argument("--edit", action="store_true")
    parser.add_argument("--timeout", type=int, default=1800)
    args = parser.parse_args()
    assignment = args.assignment.resolve(strict=True)
    workspace = args.workspace.resolve(strict=True)
    if args.timeout <= 0:
        parser.error("timeout must be positive")
    if args.edit and not workspace.is_relative_to(ROOT / "worktrees"):
        parser.error("edits require an isolated checkout under this worker's worktrees directory")
    if not (workspace / ".cursor" / "cli.json").is_file():
        parser.error("the workspace needs explicit Cursor permissions before launch")
    executable = shutil.which("agent")
    if executable is None:
        parser.error("Cursor agent CLI is unavailable")

    run = ROOT / "runs" / (datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ-") + uuid.uuid4().hex[:8])
    run.mkdir(parents=True)
    brief = assignment.read_bytes()
    (run / "assignment.md").write_bytes(brief)
    command = [executable, "--model", MODEL, "--sandbox", "disabled", "--trust",
               "--workspace", str(workspace), "-p", "--output-format", "stream-json"]
    # The host cannot start Cursor's OS sandbox. Project permissions remain
    # active; read-only launches also use the CLI's explicit ask mode.
    if not args.edit:
        command.extend(["--mode", "ask"])
    else:
        command.append("--force")
    if args.resume:
        command.extend(["--resume", args.resume])
    command.append("Execute the assignment below. Follow its scope and stop conditions.\n\n" + brief.decode())
    started = time.monotonic()
    launch = {"model": MODEL, "workspace": str(workspace), "edit": args.edit,
              "assignment_sha256": hashlib.sha256(brief).hexdigest(),
              "resume_session_id": args.resume, "timeout_seconds": args.timeout,
              "started_at": datetime.now(timezone.utc).isoformat()}
    print(str(run), flush=True)
    with (run / "events.jsonl").open("w") as out, (run / "stderr.log").open("w") as err:
        process = subprocess.Popen(command, cwd=workspace, stdout=out, stderr=err)
        launch["pid"] = process.pid
        (run / "launch.json").write_text(json.dumps(launch, indent=2) + "\n")
        timed_out = False
        try:
            code = process.wait(timeout=args.timeout)
        except subprocess.TimeoutExpired:
            timed_out = True
            process.terminate()
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait()
            code = 124
        except KeyboardInterrupt:
            process.terminate()
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait()
            code = 130

    result = {"exit_code": code, "timed_out": timed_out,
              "wall_seconds": time.monotonic() - started,
              "finished_at": datetime.now(timezone.utc).isoformat()}
    with (run / "events.jsonl").open() as events:
        for line in events:
            try:
                event = json.loads(line)
            except json.JSONDecodeError:
                continue
            if event.get("type") == "system":
                result.update(session_id=event.get("session_id"), reported_model=event.get("model"))
            if event.get("type") == "result":
                result["result"] = event
    (run / "completion.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result), flush=True)
    if code:
        print((run / "stderr.log").read_text()[-2000:], flush=True)
    return code


if __name__ == "__main__":
    raise SystemExit(main())
