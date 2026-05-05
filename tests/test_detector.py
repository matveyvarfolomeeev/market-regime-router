"""Regime detector tests."""

import pandas as pd
import pytest

from market_regime_router.config import RegimeConfig
from market_regime_router.regimes.detector import RegimeDetector


def _regime_config() -> RegimeConfig:
    return RegimeConfig(
        n_clusters=2,
        random_state=42,
        names=("trend", "mean_reversion"),
    )


def _feature_frame() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "return_1_log": [0.01, 0.02, 0.015, -0.03, -0.025, -0.035],
            "rolling_volatility": [0.10, 0.11, 0.09, 0.40, 0.42, 0.39],
            "trend_strength": [0.80, 0.75, 0.82, 0.20, 0.25, 0.18],
            "mean_reversion_distance": [1.2, 1.1, 1.3, -1.4, -1.2, -1.5],
            "liquidity_proxy": [1.1, 1.0, 1.2, 0.7, 0.8, 0.75],
        },
        index=pd.Index(
            pd.date_range("2026-01-01", periods=6, freq="h", tz="UTC"),
            name="timestamp",
        ),
    )


def test_fit_returns_self() -> None:
    detector = RegimeDetector(_regime_config())

    fitted = detector.fit(_feature_frame())

    assert fitted is detector


def test_predict_returns_series_with_input_index_and_cluster_name() -> None:
    features = _feature_frame()
    detector = RegimeDetector(_regime_config()).fit(features)

    predictions = detector.predict(features)

    assert isinstance(predictions, pd.Series)
    assert predictions.name == "cluster"
    pd.testing.assert_index_equal(predictions.index, features.index)
    assert set(predictions.unique()).issubset({0, 1})


def test_detector_is_deterministic_for_same_random_state() -> None:
    features = _feature_frame()
    first = RegimeDetector(_regime_config()).fit(features).predict(features)
    second = RegimeDetector(_regime_config()).fit(features).predict(features)

    pd.testing.assert_series_equal(first, second)


def test_fit_rejects_nan_features() -> None:
    features = _feature_frame()
    features.iloc[0, 0] = float("nan")

    with pytest.raises(ValueError, match="NaN"):
        RegimeDetector(_regime_config()).fit(features)


def test_predict_rejects_nan_features() -> None:
    train_features = _feature_frame()
    predict_features = train_features.copy()
    predict_features.iloc[0, 0] = float("nan")
    detector = RegimeDetector(_regime_config()).fit(train_features)

    with pytest.raises(ValueError, match="NaN"):
        detector.predict(predict_features)


def test_predict_before_fit_fails_clearly() -> None:
    detector = RegimeDetector(_regime_config())

    with pytest.raises(ValueError, match="fit"):
        detector.predict(_feature_frame())
