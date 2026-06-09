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

The end-to-end MVP pipeline is complete: OHLCV ingestion, feature engineering,
unsupervised regimes, deterministic regime mapping, strategy routing, a pandas
backtest, and a CLI that writes a report.

- `load_config()` reads `configs/default.yaml`, converts data paths to `Path`, and validates the
  configured regime names.
- `normalize_ohlcv()` validates the canonical OHLCV schema, converts timestamps to UTC, sorts rows,
  removes duplicate timestamps, coerces numeric columns, and returns only canonical OHLCV columns.
- `fetch_ohlcv()` wraps `ccxt` and pages on the bar timestamp for histories larger than one request.
- `build_features()` produces the research feature contract: multi-horizon log returns
  (`return_1/24/48/168_log`), `rolling_volatility`, `volatility_ratio`, `trend_strength`,
  `mean_reversion_distance`, `abs_mean_reversion_distance`, `range_pct`, and `log_liquidity_proxy`.
- `RegimeDetector` fits `StandardScaler + KMeans` and returns timestamped cluster predictions.
- `map_clusters_to_regimes()` assigns stable names (`quiet_range`, `trend_continuation`,
  `risk_off`, `high_vol_reversal`) independently of the arbitrary KMeans cluster ids.
- `StrategyRouter` routes each regime to a strategy: mean-reversion for quiet ranges, momentum for
  trend continuation, and a defensive flat strategy for risk-off and high-vol-reversal.
- `run_backtest()` runs a one-bar-shifted pandas backtest with fees/slippage on turnover and reports
  total return, CAGR, max drawdown, a Sharpe-like ratio, turnover, and trade count.
- `mrr run` wires it all together and writes a markdown report plus an equity-curve plot.

Current quality gate:

```powershell
.\.venv\Scripts\python.exe -m pytest
.\.venv\Scripts\ruff.exe check .
.\.venv\Scripts\ruff.exe format --check .
.\.venv\Scripts\mypy.exe src
```

Latest local run: `43 passed`; `ruff check`, `ruff format --check`, and `mypy src` pass.

## Usage

```powershell
# Fetch OHLCV into the raw cache (needs network)
.\.venv\Scripts\python.exe -m market_regime_router.cli ingest

# Run the full pipeline and write reports/backtest/report.md (+ equity_curve.png)
.\.venv\Scripts\python.exe -m market_regime_router.cli run

# Run offline from a saved OHLCV csv/parquet instead of fetching
.\.venv\Scripts\python.exe -m market_regime_router.cli run --input data/raw/btc_usdt_1h.parquet
```

## Regimes

The regimes and the deterministic mapping rule come from the research notes in
`reports/market_cluster_sandbox/cluster_hypotheses.md`:

- `quiet_range`: low activity; routed to mean-reversion.
- `trend_continuation`: sustained move up; routed to long-only momentum.
- `risk_off`: sustained move down; routed to a flat/defensive strategy.
- `high_vol_reversal`: volatility spike; also handled defensively.

Low liquidity is treated as a risk filter (position sizing), not a regime.

## Learning Workflow

The repository started with interfaces, docs, and test placeholders, then implemented one small
milestone at a time:

1. Load and normalize OHLCV data. Done.
2. Build feature columns. Done.
3. Fit unsupervised regimes. Done.
4. Map arbitrary cluster ids to stable regime names. Done.
5. Route regimes to simple strategy signals. Done.
6. Run the pandas backtest and generate reports. Done.

After each milestone, review the diff before moving on.
