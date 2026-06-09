"""End-to-end pipeline and CLI tests on synthetic OHLCV (no network)."""

from pathlib import Path

import numpy as np
import pandas as pd

from market_regime_router import cli
from market_regime_router.backtest.metrics import METRIC_NAMES
from market_regime_router.config import load_config
from market_regime_router.pipeline import run_pipeline
from market_regime_router.regimes.label_mapping import REGIME_NAMES

CONFIG_PATH = Path("configs/default.yaml")


def _synthetic_raw_ohlcv(periods: int = 400) -> pd.DataFrame:
    """Build a synthetic raw OHLCV frame with ms timestamps and varied regimes."""
    rng = np.random.default_rng(7)
    # Mix calm drift, a strong up-trend, and a volatile sell-off so KMeans has
    # genuinely different states to separate.
    steps = np.concatenate(
        [
            rng.normal(0.0, 0.002, periods // 4),
            rng.normal(0.004, 0.003, periods // 4),
            rng.normal(-0.003, 0.010, periods // 4),
            rng.normal(0.0, 0.005, periods - 3 * (periods // 4)),
        ]
    )
    close = 100.0 * np.exp(np.cumsum(steps))
    high = close * (1.0 + np.abs(rng.normal(0.0, 0.004, periods)))
    low = close * (1.0 - np.abs(rng.normal(0.0, 0.004, periods)))
    volume = rng.uniform(50.0, 500.0, periods)
    start_ms = 1_700_000_000_000
    timestamp = start_ms + np.arange(periods) * 3_600_000

    return pd.DataFrame(
        {
            "timestamp": timestamp,
            "open": close,
            "high": high,
            "low": low,
            "close": close,
            "volume": volume,
        }
    )


def test_run_pipeline_produces_valid_backtest() -> None:
    config = load_config(CONFIG_PATH)

    result = run_pipeline(_synthetic_raw_ohlcv(), config)

    frame = result.signal_frame
    assert list(frame.columns) == ["close", "regime", "signal", "liquidity_scale", "position"]
    assert set(frame["regime"]).issubset(set(REGIME_NAMES))
    # Position stays within the long/short unit band after the liquidity filter.
    assert frame["position"].abs().max() <= 1.0
    assert set(result.backtest.metrics) == set(METRIC_NAMES)
    assert np.isfinite(result.backtest.equity_curve["equity"]).all()


def test_liquidity_filter_can_scale_down_positions() -> None:
    config = load_config(CONFIG_PATH)

    frame = run_pipeline(_synthetic_raw_ohlcv(), config).signal_frame
    active = frame[frame["signal"] != 0]

    # Some active signals should be taken at reduced or zero size on thin volume.
    assert (active["liquidity_scale"] < 1.0).any()


def test_cli_run_writes_report(tmp_path: Path) -> None:
    csv_path = tmp_path / "ohlcv.csv"
    _synthetic_raw_ohlcv().to_csv(csv_path, index=False)
    output_dir = tmp_path / "report"

    exit_code = cli.main(
        ["--config", str(CONFIG_PATH), "run", "--input", str(csv_path), "--output", str(output_dir)]
    )

    assert exit_code == 0
    assert (output_dir / "report.md").exists()
    assert (output_dir / "equity_curve.png").exists()
