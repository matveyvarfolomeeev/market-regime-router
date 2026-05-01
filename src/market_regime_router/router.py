"""Strategy router contracts."""

from __future__ import annotations

from dataclasses import dataclass

from market_regime_router.regimes.label_mapping import RegimeName
from market_regime_router.strategies.base import Strategy


@dataclass(frozen=True)
class StrategyRouter:
    """Route a regime name to the strategy responsible for that regime."""

    trend_strategy: Strategy
    mean_reversion_strategy: Strategy
    high_vol_strategy: Strategy
    low_liquidity_strategy: Strategy

    def select(self, regime: RegimeName) -> Strategy:
        """Select a strategy for a regime.

        TODO: Route trend, mean-reversion, high-vol, and low-liquidity regimes.
        """

        raise NotImplementedError("Strategy routing is a milestone 4 task.")
