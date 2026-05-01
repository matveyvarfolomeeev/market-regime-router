"""OHLCV ingestion contracts.

The MVP data source is public `ccxt` OHLCV with parquet caching.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import pandas as pd

    from market_regime_router.config import DataConfig


def fetch_ohlcv(config: DataConfig) -> pd.DataFrame:
    """Fetch OHLCV bars from the configured exchange.

    TODO: Use `ccxt`, UTC timestamps, and cache raw parquet data.
    """

    raise NotImplementedError("OHLCV ingestion is a milestone 1 task.")
