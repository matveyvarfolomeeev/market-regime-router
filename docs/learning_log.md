# Learning Log

Use this file to record small decisions and lessons after each milestone.

## Milestone 0: Skeleton

- Repository created as a local research project.
- Code files contain interfaces and TODOs rather than completed trading logic.

## Milestone 1: Data Foundation

- Implemented `load_config()` for YAML-backed project settings.
- Added `regimes.names` to the Python config contract so YAML and dataclasses match.
- Implemented `normalize_ohlcv()` for timestamp conversion, duplicate handling, sorting, numeric
  coercion, and canonical OHLCV output columns.
- Added an initial `fetch_ohlcv()` wrapper around `ccxt`.
- Added unit tests for config loading, normalization behavior, and ingestion with a fake exchange.

## Milestone 2: Feature Engineering

- Kept the research feature contract based on `return_1_log` instead of switching back to simple
  percent return.
- Implemented causal rolling features:
  `rolling_volatility`, `trend_strength`, `mean_reversion_distance`, and `liquidity_proxy`.
- Added tests for feature column order, formula values, no-lookahead behavior, and initial rolling
  `NaN` handling.

## Milestone 3a: Regime Detector

- Implemented `RegimeDetector` as a small wrapper around `StandardScaler + KMeans`.
- `fit()` rejects feature frames with `NaN` values and returns `self`.
- `predict()` returns a `pd.Series` named `cluster` with the same index as the input feature frame.
- Added detector tests for fit contract, prediction shape, deterministic output, `NaN` rejection,
  and predict-before-fit failure.

## Current Quality Gate

- `pytest`: 22 passed, 6 skipped.
- `ruff check .`: passed.
- `ruff format --check .`: passed.
- `mypy src`: passed.

## Next Milestone: Stable Regime Mapping

- Implement `map_clusters_to_regimes()` in `src/market_regime_router/regimes/label_mapping.py`.
- Replace the skipped mapping test with real tests proving that permuted cluster ids produce the
  same human-readable regime assignment.
- Use simple deterministic ranking first: lowest liquidity, highest volatility, highest trend
  strength, then the remaining cluster as mean reversion.
