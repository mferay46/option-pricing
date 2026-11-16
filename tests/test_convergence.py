import pytest

from option_pricing.convergence import run_convergence_experiment


def test_rmse_decreases_and_slope_is_near_theory():
    result = run_convergence_experiment(
        sample_sizes=(500, 1_500, 5_000, 15_000),
        n_repetitions=30,
        seed=19,
    )
    assert all(a > b for a, b in zip(result.rmse, result.rmse[1:]))
    assert result.slope == pytest.approx(-0.5, abs=0.20)
