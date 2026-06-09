# Mini Research: BTC/USDT 1h Regime Clusters

Дата обновления: 2026-05-08.

Конфиг: `configs/default.yaml`.

Данные:

- exchange: `binance`
- symbol: `BTC/USDT`
- timeframe: `1h`
- requested limit: `20000`
- rows after feature warmup: `19952`
- period: `2024-01-27 13:00 UTC` -> `2026-05-07 20:00 UTC`

Теперь данных достаточно, чтобы увидеть разные рыночные режимы. Предыдущий
вывод на 952 строках был слишком шумным.

## Current KMeans Result

Текущий KMeans использует только старые фичи:

- `return_1_log`
- `rolling_volatility`
- `trend_strength`
- `mean_reversion_distance`
- `liquidity_proxy`

Профиль текущих кластеров:

| cluster | rows | share | return | vol | trend | z-score | liquidity |
|---:|---:|---:|---:|---:|---:|---:|---:|
| 0 | 5788 | 29.0% | 0.00046 | 0.00591 | 0.262 | 0.244 | 0.740 |
| 1 | 10444 | 52.3% | 0.00007 | 0.00375 | 0.087 | 0.010 | 0.785 |
| 2 | 1729 | 8.7% | 0.00728 | 0.00469 | 0.180 | 1.919 | 2.218 |
| 3 | 1991 | 10.0% | -0.00770 | 0.00518 | 0.182 | -1.856 | 2.142 |

Интерпретация:

- `cluster 1`: спокойный базовый режим. Это самый большой кластер, низкая
  волатильность, слабая трендовость, z-score около нуля.
- `cluster 0`: трендовый/волатильный режим продолжения. Самая высокая
  `trend_strength`, самая высокая `rolling_volatility`, но низкая ликвидность.
- `cluster 2`: сильный пробой вверх. Высокий `return_1_log`, высокий
  положительный z-score, высокий объем.
- `cluster 3`: сильное движение вниз / risk-off. Самый отрицательный
  `return_1_log`, отрицательный z-score, высокий объем.

Вывод: старые имена `trend`, `mean_reversion`, `high_vol`, `low_liquidity`
не очень хорошо описывают реальные кластеры. Особенно `low_liquidity`: это
скорее фильтр риска, а не отдельный тип рынка.

## Candidate Feature Check

Я проверил дополнительные фичи только для исследования:

- `return_24_log`
- `return_48_log`
- `return_168_log`
- `abs_mean_reversion_distance`
- `range_pct`
- `volatility_ratio`
- `log_liquidity_proxy`

Пробный KMeans с этими фичами дал более читаемые режимы:

| candidate cluster | rows | share | meaning |
|---:|---:|---:|---|
| 0 | 10584 | 53.5% | `quiet_range` |
| 1 | 4282 | 21.6% | `trend_continuation` |
| 2 | 2412 | 12.2% | `risk_off` |
| 3 | 2506 | 12.7% | `high_vol_reversal` |

Средние значения новых и ключевых старых фичей по пробным кластерам:

| candidate cluster | rows | share | return_1_log | return_24_log | return_48_log | return_168_log | rolling_volatility | volatility_ratio | trend_strength | mean_reversion_distance | abs_mean_reversion_distance | range_pct | log_liquidity_proxy |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 0 | 10584 | 53.5% | 0.00005 | 0.00074 | 0.00278 | 0.00931 | 0.00367 | 0.85159 | 0.10697 | 0.04206 | 0.77001 | 0.00456 | -0.40124 |
| 1 | 4282 | 21.6% | 0.00238 | 0.02737 | 0.03692 | 0.04377 | 0.00505 | 1.09592 | 0.23522 | 1.56353 | 1.59799 | 0.00850 | 0.09164 |
| 2 | 2412 | 12.2% | -0.00557 | -0.02085 | -0.02116 | -0.01717 | 0.00453 | 1.00519 | 0.17554 | -1.96731 | 1.98244 | 0.01174 | 0.51267 |
| 3 | 2506 | 12.7% | 0.00134 | -0.02378 | -0.04230 | -0.05589 | 0.00787 | 1.55696 | 0.20362 | -0.51861 | 0.89127 | 0.00976 | -0.37624 |

Какие фичи реально помогают разделять:

