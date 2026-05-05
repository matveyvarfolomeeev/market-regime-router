"""OHLCV normalization contracts."""

import pandas as pd

OHLCV_COLUMNS = ("timestamp", "open", "high", "low", "close", "volume")


def normalize_ohlcv(raw: pd.DataFrame) -> pd.DataFrame:
    """Normalize raw OHLCV bars."""
    data = raw.copy()

    missing_cols = [col for col in OHLCV_COLUMNS if col not in data.columns]
    if missing_cols:
        raise ValueError("missing OHLCV columns")

    data["timestamp"] = pd.to_datetime(data["timestamp"], unit="ms", utc=True)
    data = data.drop_duplicates(subset=["timestamp"], keep="last")

    data = data.sort_values(by=["timestamp"], ascending=True)

    for col in OHLCV_COLUMNS:
        if col != "timestamp":
            data[col] = pd.to_numeric(data[col], errors="coerce")

    return data[list(OHLCV_COLUMNS)]
