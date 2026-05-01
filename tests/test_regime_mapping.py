"""Regime mapping test plan."""

import pytest

from market_regime_router.regimes.label_mapping import REGIME_NAMES


def test_all_mvp_regime_names_are_declared() -> None:
    assert set(REGIME_NAMES) == {"trend", "mean_reversion", "high_vol", "low_liquidity"}


@pytest.mark.skip(reason="Implement after map_clusters_to_regimes exists.")
def test_cluster_mapping_does_not_depend_on_cluster_id_order() -> None:
    """Future test: permuted KMeans labels should map to the same regime names."""
