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

## Milestone 1b: Paginated Ingestion

- `fetch_ohlcv()` now pages on the bar timestamp when the configured `limit` is
  larger than a single ccxt request, so the research can use long histories.
- Raised the default `limit` to 20000 bars of BTC/USDT 1h.
- Added a no-network paging test driven by a fake exchange.

## Milestone 2b: Expanded Feature Set

- Acted on the `reports/market_cluster_sandbox` research: the original four
  labels did not describe the real clusters, so the feature set was widened.
- Added multi-horizon momentum (`return_24_log`, `return_48_log`,
  `return_168_log`), `volatility_ratio`, `abs_mean_reversion_distance`,
  `range_pct`, and switched the liquidity proxy to `log_liquidity_proxy`.
- Kept every feature causal and updated the feature tests for the new contract.

## Milestone 3b: Deterministic Regime Mapping

- Replaced the placeholder regime names with the research labels:
  `quiet_range`, `trend_continuation`, `risk_off`, `high_vol_reversal`.
- Implemented `map_clusters_to_regimes()` by z-scoring cluster feature means and
  picking each regime by its defining trait, so KMeans cluster ids never matter.
- Learned the hard way that `risk_off` and `high_vol_reversal` both have negative
  returns: resolving `high_vol_reversal` first by its highest `volatility_ratio`
  removes the ambiguity. Added a permutation-invariance test that proves the
  mapping is independent of cluster id order.

## Current Quality Gate

- `pytest`: 26 passed, 5 skipped.
- `ruff check .`: passed.
- `ruff format --check .`: passed.
- `mypy src`: passed.

## Next Milestone: Stable Regime Mapping

- Implement `map_clusters_to_regimes()` in `src/market_regime_router/regimes/label_mapping.py`.
- Replace the skipped mapping test with real tests proving that permuted cluster ids produce the
  same human-readable regime assignment.
- Use simple deterministic ranking first: lowest liquidity, highest volatility, highest trend
  strength, then the remaining cluster as mean reversion.
