import pytest

from option_pricing.black_scholes import black_scholes_price
from option_pricing.monte_carlo import monte_carlo_price


@pytest.mark.parametrize("option_type", ["call", "put"])
def test_large_simulation_agrees_with_black_scholes(option_type):
    args = (100, 100, 1, 0.05, 0.2)
    exact = black_scholes_price(*args, option_type)
    result = monte_carlo_price(*args, option_type, n_paths=500_000, seed=2026)
    assert result.ci_lower <= exact <= result.ci_upper
    assert abs(result.price - exact) <= 2 * result.standard_error


def test_same_seed_is_reproducible():
    first = monte_carlo_price(100, 100, 1, 0.05, 0.2, seed=7, n_paths=10_000)
    second = monte_carlo_price(100, 100, 1, 0.05, 0.2, seed=7, n_paths=10_000)
    assert first == second


def test_invalid_number_of_paths_raises():
    with pytest.raises(ValueError, match="at least 2"):
        monte_carlo_price(100, 100, 1, 0.05, 0.2, n_paths=1)
