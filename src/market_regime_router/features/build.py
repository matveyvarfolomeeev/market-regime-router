"""Feature engineering contracts for regime detection."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import pandas as pd

    from market_regime_router.config import FeatureConfig


FEATURE_COLUMNS = (
    "return_1",
    "rolling_volatility",
    "trend_strength",
    "mean_reversion_distance",
    "liquidity_proxy",
)


def build_features(ohlcv: pd.DataFrame, config: FeatureConfig) -> pd.DataFrame:
    """Build model-ready feature columns from normalized OHLCV.

    TODO: Keep the transform causal so each row only uses current and past bars.
    """

    raise NotImplementedError("Feature engineering is a milestone 2 task.")
