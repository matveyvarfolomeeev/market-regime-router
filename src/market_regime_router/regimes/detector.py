"""Unsupervised regime detector contracts."""

from __future__ import annotations

from dataclasses import dataclass

import pandas as pd
from sklearn.cluster import KMeans  # type: ignore[import-untyped]
from sklearn.preprocessing import StandardScaler  # type: ignore[import-untyped]

from market_regime_router.config import RegimeConfig


@dataclass
class RegimeDetector:
    """StandardScaler + KMeans detector placeholder."""

    def __init__(self, config: RegimeConfig) -> None:
        self.config: RegimeConfig = config
        self.scaler: StandardScaler = StandardScaler()
        self.model: KMeans = KMeans(
            n_clusters=self.config.n_clusters,
            random_state=self.config.random_state,
        )

    def fit(self, features: pd.DataFrame) -> RegimeDetector:
        """Fit the unsupervised model."""
        df = features.copy()

        if df.isna().any().any():
            raise ValueError("Features contain NaN values.")

        df = self.scaler.fit_transform(df)
        self.model = self.model.fit(df)
        return self

    def predict(self, features: pd.DataFrame) -> pd.Series:
        """Predict cluster ids for feature rows."""

        df = features.copy()

        if df.isna().any().any():
            raise ValueError("Features contain NaN values.")

        df = self.scaler.transform(df)
        predict = self.model.predict(df)

        return pd.Series(
            predict,
            index=features.index,
            name="cluster",
        )
