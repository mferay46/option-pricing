"""Small parameter sweeps for European option prices."""

from collections.abc import Sequence

from .black_scholes import black_scholes_price


def price_sweep(
    parameter: str,
    values: Sequence[float],
    spot: float = 100.0,
    strike: float = 100.0,
    maturity: float = 1.0,
    rate: float = 0.05,
    volatility: float = 0.20,
    option_type: str = "call",
) -> list[float]:
    """Price an option over values of spot, volatility, or maturity."""
    if parameter not in {"spot", "volatility", "maturity"}:
        raise ValueError("parameter must be 'spot', 'volatility', or 'maturity'.")
    base = {
        "spot": spot,
        "strike": strike,
        "maturity": maturity,
        "rate": rate,
        "volatility": volatility,
        "option_type": option_type,
    }
    prices = []
    for value in values:
        params = base.copy()
        params[parameter] = float(value)
        prices.append(black_scholes_price(**params))
    return prices
