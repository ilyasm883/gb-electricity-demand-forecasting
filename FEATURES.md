# Dataset, Features and Pipeline

**Project:** Multi-Horizon Electricity Demand Forecasting Using Classical Models and Deep Temporal Networks
**Student:** Illyas Matloob (B01050018), COM748

The full working is in the notebooks: `01_download_dataset`, `02_preprocessing`, `03_eda` and `04_feature_engineering`. All the figures quoted below come from them.

---

## 1. Data sources

| Dataset | File | Size | Content |
|---|---|---|---|
| OPSD Time Series v2020-10-06 [16] | `time_series_60min_singleindex.csv` | 130 MB, 300 columns | Hourly load, generation and prices for 32 European countries (ENTSO-E Transparency Platform) |
| OPSD Weather Data v2020-09-16 [17] | `weather_data.csv` | 234 MB, 85 columns | Hourly country-average temperature and solar radiation, 1980–2019 (NASA MERRA-2) |

Of the 300 + 85 columns, **the project uses only 2**: GB load and GB temperature.

## 2. Columns selected from the raw data

| Raw column | Renamed to | Unit | Role |
|---|---|---|---|
| `GB_GBN_load_actual_entsoe_transparency` | `load` | MW | **Target**: actual hourly electricity demand in Great Britain |
| `GB_temperature` | `temperature` | °C | **Input**: average air temperature for GB |

**Columns not used, and why:**

| Column group | Reason for exclusion |
|---|---|
| GB load forecast (`GB_GBN_load_forecast_*`) | The grid operator's own forecast. Not part of the proposal |
| Day-ahead price | Price is driven by demand (an outcome, not a cause) and is not known when the forecast is made |
| Wind and solar generation and capacity | Supply-side variables. Using them would need their own forecasts and is outside the scope |
| Solar radiation | Kept out to keep the comparison focused. Temperature is the weather variable named in RQ4 |
| `GB_NIR_*`, `GB_UKM_*` | Northern Ireland and UK total. The project targets Great Britain (`GBN`) |
| Other countries (incl. Germany) | The project uses Great Britain only |
| Year 2020 | COVID-19 lockdowns changed normal demand patterns |

**Study period:** 1 Jan 2015 to 31 Dec 2019, hourly, in UTC. That is **43,824 rows**.

## 3. What the data looks like

| | GB load (MW) | GB temperature (°C) |
|---|---|---|
| Mean | 35,523 | 9.9 |
| Std. dev. | 7,749 | 5.5 |
| Range after cleaning | 14,356–57,388 | −4.5 to 29.1 |
| Missing hours | 6 (two 3-hour gaps, both at the March clock change) | 0 |
| Wrong values | 109 hours: 24 below 10,000 MW, 59 one-hour spikes, 26 in too-low blocks | — |
| Total hours filled | 115 (0.26%), 71 of them in 2019 | — |

- There are strong **daily (24 h)** and **weekly (168 h)** cycles, and a clear **yearly** cycle (winter demand ~45–55 GW, summer ~25–35 GW).
- Average demand: weekdays 36,727 MW, weekends 33,052 MW, bank holidays 31,846 MW. Holidays behave like Sundays, which is why `is_holiday` is a feature and why RQ3 analyses holiday errors separately.
- Daily mean load vs daily mean temperature: **r = −0.74**, so colder days mean higher demand. Hourly, the correlation is only −0.13 because the daily cycle dominates. The temperature effect shows up in the level of the day, not the shape of each hour.
- Wrong values are ENTSO-E reporting glitches, found with three rules: (1) load below 10,000 MW; (2) one-hour spikes more than 5,000 MW away from both neighbours in the same direction; (3) load below 65% of the average of the same hour last week and next week, skipping bank holidays and 24 Dec – 2 Jan. Most of them are in the 2019 test year, so cleaning them matters for a fair evaluation.

## 4. Engineered features

`t` is the hour being forecast. Every feature only uses information available at forecast time, so there is no look-ahead leakage.

