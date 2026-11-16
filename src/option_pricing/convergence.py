"""Repeated Monte Carlo experiments to study convergence with sample size."""

from dataclasses import dataclass
from math import isfinite, sqrt
from typing import Sequence

import numpy as np

from .black_scholes import black_scholes_price
from .monte_carlo import monte_carlo_price


@dataclass(frozen=True)
class ConvergenceResult:
    """RMSE of Monte Carlo estimates at each sample size and fitted slope."""

    sample_sizes: np.ndarray
    rmse: np.ndarray
    slope: float


def run_convergence_experiment(
    sample_sizes: Sequence[int] = (1_000, 3_000, 10_000, 30_000, 100_000),
    n_repetitions: int = 30,
    seed: int = 2026,
    spot: float = 100.0,
    strike: float = 100.0,
    maturity: float = 1.0,
    rate: float = 0.05,
    volatility: float = 0.20,
    option_type: str = "call",
) -> ConvergenceResult:
    """Estimate convergence rate using RMSE across independent runs.

    For each sample size, repeat the Monte Carlo pricing ``n_repetitions``
    times and compute root mean squared error against Black–Scholes. Fitting
    log(RMSE) against log(sample size) gives an empirical convergence slope.
    """
    sizes = np.asarray(sample_sizes, dtype=int)
    if sizes.ndim != 1 or len(sizes) < 2 or np.any(sizes < 2):
        raise ValueError("sample_sizes must contain at least two values >= 2.")
    if np.any(np.diff(sizes) <= 0):
        raise ValueError("sample_sizes must be strictly increasing.")
    if n_repetitions < 2:
        raise ValueError("n_repetitions must be at least 2.")
    if not isfinite(seed):
        raise ValueError("seed must be finite.")

    exact = black_scholes_price(
        spot, strike, maturity, rate, volatility, option_type
    )
    squared_errors = np.empty((len(sizes), n_repetitions), dtype=float)
    for size_index, n_paths in enumerate(sizes):
        for repetition in range(n_repetitions):
            run_seed = seed + size_index * n_repetitions + repetition
            estimate = monte_carlo_price(
                spot, strike, maturity, rate, volatility,
                option_type=option_type,
                n_paths=int(n_paths),
                seed=run_seed,
            )
            squared_errors[size_index, repetition] = (estimate.price - exact) ** 2

    rmse = np.sqrt(np.mean(squared_errors, axis=1))
    slope = float(np.polyfit(np.log(sizes), np.log(rmse), 1)[0])
    return ConvergenceResult(sample_sizes=sizes, rmse=rmse, slope=slope)
