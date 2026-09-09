"""Daily report-stock revisions, separately identified from transaction volume."""

from trading_research.errors import ContractError, IntegrityError
from trading_research.foundations.time import timestamp
from trading_research.measurements.common import bounded_rows, positive_limit
from trading_research.operations.artifacts import canonical_json, digest
from trading_research.research.label_ledger import OIReport


class OIReportChanges:
    def __init__(self, prior, *, max_reports=1024, max_bytes=8388608):
        if type(prior) is not OIReport:
            raise ContractError("report-change proxy requires the actual typed prior OI receipt")
        prior.__post_init__()
        self.prior = prior
        self.max_reports, self.max_bytes = positive_limit(max_reports), positive_limit(max_bytes)
        self.reports, self.consumed, self.queries = (), (), ()
        self._check_bytes(self.reports, self.consumed, self.queries)

    def _check_bytes(self, reports, consumed, queries):
        raw = canonical_json({"prior": self.prior, "reports": reports, "consumed": consumed,
            "queries": queries, "max_reports": self.max_reports, "max_bytes": self.max_bytes})
        if len(raw) > self.max_bytes:
            raise ContractError("OI complete retained state exceeds its byte capacity")
        return raw

    def append(self, report):
        if type(report) is not OIReport or report.contract != self.prior.contract:
            raise ContractError("OI report changes require one continuing raw contract")
        report.__post_init__()
        existing = next((r for r in (self.prior, *self.reports) if r.id == report.id), None)
        if existing is not None:
            if existing != report:
                raise IntegrityError("OI receipt identity was reused with different bytes")
            return False
        if len(self.reports) >= self.max_reports:
            raise ContractError("OI report retention requires explicit archival")
        same_date = [r for r in (self.prior, *self.reports) if r.position_date == report.position_date]
        predecessor = same_date[-1] if same_date else None
        if ((predecessor is None and report.supersedes is not None)
                or predecessor is not None and report.supersedes != predecessor.id
                or self.reports and report.known_at < self.reports[-1].known_at
                or report.known_at < self.prior.known_at
                or report.position_date < self.prior.position_date):
            raise ContractError("OI receipt must append an explicit point-in-time daily revision")
        staged = (*self.reports, report)
        self._check_bytes(staged, self.consumed, self.queries)
        self.reports = staged
        return True

    def observe(self, query_at):
        timestamp(query_at)
        if self.queries and query_at < self.queries[-1]:
            raise ContractError("report-consumption queries must advance in replay order")
        if len(self.queries) >= self.max_reports:
            raise ContractError("OI query retention requires explicit archival")
        if query_at < self.prior.known_at:
            return {"state": "unavailable", "events": (), "new_change": None}
        seen, events, previous = set(self.consumed), [], self.prior
        for report in self.reports:
            if report.known_at > query_at:
                break
            if report.id not in seen:
                events.append((report.id, report.position_date, report.known_at, report.count-previous.count))
                seen.add(report.id)
            previous = report
        consumed = tuple(r.id for r in self.reports if r.id in seen)
        queries = (*self.queries, query_at)
        self._check_bytes(self.reports, consumed, queries)
        self.consumed, self.queries = consumed, queries
        return {"state": "complete" if self.consumed else "unavailable", "events": tuple(events),
            "new_change": sum(e[3] for e in events) if self.consumed else None,
            "representation": "reported_oi_stock_change", "transaction_volume": None,
            "prior_receipt": self.prior.id, "source_revision": previous.id,
            "source_digest": digest((self.prior, tuple(r for r in self.reports if r.known_at <= query_at)))}

    def checkpoint(self):
        return self._check_bytes(self.reports, self.consumed, self.queries)

    @classmethod
    def restore(cls, payload, *, prior, reports, queries, max_reports=1024, max_bytes=8388608):
        bounded_rows(reports, max_reports, name="OI replay receipts")
        bounded_rows(queries, max_reports, name="OI replay queries")
        if type(payload) is not bytes or len(payload) > max_bytes:
            raise ContractError("OI replay exceeds the retained byte bound")
        book = cls(prior, max_reports=max_reports, max_bytes=max_bytes)
        for r in reports:
            book.append(r)
        for at in queries:
            book.observe(at)
        if book.checkpoint() != payload:
            raise IntegrityError("OI checkpoint differs from actual receipt/query replay")
        return book
