"""C07 report arithmetic, atomic JSON/Markdown/trace writes, headline printer."""

from __future__ import annotations

from datetime import datetime, timezone
from fractions import Fraction
from pathlib import Path
import hashlib
import json
import os
import subprocess
import tempfile

from trading_research.research.method_pack import FORMULA_VERSION, HEADLINE, SOURCE_WIKI_COMMIT, SLUGS


STATUSES = frozenset({
    "not_run",
    "implementation_fail",
    "checks_passed",
    "source_hole",
    "data_hole",
    "measured",
    "no_candidates",
})
PHASE_TABLE = 'family | variant | n | faithful_disagreements | status | report path'
AUDIT_TABLE = 'family | id | verdict | fixture | leakage | proxy-as-faithful | notes'


def summary_status(summary: dict, implementation_status: str) -> str:
    """Name the check result and the distinct observation/discovery result."""
    if implementation_status != 'checks_passed':
        return implementation_status
    if summary.get('search_status') == 'unavailable':
        evidence_status = 'historical_unavailable'
    elif summary['u']:
        evidence_status = 'evidence_incomplete'
    elif summary['N']:
        evidence_status = 'observations_scored'
    else:
        evidence_status = 'no_observations'
    return f'{implementation_status}; {evidence_status}'


def family_tables(doc: dict, report_path: str) -> tuple[list[str], list[str]]:
    """Required family tables retain unavailable denominators explicitly."""
    method = doc['identity']['method_id']
    phase = [PHASE_TABLE]
    for summary in doc['summaries']:
        unavailable = summary.get('search_status') == 'unavailable'
        variant = f"{summary['predicate']} / {summary['cohort']}"
        n = '—' if unavailable else summary['n']
        # A rule verdict is not a matched source-versus-reconstruction audit.
        # No faithful disagreement count exists without that paired evidence.
        phase.append(f"{method} | {variant} | {n} | — | {summary_status(summary, doc['status'])} | {report_path}")
    from .catalog import METHOD_BY_ID
    q = doc['quality']
    historical = doc.get('dimensions', {}).get('historical_discovery', {}).get('status', 'unreported')
    notes = f"implementation checks; historical discovery {historical}; source agreement separate; schema failures={q.get('output_schema_failures', 0)}; missing bindings={q.get('missing_operand_implementations', 0)}"
    audit = [AUDIT_TABLE,
        f"{method} | {METHOD_BY_ID[method]} | {doc['status']} | {q['fixture_failures']} failures | {q['leakage_count']} | {q['proxy_as_faithful_count']} | {notes}"]
    return phase, audit


def counts(verdicts: list[str]) -> dict:
    if any(v not in {'pass', 'fail', 'unknown'} for v in verdicts):
        raise ValueError('unknown verdict in report cohort')
    p = sum(1 for v in verdicts if v == "pass")
    f = sum(1 for v in verdicts if v == "fail")
    u = sum(1 for v in verdicts if v == "unknown")
    n = p + f
    n_all = n + u
    rate = None if n == 0 else p / n
    if n_all == 0:
        interval = None
        interval_exact = None
    else:
        lo = Fraction(p, n_all)
        hi = Fraction(p + u, n_all)
        interval = [float(lo), float(hi)]
        interval_exact = [[lo.numerator, lo.denominator], [hi.numerator, hi.denominator]]
    return {
        "p": p,
        "f": f,
        "u": u,
        "n": n,
        "N": n_all,
        "rate": rate,
        "rate_exact": None if n == 0 else [p, n],
        "interval": interval,
        "interval_exact": interval_exact,
    }


def c07_f1() -> dict:
    block = counts(["pass"] * 8 + ["fail"] * 2 + ["unknown"] * 2)
    y2025 = counts(["pass"] * 3 + ["fail"] * 1 + ["unknown"] * 1)
    y2026 = counts(["pass"] * 5 + ["fail"] * 1 + ["unknown"] * 1)
    empty = counts([])
    return {
        "n": block["n"],
        "N": block["N"],
        "rate": block["rate"],
        "interval": block["interval"],
        "interval_exact": block["interval_exact"],
        "year_n_sum": y2025["n"] + y2026["n"],
        "empty_rate": empty["rate"],
        "empty_interval": empty["interval"],
    }


def format_rate(rate: float | None) -> str:
    if rate is None:
        return "—"
    return f"{rate:.6f}"


