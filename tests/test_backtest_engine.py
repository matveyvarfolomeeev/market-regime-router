"""Backtest engine tests."""

import numpy as np
import pandas as pd
import pytest

from market_regime_router.backtest.engine import run_backtest
from market_regime_router.backtest.metrics import METRIC_NAMES, calculate_metrics
from market_regime_router.config import BacktestConfig


def _config(fee_bps: float = 0.0, slippage_bps: float = 0.0) -> BacktestConfig:
    return BacktestConfig(
        initial_cash=10_000.0,
        fee_bps=fee_bps,
        slippage_bps=slippage_bps,
        annualization_bars=8760,
    )


def _frame(close: list[float], position: list[float]) -> pd.DataFrame:
    index = pd.date_range("2026-01-01", periods=len(close), freq="h", tz="UTC")
    return pd.DataFrame({"close": close, "position": position}, index=index)


def test_metric_contract_names_are_declared() -> None:
    assert set(METRIC_NAMES) == {
        "total_return",
        "cagr",
        "max_drawdown",
        "sharpe_like",
        "turnover",
        "trade_count",
    }


def test_backtest_applies_signal_on_next_bar() -> None:
    # Position is only set on bar 1; with the one-bar shift it should earn the
    # return of bar 2, leaving bar 1's own return untouched.
    frame = _frame(close=[100.0, 100.0, 110.0, 110.0], position=[0.0, 1.0, 0.0, 0.0])

    result = run_backtest(frame, _config())
    net_return = result.equity_curve["net_return"]

    assert net_return.iloc[1] == 0.0
    assert net_return.iloc[2] == pytest.approx(0.10)


def test_backtest_applies_fees_and_slippage_to_turnover() -> None:
    # Flat market (no price moves) so only trading costs can change equity. The
    # round trip enters on bar 1 and exits on bar 2 so both rebalances land
    # inside the window (a position change on the last bar never applies).
    frame = _frame(
        close=[100.0, 100.0, 100.0, 100.0, 100.0],
        position=[0.0, 1.0, 0.0, 0.0, 0.0],
    )
    config = _config(fee_bps=5.0, slippage_bps=2.0)

    result = run_backtest(frame, config)

    cost_rate = (config.fee_bps + config.slippage_bps) / 10_000.0
    # Two rebalances of size 1.0: into the position and back out of it.
    expected_total_return = (1.0 - cost_rate) ** 2 - 1.0
    assert result.metrics["turnover"] == pytest.approx(2.0)
    assert result.metrics["trade_count"] == 2
    assert result.metrics["total_return"] == pytest.approx(expected_total_return)
    assert result.metrics["total_return"] < 0


def test_backtest_rejects_missing_columns_and_empty_frame() -> None:
    with pytest.raises(ValueError, match="missing columns"):
        run_backtest(_frame([1.0, 2.0], [0.0, 1.0]).drop(columns=["position"]), _config())

    empty = pd.DataFrame({"close": [], "position": []})
    with pytest.raises(ValueError, match="empty"):
        run_backtest(empty, _config())


def test_backtest_treats_nan_positions_as_flat() -> None:
    # Warmup rows arrive with NaN positions and must not crash or trade.
    frame = _frame(close=[100.0, 105.0, 110.0], position=[float("nan"), float("nan"), 1.0])

    result = run_backtest(frame, _config())

    assert np.isfinite(result.equity_curve["equity"]).all()
    assert result.metrics["trade_count"] == 0


def test_metrics_track_drawdown_on_a_losing_curve() -> None:
    equity_curve = pd.DataFrame(
        {
            "equity": [100.0, 120.0, 90.0, 108.0],
            "net_return": [0.0, 0.2, -0.25, 0.2],
            "turnover": [0.0, 1.0, 0.0, 0.0],
        }
    )

    metrics = calculate_metrics(equity_curve, annualization_bars=8760)

    assert metrics["total_return"] == pytest.approx(0.08)
    assert metrics["max_drawdown"] == pytest.approx(-0.25)
    assert metrics["trade_count"] == 1
