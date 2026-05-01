"""Trend-following strategy placeholder."""

from __future__ import annotations

from market_regime_router.strategies.base import Signal, StrategyContext


class TrendStrategy:
    """Momentum or moving-average following strategy skeleton."""

    name = "trend"

    def generate_signal(self, context: StrategyContext) -> Signal:
        """Generate a trend-following signal."""

        raise NotImplementedError("Trend strategy is a milestone 4 task.")
