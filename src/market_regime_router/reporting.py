"""Render backtest results into markdown and a plot artifact."""

from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")  # headless backend: write files, never open a window
import matplotlib.pyplot as plt  # noqa: E402

from market_regime_router.pipeline import PipelineResult  # noqa: E402

_METRIC_LABELS = {
    "total_return": "Total return",
    "cagr": "CAGR",
    "max_drawdown": "Max drawdown",
    "sharpe_like": "Sharpe-like",
    "turnover": "Turnover",
    "trade_count": "Trade count",
}


def _format_metric(name: str, value: float) -> str:
    if name in {"total_return", "cagr", "max_drawdown"}:
        return f"{value:.2%}"
    if name == "trade_count":
        return f"{int(value)}"
    return f"{value:.3f}"


def write_equity_plot(result: PipelineResult, path: Path) -> Path:
    """Save the equity curve as a PNG."""
    equity = result.backtest.equity_curve["equity"]

    figure, axes = plt.subplots(figsize=(10, 4))
    axes.plot(equity.index, equity.to_numpy(), color="#1f77b4")
    axes.set_title("Equity curve")
    axes.set_ylabel("Equity")
    axes.grid(True, alpha=0.3)
    figure.tight_layout()
    figure.savefig(path, dpi=120)
    plt.close(figure)
    return path


def write_report(result: PipelineResult, output_dir: Path) -> Path:
    """Write a markdown report plus an equity-curve plot to ``output_dir``."""
    output_dir.mkdir(parents=True, exist_ok=True)
    plot_path = write_equity_plot(result, output_dir / "equity_curve.png")

    frame = result.signal_frame
    regime_counts = frame["regime"].value_counts()
    regime_share = (regime_counts / len(frame)).sort_index()

    lines: list[str] = ["# Backtest Report", ""]

    period = f"{frame.index[0]} -> {frame.index[-1]}"
    lines += ["## Coverage", "", f"- bars: {len(frame)}", f"- period: {period}", ""]

    lines += ["## Metrics", "", "| metric | value |", "|---|---|"]
    for name, value in result.backtest.metrics.items():
        lines.append(f"| {_METRIC_LABELS.get(name, name)} | {_format_metric(name, value)} |")
    lines.append("")

    lines += ["## Regime Distribution", "", "| regime | share |", "|---|---|"]
    for regime, share in regime_share.items():
        lines.append(f"| {regime} | {share:.2%} |")
    lines.append("")

    lines += ["## Artifacts", "", f"- equity curve: `{plot_path.name}`", ""]

    report_path = output_dir / "report.md"
    report_path.write_text("\n".join(lines), encoding="utf-8")
    return report_path
