"""Backtest metric contracts."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import pandas as pd


METRIC_NAMES = (
    "total_return",
    "cagr",
    "max_drawdown",
    "sharpe_like",
    "turnover",
    "trade_count",
)


def calculate_metrics(equity_curve: pd.DataFrame, annualization_bars: int) -> dict[str, float]:
    """Calculate the MVP performance metrics."""

    raise NotImplementedError("Metric calculation is a milestone 5 task.")
