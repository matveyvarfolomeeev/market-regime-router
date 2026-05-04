"""OHLCV ingestion tests for milestone 1."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from market_regime_router.config import DataConfig
from market_regime_router.data import ingest


class FakeExchange:
    """Minimal exchange double that avoids network calls."""

    last_options: dict[str, object] | None = None
    last_request: dict[str, object] | None = None

    def __init__(self, options: dict[str, object]) -> None:
        type(self).last_options = options

    def fetch_ohlcv(
        self,
        symbol: str,
        timeframe: str,
        since: str | None,
        limit: int | None,
    ) -> list[list[float | int]]:
        type(self).last_request = {
            "symbol": symbol,
            "timeframe": timeframe,
            "since": since,
            "limit": limit,
        }
        return [[1_000, 10, 12, 9, 11, 100]]


def test_fetch_ohlcv_uses_configured_exchange_and_returns_raw_frame(monkeypatch) -> None:
    monkeypatch.setattr(ingest.ccxt, "fake_exchange", FakeExchange, raising=False)
    config = DataConfig(
        exchange="fake_exchange",
        symbol="BTC/USDT",
        timeframe="1h",
        raw_path=Path("data/raw/test.parquet"),
        processed_path=Path("data/processed/test.parquet"),
        since=None,
        limit=1,
    )

    raw = ingest.fetch_ohlcv(config)

    assert FakeExchange.last_options == {"enableRateLimit": True}
    assert FakeExchange.last_request == {
        "symbol": "BTC/USDT",
        "timeframe": "1h",
        "since": None,
        "limit": 1,
    }
    pd.testing.assert_frame_equal(
        raw,
        pd.DataFrame(
            [[1_000, 10, 12, 9, 11, 100]],
            columns=["timestamp", "open", "high", "low", "close", "volume"],
        ),
    )
