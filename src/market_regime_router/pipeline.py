"""End-to-end pipeline wiring data, regimes, routing, and the backtest together."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd

from market_regime_router.backtest.engine import BacktestResult, run_backtest
from market_regime_router.config import ExecutionConfig, ProjectConfig
from market_regime_router.data.normalize import normalize_ohlcv
from market_regime_router.features.build import build_features
from market_regime_router.regimes.detector import RegimeDetector
from market_regime_router.regimes.label_mapping import map_clusters_to_regimes
from market_regime_router.router import StrategyRouter
from market_regime_router.strategies.base import StrategyContext
from market_regime_router.strategies.mean_reversion import MeanReversionStrategy
from market_regime_router.strategies.risk_off import RiskOffStrategy
from market_regime_router.strategies.trend import TrendStrategy

# Liquidity filter thresholds on log_liquidity_proxy = log(volume / avg_volume).
# At or above average volume the position is taken in full; thin volume halves it;
# very thin volume (below ~50% of average) skips the trade entirely. Low liquidity
# is a risk filter here, not a regime of its own.
_LIQUIDITY_REDUCE_THRESHOLD = 0.0
_LIQUIDITY_SKIP_THRESHOLD = np.log(0.5)


@dataclass(frozen=True)
class PipelineResult:
    """Everything produced by an end-to-end run."""

    signal_frame: pd.DataFrame
    backtest: BacktestResult


def build_default_router() -> StrategyRouter:
    """Build the router used by the MVP, sharing one defensive strategy."""
    defensive = RiskOffStrategy()
    return StrategyRouter(
        quiet_range_strategy=MeanReversionStrategy(),
        trend_continuation_strategy=TrendStrategy(),
        risk_off_strategy=defensive,
        high_vol_reversal_strategy=defensive,
    )


def _liquidity_scale(log_liquidity_proxy: float) -> float:
    if log_liquidity_proxy < _LIQUIDITY_SKIP_THRESHOLD:
        return 0.0
    if log_liquidity_proxy < _LIQUIDITY_REDUCE_THRESHOLD:
        return 0.5
    return 1.0


def apply_execution_policy(
    target_position: pd.Series,
    liquidity_scale: pd.Series,
    execution: ExecutionConfig,
) -> pd.Series:
    """Damp the realized position to keep turnover down.

    Two rules are walked forward over the realized position, so they see the real
    exposure across every regime, not just one strategy's view:

    - a fresh entry from flat is blocked unless the liquidity filter is at full
      size (``require_full_liquidity_to_enter``);
    - after any change the position is frozen for ``min_hold_bars`` bars before it
      may move again. Exits to flat are never blocked.
    """
    targets = target_position.to_numpy()
    scales = liquidity_scale.to_numpy()
    held = np.zeros(len(targets))

    current = 0.0
    bars_since_change = execution.min_hold_bars  # allow the first trade immediately

    for i in range(len(targets)):
        target = float(targets[i])

        opening_from_flat = current == 0.0 and target != 0.0
        if opening_from_flat and execution.require_full_liquidity_to_enter and scales[i] < 1.0:
            target = 0.0

        # Block early changes unless we are closing the position.
        if target != current and target != 0.0 and bars_since_change < execution.min_hold_bars:
            target = current

        if target != current:
            current = target
            bars_since_change = 0
        else:
            bars_since_change += 1

        held[i] = current

    return pd.Series(held, index=target_position.index, name="position")


def build_signal_frame(
    normalized_ohlcv: pd.DataFrame,
    config: ProjectConfig,
    router: StrategyRouter | None = None,
) -> pd.DataFrame:
    """Turn normalized OHLCV into a timestamped close/regime/signal/position frame."""
    router = router or build_default_router()

    features = build_features(normalized_ohlcv, config.features)
    features.index = pd.Index(normalized_ohlcv["timestamp"], name="timestamp")
    features = features.dropna()

    if features.empty:
        raise ValueError("no feature rows survived warmup; need more OHLCV history")

    detector = RegimeDetector(config.regimes).fit(features)
    clusters = detector.predict(features)
    mapping = map_clusters_to_regimes(features, clusters)
    regimes = clusters.map(mapping)

    signals = []
    scales = []
    for (timestamp, row), regime in zip(features.iterrows(), regimes, strict=True):
        strategy = router.select(regime)
        context = StrategyContext(timestamp=timestamp, regime=regime, row=row)
        signals.append(strategy.generate_signal(context))
        scales.append(_liquidity_scale(float(row["log_liquidity_proxy"])))

    signal = pd.Series(signals, index=features.index, name="signal", dtype="float64")
    scale = pd.Series(scales, index=features.index, name="liquidity_scale")

    close = normalized_ohlcv.set_index("timestamp")["close"].reindex(features.index)
    target_position = signal * scale
    position = apply_execution_policy(target_position, scale, config.execution)

    return pd.DataFrame(
        {
            "close": close,
            "regime": regimes,
            "signal": signal,
            "liquidity_scale": scale,
            "position": position,
        }
    )


def run_pipeline(
    raw_ohlcv: pd.DataFrame,
    config: ProjectConfig,
    router: StrategyRouter | None = None,
) -> PipelineResult:
    """Run normalize -> features -> regimes -> routing -> backtest on raw OHLCV."""
    normalized = normalize_ohlcv(raw_ohlcv)
    signal_frame = build_signal_frame(normalized, config, router=router)
    backtest = run_backtest(signal_frame[["close", "position"]], config.backtest)
    return PipelineResult(signal_frame=signal_frame, backtest=backtest)
