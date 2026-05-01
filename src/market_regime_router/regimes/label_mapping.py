"""Deterministic mapping from cluster ids to regime names."""

from __future__ import annotations

from typing import TYPE_CHECKING, Literal

if TYPE_CHECKING:
    import pandas as pd


RegimeName = Literal["trend", "mean_reversion", "high_vol", "low_liquidity"]

REGIME_NAMES: tuple[RegimeName, ...] = (
    "trend",
    "mean_reversion",
    "high_vol",
    "low_liquidity",
)


def map_clusters_to_regimes(
    features: pd.DataFrame,
    cluster_labels: pd.Series,
) -> dict[int, RegimeName]:
    """Map arbitrary cluster ids to stable regime names.

    TODO: Rank cluster statistics so label numbers from KMeans do not matter.
    """

    raise NotImplementedError("Cluster label mapping is a milestone 3 task.")
