"""OHLCV ingestion contracts.

The MVP data source is public `ccxt` OHLCV with parquet caching.
"""

from __future__ import annotations

import ccxt  # type: ignore[import-untyped]
import pandas as pd

from market_regime_router.config import DataConfig


def fetch_ohlcv(config: DataConfig) -> pd.DataFrame:
    """Fetch OHLCV bars from the configured exchange."""
    exchange_class = getattr(ccxt, config.exchange)

    exchange = exchange_class(
        {
            "enableRateLimit": True,
        }
    )

    raw_bars = exchange.fetch_ohlcv(
        symbol=config.symbol,
        timeframe=config.timeframe,
        since=config.since,
        limit=config.limit,
    )

    raw_data = pd.DataFrame(
        raw_bars, columns=["timestamp", "open", "high", "low", "close", "volume"]
    )

    return raw_data
