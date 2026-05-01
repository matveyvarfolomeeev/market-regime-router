"""Risk-off and no-trade strategy placeholders."""

from __future__ import annotations

from market_regime_router.strategies.base import Signal, StrategyContext


class RiskOffStrategy:
    """Strategy skeleton for high-volatility or low-liquidity regimes."""

    name = "risk_off"

    def generate_signal(self, context: StrategyContext) -> Signal:
        """Generate a defensive signal."""

        raise NotImplementedError("Risk-off behavior is a milestone 4 task.")