| # | Feature | Group | Definition | Why it is included | Corr. with `y` |
|---|---|---|---|---|---|
| 1 | `lag_1` | Lag | Load 1 hour before *t* | Demand changes smoothly from hour to hour | 0.95 |
| 2 | `lag_24` | Lag | Load at the same hour yesterday | Daily cycle | 0.94 |
| 3 | `lag_168` | Lag | Load at the same hour last week | Weekly cycle (also the seasonal-naive forecast) | 0.95 |
| 4 | `rolling_mean_24` | Rolling | Mean of the previous 24 hours | Current daily level | 0.52 |
| 5 | `rolling_mean_168` | Rolling | Mean of the previous 168 hours | Weekly level / slow trend | 0.47 |
| 6 | `hour` | Calendar | Hour of day, 0–23 (UK local time) | Morning and evening peaks | 0.51 |
| 7 | `day_of_week` | Calendar | 0 = Mon … 6 = Sun | Weekday/weekend pattern | −0.16 |
| 8 | `month` | Calendar | 1–12 | Seasonality | −0.16 |
| 9 | `is_weekend` | Calendar | 1 if Sat/Sun | Lower weekend demand (RQ3) | −0.20 |
| 10 | `is_holiday` | Calendar | 1 if an England & Wales bank holiday (`holidays` package) | Holiday demand drop (RQ3) | −0.07 |
| 11 | `temperature` | Weather | GB temperature at hour *t* | Heating demand (RQ4) | −0.14 (hourly), −0.74 (daily) |

Notes:
- **Rolling means** are computed on the series shifted by one hour, so the value being predicted is never included.
- **Calendar features** use Europe/London local time, because behaviour follows clock time. The data itself stays in UTC so every day has exactly 24 hours.
- **Temperature** is the *observed* value, which stands in for a perfect weather forecast. This is a stated limitation: real-world errors would be somewhat higher.
- **For the 24-hour horizon,** `lag_1` is not yet known for hours 2–24. MLForecast handles this recursively by feeding its own predictions back in as lags. This is the standard approach and is applied the same way to all models.
- The correlations are a first sanity check only. Real feature importance is measured later through XGBoost importance scores and the ablation study.

## 5. Which algorithm uses which features

| Model | Library | Input features |
|---|---|---|
| Seasonal naive | StatsForecast | `y` only. Forecast = value 168 h earlier. No training |
| SARIMA | StatsForecast AutoARIMA | `y` history only (seasonal period 24). Orders chosen by AutoARIMA on the 8 weeks before 2019 |
| XGBoost | MLForecast | All 11 features |
| LSTM | NeuralForecast | 168-hour window of `y` + calendar features + `temperature` as future-known inputs |
| PatchTST | NeuralForecast | 168-hour window of `y` only. The library's PatchTST is univariate and has no exogenous inputs |

## 6. Feature ablation (RQ4)

XGBoost and LSTM are re-run on the validation year 2018 with:

| Set | Features |
|---|---|
| A: history only | lags + rolling means |
| B: + calendar | A + hour, day_of_week, month, is_weekend, is_holiday |
| C: + temperature | A + temperature |
| D: full | A + calendar + temperature |

The difference in MAE between A, B, C and D answers RQ4.

## 7. Pipeline

```
1. Download     OPSD raw CSVs                         → datasets/raw/          (01)
2. Clean        GB load + GB temperature, 2015–2019;  → datasets/processed/    (02)
                3 rules for wrong values → missing;
                gaps ≤3 h: linear interpolation;
                gaps >3 h: same hour previous week;
                every filled value flagged
3. EDA          patterns that justify each feature                             (03)
4. Features     11 features above
5. Split        train 2015–2017 | validation 2018 | test 2019 (time-ordered, never random)
                                                      → datasets/processed/    (04)
6. Train/tune   5 models; hyperparameters chosen on 2018 only
7. Forecast     rolling origin: a fresh 1–24 h forecast from every day of 2019
8. Evaluate     MAE, RMSE, MAPE per horizon; skill vs seasonal naive;
                Diebold-Mariano test; errors by peak / weekend / holiday;
                ablation sets A–D
9. Present      results/ figures & tables → Streamlit dashboard
```
