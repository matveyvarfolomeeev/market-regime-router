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

The full MVP pipeline is implemented end to end:

- Config loading from YAML into dataclass contracts.
- OHLCV normalization with contract tests for UTC timestamps, duplicate handling, canonical schema,
  and input immutability.
- `ccxt` ingestion wrapper with timestamp-based pagination, tested against a fake exchange without
  network calls.
- Causal feature engineering: multi-horizon log returns, rolling volatility and volatility ratio,
  trend strength, signed and absolute mean-reversion distance, per-bar range, and a log liquidity
  proxy.
- `RegimeDetector` wrapper around `StandardScaler + KMeans` with a deterministic config-driven
  random state and timestamp-preserving cluster predictions.
- `map_clusters_to_regimes()`: deterministic, cluster-id-independent assignment of the research
  regimes by ranking z-scored cluster feature means.
- `StrategyRouter` plus three strategies (momentum, mean-reversion, defensive) behind a shared
  `Strategy` protocol.
- `run_backtest()`: one-bar-shifted vectorized pandas backtest with fees/slippage on turnover, an
  equity curve, a trade log, and MVP metrics.
- `pipeline.py` wires data -> features -> regimes -> mapping -> routing -> liquidity filter ->
  backtest, and `reporting.py` renders a markdown report and equity-curve plot driven by `cli.py`.

## Liquidity Filter

Low liquidity is a position-sizing filter applied after routing, not a regime. The pipeline scales
the routed signal by `log_liquidity_proxy`: full size at or above average volume, half size on thin
volume, and skipped entirely below roughly half the average volume.

## MVP Constraints

- Single-symbol crypto OHLCV.
- No order book, spread, funding, or live execution.
- Low liquidity is approximated from OHLCV volume only.
- Backtest is educational and intentionally simple.
