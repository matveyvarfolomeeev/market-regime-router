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
uv sync --dev
```

Useful commands once dependencies are installed:

```powershell
uv run pytest
uv run ruff check .
uv run mypy src
```

## Learning Workflow

The repository starts with interfaces, docs, and test placeholders. Implement one small milestone at a time:

1. Load and normalize OHLCV data.
2. Build feature columns.
3. Fit and map unsupervised regimes.
4. Route regimes to simple strategy signals.
5. Run the pandas backtest and generate reports.

After each milestone, review the diff before moving on.
