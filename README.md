# Market Regime Router MVP

Educational crypto OHLCV research project for market regime detection and strategy routing.

The first version is intentionally narrow:

- market: crypto OHLCV
- default pair/timeframe: `BTC/USDT`, `1h`
- data source: `ccxt` public OHLCV
- regime model: unsupervised clustering baseline
- execution: offline pandas backtest

This project is not trading advice and is not a live trading system.

## Local Setup

`uv` was installed into the user Python scripts directory during setup. If `uv` is not in PATH,
run it by full path or add this directory to PATH:

```powershell
C:\Users\matva\AppData\Roaming\Python\Python312\Scripts\uv.exe --version
```

Then use:

```powershell
C:\Users\matva\AppData\Roaming\Python\Python312\Scripts\uv.exe sync --dev
```

Useful commands once dependencies are installed:

```powershell
.\.venv\Scripts\python.exe -m pytest
.\.venv\Scripts\ruff.exe check .
.\.venv\Scripts\ruff.exe format --check .
.\.venv\Scripts\mypy.exe src
```

## Current State

Milestone 1 is in review:

- `load_config()` is implemented for `configs/default.yaml`.
- `normalize_ohlcv()` is implemented for schema validation, UTC timestamps, duplicate handling,
  sorting, numeric conversion, and canonical OHLCV column order.
- `fetch_ohlcv()` has an initial `ccxt` implementation and a no-network unit test using a fake
  exchange.
- Tests were added for config loading, OHLCV normalization, and ingestion behavior.

Before moving to feature engineering, the quality gate should be green:

```powershell
.\.venv\Scripts\python.exe -m pytest
.\.venv\Scripts\ruff.exe check .
.\.venv\Scripts\ruff.exe format --check .
.\.venv\Scripts\mypy.exe src
```

The next milestone starts only after the source cleanup is committed.

## Learning Workflow

The repository starts with interfaces, docs, and test placeholders. Implement one small milestone at a time:

1. Load and normalize OHLCV data. In review.
2. Build feature columns. Next.
3. Fit and map unsupervised regimes.
4. Route regimes to simple strategy signals.
5. Run the pandas backtest and generate reports.

After each milestone, review the diff before moving on.

## Next Milestone

Milestone 2 is `build_features()` in `src/market_regime_router/features/build.py`.

Required baseline features:

- `return_1`: one-bar close return.
- `rolling_volatility`: rolling standard deviation of `return_1`.
- `trend_strength`: close relative to a rolling close mean.
- `mean_reversion_distance`: rolling z-score of close.
- `liquidity_proxy`: rolling volume measure.

All features must be causal: each row can use only current and past candles, never future candles.
