# Data, Features and Steps

**Project:** Multi-Horizon Electricity Demand Forecasting Using Classical Models and Deep Temporal Networks

This file explains the data and the features in detail. All numbers come from notebooks 01 to 04.

---

## 1. Where the data comes from

| Dataset | File | Size | What is in it |
|---|---|---|---|
| OPSD Time Series, version 2020-10-06 | `time_series_60min_singleindex.csv` | 130 MB, 300 columns | Hourly electricity use, production and prices for 32 countries in Europe |
| OPSD Weather Data, version 2020-09-16 | `weather_data.csv` | 234 MB, 85 columns | Hourly temperature and sunlight for each country, 1980 to 2019 |

The two files have 385 columns in total. **We use only 2 of them:** electricity use and temperature for Great Britain.

## 2. The columns we use

| Original column | New name | Unit | What it is |
|---|---|---|---|
| `GB_GBN_load_actual_entsoe_transparency` | `load` | MW | How much electricity Great Britain used in each hour. **This is what we forecast** |
| `GB_temperature` | `temperature` | °C | The air temperature in Great Britain in each hour |

**Columns we do not use, and why:**

| Columns | Why we do not use them |
|---|---|
| GB load forecast (`GB_GBN_load_forecast_*`) | This is the grid company's own forecast. We want to make our own |
| Electricity price | The price depends on how much electricity is used. It is a result, not a cause, and it is not known in advance |
| Wind and solar power | These are about making electricity, not using it. We would need to forecast them too |
| Sunlight | We keep the study simple. Temperature is the weather input we test (RQ4) |
| `GB_NIR_*`, `GB_UKM_*` | Northern Ireland and the whole UK. We only study Great Britain (`GBN`) |
| Other countries | We only study Great Britain |
| The year 2020 | COVID-19 lockdowns changed how people used electricity |

**Time period:** 1 January 2015 to 31 December 2019, one row per hour. That is **43,824 rows**.

## 3. What the data looks like

| | Electricity use (MW) | Temperature (°C) |
|---|---|---|
| Average | 35,523 | 9.9 |
| Lowest to highest (after cleaning) | 14,356 to 57,388 | −4.5 to 29.1 |
| Missing hours | 6 (on the two days the clocks went forward in March) | 0 |
| Wrong values | 109 hours: 24 below 10,000 MW, 59 sudden jumps, 26 in blocks of low values | none |
| Hours we filled | 115 (0.26%), 71 of them in 2019 | none |

- Electricity use repeats **every day** (low at night, high in the evening) and **every week** (lower at weekends). It is also higher in **winter** (about 45,000-55,000 MW) than in **summer** (about 25,000-35,000 MW).
- On average, use is 36,727 MW on weekdays, 33,052 MW at weekends and 31,846 MW on bank holidays. **A bank holiday is like a Sunday.**
- **Colder days use more electricity.** The daily average use and the daily average temperature go together strongly (correlation −0.74).
- The wrong values are mistakes in the published data. We found them with three simple rules (see [ABOUT.md](ABOUT.md)). Most of them are in 2019, our test year, so fixing them makes the test fair.

## 4. The 11 features

A feature is a piece of information we give to a model. Every feature only uses information we would already know
at the time of the forecast, so the models never "see the future".

| # | Feature | Group | What it is | Why we use it |
|---|---|---|---|---|
| 1 | `lag_1` | Past use | Use 1 hour before | Use changes slowly from one hour to the next |
| 2 | `lag_24` | Past use | Use at the same hour yesterday | Use repeats every day |
| 3 | `lag_168` | Past use | Use at the same hour last week | Use repeats every week |
| 4 | `rolling_mean_24` | Past use | Average use of the last 24 hours | How high use is today |
| 5 | `rolling_mean_168` | Past use | Average use of the last 168 hours (one week) | How high use is this week |
| 6 | `hour` | Calendar | Hour of the day, 0 to 23 (UK time) | Use is low at night and high in the evening |
| 7 | `day_of_week` | Calendar | 0 = Monday to 6 = Sunday | Each day of the week is a bit different |
| 8 | `month` | Calendar | 1 to 12 | Use is higher in winter |
| 9 | `is_weekend` | Calendar | 1 on Saturday and Sunday | Use is lower at weekends |
| 10 | `is_holiday` | Calendar | 1 on a bank holiday in England and Wales | Use is much lower on bank holidays |
| 11 | `temperature` | Weather | Temperature in that hour | People use more electricity when it is cold |

Notes:
- The rolling averages stop one hour before the forecast hour, so the value we want to forecast is never inside them.
- The calendar features use UK time, because people follow the clock. The data itself is in UTC, so every day has exactly 24 hours.
- We use the real, measured temperature. This is like having a perfect weather forecast, so real-life errors would be a little bigger.
- When XGBoost forecasts 24 hours ahead, it does not know the real use for hours 2 to 24 yet. So it uses its own forecasts for those hours, one hour after another.

## 5. Which model uses which features

| Model | Tool | Information it uses |
|---|---|---|
| Seasonal naive | StatsForecast | Only past use. The forecast is the value from 168 hours (one week) before. No training |
| SARIMA | StatsForecast | Only past use, with a daily pattern of 24 hours. Its settings are chosen automatically on the 8 weeks before 2019 |
| XGBoost | MLForecast | All 11 features |
| LSTM | NeuralForecast | The last 168 hours of use, plus the calendar features and temperature |
| PatchTST | NeuralForecast | Only the last 168 hours of use. This model cannot take extra information |

## 6. Testing the features (RQ4)

We train XGBoost and the LSTM again on 2018 (the validation year) with four groups of features:

| Group | Features |
|---|---|
| A: past use only | lags and rolling averages |
| B: + calendar | A + hour, day_of_week, month, is_weekend, is_holiday |
| C: + temperature | A + temperature |
| D: everything | A + calendar + temperature |

If the error goes down from A to B, C or D, the extra features help. This answers RQ4.

## 7. All the steps

```
1. Download      the original OPSD files                         → datasets/raw/          (notebook 01)
2. Clean         keep GB use and temperature, 2015-2019;           → datasets/processed/    (notebook 02)
                 find wrong values with 3 rules;
                 gaps of 3 hours or less: straight line;
                 longer gaps: same hour last week;
                 mark every filled hour
3. Explore       look at the patterns that explain each feature                            (notebook 03)
4. Features      make the 11 features above
5. Split         train 2015-2017 | validation 2018 | test 2019 (by time, never mixed)
                                                                    → datasets/processed/    (notebook 04)
6. Train         5 models; settings chosen using 2018 only                                  (notebooks 05-07)
7. Forecast      every day of 2019, forecast the next 24 hours
8. Compare       errors for each hour ahead; compare with the simplest model;
                 Diebold-Mariano test; errors at peak hours, weekends, holidays;
                 feature groups A-D                                                         (notebooks 08-09)
9. Show          charts and tables in results/, and the web app
```
