"""Mean-reversion strategy."""

from __future__ import annotations

import pandas as pd

from market_regime_router.strategies.base import Signal, StrategyContext


class MeanReversionStrategy:
    """Z-score mean-reversion strategy for the quiet-range regime.

    Fades stretched prices: when the close is far below its rolling mean the
    strategy buys the dip, and when it is far above it sells the rip. Inside the
    ``entry_threshold`` band it stays flat so it does not trade noise.
    """

    name = "mean_reversion"

    def __init__(self, entry_threshold: float = 1.0) -> None:
        self.entry_threshold = entry_threshold

    def generate_signal(self, context: StrategyContext) -> Signal:
        """Generate a mean-reversion signal."""
        z_score = context.row.get("mean_reversion_distance")

        if pd.isna(z_score):
            return 0

        if z_score <= -self.entry_threshold:
            return 1
        if z_score >= self.entry_threshold:
            return -1
        return 0
