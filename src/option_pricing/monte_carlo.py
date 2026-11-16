"""Monte Carlo pricing for European options under risk-neutral GBM."""

from dataclasses import dataclass
from math import exp, isfinite, log, sqrt
from statistics import NormalDist
from typing import Literal

import numpy as np

OptionType = Literal["call", "put"]


@dataclass(frozen=True)
class MonteCarloResult:
    """Price estimate and normal-approximation confidence interval."""

    price: float
    standard_error: float
    ci_lower: float
    ci_upper: float
    n_paths: int


def monte_carlo_price(
    spot: float,
    strike: float,
    maturity: float,
    rate: float,
    volatility: float,
    option_type: OptionType = "call",
    n_paths: int = 100_000,
    seed: int | None = None,
    confidence_level: float = 0.95,
) -> MonteCarloResult:
    """Estimate a European option price and its confidence interval.

    Simulates terminal prices under risk-neutral geometric Brownian motion.
    ``standard_error`` is computed from the discounted payoff samples, and
    the interval uses a normal approximation at ``confidence_level``.
    """
    inputs = (spot, strike, maturity, rate, volatility, confidence_level)
    if not all(isfinite(value) for value in inputs):
        raise ValueError("All numeric inputs must be finite.")
    if spot <= 0 or strike <= 0:
        raise ValueError("spot and strike must be strictly positive.")
    if maturity < 0 or volatility < 0:
        raise ValueError("maturity and volatility must be non-negative.")
    if option_type not in ("call", "put"):
        raise ValueError("option_type must be 'call' or 'put'.")
    if n_paths < 2:
        raise ValueError("n_paths must be at least 2.")
    if not 0 < confidence_level < 1:
        raise ValueError("confidence_level must be between 0 and 1.")

    rng = np.random.default_rng(seed)
    z = rng.standard_normal(n_paths)
    terminal_spot = spot * np.exp(
        (rate - 0.5 * volatility**2) * maturity
        + volatility * sqrt(maturity) * z
    )
    if option_type == "call":
        payoffs = np.maximum(terminal_spot - strike, 0.0)
    else:
        payoffs = np.maximum(strike - terminal_spot, 0.0)

    discounted_payoffs = exp(-rate * maturity) * payoffs
    price = float(np.mean(discounted_payoffs))
    standard_error = float(np.std(discounted_payoffs, ddof=1) / sqrt(n_paths))
    z_score = NormalDist().inv_cdf(0.5 + confidence_level / 2)
    margin = z_score * standard_error

    return MonteCarloResult(
        price=price,
        standard_error=standard_error,
        ci_lower=price - margin,
        ci_upper=price + margin,
        n_paths=n_paths,
    )