def format_interval(interval: list[float] | None) -> str:
    if interval is None:
        return "—"
    return f"[{interval[0]:.6f},{interval[1]:.6f}]"


def format_year_split(years: dict | None) -> str:
    if not years:
        return "—"
    parts = []
    for year in sorted(years):
        row = years[year]
        n = row.get("n", 0)
        parts.append(f"{year}:{n}")
    return ";".join(parts) if parts else "—"


def headline_row(method_id: str, predicate: str, summary: dict, status: str, report_path: str) -> str:
    unavailable = summary.get('search_status') == 'unavailable'
    n = '—' if unavailable else summary['n']
    years = '—' if unavailable else format_year_split(summary.get('years'))
    return (
        f"{method_id} | {predicate} | {n} | "
        f"{format_rate(summary.get('rate'))} | {format_interval(summary.get('interval'))} | "
        f"{years} | {status} | {report_path}"
    )


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    sha = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            sha.update(chunk)
    return sha.hexdigest()


def section_hash(text: str, start: str, end: str | None) -> str:
    i = text.find(start)
    if i < 0:
        return sha256_bytes(b"")
    if end:
        j = text.find(end, i + 1)
        chunk = text[i:j] if j >= 0 else text[i:]
    else:
        chunk = text[i:]
    return sha256_bytes(chunk.encode("utf-8"))


def implementation_identity(root: Path) -> dict:
    try:
        sha = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=root, text=True).strip()
        dirty = bool(subprocess.check_output(["git", "status", "--porcelain"], cwd=root).strip())
    except (subprocess.CalledProcessError, FileNotFoundError):
        sha = "unknown"
        dirty = True
    digest = hashlib.sha256()
    package = root / 'implementation'
    for path in sorted([*package.joinpath('src').rglob('*.py'), *package.joinpath('tools').glob('*.py')]):
        digest.update(str(path.relative_to(root)).encode())
        digest.update(path.read_bytes())
    return {"implementation_version": sha, "implementation_dirty": dirty,
            "implementation_dirty_hash": digest.hexdigest()}


