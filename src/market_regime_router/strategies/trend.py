"""Trend-following strategy."""

from __future__ import annotations

import pandas as pd

from market_regime_router.strategies.base import Signal, StrategyContext


class TrendStrategy:
    """Long-only momentum strategy for the trend-continuation regime.

    Goes long when the medium-term momentum is positive on both the 1d and 2d
    horizons, and stays flat otherwise. The MVP never shorts here: a fading
    up-trend should sit out rather than flip direction.
    """

    name = "trend"

    def generate_signal(self, context: StrategyContext) -> Signal:
        """Generate a trend-following signal."""
        return_24 = context.row.get("return_24_log")
        return_48 = context.row.get("return_48_log")

        if pd.isna(return_24) or pd.isna(return_48):
            return 0

        if return_24 > 0 and return_48 > 0:
            return 1
        return 0
