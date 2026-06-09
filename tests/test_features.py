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


def _ohlcv_frame(periods: int = 12) -> pd.DataFrame:
    close = np.linspace(10.0, 10.0 + periods - 1, periods)
    return pd.DataFrame(
        {
            "timestamp": pd.date_range("2026-01-01", periods=periods, freq="h", tz="UTC"),
            "open": close - 0.5,
            "high": close + 1.0,
            "low": close - 1.0,
            "close": close,
            "volume": np.linspace(100.0, 100.0 + 10.0 * (periods - 1), periods),
        }
    )


def test_feature_contract_names_are_declared() -> None:
    expected = {
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
    }
    assert set(FEATURE_COLUMNS) == expected


def test_build_features_returns_only_feature_columns_in_order() -> None:
    features = build_features(_ohlcv_frame(), _feature_config())

    assert list(features.columns) == list(FEATURE_COLUMNS)
    # Intermediate helper columns must not leak into the contract.
    assert "sma" not in features.columns
    assert "std" not in features.columns
    assert "volume" not in features.columns


def test_build_features_calculates_expected_baseline_values() -> None:
    ohlcv = _ohlcv_frame()
    config = _feature_config()
    features = build_features(ohlcv, config)

    close = ohlcv["close"]
    expected_return_1 = np.log(close / close.shift(1))
    expected_vol = expected_return_1.rolling(3).std()
    expected_vol_ratio = expected_vol / expected_vol.rolling(3).mean()
    net_movement = (close - close.shift(3)).abs()
    total_movement = close.diff().abs().rolling(3).sum()
    expected_trend = net_movement / total_movement
    rolling_mean = close.rolling(3).mean()
    rolling_std = close.rolling(3).std()
    expected_mr = (close - rolling_mean) / rolling_std
    expected_range = (ohlcv["high"] - ohlcv["low"]) / close
    expected_liquidity = np.log(ohlcv["volume"] / ohlcv["volume"].rolling(3).mean())

    np.testing.assert_allclose(features["return_1_log"], expected_return_1, equal_nan=True)
    np.testing.assert_allclose(
        features["return_24_log"], np.log(close / close.shift(24)), equal_nan=True
    )
    np.testing.assert_allclose(features["rolling_volatility"], expected_vol, equal_nan=True)
    np.testing.assert_allclose(features["volatility_ratio"], expected_vol_ratio, equal_nan=True)
    np.testing.assert_allclose(features["trend_strength"], expected_trend, equal_nan=True)
    np.testing.assert_allclose(features["mean_reversion_distance"], expected_mr, equal_nan=True)
    np.testing.assert_allclose(
        features["abs_mean_reversion_distance"], expected_mr.abs(), equal_nan=True
    )
    np.testing.assert_allclose(features["range_pct"], expected_range, equal_nan=True)
    np.testing.assert_allclose(features["log_liquidity_proxy"], expected_liquidity, equal_nan=True)


def test_features_are_causal_without_lookahead() -> None:
    base = _ohlcv_frame()
    changed_future = base.copy()
    last = len(base) - 1
    changed_future.loc[last, "close"] = 1000.0
    changed_future.loc[last, "high"] = 1001.0
    changed_future.loc[last, "volume"] = 9999.0

    base_features = build_features(base, _feature_config())
    changed_features = build_features(changed_future, _feature_config())

    # Changing only the final bar must not move any earlier feature row.
    pd.testing.assert_frame_equal(
        base_features.iloc[:last],
        changed_features.iloc[:last],
    )


def test_features_handle_initial_rolling_nans() -> None:
    features = build_features(_ohlcv_frame(), _feature_config())

    assert features["return_1_log"].isna().tolist()[:2] == [True, False]
    assert features["rolling_volatility"].isna().tolist()[:3] == [True, True, True]
    assert features["trend_strength"].isna().tolist()[:4] == [True, True, True, False]
    assert features["mean_reversion_distance"].isna().tolist()[:2] == [True, True]
    # range_pct uses only the current bar, so it is defined from the first row.
    assert features["range_pct"].isna().tolist()[:2] == [False, False]
