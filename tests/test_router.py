"""Strategy router test plan."""

import pytest

from market_regime_router.router import StrategyRouter


def test_strategy_router_contract_is_importable() -> None:
    assert StrategyRouter.__name__ == "StrategyRouter"


@pytest.mark.skip(reason="Implement after StrategyRouter.select exists.")
def test_low_liquidity_routes_to_no_trade_behavior() -> None:
    """Future test: low-liquidity regime must not create active exposure."""


@pytest.mark.skip(reason="Implement after StrategyRouter.select exists.")
def test_high_vol_routes_to_defensive_behavior() -> None:
    """Future test: high-vol regime must reduce or close risk."""
