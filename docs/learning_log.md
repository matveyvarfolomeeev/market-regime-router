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

## Current Review Notes

- `pytest` passes for the current milestone tests.
- Source cleanup still needs to pass `ruff check .`, `ruff format --check .`, and `mypy src`.
- Keep library modules free of scratch `if __name__ == "__main__"` examples; use tests or notebooks
  for experiments.

## Next Milestone: Feature Engineering Baseline

- Implement `build_features()` with causal rolling features only.
- Start by replacing the skipped feature tests with real tests for no-lookahead behavior and initial
  rolling-window `NaN` handling.
