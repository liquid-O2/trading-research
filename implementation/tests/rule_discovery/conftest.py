"""No test in this directory may build a derived event window.

Synthetic tape fixtures carry a placeholder instrument id, so any adapter call
that reaches ``HistoricalFeatures.prior`` on one asks the shared cache for a
window that does not exist and the cache writes an empty (row_count 0) entry
under /workspace/data. That directory is frozen input, not a scratch space, so
the write guard is installed for the whole session: a cache hit still reads, a
cache miss raises CacheWriteBlocked, and the adapters record it as a named
omission exactly as they do in the runner, which installs the same guard.
"""
from __future__ import annotations

import pytest

from trading_research.research.rule_discovery.native import install_write_guard


@pytest.fixture(scope="session", autouse=True)
def _no_derived_cache_writes():
    install_write_guard()
    yield
