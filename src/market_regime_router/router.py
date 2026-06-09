"""Strategy router contracts."""

from __future__ import annotations

from dataclasses import dataclass

from market_regime_router.regimes.label_mapping import RegimeName
from market_regime_router.strategies.base import Strategy


@dataclass(frozen=True)
class StrategyRouter:
    """Route a regime name to the strategy responsible for that regime."""

    quiet_range_strategy: Strategy
    trend_continuation_strategy: Strategy
    risk_off_strategy: Strategy
    high_vol_reversal_strategy: Strategy

    def select(self, regime: RegimeName) -> Strategy:
        """Select the strategy that handles ``regime``.

        Quiet ranges mean-revert, trend continuations follow momentum, and both
        risk-off and high-vol-reversal regimes are handled defensively (no active
        long exposure in the MVP).
        """
        by_regime: dict[RegimeName, Strategy] = {
            "quiet_range": self.quiet_range_strategy,
            "trend_continuation": self.trend_continuation_strategy,
            "risk_off": self.risk_off_strategy,
            "high_vol_reversal": self.high_vol_reversal_strategy,
        }

        try:
            return by_regime[regime]
        except KeyError as error:
            raise ValueError(f"unknown regime: {regime!r}") from error
