"""If the census is incomplete, write only a wiki/log.md entry naming failed dates."""
from __future__ import annotations

from pathlib import Path
import json

ROOT = Path("/workspace")
RUN_ROOT = Path(__file__).resolve().parent


def main():
    progress = json.loads((RUN_ROOT / "PROGRESS.json").read_text())
    failed = list(progress.get("failed_dates") or [])
    jobs = RUN_ROOT / "jobs"
    remaining = sorted(
        path.name
        for path in jobs.iterdir()
        if path.is_dir() and path.name[:1].isdigit() and not (path / "completion.json").exists()
    )
    named = failed or remaining
    path = ROOT / "wiki/log.md"
    text = path.read_text()
    marker = "## 2026-09-14 — B0.1 full-history measurement incomplete"
    if marker in text:
        return
    entry = f"""# Ingest log

{marker}

B0.1 full-history run `{RUN_ROOT.name}` did not finish. Failed or unfinished dates: {', '.join(named) if named else '(none listed)'}. SUMMARY.json / RUN_COMPLETE.json / wiki/current-status.md / PROJECT_HANDOFF.md were not updated. Frozen method_pack and run-1.0.1 were not edited. Subphase 03 was not started.

Evidence: [{RUN_ROOT}]({RUN_ROOT}/).

"""
    if not text.startswith("# Ingest log\n"):
        raise SystemExit("wiki/log.md missing ingest header")
    path.write_text(entry + text[len("# Ingest log\n"):])
    print("wrote incomplete log entry", named[:20], "n", len(named))


if __name__ == "__main__":
    main()
