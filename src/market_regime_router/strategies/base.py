"""Common strategy interfaces."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Literal, Protocol

if TYPE_CHECKING:
    import pandas as pd


Signal = Literal[-1, 0, 1]


@dataclass(frozen=True)
class StrategyContext:
    """Input context available to a strategy at one timestamp."""

    timestamp: object
    regime: str
    row: pd.Series


class Strategy(Protocol):
    """Protocol for simple signal-generating strategies."""

    name: str

    def generate_signal(self, context: StrategyContext) -> Signal:
        """Return target directional signal for the next bar."""
