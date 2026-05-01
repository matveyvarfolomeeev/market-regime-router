"""Pandas backtest engine contracts."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import pandas as pd

    from market_regime_router.config import BacktestConfig


@dataclass(frozen=True)
class BacktestResult:
    """Container returned by the backtest engine."""

    equity_curve: pd.DataFrame
    trades: pd.DataFrame
    metrics: dict[str, float]


def run_backtest(frame: pd.DataFrame, config: BacktestConfig) -> BacktestResult:
    """Run a simple vectorized pandas backtest.

    TODO: Shift signals by one bar and apply fees/slippage to turnover.
    """

    raise NotImplementedError("Backtest engine is a milestone 5 task.")
