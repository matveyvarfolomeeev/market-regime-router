"""OHLCV ingestion contracts.

The MVP data source is public `ccxt` OHLCV with parquet caching.
"""

from __future__ import annotations

import ccxt  # type: ignore[import-untyped]
import pandas as pd

from market_regime_router.config import DataConfig

OHLCV_COLUMNS = ["timestamp", "open", "high", "low", "close", "volume"]
DEFAULT_BATCH_LIMIT = 1000


def fetch_ohlcv(config: DataConfig) -> pd.DataFrame:
    """Fetch OHLCV bars from the configured exchange."""
    exchange_class = getattr(ccxt, config.exchange)

    exchange = exchange_class(
        {
            "enableRateLimit": True,
        }
    )

    if config.limit is None or config.limit <= DEFAULT_BATCH_LIMIT:
        raw_bars = exchange.fetch_ohlcv(
            symbol=config.symbol,
            timeframe=config.timeframe,
            since=config.since,
            limit=config.limit,
        )
        return pd.DataFrame(raw_bars, columns=OHLCV_COLUMNS)

    timeframe_ms = int(exchange.parse_timeframe(config.timeframe) * 1000)
    since = _initial_since_ms(config.since, config.limit, timeframe_ms)
    raw_bars = []

    while len(raw_bars) < config.limit:
        batch_limit = min(DEFAULT_BATCH_LIMIT, config.limit - len(raw_bars))
        batch = exchange.fetch_ohlcv(
            symbol=config.symbol,
            timeframe=config.timeframe,
            since=since,
            limit=batch_limit,
        )

        if not batch:
            break

        raw_bars.extend(batch)
        since = int(batch[-1][0]) + timeframe_ms

        if len(batch) < batch_limit:
            break

    raw_data = pd.DataFrame(raw_bars[: config.limit], columns=OHLCV_COLUMNS)

    return raw_data


def _initial_since_ms(
    configured_since: str | None,
    limit: int,
    timeframe_ms: int,
) -> int:
    if configured_since is not None:
        if configured_since.isdigit():
            return int(configured_since)
        return int(pd.Timestamp(configured_since).timestamp() * 1000)

    now_ms = int(pd.Timestamp.now(tz="UTC").timestamp() * 1000)
    return now_ms - limit * timeframe_ms
