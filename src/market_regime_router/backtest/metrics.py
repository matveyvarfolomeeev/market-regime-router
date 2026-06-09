"""Backtest metric contracts."""

from __future__ import annotations

import numpy as np
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
    """Calculate the MVP performance metrics from a backtest equity curve.

    ``equity_curve`` is the frame produced by :func:`run_backtest` and must carry
    ``equity``, ``net_return`` and ``turnover`` columns. ``annualization_bars`` is
    the number of bars per year (8760 for 1h bars) used to annualize the return
    and the Sharpe-like ratio.
    """
    equity = equity_curve["equity"]
    net_return = equity_curve["net_return"]
    turnover = equity_curve["turnover"]

    n_bars = len(equity)
    start_equity = float(equity.iloc[0])
    end_equity = float(equity.iloc[-1])

    total_return = end_equity / start_equity - 1.0

    if n_bars > 0:
        cagr = (end_equity / start_equity) ** (annualization_bars / n_bars) - 1.0
    else:
        cagr = 0.0

    running_max = equity.cummax()
    drawdown = equity / running_max - 1.0
    max_drawdown = float(drawdown.min())

    return_std = float(net_return.std(ddof=0))
    if return_std > 0:
        sharpe_like = float(net_return.mean()) / return_std * np.sqrt(annualization_bars)
    else:
        sharpe_like = 0.0

    return {
        "total_return": float(total_return),
        "cagr": float(cagr),
        "max_drawdown": max_drawdown,
        "sharpe_like": float(sharpe_like),
        "turnover": float(turnover.sum()),
        "trade_count": float((turnover > 0).sum()),
    }
