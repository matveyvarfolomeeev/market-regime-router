"""Mean-reversion strategy placeholder."""

from __future__ import annotations

from market_regime_router.strategies.base import Signal, StrategyContext


class MeanReversionStrategy:
    """Z-score mean-reversion strategy skeleton."""

    name = "mean_reversion"

    def generate_signal(self, context: StrategyContext) -> Signal:
        """Generate a mean-reversion signal."""

        raise NotImplementedError("Mean-reversion strategy is a milestone 4 task.")
