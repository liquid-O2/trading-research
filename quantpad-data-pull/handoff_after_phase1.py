#!/usr/bin/env python3
"""Finish Phase 1, validate it, and hand the remaining pull to RunPod."""

from __future__ import annotations

import argparse
import os
import re
import subprocess
import sys
import tarfile
import time
from datetime import UTC, datetime
from pathlib import Path


ROOT = Path(__file__).resolve().parent
SSH_HOST = "r3dikublyiq57e-644117e8@ssh.runpod.io"
SSH_KEY = Path("/Users/arunavayun/.ssh/id_ed25519")
REMOTE_ROOT = Path("/workspace/quantpad-data-pull")


def run(args: list[str], *, check: bool = True) -> subprocess.CompletedProcess:
    print("+", " ".join(args), flush=True)
    return subprocess.run(args, cwd=ROOT, check=check, text=True)


def ssh(command: str) -> list[str]:
    return [
        "ssh",
        "-i",
        str(SSH_KEY),
        "-o",
        "StrictHostKeyChecking=accept-new",
        SSH_HOST,
        command,
    ]


def wait_for_pid(pid: int) -> None:
    print(f"Waiting for active Phase 1 process {pid}", flush=True)
    while True:
        try:
            os.kill(pid, 0)
        except ProcessLookupError:
            return
        time.sleep(15)


def finish_phase1() -> None:
    for attempt in range(1, 5):
        result = run(
            [
                "uv",
                "run",
                "python",
                "pull_quantpad.py",
                "run",
                "--phase",
                "1",
                "--keep-going",
                "--partition-retries",
                "3",
            ],
            check=False,
        )
        valid = run(
            ["uv", "run", "python", "validate_phase1.py"], check=False
        )
        if result.returncode == 0 and valid.returncode == 0:
            return
        if attempt < 4:
            print(f"Phase 1 retry {attempt} was incomplete; retrying", flush=True)
            time.sleep(60)
    raise RuntimeError("Phase 1 did not validate after four complete passes")


def build_archive() -> Path:
    stamp = datetime.now(tz=UTC).strftime("%Y%m%dT%H%M%SZ")
    archive = Path("/tmp") / f"quantpad-phase1-{stamp}.tar"
    excluded_roots = {
        ".env",
        ".git",
        ".venv",
        ".DS_Store",
        "__pycache__",
        "_superseded",
        "logs",
    }

    def include(info: tarfile.TarInfo) -> tarfile.TarInfo | None:
        parts = Path(info.name).parts
        if any(part in excluded_roots for part in parts):
            return None
        if info.name.endswith(".part"):
            return None
        return info

    print(f"Creating secret-free archive {archive}", flush=True)
    with tarfile.open(archive, "w") as handle:
        handle.add(ROOT, arcname=".", filter=include)
    return archive


def transfer(archive: Path) -> None:
    sender_log = ROOT / "logs" / "runpodctl-send.log"
    sender_log.parent.mkdir(parents=True, exist_ok=True)
    print(f"Starting runpodctl transfer for {archive.name}", flush=True)
    with sender_log.open("w", encoding="utf-8") as output:
        sender = subprocess.Popen(
            ["runpodctl", "send", str(archive)],
            cwd=ROOT,
            stdout=output,
            stderr=subprocess.STDOUT,
            text=True,
        )
        code = None
        deadline = time.monotonic() + 60
        while time.monotonic() < deadline:
            text = sender_log.read_text(encoding="utf-8", errors="replace")
            match = re.search(r"runpodctl receive\s+(\S+)", text)
            if match:
                code = match.group(1)
                break
            if sender.poll() is not None:
                break
            time.sleep(0.5)
        if code is None:
            sender.terminate()
            sender.wait(timeout=10)
            raise RuntimeError(
                f"runpodctl did not generate a receive code; see {sender_log}"
            )
        receive = run(
            ssh(f"cd /workspace\nexec runpodctl receive {code}"), check=False
        )
        sender_code = sender.wait(timeout=600)
    if receive.returncode != 0 or sender_code != 0:
        raise RuntimeError(
            f"runpodctl transfer failed: receive={receive.returncode}, "
            f"send={sender_code}; see {sender_log}"
        )


def configure_remote(archive: Path) -> None:
    run(ssh(f"mkdir -p {REMOTE_ROOT}"))
    remote_archive = Path("/workspace") / archive.name
    run(ssh(f"tar -xf {remote_archive} -C {REMOTE_ROOT}"))
    run(
        [
            "scp",
            "-i",
            str(SSH_KEY),
            "-o",
            "StrictHostKeyChecking=accept-new",
            str(ROOT / ".env"),
            f"{SSH_HOST}:{REMOTE_ROOT}/.env",
        ]
    )
    run(ssh(f"chmod 600 {REMOTE_ROOT}/.env"))
    run(ssh(f"bash {REMOTE_ROOT}/start_on_runpod.sh"))
    run(ssh("df -h /workspace"))
    run(ssh(f"tail -n 20 {REMOTE_ROOT}/logs/remaining.log"), check=False)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--wait-pid", type=int)
    args = parser.parse_args()

    if args.wait_pid:
        wait_for_pid(args.wait_pid)
    finish_phase1()
    archive = build_archive()
    transfer(archive)
    configure_remote(archive)
    print("RunPod handoff completed successfully", flush=True)
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"HANDOFF ERROR: {type(exc).__name__}: {exc}", file=sys.stderr)
        raise
