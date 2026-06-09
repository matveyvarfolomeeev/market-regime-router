"""Execution policy tests."""

import pandas as pd

from market_regime_router.config import ExecutionConfig
from market_regime_router.pipeline import apply_execution_policy


def _series(values: list[float]) -> pd.Series:
    index = pd.date_range("2026-01-01", periods=len(values), freq="h", tz="UTC")
    return pd.Series(values, index=index)


def test_min_hold_freezes_position_after_a_change() -> None:
    target = _series([1.0, -1.0, -1.0, -1.0, -1.0])
    scale = _series([1.0, 1.0, 1.0, 1.0, 1.0])
    execution = ExecutionConfig(min_hold_bars=2)

    held = apply_execution_policy(target, scale, execution)

    # Enter long on bar 0, then the flip is held for two bars before it is allowed
    # to flip short on bar 3.
    assert held.tolist() == [1.0, 1.0, 1.0, -1.0, -1.0]


def test_min_hold_never_blocks_an_exit() -> None:
    target = _series([1.0, 0.0, 0.0])
    scale = _series([1.0, 1.0, 1.0])
    execution = ExecutionConfig(min_hold_bars=5)

    held = apply_execution_policy(target, scale, execution)

    # Closing to flat is always allowed even before the minimum hold elapses.
    assert held.tolist() == [1.0, 0.0, 0.0]


def test_liquidity_gate_blocks_entries_on_thin_volume() -> None:
    target = _series([1.0, 1.0])
    scale = _series([0.5, 1.0])
    execution = ExecutionConfig(min_hold_bars=1, require_full_liquidity_to_enter=True)

    held = apply_execution_policy(target, scale, execution)

    # First entry is on half-size liquidity and is skipped; the full-size bar enters.
    assert held.tolist() == [0.0, 1.0]


def test_policy_reduces_trade_count_versus_raw_target() -> None:
    target = _series([1.0, -1.0, 1.0, -1.0, 1.0, -1.0])
    scale = _series([1.0] * 6)

    raw_changes = int((target.diff().fillna(target).abs() > 0).sum())
    held = apply_execution_policy(target, scale, ExecutionConfig(min_hold_bars=3))
    held_changes = int((held.diff().fillna(held).abs() > 0).sum())

    assert raw_changes == 6
    assert held_changes < raw_changes