| feature | что разделяет |
|---|---|
| `return_24_log`, `return_48_log`, `return_168_log` | Отличают `trend_continuation` от `risk_off` и `high_vol_reversal`. |
| `mean_reversion_distance` | Дает знак отклонения: положительный breakout/continuation против отрицательного stress/reversal. |
| `abs_mean_reversion_distance` | Показывает силу отклонения независимо от направления; особенно выделяет `risk_off`. |
| `range_pct` | Хорошо отделяет импульсные и стрессовые режимы от `quiet_range`. |
| `volatility_ratio` | Лучше всего выделяет `high_vol_reversal`, где волатильность резко выше фона. |
| `log_liquidity_proxy` | Подтверждает импульс/стресс объемом, но лучше использовать как risk filter, не как отдельный режим. |

Коротко по ним:

- `quiet_range`: низкая волатильность, низкий range, слабая трендовость.
- `trend_continuation`: сильные положительные `return_24_log`,
  `return_48_log`, `return_168_log`, высокая `trend_strength`.
- `risk_off`: отрицательные returns, сильный отрицательный z-score,
  высокий range и высокий объем.
- `high_vol_reversal`: самая высокая волатильность и `volatility_ratio`,
  но короткий return положительный при плохом 24-168h momentum. Это похоже
  на отскок внутри стрессового/медвежьего режима, а не на обычный bullish trend.

## Final Regimes

Итогово я бы выбрал такие режимы:

1. `quiet_range`
   Спокойный рынок в диапазоне. Главный кандидат для mean-reversion.

2. `trend_continuation`
   Устойчивое движение вверх или продолжение тренда. Главный кандидат для
   trend-following.

3. `risk_off`
   Сильное движение вниз, стресс, продавливание. Для long-only стратегии это
   defensive/flat режим. Для более сложной стратегии это кандидат для short.

4. `high_vol_reversal`
   Высокая волатильность и возможный отскок после сильного движения. Здесь
   нельзя слепо включать trend-following: нужна отдельная осторожная логика.

`low_liquidity` не берем как режим. Используем как фильтр:

- низкая ликвидность -> меньше позиция;
- очень низкая ликвидность -> можно пропустить вход;
- высокая ликвидность на импульсе -> подтверждение breakout/risk-off движения.

## Final Features

Оставить:

- `return_1_log`
- `rolling_volatility`
- `trend_strength`
- `mean_reversion_distance`

Добавить:

- `return_24_log`
- `return_48_log`
- `return_168_log`
- `abs_mean_reversion_distance`
- `range_pct`
- `volatility_ratio`
- `log_liquidity_proxy`

Убрать или заменить:

- `liquidity_proxy` лучше заменить на `log_liquidity_proxy`, чтобы объемные
  выбросы меньше ломали KMeans.

## Deterministic Mapping

После KMeans считаем средние значения фичей по каждому кластеру.

Правило:

1. `quiet_range`
   Кластер с минимальной активностью:
   низкие `rolling_volatility_mean`, `volatility_ratio_mean`,
   `range_pct_mean`, `trend_strength_mean`.

2. `risk_off`
   Среди оставшихся кластер с самым сильным движением вниз:
   минимальные `return_24_log_mean`, `return_48_log_mean`,
   `return_168_log_mean`, `mean_reversion_distance_mean`.

3. `trend_continuation`
   Среди оставшихся кластер с самым сильным устойчивым движением вверх:
   максимальные `return_24_log_mean`, `return_48_log_mean`,
   `return_168_log_mean`, `trend_strength_mean`.

4. `high_vol_reversal`
   Оставшийся кластер с высокой `rolling_volatility_mean`,
   `volatility_ratio_mean` или `range_pct_mean`.

После этого отдельно применяем liquidity filter через `log_liquidity_proxy`.

## Strategy Hypotheses

- `quiet_range`: mean-reversion, маленькие цели, строгий контроль комиссии.
- `trend_continuation`: trend-following long, trailing exit.
- `risk_off`: flat/defensive для long-only; short logic если разрешена.
- `high_vol_reversal`: сниженный размер позиции, ждать подтверждение, не
  считать автоматическим продолжением тренда.

## Next Step

Следующий практический шаг: перенести выбранные фичи в `build_features()`,
обновить список режимов в конфиге и реализовать deterministic mapping по
правилу выше. Потом проверить стратегии в backtest.
