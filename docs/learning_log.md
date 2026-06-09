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

## Milestone 4: Strategy Routing

- Implemented three strategies behind the shared `Strategy` protocol:
  `TrendStrategy` (long-only momentum), `MeanReversionStrategy` (z-score fade),
  and `RiskOffStrategy` (always flat).
- `StrategyRouter.select()` maps each regime to its strategy and lets `risk_off`
  and `high_vol_reversal` share one defensive instance.
- Strategies read features from the row context and return flat on `NaN`, so the
  warmup rows do not generate spurious trades.

## Milestone 5: Backtest Engine

- Implemented `run_backtest()` as a vectorized pandas backtest: it shifts the
  target position by one bar before it earns a return (no look-ahead) and charges
  `fee_bps + slippage_bps` on the change in held exposure.
- Implemented `calculate_metrics()` for total return, CAGR, max drawdown, a
  Sharpe-like ratio, turnover, and trade count.
- Subtle lesson: a position change on the last bar never applies because there is
  no next bar to hold it, so round-trip cost tests need an exit with bars left.

## Milestone 6: End-to-End CLI and Reports

- Added `pipeline.py` to wire normalize -> features -> regimes -> mapping ->
  routing -> liquidity filter -> backtest, and `reporting.py` to render a
  markdown report plus an equity-curve plot.
- Applied the research liquidity rule as a position-sizing filter (full / half /
  skip on `log_liquidity_proxy`) rather than as a regime.
- Built the `mrr` CLI with `ingest` and `run` subcommands; `run --input` works
  fully offline from a saved csv/parquet.
- Added an end-to-end test on synthetic OHLCV plus a CLI test, so the whole
  pipeline is covered without any network calls.

## Current Quality Gate

- `pytest`: 43 passed, 0 skipped.
- `ruff check .`: passed.
- `ruff format --check .`: passed.
- `mypy src`: passed.

## Backtest Findings on Real Data

First full run on ~19.8k bars of real BTC/USDT 1h (2024-03 -> 2026-06):

- total return -94%, max drawdown -94%, Sharpe-like -5.7, **5709 trades**.
- The regime split is sensible (quiet_range 52%, trend_continuation 21%,
  high_vol_reversal 15%, risk_off 11%) and the pipeline runs cleanly, so the
  infrastructure is correct.
- The loss is a turnover problem: the mean-reversion strategy flips long/short
  every time the z-score crosses +/-1 during the 52% of bars in `quiet_range`,
  and `fee_bps + slippage_bps` on that churn dominates the result. The naive
  strategies have no edge once costs are charged.

Honest conclusion: the MVP is a correct, end-to-end research harness, not a
profitable strategy. The next experiments should attack turnover: add a
z-score exit band / hysteresis, hold positions for a minimum number of bars,
and only trade when the liquidity filter is full size.

## Project Complete

All six milestones are implemented. Possible future work: reduce turnover in the
mean-reversion strategy, cache processed features to parquet, add the candidate
features from the research that were not adopted yet, and validate on a held-out
period.
