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

Milestones 1 and 2 are green, and the first half of milestone 3 is green:

- `load_config()` reads `configs/default.yaml`, converts data paths to `Path`, and validates the
  configured regime names.
- `normalize_ohlcv()` validates the canonical OHLCV schema, converts timestamps to UTC, sorts rows,
  removes duplicate timestamps, coerces numeric columns, and returns only canonical OHLCV columns.
- `fetch_ohlcv()` has an initial `ccxt` wrapper and a no-network unit test using a fake exchange.
- `build_features()` produces the current research feature contract:
  `return_1_log`, `rolling_volatility`, `trend_strength`, `mean_reversion_distance`,
  and `liquidity_proxy`.
- `RegimeDetector` fits `StandardScaler + KMeans` and returns cluster predictions as a timestamped
  `pd.Series` named `cluster`.

Current quality gate:

```powershell
.\.venv\Scripts\python.exe -m pytest
.\.venv\Scripts\ruff.exe check .
.\.venv\Scripts\ruff.exe format --check .
.\.venv\Scripts\mypy.exe src
```

Latest local run: `22 passed, 6 skipped`; `ruff check`, `ruff format --check`, and `mypy src` pass.

## Learning Workflow

The repository starts with interfaces, docs, and test placeholders. Implement one small milestone at a time:

1. Load and normalize OHLCV data. Done.
2. Build feature columns. Done.
3. Fit unsupervised regimes. Done.
4. Map arbitrary cluster ids to stable regime names. Next.
5. Route regimes to simple strategy signals.
6. Run the pandas backtest and generate reports.

After each milestone, review the diff before moving on.

## Next Milestone

Milestone 3b is `map_clusters_to_regimes()` in
`src/market_regime_router/regimes/label_mapping.py`.

Goal: make arbitrary KMeans cluster ids stable and human-readable.

The implementation should rank cluster-level feature statistics and assign exactly one label to
each cluster:

- `low_liquidity`: lowest average `liquidity_proxy`.
- `high_vol`: highest average `rolling_volatility` among the remaining clusters.
- `trend`: highest average `trend_strength` among the remaining clusters.
- `mean_reversion`: the remaining cluster.

The mapping must not depend on the numeric ids produced by KMeans.
