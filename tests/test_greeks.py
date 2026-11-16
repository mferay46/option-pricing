import pytest

from option_pricing.greeks import black_scholes_greeks, finite_difference_greeks


@pytest.mark.parametrize("option_type", ["call", "put"])
def test_closed_form_greeks_match_finite_differences(option_type):
    exact = black_scholes_greeks(100, 100, 1, 0.05, 0.20, option_type)
    finite = finite_difference_greeks(100, 100, 1, 0.05, 0.20, option_type)
    assert finite.delta == pytest.approx(exact.delta, abs=1e-4)
    assert finite.gamma == pytest.approx(exact.gamma, abs=1e-4)
    assert finite.vega == pytest.approx(exact.vega, abs=1e-4)


def test_call_put_greek_relationships():
    call = black_scholes_greeks(100, 105, 0.75, 0.03, 0.25, "call")
    put = black_scholes_greeks(100, 105, 0.75, 0.03, 0.25, "put")
    assert call.delta - put.delta == pytest.approx(1.0)
    assert call.gamma == pytest.approx(put.gamma)
    assert call.vega == pytest.approx(put.vega)
