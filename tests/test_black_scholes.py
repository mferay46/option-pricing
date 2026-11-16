from math import exp

import pytest

from option_pricing.black_scholes import black_scholes_price


@pytest.mark.parametrize(
    ("option_type", "expected"),
    [("call", 10.450583572185565), ("put", 5.573526022256971)],
)
def test_reference_prices(option_type, expected):
    price = black_scholes_price(100, 100, 1, 0.05, 0.20, option_type)
    assert price == pytest.approx(expected, abs=1e-10)


def test_put_call_parity_without_dividends():
    spot, strike, maturity, rate, volatility = 100, 105, 0.75, 0.03, 0.25
    call = black_scholes_price(spot, strike, maturity, rate, volatility, "call")
    put = black_scholes_price(spot, strike, maturity, rate, volatility, "put")
    assert call - put == pytest.approx(spot - strike * exp(-rate * maturity))


def test_zero_maturity_returns_intrinsic_value():
    assert black_scholes_price(110, 100, 0, 0.05, 0.2, "call") == 10
    assert black_scholes_price(90, 100, 0, 0.05, 0.2, "put") == 10


def test_zero_volatility_returns_deterministic_discounted_payoff():
    price = black_scholes_price(100, 105, 1, 0.05, 0, "call")
    assert price == pytest.approx(max(100 - 105 * exp(-0.05), 0))


@pytest.mark.parametrize(
    "arguments",
    [
        (0, 100, 1, 0.05, 0.2, "call"),
        (100, -1, 1, 0.05, 0.2, "call"),
        (100, 100, -1, 0.05, 0.2, "call"),
        (100, 100, 1, 0.05, -0.2, "call"),
        (100, 100, 1, 0.05, 0.2, "straddle"),
    ],
)
def test_invalid_inputs_raise_value_error(arguments):
    with pytest.raises(ValueError):
        black_scholes_price(*arguments)
