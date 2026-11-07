# About this project

**Multi-Horizon Electricity Demand Forecasting Using Classical Models and Deep Temporal Networks**

This project forecasts the hourly electricity demand of Great Britain **1 to 24 hours ahead** and compares five models,
from very simple to deep learning, on the same open data and in exactly the same way.
The aim is not to build a new model, but to find out **when a more complex model is really worth it**.

---

## Dataset

Two free datasets from **Open Power System Data (OPSD)**:

| Dataset | Column used | What it is |
|---|---|---|
| Time series, version 2020-10-06 | `GB_GBN_load_actual_entsoe_transparency` | Actual hourly electricity demand of Great Britain (MW) |
| Weather data, version 2020-09-16 | `GB_temperature` | Hourly air temperature of Great Britain (°C), weighted by population |

- **Period:** 1 January 2015 to 31 December 2019, which is 43,824 hours.
- **2020 is left out** because the COVID-19 lockdowns changed normal demand.
- **Split by time:** training 2015-2017, validation 2018, test 2019.

### How the data was cleaned

Only 6 hours were missing, but some recorded values were clearly wrong. Three simple rules found them:

1. **Too low:** load below 10,000 MW (real GB demand is about 15,000-57,000 MW).
2. **One-hour spikes:** load more than 5,000 MW away from both the hour before and the hour after.
3. **Blocks of too-low values:** load below 65% of the normal level for that hour (the average of the same hour last week and next week). Bank holidays and Christmas to New Year are skipped.

Wrong values were treated as missing. Gaps of up to 3 hours were filled with a straight line between the neighbouring hours,
and longer gaps with the value from the same hour one week earlier. In total **115 hours (0.26%)** were filled, and every filled hour is flagged.
After cleaning, the dataset has **no missing or wrong values**.

### Features

From the load, the temperature and the time, 11 features are built:

| Group | Features | Why |
|---|---|---|
| Past load | `lag_1`, `lag_24`, `lag_168`, `rolling_mean_24`, `rolling_mean_168` | Demand depends strongly on the previous hour, the same hour yesterday and the same hour last week |
| Calendar | `hour`, `day_of_week`, `month`, `is_weekend`, `is_holiday` | Demand has daily, weekly and yearly patterns, and holidays behave like Sundays |
| Weather | `temperature` | Cold weather increases demand for heating and lighting |

---

## Research questions

| | Question |
|---|---|
| **RQ1** | Which model gives the most accurate forecasts: seasonal naive, SARIMA, XGBoost, LSTM or PatchTST? |
| **RQ2** | How much less accurate does each model become when forecasting 24 hours ahead instead of 1 hour ahead? |
| **RQ3** | When do the models make their biggest mistakes: at peak hours, at weekends or on public holidays? |
| **RQ4** | Does adding temperature and calendar information make the forecasts more accurate? |

---

## Research gap

1. **Weak baselines:** many papers compare new deep learning models only with other deep models, not with strong simple models such as a seasonal naive forecast or a well-tuned XGBoost.
2. **One average error:** results are usually given as one number for the whole test set, which hides how accuracy changes further ahead in time, at peak hours, at weekends and on holidays.
3. **Unfair testing:** many studies use private data, short test periods or random splits that let future information leak into training.

This project fills these gaps with a fair comparison on open data, a strict time-based split, a full test year and errors reported by horizon and by type of day.

---

## Why these models

| Model | Type | Why it was chosen |
|---|---|---|
| **Seasonal naive** | Simple baseline | Repeats the demand of the same hour last week. Needs no training. Every other model must beat it |
| **SARIMA** | Classical statistics | Well known and widely used in practice. Learns from past values, past errors and the daily cycle |
| **XGBoost** | Machine learning | Gradient-boosted trees are very strong on tables of features and did very well in recent forecasting competitions |
| **LSTM** | Deep learning (recurrent network) | The most widely used deep model for load forecasting. Learns patterns from the last week of demand |
| **PatchTST** | Deep learning (transformer) | A recent transformer that splits the input into short patches. Reported better results than older transformers |

Together they cover simple, statistical, machine learning and deep learning methods, from the easiest to the most complex.

---

## Methodology

1. **Prepare the data:** take the GB load and temperature for 2015-2019, find and fill the wrong values.
2. **Explore the data:** look at the daily, weekly and yearly patterns, holidays and temperature, and use what was found to choose the features.
3. **Build the features:** 11 features that only use information known before the hour being forecast, so the models never see the future.
4. **Train and tune:** train each model on the past (2015-2017) and choose its settings on the validation year (2018) only.
5. **Test:** every day of 2019, each model forecasts the next 24 hours using only the data known up to that moment. The test year is used only once.
6. **Compare:** measure the errors (MAE, RMSE, MAPE and skill against the seasonal naive model), check whether the differences are real with the Diebold-Mariano test, and look at the errors by horizon, peak hours, weekends and holidays.
7. **Test the features:** train XGBoost and the LSTM with and without the calendar and temperature features to see how much they help.

All models use the free Nixtla libraries (StatsForecast, MLForecast and NeuralForecast), which use the same data format,
so every model is trained and tested in the same way.

---

*Academic prototype for an MSc research project. Not a tool for real grid operation.*
