"""Risk-off and no-trade strategy."""

from __future__ import annotations

from market_regime_router.strategies.base import Signal, StrategyContext


class RiskOffStrategy:
    """Defensive strategy for the risk-off and high-vol-reversal regimes.

    The MVP is long-only, so the only safe response to a sustained sell-off or a
    volatility spike is to hold no exposure. The strategy therefore always
    returns a flat signal; a later version could add short or hedged behaviour.
    """

    name = "risk_off"

    def generate_signal(self, context: StrategyContext) -> Signal:
        """Generate a defensive (flat) signal."""
        return 0
