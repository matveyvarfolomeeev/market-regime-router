"""Pandas backtest engine contracts."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

import pandas as pd

from market_regime_router.backtest.metrics import calculate_metrics

if TYPE_CHECKING:
    from market_regime_router.config import BacktestConfig

REQUIRED_COLUMNS = ("close", "position")


@dataclass(frozen=True)
class BacktestResult:
    """Container returned by the backtest engine."""

    equity_curve: pd.DataFrame
    trades: pd.DataFrame
    metrics: dict[str, float]


def run_backtest(frame: pd.DataFrame, config: BacktestConfig) -> BacktestResult:
    """Run a simple vectorized pandas backtest.

    ``frame`` must be indexed by timestamp and provide a ``close`` price and a
    target ``position`` (exposure in ``[-1, 1]``) decided at the close of each
    bar. The position is shifted by one bar before it earns a return, so a signal
    formed on bar ``t`` only affects the return of bar ``t + 1`` and there is no
    look-ahead. Fees and slippage are charged on the change in held exposure
    (turnover) whenever the portfolio rebalances.
    """
    missing = [column for column in REQUIRED_COLUMNS if column not in frame.columns]
    if missing:
        raise ValueError(f"backtest frame missing columns: {missing}")
    if frame.empty:
        raise ValueError("backtest frame is empty")

    data = frame.copy()
    returns = data["close"].pct_change().fillna(0.0)

    # Exposure held during each bar is the position decided on the previous bar.
    held = data["position"].fillna(0.0).shift(1).fillna(0.0)
    gross_return = held * returns

    # Turnover is the change in held exposure when the portfolio rebalances.
    turnover = held.diff()
    turnover.iloc[0] = held.iloc[0]
    turnover = turnover.abs()

    cost_rate = (config.fee_bps + config.slippage_bps) / 10_000.0
    cost = turnover * cost_rate
    net_return = gross_return - cost

    equity = config.initial_cash * (1.0 + net_return).cumprod()

    equity_curve = pd.DataFrame(
        {
            "return": returns,
            "position": held,
            "gross_return": gross_return,
            "turnover": turnover,
            "cost": cost,
            "net_return": net_return,
            "equity": equity,
        }
    )

    trade_mask = turnover > 0
    trades = pd.DataFrame(
        {
            "from_position": held.shift(1).fillna(0.0)[trade_mask],
            "to_position": held[trade_mask],
            "turnover": turnover[trade_mask],
            "cost": cost[trade_mask],
        }
    )

    metrics = calculate_metrics(equity_curve, config.annualization_bars)

    return BacktestResult(equity_curve=equity_curve, trades=trades, metrics=metrics)