def write_atomic(path: Path, payload: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(prefix=".pending-", suffix=path.suffix, dir=str(path.parent))
    try:
        with os.fdopen(fd, "wb") as handle:
            handle.write(payload)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(tmp, path)
    finally:
        if os.path.exists(tmp):
            os.unlink(tmp)


def write_json(path: Path, doc: dict) -> str:
    payload = json.dumps(doc, indent=2, sort_keys=True, default=_json_default).encode("utf-8")
    write_atomic(path, payload)
    return sha256_bytes(payload)


def write_text(path: Path, text: str) -> str:
    payload = text.encode("utf-8")
    write_atomic(path, payload)
    return sha256_bytes(payload)


def _json_default(value):
    if isinstance(value, Fraction):
        return [value.numerator, value.denominator]
    if isinstance(value, datetime):
        return value.isoformat()
    return str(value)


def markdown_twin(doc: dict, headlines: list[str]) -> str:
    identity = doc["identity"]
    summary = doc["summary"]
    lines = [
        f"# {identity['method_id']} method pass",
        "",
        f"formula_version: `{identity['formula_version']}`",
        f"implementation_checks: `{doc['status']}`",
        f"historical_discovery: `{doc.get('dimensions', {}).get('historical_discovery', {}).get('status', 'unreported')}`",
        f"created_at: `{identity['created_at']}`",
        "",
        "Implementation checks, source reconstruction and historical discovery are separate results. "
        "A passing check verifies the report's implementation evidence; it does not establish "
        "every private source setting or a historical sample.",
        "",
        "## Headline",
        "",
        HEADLINE,
        '--- | --- | --- | --- | --- | --- | --- | ---',
        *[f"{row}" for row in headlines],
        "",
        "## Summary",
        "",
        f"- predicate: {summary.get('predicate')}",
        '- Historical counts: unavailable (search not completed).' if summary.get('search_status') == 'unavailable'
        else f"- p={summary.get('p')} f={summary.get('f')} u={summary.get('u')} n={summary.get('n')} N={summary.get('N')}",
        f"- rate: {format_rate(summary.get('rate'))}",
        f"- interval: {format_interval(summary.get('interval'))}",
        f"- candidate_discovery: {doc.get('scope', {}).get('candidate_discovery')}",
        '- Synthetic fixtures, chart geometry checks and archive rows are excluded from p/f/u/n/N.',
        "",
        "## Candidate selector review",
        "",
    ]
    review = doc.get('discovery_audit') or {}
    if review:
        lines.extend([f"Audit: `{review['audit_version']}`; source contracts checked against their recorded hashes.",
                      '', 'branch | complete selector | unavailable inputs', '--- | --- | ---'])
        for branch, row in review['branches'].items():
            lines.append(f"{branch} | no | {', '.join(row['missing_fields'])}")
        lines.extend(['', next(iter(review['branches'].values()))['reason'],
                      '', 'Each branch has a candidate-selector record in the `holes.jsonl` artifact, including its producer rules.'])
    lines.extend(['', '## Branches', ''])
    for branch, row in [*(doc.get("branches") or {}).items(), *(doc.get("case_branches") or {}).items()]:
        if row.get('search_status') == 'unavailable':
            lines.append(f"- `{branch}` ({row.get('cohort')}): historical discovery unavailable; denominator unestablished.")
        else:
            lines.append(
                f"- `{branch}` ({row.get('cohort')}) p={row.get('p')} f={row.get('f')} u={row.get('u')} "
                f"n={row.get('n')} N={row.get('N')} status={row.get('status')}"
            )
        for cohort in row.get('cohorts', []):
            lines.append(f"- `{branch}` / {cohort['predicate']} / {cohort['cohort']} / {cohort['evidence_mode']}: "
                         f"p={cohort['p']} f={cohort['f']} u={cohort['u']} n={cohort['n']} N={cohort['N']}")
    lines.extend(['', '## Cohorts and years', '',
                  'predicate | cohort | mode | instrument | source versions | p | f | u | n | N | ET years',
                  '--- | --- | --- | --- | --- | --- | --- | --- | --- | --- | ---'])
    for row in doc['summaries']:
        unavailable = row.get('search_status') == 'unavailable'
        displayed_counts = ' | '.join('—' if unavailable else str(row[key]) for key in ('p', 'f', 'u', 'n', 'N'))
        years = '—' if unavailable else format_year_split(row['years'])
        lines.append(f"{row['predicate']} | {row['cohort']} | {row['evidence_mode']} | {row.get('instrument_id')} | {','.join(row.get('source_versions', []))} | {displayed_counts} | {years}")
    lines.extend(['', '## Coverage', '',
                  f"Historical study scope: `{doc['scope'].get('historical_study')}`.",
                  f"Archive requested span (inventory, not the method sample): `{doc['scope'].get('requested_date_span')}`.",
                  f"Observed file span: `{doc['scope'].get('actual_date_span')}`. File endpoints do not prove continuous coverage.",
                  f"Relevant files: {doc['coverage'].get('relevant_file_count', 0)}; disjoint owned tape intervals: {len(doc['ownership'])}.",
                  f"Partial years: {', '.join(doc['scope'].get('partial_endpoint_years', [])) or 'none' }.",
                  '', '## Validation', '',
                  f"Quality: `{json.dumps(doc['quality'], sort_keys=True)}`.",
                  f"Implementation: `{identity['implementation_version']}`; content hash `{identity['implementation_dirty_hash']}`."])
    lines.extend(['', '## Separate acceptance dimensions', ''])
    for name, detail in doc.get('dimensions', {}).items():
        lines.append(f"- {name}: `{json.dumps(detail, sort_keys=True)}`")
    lines.extend(['', 'Historical discovery is unavailable. Its denominator is unestablished; zero ledger rows do not report a completed search with zero candidates.'])
    phase, audit = family_tables(doc, str(Path(doc['artifacts']['cohort.json']['path']).parents[2] / f"{SLUGS[identity['method_id']]}.md"))
    lines.extend(['', '## Required family tables', '',
                  'Status reports implementation checks first, followed by the separately scoped evidence result. '
                  'The audit verdict covers implementation checks; unknown historical denominators remain unavailable.',
                  '', phase[0], '--- | --- | --- | --- | --- | ---', *phase[1:],
                  '', audit[0], '--- | --- | --- | --- | --- | --- | ---', *audit[1:]])
    lines.extend(["", "## Holes", ""])
    holes = doc.get("source_limitations") or []
    if not holes:
        lines.append("None recorded beyond the hole ledger artifact.")
    else:
        for hole in holes:
            lines.append(f"- {hole}")
    lines.extend(["", "## Artifacts", ""])
    for name, meta in (doc.get("artifacts") or {}).items():
        lines.append(f"- `{name}` {meta.get('path')} sha256={meta.get('sha256')}")
    lines.append("")
    return "\n".join(lines)


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
