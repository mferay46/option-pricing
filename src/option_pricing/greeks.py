"""Closed-form and finite-difference Greeks for Black–Scholes options."""

from dataclasses import dataclass
from math import erf, exp, isfinite, log, pi, sqrt
from typing import Literal

from .black_scholes import black_scholes_price

OptionType = Literal["call", "put"]


@dataclass(frozen=True)
class Greeks:
    """Option sensitivities; vega is per 1.00 change in volatility."""

    delta: float
    gamma: float
    vega: float


def _normal_cdf(value: float) -> float:
    return 0.5 * (1.0 + erf(value / sqrt(2.0)))


def _normal_pdf(value: float) -> float:
    return exp(-0.5 * value**2) / sqrt(2.0 * pi)


def _validate_greek_inputs(
    spot: float,
    strike: float,
    maturity: float,
    rate: float,
    volatility: float,
    option_type: OptionType,
) -> None:
    values = (spot, strike, maturity, rate, volatility)
    if not all(isfinite(value) for value in values):
        raise ValueError("All numeric inputs must be finite.")
    if spot <= 0 or strike <= 0:
        raise ValueError("spot and strike must be strictly positive.")
    if maturity <= 0 or volatility <= 0:
        raise ValueError("Greeks require positive maturity and volatility.")
    if option_type not in ("call", "put"):
        raise ValueError("option_type must be 'call' or 'put'.")


def black_scholes_greeks(
    spot: float,
    strike: float,
    maturity: float,
    rate: float,
    volatility: float,
    option_type: OptionType = "call",
) -> Greeks:
    """Return Black–Scholes delta, gamma, and vega (no dividends)."""
    _validate_greek_inputs(spot, strike, maturity, rate, volatility, option_type)
    sigma_sqrt_t = volatility * sqrt(maturity)
    d1 = (log(spot / strike) + (rate + 0.5 * volatility**2) * maturity) / sigma_sqrt_t

    delta = _normal_cdf(d1) if option_type == "call" else _normal_cdf(d1) - 1.0
    gamma = _normal_pdf(d1) / (spot * sigma_sqrt_t)
    vega = spot * _normal_pdf(d1) * sqrt(maturity)
    return Greeks(delta=delta, gamma=gamma, vega=vega)


def finite_difference_greeks(
    spot: float,
    strike: float,
    maturity: float,
    rate: float,
    volatility: float,
    option_type: OptionType = "call",
    spot_step: float | None = None,
    volatility_step: float = 1e-4,
) -> Greeks:
    """Approximate Greeks using central finite differences of the price.

    Delta and gamma use spot bumps; vega uses volatility bumps. The default
    spot bump is 1% of spot. Vega is reported per 1.00 change in volatility.
    """
    _validate_greek_inputs(spot, strike, maturity, rate, volatility, option_type)
    h_s = spot * 1e-2 if spot_step is None else spot_step
    h_v = volatility_step
    if not isfinite(h_s) or h_s <= 0 or h_s >= spot:
        raise ValueError("spot_step must be finite, positive, and smaller than spot.")
    if not isfinite(h_v) or h_v <= 0 or h_v >= volatility:
        raise ValueError("volatility_step must be finite, positive, and smaller than volatility.")

    def price(s: float = spot, vol: float = volatility) -> float:
        return black_scholes_price(s, strike, maturity, rate, vol, option_type)

    p0 = price()
    p_up = price(s=spot + h_s)
    p_down = price(s=spot - h_s)
    delta = (p_up - p_down) / (2.0 * h_s)
    gamma = (p_up - 2.0 * p0 + p_down) / h_s**2
    vega = (price(vol=volatility + h_v) - price(vol=volatility - h_v)) / (2.0 * h_v)
    return Greeks(delta=delta, gamma=gamma, vega=vega)
