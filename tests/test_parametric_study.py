from option_pricing.parametric_study import price_sweep


def test_call_price_increases_with_volatility_and_maturity():
    by_volatility = price_sweep("volatility", [0.10, 0.20, 0.30])
    by_maturity = price_sweep("maturity", [0.25, 0.75, 1.50])
    assert by_volatility[0] < by_volatility[1] < by_volatility[2]
    assert by_maturity[0] < by_maturity[1] < by_maturity[2]
