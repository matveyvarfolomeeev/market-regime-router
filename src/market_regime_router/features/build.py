"""Feature engineering contracts for regime detection."""

from __future__ import annotations

import numpy as np
import pandas as pd

from market_regime_router.config import FeatureConfig

FEATURE_COLUMNS = (
    "return_1_log",
    "rolling_volatility",
    "trend_strength",
    "mean_reversion_distance",
    "liquidity_proxy",
)


def build_features(ohlcv: pd.DataFrame, config: FeatureConfig) -> pd.DataFrame:
    """Build model-ready feature columns from normalized OHLCV.

    TODO: Keep the transform causal so each row only uses current and past bars.
    """
    df = ohlcv.copy()
    df["return_1_log"] = np.log(df["close"] / df["close"].shift(1))

    df["rolling_volatility"] = df["return_1_log"].rolling(window=config.volatility_window).std()

    net_movement = abs(df["close"] - df["close"].shift(config.trend_window))
    total_movement = df["close"].diff().abs().rolling(config.trend_window).sum()
    df["trend_strength"] = net_movement / total_movement

    df["sma"] = df["close"].rolling(config.mean_reversion_window).mean()
    df["std"] = df["close"].rolling(config.mean_reversion_window).std()
    df["mean_reversion_distance"] = (df["close"] - df["sma"]) / df["std"]

    df["liquidity_proxy"] = df["volume"] / df["volume"].rolling(config.liquidity_window).mean()

    return df[list(FEATURE_COLUMNS)]
