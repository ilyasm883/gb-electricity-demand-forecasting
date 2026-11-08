# Research Questions and Answers

**Multi-Horizon Electricity Demand Forecasting Using Classical Models and Deep Temporal Networks**

---

### 1. What is this research about?

We predict how much electricity Great Britain will use in each of the **next 1 to 24 hours**.
We test five models, from very simple to deep learning, on the same data and in the same way.
We do not make a new model. We want to find out **when a complex model is really better than a simple one**.

### 2. What is the problem?

Electricity companies need good forecasts to make the right amount of electricity at the right time.
Many new papers say deep learning models are the best. But other studies show that simple models often do just as well when the test is fair.
Also, most papers give **one average error** for everything. This hides how a model does further ahead in time, at busy hours, at weekends and on holidays.
So it is not clear which kind of model is the best choice.

### 3. What is the research gap?

Other studies are missing three things:

1. **Strong simple models:** new deep learning models are often not compared with strong simple models.
2. **More than one error number:** most studies show only one average error, not the error for each hour ahead or for special days.
3. **Fair tests of the inputs:** studies do not often check, in the same way for every model, how much temperature and calendar information help.

### 4. What are the research questions?

| | Research question |
|---|---|
| **RQ1** | Which model gives the most accurate forecasts? |
| **RQ2** | How much does the accuracy of each model drop when it forecasts 24 hours ahead instead of 1 hour ahead? |
| **RQ3** | When do the models make their biggest mistakes? Is it at peak hours, at weekends or on public holidays? |
| **RQ4** | Do temperature and calendar information make the forecasts more accurate? |

### 5. Which data do we use?

Free data from **Open Power System Data (OPSD)**:

| Data | Column | What it is |
|---|---|---|
| Time series (version 2020-10-06) | `GB_GBN_load_actual_entsoe_transparency` | How much electricity Great Britain used in each hour (MW) |
| Weather (version 2020-09-16) | `GB_temperature` | The temperature in Great Britain in each hour (°C) |

- **Years:** 2015 to 2019, which is **43,824 hours**.
- **No 2020:** COVID-19 lockdowns changed how people used electricity.
- **Why OPSD:** it is free and checked, it has electricity use and temperature for the same years, and anyone can download it.
- **Split by year, never mixed:** learn from 2015-2017, choose settings with 2018, test on 2019.

### 6. How did we clean the data?

Only 6 hours had no value, but some values were clearly wrong. Three simple rules found them:

1. Below **10,000 MW** (Great Britain never uses this little): 24 hours.
2. A **sudden jump** of more than 5,000 MW for one hour only: 59 hours.
3. A **block of low values**, below 65% of the normal value for that hour (bank holidays and Christmas skipped): 26 hours.

We filled **115 hours (0.26%)** in total. Short gaps (3 hours or less) get a straight line between the hours around them. Longer gaps get the value from the same hour last week.
We marked every filled hour, and we do not use the filled hours of 2019 when we score the models.

### 7. Which features do we use, and why?

A feature is a piece of information we give to the model. We make **11 features** from the electricity use, the temperature and the time:

| Feature | What it is | Why |
|---|---|---|
| `lag_1` | Use 1 hour before | Use changes slowly from hour to hour |
| `lag_24` | Use at the same hour yesterday | Use repeats every day |
| `lag_168` | Use at the same hour last week | Use repeats every week |
| `rolling_mean_24` | Average use of the last 24 hours | How high use is today |
| `rolling_mean_168` | Average use of the last week | How high use is this week |
| `hour` | Hour of the day (UK time) | Lowest at about 4 am, highest at about 5 pm |
| `day_of_week` | Monday to Sunday | Each day is a bit different |
| `month` | 1 to 12 | Use is higher in winter |
| `is_weekend` | 1 on Saturday and Sunday | About 10% lower at weekends |
| `is_holiday` | 1 on a bank holiday | About 13% lower, like a Sunday |
| `temperature` | Temperature in °C | People use more electricity when it is cold |

The features only use information we would already know at the time of the forecast, so the models never "see the future".
We use the real, measured temperature. This is like a perfect weather forecast, so real-life errors would be a little bigger.

### 8. What is temporal analysis?

**Temporal analysis means looking at how data changes over time.** Electricity use is measured every hour, so time is important in every step:

- **Patterns:** use repeats **every day** (24 hours), **every week** (168 hours) and **every year** (high in winter, low in summer).
- **Link with the past:** use now is very close to use 1 hour ago, 24 hours ago and 168 hours ago. That is why we use `lag_1`, `lag_24` and `lag_168`.
- **Split by time:** the models learn from the past (2015-2017) and are tested on the future (2019). We never mix the years.
- **Testing like real life:** every day of 2019, each model forecasts the next 24 hours using only the data known until then.
- **Errors over time:** we look at the errors for each hour ahead, each hour of the day, each type of day and each month.

