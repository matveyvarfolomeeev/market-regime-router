# Architecture

## Pipeline

```text
ccxt OHLCV
  -> raw OHLCV frame
  -> normalized OHLCV
  -> feature frame
  -> unsupervised regime detector
  -> deterministic regime label mapping
  -> strategy router
  -> pandas backtest
  -> metrics and report artifacts
```

## Boundaries

- `data`: fetch and normalize OHLCV only. Parquet caching is planned but not implemented yet.
- `features`: transform normalized OHLCV into model-ready features.
- `regimes`: fit/predict clusters and map them to human-readable regimes.
- `strategies`: generate target exposure or signal candidates.
- `router`: choose the strategy behavior for each regime.
- `backtest`: apply shifted signals, fees, slippage, and metrics.

## Implemented So Far

- Config loading from YAML into dataclass contracts.
- OHLCV normalization contract tests for UTC timestamps, duplicate handling, canonical schema,
  and input immutability.
- Initial `ccxt` ingestion wrapper tested with a fake exchange, without network calls.
- Causal feature engineering for log return, rolling volatility, trend strength, mean-reversion
  distance, and OHLCV volume liquidity proxy.
- `RegimeDetector` wrapper around `StandardScaler + KMeans` with deterministic config-driven
  random state and timestamp-preserving cluster predictions.

## Current Gap

`regimes/label_mapping.py` still needs the deterministic mapping from arbitrary KMeans cluster ids
to stable regime names. Until that exists, downstream strategy routing should not depend on raw
cluster numbers.

## MVP Constraints

- Single-symbol crypto OHLCV.
- No order book, spread, funding, or live execution.
- Low liquidity is approximated from OHLCV volume only.
- Backtest is educational and intentionally simple.
