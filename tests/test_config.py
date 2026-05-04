"""Config loading tests for milestone 1."""

from pathlib import Path

from market_regime_router.config import (
    BacktestConfig,
    DataConfig,
    FeatureConfig,
    ProjectConfig,
    RegimeConfig,
    load_config,
)


def test_load_config_builds_typed_project_config() -> None:
    config = load_config("configs/default.yaml")

    assert isinstance(config, ProjectConfig)
    assert isinstance(config.data, DataConfig)
    assert isinstance(config.features, FeatureConfig)
    assert isinstance(config.regimes, RegimeConfig)
    assert isinstance(config.backtest, BacktestConfig)


def test_load_config_converts_file_paths_to_path_objects() -> None:
    config = load_config("configs/default.yaml")

    assert config.data.raw_path == Path("data/raw/btc_usdt_1h.parquet")
    assert config.data.processed_path == Path("data/processed/btc_usdt_1h.parquet")


def test_load_config_preserves_default_mvp_values() -> None:
    config = load_config("configs/default.yaml")

    assert config.data.exchange == "binance"
    assert config.data.symbol == "BTC/USDT"
    assert config.data.timeframe == "1h"
    assert config.regimes.n_clusters == 4
    assert config.regimes.random_state == 42
