"""Configuration contracts for the market regime router project."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class DataConfig:
    """Data loading settings for a single OHLCV universe."""

    exchange: str
    symbol: str
    timeframe: str
    raw_path: Path
    processed_path: Path
    since: str | None = None
    limit: int | None = None


@dataclass(frozen=True)
class FeatureConfig:
    """Rolling-window settings for feature engineering."""

    volatility_window: int
    trend_window: int
    mean_reversion_window: int
    liquidity_window: int


@dataclass(frozen=True)
class RegimeConfig:
    """Unsupervised regime model settings."""

    n_clusters: int
    random_state: int


@dataclass(frozen=True)
class BacktestConfig:
    """Backtest costs and capital settings."""

    initial_cash: float
    fee_bps: float
    slippage_bps: float
    annualization_bars: int


@dataclass(frozen=True)
class ProjectConfig:
    """Top-level config passed through the end-to-end pipeline."""

    data: DataConfig
    features: FeatureConfig
    regimes: RegimeConfig
    backtest: BacktestConfig


def load_config(path: str | Path) -> ProjectConfig:
    """Load a project config from YAML.

    TODO: Parse `configs/default.yaml` into the dataclasses above.
    """

    raise NotImplementedError("Config loading is a milestone 1 task.")
