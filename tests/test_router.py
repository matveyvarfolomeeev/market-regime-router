"""Strategy router tests."""

import pytest

from market_regime_router.router import StrategyRouter
from market_regime_router.strategies.mean_reversion import MeanReversionStrategy
from market_regime_router.strategies.risk_off import RiskOffStrategy
from market_regime_router.strategies.trend import TrendStrategy


def _router() -> StrategyRouter:
    # risk_off and high_vol_reversal intentionally share one defensive strategy.
    defensive = RiskOffStrategy()
    return StrategyRouter(
        quiet_range_strategy=MeanReversionStrategy(),
        trend_continuation_strategy=TrendStrategy(),
        risk_off_strategy=defensive,
        high_vol_reversal_strategy=defensive,
    )


def test_strategy_router_contract_is_importable() -> None:
    assert StrategyRouter.__name__ == "StrategyRouter"


def test_quiet_range_routes_to_mean_reversion() -> None:
    assert _router().select("quiet_range").name == "mean_reversion"


def test_trend_continuation_routes_to_trend() -> None:
    assert _router().select("trend_continuation").name == "trend"


def test_risk_off_routes_to_defensive_behavior() -> None:
    """Risk-off regime must reduce or close risk, not take new exposure."""
    assert _router().select("risk_off").name == "risk_off"


def test_high_vol_routes_to_defensive_behavior() -> None:
    """High-vol-reversal regime must be handled defensively, not as a trend."""
    assert _router().select("high_vol_reversal").name == "risk_off"


def test_unknown_regime_raises() -> None:
    with pytest.raises(ValueError, match="unknown regime"):
        _router().select("not_a_regime")  # type: ignore[arg-type]
