"""Black–Scholes pricing for European call and put options without dividends."""

from math import erf, exp, isfinite, log, sqrt
from typing import Literal


def _normal_cdf(value: float) -> float:
    """Cumulative distribution function of a standard normal variable."""
    return 0.5 * (1.0 + erf(value / sqrt(2.0)))

OptionType = Literal["call", "put"]


def black_scholes_price(
    spot: float,
    strike: float,
    maturity: float,
    rate: float,
    volatility: float,
    option_type: OptionType = "call",
) -> float:
    """Return the Black–Scholes price of a European option.

    Parameters are expressed in consistent units: ``maturity`` in years,
    ``rate`` as a continuously compounded annual rate, and ``volatility``
    as annualized volatility (e.g. 0.20 for 20%). Dividends are not modeled.
    At zero maturity the function returns the intrinsic value; at zero
    volatility it returns the discounted deterministic payoff.
    """
    values = (spot, strike, maturity, rate, volatility)
    if not all(isfinite(value) for value in values):
        raise ValueError("All numeric inputs must be finite.")
    if spot <= 0:
        raise ValueError("spot must be strictly positive.")
    if strike <= 0:
        raise ValueError("strike must be strictly positive.")
    if maturity < 0:
        raise ValueError("maturity must be non-negative.")
    if volatility < 0:
        raise ValueError("volatility must be non-negative.")
    if option_type not in ("call", "put"):
        raise ValueError("option_type must be 'call' or 'put'.")

    if maturity == 0:
        return max(spot - strike, 0.0) if option_type == "call" else max(strike - spot, 0.0)

    discounted_strike = strike * exp(-rate * maturity)
    if volatility == 0:
        if option_type == "call":
            return max(spot - discounted_strike, 0.0)
        return max(discounted_strike - spot, 0.0)

    sigma_sqrt_t = volatility * sqrt(maturity)
    d1 = (log(spot / strike) + (rate + 0.5 * volatility**2) * maturity) / sigma_sqrt_t
    d2 = d1 - sigma_sqrt_t

    if option_type == "call":
        return spot * _normal_cdf(d1) - discounted_strike * _normal_cdf(d2)
    return discounted_strike * _normal_cdf(-d2) - spot * _normal_cdf(-d1)
