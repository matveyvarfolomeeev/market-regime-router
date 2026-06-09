"""Feature engineering contracts for regime detection."""

from __future__ import annotations

import numpy as np
import pandas as pd

from market_regime_router.config import FeatureConfig

# Fixed look-back horizons (in bars) for multi-horizon momentum features.
# These are deliberately constants, not config: they encode the economic idea of
# "1h / 1d / 2d / 1w" momentum on a 1h timeframe and should stay comparable
# across configs.
RETURN_HORIZONS = (1, 24, 48, 168)

FEATURE_COLUMNS = (
    "return_1_log",
    "return_24_log",
    "return_48_log",
    "return_168_log",
    "rolling_volatility",
    "volatility_ratio",
    "trend_strength",
    "mean_reversion_distance",
    "abs_mean_reversion_distance",
    "range_pct",
    "log_liquidity_proxy",
)


def build_features(ohlcv: pd.DataFrame, config: FeatureConfig) -> pd.DataFrame:
    """Build model-ready feature columns from normalized OHLCV.

    Every column is causal: each row only uses the current and past bars, so the
    feature frame can be reused for both research and backtesting without
    look-ahead. The research notes in ``reports/market_cluster_sandbox`` explain
    why these columns were selected.
    """
    df = ohlcv.copy()

    # Multi-horizon log returns. The 1h return drives short-term volatility while
    # the 24/48/168h returns separate sustained trends from mean-reverting noise.
    for horizon in RETURN_HORIZONS:
        df[f"return_{horizon}_log"] = np.log(df["close"] / df["close"].shift(horizon))

    # Volatility of 1h returns, plus how that volatility compares to its own
    # recent background. A high ratio flags volatility spikes (high_vol_reversal).
    df["rolling_volatility"] = df["return_1_log"].rolling(config.volatility_window).std()
    volatility_background = df["rolling_volatility"].rolling(config.trend_window).mean()
    df["volatility_ratio"] = df["rolling_volatility"] / volatility_background

    # Trend efficiency ratio: net move over the window divided by the path length.
    # Close to 1 means a clean directional move, close to 0 means choppy range.
    net_movement = (df["close"] - df["close"].shift(config.trend_window)).abs()
    total_movement = df["close"].diff().abs().rolling(config.trend_window).sum()
    df["trend_strength"] = net_movement / total_movement

    # Distance from the rolling mean in standard deviations (z-score). The signed
    # value separates breakouts (positive) from stress (negative); the absolute
    # value measures how stretched the market is in either direction.
    rolling_mean = df["close"].rolling(config.mean_reversion_window).mean()
    rolling_std = df["close"].rolling(config.mean_reversion_window).std()
    df["mean_reversion_distance"] = (df["close"] - rolling_mean) / rolling_std
    df["abs_mean_reversion_distance"] = df["mean_reversion_distance"].abs()

    # Per-bar high-low range as a fraction of close. Spikes mark impulsive or
    # stressed bars versus quiet range bars.
    df["range_pct"] = (df["high"] - df["low"]) / df["close"]

    # Log of volume relative to its rolling average. The log keeps volume outliers
    # from dominating KMeans; in the MVP this is the only liquidity proxy and is
    # used as a risk filter rather than as a regime of its own.
    liquidity_proxy = df["volume"] / df["volume"].rolling(config.liquidity_window).mean()
    df["log_liquidity_proxy"] = np.log(liquidity_proxy)

    return df[list(FEATURE_COLUMNS)]
