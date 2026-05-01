"""Feature engineering test plan."""

import pytest

from market_regime_router.features.build import FEATURE_COLUMNS


def test_feature_contract_names_are_declared() -> None:
    expected = {
        "return_1",
        "rolling_volatility",
        "trend_strength",
        "mean_reversion_distance",
        "liquidity_proxy",
    }
    assert expected.issubset(FEATURE_COLUMNS)


@pytest.mark.skip(reason="Implement after build_features exists.")
def test_features_are_causal_without_lookahead() -> None:
    """Future test: changing a future close must not alter past feature rows."""


@pytest.mark.skip(reason="Implement after build_features exists.")
def test_features_handle_initial_rolling_nans() -> None:
    """Future test: rolling windows should produce predictable initial NaNs."""