### 9. Which models do we use, and why?

| Model | Type | Why we chose it |
|---|---|---|
| **Seasonal naive** | Simplest | Copies the value from the same hour last week. No training. Experts say every new model must beat it |
| **SARIMA** | Statistics | A well-known model that is easy to explain. Statistics models did very well in a big forecasting competition (M4) |
| **XGBoost** | Machine learning (trees) | Very strong on data in tables. This kind of model won most places in another big competition (M5) |
| **LSTM** | Deep learning (memory) | The most used deep learning model for electricity forecasting. It remembers the last week of data |
| **PatchTST** | Deep learning (transformer) | A new model that cuts the data into short pieces. It did better than older transformer models |

Together they go from the simplest to the most complex. All five use the same free tools (StatsForecast, MLForecast, NeuralForecast), so every model is tested in the same way.
See [ABOUT.md](ABOUT.md) for how each choice is linked to the literature review, with sources.

### 10. How did we train and test the models?

- **Train:** the models learn from the data before 2019. SARIMA only uses the last 8 weeks before 2019, because it is slow on long data.
- **Tune (choose the settings) with 2018 only:** XGBoost tries a few settings and keeps the best one. LSTM and PatchTST stop training when they stop getting better on 2018. SARIMA chooses its own settings.
- **Test on 2019:** every day at midnight, each model forecasts the next 24 hours. That is 8,760 forecasts per model. We use the test year only once.

### 11. Why is each model trained only once?

This question can mean two things.

**a) Why is the model not trained again during 2019?**

Each model learns once, from the data before 2019. Then it forecasts all 365 days of 2019 without learning again.
Every day it gets the newest real data as input, but the model itself does not change. We do this for three reasons:

- **It is fair.** Every model gets exactly the same information at every forecast. So any difference comes from the model, not from how often it was updated.
- **It is a strict test.** The models must work for a whole year without any change.
- **Training again every day costs a lot of time, and did not help.** We tried it for SARIMA for two weeks. Training it again every day did not make it better (error 2,660 MW with daily training, 2,612 MW without), but it took much longer.

In real life, a company would train the models again from time to time, for example every month. This is good future work.

**b) Why is each model run only once, and not many times?**

| Model | Does a second run give a different result? |
|---|---|
| Seasonal naive | No. It is a fixed rule |
| SARIMA | No. It is a fixed calculation |
| XGBoost | Almost no. Its random seed is fixed (42) |
| LSTM and PatchTST | **Yes, a little.** Deep learning starts from random numbers, so every run is a bit different |

So running three of the five models again would not change anything. For the two deep learning models:

- We fixed the random seeds, so anyone can repeat our results.
- The test is big: 8,760 forecasts for each model.
- The Diebold-Mariano test checks that the differences between models are real and not luck.

To be sure, we also trained LSTM and PatchTST **5 times each, with 5 different seeds** (notebook 10).
We show the average and the spread of the 5 runs, and we check that the main findings stay the same in every run.

### 12. How do we measure the errors?

| Measure | What it means |
|---|---|
| **MAE** | On average, how many MW the forecast is wrong. Lower is better |
| **RMSE** | Like MAE, but big mistakes count more |
| **MAPE** | The average error as a percentage of the real value |
| **Skill** | How much better than the simplest model, in %. Higher is better |
| **Diebold-Mariano test** | Checks if the difference between two models is real or just luck (real if p < 0.05) |

We also compare our models with the **official forecast** for Great Britain, which is in the same data file (notebook 10).
The official forecast measures demand a little differently, so we also show it with its average error corrected, using 2018 only.

### 13. What are the limits of this study?

- Only **one country** (Great Britain) and **one test year** (2019).
- We use the **real temperature**, which is like a perfect weather forecast, so real-life errors would be a little bigger.
- 2020 is not included, so the models are not tested on unusual events like COVID-19.
- The deep learning models mostly use their standard settings (but we trained them 5 times with different seeds).
- Every forecast starts at midnight, so each "hour ahead" is also a fixed time of day.

### 14. What could be done next?

- Use **real weather forecasts** instead of the measured temperature.
- Test **more countries and newer years** (2020 and later).
- Try **more models**, like N-BEATS, NHITS or new "foundation" models such as TimesFM.
- Give a **range** instead of one number (for example "between 30,000 and 32,000 MW").
- **Tune the deep learning models more.**
- Start forecasts **every hour** instead of once a day.
- Connect the web app to **live data** so it can forecast real days in the future.

---

*A student research project. Not for real use by electricity companies.*
