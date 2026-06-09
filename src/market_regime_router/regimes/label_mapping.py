"""Deterministic mapping from cluster ids to regime names.

KMeans returns arbitrary integer cluster ids: the same market structure can be
labelled ``0`` on one run and ``3`` on another. Downstream routing needs stable,
human-readable names, so this module ranks cluster-level feature statistics and
assigns exactly one regime to each cluster. The ranking only depends on feature
values, never on the numeric ids, so permuting the ids does not change the
result. The rule follows ``reports/market_cluster_sandbox/cluster_hypotheses.md``.
"""

from __future__ import annotations

from typing import Literal

import pandas as pd

RegimeName = Literal["quiet_range", "trend_continuation", "risk_off", "high_vol_reversal"]

REGIME_NAMES: tuple[RegimeName, ...] = (
    "quiet_range",
    "trend_continuation",
    "risk_off",
    "high_vol_reversal",
)

# Feature groups used to score each cluster. Each tuple is averaged after the
# cluster means are z-scored across clusters, so features on different scales
# contribute comparably.
_ACTIVITY_FEATURES = ("rolling_volatility", "volatility_ratio", "range_pct", "trend_strength")
_UP_TREND_FEATURES = ("return_24_log", "return_48_log", "return_168_log", "trend_strength")


def _zscore_columns(frame: pd.DataFrame) -> pd.DataFrame:
    """Z-score each column across clusters, leaving constant columns at zero."""
    std = frame.std(ddof=0)
    safe_std = std.where(std > 0, 1.0)
    return (frame - frame.mean()) / safe_std


def _composite_score(scaled_means: pd.DataFrame, columns: tuple[str, ...]) -> dict[int, float]:
    """Average the z-scored cluster means over a feature group, keyed by cluster id."""
    score = scaled_means[list(columns)].mean(axis=1)
    return dict(zip(score.index.tolist(), score.tolist(), strict=True))


def map_clusters_to_regimes(
    features: pd.DataFrame,
    cluster_labels: pd.Series,
) -> dict[int, RegimeName]:
    """Map arbitrary cluster ids to stable regime names.

    The assignment is greedy and order-independent of the cluster ids. Each
    regime is picked by its strongest defining trait, so the only ambiguous
    cluster (a sell-off bounce) is resolved before it can be confused with the
    sustained sell-off:

    1. ``quiet_range``: lowest combined activity (volatility, volatility ratio,
       range, trend strength).
    2. ``high_vol_reversal``: among the rest, the highest ``volatility_ratio`` —
       its signature is volatility spiking far above its own background.
    3. ``trend_continuation``: among the rest, the strongest sustained move up
       (highest multi-horizon returns and trend strength).
    4. ``risk_off``: the remaining cluster (the sustained move down).
    """
    aligned = cluster_labels.reindex(features.index)
    cluster_means = features.groupby(aligned).mean()

    if len(cluster_means) != len(REGIME_NAMES):
        raise ValueError(f"expected {len(REGIME_NAMES)} clusters to map, got {len(cluster_means)}")

    scaled = _zscore_columns(cluster_means)

    remaining = [int(cluster_id) for cluster_id in cluster_means.index]
    mapping: dict[int, RegimeName] = {}

    def assign(regime: RegimeName, cluster_id: int) -> None:
        mapping[cluster_id] = regime
        remaining.remove(cluster_id)

    activity = _composite_score(scaled, _ACTIVITY_FEATURES)
    assign("quiet_range", min(remaining, key=lambda c: activity[c]))

    volatility_ratio = dict(
        zip(
            cluster_means.index.tolist(),
            cluster_means["volatility_ratio"].tolist(),
            strict=True,
        )
    )
    assign("high_vol_reversal", max(remaining, key=lambda c: volatility_ratio[c]))

    up_trend = _composite_score(scaled, _UP_TREND_FEATURES)
    assign("trend_continuation", max(remaining, key=lambda c: up_trend[c]))

    assign("risk_off", remaining[0])

    return mapping
