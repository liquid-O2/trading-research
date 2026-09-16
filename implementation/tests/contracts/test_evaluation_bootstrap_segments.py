"""The block bootstrap resamples within calendar-year segments (EVALUATION.md): block starts
are drawn inside each segment and a block wraps only within it, so a draw never mixes years.
Expected values come from the requirement, not from the function."""
import numpy as np

from trading_research.research.contracts.evaluation import moving_block_bootstrap


def test_a_draw_never_mixes_segments():
    # Year A is constant 1.0 for 30 days, year B constant 5.0 for 20 days: resampling within
    # segments keeps 30 days of A and 20 of B in every draw, so every draw mean is exactly 2.6.
    values = [1.0] * 30 + [5.0] * 20
    years = ["2022"] * 30 + ["2023"] * 20
    draws = moving_block_bootstrap(values, block=5, draws=500, seed=15022026, segments=years)
    assert draws.shape == (500,)
    assert np.allclose(draws, 2.6)
    # Without segments the whole series is one segment and draws mix the two years.
    mixed = moving_block_bootstrap(values, block=5, draws=500, seed=15022026)
    assert not np.allclose(mixed, 2.6) and mixed.min() < 2.6 < mixed.max()


def test_blocks_wrap_only_inside_their_segment():
    # A segment shorter than the block length still resamples only its own days.
    values = [1.0, 1.0, 1.0] + [9.0] * 10
    years = ["2022"] * 3 + ["2023"] * 10
    draws = moving_block_bootstrap(values, block=5, draws=200, seed=1, segments=years)
    assert np.allclose(draws, (3 * 1.0 + 10 * 9.0) / 13)


def test_same_seed_gives_identical_draws_and_block_one_is_iid_resampling():
    rng = np.random.default_rng(7)
    values = rng.normal(size=60).tolist()
    years = ["2022"] * 25 + ["2023"] * 35
    a = moving_block_bootstrap(values, block=5, draws=300, seed=15022026, segments=years)
    b = moving_block_bootstrap(values, block=5, draws=300, seed=15022026, segments=years)
    c = moving_block_bootstrap(values, block=5, draws=300, seed=1, segments=years)
    assert np.array_equal(a, b) and not np.array_equal(a, c)
    one = moving_block_bootstrap(values, block=1, draws=2000, seed=3, segments=years)
    assert abs(one.mean() - np.mean(values)) < 0.15      # iid resampling within segments centres on the mean


def test_empty_and_misaligned_inputs():
    assert moving_block_bootstrap([], draws=10).tolist() == [0.0] * 10
    import pytest
    with pytest.raises(ValueError, match="align"):
        moving_block_bootstrap([1.0, 2.0], segments=["2022"])
