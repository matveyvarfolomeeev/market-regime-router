"""Учебная песочница для просмотра кластеров на реальных OHLCV данных.

Файл специально простой и не является частью production-пайплайна. Он берет
настройки только из базового конфига `configs/default.yaml` и использует уже
написанные функции проекта:

- `fetch_ohlcv()` для загрузки данных;
- `normalize_ohlcv()` для приведения OHLCV к общему формату;
- `build_features()` для построения признаков;
- `RegimeDetector` для KMeans-кластеров.

Гипотезы для ручного анализа кластеров:

1. Если у кластера высокая `rolling_volatility`, это кандидат на рынок высокой
   волатильности.

2. Если у кластера высокая `trend_strength`, это кандидат на трендовый рынок.
   Если одновременно высокий `liquidity_proxy` и большое отклонение от средней,
   это может быть не спокойный тренд, а импульсный пробой.

3. Если у кластера низкая `trend_strength` и умеренная волатильность, это
   кандидат на mean-reversion рынок.

4. Если у кластера самый низкий `liquidity_proxy`, это кандидат на рынок низкой
   ликвидности. В MVP это только приближение через объем, без стакана и спреда.

Запуск:
    .\\.venv\\Scripts\\python.exe research\\market_cluster_sandbox.py
"""

from __future__ import annotations

from pathlib import Path

from market_regime_router.config import load_config
from market_regime_router.data.ingest import fetch_ohlcv
from market_regime_router.data.normalize import normalize_ohlcv
from market_regime_router.features.build import FEATURE_COLUMNS, build_features
from market_regime_router.regimes.detector import RegimeDetector

CONFIG_PATH = Path("configs/default.yaml")
OUTPUT_DIR = Path("reports/market_cluster_sandbox")


def main() -> int:
    config = load_config(CONFIG_PATH)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    raw_ohlcv = fetch_ohlcv(config.data)
    normalized_ohlcv = normalize_ohlcv(raw_ohlcv)
    features = build_features(normalized_ohlcv, config.features)
    features.index = normalized_ohlcv["timestamp"]
    features = features.dropna()

    detector = RegimeDetector(config.regimes).fit(features)
    clusters = detector.predict(features)

    research = normalized_ohlcv.set_index("timestamp").join(features)
    research = research.loc[features.index].copy()
    research["cluster"] = clusters

    cluster_profile = research.groupby("cluster").agg(
        rows=("cluster", "size"),
        **{f"{column}_mean": (column, "mean") for column in FEATURE_COLUMNS},
    )
    cluster_profile["share"] = cluster_profile["rows"] / len(research)

    research.reset_index().to_csv(OUTPUT_DIR / "research_dataset.csv", index=False)
    cluster_profile.to_csv(OUTPUT_DIR / "cluster_profile.csv")

    print(f"Saved research dataset to {OUTPUT_DIR / 'research_dataset.csv'}")
    print(f"Saved cluster profile to {OUTPUT_DIR / 'cluster_profile.csv'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
