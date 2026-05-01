"""Backtest engine test plan."""

import pytest

from market_regime_router.backtest.metrics import METRIC_NAMES


def test_metric_contract_names_are_declared() -> None:
    assert set(METRIC_NAMES) == {
        "total_return",
        "cagr",
        "max_drawdown",
        "sharpe_like",
        "turnover",
        "trade_count",
    }


@pytest.mark.skip(reason="Implement after run_backtest exists.")
def test_backtest_applies_signal_on_next_bar() -> None:
    """Future test: today's signal should affect tomorrow's return."""


@pytest.mark.skip(reason="Implement after run_backtest exists.")
def test_backtest_applies_fees_and_slippage_to_turnover() -> None:
    """Future test: changing position should reduce equity by configured costs."""


@pytest.mark.skip(reason="Implement after run_backtest exists.")
def test_backtest_handles_empty_or_nan_inputs() -> None:
    """Future test: invalid inputs should fail clearly or return empty-safe results."""
