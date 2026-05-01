"""OHLCV normalization contracts."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import pandas as pd


OHLCV_COLUMNS = ("timestamp", "open", "high", "low", "close", "volume")


def normalize_ohlcv(raw: pd.DataFrame) -> pd.DataFrame:
    """Normalize raw OHLCV bars.

    TODO: Enforce UTC timestamps, column order, sorting, and duplicate removal.
    """

    raise NotImplementedError("OHLCV normalization is a milestone 1 task.")
