"""Command-line entrypoint for the market regime router."""

from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

from market_regime_router.config import ProjectConfig, load_config
from market_regime_router.data.ingest import fetch_ohlcv
from market_regime_router.pipeline import run_pipeline
from market_regime_router.reporting import write_report

DEFAULT_CONFIG = Path("configs/default.yaml")
DEFAULT_REPORT_DIR = Path("reports/backtest")


def _load_raw_ohlcv(config: ProjectConfig, input_path: Path | None) -> pd.DataFrame:
    """Load raw OHLCV from an explicit file, the raw cache, or the exchange."""
    if input_path is not None:
        return _read_frame(input_path)

    cache = config.data.raw_path
    if cache.exists():
        return _read_frame(cache)

    return fetch_ohlcv(config.data)


def _read_frame(path: Path) -> pd.DataFrame:
    if path.suffix == ".csv":
        return pd.read_csv(path)
    return pd.read_parquet(path)


def _ingest(config: ProjectConfig) -> int:
    raw = fetch_ohlcv(config.data)
    config.data.raw_path.parent.mkdir(parents=True, exist_ok=True)
    raw.to_parquet(config.data.raw_path)
    print(f"Saved {len(raw)} raw bars to {config.data.raw_path}")
    return 0


def _run(config: ProjectConfig, input_path: Path | None, output_dir: Path) -> int:
    raw = _load_raw_ohlcv(config, input_path)
    result = run_pipeline(raw, config)
    report_path = write_report(result, output_dir)

    metrics = result.backtest.metrics
    print(f"Backtested {len(result.signal_frame)} bars")
    print(f"  total_return : {metrics['total_return']:.2%}")
    print(f"  max_drawdown : {metrics['max_drawdown']:.2%}")
    print(f"  sharpe_like  : {metrics['sharpe_like']:.3f}")
    print(f"  trade_count  : {int(metrics['trade_count'])}")
    print(f"Report written to {report_path}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="mrr", description=__doc__)
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG, help="path to config YAML")

    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("ingest", help="fetch OHLCV from the exchange into the raw cache")

    run_parser = subparsers.add_parser("run", help="run the full pipeline and write a report")
    run_parser.add_argument(
        "--input", type=Path, default=None, help="OHLCV csv/parquet to use instead of fetching"
    )
    run_parser.add_argument(
        "--output", type=Path, default=DEFAULT_REPORT_DIR, help="report output directory"
    )

    return parser


def main(argv: list[str] | None = None) -> int:
    """Run the CLI."""
    parser = build_parser()
    args = parser.parse_args(argv)
    config = load_config(args.config)

    if args.command == "ingest":
        return _ingest(config)
    if args.command == "run":
        return _run(config, args.input, args.output)

    parser.error(f"unknown command: {args.command}")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
