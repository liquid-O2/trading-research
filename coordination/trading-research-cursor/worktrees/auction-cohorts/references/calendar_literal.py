"""Small literal clock/intersection reference; no production graph imports."""

from datetime import datetime, timezone
from zoneinfo import ZoneInfo


def wall_contains(rule, at):
    epoch = datetime(1970, 1, 1, tzinfo=timezone.utc)
    endpoints = []
    for side in ('start', 'end'):
        local = datetime.fromisoformat(rule[side + '_day'] + 'T' + rule[side + '_wall'])
        aware = local.replace(tzinfo=ZoneInfo(rule['zone']), fold=rule.get(side + '_fold') or 0)
        delta = aware.astimezone(timezone.utc) - epoch
        endpoints.append((delta.days * 86400 + delta.seconds) * 1_000_000_000 + delta.microseconds * 1000)
    return endpoints[0] <= at < endpoints[1]


def intersection(left, right):
    pairs = []
    for a, b in left:
        for c, d in right:
            if max(a, c) < min(b, d):
                pairs.append((max(a, c), min(b, d)))
    merged = []
    for start, end in sorted(pairs):
        if merged and start <= merged[-1][1]:
            merged[-1] = (merged[-1][0], max(merged[-1][1], end))
        else:
            merged.append((start, end))
    return tuple(merged)
