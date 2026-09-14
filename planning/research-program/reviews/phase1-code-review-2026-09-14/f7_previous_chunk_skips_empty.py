"""F7: local_observations compares each effort window against the previous
NON-EMPTY chunk, not against its immediately preceding equal-duration window
(the registered A2-FLOW wording), so a quiet interval changes the comparison."""
import sys; sys.path.insert(0, '/tmp/claude-1001/-workspace/a537e734-3756-42f3-86a8-d5066915b22a/scratchpad/code-review-phase1')
from harness import *
from decimal import Decimal as D
from trading_research.research.method_pack.historical_flow import local_observations

TOUCH = clock(DAY, '10:00')
BAND = [D('99.75'), D('100.25')]


def run(fill_quiet_window):
    ev = [raw(START + i * MINUTE, 100) for i in range(5)]
    ev += [raw(TOUCH + 0 * SECOND, 100, 5, 'A'), raw(TOUCH + 1 * SECOND, 100, 5, 'A')]   # window at +0
    if fill_quiet_window:
        ev += [raw(TOUCH + 6 * SECOND, 150, 1, 'B')]        # a print far from the band at +5
    ev += [raw(TOUCH + 10 * SECOND, 100, 2, 'A'), raw(TOUCH + 11 * SECOND, 100, 2, 'A')]  # window at +10
    m = Market(ev)
    obs = local_observations(m, TOUCH, BAND, 'long', book=False)
    return [(int((c['start'] - TOUCH) / SECOND), c['opposing'], c['effort']) for c in obs['chunks']]


print('quiet +5s window absent :', run(False))
print('quiet +5s window present:', run(True))
print()
print('rows are (chunk start offset seconds, opposing volume, effort)')
print('EXPECTED: the +10s window is compared with the window that immediately precedes it')
print('OBSERVED: with the +5s window empty it is compared with the +0s window instead,')
print('          flipping effort (and therefore the defense stage) from True to False')
