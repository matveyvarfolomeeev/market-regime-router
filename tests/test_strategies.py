"""Strategy signal tests."""

import pandas as pd

from market_regime_router.strategies.base import StrategyContext
from market_regime_router.strategies.mean_reversion import MeanReversionStrategy
from market_regime_router.strategies.risk_off import RiskOffStrategy
from market_regime_router.strategies.trend import TrendStrategy


def _context(regime: str, **features: float) -> StrategyContext:
    row = pd.Series(features, dtype="float64")
    return StrategyContext(timestamp=pd.Timestamp("2026-01-01", tz="UTC"), regime=regime, row=row)


def test_trend_goes_long_when_momentum_is_positive() -> None:
    strategy = TrendStrategy()
    signal = strategy.generate_signal(
        _context("trend_continuation", return_24_log=0.02, return_48_log=0.03)
    )
    assert signal == 1


def test_trend_stays_flat_when_momentum_is_mixed_or_nan() -> None:
    strategy = TrendStrategy()
    mixed = strategy.generate_signal(
        _context("trend_continuation", return_24_log=0.02, return_48_log=-0.01)
    )
    nan = strategy.generate_signal(
        _context("trend_continuation", return_24_log=float("nan"), return_48_log=0.03)
    )
    assert mixed == 0
    assert nan == 0


def test_mean_reversion_buys_dips_and_sells_rips() -> None:
    strategy = MeanReversionStrategy(entry_threshold=1.0)
    long_signal = strategy.generate_signal(_context("quiet_range", mean_reversion_distance=-1.5))
    short_signal = strategy.generate_signal(_context("quiet_range", mean_reversion_distance=1.5))
    flat_signal = strategy.generate_signal(_context("quiet_range", mean_reversion_distance=0.2))
    assert long_signal == 1
    assert short_signal == -1
    assert flat_signal == 0


def test_risk_off_is_always_flat() -> None:
    strategy = RiskOffStrategy()
    assert strategy.generate_signal(_context("risk_off", return_24_log=-0.1)) == 0
    assert strategy.generate_signal(_context("high_vol_reversal", volatility_ratio=2.0)) == 0
