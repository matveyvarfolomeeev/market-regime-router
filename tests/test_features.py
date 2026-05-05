"""Feature engineering tests."""

import numpy as np
import pandas as pd

from market_regime_router.config import FeatureConfig
from market_regime_router.features.build import FEATURE_COLUMNS, build_features


def _feature_config() -> FeatureConfig:
    return FeatureConfig(
        volatility_window=3,
        trend_window=3,
        mean_reversion_window=3,
        liquidity_window=3,
    )


def _ohlcv_frame() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "timestamp": pd.date_range("2026-01-01", periods=6, freq="h", tz="UTC"),
            "open": [10, 11, 12, 13, 14, 15],
            "high": [11, 12, 13, 14, 15, 16],
            "low": [9, 10, 11, 12, 13, 14],
            "close": [10.0, 11.0, 12.0, 13.0, 14.0, 15.0],
            "volume": [100.0, 120.0, 90.0, 150.0, 160.0, 180.0],
        }
    )


def test_feature_contract_names_are_declared() -> None:
    expected = {
        "return_1_log",
        "rolling_volatility",
        "trend_strength",
        "mean_reversion_distance",
        "liquidity_proxy",
    }
    assert set(FEATURE_COLUMNS) == expected


def test_build_features_returns_only_feature_columns_in_order() -> None:
    features = build_features(_ohlcv_frame(), _feature_config())

    assert list(features.columns) == list(FEATURE_COLUMNS)
    assert "sma" not in features.columns
    assert "std" not in features.columns


def test_build_features_calculates_expected_baseline_values() -> None:
    ohlcv = _ohlcv_frame()
    features = build_features(ohlcv, _feature_config())

    expected_return = np.log(ohlcv["close"] / ohlcv["close"].shift(1))
    expected_vol = expected_return.rolling(3).std()
    net_movement = (ohlcv["close"] - ohlcv["close"].shift(3)).abs()
    total_movement = ohlcv["close"].diff().abs().rolling(3).sum()
    expected_trend = net_movement / total_movement
    rolling_mean = ohlcv["close"].rolling(3).mean()
    rolling_std = ohlcv["close"].rolling(3).std()
    expected_mr = (ohlcv["close"] - rolling_mean) / rolling_std
    expected_liquidity = ohlcv["volume"] / ohlcv["volume"].rolling(3).mean()

    np.testing.assert_allclose(features["return_1_log"], expected_return, equal_nan=True)
    np.testing.assert_allclose(features["rolling_volatility"], expected_vol, equal_nan=True)
    np.testing.assert_allclose(features["trend_strength"], expected_trend, equal_nan=True)
    np.testing.assert_allclose(features["mean_reversion_distance"], expected_mr, equal_nan=True)
    np.testing.assert_allclose(features["liquidity_proxy"], expected_liquidity, equal_nan=True)


def test_features_are_causal_without_lookahead() -> None:
    base = _ohlcv_frame()
    changed_future = base.copy()
    changed_future.loc[5, "close"] = 1000.0
    changed_future.loc[5, "volume"] = 9999.0

    base_features = build_features(base, _feature_config())
    changed_features = build_features(changed_future, _feature_config())

    pd.testing.assert_frame_equal(
        base_features.iloc[:5],
        changed_features.iloc[:5],
    )


def test_features_handle_initial_rolling_nans() -> None:
    features = build_features(_ohlcv_frame(), _feature_config())

    assert features["return_1_log"].isna().tolist()[:2] == [True, False]
    assert features["rolling_volatility"].isna().tolist()[:3] == [True, True, True]
    assert features["trend_strength"].isna().tolist()[:4] == [True, True, True, False]
    assert features["mean_reversion_distance"].isna().tolist()[:2] == [True, True]
    assert features["liquidity_proxy"].isna().tolist()[:2] == [True, True]
