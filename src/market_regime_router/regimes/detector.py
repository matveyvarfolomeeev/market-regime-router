"""Unsupervised regime detector contracts."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import pandas as pd

    from market_regime_router.config import RegimeConfig


@dataclass
class RegimeDetector:
    """StandardScaler + KMeans detector placeholder."""

    config: RegimeConfig

    def fit(self, features: pd.DataFrame) -> RegimeDetector:
        """Fit the unsupervised model.

        TODO: Use `StandardScaler` and `KMeans` with deterministic random_state.
        """

        raise NotImplementedError("Regime fitting is a milestone 3 task.")

    def predict(self, features: pd.DataFrame) -> pd.Series:
        """Predict cluster ids for feature rows."""

        raise NotImplementedError("Regime prediction is a milestone 3 task.")
