"""Regime mapping tests."""

import numpy as np
import pandas as pd

from market_regime_router.regimes.label_mapping import REGIME_NAMES, map_clusters_to_regimes

# Synthetic cluster centres, one row group per regime, chosen so the ranking is
# unambiguous: a calm cluster, a sustained up-trend, a sustained sell-off, and a
# high-volatility cluster.
_CLUSTER_CENTRES = {
    "calm": {
        "return_24_log": 0.001,
        "return_48_log": 0.002,
        "return_168_log": 0.003,
        "rolling_volatility": 0.003,
        "volatility_ratio": 0.85,
        "trend_strength": 0.10,
        "mean_reversion_distance": 0.05,
        "range_pct": 0.004,
    },
    "up": {
        "return_24_log": 0.027,
        "return_48_log": 0.037,
        "return_168_log": 0.044,
        "rolling_volatility": 0.005,
        "volatility_ratio": 1.10,
        "trend_strength": 0.24,
        "mean_reversion_distance": 1.56,
        "range_pct": 0.009,
    },
    "down": {
        "return_24_log": -0.021,
        "return_48_log": -0.021,
        "return_168_log": -0.017,
        "rolling_volatility": 0.004,
        "volatility_ratio": 1.00,
        "trend_strength": 0.18,
        "mean_reversion_distance": -1.97,
        "range_pct": 0.012,
    },
    "high_vol": {
        "return_24_log": -0.024,
        "return_48_log": -0.042,
        "return_168_log": -0.056,
        "rolling_volatility": 0.008,
        "volatility_ratio": 1.56,
        "trend_strength": 0.20,
        "mean_reversion_distance": -0.52,
        "range_pct": 0.010,
    },
}

_FEATURE_ORDER = (
    "return_24_log",
    "return_48_log",
    "return_168_log",
    "rolling_volatility",
    "volatility_ratio",
    "trend_strength",
    "mean_reversion_distance",
    "range_pct",
)


def _features_and_labels(label_for: dict[str, int]) -> tuple[pd.DataFrame, pd.Series]:
    """Build a feature frame and cluster labels from the synthetic centres.

    ``label_for`` maps each named centre to the integer cluster id it should
    receive, which lets a test permute the ids without touching the data.
    """
    rows = []
    labels = []
    rng = np.random.default_rng(0)
    for name, centre in _CLUSTER_CENTRES.items():
        for _ in range(5):
            jitter = {k: v + rng.normal(0, abs(v) * 1e-6) for k, v in centre.items()}
            rows.append(jitter)
            labels.append(label_for[name])

    index = pd.date_range("2026-01-01", periods=len(rows), freq="h", tz="UTC")
    features = pd.DataFrame(rows, index=index)[list(_FEATURE_ORDER)]
    cluster_labels = pd.Series(labels, index=index, name="cluster")
    return features, cluster_labels


def test_all_mvp_regime_names_are_declared() -> None:
    assert set(REGIME_NAMES) == {
        "quiet_range",
        "trend_continuation",
        "risk_off",
        "high_vol_reversal",
    }


def test_map_assigns_each_centre_to_expected_regime() -> None:
    features, labels = _features_and_labels({"calm": 0, "up": 1, "down": 2, "high_vol": 3})

    mapping = map_clusters_to_regimes(features, labels)

    assert mapping == {
        0: "quiet_range",
        1: "trend_continuation",
        2: "risk_off",
        3: "high_vol_reversal",
    }


def test_cluster_mapping_does_not_depend_on_cluster_id_order() -> None:
    """Permuted KMeans ids must map to the same regime per underlying centre."""
    base_ids = {"calm": 0, "up": 1, "down": 2, "high_vol": 3}
    permuted_ids = {"calm": 3, "up": 0, "down": 1, "high_vol": 2}

    base_features, base_labels = _features_and_labels(base_ids)
    permuted_features, permuted_labels = _features_and_labels(permuted_ids)

    base_mapping = map_clusters_to_regimes(base_features, base_labels)
    permuted_mapping = map_clusters_to_regimes(permuted_features, permuted_labels)

    for name in _CLUSTER_CENTRES:
        assert base_mapping[base_ids[name]] == permuted_mapping[permuted_ids[name]]


def test_mapping_returns_each_regime_exactly_once() -> None:
    features, labels = _features_and_labels({"calm": 0, "up": 1, "down": 2, "high_vol": 3})

    mapping = map_clusters_to_regimes(features, labels)

    assert sorted(mapping.values()) == sorted(REGIME_NAMES)
