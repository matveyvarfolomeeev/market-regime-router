"""OHLCV normalization tests for milestone 1."""

import pandas as pd
import pytest

from market_regime_router.data.normalize import OHLCV_COLUMNS, normalize_ohlcv


def test_normalize_sorts_deduplicates_and_keeps_last_duplicate() -> None:
    raw = pd.DataFrame(
        {
            "timestamp": [2_000, 1_000, 2_000],
            "open": ["20", "10", "21"],
            "high": ["22", "12", "23"],
            "low": ["19", "9", "20"],
            "close": ["21", "11", "22"],
            "volume": ["200", "100", "250"],
        }
    )

    normalized = normalize_ohlcv(raw)

    assert normalized["timestamp"].tolist() == [
        pd.Timestamp("1970-01-01 00:00:01", tz="UTC"),
        pd.Timestamp("1970-01-01 00:00:02", tz="UTC"),
    ]
    assert normalized["open"].tolist() == [10, 21]
    assert normalized["volume"].tolist() == [100, 250]


def test_normalize_returns_only_canonical_columns_in_order() -> None:
    raw = pd.DataFrame(
        {
            "volume": [100],
            "close": [11],
            "extra": ["ignore me"],
            "low": [9],
            "timestamp": [1_000],
            "high": [12],
            "open": [10],
        }
    )

    normalized = normalize_ohlcv(raw)

    assert list(normalized.columns) == list(OHLCV_COLUMNS)


def test_normalize_does_not_mutate_input_frame() -> None:
    raw = pd.DataFrame(
        {
            "timestamp": [1_000],
            "open": ["10"],
            "high": ["12"],
            "low": ["9"],
            "close": ["11"],
            "volume": ["100"],
        }
    )
    original = raw.copy(deep=True)

    normalize_ohlcv(raw)

    pd.testing.assert_frame_equal(raw, original)


def test_normalize_raises_clear_error_for_missing_columns() -> None:
    raw = pd.DataFrame({"timestamp": [1_000], "open": [10]})

    with pytest.raises(ValueError, match="missing OHLCV columns"):
        normalize_ohlcv(raw)
