# Architecture

## Pipeline

```text
ccxt OHLCV
  -> raw parquet cache
  -> normalized OHLCV
  -> feature frame
  -> unsupervised regime detector
  -> deterministic regime label mapping
  -> strategy router
  -> pandas backtest
  -> metrics and report artifacts
```

## Boundaries

- `data`: fetch and normalize OHLCV only.
- `features`: transform normalized OHLCV into model-ready features.
- `regimes`: fit/predict clusters and map them to human-readable regimes.
- `strategies`: generate target exposure or signal candidates.
- `router`: choose the strategy behavior for each regime.
- `backtest`: apply shifted signals, fees, slippage, and metrics.

## MVP Constraints

- Single-symbol crypto OHLCV.
- No order book, spread, funding, or live execution.
- Low liquidity is approximated from OHLCV volume only.
- Backtest is educational and intentionally simple.

